"""Whole okor role rivals with frozen W16 grammar; no new decoder."""
import ast,collections,copy,csv,hashlib,json
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
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];rules=read(W/'W05/SPEC.json')
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
for word,o in rules['word_overrides'].items():D[word]={**D[word],**o}
D['sheeody']={'role':'MATERIAL','hypothesis':'Pulver [Materialhypothese]'};D['qokeeo']={'role':'ACTION','hypothesis':'rühre [Hypothese]'}
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
for old,name in [('W05','base_arguments'),('W11','solve'),('W13','requal'),('W16','take')]:
 fn=next(n for n in ast.parse((W/old/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)
 exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_'+old+'_'+name,'exec'))
oldargs={(r['edition'],r['variant'],r['operation']):r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'}
oldtakes={(r['edition'],r['grammar'],r['target']):r for r in rows(W/'W16/TAKE_ARGUMENTS.tsv') if r['model']=='PR'}
oldquality={(r['grammar'],r['mention']):r for r in rows(W/'W16/QUALITY_BINDINGS.tsv') if r['model']=='PR'}
oldq=rows(W/'W05/QUALITY_ASSERTIONS.tsv');cols=['patient','patient_form','coingredient','rule','debts','shared_run','additional_grammar_assumption']
arguments=[];changes=[];targets=[];futures=[];parents=[];amounts=[];takes=[];qualities=[];flats=[];contexts=[]
meanings={'U':'[ungelesen: okor]','A':'teile ab','N':'abgeteilter Anteil'}
for ed,ll in alt.items():
 mapped={l['metadata']['locus']:l for l in ll}
 for target in source['targets']:
  p=target['hosts']['ZL3b'][0];raw=[]
  for line in p['lines']:
   assert not line['locus'].startswith('f84');ww=[z['ivtff_group_raw'] for z in mapped[line['locus']]['groups']]
   if ed=='ZL3b':assert ww==line['words']
   for i,word in enumerate(ww,1):raw.append(dict(id=line['locus']+':'+str(i),locus=line['locus'],index=i,form=word,role=('OPEN' if word=='okor' else D.get(word,{}).get('role','OPEN')),offset=len(raw)))
  for x in raw:flats.append(dict(edition=ed,paragraph=p['id'],**x))
  for model,role in S['models'].items():
   flat=copy.deepcopy(raw);D['okor']={'role':role,'hypothesis':meanings[model]};glosses['okor']=meanings[model]
   for x in flat:
    if x['form']=='okor':x['role']=role
   byid={x['id']:x for x in flat};versions=solve(flat)
   for g,aa in versions.items():
    amap={a['operation']:a for a in aa}
    for a in aa:
     arguments.append(dict(edition=ed,model=model,variant=g,paragraph=p['id'],**a));o=oldargs.get((ed,g,a['operation']))
     if model=='U':assert o and all(a[k]==o[k] for k in cols)
     if o:
      changed=[k for k in cols if a[k]!=o[k]]
      if changed:changes.append(dict(edition=ed,model=model,grammar=g,paragraph=p['id'],operation=a['operation'],form=a['form'],fields=','.join(changed),old_patient=o['patient'],new_patient=a['patient'],old_second=o['coingredient'],new_second=a['coingredient'],old_debts=o['debts'],new_debts=a['debts']))
    for x in [x for x in flat if x['form']=='ychor']:
     n=take(flat,x,aa,g);o=oldtakes[ed,g,x['id']];changed=[k for k in n if n[k]!=o[k]]
     if model=='U':assert not changed
     takes.append(dict(edition=ed,model=model,grammar=g,paragraph=p['id'],target=x['id'],**n,changed_fields=','.join(changed)))
    if ed=='ZL3b':
     for q in oldq:
      if q['variant']!=g or q['paragraph']!=p['id'] or q['kind']!='STANDALONE':continue
      qr=requal(q,flat,aa);x=byid[q['mention']];m=byid.get(qr['patient']);prior=[a for a in aa if m and a['patient']==m['id'] and byid[a['operation']]['locus']==m['locus'] and byid[a['operation']]['offset']<m['offset']]
      eligible=bool(m and m['locus']==x['locus'] and m['offset']==x['offset']-1 and m['role'] in MAT and prior)
      o=oldquality[g,q['mention']];changed=[k for k in ['patient','patient_form','rule','debts'] if qr[k]!=o[k]]
      if str(eligible)!=o['input_eligible']:changed.append('input_eligible')
      if model=='U':assert not changed
      qualities.append(dict(model=model,grammar=g,paragraph=p['id'],mention=q['mention'],form=q['form'],patient=qr['patient'],patient_form=qr['patient_form'],rule=qr['rule'],debts=qr['debts'],input_eligible=eligible,changed_fields=','.join(changed)))
    for x in [x for x in flat if x['form']=='okor']:
     a=amap.get(x['id']);patient=a['patient'] if a else '';uses=[a for a in aa if x['id'] in [a['patient'],a['coingredient']]]
     targets.append(dict(edition=ed,model=model,grammar=g,paragraph=p['id'],target=x['id'],meaning=meanings[model],patient=patient,patient_form=a['patient_form'] if a else '',debts=a['debts'] if a else '',nominal_uses=';'.join(a['operation'] for a in uses),partition_source=patient if model=='A' else '',partition_output='',quantity_binding='',semantic_obligation='OUTPUT_AND_QUANTITY_UNBOUND' if model=='A' else 'SOURCE_AND_QUANTITY_UNBOUND' if model=='N' else 'UNREAD',raw_line=' '.join(y['form'] for y in flat if y['locus']==x['locus'])))
     for a in aa:
      if byid[a['operation']]['offset']>x['offset']:futures.append(dict(edition=ed,model=model,grammar=g,paragraph=p['id'],target=x['id'],later_action=a['operation'],form=a['form'],patient=a['patient'],patient_form=a['patient_form'],same_source=bool(patient and a['patient']==patient),target_patient=a['patient']==x['id'],debts=a['debts']))
   for x in [x for x in flat if x['form']=='okor']:
    for y in flat:
     if y['offset']<x['offset'] and y['role'] in MAT:parents.append(dict(edition=ed,model=model,paragraph=p['id'],target=x['id'],earlier_material=y['id'],form=y['form'],role=y['role'],status='CANDIDATE_ONLY_NOT_BOUND_AS_ORIGIN'))
     if y['locus']==x['locus'] and y['role'] in {'AMOUNT','NUMBER','MATERIAL_DOSE','DISTRIBUTIVE'}:amounts.append(dict(edition=ed,model=model,paragraph=p['id'],target=x['id'],mention=y['id'],form=y['form'],role=y['role'],status='COOCCURRENCE_NOT_QUANTITY_BINDING'))
   if any(x['form']=='okor' for x in flat):
    for line in p['lines']:contexts.append(dict(edition=ed,model=model,paragraph=p['id'],locus=line['locus'],raw=' '.join(x['form'] for x in flat if x['locus']==line['locus'])))
for name,rr in [('ARGUMENTS',arguments),('CHANGES',changes),('TARGETS',targets),('FUTURES',futures),('PARENT_CANDIDATES',parents),('AMOUNT_CONTEXTS',amounts),('TAKE_ARGUMENTS',takes),('QUALITY_BINDINGS',qualities),('SOURCE_FLAT',flats),('CONTEXTS',contexts)]:table(name+'.tsv',rr)
alignment=[dict(r,U=r['joint'],A='teile ab' if r['raw']=='okor' else r['joint'],N='abgeteilter Anteil' if r['raw']=='okor' else r['joint']) for r in rows(W/'W16/ALIGNMENT.tsv')];table('ALIGNMENT.tsv',alignment)
reader=['# W23 vollständige hypothetische Lesung','W16-Basis unverändert; okor als A/N/U offen. Keine neuen Ausgangs-/Ergebnisidentitäten ergänzt. W17–W22 Alternativen bleiben in ihren eigenen Berichten erhalten.']
for p in dict.fromkeys(r['paragraph'] for r in alignment):
 reader.append('\n## '+p)
 for loc in dict.fromkeys(r['locus'] for r in alignment if r['paragraph']==p):
  rr=[r for r in alignment if r['paragraph']==p and r['locus']==loc];reader.append('\n'+loc+'\n\n'+' · '.join(r['raw']+' ['+('{A: teile ab / N: abgeteilter Anteil / U: ungelesen}' if r['raw']=='okor' else r['joint'])+']' for r in rr))
(E/'READING.md').write_text('\n'.join(reader)+'\n')
result=dict(primary_groups=len(alignment),targets_by_reading={ed:sum(r['edition']==ed and r['model']=='U' and r['grammar']=='B' for r in targets) for ed in alt},target_rows=len(targets),argument_rows=len(arguments),old_argument_change_rows=len(changes),old_patient_changes=sum(r['old_patient']!=r['new_patient'] for r in changes),take_changes=sum(bool(r['changed_fields']) for r in takes),quality_changes=sum(bool(r['changed_fields']) for r in qualities),baseline_parity=True,primary_hypothesized=sum(r['joint_status']!='UNREAD' or r['raw']=='okor' for r in alignment),primary_unread=sum(r['joint_status']=='UNREAD' and r['raw']!='okor' for r in alignment),confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
