#!/usr/bin/env python3
from pathlib import Path
import csv,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(n):
 with (HERE/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def readp(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
s=read('FIFTH_487_SURFACE_DICTIONARY.tsv');l=read('FIFTH_776_SPEAKABLE_LEDGER.tsv');u=read('FIFTH_258_READING_UNITS.tsv');c=read('FIFTH_RECLASSIFIED_487_SURFACES.tsv');a=read('FIFTH_776_GROUP_AUTONOMY.tsv')
b=ROOT/'experiments/yolo/sidequest_semantic_ten_page_workshop_fourth_edition';bl=readp(b/'FOURTH_776_SPEAKABLE_LEDGER.tsv');bu=readp(b/'FOURTH_258_READING_UNITS.tsv')
checks={'487':len(s)==487,'776':len(l)==776,'258':len(u)==258,'381_prose':sum(r['register']=='PROSE' for r in l)==381,'395_astro':sum(r['register']=='ASTRO' for r in l)==395,'36_od_groups':sum(r['lookup_mode']=='ASTRO_OD_MARKED_ENTRY_MODIFIER' for r in l)==36,'28_od_surfaces':sum(r['classification'] in {'ASTRO_OD_PRODUCTIVE_MODIFIER','REGISTER_SPLIT_ASTRO_OD_PROSE_WHOLE'} for r in c)==28,'prose_unchanged':all(x==y for x,y in zip(l,bl) if x['register']=='PROSE'),'36_group_values_changed':sum((x['atom_sequence'],x['short_value_de'],x['lookup_mode'])!=(y['atom_sequence'],y['short_value_de'],y['lookup_mode']) for x,y in zip(l,bl))==36,'full_543':sum(r['autonomy']=='FULL' for r in a)==543,'partial_144':sum(r['autonomy']=='PARTIAL' for r in a)==144,'whole_89':sum(r['autonomy']=='NONE' for r in a)==89,'one_register_split':sum(r['composition_autonomy']=='REGISTER_SPLIT' for r in c)==1,'report_present':(HERE/'FIFTH_EDITION_REPORT.md').exists()}
sealed='f'+'84';checks['sealed_token_absent']=all(sealed not in p.read_text(encoding='utf8').lower() for p in HERE.iterdir() if p.is_file())
res={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'VALIDATION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(res,ensure_ascii=False,indent=2));
if res['status']!='PASS':raise SystemExit(1)
