import collections,gzip,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2]
def main():
 lock=json.loads((P/'src/REGISTRATION_LOCK.json').read_text())
 for f,h in lock['hashes'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h
 source=json.loads((R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());targets=json.loads((R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets'];res=json.loads((P/'artifacts/RESULT.json').read_text());spec=json.loads((P/'artifacts/SPECIFICATION.json').read_text());traces=json.loads(gzip.decompress((P/'artifacts/SOURCE_TRACES.json.gz').read_bytes()));stored=json.loads((P/'artifacts/CELLS.json').read_text())
 abc='abcdefghijklmnopqrstuvwxyz';rows=[''.join(abc[(9*b+j)%26] for j in range(19)) for b in range(3)];members=[set(row) for row in rows];homes=[set(abc[:9]),set(abc[9:18]),set(abc[18:])]
 assert spec['banks']==rows and spec['ordinary_source_alphabet']==abc and spec['glyph_mapping']=='UNASSIGNED'
 books=['b4','w1','bs1','gr1'];rare=sorted(set(''.join(w for b in books for rec in source[b] for w in rec['words']))-set(abc));assert spec['quote_rare_characters']==rare and len(rare)==res['rare_characters']<=361
 limits={r:{'native_types':round(t['type_ratio']*t['tokens']),'native_top10':round(t['top10_share']*t['tokens']),'types_lower':round((t['type_ratio']-.05)*t['tokens']),'top10_upper':round((t['top10_share']+.05)*t['tokens'])} for r,t in targets.items()}
 assert all(t['tokens']==8000 for t in targets.values());assert limits==res['limits'];events=0;allok=True
 for book in books:
  rebuilt=[];counts=collections.Counter();hist=collections.Counter();changes=0
  for ri,rec in enumerate(source[book]):
   current=0
   for wi,word in enumerate(rec['words']):
    enter=current;switch=0
    for char in word:
     if char in abc and char not in members[current]:
      current=next(k for k,h in enumerate(homes) if char in h);assert char in members[current];switch+=1
    sample=len(rebuilt)<8000
    rebuilt.append({'recipe_index':ri,'word_index':wi,'word':word,'enter':enter,'end':current,'bank_changes':switch,'sample':sample})
    if sample:counts[(word,enter)]+=1;hist[enter]+=1;changes+=switch
  assert rebuilt==traces[book];events+=len(rebuilt);assert sum(counts.values())==8000
  assert stored[book]==[{'word':w,'enter':e,'count':n} for (w,e),n in sorted(counts.items())]
  cells=len(counts);top=sum(n for _,n in counts.most_common(10));br=res['books'][book];ok=True
  assert br['observed_word_entry_cells']==cells and br['top10_cell_count']==top and br['top10_cell_share']==top/8000
  assert br['source_words']==len(rebuilt) and br['recipes']==len(source[book]) and br['sample']==8000
  assert br['sample_bank_changes']==changes and br['sample_enter_bank_counts']=={str(k):v for k,v in sorted(hist.items())}
  for reader,lim in limits.items():
   first=cells>=lim['types_lower'];second=top<=lim['top10_upper'];actual={**lim,'types_not_excluded':first,'concentration_not_excluded':second,'not_excluded':first and second};assert br['conditions'][reader]==actual;ok &=first and second
  assert br['not_excluded']==ok;allok &=ok
 assert res['source_words']==events and res['source_recipes']==sum(len(source[b]) for b in books)
 assert res['status']==('NECESSARY_CAPACITY_ONLY' if allok else 'FIXED_OVERLAPPING_BANK_CAPACITY_FAIL')
 # Independent interpretation of saved source-free fixtures; no runner import.
 fixtures=json.loads((P/'artifacts/FIXTURES.json').read_text());toyrare=['.','Ä']
 for e in fixtures['roundtrips']:
  seq=list(e['output']);state=e['enter'];decoded=[];i=0
  while i<len(seq):
   if seq[i:i+2]==[19,19]:
    a,b=seq[i+2:i+4];assert a<19 and b<19;decoded.append(toyrare[a*19+b]);i+=4
   elif seq[i]>=19:
    destination=seq[i]-19;c=rows[destination][seq[i+1]]
    assert c not in members[state] and c in homes[destination];state=destination;decoded.append(c);i+=2
   else:decoded.append(rows[state][seq[i]]);i+=1
  assert ''.join(decoded)==e['word'] and state==e['end']
 assert fixtures['three_as_forms']==[[0,18],[17,9],[8,0]]
 # Independent top-k coarsening check over all set partitions of small cells.
 partitions=0
 def assignments(n,prefix=()):
  if len(prefix)==n:yield prefix;return
  for k in range(1+max(prefix,default=-1)+1):yield from assignments(n,prefix+(k,))
 for values in [[9,7,4],[5,4,3,2,1],[2,2,2,2]]:
  for a in assignments(len(values)):
   merged=collections.Counter()
   for key,value in zip(a,values):merged[key]+=value
   assert len(merged)<=len(values)
   for k in range(1,len(values)+1):assert sum(sorted(merged.values(),reverse=True)[:k])>=sum(sorted(values,reverse=True)[:k])
   partitions+=1
 out={'status':'PASS','source_word_state_traces':events,'sampled_events':32000,'books':4,'fixed_target_readings':3,'small_cell_partitions_checked':partitions,'scope':'Independent state/cell/gate reconstruction and source-free quote examples; no complete source glyph roundtrip or native meaning claim.'}
 (P/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
