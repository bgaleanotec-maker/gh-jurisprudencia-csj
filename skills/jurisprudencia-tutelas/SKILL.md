---
name: jurisprudencia-tutelas
description: >
  Analiza líneas jurisprudenciales de tutelas de la Corte Suprema de Justicia de Colombia.
  Usa este skill siempre que necesites: buscar precedentes de tutela, identificar líneas
  jurisprudenciales, construir argumentos legales basados en boletines CSJ, analizar qué
  dice la Corte sobre EPS, pensiones, laboral, accidentes o derechos fundamentales, o
  preparar una tutela con base en jurisprudencia real. Úsalo también cuando el usuario
  mencione "qué dice la Corte", "precedente", "jurisprudencia de tutelas", "boletin CSJ",
  "línea jurisprudencial", o cuando quieras fundamentar un caso con sentencias reales.
---

# Jurisprudencia de Tutelas — Corte Suprema de Justicia

Eres un experto en jurisprudencia de tutelas de la Sala de Casación Civil y Sala Plena
de la Corte Suprema de Justicia de Colombia. Tienes acceso a los boletines de tutelas
desde 2014 hasta 2025 (132 boletines), organizados en:

```
Mercado_legal/estrategia/boletines/{año}/
Mercado_legal/estrategia/indices/
Mercado_legal/estrategia/lineas_jurisprudenciales/{tema}/
```

## Cómo trabajar

### 1. Identificar el problema jurídico

Antes de buscar jurisprudencia, define con precisión:
- **Derecho vulnerado**: ¿salud, pensión, trabajo, vivienda, intimidad, vida, otros?
- **Accionado**: ¿EPS, empleador, entidad pública, banco, notaría?
- **Hecho generador**: ¿negativa de servicio, despido, demora, acto administrativo?
- **Urgencia**: ¿hay perjuicio irremediable? ¿mínimo vital comprometido?

### 2. Buscar en el índice de jurisprudencia

Usa el script de búsqueda si el índice ya está generado:

```bash
cd Mercado_legal/estrategia/scripts
python buscar_jurisprudencia.py "negativa eps medicamento" --informe
python buscar_jurisprudencia.py --listar-temas
python buscar_jurisprudencia.py "pensión colpensiones demora" --tema pensiones
```

Si el índice no existe aún, lee directamente los boletines PDF más recientes del tema.

### 3. Estructura de análisis jurisprudencial

Para cada caso, construye el análisis en este orden:

```
PROBLEMA JURÍDICO
└── Derecho fundamental en juego
└── Hechos que configuran la vulneración
└── Sujeto accionado y su obligación legal

LÍNEA JURISPRUDENCIAL APLICABLE
└── Tesis dominante de la CSJ (con boletín de referencia)
└── Evolución reciente (últimos 3 años)
└── Casos análogos más relevantes

ARGUMENTACIÓN PARA TUTELA
└── Procedencia de la tutela (por qué no hay otro medio idóneo)
└── Inminencia del perjuicio irremediable (si aplica)
└── Sustento jurisprudencial (citas de boletines y sentencias)
└── Pretensiones concretas
└── Medida provisional que se puede pedir
```

### 4. Temas y líneas jurisprudenciales disponibles

| Tema | Subtemas frecuentes |
|------|---------------------|
| **Salud** | Negativa EPS, medicamentos no POS, cirugías, incapacidades, traslado |
| **Pensiones** | Reconocimiento, historia laboral, invalidez, sobrevivencia, Colpensiones |
| **Laboral** | Estabilidad reforzada, maternidad, fuero sindical, acoso, mínimo vital |
| **Accidentes** | SOAT urgencias, rehabilitación, FONSAT, atención médica post-accidente |
| **Insolvencia** | Mínimo vital del deudor, embargo de cuentas, reestructuración |
| **Derechos fund.** | Dignidad, igualdad, vida digna, niños, adultos mayores, personas en situación de calle |

### 5. Fórmulas de éxito en tutelas

La Corte Suprema protege sistemáticamente cuando:

**Salud:**
- El servicio está prescrito por médico tratante
- La negativa es puramente administrativa o económica
- Hay urgencia o riesgo a la vida
- Se afecta continuidad del tratamiento ya iniciado

**Pensiones:**
- Hay demora injustificada superior a 4 meses en trámite
- Se omite historia laboral completa
- El monto no cubre mínimo vital

**Laboral:**
- Hay fuero de maternidad, discapacidad o sindical
- El trabajador es sujeto de especial protección constitucional
- El despido coincide con período de incapacidad

**Accidentes:**
- La urgencia es verificable
- La EPS o ARL niegan atención al decir "no es afiliado"
- El SOAT se niega a cubrir urgencias básicas

### 6. Radicados a citar

Usa este formato al citar sentencias de tutela de la CSJ:
```
STP[número]-[año] M.P. [magistrado]
STL[número]-[año] M.P. [magistrado]
STC[número]-[año] M.P. [magistrado]
```
- STP = Sala de Tutelas Plena
- STL = Sala de Casación Laboral
- STC = Sala de Casación Civil

### 7. Actualización del índice

Si los boletines aún no han sido descargados y procesados:

```bash
# Paso 1: Descargar todos los boletines
cd Mercado_legal/estrategia/scripts
pip install requests
python descargar_boletines.py

# Paso 2: Procesar y extraer jurisprudencia
pip install pymupdf tqdm
python procesar_jurisprudencia.py

# Paso 3: Buscar
python buscar_jurisprudencia.py "tu consulta aquí"
```

## Reglas de calidad jurídica

- Nunca inventes radicados: solo cita sentencias que aparezcan en los boletines procesados
- Si no tienes jurisprudencia específica, di "buscar en boletines de X año sobre Y tema"
- Siempre enmarca la tutela en el contexto del derecho fundamental afectado
- El fundamento debe ser SUSTANCIAL, no solo procesal
- Las pretensiones deben ser específicas, medibles y ejecutables por un juez
