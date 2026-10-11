from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def accepts(w,heads):
 ok=[False]*(len(w)+2);ok[len(w)]=True
 for i in range(len(w)-1,-1,-1):ok[i]=ok[i+2] if w[i] in heads else ok[i+1]
 return ok[0]
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');tables=read(B/'artifacts/HEAD_SETS.json');inventories=read(B/'artifacts/MINIMUM_HEAD_FREE_TYPES.json');res=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;decisions=0
 pattern=re.compile('|'.join(sorted(U,key=lambda s:(-len(s),s))))
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set()
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert pattern.findall(g[2])==r['units'];assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1
  assert seen==set(byid)
  grouped={}
  for row in rows:grouped.setdefault(tuple(row['units']),[]).append(row)
  words=sorted(grouped);expected=[];compatible=[]
  for heads in itertools.combinations(U,3):
   bad=next((w for w in words if not accepts(w,heads)),None);entry={'heads':list(heads),'status':'EXCLUDED_ORPHAN_HEAD' if bad is not None else 'COMPATIBLE_RELAXED_PREFIX'}
   if bad is not None:entry.update(first_failing_units=list(bad),witness=min(grouped[bad],key=lambda r:r['id']))
   else:
    free=[w for w in words if all(unit not in heads for unit in w)];entry.update(head_free_occurrences=sum(len(grouped[w]) for w in free),head_free_types=len(free));compatible.append(entry)
   expected.append(entry)
  assert tables[ed]==expected;decisions+=len(expected)
  best=min(compatible,key=lambda r:(r['head_free_occurrences'],r['heads'])) if compatible else None
  result={'groups':len(rows),'types':len(words),'head_sets':1540,'compatible_head_sets':len(compatible),'minimum_identical_source_pair_count':best['head_free_occurrences'] if best else None,'minimum_identical_source_pair_fraction':best['head_free_occurrences']/len(rows) if best else None,'selected_minimizing_heads':best['heads'] if best else None,'status':'SAME_SOURCE_PAIR_LOWER_BOUND_ONLY' if best else 'EXCLUDED_RELAXED_PREFIX_CARRIER'}
  assert res['readers'][ed]==result
  assert inventories[ed]==[{'units':list(w),'raw':''.join(w),'count':len(grouped[w])} for w in words if best and all(u not in best['heads'] for u in w)]
 assert res['fixtures']=={'status':'PASS','explicit_code_dp_checks':508,'singleton_BOTH_checks':27,'separate_heads_need_not_compose':True,'odd_final_cannot_be_BOTH_only':True}
 # Exhaustive source-free code concatenation agrees with backward recognition.
 controls=0
 for heads in ((),('x',),('y',),('x','y')):
  codes=[u for u in 'xy' if u not in heads]+[u+v for u in heads for v in 'xy'];language={''}
  for size in range(1,7):
   for word in map(''.join,itertools.product('xy',repeat=size)):
    if any(word.endswith(c) and word[:-len(c)] in language for c in codes):language.add(word)
    assert accepts(word,heads)==(word in language);controls+=1
 out={'status':'PASS','source_joins':joins,'head_set_decisions':decisions,'independent_code_language_controls':controls,'method':'Raw22unit reparse and original915joins; independent backward dynamic program; every decision, minimum and witness reconstructed.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
