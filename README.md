# Galeano Herrera | Abogados — RAG Jurisprudencia CSJ

Motor RAG (Retrieval-Augmented Generation) sobre boletines de tutelas
de la Corte Suprema de Justicia de Colombia. Pensado para abogados
litigantes: **consulta**, **analiza casos** y **genera borradores de tutela**
respaldados con precedentes reales (radicados verificables).

---

## Lo que lo hace distinto

- **Búsqueda híbrida**: BM25 (léxico) + embeddings densos (semántico) fusionados con
  *Reciprocal Rank Fusion*.
- **Diversidad MMR**: evita devolver fichas redundantes.
- **Expansión de query** con sinónimos jurídicos colombianos (EPS / IPS / fuero materno / mínimo vital…).
- **Re-ranking con LLM** como juez antes de generar la respuesta.
- **Filtros** por sala, año y área (salud, pensiones, laboral, accidentes, insolvencia, derechos fundamentales).
- **Prompts estrictos**: cita obligatoria de radicado real, prohibido inventar.
- **Stack ligero**: FastAPI + FAISS + Gemini (text-embedding-004 + gemini-2.0-flash). Cero dependencias pesadas.

---

## Estructura

```
estrategia/
├── app/main.py                 ← FastAPI + UI
├── scripts/
│   ├── rag_motor.py            ← Motor RAG híbrido
│   ├── extraer_fichas.py       ← Extrae fichas desde PDFs
│   ├── descargar_boletines.py  ← Descarga boletines CSJ
│   └── pipeline_completo.py    ← Pipeline end-to-end
├── indices/                    ← fichas_index.jsonl, faiss.index, bm25.pkl
├── boletines/                  ← PDFs (no se commitean)
├── render.yaml                 ← Deploy a Render
├── Dockerfile                  ← Deploy a cualquier host
├── requirements.txt
└── .env.example
```

---

## Inicio rápido (local)

```bash
# 1) Dependencias
python -m pip install -r requirements.txt

# 2) Variable de entorno (NO commitees la key)
export GEMINI_API_KEY=AIza...

# 3) (Una sola vez) generar el índice FAISS
python scripts/rag_motor.py --indexar

# 4) Levantar la app
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# UI en http://localhost:8000
```

En Windows también puedes ejecutar `iniciar_app.bat`.

---

## Deploy en Render

1. **Crea un Web Service** apuntando a este repo (`gh-jurisprudencia-csj`).
2. Render detectará `render.yaml` automáticamente.
3. En **Environment** del servicio agrega:
   - `GEMINI_API_KEY` → tu key (rotada, **no la del repo viejo**).
   - `APP_USER` y `APP_PASS` (opcional) para activar Basic Auth en la UI.
4. **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
5. Tras el primer despliegue, llama `GET /indexar` (autenticado) **una vez** para
   generar embeddings reales (los del proxy sandbox eran inválidos).

> En el plan free de Render el contenedor duerme tras 15 min sin tráfico.
> El primer request tras dormir tarda ~30 s. Suficiente para uso interno;
> si lo abres a usuarios, sube a plan **Starter** ($7/mes).

---

## CLI (uso local sin UI)

```bash
# Consulta libre
python scripts/rag_motor.py "EPS niega cirugía oncológica"

# Analizar caso
python scripts/rag_motor.py --caso "cliente despido en embarazo, EPS Sanitas"

# Generar tutela
python scripts/rag_motor.py --tutela "Juan Pérez, CC 123, EPS Sura, niega medicamento X"

# Resumen de línea jurisprudencial filtrando por área
python scripts/rag_motor.py --linea "fuero materno" --area laboral

# Estadísticas del índice
python scripts/rag_motor.py --stats
```

---

## API REST

| Verbo | Ruta | Cuerpo / Query |
|------|------|----------------|
| GET  | `/salud` | — |
| GET  | `/estadisticas` | — |
| POST | `/consultar` | `{pregunta, area?, sala?, anio?, top_k?, rerank?}` |
| POST | `/analizar-caso` | `{descripcion, nombre_cliente?, area?}` |
| POST | `/generar-tutela` | `{nombre, cedula, accionado, hechos, derecho_vulnerado, area?}` |
| GET  | `/linea-jurisprudencial` | `tema, area?` |
| GET  | `/buscar` | `q, area?, anio?, sala?, top_k?` |
| GET  | `/indexar` | `forzar?` |

Docs OpenAPI automáticas en `/docs`.

---

## Seguridad

- La API key de Gemini **no se commitea**. Va en `.env` local o en el dashboard de Render.
- Si exportaste la key en algún commit anterior, **rótala** en
  https://aistudio.google.com/app/apikey.
- Activa Basic Auth con `APP_USER` + `APP_PASS` para uso interno del despacho.

---

---

## Incrustar/compartir la landing en Facebook

### Opción A · Compartir link (recomendada, 99% de casos)

Cuando compartes `https://gh-jurisprudencia-csj.onrender.com/` en Facebook, WhatsApp o LinkedIn, se muestra automáticamente:
- **Imagen** (1200×630) generada dinámicamente desde `/og.png` con la marca Galeano Herrera y headline
- **Título:** "Te están negando un derecho. Recuperalo en 2 minutos."
- **Descripción:** frase que engancha + fuentes verificables

Implementado mediante Open Graph + Twitter Card. No requiere configuración adicional.

**Refrescar el cache de Facebook** (si cambias la imagen o el copy):
1. Entra a https://developers.facebook.com/tools/debug/
2. Pega la URL `https://gh-jurisprudencia-csj.onrender.com/`
3. Click **"Scrape Again"** — Facebook recarga la preview.

### Opción B · Facebook Pixel (para campañas pagadas)

Si vas a pautar en Facebook/Instagram Ads:
1. En tu Business Manager, obtén tu `Pixel ID` (15-16 dígitos).
2. En el dashboard de Render, añade la env var: `FB_PIXEL_ID=<tu_pixel>`.
3. Render redeploya solo. El Pixel queda activo y dispara eventos:
   - `PageView` (landing)
   - `Lead` (cuando ve el preview)
   - `CompleteRegistration` (tras el formulario)
   - `Contact` (cuando verifica OTP)
   - `SimulacionDescargada` (custom — descarga DOCX)
   - `Schedule` (cuando agenda cita)

Con esto puedes optimizar campañas por "conversiones" reales, no por clicks.

### Opción C · Tab en Facebook Page (iframe)

Facebook permite incrustar un sitio web como **Tab de una página** via Facebook App:
1. Crea una app en https://developers.facebook.com/apps
2. Añade el producto **"Page Tabs"**
3. Como URL del tab, usa `https://gh-jurisprudencia-csj.onrender.com/`
4. En Render, set `ALLOW_IFRAME_EMBED=1` para que permita ser embebido (el sistema automáticamente relaja `X-Frame-Options` y añade CSP `frame-ancestors` con facebook.com)
5. Instala el tab en tu página.

⚠ **Opción C** es compleja y rara vez vale la pena. La **Opción A** convierte mejor porque el usuario llega a un sitio completo, no a una miniatura limitada.

### Verificar que el OG funciona

```bash
# Debug Facebook
https://developers.facebook.com/tools/debug/?q=https%3A%2F%2Fgh-jurisprudencia-csj.onrender.com%2F

# Debug Twitter
https://cards-dev.twitter.com/validator

# LinkedIn Post Inspector
https://www.linkedin.com/post-inspector/
```

---

*Galeano Herrera | Abogados — 2025*
