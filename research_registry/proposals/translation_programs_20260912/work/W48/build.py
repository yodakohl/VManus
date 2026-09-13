import ast,copy,csv,hashlib,json,re
from collections import Counter
from pathlib import Path
DROOT=Path(__file__).parent;S=json.loads((DROOT/'SPEC.json').read_text())
def read(p):return json.loads(Path(p).read_text())
def rows(p):return list(csv.DictReader(Path(p).open(),delimiter='\t'))
def table(n,rr,cols):
 with (DROOT/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
rules=read(S['rules']);ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts=set(S['extracts']);glosses={}
D={r['form']:r for r in rows(S['lexicon'])}
for p,name in zip(S['functions'],['base_arguments','solve']):
 fn=next(n for n in ast.parse(Path(p).read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_'+name,'exec'))
ctx=read(S['context']);args=[];pairs=[];targets=[];uses=[];flatrows=[];summaries=[]
for branch,path in S['roles'].items():
 roles={r['form']:r['role'] for r in rows(path)}
 for word,role in roles.items():
  if word not in D:D[word]={'hypothesis':'UNCONFIRMED_ROLE_ONLY'}
 for p in ctx['paragraphs']:
  assert not p['page'].startswith('f84');ed=p['edition'];pid=p['id'];flat=[]
  for l in p['lines']:
   for i,word in enumerate(l['words'],1):flat.append(dict(id=l['locus']+':'+str(i),locus=l['locus'],index=i,form=word,role=roles.get(word,'OPEN'),offset=len(flat)))
  flatrows.extend(dict(branch=branch,edition=ed,paragraph=pid,**x) for x in flat);by={x['id']:x for x in flat}
  for grammar,aa in solve(flat).items():
   for a in aa:a['completion']=max(by[q]['offset'] for q in [a['operation'],a['patient'],a['coingredient']] if q)
   args.extend(dict(branch=branch,edition=ed,paragraph=pid,grammar=grammar,**a) for a in aa)
   ss=[a for a in aa if a['form']=='sheey'];qq=[a for a in aa if a['form']=='qokeor']
   for a in ss:
    future=[q for q in qq if q['completion']>a['completion']]
    targets.append(dict(branch=branch,edition=ed,paragraph=pid,grammar=grammar,operation=a['operation'],patient=a['patient'],patient_form=a['patient_form'],debts=a['debts'],later_typed_uses=len(future),same_material_uses=sum(bool(a['patient']) and a['patient_form']==q['patient_form'] for q in future)))
    for q in future:
     same=bool(a['patient'] and q['patient'] and a['patient_form']==q['patient_form']);initial=q['patient_form'] in extracts
     between=[x['id'] for x in flat if a['completion']<x['offset']<q['completion'] and x['role']=='OPEN']
     intervening=[x['operation'] for x in aa if a['completion']<x['completion']<q['completion'] and same and x['patient_form']==a['patient_form']]
     status='MISSING_PATIENT' if not a['patient'] or not q['patient'] else 'DIFFERENT_MATERIAL' if not same else 'ALREADY_EXTRACT' if initial else 'CONDITIONAL_TYPE_DIFFERENCE'
     pairs.append(dict(branch=branch,edition=ed,paragraph=pid,grammar=grammar,sheey=a['operation'],sheey_patient=a['patient'],sheey_material=a['patient_form'],qokeor=q['operation'],qokeor_patient=q['patient'],qokeor_material=q['patient_form'],W_type='EXTRACT' if initial else 'UNKNOWN',E_type='EXTRACT' if initial or same else 'UNKNOWN',status=status,NEW_continuity='SAME_MENTION' if same and a['patient']==q['patient'] else 'NOT_ESTABLISHED',unread_between=';'.join(between),intervening_actions=';'.join(intervening),sheey_debts=a['debts'],qokeor_debts=q['debts'],seam_native_status='UNVERIFIED'))
   for q in qq:
    prev=[a for a in ss if a['completion']<q['completion']];same=[a for a in prev if a['patient'] and q['patient'] and a['patient_form']==q['patient_form']]
    uses.append(dict(branch=branch,edition=ed,paragraph=pid,grammar=grammar,qokeor=q['operation'],patient=q['patient'],material=q['patient_form'],prior_sheey=len(prev),same_material_prior=len(same),W_type='EXTRACT' if q['patient_form'] in extracts else 'UNKNOWN',E_type='EXTRACT' if q['patient_form'] in extracts or same else 'UNKNOWN',debts=q['debts']))
   summaries.append(dict(branch=branch,edition=ed,paragraph=pid,grammar=grammar,groups=len(flat),actions=len(aa),sheey=len(ss),qokeor=len(qq)))
table('SOURCE_FLAT.tsv',flatrows,['branch','edition','paragraph','id','locus','index','form','role','offset'])
table('ARGUMENTS.tsv',args,['branch','edition','paragraph','grammar','operation','form','meaning','patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption','completion'])
table('TARGETS.tsv',targets,['branch','edition','paragraph','grammar','operation','patient','patient_form','debts','later_typed_uses','same_material_uses'])
table('ALL_PAIRS.tsv',pairs,['branch','edition','paragraph','grammar','sheey','sheey_patient','sheey_material','qokeor','qokeor_patient','qokeor_material','W_type','E_type','status','NEW_continuity','unread_between','intervening_actions','sheey_debts','qokeor_debts','seam_native_status'])
table('ALL_TYPED_USES.tsv',uses,['branch','edition','paragraph','grammar','qokeor','patient','material','prior_sheey','same_material_prior','W_type','E_type','debts'])
table('PARAGRAPHS.tsv',summaries,['branch','edition','paragraph','grammar','groups','actions','sheey','qokeor'])
missing=[r for r in rows(S['occurrences']) if r['paragraph']=='NO_COMPLETE_PARAGRAPH'];table('NO_PARAGRAPH_CAPACITY.tsv',missing,[k for k in missing[0] if k!='row_status'] if missing else ['edition','source_id'])
# DictReader rows already have row_status; table overwrites it with the same value.
res=dict(paragraphs=len(ctx['paragraphs']),paragraph_worlds=len(summaries),target_cases=len(targets),typed_use_cases=len(uses),all_forward_pairs=len(pairs),statuses=dict(Counter(r['status'] for r in pairs)),different_type_uses=sum(r['W_type']!=r['E_type'] for r in uses),missing_paragraph_reading_occurrences=len(missing),independent_meaning_confirmations=0)
(DROOT/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
# Reproducible complete raw reader and equivalence projection, no extra target selection.
leadkeys={(r['edition'],r['paragraph']) for r in pairs if r['status']=='CONDITIONAL_TYPE_DIFFERENCE'}
leadids={pid for ed,pid in leadkeys}
reader=['# W48 vollständige Quellabsätze der bedingten Typdifferenz','','Keine vollständige Übersetzung. Untersucht: cheo als Zubereitung, sheey als Benetzen/Auszug herstellen, qokeor als Auszug erhitzen. Alle drei Bedeutungen bleiben Annahmen; SAME verbindet wiederholte Materialnamen, NEW lässt andere Portionen offen. Alle anderen Rohgruppen bleiben unverändert sichtbar.','']
for p in ctx['paragraphs']:
 if p['id'] in leadids:
  reader+=['## '+p['edition']+' '+p['id']+' — '+str(p['groups'])+' Gruppen','']
  for l in p['lines']:reader+=[l['locus']+' `'+ ' '.join(l['words'])+'`','']
(DROOT/'READING.md').write_text('\n'.join(reader)+'\n')
cols=['edition','paragraph','sheey','sheey_material','qokeor','qokeor_material','status','NEW_continuity'];groups={}
for r in pairs:groups.setdefault(tuple(r[c] for c in cols),[]).append(r['branch']+'/'+r['grammar'])
table('PREDICTION_GROUPS.tsv',[dict(zip(cols,k),dependent_variants=';'.join(v)) for k,v in groups.items()],cols+['dependent_variants'])
