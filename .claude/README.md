# `.claude/` — Skills y agentes del proyecto Galeano Herrera

Esta carpeta contiene **conocimiento operativo** del proyecto que viaja con el repo.

Cuando un agente Claude entra a este workspace, lee estos archivos y sabe cómo:
- Diseñar y modificar las landings sin reinventar el sistema visual cada vez
- Ajustar el cerebro IA de WhatsApp (María Camila) con seguridad
- Lanzar nuevos verticales jurídicos end-to-end
- Mantener el catálogo RAG limpio
- Hacer deploys seguros a Render
- Convocar especialistas (copywriter colombiano, auditor de conversión, revisor de WhatsApp, guardián del sistema visual)

## 📁 Estructura

```
.claude/
├── README.md                                    ← este archivo
├── skills/
│   ├── gh-landing-design/SKILL.md              ← sistema visual + conversión landings
│   ├── gh-wa-brain-tuning/SKILL.md             ← María Camila, prompt, estados
│   ├── gh-vertical-launch/SKILL.md             ← lanzar nuevo vertical end-to-end
│   ├── gh-rag-jurisprudencia/SKILL.md          ← gestión catálogo RAG
│   └── gh-deploy-render/SKILL.md               ← deploy seguro Render
└── agents/
    ├── legal-copywriter-co.md                  ← copy jurídico colombiano cercano
    ├── landing-conversion-auditor.md           ← auditor Cialdini + MKT Colombia
    ├── wa-conversation-reviewer.md             ← revisor conversaciones WhatsApp
    └── design-system-guardian.md               ← guardián consistencia visual
```

## 🎯 Cuándo usar cada uno (cheat sheet)

### Skills (instrucciones cuando el usuario pide algo)

| El usuario dice... | Usa skill |
|---|---|
| "rediseña la landing", "el copy del hero", "mejora la conversión" | `gh-landing-design` |
| "el bot respondió mal", "cambia el nombre del asistente", "ajusta el prompt" | `gh-wa-brain-tuning` |
| "agrega pensiones", "lanza un vertical nuevo", "crea landing para X" | `gh-vertical-launch` |
| "la IA cita una sentencia que no existe", "sube esta sentencia al catálogo" | `gh-rag-jurisprudencia` |
| "verifica el deploy", "algo en producción no funciona", "haz un push seguro" | `gh-deploy-render` |

### Agentes (subagent_type cuando se necesita especialista)

| Necesitas... | Llama agente |
|---|---|
| Copy nuevo (hero, FAQ, CTA, mensaje WA) con voz colombiana | `legal-copywriter-co` |
| Audit de conversión de una landing existente con priorización | `landing-conversion-auditor` |
| Diagnóstico de una conversación de WA real (qué falló) | `wa-conversation-reviewer` |
| Verificar consistencia visual entre pantallas | `design-system-guardian` |

### Ejemplos de invocación de agentes

```python
# Para copy nuevo del hero de un vertical "pensiones"
Agent(
    description="Copy hero pensiones",
    subagent_type="legal-copywriter-co",
    prompt="Necesito 3 opciones de H1+sub para una landing nueva sobre reclamación de pensión por Colpensiones. Audiencia: colombiano clase media/baja, estresado por mora de Colpensiones. Tono: cercano + autoridad. Que el dolor sea reconocible."
)

# Para auditar una landing actual
Agent(
    description="Audit landing tutelas",
    subagent_type="landing-conversion-auditor",
    prompt="Audita https://gh-jurisprudencia-csj.onrender.com/c/tutelas y dame plan de acción priorizado. Especial atención a anti-patrones colombianos."
)

# Para revisar una conversación específica de WA
Agent(
    description="Review conv WA #4",
    subagent_type="wa-conversation-reviewer",
    prompt="Revisa conv id=4 (María Camila se quedó pegada confirmando abogado). Diagnostica root cause y propón fix."
)

# Para verificar coherencia visual del lawyer_dashboard
Agent(
    description="Audit visual dashboard abogado",
    subagent_type="design-system-guardian",
    prompt="Audita app/ui.py lawyer_dashboard_html() (línea 1405). Reporta inconsistencias vs sistema unificado en ui_v2.py y propón plan de migración por fases."
)
```

## 🌐 Contexto del proyecto

**Galeano Herrera | Abogados** es una plataforma jurídica colombiana SaaS que:
- Genera borradores de tutelas con IA + jurisprudencia auditable de la Corte Constitucional
- Atiende WhatsApp con María Camila (asistente IA con identidad humana)
- Gestiona expedientes con firma electrónica (OTP, Ley 527/99)
- 4 verticales: tutelas, accidentes, comparendos, laboral
- Despliegue en Render (plan free actual — sin disk persistente)
- WhatsApp vía Evolution API en VPS Hostinger

URLs principales:
- Producción: https://gh-jurisprudencia-csj.onrender.com
- Admin: `/admin` · Admin WhatsApp: `/admin/wa`
- Landings: `/c/{slug}` y preview en `/preview/{slug}`
- Health WA: `/wa/health`

## 🚀 Quickstart para un agente nuevo en el proyecto

Si acabas de entrar a este workspace:

1. **Lee `app/main.py`** para entender los endpoints
2. **Lee `app/db.py`** para entender el schema
3. **Lee `.claude/skills/gh-landing-design/SKILL.md`** si vas a tocar UI
4. **Lee `.claude/skills/gh-wa-brain-tuning/SKILL.md`** si vas a tocar la IA WA
5. **Lee este archivo (README)** para saber qué skill/agente usar cuando

## 🔒 Reglas de oro

1. **Nunca tocar `/c/{slug}` actual sin validar el cambio en `/preview/{slug}` primero** — los Facebook Ads apuntan a `/c/{slug}` en producción
2. **Nunca borrar fichas del catálogo RAG** — marcar `inactiva=1` para auditoría
3. **Nunca commitear claves** (`GEMINI_API_KEY`, `EVOLUTION_API_KEY`, etc.) — viven solo en Render env vars
4. **María Camila NUNCA dice "soy IA"** — hay regex de sanitización como red de seguridad
5. **Antes de cambiar el prompt de Gemini**, smoke test local con caso conocido
6. **Antes de push a main**, smoke test de imports (`python -c "import app.main"`)
7. **El plan de Render es FREE** — cada deploy borra la BD SQLite. Avisar al usuario si el cambio va a perder datos hasta upgrade.
