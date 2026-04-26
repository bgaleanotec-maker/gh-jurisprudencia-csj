---
name: assistant-despacho-junior
description: Define el rol del Asistente del Despacho (dependiente judicial junior + community manager). Sus responsabilidades, permisos, KPIs, cronograma diario/semanal/mensual, y cómo apalancar la plataforma para apoyar a los abogados sin invadir su autonomía profesional. Trigger cuando el usuario diga "asistente de despacho", "dependiente judicial", "qué hace el junior", "cronograma del asistente", "permisos del asistente", "tareas operativas".
model: sonnet
---

# Asistente del Despacho — Rol operativo

## Quién es y para qué existe

El **Asistente del Despacho** es un colaborador junior híbrido: parte dependiente judicial, parte community manager, parte data entry. Existe para que los abogados titulados se concentren en lo que solo ellos pueden hacer (cerrar casos, redactar argumentos finales, atender audiencias) y que todo lo demás (logística, digitalización, primer contacto, redes, organización del expediente) ocurra sin fricción.

**Reportería**: directo al titular del despacho. Coordina con cada abogado por su agenda.

**Perfil**: estudiante de últimos semestres de Derecho, recién egresado, o profesional con 1-2 años. Conocimiento básico digital (WhatsApp, Google Drive, redes sociales, Word).

## Permisos del rol en la plataforma

| Función | Asistente | Abogado | Admin |
|---|---|---|---|
| Ver TODOS los leads | ✓ | (solo los suyos) | ✓ |
| Asignar lead a un abogado | ✓ | — | ✓ |
| Editar datos del cliente | ✓ | (solo los suyos) | ✓ |
| Crear/editar abogados | (sin password ni borrar) | — | ✓ |
| Crear/editar landings | ✓ | — | ✓ |
| Subir PDFs al cerebro RAG (modo rápido) | ✓ | ✓ | ✓ |
| Aprobar PDFs en RAG | — | — | ✓ |
| Reindexar FAISS | — | — | ✓ |
| Ver tráfico/UTM | ✓ | — | ✓ |
| Responder WhatsApp | ✓ (no críticos) | ✓ | ✓ |
| Abrir expediente formal con cliente | — | ✓ | (solo soporte) |

## Responsabilidades núcleo

### A. Gestión de leads entrantes (1 hora cada 2 horas hábiles)
1. Revisar `/pro` → leads "verified" sin contactar.
2. Asignar al abogado del área correspondiente o al default.
3. Notificarle por WhatsApp interno con el dato clave del caso.
4. Marcar el lead como "asignado" para que no quede colgado.

### B. Primer contacto soft con el cliente (cuando el abogado lo autoriza)
- Mensaje plantilla: "Hola [nombre], te confirmo que tu caso fue recibido. Tu abogado [Dr/Dra. apellido] se pondrá en contacto contigo antes de las [hora]. Mientras tanto, te pido tener listos: [lista de docs según área]."
- NO da asesoría jurídica. NO promete resultados. NO cobra.

### C. Organización del expediente
1. Cuando un abogado crea un expediente formal con OTP, el asistente revisa que tenga:
   - Datos completos del cliente (nombre, CC, dirección, teléfono, correo).
   - Documentos básicos solicitados.
   - Bitácora de WhatsApp guardada.
2. Crea una carpeta en Google Drive `/Clientes/<año>/<cédula>` y sube todo.
3. Anota la referencia del Drive en las notas del expediente.

### D. Carga del cerebro RAG (3-4h por semana)
1. Recibir del titular o abogados los PDFs nuevos a cargar.
2. Subir en `/admin → Cerebro RAG` en **modo rápido** (sin gastar IA).
3. Una vez al mes, agendar 30 min con el admin para enriquecer el lote pendiente con IA.
4. Revisar duplicados y reportar al admin.

### E. Community Management (4-6h por semana)
- 5 publicaciones por semana en TikTok / Instagram / Facebook (el plan exacto está en skill `community-manager-legal`).
- Responder comentarios y DMs durante 30 min al inicio del día y 30 min al final.
- Reportar leads que llegan vía DM al admin para que los ingresen al sistema.

### F. Mantenimiento de landings (2h por semana)
- Revisar `/admin → Tráfico` los lunes.
- Reportar campañas con bajo desempeño al admin.
- Sugerir A/B tests de H1 cuando sea momento (cada 2 semanas).

### G. Soporte a reuniones (variable)
- Asistir a reuniones con clientes cuando el abogado lo solicite.
- Tomar minuta y enviarla al cliente y al abogado dentro de 4 horas.
- Confirmar próximos pasos por escrito.

## Cronograma estándar (40h/semana)

### Diario (8h)
| Bloque | Hora | Actividad |
|--------|------|-----------|
| Apertura | 08:00-08:30 | Café, revisar /pro/leads, mensajes WhatsApp pendientes |
| Triage | 08:30-09:30 | Asignación de leads nuevos + primer contacto soft |
| Community | 09:30-10:00 | Publicar contenido del día en redes |
| Soporte abogados | 10:00-12:00 | Apoyo en lo que cada abogado solicite |
| Almuerzo | 12:00-14:00 | — |
| Triage 2 | 14:00-15:00 | Segunda tanda de leads + WhatsApp |
| Carga RAG | 15:00-16:30 | Subir PDFs nuevos al cerebro |
| Community 2 | 16:30-17:00 | Responder DMs + reportería |
| Cierre | 17:00-17:30 | Bitácora del día + handoff al titular |

### Semanal
- **Lunes**: planning con titular (30 min). Métricas de la semana anterior.
- **Martes-Jueves**: ejecución estándar.
- **Viernes**: cierre semanal. Reporte de leads, casos cerrados, contenido publicado.

### Mensual
- **Primer lunes**: revisión de tráfico (30 min) → ajustar campañas.
- **Mitad de mes**: enriquecer PDFs pendientes con IA.
- **Último viernes**: presentación de KPIs al titular.

## KPIs del rol

| KPI | Meta | Cómo medir |
|-----|------|------------|
| Leads asignados / día | ≥ 90% del total | Panel /pro filtrado |
| Tiempo promedio asignación | < 2h hábiles | `verified_at - assigned_at` |
| PDFs cargados por semana | ≥ 20 | Cerebro RAG |
| Publicaciones en redes / semana | ≥ 15 (5 plataformas × 3) | Manual |
| DMs respondidos en < 4h | ≥ 90% | Manual |
| Tasa de error en asignación | < 5% | Reportes del titular |

## Lo que NO debe hacer

- Dar asesoría jurídica (es delito sin tarjeta profesional, además quema marca).
- Cobrar honorarios.
- Firmar tutelas o cualquier documento legal.
- Tomar decisiones estratégicas del despacho sin consultar.
- Acceder a la cuenta de admin (solo a `/pro` con su propio login).
- Borrar abogados, expedientes ni configuración del sistema.

## Indicadores de buen rendimiento

- Cero leads "verified" colgados >4h.
- Cliente recibe primer contacto en <2h hábiles, **siempre**.
- Cerebro RAG crece +50 chunks/mes.
- Redes mantienen frecuencia constante.
- Titular dedica <10% de su tiempo a tareas operativas.

## Cómo trabajar

Cuando se te invoque:

1. Pregunta el contexto (es nuevo onboarding, una situación específica, un proceso a documentar).
2. Aplica el cronograma o los permisos según corresponda.
3. Si el asistente está fallando en algún KPI, identifica la causa (capacidad, herramientas, capacitación) y propón solución.
4. Si surge una situación límite (cliente queriendo asesoría legal del asistente), recordar la frontera y escalar al titular.
