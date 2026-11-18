# Guía de sustentación

Daniel Felipe Chica Giraldo y Erick Noel Delgado Serna. Revisión PostgreSQL: 18/11/2026. El encabezado de Classroom exige PostgreSQL o MySQL.

## Orden para mostrar al profesor

1. PDF, portada y secciones 1-4: problema, diagnóstico del XLSM y reglas del procedimiento P-MTO-22 V1. El nombre del archivo dice P-MTO-21, pero su encabezado interno dice P-MTO-22.
2. PDF, sección 5, y `docs/modelo.mmd`: entidades, atributos, cardinalidades y participación. Hay 7 catálogos, 4 tablas operativas y 3 tablas de soporte (14 en total).
3. PDF, sección 6: transformación a 1FN, 2FN y 3FN. Explicar una dependencia funcional concreta en cada paso.
4. PDF, secciones 7-8: diccionario, llaves, políticas RESTRICT/CASCADE, índices y triggers.
5. DBeaver: conectarse a `POSTGRES_DESPUES` (base `bdi_proyecto`). Mostrar tablas, vistas y diagrama ER de la conexión.
6. DBeaver: abrir `postgresql/07_sustentacion.sql`. Ejecutar una sentencia con Ctrl+Enter o el script con Alt+X. Los parámetros ya tienen valores; no hay que rellenar `:clase`, `:desde` ni `:hasta`.
7. Mostrar `SELECT version(), current_database();` y el control de restricciones FK no validadas del guion (cero filas). PostgreSQL aplica las FK sin PRAGMA. Mostrar después la prueba de rechazo y su transacción reversible.
8. Ejecutar Q12: las hojas PRINCIPAL, AUXILIAR y DEMO permanecen separadas. Ejecutar Q01 o Q03 y modificar el rango de fechas si lo pide el profesor.
9. GitHub: mostrar estructura y cómo reproducir. Distinguir el historial inicial de las correcciones técnicas automatizadas posteriores; no afirmar aportes personales no acreditados.

La consigna recibida limita la sustentación a DBeaver, GitHub, la herramienta de modelado y el PDF. Usar esos elementos como recorrido principal. Las diapositivas son material auxiliar, sujeto a lo que permita el profesor.

## Cifras que deben explicar ambos

| Medida | Resultado | Interpretación |
|---|---:|---|
| Filas en staging | 9.460 | 8.208 principales y 1.252 auxiliares |
| Filas históricas normalizadas | 9.459 | Una auxiliar sin fecha permanece solo en staging |
| Pacas de la hoja principal | 378.778 | No sumar DEMO ni copiar a la auxiliar |
| Minutos base principales | 2.283.801 | Horas originales multiplicadas por 60 |
| Minutos de paro principales | 506.979,1 | Una sola unidad de tiempo, sin duplicar conversiones |
| Minutos de paro auxiliares | 37.211 | Se conservan aparte |
| Restricciones rechazadas correctamente | 18 | Incluye el cambio de HISTORICO a CAPTURA con código 18 |
| Consultas y controles históricos | 12 y 118 | Ver `evidencias/` |

La productividad temporal es `100 * (SUM(base)-SUM(paros))/SUM(base)`. No promediar porcentajes fila a fila. No confundir ese indicador con cumplimiento de una meta de pacas.

## Reparto sugerido por contenido

Daniel explica el problema, las anomalías del Excel, el modelo, las formas normales y las restricciones. Erick explica la extracción, staging, carga, conciliación, vistas y consultas. Ambos deben poder ejecutar y modificar cualquier consulta.

## Cinco preguntas para ensayar

1. ¿Qué dependencia parcial elimina 2FN en una tabla con clave compuesta? Usen `intervencion(paro_id,persona_id)` o `produccion_hora(registro_id,hora_relativa)`, y distingan ese caso de una dependencia transitiva eliminada en 3FN.
2. ¿Por qué una FK compuesta `(codigo,subcodigo)` evita un error que dos FK independientes no evitarían? ¿Qué ocurre cuando el subcódigo es NULL? ¿Por qué se usa RESTRICT para borrar?
3. ¿Por qué un CHECK no basta para limitar la suma de todos los paros? Expliquen los triggers INSERT/UPDATE y la excepción HISTORICO. ¿Cómo se impide convertir a CAPTURA un histórico con código 18?
4. ¿Cómo demuestran que el ETL conservó los datos, si no publican nombres ni el XLSM? Expliquen SHA-256, alias HMAC con clave privada, staging, fuente/fila, conciliación y la fila sin fecha.
5. Modifiquen Q03 para una máquina y otro trimestre. ¿Qué cambia entre porcentaje del paro y porcentaje sobre tiempo base? ¿Por qué unir producción directamente a cada paro antes de sumar puede inflar las pacas?

Para la quinta pregunta, el filtro de máquina debe aplicarse tanto a los paros como al denominador de tiempo base. En Q01 los límites representan meses completos. Q02 tiene períodos explícitos de enero-marzo y 2025 solo llega al 28 de marzo.

## Pendientes reales antes de entregar

- Comprobar que la versión mostrada coincide con la publicada y revisar el resultado de GitHub Actions.
- Registrar aportes reales de Erick y Daniel con sus propias cuentas. Los dos commits iniciales de una cuenta y las correcciones automatizadas posteriores no prueban la participación personal de ambos. No inventar fechas, cuentas o coautorías.
- Classroom se revisó directamente: exige PostgreSQL o MySQL. Algunas cantidades mínimas aparecen vacías también allí. Esta entrega tiene 9 índices explícitos, 4 vistas y 12 consultas. La entrega previamente enviada en Classroom contiene la versión anterior; requiere reemplazo autorizado por el docente si la plataforma impide reenviar.
- Hacer el ensayo con respuestas de ambos. La instalación y las pruebas automáticas no acreditan todavía su dominio oral.

Referencia de apertura de DBeaver por línea de comandos: https://dbeaver.com/docs/dbeaver/Command-Line/

## Material complementario

- `docs/GUION_ORAL.md`: texto de exposición y respuestas orientativas.
- `docs/NORMALIZACION.md`: ejemplo completo del Excel a 3FN.
- `docs/FLUJOS.md`: recorridos de exposición y ETL.
- `postgresql/README.md`: reconstrucción PostgreSQL en una base vacía y pruebas con psql.
