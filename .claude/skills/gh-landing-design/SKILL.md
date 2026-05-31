# gh-landing-design

Sistema visual y de conversión para las landings públicas de **Galeano Herrera | Abogados** (despacho jurídico colombiano con IA).

## Cuándo invocarlo

- Crear o modificar una landing `/c/{slug}` o `/preview/{slug}` (archivo `app/ui_v2.py`).
- Cuando el usuario dice: "rediseña la landing", "ajusta el copy del hero", "mejora la conversión", "el diseño se ve viejo".
- Crear un nuevo vertical (úsalo en combinación con `gh-vertical-launch`).
- Auditar un anti-patrón visual o de copy en cualquier página pública.

## Dirección visual aprobada: *"Lujo institucional cercano"*

Validada con el usuario el 5 may 2026. NO cambiar sin reconfirmar.

### Paleta (variables CSS en `ui_v2.py`)

```css
--ac:  #C5A059      /* acento principal, oro institucional */
--ac-d color-mix(in srgb, var(--ac) 75%, #000)   /* hover/active */
--ac-s color-mix(in srgb, var(--ac) 12%, white)  /* fondos suaves */
--n:   #0A0A0A      /* texto alto contraste */
--g9:  #1F1F1F      /* texto secundario */
--g7:  #4A4A4A
--g5:  #7B7B7B      /* labels / hints */
--g2:  #E8E8E8      /* bordes */
--g1:  #F4F4F2
--g0:  #FAFAF8      /* fondos card */
--ad:  #0F1E33      /* footer institucional */
--ok:  #16A34A      /* éxito */
--wa:  #25D366      /* WhatsApp */
```

Verticales sobrescriben `--ac` desde `cfg.color_acento` (oro tutelas, naranja accidentes, rojo comparendos, morado laboral).

### Tipografía
- **Display (h1, h2 grandes, testimonios):** Fraunces (Google Fonts) — serif moderna con personalidad institucional, evita el "Times New Roman aburrido"
- **Body:** Inter — estándar SaaS 2024
- **Mono (números de sentencia, IDs):** JetBrains Mono

### Espaciado y radios
- Bordes redondeados confiados: `r1=10px`, `r2=14px`, `r3=20px`, `r4=28px`, `rf=999px` (pill)
- Padding sección: 80-96px verticales, 24px horizontal mobile
- Whitespace generoso: dejar respirar

### Sombras (sutiles, multinivel)
- `sh1` cards en reposo
- `sh2` cards elevadas
- `sh3` hover lift
- `sh4` form principal
- `shg` glow oro para CTAs primarios al hover

### Microinteracciones
- `tr-fast` 120ms · `tr` 180ms · cubic-bezier(.4,0,.2,1)
- Hover en cards: `translateY(-4px)` + shadow stronger + border-color
- Focus states: `box-shadow: 0 0 0 3px var(--ac-s)` (oro suave)

## Estructura de la landing (orden de conversión validado)

Orden obligatorio (research MKT Colombia + Cialdini):

1. **Nav glass blur** con brand + microcopy "María te lee · 5 min" + CTA pill negro
2. **Hero**: eyebrow chip + h1 con DOLOR específico (no producto) + sub + CTA dual (primario oro + verde WhatsApp) + microcopy verde pulsante + stats bar elevada
3. **Selector de 4 casos** (SOLO si SLUG vacío) — reduce parálisis
4. **Casos resueltos** — grid cards con icono oro-soft + chip mono de sentencia
5. **Cómo funciona** — 3 pasos con contador 01/02/03 Fraunces oro
6. **Testimonios** — 3 con avatar inicial + nombre + ciudad + caso (Carmen R. — Soacha · Tutela vs EPS)
7. **Precios transparentes** — 3 tiers (gratis / 49k destacado / 290k+) — anti-objeción "consulta gratis es trampa"
8. **Form** — micropasos: datos básicos → caso → cédula AL FINAL con explicación del porqué + candado verde
9. **Trust signals** — T.P., NIT, SIC, Ley 1581
10. **FAQ** — objeciones reales: "¿es realmente gratis?", "¿es legal usar IA?", "¿mi caso es muy raro?"
11. **Footer institucional** azul deep con NIT/TP/SIC

Siempre con **FAB WhatsApp sticky** abajo-derecha.

## Reglas de copy (psicología MKT Colombia)

### H1 hero — DOLOR específico por vertical, NO producto

```
✓ "Tu EPS te niega lo que necesitas. Radicamos tu tutela esta semana."
✗ "Soluciones jurídicas integrales con tecnología de punta."
```

### CTA primario — verbo + posesivo + escala baja

```
✓ "Empezar mi tutela (gratis)"
✓ "Generar mi borrador →"
✗ "Solicitar más información"
✗ "Enviar"
```

### Microcopy en form
- Hint en WhatsApp: "Te escribimos por aquí, no spammeamos"
- Hint en cédula: "Tu cédula NUNCA aparece en publicidad ni se vende. Solo va en el encabezado de tu documento legal" + icono candado verde
- Consent: una sola línea con link a Política, no doble checkbox

### Microcopy post-envío
```
✓ "Listo, Carmen. Un abogado real revisa tu caso en menos de 2 horas."
✗ "Gracias por contactarnos. Pronto nos comunicaremos."
```

### Lenguaje del cliente (estrato 2-3 colombiano)
- "te están negando" (no "vulneración del derecho")
- "lo que necesitas" (no "el tratamiento médicamente requerido")
- "tu cédula" (no "su documento de identidad")

## Anti-patrones que matan conversión en Colombia jurídico

NO USAR JAMÁS:

1. ❌ Stock de abogado gringo con martillo y balanza (es meme USA, no colombiano)
2. ❌ "Soluciones jurídicas integrales", "vulneración del derecho fundamental", "expertos en derecho"
3. ❌ "Consulta gratis" sin precio visible después → grito de "trampa"
4. ❌ Cédula al inicio del form → -60% conversión
5. ❌ Chatbot que se abre solo a los 3 segundos
6. ❌ WhatsApp escondido (debe estar en nav, hero, footer y FAB sticky)
7. ❌ Footer sin NIT/T.P. → señal de fraude en Colombia
8. ❌ Logos de empresas que el visitante no reconoce
9. ❌ Hero solo-tech sin emoción (somos consumer, no B2B dev)
10. ❌ Más de 3 CTAs visibles arriba del fold

## Trust signals que SÍ funcionan en Colombia

- **T.P. visible** del abogado responsable + link al Consejo Superior de la Judicatura
- **NIT + dirección física + teléfono fijo** en footer
- **Mención SIC + Ley 1581** en cumplimiento
- **Sentencias reales anonimizadas** ("Caso T-2024-XXXX, EPS Sanitas, fallada a favor en 7 días")
- **Logo de medios donde han salido** (Semana, El Tiempo, La FM) si aplica

## Cómo aplicar este skill (workflow)

1. **Lee** `app/ui_v2.py` actual y `app/ui.py` `landing_html()` (para no perder lógica)
2. **Identifica** qué sección quieres modificar:
   - Hero copy / dolor por vertical: edita `_COPY_VERTICAL` (dict por slug)
   - Paleta: edita `:root` variables CSS
   - Estructura: localiza la sección por comentario `<!-- HERO -->`, `<!-- TESTIMONIOS -->`, etc.
3. **Mantén** el sistema de variables CSS — NO uses hex hardcoded
4. **Smoke test** local antes de push:
   ```bash
   python -c "from app import ui_v2; from app import db; \
              db.init_db(); print(len(ui_v2.landing_v2_html(db.get_landing_by_slug('tutelas'))))"
   ```
5. **Endpoint preview** sigue siendo `/preview/{slug}` (NO romper `/c/{slug}` actual sin validación del usuario)
6. **Push y deploy**, verificar HTTP 200 con `curl /preview/tutelas`

## Archivos clave

| Archivo | Función |
|---|---|
| `app/ui_v2.py` | Landing v3 actual (la que toca modificar) |
| `app/ui.py` líneas 10-1350 | Landing v1 legacy (NO modificar todavía) |
| `app/main.py` `/preview/{slug}` | Endpoint preview |
| `app/main.py` `/c/{slug}` | Endpoint producción |
| `app/db.py` `landings` table | Config por vertical (color, icon, casos, etc.) |
