PRAGMA foreign_keys=ON;
PRAGMA integrity_check;
PRAGMA foreign_key_check;
SELECT * FROM v_calidad_fuente;
SELECT * FROM v_productividad_mensual WHERE clase='REAL' AND maquina_id=2 AND mes>='2024-01' AND mes<'2025-01';
