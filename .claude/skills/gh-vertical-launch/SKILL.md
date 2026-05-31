# gh-vertical-launch

Lanzar un nuevo vertical jurídico end-to-end (landing + motor RAG + María Camila + agendamiento).

## Cuándo invocarlo

- "Quiero agregar pensiones" / "Lanzar un nuevo vertical" / "Crear landing para X"
- Cuando el usuario detecta un nicho con demanda recurrente y quiere atenderlo con un producto vertical único.

## Pre-requisito: cada vertical es un PRODUCTO ÚNICO

NO es la misma landing con un H1 cambiado. Tiene:
- Identidad visual propia (color accent, hero icon, tono)
- Motor RAG propio (prompt template específico, filtro estricto de área)
- Casos curados específicos (no derivados del catálogo genérico)
- FAQ específico
- Pretensiones tipo, pruebas sugeridas, argumento de medida provisional
- Copy en `_COPY_VERTICAL` (dolor + promesa propios)

Ver skill global `vertical-rag-tuning` para detalles del motor RAG.

## Workflow paso a paso

### 1. Define la identidad visual

Escoge:
- **Color accent** hex (ej. `#7c3aed` morado, `#0EA5E9` azul agua, etc.)
- **Hero icon** emoji (un solo emoji con personalidad)
- **Tono** del prompt (cercano / formal / técnico)

### 2. Define el dolor reconocido y la promesa

Edita `_COPY_VERTICAL` en `app/ui_v2.py`:

```python
"pensiones": {
    "eyebrow": "Pensión de vejez / invalidez / sobrevivientes · Colpensiones",
    "dolor": "Colpensiones lleva años sin reconocer",
    "dolor_acento": "tu pensión",
    "promesa": "La reclamamos por ti.",
    "sub": "Mora administrativa, negativa injustificada, semanas no contadas. Tutela + acción ordinaria si necesario.",
    "cta": "Reclamar mi pensión (gratis)",
    "wa_msg": "Hola, Colpensiones no me reconoce mi pensión y necesito ayuda",
},
```

### 3. Crea la landing en BD

Agrega entrada al seed `_vertical_seeds()` en `app/db.py`:

```python
{
    "slug": "pensiones",
    "title": "Reclamación de pensión · Galeano Herrera",
    "h1": "Colpensiones lleva años sin reconocer tu pensión.",
    "h1_resaltado": "sin reconocer tu pensión",
    "subtitulo": "...",
    "area_focus": "seguridad_social",
    "casos_filtro": ["seguridad_social"],
    "cta_texto": "Reclamar mi pensión",
    "color_acento": "#0EA5E9",
    "hero_icon": "👴",
    "tone": "explicativo",
    "utm_default": "pensiones-colpensiones",
    "casos_curados": [
        {"ic":"📅","tt":"Mora administrativa","ds":"...", "ej":"T-082/2022","area":"seguridad_social"},
        # ... 3-4 cards más
    ],
    "faq_extra": [
        {"q":"¿Cuánto tarda Colpensiones?","a":"15 días hábiles..."},
        # ...
    ],
    "prompt_template": (
        "Eres asistente jurídico colombiano especializado en SEGURIDAD SOCIAL. "
        "Redacta tutela o derecho de petición según corresponda. "
        "DATOS DEL ACCIONANTE: nombre {{nombre}}, cédula {{cedula}}, ciudad {{ciudad}}. "
        "Accionado: {{accionado}}. Hechos: {{descripcion}}. "
        "JURISPRUDENCIA: {{contexto_juris}}. "
        "ESTRUCTURA: 1) Encabezado 2) Hechos 3) Derechos vulnerados (art. 48 CP) "
        "4) Fundamento (cita 2-3 sentencias del contexto) 5) Pretensiones 6) ..."
    ),
    "pretensiones_template": [
        "Ordenar el reconocimiento y pago de la pensión...",
        # ...
    ],
    "pruebas_sugeridas": "• Copia de la cédula\\n• Historia laboral RUAF\\n• Respuesta de Colpensiones\\n...",
    "medida_provisional_arg": "Existe perjuicio irremediable porque...",
    "stats_custom": [
        {"num":"+150","label":"pensiones reconocidas"},
        # ... 4 stats
    ],
    "trust_block": [
        {"title":"Conocemos Colpensiones","desc":"..."},
        # ... 3 trust items
    ],
    "footer_extra": "Ley 100/1993 · Decreto 758/1990 · Sentencias C-...",
},
```

### 4. Reseed la BD localmente

```bash
python -c "from app import db; db.init_db(); db._migrate(); db.bootstrap_default_lawyer()"
```

### 5. Smoke test

```bash
python -c "
from app import db, ui_v2
cfg = db.get_landing_by_slug('pensiones')
print('Landing creada:', cfg.get('title'))
html = ui_v2.landing_v2_html(cfg)
print(f'HTML rendered: {len(html)} bytes')
"
```

### 6. Verifica que el motor RAG funciona

```bash
python -c "
from app import tutela_lite, db
cfg = db.get_landing_by_slug('pensiones')
r = tutela_lite.generar_borrador(
    descripcion='Llevo 3 años esperando mi pensión de vejez',
    landing_cfg=cfg,
)
print(r[:500])
"
```

Confirma que:
- El borrador tiene la estructura del prompt template específico (no copiado de tutelas genéricas)
- Cita sentencias del área `seguridad_social` (no de otra área)
- Las pretensiones son del template específico

### 7. Asegura abogados con cobertura

El vertical necesita al menos 1 abogado activo con `areas` que incluya `"seguridad_social"` o `"*"`. Si no hay, María Camila escalará todo en lugar de proponer cita.

Desde `/admin` → Abogados → asignar áreas.

### 8. Push + deploy

```bash
git add app/db.py app/ui_v2.py
git commit -m "feat(verticales): nuevo vertical 'pensiones' end-to-end"
git push origin main
```

Espera deploy live, verifica:
- `/c/pensiones` HTTP 200
- `/preview/pensiones` HTTP 200
- Borrador se genera (POST `/api/lead/preview` con slug=pensiones)

### 9. Configura UTM y lanza Facebook Ads

URL con tracking:
```
https://gh-jurisprudencia-csj.onrender.com/c/pensiones?utm_source=facebook&utm_medium=cpc&utm_campaign=pensiones-vejez-may26
```

### 10. WhatsApp: actualiza servicios en config

`/admin/wa` → tab "Servicios" → agregar entrada:
```
Pensiones::reconocimiento por Colpensiones, mora administrativa, sustitución pensional
```

Así María Camila puede mencionarlo cuando un cliente pregunte "¿qué hacen ustedes?".

## Anti-pattern: NO hacer

- ❌ Copiar la landing de tutelas y solo cambiar el H1 → falla la promesa de "producto único"
- ❌ Lanzar sin abogado con cobertura del área → María Camila escala todo
- ❌ Lanzar sin probar el RAG con un caso real
- ❌ Olvidar setear `area_focus` → el RAG busca en todas las áreas y trae ruido
