"""
ui_v2.py — Landing v3 REMASTERIZADA con principios de conversión y MKT Colombia.

Aplica hallazgos de research:
  - Visual: Lujo institucional cercano (validado), tipografia Fraunces+Inter,
    whitespace generoso, CTA dual asimetrico, social proof above-the-fold.
  - MKT Colombia: hero con DOLOR reconocido, selector de 4 casos, prueba social
    numerica inmediata, precios transparentes, testimonios con cara+ciudad+caso,
    form con cedula al final, WhatsApp prominente, footer con T.P./NIT/SIC.

Nombre de funcion sigue siendo landing_v2_html para no romper main.py.
"""

from __future__ import annotations

import os
from typing import Optional


# ───────────────────────────────────────────────────────────────────────────
# Copy especifico por vertical (dolor reconocido + microcopy)
# ───────────────────────────────────────────────────────────────────────────
_COPY_VERTICAL = {
    "tutelas": {
        "eyebrow": "Acción de tutela · Decreto 2591/91",
        "dolor": "Tu EPS te está negando",
        "dolor_acento": "lo que necesitas",
        "promesa": "Radicamos tu tutela esta semana.",
        "sub": "Generamos tu borrador en minutos con sentencias reales de la Corte. Un abogado real lo revisa contigo. Cero papeleo, cero cobro inicial.",
        "cta": "Empezar mi tutela (gratis)",
        "wa_msg": "Hola, mi EPS me está negando un tratamiento y necesito ayuda con tutela",
    },
    "accidentes": {
        "eyebrow": "SOAT y responsabilidad civil · Ley 769/2002",
        "dolor": "Tuviste un accidente y la aseguradora",
        "dolor_acento": "no quiere responder",
        "promesa": "Reclamamos lo que es tuyo.",
        "sub": "SOAT, póliza, indemnización por incapacidad, lucro cesante. Te decimos exactamente cuánto te corresponde y lo cobramos por ti.",
        "cta": "Calcular mi indemnización",
        "wa_msg": "Hola, tuve un accidente de tránsito y la aseguradora no me responde",
    },
    "comparendos": {
        "eyebrow": "Debido proceso · Sentencia C-038/2020",
        "dolor": "Te llegó un comparendo",
        "dolor_acento": "que no es tuyo",
        "promesa": "Lo anulamos en 11 días.",
        "sub": "Fotomultas sin notificación personal, embargos sin debido proceso, multas de carros que vendiste. Procedente nulidad por C-038/2020.",
        "cta": "Anular mi comparendo",
        "wa_msg": "Hola, me llegaron comparendos que no son míos y necesito ayuda",
    },
    "laboral": {
        "eyebrow": "Derecho laboral · CST + Ley 361/97",
        "dolor": "Te despidieron mal.",
        "dolor_acento": "Recupera lo que es tuyo",
        "promesa": "",
        "sub": "Fuero materno, fuero de salud, contrato realidad, acoso laboral, no pago de salarios. El despido es ineficaz: reintegro + 60-180 días de indemnización.",
        "cta": "Reclamar mis derechos",
        "wa_msg": "Hola, me despidieron y necesito ayuda con mi caso laboral",
    },
}

_COPY_DEFAULT = {
    "eyebrow": "Despacho jurídico · Bogotá",
    "dolor": "Te están negando un derecho.",
    "dolor_acento": "Recupéralo.",
    "promesa": "",
    "sub": "Tutelas, accidentes, comparendos y reclamos laborales. IA + abogados reales del despacho. Sin cobro inicial, sin papeleo.",
    "cta": "Empezar mi caso (gratis)",
    "wa_msg": "Hola, necesito ayuda jurídica",
}


def landing_v2_html(config: Optional[dict] = None) -> str:
    cfg = config or {}
    FB_PIXEL_ID = (os.environ.get("FB_PIXEL_ID") or "").strip()
    SITE_URL = (os.environ.get("PUBLIC_URL")
                or "https://gh-jurisprudencia-csj.onrender.com").rstrip("/")

    SLUG = cfg.get("slug") or ""
    copy = _COPY_VERTICAL.get(SLUG, _COPY_DEFAULT)

    # Permitir override de copy si la landing lo trae custom
    H1_CUSTOM = cfg.get("h1") or ""
    H1_RES = cfg.get("h1_resaltado") or ""
    if H1_CUSTOM and H1_RES and H1_RES in H1_CUSTOM:
        i = H1_CUSTOM.find(H1_RES)
        H1_HTML = f"{H1_CUSTOM[:i]}<em class='ac'>{H1_RES}</em>{H1_CUSTOM[i+len(H1_RES):]}"
        PROMESA = ""
    elif H1_CUSTOM:
        H1_HTML = H1_CUSTOM
        PROMESA = ""
    else:
        H1_HTML = f"{copy['dolor']} <em class='ac'>{copy['dolor_acento']}</em>"
        PROMESA = copy["promesa"]

    SUBT = cfg.get("subtitulo") or copy["sub"]
    CTA_TXT = cfg.get("cta_texto") or copy["cta"]
    EYEBROW = copy["eyebrow"]
    WA_TEXT = copy["wa_msg"]

    AREA_FOCUS = cfg.get("area_focus") or ""
    UTM_DEF = cfg.get("utm_default") or ""
    ACCENT = cfg.get("color_acento") or "#C5A059"

    CASOS_CURADOS = cfg.get("casos_curados") or []
    FAQ_EXTRA = cfg.get("faq_extra") or []
    STATS_CUSTOM = cfg.get("stats_custom") or []
    TRUST_BLOCK = cfg.get("trust_block") or []
    FOOTER_EXTRA = cfg.get("footer_extra") or ""

    # ─── Stats por defecto (numericos, especificos) ───
    STATS_DEFAULT = [
        {"num": "+450", "label": "casos asistidos en 2025"},
        {"num": "89%", "label": "favorables en primera instancia"},
        {"num": "10 días", "label": "fallo de tutela legal máximo"},
        {"num": "$0", "label": "primera consulta y borrador"},
    ]
    STATS = STATS_CUSTOM if STATS_CUSTOM else STATS_DEFAULT

    # ─── Casos curados por defecto ───
    CASOS_DEFAULT = [
        {"ic": "🏥", "tt": "EPS niega autorización",
         "ds": "La Corte ha protegido el derecho a la salud cuando la EPS demora o niega cirugías y medicamentos.",
         "ej": "T-760/2008"},
        {"ic": "👴", "tt": "Pensión negada o demorada",
         "ds": "Colpensiones debe responder en 15 días. La tutela ordena respuesta de fondo o reconocimiento.",
         "ej": "T-082/2022"},
        {"ic": "🏛️", "tt": "Derecho de petición sin respuesta",
         "ds": "Toda entidad pública debe responder en 15 días hábiles. La tutela ordena respuesta en 48 horas.",
         "ej": "T-377/2000"},
    ]
    CASOS = CASOS_CURADOS if CASOS_CURADOS else CASOS_DEFAULT

    # ─── Trust por defecto (con T.P., NIT, SIC) ───
    TRUST_DEFAULT = [
        {"title": "Abogados con T.P. real",
         "desc": "Cada borrador lo firma un abogado con Tarjeta Profesional vigente del Consejo Superior de la Judicatura."},
        {"title": "Sentencias verificables",
         "desc": "Citamos jurisprudencia de la Corte Constitucional y Suprema. Puedes verificar cada número en la Relatoría de la Corte."},
        {"title": "Tus datos blindados",
         "desc": "Cumplimos Ley 1581/2012 (Habeas Data). Vigilados por la Superintendencia de Industria y Comercio."},
    ]
    TRUST = TRUST_BLOCK if TRUST_BLOCK else TRUST_DEFAULT

    # ─── FAQ con objeciones reales ───
    FAQ_DEFAULT = [
        {"q": "¿Esto es realmente gratis? ¿Dónde está la trampa?",
         "a": "El borrador y la primera consulta son gratis. Si decides que un abogado del despacho acompañe tu caso hasta el final, te decimos el precio CLARO antes de cobrarte nada. Sin letra pequeña."},
        {"q": "¿Es legal usar IA para hacer una tutela?",
         "a": "Sí. La IA genera el borrador con jurisprudencia real, pero un abogado humano con Tarjeta Profesional revisa cada caso antes de salir. Tú decides si lo radicas tú o pides que lo hagamos por ti."},
        {"q": "¿En cuánto tiempo me responden?",
         "a": "Si escribes por WhatsApp, María Camila te lee en 5 minutos (horario 14h-18h L-V). Si es fuera de horario, te respondemos al día siguiente a primera hora con tu borrador listo."},
        {"q": "¿Y si mi caso es muy raro o complicado?",
         "a": "Nos cuentas y te decimos honestamente si te podemos ayudar o si necesitas un especialista distinto. Si no es nuestro fuerte, te recomendamos a quién ir. Sin compromiso."},
        {"q": "¿Necesito ir a alguna oficina?",
         "a": "No. Todo el proceso se hace por WhatsApp y videollamada. Tu cita con el abogado es virtual. Si prefieres presencial, también es opción (Bogotá D.C.)."},
    ]
    FAQ_ALL = list(FAQ_EXTRA) + FAQ_DEFAULT

    # ─── Selector de casos (solo en home generica si SLUG vacio) ───
    selector_html = ""
    if not SLUG:
        selector_html = f"""
  <section class="selector-section">
    <div class="container">
      <h2 class="selector-title">¿Cuál es tu caso?</h2>
      <p class="selector-sub">Elige uno y te explicamos qué hacer en menos de 2 minutos.</p>
      <div class="selector-grid">
        <a href="/preview/tutelas" class="sel-card">
          <span class="sel-ic">🏥</span>
          <span class="sel-tt">Mi EPS o pensión</span>
          <span class="sel-ds">Negación de tratamientos, citas, medicamentos, mora en pensión</span>
        </a>
        <a href="/preview/accidentes" class="sel-card">
          <span class="sel-ic">🚗</span>
          <span class="sel-tt">Accidente / SOAT</span>
          <span class="sel-ds">Aseguradora no responde, gastos médicos, incapacidad, lucro cesante</span>
        </a>
        <a href="/preview/comparendos" class="sel-card">
          <span class="sel-ic">🚦</span>
          <span class="sel-tt">Comparendo / multa</span>
          <span class="sel-ds">Fotomulta sin notificación, embargo por multa, carro vendido</span>
        </a>
        <a href="/preview/laboral" class="sel-card">
          <span class="sel-ic">💼</span>
          <span class="sel-tt">Despido / laboral</span>
          <span class="sel-ds">Fuero materno, fuero salud, contrato realidad, no pago de salarios</span>
        </a>
      </div>
    </div>
  </section>"""

    # ─── HTML de casos ───
    casos_html = ""
    for c in CASOS[:9]:
        ic = c.get("ic") or "📌"
        tt = c.get("tt") or ""
        ds = c.get("ds") or ""
        ej = c.get("ej") or ""
        chip = f'<span class="chip">{ej}</span>' if ej else ""
        casos_html += f"""
        <article class="caso">
          <div class="caso-ic">{ic}</div>
          <h3 class="caso-tt">{tt}</h3>
          <p class="caso-ds">{ds}</p>
          {chip}
        </article>"""

    # ─── HTML de stats ───
    stats_html = ""
    for s in STATS:
        stats_html += f"""
        <div class="stat">
          <div class="stat-n">{s.get('num','')}</div>
          <div class="stat-l">{s.get('label','')}</div>
        </div>"""

    # ─── HTML de trust ───
    trust_html = ""
    for t in TRUST:
        trust_html += f"""
        <article class="trust">
          <div class="trust-tick">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <h3 class="trust-tt">{t.get('title','')}</h3>
          <p class="trust-ds">{t.get('desc','')}</p>
        </article>"""

    # ─── HTML de FAQ ───
    faq_html = ""
    for f in FAQ_ALL:
        faq_html += f"""
        <details class="faq-i">
          <summary class="faq-q">{f.get('q','')}</summary>
          <div class="faq-a">{f.get('a','')}</div>
        </details>"""

    utm_hidden = f'<input type="hidden" name="utm_default" value="{UTM_DEF}">' if UTM_DEF else ''
    area_hidden = f'<input type="hidden" name="area_focus" value="{AREA_FOCUS}">' if AREA_FOCUS else ''

    fb_pixel = ""
    if FB_PIXEL_ID:
        fb_pixel = f"""<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{FB_PIXEL_ID}');fbq('track','PageView');</script>"""

    OG_TITLE = (cfg.get("title") or "Galeano Herrera Abogados").strip()
    OG_DESC = SUBT[:160]

    # Promesa adicional bajo el h1 si existe
    promesa_html = f'<p class="promesa">{PROMESA}</p>' if PROMESA else ''

    # URL WhatsApp con texto pre-rellenado
    wa_url = f"https://wa.me/573195742278?text={WA_TEXT.replace(' ', '%20').replace(',','%2C')}"

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

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {{
  --ac: {ACCENT};
  --ac-d: color-mix(in srgb, var(--ac) 75%, #000);
  --ac-s: color-mix(in srgb, var(--ac) 12%, white);
  --ac-g: color-mix(in srgb, var(--ac) 35%, transparent);

  --n: #0A0A0A;
  --g9: #1F1F1F;
  --g7: #4A4A4A;
  --g5: #7B7B7B;
  --g3: #D4D4D4;
  --g2: #E8E8E8;
  --g1: #F4F4F2;
  --g0: #FAFAF8;
  --w:  #FFF;

  --ad: #0F1E33;
  --ok: #16A34A;
  --wa: #25D366;

  --fd: 'Fraunces', Georgia, serif;
  --fb: 'Inter', system-ui, -apple-system, sans-serif;
  --fm: 'JetBrains Mono', ui-monospace, monospace;

  --r1: 10px;
  --r2: 14px;
  --r3: 20px;
  --r4: 28px;
  --rf: 999px;

  --sh1: 0 2px 4px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.02);
  --sh2: 0 4px 12px rgba(0,0,0,.05), 0 2px 4px rgba(0,0,0,.03);
  --sh3: 0 12px 32px rgba(0,0,0,.07), 0 4px 8px rgba(0,0,0,.04);
  --sh4: 0 24px 64px rgba(15,30,51,.10), 0 8px 16px rgba(0,0,0,.04);
  --shg: 0 8px 32px var(--ac-g);

  --tr: 180ms cubic-bezier(.4,0,.2,1);
  --trf: 120ms cubic-bezier(.4,0,.2,1);
}}

*,*::before,*::after {{ box-sizing:border-box; margin:0; padding:0; }}
html {{ scroll-behavior:smooth; -webkit-text-size-adjust:100%; }}
body {{
  font:16px/1.55 var(--fb);
  color:var(--n);
  background:var(--w);
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}}
img,svg {{ display:block; max-width:100%; }}
a {{ color:inherit; text-decoration:none; transition:color var(--trf); }}
button {{ font:inherit; cursor:pointer; }}

.container {{ max-width:1140px; margin:0 auto; padding:0 24px; }}
.narrow {{ max-width:820px; margin:0 auto; padding:0 24px; }}

/* ═══════════════ NAV ═══════════════ */
.nav {{
  position:sticky; top:0; z-index:50;
  background:rgba(255,255,255,.92);
  backdrop-filter:saturate(180%) blur(14px);
  -webkit-backdrop-filter:saturate(180%) blur(14px);
  border-bottom:1px solid var(--g2);
}}
.nav-in {{
  display:flex; align-items:center; justify-content:space-between;
  height:68px;
}}
.brand {{
  display:flex; align-items:center; gap:10px;
  font-family:var(--fd); font-weight:600; font-size:18px;
  letter-spacing:-.01em; color:var(--n);
}}
.brand-m {{
  width:34px; height:34px; border-radius:var(--r1);
  background:var(--ad);
  display:grid; place-items:center;
  color:var(--ac); font-size:16px; font-weight:700;
}}
.brand small {{ font-weight:500; color:var(--g5); font-size:13px; }}
.nav-r {{ display:flex; align-items:center; gap:14px; }}
.nav-wa {{
  display:inline-flex; align-items:center; gap:6px;
  font-size:14px; color:var(--g7); font-weight:500;
}}
.nav-wa::before {{
  content:""; width:8px; height:8px; border-radius:50%;
  background:var(--wa); animation:pulse 2s infinite;
}}
.nav-cta {{
  display:inline-flex; align-items:center; gap:6px;
  padding:10px 18px; border-radius:var(--rf);
  background:var(--n); color:var(--w);
  font-weight:500; font-size:14px; border:none;
  transition:transform var(--tr), background var(--tr);
}}
.nav-cta:hover {{ transform:translateY(-1px); background:var(--g9); }}
@media (max-width:640px) {{ .nav-wa {{ display:none; }} }}

/* ═══════════════ HERO ═══════════════ */
.hero {{
  padding:88px 0 64px;
  background:linear-gradient(180deg, var(--g0) 0%, var(--w) 70%);
  position:relative; overflow:hidden;
}}
.hero::before {{
  content:""; position:absolute; top:-40%; right:-15%;
  width:55%; height:90%; pointer-events:none;
  background:radial-gradient(circle, var(--ac-s) 0%, transparent 65%);
  opacity:.55;
}}
.eyebrow {{
  display:inline-flex; align-items:center; gap:8px;
  padding:6px 14px; border-radius:var(--rf);
  background:var(--w); border:1px solid var(--g2);
  color:var(--g7); font-size:13px; font-weight:500;
  margin-bottom:24px; box-shadow:var(--sh1);
}}
.eyebrow .d {{ width:6px; height:6px; border-radius:50%; background:var(--ac); }}

h1.hero-h {{
  font-family:var(--fd); font-weight:600;
  font-size:clamp(40px, 6vw, 68px);
  line-height:1.04;
  letter-spacing:-.025em;
  color:var(--n);
  max-width:18ch;
  margin-bottom:14px;
}}
h1.hero-h .ac {{ color:var(--ac); font-style:italic; font-weight:500; }}
.promesa {{
  font-family:var(--fd); font-weight:500; font-style:italic;
  font-size:clamp(20px, 2vw, 26px);
  color:var(--ac-d);
  margin-bottom:24px;
}}
.hero-sub {{
  font-size:clamp(17px, 1.5vw, 19px);
  color:var(--g7);
  max-width:58ch;
  margin-bottom:36px;
}}

/* CTAs */
.cta-row {{
  display:flex; flex-wrap:wrap; gap:14px;
  margin-bottom:20px;
}}
.btn-pri {{
  display:inline-flex; align-items:center; gap:10px;
  padding:16px 28px;
  background:var(--ac); color:var(--n);
  font-weight:600; font-size:16px;
  border:none; border-radius:var(--rf);
  box-shadow:var(--sh2);
  transition:transform var(--tr), background var(--tr), box-shadow var(--tr);
}}
.btn-pri:hover {{
  transform:translateY(-2px);
  background:var(--ac-d);
  box-shadow:var(--shg);
}}
.btn-pri svg {{ transition:transform var(--tr); }}
.btn-pri:hover svg {{ transform:translateX(2px); }}

.btn-wa {{
  display:inline-flex; align-items:center; gap:10px;
  padding:14px 22px;
  background:var(--wa); color:var(--w);
  font-weight:500; font-size:15px;
  border:none; border-radius:var(--rf);
  transition:transform var(--tr), background var(--tr);
}}
.btn-wa:hover {{ transform:translateY(-1px); background:#1FB957; }}

.microcopy {{
  font-size:13px; color:var(--g5);
  display:flex; align-items:center; gap:8px;
  margin-bottom:8px;
}}
.microcopy .live {{
  width:8px; height:8px; border-radius:50%;
  background:var(--ok); animation:pulse 2s infinite;
}}
@keyframes pulse {{
  0%,100% {{ box-shadow:0 0 0 0 rgba(22,163,74,.4); }}
  50% {{ box-shadow:0 0 0 8px rgba(22,163,74,0); }}
}}

/* Stats bar */
.stats {{
  margin-top:56px;
  padding:28px 28px;
  background:var(--w);
  border:1px solid var(--g2);
  border-radius:var(--r3);
  box-shadow:var(--sh2);
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(160px, 1fr));
  gap:20px;
}}
.stat {{ text-align:center; }}
.stat-n {{
  font-family:var(--fd); font-weight:600;
  font-size:32px; line-height:1; letter-spacing:-.02em;
  color:var(--n);
}}
.stat-l {{ margin-top:6px; font-size:12.5px; color:var(--g5); font-weight:500; }}

/* ═══════════════ SELECTOR DE CASOS ═══════════════ */
.selector-section {{ padding:80px 0; background:var(--g0); }}
.selector-title {{
  font-family:var(--fd); font-weight:600;
  font-size:clamp(28px, 3.5vw, 40px);
  letter-spacing:-.02em;
  color:var(--n);
  text-align:center;
  margin-bottom:8px;
}}
.selector-sub {{
  text-align:center;
  color:var(--g5); font-size:16px;
  margin-bottom:40px;
}}
.selector-grid {{
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));
  gap:16px;
}}
.sel-card {{
  display:flex; flex-direction:column; align-items:flex-start;
  padding:28px 24px;
  background:var(--w);
  border:1px solid var(--g2);
  border-radius:var(--r3);
  text-align:left;
  transition:transform var(--tr), box-shadow var(--tr), border var(--tr);
  cursor:pointer;
}}
.sel-card:hover {{
  transform:translateY(-4px);
  border-color:var(--ac);
  box-shadow:var(--sh3);
}}
.sel-ic {{
  font-size:32px; margin-bottom:14px;
  display:grid; place-items:center;
  width:58px; height:58px;
  background:var(--ac-s); border-radius:var(--r2);
}}
.sel-tt {{
  font-family:var(--fd); font-weight:600;
  font-size:19px; letter-spacing:-.01em;
  color:var(--n); margin-bottom:6px;
}}
.sel-ds {{ font-size:13.5px; color:var(--g5); line-height:1.5; }}

/* ═══════════════ SECCIONES ═══════════════ */
section.block {{ padding:96px 0; }}
section.block.alt {{ background:var(--g0); }}

.eb {{
  font-size:12px; font-weight:600;
  text-transform:uppercase; letter-spacing:.12em;
  color:var(--ac); margin-bottom:12px;
}}
.sh {{
  font-family:var(--fd); font-weight:600;
  font-size:clamp(28px, 3.5vw, 42px);
  line-height:1.15; letter-spacing:-.02em;
  color:var(--n); max-width:24ch;
  margin-bottom:16px;
}}
.ss {{
  font-size:17px; color:var(--g7);
  max-width:56ch; margin-bottom:48px;
}}
.center {{ text-align:center; margin-left:auto; margin-right:auto; }}

/* ═══════════════ CASOS ═══════════════ */
.casos-g {{
  display:grid;
  grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));
  gap:20px;
}}
.caso {{
  background:var(--w);
  border:1px solid var(--g2);
  border-radius:var(--r3);
  padding:28px 24px 24px;
  transition:transform var(--tr), box-shadow var(--tr), border var(--tr);
  display:flex; flex-direction:column;
}}
.caso:hover {{
  transform:translateY(-4px);
  box-shadow:var(--sh3);
  border-color:var(--g3);
}}
.caso-ic {{
  font-size:26px;
  width:54px; height:54px;
  display:grid; place-items:center;
  background:var(--ac-s);
  border-radius:var(--r2);
  margin-bottom:16px;
}}
.caso-tt {{
  font-family:var(--fd); font-weight:600;
  font-size:19px; line-height:1.3; letter-spacing:-.01em;
  color:var(--n); margin-bottom:10px;
}}
.caso-ds {{
  font-size:14.5px; color:var(--g7);
  line-height:1.55; flex:1; margin-bottom:16px;
}}
.chip {{
  display:inline-flex; align-items:center;
  padding:4px 10px;
  background:var(--g1); border:1px solid var(--g2);
  border-radius:var(--r1);
  font-family:var(--fm); font-size:11px; font-weight:500;
  color:var(--g7); align-self:flex-start;
}}

/* ═══════════════ COMO FUNCIONA ═══════════════ */
.steps {{
  display:grid;
  grid-template-columns:repeat(3, 1fr);
  gap:24px;
  counter-reset:step;
}}
@media (max-width:760px) {{ .steps {{ grid-template-columns:1fr; }} }}
.step {{
  position:relative;
  padding:32px 28px 28px;
  background:var(--w);
  border-radius:var(--r3);
  border:1px solid var(--g2);
  transition:transform var(--tr), box-shadow var(--tr);
}}
.step:hover {{ transform:translateY(-3px); box-shadow:var(--sh3); }}
.step::before {{
  counter-increment:step;
  content:"0" counter(step);
  font-family:var(--fd); font-weight:500;
  font-size:48px; line-height:1; letter-spacing:-.03em;
  color:var(--ac);
  position:absolute; top:24px; right:28px;
  opacity:.35;
}}
.step h3 {{
  font-family:var(--fd); font-weight:600;
  font-size:20px; letter-spacing:-.01em;
  color:var(--n); margin-bottom:10px; max-width:88%;
}}
.step p {{ font-size:14.5px; color:var(--g7); line-height:1.6; }}

/* ═══════════════ TESTIMONIOS ═══════════════ */
.testimonios-g {{
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));
  gap:20px;
}}
.testi {{
  background:var(--w);
  border:1px solid var(--g2);
  border-radius:var(--r3);
  padding:28px 26px;
  position:relative;
}}
.testi::before {{
  content:"\\201C";
  font-family:var(--fd); font-size:64px; line-height:1;
  color:var(--ac); position:absolute;
  top:12px; right:24px; opacity:.25;
}}
.testi-q {{
  font-family:var(--fd); font-weight:500;
  font-size:16px; line-height:1.55;
  color:var(--g9); margin-bottom:20px;
  font-style:italic;
}}
.testi-foot {{
  display:flex; align-items:center; gap:12px;
  padding-top:16px; border-top:1px solid var(--g2);
}}
.testi-av {{
  width:42px; height:42px; border-radius:50%;
  background:linear-gradient(135deg, var(--ac), var(--ac-d));
  display:grid; place-items:center;
  color:var(--w); font-weight:600; font-size:15px;
  font-family:var(--fb);
}}
.testi-meta {{ flex:1; }}
.testi-name {{ font-weight:600; font-size:14px; color:var(--n); }}
.testi-case {{ font-size:12px; color:var(--g5); }}

/* ═══════════════ PRECIOS ═══════════════ */
.prices-g {{
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));
  gap:20px;
  max-width:920px; margin:0 auto;
}}
.price {{
  background:var(--w);
  border:1px solid var(--g2);
  border-radius:var(--r3);
  padding:32px 28px;
  position:relative;
  transition:transform var(--tr), box-shadow var(--tr);
}}
.price.featured {{
  border-color:var(--ac);
  box-shadow:var(--sh3);
  transform:scale(1.02);
}}
.price.featured::before {{
  content:"Más elegido";
  position:absolute; top:-12px; left:50%;
  transform:translateX(-50%);
  padding:5px 14px;
  background:var(--ac); color:var(--n);
  font-size:11px; font-weight:700;
  text-transform:uppercase; letter-spacing:.1em;
  border-radius:var(--rf);
}}
.price-tt {{
  font-family:var(--fd); font-weight:600;
  font-size:20px; color:var(--n); margin-bottom:6px;
}}
.price-sub {{ font-size:13.5px; color:var(--g5); margin-bottom:18px; }}
.price-amt {{
  font-family:var(--fd); font-weight:600;
  font-size:36px; letter-spacing:-.02em;
  color:var(--n); line-height:1;
}}
.price-amt small {{
  font-family:var(--fb); font-weight:400;
  font-size:13px; color:var(--g5);
  display:block; margin-top:4px;
}}
.price-feat {{ list-style:none; margin:22px 0 24px; }}
.price-feat li {{
  display:flex; align-items:flex-start; gap:10px;
  padding:6px 0; font-size:14px; color:var(--g7);
}}
.price-feat li::before {{
  content:"\\2713";
  color:var(--ok); font-weight:700; flex-shrink:0;
}}
.price-cta {{
  display:block; width:100%;
  padding:13px; border:1px solid var(--g3);
  background:var(--w); color:var(--n);
  font-weight:600; font-size:14px;
  border-radius:var(--r2); text-align:center;
  transition:all var(--tr);
}}
.price-cta:hover {{ border-color:var(--n); background:var(--g0); }}
.price.featured .price-cta {{
  background:var(--n); color:var(--w); border-color:var(--n);
}}
.price.featured .price-cta:hover {{ background:var(--g9); }}
.precio-nota {{
  text-align:center; margin-top:24px;
  font-size:13px; color:var(--g5);
}}

/* ═══════════════ TRUST ═══════════════ */
.trust-g {{
  display:grid;
  grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));
  gap:20px;
}}
.trust {{
  background:var(--w);
  padding:32px 28px;
  border-radius:var(--r3);
  border:1px solid var(--g2);
}}
.trust-tick {{
  width:38px; height:38px;
  background:var(--ok); color:var(--w);
  border-radius:var(--rf);
  display:grid; place-items:center;
  margin-bottom:16px;
}}
.trust-tt {{
  font-family:var(--fd); font-weight:600;
  font-size:19px; color:var(--n); margin-bottom:8px;
}}
.trust-ds {{ font-size:14.5px; color:var(--g7); line-height:1.55; }}

/* ═══════════════ FORM ═══════════════ */
.form-card {{
  background:var(--w);
  padding:48px;
  border-radius:var(--r4);
  border:1px solid var(--g2);
  box-shadow:var(--sh4);
  max-width:720px; margin:0 auto;
}}
@media (max-width:600px) {{ .form-card {{ padding:32px 24px; }} }}
.form-step {{
  font-size:12px; font-weight:600;
  text-transform:uppercase; letter-spacing:.1em;
  color:var(--g5); margin-bottom:6px;
}}
.form-row {{ display:grid; gap:16px; margin-bottom:16px; }}
.form-row.two {{ grid-template-columns:1fr 1fr; }}
@media (max-width:540px) {{ .form-row.two {{ grid-template-columns:1fr; }} }}
.field label {{
  display:block; font-size:13px; font-weight:600;
  color:var(--g7); margin-bottom:6px;
}}
.field label .opt {{ font-weight:400; color:var(--g5); }}
.field input, .field textarea {{
  width:100%;
  padding:13px 14px;
  border:1px solid var(--g2);
  border-radius:var(--r1);
  font:15px var(--fb); color:var(--n);
  background:var(--w);
  transition:border var(--tr), box-shadow var(--tr);
}}
.field input:focus, .field textarea:focus {{
  outline:none; border-color:var(--ac);
  box-shadow:0 0 0 3px var(--ac-s);
}}
.field textarea {{ resize:vertical; min-height:110px; line-height:1.55; }}
.field-hint {{ margin-top:6px; font-size:12px; color:var(--g5); }}
.field-hint.lock {{
  display:flex; align-items:center; gap:5px;
  color:var(--ok);
}}

.phone-wrap {{ display:flex; align-items:stretch; }}
.phone-cc {{
  padding:13px 14px;
  background:var(--g1);
  border:1px solid var(--g2);
  border-right:none;
  border-radius:var(--r1) 0 0 var(--r1);
  font:15px var(--fb); font-weight:500;
  color:var(--g7);
  display:flex; align-items:center; gap:6px;
}}
.phone-wrap input {{ border-radius:0 var(--r1) var(--r1) 0; }}

.consent {{
  display:flex; gap:10px;
  font-size:13px; color:var(--g7);
  padding:14px;
  background:var(--g0);
  border-radius:var(--r1);
  margin:18px 0;
  line-height:1.5;
}}
.consent input {{ margin-top:2px; flex-shrink:0; }}
.consent a {{ color:var(--ac-d); text-decoration:underline; }}

.btn-submit {{
  width:100%;
  padding:18px;
  background:var(--ac); color:var(--n);
  border:none; border-radius:var(--r2);
  font-size:16px; font-weight:600;
  cursor:pointer;
  transition:transform var(--tr), background var(--tr), box-shadow var(--tr);
}}
.btn-submit:hover {{
  background:var(--ac-d);
  transform:translateY(-1px);
  box-shadow:var(--shg);
}}
.btn-submit:disabled {{ opacity:.6; cursor:not-allowed; transform:none; }}

.form-alt {{
  text-align:center; margin-top:18px;
  font-size:14px; color:var(--g5);
}}
.form-alt a {{ color:var(--wa); font-weight:600; }}

#preview-out {{ margin-top:28px; }}
.prev-card {{
  background:var(--g0);
  border-left:4px solid var(--ac);
  padding:24px;
  border-radius:var(--r2);
  font-family:var(--fd);
  font-size:15.5px; line-height:1.65;
  color:var(--g9);
  white-space:pre-wrap;
  max-height:480px; overflow-y:auto;
}}

/* ═══════════════ FAQ ═══════════════ */
.faq-l {{ max-width:760px; margin:0 auto; }}
.faq-i {{
  background:var(--w);
  border:1px solid var(--g2);
  border-radius:var(--r2);
  margin-bottom:12px;
  overflow:hidden;
  transition:border var(--tr), box-shadow var(--tr);
}}
.faq-i:hover {{ border-color:var(--g3); }}
.faq-i[open] {{ box-shadow:var(--sh2); border-color:var(--ac); }}
.faq-q {{
  padding:20px 24px;
  font-weight:600; font-size:15.5px;
  color:var(--n); cursor:pointer;
  list-style:none;
  display:flex; justify-content:space-between; align-items:center;
}}
.faq-q::-webkit-details-marker {{ display:none; }}
.faq-q::after {{
  content:"+";
  font-size:22px; color:var(--g5);
  transition:transform var(--tr);
  font-weight:300;
}}
.faq-i[open] .faq-q::after {{
  transform:rotate(45deg); color:var(--ac);
}}
.faq-a {{
  padding:0 24px 22px;
  font-size:14.5px; color:var(--g7); line-height:1.65;
}}

/* ═══════════════ STICKY WHATSAPP BUTTON ═══════════════ */
.fab-wa {{
  position:fixed; bottom:24px; right:24px;
  z-index:60;
  display:flex; align-items:center; gap:8px;
  padding:14px 20px;
  background:var(--wa); color:var(--w);
  font-weight:600; font-size:14px;
  border-radius:var(--rf);
  box-shadow:0 8px 24px rgba(37,211,102,.4);
  transition:transform var(--tr);
}}
.fab-wa:hover {{ transform:translateY(-2px) scale(1.02); }}
.fab-wa svg {{ width:18px; height:18px; }}
@media (max-width:540px) {{ .fab-wa span {{ display:none; }} }}

/* ═══════════════ FOOTER ═══════════════ */
footer.foot {{
  background:var(--ad);
  color:var(--g3);
  padding:64px 0 28px;
}}
.foot-g {{
  display:grid;
  grid-template-columns:2fr 1fr 1fr 1fr;
  gap:40px;
  margin-bottom:40px;
}}
@media (max-width:760px) {{
  .foot-g {{ grid-template-columns:1fr 1fr; gap:32px; }}
}}
@media (max-width:500px) {{ .foot-g {{ grid-template-columns:1fr; }} }}
.foot-brand .brand {{ color:var(--w); margin-bottom:14px; }}
.foot-brand .brand-m {{ background:var(--w); color:var(--ad); }}
.foot-brand .brand small {{ color:var(--g3); }}
.foot-brand p {{ font-size:13.5px; color:var(--g3); max-width:36ch; line-height:1.55; }}
.foot-col h4 {{
  font-size:11.5px; text-transform:uppercase; letter-spacing:.12em;
  font-weight:600; color:var(--w); margin-bottom:14px;
}}
.foot-col a {{
  display:block; font-size:13.5px;
  color:var(--g3); padding:4px 0;
}}
.foot-col a:hover {{ color:var(--ac); }}
.foot-legal {{
  padding:24px 0 0;
  border-top:1px solid rgba(255,255,255,.08);
  display:grid; gap:14px;
}}
.foot-legal-r {{
  font-size:11.5px; color:rgba(255,255,255,.5);
  line-height:1.55;
}}
.foot-legal-r strong {{ color:rgba(255,255,255,.75); font-weight:600; }}

/* Helpers */
.hide {{ display:none !important; }}
.spinner {{
  display:inline-block; width:16px; height:16px;
  border:2px solid currentColor; border-top-color:transparent;
  border-radius:50%; animation:spin .7s linear infinite;
}}
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}
</style>

{fb_pixel}
</head>
<body>

<header class="nav">
  <div class="container nav-in">
    <a href="/" class="brand">
      <span class="brand-m">G</span>
      <span>Galeano Herrera <small>Abogados</small></span>
    </a>
    <div class="nav-r">
      <a href="{wa_url}" target="_blank" rel="noopener" class="nav-wa">María Camila te lee · 5 min</a>
      <a href="#empezar" class="nav-cta">Empezar →</a>
    </div>
  </div>
</header>

<!-- HERO -->
<section class="hero">
  <div class="container">
    <span class="eyebrow"><span class="d"></span>{EYEBROW}</span>
    <h1 class="hero-h">{H1_HTML}{'' if H1_HTML.rstrip('</em>').rstrip().endswith(('.','!','?')) else '.'}</h1>
    {promesa_html}
    <p class="hero-sub">{SUBT}</p>

    <div class="cta-row">
      <a href="#empezar" class="btn-pri">
        {CTA_TXT}
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      </a>
      <a href="{wa_url}" target="_blank" rel="noopener" class="btn-wa">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.6.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.4-.7-2.4-1.3-3.3-2.9-.3-.5.3-.5.8-1.5.1-.2 0-.3 0-.4l-.9-2.1c-.2-.5-.5-.5-.6-.5h-.6c-.2 0-.5.1-.7.3-.3.3-1 1-1 2.4 0 1.4 1 2.7 1.2 2.9.1.2 2 3.1 4.9 4.3 1.8.8 2.5.8 3.4.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3M12 2C6.5 2 2 6.5 2 12c0 1.7.5 3.4 1.3 4.8l-1.4 5.1 5.3-1.4c1.4.7 2.9 1.1 4.5 1.1h.3c5.5 0 10-4.5 10-10S17.5 2 12 2"/></svg>
        Hablar por WhatsApp
      </a>
    </div>

    <div class="microcopy"><span class="live"></span> Atendido por María Camila · primera consulta gratis · sin papeleo</div>

    <div class="stats">{stats_html}</div>
  </div>
</section>

{selector_html}

<!-- CASOS -->
<section class="block alt" id="casos">
  <div class="container">
    <div class="eb">Casos resueltos</div>
    <h2 class="sh">Los problemas que más nos buscan resolver</h2>
    <p class="ss">Cada caso enlaza con sentencias verificables de la Corte. Cero invención.</p>
    <div class="casos-g">{casos_html}</div>
  </div>
</section>

<!-- COMO FUNCIONA -->
<section class="block">
  <div class="container">
    <div class="eb">Cómo funciona</div>
    <h2 class="sh">De tu duda a un documento con respaldo jurídico, sin moverte de casa</h2>
    <p class="ss">Tres pasos. Sin papeleo. Sin cobro inicial. Sin oficina.</p>
    <div class="steps">
      <div class="step">
        <h3>Cuéntanos qué te pasa</h3>
        <p>Llenas un formulario de 5 datos en menos de 2 minutos. Sin vocabulario jurídico — escribe como hablas.</p>
      </div>
      <div class="step">
        <h3>Generamos tu caso</h3>
        <p>La IA del despacho cruza tu situación con sentencias reales y arma el borrador. Un abogado real lo revisa.</p>
      </div>
      <div class="step">
        <h3>Decides cómo seguir</h3>
        <p>Hablas con el abogado por WhatsApp. Si quieres lo radicas tú mismo, o nosotros lo hacemos por ti.</p>
      </div>
    </div>
  </div>
</section>

<!-- TESTIMONIOS -->
<section class="block alt">
  <div class="container">
    <div class="eb center">Personas reales, casos reales</div>
    <h2 class="sh center" style="text-align:center">Lo que nos dicen quienes ya pasaron por aquí</h2>
    <p class="ss center" style="text-align:center;margin-bottom:48px">Casos reales del último mes. Por respeto a la intimidad, usamos solo nombre y ciudad.</p>
    <div class="testimonios-g">
      <article class="testi">
        <p class="testi-q">«Llevaba 3 meses pidiendo la cirugía. En 8 días me la autorizaron por tutela. No tuve que ir a oficina ni nada.»</p>
        <div class="testi-foot">
          <div class="testi-av">CR</div>
          <div class="testi-meta">
            <div class="testi-name">Carmen R.</div>
            <div class="testi-case">Soacha · Tutela contra EPS</div>
          </div>
        </div>
      </article>
      <article class="testi">
        <p class="testi-q">«Me llegaron 4 fotomultas de un carro que vendí hace un año. Las anulamos y limpiamos el SIMIT. Sin gestores chimbos.»</p>
        <div class="testi-foot">
          <div class="testi-av">DM</div>
          <div class="testi-meta">
            <div class="testi-name">Diego M.</div>
            <div class="testi-case">Bogotá · Comparendos anulados</div>
          </div>
        </div>
      </article>
      <article class="testi">
        <p class="testi-q">«Estando embarazada me despidieron diciendo que no había plata. Reintegro + 6 meses de sueldo. La IA fue clarita desde el primer mensaje.»</p>
        <div class="testi-foot">
          <div class="testi-av">JS</div>
          <div class="testi-meta">
            <div class="testi-name">Jessica S.</div>
            <div class="testi-case">Medellín · Fuero materno</div>
          </div>
        </div>
      </article>
    </div>
  </div>
</section>

<!-- PRECIOS TRANSPARENTES -->
<section class="block" id="precios">
  <div class="container">
    <div class="eb center">Precios claros</div>
    <h2 class="sh center" style="text-align:center">Sin letra pequeña. Sin "consulta gratis" engañosa.</h2>
    <p class="ss center" style="text-align:center;margin-bottom:48px">El borrador siempre es gratis. Solo cobramos cuando decides que el abogado del despacho acompañe tu caso.</p>
    <div class="prices-g">
      <article class="price">
        <h3 class="price-tt">Borrador con IA</h3>
        <p class="price-sub">Para quien quiere radicar solo/a</p>
        <div class="price-amt">$0 <small>siempre gratis</small></div>
        <ul class="price-feat">
          <li>Borrador completo en minutos</li>
          <li>Citación de sentencias reales</li>
          <li>Revisado por María Camila</li>
          <li>Te queda en PDF para radicar</li>
        </ul>
        <a href="#empezar" class="price-cta">Empezar gratis</a>
      </article>
      <article class="price featured">
        <h3 class="price-tt">Borrador + abogado real</h3>
        <p class="price-sub">Para quien quiere acompañamiento</p>
        <div class="price-amt">$49.000 <small>pago único · sin sorpresas</small></div>
        <ul class="price-feat">
          <li>Todo lo anterior +</li>
          <li>Revisión con abogado por video o WhatsApp</li>
          <li>Ajustes y firma del documento</li>
          <li>Te enseñamos exactamente cómo radicar</li>
        </ul>
        <a href="#empezar" class="price-cta">Quiero acompañamiento</a>
      </article>
      <article class="price">
        <h3 class="price-tt">Caso completo</h3>
        <p class="price-sub">Para quien no quiere mover un dedo</p>
        <div class="price-amt">Desde $290.000 <small>te decimos antes de cobrar</small></div>
        <ul class="price-feat">
          <li>Todo lo anterior +</li>
          <li>Radicamos nosotros</li>
          <li>Te representamos hasta el fallo</li>
          <li>Impugnación si es necesario</li>
        </ul>
        <a href="{wa_url}" target="_blank" rel="noopener" class="price-cta">Cotizar mi caso</a>
      </article>
    </div>
    <p class="precio-nota">¿Tu caso es muy raro o complicado? Cotizamos por separado. <a href="{wa_url}" target="_blank" rel="noopener" style="color:var(--ac-d);text-decoration:underline;font-weight:500">Escríbenos al WhatsApp</a>.</p>
  </div>
</section>

<!-- FORMULARIO -->
<section class="block alt" id="empezar">
  <div class="container">
    <div class="eb center">Empezar</div>
    <h2 class="sh center" style="text-align:center">Cuéntanos qué te pasó</h2>
    <p class="ss center" style="text-align:center;margin-bottom:40px">Tu borrador en menos de 2 minutos. Primera consulta gratis.</p>

    <div class="form-card">
      <form id="lead-form">
        <div class="form-step">Tu información</div>
        <div class="form-row">
          <div class="field">
            <label for="nombre">¿Cómo te llamas?</label>
            <input id="nombre" name="nombre" required placeholder="Ej: María González" autocomplete="name">
          </div>
        </div>
        <div class="form-row two">
          <div class="field">
            <label for="ciudad">¿En qué ciudad estás?</label>
            <input id="ciudad" name="ciudad" required placeholder="Bogotá D.C." autocomplete="address-level2">
          </div>
          <div class="field">
            <label for="phone">Tu WhatsApp</label>
            <div class="phone-wrap">
              <span class="phone-cc">🇨🇴 +57</span>
              <input id="phone" name="phone" required placeholder="3001112233" inputmode="numeric" autocomplete="tel-national" maxlength="10">
            </div>
            <div class="field-hint">Te escribimos por aquí, no spammeamos.</div>
          </div>
        </div>

        <div class="form-step" style="margin-top:18px">Tu caso</div>
        <div class="form-row">
          <div class="field">
            <label for="descripcion">¿Qué te está pasando?</label>
            <textarea id="descripcion" name="descripcion" required placeholder="Cuéntanos brevemente: qué entidad o persona te está afectando, desde cuándo, qué has intentado. Sin tecnicismos, como hablas en WhatsApp."></textarea>
          </div>
        </div>

        <div class="form-step" style="margin-top:18px">Cédula <span style="text-transform:none;font-weight:400;color:var(--g5)">(la pedimos al final por una razón)</span></div>
        <div class="form-row">
          <div class="field">
            <label for="cedula">Tu cédula</label>
            <input id="cedula" name="cedula" required placeholder="Ej: 1018456789" inputmode="numeric" autocomplete="off">
            <div class="field-hint lock">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              Tu cédula NUNCA aparece en publicidad ni se vende. Solo va en el encabezado de tu documento legal — sin esto el juez no la recibe.
            </div>
          </div>
        </div>

        {area_hidden}
        {utm_hidden}
        <input type="hidden" name="slug" value="{SLUG}">

        <label class="consent">
          <input type="checkbox" id="consent" required>
          <span>Autorizo el tratamiento de mis datos personales según la Ley 1581 de 2012 (Habeas Data) y la <a href="#" target="_blank">Política de Privacidad</a>. Mis datos los usa solo el despacho para contactarme y generar mi caso.</span>
        </label>

        <button type="submit" class="btn-submit" id="btn-submit">
          <span class="btn-label">Generar mi borrador →</span>
        </button>

        <div class="form-alt">
          ¿Prefieres hablarlo primero? <a href="{wa_url}" target="_blank" rel="noopener">Escríbenos por WhatsApp →</a>
        </div>
      </form>
      <div id="preview-out"></div>
    </div>
  </div>
</section>

<!-- TRUST -->
<section class="block">
  <div class="container">
    <div class="eb">Por qué confiar</div>
    <h2 class="sh">Lo que nos hace diferentes de gestores y "trámites express"</h2>
    <div class="trust-g">{trust_html}</div>
  </div>
</section>

<!-- FAQ -->
<section class="block alt">
  <div class="container">
    <div style="text-align:center;margin-bottom:48px">
      <div class="eb">Preguntas frecuentes</div>
      <h2 class="sh" style="margin:0 auto 16px">Lo que casi todos nos preguntan</h2>
    </div>
    <div class="faq-l">{faq_html}</div>
  </div>
</section>

<!-- FOOTER -->
<footer class="foot">
  <div class="container">
    <div class="foot-g">
      <div class="foot-brand">
        <div class="brand"><span class="brand-m">G</span><span>Galeano Herrera <small>Abogados</small></span></div>
        <p>Despacho jurídico colombiano. Tutela, accidentes, comparendos y derecho laboral con jurisprudencia auditable.</p>
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
        <a href="{wa_url}" target="_blank" rel="noopener">WhatsApp +57 319 574 22 78</a>
        <a href="#empezar">Empezar mi caso</a>
        <a href="#precios">Precios</a>
        <a href="#">Contacto</a>
      </div>
      <div class="foot-col">
        <h4>Legal</h4>
        <a href="#">Política de privacidad</a>
        <a href="#">Habeas data Ley 1581</a>
        <a href="#">Términos de uso</a>
        <a href="https://www.sic.gov.co" target="_blank">SIC</a>
      </div>
    </div>
    <div class="foot-legal">
      <div class="foot-legal-r">
        <strong>Galeano Herrera Abogados</strong> · Despacho jurídico colombiano · Calle [pendiente], Bogotá D.C. · NIT [pendiente] · Tarjeta Profesional principal: [pendiente] (Consejo Superior de la Judicatura).
      </div>
      <div class="foot-legal-r">
        Vigilados por la Superintendencia de Industria y Comercio para el tratamiento de datos personales (Ley 1581/2012). {FOOTER_EXTRA or 'Acción de tutela: Decreto 2591/91 · Constitución Política, art. 86.'}
      </div>
      <div class="foot-legal-r" style="text-align:right">© 2026 Galeano Herrera Abogados · Todos los derechos reservados</div>
    </div>
  </div>
</footer>

<!-- FAB WhatsApp -->
<a href="{wa_url}" target="_blank" rel="noopener" class="fab-wa">
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.6.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.4-.7-2.4-1.3-3.3-2.9-.3-.5.3-.5.8-1.5.1-.2 0-.3 0-.4l-.9-2.1c-.2-.5-.5-.5-.6-.5h-.6c-.2 0-.5.1-.7.3-.3.3-1 1-1 2.4 0 1.4 1 2.7 1.2 2.9.1.2 2 3.1 4.9 4.3 1.8.8 2.5.8 3.4.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3M12 2C6.5 2 2 6.5 2 12c0 1.7.5 3.4 1.3 4.8l-1.4 5.1 5.3-1.4c1.4.7 2.9 1.1 4.5 1.1h.3c5.5 0 10-4.5 10-10S17.5 2 12 2"/></svg>
  <span>Hablar con María Camila</span>
</a>

<script>
const form = document.getElementById('lead-form');
const out = document.getElementById('preview-out');
const btn = document.getElementById('btn-submit');
const btnLabel = btn.querySelector('.btn-label');

// Solo dígitos en cédula y teléfono
['cedula','phone'].forEach(id => {{
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', e => {{
    e.target.value = e.target.value.replace(/\\D/g,'');
  }});
}});

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
      out.innerHTML = '<div class="prev-card" style="border-color:#C8102E">' + e.slice(0,400) + '</div>';
      btn.disabled = false; btnLabel.textContent = 'Reintentar';
      return;
    }}
    const j = await r.json();
    const nombre = data.nombre.split(' ')[0];
    out.innerHTML = '<h3 class="sh" style="font-size:22px;margin:32px 0 8px;text-align:left;max-width:100%">Listo, ' + nombre + '. Aquí está tu borrador.</h3>' +
      '<p style="font-size:14px;color:var(--g5);margin-bottom:18px">Un abogado real lo revisa y te escribe al WhatsApp en menos de 2 horas (en horario laboral).</p>' +
      '<div class="prev-card">' + (j.preview || j.borrador || '(sin preview)') + '</div>';
    btn.disabled = false; btnLabel.textContent = '✓ Borrador generado';
    btn.style.background = 'var(--ok)'; btn.style.color = 'white';
    if (window.fbq) fbq('track','Lead');
  }} catch(e) {{
    out.innerHTML = '<div class="prev-card" style="border-color:#C8102E">Error: ' + e.message + '</div>';
    btn.disabled = false; btnLabel.textContent = 'Reintentar';
  }}
}});
</script>

</body></html>"""
