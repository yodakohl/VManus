"""Synthetic exhaustive comparison; no manuscript input."""
import itertools,json,random,re
from pathlib import Path
import run
import validate
E=Path(__file__).resolve().parents[1]
def fits(p,text,codes):
 pattern=''
 for gap,event in zip(p['gaps_before'],p['events']):pattern+=(('.{'+str(gap)+',}') if gap else '')+re.escape(codes[event])
 return re.fullmatch(pattern+'.{'+str(p['tail'])+',}',text) is not None
def exhaustive(d,p,v,w):
 a,x=d['T']['I.1'][0]['text'],d['T']['IV.20'][0]['text']
 common={a[i:j] for i in range(len(a)) for j in range(i+1,len(a)+1)} & {x[i:j] for i in range(len(x)) for j in range(i+1,len(x)+1)}
 for l,b in itertools.product(sorted(common),repeat=2):
  values=[v,w,l,b]
  if any(y.startswith(z) or z.startswith(y) for i,y in enumerate(values) for z in values[i+1:]):continue
  c=dict(IRIS=v,XIPHION=w,LEAF=l,BROAD=b)
  if all(fits(p[r],d['T'][r][0]['text'],c) for r in p):return True
 return False
def main():
 source=json.loads((E/'src/SPEC.json').read_text());p={r:dict(events=z['events'],gaps_before=[0 if i==0 and z['gaps_before'][0]==0 else 1 for i in range(len(z['events']))],tail=1) for r,z in source['projections'].items()}
 rng=random.Random(977);cases=[]
 for n in range(24):
  ts={r:''.join(rng.choice('abcd') for _ in range(rng.randrange(10,16))) for r in p}
  ts['I.1']='a'+ts['I.1'][1:];ts['IV.20']='b'+ts['IV.20'][1:];cases.append(('a','b',ts))
 for v,w,l,b in [('a','b','c','d'),('c','a','ba','bb')]:
  vals=dict(IRIS=v,XIPHION=w,LEAF=l,BROAD=b);ts={r:''.join('c'*gap+vals[e] for gap,e in zip(z['gaps_before'],z['events']))+'c' for r,z in p.items()};cases.append((v,w,ts))
 vals=dict(IRIS='a',XIPHION='b',LEAF='c',BROAD='c')
 ts={r:''.join('a'*gap+vals[e] for gap,e in zip(z['gaps_before'],z['events']))+'a' for r,z in p.items()};cases.insert(0,('a','b',ts))
 checks=[]
 for n,(v,w,ts) in enumerate(cases):
  d={'T':{r:[dict(page=r,physical_leaf=r,text=t)] for r,t in ts.items()}}
  spec={'projections':p,'case_cpu_seconds':60};run.support.cache_clear();run.setup(d,spec)
  base=dict(edition='T',iris_code=v,xiphion_code=w,iris_page='I.1',xiphion_page='IV.20')
  result=run.solve((n,base));actual=result['status']=='PARTIAL_FOUR_ATOM_WITNESS';expected=exhaustive(d,p,v,w)
  assert not result['status'].startswith('UNKNOWN') and actual==expected,(n,result,expected)
  vp={r:dict(gaps=z['gaps_before'],tail=z['tail']) for r,z in p.items()}
  validate.SUPPORT_CACHE.clear()
  errors=validate.validate_witness(base,d,vp,result['witness']) if actual else validate.replay_negative(base,d,vp,result)
  assert not errors,(n,errors)
  checks.append(dict(id=n,expected_exists=expected,status=result['status'],nodes=result['nodes'],certificate_errors=errors))
 assert all(x['expected_exists'] for x in checks[-2:])
 out=dict(status='PASS',cases=checks,case_count=len(checks),scope='Synthetic finite exhaustive substring comparison; not manuscript evidence or significance')
 (E/'artifacts/SEARCH_CONTROL.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'synthetic exhaustive comparisons')
if __name__=='__main__':main()
