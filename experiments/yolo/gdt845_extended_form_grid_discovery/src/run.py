import importlib.util,itertools,json,re
from pathlib import Path
from collections import Counter
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
spec=json.loads((E/'src/SPEC.json').read_text())
p=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py'
x=importlib.util.spec_from_file_location('source_reader',p);m=importlib.util.module_from_spec(x);x.loader.exec_module(m)
def save(name,x): (E/'artifacts'/name).write_text(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n')
rows,guard=m.query(spec)
words={w+h+c+'e'*n+'d'*d+'y':(w,h,c,n,d) for w,h,c,n,d in itertools.product(spec['wrappers'],spec['heads'],spec['middles'],spec['e_lengths'],spec['d_states'])}
hits=[r for r in rows if r['ivtff_group_raw'] in words];save('HITS.json',hits);save('GUARD.json',guard)
counts=Counter((r['edition'],r['ivtff_group_raw']) for r in hits)
lc=Counter((r['edition'],r['locus'],r['ivtff_group_raw']) for r in hits)
cells=[]
for word,(w,h,c,n,d) in sorted(words.items()):
    loci={r['locus'] for r in hits if r['ivtff_group_raw']==word}
    cells.append(dict(word=word,wrapper=w,head=h,middle=c,e=n,d=d,counts={ed:counts[ed,word] for ed in spec['editions']},folios={ed:sorted({re.match(r'f[0-9]+',r['page']).group() for r in hits if r['edition']==ed and r['ivtff_group_raw']==word}) for ed in spec['editions']},shared_locus_multiplicity=sum(min(lc[ed,l,word] for ed in spec['editions']) for l in loci)))
summary=[]
for ed,w in itertools.product(spec['editions'],spec['wrappers']):
    observed=0;expected=0.;strata=[]
    for h,c in itertools.product(spec['heads'],spec['middles']):
        subset=[r for r in cells if (r['wrapper'],r['head'],r['middle'])==(w,h,c)]
        total=sum(r['counts'][ed] for r in subset);e2=sum(r['counts'][ed] for r in subset if r['e']==2);d1=sum(r['counts'][ed] for r in subset if r['d']==1);joint=sum(r['counts'][ed] for r in subset if r['e']==2 and r['d']==1)
        exp=e2*d1/total if total else 0;expected+=exp;observed+=joint
        strata.append(dict(head=h,middle=c,n=total,e2=e2,d1=d1,joint=joint,expected=exp))
    summary.append(dict(edition=ed,wrapper=w,observed=observed,expected=expected,strata=strata))
save('CELLS.json',cells);save('RESULT.json',dict(status='DESCRIPTIVE_GRID_COMPLETE_NO_CONFIRMATORY_TEST',source_rows=len(rows),hit_rows=len(hits),cells=len(cells),occupied={ed:sum(r['counts'][ed]>0 for r in cells) for ed in spec['editions']},summary=summary));print(json.dumps(json.loads((E/'artifacts/RESULT.json').read_text())))
