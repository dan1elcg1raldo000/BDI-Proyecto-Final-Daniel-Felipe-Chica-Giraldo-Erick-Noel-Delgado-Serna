"""Extrae solo campos no personales reconocibles. Requiere pypdf; nunca guarda texto bruto."""
from pathlib import Path
from pypdf import PdfReader
from datetime import datetime
import re,csv,argparse,hashlib,json
p=argparse.ArgumentParser();p.add_argument('pdf');p.add_argument('--salida',default='recuperado.csv');a=p.parse_args()
dest=Path(a.salida)
if dest.exists():raise SystemExit('La salida existe; elija otra ruta.')
r=PdfReader(a.pdf);rows=[]
pattern=r'^(\d{1,2}/\d{1,2}/\d{4})\s*[A-Za-záéíóúñ]+\s*\d{4}\s*(Vinilos_[1-4])\b'
for n,page in enumerate(r.pages,1):
 for li,line in enumerate(page.extract_text().splitlines(),1):
  m=re.match(pattern,line)
  if m:
   try:date=datetime.strptime(m[1],'%m/%d/%Y').date().isoformat()
   except ValueError:continue
   rows.append([len(rows)+1,n,li,date,m[2],'PENDIENTE_EXCEL'])
with dest.open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['id','pagina','linea','fecha','maquina','estado']);w.writerows(rows)
print(json.dumps({'paginas':len(r.pages),'filas':len(rows),'sha256_csv':hashlib.sha256(dest.read_bytes()).hexdigest()},indent=2))
