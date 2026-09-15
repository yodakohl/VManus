"""Metadata and literal-capacity preflight; never computes a carrier count."""
from pathlib import Path
import collections,hashlib,json,re,importlib.util
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent
parent=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs'
spec=importlib.util.spec_from_file_location('gdt928_fixed',parent/'src/run.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
panels,dens=mod.load()
allowed={f'f{n}{s}' for n in range(75,84) for s in 'rv'}
out={'question':'At least32 complete literal paragraphs in the fixed18-selector scope?','allowed_selectors':sorted(allowed),'scope_exposure':'Already admitted/exposed; no fresh blindness; no carrier counts','panels':{},'source_hashes':{}}
for ed,rs in panels.items():
 rows=[]
 for p in rs:
  if p['page'] not in allowed:continue
  assert not p['page'].startswith('f84')
  # GDT928 anchor eligibility additionally requires at least2groups perline.
  # Retain that already-frozen conservative rule in this preflight.
  reasons=[]
  for l in p['lines']:
   if not l['anchor_eligible']:reasons.append({'locus':l['locus'],'reason':'PARENT_LINE_NOT_LITERAL_DEFINITE_OR_FEWER_THAN_TWO_GROUPS'})
  rows.append({'id':p['id'],'page':p['page'],'leaf':p['leaf'],'groups':p['groups'],'lines':len(p['lines']),'literal_eligible':not reasons,'reasons':reasons})
 out['panels'][ed]={'complete_paragraphs':len(rows),'literal_paragraphs':sum(r['literal_eligible'] for r in rows),'physical_leaves':len(set(r['leaf'] for r in rows)),'status':'LITERAL_CAPACITY' if sum(r['literal_eligible'] for r in rows)>=32 else 'NO_LITERAL_CAPACITY','rows':rows}
for path in [parent/'src/run.py',parent/'PREREG_LOCK.json',W/'BALNEIS_INCIDENCE_DECISION.md']:
 out['source_hashes'][str(path.relative_to(R))]=hashlib.sha256(path.read_bytes()).hexdigest()
(W/'BALNEIS_CAPACITY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({ed:{k:v for k,v in x.items() if k!='rows'} for ed,x in out['panels'].items()}))
