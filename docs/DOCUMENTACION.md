# Galeano Herrera — Documentación del sistema

> Plataforma legal SaaS: captación de clientes por simulación de tutelas + agenda + dashboard multi-abogado. Colombia, 2026.

**Estado:** producción · **URL:** <https://gh-jurisprudencia-csj.onrender.com>

---

## Índice

1. [Qué es y qué no es](#1-qu%C3%A9-es-y-qu%C3%A9-no-es)
2. [Arquitectura](#2-arquitectura)
3. [Flujos de usuario](#3-flujos-de-usuario)
4. [Modelo de datos](#4-modelo-de-datos)
5. [API Reference](#5-api-reference)
6. [Manual del Admin](#6-manual-del-admin)
7. [Manual del Abogado](#7-manual-del-abogado)
8. [Deploy y entornos](#8-deploy-y-entornos)
9. [Configuración (env vars)](#9-configuraci%C3%B3n-env-vars)
10. [Skills instalados](#10-skills-instalados)
11. [Troubleshooting](#11-troubleshooting)
12. [Roadmap](#12-roadmap)

---

## 1. Qué es y qué no es

**Qué es:**
- Motor RAG con 625 sentencias de la Corte Suprema (Salas Civil, Laboral, Penal, Plena — 2018-2025).
- Landing pública que convierte visitantes en **leads verificados por OTP WhatsApp**.
- Dashboard interno para abogados: sus leads + agenda propia + asistente RAG completo.
- Panel admin para gestionar abogados, ver embudo y leads.

**Qué NO es:**
- Una asesoría jurídica autónoma — las simulaciones son orientativas.
- Un sustituto del abogado titulado — el cierre y la radicación los hace un humano.
- Un sistema con escalabilidad infinita en el plan free (Render duerme tras 15 min inactivo).

---

## 2. Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│  Cliente (Chrome / Safari mobile)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Render Web Service (Oregon)                                 │
│  FastAPI · uvicorn · Python 3.11                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │  app/                                             │       │
│  │    main.py     ← Rutas (landing, admin, pro, api)│       │
│  │    ui.py       ← HTML landing/admin/dashboard    │       │
│  │    db.py       ← SQLite (leads, lawyers, appts)  │       │
│  │    auth.py     ← Sesiones itsdangerous           │       │
│  │    whatsapp.py ← UltraMsg + OTP store            │       │
│  │    tutela_lite.py ← Generador low-cost + DOCX    │       │
│  │    agenda.py   ← Slots, bloqueos, semana         │       │
│  │  scripts/                                          │       │
│  │    rag_motor.py ← Motor RAG (BM25+FAISS+Gemini)  │       │
│  │  indices/                                          │       │
│  │    fichas_index.jsonl  ← 625 sentencias          │       │
│  │    faiss.index  (se regenera al boot)            │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬────────────────┐
        │              │              │                │
        ▼              ▼              ▼                ▼
   Gemini API    UltraMsg API    Render Cron      SQLite local
   (LLM)         (WhatsApp)      (recordatorios)  (leads, lawyers)
```

**Componentes externos**
- **Gemini** `gemini-embedding-001` + `gemini-2.0-flash(-lite)`: embeddings y generación.
- **UltraMsg**: envío WhatsApp (OTP, confirmaciones, recordatorios).
- **Render Cron Job**: llama `/api/cron/reminders` cada 15 min.
- **SQLite WAL**: `data/leads.db` — leads, abogados, citas, bloqueos, eventos.

---

## 3. Flujos de usuario

### 3.1 Flujo cliente (captura y conversión)

```
 landing /
    │ escribe descripción + click "Conocer mi caso"
    ▼
 POST /api/lead/preview
    │  ↓ si ya existe en cache → respuesta en 200 ms
    │  ↓ si no → 1 call a Gemini (≈12 s)
    ▼
 ve simulación parcial (≈30% visible)
    │ click "Continuar"
    ▼
 completa 4 campos + 3 consents (T&C, Habeas Data, marketing)
    │
    ▼
 POST /api/lead/register
    │  ↓ UltraMsg envía OTP al celular
    ▼
 ingresa OTP de 6 dígitos
    │
    ▼
 POST /api/lead/verify-otp
    │  ↓ marca status=verified
    │  ↓ asigna abogado según área o default
    │  ↓ WhatsApp al abogado con datos + link DOCX
    ▼
 descarga DOCX + ve slots disponibles del abogado
    │ click slot
    ▼
 POST /api/lead/book
    │  ↓ crea appointment
    │  ↓ WhatsApp al cliente (confirmación)
    │  ↓ WhatsApp al abogado (nueva cita)
    ▼
 FIN → el abogado llama al cliente a la hora pactada
```

**Recordatorios** (Render Cron cada 15 min → `/api/cron/reminders`):
- 24 h antes → WhatsApp al cliente.
- 1 h antes → WhatsApp al cliente **y** al abogado.

### 3.2 Flujo abogado

```
 /pro/login  → email + password
    │
    ▼
 /pro dashboard
    ├─ Meta diaria: X/10 tutelas cerradas hoy (barra de progreso)
    ├─ Mini-stats: por contactar · citas próximas · tasa cierre · tiempo respuesta
    ├─ Embudo 7 días: verified → contacted → closed
    │
    ├─ Tab Agenda → calendario semanal (libre/booked/blocked)
    │    ├─ Click slot libre → bloquear
    │    ├─ Click bloqueo → desbloquear
    │    └─ Click cita → detalle del lead
    │
    ├─ Tab Mis Leads → tabla con filtro por estado
    │    └─ Acciones: ver · marcar contactado · cerrar
    │
    ├─ Tab Asistente Jurídico → 4 herramientas RAG
    │    ├─ Consulta libre (filtros área/sala/año)
    │    ├─ Análisis de caso (protocolo Galeano)
    │    ├─ Generar tutela (con datos del cliente)
    │    └─ Línea jurisprudencial (tesis + evolución + excepciones)
    │
    └─ Tab Cuenta → ver datos + cambiar password
```

### 3.3 Flujo admin

```
 /admin (Basic Auth)
    ├─ Stats globales + embudo 7d visual
    │
    ├─ Tab Leads → todos los leads del sistema
    │
    ├─ Tab Citas → todas las citas próximas
    │
    ├─ Tab Abogados → CRUD
    │    ├─ Agregar: nombre, whatsapp, email, password, áreas, default
    │    ├─ Reset password
    │    ├─ Toggle disponibilidad
    │    └─ Eliminar
    │
    └─ Tab Sistema → salud de integraciones (Gemini, UltraMsg, FAISS)
```

---

## 4. Modelo de datos

```sql
-- Abogados (login + disponibilidad + asignación por área)
lawyers(
  id, name, whatsapp, email UNIQUE, password_hash, password_salt,
  areas JSON,         -- ej: ["salud","laboral"] o ["*"] para todas
  active, available,  -- on/off visibilidad
  is_default,         -- recibe leads sin área específica
  created_at
)

-- Leads (captura pública)
leads(
  id, token UNIQUE, name, cedula, phone, email,
  area,               -- auto-detectada o elegida
  descripcion, draft, fichas JSON,
  status,             -- preview | pending_otp | verified | contacted | closed
  otp_verified, lawyer_id,
  ip, user_agent,
  consent_terms, consent_data, consent_marketing,
  created_at, verified_at, contacted_at, notes
)

-- Citas (agenda nativa, sin Google Calendar)
appointments(
  id, lead_id, lawyer_id,
  scheduled_at, duration_min,
  calendar_event_id,  -- reservado (no usado en v5+)
  meet_url,           -- el abogado puede pegar un link manual
  html_link,          -- reservado
  status,             -- scheduled | cancelled_by_user | cancelled_by_lawyer | completed | no_show
  reminded_24h, reminded_1h,
  created_at, cancelled_at, notes
)

-- Bloqueos manuales del abogado
lawyer_blocks(
  id, lawyer_id, start_at, end_at, reason, created_at
)

-- Tracking de embudo
events(
  id, type,           -- page_view | preview_started | preview_done | register | otp_verified | downloaded | meeting_booked | meeting_cancelled
  ip, user_agent, referer, payload JSON,
  ts
)

-- Rate limit por IP
rate_limit(
  ip, window_start, count
)
```

---

## 5. API Reference

### Públicos (sin auth)

| Método | Ruta | Body / Query | Respuesta |
|--------|------|--------------|-----------|
| GET    | `/` | — | Landing HTML |
| GET    | `/salud` | — | Health check |
| POST   | `/api/track` | `{type, payload}` | `{ok:true}` |
| POST   | `/api/lead/preview` | `{descripcion, area?}` | `{token, preview:{visible,oculto_chars}, fichas, area_detectada}` |
| POST   | `/api/lead/register` | `{token, name, cedula, phone, email, consent_*}` | `{ok, phone_normalized, wa_sent}` |
| POST   | `/api/lead/resend-otp` | `{token}` | `{ok}` |
| POST   | `/api/lead/verify-otp` | `{token, otp}` | `{ok, download_url, calendar_enabled}` |
| GET    | `/api/lead/download/{token}.docx` | — | DOCX file |
| GET    | `/api/lead/slots?token=...&days=7` | — | `{ok, slots[], lawyer:{name,whatsapp}}` |
| POST   | `/api/lead/book` | `{token, start_iso, duration_min?}` | `{ok, appointment_id, start, lawyer_name}` |
| GET    | `/api/lead/appointment?token=...` | — | `{ok, appointment, puede_cancelar}` |
| POST   | `/api/lead/cancel-appointment` | `{token}` | `{ok}` |
| POST   | `/api/lead/reschedule` | `{token, start_iso}` | `{ok, start}` |

### Abogado autenticado (cookie `gh_session`)

| Método | Ruta | Propósito |
|--------|------|-----------|
| GET  | `/pro/login` | Form login |
| POST | `/pro/login` | Autentica y redirige a `/pro` |
| GET  | `/pro/logout` | Borra cookie |
| GET  | `/pro` | Dashboard HTML |
| GET  | `/api/pro/me` | Datos del abogado logueado |
| PATCH | `/api/pro/me` | `{available?, password?}` |
| GET  | `/api/pro/metrics` | Meta diaria, embudo 7d, tasa cierre |
| GET  | `/api/pro/agenda?start=YYYY-MM-DD` | Grid semanal |
| POST | `/api/pro/blocks` | `{start_iso,end_iso,reason?}` |
| DELETE | `/api/pro/blocks/{id}` | Borra bloqueo propio |
| GET  | `/api/pro/leads?status=...` | Leads asignados + del área |
| GET  | `/api/pro/leads/{id}` | Detalle + borrador completo |
| GET  | `/api/pro/appointments?upcoming=true` | Sus citas |
| PATCH | `/api/pro/appointments/{id}` | `{meet_url?, status?, notes?}` |
| POST | `/api/pro/consultar` | RAG — consulta libre |
| POST | `/api/pro/analizar-caso` | RAG — protocolo de caso |
| POST | `/api/pro/generar-tutela` | RAG — tutela completa |
| GET  | `/api/pro/linea-jurisprudencial?tema=...` | RAG — línea temática |
| GET  | `/api/pro/buscar?q=...` | RAG — búsqueda directa |

### Admin (Basic Auth `ADMIN_USER:ADMIN_PASS`)

| Método | Ruta | Propósito |
|--------|------|-----------|
| GET | `/admin` | Panel HTML |
| GET | `/api/admin/stats` | Globales + `funnel_7d` + `daily_14d` |
| GET | `/api/admin/leads?status=...` | Lista leads |
| GET | `/api/admin/leads/{id}` | Detalle completo (con draft entero) |
| PATCH | `/api/admin/leads/{id}` | `{status?, notes?}` |
| GET | `/api/admin/lawyers` | Lista abogados |
| POST | `/api/admin/lawyers` | Alta (con email+password opcional) |
| PATCH | `/api/admin/lawyers/{id}` | `{email?, password?, available?}` |
| DELETE | `/api/admin/lawyers/{id}` | Borra |
| GET | `/api/admin/appointments?upcoming=true` | Todas las citas |
| GET | `/api/admin/config` | Salud de integraciones |

### Cron (token)

| GET `/api/cron/reminders?t=CRON_TOKEN` — envía recordatorios 24 h y 1 h. |

---

## 6. Manual del Admin

**URL:** <https://gh-jurisprudencia-csj.onrender.com/admin>
**Usuario:** `ADMIN_USER` (env var) — default `galeano`
**Password:** `ADMIN_PASS` (env var)

### 6.1 Primer día (onboarding)

1. Entra a `/admin`.
2. Tab **Abogados** → agrega al menos 1 abogado con:
   - Nombre legible (aparece en WhatsApp)
   - WhatsApp formato `573XXXXXXXXX` (sin `+`)
   - Email de login (se lo comunicas por canal seguro)
   - Password (si no lo llenas se genera random — el sistema te lo muestra)
   - Áreas: separadas por coma (`salud,laboral`) o `*` para todas
   - Marcar **Default** si es el único o el principal
3. Comunica al abogado sus credenciales + URL `/pro/login`.

### 6.2 Día a día

- **Pestaña Leads:** ordena por "verified" para ver los nuevos sin contactar.
- **Pestaña Citas:** revisa las próximas 48 h.
- **Pestaña Sistema:** confirma que todos los checks están en verde (Gemini, UltraMsg, FAISS, abogado default).

### 6.3 KPIs a mirar cada lunes

1. **Total 7d** (nuevos leads)
2. **Conversión OTP** (verified / total) — objetivo > 40 %
3. **Conversión contacto** (contacted / verified) — objetivo > 85 % en < 2 h
4. **Cerrados** vs contacted — objetivo > 25 %

Datos en `/api/admin/stats` o visibles en el panel.

---

## 7. Manual del Abogado

**URL:** <https://gh-jurisprudencia-csj.onrender.com/pro/login>

### 7.1 Primer ingreso

1. Usa el email y password que te dio admin.
2. Tab **Cuenta** → cambia la password a una tuya.
3. Tab **Agenda** → revisa tu grid semanal; por default eres L-V 9-12 / 14-17 Bogotá.
4. Al inicio del día, activa el **toggle de Disponibilidad** (arriba) para recibir leads.

### 7.2 Cuando llega un lead

1. Recibes WhatsApp automático con: nombre, cédula, teléfono, email, área, resumen del caso, link al DOCX, link `wa.me/`.
2. Entra a `/pro` → Tab **Mis Leads** → click **Ver** para ver el borrador completo.
3. Llama por WhatsApp al cliente citando 1 dato específico del caso (técnica "liking" — ver skill `consumer-psychology`).
4. Al terminar la conversación:
   - Si cerró → **Marcar cerrado**
   - Si quedó en stand-by → **Marcar contactado**
5. Si el cliente agendó cita desde la landing, aparecerá en tu tab **Agenda** → click la cita para ver detalle.
6. Si prefieres hacer la cita por Meet/Zoom, edita la cita desde **Agenda → Próximas citas → Agregar link Meet** y el cliente ya podrá verlo.

### 7.3 Usar el RAG para preparar un caso

Tab **Asistente Jurídico**. 4 herramientas:

- **Consulta libre**: pregunta abierta. Sirve para preparar la llamada.
  > Ej: "negativa de medicamento no POS para paciente oncológico ambulatorio"
- **Análisis de caso**: entrega el protocolo Galeano (clasificación + diagnóstico + estrategia + precedentes + siguiente paso).
- **Generar tutela completa**: cuando ya cerraste y vas a radicar. Rellena nombre, cédula, accionado, derecho, hechos → devuelve el documento listo para revisar.
- **Línea jurisprudencial**: tesis dominante + evolución + cuándo NO concede. Perfecto para anticipar objeciones.

Todo cita radicados reales. **Verifica cada radicado** en <https://relatoria.cortesuprema.gov.co> antes de firmar.

### 7.4 Gestionar tu agenda

- **Click slot libre** → bloqueas 30 min con una razón (almuerzo, reunión, etc.).
- **Click bloqueo** → lo quitas.
- **Click cita agendada** → ves datos del cliente.
- **Navegación ◀ ▶** para semanas adelante/atrás.
- Si no quieres recibir leads hoy, **apaga el toggle de Disponibilidad**.

### 7.5 Metas (gamificación)

- Barra superior: **X / 10 tutelas cerradas hoy**. Verde cuando llegas a 10.
- Mini-stats:
  - **Leads por contactar** (verified sin tu click)
  - **Citas próximas**
  - **Tasa de cierre** (closed / verified — verde si > 25%, ámbar si > 15%)
  - **Tiempo respuesta promedio** (verde si < 2 h)

Cada métrica viene de `/api/pro/metrics` en tiempo real.

---

## 8. Deploy y entornos

### 8.1 Producción (Render)

- Servicio: `srv-d7k432bbc2fs73fruhhg` (Oregon, plan free)
- Auto-deploy desde `main` del repo.
- Build: `pip install --upgrade pip && pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
- Health: `/salud`

### 8.2 Cron Job

- Servicio: `crn-d7k5g10sfn5c73bq2sd0`
- Schedule: `*/15 * * * *`
- Command: `python -c "import os,httpx;httpx.get(os.environ['URL'],timeout=30)"`
- Env var `URL=https://gh-jurisprudencia-csj.onrender.com/api/cron/reminders?t=<CRON_TOKEN>`

### 8.3 Local (desarrollo)

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=AIza...
export ULTRAMSG_INSTANCE_ID=instance154562
export ULTRAMSG_TOKEN=gxcg5k06jjz7fmi0
export DEV_MODE=1    # OTP devuelto en la respuesta
uvicorn app.main:app --reload
# http://localhost:8000
```

### 8.4 Limitaciones del plan free

- **Disco efímero:** cada redeploy borra `data/leads.db`. Los abogados y leads se pierden. Solución: subir a plan **Starter** ($7/mes) + añadir **Persistent Disk** ($1/mes).
- **Sleep 15 min:** el servicio duerme tras 15 min sin tráfico. Primer request tras dormir tarda ~45 s (spin-up + auto-index FAISS).

---

## 9. Configuración (env vars)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `GEMINI_API_KEY` | ✅ | Clave de Google AI Studio |
| `ULTRAMSG_INSTANCE_ID` | ✅ | `instance154562` |
| `ULTRAMSG_TOKEN` | ✅ | Token de la instancia |
| `SECRET_KEY` | ✅ | Firma de cookies de sesión (≥ 32 chars random) |
| `ADMIN_USER` | ✅ | Usuario del panel admin |
| `ADMIN_PASS` | ✅ | Password del admin |
| `CRON_TOKEN` | ✅ | Para `/api/cron/reminders?t=...` |
| `PYTHON_VERSION` | ✅ | `3.11.9` |
| `DEV_MODE` | ⬜ | Si `1`, OTP viene en respuesta (solo testing) |
| `LAWYER_WHATSAPP` | ⬜ | Si hay DB vacía al arranque, crea abogado default |
| `LAWYER_NAME` | ⬜ | Nombre del abogado default |
| `DATA_DIR` | ⬜ | Directorio de SQLite (default `./data`) |

---

## 10. Skills instalados

Expertos consultables desde el sistema (`/skills/*/SKILL.md`):

| Skill | Propósito |
|-------|-----------|
| `neuromarketing-klaric` | Código reptil aplicado al cliente legal |
| `behavioral-economics` | Nudges éticos, anchoring, micro-commitments |
| `consumer-psychology` | Cialdini + Heath + arco emocional del cliente |
| `color-theory-legal` | Paleta por vertical + WCAG AA |
| `lean-legal-saas` | Build-Measure-Learn, hipótesis, RICE |
| `landing-converter` | Optimización conversión de la landing |
| `whatsapp-lead-nurture` | Secuencias WA por área |
| `qc-tutela` | QC anti-alucinación antes de firmar |
| `calendar-mgmt` | Agenda nativa, slots, recordatorios |
| `lawyer-onboarding` | Alta + capacitación + metas de nuevos abogados |
| `conversion-tracker` | Embudo, ROI, reportes semanales |

---

## 11. Troubleshooting

### "La IA dice que está ocupada"
- Síntoma: usuarios ven "Estamos atendiendo muchos usuarios...".
- Causa: Gemini free tier agotado (15 RPM / 1500 RPD).
- Fix inmediato: esperar 60 s — hay cache normalizado + retry cascada de modelos.
- Fix definitivo: activar billing en <https://aistudio.google.com/app/apikey>. Costo: < $1/mes para 1000 leads.

### "No llega el OTP"
- Chequea `/salud → ultramsg: true`.
- Verifica que el celular esté en formato Colombia (12 dígitos: `573XXXXXXXXX`).
- `DEV_MODE=1` muestra OTP en la respuesta JSON (solo para testing).

### "Los abogados desaparecen después de un deploy"
- Causa: disco efímero del plan free. La DB se borra al reiniciar.
- Fix: upgrade a Starter + Persistent Disk. Mientras tanto, el admin puede recrear rápido desde `/admin`.

### "Calendar falla" o "no veo slots"
- La versión actual usa **agenda nativa** (no Google Calendar).
- Si no ves slots:
  - Verifica que haya al menos 1 abogado con `available=1` en `/admin → Abogados`.
  - Verifica que la asignación haya encontrado un abogado de esa área (o un `*`).

### "El cron no envía recordatorios"
- Golpéalo a mano: `curl "https://<url>/api/cron/reminders?t=<CRON_TOKEN>"` — debe devolver `{ok:true, sent:{...}}`.
- Revisa el cron service en Render (`crn-...`) que no esté suspended.

### "Login del abogado no funciona"
- El email debe estar **exactamente** como lo registraste (case-insensitive al comparar).
- Si olvidó la password: admin → `/admin` → Abogados → `Reset pass`.

### "El DOCX descargado está vacío"
- Probablemente el preview falló silenciosamente y el draft quedó vacío. Verifica en `/api/admin/leads/{id}.draft` que haya contenido.

---

## 12. Roadmap

### Mes 1 (consolidar)
- [x] Agenda nativa con bloqueos
- [x] Dashboard abogado con meta diaria
- [x] Skills expertos (11 ya instalados)
- [ ] Persistent disk Render
- [ ] Email transaccional (Resend) como backup a OTP WhatsApp

### Mes 2 (escalar)
- [ ] Landings verticales: `/eps-niega`, `/despido-embarazo`, `/pension-demorada`
- [ ] Webhook a Google Sheets como backup de leads
- [ ] Pagos: cobro por revisión de borrador ($50k)
- [ ] reCAPTCHA v3 antimbots

### Mes 3 (producto)
- [ ] App móvil (PWA primero)
- [ ] Firma electrónica de poderes
- [ ] Programa referidos con descuento
- [ ] Expansión a otras ciudades (Medellín, Cali, Barranquilla)

---

## Contacto

- **Repo:** <https://github.com/bgaleanotec-maker/gh-jurisprudencia-csj>
- **Dashboard Render:** <https://dashboard.render.com/web/srv-d7k432bbc2fs73fruhhg>
- **UltraMsg:** <https://app.ultramsg.com>
- **Gemini AI Studio:** <https://aistudio.google.com>

*Documento vivo — actualizar con cada deploy relevante.*
