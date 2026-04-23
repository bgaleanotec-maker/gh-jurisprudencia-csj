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
import time
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

_CACHE_MAX = 500
_cache: "OrderedDict[str, dict]" = OrderedDict()
_cache_lock = threading.Lock()


def _normalizar_para_cache(desc: str) -> str:
    """Normaliza para que 'Me niega, Sanitas!' y 'me niega sanitas' peguen al mismo cache."""
    t = (desc or "").lower().strip()
    # Quitar puntuación y múltiples espacios
    t = re.sub(r"[^\w\sáéíóúüñ]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:1500]


def _cache_key(desc: str, area: Optional[str], extra: str = "") -> str:
    raw = ((area or "") + "::" + _normalizar_para_cache(desc) + "::" + (extra or ""))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def cache_get(desc: str, area: Optional[str], extra: str = "") -> Optional[dict]:
    k = _cache_key(desc, area, extra)
    with _cache_lock:
        if k in _cache:
            _cache.move_to_end(k)
            return _cache[k]
    return None


def cache_put(desc: str, area: Optional[str], value: dict, extra: str = "") -> None:
    k = _cache_key(desc, area, extra)
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
    from datetime import datetime as _dt
    dc = datos_cliente or {}
    nombre = (dc.get("nombre") or dc.get("name") or "").strip()
    cedula = (dc.get("cedula") or "").strip()
    ciudad = (dc.get("ciudad") or "Bogotá D.C.").strip()
    accionado = (dc.get("accionado") or "").strip()
    telefono = (dc.get("phone") or "").strip()
    email = (dc.get("email") or "").strip()
    fecha = _dt.now().strftime("%d de %B de %Y")

    # Reemplazos de meses en español
    MESES = {"January":"enero","February":"febrero","March":"marzo","April":"abril",
             "May":"mayo","June":"junio","July":"julio","August":"agosto",
             "September":"septiembre","October":"octubre","November":"noviembre","December":"diciembre"}
    for en, es in MESES.items():
        fecha = fecha.replace(en, es)

    block_accionante = f"{nombre}" if nombre else "[COMPLETAR: nombre completo del accionante]"
    block_cedula = f"{cedula}" if cedula else "[COMPLETAR: número de cédula]"
    block_accionado = f"{accionado}" if accionado else "[COMPLETAR: nombre exacto y NIT de la entidad accionada]"
    block_tel = f"+{telefono}" if telefono else "[COMPLETAR: teléfono del accionante]"
    block_email = email if email else "[COMPLETAR: correo del accionante]"

    return f"""Eres jurista colombiano experto en acciones de tutela ante la Corte Suprema de Justicia.
Vas a redactar un BORRADOR de tutela sustancialmente COMPLETO basado en la situación del ciudadano.

DATOS DEL CASO (ÚSALOS LITERALMENTE — NO reemplaces por [COMPLETAR] si tienen valor):
  Accionante: {block_accionante}
  Cédula:     {block_cedula}
  Ciudad:     {ciudad}
  Accionado:  {block_accionado}
  Teléfono:   {block_tel}
  Correo:     {block_email}
  Fecha:      {fecha}

REGLAS INNEGOCIABLES:
1. Solo cita radicados que aparezcan EXPRESAMENTE en JURISPRUDENCIA RECUPERADA. NUNCA inventes.
2. Si un dato NO te fue dado arriba, entonces SÍ usa [COMPLETAR: ...] con indicación clara.
3. Sé PROLIJO: el borrador debe tener entre 700 y 1100 palabras, listo para revisión por abogado.
4. Redacta en español formal jurídico colombiano pero comprensible. Tuteo prohibido en el documento.
5. Entrega solo el documento. Sin comentarios de IA ni meta-explicaciones.
6. Numera los hechos (al menos 5, hasta 8). Incluye fechas aproximadas según la descripción.
7. Cita al menos 3 radicados de la jurisprudencia en FUNDAMENTOS JURÍDICOS.

JURISPRUDENCIA RECUPERADA:
{contexto}

SITUACIÓN RELATADA POR EL CIUDADANO:
{descripcion}

Genera el BORRADOR con esta estructura exacta (Markdown):

## ACCIÓN DE TUTELA

**Señor Juez Constitucional de {ciudad} (Reparto)**
**Referencia:** Acción de Tutela de {block_accionante} contra {block_accionado}

{block_accionante}, mayor de edad, identificado con cédula de ciudadanía No. {block_cedula}, domiciliado en {ciudad}, con el debido respeto acudo ante su Despacho para interponer ACCIÓN DE TUTELA contra {block_accionado}, por la vulneración de mis derechos fundamentales, con fundamento en los siguientes:

### I. HECHOS
1. (redacta cronológico, basado en la descripción del ciudadano)
2. ...
(5 a 8 hechos numerados, cada uno una oración clara)

### II. DERECHOS FUNDAMENTALES VULNERADOS
Lista los derechos concretos vulnerados (salud, mínimo vital, debido proceso, etc.).

### III. FUNDAMENTOS DE DERECHO
Redacta 3-4 párrafos densos citando los radicados de la jurisprudencia recuperada entre paréntesis, ej: "(STC1234-2023)". Explica cómo cada precedente aplica al caso.

### IV. PROCEDENCIA DE LA ACCIÓN
Justifica brevemente:
- **Legitimación activa** del accionante.
- **Legitimación pasiva** del accionado.
- **Inmediatez** (cuándo ocurrió el hecho).
- **Subsidiariedad** (por qué la tutela es la vía idónea).

### V. PRETENSIONES
Numeradas. Sé específico y ejecutable. Incluye siempre:
1. Amparar los derechos fundamentales vulnerados.
2. Ordenar a {block_accionado} realizar la acción específica que se pide.
3. (Cuando aplique) solicitar MEDIDA PROVISIONAL URGENTE por riesgo inminente.
4. Imponer costas y sanciones por desacato si incumple.

### VI. MEDIDA PROVISIONAL
Si el caso lo exige (salud, mínimo vital), redacta el párrafo de solicitud de medida provisional citando jurisprudencia.

### VII. PRUEBAS
Lista de documentos que debe anexar el accionante (historia clínica, comunicaciones, reclamaciones previas, órdenes médicas, etc. — según el caso).

### VIII. JURAMENTO
Declaro bajo la gravedad del juramento que no he presentado otra acción de tutela por los mismos hechos.

### IX. NOTIFICACIONES
- **Accionante:** {block_accionante}, C.C. {block_cedula}. Tel: {block_tel}. Correo: {block_email}. Dirección: [COMPLETAR: dirección física].
- **Accionado:** {block_accionado}. [COMPLETAR: dirección de notificación].
- **Despacho de apoderado (opcional):** Galeano Herrera | Abogados — contacto@galeanoherrera.co.

### X. ANEXOS
1. Copia de la cédula del accionante.
2. (Demás pruebas documentales listadas en VI.)

{ciudad}, {fecha}

Atentamente,

_______________________________
{block_accionante}
C.C. {block_cedula}

---

**Fuentes jurisprudenciales citadas en este borrador:**
(lista cada radicado en bullet)
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

    # Cache: incluye datos que cambian el texto (nombre, cedula, accionado, ciudad)
    cache_extra = ""
    if datos_cliente:
        dc = datos_cliente
        cache_extra = "|".join(str(dc.get(k,"")).strip().lower() for k in
                               ("nombre","cedula","accionado","ciudad"))
    if usar_cache:
        hit = cache_get(descripcion, area, extra=cache_extra)
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

    from google.genai import types as genai_types

    # Intento con cascada de modelos: flash-lite primero (cuota propia),
    # luego 2.0-flash. 5 intentos en total con backoff exponencial.
    MODELOS = ["gemini-2.0-flash-lite", "gemini-2.0-flash"]
    texto = ""
    last_err = None
    BACKOFFS = [0, 4, 8, 15, 25]   # segundos entre intentos

    for intento in range(5):
        modelo = MODELOS[intento % len(MODELOS)]
        if BACKOFFS[intento]:
            time.sleep(BACKOFFS[intento])
        try:
            r = motor._client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2600,
                ),
            )
            texto = (r.text or "").strip()
            if texto:
                break
        except Exception as e:
            last_err = e
            msg = str(e)
            # 429 / RESOURCE_EXHAUSTED → seguir al siguiente modelo/intento
            if any(tag in msg for tag in ("429", "RESOURCE_EXHAUSTED", "quota", "Quota")):
                continue
            # Modelo no disponible → probar el siguiente
            if "404" in msg or "NOT_FOUND" in msg:
                continue
            # Errores no recuperables
            return {"error": f"Error generando: {e}",
                    "user_message": "Hubo un problema técnico. Intenta de nuevo en unos minutos.",
                    "draft": "", "fichas": []}

    if not texto:
        return {
            "error": "rate_limited",
            "user_message": (
                "Estamos atendiendo a muchos usuarios en este momento. "
                "Espera 1 minuto y vuelve a intentar. "
                "Si el problema persiste, escríbenos por WhatsApp y te atendemos directamente."
            ),
            "draft": "", "fichas": [],
        }

    if not texto:
        return {"error": str(last_err) if last_err else "Sin respuesta del modelo",
                "user_message": "No se pudo generar el borrador. Intenta de nuevo.", "draft": "", "fichas": []}

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
    if usar_cache:
        cache_put(descripcion, area, out, extra=cache_extra)
    return out


# ── Preview parcial (con efecto blur en frontend) ────────────────────────────

def construir_preview(draft: str, palabras_visibles: int = 260) -> dict:
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
