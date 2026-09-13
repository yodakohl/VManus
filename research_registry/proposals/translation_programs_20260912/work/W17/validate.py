"""Separate exhaustive reconstruction of references and consequence projections."""
import csv,hashlib,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def read(p):return json.loads(p.read_text())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
s=read(E/'SPEC.json');assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
for r in s['inputs']:assert hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256']
lex={r['form']:r['role'] for r in rows(W/'W02/LEXICON.tsv')};lex['sheeody']='MATERIAL';mat={'MATERIAL','MATERIAL_DOSE'}
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];expected={};antecedents={};targetset=set();prior=set();flatmap={};firstmap={}
for ed,ll in alt.items():
 lines={l['metadata']['locus']:[g['ivtff_group_raw'] for g in l['groups']] for l in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for l in p['lines']:
   assert not l['locus'].startswith('f84')
   if ed=='ZL3b':assert lines[l['locus']]==l['words']
   flat.extend((l['locus']+':'+str(i),w) for i,w in enumerate(lines[l['locus']],1))
  flatmap[(ed,p['id'])]=flat;first={}
  for loc,w in flat:
   if lex.get(w) in mat:first.setdefault(w,loc)
  firstmap[(ed,p['id'])]=first;first_sho=next((i for i,(_,w) in enumerate(flat) if w=='sho'),None)
  for i,(loc,w) in enumerate(flat):
   if lex.get(w) not in mat:continue
   for m in s['models']:
    oid=first[w];anchor=''
    if w=='sho':
     targetset.add((ed,p['id'],m,loc))
     if m!='E':
      limit=first_sho if m=='P' else i
      candidates=[(l,v) for l,v in flat[:limit] if v in s['specific_liquids']]
      anchor,aw=candidates[-1] if candidates else ('','');oid=first[aw] if aw else ''
     antecedents[(ed,p['id'],m,loc)]=anchor
    expected[(ed,p['id'],m,loc)]=oid
   if w=='sho':
    prior.update((ed,p['id'],loc,l) for l,v in flat[:i] if lex.get(v) in mat)
obs=rows(E/'OBJECTS.tsv');assert len(obs)==len(expected)
for r in obs:
 key=(r['edition'],r['paragraph'],r['model'],r['mention']);assert r['object']==expected.pop(key)
assert not expected
# Reuse the independently verified object table as an immutable lookup for projections.
obj={(r['edition'],r['paragraph'],r['model'],r['mention']):(r['object'],r['object_form']) for r in obs}
tt=rows(E/'TARGETS.tsv');assert {(r['edition'],r['paragraph'],r['model'],r['target']) for r in tt}==targetset and len(tt)==len(targetset)==45
for r in tt:
 k=(r['edition'],r['paragraph'],r['model'],r['target']);assert r['antecedent']==antecedents[k];assert (r['object'],r['object_form'])==obj[k]
 flat=flatmap[k[:2]];pos={l:i for i,(l,w) in enumerate(flat)};idx=pos[r['target']]
 assert int(r['prior_specific_count'])==sum(w in s['specific_liquids'] for l,w in flat[:idx])
 if r['antecedent']:
  between=flat[pos[r['antecedent']]+1:idx]
  assert r['unread_between']==';'.join(l for l,w in between if w not in lex)
  assert r['other_materials_between']==';'.join(l for l,w in between if lex.get(w) in mat)
pr=rows(E/'PRIOR_MATERIALS.tsv');assert len(pr)==len(prior) and {(r['edition'],r['paragraph'],r['target'],r['prior']) for r in pr}==prior
original=[r for r in rows(W/'W16/ARGUMENTS.tsv') if r['model']=='PR'];okey=lambda r:(r['edition'],r.get('variant',r.get('grammar')),r['paragraph'],r['operation'])
om={okey(r):r for r in original};ac=rows(E/'ACTION_CONSEQUENCES.tsv');assert len(ac)==len(original)*3==2763
seen=set()
for r in ac:
 k=okey(r);b=om[k];seen.add((r['model'],k));prefix=(r['edition'],r['paragraph'],r['model']);oi,of=obj.get(prefix+(b['patient'],),('',''));si,sf=obj.get(prefix+(b['coingredient'],),('',''))
 assert (r['patient'],r['second'],r['object'],r['object_form'],r['second_object'])==(b['patient'],b['coingredient'],oi,of,si)
 typ='NOT_TYPED' if b['form']!='qokeor' else 'EXTRACT_BOUND' if oi and of in s['extract_types'] else 'EXTRACT_NOT_BOUND';assert r['type_status']==typ
 assert (r['binary_self_relation']=='True')==bool(oi and oi==si)
 missing=bool((b['patient'] and not oi) or (b['coingredient'] and not si));assert (r['missing_reference']=='True')==missing
 expecteddebt=[d for d in b['debts'].split(';') if d and d!='EXTRACT_PATIENT_NOT_BOUND']
 if b['patient'] and not oi:expecteddebt.append('UNRESOLVED_SHO_REFERENCE')
 if b['coingredient'] and not si:expecteddebt.append('UNRESOLVED_SECOND_SHO_REFERENCE')
 assert r['remaining_non_type_debts']==';'.join(expecteddebt) and r['old_debts']==b['debts']
assert len(seen)==len(ac)
for name,oldname,idcol,eddefault in [('TAKE_CONSEQUENCES.tsv','TAKE_ARGUMENTS.tsv','target',None),('QUALITY_REFERENTS.tsv','QUALITY_BINDINGS.tsv','mention','ZL3b')]:
 orig=[r for r in rows(W/'W16'/oldname) if r['model']=='PR'];result=rows(E/name);assert len(result)==len(orig)*3
 key=lambda r:(r.get('edition',eddefault),r['paragraph'],r['grammar'],r[idcol]);old={key(r):r for r in orig};seen=set()
 for r in result:
  b=old[key(r)];seen.add((r['model'],key(r)));assert r['patient']==b['patient'];assert (r['object'],r['object_form'])==obj.get((r.get('edition',eddefault),r['paragraph'],r['model'],r['patient']),('',''))
  assert r['old_debts']==b['debts']
 assert len(seen)==len(result)
a=rows(E/'ALIGNMENT.tsv');b=rows(W/'W16/ALIGNMENT.tsv');assert len(a)==len(b)==900
for r,old in zip(a,b):assert all(r[k]==v for k,v in old.items())
reader=(E/'READING.md').read_text()
for t in source['targets']:
 for l in t['hosts']['ZL3b'][0]['lines']:assert reader.count(l['locus']+': `'+' '.join(l['words'])+'`')==1
for m,n in [('E',0),('P',18),('R',9)]:assert sum(r['model']==m and r['type_status']=='EXTRACT_BOUND' for r in ac)==n
assert all(r['binary_self_relation']=='False' for r in ac)
v={'status':'PASS','legacy_files_hash_verified':len(s['inputs']),'targets_checked':45,'material_objects_checked':len(obs),'action_consequences_checked':len(ac),'take_consequences_checked':360,'quality_referents_checked':270,'source_groups':900,'source_lines':152,'scope':'independent complete reference reconstruction and consequence projection, not independent semantic evidence'}
(E/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
