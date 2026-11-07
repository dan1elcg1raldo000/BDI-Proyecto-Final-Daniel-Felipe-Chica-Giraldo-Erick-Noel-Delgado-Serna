"""Importa CSV previamente revisados. Atómico, sin nombres y sin ejecutar macros."""
import sqlite3,csv,argparse,json,hashlib,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('segmentos');p.add_argument('paros');a=p.parse_args()
if not Path(a.base).is_file():raise SystemExit('La base debe existir y tener el esquema 01.')
def read(path):
 with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
regs=read(a.segmentos);paros=read(a.paros)
if not regs:raise SystemExit('No se importan archivos vacíos.')
c=sqlite3.connect(a.base);c.execute('PRAGMA foreign_keys=ON')
before=c.execute("SELECT COUNT(*),COALESCE(SUM(pacas_reales),0) FROM registro_produccion WHERE clase='REAL'").fetchone()
bp=c.execute('SELECT COUNT(*),COALESCE(SUM(minutos),0) FROM paro').fetchone()
try:
 with c:
  ids={};total=0;total_min=0
  for r in regs:
   origin=r['origen'].strip()
   if not origin or origin in ids:raise ValueError('Origen vacío o repetido en archivo')
   q=float(r['pacas_reales']);meta=float(r['meta_pacas_hora'])
   if not math.isfinite(q) or not math.isfinite(meta):raise ValueError('Número no finito')
   cur=c.execute("INSERT INTO registro_produccion(fecha,maquina_id,turno_id,operario_id,referencia_id,minutos_base,meta_pacas_hora,pacas_reales,origen,clase) VALUES(?,?,?,?,?,?,?,?,?,'REAL')",(r['fecha'],int(r['maquina_id']),int(r['turno_id']),int(r['operario_id']) if r['operario_id'].strip() else None,int(r['referencia_id']),float(r['minutos_base']),meta,q,origin))
   ids[origin]=cur.lastrowid;total+=q
  for r in paros:
   mins=int(r['minutos']);total_min+=mins
   c.execute('INSERT INTO paro(registro_id,codigo,subcodigo,minutos) VALUES(?,?,?,?)',(ids[r['origen_segmento']],r['codigo'],r['subcodigo'].strip() or None,mins))
  after=c.execute("SELECT COUNT(*),COALESCE(SUM(pacas_reales),0) FROM registro_produccion WHERE clase='REAL'").fetchone()
  ap=c.execute('SELECT COUNT(*),COALESCE(SUM(minutos),0) FROM paro').fetchone()
  if after[0]-before[0]!=len(regs) or not math.isclose(after[1]-before[1],total,abs_tol=1e-6):raise ValueError('No coincide producción')
  if ap[0]-bp[0]!=len(paros) or ap[1]-bp[1]!=total_min:raise ValueError('No coinciden paros')
  if c.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('FK inválidas')
 print(json.dumps({'segmentos':len(regs),'paros':len(paros),'pacas':total,'minutos_paro':total_min,'conciliacion':'OK','sha256_segmentos':hashlib.sha256(Path(a.segmentos).read_bytes()).hexdigest(),'sha256_paros':hashlib.sha256(Path(a.paros).read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
finally:c.close()
