"""
wa_brain.py — Orquestador IA para conversaciones de WhatsApp.

Punto de entrada: procesar_mensaje_entrante(conv, msg_id, text, kind)

En UN solo llamado a Gemini hace:
  - clasificación de intención
  - extracción de datos del cliente
  - generación de respuesta (si modo='ia')
  - decisión de escalación a humano
  - sugerencia de transición de estado

Sin GEMINI_API_KEY o circuito de emergencia activo: fallback determinístico
(reglas + plantillas) para no romper la conversación.
"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Optional

try:
    from app import db as db_mod
    from app import wa_mode
except ImportError:
    import db as db_mod  # type: ignore
    import wa_mode       # type: ignore


INTENCIONES = {
    "SALUDO", "PREGUNTA_JURIDICA", "AGENDAR", "CANCELAR",
    "ENVIO_DOC", "ACTUALIZAR_DATOS", "CONFIRMAR", "NEGAR",
    "QUEJA", "FUERA_DE_TEMA", "INSEGURO",
}

VERTICALES = {"tutelas", "accidentes", "comparendos", "laboral"}

# Transiciones permitidas (origen → destinos válidos)
TRANSICIONES_OK = {
    "lead_nuevo":      {"lead_calificado", "archivado_no_califica", "lead_agendado"},
    "lead_calificado": {"lead_agendado", "cliente", "archivado_no_califica", "perdido"},
    "lead_agendado":   {"cliente", "cancelado", "perdido"},
    "cliente":         {"cliente_activo", "ganado", "perdido"},
    "cliente_activo":  {"ganado", "perdido"},
}


# ─── Cliente Gemini compartido ───────────────────────────────────────────────

_genai_client = None
_genai_types = None


def _get_genai():
    """Lazy init del cliente Gemini. Devuelve None si no hay API key."""
    global _genai_client, _genai_types
    if _genai_client is not None:
        return _genai_client
    api_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not api_key:
        return None
    try:
        from google import genai
        from google.genai import types as gt
        _genai_client = genai.Client(api_key=api_key)
        _genai_types = gt
        return _genai_client
    except Exception as e:
        print(f"[wa_brain] error iniciando Gemini: {e}")
        return None


# ─── Prompt principal (combina clasificación + extracción + respuesta) ──────

PROMPT_TEMPLATE = """\
Eres el asistente de WhatsApp del despacho jurídico colombiano "Galeano Herrera | Abogados".
Operas en Colombia, español neutro, tono cercano pero profesional. Respondes corto (máx 80 palabras).

MODO ACTUAL: {modo}
- Si modo='ia': escribes una respuesta breve y útil al cliente.
- Si modo='humano': NO escribes respuesta (campo respuesta=null) — un abogado humano contestará.

CONTEXTO DE LA CONVERSACIÓN:
- Estado del lead: {estado}
- Vertical sospechado (si aplica): {vertical}
- Datos ya capturados: {datos_capturados_json}

VERTICALES DISPONIBLES (asigna el más cercano si lo identificas):
- tutelas       (salud, pensión, derecho de petición, mínimo vital)
- accidentes    (SOAT, accidente de tránsito, indemnización)
- comparendos   (fotomultas, multas tránsito, cobro coactivo)
- laboral       (despido, fuero, contrato realidad, acoso laboral)

HISTORIAL RECIENTE (más reciente abajo):
{history_block}

ÚLTIMO MENSAJE DEL CLIENTE:
"{text}"

INSTRUCCIONES:
1. Clasifica intención del último mensaje EXACTAMENTE en una de:
   SALUDO | PREGUNTA_JURIDICA | AGENDAR | CANCELAR | ENVIO_DOC | ACTUALIZAR_DATOS |
   CONFIRMAR | NEGAR | QUEJA | FUERA_DE_TEMA | INSEGURO

2. Extrae datos NUEVOS (deja vacío lo que ya esté capturado o no aparezca):
   nombre, cedula, ciudad, telefono, email, accionado, vertical, descripcion_caso

3. Decide si el lead califica para uno de los 4 verticales (true) o si es FUERA_DE_TEMA (false).

4. Si modo='ia':
   - Si faltan datos básicos (nombre + descripción del problema), pregunta UNO solo, amablemente.
   - Si ya están: confirma vertical y propone agendar cita gratuita con un abogado (15-20 min).
   - NUNCA inventes sentencias, números de fallo, ni cifras.
   - NUNCA prometas resultado ("vas a ganar", "te van a dar X").
   - NUNCA pidas datos sensibles innecesarios (clave, banco).
   - Cierra con frase corta + invitación a continuar.

5. Si la intención es QUEJA grave, FUERA_DE_TEMA persistente, o INSEGURO → respuesta=null y escalar=true.

6. Sugiere transición de estado SOLO si tienes alta confianza:
   - lead_nuevo → lead_calificado (cuando ya tienes nombre + descripción + vertical)
   - lead_calificado → lead_agendado (cuando confirmó cita)
   - cualquier → archivado_no_califica (si confirmaste FUERA_DE_TEMA)

RESPONDE EXCLUSIVAMENTE CON UN JSON VÁLIDO (sin texto adicional) con esta forma:
{{
  "intencion": "...",
  "datos": {{ "nombre": "...", "cedula": "...", "ciudad": "...", "vertical": "...", "descripcion_caso": "..." }},
  "respuesta": "..." | null,
  "escalar": true | false,
  "razon_escalada": "..." | null,
  "transicion_estado": "lead_calificado" | "lead_agendado" | "archivado_no_califica" | null,
  "califica": true | false
}}
"""


def _format_history(msgs: list[dict]) -> str:
    if not msgs:
        return "(conversación nueva)"
    lines = []
    for m in msgs[-12:]:  # cap a 12 últimos
        who = "Cliente" if m.get("direction") == "in" else "Asistente"
        text = (m.get("text") or "").strip()
        if not text and m.get("kind") in ("image", "document", "audio", "video"):
            text = f"[{m['kind']}]"
        lines.append(f"{who}: {text[:240]}")
    return "\n".join(lines)


# ─── Llamada a Gemini con fallback a modelos alternos ────────────────────────

MODELOS = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
BACKOFFS = [0, 3, 8, 15]


def _llamar_gemini_json(prompt: str, max_tokens: int = 800) -> Optional[dict]:
    client = _get_genai()
    if client is None:
        return None
    last_err = None
    for intento in range(len(MODELOS) * 2):
        modelo = MODELOS[intento % len(MODELOS)]
        if BACKOFFS[min(intento, len(BACKOFFS) - 1)]:
            time.sleep(BACKOFFS[min(intento, len(BACKOFFS) - 1)])
        try:
            r = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=_genai_types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json",
                ),
            )
            texto = (r.text or "").strip()
            if not texto:
                continue
            return json.loads(texto)
        except Exception as e:
            last_err = e
            msg = str(e).lower()
            if any(t in msg for t in ("429", "quota", "exhausted", "rate")):
                continue
            if "404" in msg or "not_found" in msg:
                continue
            print(f"[wa_brain] gemini error: {e}")
            return None
    print(f"[wa_brain] gemini agotó reintentos: {last_err}")
    return None


# ─── Fallback determinístico (sin IA) ────────────────────────────────────────

_KW_AGENDAR = re.compile(r"\b(cit[ao]|agend|reservar|hora|llamada|consult)\b", re.I)
_KW_CANCELAR = re.compile(r"\b(cancel|aplazar|posponer|reprogram)\b", re.I)
_KW_QUEJA = re.compile(r"\b(reclamo|queja|denuncia|mal trato|incompetent|estafa)\b", re.I)
_KW_TUTELAS = re.compile(r"\b(eps|salud|cirug|medic|pensión|colpensiones|petición)\b", re.I)
_KW_ACCID = re.compile(r"\b(accident|soat|choque|tránsito|aseguradora|moto.*choque)\b", re.I)
_KW_COMP = re.compile(r"\b(comparend|fotomulta|simit|tránsito.*multa|multa)\b", re.I)
_KW_LAB = re.compile(r"\b(despid|fuero|empleado|trabajo|salar|liquid|acoso laboral)\b", re.I)


def _detectar_vertical_keyword(text: str) -> Optional[str]:
    t = (text or "").lower()
    if _KW_LAB.search(t):
        return "laboral"
    if _KW_COMP.search(t):
        return "comparendos"
    if _KW_ACCID.search(t):
        return "accidentes"
    if _KW_TUTELAS.search(t):
        return "tutelas"
    return None


def _fallback_sin_ia(conv: dict, text: str, modo: str) -> dict:
    """Respuesta determinística cuando no hay IA disponible."""
    txt = (text or "").strip()
    intencion = "PREGUNTA_JURIDICA"
    if not txt:
        intencion = "ENVIO_DOC"
    elif _KW_AGENDAR.search(txt):
        intencion = "AGENDAR"
    elif _KW_CANCELAR.search(txt):
        intencion = "CANCELAR"
    elif _KW_QUEJA.search(txt):
        intencion = "QUEJA"
    elif len(txt) < 8 and re.search(r"\b(hola|buenas|buenos|hey|hi)\b", txt.lower()):
        intencion = "SALUDO"

    vertical = _detectar_vertical_keyword(txt)

    cfg = db_mod.wa_config_get_all()
    if modo == "humano":
        respuesta = None
    else:
        if intencion == "SALUDO":
            respuesta = cfg.get("welcome_message") or "Hola, ¿en qué te ayudamos?"
        elif intencion == "QUEJA":
            respuesta = None  # escalar
        elif intencion == "AGENDAR":
            respuesta = "Listo, vamos a agendar. ¿Para qué día y hora te queda mejor?"
        elif intencion == "CANCELAR":
            respuesta = "Entendido, cancelo. Si quieres reagendar, escríbeme cuándo te queda bien."
        elif vertical:
            respuesta = (
                f"Gracias. Tu caso parece de {vertical}. "
                "Cuéntame tu nombre completo y describe brevemente lo que pasó "
                "para revisar si puedo ayudarte."
            )
        else:
            respuesta = (
                "Recibí tu mensaje. Cuéntame brevemente qué te pasa para "
                "ver si puedo ayudarte (salud, accidente, comparendo, laboral)."
            )

    return {
        "intencion": intencion,
        "datos": {"vertical": vertical} if vertical else {},
        "respuesta": respuesta,
        "escalar": intencion == "QUEJA",
        "razon_escalada": "queja_keywords" if intencion == "QUEJA" else None,
        "transicion_estado": None,
        "califica": vertical is not None,
        "_fallback": True,
    }


# ─── Punto de entrada principal ──────────────────────────────────────────────

def procesar_mensaje_entrante(
    conv: dict,
    msg_id: int,
    text: str,
    kind: str = "text",
) -> dict:
    """Procesa un mensaje entrante y devuelve la decisión completa.

    Returns dict con keys:
      - intencion (str)
      - datos_extraidos (dict)
      - respuesta (str | None)        # mensaje a enviar de vuelta, None si silencio
      - modo_aplicado ('ia' | 'humano')
      - escalar (bool)
      - razon_escalada (str | None)
      - transicion_estado (str | None)
      - usado_fallback (bool)
    """
    cfg = db_mod.wa_config_get_all()
    modo = wa_mode.decidir_modo(conv, cfg=cfg)

    # Si la IA está desactivada por bandera o no hay key, fallback
    ia_off = cfg.get("ai_disabled", "0") == "1" or not (os.environ.get("GEMINI_API_KEY") or "").strip()

    # Mensajes no-texto (foto, doc, audio): sin IA texto-a-texto, marcar y escalar/aceptar
    if kind in ("image", "document", "audio", "video", "sticker", "location"):
        respuesta = (
            "Recibí tu archivo. Lo guardé en tu expediente. ¿Quieres añadir alguna nota?"
            if modo == "ia" else None
        )
        return {
            "intencion": "ENVIO_DOC",
            "datos_extraidos": {},
            "respuesta": respuesta,
            "modo_aplicado": modo,
            "escalar": False,
            "razon_escalada": None,
            "transicion_estado": None,
            "usado_fallback": True,
        }

    history = db_mod.wa_msg_history(conv["id"], limit=14)
    # excluir el último (es el actual que ya quedó persistido)
    history_block = _format_history(history[:-1] if history else [])

    if ia_off:
        out = _fallback_sin_ia(conv, text, modo)
        return {
            "intencion": out["intencion"],
            "datos_extraidos": out["datos"],
            "respuesta": out["respuesta"],
            "modo_aplicado": modo,
            "escalar": out["escalar"],
            "razon_escalada": out["razon_escalada"],
            "transicion_estado": out["transicion_estado"],
            "usado_fallback": True,
        }

    datos_actuales = conv.get("datos_capturados") or {}
    prompt = PROMPT_TEMPLATE.format(
        modo=modo,
        estado=conv.get("estado", "lead_nuevo"),
        vertical=datos_actuales.get("vertical", "(desconocido)"),
        datos_capturados_json=json.dumps(datos_actuales, ensure_ascii=False),
        history_block=history_block,
        text=(text or "")[:1000],
    )

    out = _llamar_gemini_json(prompt, max_tokens=800)
    if not out:
        # Fallback si Gemini falló
        fb = _fallback_sin_ia(conv, text, modo)
        return {
            "intencion": fb["intencion"],
            "datos_extraidos": fb["datos"],
            "respuesta": fb["respuesta"],
            "modo_aplicado": modo,
            "escalar": fb["escalar"],
            "razon_escalada": fb["razon_escalada"] or "gemini_fallo",
            "transicion_estado": fb["transicion_estado"],
            "usado_fallback": True,
        }

    # Sanitizar salida de Gemini
    intencion = (out.get("intencion") or "INSEGURO").upper()
    if intencion not in INTENCIONES:
        intencion = "INSEGURO"

    datos = out.get("datos") or {}
    if not isinstance(datos, dict):
        datos = {}
    # filtrar keys vacíos / inválidos
    datos = {k: v for k, v in datos.items() if v not in (None, "", "null") and v != "..." and isinstance(v, (str, int))}
    if datos.get("vertical") and datos["vertical"].lower() not in VERTICALES:
        datos.pop("vertical", None)

    transicion = out.get("transicion_estado")
    if transicion:
        origen = conv.get("estado", "lead_nuevo")
        if transicion not in TRANSICIONES_OK.get(origen, set()):
            transicion = None

    respuesta = out.get("respuesta")
    if respuesta and not isinstance(respuesta, str):
        respuesta = None
    if respuesta:
        respuesta = respuesta.strip()[:1200]
    if modo == "humano":
        respuesta = None  # forzar silencio si modo humano

    return {
        "intencion": intencion,
        "datos_extraidos": datos,
        "respuesta": respuesta,
        "modo_aplicado": modo,
        "escalar": bool(out.get("escalar")),
        "razon_escalada": out.get("razon_escalada"),
        "transicion_estado": transicion,
        "usado_fallback": False,
    }
