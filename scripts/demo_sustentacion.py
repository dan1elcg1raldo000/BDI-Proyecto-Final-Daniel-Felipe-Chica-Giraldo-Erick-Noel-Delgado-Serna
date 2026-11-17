"""Demostración en vivo: reconstruye una base temporal y consulta sus resultados."""
from pathlib import Path
import json
import sqlite3
import subprocess
import sys
import tempfile
import time


def main():
    root = Path(__file__).resolve().parents[1]
    inicio = time.perf_counter()
    print('BASES DE DATOS I - RECONSTRUCCION Y CONSULTA EN VIVO', flush=True)
    print('Daniel Felipe Chica Giraldo y Erick Noel Delgado Serna\n', flush=True)
    with tempfile.TemporaryDirectory(prefix='bdi_demo_') as carpeta:
        base = Path(carpeta) / 'demo.sqlite'
        print('1. Reconstruccion desde SQL y JSONL del repositorio', flush=True)
        subprocess.run([sys.executable, str(root / 'scripts/reconstruir.py'),
                        '--salida', str(base)], cwd=root, check=True)
        con = sqlite3.connect(base)
        try:
            con.execute('PRAGMA foreign_keys=ON')
            integridad = con.execute('PRAGMA integrity_check').fetchone()[0]
            errores = con.execute('PRAGMA foreign_key_check').fetchall()
            assert integridad == 'ok' and not errores
            print('\n2. integrity_check =', integridad)
            print('   foreign_key_check: errores =', len(errores))
            print('\n3. Q12 de sql/05_consultas.sql: totales por fuente')
            texto = (root / 'sql/05_consultas.sql').read_text(encoding='utf-8')
            sql = texto.split('-- Q12:', 1)[1].split('\n', 1)[1]
            cur = con.execute(sql)
            columnas = [x[0] for x in cur.description]
            for fila in cur:
                print(json.dumps(dict(zip(columnas, fila)), ensure_ascii=False))
        finally:
            con.close()
    print(f'\nDemostracion completada en {time.perf_counter()-inicio:.2f} segundos.')
    print('La base temporal se cerro y limpio. Las bases entregadas no se modificaron.')


if __name__ == '__main__':
    main()
