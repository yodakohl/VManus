#!/usr/bin/env python3
"""Build a realization- and template-masked canonical-transfer panel."""
from __future__ import annotations
import csv,hashlib,json,os,re,tempfile
from collections import Counter,defaultdict
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/'results';SELF=Path(__file__).resolve();SPEC=B/'CHO_CHE_CANONICAL_TRANSFER_CAPACITY_SPEC.md';SOURCE=R/'source_separator_transcription.tsv';SV=R/'source_separator_transcription_validation.json';STATES=R/'parisel_cho_che_folio_states.tsv';STATEV=R/'parisel_cho_che_source_audit_validation.json';COSW=R/'cho_che_coswitch_target_validation.json';OUT=R/'cho_che_canonical_transfer_capacity.json';PANEL=R/'cho_che_canonical_transfer_masked_panel.tsv';REPORT=R/'cho_che_canonical_transfer_capacity_report.md'
EXPECTED={SOURCE:'4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0',SV:'8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb',STATES:'4c713c379b33d04985c0efbf9dd4025cb810a9c1006975f7855ed6cc52ff381c',STATEV:'17009e151704d91f795216eed0913cfece447a396d08234df9af46624f286f3b',COSW:'00b0c01d40d2e5987ac410d8f170396a916d0e559c7ce57edbe0f44984732b68'}
E=('ZL3b','IT2a','RF1b');L=('f39','f55','f68','f73','f87','f89','f90','f96');FIELDS=('source_group_id','edition','locus','page','collapsed_page','physical_folio','side','page_state','section','currier','hand','kind','grammar_scope','ascii_length','line_position_quartile','group_position_class','site_prefix');SITE=re.compile(r'(ch|sh)([oe])')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def install(a,b,c):
 if OUT.exists() or PANEL.exists() or REPORT.exists():raise FileExistsError
 with tempfile.TemporaryDirectory(prefix='cctcap_',dir=R) as d:
  q=[Path(d)/x for x in 'abc'];[p.write_bytes(v) for p,v in zip(q,(a,b,c))]
  made=[]
  try:
   for x,y in zip(q,(OUT,PANEL,REPORT)):os.link(x,y);made.append(y)
  except Exception:
   [p.unlink(missing_ok=True) for p in made];raise
def main():
 for p,h in EXPECTED.items():
  if sha(p)!=h:raise SystemExit(f'hash {p.name}')
 if json.loads(COSW.read_text())['status']!='PASS_PRODUCTION_FREE_COSWITCH_NONCONFIRMATION_RECONSTRUCTION':raise SystemExit('coswitch')
 state=defaultdict(dict)
 for r in csv.DictReader(STATES.open(),delimiter='\t'):
  if r['parser']=='SOURCE_ALL_SEPARATORS':state[r['folio']][r['edition']]=int(r['em_state'])
 consensus={p:next(iter(v.values())) for p,v in state.items() if len(v)==3 and len(set(v.values()))==1};raw=[];page_loci=defaultdict(dict)
 for r in csv.DictReader(SOURCE.open(),delimiter='\t'):
  page=re.sub(r'([rv])\d+$',r'\1',r['page']);m=re.fullmatch(r'(f\d+)([rv])',page)
  if not m or m.group(1) not in L or page not in consensus or r['clean_ascii_fragment_count']!='1':continue
  sites=list(SITE.finditer(r['clean_ascii_fragments']))
  if len(sites)!=1:continue
  gi,gc=int(r['source_group_index']),int(r['source_group_count']);gp='SINGLE' if gc==1 else('FIRST' if gi==1 else('LAST' if gi==gc else'MIDDLE'))
  row={'source_group_id':r['source_group_id'],'edition':r['edition'],'locus':r['locus'],'page':r['page'],'collapsed_page':page,'physical_folio':m.group(1),'side':m.group(2),'page_state':str(consensus[page]),'section':r['section'],'currier':r['currier'],'hand':r['hand'],'kind':r['kind'],'grammar_scope':r['grammar_scope'],'ascii_length':str(len(r['clean_ascii_fragments'])),'group_position_class':gp,'site_prefix':sites[0].group(1),'_row':int(r['source_row_index'])}
  raw.append(row);page_loci[r['edition'],page].setdefault(r['locus'],int(r['source_row_index']))
 rank={}
 for k,v in page_loci.items():
  o=sorted(v,key=lambda x:(v[x],x))
  for i,l in enumerate(o):rank[(k[0],k[1],l)]=(i,len(o))
 rows=[]
 for r in raw:
  i,n=rank[r['edition'],r['collapsed_page'],r['locus']];r['line_position_quartile']=str(min(3,4*i//max(1,n)));rows.append({k:r[k] for k in FIELDS})
 rows.sort(key=lambda r:(E.index(r['edition']),int(r['physical_folio'][1:]),r['side'],r['locus'],r['source_group_id']))
 import io
 h=io.StringIO(newline='');w=csv.DictWriter(h,fieldnames=FIELDS,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);pb=h.getvalue().encode();counts=Counter((r['edition'],r['physical_folio'],r['side']) for r in rows);orient={l:next(int(r['page_state']) for r in rows if r['physical_folio']==l and r['side']=='r') for l in L};cells=defaultdict(set)
 for r in rows:cells[r['edition'],r['physical_folio'],r['side']].add((r['section'],r['currier'],r['hand'],r['kind'],r['grammar_scope']))
 gates={'exact_three_readings':{r['edition'] for r in rows}==set(E),'exact_eight_leaves':{r['physical_folio'] for r in rows}==set(L),'both_orientations_5_3':(sum(orient.values()),8-sum(orient.values()))==(5,3),'at_least_2000_rows':len(rows)>=2000,'minimum_eight_each_side':len(counts)==48 and min(counts.values())>=8,'metadata_overlap':all(cells[e,l,'r']&cells[e,l,'v'] for e in E for l in L),'exact_256_orbit':2**len(L)==256,'masked_schema':not {'realization','surface','masked_template','score','effect','p_value'}&set(FIELDS),'target_values_stored_zero':True,'english_glosses_zero':True};passed=all(gates.values());status='PASS_SCORE_BLIND_CANONICAL_TRANSFER_CAPACITY' if passed else 'STOP_CANONICAL_TRANSFER_CAPACITY';decision='AUTHORIZE_CANONICAL_TRANSFER_SYNTHETIC_PREFLIGHT_ONLY' if passed else 'CLOSE_CANONICAL_TRANSFER_UNSCORED'
 result={'experiment':'CHO_CHE_CANONICAL_TRANSFER_CAPACITY','status':status,'decision':decision,'inputs':{p.name:sha(p) for p in (*EXPECTED,SPEC,SELF)},'rows':len(rows),'reading_counts':dict(Counter(r['edition'] for r in rows)),'minimum_leaf_side_rows':min(counts.values()),'leaves':list(L),'high_recto':sum(orient.values()),'high_verso':8-sum(orient.values()),'panel_sha256':hashlib.sha256(pb).hexdigest(),'gates':gates,'realizations_stored':0,'templates_stored':0,'scores_computed':0,'english_glosses':0,'claim_ceiling':'Capacity only for a canonical latent-form transfer preflight; no collapse result meaning sound wordhood language cipher plaintext or translation.'};report=f"# `cho/che` canonical latent-form transfer capacity\n\nStatus: **{status}**\n\nThe realization- and template-masked panel retains **{len(rows):,}** strict one-site groups across all eight leaves and three readings; the minimum reading/leaf/side count is **{min(counts.values())}**. No `o/e` realization, canonical template, score, or effect is stored. Decision: **{decision}**.\n";install((json.dumps(result,indent=2,sort_keys=True)+'\n').encode(),pb,report.encode());print(json.dumps({'status':status,'decision':decision,'rows':len(rows),'minimum':min(counts.values()),'gates':gates},sort_keys=True))
 if not passed:raise SystemExit(2)
if __name__=='__main__':main()
