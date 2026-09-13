import csv,json
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W26'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(name,rr,cols):
 with (E/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
changes=[];counts={};newconf=[]
for sm in ['Q','A']:
 for kind,keys in [('ARGUMENTS',['paragraph','grammar','operation']),('QUALITY',['paragraph','grammar','mention']),('EVENTS',['paragraph','grammar','model','timing','kind','location','assertion']),('TAKE_ARGUMENTS',['paragraph','grammar','target'])]:
  a={tuple(r[k] for k in keys):r for r in rows(B/(sm+'_'+kind+'.tsv'))};b={tuple(r[k] for k in keys):r for r in rows(E/(sm+'_'+kind+'.tsv'))};assert len(b)==len(rows(E/(sm+'_'+kind+'.tsv')))
  for key in sorted(a.keys()|b.keys()):
   old=a.get(key,{});new=b.get(key,{})
   fields=[k for k in old.keys()|new.keys() if k not in ['source_event','execution_index','row_status'] and old.get(k)!=new.get(k)]
   if fields:changes.append(dict(shol=sm,table=kind,key='|'.join(key),fields=';'.join(sorted(fields)),U=json.dumps(old,sort_keys=True),N=json.dumps(new,sort_keys=True)))
   if kind=='EVENTS' and new.get('status')=='CONFLICT' and old.get('status')!='CONFLICT':newconf.append([sm,key])
 counts[sm]={x:sum(r['shol']==sm and r['table']==x for r in changes) for x in ['ARGUMENTS','QUALITY','EVENTS','TAKE_ARGUMENTS']}
table('ALL_CHANGES.tsv',changes,['shol','table','key','fields','U','N'])
result=dict(idea='IDEA000225',changes=counts,new_hard_conflicts=newconf,decision='Retain whole sal as editorial MATERIAL hypothesis; exact substance identities remain indistinguishable',independent_confirmation_capacity=0,confirmed_meanings=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
for r in changes:
 if r['shol']=='A' and r['table'] in ['ARGUMENTS','QUALITY']:print(r['table'],r['key'],r['fields'],[(k,json.loads(r['U']).get(k),json.loads(r['N']).get(k)) for k in r['fields'].split(';')])
