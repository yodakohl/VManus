"""Audit existing again-presuppositions without changing any event or word."""
import csv,collections,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def js(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr,cols=None):
 cols=cols or list(rr[0])
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=[k for k in cols if k!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=js(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
lex={r['form']:r for r in rows(W/'W02/LEXICON.tsv')};forms={w for w,r in lex.items() if r['role'] in S['roles']};effects=js(W/'W09/SPEC.json')['effects'];source=js(W/'W02/SOURCE.json');alt=js(W/'W02/ALTERNATE_LINES.json')['readings'];opposed={'thermal':{frozenset(('cold','warm')),frozenset(('cold','hot'))},'moisture':{frozenset(('wet','dry'))}}
worlds=collections.defaultdict(list)
for r in rows(W/'W14/EVENTS.tsv'):worlds[(r['timing'],r['candidate'],r['world'])].append(r)
results=[];rep=[];restore=[];history=[];future=[];evidence=[]
for (timing,chol,world),trace in worlds.items():
 trace.sort(key=lambda x:int(x['execution_index']))
 for i,t in enumerate(trace):
  if t['kind']!='ACTION' or t['form'] not in forms:continue
  effect=json.loads(t['assertion']);axis=effect['axis'];value=effect['value'];oid=t['object'];key='PHYSICAL:'+axis
  base=dict(timing=timing,chol=chol,world=world,target=t['location'],form=t['form'],object=oid,patient=t['patient'],axis=axis,value=value)
  prior=[(j,r) for j,r in enumerate(trace[:i]) if oid and r['object']==oid]
  hits=[];observed=[]
  for j,r in prior:
   history.append(dict(**base,prior_index=j,prior_kind=r['kind'],prior_location=r['location'],prior_form=r['form'],prior_status=r['status'],prior_assertion=r['assertion'],prior_before=r['before'],prior_after=r['after'],prior_debts=r['debts']))
   val=None
   if r['kind']=='ACTION' and r['status']=='ASSUMED_EFFECT_APPLIED' and r['assertion']:
    e=json.loads(r['assertion'])
    if e['axis']==axis:
     val=e['value']
     if val==value:
      hits.append(r['location']);rep.append(dict(**base,prior_action=r['location'],prior_form=r['form'],prior_debts=r['debts'],evidence='SAME_EFFECT_CLASS_AND_ASSUMED_OBJECT_NOT_PROVEN_SAME_PROCEDURE'))
   elif r['kind'] in ('QUALITY','PROCESSED_NOMINAL','BARE_NOMINAL') and r['status'] in ('INITIAL_CONSTRAINT','MATCH') and r['assertion'].startswith(key+'='):val=r['assertion'].split('=',1)[1]
   if val is not None:
    observed.append((j,r['location'],val,r['kind']));evidence.append(dict(**base,prior_index=j,prior_location=r['location'],prior_kind=r['kind'],physical_value=val,evidence_status=r['status']))
  pairs=[(a,b) for a in observed for b in observed if a[0]<b[0] and a[2]==value and frozenset((value,b[2])) in opposed[axis]]
  for a,b in pairs:restore.append(dict(**base,old_target_state=a[1],old_target_kind=a[3],intervening_opposite=b[1],opposite_kind=b[3],opposite_value=b[2]))
  valid=t['status']=='ASSUMED_EFFECT_APPLIED'
  results.append(dict(**base,target_status=t['status'],target_before=t['before'],target_after=t['after'],target_debts=t['debts'],REP_witnesses=len(hits),REST_pairs=len(pairs),REP='SUPPORTED_CONDITIONALLY' if valid and hits else 'TARGET_NOT_EXECUTABLE' if not valid else 'NO_PRIOR_MATCHING_ACTION',REST='SUPPORTED_CONDITIONALLY' if valid and pairs else 'TARGET_NOT_EXECUTABLE' if not valid else 'NO_PRIOR_TARGET_THEN_OPPOSITE',prior_constitution_rows=sum(r['kind']=='BARE_NOMINAL' for _,r in prior)))
  for j,r in enumerate(trace[i+1:],i+1):future.append(dict(**base,later_index=j,later_kind=r['kind'],later_location=r['location'],later_object=r['object'],same_object=bool(oid and r['object']==oid),later_status=r['status'],later_before=r['before'],later_after=r['after']))
table('TARGETS.tsv',results);table('REP_WITNESSES.tsv',rep,['timing','chol','world','target','form','object','patient','axis','value','prior_action','prior_form','prior_debts','evidence']);table('REST_WITNESSES.tsv',restore,['timing','chol','world','target','form','object','patient','axis','value','old_target_state','old_target_kind','intervening_opposite','opposite_kind','opposite_value']);table('OBJECT_HISTORY.tsv',history);table('PHYSICAL_EVIDENCE.tsv',evidence,['timing','chol','world','target','form','object','patient','axis','value','prior_index','prior_location','prior_kind','physical_value','evidence_status']);table('FUTURES.tsv',future)
# Entire word census plus independent alternate-action sensitivity, no quality transfer.
args=rows(W/'W05/ARGUMENTS.tsv');census=[];altchecks=[];contexts=[]
for edition,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for host in source['targets']:
  p=host['hosts']['ZL3b'][0];rr=[]
  for l in p['lines']:
   assert not l['locus'].startswith('f84')
   for i,g in enumerate(mapped[l['locus']]['groups'],1):rr.append((l['locus']+':'+str(i),l['locus'],g['ivtff_group_raw']))
  pos={x[0]:i for i,x in enumerate(rr)};targets=[x for x in rr if x[2] in forms]
  for loc,locus,form in targets:census.append(dict(edition=edition,paragraph=p['id'],target=loc,form=form,meaning=lex[form]['hypothesis']))
  if targets:
   for l in p['lines']:contexts.append(dict(edition=edition,paragraph=p['id'],locus=l['locus'],raw_line=' '.join(w for _,loc,w in rr if loc==l['locus'])))
  if edition=='ZL3b':continue
  for grammar in ('B','J','M'):
   aa=[a for a in args if (a['edition'],a['variant'],a['paragraph'])==(edition,grammar,p['id'])]
   def order(a):return (max(pos[z] for z in [a['operation'],a['patient'],a['coingredient']] if z),pos[a['operation']])
   aa.sort(key=order)
   for chol in ('D','H'):
    eff={**effects,'chol':{'axis':'moisture','value':'dry'} if chol=='D' else {'axis':'thermal','value':'hot'}}
    for i,t in enumerate(aa):
     if t['form'] not in forms:continue
     prior=[a for a in aa[:i] if t['patient_form'] and a['patient_form']==t['patient_form'] and eff.get(a['form'])==eff[t['form']] and 'EXTRACT_PATIENT_NOT_BOUND' not in a['debts'] and 'MISSING_RELATION_PARTNER' not in a['debts']]
     altchecks.append(dict(edition=edition,chol=chol,grammar=grammar,paragraph=p['id'],target=t['operation'],form=t['form'],patient=t['patient'],patient_form=t['patient_form'],prior_actions=';'.join(a['operation'] for a in prior),REP='SUPPORTED_CONDITIONALLY' if prior else 'NO_PRIOR_MATCHING_ACTION',REST='NOT_TESTED_NO_QUALITY_TRANSFER',debts=t['debts']))
table('WORD_CENSUS.tsv',census);table('ALTERNATE_ACTION_CHECK.tsv',altchecks);table('COMPLETE_CONTEXTS.tsv',contexts)
align=rows(W/'W14/ALIGNMENT.tsv');out=[];reader=['# W15 — vollständige Arbeitslesung mit geprüfter erneut-Verpflichtung','Keine Wortänderung. Erneut bleibt eine zu prüfende Hypothese; W14 I-Markierung erhalten.']
for r in align:out.append(dict(r,repeat_obligation='REP_or_REST_requires_prior_same_object_evidence' if r['raw'] in forms else 'UNCHANGED'))
for p in dict.fromkeys(r['paragraph'] for r in out):
 reader+=['','## '+p]
 for l in dict.fromkeys(r['locus'] for r in out if r['paragraph']==p):
  rr=[r for r in out if r['locus']==l];reader+=['',l+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['H']+(' {erneut-Verpflichtung: siehe TARGETS}' if r['raw'] in forms else '')+(' {I-Eingangsattribut: '+r['input_attribute_grammars']+'}' if r['input_attribute_grammars'] else '') for r in rr)]
table('ALIGNMENT.tsv',out);(E/'READING.md').write_text('\n'.join(reader)+'\n')
result={'forms':sorted(forms),'primary_targets':sum(r['edition']=='ZL3b' for r in census),'target_counts':{e:sum(r['edition']==e for r in census) for e in alt},'primary_world_target_rows':len(results),'REP_supported_rows':sum(r['REP']=='SUPPORTED_CONDITIONALLY' for r in results),'REST_supported_rows':sum(r['REST']=='SUPPORTED_CONDITIONALLY' for r in results),'alternate_action_rows':len(altchecks),'alternate_REP_supported':sum(r['REP']=='SUPPORTED_CONDITIONALLY' for r in altchecks),'primary_groups':len(out),'meaning_confirmations':0,'independent_confirmation_capacity':0,'held_access':False}
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
