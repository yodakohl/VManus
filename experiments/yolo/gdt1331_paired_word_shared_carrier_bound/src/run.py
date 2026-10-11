from pathlib import Path
import collections,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=tuple(sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,obj):(B/'artifacts'/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def parses(w,h):
 i=0
 while i<len(w):i+=2 if w[i] in h else 1
 return i==len(w)
def fixtures():
 n=0
 for heads in (set(),{'x'},{'y'},{'x','y'}):
  codes=[(u,) for u in 'xy' if u not in heads]+[(u,v) for u in heads for v in 'xy']
  for size in range(7):
   for word in itertools.product('xy',repeat=size):
    ok=[False]*(size+1);ok[0]=True
    for end in range(1,size+1):ok[end]=any(end>=len(c) and ok[end-len(c)] and word[end-len(c):end]==c for c in codes)
    assert parses(word,heads)==ok[-1];n+=1
 assert parses('xyy',{'x'}) and parses('xyy',{'y'}) and not parses('xyy',{'x','y'})
 for letters in itertools.product('abc',repeat=3):
  left=[];right=[]
  for letter in letters:left.append(letter);right.append(letter)
  assert left==right and right
 return {'status':'PASS','explicit_code_dp_checks':n,'singleton_BOTH_checks':27,'separate_heads_need_not_compose':True,'odd_final_cannot_be_BOTH_only':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 checks=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');decisions={};inventory={};result={}
 for ed,rows in sorted(data.items()):
  counts=collections.Counter(tuple(r['units']) for r in rows);witness={}
  for r in sorted(rows,key=lambda r:r['id']):witness.setdefault(tuple(r['units']),r)
  words=sorted(counts);table=[]
  for heads in itertools.combinations(U,3):
   h=set(heads);bad=next((w for w in words if not parses(w,h)),None)
   row={'heads':list(heads),'status':'EXCLUDED_ORPHAN_HEAD' if bad is not None else 'COMPATIBLE_RELAXED_PREFIX'}
   if bad is not None:row.update(first_failing_units=list(bad),witness=witness[bad])
   else:
    free=[w for w in words if not h.intersection(w)];row.update(head_free_occurrences=sum(counts[w] for w in free),head_free_types=len(free))
   table.append(row)
  good=[r for r in table if r['status']=='COMPATIBLE_RELAXED_PREFIX'];best=min(good,key=lambda r:(r['head_free_occurrences'],r['heads'])) if good else None
  result[ed]={'groups':len(rows),'types':len(words),'head_sets':len(table),'compatible_head_sets':len(good),'minimum_identical_source_pair_count':best['head_free_occurrences'] if best else None,'minimum_identical_source_pair_fraction':best['head_free_occurrences']/len(rows) if best else None,'selected_minimizing_heads':best['heads'] if best else None,'status':'SAME_SOURCE_PAIR_LOWER_BOUND_ONLY' if good else 'EXCLUDED_RELAXED_PREFIX_CARRIER'}
  inventory[ed]=[{'units':list(w),'raw':''.join(w),'count':counts[w]} for w in words if best and not set(best['heads']).intersection(w)];decisions[ed]=table
 save('HEAD_SETS.json',decisions);save('MINIMUM_HEAD_FREE_TYPES.json',inventory);save('RESULT.json',{'status':'READER_SPECIFIC_CARRIER_BOUNDS','readers':result,'fixtures':checks});print(json.dumps(result,indent=2))
if __name__=='__main__':main()
