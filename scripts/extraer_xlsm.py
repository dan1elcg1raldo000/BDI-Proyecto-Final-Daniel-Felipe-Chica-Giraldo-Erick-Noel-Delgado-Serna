"""Lectura sin ejecutar VBA. Genera una fuente seudonimizada y controles cuantitativos.
La clave privada no se incluye en los entregables ni en Git.
"""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,date
from openpyxl import load_workbook
import argparse,json,hashlib,hmac,re,unicodedata,zipfile,xml.etree.ElementTree as ET

MAIN_COLS=[15,18,20,23,25,30,32,34,36,38,40,42,44,46,48,50,52,54]
MAIN_HOURS=[17,19,22,24,27,31,33,35,37,39,41,43,45,47,49,51,53,55]
def num(x):return isinstance(x,(int,float)) and not isinstance(x,bool)
def text(x):return unicodedata.normalize('NFC',str(x)).strip() if x is not None else ''
def serial(x):return x.isoformat() if isinstance(x,(datetime,date)) else x
def extract(source,root,key):
    root=Path(root);(root/'datos').mkdir(parents=True,exist_ok=True);(root/'evidencias').mkdir(parents=True,exist_ok=True)
    book=load_workbook(source,data_only=True,read_only=True,keep_links=False)
    sha=hashlib.sha256(Path(source).read_bytes()).hexdigest()
    refs=set();people=set();subs={};rawrows=[];counts={};totals={};quality=Counter();bycode={};fpr=Counter()
    def alias(value):
        t=text(value)
        if not t or t.lower()=='no aplica':return None
        token='PER-'+hmac.new(key,unicodedata.normalize('NFC',t).casefold().encode('utf-8'),hashlib.sha256).hexdigest()[:20]
        people.add(token);return token
    for fid,sheet,start in [(2,'Base De Datos',10),(3,'Base de datos de Sub codigos',9)]:
        rows=list(book[sheet].iter_rows(min_row=start,values_only=True));counts[sheet]=len(rows)
        colspec=list(enumerate(MAIN_COLS,1)) if fid==2 else [(1,8),(3,11),(5,14)]
        sums={'pacas':0.,'minutos_base':0.,'minutos_paro':0.};code=Counter();numericrows=0
        for rowno,row in enumerate(rows,start):
            values=[serial(v) for v in row]
            if fid==2:
                if num(row[9]):sums['pacas']+=row[9]
                if num(row[10]):sums['minutos_base']+=row[10]*60
                fp=hashlib.sha256(json.dumps(values,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()
                fpr[fp]+=1
                if fpr[fp]>1:quality['filas_exactamente_repetidas']+=1
                minutes=sum(row[c] for c in MAIN_COLS if num(row[c]))
                if num(row[10]) and minutes>row[10]*60+1e-6:quality['paros_superan_base_en_su_fila']+=1
                if row[9] is not None and row[10] is None:quality['pacas_sin_horas']+=1
                if row[10]==0:quality['horas_cero']+=1
                for c,h in zip(MAIN_COLS,MAIN_HOURS):
                    if abs((row[c] if num(row[c]) else 0)-(row[h]*60 if num(row[h]) else 0))>1e-6:quality['conversion_horas_discrepante']+=1
                if num(row[56]) and abs(minutes-row[56]*60)>1e-6:quality['total_paro_discrepante']+=1
                values[4]=alias(row[4]);values[29]=alias(row[29])
                for pos in [14,57]:
                    if values[pos] is not None:values[pos]='[OBSERVACION_RESERVADA]'
                subcols={1:16,3:21,5:26}
            else:
                values[4]=alias(row[4]);values[18]=alias(row[18]);subcols={1:9,3:12,5:15}
            if text(row[5]):refs.add(text(row[5]))
            for codeid,col in colspec:
                if num(row[col]):
                    code[f'{codeid:02}']+=row[col];sums['minutos_paro']+=row[col]
                if codeid in subcols:
                    label=text(row[subcols[codeid]])
                    match=re.match(r'^(\d+(?:\.[0-9A-Za-z]+)+)\s+(.*)',label)
                    if match:subs[(f'{codeid:02}',match[1])]=match[2].strip()
            rawrows.append({'fuente_id':fid,'fila':rowno,'valores':values,'repetida_original':fid==2 and fpr[fp]>1})
        totals[sheet]=sums;bycode[sheet]=dict(code)
    out=root/'datos/origen_xlsm.jsonl'
    with out.open('w',encoding='utf-8',newline='\n') as f:
        for row in rawrows:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    cats={'referencias':sorted(refs),'personas':sorted(people),'subcodigos':[{'codigo':k[0],'subcodigo':k[1],'descripcion':v} for k,v in sorted(subs.items())]}
    (root/'datos/catalogos_xlsm.json').write_text(json.dumps(cats,ensure_ascii=False,indent=2),encoding='utf-8')
    # Guardamos los resultados existentes del libro como controles independientes.
    pivots={}
    for name in ['TD_prodMaq','TD_prodAño','TD_prodCodigo','TD_fallaMecanica','TD_ajusteOperativo','TD_novPotencia']:
        pivots[name]=[[serial(c) for c in row] for row in book[name].iter_rows(values_only=True)]
    (root/'datos/controles_excel.json').write_text(json.dumps(pivots,ensure_ascii=False,indent=2),encoding='utf-8')
    info={'archivo':Path(source).name,'sha256_xlsm':sha,'hojas':[{'nombre':s.title,'filas':s.max_row,'columnas':s.max_column} for s in book],
          'filas_fuente':counts,'totales_fuente':totals,'minutos_por_codigo':bycode,'observaciones_calidad':dict(quality),
          'sha256_fuente_seudonimizada':hashlib.sha256(out.read_bytes()).hexdigest(),
          'proteccion':'Alias HMAC con clave privada fuera de Git; nombres y observaciones libres no se publican.',
          'macros':'No ejecutadas; lectura de valores cacheados y XML del paquete.'}
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(source) as z:
        info['vba_presente']='xl/vbaProject.bin' in z.namelist();info['formulas_pivote']=[]
        for name in z.namelist():
            if name.startswith('xl/pivotCache/pivotCacheDefinition') and name.endswith('.xml'):
                xml=ET.fromstring(z.read(name))
                for field in xml.findall('.//s:cacheField',ns):
                    if field.get('formula'):info['formulas_pivote'].append({'nombre':field.get('name'),'formula':field.get('formula')})
    (root/'evidencias/inspeccion_xlsm.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    book.close();return info

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archivo');p.add_argument('--salida',required=True);p.add_argument('--clave-privada',required=True)
    args=p.parse_args();secret=Path(args.clave_privada).read_bytes()
    if len(secret)<32:raise SystemExit('La clave privada debe tener al menos 32 bytes.')
    info=extract(args.archivo,args.salida,secret)
    print(json.dumps({'filas':info['filas_fuente'],'totales':info['totales_fuente'],'calidad':info['observaciones_calidad']},ensure_ascii=False,indent=2))
