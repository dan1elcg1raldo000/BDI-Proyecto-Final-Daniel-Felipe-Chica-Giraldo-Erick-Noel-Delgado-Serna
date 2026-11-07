"""Prueba la carga revisada en una copia temporal; no modifica la base entregada."""
from pathlib import Path
import tempfile,sqlite3,csv,subprocess,sys,json
from contextlib import closing

root=Path(__file__).resolve().parents[1]
source=Path(sys.argv[1] if len(sys.argv)>1 else 'base_demo.sqlite').resolve()
if not source.is_file():raise SystemExit('No se encontró la base de origen.')
results=[]
with tempfile.TemporaryDirectory(dir=root/'evidencias',prefix='prueba_carga_') as temp:
    folder=Path(temp);db=folder/'prueba.sqlite'
    with closing(sqlite3.connect(source)) as src, closing(sqlite3.connect(db)) as dst:src.backup(dst)
    regs=folder/'segmentos.csv';stops=folder/'paros.csv'
    with regs.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['origen','fecha','maquina_id','turno_id','operario_id','referencia_id','minutos_base','meta_pacas_hora','pacas_reales'])
        w.writerow(['PRUEBA-CARGA-001','2025-04-01',1,1,'',1,60,10,8])
    def write_stop(code):
        with stops.open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f);w.writerow(['origen_segmento','codigo','subcodigo','minutos']);w.writerow(['PRUEBA-CARGA-001',code,'',5])
    def count():
        with closing(sqlite3.connect(db)) as c:return tuple(c.execute("SELECT COUNT(*) FROM registro_produccion WHERE clase='REAL'").fetchone())
    def run():return subprocess.run([sys.executable,str(root/'scripts/cargar_revisados.py'),str(db),str(regs),str(stops)],capture_output=True,text=True)
    before=count();write_stop('99');r=run()
    assert r.returncode!=0 and count()==before
    results.append({'prueba':'FK inválida revierte la carga completa','resultado':'OK'})
    write_stop('01');r=run()
    assert r.returncode==0 and count()[0]==before[0]+1,r.stderr
    results.append({'prueba':'Carga válida y conciliación de pacas/minutos','resultado':'OK'})
    before=count();r=run()
    assert r.returncode!=0 and count()==before
    results.append({'prueba':'Reimportación rechazada por origen UNIQUE','resultado':'OK'})
(root/'evidencias/carga_revisada.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
