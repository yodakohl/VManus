"""Verify the source-collation trace without repairing the printed example."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[3]
s=json.loads((B/'SOURCES.json').read_text());t=json.loads((B/'TRACE.json').read_text())
for im in s['images']:assert hashlib.sha256((R/im['path']).read_bytes()).hexdigest()==im['sha256']
old=json.loads((B.parent/'trithemius_source_20261010/TABLE.json').read_text());labels=t['message_prefix_table_labels'];assert labels=='cavetibiab';assert len(t['cells'])==10
for i,c in enumerate(t['cells']):
 assert c['column']==i+1 and c['expected_message_label']==labels[i]
 if i<4:assert old['columns'][i]['words'][old['alphabet_labels'].index(labels[i])]==c['table_entry']
assert t['column6_countercase']['table_cell']!=t['column6_countercase']['author_reading']
x=t['column10_countercase'];assert x['expected_letter']=='b' and x['expected_cell']=='celestibus' and x['other_row_letter']=='a' and x['other_row_cell']=='celis';assert x['expected_letter']!=x['other_row_letter']
nulls={p['after_column']:p['chosen'] for p in t['supplied_null_phrases']};words=[]
for c in t['cells']:words+=c['table_entry'].split()+nulls.get(c['column'],[])
assert len(words)==15 and len(labels)==10
for c in t['multiword_cell_examples']:assert c['column']==10 and len(c['tokens'])==2
assert t['cells'][6]['assessment']=='ENDING_READING_UNRESOLVED'
result={'status':'PASS_CORRECTION_CHECK','full_author_period_recovery':False,'preserved_author_four_letter_example':'caue','canonical_table_regeneration':words,'canonical_source_label_prefix':labels,'canonical_cover_words':len(words),'message_cells':10,'supplied_null_words':5,'multiword_cell_examples':3,'scope':'Bookkeeping and integrity of manual primary-source observations. No image OCR validation, full-book decoder, source emendation or Voynich result.'}
(B/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
