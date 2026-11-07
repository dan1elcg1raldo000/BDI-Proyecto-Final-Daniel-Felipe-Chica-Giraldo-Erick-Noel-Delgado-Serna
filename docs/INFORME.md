BASES DE DATOS I · PROYECTO FINAL


Registro de producción
y paros de envasado


Vinilos y témperas · Migración del XLSM original


Daniel Felipe Chica Giraldo
Erick Noel Delgado Serna


6 de noviembre de 2026


| Componente | Resultado |

|---|---|

| Migración | 9.460 filas en staging, 9.459 filas normalizadas y una fila auxiliar sin fecha conservada. |

| Conciliación | 118 controles satisfactorios contra los datos y tablas dinámicas del Excel. |

| Repositorio | Repositorio Git incluido; el enlace se incorpora al generar el informe en GitHub. |



Los resultados principales del informe provienen del histórico real. Los datos sintéticos permanecen identificados como DEMO y no se mezclan con REAL.


# 1. Problema y propuesta


El archivo de Excel concentra la captura, el histórico y los indicadores. Las operarias diligencian el formato hora a hora, producción remite los formatos y mantenimiento los transcribe. Después se presentan resultados mensuales. Esta estructura dificulta seguir el origen de una cifra y modificar los catálogos sin afectar fórmulas.


Diseñamos una base relacional que separa catálogos, registros, causas de paro y participaciones. Cada fila conserva su hoja y número de origen. Las consultas calculan los indicadores sin depender de las macros del libro.


## Qué se implementó


La entrega incluye el esquema SQLite, catálogos, carga del histórico, cuatro vistas, nueve índices explícitos, doce consultas y pruebas de restricciones. El constructor SQL completo permite reproducir la base sin instalar bibliotecas de extracción. También se incluye el modelo editable, un informe PDF y una presentación de resultados.


| Conjunto | Contenido |

|---|---|

| Histórico principal | 8.208 filas de Base De Datos. Alimenta los indicadores. |

| Histórico auxiliar | 1.252 filas de Base de datos de Sub codigos; 1.251 con fecha se normalizan y una se conserva solo en staging. |

| Demostración | 72 registros sintéticos independientes para probar restricciones y detalle horario. |



No se exige una meta de pacas para calcular el indicador temporal original. Los datos históricos no contienen esa meta en su tabla principal; por eso el cumplimiento de una meta de volumen permanece desconocido en lugar de inventarse.


# 2. Revisión de los insumos


| Fuente | Revisión efectuada |

|---|---|

| XLSM original | 21 hojas, dos tablas de datos históricos, catálogos, formularios y ocho tablas dinámicas. Lectura de valores guardados y definiciones XML; no se ejecutó VBA ni se sobrescribió el original. |

| Procedimiento | Documento de siete páginas identificado internamente como P-MTO-22 V1. Describe flujo de captura, campos, causas y reportes. Su archivo tiene un código distinto en el nombre. |

| Exportación PDF | Sirvió para la primera inspección. Sus errores visibles de exportación no se trasladaron como valores del XLSM, cuyos minutos y conversiones pudieron comprobarse. |



## Hallazgos que afectan el diseño


| Hallazgo | Decisión |

|---|---|

| Columnas para códigos 01...18 | Convertir las duraciones en filas de paro. |

| Filas adicionales sin pacas u horas | Conservar NULL y no copiar las cantidades anteriores. |

| Hoja auxiliar de subcódigos | Mantener su ámbito AUXILIAR y no sumarla a la principal. |

| Código 18 contradictorio | Conservar sus ocho usos y minutos; bloquear nuevas capturas con ese código mientras no se apruebe su descripción. |

| Subcódigos históricos diferentes | Conservar identificadores locales, sin asumir que 4.x equivale automáticamente a 5.x. |

| Nombres y observaciones libres | Seudonimizar personas y reservar observaciones en la copia pública. |



# 3. Diagnóstico del Excel


La presencia de columnas separadas por causa hace que añadir un código implique modificar la estructura y sus fórmulas. Las conversiones a horas y el total son datos derivados. Si se sumaran con los minutos originales se duplicaría el tiempo. Las nuevas tablas conservan minutos como medida base y calculan las conversiones cuando se necesitan.


| Riesgo | Efecto | Respuesta |

|---|---|---|

| Actualizar descripciones repetidas | Textos diferentes para el mismo código | Catálogo único por clave. |

| Sumar la producción en cada detalle | Pacas contadas varias veces | No propagar medidas; una fila mantiene solo sus valores originales. |

| Sumar las dos hojas históricas | Repetición de tiempos que se relacionan con los mismos períodos | Separar fuentes y ámbitos. |

| Borrar filas repetidas sin regla | Cambio de los totales históricos | Conservar 42 repeticiones y registrarlas como hallazgo. |

| Interpretar vacíos como cero | Aparente certeza donde falta información | Preservar NULL y usar NULLIF para divisiones. |



## Calidad observada


La fuente tiene 401 filas con horas en cero, 45 con paros que superan el tiempo base de su propia fila y una con pacas pero sin horas. Estos hallazgos se conservan para reproducir el libro. No se corrigen arbitrariamente para que los porcentajes queden dentro de un rango esperado.


# 4. Entidades y reglas de negocio


| Entidad | Regla principal |

|---|---|

| Fuente | Identifica hoja, huella del archivo y ámbito. PRINCIPAL y AUXILIAR permanecen separados. |

| Máquina, turno y referencia | Son catálogos. Máquina es obligatoria; en histórico turno y referencia pueden ser desconocidos. |

| Persona | Representa un texto de identidad mediante alias. No fusiona abreviaturas sin verificación. |

| Registro de producción | Conserva una fila de origen con las cantidades y tiempos presentes. Una fila de detalle puede tener pacas u horas NULL. |

| Paro y subcódigo | Cada duración positiva pertenece a un registro y a un código. Una FK compuesta exige que la subcausa exista dentro de ese código. |

| Intervención | Resuelve la relación N:M entre personas y paros cuando hay personal registrado. |

| Producción por hora | Soporta capturas futuras y pruebas. No se generó detalle horario ficticio para el histórico. |

| Staging e incidencia | Guardan la trazabilidad completa y sus observaciones de calidad. |



En nuevas capturas, la base exige tiempo positivo, cantidad conocida, turno y referencia. Los triggers controlan el presupuesto de paro y el detalle horario. En registros HISTORICO se permiten anomalías de origen, que quedan documentadas en incidencia. Esta distinción permite migrar fielmente y controlar las capturas nuevas.


# 5. Modelo conceptual


Esquema conceptual resumido con mínimos y máximos. El archivo docs/modelo.mmd contiene el modelo completo editable en pata de gallo, con sus atributos. Persona también participa en intervención y registro puede tener incidencias, relaciones omitidas del resumen gráfico para facilitar su lectura.


| Participación | Descripción |

|---|---|

| 1 | Relación obligatoria del detalle hacia su padre. |

| 0..1 | Relación opcional, importante para los faltantes del histórico. |

| 0..N | Un padre puede existir sin detalles o tener varios. |

| N:M | Personas y paros se relacionan mediante intervención. |



# 6. Modelo relacional y normalización


Cada entidad tiene PK. El origen y la combinación (fuente_id,fila_fuente) son claves alternativas de registro. La PK de subcodigo_paro es (codigo,subcodigo); intervención usa (paro_id,persona_id) y producción_hora usa (registro_id,hora_relativa). Todas las FK tienen DELETE RESTRICT y UPDATE CASCADE.


## Primera forma normal


Las columnas de causas se convierten en filas de paro con valores individuales. Las participaciones se almacenan una por persona. Agregar una causa no exige una nueva columna ni una fórmula por máquina.


## Segunda forma normal


La producción y los tiempos base dependen de la fila de registro, no de cada causa. Se separan de los detalles de paro. En intervención, el rol corresponde a la combinación paro/persona. En producción_hora, la cantidad depende del registro y del bloque horario completo.


## Tercera forma normal


Los nombres de máquina, turno, referencia y causa se almacenan en sus catálogos. Registro determina los identificadores, y esos identificadores determinan sus descripciones. Separarlos elimina dependencias transitivas y permite corregir una descripción una sola vez.


| Dependencia | Ubicación |

|---|---|

| registro_id determina fecha, asignaciones y medidas | registro_produccion |

| codigo determina descripción | codigo_paro |

| (codigo,subcodigo) determina descripción local | subcodigo_paro |

| (paro,persona) determina rol | intervencion |

| (registro,hora) determina pacas | produccion_hora |



El núcleo del negocio llega a 3FN. Staging conserva JSON de la fuente por trazabilidad y no pretende sustituir al modelo normalizado. Los reportes leen las tablas normalizadas. Mes, año y porcentajes se derivan de fecha y medidas base, sin almacenarse redundantemente.


# 7. Diccionario de datos


INTEGER almacena enteros y REAL admite fracciones. Los minutos usan REAL porque la fuente contiene 0,1 minuto. TEXT no impone longitud fija: los límites se controlan con CHECK. Fecha tiene 10 caracteres, horas 5 y código principal 2. Todas las FK usan DELETE RESTRICT y UPDATE CASCADE. Las restricciones de fila y triggers se incluyen en el anexo SQL.


## fuente · Identifica la hoja y separa el histórico principal, su auxiliar y las capturas nuevas.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| hoja; TEXT · NULL: No; Default: Sin DEFAULT | Nombre único de la hoja o conjunto de captura.; UNIQUE(hoja) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| archivo_sha256; TEXT · NULL: Sí; Default: Sin DEFAULT | Huella del XLSM; NULL en demo/captura.; CHECK(archivo_sha256 IS NULL OR length(archivo_sha256)=64) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| ambito; TEXT · NULL: No; Default: Sin DEFAULT | PRINCIPAL alimenta indicadores; AUXILIAR se conserva aparte; DEMO se filtra por clase.; CHECK(ambito IN ('PRINCIPAL','AUXILIAR','DEMO')) |



## maquina · Línea de envasado.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| nombre; TEXT · NULL: No; Default: Sin DEFAULT | Etiqueta única del catálogo.; UNIQUE(nombre); CHECK(length(nombre) BETWEEN 1 AND 30) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| activa; INTEGER · NULL: No; Default: 1 | Indicador operativo 1/0; no borra referencias históricas.; CHECK(activa IN (0,1)) |



## turno · Horario del turno. Un turno no identificado permanece NULL.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| nombre; TEXT · NULL: No; Default: Sin DEFAULT | Etiqueta única del catálogo.; UNIQUE(nombre); CHECK(length(nombre) BETWEEN 1 AND 40) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| inicio; TEXT · NULL: No; Default: Sin DEFAULT | Inicio HH:MM.; CHECK(length(inicio)=5 AND inicio GLOB '[0-2][0-9]:[0-5][0-9]' AND inicio<'24:00') |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fin; TEXT · NULL: No; Default: Sin DEFAULT | Fin HH:MM, con posible cruce de medianoche.; CHECK(length(fin)=5 AND fin GLOB '[0-2][0-9]:[0-5][0-9]' AND fin<'24:00') |



## persona · Alias HMAC de un texto de persona; no presupone que abreviaturas distintas sean la misma identidad.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| seudonimo; TEXT · NULL: No; Default: Sin DEFAULT | Alias HMAC irreversible sin la clave privada externa.; UNIQUE(seudonimo); CHECK(length(seudonimo) BETWEEN 1 AND 30) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| activa; INTEGER · NULL: No; Default: 1 | Indicador operativo 1/0; no borra referencias históricas.; CHECK(activa IN (0,1)) |



## referencia · Nombre de la presentación tal como figura en el catálogo o la fuente.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| nombre; TEXT · NULL: No; Default: Sin DEFAULT | Etiqueta única del catálogo.; UNIQUE(nombre); CHECK(length(nombre) BETWEEN 1 AND 120) |



## codigo_paro · Causa principal; 18 conserva una denominación histórica pendiente de aclaración.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| codigo; TEXT · NULL: No; Default: Sin DEFAULT | Código principal con dos dígitos.; PK; CHECK(length(codigo)=2 AND codigo GLOB '[0-9][0-9]') |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| descripcion; TEXT · NULL: No; Default: Sin DEFAULT | Descripción única para esa clave de catálogo.; CHECK(length(descripcion) BETWEEN 1 AND 180) |



## subcodigo_paro · Identificador local a su código, incluyendo nomenclaturas históricas sin fusionarlas.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| codigo; TEXT · NULL: No; Default: Sin DEFAULT | Código principal con dos dígitos.; PK compuesta; FK codigo_paro.codigo; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| subcodigo; TEXT · NULL: No; Default: Sin DEFAULT | Identificador local, conservando variantes históricas.; PK compuesta; CHECK(length(subcodigo) BETWEEN 1 AND 15) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| descripcion; TEXT · NULL: No; Default: Sin DEFAULT | Descripción única para esa clave de catálogo.; CHECK(length(descripcion) BETWEEN 1 AND 180) |



## registro_produccion · Fila de producción o detalle con sus valores originales, sin propagar cantidades.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fecha; TEXT · NULL: No; Default: Sin DEFAULT | Fecha registrada en la fuente, ISO AAAA-MM-DD.; CHECK(length(fecha)=10 AND fecha GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(fecha,'+0 days') IS NOT NULL AND date(fecha,'+0 days')=fecha) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| maquina_id; INTEGER · NULL: No; Default: Sin DEFAULT | Línea a la que corresponde la fila.; FK maquina.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| turno_id; INTEGER · NULL: Sí; Default: Sin DEFAULT | Turno identificado; NULL significa desconocido o no aplicable según staging.; FK turno.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| operario_id; INTEGER · NULL: Sí; Default: Sin DEFAULT | Alias de la persona operadora; NULL cuando no se registró.; FK persona.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| referencia_id; INTEGER · NULL: Sí; Default: Sin DEFAULT | Presentación del producto; NULL cuando falta.; FK referencia.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| minutos_base; REAL · NULL: Sí; Default: Sin DEFAULT | Horas trabajadas del Excel multiplicadas por 60, sin rellenar faltantes. Puede ser 0 en histórico.; CHECK(minutos_base IS NULL OR minutos_base BETWEEN 0 AND 1440) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| meta_pacas_hora; REAL · NULL: Sí; Default: Sin DEFAULT | Meta de volumen opcional para captura nueva. La fuente histórica no la contiene.; CHECK(meta_pacas_hora IS NULL OR meta_pacas_hora>0) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| pacas_reales; REAL · NULL: Sí; Default: 0 | Pacas de la fila. NULL se conserva como desconocido, sin copiar datos del registro anterior.; CHECK(pacas_reales IS NULL OR pacas_reales>=0) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| origen; TEXT · NULL: No; Default: Sin DEFAULT | SHA del archivo, fuente y fila; clave idempotente.; UNIQUE(origen); CHECK(length(origen) BETWEEN 1 AND 160) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| clase; TEXT · NULL: No; Default: 'REAL' | REAL para datos del libro o capturas; DEMO para la demostración sintética.; CHECK(clase IN ('REAL','DEMO')) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| creado_en; TEXT · NULL: No; Default: CURRENT_TIMESTAMP | Sello UTC de inserción.; Sin restricción adicional |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fuente_id; INTEGER · NULL: No; Default: 4 | Hoja/conjunto de origen.; FK fuente.id; DELETE RESTRICT; UPDATE CASCADE; UNIQUE(fuente_id,fila_fuente) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fila_fuente; INTEGER · NULL: Sí; Default: Sin DEFAULT | Número de fila en la hoja Excel.; UNIQUE(fuente_id,fila_fuente); CHECK(fila_fuente IS NULL OR fila_fuente>0) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| estado; TEXT · NULL: No; Default: 'CAPTURA' | HISTORICO conserva anomalías; CAPTURA exige campos y presupuesto de tiempos válidos.; CHECK(estado IN ('CAPTURA','HISTORICO')) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| minutos_sin_trabajar; REAL · NULL: Sí; Default: Sin DEFAULT | Horas no trabajadas originales multiplicadas por 60.; CHECK(minutos_sin_trabajar IS NULL OR minutos_sin_trabajar>=0) |



## paro · Tiempo positivo por causa y subcausa de una fila. No equivale a un evento con inicio y fin.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| registro_id; INTEGER · NULL: No; Default: Sin DEFAULT | Fila de producción de la que depende el detalle.; FK registro_produccion.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| codigo; TEXT · NULL: No; Default: Sin DEFAULT | Código principal con dos dígitos.; FK subcodigo_paro.codigo; DELETE RESTRICT; UPDATE CASCADE; FK codigo_paro.codigo; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| subcodigo; TEXT · NULL: Sí; Default: Sin DEFAULT | Identificador local, conservando variantes históricas.; FK subcodigo_paro.subcodigo; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| minutos; REAL · NULL: No; Default: Sin DEFAULT | Duración en minutos, admite el decimal que aparece en la fuente.; CHECK(minutos>0) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| observacion; TEXT · NULL: Sí; Default: Sin DEFAULT | Aclaración de nuevas capturas. Las observaciones originales se reservan por privacidad.; CHECK(observacion IS NULL OR length(observacion)<=500) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| agente; TEXT · NULL: Sí; Default: Sin DEFAULT | Grupo que interviene en el ajuste; independiente de si se conoce una persona.; CHECK(agente IS NULL OR length(agente)<=60) |



## intervencion · Persona y rol asociados al paro de ajuste operativo cuando la fuente registra personal.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| paro_id; INTEGER · NULL: No; Default: Sin DEFAULT | Tiempo de paro al que corresponde una participación.; PK compuesta; FK paro.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| persona_id; INTEGER · NULL: No; Default: Sin DEFAULT | Persona participante mediante alias.; PK compuesta; FK persona.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| rol; TEXT · NULL: No; Default: Sin DEFAULT | Función de esa persona en esa participación.; CHECK(rol IN ('MANTENIMIENTO','OPERACION','CALIDAD','OTRO')) |



## produccion_hora · Detalle horario para capturas nuevas y demostración; no se inventa para el histórico.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| registro_id; INTEGER · NULL: No; Default: Sin DEFAULT | Fila de producción de la que depende el detalle.; PK compuesta; FK registro_produccion.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| hora_relativa; INTEGER · NULL: No; Default: Sin DEFAULT | Bloque horario desde el comienzo del segmento de una captura nueva.; PK compuesta; CHECK(typeof(hora_relativa)='integer' AND hora_relativa BETWEEN 0 AND 23) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| pacas; REAL · NULL: No; Default: Sin DEFAULT | Cantidad del bloque horario.; CHECK(pacas>=0) |



## staging_pdf · Estructura de la extracción PDF anterior. No interviene en los indicadores actuales.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| pagina; INTEGER · NULL: No; Default: Sin DEFAULT | Página de la exportación PDF, para la extracción previa.; UNIQUE(pagina,linea); CHECK(pagina BETWEEN 1 AND 3213) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| linea; INTEGER · NULL: No; Default: Sin DEFAULT | Línea de texto PDF extraída.; UNIQUE(pagina,linea); CHECK(linea>0) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fecha; TEXT · NULL: No; Default: Sin DEFAULT | Fecha registrada en la fuente, ISO AAAA-MM-DD.; Sin restricción adicional |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| maquina; TEXT · NULL: No; Default: Sin DEFAULT | Etiqueta recuperada en la extracción previa.; Sin restricción adicional |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| estado; TEXT · NULL: No; Default: 'PENDIENTE_EXCEL' | Estado de la extracción PDF anterior: PENDIENTE_EXCEL o REVISADO. Esta tabla no alimenta los indicadores del XLSM.; CHECK(estado IN ('PENDIENTE_EXCEL','REVISADO')) |



## staging_xlsm · Fuente seudonimizada íntegra por hoja/fila, usada para conciliación y trazabilidad.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fuente_id; INTEGER · NULL: No; Default: Sin DEFAULT | Hoja/conjunto de origen.; PK compuesta; FK fuente.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fila; INTEGER · NULL: No; Default: Sin DEFAULT | Fila de la hoja que identifica el origen.; PK compuesta; CHECK(fila>0) |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| contenido_json; TEXT · NULL: No; Default: Sin DEFAULT | Contenido seudonimizado de la fila y marcador de repetición, con nulos y ceros originales.; CHECK(json_valid(contenido_json)) |



## incidencia · Observación de calidad vinculada a su fila de origen.


| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| id; INTEGER · NULL: No; Default: Sin DEFAULT | Identificador interno.; PK |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| registro_id; INTEGER · NULL: Sí; Default: Sin DEFAULT | Fila de producción de la que depende el detalle.; FK registro_produccion.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fuente_id; INTEGER · NULL: No; Default: Sin DEFAULT | Hoja/conjunto de origen.; FK staging_xlsm.fuente_id; DELETE RESTRICT; UPDATE CASCADE; FK fuente.id; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| fila; INTEGER · NULL: No; Default: Sin DEFAULT | Fila de la hoja que identifica el origen.; FK staging_xlsm.fila; DELETE RESTRICT; UPDATE CASCADE |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| tipo; TEXT · NULL: No; Default: Sin DEFAULT | Clasificación del hallazgo de calidad.; Sin restricción adicional |



| Columna y almacenamiento | Negocio y restricciones |

|---|---|

| detalle; TEXT · NULL: No; Default: Sin DEFAULT | Explicación sin datos personales.; Sin restricción adicional |



# 8. Implementación e integridad


| Mecanismo | Uso |

|---|---|

| PK y UNIQUE | Identifican filas y evitan importar otra vez el mismo origen. La clave de staging es fuente/fila. |

| FK compuesta | Impide relacionar un subcódigo que no existe dentro del código seleccionado. |

| CHECK y NOT NULL | Controlan fechas, categorías, duraciones positivas y campos mínimos. Los faltantes históricos se admiten de manera explícita. |

| DEFAULT | Asigna estado CAPTURA, clase REAL y la fuente de capturas nuevas; la demo y la importación asignan sus fuentes explícitamente. |

| Triggers | Controlan sumas de paros y cantidades horarias en nuevas capturas. Impiden usar código 18 sin aprobar en captura nueva. |

| Transacciones | La reconstrucción y las cargas revisadas terminan completas o revierten ante un error. |



No se bloquea la importación de una fila histórica solo porque sus paros superen el tiempo de esa fila: eso impediría conservar la fuente. La excepción se identifica con estado HISTORICO y se registra en incidencia. No implica que la anomalía sea correcta ni que esté aprobada para futuras capturas.


## Índices


| Índice | Propósito |

|---|---|

| Máquina/fecha | Productividad mensual y comparativos. |

| Fecha/turno | Filtros de período y desempeño por turno. |

| Registro/código | Preagregación de paros sin multiplicar producción. |

| Código/subcódigo | Detalle de causas y catálogo compuesto. |

| Referencia y operario | Vínculos y comprobaciones de integridad. |

| Persona en intervención | Consulta de participaciones. |

| Fuente/fila e incidencia/registro | Trazabilidad y diagnóstico de importación. |



El script de creación define nueve índices explícitos. Las PK y UNIQUE añaden sus índices propios. La utilidad se relaciona con filtros y relaciones concretas; no se presume que todos los planes mejoren por el simple número de índices.


# 9. Fórmula original e indicadores


La definición está en el XML de la caché de la tabla dinámica del libro:


```sql
('Horas trabajadas'-'Tiempo de Paro')/'Horas trabajadas'
```


| Indicador | Cálculo |

|---|---|

| Productividad temporal (%) | 100 × (SUM(minutos_base) - SUM(minutos_paro)) / SUM(minutos_base). Reproduce la fórmula original agregada. |

| Participación de causa (%) | Minutos del código / minutos de todos los paros del período × 100. |

| Impacto sobre tiempo base (%) | Minutos del código / minutos base del período × 100. Es el denominador usado en el resumen de códigos del libro. |

| Participación de subcausa (%) | Minutos de la subcausa / minutos de su propio código × 100. |

| Cambio entre años | Porcentaje 2025 menos porcentaje 2024 en puntos porcentuales, usando enero-marzo de cada año. |

| Cumplimiento de meta de volumen | Pacas / pacas ideales × 100 cuando la meta existe. No se calcula en histórico porque su meta no está registrada. |



La productividad temporal no usa factores 1,1 o 1,16 del formulario. Esos factores aparecen en otros cálculos de captura, pero no en el campo calculado de la tabla dinámica que se concilió. Diferenciar las fórmulas evita reproducir un indicador distinto con el mismo nombre.


No se promedian los porcentajes fila a fila. Se agregan sus tiempos y se divide al final. NULLIF evita dividir entre cero. Se incluyen los tiempos de las filas de detalle sin copiar sus horas, tal como hace el agregado original.


# 10. Migración y conciliación


| Fuente | Pacas | Minutos base | Minutos de paro |

|---|---|---|---|

| Principal | 378.778 | 2.283.801 | 506.979,1 |

| Auxiliar | 0 registradas | 0 registrados | 37.211 |

| Tratamiento | Separada | Separada | No se añade la auxiliar a la principal |



La carga pasa todas las filas por staging, manteniendo nulos, ceros, hoja y fila. De las 9.460 filas, una auxiliar sin fecha no se convierte en registro operativo; permanece en staging con una incidencia. Las otras 9.459 se normalizan. Se generan 17.656 detalles de paro históricos y 2.723 participaciones; los 288 paros y 72 participaciones de la demo se mantienen separados.


El origen combina la huella SHA-256 del archivo con la hoja y fila. No se deduplican 42 filas exactamente repetidas, porque no existe autorización ni una clave de negocio que demuestre que deban borrarse. Los paros se expresan en minutos una sola vez; las conversiones a horas no se vuelven a sumar.


## Controles independientes


La verificación compara el JSONL con staging y los valores normalizados, controla sumas por hoja y código, y contrasta resultados guardados en seis tablas dinámicas del XLSM. En total pasan 118 controles, incluidas las doce consultas. La diferencia en los porcentajes contrastados está por debajo de 0,000001 en escala de fracción.


| Control | Resultado |

|---|---|

| Filas en staging | 9.460, coincidencia fila a fila. |

| Filas históricas normalizadas | 9.459; una sin fecha queda registrada aparte. |

| Conversiones y total de paro | Sin diferencias entre valores originales y cachés comprobadas. |

| TD_prodMaq y TD_prodAño | 12 meses de 2024 para Vinilos_2 reproducidos. |

| Códigos y subcódigos | Participaciones y agrupaciones coinciden con los controles del libro. |



# 11. Resultados reales


## Comparativo enero-marzo


| Máquina | 2024 (%) | 2025 (%) | Diferencia (pp) |

|---|---|---|---|

| Vinilos_1 | 64.78 | 74.14 | +9.36 |

| Vinilos_2 | 60.40 | 57.15 | -3.25 |

| Vinilos_3 | 75.75 | 67.59 | -8.16 |

| Vinilos_4 | 78.10 | 73.70 | -4.40 |



Vinilos_1 aumenta 9,36 puntos porcentuales; Vinilos_2 disminuye 3,25; Vinilos_3, 8,16; y Vinilos_4, 4,40. Son diferencias del indicador temporal registrado, no una prueba de causalidad. La cantidad de minutos base y la mezcla de referencias son diferentes entre años.


Se comparan los registros disponibles de enero-marzo de cada año. El histórico de 2025 llega al 28 de marzo y no permite afirmar que sea un cierre completo del trimestre. Los minutos de cada período se muestran también en la consulta Q02.


## Principales causas de paro en 2025 disponible


| Código | Minutos | % del paro | % del tiempo base |

|---|---|---|---|

| 16 | 15520.0 | 30.77 | 9.18 |

| 06 | 13682.0 | 27.13 | 8.09 |

| 05 | 11107.0 | 22.02 | 6.57 |

| 07 | 2770.0 | 5.49 | 1.64 |



En enero-marzo de 2025, alimentación y aseo (16), limpieza por derrame (06) y ajuste operativo (05) concentran la mayor participación de los tiempos registrados. La participación en paros y el impacto sobre tiempo base usan denominadores distintos.


# 12. Consultas y comprobaciones


| Consulta | Pregunta de negocio |

|---|---|

| Q01 | Productividad temporal por máquina y mes |

| Q02 | Comparativo enero-marzo 2024 y 2025 |

| Q03 | Participación de códigos de paro y porcentaje sobre tiempo base |

| Q04 | Detalle por subcódigo 01, 03 y 05 |

| Q05 | Comparación de turnos dentro de cada máquina |

| Q06 | Causas que acumulan más de 100 minutos |

| Q07 | Máquinas por debajo de la productividad del conjunto |

| Q08 | Máquinas sin filas en el período |

| Q09 | Participación de agentes en ajustes operativos |

| Q10 | Incidencias de calidad del histórico por tipo |

| Q11 | Pareto de causas de paro |

| Q12 | Conteos y totales por fuente sin mezclar las hojas |



El conjunto utiliza INNER JOIN y LEFT JOIN, agregaciones, GROUP BY, HAVING, subconsultas correlacionadas, NOT EXISTS, CTE y funciones de ventana. Los rangos son semiabiertos: fecha mayor o igual a desde y menor que hasta. Q01 usa meses completos y Q02 fija los períodos comparables.


Las pruebas rechazaron correctamente 17 casos inválidos. También comprobaron INSERT, UPDATE y DELETE válidos, duración decimal, integridad referencial y detalle horario de la demo. El constructor SQL único reconstruye la base y el script de sustentación no deja mutaciones. La carga revisada revierte ante una FK inválida y rechaza reimportaciones por origen repetido.


# 13. Calidad, privacidad y límites


| Hallazgo | Casos | Tratamiento |

|---|---|---|

| Horas cero | 401 | Conservar 0 y no dividir entre cero. |

| Paros mayores que la base de su fila | 45 | Conservar y marcar; no borrar tiempos. |

| Repeticiones originales | 42 | Conservar todas sus filas. |

| Código 18 ambiguo | 8 | Conservar minutos y bloquear nuevas capturas no aprobadas. |

| Pacas sin horas | 1 | Conservar pacas y horas NULL. |

| Auxiliar sin fecha | 1 | Conservar solo en staging. |



Hay 498 incidencias que pueden coincidir en una misma fila; no son necesariamente 498 filas distintas. Las tablas de calidad permiten identificarlas por hoja/fila. El nombre “REAL” indica origen histórico, no certificación de exactitud de la captura.


Los nombres se reemplazan por alias HMAC. La clave privada no se incluye en Git ni en los archivos entregados. No se publican observaciones libres ni el XLSM con los nombres. Las variantes de nombres se conservan como identidades de texto distintas si no hay evidencia de que sean la misma persona.


No hay horarios de inicio y fin de cada falla, por lo que no se calculan MTBF ni MTTR. El detalle horario real no está persistido en las dos tablas históricas y no se inventó. Las capturas nuevas tienen estructura para registrar esos bloques, pero los indicadores históricos se limitan a las medidas disponibles.


# 14. Repositorio y sustentación


El repositorio entregado conserva commits de los cambios efectuados durante la preparación. El autor de esos commits es Codex Automation y las fechas son reales. No se atribuyen contribuciones personales a los integrantes. El historial demuestra la evolución automatizada del proyecto; por sí solo no acredita la participación personal de ambos estudiantes exigida por el enunciado.


El historial Git documenta la evolución del modelo, la extracción de fuentes, la implementación, la conciliación y la actualización de los resultados.


La verificación de GitHub reconstruye la base desde el JSONL seudonimizado, ejecuta restricciones y conciliación y genera este informe con el enlace real del repositorio. La ejecución remota se comprobará después de publicar; las verificaciones incluidas se ejecutaron localmente.


## Reproducción


```sql
python scripts/reconstruir.py --salida base_nueva.sqlite
python scripts/verificar.py base_nueva.sqlite
python scripts/verificar_historico.py base_nueva.sqlite
python scripts/verificar_carga.py base_nueva.sqlite
python scripts/verificar_sql_completo.py
```


La base_proyecto.sqlite ya está construida y se abre directamente en DBeaver. sql/08_sustentacion.sql contiene consultas sin parámetros pendientes. El modelo editable y el PDF permiten explicar la normalización y las relaciones. La presentación resume el modelo, la migración y los resultados del histórico.


# 15. Fuentes y trazabilidad


SEGUIMIENTO TEMPERAS Y VINILOS Actividad.xlsm. Libro original entregado por el usuario. Fuentes principales: Base De Datos, A9:BF8217; Base de datos de Sub codigos, A8:S1260; catálogos y tablas dinámicas. Se revisaron metadatos de las 21 hojas y definiciones de ocho tablas dinámicas.


P-MTO-21-V1_Registro_paros_de_produccion_actividad.pdf. Se identifica internamente como P-MTO-22 V1, siete páginas, vigencia 14/05/2025. Campos y códigos en pp. 1-3; reportes en pp. 4-6.


Enunciado pegado por el usuario. Requisitos de diseño, normalización, implementación, consultas, privacidad, repositorio y sustentación. Parte de sus cantidades mínimas aparece omitida en el texto recibido; la entrega incluye 3FN, nueve índices, cuatro vistas y doce consultas.


## SHA-256 del XLSM utilizado


```sql
c7d7eabbd55844757c2be07bd61efcee9eb5e0b03aaf9fd76b798737a92d5c55
```


Los controles de cada hoja, fórmulas originales, resultados y diferencias están en evidencias/inspeccion_xlsm.json y evidencias/conciliacion_historica.json. La fuente pública es una derivación seudonimizada; su hash está registrado para verificar que la reconstrucción usa exactamente la misma extracción.


# Anexo A. Consultas SQL completas


Parámetros: clase REAL, desde 2025-01-01 y hasta 2025-04-01. El script de sustentación ya incluye esos valores. Q02 usa fechas explícitas para enero-marzo de ambos años.


## Q01. Productividad temporal por máquina y mes


```sql
SELECT m.nombre,v.mes,ROUND(v.productividad_pct,4) productividad_pct,v.minutos_base,v.minutos_paro,v.pacas
FROM v_productividad_mensual v
JOIN maquina m ON m.id=v.maquina_id
WHERE v.clase=:clase AND v.mes>=substr(:desde,1,7) AND v.mes<substr(:hasta,1,7)
ORDER BY m.id,v.mes;
```


## Q02. Comparativo enero-marzo 2024 y 2025


```sql
WITH a AS (SELECT maquina_id,substr(fecha,1,4) anio,SUM(minutos_base) base,SUM(minutos_paro) paros,100.0*(SUM(minutos_base)-SUM(minutos_paro))/NULLIF(SUM(minutos_base),0) pct
FROM v_indicador_segmento
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND ((fecha>='2024-01-01' AND fecha<'2024-04-01') OR (fecha>='2025-01-01' AND fecha<'2025-04-01'))
GROUP BY maquina_id,substr(fecha,1,4))
SELECT m.nombre,ROUND(x.pct,4) pct_2024,ROUND(y.pct,4) pct_2025,ROUND(y.pct-x.pct,4) diferencia_pp,x.base minutos_2024,y.base minutos_2025
FROM maquina m
LEFT JOIN a x ON x.maquina_id=m.id AND x.anio='2024'
LEFT JOIN a y ON y.maquina_id=m.id AND y.anio='2025'
ORDER BY m.id;
```


## Q03. Participación de códigos de paro y porcentaje sobre tiempo base


```sql
WITH p AS (SELECT codigo,SUM(minutos) minutos
FROM v_paros_detalle
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta
GROUP BY codigo)
SELECT c.codigo,c.descripcion,COALESCE(p.minutos,0) minutos,ROUND(100.0*COALESCE(p.minutos,0)/NULLIF((SELECT SUM(minutos)
FROM p),0),4) pct_del_paro,ROUND(100.0*COALESCE(p.minutos,0)/NULLIF((SELECT SUM(minutos_base)
FROM v_indicador_segmento
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta),0),4) pct_base
FROM codigo_paro c
LEFT JOIN p ON p.codigo=c.codigo
ORDER BY minutos DESC;
```


## Q04. Detalle por subcódigo 01, 03 y 05


```sql
WITH d AS (SELECT codigo,COALESCE(subcodigo,'SIN_SUBCODIGO') subcodigo,subcausa,SUM(minutos) minutos
FROM v_paros_detalle
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta AND codigo IN ('01','03','05')
GROUP BY codigo,subcodigo,subcausa)
SELECT d.*,ROUND(100.0*minutos/NULLIF((SELECT SUM(x.minutos)
FROM d x
WHERE x.codigo=d.codigo),0),4) pct_dentro_codigo
FROM d
ORDER BY codigo,minutos DESC;
```


# Anexo A. Consultas (continuación)


## Q05. Comparación de turnos dentro de cada máquina


```sql
SELECT m.nombre maquina,COALESCE(t.nombre,'Sin turno registrado') turno,COUNT(*) filas_fuente,ROUND(100.0*(SUM(v.minutos_base)-SUM(v.minutos_paro))/NULLIF(SUM(v.minutos_base),0),4) productividad_pct,SUM(v.minutos_base) minutos_base
FROM v_indicador_segmento v
JOIN maquina m ON m.id=v.maquina_id
LEFT JOIN turno t ON t.id=v.turno_id
WHERE v.clase=:clase AND v.ambito IN ('PRINCIPAL','DEMO') AND v.fecha>=:desde AND v.fecha<:hasta
GROUP BY m.id,t.id
ORDER BY m.id,t.id;
```


## Q06. Causas que acumulan más de 100 minutos


```sql
SELECT codigo,causa,SUM(minutos) minutos
FROM v_paros_detalle
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta
GROUP BY codigo,causa
HAVING SUM(minutos)>100
ORDER BY minutos DESC;
```


## Q07. Máquinas por debajo de la productividad del conjunto


```sql
WITH d AS (SELECT maquina_id,SUM(minutos_base) base,SUM(minutos_paro) paros
FROM v_indicador_segmento
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta
GROUP BY maquina_id)
SELECT m.nombre,ROUND(100.0*(d.base-d.paros)/NULLIF(d.base,0),4) productividad_pct
FROM d
JOIN maquina m ON m.id=d.maquina_id
WHERE (d.base-d.paros)/NULLIF(d.base,0)<(SELECT (SUM(base)-SUM(paros))/NULLIF(SUM(base),0)
FROM d);
```


## Q08. Máquinas sin filas en el período


```sql
SELECT m.nombre
FROM maquina m
WHERE NOT EXISTS(SELECT 1
FROM v_indicador_segmento v
WHERE v.maquina_id=m.id AND v.clase=:clase AND v.ambito IN ('PRINCIPAL','DEMO') AND v.fecha>=:desde AND v.fecha<:hasta);
```


# Anexo A. Consultas (continuación)


## Q09. Participación de agentes en ajustes operativos


```sql
SELECT COALESCE(p.agente,'Sin agente registrado') agente,COUNT(*) detalles,SUM(p.minutos) minutos
FROM paro p
JOIN v_indicador_segmento r ON r.id=p.registro_id
WHERE p.codigo='05' AND r.clase=:clase AND r.ambito IN ('PRINCIPAL','DEMO') AND r.fecha>=:desde AND r.fecha<:hasta
GROUP BY p.agente
ORDER BY minutos DESC;
```


## Q10. Incidencias de calidad del histórico por tipo


```sql
SELECT f.hoja,i.tipo,COUNT(*) casos
FROM incidencia i
JOIN fuente f ON f.id=i.fuente_id
LEFT JOIN registro_produccion r ON r.id=i.registro_id
WHERE r.id IS NULL OR (r.clase=:clase AND r.fecha>=:desde AND r.fecha<:hasta)
GROUP BY f.hoja,i.tipo
ORDER BY f.hoja,casos DESC;
```


## Q11. Pareto de causas de paro


```sql
WITH c AS (SELECT codigo,SUM(minutos) minutos
FROM v_paros_detalle
WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta
GROUP BY codigo)
SELECT codigo,minutos,ROUND(100.0*SUM(minutos) OVER(ORDER BY minutos DESC,codigo ROWS UNBOUNDED PRECEDING)/NULLIF(SUM(minutos) OVER(),0),4) acumulado_pct
FROM c
ORDER BY minutos DESC,codigo;
```


## Q12. Conteos y totales por fuente sin mezclar las hojas


```sql
SELECT f.hoja,f.ambito,COUNT(r.id) filas,COALESCE(SUM(r.pacas_reales),0) pacas,COALESCE(SUM(r.minutos_base),0) minutos_base,COALESCE(SUM(r.minutos_paro),0) minutos_paro
FROM fuente f
LEFT JOIN v_indicador_segmento r ON r.fuente_id=f.id
GROUP BY f.id
ORDER BY f.id;
```


# Anexo B. Esquema y vistas


DDL del esquema ejecutado. Los datos completos se incluyen en sql/00_PROYECTO_COMPLETO.sql y la reconstrucción con JSONL está en scripts/reconstruir.py.


```sql
PRAGMA foreign_keys = ON;
BEGIN;
CREATE TABLE fuente (
 id INTEGER PRIMARY KEY,
 hoja TEXT NOT NULL UNIQUE,
 archivo_sha256 TEXT CHECK(archivo_sha256 IS NULL OR length(archivo_sha256)=64),
 ambito TEXT NOT NULL CHECK(ambito IN ('PRINCIPAL','AUXILIAR','DEMO'))
);
CREATE TABLE maquina (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) BETWEEN 1 AND 30),
 activa INTEGER NOT NULL DEFAULT 1 CHECK(activa IN (0,1))
);
CREATE TABLE turno (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) BETWEEN 1 AND 40),
 inicio TEXT NOT NULL CHECK(length(inicio)=5 AND inicio GLOB '[0-2][0-9]:[0-5][0-9]' AND inicio<'24:00'),
 fin TEXT NOT NULL CHECK(length(fin)=5 AND fin GLOB '[0-2][0-9]:[0-5][0-9]' AND fin<'24:00')
);
CREATE TABLE persona (
 id INTEGER PRIMARY KEY,
 seudonimo TEXT NOT NULL UNIQUE CHECK(length(seudonimo) BETWEEN 1 AND 30),
 activa INTEGER NOT NULL DEFAULT 1 CHECK(activa IN (0,1))
);
CREATE TABLE referencia (
 id INTEGER PRIMARY KEY,
 nombre TEXT NOT NULL UNIQUE CHECK(length(nombre) BETWEEN 1 AND 120)
);
CREATE TABLE codigo_paro (
 codigo TEXT PRIMARY KEY NOT NULL CHECK(length(codigo)=2 AND codigo GLOB '[0-9][0-9]'),
 descripcion TEXT NOT NULL CHECK(length(descripcion) BETWEEN 1 AND 180)
);
CREATE TABLE subcodigo_paro (
 codigo TEXT NOT NULL REFERENCES codigo_paro(codigo) ON DELETE RESTRICT ON UPDATE CASCADE,
 subcodigo TEXT NOT NULL CHECK(length(subcodigo) BETWEEN 1 AND 15),
 descripcion TEXT NOT NULL CHECK(length(descripcion) BETWEEN 1 AND 180),
 PRIMARY KEY(codigo,subcodigo)
);
-- Grano histórico: una fila de origen, principal o detalle, sin propagar cantidades.
-- La captura nueva exige tiempo, referencia, turno y producción conocidos.
CREATE TABLE registro_produccion (
 id INTEGER PRIMARY KEY,
 fecha TEXT NOT NULL CHECK(length(fecha)=10 AND fecha GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(fecha,'+0 days') IS NOT NULL AND date(fecha,'+0 days')=fecha),
 maquina_id INTEGER NOT NULL REFERENCES maquina(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 turno_id INTEGER REFERENCES turno(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 operario_id INTEGER REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 referencia_id INTEGER REFERENCES referencia(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 minutos_base REAL CHECK(minutos_base IS NULL OR minutos_base BETWEEN 0 AND 1440),
 meta_pacas_hora REAL CHECK(meta_pacas_hora IS NULL OR meta_pacas_hora>0),
 pacas_reales REAL DEFAULT 0 CHECK(pacas_reales IS NULL OR pacas_reales>=0),
 origen TEXT NOT NULL UNIQUE CHECK(length(origen) BETWEEN 1 AND 160),
 clase TEXT NOT NULL DEFAULT 'REAL' CHECK(clase IN ('REAL','DEMO')),
 creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 fuente_id INTEGER NOT NULL DEFAULT 4 REFERENCES fuente(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fila_fuente INTEGER CHECK(fila_fuente IS NULL OR fila_fuente>0),
 estado TEXT NOT NULL DEFAULT 'CAPTURA' CHECK(estado IN ('CAPTURA','HISTORICO')),
 minutos_sin_trabajar REAL CHECK(minutos_sin_trabajar IS NULL OR minutos_sin_trabajar>=0),
 UNIQUE(fuente_id,fila_fuente),
 CHECK(estado='HISTORICO' OR (minutos_base>0 AND minutos_base IS NOT NULL AND pacas_reales IS NOT NULL AND turno_id IS NOT NULL AND referencia_id IS NOT NULL))
);
-- Grano: duración atribuida a una causa/subcausa dentro del segmento. No equivale
-- a un evento individual: el formato histórico no garantiza hora de inicio/fin.
CREATE TABLE paro (
 id INTEGER PRIMARY KEY,
 registro_id INTEGER NOT NULL REFERENCES registro_produccion(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 codigo TEXT NOT NULL REFERENCES codigo_paro(codigo) ON DELETE RESTRICT ON UPDATE CASCADE,
 subcodigo TEXT,
 minutos REAL NOT NULL CHECK(minutos>0),
 observacion TEXT CHECK(observacion IS NULL OR length(observacion)<=500),
 agente TEXT CHECK(agente IS NULL OR length(agente)<=60),
 FOREIGN KEY(codigo,subcodigo) REFERENCES subcodigo_paro(codigo,subcodigo) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE TABLE intervencion (
 paro_id INTEGER NOT NULL REFERENCES paro(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 persona_id INTEGER NOT NULL REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 rol TEXT NOT NULL CHECK(rol IN ('MANTENIMIENTO','OPERACION','CALIDAD','OTRO')),
 PRIMARY KEY(paro_id,persona_id)
);
CREATE TABLE produccion_hora (
 registro_id INTEGER NOT NULL REFERENCES registro_produccion(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 hora_relativa INTEGER NOT NULL CHECK(typeof(hora_relativa)='integer' AND hora_relativa BETWEEN 0 AND 23),
 pacas REAL NOT NULL CHECK(pacas>=0),
 PRIMARY KEY(registro_id,hora_relativa)
);
-- Trazabilidad de la extracción PDF previa; no alimenta los indicadores del XLSM.
CREATE TABLE staging_pdf (
 id INTEGER PRIMARY KEY,
 pagina INTEGER NOT NULL CHECK(pagina BETWEEN 1 AND 3213),
 linea INTEGER NOT NULL CHECK(linea>0),
 fecha TEXT NOT NULL,
 maquina TEXT NOT NULL,
 estado TEXT NOT NULL DEFAULT 'PENDIENTE_EXCEL' CHECK(estado IN ('PENDIENTE_EXCEL','REVISADO')),
 UNIQUE(pagina,linea)
);
CREATE INDEX idx_registro_maquina_fecha ON registro_produccion(maquina_id,fecha);
CREATE INDEX idx_registro_fecha_turno ON registro_produccion(fecha,turno_id);
CREATE INDEX idx_paro_registro_codigo ON paro(registro_id,codigo);
CREATE INDEX idx_paro_subcodigo ON paro(codigo,subcodigo);
CREATE INDEX idx_registro_referencia ON registro_produccion(referencia_id);
CREATE INDEX idx_registro_operario ON registro_produccion(operario_id);
CREATE INDEX idx_intervencion_persona ON intervencion(persona_id);
CREATE TRIGGER codigo_18_nueva_captura BEFORE INSERT ON paro
WHEN NEW.codigo='18' AND (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA'
BEGIN SELECT RAISE(ABORT,'Código 18 pendiente de aprobación para nuevas capturas'); END;
CREATE TRIGGER codigo_18_modificacion_captura BEFORE UPDATE OF codigo,registro_id ON paro
WHEN NEW.codigo='18' AND (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA'
BEGIN SELECT RAISE(ABORT,'Código 18 pendiente de aprobación para nuevas capturas'); END;
CREATE TRIGGER validar_paro_insert BEFORE INSERT ON paro
WHEN (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA' AND NEW.minutos+COALESCE((SELECT SUM(minutos) FROM paro WHERE registro_id=NEW.registro_id),0)
 > (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Los paros superan los minutos programados'); END;
CREATE TRIGGER validar_paro_update BEFORE UPDATE OF minutos,registro_id ON paro
WHEN (SELECT estado FROM registro_produccion WHERE id=NEW.registro_id)='CAPTURA' AND NEW.minutos+COALESCE((SELECT SUM(minutos) FROM paro WHERE registro_id=NEW.registro_id AND id<>OLD.id),0)
 > (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Los paros superan los minutos programados'); END;
CREATE TRIGGER validar_registro_update BEFORE UPDATE OF minutos_base,pacas_reales,estado ON registro_produccion
WHEN NEW.estado='CAPTURA' AND (NEW.minutos_base<COALESCE((SELECT SUM(minutos) FROM paro WHERE registro_id=OLD.id),0)
 OR NEW.pacas_reales<COALESCE((SELECT SUM(pacas) FROM produccion_hora WHERE registro_id=OLD.id),0)
 OR EXISTS(SELECT 1 FROM produccion_hora WHERE registro_id=OLD.id AND hora_relativa*60>=NEW.minutos_base))
BEGIN SELECT RAISE(ABORT,'El segmento es menor que su detalle'); END;
CREATE TRIGGER validar_hora_insert BEFORE INSERT ON produccion_hora
WHEN NEW.pacas+COALESCE((SELECT SUM(pacas) FROM produccion_hora WHERE registro_id=NEW.registro_id),0)
 > (SELECT pacas_reales FROM registro_produccion WHERE id=NEW.registro_id)
 OR NEW.hora_relativa*60 >= (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Detalle horario fuera del segmento'); END;
CREATE TRIGGER validar_hora_update BEFORE UPDATE ON produccion_hora
WHEN NEW.pacas+COALESCE((SELECT SUM(pacas) FROM produccion_hora WHERE registro_id=NEW.registro_id AND NOT(registro_id=OLD.registro_id AND hora_relativa=OLD.hora_relativa)),0)
 > (SELECT pacas_reales FROM registro_produccion WHERE id=NEW.registro_id)
 OR NEW.hora_relativa*60 >= (SELECT minutos_base FROM registro_produccion WHERE id=NEW.registro_id)
BEGIN SELECT RAISE(ABORT,'Detalle horario fuera del segmento'); END;

CREATE TABLE staging_xlsm (
 fuente_id INTEGER NOT NULL REFERENCES fuente(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fila INTEGER NOT NULL CHECK(fila>0),
 contenido_json TEXT NOT NULL CHECK(json_valid(contenido_json)),
 PRIMARY KEY(fuente_id,fila)
);
CREATE TABLE incidencia (
 id INTEGER PRIMARY KEY,
 registro_id INTEGER REFERENCES registro_produccion(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fuente_id INTEGER NOT NULL REFERENCES fuente(id) ON DELETE RESTRICT ON UPDATE CASCADE,
 fila INTEGER NOT NULL,
 tipo TEXT NOT NULL,
 detalle TEXT NOT NULL,
 FOREIGN KEY(fuente_id,fila) REFERENCES staging_xlsm(fuente_id,fila) ON DELETE RESTRICT ON UPDATE CASCADE
);
CREATE INDEX idx_registro_fuente ON registro_produccion(fuente_id,fila_fuente);
CREATE INDEX idx_incidencia_registro ON incidencia(registro_id);

COMMIT;

```


## Vistas


```sql
-- Productividad original: porcentaje del tiempo base que no está registrado como paro.
-- No confundir con cumplimiento de la meta por cantidad, que queda aparte y puede ser NULL.
CREATE VIEW v_indicador_segmento AS
 SELECT r.*, f.ambito,
 r.meta_pacas_hora*r.minutos_base/60.0 AS pacas_ideales,
 COALESCE(p.minutos_paro,0) AS minutos_paro,
 100.0*(r.minutos_base-COALESCE(p.minutos_paro,0))/NULLIF(r.minutos_base,0) AS productividad_pct,
 100.0*r.pacas_reales/NULLIF(r.meta_pacas_hora*r.minutos_base/60.0,0) AS cumplimiento_meta_pct
 FROM registro_produccion r JOIN fuente f ON f.id=r.fuente_id
 LEFT JOIN (SELECT registro_id,SUM(minutos) minutos_paro FROM paro GROUP BY registro_id) p ON p.registro_id=r.id;
CREATE VIEW v_productividad_mensual AS
 SELECT clase,maquina_id,substr(fecha,1,7) mes,SUM(pacas_reales) pacas,
 SUM(minutos_base) minutos_base,SUM(minutos_paro) minutos_paro,
 100.0*(SUM(minutos_base)-SUM(minutos_paro))/NULLIF(SUM(minutos_base),0) productividad_pct
 FROM v_indicador_segmento WHERE ambito IN ('PRINCIPAL','DEMO')
 GROUP BY clase,maquina_id,substr(fecha,1,7);
CREATE VIEW v_paros_detalle AS
 SELECT p.id,p.registro_id,r.fecha,r.clase,f.ambito,r.maquina_id,r.turno_id,
 m.nombre maquina,COALESCE(t.nombre,'Sin turno registrado') turno,
 p.codigo,c.descripcion causa,p.subcodigo,COALESCE(s.descripcion,'Sin especificar') subcausa,p.minutos
 FROM paro p JOIN registro_produccion r ON r.id=p.registro_id
 JOIN fuente f ON f.id=r.fuente_id JOIN maquina m ON m.id=r.maquina_id
 LEFT JOIN turno t ON t.id=r.turno_id JOIN codigo_paro c ON c.codigo=p.codigo
 LEFT JOIN subcodigo_paro s ON s.codigo=p.codigo AND s.subcodigo=p.subcodigo;
CREATE VIEW v_calidad_fuente AS
 SELECT f.hoja,i.tipo,COUNT(*) casos FROM incidencia i JOIN fuente f ON f.id=i.fuente_id
 GROUP BY f.hoja,i.tipo;

```


## DML reversible


```sql
PRAGMA foreign_keys=ON;
-- Ejemplo reversible. Ejecutar después de 01-04. IDs reservados solo para esta demo.
BEGIN;
INSERT INTO persona(id,seudonimo) VALUES(900001,'DEMO-TEMPORAL');
UPDATE persona SET activa=0 WHERE id=900001;
DELETE FROM persona WHERE id=900001;
ROLLBACK;
-- Los casos rechazados se ejecutan aislados en scripts/verificar.py:
-- INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'99',5); -- FK
-- INSERT INTO paro(registro_id,codigo,subcodigo,minutos) VALUES(1,'03','5.2',5); -- FK compuesta
-- UPDATE registro_produccion SET minutos_base=1 WHERE id=1; -- trigger
-- DELETE FROM maquina WHERE id=1; -- RESTRICT

```
