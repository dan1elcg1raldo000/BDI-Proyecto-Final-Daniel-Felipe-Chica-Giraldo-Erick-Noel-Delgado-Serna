"""Conciliación de staging, tablas normalizadas, sumas y tablas dinámicas originales."""
from pathlib import Path
from collections import Counter
import sqlite3,json,csv,sys,re,math,hashlib

root=Path(__file__).resolve().parents[1]
c=sqlite3.connect(sys.argv[1] if len(sys.argv)>1 else 'base_proyecto.sqlite');c.execute('PRAGMA foreign_keys=ON')
info=json.loads((root/'evidencias/inspeccion_xlsm.json').read_text(encoding='utf-8'))
controls=json.loads((root/'datos/controles_excel.json').read_text(encoding='utf-8'))
checks=[]
def close(a,b,label):
 assert a is not None and b is not None and abs(a-b)<=1e-6,label+': '+str((a,b))
 checks.append({'control':label,'excel':b,'base':a,'diferencia':a-b,'resultado':'OK'})
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not c.execute('PRAGMA foreign_key_check').fetchall()
source=root/'datos/origen_xlsm.jsonl'
assert hashlib.sha256(source.read_bytes()).hexdigest()==info['sha256_fuente_seudonimizada']
staging={(fid,row):data for fid,row,data in c.execute('SELECT fuente_id,fila,contenido_json FROM staging_xlsm')}
seen=Counter();core=Counter();missing=Counter()
for line in source.read_text(encoding='utf-8').splitlines():
 r=json.loads(line);key=(r['fuente_id'],r['fila']);seen[r['fuente_id']]+=1
 assert json.loads(staging[key])==r,key
 actual=c.execute('SELECT id,fecha,pacas_reales,minutos_base FROM registro_produccion WHERE fuente_id=? AND fila_fuente=?',key).fetchone()
 if r['valores'][0] is None:assert actual is None;missing[r['fuente_id']]+=1
 else:
  assert actual is not None;core[r['fuente_id']]+=1
  v=r['valores'];assert actual[1]==str(v[0])[:10]
  expected_qty=v[9] if key[0]==2 else v[6]
  assert actual[2]==expected_qty
  if key[0]==2:
   expected_min=v[10]*60 if isinstance(v[10],(int,float)) else None
   assert actual[3]==expected_min
checks.append({'control':'Comparación fila a fila JSONL/staging y cantidades normalizadas','filas':sum(seen.values()),'resultado':'OK'})
for fid,name in [(2,'Base De Datos'),(3,'Base de datos de Sub codigos')]:
 close(seen[fid],info['filas_fuente'][name],name+' filas en staging')
 actual=c.execute('SELECT COALESCE(SUM(pacas_reales),0),COALESCE(SUM(minutos_base),0) FROM registro_produccion WHERE fuente_id=?',(fid,)).fetchone()
 totalp=c.execute('SELECT SUM(p.minutos) FROM paro p JOIN registro_produccion r ON r.id=p.registro_id WHERE r.fuente_id=?',(fid,)).fetchone()[0]
 for value,key in zip([actual[0],actual[1],totalp],['pacas','minutos_base','minutos_paro']):close(value,info['totales_fuente'][name][key],name+' '+key)
 for code,expected in info['minutos_por_codigo'][name].items():
  got=c.execute('SELECT COALESCE(SUM(p.minutos),0) FROM paro p JOIN registro_produccion r ON r.id=p.registro_id WHERE r.fuente_id=? AND p.codigo=?',(fid,code)).fetchone()[0]
  close(got,expected,name+' minutos código '+code)

months={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'octubre':10,'noviembre':11,'diciembre':12}
for row in controls['TD_prodMaq']:
 if row[0] in months:
  month=f"2024-{months[row[0]]:02}"
  got=c.execute("SELECT productividad_pct/100 FROM v_productividad_mensual WHERE clase='REAL' AND maquina_id=2 AND mes=?",(month,)).fetchone()[0]
  close(got,row[1],'TD_prodMaq '+month)
for row in controls['TD_prodAño']:
 if len(row)>3 and row[2] in months:
  month=f"2024-{months[row[2]]:02}"
  got=c.execute("SELECT productividad_pct/100 FROM v_productividad_mensual WHERE clase='REAL' AND maquina_id=2 AND mes=?",(month,)).fetchone()[0]
  close(got,row[3],'TD_prodAño '+month)
base=c.execute("SELECT SUM(minutos_base) FROM registro_produccion WHERE fuente_id=2 AND maquina_id=2 AND fecha>='2024-01-01' AND fecha<'2025-01-01'").fetchone()[0]
condition="r.fuente_id=2 AND r.maquina_id=2 AND r.fecha>='2024-01-01' AND r.fecha<'2025-01-01'"
def ptotal(code):return c.execute('SELECT COALESCE(SUM(p.minutos),0) FROM paro p JOIN registro_produccion r ON r.id=p.registro_id WHERE '+condition+' AND p.codigo=?',(code,)).fetchone()[0]
for row in controls['TD_prodCodigo']:
 if len(row)<4 or not isinstance(row[3],(float,int)):continue
 m=re.match(r'^\[(\d+)\]',str(row[2]))
 if m:close(ptotal(m[1])/base,row[3],'TD_prodCodigo '+m[1])
 elif row[2]=='Suma de % Productividad':close((base-sum(ptotal(f'{k:02}') for k in range(1,19)))/base,row[3],'TD_prodCodigo productividad')
for sheet,code in [('TD_fallaMecanica','01'),('TD_novPotencia','03')]:
 total=ptotal(code)
 for row in controls[sheet]:
  if len(row)<4 or not isinstance(row[3],(int,float)):continue
  label=str(row[2]);match=re.match(r'^(\d+(?:\.[0-9A-Za-z]+)+)\s+',label)
  if match:
   got=c.execute('SELECT COALESCE(SUM(p.minutos),0) FROM paro p JOIN registro_produccion r ON r.id=p.registro_id WHERE '+condition+' AND p.codigo=? AND p.subcodigo=?',(code,match[1])).fetchone()[0]
   close(got/total,row[3],sheet+' '+match[1])
  elif label=='(en blanco)':
   got=c.execute('SELECT COALESCE(SUM(p.minutos),0) FROM paro p JOIN registro_produccion r ON r.id=p.registro_id WHERE '+condition+' AND p.codigo=? AND p.subcodigo IS NULL',(code,)).fetchone()[0]
   close(got/total,row[3],sheet+' sin subcódigo')
  elif label=='Total general':close(1,row[3],sheet+' total')
total=ptotal('05')
for row in controls['TD_ajusteOperativo']:
 if len(row)<6:continue
 match=re.match(r'^(5\.\d+)\s+',str(row[2]))
 if not match:continue
 for col,agent in [(3,'Operarios'),(4,'Personal_de_mantenimiento')]:
  if isinstance(row[col],(int,float)):
   got=c.execute('SELECT COALESCE(SUM(p.minutos),0) FROM paro p JOIN registro_produccion r ON r.id=p.registro_id WHERE '+condition+" AND p.codigo='05' AND p.subcodigo=? AND p.agente=?",(match[1],agent)).fetchone()[0]
   close(got/total,row[col],'TD_ajusteOperativo '+match[1]+' '+agent)

queries=json.loads((root/'datos/consultas.json').read_text(encoding='utf-8'))
for i,(title,sql) in enumerate(queries,1):
 cur=c.execute(sql,{'clase':'REAL','desde':'2025-01-01','hasta':'2025-04-01'});rows=cur.fetchall()
 with (root/f'evidencias/Q{i:02}.csv').open('w',encoding='utf-8',newline='') as f:
  writer=csv.writer(f);writer.writerow([x[0] for x in cur.description]);writer.writerows(rows)
 checks.append({'control':f'Q{i:02}','filas':len(rows),'resultado':'OK'})

result={'estado':'OK','fuente_sha256':info['sha256_xlsm'],'filas_staging':sum(seen.values()),'filas_normalizadas':sum(core.values()),'filas_sin_fecha_solo_staging':sum(missing.values()),'numero_controles':len(checks),'controles':checks}
(root/'evidencias/conciliacion_historica.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='controles'},ensure_ascii=False,indent=2))
c.close()
