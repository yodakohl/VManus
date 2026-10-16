#!/usr/bin/env python3
"""Endpoint-retaining inner deletion over one fixed wordbook; no meanings."""
import argparse,collections,gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 data=p.read_bytes();return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def controls():
 alpha='abc';cases=0
 for n in range(1,6):
  for letters in itertools.product(alpha,repeat=n):
   word=''.join(letters)
   for mask in itertools.product([False,True],repeat=max(0,n-2)):
    out=word if n<=2 else word[0]+''.join(c for c,keep in zip(word[1:-1],mask) if keep)+word[-1]
    for perm in itertools.permutations(alpha):
     pi=dict(zip(alpha,perm));visible=''.join(pi[c] for c in out)
     assert (len(visible)==1)==(len(word)==1)
     if len(visible)==1:assert visible==pi[word]
     cases+=1
 assert len('aa'[0]+'aa'[-1])==2 # coalescing endpoints is outside this rule.
 return {'status':'PASS_SOURCE_FREE_CONTROLS','deletion_bijection_cases':cases,'equal_endpoints_remain_two':True,'native_or_source_data_read':False}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');a=ap.parse_args()
 if a.controls:print(json.dumps(controls()));return
 for pin in read(B/'LOCK.json')['files']:assert hashlib.sha256((R/pin['path']).read_bytes()).hexdigest()==pin['sha256'],pin['path']
 s=read(B/'src/SPEC.json');src=read(R/'experiments/yolo/gdt1228_bare_hebrew_bijection_screen/artifacts/SOURCE_PROJECTION.json');sections=src['source_sections'];words=[w for sec in sections for w in sec['words']];W=set(words);alphabet=sorted(set(''.join(words)))
 assert len(words)==src['tokens']==s['source_expected_tokens'];assert len(sections)==s['source_expected_sections'] and len(alphabet)==s['source_expected_alphabet'];assert all(w for w in words)
 single=collections.defaultdict(list)
 for sec in sections:
  for index,w in enumerate(sec['words'],1):
   if len(w)==1:single[w].append({'ref':sec['ref'],'index':index})
 source={'sections':len(sections),'tokens':len(words),'alphabet':alphabet,'wordbook_types':len(W),'wordbook_sha256':hashlib.sha256('\n'.join(sorted(W)).encode('utf-8')).hexdigest(),'single_word_types':len(single),'singletons':[{'word':w,'token_count':len(ev),'occurrences':ev} for w,ev in sorted(single.items())]}
 native=read(R/'experiments/yolo/gdt1227_relation_path_one_sign_capacity/artifacts/RESULT.json');cached=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');out={'experiment_id':'GDT1396','source':source,'readers':{}}
 for ed in s['readers']:
  old=native['readings'][ed];counts=dict(sorted(old['counts'].items()));verify=collections.Counter()
  for row in cached[ed]:
   assert row['edition']==ed and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   if len(row['units'])==1:
    assert row['units'][0]==row['ivtff_group_raw'];verify.update(row['units'])
  assert dict(verify)==counts and len(counts)==old['types']==s['native_expected_types'][ed] and sum(counts.values())==old['tokens'];assert all(counts.get(x,0)>0 for x in s['common6'])
  tiers={}
  for name,forms in [('ALL',sorted(counts)),('GE2',sorted(k for k,v in counts.items() if v>=2)),('COMMON6',sorted(s['common6']))]:tiers[name]={'forms':forms,'types':len(forms),'status':'EXCLUDED' if len(forms)>len(single) else 'NOT_EXCLUDED'}
  out['readers'][ed]={'counts':counts,'inherited_tokens':old['tokens'],'tiers':tiers}
 statuses=[v['tiers']['ALL']['status']=='EXCLUDED' for v in out['readers'].values()];out['status']='FIXED_W_DOMAIN_EXCLUDED_ALL_READERS' if all(statuses) else ('SOME_READERS_EXCLUDED' if any(statuses) else 'NECESSARY_CAPACITY_ONLY');save(B/'artifacts/RESULT.json',out)
 print(json.dumps({'status':out['status'],'source_one_character_word_types':len(single),'readers':{k:{n:t['status'] for n,t in v['tiers'].items()} for k,v in out['readers'].items()}},indent=2))
if __name__=='__main__':main()
