from pathlib import Path
import json,sys,hashlib
import codec as c
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/src'))
import metrics as m
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
def save(name,obj):(A/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def wrap(words):
 lines=[];line=[];size=0
 for word in words:
  n=len(m.glyphs(word))
  if line and size+1+n>48:lines.append(line);line=[];size=0
  size+=n+bool(line);line.append(word)
 if line:lines.append(line)
 return lines

def main():
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];tables=c.train(source);save('TABLES.json',tables)
 measures={};comparisons={};roundtrips={};cost={}
 for model in c.MODELS:
  codec=c.Codec(model,tables);measures[model]={};comparisons[model]={};roundtrips[model]={}
  cost[model]={'common_table_correspondences':21*len(tables['models'][model]),'global_escape_inventory':len(c.UNITS),'context_states':int(model[1]),'positional_tables_per_state':1 if model.endswith('flat') else 3}
  for col,rs in source.items():
   pages=[];escapes=total=0
   for r in rs:
    words=codec.encode(r['words']);rows=[m.glyphs(x) for x in words];assert codec.decode(rows)==r['words'];lines=wrap(words);pages.append(lines);escapes+=sum(gs.count('q') for gs in rows);total+=sum(map(len,rows))
   segments=[line for page in pages for line in page];measures[model][col]=m.measure(segments);comparisons[model][col]={ed:m.compare(measures[model][col],t) for ed,t in targets.items()};roundtrips[model][col]={'recipes':len(rs),'words':sum(len(r['words']) for r in rs),'glyphs':total,'escapes':escapes,'exact':True}
   (A/f'{model}_{col}.txt').write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in pages)+'\n')
 passing=[model for model in c.MODELS if all(v['joint_screen'] for book in comparisons[model].values() for v in book.values())]
 result={'experiment':'GDT1180','status':'FULL_BASIC_SCREEN_PASS' if passing else 'ALL_CONTEXT_ALPHABETS_FAIL_FULL_SCREEN','passing_models':passing,'metrics':measures,'comparison':comparisons,'roundtrips':roundtrips,'costs':cost,'claim_ceiling':'Exposed-source forward construction only; no native reading or stronger structural/historical validation.'};save('RESULT.json',result)
 examples={}
 for model in c.MODELS:
  codec=c.Codec(model,tables);words=['in','dem','indem','nicht','salzen','zauberknolle','schnecken'];written=codec.encode(words);assert codec.decode([m.glyphs(x) for x in written])==words;examples[model]={'source':words,'written':written}
 save('EXAMPLES.json',examples)
 print(json.dumps({'status':result['status'],'results':{model:{col:{k:round(v,5) for k,v in met.items() if k in ['mean_length','sd_length','top10_share','type_ratio','conditional_entropy','first_last_js','exact_repeat_rate','edit1_rate']} for col,met in books.items()} for model,books in measures.items()}},indent=2))
if __name__=='__main__':main()
