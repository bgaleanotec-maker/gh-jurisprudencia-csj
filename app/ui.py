"""HTML — Landing pública v2, panel admin, login abogado, dashboard abogado."""

from __future__ import annotations


# =============================================================================
# LANDING PÚBLICA
# =============================================================================

def landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Galeano Herrera | Abogados — Simulación de tutela basada en jurisprudencia real de la Corte Suprema. Te conectamos con un abogado en menos de 2 horas.">
<meta property="og:title" content="Tu tutela respaldada en jurisprudencia real">
<meta property="og:description" content="Genera una simulación de tu acción de tutela con jurisprudencia real de la CSJ y agenda cita gratuita con un abogado.">
<title>Galeano Herrera · Tu tutela respaldada en jurisprudencia real</title>
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

  /* TOPBAR */
  .topbar{background:var(--azul);color:#fff;padding:8px 16px;font-size:12px;text-align:center;
          border-bottom:1px solid rgba(255,255,255,.1);}
  .topbar a{color:var(--oro-soft);text-decoration:underline;font-weight:600;}

  /* HEADER */
  header{padding:20px 16px;background:#fff;border-bottom:1px solid var(--gris-soft);
         display:flex;justify-content:space-between;align-items:center;max-width:1200px;margin:0 auto;}
  .logo{font-size:22px;font-weight:800;letter-spacing:-.5px;color:var(--azul);}
  .logo span{color:var(--oro);}
  .nav-links a{color:var(--azul);text-decoration:none;font-size:13px;margin-left:18px;font-weight:600;}

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

  /* BTN */
  .btn{background:var(--azul);color:#fff;border:none;padding:14px 36px;border-radius:8px;
       font-size:16px;font-weight:700;cursor:pointer;letter-spacing:.3px;width:100%;transition:transform .1s,box-shadow .15s;}
  .btn:hover{background:var(--azul-2);transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,35,71,.2);}
  .btn:disabled{background:#aab;cursor:wait;transform:none;box-shadow:none;}
  .btn.gold{background:var(--oro);box-shadow:0 4px 14px rgba(197,160,89,.3);}
  .btn.gold:hover{background:#b08a47;}
  .btn.green{background:var(--verde);}
  .btn.green:hover{background:#15803d;}
  .btn.outline{background:transparent;color:var(--azul);border:2px solid var(--azul);}

  /* PREVIEW */
  .preview-wrap{position:relative;background:#fafbfc;border:1px solid var(--gris-soft);border-radius:10px;padding:24px;font-family:'Georgia',serif;font-size:14px;line-height:1.7;max-height:560px;overflow:hidden;}
  .preview-visible{white-space:pre-wrap;}
  .preview-blur{position:relative;margin-top:12px;}
  .preview-blur .texto{filter:blur(7px);user-select:none;color:#888;white-space:pre-wrap;height:300px;overflow:hidden;}
  .preview-blur .candado{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(180deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.97) 50%);text-align:center;padding:24px;}
  .preview-blur .candado .icon{font-size:42px;margin-bottom:8px;}
  .preview-blur .candado h3{font-size:18px;color:var(--azul);margin-bottom:8px;}
  .preview-blur .candado p{font-size:13px;color:#555;margin-bottom:14px;max-width:400px;}

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

  /* CTA STICKY MOBILE */
  .cta-sticky{display:none;position:fixed;bottom:0;left:0;right:0;background:#fff;padding:12px 16px;border-top:2px solid var(--oro);box-shadow:0 -4px 20px rgba(0,0,0,.08);z-index:50;}
  @media(max-width:780px){.cta-sticky.show{display:flex;gap:10px;align-items:center;justify-content:center;}}
</style>
</head>
<body>

<div class="topbar">
  ⚖️ Plataforma legal con jurisprudencia real ·
  <a href="/pro/login">Acceso abogados</a>
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
  <h1>Tu tutela <span class="resaltar">respaldada en jurisprudencia real</span> de la Corte Suprema</h1>
  <p class="lead">Cuéntanos tu caso. Analizamos contra sentencias reales de la Sala Civil, Laboral, Penal y Plena de la CSJ y generamos una simulación de tu acción de tutela para que la valides con un abogado.</p>
  <div class="badges">
    <span class="badge-trust">📚 Sentencias CSJ 2018–2025</span>
    <span class="badge-trust">⚖️ Radicados verificables en relatoría.cortesuprema.gov.co</span>
    <span class="badge-trust">🔒 Ley 1581 · Habeas Data</span>
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

<div class="container">
  <div class="pasos">
    <div class="paso"><div class="num">1</div><div class="t">Cuenta tu caso</div><div class="d">Una sola pantalla</div></div>
    <div class="paso"><div class="num">2</div><div class="t">Lee la simulación</div><div class="d">Con radicados CSJ</div></div>
    <div class="paso"><div class="num">3</div><div class="t">Verifícate</div><div class="d">Código WhatsApp</div></div>
    <div class="paso"><div class="num">4</div><div class="t">Agenda llamada</div><div class="d">Con un abogado</div></div>
  </div>

  <!-- STEP 1: DESCRIBIR -->
  <div class="card step on" id="step-1">
    <div class="nav-step">Paso 1 de 5</div>
    <h2>📝 ¿Qué te está pasando?</h2>
    <p class="muted" style="margin-bottom:20px">Cuéntanos en tus palabras: qué pasó, contra quién, desde cuándo. Cuanta más información, mejor la simulación.</p>

    <div class="form-group">
      <label>Describe tu caso *</label>
      <textarea id="descripcion" placeholder="Ejemplo: La EPS Sanitas me niega desde hace 2 meses la quimioterapia que prescribió mi oncólogo. Soy paciente con cáncer de mama y no he podido iniciar tratamiento. Ya radiqué reclamación pero no responden..."></textarea>
    </div>
    <div class="form-group">
      <label>Tipo de caso (la IA lo detecta solo)</label>
      <select id="area">
        <option value="">Detección automática</option>
        <option value="salud">Salud / EPS</option>
        <option value="pensiones">Pensiones / Colpensiones</option>
        <option value="laboral">Laboral / Despido</option>
        <option value="accidentes">Accidente de tránsito / SOAT</option>
        <option value="insolvencia">Insolvencia / Embargo</option>
        <option value="derechos_fundamentales">Otros derechos fundamentales</option>
      </select>
    </div>
    <button class="btn" onclick="generarPreview()">Generar simulación gratis</button>
    <div class="spinner" id="spinner-1"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Analizando contra jurisprudencia de la Corte Suprema…</div>
    <div id="err-1"></div>
  </div>

  <!-- STEP 2: PREVIEW -->
  <div class="card step" id="step-2">
    <div class="nav-step">Paso 2 de 5</div>
    <h2>📄 Tu simulación de tutela</h2>
    <p class="muted" style="margin-bottom:14px"><b>Aviso:</b> Esta simulación se basa en líneas jurisprudenciales reales de la Corte Suprema. Está pensada para que un abogado la revise y la presente — no es una asesoría jurídica autónoma.</p>
    <div class="alert alert-info" id="alert-fichas"></div>

    <div class="preview-wrap">
      <div class="preview-visible" id="preview-visible"></div>
      <div class="preview-blur">
        <div class="texto" id="preview-blur-texto"></div>
        <div class="candado">
          <div class="icon">🔓</div>
          <h3>Desbloquea la simulación completa</h3>
          <p>Para descargarla en Word y agendar una llamada con un abogado, completa tu registro.</p>
          <button class="btn" style="max-width:300px" onclick="irRegistro()">Continuar</button>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 3: REGISTRO -->
  <div class="card step" id="step-3">
    <div class="nav-step">Paso 3 de 5</div>
    <h2>🪪 Verifica tu identidad</h2>
    <p class="muted" style="margin-bottom:20px">Necesitamos confirmar que eres una persona real para evitar abuso. Tus datos están protegidos por la <b>Ley 1581 de 2012</b>.</p>

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

    <h3 style="margin-top:24px">Autorizaciones (Ley 1581)</h3>
    <label class="check">
      <input type="checkbox" id="c-terms">
      <span>Acepto los <a href="#" onclick="modal('m-terms');return false">Términos y Condiciones</a> del servicio. *</span>
    </label>
    <label class="check">
      <input type="checkbox" id="c-data">
      <span>Autorizo el tratamiento de mis datos personales según la <a href="#" onclick="modal('m-data');return false">Política de Habeas Data</a>. *</span>
    </label>
    <label class="check">
      <input type="checkbox" id="c-mkt">
      <span>Autorizo a Galeano Herrera | Abogados a contactarme con fines comerciales por WhatsApp, llamada o correo. *</span>
    </label>

    <button class="btn" onclick="enviarRegistro()" style="margin-top:18px">📲 Enviarme código por WhatsApp</button>
    <div class="spinner" id="spinner-3"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Enviando código…</div>
    <div id="err-3"></div>
  </div>

  <!-- STEP 4: OTP -->
  <div class="card step" id="step-4">
    <div class="nav-step">Paso 4 de 5</div>
    <h2>🔐 Ingresa el código</h2>
    <p class="muted" id="otp-msg" style="margin-bottom:20px">Te enviamos un código de 6 dígitos por WhatsApp.</p>

    <div class="form-group">
      <label>Código de 6 dígitos</label>
      <input type="text" id="r-otp" class="otp-input" maxlength="6" inputmode="numeric" autocomplete="one-time-code" placeholder="······">
    </div>
    <button class="btn gold" onclick="verificarOtp()">🔓 Verificar y desbloquear</button>
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

    <button class="btn gold" id="btn-descargar" style="margin-bottom:14px">📥 Descargar simulación (.docx)</button>

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
    <div class="body">Generar la simulación, descargar el documento Word y la consulta inicial de 30 minutos por WhatsApp con un abogado son gratis. Si luego decides que te representemos en el proceso, conversamos los honorarios según la complejidad del caso.</div></details>

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
}

// CTA sticky en mobile cuando scrollee
window.addEventListener('scroll',()=>{
  document.getElementById('cta-sticky').classList.toggle('show', window.scrollY > 600);
});

async function generarPreview(){
  const desc = document.getElementById('descripcion').value.trim();
  if(desc.length < 30){err('err-1','Cuéntanos más detalle (mínimo 30 caracteres). ¿Qué pasó, contra quién y desde cuándo?');return;}
  err('err-1','');
  spin('spinner-1', true);
  try{
    const r = await fetch('/api/lead/preview',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({descripcion:desc, area:document.getElementById('area').value || null})});
    const d = await r.json();
    if(!r.ok){throw new Error(d.detail || 'Error generando');}
    currentToken = d.token;
    document.getElementById('preview-visible').textContent = d.preview.visible;
    document.getElementById('preview-blur-texto').textContent = '\\n\\nFundamentos jurídicos detallados con citas a precedentes específicos de la Corte Suprema...\\n\\nPretensiones precisas adaptadas a tu caso particular...\\n\\nMedida provisional para garantizar tu derecho mientras se decide la tutela...\\n\\nLista de pruebas que debes anexar (historias clínicas, comunicaciones, etc.)...\\n\\nFórmula final con datos de notificación, juramento y anexos...';
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
  const data = {
    token: currentToken,
    name:   document.getElementById('r-nombre').value.trim(),
    cedula: document.getElementById('r-cedula').value.trim(),
    phone:  document.getElementById('r-phone').value.trim(),
    email:  document.getElementById('r-email').value.trim(),
    consent_terms:     document.getElementById('c-terms').checked,
    consent_data:      document.getElementById('c-data').checked,
    consent_marketing: document.getElementById('c-mkt').checked,
  };
  if(!data.name || !data.cedula || !data.phone || !data.email){err('err-3','Completa todos los campos obligatorios.');return;}
  if(!data.consent_terms || !data.consent_data || !data.consent_marketing){err('err-3','Debes aceptar las 3 autorizaciones para continuar.');return;}
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

  <div class="stats" id="stats"></div>

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
  const leads = await api('/api/pro/leads');
  const appts = await api('/api/pro/appointments?upcoming=true');
  const ver = leads.filter(l=>l.status==='verified').length;
  const cont = leads.filter(l=>l.status==='contacted').length;
  const cls = leads.filter(l=>l.status==='closed').length;
  document.getElementById('stats').innerHTML = `
    <div class="stat"><div class="num">${leads.length}</div><div class="lbl">Mis leads totales</div></div>
    <div class="stat"><div class="num" style="color:#1e40af">${ver}</div><div class="lbl">Por contactar</div></div>
    <div class="stat"><div class="num" style="color:#16a34a">${cont}</div><div class="lbl">Contactados</div></div>
    <div class="stat"><div class="num">${cls}</div><div class="lbl">Cerrados</div></div>
    <div class="stat"><div class="num" style="color:#C5A059">${appts.length}</div><div class="lbl">Citas próximas</div></div>`;
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
        <button class="btn btn-sm outline" onclick="verLead(${l.id})">Ver</button>
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
