# Ejecución PostgreSQL

Motor de entrega: PostgreSQL 18.6, según el encabezado original de Classroom.

## En DBeaver

1. Crear una base PostgreSQL vacía y conectarse a ella.
2. Abrir `00_PROYECTO_COMPLETO.sql` y ejecutarlo completo con Alt+X.
3. Abrir `05_consultas.sql` para Q01-Q12, o `07_sustentacion.sql` para controles y DML.
4. El constructor está en una transacción: un error revierte la carga. No borra objetos existentes.

Alternativa modular: `01_esquema.sql`, `02_catalogos.sql`, `03_carga.sql`, `04_vistas.sql`, en ese orden, sobre una base vacía. `00_ANTES_sin_historico.sql` crea el estado de demostración anterior a cargar histórico.

## Con Python y psql

Configurar las variables estándar PGHOST, PGPORT, PGUSER, PGDATABASE y PGPASSWORD o PGPASSFILE con una cuenta propia. No guardar contraseñas en Git. El usuario necesita permisos para crear la base si se usa --crear-base.

```text
python postgresql/reconstruir.py --crear-base
python postgresql/verificar.py
```

psql debe estar en PATH; en Windows se detecta también bajo Program Files/PostgreSQL. La variable PSQL permite dar otra ruta. No se necesitan paquetes Python externos.

## Datos y regeneración

El SQL completo ya contiene el histórico público seudonimizado. Su carga en PostgreSQL no necesita SQLite, el XLSM privado ni macros. `generar_sql.py` regenera este SQL desde el JSONL público: usa temporalmente el transformador SQLite previo con la biblioteca estándar de Python y exporta sus filas. SQLite es un área temporal y un respaldo de conciliación, no el motor de entrega.

Los minutos y pacas se almacenan como NUMERIC; fecha usa DATE; auditoría usa TIMESTAMPTZ; staging usa JSONB. PostgreSQL aplica las FK declaradas sin activar PRAGMA. Ocho triggers PL/pgSQL comprueban las reglas de captura. Los controles agregados bloquean la fila padre antes de leer sus detalles.

## Evidencia

`../evidencias/postgresql/validacion.json`: 18 rechazos correctos, DML reversible, 12 consultas, conteos y totales.

`../evidencias/postgresql/comparacion_independiente.json`: comparación de las 14 tablas y Q01-Q12 con la referencia conciliada. Se excluye creado_en y se compara a seis decimales. Los controles históricos previos conservan su evidencia de 118 verificaciones contra el Excel.

Las credenciales de CI pertenecen a un contenedor temporal sin datos privados y no son credenciales de la instancia local.
