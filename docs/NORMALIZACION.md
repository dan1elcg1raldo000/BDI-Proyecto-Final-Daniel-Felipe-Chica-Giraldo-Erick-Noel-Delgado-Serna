# Del Excel a tercera forma normal

## Grano y dependencias de la fuente

La tabla principal tiene una fila de origen con fecha, máquina, turno, persona, referencia, pacas, horas y columnas de minutos para los códigos 01 a 18. La auxiliar contiene detalles adicionales y se conserva separada. Una fila no equivale necesariamente a un turno completo ni a una falla individual con inicio y fin.

Ejemplo didáctico, sin datos personales reales: la fila S contiene máquina M, turno T, 8 pacas, 60 minutos base, 5 minutos de causa 01 y 3 minutos de causa 05. El resultado debe seguir teniendo 8 pacas y 60 minutos base, con dos detalles de paro. No son 16 pacas ni 120 minutos.

## 1FN: valores individuales y causas como filas

Las celdas numéricas de la tabla ancha ya pueden ser atómicas. El problema de las columnas causa_01...causa_18 es su estructura repetida y su escasa extensibilidad; no basta afirmar que toda tabla ancha viola 1FN. La transformación representa cada causa con la misma estructura de atributos y separa las participaciones de personas.

| Fila | Código | Minutos | Pacas | Base |
|---|---|---:|---:|---:|
| S | 01 | 5 | 8 | 60 |
| S | 05 | 3 | 8 | 60 |

Esta relación intermedia ilustra el riesgo de repetir la cabecera al descomponer las causas. No es una tabla materializada ni el diseño final.

## 2FN: eliminar dependencias de una parte de la clave

En esa relación intermedia, la clave del ejemplo es (fila, código), mientras que `fila -> fecha, máquina, turno, pacas, base`. Las cantidades dependen solo de fila. Al separar la cabecera se elimina esa dependencia parcial y la duplicación de producción al sumar los detalles.

| Tabla final | Clave | Dependencia y resultado |
|---|---|---|
| registro_produccion | id; origen alternativo único | Una cabecera S con 8 pacas y 60 minutos base |
| paro | id | Cada fila identifica una atribución de minutos a una causa/subcausa |
| intervencion | (paro_id, persona_id) | El rol pertenece a la participación completa |
| produccion_hora | (registro_id, hora_relativa) | Las pacas pertenecen al bloque horario de un registro |

La clave (fila, código) solo corresponde al ejemplo con una atribución por causa. En el modelo real puede haber varios detalles por causa; por eso paro usa id. El detalle horario real no se inventa cuando no está presente en las tablas históricas.

## 3FN: eliminar dependencias transitivas de descripciones

En una cabecera extendida, `registro_id -> maquina_id -> nombre_maquina`. Guardar el nombre junto a cada registro produciría anomalías de actualización. El nombre pasa a maquina; el registro conserva su FK. Se aplica la misma separación a turno, persona, referencia y causas.

| Determinante | Atributos dependientes | Ubicación |
|---|---|---|
| maquina.id | nombre, activa | maquina |
| turno.id | nombre, inicio, fin | turno |
| codigo_paro.codigo | descripcion | codigo_paro |
| (codigo, subcodigo) | descripcion local | subcodigo_paro |
| registro_produccion.id | fecha, asignaciones, medidas, procedencia | registro_produccion |
| paro.id | registro, causa, subcausa, minutos, observación, agente | paro |

Un subcódigo es local a su código; su descripción depende de la pareja completa. La FK compuesta evita aceptar una subcausa bajo otra causa. La nulabilidad del subcódigo permite una causa conocida cuyo detalle no fue informado.

## Anomalías que se eliminan

- Actualización: modificar una descripción de máquina o causa una sola vez en su catálogo.
- Inserción: crear un catálogo sin inventar una fila de producción.
- Borrado: eliminar un detalle no elimina el catálogo. RESTRICT impide borrar padres utilizados.
- Agregación: sumar la producción de la cabecera sin multiplicarla por la cantidad de paros. Las vistas preagregan los paros por registro antes de unirlos.

## Redundancias intencionales y límites de la afirmación 3FN

El núcleo de operación separa dependencias y catálogos hasta 3FN. Las tablas de staging son un área de auditoría y conservan la fuente; no se presentan como tablas operativas normalizadas. El JSON contiene valores y campos derivados originales para poder conciliar, no para alimentar directamente los indicadores.

`origen` materializa un identificador de procedencia construido con huella, fuente y fila, además de la pareja fuente/fila. Es una redundancia técnica deliberada para trazabilidad y detección de reimportación. Incidencia conserva fuente/fila aunque su registro operativo pueda ser NULL. Esas decisiones se declaran explícitamente; no se afirma que toda la capa de auditoría carezca de redundancia.

Mes, año, minutos de paro totales y porcentajes operativos se calculan en las vistas. Las observaciones originales de calidad permanecen en HISTORICO y las reglas más estrictas controlan CAPTURA.
