#!/usr/bin/env python3
"""Independent splice enumeration and complete cached-source replay."""
import collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
PAIRS={'ADJACENT':(0,1,2,3),'PARALLEL':(0,2,1,3),'CROSSED':(0,3,1,2)}
def edits(a,b):
 result=set()
 # Enumerate deleted source span and inserted target span, both at most one.
 for i in range(len(a)+1):
  for oldlen,newlen in [(0,1),(1,0),(1,1)]:
   if i+oldlen>len(a) or i+newlen>len(b):continue
   old=a[i:i+oldlen];new=b[i:i+newlen]
   if old==new or a[:i]+new+a[i+oldlen:]!=b:continue
   kind={(0,1):'INS',(1,0):'DEL',(1,1):'SUB'}[(oldlen,newlen)]
   result.add((kind,old,new,'L',i));result.add((kind,old,new,'R',len(a)-i-oldlen))
 return result
def read(name):return json.loads((E/'artifacts'/name).read_text())
def key(h):return h['edition'],h['locus'],h['start_index'],h['pairing']
def main():
 spec=json.loads((E/'src/SPEC.json').read_text());hits=[];den={};full=[]
 for ed,src in spec['sources'].items():
  raw=(ROOT/src['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==src['sha256'];data=json.loads(raw);cnt=dict(candidate=0,definite_plain=0,four_distinct=0,ADJACENT=0,PARALLEL=0,CROSSED=0)
  for line in data['lines']:
   m=line['metadata'];assert m['edition']==ed and m['page'] in spec['allowed_selectors'] and not m['page'].startswith('f84')
   groups=[dict(zip(data['group_columns'],g)) for g in line['groups']];before=len(hits)
   for end in range(4,len(groups)+1):
    g=groups[end-4:end];w=[x['ivtff_group_raw'] for x in g];cnt['candidate']+=1
    if any(re.fullmatch('[a-z]+',x) is None for x in w):continue
    indices=[int(x['source_group_index']) for x in g]
    if indices!=list(range(indices[0],indices[0]+4)):continue
    if any(g[i]['right_separator']!='DEFINITE_SPACE' or g[i+1]['left_separator']!='DEFINITE_SPACE' for i in range(3)):continue
    cnt['definite_plain']+=1
    if len(set(w))!=4:continue
    cnt['four_distinct']+=1
    for pairing,(a,b,c,d) in PAIRS.items():
     shared=edits(w[a],w[b]).intersection(edits(w[c],w[d]))
     if shared:
      cnt[pairing]+=1;hits.append(dict(edition=ed,locus=m['locus'],page=m['page'],folio=re.match('f[0-9]+',m['page'])[0],start_index=indices[0],source_ids=[x['source_group_id'] for x in g],words=w,pairing=pairing,signatures=[list(s) for s in sorted(shared)]))
   if len(hits)>before:full.append(dict(edition=ed,metadata=m,group_columns=data['group_columns'],groups=line['groups']))
  den[ed]=cnt
 assert sorted(hits,key=key)==read('HITS.json');assert full==read('FULL_HIT_LINES.json')
 # Compare every edition-independent occurrence signature, counting editions once.
 support=collections.defaultdict(dict)
 for h in hits:
  for sig in h['signatures']:
   k=(h['locus'],h['start_index'],tuple(h['words']),h['pairing'],tuple(sig));support[k][h['edition']]=h
 shared=collections.defaultdict(list)
 for k,byed in support.items():
  if set(byed)==set(spec['sources']):shared[k[:-1]].append((k[-1],byed))
 consensus=[]
 for k,entries in shared.items():
  sample=entries[0][1]['ZL3b'];consensus.append({x:v for x,v in sample.items() if x not in ['edition','source_ids','signatures']}|dict(signatures=[list(s) for s in sorted(x[0] for x in entries)],source_ids_by_reading={ed:h['source_ids'] for ed,h in entries[0][1].items()}))
 canon=lambda x:json.dumps(x,sort_keys=True)
 assert sorted(consensus,key=canon)==sorted(read('CONSENSUS.json'),key=canon)
 rules=collections.defaultdict(list)
 for h in consensus:
  for s in h['signatures']:rules[(h['pairing'],tuple(s))].append(h)
 aggregate=[]
 for (pairing,sig),hs in rules.items():
  a,b,c,d=PAIRS[pairing];leaves=sorted({h['folio'] for h in hs},key=lambda f:int(f[1:]));bases=sorted({(h['words'][a],h['words'][c]) for h in hs})
  aggregate.append(dict(pairing=pairing,signature=list(sig),folios=leaves,base_pairs=[list(b) for b in bases],occurrences=len(hs),nomination=len(leaves)>=3 and len(bases)>=2))
 assert sorted(aggregate,key=canon)==sorted(read('RULES.json'),key=canon)
 expected=dict(status='COMPLETE_LOCAL_EDIT_DISCOVERY_NO_SEMANTIC_TEST',denominators=den,hit_rows=len(hits),concordant_window_pairings=len(consensus),concordant_physical_leaves=sorted({h['folio'] for h in consensus},key=lambda f:int(f[1:])),signature_rows=len(aggregate),nominated_signature_rows=sum(x['nomination'] for x in aggregate),meaning_claims=0,significance='NOT_TESTED_NO_SEARCH_NULL')
 assert expected==read('RESULT.json')
 print(json.dumps(dict(status='PASS',validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),result=expected),indent=2))
if __name__=='__main__':main()
