#!/usr/bin/env python3
"""Exhaustive complete-record fit; external answer never enters this module."""
import argparse,csv,hashlib,io,itertools,json,re,subprocess,time
from collections import defaultdict
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
EDITIONS=['ZL3b','IT2a','RF1b'];ENTRIES=['LACTUCA','PIRETRUM','APIUM']
ALLOW='experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
ATLAS='experiments/yolo/gdt807_target_masked_paragraph_exchange_codebook/artifacts/GDT807_665_STRICT_PARAGRAPH_ATLAS.tsv'
RAW='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
STA='experiments/semantic_assumptions/results/source_sta_group_alignment.tsv'
FRAMECOLS='paragraph_id,page,physical_folio,start_locus,end_locus,start_line_number,end_line_number,source_line_count'
RAWCOLS='source_group_id,edition,locus,page,kind,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw'
STACOLS='source_group_id,edition,locus,source_group_index,source_group_count,left_separator,right_separator,primary_sta_codes,primary_sta_symbol_count,alternative_site_count'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'))+'\n'
def write(name,v,check):
 p=E/'artifacts'/name;s=enc(v)
 if check:assert p.read_text()==s,name
 else:p.write_text(s)
def query(path,selector,allowed,columns):
 cmd=['./vmanus-exp','query-tsv',path,'--selector',selector]
 for value in sorted(set(allowed)):cmd+=['--allow',value]
 cmd+=['--columns',columns,'--forbid-prefix','f84','--forbid-prefix','f84r']
 out=subprocess.run(cmd,cwd=ROOT,check=True,capture_output=True,text=True).stdout
 return list(csv.DictReader(io.StringIO(out),delimiter='\t')),dict(argv=cmd,source_sha256=sha(ROOT/path),projection_sha256=hashlib.sha256(out.encode()).hexdigest())
def number(locus):
 assert re.fullmatch(r'f[0-9]+[rv][0-9]*\.[0-9]+',locus),locus
 return int(locus.rsplit('.',1)[1])
def select():
 pages=[r['page'] for r in csv.DictReader((ROOT/ALLOW).open(),delimiter='\t')]
 assert len(pages)==len(set(pages))==179 and not any(p.startswith('f84') for p in pages)
 frames,g1=query(ATLAS,'page',pages,FRAMECOLS);assert len(frames)==665
 raw,g2=query(RAW,'page',pages,RAWCOLS)
 byline=defaultdict(list)
 for r in raw:
  if r['edition'] in EDITIONS:byline[r['edition'],r['locus']].append(r)
 prose=defaultdict(list)
 for (ed,loc),rows in byline.items():
  rows.sort(key=lambda r:int(r['source_group_index']))
  assert len({r['kind'] for r in rows})==1
  if rows[0]['kind']=='P':prose[ed,rows[0]['page']].append(loc)
 all_loci=set();frame_loci={}
 for f in frames:
  assert f['page'] in pages
  assert f['physical_folio']==re.match(r'f[0-9]+[rv]',f['page']).group()
  f['atlas_physical_folio']=f['physical_folio']
  f['physical_folio']=re.match(r'f[0-9]+',f['page']).group()
  lo,hi=int(f['start_line_number']),int(f['end_line_number'])
  locs=sorted((l for l in prose['ZL3b',f['page']] if lo<=number(l)<=hi),key=number)
  assert len(locs)==int(f['source_line_count']),('FRAME_LINE_COUNT',f['paragraph_id'])
  assert locs[0]==f['start_locus'] and locs[-1]==f['end_locus'],('FRAME_ENDPOINTS',f['paragraph_id'])
  for ed in EDITIONS:
   alternate={l for l in prose[ed,f['page']] if lo<=number(l)<=hi}
   assert not alternate-set(locs),('ADDITIONAL_ALTERNATE_P_LOCUS',ed,f['paragraph_id'])
  frame_loci[f['paragraph_id']]=locs;all_loci.update(locs)
 sta,g3=query(STA,'locus',all_loci,STACOLS)
 sx={r['source_group_id']:r for r in sta};assert len(sx)==len(sta)
 out=[]
 for f in frames:
  locs=frame_loci[f['paragraph_id']];readings={}
  for ed in EDITIONS:
   groups=[];reasons=[]
   for li,loc in enumerate(locs):
    rows=byline.get((ed,loc),[])
    if not rows:reasons.append('MISSING_LOCUS');continue
    assert [int(r['source_group_index']) for r in rows]==list(range(1,len(rows)+1)),('GROUP_INDEX',ed,loc)
    assert all(int(r['source_group_count'])==len(rows) for r in rows)
    assert all(r['kind']=='P' for r in rows),('NON_P_FRAME_LOCUS',ed,loc)
    assert len({r['paragraph_start'] for r in rows})==len({r['paragraph_end'] for r in rows})==1
    assert (rows[0]['paragraph_start']=='1')==(li==0),('PARAGRAPH_START',ed,loc)
    assert (rows[0]['paragraph_end']=='1')==(li==len(locs)-1),('PARAGRAPH_END',ed,loc)
    if rows[0]['left_separator']!='LINE_START' or rows[-1]['right_separator']!='LINE_END':reasons.append('OUTER_BOUNDARY')
    assert all(a['right_separator']==b['left_separator'] for a,b in zip(rows,rows[1:])),('SEPARATOR_PARITY',ed,loc)
    if any(r['right_separator']!='DEFINITE_SPACE' for r in rows[:-1]):reasons.append('NONDEFINITE_INTERNAL_SEPARATOR')
    for r in rows:
     if not re.fullmatch('[a-z]+',r['ivtff_group_raw']):reasons.append('NONLITERAL_GROUP')
     assert r['source_group_id'] in sx,('MISSING_STA_ROW',r['source_group_id'])
     s=sx[r['source_group_id']]
     assert all(r[k]==s[k] for k in ['edition','locus','source_group_index','source_group_count','left_separator','right_separator'])
     codes=s['primary_sta_codes'].split();assert len(codes)==int(s['primary_sta_symbol_count'])
     if not codes:reasons.append('EMPTY_STA')
     if int(s['alternative_site_count']):reasons.append('STA_ALTERNATIVE')
     groups.append(dict(raw=r['ivtff_group_raw'],sta=codes,locus=loc,source_group_id=r['source_group_id']))
   readings[ed]=dict(eligible=not reasons,reasons=sorted(set(reasons)),groups=groups)
  rs=[readings[e] for e in EDITIONS]
  same=all([(g['raw'],g['sta'],g['locus']) for g in r['groups']]==[(g['raw'],g['sta'],g['locus']) for g in rs[0]['groups']] for r in rs[1:])
  readings['CONSENSUS']=dict(eligible=all(r['eligible'] for r in rs) and same,reasons=sorted(set(x for r in rs for x in r['reasons'])|({'READING_DISAGREEMENT'} if not same else set())),groups=rs[0]['groups'])
  out.append(dict(**f,loci=locs,readings=readings))
 return dict(guards=[g1,g2,g3],frames=out)
def ordinary(slots,groups):
 d={};inverse={}
 for slot,g in zip(slots,groups):
  v=tuple(g['sta']);a=slot['atom']
  if a.startswith('@'):continue
  if (a in d and d[a]!=v) or (v in inverse and inverse[v]!=a):return None
  d[a]=v;inverse[v]=a
 return d

def fit(frames,templates,edition,deadline=None):
 byentity={r['entity']:r['slots'] for r in templates};pools={};length_counts={}
 for e in ENTRIES:
  slots=byentity[e];pool=[];n=0
  for f in frames:
   r=f['readings'][edition]
   if not r['eligible'] or len(r['groups'])!=len(slots):continue
   n+=1;d=ordinary(slots,r['groups'])
   if d is not None:pool.append((f,r['groups'],d))
  pools[e]=pool;length_counts[e]=n
 solutions=[];triples=0;dictionary_triples=0;complete=True
 for chosen in itertools.product(*(pools[e] for e in ENTRIES)):
  if deadline is not None and time.monotonic()>deadline:complete=False;break
  if len({p[0]['physical_folio'] for p in chosen})!=3:continue
  triples+=1;d={};inv={};okay=True
  for _,_,local in chosen:
   for a,v in local.items():
    if (a in d and d[a]!=v) or (v in inv and inv[v]!=a):okay=False;break
    d[a]=v;inv[v]=a
   if not okay:break
  if not okay:continue
  surface={};entity_values=[]
  for e,(_,groups,_) in zip(ENTRIES,chosen):
   for slot,g in zip(byentity[e],groups):
    if slot['atom'].startswith('@'):
     value=tuple(g['sta']);entity_values.append(value)
     surface.setdefault((slot['context'],slot['atom'][1:]),[]).append(value)
  if any(v in inv for v in entity_values):continue
  dictionary_triples+=1
  heads=[surface['head',e][0] for e in ENTRIES]
  corrections=[v for (ctx,_),values in surface.items() if ctx=='corrective' for v in values]
  for nh in range(3):
   ph=heads[0][:nh]
   if any(len(v)<=nh or v[:nh]!=ph for v in heads):continue
   b={e:surface['head',e][0][nh:] for e in ENTRIES}
   for nc in range(3):
    pc=corrections[0][:nc]
    if any(len(v)<=nc or v[:nc]!=pc for v in corrections):continue
    bodies=dict(b);valid=True;held=None
    for (ctx,e),values in surface.items():
     if ctx!='corrective':continue
     tails={v[nc:] for v in values}
     if len(tails)!=1:valid=False;break
     body=next(iter(tails))
     if e=='HELD':held=body
     elif e in bodies and bodies[e]!=body:valid=False;break
     else:bodies[e]=body
    if not valid or len(bodies)!=4 or len(set(bodies.values()))!=4:continue
    if any(prefix+body in inv for prefix in [ph,pc] for body in bodies.values()):continue
    identities=[e for e,v in bodies.items() if v==held]
    if len(identities)!=1:continue
    solutions.append(dict(paragraphs={e:p[0]['paragraph_id'] for e,p in zip(ENTRIES,chosen)},prefix_head=list(ph),prefix_corrective=list(pc),bodies={e:list(v) for e,v in bodies.items()},dictionary={a:list(v) for a,v in d.items()},held_entity=identities[0]))
 solutions.sort(key=enc)
 return dict(candidates={e:[p[0]['paragraph_id'] for p in pools[e]] for e in ENTRIES},length_counts=length_counts,distinct_folio_triples=triples,dictionary_triples=dictionary_triples,complete=complete,solutions=solutions,held_entities=sorted({s['held_entity'] for s in solutions}))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 for p,h in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert sha(ROOT/p)==h,p
 selected=select();variants=json.loads((E/'src/FIT_TEMPLATES.json').read_text())['variants']
 deadline=time.monotonic()+1800;panels={}
 for edition in EDITIONS+['CONSENSUS']:
  for v in variants:panels[edition+':'+str(int(v['explicit_headers']))]=fit(selected['frames'],v['entries'],edition,deadline)
 allsol=[s for p in panels.values() for s in p['solutions']]
 result=dict(experiment_id='GDT887',panels=panels,complete=all(p['complete'] for p in panels.values()),held_entities=sorted({s['held_entity'] for s in allsol}),eligible={e:sum(f['readings'][e]['eligible'] for f in selected['frames']) for e in EDITIONS+['CONSENSUS']},claim_ceiling='Conditional notation reconstruction; source identity completion is not a confirmed manuscript meaning.')
 write('SELECTED.json',selected,a.check);write('RESULT.json',result,a.check)
 print(json.dumps(dict(eligible=result['eligible'],complete=result['complete'],panels={k:dict(length_counts=p['length_counts'],candidates={e:len(v) for e,v in p['candidates'].items()},solutions=len(p['solutions']),held=p['held_entities']) for k,p in panels.items()}),sort_keys=True))
if __name__=='__main__':main()
