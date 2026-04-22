#!/usr/bin/env python3
"""
============================================================
EXTRACTOR DE FICHAS — SUPER-AGENTE LEGAL
Galeano Herrera | Abogados
============================================================
Extrae cada sentencia de los boletines PDF como una ficha
JSON estructurada, lista para RAG con Gemini.

Por cada sentencia genera:
  {
    "id"          : "STC1059-2025",
    "tipo"        : "STC",
    "sala"        : "CIVIL",
    "anio"        : 2025,
    "mes"         : 8,
    "boletin"     : "boletin_2025_08_agosto.pdf",
    "temas"       : ["DERECHO AL DEBIDO PROCESO", ...],
    "descriptores": ["Proceso de pertenencia - Defecto fáctico...", ...],
    "texto_busqueda": "...",   ← campo principal para embeddings
    "tokens_est"  : 312,
  }

USO:
    python extraer_fichas.py                    # Procesa 2018-2025
    python extraer_fichas.py --desde 2022       # Solo desde ese año
    python extraer_fichas.py --pdf ruta.pdf     # Un boletín concreto
    python extraer_fichas.py --docx ruta.docx   # Una ficha .docx
    python extraer_fichas.py --stats            # Ver estadísticas del índice
============================================================
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import fitz          # PyMuPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False
    print("⚠  PyMuPDF no disponible. Instala: pip install pymupdf")

try:
    from docx import Document as DocxDocument
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

BASE_DIR    = Path(__file__).parent.parent
BOL_DIR     = BASE_DIR / "boletines"
FICHAS_DIR  = BASE_DIR / "fichas"
INDEX_FILE  = BASE_DIR / "indices" / "fichas_index.jsonl"
CACHE_FILE  = BASE_DIR / "indices" / "fichas_procesados.json"

# ── Patrones ─────────────────────────────────────────────────────────────────
RE_RADICADO   = re.compile(
    r'\bSENTENCIA\s+((?:STP|STL|STC|STI|STQ)\s*[\d]+-\s*\d{4})\b',
    re.IGNORECASE
)
RE_SALA_CIVIL  = re.compile(r'SALA\s+DE\s+CASACI[ÓO]N\s+CIVIL', re.IGNORECASE)
RE_SALA_PENAL  = re.compile(r'SALA\s+DE\s+CASACI[ÓO]N\s+PENAL',  re.IGNORECASE)
RE_SALA_LABORAL= re.compile(r'SALA\s+DE\s+CASACI[ÓO]N\s+LABORAL', re.IGNORECASE)
RE_SALA_PLENA  = re.compile(r'SALA\s+PLENA',                       re.IGNORECASE)
RE_ENCABEZADO  = re.compile(
    r'El contenido de este bolet[íi]n es un extracto|'
    r'https?://\S+|'
    r'Bogot[áa],\s*D\.\s*C\.,\s*\d+|'
    r'Trimestre\s+\d+-\d+',
    re.IGNORECASE
)
RE_TEMA_CAPS = re.compile(r'^([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s/,()-]{5,}[A-ZÁÉÍÓÚÜÑ])$')

TIPO_SALA = {
    'STC': 'CIVIL', 'STI': 'INSOLVENCIA',
    'STP': 'PENAL', 'STL': 'LABORAL', 'STQ': 'OTRO',
}

AREA_MAP = {
    'salud':       ['salud','eps','medicamento','tratamiento','incapacidad','cirugía','ips'],
    'pensiones':   ['pensión','pensiones','colpensiones','afp','invalidez','sobrevivencia'],
    'laboral':     ['laboral','despido','reintegro','trabajador','contrato','prestaciones',
                    'maternidad','fuero sindical','acoso'],
    'accidentes':  ['accidente','tránsito','soat','fonsat','lesiones','atropello'],
    'insolvencia': ['insolvencia','deuda','embargo','reestructuración','acreedores','mínimo vital'],
    'derechos_fundamentales': ['dignidad','vida digna','igualdad','niños','adultos mayores',
                                'desplazados','paz','conflicto'],
}


def _sala_from_radicado(radicado: str) -> str:
    tipo = re.match(r'(STC|STP|STL|STI|STQ)', radicado.upper())
    return TIPO_SALA.get(tipo.group(1) if tipo else '', 'OTRO')


def _detectar_area(texto: str) -> list[str]:
    """Detecta las áreas legales relevantes en el texto."""
    texto_l = texto.lower()
    areas = []
    for area, keywords in AREA_MAP.items():
        if any(kw in texto_l for kw in keywords):
            areas.append(area)
    return areas or ['derechos_fundamentales']


def _tokens_est(texto: str) -> int:
    """Estimación rápida de tokens (~4 chars/token para español)."""
    return len(texto) // 4


def _limpiar_linea(linea: str) -> str:
    linea = linea.strip()
    if RE_ENCABEZADO.search(linea):
        return ''
    return linea


def _construir_texto_busqueda(radicado, sala, temas, descriptores) -> str:
    """Genera el texto optimizado para embeddings (300-500 tokens objetivo)."""
    partes = [f"Sentencia {radicado} | Sala {sala}"]
    if temas:
        partes.append("TEMAS: " + " | ".join(temas[:6]))
    if descriptores:
        # Tomar los descriptores más significativos
        desc_text = " // ".join(d[:120] for d in descriptores[:12])
        partes.append("DESCRIPTORES: " + desc_text)
    return "\n".join(partes)


# ── Parser principal de boletín PDF ──────────────────────────────────────────

def extraer_sentencias_boletin(pdf_path: Path, anio: int, mes: int) -> list[dict]:
    """
    Parsea un boletín PDF y extrae cada sentencia como ficha estructurada.
    Retorna lista de dicts con todos los campos.
    """
    if not PDF_OK:
        return []

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"  ✗ No se pudo abrir {pdf_path.name}: {e}")
        return []

    # Extraer texto completo página por página
    paginas = []
    for page in doc:
        paginas.append(page.get_text())
    doc.close()

    texto_completo = "\n".join(paginas)

    # Detectar sala actual mientras recorremos
    sala_actual = "CIVIL"
    sentencias = []
    segmento_actual = []
    radicado_actual = None

    lineas = texto_completo.split('\n')

    def _flush_segmento():
        nonlocal radicado_actual, segmento_actual
        if radicado_actual and segmento_actual:
            ficha = _parsear_segmento(radicado_actual, sala_actual,
                                       segmento_actual, anio, mes,
                                       pdf_path.name)
            if ficha:
                sentencias.append(ficha)
        radicado_actual = None
        segmento_actual = []

    for linea in lineas:
        linea_limpia = _limpiar_linea(linea)
        if not linea_limpia:
            continue

        # Detectar cambio de sala
        if RE_SALA_CIVIL.search(linea_limpia):
            sala_actual = "CIVIL"
        elif RE_SALA_PENAL.search(linea_limpia):
            sala_actual = "PENAL"
        elif RE_SALA_LABORAL.search(linea_limpia):
            sala_actual = "LABORAL"
        elif RE_SALA_PLENA.search(linea_limpia):
            sala_actual = "PLENA"

        # Nueva sentencia
        m = RE_RADICADO.match(linea_limpia)
        if m:
            _flush_segmento()
            radicado_actual = m.group(1).replace(' ', '').replace('\u2013', '-')
            # Inferir sala desde el radicado si no está explícita
            sala_infer = _sala_from_radicado(radicado_actual)
            if sala_infer != 'OTRO':
                sala_actual = sala_infer
            continue

        if radicado_actual:
            segmento_actual.append(linea_limpia)

    _flush_segmento()

    return sentencias


def _parsear_segmento(radicado: str, sala: str, lineas: list[str],
                       anio: int, mes: int, boletin: str) -> Optional[dict]:
    """Convierte el bloque de texto de una sentencia en ficha estructurada."""
    temas = []
    descriptores = []
    tema_actual = None

    for linea in lineas:
        if not linea.strip():
            continue
        # ¿Es un encabezado de tema (todo mayúsculas)?
        if RE_TEMA_CAPS.match(linea.strip()):
            tema_actual = linea.strip()
            temas.append(tema_actual)
        elif linea.strip().startswith('-') or linea.strip().startswith('•'):
            desc = linea.strip().lstrip('-•').strip()
            if desc and len(desc) > 15:
                descriptores.append(desc)
        else:
            # Línea de subtema/descriptor sin guion
            stripped = linea.strip()
            if stripped and len(stripped) > 20 and tema_actual:
                descriptores.append(stripped)

    if not temas and not descriptores:
        return None

    texto_busqueda = _construir_texto_busqueda(radicado, sala, temas, descriptores)

    return {
        "id"             : radicado,
        "tipo"           : radicado[:3].upper(),
        "sala"           : sala,
        "anio"           : anio,
        "mes"            : mes,
        "boletin"        : boletin,
        "temas"          : temas,
        "descriptores"   : descriptores,
        "areas"          : _detectar_area(texto_busqueda),
        "texto_busqueda" : texto_busqueda,
        "tokens_est"     : _tokens_est(texto_busqueda),
        "fuente"         : "boletin_pdf",
        "procesado_en"   : datetime.now().isoformat(),
    }


# ── Parser de ficha .docx ─────────────────────────────────────────────────────

def extraer_ficha_docx(docx_path: Path) -> Optional[dict]:
    """
    Parsea una ficha individual en formato .docx (FICHA RADICADO-YYYY.docx).
    Estas fichas tienen Tesis con «texto» y jerarquía completa de temas.
    """
    if not DOCX_OK:
        print("  ✗ python-docx no instalado: pip install python-docx")
        return None

    # Inferir radicado del nombre de archivo
    nombre = docx_path.stem  # e.g. "FICHA STC1059-2025"
    m = re.search(r'((?:STP|STL|STC|STI|STQ)[\s-]?\d+-\s*\d{4})', nombre, re.IGNORECASE)
    radicado = m.group(1).replace(' ', '').replace('\u2013', '-') if m else docx_path.stem

    anio_m = re.search(r'(\d{4})', radicado)
    anio = int(anio_m.group(1)) if anio_m else 0

    try:
        doc = DocxDocument(str(docx_path))
    except Exception as e:
        print(f"  ✗ No se pudo abrir {docx_path.name}: {e}")
        return None

    temas = []
    descriptores = []
    tesis_partes = []
    en_tesis = False

    for para in doc.paragraphs:
        texto = para.text.strip()
        if not texto:
            continue

        # Detectar sección TESIS
        if re.match(r'^Tesis\s*:', texto, re.IGNORECASE):
            en_tesis = True
            resto = texto[texto.find(':')+1:].strip()
            if resto:
                tesis_partes.append(resto)
            continue

        if en_tesis:
            tesis_partes.append(texto)
            continue

        # Detectar TEMA
        if re.match(r'^TEMA\s*:', texto, re.IGNORECASE):
            tema_texto = texto[texto.find(':')+1:].strip()
            if tema_texto:
                temas.append(tema_texto)
            continue

        # Descriptores / encabezados de tema
        if RE_TEMA_CAPS.match(texto):
            temas.append(texto)
        elif texto.startswith('-') or texto.startswith('•'):
            desc = texto.lstrip('-•').strip()
            if desc and len(desc) > 10:
                descriptores.append(desc)

    tesis = ' '.join(tesis_partes).strip()

    # Texto para embeddings: tesis completa + temas (fichas tienen riqueza semántica alta)
    partes = [f"Sentencia {radicado} | Sala {_sala_from_radicado(radicado)}"]
    if temas:
        partes.append("TEMAS: " + " | ".join(temas[:6]))
    if descriptores:
        partes.append("DESCRIPTORES: " + " // ".join(d[:120] for d in descriptores[:10]))
    if tesis:
        # Tesis es el texto más valioso - incluir completo (es la doctrina)
        partes.append("TESIS: " + tesis[:2000])

    texto_busqueda = "\n".join(partes)

    return {
        "id"             : radicado,
        "tipo"           : radicado[:3].upper(),
        "sala"           : _sala_from_radicado(radicado),
        "anio"           : anio,
        "mes"            : 0,
        "boletin"        : docx_path.name,
        "temas"          : temas,
        "descriptores"   : descriptores,
        "tesis"          : tesis,
        "areas"          : _detectar_area(texto_busqueda),
        "texto_busqueda" : texto_busqueda,
        "tokens_est"     : _tokens_est(texto_busqueda),
        "fuente"         : "ficha_docx",
        "procesado_en"   : datetime.now().isoformat(),
    }


# ── Guardar fichas ────────────────────────────────────────────────────────────

def guardar_ficha(ficha: dict):
    """Guarda ficha individual en fichas/{anio}/{radicado}.json"""
    anio_dir = FICHAS_DIR / str(ficha["anio"])
    anio_dir.mkdir(parents=True, exist_ok=True)
    ruta = anio_dir / f"{ficha['id']}.json"
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(ficha, f, ensure_ascii=False, indent=2)
    return ruta


def agregar_a_index(ficha: dict):
    """Agrega ficha al índice JSONL para ingesta en FAISS."""
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, 'a', encoding='utf-8') as f:
        linea = {
            "id"            : ficha["id"],
            "anio"          : ficha["anio"],
            "mes"           : ficha["mes"],
            "sala"          : ficha["sala"],
            "areas"         : ficha["areas"],
            "tokens_est"    : ficha["tokens_est"],
            "texto_busqueda": ficha["texto_busqueda"],
        }
        f.write(json.dumps(linea, ensure_ascii=False) + '\n')


def cargar_cache() -> set:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, encoding='utf-8') as f:
            data = json.load(f)
        return set(data.get("procesados", []))
    return set()


def guardar_cache(procesados: set):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump({"procesados": list(procesados),
                   "actualizado": datetime.now().isoformat()}, f, indent=2)


# ── Pipeline principal ────────────────────────────────────────────────────────

def procesar_todos(desde: int = 2018, hasta: int = 2026, forzar: bool = False):
    """Procesa todos los boletines desde `desde` hasta `hasta`."""
    procesados = cargar_cache()
    nuevas_fichas = 0
    boletines_proc = 0
    errores = 0

    # Limpiar index si es forzado
    if forzar and INDEX_FILE.exists():
        INDEX_FILE.unlink()
        procesados = set()

    pdfs = sorted([
        p for p in BOL_DIR.rglob("*.pdf")
        if p.stat().st_size > 5000  # ignorar archivos vacíos/corruptos
    ])

    pdfs_objetivo = [
        p for p in pdfs
        if desde <= int(p.parent.name) <= hasta
    ]

    print(f"\n📂 Boletines encontrados ({desde}-{hasta}): {len(pdfs_objetivo)}")

    for pdf in pdfs_objetivo:
        if pdf.name in procesados and not forzar:
            continue

        anio = int(pdf.parent.name)
        # Extraer mes del nombre del archivo: boletin_2025_08_agosto.pdf
        m = re.search(r'_(\d{2})_', pdf.name)
        mes = int(m.group(1)) if m else 0

        print(f"  ▶ {pdf.name} ", end='', flush=True)
        sentencias = extraer_sentencias_boletin(pdf, anio, mes)

        if not sentencias:
            print("(sin sentencias detectadas)")
            errores += 1
        else:
            for ficha in sentencias:
                guardar_ficha(ficha)
                agregar_a_index(ficha)
                nuevas_fichas += 1
            print(f"→ {len(sentencias)} sentencias")
            procesados.add(pdf.name)
            boletines_proc += 1

    # Procesar fichas .docx sueltas si existen
    docx_dir = BASE_DIR / "fichas_docx"
    if docx_dir.exists():
        for docx in sorted(docx_dir.rglob("*.docx")):
            if docx.name in procesados and not forzar:
                continue
            print(f"  ▶ {docx.name} ", end='', flush=True)
            ficha = extraer_ficha_docx(docx)
            if ficha:
                guardar_ficha(ficha)
                agregar_a_index(ficha)
                nuevas_fichas += 1
                procesados.add(docx.name)
                print(f"→ ok ({ficha['tokens_est']} tokens est.)")
            else:
                print("(error)")
                errores += 1

    guardar_cache(procesados)

    print(f"\n{'='*55}")
    print(f"  Boletines procesados : {boletines_proc}")
    print(f"  Fichas nuevas        : {nuevas_fichas}")
    print(f"  Errores              : {errores}")
    print(f"  Índice JSONL         : {INDEX_FILE}")
    print(f"{'='*55}")
    return nuevas_fichas


def mostrar_stats():
    """Muestra estadísticas del índice actual."""
    if not INDEX_FILE.exists():
        print("❌ Índice no encontrado. Ejecute el extractor primero.")
        return

    total = 0
    por_area = {}
    por_sala = {}
    por_anio = {}
    tokens_total = 0

    with open(INDEX_FILE, encoding='utf-8') as f:
        for linea in f:
            try:
                ficha = json.loads(linea)
                total += 1
                tokens_total += ficha.get('tokens_est', 0)
                anio = str(ficha.get('anio', '?'))
                por_anio[anio] = por_anio.get(anio, 0) + 1
                sala = ficha.get('sala', '?')
                por_sala[sala] = por_sala.get(sala, 0) + 1
                for area in ficha.get('areas', []):
                    por_area[area] = por_area.get(area, 0) + 1
            except json.JSONDecodeError:
                continue

    print(f"\n📊 ESTADÍSTICAS DEL ÍNDICE DE FICHAS")
    print(f"{'='*45}")
    print(f"  Total fichas      : {total:,}")
    print(f"  Tokens estimados  : {tokens_total:,}  (~${tokens_total/1_000_000*0.10:.2f} USD Gemini)")
    print(f"\n  Por sala:")
    for sala, n in sorted(por_sala.items(), key=lambda x: -x[1]):
        print(f"    {sala:15s}: {n:>5}")
    print(f"\n  Por área legal:")
    for area, n in sorted(por_area.items(), key=lambda x: -x[1]):
        print(f"    {area:30s}: {n:>5}")
    print(f"\n  Por año:")
    for a, n in sorted(por_anio.items()):
        print(f"    {a}: {n:>4} fichas")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extractor de fichas jurisprudenciales")
    parser.add_argument("--desde",  type=int, default=2018, help="Año inicial (default: 2018)")
    parser.add_argument("--hasta",  type=int, default=2026, help="Año final (default: 2026)")
    parser.add_argument("--forzar", action="store_true",    help="Reprocesar aunque existan en caché")
    parser.add_argument("--pdf",    type=str, metavar="PATH", help="Procesar un solo PDF")
    parser.add_argument("--docx",   type=str, metavar="PATH", help="Procesar una sola ficha .docx")
    parser.add_argument("--stats",  action="store_true",    help="Mostrar estadísticas del índice")
    args = parser.parse_args()

    print("=" * 55)
    print("  EXTRACTOR DE FICHAS — GALEANO HERRERA")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    if args.stats:
        mostrar_stats()
        return

    if args.pdf:
        p = Path(args.pdf)
        m = re.search(r'(\d{4})', p.name)
        anio = int(m.group(1)) if m else datetime.now().year
        m2 = re.search(r'_(\d{2})_', p.name)
        mes = int(m2.group(1)) if m2 else 0
        print(f"\n▶ Procesando: {p.name}")
        sentencias = extraer_sentencias_boletin(p, anio, mes)
        for ficha in sentencias:
            ruta = guardar_ficha(ficha)
            agregar_a_index(ficha)
            print(f"  ✓ {ficha['id']} ({ficha['tokens_est']} tokens) → {ruta.name}")
        print(f"\n  Total: {len(sentencias)} fichas extraídas")
        return

    if args.docx:
        p = Path(args.docx)
        print(f"\n▶ Procesando: {p.name}")
        ficha = extraer_ficha_docx(p)
        if ficha:
            ruta = guardar_ficha(ficha)
            agregar_a_index(ficha)
            print(f"  ✓ {ficha['id']} ({ficha['tokens_est']} tokens) → {ruta.name}")
            print(f"  Áreas: {', '.join(ficha['areas'])}")
            print(f"  Temas: {len(ficha['temas'])}")
        return

    procesar_todos(desde=args.desde, hasta=args.hasta, forzar=args.forzar)


if __name__ == "__main__":
    main()
