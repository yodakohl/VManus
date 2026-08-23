#!/usr/bin/env python3
from pathlib import Path
import csv,json
from collections import defaultdict,Counter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/'experiments/yolo/sidequest_semantic_ten_page_workshop_fourth_edition'
OD=ROOT/'experiments/yolo/sidequest_semantic_od_marked_entry_paradigm'

def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(path,fields,rows):
 with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

surfaces=read(BASE/'FOURTH_487_SURFACE_DICTIONARY.tsv');ledger=read(BASE/'FOURTH_776_SPEAKABLE_LEDGER.tsv');units=read(BASE/'FOURTH_258_READING_UNITS.tsv');classes=read(BASE/'FOURTH_RECLASSIFIED_487_SURFACES.tsv')
od_types={r['visible_surface']:r for r in read(OD/'OD_28_TYPE_PARADIGM.tsv')};od_groups={r['opaque_local_id']:r for r in read(OD/'OD_36_GROUP_READINGS.tsv')}

surface_out=[]
for row in surfaces:
 out=dict(row);target=od_types.get(row['visible_surface'])
 if target:
  if row['visible_surface']=='ody' and row['register_status']=='PROSE_AND_ASTRO':
   out['common_atom_sequences']='PROSE:ODY_WHOLE|ASTRO:OD+Y'
   out['common_nucleus_de']='PROSE:KÜHLEN || ASTRO:DIESEN POSTEN EINTRAGEN'
   out['reading_rule_de']='register split: Prosa-Ganzkarte bewahren; Astro als OD+Y lesen'
  else:
   out['common_atom_sequences']=target['revised_atom_sequence']
   out['common_nucleus_de']=target['revised_short_reading_de']
   out['reading_rule_de']='lies OD als markiert/eingetragen; längere registrierte Körper blockieren die Teilung'
  out['astro_short_values_de']=target['revised_short_reading_de']
 surface_out.append(out)
write(HERE/'FIFTH_487_SURFACE_DICTIONARY.tsv',list(surface_out[0]),surface_out)

ledger_out=[]
for row in ledger:
 out=dict(row);target=od_groups.get(row['source_group_id'])
 if target:
  out['atom_sequence']=target['revised_atom_sequence'];out['short_value_de']=target['revised_short_reading_de'];out['lookup_mode']='ASTRO_OD_MARKED_ENTRY_MODIFIER'
 ledger_out.append(out)

group_by_unit=defaultdict(list)
for r in ledger_out:group_by_unit[(r['register'],r['page'],r['reading_unit_id'])].append(r)
unit_out=[];changed=0
for row in units:
 out=dict(row)
 if row['register']=='ASTRO':
  gs=group_by_unit[(row['register'],row['page'],row['unit_id'])]
  if any(g['lookup_mode']=='ASTRO_OD_MARKED_ENTRY_MODIFIER' for g in gs):
   prefix=row['speakable_reading_de'].split(':',1)[0]
   out['speakable_reading_de']=prefix+': '+'; '.join(g['short_value_de'] for g in gs);changed+=1
 unit_out.append(out)
unit_lookup={(r['register'],r['page'],r['unit_id']):r['speakable_reading_de'] for r in unit_out}
for r in ledger_out:r['unit_reading_de']=unit_lookup[(r['register'],r['page'],r['reading_unit_id'])]
write(HERE/'FIFTH_776_SPEAKABLE_LEDGER.tsv',list(ledger_out[0]),ledger_out);write(HERE/'FIFTH_258_READING_UNITS.tsv',list(unit_out[0]),unit_out)

class_out=[]
for row in classes:
 out=dict(row);target=od_types.get(row['visible_surface'])
 if target:
  out['common_atom_sequences']=next(r['common_atom_sequences'] for r in surface_out if r['visible_surface']==row['visible_surface'])
  if row['visible_surface']=='ody':
   out['classification']='REGISTER_SPLIT_ASTRO_OD_PROSE_WHOLE';out['historical_layer']='ASTRO_MODIFIER_VS_PROSE_NOMENCLATOR';out['composition_autonomy']='REGISTER_SPLIT';out['apprentice_action_de']='im Astroregister OD+Y lesen, in Prosa ganze Karte lernen';out['memorized_body_or_residue']='PROSE:ODY_WHOLE'
  else:
   out['classification']='ASTRO_OD_PRODUCTIVE_MODIFIER';out['historical_layer']='BOUND_TABLE_MODIFIER';out['composition_autonomy']='FULL_WITH_OWNER';out['apprentice_action_de']='Grundkörper lesen, OD=markiert hinzufügen, Y/Argument rechts lesen';out['memorized_body_or_residue']='NONE'
  out['classification_evidence']='ASTRO_LOCAL:OD';out['short_spoken_value_de']=target['revised_short_reading_de']
 class_out.append(out)
write(HERE/'FIFTH_RECLASSIFIED_487_SURFACES.tsv',list(class_out[0]),class_out)

# Group-level autonomy avoids miscounting the register-split surface ODY.
class_by_surface={r['visible_surface']:r for r in class_out}
group_autonomy=[]
for row in ledger_out:
 cls=class_by_surface[row['visible_surface']]
 if row['lookup_mode']=='ASTRO_OD_MARKED_ENTRY_MODIFIER': autonomy='FULL'
 elif cls['composition_autonomy'].startswith('FULL'): autonomy='FULL'
 elif cls['composition_autonomy']=='PARTIAL': autonomy='PARTIAL'
 elif cls['composition_autonomy']=='REGISTER_SPLIT': autonomy='NONE'
 else: autonomy='NONE'
 group_autonomy.append({'unified_serial':row['unified_serial'],'register':row['register'],'page':row['page'],'source_group_id':row['source_group_id'],'visible_surface':row['visible_surface'],'autonomy':autonomy,'classification':cls['classification']})
write(HERE/'FIFTH_776_GROUP_AUTONOMY.tsv',list(group_autonomy[0]),group_autonomy)
counts=Counter(r['autonomy'] for r in group_autonomy)
summary_rows=[{'autonomy':k,'visible_groups':counts[k]} for k in ('FULL','PARTIAL','NONE')]
write(HERE/'FIFTH_AUTONOMY_SUMMARY.tsv',list(summary_rows[0]),summary_rows)

base_text=(BASE/'COMPLETE_TEN_PAGE_WORKSHOP_FOURTH_EDITION.md').read_text(encoding='utf-8');prose_text=base_text.split('## Teil II',1)[0].rstrip();edition=prose_text+'\n\n---\n\n## Teil II — Drei Himmelsseiten, fünfte Lesung\n\n'
for page in ('f67r2','f68r1','f69v'):
 edition+=f'### {page}\n\n'
 for r in unit_out:
  if r['register']=='ASTRO' and r['page']==page:edition+=f"- `{r['unit_id']}` — {r['speakable_reading_de']}\n"
 edition+='\n'
(HERE/'COMPLETE_TEN_PAGE_WORKSHOP_FIFTH_EDITION.md').write_text(edition,encoding='utf-8')
pocket=(BASE/'FOURTH_POCKET_CODEBOOK.md').read_text(encoding='utf-8')+"\n## Markierungsstatus\n\n- `OD` — **MARKIERT / EINGETRAGEN**; nach Grundkörper und Grad, vor Y oder Argument.\n- `ODY` — **DIESEN POSTEN EINTRAGEN** im Astroregister; eine registrierte Prosa-Ganzkarte darf anders lauten.\n"
(HERE/'FIFTH_POCKET_CODEBOOK.md').write_text(pocket,encoding='utf-8')

type_counts=Counter(r['composition_autonomy'] for r in class_out)
result={'status':'PASS','counts':{'surfaces':len(surface_out),'groups':len(ledger_out),'units':len(unit_out),'od_surfaces':len(od_types),'od_groups':len(od_groups),'changed_units':changed,'full_groups':counts['FULL'],'partial_groups':counts['PARTIAL'],'whole_groups':counts['NONE'],'full_surface_types':sum(v for k,v in type_counts.items() if k.startswith('FULL')),'partial_surface_types':type_counts['PARTIAL'],'whole_surface_types':type_counts['NONE'],'register_split_surface_types':type_counts['REGISTER_SPLIT']}}
(HERE/'BUILD_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
