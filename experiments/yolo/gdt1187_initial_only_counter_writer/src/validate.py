from pathlib import Path
import sys,json,hashlib,math,importlib.util
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
import codec as c
spec=importlib.util.spec_from_file_location('writer',D/'src/run.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def close(a,b):
 if isinstance(a,dict):assert set(a)==set(b);[close(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b);[close(x,y) for x,y in zip(a,b)]
 elif isinstance(a,float):assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(a,b)
 else:assert a==b,(a,b)
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 r=json.loads((A/'RESULT.json').read_text());source=json.loads(w.engine.SOURCE.read_text());tables=json.loads(w.engine.TABLES.read_text());targets=json.loads(w.engine.TARGET.read_text())['targets'];roundtrips=0
 for stage,models in [('A',r['stage_A']),('B',r['design'])]:
  for model,e in models.items():
   codec=c.Codec(model,tables,e.get('alphabets'));assert w.engine.coverage(codec.alphabets)
   for book in w.BOOKS:
    texts=(A/f'{stage}_{model}_{book}.txt').read_text().strip().split('\n\n');assert len(texts)==len(source[book]);lines=[]
    for text,recipe in zip(texts,source[book]):
     rows=text.splitlines();words=text.split();assert codec.decode([w.m.glyphs(x) for x in words])==recipe['words'];assert codec.encode(recipe['words'])==words;roundtrips+=1;lines.extend(row.split() for row in rows)
    met=w.m.measure(lines);close(met,e['books'][book]['metrics'] if stage=='A' else e['metrics'][book])
    if stage=='B':
     comp={ed:w.m.compare(met,t) for ed,t in targets.items()};close(comp,e['comparison'][book]);assert e['tight_edit1'][book]=={ed:abs(met['edit1_repeat']-t['edit1_repeat'])<=.01 for ed,t in targets.items()}
   if stage=='A':assert e['necessary_pass']==all(x['within'] for book in e['books'].values() for ch in book['necessary_checks'].values() for x in ch.values())
   else:
    assert e['chosen_restart']==min(range(3),key=lambda i:e['restarts'][i]['optimization']['best_objective']);assert e['alphabets']==e['restarts'][e['chosen_restart']]['alphabets'];assert e['full_pass']==(all(x['joint_screen'] for b in e['comparison'].values() for x in b.values()) and all(x for b in e['tight_edit1'].values() for x in b.values()))
 assert set(r['design'])=={name for name,e in r['stage_A'].items() if e['necessary_pass']};assert r['passing_models']==[name for name,e in r['design'].items() if e['full_pass']]
 (A/'VALIDATION.json').write_text(json.dumps({'status':'PASS','complete_recipe_roundtrips':roundtrips,'scientific_status':r['status']},indent=2)+'\n');print((A/'VALIDATION.json').read_text())
if __name__=='__main__':main()
