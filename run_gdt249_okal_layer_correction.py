#!/usr/bin/env python3
"""Correct GDT248's source-group/PAGE_HOST conflation for `okal`."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
OLD='gdt248_result.json';BFE='gdt080_hpr4_bfe_join.tsv';F82='gdt241_f82r_hpr2_fields.tsv';MAN='gdt165_host_manifest.tsv';CTX='gdt166_context_inventory.tsv';DIR='gdt165_directed_relations.tsv'
OUTS=['gdt249_cross_scope_layer_correction.tsv','gdt249_corrected_candidate_status.tsv'];DOCS=['GDT249_OKAL_LAYER_CORRECTION_METHOD.md','GDT249_OKAL_LAYER_CORRECTION_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with (R/p).open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,rows):
 with (R/p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 b=read(BFE);f=read(F82);assert all(not r['locus'].startswith('f84') for r in b+f)
 lab=next(r for r in b if r['locus']=='f82r.36');field=next(r for r in f if r['locus']=='f82r.6' and 'okal' in r['source_tokens'].split('|'))
 i=field['source_tokens'].split('|').index('okal');host=field['page_hosts'].split('|')[i];cell=field['compiler_cells'].split('|')[i];right=cell.split(':')[3]
 assert (lab['token'],lab['page_host'],lab['right_family'])==('okal','ok','al') and (host,right)==('ok','al')
 mapping=[
 {'source_group':'okaly','gdt247_label':'f80r.3','gdt247_prose':'f80r.31','parsed_page_host':'okaly','right_family':'NONE','gdt248_state':'LAYER_MAPPING_VALID','corrected_state':'GENERAL_FORMAL_HOST_NO_GLOSS'},
 {'source_group':'olky','gdt247_label':'f80r.7','gdt247_prose':'f80r.38','parsed_page_host':'olky','right_family':'NONE','gdt248_state':'LAYER_MAPPING_VALID','corrected_state':'CURRIER_B_FORMAL_HOST_NO_GLOSS'},
 {'source_group':'okal','gdt247_label':'f82r.36','gdt247_prose':'f82r.6','parsed_page_host':host,'right_family':right,'gdt248_state':'INVALIDLY_MAPPED_TO_PAGE_HOST_OKAL','corrected_state':'EXACT_SHARED_GROUP_TUPLE_OK_PLUS_AL_NO_CONTENT_ADDRESS'},
 ]
 write(OUTS[0],mapping)
 ctx=[r for r in read(CTX) if r['context_mode']=='WINDOW_PM2'];assert all(not r['locus'].startswith('f84') for r in ctx)
 status=[]
 for h,state in [('ok','UBIQUITOUS_HOST_NOT_Q13_STARS_SPECIFIC'),('olky','CURRIER_B_WIDE_FORMAL_HOST'),('okaly','CROSS_REGISTER_GENERAL_FORMAL_HOST')]:
  z=[r for r in ctx if r['focal_host']==h];sec=Counter(r['section'] for r in z);cur=Counter(r['currier'] for r in z)
  status.append({'page_host':h,'window_occurrences':len(z),'physical_folios':len({r['physical_folio'] for r in z}),'sections':';'.join(f'{k}:{sec[k]}' for k in sorted(sec)),'currier':';'.join(f'{k}:{cur[k]}' for k in sorted(cur)),'corrected_state':state,'semantic_value':'UNASSIGNED'})
 assert [(r['page_host'],r['window_occurrences'],r['physical_folios']) for r in status]==[('ok',834,69),('olky',11,9),('okaly',18,15)]
 write(OUTS[1],status)
 result={'experiment':'GDT249_OKAL_LAYER_CORRECTION','status':'GDT248_OKAL_Q13_STARS_LEAD_WITHDRAWN_SOURCE_GROUP_PAGE_HOST_LAYER_CONFLATION','supersedes':'GDT248 okal candidate ranking only','gdt247_exact_source_group_reuse_retained':True,'corrected_okal_parse':{'page_host':'ok','right_family':'al'},'ok_host':{'window_occurrences':834,'physical_folios':69,'sections':6},'withdrawn_claim':'okal as a narrow PAGE_HOST shared by q13 and Stars','retained_claim':'the exact source group okal, parsed as PAGE_HOST ok plus RIGHT_FAMILY al, occurs as f82r label and internal prose group','active_semantic_assignments':0,'interpretation':'The f82r cross-scope equality is a full rendered-group tuple, not evidence for an opaque PAGE_HOST okal content address.','claim_ceiling':'Layer correction and exact tuple reuse only; no referent function word language plaintext or translation.','f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{p:sha(p) for p in [OLD,BFE,F82,MAN,CTX,DIR]},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt249_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'parse':result['corrected_okal_parse'],'ok_host':result['ok_host']},sort_keys=True))
if __name__=='__main__':main()
