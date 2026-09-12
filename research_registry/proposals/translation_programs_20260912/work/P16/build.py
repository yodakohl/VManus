import csv,json,hashlib,itertools
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P16');S=D.parent/'P12/PROSE.tsv'
lex={'qokaiin':'Stoff A','shedy':'Stoff B','qokedy':'warm','qoteedy':'kalt','chedy':'erhitze','qokeedy':'kühle','sol':'wenn','qokal':'außer wenn','chey':'nicht'}
ps={'qokedy','qoteedy','chedy','qokeedy'};cs={'sol','qokal'};ms={'qokaiin':'A','shedy':'B'}
records={}
for r in csv.DictReader(S.open(),delimiter='\t'):
 records.setdefault(r['record_id'],[]).extend(dict(at=r['locus']+':'+str(i),word=w,record=r['record_id']) for i,w in enumerate(r['zl3b_line'].split(),1))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,x):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(x[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in x)
dump('SOURCE.json',dict(source=str(S),sha256=hashlib.sha256(S.read_bytes()).hexdigest(),decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='Entire source previously exposed; discovery not confirmation'))
dump('MODEL.json',dict(lexicon=lex,worlds=['warm','kalt','neutral'],scope='single state per record',C='P implies Q; exception not P implies Q',U='P and Q',negation='forward next predicate before connector, parity'))
props=[];ops=[];rules=[]
for rid,ts in records.items():
 mat=None;local={}
 for i,t in enumerate(ts):
  w=t['word']
  if w in ms:mat=t
  if w in ps:
   p=dict(record=rid,at=t['at'],word=w,kind='state' if w in ['qokedy','qoteedy'] else 'action',value=lex[w],material=ms[mat['word']] if mat else '',material_locus=mat['at'] if mat else '',negations=[],negative=False)
   local[i]=p;props.append(p)
 for i,t in enumerate(ts):
  w=t['word']
  if w not in cs|{'chey'}:continue
  left=right=None
  if w in cs:
   for j in range(i-1,-1,-1):
    if ts[j]['word'] in cs:break
    if j in local:left=local[j];break
  for j in range(i+1,len(ts)):
   if ts[j]['word'] in cs:break
   if j in local:right=local[j];break
  issues=[]
  if w=='chey':
   if right:right['negations'].append(t['at'])
   else:issues.append('no_right_predicate')
  else:
   if not left or left['kind']!='state':issues.append('no_left_state')
   if not right:issues.append('no_right_predicate')
   if left and not left['material']:issues.append('left_unbound_material')
   if right and not right['material']:issues.append('right_unbound_material')
  o=dict(record=rid,at=t['at'],word=w,left=left['at'] if left else '',right=right['at'] if right else '',issues=','.join(issues));ops.append(o)
  if w in cs and not issues:rules.append(o)
 for p in local.values():p['negative']=bool(len(p['negations'])%2)
by={p['at']:p for p in props}
# Shared proposition scopes are explicitly detected, not silently duplicated.
for r in rules:
 assert not any(r is not q and {r['left'],r['right']}&{q['left'],q['right']} for q in rules),'overlap requires alternative parse'
for p in props:p['negations']=','.join(p['negations'])
tab('PROPOSITIONS.tsv',props);tab('OPERATORS.tsv',ops);tab('RULES.tsv',rules)
def wording(p):return ('nicht ' if p['negative'] else '')+p['value']+'('+ (p['material'] or '?') +')'
def true(p,world):return (world[p['material']]==p['value']) != p['negative']
cases=[];comparisons=[]
for rid,ts in records.items():
 local=[p for p in props if p['record']==rid];rr=[r for r in rules if r['record']==rid];used={r[k] for r in rr for k in ['left','right']}
 for a,b in itertools.product(['warm','kalt','neutral'],repeat=2):
  world={'A':a,'B':b}
  for mode in ['C','U']:
   active=[p for p in local if mode=='U' or p['at'] not in used];triggered=[]
   if mode=='C':
    for r in rr:
     trigger=true(by[r['left']],world)
     if r['word']=='qokal':trigger=not trigger
     if trigger:active.append(by[r['right']]);triggered.append(r['at'])
   violated=[];required={};forbidden={};unbound=[]
   for p in active:
    if not p['material']:unbound.append(p['at']);continue
    if p['kind']=='state':
     if not true(p,world):violated.append(p['at'])
    else:(forbidden if p['negative'] else required).setdefault(p['value']+'('+p['material']+')',[]).append(p['at'])
   conflict=sorted(set(required)&set(forbidden))
   cases.append(dict(record=rid,mode=mode,A=a,B=b,triggered=','.join(triggered),active=','.join(p['at'] for p in active),required=json.dumps(required,sort_keys=True),forbidden=json.dumps(forbidden,sort_keys=True),violated_states=','.join(violated),action_conflicts=','.join(conflict),unbound=','.join(unbound),consistent=not violated and not conflict))
 for mode in ['C','U']:
  alignment=[];md=['# '+rid+' / '+mode,'']
  for t in ts:
   p=by.get(t['at']);reading=wording(p) if p else lex.get(t['word'],'⟦'+t['word']+'⟧')
   if mode=='U' and t['word'] in cs:reading='und'
   o=next((o for o in ops if o['at']==t['at']),None)
   if o:reading+=' [links='+o['left']+'; rechts='+o['right']+'; offen='+o['issues']+']'
   if p:reading+=' [Material='+p['material_locus']+'; Negationen='+p['negations']+']'
   alignment.append(dict(record=rid,at=t['at'],word=t['word'],reading=reading));md.append(t['at']+' '+reading)
  comparisons.extend(dict(r,mode=mode) for r in alignment)
  (D/(rid+'_'+mode+'.md')).write_text('\n'.join(md)+'\n')
tab('ALL_CASES.tsv',cases)
for mode in ['C','U']:tab('ALIGNMENT_'+mode+'.tsv',[{k:v for k,v in r.items() if k!='mode'} for r in comparisons if r['mode']==mode])
summary=[]
for rid,ts in records.items():summary.append(dict(record=rid,groups=len(ts),hypothesis=sum(t['word'] in lex for t in ts),rules=sum(r['record']==rid for r in rules),C_consistent=sum(r['record']==rid and r['mode']=='C' and r['consistent'] for r in cases),U_consistent=sum(r['record']==rid and r['mode']=='U' and r['consistent'] for r in cases)))
tab('COVERAGE.tsv',summary)
dump('RESULT.json',dict(groups=341,hypothesis_positions=sum(x['hypothesis'] for x in summary),open_positions=341-sum(x['hypothesis'] for x in summary),propositions=len(props),operators=len(ops),bound_rules=len(rules),unbound_operators=sum(bool(o['issues']) for o in ops),negation_tokens=sum(o['word']=='chey' for o in ops),negated_predicates=sum(p['negative'] for p in props),case_rows=len(cases),summary=summary,confirmed_meanings=0))
print((D/'RESULT.json').read_text())
