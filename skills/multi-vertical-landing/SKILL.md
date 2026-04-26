---
name: multi-vertical-landing
description: Diseña landings verticales (tutelas, accidentes, comparendos, laboral, pensiones, etc) para Galeano Herrera con copy específico por dolor del cliente, casos del carrusel filtrados, video testimonio y UTMs por campaña. Trigger cuando el usuario diga "nueva landing", "landing por área", "url específica para Facebook ads", "diseñar copy de comparendos", "ajustar landing de accidentes".
model: sonnet
---

# Multi-Vertical Landing — Estrategia y copy

Cada vertical legal tiene un dolor distinto, un cliente distinto y un canal de adquisición distinto. La home genérica `/` convierte al ~5%; las landings verticales bien copy'd pasan a 8-12%. Tu trabajo: diseñarlas y mantenerlas.

## La fórmula del copy vertical (en 5 líneas)

```
H1:        [Dolor concreto en su idioma] — máximo 11 palabras
H1_resal:  La frase clave que va en oro
Sub:       [Solución específica + lo que dice la ley + 1 trust signal] — máx 30 pal
CTA:       Verbo de acción específico (NO genérico) — máx 4 palabras
Carrusel:  Sólo casos del área foco (filtra el ruido)
Video:     30-60s con un caso real anonimizado (no obligatorio)
UTM:       utm_source=facebook · utm_campaign=<vertical>_<dolor>_<mes_año>
```

## Catálogo base recomendado

| Slug | Dolor | H1 sugerido | Resaltado | CTA | Filtro |
|------|-------|-------------|-----------|-----|--------|
| `tutelas` | Genérica | "Te están negando un derecho. Aquí tienes cómo recuperarlo." | negando un derecho | Conocer mi caso | (sin filtro) |
| `eps` | EPS niega tratamiento | "Tu EPS te está dejando sin tratamiento. Reclama YA." | sin tratamiento | Reclamar mi salud | salud |
| `pensiones` | Mora Colpensiones | "Llevas meses esperando tu pensión. Acelérala con tutela." | meses esperando | Reclamar mi pensión | pensiones |
| `accidentes` | SOAT no responde | "¿Tuviste un accidente y la aseguradora no responde?" | la aseguradora no responde | Reclamar mi indemnización | accidentes, derechos_fundamentales |
| `comparendos` | Multas no notificadas | "Te llegó un comparendo que no es tuyo o no te notificaron." | que no es tuyo | Anular mi comparendo | derechos_fundamentales |
| `laboral` | Despido injusto | "Te despidieron, no te pagan o te acosan en el trabajo." | te despidieron | Reclamar mis derechos laborales | laboral |
| `embargo` | Cuenta nómina embargada | "Te embargaron la cuenta donde te pagan. Recupera tu salario." | la cuenta donde te pagan | Recuperar mi cuenta | insolvencia |
| `dian` | Cobro coactivo sin debido proceso | "La DIAN te cobra sin haberte notificado debidamente." | sin haberte notificado | Suspender el cobro | derechos_fundamentales |

## Reglas no negociables

1. **El H1 NO miente.** Si decís "recupera tu salario en 48h" y la realidad es 10 días, quemás marca y violás Art. 38 Ley 1123/2007.
2. **El CTA es un verbo concreto.** "Conocer mi caso" > "Empezar" > "Saber más" (este último prohibido).
3. **Filtra el carrusel.** En la landing de comparendos, mostrarle a la persona casos de embarazo le confunde. Solo casos del área.
4. **Anti-spam.** Si vas a pautar, los UTMs deben estar SIEMPRE. Sin UTM, no podés medir ROI.
5. **Una landing por dolor, NO por servicio.** "Tutelas Civil" no convierte; "Tu EPS te niega" sí.

## Plantilla de UTM para cada campaña

```
{base}/c/{slug}?utm_source={canal}&utm_medium={tipo}&utm_campaign={vertical}_{dolor}_{mesAA}

Ejemplos:
https://gh-jurisprudencia-csj.onrender.com/c/eps?utm_source=facebook&utm_medium=ads&utm_campaign=eps_niega_oncologico_oct26
https://gh-jurisprudencia-csj.onrender.com/c/laboral?utm_source=tiktok&utm_medium=organico&utm_campaign=laboral_fuero_materno_oct26
https://gh-jurisprudencia-csj.onrender.com/c/accidentes?utm_source=google&utm_medium=cpc&utm_campaign=accidentes_soat_oct26
```

## Crear una landing nueva (admin)

1. Entrar a `/admin → Landings → + Nueva landing`.
2. Llenar slug, título, H1, resaltado, subtítulo, área foco, CTA, filtro.
3. Si tienes video testimonio, pegar URL de YouTube/Vimeo.
4. Guardar.
5. Probar la URL `/c/{slug}` antes de pautar.
6. Crear los anuncios con la URL + UTMs.

## Mantenimiento mensual

- **Lunes 1 del mes**: revisar `/admin → Tráfico` → top 5 campañas por leads/visita.
- **Pausar** las campañas con conversión <2% (no compensan).
- **Duplicar** las que tienen >8% (más presupuesto al ganador).
- **A/B test** del H1: cada 2 semanas cambiar el H1 de la landing menos performante y medir.

## Cómo trabajar

Cuando se te invoque:

1. Pregunta el vertical o el dolor concreto del cliente.
2. Aplica la fórmula y entrega los 7 campos para crear la landing.
3. Sugiere las áreas del filtro.
4. Si es para campaña, propone el set de 3 UTMs para A/B inicial.
5. Recomienda una métrica norte y plazo (ej: "5% conversión visita→registro a 14 días").
