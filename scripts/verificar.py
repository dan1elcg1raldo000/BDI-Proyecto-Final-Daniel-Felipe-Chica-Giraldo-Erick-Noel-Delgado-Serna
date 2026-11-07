"""Prueba restricciones en transacciones reversibles, sin alterar el histórico."""
from pathlib import Path
import sqlite3,json,sys,csv
root=Path(__file__).resolve().parents[1]
c=sqlite3.connect(sys.argv[1] if len(sys.argv)>1 else 'base_proyecto.sqlite');c.execute('PRAGMA foreign_keys=ON')
results=[]
def rejected(title,sql):
 c.execute('SAVEPOINT caso')
 try:c.execute(sql)
 except sqlite3.IntegrityError as e:results.append({'prueba':title,'resultado':'RECHAZO_CORRECTO','detalle':str(e)})
 else:raise AssertionError('Dato inválido aceptado: '+title)
 finally:c.execute('ROLLBACK TO caso');c.execute('RELEASE caso')
cases=[
 ('Código inexistente',"INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'99',5)"),
 ('Subcódigo de otra causa',"INSERT INTO paro(registro_id,codigo,subcodigo,minutos) VALUES(1,'03','5.2',5)"),
 ('Duración negativa',"INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'01',-1)"),
 ('Duración cero',"INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'01',0)"),
 ('Exceso de paro en INSERT',"INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'01',480)"),
 ('Exceso de paro en UPDATE',"UPDATE paro SET minutos=480 WHERE id=1"),
 ('Reducir el tiempo base',"UPDATE registro_produccion SET minutos_base=1 WHERE id=1"),
 ('Borrar máquina utilizada',"DELETE FROM maquina WHERE id=1"),
 ('Origen duplicado',"UPDATE registro_produccion SET origen='DEMO:1' WHERE id=2"),
 ('Fecha inválida',"UPDATE registro_produccion SET fecha='2025-02-30' WHERE id=1"),
 ('Detalle horario excesivo',"UPDATE produccion_hora SET pacas=100000 WHERE registro_id=1 AND hora_relativa=0"),
 ('Hora fuera del segmento',"INSERT INTO produccion_hora VALUES(1,20,0)"),
 ('Producción inferior a su detalle',"UPDATE registro_produccion SET pacas_reales=0 WHERE id=1"),
 ('NOT NULL',"INSERT INTO persona(seudonimo) VALUES(NULL)"),
 ('Código 18 sin aprobar en nueva captura',"INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'18',1)"),
 ('Código 18 sin aprobar en modificación',"UPDATE paro SET codigo='18',subcodigo=NULL WHERE id=1"),
 ('Fuente y fila repetidas',"INSERT INTO staging_xlsm SELECT * FROM staging_xlsm LIMIT 1")]
for name,sql in cases:rejected(name,sql)
c.execute('SAVEPOINT valido')
c.execute("INSERT INTO persona(id,seudonimo) VALUES(999999,'DEMO-PRUEBA')")
c.execute('UPDATE persona SET activa=0 WHERE id=999999')
assert c.execute('SELECT activa FROM persona WHERE id=999999').fetchone()[0]==0
c.execute('DELETE FROM persona WHERE id=999999')
c.execute("INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'01',0.1)")
c.execute('ROLLBACK TO valido');c.execute('RELEASE valido')
results.append({'prueba':'INSERT, UPDATE, DELETE válidos y duración decimal','resultado':'OK'})
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not c.execute('PRAGMA foreign_key_check').fetchall()
assert not c.execute("SELECT r.id FROM registro_produccion r LEFT JOIN produccion_hora h ON h.registro_id=r.id WHERE r.clase='DEMO' GROUP BY r.id HAVING ABS(r.pacas_reales-SUM(h.pacas))>0.000001").fetchall()
queries=json.loads((root/'datos/consultas.json').read_text(encoding='utf-8'))
for i,(title,q) in enumerate(queries,1):
 cur=c.execute(q,{'clase':'DEMO','desde':'2025-01-01','hasta':'2025-04-01'});data=cur.fetchall()
 results.append({'consulta':f'Q{i:02}','filas':len(data),'resultado':'OK'})
(root/'evidencias/validacion.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rechazos_correctos':len(cases),'consultas':len(queries),'integridad':'OK'},ensure_ascii=False,indent=2))
c.close()
