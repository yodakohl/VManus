"""Separate complete census and frozen-contract replay, not independent semantics."""
import ast,copy,csv,hashlib,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;W=E.parent;ROOT=next(p for p in E.parents if (p/'vmanus-work').exists())
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def read(p):return json.loads(p.read_text())
S=read(E/'SPEC.json')
assert hashlib.sha256((E/'DECISION.md').read_bytes()).hexdigest()==S['decision_sha256']
for f in S['inputs']:assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
# Reconstruct all words directly from the safe packet, not from builder output.
source=read(W/'W02/SOURCE.json');alt=read(W/'W02/ALTERNATE_LINES.json')['readings'];rules=read(W/'W05/SPEC.json')
D={r['form']:r for r in rows(W/'W02/LEXICON.tsv')}
for k,v in rules['word_overrides'].items():D[k].update(v)
D.update(sheeody={'role':'MATERIAL','hypothesis':'Pulver'},qokeeo={'role':'ACTION','hypothesis':'rühre'})
ACT=set(rules['action_roles']);MAT=set(rules['material_roles']);MOD=set(rules['transparent_roles']);extracts={'cheor','okeeor','okeor','keeor','cheeor','sheeor'}
glosses={r['raw']:r['joint'] for r in rows(W/'W16/ALIGNMENT.tsv')}
for folder,name in [('W05','base_arguments'),('W11','solve'),('W16','take'),('W13','requal')]:
 fn=next(n for n in ast.parse((W/folder/'build.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name);exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen_contract','exec'))
args=rows(E/'ARGUMENTS.tsv');ix={(r['edition'],r['paragraph'],r['model'],r['variant'],r['operation']):r for r in args};assert len(ix)==len(args)
targets=rows(E/'TARGETS.tsv');futures=rows(E/'FUTURES.tsv');parents=rows(E/'PARENT_CANDIDATES.tsv');amounts=rows(E/'AMOUNT_CONTEXTS.tsv');flatrows=rows(E/'SOURCE_FLAT.tsv');takes=rows(E/'TAKE_ARGUMENTS.tsv');qualities=rows(E/'QUALITY_BINDINGS.tsv')
oldtakes={(r['edition'],r['grammar'],r['target']):r for r in rows(W/'W16/TAKE_ARGUMENTS.tsv') if r['model']=='PR'}
oldq=rows(W/'W05/QUALITY_ASSERTIONS.tsv');expected_target=set();expected_future=set();expected_parents=set();expected_amount=set();checked=0
for ed,ll in alt.items():
 lines={x['metadata']['locus']:[g['ivtff_group_raw'] for g in x['groups']] for x in ll}
 for t in source['targets']:
  p=t['hosts']['ZL3b'][0];flat=[]
  for l in p['lines']:
   assert not l['locus'].startswith('f84')
   if ed=='ZL3b':assert lines[l['locus']]==l['words']
   for i,w in enumerate(lines[l['locus']],1):flat.append(dict(id=l['locus']+':'+str(i),locus=l['locus'],index=i,form=w,role='OPEN' if w=='okor' else D.get(w,{}).get('role','OPEN'),offset=len(flat)))
  actual=[r for r in flatrows if r['edition']==ed and r['paragraph']==p['id']];assert len(actual)==len(flat)
  for a,b in zip(actual,flat):assert all(a[k]==str(v) for k,v in b.items())
  for model,role in S['models'].items():
   D['okor']={'role':role,'hypothesis':{'U':'[ungelesen: okor]','A':'teile ab','N':'abgeteilter Anteil'}[model]};glosses['okor']=D['okor']['hypothesis'];ff=copy.deepcopy(flat)
   for x in ff:
    if x['form']=='okor':x['role']=role
   byid={x['id']:x for x in ff}
   for g,aa in solve(ff).items():
    for a in aa:
     r=ix[ed,p['id'],model,g,a['operation']];assert all(r[k]==v for k,v in a.items());checked+=1
    for x in ff:
     if x['form']=='ychor':
      n=take(ff,x,aa,g);tr=next(r for r in takes if (r['edition'],r['model'],r['grammar'],r['target'])==(ed,model,g,x['id']));assert all(tr[k]==str(v) for k,v in n.items())
     if x['form']!='okor':continue
     key=(ed,model,g,x['id']);expected_target.add(key);tr=next(r for r in targets if (r['edition'],r['model'],r['grammar'],r['target'])==key)
     a=next((r for r in aa if r['operation']==x['id']),None);assert tr['patient']==(a['patient'] if a else '')
     assert tr['nominal_uses']==';'.join(a['operation'] for a in aa if x['id'] in [a['patient'],a['coingredient']])
     assert not tr['partition_output'] and not tr['quantity_binding']
     for a in aa:
      if byid[a['operation']]['offset']>x['offset']:expected_future.add((*key,a['operation'],a['patient']))
    if ed=='ZL3b':
     for q in oldq:
      if q['variant']==g and q['paragraph']==p['id'] and q['kind']=='STANDALONE':
       qr=requal(q,ff,aa);r=next(r for r in qualities if (r['model'],r['grammar'],r['mention'])==(model,g,q['mention']));assert all(qr[k]==r[k] for k in ['patient','patient_form','rule','debts'])
   for x in ff:
    if x['form']!='okor':continue
    for y in ff:
     if y['offset']<x['offset'] and y['role'] in MAT:expected_parents.add((ed,model,x['id'],y['id']))
     if y['locus']==x['locus'] and y['role'] in {'AMOUNT','NUMBER','MATERIAL_DOSE','DISTRIBUTIVE'}:expected_amount.add((ed,model,x['id'],y['id']))
assert checked==len(args)==2781
assert expected_target=={(r['edition'],r['model'],r['grammar'],r['target']) for r in targets} and len(targets)==54
assert expected_future=={(r['edition'],r['model'],r['grammar'],r['target'],r['later_action'],r['patient']) for r in futures} and len(expected_future)==len(futures)
assert expected_parents=={(r['edition'],r['model'],r['target'],r['earlier_material']) for r in parents} and len(expected_parents)==len(parents)
assert expected_amount=={(r['edition'],r['model'],r['target'],r['mention']) for r in amounts} and len(expected_amount)==len(amounts)
a=rows(W/'W16/ALIGNMENT.tsv');b=rows(E/'ALIGNMENT.tsv');assert len(a)==len(b)==900
for x,y in zip(a,b):
 assert all(y[k]==v for k,v in x.items())
 for m in ['U','A','N']:assert y[m]==({'A':'teile ab','N':'abgeteilter Anteil'}[m] if x['raw']=='okor' and m!='U' else x['joint'])
result=dict(status='PASS',frozen_files=len(S['inputs']),argument_replay=checked,targets=len(targets),future_rows=len(futures),prior_material_pairs=len(parents),quantity_contexts=len(amounts),raw_groups=900,limits='Independent artifact census using reused frozen binding functions; no independent grammar or meaning validation')
(E/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
