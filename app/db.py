"""
SQLite — Leads y Abogados (Galeano Herrera).
WAL para concurrencia, sin ORM (mantenerlo simple).
"""

from __future__ import annotations

import json
import os
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
            areas TEXT NOT NULL DEFAULT '[]',   -- JSON array
            active INTEGER NOT NULL DEFAULT 1,
            is_default INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
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


# ── Bootstrap ─────────────────────────────────────────────────────────────────

def bootstrap_default_lawyer() -> None:
    """Si no hay abogados y hay env LAWYER_WHATSAPP, crea uno default."""
    init_db()
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
