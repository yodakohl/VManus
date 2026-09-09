#!/usr/bin/env python3
"""Exact maximum and universal projection over the frozen candidate pools."""
import argparse,gzip,json,subprocess,time
from pathlib import Path
from run import BASE,ROOT,sha,write_json

# Execution order and individual caps change computation, never scientific scope.
ORDER=(('ZL3b',90),('RF1b',360),('CONSENSUS',90),('IT2a',900))

def projection(candidates,fit):
 if fit['status']!='COMPLETE':return None
 return {
  'forced_paragraphs':[{'candidate_index':i,'paragraph':candidates[i]['paragraph'],
   'plain_word_ids':candidates[i]['plain_word_ids'],'provenance':candidates[i]['provenance']}
   for i in fit['forced_candidate_indices']],
  'forced_word_values':[{'cipher_word_id':k,'source_word_id':v} for k,v in fit['forced_word_values']]}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--fit-dir',type=Path,required=True)
 p.add_argument('--budget-seconds',type=float,default=1500)
 a=p.parse_args();out=a.fit_dir
 assert not (out/'RESULT.json').exists(),'refusing overwrite'
 lock=json.loads((BASE/'artifacts/CANDIDATE_LOCK.json').read_text())
 assert sha(out/'FIT_PACKET.json.gz')==lock['fit_packet_sha256']
 for name,digest in lock['files'].items():assert sha(out/name)==digest,name+' changed'
 packet=json.loads(gzip.decompress((out/'FIT_PACKET.json.gz').read_bytes()))
 binary=out/'solve_projection'
 subprocess.run(['g++','-std=c++17','-O3','-DNDEBUG',str(BASE/'src/solve_projection.cpp'),'-o',str(binary)],check=True)
 started=time.monotonic();deadline=started+a.budget_seconds;results={}
 for e,cap in ORDER:
  remaining=min(cap,deadline-time.monotonic())
  if remaining<=0:results[e]={'status':'UNKNOWN_BUDGET','stage':'NOT_STARTED'};continue
  optpath=out/(e+'_SYMBOLIC.json');assert not optpath.exists(),'refusing overwrite'
  subprocess.run([str(binary),str(out/(e+'_OPT_INPUT.txt')),str(optpath),str(remaining)],check=True)
  fit=json.loads(optpath.read_text())
  payload=json.loads(gzip.decompress((out/(e+'_CANDIDATES.json.gz')).read_bytes()))
  proj=projection(payload['candidates'],fit)
  record={'edition':e,'optimization':fit,'projection':proj,
   'candidate_file':e+'_CANDIDATES.json.gz','candidate_sha256':lock['files'][e+'_CANDIDATES.json.gz'],
   'constraint_file':e+'_OPT_INPUT.txt','constraint_sha256':lock['files'][e+'_OPT_INPUT.txt'],
   'family_representation':'All feasible frozen candidate sets at the proved maximum; implicit, cardinality not enumerated.'}
  write_json(out/(e+'_FIT.json.gz'),record)
  summary={'status':fit['status'],'paragraphs':len(packet['panels'][e]),
   'eligible_words':sum(len(r['words']) for r in packet['panels'][e]),
   'source_windows_matching':payload['enumeration']['matches'],'distinct_candidates':len(payload['candidates']),
   'best_weight':fit['best_weight'],'best_weight_is_proven':fit['stats']['best_weight_is_proven'],
   'optimal_sets':None,'optimal_family_retained_implicitly':fit['stats']['best_weight_is_proven'],
   'forced_paragraphs':len(proj['forced_paragraphs']) if proj is not None else None,
   'forced_word_values':len(proj['forced_word_values']) if proj is not None else None}
  results[e]=summary;print(json.dumps({'edition':e,**summary}),flush=True)
  write_json(out/'PROGRESS.json',results);del payload,fit
 names=('run.py','prepare_cpp.py','run_cpp.py','source.py','solve_projection.cpp','match.cpp','SPEC.json')
 source_hashes={str((BASE/'src'/name).relative_to(ROOT)):sha(BASE/'src'/name) for name in names}
 result={'status':'COMPLETE' if all(x['status']=='COMPLETE' for x in results.values()) else 'PARTIAL_UNKNOWN_BUDGET',
  'schema':'GDT893_GLOBAL_MONTAGE_SYMBOLIC_RESULT_V1','panels':results,
  'elapsed_seconds':time.monotonic()-started,'input_lock':packet['input_lock'],
  'candidate_lock':lock,'fit_packet_sha256':sha(out/'FIT_PACKET.json.gz'),'source_hashes':source_hashes,
  'held_folio_fit':False,'interpretation':'Exploratory source-pool-relative fit, not confirmed meaning or significance.'}
 write_json(out/'RESULT.json',result)

if __name__=='__main__':main()
