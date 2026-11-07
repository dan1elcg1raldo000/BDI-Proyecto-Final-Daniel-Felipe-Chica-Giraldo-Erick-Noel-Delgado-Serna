from pathlib import Path
import sqlite3,json
root=Path(__file__).resolve().parents[1]
c=sqlite3.connect(':memory:')
c.executescript((root/'sql/00_PROYECTO_COMPLETO.sql').read_text(encoding='utf-8'))
assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not c.execute('PRAGMA foreign_key_check').fetchall()
assert c.execute('SELECT COUNT(*) FROM staging_xlsm').fetchone()[0]==9460
assert c.execute("SELECT COUNT(*) FROM registro_produccion WHERE clase='REAL'").fetchone()[0]==9459
assert c.execute('SELECT SUM(pacas_reales) FROM registro_produccion WHERE fuente_id=2').fetchone()[0]==378778
before=list(c.iterdump())
c.executescript((root/'sql/08_sustentacion.sql').read_text(encoding='utf-8'))
assert before==list(c.iterdump())
result={'sql_completo':'OK','staging':9460,'historico':9459,'sustentacion_sin_mutaciones':'OK'}
(root/'evidencias/sql_completo.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
