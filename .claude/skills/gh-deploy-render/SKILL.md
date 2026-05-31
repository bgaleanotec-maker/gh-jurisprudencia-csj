# gh-deploy-render

Deploy seguro a Render con checks pre/post.

## Cuándo invocarlo

- Después de cualquier `git push origin main` que afecte el servicio
- Cuando algo en producción no funciona y hay que diagnosticar
- Antes de hacer una migración crítica de schema
- Cuando cambias env vars en Render

## Datos del servicio

| Recurso | Valor |
|---|---|
| **Service ID** | `srv-d7k432bbc2fs73fruhhg` |
| **Owner ID** | `tea-d5r51iidbo4c73abl6t0` |
| **Plan** | Free ⚠️ (sin disk persistente — BD se borra en cada deploy) |
| **URL** | `https://gh-jurisprudencia-csj.onrender.com` |
| **Auto-deploy** | Activado desde `main` branch |
| **Repo** | `bgaleanotec-maker/gh-jurisprudencia-csj` |

## Pre-deploy checks

### 1. Smoke test local
```bash
cd "C:/Users/bgale/OneDrive/Mercado_legal/estrategia"
python -c "
import sys, os, tempfile
os.environ['DATA_DIR'] = tempfile.mkdtemp()
import app.main as m
print('main.py OK ->', type(m.app).__name__)
"
```

### 2. Verificar que la migración de BD no rompa
Si tocaste `app/db.py`, prueba:
```bash
python -c "
from app import db
db.init_db(); db._migrate()
db.bootstrap_default_lawyer()
print('migration OK')
"
```

### 3. Validar imports y rutas
```bash
python -c "
import app.main as m
print('routes:', len(list(m.app.routes)))
"
```

## Push y deploy

```bash
git add app/<archivos> .claude/<skills>
git commit -m "feat(scope): descripcion concisa"
git push origin main
```

Render detecta el push y empieza el build automáticamente (~3-5 min).

## Esperar deploy live (background)

```bash
until [ "$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
   'https://api.render.com/v1/services/srv-d7k432bbc2fs73fruhhg/deploys?limit=1' \
   | python -c 'import sys,json; print(json.load(sys.stdin)[0]["deploy"]["status"])')" = "live" ]
do sleep 15; done
echo "LIVE"
```

Estados intermedios: `created → build_in_progress → update_in_progress → live` (o `build_failed`, `update_failed`).

## Post-deploy verification

### 1. Health check WhatsApp
```bash
curl -s https://gh-jurisprudencia-csj.onrender.com/wa/health | python -m json.tool
```
Debe responder:
- `gemini_key_present: true`
- `evolution_key_present: true`
- `mode_global: hibrido` (o lo que esté seteado)
- `office_hours: 14:00-18:00` (o lo configurado)

### 2. Landings HTTP 200
```bash
for s in tutelas accidentes comparendos laboral; do
  printf "%-12s " "$s"
  curl -s -o /dev/null -w "HTTP %{http_code}  %{size_download} bytes\n" \
    "https://gh-jurisprudencia-csj.onrender.com/c/$s"
done
```

### 3. Admin accesible
```bash
curl -s -u "galeano:TI_of50yTTlVC-z6pdEXgQ" \
  https://gh-jurisprudencia-csj.onrender.com/api/admin/wa/config | head -c 200
```

### 4. Webhook Evolution apuntando correcto
```bash
curl -s -H "apikey: <evolution_global_key>" \
  http://2.24.212.56:8080/webhook/find/abogados-hseq \
  | python -c "import sys,json; print(json.load(sys.stdin)['url'])"
```
Debe ser: `https://gh-jurisprudencia-csj.onrender.com/wa/evolution/webhook`

### 5. Logs en vivo
```bash
START=$(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/logs?ownerId=tea-d5r51iidbo4c73abl6t0&resource=srv-d7k432bbc2fs73fruhhg&limit=50&startTime=$START&endTime=$END&direction=backward" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(l['timestamp'][11:19],'|',l['message'][:160]) for l in d.get('logs',[])]"
```

Buscar `[wa]` para pipeline WhatsApp, `[db]` para migrations, `ERROR` para problemas.

## Rollback si algo falla

### Opción A: Revert commit
```bash
git revert HEAD --no-edit
git push origin main
```
Render hace nuevo deploy con el revert.

### Opción B: Trigger rollback desde Render API
```bash
DEPLOY_ID="dep-XXXXX"  # del deploy anterior live
curl -X POST -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/services/srv-d7k432bbc2fs73fruhhg/rollback" \
  -d "{\"deployId\":\"$DEPLOY_ID\"}"
```

## ⚠️ Limitación crítica del plan free

**Cada deploy borra `/var/data`** (la SQLite). Implicación:
- Leads / conversaciones / abogados / appointments se pierden
- Las landings se recrean por `bootstrap_default_lawyer()` en startup
- La config de wa_config también se re-crea con defaults

**Solución:** upgrade a plan **Starter ($7/mes)** que permite disk de 1 GB persistente.

Cuando se haga el upgrade:
```bash
# Setear DATA_DIR como env var
curl -X PUT -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/services/srv-d7k432bbc2fs73fruhhg/env-vars \
  -d '[{"key":"DATA_DIR","value":"/var/data"}]'

# Crear disk de 1GB en /var/data
curl -X POST -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/disks \
  -d '{"serviceId":"srv-d7k432bbc2fs73fruhhg","name":"data","mountPath":"/var/data","sizeGB":1}'
```

## Env vars que NUNCA deben faltar

| Variable | Para qué |
|---|---|
| `GEMINI_API_KEY` | RAG + María Camila — sin esto la IA muere |
| `EVOLUTION_API_URL` | Donde está Evolution (http://2.24.212.56:8080) |
| `EVOLUTION_API_KEY` | Key global de Evolution |
| `EVOLUTION_INSTANCE` | `abogados-hseq` |
| `WA_PROVIDER` | `evolution` (o `hybrid` si UltraMsg de fallback) |
| `SECRET_KEY` | Firma sesiones de abogados |
| `ADMIN_USER`/`ADMIN_PASS` | Login admin HTTP Basic |
| `PUBLIC_URL` | URL pública del sitio (para enlaces en correos/WA) |

Verificar:
```bash
curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/services/srv-d7k432bbc2fs73fruhhg/env-vars?limit=50" \
  | python -c "import sys,json; d=json.load(sys.stdin); [print(v['envVar']['key']) for v in d]"
```
