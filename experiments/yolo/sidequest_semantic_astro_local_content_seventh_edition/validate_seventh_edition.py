#!/usr/bin/env python3
from pathlib import Path
import csv,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(n):
 with (HERE/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def readp(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
s=read('SEVENTH_487_SURFACE_DICTIONARY.tsv');l=read('SEVENTH_776_SPEAKABLE_LEDGER.tsv');u=read('SEVENTH_258_READING_UNITS.tsv');c=read('SEVENTH_RECLASSIFIED_487_SURFACES.tsv');a=read('SEVENTH_776_GROUP_AUTONOMY.tsv');roots=read('THREE_LOCAL_ROOTS.tsv');t=read('LOCAL_ROOT_17_TYPE_PARADIGM.tsv');g=read('LOCAL_ROOT_20_GROUP_READINGS.tsv')
base=ROOT/'experiments/yolo/sidequest_semantic_renderer_completed_sixth_edition';bl=readp(base/'SIXTH_776_SPEAKABLE_LEDGER.tsv')
checks={'487':len(s)==487,'776':len(l)==776,'258':len(u)==258,'three_roots':len(roots)==3,'17_types':len(t)==17,'20_groups':len(g)==20,'20_updates':sum(r['lookup_mode']=='ASTRO_LOCAL_AM_G_OS_ROOT' for r in l)==20,'prose_unchanged':all(x==y for x,y in zip(l,bl) if x['register']=='PROSE'),'full_578':sum(r['autonomy']=='FULL' for r in a)==578,'partial_123':sum(r['autonomy']=='PARTIAL' for r in a)==123,'whole_75':sum(r['autonomy']=='NONE' for r in a)==75,'three_splits':sum(r['composition_autonomy']=='REGISTER_SPLIT' for r in c)==3,'report_present':(HERE/'SEVENTH_EDITION_REPORT.md').exists()}
sealed='f'+'84';checks['sealed_token_absent']=all(sealed not in p.read_text(encoding='utf8').lower() for p in HERE.iterdir() if p.is_file())
res={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'VALIDATION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(res,ensure_ascii=False,indent=2));
if res['status']!='PASS':raise SystemExit(1)
