#!/usr/bin/env python3
from pathlib import Path
import csv,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(n):
 with (HERE/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def readp(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
s=read('SIXTH_487_SURFACE_DICTIONARY.tsv');l=read('SIXTH_776_SPEAKABLE_LEDGER.tsv');u=read('SIXTH_258_READING_UNITS.tsv');c=read('SIXTH_RECLASSIFIED_487_SURFACES.tsv');a=read('SIXTH_776_GROUP_AUTONOMY.tsv');al=read('RENDERER_26_ALLOGRAPHS.tsv');b=read('FOUR_BARE_FRAME_CARDS.tsv')
base=ROOT/'experiments/yolo/sidequest_semantic_ten_page_workshop_fifth_edition';bl=readp(base/'FIFTH_776_SPEAKABLE_LEDGER.tsv')
checks={'487':len(s)==487,'776':len(l)==776,'258':len(u)==258,'26_allographs':len(al)==26,'39_allograph_groups':sum(int(r['occurrences']) for r in al)==39,'four_bare':len(b)==4 and sum(int(r['occurrences']) for r in b)==8,'39_group_updates':sum(r['lookup_mode']=='ASTRO_REGISTERED_RENDERER_ALLOGRAPH' for r in l)==39,'prose_unchanged':all(x==y for x,y in zip(l,bl) if x['register']=='PROSE'),'full_558':sum(r['autonomy']=='FULL' for r in a)==558,'partial_130':sum(r['autonomy']=='PARTIAL' for r in a)==130,'whole_88':sum(r['autonomy']=='NONE' for r in a)==88,'two_splits':sum(r['composition_autonomy']=='REGISTER_SPLIT' for r in c)==2,'report_present':(HERE/'SIXTH_EDITION_REPORT.md').exists()}
sealed='f'+'84';checks['sealed_token_absent']=all(sealed not in p.read_text(encoding='utf8').lower() for p in HERE.iterdir() if p.is_file())
res={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'VALIDATION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(res,ensure_ascii=False,indent=2));
if res['status']!='PASS':raise SystemExit(1)
