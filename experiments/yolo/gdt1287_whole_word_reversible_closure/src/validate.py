import gzip,hashlib,itertools,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[2]
ALPH=['a','o','e','i','n','d','q','y','s','r','l','m','k','t','p','f','ch','sh','ckh','cth','cph','cfh']
def gz(path):return json.loads(gzip.decompress((ROOT/path).read_bytes()))
def main():
 lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 data=gz('experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');packet=json.loads((P/'artifacts/PROOFS.json').read_text());res=json.loads((P/'artifacts/RESULT.json').read_text());checked=0;linked=set()
 for reader in ['ZL3b','IT2a','RF1b']:
  cache={r['id']:r for r in data[reader]};assert len(cache)==len(data[reader]);words={}
  for rid,r in cache.items():
   assert not r['page'].startswith('f84') and r['page']!='f116v'
   assert r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and r['kind']=='P'
   assert ''.join(r['units'])==r['ivtff_group_raw']
   words.setdefault(tuple(r['units']),[]).append(rid)
  pr=packet[reader];sr=res['readers'][reader]
  for spelling,u in [('ol',('o','l')),('olol',('o','l','o','l'))]:
   expected=[{'id':rid,'page':cache[rid]['page'],'locus':cache[rid]['locus'],'word':spelling,'units':list(u)} for rid in sorted(words.get(u,[]))]
   assert pr['square'][spelling]==expected;assert sr['square_counts'][spelling]==len(expected)
   linked.update((reader,v['id']) for v in expected)
  old={}
  for side,d,f in [('LEFT','gdt1234_prefix_quotient_code_capacity','CERTIFICATE_'),('RIGHT','gdt1241_suffix_quotient_expansion','CLOSURE_')]:old[side]=gz('experiments/yolo/'+d+'/artifacts/'+f+reader+'.json.gz')['nodes']
  needed={'LEFT':set(),'RIGHT':set()};expectedtargets={}
  for symbol in ALPH:
   hits={side:next((i for i,n in enumerate(ns) if n['word']==[symbol]),None) for side,ns in old.items()}
   side='LEFT' if hits['LEFT'] is not None else 'RIGHT'
   if hits[side] is None:continue
   i=hits[side];expectedtargets[symbol]=[side,i];stack=[i]
   while stack:
    j=stack.pop()
    if j in needed[side]:continue
    needed[side].add(j);parents=old[side][j]['parents']
    if parents is not None:assert all(k<j for k in parents);stack.extend(parents)
  assert pr['targets']==expectedtargets
  seeds=set();fixed={}
  for side,chain in pr['chains'].items():
   assert [n['old_id'] for n in chain]==sorted(needed[side]);fixed[side]={}
   for n in chain:
    i=n['old_id'];w=tuple(n['word']);original=old[side][i]
    assert n['word']==original['word'] and n['parents']==original['parents']
    if n['parents'] is None:
     assert w in words;ids=sorted(words[w]);assert n['source_ids']==ids and n['frequency']==len(ids)
     assert n['pages']==sorted({cache[rid]['page'] for rid in ids});seeds.add(w);linked.update((reader,rid) for rid in ids)
    else:
     a,b=[fixed[side][j] for j in n['parents']]
     # Independently remove the known prefix/suffix from the longer parent.
     if side=='LEFT':assert b[:len(a)]==a and b[len(a):]==w
     else:assert b[-len(a):]==a and b[:-len(a)]==w
    fixed[side][i]=w;checked+=1
  for g,(side,i) in expectedtargets.items():assert fixed[side][i]==(g,)
  forced=[g for g in ALPH if g in expectedtargets];missing=[g for g in ALPH if g not in expectedtargets]
  assert sr['forced_units']==forced and sr['missing_units']==missing
  assert sr['whole_groups']==len(data[reader]) and sr['whole_types']==len(words)
  assert sr['chain_nodes']==sum(map(len,needed.values())) and sr['seed_types']==len(seeds)
  assert sr['left_targets']==sum(v[0]=='LEFT' for v in expectedtargets.values()) and sr['right_targets']==sum(v[0]=='RIGHT' for v in expectedtargets.values())
  assert sr['seed_occurrences']==sum(len(words[w]) for w in seeds)
  assert sr['singleton_frequency_seed_types']==[''.join(w) for w in sorted(seeds) if len(words[w])==1]
  status='NONTRIVIAL_REVERSIBLE_WORD_COMPLETION_EXCLUDED' if len(forced)==22 and all(pr['square'].values()) else 'INCONCLUSIVE_BRIDGE';assert sr['status']==status
 assert res['source_occurrences']==sum(map(len,data.values()))
 expected='ALL_READERS_REVERSIBLE_WORD_COMPLETION_EXCLUDED' if all(r['status']=='NONTRIVIAL_REVERSIBLE_WORD_COMPLETION_EXCLUDED' for r in res['readers'].values()) else 'INCONCLUSIVE_BRIDGE';assert res['status']==expected
 # Direct inverse identities on all permutations up to4states (square), up to3(quotients).
 sq=qu=0
 for size in range(1,5):
  perms=list(itertools.permutations(range(size)))
  for t in perms:
   inverse={v:i for i,v in enumerate(t)}
   for start in range(size):
    if t[start]==t[t[start]]:assert inverse[t[start]]==inverse[t[t[start]]]==start
    sq+=1
  if size<4:
   for u in perms:
    inv={v:i for i,v in enumerate(u)}
    for v in perms:
     for s in range(size):
      if u[s]==s and v[u[s]]==s:assert v[s]==s
      if u[s]==s and u[v[s]]==s:assert inv[s]==v[s]==s
      qu+=1
 fixtures=json.loads((P/'artifacts/FIXTURES.json').read_text());assert fixtures['square_cases']==sq and fixtures['quotient_cases']==qu
 c=fixtures['noninjective_square_counterexample'];t=c['map'];s=c['start'];assert t[s]==t[t[s]]==c['end']!=s
 ex=fixtures['insufficient_generator_example'];assert ex['A'][ex['start']]!=ex['start']
 for word in ex['words']:
  q=ex['start']
  for ch in word:q=ex[ch][q]
  assert q==ex['end']
 out={'status':'PASS','certificate_nodes_checked':checked,'original_occurrence_ids_bound':len(linked),'square_cases':sq,'quotient_cases':qu,'scope':'Old proof-chain/source binding and algebraic fixture replay; no new source reconstruction, native machine fit, palaeography or meanings.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
