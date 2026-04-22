#!/usr/bin/env python3
"""
============================================================
PROCESADOR DE LÍNEAS JURISPRUDENCIALES — TUTELAS CSJ
Galeano Herrera | Abogados
============================================================
Extrae texto de los boletines PDF, identifica líneas
jurisprudenciales por tema y genera índices para el
super-agente legal.

REQUISITOS:
    pip install pymupdf openai python-dotenv tqdm

USO:
    python procesar_jurisprudencia.py
    python procesar_jurisprudencia.py --anio 2024
    python procesar_jurisprudencia.py --tema salud
============================================================
"""

import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import fitz  # PyMuPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False
    print("⚠ PyMuPDF no instalado. Instale con: pip install pymupdf")

try:
    from tqdm import tqdm
    TQDM_OK = True
except ImportError:
    TQDM_OK = False

# ── Rutas ────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent
BOLETINES_DIR = BASE_DIR / "boletines"
INDICES_DIR   = BASE_DIR / "indices"
LINEAS_DIR    = BASE_DIR / "lineas_jurisprudenciales"

# ── Categorías de análisis ───────────────────────────────────
CATEGORIAS = {
    "salud": {
        "keywords": [
            "salud", "EPS", "IPS", "medicamento", "cirugía", "tratamiento",
            "incapacidad", "diagnóstico", "médico", "clínica", "hospital",
            "SIDA", "cáncer", "quimioterapia", "discapacidad", "rehabilitación",
            "autorización de servicios", "plan obligatorio", "ADRES",
        ],
        "temas_frecuentes": [
            "Negativa de servicios médicos",
            "Incumplimiento plan de tratamiento",
            "Traslado de EPS",
            "Medicamentos NO POS",
            "Incapacidades laborales",
        ]
    },
    "pensiones": {
        "keywords": [
            "pensión", "jubilación", "Colpensiones", "AFP", "cesantías",
            "fondo de pensiones", "vejez", "invalidez", "sobrevivencia",
            "mesada pensional", "historia laboral", "semanas cotizadas",
            "mesada", "ISS", "prima media", "ahorro individual",
        ],
        "temas_frecuentes": [
            "Negativa de reconocimiento pensional",
            "Historia laboral incompleta",
            "Demora en trámite pensional",
            "Pensión de invalidez",
            "Pensión de sobrevivientes",
        ]
    },
    "laboral": {
        "keywords": [
            "despido", "contrato de trabajo", "nulidad", "reintegro",
            "acoso laboral", "liquidación", "prima", "cesantías",
            "trabajador", "empleador", "salario", "horas extras",
            "fuero sindical", "fuero de maternidad", "estabilidad laboral",
            "contrato indefinido", "terminación", "justa causa",
        ],
        "temas_frecuentes": [
            "Estabilidad laboral reforzada",
            "Reintegro por fuero de maternidad",
            "Acoso laboral",
            "Derechos de trabajadores sindicalizados",
            "Mínimo vital de trabajador",
        ]
    },
    "accidentes": {
        "keywords": [
            "accidente de tránsito", "SOAT", "lesiones", "indemnización",
            "víctima", "responsabilidad civil", "vehículo", "conductor",
            "atropello", "colisión", "daño", "perjuicio",
            "seguro obligatorio", "FONSAT",
        ],
        "temas_frecuentes": [
            "Cobro SOAT",
            "Atención de urgencias post-accidente",
            "Rehabilitación de víctimas",
            "Indemnización por lesiones",
        ]
    },
    "insolvencia": {
        "keywords": [
            "insolvencia", "deudor", "acreedor", "liquidación patrimonial",
            "negociación de deudas", "Ley 1564", "Código General del Proceso",
            "concordato", "reorganización", "patrimonio",
            "codeudor", "fiador", "embargo", "secuestro",
        ],
        "temas_frecuentes": [
            "Protección patrimonial del deudor",
            "Acuerdos de reestructuración",
            "Mínimo vital en insolvencia",
        ]
    },
    "derechos_fundamentales": {
        "keywords": [
            "dignidad humana", "mínimo vital", "igualdad", "vida digna",
            "debido proceso", "libre desarrollo", "libertad", "intimidad",
            "educación", "vivienda digna", "agua potable", "alimentación",
            "personas mayores", "niños", "NNA", "adolescentes", "mujer",
            "comunidades étnicas", "indígenas", "LGTBI",
        ],
        "temas_frecuentes": [
            "Mínimo vital y móvil",
            "Dignidad humana",
            "Igualdad material",
            "Derechos de niños y adolescentes",
            "Derechos de adultos mayores",
        ]
    },
}


# ── Extracción de texto PDF ──────────────────────────────────
def extraer_texto_pdf(ruta_pdf: Path) -> str:
    """Extrae el texto completo de un PDF usando PyMuPDF."""
    if not PDF_OK:
        return ""
    try:
        doc  = fitz.open(str(ruta_pdf))
        texto = "\n".join(page.get_text() for page in doc)
        doc.close()
        return texto
    except Exception as e:
        print(f"  ⚠ Error al leer {ruta_pdf.name}: {e}")
        return ""


# ── Extracción de radicados ──────────────────────────────────
RE_RADICADO = re.compile(
    r"\b(?:STP|STL|STT|STC|STI|STQ|)[\s-]?\d{4,6}[-–]\d{4}\b",
    re.IGNORECASE
)
RE_MAGISTRADO = re.compile(
    r"(?:M\.?\s*P\.?|Magistrado(?:a)? Ponente)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]+)",
    re.IGNORECASE
)
RE_FECHA = re.compile(
    r"(?:de\s+)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    r"septiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?(\d{4})",
    re.IGNORECASE
)


def clasificar_por_tema(texto: str) -> dict:
    """Clasifica un texto en categorías jurídicas por keywords."""
    texto_lower = texto.lower()
    scores = {}
    for cat, datos in CATEGORIAS.items():
        score = sum(texto_lower.count(kw.lower()) for kw in datos["keywords"])
        if score > 0:
            scores[cat] = score
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))


def extraer_sentencias(texto: str) -> list:
    """Extrae referencias a sentencias del texto."""
    return list(set(RE_RADICADO.findall(texto)))


def extraer_magistrados(texto: str) -> list:
    """Extrae nombres de magistrados ponentes."""
    matches = RE_MAGISTRADO.findall(texto)
    return list(set(m.strip() for m in matches if len(m.strip()) > 5))


def procesar_boletin(ruta_pdf: Path, year: int, mes: int) -> dict:
    """Procesa un boletín y retorna estructura de datos."""
    texto = extraer_texto_pdf(ruta_pdf)
    if not texto:
        return {}

    temas   = clasificar_por_tema(texto)
    sents   = extraer_sentencias(texto)
    mags    = extraer_magistrados(texto)
    palabras = len(texto.split())

    return {
        "archivo"      : ruta_pdf.name,
        "anio"         : year,
        "mes"          : mes,
        "palabras"     : palabras,
        "temas"        : temas,
        "sentencias"   : sents[:50],    # Primeras 50 referencias
        "magistrados"  : mags,
        "procesado"    : datetime.now().isoformat(),
        "texto_preview": texto[:2000],  # Preview para búsqueda rápida
    }


def generar_lineas_jurisprudenciales(indice_procesado: list) -> dict:
    """
    Consolida el índice procesado en líneas jurisprudenciales por tema.
    Una línea jurisprudencial agrupa las sentencias recurrentes
    sobre el mismo problema jurídico a través del tiempo.
    """
    lineas = {cat: {"boletines": [], "total_menciones": 0} for cat in CATEGORIAS}

    for item in indice_procesado:
        for tema, score in item.get("temas", {}).items():
            if tema in lineas:
                lineas[tema]["boletines"].append({
                    "archivo": item["archivo"],
                    "anio"   : item["anio"],
                    "mes"    : item["mes"],
                    "score"  : score,
                })
                lineas[tema]["total_menciones"] += score

    # Ordenar por score dentro de cada tema
    for tema in lineas:
        lineas[tema]["boletines"].sort(key=lambda x: x["score"], reverse=True)

    return lineas


def main():
    parser = argparse.ArgumentParser(description="Procesador de jurisprudencia CSJ")
    parser.add_argument("--anio",  type=int, help="Procesar solo este año")
    parser.add_argument("--tema",  type=str, choices=list(CATEGORIAS.keys()),
                        help="Filtrar por tema")
    parser.add_argument("--rerun", action="store_true",
                        help="Re-procesar aunque ya existan los índices")
    args = parser.parse_args()

    if not PDF_OK:
        print("❌ Instala PyMuPDF: pip install pymupdf")
        return

    INDICES_DIR.mkdir(exist_ok=True)
    LINEAS_DIR.mkdir(exist_ok=True)
    for cat in CATEGORIAS:
        (LINEAS_DIR / cat).mkdir(exist_ok=True)

    # ── Cargar índice de boletines descargados ──────────────
    indice_path = BOLETINES_DIR / "indice_boletines.json"
    if not indice_path.exists():
        print(f"❌ No existe {indice_path}")
        print("   Ejecute primero: python descargar_boletines.py")
        return

    with open(indice_path, encoding="utf-8") as f:
        indice_descarga = json.load(f)

    print("=" * 65)
    print("  PROCESADOR DE JURISPRUDENCIA — CSJ TUTELAS")
    print("=" * 65)

    resultados = []
    cache_path = INDICES_DIR / "procesados.json"
    cache = {}
    if cache_path.exists() and not args.rerun:
        with open(cache_path, encoding="utf-8") as f:
            cache = {item["archivo"]: item for item in json.load(f).get("items", [])}

    for anio_str, boletines in sorted(indice_descarga["boletines"].items(), reverse=True):
        year = int(anio_str)
        if args.anio and year != args.anio:
            continue

        print(f"\n📁  {year}")
        for b in boletines:
            ruta = BOLETINES_DIR / anio_str / b["archivo"]
            if not ruta.exists():
                print(f"  ⚠ No encontrado: {b['archivo']}")
                continue

            if b["archivo"] in cache and not args.rerun:
                print(f"  ✓ (cache) {b['archivo']}")
                resultados.append(cache[b["archivo"]])
                continue

            print(f"  ⚙ Procesando {b['archivo']}...")
            res = procesar_boletin(ruta, year, b["mes"])
            if res:
                resultados.append(res)
                # Guardar análisis individual por tema
                temas_top = list(res["temas"].keys())[:2]
                for tema in temas_top:
                    if args.tema and tema != args.tema:
                        continue
                    tema_dir = LINEAS_DIR / tema
                    tema_dir.mkdir(exist_ok=True)
                    out = tema_dir / f"analisis_{anio_str}_{b['mes']:02d}.json"
                    with open(out, "w", encoding="utf-8") as f:
                        json.dump(res, f, ensure_ascii=False, indent=2)

    # ── Guardar índice consolidado ───────────────────────────
    indice_consolidado = {
        "generado": datetime.now().isoformat(),
        "total_procesados": len(resultados),
        "items": resultados,
    }
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(indice_consolidado, f, ensure_ascii=False, indent=2)

    # ── Generar líneas jurisprudenciales ─────────────────────
    lineas = generar_lineas_jurisprudenciales(resultados)
    lineas_path = INDICES_DIR / "lineas_jurisprudenciales.json"
    with open(lineas_path, "w", encoding="utf-8") as f:
        json.dump({
            "generado": datetime.now().isoformat(),
            "lineas": lineas,
        }, f, ensure_ascii=False, indent=2)

    # ── Resumen ──────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print(f"  ✓ Boletines procesados: {len(resultados)}")
    print(f"\n  LÍNEAS JURISPRUDENCIALES IDENTIFICADAS:")
    for tema, datos in sorted(lineas.items(), key=lambda x: x[1]["total_menciones"], reverse=True):
        print(f"    {tema:30s}: {datos['total_menciones']:>6} menciones | {len(datos['boletines'])} boletines")
    print(f"\n  📋 Índice : {cache_path}")
    print(f"  📊 Líneas : {lineas_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
