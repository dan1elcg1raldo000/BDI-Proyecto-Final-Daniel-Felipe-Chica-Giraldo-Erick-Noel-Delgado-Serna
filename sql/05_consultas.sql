-- Parámetros: clase=REAL; desde=2025-01-01; hasta=2025-04-01.
-- Q01 exige meses completos; Q02 compara el mismo trimestre disponible.
-- Q01: Productividad temporal por máquina y mes
SELECT m.nombre,v.mes,ROUND(v.productividad_pct,4) productividad_pct,v.minutos_base,v.minutos_paro,v.pacas FROM v_productividad_mensual v JOIN maquina m ON m.id=v.maquina_id WHERE v.clase=:clase AND v.mes>=substr(:desde,1,7) AND v.mes<substr(:hasta,1,7) ORDER BY m.id,v.mes;

-- Q02: Comparativo enero-marzo 2024 y 2025
WITH a AS (SELECT maquina_id,substr(fecha,1,4) anio,SUM(minutos_base) base,SUM(minutos_paro) paros,100.0*(SUM(minutos_base)-SUM(minutos_paro))/NULLIF(SUM(minutos_base),0) pct FROM v_indicador_segmento WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND ((fecha>='2024-01-01' AND fecha<'2024-04-01') OR (fecha>='2025-01-01' AND fecha<'2025-04-01')) GROUP BY maquina_id,substr(fecha,1,4)) SELECT m.nombre,ROUND(x.pct,4) pct_2024,ROUND(y.pct,4) pct_2025,ROUND(y.pct-x.pct,4) diferencia_pp,x.base minutos_2024,y.base minutos_2025 FROM maquina m LEFT JOIN a x ON x.maquina_id=m.id AND x.anio='2024' LEFT JOIN a y ON y.maquina_id=m.id AND y.anio='2025' ORDER BY m.id;

-- Q03: Participación de códigos de paro y porcentaje sobre tiempo base
WITH p AS (SELECT codigo,SUM(minutos) minutos FROM v_paros_detalle WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta GROUP BY codigo) SELECT c.codigo,c.descripcion,COALESCE(p.minutos,0) minutos,ROUND(100.0*COALESCE(p.minutos,0)/NULLIF((SELECT SUM(minutos) FROM p),0),4) pct_del_paro,ROUND(100.0*COALESCE(p.minutos,0)/NULLIF((SELECT SUM(minutos_base) FROM v_indicador_segmento WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta),0),4) pct_base FROM codigo_paro c LEFT JOIN p ON p.codigo=c.codigo ORDER BY minutos DESC;

-- Q04: Detalle por subcódigo 01, 03 y 05
WITH d AS (SELECT codigo,COALESCE(subcodigo,'SIN_SUBCODIGO') subcodigo,subcausa,SUM(minutos) minutos FROM v_paros_detalle WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta AND codigo IN ('01','03','05') GROUP BY codigo,subcodigo,subcausa) SELECT d.*,ROUND(100.0*minutos/NULLIF((SELECT SUM(x.minutos) FROM d x WHERE x.codigo=d.codigo),0),4) pct_dentro_codigo FROM d ORDER BY codigo,minutos DESC;

-- Q05: Comparación de turnos dentro de cada máquina
SELECT m.nombre maquina,COALESCE(t.nombre,'Sin turno registrado') turno,COUNT(*) filas_fuente,ROUND(100.0*(SUM(v.minutos_base)-SUM(v.minutos_paro))/NULLIF(SUM(v.minutos_base),0),4) productividad_pct,SUM(v.minutos_base) minutos_base FROM v_indicador_segmento v JOIN maquina m ON m.id=v.maquina_id LEFT JOIN turno t ON t.id=v.turno_id WHERE v.clase=:clase AND v.ambito IN ('PRINCIPAL','DEMO') AND v.fecha>=:desde AND v.fecha<:hasta GROUP BY m.id,t.id ORDER BY m.id,t.id;

-- Q06: Causas que acumulan más de 100 minutos
SELECT codigo,causa,SUM(minutos) minutos FROM v_paros_detalle WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta GROUP BY codigo,causa HAVING SUM(minutos)>100 ORDER BY minutos DESC;

-- Q07: Máquinas por debajo de la productividad del conjunto
WITH d AS (SELECT maquina_id,SUM(minutos_base) base,SUM(minutos_paro) paros FROM v_indicador_segmento WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta GROUP BY maquina_id) SELECT m.nombre,ROUND(100.0*(d.base-d.paros)/NULLIF(d.base,0),4) productividad_pct FROM d JOIN maquina m ON m.id=d.maquina_id WHERE (d.base-d.paros)/NULLIF(d.base,0)<(SELECT (SUM(base)-SUM(paros))/NULLIF(SUM(base),0) FROM d);

-- Q08: Máquinas sin filas en el período
SELECT m.nombre FROM maquina m WHERE NOT EXISTS(SELECT 1 FROM v_indicador_segmento v WHERE v.maquina_id=m.id AND v.clase=:clase AND v.ambito IN ('PRINCIPAL','DEMO') AND v.fecha>=:desde AND v.fecha<:hasta);

-- Q09: Participación de agentes en ajustes operativos
SELECT COALESCE(p.agente,'Sin agente registrado') agente,COUNT(*) detalles,SUM(p.minutos) minutos FROM paro p JOIN v_indicador_segmento r ON r.id=p.registro_id WHERE p.codigo='05' AND r.clase=:clase AND r.ambito IN ('PRINCIPAL','DEMO') AND r.fecha>=:desde AND r.fecha<:hasta GROUP BY p.agente ORDER BY minutos DESC;

-- Q10: Incidencias de calidad del histórico por tipo
SELECT f.hoja,i.tipo,COUNT(*) casos FROM incidencia i JOIN fuente f ON f.id=i.fuente_id LEFT JOIN registro_produccion r ON r.id=i.registro_id WHERE r.id IS NULL OR (r.clase=:clase AND r.fecha>=:desde AND r.fecha<:hasta) GROUP BY f.hoja,i.tipo ORDER BY f.hoja,casos DESC;

-- Q11: Pareto de causas de paro
WITH c AS (SELECT codigo,SUM(minutos) minutos FROM v_paros_detalle WHERE clase=:clase AND ambito IN ('PRINCIPAL','DEMO') AND fecha>=:desde AND fecha<:hasta GROUP BY codigo) SELECT codigo,minutos,ROUND(100.0*SUM(minutos) OVER(ORDER BY minutos DESC,codigo ROWS UNBOUNDED PRECEDING)/NULLIF(SUM(minutos) OVER(),0),4) acumulado_pct FROM c ORDER BY minutos DESC,codigo;

-- Q12: Conteos y totales por fuente sin mezclar las hojas
SELECT f.hoja,f.ambito,COUNT(r.id) filas,COALESCE(SUM(r.pacas_reales),0) pacas,COALESCE(SUM(r.minutos_base),0) minutos_base,COALESCE(SUM(r.minutos_paro),0) minutos_paro FROM fuente f LEFT JOIN v_indicador_segmento r ON r.fuente_id=f.id GROUP BY f.id ORDER BY f.id;
