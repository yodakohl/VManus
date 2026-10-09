import collections,gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
SOURCE='experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET='experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
BANKS=['abcdefghijklmnopqrs','jklmnopqrstuvwxyzab','stuvwxyzabcdefghijk'];BOOKS=['b4','w1','bs1','gr1'];LOWER='abcdefghijklmnopqrstuvwxyz'
def home(c):return min((ord(c)-97)//9,2)
def encode(word,bank,rare):
 out=[]
 for c in word:
  if c in LOWER:
   if c not in BANKS[bank]:bank=home(c);out.append(19+bank)
   out.append(BANKS[bank].index(c))
  else:
   i=rare.index(c);a,b=divmod(i,19);out.extend([19,19,a,b])
 return out,bank

def decode(seq,bank,rare):
 original=bank;word='';i=0
 while i<len(seq):
  x=seq[i]
  if x==19 and i+1<len(seq) and seq[i+1]==19:
   assert i+3<len(seq) and 0<=seq[i+2]<19 and 0<=seq[i+3]<19
   j=19*seq[i+2]+seq[i+3];assert j<len(rare);word+=rare[j];i+=4
  elif x>=19:
   assert 19<=x<=21 and i+1<len(seq) and 0<=seq[i+1]<19
   bank=x-19;word+=BANKS[bank][seq[i+1]];i+=2
  else:assert 0<=x<19;word+=BANKS[bank][x];i+=1
 assert word and encode(word,original,rare)==(seq,bank)
 return word,bank

def fixtures():
 rare=['.','Ä'];samples=[]
 for bank in range(3):
  for word in ['as','tl','aA' .replace('A','Ä'),'s.s','abcdefghijklmnopqrstuvwxyz','Ä.']:
   w,end=encode(word,bank,rare);assert decode(w,bank,rare)==(word,end);samples.append({'word':word,'enter':bank,'output':w,'end':end})
 triples=[encode('as',b,rare)[0] for b in range(3)];assert len({tuple(x) for x in triples})==3
 assert encode('t',0,rare)[1]==2 and encode('l',2,rare)[1]==1
 malformed=[[20,20,0,0],[19,19,0],[19,19,18,18],[19,0],[]]
 for seq in malformed:
  try:decode(seq,0,rare)
  except (AssertionError,IndexError):pass
  else:raise AssertionError(seq)
 # Coalescence cannot increase types or reduce any top-k sum.
 for counts in [[9,7,4],[1]*12,[20,1,1,1]]:
  for i in range(len(counts)):
   for j in range(i+1,len(counts)):
    after=[x for k,x in enumerate(counts) if k not in [i,j]]+[counts[i]+counts[j]]
    for k in range(1,len(counts)+1):assert sum(sorted(after,reverse=True)[:k])>=sum(sorted(counts,reverse=True)[:k])
 return {'status':'PASS','roundtrips':samples,'three_as_forms':triples,'malformed_rejected':len(malformed),'claim':'Source-free arithmetic/canonicality checks, not a native fit.'}
def save(n,obj):(B/('artifacts/'+n+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 fixture=fixtures();source=json.loads((ROOT/SOURCE).read_text());targets=json.loads((ROOT/TARGET).read_text())['targets']
 rare=sorted({c for b in BOOKS for rec in source[b] for w in rec['words'] for c in w if c not in LOWER});assert len(rare)<=361,'SOURCE_CONTRACT_FAIL_TOO_MANY_RARE_CHARACTERS'
 limits={}
 for reader,t in targets.items():
  assert t['tokens']==8000;types=round(8000*t['type_ratio']);top=round(8000*t['top10_share']);assert abs(types/8000-t['type_ratio'])<1e-12 and abs(top/8000-t['top10_share'])<1e-12
  limits[reader]={'types_lower':types-400,'top10_upper':top+400,'native_types':types,'native_top10':top}
 traces={};freq={};books={}
 for book in BOOKS:
  rows=[];counts=collections.Counter();seen=0;switches=0
  for ri,rec in enumerate(source[book]):
   bank=0
   for wi,word in enumerate(rec['words']):
    assert isinstance(word,str) and word;start=bank;n_switch=0
    for ch in word:
     if ch in LOWER and ch not in BANKS[bank]:bank=home(ch);n_switch+=1
    sample=seen<8000;row={'recipe_index':ri,'word_index':wi,'word':word,'enter':start,'end':bank,'bank_changes':n_switch,'sample':sample};rows.append(row)
    if sample:counts[word,start]+=1;switches+=n_switch
    seen+=1
  assert seen>=8000 and sum(counts.values())==8000
  cells=[{'word':w,'enter':bank,'count':n} for (w,bank),n in sorted(counts.items())];T=len(cells);C=sum(sorted(counts.values(),reverse=True)[:10]);conditions={}
  for reader,lim in limits.items():
   a=T>=lim['types_lower'];c=C<=lim['top10_upper'];conditions[reader]={**lim,'types_not_excluded':a,'concentration_not_excluded':c,'not_excluded':a and c}
  traces[book]=rows;freq[book]=cells;books[book]={'recipes':len(source[book]),'source_words':seen,'sample':8000,'observed_word_entry_cells':T,'top10_cell_count':C,'top10_cell_share':C/8000,'sample_bank_changes':switches,'sample_enter_bank_counts':dict(sorted(collections.Counter(r['enter'] for r in rows if r['sample']).items())),'conditions':conditions,'not_excluded':all(c['not_excluded'] for c in conditions.values())}
 status='NECESSARY_CAPACITY_ONLY' if all(v['not_excluded'] for v in books.values()) else 'FIXED_OVERLAPPING_BANK_CAPACITY_FAIL'
 save('SPECIFICATION',{'banks':BANKS,'ordinary_source_alphabet':LOWER,'home_ranges':['a..i','j..r','s..z'],'quote_rare_characters':rare,'payload_signs':19,'selector_signs':3,'total_signs':22,'quote':'S0 S0 then2base19digits; no bank change','glyph_mapping':'UNASSIGNED','source_is_exposed':True});save('FIXTURES',fixture);save('CELLS',freq)
 (B/'artifacts/SOURCE_TRACES.json.gz').write_bytes(gzip.compress(json.dumps(traces,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 result={'status':status,'books':books,'limits':limits,'rare_characters':len(rare),'source_recipes':sum(len(source[b]) for b in BOOKS),'source_words':sum(len(v) for v in traces.values()),'scope':'Necessary optimistic equality-frequency bound only for fixed source/state/wholeword grouping; no full rendered writer or native reading.'};save('RESULT',result)
 print(json.dumps({'status':status,'rare_characters':len(rare),'limits':limits,'books':{b:{k:v for k,v in z.items() if k!='conditions'} for b,z in books.items()}},indent=2))
if __name__=='__main__':main()
