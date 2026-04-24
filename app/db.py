"""
SQLite — Leads, Abogados, Citas, Eventos de tracking (Galeano Herrera).
WAL para concurrencia, sin ORM (mantenerlo simple).
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets as _secrets
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).parent.parent / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "leads.db"

_lock = threading.Lock()


def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(str(DB_PATH), timeout=10, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    with _lock:
        c = _conn()
        try:
            yield c
            c.commit()
        finally:
            c.close()


def init_db() -> None:
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS lawyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            whatsapp TEXT NOT NULL,             -- formato 573XXXXXXXXX
            email TEXT UNIQUE,                  -- login del abogado
            password_hash TEXT,                 -- sha256(salt+pwd)
            password_salt TEXT,
            areas TEXT NOT NULL DEFAULT '[]',   -- JSON array
            active INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1,   -- toggle "no me agenden hoy"
            is_default INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL REFERENCES leads(id),
            lawyer_id INTEGER REFERENCES lawyers(id),
            calendar_event_id TEXT,
            meet_url TEXT,
            html_link TEXT,
            scheduled_at TEXT NOT NULL,         -- ISO8601 con tz
            duration_min INTEGER NOT NULL DEFAULT 30,
            status TEXT NOT NULL DEFAULT 'scheduled',
                -- scheduled / cancelled_by_user / cancelled_by_lawyer / completed / no_show / rescheduled
            reminded_24h INTEGER NOT NULL DEFAULT 0,
            reminded_1h INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            cancelled_at TEXT,
            notes TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_appt_sched ON appointments(scheduled_at);
        CREATE INDEX IF NOT EXISTS idx_appt_lead ON appointments(lead_id);

        CREATE TABLE IF NOT EXISTS lawyer_blocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lawyer_id INTEGER NOT NULL REFERENCES lawyers(id) ON DELETE CASCADE,
            start_at TEXT NOT NULL,
            end_at TEXT NOT NULL,
            reason TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_blocks_lawyer ON lawyer_blocks(lawyer_id, start_at);

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
                -- page_view / preview_started / preview_done / register / otp_verified / downloaded / meeting_booked / meeting_cancelled
            ip TEXT,
            user_agent TEXT,
            referer TEXT,
            payload TEXT,
            ts TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts DESC);
        CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts DESC);
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL UNIQUE,
            name TEXT,
            cedula TEXT,
            phone TEXT,
            email TEXT,
            area TEXT,
            descripcion TEXT NOT NULL,
            draft TEXT,                          -- borrador completo
            fichas TEXT,                         -- JSON: radicados usados
            status TEXT NOT NULL DEFAULT 'preview',
                -- preview / pending_otp / verified / contacted / closed
            otp_verified INTEGER NOT NULL DEFAULT 0,
            lawyer_id INTEGER REFERENCES lawyers(id),
            ip TEXT,
            user_agent TEXT,
            consent_terms INTEGER NOT NULL DEFAULT 0,
            consent_data INTEGER NOT NULL DEFAULT 0,
            consent_marketing INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            verified_at TEXT,
            contacted_at TEXT,
            notes TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
        CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);

        CREATE TABLE IF NOT EXISTS rate_limit (
            ip TEXT NOT NULL,
            window_start TEXT NOT NULL,
            count INTEGER NOT NULL,
            PRIMARY KEY (ip, window_start)
        );
        """)


# ── Lawyers ───────────────────────────────────────────────────────────────────

def create_lawyer(name: str, whatsapp: str, areas: list[str], is_default: bool = False) -> int:
    with db() as c:
        if is_default:
            c.execute("UPDATE lawyers SET is_default=0")
        cur = c.execute(
            "INSERT INTO lawyers(name,whatsapp,areas,is_default) VALUES(?,?,?,?)",
            (name, whatsapp, json.dumps(areas), 1 if is_default else 0),
        )
        return cur.lastrowid


def list_lawyers(active_only: bool = False) -> list[dict]:
    with db() as c:
        sql = "SELECT * FROM lawyers"
        if active_only:
            sql += " WHERE active=1"
        sql += " ORDER BY is_default DESC, name"
        return [_lawyer_row(r) for r in c.execute(sql)]


def update_lawyer(lid: int, **fields) -> None:
    if not fields:
        return
    if "areas" in fields and isinstance(fields["areas"], list):
        fields["areas"] = json.dumps(fields["areas"])
    cols = ", ".join(f"{k}=?" for k in fields)
    with db() as c:
        if fields.get("is_default"):
            c.execute("UPDATE lawyers SET is_default=0")
        c.execute(f"UPDATE lawyers SET {cols} WHERE id=?", (*fields.values(), lid))


def delete_lawyer(lid: int) -> None:
    with db() as c:
        c.execute("DELETE FROM lawyers WHERE id=?", (lid,))


def lawyer_for_area(area: Optional[str]) -> Optional[dict]:
    """Devuelve el abogado que cubre el área o el default."""
    with db() as c:
        if area:
            for r in c.execute("SELECT * FROM lawyers WHERE active=1 ORDER BY is_default DESC"):
                areas = json.loads(r["areas"] or "[]")
                if area in areas or "*" in areas:
                    return _lawyer_row(r)
        r = c.execute("SELECT * FROM lawyers WHERE active=1 AND is_default=1").fetchone()
        if r: return _lawyer_row(r)
        r = c.execute("SELECT * FROM lawyers WHERE active=1 ORDER BY id LIMIT 1").fetchone()
        return _lawyer_row(r) if r else None


def _lawyer_row(r) -> dict:
    if r is None: return None
    d = dict(r)
    d["areas"] = json.loads(d.get("areas") or "[]")
    return d


# ── Leads ─────────────────────────────────────────────────────────────────────

def create_lead(token: str, descripcion: str, area: Optional[str],
                draft: str, fichas: list[dict],
                ip: str = "", user_agent: str = "") -> int:
    with db() as c:
        cur = c.execute(
            """INSERT INTO leads(token, descripcion, area, draft, fichas, ip, user_agent, status)
               VALUES(?,?,?,?,?,?,?, 'preview')""",
            (token, descripcion, area, draft, json.dumps(fichas), ip, user_agent),
        )
        return cur.lastrowid


def attach_user_to_lead(token: str, *, name: str, cedula: str, phone: str, email: str,
                        consent_terms: bool, consent_data: bool, consent_marketing: bool) -> Optional[dict]:
    with db() as c:
        c.execute(
            """UPDATE leads SET name=?, cedula=?, phone=?, email=?,
               consent_terms=?, consent_data=?, consent_marketing=?,
               status='pending_otp'
               WHERE token=? AND status='preview'""",
            (name, cedula, phone, email,
             1 if consent_terms else 0, 1 if consent_data else 0, 1 if consent_marketing else 0,
             token),
        )
        r = c.execute("SELECT * FROM leads WHERE token=?", (token,)).fetchone()
        return dict(r) if r else None


def mark_lead_verified(token: str, lawyer_id: Optional[int]) -> Optional[dict]:
    with db() as c:
        c.execute(
            "UPDATE leads SET otp_verified=1, status='verified', verified_at=datetime('now'), lawyer_id=? WHERE token=?",
            (lawyer_id, token),
        )
        r = c.execute("SELECT * FROM leads WHERE token=?", (token,)).fetchone()
        return dict(r) if r else None


def mark_lead_contacted(lid: int, notes: str = "") -> None:
    with db() as c:
        c.execute(
            "UPDATE leads SET status='contacted', contacted_at=datetime('now'), notes=? WHERE id=?",
            (notes, lid),
        )


def update_lead_status(lid: int, status: str, notes: str = "") -> None:
    with db() as c:
        c.execute("UPDATE leads SET status=?, notes=COALESCE(?,notes) WHERE id=?",
                  (status, notes or None, lid))


def get_lead_by_token(token: str) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM leads WHERE token=?", (token,)).fetchone()
        if not r: return None
        d = dict(r); d["fichas"] = json.loads(d.get("fichas") or "[]"); return d


def list_leads(limit: int = 200, status: Optional[str] = None) -> list[dict]:
    with db() as c:
        if status:
            rows = c.execute(
                "SELECT * FROM leads WHERE status=? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            )
        else:
            rows = c.execute(
                "SELECT * FROM leads ORDER BY created_at DESC LIMIT ?", (limit,)
            )
        out = []
        for r in rows:
            d = dict(r); d["fichas"] = json.loads(d.get("fichas") or "[]"); out.append(d)
        return out


def stats() -> dict:
    with db() as c:
        total      = c.execute("SELECT COUNT(*) c FROM leads").fetchone()["c"]
        verified   = c.execute("SELECT COUNT(*) c FROM leads WHERE status IN ('verified','contacted','closed')").fetchone()["c"]
        contacted  = c.execute("SELECT COUNT(*) c FROM leads WHERE status IN ('contacted','closed')").fetchone()["c"]
        closed     = c.execute("SELECT COUNT(*) c FROM leads WHERE status='closed'").fetchone()["c"]
        last24     = c.execute("SELECT COUNT(*) c FROM leads WHERE created_at > datetime('now','-1 day')").fetchone()["c"]
        return {
            "total": total, "verified": verified, "contacted": contacted,
            "closed": closed, "last_24h": last24,
            "conversion_otp": round(100*verified/total,1) if total else 0,
            "conversion_contact": round(100*contacted/verified,1) if verified else 0,
        }


# ── Rate limit ────────────────────────────────────────────────────────────────

def check_rate(ip: str, max_per_hour: int = 5) -> bool:
    """True si está dentro del límite, False si lo excedió."""
    with db() as c:
        c.execute("DELETE FROM rate_limit WHERE window_start < datetime('now','-1 hour')")
        r = c.execute(
            "SELECT SUM(count) AS c FROM rate_limit WHERE ip=? AND window_start > datetime('now','-1 hour')",
            (ip,),
        ).fetchone()
        cnt = (r["c"] or 0) if r else 0
        if cnt >= max_per_hour:
            return False
        c.execute(
            "INSERT INTO rate_limit(ip, window_start, count) VALUES(?, datetime('now'), 1)",
            (ip,),
        )
        return True


# ── Auth abogados (login email+password) ─────────────────────────────────────

def _hash_password(pwd: str, salt: Optional[str] = None) -> tuple[str,str]:
    salt = salt or _secrets.token_hex(16)
    h = hashlib.sha256((salt + pwd).encode("utf-8")).hexdigest()
    return h, salt


def set_lawyer_password(lid: int, password: str) -> None:
    h, salt = _hash_password(password)
    with db() as c:
        c.execute("UPDATE lawyers SET password_hash=?, password_salt=? WHERE id=?",
                  (h, salt, lid))


def set_lawyer_email(lid: int, email: str) -> None:
    with db() as c:
        c.execute("UPDATE lawyers SET email=? WHERE id=?", (email.strip().lower(), lid))


def authenticate_lawyer(email: str, password: str) -> Optional[dict]:
    if not (email and password):
        return None
    with db() as c:
        r = c.execute("SELECT * FROM lawyers WHERE lower(email)=? AND active=1",
                      (email.strip().lower(),)).fetchone()
        if not r or not r["password_hash"] or not r["password_salt"]:
            return None
        expected, _ = _hash_password(password, r["password_salt"])
        if not _secrets.compare_digest(expected, r["password_hash"]):
            return None
        return _lawyer_row(r)


def get_lawyer_by_email(email: str) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM lawyers WHERE lower(email)=?", (email.strip().lower(),)).fetchone()
        return _lawyer_row(r) if r else None


def get_lawyer(lid: int) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM lawyers WHERE id=?", (lid,)).fetchone()
        return _lawyer_row(r) if r else None


def set_lawyer_availability(lid: int, available: bool) -> None:
    with db() as c:
        c.execute("UPDATE lawyers SET available=? WHERE id=?", (1 if available else 0, lid))


# ── Schedule semanal del abogado ─────────────────────────────────────────────

WEEKDAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DEFAULT_SCHEDULE = {
    "mon": [["09:00", "12:00"], ["14:00", "17:00"]],
    "tue": [["09:00", "12:00"], ["14:00", "17:00"]],
    "wed": [["09:00", "12:00"], ["14:00", "17:00"]],
    "thu": [["09:00", "12:00"], ["14:00", "17:00"]],
    "fri": [["09:00", "12:00"], ["14:00", "17:00"]],
    "sat": [],
    "sun": [],
}


def get_lawyer_schedule(lid: int) -> dict:
    """Retorna el schedule del abogado, o el default si no tiene configurado."""
    with db() as c:
        r = c.execute("SELECT schedule FROM lawyers WHERE id=?", (lid,)).fetchone()
    if not r or not r["schedule"]:
        return {k: list(v) for k, v in DEFAULT_SCHEDULE.items()}
    try:
        sched = json.loads(r["schedule"])
        # Asegurar que están todas las claves
        for k in WEEKDAY_KEYS:
            if k not in sched: sched[k] = []
        return sched
    except Exception:
        return {k: list(v) for k, v in DEFAULT_SCHEDULE.items()}


def _validar_hora(s: str) -> Optional[tuple[int, int]]:
    try:
        h, m = s.split(":")
        h, m = int(h), int(m)
        if 0 <= h <= 24 and 0 <= m < 60:
            return h, m
    except Exception:
        pass
    return None


def set_lawyer_schedule(lid: int, schedule: dict) -> dict:
    """Valida y guarda el schedule del abogado. Retorna el schedule limpio."""
    if not isinstance(schedule, dict):
        raise ValueError("schedule debe ser un dict")
    cleaned: dict[str, list[list[str]]] = {k: [] for k in WEEKDAY_KEYS}
    for day, blocks in schedule.items():
        if day not in WEEKDAY_KEYS:
            continue
        if not isinstance(blocks, list):
            continue
        rangos: list[tuple[int, int, int, int]] = []
        for b in blocks:
            if not (isinstance(b, list) and len(b) == 2):
                continue
            s_t = _validar_hora(b[0])
            e_t = _validar_hora(b[1])
            if not (s_t and e_t):
                continue
            sh, sm = s_t
            eh, em = e_t
            if (sh, sm) >= (eh, em):
                continue
            if eh > 23 or (eh == 23 and em > 59):
                if not (eh == 24 and em == 0):
                    continue
            rangos.append((sh, sm, eh, em))
        # Ordenar y mergear solapados
        rangos.sort()
        merged: list[tuple[int, int, int, int]] = []
        for r in rangos:
            if merged and (r[0], r[1]) <= (merged[-1][2], merged[-1][3]):
                last = merged[-1]
                merged[-1] = (last[0], last[1], max(last[2], r[2]), max(last[3], r[3]))
            else:
                merged.append(r)
        cleaned[day] = [[f"{a:02d}:{b:02d}", f"{c:02d}:{d:02d}"] for a, b, c, d in merged]

    with db() as c:
        c.execute("UPDATE lawyers SET schedule=? WHERE id=?",
                  (json.dumps(cleaned, ensure_ascii=False), lid))
    return cleaned


def lawyer_for_assignment(area: Optional[str]) -> Optional[dict]:
    """Como lawyer_for_area pero filtrando solo abogados disponibles."""
    with db() as c:
        if area:
            for r in c.execute("SELECT * FROM lawyers WHERE active=1 AND available=1 ORDER BY is_default DESC"):
                areas = json.loads(r["areas"] or "[]")
                if area in areas or "*" in areas:
                    return _lawyer_row(r)
        r = c.execute("SELECT * FROM lawyers WHERE active=1 AND available=1 AND is_default=1").fetchone()
        if r: return _lawyer_row(r)
        r = c.execute("SELECT * FROM lawyers WHERE active=1 AND available=1 ORDER BY id LIMIT 1").fetchone()
        return _lawyer_row(r) if r else None


# ── Citas (appointments) ─────────────────────────────────────────────────────

def create_appointment(lead_id: int, lawyer_id: Optional[int], scheduled_at: str,
                       duration_min: int, modality: str = "whatsapp",
                       meet_url: str = "", notes: str = "") -> int:
    with db() as c:
        cur = c.execute(
            """INSERT INTO appointments(lead_id, lawyer_id, scheduled_at, duration_min,
                meet_url, status, notes)
               VALUES(?,?,?,?,?, 'scheduled', ?)""",
            (lead_id, lawyer_id, scheduled_at, duration_min, meet_url,
             (notes or f"Modalidad: {modality}")),
        )
        return cur.lastrowid


def get_appointment(aid: int) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM appointments WHERE id=?", (aid,)).fetchone()
        return dict(r) if r else None


def get_appointment_by_lead(lead_id: int) -> Optional[dict]:
    with db() as c:
        r = c.execute(
            "SELECT * FROM appointments WHERE lead_id=? AND status='scheduled' ORDER BY scheduled_at DESC LIMIT 1",
            (lead_id,)
        ).fetchone()
        return dict(r) if r else None


def update_appointment_status(aid: int, status: str, notes: str = "") -> None:
    with db() as c:
        if status.startswith("cancelled"):
            c.execute("UPDATE appointments SET status=?, cancelled_at=datetime('now'), notes=COALESCE(?,notes) WHERE id=?",
                      (status, notes or None, aid))
        else:
            c.execute("UPDATE appointments SET status=?, notes=COALESCE(?,notes) WHERE id=?",
                      (status, notes or None, aid))


def update_appointment_time(aid: int, new_start: str) -> None:
    with db() as c:
        c.execute(
            "UPDATE appointments SET scheduled_at=?, status='scheduled', reminded_24h=0, reminded_1h=0 WHERE id=?",
            (new_start, aid),
        )


def update_appointment_meet(aid: int, meet_url: str) -> None:
    with db() as c:
        c.execute("UPDATE appointments SET meet_url=? WHERE id=?", (meet_url, aid))


def list_appointments(status: Optional[str] = None, lawyer_id: Optional[int] = None,
                      upcoming_only: bool = False, limit: int = 200) -> list[dict]:
    sql = """SELECT a.*, l.name as lead_name, l.phone as lead_phone, l.email as lead_email,
                    l.area as lead_area, l.descripcion as lead_descripcion,
                    w.name as lawyer_name, w.email as lawyer_email
             FROM appointments a
             LEFT JOIN leads l ON a.lead_id = l.id
             LEFT JOIN lawyers w ON a.lawyer_id = w.id
             WHERE 1=1"""
    params = []
    if status:    sql += " AND a.status=?";   params.append(status)
    if lawyer_id: sql += " AND a.lawyer_id=?"; params.append(lawyer_id)
    if upcoming_only: sql += " AND a.scheduled_at > datetime('now') AND a.status='scheduled'"
    sql += " ORDER BY a.scheduled_at ASC LIMIT ?"; params.append(limit)
    with db() as c:
        return [dict(r) for r in c.execute(sql, params)]


def appointments_pending_reminder(window: str) -> list[dict]:
    """
    window: '24h' o '1h'. Devuelve citas que necesitan recordatorio en esa ventana.
    """
    with db() as c:
        if window == "24h":
            sql = """SELECT a.*, l.name as lead_name, l.phone as lead_phone, l.email as lead_email
                     FROM appointments a JOIN leads l ON l.id=a.lead_id
                     WHERE a.status='scheduled' AND a.reminded_24h=0
                       AND a.scheduled_at > datetime('now')
                       AND a.scheduled_at <= datetime('now','+25 hours')"""
        elif window == "1h":
            sql = """SELECT a.*, l.name as lead_name, l.phone as lead_phone, l.email as lead_email
                     FROM appointments a JOIN leads l ON l.id=a.lead_id
                     WHERE a.status='scheduled' AND a.reminded_1h=0
                       AND a.scheduled_at > datetime('now')
                       AND a.scheduled_at <= datetime('now','+90 minutes')"""
        else:
            return []
        return [dict(r) for r in c.execute(sql)]


def mark_appointment_reminded(aid: int, window: str) -> None:
    col = "reminded_24h" if window == "24h" else "reminded_1h"
    with db() as c:
        c.execute(f"UPDATE appointments SET {col}=1 WHERE id=?", (aid,))


# ── Bloqueos manuales del abogado ────────────────────────────────────────────

def create_block(lawyer_id: int, start_at: str, end_at: str, reason: str = "") -> int:
    with db() as c:
        cur = c.execute(
            "INSERT INTO lawyer_blocks(lawyer_id, start_at, end_at, reason) VALUES(?,?,?,?)",
            (lawyer_id, start_at, end_at, reason),
        )
        return cur.lastrowid


def delete_block(bid: int, lawyer_id: Optional[int] = None) -> None:
    with db() as c:
        if lawyer_id is not None:
            c.execute("DELETE FROM lawyer_blocks WHERE id=? AND lawyer_id=?", (bid, lawyer_id))
        else:
            c.execute("DELETE FROM lawyer_blocks WHERE id=?", (bid,))


def list_blocks(lawyer_id: int) -> list[dict]:
    with db() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM lawyer_blocks WHERE lawyer_id=? AND end_at > datetime('now') ORDER BY start_at",
            (lawyer_id,),
        )]


# ── Tracking de eventos ───────────────────────────────────────────────────────

def track_event(type_: str, ip: str = "", user_agent: str = "", referer: str = "",
                payload: Optional[dict] = None) -> None:
    with db() as c:
        c.execute(
            "INSERT INTO events(type, ip, user_agent, referer, payload) VALUES(?,?,?,?,?)",
            (type_, ip[:64], (user_agent or "")[:200], (referer or "")[:300],
             json.dumps(payload) if payload else None),
        )


def funnel_stats(days: int = 7) -> dict:
    """Conversión por etapa en los últimos N días."""
    with db() as c:
        rows = c.execute(
            f"""SELECT type, COUNT(*) c, COUNT(DISTINCT ip) uniq
                FROM events WHERE ts > datetime('now','-{int(days)} days')
                GROUP BY type""",
        ).fetchall()
        return {r["type"]: {"total": r["c"], "uniq": r["uniq"]} for r in rows}


def daily_counts(days: int = 14) -> list[dict]:
    """Cuántos page_view, register, downloaded por día."""
    with db() as c:
        rows = c.execute(
            f"""SELECT date(ts) d, type, COUNT(*) c
                FROM events WHERE ts > datetime('now','-{int(days)} days')
                GROUP BY date(ts), type ORDER BY d DESC""",
        ).fetchall()
        agg = {}
        for r in rows:
            agg.setdefault(r["d"], {})[r["type"]] = r["c"]
        return [{"date": d, **counts} for d, counts in agg.items()]


# ── Migración suave (columnas nuevas en lawyers existentes) ──────────────────

def _migrate() -> None:
    with db() as c:
        cols = {r["name"] for r in c.execute("PRAGMA table_info(lawyers)")}
        if "email" not in cols:
            c.execute("ALTER TABLE lawyers ADD COLUMN email TEXT")
            c.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_lawyers_email ON lawyers(email)")
        if "password_hash" not in cols:
            c.execute("ALTER TABLE lawyers ADD COLUMN password_hash TEXT")
        if "password_salt" not in cols:
            c.execute("ALTER TABLE lawyers ADD COLUMN password_salt TEXT")
        if "available" not in cols:
            c.execute("ALTER TABLE lawyers ADD COLUMN available INTEGER NOT NULL DEFAULT 1")
        if "schedule" not in cols:
            c.execute("ALTER TABLE lawyers ADD COLUMN schedule TEXT")


# ── Bootstrap ─────────────────────────────────────────────────────────────────

def bootstrap_default_lawyer() -> None:
    """Si no hay abogados y hay env LAWYER_WHATSAPP, crea uno default."""
    init_db()
    _migrate()
    with db() as c:
        n = c.execute("SELECT COUNT(*) c FROM lawyers").fetchone()["c"]
    if n == 0:
        wa = (os.environ.get("LAWYER_WHATSAPP") or "").strip()
        name = os.environ.get("LAWYER_NAME", "Galeano Herrera | Abogados")
        if wa:
            create_lawyer(name=name, whatsapp=wa, areas=["*"], is_default=True)
            print(f"[db] abogado default creado: {name} ({wa})")
        else:
            print("[db] sin LAWYER_WHATSAPP: configura uno en /admin")
