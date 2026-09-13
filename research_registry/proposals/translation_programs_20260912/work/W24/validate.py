"""Independent source/partitive selection audit; does not import build."""
import csv,json,hashlib,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
S=json.loads((E/'SPEC.json').read_text());assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
MAT=set(json.loads((W/'W05/SPEC.json').read_text())['material_roles']);groups=collections.defaultdict(list)
for r in rows(W/'W23/SOURCE_FLAT.tsv'):r['offset']=int(r['offset']);groups[r['edition'],r['paragraph']].append(r)
args=[a for a in rows(W/'W23/ARGUMENTS.tsv') if a['model']=='U'];refs=rows(E/'REFERENCES.tsv');pairs=rows(E/'ALL_SOURCE_PAIRS.tsv');phrases=rows(E/'PARTITIVE_PHRASES.tsv');bridges=rows(E/'AL_TO_OKOR.tsv')
index={(r['edition'],r['paragraph'],r['grammar'],r['model'],r['target']):r for r in refs};assert len(index)==len(refs)
expected_refs=set();expected_pairs=set();expected_phrases=set();expected_bridges=set()
for (ed,p),ff in groups.items():
 byid={x['id']:x for x in ff};byoffset={x['offset']:x for x in ff}
 for x in ff:
  if x['form']!='al':continue
  mm=[m for m in ff if m['role'] in MAT and m['offset']<x['offset']]
  expected_pairs.update((ed,p,x['id'],m['id']) for m in mm)
  prev=byoffset.get(x['offset']-1);amount=prev['id'] if prev and prev['role']=='AMOUNT' and prev['locus']==x['locus'] else ''
  for g in S['grammars']:
   prior=[a for a in args if a['edition']==ed and a['paragraph']==p and a['variant']==g and byid[a['operation']]['offset']<x['offset']]
   a=max(prior,key=lambda a:byid[a['operation']]['offset'],default=None)
   for model in S['models']:
    key=(ed,p,g,model,x['id']);expected_refs.add(key);r=index[key]
    source=max(mm,key=lambda m:m['offset'])['id'] if model=='T' and mm else a['patient'] if model=='V' and a else ''
    assert r['source']==source and r['amount']==amount
    assert r['via_action']==(a['operation'] if a and model=='V' else '')
    assert r['inherited_debts']==(a['debts'] if a and model=='V' else '')
    crossed=[z for z in ff if source and min(byid[source]['offset'],x['offset'])<z['offset']<max(byid[source]['offset'],x['offset'])]
    assert r['unread_between']==';'.join(z['id'] for z in crossed if z['role']=='OPEN')
    assert r['other_materials']==';'.join(z['id'] for z in crossed if z['role'] in MAT)
    assert r['source_after_reference']==str(bool(source and byid[source]['offset']>x['offset']))
    if amount:expected_phrases.add(key)
  for y in ff:
   if y['form']!='okor' or y['offset']<=x['offset']:continue
   key=(ed,p,x['id'],y['id']);expected_bridges.add(key);r=next(r for r in bridges if (r['edition'],r['paragraph'],r['al'],r['okor'])==key)
   zz=[z for z in ff if x['offset']<z['offset']<y['offset']];assert int(r['groups_between'])==len(zz)
   assert r['raw_between']==' '.join(z['form'] for z in zz)
   assert r['unread_between']==';'.join(z['id'] for z in zz if z['role']=='OPEN')
   assert r['materials_between']==';'.join(z['id'] for z in zz if z['role'] in MAT)
   assert r['actions_between']==';'.join(a['operation'] for a in args if a['edition']==ed and a['paragraph']==p and a['variant']=='B' and x['offset']<byid[a['operation']]['offset']<y['offset'])
assert expected_refs==set(index)
assert expected_pairs=={(r['edition'],r['paragraph'],r['target'],r['material']) for r in pairs} and len(expected_pairs)==len(pairs)
assert expected_phrases=={(r['edition'],r['paragraph'],r['grammar'],r['model'],r['target']) for r in phrases} and len(expected_phrases)==len(phrases)
for r in phrases:
 source=index[r['edition'],r['paragraph'],r['grammar'],r['model'],r['target']];assert all(r[k]==v for k,v in source.items());assert r['numerical_quantity']=='' and r['actual_partition_event']=='NOT_ESTABLISHED'
assert len(expected_bridges)==len(bridges)
a=rows(W/'W23/ALIGNMENT.tsv');b=rows(E/'ALIGNMENT.tsv');assert len(a)==len(b)==900
for x,y in zip(a,b):assert all(y[k]==v for k,v in x.items())
result=dict(status='PASS',frozen_files=len(S['inputs']),reference_cases=len(refs),all_source_pairs=len(pairs),partitive_cases=len(phrases),all_al_okor_bridges=len(bridges),raw_groups=900,limits='Independent new reference selection/census; inherited role meanings and action arguments not independently validated')
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
