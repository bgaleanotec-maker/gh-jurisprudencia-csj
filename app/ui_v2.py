"""
ui_v2.py — Sistema visual v2: "Lujo institucional cercano".

Tipografia: Fraunces (display serif) + Inter (body).
Paleta: oro #C5A059 como acento, escala de grises calida, azul deep para hero/footer.

Por ahora expone:
  - landing_v2_html(cfg) : reemplaza a ui.landing_html con estilo moderno.

Servido temporalmente en /preview/{slug} para validar sin romper /c/{slug}.
"""

from __future__ import annotations

import json
import os
from typing import Optional


def landing_v2_html(config: Optional[dict] = None) -> str:
    cfg = config or {}
    FB_PIXEL_ID = (os.environ.get("FB_PIXEL_ID") or "").strip()
    SITE_URL = (os.environ.get("PUBLIC_URL")
                or "https://gh-jurisprudencia-csj.onrender.com").rstrip("/")

    SLUG = cfg.get("slug") or ""
    H1 = cfg.get("h1") or "Te están negando un derecho"
    H1_RES = cfg.get("h1_resaltado") or ""
    SUBT = cfg.get("subtitulo") or (
        "Describe tu caso. Cruzamos tu situación con sentencias reales de la "
        "Corte Constitucional y te mostramos, en minutos, qué dice la ley y cuál es tu mejor camino."
    )
    CTA_TXT = cfg.get("cta_texto") or "Conocer mi caso"
    CASOS_CURADOS = cfg.get("casos_curados") or []
    FAQ_EXTRA = cfg.get("faq_extra") or []
    AREA_FOCUS = cfg.get("area_focus") or ""
    UTM_DEF = cfg.get("utm_default") or ""
    HERO_ICON = cfg.get("hero_icon") or "⚖️"
    ACCENT = cfg.get("color_acento") or "#C5A059"
    STATS_CUSTOM = cfg.get("stats_custom") or []
    TRUST_BLOCK = cfg.get("trust_block") or []
    FOOTER_EXTRA = cfg.get("footer_extra") or ""

    # H1 con resaltado en oro
    if H1_RES and H1_RES in H1:
        i = H1.find(H1_RES)
        H1_HTML = H1[:i] + f'<em class="acento">{H1_RES}</em>' + H1[i+len(H1_RES):]
    else:
        H1_HTML = H1

    # Eyebrow según slug
    EYEBROW_MAP = {
        "tutelas": "Acción de tutela · Decreto 2591/91",
        "accidentes": "SOAT · Ley 769/2002",
        "comparendos": "Debido proceso · C-038/2020",
        "laboral": "Derecho laboral · CST + Ley 361/97",
    }
    EYEBROW = EYEBROW_MAP.get(SLUG, "Derecho colombiano · jurisprudencia verificable")

    # Stats default si no hay custom
    STATS_DEFAULT = [
        {"num": "10 días", "label": "fallo legal máximo"},
        {"num": "+450", "label": "casos asistidos"},
        {"num": "94%", "label": "favorables"},
        {"num": "$0", "label": "sin cobro inicial"},
    ]
    STATS = STATS_CUSTOM if STATS_CUSTOM else STATS_DEFAULT

    # Trust default
    TRUST_DEFAULT = [
        {"title": "Autoridad real",
         "desc": "Citamos sentencias verificables de la Corte Constitucional y Suprema. Nunca inventamos."},
        {"title": "Sin costo oculto",
         "desc": "Borrador y consulta inicial sin cobro. Solo facturamos si tu caso requiere acompañamiento."},
        {"title": "Tus datos, tu control",
         "desc": "Habeas data Ley 1581/2012. Nunca compartimos tu información sin tu autorización expresa."},
    ]
    TRUST = TRUST_BLOCK if TRUST_BLOCK else TRUST_DEFAULT

    # FAQ default
    FAQ_DEFAULT = [
        {"q": "¿Cuánto tarda mi caso?",
         "a": "El juez constitucional tiene máximo 10 días hábiles para fallar (Decreto 2591/91, art. 29). Si hay perjuicio irremediable, pedimos medida provisional para protección inmediata."},
        {"q": "¿Necesito pagar algo para empezar?",
         "a": "No. El borrador inicial y la primera consulta son gratuitos. Solo cobramos si decides contratar acompañamiento procesal completo."},
        {"q": "¿Cómo sé que las sentencias citadas son reales?",
         "a": "Toda referencia se construye con un catálogo verificable de PDFs oficiales de la Corte. Puedes consultar el número de sentencia en la Relatoría de la Corte Constitucional."},
    ]
    FAQ_ALL = list(FAQ_EXTRA) + FAQ_DEFAULT

    # Casos curados - fallback con 3 genéricos si la landing no trae
    CASOS_DEFAULT = [
        {"ic": "🏥", "tt": "EPS niega autorización",
         "ds": "La Corte ha protegido el derecho a la salud cuando la EPS demora o niega cirugías y medicamentos.",
         "ej": "T-760/2008"},
        {"ic": "👴", "tt": "Pensión negada o demorada",
         "ds": "Colpensiones debe responder en 15 días. La tutela ordena respuesta de fondo o reconocimiento.",
         "ej": "T-082/2022"},
        {"ic": "🏛️", "tt": "Derecho de petición sin respuesta",
         "ds": "Toda entidad pública debe responder en 15 días hábiles. Si no, la tutela ordena respuesta en 48 horas.",
         "ej": "T-377/2000"},
    ]
    CASOS = CASOS_CURADOS if CASOS_CURADOS else CASOS_DEFAULT

    # Pixel Facebook
    fb_pixel = ""
    if FB_PIXEL_ID:
        fb_pixel = f"""<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{FB_PIXEL_ID}');fbq('track','PageView');</script>"""

    OG_TITLE = (cfg.get("title") or "Galeano Herrera | Abogados").strip()
    OG_DESC = SUBT[:160]
    OG_IMG = f"{SITE_URL}/og/{SLUG}.png" if SLUG else f"{SITE_URL}/og/default.png"

    # CASOS HTML
    casos_html = ""
    for c in CASOS[:9]:
        ic = c.get("ic") or "📌"
        tt = c.get("tt") or ""
        ds = c.get("ds") or ""
        ej = c.get("ej") or ""
        chip = f'<span class="chip-sentencia">{ej}</span>' if ej else ""
        casos_html += f"""
        <article class="caso-card">
          <div class="caso-ic">{ic}</div>
          <h3 class="caso-tt">{tt}</h3>
          <p class="caso-ds">{ds}</p>
          {chip}
        </article>"""

    # Stats HTML
    stats_html = ""
    for s in STATS:
        stats_html += f"""
        <div class="stat-item">
          <div class="stat-num">{s.get('num','')}</div>
          <div class="stat-lbl">{s.get('label','')}</div>
        </div>"""

    # Trust HTML
    trust_html = ""
    for t in TRUST:
        trust_html += f"""
        <article class="trust-card">
          <div class="trust-check">✓</div>
          <h3 class="trust-tt">{t.get('title','')}</h3>
          <p class="trust-ds">{t.get('desc','')}</p>
        </article>"""

    # FAQ HTML
    faq_html = ""
    for f in FAQ_ALL:
        faq_html += f"""
        <details class="faq-item">
          <summary class="faq-q">{f.get('q','')}</summary>
          <div class="faq-a">{f.get('a','')}</div>
        </details>"""

    utm_hidden = ""
    if UTM_DEF:
        utm_hidden = f'<input type="hidden" name="utm_default" value="{UTM_DEF}">'

    area_hidden = ""
    if AREA_FOCUS:
        area_hidden = f'<input type="hidden" name="area_focus" value="{AREA_FOCUS}">'

    # Microcopy bajo CTA
    MICROCOPY = "Atendido por María Camila · responde en 5 min · primera consulta gratuita"

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="index,follow">
<meta name="description" content="{OG_DESC}">
<title>{OG_TITLE}</title>
<link rel="canonical" href="{SITE_URL}/c/{SLUG}">

<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/c/{SLUG}">
<meta property="og:title" content="{OG_TITLE}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image" content="{OG_IMG}">
<meta name="twitter:card" content="summary_large_image">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {{
  --acento: {ACCENT};
  --acento-d: color-mix(in srgb, var(--acento) 80%, #000);
  --acento-soft: color-mix(in srgb, var(--acento) 12%, white);
  --acento-glow: color-mix(in srgb, var(--acento) 35%, transparent);

  --negro: #0A0A0A;
  --gris-900: #1F1F1F;
  --gris-700: #4A4A4A;
  --gris-500: #7B7B7B;
  --gris-300: #D4D4D4;
  --gris-200: #E8E8E8;
  --gris-100: #F4F4F2;
  --gris-50: #FAFAF8;
  --blanco: #FFFFFF;

  --azul-deep: #0F1E33;
  --ok: #16A34A;
  --warn: #C8102E;

  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Inter', system-ui, -apple-system, sans-serif;

  --r-sm: 10px;
  --r-md: 14px;
  --r-lg: 20px;
  --r-xl: 28px;
  --r-full: 999px;

  --sh-sm: 0 2px 4px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.02);
  --sh-md: 0 4px 12px rgba(0,0,0,.05), 0 2px 4px rgba(0,0,0,.03);
  --sh-lg: 0 12px 32px rgba(0,0,0,.07), 0 4px 8px rgba(0,0,0,.04);
  --sh-xl: 0 24px 64px rgba(15,30,51,.10), 0 8px 16px rgba(0,0,0,.04);
  --sh-glow: 0 8px 32px var(--acento-glow);

  --tr-fast: 120ms cubic-bezier(.4,0,.2,1);
  --tr: 180ms cubic-bezier(.4,0,.2,1);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }}
body {{
  font-family: var(--font-body);
  color: var(--negro);
  background: var(--blanco);
  line-height: 1.55;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}

img, svg {{ display: block; max-width: 100%; }}
a {{ color: inherit; text-decoration: none; transition: color var(--tr-fast); }}
button {{ font: inherit; cursor: pointer; }}

.container {{ max-width: 1140px; margin: 0 auto; padding: 0 24px; }}
.narrow {{ max-width: 820px; margin: 0 auto; padding: 0 24px; }}

/* ────────────────── NAV ────────────────── */
.nav {{
  position: sticky; top: 0; z-index: 50;
  background: rgba(255,255,255,.92);
  backdrop-filter: saturate(180%) blur(12px);
  -webkit-backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--gris-200);
}}
.nav-inner {{
  display: flex; align-items: center; justify-content: space-between;
  height: 64px;
}}
.brand {{
  display: flex; align-items: center; gap: 10px;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 18px;
  letter-spacing: -.01em;
  color: var(--negro);
}}
.brand-mark {{
  width: 32px; height: 32px; border-radius: var(--r-sm);
  background: var(--azul-deep);
  display: grid; place-items: center;
  color: var(--acento); font-size: 16px;
}}
.nav-cta {{
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 18px; border-radius: var(--r-full);
  background: var(--negro); color: var(--blanco);
  font-weight: 500; font-size: 14px;
  border: none; transition: transform var(--tr), background var(--tr);
}}
.nav-cta:hover {{ transform: translateY(-1px); background: var(--gris-900); }}

/* ────────────────── HERO ────────────────── */
.hero {{
  padding: 88px 0 64px;
  background: linear-gradient(180deg, var(--gris-50) 0%, var(--blanco) 70%);
  position: relative; overflow: hidden;
}}
.hero::before {{
  content: ""; position: absolute; top: -40%; right: -10%;
  width: 60%; height: 80%; pointer-events: none;
  background: radial-gradient(circle, var(--acento-soft) 0%, transparent 70%);
  opacity: .6;
}}
.eyebrow {{
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: var(--r-full);
  background: var(--blanco); border: 1px solid var(--gris-200);
  color: var(--gris-700); font-size: 13px; font-weight: 500;
  margin-bottom: 24px; box-shadow: var(--sh-sm);
}}
.eyebrow .dot {{
  width: 6px; height: 6px; border-radius: 50%; background: var(--acento);
}}
h1.hero-h {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: clamp(40px, 6vw, 68px);
  line-height: 1.05;
  letter-spacing: -.025em;
  color: var(--negro);
  max-width: 16ch;
  margin-bottom: 20px;
}}
h1.hero-h .acento {{
  color: var(--acento);
  font-style: italic;
  font-weight: 500;
}}
.hero-sub {{
  font-size: clamp(17px, 1.5vw, 19px);
  color: var(--gris-700);
  max-width: 56ch;
  margin-bottom: 36px;
}}
.cta-row {{
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  margin-bottom: 18px;
}}
.btn-primary {{
  display: inline-flex; align-items: center; gap: 10px;
  padding: 16px 28px;
  background: var(--acento); color: var(--negro);
  font-weight: 600; font-size: 16px;
  border: none; border-radius: var(--r-full);
  box-shadow: var(--sh-md);
  transition: transform var(--tr), box-shadow var(--tr), background var(--tr);
}}
.btn-primary:hover {{
  transform: translateY(-2px);
  background: var(--acento-d);
  box-shadow: var(--sh-glow);
}}
.btn-primary svg {{ transition: transform var(--tr); }}
.btn-primary:hover svg {{ transform: translateX(2px); }}

.btn-secondary {{
  display: inline-flex; align-items: center; gap: 8px;
  padding: 14px 22px;
  background: transparent; color: var(--negro);
  font-weight: 500; font-size: 15px;
  border: 1px solid var(--gris-300); border-radius: var(--r-full);
  transition: border var(--tr), background var(--tr);
}}
.btn-secondary:hover {{ border-color: var(--negro); background: var(--gris-50); }}

.microcopy {{
  font-size: 13px;
  color: var(--gris-500);
  display: flex; align-items: center; gap: 8px;
}}
.microcopy .live {{
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--ok); animation: pulse 2s infinite;
}}
@keyframes pulse {{
  0%, 100% {{ box-shadow: 0 0 0 0 rgba(22,163,74,.4); }}
  50% {{ box-shadow: 0 0 0 8px rgba(22,163,74,0); }}
}}

/* ────────────────── STATS BAR ────────────────── */
.stats-bar {{
  margin-top: 56px;
  padding: 28px 32px;
  background: var(--blanco);
  border: 1px solid var(--gris-200);
  border-radius: var(--r-lg);
  box-shadow: var(--sh-md);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 24px;
}}
.stat-item {{ text-align: center; }}
.stat-num {{
  font-family: var(--font-display);
  font-size: 32px; font-weight: 600;
  color: var(--negro);
  letter-spacing: -.02em;
  line-height: 1;
}}
.stat-lbl {{
  margin-top: 6px;
  font-size: 13px;
  color: var(--gris-500);
  font-weight: 500;
}}

/* ────────────────── SECCIONES ────────────────── */
section.block {{ padding: 96px 0; }}
section.block.alt {{ background: var(--gris-50); }}

.section-eyebrow {{
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .12em;
  color: var(--acento);
  margin-bottom: 12px;
}}
.section-h {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: clamp(28px, 3.5vw, 44px);
  line-height: 1.15;
  letter-spacing: -.02em;
  color: var(--negro);
  max-width: 24ch;
  margin-bottom: 16px;
}}
.section-sub {{
  font-size: 17px;
  color: var(--gris-700);
  max-width: 56ch;
  margin-bottom: 48px;
}}

/* ────────────────── CASOS ────────────────── */
.casos-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}}
.caso-card {{
  background: var(--blanco);
  border: 1px solid var(--gris-200);
  border-radius: var(--r-lg);
  padding: 28px 24px 24px;
  transition: transform var(--tr), box-shadow var(--tr), border var(--tr);
  display: flex; flex-direction: column;
  position: relative;
}}
.caso-card:hover {{
  transform: translateY(-4px);
  box-shadow: var(--sh-lg);
  border-color: var(--gris-300);
}}
.caso-ic {{
  font-size: 28px;
  width: 56px; height: 56px;
  display: grid; place-items: center;
  background: var(--acento-soft);
  border-radius: var(--r-md);
  margin-bottom: 16px;
}}
.caso-tt {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 19px;
  line-height: 1.3;
  letter-spacing: -.01em;
  margin-bottom: 10px;
  color: var(--negro);
}}
.caso-ds {{
  font-size: 14.5px;
  color: var(--gris-700);
  line-height: 1.55;
  flex: 1;
  margin-bottom: 16px;
}}
.chip-sentencia {{
  display: inline-flex; align-items: center;
  padding: 4px 10px;
  background: var(--gris-100);
  border: 1px solid var(--gris-200);
  border-radius: var(--r-sm);
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px;
  font-weight: 500;
  color: var(--gris-700);
  align-self: flex-start;
}}

/* ────────────────── COMO FUNCIONA ────────────────── */
.steps {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  counter-reset: step;
}}
@media (max-width: 760px) {{ .steps {{ grid-template-columns: 1fr; }} }}
.step {{
  position: relative;
  padding: 32px 24px 28px;
  background: var(--blanco);
  border-radius: var(--r-lg);
  border: 1px solid var(--gris-200);
}}
.step::before {{
  counter-increment: step;
  content: "0" counter(step);
  font-family: var(--font-display);
  font-weight: 500;
  font-size: 48px;
  color: var(--acento);
  line-height: 1;
  letter-spacing: -.03em;
  position: absolute;
  top: 24px; right: 28px;
  opacity: .35;
}}
.step h3 {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 20px;
  letter-spacing: -.01em;
  margin-bottom: 10px;
  color: var(--negro);
  max-width: 90%;
}}
.step p {{
  font-size: 14.5px;
  color: var(--gris-700);
  line-height: 1.6;
}}

/* ────────────────── TRUST ────────────────── */
.trust-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}}
.trust-card {{
  background: var(--blanco);
  padding: 32px 28px;
  border-radius: var(--r-lg);
  border: 1px solid var(--gris-200);
}}
.trust-check {{
  width: 36px; height: 36px;
  background: var(--ok);
  color: var(--blanco);
  border-radius: var(--r-full);
  display: grid; place-items: center;
  font-weight: 700;
  font-size: 16px;
  margin-bottom: 16px;
}}
.trust-tt {{
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 19px;
  color: var(--negro);
  margin-bottom: 8px;
}}
.trust-ds {{
  font-size: 14.5px;
  color: var(--gris-700);
}}

/* ────────────────── FORMULARIO ────────────────── */
.form-card {{
  background: var(--blanco);
  padding: 48px;
  border-radius: var(--r-xl);
  border: 1px solid var(--gris-200);
  box-shadow: var(--sh-xl);
  max-width: 720px; margin: 0 auto;
}}
@media (max-width: 600px) {{ .form-card {{ padding: 32px 24px; }} }}
.form-row {{ display: grid; gap: 16px; margin-bottom: 16px; }}
.form-row.two {{ grid-template-columns: 1fr 1fr; }}
@media (max-width: 540px) {{ .form-row.two {{ grid-template-columns: 1fr; }} }}
.field label {{
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--gris-700);
  margin-bottom: 6px;
}}
.field input, .field textarea {{
  width: 100%;
  padding: 13px 14px;
  border: 1px solid var(--gris-200);
  border-radius: var(--r-sm);
  font-family: var(--font-body);
  font-size: 15px;
  color: var(--negro);
  background: var(--blanco);
  transition: border var(--tr), box-shadow var(--tr);
}}
.field input:focus, .field textarea:focus {{
  outline: none;
  border-color: var(--acento);
  box-shadow: 0 0 0 3px var(--acento-soft);
}}
.field textarea {{ resize: vertical; min-height: 110px; line-height: 1.55; }}
.consent-row {{
  display: flex; gap: 10px;
  font-size: 13px; color: var(--gris-700);
  padding: 14px;
  background: var(--gris-50);
  border-radius: var(--r-sm);
  margin: 18px 0;
}}
.consent-row input {{ margin-top: 2px; flex-shrink: 0; }}
.consent-row a {{ color: var(--acento-d); text-decoration: underline; }}

.btn-submit {{
  width: 100%;
  padding: 18px;
  background: var(--acento);
  color: var(--negro);
  border: none;
  border-radius: var(--r-md);
  font-size: 16px; font-weight: 600;
  cursor: pointer;
  transition: transform var(--tr), background var(--tr), box-shadow var(--tr);
}}
.btn-submit:hover {{
  background: var(--acento-d);
  transform: translateY(-1px);
  box-shadow: var(--sh-glow);
}}
.btn-submit:disabled {{ opacity: .6; cursor: not-allowed; transform: none; }}

#preview-out {{ margin-top: 28px; }}
.preview-card {{
  background: var(--gris-50);
  border-left: 4px solid var(--acento);
  padding: 24px;
  border-radius: var(--r-md);
  font-family: var(--font-display);
  font-size: 15.5px;
  color: var(--gris-900);
  white-space: pre-wrap;
  line-height: 1.65;
  max-height: 480px;
  overflow-y: auto;
}}

/* ────────────────── FAQ ────────────────── */
.faq-list {{ max-width: 760px; margin: 0 auto; }}
.faq-item {{
  background: var(--blanco);
  border: 1px solid var(--gris-200);
  border-radius: var(--r-md);
  margin-bottom: 12px;
  overflow: hidden;
  transition: border var(--tr), box-shadow var(--tr);
}}
.faq-item:hover {{ border-color: var(--gris-300); }}
.faq-item[open] {{ box-shadow: var(--sh-md); border-color: var(--acento); }}
.faq-q {{
  padding: 20px 24px;
  font-weight: 600;
  font-size: 15.5px;
  color: var(--negro);
  cursor: pointer;
  list-style: none;
  display: flex; justify-content: space-between; align-items: center;
}}
.faq-q::-webkit-details-marker {{ display: none; }}
.faq-q::after {{
  content: "+";
  font-size: 22px;
  color: var(--gris-500);
  transition: transform var(--tr);
  font-weight: 300;
}}
.faq-item[open] .faq-q::after {{ transform: rotate(45deg); color: var(--acento); }}
.faq-a {{
  padding: 0 24px 22px;
  font-size: 14.5px;
  color: var(--gris-700);
  line-height: 1.65;
}}

/* ────────────────── FOOTER ────────────────── */
footer.foot {{
  background: var(--azul-deep);
  color: var(--gris-300);
  padding: 64px 0 32px;
  margin-top: 0;
}}
.foot-grid {{
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 48px;
  margin-bottom: 48px;
}}
@media (max-width: 720px) {{ .foot-grid {{ grid-template-columns: 1fr; gap: 32px; }} }}
.foot-brand .brand {{ color: var(--blanco); margin-bottom: 14px; }}
.foot-brand .brand-mark {{ background: var(--blanco); color: var(--azul-deep); }}
.foot-brand p {{ font-size: 14px; color: var(--gris-300); max-width: 38ch; }}
.foot-col h4 {{
  font-size: 12px; text-transform: uppercase; letter-spacing: .12em;
  font-weight: 600; color: var(--blanco); margin-bottom: 14px;
}}
.foot-col a {{ display: block; font-size: 14px; color: var(--gris-300); padding: 4px 0; }}
.foot-col a:hover {{ color: var(--acento); }}
.foot-legal {{
  padding-top: 24px;
  border-top: 1px solid rgba(255,255,255,.08);
  font-size: 12px; color: rgba(255,255,255,.5);
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}}

/* ────────────────── HELPERS ────────────────── */
.hide {{ display: none !important; }}
.spinner {{
  display: inline-block; width: 16px; height: 16px;
  border: 2px solid currentColor; border-top-color: transparent;
  border-radius: 50%; animation: spin .7s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>

{fb_pixel}
</head>
<body>

<header class="nav">
  <div class="container nav-inner">
    <a href="/" class="brand">
      <span class="brand-mark">⚖</span>
      <span>Galeano Herrera <strong style="font-weight:500;color:var(--gris-500)">Abogados</strong></span>
    </a>
    <a href="#empezar" class="nav-cta">Empezar ahora →</a>
  </div>
</header>

<!-- HERO -->
<section class="hero">
  <div class="container">
    <span class="eyebrow"><span class="dot"></span>{EYEBROW}</span>
    <h1 class="hero-h">{H1_HTML}.</h1>
    <p class="hero-sub">{SUBT}</p>
    <div class="cta-row">
      <a href="#empezar" class="btn-primary">
        {CTA_TXT}
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </a>
      <a href="#casos" class="btn-secondary">Ver casos resueltos</a>
    </div>
    <div class="microcopy"><span class="live"></span> {MICROCOPY}</div>

    <div class="stats-bar">{stats_html}</div>
  </div>
</section>

<!-- CASOS -->
<section class="block alt" id="casos">
  <div class="container">
    <div class="section-eyebrow">Casos resueltos</div>
    <h2 class="section-h">Los problemas que solucionamos esta semana</h2>
    <p class="section-sub">Cada caso enlaza con sentencias verificables de la Corte. Cero invención.</p>
    <div class="casos-grid">{casos_html}</div>
  </div>
</section>

<!-- COMO FUNCIONA -->
<section class="block">
  <div class="container">
    <div class="section-eyebrow">Cómo funciona</div>
    <h2 class="section-h">De tu duda a un documento con respaldo jurídico en minutos</h2>
    <p class="section-sub">Tres pasos. Ningún papeleo. Sin cobro inicial.</p>
    <div class="steps">
      <div class="step">
        <h3>Cuéntanos qué te pasa</h3>
        <p>Llenas el formulario con tu situación en lenguaje natural. No necesitas vocabulario jurídico.</p>
      </div>
      <div class="step">
        <h3>Generamos tu caso</h3>
        <p>La IA del despacho cruza tu situación con sentencias reales de la Corte y arma el borrador.</p>
      </div>
      <div class="step">
        <h3>Hablas con un abogado</h3>
        <p>Te contactamos por WhatsApp para revisar el documento contigo y decidir cómo proceder.</p>
      </div>
    </div>
  </div>
</section>

<!-- FORMULARIO -->
<section class="block alt" id="empezar">
  <div class="container">
    <div class="section-eyebrow">Empezar</div>
    <h2 class="section-h" style="margin:0 auto 16px;text-align:center">Cuéntanos tu caso</h2>
    <p class="section-sub" style="margin:0 auto 40px;text-align:center">Empezamos en 2 minutos. Primera consulta gratuita.</p>

    <div class="form-card">
      <form id="lead-form">
        <div class="form-row two">
          <div class="field"><label for="nombre">Tu nombre completo</label><input id="nombre" name="nombre" required placeholder="Ej: Juan Pérez González"></div>
          <div class="field"><label for="cedula">Cédula</label><input id="cedula" name="cedula" required placeholder="Ej: 1018456789"></div>
        </div>
        <div class="form-row two">
          <div class="field"><label for="ciudad">Ciudad</label><input id="ciudad" name="ciudad" required placeholder="Bogotá D.C."></div>
          <div class="field"><label for="phone">WhatsApp</label><input id="phone" name="phone" required placeholder="3001112233"></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="descripcion">¿Qué te está pasando?</label>
            <textarea id="descripcion" name="descripcion" required placeholder="Cuéntanos brevemente: qué entidad o persona te está afectando, desde cuándo, qué has intentado..."></textarea></div>
        </div>
        {area_hidden}
        {utm_hidden}
        <input type="hidden" name="slug" value="{SLUG}">
        <label class="consent-row">
          <input type="checkbox" id="consent" required>
          <span>Autorizo el tratamiento de mis datos personales conforme a la <a href="#" target="_blank">Política de Privacidad</a> (Ley 1581/2012), para que un abogado del despacho me contacte y para generar el borrador de mi caso.</span>
        </label>
        <button type="submit" class="btn-submit" id="btn-submit">
          <span class="btn-label">Generar mi caso →</span>
        </button>
      </form>
      <div id="preview-out"></div>
    </div>
  </div>
</section>

<!-- TRUST -->
<section class="block">
  <div class="container">
    <div class="section-eyebrow">Por qué confiar</div>
    <h2 class="section-h">Lo que nos hace diferente</h2>
    <div class="trust-grid">{trust_html}</div>
  </div>
</section>

<!-- FAQ -->
<section class="block alt">
  <div class="container">
    <div style="text-align:center;margin-bottom:48px">
      <div class="section-eyebrow">Preguntas frecuentes</div>
      <h2 class="section-h" style="margin:0 auto 16px">Lo que casi todos nos preguntan</h2>
    </div>
    <div class="faq-list">{faq_html}</div>
  </div>
</section>

<!-- FOOTER -->
<footer class="foot">
  <div class="container">
    <div class="foot-grid">
      <div class="foot-brand">
        <div class="brand"><span class="brand-mark">⚖</span><span>Galeano Herrera Abogados</span></div>
        <p>Despacho jurídico colombiano. Tutela, derecho laboral, accidentes de tránsito y comparendos con jurisprudencia auditable.</p>
      </div>
      <div class="foot-col">
        <h4>Servicios</h4>
        <a href="/c/tutelas">Tutelas</a>
        <a href="/c/accidentes">Accidentes / SOAT</a>
        <a href="/c/comparendos">Comparendos</a>
        <a href="/c/laboral">Laboral</a>
      </div>
      <div class="foot-col">
        <h4>Despacho</h4>
        <a href="https://wa.me/573195742278">WhatsApp +57 319 574 22 78</a>
        <a href="#">Contacto</a>
        <a href="#">Habeas data</a>
      </div>
    </div>
    <div class="foot-legal">
      <span>© Galeano Herrera Abogados · Bogotá D.C., Colombia</span>
      <span>{FOOTER_EXTRA or 'Acción de tutela · Decreto 2591/91 · Constitución Política art. 86'}</span>
    </div>
  </div>
</footer>

<script>
const form = document.getElementById('lead-form');
const out = document.getElementById('preview-out');
const btn = document.getElementById('btn-submit');
const btnLabel = btn.querySelector('.btn-label');

form.addEventListener('submit', async (ev) => {{
  ev.preventDefault();
  if (!document.getElementById('consent').checked) {{
    alert('Necesitas aceptar el tratamiento de datos para continuar.');
    return;
  }}
  btn.disabled = true;
  btnLabel.innerHTML = '<span class="spinner"></span> Generando tu borrador…';
  out.innerHTML = '';

  const data = Object.fromEntries(new FormData(form).entries());
  try {{
    const r = await fetch('/api/lead/preview', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{
        nombre: data.nombre, cedula: data.cedula, ciudad: data.ciudad,
        phone: data.phone, email: '', descripcion: data.descripcion,
        landing_slug: data.slug || '{SLUG}',
      }}),
    }});
    if (!r.ok) {{
      const e = await r.text();
      out.innerHTML = '<div class="preview-card" style="border-color:var(--warn)">' + e.slice(0,300) + '</div>';
      btn.disabled = false; btnLabel.textContent = 'Reintentar';
      return;
    }}
    const j = await r.json();
    out.innerHTML = '<h3 class="section-h" style="font-size:24px;margin:32px 0 16px;text-align:left;max-width:100%">Tu borrador preliminar</h3>' +
      '<div class="preview-card">' + (j.preview || j.borrador || '(sin preview)') + '</div>' +
      '<p style="font-size:13px;color:var(--gris-500);margin-top:14px">Este es un borrador de orientación. Un abogado humano del despacho te contactará para revisarlo y decidir cómo proceder.</p>';
    btn.disabled = false; btnLabel.textContent = 'Pedir contacto del abogado';
    if (window.fbq) fbq('track','Lead');
  }} catch(e) {{
    out.innerHTML = '<div class="preview-card" style="border-color:var(--warn)">Error: ' + e.message + '</div>';
    btn.disabled = false; btnLabel.textContent = 'Reintentar';
  }}
}});
</script>

</body></html>"""
