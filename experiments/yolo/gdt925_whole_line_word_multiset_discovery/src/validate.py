import collections, hashlib, itertools, json, re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];P=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
def main():
 result=json.loads((E/'artifacts/RESULT.json').read_text());pairs=json.loads((E/'artifacts/PAIRS.json').read_text());groups=json.loads((E/'artifacts/GROUPS.json').read_text())
 for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 spec=json.loads((P/'src/SPEC.json').read_text());counts={}; signatures=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  valid={};den=collections.Counter()
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text());ci={k:i for i,k in enumerate(d['group_columns'])}
   for row in d['lines']:
    m=row['metadata'];assert m['page'] in spec['partitions'][phase] and not m['page'].startswith('f84')
    if m['kind']!='P':continue
    den['prose_lines']+=1;g=row['groups'];w=[x[ci['ivtff_group_raw']] for x in g]
    if len(g)<2:den['short']+=1;continue
    if any(not re.fullmatch(r'[a-z]+',v) for v in w):den['nonliteral']+=1;continue
    ix=[int(x[ci['source_group_index']]) for x in g]
    seams=[x[ci['right_separator']] for x in g[:-1]]+[x[ci['left_separator']] for x in g[1:]]
    if ix!=list(range(ix[0],ix[0]+len(ix))) or set(seams)!={'DEFINITE_SPACE'}:den['seam_or_index']+=1;continue
    uid=m['page']+'|'+m['locus'];assert uid not in valid
    valid[uid]=(w,int(re.match(r'f(\d+)',m['page'])[1]),[x[ci['source_group_id']] for x in g]);den['eligible_lines']+=1
  bylen=collections.defaultdict(list)
  for uid,(w,leaf,ids) in valid.items():bylen[len(w)].append((uid,w,leaf,collections.Counter(w)))
  expected=[];comparisons=0
  for rows in bylen.values():
   for a,b in itertools.combinations(sorted(rows),2):
    comparisons+=1
    if a[3]!=b[3]:continue
    expected.append(dict(a=a[0],b=b[0],words_a=a[1],words_b=b[1],n=len(a[1]),changed_order=a[1]!=b[1],exact_reversal=a[1]!=b[1] and a[1]==list(reversed(b[1])),cross_leaf=a[2]!=b[2]))
  expected.sort(key=lambda q:(q['a'],q['b']));assert expected==pairs[ed]
  panel=result['panels'][ed];assert panel['denominators']==dict(den);assert panel['eligible_ids']==sorted(valid)
  assert panel['pairs']==len(expected)
  assert panel['changed_order_pairs']==sum(p['changed_order'] for p in expected)
  assert panel['changed_order_n_ge_3']==sum(p['changed_order'] and p['n']>=3 for p in expected)
  assert panel['cross_leaf_changed_order']==sum(p['changed_order'] and p['cross_leaf'] for p in expected)
  gp=[];seen=set()
  for group in groups[ed]:
   assert len(group['lines'])>=2
   for row in group['lines']:
    uid=row['id'];assert uid not in seen;seen.add(uid);w,leaf,ids=valid[uid]
    assert (row['words'],row['leaf'],row['source_ids'])==(w,leaf,ids)
    assert collections.Counter(group['multiset'])==collections.Counter(w)
   gp.extend(tuple(sorted([a['id'],b['id']])) for a,b in itertools.combinations(group['lines'],2))
  assert sorted(gp)==[(p['a'],p['b']) for p in expected];assert panel['recurrent_multisets']==len(groups[ed])
  signatures.append({(q['a'],q['b']) for q in expected if q['changed_order']});counts[ed]=dict(eligible=len(valid),direct_pair_comparisons=comparisons,matching_pairs=len(expected))
 assert result['all_three_changed_order_locus_pairs']==[list(x) for x in sorted(set.intersection(*signatures))]
 assert result['meaning_claims']==0 and not result['significance_claim'] and result['independent_confirmation_capacity']==0
 # Multiplicity and reversal must not collapse to set equality or identity.
 assert collections.Counter(['a','a','b'])!=collections.Counter(['a','b','b'])
 assert collections.Counter(['a','b','a'])==collections.Counter(['b','a','a'])
 out=dict(status='PASS',method='nonimporting direct Counter comparison of every eligible equal-length pair',counts=counts,synthetic_checks=2)
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(out))
if __name__=='__main__':main()
