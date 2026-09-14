#!/usr/bin/env python3
"""Descriptive admitted-source inventory and explicitly conditional arithmetic."""
import collections,hashlib,json,math,re
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parents[2]
BASE='experiments/yolo/gdt947_ol_content_reference_direction/'
def load(p):return json.loads((R/p).read_text())
def build():
 lock=load(BASE+'PREREG_LOCK.json')
 model_path=BASE+'src/MODEL.json'
 assert hashlib.sha256((R/model_path).read_bytes()).hexdigest()==lock['files'][model_path]
 m=load(model_path)
 for p in [m['allow_source']]+m['sources']:
  assert hashlib.sha256((R/p).read_bytes()).hexdigest()==lock['files'][p],p
 allow=set(load(m['allow_source'])['allowed_selectors'])
 assert len(allow)==179 and not any(p.startswith('f84') or p=='f116v' for p in allow)
 out={}
 for ed in ['ZL3b','IT2a','RF1b']:
  words=[];prose=[];simple=[];definite=[];sources=[];pages=set();ids=set()
  for p in m['sources']:
   if not p.endswith('_'+ed+'.json'):continue
   sources.append({'path':p,'sha256':lock['files'][p]});d=load(p)
   for line in d['lines']:
    meta=line['metadata'];assert meta['page'] in allow and meta['edition']==ed;pages.add(meta['page'])
    for g in line['groups']:
     r=dict(zip(d['group_columns'],g));sid=r['source_group_id'];assert sid not in ids;ids.add(sid)
     w=r['ivtff_group_raw'];words.append(w)
     if meta['kind']=='P':prose.append(w)
     if re.fullmatch('[a-z]+',w):
      simple.append(w)
      if r['left_separator'] in ['DEFINITE_SPACE','LINE_START','LINE_END'] and r['right_separator'] in ['DEFINITE_SPACE','LINE_START','LINE_END']:definite.append(w)
  c=collections.Counter(simple);cum=0
  cover={str(k):sum(n for _,n in c.most_common(k))/len(simple) for k in [10,20,50,100,200,500,1000]}
  for k50,(_,n) in enumerate(c.most_common(),1):
   cum+=n
   if cum*2>=len(simple):break
  out[ed]={'raw_groups':len(words),'raw_distinct':len(set(words)),'prose_groups':len(prose),'prose_distinct':len(set(prose)),'alphabetic_groups':len(simple),'alphabetic_distinct':len(c),'alphabetic_hapax_types':sum(n==1 for n in c.values()),'definitely_bounded_alphabetic_groups':len(definite),'definitely_bounded_alphabetic_distinct':len(set(definite)),'top_type_token_coverage':cover,'types_for_50_percent_alphabetic_tokens':k50,'page_selectors':len(pages),'inputs':sources}
 assert sum(c['raw_groups'] for c in out.values())==96184 # source inventory checksum, not independent evidence
 math_cases={str(n):{'log10_factorial':math.lgamma(n+1)/math.log(10),'ideal_balanced_binary_answers':math.ceil(math.lgamma(n+1)/math.log(2))} for n in [10,20,30,50,100,1000,8000,9000,10000]}
 local=[]
 for k in [6,8,10]:
  n=3**k*2**4
  local.append({'semantic_slots':k,'values_each':3,'binary_rule_choices':4,'cartesian_candidates':n,'expected_position_one_correct_uniform_without_replacement':(n+1)/2})
 return {'status':'DESCRIPTIVE_INVENTORY_AND_CONDITIONAL_ARITHMETIC','scope':'already exposed179-selector GDT915 snapshots, alternate transcriptions not independent; raw types are not lemmas; alphabetic filter is not a claim of reliable text','counts':out,'factorial_scenarios':math_cases,'local_scenarios':local,'role_partition_example':{'assumption':'20forms and20known meanings independently assigned to four compatible classes of5, bijection only','before':math.factorial(20),'after':math.factorial(5)**4},'expectation_assumptions':['correct model present in the finite family','exactly one correct model and uniformly random ordering for stated expectation','correctness is recognizable; no attempt duration inferred'],'estimated_actual_trials_to_translation':None,'confirmed_words':0,'new_admissions':0,'source_bindings':{'model':model_path,'model_sha256':lock['files'][model_path]}}
if __name__=='__main__':
 result=build();(E/'COUNTS.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'editions':{ed:{k:c[k] for k in ['raw_groups','raw_distinct','types_for_50_percent_alphabetic_tokens']} for ed,c in result['counts'].items()},'local_cartesian_counts':[s['cartesian_candidates'] for s in result['local_scenarios']]}))
