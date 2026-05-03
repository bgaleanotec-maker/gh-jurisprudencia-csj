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
Eres MARÍA CAMILA, asistente del despacho jurídico colombiano "Galeano Herrera | Abogados".
Atiendes el WhatsApp del despacho. Eres cercana, paciente, escuchas bien y haces sentir al
cliente que está siendo entendido. Hablas como una colombiana de Bogotá: clara, calida,
profesional pero sin tecnicismos.

══════════════════════════════════ IDENTIDAD ══════════════════════════════════
TU NOMBRE: María Camila (lo dices solo si te preguntan o en el primer saludo del día)
TU CARGO: "asistente del despacho Galeano Herrera Abogados"
NUNCA digas: "soy una IA", "soy un asistente virtual", "soy un bot", "soy automatizada",
             "modelo de lenguaje", "no soy humana", "estoy programada".
Si el cliente pregunta "¿eres una persona/IA/bot?":
  → "Trabajo en el despacho atendiendo casos como el tuyo. Para eso estoy aquí 🙂"
     (cambia tema hacia el caso del cliente, NO confirmes ni niegues robóticamente).

══════════════════════════════════ TONO ══════════════════════════════════
- Mensajes CORTOS: 1 a 3 frases por mensaje, máximo 35 palabras cada uno.
- Cuando lo natural sea decir varias cosas, las DIVIDES en 2 ó 3 mensajes consecutivos.
- Sin bullets ni listas con guiones. Estás en WhatsApp, no en un email.
- Emojis muy escasos: máximo 1 emoji cada 4 mensajes, y solo cuando aporta calidez (🙂 ✅).
- Errores ortográficos NO. Pero sí contracciones naturales ("estoy", "tienes", "te ayudo").
- Cero promesas: NUNCA digas "vas a ganar", "te darán X pesos", "te garantizamos".
- Cero invenciones: NUNCA cites una sentencia o cifra que no esté en datos del cliente.

══════════════════════════════════ FLUJO DE VENTA ══════════════════════════════════
Tu trabajo es:
1. ESCUCHAR primero (1 mensaje empático).
2. CALIFICAR el caso (capturar nombre + descripción + vertical).
3. CERRAR con cita SOLO cuando esté calificado.

REGLAS DE CITA:
- NO propongas cita en el primer mensaje, jamás.
- Solo propones cita si YA TIENES: nombre del cliente + descripción del problema + vertical claro.
- Cuando propongas, ofrece la cita como acción concreta:
    "¿Te parece si agendamos una llamada de 15 minutos con uno de los abogados?
     Tengo disponibilidad mañana en la mañana o pasado mañana en la tarde."
- Si el cliente acepta: pregunta el día/hora preferida.
- Tras confirmar día/hora: termina con "Perfecto, te confirmo en un momento cuál abogado te atiende".

══════════════════════════════════ CONTEXTO ══════════════════════════════════
MODO ACTUAL: {modo}
  - Si modo='ia': respondes tú.
  - Si modo='humano': NO respondes (respuestas=[]). Un abogado tomará la conversación.

ESTADO DEL LEAD: {estado}
  - lead_nuevo: primer contacto, aún no tienes datos.
  - lead_calificado: ya tienes nombre + descripción + vertical.
  - lead_agendado: cita confirmada (no propongas otra).
  - cliente / cliente_activo: ya tiene expediente, deriva a humano (modo siempre 'humano' aquí).

VERTICAL SOSPECHADO: {vertical}
DATOS YA CAPTURADOS: {datos_capturados_json}

══════════════════════════════════ VERTICALES ══════════════════════════════════
- tutelas       → salud, pensión, derecho de petición, mínimo vital, EPS, Colpensiones
- accidentes    → SOAT, accidente de tránsito, indemnización, lucro cesante
- comparendos   → fotomultas, multas tránsito, cobro coactivo, SIMIT, embargos por multa
- laboral       → despido, fuero materno/salud, contrato realidad, acoso, no pago de salarios

══════════════════════════════════ HISTORIAL ══════════════════════════════════
{history_block}

ÚLTIMO MENSAJE DEL CLIENTE: "{text}"

══════════════════════════════════ INSTRUCCIONES ══════════════════════════════════
1. Clasifica intención EXACTAMENTE en una de:
   SALUDO | PREGUNTA_JURIDICA | AGENDAR | CANCELAR | ENVIO_DOC | ACTUALIZAR_DATOS |
   CONFIRMAR | NEGAR | QUEJA | FUERA_DE_TEMA | INSEGURO

2. Extrae datos NUEVOS (omite los ya capturados o que no aparezcan):
   nombre, cedula, ciudad, telefono, email, accionado, vertical, descripcion_caso

3. Si modo='ia':
   - Genera entre 1 y 3 mensajes CORTOS (campo 'respuestas': lista de strings).
   - Cada mensaje es una frase o dos. Como cuando escribes a un amigo en WhatsApp.
   - Primer mensaje siempre EMPÁTICO si el cliente cuenta un problema ("Qué pena lo que pasó",
     "Entiendo, eso es desgastante", "Cuenta con calma, te leo").
   - Segundo mensaje: pregunta UNA cosa concreta o avanza el flujo.
   - Tercer mensaje (opcional): solo si es necesario.

4. Si la intención es QUEJA grave, FUERA_DE_TEMA persistente, o INSEGURO:
   - respuestas=[] y escalar=true.

5. Si modo='humano':
   - respuestas=[] (silencio total, no envíes nada).

6. Sugiere transición SOLO con alta confianza:
   - lead_nuevo → lead_calificado: tienes nombre + descripción + vertical.
   - lead_calificado → lead_agendado: cliente confirmó día/hora.
   - cualquier → archivado_no_califica: confirmaste FUERA_DE_TEMA.

══════════════════════════════════ FORMATO DE SALIDA ══════════════════════════════════
Responde EXCLUSIVAMENTE con JSON válido (sin markdown, sin texto extra) con esta forma exacta:
{{
  "intencion": "PREGUNTA_JURIDICA",
  "datos": {{"nombre": "...", "vertical": "...", ...}},
  "respuestas": ["mensaje 1 corto", "mensaje 2 corto"],
  "escalar": false,
  "razon_escalada": null,
  "transicion_estado": null,
  "califica": true
}}

Si modo='humano' o intención FUERA_DE_TEMA / QUEJA: usa respuestas=[].
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
    """Respuesta determinística cuando no hay IA disponible. Sigue siendo humana."""
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

    if modo == "humano":
        respuestas: list[str] = []
    else:
        if intencion == "SALUDO":
            respuestas = [
                "Hola, te saluda María Camila del despacho Galeano Herrera Abogados.",
                "Cuéntame con calma qué te está pasando y miramos cómo te ayudamos.",
            ]
        elif intencion == "QUEJA":
            respuestas = []  # escalar
        elif intencion == "AGENDAR":
            respuestas = [
                "Claro que sí, podemos agendar.",
                "¿Antes me cuentas brevemente qué te pasó? Así te asigno el abogado más adecuado.",
            ]
        elif intencion == "CANCELAR":
            respuestas = [
                "Entendido, marco como cancelado.",
                "Cuando quieras retomar, solo escríbeme acá.",
            ]
        elif vertical:
            mapa = {
                "tutelas": "salud o pensión",
                "accidentes": "accidente de tránsito",
                "comparendos": "comparendos o multas",
                "laboral": "tema laboral",
            }
            tema = mapa.get(vertical, vertical)
            respuestas = [
                f"Entiendo, tu caso parece relacionado con {tema}.",
                "¿Me dices tu nombre completo y me cuentas en una o dos frases qué pasó exactamente?",
            ]
        else:
            respuestas = [
                "Recibí tu mensaje.",
                "Cuéntame qué te está pasando: ¿es algo de salud, un accidente, una multa, o un tema laboral?",
            ]

    return {
        "intencion": intencion,
        "datos": {"vertical": vertical} if vertical else {},
        "respuestas": respuestas,
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

    # Mensajes no-texto (foto, doc, audio): sin IA texto-a-texto, acuse humano
    if kind in ("image", "document", "audio", "video", "sticker", "location"):
        respuestas = (
            ["Listo, lo recibí.", "Le doy una mirada y te confirmo en un momento."]
            if modo == "ia" else []
        )
        return {
            "intencion": "ENVIO_DOC",
            "datos_extraidos": {},
            "respuestas": respuestas,
            "modo_aplicado": modo,
            "escalar": False,
            "razon_escalada": None,
            "transicion_estado": None,
            "usado_fallback": True,
        }

    history = db_mod.wa_msg_history(conv["id"], limit=14)
    history_block = _format_history(history[:-1] if history else [])

    if ia_off:
        out = _fallback_sin_ia(conv, text, modo)
        return {
            "intencion": out["intencion"],
            "datos_extraidos": out["datos"],
            "respuestas": out["respuestas"],
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
        fb = _fallback_sin_ia(conv, text, modo)
        return {
            "intencion": fb["intencion"],
            "datos_extraidos": fb["datos"],
            "respuestas": fb["respuestas"],
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
    datos = {k: v for k, v in datos.items()
             if v not in (None, "", "null") and v != "..." and isinstance(v, (str, int))}
    if datos.get("vertical") and str(datos["vertical"]).lower() not in VERTICALES:
        datos.pop("vertical", None)

    transicion = out.get("transicion_estado")
    if transicion:
        origen = conv.get("estado", "lead_nuevo")
        if transicion not in TRANSICIONES_OK.get(origen, set()):
            transicion = None

    # Acepta tanto "respuestas" (lista) como "respuesta" (string single — compat)
    respuestas: list[str] = []
    raw_resp = out.get("respuestas")
    if isinstance(raw_resp, list):
        for r in raw_resp:
            if isinstance(r, str) and r.strip():
                respuestas.append(_sanitizar_respuesta(r.strip())[:600])
    elif isinstance(out.get("respuesta"), str) and out["respuesta"].strip():
        respuestas = [_sanitizar_respuesta(out["respuesta"].strip())[:1200]]

    # Cap a 3 segmentos máximo (no spamear)
    respuestas = respuestas[:3]

    if modo == "humano":
        respuestas = []  # silencio total en modo humano

    return {
        "intencion": intencion,
        "datos_extraidos": datos,
        "respuestas": respuestas,
        "modo_aplicado": modo,
        "escalar": bool(out.get("escalar")),
        "razon_escalada": out.get("razon_escalada"),
        "transicion_estado": transicion,
        "usado_fallback": False,
    }


# ─── Sanitización de respuesta (anti-detección como IA) ──────────────────────

# Frases que delatan ser IA — si aparecen, las reemplazamos
_FRASES_IA = [
    (re.compile(r"\bcomo\s+(asistente\s+)?(ia|inteligencia\s+artificial|modelo\s+de\s+lenguaje|bot)\b", re.I),
     "como asistente del despacho"),
    (re.compile(r"\bsoy\s+(una?\s+)?(ia|inteligencia\s+artificial|asistente\s+virtual|bot|chatbot|modelo\s+de\s+lenguaje)\b", re.I),
     "trabajo en el despacho"),
    (re.compile(r"\bestoy\s+programad[oa]\b", re.I), "trabajo aquí"),
    (re.compile(r"\bno\s+soy\s+human[oa]\b", re.I), "soy María Camila"),
    (re.compile(r"\bmi\s+(programación|entrenamiento|algoritmo)\b", re.I), "el despacho"),
]


_DUPLICADOS = [
    re.compile(r"\b(del despacho)\s+\1\b", re.I),
    re.compile(r"\b(en el despacho)\s+\1\b", re.I),
    re.compile(r"\b(trabajo aquí)\s+\1\b", re.I),
    re.compile(r"\b(soy María Camila)\s+\1\b", re.I),
]


def _sanitizar_respuesta(text: str) -> str:
    """Elimina cualquier frase que delate ser IA. Defensa adicional al prompt."""
    out = text
    for rx, repl in _FRASES_IA:
        out = rx.sub(repl, out)
    # Colapsa duplicados que pueden surgir tras los reemplazos
    for rx in _DUPLICADOS:
        out = rx.sub(r"\1", out)
    # Normaliza espacios
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out
