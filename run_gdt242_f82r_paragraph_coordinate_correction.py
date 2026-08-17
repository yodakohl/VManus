#!/usr/bin/env python3
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
PAGE=R/'experiments/semantic_assumptions/results/existing_human_page_annotations.tsv';PROJ=R/'gdt002_grammar_projection.tsv';HPR=R/'gdt241_f82r_line_coverage.tsv';OLD=R/'gdt239_f82r_field_dossier.tsv'
OUTS=['gdt242_f82r_paragraph_coordinate.tsv','gdt242_f82r_record_correction.tsv']
DOCS=['GDT242_F82R_PARAGRAPH_COORDINATE_CORRECTION_METHOD.md','GDT242_F82R_PARAGRAPH_COORDINATE_CORRECTION_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def only(path):
 out=[]
 with path.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');pi=h.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t')
   if a[pi]!='f82r':continue
   out.append(dict(zip(h,a)))
 return out
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 page=only(PAGE)[0];pr=only(PROJ);hpr={x['locus']:x for x in only(HPR)};old=only(OLD)
 first={}
 for x in pr:
  if x['kind']=='P' and x['source_group_index']=='1':first.setdefault(x['locus'],[]).append(x)
 loci=sorted(first,key=lambda x:int(x.split('.')[1]));starts=[x for x in loci if first[x][0]['code'] in {'@P0','*P0'}]
 assert starts==['f82r.1','f82r.11','f82r.20'] and 'three paragraphs' in page['text_description'].lower()
 start_nums=[int(x.split('.')[1]) for x in starts];rows=[]
 for loc in loci:
  n=int(loc.split('.')[1]);pid=1+sum(n>=s for s in start_nums[1:]);members=[x for x in loci if 1+sum(int(x.split('.')[1])>=s for s in start_nums[1:])==pid];ordn=members.index(loc)+1
  codes=sorted({x['code'] for x in first[loc]});starts_by=','.join(sorted(x['edition'] for x in first[loc] if x['paragraph_start']=='1')) or 'NONE'
  rows.append({'page':'f82r','locus':loc,'source_codes':','.join(codes),'paragraph_id':f'P{pid}','paragraph_line_ordinal':ordn,'paragraph_line_count':len(members),'source_editions_marking_start':starts_by,'code_defined_paragraph_start':int(loc in starts),'hpr2_available':int(loc in hpr),'hpr2_field_count':int(hpr[loc]['hpr2_field_count']) if loc in hpr else 0,'gdt229_role_available':int(any(x['locus']==loc for x in old))})
 write(OUTS[0],rows)
 old_records=sorted({x['record_id'] for x in old});corr=[]
 for pid in ('P1','P2','P3'):
  rr=[x for x in rows if x['paragraph_id']==pid]
  corr.append({'page':'f82r','corrected_paragraph_id':pid,'physical_prose_loci':len(rr),'hpr2_covered_loci':sum(x['hpr2_available'] for x in rr),'hpr2_fields':sum(x['hpr2_field_count'] for x in rr),'gdt229_role_covered_loci':sum(x['gdt229_role_available'] for x in rr),'historical_gdt229_record_ids':','.join(old_records),'correction_state':'PARAGRAPH_BOUNDARY_MISSING_FROM_COMPLETE_LINE_FRAME_ROLE_COORDINATE_WITHDRAWN'})
 write(OUTS[1],corr)
 result={'experiment':'GDT242_F82R_PARAGRAPH_COORDINATE_CORRECTION','status':'GDT229_F82R_RECORD_COORDINATE_INVALID_THREE_PARAGRAPHS_COLLAPSED','source_paragraphs':3,'paragraph_starts':starts,'paragraph_line_counts':[sum(x['paragraph_id']==p for x in rows) for p in ('P1','P2','P3')],'hpr2_covered_by_paragraph':[sum(x['hpr2_available'] for x in rows if x['paragraph_id']==p) for p in ('P1','P2','P3')],'hpr2_fields_by_paragraph':[sum(x['hpr2_field_count'] for x in rows if x['paragraph_id']==p) for p in ('P1','P2','P3')],'historical_gdt229_record_ids':old_records,'historical_role_loci_by_paragraph':[sum(x['gdt229_role_available'] for x in rows if x['paragraph_id']==p) for p in ('P1','P2','P3')],
 'correction':'Withdraw f82r GDT229/GDT239 record-relative abstract role counts; retain source groups, PAGE_HOST/compiler parses, DY fields, label dossier, and formal coverage.',
 'interpretation':'The selected complete-line frame omitted every paragraph-start locus and merged three physical paragraphs into one role coordinate.',
 'claim_ceiling':'Coordinate correction only; no replacement semantic role, word, language, plaintext, or translation.',
 'f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(x.relative_to(R)):sha(str(x.relative_to(R))) for x in (PAGE,PROJ,HPR,OLD)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt242_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'line_counts':result['paragraph_line_counts'],'hpr2_lines':result['hpr2_covered_by_paragraph'],'fields':result['hpr2_fields_by_paragraph'],'old_records':old_records},sort_keys=True))
if __name__=='__main__':main()
