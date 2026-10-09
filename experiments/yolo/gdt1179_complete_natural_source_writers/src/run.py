#!/usr/bin/env python3
from pathlib import Path
import sys,json,hashlib
from collections import Counter
import writers as w
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/src'))
import metrics as m
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
def save(name,obj):(A/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def wrap(words):
 lines=[];line=[];size=0
 for word in words:
  n=len(m.glyphs(word))
  if line and size+1+n>48:lines.append(line);line=[];size=0
  size+=n+bool(line);line.append(word)
 if line:lines.append(line)
 return lines

def calculate():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];dictionary=w.train(source)
 assert len(dictionary)==503
 metrics={};comparison={};output={};roundtrips={}
 for mode in 'ABC':
  metrics[mode]={};comparison[mode]={};output[mode]={};roundtrips[mode]={}
  for col,rs in source.items():
   writer=w.Writer(mode,dictionary);reader=w.Reader(mode,dictionary);pages=[];observed=[]
   for r in rs:
    rows=writer.paragraph(r['words']);lines=wrap(rows)
    assert all(m.glyphs(word) for line in lines for word in line)
    decoded=reader.paragraph([m.glyphs(word) for line in lines for word in line]);assert decoded==r['words'],(mode,col,r['id'])
    pages.append(lines);observed.append(rows)
   # A second independent run of the public encoder sees only decoded words;
   # no original grouping metadata or hidden word-boundary labels are needed.
   roundtrips[mode][col]={'complete_recipes':len(rs),'source_words':sum(len(r['words']) for r in rs),'all_exact':True,'written_groups':sum(len(x) for x in observed)}
   metrics[mode][col]=m.measure([line for page in pages for line in page])
   comparison[mode][col]={ed:m.compare(metrics[mode][col],t) for ed,t in targets.items()}
   output[mode][col]=pages
 for col in source:
  for key in ('types','type_ratio','top10_share'):assert metrics['A'][col][key]==metrics['B'][col][key],('A/B injectivity',key)
 examples={}
 source_examples=[['in','dem'],['indem'],['nicht','salzen'],['einen'],['zauberknolle'],['salz','wasser','salz','wasser']]
 for mode in 'ABC':
  writer=w.Writer(mode,dictionary);reader=w.Reader(mode,dictionary);es=[]
  for x in source_examples:
   encoded=writer.paragraph(x);decoded=reader.paragraph([m.glyphs(z) for z in encoded]);assert decoded==x
   es.append({'source':x,'written':encoded,'decoded':decoded})
  assert es[0]['written']!=es[1]['written']
  examples[mode]=es
 passing=[mode for mode in 'ABC' if all(v['joint_screen'] for col in comparison[mode].values() for v in col.values())]
 result={'experiment':'GDT1179','status':'FULL_BASIC_SCREEN_PASS' if passing else 'ALL_COMPLETE_WRITERS_FAIL_FULL_SCREEN','metrics':metrics,'comparison':comparison,'roundtrips':roundtrips,'passing_models':passing,'dictionary_entries':len(dictionary),'training_collections':['b4','w1'],'exposed_transfer_collections':['bs1','gr1'],'claim_ceiling':'Complete normalized-source writing; full basic descriptive filter only; no native interpretation, historical practicality, independent confirmation or stronger structural validation.'}
 return result,output,dictionary,examples

def main():
 r,output,dictionary,examples=calculate()
 save('RESULT.json',r);save('DICTIONARY.json',{'training':['b4','w1'],'entries':[{'rank':i,'source_word':x,'glyphs':w.rankcode(i)} for i,x in enumerate(dictionary)]});save('EXAMPLES.json',examples)
 for mode,books in output.items():
  for col,pages in books.items():
   (A/f'{mode}_{col}.txt').write_text('\n\n'.join('\n'.join(' '.join(line) for line in page) for page in pages)+'\n')
 print(json.dumps({'status':r['status'],'passing':r['passing_models'],'results':{mode:{col:{'mean':r['metrics'][mode][col]['mean_length'],'sd':r['metrics'][mode][col]['sd_length'],'top10':r['metrics'][mode][col]['top10_share'],'types':r['metrics'][mode][col]['type_ratio'],'h2':r['metrics'][mode][col]['conditional_entropy'],'pass_counts':{ed:z['passed'] for ed,z in values.items()}} for col,values in books.items()} for mode,books in r['comparison'].items()}},indent=2))
if __name__=='__main__':main()
