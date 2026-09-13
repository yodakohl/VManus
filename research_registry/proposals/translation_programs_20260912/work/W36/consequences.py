import csv,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
def eventkey(r):return r['kind'],r['location'],r['assertion']
out=[];future=[];takefuture=[]
for sm in ['Q','A']:
 cflat=rows(B/(sm+'_SOURCE_FLAT.tsv'));targets=[r for r in cflat if r['form'] in ['chocthy','cthaiin']];Cevents=rows(B/(sm+'_EVENTS.tsv'));Ctakes=rows(B/(sm+'_TAKE_ARGUMENTS.tsv'))
 for candidate in ['C','P','K','PK']:
  N=Cevents if candidate=='C' else rows(E/(candidate+'_'+sm+'_EVENTS.tsv'));Nt=Ctakes if candidate=='C' else rows(E/(candidate+'_'+sm+'_TAKE_ARGUMENTS.tsv'))
  for t in targets:
   for grammar in ['B','J','M']:
    for model in ['D','H']:
     for timing in ['O','I']:
      match=lambda r:(r['paragraph'],r['grammar'],r['model'],r['timing'])==(t['paragraph'],grammar,model,timing)
      cc=[r for r in Cevents if match(r)];nn=[r for r in N if match(r)];ci={eventkey(r):r for r in cc};ni={eventkey(r):r for r in nn};mat=next((r for r in nn if r['location']==t['id'] and r['kind']=='MATERIAL'),None)
      direct=[r for r in nn if r['kind'] in ['ACTION','QUALITY'] and (r['patient']==t['id'] or r.get('second')==t['id'])];objects={mat['object']} if mat else set();displaced={ci[eventkey(r)][field] for r in direct if eventkey(r) in ci for field in ['object','second_object'] if ci[eventkey(r)][field]!=r[field]}-{''};objects|=displaced
      meta=dict(candidate=candidate,shol=sm,paragraph=t['paragraph'],grammar=grammar,model=model,timing=timing,target=t['id'],form=t['form'])
      takes=[r for r in Nt if (r['paragraph'],r['grammar'],r['patient'])==(t['paragraph'],grammar,t['id'])]
      out.append(dict(**meta,material=bool(mat),object=mat['object'] if mat else '',direct_actions=';'.join(r['location'] for r in direct if r['kind']=='ACTION'),direct_qualities=';'.join(r['location'] for r in direct if r['kind']=='QUALITY'),take_uses=';'.join(r['target'] for r in takes),displaced_objects=';'.join(sorted(displaced))))
      if not mat:continue
      keys={eventkey(r) for trace in [cc,nn] for r in trace if int(r['order'])>=int(t['offset']) and r['kind']!='MATERIAL' and (r['object'] in objects or r['second_object'] in objects)}
      for k in sorted(keys):
       a=ci.get(k);b=ni.get(k);future.append(dict(**meta,location=k[1],kind=k[0],C_object=a['object'] if a else '',N_object=b['object'] if b else '',C_status=a['status'] if a else 'ABSENT',N_status=b['status'] if b else 'ABSENT',C_before=a['before'] if a else '',N_before=b['before'] if b else '',C_after=a['after'] if a else '',N_after=b['after'] if b else '',role='DIRECT_USE' if b and b['patient']==t['id'] else 'OTHER_USE_OR_DISPLACED',constraint_status_change=k[0]!='ACTION' and (a or {}).get('status')!=(b or {}).get('status')))
      for r in Nt:
       if (r['paragraph'],r['grammar'])!=(t['paragraph'],grammar):continue
       pos=next(x for x in cflat if x['id']==r['target'])
       if int(pos['offset'])<int(t['offset']):continue
       patientmat=next((x for x in nn if x['kind']=='MATERIAL' and x['location']==r['patient']),None)
       if patientmat and patientmat['object'] in objects:
        old=next(x for x in Ctakes if (x['paragraph'],x['grammar'],x['target'])==(r['paragraph'],grammar,r['target']));takefuture.append(dict(**meta,take=r['target'],C_patient=old['patient'],N_patient=r['patient'],N_debts=r['debts']))
table('CANDIDATES.tsv',out,list(out[0]));table('ALL_LATER_REQUIREMENTS.tsv',future,list(future[0]));table('ALL_LATER_TAKE.tsv',takefuture,list(takefuture[0]) if takefuture else ['candidate','shol','paragraph','grammar','model','timing','target','form','take','C_patient','N_patient','N_debts'])
r=json.loads((E/'RESULT.json').read_text());r.update(candidate_rows=len(out),later_requirement_rows=len(future),later_take_rows=len(takefuture),constraint_change_rows=sum(x['constraint_status_change'] for x in future));(E/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['candidate_rows','later_requirement_rows','later_take_rows','constraint_change_rows']}))
print('changed constraints',collections.Counter((r['candidate'],r['location'],r['C_status'],r['N_status']) for r in future if r['constraint_status_change']))
