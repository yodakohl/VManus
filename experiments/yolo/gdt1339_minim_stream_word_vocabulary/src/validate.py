from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,itertools,json,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());W={'I':1,'N':2,'M':3,'V':2}
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def split(raw):
 ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
 for i in range(len(raw)):
  for u in U:
   if raw.startswith(u,i):ways[i+len(u)]+=[v+(u,) for v in ways[i]]
 assert len(ways[-1])==1;return list(ways[-1][0])
def lower(us):
 dp=[0]+[10**9]*len(us)
 for i,u in enumerate(us):
  sizes=(1,2,3) if u in ('e','i') else (1,)
  for n in sizes:
   if i+n<=len(us) and all(v==u for v in us[i:i+n]):dp[i+n]=min(dp[i+n],dp[i]+1)
 return dp[-1]
def match(word,us):
 i=0;f={};rev={}
 for c in word:
  if c in W:
   n=W[c]
   if i+n>len(us) or us[i] not in ('e','i') or any(v!=us[i] for v in us[i:i+n]):return False
   i+=n
  else:
   if i>=len(us) or us[i] in ('e','i'):return False
   u=us[i]
   if (c in f and f[c]!=u) or (u in rev and rev[u]!=c):return False
   f[c]=u;rev[u]=c;i+=1
 return i==len(us)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 sources=read(R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json');vocab=read(B/'artifacts/REFERENCE_VOCABULARY.json');res=read(B/'artifacts/RESULT.json');origins=defaultdict(Counter);stats={};trans={'J':'I','U':'V','W':'VV'}
 for book in ('b4','w1','bs1','gr1'):
  total=0;accepted=0;excluded=Counter()
  for recipe in sources[book]:
   for token in recipe['words']:
    total+=1
    if not token or not all(('a'<=c<='z') or ('A'<=c<='Z') for c in token):excluded[token]+=1;continue
    word=''.join(trans.get(c.upper(),c.upper()) for c in token);origins[word][book]+=1;accepted+=1
  stats[book]={'stored_tokens':total,'admitted_tokens':accepted,'excluded_tokens':sum(excluded.values()),'excluded_types':dict(sorted(excluded.items()))}
 words=sorted(origins);assert words;expected_words=[{'id':i,'word':w,'book_occurrences':dict(origins[w])} for i,w in enumerate(words)];assert vocab['words']==expected_words and vocab['books']==stats;L=max(len(w) for w in words);assert L==vocab['maximum_projected_word_length']==res['reference_maximum_word_length'];assert res['reference_types']==len(words)
 # Direct alignment does not use primary signature/index functions.
 assert match('N',['e','e']) and match('V',['e','e']) and match('II',['e','e']) and not match('N',['e','i']) and match('II',['e','i'])
 assert not match('AB',['a','a']) and not match('AA',['a','o']) and not match('AI',['e','a'])
 bywidth=defaultdict(list)
 for i,w in enumerate(words):bywidth[sum(W.get(c,1) for c in w)].append(i)
 cache={}
 def candidates(us):
  k=tuple(us)
  if k not in cache:cache[k]=[i for i in bywidth[len(us)] if match(words[i],us)]
  return cache[k]
 cert=read(R/'experiments/yolo/gdt1259_paragraph_integer_balance/artifacts/CERTIFICATES.json');oldspec=read(R/'experiments/yolo/gdt1259_paragraph_integer_balance/src/SPEC.json');loci=sorted({g['locus'] for rr in cert.values() for p in rr for g in p['raw_groups']});assert all(not s.startswith(('f84','f116v.','f1r.')) for s in loci)
 source=oldspec['native_source'];pin=next(x['sha256'] for x in oldspec['inputs'] if x['path']==source);assert hashlib.sha256((R/source).read_bytes()).hexdigest()==pin
 columns=oldspec['columns'];cmd=['./vmanus-exp','query-tsv',source,'--selector','locus','--columns',','.join(columns)]+[x for locus in loci for x in ('--allow',locus)];call=subprocess.run(cmd,cwd=R,text=True,capture_output=True,check=True);original={}
 for g in csv.DictReader(io.StringIO('\n'.join(line for line in call.stdout.splitlines() if not line.startswith('GUARD_STATS '))),delimiter='\t'):
  key=(g['edition'],g['locus'],int(g['source_group_index']));assert key not in original;original[key]=g
 guard={'command':cmd,'source_sha256':pin,'output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest(),'selected_loci':len(loci),'guarded_rows':len(original)}
 stored_streams=read(B/'artifacts/STREAMS.json.gz');saved=read(B/'artifacts/CASES.json.gz');joins=0;spanchecks=0;decisions=0;unitcount=0
 for ed,packets in sorted(cert.items()):
  streams=[]
  for packet in packets:
   us=[];ptr=[];lines=defaultdict(list)
   for g in packet['raw_groups']:
    orig=original[(ed,g['locus'],int(g['source_group_index']))];assert g=={k:orig[k] for k in g};assert orig['kind']=='P' and orig['edition']==ed;assert orig['left_separator'] in oldspec['permitted_separators'] and orig['right_separator'] in oldspec['permitted_separators'];lines[int(orig['source_row_index'])].append(orig);joins+=1
    units=split(orig['ivtff_group_raw'])
    for j,u in enumerate(units):us.append(u);ptr.append({'id':f"{ed}|{orig['locus']}|G{int(orig['source_group_index']):03d}",'unit_offset':j})
   seq=sorted(lines);assert seq==list(range(seq[0],seq[-1]+1));assert seq==packet['paragraph']['source_rows']
   for ri,gs in lines.items():assert [int(g['source_group_index']) for g in gs]==list(range(1,int(gs[0]['source_group_count'])+1))
   assert lines[seq[0]][0]['paragraph_start']=='1' and lines[seq[-1]][0]['paragraph_end']=='1';assert [Counter(us)[u] for u in oldspec['working_signs']]==packet['paragraph']['counts'];streams.append({'id':packet['paragraph']['id'],'units':us,'pointers':ptr});unitcount+=len(us)
  assert streams==stored_streams[ed];records=[];detail=[]
  for marker in [u for u in U if u not in ('e','i')]:
   complete=[];segments=[];doubles=[]
   for snippet in streams:
    us=snippet['units'];left=-1
    for right in range(len(us)+1):
     if right<len(us) and us[right]!=marker:continue
     seg=us[left+1:right];whole=left!=-1 and right<len(us);r={'snippet':snippet['id'],'start':left+1,'stop':right,'complete':whole,'units':seg,'minimum_source_letters':lower(seg)};segments.append(r)
     if whole and not seg:doubles.append({'snippet':snippet['id'],'positions':[left,right],'pointers':[snippet['pointers'][left],snippet['pointers'][right]]})
     elif whole:
      ids=candidates(seg);complete.append(dict(r,candidate_ids=ids,candidate_count=len(ids)));spanchecks+=1
     left=right
   bad=[r for r in complete if not r['candidate_ids']];long=[r for r in segments if r['minimum_source_letters']>L];mx=max(r['minimum_source_letters'] for r in segments);good=not bad and not long
   records.append({'marker':marker,'adjacent_marker_pairs':len(doubles),'complete_nonempty_spans':len(complete),'locally_supported_spans':len(complete)-len(bad),'unsupported_spans':len(bad),'maximum_required_source_word_length':mx,'over_reference_length_segments':len(long),'strict_S_compatible':good and not doubles,'relaxed_R_compatible':good,'informative_complete_spans':bool(complete)})
   detail.append({'marker':marker,'complete_spans':complete,'hh_witnesses':doubles,'first_unsupported':bad[0] if bad else None,'first_overlength':long[0] if long else None,'maximum_length_witness':next(r for r in segments if r['minimum_source_letters']==mx)});decisions+=1
  assert detail==saved[ed];expected={'snippets':len(streams),'stream_units':sum(len(s['units']) for s in streams),'markers':records,'strict_S_survivors':[r['marker'] for r in records if r['strict_S_compatible']],'relaxed_R_survivors':[r['marker'] for r in records if r['relaxed_R_compatible']],'minimum_over_markers_of_required_maximum':min(r['maximum_required_source_word_length'] for r in records),'status':'REFERENCE_VOCABULARY_EXCLUDED_EVEN_SPACE_RUN_RELAXATION' if not any(r['relaxed_R_compatible'] for r in records) else 'NECESSARY_LOCAL_CANDIDATES_ONLY'};assert res['readers'][ed]==expected
 # All reference-word true examples, with a known key, independent direct matcher.
 others=[c for c in 'ABCDEFGHIKLMNOPQRSTVXYZ' if c not in W];key=dict(zip(others,[u for u in U if u not in ('a','e','i')]));checks=0
 for word in words:
  for style in range(3):
   us=[];j=0
   for c in word:
    if c in W:us.extend([('e' if style==0 or (style==2 and j%2==0) else 'i')]*W[c]);j+=1
    else:us.append(key[c])
   assert match(word,us) and lower(us)<=len(word);checks+=1
 assert checks==vocab['source_only_true_word_checks']==res['source_only_true_word_checks'];assert spanchecks==res['complete_span_checks']
 clips=0
 for n in range(1,4):
  for word in itertools.product(tuple(W),repeat=n):
   for styles in itertools.product('ei',repeat=n):
    us=[];intervals=[]
    for c,s in zip(word,styles):a=len(us);us.extend([s]*W[c]);intervals.append((a,len(us)))
    for a in range(len(us)+1):
     for b in range(a,len(us)+1):
      touched=sum(l<b and r>a for l,r in intervals) if a<b else 0;assert lower(us[a:b])<=touched;clips+=1
 out={'status':'PASS','guarded_original_group_joins':joins,'stream_units':unitcount,'marker_cases':decisions,'complete_span_candidate_sets':spanchecks,'source_only_true_word_checks':checks,'clipped_source_word_fixtures':clips,'method':'Guarded exact-locus source recollation and continuity; independent dynamic unit parsing, direct word alignment/partial bijection instead of signature buckets, DP letter bounds and source-word fixtures.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');(B/'artifacts/GUARD_RECEIPT.json').write_text(json.dumps(guard,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
