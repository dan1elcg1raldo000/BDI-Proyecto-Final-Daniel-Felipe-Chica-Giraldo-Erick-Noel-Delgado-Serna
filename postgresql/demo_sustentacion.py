"""Demostración PostgreSQL reproducible en una base temporal propia.

Requiere psql, variables PG* y permiso CREATEDB. Conserva la base de entrega.
"""
from pathlib import Path
import os,uuid,json,subprocess,sys
from reconstruir import run
P=Path(__file__).resolve().parent
def main():
 name='bdi_demo_'+uuid.uuid4().hex[:12]
 created=False
 try:
  print('1. MOTOR REAL: '+run(sql='SELECT version()',database='postgres').strip(),flush=True)
  run(sql=f'CREATE DATABASE "{name}"',database='postgres');created=True
  print('2. ANTES: base temporal nueva, sin tablas de usuario.',flush=True)
  print('3. Ejecutando 00_PROYECTO_COMPLETO.sql...',flush=True)
  run(file=P/'00_PROYECTO_COMPLETO.sql',database=name)
  print('4. DESPUES: datos, restricciones y Q01-Q12.',flush=True)
  env=dict(os.environ,PGDATABASE=name,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
  # La prueba escribe evidencia en disco y revierte todas sus modificaciones SQL.
  result=subprocess.run([sys.executable,str(P/'verificar.py')],env=env,capture_output=True,text=True,encoding='utf-8',timeout=180)
  if result.returncode:raise RuntimeError(result.stderr)
  data=json.loads(result.stdout)
  print(json.dumps({'motor':data['motor'],'rechazos_correctos':data['rechazos_correctos'],'consultas':len(data['consultas']),'datos':data['resumen']},ensure_ascii=False,indent=2),flush=True)
  print('DEMOSTRACION POSTGRESQL TERMINADA CORRECTAMENTE',flush=True)
 finally:
  if created:
   run(sql=f'DROP DATABASE "{name}"',database='postgres')
   print('Se retiró únicamente la base temporal creada por esta ejecución. La base de entrega se conserva.',flush=True)
if __name__=='__main__':main()
