"""Fixed W28 inputs, frozen W09 alias and W14 timing; no new decoder."""
import ast,collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;B=W/'W28';ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def table(n,rr,cols):
 with (E/n).open('w') as f:
  out=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');out.writeheader();out.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
features=collections.defaultdict(list)
for f in read(W/'W03/SPEC.json')['features']:
 if f['kind']!='STANDALONE':features[f['form']].append(f)
opposed={'moisture':{frozenset(('wet','dry'))},'thermal':{frozenset(('cold','warm')),frozenset(('cold','hot'))}}
ns=dict(json=json,encode=js,features=features,material_roles={'MATERIAL','MATERIAL_DOSE'},opposed=opposed)
for folder,names in [('W09',['js','snapshots','execute']),('W14',['replay'])]:
 ff=[n for n in ast.parse((W/folder/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names];exec(compile(ast.Module(body=ff,type_ignores=[]),'frozen_'+folder,'exec'),ns)
source=read(B/'SOURCE.json')['paragraphs'];targets=[];ev=[];changes=[];later=[];summary=[];baseline_count=0
for sm in S['shol_models']:
 flats=rows(B/(sm+'_SOURCE_FLAT.tsv'));args=rows(B/(sm+'_ARGUMENTS.tsv'));quals=rows(B/(sm+'_QUALITY.tsv'));inputs=rows(B/(sm+'_INPUT_ELIGIBILITY.tsv'));old=rows(B/(sm+'_EVENTS.tsv'))
 for p in source:
  flat=[{k:(int(r[k]) if k in ['index','offset'] else r[k]) for k in ['id','locus','index','form','role','offset']} for r in flats if r['paragraph']==p['id']];byid={r['id']:r for r in flat}
  tt=[x for x in flat if x['form']=='sal'];assert len(tt)<=1
  for g in ['B','J','M']:
   aa=[r for r in args if r['paragraph']==p['id'] and r['grammar']==g];qq=[r for r in quals if r['paragraph']==p['id'] and r['grammar']==g];shifts={r['mention']:byid[r['patient']]['offset'] for r in inputs if r['paragraph']==p['id'] and r['grammar']==g and r['input_eligible']=='True'}
   for model in S['models']:
    effects=read(W/'W09/SPEC.json')['effects'];effects['chol']=S['models'][model]
    if sm=='A':effects['shol']={'axis':'moisture','value':'wet'}
    ns['S']={'effects':effects};base,_,_=ns['execute'](flat,aa,qq)
    for timing in S['timings']:
     trE=ns['replay'](base,shifts if timing=='I' else {});oo=[r for r in old if r['paragraph']==p['id'] and r['grammar']==g and r['model']==model and r['timing']==timing]
     assert len(oo)==len(trE)
     for before,(_,after) in zip(oo,trE):assert all(before[k]==str(after[k]) for k in after),(p['id'],g,model,timing,before,after)
     baseline_count+=1
     if not tt:continue
     target=tt[0];prior=[x for x in flat if x['offset']<target['offset'] and x['role'] in ns['material_roles']];assert prior
     parent=prior[-1];rawR,_,_=ns['execute'](flat,aa,qq,target=target['id'],parent_form=parent['form']);trR=ns['replay'](rawR,shifts if timing=='I' else {})
     te=next(r for _,r in trE if r['kind']=='MATERIAL' and r['location']==target['id']);pr=next(r for _,r in trE if r['kind']=='MATERIAL' and r['location']==parent['id']);oid=pr['object'];targetobj=te['object']
     earlier=[r for _,r in trE if r['kind']=='ACTION' and r['object']==oid and byid[r['location']]['offset']<target['offset'] and int(r['order'])<target['offset'] and r['status']=='ASSUMED_EFFECT_APPLIED']
     meta=dict(shol=sm,paragraph=p['id'],grammar=g,chol=model,timing=timing,target=target['id']);targets.append(dict(**meta,antecedent=parent['id'],antecedent_form=parent['form'],antecedent_object=oid,earlier_applied_actions=';'.join(r['location'] for r in earlier),E_state=te['before'],R_state=next(r['before'] for _,r in trR if r['kind']=='MATERIAL' and r['location']==target['id'])))
     for reference,trace in [('E',trE),('R',trR)]:
      for serial,(i,r) in enumerate(trace):ev.append(dict(**meta,reference=reference,source_event=i,execution_index=serial,**r))
      summary.append(dict(**meta,reference=reference,events=len(trace),conflicts=sum(r['status']=='CONFLICT' for _,r in trace),unequal=sum(r['status']=='DIFFERENT_NOT_OPPOSED' for _,r in trace),missing=sum(r['status']=='MISSING_PATIENT' for _,r in trace),incomplete=sum(r['status']=='ARGUMENT_INCOMPLETE' for _,r in trace)))
     assert len(trE)==len(trR)
     for (i,a),(j,b) in zip(trE,trR):
      assert i==j and (a['kind'],a['location'],a['assertion'])==(b['kind'],b['location'],b['assertion'])
      diff=[k for k in a if str(a[k])!=str(b[k])]
      if diff:changes.append(dict(**meta,event=i,location=a['location'],kind=a['kind'],fields=';'.join(diff),E=js(a),R=js(b)))
      # Include all later-executed requirements on source/target, not just written-later tokens.
      after=int(a['order'])>=target['offset'] and not (a['kind']=='MATERIAL' and a['location']==target['id'])
      if after and a['kind']!='MATERIAL' and (a['object'] in [oid,targetobj] or a['second_object'] in [oid,targetobj]):
       later.append(dict(**meta,event=i,location=a['location'],kind=a['kind'],form=a['form'],written_before_target=byid[a['location']]['offset']<target['offset'],E_object=a['object'],R_object=b['object'],E_before=a['before'],R_before=b['before'],E_after=a['after'],R_after=b['after'],E_status=a['status'],R_status=b['status'],constraint_discriminator=a['kind']!='ACTION' and a['status']!=b['status'],debts=a['debts']))
meta=['shol','paragraph','grammar','chol','timing','target']
table('TARGETS.tsv',targets,meta+['antecedent','antecedent_form','antecedent_object','earlier_applied_actions','E_state','R_state'])
table('EVENTS.tsv',ev,list(ev[0]));table('ALL_CHANGES.tsv',changes,list(changes[0]));table('ALL_LATER_REQUIREMENTS.tsv',later,list(later[0]));table('WORLD_SUMMARY.tsv',summary,list(summary[0]))
res=dict(idea='IDEA000226',source_paragraphs=len(source),baseline_worlds_replayed=baseline_count,target_cases=len(targets),reference_worlds=len(summary),events=len(ev),changes=len(changes),later_requirements=len(later),constraint_discriminators=sum(r['constraint_discriminator'] for r in later),new_R_conflicts=sum(json.loads(r['R'])['status']=='CONFLICT' and json.loads(r['E'])['status']!='CONFLICT' for r in changes),independent_confirmation_capacity=0,confirmed_meanings=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
