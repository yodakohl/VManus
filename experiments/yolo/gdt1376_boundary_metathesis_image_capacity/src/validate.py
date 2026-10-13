#!/usr/bin/env python3
"""Independent direct canonical-inverse/forward image validation."""
import argparse, collections, csv, gzip, hashlib, itertools, json, re
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
OLD='experiments/yolo/'
ALPHABET=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def transform(words,a,b):
 marked=[i for i in range(len(words)-1) if words[i][-1]==a and words[i+1][0]==b]
 result=[list(w) for w in words];touched=set()
 for i in marked:
  positions=((i,len(words[i])-1),(i+1,0));assert not touched.intersection(positions);touched.update(positions)
  result[i][-1],result[i+1][0]=words[i+1][0],words[i][-1]
 return result

def canonical(words,a,b):
 original=[[b,b]]+[list(w) for w in words]+[[a,a]]
 inverse=transform(original,b,a);forward=transform(inverse,a,b)
 return original,inverse,forward

def lemma(words,a,b):
 for i in range(len(words)-1):
  if words[i][-1]!=a or words[i+1][0]!=b:continue
  left=len(words[i])==1 and i>0 and words[i-1][-1]==b
  right=len(words[i+1])==1 and i+2<len(words) and words[i+2][0]==a
  if not(left or right):return False
 return True

def controls():
 # Enumerate full source images rather than possible inverse choices.
 vocab=[list(x) for n in (1,2) for x in itertools.product('ABC',repeat=n)]
 checked=0
 for size in range(4):
  image={tuple(map(tuple,transform(words,'A','B'))) for words in itertools.product(vocab,repeat=size)}
  for words in itertools.product(vocab,repeat=size):
   valid=tuple(map(tuple,words)) in image
   assert valid==lemma(words,'A','B')
   assert valid==(transform(transform(words,'B','A'),'A','B')==list(words));checked+=1
 # Any external source words of length1/2 over A/B suffice to verify open extensions on small cases.
 small=[list(x) for n in (1,2) for x in itertools.product('AB',repeat=n)];opened=0
 for size in range(4):
  image=set()
  for source in itertools.product(small,repeat=size):
   for left,right in itertools.product(small,repeat=2):
    image.add(tuple(map(tuple,transform([left]+list(source)+[right],'A','B')[1:-1])))
  for words in itertools.product(small,repeat=size):
   padded,inv,forward=canonical(words,'A','B');valid=tuple(map(tuple,words)) in image
   assert valid==(padded==forward)==lemma(padded,'A','B');opened+=1
 assert transform([['A'],['A'],['B']],'A','B')==[['A'],['B'],['A']]
 return {'closed_exhaustive_streams':checked,'open_exhaustive_streams':opened,'singleton_created_AB':'PASS','canonical_inverse':'PASS','output_padding':'PASS'}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--controls-only',action='store_true');args=parser.parse_args();checks=controls()
 if args.controls_only:print(json.dumps(checks));return
 lock=read(B/'src/REGISTRATION_LOCK.json')
 for path,h in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h,path
 data=read(ROOT/(OLD+'gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'))
 allowed={x['page'] for x in csv.DictReader((ROOT/(OLD+'gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')).open(),delimiter='\t')}
 assert sorted(read(ROOT/(OLD+'gdt1279_strict_inner_symbol_prediction/artifacts/MODEL.json'))['alphabet'])==ALPHABET
 allruns={};allresults={};direct_cases=0
 for rd,rows in data.items():
  loci=collections.defaultdict(list);ids=set()
  for row in rows:
   assert row['edition']==rd and row['id'] not in ids;ids.add(row['id'])
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v')
   assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   raw=row['ivtff_group_raw'];parsed=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',raw)
   assert ''.join(parsed)==raw and parsed==row['units'] and parsed and set(parsed)<=set(ALPHABET)
   assert row['id']==rd+'|'+row['locus']+'|G'+str(int(row['source_group_index'])).zfill(3)
   loci[(row['page'],row['locus'])].append(row)
  runs=[]
  for key,members in sorted(loci.items()):
   ordered=sorted(members,key=lambda r:int(r['source_group_index']));assert len({int(r['source_group_index']) for r in ordered})==len(ordered)
   run=[]
   for row in ordered:
    if run and int(row['source_group_index'])!=int(run[-1]['source_group_index'])+1:
     runs.append({'sources':run});run=[]
    run.append(row)
   if run:runs.append({'sources':run})
  allruns[rd]=runs;keys=[]
  for a,b in itertools.permutations(ALPHABET,2):
   ab=non=bad=ba=0;leaves=set();first=None;digest=hashlib.sha256()
   for ri,run in enumerate(runs):
    words=[r['units'] for r in run['sources']];original,inverse,forward=canonical(words,a,b);direct_cases+=1
    internalbad=[]
    for i in range(len(words)-1):
     if words[i][-1]==b and words[i+1][0]==a:ba+=1
     if words[i][-1]==a and words[i+1][0]==b:
      ab+=1;non+=int(len(words[i])>=2 and len(words[i+1])>=2)
      if forward[i+1][-1]!=a or forward[i+2][0]!=b:
       assert forward[i+1][-1]==b and forward[i+2][0]==a;internalbad.append(i)
    reconstructed=[w[:] for w in original]
    for i in internalbad:reconstructed[i+1][-1]=b;reconstructed[i+2][0]=a
    assert reconstructed==forward
    assert (not internalbad)==(original==forward)
    if internalbad:
     bad+=len(internalbad);leaves.add(int(re.match(r'f(\d+)',run['sources'][0]['page'])[1]))
     if first is None:first={'run_index':ri,'boundary_index':internalbad[0]}
    digest.update((json.dumps(inverse[1:-1],ensure_ascii=False,separators=(',',':'))+'\n').encode())
   keys.append({'A':a,'B':b,'ab_count':ab,'nonsingleton_ab':non,'unsupported_ab':bad,'unsupported_leaves':len(leaves),'first_unsupported':first,'ba_opportunities':ba,'status':'EXCLUDED' if bad else 'LOCAL_IMAGE_CAPACITY','canonical_preimage_sha256':None if bad else digest.hexdigest()})
  survivors=[x for x in keys if x['status']=='LOCAL_IMAGE_CAPACITY']
  allresults[rd]={'groups':len(rows),'runs':len(runs),'boundaries':sum(len(r['sources'])-1 for r in runs),'keys':keys,'excluded_keys':len(keys)-len(survivors),'surviving_keys':len(survivors),'survivors_with_ba':sum(x['ba_opportunities']>0 for x in survivors),'survivors_requiring_change':sum(x['ab_count']>0 for x in survivors)}
 assert allruns==read(B/'artifacts/RUNS.json.gz'),'run reconstruction'
 expected={'status':'BOUNDARY_METATHESIS_IMAGE_CAPACITY','readers':allresults};actual=read(B/'artifacts/RESULT.json')
 assert expected==actual,'result discrepancy'
 receipt={'status':'PASS','controls':checks,'direct_padded_inverse_forward_cases':direct_cases,'readers':{rd:{'keys':len(r['keys']),'surviving_keys':r['surviving_keys']} for rd,r in allresults.items()},'method':'Direct canonical BA inverse followed by original-source AB writer for every padded run/key; no native lemma counting, no primary imports.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
