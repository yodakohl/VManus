from pathlib import Path
import collections,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,v):(B/'artifacts'/n).write_text(json.dumps(v,indent=2)+'\n')
def fixtures():
 alphabet='abcdefghijklmnopqrstuvwxyz '; bank=['a'*i+'o' for i in range(1,61)]; index={w:i for i,w in enumerate(bank)};n=0
 for chars in itertools.chain([()],itertools.product(alphabet,repeat=1),itertools.product(alphabet,repeat=2)):
  for k in (0,1,2):
   anchor=13;state=anchor;out=[bank[state]]*k
   for c in chars:
    state=(state+alphabet.index(c)+1)%len(bank);out+=[bank[state]]*(1+k)
   got=[];state=anchor
   for w in out:
    d=(index[w]-state)%len(bank);state=index[w]
    if d:assert 1<=d<=27;got.append(alphabet[d-1])
   assert ''.join(got)==''.join(chars);n+=1
 cases=0
 for s in range(1,7):
  for m in range(s+1,4*s+3):
   feasible=any(1<=d<=s and 1<=(-d)%m<=s for d in range(1,m))
   assert feasible==(m<=2*s);cases+=1
 return {'roundtrips':n,'small_ring_cases':cases,'status':'PASS'}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();groups=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');pairs=read(R/'experiments/yolo/gdt1319_cross_word_endpoint_state/artifacts/PAIRS.json.gz');tables={};witness={};result={}
 for ed,rows in sorted(groups.items()):
  types=collections.defaultdict(set);edges=collections.defaultdict(dict)
  for r in rows:types[r['page']].add(r['ivtff_group_raw'])
  for p in sorted(pairs[ed],key=lambda p:(p['left']['locus'],int(p['left']['source_group_index']))):
   l,r=p['left'],p['right'];assert l['page']==r['page'] and l['locus']==r['locus'] and int(r['source_group_index'])==int(l['source_group_index'])+1
   a,b=l['ivtff_group_raw'],r['ivtff_group_raw']
   if a!=b:edges[l['page']].setdefault((a,b),{'left':l,'right':r})
  table=[];qual=[]
  for page,forms in sorted(types.items()):
   e=edges[page];rec=sorted((a,b) for a,b in e if a<b and (b,a) in e);q=len(forms)>54 and bool(rec)
   table.append({'page':page,'distinct_forms':len(forms),'reciprocal_pairs':len(rec),'qualifies':q})
   if q:qual.append(page)
   if q and ed not in witness:
    a,b=rec[0];witness[ed]={'page':page,'distinct_forms':len(forms),'forms':sorted(forms),'pair':[a,b],'forward':e[a,b],'reverse':e[b,a]}
  tables[ed]=table;result[ed]={'status':'FORWARD_WHEEL_EXCLUDED' if qual else 'NOT_EXCLUDED_BY_THIS_TEST','qualifying_pages':len(qual),'selected_page':qual[0] if qual else None,'groups':len(rows),'original_pairs':len(pairs[ed])};print(ed,result[ed],flush=True)
 save('PAGES.json',tables);save('WITNESSES.json',witness);save('RESULT.json',{'status':'FORWARD_WORD_WHEEL_EXCLUDED_ALL_READINGS' if len(witness)==3 else 'READER_SPECIFIC_NECESSARY_BOUND','readers':result,'fixtures':fx})
if __name__=='__main__':main()
