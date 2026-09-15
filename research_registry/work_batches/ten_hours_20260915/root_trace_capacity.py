"""Prospective23-group complete-calculation capacity, no numeric or carrier fit."""
from pathlib import Path
import importlib.util,json,collections,hashlib,datetime
R=Path.cwd()
D=R/'research_registry/work_batches/ten_hours_20260915'
p=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/src/run.py'
sp=importlib.util.spec_from_file_location('parent928',p)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
panels,dens=m.load();out={}
for ed,ps in panels.items():
    hist=collections.Counter()
    literal_hist=collections.Counter()
    rows=[]
    for par in ps:
        good=all(l['anchor_eligible'] for l in par['lines'])
        hist[par['groups']]+=1
        if good:literal_hist[par['groups']]+=1
        if par['groups']==23:
            rows.append({'id':par['id'],'page':par['page'],'leaf':par['leaf'],
                         'groups':par['groups'],'eligible':good,
                         'ineligible_lines':[l['locus'] for l in par['lines'] if not l['anchor_eligible']]})
    leaves=sorted({r['leaf'] for r in rows if r['eligible']})
    out[ed]={'complete':len(ps),'literal':sum(literal_hist.values()),
             'all_length_histogram':dict(sorted(hist.items())),
             'literal_length_histogram':dict(sorted(literal_hist.items())),
             'candidate_rows':rows,'eligible_physical_leaves':leaves,
             'three_leaf_capacity':len(leaves)>=3}
result={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'decision_sha256':hashlib.sha256((D/'ROOT_TRACE_DECISION.md').read_bytes()).hexdigest(),
        'scope':'metadata and original eligibility only; no numeric/carrier fit',
        'required_groups':23,'required_distinct_physical_leaves':3,
        'denominators':dens,'panels':out,'independent_meaning_confirmation_capacity':0}
(D/'ROOT_TRACE_CAPACITY.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({ed:{k:v for k,v in x.items() if 'histogram' not in k} for ed,x in out.items()},indent=2))
