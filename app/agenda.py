"""
Agenda nativa — Galeano Herrera.

Genera slots libres para un abogado combinando:
  - Horario de oficina (configurable por abogado, default lun-vie 9-12 y 14-17)
  - Duración del slot (default 30 min)
  - Citas existentes en DB
  - Bloqueos manuales del abogado (lawyer_blocks)
  - Mínimo 1h de anticipación

No depende de Google Calendar ni de APIs externas.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

TZ_BOGOTA = timezone(timedelta(hours=-5))

DEFAULT_DURACION_MIN = 30
DEFAULT_HORARIO = [(9, 12), (14, 17)]    # bloques (inicio, fin) en hora local
DEFAULT_DIAS = [0, 1, 2, 3, 4]            # lunes..viernes
DEFAULT_DIAS_ADELANTE = 7                # slots hasta 7 días adelante


def _parse_dt(s: str) -> datetime:
    """Parsea ISO8601. Si no trae tz, asume Bogotá."""
    if not s:
        return datetime.now(TZ_BOGOTA)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        # SQLite sin tz
        dt = datetime.fromisoformat(s.replace("T", " ").split(".")[0])
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_BOGOTA)
    return dt.astimezone(TZ_BOGOTA)


def slots_disponibles(lawyer_id: Optional[int],
                      dias_adelante: int = DEFAULT_DIAS_ADELANTE,
                      duracion_min: int = DEFAULT_DURACION_MIN,
                      horarios=DEFAULT_HORARIO,
                      dias_semana=DEFAULT_DIAS,
                      max_slots: int = 40) -> list[dict]:
    """
    Devuelve slots libres del abogado dado (o del calendario general si lawyer_id=None).
    """
    from app import db as db_mod

    ahora = datetime.now(TZ_BOGOTA)
    fin = ahora + timedelta(days=dias_adelante)

    # Citas existentes (programadas) del abogado
    with db_mod.db() as c:
        if lawyer_id:
            rows = c.execute(
                """SELECT scheduled_at, duration_min FROM appointments
                   WHERE lawyer_id=? AND status='scheduled'
                     AND scheduled_at BETWEEN ? AND ?""",
                (lawyer_id, ahora.isoformat(), fin.isoformat()),
            ).fetchall()
        else:
            rows = c.execute(
                """SELECT scheduled_at, duration_min FROM appointments
                   WHERE status='scheduled' AND scheduled_at BETWEEN ? AND ?""",
                (ahora.isoformat(), fin.isoformat()),
            ).fetchall()
    busy = []
    for r in rows:
        s = _parse_dt(r["scheduled_at"])
        e = s + timedelta(minutes=int(r["duration_min"] or duracion_min))
        busy.append((s, e))

    # Bloqueos manuales del abogado
    if lawyer_id:
        with db_mod.db() as c:
            rows = c.execute(
                """SELECT start_at, end_at FROM lawyer_blocks
                   WHERE lawyer_id=? AND end_at > ? AND start_at < ?""",
                (lawyer_id, ahora.isoformat(), fin.isoformat()),
            ).fetchall()
        for r in rows:
            busy.append((_parse_dt(r["start_at"]), _parse_dt(r["end_at"])))

    def colisiona(s: datetime, e: datetime) -> bool:
        for bs, be in busy:
            if s < be and bs < e:
                return True
        return False

    slots = []
    start_cur = ahora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    for off in range(dias_adelante + 1):
        dia = (start_cur + timedelta(days=off)).date()
        if dia.weekday() not in dias_semana:
            continue
        for hi, hf in horarios:
            for h in range(hi, hf):
                for m in (0, 30) if duracion_min <= 30 else (0,):
                    s = datetime(dia.year, dia.month, dia.day, h, m, tzinfo=TZ_BOGOTA)
                    e = s + timedelta(minutes=duracion_min)
                    if s <= ahora + timedelta(hours=1):
                        continue
                    if e.hour > hf or (e.hour == hf and e.minute > 0):
                        continue
                    if colisiona(s, e):
                        continue
                    slots.append({
                        "start": s.isoformat(),
                        "end":   e.isoformat(),
                        "label": s.strftime("%a %d %b · %H:%M"),
                    })
                    if len(slots) >= max_slots:
                        return slots
    return slots


def semana_del_abogado(lawyer_id: int, start_date: Optional[str] = None,
                        horarios=DEFAULT_HORARIO,
                        duracion_min: int = DEFAULT_DURACION_MIN) -> dict:
    """
    Devuelve la agenda semanal del abogado: grid de días × slots con estado.
    Estado de cada celda: 'free' / 'booked' / 'blocked' / 'past' / 'off_hours'.
    """
    from app import db as db_mod
    if start_date:
        base = _parse_dt(start_date).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        ahora = datetime.now(TZ_BOGOTA)
        # lunes de esta semana
        base = (ahora - timedelta(days=ahora.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = base + timedelta(days=7)

    with db_mod.db() as c:
        appts = c.execute(
            """SELECT a.id, a.scheduled_at, a.duration_min, a.status,
                      l.name as lead_name, l.phone as lead_phone, l.area as lead_area
               FROM appointments a LEFT JOIN leads l ON l.id = a.lead_id
               WHERE a.lawyer_id=? AND a.scheduled_at BETWEEN ? AND ?""",
            (lawyer_id, base.isoformat(), end.isoformat()),
        ).fetchall()
        blocks = c.execute(
            """SELECT id, start_at, end_at, reason FROM lawyer_blocks
               WHERE lawyer_id=? AND end_at > ? AND start_at < ?""",
            (lawyer_id, base.isoformat(), end.isoformat()),
        ).fetchall()

    appt_items = []
    for a in appts:
        s = _parse_dt(a["scheduled_at"])
        e = s + timedelta(minutes=int(a["duration_min"] or duracion_min))
        appt_items.append({
            "id": a["id"], "type": "appointment",
            "start": s.isoformat(), "end": e.isoformat(),
            "status": a["status"], "title": a["lead_name"] or "Cliente",
            "phone": a["lead_phone"], "area": a["lead_area"],
        })

    block_items = []
    for b in blocks:
        block_items.append({
            "id": b["id"], "type": "block",
            "start": _parse_dt(b["start_at"]).isoformat(),
            "end":   _parse_dt(b["end_at"]).isoformat(),
            "reason": b["reason"] or "",
        })

    # Generar rejilla de slots
    ahora = datetime.now(TZ_BOGOTA)
    dias = []
    for d in range(7):
        dia = base + timedelta(days=d)
        slots_dia = []
        for hi, hf in horarios:
            for h in range(hi, hf):
                for m in (0, 30) if duracion_min <= 30 else (0,):
                    s = datetime(dia.year, dia.month, dia.day, h, m, tzinfo=TZ_BOGOTA)
                    e = s + timedelta(minutes=duracion_min)
                    estado = "free"
                    item = None
                    if dia.weekday() not in DEFAULT_DIAS:
                        estado = "off_hours"
                    elif s < ahora:
                        estado = "past"
                    else:
                        for it in appt_items:
                            ist = _parse_dt(it["start"]); ien = _parse_dt(it["end"])
                            if s < ien and ist < e:
                                estado = "booked" if it["status"] == "scheduled" else it["status"]
                                item = it; break
                        if estado == "free":
                            for bl in block_items:
                                bst = _parse_dt(bl["start"]); ben = _parse_dt(bl["end"])
                                if s < ben and bst < e:
                                    estado = "blocked"; item = bl; break
                    slots_dia.append({
                        "start": s.isoformat(), "end": e.isoformat(),
                        "hour": s.strftime("%H:%M"),
                        "state": estado, "item": item,
                    })
        dias.append({
            "date": dia.strftime("%Y-%m-%d"),
            "label": dia.strftime("%a %d"),
            "weekday": dia.weekday(),
            "slots": slots_dia,
        })

    return {
        "week_start": base.strftime("%Y-%m-%d"),
        "week_end":   (end - timedelta(days=1)).strftime("%Y-%m-%d"),
        "dias":       dias,
        "horarios":   horarios,
        "duracion_min": duracion_min,
    }


def puede_cancelar(scheduled_at: str, margen_min: int = 60) -> bool:
    """True si quedan al menos `margen_min` minutos para la cita."""
    s = _parse_dt(scheduled_at)
    return (s - datetime.now(TZ_BOGOTA)).total_seconds() / 60 >= margen_min
