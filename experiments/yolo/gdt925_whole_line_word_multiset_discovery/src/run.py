import collections, hashlib, itertools, json, re
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
P=ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
def write(name,obj):
 (E/'artifacts'/name).write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
def main():
 lock=json.loads((E/'PREREG_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 spec=json.loads((P/'src/SPEC.json').read_text()); panels={}; allgroups={}; allpairs={}
 for ed in ['ZL3b','IT2a','RF1b']:
  den=collections.Counter(); buckets=collections.defaultdict(list); eligible=[]
  for phase in ['DISCOVERY','EVALUATION']:
   d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text())
   for r in d['lines']:
    m=r['metadata']; assert m['page'] in spec['partitions'][phase] and not m['page'].startswith('f84')
    if m['kind']!='P':continue
    den['prose_lines']+=1; gs=[dict(zip(d['group_columns'],g)) for g in r['groups']]
    if len(gs)<2:den['short']+=1;continue
    if not all(re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs):den['nonliteral']+=1;continue
    if not all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:])):den['seam_or_index']+=1;continue
    w=[g['ivtff_group_raw'] for g in gs]; leaf=int(re.match(r'f(\d+)',m['page'])[1]); uid=m['page']+'|'+m['locus']
    v=dict(id=uid,page=m['page'],locus=m['locus'],leaf=leaf,words=w,source_ids=[g['source_group_id'] for g in gs])
    buckets[tuple(sorted(w))].append(v);eligible.append(uid);den['eligible_lines']+=1
  groups=[]; pairs=[]
  for bag,rows in sorted(buckets.items()):
   if len(rows)<2:continue
   rows.sort(key=lambda r:r['id']);groups.append(dict(multiset=list(bag),lines=rows))
   for a,b in itertools.combinations(rows,2):
    pairs.append(dict(a=a['id'],b=b['id'],words_a=a['words'],words_b=b['words'],n=len(bag),changed_order=a['words']!=b['words'],exact_reversal=a['words']!=b['words'] and a['words']==b['words'][::-1],cross_leaf=a['leaf']!=b['leaf']))
  pairs.sort(key=lambda q:(q['a'],q['b']))
  panels[ed]=dict(denominators=dict(den),eligible_ids=sorted(eligible),recurrent_multisets=len(groups),pairs=len(pairs),changed_order_pairs=sum(q['changed_order'] for q in pairs),changed_order_n_ge_3=sum(q['changed_order'] and q['n']>=3 for q in pairs),cross_leaf_changed_order=sum(q['changed_order'] and q['cross_leaf'] for q in pairs))
  allgroups[ed]=groups;allpairs[ed]=pairs
 signatures=[{(q['a'],q['b']) for q in allpairs[ed] if q['changed_order']} for ed in panels]
 common=sorted(set.intersection(*signatures))
 result=dict(status='COMPLETE_EXPLORATORY_CENSUS',panels=panels,all_three_changed_order_locus_pairs=common,meaning_claims=0,significance_claim=False,independent_confirmation_capacity=0,prior_exposure=True)
 write('GROUPS.json',allgroups);write('PAIRS.json',allpairs);write('RESULT.json',result)
 lines=['# Complete recurrent-line table','','All qualifying repeated multisets, including unchanged order. No semantic identity is asserted.','']
 for ed,groups in allgroups.items():
  lines+=['## '+ed,'','| Multiset | Locus | Complete written line |','|---|---|---|']
  for g in groups:
   for r in g['lines']:lines.append('| '+' '.join(g['multiset'])+' | '+r['id'].replace('|',' / ')+' | '+' '.join(r['words'])+' |')
  if not groups:lines+=['','No qualifying recurrent multiset.']
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({ed:{k:v for k,v in p.items() if k!='eligible_ids'} for ed,p in panels.items()},sort_keys=True))
if __name__=='__main__':main()
