"""Pruebas reales PostgreSQL: 18 rechazos, DML reversible y Q01-Q12.

Usa las variables PG* de libpq. Todas las modificaciones de prueba revierten.
"""
from pathlib import Path
import ast,json,re,os,csv
from reconstruir import run
P=Path(__file__).resolve().parent;ROOT=P.parent

def queries():
 text=(P/'05_consultas.sql').read_text(encoding='utf-8')
 return [(m[1],m[2],m[3].strip().rstrip(';')) for m in re.finditer(r'-- Q(\d{2}): ([^\n]+)\n(.*?)(?=\n-- Q\d{2}:|\Z)',text,re.S)]
def quote(s):return "'"+s.replace("'","''")+"'"
def main():
 old=ast.parse((ROOT/'scripts/verificar.py').read_text(encoding='utf-8'))
 cases=next(ast.literal_eval(n.value) for n in old.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cases' for t in n.targets))
 script="""BEGIN;
CREATE FUNCTION pg_temp.rechazado(titulo text, sentencia text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
 BEGIN
  EXECUTE sentencia;
 EXCEPTION WHEN integrity_constraint_violation OR invalid_datetime_format OR datetime_field_overflow OR invalid_text_representation THEN
  RETURN;
 END;
 RAISE EXCEPTION 'Dato inválido aceptado: %',titulo;
END $$;
"""
 for title,sql in cases:script+=f'SELECT pg_temp.rechazado({quote(title)},{quote(sql)});\n'
 script+="""
UPDATE registro_produccion SET estado='HISTORICO' WHERE id=1;
INSERT INTO paro(registro_id,codigo,minutos) VALUES(1,'18',0.1);
SELECT pg_temp.rechazado('Código 18 al convertir histórico en captura','UPDATE registro_produccion SET estado=''CAPTURA'' WHERE id=1');
INSERT INTO persona(id,seudonimo) VALUES(999999,'DEMO-PRUEBA');
UPDATE persona SET activa=0 WHERE id=999999;
DO $$ BEGIN IF (SELECT activa FROM persona WHERE id=999999)<>0 THEN RAISE EXCEPTION 'UPDATE no aplicado'; END IF; END $$;
DELETE FROM persona WHERE id=999999;
INSERT INTO paro(registro_id,codigo,minutos) VALUES(2,'01',0.1);
ROLLBACK;
"""
 run(sql=script)
 qs=queries();assert len(qs)==12
 evidence=ROOT/'evidencias/postgresql';evidence.mkdir(exist_ok=True)
 qr=[]
 for code,title,q in qs:
  rows=json.loads(run(sql=f"SELECT COALESCE(json_agg(t),'[]'::json) FROM ({q}) t"))
  (evidence/f'Q{code}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
  qr.append({'consulta':'Q'+code,'titulo':title,'filas':len(rows),'resultado':'OK'})
 invariants=json.loads(run(sql="""SELECT json_build_object(
 'motor',version(),
 'historicos',(SELECT count(*) FROM registro_produccion WHERE clase='REAL'),
 'demo',(SELECT count(*) FROM registro_produccion WHERE clase='DEMO'),
 'staging',(SELECT count(*) FROM staging_xlsm),
 'tablas',(SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'),
 'vistas',(SELECT count(*) FROM information_schema.views WHERE table_schema='public'),
 'triggers',(SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal),
 'fk_no_validadas',(SELECT count(*) FROM pg_constraint WHERE contype='f' AND NOT convalidated),
 'pacas_principal',(SELECT SUM(pacas_reales) FROM v_indicador_segmento WHERE clase='REAL' AND ambito='PRINCIPAL'),
 'minutos_base_principal',(SELECT SUM(minutos_base) FROM v_indicador_segmento WHERE clase='REAL' AND ambito='PRINCIPAL'),
 'minutos_paro_principal',(SELECT SUM(minutos_paro) FROM v_indicador_segmento WHERE clase='REAL' AND ambito='PRINCIPAL'))"""))
 expected={'historicos':9459,'demo':72,'staging':9460,'tablas':14,'vistas':4,'triggers':8,'fk_no_validadas':0,'pacas_principal':378778,'minutos_base_principal':2283801,'minutos_paro_principal':506979.1}
 for k,v in expected.items():assert invariants[k]==v,(k,invariants[k],v)
 result={'estado':'OK','motor':invariants.pop('motor'),'rechazos_correctos':18,'dml_reversible':'OK','resumen':invariants,'consultas':qr}
 (evidence/'validacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
