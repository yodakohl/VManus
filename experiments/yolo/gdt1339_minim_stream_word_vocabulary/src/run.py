from pathlib import Path
from collections import Counter,defaultdict
import gzip,hashlib,itertools,json,math,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());W={'I':1,'N':2,'M':3,'V':2};LETTERS='ABCDEFGHIKLMNOPQRSTVXYZ';PAT=re.compile('|'.join(sorted(U,key=lambda x:(-len(x),x))))
def read(p):return json.loads(p.read_text())
def save(name,x):
 raw=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def equality(items):
 d={};out=[]
 for u in items:
  if u not in d:d[u]=len(d)
  out.append(d[u])
 return tuple(out)
def source_parts(word):
 anchors=[];slots=[[]]
 for c in word:
  if c in W:slots[-1].append(W[c])
  else:anchors.append(c);slots.append([])
 return (equality(anchors),tuple(map(sum,slots))),slots

def target_parts(units):
 anchors=[];slots=[[]]
 for u in units:
  if u in ('e','i'):slots[-1].append(u)
  else:anchors.append(u);slots.append([])
 return (equality(anchors),tuple(map(len,slots))),slots

def colors(weights,units):
 i=0
 for n in weights:
  block=units[i:i+n]
  if len(block)!=n or len(set(block))!=1 or block[0] not in ('e','i'):return False
  i+=n
 return i==len(units)
def lower(units):
 total=0
 for u,g in itertools.groupby(units):
  n=len(list(g));total+=(n+2)//3 if u in ('e','i') else n
 return total

def vocabulary():
 raw=read(R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json');origins=defaultdict(Counter);summary={}
 for book in ('b4','w1','bs1','gr1'):
  retained=0;excluded=Counter();total=0
  for rec in raw[book]:
   for token in rec['words']:
    total+=1
    if not re.fullmatch('[A-Za-z]+',token):excluded[token]+=1;continue
    word=token.upper().replace('J','I').replace('U','V').replace('W','VV');assert set(word)<=set(LETTERS);origins[word][book]+=1;retained+=1
  summary[book]={'stored_tokens':total,'admitted_tokens':retained,'excluded_tokens':sum(excluded.values()),'excluded_types':dict(sorted(excluded.items()))}
 words=sorted(origins);assert words,'Empty reference vocabulary';return words,origins,summary

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 words,origins,source_summary=vocabulary();parts={};index=defaultdict(list)
 for i,w in enumerate(words):sig,slots=source_parts(w);parts[i]=slots;index[sig].append(i)
 cache={}
 def candidates(units):
  key=tuple(units)
  if key not in cache:
   sig,slots=target_parts(units);cache[key]=[i for i in index.get(sig,[]) if all(colors(ws,us) for ws,us in zip(parts[i],slots))]
  return cache[key]
 # Source-only true examples are checked before the native packet is opened.
 checks=0;h='a';non=[u for u in U if u not in ('e','i',h)];key=dict(zip([c for c in LETTERS if c not in W],non));assert len(key)==19
 for i,w in enumerate(words):
  for style in range(3):
   encoded=[];j=0
   for c in w:
    if c in W:encoded += [('e' if style==0 or (style==2 and j%2==0) else 'i')]*W[c];j+=1
    else:encoded.append(key[c])
   assert i in candidates(encoded);assert lower(encoded)<=len(w);checks+=1
 assert not colors([2],['e','i']) and colors([1,1],['e','i']) and colors([2],['e','e'])
 assert source_parts('IN')[0]==source_parts('IV')[0] and source_parts('II')[0]==source_parts('N')[0]
 cache.clear();data=read(R/'experiments/yolo/gdt1259_paragraph_integer_balance/artifacts/CERTIFICATES.json');streams={};out={};cases={};L=max(map(len,words));lookup_calls=0
 for ed,rows in sorted(data.items()):
  snippets=[]
  for row in rows:
   units=[];pointers=[]
   for g in row['raw_groups']:
    us=PAT.findall(g['ivtff_group_raw']);assert ''.join(us)==g['ivtff_group_raw']
    for j,u in enumerate(us):units.append(u);pointers.append({'id':f"{ed}|{g['locus']}|G{int(g['source_group_index']):03d}",'unit_offset':j})
   old_order=read(R/'experiments/yolo/gdt1259_paragraph_integer_balance/src/SPEC.json')['working_signs'];assert [Counter(units)[u] for u in old_order]==row['paragraph']['counts'];snippets.append({'id':row['paragraph']['id'],'units':units,'pointers':pointers})
  streams[ed]=snippets;records=[];details=[]
  for marker in [u for u in U if u not in ('e','i')]:
   complete=[];segments=[];doubles=[]
   for snippet in snippets:
    units=snippet['units'];pos=[j for j,u in enumerate(units) if u==marker];bounds=[-1]+pos+[len(units)]
    for k,(left,right) in enumerate(zip(bounds,bounds[1:])):
     us=units[left+1:right];whole=left>=0 and right<len(units);rec={'snippet':snippet['id'],'start':left+1,'stop':right,'complete':whole,'units':us,'minimum_source_letters':lower(us)};segments.append(rec)
     if whole and not us:doubles.append({'snippet':snippet['id'],'positions':[left,right],'pointers':[snippet['pointers'][left],snippet['pointers'][right]]})
     if whole and us:
      ids=candidates(us);lookup_calls+=1;complete.append(dict(rec,candidate_ids=ids,candidate_count=len(ids)))
   bad=[x for x in complete if not x['candidate_count']];long=[x for x in segments if x['minimum_source_letters']>L];mx=max(x['minimum_source_letters'] for x in segments);relaxed=not bad and not long
   record={'marker':marker,'adjacent_marker_pairs':len(doubles),'complete_nonempty_spans':len(complete),'locally_supported_spans':len(complete)-len(bad),'unsupported_spans':len(bad),'maximum_required_source_word_length':mx,'over_reference_length_segments':len(long),'strict_S_compatible':relaxed and not doubles,'relaxed_R_compatible':relaxed,'informative_complete_spans':bool(complete)};records.append(record);details.append({'marker':marker,'complete_spans':complete,'hh_witnesses':doubles,'first_unsupported':bad[0] if bad else None,'first_overlength':long[0] if long else None,'maximum_length_witness':next(x for x in segments if x['minimum_source_letters']==mx)})
  out[ed]={'snippets':len(snippets),'stream_units':sum(len(s['units']) for s in snippets),'markers':records,'strict_S_survivors':[r['marker'] for r in records if r['strict_S_compatible']],'relaxed_R_survivors':[r['marker'] for r in records if r['relaxed_R_compatible']],'minimum_over_markers_of_required_maximum':min(r['maximum_required_source_word_length'] for r in records),'status':'REFERENCE_VOCABULARY_EXCLUDED_EVEN_SPACE_RUN_RELAXATION' if not any(r['relaxed_R_compatible'] for r in records) else 'NECESSARY_LOCAL_CANDIDATES_ONLY'};cases[ed]=details;print(ed,json.dumps({k:v for k,v in out[ed].items() if k!='markers'}),flush=True)
 save('REFERENCE_VOCABULARY.json',{'words':[{'id':i,'word':w,'book_occurrences':dict(origins[w])} for i,w in enumerate(words)],'books':source_summary,'maximum_projected_word_length':L,'source_only_true_word_checks':checks,'source_status':'Reference inventory only; nonletters omitted from vocabulary, not claimed encoded full books.'})
 save('STREAMS.json.gz',streams);save('CASES.json.gz',cases);save('RESULT.json',{'status':'FIXED_VOCABULARY_LOCAL_STREAM_SCREEN','reference_types':len(words),'reference_maximum_word_length':L,'source_only_true_word_checks':checks,'complete_span_checks':lookup_calls,'readers':out,'scope':'Local compatibility under fixed new stream/vocabulary contract; no shared key, language identification or word meaning.'})
if __name__=='__main__':main()
