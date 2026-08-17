#!/usr/bin/env python3
"""Freeze GDT225 mechanisms before joining B3 and label rows."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;OLD=R/'gdt224_result.json';REC=R/'gdt224_record_role_summary.tsv';PROJ=R/'gdt224_field_role_projection.tsv';FRAME=R/'gdt046_line_frames.tsv';LABELS=R/'gdt012_annotated_core_inventory.tsv';METHOD=R/'GDT225_Q13_DISTRIBUTED_CLOSURE_FREEZE_METHOD.md';OUT=R/'gdt225_prediction_freeze.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
old=json.loads(OLD.read_text());assert old['target']['records']==33 and old['control']['records']==22 and not any(old['f84'].values())
v={'schema':'GDT225_Q13_DISTRIBUTED_CLOSURE_FREEZE_V1','status':'FROZEN_BEFORE_B3_AND_FOLLOWING_LABEL_JOIN','target_records':33,'control_records':22,'mechanisms':['FINAL_LINE_B3','FOLLOWING_LABEL_BLOCK','UNION_DISTRIBUTED_CLOSURE_PROXY'],'predictions':['Q13_MISSING_CLOSER_PROXY_RATE_EXCEEDS_HERBAL','Q13_PROXY_ENRICHED_WHEN_FIELD_CLOSER_MISSING','EXPANDED_CLOSURE_REDUCES_DEFICIT_BY_AT_LEAST_HALF'],'required_lofo_positive':8,'f84':{'accessed':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (OLD,REC,PROJ,FRAME,LABELS)},'documents':{METHOD.name:sha(METHOD)},'implementation':{Path(__file__).name:sha(Path(__file__))}}
v['freeze_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(v['status'])
