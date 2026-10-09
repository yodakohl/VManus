from pathlib import Path
import sys,json,hashlib,os,importlib.util
import numpy as np
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';OLD=ROOT/'experiments/yolo/gdt1191_source_codebook_assignment'
sys.path.insert(0,str(OLD/'src'));spec=importlib.util.spec_from_file_location('assignment',OLD/'src/run.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
MODEL='H2048-S6-K7'
def save(n,x):(A/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def prepare():
 source=json.loads(w.engine.SOURCE.read_text());tables=json.loads(w.engine.TABLES.read_text());targets=json.loads(w.engine.TARGET.read_text())['targets'];baseline=json.loads((OLD/'artifacts/RESULT.json').read_text())['models'][MODEL];codec=w.c.Codec(MODEL,tables,baseline['alphabets'],baseline['assignment']);cache=w.fast.Cache(codec,source);return source,tables,targets,baseline,codec,cache

def length_candidates(cache,baseline,targets):
 U=len(baseline['assignment']);code_lengths=cache.lengths[np.array(baseline['assignment'])].astype(np.int64);counts={b:np.bincount(data[:,0],minlength=U).astype(np.int64) for b,data in cache.books.items()};total_counts=sum(counts.values());W=max(int(cache.lengths.max()),max(int(k) for t in targets.values() for k in t['length_counts']))+1;hists={b:np.bincount(code_lengths[data[:,0]],minlength=W).astype(np.int64) for b,data in cache.books.items()};sums={b:int(np.dot(h,np.arange(W))) for b,h in hists.items()};sq={b:int(np.dot(h,np.arange(W)**2)) for b,h in hists.items()};targeth={ed:np.array([t['length_counts'].get(str(k),0) for k in range(W)],dtype=np.int64) for ed,t in targets.items()};assert all(t['tokens']==8000 for t in targets.values());rows=[];same=0
 for i in range(U-1):
  js=np.arange(i+1,U);la=int(code_lengths[i]);lb=code_lengths[js];keep=la!=lb;same+=int((~keep).sum())
  for book in w.BOOKS:
   delta=counts[book][i]-counts[book][js];means=(sums[book]+(lb-la)*delta)/8000;variances=(sq[book]+(lb*lb-la*la)*delta)/8000-means*means;sds=np.sqrt(np.maximum(0,variances));hist=hists[book]
   for ed,t in targets.items():
    keep&=(abs(means-t['mean_length'])<=.2*t['mean_length']+1e-12)&(abs(sds-t['sd_length'])<=.25*t['sd_length']+1e-12)
    th=targeth[ed];base=int(np.abs(hist-th).sum());distance=base+np.abs(hist[la]-delta-th[la])-abs(int(hist[la]-th[la]))+np.abs(hist[lb]+delta-th[lb])-np.abs(hist[lb]-th[lb]);keep&=distance<=3200
  for j in js[keep]:rows.append([int(total_counts[i]+total_counts[j]),i,int(j)])
 rows.sort();return rows,{'units':U,'unordered_pairs':U*(U-1)//2,'equal_length_skipped':same,'length_survivors':len(rows),'histograms':{b:{str(k):int(v) for k,v in enumerate(h) if v} for b,h in hists.items()},'glyph_totals':sums,'squared_length_totals':sq}

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source,tables,targets,baseline,codec,cache=prepare();pairs,summary=length_candidates(cache,baseline,targets);save('LENGTH_FILTER.json',summary);save('CANDIDATES.json',pairs);print(json.dumps(summary),flush=True);tested=[];selected=None
 for rank,(affected,i,j) in enumerate(pairs[:2000]):
  perm=baseline['assignment'][:];perm[i],perm[j]=perm[j],perm[i];energy,full,met,comp,tight=w.evaluate(cache,perm,baseline['alphabets'],targets);tested.append({'rank':rank,'pair':[i,j],'affected_occurrences':affected,'energy':energy,'full_pass':full})
  if full:
   selected={'rank':rank,'pair':[i,j],'source_entries':[codec.units[i],codec.units[j]],'affected_occurrences':affected,'assignment':perm,'alphabets':baseline['alphabets'],'metrics':met,'comparison':comp,'tight_edit1':tight,'energy':energy};break
  if rank%100==0:print(json.dumps(tested[-1]),flush=True);save('TESTED.json',tested)
 if selected:
  writer=w.c.Codec(MODEL,tables,selected['alphabets'],selected['assignment']);roundtrips=0
  for book in w.BOOKS:
   ps,_=w.engine.pages(writer,source[book]);observed=w.engine.measure(ps);w.fast.close(observed,selected['metrics'][book]);roundtrips+=len(source[book]);(A/(book+'.txt')).write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in ps)+'\n')
  selected['complete_recipe_roundtrips']=roundtrips;save('PUBLIC_TABLE.json',{'model':MODEL,'alphabets':selected['alphabets'],'entries':{u:{'rank':r,'tail':list(ds)} for u,(r,ds) in writer.encoded.items()},'rules':'Longest matching literal fragment; character count modulo6 changes initial rank modulo7; three public styles; E/C preserves source word endings; spaces delimit codes and blank paragraphs reset.'})
 result={'experiment':'GDT1192','status':'FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS' if selected else 'ONE_EXCHANGE_COMPLETE_FILTER_FAILS' if len(tested)==len(pairs) else 'ONE_EXCHANGE_BOUNDED_PREFIX_FAILS','model':MODEL,'filter':summary,'tested_count':len(tested),'all_filtered_examined':len(tested)==len(pairs),'selected':selected,'claim_ceiling':'Engineered complete source-control writer under known basic summaries; not native meanings, independent confirmation, historical usability or stronger structure.'};save('TESTED.json',tested);save('RESULT.json',result);print(json.dumps({'status':result['status'],'tested_count':len(tested),'selected_rank':None if selected is None else selected['rank']}),flush=True)
if __name__=='__main__':main()
