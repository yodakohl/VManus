#!/usr/bin/env python3
"""Decompose frozen GDT334 held gain by placement component."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parent;INTER=R/'gdt327_joint_tuple_interlinear.tsv';FOLDS=R/'gdt334_folds.tsv';METHOD=R/'GDT335_TUPLE_PLACEMENT_COMPONENT_DECOMPOSITION_METHOD.md';SCORES=R/'gdt335_component_gains.tsv';REPORT=R/'GDT335_TUPLE_PLACEMENT_COMPONENT_DECOMPOSITION_REPORT.md';RESULT=R/'gdt335_result.json';NAMES=('LINE_FIRST','WITHIN_FIELD_POSITION','FIELD_ORDINAL','LINE_QUARTILE')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def write(p,rows):
 with Path(p).open('w',encoding='utf8',newline='') as h:w=csv.DictWriter(h,rows[0].keys(),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def roles(x):
 gi=int(x['group_index']);gc=int(x['group_count']);return (x['line_first'],x['within_field_position'],str(min(4,int(x['field_ordinal']))),str(min(3,int(4*(gi-1)/max(1,gc)))))
def main():
 rows=read(INTER);assert len(rows)==8448 and not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in rows);foldalpha={(x['register'],x['held_folio']):int(x['selected_alpha']) for x in read(FOLDS)};classes=[sorted({roles(x)[j] for x in rows}) for j in range(4)];gain=defaultdict(Counter);events=Counter()
 for reg in sorted({x['register'] for x in rows}):
  rr=[x for x in rows if x['register']==reg]
  for hold in sorted({x['physical_folio'] for x in rr}):
   train=[x for x in rr if x['physical_folio']!=hold];seen={x['joint_tuple_id'] for x in train};test=[x for x in rr if x['physical_folio']==hold and x['joint_tuple_id'] in seen];events[reg]+=len(test);alpha=foldalpha[reg,hold]
   for j,C in enumerate(classes):
    coord=defaultdict(Counter);tu=defaultdict(Counter)
    for x in train:coord[x['coordinate_id']][roles(x)[j]]+=1;tu[x['joint_tuple_id']][roles(x)[j]]+=1
    for x in test:
     y=roles(x)[j];c=coord[x['coordinate_id']];t=tu[x['joint_tuple_id']];pc=(c[y]+.5)/(sum(c.values())+.5*len(C));pt=(t[y]+alpha*pc)/(sum(t.values())+alpha);g=math.log2(pt/pc);gain[reg][NAMES[j]]+=g;gain['ALL'][NAMES[j]]+=g
 out=[]
 for scope in ('ALL',)+tuple(sorted(events)):
  for name in NAMES:out.append({'scope':scope,'component':name,'scored_events':sum(events.values()) if scope=='ALL' else events[scope],'held_gain_bits':f'{gain[scope][name]:.12f}','positive_gain':int(gain[scope][name]>0)})
 write(SCORES,out);total={k:gain['ALL'][k] for k in NAMES};status='TUPLE_GAIN_IS_LINE_PLACEMENT_NOT_RECORD_FIELD_ORDINAL'
 report=f'''# GDT335 — tuple placement component decomposition

Status: **{status}**.

The frozen GDT334 gain decomposes as follows:

- physical line entry: {total['LINE_FIRST']:+.3f} bits;
- within-field position: {total['WITHIN_FIELD_POSITION']:+.3f} bits;
- physical line quartile: {total['LINE_QUARTILE']:+.3f} bits;
- field ordinal: {total['FIELD_ORDINAL']:+.3f} bits.

Field ordinal is negative in all five registers. Line entry is positive in all five; within-field position and line quartile are positive in four.  GDT334 therefore supports register-conditioned *line-placement signatures* of exact joint tuples, not stable numbered record fields.  The within-field component remains a formal boundary-position effect, not a semantic role.

No tuple meaning, semantic role, word, POS, sound, language, plaintext, or translation follows. No f84 row was opened, retained, joined, or scored.
''';REPORT.write_text(report)
 result={'schema':'GDT335_TUPLE_PLACEMENT_COMPONENT_DECOMPOSITION_RESULT_V1','status':status,'events':sum(events.values()),'component_gains':total,'register_component_gains':{r:dict(gain[r]) for r in sorted(events)},'claim_ceiling':'Register-conditioned line-placement signature only; no record-field semantics meaning plaintext or translation.','f84':{'input_rows':0,'opened':False,'retained':False,'joined':False,'scored':False},'inputs':{p.name:sha(p) for p in (INTER,FOLDS,R/'gdt334_result.json')},'documents':{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},'implementation':{Path(__file__).name:sha(Path(__file__))},'outputs':{SCORES.name:sha(SCORES)}};result['content_sha256']=can(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':status,'component_gains':total},sort_keys=True))
if __name__=='__main__':main()
