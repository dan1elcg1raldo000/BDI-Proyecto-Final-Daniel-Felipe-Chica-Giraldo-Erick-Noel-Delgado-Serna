# Guion oral de Daniel y Erick

Recorrido de unos 10-12 minutos, ajustable al tiempo que conceda el profesor. El soporte principal es el informe, el modelo, DBeaver y GitHub. Los números siguientes son diez momentos de exposición y no una verificación de las diapositivas de Google Slides.

## 1. Daniel: presentación y objetivo

«Somos Daniel Felipe Chica Giraldo y Erick Noel Delgado Serna. El proyecto transforma el histórico de producción y paros de cuatro líneas de vinilos en una base relacional PostgreSQL. La finalidad es conservar la información de origen y reproducir indicadores con consultas verificables.»

Mostrar la portada del PDF y el enlace al repositorio.

## 2. Daniel: problema y diagnóstico

«Las operarias registran producción por hora y paros en un formato físico. Producción remite los formatos a mantenimiento, que los transcribe al Excel. El libro mezcla datos, formularios, cálculos y reportes. Tiene columnas repetidas para las causas y una hoja auxiliar que no se puede sumar sin analizar su significado. El procedimiento se identifica internamente como P-MTO-22 V1, aunque el nombre del archivo dice P-MTO-21.»

«El diagnóstico también encontró nulos, horas cero, repeticiones y paros mayores que el tiempo de su fila. Conservar el histórico no significa declarar correctas esas anomalías: quedan documentadas.»

## 3. Daniel: modelo y normalización

«El núcleo tiene siete catálogos y cuatro tablas operativas. Registro de producción es la cabecera; paro contiene los detalles de minutos; intervención resuelve la relación entre paros y personas; producción por hora conserva el detalle cuando existe. Hay tres tablas adicionales de soporte y auditoría.»

«En un ejemplo, una cabecera tiene 8 pacas y dos causas de paro. Al separar las causas no se deben convertir en 16 pacas. La cabecera evita repetir esas medidas. En 2FN se eliminan dependencias de una parte de una clave compuesta. En 3FN se separan las descripciones: registro determina máquina y máquina determina su nombre. El nombre se guarda una sola vez en el catálogo.»

Mostrar `docs/MODELO.md` y el ejemplo de `docs/NORMALIZACION.md`.

## 4. Daniel: llaves y restricciones

«Las PK identifican filas. Las FK impiden referencias inexistentes. La pareja código/subcódigo forma una FK compuesta porque una subcausa solo es válida dentro de su causa. RESTRICT protege los registros históricos frente a borrados de sus catálogos; CASCADE propaga cambios de identificador. UNIQUE protege el origen de una reimportación; CHECK, NOT NULL y DEFAULT completan las reglas de fila.»

«PostgreSQL aplica las llaves foráneas declaradas. Las restricciones se comprueban en el servidor, no se activan con PRAGMA. La clave compuesta exige que código y subcódigo pertenezcan a la misma causa.»

## 5. Daniel: triggers

«Los triggers controlan reglas que consultan otras filas: la suma de paros no debe superar la base de una captura y el detalle horario no puede exceder su producción. El código 18 tiene una denominación histórica ambigua: se conserva al migrar y se bloquea en nuevas capturas. Se controla insertar, modificar y convertir un histórico a captura.»

«HISTORICO permite conservar incidencias originales; CAPTURA aplica los controles para nuevos registros. Ese estado es una decisión de importación, no una autorización para corregir datos sin evidencia.»

Transición: «Erick explicará cómo se conservan y verifican los datos al cargarlos.»

## 6. Erick: ETL y protección de personas

«La extracción opcional lee valores guardados del XLSM con openpyxl, sin ejecutar VBA. Los nombres se sustituyen por alias HMAC con una clave privada que no se publica. La fuente pública es un JSONL seudonimizado. La entrega PostgreSQL incluye un SQL completo construido desde ese JSONL. Para regenerarlo se usa un área temporal SQLite con Python estándar; la carga final, las restricciones y las consultas se ejecutan en PostgreSQL. No se necesita el archivo privado ni ejecutar macros.»

«Cada fila conserva fuente y número original. Todas pasan por staging antes de poblar las tablas operativas. Los minutos se cargan una sola vez; no se suman de nuevo las columnas convertidas a horas.»

## 7. Erick: conciliación

«Son 9.460 filas en staging y 9.459 normalizadas: una fila auxiliar sin fecha se conserva solo en staging. La hoja principal aporta 8.208 filas, 378.778 pacas, 2.283.801 minutos base y 506.979,1 minutos de paro. La auxiliar aporta 1.251 filas normalizadas y 37.211 minutos que permanecen separados. Las 72 filas de demostración también se identifican aparte.»

«Los 118 controles concilian filas, sumas, códigos y tablas dinámicas. Las 498 incidencias son observaciones que pueden coincidir en una misma fila. No equivalen necesariamente a 498 filas distintas.»

## 8. Erick: demostración reproducible

En DBeaver, ejecutar por bloques `postgresql/07_sustentacion.sql`. Para demostrar la reconstrucción, usar una base PostgreSQL nueva y ejecutar `postgresql/00_PROYECTO_COMPLETO.sql`. La carga no modifica otra base ya existente.

«Aquí la base se reconstruyó en PostgreSQL con los archivos del repositorio. El catálogo muestra las tablas, vistas y restricciones; las FK están validadas. Q12 separa las fuentes y permite comprobar las cifras sin mezclar la demostración.»

## 9. Erick: vistas y consultas

«Las cuatro vistas reutilizan la lógica de indicadores. Las doce consultas cubren productividad por máquina y mes, comparación anual, participación de causas, subcausas, turnos, Pareto y calidad. Usan INNER y LEFT JOIN, agregaciones, HAVING, subconsultas y rangos de fechas.»

«La productividad temporal es 100 por la diferencia entre minutos base y paro, dividida por los minutos base. Se agregan las medidas y se divide al final; no se promedian porcentajes de filas. El porcentaje de una causa sobre los paros y su porcentaje sobre el tiempo base tienen denominadores diferentes.»

Mostrar Q01, Q03 y Q12 en `sql/08_sustentacion.sql`. Q02 compara enero-marzo de ambos años; 2025 llega al 28 de marzo y no es un trimestre completo.

## 10. Cierre conjunto

Daniel: «El modelo separa catálogos, producción y detalles y controla las nuevas capturas.»

Erick: «La migración mantiene la trazabilidad y las consultas reproducen los indicadores disponibles. La entrega permite reconstruir y auditar la base desde los archivos públicos.»

## Respuestas orientativas para cinco preguntas difíciles

1. **¿Por qué separar una tabla con una PK artificial no basta para llegar a 3FN?** Porque las dependencias funcionales y claves candidatas importan. Una columna id no elimina la dependencia transitiva entre máquina y nombre ni la dependencia parcial de una medida respecto a la clave de una relación intermedia. Hay que separar esos atributos y justificar el grano.
2. **¿Por qué no usar una FK independiente al código y otra al subcódigo?** Porque que ambos existan por separado no demuestra que formen una pareja válida. La FK compuesta comprueba la pareja. Si el subcódigo es NULL, el detalle es desconocido y la FK compuesta de SQLite no exige esa pareja; la FK al código sigue comprobándose.
3. **¿Por qué triggers y por qué no rechazar todo el histórico anómalo?** Un CHECK valida una fila y no puede contener la subconsulta necesaria para sumar sus paros. El trigger consulta el conjunto. Rechazar el histórico por una anomalía conocida perdería evidencia: se conserva con estado HISTORICO e incidencia y se controla CAPTURA.
4. **¿Cómo demuestran una migración íntegra si cambian los nombres?** Se separa fidelidad cuantitativa de tratamiento de identidad. SHA-256 identifica el archivo original; el JSONL tiene su propia huella; staging conserva la fila seudonimizada; se concilian todas las cantidades y reportes. HMAC es seudonimización con secreto, no una afirmación de anonimato absoluto.
5. **¿Cómo adaptar Q03 a una máquina?** Aplicando el mismo filtro de máquina tanto al conjunto de paros como al denominador de minutos base. Filtrar solo el numerador daría una razón entre poblaciones distintas. Para cambiar períodos se usa fecha >= inicio y fecha < fin; Q01 exige meses completos y Q02 tiene períodos propios explícitos.

Estas respuestas son material de práctica. No son evidencia de un ensayo oral realizado por los estudiantes.
