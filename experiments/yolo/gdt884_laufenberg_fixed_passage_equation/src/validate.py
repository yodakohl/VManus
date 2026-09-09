#!/usr/bin/env python3
"""Independent source reconstruction, stack search, and mapping certificates."""
import argparse,csv,hashlib,io,itertools,json,re,subprocess,time,unicodedata
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def independent(groups,target,limit=1000000,seconds=60):
 start=time.monotonic();flat=sum(groups,[]);alphabet=list(dict.fromkeys(flat));ix={c:i for i,c in enumerate(alphabet)}
 src=[ix[c] for c in flat];counts=[flat.count(c) for c in alphabet];sets=[set(ix[c] for c in g) for g in groups]
 n=len(target);cap=(1<<(n+1))-1;reach=[0]*(len(alphabet)+1);reach[-1]=1
 for d in range(len(alphabet)-1,-1,-1):
  r=reach[d+1]
  while True:
   next_r=(r|(r<<counts[d]))&cap
   if next_r==r:break
   r=next_r
  reach[d]=r
 todo=[(0,0,())];solutions=set();nodes=0
 while todo:
  if nodes>=limit or time.monotonic()-start>=seconds:return None,nodes
  pos,off,images=todo.pop();nodes+=1;d=len(images)
  residual=n-sum(counts[i]*len(v) for i,v in enumerate(images))
  if residual<0:continue
  need=set();bad=False
  for g in sets:
   if any(i<d and images[i] for i in g):continue
   pending=g-set(range(d))
   if not pending:bad=True;break
   if len(pending)==1:need.update(pending)
  if bad:continue
  min_cost=sum(counts[i] for i in need)
  if residual<min_cost or not ((reach[d]>>(residual-min_cost))&1):continue
  while pos<len(src) and src[pos]<d:
   v=images[src[pos]]
   if target[off:off+len(v)]!=v:bad=True;break
   off+=len(v);pos+=1
  if bad:continue
  if pos==len(src):
   if off==n:solutions.add(tuple(sorted(zip(alphabet,images))))
   continue
  assert src[pos]==d
  lower=int(d in need);upper=min(n-off,(residual-(min_cost-lower*counts[d]))//counts[d])
  for length in range(upper,lower-1,-1):todo.append((pos,off,images+(target[off:off+length],)))
 return solutions,nodes

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for path,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/path)==h,path
 spec=json.loads((E/'src/SPEC.json').read_text());data=json.loads((E/'artifacts/INPUT.json').read_text());result=json.loads((E/'artifacts/RESULT.json').read_text())
 assert result['winter_queried'] is False
 tables={}
 for name,atlas,columns in [('source',spec['source_atlas'],spec['source_columns']),('sta',spec['sta_atlas'],spec['sta_columns'])]:
  argv=['./vmanus-exp','query-tsv',atlas,'--selector','locus']
  for locus in spec['north_loci']:
   assert not locus.startswith('f84');argv+=['--allow',locus]
  argv+=['--columns',','.join(columns),'--forbid-prefix','f84','--forbid-prefix','f84r']
  assert argv==data['guards'][name]['argv']
  p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,check=True)
  assert hashlib.sha256(p.stdout.encode()).hexdigest()==data['guards'][name]['sha256']
  rows=list(csv.DictReader(io.StringIO(p.stdout),delimiter='\t'));tables[name]={r['source_group_id']:r for r in rows}
  assert len(rows)==len(tables[name]) and rows
 assert tables['source'].keys()==tables['sta'].keys()
 seen=set()
 for ed in spec['editions']:
  expected=[]
  for locus in spec['north_loci']:
   rows=sorted([r for r in tables['source'].values() if (r['edition'],r['locus'])==(ed,locus)],key=lambda r:int(r['source_group_index']))
   assert rows
   for i,r in enumerate(rows):
    sid=r['source_group_id'];t=tables['sta'][sid];seen.add(sid)
    assert r['page']=='f85r2' and int(r['source_group_index'])==i+1 and int(r['source_group_count'])==len(rows)
    assert r['left_separator']==('LINE_START' if i==0 else rows[i-1]['right_separator'])
    if i==len(rows)-1:assert r['right_separator']=='LINE_END'
    for key in ['edition','locus','source_group_index','source_group_count','left_separator','right_separator']:assert r[key]==t[key]
    codes=t['primary_sta_codes'].split();assert codes and len(codes)==int(t['primary_sta_symbol_count'])
    expected.append(dict(source_group_id=sid,locus=locus,index=i+1,raw=r['ivtff_group_raw'],codes=codes,sta_raw=t['sta_group_raw'],alternative_site_count=int(t['alternative_site_count']),left_separator=r['left_separator'],right_separator=r['right_separator']))
  assert expected==data['editions'][ed]
 assert seen==tables['source'].keys()
 source=json.loads((E/'artifacts/SOURCE_INTRO.json').read_text());raw=' '.join(source['lines']);versions=[raw]
 while '{' in versions[0]:
  new=[]
  for s in versions:
   a=s.index('{');b=s.index('}',a)
   new.extend(s[:a]+choice+s[b+1:] for choice in s[a+1:b].split('|'))
  versions=new
 normalized=[]
 for s in versions:
  s=unicodedata.normalize('NFKD',s.replace('ſ','s').replace('ß','ss')).lower().translate(str.maketrans({'v':'u','j':'i'}))
  normalized.append(''.join(c for c in s if c in 'abcdefghijklmnopqrstuvwxyz'))
 assert len(normalized)==8 and normalized==[v['text'] for v in data['source_variants']]
 assert len(result['cases'])==24
 expected_cases=[(e,v['id']) for e in spec['editions'] for v in data['source_variants']]
 assert expected_cases==[(c['edition'],c['variant_id']) for c in result['cases']]
 # Test independent implementation's erasing and non-erasing constraints.
 assert independent([['a','b','a']],'x')[0]=={(('a',''),('b','x'))}
 assert independent([['a'],['a']],'xy')[0]==set()
 checks=[]
 for c in result['cases']:
  groups=[g['codes'] for g in data['editions'][c['edition']]];target=next(v['text'] for v in data['source_variants'] if v['id']==c['variant_id'])
  assert c['target_sha256']==hashlib.sha256(target.encode()).hexdigest()
  found=set()
  for sol in c['solutions']:
   m=sol['mapping'];assert set(m)==set(sum(groups,[]));output=[''.join(m[s] for s in g) for g in groups]
   assert all(output) and ''.join(output)==target
   offset=0;spans=[]
   for text in output:spans.append([offset,offset+len(text)]);offset+=len(text)
   assert spans==sol['group_spans'];found.add(tuple(sorted(m.items())))
  assert len(found)==len(c['solutions'])
  if c['status'] in ('UNSAT','SAT_COMPLETE'):
   truth,nodes=independent(groups,target,limit=spec['node_limit'],seconds=spec['seconds'])
   assert truth is not None,('independent_budget',c['edition'],c['variant_id'])
   assert truth==found,(c['edition'],c['variant_id'])
   assert bool(found)==(c['status']=='SAT_COMPLETE')
   checks.append(dict(edition=c['edition'],variant_id=c['variant_id'],complete=True,independent_nodes=nodes))
  else:
   assert c['status'] in ('SAT_PARTIAL','UNKNOWN_BUDGET') and bool(found)==(c['status']=='SAT_PARTIAL')
   checks.append(dict(edition=c['edition'],variant_id=c['variant_id'],complete=False))
 statuses={c['status'] for c in result['cases']}
 expected_status='NO_FIXED_PRIMARY_STA_EXPANSION_TO_DECLARED_INTRO' if statuses=={'UNSAT'} else ('INCOMPLETE_NORTH_SEARCH_NO_WINTER_RELEASE' if statuses&{'SAT_PARTIAL','UNKNOWN_BUDGET'} else 'FINITE_NORTH_KEYS_AVAILABLE_WINTER_PENDING')
 assert result['status']==expected_status
 output=dict(status='PASS',source_reconstructed=True,case_checks=checks,winter_queried=False)
 encoded=json.dumps(output,sort_keys=True,separators=(',',':'))+'\n';p=E/'artifacts/VALIDATION.json'
 if args.check:assert p.read_text()==encoded
 else:p.write_text(encoded)
 print(encoded)
if __name__=='__main__':main()
