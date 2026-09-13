import csv,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
def ek(r):return r['kind'],r['location'],r['assertion']
candidates=[];later=[]
for sm in ['Q','A']:
 cc=rows(B/(sm+'_EVENTS.tsv'));nn=rows(E/(sm+'_EVENTS.tsv'));scopes=[r for r in rows(E.parent/'W30/SCOPES.tsv') if r['shol']==sm and r['contract']=='TRANSFER']
 for t in scopes:
  for g in ['B','J','M']:
   for model in ['D','H']:
    for timing in ['O','I']:
     match=lambda r:(r['paragraph'],r['grammar'],r['model'],r['timing'])==(t['paragraph'],g,model,timing)
     C=[r for r in cc if match(r)];N=[r for r in nn if match(r)];a=next(r for r in C if r['location']==t['target'] and r['kind'] in ['ACTION','QUALITY']);b=next(r for r in N if r['location']==t['target'] and r['kind'] in ['ACTION','QUALITY']);meta=dict(shol=sm,paragraph=t['paragraph'],grammar=g,model=model,timing=timing,chey=t['chey'],target=t['target'],target_form=t['target_form'])
     candidates.append(dict(**meta,kind=b['kind'],C_patient=a['patient'],N_patient=b['patient'],C_object=a['object'],N_object=b['object'],C_status=a['status'],N_status=b['status'],C_before=a['before'],N_before=b['before'],C_after=a['after'],N_after=b['after'],N_debts=b['debts'],open_scope=t['open_interval']))
     objects={a['object'],b['object']}-{''};cidx={ek(r):r for r in C};nidx={ek(r):r for r in N};futurekeys={ek(r) for trace,target in [(C,a),(N,b)] for r in trace[trace.index(target)+1:] if r['kind']!='MATERIAL' and (r['object'] in objects or r['second_object'] in objects)}
     for key in sorted(futurekeys):
      x=cidx.get(key);y=nidx.get(key);later.append(dict(**meta,location=key[1],kind=key[0],C_status=x['status'] if x else 'ABSENT',N_status=y['status'] if y else 'ABSENT',C_before=x['before'] if x else '',N_before=y['before'] if y else '',C_after=x['after'] if x else '',N_after=y['after'] if y else '',constraint_discriminator=key[0] not in ['ACTION','MATERIAL'] and (x or {}).get('status')!=(y or {}).get('status')))
table('CANDIDATES.tsv',candidates,list(candidates[0]));table('ALL_LATER_REQUIREMENTS.tsv',later,list(later[0]) if later else ['shol','paragraph','grammar','model','timing','chey','target','target_form','location','kind','C_status','N_status','C_before','N_before','C_after','N_after','constraint_discriminator'])
r=json.loads((E/'RESULT.json').read_text());r.update(candidate_cases=len(candidates),negative_missing_patient_cases=sum(x['kind']=='QUALITY' and not x['N_patient'] for x in candidates),later_requirement_rows=len(later),later_constraint_discriminators=sum(x['constraint_discriminator'] for x in later),replayed_worlds=408,replayed_events=10680);(E/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
print('later differences',collections.Counter((x['target'],x['location'],x['kind'],x['C_status'],x['N_status']) for x in later if x['C_status']!=x['N_status']))
