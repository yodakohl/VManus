import gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
PH=['N','E','Q','D2','D1'];END=['a','ch','ckh','cth','d','e','f','i','k','l','m','n','o','p','r','s','sh','t','y'];SEL=['q','cph','cfh']
def gz(p):return json.loads(gzip.decompress((R/p).read_bytes()))
def matrices():
 M={s:[[False]*15 for _ in range(15)] for s in ['P','S0','S1','S2']}
 for b in range(3):
  n,e,q,d2,d1=[5*b+i for i in range(5)]
  for u,v in [(n,n),(e,n),(d2,d1),(d1,n)]:M['P'][u][v]=True
  M['S0'][n][q]=True;M['S0'][q][d2]=True
  for target in range(3):
   if target!=b:M['S'+str(target)][n][5*target+1]=True
 return M

def replay(symbols,initial):
 tables=matrices();v=[False]*15
 for phase,b in initial:v[5*b+PH.index(phase)]=True
 def state():return sorted([[PH[i%5],i//5] for i,x in enumerate(v) if x])
 out=[state()]
 for s in symbols:
  m=tables[s];v=[any(v[i] and m[i][j] for i in range(15)) for j in range(15)];out.append(state())
 return out

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 data=gz('experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');oldlines=json.loads((R/'experiments/yolo/gdt983_qo_reduplication_expansion/artifacts/SOURCE_LINES.json').read_text());oldpairs=json.loads((R/'experiments/yolo/gdt1274_shorter_reference_doublet_bound/artifacts/RESULT.json').read_text())['cases'];packet=json.loads((B/'artifacts/PACKET.json').read_text());res=json.loads((B/'artifacts/RESULT.json').read_text());nativeids=set();paths=0;rolecases=0
 for reader,p in packet.items():
  rows=data[reader];byid={r['id']:r for r in rows};byword={}
  for r in rows:byword.setdefault(tuple(r['units']),[]).append(r)
  nodes=gz('experiments/yolo/gdt1234_prefix_quotient_code_capacity/artifacts/CERTIFICATE_'+reader+'.json.gz')['nodes']
  assert [e['unit'] for e in p['ending_witnesses']]==END
  for e in p['ending_witnesses']:
   ids=e['ancestry'];assert nodes[ids[0]]['word']==[e['unit']]
   for a,b in zip(ids,ids[1:]):
    n=nodes[a];assert n['parents'][1]==b;prefix=nodes[n['parents'][0]]['word'];assert nodes[b]['word'][:len(prefix)]==prefix and nodes[b]['word'][len(prefix):]==n['word']
   leaf=nodes[ids[-1]];assert leaf['parents'] is None and e['leaf']==ids[-1] and e['units']==leaf['word'];assert leaf['word'][-1]==e['unit'] and ''.join(leaf['word'])==e['word']
   rr=byword[tuple(leaf['word'])];assert e['source_ids']==sorted(r['id'] for r in rr) and e['frequency']==len(rr) and e['pages']==sorted({r['page'] for r in rr})
   for r in rr:
    assert r['ivtff_group_raw']==e['word'] and r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
    assert not r['page'].startswith('f84') and r['page']!='f116v';nativeids.add(r['id'])
   paths+=1
  line=oldlines[reader+'|f75v.39'];assert p['qoqo_complete_line']==line
  matches=[g for g in line['groups'] if g['ivtff_group_raw']=='qoqokeey'];assert matches==[p['qoqo_group']]
  assert p['qoqo_units']==list('qoqokeey') and matches[0]['source_group_index']=='1';assert line['metadata']['page']=='f75v' and line['metadata']['edition']==reader and line['metadata']['kind']=='P'
  nativeids.add(matches[0]['source_group_id'])
  pair=next(x for x in oldpairs if x['reader']==reader);assert p['doublet_old_case']==pair
  index=pair['first_group_index'];group={int(g['source_group_index']):g for g in pair['complete_line']}
  for i in [index,index+1]:
   g=group[i];assert g['ivtff_group_raw']=='qokeedy';assert g['left_separator']==g['right_separator']=='DEFINITE_SPACE';assert group[i-1]['right_separator']==g['left_separator'] and g['right_separator']==group[i+1]['left_separator']
   rid=reader+'|'+pair['locus']+'|G'+str(i).zfill(3);assert byid[rid]['ivtff_group_raw']=='qokeedy';nativeids.add(rid)
  expected_roles=[dict(zip(SEL,['S'+str(i) for i in perm])) for perm in itertools.permutations(range(3))];assert [x['selector_roles'] for x in p['cases']]==expected_roles
  primary=secondary=0
  for c in p['cases']:
   roles=c['selector_roles'];enc=lambda word:[roles.get(x,'P') for x in word]
   ptest=replay(enc('qoqo'),[(phase,b) for phase in PH for b in range(3)]);assert ptest==c['primary_prefix_trace'];assert bool(ptest[-1])==c['primary_compatible'];primary+=bool(ptest[-1])
   t1=replay(enc('qokeedy'),[('N',b) for b in range(3)]);t2=replay(enc('qokeedy'),[s for s in t1[-1] if s[0]=='N']);assert t1==c['doublet_first_trace'] and t2==c['doublet_second_trace']
   yes=any(s[0]=='N' for s in t2[-1]);assert yes==c['doublet_compatible'];secondary+=yes;rolecases+=1
  sr=res['readers'][reader];assert sr['payload_units_forced']==END and sr['selector_units_forced']==SEL
  assert sr['primary_compatible_assignments']==primary and sr['doublet_compatible_assignments']==secondary
  assert sr['endpoint_types']==len({e['word'] for e in p['ending_witnesses']}) and sr['single_occurrence_endpoint_types']==sorted({e['word'] for e in p['ending_witnesses'] if e['frequency']==1})
  assert sr['qoqo_locus']=='f75v.39' and sr['qoqo_left_separator']==matches[0]['left_separator'] and sr['doublet_locus']==pair['locus']
  expected='EXACT_BANK_CARRIER_SYNTAX_EXCLUDED' if primary==0 or secondary==0 else 'NECESSARY_SYNTAX_CAPACITY';assert sr['status']==expected
 for f in json.loads((B/'artifacts/FIXTURES.json').read_text())['cases']:
  actual=replay(f['symbols'],f['initial']);assert actual==f['trace'] and bool(actual[-1])==f['expected_nonempty']
 assert res['status']==('ALL_READERS_EXACT_OVERLAP_CARRIER_SYNTAX_EXCLUDED' if all(r['status']=='EXACT_BANK_CARRIER_SYNTAX_EXCLUDED' for r in res['readers'].values()) else 'MIXED_OR_CAPACITY')
 out={'status':'PASS','endpoint_ancestries':paths,'source_ids_bound':len(nativeids),'selector_role_cases':rolecases,'implementation':'Independent boolean adjacency-matrix reachability; no runner import. Complete source witness/old certificate binding.','ceiling':'Conditional fixed carrier/working-unit/boundary proof, not native meanings or independent palaeography.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
