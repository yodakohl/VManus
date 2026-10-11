from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,re
from fractions import Fraction
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,v):(B/'artifacts'/n).write_text(json.dumps(v,indent=2)+'\n')
def parse(u):
 source=[];runs=[];i=0
 while i<len(u):
  g=u[i];j=i+1
  if g in ('e','i'):
   while j<len(u) and u[j]==g:j+=1
   runs.append((len(source),g,j-i))
  source.append(g);i=j
 return source,runs
def eligible(pairs):return len(pairs)>=3 and len({x[0] for x in pairs})>=2 and len({x[1] for x in pairs})>=2
def fixtures():
 assert parse(['e','e','k','i','i','n'])==(['e','k','i','n'],[(0,'e',2),(2,'i',2)])
 assert len(parse(['e','k','e','d','i'])[1])==3
 assert parse(['e','k','k','i'])[0]==['e','k','k','i']
 assert eligible([(1,1),(1,2),(2,1)]) and not eligible([(1,1),(1,2),(1,3)]) and not eligible([(1,1),(2,2)])
 x=[1,1,1,2];values=[]
 for y in sorted(set(itertools.permutations([1,1,2,2]))):
  cross=4*sum(a*b for a,b in zip(x,y))-sum(x)*sum(y);xx=4*sum(a*a for a in x)-sum(x)**2;yy=4*sum(b*b for b in y)-sum(y)**2;values.append(Fraction(cross*cross,xx*yy))
 assert len(set(values))==1 and values[0]==Fraction(1,3)
 return {'status':'PASS','nominal_but_squared_correlation_invariant_permutations':len(values),'invariant_squared_correlation':'1/3'}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={};saved={}
 for ed,rows in sorted(data.items()):
  cells=collections.defaultdict(list);details={};ntwo=0
  for r in rows:
   assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';source,runs=parse(r['units'])
   if len(runs)!=2:continue
   ntwo+=1;k=(r['page'],tuple(source));cells[k].append({'id':r['id'],'raw':r['ivtff_group_raw'],'lengths':[v[2] for v in runs]});details[k]={'slots':[v[0] for v in runs],'families':''.join(v[1] for v in runs)}
  candidates=[]
  for k,events in sorted(cells.items()):
   if eligible([e['lengths'] for e in events]):candidates.append({'page':k[0],'leaf':int(re.match(r'f(\d+)',k[0])[1]),'source':list(k[1]),**details[k],'events':sorted(events,key=lambda x:x['id'])})
  leaves=sorted({c['leaf'] for c in candidates});count=sum(len(c['events']) for c in candidates);families={f:{'cells':sum(c['families']==f for c in candidates),'occurrences':sum(len(c['events']) for c in candidates if c['families']==f)} for f in ['ee','ei','ie','ii']};passed=len(candidates)>=20 and count>=100 and len(leaves)>=10
  results[ed]={'status':'NOMINAL_CAPACITY_ONLY' if passed else 'NO_CAPACITY_UPPER_BOUND','groups':len(rows),'exactly_two_run_occurrences':ntwo,'exactly_two_run_cells':len(cells),'eligible_cells':len(candidates),'eligible_occurrences':count,'physical_leaves':leaves,'families':families,'permutations_run':0};saved[ed]=candidates;print(ed,results[ed],flush=True)
 save('CELLS.json',saved);save('RESULT.json',{'status':'PAIRED_RUN_CAPACITY_STOP_ALL_READINGS' if all(r['status']=='NO_CAPACITY_UPPER_BOUND' for r in results.values()) else 'READER_SPECIFIC_NOMINAL_CAPACITY','readers':results,'fixtures':fx})
if __name__=='__main__':main()
