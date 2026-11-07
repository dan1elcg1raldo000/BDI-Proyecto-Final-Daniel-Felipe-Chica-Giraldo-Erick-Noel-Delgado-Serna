"""Reconstruye la demostración y el histórico seudonimizado sin necesitar el XLSM."""
from pathlib import Path
import sqlite3,json,argparse,csv
from cargar_historico import load
p=argparse.ArgumentParser();p.add_argument('--salida',default='base_proyecto.sqlite');a=p.parse_args()
root=Path(__file__).resolve().parents[1];dest=Path(a.salida).resolve()
if dest.exists():raise SystemExit('La salida existe; elija otra con --salida.')
con=sqlite3.connect(dest)
try:
 con.execute('PRAGMA foreign_keys=ON')
 for filename in ['01_esquema.sql','02_catalogos.sql','03_demo.sql','04_vistas.sql']:
  con.executescript((root/'sql'/filename).read_text(encoding='utf-8'))
 result=load(con,root)
 assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 assert not con.execute('PRAGMA foreign_key_check').fetchall()
 print(json.dumps(result,ensure_ascii=False,indent=2))
except Exception:
 con.close();dest.unlink(missing_ok=True);raise
else:con.close()
