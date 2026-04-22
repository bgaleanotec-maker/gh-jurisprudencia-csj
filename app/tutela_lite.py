"""
Generador de borrador de tutela LIGERO (1 sola llamada Gemini, sin rerank).

Optimizaciones de costo:
  • top_k = 4 fichas, sin rerank LLM
  • max_output_tokens = 1300
  • Cache LRU por hash(descripcion+area) → reusa borradores
  • Prompt con prohibición explícita de inventar y obligación de citar

Detección automática de área a partir de palabras clave para no obligar al
cliente a saber clasificar su caso.
"""

from __future__ import annotations

import hashlib
import io
import re
import threading
from collections import OrderedDict
from typing import Optional

# ── Detección de área por keywords (cero costo) ───────────────────────────────

_KW_AREA = {
    "salud":        ["eps", "ips", "medicamento", "cirugía", "medico", "tratamiento",
                     "oncolo", "cancer", "quimio", "radio", "diagnostico", "hospital",
                     "clinica", "sanitas", "sura", "compensar", "salud total"],
    "pensiones":    ["pension", "colpensiones", "afp", "porvenir", "proteccion",
                     "mesada", "vejez", "invalidez", "sustitucion"],
    "laboral":      ["despido", "trabajo", "salario", "prestaciones", "contrato",
                     "laboral", "empleador", "embarazo", "maternidad", "fuero",
                     "lactancia", "discapacidad laboral", "acoso laboral", "renuncia"],
    "accidentes":   ["accidente", "transito", "soat", "choque", "atropello",
                     "vehiculo", "moto", "polizon", "responsabilidad civil"],
    "insolvencia":  ["insolvencia", "deuda", "embargo", "ejecutivo", "acreedor",
                     "ley 1564", "concurso", "quiebra", "reorganizacion"],
    "derechos_fundamentales": ["fotomulta", "comparendo", "infraccion", "cobro coactivo",
                               "minimo vital", "habeas corpus", "libertad", "libertad inmediata",
                               "mora judicial", "debido proceso"],
}


def detectar_area(texto: str) -> Optional[str]:
    t = (texto or "").lower()
    scores = {}
    for area, kws in _KW_AREA.items():
        scores[area] = sum(1 for k in kws if k in t)
    if not scores: return None
    mejor, n = max(scores.items(), key=lambda x: x[1])
    return mejor if n >= 1 else None


# ── Cache LRU en memoria ──────────────────────────────────────────────────────

_CACHE_MAX = 200
_cache: "OrderedDict[str, dict]" = OrderedDict()
_cache_lock = threading.Lock()


def _cache_key(desc: str, area: Optional[str]) -> str:
    raw = ((area or "") + "::" + (desc or "").lower().strip()[:1500])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cache_get(desc: str, area: Optional[str]) -> Optional[dict]:
    k = _cache_key(desc, area)
    with _cache_lock:
        if k in _cache:
            _cache.move_to_end(k)
            return _cache[k]
    return None


def cache_put(desc: str, area: Optional[str], value: dict) -> None:
    k = _cache_key(desc, area)
    with _cache_lock:
        _cache[k] = value
        _cache.move_to_end(k)
        while len(_cache) > _CACHE_MAX:
            _cache.popitem(last=False)


# ── Prompt anti-alucinación ───────────────────────────────────────────────────

DISCLAIMER = (
    "─────────────────────────────────────────\n"
    "⚠ AVISO IMPORTANTE — ESTE BORRADOR NO CONSTITUYE ASESORÍA JURÍDICA\n"
    "─────────────────────────────────────────\n"
    "Este documento es una guía orientativa generada por inteligencia\n"
    "artificial a partir de jurisprudencia pública de la Corte Suprema de\n"
    "Justicia de Colombia. Su contenido NO sustituye la asesoría de un\n"
    "abogado titulado.\n\n"
    "Antes de presentar cualquier acción legal, le recomendamos validar\n"
    "este borrador con un abogado. En Galeano Herrera | Abogados podemos\n"
    "evaluar su caso y acompañarlo en todo el proceso.\n"
    "─────────────────────────────────────────\n\n"
)


def _prompt_publico(descripcion: str, contexto: str, datos_cliente: Optional[dict] = None) -> str:
    datos = ""
    if datos_cliente:
        datos = (
            f"DATOS DEL CLIENTE (úselos textualmente en el borrador):\n"
            f"  Nombre: {datos_cliente.get('name','[COMPLETAR NOMBRE]')}\n"
            f"  Cédula: {datos_cliente.get('cedula','[COMPLETAR CC]')}\n"
            f"  Teléfono: +{datos_cliente.get('phone','')}\n\n"
        )
    return f"""Eres jurista colombiano experto en jurisprudencia de tutelas de la Corte Suprema de Justicia.
Vas a redactar un BORRADOR de acción de tutela basado en la situación de un ciudadano.

REGLAS ESTRICTAS:
1. SOLO puedes citar radicados que aparezcan EXPRESAMENTE en la jurisprudencia recuperada (sección JURISPRUDENCIA).
   NUNCA inventes radicados, fechas o magistrados.
2. Si la jurisprudencia no respalda un punto, di "se requiere análisis adicional con su abogado".
3. Marca con [COMPLETAR: ...] cualquier dato que falte.
4. Lenguaje formal pero claro, accesible para el ciudadano.
5. NO incluyas comentarios de IA ni meta-explicaciones; entrega solo el documento.

{datos}JURISPRUDENCIA RECUPERADA:
{contexto}

SITUACIÓN RELATADA POR EL CIUDADANO:
{descripcion}

Genera el BORRADOR siguiendo esta estructura exacta en Markdown:

## ACCIÓN DE TUTELA

**Señor Juez Constitucional (Reparto)**
[COMPLETAR: Ciudad]

**Asunto:** Acción de Tutela instaurada por [nombre] contra [accionado] por vulneración de derechos fundamentales.

### I. PARTES
- **Accionante:** [nombre], cédula [cédula].
- **Accionado:** [COMPLETAR: nombre exacto de la entidad].

### II. HECHOS
1. ...
2. ...
(numera 4-7 hechos a partir de la situación relatada)

### III. DERECHOS FUNDAMENTALES VULNERADOS
Lista breve.

### IV. FUNDAMENTOS JURÍDICOS
3-5 párrafos. CADA afirmación jurisprudencial debe llevar su radicado entre paréntesis,
tomado SOLO de la sección JURISPRUDENCIA. Ejemplo: "(STC1234-2023)".

### V. PRETENSIONES
Numeradas. Incluye solicitud de medida provisional si aplica.

### VI. PRUEBAS
Lista de documentos que el accionante debe anexar.

### VII. JURAMENTO Y NOTIFICACIONES
Datos de contacto del accionante.

### VIII. ANEXOS
Lista breve.

Al final del documento agrega una sección "**Fuentes jurisprudenciales utilizadas**"
con los radicados citados en formato lista.
"""


# ── Generador principal ───────────────────────────────────────────────────────

def generar_borrador(motor, descripcion: str, area: Optional[str] = None,
                     datos_cliente: Optional[dict] = None,
                     usar_cache: bool = True) -> dict:
    """
    motor: instancia de MotorRAG (con FAISS listo o BM25 como mínimo).
    Retorna dict: {draft, fichas, area_detectada, cached, tokens_aprox}
    """
    descripcion = (descripcion or "").strip()
    if len(descripcion) < 30:
        return {"error": "Descripción demasiado corta. Cuente al menos: qué pasó, quién es el accionado y desde cuándo.",
                "draft": "", "fichas": []}

    if not area:
        area = detectar_area(descripcion)

    # Cache (sin datos personales — solo descripción + área)
    if usar_cache and not datos_cliente:
        hit = cache_get(descripcion, area)
        if hit:
            hit2 = dict(hit); hit2["cached"] = True
            return hit2

    fichas = motor.buscar(descripcion, k=4, filtro_area=area, hibrido=True)
    if not fichas:
        # Reintentar sin filtro de área
        fichas = motor.buscar(descripcion, k=4, hibrido=True)

    if not fichas:
        return {"error": "No se encontraron precedentes en la base. Reformule incluyendo términos del área legal.",
                "draft": "", "fichas": []}

    contexto = motor._construir_contexto(fichas)
    prompt   = _prompt_publico(descripcion, contexto, datos_cliente)

    try:
        from google.genai import types as genai_types
        r = motor._client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.15,
                max_output_tokens=1300,
            ),
        )
        texto = (r.text or "").strip()
    except Exception as e:
        return {"error": f"Error generando: {e}", "draft": "", "fichas": []}

    draft = DISCLAIMER + texto + (
        "\n\n─────────────────────────────────────────\n"
        "📞 *Galeano Herrera | Abogados*\n"
        "Su caso merece la asesoría de un especialista.\n"
        "Coordinamos una evaluación gratuita por WhatsApp.\n"
        "─────────────────────────────────────────"
    )

    out = {
        "draft": draft,
        "fichas": [{"id": f["id"], "sala": f.get("sala"), "anio": f.get("anio"),
                    "areas": f.get("areas", [])} for f in fichas],
        "area_detectada": area,
        "cached": False,
        "tokens_aprox": len(prompt)//4 + len(texto)//4,
    }
    if usar_cache and not datos_cliente:
        cache_put(descripcion, area, out)
    return out


# ── Preview parcial (con efecto blur en frontend) ────────────────────────────

def construir_preview(draft: str, palabras_visibles: int = 180) -> dict:
    """Devuelve el draft particionado: 'visible' (texto plano) y 'oculto' (resto enmascarado)."""
    if not draft: return {"visible": "", "oculto_chars": 0}
    palabras = draft.split()
    if len(palabras) <= palabras_visibles:
        return {"visible": draft, "oculto_chars": 0}
    visible = " ".join(palabras[:palabras_visibles])
    oculto  = " ".join(palabras[palabras_visibles:])
    return {"visible": visible, "oculto_chars": len(oculto), "oculto_palabras": len(palabras)-palabras_visibles}


# ── Render a DOCX (sin dependencias pesadas, fallback a TXT) ─────────────────

def borrador_a_docx(draft: str, nombre_cliente: str = "") -> bytes:
    try:
        from docx import Document
        from docx.shared import Pt, Cm, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        return draft.encode("utf-8")

    d = Document()
    section = d.sections[0]
    for m in (section.top_margin, section.bottom_margin, section.left_margin, section.right_margin):
        pass
    section.top_margin = Cm(2.5); section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5); section.right_margin = Cm(2.5)

    style = d.styles["Normal"]
    style.font.name = "Calibri"; style.font.size = Pt(11)

    # Encabezado de marca
    h = d.add_paragraph()
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = h.add_run("GALEANO HERRERA | ABOGADOS")
    run.bold = True; run.font.size = Pt(14); run.font.color.rgb = RGBColor(0x00, 0x23, 0x47)
    sub = d.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.add_run("Borrador de Acción de Tutela — Documento orientativo").italic = True
    d.add_paragraph()

    for raw_line in draft.splitlines():
        line = raw_line.rstrip()
        if not line:
            d.add_paragraph(); continue
        if line.startswith("## "):
            p = d.add_paragraph(); r = p.add_run(line[3:].strip())
            r.bold = True; r.font.size = Pt(13); r.font.color.rgb = RGBColor(0x00, 0x23, 0x47)
        elif line.startswith("### "):
            p = d.add_paragraph(); r = p.add_run(line[4:].strip())
            r.bold = True; r.font.size = Pt(12)
        elif line.startswith("**") and line.endswith("**"):
            p = d.add_paragraph(); p.add_run(line.strip("*")).bold = True
        elif line.startswith("- ") or line.startswith("* "):
            d.add_paragraph(line[2:], style="List Bullet")
        elif re.match(r"^\d+\. ", line):
            d.add_paragraph(line[line.find(".")+1:].strip(), style="List Number")
        elif line.startswith("─") or set(line.strip()) == {"─"}:
            continue
        else:
            d.add_paragraph(line)

    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()
