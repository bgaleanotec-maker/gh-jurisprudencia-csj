#!/usr/bin/env python3
"""
============================================================
APP JURISPRUDENCIA — GALEANO HERRERA | ABOGADOS  (v4)
============================================================
- /                  Landing pública (clientes)
- /admin             Panel admin (Basic Auth)
- /pro/login         Login abogado (email + password)
- /pro               Dashboard del abogado (sesión)
- /api/lead/*        Captura de leads + booking de citas
- /api/admin/*       CRUD admin
- /api/pro/*         RAG completo (autenticado)
- /api/track         Eventos de tracking (público, no auth)
- /api/cron/*        Tareas programadas (Render Cron Job)
============================================================
"""

from __future__ import annotations

import asyncio
import os
import secrets
import sys
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fastapi import FastAPI, HTTPException, Query, Depends, Request, Response, status, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

try:
    from rag_motor import (
        MotorRAG, obtener_api_key, guardar_config,
        FAISS_INDEX, BASE_DIR, INVALID_FLG,
    )
    RAG_OK = True
except Exception as e:
    RAG_OK = False
    print(f"⚠ Motor RAG no disponible: {e}")

from app import db as db_mod
from app import whatsapp as wa
from app import tutela_lite as tl
from app import ui as ui_mod
from app import calendar_svc as cal
from app import auth as auth_mod

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Galeano Herrera | Abogados — Plataforma Legal",
    description="RAG jurisprudencial + captación + agendamiento + multi-abogado.",
    version="4.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Auth ───────────────────────────────────────────────────────────────────────

_admin_security = HTTPBasic(auto_error=True)


def admin_auth(creds: HTTPBasicCredentials = Depends(_admin_security)):
    user = os.environ.get("ADMIN_USER", "admin")
    pwd  = os.environ.get("ADMIN_PASS", "galeanoherrera2025")
    if not (secrets.compare_digest(creds.username, user) and secrets.compare_digest(creds.password, pwd)):
        raise HTTPException(401, "Credenciales inválidas",
                            headers={"WWW-Authenticate": 'Basic realm="admin"'})


# ── Motor singleton ───────────────────────────────────────────────────────────

_motor: Optional["MotorRAG"] = None
_motor_lite: Optional["MotorRAG"] = None


def get_motor() -> "MotorRAG":
    global _motor
    if _motor is None:
        api_key = obtener_api_key()
        if not api_key:
            raise HTTPException(503, "GEMINI_API_KEY no configurada.")
        _motor = MotorRAG(api_key=api_key)
    return _motor


def get_motor_lite() -> "MotorRAG":
    global _motor_lite, _motor
    if _motor is not None and _motor._listo:
        return _motor
    if _motor_lite is None:
        _motor_lite = MotorRAG(solo_busqueda=True)
    elif not _motor_lite._listo and FAISS_INDEX.exists() and not INVALID_FLG.exists():
        _motor_lite = MotorRAG(solo_busqueda=True)
    return _motor_lite


def _auto_index_background() -> None:
    if not RAG_OK:
        return
    try:
        db_mod.bootstrap_default_lawyer()
    except Exception as e:
        print(f"[boot] db init error: {e}")
    api_key = obtener_api_key()
    if not api_key:
        print("[auto-index] sin GEMINI_API_KEY; salto.")
        return
    if FAISS_INDEX.exists() and not INVALID_FLG.exists():
        print("[auto-index] FAISS ya existe; salto.")
        return
    try:
        print("[auto-index] generando índice FAISS al arranque...")
        m = MotorRAG(api_key=api_key)
        n = m.indexar()
        global _motor
        _motor = m
        print(f"[auto-index] listo: {n} fichas, faiss_listo={m._listo}")
    except Exception as e:
        print(f"[auto-index] error: {e}")


def _ip_of(req: Request) -> str:
    fwd = req.headers.get("x-forwarded-for")
    return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "0.0.0.0"


@app.on_event("startup")
async def _startup_event():
    threading.Thread(target=_auto_index_background, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# PÚBLICO — Landing
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    db_mod.track_event("page_view", ip=_ip_of(request),
                       user_agent=request.headers.get("user-agent",""),
                       referer=request.headers.get("referer",""))
    return ui_mod.landing_html()


# ── Tracking público ──────────────────────────────────────────────────────────

class TrackReq(BaseModel):
    type: str = Field(..., max_length=40)
    payload: Optional[dict] = None

@app.post("/api/track")
async def track(req: TrackReq, request: Request):
    db_mod.track_event(req.type, ip=_ip_of(request),
                       user_agent=request.headers.get("user-agent",""),
                       referer=request.headers.get("referer",""),
                       payload=req.payload)
    return {"ok": True}


# ── Lead: preview / register / OTP / download ─────────────────────────────────

class LeadPreviewReq(BaseModel):
    descripcion: str = Field(..., min_length=30, max_length=4000)
    area: Optional[str] = None

class LeadRegisterReq(BaseModel):
    token: str
    name:   str = Field(..., min_length=3, max_length=120)
    cedula: str = Field(..., min_length=4, max_length=15)
    phone:  str = Field(..., min_length=7, max_length=20)
    email:  str = Field(..., min_length=4, max_length=120)
    consent_terms: bool
    consent_data:  bool
    consent_marketing: bool

class LeadOtpReq(BaseModel):
    token: str
    otp:   str = Field(..., min_length=6, max_length=6)

class LeadResendReq(BaseModel):
    token: str


@app.post("/api/lead/preview")
async def lead_preview(req: LeadPreviewReq, request: Request):
    ip = _ip_of(request)
    if not db_mod.check_rate(ip, max_per_hour=5):
        raise HTTPException(429, "Has excedido el límite de simulaciones por hora desde tu conexión. Intenta más tarde.")

    db_mod.track_event("preview_started", ip=ip,
                       user_agent=request.headers.get("user-agent",""),
                       payload={"area": req.area, "len": len(req.descripcion)})

    motor = get_motor()
    res = tl.generar_borrador(motor, req.descripcion, area=req.area)
    if "error" in res:
        msg = res.get("user_message") or res["error"]
        code = 503 if res["error"] == "rate_limited" else 400
        raise HTTPException(code, msg)

    token = uuid.uuid4().hex
    db_mod.create_lead(
        token=token, descripcion=req.descripcion,
        area=res.get("area_detectada") or req.area,
        draft=res["draft"], fichas=res["fichas"], ip=ip,
        user_agent=request.headers.get("user-agent","")[:300],
    )
    db_mod.track_event("preview_done", ip=ip,
                       payload={"area": res.get("area_detectada"), "fichas": [f["id"] for f in res["fichas"]]})
    preview = tl.construir_preview(res["draft"], palabras_visibles=180)
    return {
        "token": token, "preview": preview, "fichas": res["fichas"],
        "area_detectada": res.get("area_detectada"),
        "tokens_aprox": res.get("tokens_aprox"), "cached": res.get("cached", False),
    }


@app.post("/api/lead/register")
async def lead_register(req: LeadRegisterReq, request: Request):
    if not (req.consent_terms and req.consent_data and req.consent_marketing):
        raise HTTPException(400, "Debes aceptar las 3 autorizaciones.")
    phone_norm = wa.normalizar_telefono(req.phone)
    if not wa.es_celular_colombia(phone_norm):
        raise HTTPException(400, "Número de celular Colombia inválido (formato: 3001234567).")
    if "@" not in req.email or "." not in req.email:
        raise HTTPException(400, "Email inválido.")

    lead = db_mod.attach_user_to_lead(
        token=req.token, name=req.name.strip(), cedula=req.cedula.strip(),
        phone=phone_norm, email=req.email.strip().lower(),
        consent_terms=req.consent_terms, consent_data=req.consent_data,
        consent_marketing=req.consent_marketing,
    )
    if not lead:
        raise HTTPException(404, "Sesión expirada. Vuelve a generar la simulación.")

    db_mod.track_event("register", ip=_ip_of(request), payload={"area": lead.get("area")})
    otp_res = wa.crear_y_enviar_otp(phone_norm)
    out = {"ok": otp_res["ok"], "phone_normalized": phone_norm,
           "wa_sent": otp_res.get("wa_response", {}).get("sent", False)}
    if "otp_debug" in otp_res:
        out["otp_debug"] = otp_res["otp_debug"]
    if not otp_res["ok"] and "error" in otp_res:
        out["wa_error"] = otp_res["error"]
    return out


@app.post("/api/lead/resend-otp")
async def lead_resend(req: LeadResendReq):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead or lead["status"] != "pending_otp":
        raise HTTPException(400, "No hay registro pendiente.")
    res = wa.crear_y_enviar_otp(lead["phone"])
    return {"ok": res["ok"], **({"otp_debug": res["otp_debug"]} if "otp_debug" in res else {})}


@app.post("/api/lead/verify-otp")
async def lead_verify(req: LeadOtpReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead:
        raise HTTPException(404, "Simulación no encontrada.")
    if lead["status"] not in ("pending_otp", "verified"):
        raise HTTPException(400, "Lead en estado inválido.")

    if lead["status"] == "pending_otp":
        if not wa.verificar_otp(lead["phone"], req.otp):
            raise HTTPException(400, "Código incorrecto o vencido. Reenvía y vuelve a intentar.")
        lawyer = db_mod.lawyer_for_assignment(lead["area"]) or db_mod.lawyer_for_area(lead["area"])
        lead = db_mod.mark_lead_verified(req.token, lawyer["id"] if lawyer else None)

        if lawyer:
            try:
                base = str(request.base_url).rstrip("/")
                download_url = f"{base}/api/lead/download/{req.token}.docx"
                wa.notificar_lead_a_abogado(lawyer["whatsapp"], lead, download_url)
            except Exception as e:
                print(f"[wa-notify] error: {e}")

    db_mod.track_event("otp_verified", ip=_ip_of(request), payload={"area": lead.get("area")})
    return {
        "ok": True,
        "download_url": f"/api/lead/download/{req.token}.docx",
        "calendar_enabled": cal.is_enabled(),
    }


@app.get("/api/lead/download/{token}.docx")
async def lead_download(token: str, request: Request):
    lead = db_mod.get_lead_by_token(token)
    if not lead:
        raise HTTPException(404, "Simulación no encontrada.")
    if lead["status"] not in ("verified", "contacted", "closed"):
        raise HTTPException(403, "Verifica tu OTP primero.")
    db_mod.track_event("downloaded", ip=_ip_of(request))
    nombre = lead.get("name") or "cliente"
    docx_bytes = tl.borrador_a_docx(lead["draft"], nombre)
    safe = "".join(c for c in nombre if c.isalnum() or c in " _-")[:40].replace(" ", "_") or "simulacion"
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="simulacion_tutela_{safe}.docx"'},
    )


# ── Booking de citas (público; requiere lead verificado) ──────────────────────

class SlotsQuery(BaseModel):
    token: str
    days: int = Field(5, ge=1, le=10)


@app.get("/api/lead/slots")
async def lead_slots(token: str, days: int = 5, request: Request = None):
    lead = db_mod.get_lead_by_token(token)
    if not lead or lead["status"] not in ("verified","contacted","closed"):
        raise HTTPException(403, "Verifica tu OTP primero.")
    if not cal.is_enabled():
        return {"ok": False, "calendar_enabled": False, "slots": []}
    lawyer_email = None
    if lead.get("lawyer_id"):
        lw = db_mod.get_lawyer(lead["lawyer_id"])
        lawyer_email = lw and lw.get("email")
    return {"ok": True, "calendar_enabled": True,
            "slots": cal.slots_disponibles(dias_adelante=days, lawyer_email=lawyer_email)}


class BookReq(BaseModel):
    token: str
    start_iso: str
    duration_min: int = 30


@app.post("/api/lead/book")
async def lead_book(req: BookReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead or lead["status"] not in ("verified","contacted","closed"):
        raise HTTPException(403, "Verifica tu OTP primero.")
    if not cal.is_enabled():
        raise HTTPException(503, "Agendamiento no disponible. Te contactaremos por WhatsApp.")

    existing = db_mod.get_appointment_by_lead(lead["id"])
    if existing:
        raise HTTPException(400, "Ya tienes una cita agendada. Cancélala o reprográmala.")

    lawyer = db_mod.get_lawyer(lead["lawyer_id"]) if lead.get("lawyer_id") else db_mod.lawyer_for_assignment(lead.get("area"))
    if not lawyer:
        raise HTTPException(503, "No hay abogados disponibles. Te contactaremos pronto.")

    res = cal.crear_cita(req.start_iso, req.duration_min, lead, lawyer,
                         descripcion_caso=lead.get("descripcion",""))
    if not res.get("ok"):
        raise HTTPException(503, f"Error agendando: {res.get('error')}")

    aid = db_mod.create_appointment(
        lead_id=lead["id"], lawyer_id=lawyer["id"],
        scheduled_at=res["start"], duration_min=req.duration_min,
        calendar_event_id=res["event_id"], meet_url=res.get("meet_url",""),
        html_link=res.get("html_link",""),
    )
    db_mod.track_event("meeting_booked", ip=_ip_of(request),
                       payload={"start": res["start"], "lawyer": lawyer["name"]})

    # Confirmación al cliente por WhatsApp
    try:
        s = datetime.fromisoformat(res["start"])
        body = (
            "✅ *Cita confirmada · Galeano Herrera*\n\n"
            f"📅 {s.strftime('%A %d de %B %Y · %H:%M')} (hora Bogotá)\n"
            f"⏱  Duración: {req.duration_min} min\n"
            f"👨‍⚖️ Abogado: {lawyer['name']}\n\n"
            f"🎥 Únete por Meet: {res.get('meet_url','(enlace en el correo)')}\n\n"
            "Te llegará invitación al correo y recordatorios 24h y 1h antes.\n"
            "Si necesitas cancelar, hazlo al menos 60 minutos antes."
        )
        wa.send_text(lead["phone"], body)
    except Exception as e:
        print(f"[book] confirm wa error: {e}")

    return {"ok": True, "appointment_id": aid, "meet_url": res.get("meet_url"),
            "html_link": res.get("html_link"), "start": res["start"]}


@app.get("/api/lead/appointment")
async def lead_appointment(token: str):
    lead = db_mod.get_lead_by_token(token)
    if not lead: raise HTTPException(404, "no encontrado")
    appt = db_mod.get_appointment_by_lead(lead["id"])
    if not appt: return {"ok": False, "appointment": None}
    return {"ok": True, "appointment": appt, "puede_cancelar": cal.puede_cancelar(appt["scheduled_at"], 60)}


class CancelReq(BaseModel):
    token: str

@app.post("/api/lead/cancel-appointment")
async def lead_cancel_appt(req: CancelReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead: raise HTTPException(404, "no encontrado")
    appt = db_mod.get_appointment_by_lead(lead["id"])
    if not appt: raise HTTPException(404, "sin cita")
    if not cal.puede_cancelar(appt["scheduled_at"], 60):
        raise HTTPException(400, "Quedan menos de 60 minutos para tu cita: ya no se puede cancelar. Si no puedes asistir, escríbenos por WhatsApp para reprogramar.")
    if appt.get("calendar_event_id"):
        cal.cancelar_cita(appt["calendar_event_id"])
    db_mod.update_appointment_status(appt["id"], "cancelled_by_user")
    db_mod.track_event("meeting_cancelled", ip=_ip_of(request))
    return {"ok": True}


class RescheduleReq(BaseModel):
    token: str
    start_iso: str
    duration_min: int = 30

@app.post("/api/lead/reschedule")
async def lead_resched(req: RescheduleReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead: raise HTTPException(404, "no encontrado")
    appt = db_mod.get_appointment_by_lead(lead["id"])
    if not appt: raise HTTPException(404, "sin cita")
    if not cal.puede_cancelar(appt["scheduled_at"], 60):
        raise HTTPException(400, "No puedes reprogramar a menos de 60 min de la cita.")
    res = cal.reprogramar_cita(appt["calendar_event_id"], req.start_iso, req.duration_min)
    if not res.get("ok"):
        raise HTTPException(503, f"Error: {res.get('error')}")
    db_mod.update_appointment_event(appt["id"], appt["calendar_event_id"],
                                    appt.get("meet_url",""), res.get("html_link",""),
                                    scheduled_at=req.start_iso)
    return {"ok": True, "start": req.start_iso}


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
async def admin_panel():
    return ui_mod.admin_html()

@app.get("/api/admin/stats", dependencies=[Depends(admin_auth)])
async def admin_stats():
    s = db_mod.stats()
    s["funnel_7d"] = db_mod.funnel_stats(7)
    s["daily_14d"] = db_mod.daily_counts(14)
    return s

@app.get("/api/admin/leads", dependencies=[Depends(admin_auth)])
async def admin_list_leads(status: Optional[str] = None, limit: int = 200):
    out = db_mod.list_leads(limit=limit, status=status)
    for l in out:
        l["draft"] = (l.get("draft") or "")[:280] + ("…" if l.get("draft") and len(l["draft"])>280 else "")
    return out

@app.get("/api/admin/leads/{lid}", dependencies=[Depends(admin_auth)])
async def admin_get_lead(lid: int):
    leads = db_mod.list_leads(limit=1000)
    for l in leads:
        if l["id"] == lid:
            return l
    raise HTTPException(404, "lead no encontrado")

class AdminPatchLead(BaseModel):
    status: Optional[str] = None
    notes:  Optional[str] = None

@app.patch("/api/admin/leads/{lid}", dependencies=[Depends(admin_auth)])
async def admin_update_lead(lid: int, body: AdminPatchLead):
    if body.status:
        if body.status not in ("preview","pending_otp","verified","contacted","closed"):
            raise HTTPException(400, "status inválido")
        if body.status == "contacted":
            db_mod.mark_lead_contacted(lid, notes=body.notes or "")
        else:
            db_mod.update_lead_status(lid, body.status, notes=body.notes or "")
    return {"ok": True}

@app.get("/api/admin/lawyers", dependencies=[Depends(admin_auth)])
async def admin_list_lawyers():
    return db_mod.list_lawyers()

class LawyerCreate(BaseModel):
    name: str
    whatsapp: str
    email: Optional[str] = None
    password: Optional[str] = None
    areas: list[str] = []
    is_default: bool = False

@app.post("/api/admin/lawyers", dependencies=[Depends(admin_auth)])
async def admin_create_lawyer(body: LawyerCreate):
    wa_norm = wa.normalizar_telefono(body.whatsapp)
    if len(wa_norm) < 10:
        raise HTTPException(400, "WhatsApp inválido (formato 573XXXXXXXXX).")
    lid = db_mod.create_lawyer(name=body.name.strip(), whatsapp=wa_norm,
                                areas=body.areas, is_default=body.is_default)
    if body.email:
        db_mod.set_lawyer_email(lid, body.email)
    if body.password:
        db_mod.set_lawyer_password(lid, body.password)
    return {"ok": True, "id": lid}


class LawyerPatch(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    available: Optional[bool] = None

@app.patch("/api/admin/lawyers/{lid}", dependencies=[Depends(admin_auth)])
async def admin_patch_lawyer(lid: int, body: LawyerPatch):
    if body.email is not None:
        db_mod.set_lawyer_email(lid, body.email)
    if body.password:
        db_mod.set_lawyer_password(lid, body.password)
    if body.available is not None:
        db_mod.set_lawyer_availability(lid, body.available)
    return {"ok": True}

@app.delete("/api/admin/lawyers/{lid}", dependencies=[Depends(admin_auth)])
async def admin_delete_lawyer(lid: int):
    db_mod.delete_lawyer(lid); return {"ok": True}

@app.get("/api/admin/appointments", dependencies=[Depends(admin_auth)])
async def admin_list_appts(status: Optional[str] = None, upcoming: bool = False):
    return db_mod.list_appointments(status=status, upcoming_only=upcoming, limit=500)

@app.get("/api/admin/config", dependencies=[Depends(admin_auth)])
async def admin_config():
    motor = get_motor_lite()
    lawyer = db_mod.lawyer_for_area(None)
    return {
        "gemini_api_key": bool(obtener_api_key()),
        "faiss_listo": motor._listo, "fichas": len(motor.meta),
        "ultramsg": bool(wa.ULTRAMSG_INSTANCE and wa.ULTRAMSG_TOKEN),
        "calendar": cal.is_enabled(),
        "lawyer_default": (lawyer["name"] + " (+" + lawyer["whatsapp"] + ")") if lawyer else None,
        "dev_mode": wa.DEV_MODE,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PRO — Login + Dashboard del abogado
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/pro/login", response_class=HTMLResponse)
async def pro_login_page():
    return ui_mod.lawyer_login_html()


@app.post("/pro/login")
async def pro_login_action(email: str = Form(...), password: str = Form(...)):
    lw = db_mod.authenticate_lawyer(email, password)
    if not lw:
        return RedirectResponse("/pro/login?err=1", status_code=303)
    token = auth_mod.make_session(lw["id"], lw["email"])
    resp = RedirectResponse("/pro", status_code=303)
    resp.set_cookie(auth_mod.SESSION_COOKIE, token, max_age=auth_mod.SESSION_MAX_AGE,
                    httponly=True, samesite="lax")
    return resp


@app.get("/pro/logout")
async def pro_logout():
    resp = RedirectResponse("/pro/login", status_code=303)
    resp.delete_cookie(auth_mod.SESSION_COOKIE)
    return resp


@app.get("/pro", response_class=HTMLResponse)
async def pro_dashboard(request: Request, gh_session: Optional[str] = Cookie(default=None)):
    data = auth_mod.parse_session(gh_session or "")
    if not data:
        return RedirectResponse("/pro/login", status_code=303)
    lw = db_mod.get_lawyer(int(data["lid"]))
    if not lw or not lw.get("active"):
        return RedirectResponse("/pro/login", status_code=303)
    return ui_mod.lawyer_dashboard_html(lw)


# Endpoints del dashboard (para JS del lawyer)

@app.get("/api/pro/me")
async def pro_me(lawyer: dict = Depends(auth_mod.require_lawyer)):
    return {"id": lawyer["id"], "name": lawyer["name"], "email": lawyer.get("email"),
            "whatsapp": lawyer["whatsapp"], "areas": lawyer["areas"],
            "available": bool(lawyer.get("available", 1))}


class PatchMe(BaseModel):
    available: Optional[bool] = None
    password: Optional[str] = None

@app.patch("/api/pro/me")
async def pro_patch_me(body: PatchMe, lawyer: dict = Depends(auth_mod.require_lawyer)):
    if body.available is not None:
        db_mod.set_lawyer_availability(lawyer["id"], body.available)
    if body.password:
        db_mod.set_lawyer_password(lawyer["id"], body.password)
    return {"ok": True}


@app.get("/api/pro/leads")
async def pro_leads(lawyer: dict = Depends(auth_mod.require_lawyer), status: Optional[str] = None):
    leads = db_mod.list_leads(limit=300, status=status)
    # Filtrar a los del abogado o que cubren su área
    areas = set(lawyer.get("areas") or [])
    todos = "*" in areas
    out = []
    for l in leads:
        if l.get("lawyer_id") == lawyer["id"]:
            out.append(l); continue
        if todos or (l.get("area") in areas):
            out.append(l)
    for l in out:
        l["draft"] = (l.get("draft") or "")[:280] + ("…" if l.get("draft") and len(l["draft"])>280 else "")
    return out


@app.get("/api/pro/appointments")
async def pro_appts(lawyer: dict = Depends(auth_mod.require_lawyer), upcoming: bool = True):
    return db_mod.list_appointments(lawyer_id=lawyer["id"], upcoming_only=upcoming, limit=200)


@app.get("/api/pro/leads/{lid}")
async def pro_lead_detail(lid: int, lawyer: dict = Depends(auth_mod.require_lawyer)):
    leads = db_mod.list_leads(limit=2000)
    for l in leads:
        if l["id"] == lid: return l
    raise HTTPException(404, "no encontrado")


# ── Endpoints RAG completo (autenticado por sesión) ──────────────────────────

class ConsultaRequest(BaseModel):
    pregunta: str = Field(..., min_length=3)
    area: Optional[str] = None
    anio: Optional[int] = None
    sala: Optional[str] = None
    top_k: Optional[int] = Field(6, ge=1, le=15)
    rerank: bool = True

class CasoRequest(BaseModel):
    descripcion: str = Field(..., min_length=10)
    nombre_cliente: Optional[str] = ""
    area: Optional[str] = None

class TutelaRequest(BaseModel):
    nombre: str
    cedula: str
    accionado: str
    hechos: str = Field(..., min_length=10)
    derecho_vulnerado: str
    area: Optional[str] = None


@app.post("/api/pro/consultar")
async def pro_consultar(req: ConsultaRequest, lawyer: dict = Depends(auth_mod.require_lawyer)):
    motor = get_motor()
    res = motor.consultar(req.pregunta, filtro_area=req.area, filtro_anio=req.anio,
                          filtro_sala=req.sala, modo="respuesta", rerank=req.rerank,
                          top_k=req.top_k)
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.post("/api/pro/analizar-caso")
async def pro_caso(req: CasoRequest, lawyer: dict = Depends(auth_mod.require_lawyer)):
    motor = get_motor()
    q = req.descripcion if not req.nombre_cliente else f"Cliente: {req.nombre_cliente}. {req.descripcion}"
    res = motor.consultar(q, filtro_area=req.area, modo="caso")
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.post("/api/pro/generar-tutela")
async def pro_tutela(req: TutelaRequest, lawyer: dict = Depends(auth_mod.require_lawyer)):
    motor = get_motor()
    datos = (
        f"Accionante: {req.nombre}, CC {req.cedula}. Accionado: {req.accionado}. "
        f"Derecho vulnerado: {req.derecho_vulnerado}. Hechos: {req.hechos}"
    )
    res = motor.consultar(datos, filtro_area=req.area, modo="tutela")
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.get("/api/pro/linea-jurisprudencial")
async def pro_linea(tema: str = Query(..., min_length=3), area: Optional[str] = None,
                    lawyer: dict = Depends(auth_mod.require_lawyer)):
    motor = get_motor()
    res = motor.consultar(tema, filtro_area=area, modo="linea")
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.get("/api/pro/buscar")
async def pro_buscar(q: str = Query(..., min_length=2), area: Optional[str] = None,
                     anio: Optional[int] = None, sala: Optional[str] = None,
                     top_k: int = Query(10, le=25),
                     lawyer: dict = Depends(auth_mod.require_lawyer)):
    try:
        motor = get_motor()
    except HTTPException:
        motor = get_motor_lite()
    fichas = motor.buscar(q, k=top_k, filtro_area=area, filtro_anio=anio, filtro_sala=sala)
    return {"query": q, "total": len(fichas), "semantico": motor._listo, "lexico": motor.bm25 is not None,
            "resultados": [{"id": f["id"], "sala": f.get("sala"), "anio": f.get("anio"),
                            "areas": f.get("areas", []), "temas": (f.get("temas") or [])[:3],
                            "score": f.get("score", 0),
                            "preview": (f.get("texto_busqueda","") or "")[:240]} for f in fichas]}

@app.get("/api/pro/estadisticas")
async def pro_stats(lawyer: dict = Depends(auth_mod.require_lawyer)):
    return get_motor_lite().estadisticas()


# ─────────────────────────────────────────────────────────────────────────────
# CRON — recordatorios (Render Cron Job o curl manual)
# ─────────────────────────────────────────────────────────────────────────────

def _cron_token_check(t: str):
    expected = os.environ.get("CRON_TOKEN", os.environ.get("SECRET_KEY",""))
    if not expected or not secrets.compare_digest(t or "", expected):
        raise HTTPException(401, "cron token inválido")


@app.get("/api/cron/reminders")
async def cron_reminders(t: str = ""):
    _cron_token_check(t)
    sent = {"24h": 0, "1h": 0}
    for w in ("24h", "1h"):
        for appt in db_mod.appointments_pending_reminder(w):
            try:
                s = datetime.fromisoformat(appt["scheduled_at"])
                cuerpo = (
                    "🔔 *Recordatorio de cita · Galeano Herrera*\n\n"
                    f"📅 {s.strftime('%A %d de %B %Y · %H:%M')} (Bogotá)\n"
                    f"🎥 Únete por Meet: {appt.get('meet_url','(ver correo)')}\n\n"
                    + ("Tu cita es en aproximadamente *24 horas*.\n"
                       "Si no puedes asistir, cancela ahora desde el sitio."
                       if w == "24h" else
                       "Tu cita empieza en aproximadamente *1 hora*.\n"
                       "Ya no es posible cancelar (ventana de 60 min).")
                )
                wa.send_text(appt["lead_phone"], cuerpo)
                db_mod.mark_appointment_reminded(appt["id"], w)
                sent[w] += 1
            except Exception as e:
                print(f"[cron] reminder {w} error: {e}")
    return {"ok": True, "sent": sent}


# ── Salud ─────────────────────────────────────────────────────────────────────

@app.get("/salud")
async def salud():
    if not RAG_OK:
        return {"status": "rag_off", "timestamp": datetime.now().isoformat()}
    motor = get_motor_lite()
    return {
        "status": "ok", "timestamp": datetime.now().isoformat(),
        "faiss_listo": motor._listo, "bm25_listo": motor.bm25 is not None,
        "fichas": len(motor.meta),
        "api_key": bool(obtener_api_key()),
        "ultramsg": bool(wa.ULTRAMSG_INSTANCE and wa.ULTRAMSG_TOKEN),
        "calendar": cal.is_enabled(),
        "version": app.version,
    }


# ── Entrada directa ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
