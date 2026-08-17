#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
PAGE=R/'experiments/semantic_assumptions/results/existing_human_page_annotations.tsv'
ANN=R/'experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv'
LAT=R/'gdt229_q13_semantic_role_lattice.tsv';PRED=R/'gdt233_q13_label_predictions.tsv';PFX=R/'gdt237_prefix_stability.tsv'
OUTS=['gdt239_f82r_label_dossier.tsv','gdt239_f82r_field_dossier.tsv','gdt239_f82r_page_model.json']
DOCS=['GDT239_F82R_TRANSLATION_DOSSIER_METHOD.md','GDT239_F82R_TRANSLATION_DOSSIER_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def only_page(path,target='f82r'):
 out=[]
 with path.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');pi=h.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t')
   if a[pi]!=target:continue
   out.append(dict(zip(h,a)))
 return out
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 page=only_page(PAGE)[0];ann=only_page(ANN);lat=only_page(LAT);pred={x['locus']:x for x in only_page(PRED)}
 stable=[]
 with PFX.open(encoding='utf-8') as f:
  for x in csv.DictReader(f,delimiter='\t'):
   if x['all_folds']=='1':stable.append(x['prefix'])
 labels=[]
 for a in ann:
  p=pred[a['locus']];surf=p['family_surface'];mm=sorted((x for x in stable if surf.startswith(x)),key=lambda x:(-len(x),x));sp=mm[0] if mm else 'NONE'
  owner='CONNECTED_COMPONENT' if a['local_relation_tags']=='REL_EXPLICIT_ATTACHMENT' and 'tube' in a['local_comment'].lower() else ('PROXIMITY_ONLY' if 'REL_PROXIMITY' in a['local_relation_tags'] else 'UNKNOWN')
  labels.append({'page':'f82r','locus':a['locus'],'visual_unit':a['unit'],'human_local_comment':a['local_comment'],'human_relation_tags':a['local_relation_tags'],'ownership_evidence':owner,'family_expression':surf,'gdt233_strict_prefix':p['strict_prefix'],'gdt233_strict_residual':p['strict_residual'],'gdt237_fold_stable_prefix':sp,'fold_stable_residual':surf[len(sp):] if sp!='NONE' else surf,'baca_exposed_sensitivity':p['baca_sensitivity'],'baca_sensitivity_residual':p['baca_residual'],'formal_interpretation':'LABEL_RENDERER_PLUS_OPAQUE_RESIDUAL','semantic_value':'UNASSIGNED'})
 write(OUTS[0],labels)
 fields=[]
 for x in lat:
  fields.append({'page':'f82r','record_id':x['record_id'],'field_ordinal':x['field_ordinal'],'record_field_count':x['record_field_count'],'locus':x['locus'],'source_tokens':x['source_tokens'],'page_hosts':x['page_hosts'],'compiler_cells':x['compiler_cells'],'field_group_count':x['field_group_count'],'line_field_end':x['line_field_end'],'abstract_role_like':x['abstract_role_like'],'leading_latent_document_role':x['leading_latent_document_role'],'mandatory_alternatives':x['mandatory_alternatives'],'evidence_grade':x['evidence_grade'],'semantic_value':'UNASSIGNED'})
 write(OUTS[1],fields)
 model={'page':'f82r','human_catalogue':{'general_description':page['general_description'],'illustrations':page['illustrations'],'text_description':page['text_description'],'source_url':page['source_url']},
 'human_counts':{'loci':45,'prose_lines':32,'labels':13,'paragraphs':3},'formal_counts':{'parsed_fields':len(fields),'covered_prose_loci':len({x['locus'] for x in fields}),'human_prose_locus_coverage':len({x['locus'] for x in fields})/32,'mechanical_record_keys':len({x['record_id'] for x in fields}),'short_argument_like':sum(x['abstract_role_like']=='SHORT_ARGUMENT_LIKE' for x in fields),'instruction_clause_like':sum(x['abstract_role_like']=='INSTRUCTION_CLAUSE_LIKE' for x in fields),'dy_ended':sum(x['line_field_end']=='DY' for x in fields),'line_ended':sum(x['line_field_end']=='LINE_END' for x in fields)},
 'label_counts':{'exact_labels':len(labels),'gdt233_strict_prefix_detected':sum(x['gdt233_strict_prefix']!='NONE' for x in labels),'gdt237_fold_stable_prefix_detected':sum(x['gdt237_fold_stable_prefix']!='NONE' for x in labels),'connected_component_evidence':sum(x['ownership_evidence']=='CONNECTED_COMPONENT' for x in labels),'proximity_only':sum(x['ownership_evidence']=='PROXIMITY_ONLY' for x in labels)},
 'leading_page_hypothesis':'ILLUSTRATED_THERAPEUTIC_OR_HYDRAULIC_PRACTICAL_RECORD_WITH_COMPONENT_STATE_ARGUMENTS','mandatory_alternatives':['ILLUSTRATED_CASE_OR_INDICATION_RECORD','APPARATUS_OR_SETTING_KEY_WITH_PROSE','NONSEMANTIC_RECORD_RENDERER'],'lexical_assignments':0,
 'claim_ceiling':'Translation-shaped page organization only; no field ownership, object word, action, condition, material, language, plaintext, or translation.'}
 (R/OUTS[2]).write_text(json.dumps(model,indent=2,sort_keys=True)+'\n')
 result={'experiment':'GDT239_F82R_TRANSLATION_DOSSIER','status':'F82R_VISUAL_LABEL_DOSSIER_COMPLETE_PROSE_LATTICE_PARTIAL_NO_LEXICAL_KEY','page':'f82r','human_counts':model['human_counts'],'formal_counts':model['formal_counts'],'label_counts':model['label_counts'],'leading_page_hypothesis':model['leading_page_hypothesis'],'mandatory_alternatives':model['mandatory_alternatives'],'lexical_assignments':0,
 'interpretation':'f82r can be rendered as a complete visual-label dossier plus a partial selected-record field scaffold; the apparatus and figure labels remain renderer-plus-opaque-residual forms and prose fields remain broad role alternatives.',
 'claim_ceiling':model['claim_ceiling'],'f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},
 'inputs':{str(x.relative_to(R)):sha(str(x.relative_to(R))) for x in (PAGE,ANN,LAT,PRED,PFX)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 (R/'gdt239_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'fields':len(fields),'labels':len(labels),'label_counts':model['label_counts']},sort_keys=True))
if __name__=='__main__':main()
