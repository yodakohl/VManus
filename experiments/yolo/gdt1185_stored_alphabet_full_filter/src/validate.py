from pathlib import Path
import sys,json,hashlib,math,re,importlib.util
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';OLD=ROOT/'experiments/yolo/gdt1184_contextual_initial_styles'
sys.path.insert(0,str(OLD/'src'))
import codec as c
import run as engine
PAT=re.compile(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]')
def signs(w):
 gs=PAT.findall(w);assert ''.join(gs)==w;return gs

def near(a,b):
 if isinstance(a,float):assert math.isclose(a,b,abs_tol=1e-12,rel_tol=0)
 elif isinstance(a,dict):
  assert set(a)==set(b)
  for k in a:near(a[k],b[k])
 elif isinstance(a,list):
  assert len(a)==len(b)
  for x,y in zip(a,b):near(x,y)
 else:assert a==b

def readcheck(name,codec,recipes):
 blocks=(A/name).read_text().strip().split('\n\n');assert len(blocks)==len(recipes);segments=[]
 for block,r in zip(blocks,recipes):
  ws=block.split();decoded=codec.decode([signs(w) for w in ws]);assert decoded==r['words'];assert codec.encode(decoded)==ws;segments.extend(line.split() for line in block.splitlines())
 return engine.m.measure(segments)
def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(engine.SOURCE.read_text());targets=json.loads(engine.TARGET.read_text())['targets'];tables=json.loads((OLD/'artifacts/TABLES.json').read_text());parent=json.loads((OLD/'artifacts/RESULT.json').read_text());result=json.loads((A/'RESULT.json').read_text());total=0;eligible=[]
 expected={f'{model}-R{i}' for model,d in parent['design'].items() for i in range(4) if i!=d['chosen_restart']};assert set(result['design'])==expected
 for key,d in result['design'].items():
  assert d['alphabets']==parent['design'][d['model']]['restarts'][d['restart']]['alphabets'];assert d['restart']!=parent['design'][d['model']]['chosen_restart'];codec=c.Codec(d['model'],tables,d['alphabets']);ok=True
  for col in ['b4','w1']:
   met=readcheck(f'D_{key}_{col}.txt',codec,source[col]);total+=len(source[col]);near(met,d['metrics'][col]);co={ed:engine.m.compare(met,t) for ed,t in targets.items()};near(co,d['comparison'][col]);ok=ok and all(x['joint_screen'] for x in co.values())
  assert ok==d['full_design_pass']
  if ok:eligible.append(key)
 if not eligible:assert result['selected'] is None and not result['transfer_scored'] and result['status']=='STORED_ALTERNATIVES_FAIL_FULL_DESIGN'
 else:
  selected=min(eligible,key=lambda k:(result['design'][k]['table_entries'],result['design'][k]['original_objective'],result['design'][k]['model'],result['design'][k]['restart']));assert result['selected']==selected;d=result['design'][selected];codec=c.Codec(d['model'],tables,d['alphabets']);ok=True
  for col,rs in source.items():
   met=readcheck(f'SELECTED_{col}.txt',codec,rs);total+=len(rs);near(met,result['metrics'][col]);co={ed:engine.m.compare(met,t) for ed,t in targets.items()};near(co,result['comparison'][col]);ok=ok and all(x['joint_screen'] for x in co.values())
  assert result['status']==('FULL_BASIC_SCREEN_PASS' if ok else 'STORED_SELECTED_WRITER_FAILS_TRANSFER')
 out={'status':'PASS','scientific_result':result['status'],'scope':'Six exact frozen alternative tables, failed choices excluded, persisted source decode/rewrite and full inherited criteria','complete_recipe_roundtrips':total,'selected':result['selected']};(A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
