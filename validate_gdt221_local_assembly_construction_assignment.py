#!/usr/bin/env python3
"""Independent retained-output validator for GDT221."""
import csv,hashlib,itertools,json
from pathlib import Path
R=Path(__file__).resolve().parent
def read(n):
 with (R/n).open(encoding='utf8',newline='')as h:return list(csv.DictReader(h,delimiter='\t'))
def sha(n):return hashlib.sha256((R/n).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def main():
 res=json.loads((R/'gdt221_result.json').read_text());scores=read('gdt221_assembly_scores.tsv');retr=read('gdt221_label_retrieval.tsv');counter=read('gdt221_counterexamples.tsv');checks=[]
 def ck(n,v):checks.append(n);assert v,n
 ck('score_rows',len(scores)==12);ck('retrieval_rows',len(retr)==168);ck('counter_rows',len(counter)==5)
 ck('no_f84',not any('f84' in json.dumps(x) for x in scores+retr))
 primary=[r for r in scores if r['scope']=='COMPLETE_LINES_PRIMARY'];ck('primary_six',len(primary)==6)
 leads={rep:{r['page']:float(r['correct_assignment_lead']) for r in primary if r['representation']==rep} for rep in res['representations']}
 worlds=list(itertools.product((1,-1),repeat=2))
 for rep in res['representations']:
  vals=[sum(w[i]*leads[rep][p] for i,p in enumerate(('f75v','f83r'))) for w in worlds];obs=vals[0]
  ck('lead_'+rep,abs(obs-res['primary'][rep]['aggregate_lead'])<1e-11)
  ck('localp_'+rep,abs(sum(v>=obs-1e-12 for v in vals)/4-res['primary'][rep]['local_exact_p'])<1e-12)
  ck('f75_positive_'+rep,leads[rep]['f75v']>0);ck('f83_negative_'+rep,leads[rep]['f83r']<0)
 for rep in res['representations']:
  rows=[r for r in retr if r['scope']=='COMPLETE_LINES_PRIMARY' and r['representation']==rep]
  ck('retr_n_'+rep,len(rows)==28)
  ck('retr_correct_'+rep,sum(int(r['correct']) for r in rows)==res['individual_retrieval'][rep]['correct'])
  ck('retr_below_majority_'+rep,res['individual_retrieval'][rep]['correct']<res['individual_retrieval_majority_top_correct'])
 ck('majority_top',res['individual_retrieval_majority_top_correct']==20)
 ck('status',res['status']=='LOCAL_ASSEMBLY_CONSTRUCTION_NOT_TRANSFERABLE')
 ck('content_hash',res['result_content_sha256']==csha({k:v for k,v in res.items() if k!='result_content_sha256'}))
 for group in ('inputs','outputs','documents','implementation'):
  for n,d in res[group].items():ck('hash_'+n,sha(n)==d)
 ck('f84_flags',not any(res['f84'].values()))
 out={'schema':'GDT221_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_failed':0,'result_sha256':sha('gdt221_result.json'),'checks':checks};(R/'gdt221_validation.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')
if __name__=='__main__':main()
