#!/usr/bin/env python3
"""Independent validation of GDT168 truth, blind firewall, and central scores."""
from __future__ import annotations
import ast,csv,gzip,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

R=Path(__file__).resolve().parent
BLIND=R/'gdt168_blind_synthetic_corpora.json.gz';TRUTH=R/'gdt168_synthetic_ground_truth.json.gz';CODE=R/'gdt168_codebook_truth.tsv';FREEZE=R/'gdt168_source_encoder_freeze.json';BR=R/'gdt168_blind_result.json';BS=R/'gdt168_blind_diagnostic_summary.tsv';BC=R/'gdt168_blind_context_scores.tsv';RESULT=R/'gdt168_result.json';INFO=R/'gdt168_ground_truth_information.tsv';DEC=R/'gdt168_ground_truth_decoder.tsv';REC=R/'gdt168_diagnostic_recovery_matrix.tsv';COUNTER=R/'gdt168_counterexamples.tsv';REPORT=R/'GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_REPORT.md';METHOD=R/'GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_METHOD.md';SCORER=R/'run_gdt168_blind_diagnostics.py';UNBLIND=R/'unblind_gdt168_synthetic_calibration.py';VALID=R/'gdt168_validation.json'
ALPHA,BETA=16.,8.
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def close(a,b,t=5e-9):a=float(a);b=float(b);return abs(a-b)<=t*max(1.,abs(a),abs(b))
def tsv(p):
 with Path(p).open(encoding='utf8',newline='')as h:return list(csv.DictReader(h,delimiter='\t'))
class C:
 def __init__(self):self.rows=[]
 def add(self,n,p,d=''):
  self.rows.append({'name':n,'passed':bool(p),'detail':str(d)})
  if not p:raise AssertionError(f'{n}:{d}')
def entropy(c):
 n=sum(c.values());return -sum(x/n*math.log2(x/n)for x in c.values()if x)if n else 0.
def compiler(x):return(x['wrapper'],x['local_frame'],x['right_family'],x['closure_value'],int(x['dy_closure']),int(x['b3']))
def reps():return{'PAGE_HOST':lambda x:x['page_host'],'COMPILER_ONLY':compiler,'PAGE_HOST_PLUS_SLOT':lambda x:(x['page_host'],int(x['slot'])),'FULL_TUPLE_PLUS_SLOT':lambda x:(x['page_host'],compiler(x),int(x['slot'])),'RAW_SURFACE':lambda x:x['surface']}
def information(rows,key):
 c=Counter(int(x['concept_index'])for x in rows);groups=defaultdict(Counter)
 for x in rows:groups[key(x)][int(x['concept_index'])]+=1
 h=entropy(c);cond=sum(sum(v.values())/len(rows)*entropy(v)for v in groups.values());return h,cond,h-cond,(h-cond)/h
def decoder(rows,key):
 units=sorted({x['source_unit_id']for x in rows});total=covered=correct=positive=0
 for held in units:
  maps=defaultdict(Counter)
  for x in rows:
   if x['source_unit_id']!=held:maps[key(x)][int(x['concept_index'])]+=1
  fc=0
  for x in rows:
   if x['source_unit_id']!=held:continue
   total+=1;k=key(x)
   if k in maps:
    covered+=1;pred=sorted(maps[k].items(),key=lambda y:(-y[1],y[0]))[0][0];correct+=pred==int(x['concept_index']);fc+=pred==int(x['concept_index'])
  positive+=fc>0
 return covered,correct,total,covered/total,correct/covered if covered else 0.,positive,len(units)
def lines(rows):
 z=defaultdict(list)
 for x in rows:z[x['line_id']].append(x)
 for x in z.values():x.sort(key=lambda y:int(y['position_in_line']))
 return z
def observations(rows,mode):
 if mode=='COMPILER':return[(x,'|'.join(map(str,compiler(x))),1.)for x in rows]
 out=[]
 for line in lines(rows).values():
  bag=Counter(x['page_host']for x in line)
  for i,x in enumerate(line):
   if mode=='NEXT_HOST':
    if i+1<len(line):out.append((x,line[i+1]['page_host'],1.))
   else:
    vals=Counter(line[j]['page_host']for j in range(max(0,i-2),min(len(line),i+3))if j!=i)if mode=='WINDOW_PM2'else bag.copy()
    if mode=='WHOLE_LINE':
     vals[x['page_host']]-=1
     if not vals[x['page_host']]:del vals[x['page_host']]
    n=sum(vals.values())
    for y,q in vals.items():out.append((x,y,q/n))
 return out
def gain(rows,mode):
 obs=observations(rows,mode);v={y for _,y,_ in obs};gt=Counter();gn=0.;nt=Counter();nn=Counter();ht=Counter();hn=Counter();ut=defaultdict(Counter);un=Counter();unt=defaultdict(Counter);unn=defaultdict(Counter);uht=defaultdict(Counter);uhn=defaultdict(Counter);unitgain=Counter()
 for x,y,w in obs:
  u=x['source_unit_id'];nk=(x['renderer'],int(x['position_in_line']),int(x['line_index']),min(18,int(x['record_length'])));h=x['page_host'];gt[y]+=w;gn+=w;nt[nk,y]+=w;nn[nk]+=w;ht[h,y]+=w;hn[h]+=w;ut[u][y]+=w;un[u]+=w;unt[u][nk,y]+=w;unn[u][nk]+=w;uht[u][h,y]+=w;uhn[u][h]+=w
 total=0.
 for x,y,w in obs:
  u=x['source_unit_id'];nk=(x['renderer'],int(x['position_in_line']),int(x['line_index']),min(18,int(x['record_length'])));h=x['page_host'];q=(gt[y]-ut[u][y]+.5)/(gn-un[u]+.5*len(v));b=(nt[nk,y]-unt[u][nk,y]+ALPHA*q)/(nn[nk]-unn[u][nk]+ALPHA);p=(ht[h,y]-uht[u][h,y]+BETA*b)/(hn[h]-uhn[u][h]+BETA);g=w*math.log2(p/b);total+=g;unitgain[u]+=g
 return len({x['blind_id']for x,_,_ in obs}),sum(w for _,_,w in obs),total,total/max(1,len({x['blind_id']for x,_,_ in obs})),sum(x>0 for x in unitgain.values()),len(unitgain)
def main():
 c=C();r=json.loads(RESULT.read_text());d=r.pop('result_content_sha256');c.add('result_content',csha(r)==d);r['result_content_sha256']=d
 for kind in('inputs','implementation','outputs','documents'):
  for name,digest in r[kind].items():c.add('hash:'+kind+':'+name,sha(R/name)==digest)
 b=json.load(gzip.open(BLIND,'rt',encoding='utf8'))['rows'];t=json.load(gzip.open(TRUTH,'rt',encoding='utf8'))['rows'];c.add('row_counts',len(b)==len(t)==240000);tm={x['blind_id']:x for x in t};c.add('truth_unique',len(tm)==240000)
 joined=[{**x,**tm[x['blind_id']]}for x in b];c.add('view_system_join',all((x['corpus_view']=='CONTROL_X')==(x['system']=='SYSTEM_A')for x in joined));c.add('no_voynich_locator_fields',not {'page','locus','physical_folio','voynich_page'}.intersection(b[0]))
 freeze=json.loads(FREEZE.read_text());c.add('no_voynich_input',freeze['f84r']['voynich_inputs']==0 and all(x is False for k,x in freeze['f84r'].items() if k!='voynich_inputs'));maps=freeze['renderer_keys'];cb={int(x['concept_index']):x for x in tsv(CODE)};c.add('codebook_types',len(cb)==6175)
 for x in joined:
  hm=maps[x['renderer']]['host'];expected=''.join(hm[z]for z in x['canonical_host']);
  if expected!=x['page_host']:raise AssertionError('render')
  if x['system']=='SYSTEM_B':
   u=(int(x['concept_index'])+137*int(x['slot']))%6175;re=int(x['wrapper_digit'])*100+int(x['right_digit'])*400+int(x['closure_digit'])*1600+(u%100)
   if re!=u:raise AssertionError('mixed radix')
 c.add('all_renderer_and_mixed_radix_rows',True,len(joined))
 prim={s:[x for x in joined if x['system']==s and x['renderer']=='R1_S1']for s in('SYSTEM_A','SYSTEM_B')};ei={(x['system'],x['representation']):x for x in tsv(INFO)};ed={(x['system'],x['representation']):x for x in tsv(DEC)}
 for s,rows in prim.items():
  for name,key in reps().items():
   vals=information(rows,key);c.add('info:'+s+':'+name,all(close(ei[s,name][f],v)for f,v in zip(('concept_entropy_bits','conditional_entropy_bits','mutual_information_bits','fraction_concept_entropy'),vals)))
   vals=decoder(rows,key);c.add('decoder:'+s+':'+name,(int(ed[s,name]['predictions']),int(ed[s,name]['correct']),int(ed[s,name]['total_rows']))==vals[:3]and all(close(ed[s,name][f],v)for f,v in zip(('coverage','accuracy_on_predictions'),vals[3:5])))
 c.add('truth_architecture',close(ei['SYSTEM_A','PAGE_HOST']['fraction_concept_entropy'],1)and close(ei['SYSTEM_B','FULL_TUPLE_PLUS_SLOT']['fraction_concept_entropy'],1)and float(ei['SYSTEM_B','PAGE_HOST']['fraction_concept_entropy'])<.5)
 exported={(x['view'],x['renderer'],x['mode']):x for x in tsv(BC)}
 by=defaultdict(list)
 for x in b:by[x['corpus_view'],x['renderer']].append(x)
 for v in('CONTROL_X','CONTROL_Y'):
  for renderer in sorted({x['renderer']for x in b}):
   rows=by[v,renderer]
   for mode in('COMPILER','NEXT_HOST','WINDOW_PM2','WHOLE_LINE'):
    vals=gain(rows,mode);got=exported[v,renderer,mode];c.add('context:'+v+':'+renderer+':'+mode,(int(got['events']),int(float(got['weighted_targets'])),int(got['positive_units']),int(got['units']))==(vals[0],int(vals[1]),vals[4],vals[5])and close(got['gain_bits'],vals[2])and close(got['gain_per_event'],vals[3]))
 br=json.loads(BR.read_text());c.add('blind_firewall',br['truth_files_read']==[]and br['forbidden_fields_seen']==[])
 source=SCORER.read_text();tree=ast.parse(source);c.add('scorer_no_truth_names','gdt168_synthetic_ground_truth'not in source and'gdt168_codebook_truth'not in source)
 c.add('recovery_rows',len(tsv(REC))==10);c.add('counter_rows',len(tsv(COUNTER))==5);c.add('decision',r['status']=='HOST_NEGATIVES_DO_NOT_DISTINGUISH_LEXICAL_FROM_DISTRIBUTED_CODE')
 c.add('f84_flags',all(x is False for x in r['f84r'].values()))
 out={'schema':'GDT168_SYNTHETIC_ARCHITECTURE_CALIBRATION_VALIDATION_V1','status':f'PASS_{len(c.rows)}_CHECK_INDEPENDENT_TRUTH_CONTEXT_AND_BINDING_RECONSTRUCTION','checks':len(c.rows),'check_manifest_sha256':csha(c.rows),'result_sha256':sha(RESULT),'validator_sha256':sha(Path(__file__)),'scope':'Independent encoder truth, information, held-unit decoders, all 80 context fits, hashes and blind firewall; algebra/substitution/alignment outputs are hash-bound rather than independently recomputed.','decision':r['status'],'f84r':r['f84r'],'claim_ceiling':r['claim_ceiling']};out['validation_content_sha256']=csha(out);VALID.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':out['status'],'decision':out['decision']},sort_keys=True))
if __name__=='__main__':main()
