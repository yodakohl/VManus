from pathlib import Path
import sys,json,hashlib,os,importlib.util,itertools
import numpy as np
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('cycle',D/'src/run.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);w=x.w

def fixtures():
 count=0
 for ra,rb,rc,fi,fj,ori in itertools.product(range(-2,3),range(-2,3),range(-2,3),range(4),range(4),range(2)):
  baseline=abs(ra)+abs(rb)+abs(rc)+3
  for budget in (3,6,9):
   low,high,valid=x.tv_interval(ra,rb,rc,baseline,fi,fj,ori,budget)
   for fk in range(7):
    rr=(ra-fi+fk,rb-fj+fi,rc-fk+fj) if ori==0 else (ra-fi+fj,rb-fj+fk,rc-fk+fi)
    assert (sum(abs(z) for z in rr)+3<=budget)==bool(valid and low<=fk<=high);count+=1
 rng=x.Ranges([0,2,2,4,8])
 for lo in range(-1,10):
  for hi in range(-1,10):assert rng.between(lo,hi)==sum(1<<i for i,z in enumerate([0,2,2,4,8]) if lo<=z<=hi)
 return count

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0';checks=fixtures()
 if '--fixtures' in sys.argv:print(json.dumps({'status':'PASS','interval_fixtures':checks}));return
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source,tables,targets,base,codec,cache=x.prepare();r=json.loads((A/'RESULT.json').read_text());rows=json.loads((A/'CANDIDATES.json').read_text());tested=json.loads((A/'TESTED.json').read_text());rows2,summary=x.candidates(cache,base,targets);assert rows==rows2 and summary==r['filter'];assert len(tested)==r['tested_count']<=2000
 # Independent literal per-position lengths for every retained candidate.
 lens=cache.lengths[np.array(base['assignment'])];W=max(int(lens.max()),max(int(k) for t in targets.values() for k in t['length_counts']))+1;length_checks=0
 for row in rows:
  p=x.apply_cycle(base,row);newlens=cache.lengths[np.array(p)];assert len(set(p))==len(p)
  for b in w.BOOKS:
   values=newlens[cache.books[b][:,0]];hist=np.bincount(values,minlength=W);mean=float(values.mean())
   for target in targets.values():
    th=np.array([target['length_counts'].get(str(k),0) for k in range(W)]);assert abs(mean-target['mean_length'])<=.2*target['mean_length']+1e-12;assert int(abs(hist-th).sum())<=3200
   length_checks+=1
 for rank,t in enumerate(tested):
  assert t['rank']==rank and t['cycle']==rows[rank];e,full,*_=w.evaluate(cache,x.apply_cycle(base,rows[rank]),base['alphabets'],targets);assert full==t['full_pass'];assert abs(e-t['energy'])<1e-12
 selected=r['selected'];roundtrips=0;frozen_checks=0
 if selected:
  assert tested[-1]['full_pass'] and not any(t['full_pass'] for t in tested[:-1]);assert selected['assignment']==x.apply_cycle(base,rows[selected['rank']]);assert selected['alphabets']==base['alphabets'];writer=w.c.Codec(x.MODEL,tables,selected['alphabets'],selected['assignment']);pub=json.loads((A/'PUBLIC_TABLE.json').read_text());assert pub['entries']=={u:{'rank':rank,'tail':list(ds)} for u,(rank,ds) in writer.encoded.items()}
  for book in w.BOOKS:
   pages=(A/(book+'.txt')).read_text().strip().split('\n\n');assert len(pages)==len(source[book]);lines=[]
   for page,recipe in zip(pages,source[book]):
    groups=page.split();decoded=writer.decode([w.m.glyphs(word) for word in groups]);assert decoded==recipe['words'];assert writer.encode(decoded)==groups;roundtrips+=1;lines.extend(line.split() for line in page.splitlines())
   met=w.m.measure(lines);w.fast.close(met,selected['metrics'][book]);comp={ed:w.m.compare(met,t) for ed,t in targets.items()};w.fast.close(comp,selected['comparison'][book]);assert all(z['joint_screen'] for z in comp.values());assert all(abs(met['edit1_repeat']-t['edit1_repeat'])<=.01 for t in targets.values());frozen_checks+=1
 assert (selected is not None)==(r['status']=='FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS')
 result={'status':'PASS','interval_fixtures':checks,'complete_candidate_filter_reproduced':True,'literal_length_book_checks':length_checks,'full_metric_decisions_recomputed':len(tested),'frozen_metric_book_checks':frozen_checks,'complete_recipe_roundtrips':roundtrips,'scientific_status':r['status']};(A/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
