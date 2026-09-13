"""Independent all-target history scan, without importing the builder."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(p):return json.loads(p.read_text())
s=js(E/'SPEC.json')
for f in s['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
lex={r['form']:r for r in rows(W/'W02/LEXICON.tsv')};forms={w for w,r in lex.items() if r['role'] in s['roles']};assert forms=={'ykeey','yteey'}
worlds=collections.defaultdict(list)
for r in rows(W/'W14/EVENTS.tsv'):worlds[(r['timing'],r['candidate'],r['world'])].append(r)
results=rows(E/'TARGETS.tsv');assert len(results)==60
hist=rows(E/'OBJECT_HISTORY.tsv');futures=rows(E/'FUTURES.tsv');phys=rows(E/'PHYSICAL_EVIDENCE.tsv')
expectedkeys=set()
for key,rr in worlds.items():
 rr.sort(key=lambda x:int(x['execution_index']))
 for i,t in enumerate(rr):
  if t['kind']!='ACTION' or t['form'] not in forms:continue
  expectedkeys.add(key+(t['location'],))
assert {(r['timing'],r['chol'],r['world'],r['target']) for r in results}==expectedkeys
for t in results:
 key=(t['timing'],t['chol'],t['world']);rr=worlds[key];idx=next(i for i,r in enumerate(rr) if r['kind']=='ACTION' and r['location']==t['target']);target=rr[idx]
 assert t['object']==target['object'] and t['patient']==target['patient']
 assert t['target_before']==target['before'] and t['target_after']==target['after']
 earlier=[(i,r) for i,r in enumerate(rr[:idx]) if r['object']==target['object'] and target['object']]
 def select(data):return [r for r in data if (r['timing'],r['chol'],r['world'],r['target'])==key+(t['target'],)]
 hh=select(hist);assert [(int(r['prior_index']),r['prior_location'],r['prior_kind']) for r in hh]==[(i,r['location'],r['kind']) for i,r in earlier]
 matching=[];states=[];eff=json.loads(target['assertion']);statekey='PHYSICAL:'+eff['axis']
 for i,r in earlier:
  if r['kind']=='ACTION' and r['status']=='ASSUMED_EFFECT_APPLIED':
   e=json.loads(r['assertion'])
   if e==eff:matching.append(r['location'])
   if e['axis']==eff['axis']:states.append((i,r['location'],e['value']))
  elif r['status'] in ('MATCH','INITIAL_CONSTRAINT') and r['assertion'].startswith(statekey+'='):states.append((i,r['location'],r['assertion'].split('=',1)[1]))
 assert not matching and t['REP_witnesses']=='0'
 # Target effects are warm or cold; warm/hot remain distinct.
 def opposite(v):return (eff['value']=='cold' and v in ('warm','hot')) or (eff['value'] in ('warm','hot') and v=='cold')
 pairs=[(a,b) for a in states for b in states if a[0]<b[0] and a[2]==eff['value'] and opposite(b[2])]
 assert not pairs and t['REST_pairs']=='0'
 assert {(int(r['prior_index']),r['prior_location'],r['physical_value']) for r in select(phys)}==set(states)
 ff=select(futures);assert [(int(r['later_index']),r['later_location'],r['later_kind']) for r in ff]==[(i,r['location'],r['kind']) for i,r in enumerate(rr[idx+1:],idx+1)]
assert not rows(E/'REP_WITNESSES.tsv') and not rows(E/'REST_WITNESSES.tsv')
source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];expected=[];positions={};wordmaps={}
for ed,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];rr=[]
  for l in p['lines']:
   assert not l['locus'].startswith('f84')
   rr.extend((l['locus']+':'+str(i),g['ivtff_group_raw']) for i,g in enumerate(mapped[l['locus']]['groups'],1))
  positions[(ed,p['id'])]={loc:i for i,(loc,w) in enumerate(rr)};wordmaps[(ed,p['id'])]=dict(rr)
  expected.extend((ed,p['id'],loc,w) for loc,w in rr if w in forms)
assert set(expected)=={(r['edition'],r['paragraph'],r['target'],r['form']) for r in rows(E/'WORD_CENSUS.tsv')}
assert len(expected)==15
args=rows(W/'W05/ARGUMENTS.tsv');effects=js(W/'W09/SPEC.json')['effects'];checks=rows(E/'ALTERNATE_ACTION_CHECK.tsv');assert len(checks)==60
for t in checks:
 pos=positions[(t['edition'],t['paragraph'])];aa=[a for a in args if (a['edition'],a['paragraph'],a['variant'])==(t['edition'],t['paragraph'],t['grammar'])]
 def order(a):return max(pos[v] for v in (a['operation'],a['patient'],a['coingredient']) if v),pos[a['operation']]
 aa.sort(key=order);i=next(i for i,a in enumerate(aa) if a['operation']==t['target']);target=aa[i]
 eff=dict(effects);eff['chol']={'axis':'moisture','value':'dry'} if t['chol']=='D' else {'axis':'thermal','value':'hot'}
 prior=[a for a in aa[:i] if a['patient_form']==target['patient_form'] and target['patient_form'] and eff.get(a['form'])==eff[target['form']] and 'EXTRACT_PATIENT_NOT_BOUND' not in a['debts'] and 'MISSING_RELATION_PARTNER' not in a['debts']]
 assert not prior and t['prior_actions']==''
for a,b in zip(rows(W/'W14/ALIGNMENT.tsv'),rows(E/'ALIGNMENT.tsv')):
 for k,v in a.items():assert b[k]==v
assert len(rows(E/'ALIGNMENT.tsv'))==900
result={'status':'PASS','all_source_and_registration_hashes':True,'primary_targets':5,'primary_context_rows_checked':60,'alternate_action_rows_checked':60,'complete_object_histories_and_futures':True,'REP_witnesses':0,'REST_pairs':0,'primary_groups':900,'semantic_validation':False,'independent_confirmation_capacity':0}
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
