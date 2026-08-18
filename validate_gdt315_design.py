#!/usr/bin/env python3
"""Validate GDT315 control freeze."""
import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;PANEL=R/'gdt315_frozen_panel.tsv';CAP=R/'gdt315_capacity.tsv';DESIGN=R/'gdt315_design.json';OUT=R/'gdt315_design_validation.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def can(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding='utf8',newline='') as h:return list(csv.DictReader(h,delimiter='\t'))
def main():
 c=[]
 def ck(n,v):
  if not v:raise AssertionError(n)
  c.append(n)
 d=json.loads(DESIGN.read_text());stored=d.pop('content_sha256');ck('content',stored==can(d));p=read(PANEL);cap={x['panel']:x for x in read(CAP)};expected={'ARBITRARY_LOCAL_CODEBOOK':(67,1542,292,171),'COMPOSITIONAL_TECHNICAL_NOTATION':(52,1696,197,173),'HYBRID_SHORTHAND':(63,1488,277,175),'IFORAL_1395_1411_GRAPHEMATIC':(13,231,57,6),'LATIN_15C_GRAPHEMATIC':(14,167,82,11),'LATIN_MEDICAL_GRAPHEMATIC':(10,184,38,10),'LATIN_SCHOLASTIC_GRAPHEMATIC':(7,319,48,6),'VOYNICH_REFERENCE':(15,344,35,78)};ck('capacity',all(tuple(int(cap[k][x]) for x in ('cells','events','s_events','folios'))==v for k,v in expected.items()));ck('panels',set(d['powered_panels'])==set(expected) and {x['panel'] for x in p}==set(expected));ck('rows',len(p)==sum(v[1] for v in expected.values()));ck('unique',len(p)==len({(x['panel'],x['event_id_sha256']) for x in p}));ck('withheld',{x['s_choice_withheld'] for x in p}=={'WITHHELD_UNTIL_SCORING'});ck('f84',not any(x['page'].startswith('f84') or x['locus'].startswith('f84') for x in p) and not any(d['f84'].values()));ck('hashes',all(d['inputs'][n]==sha(R/n) for n in d['inputs']) and all(d['outputs'][n]==sha(R/n) for n in d['outputs']));v={'schema':'GDT315_DESIGN_VALIDATION_V1','status':'PASS','checks_passed':len(c),'checks':c,'design_sha256':sha(DESIGN),'f84_rows':0};v['content_sha256']=can(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','checks':len(c)},sort_keys=True))
if __name__=='__main__':main()
