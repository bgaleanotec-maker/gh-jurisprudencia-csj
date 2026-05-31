# gh-wa-brain-tuning

Ajustar el cerebro orquestador IA (María Camila) que atiende WhatsApp del despacho.

## Cuándo invocarlo

- "El bot de WhatsApp respondió mal", "se quedó pegado", "no entendió", "respondió fuera de tema"
- Cambiar identidad / tono / nombre del asistente
- Modificar prompt de Gemini
- Ajustar reglas de transición de estado de lead
- Agregar/quitar verticales que María Camila maneja
- Modificar flujo de agendamiento (validación de slots, cierre real)
- Anti-ban: ajustar tiempos de typing, pausas, segmentación

## Arquitectura del cerebro

```
WhatsApp → Evolution webhook → /wa/evolution/webhook (app/wa_inbound.py)
         → lock por phone (anti race condition)
         → marca leído (✓✓ azul)
         → pausa pre-pensar (1-2.5s)
         → wa_brain.procesar_mensaje_entrante (Gemini)
              ├── consulta disponibilidad real (wa_disponibilidad)
              ├── construye prompt dinámico con cfg de wa_config
              ├── Gemini devuelve JSON con respuestas, intención, slot
              └── valida slot contra disponibilidad real
         → si slot confirmado → wa_disponibilidad.agendar_slot
              ├── valida atomicidad
              ├── elige abogado real
              ├── crea lead + appointment
              └── reemplaza respuesta con confirmación REAL
         → guarda outbound OPTIMISTA en BD (antes de enviar)
         → enviar_texto con presence "composing" humano
         → loggea cada paso
```

## Archivos clave

| Archivo | Responsabilidad |
|---|---|
| `app/wa_brain.py` | Prompt + Gemini + validación slot + fallback |
| `app/wa_inbound.py` | Webhook + lock por phone + envío humanizado + persistencia |
| `app/wa_disponibilidad.py` | Cálculo de slots + creación de appointment + anti-doble-booking |
| `app/wa_mode.py` | Decisión IA / humano / híbrido según hora + estado lead |
| `app/db.py` `wa_config` | 28+ keys configurables: identidad, tono, horario, mensajes, servicios |
| `app/ui.py` `admin_wa_html()` | UI en `/admin/wa` con 8 tabs configurables sin redeploy |

## Identidad actual (configurable en `/admin/wa`)

```python
asistente_nombre   = "María Camila"
asistente_cargo    = "asistente del despacho Galeano Herrera Abogados"
asistente_genero   = "femenino"  # afecta concordancia gramatical
tono               = "cercano"    # cercano | formal | tecnico
despacho_nombre    = "Galeano Herrera Abogados"
ciudad_principal   = "Bogotá"
```

Todo se puede cambiar en caliente desde el admin → el prompt se rearma en el próximo turno.

## Reglas absolutas del prompt

María Camila NUNCA debe:
- Decir "soy IA", "modelo de lenguaje", "asistente virtual", "estoy programada"
- Inventar sentencias o cifras (solo cita del catálogo RAG)
- Prometer resultados ("vas a ganar", "te darán $X")
- Pedir cédula sin explicar el porqué
- Proponer cita sin verificar disponibilidad real
- Mencionar el nombre del abogado antes de que el sistema lo confirme

Si Gemini se desliza, hay **red de seguridad de sanitización por regex** en `_sanitizar_respuesta()`.

## Estados del lead (transiciones controladas)

```
lead_nuevo ─▶ lead_calificado ─▶ lead_agendado ─▶ cliente ─▶ cliente_activo
                                                              │
                                                              ▼
                                                          ganado / perdido
```

Solo Gemini puede sugerir transición, pero `wa_brain` valida que sea legal usando `TRANSICIONES_OK`.

## Anti-ban (humanización)

Configurable en `/admin/wa` → tab "Anti-ban":
- `typing_min_ms` 1400 — mínimo "escribiendo..."
- `typing_max_ms` 11000 — máximo
- `typing_per_word_ms` 230 — escalado por largo
- `pre_thinking_min_ms` 1000 / `pre_thinking_max_ms` 2500 — pausa antes de procesar
- `max_segmentos_por_turno` 3 — máximo mensajes consecutivos

Cada delay tiene ±20% jitter automático para evitar patrones mecánicos.

## Cómo modificar el prompt

1. Edita `PROMPT_TEMPLATE` en `app/wa_brain.py`
2. Mantén los placeholders entre `{}` que recibe `_build_prompt()`:
   ```
   {asistente_nombre} {asistente_cargo} {tono_descriptor} {genero_a}
   {articulo_indef} {ciudad_principal} {modo} {estado} {vertical}
   {datos_capturados_json} {servicios_block} {cita_duracion_min}
   {cita_modalidad} {cita_costo} {office_days_str} {office_hours_start}
   {office_hours_end} {timezone} {disponibilidad_block} {history_block} {text}
   ```
3. Mantén el formato JSON de salida (intencion + datos + respuestas + escalar + slot_iso_confirmado)
4. Smoke test:
   ```python
   from app import wa_brain, db
   db.init_db(); db._migrate()
   conv = db.wa_conv_get_or_create('573050099001')
   r = wa_brain.procesar_mensaje_entrante(conv, 0, 'hola', kind='text')
   print(r)
   ```

## Cómo apagar la IA en emergencia

Desde `/admin/wa` → tab "Modo y horario" → "Circuito de emergencia" → **IA APAGADA (todo a humano)** → Guardar. Sin redeploy.

## Cómo cambiar el modo global

`/admin/wa` → tab "Modo y horario":
- **Híbrido (default):** IA atiende lead_nuevo/calificado/agendado; humano toma cliente activo
- **Solo IA:** María atiende todo
- **Solo humano:** María calla, equipo atiende

## Diagnóstico cuando algo falla

1. **`curl /wa/health`** — chequea Gemini key, Evolution key, modo, IA on/off
2. **`/api/admin/wa/conversations`** — ver últimas convs, estado, datos capturados
3. **`/api/admin/wa/conversations/{id}`** — historial completo de una conv
4. **Render logs** — buscar `[wa]` para ver pipeline detallado (INBOUND, BRAIN-IN, BRAIN-OUT, OUT, DONE)
