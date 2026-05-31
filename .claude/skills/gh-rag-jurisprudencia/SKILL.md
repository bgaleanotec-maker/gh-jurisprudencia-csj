# gh-rag-jurisprudencia

Gestionar el catálogo de jurisprudencia (sentencias de Corte Constitucional y Suprema) que alimenta el motor RAG.

## Cuándo invocarlo

- "El sistema cita una sentencia que no existe" / "El RAG trae jurisprudencia equivocada"
- Agregar nuevas sentencias al catálogo
- Reorganizar/depurar el índice RAG
- Cambiar el área de práctica de una sentencia
- Re-indexar tras cambios masivos

## Arquitectura RAG

```
PDFs sentencias  →  app/rag_ingest.py (parser + chunker)
                    ├── extrae texto del PDF
                    ├── divide en chunks de ~800 tokens
                    ├── etiqueta con área (salud, laboral, accidentes, ...)
                    ├── calcula embeddings (Gemini)
                    └── guarda en SQLite (tabla fichas) + índice FAISS

Consulta cliente (con o sin landing_cfg)
                 → tutela_lite.generar_borrador
                    ├── detecta área (auto o forzada por landing.area_focus)
                    ├── busqueda híbrida:
                    │    BM25 (palabras clave) + FAISS (semántica)
                    ├── top-N chunks → contexto_juris
                    ├── prompt template (genérico o de landing.prompt_template)
                    └── Gemini genera borrador con citaciones
```

## Áreas de práctica disponibles

```
derechos_fundamentales   (tutela genérica)
salud                    (T-760/2008, T-121/2024, ...)
seguridad_social         (pensiones, Colpensiones)
laboral                  (despido, fuero, contrato realidad)
accidentes               (SOAT, responsabilidad civil tránsito)
familia                  (alimentos, custodia)
penal                    (debido proceso, libertad)
civil_general
```

Agregar área nueva: edita `_AREAS_VALIDAS` en `app/rag_ingest.py` y `app/tutela_lite.py`.

## Archivos clave

| Archivo | Responsabilidad |
|---|---|
| `app/rag_ingest.py` | Parser PDF + chunker + embeddings + index FAISS |
| `app/tutela_lite.py` | Búsqueda híbrida + generación con Gemini |
| `app/db.py` `fichas` table | Chunks indexados con área, texto, número sentencia |
| `data/faiss.index` | Índice vectorial (binario) |
| `data/sentencias/` | PDFs originales (carpeta de subida) |

## Cómo agregar sentencias nuevas

### Opción A: Vía admin UI (recomendada)

1. Entra a `/admin` → tab "Cargar jurisprudencia"
2. Sube 1-N PDFs de sentencias
3. Selecciona el área correspondiente
4. (Opcional) Marca "Enriquecer con IA" para mejor extracción de metadatos
5. Espera procesamiento (puede tardar 30s por PDF si es largo)
6. Verifica en tabla de fichas que aparecen los chunks indexados

### Opción B: Vía script

```python
from app import rag_ingest
rag_ingest.procesar_pdf(
    path="data/sentencias/T-2024-456.pdf",
    area="salud",
    fuente="Corte Constitucional",
    enriquecer=True,  # usa IA para extraer número, fecha, magistrado
)
```

### Opción C: Bulk desde carpeta

```python
from app import rag_ingest
rag_ingest.procesar_carpeta(
    folder="data/sentencias/salud/",
    area="salud",
    enriquecer=True,
)
```

## Cómo depurar sentencias incorrectas

### Si la IA cita una sentencia que no existe

1. Lee el borrador generado, identifica el número (ej. T-555/2023)
2. Busca en BD:
   ```sql
   SELECT id, area, texto FROM fichas WHERE texto LIKE '%T-555/2023%';
   ```
3. Si NO existe → Gemini la inventó. Revisa el prompt template del vertical: debe decir "NO inventes sentencias, solo cita las del contexto"
4. Si SÍ existe pero está mal clasificada → corrige el `area` en la fila
5. Si está completamente errónea → marca como `inactiva=1` (no se eliminará pero no aparecerá en búsquedas)

### Si el RAG trae jurisprudencia de otro área

1. Verifica que `landing.area_focus` está seteado correctamente
2. Verifica que `tutela_lite._buscar_jurisprudencia` filtra por área cuando viene `landing_cfg`
3. Inspecciona qué chunks salieron en la última búsqueda (agregar log temporal)

## Formato esperado de sentencias

Los PDFs de la Corte vienen heterogéneos. El parser intenta extraer:
- **Número** (ej. T-760/2008, SU-070/2013, C-038/2020)
- **Magistrado ponente**
- **Fecha**
- **Línea jurisprudencial** (un resumen de 2-3 frases del thesis)
- **Texto completo** (para chunking semántico)

Si el parser falla → cae al texto crudo y solo se indexa por contenido (sin metadata).

## Re-indexar todo el catálogo

```python
from app import rag_ingest
rag_ingest.reindex_all()  # rebuilds FAISS desde cero
```

Tarda ~1 min por cada 100 fichas. Hacer solo si el FAISS quedó corrupto o si cambias el modelo de embeddings.

## Verificar calidad de un borrador

```python
from app import tutela_lite, db
cfg = db.get_landing_by_slug('tutelas')
r = tutela_lite.generar_borrador(
    descripcion="Mi EPS Sanitas no autoriza una cirugía urgente desde hace 3 meses",
    landing_cfg=cfg,
)
print(r)
```

Checklist:
- ✅ Cita 2-3 sentencias REALES del catálogo (verificable en BD)
- ✅ Las sentencias son del área correcta (no mezcla penal con salud)
- ✅ Estructura sigue el prompt template del vertical
- ✅ Las pretensiones tienen sentido jurídico
- ✅ No promete resultado ("vas a ganar")

## Anti-pattern: NO hacer

- ❌ Subir PDFs de gacetas judiciales (no son sentencias, son noticias)
- ❌ Mezclar sentencias de Costa Rica/Argentina con el catálogo Colombia
- ❌ Etiquetar como "salud" todo lo que mencione "salud" (T-760 es salud, T-156/2019 es debido proceso aunque mencione hospitales)
- ❌ Eliminar fichas en lugar de marcar `inactiva=1` (perdemos auditoría)
