# Migración del XLSM y conciliación

La extracción leyó las 21 hojas y las definiciones XML de las tablas dinámicas sin
ejecutar VBA ni guardar cambios sobre el original. El histórico se obtiene de:

| Hoja | Filas de origen | Filas normalizadas | Tratamiento |
|---|---:|---:|---|
| Base De Datos | 8.208 | 8.208 | Fuente principal de indicadores |
| Base de datos de Sub codigos | 1.252 | 1.251 | Auxiliar separada, sin sumarla a la principal |
| Total | 9.460 | 9.459 | Una fila sin fecha queda solo en staging |

Cada fila conserva fuente, número de fila y origen único. Se descomponen las
columnas de código 01...18 en filas de paro, sin sumar de nuevo sus conversiones
a horas. Las columnas de horas y el total guardado coinciden con los minutos de
origen: no se encontraron diferencias en esos controles.

No se copian pacas ni horas hacia las filas adicionales de subcódigo. La ausencia
se conserva como NULL. Tampoco se unen registros por parecido ni se eliminan las
42 repeticiones exactas observadas en la fuente. Las referencias sin registrar y
los turnos desconocidos permanecen NULL.

Los códigos históricos antiguos se conservan como identificadores locales del
código donde fueron capturados. Por ejemplo, un subcódigo 4.x dentro de la columna
de ajuste operativo queda bajo el código 05. No se afirma equivalencia automática
con 5.x. El código 18 conserva sus minutos, con descripción en revisión y bloqueo
para nuevas capturas hasta su aprobación.

## Totales de la fuente principal

- Pacas: 378.778.
- Minutos base: 2.283.801.
- Minutos de paro: 506.979,1.

La hoja auxiliar contiene 37.211 minutos adicionales que se conservan como datos
de esa hoja, sin añadirlos a los indicadores de la fuente principal.

## Evidencia

`verificar_historico.py` compara fila a fila la fuente seudonimizada con staging,
los valores normalizados, las sumas de cada hoja/código y resultados originales
de seis tablas dinámicas. Pasa 118 controles, incluyendo las 12 consultas.
`evidencias/conciliacion_historica.json` contiene los valores y diferencias.

## Calidad conservada

Se registran 498 incidencias: 401 filas con cero horas, 45 con paro mayor que el
tiempo de su propia fila, 42 repeticiones originales, 8 usos del código 18 ambiguo,
una fila con pacas pero sin horas y una auxiliar sin fecha. Son observaciones que
pueden superponerse; no equivalen a 498 filas distintas ni se descartan del histórico.

## Protección de personas

Los textos de personas se sustituyen por alias HMAC con una clave privada que no
se publica. No se presupone que dos abreviaturas distintas identifiquen a la misma
persona. Las observaciones libres se reservan, conservando su presencia mediante
un marcador. La conciliación cuantitativa no depende de esos textos.

## Reproducción

La base se reconstruye con la fuente seudonimizada incluida, sin abrir el Excel y
sin instalar openpyxl. Repetir la extracción del XLSM es una operación opcional de
análisis, requiere openpyxl y una clave privada local; no es necesario para usar
el proyecto entregado.
