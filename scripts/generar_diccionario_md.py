"""Completa las longitudes documentadas y genera el diccionario desde sus metadatos."""
from pathlib import Path
import json
import re


def longitud(columna):
    tipo = columna['type'].upper()
    if tipo == 'INTEGER':
        return 'Entero con signo de hasta 64 bits; no tiene longitud decimal fija'
    if tipo == 'REAL':
        return 'Punto flotante de 64 bits; no tiene escala decimal fija'
    regla = columna['constraints']
    campo = re.escape(columna['name'])
    patron = rf'length\({campo}\)\s*'
    match = re.search(patron + r'BETWEEN\s+(\d+)\s+AND\s+(\d+)', regla, re.I)
    if match:
        return f'{match[1]} a {match[2]} caracteres (CHECK)'
    match = re.search(patron + r'=\s*(\d+)', regla, re.I)
    if match:
        return f'{match[1]} caracteres (CHECK)'
    match = re.search(patron + r'<=\s*(\d+)', regla, re.I)
    if match:
        return f'Hasta {match[1]} caracteres (CHECK)'
    return 'Variable; sin límite de negocio adicional al dominio CHECK y al límite del motor'


def generar(root):
    root = Path(root)
    archivo = root / 'docs/diccionario.json'
    tablas = json.loads(archivo.read_text(encoding='utf-8'))
    lineas = [
        '# Diccionario de datos',
        'SQLite usa afinidades de tipo. INTEGER y REAL no imponen longitud decimal; '
        'TEXT tiene longitud variable y los límites de negocio se aplican con CHECK. '
        'Las FK usan ON DELETE RESTRICT y ON UPDATE CASCADE. NULL conserva lo desconocido.',
    ]
    for tabla in tablas:
        lineas.extend(['', '## ' + tabla['name'], tabla['desc'], '',
                       '|Columna|Tipo|Longitud o almacenamiento|NULL|Default|Restricciones|Significado|',
                       '|---|---|---|---|---|---|---|'])
        for col in tabla['columns']:
            col['length'] = longitud(col)
            valores = [col['name'], col['type'], col['length'],
                       'Sí' if col['nullable'] else 'No', col['default'],
                       col['constraints'], col['business']]
            lineas.append('|' + '|'.join(str(v).replace('|', '/') for v in valores) + '|')
    archivo.write_text(json.dumps(tablas, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    (root / 'docs/DICCIONARIO.md').write_text('\n'.join(lineas) + '\n', encoding='utf-8', newline='\n')
    return sum(len(t['columns']) for t in tablas)


if __name__ == '__main__':
    print('Columnas documentadas:', generar(Path(__file__).resolve().parents[1]))
