"""
WhatsApp providers — abstracción para intercambiar UltraMsg ↔ Evolution API.

Modos (env var WA_PROVIDER):
  - "ultramsg" (default): solo UltraMsg
  - "evolution":          solo Evolution API self-hosted
  - "hybrid":             intenta Evolution; si falla, cae a UltraMsg

Variables de entorno:
  ULTRAMSG_INSTANCE_ID      ej: instance154562
  ULTRAMSG_TOKEN            token de la instancia

  EVOLUTION_API_URL         ej: https://wa.tudespacho.com  (sin slash final)
  EVOLUTION_API_KEY         API key global de Evolution
  EVOLUTION_INSTANCE        nombre de la instancia (ej: "galeano1")

Uso:
  from app.wa_provider import get_provider
  res = get_provider().send_text("573001234567", "Hola")
"""

from __future__ import annotations

import os
from typing import Protocol

import httpx

# ── Config ────────────────────────────────────────────────────────────────────

WA_PROVIDER = os.environ.get("WA_PROVIDER", "ultramsg").strip().lower()

ULTRAMSG_INSTANCE = os.environ.get("ULTRAMSG_INSTANCE_ID", "").strip()
ULTRAMSG_TOKEN    = os.environ.get("ULTRAMSG_TOKEN", "").strip()

EVOLUTION_API_URL = os.environ.get("EVOLUTION_API_URL", "").strip().rstrip("/")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "").strip()
EVOLUTION_INSTANCE = os.environ.get("EVOLUTION_INSTANCE", "").strip()

TIMEOUT_S = 15


# ── Interfaz común ────────────────────────────────────────────────────────────

class Provider(Protocol):
    name: str
    def is_configured(self) -> bool: ...
    def send_text(self, to_phone: str, body: str) -> dict: ...


# ── UltraMsg ──────────────────────────────────────────────────────────────────

class UltraMsgProvider:
    name = "ultramsg"

    def is_configured(self) -> bool:
        return bool(ULTRAMSG_INSTANCE and ULTRAMSG_TOKEN)

    def send_text(self, to_phone: str, body: str) -> dict:
        if not self.is_configured():
            return {"sent": False, "provider": self.name, "error": "UltraMsg no configurado"}
        url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
        try:
            r = httpx.post(url, data={
                "token": ULTRAMSG_TOKEN, "to": to_phone, "body": body, "priority": "10",
            }, timeout=TIMEOUT_S)
            r.raise_for_status()
            data = r.json() if r.headers.get("content-type","").startswith("application/json") else {"raw": r.text}
            return {"sent": True, "provider": self.name, **data}
        except httpx.HTTPError as e:
            return {"sent": False, "provider": self.name, "error": str(e)}


# ── Evolution API (self-hosted) ───────────────────────────────────────────────

class EvolutionAPIProvider:
    """
    Cliente HTTP para Evolution API (https://github.com/EvolutionAPI/evolution-api).
    Endpoints estándar:
      POST {URL}/message/sendText/{INSTANCE}
        headers: {"apikey": KEY, "Content-Type":"application/json"}
        body: {"number":"573001234567", "textMessage":{"text":"..."}}  (v1.x)
        body: {"number":"573001234567", "text":"..."}                  (v2.x)
    Detectamos versión por respuesta y caemos al formato correcto.
    """
    name = "evolution"

    def is_configured(self) -> bool:
        return bool(EVOLUTION_API_URL and EVOLUTION_API_KEY and EVOLUTION_INSTANCE)

    def send_text(self, to_phone: str, body: str) -> dict:
        if not self.is_configured():
            return {"sent": False, "provider": self.name, "error": "Evolution API no configurado"}
        url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"
        headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
        # Probamos v2.x primero (formato más nuevo)
        for payload in (
            {"number": to_phone, "text": body},
            {"number": to_phone, "textMessage": {"text": body}},  # v1.x fallback
        ):
            try:
                r = httpx.post(url, json=payload, headers=headers, timeout=TIMEOUT_S)
                if r.status_code in (200, 201):
                    try: data = r.json()
                    except Exception: data = {"raw": r.text}
                    return {"sent": True, "provider": self.name, **data}
                if r.status_code == 400:
                    # formato incorrecto, probar siguiente
                    continue
                return {"sent": False, "provider": self.name,
                        "error": f"HTTP {r.status_code}: {r.text[:200]}"}
            except httpx.HTTPError as e:
                return {"sent": False, "provider": self.name, "error": str(e)}
        return {"sent": False, "provider": self.name, "error": "Ningún formato de payload funcionó"}


# ── Hybrid (Evolution con fallback a UltraMsg) ───────────────────────────────

class HybridProvider:
    name = "hybrid"

    def __init__(self):
        self.primary = EvolutionAPIProvider()
        self.fallback = UltraMsgProvider()

    def is_configured(self) -> bool:
        return self.primary.is_configured() or self.fallback.is_configured()

    def send_text(self, to_phone: str, body: str) -> dict:
        if self.primary.is_configured():
            res = self.primary.send_text(to_phone, body)
            if res.get("sent"):
                return res
            # falló: log y fallback
            res_fb = self.fallback.send_text(to_phone, body)
            res_fb["fallback_from"] = "evolution"
            res_fb["primary_error"] = res.get("error")
            return res_fb
        # primary no configurado → directo a fallback
        return self.fallback.send_text(to_phone, body)


# ── Selector ──────────────────────────────────────────────────────────────────

_provider_cache: Provider | None = None


def get_provider() -> Provider:
    global _provider_cache
    if _provider_cache is not None:
        return _provider_cache
    p = WA_PROVIDER
    if p == "evolution":   _provider_cache = EvolutionAPIProvider()
    elif p == "hybrid":    _provider_cache = HybridProvider()
    else:                  _provider_cache = UltraMsgProvider()
    return _provider_cache


def reset_provider() -> None:
    """Útil en tests o cuando cambian las env vars."""
    global _provider_cache
    _provider_cache = None


def status() -> dict:
    """Retorna el estado de todos los providers (para diagnóstico admin)."""
    u = UltraMsgProvider()
    e = EvolutionAPIProvider()
    return {
        "current_mode": WA_PROVIDER,
        "ultramsg":  {"configured": u.is_configured(), "instance": ULTRAMSG_INSTANCE or None},
        "evolution": {"configured": e.is_configured(),
                       "url": EVOLUTION_API_URL or None,
                       "instance": EVOLUTION_INSTANCE or None},
    }
