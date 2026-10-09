import gzip,hashlib,itertools,json,random,re
from collections import Counter
from pathlib import Path
import codec as c
import metrics as m
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2];A=B/'artifacts'
def save(name,x):
 p=A/name;data=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()
 p.write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def natural(s):return tuple((1,int(p)) if p.isdigit() else (0,p) for p in re.split(r'(\d+)',s))
def leaf(page):return int(re.match(r'f(\d+)',page)[1])
def streams(source):return {book:'\n'.join(' '.join(r['words']) for r in source[book]) for book in ['b4','w1','bs1','gr1']}
def segments(rows):
 rows=sorted(rows,key=lambda r:(natural(r['page']),natural(r['locus']),int(r['source_group_index'])));out=[];part=[];last=None;ids=[]
 for r in rows:
  linked=last and r['page']==last['page'] and r['locus']==last['locus'] and int(r['source_group_index'])==int(last['source_group_index'])+1
  if part and not linked:out.append(part);part=[]
  part.append(r['ivtff_group_raw']);ids.append(r['id']);last=r
 if part:out.append(part)
 return out,ids
def wrap(words):
 out=[];line=[];width=0
 for w in words:
  n=len(c.parse(w));assert n<=26
  if line and width+1+n>48:out.append(line);line=[];width=0
  width+=n+bool(line);line.append(w)
 if line:out.append(line)
 return out
def compare(observed,target):
 base=m.compare(observed,target);gates={k:dict(v) for k,v in base['diagnostics'].items()};gates['edit1_repeat']['limit']=.01;gates['edit1_repeat']['within']=gates['edit1_repeat']['difference']<=.01
 for key,tol,relative in [('q_followed_o',.03,False),('q_count',.25,True),('y_final',.05,False),('glyph_entropy',.15,False),('word_entropy',.30,False)]:
  diff=None if observed[key] is None or target[key] is None else abs(observed[key]-target[key]);lim=tol*target[key] if relative else tol
  gates[key]={'model':observed[key],'target':target[key],'difference':diff,'limit':lim,'within':diff is not None and diff<=lim}
 # Ten old gates, of which edit1 is tightened, plus five extra gates =15
 # distinct gates; the old protocol calls these16conditions when counting
 # both loose and strict edit1. Keep both explicit, never duplicate successes.
 gates['edit1_repeat_original_loose']=base['diagnostics']['edit1_repeat']
 return {'basic10_pass':base['joint_screen'],'passed':sum(x['within'] for x in gates.values()),'total':len(gates),'joint':all(x['within'] for x in gates.values()),'gates':gates}
def fixtures(spec):
 cases=0
 allpairs=list(itertools.product(range(2),repeat=2))
 for mask in range(16):
  pairs=[list(p) for i,p in enumerate(allpairs) if mask>>i&1];vocab={i:[i] for i in range(22)};vocab.update({22+i:p for i,p in enumerate(pairs)});allowed_ids=[0,1]+list(range(22,22+len(pairs)));pairset={tuple(p) for p in pairs}
  for n in range(1,5):
   for ids in itertools.product(allowed_ids,repeat=n):
    units=[u for t in ids for u in vocab[t]];legal=all(len(vocab[a])==2 or (vocab[a][0],vocab[b][0]) not in pairset for a,b in zip(ids,ids[1:]));assert (c.greedy(units,pairs)==list(ids))==legal;cases+=1
 toy=[]
 for n in range(1,5):
  for units in itertools.product(c.SIGNS[:3],repeat=n):toy.append({'id':'toy'+str(len(toy)),'units':list(units)})
 small=dict(spec,pairs=4);model=c.build_model(toy,{'toy':'abba a b'},small);co=c.Codec(model);roundtrips=0
 for n in range(5):
  for chars in itertools.product('ab',repeat=n):
   text=''.join(chars);w,_=co.encode(text);assert co.decode(w)==text;roundtrips+=1
 w,_=co.encode('abba');extra=co.word(lambda:'0')
 assert co.bits([extra]) and set(co.bits([extra]))=={'0'}
 try:co.decode(w+[extra])
 except ValueError:pass
 else:raise AssertionError('extra zero word accepted')
 return {'status':'PASS','greedy_sequence_cases':cases,'source_roundtrips_including_empty':roundtrips,'extra_all_zero_word_rejected':True,'native_data_used':False}
def main():
 spec=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 assert not (A/'RESULT.json').exists(),'Do not overwrite empirical result'
 save('FIXTURES.json',fixtures(spec))
 source=json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());texts=streams(source)
 native=json.loads(gzip.decompress((ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()))
 for ed,rows in native.items():
  for r in rows:assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE' and not r['page'].startswith('f84') and r['page']!='f116v'
 train=[r for r in native['ZL3b'] if leaf(r['page'])%2];model=c.build_model(train,texts,spec);save('MODEL.json',model)
 save('MODEL_SEAL.json',{'stage':'before source generation or even-leaf statistics','model_sha256':c.sha((A/'MODEL.json').read_bytes()),'train_groups':len(train),'train_physical_leaves':sorted({leaf(r['page']) for r in train}),'no_whole_word_dictionary':True})
 capacity={'output_lookup_entries':model['output_lookup_entries'],'unique_output_tables':model['unique_output_tables'],'cap':1200,'source_table_entries':model['source_table_entries'],'length_table_entries':13,'pair_entries':16,'class_entries':22,'pass':model['output_lookup_entries']<=1200};save('CAPACITY.json',capacity)
 if not capacity['pass']:save('RESULT.json',{'status':'OUTPUT_TABLE_COST_STOP','capacity':capacity});print(json.dumps(capacity));return
 co=c.Codec(model);targets={};samples={}
 for ed in spec.get('readers',['ZL3b','IT2a','RF1b']):
  held=[r for r in native[ed] if leaf(r['page'])%2==0];seg,ids=segments(held);assert len(ids)>=8000;targets[ed]=m.measure(seg);samples[ed]={'whole_groups':len(held),'physical_leaves':len({leaf(r['page']) for r in held}),'first8000_ids':ids[:8000],'metrics':targets[ed]}
 save('TARGETS.json.gz',samples)
 outputs={};books={}
 for book,text in texts.items():
  words,receipt=co.encode(text);assert co.decode(words)==text;assert len(words)>=8000;lines=wrap(words);met=m.measure(lines);outputs[book]=words
  books[book]={'receipt':receipt,'full_source_roundtrip':True,'metrics':met,'comparison':{ed:compare(met,t) for ed,t in targets.items()}}
 examples=[]
 for text in spec['hand_examples']:
  if not set(text)<=set(model['source_codes']):examples.append({'plaintext':text,'status':'UNSUPPORTED_EXAMPLE'});continue
  words,receipt=co.encode(text);assert co.decode(words)==text;examples.append({'plaintext':text,'synthetic_written_words':words,'receipt':receipt,'inverse_exact':True,'native_meanings_assigned':False})
 rng=random.Random(spec['fair_bit_control_seed']);fairbits=[]
 def bit():
  v=str(rng.getrandbits(1));fairbits.append(v);return v
 fw=[co.word(bit) for _ in range(8000)];bits=''.join(fairbits);assert co.bits(fw)==bits;fmet=m.measure(wrap(fw));outputs['FAIR_BITS_CONTROL']=fw
 fair={'not_a_source_language_message':True,'seed':1300,'consumed_bits':len(bits),'bit_sha256':c.sha(bits.encode()),'bit_layer_inverse_exact':True,'metrics':fmet,'comparison':{ed:compare(fmet,t) for ed,t in targets.items()}}
 joint=all(v['joint'] for b in books.values() for v in b['comparison'].values());status='COMPATIBLE_SYNTHETIC_CONTROL_NOT_READING' if joint else 'FIXED_CODEC_SCREEN_FAILED'
 save('SYNTHETIC_TEXTS.json.gz',outputs);save('EXAMPLES.json',examples);save('RESULT.json',{'status':status,'capacity':capacity,'books':books,'fair_bits':fair,'source_control_count':4,'reader_count':3,'confirmed_words':0,'scope':'Fixed exposed train/even-leaf held engineering screen only; no native key, historical attribution or meaning.'})
 print(json.dumps({'status':status,'capacity':capacity,'books':{b:{'words':r['receipt']['word_count'],'padding':r['receipt']['padding_bits'],'passes':{ed:v['passed'] for ed,v in r['comparison'].items()}} for b,r in books.items()},'fair_passes':{ed:v['passed'] for ed,v in fair['comparison'].items()}},indent=2))
if __name__=='__main__':main()
