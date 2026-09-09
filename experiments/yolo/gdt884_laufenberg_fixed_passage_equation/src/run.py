#!/usr/bin/env python3
import argparse,csv,hashlib,io,itertools,json,re,subprocess,unicodedata
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from morphism import solve,selftest
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n'
def query(path,columns,loci):
 argv=['./vmanus-exp','query-tsv',path,'--selector','locus']
 for locus in loci:
  assert not locus.startswith('f84');argv+=['--allow',locus]
 argv+=['--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
 s=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,check=True).stdout
 rows=list(csv.DictReader(io.StringIO(s),delimiter='\t'));assert rows
 return rows,dict(argv=argv,sha256=hashlib.sha256(s.encode()).hexdigest())
def normalize(s):
 s=unicodedata.normalize('NFKD',s.replace('ſ','s').replace('ß','ss')).lower().replace('v','u').replace('j','i')
 return ''.join(c for c in s if 'a'<=c<='z')
def variants(source):
 text=' '.join(source['lines']);options=[m.group(1).split('|') for m in re.finditer(r'\{([^{}]+)\}',text)]
 result=[]
 for choice in itertools.product(*options):
  seq=iter(choice);s=re.sub(r'\{([^{}]+)\}',lambda m:next(seq),text)
  result.append(dict(choices=list(choice),text=normalize(s)))
 assert len(result)==8 and len({x['text'] for x in result})==8
 return [dict(id='V'+str(i+1),**x) for i,x in enumerate(result)]
def source(spec):
 a,ga=query(spec['source_atlas'],spec['source_columns'],spec['north_loci'])
 b,gb=query(spec['sta_atlas'],spec['sta_columns'],spec['north_loci'])
 byid={r['source_group_id']:r for r in b};assert len(byid)==len(b)
 assert {r['source_group_id'] for r in a}==set(byid)
 result={}
 for ed in spec['editions']:
  groups=[]
  for locus in spec['north_loci']:
   rows=sorted([r for r in a if r['edition']==ed and r['locus']==locus],key=lambda r:int(r['source_group_index']))
   assert rows,(ed,locus)
   assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1))
   for i,r in enumerate(rows):
    sid=r['source_group_id'];t=byid[sid]
    assert r['page']=='f85r2' and int(r['source_group_count'])==len(rows)
    for key in ['edition','locus','source_group_index','source_group_count','left_separator','right_separator']:assert r[key]==t[key],(sid,key)
    assert (i or r['left_separator']=='LINE_START') and (i<len(rows)-1 or r['right_separator']=='LINE_END')
    codes=t['primary_sta_codes'].split();assert codes and len(codes)==int(t['primary_sta_symbol_count'])
    groups.append(dict(source_group_id=sid,locus=locus,index=i+1,raw=r['ivtff_group_raw'],codes=codes,sta_raw=t['sta_group_raw'],alternative_site_count=int(t['alternative_site_count']),left_separator=r['left_separator'],right_separator=r['right_separator']))
  result[ed]=groups
 return result,dict(source=ga,sta=gb)
def worker(job):
 ed,variant,groups,spec=job
 answer=solve(groups,variant['text'],node_limit=spec['node_limit'],seconds=spec['seconds'],max_solutions=spec['max_solutions'])
 return dict(edition=ed,variant_id=variant['id'],target_sha256=hashlib.sha256(variant['text'].encode()).hexdigest(),**answer)
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
 for path,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/path)==h,path
 spec=json.loads((E/'src/SPEC.json').read_text());original=json.loads((E/'artifacts/SOURCE_INTRO.json').read_text());vs=variants(original)
 groups,guards=source(spec)
 inputs=dict(editions=groups,source_variants=vs,guards=guards)
 jobs=[(ed,v,[x['codes'] for x in groups[ed]],spec) for ed in spec['editions'] for v in vs]
 with ProcessPoolExecutor(max_workers=min(spec['workers'],len(jobs))) as pool:results=list(pool.map(worker,jobs))
 statuses=[r['status'] for r in results]
 if all(s=='UNSAT' for s in statuses):status='NO_FIXED_PRIMARY_STA_EXPANSION_TO_DECLARED_INTRO'
 elif any(s in ('UNKNOWN_BUDGET','SAT_PARTIAL') for s in statuses):status='INCOMPLETE_NORTH_SEARCH_NO_WINTER_RELEASE'
 else:status='FINITE_NORTH_KEYS_AVAILABLE_WINTER_PENDING'
 result=dict(experiment_id='GDT884',status=status,cases=results,selftests=selftest(),winter_queried=False)
 for name,value in [('INPUT.json',inputs),('RESULT.json',result)]:
  path=E/'artifacts'/name;text=dump(value)
  if args.check:assert path.read_text()==text,name
  else:path.write_text(text)
 print(dump(dict(status=status,cases=[{k:v for k,v in r.items() if k!='solutions'}|dict(solution_count=len(r['solutions'])) for r in results])))
if __name__=='__main__':main()
