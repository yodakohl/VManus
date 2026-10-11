from pathlib import Path
import collections,csv,gzip,hashlib,io,json,re,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(n):return json.loads((B/n).read_text())
def main():
 checks=0
 for p,h in read('src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h;checks+=1
 source=json.loads(gzip.decompress((B/'artifacts/SOURCE.json.gz').read_bytes()));cases=read('artifacts/CASES.json');result=read('artifacts/RESULT.json');receipt=read('artifacts/GUARD_RECEIPT.json')
 # A second selector-first read compares the complete saved P projection.
 q=subprocess.run(receipt['command'],cwd=R,text=True,capture_output=True,check=True)
 keys={'id':'source_group_id','edition':'edition','page':'page','locus':'locus','row':'source_row_index','index':'source_group_index','count':'source_group_count','raw':'ivtff_group_raw','left':'left_separator','right':'right_separator','section':'section','currier':'currier'}
 expected=[]
 for x in csv.DictReader(io.StringIO(q.stdout),delimiter='\t'):
  if x['kind']=='P':expected.append({a:int(x[b]) if a in {'row','index','count'} else x[b] for a,b in keys.items()})
 expected.sort(key=lambda x:(x['edition'],x['page'],x['row'],x['index']))
 assert source==expected;checks+=1
 assert not any(x['page'].startswith('f84') or x['page'] in {'f1r','f116v'} for x in source)
 expected_cases=[x for x in source if x['raw']=='qoky'];assert [c['consumer'] for c in cases]==expected_cases;checks+=1
 safe=lambda x:x['left'] in ('DEFINITE_SPACE','LINE_START','LINE_END') and x['right'] in ('DEFINITE_SPACE','LINE_START','LINE_END')
 reliable=lambda x:safe(x) and bool(re.fullmatch(r'[a-z]+',x['raw']))
 pages=collections.defaultdict(list)
 for x in source:pages[x['edition'],x['page']].append(x)
 for c in cases:
  x=c['consumer'];allpage=pages[x['edition'],x['page']];prefix=[y for y in allpage if (y['row'],y['index'])<(x['row'],x['index'])]
  donors=[y['id'] for y in prefix if reliable(y) and y['raw'] in ('qokey','qokeey','qokedy','qokeedy')]
  unknown=[y['id'] for y in prefix if not reliable(y)]
  status='CONSUMER_UNCERTAIN' if not safe(x) else 'AVAILABLE' if donors else 'SOURCE_UNCERTAIN' if unknown else 'MISSING_PREDECESSOR'
  assert (c['status'],c['earlier_producers'],c['uncertain_prefix'])==(status,donors,unknown)
  assert c['consumer_line']==[y['id'] for y in allpage if y['locus']==x['locus']]
  checks+=2
 for ed,phases in result['readers'].items():
  for phase,summary in phases.items():
   cc=[c for c in cases if c['consumer']['edition']==ed and (c['consumer']['page']=='f83r')==(phase=='f83r_development')]
   counts=dict(collections.Counter(c['status'] for c in cc));assert summary['counts']==counts and summary['cases']==len(cc)
   decision='CONTRADICTED' if counts.get('MISSING_PREDECESSOR',0) else 'NECESSARY_ONLY' if counts.get('AVAILABLE',0) else 'NO_ASSESSABLE_CAPACITY'
   assert summary['decision']==decision
   assert summary['missing_pages']==sorted({c['consumer']['page'] for c in cc if c['status']=='MISSING_PREDECESSOR'})
   checks+=3
 out=dict(status='PASS',checks=checks,source_groups=len(source),cases=len(cases),qualification='Separate prefix enumeration and guarded source equality; not independent semantic or palaeographic validation.')
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
