"""
wa_mode.py — Decisor de modo de atención (IA / humano / híbrido).

Responsabilidad única: dado el estado de la conversación, la hora actual y la
configuración del despacho, decidir si la IA contesta, si solo humano o si
escalamos.

Reglas (en orden de precedencia):

1. wa_config['ai_disabled'] == '1'      → 'humano' (circuito de emergencia)
2. conversation.modo == 'ia'            → 'ia'    (override por conversación)
3. conversation.modo == 'humano'        → 'humano' (override por conversación)
4. fuera de horario laboral             → wa_config['mode_outside_hours']
5. modo global == 'hibrido':
     - si estado in {cliente, cliente_activo, ganado}  → 'humano'
     - si no                                            → 'ia'
6. modo global == 'ia'                  → 'ia'
7. modo global == 'humano'              → 'humano'
"""

from __future__ import annotations

from datetime import datetime, time as dtime
from typing import Optional
from zoneinfo import ZoneInfo

try:
    from app import db as db_mod
except ImportError:
    import db as db_mod  # type: ignore

TZ_BOGOTA = ZoneInfo("America/Bogota")

# Estados donde el HÍBRIDO entrega al humano
ESTADOS_HUMANO_EN_HIBRIDO = {"cliente", "cliente_activo", "ganado"}


def _parse_hhmm(s: str, fallback: dtime) -> dtime:
    try:
        h, m = s.split(":")
        return dtime(int(h), int(m))
    except Exception:
        return fallback


def _is_office_hours(now_bog: Optional[datetime] = None, cfg: Optional[dict] = None) -> bool:
    """¿Estamos dentro del horario laboral configurado en wa_config?"""
    if cfg is None:
        cfg = db_mod.wa_config_get_all()
    if now_bog is None:
        now_bog = datetime.now(TZ_BOGOTA)

    start = _parse_hhmm(cfg.get("office_hours_start", "08:00"), dtime(8, 0))
    end = _parse_hhmm(cfg.get("office_hours_end", "18:00"), dtime(18, 0))
    days_str = cfg.get("office_days", "1,2,3,4,5")
    try:
        days = {int(x.strip()) for x in days_str.split(",") if x.strip()}
    except Exception:
        days = {1, 2, 3, 4, 5}

    # isoweekday: lunes=1..domingo=7
    if now_bog.isoweekday() not in days:
        return False
    return start <= now_bog.time() <= end


def decidir_modo(
    conversation: dict,
    now_bog: Optional[datetime] = None,
    cfg: Optional[dict] = None,
) -> str:
    """
    Devuelve 'ia' o 'humano' (nunca 'hibrido' — eso se resuelve aquí).

    Args:
        conversation: dict con keys 'modo', 'estado'
        now_bog: datetime opcional para testing
        cfg: dict de wa_config opcional para testing
    """
    if cfg is None:
        cfg = db_mod.wa_config_get_all()

    # 1) Circuito de emergencia
    if cfg.get("ai_disabled", "0") == "1":
        return "humano"

    # 2-3) Override por conversación
    modo_conv = (conversation.get("modo") or "auto").lower()
    if modo_conv == "ia":
        return "ia"
    if modo_conv == "humano":
        return "humano"

    # 4) Fuera de horario
    if not _is_office_hours(now_bog, cfg):
        out = (cfg.get("mode_outside_hours", "ia") or "ia").lower()
        return "humano" if out == "humano" else "ia"

    # 5-7) Modo global
    modo_global = (cfg.get("mode_global", "hibrido") or "hibrido").lower()
    if modo_global == "humano":
        return "humano"
    if modo_global == "ia":
        return "ia"

    # hibrido
    estado = (conversation.get("estado") or "lead_nuevo").lower()
    if estado in ESTADOS_HUMANO_EN_HIBRIDO:
        return "humano"
    return "ia"


def explicar_decision(
    conversation: dict,
    now_bog: Optional[datetime] = None,
    cfg: Optional[dict] = None,
) -> dict:
    """Devuelve el modo + la regla que disparó (útil para audit en admin)."""
    if cfg is None:
        cfg = db_mod.wa_config_get_all()
    if now_bog is None:
        now_bog = datetime.now(TZ_BOGOTA)

    if cfg.get("ai_disabled", "0") == "1":
        return {"modo": "humano", "regla": "ai_disabled=1"}

    modo_conv = (conversation.get("modo") or "auto").lower()
    if modo_conv in ("ia", "humano"):
        return {"modo": modo_conv, "regla": f"override conversación: modo={modo_conv}"}

    if not _is_office_hours(now_bog, cfg):
        out = (cfg.get("mode_outside_hours", "ia") or "ia").lower()
        return {
            "modo": "humano" if out == "humano" else "ia",
            "regla": f"fuera de horario → mode_outside_hours={out}",
        }

    modo_global = (cfg.get("mode_global", "hibrido") or "hibrido").lower()
    if modo_global in ("ia", "humano"):
        return {"modo": modo_global, "regla": f"mode_global={modo_global}"}

    estado = (conversation.get("estado") or "lead_nuevo").lower()
    if estado in ESTADOS_HUMANO_EN_HIBRIDO:
        return {"modo": "humano", "regla": f"híbrido + estado={estado} → humano"}
    return {"modo": "ia", "regla": f"híbrido + estado={estado} → ia"}
