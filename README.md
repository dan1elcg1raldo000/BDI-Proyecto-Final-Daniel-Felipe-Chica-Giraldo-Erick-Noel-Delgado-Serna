# Registro de producción y paros de vinilos y témperas

**Bases de Datos I**  
**Daniel Felipe Chica Giraldo y Erick Noel Delgado Serna**

Base relacional SQLite normalizada hasta 3FN, con migración del XLSM original,
catálogos, indicadores de producción y análisis de causas de paro.

## Contenido

| Ruta | Descripción |
|---|---|
| `BDI_ProyectoFinal_Chica_Delgado.pdf` | Informe del proyecto |
| `base_proyecto.sqlite` | Base de datos poblada |
| `sql/` | Esquema, catálogos, vistas, consultas, DML y constructor completo |
| `datos/` | Histórico seudonimizado, catálogos y controles del Excel |
| `scripts/` | Extracción, migración, reconstrucción y verificaciones |
| `docs/` | Modelo, diccionario, informe editable y metodología de migración |
| `evidencias/` | Resultados y controles de integridad y conciliación |
| `presentacion/` | Presentación de resultados en PowerPoint y PDF |
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

`sql/00_PROYECTO_COMPLETO.sql` crea y carga el proyecto sobre una base SQLite vacía.
La alternativa con Python 3 usa su módulo estándar sqlite3:

```powershell
python scripts/reconstruir.py --salida base_nueva.sqlite
python scripts/verificar.py base_nueva.sqlite
python scripts/verificar_historico.py base_nueva.sqlite
python scripts/verificar_carga.py base_nueva.sqlite
python scripts/verificar_sql_completo.py
```

Las FK se activan por conexión con `PRAGMA foreign_keys=ON;`. El constructor no
sobrescribe bases existentes. Las verificaciones incluyen 17 rechazos correctos,
12 consultas y 118 controles de conciliación histórica. La extracción opcional
del XLSM usa openpyxl solo para lectura y no ejecuta macros.

## Procedencia

Fuentes: libro de seguimiento original y procedimiento P-MTO-22 V1 entregados
para la actividad. El informe y la evidencia identifican sus campos y huellas.
El historial Git registra el trabajo automatizado con sus fechas y autoría reales.
