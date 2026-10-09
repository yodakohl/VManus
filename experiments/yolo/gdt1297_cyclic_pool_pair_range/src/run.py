#!/usr/bin/env python3
import collections,gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
def make_runs(rows,reader):
 grouped=collections.defaultdict(list)
 for q in rows:grouped[(q['page'],q['locus'])].append(q)
 runs=[]
 for (page,locus),qs in sorted(grouped.items()):
  current=[]
  def emit():
   if current:
    first=int(current[0]['source_group_index']);last=int(current[-1]['source_group_index'])
    runs.append({'id':f'{reader}|{locus}|{first:03}-{last:03}','page':page,'locus':locus,'groups':list(current)})
  for q in sorted(qs,key=lambda z:int(z['source_group_index'])):
   if current and int(q['source_group_index'])!=int(current[-1]['source_group_index'])+1:emit();current=[]
   current.append(q)
  emit()
 return sorted(runs,key=lambda z:z['id'])
def difference(forms,a,b):
 d=[0]
 for w in forms:d.append(d[-1]+(w==a)-(w==b))
 return d

def analyze(runs):
 seeds={};word_runs=collections.defaultdict(set);direct=set()
 for ri,run in enumerate(runs):
  forms=[q['ivtff_group_raw'] for q in run['groups']];positions=collections.defaultdict(list)
  for i,w in enumerate(forms):positions[w].append(i);word_runs[w].add(ri)
  direct.update(forms[i] for i in range(len(forms)-2) if forms[i]==forms[i+1]==forms[i+2])
  for a,ps in positions.items():
   for j in range(len(ps)-2):
    lo,hi=ps[j],ps[j+2];qs=run['groups'][lo:hi+1];ids=tuple(q['id'] for q in qs);key=(hi-lo+1,ids)
    if a not in seeds or key<seeds[a][0]:seeds[a]=(key,ri,lo,hi)
 results=[];pair_checks=0
 for a,(key,ri,lo,hi) in sorted(seeds.items()):
  run=runs[ri];qs=run['groups'][lo:hi+1];partners=sorted({q['ivtff_group_raw'] for q in qs}-{a});checks=[]
  for b in partners:
   bad=None
   for rj in sorted(word_runs[a]|word_runs[b]):
    other=runs[rj];forms=[q['ivtff_group_raw'] for q in other['groups']];d=difference(forms,a,b)
    if max(d)-min(d)>2:
     bad={'run_id':other['id'],'prefix_difference':d,'range':max(d)-min(d),'source_ids':[q['id'] for q in other['groups']]};break
   checks.append({'partner':b,'excluded':bad is not None,'witness':bad});pair_checks+=1
  survivors=[x['partner'] for x in checks if not x['excluded']]
  results.append({'form':a,'seed':{'run_id':run['id'],'start_offset':lo,'end_offset':hi,'source_ids':[q['id'] for q in qs],'forms':[q['ivtff_group_raw'] for q in qs],'candidate_partners':partners},'partner_checks':checks,'surviving_partners':survivors,'forced_singleton':not survivors})
 return results,sorted(direct),pair_checks

def fake(words,offset=0):
 return {'id':str(offset),'groups':[{'id':f'{offset}:{i}','ivtff_group_raw':w} for i,w in enumerate(words)]}
def fixtures():
 for s in ['BAAB','ABBAAB']:assert max(difference(s,'A','B'))-min(difference(s,'A','B'))<=2
 a,_,_=analyze([fake('AABAAB')]);assert next(x for x in a if x['form']=='A')['forced_singleton']
 a,_,_=analyze([fake('AXAXA'),fake('AYAYA',1)]);assert next(x for x in a if x['form']=='A')['forced_singleton']
 a,_,_=analyze([fake('ABBAAB')]);assert not any(x['forced_singleton'] for x in a)
 a,_,_=analyze([fake('AAA')]);assert a[0]['forced_singleton']
 for x,y in itertools.combinations('ABC',2):assert max(difference('AABBCC',x,y))-min(difference('AABBCC',x,y))<=2
 assert not any(all(set('AABBCC'[j:j+3])==set('ABC') for j in range(phase,4,3)) for phase in range(3))
 windows=0
 for size in [2,3]:
  members=tuple('ABC'[:size]);perms=list(itertools.permutations(members))
  for cycles in itertools.product(perms,repeat=3):
   stream=sum(cycles,())
   for lo in range(len(stream)):
    for hi in range(lo+1,len(stream)+1):
     chunk=stream[lo:hi];windows+=1
     for x,y in itertools.combinations(members,2):
      ds=difference(chunk,x,y);assert max(ds)-min(ds)<=2
     findings,_,_=analyze([fake(chunk)])
     for f in findings:assert set(members)-{f['form']}<=set(f['surviving_partners'])
 rows=[{'page':'f1r','locus':'f1r.1','source_group_index':str(i),'id':str(i),'ivtff_group_raw':'A'} for i in [2,3,5]]
 rs=make_runs(rows,'S');assert [len(r['groups']) for r in rs]==[2,1] and not analyze(rs)[0]
 return {'status':'PASS','valid_cycle_windows':windows,'missing_index_split':True,'nonlocal_without_AA':True,'pair_not_pool_sufficiency':True,'native_data_read':False}

def main():
 spec=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 for inp in spec['inputs']:assert hashlib.sha256((ROOT/inp['path']).read_bytes()).hexdigest()==inp['sha256']
 data=json.loads(gzip.decompress((ROOT/spec['inputs'][0]['path']).read_bytes()));old=json.loads((ROOT/spec['inputs'][1]['path']).read_text());oldsets={r:{q['raw'] for q in old if q['edition']==r} for r in spec['readers']};results={};pack={};allruns={}
 for reader in spec['readers']:
  rows=data[reader];assert len({q['id'] for q in rows})==len(rows)
  for q in rows:assert q['edition']==reader and q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE' and not q['page'].startswith('f84') and q['page']!='f116v'
  runs=make_runs(rows,reader);findings,direct,checks=analyze(runs);forced=sorted(x['form'] for x in findings if x['forced_singleton']);types={q['ivtff_group_raw'] for q in rows};additional=sorted(set(forced)-oldsets[reader]-set(direct))
  results[reader]={'groups':len(rows),'runs':len(runs),'forms':len(types),'repeat_anchors':len(findings),'seed_partner_checks':checks,'forced_singletons':forced,'current_direct_AAA':direct,'old857_AAA':sorted(oldsets[reader]),'additional_nonlocal_forced':additional,'minimum_distinct_pools':len(forced)+int(bool(types-set(forced))),'unexcluded_anchor_forms':[x['form'] for x in findings if not x['forced_singleton']]};pack[reader]=findings;allruns[reader]=runs
  print(reader,json.dumps(results[reader]),flush=True)
 status='ADDITIONAL_SINGLETON_CONSEQUENCES' if any(x['additional_nonlocal_forced'] for x in results.values()) else 'NO_ADDITIONAL_SINGLETON_CONSEQUENCE'
 (B/'artifacts/RESULT.json').write_text(json.dumps({'status':status,'readers':results,'scope':'Conditionalfixedfaithfuldisjointcyclingpools,wholegroupoutputs,nostate resetinsidearun;notgeneralhomophonyorwordmeanings'},indent=2)+'\n')
 for name,obj in [('RUNS',allruns),('PROOFS',pack)]: (B/f'artifacts/{name}.json.gz').write_bytes(gzip.compress(json.dumps(obj,sort_keys=True,separators=(',',':')).encode(),mtime=0))
if __name__=='__main__':
 import sys
 if '--fixtures' in sys.argv:
  f=fixtures();(B/'artifacts/FIXTURES.json').write_text(json.dumps(f,indent=2)+'\n');print(json.dumps(f))
 else:main()
