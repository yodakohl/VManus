from pathlib import Path
import sys,json,hashlib,os,importlib.util
import numpy as np
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('exchange',D/'src/run.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);w=x.w

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 r=json.loads((A/'RESULT.json').read_text());pairs=json.loads((A/'CANDIDATES.json').read_text());tested=json.loads((A/'TESTED.json').read_text());source,tables,targets,base,codec,cache=x.prepare();pairs2,summary=x.length_candidates(cache,base,targets);assert pairs2==pairs and summary==r['filter'];assert len(tested)==r['tested_count']<=2000
 for rank,t in enumerate(tested):assert t['rank']==rank and t['pair']==pairs[rank][1:] and t['affected_occurrences']==pairs[rank][0]
 checks=0;roundtrips=0
 U=len(base['assignment']);lens=cache.lengths[np.array(base['assignment'])];width=max(int(lens.max()),max(int(k) for t in targets.values() for k in t['length_counts']))+1;positions=np.arange(width);freq={b:np.bincount(data[:,0],minlength=U) for b,data in cache.books.items()};hists={b:np.bincount(lens[data[:,0]],minlength=width) for b,data in cache.books.items()};totalfreq=sum(freq.values());independent=[]
 for i in range(U-1):
  jj=np.arange(i+1,U);keep=lens[i]!=lens[jj]
  for b in w.BOOKS:
   hs=np.tile(hists[b],(len(jj),1));delta=freq[b][i]-freq[b][jj];hs[:,lens[i]]-=delta;hs[np.arange(len(jj)),lens[jj]]+=delta
   mean=(hs@positions)/8000;sd=np.sqrt(np.maximum(0,(hs@(positions*positions))/8000-mean*mean))
   for target in targets.values():
    th=np.array([target['length_counts'].get(str(k),0) for k in positions]);keep&=(abs(mean-target['mean_length'])<=.2*target['mean_length']+1e-12)&(abs(sd-target['sd_length'])<=.25*target['sd_length']+1e-12)&(np.abs(hs-th).sum(axis=1)<=3200)
  independent.extend([int(totalfreq[i]+totalfreq[j]),i,int(j)] for j in jj[keep])
 independent.sort();assert independent==pairs
 # Independent actual glyph-length reconstruction for every tested table,
 # not the analytical two-bin update used to shortlist it.
 for t in tested:
  p=base['assignment'][:];i,j=t['pair'];p[i],p[j]=p[j],p[i]
  for book,matrix,lengths,recipes in cache.matrices(p,base['alphabets']):
   values=lengths.tolist();hist={str(n):values.count(n) for n in set(values)};mean=sum(values)/8000;sd=(sum((n-mean)**2 for n in values)/8000)**.5
   for ed,target in targets.items():
    assert abs(mean-target['mean_length'])<=.2*target['mean_length']+1e-12;assert abs(sd-target['sd_length'])<=.25*target['sd_length']+1e-12
    assert sum(abs(hist.get(k,0)-target['length_counts'].get(k,0)) for k in hist.keys()|target['length_counts'].keys())<=3200
   checks+=1
 selected=r['selected']
 if selected:
  assert tested[-1]['full_pass'] and not any(t['full_pass'] for t in tested[:-1]);writer=w.c.Codec(x.MODEL,tables,selected['alphabets'],selected['assignment']);i,j=selected['pair'];expected=base['assignment'][:];expected[i],expected[j]=expected[j],expected[i];assert expected==selected['assignment'];assert selected['alphabets']==base['alphabets'];pub=json.loads((A/'PUBLIC_TABLE.json').read_text());assert pub['entries']=={u:{'rank':rank,'tail':list(ds)} for u,(rank,ds) in writer.encoded.items()}
  for book in w.BOOKS:
   pages=(A/(book+'.txt')).read_text().strip().split('\n\n');assert len(pages)==len(source[book]);lines=[]
   for page,recipe in zip(pages,source[book]):
    words=page.split();decoded=writer.decode([w.m.glyphs(word) for word in words]);assert decoded==recipe['words'];assert writer.encode(decoded)==words;roundtrips+=1;lines.extend(line.split() for line in page.splitlines())
   met=w.m.measure(lines);w.fast.close(met,selected['metrics'][book]);comp={ed:w.m.compare(met,t) for ed,t in targets.items()};w.fast.close(comp,selected['comparison'][book]);assert all(z['joint_screen'] for z in comp.values());assert all(abs(met['edit1_repeat']-t['edit1_repeat'])<=.01 for t in targets.values())
 assert (selected is not None)==(r['status']=='FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS')
 (A/'VALIDATION.json').write_text(json.dumps({'status':'PASS','complete_recipe_roundtrips':roundtrips,'direct_length_book_checks':checks,'complete_candidate_filter_reproduced':True,'independent_full_histogram_pair_checks':U*(U-1)//2,'scientific_status':r['status']},indent=2)+'\n');print((A/'VALIDATION.json').read_text())
if __name__=='__main__':main()
