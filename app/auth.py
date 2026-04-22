"""
Sesiones firmadas para abogados (sin servidor de sesiones).
Usa itsdangerous con SECRET_KEY de env.
"""

from __future__ import annotations

import os
from typing import Optional

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Cookie, HTTPException, Request

SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key_change_in_production")
SESSION_COOKIE = "gh_session"
SESSION_MAX_AGE = 60 * 60 * 12   # 12 horas

_signer = URLSafeTimedSerializer(SECRET_KEY, salt="gh-lawyer-session")


def make_session(lawyer_id: int, email: str) -> str:
    return _signer.dumps({"lid": lawyer_id, "email": email})


def parse_session(token: str) -> Optional[dict]:
    if not token:
        return None
    try:
        data = _signer.loads(token, max_age=SESSION_MAX_AGE)
        return data if isinstance(data, dict) and "lid" in data else None
    except (BadSignature, SignatureExpired):
        return None


def require_lawyer(request: Request, gh_session: Optional[str] = Cookie(default=None)) -> dict:
    """Dependency FastAPI: extrae el abogado logueado o 401."""
    data = parse_session(gh_session or "")
    if not data:
        raise HTTPException(401, "No autenticado", headers={"Location": "/pro/login"})
    # Hidratar desde DB para datos frescos
    from app import db as db_mod
    lw = db_mod.get_lawyer(int(data["lid"]))
    if not lw or not lw.get("active"):
        raise HTTPException(401, "Sesión inválida", headers={"Location": "/pro/login"})
    return lw
