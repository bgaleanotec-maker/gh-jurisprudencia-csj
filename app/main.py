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

from fastapi import FastAPI, HTTPException, Query, Depends, Request, Response, status, Form, Cookie, UploadFile, File
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
from app import agenda as ag
from app import auth as auth_mod
from app import og_image as og_mod
from app import rag_ingest as rag_in

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
    resp = HTMLResponse(ui_mod.landing_html())
    # permitir embed en Facebook/Instagram (por defecto los browsers ya permiten;
    # algunos hostings añaden X-Frame-Options: DENY). Lo relajamos:
    allow_embed = os.environ.get("ALLOW_IFRAME_EMBED", "").strip().lower() in ("1","true","yes")
    if allow_embed:
        resp.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://*.facebook.com https://*.instagram.com https://www.facebook.com"
        if "X-Frame-Options" in resp.headers:
            del resp.headers["X-Frame-Options"]
    return resp


@app.get("/og.png")
async def og_image():
    png = og_mod.generar_og_png()
    return Response(content=png, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})


@app.get("/favicon.ico")
async def favicon():
    # SVG inline (el <link> en el HTML ya tiene data:image/svg+xml). Este endpoint
    # devuelve también un SVG para crawlers que buscan /favicon.ico directo.
    svg = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           b'<rect width="64" height="64" rx="10" fill="#002347"/>'
           b'<text x="50%" y="54%" font-family="Georgia,serif" font-size="42" '
           b'font-weight="900" text-anchor="middle" fill="#C5A059">G</text></svg>')
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control":"public, max-age=604800"})


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
    # Datos orientadores (opcionales) — si vienen, el borrador los usa literales
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    ciudad: Optional[str] = None
    accionado: Optional[str] = None

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

    db_mod.track_event("preview_started", ip=ip,
                       user_agent=request.headers.get("user-agent",""),
                       payload={"area": req.area, "len": len(req.descripcion)})

    # Datos orientadores (si el usuario los llenó)
    datos_orient = {
        k: (getattr(req, k) or "").strip()
        for k in ("nombre","cedula","ciudad","accionado")
        if getattr(req, k, None)
    } or None

    # 1) Cache primero (no consume rate limit ni cuota Gemini)
    area_auto = req.area or tl.detectar_area(req.descripcion)
    cache_extra = ""
    if datos_orient:
        cache_extra = "|".join(str(datos_orient.get(k,"")).lower() for k in ("nombre","cedula","accionado","ciudad"))
    hit = tl.cache_get(req.descripcion, area_auto, extra=cache_extra)
    motor = get_motor()
    if hit:
        res = dict(hit); res["cached"] = True
    else:
        # 2) Rate limit solo para queries NUEVAS (abuso real)
        if not db_mod.check_rate(ip, max_per_hour=15):
            raise HTTPException(429, "Has excedido el límite de simulaciones por hora desde esta conexión. Intenta en 1 hora o escríbenos por WhatsApp.")
        res = tl.generar_borrador(motor, req.descripcion, area=req.area,
                                  datos_cliente=datos_orient)
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
        "calendar_enabled": True,   # agenda nativa siempre activa
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


# ── Booking con agenda NATIVA (público; requiere lead verificado) ─────────────

@app.get("/api/lead/slots")
async def lead_slots(token: str, days: int = 7):
    lead = db_mod.get_lead_by_token(token)
    if not lead or lead["status"] not in ("verified","contacted","closed"):
        raise HTTPException(403, "Verifica tu OTP primero.")
    # Asegurar asignación de abogado
    lawyer = None
    if lead.get("lawyer_id"):
        lawyer = db_mod.get_lawyer(lead["lawyer_id"])
    if not lawyer:
        lawyer = db_mod.lawyer_for_assignment(lead.get("area")) or db_mod.lawyer_for_area(lead.get("area"))
    if not lawyer:
        return {"ok": False, "reason": "no_lawyer_available", "slots": []}
    slots = ag.slots_disponibles(lawyer_id=lawyer["id"], dias_adelante=days)
    return {"ok": True, "slots": slots,
            "lawyer": {"name": lawyer["name"], "whatsapp": lawyer["whatsapp"]}}


class BookReq(BaseModel):
    token: str
    start_iso: str
    duration_min: int = 30


def _fecha_es(dt: datetime) -> str:
    """Formato legible en español."""
    DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
    return f"{DIAS[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} · {dt.strftime('%H:%M')}"


@app.post("/api/lead/book")
async def lead_book(req: BookReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead or lead["status"] not in ("verified","contacted","closed"):
        raise HTTPException(403, "Verifica tu OTP primero.")

    existing = db_mod.get_appointment_by_lead(lead["id"])
    if existing:
        raise HTTPException(400, "Ya tienes una cita agendada. Cancélala o reprográmala.")

    lawyer = None
    if lead.get("lawyer_id"):
        lawyer = db_mod.get_lawyer(lead["lawyer_id"])
    if not lawyer:
        lawyer = db_mod.lawyer_for_assignment(lead.get("area")) or db_mod.lawyer_for_area(lead.get("area"))
    if not lawyer:
        raise HTTPException(503, "No hay abogados disponibles. Te contactaremos pronto.")

    # Validar que el slot siga libre
    start_dt = ag._parse_dt(req.start_iso)
    libres = ag.slots_disponibles(lawyer_id=lawyer["id"], dias_adelante=10, max_slots=200)
    if not any(abs((ag._parse_dt(s["start"]) - start_dt).total_seconds()) < 60 for s in libres):
        raise HTTPException(409, "Ese horario acaba de ocuparse o quedó fuera de disponibilidad. Refresca y elige otro.")

    # Si aún no estaba asignado, asignamos ahora
    if not lead.get("lawyer_id"):
        with db_mod.db() as c:
            c.execute("UPDATE leads SET lawyer_id=? WHERE id=?", (lawyer["id"], lead["id"]))

    aid = db_mod.create_appointment(
        lead_id=lead["id"], lawyer_id=lawyer["id"],
        scheduled_at=start_dt.isoformat(), duration_min=req.duration_min,
        modality="whatsapp",
    )
    db_mod.track_event("meeting_booked", ip=_ip_of(request),
                       payload={"start": start_dt.isoformat(), "lawyer": lawyer["name"]})

    fecha_legible = _fecha_es(start_dt)
    base = str(request.base_url).rstrip("/")
    dashboard_url = f"{base}/pro"

    # WhatsApp al cliente
    try:
        body_cli = (
            "✅ *Cita confirmada · Galeano Herrera*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📅 *{fecha_legible}* (Bogotá)\n"
            f"⏱  Duración: {req.duration_min} min\n"
            f"👨‍⚖️ Abogado: {lawyer['name']}\n"
            "📱 Modalidad: llamada por WhatsApp\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Tu abogado te llamará a este mismo número a la hora acordada.\n\n"
            "🔔 Te enviaremos recordatorio *24 h* y *1 h* antes.\n"
            "⚠ Si no puedes asistir, cancela al menos 60 min antes."
        )
        wa.send_text(lead["phone"], body_cli)
    except Exception as e:
        print(f"[book] wa cliente: {e}")

    # WhatsApp al abogado
    try:
        body_lw = (
            "🆕 *Nueva cita agendada*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 {lead.get('name','Cliente')}\n"
            f"📱 +{lead.get('phone','')}\n"
            f"⚖️  Área: {lead.get('area') or '—'}\n"
            f"📅 *{fecha_legible}*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"Caso: {(lead.get('descripcion','') or '')[:280]}…\n\n"
            f"📲 WhatsApp cliente: https://wa.me/{lead.get('phone','')}\n"
            f"📊 Dashboard: {dashboard_url}"
        )
        wa.send_text(lawyer["whatsapp"], body_lw)
    except Exception as e:
        print(f"[book] wa abogado: {e}")

    return {"ok": True, "appointment_id": aid,
            "start": start_dt.isoformat(),
            "lawyer_name": lawyer["name"]}


@app.get("/api/lead/appointment")
async def lead_appointment(token: str):
    lead = db_mod.get_lead_by_token(token)
    if not lead: raise HTTPException(404, "no encontrado")
    appt = db_mod.get_appointment_by_lead(lead["id"])
    if not appt: return {"ok": False, "appointment": None}
    return {"ok": True, "appointment": appt, "puede_cancelar": ag.puede_cancelar(appt["scheduled_at"], 60)}


class CancelReq(BaseModel):
    token: str

@app.post("/api/lead/cancel-appointment")
async def lead_cancel_appt(req: CancelReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead: raise HTTPException(404, "no encontrado")
    appt = db_mod.get_appointment_by_lead(lead["id"])
    if not appt: raise HTTPException(404, "sin cita")
    if not ag.puede_cancelar(appt["scheduled_at"], 60):
        raise HTTPException(400, "Quedan menos de 60 minutos para tu cita: ya no se puede cancelar. Si no puedes asistir, escríbenos por WhatsApp para reprogramar.")
    db_mod.update_appointment_status(appt["id"], "cancelled_by_user")
    db_mod.track_event("meeting_cancelled", ip=_ip_of(request))
    # Notificar al abogado
    lw = db_mod.get_lawyer(appt.get("lawyer_id")) if appt.get("lawyer_id") else None
    if lw:
        try:
            s = ag._parse_dt(appt["scheduled_at"])
            wa.send_text(lw["whatsapp"],
                "❌ *Cita cancelada por el cliente*\n"
                f"📅 {_fecha_es(s)}\n"
                f"👤 {lead.get('name','')} (+{lead.get('phone','')})")
        except Exception as e:
            print(f"[cancel] wa abogado: {e}")
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
    if not ag.puede_cancelar(appt["scheduled_at"], 60):
        raise HTTPException(400, "No puedes reprogramar a menos de 60 min de la cita.")
    # Validar nuevo slot
    new_dt = ag._parse_dt(req.start_iso)
    libres = ag.slots_disponibles(lawyer_id=appt.get("lawyer_id"), dias_adelante=10, max_slots=200)
    if not any(abs((ag._parse_dt(s["start"]) - new_dt).total_seconds()) < 60 for s in libres):
        raise HTTPException(409, "Ese horario no está disponible.")
    db_mod.update_appointment_time(appt["id"], new_dt.isoformat())
    # Notificar a ambos
    lw = db_mod.get_lawyer(appt.get("lawyer_id")) if appt.get("lawyer_id") else None
    for phone, titulo in [(lead.get("phone"), "Cliente"), (lw and lw.get("whatsapp"), "Abogado")]:
        if not phone: continue
        try:
            wa.send_text(phone,
                f"🔄 *Cita reprogramada · Galeano Herrera*\n"
                f"Nueva fecha: *{_fecha_es(new_dt)}* (Bogotá).")
        except Exception as e:
            print(f"[resched] wa: {e}")
    return {"ok": True, "start": new_dt.isoformat()}


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
        "agenda_nativa": True,
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


@app.get("/api/pro/metrics")
async def pro_metrics(lawyer: dict = Depends(auth_mod.require_lawyer)):
    """Métricas personales del abogado: meta diaria, tasa de cierre, embudo 7d."""
    areas = set(lawyer.get("areas") or [])
    todos = "*" in areas
    with db_mod.db() as c:
        # Leads asignados directamente o que cubren su área
        rows = c.execute(
            """SELECT status, area, created_at, contacted_at, verified_at
               FROM leads WHERE lawyer_id=? OR (?=1 AND lawyer_id IS NULL)
               ORDER BY created_at DESC LIMIT 1000""",
            (lawyer["id"], 1 if todos else 0),
        ).fetchall()
        leads = [dict(r) for r in rows]
        if not todos:
            leads = [l for l in leads if not l.get("area") or l.get("area") in areas]

        # Cierres HOY (Bogotá TZ aproximado)
        hoy = c.execute(
            "SELECT COUNT(*) c FROM leads WHERE lawyer_id=? AND status='closed' AND date(contacted_at)=date('now','-5 hours')",
            (lawyer["id"],)
        ).fetchone()["c"]

        # Citas próximas
        citas = c.execute(
            "SELECT COUNT(*) c FROM appointments WHERE lawyer_id=? AND status='scheduled' AND scheduled_at > datetime('now')",
            (lawyer["id"],),
        ).fetchone()["c"]

        # Embudo 7d del abogado
        d7 = c.execute(
            """SELECT status, COUNT(*) c FROM leads
               WHERE (lawyer_id=? OR (?=1 AND lawyer_id IS NULL))
                 AND created_at > datetime('now','-7 days')
               GROUP BY status""",
            (lawyer["id"], 1 if todos else 0),
        ).fetchall()
        emb7d = {r["status"]: r["c"] for r in d7}

    total = len(leads)
    contacted = len([l for l in leads if l["status"] in ("contacted","closed")])
    closed = len([l for l in leads if l["status"] == "closed"])
    verified = len([l for l in leads if l["status"] in ("verified","contacted","closed")])

    # Tiempo promedio de respuesta (verified -> contacted)
    tiempos = []
    for l in leads:
        if l.get("verified_at") and l.get("contacted_at"):
            try:
                v = datetime.fromisoformat(l["verified_at"].replace(" ","T"))
                k = datetime.fromisoformat(l["contacted_at"].replace(" ","T"))
                tiempos.append((k - v).total_seconds() / 3600)
            except Exception:
                pass
    tiempo_resp_h = round(sum(tiempos)/len(tiempos), 1) if tiempos else None

    return {
        "goal_daily": 10,
        "closed_today": hoy,
        "progress_pct": min(100, round(100*hoy/10)),
        "upcoming_appointments": citas,
        "total_leads": total,
        "verified": verified,
        "contacted": contacted,
        "closed": closed,
        "close_rate": round(100*closed/verified, 1) if verified else 0.0,
        "avg_response_hours": tiempo_resp_h,
        "funnel_7d": emb7d,
    }


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


# ── Schedule semanal del abogado (auto-gestión) ──────────────────────────────

class ScheduleBody(BaseModel):
    mon: list = []
    tue: list = []
    wed: list = []
    thu: list = []
    fri: list = []
    sat: list = []
    sun: list = []


@app.get("/api/pro/me/schedule")
async def pro_get_schedule(lawyer: dict = Depends(auth_mod.require_lawyer)):
    return db_mod.get_lawyer_schedule(lawyer["id"])


@app.put("/api/pro/me/schedule")
async def pro_set_schedule(body: ScheduleBody, lawyer: dict = Depends(auth_mod.require_lawyer)):
    try:
        cleaned = db_mod.set_lawyer_schedule(lawyer["id"], body.dict())
        return {"ok": True, "schedule": cleaned}
    except ValueError as e:
        raise HTTPException(400, str(e))


# Admin también puede ver/editar el schedule de cualquier abogado
@app.get("/api/admin/lawyers/{lid}/schedule", dependencies=[Depends(admin_auth)])
async def admin_get_schedule(lid: int):
    if not db_mod.get_lawyer(lid):
        raise HTTPException(404, "lawyer no encontrado")
    return db_mod.get_lawyer_schedule(lid)


@app.put("/api/admin/lawyers/{lid}/schedule", dependencies=[Depends(admin_auth)])
async def admin_set_schedule(lid: int, body: ScheduleBody):
    if not db_mod.get_lawyer(lid):
        raise HTTPException(404, "lawyer no encontrado")
    try:
        cleaned = db_mod.set_lawyer_schedule(lid, body.dict())
        return {"ok": True, "schedule": cleaned}
    except ValueError as e:
        raise HTTPException(400, str(e))


# ── Agenda del abogado (calendar nativo) ─────────────────────────────────────

@app.get("/api/pro/agenda")
async def pro_agenda(start: Optional[str] = None,
                     lawyer: dict = Depends(auth_mod.require_lawyer)):
    """Grid semanal del abogado con slots libres/ocupados/bloqueados."""
    return ag.semana_del_abogado(lawyer["id"], start_date=start)


class BlockCreate(BaseModel):
    start_iso: str
    end_iso: str
    reason: Optional[str] = ""

@app.post("/api/pro/blocks")
async def pro_block_create(body: BlockCreate, lawyer: dict = Depends(auth_mod.require_lawyer)):
    # Validar que no solape con citas programadas
    with db_mod.db() as c:
        conflicts = c.execute(
            """SELECT id FROM appointments WHERE lawyer_id=? AND status='scheduled'
               AND scheduled_at < ? AND datetime(scheduled_at, '+'||duration_min||' minutes') > ?""",
            (lawyer["id"], body.end_iso, body.start_iso),
        ).fetchall()
    if conflicts:
        raise HTTPException(409, f"Ya hay {len(conflicts)} cita(s) agendada(s) en ese rango. Cancélalas primero.")
    bid = db_mod.create_block(lawyer["id"], body.start_iso, body.end_iso, body.reason or "")
    return {"ok": True, "id": bid}


@app.delete("/api/pro/blocks/{bid}")
async def pro_block_delete(bid: int, lawyer: dict = Depends(auth_mod.require_lawyer)):
    db_mod.delete_block(bid, lawyer_id=lawyer["id"])
    return {"ok": True}


class AppointmentUpdate(BaseModel):
    meet_url: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@app.patch("/api/pro/appointments/{aid}")
async def pro_appt_update(aid: int, body: AppointmentUpdate,
                          lawyer: dict = Depends(auth_mod.require_lawyer)):
    appt = db_mod.get_appointment(aid)
    if not appt or appt.get("lawyer_id") != lawyer["id"]:
        raise HTTPException(404, "cita no encontrada")
    if body.meet_url is not None:
        db_mod.update_appointment_meet(aid, body.meet_url.strip())
    if body.status:
        if body.status not in ("scheduled","cancelled_by_lawyer","completed","no_show"):
            raise HTTPException(400, "status inválido")
        db_mod.update_appointment_status(aid, body.status, notes=body.notes or "")
        # Notificar al cliente en cancelación/no_show
        if body.status == "cancelled_by_lawyer":
            with db_mod.db() as c:
                r = c.execute("SELECT phone, name FROM leads WHERE id=?", (appt["lead_id"],)).fetchone()
            if r:
                try:
                    wa.send_text(r["phone"],
                        "❌ *Tu cita fue cancelada por el abogado*\n"
                        "Contáctanos por WhatsApp para reprogramar.")
                except Exception: pass
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


class ProLeadEdit(BaseModel):
    name:        Optional[str] = None
    cedula:      Optional[str] = None
    phone:       Optional[str] = None
    email:       Optional[str] = None
    area:        Optional[str] = None
    descripcion: Optional[str] = None


@app.patch("/api/pro/leads/{lid}")
async def pro_edit_lead(lid: int, body: ProLeadEdit, lawyer: dict = Depends(auth_mod.require_lawyer)):
    """Permite al abogado actualizar los datos del cliente."""
    with db_mod.db() as c:
        r = c.execute("SELECT id, lawyer_id, area FROM leads WHERE id=?", (lid,)).fetchone()
        if not r: raise HTTPException(404, "lead no encontrado")
        areas = set(lawyer.get("areas") or [])
        if r["lawyer_id"] != lawyer["id"] and not ("*" in areas or r["area"] in areas):
            raise HTTPException(403, "no autorizado")
        updates, params = [], []
        if body.name is not None:        updates.append("name=?");        params.append(body.name.strip())
        if body.cedula is not None:      updates.append("cedula=?");      params.append(body.cedula.strip())
        if body.phone is not None:
            ph = wa.normalizar_telefono(body.phone)
            if ph and not wa.es_celular_colombia(ph):
                raise HTTPException(400, "Celular Colombia inválido (formato 3XXXXXXXXX).")
            updates.append("phone=?"); params.append(ph or body.phone.strip())
        if body.email is not None:       updates.append("email=?");       params.append(body.email.strip().lower())
        if body.area is not None:
            if body.area and body.area not in ("salud","pensiones","laboral","accidentes","insolvencia","derechos_fundamentales"):
                raise HTTPException(400, "Área inválida.")
            updates.append("area=?"); params.append(body.area)
        if body.descripcion is not None:
            if len(body.descripcion.strip()) < 10:
                raise HTTPException(400, "La descripción es muy corta.")
            updates.append("descripcion=?"); params.append(body.descripcion.strip())
        if not updates:
            return {"ok": True, "updated": 0}
        params.append(lid)
        c.execute(f"UPDATE leads SET {', '.join(updates)} WHERE id=?", params)
    return {"ok": True, "updated": len(updates)}


class ProDraftSave(BaseModel):
    draft: str = Field(..., min_length=10)
    notes: Optional[str] = None

@app.put("/api/pro/leads/{lid}/draft")
async def pro_save_draft(lid: int, body: ProDraftSave, lawyer: dict = Depends(auth_mod.require_lawyer)):
    """El abogado reemplaza el draft del cliente con su versión trabajada."""
    with db_mod.db() as c:
        r = c.execute("SELECT id, lawyer_id, area FROM leads WHERE id=?", (lid,)).fetchone()
        if not r: raise HTTPException(404, "lead no encontrado")
        # permitir al abogado asignado o a los que cubren el área
        areas = set(lawyer.get("areas") or [])
        if r["lawyer_id"] != lawyer["id"] and not ("*" in areas or r["area"] in areas):
            raise HTTPException(403, "no autorizado para este lead")
        c.execute("UPDATE leads SET draft=?, notes=COALESCE(?,notes) WHERE id=?",
                  (body.draft, body.notes, lid))
    return {"ok": True}


@app.get("/pro/lead/{lid}", response_class=HTMLResponse)
async def pro_lead_workspace(lid: int, request: Request, gh_session: Optional[str] = Cookie(default=None)):
    data = auth_mod.parse_session(gh_session or "")
    if not data:
        return RedirectResponse("/pro/login", status_code=303)
    lw = db_mod.get_lawyer(int(data["lid"]))
    if not lw: return RedirectResponse("/pro/login", status_code=303)
    leads = db_mod.list_leads(limit=2000)
    lead = next((l for l in leads if l["id"] == lid), None)
    if not lead:
        return HTMLResponse("<h1>Lead no encontrado</h1><a href='/pro'>Volver</a>", status_code=404)
    # permiso: asignado o área cubierta
    areas = set(lw.get("areas") or [])
    if lead.get("lawyer_id") != lw["id"] and not ("*" in areas or lead.get("area") in areas):
        return HTMLResponse("<h1>No autorizado</h1><a href='/pro'>Volver</a>", status_code=403)
    return ui_mod.lawyer_workspace_html(lw, lead)


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
                s = ag._parse_dt(appt["scheduled_at"])
                fecha = _fecha_es(s)
                # Mensaje al cliente
                msg_cli = (
                    "🔔 *Recordatorio · Galeano Herrera*\n\n"
                    f"📅 *{fecha}* (Bogotá)\n"
                ) + (
                    "Tu cita es en aproximadamente *24 horas*.\n\n"
                    "El abogado te llamará por WhatsApp a este número.\n"
                    "Si no puedes asistir, cancela desde el sitio o avísanos aquí."
                    if w == "24h" else
                    "Tu cita empieza en aproximadamente *1 hora*.\n\n"
                    "Ten a la mano los documentos de tu caso (cédula, historia clínica, "
                    "comunicaciones con la entidad accionada).\n"
                    "Ya no es posible cancelar desde la app."
                )
                wa.send_text(appt["lead_phone"], msg_cli)

                # A 1h antes, también avisamos al abogado
                if w == "1h" and appt.get("lawyer_id"):
                    lw = db_mod.get_lawyer(appt["lawyer_id"])
                    if lw:
                        msg_lw = (
                            "⏰ *Cita en 1 hora*\n"
                            f"📅 {fecha}\n"
                            f"👤 {appt.get('lead_name','Cliente')}\n"
                            f"📱 https://wa.me/{appt.get('lead_phone','')}\n\n"
                            f"Abre tu dashboard para ver el caso completo:\n"
                            f"https://gh-jurisprudencia-csj.onrender.com/pro"
                        )
                        wa.send_text(lw["whatsapp"], msg_lw)

                db_mod.mark_appointment_reminded(appt["id"], w)
                sent[w] += 1
            except Exception as e:
                print(f"[cron] reminder {w} error: {e}")
    return {"ok": True, "sent": sent}


# ─────────────────────────────────────────────────────────────────────────────
# CEREBRO RAG: carga, transformación con IA y administración de PDFs
# ─────────────────────────────────────────────────────────────────────────────

MAX_PDF_SIZE = 25 * 1024 * 1024  # 25 MB


async def _process_uploaded_pdfs(files: list[UploadFile], lawyer_id: Optional[int],
                                  by_admin: bool, doc_type: str = "otro",
                                  enriquecer: bool = False) -> list[dict]:
    """Procesa PDFs: extrae texto, chunkifica, opcionalmente ficha con IA.
    Por default modo RÁPIDO (sin IA) — para miles de PDFs sin gastar cuota.
    Usa enrich-batch o enrich/{id} después para enriquecer."""
    out = []
    motor = None
    if enriquecer:
        try: motor = get_motor()
        except HTTPException: motor = None

    for upload in files:
        if not upload.filename.lower().endswith(".pdf"):
            out.append({"filename": upload.filename, "ok": False, "error": "Solo se aceptan PDFs."}); continue
        data = await upload.read()
        if len(data) > MAX_PDF_SIZE:
            out.append({"filename": upload.filename, "ok": False,
                        "error": f"Archivo demasiado grande (>25 MB)."}); continue

        doc_id = db_mod.create_rag_document(
            filename=upload.filename, file_size=len(data),
            uploaded_by_lawyer_id=lawyer_id, uploaded_by_admin=by_admin, doc_type=doc_type,
        )
        db_mod.update_rag_document(doc_id, status="processing")

        try:
            res = rag_in.procesar_pdf(data, upload.filename, motor=motor, enriquecer=enriquecer)
            chunks_count = db_mod.add_rag_chunks(doc_id, res["chunks"])
            db_mod.update_rag_document(doc_id,
                status="processed",
                metadata=res["metadata"],
                chunks_count=chunks_count,
                tokens_est=res["tokens_est"],
                processed_at=datetime.now().isoformat(),
                doc_type=res["metadata"].get("tipo") or doc_type,
            )
            out.append({"filename": upload.filename, "ok": True, "doc_id": doc_id,
                        "chunks": chunks_count, "metadata": res["metadata"],
                        "enriched": res.get("enriched", False)})
        except Exception as e:
            db_mod.update_rag_document(doc_id, status="error", error=str(e))
            out.append({"filename": upload.filename, "ok": False, "error": str(e)})
    return out


def _enriquecer_un_doc(doc_id: int, motor) -> dict:
    """Toma un doc existente, carga sus primeros chunks de DB y le pide a IA la metadata."""
    with db_mod.db() as c:
        rows = c.execute(
            "SELECT chunk_index, page, texto FROM rag_chunks WHERE doc_id=? ORDER BY chunk_index LIMIT 6",
            (doc_id,)
        ).fetchall()
    if not rows:
        raise ValueError("doc sin chunks")
    primeros = [{"texto": r["texto"], "page": r["page"]} for r in rows]
    meta = rag_in.enriquecer_documento_existente(motor, primeros)
    db_mod.update_rag_document(doc_id, metadata=meta,
        doc_type=meta.get("tipo") or "otro")
    return meta


# Endpoints ADMIN

@app.post("/api/admin/rag/upload", dependencies=[Depends(admin_auth)])
async def admin_rag_upload(files: list[UploadFile] = File(...), enriquecer: bool = False):
    """Por default modo RÁPIDO (sin IA). Pasa ?enriquecer=true para fichar con IA al subir."""
    if not files:
        raise HTTPException(400, "Sin archivos")
    res = await _process_uploaded_pdfs(files, lawyer_id=None, by_admin=True,
                                        enriquecer=enriquecer)
    return {"ok": True, "results": res, "enriched": enriquecer}


@app.post("/api/admin/rag/documents/{doc_id}/enrich", dependencies=[Depends(admin_auth)])
async def admin_rag_enrich_one(doc_id: int):
    d = db_mod.get_rag_document(doc_id)
    if not d: raise HTTPException(404, "doc no encontrado")
    motor = get_motor()
    try:
        meta = _enriquecer_un_doc(doc_id, motor)
        return {"ok": True, "metadata": meta}
    except Exception as e:
        raise HTTPException(500, str(e))


class EnrichBatchBody(BaseModel):
    limit: int = Field(10, ge=1, le=50)


@app.post("/api/admin/rag/enrich-batch", dependencies=[Depends(admin_auth)])
async def admin_rag_enrich_batch(body: EnrichBatchBody):
    """Toma N documentos en estado 'processed' que NO han sido enriquecidos y les
    aplica IA. Para procesar miles sin saturar la cuota: corre por lotes pequeños."""
    motor = get_motor()
    # buscar pendientes (no _enriched o sin radicado real)
    docs = db_mod.list_rag_documents(status="processed", limit=200)
    pendientes = []
    for d in docs:
        m = d.get("metadata") or {}
        if not m.get("_enriched"):
            pendientes.append(d)
    pendientes = pendientes[:body.limit]

    enriquecidos = []
    for d in pendientes:
        try:
            meta = _enriquecer_un_doc(d["id"], motor)
            enriquecidos.append({"doc_id": d["id"], "filename": d["filename"],
                                  "ok": True, "tipo": meta.get("tipo"),
                                  "radicado": meta.get("radicado")})
        except Exception as e:
            enriquecidos.append({"doc_id": d["id"], "filename": d["filename"],
                                  "ok": False, "error": str(e)})
    return {"ok": True, "processed": len(enriquecidos), "results": enriquecidos,
            "remaining_pending": max(0, len(pendientes) - body.limit + (len(docs) - len(pendientes)))}


@app.get("/api/admin/rag/documents", dependencies=[Depends(admin_auth)])
async def admin_rag_list(status: Optional[str] = None, limit: int = 200):
    docs = db_mod.list_rag_documents(status=status, limit=limit)
    # quitar chunks (pesa) del listado
    for d in docs:
        d.pop("error", None) if not d.get("error") else None
    return {"documents": docs, "stats": db_mod.rag_stats()}


@app.get("/api/admin/rag/documents/{doc_id}", dependencies=[Depends(admin_auth)])
async def admin_rag_detail(doc_id: int):
    d = db_mod.get_rag_document(doc_id)
    if not d: raise HTTPException(404, "doc no encontrado")
    # adjuntar chunks (preview de los primeros 5)
    with db_mod.db() as c:
        rows = c.execute(
            "SELECT chunk_index, page, texto FROM rag_chunks WHERE doc_id=? ORDER BY chunk_index LIMIT 6",
            (doc_id,)
        ).fetchall()
    d["chunks_preview"] = [{"chunk_index": r["chunk_index"], "page": r["page"],
                            "texto": r["texto"][:600] + ("…" if len(r["texto"])>600 else "")}
                           for r in rows]
    return d


class RagApprovalBody(BaseModel):
    notes: Optional[str] = None


@app.post("/api/admin/rag/documents/{doc_id}/approve", dependencies=[Depends(admin_auth)])
async def admin_rag_approve(doc_id: int, body: RagApprovalBody = None):
    d = db_mod.get_rag_document(doc_id)
    if not d: raise HTTPException(404, "doc no encontrado")
    if d["status"] not in ("processed", "rejected"):
        raise HTTPException(400, f"No se puede aprobar desde estado '{d['status']}'.")
    db_mod.update_rag_document(doc_id, status="approved",
                                approved_at=datetime.now().isoformat(),
                                approved_by="admin",
                                notes=(body.notes if body else None))
    # Forzar recarga del motor para que los nuevos chunks aparezcan en BM25
    global _motor, _motor_lite
    _motor = None; _motor_lite = None
    return {"ok": True}


@app.post("/api/admin/rag/documents/{doc_id}/reject", dependencies=[Depends(admin_auth)])
async def admin_rag_reject(doc_id: int, body: RagApprovalBody = None):
    d = db_mod.get_rag_document(doc_id)
    if not d: raise HTTPException(404, "doc no encontrado")
    db_mod.update_rag_document(doc_id, status="rejected",
                                notes=(body.notes if body else None))
    global _motor, _motor_lite
    _motor = None; _motor_lite = None
    return {"ok": True}


@app.delete("/api/admin/rag/documents/{doc_id}", dependencies=[Depends(admin_auth)])
async def admin_rag_delete(doc_id: int):
    d = db_mod.get_rag_document(doc_id)
    if not d: raise HTTPException(404, "doc no encontrado")
    db_mod.delete_rag_document(doc_id)
    global _motor, _motor_lite
    _motor = None; _motor_lite = None
    return {"ok": True}


@app.post("/api/admin/rag/reindex", dependencies=[Depends(admin_auth)])
async def admin_rag_reindex():
    """Regenera el índice FAISS desde 0 (incluyendo fichas CSJ + chunks aprobados)."""
    api_key = obtener_api_key()
    if not api_key:
        raise HTTPException(503, "GEMINI_API_KEY no configurada.")
    # Por ahora reusa el endpoint de indexar (que lee fichas_index.jsonl).
    # En el futuro podemos hacer indexación incremental de los chunks aprobados.
    motor = MotorRAG(api_key=api_key)
    n = motor.indexar(forzar=True)
    global _motor
    _motor = motor
    return {"ok": True, "fichas_indexadas": n,
            "chunks_aprobados": db_mod.rag_stats()["chunks_in_rag"]}


# Endpoints PRO (abogado autenticado puede subir, ver, NO aprobar)

@app.post("/api/pro/rag/upload")
async def pro_rag_upload(files: list[UploadFile] = File(...),
                          lawyer: dict = Depends(auth_mod.require_lawyer)):
    """Modo RÁPIDO siempre (los abogados nunca disparan IA al subir, para preservar
    cuota global). El admin puede después enriquecer en lote."""
    if not files:
        raise HTTPException(400, "Sin archivos")
    res = await _process_uploaded_pdfs(files, lawyer_id=lawyer["id"], by_admin=False,
                                        enriquecer=False)
    return {"ok": True, "results": res}


@app.get("/api/pro/rag/documents")
async def pro_rag_list(only_mine: bool = False,
                        lawyer: dict = Depends(auth_mod.require_lawyer)):
    docs = db_mod.list_rag_documents(
        lawyer_id=lawyer["id"] if only_mine else None
    )
    # los abogados ven solo: sus propios docs (cualquier estado) + los aprobados de todos
    if not only_mine:
        docs = [d for d in docs
                if d["status"] == "approved" or d.get("uploaded_by_lawyer_id") == lawyer["id"]]
    return {"documents": docs, "stats": db_mod.rag_stats()}


@app.get("/api/pro/rag/documents/{doc_id}")
async def pro_rag_detail(doc_id: int, lawyer: dict = Depends(auth_mod.require_lawyer)):
    d = db_mod.get_rag_document(doc_id)
    if not d: raise HTTPException(404, "doc no encontrado")
    # permiso: aprobado para todos, o suyo en cualquier estado
    if d["status"] != "approved" and d.get("uploaded_by_lawyer_id") != lawyer["id"]:
        raise HTTPException(403, "No autorizado")
    with db_mod.db() as c:
        rows = c.execute(
            "SELECT chunk_index, page, texto FROM rag_chunks WHERE doc_id=? ORDER BY chunk_index LIMIT 6",
            (doc_id,)
        ).fetchall()
    d["chunks_preview"] = [{"chunk_index": r["chunk_index"], "page": r["page"],
                            "texto": r["texto"][:600] + ("…" if len(r["texto"])>600 else "")}
                           for r in rows]
    return d


# ─────────────────────────────────────────────────────────────────────────────
# EXPEDIENTES (mandato escrito + OTP de aceptación + bitácora silenciosa)
# ─────────────────────────────────────────────────────────────────────────────

class ExpedienteCreateBody(BaseModel):
    alcance: str = Field("", max_length=2000)
    area: Optional[str] = None
    honorarios_cop: Optional[int] = Field(None, ge=0, le=200_000_000)
    honorarios_modalidad: str = Field("fijo")  # fijo|porcentaje|mixto|contingente|pro_bono
    honorarios_descripcion: str = Field("", max_length=600)
    obligaciones_cliente: str = Field("", max_length=1000)


class ExpedienteUpdateBody(ExpedienteCreateBody):
    estado: Optional[str] = None
    closed_reason: Optional[str] = None


@app.post("/api/pro/leads/{lid}/expediente")
async def pro_crear_expediente(lid: int, body: ExpedienteCreateBody,
                                lawyer: dict = Depends(auth_mod.require_lawyer)):
    """Crea un expediente en estado 'borrador' para el lead. Sin OTP aún —
    el abogado puede ajustar antes de enviarlo al cliente."""
    leads = db_mod.list_leads(limit=2000)
    lead = next((l for l in leads if l["id"] == lid), None)
    if not lead: raise HTTPException(404, "lead no encontrado")
    # Validar honorarios — alerta silenciosa por porcentaje > 40%
    if body.honorarios_modalidad == "porcentaje" and (body.honorarios_cop or 0) > 40:
        # honorarios_cop en este caso representa el porcentaje
        pass  # solo se registra, no bloquea
    e = db_mod.crear_expediente(
        lead_id=lid, lawyer_id=lawyer["id"], by_lawyer_id=lawyer["id"],
        alcance=body.alcance, area=body.area or lead.get("area"),
        honorarios_cop=body.honorarios_cop,
        honorarios_modalidad=body.honorarios_modalidad,
        honorarios_descripcion=body.honorarios_descripcion,
        obligaciones_cliente=body.obligaciones_cliente,
    )
    return e


@app.patch("/api/pro/expedientes/{eid}")
async def pro_editar_expediente(eid: int, body: ExpedienteUpdateBody,
                                 lawyer: dict = Depends(auth_mod.require_lawyer)):
    e = db_mod.get_expediente(eid)
    if not e: raise HTTPException(404, "expediente no encontrado")
    if e.get("lawyer_id") != lawyer["id"]:
        raise HTTPException(403, "no autorizado")
    fields = {k: v for k, v in body.dict().items() if v is not None}
    upd = db_mod.update_expediente(eid, by_lawyer_id=lawyer["id"], **fields)
    return upd


@app.post("/api/pro/expedientes/{eid}/send-otp")
async def pro_send_otp_expediente(eid: int, lawyer: dict = Depends(auth_mod.require_lawyer)):
    e = db_mod.get_expediente(eid)
    if not e: raise HTTPException(404, "expediente no encontrado")
    if e.get("lawyer_id") != lawyer["id"]:
        raise HTTPException(403, "no autorizado")
    if e["estado"] not in ("borrador", "pendiente_aceptacion"):
        raise HTTPException(400, f"No se puede enviar OTP desde estado '{e['estado']}'.")
    if not e.get("lead_phone"):
        raise HTTPException(400, "El lead no tiene teléfono registrado.")
    # generar y enviar
    otp = wa.generar_otp()
    db_mod.expediente_set_otp(eid, otp, ttl_seconds=1800,
                                by_lawyer_id=lawyer["id"], phone=e["lead_phone"])
    base = os.environ.get("PUBLIC_URL", "https://gh-jurisprudencia-csj.onrender.com").rstrip("/")
    url = f"{base}/expediente/aceptar?t={e['token']}"
    monto = e.get("honorarios_cop") or 0
    modalidad = e.get("honorarios_modalidad") or "—"
    body = (
        "📋 *Galeano Herrera | Abogados*\n\n"
        f"Hola {e.get('lead_name','Cliente')}, tu abogado *{e.get('lawyer_name','—')}* "
        f"te propone iniciar el servicio:\n\n"
        f"*Expediente:* {e['numero']}\n"
        f"*Alcance:* {(e.get('alcance') or '—')[:300]}\n"
        f"*Honorarios:* {modalidad}"
        + (f" · ${monto:,} COP" if monto else "")
        + "\n\n"
        f"Para aceptar y abrir tu expediente, ingresa este código en:\n{url}\n\n"
        f"*Código:* {otp}\n_(válido 30 minutos)_\n\n"
        "Al aceptar firmas electrónicamente el mandato (Ley 527/99)."
    )
    res = wa.send_text(e["lead_phone"], body)
    out = {"ok": res.get("sent", False), "url": url}
    if wa.DEV_MODE: out["otp_debug"] = otp
    return out


@app.get("/api/pro/expedientes")
async def pro_listar_expedientes(lawyer: dict = Depends(auth_mod.require_lawyer),
                                   estado: Optional[str] = None):
    return db_mod.list_expedientes(lawyer_id=lawyer["id"], estado=estado)


@app.get("/api/pro/expedientes/{eid}")
async def pro_get_expediente(eid: int, lawyer: dict = Depends(auth_mod.require_lawyer)):
    e = db_mod.get_expediente(eid)
    if not e: raise HTTPException(404, "no encontrado")
    if e.get("lawyer_id") != lawyer["id"]:
        raise HTTPException(403, "no autorizado")
    return e


@app.get("/api/pro/leads/{lid}/expediente")
async def pro_get_expediente_lead(lid: int, lawyer: dict = Depends(auth_mod.require_lawyer)):
    """Retorna el expediente del lead si existe, o 404."""
    e = db_mod.get_expediente_by_lead(lid)
    if not e: raise HTTPException(404, "sin expediente")
    return e


# Endpoints PÚBLICOS para que el cliente acepte con OTP

class ExpAcceptBody(BaseModel):
    token: str
    otp: str = Field(..., min_length=6, max_length=6)


@app.get("/api/expediente/{token}/info")
async def public_exp_info(token: str):
    """Devuelve info pública del expediente para mostrar al cliente antes de OTP."""
    e = db_mod.get_expediente_by_token(token)
    if not e: raise HTTPException(404, "Expediente no encontrado")
    # Solo info necesaria para mostrar al cliente
    return {
        "numero": e["numero"], "estado": e["estado"],
        "alcance": e.get("alcance"),
        "honorarios_cop": e.get("honorarios_cop"),
        "honorarios_modalidad": e.get("honorarios_modalidad"),
        "honorarios_descripcion": e.get("honorarios_descripcion"),
        "obligaciones_cliente": e.get("obligaciones_cliente"),
        "expirable": e["estado"] == "pendiente_aceptacion",
    }


@app.post("/api/expediente/accept")
async def public_exp_accept(body: ExpAcceptBody, request: Request):
    res = db_mod.expediente_verificar_otp(body.token, body.otp, ip=_ip_of(request))
    if not res["ok"]:
        raise HTTPException(400, res["error"])
    return {"ok": True, "numero": res["expediente"]["numero"]}


@app.get("/expediente/aceptar", response_class=HTMLResponse)
async def public_exp_pagina(t: str = ""):
    return ui_mod.expediente_aceptar_html(t)


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
        "agenda_nativa": True,
        "version": app.version,
    }


# ── Entrada directa ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
