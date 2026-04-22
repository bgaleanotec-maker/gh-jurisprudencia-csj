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

*Galeano Herrera | Abogados — 2025*
