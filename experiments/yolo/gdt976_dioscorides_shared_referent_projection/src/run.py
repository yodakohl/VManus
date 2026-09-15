import collections,csv,gzip,hashlib,json,re,time
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];OLD=R/'experiments/yolo/gdt963_dioscorides_complete_content_code'
def save(name,obj):
 b=(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode();p=E/'artifacts'/name
 if name.endswith('.gz'):
  with gzip.GzipFile(filename=str(p),mode='wb',mtime=0) as f:f.write(b)
 else:p.write_bytes(b)
def table(name,columns,rows):
 with (E/'artifacts'/name).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(columns);w.writerows(rows)
def project(p,text,codes):
 cursor=0;positions=[]
 for gap,atom in zip(p['gaps_before'],p['events']):
  value=codes[atom]
  if gap==0:
   pos=cursor
   if not text.startswith(value,pos):return None
  else:pos=text.find(value,cursor+gap)
  if pos<0:return None
  positions.append(pos);cursor=pos+len(value)
 return positions if len(text)-cursor>=p['tail'] else None

def main():
 started=time.monotonic()
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 spec=json.loads((E/'src/SPEC.json').read_text());ps={p['record']:p for p in spec['projections']}
 with gzip.open(OLD/'artifacts/TARGET_FRAMES.json.gz','rt') as f:frames=json.load(f)
 assert all(not x['page'].startswith('f84') and x['page']!='f116v' for x in frames)
 with (OLD/'artifacts/CANDIDATE_TABLE.tsv').open() as f:local=list(csv.DictReader(f,delimiter='\t'))
 status={(x['edition'],x['page'],x['record']):x['status'] for x in local}
 domains={ed:{p:[] for p in ps} for ed in spec['editions']}
 for x in frames:
  if not x['eligible']:continue
  for rid in ps:
   st=status[x['edition'],x['page'],rid]
   if st in ('UNKNOWN_SOLVER','UNKNOWN_WALL_CEILING','SAT'):
    domains[x['edition']][rid].append({k:x[k] for k in ['page','physical_leaf','text']})
   else:assert st in ('CONTRADICTED_LENGTH_BOUND','UNSAT_SOLVER','UNSAT_EMPTY_DOMAIN','UNSAT_NONEMPTY_LENGTH'),st
 for ed in domains:
  for rid in domains[ed]:domains[ed][rid].sort(key=lambda x:x['page'])
 save('DOMAINS.json',domains)
 candidates=[];pairs=[];asupport={ed:{} for ed in domains};counts={}
 for ed,d in domains.items():
  p1,p2,p3,p4=(d[k] for k in ['I.1','I.2','I.3','IV.20']);capacity=len({x['physical_leaf'] for xs in d.values() for x in xs})>=4 and all(d.values());nstart=len(candidates)
  for a in p1:
   for b in p4:
    row=dict(edition=ed,iris_page=a['page'],xiphion_page=b['page'],iris_leaf=a['physical_leaf'],xiphion_leaf=b['physical_leaf'],status='NO_SHARED_REFERENT_PROJECTION',candidate_code_pairs=0,four_page_assignments=0)
    if a['physical_leaf']==b['physical_leaf']:row['status']='SAME_PHYSICAL_LEAF';pairs.append(row);continue
    if not capacity:row['status']='NO_FOUR_LEAF_CAPACITY';pairs.append(row);continue
    x,y=a['text'],b['text'];maxv=min(len(x)-(ps['I.1']['source_atoms']-1),len(y)-(ps['IV.20']['source_atoms']-1),max((len(z['text'])-(ps['I.2']['source_atoms']-2))//2 for z in p2))
    for lv in range(1,maxv+1):
     v=x[:lv]
     # Any longer prefix has a subset of this substring's possible positions.
     j=y.find(v,ps['IV.20']['gaps_before'][1]+1)
     if j<0 or j+lv>len(y)-ps['IV.20']['tail']:break
     if v not in asupport[ed]:
      sup=[]
      for z in p2:
       pos=project(ps['I.2'],z['text'],{'IRIS':v})
       if pos is not None:sup.append(dict(page=z['page'],physical_leaf=z['physical_leaf'],positions=pos))
      asupport[ed][v]=sup
     if not asupport[ed][v]:break
     supported=[];assignment_count=0
     for z in asupport[ed][v]:
      leaves={a['physical_leaf'],b['physical_leaf'],z['physical_leaf']}
      if len(leaves)!=3:continue
      m=sum(q['physical_leaf'] not in leaves for q in p3)
      if m:supported.append(z['page']);assignment_count+=m
     if not supported:continue
     maxw=min(len(y)-(ps['IV.20']['source_atoms']-1),len(x)-lv-(ps['I.1']['source_atoms']-2),len(y)-lv-(ps['IV.20']['source_atoms']-2))
     for lw in range(1,maxw+1):
      w=y[:lw];codes={'IRIS':v,'XIPHION':w};pa=project(ps['I.1'],x,codes);pb=project(ps['IV.20'],y,codes)
      if pa is None or pb is None:break
      if v.startswith(w) or w.startswith(v):continue
      candidates.append(dict(edition=ed,iris_page=a['page'],xiphion_page=b['page'],iris_code=v,xiphion_code=w,iris_positions=pa,xiphion_positions=pb,acorus_pages=supported,four_page_assignments=assignment_count))
      row['candidate_code_pairs']+=1;row['four_page_assignments']+=assignment_count
    if row['candidate_code_pairs']:row['status']='PARTIAL_SHARED_REFERENT_ONLY'
    pairs.append(row)
  cs=candidates[nstart:];counts[ed]=dict(domains={k:len(v) for k,v in d.items()},physical_leaves=len({x['physical_leaf'] for xs in d.values() for x in xs}),status='NO_CAPACITY' if not capacity else 'PARTIAL_SHARED_REFERENT_ONLY' if cs else 'SHARED_REFERENT_PROJECTION_CONTRADICTED',candidate_code_pairs=len(cs),acorus_triples=sum(len(x['acorus_pages']) for x in cs),four_page_assignments=sum(x['four_page_assignments'] for x in cs))
  print(ed,counts[ed],flush=True)
 candidates.sort(key=lambda x:(x['edition'],x['iris_page'],x['xiphion_page'],len(x['iris_code']),len(x['xiphion_code'])))
 save('CANDIDATES.json.gz',candidates);save('ACORUS_SUPPORT.json.gz',asupport)
 cols=['edition','iris_page','xiphion_page','iris_leaf','xiphion_leaf','status','candidate_code_pairs','four_page_assignments'];table('PAGE_PAIRS.tsv',cols,[[x[k] for k in cols] for x in pairs])
 classes={}
 for c in candidates:
  key=(c['edition'],c['iris_code'],c['xiphion_code']);s=classes.setdefault(key,dict(page_pairs=0,acorus_triples=0,four_page_assignments=0));s['page_pairs']+=1;s['acorus_triples']+=len(c['acorus_pages']);s['four_page_assignments']+=c['four_page_assignments']
 table('CODE_CLASSES.tsv',['edition','iris_code','xiphion_code','page_pairs','acorus_triples','four_page_assignments'],[[*k,*[v[z] for z in ['page_pairs','acorus_triples','four_page_assignments']]] for k,v in sorted(classes.items())])
 table('CANDIDATE_PREDICTIONS.tsv',['edition','iris_page','xiphion_page','iris_code','xiphion_code','iris_positions','xiphion_positions','acorus_pages','four_page_assignments'],[[c['edition'],c['iris_page'],c['xiphion_page'],c['iris_code'],c['xiphion_code'],','.join(map(str,c['iris_positions'])),','.join(map(str,c['xiphion_positions'])),','.join(c['acorus_pages']),c['four_page_assignments']] for c in candidates])
 result=dict(status='PARTIAL_SHARED_REFERENT_BINDINGS_REMAIN' if candidates else 'NO_LITERAL_SHARED_REFERENT_BINDING',frames=len(frames),eligible_frames=sum(x['eligible'] for x in frames),source_unknown_frames=sum(not x['eligible'] for x in frames),page_pairs=len(pairs),candidate_code_pairs=len(candidates),code_classes=len(classes),editions=counts,confirmed_words=0,independent_confirmation_leaves=0,full_code_tested=False,reserve_access=False,prior_exposure=True,complete_enumeration=True,elapsed_seconds=time.monotonic()-started)
 save('RESULT.json',result);print(json.dumps(result))
if __name__=='__main__':main()
