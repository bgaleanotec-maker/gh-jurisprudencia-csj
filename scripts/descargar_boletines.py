#!/usr/bin/env python3
"""
============================================================
DESCARGADOR DE BOLETINES - CORTE SUPREMA DE JUSTICIA
Galeano Herrera | Abogados
Sistema Masivo de Jurisprudencia - Modelo Uri Levine
============================================================
Descarga los 132 boletines de tutelas (2014-2025)
y los organiza por año en la carpeta boletines/

USO:
    pip install requests
    python descargar_boletines.py

    # Solo años recientes:
    python descargar_boletines.py --desde 2022

    # Forzar re-descarga:
    python descargar_boletines.py --forzar
============================================================
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime

# ── Configuración de rutas ──────────────────────────────────
BASE_DIR = Path(__file__).parent.parent / "boletines"
INDICE_PATH = BASE_DIR / "indice_boletines.json"
LOG_PATH = BASE_DIR / "descarga_log.txt"

BASE_URL_WWW = "https://www.cortesuprema.gov.co/corte/wp-content/uploads/relatorias/tutelas"
BASE_URL_API = "https://archivodigitalapi.cortesuprema.gov.co/share"

# ── Meses en español ────────────────────────────────────────
MESES = {
    1:  {"abr": "ENE", "nombre": "ENERO"},
    2:  {"abr": "FEB", "nombre": "FEBRERO"},
    3:  {"abr": "MAR", "nombre": "MARZO"},
    4:  {"abr": "ABR", "nombre": "ABRIL"},
    5:  {"abr": "MAY", "nombre": "MAYO"},
    6:  {"abr": "JUN", "nombre": "JUNIO"},
    7:  {"abr": "JUL", "nombre": "JULIO"},
    8:  {"abr": "AGO", "nombre": "AGOSTO"},
    9:  {"abr": "SEP", "nombre": "SEPTIEMBRE"},
    10: {"abr": "OCT", "nombre": "OCTUBRE"},
    11: {"abr": "NOV", "nombre": "NOVIEMBRE"},
    12: {"abr": "DIC", "nombre": "DICIEMBRE"},
}

# ── Catálogo completo de boletines disponibles ──────────────
BOLETINES_POR_ANIO = {
    2025: list(range(1, 9)),   # Enero–Agosto 2025
    2024: list(range(1, 13)),
    2023: list(range(1, 13)),
    2022: list(range(1, 13)),
    2021: list(range(1, 13)),
    2020: list(range(1, 13)),
    2019: list(range(1, 13)),
    2018: list(range(1, 13)),
    2017: list(range(1, 13)),
    2016: list(range(1, 12)),  # Enero–Noviembre (sin diciembre)
    2015: list(range(1, 13)),
    2014: [1, 2, 3, 4, 5],    # Solo enero–mayo
}

# ── URLs especiales (nuevo servidor API desde mayo 2025) ────
URLS_ESPECIALES = {
    (2025, 8): f"{BASE_URL_API}/2025/8/Boletines/BOLETIN AGOSTO 2025.pdf",
    (2025, 7): f"{BASE_URL_API}/2025/7/Boletines/BOLETIN JULIO 2025.pdf",
    (2025, 6): f"{BASE_URL_API}/2025/6/Relevantes/BOLETIN JUNIO 2025.pdf",
    (2025, 5): f"{BASE_URL_API}/2025/5/Boletines/BOLETIN MAYO 2025.pdf",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
    "Referer": "https://cortesuprema.gov.co/boletines-anteriores-de-la-relatoria-de-sala-plena-y-tutelas/",
}


def construir_url(year: int, mes: int) -> str:
    """Devuelve la URL del PDF para el año y mes dados."""
    if (year, mes) in URLS_ESPECIALES:
        return URLS_ESPECIALES[(year, mes)].replace(" ", "%20")
    mes_abr   = MESES[mes]["abr"]
    mes_nombre = MESES[mes]["nombre"]
    carpeta   = f"B {mes_abr}{year}".replace(" ", "%20")
    archivo   = f"BOLETIN {mes_nombre} {year}.pdf".replace(" ", "%20")
    return f"{BASE_URL_WWW}/{carpeta}/{archivo}"


def nombre_archivo(year: int, mes: int) -> str:
    return f"boletin_{year}_{mes:02d}_{MESES[mes]['nombre'].lower()}.pdf"


def descargar(year: int, mes: int, directorio: Path, forzar: bool = False) -> dict:
    """Descarga un boletín. Retorna dict con resultado."""
    url   = construir_url(year, mes)
    fname = nombre_archivo(year, mes)
    dest  = directorio / fname

    if dest.exists() and not forzar:
        return {"ok": True, "archivo": fname, "estado": "ya_existe", "url": url}

    try:
        resp = requests.get(url, headers=HEADERS, timeout=90, stream=True)
        if resp.status_code == 200:
            contenido = resp.content
            if len(contenido) < 500:
                return {"ok": False, "archivo": fname, "estado": "vacio", "url": url}
            with open(dest, "wb") as f:
                f.write(contenido)
            kb = len(contenido) / 1024
            return {"ok": True, "archivo": fname, "estado": "descargado", "url": url, "kb": round(kb)}
        else:
            return {"ok": False, "archivo": fname, "estado": f"http_{resp.status_code}", "url": url}
    except requests.exceptions.Timeout:
        return {"ok": False, "archivo": fname, "estado": "timeout", "url": url}
    except Exception as e:
        return {"ok": False, "archivo": fname, "estado": f"error: {e}", "url": url}


def main():
    parser = argparse.ArgumentParser(description="Descargador de boletines CSJ")
    parser.add_argument("--desde", type=int, default=2014,
                        help="Año inicial (default: 2014)")
    parser.add_argument("--hasta", type=int, default=2025,
                        help="Año final (default: 2025)")
    parser.add_argument("--forzar", action="store_true",
                        help="Re-descargar aunque ya existan los archivos")
    args = parser.parse_args()

    print("=" * 65)
    print("  BOLETINES DE TUTELAS — CORTE SUPREMA DE JUSTICIA")
    print("  Galeano Herrera | Abogados  ·  Sistema Uri Levine")
    print("=" * 65)
    print(f"  Período: {args.desde} – {args.hasta}")
    print(f"  Destino: {BASE_DIR.resolve()}")
    print("=" * 65)

    BASE_DIR.mkdir(parents=True, exist_ok=True)

    indice   = {}
    total_ok = 0
    total_err= 0
    log_lines= []

    for year in sorted(BOLETINES_POR_ANIO.keys(), reverse=True):
        if not (args.desde <= year <= args.hasta):
            continue

        dir_year = BASE_DIR / str(year)
        dir_year.mkdir(exist_ok=True)
        print(f"\n📁  {year}")

        indice[str(year)] = []

        for mes in BOLETINES_POR_ANIO[year]:
            res = descargar(year, mes, dir_year, args.forzar)
            icono = "✓" if res["ok"] else "✗"
            detalle = f"  {icono} {res['archivo']}"
            if res["estado"] == "descargado":
                detalle += f"  [{res.get('kb','?')} KB]"
            elif res["estado"] == "ya_existe":
                detalle += "  (ya existe)"
            else:
                detalle += f"  → {res['estado']}"
            print(detalle)
            log_lines.append(f"{datetime.now().isoformat()} | {year}-{mes:02d} | {res['estado']} | {res['url']}")

            if res["ok"]:
                total_ok += 1
                indice[str(year)].append({
                    "mes": mes,
                    "nombre_mes": MESES[mes]["nombre"],
                    "archivo": res["archivo"],
                    "ruta_relativa": f"{year}/{res['archivo']}",
                    "url_fuente": res["url"],
                    "descargado": datetime.now().isoformat(),
                })
            else:
                total_err += 1

            if res["estado"] == "descargado":
                time.sleep(0.8)  # Ser respetuosos con el servidor

    # ── Guardar índice JSON ──────────────────────────────────
    indice_data = {
        "generado": datetime.now().isoformat(),
        "fuente": "https://cortesuprema.gov.co/boletines-anteriores-de-la-relatoria-de-sala-plena-y-tutelas/",
        "total_descargados": total_ok,
        "total_errores": total_err,
        "boletines": indice,
    }
    with open(INDICE_PATH, "w", encoding="utf-8") as f:
        json.dump(indice_data, f, ensure_ascii=False, indent=2)

    # ── Log de descarga ──────────────────────────────────────
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print(f"\n{'=' * 65}")
    print(f"  ✓ Exitosos : {total_ok}")
    print(f"  ✗ Errores  : {total_err}")
    print(f"  📋 Índice  : {INDICE_PATH}")
    print(f"  📝 Log     : {LOG_PATH}")
    print("=" * 65)


if __name__ == "__main__":
    main()
