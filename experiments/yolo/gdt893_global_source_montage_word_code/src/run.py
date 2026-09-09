#!/usr/bin/env python3
"""Complete-paragraph source discovery under one global word bijection."""
import argparse,csv,gzip,hashlib,json,re,subprocess,time
from collections import Counter
from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE.parents[2]
EDITIONS=('ZL3b','IT2a','RF1b','CONSENSUS')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,o):
 raw=json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 Path(p).write_bytes(gzip.compress(raw,mtime=0) if str(p).endswith('.gz') else raw)
def records(path,rows,ids):
 with Path(path).open('w') as f:
  f.write(str(len(rows))+'\n')
  for r in rows:f.write(r['id']+' '+str(len(r['words']))+' '+' '.join(str(ids[w]) for w in r['words'])+'\n')
def prepare(source_path,out):
 lock=json.loads((BASE/'artifacts/INPUT_LOCK.json').read_text())
 assert sha(source_path)==lock['source_units_sha256'],'source changed'
 target_path=ROOT/lock['target_cache_path']
 assert sha(target_path)==lock['target_cache_sha256'],'target cache changed'
 units=json.loads(Path(source_path).read_text())['units']
 assert len(units)==lock['source_units']
 assert sum(len(r['words']) for r in units)==lock['source_tokens']
 panels={e:[] for e in EDITIONS};intake=Counter()
 for f in json.loads(target_path.read_text())['frames']:
  leaf=f['physical_folio'];assert re.fullmatch('f[0-9]+',leaf)
  assert not f['page'].startswith('f84'),'sealed cache row'
  # Consult metadata before any body/reading field; only odd packet reaches fit.
  if int(leaf[1:])%2==0:intake['even_frames_not_sent_to_fitter']+=1;continue
  intake['odd_frames']+=1
  for e in EDITIONS:
   r=f['readings'][e]
   if not r['eligible']:intake[e+'_ineligible']+=1;continue
   g=r['groups'];assert g and all(x['kind']=='P' and re.fullmatch('[a-z]+',x['raw']) for x in g)
   panels[e].append({'id':f['paragraph_id'],'page':f['page'],'physical_folio':leaf,'words':[x['raw'] for x in g],'source_group_ids':[x['source_group_id'] for x in g]})
 sw=sorted({w for r in units for w in r['words']});cw=sorted({w for rows in panels.values() for r in rows for w in r['words']})
 si={w:i for i,w in enumerate(sw)};ci={w:i for i,w in enumerate(cw)}
 records(out/'SOURCE_RECORDS.txt',units,si)
 for e,rows in panels.items():records(out/(e+'_TARGET.txt'),rows,ci)
 packet={'schema':'GDT893_ODD_ONLY_FIT_PACKET_V1','panels':panels,'source_words':sw,'cipher_words':cw,'source_units':[{'id':u['id'],'source':u['source'],'word_ids':[si[w] for w in u['words']]} for u in units],'input_lock':lock,'intake':dict(intake)}
 write_json(out/'FIT_PACKET.json.gz',packet);return packet

def candidate_rows(packet,e,path,deadline):
 targets=packet['panels'][e];ci={w:i for i,w in enumerate(packet['cipher_words'])};unique={};count=0
 with Path(path).open() as f:
  for r in csv.DictReader(f):
   if time.monotonic()>deadline:return list(unique.values()),count,False
   t,s,start,n=(int(r[k]) for k in ('target_index','source_index','start','length'))
   target,unit=targets[t],packet['source_units'][s];assert n==len(target['words'])
   plain=unit['word_ids'][start:start+n];assert len(plain)==n
   mapping={};reverse={}
   for w,v in zip(target['words'],plain):
    c=ci[w];assert c not in mapping or mapping[c]==v;assert v not in reverse or reverse[v]==c
    mapping[c]=v;reverse[v]=c
   key=(target['id'],tuple(sorted(mapping.items())))
   if key not in unique:unique[key]={'paragraph':target['id'],'target_index':t,'weight':n,'mapping':mapping,'plain_word_ids':plain,'provenance':[]}
   unique[key]['provenance'].append({'unit':unit['id'],'source':unit['source'],'start':start,'length':n});count+=1
 return list(unique.values()),count,True

def projections(candidates,solutions,targets):
 if not solutions:return {'forced_paragraphs':[],'forced_word_values':[]}
 maps=[];selected=[]
 for solution in solutions:
  m={};s={}
  for i in solution:m.update(candidates[i]['mapping']);s[candidates[i]['paragraph']]=candidates[i]['plain_word_ids']
  maps.append(m);selected.append(s)
 forced=[]
 for t in targets:
  values=[s.get(t['id']) for s in selected]
  if values[0] is not None and all(v==values[0] for v in values):forced.append({'paragraph':t['id'],'plain_word_ids':values[0]})
 common=[{'cipher_word_id':k,'source_word_id':v} for k,v in sorted(maps[0].items()) if all(m.get(k)==v for m in maps)]
 return {'forced_paragraphs':forced,'forced_word_values':common}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-units',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--budget-seconds',type=float,default=1800);a=p.parse_args()
 from optimize import solve
 out=a.output_dir;out.mkdir(parents=True,exist_ok=True);assert not (out/'RESULT.json').exists(),'refusing overwrite'
 started=time.monotonic();deadline=started+a.budget_seconds;packet=prepare(a.source_units,out)
 binary=out/'match';subprocess.run(['g++','-O3','-std=c++17','-fopenmp',str(BASE/'src/match.cpp'),'-o',str(binary)],check=True)
 results={}
 for e in EDITIONS:
  remaining=deadline-time.monotonic()
  if remaining<=0:results[e]={'status':'UNKNOWN_BUDGET','stage':'NOT_STARTED'};continue
  matches=out/(e+'_MATCHES.csv')
  try:r=subprocess.run([str(binary),str(out/(e+'_TARGET.txt')),str(out/'SOURCE_RECORDS.txt'),str(matches)],capture_output=True,text=True,timeout=remaining,check=True)
  except subprocess.TimeoutExpired:results[e]={'status':'UNKNOWN_BUDGET','stage':'WINDOW_ENUMERATION'};continue
  enumeration=json.loads(r.stdout);candidates,count,complete=candidate_rows(packet,e,matches,deadline)
  fit=solve(candidates,deadline) if complete else {'status':'UNKNOWN_BUDGET','stage':'CANDIDATE_MATERIALIZATION'}
  payload={'edition':e,'enumeration':enumeration,'raw_matches':count,'candidate_materialization_complete':complete,'candidates':candidates,'optimization':fit}
  if complete and fit['status']=='COMPLETE':payload['projection']=projections(candidates,fit['optimal_solutions'],packet['panels'][e])
  write_json(out/(e+'_FIT.json.gz'),payload)
  summary={'status':fit['status'],'paragraphs':len(packet['panels'][e]),'eligible_words':sum(len(r['words']) for r in packet['panels'][e]),'source_windows_matching':enumeration['matches'],'distinct_candidates':len(candidates),'best_weight':fit.get('best_weight'),'optimal_sets':len(fit.get('optimal_solutions',[])) if fit['status']=='COMPLETE' else None,'forced_paragraphs':len(payload.get('projection',{}).get('forced_paragraphs',[])) if fit['status']=='COMPLETE' else None}
  results[e]=summary;print(json.dumps({'edition':e,**summary}),flush=True);write_json(out/'PROGRESS.json',results)
 source_hashes={str((BASE/'src'/name).relative_to(ROOT)):sha(BASE/'src'/name) for name in ('run.py','source.py','optimize.py','match.cpp','SPEC.json')}
 answer={'status':'COMPLETE' if all(x['status']=='COMPLETE' for x in results.values()) else 'UNKNOWN_BUDGET','schema':'GDT893_GLOBAL_MONTAGE_RESULT_V1','panels':results,'elapsed_seconds':time.monotonic()-started,'input_lock':packet['input_lock'],'fit_packet_sha256':sha(out/'FIT_PACKET.json.gz'),'source_hashes':source_hashes,'held_folio_fit':False,'interpretation':'Exploratory source-pool-relative fit, not confirmed meaning or significance.'}
 write_json(out/'RESULT.json',answer);print(json.dumps(results),flush=True)
if __name__=='__main__':main()
