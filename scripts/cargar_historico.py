"""Carga la fuente seudonimizada preservando filas, valores nulos y trazabilidad."""
from pathlib import Path
from collections import Counter
import sqlite3,json,re,math

MAIN_COLS=[15,18,20,23,25,30,32,34,36,38,40,42,44,46,48,50,52,54]
def num(x):return isinstance(x,(int,float)) and not isinstance(x,bool)
def txt(x):return str(x).strip() if x is not None else ''
def subtoken(x):
 m=re.match(r'^(\d+(?:\.[0-9A-Za-z]+)+)\s+',txt(x))
 return m[1] if m else None
def load(con,root):
 root=Path(root);cats=json.loads((root/'datos/catalogos_xlsm.json').read_text(encoding='utf-8'))
 info=json.loads((root/'evidencias/inspeccion_xlsm.json').read_text(encoding='utf-8'))
 con.execute('PRAGMA foreign_keys=ON')
 with con:
  con.executemany('INSERT INTO fuente VALUES(?,?,?,?)',[(2,'Base De Datos',info['sha256_xlsm'],'PRINCIPAL'),(3,'Base de datos de Sub codigos',info['sha256_xlsm'],'AUXILIAR')])
  con.execute("INSERT INTO codigo_paro VALUES('18','Código 18 histórico: denominación contradictoria entre catálogos')")
  for i,name in enumerate(cats['referencias'],1000):con.execute('INSERT OR IGNORE INTO referencia(id,nombre) VALUES(?,?)',(i,name))
  for i,name in enumerate(cats['personas'],1000):con.execute('INSERT INTO persona(id,seudonimo) VALUES(?,?)',(i,name))
  for s in cats['subcodigos']:con.execute('INSERT OR IGNORE INTO subcodigo_paro VALUES(:codigo,:subcodigo,:descripcion)',s)
  refs=dict(con.execute('SELECT nombre,id FROM referencia'));persons=dict(con.execute('SELECT seudonimo,id FROM persona'))
  machines=dict(con.execute('SELECT nombre,id FROM maquina'));turns=dict(con.execute('SELECT nombre,id FROM turno'))
  aliases={'6am-2pm':'6am-2pm (Turno 1)','2pm-10pm':'2pm-10pm (Turno 2)','10pm-6am':'10pm-6am (Turno 3)'}
  incident_count=0;loaded=Counter()
  def issue(rid,fid,row,kind,detail):
   nonlocal incident_count
   con.execute('INSERT INTO incidencia(registro_id,fuente_id,fila,tipo,detalle) VALUES(?,?,?,?,?)',(rid,fid,row,kind,detail));incident_count+=1
  with (root/'datos/origen_xlsm.jsonl').open(encoding='utf-8') as stream:
   for line in stream:
    source=json.loads(line);fid=source['fuente_id'];row=source['fila'];v=source['valores']
    con.execute('INSERT INTO staging_xlsm VALUES(?,?,?)',(fid,row,json.dumps(source,ensure_ascii=False,separators=(',',':'))));loaded['staging']+=1
    if v[0] is None:
     issue(None,fid,row,'FILA_SIN_FECHA','Fila con fórmulas sin fecha; conservada solamente en staging.');continue
    date=txt(v[0])[:10]
    shift=txt(v[11] if fid==2 else v[7]);recovered=False
    if fid==2 and not shift and txt(v[7]) in (set(turns)|set(aliases)):
     shift=txt(v[7]);recovered=True
    shift=aliases.get(shift,shift)
    mins=float(v[10])*60 if fid==2 and num(v[10]) else None
    qty=v[9] if fid==2 and num(v[9]) else (v[6] if fid==3 and num(v[6]) else None)
    nowork=float(v[12])*60 if fid==2 and num(v[12]) else None
    origin=f"{info['sha256_xlsm']}:{fid}:{row}"
    cur=con.execute("INSERT INTO registro_produccion(fecha,maquina_id,turno_id,operario_id,referencia_id,minutos_base,meta_pacas_hora,pacas_reales,origen,clase,fuente_id,fila_fuente,estado,minutos_sin_trabajar) VALUES(?,?,?,?,?,?,NULL,?,?,'REAL',?,?,'HISTORICO',?)",(date,machines[txt(v[3])],turns.get(shift),persons.get(v[4]),refs.get(txt(v[5])),mins,qty,origin,fid,row,nowork))
    rid=cur.lastrowid;loaded['registros']+=1
    codecols=list(enumerate(MAIN_COLS,1)) if fid==2 else [(1,8),(3,11),(5,14)]
    subcols={1:16,3:21,5:26} if fid==2 else {1:9,3:12,5:15}
    total=0
    for code,col in codecols:
     if not num(v[col]) or v[col]<=0:continue
     total+=v[col];sub=subtoken(v[subcols[code]]) if code in subcols else None
     agent=txt(v[28] if fid==2 else v[17]) if code==5 else ''
     p=con.execute('INSERT INTO paro(registro_id,codigo,subcodigo,minutos,agente) VALUES(?,?,?,?,?)',(rid,f'{code:02}',sub,v[col],agent or None));loaded['paros']+=1
     if code==5:
      person=v[29] if fid==2 else v[18];agent=txt(v[28] if fid==2 else v[17])
      if person in persons:
       role='MANTENIMIENTO' if agent=='Personal_de_mantenimiento' else 'OPERACION' if agent=='Operarios' else 'CALIDAD' if 'calidad' in agent.lower() else 'OTRO'
       con.execute('INSERT INTO intervencion VALUES(?,?,?)',(p.lastrowid,persons[person],role));loaded['intervenciones']+=1
    if fid==2:
     if mins is not None and total>mins+1e-6:issue(rid,fid,row,'PARO_SUPERA_BASE','La suma de causas supera los minutos base en esta fila histórica.')
     if mins==0:issue(rid,fid,row,'HORAS_CERO','La fuente registra cero horas; no se divide entre cero.')
     if qty is not None and mins is None:issue(rid,fid,row,'PACAS_SIN_HORAS','Cantidad original conservada; tiempo desconocido.')
     if source.get('repetida_original'):issue(rid,fid,row,'REPETIDA_ORIGINAL','Coincide con otra fila de la fuente; se conserva sin eliminación automática.')
     if recovered:issue(rid,fid,row,'TURNO_RECUPERADO_H','Turno recuperado de la columna H antigua; L está vacía y H coincide con un turno válido.')
     if num(v[54]) and v[54]>0:issue(rid,fid,row,'CODIGO_18_AMBIGUO','Minutos conservados bajo el código 18; su descripción de negocio requiere aprobación.')
  assert not con.execute('PRAGMA foreign_key_check').fetchall()
 return {**loaded,'incidencias':incident_count}
