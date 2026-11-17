# Flujos para la exposición

## Recorrido oral

```mermaid
flowchart TD
 A[Daniel: problema y procedimiento] --> B[Excel: tabla ancha y anomalías]
 B --> C[Modelo: entidades, llaves y cardinalidades]
 C --> D[1FN, 2FN y 3FN con ejemplo]
 D --> E[Restricciones y triggers en CAPTURA]
 E --> F[Erick: extracción y staging]
 F --> G[Carga y conciliación]
 G --> H[DBeaver: PRAGMA y Q12 en vivo]
 H --> I[Q01-Q12: indicadores y límites]
 I --> J[Cierre conjunto y preguntas]
```

## Recorrido técnico

```mermaid
flowchart TD
 X[XLSM privado: lectura sin VBA] -->|Extracción opcional con openpyxl| P[Alias HMAC; clave privada fuera de Git]
 P --> J[JSONL seudonimizado público]
 J -->|Reconstrucción con Python estándar| S[Staging: 9460 filas]
 C[Esquema y catálogos SQL] --> S
 S --> N[Histórico normalizado: 9459 filas]
 S --> I[Una fila sin fecha: staging e incidencia]
 N --> V[Vistas: principal separado de auxiliar y DEMO]
 V --> Q[Consultas Q01-Q12]
 Q --> A[118 controles históricos e integridad]
 N --> R[CAPTURA: controles de paros, horarios y código 18]
 SQL[Constructor SQL completo] --> O[Alternativa: base vacía en SQLite]
 O --> V
```

La reconstrucción habitual usa los datos seudonimizados del repositorio. No necesita el XLSM original, la clave HMAC, openpyxl ni ejecutar macros.
