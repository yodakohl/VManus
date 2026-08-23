#!/usr/bin/env python3
from pathlib import Path
import csv,json
HERE=Path(__file__).resolve().parent
def read(n):
 with (HERE/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
t=read('OD_28_TYPE_PARADIGM.tsv');g=read('OD_36_GROUP_READINGS.tsv');c=read('OD_CONTRASTS.tsv');p=read('OD_FORWARD_CELLS.tsv')
checks={'types_28':len(t)==28,'groups_36':len(g)==36,'owners_28':len({r['visible_owner'] for r in g})==28,'contrasts_11':len(c)==11,'forward_6':len(p)==6,'constant_od':all(r['od_contribution_de']=='MARKIERT/EINGETRAGEN' for r in t),'unique_groups':len({r['group_serial'] for r in g})==36,'report_present':(HERE/'OD_MARKED_ENTRY_REPORT.md').stat().st_size>2000}
sealed='f'+'84';checks['sealed_token_absent']=all(sealed not in x.read_text(encoding='utf8').lower() for x in HERE.iterdir() if x.is_file())
res={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks};(HERE/'VALIDATION.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(res,ensure_ascii=False,indent=2));
if res['status']!='PASS':raise SystemExit(1)
