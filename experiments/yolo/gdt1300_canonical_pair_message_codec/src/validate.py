"""Independent model/count rebuild and inverse; does not import producer/codec."""
import gzip,hashlib,json,re,math,itertools,random
from collections import Counter
from functools import lru_cache
from pathlib import Path
import independent_metrics as im
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts';SIGNS=im.SIGNS
END='\0'
def load(n):
 p=A/n;return json.loads(gzip.decompress(p.read_bytes()) if n.endswith('.gz') else p.read_text())
def digest(data):return hashlib.sha256(data).hexdigest()
def nat(s):return tuple((1,int(x)) if x.isdigit() else (0,x) for x in re.split(r'(\d+)',s))
def huff(weights):
 forest=[(w,i,{i:''}) for i,w in weights.items()]
 while len(forest)>1:
  forest.sort(key=lambda n:(n[0],n[1]));a,b=forest[:2];forest=forest[2:]
  joined={i:'0'+c for i,c in a[2].items()};joined.update({i:'1'+c for i,c in b[2].items()});forest.append((a[0]+b[0],min(a[1],b[1]),joined))
 return forest[0][2]
def close(a,b):
 if isinstance(a,dict):assert set(a)==set(b);[close(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b);[close(x,y) for x,y in zip(a,b)]
 elif isinstance(a,float):assert abs(a-b)<1e-9,(a,b)
 else:assert a==b,(a,b)
def wrap(words):
 lines=[];row=[];used=0
 for w in words:
  size=len(im.parse(w));assert size<=26
  if row and used+1+size>48:lines.append(row);row=[];used=0
  used+=size+bool(row);row.append(w)
 if row:lines.append(row)
 return lines
def met(seg):
 d=im.independent(seg);words=[]
 for line in seg:words.extend(line)
 gs=[im.parse(w) for w in words[:8000]];pairs=Counter((a,b) for w in gs for a,b in zip(w,w[1:]));q=sum(n for (a,b),n in pairs.items() if a=='q')
 d.update(q_followed_o=pairs['q','o']/q if q else None,q_count=sum(w.count('q') for w in gs),y_final=sum(w[-1]=='y' for w in gs)/8000);return d
def check_gates(observed,target,row):
 margins={'mean_length':('rel',.2),'sd_length':('rel',.25),'top10_share':('abs',.05),'type_ratio':('abs',.05),'conditional_entropy':('abs',.3),'exact_repeat':('abs',.01),'edit1_repeat':('abs',.01),'first_last_js':('abs',.12),'q_followed_o':('abs',.03),'q_count':('rel',.25),'y_final':('abs',.05),'glyph_entropy':('abs',.15),'word_entropy':('abs',.3)}
 expected={}
 for k,(kind,tol) in margins.items():
  delta=None if observed[k] is None or target[k] is None else abs(observed[k]-target[k]);limit=tol*target[k] if kind=='rel' else tol;expected[k]=delta is not None and delta<=limit
  assert row['gates'][k]['within']==expected[k]
 expected['edit1_repeat_original_loose']=abs(observed['edit1_repeat']-target['edit1_repeat'])<=.03
 tv=sum(abs(observed['length_counts'].get(k,0)-target['length_counts'].get(k,0)) for k in observed['length_counts'].keys()|target['length_counts'].keys())/16000
 pa=observed['glyph_counts'];pb=target['glyph_counts'];sa=sum(pa.values());sb=sum(pb.values());mixture={k:(pa.get(k,0)/sa+pb.get(k,0)/sb)/2 for k in pa.keys()|pb.keys()};h=lambda c:-sum(v*math.log2(v) for v in c.values() if v)
 js=h(mixture)-(h({k:v/sa for k,v in pa.items()})+h({k:v/sb for k,v in pb.items()}))/2
 expected['length_tv']=tv<=.2;expected['glyph_js']=js<=.1
 assert set(expected)==set(row['gates'])
 for k,v in expected.items():assert row['gates'][k]['within']==v
 assert row['passed']==sum(expected.values()) and row['joint']==all(expected.values())
 basic=list(margins)[:8];basic.remove('edit1_repeat');basic+=['edit1_repeat_original_loose','length_tv','glyph_js'];assert row['basic10_pass']==all(expected[k] for k in basic)
def main():
 spec=json.loads((B/'src/SPEC.json').read_text());model=load('MODEL.json');result=load('RESULT.json');seal=load('MODEL_SEAL.json');assert seal['model_sha256']==digest((A/'MODEL.json').read_bytes())
 for p,h in spec['input_hashes'].items():assert digest((ROOT/p).read_bytes())==h
 raw=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));src=json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());texts={b:'\n'.join(' '.join(r['words']) for r in src[b]) for b in spec['books']}
 train=[r for r in raw['ZL3b'] if int(re.match(r'f(\d+)',r['page'])[1])%2];assert model['train_groups']==len(train) and model['train_ids_sha256']==digest('\n'.join(r['id'] for r in train).encode())
 pairc=Counter()
 for r in train:
  units=[SIGNS.index(x) for x in im.parse(r['ivtff_group_raw'])];assert [SIGNS[i] for i in units]==r['units'];pairc.update(zip(units,units[1:]))
 pairs=sorted(pairc,key=lambda p:(-pairc[p],p))[:16];assert model['pairs']==[list(p) for p in pairs];assert model['pair_counts']==[pairc[p] for p in pairs]
 vocab=[[i] for i in range(22)]+[list(p) for p in pairs];assert vocab==model['vocabulary'];pidx={p:22+i for i,p in enumerate(pairs)}
 @lru_cache(None)
 def parse_tokens(word):
  units=tuple(SIGNS.index(g) for g in im.parse(word))
  @lru_cache(None)
  def routes(i,prev):
   if i==len(units):return ((),)
   x=units[i]
   if prev>=0 and (prev,x) in pidx:return ()
   choices=[(x,1)]
   if tuple(units[i:i+2]) in pidx:choices.append((pidx[tuple(units[i:i+2])],2))
   answers=[]
   for t,n in choices:
    for tail in routes(i+n,x if n==1 else -1):answers.append((t,)+tail)
   return tuple(answers)
  found=routes(0,-1);assert len(found)==1;return found[0]
 roles={k:[0]*len(vocab) for k in model['role_counts']};tc=Counter()
 def cl(t):
  g=SIGNS[vocab[t][-1]];return '0' if g in spec['class0'] else '1' if g in spec['class1'] else 'U'
 for r in train:
  ids=parse_tokens(r['ivtff_group_raw']);T=len(ids);assert T<=13;tc[T]+=1
  for j,t in enumerate(ids):
   if T==1:roles['SINGLE'][t]+=1
   elif j==0:roles['HEAD'][t]+=1
   else:
    ph='TAIL' if j==T-1 else 'MIDDLE';roles[ph+'_U'][t]+=1;classid=cl(ids[j-1])
    if classid!='U':roles[ph+'_'+classid][t]+=1
 assert roles==model['role_counts'];assert {str(t):tc[t] for t in range(1,14)}==model['T_counts'];assert {str(k):v for k,v in huff({t:2*tc[t]+1 for t in range(1,14)}).items()}==model['T_codes']
 codebooks={};unique=set()
 for key,index in model['contexts'].items():
  if '|' not in key:phase=key;prev=None;role=phase;allowed=list(range(len(vocab)))
  else:
   phase,value=key.split('|');prev=int(value);role=phase+'_'+cl(prev);allowed=[t for t in range(len(vocab)) if len(vocab[prev])==2 or (vocab[prev][0],vocab[t][0]) not in pidx]
  codes={str(k):v for k,v in huff({t:2*roles[role][t]+1 for t in allowed}).items()};assert codes==model['tables'][index];codebooks[key]=codes;unique.add(tuple(sorted(codes.items())))
 assert len(unique)==len(model['tables']) and sum(len(c) for c in unique)==model['output_lookup_entries']
 counts=Counter(''.join(texts.values()));assert END not in counts;counts[END]=4;assert dict(counts)==model['source_counts'];chars=sorted(counts);sc=huff({i:counts[c] for i,c in enumerate(chars)});assert {c:sc[i] for i,c in enumerate(chars)}==model['source_codes']
 if not result['capacity']['pass']:
  assert model['output_lookup_entries']>1200 and result['status']=='OUTPUT_TABLE_COST_STOP';checks={'status':'PASS','scope':'independent model/cost reconstruction only'}
 else:
  textsout=load('SYNTHETIC_TEXTS.json.gz');targets=load('TARGETS.json.gz');decoded=0;measurements=0
  def recovered_bits(words):
   bits=[]
   for w in words:
    ids=parse_tokens(w);T=len(ids);assert 1<=T<=13;bits.append(model['T_codes'][str(T)])
    for j,t in enumerate(ids):
     phase='SINGLE' if T==1 else 'HEAD' if j==0 else 'TAIL' if j==T-1 else 'MIDDLE';key=phase if j==0 else phase+'|'+str(ids[j-1]);bits.append(codebooks[key][str(t)])
   return ''.join(bits)
  # Exact expected source bitstream and minimal completion word are checked
  # without invoking the producer's encoder or decoder.
  for book,text in texts.items():
   words=textsout[book];bits=recovered_bits(words);expected=''.join(model['source_codes'][c] for c in text+END);assert bits.startswith(expected) and set(bits[len(expected):])<=set('0');assert len(recovered_bits(words[:-1]))<len(expected)
   receipt=result['books'][book]['receipt'];assert receipt['source_bits']==len(expected) and receipt['padding_bits']==len(bits)-len(expected) and receipt['source_sha256']==digest(text.encode());decoded+=1
   measured=met(wrap(words));close(measured,result['books'][book]['metrics']);measurements+=1
  for ex in load('EXAMPLES.json'):
   if ex.get('status')=='UNSUPPORTED_EXAMPLE':assert not set(ex['plaintext'])<=set(model['source_codes']);continue
   bits=recovered_bits(ex['synthetic_written_words']);expected=''.join(model['source_codes'][c] for c in ex['plaintext']+END);assert bits.startswith(expected) and set(bits[len(expected):])<=set('0');assert len(recovered_bits(ex['synthetic_written_words'][:-1]))<len(expected)
  for ed,saved in targets.items():
   rows=sorted((r for r in raw[ed] if int(re.match(r'f(\d+)',r['page'])[1])%2==0),key=lambda r:(nat(r['page']),nat(r['locus']),int(r['source_group_index'])));assert [r['id'] for r in rows[:8000]]==saved['first8000_ids']
   lines=[];part=[];prev=None
   for r in rows:
    link=prev is not None and (r['page'],r['locus'])==(prev['page'],prev['locus']) and int(r['source_group_index'])-int(prev['source_group_index'])==1
    if part and not link:lines.append(part);part=[]
    part.append(r['ivtff_group_raw']);prev=r
   if part:lines.append(part)
   close(met(lines),saved['metrics']);measurements+=1
  fair=result['fair_bits'];fb=recovered_bits(textsout['FAIR_BITS_CONTROL']);rng=random.Random(1300);expected=''.join(str(rng.getrandbits(1)) for _ in range(len(fb)));assert fb==expected and digest(fb.encode())==fair['bit_sha256'];close(met(wrap(textsout['FAIR_BITS_CONTROL'])),fair['metrics']);measurements+=1
  for book in spec['books']:
   for ed,t in targets.items():check_gates(result['books'][book]['metrics'],t['metrics'],result['books'][book]['comparison'][ed])
  for ed,t in targets.items():check_gates(fair['metrics'],t['metrics'],fair['comparison'][ed])
  joint=all(v['joint'] for b in result['books'].values() for v in b['comparison'].values());assert result['status']==('COMPATIBLE_SYNTHETIC_CONTROL_NOT_READING' if joint else 'FIXED_CODEC_SCREEN_FAILED')
  checks={'status':'PASS','scope':'Independent odd-TRAIN key reconstruction, canonical parse search, complete source bit recovery, padding and separate metric formulas; not semantic or historical validation','source_books_recovered':decoded,'metric_decks':measurements,'comparison_decks':15,'native_key_identified':False}
 (A/'VALIDATION.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks))
if __name__=='__main__':main()
