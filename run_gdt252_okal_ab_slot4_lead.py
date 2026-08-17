#!/usr/bin/env python3
"""Document the post-hoc okal+AB slot-4/10 positional lead and controls."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent
ARR='experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv';NON='gdt053_nonprose_member_groups.tsv';OBJ='gdt235_label_object_inventory.tsv';REN='gdt251_okal_renderer_cluster.tsv';R251='gdt251_result.json'
OUTS=['gdt252_ten_slot_slot4_inventory.tsv','gdt252_okal_ab_position_evidence.tsv','gdt252_counterexamples.tsv'];DOCS=['GDT252_OKAL_AB_SLOT4_LEAD_METHOD.md','GDT252_OKAL_AB_SLOT4_LEAD_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with (R/p).open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,rows):
 with (R/p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 arr=read(ARR);non={r['locus']:r for r in read(NON)};obj={r['locus']:r for r in read(OBJ)};assert all(not r['locus'].startswith('f84') for r in arr) and all(not r['locus'].startswith('f84') for r in non.values())
 slots=[]
 for a in arr:
  if a['slot_count']!='10' or a['slot_index']!='4':continue
  n=non.get(a['locus']);o=obj.get(a['locus'])
  token=n['token'] if n else 'UNRESOLVED';fam=o['raw_family'] if o else 'UNRESOLVED';pre=o['transferred_prefix'] if o else 'UNRESOLVED';res=o['strict_residual'] if o else 'UNRESOLVED'
  cand=int(token.startswith('okal') and pre=='AQAB' and res=='AB')
  slots.append({'array_id':a['array_id'],'page':a['page'],'physical_folio':a['physical_folio'],'unit':a['unit'],'slot_index':a['slot_index'],'slot_count':a['slot_count'],'locus':a['locus'],'token':token,'raw_family':fam,'transferred_prefix':pre,'strict_residual':res,'okal_plus_ab_candidate':cand,'catalogue_homolog':'KLUGE_09A' if "Kluge's 09A" in a['local_comment'] else 'OTHER_OR_UNSPECIFIED','human_local_comment':a['local_comment'],'coverage_state':'FORMAL_COVERED' if n and o else 'FORMAL_UNRESOLVED'})
 assert len(slots)==8 and sum(int(r['okal_plus_ab_candidate']) for r in slots)==2;write(OUTS[0],slots)
 evidence=[r for r in slots if r['okal_plus_ab_candidate']==1];assert [(r['locus'],r['token']) for r in evidence]==[('f70v1.5','okalal'),('f72r1.5','okalam')]
 e=[]
 for r in evidence:e.append({'construction':'VISIBLE_OKAL_PLUS_FAMILY_RESIDUAL_AB','locus':r['locus'],'physical_folio':r['physical_folio'],'array_id':r['array_id'],'token':r['token'],'raw_family':r['raw_family'],'slot_index':r['slot_index'],'slot_count':r['slot_count'],'catalogue_homolog':'KLUGE_09A','candidate_role':'POSITION_4_OF_10_OR_HOMOLOGOUS_SLOT_09A','evidence_class':'POSTHOC_TWO_FOLIO_EXPLORATORY','semantic_assignment':'HYPOTHESIS_ONLY'})
 write(OUTS[1],e)
 # The same family under a different surface renderer is a direct positional counterexample.
 a25=next(r for r in arr if r['locus']=='f70v2.25');o25=obj['f70v2.25'];n25=non['f70v2.25'];assert o25['raw_family']=='AQABAB' and a25['slot_index']=='3'
 counter=[
 {'counterexample':'LOW_RECALL','value':'2 candidate positives among 7 formally covered slot-4 labels in eight 10-slot arrays','consequence':'not a universal slot-4 label'},
 {'counterexample':'KLUGE_09A_RECALL','value':'2 candidate positives among 4 formally covered Kluge 09A homologs','consequence':'even the named homolog is not invariant'},
 {'counterexample':'FAMILY_ONLY_FAILURE','value':f"{n25['token']} at f70v2.25 has family AQABAB but occupies slot 3/10",'consequence':'residual AB alone does not encode position 4'},
 {'counterexample':'POSTSELECTION','value':'construction and target slot were noticed after expanding the okal renderer family','consequence':'conditional same-slot chance 1/10 is descriptive and not confirmatory'},
 {'counterexample':'TWO_FOLIOS','value':'the lead consists only of f70 and f72','consequence':'no held-folio transfer has occurred'},
 {'counterexample':'EDITORIAL_PHASE','value':'slot index follows the human catalogue sequence and no universal authorial degree-1 phase is established','consequence':'candidate is homologous catalogue position not a numbered degree'},
 {'counterexample':'SURFACE_MEMBER_DIFFERENCE','value':'okalal and okalam differ at the final source member while sharing family AQABAB','consequence':'only family-level renderer equivalence supports the pair'},
 ]
 write(OUTS[2],counter)
 result={'experiment':'GDT252_OKAL_AB_SLOT4_LEAD','status':'POSTHOC_OKAL_PLUS_AB_SLOT4_OF_10_POSITION_LEAD_TWO_FOLIOS_NOT_VALIDATED','ten_slot_arrays':8,'slot4_formal_covered':7,'slot4_candidate_positive':2,'kluge_09a_formal_covered':4,'kluge_09a_candidate_positive':2,'candidate_folios':['f70','f72'],'candidate_tokens':['okalal','okalam'],'candidate_family':'AQABAB','candidate_catalogue_homolog':'KLUGE_09A','broader_family_counterexample':{'locus':'f70v2.25','token':'otalam','slot_index':3,'slot_count':10},'hypothesis':'The full visible okal renderer plus family residual AB may denote homologous position 4 in a 10-slot astronomical band.','active_semantic_assignments':0,'claim_ceiling':'Post-hoc positional hypothesis only; no number value degree word language plaintext or translation.','f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{p:sha(p) for p in [ARR,NON,OBJ,REN,R251]},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt252_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'covered':7,'positive':2,'tokens':result['candidate_tokens'],'counterexample':result['broader_family_counterexample']},sort_keys=True))
if __name__=='__main__':main()
