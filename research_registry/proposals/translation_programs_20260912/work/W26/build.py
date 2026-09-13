"""Run both isolated shol worlds and retain every target/future consequence."""
import csv,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent
for model in ['Q','A']:exec(compile((E/'engine.py').read_text(),'W26_engine','exec'),{'__file__':str(E/'engine.py'),'SHOL_MODEL':model})
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
old=rows(W/'W25/EVENTS.tsv');new=rows(E/'Q_EVENTS.tsv');herb={r['paragraph'] for r in old};part=[r for r in new if r['paragraph'] in herb];assert part==old
oldalign=rows(W/'W25/ALIGNMENT.tsv');assert [r for r in rows(E/'Q_ALIGNMENT.tsv') if r['paragraph'] in herb]==oldalign
flat=rows(E/'Q_SOURCE_FLAT.tsv');raw={r['id']:r['form'] for r in flat};locations=[r for r in flat if r['form']=='shol'];targets=[];futures=[];changes=[]
qworld=collections.defaultdict(list);aworld=collections.defaultdict(list)
for m,ww in [('Q',qworld),('A',aworld)]:
 for r in rows(E/(m+'_EVENTS.tsv')):ww[r['paragraph'],r['grammar'],r['model'],r['timing']].append(r)
for key,q in qworld.items():
 a=aworld[key];aidx={(r['kind'],r['location'],r['assertion'] if r['kind'] not in ['ACTION','QUALITY'] else ''):r for r in a}
 for x in [x for x in locations if x['paragraph']==key[0]]:
  qt=next(r for r in q if r['location']==x['id'] and r['kind']=='QUALITY');at=next(r for r in a if r['location']==x['id'] and r['kind']=='ACTION')
  targets.append(dict(paragraph=key[0],grammar=key[1],chol=key[2],timing=key[3],target=x['id'],Q_patient=qt['patient'],Q_object=qt['object'],Q_status=qt['status'],Q_debts=qt['debts'],A_patient=at['patient'],A_patient_form=raw.get(at['patient'],''),A_object=at['object'],A_status=at['status'],A_debts=at['debts'],Q_before=qt['before'],A_before=at['before'],A_after=at['after']))
  for sm,trace,t in [('Q',q,qt),('A',a,at)]:
   ti=trace.index(t)
   for r in trace[ti+1:]:
    if t['object'] and r['object']==t['object']:futures.append(dict(paragraph=key[0],grammar=key[1],chol=key[2],timing=key[3],shol_model=sm,target=x['id'],location=r['location'],kind=r['kind'],form=r['form'],object=r['object'],status=r['status'],before=r['before'],after=r['after'],debts=r['debts']))
 for r in q:
  if r['form']=='shol':continue
  ar=aidx[(r['kind'],r['location'],r['assertion'] if r['kind'] not in ['ACTION','QUALITY'] else '')]
  changed=[k for k in ['patient','object','before','after','status','debts','state_origin','order'] if r[k]!=ar[k]]
  if changed:changes.append(dict(paragraph=key[0],grammar=key[1],chol=key[2],timing=key[3],location=r['location'],kind=r['kind'],form=r['form'],changed_fields=','.join(changed),Q_patient=r['patient'],A_patient=ar['patient'],Q_object=r['object'],A_object=ar['object'],Q_status=r['status'],A_status=ar['status'],Q_before=r['before'],A_before=ar['before'],Q_after=r['after'],A_after=ar['after']))
table('SHOL_TARGETS.tsv',targets);table('ALL_TARGET_FUTURES.tsv',futures);table('OTHER_CHANGES.tsv',changes)
result={'HERB4_Q_parity':True,'groups':1045,'shol_positions':len(locations),'target_cases':len(targets),'future_rows':len(futures),'other_change_rows':len(changes),'models':{m:json.loads((E/(m+'_RESULT.json')).read_text()) for m in ['Q','A']},'newly_assigned_positions':0,'revised_gloss_positions':8,'independent_confirmation_capacity':0,'held_access':False}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='models'}))
