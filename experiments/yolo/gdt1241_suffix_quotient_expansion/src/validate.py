"""Direct original-direction right closure; no imports from runner/old engine."""
import gzip, hashlib, itertools, json, sys
from datetime import datetime,timezone
from pathlib import Path
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
CACHE=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
OLD=ROOT/'experiments/yolo/gdt1240_prefix_expansion_fourth_power/artifacts'
def derive(original):
 seen=set(map(tuple,original));changed=True
 while changed:
  new={v[:i] for v in seen for i in range(1,len(v)) if v[i:] in seen}
  changed=bool(new-seen);seen.update(new)
 return seen

def fixture():
 words=[tuple(x) for n in range(1,4) for x in itertools.product('ab',repeat=n)]
 tables=0
 for k in (1,2,3):
  for cs in itertools.combinations(words,k):
   if any(x!=y and len(x)<=len(y) and y[len(y)-len(x):]==x for x in cs for y in cs):continue
   originals={sum(parts,()) for m in (1,2,3) for parts in itertools.product(cs,repeat=m)}
   for w in derive(originals):
    rest={w}
    while rest and () not in rest:
     rest={r[:-len(c)] for r in rest for c in cs if len(r)>=len(c) and r[-len(c):]==c}
    assert () in rest
   tables+=1
 assert derive([('a',),('a','b')])=={('a',),('a','b')}
 assert ('b',) in derive([('a',),('b','a')])
 assert ('ch',) in derive([('a',),('ch','a')])
 return {'status':'PASS','suffix_free_tables':tables,'wrong_side_and_unit_cases':3}

def main():
 if '--fixtures' in sys.argv:print(json.dumps(fixture()));return
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress(CACHE.read_bytes()));result=json.loads((A/'RESULT.json').read_text())
 proofs=json.loads((A/'PROOFS.json').read_text());checked=0
 prior=json.loads((OLD/'RESULT.json').read_text())
 assert prior['status']=='ALL_FIVE_SOURCE_EXPANSION_ENVELOPES_EXCLUDED'
 assert json.loads((OLD/'VALIDATION.json').read_text())['status']=='PASS'
 assert set(prior['sources'])=={'b4','w1','bs1','gr1','deot'}
 assert all(x['factorizations']==x['supporting_tokens']==x['supporting_types']==0 for x in prior['sources'].values())
 for reader,rows in sorted(data.items()):
  original={tuple(r['units']) for r in rows};byword={}
  for r in rows:
   assert not r['page'].startswith('f84')
   byword.setdefault(tuple(r['units']),[]).append(r)
  actual=derive(original)
  nodes=json.loads(gzip.decompress((A/f'CLOSURE_{reader}.json.gz').read_bytes()))['nodes']
  seen=set()
  for i,node in enumerate(nodes):
   w=tuple(node['word']);assert w and w not in seen;seen.add(w)
   if node['parents'] is None:assert w in original
   else:
    u,v=node['parents'];assert 0<=u<i and 0<=v<i
    assert nodes[v]['word']==node['word']+nodes[u]['word']
   checked+=1
  assert seen==actual
  singles=sorted(w[0] for w in actual if len(w)==1)
  used=sorted({c for w in original for c in w})
  s=result['readers'][reader]
  assert s['used_units']==used and s['forced_singletons']==singles
  assert s['not_forced']==sorted(set(used)-set(singles))
  assert s['whole_tokens']==len(rows) and s['whole_types']==len(original) and s['closure_types']==len(actual)
  assert s['code_status']==('ALL_USED_CODES_SINGLETON' if singles==used else 'PARTIAL_SINGLETON_OBLIGATIONS')
  need=set()
  def visit(i):
   if i in need:return
   need.add(i)
   if nodes[i]['parents']:
    for j in nodes[i]['parents']:visit(j)
  mapping={tuple(n['word']):i for i,n in enumerate(nodes)}
  assert proofs[reader]['forced_nodes']=={g:mapping[(g,)] for g in singles}
  for g in singles:visit(mapping[(g,)])
  assert [n['id'] for n in proofs[reader]['nodes']]==sorted(need)
  for n in proofs[reader]['nodes']:
   assert n['word']==nodes[n['id']]['word'] and n['parents']==nodes[n['id']]['parents']
   if n['parents'] is None:
    raw=byword[tuple(n['word'])]
    assert n['source_ids']==sorted(r['id'] for r in raw)
    assert n['frequency']==len(raw) and n['pages']==sorted({r['page'] for r in raw})
  witness=byword.get(('k','e','e','e','e','s'),[])
  power={'k','e','s'}<=set(singles) and bool(witness)
  assert s['keeees_ids']==sorted(r['id'] for r in witness)
  assert s['keeees_pages']==sorted({r['page'] for r in witness})
  assert s['fourth_power_obligation']==power
  assert s['source_contracts']=={k:'EXCLUDED_BY_FROZEN1240' if power else 'NO_EXCLUSION_FROM_THIS_TEST' for k in prior['sources']}
 assert result['status']==('ALL_READINGS_SINGLETON_ONLY' if all(v['code_status']=='ALL_USED_CODES_SINGLETON' for v in result['readers'].values()) else 'PARTIAL_SINGLETON_OBLIGATIONS')
 assert result['source_status']==('ALL_READINGS_FIVE_SOURCE_CONTRACTS_EXCLUDED' if all(v['fourth_power_obligation'] for v in result['readers'].values()) else 'SEE_READER_SPECIFIC_CONSEQUENCES')
 out={'status':'PASS','completed_utc':datetime.now(timezone.utc).isoformat(),'closure_nodes_checked':checked,'readings':len(data),'fixtures':fixture(),'scope':'Independent direct-right-quotient algorithm and certificates; frozen1240source outcome reused, no new source census'}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
