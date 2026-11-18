-- Productividad original: porcentaje del tiempo base que no está registrado como paro.
-- No confundir con cumplimiento de la meta por cantidad, que queda aparte y puede ser NULL.
CREATE VIEW v_indicador_segmento AS
 SELECT r.*, f.ambito,
 r.meta_pacas_hora*r.minutos_base/60.0 AS pacas_ideales,
 COALESCE(p.minutos_paro,0) AS minutos_paro,
 100.0*(r.minutos_base-COALESCE(p.minutos_paro,0))/NULLIF(r.minutos_base,0) AS productividad_pct,
 100.0*r.pacas_reales/NULLIF(r.meta_pacas_hora*r.minutos_base/60.0,0) AS cumplimiento_meta_pct
 FROM registro_produccion r JOIN fuente f ON f.id=r.fuente_id
 LEFT JOIN (SELECT registro_id,SUM(minutos) minutos_paro FROM paro GROUP BY registro_id) p ON p.registro_id=r.id;
CREATE VIEW v_productividad_mensual AS
 SELECT clase,maquina_id,substr(fecha::text,1,7) mes,SUM(pacas_reales) pacas,
 SUM(minutos_base) minutos_base,SUM(minutos_paro) minutos_paro,
 100.0*(SUM(minutos_base)-SUM(minutos_paro))/NULLIF(SUM(minutos_base),0) productividad_pct
 FROM v_indicador_segmento WHERE ambito IN ('PRINCIPAL','DEMO')
 GROUP BY clase,maquina_id,substr(fecha::text,1,7);
CREATE VIEW v_paros_detalle AS
 SELECT p.id,p.registro_id,r.fecha,r.clase,f.ambito,r.maquina_id,r.turno_id,
 m.nombre maquina,COALESCE(t.nombre,'Sin turno registrado') turno,
 p.codigo,c.descripcion causa,p.subcodigo,COALESCE(s.descripcion,'Sin especificar') subcausa,p.minutos
 FROM paro p JOIN registro_produccion r ON r.id=p.registro_id
 JOIN fuente f ON f.id=r.fuente_id JOIN maquina m ON m.id=r.maquina_id
 LEFT JOIN turno t ON t.id=r.turno_id JOIN codigo_paro c ON c.codigo=p.codigo
 LEFT JOIN subcodigo_paro s ON s.codigo=p.codigo AND s.subcodigo=p.subcodigo;
CREATE VIEW v_calidad_fuente AS
 SELECT f.hoja,i.tipo,COUNT(*) casos FROM incidencia i JOIN fuente f ON f.id=i.fuente_id
 GROUP BY f.hoja,i.tipo;
