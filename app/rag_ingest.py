"""
Cerebro RAG — pipeline de ingesta de documentos PDF.

Flujo:
1. Recibir PDF (bytes).
2. Extraer texto por página con PyMuPDF.
3. Chunkificar (≈1500 caracteres con overlap 200).
4. Transformar con IA: extraer metadata estructurada (sala, radicado, año,
   áreas, temas, tesis) — fichar como sentencia/ley/doctrina.
5. Persistir documento + chunks en SQLite (status='processed').
6. Esperar aprobación admin para entrar al RAG.

Sin Pillow ni OCR: si el PDF es solo imágenes, falla con un mensaje claro.
"""

from __future__ import annotations

import io
import json
import re
from typing import Optional

try:
    import fitz  # PyMuPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 200
MAX_PAGES_FOR_AI_METADATA = 6   # solo las primeras N páginas para extraer meta


def _limpiar_texto(t: str) -> str:
    if not t:
        return ""
    # normalizar espacios
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    # quitar caracteres no imprimibles excepto saltos de línea
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", t)
    return t.strip()


def extraer_texto_pdf(file_bytes: bytes) -> tuple[list[dict], str]:
    """
    Devuelve ([{'page': n, 'text': str}], full_text).
    Lanza ValueError si no se puede leer el PDF o no tiene texto.
    """
    if not PDF_OK:
        raise RuntimeError("PyMuPDF (fitz) no está instalado.")
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise ValueError(f"No se puede abrir el PDF: {e}")

    paginas = []
    full = []
    for i, page in enumerate(doc, start=1):
        try:
            txt = page.get_text("text") or ""
        except Exception:
            txt = ""
        txt = _limpiar_texto(txt)
        if txt:
            paginas.append({"page": i, "text": txt})
            full.append(txt)
    doc.close()
    if not paginas:
        raise ValueError("El PDF no contiene texto extraíble (¿es una imagen escaneada?).")
    return paginas, "\n\n".join(full)


def chunkificar(paginas: list[dict], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """
    Devuelve chunks con metadata de página: [{'chunk_index', 'page', 'texto', 'tokens_est'}].
    Trata de no cortar en medio de oraciones.
    """
    chunks = []
    idx = 0
    for p in paginas:
        text = p["text"]
        if len(text) < MIN_CHUNK_CHARS:
            chunks.append({
                "chunk_index": idx, "page": p["page"], "texto": text,
                "tokens_est": len(text) // 4,
            })
            idx += 1
            continue
        i = 0
        while i < len(text):
            end = min(i + size, len(text))
            # ajustar al final de oración cercano
            if end < len(text):
                p_dot = text.rfind(". ", i, end)
                p_nl  = text.rfind("\n", i, end)
                cut = max(p_dot, p_nl)
                if cut > i + size // 2:
                    end = cut + 1
            slice_ = text[i:end].strip()
            if len(slice_) >= MIN_CHUNK_CHARS or i == 0:
                chunks.append({
                    "chunk_index": idx, "page": p["page"], "texto": slice_,
                    "tokens_est": len(slice_) // 4,
                })
                idx += 1
            i = end - overlap if end - overlap > i else end
            if i >= len(text):
                break
    return chunks


# ── Transformación con IA (extrae metadata estructurada) ─────────────────────

PROMPT_FICHAR = """Eres jurista colombiano. A continuación recibirás texto de un documento legal
(probablemente sentencia, ley, decreto, doctrina o pieza procesal). Tu trabajo es devolver
SOLAMENTE un objeto JSON con esta estructura, sin texto adicional ni explicación:

{
  "tipo": "sentencia" | "ley" | "decreto" | "doctrina" | "pieza_procesal" | "otro",
  "sala": "CIVIL" | "LABORAL" | "PENAL" | "PLENA" | "CONSTITUCIONAL" | "—",
  "radicado": string o null (ej: "STC1234-2023", "T-456/19", "C-005/17"),
  "anio": int o null,
  "ciudad": string o null,
  "areas": [   // las que apliquen, de esta lista cerrada
    "salud" | "pensiones" | "laboral" | "accidentes" |
    "insolvencia" | "derechos_fundamentales"
  ],
  "temas": [string, string, ...],   // 2 a 6 temas en mayúsculas (ej: "DERECHO A LA SALUD")
  "tesis": string,                  // 1-3 frases con la regla de decisión o tesis central
  "descriptores": [string, ...],    // 3-8 descriptores breves del contenido
  "resumen_corto": string           // 1 párrafo (máx 60 palabras) para mostrar en UI
}

REGLAS ESTRICTAS:
- Solo JSON válido. Sin markdown, sin comentarios, sin etiquetas.
- Si un campo no aplica o no se puede extraer, usa null o lista vacía.
- Si el texto está incompleto, infiere lo que puedas con cuidado, sin inventar radicado.
- NO inventes radicados. Si no hay uno claro, "radicado": null.

DOCUMENTO:
"""


def fichar_documento_con_ia(motor, texto_inicio: str) -> dict:
    """
    Llama a Gemini con las primeras páginas del PDF para extraer metadata estructurada.
    motor: instancia de MotorRAG (debe tener self._client + GENAI_NEW=True).
    Si falla, retorna metadata mínima.
    """
    fallback = {
        "tipo": "otro", "sala": "—", "radicado": None, "anio": None, "ciudad": None,
        "areas": [], "temas": [], "tesis": None, "descriptores": [],
        "resumen_corto": "Documento cargado sin metadata automática.",
    }
    if not (motor and getattr(motor, "_client", None)):
        return fallback
    try:
        from google.genai import types as genai_types
        prompt = PROMPT_FICHAR + texto_inicio[:14000]
        for modelo in ("gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-2.5-flash"):
            try:
                r = motor._client.models.generate_content(
                    model=modelo, contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=0.0, max_output_tokens=900,
                        response_mime_type="application/json",
                    ),
                )
                texto = (r.text or "").strip()
                if not texto: continue
                # Limpiar: a veces incluye ```json ... ```
                if texto.startswith("```"):
                    texto = re.sub(r"^```[a-zA-Z]*\n?", "", texto)
                    texto = re.sub(r"\n?```$", "", texto)
                data = json.loads(texto)
                # sanitizar
                AREAS_VALIDAS = {"salud","pensiones","laboral","accidentes","insolvencia","derechos_fundamentales"}
                data["areas"] = [a for a in (data.get("areas") or []) if a in AREAS_VALIDAS]
                data["temas"] = [str(t)[:120] for t in (data.get("temas") or [])][:8]
                data["descriptores"] = [str(d)[:200] for d in (data.get("descriptores") or [])][:10]
                if data.get("anio"):
                    try: data["anio"] = int(data["anio"])
                    except: data["anio"] = None
                return {**fallback, **data}
            except Exception as e:
                last_err = e
                continue
        return {**fallback, "_error_ai": str(last_err) if 'last_err' in dir() else "no model"}
    except Exception as e:
        return {**fallback, "_error_ai": str(e)}


def procesar_pdf(file_bytes: bytes, filename: str, motor=None) -> dict:
    """
    Pipeline completo: extraer texto → chunks → metadata IA.
    Devuelve {'paginas','chunks','metadata','tokens_est','full_text_len'}.
    NO persiste; eso lo hace el endpoint con db.create_rag_document + add_rag_chunks.
    """
    paginas, full = extraer_texto_pdf(file_bytes)
    chunks = chunkificar(paginas)
    # primeras N páginas para fichar
    inicio = "\n\n".join(p["text"] for p in paginas[:MAX_PAGES_FOR_AI_METADATA])
    metadata = fichar_documento_con_ia(motor, inicio) if motor else {
        "tipo":"otro","sala":"—","radicado":None,"anio":None,"areas":[],"temas":[],
        "tesis":None,"descriptores":[],"resumen_corto":"Cargado sin IA."
    }
    metadata["paginas_total"] = len(paginas)
    metadata["filename"] = filename
    return {
        "paginas": len(paginas),
        "chunks": chunks,
        "metadata": metadata,
        "tokens_est": sum(c["tokens_est"] for c in chunks),
        "full_text_len": len(full),
    }
