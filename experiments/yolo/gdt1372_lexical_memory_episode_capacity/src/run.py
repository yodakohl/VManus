from pathlib import Path
from collections import defaultdict
from functools import lru_cache
import gzip,hashlib,json,re,csv
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 x=p.read_bytes();return json.loads(gzip.decompress(x) if p.suffix=='.gz' else x)
def save(n,x):
 x=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(x,mtime=0) if n.endswith('.gz') else x)
@lru_cache(None)
def extrema(n,total,first,last):
 states={(first,first):(0,0)}
 for i in range(1,n):
  nxt={}
  for (ones,prev),(lo,hi) in states.items():
   for bit in ([last] if i==n-1 else [0,1]):
    if ones+bit>total:continue
    key=(ones+bit,bit);a,b=lo+(bit!=prev),hi+(bit!=prev)
    if key in nxt:a=min(a,nxt[key][0]);b=max(b,nxt[key][1])
    nxt[key]=(a,b)
  states=nxt
 return states[(total,last)]
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1369_open_edge_fragment_partition/artifacts/RUNS.json.gz');old=read(R/'experiments/yolo/gdt1368_fragment_window_nucleus_capacity/artifacts/WINDOWS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};out={};results={}
 for rd,runs in sorted(data.items()):
  replay=[]
  for run in runs:
   rows=run['sources'];assert len(rows)>=3
   for j,row in enumerate(rows):
    assert row['edition']==rd and row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v') and row['kind']=='P';assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE';raw=row['ivtff_group_raw'];u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',raw);assert ''.join(u)==raw and u==row['units'];i=int(row['source_group_index']);assert row['id']==f"{rd}|{row['locus']}|G{i:03d}"
    if j:assert row['page']==rows[0]['page'] and row['locus']==rows[0]['locus'] and i==int(rows[j-1]['source_group_index'])+1
   replay.extend({'sources':rows[i:i+3],'support':sorted({c for row in rows[i:i+3] for c in row['ivtff_group_raw']})} for i in range(len(rows)-2))
  assert replay==old[rd]
  for order in ['BH','HB']:
   for height in 'ktpf':
    chosen='c'+height+'h';pair=['ch',height] if order=='BH' else [height,'ch'];case=rd+'_'+order+'_'+height;episodes=[];opps=keys=single=0
    for ri,run in enumerate(runs):
     histories=defaultdict(list)
     for row in run['sources']:
      source=[];orig=[]
      for oi,u in enumerate(row['units']):
       expanded=pair if u==chosen else [u];source.extend(expanded);orig.extend([oi]*len(expanded))
      for pos in range(len(source)-1):
       if source[pos:pos+2]==pair:
        y=int(orig[pos]==orig[pos+1]);histories[(tuple(source),pos)].append({'id':row['id'],'index':int(row['source_group_index']),'y':y});opps+=1
     keys+=len(histories)
     for (source,pos),visits in sorted(histories.items()):
      if len(visits)==1:single+=1;continue
      bits=[v['y'] for v in visits];lo,hi=extrema(len(bits),sum(bits),bits[0],bits[-1]);episodes.append({'run_index':ri,'page':run['sources'][0]['page'],'locus':run['sources'][0]['locus'],'source':list(source),'position':pos,'visits':visits,'min_switches':lo,'max_switches':hi,'mobile':hi>lo,'remote_transitions':sum(b['index']>a['index']+1 for a,b in zip(visits,visits[1:]))})
    mobile=[e for e in episodes if e['mobile']];remote=sum(e['remote_transitions'] for e in mobile);leaves=len({int(re.match(r'f(\d+)',e['page']).group(1)) for e in mobile});status='CAPACITY_READY' if remote>=100 and leaves>=10 else 'NO_CAPACITY'
    results[case]={'runs':len(runs),'opportunities':opps,'keys':keys,'singleton_keys':single,'episodes':len(episodes),'visits':sum(len(e['visits']) for e in episodes),'mobile_episodes':len(mobile),'mobile_visits':sum(len(e['visits']) for e in mobile),'mobile_remote_transitions':remote,'mobile_leaves':leaves,'status':status};out[case]=episodes
    print(case,{k:results[case][k] for k in ['opportunities','episodes','mobile_episodes','mobile_remote_transitions','mobile_leaves','status']})
 save('EPISODES.json.gz',out);save('RESULT.json',{'status':'LEXICAL_MEMORY_EPISODE_CAPACITY','cases':results})
if __name__=='__main__':main()
