---
name: color-theory-legal
description: Teoría del color aplicada a conversión en servicios legales colombianos. Define paletas por vertical (salud/laboral/pensiones), jerarquía visual, accesibilidad WCAG AA y efectos emocionales medibles. Trigger cuando el usuario diga "ajustar colores", "la landing se ve fría", "CTA no resalta", "revisa accesibilidad", "paleta para campaña X".
model: sonnet
---

# Color Theory — Servicios legales

El color es emoción antes que estética. En legal, mal color = cliente no confía, no importa qué diga el copy.

## Paleta Galeano Herrera (ya implementada)

| Rol | Color | HEX | Uso |
|-----|-------|-----|-----|
| Primario | Azul profundo | `#002347` | Fondo hero, headers, CTA secundario |
| Secundario | Azul hover | `#003f7a` | Hover states, links |
| Acento | Oro | `#C5A059` | Resaltados puntuales, bordes premium |
| Éxito | Verde | `#16a34a` | CTA principal de acción positiva |
| Alerta | Rojo | `#c8102e` | Disclaimers, errores |
| Fondo claro | Gris | `#f6f8fb` | Secciones alternas |
| Texto | Grafito | `#1a2332` | Cuerpo de texto |

## Psicología del color en legal

### Azul profundo → CONFIANZA + AUTORIDAD
Bancos, corporativas, gobierno y firmas serias lo usan. Transmite solidez. **Base obligatoria** de cualquier sitio legal premium.

- Donde funciona: headers, encabezados, iconos de autoridad, CTAs secundarios.
- Donde falla: CTA primario (azul es "pensar" — el CTA necesita "actuar" = verde).

### Oro / dorado → PRESTIGIO + ESCASEZ
Premium, exclusivo, "ganador". **Usar con cuentagotas** (≤ 5% de la pantalla).

- Donde funciona: bordes sutiles, underlines de palabras clave en H1, separadores.
- Donde falla: si lo usas en mucha superficie, pierde el poder de escasez.

### Verde → ACCIÓN + ÉXITO
El cerebro lee verde como "avanza", "confirma", "ganas". En legal es el color perfecto para el CTA principal "Conocer mi caso".

- Donde funciona: botón primario arriba del fold, indicadores de "disponible", banderitas de éxito en pasos completados.
- Donde falla: sobre fondos saturados pierde contraste.

### Rojo → URGENCIA + ALERTA
Peligro, STOP. En legal colombiano hay que cuidarlo — exceso de rojo parece telemarketing.

- Donde funciona: disclaimers obligatorios, errores de validación, icono de aviso.
- Donde falla: CTAs principales (genera ansiedad → abandono).

### Blanco → CLARIDAD + RESPIRO
Es el color más importante y el más olvidado. El espacio blanco **aumenta conversión** porque reduce carga cognitiva.

- Cada sección debe tener ≥ 30% de blanco.
- Entre H1 y el párrafo siguiente: mínimo 16 px.

## Jerarquía visual por impacto

| Nivel | Elemento | Color de fondo | Color de texto |
|-------|----------|---------------|----------------|
| 1 (más fuerza) | CTA primario | Verde `#16a34a` | Blanco |
| 2 | CTA secundario | Azul `#002347` | Blanco |
| 3 | Hero background | Azul `#002347` | Blanco |
| 4 | Cards / secciones | Blanco | Azul |
| 5 | Texto cuerpo | Blanco | Grafito |
| 6 | Badges / tags | Azul claro `#e3f0ff` | Azul oscuro |

**Regla:** nunca más de 2 colores "gritando" en la misma vista. Si CTA es verde y hay un rojo de error, lo demás tiene que ser plano.

## Conversión por vertical legal

Cada área legal tiene emociones distintas. Ajusta el acento:

| Área | Emoción dominante | Acento recomendado |
|------|-------------------|--------------------|
| Salud | Miedo + urgencia | Verde CTA + azul (protección) |
| Laboral | Indignación | Oro (reivindicación, prestigio) |
| Pensiones | Paciencia + trascendencia | Azul profundo + oro |
| Accidentes | Pánico | Verde (salida) + rojo mínimo |
| Insolvencia | Vergüenza | Azul claro (discreción) |
| Derechos fundamentales | Impotencia | Verde CTA (empoderamiento) |

## Accesibilidad WCAG AA (no opcional)

Contraste mínimo para texto:

- Texto normal: 4.5:1
- Texto grande (>18 px bold, >24 px normal): 3:1

Nuestras combinaciones validadas:

| Fondo | Texto | Ratio | OK? |
|-------|-------|-------|-----|
| Azul `#002347` | Blanco | 14.77 | ✅ |
| Oro `#C5A059` | Blanco | 2.39 | ❌ solo para >24px |
| Oro `#C5A059` | Azul `#002347` | 6.17 | ✅ |
| Verde `#16a34a` | Blanco | 3.36 | ✅ para grande |
| Gris `#f6f8fb` | Grafito `#1a2332` | 14.08 | ✅ |

**Regla:** sobre oro, solo texto azul (no blanco).

## Paletas para campañas (Facebook/Google Ads)

### Campaña "EPS te niega"
- Fondo: blanco limpio
- Acento: verde CTA (salida, solución)
- Texto principal: grafito
- Urgencia mínima: banda de oro delgada arriba con "Ley 1751 respalda tu derecho"

### Campaña "Despido en embarazo"
- Fondo: azul profundo hero
- Imagen: silueta de mamá con bebé (no foto stock genérica)
- CTA: oro sobre azul (respeto + prestigio)

### Campaña "Pensión demorada"
- Fondo: azul clásico
- Imagen: manos de adulto mayor + manos jóvenes (trascendencia)
- CTA: verde (avance después de mucha espera)

## Micro-interacciones de color

- Botón primario en reposo: verde `#16a34a`.
- Hover: `#15803d` (oscurece 10%).
- Active / pressed: `#14532d` (oscurece 20%).
- Disabled: gris `#9ca3af` con cursor `not-allowed`.
- Focus ring: oro `#C5A059` con outline 2px → accesibilidad + marca.

## Antipatrones cromáticos

- ❌ Botones con gradiente arcoiris — luce SaaS genérico
- ❌ Rojo en más del 3% de la pantalla — parece spam
- ❌ 3+ colores saturados en la misma vista — distrae
- ❌ Texto blanco sobre oro — ilegible
- ❌ Fondos oscuros en formularios largos — cansa visualmente

## Cómo trabajar

Cuando se te invoque:

1. Identifica la pantalla/sección a revisar.
2. Valida contraste WCAG (usa el mini-table arriba).
3. Identifica el CTA primario y confirma que es **verde**.
4. Revisa que el oro ocupe ≤ 5% de la superficie.
5. Entrega: snippet CSS con los cambios + razón emocional de cada uno.
