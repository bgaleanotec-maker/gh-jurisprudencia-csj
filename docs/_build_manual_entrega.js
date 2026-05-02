// Build script: Manual_Entrega_Galeano_Herrera.docx
// Documento de entrega para usuarios de pruebas (clientes finales,
// abogados y admin). SIN claves API ni secretos.

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, ExternalHyperlink,
  InternalHyperlink, Bookmark, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, TabStopType,
  TabStopPosition, TableOfContents,
} = require("docx");

// ---------- helpers ----------
const ORO = "C5A059";
const NARANJA = "EA580C";
const ROJO = "C8102E";
const MORADO = "7C3AED";
const GRIS = "555555";
const GRIS_BORDE = "CCCCCC";
const GRIS_FONDO = "F4F4F4";

const CONTENT_W = 9360;

const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: GRIS_BORDE };
const cellBorders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
const cellMargins = { top: 100, bottom: 100, left: 140, right: 140 };

function P(text, opts = {}) {
  if (typeof text === "string") {
    return new Paragraph({
      children: [new TextRun({ text, ...opts })],
      spacing: { after: 120, ...(opts.spacing || {}) },
      alignment: opts.alignment,
    });
  }
  return new Paragraph({ children: text, spacing: { after: 120 } });
}

function H(level, text, color) {
  return new Paragraph({
    heading: level,
    children: [new TextRun({ text, color: color || "111111" })],
    spacing: { before: 240, after: 160 },
  });
}

function bullet(text, level = 0, runs = null) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    children: runs || [new TextRun({ text })],
    spacing: { after: 60 },
  });
}

function numbered(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "numbers", level },
    children: [new TextRun({ text })],
    spacing: { after: 60 },
  });
}

function divider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ORO, space: 6 } },
    spacing: { before: 60, after: 200 },
  });
}

function cell(text, opts = {}) {
  const runs = Array.isArray(text)
    ? text.map((t) => new TextRun(typeof t === "string" ? { text: t } : t))
    : [new TextRun(typeof text === "string" ? { text, ...(opts.run || {}) } : text)];
  return new TableCell({
    borders: cellBorders,
    margins: cellMargins,
    width: { size: opts.w || CONTENT_W, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ children: runs, alignment: opts.align })],
  });
}

function header2col(left, right, fill) {
  return new TableRow({
    children: [
      cell(left, { w: 3200, fill, run: { bold: true, color: "FFFFFF" } }),
      cell(right, { w: CONTENT_W - 3200, fill: GRIS_FONDO, run: { bold: true } }),
    ],
  });
}

function row2col(left, right) {
  return new TableRow({
    children: [
      cell(left, { w: 3200, run: { bold: true } }),
      cell(right, { w: CONTENT_W - 3200 }),
    ],
  });
}

function table2col(rows, headerFill = ORO, header = ["Campo", "Valor"]) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [3200, CONTENT_W - 3200],
    rows: [header2col(header[0], header[1], headerFill), ...rows.map(([l, r]) => row2col(l, r))],
  });
}

function table3col(header, rows, fill = ORO) {
  const w1 = 2400, w2 = 3000, w3 = CONTENT_W - w1 - w2;
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [w1, w2, w3],
    rows: [
      new TableRow({
        children: [
          cell(header[0], { w: w1, fill, run: { bold: true, color: "FFFFFF" } }),
          cell(header[1], { w: w2, fill, run: { bold: true, color: "FFFFFF" } }),
          cell(header[2], { w: w3, fill, run: { bold: true, color: "FFFFFF" } }),
        ],
      }),
      ...rows.map((r) =>
        new TableRow({
          children: [
            cell(r[0], { w: w1, run: { bold: true } }),
            cell(r[1], { w: w2 }),
            cell(r[2], { w: w3 }),
          ],
        })
      ),
    ],
  });
}

function link(text, url) {
  return new ExternalHyperlink({
    children: [new TextRun({ text, style: "Hyperlink" })],
    link: url,
  });
}

function callout(title, body, color = ORO) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: [CONTENT_W],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: {
              top: { style: BorderStyle.SINGLE, size: 4, color },
              bottom: { style: BorderStyle.SINGLE, size: 4, color },
              left: { style: BorderStyle.SINGLE, size: 24, color },
              right: { style: BorderStyle.SINGLE, size: 4, color },
            },
            margins: { top: 160, bottom: 160, left: 200, right: 200 },
            width: { size: CONTENT_W, type: WidthType.DXA },
            shading: { fill: GRIS_FONDO, type: ShadingType.CLEAR },
            children: [
              new Paragraph({ children: [new TextRun({ text: title, bold: true, color })], spacing: { after: 80 } }),
              ...(Array.isArray(body) ? body : [body]).map((t) =>
                new Paragraph({ children: [new TextRun({ text: t })], spacing: { after: 60 } })
              ),
            ],
          }),
        ],
      }),
    ],
  });
}

// ---------- contenido ----------
const SITIO = "https://gh-jurisprudencia-csj.onrender.com";

const portada = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 1800, after: 400 },
    children: [new TextRun({ text: "GALEANO HERRERA", bold: true, size: 64, color: ORO })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160 },
    children: [new TextRun({ text: "ABOGADOS", bold: true, size: 32, color: GRIS, characterSpacing: 60 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: ORO, space: 6 } },
    spacing: { before: 120, after: 360 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200 },
    children: [new TextRun({ text: "Manual de entrega · Programa de pruebas", bold: true, size: 36 })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 600 },
    children: [
      new TextRun({
        text: "Plataforma de acciones de tutela y reclamaciones legales con motor RAG sobre jurisprudencia colombiana",
        italics: true, size: 24, color: GRIS,
      }),
    ],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 1200, after: 80 },
    children: [new TextRun({ text: "Versión 1.0 · Programa cerrado de pruebas", size: 20, color: GRIS })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
    children: [new TextRun({ text: "Documento confidencial · Uso exclusivo de probadores autorizados", size: 18, color: GRIS, italics: true })],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

const seccion_indice = [
  H(HeadingLevel.HEADING_1, "Tabla de contenido"),
  new TableOfContents("Tabla de contenido", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [new PageBreak()] }),
];

const seccion_bienvenida = [
  H(HeadingLevel.HEADING_1, "1. Bienvenida"),
  P(
    "Gracias por participar en el programa de pruebas de la plataforma Galeano Herrera | Abogados. " +
    "Este documento es la guía completa para que pruebes todas las funcionalidades, entiendas la propuesta de valor y " +
    "nos ayudes a depurar la experiencia antes de la apertura comercial.",
  ),
  P("Tu rol es central. Lo que reportes en estas semanas decide qué funcionalidades quedan en producción y cuáles ajustamos."),
  callout(
    "¿Qué esperamos de ti como probador?",
    [
      "1) Recorrer al menos 3 de los 4 verticales (tutelas, accidentes, comparendos, laboral).",
      "2) Generar al menos 2 borradores de tutela / reclamación por vertical con casos reales o ficticios.",
      "3) Reportar todo: errores, frases mal redactadas, jurisprudencia que no aplica, falta de claridad, lentitud.",
      "4) Calificar la experiencia (de 1 a 10) al final del programa de pruebas, junto con tus 3 mejoras prioritarias.",
    ],
    ORO,
  ),
  H(HeadingLevel.HEADING_2, "Qué es Galeano Herrera"),
  P(
    "Una plataforma jurídica colombiana que ayuda a personas comunes a redactar acciones de tutela, reclamaciones a aseguradoras, " +
    "impugnaciones de comparendos y reclamos laborales. El motor de inteligencia artificial cita sentencias reales de la Corte " +
    "Constitucional y la Corte Suprema, evitando improvisaciones."
  ),
  P("La diferencia con un \"chatbot legal\" cualquiera:"),
  bullet("Cada vertical (tutelas, accidentes, comparendos, laboral) es un PRODUCTO ÚNICO con su propio motor RAG, su propia jurisprudencia curada y su propia identidad visual."),
  bullet("Toda referencia a sentencias se construye a partir de un catálogo verificable cargado por nosotros, no \"inventado\" por la IA."),
  bullet("El abogado humano interviene en los casos que se convierten en clientes reales: la IA hace el primer 70 %, el abogado el último 30 %."),
  bullet("WhatsApp, agenda nativa, expedientes con firma electrónica (Ley 527/99) y panel de admin para gestionar abogados y leads."),
];

const seccion_visiongeneral = [
  H(HeadingLevel.HEADING_1, "2. Visión general del producto"),
  H(HeadingLevel.HEADING_2, "2.1 Las 4 verticales · cada una es un producto único"),
  P(
    "La plataforma se organiza en 4 \"landings verticales\" (vendedores especializados). Cada uno se ve, suena y razona distinto. " +
    "No son la misma página con cambios cosméticos: cada uno tiene su propio motor RAG con prompt template, área del catálogo, " +
    "casos curados y argumentos de medida provisional específicos."
  ),
  table3col(
    ["Vertical", "Identidad visual", "Especialización"],
    [
      ["Tutelas (genérica)", "⚖️  Color oro #C5A059  ·  tono explicativo", "Salud, pensión, derecho de petición, mínimo vital. Filtra todas las áreas del catálogo."],
      ["Accidentes / SOAT", "🚗  Color naranja #EA580C  ·  tono urgente", "SOAT, indemnización por incapacidad, lucro cesante, vehículo fantasma. Cifras claras en SMDLV."],
      ["Comparendos", "🚦  Color rojo #C8102E  ·  tono reivindicativo", "Fotomultas sin notificación (C-038/2020), cobros coactivos, vehículo vendido. Eje: debido proceso art. 29 CP."],
      ["Laboral", "💼  Color morado #7C3AED  ·  tono reivindicativo", "Fuero materno, fuero de salud, contrato realidad, acoso. Reintegro inmediato y mora art. 65 CST."],
    ],
    ORO
  ),
  P(""),
  H(HeadingLevel.HEADING_2, "2.2 Arquitectura en una página"),
  P("De arriba hacia abajo, el flujo del cliente:"),
  numbered("Llega a una landing pública (/c/tutelas, /c/accidentes, /c/comparendos, /c/laboral)."),
  numbered("Lee el caso curado más parecido al suyo, agenda cita o pulsa \"generar borrador\"."),
  numbered("Llena un formulario corto: nombre, cédula, ciudad, accionado, descripción del caso."),
  numbered("La IA + el motor RAG recuperan jurisprudencia relevante del catálogo y generan un borrador formal."),
  numbered("El cliente puede descargar el borrador, agendar cita o ser contactado vía WhatsApp."),
  numbered("Si decide contratar al abogado, se abre un expediente con OTP de aceptación (firma electrónica Ley 527/99)."),
  numbered("Todas las interacciones quedan auditadas en la base de datos para trazabilidad y cumplimiento."),
];

const seccion_accesos = [
  H(HeadingLevel.HEADING_1, "3. URLs y accesos"),
  callout(
    "Sin credenciales en este documento",
    [
      "Por seguridad este manual no incluye contraseñas, claves API ni accesos al panel de admin.",
      "Las credenciales se entregarán por canal separado a cada probador autorizado.",
      "Si te compartieron este archivo y necesitas accesos, escríbele al administrador del programa.",
    ],
    ROJO
  ),
  P(""),
  H(HeadingLevel.HEADING_2, "3.1 URLs públicas"),
  table2col([
    ["Sitio principal", new TextRun({ text: SITIO, color: "0563C1", underline: { type: "single" } })],
    ["Tutelas (genérica)", `${SITIO}/c/tutelas`],
    ["Accidentes / SOAT", `${SITIO}/c/accidentes`],
    ["Comparendos / fotomultas", `${SITIO}/c/comparendos`],
    ["Reclamaciones laborales", `${SITIO}/c/laboral`],
  ], ORO),
  P(""),
  H(HeadingLevel.HEADING_2, "3.2 Áreas internas (requieren login)"),
  table2col([
    ["Panel de abogado", `${SITIO}/pro/login  ·  panel: ${SITIO}/pro`],
    ["Panel de admin (HTTP Basic Auth)", `${SITIO}/admin`],
    ["Expediente (con OTP)", `${SITIO}/expediente/{token}  ·  el token llega por WhatsApp / correo`],
  ], ORO),
  P(""),
  H(HeadingLevel.HEADING_2, "3.3 Roles disponibles"),
  table3col(
    ["Rol", "Quién", "Qué puede hacer"],
    [
      ["Cliente final", "Cualquier persona en internet", "Visitar landings, generar borradores, agendar cita, recibir su expediente."],
      ["Abogado", "Profesional habilitado por el admin", "Atender leads asignados, ver agenda, abrir y cerrar expedientes, agregar notas internas."],
      ["Asistente de despacho", "Paralegal o practicante junior", "Triaje de leads, agendamiento, cargue de pruebas. NO firma documentos finales."],
      ["Admin", "Galeano Herrera (tú)", "Crea abogados y asistentes, configura landings, sube jurisprudencia, audita la BD."],
    ],
    ORO
  ),
];

// 4 — clientes finales por vertical
function pasoaPaso(numero, slug, color, icono, titulo, narrativa, pretensiones, pruebas) {
  return [
    H(HeadingLevel.HEADING_2, `4.${numero} ${icono} Vertical "${titulo}" — /c/${slug}`),
    P(narrativa),
    H(HeadingLevel.HEADING_3, `Cómo probarlo (paso a paso)`),
    numbered(`Abre ${SITIO}/c/${slug} en el navegador.`),
    numbered("Verifica que la página tenga el ícono y el color correctos (parte superior y botones). Si ves todo en oro genérico, repórtalo: significa que la identidad del vertical no se aplicó."),
    numbered("Lee al menos 2 \"casos más frecuentes\" en el carrusel central. Comprueba que los casos sean específicos del vertical, no genéricos de tutelas."),
    numbered("Pulsa el botón de acción principal (varía por vertical). Llena el formulario con un caso real o realista (puedes inventar el accionado)."),
    numbered("Espera el borrador generado. Revisa: ¿la estructura es la del vertical? ¿cita sentencias del área correcta? ¿hay placeholders [COMPLETAR ...] sin rellenar?"),
    numbered("Descarga el borrador o copia el texto. Compáralo con el de OTRO vertical: deben ser claramente distintos en estructura y argumentación."),
    numbered("(Opcional) Agenda una cita usando el botón \"Agendar cita\". Verifica que el modal abra y muestre disponibilidad de los próximos 7 días."),
    H(HeadingLevel.HEADING_3, "Pretensiones tipo que la IA debería sugerir"),
    ...pretensiones.map((p) => bullet(p)),
    H(HeadingLevel.HEADING_3, "Pruebas que el sistema debería pedir"),
    ...pruebas.map((p) => bullet(p)),
    callout(
      `Bandera roja en ${slug}`,
      [
        `Si el borrador menciona "EPS" cuando hablaste de un accidente de tránsito, o si cita una sentencia laboral en un comparendo, eso es un fallo del filtro de área. Repórtalo con captura.`,
      ],
      color
    ),
    P(""),
  ];
}

const seccion_clientes = [
  H(HeadingLevel.HEADING_1, "4. Guía paso a paso para clientes finales"),
  P("Esta sección está pensada para que la pruebes \"poniéndote los zapatos\" de un cliente real. Recomendamos hacer al menos 2 pasadas por cada vertical: una con un caso simple y otra con un caso complejo."),
  ...pasoaPaso(
    1, "tutelas", ORO, "⚖️", "Tutelas (genérica)",
    "Es el vertical de entrada para casos que no encajan en los otros tres. Salud, pensión, derecho de petición sin respuesta, mínimo vital. Es el más amplio y el que la mayoría de personas conocen como \"tutela\".",
    [
      "Tutelar los derechos fundamentales invocados.",
      "Ordenar al accionado realizar / abstenerse de la conducta vulneradora en plazo no superior a 48 horas.",
      "Compulsar copias a entes de control si hay falla del servicio.",
    ],
    [
      "Copia de la cédula del accionante.",
      "Derecho de petición presentado y constancia de radicado.",
      "Respuesta (o silencio) del accionado.",
      "Historia clínica / formulario de pensión / contrato según aplique.",
    ]
  ),
  ...pasoaPaso(
    2, "accidentes", NARANJA, "🚗", "Accidentes de tránsito · SOAT",
    "Vertical de tono urgente. El cliente típico tuvo un accidente, su EPS o aseguradora se demora, y necesita atención médica o indemnización ya. La IA argumenta con cifras (SMDLV) y normativa específica del SOAT.",
    [
      "Reconocer y pagar la totalidad de los gastos médicos derivados del accidente.",
      "Indemnización por incapacidad temporal o permanente conforme dictamen.",
      "Pagar lucro cesante por días dejados de laborar.",
      "Pagar daño emergente (transporte, medicamentos, terapias).",
      "Reconocer daño moral conforme tasación de la Corte Suprema (Sala Civil).",
    ],
    [
      "Informe Policial de Accidente de Tránsito (IPAT).",
      "FURIPS y FURTRAN (formularios SOAT).",
      "Historia clínica completa y epicrisis.",
      "Dictamen de pérdida de capacidad laboral.",
      "Facturas de gastos médicos no cubiertos.",
    ]
  ),
  ...pasoaPaso(
    3, "comparendos", ROJO, "🚦", "Comparendos y fotomultas",
    "Vertical que ataca el debido proceso (art. 29 CP) cuando una autoridad de tránsito sanciona sin notificar en debida forma. Argumento estrella: C-038/2020, que exige notificación personal en fotomultas.",
    [
      "Declarar la nulidad del comparendo por falta de notificación personal.",
      "Suspender de inmediato el cobro coactivo.",
      "Limpieza del registro SIMIT y reportes negativos asociados.",
      "Levantar medidas cautelares (embargo de cuenta o vehículo).",
    ],
    [
      "Copia del comparendo o fotomulta recibida.",
      "Certificado del SIMIT con detalle del cobro.",
      "Certificado de tradición del vehículo (RUNT).",
      "Si vendiste el carro: contrato de compraventa o traspaso.",
      "Si hubo embargo: oficio y certificación bancaria.",
    ]
  ),
  ...pasoaPaso(
    4, "laboral", MORADO, "💼", "Reclamaciones laborales",
    "Vertical de tono reivindicativo. Cubre fueros (maternidad, salud, sindical, prepensión), contrato realidad, no pago de salarios y acoso laboral (Ley 1010/2006). Cuando hay fuero, propone tutela con reintegro inmediato.",
    [
      "Declarar la ineficacia del despido por violación al fuero.",
      "Ordenar reintegro al cargo o uno de igual o superior categoría.",
      "Pagar salarios y prestaciones dejados de percibir.",
      "Indemnización del art. 64 CST y sanción moratoria del art. 65 CST.",
      "Cotizaciones a salud, pensión y ARL durante el periodo del despido.",
      "Indemnización adicional de 180 días en casos de fuero de salud (Ley 361/97).",
    ],
    [
      "Contrato laboral o constancia de la relación.",
      "Comprobantes de pago de los últimos 6 meses.",
      "Carta de despido o renuncia.",
      "Certificación médica si hay fuero de salud o maternidad.",
      "Constancia de afiliación a EPS y AFP (RUAF).",
      "Si hay acoso: testimonios, comunicaciones, memorandos.",
    ]
  ),
];

const seccion_abogados = [
  H(HeadingLevel.HEADING_1, "5. Guía para abogados"),
  P(`Si recibiste credenciales de "abogado" (email + contraseña), entras en ${SITIO}/pro/login y, tras autenticarte, ves los leads que el admin te asignó en ${SITIO}/pro. Tu día típico se ve así:`),
  H(HeadingLevel.HEADING_2, "5.1 Bandeja de leads"),
  bullet("Ves todos los leads que generaron borrador en alguna landing y quedaron pendientes de contacto."),
  bullet("Cada lead muestra: vertical, fecha, datos de contacto, descripción del caso, borrador generado y trazabilidad UTM."),
  bullet("Puedes filtrar por vertical, por estado (nuevo / contactado / agendado / perdido / ganado) y por rango de fechas."),
  bullet("Botón \"Marcar como contactado\" registra cuándo y cómo escribiste al cliente. Botón \"Agendar\" abre un modal con tu disponibilidad."),
  H(HeadingLevel.HEADING_2, "5.2 Agenda nativa"),
  P("La agenda no usa Google Calendar (decisión consciente para no depender de cuentas externas). Cada abogado define su disponibilidad desde el panel:"),
  numbered("Pulsa \"Mi agenda\" en el menú lateral."),
  numbered("Marca los días y rangos horarios disponibles (ej. lunes a viernes 9-12 y 14-17)."),
  numbered("Define duración de cita por defecto (30 min, 45 min, 1 h)."),
  numbered("Las citas que agenden los clientes desde la landing se publican aquí automáticamente."),
  H(HeadingLevel.HEADING_2, "5.3 Expedientes con OTP"),
  P("Cuando un cliente acepta contratar al abogado:"),
  numbered("Desde el lead, pulsa \"Convertir en expediente\"."),
  numbered("El sistema genera un token único y envía un código OTP al WhatsApp / correo del cliente."),
  numbered("El cliente entra a /expediente/{token}, ingresa el OTP y firma electrónicamente la aceptación de servicios profesionales (Ley 527/99)."),
  numbered("Desde ese momento puedes subir documentos, agregar notas internas y registrar avances. Toda acción queda en el audit_log (append-only)."),
  H(HeadingLevel.HEADING_2, "5.4 WhatsApp"),
  P("La plataforma puede enviar mensajes por WhatsApp para notificar al cliente sobre su borrador, agendamientos y OTPs. Internamente usa un proveedor (UltraMsg o Evolution API) con fallback automático: si uno falla, intenta con el otro. Tú solo ves: \"WhatsApp enviado\" o \"WhatsApp falló\". Si falla, el sistema intenta correo electrónico."),
];

const seccion_admin = [
  H(HeadingLevel.HEADING_1, "6. Guía para admin"),
  P(`El panel de admin (${SITIO}/admin) es el centro de control del despacho. Usa autenticación HTTP básica (usuario + contraseña en el pop-up del navegador). Solo tú o los socios deben tener este rol.`),
  H(HeadingLevel.HEADING_2, "6.1 Gestión de abogados"),
  bullet("Crear abogado: nombre, correo, teléfono WhatsApp, áreas de práctica (puedes marcar todas con *)."),
  bullet("Editar abogado existente: cambiar disponibilidad, áreas, marcar como inactivo (no se le asignan más leads pero su histórico permanece)."),
  bullet("Crear asistentes de despacho: rol restringido para paralegales o practicantes."),
  bullet("Ver KPIs por abogado: leads asignados, tasa de conversión, expedientes abiertos, expedientes ganados."),
  H(HeadingLevel.HEADING_2, "6.2 Gestión de landings (verticales)"),
  P("Las 4 landings se siembran automáticamente al primer arranque. Si una está vacía o desactualizada, el sistema la enriquece automáticamente con el seed rico (config completa con prompt template, casos curados, FAQ, etc.)."),
  P("Desde admin puedes:"),
  bullet("Ver todas las landings con su slug, color, ícono, área RAG y estado."),
  bullet("Editar cualquier campo de cualquier landing en caliente, sin redeploy: H1, subtitulo, color, casos curados, prompt template, FAQ, pretensiones tipo, pruebas sugeridas, trust block, stats."),
  bullet("Activar / desactivar una landing (la URL devuelve 404 si está desactivada)."),
  bullet("Crear NUEVAS landings además de las 4 default. Útil para campañas A/B o nichos micro (ej. \"pensiones\", \"servicios públicos\", \"PQR aerolíneas\")."),
  callout(
    "Crear un nuevo vertical sin programar",
    [
      "Pulsa \"Nueva landing\" en el panel admin → llena el formulario completo (slug, color, ícono, prompt template) → guarda. Queda viva en /c/{slug} sin redeploy.",
      "El skill \"vertical-rag-tuning\" en la documentación interna explica cómo diseñar el prompt template para que el motor RAG se sienta diferenciado.",
    ],
    ORO
  ),
  H(HeadingLevel.HEADING_2, "6.3 Auditoría de jurisprudencia"),
  bullet("Vista de todos los documentos cargados al catálogo RAG: número de sentencia, área, fecha, fuente, estado de procesamiento."),
  bullet("Subir nuevas sentencias en PDF: el sistema las parsea, extrae texto, las indexa con BM25 + FAISS y las deja disponibles para el RAG."),
  bullet("Editar metadatos: cambiar el área de una sentencia mal clasificada, añadir tags, marcar como \"no usar\" si está obsoleta."),
  bullet("Eliminar sentencias del catálogo (con confirmación, queda registro en audit_log)."),
  H(HeadingLevel.HEADING_2, "6.4 Tracking UTM y conversiones"),
  P("Toda landing acepta parámetros UTM en la URL (?utm_source=facebook&utm_medium=cpc&utm_campaign=tutelas-mar26). El sistema los persiste en cada lead. En admin puedes ver:"),
  bullet("Top 10 fuentes que más leads generan."),
  bullet("Tasa de conversión lead → expediente por fuente."),
  bullet("Costo por lead si subes el gasto publicitario por campaña."),
];

const seccion_funcionalidades = [
  H(HeadingLevel.HEADING_1, "7. Funcionalidades clave en detalle"),
  H(HeadingLevel.HEADING_2, "7.1 Motor RAG (Retrieval Augmented Generation)"),
  P(
    "El cerebro de la plataforma. Cada vez que se genera un borrador, el sistema:"
  ),
  numbered("Toma la descripción del caso del cliente y, si es necesario, detecta el área (salud, laboral, accidentes, etc.). Si la landing tiene area_focus, lo respeta y omite la auto-detección."),
  numbered("Lanza una búsqueda híbrida en el catálogo: BM25 (palabras exactas) + FAISS (vectores semánticos)."),
  numbered("Toma las top sentencias del área y las inyecta en el prompt template del vertical."),
  numbered("Llama al modelo (Gemini) con el prompt completo y devuelve el borrador."),
  numbered("Toda la respuesta se guarda en BD, junto con qué sentencias citó, para trazabilidad."),
  H(HeadingLevel.HEADING_2, "7.2 Agenda y citas"),
  P("Agenda nativa por abogado, sin dependencias externas. Decisión consciente: no obligamos a los clientes a tener Google. La agenda respeta zona horaria de Bogotá y bloquea automáticamente las franjas ya tomadas."),
  H(HeadingLevel.HEADING_2, "7.3 Expedientes con firma electrónica"),
  P(
    "Implementación de firma electrónica simple según Ley 527/1999 (artículos 7 y 28). " +
    "El cliente recibe un OTP, lo ingresa, y queda registrado en el audit_log:"
  ),
  bullet("Hash SHA-256 del documento aceptado."),
  bullet("OTP usado y timestamp."),
  bullet("IP y user-agent del cliente."),
  bullet("Geolocalización aproximada (si el navegador la concede)."),
  P("Esto da fuerza probatoria razonable en juicio para procesos de bajo / medio valor. Para casos de alto valor o cuando una contraparte cuestione la firma, recomendamos pasar a firma electrónica certificada de tercero (ej. Andes SCD)."),
  H(HeadingLevel.HEADING_2, "7.4 WhatsApp con failover"),
  P("Dos proveedores configurados:"),
  bullet("Principal: UltraMsg (más fácil de configurar, paga por uso)."),
  bullet("Secundario: Evolution API self-hosted (Hostinger VPS, sin costo por mensaje pero requiere mantener un servidor)."),
  P("La capa Hybrid intenta primero con uno, si falla por timeout o sesión caída intenta con el otro. Si ambos fallan, el sistema escribe el mensaje a una cola y lo reintenta cada 5 minutos hasta 1 hora. Como último recurso, envía correo."),
  H(HeadingLevel.HEADING_2, "7.5 Tracking UTM y atribución"),
  P("Cada lead se etiqueta con utm_source, utm_medium, utm_campaign, utm_term, utm_content. Permite saber qué Facebook ad o qué publicación en LinkedIn generó cada cliente. Los reportes de admin agrupan por estos campos."),
  H(HeadingLevel.HEADING_2, "7.6 Jurisprudencia auditable"),
  P(
    "El catálogo de sentencias es la diferencia con un \"chatbot legal\" cualquiera. Toda sentencia citada en un borrador puede ser " +
    "trazada al PDF original. Esto te protege ante un cliente que pregunte \"¿de dónde sacaste esta sentencia?\" o ante una posible " +
    "queja por mala práctica: tienes el catálogo verificable, no improvisado por la IA."
  ),
];

const seccion_pruebas = [
  H(HeadingLevel.HEADING_1, "8. Guion de pruebas (test scripts)"),
  P("Esta es la lista mínima de pruebas que pedimos a cada probador. Calcula 2-3 horas para hacerla con calma."),
  H(HeadingLevel.HEADING_2, "8.1 Pruebas de identidad visual (15 min)"),
  numbered("Abre las 4 landings en pestañas distintas y compara. ¿Cada una tiene su color (oro / naranja / rojo / morado) y su ícono (⚖️ / 🚗 / 🚦 / 💼)?"),
  numbered("Si una se ve igual a otra, captura las dos y reporta."),
  numbered("Verifica que los \"casos más frecuentes\" sean específicos del vertical, no genéricos."),
  H(HeadingLevel.HEADING_2, "8.2 Pruebas de RAG por vertical (45 min)"),
  P("Para cada vertical, genera 2 borradores con casos distintos. Sugerencias:"),
  table3col(
    ["Vertical", "Caso 1", "Caso 2"],
    [
      ["Tutelas", "Sanitas EPS lleva 3 meses sin autorizar la cirugía de rodilla.", "Colpensiones no responde el derecho de petición de pensión de invalidez (radicado hace 4 meses)."],
      ["Accidentes", "Choque en moto, conductor del carro huyó, gastos médicos $4.5 millones, EPS solo cubre parte.", "Acompañante en bus intermunicipal, fractura de fémur, aseguradora del bus dice que no responde."],
      ["Comparendos", "Llegaron 6 fotomultas a casa por un carro que vendí hace 8 meses (traspaso registrado).", "Embargo de cuenta de ahorros por comparendo del 2019 que nunca me notificaron."],
      ["Laboral", "Despido durante embarazo de 5 meses, sin permiso del Ministerio.", "OPS de 18 meses con horario fijo, supervisor diario y entrega de portátil. Quieren no renovar."],
    ],
    ORO
  ),
  P(""),
  P("Para cada borrador generado, califica:"),
  bullet("¿Estructura del documento es la del vertical (no copiada de tutelas genéricas)?"),
  bullet("¿Cita sentencias del área correcta?"),
  bullet("¿Las pretensiones tienen sentido jurídico?"),
  bullet("¿Pide pruebas relevantes para el caso?"),
  bullet("¿Hay placeholders [COMPLETAR ...] mal rellenados?"),
  bullet("¿Tono adecuado (urgente / explicativo / reivindicativo)?"),
  H(HeadingLevel.HEADING_2, "8.3 Pruebas de agenda (15 min)"),
  numbered("Como cliente, intenta agendar una cita desde una landing."),
  numbered("Verifica que solo se ofrezcan franjas que un abogado tenga marcadas como disponibles."),
  numbered("Si tienes credencial de abogado, marca un día como no disponible y comprueba que desaparece de la oferta al cliente."),
  H(HeadingLevel.HEADING_2, "8.4 Pruebas de expediente y OTP (20 min)"),
  numbered("Como abogado, convierte un lead en expediente."),
  numbered("Como cliente, abre el enlace recibido. ¿Llega el OTP?"),
  numbered("Ingresa el OTP correcto: ¿se firma y queda confirmación?"),
  numbered("Ingresa OTP incorrecto: ¿da error claro? ¿bloquea tras 3 intentos?"),
  H(HeadingLevel.HEADING_2, "8.5 Pruebas de admin (30 min)"),
  numbered("Crea un abogado nuevo (ficticio). Asígnale área \"laboral\" únicamente."),
  numbered("Genera un lead en /c/laboral y verifica que el lead aparezca en su bandeja, no en la de los demás abogados."),
  numbered("Edita una landing existente (cambia el subtítulo). Recarga /c/{slug} y verifica el cambio en vivo."),
  numbered("Sube una sentencia nueva al catálogo y, después de procesada, genera un nuevo borrador donde esa sentencia debería citarse. ¿Aparece?"),
];

const seccion_bugs = [
  H(HeadingLevel.HEADING_1, "9. Cómo reportar bugs y feedback"),
  callout(
    "Plantilla de reporte (copia y pega)",
    [
      "Vertical / módulo: (ej. /c/accidentes · generación de borrador)",
      "Severidad: (alta / media / baja)",
      "Pasos para reproducir: 1) ... 2) ... 3) ...",
      "Resultado obtenido: ...",
      "Resultado esperado: ...",
      "Captura adjunta: sí / no",
      "Navegador y dispositivo: (ej. Chrome 124 · Windows 11)",
      "Hora aproximada: (ej. 27 abril 16:42)",
    ],
    ORO
  ),
  P(""),
  H(HeadingLevel.HEADING_2, "9.1 Niveles de severidad"),
  table3col(
    ["Severidad", "Definición", "Ejemplos"],
    [
      ["ALTA", "Bloquea el flujo principal, expone datos o genera contenido jurídicamente incorrecto.", "Borrador cita una sentencia que no existe. Login no funciona. Lead no se guarda."],
      ["MEDIA", "Funciona pero entrega resultado deficiente o lento.", "Borrador toma más de 30 segundos. Color del vertical no se ve. Caso curado mal redactado."],
      ["BAJA", "Cosmético o de copy. No bloquea ningún flujo.", "Typo en una FAQ. Espacio extra en un párrafo. Emoji desalineado."],
    ],
    ROJO
  ),
  P(""),
  H(HeadingLevel.HEADING_2, "9.2 Canal de reporte"),
  P("Por ahora todos los reportes van por WhatsApp directo al admin del programa. En la versión 2 abriremos un canal en Notion / Linear con tablero público para los probadores."),
  H(HeadingLevel.HEADING_2, "9.3 Feedback cualitativo (al final del programa)"),
  P("Cuando termines tu ronda de pruebas, te pediremos:"),
  bullet("Calificación general 1-10."),
  bullet("Tu Top 3 de mejoras prioritarias."),
  bullet("Una idea de funcionalidad que falta."),
  bullet("Un caso real que NO supiste cómo encajar en ninguno de los 4 verticales (esto nos dice qué quinto vertical crear)."),
];

const seccion_roadmap = [
  H(HeadingLevel.HEADING_1, "10. Roadmap"),
  P("Lo que está vivo hoy y lo que viene en las próximas iteraciones."),
  H(HeadingLevel.HEADING_2, "10.1 v1.0 — Disponible (lo que estás probando)"),
  bullet("4 verticales únicos (tutelas, accidentes, comparendos, laboral) con motor RAG propio."),
  bullet("Generación de borrador con citación de sentencias verificables."),
  bullet("Agenda nativa por abogado."),
  bullet("Expedientes con OTP (firma electrónica simple Ley 527/99)."),
  bullet("WhatsApp con failover (UltraMsg + Evolution API)."),
  bullet("Tracking UTM y atribución de leads."),
  bullet("Panel admin para abogados, asistentes, landings y catálogo."),
  bullet("Skill \"vertical-rag-tuning\" para crear nuevos verticales sin programar."),
  H(HeadingLevel.HEADING_2, "10.2 v1.1 — Próximas 4 semanas"),
  bullet("Notificaciones push web y mejor manejo del estado del lead."),
  bullet("Dashboard ejecutivo con KPIs en tiempo real (leads, conversión, ingresos)."),
  bullet("Verticales adicionales con base en feedback: candidatos fuertes son \"pensiones\", \"servicios públicos\" y \"consumidor financiero\"."),
  bullet("Mejor parser de PDFs jurídicos (extrae jurisprudencia con menos ruido)."),
  H(HeadingLevel.HEADING_2, "10.3 v1.2 — Próximos 2 meses"),
  bullet("Integración con firma electrónica certificada de tercero para casos de alto valor."),
  bullet("Plantillas de respuesta automática para preguntas frecuentes en WhatsApp."),
  bullet("Monetización: paquetes de honorarios fijos por tipo de caso. Test A/B sobre el cierre."),
  H(HeadingLevel.HEADING_2, "10.4 v2.0 — Próximos 4 meses"),
  bullet("App móvil para clientes (consultar el estado de su expediente)."),
  bullet("Marketplace de abogados (otros despachos publican su perfil y compran leads de la plataforma)."),
  bullet("Modo \"asesoría legal preventiva\" con suscripción mensual."),
];

const seccion_faq = [
  H(HeadingLevel.HEADING_1, "11. FAQ"),
  H(HeadingLevel.HEADING_3, "¿La IA reemplaza al abogado?"),
  P("No. La IA hace el trabajo repetitivo (estructura, citación, lenguaje formal). El abogado humano valida, ajusta el caso al hecho concreto, firma, presenta y litiga. Sin abogado humano, la plataforma sería ilegal en Colombia (ejercicio del derecho)."),
  H(HeadingLevel.HEADING_3, "¿Por qué cuatro verticales y no \"un asistente legal general\"?"),
  P("Un \"asistente general\" pierde foco. Tutelas, comparendos, accidentes y laboral exigen razonamientos, jurisprudencia y pretensiones distintas. Un cliente que entra buscando ayuda con un comparendo no quiere que la IA le hable de fueros laborales. Verticalizar mejora la conversión y la calidad del documento."),
  H(HeadingLevel.HEADING_3, "¿Las sentencias citadas son reales?"),
  P("Sí. Vienen de un catálogo cargado por nosotros con PDFs oficiales. La IA solo puede citar sentencias que están en el catálogo. Si una sentencia no está, la IA puede mencionar la línea jurisprudencial pero no inventar el número de sentencia."),
  H(HeadingLevel.HEADING_3, "¿Qué pasa si el RAG cita una sentencia mal?"),
  P("Repórtalo con captura. El equipo revisa el PDF original, corrige metadatos o saca esa sentencia del catálogo. Cero tolerancia con citaciones erróneas: es lo que diferencia esta plataforma de un chatbot común."),
  H(HeadingLevel.HEADING_3, "¿La firma electrónica vale en juicio?"),
  P("La firma electrónica simple (OTP + audit_log) tiene valor probatorio según los artículos 7 y 28 de la Ley 527/1999, especialmente para procesos de bajo y medio valor. Para casos donde una contraparte va a cuestionar la firma o donde el monto es alto, recomendamos firma electrónica certificada de tercero."),
  H(HeadingLevel.HEADING_3, "¿Por qué no usan Google Calendar?"),
  P("Tres razones: privacidad (no compartimos los calendarios de los clientes con Google), control (manejamos los datos en nuestra propia base) y fricción (un cliente promedio en Colombia no tiene cuenta de Google sincronizada). La agenda nativa funciona en cualquier navegador."),
  H(HeadingLevel.HEADING_3, "¿Cuánto cobra el abogado?"),
  P("Eso lo decide cada abogado por caso. La plataforma sugiere modelos (cuota litis, honorarios fijos, suscripción) pero no impone tarifa. La transparencia con el cliente es obligatoria desde el primer contacto."),
  H(HeadingLevel.HEADING_3, "¿Mis datos están seguros?"),
  P("Cumplimos con la Ley 1581/2012 (habeas data). Solo personas autorizadas dentro del despacho ven los datos del cliente. Las contraseñas están cifradas. La base de datos hace backup diario. La plataforma corre en infraestructura de Render con TLS."),
  H(HeadingLevel.HEADING_3, "¿Puedo usar la plataforma para casos en otros países?"),
  P("Por ahora no. Toda la jurisprudencia y la normativa cargadas son colombianas. Es una decisión consciente: \"profundidad antes que extensión\"."),
];

const seccion_glosario = [
  H(HeadingLevel.HEADING_1, "12. Glosario jurídico mínimo"),
  P("Términos que aparecen en la plataforma y en este manual."),
  table2col(
    [
      ["Acción de tutela", "Mecanismo constitucional (art. 86 CP, Decreto 2591/91) para proteger derechos fundamentales cuando se vulneran o amenazan. Fallo en máximo 10 días hábiles."],
      ["Audit_log", "Registro append-only (no se borra ni edita) de todas las acciones realizadas en un expediente. Trazabilidad y soporte probatorio."],
      ["BM25", "Algoritmo clásico de búsqueda por palabras clave. Encuentra sentencias que coinciden literalmente con términos de la consulta."],
      ["Cobro coactivo", "Procedimiento administrativo para cobrar deudas con el Estado (multas de tránsito, impuestos). Requiere debido proceso para ser válido."],
      ["Contrato realidad", "Cuando una OPS o servicios encubren una relación laboral subordinada. La Corte ordena pagar prestaciones como si hubiera sido contrato laboral."],
      ["Daño emergente", "Gasto efectivo causado por un hecho dañoso (transporte a citas, medicamentos, terapias)."],
      ["Debido proceso", "Garantía constitucional (art. 29 CP) de ser oído antes de ser sancionado, conocer las pruebas y poder controvertirlas."],
      ["Derecho de petición", "Derecho fundamental (art. 23 CP) a presentar peticiones a las autoridades y obtener respuesta de fondo en máximo 15 días hábiles."],
      ["Estabilidad laboral reforzada", "Protección especial al trabajador en condición de vulnerabilidad (embarazo, salud, sindical, prepensión). Despido requiere permiso del Ministerio."],
      ["Expediente", "Caso convertido en cliente. Implica firma electrónica del cliente y obligación profesional del abogado."],
      ["FAISS", "Biblioteca de búsqueda vectorial (semántica). Encuentra sentencias parecidas en significado, aunque no compartan palabras literales."],
      ["FOSYGA / ADRES Subcuenta ECAT", "Fondo que cubre accidentes de tránsito cuando el vehículo causante es desconocido o no tiene SOAT."],
      ["Fuero", "Protección constitucional contra despido. Maternidad, salud (Ley 361/97), sindical y prepensión."],
      ["Habeas data", "Derecho a conocer, actualizar y rectificar datos personales (Ley 1581/2012)."],
      ["IPAT", "Informe Policial de Accidente de Tránsito. Documento clave para reclamar al SOAT o a la aseguradora."],
      ["Lucro cesante", "Lo que se dejó de percibir por culpa de un hecho dañoso (días de salario perdidos por incapacidad)."],
      ["Medida provisional", "Orden que dicta el juez constitucional antes del fallo, cuando hay perjuicio irremediable (art. 7 D.2591/91)."],
      ["Mínimo vital", "Recursos básicos para subsistencia digna del trabajador y su familia. Bajar de él activa protección constitucional."],
      ["OPS", "Orden de Prestación de Servicios. Contrato civil (no laboral). Si encubre subordinación, hay contrato realidad."],
      ["OTP", "One-Time Password. Código de un solo uso enviado al WhatsApp / correo del cliente para firmar electrónicamente."],
      ["Perjuicio irremediable", "Daño actual, grave, inminente e impostergable. Habilita la medida provisional y la tutela urgente."],
      ["Pretensiones", "Lo que se le pide al juez en una tutela o demanda. Deben ser concretas, posibles y proporcionales."],
      ["RAG", "Retrieval Augmented Generation. La IA recupera primero documentos verificables y luego genera la respuesta basándose solo en ellos."],
      ["RUNT", "Registro Único Nacional de Tránsito. Base oficial de vehículos en Colombia."],
      ["SIMIT", "Sistema Integrado de Información sobre Multas y Sanciones por Infracciones de Tránsito."],
      ["SMDLV", "Salario Mínimo Diario Legal Vigente. Unidad usada por el SOAT y otras normativas para fijar topes."],
      ["SOAT", "Seguro Obligatorio de Accidentes de Tránsito. Cubre gastos médicos, incapacidad y muerte por accidente."],
      ["Tutela contra particulares", "Procedente cuando hay subordinación, indefensión o el particular presta un servicio público (EPS, banco con monopolio, etc.)."],
      ["UTM", "Parámetros de URL (utm_source, utm_medium, utm_campaign) que identifican de dónde viene cada cliente."],
    ],
    ORO,
    ["Término", "Definición"]
  ),
];

const seccion_cierre = [
  divider(),
  P(""),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 400, after: 200 },
    children: [new TextRun({ text: "Gracias por probar.", bold: true, size: 36, color: ORO })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 80 },
    children: [new TextRun({ text: "Tu feedback decide la versión final.", size: 24, color: GRIS })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 600 },
    children: [new TextRun({ text: "Galeano Herrera | Abogados", italics: true, size: 20, color: GRIS })],
  }),
];

// ---------- documento ----------
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } }, // 11pt
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: ORO },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ORO, space: 8 } } },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "111111" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "333333" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
        ],
      },
      {
        reference: "numbers",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        },
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: ORO, space: 4 } },
              children: [
                new TextRun({ text: "Galeano Herrera | Abogados", bold: true, color: ORO, size: 18 }),
                new TextRun({ text: "\tManual de entrega · Programa de pruebas v1.0", color: GRIS, size: 16 }),
              ],
            }),
          ],
        }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: "Documento confidencial · ", color: GRIS, size: 16 }),
                new TextRun({ text: "Página ", color: GRIS, size: 16 }),
                new TextRun({ children: [PageNumber.CURRENT], color: GRIS, size: 16 }),
                new TextRun({ text: " de ", color: GRIS, size: 16 }),
                new TextRun({ children: [PageNumber.TOTAL_PAGES], color: GRIS, size: 16 }),
              ],
            }),
          ],
        }),
      },
      children: [
        ...portada,
        ...seccion_indice,
        ...seccion_bienvenida,
        ...seccion_visiongeneral,
        ...seccion_accesos,
        ...seccion_clientes,
        ...seccion_abogados,
        ...seccion_admin,
        ...seccion_funcionalidades,
        ...seccion_pruebas,
        ...seccion_bugs,
        ...seccion_roadmap,
        ...seccion_faq,
        ...seccion_glosario,
        ...seccion_cierre,
      ],
    },
  ],
});

// Escribir a un archivo con sufijo si el principal está bloqueado (Word abierto)
const primary = path.join(__dirname, "Manual_Entrega_Galeano_Herrera.docx");
let out = primary;
try {
  fs.openSync(primary, "r+"); // ¿podemos escribir?
} catch (e) {
  if (e.code === "EBUSY") {
    out = path.join(__dirname, "Manual_Entrega_Galeano_Herrera_v2.docx");
    console.log("Original abierto en Word — escribiendo en", path.basename(out));
  }
}
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("OK ->", out, "| size:", buf.length, "bytes");
});
