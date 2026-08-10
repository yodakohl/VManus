#!/usr/bin/env python3
"""Independent reconstruction of canonical-transfer masked capacity."""
from __future__ import annotations
import csv,hashlib,io,json,os,re,tempfile
from collections import Counter,defaultdict
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/'results';SELF=Path(__file__).resolve();SRC=R/'source_separator_transcription.tsv';ST=R/'parisel_cho_che_folio_states.tsv';PROD=R/'cho_che_canonical_transfer_capacity.json';PANEL=R/'cho_che_canonical_transfer_masked_panel.tsv';PREP=R/'cho_che_canonical_transfer_capacity_report.md';OUT=R/'cho_che_canonical_transfer_capacity_validation.json';REPORT=R/'cho_che_canonical_transfer_capacity_validation_report.md'
HASH={SRC:'4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0',ST:'4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c',B/'CHO_CHE_CANONICAL_TRANSFER_CAPACITY_SPEC.md':'a51103e0234e13373923a82c804a72f5265484fa8780421ccf3e5cadf1a67e65',B/'build_cho_che_canonical_transfer_capacity.py':'5fcc942e69c3def8915aab8e45cc1e49c233bc54092a1fb67fc2d3443c97d506',PROD:'44ccd816eb393ccebb017d209d5cfd7b398f46a5af34cf787084ded3507031c5',PANEL:'8287193a0fcea0e9e7219153fee3d58b830bc60c5a37ee358dfa8abd18e8bf1a',PREP:'b00df0be36c7d49c3cd6bc1a433bc04620f9a16dffb75feb90b7d177e6273b9a'}
E=('ZL3b','IT2a','RF1b');L=('f39','f55','f68','f73','f87','f89','f90','f96');F=('source_group_id','edition','locus','page','collapsed_page','physical_folio','side','page_state','section','currier','hand','kind','grammar_scope','ascii_length','line_position_quartile','group_position_class','site_prefix');SITE=re.compile(r'(ch|sh)([oe])')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reconstruct():
 states=defaultdict(dict)
 for r in csv.DictReader(ST.open(),delimiter='\t'):
  if r['parser']=='SOURCE_ALL_SEPARATORS':states[r['folio']][r['edition']]=int(r['em_state'])
 state={p:next(iter(v.values())) for p,v in states.items() if len(v)==3 and len(set(v.values()))==1};raw=[];pl=defaultdict(dict);mutation=False
 for r in csv.DictReader(SRC.open(),delimiter='\t'):
  page=re.sub(r'([rv])\d+$',r'\1',r['page']);m=re.fullmatch(r'(f\d+)([rv])',page)
  if not m or m.group(1) not in L or page not in state or r['clean_ascii_fragment_count']!='1':continue
  sites=list(SITE.finditer(r['clean_ascii_fragments']))
  if len(sites)!=1:continue
  if not mutation:
   s=r['clean_ascii_fragments'];i=sites[0].end()-1;t=s[:i]+('e' if s[i]=='o' else'o')+s[i+1:];q=list(SITE.finditer(t));mutation=len(q)==1 and q[0].group(1)==sites[0].group(1) and len(t)==len(s)
  gi,gc=int(r['source_group_index']),int(r['source_group_count']);gp='SINGLE' if gc==1 else('FIRST' if gi==1 else('LAST' if gi==gc else'MIDDLE'));x={'source_group_id':r['source_group_id'],'edition':r['edition'],'locus':r['locus'],'page':r['page'],'collapsed_page':page,'physical_folio':m.group(1),'side':m.group(2),'page_state':str(state[page]),'section':r['section'],'currier':r['currier'],'hand':r['hand'],'kind':r['kind'],'grammar_scope':r['grammar_scope'],'ascii_length':str(len(r['clean_ascii_fragments'])),'group_position_class':gp,'site_prefix':sites[0].group(1)};raw.append(x);pl[r['edition'],page].setdefault(r['locus'],int(r['source_row_index']))
 ranks={}
 for (e,p),v in pl.items():
  o=sorted(v,key=lambda x:(v[x],x))
  for i,l in enumerate(o):ranks[e,p,l]=(i,len(o))
 rows=[]
 for x in raw:
  i,n=ranks[x['edition'],x['collapsed_page'],x['locus']];x['line_position_quartile']=str(min(3,4*i//max(1,n)));rows.append({k:x[k] for k in F})
 rows.sort(key=lambda x:(E.index(x['edition']),int(x['physical_folio'][1:]),x['side'],x['locus'],x['source_group_id']));h=io.StringIO(newline='');w=csv.DictWriter(h,fieldnames=F,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return rows,h.getvalue().encode(),mutation
def install(a,b):
 if OUT.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix='cctval_',dir=R) as d:
  x,y=Path(d)/'j',Path(d)/'m';x.write_bytes(a);y.write_bytes(b);os.link(x,OUT)
  try:os.link(y,REPORT)
  except Exception:OUT.unlink(missing_ok=True);raise
def main():
 checks=[]
 for p,h in HASH.items():
  if sha(p)!=h:raise AssertionError(p.name)
  checks.append('hash:'+p.name)
 rows,pb,mutation=reconstruct();actual=json.loads(PROD.read_text());counts=Counter((r['edition'],r['physical_folio'],r['side']) for r in rows)
 assertions={'panel_bytes':pb==PANEL.read_bytes(),'rows':len(rows)==2223,'unique':len({r['source_group_id'] for r in rows})==2223,'reading_counts':Counter(r['edition'] for r in rows)=={'ZL3b':756,'IT2a':764,'RF1b':703},'leaves':{r['physical_folio'] for r in rows}==set(L),'minimum':min(counts.values())==8,'forty_eight_sides':len(counts)==48,'schema_masked':not {'realization','surface','masked_template','score','effect','p_value'}&set(F),'realization_swap_isolated':mutation,'status':actual['status']=='PASS_SCORE_BLIND_CANONICAL_TRANSFER_CAPACITY','gates':all(actual['gates'].values()),'panel_hash':actual['panel_sha256']==hashlib.sha256(pb).hexdigest(),'zero_targets':actual['realizations_stored']==actual['templates_stored']==actual['scores_computed']==0}
 for k,v in assertions.items():
  if not v:raise AssertionError(k)
  checks.append(k)
 result={'experiment':'CHO_CHE_CANONICAL_TRANSFER_CAPACITY_VALIDATION','status':'PASS_INDEPENDENT_REALIZATION_TEMPLATE_MASKED_CAPACITY','checks_passed':len(checks),'inputs':{p.name:sha(p) for p in (*HASH,SELF)},'rows':len(rows),'reading_counts':dict(Counter(r['edition'] for r in rows)),'minimum_side':min(counts.values()),'realization_swap_isolated':mutation,'target_scores_computed':0,'english_glosses':0,'claim_ceiling':'Capacity validation only; no canonical collapse meaning sound wordhood language cipher plaintext or translation.'};report=f"# `cho/che` canonical-transfer capacity validation\n\n**PASS**: {len(checks)} checks reconstruct all 2,223 masked rows, exact reading/leaf/side counts, panel bytes, gates, and realization-swap isolation. No template/state score was computed.\n";install((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),report.encode());print(json.dumps({'status':result['status'],'checks':len(checks)},sort_keys=True))
if __name__=='__main__':main()
