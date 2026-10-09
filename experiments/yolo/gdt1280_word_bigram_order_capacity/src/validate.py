"""Independent capped-two suffix enumeration, not Euler feasibility."""
import collections,functools,gzip,hashlib,json,re,time
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 began=time.monotonic()
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));types=json.loads((B/'artifacts/TYPES.json').read_text());result=json.loads((B/'artifacts/RESULT.json').read_text());events=json.loads(gzip.decompress((B/'artifacts/EVENTS.json.gz').read_bytes()));fibres=json.loads((B/'artifacts/ATTESTED_FIBRES.json').read_text());examples=json.loads((B/'artifacts/EXAMPLES.json').read_text())
 def sig(w):
  c=collections.Counter((w[i-1],w[i]) for i in range(1,len(w)));return w[0],w[-1],tuple(sorted(c.items()))
 expected_words=sorted({tuple(r['units']) for rows in data.values() for r in rows});assert [tuple(t['units']) for t in types]==expected_words;ids={w:i for i,w in enumerate(expected_words)};total_states=0;max_states=0
 for t in types:
  word=t['units'];counts=collections.Counter(zip(word,word[1:]));edges=sorted(counts);state_count=0
  @functools.lru_cache(None)
  def completions(current,left):
   nonlocal state_count
   state_count+=1
   if state_count>50000 or time.monotonic()-began>90:raise RuntimeError('VALIDATION_CAPACITY_STOP')
   if not any(left):return int(current==word[-1])
   answer=0
   for j,(u,v) in enumerate(edges):
    if u!=current or not left[j]:continue
    rest=list(left);rest[j]-=1;answer+=completions(v,tuple(rest))
    if answer>=2:return 2
   return answer
  n=completions(word[0],tuple(counts[e] for e in edges));assert n>=1
  assert (t['alternative'] is not None)==(n==2)
  if n==2:
   alt=t['alternative'];assert alt!=word and len(alt)==len(word) and collections.Counter(alt)==collections.Counter(word) and sig(alt)==sig(word)
  total_states+=state_count;max_states=max(max_states,state_count)
 # Reconstruct event/cohort/attested-fibre accounting directly from allsourcegroups.
 expected_events=[];summary={};expected_fibres={}
 for reader,rows in data.items():
  leaf=lambda r:int(re.match('f([0-9]+)',r['page'])[1]);train={tuple(r['units']) for r in rows if leaf(r)%2};cohorts={c:[] for c in ['ALL_CACHE','LENGTH_GE4','EVEN_GE4','EVEN_UNSEEN_WHOLE_GE4']};classes=collections.defaultdict(lambda:collections.defaultdict(list))
  for row in rows:
   assert not row['page'].startswith('f84') and row['page']!='f116v';w=tuple(row['units']);i=ids[w];e={'reader':reader,'id':row['id'],'page':row['page'],'leaf':leaf(row),'type_index':i,'mobile':types[i]['alternative'] is not None};expected_events.append(e);classes[sig(w)][i].append(row['id']);cohorts['ALL_CACHE'].append(e)
   if len(w)>=4:
    cohorts['LENGTH_GE4'].append(e)
    if leaf(row)%2==0:
     cohorts['EVEN_GE4'].append(e)
     if w not in train:cohorts['EVEN_UNSEEN_WHOLE_GE4'].append(e)
  summary[reader]={}
  for name,es in cohorts.items():
   leaves={e['leaf'] for e in es};typ={e['type_index'] for e in es};mobile=[e for e in es if e['mobile']];per={str(l):{'occurrences':sum(e['leaf']==l for e in es),'mobile':sum(e['leaf']==l for e in mobile)} for l in sorted(leaves)}
   summary[reader][name]={'occurrences':len(es),'mobile_occurrences':len(mobile),'distinct_types':len(typ),'mobile_types':sum(types[i]['alternative'] is not None for i in typ),'leaves':len(leaves),'mobile_leaves':len({e['leaf'] for e in mobile}),'per_leaf':per}
  expected_fibres[reader]=[{'types':[{'type_index':i,'units':types[i]['units'],'source_ids':rs} for i,rs in sorted(g.items())]} for _,g in sorted(classes.items()) if len(g)>1]
 assert expected_events==events and summary==result['readers'] and expected_fibres==fibres
 assert result['distinct_computational_types']==len(types) and result['attested_fibres']=={r:len(v) for r,v in fibres.items()} and result['controls']==1602
 p=summary['ZL3b']['EVEN_UNSEEN_WHOLE_GE4'];assert result['status']==('ORDER_CONTROL_CAPACITY' if p['mobile_occurrences']>=100 and p['mobile_leaves']>=10 else 'ORDER_CONTROL_CAPACITY_STOP')
 for name,t in examples['old_named'].items():assert t==next((x for x in types if ''.join(x['units'])==name),None)
 zl={tuple(r['units']) for r in data['ZL3b']};assert examples['first_three_mobile_ZL']==[t for t in types if t['alternative'] is not None and tuple(t['units']) in zl][:3]
 out={'status':'PASS','distinct_types':len(types),'source_occurrences':len(events),'recursive_states':total_states,'maximum_states_per_word':max_states,'elapsed_seconds':time.monotonic()-began,'scope':'Independentcapped-two enumeration, witnessinvariants,completecohortsandattestedfibres;notnullsampling,contentorgrammaticalvalidation.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
