"""HTML para landing pública y panel admin."""

from __future__ import annotations


def landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Galeano Herrera | Abogados — Genera el borrador de tu tutela en segundos basado en jurisprudencia real de la Corte Suprema de Justicia de Colombia.">
<title>Galeano Herrera | Borrador de Tutela en 60 segundos</title>
<style>
  :root{--azul:#002347;--oro:#C5A059;--gris:#f4f6f9;--texto:#1a2332;--rojo:#c8102e;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',-apple-system,sans-serif;background:#fff;color:var(--texto);line-height:1.55;}

  /* HERO */
  .hero{background:linear-gradient(135deg,var(--azul) 0%,#003f7a 100%);color:#fff;padding:48px 16px 64px;text-align:center;border-bottom:4px solid var(--oro);}
  .hero .logo{font-size:24px;font-weight:800;letter-spacing:-1px;margin-bottom:24px;}
  .hero .logo span{color:var(--oro);}
  .hero h1{font-size:38px;font-weight:800;line-height:1.15;max-width:820px;margin:0 auto 16px;letter-spacing:-1px;}
  .hero h1 .resaltar{color:var(--oro);}
  .hero p.lead{font-size:18px;opacity:.92;max-width:640px;margin:0 auto 28px;}
  .badges{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:14px;}
  .badge-trust{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);padding:6px 14px;border-radius:30px;font-size:12px;font-weight:600;letter-spacing:.3px;}

  /* CONTAINER */
  .container{max-width:880px;margin:0 auto;padding:32px 16px 48px;}

  /* CARD */
  .card{background:#fff;border-radius:14px;padding:32px;box-shadow:0 4px 24px rgba(0,35,71,.08);margin-bottom:24px;border:1px solid #e8edf5;}
  h2{font-size:22px;color:var(--azul);margin-bottom:8px;font-weight:700;}
  h3{font-size:16px;color:var(--azul);margin:18px 0 12px;font-weight:700;}
  .muted{color:#666;font-size:14px;}

  /* PASOS */
  .pasos{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:32px 0;}
  @media(max-width:680px){.pasos{grid-template-columns:repeat(2,1fr);}}
  .paso{text-align:center;padding:14px 8px;}
  .paso .num{display:inline-flex;width:36px;height:36px;background:var(--oro);color:#fff;border-radius:50%;align-items:center;justify-content:center;font-weight:800;margin-bottom:8px;}
  .paso .t{font-weight:700;font-size:13px;color:var(--azul);margin-bottom:4px;}
  .paso .d{font-size:12px;color:#777;}

  /* FORMS */
  label{display:block;font-size:12px;font-weight:700;color:var(--azul);text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;}
  input[type=text],input[type=email],input[type=tel],textarea,select{
    width:100%;padding:12px 14px;border:2px solid #dce3ef;border-radius:8px;
    font-size:15px;color:var(--texto);font-family:inherit;background:#fafbfc;}
  input:focus,textarea:focus,select:focus{outline:none;border-color:var(--azul);background:#fff;}
  textarea{resize:vertical;min-height:140px;}
  .form-group{margin-bottom:18px;}
  .row{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
  @media(max-width:600px){.row{grid-template-columns:1fr;}}

  /* CHECKBOX */
  .check{display:flex;align-items:flex-start;gap:10px;font-size:13px;color:#444;margin-bottom:10px;cursor:pointer;}
  .check input[type=checkbox]{margin-top:3px;width:16px;height:16px;flex-shrink:0;}
  .check a{color:var(--azul);text-decoration:underline;}

  /* BTN */
  .btn{background:var(--azul);color:#fff;border:none;padding:14px 36px;border-radius:8px;
       font-size:16px;font-weight:700;cursor:pointer;letter-spacing:.3px;width:100%;}
  .btn:hover{background:#003f7a;} .btn:disabled{background:#aab;cursor:wait;}
  .btn.gold{background:var(--oro);} .btn.gold:hover{background:#a88440;}
  .btn.outline{background:transparent;color:var(--azul);border:2px solid var(--azul);}

  /* PREVIEW */
  .preview-wrap{position:relative;background:#fafbfc;border:1px solid #e8edf5;border-radius:10px;padding:24px;font-family:'Georgia',serif;font-size:14px;line-height:1.7;max-height:520px;overflow:hidden;}
  .preview-visible{white-space:pre-wrap;}
  .preview-blur{position:relative;margin-top:12px;}
  .preview-blur .texto{filter:blur(7px);user-select:none;color:#888;white-space:pre-wrap;height:280px;overflow:hidden;}
  .preview-blur .candado{
    position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
    background:linear-gradient(180deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.95) 50%);
    text-align:center;padding:24px;}
  .preview-blur .candado .icon{font-size:40px;margin-bottom:8px;}
  .preview-blur .candado h3{font-size:18px;color:var(--azul);margin-bottom:8px;}
  .preview-blur .candado p{font-size:13px;color:#555;margin-bottom:14px;max-width:380px;}

  .fichas-tag{display:inline-block;background:#e3f0ff;color:#004a9f;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:700;margin:3px;}

  /* ALERTS */
  .alert{padding:12px 16px;border-radius:8px;font-size:14px;margin-bottom:16px;}
  .alert-info{background:#e8f1ff;border-left:4px solid var(--azul);color:var(--azul);}
  .alert-ok{background:#e8f5e9;border-left:4px solid #2e7d32;color:#1b5e20;}
  .alert-err{background:#ffebee;border-left:4px solid #c62828;color:#b71c1c;}

  /* OTP */
  .otp-input{font-size:28px;letter-spacing:14px;text-align:center;padding:14px;font-family:monospace;}

  /* DISCLAIMER FIJO */
  .disclaimer-fijo{background:#fff8e1;border-top:3px solid #ffc107;padding:14px;text-align:center;font-size:12px;color:#7a5200;}
  .disclaimer-fijo b{color:#5a3d00;}

  /* FOOTER */
  footer{background:var(--azul);color:#fff;padding:32px 16px;text-align:center;}
  footer .logo{font-size:18px;font-weight:800;margin-bottom:8px;}
  footer .logo span{color:var(--oro);}
  footer p{font-size:12px;opacity:.7;}
  footer a{color:var(--oro);text-decoration:none;}

  /* SPINNER */
  .spinner{display:none;text-align:center;padding:30px;color:var(--azul);}
  .spinner.on{display:block;}
  .spinner .dot{display:inline-block;width:10px;height:10px;background:var(--oro);border-radius:50%;margin:0 4px;animation:bounce 1.2s infinite;}
  .spinner .dot:nth-child(2){animation-delay:.2s;} .spinner .dot:nth-child(3){animation-delay:.4s;}
  @keyframes bounce{0%,80%,100%{transform:scale(.6);opacity:.4;}40%{transform:scale(1);opacity:1;}}

  .step{display:none;} .step.on{display:block;}
  .nav-step{font-size:12px;color:#888;text-align:center;margin-bottom:14px;letter-spacing:1px;text-transform:uppercase;}

  /* MODAL */
  .modal-bg{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:100;align-items:center;justify-content:center;padding:20px;}
  .modal-bg.on{display:flex;}
  .modal{background:#fff;max-width:600px;max-height:80vh;overflow-y:auto;border-radius:10px;padding:28px;}
  .modal h3{margin-bottom:14px;}
  .modal-close{float:right;cursor:pointer;color:#888;font-size:22px;line-height:1;}
</style>
</head>
<body>

<header class="hero">
  <div class="logo">Galeano <span>Herrera</span> · Abogados</div>
  <h1>Tu borrador de <span class="resaltar">tutela</span> en <span class="resaltar">60 segundos</span></h1>
  <p class="lead">Cuéntanos qué te pasó. Nuestra IA jurídica, entrenada con jurisprudencia real de la Corte Suprema de Justicia, redacta tu acción de tutela apoyada en precedentes verificables.</p>
  <div class="badges">
    <span class="badge-trust">📚 Jurisprudencia CSJ 2018–2025</span>
    <span class="badge-trust">⚖️ Radicados verificables</span>
    <span class="badge-trust">🔒 Datos protegidos · Ley 1581</span>
    <span class="badge-trust">🇨🇴 Hecho en Colombia</span>
  </div>
</header>

<div class="container">

  <!-- PASOS -->
  <div class="pasos">
    <div class="paso"><div class="num">1</div><div class="t">Cuenta tu caso</div><div class="d">En tus propias palabras</div></div>
    <div class="paso"><div class="num">2</div><div class="t">Vista previa</div><div class="d">Ve el inicio del borrador</div></div>
    <div class="paso"><div class="num">3</div><div class="t">Verifícate</div><div class="d">Código por WhatsApp</div></div>
    <div class="paso"><div class="num">4</div><div class="t">Descarga DOCX</div><div class="d">Listo para revisar</div></div>
  </div>

  <!-- STEP 1: DESCRIBIR -->
  <div class="card step on" id="step-1">
    <div class="nav-step">Paso 1 de 4</div>
    <h2>Describe tu caso</h2>
    <p class="muted" style="margin-bottom:20px">Cuanta más información, mejor el borrador. Incluye qué pasó, contra quién y desde cuándo.</p>

    <div class="form-group">
      <label>¿Qué te está pasando? *</label>
      <textarea id="descripcion" placeholder="Ejemplo: La EPS Sanitas me niega desde hace 2 meses la quimioterapia que me prescribió mi oncólogo. Soy paciente con cáncer de mama y no he podido iniciar tratamiento. Ya radiqué reclamación pero no responden..."></textarea>
    </div>
    <div class="form-group">
      <label>Tipo de caso (opcional — la IA lo detecta solo)</label>
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
    <button class="btn" onclick="generarPreview()">⚡ Generar borrador gratis</button>
    <div class="spinner" id="spinner-1"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Analizando tu caso con jurisprudencia de la Corte Suprema…</div>
    <div id="err-1"></div>
  </div>

  <!-- STEP 2: PREVIEW -->
  <div class="card step" id="step-2">
    <div class="nav-step">Paso 2 de 4</div>
    <h2>Vista previa de tu borrador</h2>
    <div class="alert alert-info" id="alert-fichas"></div>

    <div class="preview-wrap">
      <div class="preview-visible" id="preview-visible"></div>
      <div class="preview-blur">
        <div class="texto" id="preview-blur-texto"></div>
        <div class="candado">
          <div class="icon">🔒</div>
          <h3>Desbloquea el borrador completo</h3>
          <p>Para descargar el documento completo en Word necesitamos verificar tu identidad y aceptación de términos. Tarda 30 segundos.</p>
          <button class="btn gold" style="max-width:300px" onclick="irRegistro()">Continuar — es gratis</button>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 3: REGISTRO -->
  <div class="card step" id="step-3">
    <div class="nav-step">Paso 3 de 4</div>
    <h2>Tus datos para verificar</h2>
    <p class="muted" style="margin-bottom:20px">Necesitamos confirmar que eres una persona real para evitar abuso del servicio. Tus datos quedan protegidos por la Ley 1581 de 2012.</p>

    <div class="row">
      <div class="form-group">
        <label>Nombre completo *</label>
        <input type="text" id="r-nombre" placeholder="María García López">
      </div>
      <div class="form-group">
        <label>Cédula *</label>
        <input type="text" id="r-cedula" placeholder="1234567890">
      </div>
    </div>
    <div class="row">
      <div class="form-group">
        <label>Celular Colombia (WhatsApp) *</label>
        <input type="tel" id="r-phone" placeholder="3001234567">
      </div>
      <div class="form-group">
        <label>Correo electrónico *</label>
        <input type="email" id="r-email" placeholder="maria@email.com">
      </div>
    </div>

    <h3 style="margin-top:24px">Autorización legal</h3>
    <label class="check">
      <input type="checkbox" id="c-terms">
      <span>Acepto los <a href="#" onclick="modal('m-terms');return false">Términos y Condiciones</a> del servicio. *</span>
    </label>
    <label class="check">
      <input type="checkbox" id="c-data">
      <span>Autorizo el tratamiento de mis datos personales conforme a la <a href="#" onclick="modal('m-data');return false">Política de Habeas Data</a> (Ley 1581 de 2012). *</span>
    </label>
    <label class="check">
      <input type="checkbox" id="c-mkt">
      <span>Autorizo a Galeano Herrera | Abogados a contactarme con fines comerciales por WhatsApp, llamada o correo, para evaluar mi caso. *</span>
    </label>

    <button class="btn" onclick="enviarRegistro()" style="margin-top:18px">📲 Enviarme código por WhatsApp</button>
    <div class="spinner" id="spinner-3"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Enviando código…</div>
    <div id="err-3"></div>
  </div>

  <!-- STEP 4: OTP + DESCARGA -->
  <div class="card step" id="step-4">
    <div class="nav-step">Paso 4 de 4</div>
    <h2>Ingresa el código que recibiste</h2>
    <p class="muted" id="otp-msg" style="margin-bottom:20px">Te enviamos un código de 6 dígitos por WhatsApp.</p>

    <div class="form-group">
      <label>Código de 6 dígitos</label>
      <input type="text" id="r-otp" class="otp-input" maxlength="6" inputmode="numeric" placeholder="······">
    </div>
    <button class="btn gold" onclick="verificarOtp()">🔓 Verificar y descargar borrador</button>
    <div class="spinner" id="spinner-4"><div class="dot"></div><div class="dot"></div><div class="dot"></div><br><br>Verificando…</div>
    <div id="err-4"></div>
    <p class="muted" style="margin-top:14px;text-align:center">¿No recibiste el código? <a href="#" onclick="reenviarOtp();return false" style="color:var(--azul)">Reenviar</a></p>
  </div>

  <!-- STEP 5: ÉXITO -->
  <div class="card step" id="step-5">
    <div class="alert alert-ok" style="text-align:center;padding:24px">
      <div style="font-size:48px;margin-bottom:8px">✅</div>
      <h2 style="color:#1b5e20">¡Verificado!</h2>
      <p style="margin-top:8px">Tu borrador está listo para descargar.</p>
    </div>
    <button class="btn gold" id="btn-descargar" style="margin-bottom:14px">📥 Descargar borrador (.docx)</button>
    <div class="alert alert-info" style="margin-top:16px">
      <strong>Próximo paso:</strong> uno de nuestros abogados te contactará en las próximas <b>2 horas hábiles</b> por WhatsApp para evaluar tu caso. La consulta inicial es <b>gratis</b>.
    </div>
  </div>

</div>

<!-- DISCLAIMER FIJO -->
<div class="disclaimer-fijo">
  <b>⚠ Aviso:</b> Este servicio genera borradores orientativos basados en IA + jurisprudencia pública.
  No constituye asesoría jurídica. Validá siempre con un abogado titulado antes de presentar tu acción.
</div>

<footer>
  <div class="logo">Galeano <span>Herrera</span></div>
  <p>© 2025 · Galeano Herrera | Abogados · Colombia</p>
  <p style="margin-top:6px"><a href="#" onclick="modal('m-terms');return false">Términos</a> · <a href="#" onclick="modal('m-data');return false">Habeas Data</a> · <a href="/pro">Acceso abogados</a></p>
</footer>

<!-- MODALES -->
<div class="modal-bg" id="m-terms">
  <div class="modal">
    <span class="modal-close" onclick="cerrarModal()">×</span>
    <h3>Términos y Condiciones</h3>
    <div style="font-size:13px;line-height:1.6">
    <p><b>1. Naturaleza del servicio.</b> Galeano Herrera | Abogados pone a disposición una herramienta tecnológica que, mediante inteligencia artificial, genera borradores orientativos de acciones de tutela a partir de la situación descrita por el usuario y de jurisprudencia pública de la Corte Suprema de Justicia de Colombia.</p>
    <p><b>2. No es asesoría jurídica.</b> Los borradores generados <b>no constituyen</b> consejo legal, dictamen, ni opinión profesional. No reemplazan la asesoría de un abogado titulado y no garantizan el éxito de la acción.</p>
    <p><b>3. Validación obligatoria.</b> El usuario se compromete a no presentar el borrador ante autoridad alguna sin la revisión previa de un abogado.</p>
    <p><b>4. Limitación de responsabilidad.</b> Galeano Herrera | Abogados no responde por las consecuencias derivadas del uso del borrador sin asesoría profesional. La firma queda exonerada de responsabilidad por interpretaciones, errores u omisiones del modelo de IA.</p>
    <p><b>5. Uso adecuado.</b> Está prohibido usar el servicio para casos hipotéticos, fines ilícitos, hostigamiento o automatización masiva. Detectamos y bloqueamos abuso.</p>
    <p><b>6. Propiedad intelectual.</b> El sistema, su diseño y su modelo son propiedad de Galeano Herrera | Abogados.</p>
    <p><b>7. Modificaciones.</b> La firma puede modificar estos términos. La versión vigente está siempre en este sitio.</p>
    <p><b>8. Jurisdicción.</b> Estos términos se rigen por la legislación colombiana. Cualquier controversia se ventila ante los jueces competentes de Bogotá D.C.</p>
    </div>
  </div>
</div>

<div class="modal-bg" id="m-data">
  <div class="modal">
    <span class="modal-close" onclick="cerrarModal()">×</span>
    <h3>Política de Tratamiento de Datos Personales · Ley 1581 de 2012</h3>
    <div style="font-size:13px;line-height:1.6">
    <p><b>Responsable:</b> Galeano Herrera | Abogados, con domicilio en Colombia. Correo: contacto@galeanoherrera.co</p>
    <p><b>Datos recolectados:</b> nombre, cédula, celular, correo electrónico, descripción del caso, dirección IP y registro de actividad en la plataforma.</p>
    <p><b>Finalidades:</b></p>
    <ul style="padding-left:20px;margin:8px 0">
      <li>Generar el borrador de tutela solicitado.</li>
      <li>Verificar identidad mediante código OTP por WhatsApp.</li>
      <li>Contactarle para ofrecer servicios legales relacionados con su caso.</li>
      <li>Enviarle información comercial, comunicaciones y novedades de la firma.</li>
      <li>Cumplir obligaciones legales y fines estadísticos.</li>
    </ul>
    <p><b>Derechos del titular:</b> conocer, actualizar, rectificar, suprimir sus datos y revocar la autorización en cualquier momento, escribiendo a <b>contacto@galeanoherrera.co</b>.</p>
    <p><b>Conservación:</b> los datos se conservan por el tiempo necesario para las finalidades descritas, salvo obligación legal en contrario.</p>
    <p><b>Transferencia:</b> no se ceden datos a terceros sin autorización, salvo requerimiento de autoridad competente.</p>
    <p><b>Seguridad:</b> implementamos medidas técnicas y administrativas razonables para proteger sus datos.</p>
    <p>Al aceptar autoriza expresamente el tratamiento de sus datos para los fines aquí descritos. Esta autorización es voluntaria y revocable.</p>
    </div>
  </div>
</div>

<script>
let currentToken = null;
let currentPhone = null;

function show(stepId){
  document.querySelectorAll('.step').forEach(s=>s.classList.remove('on'));
  document.getElementById(stepId).classList.add('on');
  window.scrollTo({top:0,behavior:'smooth'});
}
function spin(id,on){document.getElementById(id).classList.toggle('on',on);}
function err(id,msg){document.getElementById(id).innerHTML=msg?`<div class="alert alert-err">${msg}</div>`:'';}

function modal(id){document.getElementById(id).classList.add('on');}
function cerrarModal(){document.querySelectorAll('.modal-bg').forEach(m=>m.classList.remove('on'));}
document.querySelectorAll('.modal-bg').forEach(m=>m.addEventListener('click',e=>{if(e.target===m)cerrarModal();}));

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
    document.getElementById('preview-blur-texto').textContent = '\\n\\nFundamentos jurídicos detallados con citas a precedentes de la Corte Suprema...\\n\\nPretensiones específicas redactadas para tu caso...\\n\\nMedida provisional solicitada...\\n\\nPruebas a anexar...\\n\\nFórmula final con datos de notificación...';
    const fichasHtml = d.fichas.map(f=>`<span class="fichas-tag">${f.id} · ${f.sala} ${f.anio}</span>`).join(' ');
    document.getElementById('alert-fichas').innerHTML =
      `<b>📚 Tu borrador se basa en ${d.fichas.length} precedentes reales:</b><br>${fichasHtml}` +
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
    document.getElementById('otp-msg').innerHTML = `Código enviado a <b>+${currentPhone}</b>` + (d.otp_debug ? `<br><br><b style="color:#c8102e">DEV: el código es ${d.otp_debug}</b>` : '');
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
    if(!r.ok){throw new Error(d.detail || 'Código incorrecto o vencido');}
    document.getElementById('btn-descargar').onclick = ()=>window.location.href = d.download_url;
    show('step-5');
  }catch(e){err('err-4', e.message);}
  spin('spinner-4', false);
}

async function reenviarOtp(){
  if(!currentToken){return;}
  spin('spinner-4', true);
  try{
    const r = await fetch('/api/lead/resend-otp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:currentToken})});
    const d = await r.json();
    if(!r.ok){throw new Error(d.detail || 'Error');}
    err('err-4','<div class="alert alert-ok">Código reenviado.</div>');
    setTimeout(()=>err('err-4',''),3000);
  }catch(e){err('err-4', e.message);}
  spin('spinner-4', false);
}
</script>
</body>
</html>"""


def admin_html() -> str:
    return """<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8">
<title>Admin · Galeano Herrera</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0;font-family:'Segoe UI',sans-serif;}
  body{background:#f4f6f9;color:#1a2332;}
  header{background:#002347;color:#fff;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #C5A059;}
  header h1{font-size:18px;}
  header a{color:#C5A059;text-decoration:none;font-size:13px;margin-left:14px;}
  .container{max-width:1300px;margin:0 auto;padding:20px;}
  .stats{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px;}
  @media(max-width:780px){.stats{grid-template-columns:repeat(2,1fr);}}
  .stat{background:#fff;padding:18px;border-radius:8px;box-shadow:0 1px 6px rgba(0,35,71,.08);}
  .stat .num{font-size:28px;font-weight:800;color:#002347;}
  .stat .lbl{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-top:4px;}
  .stat .pct{font-size:12px;color:#C5A059;font-weight:700;margin-top:4px;}
  .tabs{display:flex;gap:4px;margin-bottom:20px;border-bottom:2px solid #002347;}
  .tab{padding:10px 18px;cursor:pointer;border:2px solid transparent;border-bottom:none;border-radius:6px 6px 0 0;font-weight:600;color:#002347;background:#fff;font-size:13px;}
  .tab.on{background:#002347;color:#fff;}
  .panel{display:none;background:#fff;padding:24px;border-radius:0 8px 8px 8px;box-shadow:0 2px 12px rgba(0,35,71,.08);}
  .panel.on{display:block;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th{background:#f4f6f9;padding:10px;text-align:left;font-weight:700;color:#002347;font-size:12px;text-transform:uppercase;letter-spacing:.5px;border-bottom:2px solid #002347;}
  td{padding:10px;border-bottom:1px solid #eee;vertical-align:top;}
  tr:hover{background:#fafbfc;}
  .badge{display:inline-block;padding:3px 8px;border-radius:10px;font-size:10px;font-weight:700;}
  .badge.preview{background:#f3f4f6;color:#666;}
  .badge.pending_otp{background:#fef3c7;color:#92400e;}
  .badge.verified{background:#dbeafe;color:#1e40af;}
  .badge.contacted{background:#dcfce7;color:#166534;}
  .badge.closed{background:#e5e7eb;color:#374151;}
  .btn{background:#002347;color:#fff;padding:6px 14px;border:none;border-radius:5px;cursor:pointer;font-size:12px;font-weight:600;}
  .btn.green{background:#16a34a;} .btn.gold{background:#C5A059;}
  .btn.outline{background:transparent;color:#002347;border:1px solid #002347;}
  .btn-sm{padding:4px 10px;font-size:11px;}
  input,select,textarea{padding:8px 10px;border:1px solid #dce3ef;border-radius:5px;font-size:13px;font-family:inherit;width:100%;}
  .form-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr auto;gap:10px;align-items:end;margin-bottom:14px;}
  label{font-size:11px;font-weight:700;color:#002347;text-transform:uppercase;display:block;margin-bottom:4px;}
  .actions{display:flex;gap:6px;flex-wrap:wrap;}
  .desc-cell{max-width:260px;font-size:12px;color:#555;}
  .truncate{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
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

  <div class="tabs">
    <div class="tab on" onclick="tab('leads')">📋 Leads</div>
    <div class="tab" onclick="tab('lawyers')">⚖ Abogados</div>
    <div class="tab" onclick="tab('config')">🔧 Configuración</div>
  </div>

  <!-- LEADS -->
  <div class="panel on" id="p-leads">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <h3>Leads recientes</h3>
      <select id="filter-status" onchange="loadLeads()" style="width:200px">
        <option value="">Todos los estados</option>
        <option value="preview">Solo preview (sin registro)</option>
        <option value="pending_otp">Esperando OTP</option>
        <option value="verified">Verificados (sin contactar)</option>
        <option value="contacted">Contactados</option>
        <option value="closed">Cerrados</option>
      </select>
    </div>
    <div style="overflow-x:auto"><table id="t-leads"><thead><tr>
      <th>Fecha</th><th>Nombre</th><th>Contacto</th><th>Área</th>
      <th>Caso</th><th>Estado</th><th>Acciones</th>
    </tr></thead><tbody></tbody></table></div>
  </div>

  <!-- LAWYERS -->
  <div class="panel" id="p-lawyers">
    <h3 style="margin-bottom:14px">Abogados que reciben leads</h3>
    <div class="form-row">
      <div><label>Nombre</label><input id="l-name" placeholder="Dr. Galeano"></div>
      <div><label>WhatsApp (573...)</label><input id="l-wa" placeholder="573001234567"></div>
      <div><label>Áreas (separadas por coma, * = todas)</label><input id="l-areas" placeholder="salud,laboral o *"></div>
      <div><label>Por defecto</label><select id="l-default"><option value="0">No</option><option value="1">Sí</option></select></div>
      <div><button class="btn green" onclick="addLawyer()">+ Agregar</button></div>
    </div>
    <table id="t-lawyers"><thead><tr>
      <th>Nombre</th><th>WhatsApp</th><th>Áreas</th><th>Default</th><th>Activo</th><th></th>
    </tr></thead><tbody></tbody></table>
  </div>

  <!-- CONFIG -->
  <div class="panel" id="p-config">
    <h3 style="margin-bottom:14px">Configuración del sistema</h3>
    <div id="cfg-info"></div>
    <p style="margin-top:14px;font-size:13px;color:#555">Las variables de entorno se configuran en el dashboard de Render. Variables actuales:</p>
    <ul style="margin:10px 0 0 24px;font-size:13px;color:#555">
      <li><code>GEMINI_API_KEY</code> — clave de Gemini API</li>
      <li><code>ULTRAMSG_INSTANCE_ID</code> + <code>ULTRAMSG_TOKEN</code> — credenciales WhatsApp</li>
      <li><code>LAWYER_WHATSAPP</code> — número del abogado por defecto (se crea al primer arranque si no hay abogados)</li>
      <li><code>ADMIN_USER</code> + <code>ADMIN_PASS</code> — credenciales de este panel</li>
      <li><code>DEV_MODE=1</code> — devuelve el OTP en la respuesta (solo testing)</li>
    </ul>
  </div>
</div>

<script>
function tab(name){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('on'));
  document.querySelector(`[onclick="tab('${name}')"]`).classList.add('on');
  document.getElementById('p-'+name).classList.add('on');
  if(name==='lawyers')loadLawyers(); if(name==='config')loadConfig();
}
async function api(url,opts){
  const r=await fetch(url,opts);
  const d=await r.json();
  if(!r.ok)throw new Error(d.detail||'Error');
  return d;
}
async function loadStats(){
  const s=await api('/api/admin/stats');
  document.getElementById('stats').innerHTML=`
    <div class="stat"><div class="num">${s.total}</div><div class="lbl">Total leads</div></div>
    <div class="stat"><div class="num">${s.last_24h}</div><div class="lbl">Últimas 24h</div></div>
    <div class="stat"><div class="num">${s.verified}</div><div class="lbl">Verificados</div><div class="pct">${s.conversion_otp}% conv. OTP</div></div>
    <div class="stat"><div class="num">${s.contacted}</div><div class="lbl">Contactados</div><div class="pct">${s.conversion_contact}% conv. contacto</div></div>
    <div class="stat"><div class="num">${s.closed}</div><div class="lbl">Cerrados</div></div>`;
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
      <td><span class="badge preview">${l.area||'—'}</span></td>
      <td class="desc-cell"><div class="truncate">${(l.descripcion||'').slice(0,140)}</div></td>
      <td><span class="badge ${l.status}">${l.status}</span></td>
      <td><div class="actions">
        ${l.draft?`<button class="btn btn-sm outline" onclick="verDraft(${l.id})">Ver borrador</button>`:''}
        ${l.status==='verified'?`<button class="btn btn-sm green" onclick="setStatus(${l.id},'contacted')">Marcar contactado</button>`:''}
        ${(l.status==='contacted'||l.status==='verified')?`<button class="btn btn-sm gold" onclick="setStatus(${l.id},'closed')">Cerrar</button>`:''}
      </div></td>
    </tr>`).join('');
}
async function setStatus(id,s){
  const notes=prompt('Notas (opcional):')||'';
  await api('/api/admin/leads/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:s,notes:notes})});
  loadLeads(); loadStats();
}
async function verDraft(id){
  const d=await api('/api/admin/leads/'+id);
  const w=window.open('','_blank','width=800,height=900');
  w.document.write('<pre style="font-family:Georgia,serif;white-space:pre-wrap;padding:30px;line-height:1.6">'+(d.draft||'sin borrador')+'</pre>');
}
async function loadLawyers(){
  const data=await api('/api/admin/lawyers');
  document.querySelector('#t-lawyers tbody').innerHTML=data.map(l=>`
    <tr>
      <td><b>${l.name}</b></td>
      <td><a href="https://wa.me/${l.whatsapp}" target="_blank">+${l.whatsapp}</a></td>
      <td>${(l.areas||[]).join(', ')||'—'}</td>
      <td>${l.is_default?'⭐':''}</td>
      <td>${l.active?'✓':'—'}</td>
      <td><button class="btn btn-sm outline" onclick="delLawyer(${l.id})">Eliminar</button></td>
    </tr>`).join('') || '<tr><td colspan="6" style="text-align:center;color:#888;padding:20px">Sin abogados — agrega uno arriba</td></tr>';
}
async function addLawyer(){
  const data={
    name: document.getElementById('l-name').value.trim(),
    whatsapp: document.getElementById('l-wa').value.trim(),
    areas: document.getElementById('l-areas').value.split(',').map(s=>s.trim()).filter(Boolean),
    is_default: document.getElementById('l-default').value==='1',
  };
  if(!data.name||!data.whatsapp){alert('Nombre y WhatsApp son obligatorios');return;}
  await api('/api/admin/lawyers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  document.getElementById('l-name').value=''; document.getElementById('l-wa').value=''; document.getElementById('l-areas').value='';
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
    <div style="background:#f4f6f9;padding:14px;border-radius:6px;font-size:13px">
      <div>✅ GEMINI_API_KEY: <b>${c.gemini_api_key?'configurado':'❌ FALTA'}</b></div>
      <div>✅ FAISS: <b>${c.faiss_listo?'listo ('+c.fichas+' fichas)':'no indexado'}</b></div>
      <div>✅ UltraMsg: <b>${c.ultramsg?'configurado':'❌ FALTA'}</b></div>
      <div>✅ Abogado default: <b>${c.lawyer_default||'❌ Configura uno arriba'}</b></div>
      <div>${c.dev_mode?'⚠ DEV_MODE activo (OTP visible en respuestas)':'🔒 DEV_MODE off'}</div>
    </div>`;
}

loadStats(); loadLeads();
setInterval(loadStats, 60000);
</script>
</body></html>"""
