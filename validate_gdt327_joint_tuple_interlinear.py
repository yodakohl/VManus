#!/usr/bin/env python3
"""Independently validate the GDT327 joint-tuple interlinear."""
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;OUT=R/'gdt327_validation.json';RESULT=R/'gdt327_result.json';COORD=('local_frame','inner_d','right_family','dy_closure','b3')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(n):
 with (R/n).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def hid(p,v):return hashlib.sha256((p+'|'+'|'.join(v)).encode()).hexdigest()[:20]
def close(a,b,t=3e-9):return abs(float(a)-float(b))<=t
def main():
 checks=[]
 def check(n,c):
  if not c:raise AssertionError(n)
  checks.append(n)
 res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');check('result_content',stored==can(res));source=[x for x in read('gdt278_native_event_inventory.tsv') if x['control_id']=='VOYNICH_REFERENCE'];check('source',len(source)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in source));inter=read('gdt327_joint_tuple_interlinear.tsv');check('rows',len(inter)==len(source));model=json.loads((R/'gdt322_renderer_model.json').read_text());classes=model['classes'];lex={x['cell_id']:x for x in read('gdt322_opaque_cell_lexicon.tsv')};positions={(x['locus'],int(x['group_index'])):x for x in source};covered=0
 for i,(x,y) in enumerate(zip(source,inter)):
  coord=tuple(x[k] for k in COORD);cell=hid('CELL',(x['page_host'],)+coord);previous=positions.get((x['locus'],int(x['group_index'])-1));line=int(x['group_index']=='1');prev=int(previous is not None and previous['dy_closure']=='1');check(f'id_{i}',y['event_id_sha256']==hashlib.sha256(x['observation_id'].encode()).hexdigest()[:20] and y['joint_tuple_id']==cell and y['host_id']==hid('HOST',(x['page_host'],)) and y['coordinate_id']==hid('COORD',coord));check(f'context_{i}',int(y['line_first'])==line and int(y['prev_dy'])==prev and y['observed_wrapper']==x['wrapper']);check(f'unassigned_{i}',y['semantic_state']=='UNASSIGNED' and y['translation_state']=='UNASSIGNED')
  if cell in lex:
   covered+=1;counts=json.loads(lex[cell]['wrapper_counts_json']);scores=np.array([math.log(counts[w]+model['alpha']) for w in classes]);scores[classes.index('s')]+=model['beta_s_line_first']*line;scores[classes.index('q')]+=model['beta_q_prev_dy']*prev;scores-=scores.max();p=np.exp(scores);p/=p.sum();check(f'prob_{i}',y['renderer_state']=='EXECUTABLE_POWERED_CELL' and close(y['observed_wrapper_probability'],p[classes.index(x['wrapper'])]) and close(y['observed_wrapper_surprisal_bits'],-math.log2(p[classes.index(x['wrapper'])])))
  else:check(f'unknown_{i}',y['renderer_state']=='UNLICENSED_OR_UNKNOWN' and y['observed_wrapper_probability']=='' and y['wrapper_probabilities_json']=='')
 check('coverage',covered==5607);atlas=read('gdt327_joint_tuple_atlas.tsv');check('atlas',len(atlas)==1676 and sum(int(x['events']) for x in atlas)==8448 and sum(x['renderer_state']=='EXECUTABLE_POWERED_CELL' for x in atlas)==126);grammar=json.loads((R/'gdt327_executable_grammar.json').read_text());gs=grammar.pop('content_sha256');check('grammar_content',gs==can(grammar));check('grammar_counts',grammar['events']==8448 and grammar['joint_tuples']==1676 and grammar['executable_events']==5607 and grammar['semantic_assignments']==grammar['translation_assignments']==0);check('inputs',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));check('docs',all(res['documents'][n]==sha(R/n) for n in res['documents']));check('impl',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));check('outputs',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));check('f84',res['f84']['input_rows']==0 and not any(v for k,v in res['f84'].items() if k!='input_rows'));v={'schema':'GDT327_VALIDATION_V1','status':'PASS','scope':'INDEPENDENT_SOURCE_ROW_IDS_CONTEXTS_ALL_POWERED_PROBABILITIES_ATLAS_GRAMMAR_HASHES','checks_passed':len(checks),'result_sha256':sha(RESULT),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
