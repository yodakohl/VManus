from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,itertools,json,re,sys
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def folio(row):return int(re.match(r'f(\d+)',row['page']).group(1))
def odd_encoded(word,escape,alphabet):
 table={a:chr(65+i) for i,a in enumerate(alphabet)};text=''.join(table[a] for a in word)
 return [[m.start(),m.end()] for m in re.finditer(table[escape]+'+',text) if len(m.group())%2]
def pair_reader(word,escape):
 pos=0;plain=[]
 while pos<len(word):
  item=word[pos]
  if item==escape:
   if tuple(word[pos:pos+2])!=(escape,escape):return None
   pos+=2
  else:pos+=1
  plain.append(item)
 return tuple(plain)
def controls():
 count=0
 for n in range(1,8):
  for word in itertools.product('abc',repeat=n):
   for marker in 'abc':
    runs=odd_encoded(word,marker,'abc');decoded=pair_reader(word,marker)
    assert (decoded is None)==bool(runs)
    if decoded is not None:
     rendered=tuple(x for a in decoded for x in ((a,a) if a==marker else (a,)));assert rendered==word
    count+=1
 assert odd_encoded(tuple('abbba'),'b','abc')==[[1,4]]
 assert odd_encoded(tuple('abbbb'),'b','abc')==[]
 return {'status':'PASS','source_free':True,'independent_regex_parser_cases':count}
def main():
 for path,digest in read(BASE/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 source=read(ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allowed={r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};result=read(BASE/'artifacts/RESULT.json');packets=read(BASE/'artifacts/VIOLATIONS.json.gz');assert result['status']=='EXACT_QUOTED_LITERAL_MARKER_SCREEN';assert set(source)=={'IT2a','RF1b','ZL3b'}
 expected_keys={a+'_'+b for a in source for b in ['FULL','GE2']};assert set(result['panels'])==set(packets)==expected_keys;checks=groups=0;summary={}
 for reader,rows in sorted(source.items()):
  dictionary=defaultdict(list)
  for row in rows:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   word=tuple(re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw']));assert ''.join(word)==row['ivtff_group_raw'] and list(word)==row['units'] and word;dictionary[word].append(row);groups+=1
  for mode in ['FULL','GE2']:
   words={w:rr for w,rr in dictionary.items() if mode=='FULL' or len({folio(r) for r in rr})>=2};alphabet=sorted({a for w in words for a in w});assert len(alphabet)==22;name=reader+'_'+mode;got=result['panels'][name];assert got['groups']==sum(map(len,words.values())) and got['types']==len(words);assert set(got['keys'])==set(packets[name])==set(alphabet);survivors=[]
   for marker in alphabet:
    initial=literal=contains=bad_count=0;bad={};intervals={}
    for word,occ in sorted(words.items()):
     checks+=1
     if word[0]==marker:initial+=len(occ);continue
     literal+=len(occ)
     if marker in word:contains+=len(occ)
     spans=odd_encoded(word,marker,alphabet);decoded=pair_reader(word,marker)
     assert bool(spans)==(decoded is None)
     if spans:bad[word]=occ;intervals[word]=spans;bad_count+=len(occ)
    witness=None
    if bad:
     first=min(bad);rr=bad[first];witness={'word':list(first),'odd_intervals':intervals[first],'count':len(rr),'physical_leaves':sorted({folio(r) for r in rr}),'first_row':rr[0]}
    expected={'granted_initial_groups':initial,'literal_groups':literal,'literal_containing_groups':contains,'violating_groups':bad_count,'violating_types':len(bad),'violating_physical_leaves':sorted({folio(r) for rr in bad.values() for r in rr}),'conditional_fraction':[bad_count,contains],'witness':witness,'survives':not bad}
    assert got['keys'][marker]==expected,(name,marker)
    assert packets[name][marker]==[{'word':list(w),'odd_intervals':intervals[w],'source_ids':[r['id'] for r in rr]} for w,rr in sorted(bad.items())],(name,marker,'packet')
    if not bad:survivors.append(marker)
   assert got['surviving_markers']==survivors and got['status']==('NO_MARKER' if not survivors else 'NECESSARY_SYNTAX_SURVIVORS');summary[name]=survivors
 output={'status':'PASS','original_groups_checked':groups,'word_marker_checks':checks,'panels':summary,'controls':controls(),'scope':'Independent raw reparse, literal-pair consumption, regex-run certificates and all counts/support; no linguistic or historical validation.'};(BASE/'artifacts/VALIDATION.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n');print(json.dumps(output,sort_keys=True))
if __name__=='__main__':
 if '--controls' in sys.argv:
  out=controls();(BASE/'artifacts/VALIDATOR_CONTROLS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out)
 else:main()
