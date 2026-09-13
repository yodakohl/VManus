"""Fixed whole-noun reference alternatives, with downstream typed consequences."""
import collections,csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def save(n,v):(E/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def table(n,rr,cols=None):
 cols=[k for k in (cols or list(rr[0])) if k!='row_status']+['row_status']
 with (E/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];lex={r['form']:r for r in rows(W/'W02/LEXICON.tsv')};lex['sheeody']={'role':'MATERIAL','hypothesis':'Pulver [Materialhypothese]'}
liquids=set(S['specific_liquids']);extracts=set(S['extract_types']);mat={'MATERIAL','MATERIAL_DOSE'}
assert all(lex[w]['role'] in mat for w in liquids);assert 'okeeor' not in lex
args=[r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'];takes=[r for r in rows(W/'W16/TAKE_ARGUMENTS.tsv') if r['model']=='PR'];qualities=[r for r in rows(W/'W16/QUALITY_BINDINGS.tsv') if r['model']=='PR']
flats={};objects={};targets=[];priorrows=[];objectrows=[];context=[]
for ed,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for line in p['lines']:
   loc=line['locus'];assert not loc.startswith('f84');words=[z['ivtff_group_raw'] for z in mapped[loc]['groups']]
   if ed=='ZL3b':assert words==line['words']
   for i,w in enumerate(words,1):flat.append(dict(id=loc+':'+str(i),locus=loc,index=i,form=w,offset=len(flat),role=lex.get(w,{}).get('role','OPEN')))
  flats[(ed,p['id'])]=flat;materials=[x for x in flat if x['role'] in mat];first={}
  for x in materials:first.setdefault(x['form'],x)
  shos=[x for x in flat if x['form']=='sho'];byid={x['id']:x for x in flat}
  for x in shos:
   for y in materials:
    if y['offset']<x['offset']:priorrows.append(dict(edition=ed,paragraph=p['id'],target=x['id'],prior=y['id'],form=y['form'],specific_liquid=y['form'] in liquids,offset=y['offset']))
   context.append(dict(edition=ed,paragraph=p['id'],target=x['id'],raw_line=' '.join(y['form'] for y in flat if y['locus']==x['locus'])))
  for m in S['models']:
   mapping={x['id']:first[x['form']]['id'] for x in materials};anchor=None;selected={}
   for i,x in enumerate(shos):
    eligible=[y for y in materials if y['offset']<x['offset'] and y['form'] in liquids]
    if m=='E':a=first['sho']
    elif m=='R' or i==0:a=eligible[-1] if eligible else None;anchor=a
    else:a=anchor
    oid=first[a['form']]['id'] if a else '';mapping[x['id']]=oid;selected[x['id']]=a
    between=[y for y in flat if a and a['offset']<y['offset']<x['offset']]
    targets.append(dict(edition=ed,paragraph=p['id'],model=m,target=x['id'],antecedent=a['id'] if a and m!='E' else '',antecedent_form=a['form'] if a and m!='E' else '',object=oid,object_form=byid[oid]['form'] if oid else '',status='SEPARATE_SAME' if m=='E' else 'BOUND_ASSUMED' if oid else 'MISSING_ANTECEDENT',prior_specific_count=len(eligible),unread_between=';'.join(y['id'] for y in between if y['role']=='OPEN'),other_materials_between=';'.join(y['id'] for y in between if y['role'] in mat)))
   objects[(ed,p['id'],m)]=mapping
   for x in materials:objectrows.append(dict(edition=ed,paragraph=p['id'],model=m,mention=x['id'],form=x['form'],object=mapping[x['id']],object_form=byid[mapping[x['id']]]['form'] if mapping[x['id']] else ''))
table('TARGETS.tsv',targets);table('PRIOR_MATERIALS.tsv',priorrows);table('OBJECTS.tsv',objectrows);table('CONTEXTS.tsv',context)
consequences=[];takeout=[];qout=[];summary=[]
def identity(ed,p,m,mention):
 oid=objects[(ed,p,m)].get(mention,'');flat=flats[(ed,p)]
 return oid,next((x['form'] for x in flat if x['id']==oid),'')
for r in args:
 ed,p,g=r['edition'],r['paragraph'],r['variant']
 for m in S['models']:
  oid,form=identity(ed,p,m,r['patient']);sid,sform=identity(ed,p,m,r['coingredient']);eid,_=identity(ed,p,'E',r['patient']);esid,_=identity(ed,p,'E',r['coingredient'])
  type_status='NOT_TYPED' if r['form']!='qokeor' else 'EXTRACT_BOUND' if oid and form in extracts else 'EXTRACT_NOT_BOUND'
  if m=='E' and r['form']=='qokeor':assert (type_status=='EXTRACT_NOT_BOUND')==('EXTRACT_PATIENT_NOT_BOUND' in r['debts'])
  other=[d for d in r['debts'].split(';') if d and d!='EXTRACT_PATIENT_NOT_BOUND']
  if r['patient'] and not oid:other.append('UNRESOLVED_SHO_REFERENCE')
  if r['coingredient'] and not sid:other.append('UNRESOLVED_SECOND_SHO_REFERENCE')
  consequences.append(dict(edition=ed,paragraph=p,grammar=g,model=m,operation=r['operation'],form=r['form'],meaning=r['meaning'],patient=r['patient'],patient_form=r['patient_form'],second=r['coingredient'],object=oid,object_form=form,second_object=sid,reference_changed=oid!=eid or sid!=esid,old_debts=r['debts'],remaining_non_type_debts=';'.join(other),type_status=type_status,binary_self_relation=bool(oid and oid==sid),missing_reference=bool((r['patient'] and not oid) or (r['coingredient'] and not sid))))
for r in takes:
 for m in S['models']:
  oid,form=identity(r['edition'],r['paragraph'],m,r['patient']);takeout.append(dict(edition=r['edition'],paragraph=r['paragraph'],grammar=r['grammar'],model=m,target=r['target'],patient=r['patient'],object=oid,object_form=form,old_debts=r['debts'],missing_reference=bool(r['patient'] and not oid)))
for r in qualities:
 for m in S['models']:
  oid,form=identity('ZL3b',r['paragraph'],m,r['patient']);qout.append(dict(paragraph=r['paragraph'],grammar=r['grammar'],model=m,mention=r['mention'],form=r['form'],axis=r['axis'],value=r['value'],patient=r['patient'],object=oid,object_form=form,input_eligible=r['input_eligible'],old_debts=r['debts'],state_status='NOT_SIMULATED'))
for ed in alt:
 for m in S['models']:
  tt=[r for r in targets if r['edition']==ed and r['model']==m]
  for g in S['variants']:
   aa=[r for r in consequences if (r['edition'],r['model'],r['grammar'])==(ed,m,g)]
   summary.append(dict(edition=ed,model=m,grammar=g,sho_mentions=len(tt),bound_sho=sum(bool(r['object']) for r in tt),missing_sho=sum(not r['object'] for r in tt),typed_commands=sum(r['form']=='qokeor' for r in aa),typed_bound=sum(r['type_status']=='EXTRACT_BOUND' for r in aa),binary_self_relations=sum(r['binary_self_relation'] for r in aa),actions_with_missing_reference=sum(r['missing_reference'] for r in aa),actions_with_changed_reference=sum(r['reference_changed'] for r in aa)))
table('ACTION_CONSEQUENCES.tsv',consequences);table('TAKE_CONSEQUENCES.tsv',takeout);table('QUALITY_REFERENTS.tsv',qout);table('MODEL_SUMMARY.tsv',summary)
full=rows(W/'W16/ALIGNMENT.tsv');out=[];reader=['# W17 – drei Referenzfassungen der vollständigen Arbeitslesung','','Wortwerte aus W16 unverändert hypothetisch. E: getrennte Flüssigkeit; P: erster Flüssigkeitsanker bleibt; R: jede sho-Nennung sucht erneut den letzten spezifischen Flüssigkeitsanker. Die Anmerkungen geben Stoffidentitäten nur unter diesen Annahmen an. Keine Produktion, keine neue Zustandsrechnung.']
for r in full:
 loc=r['locus']+':'+r['index'];annotations=[]
 for m in S['models']:
  match=next((t for t in targets if t['edition']=='ZL3b' and t['model']==m and t['target']==loc),None)
  if match:annotations.append(m+': '+(match['object_form']+'@'+match['object'] if match['object'] else 'kein interner Antezedent'))
 out.append(dict(r,reference_alternatives=' / '.join(annotations)))
for p in dict.fromkeys(r['paragraph'] for r in out):
 reader+=['','## '+p]
 for loc in dict.fromkeys(r['locus'] for r in out if r['paragraph']==p):
  rr=[r for r in out if r['locus']==loc];reader+=['',loc+': `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['joint']+(' {'+r['reference_alternatives']+'}' if r['reference_alternatives'] else '')+(' {Eingangsattribut J/M}' if r['input_attribute_grammars'] else '')+(' {erneut: Vorbedingung offen}' if r['repeat_obligation']!='UNCHANGED' else '') for r in rr)]
table('ALIGNMENT.tsv',out);(E/'READING.md').write_text('\n'.join(reader)+'\n')
result={'primary_groups':len(full),'primary_sho_mentions':sum(r['edition']=='ZL3b' and r['model']=='E' for r in targets),'target_rows':len(targets),'object_rows':len(objectrows),'action_rows':len(consequences),'take_rows':len(takeout),'quality_rows':len(qout),'model_summary':summary,'confirmed_meanings':0,'independent_confirmation_capacity':0,'new_word_values':0,'held_access':False,'state_simulation':False}
save('RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='model_summary'}));print(json.dumps([r for r in summary if r['edition']=='ZL3b']))
