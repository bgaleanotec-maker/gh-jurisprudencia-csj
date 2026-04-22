"""
Google Calendar + Meet — Galeano Herrera.

Lee credenciales OAuth de la env GOOGLE_CALENDAR_TOKEN (JSON serializado).
Refresca el access_token automáticamente con el refresh_token.

Sin GOOGLE_CALENDAR_TOKEN → todas las funciones devuelven {"ok": False, "error": "calendar_off"}.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timedelta, timezone
from typing import Optional

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GoogleRequest
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GCAL_LIBS_OK = True
except ImportError:
    GCAL_LIBS_OK = False

CALENDAR_TOKEN_RAW = os.environ.get("GOOGLE_CALENDAR_TOKEN", "").strip()
CALENDAR_ID        = os.environ.get("GOOGLE_CALENDAR_ID", "primary").strip() or "primary"
MEET_SUPPRESS      = os.environ.get("MEET_SUPPRESS_CREATE", "false").strip().lower() == "true"
TZ_BOGOTA          = timezone(timedelta(hours=-5))   # America/Bogota (sin DST)

_lock = threading.Lock()
_creds: Optional["Credentials"] = None
_service = None


def _load_creds() -> Optional["Credentials"]:
    global _creds
    if not (GCAL_LIBS_OK and CALENDAR_TOKEN_RAW):
        return None
    if _creds is not None:
        return _creds
    try:
        info = json.loads(CALENDAR_TOKEN_RAW)
        c = Credentials.from_authorized_user_info(info, scopes=info.get("scopes"))
        _creds = c
        return c
    except Exception as e:
        print(f"[calendar] error cargando credenciales: {e}")
        return None


def _service_obj():
    global _service
    with _lock:
        creds = _load_creds()
        if creds is None:
            return None
        if not creds.valid:
            try:
                if creds.expired and creds.refresh_token:
                    creds.refresh(GoogleRequest())
                else:
                    return None
            except Exception as e:
                print(f"[calendar] refresh fallido: {e}")
                return None
        if _service is None:
            _service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        return _service


def is_enabled() -> bool:
    return _service_obj() is not None


# ── Slots disponibles ─────────────────────────────────────────────────────────

DEFAULT_DURACION_MIN = 30
DEFAULT_HORARIO = [(9, 12), (14, 17)]   # bloques de oficina
DEFAULT_DIAS = [0, 1, 2, 3, 4]           # lun-vie


def slots_disponibles(dias_adelante: int = 5,
                      duracion_min: int = DEFAULT_DURACION_MIN,
                      horarios=DEFAULT_HORARIO,
                      dias_semana=DEFAULT_DIAS,
                      lawyer_email: Optional[str] = None) -> list[dict]:
    """
    Genera slots libres en el calendario para los próximos `dias_adelante` días.
    Si `lawyer_email` se da, también consulta su free/busy.
    """
    svc = _service_obj()
    if svc is None:
        return []

    ahora = datetime.now(TZ_BOGOTA)
    fin = ahora + timedelta(days=dias_adelante)

    # Free/busy del calendario principal + abogado (si tenemos su email)
    cals = [{"id": CALENDAR_ID}]
    if lawyer_email:
        cals.append({"id": lawyer_email})
    try:
        fb = svc.freebusy().query(body={
            "timeMin": ahora.isoformat(),
            "timeMax": fin.isoformat(),
            "items": cals,
        }).execute()
    except HttpError as e:
        print(f"[calendar] freebusy fallo: {e}")
        return []

    busy_periods = []
    for cal_id, info in fb.get("calendars", {}).items():
        for b in info.get("busy", []):
            busy_periods.append((datetime.fromisoformat(b["start"]), datetime.fromisoformat(b["end"])))

    def colisiona(start, end):
        for bs, be in busy_periods:
            if start < be and bs < end:
                return True
        return False

    slots = []
    cur = ahora.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    for offset_d in range(dias_adelante + 1):
        dia = (cur + timedelta(days=offset_d)).date()
        if dia.weekday() not in dias_semana:
            continue
        for hi, hf in horarios:
            for h in range(hi, hf):
                for m in (0, 30):
                    s = datetime(dia.year, dia.month, dia.day, h, m, tzinfo=TZ_BOGOTA)
                    e = s + timedelta(minutes=duracion_min)
                    if s <= ahora + timedelta(hours=1):  # mínimo 1h de anticipación
                        continue
                    if e.hour > hf or (e.hour == hf and e.minute > 0):
                        continue
                    if colisiona(s, e):
                        continue
                    slots.append({
                        "start": s.isoformat(),
                        "end": e.isoformat(),
                        "label": s.strftime("%a %d %b · %H:%M"),
                    })
                    if len(slots) >= 30:
                        return slots
    return slots


# ── Crear evento + Meet ───────────────────────────────────────────────────────

def crear_cita(start_iso: str, duracion_min: int,
               lead: dict, lawyer: dict,
               ciudad: str = "Bogotá",
               descripcion_caso: str = "") -> dict:
    """
    Crea evento en el calendario con Meet auto-generado, invitados al cliente y al abogado.
    Retorna {ok, event_id, html_link, meet_url, start, end} o {ok:False, error}.
    """
    svc = _service_obj()
    if svc is None:
        return {"ok": False, "error": "calendar_off"}

    start_dt = datetime.fromisoformat(start_iso)
    end_dt = start_dt + timedelta(minutes=duracion_min)

    body = {
        "summary": f"Cita Galeano Herrera — {lead.get('name','Cliente')} · {lead.get('area') or 'consulta'}",
        "description": (
            f"Cita de evaluación legal gratuita.\n\n"
            f"Cliente: {lead.get('name','—')}\n"
            f"Cédula: {lead.get('cedula','—')}\n"
            f"Tel: +{lead.get('phone','—')}\n"
            f"Email: {lead.get('email','—')}\n\n"
            f"Abogado: {lawyer.get('name','—')}\n"
            f"WhatsApp: +{lawyer.get('whatsapp','—')}\n\n"
            f"--- Caso ---\n{(descripcion_caso or lead.get('descripcion',''))[:1500]}\n\n"
            f"Galeano Herrera | Abogados"
        ),
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/Bogota"},
        "end":   {"dateTime": end_dt.isoformat(),   "timeZone": "America/Bogota"},
        "attendees": [],
        "reminders": {"useDefault": False, "overrides": [
            {"method": "email", "minutes": 24*60},
            {"method": "popup", "minutes": 60},
            {"method": "popup", "minutes": 10},
        ]},
    }
    if lead.get("email"):
        body["attendees"].append({"email": lead["email"], "displayName": lead.get("name","Cliente"),
                                  "responseStatus": "needsAction"})
    if lawyer.get("email"):
        body["attendees"].append({"email": lawyer["email"], "displayName": lawyer.get("name","Abogado"),
                                  "responseStatus": "accepted"})

    if not MEET_SUPPRESS:
        body["conferenceData"] = {
            "createRequest": {
                "requestId": f"gh-{int(start_dt.timestamp())}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    try:
        ev = svc.events().insert(
            calendarId=CALENDAR_ID, body=body,
            conferenceDataVersion=1 if not MEET_SUPPRESS else 0,
            sendUpdates="all",
        ).execute()
    except HttpError as e:
        return {"ok": False, "error": f"calendar_api: {e}"}

    meet_url = ""
    for ep in (ev.get("conferenceData", {}).get("entryPoints", []) or []):
        if ep.get("entryPointType") == "video":
            meet_url = ep.get("uri", ""); break
    if not meet_url:
        meet_url = ev.get("hangoutLink", "")

    return {
        "ok": True,
        "event_id": ev.get("id"),
        "html_link": ev.get("htmlLink"),
        "meet_url": meet_url,
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
    }


# ── Cancelar / reprogramar ────────────────────────────────────────────────────

def puede_cancelar(start_iso: str, margen_min: int = 60) -> bool:
    """True si todavía faltan al menos `margen_min` minutos para la cita."""
    s = datetime.fromisoformat(start_iso)
    ahora = datetime.now(TZ_BOGOTA)
    return (s - ahora).total_seconds() / 60 >= margen_min


def cancelar_cita(event_id: str) -> dict:
    svc = _service_obj()
    if svc is None:
        return {"ok": False, "error": "calendar_off"}
    try:
        svc.events().delete(calendarId=CALENDAR_ID, eventId=event_id, sendUpdates="all").execute()
        return {"ok": True}
    except HttpError as e:
        return {"ok": False, "error": str(e)}


def reprogramar_cita(event_id: str, nuevo_start_iso: str, duracion_min: int) -> dict:
    svc = _service_obj()
    if svc is None:
        return {"ok": False, "error": "calendar_off"}
    try:
        ev = svc.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        s = datetime.fromisoformat(nuevo_start_iso)
        e = s + timedelta(minutes=duracion_min)
        ev["start"] = {"dateTime": s.isoformat(), "timeZone": "America/Bogota"}
        ev["end"]   = {"dateTime": e.isoformat(), "timeZone": "America/Bogota"}
        ev2 = svc.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=ev,
                                   sendUpdates="all").execute()
        return {"ok": True, "event_id": ev2.get("id"), "html_link": ev2.get("htmlLink")}
    except HttpError as e:
        return {"ok": False, "error": str(e)}
