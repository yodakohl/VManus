from pathlib import Path
import sys,json,hashlib,importlib.util,os
import codec as c
import fast
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('writer',D/'src/run.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def main():
 assert os.environ.get('PYTHONHASHSEED')=='0'
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 r=json.loads((A/'RESULT.json').read_text());source=json.loads(w.engine.SOURCE.read_text());tables=json.loads(w.engine.TABLES.read_text());targets=json.loads(w.engine.TARGET.read_text())['targets'];roundtrips=0
 assert list(r['models'])==c.MODELS[:len(r['models'])]
 for model,e in r['models'].items():
  codec=c.Codec(model,tables,e['alphabets'],e['assignment']);assert codec.units==e['units'];assert w.engine.coverage(e['alphabets']);assert r['parity_checks'][model]==16
  pub=json.loads((A/(model+'_PUBLIC_TABLE.json')).read_text());assert pub['entries']=={u:{'rank':rank,'tail':list(ds)} for u,(rank,ds) in codec.encoded.items()}
  for book in w.BOOKS:
   blocks=(A/f'{model}_{book}.txt').read_text().strip().split('\n\n');assert len(blocks)==len(source[book]);lines=[]
   for text,recipe in zip(blocks,source[book]):
    words=text.split();decoded=codec.decode([w.m.glyphs(x) for x in words]);assert decoded==recipe['words'];assert codec.encode(decoded)==words;roundtrips+=1;lines.extend(line.split() for line in text.splitlines())
   met=w.m.measure(lines);fast.close(met,e['metrics'][book]);fast.close({ed:w.m.compare(met,t) for ed,t in targets.items()},e['comparison'][book]);assert e['tight_edit1'][book]=={ed:abs(met['edit1_repeat']-t['edit1_repeat'])<=.01 for ed,t in targets.items()}
  full=all(x['joint_screen'] for b in e['comparison'].values() for x in b.values()) and all(x for b in e['tight_edit1'].values() for x in b.values());assert full==e['full_pass'];assert e['search']['attempted']<=6000
 assert r['selected']==next((name for name,e in r['models'].items() if e['full_pass']),None)
 assert r['status']==('FULL_BASIC_AND_TIGHT_EDIT_SCREEN_PASS' if r['selected'] else 'SOURCE_CODE_ASSIGNMENT_SEARCH_FAILS')
 (A/'VALIDATION.json').write_text(json.dumps({'status':'PASS','complete_recipe_roundtrips':roundtrips,'parity_map_book_checks':sum(r['parity_checks'].values()),'scientific_status':r['status']},indent=2)+'\n');print((A/'VALIDATION.json').read_text())
if __name__=='__main__':main()
