"""
ui_internal.py — Sistema visual v3 aplicado a las pantallas INTERNAS:
  - lawyer_login_html_v3
  - admin_html_v3
  - lawyer_dashboard_html_v3
  - lawyer_workspace_html_v3
  - expediente_aceptar_html_v3

Mismo sistema visual "Lujo institucional cercano" que ui_v2 (landing):
  - Fraunces (display) + Inter (body)
  - Paleta oro/blanco/grises calidos + azul deep institucional
  - Sombras sutiles multinivel + microinteracciones 120-180ms
  - Tipografia jerarquica clara, espaciado generoso

Endpoints preview: /preview/internal/{page} — NO toca producción.
"""

from __future__ import annotations

from typing import Optional


# ───────────────────────────────────────────────────────────────────────────
# CSS base compartido por TODAS las pantallas internas.
# Se inyecta una vez por página (~10 KB) — cache del browser lo amortiza.
# ───────────────────────────────────────────────────────────────────────────

_BASE_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --ac: #C5A059;
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
  --ok-s: #DCFCE7;
  --wa: #25D366;
  --warn: #C8102E;
  --warn-s: #FCE8E6;
  --info: #2563EB;
  --info-s: #DBEAFE;

  --fd: 'Fraunces', Georgia, serif;
  --fb: 'Inter', system-ui, -apple-system, sans-serif;
  --fm: 'JetBrains Mono', ui-monospace, monospace;

  --r1: 8px; --r2: 12px; --r3: 18px; --r4: 24px; --rf: 999px;

  --sh1: 0 1px 2px rgba(0,0,0,.04);
  --sh2: 0 2px 6px rgba(0,0,0,.05), 0 1px 2px rgba(0,0,0,.03);
  --sh3: 0 8px 24px rgba(0,0,0,.06), 0 2px 6px rgba(0,0,0,.04);
  --sh4: 0 16px 48px rgba(15,30,51,.08), 0 4px 10px rgba(0,0,0,.04);
  --shg: 0 6px 24px var(--ac-g);

  --tr: 160ms cubic-bezier(.4,0,.2,1);
  --trf: 100ms cubic-bezier(.4,0,.2,1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font: 14.5px/1.55 var(--fb);
  color: var(--n);
  background: var(--g0);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
a { color: inherit; text-decoration: none; transition: color var(--trf); }
button { font: inherit; cursor: pointer; }
img, svg { display: block; max-width: 100%; }

/* ───── NAV institucional ───── */
.nav {
  position: sticky; top: 0; z-index: 40;
  background: rgba(255,255,255,.94);
  backdrop-filter: saturate(180%) blur(14px);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid var(--g2);
}
.nav-in {
  max-width: 1280px; margin: 0 auto; padding: 0 24px;
  display: flex; align-items: center; justify-content: space-between;
  height: 60px;
}
.brand {
  display: flex; align-items: center; gap: 10px;
  font-family: var(--fd); font-weight: 600; font-size: 16px;
  letter-spacing: -.01em; color: var(--n);
}
.brand-m {
  width: 30px; height: 30px; border-radius: var(--r1);
  background: var(--ad); display: grid; place-items: center;
  color: var(--ac); font-size: 14px; font-weight: 700;
}
.brand small { font-weight: 500; color: var(--g5); font-size: 12px; }
.nav-tabs { display: flex; gap: 6px; }
.nav-tab {
  padding: 8px 14px; border-radius: var(--r1);
  font-size: 13.5px; font-weight: 500; color: var(--g7);
  transition: background var(--trf), color var(--trf);
}
.nav-tab:hover { background: var(--g1); color: var(--n); }
.nav-tab.active { background: var(--ac-s); color: var(--ac-d); font-weight: 600; }
.nav-r { display: flex; align-items: center; gap: 12px; }
.nav-user {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 12px; border-radius: var(--rf);
  background: var(--g1); font-size: 13px; color: var(--g7);
}
.nav-user-av {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--ac); color: var(--w);
  display: grid; place-items: center;
  font-size: 11px; font-weight: 700;
}

/* ───── Botones ───── */
.btn { display: inline-flex; align-items: center; gap: 8px;
       border: none; border-radius: var(--r1); font-weight: 500;
       transition: all var(--tr); cursor: pointer; }
.btn:disabled { opacity: .55; cursor: not-allowed; }
.btn-pri { background: var(--ac); color: var(--n); padding: 10px 20px; font-size: 14px; font-weight: 600; box-shadow: var(--sh1); }
.btn-pri:hover:not(:disabled) { background: var(--ac-d); transform: translateY(-1px); box-shadow: var(--shg); }
.btn-sec { background: var(--w); color: var(--n); border: 1px solid var(--g2); padding: 9px 18px; font-size: 14px; }
.btn-sec:hover { border-color: var(--n); background: var(--g0); }
.btn-dark { background: var(--n); color: var(--w); padding: 10px 20px; font-size: 14px; }
.btn-dark:hover { background: var(--g9); transform: translateY(-1px); }
.btn-ghost { background: transparent; color: var(--g7); padding: 8px 14px; font-size: 13px; }
.btn-ghost:hover { background: var(--g1); color: var(--n); }
.btn-wa { background: var(--wa); color: var(--w); padding: 9px 16px; font-size: 13.5px; font-weight: 500; }
.btn-wa:hover { background: #1FB957; }
.btn-warn { background: var(--warn); color: var(--w); padding: 8px 14px; font-size: 13px; }
.btn-warn:hover { background: #A50D24; }
.btn-sm { padding: 6px 12px; font-size: 12.5px; }
.btn-lg { padding: 13px 26px; font-size: 15px; }

/* ───── Cards y paneles ───── */
.card { background: var(--w); border: 1px solid var(--g2); border-radius: var(--r3); padding: 24px; box-shadow: var(--sh1); }
.card-h { font-family: var(--fd); font-weight: 600; font-size: 17px; letter-spacing: -.01em; color: var(--n); margin-bottom: 6px; }
.card-d { font-size: 13px; color: var(--g5); margin-bottom: 18px; }

/* ───── Inputs ───── */
.field { display: block; margin-bottom: 14px; }
.field label { display: block; font-size: 12.5px; font-weight: 600; color: var(--g7); margin-bottom: 5px; }
.field input, .field textarea, .field select {
  width: 100%; padding: 11px 13px;
  border: 1px solid var(--g2); border-radius: var(--r1);
  font: 14.5px var(--fb); color: var(--n); background: var(--w);
  transition: border var(--trf), box-shadow var(--trf);
}
.field input:focus, .field textarea:focus, .field select:focus {
  outline: none; border-color: var(--ac);
  box-shadow: 0 0 0 3px var(--ac-s);
}
.field textarea { resize: vertical; min-height: 90px; line-height: 1.5; }
.field-hint { margin-top: 4px; font-size: 11.5px; color: var(--g5); }

/* ───── Tipografía ───── */
.eb { font-size: 11px; font-weight: 700; text-transform: uppercase;
      letter-spacing: .12em; color: var(--ac); margin-bottom: 8px; }
.h-disp {
  font-family: var(--fd); font-weight: 600;
  font-size: clamp(24px, 3vw, 32px);
  line-height: 1.15; letter-spacing: -.02em; color: var(--n);
}
.h-page {
  font-family: var(--fd); font-weight: 600;
  font-size: 22px; letter-spacing: -.01em; color: var(--n);
  margin-bottom: 4px;
}
.sub-page { font-size: 14px; color: var(--g5); margin-bottom: 24px; }

/* ───── Badges ───── */
.bd { display: inline-flex; align-items: center; padding: 3px 10px;
      border-radius: var(--rf); font-size: 11.5px; font-weight: 600; }
.bd-ok { background: var(--ok-s); color: var(--ok); }
.bd-warn { background: var(--warn-s); color: var(--warn); }
.bd-info { background: var(--info-s); color: var(--info); }
.bd-gris { background: var(--g1); color: var(--g7); }
.bd-oro { background: var(--ac-s); color: var(--ac-d); }

/* ───── Tablas ───── */
.tbl-wrap { background: var(--w); border: 1px solid var(--g2);
            border-radius: var(--r3); overflow: hidden; box-shadow: var(--sh1); }
.tbl { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.tbl thead th {
  background: var(--g0); padding: 13px 16px;
  text-align: left; font-weight: 600; font-size: 11.5px;
  text-transform: uppercase; letter-spacing: .08em; color: var(--g5);
  border-bottom: 1px solid var(--g2);
}
.tbl tbody td {
  padding: 14px 16px; border-bottom: 1px solid var(--g2);
  color: var(--g9); vertical-align: middle;
}
.tbl tbody tr:hover { background: var(--g0); }
.tbl tbody tr:last-child td { border-bottom: none; }
.tbl-empty { padding: 48px 20px; text-align: center; color: var(--g5); font-size: 14px; }

/* ───── Stat cards ───── */
.stat-grid {
  display: grid; gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}
.stat-card {
  background: var(--w); border: 1px solid var(--g2);
  border-radius: var(--r3); padding: 20px;
  transition: transform var(--tr), box-shadow var(--tr);
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--sh3); }
.stat-card .lbl { font-size: 11.5px; font-weight: 600;
  text-transform: uppercase; letter-spacing: .08em; color: var(--g5); margin-bottom: 6px; }
.stat-card .num {
  font-family: var(--fd); font-weight: 600; font-size: 30px;
  letter-spacing: -.02em; color: var(--n); line-height: 1;
}
.stat-card .num .small { font-size: 13px; color: var(--g5); font-weight: 400; }
.stat-card .delta { font-size: 12px; margin-top: 6px; color: var(--g5); }
.stat-card .delta.up { color: var(--ok); }
.stat-card .delta.down { color: var(--warn); }

/* ───── Toast ───── */
.toast {
  position: fixed; bottom: 24px; right: 24px;
  padding: 14px 22px; border-radius: var(--r1);
  color: var(--w); font-weight: 600; font-size: 14px;
  opacity: 0; transform: translateY(20px);
  transition: all var(--tr); z-index: 1000;
  box-shadow: var(--sh4);
}
.toast.show { opacity: 1; transform: translateY(0); }
.toast.ok { background: var(--ok); }
.toast.err { background: var(--warn); }

/* ───── Modal ───── */
.modal-bg {
  position: fixed; inset: 0; background: rgba(15,30,51,.5);
  backdrop-filter: blur(4px); z-index: 200;
  display: none; align-items: center; justify-content: center;
  padding: 20px;
}
.modal-bg.open { display: flex; }
.modal {
  background: var(--w); border-radius: var(--r4);
  max-width: 540px; width: 100%; max-height: 90vh; overflow-y: auto;
  box-shadow: var(--sh4);
  animation: modalIn .25s cubic-bezier(.4,0,.2,1);
}
@keyframes modalIn { from { opacity: 0; transform: translateY(20px) scale(.97); } }
.modal-h {
  padding: 22px 26px; border-bottom: 1px solid var(--g2);
  display: flex; justify-content: space-between; align-items: center;
}
.modal-h h3 { font-family: var(--fd); font-weight: 600; font-size: 18px; color: var(--n); }
.modal-x {
  background: transparent; border: none; font-size: 22px;
  color: var(--g5); cursor: pointer; width: 30px; height: 30px;
  border-radius: 50%; display: grid; place-items: center;
  transition: background var(--trf);
}
.modal-x:hover { background: var(--g1); color: var(--n); }
.modal-body { padding: 26px; }
.modal-foot {
  padding: 18px 26px; border-top: 1px solid var(--g2);
  display: flex; justify-content: flex-end; gap: 10px;
}

/* ───── Helpers ───── */
.spinner { display: inline-block; width: 14px; height: 14px;
  border: 2px solid currentColor; border-top-color: transparent;
  border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.hide { display: none !important; }
.container { max-width: 1280px; margin: 0 auto; padding: 24px; }
.container-narrow { max-width: 760px; margin: 0 auto; padding: 24px; }
</style>
"""


def _head(title: str) -> str:
    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{title} · Galeano Herrera</title>
{_BASE_CSS}
</head>"""


def _nav(role: str = "admin", active: str = "", user_name: str = "Admin") -> str:
    """Nav bar institucional. role: admin|pro|client. active: tab key."""
    initials = "".join([w[0].upper() for w in (user_name or "U").split()[:2]]) or "U"
    if role == "admin":
        tabs = [
            ("dashboard", "/admin", "Inicio"),
            ("leads", "/admin#leads", "Leads"),
            ("lawyers", "/admin#lawyers", "Abogados"),
            ("landings", "/admin#landings", "Landings"),
            ("rag", "/admin#rag", "Jurisprudencia"),
            ("wa", "/admin/wa", "WhatsApp"),
        ]
        right = f"""<div class="nav-user"><span class="nav-user-av">{initials}</span><span>{user_name}</span></div>"""
    elif role == "pro":
        tabs = [
            ("leads", "/pro", "Mis leads"),
            ("schedule", "/pro/schedule", "Mi agenda"),
            ("expedientes", "/pro/expedientes", "Expedientes"),
        ]
        right = f"""<div class="nav-user"><span class="nav-user-av">{initials}</span><span>{user_name}</span></div>
                   <a href="/pro/logout" class="btn-ghost btn">Salir</a>"""
    else:
        tabs = []
        right = ""

    tabs_html = "".join(
        f'<a href="{href}" class="nav-tab{" active" if k == active else ""}">{lbl}</a>'
        for k, href, lbl in tabs
    )
    return f"""<header class="nav">
  <div class="nav-in">
    <a href="/" class="brand">
      <span class="brand-m">G</span>
      <span>Galeano Herrera <small>Abogados</small></span>
    </a>
    <nav class="nav-tabs">{tabs_html}</nav>
    <div class="nav-r">{right}</div>
  </div>
</header>"""


# ═══════════════════════════════════════════════════════════════════════════
# 1) LAWYER LOGIN
# ═══════════════════════════════════════════════════════════════════════════

def lawyer_login_html_v3(error: str = "") -> str:
    err = f'<div class="login-err">{error}</div>' if error else ''
    return f"""{_head("Acceso abogados")}
<body style="background: linear-gradient(180deg, var(--g0) 0%, var(--w) 100%); min-height: 100vh;">

<style>
  body {{ display: flex; align-items: center; justify-content: center; padding: 40px 20px; }}
  .login-wrap {{ width: 100%; max-width: 440px; }}
  .login-top {{ text-align: center; margin-bottom: 32px; }}
  .login-top .brand {{ justify-content: center; font-size: 22px; margin-bottom: 8px; }}
  .login-top .brand-m {{ width: 44px; height: 44px; font-size: 18px; }}
  .login-top p {{ color: var(--g5); font-size: 14px; }}
  .login-card {{
    background: var(--w); padding: 36px;
    border-radius: var(--r4); border: 1px solid var(--g2);
    box-shadow: var(--sh4);
  }}
  .login-card h1 {{ font-family: var(--fd); font-weight: 600; font-size: 24px;
                    letter-spacing: -.01em; color: var(--n); margin-bottom: 6px; }}
  .login-card .sub {{ color: var(--g5); font-size: 14px; margin-bottom: 28px; }}
  .login-err {{
    background: var(--warn-s); color: var(--warn);
    padding: 12px 14px; border-radius: var(--r1);
    font-size: 13.5px; margin-bottom: 18px;
    border-left: 3px solid var(--warn);
  }}
  .login-btn {{
    width: 100%; padding: 14px; margin-top: 6px;
    background: var(--n); color: var(--w); border: none;
    border-radius: var(--r1); font-size: 15px; font-weight: 600;
    cursor: pointer; transition: all var(--tr);
  }}
  .login-btn:hover {{ background: var(--g9); transform: translateY(-1px); box-shadow: var(--sh3); }}
  .login-foot {{ text-align: center; margin-top: 22px; font-size: 13px; color: var(--g5); }}
  .login-foot a {{ color: var(--ac-d); font-weight: 500; }}
  .login-back {{ text-align: center; margin-top: 18px; font-size: 13px; }}
  .login-back a {{ color: var(--g5); }}
  .login-back a:hover {{ color: var(--n); }}
</style>

<div class="login-wrap">
  <div class="login-top">
    <a href="/" class="brand">
      <span class="brand-m">G</span>
      <span>Galeano Herrera <small>Abogados</small></span>
    </a>
    <p>Panel del profesional</p>
  </div>

  <div class="login-card">
    <h1>Hola de nuevo</h1>
    <p class="sub">Entra a tu bandeja con tu correo y contraseña.</p>
    {err}
    <form method="POST" action="/pro/login">
      <div class="field">
        <label for="email">Correo electrónico</label>
        <input id="email" type="email" name="email" required autofocus autocomplete="email"
               placeholder="tu@galeano.com">
      </div>
      <div class="field">
        <label for="password">Contraseña</label>
        <input id="password" type="password" name="password" required autocomplete="current-password">
      </div>
      <button type="submit" class="login-btn">Entrar al panel →</button>
    </form>
    <div class="login-foot">
      ¿Aún no tienes acceso? Pídelo al administrador del despacho.
    </div>
  </div>

  <div class="login-back">
    <a href="/">← Volver al sitio público</a>
  </div>
</div>

<script>
if (location.search.includes('err=1')) {{
  const c = document.querySelector('.login-card');
  const e = document.createElement('div');
  e.className = 'login-err';
  e.textContent = 'Email o contraseña incorrectos. Verifica tus datos.';
  c.insertBefore(e, c.querySelector('form'));
}}
</script>
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════
# 2) EXPEDIENTE — Pantalla de aceptación con OTP (cliente)
# ═══════════════════════════════════════════════════════════════════════════

def expediente_aceptar_html_v3(token: str = "") -> str:
    return f"""{_head("Aceptar acompañamiento")}
<body style="background: linear-gradient(180deg, var(--g0) 0%, var(--w) 100%); min-height: 100vh; padding: 40px 20px;">

<style>
  .exp-wrap {{ max-width: 540px; margin: 0 auto; }}
  .exp-card {{ background: var(--w); border: 1px solid var(--g2);
               border-radius: var(--r4); box-shadow: var(--sh4); overflow: hidden; }}
  .exp-head {{
    background: var(--ad); color: var(--w);
    padding: 36px 32px;
    border-bottom: 3px solid var(--ac);
  }}
  .exp-head .badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 12px; border-radius: var(--rf);
    background: rgba(255,255,255,.1); color: var(--ac);
    font-size: 12px; font-weight: 600;
    text-transform: uppercase; letter-spacing: .08em;
    margin-bottom: 14px;
  }}
  .exp-head h1 {{ font-family: var(--fd); font-weight: 600; font-size: 28px;
                  letter-spacing: -.02em; color: var(--w); margin-bottom: 8px; line-height: 1.2; }}
  .exp-head p {{ color: rgba(255,255,255,.75); font-size: 14.5px; line-height: 1.55; }}

  .exp-body {{ padding: 32px; }}
  .exp-info {{
    background: var(--g0); border: 1px solid var(--g2);
    border-radius: var(--r2); padding: 16px;
    margin-bottom: 24px; font-size: 13.5px; color: var(--g7);
    line-height: 1.55;
  }}
  .exp-info strong {{ color: var(--n); }}

  .otp-label {{ font-size: 13px; font-weight: 600; color: var(--g7);
                margin-bottom: 8px; text-align: center; }}
  .otp-input {{
    width: 100%; text-align: center;
    font-family: var(--fm); font-size: 32px; font-weight: 600;
    letter-spacing: 14px; padding: 18px;
    border: 2px solid var(--g2); border-radius: var(--r2);
    background: var(--w); transition: border var(--trf), box-shadow var(--trf);
  }}
  .otp-input:focus {{ outline: none; border-color: var(--ac);
                      box-shadow: 0 0 0 4px var(--ac-s); }}
  .otp-hint {{ text-align: center; font-size: 12.5px; color: var(--g5); margin-top: 8px; }}

  .exp-btn {{
    width: 100%; padding: 16px; margin-top: 22px;
    background: var(--ok); color: var(--w); border: none;
    border-radius: var(--r2); font-size: 15px; font-weight: 600;
    cursor: pointer; transition: all var(--tr);
  }}
  .exp-btn:hover {{ background: #138842; transform: translateY(-1px); box-shadow: var(--sh3); }}
  .exp-btn:disabled {{ background: var(--g3); cursor: not-allowed; transform: none; box-shadow: none; }}

  .exp-legal {{
    margin-top: 24px; padding-top: 20px;
    border-top: 1px solid var(--g2);
    font-size: 11.5px; color: var(--g5); line-height: 1.5; text-align: center;
  }}
  .exp-legal strong {{ color: var(--g7); }}
</style>

<div class="exp-wrap">
  <div class="exp-card">
    <div class="exp-head">
      <span class="badge">Firma electrónica · Ley 527/99</span>
      <h1>Acepta el acompañamiento profesional</h1>
      <p>Estás a un paso de que un abogado del despacho tome formalmente tu caso. Solo necesitamos confirmar que eres tú.</p>
    </div>
    <div class="exp-body">
      <div class="exp-info">
        Te enviamos un <strong>código de 6 dígitos por WhatsApp</strong> al número que nos diste. Escríbelo aquí abajo para firmar electrónicamente y abrir tu expediente.
      </div>

      <form id="otp-form">
        <input type="hidden" name="token" value="{token}">
        <div class="otp-label">Código de 6 dígitos</div>
        <input class="otp-input" name="otp" maxlength="6" inputmode="numeric"
               autocomplete="one-time-code" pattern="[0-9]{{6}}" required autofocus
               placeholder="······">
        <div class="otp-hint">¿No te llegó? Espera 60 segundos y pide reenvío al abogado.</div>
        <button type="submit" class="exp-btn" id="btn-aceptar">
          Aceptar y firmar electrónicamente
        </button>
      </form>

      <div id="result-out"></div>

      <div class="exp-legal">
        Al ingresar el código aceptas el contrato de prestación de servicios profesionales y autorizas el tratamiento de tus datos según la <strong>Ley 1581/2012</strong> (Habeas Data). La firma electrónica simple tiene fuerza probatoria conforme a los <strong>arts. 7 y 28 de la Ley 527/1999</strong>.
      </div>
    </div>
  </div>
</div>

<script>
const f = document.getElementById('otp-form');
const btn = document.getElementById('btn-aceptar');
const out = document.getElementById('result-out');
f.addEventListener('submit', async (ev) => {{
  ev.preventDefault();
  btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Verificando...';
  const fd = new FormData(f);
  try {{
    const r = await fetch('/expediente/aceptar', {{ method: 'POST', body: fd }});
    if (r.ok) {{
      out.innerHTML = '<div style="margin-top:18px;padding:18px;background:var(--ok-s);color:var(--ok);border-radius:var(--r1);text-align:center;font-weight:600">✓ Expediente abierto. Un abogado te contactará por WhatsApp.</div>';
      btn.textContent = '✓ Aceptado';
      btn.style.background = 'var(--ok)';
    }} else {{
      const e = await r.text();
      out.innerHTML = '<div style="margin-top:18px;padding:14px;background:var(--warn-s);color:var(--warn);border-radius:var(--r1);font-size:13.5px">Código incorrecto o vencido. Pide uno nuevo.</div>';
      btn.disabled = false; btn.textContent = 'Reintentar';
    }}
  }} catch(e) {{
    out.innerHTML = '<div style="margin-top:18px;padding:14px;background:var(--warn-s);color:var(--warn);border-radius:var(--r1);font-size:13.5px">Error de conexión. Reintenta.</div>';
    btn.disabled = false; btn.textContent = 'Reintentar';
  }}
}});

// Solo dígitos
document.querySelector('.otp-input').addEventListener('input', e => {{
  e.target.value = e.target.value.replace(/\\D/g, '').slice(0, 6);
}});
</script>
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════
# 3) ADMIN PANEL
# ═══════════════════════════════════════════════════════════════════════════

def admin_html_v3() -> str:
    return f"""{_head("Panel admin")}
<body>

{_nav("admin", active="dashboard", user_name="Admin")}

<main class="container">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:28px;flex-wrap:wrap;gap:16px">
    <div>
      <div class="eb">Inicio</div>
      <h1 class="h-disp">Panel ejecutivo</h1>
      <p class="sub-page" style="margin-top:6px">Resumen del despacho · datos en tiempo real</p>
    </div>
    <div style="display:flex;gap:10px;align-items:center">
      <a href="/wa/health" target="_blank" class="btn btn-sec">Health WhatsApp</a>
      <a href="/admin/wa" class="btn btn-dark">Configurar María Camila →</a>
    </div>
  </div>

  <!-- KPIs -->
  <section style="margin-bottom:32px">
    <div class="stat-grid" id="stat-grid"></div>
  </section>

  <!-- Funnel + actividad -->
  <section style="display:grid;grid-template-columns:1.4fr 1fr;gap:20px;margin-bottom:32px">
    <div class="card">
      <div class="card-h">Embudo de conversión</div>
      <p class="card-d">Lead → calificado → cita → expediente abierto</p>
      <div id="funnel"></div>
    </div>
    <div class="card">
      <div class="card-h">Actividad reciente</div>
      <p class="card-d">Últimos 7 días</p>
      <div id="activity"></div>
    </div>
  </section>

  <!-- Tabla leads -->
  <section id="leads" style="margin-bottom:32px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
      <div>
        <h2 class="h-page">Leads recientes</h2>
        <p style="font-size:13px;color:var(--g5)">Últimos 25 leads capturados desde las landings</p>
      </div>
      <button class="btn btn-sec btn-sm" onclick="loadLeads()">Recargar</button>
    </div>
    <div class="tbl-wrap">
      <table class="tbl">
        <thead><tr>
          <th>Fecha</th><th>Nombre</th><th>Vertical</th><th>WhatsApp</th><th>Estado</th><th>Origen</th><th></th>
        </tr></thead>
        <tbody id="leads-tbl"><tr><td colspan="7" class="tbl-empty">Cargando...</td></tr></tbody>
      </table>
    </div>
  </section>

  <!-- Abogados + landings + jurisprudencia: links -->
  <section style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:32px">
    <a href="#lawyers" class="card" style="text-decoration:none;transition:all var(--tr)">
      <div class="card-h">Abogados</div>
      <p class="card-d">Crear, editar, ver disponibilidad</p>
      <div style="font-family:var(--fd);font-size:28px;color:var(--n)" id="cnt-lawyers">—</div>
    </a>
    <a href="#landings" class="card" style="text-decoration:none">
      <div class="card-h">Landings</div>
      <p class="card-d">4 verticales activas</p>
      <div style="font-family:var(--fd);font-size:28px;color:var(--n)" id="cnt-landings">—</div>
    </a>
    <a href="#rag" class="card" style="text-decoration:none">
      <div class="card-h">Jurisprudencia RAG</div>
      <p class="card-d">Sentencias indexadas</p>
      <div style="font-family:var(--fd);font-size:28px;color:var(--n)" id="cnt-fichas">—</div>
    </a>
  </section>
</main>

<div class="toast" id="toast"></div>

<script>
function toast(msg, type) {{
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = 'toast show ' + (type || 'ok');
  setTimeout(() => t.classList.remove('show'), 2800);
}}
async function loadStats() {{
  try {{
    const r = await fetch('/api/admin/stats');
    if (!r.ok) return;
    const s = await r.json();
    document.getElementById('stat-grid').innerHTML =
      kpi('Leads totales', s.leads_total || 0, '+' + (s.leads_hoy || 0) + ' hoy') +
      kpi('Calificados', s.leads_calif || 0, ((s.leads_total ? (s.leads_calif*100/s.leads_total).toFixed(0):0)) + '% del total') +
      kpi('Citas agendadas', s.appointments_total || 0, (s.appointments_hoy || 0) + ' hoy') +
      kpi('Expedientes', s.expedientes_total || 0, (s.expedientes_activos || 0) + ' activos');
    document.getElementById('cnt-lawyers').textContent = s.lawyers || 0;
    document.getElementById('cnt-landings').textContent = s.landings || 0;
    document.getElementById('cnt-fichas').textContent = s.fichas || 0;
    renderFunnel(s);
  }} catch(e) {{ console.warn(e); }}
}}
function kpi(lbl, num, delta) {{
  return '<div class="stat-card"><div class="lbl">'+lbl+'</div>' +
         '<div class="num">'+num+'</div>' +
         '<div class="delta">'+delta+'</div></div>';
}}
function renderFunnel(s) {{
  const fases = [
    ['Lead nuevo',     s.leads_total || 0, 'var(--info)'],
    ['Calificado',     s.leads_calif || 0, 'var(--ac)'],
    ['Agendado',       s.appointments_total || 0, 'var(--ok)'],
    ['Expediente',     s.expedientes_total || 0, 'var(--ad)'],
  ];
  const max = Math.max(1, ...fases.map(f => f[1]));
  document.getElementById('funnel').innerHTML = fases.map(f => {{
    const pct = (f[1] * 100 / max).toFixed(0);
    return '<div style="margin-bottom:14px">' +
      '<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px">' +
      '<span style="color:var(--g7);font-weight:500">'+f[0]+'</span>' +
      '<span style="font-weight:600;color:var(--n);font-family:var(--fd)">'+f[1]+'</span></div>' +
      '<div style="height:8px;background:var(--g1);border-radius:var(--rf);overflow:hidden">' +
      '<div style="height:100%;background:'+f[2]+';width:'+pct+'%;transition:width .5s"></div></div></div>';
  }}).join('');
  document.getElementById('activity').innerHTML =
    '<p style="color:var(--g5);font-size:13px;line-height:1.7">' +
    '<strong style="color:var(--n)">'+(s.leads_hoy||0)+'</strong> leads hoy · ' +
    '<strong style="color:var(--n)">'+(s.appointments_hoy||0)+'</strong> citas hoy<br>' +
    '<strong style="color:var(--n)">'+(s.wa_msgs_hoy||0)+'</strong> mensajes WhatsApp procesados<br>' +
    '<strong style="color:var(--n)">'+(s.borradores_hoy||0)+'</strong> borradores generados' +
    '</p>';
}}
async function loadLeads() {{
  try {{
    const r = await fetch('/api/admin/leads?limit=25');
    if (!r.ok) return;
    const j = await r.json();
    const tb = document.getElementById('leads-tbl');
    if (!j.length) {{
      tb.innerHTML = '<tr><td colspan="7" class="tbl-empty">Aún no hay leads. Cuando los Facebook Ads empiecen a correr, aparecerán aquí.</td></tr>';
      return;
    }}
    tb.innerHTML = j.map(l => {{
      const estadoMap = {{ 'new':'bd-info', 'verified':'bd-ok', 'contacted':'bd-oro', 'won':'bd-ok', 'lost':'bd-warn' }};
      const ec = estadoMap[l.status] || 'bd-gris';
      const fecha = (l.created_at||'').slice(5,16).replace('T',' ');
      return '<tr>' +
        '<td style="color:var(--g5);font-family:var(--fm);font-size:12.5px">'+fecha+'</td>' +
        '<td style="font-weight:600">'+(l.name||'-')+'</td>' +
        '<td><span class="bd bd-oro">'+(l.area||'general')+'</span></td>' +
        '<td style="font-family:var(--fm);font-size:13px">+'+(l.phone||'')+'</td>' +
        '<td><span class="bd '+ec+'">'+(l.status||'-')+'</span></td>' +
        '<td style="color:var(--g5);font-size:12.5px">'+(l.utm_source||'-')+'</td>' +
        '<td style="text-align:right"><a href="/admin/leads/'+l.id+'" class="btn btn-ghost btn-sm">Ver →</a></td>' +
        '</tr>';
    }}).join('');
  }} catch(e) {{ console.warn(e); }}
}}
loadStats(); loadLeads();
setInterval(loadStats, 60000);
</script>
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════
# 4) LAWYER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

def lawyer_dashboard_html_v3(lawyer: dict) -> str:
    name = (lawyer or {}).get("name") or "Abogado"
    name_safe = name.replace("'", "&#39;").replace('"', "&quot;")
    return f"""{_head("Mi bandeja")}
<body>

{_nav("pro", active="leads", user_name=name_safe)}

<main class="container">
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:28px;flex-wrap:wrap;gap:16px">
    <div>
      <div class="eb">Bandeja</div>
      <h1 class="h-disp">Hola, {name_safe}</h1>
      <p class="sub-page" style="margin-top:6px">Tus leads asignados y citas próximas</p>
    </div>
    <div style="display:flex;gap:10px">
      <button class="btn btn-sec btn-sm" onclick="loadAll()">Recargar</button>
      <button class="btn btn-pri btn-sm" onclick="openSchedule()">Mi agenda →</button>
    </div>
  </div>

  <!-- KPIs del abogado -->
  <section style="margin-bottom:28px">
    <div class="stat-grid" id="stat-grid"></div>
  </section>

  <!-- Próximas citas -->
  <section class="card" style="margin-bottom:28px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div>
        <div class="card-h">Próximas citas</div>
        <p class="card-d">Tus 5 próximas citas confirmadas</p>
      </div>
    </div>
    <div id="citas-list"></div>
  </section>

  <!-- Tabla de leads -->
  <section>
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:14px;flex-wrap:wrap;gap:12px">
      <div>
        <h2 class="h-page">Mis leads</h2>
        <p style="font-size:13px;color:var(--g5)">Leads asignados a ti, ordenados por más reciente</p>
      </div>
      <div style="display:flex;gap:8px">
        <select class="field" style="margin:0;min-width:160px" id="filter-status" onchange="loadLeads()">
          <option value="">Todos los estados</option>
          <option value="new">Nuevos</option>
          <option value="verified">Verificados</option>
          <option value="contacted">Contactados</option>
          <option value="won">Ganados</option>
          <option value="lost">Perdidos</option>
        </select>
      </div>
    </div>
    <div class="tbl-wrap">
      <table class="tbl">
        <thead><tr>
          <th>Fecha</th><th>Cliente</th><th>Caso</th><th>Vertical</th><th>Estado</th><th></th>
        </tr></thead>
        <tbody id="leads-tbl"><tr><td colspan="6" class="tbl-empty">Cargando...</td></tr></tbody>
      </table>
    </div>
  </section>
</main>

<div class="toast" id="toast"></div>

<script>
const LAWYER = {{ id: {(lawyer or {}).get("id", 0)}, name: '{name_safe}' }};
function toast(m, t) {{
  const el = document.getElementById('toast');
  el.textContent = m; el.className = 'toast show ' + (t || 'ok');
  setTimeout(() => el.classList.remove('show'), 2500);
}}

async function loadStats() {{
  try {{
    const r = await fetch('/api/pro/stats');
    if (!r.ok) return;
    const s = await r.json();
    document.getElementById('stat-grid').innerHTML =
      kpi('Leads activos', s.leads_activos || 0, (s.leads_hoy || 0) + ' nuevos hoy') +
      kpi('Citas semana', s.citas_semana || 0, (s.citas_hoy || 0) + ' hoy') +
      kpi('Tasa cierre', (s.tasa_cierre || 0) + '%', 'últimos 30 días') +
      kpi('Expedientes activos', s.expedientes || 0, 'en proceso');
  }} catch(e) {{}}
}}
function kpi(lbl, num, delta) {{
  return '<div class="stat-card"><div class="lbl">'+lbl+'</div><div class="num">'+num+'</div><div class="delta">'+delta+'</div></div>';
}}

async function loadCitas() {{
  try {{
    const r = await fetch('/api/pro/citas?limit=5');
    const j = r.ok ? await r.json() : [];
    const c = document.getElementById('citas-list');
    if (!j.length) {{
      c.innerHTML = '<p style="color:var(--g5);font-size:13.5px;padding:20px;text-align:center">Sin citas próximas.</p>';
      return;
    }}
    c.innerHTML = j.map(a => {{
      const dt = new Date(a.scheduled_at);
      const fecha = dt.toLocaleString('es-CO', {{day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit'}});
      return '<div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--g2)">' +
        '<div><div style="font-weight:600;font-size:14px">'+(a.client_name||'Cliente')+'</div>' +
        '<div style="font-size:12.5px;color:var(--g5);margin-top:2px">'+fecha+' · '+(a.duration_min||20)+' min · '+(a.area||'general')+'</div></div>' +
        '<a class="btn btn-ghost btn-sm" href="/pro/lead/'+a.lead_id+'">Abrir →</a></div>';
    }}).join('');
  }} catch(e) {{}}
}}

async function loadLeads() {{
  const status = document.getElementById('filter-status').value;
  const qs = status ? '?status='+status : '';
  try {{
    const r = await fetch('/api/pro/leads'+qs);
    const j = r.ok ? await r.json() : [];
    const tb = document.getElementById('leads-tbl');
    if (!j.length) {{
      tb.innerHTML = '<tr><td colspan="6" class="tbl-empty">Sin leads en este filtro.</td></tr>';
      return;
    }}
    const ec = {{'new':'bd-info','verified':'bd-ok','contacted':'bd-oro','won':'bd-ok','lost':'bd-warn'}};
    tb.innerHTML = j.map(l => {{
      const desc = (l.descripcion || '').slice(0, 90) + ((l.descripcion||'').length > 90 ? '...' : '');
      const fecha = (l.created_at || '').slice(5,16).replace('T',' ');
      return '<tr style="cursor:pointer" onclick="location.href=\\'/pro/lead/'+l.id+'\\'">' +
        '<td style="color:var(--g5);font-family:var(--fm);font-size:12.5px">'+fecha+'</td>' +
        '<td><div style="font-weight:600">'+(l.name||'-')+'</div><div style="font-size:11.5px;color:var(--g5);font-family:var(--fm)">+'+(l.phone||'')+'</div></td>' +
        '<td style="font-size:13px;color:var(--g7);max-width:280px">'+desc+'</td>' +
        '<td><span class="bd bd-oro">'+(l.area||'gen')+'</span></td>' +
        '<td><span class="bd '+(ec[l.status]||'bd-gris')+'">'+(l.status||'-')+'</span></td>' +
        '<td style="text-align:right"><a class="btn btn-ghost btn-sm" href="/pro/lead/'+l.id+'" onclick="event.stopPropagation()">Abrir →</a></td>' +
        '</tr>';
    }}).join('');
  }} catch(e) {{}}
}}

function loadAll() {{ loadStats(); loadCitas(); loadLeads(); }}
function openSchedule() {{ location.href = '/pro/schedule'; }}

loadAll();
setInterval(loadStats, 60000);
</script>
</body></html>"""


# ═══════════════════════════════════════════════════════════════════════════
# 5) LAWYER WORKSPACE — lead individual
# ═══════════════════════════════════════════════════════════════════════════

def lawyer_workspace_html_v3(lawyer: dict, lead: dict) -> str:
    lw_name = (lawyer or {}).get("name") or "Abogado"
    lid = (lead or {}).get("id", 0)
    nombre = (lead or {}).get("name") or "Cliente"
    phone = (lead or {}).get("phone") or ""
    cedula = (lead or {}).get("cedula") or ""
    email = (lead or {}).get("email") or ""
    descripcion = ((lead or {}).get("descripcion") or "").replace("<","&lt;").replace(">","&gt;")
    area = (lead or {}).get("area") or "general"
    status = (lead or {}).get("status") or "new"
    return f"""{_head(f"Lead #{lid} — {nombre}")}
<body>

{_nav("pro", active="leads", user_name=lw_name)}

<main class="container">
  <div style="margin-bottom:20px">
    <a href="/pro" class="btn btn-ghost btn-sm">← Volver a mis leads</a>
  </div>

  <div style="display:grid;grid-template-columns:360px 1fr;gap:24px">
    <!-- Panel izquierdo: ficha del cliente -->
    <aside>
      <div class="card" style="position:sticky;top:80px">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px">
          <div style="width:56px;height:56px;border-radius:50%;background:var(--ac);color:var(--w);display:grid;place-items:center;font-family:var(--fd);font-weight:600;font-size:22px">
            {(nombre[:2] or '?').upper()}
          </div>
          <div>
            <h2 style="font-family:var(--fd);font-size:18px;font-weight:600;color:var(--n);line-height:1.2">{nombre}</h2>
            <span class="bd bd-oro" style="margin-top:4px">{area}</span>
          </div>
        </div>

        <div style="font-size:13.5px;color:var(--g7);line-height:1.8">
          <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--g2)">
            <span style="color:var(--g5)">Estado</span>
            <span><span class="bd bd-info">{status}</span></span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--g2)">
            <span style="color:var(--g5)">WhatsApp</span>
            <span style="font-family:var(--fm);font-size:12.5px">+{phone or '—'}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--g2)">
            <span style="color:var(--g5)">Cédula</span>
            <span style="font-family:var(--fm);font-size:12.5px">{cedula or '—'}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:6px 0">
            <span style="color:var(--g5)">Correo</span>
            <span style="font-size:12.5px">{email or '—'}</span>
          </div>
        </div>

        <div style="margin-top:20px;display:grid;gap:8px">
          <a class="btn btn-wa" href="https://wa.me/{phone}" target="_blank" style="justify-content:center">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.6.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-1.4-.7-2.4-1.3-3.3-2.9-.3-.5.3-.5.8-1.5.1-.2 0-.3 0-.4l-.9-2.1c-.2-.5-.5-.5-.6-.5h-.6c-.2 0-.5.1-.7.3-.3.3-1 1-1 2.4 0 1.4 1 2.7 1.2 2.9.1.2 2 3.1 4.9 4.3 1.8.8 2.5.8 3.4.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3M12 2C6.5 2 2 6.5 2 12c0 1.7.5 3.4 1.3 4.8l-1.4 5.1 5.3-1.4c1.4.7 2.9 1.1 4.5 1.1h.3c5.5 0 10-4.5 10-10S17.5 2 12 2"/></svg>
            Escribir por WhatsApp
          </a>
          <button class="btn btn-pri" onclick="openSchedule()" style="justify-content:center">Agendar cita</button>
          <button class="btn btn-sec btn-sm" onclick="markStatus('contacted')" style="justify-content:center">Marcar contactado</button>
          <button class="btn btn-sec btn-sm" onclick="abrirExpediente()" style="justify-content:center">Abrir expediente con OTP →</button>
        </div>
      </div>
    </aside>

    <!-- Panel central: descripción + herramientas -->
    <section>
      <div class="card" style="margin-bottom:18px">
        <div class="card-h">Descripción del caso</div>
        <p class="card-d">Como el cliente lo contó al llenar el formulario</p>
        <div style="background:var(--g0);border-left:3px solid var(--ac);padding:18px 20px;border-radius:var(--r1);font-family:var(--fd);font-size:15px;line-height:1.7;color:var(--g9);font-style:italic">
          "{descripcion or '(sin descripción)'}"
        </div>
      </div>

      <div class="card" style="margin-bottom:18px">
        <div class="card-h">Herramientas IA</div>
        <p class="card-d">Genera documentos a partir del caso usando el motor RAG</p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <button class="btn btn-dark" onclick="genBorrador()" style="justify-content:center;padding:14px">
            ⚖ Generar borrador de tutela
          </button>
          <button class="btn btn-sec" onclick="genResumen()" style="justify-content:center;padding:14px">
            📋 Resumen ejecutivo
          </button>
          <button class="btn btn-sec" onclick="genPreguntas()" style="justify-content:center;padding:14px">
            ❓ Preguntas para el cliente
          </button>
          <button class="btn btn-sec" onclick="genCalculo()" style="justify-content:center;padding:14px">
            💰 Cálculo de pretensiones
          </button>
        </div>
      </div>

      <div class="card" id="result-card" style="display:none">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <div class="card-h" id="result-title">Resultado</div>
          <div>
            <button class="btn btn-ghost btn-sm" onclick="copyResult()">Copiar</button>
            <button class="btn btn-ghost btn-sm" onclick="downloadResult()">Descargar</button>
          </div>
        </div>
        <div id="result-out" style="background:var(--g0);border:1px solid var(--g2);border-radius:var(--r2);padding:24px;font-family:var(--fd);font-size:14.5px;line-height:1.7;color:var(--g9);white-space:pre-wrap;max-height:600px;overflow-y:auto"></div>
      </div>

      <div class="card" style="margin-top:18px">
        <div class="card-h">Notas internas</div>
        <p class="card-d">Solo visibles para abogados y admin del despacho</p>
        <div class="field">
          <textarea id="nota" placeholder="Escribe una nota sobre este lead..."></textarea>
        </div>
        <button class="btn btn-pri btn-sm" onclick="addNota()">Agregar nota</button>
        <div id="notas-list" style="margin-top:16px"></div>
      </div>
    </section>
  </div>
</main>

<div class="toast" id="toast"></div>

<script>
const LEAD_ID = {lid};
function toast(m, t) {{
  const el = document.getElementById('toast');
  el.textContent = m; el.className = 'toast show ' + (t || 'ok');
  setTimeout(() => el.classList.remove('show'), 2500);
}}

async function genBorrador() {{ await runTool('borrador', '⚖ Borrador de tutela'); }}
async function genResumen() {{ await runTool('resumen', '📋 Resumen ejecutivo'); }}
async function genPreguntas() {{ await runTool('preguntas', '❓ Preguntas para el cliente'); }}
async function genCalculo() {{ await runTool('calculo', '💰 Cálculo de pretensiones'); }}

async function runTool(tipo, title) {{
  const card = document.getElementById('result-card');
  const out = document.getElementById('result-out');
  document.getElementById('result-title').textContent = title;
  card.style.display = 'block';
  out.innerHTML = '<div style="text-align:center;padding:40px"><span class="spinner"></span> Generando con IA...</div>';
  card.scrollIntoView({{behavior:'smooth', block:'nearest'}});
  try {{
    const r = await fetch('/api/pro/lead/'+LEAD_ID+'/tool/'+tipo, {{method:'POST'}});
    if (!r.ok) {{
      out.textContent = 'Error: ' + (await r.text()).slice(0, 400);
      return;
    }}
    const j = await r.json();
    out.textContent = j.texto || j.result || '(sin contenido)';
    toast('Generado', 'ok');
  }} catch(e) {{
    out.textContent = 'Error de conexión: ' + e.message;
  }}
}}

function copyResult() {{
  navigator.clipboard.writeText(document.getElementById('result-out').textContent);
  toast('Copiado al portapapeles', 'ok');
}}
function downloadResult() {{
  const blob = new Blob([document.getElementById('result-out').textContent], {{type:'text/plain'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'lead-'+LEAD_ID+'-'+document.getElementById('result-title').textContent.split(' ')[1]+'.txt';
  a.click();
}}

async function markStatus(s) {{
  try {{
    await fetch('/api/pro/lead/'+LEAD_ID+'/status', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{status:s}})
    }});
    toast('Estado actualizado', 'ok');
    setTimeout(()=>location.reload(), 800);
  }} catch(e) {{ toast('Error', 'err'); }}
}}
function openSchedule() {{ location.href = '/pro/schedule?lead='+LEAD_ID; }}
async function abrirExpediente() {{
  try {{
    const r = await fetch('/api/pro/lead/'+LEAD_ID+'/expediente', {{method:'POST'}});
    if (!r.ok) {{ toast('Error abriendo expediente', 'err'); return; }}
    const j = await r.json();
    toast('OTP enviado al cliente', 'ok');
  }} catch(e) {{ toast('Error', 'err'); }}
}}
async function addNota() {{
  const txt = document.getElementById('nota').value.trim();
  if (!txt) return;
  try {{
    await fetch('/api/pro/lead/'+LEAD_ID+'/nota', {{
      method:'POST', headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{text:txt}})
    }});
    document.getElementById('nota').value = '';
    loadNotas();
    toast('Nota agregada', 'ok');
  }} catch(e) {{}}
}}
async function loadNotas() {{
  try {{
    const r = await fetch('/api/pro/lead/'+LEAD_ID+'/notas');
    if (!r.ok) return;
    const j = await r.json();
    if (!j.length) {{ document.getElementById('notas-list').innerHTML = ''; return; }}
    document.getElementById('notas-list').innerHTML = j.map(n => {{
      return '<div style="padding:10px 12px;background:var(--g0);border-left:3px solid var(--ac);border-radius:var(--r1);margin-bottom:8px;font-size:13.5px;color:var(--g9);line-height:1.5">' +
        '<div style="font-size:11.5px;color:var(--g5);margin-bottom:4px">'+(n.author||'')+' · '+(n.created_at||'').slice(0,16).replace('T',' ')+'</div>' +
        n.text + '</div>';
    }}).join('');
  }} catch(e) {{}}
}}
loadNotas();
</script>
</body></html>"""
