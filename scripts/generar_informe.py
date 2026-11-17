from pathlib import Path
import json,csv,sqlite3,os,re,sys,html,textwrap
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing,Rect,String,Line

P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
M=json.loads((P/'evidencias/inspeccion_xlsm.json').read_text(encoding='utf-8'))
D=json.loads((P/'docs/diccionario.json').read_text(encoding='utf-8'))
Q=json.loads((P/'datos/consultas.json').read_text(encoding='utf-8'))
V=json.loads((P/'evidencias/conciliacion_historica.json').read_text(encoding='utf-8'))
repo=os.getenv('GITHUB_REPOSITORY','')
url='https://github.com/'+repo if re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo) else 'https://github.com/dan1elcg1raldo000/BDI-Proyecto-Final-Daniel-Felipe-Chica-Giraldo-Erick-Noel-Delgado-Serna'
fd=Path('C:/Windows/Fonts')
if (fd/'arial.ttf').exists():normal,bold=fd/'arial.ttf',fd/'arialbd.ttf'
else:
 import reportlab
 fd=Path(reportlab.__file__).parent/'fonts';normal,bold=fd/'Vera.ttf',fd/'VeraBd.ttf'
pdfmetrics.registerFont(TTFont('Body',str(normal)));pdfmetrics.registerFont(TTFont('BodyBold',str(bold)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
S=getSampleStyleSheet()
S.add(ParagraphStyle(name='B',fontName='Body',fontSize=10,leading=14,spaceAfter=9,textColor=colors.HexColor('#243247')))
S.add(ParagraphStyle(name='Sm',parent=S['B'],fontSize=8.2,leading=11,spaceAfter=4))
S.add(ParagraphStyle(name='H',fontName='BodyBold',fontSize=20,leading=25,spaceAfter=16,textColor=colors.HexColor('#12374B')))
S.add(ParagraphStyle(name='H2',fontName='BodyBold',fontSize=12,leading=16,spaceBefore=9,spaceAfter=8,keepWithNext=True,textColor=colors.HexColor('#166477')))
S.add(ParagraphStyle(name='T',fontName='BodyBold',fontSize=30,leading=36,spaceAfter=20,textColor=colors.HexColor('#12374B')))
S.add(ParagraphStyle(name='CodeES',fontName='Courier',fontSize=7.2,leading=9.7,spaceAfter=10))
story=[];md=[]
def p(t,style='B'):
 story.append(Paragraph(html.escape(str(t)).replace('\n','<br/>'),S[style]));md.append(str(t)+'\n')
def h(t):p(t,'H');md[-1]='# '+md[-1]
def sub(t):p(t,'H2');md[-1]='## '+md[-1]
def page():story.append(PageBreak())
def table(head,rows,widths):
 def markup(v):
  escaped=html.escape(str(v))
  return '<link href="'+escaped+'" color="#166477">'+escaped+'</link>' if str(v).startswith('https://') else escaped
 values=[[Paragraph(markup(v),S['Sm']) for v in row] for row in [head]+rows]
 t=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E3EFF3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#68A2AF')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#D8E1E6')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,10))
 md.extend(['| '+' | '.join(head)+' |','|'+'|'.join(['---']*len(head))+'|']+['| '+' | '.join(str(v).replace('|','/').replace('\n','; ') for v in row)+' |' for row in rows]+[''])
def code(text):
 lines=[]
 for line in text.splitlines():lines.extend(textwrap.wrap(line,width=99,replace_whitespace=False,drop_whitespace=False) or [''])
 story.append(Preformatted('\n'.join(lines),S['CodeES']));md.append('```sql\n'+text+'\n```\n')
def csvrows(file):
 with (P/file).open(encoding='utf-8',newline='') as f:return list(csv.reader(f))

story.append(Spacer(1,65));p('BASES DE DATOS I · PROYECTO FINAL','H2')
p('Registro de producción\ny paros de envasado','T')
p('Vinilos y témperas · Migración del XLSM original','H2')
story.append(Spacer(1,25));p('Daniel Felipe Chica Giraldo\nErick Noel Delgado Serna','H2');p('Revisión local: 17 de noviembre de 2026')
story.append(Spacer(1,25))
table(['Componente','Resultado'],[['Migración','9.460 filas en staging, 9.459 filas normalizadas y una fila auxiliar sin fecha conservada.'],['Conciliación','118 controles satisfactorios contra los datos y tablas dinámicas del Excel.'],['Repositorio',url]],[120,360])
p('Los resultados principales del informe provienen del histórico real. Los datos sintéticos permanecen identificados como DEMO y no se mezclan con REAL.','Sm')
page();h('1. Problema y propuesta')
p('El archivo de Excel concentra la captura, el histórico y los indicadores. Las operarias diligencian el formato hora a hora, producción remite los formatos y mantenimiento los transcribe. Después se presentan resultados mensuales. Esta estructura dificulta seguir el origen de una cifra y modificar los catálogos sin afectar fórmulas.')
p('Diseñamos una base relacional que separa catálogos, registros, causas de paro y participaciones. Cada fila conserva su hoja y número de origen. Las consultas calculan los indicadores sin depender de las macros del libro.')
sub('Qué se implementó')
p('La entrega incluye el esquema SQLite, catálogos, carga del histórico, cuatro vistas, nueve índices explícitos, doce consultas y pruebas de restricciones. El constructor SQL completo permite reproducir la base sin instalar bibliotecas de extracción. También se incluye el modelo editable, un informe PDF y una presentación de resultados.')
table(['Conjunto','Contenido'],[['Histórico principal','8.208 filas de Base De Datos. Alimenta los indicadores.'],['Histórico auxiliar','1.252 filas de Base de datos de Sub codigos; 1.251 con fecha se normalizan y una se conserva solo en staging.'],['Demostración','72 registros sintéticos independientes para probar restricciones y detalle horario.']],[140,340])
p('No se exige una meta de pacas para calcular el indicador temporal original. Los datos históricos no contienen esa meta en su tabla principal; por eso el cumplimiento de una meta de volumen permanece desconocido en lugar de inventarse.')

page();h('2. Revisión de los insumos')
table(['Fuente','Revisión efectuada'],[['XLSM original','21 hojas, dos tablas de datos históricos, catálogos, formularios y ocho tablas dinámicas. Lectura de valores guardados y definiciones XML; no se ejecutó VBA ni se sobrescribió el original.'],['Procedimiento','Documento de siete páginas identificado internamente como P-MTO-22 V1. Describe flujo de captura, campos, causas y reportes. Su archivo tiene un código distinto en el nombre.'],['Exportación PDF','Sirvió para la primera inspección. Sus errores visibles de exportación no se trasladaron como valores del XLSM, cuyos minutos y conversiones pudieron comprobarse.']],[135,345])
sub('Hallazgos que afectan el diseño')
table(['Hallazgo','Decisión'],[['Columnas para códigos 01...18','Convertir las duraciones en filas de paro.'],['Filas adicionales sin pacas u horas','Conservar NULL y no copiar las cantidades anteriores.'],['Hoja auxiliar de subcódigos','Mantener su ámbito AUXILIAR y no sumarla a la principal.'],['Código 18 contradictorio','Conservar sus ocho usos y minutos; bloquear nuevas capturas con ese código mientras no se apruebe su descripción.'],['Subcódigos históricos diferentes','Conservar identificadores locales, sin asumir que 4.x equivale automáticamente a 5.x.'],['Nombres y observaciones libres','Seudonimizar personas y reservar observaciones en la copia pública.']],[155,325])

page();h('3. Diagnóstico del Excel')
p('La presencia de columnas separadas por causa hace que añadir un código implique modificar la estructura y sus fórmulas. Las conversiones a horas y el total son datos derivados. Si se sumaran con los minutos originales se duplicaría el tiempo. Las nuevas tablas conservan minutos como medida base y calculan las conversiones cuando se necesitan.')
table(['Riesgo','Efecto','Respuesta'],[['Actualizar descripciones repetidas','Textos diferentes para el mismo código','Catálogo único por clave.'],['Sumar la producción en cada detalle','Pacas contadas varias veces','No propagar medidas; una fila mantiene solo sus valores originales.'],['Sumar las dos hojas históricas','Repetición de tiempos que se relacionan con los mismos períodos','Separar fuentes y ámbitos.'],['Borrar filas repetidas sin regla','Cambio de los totales históricos','Conservar 42 repeticiones y registrarlas como hallazgo.'],['Interpretar vacíos como cero','Aparente certeza donde falta información','Preservar NULL y usar NULLIF para divisiones.']],[115,180,185])
sub('Calidad observada')
p('La fuente tiene 401 filas con horas en cero, 45 con paros que superan el tiempo base de su propia fila y una con pacas pero sin horas. Estos hallazgos se conservan para reproducir el libro. No se corrigen arbitrariamente para que los porcentajes queden dentro de un rango esperado.')

page();h('4. Entidades y reglas de negocio')
table(['Entidad','Regla principal'],[['Fuente','Identifica hoja, huella del archivo y ámbito. PRINCIPAL y AUXILIAR permanecen separados.'],['Máquina, turno y referencia','Son catálogos. Máquina es obligatoria; en histórico turno y referencia pueden ser desconocidos.'],['Persona','Representa un texto de identidad mediante alias. No fusiona abreviaturas sin verificación.'],['Registro de producción','Conserva una fila de origen con las cantidades y tiempos presentes. Una fila de detalle puede tener pacas u horas NULL.'],['Paro y subcódigo','Cada duración positiva pertenece a un registro y a un código. Una FK compuesta exige que la subcausa exista dentro de ese código.'],['Intervención','Resuelve la relación N:M entre personas y paros cuando hay personal registrado.'],['Producción por hora','Soporta capturas futuras y pruebas. No se generó detalle horario ficticio para el histórico.'],['Staging e incidencia','Guardan la trazabilidad completa y sus observaciones de calidad.']],[140,340])
p('En nuevas capturas, la base exige tiempo positivo, cantidad conocida, turno y referencia. Los triggers controlan el presupuesto de paro y el detalle horario. En registros HISTORICO se permiten anomalías de origen, que quedan documentadas en incidencia. Esta distinción permite migrar fielmente y controlar las capturas nuevas.')

page();h('5. Modelo conceptual')
d=Drawing(480,420)
boxes={'MAQUINA':(0,365,105,30),'TURNO':(125,365,105,30),'PERSONA':(250,365,105,30),'REFERENCIA':(375,365,105,30),'FUENTE':(0,265,105,35),'REGISTRO':(165,265,165,40),'CODIGO':(375,265,105,35),'STAGING':(0,150,105,35),'PARO':(185,150,125,35),'SUBCODIGO':(375,150,105,35),'HORA':(0,30,105,35),'INTERVENCION':(185,30,125,35),'INCIDENCIA':(375,30,105,35)}
edges=[([(52,365),(52,333),(190,333),(190,305)],'1','0..N'),([(177,365),(218,305)],'0..1','0..N'),([(302,365),(275,305)],'0..1','0..N'),([(427,365),(427,330),(306,330),(306,305)],'0..1','0..N'),([(105,282),(165,282)],'1','0..N'),([(52,265),(52,185)],'1','0..N'),([(247,265),(247,185)],'1','0..N'),([(375,282),(350,282),(350,170),(310,170)],'1','0..N'),([(427,265),(427,185)],'1','0..N'),([(375,165),(310,165)],'0..1','0..N'),([(247,150),(247,65)],'1','0..N'),([(165,280),(135,280),(135,100),(52,100),(52,65)],'1','0..N'),([(105,166),(150,166),(150,92),(427,92),(427,65)],'1','0..N')]
edges[9]=([(375,165),(340,165),(340,155),(310,155)],'0..1','0..N')
for points,a,b in edges:
 for q,z in zip(points,points[1:]):d.add(Line(*q,*z,strokeColor=colors.HexColor('#7194A0'),strokeWidth=.8))
 x,y=points[0]
 leftside=any(x==bx and by<y<by+bh for bx,by,bw,bh in boxes.values())
 d.add(String(x-25 if leftside else x+3,y+5 if leftside else y-12,a,fontName='Body',fontSize=7))
 x,y=points[-1]
 leftside=any(x==bx and by<y<by+bh for bx,by,bw,bh in boxes.values())
 d.add(String(x-30 if leftside else x+3,y+5,b,fontName='Body',fontSize=7))
for name,(x,y,w,hh) in boxes.items():
 d.add(Rect(x,y,w,hh,rx=3,fillColor=colors.HexColor('#EDF5F7'),strokeColor=colors.HexColor('#28748A')))
 d.add(String(x+w/2,y+hh/2-3,name,fontName='BodyBold',fontSize=9,textAnchor='middle'))
story.append(d)
p('Esquema conceptual resumido con mínimos y máximos. El archivo docs/modelo.mmd contiene el modelo completo editable en pata de gallo, con sus atributos. Persona también participa en intervención y registro puede tener incidencias, relaciones omitidas del resumen gráfico para facilitar su lectura.','Sm')
table(['Participación','Descripción'],[['1','Relación obligatoria del detalle hacia su padre.'],['0..1','Relación opcional, importante para los faltantes del histórico.'],['0..N','Un padre puede existir sin detalles o tener varios.'],['N:M','Personas y paros se relacionan mediante intervención.']],[115,365])

page();h('6. Modelo relacional y normalización')
p('Cada entidad tiene PK. El origen y la combinación (fuente_id,fila_fuente) son claves alternativas de registro. La PK de subcodigo_paro es (codigo,subcodigo); intervención usa (paro_id,persona_id) y producción_hora usa (registro_id,hora_relativa). Todas las FK tienen DELETE RESTRICT y UPDATE CASCADE.')
sub('Primera forma normal')
p('Las celdas numéricas de la tabla ancha ya pueden ser atómicas; el problema es la estructura repetida de causas y su mantenimiento. Las columnas de causas se convierten en filas de paro con la misma estructura. Las participaciones se almacenan una por persona. Agregar una causa no exige una nueva columna ni una fórmula por máquina.')
sub('Segunda forma normal')
p('La producción y los tiempos base dependen de la fila de registro, no de cada causa. Se separan de los detalles de paro. En intervención, el rol corresponde a la combinación paro/persona. En producción_hora, la cantidad depende del registro y del bloque horario completo.')
p('Ejemplo didáctico: una fila S tiene 8 pacas, 60 minutos base y dos causas con 5 y 3 minutos. Si la relación intermedia tiene clave (fila,código), fila determina por sí sola las pacas y la base: existe dependencia parcial. La cabecera final conserva una sola vez las 8 pacas y los 60 minutos; paro conserva los dos detalles. La clave real de paro es id porque puede haber más de un detalle por causa.')
sub('Tercera forma normal')
p('Los nombres de máquina, turno, referencia y causa se almacenan en sus catálogos. Registro determina los identificadores, y esos identificadores determinan sus descripciones. Separarlos elimina dependencias transitivas y permite corregir una descripción una sola vez.')
table(['Dependencia','Ubicación'],[['registro_id determina fecha, asignaciones y medidas','registro_produccion'],['codigo determina descripción','codigo_paro'],['(codigo,subcodigo) determina descripción local','subcodigo_paro'],['(paro,persona) determina rol','intervencion'],['(registro,hora) determina pacas','produccion_hora']],[290,190])
p('El núcleo del negocio llega a 3FN. Staging conserva JSON de la fuente por trazabilidad y no pretende sustituir al modelo normalizado. Los reportes leen las tablas normalizadas. Mes, año y porcentajes se derivan de fecha y medidas base, sin almacenarse redundantemente.')
p('Se declara una redundancia técnica deliberada: origen materializa huella, fuente y fila, además de la clave alternativa fuente/fila. Incidencia también conserva la procedencia cuando falta un registro operativo. La capa de staging y auditoría conserva el origen para conciliar y no se presenta como un modelo operativo sin redundancia. El desarrollo paso a paso está en docs/NORMALIZACION.md.')

page();h('7. Diccionario de datos')
p('INTEGER almacena enteros y REAL admite fracciones. Los minutos usan REAL porque la fuente contiene 0,1 minuto. TEXT no impone longitud fija: los límites se controlan con CHECK. Fecha tiene 10 caracteres, horas 5 y código principal 2. Todas las FK usan DELETE RESTRICT y UPDATE CASCADE. Las restricciones de fila y triggers se incluyen en el anexo SQL.')
for t in D:
 sub(t['name']+' · '+t['desc'])
 for x in t['columns']:
  left=f"{x['name']}\n{x['type']} · NULL: {'Sí' if x['nullable'] else 'No'}\nLongitud: {x['length']}\nDefault: {x['default']}"
  table(['Columna y almacenamiento','Negocio y restricciones'],[[left,x['business']+'\n'+x['constraints']]],[155,325])

page();h('8. Implementación e integridad')
table(['Mecanismo','Uso'],[['PK y UNIQUE','Identifican filas y evitan importar otra vez el mismo origen. La clave de staging es fuente/fila.'],['FK compuesta','Impide relacionar un subcódigo que no existe dentro del código seleccionado.'],['CHECK y NOT NULL','Controlan fechas, categorías, duraciones positivas y campos mínimos. Los faltantes históricos se admiten de manera explícita.'],['DEFAULT','Asigna estado CAPTURA, clase REAL y la fuente de capturas nuevas; la demo y la importación asignan sus fuentes explícitamente.'],['Triggers','Controlan sumas de paros y cantidades horarias en nuevas capturas. Impiden usar código 18 sin aprobar en captura nueva.'],['Transacciones','La reconstrucción y las cargas revisadas terminan completas o revierten ante un error.']],[135,345])
p('No se bloquea la importación de una fila histórica solo porque sus paros superen el tiempo de esa fila: eso impediría conservar la fuente. La excepción se identifica con estado HISTORICO y se registra en incidencia. No implica que la anomalía sea correcta ni que esté aprobada para futuras capturas.')
sub('Índices')
table(['Índice','Propósito'],[['Máquina/fecha','Productividad mensual y comparativos.'],['Fecha/turno','Filtros de período y desempeño por turno.'],['Registro/código','Preagregación de paros sin multiplicar producción.'],['Código/subcódigo','Detalle de causas y catálogo compuesto.'],['Referencia y operario','Vínculos y comprobaciones de integridad.'],['Persona en intervención','Consulta de participaciones.'],['Fuente/fila e incidencia/registro','Trazabilidad y diagnóstico de importación.']],[160,320])
p('El script de creación define nueve índices explícitos. Las PK y UNIQUE añaden sus índices propios. La utilidad se relaciona con filtros y relaciones concretas; no se presume que todos los planes mejoren por el simple número de índices.')

page();h('9. Fórmula original e indicadores')
p('La definición está en el XML de la caché de la tabla dinámica del libro:')
code("('Horas trabajadas'-'Tiempo de Paro')/'Horas trabajadas'")
table(['Indicador','Cálculo'],[['Productividad temporal (%)','100 × (SUM(minutos_base) - SUM(minutos_paro)) / SUM(minutos_base). Reproduce la fórmula original agregada.'],['Participación de causa (%)','Minutos del código / minutos de todos los paros del período × 100.'],['Impacto sobre tiempo base (%)','Minutos del código / minutos base del período × 100. Es el denominador usado en el resumen de códigos del libro.'],['Participación de subcausa (%)','Minutos de la subcausa / minutos de su propio código × 100.'],['Cambio entre años','Porcentaje 2025 menos porcentaje 2024 en puntos porcentuales, usando enero-marzo de cada año.'],['Cumplimiento de meta de volumen','Pacas / pacas ideales × 100 cuando la meta existe. No se calcula en histórico porque su meta no está registrada.']],[150,330])
p('La productividad temporal no usa factores 1,1 o 1,16 del formulario. Esos factores aparecen en otros cálculos de captura, pero no en el campo calculado de la tabla dinámica que se concilió. Diferenciar las fórmulas evita reproducir un indicador distinto con el mismo nombre.')
p('No se promedian los porcentajes fila a fila. Se agregan sus tiempos y se divide al final. NULLIF evita dividir entre cero. Se incluyen los tiempos de las filas de detalle sin copiar sus horas, tal como hace el agregado original.')

page();h('10. Migración y conciliación')
table(['Fuente','Pacas','Minutos base','Minutos de paro'],[['Principal','378.778','2.283.801','506.979,1'],['Auxiliar','0 registradas','0 registrados','37.211'],['Tratamiento','Separada','Separada','No se añade la auxiliar a la principal']],[95,120,130,135])
p('La carga pasa todas las filas por staging, manteniendo nulos, ceros, hoja y fila. De las 9.460 filas, una auxiliar sin fecha no se convierte en registro operativo; permanece en staging con una incidencia. Las otras 9.459 se normalizan. Se generan 17.656 detalles de paro históricos y 2.723 participaciones; los 288 paros y 72 participaciones de la demo se mantienen separados.')
p('El origen combina la huella SHA-256 del archivo con la hoja y fila. No se deduplican 42 filas exactamente repetidas, porque no existe autorización ni una clave de negocio que demuestre que deban borrarse. Los paros se expresan en minutos una sola vez; las conversiones a horas no se vuelven a sumar.')
sub('Controles independientes')
p('La verificación compara el JSONL con staging y los valores normalizados, controla sumas por hoja y código, y contrasta resultados guardados en seis tablas dinámicas del XLSM. En total pasan 118 controles, incluidas las doce consultas. La diferencia en los porcentajes contrastados está por debajo de 0,000001 en escala de fracción.')
table(['Control','Resultado'],[['Filas en staging','9.460, coincidencia fila a fila.'],['Filas históricas normalizadas','9.459; una sin fecha queda registrada aparte.'],['Conversiones y total de paro','Sin diferencias entre valores originales y cachés comprobadas.'],['TD_prodMaq y TD_prodAño','12 meses de 2024 para Vinilos_2 reproducidos.'],['Códigos y subcódigos','Participaciones y agrupaciones coinciden con los controles del libro.']],[195,285])

page();h('11. Resultados reales')
sub('Comparativo enero-marzo')
rows=csvrows('evidencias/Q02.csv')
table(['Máquina','2024 (%)','2025 (%)','Diferencia (pp)'],[[r[0],f'{float(r[1]):.2f}',f'{float(r[2]):.2f}',f'{float(r[3]):+.2f}'] for r in rows[1:]],[135,110,110,125])
p('Vinilos_1 aumenta 9,36 puntos porcentuales; Vinilos_2 disminuye 3,25; Vinilos_3, 8,16; y Vinilos_4, 4,40. Son diferencias del indicador temporal registrado, no una prueba de causalidad. La cantidad de minutos base y la mezcla de referencias son diferentes entre años.')
p('Se comparan los registros disponibles de enero-marzo de cada año. El histórico de 2025 llega al 28 de marzo y no permite afirmar que sea un cierre completo del trimestre. Los minutos de cada período se muestran también en la consulta Q02.')
sub('Principales causas de paro en 2025 disponible')
rows=csvrows('evidencias/Q03.csv')
table(['Código','Minutos','% del paro','% del tiempo base'],[[r[0],r[2],f'{float(r[3]):.2f}',f'{float(r[4]):.2f}'] for r in rows[1:5]],[95,120,130,135])
p('En enero-marzo de 2025, alimentación y aseo (16), limpieza por derrame (06) y ajuste operativo (05) concentran la mayor participación de los tiempos registrados. La participación en paros y el impacto sobre tiempo base usan denominadores distintos.')

page();h('12. Consultas y comprobaciones')
table(['Consulta','Pregunta de negocio'],[[f'Q{i:02}',title] for i,(title,q) in enumerate(Q,1)],[55,425])
p('El conjunto utiliza INNER JOIN y LEFT JOIN, agregaciones, GROUP BY, HAVING, subconsultas correlacionadas, NOT EXISTS, CTE y funciones de ventana. Los rangos son semiabiertos: fecha mayor o igual a desde y menor que hasta. Q01 usa meses completos y Q02 fija los períodos comparables.')
p('Las pruebas rechazaron correctamente 18 casos inválidos. También comprobaron INSERT, UPDATE y DELETE válidos, duración decimal, integridad referencial y detalle horario de la demo. El constructor SQL único reconstruye la base y el script de sustentación no deja mutaciones. La carga revisada revierte ante una FK inválida y rechaza reimportaciones por origen repetido.')

page();h('13. Calidad, privacidad y límites')
table(['Hallazgo','Casos','Tratamiento'],[['Horas cero','401','Conservar 0 y no dividir entre cero.'],['Paros mayores que la base de su fila','45','Conservar y marcar; no borrar tiempos.'],['Repeticiones originales','42','Conservar todas sus filas.'],['Código 18 ambiguo','8','Conservar minutos y bloquear nuevas capturas no aprobadas.'],['Pacas sin horas','1','Conservar pacas y horas NULL.'],['Auxiliar sin fecha','1','Conservar solo en staging.']],[235,55,190])
p('Hay 498 incidencias que pueden coincidir en una misma fila; no son necesariamente 498 filas distintas. Las tablas de calidad permiten identificarlas por hoja/fila. El nombre “REAL” indica origen histórico, no certificación de exactitud de la captura.')
p('Los nombres se reemplazan por alias HMAC. La clave privada no se incluye en Git ni en los archivos entregados. No se publican observaciones libres ni el XLSM con los nombres. Las variantes de nombres se conservan como identidades de texto distintas si no hay evidencia de que sean la misma persona.')
p('No hay horarios de inicio y fin de cada falla, por lo que no se calculan MTBF ni MTTR. El detalle horario real no está persistido en las dos tablas históricas y no se inventó. Las capturas nuevas tienen estructura para registrar esos bloques, pero los indicadores históricos se limitan a las medidas disponibles.')

page();h('14. Repositorio y sustentación')
p('La revisión inicial del repositorio público al 17 de noviembre de 2026 encontró dos commits bajo la cuenta dan1elcg1raldo000. Las correcciones posteriores se identifican como preparación técnica automatizada de Codex. Ese trabajo no acredita contribuciones personales de ambos integrantes ni sustituye el requisito de evolución y participación del enunciado. No se reconstruyen autorías ni fechas ficticias.')
p('La entrega incluye .gitignore, una regla .gitattributes para conservar el SHA-256 de la fuente JSONL y un flujo de verificación en .github/workflows/verificar.yml. La versión publicada debe comprobarse en GitHub contra la versión local que se muestra en la sustentación.')
p('El flujo de GitHub Actions reconstruye y audita SQLite y genera el informe. Su estado se consulta en la sección Actions del repositorio; la existencia del archivo YAML no basta para afirmar que pasó. Las cinco verificaciones del proyecto se ejecutaron satisfactoriamente en este PC. DEMOSTRAR.cmd ejecuta una reconstrucción temporal y Q12 sin editar código.')
sub('Reproducción')
code('python scripts/reconstruir.py --salida base_nueva.sqlite\npython scripts/verificar.py base_nueva.sqlite\npython scripts/verificar_historico.py base_nueva.sqlite\npython scripts/verificar_carga.py base_nueva.sqlite\npython scripts/verificar_sql_completo.py')
p('La base_proyecto.sqlite ya está construida y se abre directamente en DBeaver. sql/08_sustentacion.sql contiene consultas sin parámetros pendientes. El modelo editable y el PDF permiten explicar la normalización y las relaciones. La presentación resume el modelo, la migración y los resultados del histórico.')

page();h('15. Fuentes y trazabilidad')
p('SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm. Libro original entregado por el usuario. Fuentes principales: Base De Datos, A9:BF8217; Base de datos de Sub codigos, A8:S1260; catálogos y tablas dinámicas. Se revisaron metadatos de las 21 hojas y definiciones de ocho tablas dinámicas.')
p('P-MTO-21-V1_Registro_paros_de_produccion_actividad.pdf. Se identifica internamente como P-MTO-22 V1, siete páginas, vigencia 14/05/2025. Campos y códigos en pp. 1-3; reportes en pp. 4-6.')
p('Enunciado pegado por el usuario. Requisitos de diseño, normalización, implementación, consultas, privacidad, repositorio y sustentación. Parte de sus cantidades mínimas aparece omitida en el texto recibido; la entrega incluye 3FN, nueve índices, cuatro vistas y doce consultas.')
sub('SHA-256 del XLSM utilizado');code(M['sha256_xlsm'])
p('Los controles de cada hoja, fórmulas originales, resultados y diferencias están en evidencias/inspeccion_xlsm.json y evidencias/conciliacion_historica.json. La fuente pública es una derivación seudonimizada; su hash está registrado para verificar que la reconstrucción usa exactamente la misma extracción.')

page();h('Anexo A. Consultas SQL completas')
p('Parámetros: clase REAL, desde 2025-01-01 y hasta 2025-04-01. El script de sustentación ya incluye esos valores. Q02 usa fechas explícitas para enero-marzo de ambos años.')
for i,(title,q) in enumerate(Q,1):
 if i in [5,9]:page();h('Anexo A. Consultas (continuación)')
 sub(f'Q{i:02}. {title}')
 code(re.sub(r'\s+(FROM|LEFT JOIN|JOIN|WHERE|GROUP BY|HAVING|ORDER BY|SELECT)\s+',lambda m:'\n'+m[1]+' ',q))
page();h('Anexo B. Esquema y vistas')
p('DDL del esquema ejecutado. Los datos completos se incluyen en sql/00_PROYECTO_COMPLETO.sql y la reconstrucción con JSONL está en scripts/reconstruir.py.')
code((P/'sql/01_esquema.sql').read_text(encoding='utf-8'))
sub('Vistas');code((P/'sql/04_vistas.sql').read_text(encoding='utf-8'))
sub('DML reversible');code((P/'sql/06_dml.sql').read_text(encoding='utf-8'))

def footer(canvas,doc):
 w,hh=A4;canvas.setStrokeColor(colors.HexColor('#B7CBD2'));canvas.line(48,45,w-48,45)
 canvas.setFillColor(colors.HexColor('#627884'));canvas.setFont('Body',8)
 canvas.drawString(48,31,'BDI · Chica / Delgado · Histórico del XLSM');canvas.drawRightString(w-48,31,str(doc.page))
 if doc.page>1:canvas.setFont('Body',7.5);canvas.drawString(48,hh-30,'VINILOS Y TÉMPERAS / MODELO, MIGRACIÓN Y CONCILIACIÓN')
dest=P/'BDI_ProyectoFinal_Chica_Delgado.pdf'
doc=SimpleDocTemplate(str(dest),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=53,bottomMargin=59,title='Registro de producción y paros - Histórico XLSM',author='Daniel Felipe Chica Giraldo; Erick Noel Delgado Serna')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(P/'docs/INFORME.md').write_text('\n\n'.join(md),encoding='utf-8',newline='\n')
print(dest)

