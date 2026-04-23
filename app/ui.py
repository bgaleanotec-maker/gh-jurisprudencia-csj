"""HTML — Landing pública v2, panel admin, login abogado, dashboard abogado."""

from __future__ import annotations


# =============================================================================
# LANDING PÚBLICA
# =============================================================================

def landing_html() -> str:
    import os as _os
    FB_PIXEL_ID = (_os.environ.get("FB_PIXEL_ID") or "").strip()
    SITE_URL = (_os.environ.get("PUBLIC_URL") or "https://gh-jurisprudencia-csj.onrender.com").rstrip("/")
    fb_pixel_snippet = ""
    fb_pixel_noscript = ""
    if FB_PIXEL_ID:
        fb_pixel_snippet = (
            "<script>\n"
            "!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?"
            "n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;"
            "n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;"
            "t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}"
            "(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');\n"
            f"fbq('init','{FB_PIXEL_ID}');fbq('track','PageView');\n"
            "</script>"
        )
        fb_pixel_noscript = (
            f'<noscript><img height="1" width="1" style="display:none" '
            f'src="https://www.facebook.com/tr?id={FB_PIXEL_ID}&ev=PageView&noscript=1"/></noscript>'
        )

    OG_TITLE = "Te están negando un derecho. Recuperalo en 2 minutos."
    OG_DESC  = ("Genera tu acción de tutela respaldada en sentencias reales de la Corte Suprema de Justicia. "
                "Habla gratis con un abogado por WhatsApp. Sin papeleos.")
    head_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index,follow">
<meta name="description" content="Galeano Herrera | Abogados — Simulación de tu acción de tutela respaldada en jurisprudencia real de la Corte Suprema. Te conecta con un abogado por WhatsApp.">
<link rel="canonical" href="{SITE_URL}/">

<!-- Open Graph (Facebook, WhatsApp, LinkedIn) -->
<meta property="og:type"        content="website">
<meta property="og:site_name"   content="Galeano Herrera | Abogados">
<meta property="og:locale"      content="es_CO">
<meta property="og:url"         content="{SITE_URL}/">
<meta property="og:title"       content="{OG_TITLE}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image"       content="{SITE_URL}/og.png">
<meta property="og:image:width"  content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt"   content="Galeano Herrera | Abogados — Tu tutela en 2 minutos">

<!-- Twitter -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="{OG_TITLE}">
<meta name="twitter:description" content="{OG_DESC}">
<meta name="twitter:image"       content="{SITE_URL}/og.png">

<!-- Favicon SVG inline (escudo con G) -->
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='10' fill='%23002347'/><text x='50%25' y='54%25' font-family='Georgia,serif' font-size='42' font-weight='900' text-anchor='middle' fill='%23C5A059'>G</text></svg>">
<link rel="apple-touch-icon" href="{SITE_URL}/og.png">

{fb_pixel_snippet}

<title>Galeano Herrera · Tu tutela en 2 minutos, respaldada en la Corte Suprema</title>'''
    return head_html + _landing_body(FB_PIXEL_ID, fb_pixel_noscript)


def _landing_body(FB_PIXEL_ID: str, fb_pixel_noscript: str) -> str:
    return """</head>
""" + fb_pixel_noscript + """
<style>
  /* — Paleta basada en psicología del consumidor legal —
     Azul profundo: confianza, autoridad, profesionalismo
     Oro: prestigio, exclusividad
     Verde: éxito, "vas a ganar"
     Blanco amplio: claridad, transparencia */
  :root{
    --azul:#002347; --azul-2:#003f7a; --oro:#C5A059; --oro-soft:#e6cf95;
    --verde:#16a34a; --rojo:#c8102e; --gris:#f6f8fb; --texto:#1a2332;
    --gris-soft:#eef2f7; --sombra:0 4px 24px rgba(0,35,71,.08);
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',-apple-system,'Inter',sans-serif;background:#fff;color:var(--texto);line-height:1.55;}

  /* ACTION BAR sticky */
  .action-bar{position:sticky;top:0;z-index:40;background:linear-gradient(135deg,var(--azul) 0%,var(--azul-2) 100%);
              color:#fff;padding:10px 16px;display:flex;justify-content:center;align-items:center;gap:14px;
              border-bottom:2px solid var(--oro);box-shadow:0 2px 10px rgba(0,0,0,.18);flex-wrap:wrap;}
  .action-msg{font-size:13px;font-weight:600;}
  @media(max-width:560px){.action-msg{font-size:12px;}.action-aux{display:none;}}
  .action-cta{background:var(--verde);color:#fff;padding:8px 20px;border-radius:6px;font-weight:700;font-size:13px;
              text-decoration:none;transition:all .15s;white-space:nowrap;box-shadow:0 2px 8px rgba(22,163,74,.35);}
  .action-cta:hover{background:#15803d;transform:translateY(-1px);box-shadow:0 4px 12px rgba(22,163,74,.45);}
  .action-aux{color:var(--oro-soft);text-decoration:none;font-size:12px;font-weight:600;opacity:.9;}

  /* HEADER */
  header{padding:20px 16px;background:#fff;border-bottom:1px solid var(--gris-soft);
         display:flex;justify-content:space-between;align-items:center;max-width:1200px;margin:0 auto;}
  .logo{font-size:22px;font-weight:800;letter-spacing:-.5px;color:var(--azul);}
  .logo span{color:var(--oro);}
  .nav-links a{color:var(--azul);text-decoration:none;font-size:13px;margin-left:18px;font-weight:600;}

  /* CARRUSEL CASOS */
  .cases-section{padding:36px 0 24px;background:#fff;border-bottom:1px solid var(--gris-soft);}
  .cases-section .head{max-width:1100px;margin:0 auto;padding:0 16px 16px;}
  .cases-section .head h2{font-size:26px;color:var(--azul);font-weight:800;letter-spacing:-.3px;margin-bottom:6px;}
  .cases-section .head p{font-size:14px;color:#6b7280;}
  .cases-scroll{display:flex;gap:14px;overflow-x:auto;padding:10px 16px 24px;scroll-snap-type:x mandatory;scroll-behavior:smooth;
                scrollbar-color:var(--oro) #f3f4f6;}
  .cases-scroll::-webkit-scrollbar{height:8px;}
  .cases-scroll::-webkit-scrollbar-track{background:#f3f4f6;border-radius:4px;}
  .cases-scroll::-webkit-scrollbar-thumb{background:var(--oro);border-radius:4px;}
  .case-card{flex:0 0 280px;scroll-snap-align:start;background:#fff;border:1px solid var(--gris-soft);border-radius:12px;
             padding:18px;cursor:pointer;transition:all .15s;position:relative;}
  .case-card:hover{border-color:var(--oro);transform:translateY(-3px);box-shadow:0 10px 24px rgba(0,0,0,.08);}
  .case-card .ab{display:inline-block;padding:3px 10px;font-size:10px;font-weight:700;border-radius:10px;
                 text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px;color:#fff;}
  .case-card .ab.salud{background:#16a34a;}
  .case-card .ab.laboral{background:#7c3aed;}
  .case-card .ab.pensiones{background:#0891b2;}
  .case-card .ab.accidentes{background:#ea580c;}
  .case-card .ab.insolvencia{background:#64748b;}
  .case-card .ab.derechos_fundamentales{background:#C5A059;}
  .case-card .tt{font-weight:700;color:var(--azul);font-size:15px;margin-bottom:6px;line-height:1.3;}
  .case-card .ds{font-size:13px;color:#6b7280;line-height:1.5;}
  .case-card .go{position:absolute;top:14px;right:14px;color:var(--verde);font-size:16px;opacity:0;transition:opacity .15s;}
  .case-card:hover .go{opacity:1;}
  .case-nav{max-width:1100px;margin:0 auto;padding:0 16px;display:flex;justify-content:flex-end;gap:6px;margin-top:-14px;margin-bottom:10px;}
  .case-nav button{background:#fff;border:1px solid var(--gris-soft);border-radius:50%;width:34px;height:34px;cursor:pointer;
                   color:var(--azul);font-size:14px;transition:all .15s;}
  .case-nav button:hover{border-color:var(--oro);background:var(--gris);}

  /* HERO sobrio */
  .hero{background:var(--azul);color:#fff;padding:52px 16px 56px;text-align:center;border-bottom:3px solid var(--oro);}
  .hero h1{font-size:36px;font-weight:700;line-height:1.2;max-width:820px;margin:0 auto 14px;letter-spacing:-.5px;}
  .hero h1 .resaltar{color:var(--oro);}
  .hero p.lead{font-size:17px;opacity:.9;max-width:620px;margin:0 auto 24px;font-weight:300;line-height:1.5;}
  .badges{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:20px;}
  .badge-trust{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);padding:5px 12px;border-radius:4px;font-size:12px;font-weight:500;}

  /* BARRA STATS */
  .stats-bar{background:#fff;padding:24px 16px;border-bottom:1px solid var(--gris-soft);}
  .stats-bar .grid{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:18px;text-align:center;}
  @media(max-width:680px){.stats-bar .grid{grid-template-columns:repeat(2,1fr);}}
  .stat{padding:8px;}
  .stat .num{font-size:28px;font-weight:800;color:var(--azul);}
  .stat .lbl{font-size:11px;color:#777;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-top:4px;}

  /* CONTAINER */
  .container{max-width:880px;margin:0 auto;padding:32px 16px 48px;}
  .container-wide{max-width:1100px;margin:0 auto;padding:48px 16px;}

  /* CARD */
  .card{background:#fff;border-radius:14px;padding:32px;box-shadow:var(--sombra);margin-bottom:24px;border:1px solid var(--gris-soft);}
  h2{font-size:24px;color:var(--azul);margin-bottom:8px;font-weight:700;letter-spacing:-.3px;}
  h3{font-size:16px;color:var(--azul);margin:18px 0 12px;font-weight:700;}
  .muted{color:#666;font-size:14px;}

  /* PASOS */
  .pasos{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:32px 0;}
  @media(max-width:680px){.pasos{grid-template-columns:repeat(2,1fr);}}
  .paso{text-align:center;padding:16px 8px;background:var(--gris);border-radius:10px;}
  .paso .num{display:inline-flex;width:38px;height:38px;background:var(--oro);color:#fff;border-radius:50%;align-items:center;justify-content:center;font-weight:800;margin-bottom:8px;}
  .paso .t{font-weight:700;font-size:13px;color:var(--azul);margin-bottom:4px;}
  .paso .d{font-size:11px;color:#666;line-height:1.4;}

  /* FORMS */
  label{display:block;font-size:12px;font-weight:700;color:var(--azul);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}
  input[type=text],input[type=email],input[type=tel],input[type=password],textarea,select{
    width:100%;padding:12px 14px;border:2px solid #dce3ef;border-radius:8px;
    font-size:15px;color:var(--texto);font-family:inherit;background:#fafbfc;transition:border-color .15s,background .15s;}
  input:focus,textarea:focus,select:focus{outline:none;border-color:var(--azul);background:#fff;}
  textarea{resize:vertical;min-height:140px;}
  .form-group{margin-bottom:18px;}
  .row{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
  @media(max-width:600px){.row{grid-template-columns:1fr;}}

  /* CHECKBOX */
  .check{display:flex;align-items:flex-start;gap:10px;font-size:13px;color:#444;margin-bottom:10px;cursor:pointer;}
  .check input[type=checkbox]{margin-top:3px;width:16px;height:16px;flex-shrink:0;accent-color:var(--azul);}
  .check a{color:var(--azul);text-decoration:underline;}

  /* BTN — CTA primario VERDE (color theory: acción + éxito) */
  .btn{background:var(--verde);color:#fff;border:none;padding:14px 36px;border-radius:8px;
       font-size:16px;font-weight:700;cursor:pointer;letter-spacing:.3px;width:100%;
       transition:background .15s,transform .1s,box-shadow .15s;}
  .btn:hover{background:#15803d;transform:translateY(-1px);box-shadow:0 6px 18px rgba(22,163,74,.25);}
  .btn:focus-visible{outline:3px solid var(--oro);outline-offset:2px;}
  .btn:disabled{background:#9ca3af;cursor:wait;transform:none;box-shadow:none;}
  .btn.azul{background:var(--azul);}
  .btn.azul:hover{background:var(--azul-2);box-shadow:0 6px 18px rgba(0,35,71,.2);}
  .btn.gold{background:var(--oro);}
  .btn.gold:hover{background:#b08a47;}
  .btn.outline{background:transparent;color:var(--azul);border:2px solid var(--azul);}

  /* PREVIEW — sin overflow hidden en wrap, para que el candado y botón se vean siempre */
  .preview-wrap{background:#fafbfc;border:1px solid var(--gris-soft);border-radius:10px;padding:24px 24px 0;font-family:'Georgia',serif;font-size:14px;line-height:1.7;}
  .preview-visible{white-space:pre-wrap;max-height:420px;overflow:hidden;-webkit-mask-image:linear-gradient(180deg,#000 85%,transparent 100%);mask-image:linear-gradient(180deg,#000 85%,transparent 100%);}
  .preview-blur{position:relative;margin-top:0;padding:20px 0 24px;text-align:center;}
  .preview-blur .candado-box{background:linear-gradient(180deg,#fff 0%,var(--gris) 100%);border:1px solid var(--gris-soft);border-radius:10px;padding:28px 20px;margin-top:-40px;position:relative;z-index:2;}
  .preview-blur .candado-box .icon{font-size:44px;margin-bottom:8px;display:inline-block;}
  .preview-blur .candado-box h3{font-size:20px;color:var(--azul);margin-bottom:8px;font-weight:800;}
  .preview-blur .candado-box p{font-size:14px;color:#555;margin-bottom:18px;max-width:440px;margin-left:auto;margin-right:auto;}
  .preview-blur .candado-box .btn{max-width:320px;margin:0 auto;}

  .fichas-tag{display:inline-block;background:#e3f0ff;color:#004a9f;padding:5px 11px;border-radius:14px;font-size:11px;font-weight:700;margin:3px;}

  /* ALERTS */
  .alert{padding:12px 16px;border-radius:8px;font-size:14px;margin-bottom:16px;}
  .alert-info{background:#e8f1ff;border-left:4px solid var(--azul);color:var(--azul);}
  .alert-ok{background:#dcfce7;border-left:4px solid var(--verde);color:#14532d;}
  .alert-err{background:#ffebee;border-left:4px solid var(--rojo);color:#b71c1c;}
  .alert-gold{background:#fef9e7;border-left:4px solid var(--oro);color:#7a5200;}

  /* OTP */
  .otp-input{font-size:30px;letter-spacing:14px;text-align:center;padding:14px;font-family:monospace;}

  /* SLOTS de agenda */
  .slots-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin:16px 0;}
  .slot{padding:12px 8px;background:#fff;border:2px solid var(--gris-soft);border-radius:8px;text-align:center;cursor:pointer;transition:all .15s;font-size:13px;font-weight:600;color:var(--azul);}
  .slot:hover{border-color:var(--oro);background:var(--gris);transform:translateY(-1px);}
  .slot.selected{background:var(--azul);color:#fff;border-color:var(--azul);}
  .slot .day{font-size:11px;opacity:.7;display:block;}

  /* SECCIÓN CÓMO FUNCIONA / SOCIAL PROOF */
  section.bloque{padding:48px 16px;}
  section.bloque.gris{background:var(--gris);}
  .section-title{text-align:center;font-size:30px;color:var(--azul);font-weight:800;margin-bottom:8px;letter-spacing:-.5px;}
  .section-sub{text-align:center;color:#666;margin-bottom:36px;max-width:600px;margin-left:auto;margin-right:auto;}

  .casos-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;max-width:1100px;margin:0 auto;}
  @media(max-width:780px){.casos-grid{grid-template-columns:1fr;}}
  .caso{background:#fff;border-radius:12px;padding:22px;box-shadow:var(--sombra);border-top:4px solid var(--oro);}
  .caso .titulo{font-weight:700;color:var(--azul);font-size:16px;margin-bottom:8px;}
  .caso .resultado{color:var(--verde);font-size:13px;font-weight:700;margin-bottom:10px;}
  .caso .desc{font-size:13px;color:#555;line-height:1.6;margin-bottom:10px;}
  .caso .badge{font-size:11px;color:#888;font-style:italic;}

  /* FAQ */
  details{background:#fff;border:1px solid var(--gris-soft);border-radius:10px;margin-bottom:10px;padding:0;overflow:hidden;}
  details[open]{box-shadow:0 2px 12px rgba(0,35,71,.06);}
  summary{padding:18px 22px;font-weight:700;color:var(--azul);cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;}
  summary::after{content:'+';font-size:22px;color:var(--oro);font-weight:300;transition:transform .2s;}
  details[open] summary::after{transform:rotate(45deg);}
  details .body{padding:0 22px 22px;font-size:14px;color:#555;line-height:1.65;}

  /* DISCLAIMER */
  .disclaimer-fijo{background:#fff8e1;border-top:3px solid #ffc107;padding:14px;text-align:center;font-size:12px;color:#7a5200;}
  .disclaimer-fijo b{color:#5a3d00;}

  /* FOOTER */
  footer{background:var(--azul);color:#fff;padding:32px 16px;text-align:center;}
  footer .logo{font-size:18px;font-weight:800;margin-bottom:8px;color:#fff;}
  footer .logo span{color:var(--oro);}
  footer p{font-size:12px;opacity:.7;}
  footer a{color:var(--oro);text-decoration:none;}

  /* SPINNER */
  .spinner{display:none;text-align:center;padding:30px;color:var(--azul);}
  .spinner.on{display:block;}
  .spinner .dot{display:inline-block;width:10px;height:10px;background:var(--oro);border-radius:50%;margin:0 4px;animation:bounce 1.2s infinite;}
  .spinner .dot:nth-child(2){animation-delay:.2s;}.spinner .dot:nth-child(3){animation-delay:.4s;}
  @keyframes bounce{0%,80%,100%{transform:scale(.6);opacity:.4;}40%{transform:scale(1);opacity:1;}}

  .step{display:none;}.step.on{display:block;}
  .nav-step{font-size:12px;color:#888;text-align:center;margin-bottom:14px;letter-spacing:1px;text-transform:uppercase;}

  /* MODAL */
  .modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:100;align-items:center;justify-content:center;padding:20px;}
  .modal-bg.on{display:flex;}
  .modal{background:#fff;max-width:600px;max-height:80vh;overflow-y:auto;border-radius:12px;padding:30px;}
  .modal h3{margin-bottom:14px;}
  .modal-close{float:right;cursor:pointer;color:#888;font-size:24px;line-height:1;}

  /* WIZARD */
  .wiz-progress{margin-bottom:22px;}
  .wiz-track{background:#e5e7eb;height:6px;border-radius:3px;overflow:hidden;margin-bottom:12px;}
  .wiz-fill{background:linear-gradient(90deg,var(--azul) 0%,var(--verde) 100%);height:100%;transition:width .35s;}
  .wiz-steps{display:flex;justify-content:space-between;gap:6px;font-size:10px;color:#9ca3af;font-weight:700;text-transform:uppercase;letter-spacing:.5px;flex-wrap:wrap;}
  .wiz-dot{flex:1;text-align:center;padding:4px 2px;}
  .wiz-dot.on{color:var(--azul);}
  .wiz-panel{display:none;animation:fadeIn .3s;}
  .wiz-panel.on{display:block;}
  @keyframes fadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
  .wiz-nav{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:22px;}
  .wiz-nav .btn{flex:1;max-width:260px;margin-left:auto;}
  .btn-ghost{background:transparent;color:var(--azul);border:1px solid #dce3ef;padding:12px 22px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;}
  .btn-ghost:hover{background:var(--gris);}
  /* Tipo cards */
  .tipo-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:8px;}
  @media(max-width:680px){.tipo-grid{grid-template-columns:repeat(2,1fr);}}
  .tipo-card{background:#fff;border:2px solid #e5e7eb;border-radius:10px;padding:16px 10px;cursor:pointer;text-align:center;transition:all .15s;}
  .tipo-card:hover{border-color:var(--oro);transform:translateY(-2px);box-shadow:0 6px 16px rgba(197,160,89,.15);}
  .tipo-card.sel{border-color:var(--verde);background:#dcfce7;}
  .tipo-card .ic{font-size:32px;margin-bottom:6px;display:block;}
  .tipo-card .tt{font-weight:700;color:var(--azul);font-size:13px;margin-bottom:4px;}
  .tipo-card .ds{font-size:11px;color:#6b7280;line-height:1.4;}

  /* CTA STICKY MOBILE */
  .cta-sticky{display:none;position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px 16px;border-top:2px solid var(--oro);box-shadow:0 -4px 20px rgba(0,0,0,.08);z-index:50;}
  @media(max-width:780px){.cta-sticky.show{display:flex;gap:10px;align-items:center;justify-content:center;}}
</style>
</head>
<body>

<!-- Action bar sticky: visible siempre -->
<div class="action-bar">
  <div class="action-msg">⚡ Genera tu tutela en 2 minutos, respaldada en sentencias de la Corte Suprema</div>
  <a class="action-cta" href="#step-1" onclick="scrollToWizard(event)">Empezar ahora →</a>
  <a class="action-aux" href="/pro/login">Abogados</a>
</div>

<header>
  <div class="logo">Galeano <span>Herrera</span></div>
  <nav class="nav-links">
    <a href="#como-funciona">Cómo funciona</a>
    <a href="#casos">Casos</a>
    <a href="#faq">FAQ</a>
  </nav>
</header>

<section class="hero">
  <h1>Te están <span class="resaltar">negando un derecho</span>.<br>Aquí tienes cómo recuperarlo.</h1>
  <p class="lead">Describe tu caso. Cruzamos tu situación con sentencias reales de la Corte Suprema y te mostramos, en minutos, qué dice la ley y cuál es tu mejor camino.</p>
  <div class="badges">
    <span class="badge-trust">Sentencias CSJ 2018–2025</span>
    <span class="badge-trust">Radicados verificables</span>
    <span class="badge-trust">Habeas Data · Ley 1581</span>
  </div>
</section>

<section class="stats-bar">
  <div class="grid">
    <div class="stat"><div class="num" id="s-fichas">—</div><div class="lbl">Sentencias indexadas</div></div>
    <div class="stat"><div class="num">6</div><div class="lbl">Áreas legales cubiertas</div></div>
    <div class="stat"><div class="num">4</div><div class="lbl">Salas CSJ (Civil · Laboral · Penal · Plena)</div></div>
    <div class="stat"><div class="num">$0</div><div class="lbl">Costo de la simulación</div></div>
  </div>
</section>

<!-- POR QUÉ CONFIAR (Cialdini: autoridad + prueba social honesta + reciprocidad) -->
<section class="bloque" style="padding:40px 16px 16px">
  <div class="container-wide">
    <div class="casos-grid">
      <div class="caso">
        <div class="titulo">Autoridad real</div>
        <div class="desc">Cada cita viene de una sentencia pública de la Corte Suprema de Justicia. Puedes verificar todos los radicados en <a href="https://relatoria.cortesuprema.gov.co" target="_blank" rel="noopener">relatoria.cortesuprema.gov.co</a>.</div>
      </div>
      <div class="caso">
        <div class="titulo">Sin costo oculto</div>
        <div class="desc">La simulación es gratuita. La primera llamada con el abogado también. Si decides contratar representación, los honorarios se discuten antes, por escrito.</div>
      </div>
      <div class="caso">
        <div class="titulo">Tus datos, protegidos</div>
        <div class="desc">Tratamos tu información bajo la Ley 1581 de 2012. Tienes derecho a consultar, actualizar, rectificar o suprimir tus datos en cualquier momento.</div>
      </div>
    </div>
  </div>
</section>

<!-- CARRUSEL DE CASOS FRECUENTES (basado en jurisprudencia) -->
<section class="cases-section">
  <div class="head">
    <h2>Casos más frecuentes</h2>
    <p>Tipos de tutela que los jueces conceden con más regularidad en Colombia. Toca una para empezar tu caso — te lleva al paso 4 con un ejemplo ya escrito que puedes editar.</p>
  </div>
  <div class="case-nav">
    <button onclick="scrollCases(-1)" aria-label="Anterior">◀</button>
    <button onclick="scrollCases(1)" aria-label="Siguiente">▶</button>
  </div>
  <div class="cases-scroll" id="cases-scroll">
    <!-- SALUD -->
    <div class="case-card" data-area="salud" data-ej="Mi EPS Sanitas me niega desde hace 2 meses la quimioterapia que me prescribió el oncólogo. Soy paciente con cáncer de mama y no he podido iniciar tratamiento. Ya radiqué PQR y no responden."><span class="ab salud">Salud</span><div class="tt">EPS niega medicamento oncológico</div><div class="ds">Quimioterapia, radioterapia o fármacos no POS que la EPS rechaza por "no cobertura".</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="El ortopedista ordenó cirugía de rodilla hace 4 meses. La EPS dice que debo esperar autorización pero no avanza. Tengo dolor crónico y no puedo caminar bien."><span class="ab salud">Salud</span><div class="tt">Cirugía prescrita sin autorizar</div><div class="ds">Reemplazo de cadera, columna, cesárea programada y otras cirugías que se demoran meses.</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="Necesito cita con el neurólogo urgente por convulsiones. La EPS solo me da cita para dentro de 6 meses. Mi condición empeora cada semana."><span class="ab salud">Salud</span><div class="tt">Cita con especialista demorada meses</div><div class="ds">Cardiología, oncología, neurología, oftalmología con agenda a 4+ meses.</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="Soy paciente con lupus. La EPS me autoriza solo algunos tratamientos, pero no el tratamiento integral que indica el reumatólogo (terapias, medicamentos, controles). Llevo 8 meses sin el plan completo."><span class="ab salud">Salud</span><div class="tt">Tratamiento integral a enfermedad ruinosa</div><div class="ds">Cáncer, VIH, lupus, insuficiencia renal: EPS cubre parcial, debería ser integral.</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="Mi madre quedó postrada tras un ACV. El médico tratante ordenó cuidador domiciliario 24 horas. La EPS lo niega diciendo que es responsabilidad familiar. Mi familia no puede contratar a alguien, necesitamos trabajar."><span class="ab salud">Salud</span><div class="tt">Cuidador domiciliario negado</div><div class="ds">Paciente postrado, adulto mayor: EPS alega que es responsabilidad familiar.</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="Vivo en un municipio y mi tratamiento oncológico es en Bogotá. La EPS solo cubre el transporte una vez al mes, pero el protocolo exige semanal. No tengo recursos para pagar los demás viajes."><span class="ab salud">Salud</span><div class="tt">Transporte médico intermunicipal</div><div class="ds">Paciente rural con tratamiento especializado en otra ciudad.</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="Soy cuidador de mi papá con Alzheimer en etapa avanzada. La EPS niega pañales, sonda y nutrición enteral aduciendo que no están en el POS. Sin estos insumos no puede sobrevivir."><span class="ab salud">Salud</span><div class="tt">Insumos médicos negados (pañales, sonda)</div><div class="ds">Pacientes crónicos que necesitan insumos "no POS" para vivir.</div><div class="go">→</div></div>
    <div class="case-card" data-area="salud" data-ej="Llegué a urgencias con dolor torácico intenso. La clínica me negó atención por 'tema administrativo' con la EPS. Tuvieron que estabilizarme varias horas después."><span class="ab salud">Salud</span><div class="tt">Atención de urgencias negada</div><div class="ds">Hospital/clínica que condiciona atención urgente por trámite con EPS.</div><div class="go">→</div></div>

    <!-- PENSIONES -->
    <div class="case-card" data-area="pensiones" data-ej="Radiqué mi solicitud de pensión de vejez en Colpensiones en enero. Hoy en abril no me han respondido. Tengo 63 años, 1500 semanas cotizadas y necesito la pensión para vivir."><span class="ab pensiones">Pensiones</span><div class="tt">Mora Colpensiones: 4+ meses sin respuesta</div><div class="ds">Solicitudes de vejez/invalidez sin resolver pese a tener documentos completos.</div><div class="go">→</div></div>
    <div class="case-card" data-area="pensiones" data-ej="Tuve un accidente laboral que me dejó con 65% de pérdida de capacidad laboral según dictamen de la Junta. Colpensiones me niega la pensión de invalidez diciendo que no cumplo el 50% de semanas."><span class="ab pensiones">Pensiones</span><div class="tt">Pensión de invalidez negada</div><div class="ds">Pese a dictamen de pérdida capacidad laboral ≥50%.</div><div class="go">→</div></div>
    <div class="case-card" data-area="pensiones" data-ej="Mi esposo falleció el 20 de febrero. Era pensionado de Colpensiones. Solicité la pensión de sobreviviente hace 2 meses y no hay respuesta. Dependía económicamente de él."><span class="ab pensiones">Pensiones</span><div class="tt">Pensión de sobreviviente / sustitución</div><div class="ds">Viuda/o, compañera permanente, hijos menores o con discapacidad.</div><div class="go">→</div></div>
    <div class="case-card" data-area="pensiones" data-ej="Cumplí 57 años y tengo 650 semanas cotizadas. Colpensiones me negó la indemnización sustitutiva argumentando que debo esperar la vejez. No tengo cómo mantenerme mientras tanto."><span class="ab pensiones">Pensiones</span><div class="tt">Indemnización sustitutiva negada</div><div class="ds">Cuando no se alcanzan las semanas para pensión pero sí aportes cotizados.</div><div class="go">→</div></div>
    <div class="case-card" data-area="pensiones" data-ej="Solicité traslado de Porvenir a Colpensiones hace 6 meses. Porvenir no remite mi expediente. Mientras tanto no se mueven mis trámites y no puedo pensionarme."><span class="ab pensiones">Pensiones</span><div class="tt">Traslado entre AFPs bloqueado</div><div class="ds">AFP privada retiene expediente al pasar a régimen público.</div><div class="go">→</div></div>
    <div class="case-card" data-area="pensiones" data-ej="Me pensioné en 2018 con mesada mínima. Llevo 3 años sin reajuste y la ley exige incremento según IPC. Colpensiones no ha actualizado mi mesada."><span class="ab pensiones">Pensiones</span><div class="tt">Reajuste de mesada no aplicado</div><div class="ds">Incremento anual según IPC o salario mínimo que Colpensiones omite.</div><div class="go">→</div></div>

    <!-- LABORAL -->
    <div class="case-card" data-area="laboral" data-ej="Me despidieron el 15 de marzo estando en el sexto mes de embarazo. Mi contrato era a término indefinido desde hace 3 años. La empresa no solicitó permiso al Ministerio del Trabajo."><span class="ab laboral">Laboral</span><div class="tt">Despido en embarazo (fuero materno)</div><div class="ds">Cualquier despido durante embarazo o 3 meses post-parto sin permiso del Mintrabajo.</div><div class="go">→</div></div>
    <div class="case-card" data-area="laboral" data-ej="Tuve incapacidad médica de 180 días por enfermedad común (depresión severa diagnosticada). Al reintegrarme la empresa me notificó terminación sin justa causa pagándome la indemnización."><span class="ab laboral">Laboral</span><div class="tt">Despido por incapacidad / salud</div><div class="ds">Estabilidad laboral reforzada en personas con condición de salud.</div><div class="go">→</div></div>
    <div class="case-card" data-area="laboral" data-ej="Llevo 4 años trabajando por contrato de prestación de servicios como profesional. Tengo horario fijo, subordinación, reportes semanales y uso las herramientas de la empresa. Nunca me han pagado prestaciones sociales."><span class="ab laboral">Laboral</span><div class="tt">Contrato prestación servicios disfrazado</div><div class="ds">Contrato de servicios con subordinación y horario (contrato realidad).</div><div class="go">→</div></div>
    <div class="case-card" data-area="laboral" data-ej="Mi jefe me humilla frente a colegas, me cambia funciones sin aviso, me prohíbe tomar vacaciones. Desde hace 8 meses he bajado de peso, duermo mal. Tengo evidencia escrita (WhatsApp, correos)."><span class="ab laboral">Laboral</span><div class="tt">Acoso laboral / mobbing</div><div class="ds">Hostigamiento sistemático con evidencia documental o testigos.</div><div class="go">→</div></div>
    <div class="case-card" data-area="laboral" data-ej="La empresa dejó de pagarme el salario desde hace 2 meses. Tampoco han consignado la seguridad social. Tengo arriendo, servicios y alimentación atrasadas."><span class="ab laboral">Laboral</span><div class="tt">No pago de salario o seguridad social</div><div class="ds">Mínimo vital afectado; derecho a suspender contrato y reclamar.</div><div class="go">→</div></div>
    <div class="case-card" data-area="laboral" data-ej="Soy una persona con discapacidad auditiva reconocida. Mi empresa me notificó el despido sin permiso del Ministerio del Trabajo, alegando que ya no necesitan mi puesto."><span class="ab laboral">Laboral</span><div class="tt">Despido de persona con discapacidad</div><div class="ds">Estabilidad reforzada; requiere autorización del Ministerio del Trabajo.</div><div class="go">→</div></div>
    <div class="case-card" data-area="laboral" data-ej="Mi madre falleció el jueves. Pedí licencia de luto remunerada de 5 días según la ley y me la negaron diciendo que debo usar vacaciones."><span class="ab laboral">Laboral</span><div class="tt">Licencia de luto / paternidad negada</div><div class="ds">Licencias legales remuneradas que la empresa desconoce.</div><div class="go">→</div></div>

    <!-- ACCIDENTES / SOAT -->
    <div class="case-card" data-area="accidentes" data-ej="Tuve un accidente en moto el 10 de marzo. La Previsora (SOAT) me negó cobertura alegando que el otro conductor estaba embriagado. Yo no lo estaba y tengo 50% de pérdida capacidad por fractura."><span class="ab accidentes">Accidentes</span><div class="tt">SOAT niega atención tras accidente</div><div class="ds">Seguradora elude cobertura con excusas. Procede tutela por vida/salud.</div><div class="go">→</div></div>
    <div class="case-card" data-area="accidentes" data-ej="Fui atropellado por un carro que se dio a la fuga. La clínica me cobra los 30 días que estuve hospitalizado porque no hay responsable identificado y el SOAT solo cubre 800 SMDLV."><span class="ab accidentes">Accidentes</span><div class="tt">Hospitalización no cubierta (carro fantasma)</div><div class="ds">Fondo FOSYGA / ADRES debe responder cuando no hay responsable identificado.</div><div class="go">→</div></div>
    <div class="case-card" data-area="accidentes" data-ej="Sufrí accidente de tránsito con 45% pérdida capacidad laboral. Soy trabajador independiente. La ARL dice que yo debo cotizar como independiente. Colpensiones tampoco responde."><span class="ab accidentes">Accidentes</span><div class="tt">Incapacidades e indemnización ignoradas</div><div class="ds">Pago de incapacidades laborales y daños tras accidente de tránsito.</div><div class="go">→</div></div>
    <div class="case-card" data-area="accidentes" data-ej="La aseguradora solo cubrió los primeros días del hospital. Los demás 20 días me los cobran a mí. Tengo copia de los pagos de SOAT vigentes al momento del accidente."><span class="ab accidentes">Accidentes</span><div class="tt">Cobertura SOAT insuficiente</div><div class="ds">Agotamiento prematuro de los 800 SMDLV sin habilitar FOSYGA.</div><div class="go">→</div></div>

    <!-- INSOLVENCIA -->
    <div class="case-card" data-area="insolvencia" data-ej="El banco embargó mi cuenta de ahorros donde me depositan el salario mínimo cada mes. Es la única cuenta que tengo. Sin ese dinero no puedo comer ni pagar arriendo."><span class="ab insolvencia">Insolvencia</span><div class="tt">Embargo de cuenta de nómina / mínimo vital</div><div class="ds">Cuentas con salario mínimo son inembargables hasta 5 SMMLV.</div><div class="go">→</div></div>
    <div class="case-card" data-area="insolvencia" data-ej="Recibo mi pensión de vejez en mi cuenta de Bancolombia. Un banco embargó esa cuenta por un crédito en mora. Tengo 68 años y dependo 100% de esa pensión."><span class="ab insolvencia">Insolvencia</span><div class="tt">Embargo de cuenta pensional</div><div class="ds">Mesadas pensionales son inembargables (salvo alimentos).</div><div class="go">→</div></div>
    <div class="case-card" data-area="insolvencia" data-ej="El banco inició proceso ejecutivo contra mí y embargó mi apartamento. Nunca me notificaron la demanda: se enviaron notificaciones a una dirección anterior de hace 4 años."><span class="ab insolvencia">Insolvencia</span><div class="tt">Proceso ejecutivo sin notificación válida</div><div class="ds">Defecto en notificación vulnera el debido proceso.</div><div class="go">→</div></div>
    <div class="case-card" data-area="insolvencia" data-ej="Tengo deudas por 35 millones con 4 bancos. Mis ingresos no alcanzan. Quiero acogerme al régimen de insolvencia persona natural Ley 1564 para renegociar pero el Centro de Conciliación me niega la admisión."><span class="ab insolvencia">Insolvencia</span><div class="tt">Insolvencia persona natural rechazada</div><div class="ds">Ley 1564 de 2012 permite renegociar deudas; centros niegan a veces.</div><div class="go">→</div></div>

    <!-- DERECHOS FUNDAMENTALES -->
    <div class="case-card" data-area="derechos_fundamentales" data-ej="La DIAN me inició cobro coactivo por 15 millones por una declaración de renta del 2019 que yo no debo. Embargaron mi salario sin que me hayan notificado el mandamiento de pago."><span class="ab derechos_fundamentales">DD.FF.</span><div class="tt">Cobro coactivo DIAN sin debido proceso</div><div class="ds">Embargo administrativo sin notificación o sin título ejecutivo claro.</div><div class="go">→</div></div>
    <div class="case-card" data-area="derechos_fundamentales" data-ej="Me llegó una fotomulta por 600 mil del 2022. Nunca me notificaron en su momento. Ahora aparece en cobro coactivo y no me dejan renovar la licencia."><span class="ab derechos_fundamentales">DD.FF.</span><div class="tt">Fotomulta sin notificación</div><div class="ds">Comparendos sin notificación personal ni avisos en 6 meses.</div><div class="go">→</div></div>
    <div class="case-card" data-area="derechos_fundamentales" data-ej="Mi esposo fue absuelto en primera instancia. Apeló la Fiscalía hace 2 años y el Tribunal Superior no ha resuelto. Mi esposo sigue en detención preventiva sin tener fallo condenatorio."><span class="ab derechos_fundamentales">DD.FF.</span><div class="tt">Mora judicial / plazo razonable</div><div class="ds">Procesos sin decisión por años. Tutela por plazo razonable.</div><div class="go">→</div></div>
    <div class="case-card" data-area="derechos_fundamentales" data-ej="Mi hermano lleva 14 meses en prisión y ya cumplió la pena que le imponen en primera instancia (12 meses). El juzgado no resuelve la solicitud de libertad inmediata."><span class="ab derechos_fundamentales">DD.FF.</span><div class="tt">Libertad inmediata por pena cumplida</div><div class="ds">Procedimiento para obtener libertad cuando se cumplió la pena.</div><div class="go">→</div></div>
    <div class="case-card" data-area="derechos_fundamentales" data-ej="Presenté derecho de petición a la Alcaldía hace 45 días pidiendo copia de un expediente urbanístico y no me han respondido. La ley da 15 días."><span class="ab derechos_fundamentales">DD.FF.</span><div class="tt">Derecho de petición sin respuesta</div><div class="ds">Entidad pública o privada con función pública que no responde en término.</div><div class="go">→</div></div>
  </div>
</section>

<div class="container">
  <div class="pasos">
    <div class="paso"><div class="num">1</div><div class="t">Describe</div><div class="d">En tus palabras</div></div>
    <div class="paso"><div class="num">2</div><div class="t">Conoce</div><div class="d">Qué dice la Corte</div></div>
    <div class="paso"><div class="num">3</div><div class="t">Valida</div><div class="d">Con un abogado</div></div>
    <div class="paso"><div class="num">4</div><div class="t">Actúa</div><div class="d">Con confianza</div></div>
  </div>

  <!-- STEP 1: WIZARD CARRUSEL (5 micro-pasos) -->
  <div class="card step on" id="step-1">

    <!-- Progress bar del wizard -->
    <div class="wiz-progress">
      <div class="wiz-track"><div id="wiz-bar" class="wiz-fill" style="width:20%"></div></div>
      <div class="wiz-steps">
        <span class="wiz-dot on" data-s="1">1. Tipo</span>
        <span class="wiz-dot" data-s="2">2. Contra quién</span>
        <span class="wiz-dot" data-s="3">3. Cuándo</span>
        <span class="wiz-dot" data-s="4">4. Detalles</span>
        <span class="wiz-dot" data-s="5">5. Tú</span>
      </div>
    </div>

    <!-- Micro-paso 1.1: Tipo de caso -->
    <div class="wiz-panel on" id="wiz-1">
      <h2>¿Qué te está pasando?</h2>
      <p class="muted" style="margin-bottom:16px">Elige la opción más cercana a tu situación.</p>
      <div class="tipo-grid" id="tipo-grid">
        <div class="tipo-card" data-area="salud"><div class="ic">🏥</div><div class="tt">Salud · EPS</div><div class="ds">Me niegan medicamentos, cirugía, tratamiento</div></div>
        <div class="tipo-card" data-area="pensiones"><div class="ic">👴</div><div class="tt">Pensiones · Colpensiones</div><div class="ds">Mora, negación de pensión, AFP</div></div>
        <div class="tipo-card" data-area="laboral"><div class="ic">💼</div><div class="tt">Laboral · Despido</div><div class="ds">Fuero, embarazo, salud, acoso</div></div>
        <div class="tipo-card" data-area="accidentes"><div class="ic">🚗</div><div class="tt">Accidente · SOAT</div><div class="ds">Seguradora no paga atención</div></div>
        <div class="tipo-card" data-area="insolvencia"><div class="ic">💳</div><div class="tt">Embargo · Insolvencia</div><div class="ds">Cuenta nómina, bienes, deudas</div></div>
        <div class="tipo-card" data-area="derechos_fundamentales"><div class="ic">⚖️</div><div class="tt">Otros derechos</div><div class="ds">Debido proceso, mora judicial, libertad</div></div>
      </div>
      <div class="wiz-nav">
        <div></div>
        <button class="btn" id="wiz-next-1" disabled onclick="wizNext(1)">Siguiente →</button>
      </div>
    </div>

    <!-- Micro-paso 1.2: Contra quién -->
    <div class="wiz-panel" id="wiz-2">
      <h2>¿Contra quién es?</h2>
      <p class="muted" style="margin-bottom:16px" id="wiz-2-hint">Escribe el nombre completo de la entidad.</p>
      <div class="form-group">
        <label>Entidad, empresa o persona accionada</label>
        <input type="text" id="o-accionado" placeholder="Ej: EPS Sanitas S.A.S.">
      </div>
      <div class="wiz-nav">
        <button class="btn-ghost" onclick="wizPrev(2)">← Volver</button>
        <button class="btn" onclick="wizNext(2)">Siguiente →</button>
      </div>
    </div>

    <!-- Micro-paso 1.3: Cuándo -->
    <div class="wiz-panel" id="wiz-3">
      <h2>¿Desde cuándo ocurrió?</h2>
      <p class="muted" style="margin-bottom:16px">La inmediatez importa: si pasó hace menos de 6 meses, tu tutela tiene mejor chance.</p>
      <div class="row">
        <div class="form-group">
          <label>Fecha aproximada del hecho</label>
          <input type="date" id="o-fecha">
        </div>
        <div class="form-group">
          <label>¿Ya reclamaste a la entidad?</label>
          <select id="o-reclamo">
            <option value="">Selecciona</option>
            <option value="si_sin_respuesta">Sí, no respondieron</option>
            <option value="si_negado">Sí, me lo negaron</option>
            <option value="no">No, aún no</option>
          </select>
        </div>
      </div>
      <div class="wiz-nav">
        <button class="btn-ghost" onclick="wizPrev(3)">← Volver</button>
        <button class="btn" onclick="wizNext(3)">Siguiente →</button>
      </div>
    </div>

    <!-- Micro-paso 1.4: Detalles libres -->
    <div class="wiz-panel" id="wiz-4">
      <h2>Cuéntanos más detalle</h2>
      <p class="muted" style="margin-bottom:16px">Tres frases basta. ¿Qué te prescribieron? ¿Qué síntomas/consecuencias tienes? ¿Qué pruebas tienes?</p>
      <div class="form-group">
        <label>Tu historia *</label>
        <textarea id="descripcion" autofocus placeholder="Por ejemplo: Mi oncólogo ordenó quimioterapia el 10 de enero. La EPS dice que el medicamento no está en el POS. Tengo la orden médica y un concepto que dice que sin tratamiento hay riesgo vital..."></textarea>
      </div>
      <div class="wiz-nav">
        <button class="btn-ghost" onclick="wizPrev(4)">← Volver</button>
        <button class="btn" onclick="wizNext(4)">Siguiente →</button>
      </div>
    </div>

    <!-- Micro-paso 1.5: Datos personales -->
    <div class="wiz-panel" id="wiz-5">
      <h2>Tus datos (para personalizar el borrador)</h2>
      <p class="muted" style="margin-bottom:16px">Si los llenas, el documento sale con tu nombre real en vez de <i>[COMPLETAR]</i>.</p>
      <div class="row">
        <div class="form-group">
          <label>Tu nombre completo</label>
          <input type="text" id="o-nombre" placeholder="María García López" autocomplete="name">
        </div>
        <div class="form-group">
          <label>Tu cédula</label>
          <input type="text" id="o-cedula" inputmode="numeric" placeholder="1234567890">
        </div>
      </div>
      <div class="form-group">
        <label>Ciudad</label>
        <input type="text" id="o-ciudad" placeholder="Bogotá D.C." value="Bogotá D.C.">
      </div>
      <div class="wiz-nav">
        <button class="btn-ghost" onclick="wizPrev(5)">← Volver</button>
        <button class="btn" onclick="generarPreview()">Analizar mi caso ⚡</button>
      </div>
    </div>

    <div class="spinner" id="spinner-1"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Analizando contra jurisprudencia de la Corte Suprema…</div>
    <div id="err-1"></div>

    <!-- input oculto para compatibilidad -->
    <input type="hidden" id="area" value="">
  </div>

  <!-- STEP 2: PREVIEW -->
  <div class="card step" id="step-2">
    <div class="nav-step">Paso 2 de 5</div>
    <h2>Esto dice la Corte sobre tu caso</h2>
    <p class="muted" style="margin-bottom:14px">Simulación basada en líneas jurisprudenciales reales. Pensada para validar con un abogado — no es asesoría jurídica autónoma.</p>
    <div class="alert alert-info" id="alert-fichas"></div>

    <div class="preview-wrap">
      <div class="preview-visible" id="preview-visible"></div>
      <div class="preview-blur">
        <div class="candado-box">
          <div class="icon">🔓</div>
          <h3>Desbloquea el borrador completo</h3>
          <p>Fundamentos jurídicos con citas, pretensiones, medida provisional, pruebas, juramento y firma. Listo para que tu abogado lo revise.</p>
          <button class="btn" onclick="irRegistro()">Continuar — desbloquear</button>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 3: REGISTRO -->
  <div class="card step" id="step-3">
    <div class="nav-step">Paso 3 de 5</div>
    <h2>Un paso más para acompañarte</h2>
    <p class="muted" style="margin-bottom:20px">Solo necesitamos tu contacto para que un abogado se conecte contigo. Tus datos están protegidos por la <b>Ley 1581 de 2012</b>.</p>

    <div class="row">
      <div class="form-group">
        <label>Nombre completo *</label>
        <input type="text" id="r-nombre" placeholder="María García López" autocomplete="name">
      </div>
      <div class="form-group">
        <label>Cédula *</label>
        <input type="text" id="r-cedula" placeholder="1234567890" inputmode="numeric">
      </div>
    </div>
    <div class="row">
      <div class="form-group">
        <label>Celular Colombia (WhatsApp) *</label>
        <input type="tel" id="r-phone" placeholder="3001234567" autocomplete="tel">
      </div>
      <div class="form-group">
        <label>Correo electrónico *</label>
        <input type="email" id="r-email" placeholder="maria@email.com" autocomplete="email">
      </div>
    </div>

    <h3 style="margin-top:24px">Autorización</h3>
    <label class="check" style="align-items:flex-start;background:#f6f8fb;padding:14px;border-radius:8px;border:1px solid #e5e7eb">
      <input type="checkbox" id="c-all">
      <span style="font-size:13px;line-height:1.55">
        Acepto los <a href="#" onclick="modal('m-terms');return false">Términos y Condiciones</a>,
        autorizo el tratamiento de mis datos personales conforme a la
        <a href="#" onclick="modal('m-data');return false">Política de Habeas Data</a> (Ley 1581 de 2012)
        y autorizo a <b>Galeano Herrera | Abogados</b> a contactarme con fines comerciales por
        WhatsApp, llamada o correo. *
      </span>
    </label>

    <button class="btn" onclick="enviarRegistro()" style="margin-top:18px">📲 Enviarme código por WhatsApp</button>
    <div class="spinner" id="spinner-3"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Enviando código…</div>
    <div id="err-3"></div>
  </div>

  <!-- STEP 4: OTP -->
  <div class="card step" id="step-4">
    <div class="nav-step">Paso 4 de 5</div>
    <h2>Ingresa el código</h2>
    <p class="muted" id="otp-msg" style="margin-bottom:20px">Te enviamos un código de 6 dígitos por WhatsApp.</p>

    <div class="form-group">
      <label>Código de 6 dígitos</label>
      <input type="text" id="r-otp" class="otp-input" maxlength="6" inputmode="numeric" autocomplete="one-time-code" placeholder="······">
    </div>
    <button class="btn" onclick="verificarOtp()">Verificar y ver mi caso completo</button>
    <div class="spinner" id="spinner-4"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Verificando…</div>
    <div id="err-4"></div>
    <p class="muted" style="margin-top:14px;text-align:center">¿No recibiste el código? <a href="#" onclick="reenviarOtp();return false" style="color:var(--azul)">Reenviar</a></p>
  </div>

  <!-- STEP 5: ÉXITO + AGENDA -->
  <div class="card step" id="step-5">
    <div class="nav-step">Paso 5 de 5</div>
    <div class="alert alert-ok" style="text-align:center;padding:24px">
      <div style="font-size:48px;margin-bottom:8px">✅</div>
      <h2 style="color:#14532d">¡Verificado!</h2>
      <p style="margin-top:8px">Tu simulación está desbloqueada y un abogado fue notificado de tu caso.</p>
    </div>

    <button class="btn" id="btn-descargar" style="margin-bottom:14px">📥 Descargar simulación (.docx)</button>

    <!-- UPSELL: sin papeleos + 10% descuento -->
    <div id="upsell-box" style="background:linear-gradient(135deg,#C5A059 0%,#b08a47 100%);color:#fff;padding:22px;border-radius:12px;margin:18px 0;text-align:left">
      <div style="font-size:18px;font-weight:800;margin-bottom:8px">📋 ¿No quieres papeleos?</div>
      <div style="font-size:14px;margin-bottom:12px;opacity:.95;line-height:1.5">
        Que un abogado de Galeano Herrera presente TODO por ti:<br>
        ✓ Radicación en el juzgado · ✓ Seguimiento del fallo<br>
        ✓ Notificación al accionado · ✓ Atención de impugnaciones
      </div>
      <div style="background:rgba(255,255,255,.2);padding:10px 14px;border-radius:6px;margin-bottom:12px;font-size:15px;font-weight:700">
        🎁 Descuento del 10% si contratas HOY
      </div>
      <a id="upsell-wa" href="#" target="_blank" rel="noopener"
         style="display:block;background:#16a34a;color:#fff;padding:13px;border-radius:8px;text-align:center;font-weight:700;text-decoration:none;font-size:15px">
        💬 Hablar ya con un abogado por WhatsApp
      </a>
    </div>

    <div id="agenda-block">
      <h3 style="margin-top:24px">🗓️ Agenda tu llamada gratuita</h3>
      <p class="muted" style="margin-bottom:16px">Habla 30 minutos por <b>WhatsApp</b> con un abogado especializado. Sin costo, sin compromiso. El abogado te marca a la hora acordada.</p>
      <div id="lawyer-info"></div>
      <div id="slots-cont"><div class="spinner on"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Buscando horarios disponibles…</div></div>
      <button class="btn green" id="btn-confirmar-cita" style="display:none;margin-top:14px">📅 Confirmar cita</button>
      <div id="agenda-result"></div>
    </div>

    <div class="alert alert-info" style="margin-top:20px">
      <strong>Próximo paso:</strong> Si no agendas ahora, un abogado te escribirá por WhatsApp en horario hábil.
    </div>
  </div>

  <!-- STEP 6: CITA CONFIRMADA -->
  <div class="card step" id="step-6">
    <div class="alert alert-ok" style="text-align:center;padding:32px">
      <div style="font-size:56px;margin-bottom:8px">🎉</div>
      <h2 style="color:#14532d">¡Cita agendada!</h2>
      <div id="cita-info" style="margin-top:14px;font-size:16px"></div>
    </div>
    <div class="alert alert-info" style="margin-top:14px">
      <b>📱 El abogado te llamará por WhatsApp</b> a este número a la hora acordada.<br>
      <b>🔔 Recordatorios:</b> 24 h y 1 h antes.<br>
      <b>⏰ Cancelación:</b> hasta 60 minutos antes de la cita.
    </div>
    <button class="btn outline" onclick="window.location.href='/'">Volver al inicio</button>
  </div>
</div>

<!-- ÁREAS QUE CUBRIMOS -->
<section class="bloque gris" id="casos">
  <div class="container-wide">
    <h2 class="section-title">Áreas que cubrimos</h2>
    <p class="section-sub">Tipos de procesos para los que la base jurisprudencial está entrenada. Cada simulación cita radicados verificables de la CSJ.</p>
    <div class="casos-grid">
      <div class="caso">
        <div class="titulo">🏥 Salud · Tutelas contra EPS</div>
        <div class="desc">Negativas de medicamentos, cirugías, tratamientos oncológicos y exámenes prescritos. Principio de continuidad, integralidad y mínimo vital en salud.</div>
      </div>
      <div class="caso">
        <div class="titulo">🤰 Laboral · Fuero materno y despidos</div>
        <div class="desc">Despidos durante embarazo, licencia de maternidad o lactancia. Estabilidad laboral reforzada. Contratos disfrazados de prestación de servicios.</div>
      </div>
      <div class="caso">
        <div class="titulo">👴 Pensiones · Colpensiones y AFP</div>
        <div class="desc">Mora en el reconocimiento pensional, indemnización sustitutiva, sustitución pensional y pensión de invalidez.</div>
      </div>
      <div class="caso">
        <div class="titulo">🚗 Accidentes de tránsito · SOAT</div>
        <div class="desc">Negativa de aseguradoras a cubrir atención médica, incapacidades e indemnizaciones tras accidentes de tránsito.</div>
      </div>
      <div class="caso">
        <div class="titulo">📉 Insolvencia · Persona natural</div>
        <div class="desc">Régimen de insolvencia Ley 1564. Protección frente a embargos sobre el mínimo vital.</div>
      </div>
      <div class="caso">
        <div class="titulo">⚖️ Derechos fundamentales</div>
        <div class="desc">Debido proceso, mora judicial, fotomultas, cobros coactivos, acceso a documentos públicos y derecho de petición.</div>
      </div>
    </div>
  </div>
</section>

<!-- CÓMO FUNCIONA -->
<section class="bloque" id="como-funciona">
  <div class="container-wide">
    <h2 class="section-title">Cómo funciona</h2>
    <p class="section-sub">Diseñado para que cualquier persona, sin conocimientos legales, pueda preparar su caso con seguridad.</p>
    <div class="casos-grid">
      <div class="caso">
        <div class="titulo">1. Análisis de tu caso</div>
        <div class="desc">Un motor de IA jurídica busca dentro de 625 sentencias reales de la Sala Civil, Laboral, Penal y Plena de la CSJ los precedentes que mejor encajan con tu situación.</div>
      </div>
      <div class="caso">
        <div class="titulo">2. Simulación profesional</div>
        <div class="desc">Generamos un borrador de tutela estructurado: hechos, derechos vulnerados, fundamentos jurisprudenciales con radicados reales, pretensiones y pruebas a anexar.</div>
      </div>
      <div class="caso">
        <div class="titulo">3. Validación por abogado</div>
        <div class="desc">Un abogado de Galeano Herrera revisa contigo el caso por Meet o WhatsApp, te dice si es viable, qué probabilidad de éxito tiene y cuánto vale presentarla.</div>
      </div>
    </div>
  </div>
</section>

<!-- FAQ -->
<section class="bloque gris" id="faq">
  <div class="container">
    <h2 class="section-title">Preguntas frecuentes</h2>
    <p class="section-sub" style="margin-bottom:24px">Lo que la mayoría de personas pregunta antes de agendar.</p>

    <details><summary>¿Es realmente gratis?</summary>
    <div class="body">La simulación, el documento Word y la primera llamada de 30 minutos con un abogado son gratis. Para referencia, un abogado particular suele cobrar entre $400.000 y $1.000.000 por presentar una tutela de salud; nuestros honorarios para casos estándar se mueven en un rango considerablemente menor y los conversamos durante la llamada según la complejidad.</div></details>

    <details><summary>¿La simulación sirve para presentarla yo mismo en el juzgado?</summary>
    <div class="body">Es un excelente punto de partida, pero <b>no recomendamos</b> presentarla sin que un abogado la revise. La tutela tiene requisitos formales (legitimación, subsidiariedad, inmediatez) que un juez puede usar para inadmitirla. La revisión por nuestro equipo cuesta menos de lo que te ahorras.</div></details>

    <details><summary>¿Cómo sé que los precedentes que cita son reales?</summary>
    <div class="body">Cada radicado citado (ejemplo: STC8916-2023) está en el índice oficial de la Relatoría de la Corte Suprema. Puedes verificarlo en <a href="https://relatoria.cortesuprema.gov.co" target="_blank">relatoria.cortesuprema.gov.co</a>. Nuestro motor está diseñado para nunca inventar radicados.</div></details>

    <details><summary>¿Qué hacen con mis datos?</summary>
    <div class="body">Tus datos están protegidos por la <a href="#" onclick="modal('m-data');return false">Ley 1581 de 2012</a>. Solo se usan para generar tu simulación, contactarte sobre tu caso y enviarte información comercial relacionada. Puedes pedir su eliminación en cualquier momento escribiendo a contacto@galeanoherrera.co.</div></details>

    <details><summary>¿Por qué necesitan verificarme con OTP?</summary>
    <div class="body">Para evitar que bots o personas malintencionadas abusen del sistema. El código que recibes por WhatsApp confirma que el celular es tuyo y nos permite asignarte un abogado real.</div></details>

    <details><summary>¿Qué pasa si no puedo asistir a la cita agendada?</summary>
    <div class="body">Puedes <b>cancelar o reprogramar</b> hasta 60 minutos antes desde el mismo enlace. Después de eso, contáctanos por WhatsApp para que el abogado te asigne un nuevo espacio.</div></details>

    <details><summary>¿Atienden en toda Colombia?</summary>
    <div class="body">Sí. Las tutelas se pueden presentar electrónicamente y atendemos casos de todo el país por Meet/WhatsApp. Si tu caso requiere presencialidad (audiencias particulares), te derivamos a un abogado aliado en tu ciudad.</div></details>
  </div>
</section>

<!-- CTA STICKY MOBILE -->
<div class="cta-sticky" id="cta-sticky">
  <button class="btn" style="padding:10px 18px;font-size:14px" onclick="document.getElementById('step-1').scrollIntoView({behavior:'smooth'});document.getElementById('descripcion').focus();">Generar simulación</button>
</div>

<div class="disclaimer-fijo">
  <b>⚠ Importante:</b> Las simulaciones son orientativas, basadas en líneas jurisprudenciales reales y pensadas para validarse con un abogado. No constituyen asesoría jurídica autónoma.
</div>

<footer>
  <div class="logo">Galeano <span>Herrera</span></div>
  <p>© 2026 · Galeano Herrera | Abogados · Colombia</p>
  <p style="margin-top:6px"><a href="#" onclick="modal('m-terms');return false">Términos</a> · <a href="#" onclick="modal('m-data');return false">Habeas Data</a> · <a href="/pro/login">Acceso abogados</a></p>
</footer>

<!-- MODALES -->
<div class="modal-bg" id="m-terms">
  <div class="modal">
    <span class="modal-close" onclick="cerrarModal()">×</span>
    <h3>Términos y Condiciones</h3>
    <div style="font-size:13px;line-height:1.6">
    <p><b>1. Naturaleza del servicio.</b> Galeano Herrera | Abogados pone a disposición una herramienta tecnológica que, mediante inteligencia artificial, genera <b>simulaciones</b> de acciones de tutela basadas en líneas jurisprudenciales reales de la Corte Suprema de Justicia de Colombia.</p>
    <p><b>2. No es asesoría jurídica autónoma.</b> Las simulaciones son insumos para el análisis de un abogado. <b>No reemplazan</b> la asesoría profesional ni garantizan el éxito de la acción.</p>
    <p><b>3. Validación obligatoria.</b> Te comprometes a no presentar la simulación ante autoridad alguna sin la revisión previa de un abogado titulado.</p>
    <p><b>4. Limitación de responsabilidad.</b> Galeano Herrera no responde por las consecuencias derivadas del uso de la simulación sin asesoría profesional.</p>
    <p><b>5. Uso adecuado.</b> Está prohibido usar el servicio para casos hipotéticos, fines ilícitos, hostigamiento o automatización masiva.</p>
    <p><b>6. Propiedad intelectual.</b> El sistema, su diseño y su modelo son propiedad de Galeano Herrera | Abogados.</p>
    <p><b>7. Modificaciones.</b> La firma puede modificar estos términos. La versión vigente está siempre en este sitio.</p>
    <p><b>8. Jurisdicción.</b> Estos términos se rigen por la legislación colombiana. Cualquier controversia se ventila ante los jueces competentes de Bogotá D.C.</p>
    </div>
  </div>
</div>

<div class="modal-bg" id="m-data">
  <div class="modal">
    <span class="modal-close" onclick="cerrarModal()">×</span>
    <h3>Política de Tratamiento de Datos · Ley 1581/2012</h3>
    <div style="font-size:13px;line-height:1.6">
    <p><b>Responsable:</b> Galeano Herrera | Abogados, Colombia. Correo: contacto@galeanoherrera.co</p>
    <p><b>Datos recolectados:</b> nombre, cédula, celular, correo, descripción del caso, IP, registro de actividad.</p>
    <p><b>Finalidades:</b></p>
    <ul style="padding-left:20px;margin:8px 0">
      <li>Generar la simulación solicitada.</li>
      <li>Verificar identidad mediante código OTP por WhatsApp.</li>
      <li>Contactarle para ofrecer servicios legales.</li>
      <li>Enviarle información comercial relacionada.</li>
      <li>Cumplir obligaciones legales y fines estadísticos.</li>
    </ul>
    <p><b>Derechos:</b> conocer, actualizar, rectificar, suprimir y revocar la autorización en cualquier momento.</p>
    <p><b>Conservación:</b> el tiempo necesario para las finalidades descritas.</p>
    <p><b>Transferencia:</b> no se ceden a terceros sin autorización, salvo requerimiento de autoridad competente.</p>
    </div>
  </div>
</div>

<script>
let currentToken = null, currentPhone = null, selectedSlot = null, calendarEnabled = false;

function show(id){
  document.querySelectorAll('.step').forEach(s=>s.classList.remove('on'));
  document.getElementById(id).classList.add('on');
  window.scrollTo({top:0,behavior:'smooth'});
}
function spin(id,on){document.getElementById(id).classList.toggle('on',on);}
function err(id,msg){document.getElementById(id).innerHTML=msg?`<div class="alert alert-err">${msg}</div>`:'';}
function modal(id){document.getElementById(id).classList.add('on');}
function cerrarModal(){document.querySelectorAll('.modal-bg').forEach(m=>m.classList.remove('on'));}
document.querySelectorAll('.modal-bg').forEach(m=>m.addEventListener('click',e=>{if(e.target===m)cerrarModal();}));

async function track(type, payload){
  try{await fetch('/api/track',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type,payload})});}catch(e){}
  // Facebook Pixel events si está cargado
  try{
    if(typeof fbq === 'function'){
      if(type === 'preview_done')        fbq('track','Lead');
      else if(type === 'register')       fbq('track','CompleteRegistration');
      else if(type === 'otp_verified')   fbq('track','Contact');
      else if(type === 'downloaded')     fbq('trackCustom','SimulacionDescargada');
      else if(type === 'meeting_booked') fbq('track','Schedule');
    }
  }catch(e){}
}

// CTA sticky en mobile cuando scrollee
window.addEventListener('scroll',()=>{
  document.getElementById('cta-sticky').classList.toggle('show', window.scrollY > 600);
});

// ─── Wizard carrusel ─────────────────────────────────────────
let wizStep = 1;
const WIZ_HINTS = {
  salud:      {acc:'Ej: EPS Sanitas, Sura, Compensar, Salud Total…', lbl:'Tu EPS o IPS',
               ej:'Mi EPS Sanitas me niega desde hace 2 meses la cirugía de rodilla que ordenó el ortopedista. Ya radiqué PQR y no responden. Tengo dolor crónico y no puedo caminar bien. Tengo copia de la orden médica.'},
  pensiones:  {acc:'Ej: Colpensiones, Porvenir, Protección, Old Mutual…', lbl:'Administradora de pensiones',
               ej:'Radiqué mi solicitud de pensión de vejez en Colpensiones en enero. Hoy no me han respondido. Tengo 63 años y 1500 semanas cotizadas. Dependo de la pensión para vivir.'},
  laboral:    {acc:'Ej: nombre exacto de la empresa o empleador', lbl:'Empresa / empleador',
               ej:'Me despidieron el 15 de marzo estando en el sexto mes de embarazo. Tenía contrato a término indefinido desde hace 3 años. La empresa no pidió permiso al Ministerio del Trabajo.'},
  accidentes: {acc:'Ej: Previsora, Seguros Bolívar, Sura SOAT…', lbl:'Aseguradora SOAT',
               ej:'Tuve un accidente en moto el 10 de marzo. La aseguradora SOAT negó cobertura alegando que el otro conductor estaba ebrio. Yo no lo estaba y tengo 50% de pérdida capacidad por fractura.'},
  insolvencia:{acc:'Ej: Banco Bogotá, Davivienda, Bancolombia…', lbl:'Entidad que embarga',
               ej:'El banco embargó mi cuenta de ahorros donde me depositan el salario mínimo cada mes. Es la única cuenta que tengo. Sin ese dinero no puedo comer ni pagar arriendo.'},
  derechos_fundamentales:{acc:'Ej: DIAN, Juzgado X, Alcaldía…', lbl:'Entidad accionada',
               ej:'Presenté derecho de petición a la Alcaldía hace 45 días y no me han respondido. Solicité copia de un expediente al que tengo derecho. La ley da 15 días de plazo.'},
};

function aplicarHintsArea(area, placeholderTextarea=true){
  const h = WIZ_HINTS[area]; if(!h) return;
  const lbl = document.querySelector('#wiz-2 label'); if(lbl) lbl.textContent = h.lbl;
  const inp = document.getElementById('o-accionado'); if(inp) inp.placeholder = h.acc;
  const ta = document.getElementById('descripcion');
  if(ta && placeholderTextarea) ta.placeholder = h.ej;
}

// Selección de tipo (paso 1.1)
document.querySelectorAll('.tipo-card').forEach(c=>c.addEventListener('click',()=>{
  document.querySelectorAll('.tipo-card').forEach(x=>x.classList.remove('sel'));
  c.classList.add('sel');
  const area = c.dataset.area;
  document.getElementById('area').value = area;
  document.getElementById('wiz-next-1').disabled = false;
  aplicarHintsArea(area);
}));

// Acción bar: scroll al wizard
function scrollToWizard(ev){
  if(ev) ev.preventDefault();
  const el = document.getElementById('step-1');
  if(el) el.scrollIntoView({behavior:'smooth', block:'start'});
  setTimeout(()=>{
    const first = document.querySelector('.tipo-card');
    if(first) first.focus();
  }, 400);
}

// Carrusel casos: navegación con flechas
function scrollCases(dir){
  const s = document.getElementById('cases-scroll');
  if(!s) return;
  s.scrollBy({left: dir * 320, behavior:'smooth'});
}

// Click en case-card → preconfigura el wizard y salta a paso 4
document.querySelectorAll('.case-card').forEach(c=>c.addEventListener('click',()=>{
  const area = c.dataset.area;
  const ej = c.dataset.ej || '';
  // marcar la tarjeta del tipo
  document.querySelectorAll('.tipo-card').forEach(x=>{
    x.classList.toggle('sel', x.dataset.area === area);
  });
  document.getElementById('area').value = area;
  document.getElementById('wiz-next-1').disabled = false;
  aplicarHintsArea(area, false);   // no sobreescribir placeholder textarea porque llenamos value
  // llenar textarea con el ejemplo (editable por el usuario)
  const ta = document.getElementById('descripcion');
  if(ta){ ta.value = ej; }
  // ir al paso 4 directo
  wizShow(4);
  scrollToWizard();
}));

function wizShow(n){
  wizStep = n;
  document.querySelectorAll('.wiz-panel').forEach(p=>p.classList.remove('on'));
  document.getElementById('wiz-'+n).classList.add('on');
  document.querySelectorAll('.wiz-dot').forEach(d=>{
    d.classList.toggle('on', parseInt(d.dataset.s) <= n);
  });
  document.getElementById('wiz-bar').style.width = (n*20) + '%';
  // Scroll al top del card
  document.getElementById('step-1').scrollIntoView({behavior:'smooth',block:'start'});
}
function wizNext(from){
  if(from===4){
    const desc = document.getElementById('descripcion').value.trim();
    if(desc.length < 30){err('err-1','Escribe al menos una historia de 3 frases (mínimo 30 caracteres).');return;}
  }
  wizShow(from+1);
}
function wizPrev(from){ wizShow(from-1); }

async function generarPreview(){
  const desc = document.getElementById('descripcion').value.trim();
  if(desc.length < 30){err('err-1','Cuéntanos más detalle (mínimo 30 caracteres). ¿Qué pasó, contra quién y desde cuándo?');wizShow(4);return;}
  err('err-1','');
  spin('spinner-1', true);
  try{
    // Componer descripción enriquecida (fecha + reclamo previo si los dio)
    let descFinal = desc;
    const fecha = (document.getElementById('o-fecha')||{}).value;
    const recl = (document.getElementById('o-reclamo')||{}).value;
    if(fecha){ descFinal = `Fecha del hecho: ${fecha}. ` + descFinal; }
    if(recl === 'si_sin_respuesta') descFinal += ' He radicado reclamación ante la entidad sin recibir respuesta.';
    else if(recl === 'si_negado') descFinal += ' Reclamé y la entidad me negó lo solicitado.';
    else if(recl === 'no') descFinal += ' Aún no he radicado reclamación formal.';

    const body = {
      descripcion: descFinal,
      area: document.getElementById('area').value || null,
      nombre: (document.getElementById('o-nombre')||{}).value || null,
      cedula: (document.getElementById('o-cedula')||{}).value || null,
      ciudad: (document.getElementById('o-ciudad')||{}).value || null,
      accionado: (document.getElementById('o-accionado')||{}).value || null,
    };
    const r = await fetch('/api/lead/preview',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)});
    const d = await r.json();
    if(!r.ok){throw new Error(d.detail || 'Error generando');}
    currentToken = d.token;
    document.getElementById('preview-visible').textContent = d.preview.visible;
    const fichasHtml = d.fichas.map(f=>`<span class="fichas-tag">${f.id} · ${f.sala} ${f.anio}</span>`).join(' ');
    document.getElementById('alert-fichas').innerHTML =
      `<b>📚 Tu simulación se basa en ${d.fichas.length} sentencias reales de la CSJ:</b><br>${fichasHtml}` +
      (d.area_detectada ? `<br><br><b>Área detectada:</b> ${d.area_detectada}` : '');
    show('step-2');
  }catch(e){err('err-1', e.message);}
  spin('spinner-1', false);
}

function irRegistro(){show('step-3');}

async function enviarRegistro(){
  const all = document.getElementById('c-all').checked;
  const data = {
    token: currentToken,
    name:   document.getElementById('r-nombre').value.trim(),
    cedula: document.getElementById('r-cedula').value.trim(),
    phone:  document.getElementById('r-phone').value.trim(),
    email:  document.getElementById('r-email').value.trim(),
    consent_terms:     all,
    consent_data:      all,
    consent_marketing: all,
  };
  if(!data.name || !data.cedula || !data.phone || !data.email){err('err-3','Completa todos los campos obligatorios.');return;}
  if(!all){err('err-3','Debes aceptar la autorización para continuar.');return;}
  err('err-3',''); spin('spinner-3', true);
  try{
    const r = await fetch('/api/lead/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    const d = await r.json();
    if(!r.ok){throw new Error(d.detail || 'Error');}
    currentPhone = d.phone_normalized;
    document.getElementById('otp-msg').innerHTML = `Código enviado a <b>+${currentPhone}</b>` + (d.otp_debug ? `<br><br><b style="color:var(--rojo)">DEV: el código es ${d.otp_debug}</b>` : '');
    show('step-4');
  }catch(e){err('err-3', e.message);}
  spin('spinner-3', false);
}

async function verificarOtp(){
  const otp = document.getElementById('r-otp').value.trim();
  if(otp.length !== 6){err('err-4','Ingresa los 6 dígitos.');return;}
  err('err-4',''); spin('spinner-4', true);
  try{
    const r = await fetch('/api/lead/verify-otp',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({token:currentToken, otp:otp})});
    const d = await r.json();
    if(!r.ok){throw new Error(d.detail || 'Código incorrecto');}
    document.getElementById('btn-descargar').onclick = ()=>window.location.href = d.download_url;
    show('step-5');
    cargarSlots();
  }catch(e){err('err-4', e.message);}
  spin('spinner-4', false);
}

async function reenviarOtp(){
  if(!currentToken)return;
  spin('spinner-4', true);
  try{
    const r = await fetch('/api/lead/resend-otp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:currentToken})});
    if(!r.ok){const d=await r.json();throw new Error(d.detail||'Error');}
    err('err-4','<div class="alert alert-ok">Código reenviado.</div>');
    setTimeout(()=>err('err-4',''),3000);
  }catch(e){err('err-4', e.message);}
  spin('spinner-4', false);
}

async function cargarSlots(){
  try{
    const r = await fetch('/api/lead/slots?token='+currentToken+'&days=7');
    const d = await r.json();
    if(d.lawyer){
      document.getElementById('lawyer-info').innerHTML =
        `<div class="alert alert-gold"><b>👨‍⚖️ Abogado asignado:</b> ${d.lawyer.name}<br><span class="muted">Te llamará por WhatsApp a la hora que elijas.</span></div>`;
      // Enganchar el botón del upsell con WhatsApp del abogado + mensaje prearmado
      if(d.lawyer.whatsapp){
        const msg = encodeURIComponent(
          `Hola ${d.lawyer.name}, acabo de descargar mi simulación de tutela en Galeano Herrera y me interesa el descuento del 10% para que presenten todo el proceso por mí. ¿Podemos coordinar?`
        );
        document.getElementById('upsell-wa').href = `https://wa.me/${d.lawyer.whatsapp}?text=${msg}`;
      }
    }
    if(!d.slots || !d.slots.length){
      document.getElementById('slots-cont').innerHTML = '<div class="alert alert-info">No hay horarios disponibles los próximos días. El abogado te contactará por WhatsApp para coordinar.</div>';
      return;
    }
    const html = d.slots.map(s=>`
      <div class="slot" data-start="${s.start}" onclick="seleccionarSlot(this)">
        <span class="day">${s.label.split(' · ')[0]}</span>
        ${s.label.split(' · ')[1]}
      </div>`).join('');
    document.getElementById('slots-cont').innerHTML = `<div class="slots-grid">${html}</div>`;
  }catch(e){
    document.getElementById('slots-cont').innerHTML = '<div class="alert alert-err">Error cargando horarios.</div>';
  }
}

function seleccionarSlot(el){
  document.querySelectorAll('.slot').forEach(s=>s.classList.remove('selected'));
  el.classList.add('selected');
  selectedSlot = el.dataset.start;
  document.getElementById('btn-confirmar-cita').style.display = 'block';
}

document.addEventListener('click',e=>{
  if(e.target.id === 'btn-confirmar-cita'){
    if(!selectedSlot)return;
    confirmarCita();
  }
});

async function confirmarCita(){
  document.getElementById('btn-confirmar-cita').disabled = true;
  document.getElementById('btn-confirmar-cita').textContent = 'Agendando…';
  try{
    const r = await fetch('/api/lead/book',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({token:currentToken, start_iso:selectedSlot, duration_min:30})});
    const d = await r.json();
    if(!r.ok)throw new Error(d.detail||'Error');
    const dt = new Date(d.start);
    const fmt = dt.toLocaleString('es-CO',{weekday:'long',day:'numeric',month:'long',hour:'2-digit',minute:'2-digit'});
    document.getElementById('cita-info').innerHTML = `
      <div style="margin-bottom:12px"><b>📅 ${fmt} (Bogotá)</b></div>
      <div style="margin-bottom:12px">👨‍⚖️ Abogado: <b>${d.lawyer_name||''}</b></div>
      <div class="muted">Te enviamos confirmación por WhatsApp.</div>`;
    show('step-6');
  }catch(e){
    document.getElementById('agenda-result').innerHTML = '<div class="alert alert-err">'+e.message+'</div>';
    document.getElementById('btn-confirmar-cita').disabled = false;
    document.getElementById('btn-confirmar-cita').textContent = '📅 Confirmar cita';
  }
}

// Cargar stat real (cantidad de sentencias indexadas)
async function cargarStats(){
  try{
    const r = await fetch('/salud');
    const s = await r.json();
    document.getElementById('s-fichas').textContent = (s.fichas||'').toLocaleString('es-CO');
  }catch(e){}
}
cargarStats();
</script>
</body>
</html>"""


# =============================================================================
# LAWYER LOGIN
# =============================================================================

def lawyer_login_html() -> str:
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Acceso Abogados · Galeano Herrera</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}
  body{background:linear-gradient(135deg,#002347 0%,#003f7a 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;}
  .login-card{background:#fff;padding:40px;border-radius:14px;width:100%;max-width:420px;box-shadow:0 20px 60px rgba(0,0,0,.3);}
  .logo{text-align:center;font-size:24px;font-weight:800;color:#002347;margin-bottom:6px;}
  .logo span{color:#C5A059;}
  .sub{text-align:center;color:#666;font-size:13px;margin-bottom:28px;letter-spacing:1px;text-transform:uppercase;}
  label{display:block;font-size:12px;font-weight:700;color:#002347;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}
  input{width:100%;padding:12px 14px;border:2px solid #dce3ef;border-radius:8px;font-size:15px;}
  input:focus{outline:none;border-color:#002347;}
  .form-group{margin-bottom:18px;}
  .btn{background:#002347;color:#fff;border:none;padding:14px;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;width:100%;}
  .btn:hover{background:#003f7a;}
  .err{background:#ffebee;color:#b71c1c;padding:10px;border-radius:6px;font-size:13px;margin-bottom:14px;}
  .info{font-size:12px;color:#888;text-align:center;margin-top:18px;}
  .info a{color:#002347;}
</style></head><body>
<form class="login-card" method="POST" action="/pro/login">
  <div class="logo">Galeano <span>Herrera</span></div>
  <div class="sub">Acceso Abogados</div>
  ERR_PLACEHOLDER
  <div class="form-group">
    <label>Correo electrónico</label>
    <input type="email" name="email" required autofocus>
  </div>
  <div class="form-group">
    <label>Contraseña</label>
    <input type="password" name="password" required>
  </div>
  <button class="btn" type="submit">Ingresar</button>
  <div class="info">¿Aún no tienes acceso? Pídelo al administrador.<br>
    <a href="/">← Ver landing pública</a>
  </div>
</form>
<script>
  if(location.search.includes('err=1')){
    document.querySelector('.login-card').insertBefore(
      Object.assign(document.createElement('div'),{className:'err',textContent:'Email o contraseña incorrectos.'}),
      document.querySelector('.form-group')
    );
  }
</script>
</body></html>""".replace("ERR_PLACEHOLDER", "")


# =============================================================================
# LAWYER DASHBOARD
# =============================================================================

def lawyer_dashboard_html(lawyer: dict) -> str:
    name = (lawyer.get("name") or "Abogado").replace("'", "&#39;")
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard · Galeano Herrera</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}
  body{background:#f4f6f9;color:#1a2332;}
  header{background:#002347;color:#fff;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #C5A059;}
  header h1{font-size:18px;}
  header .me{display:flex;align-items:center;gap:14px;font-size:13px;}
  header a{color:#C5A059;text-decoration:none;font-size:13px;}
  .container{max-width:1400px;margin:0 auto;padding:20px;}
  .stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px;}
  @media(max-width:780px){.stats{grid-template-columns:repeat(2,1fr);}}
  .stat{background:#fff;padding:16px;border-radius:8px;box-shadow:0 1px 6px rgba(0,35,71,.08);}
  .stat .num{font-size:26px;font-weight:800;color:#002347;}
  .stat .lbl{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;}
  .toggle{display:flex;align-items:center;gap:10px;background:#fff;padding:14px 18px;border-radius:8px;margin-bottom:20px;box-shadow:0 1px 6px rgba(0,35,71,.08);}
  .toggle.on{background:#dcfce7;}
  .toggle.off{background:#fee2e2;}
  .switch{position:relative;display:inline-block;width:50px;height:26px;}
  .switch input{opacity:0;width:0;height:0;}
  .slider{position:absolute;cursor:pointer;inset:0;background:#ccc;transition:.2s;border-radius:26px;}
  .slider:before{position:absolute;content:"";height:20px;width:20px;left:3px;bottom:3px;background:#fff;transition:.2s;border-radius:50%;}
  input:checked + .slider{background:#16a34a;}
  input:checked + .slider:before{transform:translateX(24px);}
  .tabs{display:flex;gap:4px;margin-bottom:18px;border-bottom:2px solid #002347;flex-wrap:wrap;}
  .tab{padding:10px 18px;cursor:pointer;border-radius:6px 6px 0 0;border:2px solid transparent;border-bottom:none;font-weight:600;color:#002347;background:#fff;font-size:13px;}
  .tab.on{background:#002347;color:#fff;}
  .panel{display:none;background:#fff;padding:24px;border-radius:0 8px 8px 8px;box-shadow:0 2px 12px rgba(0,35,71,.08);}
  .panel.on{display:block;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th{background:#f4f6f9;padding:10px;text-align:left;font-weight:700;color:#002347;font-size:12px;text-transform:uppercase;border-bottom:2px solid #002347;}
  td{padding:10px;border-bottom:1px solid #eee;vertical-align:top;}
  tr:hover{background:#fafbfc;}
  .badge{display:inline-block;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:700;}
  .badge.preview{background:#f3f4f6;color:#666;}
  .badge.pending_otp{background:#fef3c7;color:#92400e;}
  .badge.verified{background:#dbeafe;color:#1e40af;}
  .badge.contacted{background:#dcfce7;color:#166534;}
  .badge.closed{background:#e5e7eb;color:#374151;}
  .btn{background:#002347;color:#fff;padding:6px 14px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;}
  .btn.green{background:#16a34a;}.btn.gold{background:#C5A059;}
  .btn.outline{background:transparent;color:#002347;border:1px solid #002347;}
  .btn-sm{padding:4px 10px;font-size:11px;}
  .actions{display:flex;gap:6px;flex-wrap:wrap;}
  .truncate{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;max-width:280px;}
  .rag-tools{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px;}
  @media(max-width:780px){.rag-tools{grid-template-columns:1fr;}}
  .tool-card{background:#fff;padding:18px;border-radius:8px;border:1px solid #dce3ef;cursor:pointer;transition:all .15s;}
  .tool-card:hover{border-color:#C5A059;transform:translateY(-2px);box-shadow:0 4px 14px rgba(197,160,89,.2);}
  .tool-card h4{color:#002347;font-size:15px;margin-bottom:6px;}
  .tool-card p{font-size:12px;color:#666;}
  textarea,input,select{width:100%;padding:10px;border:1px solid #dce3ef;border-radius:5px;font-size:13px;font-family:inherit;}
  .form-group{margin-bottom:14px;}
  label{font-size:11px;font-weight:700;color:#002347;text-transform:uppercase;display:block;margin-bottom:4px;}
  .result{background:#f0f4fa;border-left:4px solid #002347;padding:16px;border-radius:0 6px 6px 0;white-space:pre-wrap;font-size:13px;line-height:1.6;max-height:500px;overflow-y:auto;display:none;}
  .result.on{display:block;}
  .fuentes{font-size:11px;color:#666;margin-top:10px;padding:8px;background:#fff;border-radius:4px;display:none;}
  .fuentes.on{display:block;}
  .fuentes b{color:#002347;}
  .spinner{display:none;text-align:center;padding:14px;color:#002347;font-size:13px;}
  .spinner.on{display:block;}
  .badge-fch{background:#e3f0ff;color:#004a9f;padding:2px 6px;border-radius:8px;font-size:10px;font-weight:700;margin:2px;display:inline-block;}
  /* Meta diaria gamificada */
  .goal-card{background:linear-gradient(135deg,#002347 0%,#003f7a 100%);color:#fff;padding:20px 24px;border-radius:12px;margin-bottom:18px;position:relative;overflow:hidden;}
  .goal-card::after{content:'';position:absolute;top:0;right:0;width:180px;height:100%;background:radial-gradient(circle,rgba(197,160,89,.2) 0%,transparent 70%);}
  .goal-card h3{font-size:13px;color:#C5A059;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;font-weight:700;}
  .goal-card .progress{display:flex;align-items:baseline;gap:10px;margin-bottom:10px;}
  .goal-card .big{font-size:40px;font-weight:800;line-height:1;}
  .goal-card .of{font-size:18px;opacity:.7;}
  .goal-card .lbl{font-size:13px;opacity:.85;}
  .bar{width:100%;height:8px;background:rgba(255,255,255,.15);border-radius:4px;overflow:hidden;}
  .bar .fill{height:100%;background:linear-gradient(90deg,#16a34a 0%,#C5A059 100%);transition:width .5s;}
  .mini-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px;}
  @media(max-width:680px){.mini-stats{grid-template-columns:repeat(2,1fr);}}
  .mini-stat{background:#fff;padding:14px;border-radius:8px;border:1px solid #e5e7eb;box-shadow:0 1px 3px rgba(0,0,0,.04);}
  .mini-stat .k{font-size:22px;font-weight:800;color:#002347;line-height:1;}
  .mini-stat .v{font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-top:5px;font-weight:600;}
  .mini-stat.ok .k{color:#16a34a;}
  .mini-stat.warn .k{color:#C5A059;}
  /* Embudo personal */
  .funnel-personal{background:#fff;padding:18px;border-radius:10px;border:1px solid #e5e7eb;margin-bottom:18px;}
  .funnel-personal h4{color:#002347;font-size:14px;margin-bottom:12px;text-transform:uppercase;letter-spacing:.5px;}
  .funnel-row2{display:flex;align-items:center;gap:12px;margin-bottom:6px;font-size:13px;}
  .funnel-row2 .label2{width:140px;font-weight:600;color:#374151;font-size:12px;}
  .funnel-row2 .bar2{flex:1;height:22px;background:#f3f4f6;border-radius:4px;position:relative;overflow:hidden;}
  .funnel-row2 .bar2 .fill2{height:100%;background:#002347;display:flex;align-items:center;padding-left:8px;color:#fff;font-size:11px;font-weight:700;}

  .meeting-card{background:#f0f9ff;border-left:4px solid #002347;padding:14px;border-radius:0 6px 6px 0;margin-bottom:10px;}
  .meeting-card h4{color:#002347;font-size:14px;margin-bottom:6px;}
  .meeting-card .meta{font-size:12px;color:#555;margin-bottom:6px;}
  .meeting-card a.meet{color:#16a34a;font-weight:700;font-size:13px;text-decoration:none;}

  /* Calendar semanal */
  .cal-nav{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;}
  .cal-nav .range{font-weight:700;color:#002347;}
  .cal-grid{display:grid;grid-template-columns:60px repeat(7,1fr);border:1px solid #e2e8f0;border-radius:8px;overflow:hidden;font-size:11px;min-width:760px;}
  .cal-cell{border-right:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;padding:4px;min-height:32px;}
  .cal-cell:nth-child(8n){border-right:none;}
  .cal-header{background:#002347;color:#fff;padding:8px;text-align:center;font-weight:700;font-size:12px;}
  .cal-header.today{background:#C5A059;}
  .cal-hour{background:#f4f6f9;color:#666;text-align:center;padding:6px 4px;font-weight:700;}
  .cal-slot{cursor:pointer;position:relative;}
  .cal-slot.free{background:#fff;}
  .cal-slot.free:hover{background:#dcfce7;}
  .cal-slot.booked{background:#dbeafe;cursor:pointer;}
  .cal-slot.booked:hover{background:#bfdbfe;}
  .cal-slot.blocked{background:#fee2e2;cursor:pointer;}
  .cal-slot.past,.cal-slot.off_hours{background:#f4f6f9;color:#ccc;}
  .cal-slot.past{cursor:not-allowed;}
  .cal-slot .mini{font-size:9px;font-weight:700;display:block;}
  .cal-slot.booked .mini{color:#1e40af;}
  .cal-slot.blocked .mini{color:#991b1b;}
  .cal-scroll{overflow-x:auto;}
  .legend{display:flex;gap:14px;margin-top:10px;font-size:11px;}
  .legend .lg{display:inline-flex;align-items:center;gap:4px;}
  .legend .sw{width:12px;height:12px;border-radius:2px;display:inline-block;}
</style></head><body>

<header>
  <h1>👨‍⚖️ Dashboard · NAME_PLACEHOLDER</h1>
  <div class="me">
    <span id="me-info"></span>
    <a href="/pro/logout">Salir</a>
  </div>
</header>

<div class="container">

  <div id="toggle-disp" class="toggle">
    <label class="switch"><input type="checkbox" id="sw-disp" onchange="toggleDisp()"><span class="slider"></span></label>
    <span id="toggle-label">Disponible para nuevos casos</span>
  </div>

  <!-- Meta diaria + embudo personal -->
  <div id="goal-block"></div>
  <div class="mini-stats" id="mini-stats"></div>
  <div class="funnel-personal" id="funnel-personal"></div>

  <div class="tabs">
    <div class="tab on" onclick="tab('agenda')">📅 Agenda</div>
    <div class="tab" onclick="tab('leads')">👥 Mis Leads</div>
    <div class="tab" onclick="tab('rag')">⚖ Asistente Jurídico</div>
    <div class="tab" onclick="tab('config')">🔧 Cuenta</div>
  </div>

  <!-- AGENDA -->
  <div class="panel on" id="p-agenda">
    <div class="cal-nav">
      <button class="btn btn-sm outline" onclick="semanaPrev()">◀ Semana anterior</button>
      <div class="range" id="cal-range">—</div>
      <button class="btn btn-sm outline" onclick="semanaNext()">Semana siguiente ▶</button>
    </div>
    <div class="cal-scroll"><div id="cal-grid"></div></div>
    <div class="legend">
      <span class="lg"><span class="sw" style="background:#fff;border:1px solid #e2e8f0"></span> Libre</span>
      <span class="lg"><span class="sw" style="background:#dbeafe"></span> Cita agendada</span>
      <span class="lg"><span class="sw" style="background:#fee2e2"></span> Bloqueado</span>
      <span class="lg"><span class="sw" style="background:#f4f6f9"></span> Fuera de horario / pasado</span>
    </div>

    <h3 style="margin:24px 0 14px;color:#002347">Próximas citas</h3>
    <div id="appts-cont">Cargando…</div>
  </div>

  <!-- LEADS -->
  <div class="panel" id="p-leads">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <h3 style="color:#002347">Leads asignados</h3>
      <select id="filter-leads" onchange="loadLeads()" style="width:200px">
        <option value="">Todos los estados</option>
        <option value="verified">Verificados (sin contactar)</option>
        <option value="contacted">Contactados</option>
        <option value="closed">Cerrados</option>
      </select>
    </div>
    <div style="overflow-x:auto"><table id="t-leads"><thead><tr>
      <th>Fecha</th><th>Cliente</th><th>Contacto</th><th>Área</th>
      <th>Caso</th><th>Estado</th><th>Acciones</th>
    </tr></thead><tbody></tbody></table></div>
  </div>

  <!-- RAG TOOLS -->
  <div class="panel" id="p-rag">
    <h3 style="margin-bottom:18px;color:#002347">Asistente jurídico potente — RAG sobre 625 sentencias CSJ</h3>
    <div class="rag-tools">
      <div class="tool-card" onclick="ragTool('consultar')"><h4>🔍 Consulta libre</h4><p>Pregunta abierta sobre cualquier tema. Devuelve análisis con precedentes.</p></div>
      <div class="tool-card" onclick="ragTool('caso')"><h4>📋 Análisis de caso</h4><p>Protocolo Galeano: clasificación + diagnóstico + estrategia + precedentes.</p></div>
      <div class="tool-card" onclick="ragTool('tutela')"><h4>⚖ Generar tutela completa</h4><p>Borrador profesional con datos del cliente, listo para firmar.</p></div>
      <div class="tool-card" onclick="ragTool('linea')"><h4>📈 Línea jurisprudencial</h4><p>Tesis dominante de la Corte sobre un tema, evolución y excepciones.</p></div>
    </div>

    <div id="rag-form"></div>
    <div class="spinner" id="rag-spinner">⏳ Analizando con jurisprudencia real…</div>
    <div class="result" id="rag-result"></div>
    <div class="fuentes" id="rag-fuentes"></div>
  </div>

  <!-- CONFIG -->
  <div class="panel" id="p-config">
    <h3 style="margin-bottom:14px;color:#002347">Datos de mi cuenta</h3>
    <div id="my-info" style="background:#f4f6f9;padding:14px;border-radius:6px;font-size:13px;margin-bottom:18px"></div>

    <h4 style="color:#002347;margin-bottom:8px">Cambiar contraseña</h4>
    <div class="form-group" style="max-width:400px">
      <label>Nueva contraseña</label>
      <input type="password" id="new-pwd" placeholder="Mínimo 8 caracteres">
    </div>
    <button class="btn" onclick="cambiarPwd()" style="max-width:200px">Actualizar</button>
    <div id="pwd-msg" style="margin-top:10px;font-size:13px"></div>
  </div>

</div>

<script>
let me = null;

async function api(url,opts){
  const r=await fetch(url,opts);
  if(!r.ok){const d=await r.json().catch(()=>({}));throw new Error(d.detail||'Error '+r.status);}
  return r.json();
}

function tab(name){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
  document.querySelector(`[onclick="tab('${name}')"]`).classList.add('on');
  document.getElementById('p-'+name).classList.add('on');
  if(name==='leads')loadLeads();
  if(name==='agenda'){loadCal(); loadAppts();}
  if(name==='config')loadMe();
}

async function loadMe(){
  me = await api('/api/pro/me');
  document.getElementById('me-info').textContent = me.email || me.name;
  document.getElementById('sw-disp').checked = me.available;
  updateToggleLabel();
  document.getElementById('my-info').innerHTML = `
    <div><b>Nombre:</b> ${me.name}</div>
    <div><b>Email:</b> ${me.email||'—'}</div>
    <div><b>WhatsApp:</b> +${me.whatsapp}</div>
    <div><b>Áreas:</b> ${(me.areas||[]).join(', ')||'—'}</div>
    <div><b>Estado:</b> ${me.available?'✅ Disponible para nuevos leads':'⏸ Pausado'}</div>`;
}

function updateToggleLabel(){
  const on = document.getElementById('sw-disp').checked;
  const t = document.getElementById('toggle-disp');
  t.classList.toggle('on', on); t.classList.toggle('off', !on);
  document.getElementById('toggle-label').textContent = on
    ? '✅ Disponible — los leads nuevos te llegan'
    : '⏸ No disponible — los leads se asignan a otros abogados';
}

async function toggleDisp(){
  const v = document.getElementById('sw-disp').checked;
  await api('/api/pro/me',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({available:v})});
  updateToggleLabel();
}

async function loadStats(){
  const m = await api('/api/pro/metrics');
  // Meta diaria gamificada
  const pct = m.progress_pct;
  const msg = pct >= 100 ? '🏆 ¡Meta alcanzada hoy!'
           : pct >= 50 ? 'Vas a buen ritmo. Sigue.'
           : pct > 0  ? 'Primer cierre hecho. Al próximo.'
           : 'Arranquemos el día.';
  document.getElementById('goal-block').innerHTML = `
    <div class="goal-card">
      <h3>Meta diaria</h3>
      <div class="progress">
        <span class="big">${m.closed_today}</span>
        <span class="of">/ ${m.goal_daily} tutelas cerradas hoy</span>
      </div>
      <div class="bar"><div class="fill" style="width:${pct}%"></div></div>
      <div class="lbl" style="margin-top:8px">${msg}</div>
    </div>`;

  // Mini stats
  const respLabel = m.avg_response_hours == null ? '—'
    : m.avg_response_hours < 2 ? m.avg_response_hours + ' h'
    : m.avg_response_hours + ' h';
  const respKlass = m.avg_response_hours == null ? '' :
                    m.avg_response_hours <= 2 ? 'ok' :
                    m.avg_response_hours <= 6 ? 'warn' : '';
  const closeKlass = m.close_rate >= 25 ? 'ok' : m.close_rate >= 15 ? 'warn' : '';
  document.getElementById('mini-stats').innerHTML = `
    <div class="mini-stat"><div class="k">${m.verified}</div><div class="v">Leads por contactar</div></div>
    <div class="mini-stat"><div class="k">${m.upcoming_appointments}</div><div class="v">Citas próximas</div></div>
    <div class="mini-stat ${closeKlass}"><div class="k">${m.close_rate}%</div><div class="v">Tasa de cierre</div></div>
    <div class="mini-stat ${respKlass}"><div class="k">${respLabel}</div><div class="v">Tiempo respuesta promedio</div></div>`;

  // Embudo personal 7d
  const f = m.funnel_7d || {};
  const etapas = [
    ['verified','Verificados'],
    ['contacted','Contactados'],
    ['closed','Cerrados'],
  ];
  const max = Math.max(1, ...etapas.map(([k])=>f[k]||0));
  const rows = etapas.map(([k,lbl])=>{
    const v = f[k]||0; const w = max ? (v/max*100) : 0;
    return `<div class="funnel-row2"><div class="label2">${lbl}</div>
      <div class="bar2"><div class="fill2" style="width:${w}%">${v>0?v:''}</div></div></div>`;
  }).join('');
  document.getElementById('funnel-personal').innerHTML =
    `<h4>📊 Mi embudo · últimos 7 días</h4>${rows}`;
}

async function loadLeads(){
  const status = document.getElementById('filter-leads').value;
  const data = await api('/api/pro/leads'+(status?'?status='+status:''));
  const tbody = document.querySelector('#t-leads tbody');
  if(!data.length){tbody.innerHTML='<tr><td colspan="7" style="text-align:center;color:#888;padding:30px">Sin leads aún</td></tr>';return;}
  tbody.innerHTML = data.map(l=>`
    <tr>
      <td style="font-size:11px;color:#888">${(l.created_at||'').slice(0,16)}</td>
      <td><b>${l.name||'<i style="color:#aaa">Sin registrar</i>'}</b><br><small>${l.cedula||''}</small></td>
      <td style="font-size:12px">${l.phone?`<a href="https://wa.me/${l.phone}" target="_blank">+${l.phone}</a><br>`:''}${l.email||''}</td>
      <td>${l.area||'—'}</td>
      <td><div class="truncate">${(l.descripcion||'').slice(0,140)}</div></td>
      <td><span class="badge ${l.status}">${l.status}</span></td>
      <td><div class="actions">
        <a class="btn btn-sm green" href="/pro/lead/${l.id}" target="_blank">🧠 Trabajar caso</a>
        <button class="btn btn-sm outline" onclick="verLead(${l.id})">Ver</button>
        ${l.status==='verified'?`<button class="btn btn-sm green" onclick="setStatus(${l.id},'contacted')">Contactado</button>`:''}
        ${(l.status==='contacted'||l.status==='verified')?`<button class="btn btn-sm gold" onclick="setStatus(${l.id},'closed')">Cerrar</button>`:''}
      </div></td>
    </tr>`).join('');
}

async function verLead(id){
  const l = await api('/api/pro/leads/'+id);
  const w = window.open('','_blank','width=900,height=900');
  w.document.write(`<html><head><title>Lead ${l.name||''}</title>
    <style>body{font-family:'Segoe UI',sans-serif;padding:30px;max-width:800px;margin:0 auto;}
    h1{color:#002347}.meta{background:#f4f6f9;padding:14px;border-radius:6px;margin:10px 0;font-size:13px}
    pre{background:#fafbfc;padding:20px;border-left:4px solid #002347;white-space:pre-wrap;font-family:'Georgia',serif;line-height:1.6;font-size:14px;}</style>
    </head><body>
    <h1>${l.name||'Sin nombre'} · ${l.area||'—'}</h1>
    <div class="meta">
      <div><b>CC:</b> ${l.cedula||'—'}</div>
      <div><b>Tel:</b> +${l.phone||'—'} · <a href="https://wa.me/${l.phone}" target="_blank">Abrir WhatsApp</a></div>
      <div><b>Email:</b> ${l.email||'—'}</div>
      <div><b>Estado:</b> ${l.status}</div>
      <div><b>Fecha:</b> ${(l.created_at||'').slice(0,16)}</div>
    </div>
    <h3>Descripción del cliente</h3>
    <p>${l.descripcion||''}</p>
    <h3>Simulación generada</h3>
    <pre>${(l.draft||'sin borrador').replace(/</g,'&lt;')}</pre>
    </body></html>`);
}

async function setStatus(id,s){
  const notes = prompt('Notas (opcional):')||'';
  // El admin path funciona con auth admin; para el lawyer usamos su propio endpoint... aún no existe; reusamos admin via cookie no — mejor implementarlo abajo
  await fetch('/api/admin/leads/'+id,{method:'PATCH',headers:{'Content-Type':'application/json','Authorization':'Basic '+btoa('galeano:'+prompt('Admin pass:'))},body:JSON.stringify({status:s,notes})}).catch(()=>{});
  loadLeads(); loadStats();
}

async function loadAppts(){
  const data = await api('/api/pro/appointments?upcoming=true');
  const cont = document.getElementById('appts-cont');
  if(!data.length){cont.innerHTML = '<div style="text-align:center;color:#888;padding:30px">No tienes citas próximas. Los clientes que descarguen su simulación pueden agendar contigo automáticamente.</div>';return;}
  cont.innerHTML = data.map(a=>{
    const d = new Date(a.scheduled_at);
    const fmt = d.toLocaleString('es-CO',{weekday:'long',day:'numeric',month:'long',hour:'2-digit',minute:'2-digit'});
    return `<div class="meeting-card">
      <h4>📅 ${fmt} · ${a.lead_name||'Cliente'}</h4>
      <div class="meta">📱 <a href="https://wa.me/${a.lead_phone}" target="_blank">+${a.lead_phone}</a> · ${a.lead_email||''}</div>
      <div class="meta"><b>Área:</b> ${a.lead_area||'—'} · <b>Caso:</b> ${(a.lead_descripcion||'').slice(0,200)}…</div>
      <div class="meta">
        ${a.meet_url?`🎥 <a href="${a.meet_url}" target="_blank" class="meet">Abrir Meet manual</a> · `:''}
        <a href="#" onclick="editMeet(${a.id});return false" style="color:#002347;font-size:12px">${a.meet_url?'Editar':'Agregar'} link Meet</a> ·
        <a href="#" onclick="marcarCita(${a.id},'completed');return false" style="color:#16a34a;font-size:12px">Marcar completada</a> ·
        <a href="#" onclick="marcarCita(${a.id},'cancelled_by_lawyer');return false" style="color:#c8102e;font-size:12px">Cancelar</a>
      </div>
    </div>`;
  }).join('');
}

async function editMeet(aid){
  const url = prompt('Pegá el link de Meet/Zoom/Teams (opcional):')||'';
  await api('/api/pro/appointments/'+aid,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({meet_url:url.trim()})});
  loadAppts();
}
async function marcarCita(aid, estado){
  const notes = estado==='cancelled_by_lawyer' ? (prompt('Razón de cancelación (se envía al cliente):')||'') : '';
  if(estado==='cancelled_by_lawyer' && !confirm('¿Cancelar esta cita y notificar al cliente?'))return;
  await api('/api/pro/appointments/'+aid,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:estado,notes})});
  loadAppts(); loadCal();
}

// ── Calendar semanal ───────────────────────────────────────────────────
let calCurStart = null;
async function loadCal(startDate){
  const url = '/api/pro/agenda'+(startDate?'?start='+startDate:'');
  const d = await api(url);
  calCurStart = d.week_start;
  document.getElementById('cal-range').textContent = `Semana ${d.week_start} a ${d.week_end}`;
  const hoy = new Date().toISOString().slice(0,10);
  // Header
  let html = '<div class="cal-grid" style="min-width:760px">';
  html += '<div class="cal-header">Hora</div>';
  d.dias.forEach(dia=>{
    html += `<div class="cal-header${dia.date===hoy?' today':''}">${dia.label}</div>`;
  });
  // Transpose: por cada slot horario, una fila con los 7 días
  const horas = d.dias[0].slots.map(s=>s.hour);
  horas.forEach((h, hi)=>{
    html += `<div class="cal-cell cal-hour">${h}</div>`;
    d.dias.forEach(dia=>{
      const sl = dia.slots[hi];
      let content = '';
      if(sl.state==='booked' && sl.item){
        content = `<span class="mini">${(sl.item.title||'').slice(0,10)}</span>`;
      }else if(sl.state==='blocked' && sl.item){
        content = `<span class="mini">⛔ ${(sl.item.reason||'Bloqueado').slice(0,10)}</span>`;
      }
      html += `<div class="cal-cell cal-slot ${sl.state}" onclick="calClick('${sl.state}','${sl.start}',${sl.item?sl.item.id:'null'},${sl.item?"'"+(sl.item.type||'')+"'":'null'})">${content}</div>`;
    });
  });
  html += '</div>';
  document.getElementById('cal-grid').innerHTML = html;
}
async function calClick(state, startIso, itemId, itemType){
  if(state==='past' || state==='off_hours')return;
  if(state==='free'){
    if(!confirm('¿Bloquear este horario? (30 min)\\nEj: porque estás en otra reunión, almuerzo, etc.'))return;
    const reason = prompt('Motivo (opcional):')||'';
    const endIso = new Date(new Date(startIso).getTime()+30*60000).toISOString();
    try{
      await api('/api/pro/blocks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({start_iso:startIso,end_iso:endIso,reason})});
      loadCal(calCurStart);
    }catch(e){alert(e.message);}
    return;
  }
  if(state==='blocked'){
    if(!confirm('¿Desbloquear este horario?'))return;
    await api('/api/pro/blocks/'+itemId,{method:'DELETE'});
    loadCal(calCurStart); return;
  }
  if(state==='booked'){
    // Ver detalle del lead asociado a esta cita
    const appts = await api('/api/pro/appointments?upcoming=true');
    const a = appts.find(x=>x.id===itemId);
    if(!a)return;
    alert(`Cita: ${a.lead_name}\\nTel: +${a.lead_phone}\\nÁrea: ${a.lead_area}\\n\\nCaso: ${(a.lead_descripcion||'').slice(0,300)}`);
  }
}
function semanaPrev(){
  const d=new Date(calCurStart); d.setDate(d.getDate()-7);
  loadCal(d.toISOString().slice(0,10));
}
function semanaNext(){
  const d=new Date(calCurStart); d.setDate(d.getDate()+7);
  loadCal(d.toISOString().slice(0,10));
}

// ── RAG tools ────────────────────────────────────────────────────────────
function ragTool(modo){
  document.getElementById('rag-result').classList.remove('on');
  document.getElementById('rag-fuentes').classList.remove('on');
  const forms = {
    consultar:`<div class="form-group"><label>Pregunta</label><textarea id="rag-q" rows="3" placeholder="EPS Sanitas niega..."></textarea></div>
      <div class="form-group" style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
        <div><label>Área</label><select id="rag-area"><option value="">Todas</option><option value="salud">Salud</option><option value="pensiones">Pensiones</option><option value="laboral">Laboral</option></select></div>
        <div><label>Sala</label><select id="rag-sala"><option value="">Todas</option><option value="CIVIL">Civil</option><option value="LABORAL">Laboral</option><option value="PENAL">Penal</option><option value="PLENA">Plena</option></select></div>
        <div><label>Año</label><input type="number" id="rag-anio" placeholder="2024"></div>
      </div>
      <button class="btn" onclick="ragRun('consultar')">Consultar</button>`,
    caso:`<div class="form-group"><label>Cliente</label><input id="rag-cliente"></div>
      <div class="form-group"><label>Descripción del caso</label><textarea id="rag-q" rows="4"></textarea></div>
      <div class="form-group"><label>Área</label><select id="rag-area"><option value="">Auto</option><option value="salud">Salud</option><option value="pensiones">Pensiones</option><option value="laboral">Laboral</option></select></div>
      <button class="btn" onclick="ragRun('caso')">Analizar caso</button>`,
    tutela:`<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="form-group"><label>Nombre</label><input id="rag-nombre"></div>
        <div class="form-group"><label>Cédula</label><input id="rag-cedula"></div></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="form-group"><label>Accionado</label><input id="rag-accionado"></div>
        <div class="form-group"><label>Derecho</label><input id="rag-derecho" placeholder="Salud, vida digna"></div></div>
      <div class="form-group"><label>Hechos</label><textarea id="rag-q" rows="5"></textarea></div>
      <div class="form-group"><label>Área</label><select id="rag-area"><option value="salud">Salud</option><option value="pensiones">Pensiones</option><option value="laboral">Laboral</option></select></div>
      <button class="btn gold" onclick="ragRun('tutela')">Generar tutela</button>`,
    linea:`<div class="form-group"><label>Tema</label><input id="rag-q" placeholder="fuero materno despido"></div>
      <div class="form-group"><label>Área</label><select id="rag-area"><option value="">Todas</option><option value="salud">Salud</option><option value="pensiones">Pensiones</option><option value="laboral">Laboral</option></select></div>
      <button class="btn" onclick="ragRun('linea')">Explorar línea</button>`,
  };
  document.getElementById('rag-form').innerHTML = forms[modo];
  document.getElementById('rag-form').dataset.modo = modo;
}

async function ragRun(modo){
  document.getElementById('rag-result').classList.remove('on');
  document.getElementById('rag-fuentes').classList.remove('on');
  document.getElementById('rag-spinner').classList.add('on');
  try{
    let r;
    const q = document.getElementById('rag-q').value.trim();
    const area = document.getElementById('rag-area')?.value || null;
    if(modo==='consultar'){
      r = await api('/api/pro/consultar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pregunta:q,area,sala:document.getElementById('rag-sala').value||null,anio:parseInt(document.getElementById('rag-anio').value)||null})});
    }else if(modo==='caso'){
      r = await api('/api/pro/analizar-caso',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({descripcion:q,nombre_cliente:document.getElementById('rag-cliente').value,area})});
    }else if(modo==='tutela'){
      r = await api('/api/pro/generar-tutela',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nombre:document.getElementById('rag-nombre').value,cedula:document.getElementById('rag-cedula').value,accionado:document.getElementById('rag-accionado').value,derecho_vulnerado:document.getElementById('rag-derecho').value,hechos:q,area})});
    }else if(modo==='linea'){
      r = await api('/api/pro/linea-jurisprudencial?tema='+encodeURIComponent(q)+(area?'&area='+area:''));
    }
    const res = document.getElementById('rag-result'); res.textContent = r.respuesta; res.classList.add('on');
    const fu = document.getElementById('rag-fuentes');
    fu.innerHTML = '<b>Fichas usadas:</b> '+(r.fichas_usadas||[]).map(f=>`<span class="badge-fch">${f.id} · ${f.sala} ${f.anio}</span>`).join(' ');
    fu.classList.add('on');
  }catch(e){
    document.getElementById('rag-result').textContent = '❌ '+e.message;
    document.getElementById('rag-result').classList.add('on');
  }
  document.getElementById('rag-spinner').classList.remove('on');
}

async function cambiarPwd(){
  const p = document.getElementById('new-pwd').value;
  if(p.length < 8){document.getElementById('pwd-msg').innerHTML='<span style="color:#c8102e">Mínimo 8 caracteres</span>';return;}
  await api('/api/pro/me',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});
  document.getElementById('pwd-msg').innerHTML='<span style="color:#16a34a">✅ Contraseña actualizada</span>';
  document.getElementById('new-pwd').value='';
}

loadMe(); loadStats(); loadCal(); loadAppts();
setInterval(loadStats, 60000);
</script>
</body></html>""".replace("NAME_PLACEHOLDER", name)


# =============================================================================
# LAWYER WORKSPACE (por-lead)
# =============================================================================

def lawyer_workspace_html(lawyer: dict, lead: dict) -> str:
    import json as _json
    lead_json = _json.dumps({k: lead.get(k) for k in
        ("id","name","cedula","phone","email","area","descripcion","draft","status","created_at")})
    def esc(s): return (s or "").replace("<","&lt;").replace(">","&gt;")
    phone = lead.get("phone") or ""
    area = lead.get("area") or ""
    fichas = lead.get("fichas") or []
    fichas_html = " ".join(f'<span class="badge-fch">{esc(f.get("id",""))} · {esc(f.get("sala","") or "")} {esc(str(f.get("anio","")))}</span>' for f in fichas)
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Caso · """ + esc(lead.get("name") or "Lead") + """ · Galeano Herrera</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}
  body{background:#f4f6f9;color:#1a2332;}
  header{background:#002347;color:#fff;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #C5A059;}
  header h1{font-size:17px;}
  header a{color:#C5A059;text-decoration:none;font-size:13px;margin-left:14px;}
  .container{max-width:1400px;margin:0 auto;padding:20px;}

  .case-head{background:#fff;padding:20px 24px;border-radius:10px;box-shadow:0 1px 6px rgba(0,35,71,.08);margin-bottom:18px;}
  .case-head .title{color:#002347;font-size:22px;font-weight:800;margin-bottom:6px;}
  .case-head .meta{font-size:13px;color:#6b7280;margin-bottom:12px;}
  .case-head .badges{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;}
  .case-head .badges span{font-size:11px;font-weight:700;padding:4px 10px;border-radius:12px;background:#e3f0ff;color:#004a9f;}
  .case-head .badges .status{background:#dcfce7;color:#166534;}
  .quick-actions{display:flex;gap:10px;flex-wrap:wrap;}
  .btn{background:#002347;color:#fff;padding:9px 16px;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;text-decoration:none;display:inline-block;}
  .btn:hover{background:#003f7a;}
  .btn.green{background:#16a34a;}.btn.green:hover{background:#15803d;}
  .btn.gold{background:#C5A059;}.btn.gold:hover{background:#b08a47;}
  .btn.outline{background:transparent;color:#002347;border:1px solid #002347;}
  .btn.danger{background:#c8102e;}
  .btn-sm{padding:6px 12px;font-size:12px;}

  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;}
  @media(max-width:980px){.grid{grid-template-columns:1fr;}}

  .col{display:flex;flex-direction:column;gap:14px;}
  .card{background:#fff;padding:18px;border-radius:10px;box-shadow:0 1px 6px rgba(0,35,71,.08);}
  .card h3{color:#002347;font-size:15px;margin-bottom:12px;font-weight:700;display:flex;align-items:center;gap:8px;}
  .card h3 .tag{font-size:10px;background:#C5A059;color:#fff;padding:2px 7px;border-radius:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;}
  .card .sub{font-size:12px;color:#6b7280;margin-bottom:10px;}

  label{font-size:11px;font-weight:700;color:#002347;text-transform:uppercase;display:block;margin-bottom:4px;letter-spacing:.5px;}
  input,select,textarea{width:100%;padding:9px 11px;border:1px solid #dce3ef;border-radius:6px;font-size:13px;font-family:inherit;}
  input:focus,select:focus,textarea:focus{outline:none;border-color:#002347;}
  textarea{resize:vertical;min-height:90px;}
  .row2{display:grid;grid-template-columns:1fr 1fr;gap:10px;}

  .cliente-desc{background:#f6f8fb;padding:12px;border-left:3px solid #C5A059;border-radius:0 6px 6px 0;font-size:13px;line-height:1.6;white-space:pre-wrap;max-height:200px;overflow-y:auto;}
  .badge-fch{display:inline-block;background:#e3f0ff;color:#004a9f;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;margin:2px;}

  .tool-btn{background:#fff;border:1px solid #dce3ef;border-radius:8px;padding:12px;cursor:pointer;text-align:left;transition:all .15s;width:100%;margin-bottom:8px;display:flex;align-items:center;gap:10px;}
  .tool-btn:hover{border-color:#C5A059;transform:translateX(2px);}
  .tool-btn .ic{font-size:22px;}
  .tool-btn .t{font-weight:700;color:#002347;font-size:13px;}
  .tool-btn .d{font-size:11px;color:#6b7280;margin-top:2px;}

  .result-box{background:#fafbfc;border:1px solid #e5e7eb;border-radius:8px;padding:14px;max-height:600px;overflow-y:auto;font-family:'Georgia',serif;font-size:13px;line-height:1.7;white-space:pre-wrap;display:none;}
  .result-box.on{display:block;}
  .result-actions{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;}

  .spinner{display:none;text-align:center;padding:14px;color:#002347;font-size:13px;}
  .spinner.on{display:block;}
  .spinner .dot{display:inline-block;width:8px;height:8px;background:#C5A059;border-radius:50%;margin:0 3px;animation:bounce 1.2s infinite;}
  .spinner .dot:nth-child(2){animation-delay:.2s;}.spinner .dot:nth-child(3){animation-delay:.4s;}
  @keyframes bounce{0%,80%,100%{transform:scale(.6);opacity:.4;}40%{transform:scale(1);opacity:1;}}

  .toast{position:fixed;bottom:20px;right:20px;background:#16a34a;color:#fff;padding:12px 18px;border-radius:8px;font-size:13px;box-shadow:0 4px 12px rgba(0,0,0,.15);z-index:100;display:none;}
  .toast.on{display:block;animation:slideIn .3s;}
  @keyframes slideIn{from{transform:translateX(100%);}to{transform:none;}}
</style></head><body>

<header>
  <h1>⚖ Caso · """ + esc(lead.get("name") or "Sin registrar") + """</h1>
  <div><a href="/pro">← Dashboard</a><a href="/pro/logout">Salir</a></div>
</header>

<div class="container">

  <!-- Case head -->
  <div class="case-head">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:14px;flex-wrap:wrap">
      <div style="flex:1;min-width:260px">
        <div class="title" id="hd-name">""" + esc(lead.get("name") or "Cliente sin registrar") + """</div>
        <div class="meta" id="hd-meta">
          CC <span id="hd-cedula">""" + esc(lead.get("cedula") or "—") + """</span>
          · Tel <a href="https://wa.me/""" + esc(phone) + """" id="hd-wa" target="_blank">+<span id="hd-phone">""" + esc(phone) + """</span></a>
          · <span id="hd-email">""" + esc(lead.get("email") or "—") + """</span>
          · Creado """ + esc((lead.get("created_at") or "")[:16]) + """
        </div>
        <div class="badges">
          <span class="status">""" + esc(lead.get("status") or "") + """</span>
          <span id="hd-area">""" + esc(area or "sin área") + """</span>
        </div>
      </div>
      <button class="btn outline btn-sm" onclick="toggleEditClient()" id="btn-edit-client">✏️ Editar datos</button>
    </div>
    <div class="quick-actions" style="margin-top:12px">
      <a class="btn green" href="https://wa.me/""" + esc(phone) + """" target="_blank" id="qa-wa">💬 WhatsApp</a>
      <button class="btn gold" onclick="setStatus('contacted')">Marcar contactado</button>
      <button class="btn" onclick="setStatus('closed')">Cerrar caso</button>
      <a class="btn outline" href="/api/lead/download/""" + esc(lead.get("token","")) + """.docx" target="_blank">📥 Descargar borrador actual</a>
    </div>
  </div>

  <!-- Editor de datos del cliente (oculto por default) -->
  <div class="card" id="edit-client-box" style="display:none;border-top:3px solid #C5A059">
    <h3>✏️ Editar datos del cliente <span class="tag">Requiere confirmación</span></h3>
    <div class="sub">Los cambios se guardan contra la base de datos. Se envían al endpoint autenticado de abogado.</div>
    <div class="row2">
      <div><label>Nombre completo</label><input id="e-name" value=""" + '"' + esc(lead.get("name") or "") + '"' + """></div>
      <div><label>Cédula</label><input id="e-cedula" value=""" + '"' + esc(lead.get("cedula") or "") + '"' + """></div>
    </div>
    <div class="row2" style="margin-top:8px">
      <div><label>Teléfono (3XXXXXXXXX)</label><input id="e-phone" value=""" + '"' + esc(phone) + '"' + """></div>
      <div><label>Email</label><input id="e-email" type="email" value=""" + '"' + esc(lead.get("email") or "") + '"' + """></div>
    </div>
    <div style="margin-top:8px">
      <label>Área legal</label>
      <select id="e-area">
        <option value="">— sin clasificar —</option>
        <option value="salud">Salud</option>
        <option value="pensiones">Pensiones</option>
        <option value="laboral">Laboral</option>
        <option value="accidentes">Accidentes</option>
        <option value="insolvencia">Insolvencia</option>
        <option value="derechos_fundamentales">Derechos fundamentales</option>
      </select>
    </div>
    <div style="margin-top:8px">
      <label>Descripción del caso (afecta al RAG)</label>
      <textarea id="e-desc" rows="5">""" + esc(lead.get("descripcion") or "") + """</textarea>
    </div>
    <div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap">
      <button class="btn green" onclick="saveClient()">💾 Guardar cambios</button>
      <button class="btn outline" onclick="toggleEditClient()">Cancelar</button>
    </div>
  </div>

  <!-- 2 columnas: Izquierda = caso cliente · Derecha = asistente IA -->
  <div class="grid">
    <div class="col">

      <div class="card">
        <h3>📝 Caso del cliente <span class="tag">Original</span></h3>
        <div class="sub">Lo que el cliente escribió en la landing:</div>
        <div class="cliente-desc">""" + esc(lead.get("descripcion") or "") + """</div>
        <div style="margin-top:10px;font-size:11px;color:#6b7280">📚 Fichas base: """ + fichas_html + """</div>
      </div>

      <div class="card">
        <h3>✍️ Complementa el caso <span class="tag">Opcional</span></h3>
        <div class="sub">Datos que tú tienes y el cliente no puso. Se usan en las herramientas IA de la derecha.</div>
        <div class="row2">
          <div><label>Accionado (exacto)</label><input id="c-accionado" placeholder="EPS Sanitas S.A.S. NIT…"></div>
          <div><label>Derecho vulnerado</label><input id="c-derecho" placeholder="Salud y vida digna"></div>
        </div>
        <div style="margin-top:8px"><label>Hechos ampliados (si tienes más info del cliente por WhatsApp)</label>
          <textarea id="c-hechos" placeholder="Ej: Cliente confirmó por WhatsApp que tiene concepto médico del 15 de abril. Historia clínica adjunta. PQR radicada el 20 de marzo sin respuesta."></textarea>
        </div>
      </div>

      <div class="card">
        <h3>📄 Borrador final <span class="tag">Para radicar</span></h3>
        <div class="sub">Pega aquí el resultado que trabajes con las herramientas y guarda. Esta versión reemplaza la simulación original y queda disponible para descargar.</div>
        <textarea id="draft-final" style="min-height:260px;font-family:'Georgia',serif;font-size:13px" placeholder="El borrador final irá aquí…">""" + esc(lead.get("draft") or "") + """</textarea>
        <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
          <button class="btn green" onclick="guardarBorrador()">💾 Guardar borrador final</button>
          <a class="btn outline" href="/api/lead/download/""" + esc(lead.get("token","")) + """.docx" target="_blank">📥 Descargar DOCX</a>
        </div>
      </div>
    </div>

    <div class="col">
      <div class="card">
        <h3>🧠 Asistente IA <span class="tag">RAG · 625 fichas CSJ</span></h3>
        <div class="sub">Todas las herramientas usan los datos del cliente + lo que complementes a la izquierda.</div>

        <button class="tool-btn" onclick="runTool('caso')">
          <span class="ic">📋</span>
          <div><div class="t">Análisis completo del caso</div><div class="d">Protocolo Galeano: diagnóstico + estrategia + probabilidad de éxito</div></div>
        </button>
        <button class="tool-btn" onclick="runTool('tutela')">
          <span class="ic">⚖</span>
          <div><div class="t">Generar tutela FINAL (completa)</div><div class="d">Versión lista para radicar. Sin tope de palabras. Cita radicados.</div></div>
        </button>
        <button class="tool-btn" onclick="runTool('linea')">
          <span class="ic">📈</span>
          <div><div class="t">Línea jurisprudencial del área</div><div class="d">Tesis dominante + evolución + cuándo NO concede la Corte</div></div>
        </button>
        <button class="tool-btn" onclick="runTool('consultar')">
          <span class="ic">🔍</span>
          <div><div class="t">Consulta libre (tu pregunta)</div><div class="d">Para dudas específicas que no caen en las 3 anteriores</div></div>
        </button>

        <div id="query-ad-hoc" style="display:none;margin-top:10px">
          <label>Tu pregunta</label>
          <textarea id="q-libre" rows="2" placeholder="Ej: ¿Procede agente oficioso para este caso?"></textarea>
          <button class="btn btn-sm" style="margin-top:8px" onclick="runConsulta()">Consultar</button>
        </div>

        <div class="spinner" id="ia-spinner"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Consultando jurisprudencia…</div>
        <div class="result-box" id="ia-result"></div>
        <div class="result-actions" id="ia-actions" style="display:none">
          <button class="btn btn-sm green" onclick="copiarABorrador()">📥 Usar este texto como borrador final</button>
          <button class="btn btn-sm outline" onclick="copiarPortapapeles()">📋 Copiar al portapapeles</button>
        </div>
      </div>
    </div>
  </div>

</div>

<div class="toast" id="toast">✓ Guardado</div>

<script>
const LEAD = """ + lead_json + """;
let lastResult = "";

// Preseleccionar el área actual en el select
(function(){
  const sel = document.getElementById('e-area');
  if(sel && LEAD.area){
    for(const o of sel.options){ if(o.value === LEAD.area){ o.selected = true; break; } }
  }
})();

function toggleEditClient(){
  const box = document.getElementById('edit-client-box');
  const btn = document.getElementById('btn-edit-client');
  const open = box.style.display !== 'none' && box.style.display !== '';
  box.style.display = open ? 'none' : 'block';
  btn.textContent = open ? '✏️ Editar datos' : '× Cerrar editor';
  if(!open) box.scrollIntoView({behavior:'smooth', block:'start'});
}

async function saveClient(){
  const body = {
    name:        document.getElementById('e-name').value.trim(),
    cedula:      document.getElementById('e-cedula').value.trim(),
    phone:       document.getElementById('e-phone').value.trim(),
    email:       document.getElementById('e-email').value.trim(),
    area:        document.getElementById('e-area').value || null,
    descripcion: document.getElementById('e-desc').value.trim(),
  };
  // Resumen de cambios para el confirm
  const cambios = [];
  if(body.name        !== (LEAD.name||''))        cambios.push('• Nombre: "'+ (LEAD.name||'(vacío)') + '" → "' + body.name + '"');
  if(body.cedula      !== (LEAD.cedula||''))      cambios.push('• Cédula: "'+ (LEAD.cedula||'(vacío)') + '" → "' + body.cedula + '"');
  if(body.phone       !== (LEAD.phone||''))       cambios.push('• Teléfono: "'+ (LEAD.phone||'(vacío)') + '" → "' + body.phone + '"');
  if(body.email       !== (LEAD.email||''))       cambios.push('• Email: "'+ (LEAD.email||'(vacío)') + '" → "' + body.email + '"');
  if(body.area        !== (LEAD.area||null))      cambios.push('• Área: "'+ (LEAD.area||'(vacío)') + '" → "' + (body.area||'(vacío)') + '"');
  if(body.descripcion !== (LEAD.descripcion||'')) cambios.push('• Descripción del caso (modificada)');
  if(cambios.length === 0){ alert('No hay cambios que guardar.'); return; }
  if(!confirm('¿Confirmas actualizar los datos del cliente?\\n\\n' + cambios.join('\\n'))) return;
  try{
    await api('/api/pro/leads/'+LEAD.id,{method:'PATCH',
      headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    toast('✓ Datos actualizados');
    // Actualizar LEAD en memoria y la vista
    Object.assign(LEAD, body);
    document.getElementById('hd-name').textContent = body.name || 'Cliente sin registrar';
    document.getElementById('hd-cedula').textContent = body.cedula || '—';
    document.getElementById('hd-phone').textContent = body.phone || '—';
    document.getElementById('hd-email').textContent = body.email || '—';
    document.getElementById('hd-area').textContent  = body.area  || 'sin área';
    const waUrl = 'https://wa.me/'+(body.phone||'');
    document.getElementById('hd-wa').href = waUrl;
    document.getElementById('qa-wa').href = waUrl;
    // Actualizar también la caja de "Caso del cliente" (descripción)
    const descBox = document.querySelector('.cliente-desc');
    if(descBox) descBox.textContent = body.descripcion;
    toggleEditClient();
  }catch(e){ alert('Error: ' + e.message); }
}

function toast(msg){
  const t=document.getElementById('toast');t.textContent=msg;t.classList.add('on');
  setTimeout(()=>t.classList.remove('on'),2400);
}
async function api(url,opts){
  const r=await fetch(url,opts);
  const d=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(d.detail||'Error '+r.status);
  return d;
}

async function setStatus(s){
  const notes = prompt('Notas (opcional):')||'';
  // usa admin endpoint requiere basic auth → mejor endpoint público del pro (si no existe, pedimos admin)
  const user = prompt('Admin usuario (galeano):','galeano');
  const pass = prompt('Admin password:');
  if(!pass)return;
  try{
    await fetch('/api/admin/leads/'+LEAD.id,{method:'PATCH',
      headers:{'Content-Type':'application/json','Authorization':'Basic '+btoa(user+':'+pass)},
      body:JSON.stringify({status:s,notes})});
    toast('✓ Estado: '+s);
    setTimeout(()=>location.reload(),700);
  }catch(e){alert(e.message);}
}

function descripcionEnriquecida(){
  let base = LEAD.descripcion || '';
  const acc = (document.getElementById('c-accionado')||{}).value||'';
  const der = (document.getElementById('c-derecho')||{}).value||'';
  const hec = (document.getElementById('c-hechos')||{}).value||'';
  if(acc) base += `\\nAccionado exacto: ${acc}.`;
  if(der) base += `\\nDerecho fundamental vulnerado: ${der}.`;
  if(hec) base += `\\nInformación complementaria del abogado: ${hec}`;
  return base;
}

async function runTool(modo){
  document.getElementById('ia-result').classList.remove('on');
  document.getElementById('ia-actions').style.display='none';
  document.getElementById('query-ad-hoc').style.display='none';
  if(modo==='consultar'){
    document.getElementById('query-ad-hoc').style.display='block';
    return;
  }
  document.getElementById('ia-spinner').classList.add('on');
  try{
    let r;
    const desc = descripcionEnriquecida();
    if(modo==='caso'){
      r = await api('/api/pro/analizar-caso',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({descripcion:desc, nombre_cliente:LEAD.name||'', area:LEAD.area||null})});
    }else if(modo==='tutela'){
      r = await api('/api/pro/generar-tutela',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          nombre: LEAD.name||'',
          cedula: LEAD.cedula||'',
          accionado: (document.getElementById('c-accionado').value||'[COMPLETAR accionado]'),
          derecho_vulnerado: (document.getElementById('c-derecho').value||'derechos fundamentales'),
          hechos: desc,
          area: LEAD.area||null,
        })});
    }else if(modo==='linea'){
      const tema = prompt('Tema de la línea jurisprudencial:', LEAD.descripcion.slice(0,100));
      if(!tema){document.getElementById('ia-spinner').classList.remove('on');return;}
      r = await api('/api/pro/linea-jurisprudencial?tema='+encodeURIComponent(tema)+(LEAD.area?'&area='+LEAD.area:''));
    }
    mostrarResultado(r);
  }catch(e){
    document.getElementById('ia-result').textContent = '❌ '+e.message;
    document.getElementById('ia-result').classList.add('on');
  }
  document.getElementById('ia-spinner').classList.remove('on');
}

async function runConsulta(){
  const q = document.getElementById('q-libre').value.trim();
  if(!q)return;
  document.getElementById('ia-spinner').classList.add('on');
  try{
    const r = await api('/api/pro/consultar',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({pregunta:q+'. Contexto: '+descripcionEnriquecida(), area:LEAD.area||null})});
    mostrarResultado(r);
  }catch(e){
    document.getElementById('ia-result').textContent = '❌ '+e.message;
    document.getElementById('ia-result').classList.add('on');
  }
  document.getElementById('ia-spinner').classList.remove('on');
}

function mostrarResultado(r){
  lastResult = r.respuesta || '';
  let html = lastResult;
  if(r.fichas_usadas && r.fichas_usadas.length){
    html += '\\n\\n── Fichas usadas ──\\n' + r.fichas_usadas.map(f=>`• ${f.id} · Sala ${f.sala||'?'} ${f.anio||''}`).join('\\n');
  }
  const box = document.getElementById('ia-result');
  box.textContent = html; box.classList.add('on');
  document.getElementById('ia-actions').style.display='flex';
}

function copiarABorrador(){
  if(!lastResult)return;
  const ta = document.getElementById('draft-final');
  ta.value = lastResult;
  ta.focus();
  toast('✓ Copiado al borrador final');
}
function copiarPortapapeles(){
  if(!lastResult)return;
  navigator.clipboard.writeText(lastResult).then(()=>toast('✓ Copiado al portapapeles'));
}
async function guardarBorrador(){
  const draft = document.getElementById('draft-final').value.trim();
  if(draft.length < 50){alert('El borrador debe tener al menos 50 caracteres.');return;}
  try{
    await api('/api/pro/leads/'+LEAD.id+'/draft',{method:'PUT',
      headers:{'Content-Type':'application/json'},body:JSON.stringify({draft})});
    toast('✓ Borrador guardado. El cliente verá esta versión al descargar.');
  }catch(e){alert(e.message);}
}
</script>
</body></html>"""


# =============================================================================
# ADMIN
# =============================================================================

def admin_html() -> str:
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin · Galeano Herrera</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}
  body{background:#f4f6f9;color:#1a2332;}
  header{background:#002347;color:#fff;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #C5A059;}
  header h1{font-size:18px;}
  header a{color:#C5A059;text-decoration:none;font-size:13px;margin-left:14px;}
  .container{max-width:1400px;margin:0 auto;padding:20px;}
  .stats{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px;}
  @media(max-width:780px){.stats{grid-template-columns:repeat(2,1fr);}}
  .stat{background:#fff;padding:16px;border-radius:8px;box-shadow:0 1px 6px rgba(0,35,71,.08);}
  .stat .num{font-size:26px;font-weight:800;color:#002347;}
  .stat .lbl{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-top:4px;}
  .stat .pct{font-size:12px;color:#C5A059;font-weight:700;margin-top:4px;}

  .funnel{background:#fff;padding:18px;border-radius:8px;margin-bottom:20px;box-shadow:0 1px 6px rgba(0,35,71,.08);}
  .funnel h3{color:#002347;margin-bottom:14px;font-size:14px;}
  .funnel-row{display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:13px;}
  .funnel-row .label{width:160px;font-weight:600;color:#002347;font-size:12px;}
  .funnel-row .bar{flex:1;height:24px;background:#f4f6f9;border-radius:4px;position:relative;overflow:hidden;}
  .funnel-row .fill{height:100%;background:linear-gradient(90deg,#002347 0%,#C5A059 100%);}
  .funnel-row .vals{font-size:11px;color:#666;width:140px;text-align:right;}

  .tabs{display:flex;gap:4px;margin-bottom:18px;border-bottom:2px solid #002347;flex-wrap:wrap;}
  .tab{padding:10px 18px;cursor:pointer;border-radius:6px 6px 0 0;border:2px solid transparent;border-bottom:none;font-weight:600;color:#002347;background:#fff;font-size:13px;}
  .tab.on{background:#002347;color:#fff;}
  .panel{display:none;background:#fff;padding:24px;border-radius:0 8px 8px 8px;box-shadow:0 2px 12px rgba(0,35,71,.08);}
  .panel.on{display:block;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th{background:#f4f6f9;padding:10px;text-align:left;font-weight:700;color:#002347;font-size:12px;text-transform:uppercase;border-bottom:2px solid #002347;}
  td{padding:10px;border-bottom:1px solid #eee;vertical-align:top;}
  tr:hover{background:#fafbfc;}
  .badge{display:inline-block;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:700;}
  .badge.preview{background:#f3f4f6;color:#666;}
  .badge.pending_otp{background:#fef3c7;color:#92400e;}
  .badge.verified{background:#dbeafe;color:#1e40af;}
  .badge.contacted{background:#dcfce7;color:#166534;}
  .badge.closed{background:#e5e7eb;color:#374151;}
  .btn{background:#002347;color:#fff;padding:6px 14px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;}
  .btn.green{background:#16a34a;}.btn.gold{background:#C5A059;}
  .btn.outline{background:transparent;color:#002347;border:1px solid #002347;}
  .btn-sm{padding:4px 10px;font-size:11px;}
  input,select,textarea{padding:8px 10px;border:1px solid #dce3ef;border-radius:5px;font-size:13px;font-family:inherit;width:100%;}
  .form-row{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;align-items:end;margin-bottom:14px;}
  @media(max-width:980px){.form-row{grid-template-columns:1fr 1fr;}}
  label{font-size:11px;font-weight:700;color:#002347;text-transform:uppercase;display:block;margin-bottom:4px;}
  .actions{display:flex;gap:6px;flex-wrap:wrap;}
  .truncate{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;max-width:280px;}
  .pwd-cell{font-family:monospace;font-size:11px;background:#fef3c7;padding:2px 6px;border-radius:3px;cursor:pointer;}
</style></head>
<body>

<header>
  <h1>⚙ Panel Admin · Galeano Herrera</h1>
  <div>
    <a href="/pro">App Pro</a>
    <a href="/" target="_blank">Ver landing</a>
  </div>
</header>

<div class="container">

  <div class="stats" id="stats"></div>
  <div class="funnel" id="funnel"></div>

  <div class="tabs">
    <div class="tab on" onclick="tab('leads')">📋 Leads</div>
    <div class="tab" onclick="tab('citas')">📅 Citas</div>
    <div class="tab" onclick="tab('lawyers')">⚖ Abogados</div>
    <div class="tab" onclick="tab('config')">🔧 Sistema</div>
  </div>

  <div class="panel on" id="p-leads">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <h3 style="color:#002347">Leads recientes</h3>
      <select id="filter-status" onchange="loadLeads()" style="width:200px">
        <option value="">Todos</option>
        <option value="preview">Solo preview</option>
        <option value="pending_otp">Esperando OTP</option>
        <option value="verified">Verificados</option>
        <option value="contacted">Contactados</option>
        <option value="closed">Cerrados</option>
      </select>
    </div>
    <div style="overflow-x:auto"><table id="t-leads"><thead><tr>
      <th>Fecha</th><th>Nombre</th><th>Contacto</th><th>Área</th>
      <th>Caso</th><th>Estado</th><th>Acciones</th>
    </tr></thead><tbody></tbody></table></div>
  </div>

  <div class="panel" id="p-citas">
    <h3 style="margin-bottom:14px;color:#002347">Próximas citas (todos los abogados)</h3>
    <div style="overflow-x:auto"><table id="t-appts"><thead><tr>
      <th>Cuándo</th><th>Cliente</th><th>Abogado</th><th>Meet</th><th>Estado</th>
    </tr></thead><tbody></tbody></table></div>
  </div>

  <div class="panel" id="p-lawyers">
    <h3 style="margin-bottom:14px;color:#002347">Abogados que reciben leads</h3>
    <div class="form-row">
      <div><label>Nombre</label><input id="l-name" placeholder="Dr. Galeano"></div>
      <div><label>WhatsApp</label><input id="l-wa" placeholder="573001234567"></div>
      <div><label>Email (login)</label><input id="l-email" type="email" placeholder="abogado@galeano.co"></div>
      <div><label>Password inicial</label><input id="l-pwd" type="text" placeholder="(autogenerado si vacío)"></div>
      <div><label>Áreas (* = todas)</label><input id="l-areas" placeholder="salud,laboral o *"></div>
      <div><button class="btn green" onclick="addLawyer()">+ Agregar</button></div>
    </div>
    <table id="t-lawyers"><thead><tr>
      <th>Nombre</th><th>Email</th><th>WhatsApp</th><th>Áreas</th><th>Default</th><th>Activo</th><th>Disp</th><th></th>
    </tr></thead><tbody></tbody></table>
  </div>

  <div class="panel" id="p-config">
    <h3 style="margin-bottom:14px;color:#002347">Configuración del sistema</h3>
    <div id="cfg-info"></div>
    <p style="margin-top:14px;font-size:13px;color:#555">Variables de entorno (configurar en Render dashboard):</p>
    <ul style="margin:10px 0 0 24px;font-size:13px;color:#555">
      <li><code>GEMINI_API_KEY</code> · <code>ULTRAMSG_INSTANCE_ID</code> · <code>ULTRAMSG_TOKEN</code></li>
      <li><code>GOOGLE_CALENDAR_TOKEN</code> · <code>GOOGLE_CALENDAR_ID</code> · <code>MEET_SUPPRESS_CREATE</code></li>
      <li><code>SECRET_KEY</code> (firma sesiones) · <code>ADMIN_USER</code> · <code>ADMIN_PASS</code></li>
      <li><code>CRON_TOKEN</code> (recordatorios) · <code>DEV_MODE=1</code> (debug)</li>
    </ul>
  </div>
</div>

<script>
function tab(name){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
  document.querySelector(`[onclick="tab('${name}')"]`).classList.add('on');
  document.getElementById('p-'+name).classList.add('on');
  if(name==='lawyers')loadLawyers();
  if(name==='citas')loadAppts();
  if(name==='config')loadConfig();
}
async function api(url,opts){
  const r=await fetch(url,opts);
  const d=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(d.detail||'Error');
  return d;
}

async function loadStats(){
  const s = await api('/api/admin/stats');
  document.getElementById('stats').innerHTML=`
    <div class="stat"><div class="num">${s.total}</div><div class="lbl">Leads totales</div></div>
    <div class="stat"><div class="num">${s.last_24h}</div><div class="lbl">Últimas 24h</div></div>
    <div class="stat"><div class="num">${s.verified}</div><div class="lbl">Verificados</div><div class="pct">${s.conversion_otp}% conv</div></div>
    <div class="stat"><div class="num">${s.contacted}</div><div class="lbl">Contactados</div><div class="pct">${s.conversion_contact}% conv</div></div>
    <div class="stat"><div class="num">${s.closed}</div><div class="lbl">Cerrados</div></div>`;
  // Funnel
  const fn = s.funnel_7d || {};
  const order = ['page_view','preview_started','preview_done','register','otp_verified','downloaded','meeting_booked'];
  const labels = {page_view:'Vistas landing',preview_started:'Inicia simulación',preview_done:'Simulación lista',register:'Registro datos',otp_verified:'OTP verificado',downloaded:'Descarga DOCX',meeting_booked:'Cita agendada'};
  const max = Math.max(1, ...Object.values(fn).map(v=>v?.uniq||0));
  document.getElementById('funnel').innerHTML = `<h3>📊 Embudo últimos 7 días (visitantes únicos)</h3>` +
    order.map(k=>{
      const v = fn[k] || {total:0,uniq:0};
      const pct = (v.uniq||0)/max*100;
      return `<div class="funnel-row"><div class="label">${labels[k]||k}</div><div class="bar"><div class="fill" style="width:${pct}%"></div></div><div class="vals">${v.uniq||0} únicos · ${v.total||0} total</div></div>`;
    }).join('');
}
async function loadLeads(){
  const status=document.getElementById('filter-status').value;
  const data=await api('/api/admin/leads'+(status?'?status='+status:''));
  const tbody=document.querySelector('#t-leads tbody');
  if(!data.length){tbody.innerHTML='<tr><td colspan="7" style="text-align:center;color:#888;padding:30px">Sin leads aún</td></tr>';return;}
  tbody.innerHTML=data.map(l=>`
    <tr>
      <td style="font-size:11px;color:#888">${(l.created_at||'').slice(0,16)}</td>
      <td><b>${l.name||'<i style="color:#aaa">Sin registrar</i>'}</b><br><small>${l.cedula||''}</small></td>
      <td style="font-size:12px">${l.phone?`<a href="https://wa.me/${l.phone}" target="_blank">+${l.phone}</a><br>`:''}${l.email||''}</td>
      <td>${l.area||'—'}</td>
      <td><div class="truncate">${(l.descripcion||'').slice(0,140)}</div></td>
      <td><span class="badge ${l.status}">${l.status}</span></td>
      <td><div class="actions">
        <a class="btn btn-sm green" href="/pro/lead/${l.id}" target="_blank">🧠 Workspace</a>
        <button class="btn btn-sm outline" onclick="verLead(${l.id})">Borrador</button>
        ${l.status==='verified'?`<button class="btn btn-sm green" onclick="setStatus(${l.id},'contacted')">Contactado</button>`:''}
        ${(l.status==='contacted'||l.status==='verified')?`<button class="btn btn-sm gold" onclick="setStatus(${l.id},'closed')">Cerrar</button>`:''}
      </div></td>
    </tr>`).join('');
}
async function setStatus(id,s){
  const notes=prompt('Notas (opcional):')||'';
  await api('/api/admin/leads/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:s,notes})});
  loadLeads(); loadStats();
}
async function verLead(id){
  const l=await api('/api/admin/leads/'+id);
  const w=window.open('','_blank','width=900,height=900');
  w.document.write(`<pre style="font-family:Georgia,serif;white-space:pre-wrap;padding:30px;line-height:1.6">${(l.draft||'sin borrador').replace(/</g,'&lt;')}</pre>`);
}
async function loadAppts(){
  const data = await api('/api/admin/appointments?upcoming=true');
  const tb = document.querySelector('#t-appts tbody');
  if(!data.length){tb.innerHTML='<tr><td colspan="5" style="text-align:center;color:#888;padding:30px">Sin citas próximas</td></tr>';return;}
  tb.innerHTML = data.map(a=>{
    const dt = new Date(a.scheduled_at).toLocaleString('es-CO',{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'});
    return `<tr>
      <td><b>${dt}</b></td>
      <td>${a.lead_name||''}<br><small>+${a.lead_phone||''}</small></td>
      <td>${a.lawyer_name||'—'}</td>
      <td>${a.meet_url?`<a href="${a.meet_url}" target="_blank">Meet</a>`:'—'}</td>
      <td><span class="badge ${a.status}">${a.status}</span></td>
    </tr>`;
  }).join('');
}
async function loadLawyers(){
  const data=await api('/api/admin/lawyers');
  document.querySelector('#t-lawyers tbody').innerHTML=data.map(l=>`
    <tr>
      <td><b>${l.name}</b></td>
      <td>${l.email||'<i style="color:#aaa">sin login</i>'}</td>
      <td><a href="https://wa.me/${l.whatsapp}" target="_blank">+${l.whatsapp}</a></td>
      <td>${(l.areas||[]).join(', ')||'—'}</td>
      <td>${l.is_default?'⭐':''}</td>
      <td>${l.active?'✓':'—'}</td>
      <td><button class="btn btn-sm outline" onclick="toggleAvail(${l.id},${l.available?0:1})">${l.available?'On':'Off'}</button></td>
      <td>
        <button class="btn btn-sm outline" onclick="resetPwd(${l.id})">Reset pass</button>
        <button class="btn btn-sm" style="background:#c8102e" onclick="delLawyer(${l.id})">×</button>
      </td>
    </tr>`).join('') || '<tr><td colspan="8" style="text-align:center;color:#888;padding:20px">Sin abogados</td></tr>';
}
async function addLawyer(){
  const data={
    name: document.getElementById('l-name').value.trim(),
    whatsapp: document.getElementById('l-wa').value.trim(),
    email: document.getElementById('l-email').value.trim() || null,
    password: document.getElementById('l-pwd').value.trim() || null,
    areas: document.getElementById('l-areas').value.split(',').map(s=>s.trim()).filter(Boolean),
    is_default: false,
  };
  if(!data.name||!data.whatsapp){alert('Nombre y WhatsApp son obligatorios');return;}
  if(!data.password && data.email){
    data.password = Math.random().toString(36).slice(-10);
    alert('Password autogenerado para '+data.email+': '+data.password+'\\n\\nGUÁRDALO ahora — no se vuelve a mostrar.');
  }
  await api('/api/admin/lawyers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  ['l-name','l-wa','l-email','l-pwd','l-areas'].forEach(id=>document.getElementById(id).value='');
  loadLawyers();
}
async function resetPwd(id){
  const p = prompt('Nueva contraseña para este abogado:');
  if(!p)return;
  await api('/api/admin/lawyers/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:p})});
  alert('Password actualizado.');
}
async function toggleAvail(id, val){
  await api('/api/admin/lawyers/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({available:!!val})});
  loadLawyers();
}
async function delLawyer(id){
  if(!confirm('¿Eliminar este abogado?'))return;
  await api('/api/admin/lawyers/'+id,{method:'DELETE'});
  loadLawyers();
}
async function loadConfig(){
  const c=await api('/api/admin/config');
  document.getElementById('cfg-info').innerHTML=`
    <div style="background:#f4f6f9;padding:14px;border-radius:6px;font-size:13px;line-height:1.8">
      <div>${c.gemini_api_key?'✅':'❌'} GEMINI_API_KEY</div>
      <div>${c.faiss_listo?'✅':'⏳'} FAISS index (${c.fichas} fichas)</div>
      <div>${c.ultramsg?'✅':'❌'} UltraMsg WhatsApp</div>
      <div>${c.calendar?'✅':'❌'} Google Calendar / Meet</div>
      <div>📞 Abogado default: <b>${c.lawyer_default||'❌ Configura uno'}</b></div>
      <div>${c.dev_mode?'⚠ DEV_MODE activo (OTP visible)':'🔒 DEV_MODE off'}</div>
    </div>`;
}

loadStats(); loadLeads();
setInterval(loadStats, 60000);
</script>
</body></html>"""
