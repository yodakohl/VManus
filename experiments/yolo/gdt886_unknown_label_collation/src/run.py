#!/usr/bin/env python3
import argparse,csv,hashlib,io,json,re,subprocess
from collections import deque
from pathlib import Path
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
ED=['ZL3b','IT2a','RF1b'];ROWS=[[f'f88r.{i}' for i in range(1,7)],[f'f88r.{i}' for i in range(12,18)]]
SOURCES={
 'raw':('experiments/semantic_assumptions/results/source_separator_transcription.tsv','source_group_id,edition,locus,page,source_group_index,source_group_count,left_separator,right_separator,ivtff_group_raw'),
 'sta':('experiments/semantic_assumptions/results/source_sta_group_alignment.tsv','source_group_id,edition,locus,source_group_index,source_group_count,left_separator,right_separator,primary_sta_codes,primary_sta_symbol_count,alternative_site_count')}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def write(name,x,check):
 p=E/'artifacts'/name;s=enc(x)
 if check:assert p.read_text()==s,name
 else:p.write_text(s)
def query(path,columns):
 argv=['./vmanus-exp','query-tsv',path,'--selector','locus']
 for row in ROWS:
  for loc in row:argv+=['--allow',loc]
 argv+=['--columns',columns,'--forbid-prefix','f84','--forbid-prefix','f84r']
 out=subprocess.run(argv,cwd=ROOT,check=True,capture_output=True,text=True).stdout
 records=list(csv.DictReader(io.StringIO(out),delimiter='\t'));assert records
 return records,dict(argv=argv,source_sha256=sha(ROOT/path),projection_sha256=hashlib.sha256(out.encode()).hexdigest())
def select():
 raw,g1=query(*SOURCES['raw']);sta,g2=query(*SOURCES['sta']);sx={r['source_group_id']:r for r in sta};assert len(sx)==len(sta)
 selected=[]
 for r in raw:
  s=sx[r['source_group_id']];assert all(r[k]==s[k] for k in ['edition','locus','source_group_index','source_group_count','left_separator','right_separator'])
  assert r['edition'] in ED and r['page']=='f88r'
  reasons=[]
  if (r['source_group_index'],r['source_group_count'])!=('1','1'):reasons.append('not_single_group')
  if (r['left_separator'],r['right_separator'])!=('LINE_START','LINE_END'):reasons.append('unclear_outer_boundary')
  if not re.fullmatch('[a-z]+',r['ivtff_group_raw']):reasons.append('nonliteral_annotation')
  codes=s['primary_sta_codes'].split();assert len(codes)==int(s['primary_sta_symbol_count'])
  selected.append(dict(source_group_id=r['source_group_id'],edition=r['edition'],locus=r['locus'],raw=r['ivtff_group_raw'],sta=codes,raw_exclusions=reasons,sta_exclusions=reasons+(['sta_alternatives'] if int(s['alternative_site_count']) else [])))
 return selected,[g1,g2]
def compare(a,b):
 for i,(x,y) in enumerate(zip(a,b)):
  if x!=y:return dict(kind='edge',symbols=[x,y],position=i)
 if len(a)>len(b):return dict(kind='prefix_inversion')
 return dict(kind='equal' if len(a)==len(b) else 'prefix_correct')
def analyse(rows):
 comparisons=[];alphabet=sorted({c for row in rows for rec in row for c in rec['symbols']})
 for ri,row in enumerate(rows):
  for a,b in zip(row,row[1:]):comparisons.append(dict(row=ri+1,loci=[a['locus'],b['locus']],**compare(a['symbols'],b['symbols'])))
 def graph(cs):
  adj={x:set() for x in alphabet};witness={}
  for c in cs:
   if c['kind']=='edge':
    a,b=c['symbols'];adj[a].add(b);witness.setdefault((a,b),c)
  reach={x:set(adj[x]) for x in alphabet}
  for k in alphabet:
   for x in alphabet:
    if k in reach[x]:reach[x].update(reach[k])
  cyc=[]
  for start in alphabet:
   q=deque([(start,[start])]);seen={start}
   while q:
    x,path=q.popleft()
    for y in sorted(adj[x]):
     if y==start:cyc=path+[y];break
     if y not in seen:seen.add(y);q.append((y,path+[y]))
    if cyc:break
   if cyc:break
  prefix=[c for c in cs if c['kind']=='prefix_inversion'];order=[]
  if not cyc and not prefix:
   left=set(alphabet)
   while left:
    zero=sorted(x for x in left if not any(x in adj[y] for y in left));assert zero
    x=zero[0];order.append(x);left.remove(x)
  return dict(status='CONTRADICTION' if cyc or prefix else 'COMPATIBLE_PARTIAL_ORDER',cycle=cyc,cycle_witnesses=[witness[(a,b)] for a,b in zip(cyc,cyc[1:])],prefix_inversions=prefix,closure={x:sorted(reach[x]) for x in alphabet},one_extension=order)
 train=graph([c for c in comparisons if c['row']==1]);held=[]
 for c in comparisons:
  if c['row']!=2:continue
  if train['status']=='CONTRADICTION':v='TRAIN_INCONSISTENT'
  elif c['kind']!='edge':v=c['kind'].upper()
  else:
   a,b=c['symbols'];v='FORCED_CORRECT' if b in train['closure'][a] else 'FORCED_WRONG' if a in train['closure'][b] else 'UNCONSTRAINED'
  held.append(dict(**c,prediction=v))
 return dict(retained_rows=[[r['locus'] for r in row] for row in rows],alphabet=alphabet,comparisons=comparisons,training=train,held=held,joint=graph(comparisons))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
 for p,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/p)==h,p
 data,guards=select();idx={(r['edition'],r['locus']):r for r in data};assert len(idx)==len(data)
 panels={}
 for unit in ['raw','sta']:
  for ed in ED+['CONSENSUS']:
   rows=[]
   for locs in ROWS:
    row=[]
    for loc in locs:
     rs=[idx.get((e,loc)) for e in (ED if ed=='CONSENSUS' else [ed])]
     if any(r is None or r[unit+'_exclusions'] for r in rs):continue
     if any(r[unit]!=rs[0][unit] for r in rs):continue
     row.append(dict(locus=loc,symbols=list(rs[0][unit])))
    rows.append(row)
   panels[unit+':'+ed]=analyse(rows)
 result=dict(experiment_id='GDT886',guards=guards,panels=panels,ceiling='conditional literal-unit collation; one physical folio, no meaning')
 write('SELECTED.json',data,args.check);write('RESULT.json',result,args.check)
 print(json.dumps({k:dict(status=v['joint']['status'],cycle=v['joint']['cycle'],retained=[len(row) for row in v['retained_rows']],held=[c['prediction'] for c in v['held']]) for k,v in panels.items()},sort_keys=True))
if __name__=='__main__':main()
