#!/usr/bin/env python3
"""
============================================================
APP JURISPRUDENCIA — GALEANO HERRERA | ABOGADOS  (v3)
============================================================
- /             → Landing pública (clientes) → genera borrador → OTP → descarga
- /admin        → Panel admin (Basic Auth) — abogados, leads, métricas
- /pro          → App de abogado con RAG completo
- /api/lead/*   → Endpoints de captura de leads (público)
- /api/admin/*  → CRUD admin (Basic Auth)
- /api/pro/*    → RAG completo (sin auth por defecto, opcional Basic Auth)
============================================================
"""

from __future__ import annotations

import asyncio
import os
import secrets
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fastapi import FastAPI, HTTPException, Query, Depends, Request, status, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, EmailStr

# ── Imports internos ──────────────────────────────────────────────────────────
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

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Jurisprudencia CSJ — Galeano Herrera | Abogados",
    description="Plataforma de captación legal con RAG jurisprudencial.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"],
)


# ── Auth ───────────────────────────────────────────────────────────────────────

_admin_security = HTTPBasic(auto_error=True)
_pro_security   = HTTPBasic(auto_error=False)


def admin_auth(creds: HTTPBasicCredentials = Depends(_admin_security)):
    user = os.environ.get("ADMIN_USER", "admin")
    pwd  = os.environ.get("ADMIN_PASS", "galeanoherrera2025")
    if not (secrets.compare_digest(creds.username, user) and secrets.compare_digest(creds.password, pwd)):
        raise HTTPException(401, "Credenciales inválidas",
                            headers={"WWW-Authenticate": 'Basic realm="admin"'})


def pro_auth(creds: Optional[HTTPBasicCredentials] = Depends(_pro_security)):
    user = os.environ.get("APP_USER")
    pwd  = os.environ.get("APP_PASS")
    if not (user and pwd):
        return  # auth deshabilitada
    if creds is None or not (
        secrets.compare_digest(creds.username, user) and secrets.compare_digest(creds.password, pwd)
    ):
        raise HTTPException(401, "Credenciales inválidas",
                            headers={"WWW-Authenticate": 'Basic realm="pro"'})


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


@app.on_event("startup")
async def _startup_event():
    threading.Thread(target=_auto_index_background, daemon=True).start()


# ─────────────────────────────────────────────────────────────────────────────
# PÚBLICO — Landing
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def landing():
    return ui_mod.landing_html()


# ── Modelos lead ──────────────────────────────────────────────────────────────

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


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ip_of(req: Request) -> str:
    fwd = req.headers.get("x-forwarded-for")
    return (fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")) or "0.0.0.0"


# ── Endpoints lead ────────────────────────────────────────────────────────────

@app.post("/api/lead/preview")
async def lead_preview(req: LeadPreviewReq, request: Request):
    ip = _ip_of(request)
    if not db_mod.check_rate(ip, max_per_hour=5):
        raise HTTPException(429, "Has excedido el límite de borradores por hora desde tu conexión. Intenta más tarde.")

    motor = get_motor()
    res = tl.generar_borrador(motor, req.descripcion, area=req.area)
    if "error" in res:
        # Mensaje amigable al usuario; código 503 si fue rate-limit
        msg = res.get("user_message") or res["error"]
        code = 503 if res["error"] == "rate_limited" else 400
        raise HTTPException(code, msg)

    token = uuid.uuid4().hex
    db_mod.create_lead(
        token=token,
        descripcion=req.descripcion,
        area=res.get("area_detectada") or req.area,
        draft=res["draft"],
        fichas=res["fichas"],
        ip=ip,
        user_agent=request.headers.get("user-agent","")[:300],
    )
    preview = tl.construir_preview(res["draft"], palabras_visibles=180)
    return {
        "token": token,
        "preview": preview,
        "fichas": res["fichas"],
        "area_detectada": res.get("area_detectada"),
        "tokens_aprox": res.get("tokens_aprox"),
        "cached": res.get("cached", False),
    }


@app.post("/api/lead/register")
async def lead_register(req: LeadRegisterReq):
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
        raise HTTPException(404, "Sesión expirada. Vuelve a generar el borrador.")

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
        raise HTTPException(400, "No hay registro pendiente para este borrador.")
    res = wa.crear_y_enviar_otp(lead["phone"])
    return {"ok": res["ok"], **({"otp_debug": res["otp_debug"]} if "otp_debug" in res else {})}


@app.post("/api/lead/verify-otp")
async def lead_verify(req: LeadOtpReq, request: Request):
    lead = db_mod.get_lead_by_token(req.token)
    if not lead:
        raise HTTPException(404, "Borrador no encontrado.")
    if lead["status"] not in ("pending_otp", "verified"):
        raise HTTPException(400, "Lead en estado inválido.")

    if lead["status"] == "pending_otp":
        if not wa.verificar_otp(lead["phone"], req.otp):
            raise HTTPException(400, "Código incorrecto o vencido. Reenvía y vuelve a intentar.")

        lawyer = db_mod.lawyer_for_area(lead["area"])
        lead = db_mod.mark_lead_verified(req.token, lawyer["id"] if lawyer else None)

        # Notificar al abogado por WhatsApp (best-effort, no bloquea descarga)
        if lawyer:
            try:
                base = str(request.base_url).rstrip("/")
                download_url = f"{base}/api/lead/download/{req.token}.docx"
                wa.notificar_lead_a_abogado(lawyer["whatsapp"], lead, download_url)
            except Exception as e:
                print(f"[wa-notify] error: {e}")

    return {"ok": True, "download_url": f"/api/lead/download/{req.token}.docx"}


@app.get("/api/lead/download/{token}.docx")
async def lead_download(token: str):
    lead = db_mod.get_lead_by_token(token)
    if not lead:
        raise HTTPException(404, "Borrador no encontrado.")
    if lead["status"] not in ("verified", "contacted", "closed"):
        raise HTTPException(403, "Verifica tu OTP primero.")
    nombre = lead.get("name") or "cliente"
    docx_bytes = tl.borrador_a_docx(lead["draft"], nombre)
    safe = "".join(c for c in nombre if c.isalnum() or c in " _-")[:40].replace(" ", "_") or "borrador"
    return StreamingResponse(
        iter([docx_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="borrador_tutela_{safe}.docx"'},
    )


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — Panel + REST
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(admin_auth)])
async def admin_panel():
    return ui_mod.admin_html()


@app.get("/api/admin/stats", dependencies=[Depends(admin_auth)])
async def admin_stats():
    return db_mod.stats()


@app.get("/api/admin/leads", dependencies=[Depends(admin_auth)])
async def admin_list_leads(status: Optional[str] = None, limit: int = 200):
    out = db_mod.list_leads(limit=limit, status=status)
    # Ocultamos el draft completo en el listado (pesa); se obtiene por id
    for l in out: l["draft"] = (l.get("draft") or "")[:280] + ("…" if l.get("draft") and len(l["draft"])>280 else "")
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
    areas: list[str] = []
    is_default: bool = False

@app.post("/api/admin/lawyers", dependencies=[Depends(admin_auth)])
async def admin_create_lawyer(body: LawyerCreate):
    wa_norm = wa.normalizar_telefono(body.whatsapp)
    if len(wa_norm) < 10:
        raise HTTPException(400, "WhatsApp inválido (formato 573XXXXXXXXX).")
    lid = db_mod.create_lawyer(name=body.name.strip(), whatsapp=wa_norm,
                                areas=body.areas, is_default=body.is_default)
    return {"ok": True, "id": lid}


@app.delete("/api/admin/lawyers/{lid}", dependencies=[Depends(admin_auth)])
async def admin_delete_lawyer(lid: int):
    db_mod.delete_lawyer(lid); return {"ok": True}


@app.get("/api/admin/config", dependencies=[Depends(admin_auth)])
async def admin_config():
    motor = get_motor_lite()
    lawyer = db_mod.lawyer_for_area(None)
    return {
        "gemini_api_key": bool(obtener_api_key()),
        "faiss_listo": motor._listo,
        "fichas": len(motor.meta),
        "ultramsg": bool(wa.ULTRAMSG_INSTANCE and wa.ULTRAMSG_TOKEN),
        "lawyer_default": (lawyer["name"] + " (+" + lawyer["whatsapp"] + ")") if lawyer else None,
        "dev_mode": wa.DEV_MODE,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PRO — App del abogado con RAG completo (la UI v2 anterior)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/pro", response_class=HTMLResponse, dependencies=[Depends(pro_auth)])
async def pro_app():
    return _pro_html()


# Endpoints /api/pro/* (RAG full power)

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


@app.post("/api/pro/consultar", dependencies=[Depends(pro_auth)])
async def pro_consultar(req: ConsultaRequest):
    motor = get_motor()
    res = motor.consultar(req.pregunta, filtro_area=req.area, filtro_anio=req.anio,
                          filtro_sala=req.sala, modo="respuesta", rerank=req.rerank,
                          top_k=req.top_k)
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.post("/api/pro/analizar-caso", dependencies=[Depends(pro_auth)])
async def pro_caso(req: CasoRequest):
    motor = get_motor()
    q = req.descripcion if not req.nombre_cliente else f"Cliente: {req.nombre_cliente}. {req.descripcion}"
    res = motor.consultar(q, filtro_area=req.area, modo="caso")
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.post("/api/pro/generar-tutela", dependencies=[Depends(pro_auth)])
async def pro_tutela(req: TutelaRequest):
    motor = get_motor()
    datos = (
        f"Accionante: {req.nombre}, CC {req.cedula}. "
        f"Accionado: {req.accionado}. "
        f"Derecho vulnerado: {req.derecho_vulnerado}. "
        f"Hechos: {req.hechos}"
    )
    res = motor.consultar(datos, filtro_area=req.area, modo="tutela")
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.get("/api/pro/linea-jurisprudencial", dependencies=[Depends(pro_auth)])
async def pro_linea(tema: str = Query(..., min_length=3), area: Optional[str] = None):
    motor = get_motor()
    res = motor.consultar(tema, filtro_area=area, modo="linea")
    if "error" in res: raise HTTPException(500, res["error"])
    return res

@app.get("/api/pro/buscar", dependencies=[Depends(pro_auth)])
async def pro_buscar(q: str = Query(..., min_length=2), area: Optional[str] = None,
                     anio: Optional[int] = None, sala: Optional[str] = None,
                     top_k: int = Query(10, le=25)):
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

@app.get("/api/pro/estadisticas", dependencies=[Depends(pro_auth)])
async def pro_stats():
    return get_motor_lite().estadisticas()


# ── Salud / health ────────────────────────────────────────────────────────────

@app.get("/salud")
async def salud():
    if not RAG_OK:
        return {"status": "rag_off", "timestamp": datetime.now().isoformat()}
    motor = get_motor_lite()
    return {
        "status"      : "ok",
        "timestamp"   : datetime.now().isoformat(),
        "faiss_listo" : motor._listo,
        "bm25_listo"  : motor.bm25 is not None,
        "fichas"      : len(motor.meta),
        "api_key"     : bool(obtener_api_key()),
        "ultramsg"    : bool(wa.ULTRAMSG_INSTANCE and wa.ULTRAMSG_TOKEN),
        "version"     : app.version,
    }


# ─────────────────────────────────────────────────────────────────────────────
# UI Pro (HTML — la v2 anterior, llamando ahora a /api/pro/*)
# ─────────────────────────────────────────────────────────────────────────────

def _pro_html() -> str:
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Galeano Herrera | App Pro · Jurisprudencia CSJ</title>
<style>
  :root{--azul:#002347;--oro:#C5A059;--gris:#f4f6f9;--texto:#1a2332;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',sans-serif;background:var(--gris);color:var(--texto);}
  header{background:var(--azul);color:#fff;padding:16px 32px;display:flex;align-items:center;
         gap:16px;border-bottom:3px solid var(--oro);}
  .logo{font-size:24px;font-weight:800;letter-spacing:-1px;}.logo span{color:var(--oro);}
  .subtitle{font-size:12px;opacity:.75;letter-spacing:2px;text-transform:uppercase;}
  .container{max-width:1100px;margin:0 auto;padding:24px 16px;}
  .tabs{display:flex;gap:4px;margin-bottom:24px;border-bottom:2px solid var(--azul);flex-wrap:wrap;}
  .tab{padding:10px 18px;cursor:pointer;border-radius:6px 6px 0 0;border:2px solid transparent;
       border-bottom:none;font-weight:600;font-size:13px;color:var(--azul);background:#fff;}
  .tab:hover{background:#e8ecf3;} .tab.active{background:var(--azul);color:#fff;}
  .panel{display:none;} .panel.active{display:block;}
  .card{background:#fff;border-radius:10px;padding:24px;box-shadow:0 2px 12px rgba(0,35,71,.08);margin-bottom:20px;}
  label{display:block;font-size:12px;font-weight:700;color:var(--azul);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}
  input,textarea,select{width:100%;padding:10px 14px;border:2px solid #dce3ef;border-radius:6px;font-size:14px;color:var(--texto);font-family:inherit;}
  textarea{resize:vertical;min-height:90px;}
  .row{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}
  @media(max-width:600px){.row,.row3{grid-template-columns:1fr;}}
  .btn{background:var(--azul);color:#fff;border:none;padding:12px 28px;border-radius:6px;font-size:14px;font-weight:700;cursor:pointer;}
  .btn:hover{background:#003d7a;} .btn.gold{background:var(--oro);} .btn.gold:hover{background:#a88440;}
  .result{background:#f0f4fa;border-left:4px solid var(--azul);padding:16px;border-radius:0 6px 6px 0;
          white-space:pre-wrap;font-size:14px;line-height:1.65;max-height:600px;overflow-y:auto;display:none;}
  .result.visible{display:block;}
  .fuentes{font-size:12px;color:#666;margin-top:10px;padding:8px 12px;background:#fff;border-radius:4px;border:1px solid #dce3ef;display:none;}
  .fuentes b{color:var(--azul);}
  .spinner{display:none;margin:16px 0;color:var(--azul);font-size:14px;} .spinner.visible{display:block;}
  .badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;margin:2px;background:#e3f0ff;color:#004a9f;}
  h3{font-size:16px;color:var(--azul);margin-bottom:16px;}
  .form-group{margin-bottom:16px;}
  .stat{display:inline-block;background:#fff;border:1px solid #dce3ef;border-radius:6px;padding:8px 14px;margin:4px;font-size:13px;color:var(--azul);font-weight:700;}
  .stat span{color:var(--oro);}
</style></head><body>
<header>
  <div><div class="logo">Galeano <span>Herrera</span></div>
  <div class="subtitle">App Pro · RAG Híbrido · Uso interno</div></div>
  <div style="margin-left:auto"><a href="/admin" style="color:var(--oro);font-size:13px;text-decoration:none">⚙ Admin</a> · <a href="/" style="color:var(--oro);font-size:13px;text-decoration:none">Landing</a></div>
</header>
<div class="container">
  <div id="stats-bar"></div>
  <div class="tabs">
    <div class="tab active" onclick="showTab('consultar')">🔍 Consultar</div>
    <div class="tab" onclick="showTab('caso')">📋 Analizar Caso</div>
    <div class="tab" onclick="showTab('tutela')">⚖ Tutela</div>
    <div class="tab" onclick="showTab('linea')">📈 Línea</div>
    <div class="tab" onclick="showTab('buscar')">🗂 Buscar</div>
  </div>
  <div id="panel-consultar" class="panel active"><div class="card"><h3>Consulta Jurisprudencial</h3>
    <div class="form-group"><label>Pregunta</label>
      <textarea id="q-pregunta" placeholder="Ej: EPS Sanitas niega cirugía urgente..."></textarea></div>
    <div class="row3">
      <div><label>Área</label><select id="q-area">
        <option value="">Todas</option><option value="salud">Salud</option><option value="pensiones">Pensiones</option>
        <option value="laboral">Laboral</option><option value="accidentes">Accidentes</option>
        <option value="insolvencia">Insolvencia</option><option value="derechos_fundamentales">DD.FF.</option></select></div>
      <div><label>Sala</label><select id="q-sala">
        <option value="">Todas</option><option value="CIVIL">Civil</option><option value="LABORAL">Laboral</option>
        <option value="PENAL">Penal</option><option value="PLENA">Plena</option><option value="INSOLVENCIA">Insolvencia</option></select></div>
      <div><label>Año</label><input type="number" id="q-anio" min="2014" max="2030" placeholder="ej. 2024"></div>
    </div><br>
    <button class="btn" onclick="consultar()">Consultar</button>
    <div class="spinner" id="q-spinner">⏳ Generando análisis…</div>
    <div class="result" id="q-result"></div><div class="fuentes" id="q-fuentes"></div>
  </div></div>
  <div id="panel-caso" class="panel"><div class="card"><h3>Analizar Caso (Protocolo Galeano Herrera)</h3>
    <div class="row">
      <div class="form-group"><label>Cliente</label><input id="caso-nombre" placeholder="María García"></div>
      <div class="form-group"><label>Área</label><select id="caso-area"><option value="">Auto</option>
        <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
        <option value="laboral">Laboral</option><option value="accidentes">Accidentes</option>
        <option value="insolvencia">Insolvencia</option></select></div></div>
    <div class="form-group"><label>Descripción</label><textarea id="caso-desc" style="min-height:130px"></textarea></div>
    <button class="btn" onclick="analizarCaso()">Analizar</button>
    <div class="spinner" id="caso-spinner">⏳ Analizando…</div>
    <div class="result" id="caso-result"></div><div class="fuentes" id="caso-fuentes"></div>
  </div></div>
  <div id="panel-tutela" class="panel"><div class="card"><h3>Generar Tutela</h3>
    <div class="row">
      <div class="form-group"><label>Nombre</label><input id="t-nombre"></div>
      <div class="form-group"><label>Cédula</label><input id="t-cedula"></div></div>
    <div class="row">
      <div class="form-group"><label>Accionado</label><input id="t-accionado"></div>
      <div class="form-group"><label>Derecho vulnerado</label><input id="t-derecho"></div></div>
    <div class="form-group"><label>Hechos</label><textarea id="t-hechos" style="min-height:130px"></textarea></div>
    <div class="form-group"><label>Área</label><select id="t-area">
      <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
      <option value="laboral">Laboral</option><option value="derechos_fundamentales">DD.FF.</option></select></div>
    <button class="btn gold" onclick="generarTutela()">⚖ Generar Borrador</button>
    <div class="spinner" id="t-spinner">⏳ Generando…</div>
    <div class="result" id="t-result"></div><div class="fuentes" id="t-fuentes"></div>
  </div></div>
  <div id="panel-linea" class="panel"><div class="card"><h3>Línea Jurisprudencial</h3>
    <div class="form-group"><label>Tema</label><input id="l-tema"></div>
    <div class="row"><div><label>Área</label><select id="l-area"><option value="">Todas</option>
      <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
      <option value="laboral">Laboral</option><option value="accidentes">Accidentes</option>
      <option value="insolvencia">Insolvencia</option></select></div>
      <div style="display:flex;align-items:flex-end"><button class="btn" onclick="explorarLinea()">Explorar</button></div></div>
    <div class="spinner" id="l-spinner">⏳ Analizando…</div>
    <div class="result" id="l-result"></div><div class="fuentes" id="l-fuentes"></div>
  </div></div>
  <div id="panel-buscar" class="panel"><div class="card"><h3>Búsqueda híbrida</h3>
    <div class="row"><div class="form-group"><label>Búsqueda</label><input id="b-query"></div>
      <div style="display:flex;align-items:flex-end"><button class="btn" onclick="buscarFichas()">Buscar</button></div></div>
    <div class="spinner" id="b-spinner">⏳…</div><div id="b-result"></div>
  </div></div>
</div>
<script>
const API='/api/pro';
function showTab(n){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelector(`[onclick="showTab('${n}')"]`).classList.add('active');
  document.getElementById('panel-'+n).classList.add('active');}
function spin(id,on){document.getElementById(id).className='spinner'+(on?' visible':'');}
function showResult(id,t){const e=document.getElementById(id);e.textContent=t;e.className='result visible';}
function showFuentes(id,fichas){const e=document.getElementById(id);
  if(!fichas||!fichas.length){e.style.display='none';return;}
  e.style.display='block';
  e.innerHTML='<b>Fichas usadas:</b> '+fichas.map(f=>`<span class="badge">${f.id}</span>`).join(' ');}
async function post(u,d){const r=await fetch(API+u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
  if(!r.ok){const e=await r.json();throw new Error(e.detail||'Error');}return r.json();}
async function get(u){const r=await fetch(API+u);if(!r.ok){const e=await r.json();throw new Error(e.detail||'Error');}return r.json();}
async function consultar(){const p=document.getElementById('q-pregunta').value.trim();if(!p)return;
  spin('q-spinner',true);try{const d=await post('/consultar',{pregunta:p,
    area:document.getElementById('q-area').value||null,sala:document.getElementById('q-sala').value||null,
    anio:parseInt(document.getElementById('q-anio').value)||null});
    showResult('q-result',d.respuesta);showFuentes('q-fuentes',d.fichas_usadas);}
  catch(e){showResult('q-result','❌ '+e.message);}spin('q-spinner',false);}
async function analizarCaso(){const d=document.getElementById('caso-desc').value.trim();if(!d)return;
  spin('caso-spinner',true);try{const r=await post('/analizar-caso',{descripcion:d,
    nombre_cliente:document.getElementById('caso-nombre').value,
    area:document.getElementById('caso-area').value||null});
    showResult('caso-result',r.respuesta);showFuentes('caso-fuentes',r.fichas_usadas);}
  catch(e){showResult('caso-result','❌ '+e.message);}spin('caso-spinner',false);}
async function generarTutela(){const n=document.getElementById('t-nombre').value.trim();
  const h=document.getElementById('t-hechos').value.trim();if(!n||!h)return alert('Nombre y hechos');
  spin('t-spinner',true);try{const r=await post('/generar-tutela',{nombre:n,
    cedula:document.getElementById('t-cedula').value,accionado:document.getElementById('t-accionado').value,
    hechos:h,derecho_vulnerado:document.getElementById('t-derecho').value,
    area:document.getElementById('t-area').value});
    showResult('t-result',r.respuesta);showFuentes('t-fuentes',r.fichas_usadas);}
  catch(e){showResult('t-result','❌ '+e.message);}spin('t-spinner',false);}
async function explorarLinea(){const t=document.getElementById('l-tema').value.trim();if(!t)return;
  spin('l-spinner',true);try{const a=document.getElementById('l-area').value;
    const r=await get('/linea-jurisprudencial?tema='+encodeURIComponent(t)+(a?'&area='+a:''));
    showResult('l-result',r.respuesta);showFuentes('l-fuentes',r.fichas_usadas);}
  catch(e){showResult('l-result','❌ '+e.message);}spin('l-spinner',false);}
async function buscarFichas(){const q=document.getElementById('b-query').value.trim();if(!q)return;
  spin('b-spinner',true);try{const d=await get('/buscar?q='+encodeURIComponent(q)+'&top_k=10');
    document.getElementById('b-result').innerHTML=d.resultados.map(r=>`<div class="card" style="margin-bottom:10px;padding:14px">
      <div style="display:flex;justify-content:space-between"><strong style="color:#002347">${r.id}</strong>
      <span style="font-size:12px;color:#888">${r.anio||''} · ${r.sala||''}</span></div>
      <div>${(r.areas||[]).map(a=>`<span class="badge">${a}</span>`).join('')}</div>
      <div style="font-size:13px;margin-top:6px">${r.preview}…</div></div>`).join('');}
  catch(e){document.getElementById('b-result').innerHTML='<p style="color:red">❌ '+e.message+'</p>';}spin('b-spinner',false);}
window.onload=async()=>{try{const s=await get('/estadisticas');
  document.getElementById('stats-bar').innerHTML=
    `<span class="stat">📚 <span>${s.total_fichas}</span> fichas</span>`+
    `<span class="stat">🧠 FAISS: <span>${s.faiss_listo?'on':'off'}</span></span>`;}catch(e){}};
</script></body></html>"""


# ── Entrada directa ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
