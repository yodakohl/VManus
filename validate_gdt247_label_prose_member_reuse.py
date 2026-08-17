#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt247_result.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
m=list(csv.DictReader((R/'gdt247_exact_label_prose_member_matches.tsv').open(),delimiter='\t'));c=list(csv.DictReader((R/'gdt247_page_recurrence_context.tsv').open(),delimiter='\t'));x=list(csv.DictReader((R/'gdt247_counterexamples.tsv').open(),delimiter='\t'))
ck(len(m)==3);ck([(r['member_surface'],r['label_locus'],r['prose_locus']) for r in m]==[('okaly','f80r.3','f80r.31'),('olky','f80r.7','f80r.38'),('okal','f82r.36','f82r.6')])
ck([int(r['aligned_label_groups']) for r in c]==[10,13]);ck([int(r['aligned_prose_groups']) for r in c]==[426,268]);ck([int(r['label_groups_with_exact_prose_match']) for r in c]==[2,1])
ck(all(r['all_reading_member_identity']=='EXACT_ZL3b_IT2a_RF1b' for r in m));ck(all(r['prose_group_position']=='LINE_INTERNAL' for r in m));ck(all(r['ownership_evidence']=='PROXIMITY_ONLY' for r in m));ck(all(r['semantic_value']=='UNASSIGNED' for r in m))
ck({r['transferred_label_prefix'] for r in m}=={'AQAB','ABQA'});ck(len(x)==5);ck(z['exact_matches']==3 and z['aligned_label_groups']==23 and z['aligned_prose_groups']==694);ck(z['active_semantic_assignments']==0)
ck(z['status']=='MINORITY_EXACT_LABEL_TO_PROSE_CODE_INTERFACE_DESCRIPTIVE_NOT_SEMANTIC');ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt247_result.json')};(R/'gdt247_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')
