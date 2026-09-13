import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
changes=[];summaries=[];bad=[];grouping=collections.defaultdict(list)
for sm in ['Q','A']:
 for candidate in ['C','O','L','OL']:
  folder=B if candidate=='C' else E;prefix=sm if candidate=='C' else candidate+'_'+sm
  tables={name:rows(folder/(prefix+'_'+name+'.tsv')) for name in ['ARGUMENTS','QUALITY','TAKE_ARGUMENTS','EVENTS']}
  digest=hashlib.sha256(json.dumps({k:v for k,v in tables.items() if k!='EVENTS'},sort_keys=True).encode()).hexdigest();grouping[sm,digest].append(candidate)
  if candidate=='C':continue
  counts={}
  for name,keys in [('ARGUMENTS',['paragraph','grammar','operation']),('QUALITY',['paragraph','grammar','mention']),('TAKE_ARGUMENTS',['paragraph','grammar','target']),('EVENTS',['paragraph','grammar','model','timing','kind','location','assertion'])]:
   C={tuple(r[k] for k in keys):r for r in rows(B/(sm+'_'+name+'.tsv'))};N={tuple(r[k] for k in keys):r for r in tables[name]};count=0
   for key in sorted(C.keys()|N.keys()):
    a=C.get(key,{});b=N.get(key,{})
    fields=sorted(k for k in a.keys()|b.keys() if k not in ['source_event','execution_index','row_status'] and a.get(k)!=b.get(k))
    if fields:changes.append(dict(candidate=candidate,shol=sm,table=name,key='|'.join(key),fields=';'.join(fields),C=json.dumps(a,sort_keys=True),N=json.dumps(b,sort_keys=True)));count+=1
    if name=='EVENTS' and b.get('status') in ['CONFLICT','ARGUMENT_INCOMPLETE'] and a.get('status')!=b['status']:bad.append(dict(candidate=candidate,shol=sm,key='|'.join(key),old_status=a.get('status','ABSENT'),new_status=b['status']))
   counts[name]=count
  summaries.append(dict(candidate=candidate,shol=sm,**counts))
table('ALL_CHANGES.tsv',changes,list(changes[0]));table('CHANGE_COUNTS.tsv',summaries,list(summaries[0]));table('NEW_FAILURES.tsv',bad,['candidate','shol','key','old_status','new_status'])
groups=[dict(shol=k[0],members=','.join(v),digest=k[1],scope='Identical ARGUMENTS QUALITY TAKE tables only; material mentions/lexical labels can differ') for k,v in grouping.items()];table('PREDICTION_GROUPS.tsv',groups,list(groups[0]))
result=dict(idea='IDEA000230',changes=summaries,new_failures=bad,prediction_groups=groups,source_paragraphs=17,source_groups=1045,new_worlds=1224,new_events=sum(json.loads((E/(c+'_'+sm+'_RESULT.json')).read_text())['events'] for c in ['O','L','OL'] for sm in ['Q','A']),confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
for r in changes:
 if r['candidate']=='O' and r['shol']=='A' and r['table'] in ['ARGUMENTS','QUALITY','TAKE_ARGUMENTS']:
  a=json.loads(r['C']);b=json.loads(r['N'])
  if b.get('grammar')=='J':print(r['table'],r['key'],a.get('patient'),b.get('patient'),r['fields'])
