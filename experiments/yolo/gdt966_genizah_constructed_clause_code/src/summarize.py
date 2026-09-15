"""Derive compact tables from independently validated full case receipts."""
from pathlib import Path
import json,csv,collections,hashlib
p=Path('experiments/yolo/gdt966_genizah_constructed_clause_code')
a=p/'artifacts'
cases=json.loads((a/'ALL_CASES.json').read_text()); sources=json.loads((a/'GENERATED_PARAGRAPHS.json').read_text())
with (a/'SOURCE_CANDIDATE_SUMMARY.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['source_id','whole_source','whole_working_translation','required_word_count','tested_targets','word_count_contradictions','same_count_contradictions','survivors','independent_confirmation_capacity'])
 for s in sources:
  rows=[r for r in cases if r['source_id']==s['id']];wc=sum(any(x['kind']=='WORD_COUNT' for x in r['contradictions']) for r in rows)
  w.writerow([s['id'],' '.join(s['words']),s['working_translation'],s['word_count'],len(rows),wc,len(rows)-wc,0,0])
with (a/'TARGET_SUMMARY.tsv').open('w',newline='') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['target_id','edition','page','physical_folio','source_candidates','word_count_contradictions','same_count_contradictions','survivors','independent_confirmation_capacity'])
 for tid in dict.fromkeys(r['target_id'] for r in cases):
  rows=[r for r in cases if r['target_id']==tid];r=rows[0];wc=sum(any(x['kind']=='WORD_COUNT' for x in r['contradictions']) for r in rows)
  w.writerow([tid,r['edition'],r['page'],r['physical_folio'],len(rows),wc,len(rows)-wc,0,0])
