#!/usr/bin/env python3
"""
============================================================
BUSCADOR DE JURISPRUDENCIA — SUPER-AGENTE LEGAL
Galeano Herrera | Abogados
============================================================
Motor de búsqueda sobre los boletines procesados.
Permite al super-agente responder preguntas jurídicas
con base en líneas jurisprudenciales reales de la CSJ.

USO:
    python buscar_jurisprudencia.py "negativa eps medicamento"
    python buscar_jurisprudencia.py --tema salud --anio 2023
    python buscar_jurisprudencia.py --listar-temas
============================================================
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Optional

BASE_DIR    = Path(__file__).parent.parent
INDICES_DIR = BASE_DIR / "indices"
LINEAS_DIR  = BASE_DIR / "lineas_jurisprudenciales"
BOLETINES_DIR = BASE_DIR / "boletines"

try:
    import fitz
    PDF_OK = True
except ImportError:
    PDF_OK = False


def cargar_indices() -> dict:
    """Carga el índice consolidado de jurisprudencia procesada."""
    p = INDICES_DIR / "procesados.json"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cargar_lineas() -> dict:
    """Carga las líneas jurisprudenciales consolidadas."""
    p = INDICES_DIR / "lineas_jurisprudenciales.json"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def buscar_en_texto(query: str, indice: dict, max_resultados: int = 10) -> list:
    """
    Búsqueda por palabras clave en los previews de texto de los boletines.
    Retorna lista de boletines relevantes ordenados por relevancia.
    """
    terminos = query.lower().split()
    resultados = []

    for item in indice.get("items", []):
        texto = item.get("texto_preview", "").lower()
        score = sum(texto.count(t) for t in terminos)
        if score > 0:
            resultados.append({
                "archivo": item["archivo"],
                "anio"   : item["anio"],
                "mes"    : item["mes"],
                "score"  : score,
                "temas"  : list(item.get("temas", {}).keys())[:3],
                "sentencias": item.get("sentencias", [])[:5],
                "preview": texto[:500],
            })

    return sorted(resultados, key=lambda x: x["score"], reverse=True)[:max_resultados]


def buscar_en_pdf(query: str, ruta_pdf: Path, contexto_chars: int = 400) -> list:
    """Busca query en un PDF y retorna fragmentos contextuales."""
    if not PDF_OK:
        return []
    try:
        doc = fitz.open(str(ruta_pdf))
        fragmentos = []
        patron = re.compile(re.escape(query), re.IGNORECASE)
        for i, page in enumerate(doc):
            texto = page.get_text()
            for m in patron.finditer(texto):
                inicio = max(0, m.start() - contexto_chars // 2)
                fin    = min(len(texto), m.end() + contexto_chars // 2)
                fragmentos.append({
                    "pagina"  : i + 1,
                    "contexto": texto[inicio:fin].strip(),
                })
        doc.close()
        return fragmentos
    except Exception:
        return []


def generar_informe_caso(tipo_caso: str, hechos: str, indice: dict) -> str:
    """
    Genera un informe jurisprudencial para un caso específico.
    Diseñado para alimentar directamente al super-agente.
    """
    query    = f"{tipo_caso} {hechos}"
    resultados = buscar_en_texto(query, indice, max_resultados=5)
    lineas   = cargar_lineas()

    informe = [
        f"# INFORME JURISPRUDENCIAL — CASO: {tipo_caso.upper()}",
        f"**Consulta:** {hechos}",
        f"**Fecha:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}",
        "",
        "## Boletines con jurisprudencia relevante:",
    ]

    for r in resultados:
        informe.append(
            f"\n### Boletín {r['anio']}-{r['mes']:02d}  (relevancia: {r['score']})"
        )
        informe.append(f"**Temas:** {', '.join(r['temas'])}")
        if r["sentencias"]:
            informe.append(f"**Sentencias citadas:** {', '.join(r['sentencias'][:3])}")

    # Agregar líneas jurisprudenciales del tema
    tema_map = {
        "salud": "salud",  "eps": "salud", "medicamento": "salud",
        "pensión": "pensiones", "colpensiones": "pensiones",
        "despido": "laboral", "reintegro": "laboral", "trabajador": "laboral",
        "accidente": "accidentes", "soat": "accidentes",
        "insolvencia": "insolvencia", "deuda": "insolvencia",
    }
    tema_detectado = None
    query_lower = query.lower()
    for kw, tema in tema_map.items():
        if kw in query_lower:
            tema_detectado = tema
            break

    if tema_detectado and "lineas" in lineas:
        datos_linea = lineas["lineas"].get(tema_detectado, {})
        if datos_linea.get("total_menciones", 0) > 0:
            informe.append(f"\n## Línea jurisprudencial: {tema_detectado.upper()}")
            informe.append(
                f"**Menciones totales en boletines CSJ:** {datos_linea['total_menciones']}"
            )
            boletines_top = datos_linea["boletines"][:3]
            informe.append("**Boletines más relevantes:**")
            for b in boletines_top:
                informe.append(f"  - {b['archivo']} (score {b['score']})")

    return "\n".join(informe)


def listar_temas(lineas: dict):
    """Muestra resumen de líneas jurisprudenciales disponibles."""
    print("\n LÍNEAS JURISPRUDENCIALES DISPONIBLES")
    print("=" * 55)
    for tema, datos in sorted(
        lineas.get("lineas", {}).items(),
        key=lambda x: x[1].get("total_menciones", 0), reverse=True
    ):
        n_bol = len(datos.get("boletines", []))
        menc  = datos.get("total_menciones", 0)
        print(f"  {tema:30s}: {menc:>5} menciones | {n_bol:>3} boletines")
    print()


def main():
    parser = argparse.ArgumentParser(description="Buscador de jurisprudencia CSJ")
    parser.add_argument("query", nargs="?", help="Texto a buscar")
    parser.add_argument("--tema", choices=["salud","pensiones","laboral",
                                           "accidentes","insolvencia",
                                           "derechos_fundamentales"])
    parser.add_argument("--anio", type=int)
    parser.add_argument("--listar-temas", action="store_true")
    parser.add_argument("--informe",  action="store_true",
                        help="Generar informe completo para un caso")
    args = parser.parse_args()

    indice = cargar_indices()
    lineas = cargar_lineas()

    if not indice:
        print("❌ No hay índice procesado.")
        print("   Ejecute: python procesar_jurisprudencia.py")
        return

    if args.listar_temas:
        listar_temas(lineas)
        return

    if not args.query:
        parser.print_help()
        return

    if args.informe:
        tipo = args.tema or "tutela"
        print(generar_informe_caso(tipo, args.query, indice))
        return

    resultados = buscar_en_texto(args.query, indice)

    print(f"\n🔍 Resultados para: '{args.query}'")
    print(f"   Encontrados: {len(resultados)} boletines relevantes\n")

    for i, r in enumerate(resultados, 1):
        print(f"  {i}. Boletín {r['anio']}-{r['mes']:02d} | score {r['score']}")
        print(f"     Temas: {', '.join(r['temas'])}")
        if r["sentencias"]:
            print(f"     Sentencias: {', '.join(r['sentencias'][:3])}")
        print()


if __name__ == "__main__":
    main()
