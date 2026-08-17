#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;checks=[]
def ck(x):checks.append(bool(x));assert x
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
z=json.loads((R/'gdt239_result.json').read_text());m=json.loads((R/'gdt239_f82r_page_model.json').read_text())
for k in ('inputs','outputs','documents','implementation'):
 for p,h in z[k].items():ck(sha(p)==h)
lab=list(csv.DictReader((R/'gdt239_f82r_label_dossier.tsv').open(),delimiter='\t'));fld=list(csv.DictReader((R/'gdt239_f82r_field_dossier.tsv').open(),delimiter='\t'))
ck(len(lab)==13);ck(len(fld)==26);ck(all(x['page']=='f82r' for x in lab+fld));ck(all(x['semantic_value']=='UNASSIGNED' for x in lab+fld))
ck(len({x['locus'] for x in fld})==z['formal_counts']['covered_prose_loci']==8);ck(z['formal_counts']['human_prose_locus_coverage']==.25)
ck(sum(x['ownership_evidence']=='CONNECTED_COMPONENT' for x in lab)==1);ck(sum(x['ownership_evidence']=='PROXIMITY_ONLY' for x in lab)==12)
ck(sum(x['abstract_role_like']=='SHORT_ARGUMENT_LIKE' for x in fld)==16);ck(sum(x['abstract_role_like']=='INSTRUCTION_CLAUSE_LIKE' for x in fld)==10)
ck(sum(x['line_field_end']=='DY' for x in fld)==19);ck(sum(x['line_field_end']=='LINE_END' for x in fld)==7)
ck(m['lexical_assignments']==z['lexical_assignments']==0);ck(z['f84']=={'input':False,'joined':False,'new_access':False,'retained':False,'scored':False})
ck(z['status']=='F82R_VISUAL_LABEL_DOSSIER_COMPLETE_PROSE_LATTICE_PARTIAL_NO_LEXICAL_KEY')
core=dict(z);got=core.pop('content_hash');ck(hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':')).encode()).hexdigest()==got)
o={'experiment':z['experiment'],'status':'PASS','checks_passed':len(checks),'checks_total':len(checks),'result_hash':sha('gdt239_result.json')};(R/'gdt239_validation.json').write_text(json.dumps(o,indent=2,sort_keys=True)+'\n');print(f'PASS {len(checks)}/{len(checks)}')
