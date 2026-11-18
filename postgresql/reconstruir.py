"""Carga PostgreSQL mediante psql; no requiere paquetes Python externos.

PGHOST, PGPORT, PGUSER, PGPASSWORD/PGPASSFILE y PGDATABASE son variables estándar.
No borra ni sobrescribe bases o tablas existentes.
"""
from pathlib import Path
import subprocess,os,shutil,argparse,re,sys
P=Path(__file__).resolve().parent
def psql_path():
 if os.environ.get('PSQL'):return os.environ['PSQL']
 found=shutil.which('psql')
 if found:return found
 paths=sorted(Path(os.environ.get('PROGRAMFILES','C:/Program Files')).glob('PostgreSQL/*/bin/psql.exe'),reverse=True)
 if paths:return str(paths[0])
 raise SystemExit('No se encontró psql. Instale PostgreSQL o configure PSQL con su ruta.')
def run(sql=None,file=None,database=None):
 args=[psql_path(),'-X','-w','-v','ON_ERROR_STOP=1','-At','-q']
 if database:args+=['-d',database]
 args+=['-f',str(file)] if file else ['-f','-']
 env=dict(os.environ,PGCLIENTENCODING='UTF8',PGCONNECT_TIMEOUT='10')
 r=subprocess.run(args,input=None if file else sql,capture_output=True,text=True,encoding='utf-8',errors='replace',env=env,timeout=180)
 if r.returncode:raise RuntimeError(r.stderr.strip())
 return r.stdout
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--crear-base',action='store_true')
 parser.add_argument('--antes',action='store_true')
 a=parser.parse_args()
 database=os.environ.get('PGDATABASE','bdi_proyecto')
 if not re.fullmatch('[a-z][a-z0-9_]{0,62}',database):raise SystemExit('Nombre de base inválido.')
 if a.crear_base:
  exists=run(sql=f"SELECT 1 FROM pg_database WHERE datname='{database}'",database='postgres').strip()
  if exists:raise SystemExit('La base ya existe. Elija otra PGDATABASE; no se sobrescribe.')
  run(sql=f'CREATE DATABASE "{database}"',database='postgres')
 filename='00_ANTES_sin_historico.sql' if a.antes else '00_PROYECTO_COMPLETO.sql'
 run(file=P/filename,database=database)
 print('PostgreSQL: carga completada en '+database+(' (ANTES, sin histórico)' if a.antes else ' (DESPUÉS, histórico + DEMO)'))
 print(run(sql="SELECT json_build_object('motor',version(),'historicos',(SELECT count(*) FROM registro_produccion WHERE clase='REAL'),'demo',(SELECT count(*) FROM registro_produccion WHERE clase='DEMO'),'staging',(SELECT count(*) FROM staging_xlsm))",database=database).strip())
if __name__=='__main__':main()
