#!/usr/bin/env python3
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'documentacion'
OUT.mkdir(exist_ok=True)
DOC=Document()
section=DOC.sections[0]
section.page_height=Cm(29.7)
section.page_width=Cm(21)
section.top_margin=Cm(2.15)
section.bottom_margin=Cm(1.85)
section.left_margin=Cm(2.05)
section.right_margin=Cm(2.0)
section.header_distance=Cm(0.95)
section.footer_distance=Cm(0.92)

styles=DOC.styles
base=styles['Normal']
base.font.name='Aptos'
base.font.size=Pt(10)
base.font.color.rgb=RGBColor(25,41,61)
base.paragraph_format.space_after=Pt(5)
base.paragraph_format.line_spacing=1.14
for nm,size,color,space in [('Title',26,RGBColor(17,35,61),14),('Heading 1',16,RGBColor(17,35,61),10),('Heading 2',12.5,RGBColor(23,75,146),6),('Heading 3',11,RGBColor(23,75,146),5)]:
    st=styles[nm]
    st.font.name='Aptos Display'
    st.font.size=Pt(size)
    st.font.bold=True
    st.font.color.rgb=color
    st.paragraph_format.space_before=Pt(space)
    st.paragraph_format.space_after=Pt(6)
    st.paragraph_format.keep_with_next=True

header=section.header.paragraphs[0]
header.text='ET N.º 35   /   DESARROLLO DE SISTEMAS                                                   TP 02 · 2026'
header.alignment=WD_ALIGN_PARAGRAPH.LEFT
for run in header.runs:
    run.font.size=Pt(7.8);run.font.bold=True;run.font.color.rgb=RGBColor(89,107,130)
footer=section.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('Pañol-App  •  Carpeta técnica    |    Página ')
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
for run in footer.runs:
    run.font.size=Pt(8);run.font.color.rgb=RGBColor(102,119,139)

def p(text='',style=None,boldfirst=None):
    a=DOC.add_paragraph(style=style)
    if boldfirst and text.startswith(boldfirst):
        a.add_run(boldfirst).bold=True;a.add_run(text[len(boldfirst):])
    else:a.add_run(text)
    return a

def hd(x,level=1): DOC.add_heading(x,level=level)

def bullet(x): p(x,'List Bullet')
def numbered(x): p(x,'List Number')

def table(headers,rows,widths=None):
    t=DOC.add_table(rows=1, cols=len(headers))
    t.style='Light Shading Accent 1'
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(headers):
        cell=t.rows[0].cells[i];cell.text=h
    for row in rows:
        cells=t.add_row().cells
        for i,v in enumerate(row): cells[i].text=str(v)
    for ri,row in enumerate(t.rows):
        for cell in row.cells:
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for para in cell.paragraphs:
                para.paragraph_format.space_after=Pt(1)
                para.paragraph_format.line_spacing=1.03
                for run in para.runs:
                    run.font.size=Pt(8.2)
                    if ri==0:run.font.bold=True;run.font.color.rgb=RGBColor(255,255,255)
            if ri==0:
                tcpr=cell._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'174B92');tcpr.append(sh)
    DOC.add_paragraph().paragraph_format.space_after=Pt(0)
    return t

def label(txt,body):
    para=DOC.add_paragraph()
    a=para.add_run(txt+'  ');a.bold=True;a.font.color.rgb=RGBColor(23,75,146)
    para.add_run(body)

def rule_lines(lines):
    for a,b in lines: label(a,b)

# Cover
DOC.add_paragraph('\n\n')
a=DOC.add_paragraph();a.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=a.add_run('ESCUELA TÉCNICA N.º 35\nING. EDUARDO LATZINA')
r.bold=True;r.font.size=Pt(15);r.font.color.rgb=RGBColor(25,77,146)
DOC.add_paragraph('\n')
a=DOC.add_paragraph(style='Title');a.alignment=WD_ALIGN_PARAGRAPH.CENTER
a.add_run('TRABAJO PRÁCTICO N.º 2\nPAÑOL-APP')
a=DOC.add_paragraph();a.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=a.add_run('Sistema Móvil de Gestión y Trazabilidad\nde Tablets Corporativas')
r.font.size=Pt(18);r.font.color.rgb=RGBColor(42,69,102)
DOC.add_paragraph('\n')
a=DOC.add_paragraph();a.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=a.add_run('FASE 1 · ANÁLISIS Y DISEÑO\nFASE 2 · IMPLEMENTACIÓN INCREMENTAL\nFASE 3 · PRUEBAS Y DEFENSA')
r.font.size=Pt(12);r.bold=True;r.font.color.rgb=RGBColor(25,77,146)
DOC.add_paragraph('\n\n')
for s in ['Materia: Desarrollo de Sistemas','Alumno: Ezequiel Freiheit','Curso: 6.º 3.ª','Profesor: Marcelo Rosales','Año lectivo: 2026','Plataforma objetivo: Android · Java · SQLite']:
    a=DOC.add_paragraph(s);a.alignment=WD_ALIGN_PARAGRAPH.CENTER
DOC.add_paragraph('\n')
a=DOC.add_paragraph('Versión de la carpeta: 1.0 · 20 de noviembre de 2026')
a.alignment=WD_ALIGN_PARAGRAPH.CENTER
DOC.add_page_break()

hd('Resumen ejecutivo')
p('Pañol-App es una aplicación Android para identificar tablets por código QR, registrar sus datos técnicos, controlar los préstamos internos y externos, recibir devoluciones, derivar equipos averiados a Servicio Técnico y auditar los movimientos en una base de datos local. La identificación también puede realizarse por número de serie cuando la etiqueta QR no puede leerse.')
p('Hereda del trabajo previo sobre almacenamiento LTO cuatro principios: estados mutuamente excluyentes, ubicación física derivada del estado, reglas de negocio centralizadas y Casos de Uso expandidos. Evoluciona hacia el uso de cámara real y el empaquetado Android APK.')
label('Alcance de entrega','Proyecto Android de código fuente, ejemplos QR físicos imprimibles, modelo de datos, reglas, casos de uso, pruebas de lógica y guía de compilación/instalación y defensa.')
label('Estado de validación','Las reglas de negocio están implementadas y superaron 15 pruebas JVM. No se ejecutó una compilación Android ni ensayos con un equipo físico en el entorno de generación (no dispone del SDK ni de Gradle). El APK debe construirse con el proyecto Android adjunto; por integridad, no se afirma que exista un APK ya compilado.')

hd('1. Problema, propósito y alcance')
p('Problema: el registro en planillas o mensajes dispersos dificulta determinar quién retiró cada tablet, dónde está, para qué tarea se autorizó la salida y si el equipo regresó en condiciones. Una duplicación de ubicación o un préstamo sin tarea comprometen la trazabilidad.')
p('Objetivo general: preservar una fuente única de verdad de estado, ubicación y responsable por número de serie, con operaciones auditables y escaneo físico mediante cámara.')
hd('1.1 Objetivos verificables',2)
for s in [
'Consultar ficha técnica tras leer un QR JSON o delimitado.',
'Impedir series duplicadas y retiros simultáneos o fuera de estado.',
'Exigir legajo en despachos y tarea mínima justificante para Home Office.',
'Registrar estado físico de la devolución y derivación a soporte.',
'Consultar estado actual e historial aun después de cerrar y reabrir la app.',
'Operar mediante teclado ante un QR deteriorado o imposibilidad de abrir el lector.'
]:bullet(s)
hd('1.2 Límites del prototipo',2)
p('Es una aplicación local de demostración académica. No se incluye inicio de sesión, verificación contra nómina real, aprobación por superiores, sincronización entre teléfonos, cifrado específico del contenido SQLite ni copia de seguridad en la nube. Tampoco se gestiona el recorrido de una reparación más allá de su inicio y finalización. Estas funciones constituyen una evolución futura y no deben confundirse con características ya implementadas.')

hd('2. Actores y casos de uso')
table(['Actor','Responsabilidad'],[
('Encargado de pañol','Da de alta, consulta inventario, despacha y recibe tablets.'),
('Empleado','Recibe equipo para uso local o remoto; informa su devolución.'),
('Personal técnico','Informa el fin de una reparación y el reingreso al pañol.'),
('Google Code Scanner','Servicio de escaneo que usa la cámara y devuelve el texto QR.'),
])
table(['Código','Caso de uso','Resultado'],[
('CU-01','Registrar alta','Nueva serie única, estado En Pañol e historial ALTA.'),
('CU-02','Despachar tablet','Estado local/externo, legajo y tarea según política.'),
('CU-03','Recibir devolución','En Pañol o Servicio Técnico según inspección.'),
('CU-04','Finalizar servicio','Tablet reparada vuelve a En Pañol; nuevo movimiento.'),
('CU-05','Identificación manual','Buscar por serie o ingresar QR por teclado.'),
])

hd('3. Reglas de dominio y ubicación')
p('El estado es exclusivo por dispositivo; se guarda una sola columna estado en tablets. La ubicación NO es un segundo dato editable: se calcula a partir del estado para que no pueda contradecirlo.')
table(['Estado persistido','Nombre visible','Ubicación derivada','Responsable'],[
('EN_PANOL','En Pañol','Depósito · Pañol','Custodia del encargado'),
('EN_USO_LOCAL','En Uso Local (Oficina)','Oficina de la empresa','Legajo obligatorio'),
('EN_USO_EXTERNO','En Uso Externo (Home Office)','Domicilio autorizado','Legajo y tarea obligatorios'),
('EN_SERVICIO_TECNICO','En Servicio Técnico','Área de Servicio Técnico','Sin empleado prestado'),
])
hd('3.1 Matriz de transiciones permitidas',2)
table(['Estado inicial','Operación','Guardas','Estado final'],[
('Sin registro','Alta','QR completo o carga manual válida; serie única','En Pañol'),
('En Pañol','Despacho local','Legajo válido','En Uso Local'),
('En Pañol','Despacho externo','Legajo + tarea ≥3 caracteres','En Uso Externo'),
('En Uso Local','Devolución correcta','Inspección física','En Pañol'),
('En Uso Externo','Devolución correcta','Inspección física','En Pañol'),
('En Uso Local / Externo','Devolución dañada','Inspección física','En Servicio Técnico'),
('En Servicio Técnico','Fin de servicio','Confirmación de equipo apto','En Pañol'),
])
p('Cualquier otra transición es rechazada. Una devolución no admite estado inicial En Pañol; el intento de segundo despacho se rechaza. El registro de un movimiento y la actualización del estado se realizan en la misma transacción SQLite.')
hd('3.2 Reglas de negocio formales',2)
for k,v in [
('RN-01 · Identidad','serial normalizado a mayúsculas; patrón de 3 a 40 caracteres alfanuméricos y símbolos . _ -; clave primaria única.'),
('RN-02 · Estado único','un único estado válido por serie, restringido mediante CHECK en SQLite.'),
('RN-03 · Ubicación','ubicación se calcula a partir del estado; no hay columna de ubicación libre.'),
('RN-04 · Disponibilidad','solo se despacha un equipo en En Pañol.'),
('RN-05 · Empleado','un despacho requiere legajo de 3 a 24 caracteres: letras, cifras y guiones.'),
('RN-06 · Home Office','se exige tarea explícita de al menos tres caracteres; un intento inválido presenta alerta visual y no escribe en SQLite.'),
('RN-07 · Retorno','solo se devuelve un equipo que esté En Uso Local o En Uso Externo.'),
('RN-08 · Inspección','devolución correcta retorna al pañol; dañada pasa a soporte.'),
('RN-09 · Historial','cada operación registra tipo, antes/después, fecha, legajo/tarea históricos y método de identificación.'),
('RN-10 · Consistencia','las modificaciones de estado y el asiento en movimientos son atómicos y se verifican con UPDATE condicionado.'),
('RN-11 · QR estático','la etiqueta incluye datos técnicos y serie, nunca estado, legajo, tarea o ubicación; esos campos cambian en SQLite.'),
('RN-12 · Conflicto QR','si el QR de una serie existente contradice el inventario, se conserva el registro local y se avisa la discrepancia.'),
]:label(k,v)

hd('4. Modelado de casos de uso expandidos')

def caso(nombre,actor,obj,pre,trigger,main,alt,post):
    hd(nombre,2)
    rule_lines([('Actor principal:',actor),('Objetivo:',obj),('Precondiciones:',pre),('Disparador:',trigger)])
    p('Flujo principal:',boldfirst='Flujo principal:')
    for a in main:numbered(a)
    p('Flujos alternativos y excepciones:',boldfirst='Flujos alternativos y excepciones:')
    for a in alt:bullet(a)
    label('Postcondiciones:',post)

caso('CU-01 · Registrar Alta de Tablet en Pañol','Encargado de pañol',
'Incorporar una tablet única con datos técnicos completos y estado disponible.',
'Aplicación abierta; código QR válido o formulario manual disponible.','Se presenta una tablet nueva o se solicita un alta.',
['El encargado pulsa Escanear QR o Registrar tablet manualmente.',
'El servicio QR lee una etiqueta física y devuelve texto JSON/delimitado, o el actor completa el formulario.',
'Se interpreta serie, procesador, RAM, almacenamiento, pantalla, puertos y conectividad.',
'El dominio comprueba formato, rangos y ausencia de esa serie en SQLite.',
'Se presenta una vista previa con estado inicial En Pañol y ubicación Depósito.',
'El operador confirma; una transacción inserta tablets y movimiento ALTA.',
'La aplicación muestra la ficha y ofrece compartir el QR lógico JSON.'],
['A1 · QR deteriorado: ingresar el contenido por teclado o completar alta manual con datos técnicos.',
'A2 · QR con JSON inválido o siete campos incompletos: informar error y no registrar.',
'A3 · Serie duplicada: rechazar alta y conservar el registro original.',
'A4 · Datos técnicos fuera de rango: rechazar operación y solicitar corrección.'],
'Una tablet nueva y un movimiento ALTA quedan persistidos; no se registra nada ante error.')
caso('CU-02 · Despachar Tablet','Encargado de pañol',
'Asignar el dispositivo a un empleado para uso en oficina o Home Office.',
'Tablet existente y en estado En Pañol.','Empleado solicita retiro para una tarea.',
['Identificar mediante QR, serie escrita o catálogo.',
'Consultar ficha, disponibilidad y ubicación actual.',
'Pulsar Despachar tablet y escoger Uso Local u Home Office.',
'Ingresar legajo y, para Home Office, la tarea asignada.',
'Validar legajo, tarea obligatoria si es externo, y estado En Pañol.',
'Actualizar estado y responsable con UPDATE condicional dentro de una transacción.',
'Crear movimiento DESPACHO y mostrar nueva ficha con legajo y ubicación.'],
['A1 · Home Office sin tarea: alerta visual roja, operación bloqueada; los datos no cambian.',
'A2 · Legajo ausente o inválido: rechazar y conservar formulario.',
'A3 · Tablet ocupada o en soporte: no ofrecer despacho y validar nuevamente en dominio.',
'A4 · Conflicto de estado: actualización afecta cero filas; anular transacción.',
'A5 · QR dañado: buscar por serie mediante teclado y continuar.'],
'Estado En Uso Local o En Uso Externo, legajo vinculado, tarea conservada y evento auditable.')
caso('CU-03 · Recibir Devolución de Dispositivo','Encargado de pañol',
'Registrar el regreso y la inspección física del equipo.',
'La tablet está en Uso Local o Externo y existe en SQLite.','Empleado entrega la tablet.',
['Escanear la etiqueta QR o ingresar el número de serie.',
'Consultar el estado actual y legajo responsable.',
'Pulsar Recibir devolución.',
'Inspeccionar físicamente la tablet y seleccionar Buen estado o Con daños.',
'Validar que el equipo figura prestado.',
'Devolver al estado En Pañol si está sano o a Servicio Técnico si está dañado.',
'Limpiar responsable/tarea vigentes; guardar un movimiento DEVOLUCION con los datos históricos del préstamo.'],
['A1 · QR ilegible: identificación por teclado; no se altera la transición.',
'A2 · Tablet ya en Pañol: rechazar la segunda devolución.',
'A3 · Tablet en Servicio Técnico: rechazar devolución por no existir préstamo activo.',
'A4 · Error de escritura o conflicto: revertir la transacción.'],
'Estado correcto y ubicación consistente; historial conserva legajo, tarea y estado físico.')
caso('CU-04 · Finalizar Servicio Técnico (complementario)','Personal técnico / encargado de pañol',
'Devolver a disponibilidad un equipo reparado.',
'Tablet En Servicio Técnico.','Se confirma reparación y verificación de funcionamiento.',
['Abrir ficha identificada por serie o QR.','Pulsar Registrar fin de servicio.',
'Confirmar que el equipo fue revisado y está apto.',
'Actualizar En Servicio Técnico → En Pañol y registrar FIN_SERVICIO en una transacción.'],
['A1 · Estado distinto de servicio: acción no disponible y regla bloquea.',
'A2 · Reparación no aprobada: cancelar sin cambios.'],
'Tablet disponible y evento técnico registrado.')

hd('5. Diseño de software y persistencia')
hd('5.1 Arquitectura en capas',2)
table(['Capa','Paquete / clase','Responsabilidad'],[
('Presentación','ui/MainActivity.java','Pantallas, alertas, navegación, eventos y entrada de datos.'),
('Identificación','qr/QrCodec.java','Interpretar/serializar QR JSON o delimitado.'),
('Dominio','domain/Reglas.java; Tablet.java','Invariantes, estados, guardas y ubicación derivada.'),
('Persistencia','data/PanolDb.java','SQLiteOpenHelper, consultas, histórico y transacciones.'),
('Servicio de cámara','Google Code Scanner','Vista de cámara, autoenfoque/autozoom y resultado QR.'),
])
p('Flujo de datos: Cámara / teclado → QrCodec → Regla de negocio → PanolDb (SQLite, transacción) → Ficha de estado / historial. El flujo de errores vuelve a la interfaz y no modifica la base.')
hd('5.2 Modelo entidad-relación',2)
p('TABLETS (1) — (N) MOVIMIENTOS, vinculadas por serial. Cada movimiento conserva el estado anterior y posterior. El responsable actual figura en TABLETS, mientras que sus datos históricos quedan congelados en MOVIMIENTOS.')
table(['Entidad','Campos principales','Restricciones'],[
('TABLETS','serial; procesador; ram_gb; almacenamiento_gb; pantalla_pulgadas; puertos; conectividad; estado; legajo; tarea; creado_en; actualizado_en','PK serial; CHECK estado; CHECK legajo para préstamo; CHECK tarea para externo.'),
('MOVIMIENTOS','id; serial; tipo; desde_estado; hacia_estado; legajo; tarea; condicion_fisica; metodo_identificacion; fecha','PK id; FK serial → TABLETS; índice (serial, fecha).'),
])
p('No existe una tabla de ubicación porque sería redundante y riesgosa. Tampoco existe un padrón de empleados dentro del prototipo: la entrada de legajo se valida por formato, no por autenticación corporativa.')
hd('5.3 Integridad y transacciones',2)
for s in ['BEGIN TRANSACTION; leer estado actual; validar regla; UPDATE tablets SET estado=... WHERE serial=? AND estado=estado_anterior; verificar que cambió exactamente una fila; INSERT movimientos; COMMIT. En error: ROLLBACK.',
'El uso de una clave primaria impide duplicar altas y los CHECK de SQLite actúan como segunda barrera frente a datos inconsistentes.',
'La trazabilidad es local: si dos celulares mantienen bases separadas, no se garantiza un estado global único. Un entorno productivo necesitaría servidor central, autorización por usuario y sincronización transaccional.']:bullet(s)

hd('6. Formatos de QR y datos')
p('QR estático versión 1. Contiene solo serial y características físicas. Se usa una cadena JSON UTF-8, de estructura estable:')
example='{"version":"1","serial":"TAB-001","procesador":"Snapdragon 680","ram_gb":4,"almacenamiento_gb":64,"pantalla_pulgadas":10.1,"puertos":["USB-C","Jack 3.5"],"conectividad":["Wi-Fi","Bluetooth"]}'
a=p(example)
for r in a.runs:r.font.name='Consolas';r.font.size=Pt(8.3)
p('Alternativa delimitada (7 campos en orden):')
a=p('TAB-001|Snapdragon 680|4|64|10.1|USB-C, Jack 3.5|Wi-Fi, Bluetooth')
for r in a.runs:r.font.name='Consolas';r.font.size=Pt(8.3)
p('Tamaño de texto máximo: 4096 caracteres. Los campos son validados antes del alta. En caso de etiqueta dañada, se permite escribir la serie de una tablet ya registrada o pegar el texto QR completo.')
p('En la carpeta etiquetas/ se entregan tres PNG con QR reales y un PDF de etiquetas A4. Estos ejemplares incluyen datos ficticios y pueden imprimirse para la práctica.')
DOC.add_picture(str(ROOT/'etiquetas/TAB-001.png'),width=Cm(5.4))
a=p('Figura 1. QR físico de prueba TAB-001; la misma ficha está en etiquetas/TAB-001.txt.')
for r in a.runs:r.italic=True;r.font.size=Pt(8)

hd('7. Metodología híbrida y Fase 2')
p('Fase predictiva: se fija inicialmente el problema, los actores, los Casos de Uso expandidos, el modelo de datos, los invariantes y los criterios de aceptación. Fase iterativa: se implementan dos sprints cortos, se revisa el comportamiento real con códigos físicos y se ajusta la experiencia sin romper los contratos de dominio.')
hd('7.1 Sprint 1 — Núcleo de Lectura e Interfaz',2)
label('Objetivo','Leer QR reales mediante cámara y presentar una ficha técnica ordenada.')
label('Historias','Como encargado, quiero enfocar una etiqueta y ver serie, procesador, RAM, almacenamiento, pantalla, puertos y conectividad. Como operador, quiero recuperar la lectura por teclado si la cámara falla.')
label('Actividades','Crear proyecto Android; integrar Google Code Scanner; implementar QrCodec; crear ficha, vista previa y navegación; generar etiquetas de prueba.')
label('Criterios de aceptación','Lectura QR JSON y delimitado; rechazo de estructuras inválidas; visualización correcta de campos; navegación sin alta automática al escanear; ingreso alternativo manual.')
label('Producto incremental','Interfaz + lector de cámara + decodificación + fichas + etiquetas imprimibles.')
hd('7.2 Sprint 2 — Lógica de Negocio y Persistencia',2)
label('Objetivo','Operar préstamos, devoluciones, Servicio Técnico e historial inalterable de cada transición.')
label('Historias','Como encargado, quiero bloquear un préstamo externo sin tarea; identificar al responsable por legajo; distinguir una devolución correcta de una dañada; consultar el historial.')
label('Actividades','Implementar Reglas y Tabla de estados; SQLite; movimientos atómicos; formularios de despacho/devolución; alertas rojas; cierre de servicio; tests de reglas.')
label('Criterios de aceptación','No hay doble préstamo ni serie duplicada; Home Office no permite tarea vacía; al devolver se borra la asignación vigente pero se conserva en historial; estado/ubicación siempre coinciden; persiste después de reiniciar.')
label('Producto incremental','Aplicación completa a nivel código fuente, persistencia SQLite y flujos de negocio.')
hd('7.3 Gestión de cambios de último momento',2)
p('Ejemplo: el docente agrega “QR deteriorado, ingreso por teclado” en la defensa. En el enfoque híbrido, el CU-05 se registra como extensión sin modificar la arquitectura ni las reglas de préstamo: se incorpora una segunda estrategia de identificación que invoca el mismo método de consulta y la misma máquina de estados. Se prioriza la contingencia, se prueba y se incorpora al siguiente incremento.')

hd('8. Estrategia de pruebas')
table(['ID','Escenario','Resultado esperado'],[
('P01','Alta TAB-001 por QR físico','Ficha técnica y evento ALTA; estado En Pañol.'),
('P02','Escanear otra vez serie existente','Muestra ficha, no crea duplicado.'),
('P03','Despachar local con legajo válido','Pasa a Oficina; responsable asignado.'),
('P04','Despachar externo sin tarea','Alerta roja, rechazo, sin cambios.'),
('P05','Despachar externo con tarea válida','Pasa a Home Office y guarda tarea.'),
('P06','Intentar otro despacho de equipo ocupado','Rechazo por estado.'),
('P07','Devolución sin daños','Pañol, legajo vaciado en estado vigente.'),
('P08','Devolución con daños','Servicio Técnico, movimiento con DANADA.'),
('P09','Cerrar servicio','Vuelve a Pañol; se añade FIN_SERVICIO.'),
('P10','QR roto / no legible','Entrada por teclado y continuidad del flujo.'),
('P11','Cerrar y abrir la aplicación','Estado e historial persisten en SQLite.'),
('P12','QR con serie conocida pero ficha diferente','Se preservan datos locales y se advierte.'),
('P13','JSON inválido / QR incompleto','Error visible; no escribe estado.'),
('P14','Teléfono sin Servicios Google','Lector puede fallar; alternativa manual.'),
])
label('Evidencia ejecutada','15 pruebas JVM de ReglasTest.java: normalización, disponibilidad, legalidad de transiciones, obligatoriedad de tarea, estados de devolución y fin de soporte; todas aprobadas. Se entregan comando y salida en pruebas/.')
label('Evidencia no ejecutada','La matriz P01-P14 es el protocolo para Android real; no se registra como superada hasta ejecutar la app en el dispositivo. No se realizó compilación APK en este entorno.')

hd('9. Artefacto Android: cómo obtener pañol-app.apk')
for line in [
'Abrir android/ desde Android Studio (proyecto Gradle) con SDK 35 y JDK 17; agregar Gradle 8.13 si lo solicita.',
'Sincronizar: se descargará com.google.android.gms:play-services-code-scanner:16.1.0 y el Android Gradle Plugin 8.13.0.',
'Seleccionar Build → Build Bundle(s) / APK(s) → Build APK(s), o ejecutar gradle :app:assembleDebug desde android/.',
'Copiar android/app/build/outputs/apk/debug/app-debug.apk al nombre solicitado pañol-app.apk; el APK debug está firmado para instalación de prueba.',
'Instalarlo desde archivos del teléfono habilitando instalación de origen desconocido cuando se solicite o usar adb install -r pañol-app.apk.',
'En el teléfono, abrir lector y mostrar Etiquetas_QR_Imprimir_A4.pdf desde un monitor o en papel; puede requerirse Internet inicial para descargar el módulo de escaneo.',
'Si la cámara no inicia, comprobar Servicios de Google Play y usar la alternativa manual para continuar la demostración.'
]:numbered(line)
p('Aviso de integridad: el archivo APK compilado NO se genera por mero cambio de nombre de un ZIP o del código fuente. La compilación real requiere las herramientas de Android. También se incluye workflow GitHub Actions para realizar esa compilación en un runner Android y publicar el artefacto.')

hd('10. Seguridad, limitaciones y evolución')
for s in [
'Validación de entrada QR: máximo de caracteres, esquema de campos, formatos de serie y rangos técnicos; se rechazan estructuras mal formadas.',
'Datos personales: legajos y tareas se almacenan localmente en SQLite y pueden ser sensibles. Para uso real, implementar control de acceso, cifrado, borrado controlado, respaldo y política de retención.',
'Fraude físico: un QR fotocopiado replica el identificador. El QR no autentica el activo; para producción deben añadirse verificación de etiqueta, credenciales del operador y eventualmente firmas digitales.',
'Sincronización: dos móviles aislados pueden crear historiales divergentes. El prototipo es monodispositivo; una versión corporativa requiere servidor y concurrencia centralizada.',
'Google Code Scanner: la primera ejecución depende de Servicios de Google Play; la lectura es por cámara, aunque la UI del escáner está gestionada por Google y no dibujada internamente.',
'Próximos incrementos: administración de empleados, listado de tareas autorizadas, aprobación de Home Office, reparación con diagnóstico, exportación CSV y sincronización central.'
]:bullet(s)

hd('11. Defensa oral: guion y respuestas')
hd('11.1 Presentación breve (90–120 s)',2)
p('“Pañol-App resuelve el problema de no saber dónde está cada tablet y quién es responsable. Cada dispositivo tiene una serie única y cuatro estados exclusivos. El QR contiene datos técnicos fijos; el estado y el historial quedan guardados en SQLite, porque cambian con el uso. En una demostración puedo leer un QR real, dar de alta el equipo, despacharlo con un legajo y recibirlo. Si el retiro es para Home Office, el sistema bloquea la salida cuando no hay tarea asignada. Si vuelve dañado, no queda disponible: pasa directamente a Servicio Técnico. Las transiciones se validan en dominio y se guardan junto con el movimiento en una sola transacción. Para un QR ilegible existe ingreso manual, que usa las mismas reglas. El proyecto se hizo con análisis previo de casos de uso y modelo de datos, seguido de dos sprints de implementación.”')
hd('11.2 Preguntas habituales y respuestas técnicas',2)
qa=[
('¿Por qué no guardaron la ubicación como campo editable?','Porque se producirían contradicciones: una tablet podría figurar en Pañol y en casa a la vez. La ubicación se deriva de su único estado.'),
('¿Qué significa una transacción?','Que actualizar el estado y registrar el movimiento sucede como una unidad: o se guardan las dos operaciones o ninguna.'),
('¿Cómo evitan prestar dos veces la misma tablet?','Solo se despacha si el estado es En Pañol; además, el UPDATE condiciona el estado anterior y verifica que se modifique exactamente un registro.'),
('¿Qué diferencia hay entre QR y base de datos?','El QR identifica un equipo y transporta ficha técnica fija. SQLite conserva el estado, asignación e historial actualizados.'),
('¿Qué pasa si no hay tarea en Home Office?','La regla de negocio lo impide; la interfaz indica el motivo en rojo, y no se escribe en la base.'),
('¿Y si el QR está dañado?','Ingreso por teclado de serie o contenido QR. Ambas entradas desembocan en la misma ficha y validaciones.'),
('¿Qué pasa si una tablet vuelve rota?','El responsable histórico queda en movimientos y la tablet pasa a En Servicio Técnico, bloqueada para préstamos.'),
('¿Qué es la persistencia?','Que los datos continúan guardados incluso al cerrar la aplicación; se consigue con SQLite.'),
('¿Por qué metodología híbrida?','El modelo de estados y la base se definieron de forma predictiva para mantener integridad; las pantallas y contingencias se desarrollaron por incrementos.'),
('¿Funciona en cualquier celular?','En Android 6 o superior con Servicios de Google Play para el lector; la app puede seguir operando por teclado cuando el lector no está disponible.'),
('¿La APK ya fue probada en un teléfono?','Se entregó proyecto compilable y se verificaron 15 reglas JVM. La compilación e instalación física no se realizaron en este entorno; no corresponde afirmarlas como probadas.'),
]
for q,a in qa:
    label('P: '+q,'R: '+a)

hd('12. Referencias técnicas')
for s in [
'Google for Developers — Google Code Scanner (Android): https://developers.google.com/ml-kit/vision/barcode-scanning/code-scanner',
'Android Developers — Android Gradle Plugin y compatibilidad: https://developer.android.com/build/releases/about-agp',
'Android Developers — SQLite y almacenamiento local: https://developer.android.com/training/data-storage/sqlite',
'Android Developers — Construir y ejecutar Android: https://developer.android.com/studio/run',
'Código fuente interno de la entrega: android/app/src/main/java/ar/edu/et35/panolapp/.',
]:bullet(s)

path=OUT/'Carpeta_Tecnica_Panol_App.docx'
DOC.save(path)
print('DOCX',path)

# Defensa oral de bolsillo, formato pdf con texto grande
pdf=OUT/'Guion_Defensa_Oral.pdf'
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
c=canvas.Canvas(str(pdf),pagesize=A4)
c.setTitle('Pañol-App — guía rápida para la defensa oral')
W,H=A4
margin=43

def wrapped(txt,font='DejaVu',size=9,width=490):
    words=txt.split(); out=[]; line=''
    for word in words:
        probe=(line+' '+word).strip()
        if pdfmetrics.stringWidth(probe,font,size) > width and line:
            out.append(line);line=word
        else:line=probe
    if line:out.append(line)
    return out

def pageheader(page):
    c.setFillColor(HexColor('#102039'));c.rect(0,H-104,W,104,fill=1,stroke=0)
    c.setFillColor(HexColor('#FFFFFF'));c.setFont('DejaVuBold',16)
    c.drawString(margin,H-54,'PAÑOL-APP · DEFENSA ORAL')
    c.setFont('DejaVu',9);c.drawString(margin,H-75,'ET 35 · Desarrollo de Sistemas · TP 02 · 2026')
    c.setFillColor(HexColor('#64748B'));c.setFont('DejaVu',8)
    c.drawString(margin,32,f'Guía de estudio y demostración | página {page}')

page=1;pageheader(page);y=H-128

def title(t):
    global y,page
    if y<115:
        c.showPage();page+=1;pageheader(page);y=H-130
    c.setFillColor(HexColor('#174B92'));c.setFont('DejaVuBold',11)
    c.drawString(margin,y,t);y-=21

def paragraph(t,big=False):
    global y,page
    s=10 if big else 9
    lines=wrapped(t,size=s)
    for line in lines:
        if y<75:
            c.showPage();page+=1;pageheader(page);y=H-130
        c.setFillColor(HexColor('#102039'));c.setFont('DejaVu',s)
        c.drawString(margin,y,line);y-=15
    y-=9

title('Presentación de 90 segundos')
paragraph('Pañol-App permite saber qué tablet tenemos, quién la retiró y dónde está. Los equipos se identifican por QR real y tienen uno de cuatro estados: Pañol, Uso Local, Uso Externo y Servicio Técnico. El QR almacena solo la serie y la ficha técnica; la base SQLite conserva el estado actualizado y el historial de préstamos. El retiro externo exige legajo y una tarea; si falta la tarea, se bloquea la operación. La devolución verifica el estado físico: correcta vuelve al pañol y dañada pasa a soporte. Si el QR no se lee, se ingresa la serie por teclado. En el desarrollo usamos casos de uso y reglas iniciales, seguidos de dos sprints.',True)
title('Secuencia de demostración')
for k in ['1. Mostrar QR impreso TAB-001; escanearlo con la cámara.', '2. Confirmar alta; mostrar la ficha y la ubicación En Pañol.', '3. Elegir Home Office sin tarea: explicar el bloqueo rojo.', '4. Agregar legajo EMP-123 y tarea TSK-100: despachar.', '5. Escanear otra vez; comprobar ubicación Home Office.', '6. Devolver como dañada: pasa a Servicio Técnico.', '7. Registrar fin de servicio; vuelve a En Pañol.', '8. Mostrar historial y luego ingreso manual TAB-001.']:
    paragraph(k)
title('Preguntas cortas de alto valor')
for q,a in qa[:8]:
    paragraph(q+' — '+a)
title('Conceptos para repetir')
paragraph('Regla de negocio = condición que limita una operación. Persistencia = conservación de datos. Transacción = todo o nada. SQLite = base de datos local. QR = representación escaneable de una cadena. Estado exclusivo = un único estado por tablet. Metodología híbrida = diseño estable + incrementos adaptables.')
title('Una limitación que conviene reconocer')
paragraph('Los 15 tests JVM verifican reglas. La carpeta incluye el código fuente para generar el APK, pero este entorno no ejecutó compilación Android ni prueba física; esas verificaciones no deben inventarse.')
c.save()
print('PDF defensa',pdf)
