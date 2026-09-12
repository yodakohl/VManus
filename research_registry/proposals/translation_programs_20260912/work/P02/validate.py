"""Independent event-target graph then ordered state replay; does not import builder."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
D=Path('research_registry/proposals/translation_programs_20260912/work/P02')
def rr(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
src=json.loads((D/'SOURCE.json').read_text())
for p,h in src['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
orig=json.loads((D.parent/'P11/INPUT.json').read_text())['lines'];pages=['f29v','f32v','f17r','f21r'];flat=[]
for page in pages:
 for l in orig:
  if l['locus'].split('.')[0]==page:
   for k,w in enumerate(l['groups'],1):flat.append((page,l['locus'],f'{l["locus"]}:{k}',w))
assert [(r['record'],r['line'],r['locus'],r['word']) for r in rr('INPUT.tsv')]==flat
assert any(l['locus']=='f21r.11' and l['groups'][:3]==['shol','chol','shol'] for l in orig)
nouns={'okaiin':'A','cthy':'B','chor':'C'}
ops={'shytchy':('RIGHT','moisture','WET'),'otshy':('RIGHT','temperature','COLD'),'shot':('LEFT','temperature','HOT'),'qotchy':('LEFT','texture','GROUND'),'cpho':('LEFT','texture','GROUND'),'cphos':('LEFT','texture','GROUND')}
aff={'chol':{'moisture':'DRY'},'shol':{'moisture':'WET'},'shy':{'moisture':'WET'},'oltchy':{'temperature':'COLD','moisture':'DRY'}};axes=['moisture','temperature','texture']
def show(s):return ';'.join(a+'='+s[a] for a in axes)
actualevents=rr('OPERATIONS.tsv');actualchecks=rr('STATE_CHECKS.tsv');actualmentions=rr('MENTIONS.tsv')
for mode in ['CARRY','NEW']:
 ids={}
 for j,t in enumerate(flat):
  if t[3] in nouns:
   n=sum(x[0]==t[0] and x[3]=='okaiin' for x in flat[:j+1]) if mode=='NEW' and t[3]=='okaiin' else 1
   ids[j]=nouns[t[3]]+str(n)
 plans=defaultdict(list)
 for j,t in enumerate(flat):
  if t[3] not in ops:continue
  direction,axis,value=ops[t[3]];target=None
  if direction=='LEFT':
   eligible=[k for k in ids if k<j and flat[k][0]==t[0]];target=eligible[-1] if eligible else None;execution=j
  else:
   for k in range(j+1,len(flat)):
    if flat[k][1]!=t[1] or flat[k][3] in ops:break
    if k in ids:target=k;break
   execution=target if target is not None else j
  plans[execution].append((j,target,axis,value))
 state={};provenance={};current=None;rec=None;checked_mentions=0
 for j,t in enumerate(flat):
  if t[0]!=rec:rec=t[0];state={};provenance={};current=None
  prior=None;fresh=False
  if j in ids:
   current=ids[j];fresh=current not in state
   if fresh:state[current]={a:'UNKNOWN' for a in axes};provenance[current]={a:'NA' for a in axes}
   prior=(show(state[current]),show(provenance[current]))
  for opindex,target,axis,value in plans[j]:
   op=flat[opindex];identity=ids[target] if target is not None else None
   e=next(e for e in actualevents if e['mode']==mode and e['action_source']==op[2]);before=show(state[identity]) if identity else 'NA'
   assert e['before']==before and e['execution_at']==t[2] and e['target']==(identity or 'NA')
   if identity:state[identity][axis]=value;provenance[identity][axis]=op[2]
   assert e['after']==(show(state[identity]) if identity else 'NA')
   assert e['status']==('BOUND_TARGET_MISSING_LIQUID' if identity and op[3]=='shytchy' else 'BOUND' if identity else 'MISSING_TARGET')
  if j in ids:
   m=next(m for m in actualmentions if m['mode']==mode and m['locus']==t[2]);assert (m['before'],m['prior_axis_sources'])==prior
   assert (m['after'],m['axis_sources'])==(show(state[current]),show(provenance[current]))
   assert m['identity']==current and m['introduction']==('NEW_INSTANCE' if fresh else 'REUSED_INSTANCE');checked_mentions+=1
  if t[3] in aff:
   for axis,value in aff[t[3]].items():
    old=state[current][axis] if current else 'UNKNOWN';pr=provenance[current][axis] if current else 'NA'
    status='MISSING_TARGET' if current is None else 'INITIAL_CONSTRAINT' if old=='UNKNOWN' else 'CONSISTENT' if old==value else 'CONFLICT'
    c=next(c for c in actualchecks if c['mode']==mode and c['locus']==t[2] and c['axis']==axis)
    assert (c['predicted'],c['prior_source'],c['status'],c['asserted'])==(old,pr,status,value)
    assert c['target']==(current or 'NA')
    if current and old=='UNKNOWN':state[current][axis]=value;provenance[current][axis]=t[2]
 assert checked_mentions==12
 align=rr(f'ALIGNMENT_{mode}.tsv');assert [(r['record'],r['line'],r['locus'],r['word']) for r in align]==flat
 assert sum(r['kind']=='OPEN' for r in align)==113
 assert all(r['rendering']=='⟦'+r['word']+'⟧' for r in align if r['kind']=='OPEN')
 text=(D/f'READING_{mode}.md').read_text();assert all('`'+l['raw_line']+'`' in text for l in orig)
 r=json.loads((D/'RESULT.json').read_text())['models'][mode]
 assert r['operations']==dict(Counter(e['status'] for e in actualevents if e['mode']==mode))
 assert r['state_axis_checks']==dict(Counter(c['status'] for c in actualchecks if c['mode']==mode))
 assert max(r['instances_per_record'].values())<=3
assert len(actualevents)==14 and len(actualchecks)==28 and len(actualmentions)==24
changes=rr('IDENTITY_CONSEQUENCES.tsv');assert len(changes)==1;diff=changes[0]
assert diff['locus']=='f29v.4:9' and diff['later_checks']=='NONE'
assert 'temperature=COLD' in diff['CARRY_state'] and 'temperature=UNKNOWN' in diff['NEW_state']
assert diff['CARRY_identity']=='A1' and diff['NEW_identity']=='A2'
receipt={'status':'PASS','source_hashes':len(src['inputs']),'groups_per_reading':145,'independent_operations':14,'independent_state_axis_checks':28,'independent_mentions':24,'identity_difference':'f29v.4:9 cold A1 vs unknown A2; no later assertion','checks':['source coordinate correction','static action-target graph','ordered state/axis provenance replay','assertion conflicts retained','three-instance bound','complete source-preserving readings'],'limit':'Internal consequences, not meanings, observed object identity or scientific significance.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
