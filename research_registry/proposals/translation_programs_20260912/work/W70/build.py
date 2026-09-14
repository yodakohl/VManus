from pathlib import Path
import csv,json,collections
D=Path(__file__).parent
src=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text())
by={(r['model'],r['edition'],r['paragraph'],r['at']):r for r in src}
fields=['word','hypothesis','kind','polarity','patient','patient_hypothesis']
rows=[];chains=[];md=['# Vollständiger Entwurf mit beiden Verzweigungen','','Alle Bedeutungen und Bezüge bleiben Hypothesen. Gemeinsam bedeutet nur Gleichheit unter NRC und AMV. Rohtext und offene Nicht-Ereignisgruppen bleiben vollständig sichtbar.','']
def phrase(r):
 return 'kein Prädikat in dieser Fassung' if r is None else r['polarity']+' '+r['hypothesis']+' → '+(r['patient_word']+' / '+r['patient_hypothesis']+' @'+r['patient'] if r['patient'] else 'OBJEKT FEHLT')
for p in ps:
 pr=[];md+=['## '+p['edition']+' '+p['id'],'']
 for l in p['lines']:
  md += [l['locus']+' `'+ ' '.join(l['words'])+'`','']
  for at,w in zip(l['source_ids'],l['words']):
   a=by.get(('NRC',p['edition'],p['id'],at));b=by.get(('AMV',p['edition'],p['id'],at))
   if a is None and b is None:continue
   diff=[f for f in fields if a and b and a[f]!=b[f]]
   status='NRC_ONLY' if b is None else 'AMV_ONLY' if a is None else 'DIFFERENT' if diff else 'SHARED_BOUND' if a['patient'] else 'SHARED_UNBOUND'
   row=dict(edition=p['edition'],paragraph=p['id'],at=at,word=w,status=status,differences=';'.join(diff),NRC=phrase(a),AMV=phrase(b),shared_patient=a['patient'] if status=='SHARED_BOUND' else '')
   rows.append(row);pr.append(row)
   md += ['- '+at+' **'+status+'**: '+(phrase(a) if status.startswith('SHARED') else 'NRC: '+phrase(a)+'; AMV: '+phrase(b))]
  md+=['']
 run=[]
 def flush():
  if len(run)>=2:chains.append(dict(edition=p['edition'],paragraph=p['id'],patient=run[0]['shared_patient'],events=[x['at'] for x in run],readings=[x['NRC'] for x in run]))
 for r in pr:
  if r['status']!='SHARED_BOUND' or run and r['shared_patient']!=run[-1]['shared_patient']:flush();run=[]
  if r['status']=='SHARED_BOUND':run.append(r)
 flush()
with (D/'COMPARISON.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n');(D/'CHAINS.json').write_text(json.dumps(chains,ensure_ascii=False,indent=2)+'\n')
r=dict(source_events=len(src),union_positions=len(rows),counts=dict(collections.Counter(x['status'] for x in rows)),chains=len(chains),meaning_confirmed=False,independent_confirmation_capacity=0)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print(json.dumps(chains,ensure_ascii=False))
