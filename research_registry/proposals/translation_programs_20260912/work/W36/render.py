from pathlib import Path
import csv,json
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0])+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
gaps=[]
for sm in ['Q','A']:
 for c in ['C','P','K','PK']:
  folder=B if c=='C' else E;pre=sm if c=='C' else c+'_'+sm
  ff=rows(folder/(pre+'_SOURCE_FLAT.tsv'));byid={r['id']:r for r in ff}
  for r in rows(folder/(pre+'_ARGUMENTS.tsv')):
   if r['operation'] not in ['f22v.15:4','f32v.9:1']:continue
   ids=[r[k] for k in ['operation','patient','coingredient'] if r[k]];lo=min(int(byid[x]['offset']) for x in ids);hi=max(int(byid[x]['offset']) for x in ids)
   unknown=[x for x in ff if x['paragraph']==r['paragraph'] and lo<int(x['offset'])<hi and x['role']=='OPEN']
   gaps.append(dict(candidate=c,shol=sm,paragraph=r['paragraph'],grammar=r['grammar'],operation=r['operation'],patient=r['patient'],second=r['coingredient'],engine_debts=r['debts'],diagnostic_open_ids=';'.join(x['id'] for x in unknown),diagnostic_open_forms=';'.join(x['form'] for x in unknown),interpretation='Independent gap display; unchanged parser debt field is not evidence of clean syntax'))
table('BINDING_GAPS.tsv',gaps)
source=json.loads((E/'SOURCE.json').read_text())['paragraphs'];al=rows(E/'PK_A_ALIGNMENT.tsv')
out=['# W36 vollständige hypothetische PK-Lesung','Alle1045Rohgruppen unverändert. Nur chocthy/cthaiin neue Ganzwortannahmen; shol=A. chol H=erhitze/D=trockne. C/P/K bleiben explizite Rivalen; diese Tabelle bestätigt keine Übersetzung. cthaiin-Wertachse offen; chocthy-Trockenheit nur Konstitution.']
for p in source:
 out.append('\n## '+p['id'])
 for l in p['lines']:
  rr=[r for r in al if r['locus']==l['locus']];out.extend(['\n'+l['locus'],'\n`'+' '.join(l['words'])+'`','\n'+' · '.join(r['raw']+' ['+('D: trockne / H: erhitze' if r['raw']=='chol' else r['H'])+']' for r in rr)])
(E/'READING.md').write_text('\n'.join(out)+'\n')
