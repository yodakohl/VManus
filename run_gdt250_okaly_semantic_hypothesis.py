#!/usr/bin/env python3
"""Generate a narrow semantic hypothesis from GDT247 exact-host candidates."""
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
EXT='gdt059_hpr2_external_inventory.tsv';OBJ='gdt235_label_object_inventory.tsv';CORR='gdt249_result.json';CSTAT='gdt249_corrected_candidate_status.tsv'
OUTS=['gdt250_candidate_semantic_roles.tsv','gdt250_candidate_evidence.tsv','gdt250_counterexamples.tsv'];DOCS=['GDT250_OKALY_SEMANTIC_HYPOTHESIS_METHOD.md','GDT250_OKALY_SEMANTIC_HYPOTHESIS_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with (R/p).open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,rows):
 with (R/p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 ext=read(EXT);obj={r['locus']:r for r in read(OBJ)};assert all(not r['locus'].startswith('f84') for r in ext) and all(not r['locus'].startswith('f84') for r in obj.values())
 ev=[]
 for h in ('okaly','olky'):
  for r in ext:
   if r['page_host']!=h or r['locus'] not in obj:continue
   o=obj[r['locus']];tags=set(r['tags'].split(';'))
   ev.append({'page_host':h,'locus':r['locus'],'physical_folio':r['physical_folio'],'section':r['section'],'token':r['token'],'object_class':o['object_class'],'figure_tag':int('FIGURE' in tags),'plant_tag':int('PLANT' in tags),'star_or_sky_tag':int('STAR_OR_SKY' in tags),'certainty':o['certainty'],'relation_scope':o['relation_scope'],'relation_tags':';'.join(sorted(t for t in tags if t.startswith('REL_'))),'evidence_state':'EXISTING_HUMAN_ANNOTATION_JOIN_NO_NEW_VISUAL'})
 ev.sort(key=lambda r:(r['page_host'],r['physical_folio'],r['locus']));write(OUTS[1],ev)
 assert len([r for r in ev if r['page_host']=='okaly'])==4 and len([r for r in ev if r['page_host']=='olky'])==2
 roles=[
 {'rank':1,'page_host':'okaly','provisional_role':'FIGURE_ASSOCIATED_CLASS_DESCRIPTOR','classification':'PROVISIONAL_LOW_INDEPENDENCE','annotated_label_occurrences':4,'physical_folios':2,'figure_positive':4,'plant_positive':0,'unhedged_exact_local_occurrences':1,'main_support':'three astronomical figure labels on f72 plus one q13 figure-position label on f80','main_confounds':'three observations share f72; f72 evidence hedged; f80 ownership proximity-only; section ecology','prospective_prediction':'next independently selected exact okaly graphical label is FIGURE-tagged rather than PLANT CONTAINER LINE or STAR_ONLY','semantic_assignment':'HYPOTHESIS_ONLY_NOT_EXECUTABLE'},
 {'rank':2,'page_host':'olky','provisional_role':'OBJECT_CLASS_INVARIANT','classification':'FAILED_COUNTEREXAMPLE','annotated_label_occurrences':2,'physical_folios':2,'figure_positive':1,'plant_positive':1,'unhedged_exact_local_occurrences':2,'main_support':'none after cross-folio comparison','main_confounds':'f80 figure-position and f99 plant-position are incompatible coarse classes','prospective_prediction':'NONE_GLOSS_REJECTED','semantic_assignment':'REJECTED'},
 ]
 write(OUTS[0],roles)
 counter=[
 {'counterexample':'OKALY_FOLIO_CLUSTER','value':'3/4 okaly annotations are on physical folio f72','consequence':'effective independent visual support is two folios'},
 {'counterexample':'OKALY_CERTAINTY','value':'the three f72 annotations are HEDGED; only f80r.3 is UNHEDGED exact-local','consequence':'the figure association is provisional'},
 {'counterexample':'OKALY_OWNERSHIP','value':'f80r.3 is PROXIMITY_ONLY in the current visual inventory','consequence':'no figure name or owned descriptor is established'},
 {'counterexample':'OKALY_PROSE_BREADTH','value':'GDT249 records 18 contexts on 15 folios across four sections','consequence':'any figure-class hypothesis must also explain broad prose use'},
 {'counterexample':'OLKY_OBJECT_CONFLICT','value':'f80r.7 is figure-associated while f99v.30 is plant-associated','consequence':'reject a stable coarse object-class gloss for olky'},
 {'counterexample':'SECTION_ECOLOGY','value':'f72 labels are astronomical and f80 labels are q13 by construction','consequence':'all-figure tags need prospective cross-section replication'},
 ]
 write(OUTS[2],counter)
 result={'experiment':'GDT250_OKALY_SEMANTIC_HYPOTHESIS','status':'OKALY_PROVISIONAL_FIGURE_CLASS_DESCRIPTOR_TWO_FOLIO_HYPOTHESIS_OLKY_OBJECT_GLOSS_FAILED','hypotheses_generated':1,'active_semantic_assignments':0,'okaly':{'annotations':4,'physical_folios':2,'figure_positive':4,'hedged_same_f72':3,'unhedged_exact_local':1,'global_prose_contexts':18,'global_prose_folios':15},'olky':{'annotations':2,'physical_folios':2,'object_classes':['FIGURE_ONLY','PLANT'],'object_invariance':'FAILED'},'frozen_future_prediction':'On a future visual-first independently selected graphical label, exact PAGE_HOST okaly predicts FIGURE association rather than PLANT CONTAINER LINE or STAR_ONLY.','interpretation':'okaly is the first current exact PAGE_HOST with a concrete but low-independence semantic-class hypothesis; olky supplies the meaningful counterexample.','claim_ceiling':'Hypothesis generation only; no ownership object name word language plaintext or translation.','f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{p:sha(p) for p in [EXT,OBJ,CORR,CSTAT]},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt250_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'okaly':result['okaly'],'olky':result['olky']},sort_keys=True))
if __name__=='__main__':main()
