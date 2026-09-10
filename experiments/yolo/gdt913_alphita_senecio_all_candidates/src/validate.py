#!/usr/bin/env python3
"""Independent metadata and explicitly released phase replay; never opens legacy cache."""
import argparse,collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
OLD=ROOT/'experiments/yolo/gdt888_alphita_joint_name_incidence'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['prediction','selection','confirmation'],default='prediction');args=ap.parse_args()
 p=read(E/'artifacts/PREDICTIONS.json');fit=read(OLD/'artifacts/FIT_INPUT.json');result=read(OLD/'artifacts/RESULT.json')['panels']['IT2a'];source=read(OLD/'src/SOURCE.json');roles=source['node_order']
 for path,digest in p['legacy_bindings'].items():assert sha(ROOT/path)==digest
 assert p['cache_sha256']==fit['source_sha256'] and p['cache_path']==fit['source']
 tokens=re.findall('[a-z]+',source['entries']['S']['body'].lower());names={n:re.findall('[a-z]+',v.lower()) for n,v in source['headwords'].items()};counts=dict.fromkeys(roles,0);i=0
 while i<len(tokens):
  found=[n for n,w in names.items() if tokens[i:i+len(w)]==w]
  if found:
   n=max(found,key=lambda n:len(names[n]));counts[n]+=1;i+=len(names[n])
  else:i+=1
 assert counts==dict(B=1,D=1,C=0,L=0,M=0,S=0)==p['expected_counts']
 heads=fit['panels']['IT2a']['held_heads'];train={r['paragraph_id']:r for r in fit['panels']['IT2a']['train']};lex=result['lexicons'];assert len(heads)==239 and len(lex)==len(p['candidates'])==18
 matches=[[h for h in heads if h['head']==l['head_forms']['S']] for l in lex]
 selection={min((h['physical_folio'] for h in m),key=lambda f:int(f[1:])) for m in matches};union={h['physical_folio'] for m in matches for h in m}
 assert selection=={'f80','f104','f112'} and union-selection=={'f108','f116'}
 assert set(p['selection_leaves'])==selection and set(p['confirmation_leaves'])==union-selection
 full=collections.defaultdict(list);positive=collections.defaultdict(list)
 for j,(l,c,m) in enumerate(zip(lex,p['candidates'],matches)):
  assert c['candidate']==f'K{j+1:02}' and c['saved_lexicon_index']==j and c['lexicon']==l
  assert c['lexicon_sha256']==hashlib.sha256(canonical(l).encode()).hexdigest() and c['expected_counts']==counts
  expected=[dict(h,phase='selection' if h['physical_folio'] in selection else 'confirmation') for h in m]
  assert sorted(c['paragraphs'],key=canonical)==sorted(expected,key=canonical)
  assignments=[]
  for k,s in enumerate(result['solutions']):
   if s['head_forms']==l['head_forms'] and s['mention_forms']==l['mention_forms']:
    assignments.append(dict(saved_solution_index=k,paragraphs=s['paragraphs'],physical_leaves={n:train[pid]['physical_folio'] for n,pid in s['paragraphs'].items()}))
  assert c['training_assignments']==assignments
  ids=tuple(sorted(h['paragraph_id'] for h in m));forms=l['mention_forms']
  full[(ids,tuple(sorted((tuple(forms[n]),counts[n]) for n in roles)))].append(c['candidate'])
  positive[(ids,tuple(sorted((tuple(forms[n]),1) for n in ['B','D'])))].append(c['candidate'])
 for groups,key,prefix in [(full,'exact_predicate_classes','F'),(positive,'positive_only_classes','P')]:
  expected=[dict(class_=f'{prefix}{i+1:02}',members=g) for i,g in enumerate(groups.values())]
  assert [(x['class'],x['members']) for x in p[key]]==[(x['class_'],x['members']) for x in expected]
  field='full_predicate_class' if prefix=='F' else 'positive_only_class'
  for x in p[key]:
   for c in p['candidates']:
    if c['candidate'] in x['members']:assert c[field]==x['class']
 phases=[] if args.phase=='prediction' else ['selection'] if args.phase=='selection' else ['selection','confirmation'];survivors=[];phase_receipts={}
 for phase in phases:
  ip=E/'artifacts'/f'{phase.upper()}_INPUT.json';op=E/'artifacts'/f'{phase.upper()}.json';inp=read(ip);out=read(op)
  assert inp['phase']==out['phase']==phase and inp['cache_sha256']==p['cache_sha256']
  assert out['predictions_sha256']==sha(E/'artifacts/PREDICTIONS.json') and out['input_sha256']==sha(ip)
  allowed={h['paragraph_id']:h for c in p['candidates'] for h in c['paragraphs'] if h['phase']==phase};frames={f['paragraph_id']:f for f in inp['paragraphs']}
  assert len(frames)==len(inp['paragraphs']) and frames.keys()==allowed.keys()
  for pid,f in frames.items():
   h=allowed[pid];assert all(f[k]==h[k] for k in ['page','physical_folio','head']);assert f['groups'][0]['sta']==h['head'];assert not f['page'].startswith('f84')
  assert len(out['candidates'])==18
  for c,o in zip(p['candidates'],out['candidates']):
   obs=[]
   for h in c['paragraphs']:
    if h['phase']!=phase:continue
    f=frames[h['paragraph_id']];actual=dict.fromkeys(roles,0);hits=[]
    for ordinal,g in enumerate(f['groups'][1:],1):
     for n in roles:
      if g['sta']==c['lexicon']['mention_forms'][n]:
       actual[n]+=1;hits.append(dict(role=n,body_ordinal_one_based=ordinal,**{k:g[k] for k in ['source_group_id','locus','raw','sta']}))
    contradictions=[dict(role=n,expected=counts[n],observed=actual[n],delta=actual[n]-counts[n]) for n in roles if actual[n]!=counts[n]]
    obs.append(dict(paragraph_id=h['paragraph_id'],page=h['page'],physical_folio=h['physical_folio'],observed_counts=actual,expected_counts=counts,passed=not contradictions,contradictions=contradictions,matched_groups=hits))
   status='NO_CAPACITY' if not obs else 'ALL_PASS' if all(x['passed'] for x in obs) else 'CONTRADICTED'
   assert o==dict(candidate=c['candidate'],status=status,observations=obs,independent_leaves=sorted({x['physical_folio'] for x in obs},key=lambda f:int(f[1:])))
  if phase=='selection':
   survivors=[o['candidate'] for o in out['candidates'] if o['status']=='ALL_PASS'];assert out['survivors']==survivors
  else:
   yes=[o['candidate'] for o in out['candidates'] if o['status']=='ALL_PASS' and o['candidate'] in survivors];none=[o['candidate'] for o in out['candidates'] if o['status']=='NO_CAPACITY' and o['candidate'] in survivors]
   assert out['selection_survivors_frozen']==survivors and out['additionally_confirmed']==yes and out['selection_only_no_confirmation']==none and out['full_contract_survivors']==yes+none
  phase_receipts[phase]={'input_sha256':sha(ip),'result_sha256':sha(op),'paragraphs':len(frames)}
 print(json.dumps(dict(status='PASS',phase=args.phase,candidates=18,full_classes=len(full),positive_classes=len(positive),predictions_sha256=sha(E/'artifacts/PREDICTIONS.json'),validator_sha256=sha(Path(__file__)),phases=phase_receipts),indent=2))
if __name__=='__main__':main()
