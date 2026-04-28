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

        -- Cerebro RAG: documentos cargados por admin/abogados (PDF transformados con IA)
        CREATE TABLE IF NOT EXISTS rag_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_size INTEGER,
            doc_type TEXT,                  -- sentencia | ley | doctrina | otro
            metadata TEXT,                  -- JSON: sala, radicado, año, areas, temas, tesis (extraído por IA)
            uploaded_by_lawyer_id INTEGER REFERENCES lawyers(id),
            uploaded_by_admin INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'uploaded',
                -- uploaded | processing | processed | approved | rejected | error
            chunks_count INTEGER NOT NULL DEFAULT 0,
            tokens_est INTEGER NOT NULL DEFAULT 0,
            error TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            processed_at TEXT,
            approved_at TEXT,
            approved_by TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_rag_docs_status ON rag_documents(status);

        CREATE TABLE IF NOT EXISTS rag_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            page INTEGER,
            texto TEXT NOT NULL,
            tokens_est INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_rag_chunks_doc ON rag_chunks(doc_id);
        CREATE INDEX IF NOT EXISTS idx_rag_chunks_active ON rag_chunks(active);

        -- Landings multi-vertical (tutelas, accidentes, comparendos, laboral, etc)
        CREATE TABLE IF NOT EXISTS landings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE NOT NULL,                -- url path (ej: 'accidentes')
            title TEXT NOT NULL,                      -- nombre interno
            h1 TEXT NOT NULL,                         -- titular hero
            h1_resaltado TEXT,                        -- la parte oro del h1
            subtitulo TEXT,                           -- lead bajo H1
            area_focus TEXT,                          -- salud|pensiones|laboral|accidentes|insolvencia|derechos_fundamentales
            accionado_label TEXT,                     -- ej: "Tu aseguradora SOAT"
            accionado_placeholder TEXT,               -- ej: "Previsora, Sura, AXA..."
            video_url TEXT,                           -- youtube/vimeo embed url opcional
            casos_filtro TEXT,                        -- JSON: lista de IDs de casos del carrusel a mostrar
            casos_extra TEXT,                         -- JSON: casos custom que NO están en el catálogo base
            faq_extra TEXT,                           -- JSON: [{q, a}] añadido al FAQ base
            cta_texto TEXT,                           -- ej: "Reclamar mi indemnización"
            color_acento TEXT,                        -- hex opcional para personalizar (default oro)
            utm_default TEXT,                         -- utm_source default a sumar
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_landings_slug ON landings(slug);

        -- Expedientes formales (con OTP de aceptación del cliente)
        CREATE TABLE IF NOT EXISTS expedientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL REFERENCES leads(id),
            lawyer_id INTEGER REFERENCES lawyers(id),
            numero TEXT UNIQUE,                          -- ej: GH-2026-001
            token TEXT NOT NULL UNIQUE,                  -- para acceso público
            estado TEXT NOT NULL DEFAULT 'borrador',
                -- borrador | pendiente_aceptacion | aceptado | en_curso | cerrado | desistido
            area TEXT,
            honorarios_cop INTEGER,
            honorarios_modalidad TEXT,                   -- fijo | porcentaje | mixto | contingente | pro_bono
            honorarios_descripcion TEXT,
            alcance TEXT,
            obligaciones_cliente TEXT,
            otp TEXT,
            otp_expires TEXT,
            otp_attempts INTEGER NOT NULL DEFAULT 0,
            accepted_at TEXT,
            accepted_ip TEXT,
            closed_at TEXT,
            closed_reason TEXT,
            audit_log TEXT NOT NULL DEFAULT '[]',        -- JSON array append-only
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_exp_lead ON expedientes(lead_id);
        CREATE INDEX IF NOT EXISTS idx_exp_lawyer ON expedientes(lawyer_id);
        CREATE INDEX IF NOT EXISTS idx_exp_estado ON expedientes(estado);
        """)


# ── Lawyers ───────────────────────────────────────────────────────────────────

def create_lawyer(name: str, whatsapp: str, areas: list[str], is_default: bool = False,
                  role: str = "lawyer") -> int:
    with db() as c:
        if is_default:
            c.execute("UPDATE lawyers SET is_default=0")
        cur = c.execute(
            "INSERT INTO lawyers(name,whatsapp,areas,is_default,role) VALUES(?,?,?,?,?)",
            (name, whatsapp, json.dumps(areas), 1 if is_default else 0, role),
        )
        return cur.lastrowid


def update_lawyer_full(lid: int, **fields) -> None:
    """Update extendido para edición completa desde admin."""
    allowed = {"name","whatsapp","email","areas","is_default","active","role"}
    fields = {k:v for k,v in fields.items() if k in allowed}
    if not fields: return
    if "areas" in fields and isinstance(fields["areas"], list):
        fields["areas"] = json.dumps(fields["areas"])
    cols = ", ".join(f"{k}=?" for k in fields)
    with db() as c:
        if fields.get("is_default"):
            c.execute("UPDATE lawyers SET is_default=0")
        c.execute(f"UPDATE lawyers SET {cols} WHERE id=?", (*fields.values(), lid))


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


# ── Cerebro RAG (PDFs cargados) ───────────────────────────────────────────────

def create_rag_document(filename: str, file_size: int, uploaded_by_lawyer_id: Optional[int],
                        uploaded_by_admin: bool, doc_type: str = "otro") -> int:
    with db() as c:
        cur = c.execute(
            """INSERT INTO rag_documents(filename, file_size, doc_type,
                                          uploaded_by_lawyer_id, uploaded_by_admin, status)
               VALUES(?,?,?,?,?, 'uploaded')""",
            (filename, file_size, doc_type, uploaded_by_lawyer_id, 1 if uploaded_by_admin else 0),
        )
        return cur.lastrowid


def update_rag_document(doc_id: int, **fields) -> None:
    """Campos válidos: status, metadata, chunks_count, tokens_est, error, notes,
    processed_at, approved_at, approved_by, doc_type."""
    if not fields:
        return
    if "metadata" in fields and not isinstance(fields["metadata"], str):
        fields["metadata"] = json.dumps(fields["metadata"], ensure_ascii=False)
    cols = ", ".join(f"{k}=?" for k in fields)
    with db() as c:
        c.execute(f"UPDATE rag_documents SET {cols} WHERE id=?", (*fields.values(), doc_id))


def get_rag_document(doc_id: int) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM rag_documents WHERE id=?", (doc_id,)).fetchone()
        if not r: return None
        d = dict(r)
        try:
            d["metadata"] = json.loads(d.get("metadata") or "{}")
        except Exception:
            d["metadata"] = {}
        return d


def list_rag_documents(status: Optional[str] = None, limit: int = 200,
                       lawyer_id: Optional[int] = None) -> list[dict]:
    sql = """SELECT d.*, l.name as lawyer_name
             FROM rag_documents d
             LEFT JOIN lawyers l ON l.id = d.uploaded_by_lawyer_id
             WHERE 1=1"""
    params: list = []
    if status:    sql += " AND d.status=?";  params.append(status)
    if lawyer_id: sql += " AND d.uploaded_by_lawyer_id=?"; params.append(lawyer_id)
    sql += " ORDER BY d.created_at DESC LIMIT ?"; params.append(limit)
    out = []
    with db() as c:
        for r in c.execute(sql, params):
            d = dict(r)
            try: d["metadata"] = json.loads(d.get("metadata") or "{}")
            except Exception: d["metadata"] = {}
            out.append(d)
    return out


def delete_rag_document(doc_id: int) -> None:
    with db() as c:
        c.execute("DELETE FROM rag_chunks WHERE doc_id=?", (doc_id,))
        c.execute("DELETE FROM rag_documents WHERE id=?", (doc_id,))


def add_rag_chunks(doc_id: int, chunks: list[dict]) -> int:
    """Inserta chunks. Retorna cuántos quedaron almacenados."""
    if not chunks: return 0
    with db() as c:
        for ch in chunks:
            c.execute(
                """INSERT INTO rag_chunks(doc_id, chunk_index, page, texto, tokens_est, active)
                   VALUES(?,?,?,?,?, 1)""",
                (doc_id, ch.get("chunk_index", 0), ch.get("page"), ch["texto"],
                 ch.get("tokens_est") or len(ch["texto"]) // 4),
            )
    return len(chunks)


def get_active_rag_chunks(only_approved: bool = True) -> list[dict]:
    """Retorna todos los chunks activos para alimentar el RAG. Cada chunk con
    el formato compatible con fichas (id, texto_busqueda, tipo, areas, ...)."""
    sql = """SELECT c.id, c.doc_id, c.chunk_index, c.page, c.texto, c.tokens_est,
                    d.filename, d.metadata, d.doc_type, d.status as doc_status
             FROM rag_chunks c
             JOIN rag_documents d ON d.id = c.doc_id
             WHERE c.active = 1"""
    if only_approved:
        sql += " AND d.status = 'approved'"
    out = []
    with db() as c:
        for r in c.execute(sql):
            try: meta = json.loads(r["metadata"] or "{}")
            except Exception: meta = {}
            tipo = meta.get("tipo") or r["doc_type"] or "doc"
            radicado = meta.get("radicado") or f"DOC{r['doc_id']}-{r['chunk_index']}"
            out.append({
                "id": f"{radicado}-c{r['chunk_index']}",
                "tipo": tipo,
                "sala": meta.get("sala", "—"),
                "anio": meta.get("anio") or meta.get("año"),
                "areas": meta.get("areas") or [],
                "temas": meta.get("temas") or [],
                "tesis": meta.get("tesis"),
                "texto_busqueda": r["texto"],
                "tokens_est": r["tokens_est"],
                "doc_id": r["doc_id"],
                "doc_filename": r["filename"],
                "page": r["page"],
                "_source": "rag_chunks",
            })
    return out


def rag_stats() -> dict:
    with db() as c:
        total_docs = c.execute("SELECT COUNT(*) c FROM rag_documents").fetchone()["c"]
        pending = c.execute("SELECT COUNT(*) c FROM rag_documents WHERE status IN ('uploaded','processing','processed')").fetchone()["c"]
        approved = c.execute("SELECT COUNT(*) c FROM rag_documents WHERE status='approved'").fetchone()["c"]
        chunks = c.execute("SELECT COUNT(*) c FROM rag_chunks WHERE active=1").fetchone()["c"]
        chunks_appr = c.execute(
            """SELECT COUNT(*) c FROM rag_chunks ch
               JOIN rag_documents d ON d.id=ch.doc_id
               WHERE ch.active=1 AND d.status='approved'"""
        ).fetchone()["c"]
    return {
        "total_documents": total_docs,
        "pending_approval": pending,
        "approved": approved,
        "total_chunks": chunks,
        "chunks_in_rag": chunks_appr,
    }


# ── Landings multi-vertical ───────────────────────────────────────────────────

def crear_landing(slug: str, title: str, h1: str, h1_resaltado: str = "",
                  subtitulo: str = "", area_focus: Optional[str] = None,
                  accionado_label: str = "Entidad accionada",
                  accionado_placeholder: str = "",
                  video_url: str = "", casos_filtro: Optional[list] = None,
                  casos_extra: Optional[list] = None,
                  faq_extra: Optional[list] = None,
                  cta_texto: str = "Conocer mi caso",
                  color_acento: str = "",
                  utm_default: str = "",
                  # nuevos campos (todos opcionales)
                  hero_icon: str = "",
                  casos_curados: Optional[list] = None,
                  prompt_template: str = "",
                  pretensiones_template: Optional[list] = None,
                  pruebas_sugeridas: str = "",
                  medida_provisional_arg: str = "",
                  tone: str = "",
                  stats_custom: Optional[list] = None,
                  trust_block: Optional[list] = None,
                  footer_extra: str = "") -> int:
    with db() as c:
        cur = c.execute(
            """INSERT INTO landings(slug,title,h1,h1_resaltado,subtitulo,area_focus,
                  accionado_label,accionado_placeholder,video_url,casos_filtro,
                  casos_extra,faq_extra,cta_texto,color_acento,utm_default,active,
                  hero_icon, casos_curados, prompt_template, pretensiones_template,
                  pruebas_sugeridas, medida_provisional_arg, tone, stats_custom,
                  trust_block, footer_extra)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1, ?,?,?,?,?,?,?,?,?,?)""",
            (slug, title, h1, h1_resaltado, subtitulo, area_focus,
             accionado_label, accionado_placeholder, video_url,
             json.dumps(casos_filtro or []),
             json.dumps(casos_extra or []),
             json.dumps(faq_extra or []),
             cta_texto, color_acento, utm_default,
             hero_icon, json.dumps(casos_curados or []),
             prompt_template, json.dumps(pretensiones_template or []),
             pruebas_sugeridas, medida_provisional_arg, tone,
             json.dumps(stats_custom or []), json.dumps(trust_block or []),
             footer_extra),
        )
        return cur.lastrowid


def get_landing_by_slug(slug: str) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM landings WHERE slug=? AND active=1", (slug,)).fetchone()
        if not r: return None
        d = dict(r)
        for k in ("casos_filtro","casos_extra","faq_extra","casos_curados",
                   "pretensiones_template","stats_custom","trust_block"):
            try: d[k] = json.loads(d.get(k) or "[]")
            except Exception: d[k] = []
        return d


def get_landing(lid: int) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM landings WHERE id=?", (lid,)).fetchone()
        if not r: return None
        d = dict(r)
        for k in ("casos_filtro","casos_extra","faq_extra","casos_curados",
                   "pretensiones_template","stats_custom","trust_block"):
            try: d[k] = json.loads(d.get(k) or "[]")
            except Exception: d[k] = []
        return d


def list_landings(active_only: bool = False) -> list[dict]:
    sql = "SELECT * FROM landings"
    if active_only: sql += " WHERE active=1"
    sql += " ORDER BY created_at DESC"
    out = []
    with db() as c:
        for r in c.execute(sql):
            d = dict(r)
            for k in ("casos_filtro","casos_extra","faq_extra","casos_curados",
                       "pretensiones_template","stats_custom","trust_block"):
                try: d[k] = json.loads(d.get(k) or "[]")
                except Exception: d[k] = []
            out.append(d)
    return out


_LANDING_FIELDS = {
    "slug","title","h1","h1_resaltado","subtitulo","area_focus",
    "accionado_label","accionado_placeholder","video_url",
    "casos_filtro","casos_extra","faq_extra",
    "cta_texto","color_acento","utm_default","active",
    "hero_icon","casos_curados","prompt_template","pretensiones_template",
    "pruebas_sugeridas","medida_provisional_arg","tone","stats_custom",
    "trust_block","footer_extra",
}
_LANDING_JSON_FIELDS = {"casos_filtro","casos_extra","faq_extra","casos_curados",
                        "pretensiones_template","stats_custom","trust_block"}


def update_landing(lid: int, **fields) -> Optional[dict]:
    if not fields: return get_landing(lid)
    fields = {k:v for k,v in fields.items() if k in _LANDING_FIELDS}
    for k in _LANDING_JSON_FIELDS:
        if k in fields and not isinstance(fields[k], str):
            fields[k] = json.dumps(fields[k])
    fields["updated_at"] = datetime.now().isoformat()
    cols = ", ".join(f"{k}=?" for k in fields)
    with db() as c:
        c.execute(f"UPDATE landings SET {cols} WHERE id=?", (*fields.values(), lid))
    return get_landing(lid)


def delete_landing(lid: int) -> None:
    with db() as c:
        c.execute("DELETE FROM landings WHERE id=?", (lid,))


def landing_metrics(slug: str, days: int = 30) -> dict:
    """Eventos por landing en los últimos N días (page_view, register, etc)."""
    days = int(days)
    with db() as c:
        rows = c.execute(
            f"""SELECT type, COUNT(*) c, COUNT(DISTINCT ip) uniq
                FROM events
                WHERE ts > datetime('now','-{days} days')
                  AND json_extract(payload,'$.landing')=?
                GROUP BY type""",
            (slug,)
        ).fetchall()
    return {r["type"]: {"total": r["c"], "uniq": r["uniq"]} for r in rows}


def utm_breakdown(days: int = 30) -> list[dict]:
    """Agrupa eventos page_view por utm_source para análisis de tráfico."""
    days = int(days)
    out = []
    with db() as c:
        rows = c.execute(
            f"""SELECT
                  json_extract(payload,'$.utm_source')   as src,
                  json_extract(payload,'$.utm_campaign') as cam,
                  json_extract(payload,'$.landing')      as ld,
                  COUNT(*) total,
                  COUNT(DISTINCT ip) uniq
                FROM events
                WHERE ts > datetime('now','-{days} days') AND type='page_view'
                GROUP BY src, cam, ld
                ORDER BY total DESC LIMIT 100"""
        ).fetchall()
        for r in rows:
            out.append({
                "utm_source": r["src"] or "(directo)",
                "utm_campaign": r["cam"] or "(sin campaña)",
                "landing": r["ld"] or "(home)",
                "total": r["total"],
                "uniq": r["uniq"],
            })
    return out


# ── Vista de jurisprudencia (paginada para auditoría) ─────────────────────────

def jurisprudencia_paginada(page: int = 1, per_page: int = 50,
                             sala: Optional[str] = None,
                             area: Optional[str] = None,
                             anio: Optional[int] = None,
                             fuente: Optional[str] = None,    # csj | pdf
                             search: Optional[str] = None) -> dict:
    """Lista combinada de fichas CSJ (del JSONL) + chunks de PDFs aprobados.
    Para tab admin de auditoría."""
    fichas: list[dict] = []

    # 1) Fichas CSJ desde el JSONL
    if fuente in (None, "csj"):
        from pathlib import Path as _P
        idx_path = _P(__file__).parent.parent / "indices" / "fichas_index.jsonl"
        if idx_path.exists():
            with open(idx_path, encoding="utf-8") as f:
                for linea in f:
                    try:
                        f_obj = json.loads(linea)
                        f_obj["_fuente"] = "csj"
                        fichas.append(f_obj)
                    except json.JSONDecodeError:
                        continue

    # 2) Chunks de PDFs (todos los aprobados, no sólo activos)
    if fuente in (None, "pdf"):
        with db() as c:
            rows = c.execute(
                """SELECT c.*, d.filename, d.metadata, d.status
                   FROM rag_chunks c JOIN rag_documents d ON d.id=c.doc_id
                   WHERE c.active=1"""
            ).fetchall()
            for r in rows:
                try: meta = json.loads(r["metadata"] or "{}")
                except Exception: meta = {}
                fichas.append({
                    "id": f"PDF-{r['doc_id']}-c{r['chunk_index']}",
                    "tipo": meta.get("tipo") or "doc",
                    "sala": meta.get("sala", "—"),
                    "anio": meta.get("anio") or meta.get("año"),
                    "areas": meta.get("areas") or [],
                    "temas": meta.get("temas") or [],
                    "tesis": meta.get("tesis"),
                    "texto_busqueda": r["texto"],
                    "_fuente": "pdf",
                    "_doc_filename": r["filename"],
                    "_doc_status": r["status"],
                    "_page": r["page"],
                    "_chunk_index": r["chunk_index"],
                })

    # 3) Filtros
    def matches(f):
        if sala and (f.get("sala") or "").upper() != sala.upper(): return False
        if area and area not in (f.get("areas") or []): return False
        if anio:
            try:
                if int(f.get("anio") or 0) != anio: return False
            except Exception: return False
        if search:
            s = search.lower()
            blob = (f.get("texto_busqueda","") + " " + str(f.get("temas",""))).lower()
            if s not in blob: return False
        return True

    fichas = [f for f in fichas if matches(f)]
    total = len(fichas)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": fichas[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total else 0,
    }


def jurisprudencia_stats() -> dict:
    """Resumen para el header del tab: total CSJ, total PDFs aprobados, por área."""
    csj = 0
    from pathlib import Path as _P
    idx_path = _P(__file__).parent.parent / "indices" / "fichas_index.jsonl"
    if idx_path.exists():
        with open(idx_path, encoding="utf-8") as f:
            csj = sum(1 for _ in f)
    with db() as c:
        pdf_chunks = c.execute(
            "SELECT COUNT(*) c FROM rag_chunks WHERE active=1"
        ).fetchone()["c"]
        pdf_docs = c.execute(
            "SELECT COUNT(DISTINCT doc_id) c FROM rag_chunks WHERE active=1"
        ).fetchone()["c"]
        pdf_aprobados = c.execute(
            "SELECT COUNT(*) c FROM rag_documents WHERE status='approved'"
        ).fetchone()["c"]
    return {
        "csj_fichas": csj,
        "pdf_chunks": pdf_chunks,
        "pdf_docs": pdf_docs,
        "pdf_aprobados": pdf_aprobados,
    }


# ── Expedientes (con OTP de aceptación del cliente y bitácora silenciosa) ────

import secrets as _ssec_exp
import time as _t_exp


def _next_expediente_numero() -> str:
    """Numerador correlativo GH-YYYY-NNN."""
    yr = datetime.now().strftime("%Y")
    with db() as c:
        r = c.execute("SELECT numero FROM expedientes WHERE numero LIKE ? ORDER BY id DESC LIMIT 1",
                      (f"GH-{yr}-%",)).fetchone()
    if not r or not r["numero"]:
        return f"GH-{yr}-001"
    try:
        n = int(r["numero"].split("-")[-1]) + 1
        return f"GH-{yr}-{n:03d}"
    except Exception:
        return f"GH-{yr}-001"


def _audit_append(audit_log_json: Optional[str], evento: str, **data) -> str:
    try: arr = json.loads(audit_log_json or "[]")
    except Exception: arr = []
    entry = {"evento": evento, "ts": datetime.now().isoformat(), **data}
    arr.append(entry)
    return json.dumps(arr, ensure_ascii=False)


def _audit_log_to_dict(json_str: Optional[str]) -> list:
    try: return json.loads(json_str or "[]")
    except Exception: return []


def crear_expediente(lead_id: int, lawyer_id: Optional[int],
                     by_lawyer_id: Optional[int],
                     alcance: str = "", area: str = "",
                     honorarios_cop: Optional[int] = None,
                     honorarios_modalidad: str = "fijo",
                     honorarios_descripcion: str = "",
                     obligaciones_cliente: str = "") -> dict:
    """Crea un expediente en estado 'borrador'. Genera token público y número correlativo."""
    numero = _next_expediente_numero()
    token = _ssec_exp.token_hex(16)
    audit = _audit_append(None, "expediente.creado",
                          by_lawyer_id=by_lawyer_id, lead_id=lead_id, numero=numero)
    with db() as c:
        cur = c.execute(
            """INSERT INTO expedientes(lead_id, lawyer_id, numero, token, estado, area,
                  honorarios_cop, honorarios_modalidad, honorarios_descripcion,
                  alcance, obligaciones_cliente, audit_log)
               VALUES(?,?,?,?, 'borrador', ?,?,?,?,?,?, ?)""",
            (lead_id, lawyer_id, numero, token, area, honorarios_cop,
             honorarios_modalidad, honorarios_descripcion, alcance, obligaciones_cliente, audit),
        )
        eid = cur.lastrowid
    return get_expediente(eid)


def get_expediente(eid: int) -> Optional[dict]:
    with db() as c:
        r = c.execute("""SELECT e.*, l.name as lead_name, l.cedula as lead_cedula,
                                l.phone as lead_phone, l.email as lead_email,
                                l.descripcion as lead_descripcion,
                                w.name as lawyer_name, w.email as lawyer_email
                         FROM expedientes e
                         LEFT JOIN leads l ON l.id = e.lead_id
                         LEFT JOIN lawyers w ON w.id = e.lawyer_id
                         WHERE e.id=?""", (eid,)).fetchone()
        if not r: return None
        d = dict(r)
        d["audit_log"] = _audit_log_to_dict(d.get("audit_log"))
        return d


def get_expediente_by_token(token: str) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT * FROM expedientes WHERE token=?", (token,)).fetchone()
        if not r: return None
        d = dict(r); d["audit_log"] = _audit_log_to_dict(d.get("audit_log")); return d


def list_expedientes(lawyer_id: Optional[int] = None,
                     estado: Optional[str] = None, limit: int = 200) -> list[dict]:
    sql = """SELECT e.*, l.name as lead_name, l.phone as lead_phone, l.email as lead_email
             FROM expedientes e LEFT JOIN leads l ON l.id = e.lead_id
             WHERE 1=1"""
    params: list = []
    if lawyer_id: sql += " AND e.lawyer_id=?"; params.append(lawyer_id)
    if estado:    sql += " AND e.estado=?";    params.append(estado)
    sql += " ORDER BY e.created_at DESC LIMIT ?"; params.append(limit)
    out = []
    with db() as c:
        for r in c.execute(sql, params):
            d = dict(r); d["audit_log"] = _audit_log_to_dict(d.get("audit_log")); out.append(d)
    return out


def update_expediente(eid: int, by_lawyer_id: Optional[int] = None, **fields) -> Optional[dict]:
    """Campos válidos: alcance, area, honorarios_cop, honorarios_modalidad,
    honorarios_descripcion, obligaciones_cliente, estado, closed_reason."""
    if not fields: return get_expediente(eid)
    allowed = {"alcance","area","honorarios_cop","honorarios_modalidad",
               "honorarios_descripcion","obligaciones_cliente","estado","closed_reason"}
    fields = {k:v for k,v in fields.items() if k in allowed}
    if not fields: return get_expediente(eid)
    with db() as c:
        prev = c.execute("SELECT estado, audit_log FROM expedientes WHERE id=?", (eid,)).fetchone()
        if not prev: return None
        cols = ", ".join(f"{k}=?" for k in fields)
        c.execute(f"UPDATE expedientes SET {cols} WHERE id=?", (*fields.values(), eid))
        # bitácora
        evento = "estado.cambiado" if "estado" in fields and fields["estado"] != prev["estado"] else "expediente.modificado"
        new_log = _audit_append(prev["audit_log"], evento,
                                 by_lawyer_id=by_lawyer_id, cambios=list(fields.keys()),
                                 from_state=prev["estado"] if "estado" in fields else None,
                                 to_state=fields.get("estado"))
        c.execute("UPDATE expedientes SET audit_log=? WHERE id=?", (new_log, eid))
        if fields.get("estado") == "cerrado":
            c.execute("UPDATE expedientes SET closed_at=datetime('now') WHERE id=?", (eid,))
    return get_expediente(eid)


def expediente_set_otp(eid: int, otp: str, ttl_seconds: int = 1800,
                       by_lawyer_id: Optional[int] = None,
                       phone: Optional[str] = None) -> None:
    """Guarda OTP con expiración (default 30 min) y registra envío en bitácora."""
    expires = datetime.now().timestamp() + ttl_seconds
    with db() as c:
        prev = c.execute("SELECT audit_log FROM expedientes WHERE id=?", (eid,)).fetchone()
        new_log = _audit_append(prev["audit_log"] if prev else None,
                                 "otp.enviado_cliente",
                                 by_lawyer_id=by_lawyer_id, phone=phone, ttl_seconds=ttl_seconds)
        c.execute(
            """UPDATE expedientes
               SET otp=?, otp_expires=?, estado='pendiente_aceptacion',
                   audit_log=?, otp_attempts=0
               WHERE id=?""",
            (otp, str(expires), new_log, eid),
        )


def expediente_verificar_otp(token: str, otp_in: str, ip: str = "") -> dict:
    """Retorna {ok, expediente|error}. Marca aceptado_at + IP si OK."""
    with db() as c:
        r = c.execute("SELECT * FROM expedientes WHERE token=?", (token,)).fetchone()
        if not r: return {"ok": False, "error": "Expediente no encontrado"}
        if r["estado"] != "pendiente_aceptacion":
            return {"ok": False, "error": f"Estado inválido: {r['estado']}"}
        if r["otp_attempts"] >= 5:
            return {"ok": False, "error": "Demasiados intentos. Solicita reenvío."}
        # validar TTL
        try: expires = float(r["otp_expires"] or 0)
        except: expires = 0
        if datetime.now().timestamp() > expires:
            return {"ok": False, "error": "El código expiró. Solicita uno nuevo."}
        if (otp_in or "").strip() != (r["otp"] or ""):
            c.execute("UPDATE expedientes SET otp_attempts = otp_attempts+1 WHERE id=?", (r["id"],))
            return {"ok": False, "error": "Código incorrecto."}
        # OK!
        new_log = _audit_append(r["audit_log"], "otp.aceptado_cliente",
                                 ip=ip[:64], intento=(r["otp_attempts"] or 0) + 1)
        c.execute(
            """UPDATE expedientes
               SET estado='aceptado', accepted_at=datetime('now'), accepted_ip=?,
                   otp=NULL, otp_expires=NULL, audit_log=?
               WHERE id=?""",
            (ip[:64], new_log, r["id"]),
        )
    return {"ok": True, "expediente": get_expediente(r["id"])}


def expediente_log_evento(eid: int, evento: str, **data) -> None:
    """Helper genérico para que cualquier parte del sistema agregue al audit_log."""
    with db() as c:
        r = c.execute("SELECT audit_log FROM expedientes WHERE id=?", (eid,)).fetchone()
        if not r: return
        new_log = _audit_append(r["audit_log"], evento, **data)
        c.execute("UPDATE expedientes SET audit_log=? WHERE id=?", (new_log, eid))


def get_expediente_by_lead(lead_id: int) -> Optional[dict]:
    with db() as c:
        r = c.execute("SELECT id FROM expedientes WHERE lead_id=? ORDER BY created_at DESC LIMIT 1",
                      (lead_id,)).fetchone()
        return get_expediente(r["id"]) if r else None


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
        if "role" not in cols:
            c.execute("ALTER TABLE lawyers ADD COLUMN role TEXT NOT NULL DEFAULT 'lawyer'")

        # Migración landings: campos de identidad y motor por vertical
        cols_l = {r["name"] for r in c.execute("PRAGMA table_info(landings)")}
        nuevas_l = {
            "hero_icon":            "TEXT",
            "casos_curados":        "TEXT",      # JSON: [{ic,tt,ds,ej,area}]
            "prompt_template":      "TEXT",      # texto que reemplaza el prompt genérico
            "pretensiones_template":"TEXT",      # JSON lista de pretensiones tipo
            "pruebas_sugeridas":    "TEXT",      # bloque de pruebas tipo
            "medida_provisional_arg":"TEXT",     # argumento específico
            "tone":                 "TEXT",      # 'urgente'|'explicativo'|'reivindicativo'
            "stats_custom":         "TEXT",      # JSON [{num,label}] reemplaza stats bar
            "trust_block":          "TEXT",      # JSON [{title,desc}] reemplaza el "Por qué confiar"
            "footer_extra":         "TEXT",      # texto disclaimer/links extra
        }
        for col, tipo in nuevas_l.items():
            if col not in cols_l:
                c.execute(f"ALTER TABLE landings ADD COLUMN {col} {tipo}")


# ── Bootstrap ─────────────────────────────────────────────────────────────────

def bootstrap_default_lawyer() -> None:
    """Si no hay abogados y hay env LAWYER_WHATSAPP, crea uno default.
    También siembra 4 landings verticales si la tabla está vacía."""
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

    # Seed / upgrade de 4 landings verticales.
    # - Si no existe la landing del slug → se crea con la config rica.
    # - Si existe pero le falta prompt_template (seed antiguo "delgado")
    #   → se enriquece in-place SIN tocar campos personalizados existentes
    #   distintos de los que aporta el seed.
    seeds = _vertical_seeds()
    with db() as c:
        existentes = {
            r["slug"]: r["id"]
            for r in c.execute("SELECT id, slug FROM landings")
        }
        delgadas = {
            r["slug"]: r["id"]
            for r in c.execute(
                "SELECT id, slug FROM landings "
                "WHERE COALESCE(prompt_template,'')='' "
                "   OR COALESCE(casos_curados,'[]')='[]'"
            )
        }
    for s in seeds:
        slug = s["slug"]
        if slug not in existentes:
            try:
                crear_landing(**s)
                print(f"[db] landing creada: {slug}")
            except Exception as e:
                print(f"[db] error creando landing {slug}: {e}")
        elif slug in delgadas:
            try:
                payload = {k: v for k, v in s.items() if k != "slug"}
                update_landing(delgadas[slug], **payload)
                print(f"[db] landing enriquecida con seed rico: {slug}")
            except Exception as e:
                print(f"[db] error enriqueciendo landing {slug}: {e}")


# ---------------------------------------------------------------------------
# Seeds verticales: cada landing es un PRODUCTO ÚNICO con su propio motor RAG
# (prompt_template, pretensiones, pruebas, casos curados, identidad visual).
# ---------------------------------------------------------------------------
def _vertical_seeds() -> list[dict]:
    """4 landings verticales completas. Cada una tiene:
       - identidad visual (color_acento, hero_icon, tone)
       - motor RAG propio (prompt_template + area_focus estricto)
       - casos curados (no derivados del catálogo genérico)
       - FAQ específico, pretensiones tipo, pruebas sugeridas,
         argumento de medida provisional, stats y trust_block propios.
    """
    return [
        # ============== 1) TUTELAS · genérica (oro institucional) ==============
        {
            "slug": "tutelas",
            "title": "Acciones de tutela · Galeano Herrera",
            "h1": "Te están negando un derecho. Recupéralo en 10 días.",
            "h1_resaltado": "negando un derecho",
            "subtitulo": "Salud, pensión, debido proceso, mínimo vital. Generamos tu tutela citando sentencias reales de la Corte Constitucional y Suprema. Sin cobro adelantado.",
            "area_focus": None,
            "accionado_label": "Entidad accionada (EPS, Colpensiones, alcaldía, etc.)",
            "accionado_placeholder": "Ej: Sanitas EPS, Colpensiones, Secretaría de Salud…",
            "casos_filtro": ["derechos_fundamentales", "salud", "seguridad_social"],
            "cta_texto": "Generar mi tutela ahora",
            "color_acento": "#C5A059",
            "hero_icon": "⚖️",
            "tone": "explicativo",
            "utm_default": "tutelas-genericas",
            "casos_curados": [
                {"ic": "🏥", "tt": "EPS niega cirugía o medicamento",
                 "ds": "La Corte ha protegido el derecho a la salud cuando la EPS demora autorizaciones. Tutela en 10 días con orden de cumplimiento inmediato.",
                 "ej": "T-760/2008, T-121/2024", "area": "salud"},
                {"ic": "👴", "tt": "Colpensiones no reconoce pensión",
                 "ds": "Mora administrativa, no respuesta a derecho de petición o negativa injustificada de pensión de vejez/invalidez/sobrevivientes.",
                 "ej": "T-082/2022, SU-005/2018", "area": "seguridad_social"},
                {"ic": "🏛️", "tt": "Entidad pública no responde tu derecho de petición",
                 "ds": "Toda entidad debe responder en 15 días hábiles. Si no, la tutela ordena respuesta de fondo en 48 horas.",
                 "ej": "T-377/2000, T-149/2013", "area": "derechos_fundamentales"},
                {"ic": "🍼", "tt": "Mínimo vital y subsistencia",
                 "ds": "No pago de salarios, suspensión arbitraria de subsidios, retención indebida de prestaciones que afectan tu subsistencia digna.",
                 "ej": "T-211/2011, T-406/1992", "area": "derechos_fundamentales"},
            ],
            "faq_extra": [
                {"q": "¿En cuántos días me responden la tutela?",
                 "a": "El juez tiene máximo 10 días hábiles para fallar (Decreto 2591/91, art. 29). Si hay perjuicio irremediable, podemos pedir medida provisional para protección inmediata."},
                {"q": "¿Necesito abogado para presentar tutela?",
                 "a": "No. La tutela es informal y puede presentarla cualquier persona. Pero un texto bien estructurado, con jurisprudencia citada, multiplica las probabilidades de éxito."},
                {"q": "¿Qué pasa si pierdo en primera instancia?",
                 "a": "Tienes 3 días para impugnar. El superior decide en 20 días. Si pierdes ahí, el expediente sube a la Corte Constitucional para eventual revisión."},
            ],
            "prompt_template": (
                "Eres un asistente jurídico colombiano especializado en ACCIONES DE TUTELA. "
                "Redacta un borrador formal de tutela ante un juez constitucional, citando jurisprudencia real "
                "de la Corte Constitucional y la Corte Suprema de Justicia.\n\n"
                "DATOS DEL ACCIONANTE:\n"
                "- Nombre: {{nombre}}\n- Cédula: {{cedula}}\n- Ciudad: {{ciudad}}\n"
                "- Accionado: {{accionado}}\n- Contacto: {{phone}} / {{email}}\n\n"
                "HECHOS NARRADOS POR EL ACCIONANTE:\n{{descripcion}}\n\n"
                "JURISPRUDENCIA RELEVANTE (úsala literal con número de sentencia):\n{{contexto_juris}}\n\n"
                "ESTRUCTURA OBLIGATORIA:\n"
                "1) Encabezado (Señor Juez Constitucional de Reparto, ciudad y fecha).\n"
                "2) Identificación del accionante y accionado.\n"
                "3) HECHOS numerados (mínimo 5).\n"
                "4) DERECHOS FUNDAMENTALES VULNERADOS (cita artículos 23, 29, 49, 53 CP según aplique).\n"
                "5) FUNDAMENTOS DE DERECHO (cita 2-3 sentencias del contexto, con número y línea jurisprudencial).\n"
                "6) PRETENSIONES (qué se ordene al accionado, plazo).\n"
                "7) MEDIDA PROVISIONAL si hay perjuicio irremediable (art. 7 D.2591/91).\n"
                "8) JURAMENTO de no haber presentado otra tutela por los mismos hechos.\n"
                "9) PRUEBAS y ANEXOS.\n"
                "10) NOTIFICACIONES.\n\n"
                "Tono: técnico-jurídico pero claro. NO inventes sentencias. Si falta un dato del accionante, deja "
                "[COMPLETAR …] entre corchetes."
            ),
            "pretensiones_template": [
                "Tutelar los derechos fundamentales invocados.",
                "Ordenar al accionado realizar/abstenerse de [conducta] en un plazo no superior a 48 horas.",
                "Ordenar al accionado abstenerse de incurrir nuevamente en la conducta vulneradora.",
                "Compulsar copias a los entes de control si se evidencia falla del servicio.",
            ],
            "pruebas_sugeridas": (
                "• Copia de la cédula del accionante.\n"
                "• Copia del derecho de petición presentado y constancia de radicado.\n"
                "• Respuesta (o silencio) del accionado.\n"
                "• Historia clínica / formulario de pensión / contrato según aplique.\n"
                "• Cualquier comunicación con la entidad (correos, capturas, oficios)."
            ),
            "medida_provisional_arg": (
                "Existe perjuicio irremediable porque la afectación es ACTUAL, GRAVE, INMINENTE e IMPOSTERGABLE: "
                "la demora en la protección consolida un daño en el derecho fundamental que no admite reparación "
                "ulterior. Por ello, con fundamento en el art. 7 del Decreto 2591/91, se solicita medida provisional."
            ),
            "stats_custom": [
                {"num": "10 días", "label": "fallo legal máximo"},
                {"num": "+450", "label": "tutelas redactadas"},
                {"num": "94%", "label": "ordenadas a favor"},
                {"num": "$0", "label": "sin costo adelantado"},
            ],
            "trust_block": [
                {"title": "Autoridad real",
                 "desc": "Citamos sentencias verificables de la Corte Constitucional y Suprema. Cero invención."},
                {"title": "Sin costo oculto",
                 "desc": "Borrador y revisión inicial sin cobro. Solo facturamos si tu caso requiere acompañamiento procesal."},
                {"title": "Tus datos protegidos",
                 "desc": "Habeas data Ley 1581/2012. Nunca compartimos tu información sin autorización expresa."},
            ],
            "footer_extra": "Acción de tutela: Decreto 2591/1991 · Constitución Política, art. 86.",
        },

        # ============== 2) ACCIDENTES · SOAT (naranja urgencia) ==============
        {
            "slug": "accidentes",
            "title": "Indemnización por accidente de tránsito · SOAT",
            "h1": "Tuviste un accidente y la aseguradora no responde. Reclama lo que te corresponde.",
            "h1_resaltado": "no responde",
            "subtitulo": "SOAT, póliza de responsabilidad civil contractual y extracontractual, lucro cesante, daño emergente y pérdida de capacidad laboral. Reclamación administrativa y, si toca, tutela.",
            "area_focus": "accidentes",
            "accionado_label": "Aseguradora o entidad responsable",
            "accionado_placeholder": "Ej: Seguros Bolívar, Sura, Mundial, Positiva…",
            "casos_filtro": ["accidentes", "derechos_fundamentales", "salud"],
            "cta_texto": "Calcular mi indemnización",
            "color_acento": "#ea580c",
            "hero_icon": "🚗",
            "tone": "urgente",
            "utm_default": "accidentes-soat",
            "casos_curados": [
                {"ic": "🚑", "tt": "SOAT no cubre toda la atención médica",
                 "ds": "El SOAT cubre hasta 800 SMDLV en gastos médicos. Si la EPS o el hospital se niegan, la Corte ha ordenado atención inmediata vía tutela.",
                 "ej": "T-503/2022, T-127/2023", "area": "accidentes"},
                {"ic": "💰", "tt": "Indemnización por incapacidad permanente",
                 "ds": "Pérdida de capacidad laboral mayor al 5%: derecho a indemnización por la aseguradora del vehículo causante. Tope SOAT + póliza RCE.",
                 "ej": "Ley 769/2002 art. 110, T-032/2024", "area": "accidentes"},
                {"ic": "⚰️", "tt": "Muerte y gastos funerarios",
                 "ds": "SOAT paga 750 SMDLV por muerte y 150 SMDLV por gastos funerarios al beneficiario legal. Reclamación administrativa primero, tutela si demoran.",
                 "ej": "Decreto 056/2015", "area": "accidentes"},
                {"ic": "🏍️", "tt": "Vehículo fantasma o sin SOAT",
                 "ds": "El FOSYGA / ADRES Subcuenta ECAT cubre cuando el vehículo causante es desconocido o no tiene SOAT. Reclamación específica.",
                 "ej": "Ley 100/93 art. 167", "area": "accidentes"},
            ],
            "faq_extra": [
                {"q": "¿Cuánto cubre realmente el SOAT?",
                 "a": "Hasta 800 SMDLV por gastos médicos, 750 SMDLV por muerte, 180 SMDLV por incapacidad permanente y 300 SMDLV por incapacidad temporal. Excedentes los cubre la EPS o póliza RCE."},
                {"q": "¿Qué pasa si la aseguradora niega el pago?",
                 "a": "Primero reclamación administrativa con sustento médico (Resolución 1915/2008). Si guarda silencio o niega sin justa causa, procede tutela por vulneración al mínimo vital y a la salud."},
                {"q": "¿Tengo derecho a lucro cesante?",
                 "a": "Sí, si el accidente te impidió trabajar. Se calcula según los días de incapacidad por tu salario o ingreso promedio, demostrado con declaración de renta o certificación laboral."},
            ],
            "prompt_template": (
                "Eres un asistente jurídico colombiano especializado en RECLAMACIONES POR ACCIDENTES DE TRÁNSITO. "
                "Redacta el documento que corresponda según los hechos: reclamación administrativa ante aseguradora, "
                "o tutela si hay urgencia médica o vulneración al mínimo vital.\n\n"
                "DATOS DEL RECLAMANTE:\n"
                "- Nombre: {{nombre}}\n- Cédula: {{cedula}}\n- Ciudad: {{ciudad}}\n"
                "- Aseguradora/responsable: {{accionado}}\n- Contacto: {{phone}} / {{email}}\n\n"
                "HECHOS DEL ACCIDENTE:\n{{descripcion}}\n\n"
                "JURISPRUDENCIA Y NORMATIVA RELEVANTE:\n{{contexto_juris}}\n\n"
                "ESTRUCTURA OBLIGATORIA:\n"
                "1) Encabezado (destinatario: aseguradora o juez según caso, ciudad y fecha).\n"
                "2) Identificación del reclamante y del vehículo causante (si se conoce placa).\n"
                "3) HECHOS DEL ACCIDENTE (fecha, lugar, descripción, gravedad).\n"
                "4) AMPAROS RECLAMADOS:\n"
                "   - Gastos médicos (SOAT hasta 800 SMDLV)\n"
                "   - Incapacidad temporal/permanente\n"
                "   - Lucro cesante y daño emergente\n"
                "   - Daño moral si aplica\n"
                "5) FUNDAMENTO LEGAL: Ley 769/2002 (CNT), Decreto 056/2015 (SOAT), Decreto 1072/2015 si laboral, "
                "Sentencias citadas del contexto.\n"
                "6) PRETENSIONES con CIFRAS aproximadas en SMDLV.\n"
                "7) DOCUMENTOS QUE SE ADJUNTAN (historia clínica, FURIPS, FURTRAN, certificación laboral).\n"
                "8) PLAZO LEGAL DE RESPUESTA (15 días hábiles, Resolución 1915/2008).\n"
                "9) Anuncio de tutela y denuncia ante SuperFinanciera si no hay respuesta.\n\n"
                "Tono: contundente, técnico, con cifras claras. NO inventes pólizas ni montos. "
                "Si falta un dato, deja [COMPLETAR …]."
            ),
            "pretensiones_template": [
                "Reconocer y pagar la totalidad de los gastos médicos derivados del accidente.",
                "Reconocer indemnización por incapacidad temporal/permanente conforme dictamen de pérdida de capacidad laboral.",
                "Pagar lucro cesante por los días dejados de laborar.",
                "Pagar daño emergente (transporte a citas, medicamentos no POS, terapias).",
                "Reconocer daño moral conforme tasación de la Corte Suprema (Sala Civil).",
            ],
            "pruebas_sugeridas": (
                "• Informe Policial de Accidente de Tránsito (IPAT).\n"
                "• FURIPS y FURTRAN (formularios SOAT).\n"
                "• Historia clínica completa y epicrisis.\n"
                "• Dictamen de pérdida de capacidad laboral (JRCI o EPS).\n"
                "• Facturas de gastos médicos no cubiertos.\n"
                "• Certificación laboral y/o declaración de renta para cálculo de lucro cesante.\n"
                "• Copia del SOAT del vehículo causante (si se obtuvo)."
            ),
            "medida_provisional_arg": (
                "El accionante requiere atención médica continua y los recursos para subsistencia mientras se "
                "recupera. La negativa o demora de la aseguradora vulnera el mínimo vital y la salud. Se solicita "
                "medida provisional ordenando autorización inmediata de servicios médicos y pago anticipado de "
                "incapacidad temporal."
            ),
            "stats_custom": [
                {"num": "800 SMDLV", "label": "tope médico SOAT"},
                {"num": "15 días", "label": "plazo legal de respuesta"},
                {"num": "+180", "label": "reclamaciones tramitadas"},
                {"num": "$0", "label": "sin pago hasta cobrar"},
            ],
            "trust_block": [
                {"title": "Cifras claras desde el día 1",
                 "desc": "Te decimos exactamente cuánto te corresponde según tu caso, sin promesas vacías."},
                {"title": "Aseguradoras conocen nuestro sello",
                 "desc": "Reclamaciones bien sustentadas se pagan más rápido. Sin tecnicismos vacíos."},
                {"title": "Si no cobras, no pagas",
                 "desc": "Honorarios por cuota litis. Solo cobramos si recuperamos tu dinero."},
            ],
            "footer_extra": "Ley 769/2002 (CNT) · Decreto 056/2015 (SOAT) · Resolución 1915/2008 SuperFinanciera.",
        },

        # ============== 3) COMPARENDOS · fotomultas (rojo institucional) ==============
        {
            "slug": "comparendos",
            "title": "Anula tu comparendo o fotomulta · Tutela",
            "h1": "Te llegó un comparendo que no es tuyo o no te notificaron. Anúlalo.",
            "h1_resaltado": "no es tuyo",
            "subtitulo": "Fotomultas sin notificación, comparendos al conductor equivocado, cobros coactivos sin debido proceso. Tutela y recurso de reposición para tumbarlos.",
            "area_focus": "derechos_fundamentales",
            "accionado_label": "Secretaría de Tránsito o Movilidad",
            "accionado_placeholder": "Ej: Secretaría Distrital de Movilidad de Bogotá…",
            "casos_filtro": ["derechos_fundamentales"],
            "cta_texto": "Anular mi comparendo",
            "color_acento": "#c8102e",
            "hero_icon": "🚦",
            "tone": "reivindicativo",
            "utm_default": "comparendos-fotomultas",
            "casos_curados": [
                {"ic": "📸", "tt": "Fotomulta sin notificación personal",
                 "ds": "La C-038/2020 exigió notificación personal al propietario. Sin ello, el comparendo es nulo y no genera ejecutoria.",
                 "ej": "C-038/2020, T-051/2016", "area": "derechos_fundamentales"},
                {"ic": "🚙", "tt": "Vendiste el carro pero te llegan los comparendos",
                 "ds": "Si traspasaste antes del comparendo y el RUNT lo registró, no eres responsable. Recurso de reposición + reclamación al SIMIT.",
                 "ej": "Ley 769/2002 art. 135", "area": "derechos_fundamentales"},
                {"ic": "🧾", "tt": "Cobro coactivo sin debido proceso",
                 "ds": "Te embargan cuenta o vehículo sin mandamiento de pago debidamente notificado. Tutela inmediata por debido proceso (art. 29 CP).",
                 "ej": "T-446/2022, T-156/2019", "area": "derechos_fundamentales"},
                {"ic": "👮", "tt": "Comparendo sin firma del agente o sin testigos",
                 "ds": "El art. 135 del CNT exige requisitos formales. Falla en cualquiera = nulidad. Recurso de reposición y apelación.",
                 "ej": "Ley 769/2002, T-204/2018", "area": "derechos_fundamentales"},
            ],
            "faq_extra": [
                {"q": "¿Cuánto tiempo tengo para impugnar un comparendo?",
                 "a": "11 días hábiles desde la notificación para presentar recurso de reposición ante la autoridad de tránsito. Si pasaron, igual procede tutela si nunca te notificaron en debida forma."},
                {"q": "¿Puedo evitar el cobro coactivo con tutela?",
                 "a": "Sí, cuando vulneraron tu debido proceso (art. 29 CP). La tutela suspende el cobro mientras se decide el fondo. Especialmente útil si te están embargando."},
                {"q": "¿Qué pasa si vendí el carro y me llegan los comparendos?",
                 "a": "Si registraste el traspaso en el RUNT antes del comparendo, no eres responsable. Hay que probarlo y pedir limpieza del SIMIT. Si te lo cobran, procede tutela."},
            ],
            "prompt_template": (
                "Eres un asistente jurídico colombiano especializado en COMPARENDOS Y FOTOMULTAS. "
                "El eje argumentativo es DEBIDO PROCESO (art. 29 CP) y NOTIFICACIÓN PERSONAL "
                "(C-038/2020, Ley 769/2002 art. 135-137). Redacta el documento más eficaz según el caso: "
                "recurso de reposición, tutela, o ambos.\n\n"
                "DATOS DEL ACCIONANTE:\n"
                "- Nombre: {{nombre}}\n- Cédula: {{cedula}}\n- Ciudad: {{ciudad}}\n"
                "- Autoridad de tránsito: {{accionado}}\n- Contacto: {{phone}} / {{email}}\n\n"
                "HECHOS:\n{{descripcion}}\n\n"
                "JURISPRUDENCIA RELEVANTE:\n{{contexto_juris}}\n\n"
                "ESTRUCTURA OBLIGATORIA:\n"
                "1) Encabezado (Juez Constitucional o Secretaría de Movilidad según caso).\n"
                "2) Identificación del accionante y del comparendo (número, fecha, placa).\n"
                "3) HECHOS:\n"
                "   - Fecha del supuesto comparendo\n"
                "   - Cómo se enteró (o no se enteró) del mismo\n"
                "   - Estado actual: notificado, ejecutoriado, en cobro coactivo\n"
                "4) DERECHOS VULNERADOS:\n"
                "   - Debido proceso (art. 29 CP) por falta de notificación personal\n"
                "   - Defensa y contradicción\n"
                "   - Mínimo vital si hay embargo\n"
                "5) FUNDAMENTO JURÍDICO:\n"
                "   - C-038/2020 (notificación personal en fotomultas)\n"
                "   - Ley 769/2002 art. 135-137 (requisitos del comparendo)\n"
                "   - Sentencias del contexto\n"
                "6) PRETENSIONES: nulidad del comparendo, suspensión del cobro coactivo, limpieza del SIMIT.\n"
                "7) MEDIDA PROVISIONAL si hay embargo o reporte negativo activo.\n"
                "8) PRUEBAS: copia del comparendo, certificado del RUNT, prueba de venta del vehículo si aplica.\n\n"
                "Tono: reivindicativo y contundente, citando el debido proceso. NO inventes números de comparendo."
            ),
            "pretensiones_template": [
                "Declarar la nulidad del comparendo Nº [COMPLETAR] por falta de notificación personal.",
                "Ordenar a la autoridad accionada suspender de inmediato cualquier cobro coactivo.",
                "Ordenar la limpieza del registro SIMIT y cualquier reporte negativo asociado.",
                "Levantar las medidas cautelares (embargo de cuenta o vehículo) si fueron ordenadas.",
            ],
            "pruebas_sugeridas": (
                "• Copia del comparendo o fotomulta recibida.\n"
                "• Certificado del SIMIT con el detalle del cobro.\n"
                "• Certificado de tradición del vehículo (RUNT) para probar fechas.\n"
                "• Si vendiste el carro: contrato de compraventa o traspaso registrado.\n"
                "• Si hubo embargo: oficio de embargo y certificación bancaria.\n"
                "• Cualquier comunicación con la autoridad de tránsito."
            ),
            "medida_provisional_arg": (
                "El cobro coactivo en curso o el embargo bancario afectan el mínimo vital del accionante. La "
                "ejecución sin debido proceso causa perjuicio irremediable que no se repara con la decisión "
                "ulterior. Se solicita medida provisional suspendiendo el cobro y levantando el embargo "
                "mientras se resuelve la tutela (art. 7 D.2591/91)."
            ),
            "stats_custom": [
                {"num": "11 días", "label": "para impugnar"},
                {"num": "C-038/2020", "label": "tu mejor argumento"},
                {"num": "+220", "label": "comparendos anulados"},
                {"num": "$0", "label": "consulta inicial"},
            ],
            "trust_block": [
                {"title": "Conocemos el SIMIT al detalle",
                 "desc": "Sabemos qué reportes son ilegítimos y cómo limpiarlos. No es magia, es procedimiento."},
                {"title": "Tutela como bisturí",
                 "desc": "Cuando hay embargo o reporte activo, la tutela suspende el cobro de inmediato."},
                {"title": "Honorarios solo si ganamos",
                 "desc": "No te cobramos por radicar. Cobramos cuando el comparendo queda anulado."},
            ],
            "footer_extra": "Ley 769/2002 (CNT) · Sentencia C-038/2020 · Constitución Política, art. 29.",
        },

        # ============== 4) LABORAL · fuero/despido (morado dignidad) ==============
        {
            "slug": "laboral",
            "title": "Reclamaciones laborales · Despido y derechos",
            "h1": "Te despidieron, no te pagan o te acosan. Recupera lo que es tuyo.",
            "h1_resaltado": "es tuyo",
            "subtitulo": "Fuero materno, fuero de salud, despido por enfermedad, contrato realidad, acoso laboral, no pago de salarios y prestaciones. Tutela laboral con jurisprudencia de la Corte Constitucional y Suprema (Sala Laboral).",
            "area_focus": "laboral",
            "accionado_label": "Empleador o entidad accionada",
            "accionado_placeholder": "Ej: empresa, persona natural empleadora…",
            "casos_filtro": ["laboral"],
            "cta_texto": "Reclamar mis derechos laborales",
            "color_acento": "#7c3aed",
            "hero_icon": "💼",
            "tone": "reivindicativo",
            "utm_default": "laboral-despido",
            "casos_curados": [
                {"ic": "🤰", "tt": "Despido durante embarazo o lactancia",
                 "ds": "Fuero de maternidad: el despido es ineficaz y procede reintegro + salarios dejados de percibir + indemnización de 60 días.",
                 "ej": "SU-070/2013, T-138/2015", "area": "laboral"},
                {"ic": "🩺", "tt": "Despido por enfermedad o incapacidad",
                 "ds": "Estabilidad laboral reforzada (Ley 361/97 art. 26). Despido sin permiso del Ministerio = ineficaz, procede reintegro + 180 días de indemnización.",
                 "ej": "SU-049/2017, T-320/2016", "area": "laboral"},
                {"ic": "📋", "tt": "Contrato realidad (eras empleado disfrazado de OPS)",
                 "ds": "Si había subordinación, prestación personal y salario, era contrato laboral. Procede pago de prestaciones, aportes y sanciones.",
                 "ej": "C-555/1994, T-733/2017", "area": "laboral"},
                {"ic": "💸", "tt": "No pago de salarios o liquidación",
                 "ds": "Mora en pago genera indemnización moratoria del art. 65 CST: un día de salario por cada día de mora, hasta 24 meses.",
                 "ej": "CSJ Sala Laboral SL2851/2020", "area": "laboral"},
            ],
            "faq_extra": [
                {"q": "Si tengo fuero de salud o maternidad, ¿qué hago primero?",
                 "a": "Tutela inmediata por estabilidad laboral reforzada. La Corte ordena reintegro + pago de salarios desde el despido + cotizaciones a seguridad social, en muchos casos en menos de 15 días."},
                {"q": "Me hicieron firmar renuncia, ¿puedo reclamar?",
                 "a": "Sí, si la firma fue forzada, sin libre consentimiento o bajo presión. Es renuncia provocada (despido indirecto). Procede demanda ordinaria laboral con indemnización del art. 64 CST."},
                {"q": "¿Cuánto tiempo tengo para demandar?",
                 "a": "Salarios y prestaciones prescriben a los 3 años. Tutela por fuero o vulneración de derechos no tiene caducidad estricta pero conviene actuar rápido (4-6 meses ideal)."},
            ],
            "prompt_template": (
                "Eres un asistente jurídico colombiano especializado en DERECHO LABORAL Y DE SEGURIDAD SOCIAL. "
                "Determina si el caso requiere TUTELA por estabilidad laboral reforzada (fuero) o DEMANDA "
                "ORDINARIA LABORAL. Redacta el documento que corresponda.\n\n"
                "DATOS DEL TRABAJADOR:\n"
                "- Nombre: {{nombre}}\n- Cédula: {{cedula}}\n- Ciudad: {{ciudad}}\n"
                "- Empleador accionado: {{accionado}}\n- Contacto: {{phone}} / {{email}}\n\n"
                "HECHOS LABORALES:\n{{descripcion}}\n\n"
                "JURISPRUDENCIA RELEVANTE:\n{{contexto_juris}}\n\n"
                "ESTRUCTURA OBLIGATORIA:\n"
                "1) Encabezado (Juez Laboral del Circuito o Juez Constitucional según caso).\n"
                "2) Identificación del trabajador y empleador.\n"
                "3) HECHOS:\n"
                "   - Fecha de inicio y terminación del vínculo\n"
                "   - Salario y modalidad de contrato (TI, TF, OPS encubierto)\n"
                "   - Causal del despido o conflicto\n"
                "   - Estado actual (sin trabajo, sin liquidación, sin aportes)\n"
                "4) DERECHOS VULNERADOS:\n"
                "   - Estabilidad laboral reforzada si hay fuero\n"
                "   - Mínimo vital y seguridad social\n"
                "   - Igualdad y dignidad si hay acoso\n"
                "5) FUNDAMENTO JURÍDICO:\n"
                "   - CST: arts. 64 (indemnización), 65 (mora), 127 (salarios)\n"
                "   - Ley 361/97 art. 26 (fuero salud)\n"
                "   - Ley 1010/2006 (acoso laboral)\n"
                "   - SU-070/2013, SU-049/2017, sentencias del contexto\n"
                "6) PRETENSIONES con CIFRAS aproximadas (salarios, indemnización, prestaciones).\n"
                "7) MEDIDA PROVISIONAL si hay fuero (reintegro inmediato + cotización a seguridad social).\n"
                "8) PRUEBAS: contrato, comprobantes de nómina, carta de despido, certificación médica.\n\n"
                "Tono: reivindicativo, técnico, con cifras. NO inventes salarios ni fechas. "
                "Si falta dato, deja [COMPLETAR …]."
            ),
            "pretensiones_template": [
                "Declarar la ineficacia del despido por violación al fuero [maternidad/salud/sindical].",
                "Ordenar el reintegro al cargo desempeñado o uno de igual o superior categoría.",
                "Pagar los salarios y prestaciones dejados de percibir desde el despido hasta el reintegro.",
                "Pagar indemnización del art. 64 CST y sanción moratoria del art. 65 CST si hubo mora.",
                "Reconocer y pagar las cotizaciones a salud, pensión y ARL durante el periodo del despido.",
                "Reconocer indemnización adicional de 180 días en casos de fuero de salud (Ley 361/97).",
            ],
            "pruebas_sugeridas": (
                "• Contrato laboral o constancia de la relación (recibos, correos, OPS sucesivos).\n"
                "• Comprobantes de pago de los últimos 6 meses.\n"
                "• Carta de despido o renuncia (si la hubo).\n"
                "• Certificación médica si hay fuero de salud o maternidad.\n"
                "• Constancia de afiliación a EPS y AFP (RUAF).\n"
                "• Si hay acoso laboral: testimonios, comunicaciones, memorandos.\n"
                "• Liquidación recibida (si la pagaron) para detectar diferencias."
            ),
            "medida_provisional_arg": (
                "El trabajador y su núcleo familiar dependen del salario para subsistencia. La pérdida del empleo "
                "y la desafiliación a seguridad social vulneran el mínimo vital, la salud y la seguridad social. "
                "En casos con fuero, la jurisprudencia exige reintegro inmediato vía medida provisional para "
                "evitar perjuicio irremediable (SU-070/2013, SU-049/2017)."
            ),
            "stats_custom": [
                {"num": "60 días", "label": "indemnización fuero materno"},
                {"num": "180 días", "label": "indemnización fuero salud"},
                {"num": "+310", "label": "casos laborales asistidos"},
                {"num": "$0", "label": "sin cobro hasta cobrar"},
            ],
            "trust_block": [
                {"title": "Fueros, nuestro fuerte",
                 "desc": "Maternidad, salud, sindical, prepensión: sabemos qué pruebas pedir y qué jurisprudencia aplicar."},
                {"title": "Cifras claras",
                 "desc": "Te decimos cuánto te corresponde por liquidación, indemnización y mora antes de radicar."},
                {"title": "Cuota litis",
                 "desc": "Cobramos solo un porcentaje de lo recuperado. Si no cobras, no pagas honorarios."},
            ],
            "footer_extra": "CST · Ley 361/97 · Ley 1010/2006 (acoso laboral) · SU-070/2013 · SU-049/2017.",
        },
    ]
