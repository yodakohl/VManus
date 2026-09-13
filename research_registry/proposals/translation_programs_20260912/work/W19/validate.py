"""Full independent pair census from fixed action records and raw positions."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
s=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
for r in s['inputs']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];positions={};rawtargets=set()
for ed,ll in alt.items():
 lines={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];off=0
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84')
   if ed=='ZL3b':assert lines[loc]==line['words']
   for i,w in enumerate(lines[loc],1):
    mention=loc+':'+str(i);positions[(ed,p['id'],mention)]=off;off+=1
    if w in s['targets']:rawtargets.add((ed,p['id'],mention))
key=lambda r:(r['edition'],r['paragraph'],r['model'],r['grammar'],r['operation'])
old={key(r):r for r in rows(W/'W17/ACTION_CONSEQUENCES.tsv')};aa=rows(E/'ACTIONS.tsv');assert len(aa)==len(old)==2763;groups=collections.defaultdict(list)
effects=read(W/'W09/SPEC.json')['effects'];effects['chol']={'axis':'thermal','value':'hot'}
for a in aa:
 b=old.pop(key(a));assert all(a[k]==v for k,v in b.items());prefix=(a['edition'],a['paragraph']);times=[positions[prefix+(a[k],)] for k in ['operation','patient','second'] if a[k]]
 assert int(a['execution_offset'])==max(times) and int(a['written_offset'])==positions[prefix+(a['operation'],)]
 assert json.loads(a['effect'])==effects.get(a['form'])
 valid=bool(a['object']) and a['type_status']!='EXTRACT_NOT_BOUND' and a['missing_reference']=='False' and 'MISSING_RELATION_PARTNER' not in a['old_debts'];assert (a['valid']=='True')==valid
 groups[key(a)[:4]].append(a)
assert not old
expected={};targets={}
for group,rr in groups.items():
 for t in rr:
  if t['form'] not in s['targets']:continue
  tt=(int(t['execution_offset']),int(t['written_offset']));good=[]
  for a in rr:
   at=(int(a['execution_offset']),int(a['written_offset']))
   if at>=tt:continue
   status='INVALID_PRIOR_ACTION' if a['valid']!='True' else 'NO_MODELED_EFFECT' if json.loads(a['effect']) is None else 'DIFFERENT_OBJECT' if not t['object'] or a['object']!=t['object'] else 'DIFFERENT_EFFECT' if json.loads(a['effect'])!=json.loads(t['effect']) else 'EXACT_EFFECT_WITNESS'
   expected[group+(t['operation'],a['operation'])]=status
   if status=='EXACT_EFFECT_WITNESS':good.append((at,a['operation']))
  targets[group+(t['operation'],)]=[op for _,op in sorted(good)]
pp=rows(E/'ALL_PRIOR_ACTIONS.tsv');assert len(pp)==len(expected)==837
for r in pp:assert r['status']==expected.pop((r['edition'],r['paragraph'],r['model'],r['grammar'],r['target'],r['prior']))
assert not expected
tr=rows(E/'TARGETS.tsv');assert len(tr)==len(targets)==135
for r in tr:
 kk=(r['edition'],r['paragraph'],r['model'],r['grammar'],r['target']);ww=targets.pop(kk);assert r['witnesses']==';'.join(ww) and int(r['witness_count'])==len(ww)
assert not targets
assert {(r['edition'],r['paragraph'],r['target']) for r in tr}==rawtargets
ww=rows(E/'WITNESSES.tsv');positive=[r for r in pp if r['status']=='EXACT_EFFECT_WITNESS'];assert ww==positive and len(ww)==18
v={'status':'PASS','legacy_files_verified':len(s['inputs']),'actions':2763,'repeat_targets':135,'complete_prior_pairs':837,'witnesses':18,'distinct_positive_loci':['f102v2.38:8'],'editions':['ZL3b','IT2a','RF1b'],'semantic_confirmation':False}
(E/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
