from pathlib import Path
import importlib.util,json,os,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('witness_run',D/'src/run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r);x=r.x

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 result=json.loads((A/'RESULT.json').read_text());cap=json.loads((A/'CAPACITY.json').read_text());source,tables,targets,base,inner,cache=x.prepare();fast=x.Fast(cache,base);assert fast.y_counts(2).tolist()==cap['counts'];witness=result['witness'];assert witness==cap['witness'];roundtrips=checks=0
 if witness['choice'] is not None:
  choice=witness['choice'];assert len(choice)==13 and all(0<=i<6 for i in choice);totals=[sum(cap['counts'][b][c][i] for c,i in enumerate(choice)) for b in range(4)];assert totals==witness['book_counts'] and all(2922<=n<=3364 for n in totals);assert result['parity_checks']==16;best=result['best'];p=best['params'];assert x.legal(p);candidates,_=fast.candidates(targets);assert any(mask==p['mask'] and q==p['qpos'] for _,mask,q in candidates);e,full,met,comp,extra=x.evaluate(fast,p,targets);assert abs(e-best['energy'])<1e-12;assert full==result['selected']==best['full_pass'];x.w.fast.close(met,best['metrics']);x.w.fast.close(comp,best['comparison']);x.w.fast.close(extra,best['extra']);writer=x.Writer(inner,p)
  for b in x.BOOKS:
   pages=(A/(b+'.txt')).read_text().strip().split('\n\n');assert len(pages)==len(source[b]);lines=[]
   for page,recipe in zip(pages,source[b]):
    words=page.split();decoded=writer.decode([x.w.m.glyphs(word) for word in words]);assert decoded==recipe['words'];assert writer.encode(decoded)==words;roundtrips+=1;lines.extend(line.split() for line in page.splitlines())
   observed=x.w.m.measure(lines);x.w.fast.close(observed,met[b]);checks+=1
   if full:
    assert all(x.w.m.compare(observed,t)['joint_screen'] for t in targets.values());assert all(abs(observed['edit1_repeat']-t['edit1_repeat'])<=.01 for t in targets.values());assert all(z['within'] for d in extra[b].values() for z in d.values())
 assert result['selected']==(result['status']=='FULL_STRENGTHENED_CONTROL_SCREEN_PASS')
 out={'status':'PASS','capacity_witness_verified':witness['choice'] is not None,'complete_recipe_roundtrips':roundtrips,'frozen_metric_book_checks':checks,'scientific_status':result['status']};(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
