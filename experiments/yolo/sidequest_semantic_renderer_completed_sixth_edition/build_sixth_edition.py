#!/usr/bin/env python3
from pathlib import Path
import csv,json
from collections import defaultdict,Counter

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'experiments/yolo/sidequest_semantic_ten_page_workshop_fifth_edition'
RES=ROOT/'experiments/yolo/sidequest_semantic_astro_residual_morphology/ASTRO_301_RESIDUAL_PARSE.tsv'

def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(path,fields,rows):
 with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

VALUE={'AIIN':'Sollwert','AIN':'Portion','AIR':'Lauf/Bahn','AL':'Ziel','AR':'Quelle','CHEO':'Ausgabe/Auszug','HO':'Eingangsposten','OL':'Fortsetzen','OT':'Folge','OR':'Satz/Ansatz','CHD':'Umsetzen','OK':'Aktivieren'}
def speak(seq):
 special={'AL+AIIN':'Ziel-Sollwert','AR+AL':'von Quelle zum Ziel','OT+AR':'nächste Quelle','OT+AIR':'nächster Lauf','CHD+AR':'von Quelle umsetzen','OT+AL+AL':'nächsten Doppelziel-Eintrag setzen'}
 return special.get(seq,' + '.join(VALUE.get(a,a) for a in seq.split('+')))

residual=read(RES)
allographs=[r for r in residual if r['residual_family']=='RENDERER_FRAME' and r['detected_literal_atoms']!='NONE']
bare=[r for r in residual if r['residual_family']=='RENDERER_FRAME' and r['detected_literal_atoms']=='NONE']
allograph_by_surface={r['visible_surface']:r for r in allographs}

allograph_rows=[]
for r in allographs:
 allograph_rows.append({'visible_surface':r['visible_surface'],'occurrences':r['occurrences'],'pages':r['pages'],'owners':r['owners'],'renderer_frame':r['residual_string'],'productive_atom_sequence':r['detected_literal_atoms'],'short_reading_de':speak(r['detected_literal_atoms']),'rule':'strip registered renderer frame, then read productive core','register_split':'YES_PROSE_WHOLE_DAIN' if r['visible_surface']=='dain' else 'NO'})
write(HERE/'RENDERER_26_ALLOGRAPHS.tsv',list(allograph_rows[0]),allograph_rows)
bare_rows=[{'visible_surface':r['visible_surface'],'occurrences':r['occurrences'],'pages':r['pages'],'owners':r['owners'],'local_value_de':r['revised_short_reading_de'],'decision':'KEEP_LOCAL_FRAME_CARD_NO_FREE_SEMANTICS'} for r in bare]
write(HERE/'FOUR_BARE_FRAME_CARDS.tsv',list(bare_rows[0]),bare_rows)

surfaces=read(BASE/'FIFTH_487_SURFACE_DICTIONARY.tsv');ledger=read(BASE/'FIFTH_776_SPEAKABLE_LEDGER.tsv');units=read(BASE/'FIFTH_258_READING_UNITS.tsv');classes=read(BASE/'FIFTH_RECLASSIFIED_487_SURFACES.tsv')
base_autonomy={r['unified_serial']:r['autonomy'] for r in read(BASE/'FIFTH_776_GROUP_AUTONOMY.tsv')}
surface_out=[]
for row in surfaces:
 out=dict(row);target=allograph_by_surface.get(row['visible_surface'])
 if target:
  seq=target['detected_literal_atoms'];value=speak(seq)
  if row['visible_surface']=='dain':
   out['common_atom_sequences']='PROSE:DAIN_WHOLE|ASTRO:AIN';out['common_nucleus_de']='PROSE:TUCH || ASTRO:PORTION';out['reading_rule_de']='register split: Prosa-Ganzkarte bewahren; Astro D-Rahmen abziehen und AIN lesen'
  else:
   out['common_atom_sequences']=seq;out['common_nucleus_de']=value;out['reading_rule_de']='registrierten Renderer-Rahmen abziehen; produktive Kerne lesen'
  out['astro_short_values_de']=value
 surface_out.append(out)
write(HERE/'SIXTH_487_SURFACE_DICTIONARY.tsv',list(surface_out[0]),surface_out)

ledger_out=[]
for row in ledger:
 out=dict(row);target=allograph_by_surface.get(row['visible_surface']) if row['register']=='ASTRO' else None
 if target:
  out['atom_sequence']=target['detected_literal_atoms'];out['short_value_de']=speak(target['detected_literal_atoms']);out['lookup_mode']='ASTRO_REGISTERED_RENDERER_ALLOGRAPH'
 ledger_out.append(out)

by_unit=defaultdict(list)
for r in ledger_out:by_unit[(r['register'],r['page'],r['reading_unit_id'])].append(r)
unit_out=[];changed=0
for row in units:
 out=dict(row)
 if row['register']=='ASTRO':
  gs=by_unit[(row['register'],row['page'],row['unit_id'])]
  if any(g['lookup_mode']=='ASTRO_REGISTERED_RENDERER_ALLOGRAPH' for g in gs):
   prefix=row['speakable_reading_de'].split(':',1)[0];out['speakable_reading_de']=prefix+': '+'; '.join(g['short_value_de'] for g in gs);changed+=1
 unit_out.append(out)
lookup={(r['register'],r['page'],r['unit_id']):r['speakable_reading_de'] for r in unit_out}
for r in ledger_out:r['unit_reading_de']=lookup[(r['register'],r['page'],r['reading_unit_id'])]
write(HERE/'SIXTH_776_SPEAKABLE_LEDGER.tsv',list(ledger_out[0]),ledger_out);write(HERE/'SIXTH_258_READING_UNITS.tsv',list(unit_out[0]),unit_out)

class_out=[]
for row in classes:
 out=dict(row);target=allograph_by_surface.get(row['visible_surface'])
 if target:
  if row['visible_surface']=='dain':
   out['classification']='REGISTER_SPLIT_ASTRO_AIN_PROSE_DAIN_WHOLE';out['historical_layer']='ASTRO_RENDERER_VS_PROSE_NOMENCLATOR';out['composition_autonomy']='REGISTER_SPLIT';out['apprentice_action_de']='Astro D-Rahmen abziehen und AIN lesen; Prosa-Ganzkarte lernen';out['memorized_body_or_residue']='PROSE:DAIN_WHOLE'
  else:
   out['classification']='RENDERER_ALLOGRAPH_OF_PRODUCTIVE';out['historical_layer']='RENDERER_PLUS_BREVIGRAPH';out['composition_autonomy']='FULL_AFTER_RENDERER_NORMALIZATION';out['apprentice_action_de']='Renderer abziehen, dann zusammensetzen';out['memorized_body_or_residue']='NONE'
  out['common_atom_sequences']=target['detected_literal_atoms'];out['classification_evidence']='ASTRO:REGISTERED_RENDERER_FRAME';out['short_spoken_value_de']=speak(target['detected_literal_atoms'])
 class_out.append(out)
write(HERE/'SIXTH_RECLASSIFIED_487_SURFACES.tsv',list(class_out[0]),class_out)

class_by={r['visible_surface']:r for r in class_out};aut=[]
for row in ledger_out:
 cls=class_by[row['visible_surface']]
 if row['lookup_mode']=='ASTRO_REGISTERED_RENDERER_ALLOGRAPH':a='FULL'
 else:a=base_autonomy[row['unified_serial']]
 aut.append({'unified_serial':row['unified_serial'],'register':row['register'],'page':row['page'],'source_group_id':row['source_group_id'],'visible_surface':row['visible_surface'],'autonomy':a,'classification':cls['classification']})
write(HERE/'SIXTH_776_GROUP_AUTONOMY.tsv',list(aut[0]),aut)
counts=Counter(r['autonomy'] for r in aut);write(HERE/'SIXTH_AUTONOMY_SUMMARY.tsv',['autonomy','visible_groups'],[{'autonomy':k,'visible_groups':counts[k]} for k in ('FULL','PARTIAL','NONE')])

base_text=(BASE/'COMPLETE_TEN_PAGE_WORKSHOP_FIFTH_EDITION.md').read_text(encoding='utf-8');prose=base_text.split('## Teil II',1)[0].rstrip();edition=prose+'\n\n---\n\n## Teil II — Drei Himmelsseiten, sechste Lesung\n\n'
for page in ('f67r2','f68r1','f69v'):
 edition+=f'### {page}\n\n'
 for r in unit_out:
  if r['register']=='ASTRO' and r['page']==page:edition+=f"- `{r['unit_id']}` — {r['speakable_reading_de']}\n"
 edition+='\n'
(HERE/'COMPLETE_TEN_PAGE_WORKSHOP_SIXTH_EDITION.md').write_text(edition,encoding='utf-8')
pocket=(BASE/'FIFTH_POCKET_CODEBOOK.md').read_text(encoding='utf-8')+"\n## Schreibrahmen\n\n- `D/S/CH/CHE/O/Q/T` tragen in registrierten Allographen keinen Sachwert.\n- Ein nackter Rahmen bleibt eine lokale Tafelkarte; er wird nicht automatisch gelöscht.\n- `dain` ist registergespalten: Astro D+AIN=Portion, Prosa gelernte Tuchkarte.\n"
(HERE/'SIXTH_POCKET_CODEBOOK.md').write_text(pocket,encoding='utf-8')

tc=Counter(r['composition_autonomy'] for r in class_out);result={'status':'PASS','counts':{'allograph_types':len(allographs),'allograph_groups':sum(int(r['occurrences']) for r in allographs),'bare_frame_types':len(bare),'bare_frame_groups':sum(int(r['occurrences']) for r in bare),'surfaces':len(surface_out),'groups':len(ledger_out),'units':len(unit_out),'changed_units':changed,'full_groups':counts['FULL'],'partial_groups':counts['PARTIAL'],'whole_groups':counts['NONE'],'full_types':sum(v for k,v in tc.items() if k.startswith('FULL')),'partial_types':tc['PARTIAL'],'whole_types':tc['NONE'],'split_types':tc['REGISTER_SPLIT']}}
(HERE/'BUILD_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
