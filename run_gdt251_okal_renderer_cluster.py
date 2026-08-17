#!/usr/bin/env python3
"""Audit the complete annotated `okal*` nonprose cluster against GDT233."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
NON='gdt053_nonprose_member_groups.tsv';OBJ='gdt235_label_object_inventory.tsv';HYP='gdt250_result.json';PRED='gdt233_q13_label_predictions.tsv'
OUTS=['gdt251_okal_renderer_cluster.tsv','gdt251_okal_variant_summary.tsv','gdt251_section_confounds.tsv','gdt251_counterexamples.tsv'];DOCS=['GDT251_OKAL_RENDERER_CLUSTER_METHOD.md','GDT251_OKAL_RENDERER_CLUSTER_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with (R/p).open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,rows):
 with (R/p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 non=read(NON);obj={r['locus']:r for r in read(OBJ)};assert all(not r['locus'].startswith('f84') for r in non) and all(not r['locus'].startswith('f84') for r in obj.values())
 rows=[]
 for r in non:
  if not r['token'].startswith('okal'):continue
  o=obj.get(r['locus']);fam=o['raw_family'] if o else {'okal':'AQAB','okaly':'AQABA'}.get(r['token'],'UNRESOLVED')
  prefix=o['transferred_prefix'] if o else ('AQAB' if fam.startswith('AQAB') else 'UNAVAILABLE');res=o['strict_residual'] if o else (fam[4:] or 'EMPTY' if fam.startswith('AQAB') else 'UNAVAILABLE')
  tags=set(r['object_tags'].split(';'));rows.append({'locus':r['locus'],'page':r['page'],'physical_folio':r['physical_folio'],'token':r['token'],'raw_family':fam,'transferred_prefix':prefix,'strict_residual':res,'figure_tag':int('FIGURE' in tags),'star_or_sky_tag':int('STAR_OR_SKY' in tags),'plant_tag':int('PLANT' in tags),'annotation_certainty':r['annotation_certainty'],'object_tags':r['object_tags'],'relation_tags':r['relation_tags'],'claim_state':'AQAB_LABEL_RENDERER_CLUSTER_RESIDUAL_UNASSIGNED'})
 rows.sort(key=lambda r:(int(r['physical_folio'][1:]),r['page'],int(r['locus'].split('.')[1])));assert len(rows)==20 and all(r['transferred_prefix']=='AQAB' for r in rows);write(OUTS[0],rows)
 variants=[]
 for token in sorted({r['token'] for r in rows}):
  z=[r for r in rows if r['token']==token];variants.append({'token':token,'occurrences':len(z),'physical_folios':len({r['physical_folio'] for r in z}),'raw_families':';'.join(sorted({r['raw_family'] for r in z})),'strict_residuals':';'.join(sorted({r['strict_residual'] for r in z})),'figure_positive':sum(int(r['figure_tag']) for r in z),'star_or_sky_positive':sum(int(r['star_or_sky_tag']) for r in z),'semantic_value':'UNASSIGNED'})
 write(OUTS[1],variants)
 joined=[r for r in non if r['locus'] in obj]
 sec=[]
 for s in ['Z','B']:
  z=[r for r in joined if obj[r['locus']]['section']==s];q=[r for r in z if r['token'].startswith('okal')]
  sec.append({'section':s,'all_annotated_groups':len(z),'all_figure_positive':sum('FIGURE' in r['object_tags'].split(';') for r in z),'all_figure_fraction':f'{sum("FIGURE" in r["object_tags"].split(";") for r in z)/len(z):.9f}','okal_prefix_groups':len(q),'okal_figure_positive':sum('FIGURE' in r['object_tags'].split(';') for r in q),'okal_figure_fraction':f'{sum("FIGURE" in r["object_tags"].split(";") for r in q)/len(q):.9f}' if q else 'NA','confound_state':'SECTION_OBJECT_ECOLOGY_NOT_CONTROLLED'})
 write(OUTS[2],sec)
 counter=[
 {'counterexample':'COMMON_RENDERER_PREFIX','value':'20/20 okal* groups begin with transferred family prefix AQAB','consequence':'whole-host figure association can be label rendering rather than content'},
 {'counterexample':'SECTION_RESTRICTION','value':'all 20 occur in Z or B; Z joined labels are 178/178 figure-tagged and B 55/73','consequence':'section ecology explains most apparent class purity'},
 {'counterexample':'RESIDUAL_DIVERSITY','value':'10 surface forms and nine residual renderings across seven folios','consequence':'okal* is a construction family not one invariant opaque semantic address'},
 {'counterexample':'NONFIGURE_UNRESOLVED_ROWS','value':'f67r2.22 has STAR_OR_SKY without FIGURE and f67v1.3 has LABEL only','consequence':'18/20 strict FIGURE is not universal'},
 {'counterexample':'OLKY_PLANT','value':'nearby whole-host olky has an unhedged plant-label occurrence','consequence':'short o/k/l/y texture cannot carry a generic figure gloss'},
 {'counterexample':'NO_RESIDUAL_GROUNDING','value':'EMPTY A AB BAB BA AC AF KA and boundary-bearing residuals lack repeated owned referents','consequence':'suffix variants cannot yet be translated'},
 ]
 write(OUTS[3],counter)
 result={'experiment':'GDT251_OKAL_RENDERER_CLUSTER','status':'OKALY_FIGURE_GLOSS_DEMOTED_AQAB_RENDERER_CLUSTER_SECTION_CONFOUNDED','cluster_groups':20,'surface_variants':len(variants),'physical_folios':len({r['physical_folio'] for r in rows}),'transferred_aqab_prefix_fraction':1.0,'figure_positive':sum(int(r['figure_tag']) for r in rows),'figure_or_sky_positive':sum(int(r['figure_tag']) or int(r['star_or_sky_tag']) for r in rows),'sections':['B','Z'],'residuals':sorted({r['strict_residual'] for r in rows}),'gdt250_okaly_hypothesis_state':'DEMOTED_LIKELY_RENDERER_AND_SECTION_CONFOUND','active_semantic_assignments':0,'interpretation':'The okal* family is a productive graphical-label renderer cluster; any content must lie in unresolved residuals or external record context, not the shared prefix alone.','claim_ceiling':'Renderer-family census only; no figure word suffix meaning object name plaintext or translation.','f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{p:sha(p) for p in [NON,OBJ,HYP,PRED]},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt251_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'groups':20,'variants':len(variants),'folios':result['physical_folios'],'figure':result['figure_positive'],'fig_or_sky':result['figure_or_sky_positive'],'residuals':result['residuals']},sort_keys=True))
if __name__=='__main__':main()
