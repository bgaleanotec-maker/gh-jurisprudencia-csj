#!/usr/bin/env python3
"""
============================================================
PIPELINE COMPLETO — SUPER-AGENTE LEGAL
Galeano Herrera | Abogados
============================================================
Ejecuta el pipeline completo:
  1. Descarga boletines CSJ nuevos
  2. Procesa y extrae jurisprudencia
  3. Genera índice actualizado
  4. Reporta novedades

USO:
    python pipeline_completo.py              # Pipeline completo
    python pipeline_completo.py --solo-nuevo # Solo boletines nuevos
    python pipeline_completo.py --reporte    # Solo genera reporte

Ideal para ejecutar semanalmente (cron job / tarea programada)
============================================================
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

BASE_DIR    = Path(__file__).parent.parent
SCRIPTS_DIR = Path(__file__).parent
LOG_DIR     = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


def ejecutar_script(nombre: str, args_extra: list = None) -> bool:
    """Ejecuta un script Python del directorio scripts/."""
    cmd = [sys.executable, str(SCRIPTS_DIR / nombre)] + (args_extra or [])
    print(f"\n▶ Ejecutando: {nombre}")
    print(f"  Comando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"  ✗ Error en {nombre} (código {result.returncode})")
        return False
    print(f"  ✓ {nombre} completado")
    return True


def generar_reporte_novedades() -> dict:
    """
    Genera un reporte de las novedades jurisprudenciales
    del último mes, clasificadas por tema.
    """
    indices_path = BASE_DIR / "indices" / "procesados.json"
    if not indices_path.exists():
        return {"error": "índice no disponible"}

    with open(indices_path, encoding="utf-8") as f:
        data = json.load(f)

    # Tomar los últimos 3 boletines procesados
    items = sorted(
        data.get("items", []),
        key=lambda x: (x.get("anio", 0), x.get("mes", 0)),
        reverse=True
    )[:3]

    reporte = {
        "fecha"    : datetime.now().isoformat(),
        "novedades": [],
    }

    for item in items:
        reporte["novedades"].append({
            "boletin": f"{item.get('anio')}-{item.get('mes', 0):02d}",
            "temas_principales": list(item.get("temas", {}).keys())[:3],
            "total_sentencias" : len(item.get("sentencias", [])),
            "magistrados"      : item.get("magistrados", [])[:2],
        })

    return reporte


def main():
    parser = argparse.ArgumentParser(description="Pipeline completo super-agente legal")
    parser.add_argument("--solo-nuevo",  action="store_true",
                        help="Solo descarga boletines del año actual")
    parser.add_argument("--reporte",     action="store_true",
                        help="Solo genera reporte de novedades")
    parser.add_argument("--desde",       type=int, default=2022,
                        help="Año desde el que descargar (default: 2022)")
    args = parser.parse_args()

    log_path = LOG_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    print("=" * 65)
    print("  PIPELINE SUPER-AGENTE LEGAL — GALEANO HERRERA")
    print(f"  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    if args.reporte:
        reporte = generar_reporte_novedades()
        print("\n📊 NOVEDADES JURISPRUDENCIALES:")
        for nov in reporte.get("novedades", []):
            print(f"\n  Boletín {nov['boletin']}")
            print(f"    Temas: {', '.join(nov['temas_principales'])}")
            print(f"    Sentencias citadas: {nov['total_sentencias']}")
        return

    # ── Paso 1: Descargar ────────────────────────────────────
    descarga_args = []
    if args.solo_nuevo:
        descarga_args = ["--desde", "2025"]
    elif args.desde:
        descarga_args = ["--desde", str(args.desde)]

    ok_descarga = ejecutar_script("descargar_boletines.py", descarga_args)

    # ── Paso 2: Procesar ─────────────────────────────────────
    if ok_descarga:
        ok_proceso = ejecutar_script("procesar_jurisprudencia.py")
    else:
        print("⚠ Descarga con errores parciales, intentando procesar lo disponible...")
        ok_proceso = ejecutar_script("procesar_jurisprudencia.py")

    # ── Paso 3: Reporte ──────────────────────────────────────
    if ok_proceso:
        reporte = generar_reporte_novedades()
        reporte_path = BASE_DIR / "indices" / "ultimo_reporte.json"
        with open(reporte_path, "w", encoding="utf-8") as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)
        print(f"\n📊 Reporte guardado en: {reporte_path}")

    print(f"\n{'=' * 65}")
    print(f"  Pipeline completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Log: {log_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
