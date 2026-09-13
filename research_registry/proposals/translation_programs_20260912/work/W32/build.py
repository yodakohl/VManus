"""Fixed adjunct attachment census; existing action histories are never mutated."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;B=W/'W28';ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
S=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for x in S['inputs']:assert hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()==x['sha256']
census=[];cases=[];later=[]
for sm in ['Q','A']:
 ff=rows(B/(sm+'_SOURCE_FLAT.tsv'));events=rows(B/(sm+'_EVENTS.tsv'));actionids={r['location'] for r in events if r['kind']=='ACTION'}
 for p in read(B/'SOURCE.json')['paragraphs']:
  flat=[r for r in ff if r['paragraph']==p['id']];byid={r['id']:r for r in flat};pos={r['id']:i for i,r in enumerate(flat)}
  for i,x in enumerate(flat):
   if x['form'] not in S['markers']:continue
   companion=None;stop='PARAGRAPH_END';gap=[]
   for y in flat[i+1:]:
    if y['id'] in actionids or y['form'] in S['markers']:stop=y['id'];break
    if y['role'] in ['MATERIAL','MATERIAL_DOSE']:companion=y;stop='COMPANION';break
    gap.append(y)
   for direction in ['P','F']:
    candidates=[r for r in flat if r['id'] in actionids and (pos[r['id']]<i if direction=='P' else pos[r['id']]>(pos[companion['id']] if companion else i))];gov=(candidates[-1] if direction=='P' else candidates[0]) if candidates else None
    span=flat[min(i,pos[gov['id']])+1:max(i,pos[gov['id']])] if gov else []
    meta=dict(shol=sm,paragraph=p['id'],marker=x['id'],form=x['form'],direction=direction)
    census.append(dict(**meta,companion=companion['id'] if companion else '',companion_form=companion['form'] if companion else '',stop=stop,companion_open=';'.join(r['id']+'='+r['form'] for r in gap if r['role']=='OPEN'),governor=gov['id'] if gov else '',governor_form=gov['form'] if gov else '',governor_open=';'.join(r['id']+'='+r['form'] for r in span if r['role']=='OPEN')))
    for g in ['B','J','M']:
     for model in ['D','H']:
      for timing in ['O','I']:
       rr=[r for r in events if (r['paragraph'],r['grammar'],r['model'],r['timing'])==(p['id'],g,model,timing)];a=next((r for r in rr if gov and r['kind']=='ACTION' and r['location']==gov['id']),None);c=next((r for r in rr if companion and r['kind']=='MATERIAL' and r['location']==companion['id']),None)
       debt=[]
       if not c:debt.append('MISSING_COMPANION')
       if not a:debt.append('MISSING_GOVERNOR')
       elif not a['object']:debt.append('MISSING_PATIENT')
       if a and c and a['object']==c['object']:debt.append('SAME_OBJECT_ACCOMPANIMENT')
       if a and c and a['second_object'] and a['second_object']!=c['object']:debt.append('DIFFERENT_EXISTING_SECOND_OBJECT')
       if a and a['status']=='ARGUMENT_INCOMPLETE':debt.append('EXISTING_ACTION_INCOMPLETE')
       full=bool(a and c and a['object'] and a['object']!=c['object']);info=dict(**meta,grammar=g,model=model,timing=timing,companion=companion['id'] if companion else '',companion_object=c['object'] if c else '',governor=gov['id'] if gov else '',governor_form=gov['form'] if gov else '',patient=a['patient'] if a else '',patient_object=a['object'] if a else '',existing_second=a['second_object'] if a else '',existing_status=a['status'] if a else '',existing_debts=a['debts'] if a else '',attachment_issues=';'.join(debt),distinct_bound_pair=full)
       cases.append(info)
       if full:
        # An adjunct is available only after both its written companion and governor are available.
        after=max(rr.index(a),rr.index(c));objects={a['object'],c['object']}
        for r in rr[after+1:]:
         if r['kind']!='MATERIAL' and (r['object'] in objects or r['second_object'] in objects):later.append(dict(**meta,grammar=g,model=model,timing=timing,governor=gov['id'],companion=companion['id'],location=r['location'],kind=r['kind'],object=r['object'],role='COMPANION' if r['object']==c['object'] else 'PATIENT_OR_SECOND',status=r['status'],assertion=r['assertion'],before=r['before'],after=r['after'],capacity_only='NO_NEW_EFFECT_OR_CONFIRMATION'))
table('SCOPES.tsv',census,list(census[0]));table('CANDIDATES.tsv',cases,list(cases[0]));table('ALL_LATER_REQUIREMENTS.tsv',later,list(later[0]) if later else ['shol','paragraph','marker','form','direction','grammar','model','timing','governor','companion','location','kind','object','role','status','assertion','before','after','capacity_only'])
groups=collections.defaultdict(list)
for r in cases:
 key=tuple(r[k] for k in ['marker','direction','companion','governor','patient','existing_second','attachment_issues'])
 groups[key].append('|'.join(r[k] for k in ['shol','grammar','model','timing']))
group_rows=[dict(group='G'+str(i),**dict(zip(['marker','direction','companion','governor','patient','existing_second','attachment_issues'],key)),case_count=len(members),members=';'.join(members),limits='Same attachments only; D/H meanings are not identical') for i,(key,members) in enumerate(groups.items(),1)]
table('PREDICTION_GROUPS.tsv',group_rows,list(group_rows[0]))
summary=[]
for sm in ['Q','A']:
 for direction in ['P','F']:
  rr=[r for r in cases if r['shol']==sm and r['direction']==direction];summary.append(dict(shol=sm,direction=direction,cases=len(rr),distinct_pairs=sum(r['distinct_bound_pair'] for r in rr),clean_distinct_pairs=sum(r['distinct_bound_pair'] and not r['attachment_issues'] for r in rr),issues=dict(collections.Counter(d for r in rr for d in r['attachment_issues'].split(';') if d))))
result=dict(idea='IDEA000229',source_paragraphs=17,source_groups=1045,marker_positions=len({r['marker'] for r in census}),marker_forms=dict(collections.Counter(r['form'] for r in census if r['shol']=='A' and r['direction']=='P')),scope_rows=len(census),attachment_groups=len(groups),candidate_cases=len(cases),summary=summary,later_requirement_rows=len(later),changed_existing_events=0,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
