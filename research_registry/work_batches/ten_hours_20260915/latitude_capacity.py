"""Metadata-only fixed7/12 complete-paragraph capacity; no carrier/numeral fit."""
from pathlib import Path
import importlib.util,json,collections
R=Path.cwd();p=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/src/run.py';sp=importlib.util.spec_from_file_location('parent928',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
panels,_=m.load();out={}
for ed,ps in panels.items():
 good=[p for p in ps if all(l['anchor_eligible'] for l in p['lines'])]
 out[ed]={'complete':len(ps),'literal':len(good),'nonliteral':len(ps)-len(good),'literal_length_histogram':dict(sorted(collections.Counter(p['groups'] for p in good).items())),'models':{}}
 for model,n in [('FUSED',7),('SEPARATE',12)]:
  rs=[{'id':p['id'],'page':p['page'],'leaf':p['leaf'],'groups':p['groups']} for p in good if p['groups']==n];leaves=sorted({p['leaf'] for p in rs});out[ed]['models'][model]={'paragraphs':len(rs),'physical_leaves':leaves,'minimum_three_leaf_capacity':len(leaves)>=3,'rows':rs}
result={'scope':'metadata and eligibility only; no carrier counts or code fit','independent_confirmation_capacity':0,'panels':out};q=Path('research_registry/work_batches/ten_hours_20260915/LATITUDE_CAPACITY.json');q.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({ed:{'complete':d['complete'],'literal':d['literal'],'models':{m:{k:v for k,v in x.items() if k!='rows'} for m,x in d['models'].items()}} for ed,d in out.items()},indent=2))
