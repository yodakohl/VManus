from pathlib import Path
import gzip,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());I={u:i for i,u in enumerate(U)}
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 correction=read(B/'artifacts/EXPLANATION_CORRECTION_20261011.json')
 for case in correction['cases']:
  pm,pq=case['m_port'],case['q_port'];options=[]
  for chars in __import__('itertools').product('mq',repeat=2):
   ports=tuple(pm if c=='m' else pq for c in chars);options.append((int(ports[0]%2!=ports[1]//2),ports,''.join(chars)))
  best=min(options);assert best[2]==case['canonical_two_body_output'] and best[0]==case['cost']
  assert [{'output':o,'cost':cost,'codes':list(codes)} for cost,codes,o in sorted(options)]==case['all_candidates']
 assert [c['canonical_two_body_output'] for c in correction['cases']]==['mm','qm']
 decisions=read(B/'artifacts/DECISIONS.json.gz');data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');out={}
 for ed,table in decisions.items():
  witness=next(w for w in table['witnesses'] if w['pair']==['m','q'] and w['pair_ports']==[0,1]);bits=witness['bits'];high={u for u in U if bits[2*I[u]]};assert not high.intersection(('m','q'));fail=[];checked=0
  for r in data[ed]:
   u=r['units'];body=['MQ' if x in ('m','q') else x for x in u];written=[('q' if i+1<len(body) and body[i+1] in high else 'm') if x=='MQ' else x for i,x in enumerate(body)];assert ['MQ' if x in ('m','q') else x for x in written]==body;checked+=1
   if written!=u:fail.append({'id':r['id'],'original':r['ivtff_group_raw'],'canonical':''.join(written)})
  assert len(fail)==1 and fail[0]['original']=='aman' and fail[0]['canonical']=='aqan'
  pairs={tuple(w['pair']) for w in table['witnesses']};assert pairs and all('m' in pair for pair in pairs)
  assert all(set(a)&set(b) for a,b in __import__('itertools').combinations(pairs,2))
  residual_ids={w['residual']['id'] for w in table['witnesses']};assert len(residual_ids)==1
  assert {u for r in data[ed] if r['id'] not in residual_ids for u in r['units']}==set(U)
  out[ed]={'hypothetical_common_body':'MQ (opaque body identifier, not a sound or meaning)','write_q_before':sorted(high),'write_m':'before every other body and at word end','other20bodies':'identity drawings','original_occurrences_checked':checked,'unmodified_residuals':fail,'scope':'Post-result algebraic simplification of saved m00/q01 witness; not a new fitted model.','post_result_star_graph_inference':{'all22units_remain':True,'feasible_pairs':[list(p) for p in sorted(pairs)],'observed_body_classes_for_every_nontrivial_one_residual_writer':21,'reason':'Every class must be a clique in the complete feasible-pair star; no triple clique or two disjoint edges. Thus exactly one pair can be merged.','maximum_minority_mass_over_all_such_partitions':max((w['minority_mass'] for w in table['witnesses']),key=lambda x:x[0])}}
 profiles={p['form']:p['editions'] for p in read(B/'artifacts/POSTRESULT_PROFILES.json')['profiles']}
 for ed in data:
  assert profiles['aman'][ed]['count']==profiles['q'][ed]['count']==1 and profiles['m'][ed]['count']>0
  assert next(x['count'] for x in profiles['q'][ed]['strata']['kind'] if x['value']=='L')==1
  assert next(x['count'] for x in profiles['q'][ed]['strata']['kind'] if x['value']=='P')==0
  assert next(x['count'] for x in profiles['m'][ed]['strata']['kind'] if x['value']=='P')==profiles['m'][ed]['count']
 (B/'artifacts/SIMPLIFIED_WITNESSES.json').write_text(json.dumps({'status':'PASS','readers':out,'broader_singleton_scope':'Both standalone m prose and q label occur; unchanged free-edge deterministic one-body spelling cannot produce both.'},indent=2,sort_keys=True)+'\n');print('PASS: closed-form replay and post-result singleton scope check')
if __name__=='__main__':main()
