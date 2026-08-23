#!/usr/bin/env python3
from pathlib import Path
import csv, json
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def read(name):
    with (HERE/name).open(encoding="utf-8",newline="") as f: return list(csv.DictReader(f,delimiter="\t"))
s=read("FOURTH_487_SURFACE_DICTIONARY.tsv"); l=read("FOURTH_776_SPEAKABLE_LEDGER.tsv"); u=read("FOURTH_258_READING_UNITS.tsv"); c=read("FOURTH_RECLASSIFIED_487_SURFACES.tsv"); a=read("FOURTH_AUTONOMY_SUMMARY.tsv")
base_dir=ROOT/'experiments/yolo/sidequest_semantic_ten_page_workshop_edition'
def read_path(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
base_s=read_path(base_dir/'TEN_PAGE_487_SURFACE_DICTIONARY.tsv');base_l=read_path(base_dir/'TEN_PAGE_776_SPEAKABLE_LEDGER.tsv');base_u=read_path(base_dir/'TEN_PAGE_258_READING_UNITS.tsv')
checks={
 "487_surfaces":len(s)==487 and len({r['visible_surface'] for r in s})==487,
 "776_groups":len(l)==776,
 "381_prose":sum(r['register']=='PROSE' for r in l)==381,
 "395_astro":sum(r['register']=='ASTRO' for r in l)==395,
 "258_units":len(u)==258,
 "116_prose_units":sum(r['register']=='PROSE' for r in u)==116,
 "142_astro_units":sum(r['register']=='ASTRO' for r in u)==142,
 "36_table_stem_surfaces":sum(r['classification']=='ASTRO_LOCAL_PRODUCTIVE_TABLE_STEM' for r in c)==36,
 "43_table_stem_groups":sum(r['lookup_mode']=='ASTRO_LOCAL_TABLE_STEM' for r in l)==43,
 "36_surface_rows_changed":sum(x!=y for x,y in zip(s,base_s))==36,
 "30_units_changed":sum(x!=y for x,y in zip(u,base_u))==30,
 "prose_rows_unchanged":all(x==y for x,y in zip(l,base_l) if x['register']=='PROSE'),
 "43_group_values_revised":sum((x['atom_sequence'],x['short_value_de'],x['lookup_mode'])!=(y['atom_sequence'],y['short_value_de'],y['lookup_mode']) for x,y in zip(l,base_l))==43,
 "full_518":sum(int(r['visible_groups']) for r in a if r['composition_autonomy'].startswith('FULL'))==518,
 "partial_163":next(int(r['visible_groups']) for r in a if r['composition_autonomy']=='PARTIAL')==163,
 "whole_95":next(int(r['visible_groups']) for r in a if r['composition_autonomy']=='NONE')==95,
 "report_present":(HERE/'FOURTH_EDITION_REPORT.md').exists(),
}
sealed='f'+'84'; checks['sealed_token_absent']=all(sealed not in p.read_text(encoding='utf8').lower() for p in HERE.iterdir() if p.is_file())
result={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2));
if result['status']!='PASS':raise SystemExit(1)
