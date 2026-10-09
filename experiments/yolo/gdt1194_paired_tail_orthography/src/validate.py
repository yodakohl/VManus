from pathlib import Path
import json,hashlib,os,importlib.util,itertools
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('orthography_runner',D/'src/run.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)

def fixtures():
 count=0
 for n in range(6):
  for digits in itertools.product(range(3),repeat=n):
   for mask in (0,1,5,18,73,170,511):
    code=x.contract(list(digits),mask);back=[]
    for v in code:back.extend([v] if v<3 else divmod(v-3,3))
    assert back==list(digits);assert x.contract(back,mask)==code;count+=1
 return count

def main():
 assert os.environ.get('PYTHONHASHSEED')=='0';fc=fixtures()
 if '--fixtures' in __import__('sys').argv:print(json.dumps({'status':'PASS','pair_roundtrips':fc}));return
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source,tables,targets,base,inner,cache=x.prepare();fast=x.Fast(cache,base);r=json.loads((A/'RESULT.json').read_text());cands,qs=fast.candidates(targets);assert cands==json.loads((A/'LENGTH_CANDIDATES.json').read_text());assert len(cands)==r['length_candidates'];checks=roundtrips=0
 for depth,arm in r['arms'].items():
  depth=int(depth);ys=arm['y_feasibility']
  if ys['solver_status']=='verified_feasible':
   counts=fast.y_counts(depth);totals=[sum(int(counts[b,c,i]) for c,i in enumerate(ys['choice'])) for b in range(4)];assert totals==ys['source_counts'];assert all(ys['allowed_counts'][0]<=n<=ys['allowed_counts'][1] for n in totals)
  if 'best' not in arm:continue
  assert arm['parity_checks']==16;best=arm['best'];p=best['params'];assert x.legal(p);assert any(mask==p['mask'] and q==p['qpos'] for _,mask,q in cands);e,full,met,comp,extra=x.evaluate(fast,p,targets);assert abs(e-best['energy'])<1e-12 and full==best['full_pass'];x.w.fast.close(met,best['metrics']);x.w.fast.close(comp,best['comparison']);x.w.fast.close(extra,best['extra']);writer=x.Writer(inner,p)
  for b in x.BOOKS:
   pages=(A/f'D{depth}_{b}.txt').read_text().strip().split('\n\n');assert len(pages)==len(source[b]);lines=[]
   for page,recipe in zip(pages,source[b]):
    words=page.split();decoded=writer.decode([x.w.m.glyphs(w) for w in words]);assert decoded==recipe['words'];assert writer.encode(decoded)==words;roundtrips+=1;lines.extend(line.split() for line in page.splitlines())
   observed=x.w.m.measure(lines);x.w.fast.close(observed,met[b]);checks+=1
   if full:
    assert all(x.w.m.compare(observed,t)['joint_screen'] for t in targets.values());assert all(abs(observed['edit1_repeat']-t['edit1_repeat'])<=.01 for t in targets.values());assert all(z['within'] for d in extra[b].values() for z in d.values())
 if r['selected'] is not None:assert r['arms'][str(r['selected'])]['best']['full_pass'] and r['status']=='FULL_STRENGTHENED_CONTROL_SCREEN_PASS'
 out={'status':'PASS','pair_roundtrip_fixtures':fc,'length_filter_reproduced':True,'full_recipe_inverse_and_rewrite':roundtrips,'frozen_metric_book_checks':checks,'scientific_status':r['status']};(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
