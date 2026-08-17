#!/usr/bin/env python3
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent
AUDIT=R/'GDT002_EXISTING_VISUAL_EVIDENCE_AUDIT.md';PROJ=R/'gdt002_grammar_projection.tsv';OLD=R/'gdt229_q13_semantic_role_lattice.tsv'
OUTS=['gdt244_f80r_paragraph_coordinate.tsv','gdt244_f80r_record_correction.tsv']
DOCS=['GDT244_F80R_PARAGRAPH_COORDINATE_CORRECTION_METHOD.md','GDT244_F80R_PARAGRAPH_COORDINATE_CORRECTION_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def only(path,page='f80r'):
 out=[]
 with path.open(encoding='utf-8') as f:
  h=f.readline().rstrip('\n').split('\t');pi=h.index('page')
  for raw in f:
   a=raw.rstrip('\n').split('\t')
   if a[pi]!=page:continue
   out.append(dict(zip(h,a)))
 return out
def write(n,rows):
 with (R/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 text=AUDIT.read_text();assert 'paragraph lines, 10 upper figure labels, and five paragraphs' in text and '43' in text
 pr=only(PROJ);old=only(OLD);first=defaultdict(list)
 for x in pr:
  if x['kind']=='P' and x['source_group_index']=='1':first[x['locus']].append(x)
 loci=sorted(first,key=lambda x:int(x.split('.')[1]));starts=[];single=[]
 for loc in loci:
  marked=sorted(x['edition'] for x in first[loc] if x['paragraph_start']=='1')
  if len(marked)>=2:starts.append(loc)
  elif len(marked)==1:single.append(loc)
 assert starts==['f80r.11','f80r.28','f80r.34','f80r.40','f80r.47'] and single==['f80r.18']
 nums=[int(x.split('.')[1]) for x in starts];rows=[]
 for loc in loci:
  n=int(loc.split('.')[1]);pid=1+sum(n>=s for s in nums[1:]);members=[x for x in loci if 1+sum(int(x.split('.')[1])>=s for s in nums[1:])==pid]
  marked=','.join(sorted(x['edition'] for x in first[loc] if x['paragraph_start']=='1')) or 'NONE';oldids=sorted({x['record_id'] for x in old if x['locus']==loc})
  rows.append({'page':'f80r','locus':loc,'paragraph_id':f'P{pid}','paragraph_line_ordinal':members.index(loc)+1,'paragraph_line_count':len(members),'source_editions_marking_start':marked,'majority_paragraph_start':int(loc in starts),'single_reading_start_disagreement':int(loc in single),'gdt229_role_available':int(bool(oldids)),'historical_gdt229_record_ids':','.join(oldids) or 'NONE'})
 write(OUTS[0],rows)
 corr=[]
 for pid in [f'P{i}' for i in range(1,6)]:
  rr=[x for x in rows if x['paragraph_id']==pid];ids=sorted({x['historical_gdt229_record_ids'] for x in rr if x['historical_gdt229_record_ids']!='NONE'})
  corr.append({'page':'f80r','corrected_paragraph_id':pid,'physical_prose_loci':len(rr),'gdt229_role_covered_loci':sum(x['gdt229_role_available'] for x in rr),'historical_gdt229_record_ids':','.join(ids) or 'NONE','correction_state':'PARAGRAPH_COLLAPSED_IN_HISTORICAL_ROLE_COORDINATE'})
 write(OUTS[1],corr)
 hist=sorted({x['record_id'] for x in old});result={'experiment':'GDT244_F80R_PARAGRAPH_COORDINATE_CORRECTION','status':'GDT229_F80R_RECORD_COORDINATE_INVALID_FIVE_PARAGRAPHS_COLLAPSED_TO_TWO','source_paragraphs':5,'paragraph_starts':starts,'single_reading_disagreement':single,'paragraph_line_counts':[sum(x['paragraph_id']==f'P{i}' for x in rows) for i in range(1,6)],'historical_records':hist,'historical_role_loci_by_paragraph':[sum(x['gdt229_role_available'] for x in rows if x['paragraph_id']==f'P{i}') for i in range(1,6)],
 'correction':'Withdraw f80r GDT229 record-relative abstract roles and treat every unaudited q13 record coordinate as provisional until its full paragraph starts are checked.',
 'interpretation':'The frame-selected role lattice merges f80r paragraphs P1-P3 into historical R01 and P4-P5 into R02.',
 'claim_ceiling':'Coordinate correction only; no replacement semantic role, word, language, plaintext, or translation.',
 'f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{str(x.relative_to(R)):sha(str(x.relative_to(R))) for x in (AUDIT,PROJ,OLD)},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt244_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'starts':starts,'single':single,'line_counts':result['paragraph_line_counts'],'role_loci':result['historical_role_loci_by_paragraph'],'old_records':hist},sort_keys=True))
if __name__=='__main__':main()
