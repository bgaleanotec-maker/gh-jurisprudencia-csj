"""
WhatsApp via UltraMsg + manejador de OTP en memoria (TTL 5 min).

Env vars necesarias:
  ULTRAMSG_INSTANCE_ID  → instance154562
  ULTRAMSG_TOKEN        → token de la API
  DEV_MODE              → si "1", el OTP también se devuelve en la response (para testing)
"""

from __future__ import annotations

import os
import random
import time
import threading
from typing import Optional

import httpx

ULTRAMSG_INSTANCE = os.environ.get("ULTRAMSG_INSTANCE_ID", "").strip()
ULTRAMSG_TOKEN    = os.environ.get("ULTRAMSG_TOKEN", "").strip()
DEV_MODE          = os.environ.get("DEV_MODE", "").strip() == "1"

API_BASE = "https://api.ultramsg.com"

_otp_store: dict[str, tuple[str, float]] = {}  # phone → (otp, expires_at)
_lock = threading.Lock()


def normalizar_telefono(raw: str) -> str:
    """+57 300 123 45 67 → 573001234567"""
    if not raw:
        return ""
    s = "".join(ch for ch in raw if ch.isdigit())
    if s.startswith("57") and len(s) == 12:
        return s
    if len(s) == 10 and s.startswith("3"):  # celular Colombia sin prefijo
        return "57" + s
    if s.startswith("0057"):
        return s[2:]
    return s


def es_celular_colombia(phone_norm: str) -> bool:
    return len(phone_norm) == 12 and phone_norm.startswith("573")


# ── Envío bruto ───────────────────────────────────────────────────────────────

def send_text(to_phone_norm: str, body: str) -> dict:
    """Envía mensaje. Usa el provider configurado en WA_PROVIDER
    (ultramsg | evolution | hybrid). Mantiene compatibilidad con código existente."""
    from app import wa_provider
    return wa_provider.get_provider().send_text(to_phone_norm, body)


# ── OTP ───────────────────────────────────────────────────────────────────────

def generar_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


def crear_y_enviar_otp(phone_norm: str) -> dict:
    if not es_celular_colombia(phone_norm):
        return {"ok": False, "error": "Número de celular Colombia inválido (debe ser 57 + 10 dígitos)"}
    otp = generar_otp()
    with _lock:
        _otp_store[phone_norm] = (otp, time.time() + 300)
    body = (
        "🔐 *Galeano Herrera | Abogados*\n\n"
        f"Tu código de verificación es: *{otp}*\n\n"
        "Vence en 5 minutos. No lo compartas con nadie.\n\n"
        "Si no solicitaste este código, ignora este mensaje."
    )
    res = send_text(phone_norm, body)
    out = {"ok": res.get("sent", False), "wa_response": res}
    if DEV_MODE:
        out["otp_debug"] = otp     # NO usar en producción
    return out


def verificar_otp(phone_norm: str, codigo: str) -> bool:
    with _lock:
        item = _otp_store.get(phone_norm)
        if not item:
            return False
        otp, expires = item
        if time.time() > expires:
            _otp_store.pop(phone_norm, None)
            return False
        if otp != (codigo or "").strip():
            return False
        _otp_store.pop(phone_norm, None)   # one-shot
        return True


def limpiar_otps_vencidos() -> None:
    now = time.time()
    with _lock:
        for k in [k for k, v in _otp_store.items() if v[1] < now]:
            _otp_store.pop(k, None)


# ── Notificaciones a abogado ──────────────────────────────────────────────────

def notificar_lead_a_abogado(lawyer_phone: str, lead: dict, download_url: str) -> dict:
    """Mensaje formateado al WhatsApp del abogado con todos los datos del lead."""
    desc = (lead.get("descripcion") or "").strip()
    if len(desc) > 400:
        desc = desc[:400] + "…"
    body = (
        "🔔 *NUEVO LEAD VERIFICADO*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *{lead.get('name','—')}*\n"
        f"📄 CC: {lead.get('cedula','—')}\n"
        f"📱 Tel: +{lead.get('phone','—')}\n"
        f"✉️  Email: {lead.get('email','—')}\n"
        f"⚖️  Área: {lead.get('area') or 'sin clasificar'}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"*Caso del cliente:*\n{desc}\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📥 Borrador: {download_url}\n"
        f"💬 Contactar: https://wa.me/{lead.get('phone','')}\n\n"
        "_Galeano Herrera | Abogados — Sistema de captación_"
    )
    return send_text(lawyer_phone, body)
