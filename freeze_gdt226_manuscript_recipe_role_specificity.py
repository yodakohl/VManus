#!/usr/bin/env python3
"""Freeze manuscript-wide GDT176 role-specificity scopes before projection."""
import csv,hashlib,json,re
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
FRAME=R/'gdt046_line_frames.tsv';GROUPS=R/'gdt016_group_state_inventory.tsv';EXT=R/'gdt176_external_role_units.tsv';OLD=R/'gdt176_result.json';G224=R/'gdt224_result.json';METHOD=R/'GDT226_MANUSCRIPT_RECIPE_ROLE_SPECIFICITY_FREEZE_METHOD.md';OUT=R/'gdt226_prediction_freeze.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
def pn(p):return int(re.match(r'f(\d+)',p).group(1))
def scope(r):
 if r['register']=='HA':return 'HERBAL_A'
 if r['register']=='HB':return 'HERBAL_B'
 if r['register']=='SB':return 'STARS_B'
 if r['register']=='OA':return 'OTHER_A'
 if r['register']=='OB' and 75<=pn(r['page'])<=83:return 'Q13'
 if r['register']=='OB':return 'OTHER_B'
 raise AssertionError(r['register'])
rows=[]
with FRAME.open(encoding='utf8',newline='') as h:
 for r in csv.DictReader(h,delimiter='\t'):
  if r['page'].startswith('f84'):continue
  rows.append((scope(r),r['page'],r['physical_folio'],r['locus']))
counts=Counter(x[0] for x in rows);pages={s:len({x[1] for x in rows if x[0]==s}) for s in counts};folios={s:len({x[2] for x in rows if x[0]==s}) for s in counts}
v={'schema':'GDT226_MANUSCRIPT_RECIPE_ROLE_SPECIFICITY_FREEZE_V1','status':'FROZEN_BEFORE_SIX_SCOPE_ROLE_PROJECTION','scope_rule':'HA_HB_SB_OA_Q13_F75_TO_F83_REMAINING_OB','line_counts':dict(sorted(counts.items())),'page_counts':dict(sorted(pages.items())),'folio_counts':dict(sorted(folios.items())),'instrument':'UNCHANGED_GDT176_POSITION_LENGTH','field_rule':'DY_CLOSURE_OR_LINE_END','record_rule':'PAGE_OR_EDITOR_PARAGRAPH_START','predictions':[{'id':'P1','rule':'Q13_RECIPE_JS_LT_HERBAL_A_AND_HERBAL_B'},{'id':'P2','rule':'Q13_RECIPE_JS_RANK_LE_2_OF_6'},{'id':'P3','rule':'Q13_NEAREST_OTHER_SCOPE_IS_STARS_B'}],'decision_rule':'ALL_3_DIRECTIONS_AND_AT_LEAST_8_OF_9_Q13_FOLIO_DELETIONS','prior_exposure':'P1_Q13_VS_HERBAL_B_AND_PUBLISHED_STARS_PROJECTION_ALREADY_EXPOSED','f84':{'public_metadata_previously_exposed':True,'source_or_formal_payload_retained':False,'joined':False,'scored':False,'future_access_authorized':False},'inputs':{p.name:sha(p) for p in (FRAME,GROUPS,EXT,OLD,G224)},'documents':{METHOD.name:sha(METHOD)},'implementation':{Path(__file__).name:sha(Path(__file__))}}
v['freeze_content_sha256']=csha(v);OUT.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':v['status'],'line_counts':v['line_counts']},sort_keys=True))
