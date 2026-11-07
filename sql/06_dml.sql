PRAGMA foreign_keys=ON;
-- Ejemplo reversible. Ejecutar después de 01-04. IDs reservados solo para esta demo.
BEGIN;
INSERT INTO persona(id,seudonimo) VALUES(900001,'DEMO-TEMPORAL');
UPDATE persona SET activa=0 WHERE id=900001;
DELETE FROM persona WHERE id=900001;
ROLLBACK;
-- Los casos rechazados se ejecutan aislados en scripts/verificar.py:
-- INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'99',5); -- FK
-- INSERT INTO paro(registro_id,codigo,subcodigo,minutos) VALUES(1,'03','5.2',5); -- FK compuesta
-- UPDATE registro_produccion SET minutos_base=1 WHERE id=1; -- trigger
-- DELETE FROM maquina WHERE id=1; -- RESTRICT
