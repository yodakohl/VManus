from pathlib import Path
import collections,gzip,hashlib,importlib.util,itertools,json,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1];R=B.parents[2]
spec=importlib.util.spec_from_file_location('old1334',R/'experiments/yolo/gdt1334_canonical_two_port_alias_capacity/src/run.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
U=old.U;I=old.I;TARGETS={'mol','damo','qokomo'}
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,x):(B/'artifacts'/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');edges=read(R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/EDGES.json.gz');prior=read(R/'experiments/yolo/gdt1337_two_port_single_discrepancy/artifacts/DECISIONS.json.gz');selected={};decisions={};summary={}
 for ed,rows in sorted(data.items()):
  selected[ed]=[r for r in edges[ed] if r['ivtff_group_raw'] in TARGETS];support={u:sum(u in r['units'] for r in rows) for u in U};gate=min(support.values())>=2;rec={'unit_group_support':support,'bridge_gate':gate,'pairs':[]};assert not ({r['id'] for r in rows}&{r['id'] for r in selected[ed]})
  if not gate:decisions[ed]=rec;summary[ed]={'status':'INCOMPLETE_SCOPE'};continue
  assert {w['residual']['ivtff_group_raw'] for w in prior[ed]['witnesses']}=={'aman'};removed=[r for r in rows if r['ivtff_group_raw']=='aman'];assert len(removed)==1
  accepted=[dict(r,cohort='strict') for r in rows if r['ivtff_group_raw']!='aman']+[dict(r,cohort='fixed_old_edge') for r in selected[ed]];words=sorted({tuple(r['units']) for r in accepted});ctx={u:{} for u in U}
  for r in sorted(accepted,key=lambda r:r['id']):
   w=r['units']
   for i,u in enumerate(w):ctx[u].setdefault((w[i-1] if i else 'BOS',w[i+1] if i+1<len(w) else 'EOS'),{'row':r,'index':i})
  pairs=sorted({tuple(w['pair']) for w in prior[ed]['witnesses']});rec['old_strict_residual']=removed[0]
  for pair in pairs:
   x,y=pair;cases=sorted({tuple(w['pair_ports']) for w in prior[ed]['witnesses'] if tuple(w['pair'])==pair});common=sorted(set(ctx[x])&set(ctx[y]));p={'pair':list(pair),'prior_port_cases':[list(c) for c in cases]}
   if common:
    c=common[0];wit=[ctx[u][c] for u in pair];assert any(w['row']['cohort']=='fixed_old_edge' for w in wit);p.update(status='ALL_PORTS_LITERAL_CONFLICT',context=list(c),witnesses=wit,port_cases=[])
   else:
    out=[];rs=old.runs(words,pair)
    for px,py in cases:
     clauses=old.clauses_for(rs,pair,px,py);bits=old.least_model(clauses,44);case={'pair_ports':[px,py],'clauses':[list(c) for c in clauses],'bits':bits,'status':'UNSAT' if bits is None else 'EXPANDED_SUBSET_WRITER'}
     if bits is not None:
      ports=[2*bits[2*i]+bits[2*i+1] for i in range(22)];assert all(old.render(w,pair,ports)==w for w in words);assert old.render(tuple(removed[0]['units']),pair,ports)!=tuple(removed[0]['units'])
     out.append(case)
    p.update(status='PAIR_EXCLUDED' if all(c['bits'] is None for c in out) else 'PAIR_REMAINS',port_cases=out)
   rec['pairs'].append(p)
  decisions[ed]=rec;summary[ed]={'strict_groups':len(rows),'selected_edge_occurrences':len(selected[ed]),'selected_counts':dict(sorted(collections.Counter(r['ivtff_group_raw'] for r in selected[ed]).items())),'minimum_strict_unit_group_support':min(support.values()),'prior_pairs':len(pairs),'prior_positive_port_cases':sum(len(p['prior_port_cases']) for p in rec['pairs']),'literal_conflict_pairs':sum(p['status']=='ALL_PORTS_LITERAL_CONFLICT' for p in rec['pairs']),'fallback_solver_cases':sum(len(p['port_cases']) for p in rec['pairs']),'status':'EXPANDED_SUBSET_RADIUS_AT_LEAST_TWO' if all(p['status']!='PAIR_REMAINS' for p in rec['pairs']) else 'EXPANDED_SUBSET_RADIUS_ONE'};print(ed,json.dumps(summary[ed]),flush=True)
 save('SELECTED_EDGES.json',selected);save('DECISIONS.json',decisions);save('RESULT.json',{'status':'FIXED_OLD_EDGE_COMPATIBILITY','readers':summary,'scope':'Old three-form countercases only; no new source/spelling, no error diagnosis, no exact radius2 or larger-budget search.'})
if __name__=='__main__':main()
