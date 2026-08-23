#!/usr/bin/env python3
from pathlib import Path
import csv,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(n):
 with (HERE/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def readp(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
s=read('EIGHTH_487_SURFACE_DICTIONARY.tsv');l=read('EIGHTH_776_SPEAKABLE_LEDGER.tsv');u=read('EIGHTH_258_READING_UNITS.tsv');c=read('EIGHTH_RECLASSIFIED_487_SURFACES.tsv');a=read('EIGHTH_776_GROUP_AUTONOMY.tsv');p=read('CHEEY_10_SURFACE_PARADIGM.tsv')
base=ROOT/'experiments/yolo/sidequest_semantic_astro_local_content_seventh_edition';bl=readp(base/'SEVENTH_776_SPEAKABLE_LEDGER.tsv')
checks={'487':len(s)==487,'776':len(l)==776,'258':len(u)==258,'ten_surfaces':len(p)==10,'fifteen_groups':sum(int(r['total_groups']) for r in p)==15,'nine_astro_updates':sum(r['lookup_mode']=='CROSS_REGISTER_CHEEY_READOUT' for r in l)==9,'six_prose_bindings':sum(r['lookup_mode']=='CROSS_REGISTER_CHEEY_WET_RESULT' for r in l)==6,'other_prose_unchanged':all(x==y for x,y in zip(l,bl) if x['register']=='PROSE' and x['visible_surface'] not in {r['visible_surface'] for r in p}),'full_593':sum(r['autonomy']=='FULL' for r in a)==593,'partial_121':sum(r['autonomy']=='PARTIAL' for r in a)==121,'whole_62':sum(r['autonomy']=='NONE' for r in a)==62,'three_splits':sum(r['composition_autonomy']=='REGISTER_SPLIT' for r in c)==3,'report_present':(HERE/'EIGHTH_EDITION_REPORT.md').exists()}
sealed='f'+'84';checks['sealed_token_absent']=all(sealed not in x.read_text(encoding='utf8').lower() for x in HERE.iterdir() if x.is_file())
res={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'VALIDATION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(res,ensure_ascii=False,indent=2));
if res['status']!='PASS':raise SystemExit(1)
