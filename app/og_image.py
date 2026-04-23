"""
Genera la imagen Open Graph para Facebook/WhatsApp/Twitter.
Formato estándar OG: 1200x630 PNG.

Sin archivos externos: usa solo PIL con las fuentes por defecto.
Se cachea en memoria en la primera llamada.
"""

from __future__ import annotations

import io
import threading
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False

_W, _H = 1200, 630
_AZUL = (0, 35, 71)
_AZUL_2 = (0, 63, 122)
_ORO = (197, 160, 89)
_BLANCO = (255, 255, 255)
_VERDE = (22, 163, 74)

_cache_png: Optional[bytes] = None
_lock = threading.Lock()


def _find_font(size: int) -> "ImageFont.FreeTypeFont | ImageFont.ImageFont":
    """Intenta fuentes comunes en Linux/Windows; cae a default."""
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generar_og_png() -> bytes:
    """Retorna el PNG de la imagen OG. Cacheado en memoria."""
    global _cache_png
    if _cache_png is not None:
        return _cache_png
    if not PIL_OK:
        # fallback: PNG mínimo 1x1 azul (firma PNG válida)
        return (b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
                b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\x99c\xf8\x0f'
                b'\x04\x00\x00\xff\xff\x00\x02\x00\x01\xe5\x27\xde\xfc\x00\x00\x00\x00IEND\xaeB`\x82')

    with _lock:
        if _cache_png is not None:
            return _cache_png

        img = Image.new("RGB", (_W, _H), _AZUL)
        d = ImageDraw.Draw(img)

        # Gradiente diagonal simple (simulado con rectángulos)
        for i in range(60):
            ratio = i / 60
            r = int(_AZUL[0] + (_AZUL_2[0] - _AZUL[0]) * ratio)
            g = int(_AZUL[1] + (_AZUL_2[1] - _AZUL[1]) * ratio)
            b = int(_AZUL[2] + (_AZUL_2[2] - _AZUL[2]) * ratio)
            d.rectangle([(0, int(_H*i/60)), (_W, int(_H*(i+1)/60))], fill=(r, g, b))

        # Banda superior oro
        d.rectangle([(0, 0), (_W, 6)], fill=_ORO)

        # Logo Galeano Herrera
        f_logo = _find_font(44)
        d.text((60, 56), "Galeano", font=f_logo, fill=_BLANCO)
        d.text((60, 110), "Herrera", font=f_logo, fill=_ORO)
        f_sub  = _find_font(18)
        d.text((60, 170), "A B O G A D O S", font=f_sub, fill=_BLANCO)

        # Headline principal
        f_h1 = _find_font(64)
        f_h1_2 = _find_font(64)
        y = 260
        d.text((60, y),     "Te están negando", font=f_h1, fill=_BLANCO)
        d.text((60, y+72),  "un derecho.", font=f_h1, fill=_ORO)
        d.text((60, y+144), "Recuperalo en 2 minutos.", font=f_h1_2, fill=_BLANCO)

        # Bullet bar inferior — textos cortos que caben en una sola fila de 1200
        f_b = _find_font(20)
        bullets = [
            "Respaldo en la Corte Suprema",
            "Radicados verificables",
            "Abogado en WhatsApp",
        ]
        y_b = 542
        d.rectangle([(0, 510), (_W, _H)], fill=(0, 20, 50))
        d.rectangle([(0, 510), (_W, 514)], fill=_ORO)
        # Calcular ancho total y distribuir
        widths = [int(d.textlength(b, font=f_b)) if hasattr(d, "textlength") else len(b)*11 for b in bullets]
        total_text = sum(widths)
        gap = (_W - 120 - total_text - 3*26) // 2   # 3 bullets => 2 gaps ; 26 = circle+margin
        x = 60
        for i, b in enumerate(bullets):
            d.ellipse([(x, y_b+7), (x+12, y_b+19)], fill=_VERDE)
            d.text((x+22, y_b), b, font=f_b, fill=_BLANCO)
            x += widths[i] + 26 + (gap if i < len(bullets)-1 else 0)

        # Footer: URL + pequeño disclaimer
        f_u = _find_font(16)
        d.text((60, 605), "gh-jurisprudencia-csj.onrender.com · Ley 1581 Habeas Data",
               font=f_u, fill=(180, 180, 180))

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        _cache_png = buf.getvalue()
        return _cache_png
