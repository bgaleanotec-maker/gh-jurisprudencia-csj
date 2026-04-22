#!/usr/bin/env python3
"""
============================================================
APP JURISPRUDENCIA — GALEANO HERRERA | ABOGADOS  (v2)
============================================================
FastAPI con motor RAG híbrido (BM25 + dense + RRF + MMR + LLM rerank).

Endpoints:
  GET  /                 → Interfaz web
  GET  /salud            → Health check
  GET  /estadisticas     → Stats del índice
  POST /config           → Guardar API key (solo admin local)
  GET  /indexar          → Genera embeddings (consume API)
  POST /consultar        → Análisis jurisprudencial libre
  POST /analizar-caso    → Protocolo Galeano Herrera
  POST /generar-tutela   → Borrador de tutela listo
  GET  /linea-jurisprudencial?tema=...
  GET  /buscar?q=...     → Búsqueda híbrida con filtros
============================================================
"""

from __future__ import annotations

import os
import sys
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional

# Permitir importar scripts/rag_motor.py
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.responses import HTMLResponse
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

# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Jurisprudencia CSJ — Galeano Herrera | Abogados",
    description="Motor RAG híbrido de líneas jurisprudenciales de tutelas (CSJ 2018–2025).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"],
)

# ── Auth básica opcional (si APP_USER + APP_PASS) ─────────────────────────────

_security = HTTPBasic(auto_error=False)
_USER = os.environ.get("APP_USER")
_PASS = os.environ.get("APP_PASS")


def _check_auth(creds: Optional[HTTPBasicCredentials] = Depends(_security)):
    if not _USER or not _PASS:
        return  # auth deshabilitada
    if creds is None or not (
        secrets.compare_digest(creds.username, _USER)
        and secrets.compare_digest(creds.password, _PASS)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )


# ── Motor singleton ───────────────────────────────────────────────────────────

_motor: Optional["MotorRAG"] = None
_motor_lite: Optional["MotorRAG"] = None


def get_motor() -> "MotorRAG":
    global _motor
    if _motor is None:
        api_key = obtener_api_key()
        if not api_key:
            raise HTTPException(
                503, "API key de Gemini no configurada. Definir GEMINI_API_KEY.")
        _motor = MotorRAG(api_key=api_key)
    return _motor


def get_motor_lite() -> "MotorRAG":
    global _motor_lite
    if _motor_lite is None:
        _motor_lite = MotorRAG(solo_busqueda=True)
    return _motor_lite


# ── Modelos ────────────────────────────────────────────────────────────────────

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


class ConfigRequest(BaseModel):
    gemini_api_key: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root(_=Depends(_check_auth)):
    return _html_ui()


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
        "version"     : app.version,
    }


@app.post("/config")
async def configurar(req: ConfigRequest, _=Depends(_check_auth)):
    """Guarda API key en config.json (solo para uso local; en Render usar env)."""
    global _motor
    guardar_config({"gemini_api_key": req.gemini_api_key})
    _motor = None
    return {"ok": True}


@app.get("/indexar")
async def indexar(forzar: bool = False, _=Depends(_check_auth)):
    api_key = obtener_api_key()
    if not api_key:
        raise HTTPException(503, "API key no configurada.")
    motor = MotorRAG(api_key=api_key)
    n = motor.indexar(forzar=forzar)
    global _motor
    _motor = motor
    return {"ok": True, "fichas_indexadas": n, "faiss_listo": motor._listo}


@app.post("/consultar")
async def consultar(req: ConsultaRequest, _=Depends(_check_auth)):
    motor = get_motor()
    res = motor.consultar(
        req.pregunta, filtro_area=req.area, filtro_anio=req.anio,
        filtro_sala=req.sala, modo="respuesta", rerank=req.rerank, top_k=req.top_k,
    )
    if "error" in res: raise HTTPException(500, res["error"])
    return res


@app.post("/analizar-caso")
async def analizar_caso(req: CasoRequest, _=Depends(_check_auth)):
    motor = get_motor()
    q = req.descripcion if not req.nombre_cliente else f"Cliente: {req.nombre_cliente}. {req.descripcion}"
    res = motor.consultar(q, filtro_area=req.area, modo="caso")
    if "error" in res: raise HTTPException(500, res["error"])
    return res


@app.post("/generar-tutela")
async def generar_tutela(req: TutelaRequest, _=Depends(_check_auth)):
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


@app.get("/linea-jurisprudencial")
async def linea(tema: str = Query(..., min_length=3),
                area: Optional[str] = None, _=Depends(_check_auth)):
    motor = get_motor()
    res = motor.consultar(tema, filtro_area=area, modo="linea")
    if "error" in res: raise HTTPException(500, res["error"])
    return res


@app.get("/buscar")
async def buscar(q: str = Query(..., min_length=2),
                 area: Optional[str] = None, anio: Optional[int] = None,
                 sala: Optional[str] = None, top_k: int = Query(10, le=25),
                 _=Depends(_check_auth)):
    try:
        motor = get_motor()
    except HTTPException:
        motor = get_motor_lite()
    fichas = motor.buscar(q, k=top_k, filtro_area=area, filtro_anio=anio, filtro_sala=sala)
    return {
        "query": q, "total": len(fichas),
        "semantico": motor._listo, "lexico": motor.bm25 is not None,
        "resultados": [
            {"id": f["id"], "sala": f.get("sala"), "anio": f.get("anio"),
             "areas": f.get("areas", []),
             "temas": (f.get("temas") or [])[:3],
             "score": f.get("score", 0),
             "preview": (f.get("texto_busqueda","") or "")[:240]} for f in fichas
        ],
    }


@app.get("/estadisticas")
async def estadisticas(_=Depends(_check_auth)):
    return get_motor_lite().estadisticas()


# ── HTML (UI) ─────────────────────────────────────────────────────────────────

def _html_ui() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Galeano Herrera | Jurisprudencia CSJ</title>
<style>
  :root {--azul:#002347;--oro:#C5A059;--gris:#f4f6f9;--texto:#1a2332;}
  * {box-sizing:border-box;margin:0;padding:0;}
  body {font-family:'Segoe UI',sans-serif;background:var(--gris);color:var(--texto);}
  header {background:var(--azul);color:#fff;padding:16px 32px;display:flex;align-items:center;
          gap:16px;border-bottom:3px solid var(--oro);}
  .logo {font-size:28px;font-weight:800;letter-spacing:-1px;}
  .logo span {color:var(--oro);}
  .subtitle {font-size:12px;opacity:.75;letter-spacing:2px;text-transform:uppercase;}
  .container {max-width:1100px;margin:0 auto;padding:24px 16px;}
  .tabs {display:flex;gap:4px;margin-bottom:24px;border-bottom:2px solid var(--azul);
         flex-wrap:wrap;}
  .tab {padding:10px 18px;cursor:pointer;border-radius:6px 6px 0 0;border:2px solid transparent;
        border-bottom:none;font-weight:600;font-size:13px;color:var(--azul);background:#fff;}
  .tab:hover {background:#e8ecf3;} .tab.active {background:var(--azul);color:#fff;}
  .panel {display:none;} .panel.active {display:block;}
  .card {background:#fff;border-radius:10px;padding:24px;box-shadow:0 2px 12px rgba(0,35,71,.08);
         margin-bottom:20px;}
  label {display:block;font-size:12px;font-weight:700;color:var(--azul);text-transform:uppercase;
         letter-spacing:.5px;margin-bottom:6px;}
  input[type=text],input[type=number],textarea,select {
    width:100%;padding:10px 14px;border:2px solid #dce3ef;border-radius:6px;
    font-size:14px;color:var(--texto);font-family:inherit;}
  input:focus,textarea:focus,select:focus {outline:none;border-color:var(--azul);}
  textarea {resize:vertical;min-height:90px;}
  .row {display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .row3 {display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}
  @media (max-width:600px) {.row,.row3 {grid-template-columns:1fr;}}
  .btn {background:var(--azul);color:#fff;border:none;padding:12px 28px;border-radius:6px;
        font-size:14px;font-weight:700;cursor:pointer;letter-spacing:.5px;}
  .btn:hover {background:#003d7a;} .btn.gold {background:var(--oro);}
  .btn.gold:hover {background:#a88440;} .btn:disabled {background:#9aa;cursor:not-allowed;}
  .result {background:#f0f4fa;border-left:4px solid var(--azul);padding:16px;border-radius:0 6px 6px 0;
           white-space:pre-wrap;font-size:14px;line-height:1.65;max-height:600px;overflow-y:auto;
           display:none;}
  .result.visible {display:block;}
  .fuentes {font-size:12px;color:#666;margin-top:10px;padding:8px 12px;background:#fff;
            border-radius:4px;border:1px solid #dce3ef;display:none;}
  .fuentes b {color:var(--azul);}
  .spinner {display:none;margin:16px 0;color:var(--azul);font-size:14px;}
  .spinner.visible {display:block;}
  .badge {display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;
          margin:2px;background:#e3f0ff;color:#004a9f;}
  h3 {font-size:16px;color:var(--azul);margin-bottom:16px;}
  .form-group {margin-bottom:16px;}
  .alert {padding:10px 14px;border-radius:6px;font-size:13px;margin-bottom:16px;}
  .alert-warn {background:#fff8e1;border:1px solid #ffc107;color:#7a5200;}
  .alert-ok {background:#e8f5e9;border:1px solid #4caf50;color:#1b5e20;}
  .stat {display:inline-block;background:#fff;border:1px solid #dce3ef;border-radius:6px;
         padding:8px 14px;margin:4px;font-size:13px;color:var(--azul);font-weight:700;}
  .stat span {color:var(--oro);}
</style>
</head>
<body>

<header>
  <div>
    <div class="logo">Galeano <span>Herrera</span></div>
    <div class="subtitle">Motor RAG Híbrido · Jurisprudencia CSJ</div>
  </div>
</header>

<div class="container">
  <div id="status-bar" class="alert alert-warn" style="display:none"></div>
  <div id="stats-bar"></div>

  <div class="tabs">
    <div class="tab active" onclick="showTab('consultar')">🔍 Consultar</div>
    <div class="tab" onclick="showTab('caso')">📋 Analizar Caso</div>
    <div class="tab" onclick="showTab('tutela')">⚖️ Generar Tutela</div>
    <div class="tab" onclick="showTab('linea')">📈 Línea Jurisprudencial</div>
    <div class="tab" onclick="showTab('buscar')">🗂️ Buscar Fichas</div>
  </div>

  <div id="panel-consultar" class="panel active">
    <div class="card">
      <h3>Consulta Jurisprudencial Libre</h3>
      <div class="form-group">
        <label>Pregunta o situación del cliente</label>
        <textarea id="q-pregunta" placeholder="Ej: EPS Sanitas niega cirugía de rodilla prescrita por ortopedista hace 3 meses..."></textarea>
      </div>
      <div class="row3">
        <div><label>Área</label><select id="q-area">
          <option value="">Todas</option>
          <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
          <option value="laboral">Laboral</option><option value="accidentes">Accidentes</option>
          <option value="insolvencia">Insolvencia</option>
          <option value="derechos_fundamentales">Derechos Fundamentales</option>
        </select></div>
        <div><label>Sala</label><select id="q-sala">
          <option value="">Todas</option>
          <option value="CIVIL">Civil</option><option value="LABORAL">Laboral</option>
          <option value="PENAL">Penal</option><option value="PLENA">Plena</option>
          <option value="INSOLVENCIA">Insolvencia</option>
        </select></div>
        <div><label>Año</label>
          <input type="number" id="q-anio" min="2014" max="2030" placeholder="ej. 2024"></div>
      </div>
      <br>
      <button class="btn" onclick="consultar()">Consultar Jurisprudencia</button>
      <div class="spinner" id="q-spinner">⏳ Recuperando precedentes y generando análisis…</div>
      <div class="result" id="q-result"></div>
      <div class="fuentes" id="q-fuentes"></div>
    </div>
  </div>

  <div id="panel-caso" class="panel">
    <div class="card">
      <h3>Protocolo Galeano Herrera</h3>
      <div class="row">
        <div class="form-group"><label>Cliente</label>
          <input type="text" id="caso-nombre" placeholder="María García López"></div>
        <div class="form-group"><label>Área</label>
          <select id="caso-area"><option value="">Auto-detectar</option>
            <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
            <option value="laboral">Laboral</option><option value="accidentes">Accidentes</option>
            <option value="insolvencia">Insolvencia</option></select></div>
      </div>
      <div class="form-group"><label>Descripción</label>
        <textarea id="caso-desc" style="min-height:130px"
          placeholder="Qué pasó, accionado, fechas, documentos disponibles…"></textarea></div>
      <button class="btn" onclick="analizarCaso()">Analizar Caso</button>
      <div class="spinner" id="caso-spinner">⏳ Aplicando protocolo…</div>
      <div class="result" id="caso-result"></div>
      <div class="fuentes" id="caso-fuentes"></div>
    </div>
  </div>

  <div id="panel-tutela" class="panel">
    <div class="card">
      <h3>Generador de Tutelas</h3>
      <div class="row">
        <div class="form-group"><label>Nombre</label>
          <input type="text" id="t-nombre" placeholder="María García López"></div>
        <div class="form-group"><label>Cédula</label>
          <input type="text" id="t-cedula" placeholder="1.234.567.890"></div>
      </div>
      <div class="row">
        <div class="form-group"><label>Accionado</label>
          <input type="text" id="t-accionado" placeholder="EPS Sanitas S.A.S."></div>
        <div class="form-group"><label>Derecho vulnerado</label>
          <input type="text" id="t-derecho" placeholder="Salud y vida digna"></div>
      </div>
      <div class="form-group"><label>Hechos</label>
        <textarea id="t-hechos" style="min-height:130px"
          placeholder="1. Soy paciente con diagnóstico…"></textarea></div>
      <div class="form-group"><label>Área</label>
        <select id="t-area">
          <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
          <option value="laboral">Laboral</option>
          <option value="derechos_fundamentales">Derechos Fundamentales</option></select></div>
      <button class="btn gold" onclick="generarTutela()">⚖️ Generar Borrador</button>
      <div class="spinner" id="t-spinner">⏳ Generando con precedentes reales…</div>
      <div class="result" id="t-result"></div>
      <div class="fuentes" id="t-fuentes"></div>
    </div>
  </div>

  <div id="panel-linea" class="panel">
    <div class="card">
      <h3>Línea Jurisprudencial</h3>
      <div class="form-group"><label>Tema</label>
        <input type="text" id="l-tema" placeholder="Ej: medicamento no POS, despido embarazada…"></div>
      <div class="row">
        <div><label>Área</label><select id="l-area">
          <option value="">Todas</option>
          <option value="salud">Salud</option><option value="pensiones">Pensiones</option>
          <option value="laboral">Laboral</option><option value="accidentes">Accidentes</option>
          <option value="insolvencia">Insolvencia</option></select></div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn" onclick="explorarLinea()">Explorar</button></div>
      </div>
      <div class="spinner" id="l-spinner">⏳ Analizando línea…</div>
      <div class="result" id="l-result"></div>
      <div class="fuentes" id="l-fuentes"></div>
    </div>
  </div>

  <div id="panel-buscar" class="panel">
    <div class="card">
      <h3>Búsqueda híbrida (semántica + léxica)</h3>
      <div class="row">
        <div class="form-group"><label>Búsqueda</label>
          <input type="text" id="b-query" placeholder="Ej: fuero de maternidad despido"></div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn" onclick="buscarFichas()">Buscar</button></div>
      </div>
      <div class="spinner" id="b-spinner">⏳ Buscando…</div>
      <div id="b-result"></div>
    </div>
  </div>
</div>

<script>
const API='';
function showTab(n){document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelector(`[onclick="showTab('${n}')"]`).classList.add('active');
  document.getElementById('panel-'+n).classList.add('active');}
function spin(id,on){document.getElementById(id).className='spinner'+(on?' visible':'');}
function showResult(id,t){const e=document.getElementById(id);e.textContent=t;e.className='result visible';}
function showFuentes(id,fichas){const e=document.getElementById(id);
  if(!fichas||!fichas.length){e.style.display='none';return;}
  e.style.display='block';
  e.innerHTML='<b>Fichas usadas:</b> '+fichas.map(f=>
    `<span class="badge" title="Sala ${f.sala||'?'} · ${f.anio||'?'}">${f.id}</span>`).join(' ');}
async function post(url,data){const r=await fetch(API+url,{method:'POST',
  headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  if(!r.ok){const e=await r.json();throw new Error(e.detail||'Error');}return r.json();}
async function get(url){const r=await fetch(API+url);
  if(!r.ok){const e=await r.json();throw new Error(e.detail||'Error');}return r.json();}

async function consultar(){
  const p=document.getElementById('q-pregunta').value.trim();
  if(!p)return alert('Escribe una consulta');
  spin('q-spinner',true);
  try{const d=await post('/consultar',{
    pregunta:p,
    area:document.getElementById('q-area').value||null,
    sala:document.getElementById('q-sala').value||null,
    anio:parseInt(document.getElementById('q-anio').value)||null,
  });showResult('q-result',d.respuesta);showFuentes('q-fuentes',d.fichas_usadas);}
  catch(e){showResult('q-result','❌ '+e.message);}
  spin('q-spinner',false);
}
async function analizarCaso(){
  const d=document.getElementById('caso-desc').value.trim();
  if(!d)return alert('Describe el caso');
  spin('caso-spinner',true);
  try{const r=await post('/analizar-caso',{descripcion:d,
    nombre_cliente:document.getElementById('caso-nombre').value,
    area:document.getElementById('caso-area').value||null});
    showResult('caso-result',r.respuesta);showFuentes('caso-fuentes',r.fichas_usadas);}
  catch(e){showResult('caso-result','❌ '+e.message);}
  spin('caso-spinner',false);
}
async function generarTutela(){
  const n=document.getElementById('t-nombre').value.trim();
  const h=document.getElementById('t-hechos').value.trim();
  if(!n||!h)return alert('Completa nombre y hechos');
  spin('t-spinner',true);
  try{const r=await post('/generar-tutela',{nombre:n,
    cedula:document.getElementById('t-cedula').value,
    accionado:document.getElementById('t-accionado').value,
    hechos:h,derecho_vulnerado:document.getElementById('t-derecho').value,
    area:document.getElementById('t-area').value});
    showResult('t-result',r.respuesta);showFuentes('t-fuentes',r.fichas_usadas);}
  catch(e){showResult('t-result','❌ '+e.message);}
  spin('t-spinner',false);
}
async function explorarLinea(){
  const t=document.getElementById('l-tema').value.trim();
  if(!t)return alert('Escribe un tema');
  spin('l-spinner',true);
  try{const a=document.getElementById('l-area').value;
    const r=await get('/linea-jurisprudencial?tema='+encodeURIComponent(t)+(a?'&area='+a:''));
    showResult('l-result',r.respuesta);showFuentes('l-fuentes',r.fichas_usadas);}
  catch(e){showResult('l-result','❌ '+e.message);}
  spin('l-spinner',false);
}
async function buscarFichas(){
  const q=document.getElementById('b-query').value.trim();
  if(!q)return alert('Escribe una búsqueda');
  spin('b-spinner',true);
  try{const d=await get('/buscar?q='+encodeURIComponent(q)+'&top_k=10');
    document.getElementById('b-result').innerHTML=d.resultados.map(r=>`
      <div class="card" style="margin-bottom:10px;padding:14px">
        <div style="display:flex;justify-content:space-between">
          <strong style="color:var(--azul)">${r.id}</strong>
          <span style="font-size:12px;color:#888">${r.anio||''} · Sala ${r.sala||''}</span></div>
        <div style="margin:6px 0">${(r.areas||[]).map(a=>`<span class="badge">${a}</span>`).join('')}</div>
        <div style="font-size:13px;color:#444;margin-top:6px">${r.preview}…</div>
      </div>`).join('');}
  catch(e){document.getElementById('b-result').innerHTML='<p style="color:red">❌ '+e.message+'</p>';}
  spin('b-spinner',false);
}

window.onload=async()=>{
  try{const s=await get('/salud');
    if(!s.api_key){const sb=document.getElementById('status-bar');
      sb.style.display='block';
      sb.textContent='⚠ Configura GEMINI_API_KEY para activar el modo semántico.';}
    if(s.fichas){const stats=await get('/estadisticas');
      document.getElementById('stats-bar').innerHTML=
        `<span class="stat">📚 <span>${stats.total_fichas}</span> fichas</span>`+
        `<span class="stat">🧠 FAISS: <span>${stats.faiss_listo?'on':'off'}</span></span>`+
        `<span class="stat">🔤 BM25: <span>${stats.bm25_listo?'on':'off'}</span></span>`;}}
  catch(e){}
};
document.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&e.ctrlKey){const a=document.querySelector('.panel.active');
    if(a.id==='panel-consultar')consultar();
    else if(a.id==='panel-linea')explorarLinea();
    else if(a.id==='panel-buscar')buscarFichas();}});
</script>
</body>
</html>"""


# ── Entrada directa ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("=" * 60)
    print("  APP JURISPRUDENCIA — GALEANO HERRERA | ABOGADOS")
    print(f"  http://localhost:{port}")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
