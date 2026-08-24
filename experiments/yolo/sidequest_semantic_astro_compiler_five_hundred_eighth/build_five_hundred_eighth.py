#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P507=R/'experiments/yolo/sidequest_semantic_apprentice_compiler_five_hundred_seventh'
P75=R/'experiments/yolo/sidequest_theory_candidates_v75'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def main():
 loci=read(P75/'V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv');groups=read(P75/'V75_SELECTED_395_GROUP_CELESTIAL_EDITION.tsv');names=read(P75/'V75_SELECTED_NAMESPACE_REGISTRY.tsv')
 locus_ns={locus:x['namespace_id'] for x in names for locus in x['source_loci'].split('|')}
 locus_map={x['locus']:x for x in loci}
 gt=[]
 for x in groups:
  loc=locus_map[x['locus']];ns=locus_ns[x['locus']]
  gt.append({'group_serial':x['group_serial'],'page':x['page'],'diagram_id':x['diagram_id'],'locus':x['locus'],'group_in_locus':x['event_index'],'opaque_group_id':x['opaque_local_id'],'namespace_id':ns,'visible_owner':x['local_image_owner'],'compiler_track':'ASTRO_LOCATE_READ_RECORD','locate_step':f"LOCATE {x['locus']} IN {ns}",'read_step':'COPY THIS OPAQUE LABEL SEGMENT IN LOCAL ORDER','record_step':f"RECORD AS SEGMENT {x['event_index']} OF {loc['group_count']}",'orientation':'NONE','crosspage_join':'NONE','prose_primitive_import':'NONE','creative_page_default':('Zwei getrennte Himmels-Auswahlräder' if x['page']=='f67r2' else 'Mehrpaneel-Sternstationsatlas' if x['page']=='f68r1' else 'Drei getrennte Himmels-Bedingungsräder')})
 write('FIVE_HUNDRED_EIGHTH_395_ASTRO_GROUP_COMPILER_TRACES.tsv',gt)
 lt=[]
 by_locus=defaultdict(list)
 for x in gt:by_locus[x['locus']].append(x)
 for locus_row,x in enumerate(loci,1):
  gg=by_locus[x['locus']];lt.append({'locus_row':str(locus_row),'page':x['page'],'diagram_id':x['diagram_id'],'locus':x['locus'],'namespace_id':locus_ns[x['locus']],'visible_owner':x['local_image_owner'],'owner_status':x['owner_status'],'group_count':x['group_count'],'opaque_group_ids':'|'.join(y['opaque_group_id'] for y in gg),'loop_trace':'START>LOCATED>LABEL_OPEN>LABEL_COPIED>RECORDED>RESET','local_unit_default_de':x['complete_copied_local_meaning_or_label'],'orientation':'NONE','cross_instrument_join':'NONE','next_locus_rule':'RESET_AND_LOCATE_AFRESH'})
 write('FIVE_HUNDRED_EIGHTH_142_ASTRO_LOCUS_LOOPS.tsv',lt)
 pages=[]
 for page,default in [('f67r2','Zwei getrennte Himmels-Auswahlräder; lokale Sektoren und Felder nachschlagen.'),('f68r1','Mehrpaneel-Sternstationsatlas; 28 Sternorte einzeln adressieren.'),('f69v','Drei getrennte Himmels-Bedingungsräder; nur links 28 lokale Plätze.')]:
  ll=[x for x in lt if x['page']==page];gg=[x for x in gt if x['page']==page];nn=sorted({x['namespace_id'] for x in ll})
  pages.append({'page':page,'loci':str(len(ll)),'groups':str(len(gg)),'namespaces':str(len(nn)),'namespace_ids':'|'.join(nn),'creative_workshop_reading_de':default,'orientation_rule':'KEIN START KEINE RICHTUNG KEINE ROTATION','crosspage_rule':'KEIN F68-F69-SCHLUESSEL','compiler_loop':'LOCATE>READ_LOCAL_LABEL>RECORD>RESET'})
 write('FIVE_HUNDRED_EIGHTH_THREE_ASTRO_PAGE_WORKFLOWS.tsv',pages)
 prose=read(P507/'FIVE_HUNDRED_SEVENTH_381_FORWARD_BACKWARD_CARD_TRACES.tsv');unified=[]
 for i,x in enumerate(prose,1):unified.append({'visible_order':str(i),'domain':'PROSE','item_id':x['event_id'],'page':x['page'],'locus':x['locus'],'owner_or_namespace':x['owner_code'],'visible_form_or_opaque_id':x['observed_surface'],'compiler_track':'OWNER>REGISTER>PRIMITIVE>CARD>RENDER','operation_or_loop':x['procedure_tokens'],'semantic_mode':'WORKSHOP_ACTION_WITH_LOCAL_OWNER'})
 for j,x in enumerate(gt,382):unified.append({'visible_order':str(j),'domain':'ASTRO','item_id':'A'+x['group_serial'].zfill(3),'page':x['page'],'locus':x['locus'],'owner_or_namespace':x['namespace_id'],'visible_form_or_opaque_id':x['opaque_group_id'],'compiler_track':'LOCATE>READ>RECORD>RESET','operation_or_loop':'COPY_LOCAL_LABEL_SEGMENT','semantic_mode':'CELESTIAL_LOOKUP_LABEL'})
 write('FIVE_HUNDRED_EIGHTH_776_TEN_PAGE_COMPILER_LEDGER.tsv',unified)
 manual=read(P507/'FIVE_HUNDRED_SEVENTH_125_ITEM_APPRENTICE_MANUAL.tsv');old=[x for x in manual if not (x['layer']=='L2_OWNER_CLASS' and x['scope']=='ASTRO')]
 pos=next(i for i,x in enumerate(old) if x['layer']=='L3_SHARED_SENTENCE_MOTIF')
 new=[]
 for x in names:new.append({'manual_order':'0','layer':'L2_ASTRO_NAMESPACE','item_id':x['namespace_id'],'teaching_value_or_rule_de':x['entry_rule'],'scope':'ASTRO','support_or_instances':f"{x['locus_count']} loci;{x['group_count']} groups",'source_artifact':'PASS508_SELECTED_V75_NAMESPACES'})
 old[pos:pos]=new
 for x in old:
  if x['item_id']=='ASTRO_LOCATE_READ_RECORD':
   x['teaching_value_or_rule_de']='Namensraum wählen; sichtbaren Locus adressieren; lokale Gruppenfolge als eine Etikette kopieren; Wert eintragen; vor dem nächsten Locus vollständig zurücksetzen.';x['source_artifact']='PASS508_ASTRO_COMPILER'
 for i,x in enumerate(old,1):x['manual_order']=str(i)
 write('FIVE_HUNDRED_EIGHTH_124_ITEM_TEN_PAGE_MANUAL.tsv',old)
 summary={'status':'PASS','prose_events':len(prose),'astro_groups':len(gt),'unified':len(unified),'astro_loci':len(lt),'astro_namespaces':len(names),'page_loci':{x['page']:int(x['loci']) for x in pages},'page_groups':{x['page']:int(x['groups']) for x in pages},'manual_before':len(manual),'old_astro_owner_classes_removed':len(manual)-len([x for x in manual if x['layer']=='L2_OWNER_CLASS' and x['scope']=='ASTRO']),'new_namespaces':len(new),'manual_after':len(old)}
 (H/'FIVE_HUNDRED_EIGHTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
