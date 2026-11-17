# Diccionario de datos
SQLite usa afinidades de tipo. INTEGER y REAL no imponen longitud decimal; TEXT tiene longitud variable y los límites de negocio se aplican con CHECK. Las FK usan ON DELETE RESTRICT y ON UPDATE CASCADE. NULL conserva lo desconocido.

## fuente
Identifica la hoja y separa el histórico principal, su auxiliar y las capturas nuevas.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|hoja|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|UNIQUE(hoja)|Nombre único de la hoja o conjunto de captura.|
|archivo_sha256|TEXT|64 caracteres (CHECK)|Sí|Sin DEFAULT|CHECK(archivo_sha256 IS NULL OR length(archivo_sha256)=64)|Huella del XLSM; NULL en demo/captura.|
|ambito|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|CHECK(ambito IN ('PRINCIPAL','AUXILIAR','DEMO'))|PRINCIPAL alimenta indicadores; AUXILIAR se conserva aparte; DEMO se filtra por clase.|

## maquina
Línea de envasado.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|nombre|TEXT|1 a 30 caracteres (CHECK)|No|Sin DEFAULT|UNIQUE(nombre); CHECK(length(nombre) BETWEEN 1 AND 30)|Etiqueta única del catálogo.|
|activa|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|1|CHECK(activa IN (0,1))|Indicador operativo 1/0; no borra referencias históricas.|

## turno
Horario del turno. Un turno no identificado permanece NULL.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|nombre|TEXT|1 a 40 caracteres (CHECK)|No|Sin DEFAULT|UNIQUE(nombre); CHECK(length(nombre) BETWEEN 1 AND 40)|Etiqueta única del catálogo.|
|inicio|TEXT|5 caracteres (CHECK)|No|Sin DEFAULT|CHECK(length(inicio)=5 AND inicio GLOB '[0-2][0-9]:[0-5][0-9]' AND inicio<'24:00')|Inicio HH:MM.|
|fin|TEXT|5 caracteres (CHECK)|No|Sin DEFAULT|CHECK(length(fin)=5 AND fin GLOB '[0-2][0-9]:[0-5][0-9]' AND fin<'24:00')|Fin HH:MM, con posible cruce de medianoche.|

## persona
Alias HMAC de un texto de persona; no presupone que abreviaturas distintas sean la misma identidad.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|seudonimo|TEXT|1 a 30 caracteres (CHECK)|No|Sin DEFAULT|UNIQUE(seudonimo); CHECK(length(seudonimo) BETWEEN 1 AND 30)|Alias HMAC irreversible sin la clave privada externa.|
|activa|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|1|CHECK(activa IN (0,1))|Indicador operativo 1/0; no borra referencias históricas.|

## referencia
Nombre de la presentación tal como figura en el catálogo o la fuente.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|nombre|TEXT|1 a 120 caracteres (CHECK)|No|Sin DEFAULT|UNIQUE(nombre); CHECK(length(nombre) BETWEEN 1 AND 120)|Etiqueta única del catálogo.|

## codigo_paro
Causa principal; 18 conserva una denominación histórica pendiente de aclaración.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|codigo|TEXT|2 caracteres (CHECK)|No|Sin DEFAULT|PK; CHECK(length(codigo)=2 AND codigo GLOB '[0-9][0-9]')|Código principal con dos dígitos.|
|descripcion|TEXT|1 a 180 caracteres (CHECK)|No|Sin DEFAULT|CHECK(length(descripcion) BETWEEN 1 AND 180)|Descripción única para esa clave de catálogo.|

## subcodigo_paro
Identificador local a su código, incluyendo nomenclaturas históricas sin fusionarlas.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|codigo|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|PK compuesta; FK codigo_paro.codigo; DELETE RESTRICT; UPDATE CASCADE|Código principal con dos dígitos.|
|subcodigo|TEXT|1 a 15 caracteres (CHECK)|No|Sin DEFAULT|PK compuesta; CHECK(length(subcodigo) BETWEEN 1 AND 15)|Identificador local, conservando variantes históricas.|
|descripcion|TEXT|1 a 180 caracteres (CHECK)|No|Sin DEFAULT|CHECK(length(descripcion) BETWEEN 1 AND 180)|Descripción única para esa clave de catálogo.|

## registro_produccion
Fila de producción o detalle con sus valores originales, sin propagar cantidades.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|fecha|TEXT|10 caracteres (CHECK)|No|Sin DEFAULT|CHECK(length(fecha)=10 AND fecha GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]' AND date(fecha,'+0 days') IS NOT NULL AND date(fecha,'+0 days')=fecha)|Fecha registrada en la fuente, ISO AAAA-MM-DD.|
|maquina_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|FK maquina.id; DELETE RESTRICT; UPDATE CASCADE|Línea a la que corresponde la fila.|
|turno_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|Sí|Sin DEFAULT|FK turno.id; DELETE RESTRICT; UPDATE CASCADE|Turno identificado; NULL significa desconocido o no aplicable según staging.|
|operario_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|Sí|Sin DEFAULT|FK persona.id; DELETE RESTRICT; UPDATE CASCADE|Alias de la persona operadora; NULL cuando no se registró.|
|referencia_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|Sí|Sin DEFAULT|FK referencia.id; DELETE RESTRICT; UPDATE CASCADE|Presentación del producto; NULL cuando falta.|
|minutos_base|REAL|Punto flotante de 64 bits; no tiene escala decimal fija|Sí|Sin DEFAULT|CHECK(minutos_base IS NULL OR minutos_base BETWEEN 0 AND 1440)|Horas trabajadas del Excel multiplicadas por 60, sin rellenar faltantes. Puede ser 0 en histórico.|
|meta_pacas_hora|REAL|Punto flotante de 64 bits; no tiene escala decimal fija|Sí|Sin DEFAULT|CHECK(meta_pacas_hora IS NULL OR meta_pacas_hora>0)|Meta de volumen opcional para captura nueva. La fuente histórica no la contiene.|
|pacas_reales|REAL|Punto flotante de 64 bits; no tiene escala decimal fija|Sí|0|CHECK(pacas_reales IS NULL OR pacas_reales>=0)|Pacas de la fila. NULL se conserva como desconocido, sin copiar datos del registro anterior.|
|origen|TEXT|1 a 160 caracteres (CHECK)|No|Sin DEFAULT|UNIQUE(origen); CHECK(length(origen) BETWEEN 1 AND 160)|SHA del archivo, fuente y fila; clave idempotente.|
|clase|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|'REAL'|CHECK(clase IN ('REAL','DEMO'))|REAL para datos del libro o capturas; DEMO para la demostración sintética.|
|creado_en|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|CURRENT_TIMESTAMP|Sin restricción adicional|Sello UTC de inserción.|
|fuente_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|4|FK fuente.id; DELETE RESTRICT; UPDATE CASCADE; UNIQUE(fuente_id,fila_fuente)|Hoja/conjunto de origen.|
|fila_fuente|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|Sí|Sin DEFAULT|UNIQUE(fuente_id,fila_fuente); CHECK(fila_fuente IS NULL OR fila_fuente>0)|Número de fila en la hoja Excel.|
|estado|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|'CAPTURA'|CHECK(estado IN ('CAPTURA','HISTORICO'))|HISTORICO conserva anomalías; CAPTURA exige campos y presupuesto de tiempos válidos.|
|minutos_sin_trabajar|REAL|Punto flotante de 64 bits; no tiene escala decimal fija|Sí|Sin DEFAULT|CHECK(minutos_sin_trabajar IS NULL OR minutos_sin_trabajar>=0)|Horas no trabajadas originales multiplicadas por 60.|

## paro
Tiempo positivo por causa y subcausa de una fila. No equivale a un evento con inicio y fin.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|registro_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|FK registro_produccion.id; DELETE RESTRICT; UPDATE CASCADE|Fila de producción de la que depende el detalle.|
|codigo|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|FK subcodigo_paro.codigo; DELETE RESTRICT; UPDATE CASCADE; FK codigo_paro.codigo; DELETE RESTRICT; UPDATE CASCADE|Código principal con dos dígitos.|
|subcodigo|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|Sí|Sin DEFAULT|FK subcodigo_paro.subcodigo; DELETE RESTRICT; UPDATE CASCADE|Identificador local, conservando variantes históricas.|
|minutos|REAL|Punto flotante de 64 bits; no tiene escala decimal fija|No|Sin DEFAULT|CHECK(minutos>0)|Duración en minutos, admite el decimal que aparece en la fuente.|
|observacion|TEXT|Hasta 500 caracteres (CHECK)|Sí|Sin DEFAULT|CHECK(observacion IS NULL OR length(observacion)<=500)|Aclaración de nuevas capturas. Las observaciones originales se reservan por privacidad.|
|agente|TEXT|Hasta 60 caracteres (CHECK)|Sí|Sin DEFAULT|CHECK(agente IS NULL OR length(agente)<=60)|Grupo que interviene en el ajuste; independiente de si se conoce una persona.|

## intervencion
Persona y rol asociados al paro de ajuste operativo cuando la fuente registra personal.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|paro_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK compuesta; FK paro.id; DELETE RESTRICT; UPDATE CASCADE|Tiempo de paro al que corresponde una participación.|
|persona_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK compuesta; FK persona.id; DELETE RESTRICT; UPDATE CASCADE|Persona participante mediante alias.|
|rol|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|CHECK(rol IN ('MANTENIMIENTO','OPERACION','CALIDAD','OTRO'))|Función de esa persona en esa participación.|

## produccion_hora
Detalle horario para capturas nuevas y demostración; no se inventa para el histórico.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|registro_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK compuesta; FK registro_produccion.id; DELETE RESTRICT; UPDATE CASCADE|Fila de producción de la que depende el detalle.|
|hora_relativa|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK compuesta; CHECK(typeof(hora_relativa)='integer' AND hora_relativa BETWEEN 0 AND 23)|Bloque horario desde el comienzo del segmento de una captura nueva.|
|pacas|REAL|Punto flotante de 64 bits; no tiene escala decimal fija|No|Sin DEFAULT|CHECK(pacas>=0)|Cantidad del bloque horario.|

## staging_pdf
Estructura de la extracción PDF anterior. No interviene en los indicadores actuales.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|pagina|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|UNIQUE(pagina,linea); CHECK(pagina BETWEEN 1 AND 3213)|Página de la exportación PDF, para la extracción previa.|
|linea|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|UNIQUE(pagina,linea); CHECK(linea>0)|Línea de texto PDF extraída.|
|fecha|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|Sin restricción adicional|Fecha registrada en la fuente, ISO AAAA-MM-DD.|
|maquina|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|Sin restricción adicional|Etiqueta recuperada en la extracción previa.|
|estado|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|'PENDIENTE_EXCEL'|CHECK(estado IN ('PENDIENTE_EXCEL','REVISADO'))|Estado de la extracción PDF anterior: PENDIENTE_EXCEL o REVISADO. Esta tabla no alimenta los indicadores del XLSM.|

## staging_xlsm
Fuente seudonimizada íntegra por hoja/fila, usada para conciliación y trazabilidad.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|fuente_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK compuesta; FK fuente.id; DELETE RESTRICT; UPDATE CASCADE|Hoja/conjunto de origen.|
|fila|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK compuesta; CHECK(fila>0)|Fila de la hoja que identifica el origen.|
|contenido_json|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|CHECK(json_valid(contenido_json))|Contenido seudonimizado de la fila y marcador de repetición, con nulos y ceros originales.|

## incidencia
Observación de calidad vinculada a su fila de origen.

|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|
|---|---|---|---|---|---|---|
|id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|PK|Identificador interno.|
|registro_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|Sí|Sin DEFAULT|FK registro_produccion.id; DELETE RESTRICT; UPDATE CASCADE|Fila de producción de la que depende el detalle.|
|fuente_id|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|FK staging_xlsm.fuente_id; DELETE RESTRICT; UPDATE CASCADE; FK fuente.id; DELETE RESTRICT; UPDATE CASCADE|Hoja/conjunto de origen.|
|fila|INTEGER|Entero con signo de hasta 64 bits; no tiene longitud decimal fija|No|Sin DEFAULT|FK staging_xlsm.fila; DELETE RESTRICT; UPDATE CASCADE|Fila de la hoja que identifica el origen.|
|tipo|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|Sin restricción adicional|Clasificación del hallazgo de calidad.|
|detalle|TEXT|Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor|No|Sin DEFAULT|Sin restricción adicional|Explicación sin datos personales.|
