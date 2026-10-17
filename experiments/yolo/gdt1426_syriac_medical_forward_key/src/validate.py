#!/usr/bin/env python3
"""Independent old finite-choice SMT and static full-certificate replay."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,p):
 sp=importlib.util.spec_from_file_location(name,ROOT/p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def save(n,x,replace=False):
 p=A/n
 if not replace:assert not p.exists(),str(p)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def configuration():
 s=read(E/'src/SPEC.json')
 for p,h in read(E/'LOCK.json')['files'].items():assert sha(ROOT/p)==h,p
 return s
def source():
 p=read(A/'SOURCE_PROJECTION.json');W=p['words'];edges={tuple(x) for x in p['edges']};assert W==sorted(set(W));return p,W,edges

def check(result,groups,W,edges,signs):
 words=result.get('words',result.get('source_words'));key=result['key'];assert len(words)==len(groups)
 assert set(key)==set(''.join(W)) and all(v in signs for v in key.values())
 assert all(w in W for w in words) and all(p in edges for p in zip(words,words[1:]))
 assert [[key[c] for c in w] for w in words]==groups
 return {'status':'PASS','word_count':len(words),'letter_count':sum(map(len,words)),'all_words_edges_and_letter_values_checked':True}
def smt():return module('gdt1426_old_smt','experiments/yolo/gdt1420_forward_merger_shared_key/src/validate.py')
def gate():
 s=configuration();src,W,edges=source();inp=read(A/'CONTROL_INPUT.json');a=read(A/'CONTROL_PRIMARY.json');old=smt();fixtures=old.controls();rs=src['records'];idx=next(i for i,r in enumerate(rs) if len(r['words'])>=32);words=rs[idx]['words'][:32]
 key={c:s['signs'][j%s['control_mapping_modulo']] for j,c in enumerate(sorted(set(''.join(W))))};groups=[[key[c] for c in w] for w in words]
 assert idx==inp['source_record_index'] and words==inp['planted_words'] and key==inp['planted_key'] and groups==inp['groups']
 planted=check({'words':words,'key':key},groups,W,edges,s['signs']);t=time.monotonic();r=old.solve(groups,W,edges,s['signs'],s['independent_seconds']);elapsed=time.monotonic()-t
 certs=[{'engine':'planted',**planted}]
 if a['status']=='SAT':certs.append({'engine':'primary',**check(a['result'],groups,W,edges,s['signs'])})
 if r['status']=='SAT':certs.append({'engine':'independent',**check(r,groups,W,edges,s['signs'])})
 status='PASS' if a['status']==r['status']=='SAT' else 'CONTROL_UNKNOWN_STOP'
 if a['status']=='UNSAT' or r['status']=='UNSAT':status='INVALID_PLANTED_CONTROL_UNSAT_STOP'
 save('INDEPENDENT_CONTROL.json',{'status':r['status'],'result':r,'elapsed_seconds':elapsed,'source_free_controls':fixtures})
 save('GATE_VALIDATION.json',{'status':status,'certificates':certs,'both_any_keys_verified':status=='PASS','planted_source_word_recovery_diagnostic':{'primary':a.get('result',{}).get('source_words')==words,'independent':r.get('words')==words},'uniqueness_tested':False,'native_cases_executed':0});print(json.dumps({'gate':status,'independent_control':r['status'],'elapsed_seconds':elapsed}),flush=True)
def native():
 s=configuration();assert read(A/'GATE_VALIDATION.json')['status']=='PASS';src,W,edges=source();p=read(A/'NATIVE_INPUT.json');t=time.monotonic();r=smt().solve(p['groups'],W,edges,s['signs'],s['independent_seconds']);elapsed=time.monotonic()-t
 if r['status']=='SAT':check(r,p['groups'],W,edges,s['signs'])
 save('INDEPENDENT_RESULT.json',{'experiment_id':'GDT1426','status':r['status'],'result':r,'elapsed_seconds':elapsed});print(json.dumps({'independent_native':r['status'],'elapsed_seconds':elapsed}),flush=True)
def static():
 s=configuration();src,W,edges=source();c=read(A/'CONTROL_INPUT.json');g=read(A/'GATE_VALIDATION.json');check({'words':c['planted_words'],'key':c['planted_key']},c['groups'],W,edges,s['signs']);cp=read(A/'CONTROL_PRIMARY.json');ci=read(A/'INDEPENDENT_CONTROL.json')
 for r in [cp,ci]:
  if r['status']=='SAT':check(r['result'],c['groups'],W,edges,s['signs'])
 assert (g['status']=='PASS')==(cp['status']==ci['status']=='SAT')
 p=read(A/'NATIVE_INPUT.json');assert len(p['groups'])==59 and [''.join(v) for v in p['groups']]==p['raw_groups']
 certificates=[]
 if g['status']!='PASS':
  assert not (A/'RESULT.json').exists() and not (A/'INDEPENDENT_RESULT.json').exists();assert read(A/'NATIVE_STOP.json')['native_cases_executed']==0;status='CONTROL_STOP_NO_NATIVE_TEST';n=0
 else:
  a=read(A/'RESULT.json');b=read(A/'INDEPENDENT_RESULT.json');statuses=[a['status'],b['status']]
  assert set(statuses)!={'SAT','UNSAT'},'INVALID_DISAGREEMENT'
  for engine,r in zip(['primary','independent'],[a,b]):
   if r['status']=='SAT':certificates.append({'engine':engine,**check(r['result'],p['groups'],W,edges,s['signs'])})
  status='SAT_CAPACITY_UNASSESSED' if certificates else 'DUAL_UNSAT_FIXED_SOURCE_CHANNEL' if statuses==['UNSAT','UNSAT'] else 'UNKNOWN_OPEN';n=1
 result={'experiment_id':'GDT1426','status':status,'native_cases_executed':n,'groups':59,'certificates':certificates,'confirmed_words':0,'claim_ceiling':s['claim_ceiling'],'lock_sha256':sha(E/'LOCK.json')}
 save('FINAL_DECISION.json',result,True);save('VALIDATION.json',{'status':'PASS_STATIC_CERTIFICATE_AND_GATE_REPLAY','final_decision':status,'native_cases_executed':n,'source_validation_status':read(A/'SOURCE_VALIDATION.json')['status'],'no_solver_called':True,'confirmed_words':0},True);print(json.dumps(result),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--gate',action='store_true');p.add_argument('--native',action='store_true');p.add_argument('--validate',action='store_true');a=p.parse_args()
 if a.gate:gate()
 elif a.native:native()
 elif a.validate:static()
 else:p.error('choose one phase')
if __name__=='__main__':main()
