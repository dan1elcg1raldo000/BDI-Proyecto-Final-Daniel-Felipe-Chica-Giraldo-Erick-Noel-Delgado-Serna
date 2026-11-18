-- El redondeo es solo de presentación; las tablas conservan sus valores.
SELECT indicador,valor FROM (
 SELECT 1 AS orden,'Motor' AS indicador,version() AS valor
 UNION ALL SELECT 2,'Staging',count(*)::text FROM staging_xlsm
 UNION ALL SELECT 3,'Históricos',count(*)::text FROM registro_produccion WHERE clase='REAL'
 UNION ALL SELECT 4,'DEMO',count(*)::text FROM registro_produccion WHERE clase='DEMO'
 UNION ALL SELECT 5,'Pacas principal',round(COALESCE(sum(pacas_reales),0),0)::text FROM v_indicador_segmento WHERE clase='REAL' AND ambito='PRINCIPAL'
 UNION ALL SELECT 6,'Minutos base principal',round(COALESCE(sum(minutos_base),0),0)::text FROM v_indicador_segmento WHERE clase='REAL' AND ambito='PRINCIPAL'
 UNION ALL SELECT 7,'Minutos paro principal',round(COALESCE(sum(minutos_paro),0),1)::text FROM v_indicador_segmento WHERE clase='REAL' AND ambito='PRINCIPAL'
) x ORDER BY orden;
