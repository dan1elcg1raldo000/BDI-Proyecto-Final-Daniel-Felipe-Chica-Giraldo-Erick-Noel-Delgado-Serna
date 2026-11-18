# Registro de producción y paros de vinilos y témperas

**Bases de Datos I**
**Daniel Felipe Chica Giraldo y Erick Noel Delgado Serna**

**Motor de entrega: PostgreSQL 18.6**, conforme al encabezado original de Classroom revisado el 18/11/2026. La versión SQLite previa se conserva como respaldo y transformación temporal.

Base relacional PostgreSQL normalizada hasta 3FN, con migración del XLSM original,
catálogos, indicadores de producción y análisis de causas de paro.

## Contenido

| Ruta | Descripción |
|---|---|
| `BDI_ProyectoFinal_Chica_Delgado.pdf` | Informe del proyecto |
| `postgresql/` | Esquema, carga completa, doce consultas y pruebas PostgreSQL |
| `base_proyecto.sqlite` | Respaldo SQLite de conciliación, no motor de entrega |
| `sql/` | Implementación SQLite previa de respaldo |
| `datos/` | Histórico seudonimizado, catálogos y controles del Excel |
| `scripts/` | Extracción, migración, reconstrucción y verificaciones |
| `docs/` | Modelo, diccionario, informe editable y metodología de migración |
| `evidencias/` | Resultados y controles de integridad y conciliación |
| `presentacion/` | Material auxiliar de la versión SQLite previa; no usar para la demostración PostgreSQL |
| `.github/workflows/` | Verificación automática del proyecto |

## Modelo y datos

El modelo separa fuentes, máquinas, turnos, personas, referencias, registros,
códigos, subcódigos, paros e intervenciones. Las relaciones usan PK, FK y claves
compuestas; las restricciones controlan campos obligatorios, fechas y tiempos.

La migración conserva 9.460 filas en staging y normaliza 9.459. Una fila auxiliar
sin fecha permanece en staging. La hoja principal aporta 378.778 pacas,
2.283.801 minutos base y 506.979,1 minutos de paro. La hoja auxiliar se mantiene
separada para evitar doble conteo. Los datos sintéticos se identifican como DEMO.

La productividad temporal reproduce el campo calculado del Excel:

`100 × (SUM(minutos_base) - SUM(minutos_paro)) / SUM(minutos_base)`

Los resultados se concilian con las tablas dinámicas de la fuente. Los nombres
del personal se sustituyen por alias HMAC; el XLSM y la clave privada no se publican.
Las 498 incidencias de calidad de origen se conservan sin correcciones arbitrarias.

## Reproducción

Ejecutar `postgresql/00_PROYECTO_COMPLETO.sql` sobre una base PostgreSQL vacía en DBeaver. El archivo incluye esquema, catálogos, histórico y vistas en una transacción. No sobrescribe objetos existentes.

Con psql instalado y variables de conexión PGHOST, PGPORT, PGUSER, PGDATABASE y PGPASSWORD/PGPASSFILE configuradas fuera de Git:

```text
python postgresql/reconstruir.py --crear-base
python postgresql/verificar.py
```

Ver [instrucciones PostgreSQL](postgresql/README.md). La demostración usa `postgresql/07_sustentacion.sql` por bloques y `postgresql/05_consultas.sql` para Q01-Q12. PostgreSQL aplica las FK sin activar PRAGMA. Los tipos nativos incluyen DATE, NUMERIC, TIMESTAMPTZ y JSONB.

En PostgreSQL se comprobaron 18 rechazos correctos, DML reversible y las doce consultas. Las 14 tablas y los doce resultados coinciden con la referencia conciliada a seis decimales; solo se excluye creado_en. Las evidencias están en `evidencias/postgresql/`. Los 118 controles previos contra el Excel se conservan en la evidencia histórica.

La generación opcional de SQL (`python postgresql/generar_sql.py`) utiliza una transformación temporal SQLite con Python estándar. El SQL generado se carga directamente en PostgreSQL y no necesita el XLSM privado ni macros.

## Procedencia

Fuentes: libro de seguimiento original y procedimiento P-MTO-22 V1 entregados
para la actividad. El informe y la evidencia identifican sus campos y huellas.
El historial Git registra el trabajo automatizado con sus fechas y autoría reales.

## Revisión local para sustentación (17/11/2026)

Se añadió una prueba que rechaza convertir a CAPTURA un histórico con código 18; son 18 rechazos correctos. .gitattributes conserva los bytes del JSONL en Windows.

El historial inicial revisado tiene dos commits de una cuenta. Las correcciones posteriores se identifican como automatizadas y no acreditan aportes personales de ambos integrantes. La sección Actions permite comprobar la ejecución remota del flujo de verificación.

## Material para la sustentación

- [Modelo visual](docs/MODELO.md) y [normalización paso a paso](docs/NORMALIZACION.md).
- [Diccionario completo](docs/DICCIONARIO.md), con longitud o almacenamiento de cada columna.
- [Flujos](docs/FLUJOS.md) y [guion oral](docs/GUION_ORAL.md).
- `DEMOSTRAR.cmd` y `scripts/demo_sustentacion.py` pertenecen a la demostración SQLite previa. Para sustentar la versión PostgreSQL se utilizan los archivos de `postgresql/`.
- `postgresql/07_sustentacion.sql` reúne controles, Q01-Q12 y DML por bloques; no usa PRAGMA.

La preparación y revisión técnica se realizaron con asistencia automatizada de Codex. Los resultados de las pruebas corresponden a ejecuciones reales; el guion no acredita un ensayo oral ya realizado.
