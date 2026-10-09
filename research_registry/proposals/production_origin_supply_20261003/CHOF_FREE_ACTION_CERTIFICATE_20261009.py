"""Replay a bounded algebraic certificate; no new source census or closure search."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2]
inputs=['experiments/yolo/gdt1287_whole_word_reversible_closure/artifacts/PROOFS.json',str((B/'CHOF_ENDPOINT_DEPENDENCY_20261009.json').relative_to(R))]
p=json.loads((R/inputs[0]).read_text()); replacement=json.loads((R/inputs[1]).read_text())
out={'status':'CHOF_NOT_NECESSARY_FOR_ACTION_EXCLUSION','inputs':[{'path':f,'sha256':hashlib.sha256((R/f).read_bytes()).hexdigest()} for f in inputs],'readers':{},'limits':['Same reversible common-start/common-natural-end action contract as1287.','cheef remains one unverified physical source site; other rare seed assumptions remain.','Composed chee is an algebraic word, not an attested written whole.','No image result, meaning, new census or new construction selected.']}
for ed,d in p.items():
 assert d['square']['ol'] and d['square']['olol']
 good={};bad=[];sources={}
 for side,ns in d['chains'].items():
  for n in ns:
   key=(side,n['old_id']);w=tuple(n['word'])
   if n['parents'] is None:
    if ''.join(w)=='chof':bad.append([side,n['old_id']]);continue
    assert n['source_ids'];good[key]=w;sources[key]=set(n['source_ids'])
   else:
    keys=[(side,i) for i in n['parents']]
    if not all(k in good for k in keys):continue
    a,b=[good[k] for k in keys]
    assert b==(a+w if side=='LEFT' else w+a)
    good[key]=w;sources[key]=set.union(*(sources[k] for k in keys))
 targets={u:tuple(k) for u,k in d['targets'].items()};remaining=[u for u,k in targets.items() if k not in good]
 assert remaining==(['f'] if ed!='IT2a' else [])
 assert good[targets['ch']]==('ch',) and good[targets['e']]==('e',)
 src=replacement['readers'][ed]['cheef_sources'];assert len(src)==1 and src[0]['units']==['ch','e','e','f']
 dependencies=sorted(sources[targets['ch']]|sources[targets['e']]|{src[0]['id']})
 out['readers'][ed]={'unaffected_targets':[u for u,k in targets.items() if k in good],'removed_chof_nodes':bad,'replacement_f_proof':{'fixed_actions':['ch','e'],'composed_action':['ch','e','e'],'whole_source':src[0],'source_dependencies':dependencies,'inference':'s.ch=s and s.e=s imply s.chee=s; s.cheef=s then implies s.f=s.'},'all_targets_after_replacement':sorted(targets),'original_it_f_already_independent':ed=='IT2a'}
assert len({tuple(v['all_targets_after_replacement']) for v in out['readers'].values()})==1
(B/'CHOF_FREE_ACTION_CERTIFICATE_20261009.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({ed:{'unaffected':len(v['unaffected_targets']),'all':len(v['all_targets_after_replacement'])} for ed,v in out['readers'].items()}))
