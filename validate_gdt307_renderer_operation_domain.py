#!/usr/bin/env python3
"""Validate GDT307 retained vectors, scores, decisions and hashes."""
import csv,hashlib,json,statistics
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;SOURCE=R/'gdt278_native_event_inventory.tsv';FROZEN=R/'gdt307_frozen_domain_cells.tsv';PAIR=R/'gdt307_pair_domain_vectors.tsv';CELL=R/'gdt307_host_domain_vectors.tsv';SCORES=R/'gdt307_domain_scores.tsv';RESULT=R/'gdt307_result.json';OUT=R/'gdt307_validation.json';Y=('FIRST','MIDDLE','LAST')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def role(x):
 i=int(x['group_index']);n=int(x['group_count']);return 'FIRST' if i==1 else 'LAST' if i==n else 'MIDDLE'
def delta(a,b):
 ca=Counter(role(x) for x in a);cb=Counter(role(x) for x in b);return tuple(cb[y]/len(b)-ca[y]/len(a) for y in Y)
checks=[]
def ck(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def close(a,b):return abs(float(a)-float(b))<5e-12
def sign(seed,w,test,cell):return 1 if int(hashlib.sha256(f'{seed}|{w}|{test}|{cell}'.encode()).hexdigest()[:16],16)&1 else -1
def main():
 frozen=read(FROZEN);wanted={(x['page_host'],x['source_surface_sha256']) for x in frozen}|{(x['page_host'],x['target_surface_sha256']) for x in frozen};events=defaultdict(list);f84=0
 with SOURCE.open(encoding='utf8',newline='') as h:
  for x in csv.DictReader(h,delimiter='\t'):
   if x['control_id']!='VOYNICH_REFERENCE':continue
   f84+=x['page'].startswith('f84') or x['locus'].startswith('f84');key=(x['page_host'],x['source_surface_sha256'])
   if key in wanted:events[key].append(x)
 ck('source_f84_zero',f84==0);pair={x['cell_id']:x for x in read(PAIR)};agg=defaultdict(list)
 for c in frozen:
  dt=c['domain_type'];held=c['held_domain'];a=events[(c['page_host'],c['source_surface_sha256'])];b=events[(c['page_host'],c['target_surface_sha256'])];tr=delta([x for x in a if x[dt]!=held],[x for x in b if x[dt]!=held]);he=delta([x for x in a if x[dt]==held],[x for x in b if x[dt]==held]);row=pair[c['cell_id']];ck('pair_vectors',all(close(row[f'train_delta_{Y[i].lower()}'],tr[i]) and close(row[f'held_delta_{Y[i].lower()}'],he[i]) for i in range(3)));agg[(c['operation'],dt,held,c['page_host'])].append((tr,he))
 ck('pair_inventory',set(pair)=={x['cell_id'] for x in frozen});cells={(x['operation'],x['domain_type'],x['held_domain'],x['page_host']):x for x in read(CELL)};dots=defaultdict(list);cell_dots={}
 for key,vals in agg.items():
  tr=tuple(statistics.mean(v[0][i] for v in vals) for i in range(3));he=tuple(statistics.mean(v[1][i] for v in vals) for i in range(3));dot=sum(x*y for x,y in zip(tr,he));row=cells[key];ck('host_domain_vectors',all(close(row[f'train_delta_{Y[i].lower()}'],tr[i]) and close(row[f'held_delta_{Y[i].lower()}'],he[i]) for i in range(3)) and close(row['train_held_dot'],dot));dots[key[:2]].append(dot);cell_dots[key]=dot
 scores={(x['operation'],x['domain_type']):x for x in read(SCORES)}
 for key,v in dots.items():ck('score_means',close(scores[key]['mean_train_held_dot'],statistics.mean(v)) and int(scores[key]['direction_correct_cells'])==sum(x>0 for x in v))
 d=json.loads((R/'gdt307_design.json').read_text());classes={}
 tests=sorted(dots);observed={key:statistics.mean(dots[key]) for key in tests};null={key:[] for key in tests}
 for world in range(d['null_worlds']):
  for key in tests:
   values=[]
   for cell_key,value in ((k,v) for k,v in cell_dots.items() if k[:2]==key):values.append(sign(d['null_seed'],world,'|'.join(key),'|'.join(cell_key))*value)
   null[key].append(statistics.mean(values))
 mu={key:statistics.mean(values) for key,values in null.items()};sd={key:statistics.pstdev(values) for key,values in null.items()};z={key:(observed[key]-mu[key])/sd[key] if sd[key] else 0 for key in tests};maxz=[max((null[key][world]-mu[key])/sd[key] if sd[key] else 0 for key in tests) for world in range(d['null_worlds'])]
 for key in tests:
  local=(1+sum(value>=observed[key]-1e-15 for value in null[key]))/(1+d['null_worlds']);maximum=(1+sum(value>=z[key]-1e-15 for value in maxz))/(1+d['null_worlds']);ck('null_scores',close(scores[key]['null_mean'],mu[key]) and close(scores[key]['null_sd'],sd[key]) and close(scores[key]['local_p'],local) and close(scores[key]['max12_p'],maximum))
 for op in d['operations']:
  a=scores[(op,'section')];b=scores[(op,'hand')];stable=float(a['mean_train_held_dot'])>0 and float(b['mean_train_held_dot'])>0 and float(a['direction_accuracy'])>=d['decision']['minimum_direction_accuracy'] and float(b['direction_accuracy'])>=d['decision']['minimum_direction_accuracy'] and min(float(a['max12_p']),float(b['max12_p']))<=d['decision']['max12_p_le'];classes[op]='DOMAIN_STABLE' if stable else 'DOMAIN_MIXED_OR_UNSTABLE'
 status='SELECTED_OPERATIONS_DOMAIN_STABLE' if all(v=='DOMAIN_STABLE' for v in classes.values()) else 'SELECTED_OPERATIONS_DOMAIN_MIXED';res=json.loads(RESULT.read_text());stored=res.pop('content_sha256');ck('content_hash',stored==can(res));ck('status_classes',res['status']==status and res['classifications']==classes);ck('input_hashes',all(res['inputs'][n]==sha(R/n) for n in res['inputs']));ck('output_hashes',all(res['outputs'][n]==sha(R/n) for n in res['outputs']));ck('document_hashes',all(res['documents'][n]==sha(R/n) for n in res['documents']));ck('implementation_hash',all(res['implementation'][n]==sha(R/n) for n in res['implementation']));ck('f84_flags',not any(res['f84'].values()));v={'schema':'GDT307_RENDERER_OPERATION_DOMAIN_STABILITY_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks':checks,'result_sha256':sha(RESULT),'reconstructed_status':status,'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'reconstructed_status':status},sort_keys=True))
if __name__=='__main__':main()
