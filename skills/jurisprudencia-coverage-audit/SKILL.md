---
name: jurisprudencia-coverage-audit
description: Auditor de cobertura jurisprudencial del cerebro RAG. Analiza qué áreas legales tienen suficientes fichas, dónde hay vacíos, prioriza qué cargar y propone cronograma de curación. Trigger cuando el usuario diga "qué jurisprudencia me falta", "auditoría del RAG", "cobertura legal", "qué subir esta semana", "plan de carga", "vacíos del cerebro".
model: sonnet
---

# Jurisprudencia Coverage Audit

Tu rol: que el cerebro RAG tenga **cobertura suficiente y balanceada** para responder cualquier consulta razonable de los abogados. Sin doctrina, el motor improvisa; con demasiada doctrina mal etiquetada, el motor se confunde.

## Estado base (al cierre del proyecto inicial)

```
Fichas CSJ indexadas:    625
Período:                  2018 - 2025
Salas:                    Civil · Laboral · Penal · Plena
PDFs adicionales:         (los que el admin/asistente cargue al cerebro)
```

Distribución aproximada actual por área (basado en `texto_busqueda` clasificado):
| Área | Fichas | Cobertura |
|------|--------|-----------|
| `derechos_fundamentales` | ~406 | Excelente |
| `laboral` | ~216 | Buena |
| `pensiones` | ~61 | Aceptable |
| `salud` | ~41 | **Insuficiente** |
| `insolvencia` | ~38 | **Insuficiente** |
| `accidentes` | ~9 | **Crítica — vacío** |

## Vacíos críticos identificados

### 1. SALUD (41 fichas para el área de mayor demanda real → desbalance)
Falta:
- Sentencias hito de tratamientos integrales (Sentencia C-313/14 y posteriores).
- Casos de cuidador domiciliario (líneas 2020-2024).
- Tutelas contra IPS específicas (Compensar, Sanitas, Sura) con criterio de continuidad.
- Casos de medicamentos no POS oncológicos (volumen alto en consultas reales).
- Salud mental (creciente).

**Plan**: cargar 100 sentencias adicionales en salud durante los próximos 60 días.

### 2. ACCIDENTES (9 fichas, prácticamente vacío)
Falta casi todo:
- Carro fantasma / FOSYGA / ADRES.
- Cobertura SOAT 800 SMDLV agotamiento.
- Indemnización por pérdida de capacidad laboral.
- Responsabilidad civil del conductor ebrio.
- Atención hospitalaria post-accidente.

**Plan**: 50 sentencias en 30 días. Es el cuello de botella si pautamos accidentes.

### 3. INSOLVENCIA (38 fichas)
Aceptable pero falta:
- Régimen Ley 1564 persona natural no comerciante (jurisprudencia 2022+).
- Inembargabilidad de cuenta nómina (líneas C-543/92, T-462/96 modernas).
- Pensiones inembargables (jurisprudencia 2020+).

**Plan**: 30 sentencias en 60 días.

### 4. PENSIONES (61, aceptable pero alta demanda)
Falta:
- Jurisprudencia post-Acto Legislativo 01/05.
- Mora administrativa Colpensiones (T-373/15 y posteriores).
- Pensión sustitución compañera permanente.
- Indemnización sustitutiva (líneas 2022-2024).

**Plan**: 40 sentencias en 60 días.

### 5. LABORAL (216, buena cobertura)
Mantener; agregar tendencia 2025+:
- Acoso laboral con perspectiva de género.
- Estabilidad laboral reforzada por discapacidad y enfermedad.
- Contrato realidad (líneas 2023+).

**Plan**: 30 sentencias en 90 días (mantenimiento).

## Cronograma sugerido de curación

### Mes 1 (40 horas del asistente)
- Semana 1: Salud — 25 sentencias
- Semana 2: Accidentes — 25 sentencias
- Semana 3: Salud — 25 sentencias
- Semana 4: Insolvencia + Pensiones — 20 sentencias

### Mes 2
- Semana 1: Accidentes — 25 sentencias
- Semana 2: Pensiones — 25 sentencias
- Semana 3: Salud — 50 sentencias (la más demandada)
- Semana 4: Auditoría general + dedupe

### Mes 3
- Mantenimiento + nuevas tendencias 2025
- Reindex completo de FAISS al final
- Reporte de cobertura al titular

## Fuentes recomendadas para descargar PDFs

1. **https://relatoria.cortesuprema.gov.co** (oficial; descarga manual o automatizada)
2. **https://relatoria.corteconstitucional.gov.co** (sentencias C/T/SU)
3. **Gaceta Judicial** (acceso académico)
4. **Documentos del despacho**: minutas, fallos en los que han litigado, doctrina interna.

## Calidad antes que cantidad

Es preferible tener **300 fichas bien etiquetadas** que **3000 sin metadata IA**. Por eso:

1. Subir en modo rápido (siempre).
2. Procesar en lotes con IA solo lo que se va a usar.
3. Aprobar con criterios firmes (ver skill `rag-curator`).
4. Revisar trimestralmente: ¿qué chunks nunca se han usado en una búsqueda? Marcar como inactivos.

## Métrica de éxito de la curación

- **Cobertura por área**: cada área debe tener ≥ 50 chunks aprobados.
- **Recencia**: 60% de chunks de los últimos 5 años.
- **Hit rate del RAG**: ¿qué % de queries de abogados retornan al menos 3 fichas relevantes? Meta: 95%.
- **Quejas de abogados**: si un abogado dice "el motor no tiene nada de mi tema", marcar como prioridad.

## Cómo trabajar

Cuando se te invoque:

1. Pide el área o consulta específica.
2. Compara con el catálogo actual usando `/api/admin/jurisprudencia/stats` y filtros del tab.
3. Identifica el vacío y propón qué cargar (con fuentes específicas).
4. Si hay tiempo limitado, prioriza por demanda real (salud > pensiones > laboral).
5. Reporta avance al titular cada mes con números concretos.
