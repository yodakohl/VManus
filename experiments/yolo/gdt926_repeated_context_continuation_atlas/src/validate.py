import collections,json,re,hashlib
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];P=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
export=json.loads((E/'artifacts/ELIGIBLE_LINES.json').read_text());allowed=set(json.loads((P/'src/SPEC.json').read_text())['allowed_selectors']);validated={};all_seen={}
for ed in ['ZL3b','IT2a','RF1b']:
 actual={};seen={}
 for phase in ['DISCOVERY','EVALUATION']:
  d=json.loads((P/'artifacts'/f'SOURCE_{phase}_{ed}.json').read_text());ix={n:i for i,n in enumerate(d['group_columns'])}
  for row in d['lines']:
   m=row['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
   if m['kind']!='P':continue
   gs=row['groups'];w=[g[ix['ivtff_group_raw']] for g in gs];seen[m['page']+'|'+m['locus']]=w
   if len(w)<2 or any(re.fullmatch('[a-z]+',x) is None for x in w):continue
   valid=True
   for j in range(1,len(gs)):
    a,b=gs[j-1],gs[j]
    if int(b[ix['source_group_index']])-int(a[ix['source_group_index']])!=1 or a[ix['right_separator']]!='DEFINITE_SPACE' or b[ix['left_separator']]!='DEFINITE_SPACE':valid=False
   if valid:actual[m['page']+'|'+m['locus']]=(w,[g[ix['source_group_id']] for g in gs])
 all_seen[ed]=seen
 assert actual=={x['id']:(x['words'],x['source_ids']) for x in export[ed]}
 # Independent trie of all prefixes of each suffix, instead of tuple hash buckets.
 root={}
 for l in export[ed]:
  for start in range(len(l['words'])):
   node=root
   for end in range(start,len(l['words'])-1):
    node=node.setdefault(l['words'][end],{'children':{},'occ':[]});node['occ'].append((l['id'],start,end+1,l['words'][end+1],l['leaf']));node=node['children']
 found={}
 def visit(children,prefix=()):
  for word,node in children.items():
   a=prefix+(word,);os=node['occ'];leaves={o[4] for o in os};branches={o[3] for o in os}
   if len(a)>=3 and len(set(a))>=2 and len(leaves)>=2 and len(branches)>=2:found[a]=sorted(os)
   visit(node['children'],a)
 visit(root)
 candidates=json.loads((E/'artifacts'/f'CANDIDATES_{ed}.json').read_text())
 reported={tuple(a['anchor']):sorted((o['line'],o['start'],o['end'],o['next'],o['leaf']) for o in a['occurrences']) for a in candidates}
 assert found==reported
 for a in candidates:
  branchleaves=collections.defaultdict(set)
  for o in a['occurrences']:
   w=actual[o['line']][0];assert w[o['start']:o['end']]==a['anchor'] and w[o['end']:]==o['tail'];branchleaves[o['next']].add(o['leaf'])
  assert a['repeated_branch']==(sum(len(x)>=2 for x in branchleaves.values())>=2)
 validated[ed]={'eligible_lines':len(actual),'complete_trie_candidates':len(found),'all_occurrences_and_tails':'PASS'}
# Independently replay every exported top10 alternate-reading status.
anchors={a['id']:a['anchor'] for a in json.loads((E/'artifacts/CANDIDATES_ZL3b.json').read_text())}
for c in json.loads((E/'artifacts/ALTERNATE_AUDIT.json').read_text()):
 ed=c['edition'];line=c['line'];eligible={l['id']:l['words'] for l in export[ed]};seq=anchors[c['anchor_id']]+[c['next']]
 if line not in all_seen[ed]:status='ABSENT_LINE';hits=[]
 elif line not in eligible:status='INELIGIBLE_LINE';hits=[]
 else:
  w=eligible[line];hits=[i for i in range(len(w)-len(seq)+1) if w[i:i+len(seq)]==seq]
  status='UNIQUE_MATCH' if len(hits)==1 else 'AMBIGUOUS_MATCH' if hits else 'NO_EXACT_MATCH'
 assert status==c['status'] and hits==c['matches']

# Audit explicit anchor and continuation in all three guarded literal lines.
for ed in export:
 lines={x['id']:x['words'] for x in export[ed]}
 assert lines['f15v|f15v.12']==['daiin','cthor','chol','chor']
 assert lines['f19r|f19r.10']==['daiin','cthor','chol','ykchor','chordy']
out={'status':'PASS','panels':validated,'complete_context_pair_all_three':'f15v.12 / f19r.10','semantic_validation':False,'significance_control':False}
(E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
