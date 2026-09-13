"""Complete action-only sensitivity test of existing repeat hypotheses."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];effects=read(W/'W09/SPEC.json')['effects'];effects['chol']={'axis':'thermal','value':'hot'};offset={};contexts=[]
for ed,ll in alt.items():
 lines={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];off={}
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84');words=lines[loc]
   if ed=='ZL3b':assert words==line['words']
   for i,w in enumerate(words,1):
    key=loc+':'+str(i);off[key]=len(off)
    if w in S['targets']:contexts.append(dict(edition=ed,paragraph=p['id'],target=key,form=w,raw_line=' '.join(words)))
  offset[(ed,p['id'])]=off
worlds=collections.defaultdict(list);actions=[]
for old in rows(W/'W17/ACTION_CONSEQUENCES.tsv'):
 r=old.copy();off=offset[(r['edition'],r['paragraph'])];positions=[off[r['operation']]]+[off[r[k]] for k in ('patient','second') if r[k]]
 r['execution_offset']=max(positions);r['written_offset']=off[r['operation']];r['effect']=json.dumps(effects.get(r['form']),sort_keys=True)
 r['valid']=bool(r['object']) and r['type_status']!='EXTRACT_NOT_BOUND' and r['missing_reference']=='False' and 'MISSING_RELATION_PARTNER' not in r['old_debts']
 worlds[(r['edition'],r['paragraph'],r['model'],r['grammar'])].append(r)
targets=[];pairs=[];witness=[]
for key,aa in worlds.items():
 aa.sort(key=lambda r:(r['execution_offset'],r['written_offset']));actions+=aa
 for i,r in enumerate(aa):
  if r['form'] not in S['targets']:continue
  good=[]
  for prev in aa[:i]:
   reason='INVALID_PRIOR_ACTION' if not prev['valid'] else 'NO_MODELED_EFFECT' if prev['effect']=='null' else 'DIFFERENT_OBJECT' if not r['object'] or prev['object']!=r['object'] else 'DIFFERENT_EFFECT' if prev['effect']!=r['effect'] else 'EXACT_EFFECT_WITNESS'
   row=dict(edition=r['edition'],paragraph=r['paragraph'],model=r['model'],grammar=r['grammar'],target=r['operation'],target_object=r['object'],prior=prev['operation'],prior_form=prev['form'],prior_object=prev['object'],prior_effect=prev['effect'],status=reason,prior_debts=prev['remaining_non_type_debts'])
   pairs.append(row)
   if reason=='EXACT_EFFECT_WITNESS':good.append(prev);witness.append(row)
  targets.append(dict(edition=r['edition'],paragraph=r['paragraph'],model=r['model'],grammar=r['grammar'],target=r['operation'],form=r['form'],patient=r['patient'],object=r['object'],object_form=r['object_form'],valid=r['valid'],effect=r['effect'],witness_count=len(good),witnesses=';'.join(x['operation'] for x in good),debts=r['remaining_non_type_debts']))
old={(r['model'],r['world'].split('|',3)[2],r['target'],r['witness'],r['object']) for r in rows(W/'W18/REPEAT_WITNESSES.tsv') if r['kind']=='REP_EXACT'}
new={(r['model'],r['grammar'],r['target'],r['prior'],r['target_object']) for r in witness if r['edition']=='ZL3b'};assert old==new
for ed in alt:
 rawtargets={(r['paragraph'],r['target']) for r in contexts if r['edition']==ed}
 for m in S['models']:
  for g in S['grammars']:assert {(r['paragraph'],r['target']) for r in targets if (r['edition'],r['model'],r['grammar'])==(ed,m,g)}==rawtargets
summ=[dict(edition=ed,model=m,targets=sum(r['edition']==ed and r['model']==m for r in targets),positive_targets=sum(r['edition']==ed and r['model']==m and r['witness_count']>0 for r in targets),positive_loci=';'.join(sorted({r['target'] for r in targets if r['edition']==ed and r['model']==m and r['witness_count']>0})),witness_rows=sum(r['edition']==ed and r['model']==m for r in witness)) for ed in alt for m in S['models']]
table('ACTIONS.tsv',actions);table('TARGETS.tsv',targets);table('ALL_PRIOR_ACTIONS.tsv',pairs);table('WITNESSES.tsv',witness);table('CONTEXTS.tsv',contexts);table('SUMMARY.tsv',summ)
result={'action_rows':len(actions),'target_rows':len(targets),'prior_action_comparisons':len(pairs),'witness_rows':len(witness),'primary_W18_parity':True,'summary':summ,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_access':False,'state_simulation':False}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
