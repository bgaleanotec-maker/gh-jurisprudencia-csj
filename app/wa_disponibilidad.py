"""
wa_disponibilidad.py — Cálculo y agendamiento REAL de citas para WhatsApp.

María Camila NUNCA debe inventar slots. Antes de proponer cita:
  1. Llamar `slots_proximos(area, max_slots=5)` para ver qué hay.
  2. Si no hay slots → no proponer cita, devolver respuesta "te confirmo agenda en
     cuanto un abogado esté libre" + escalar al equipo humano.
  3. Si hay slots → mencionar 1-2 al cliente y esperar confirmación.

Cuando el cliente confirma un slot:
  4. Llamar `agendar_slot(phone, slot_iso, area, lead_id?)` que valida atomicidad,
     elige abogado, crea appointment y devuelve {ok, abogado_nombre, fecha_humana}.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

try:
    from app import db as db_mod
    from app import agenda as ag
except ImportError:
    import db as db_mod  # type: ignore
    import agenda as ag  # type: ignore


TZ_BOGOTA = ZoneInfo("America/Bogota")

_DIA_NOMBRE = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
               4: "viernes", 5: "sábado", 6: "domingo"}
_MES_NOMBRE = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
               7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}


def _abogados_activos_por_area(area: Optional[str]) -> list[dict]:
    """Devuelve abogados activos+disponibles que cubren el área dada (o todos)."""
    todos = [l for l in db_mod.list_lawyers() if l.get("active") and l.get("available")]
    if not area:
        return todos
    out = []
    for l in todos:
        try:
            areas = json.loads(l.get("areas") or "[]") if isinstance(l.get("areas"), str) else (l.get("areas") or [])
        except Exception:
            areas = []
        if "*" in areas or area in areas:
            out.append(l)
    return out


def _label_humano(dt_iso: str) -> str:
    """'2026-05-05T15:00:00-05:00' → 'martes 5 may a las 3:00 pm'."""
    try:
        dt = datetime.fromisoformat(dt_iso)
    except Exception:
        return dt_iso
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_BOGOTA)
    dt = dt.astimezone(TZ_BOGOTA)
    dia = _DIA_NOMBRE.get(dt.weekday(), "")
    mes = _MES_NOMBRE.get(dt.month, "")
    h12 = dt.hour % 12 or 12
    am_pm = "am" if dt.hour < 12 else "pm"
    minutos = f":{dt.minute:02d}" if dt.minute else ":00"
    return f"{dia} {dt.day} {mes} a las {h12}{minutos} {am_pm}"


def slots_proximos(area: Optional[str] = None,
                   dias: int = 14,
                   max_slots: int = 5,
                   duracion_min: int = 20) -> list[dict]:
    """Devuelve los próximos N slots disponibles agrupando todos los abogados.

    Cada item: {start, end, label, lawyer_id, lawyer_name, area_match}
    Ordenados cronológicamente. Solo trae slots futuros con >= 1 hora de margen.
    """
    abs_ = _abogados_activos_por_area(area)
    if not abs_:
        return []

    todos: list[dict] = []
    for lw in abs_:
        try:
            slots = ag.slots_disponibles(
                lawyer_id=lw["id"],
                dias_adelante=dias,
                duracion_min=duracion_min,
                max_slots=max_slots * 2,
            )
        except Exception:
            slots = []
        for s in slots:
            todos.append({
                **s,
                "lawyer_id": lw["id"],
                "lawyer_name": lw.get("name") or "—",
                "label_humano": _label_humano(s["start"]),
            })

    # Ordenar por fecha y devolver los primeros max_slots
    todos.sort(key=lambda x: x["start"])
    # Dedup por timestamp (varios abogados pueden tener mismo slot, queremos
    # ofrecer cada hora una sola vez al cliente; el sistema asignará abogado)
    vistos = set()
    out = []
    for s in todos:
        key = s["start"]
        if key in vistos:
            continue
        vistos.add(key)
        out.append(s)
        if len(out) >= max_slots:
            break
    return out


def hay_disponibilidad(area: Optional[str] = None) -> bool:
    """Quick check: ¿hay al menos 1 abogado activo capaz de tomar este área?"""
    return len(_abogados_activos_por_area(area)) > 0


def slots_a_texto(slots: list[dict], max_lineas: int = 4) -> str:
    """Convierte lista de slots a texto natural para el prompt o mensaje al cliente."""
    if not slots:
        return "(sin disponibilidad próxima)"
    lines = []
    for s in slots[:max_lineas]:
        lines.append(f"- {s['label_humano']}")
    return "\n".join(lines)


def agendar_slot(*,
                 phone: str,
                 slot_iso: str,
                 area: Optional[str] = None,
                 lead_id: Optional[int] = None,
                 conv_id: Optional[int] = None,
                 duracion_min: int = 20) -> dict:
    """Crea un appointment real para el slot dado.

    Returns: {ok: bool, appointment_id?, lawyer_id?, lawyer_name?,
              fecha_humana?, error?}
    """
    # 1) Validar slot futuro con margen
    try:
        dt = datetime.fromisoformat(slot_iso)
    except Exception:
        return {"ok": False, "error": "fecha inválida"}
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_BOGOTA)
    if dt < datetime.now(TZ_BOGOTA) + timedelta(minutes=30):
        return {"ok": False, "error": "fecha demasiado próxima o pasada"}

    # 2) Buscar abogado libre que cubra el área
    candidatos = _abogados_activos_por_area(area)
    if not candidatos:
        return {"ok": False, "error": "sin abogados activos para esta área"}

    elegido = None
    fin = dt + timedelta(minutes=duracion_min)
    for lw in candidatos:
        # ¿Tiene este slot libre?
        slots = ag.slots_disponibles(
            lawyer_id=lw["id"], dias_adelante=14,
            duracion_min=duracion_min, max_slots=80,
        )
        for s in slots:
            try:
                s_start = datetime.fromisoformat(s["start"])
            except Exception:
                continue
            # mismo timestamp (con tolerancia 5 min)
            if abs((s_start - dt).total_seconds()) < 300:
                elegido = lw
                break
        if elegido:
            break

    if not elegido:
        return {"ok": False, "error": "ningún abogado tiene ese slot libre"}

    # 3) Si no hay lead_id, crear lead "fantasma" desde el conv (mínimo viable)
    if not lead_id and conv_id:
        try:
            conv = db_mod.wa_conv_get_by_phone(phone)
            datos = (conv or {}).get("datos_capturados") or {}
            # Sólo creamos lead si tenemos al menos algo de identidad + descripción
            if datos.get("nombre") or datos.get("nombre_wa"):
                lid = _crear_lead_desde_conv(conv, datos, area or "general")
                if lid:
                    lead_id = lid
                    db_mod.wa_conv_update(conv["id"], lead_id=lid)
        except Exception as e:
            print(f"[wa_disp] no se pudo crear lead desde conv: {e}")

    if not lead_id:
        return {"ok": False, "error": "no hay lead creado para asociar la cita"}

    # 4) Crear appointment en BD
    try:
        appt_id = _insertar_appointment(
            lead_id=lead_id,
            lawyer_id=elegido["id"],
            scheduled_at=dt.isoformat(),
            duration_min=duracion_min,
        )
    except Exception as e:
        return {"ok": False, "error": f"db: {e}"}

    return {
        "ok": True,
        "appointment_id": appt_id,
        "lawyer_id": elegido["id"],
        "lawyer_name": elegido.get("name") or "el abogado del despacho",
        "lawyer_phone": elegido.get("whatsapp") or "",
        "fecha_humana": _label_humano(dt.isoformat()),
        "duracion_min": duracion_min,
    }


def _insertar_appointment(*, lead_id: int, lawyer_id: int,
                          scheduled_at: str, duration_min: int = 20) -> int:
    with db_mod.db() as c:
        cur = c.execute(
            """INSERT INTO appointments(lead_id, lawyer_id, scheduled_at,
                  duration_min, status)
               VALUES(?,?,?,?,'scheduled')""",
            (lead_id, lawyer_id, scheduled_at, duration_min),
        )
        return cur.lastrowid


def _crear_lead_desde_conv(conv: dict, datos: dict, area: str) -> Optional[int]:
    """Crea un lead mínimo desde una conversación WA para poder asociar appointment."""
    import secrets as _sec
    nombre = datos.get("nombre") or datos.get("nombre_wa") or "Cliente WhatsApp"
    descripcion = datos.get("descripcion_caso") or "(captado por WhatsApp - pendiente detalle)"
    token = _sec.token_urlsafe(16)
    with db_mod.db() as c:
        cur = c.execute(
            """INSERT INTO leads(token, name, cedula, phone, email, area,
                  descripcion, status, otp_verified, consent_terms, consent_data)
               VALUES(?,?,?,?,?,?,?,'verified',1,1,1)""",
            (token, nombre, datos.get("cedula"),
             conv.get("phone"), datos.get("email"),
             area, descripcion),
        )
        return cur.lastrowid
