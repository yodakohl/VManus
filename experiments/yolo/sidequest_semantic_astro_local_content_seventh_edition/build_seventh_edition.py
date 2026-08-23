#!/usr/bin/env python3
from pathlib import Path
import csv,json
from collections import defaultdict,Counter

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'experiments/yolo/sidequest_semantic_renderer_completed_sixth_edition'
ASTRO=ROOT/'experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv'

def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(path,fields,rows):
 with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

PARSE={
'am':('AM','ASPEKT'), 'amy':('AM+Y','aktueller Aspekt'), 'aram':('AR+AM','Quellaspekt'), 'daram':('AR+AM','Quellaspekt'), 'oaram':('AR+AM','Quellaspekt'), 'ydam':('AM+Y','aktueller festgehaltener Aspekt'),
'g':('G','GRAD'), 'giin':('G+IIN','Gradstufe'), 'og':('G','Grundgrad'), 'qsg':('G','Nebengrad'),
'os':('OS','FELD/RAHMEN'), 'osar':('OS+AR','Feldquelle'), 'osdaiin':('OS+AIIN','Feld-Sollwert'), 'sosho':('OS+HO','Feldeingang'), 'oeeos':('EE+OS','langes oder zweites Feld'), 'okeeos':('OK+EE+OS','zweites Feld aktivieren'), 'sykos':('YK+OS','Klassenfeld'),
}
astro_groups=read(ASTRO);source_by_surface=defaultdict(list)
for r in astro_groups:source_by_surface[r['visible_surface']].append(r)

root_rows=[
{'local_root':'AM','short_value_de':'ASPEKT','surface_types':6,'astro_groups':8,'composition_rule':'AM + Y current; AR + AM source aspect','examples':'am|amy|aram|daram|oaram|ydam','boundary':'Astro-local table root'},
{'local_root':'G','short_value_de':'GRAD','surface_types':4,'astro_groups':4,'composition_rule':'G + IIN degree stage; renderer + G base or side degree','examples':'g|giin|og|qsg','boundary':'Astro-local table root'},
{'local_root':'OS','short_value_de':'FELD/RAHMEN','surface_types':7,'astro_groups':8,'composition_rule':'OS + source/value/input/grade/class relation','examples':'os|osar|osdaiin|sosho|oeeos|okeeos|sykos','boundary':'Astro-local root; prose OS remains learned vessel card'},
]
write(HERE/'THREE_LOCAL_ROOTS.tsv',list(root_rows[0]),root_rows)

type_rows=[];group_rows=[]
for surface,(atoms,reading) in PARSE.items():
 srcs=source_by_surface[surface]
 type_rows.append({'visible_surface':surface,'occurrences':len(srcs),'pages':'|'.join(sorted({r['page'] for r in srcs})),'owners':'|'.join(sorted({r['visible_owner'] for r in srcs})),'revised_atom_sequence':atoms,'revised_short_reading_de':reading,'decision':'PROMOTE_ASTRO_LOCAL_CONTENT_ROOT'})
 for src in srcs:group_rows.append({'group_serial':src['group_serial'],'opaque_local_id':src['opaque_local_id'],'page':src['page'],'locus':src['locus'],'visible_owner':src['visible_owner'],'visible_surface':surface,'revised_atom_sequence':atoms,'revised_short_reading_de':reading})
write(HERE/'LOCAL_ROOT_17_TYPE_PARADIGM.tsv',list(type_rows[0]),type_rows);write(HERE/'LOCAL_ROOT_20_GROUP_READINGS.tsv',list(group_rows[0]),group_rows)

surfaces=read(BASE/'SIXTH_487_SURFACE_DICTIONARY.tsv');ledger=read(BASE/'SIXTH_776_SPEAKABLE_LEDGER.tsv');units=read(BASE/'SIXTH_258_READING_UNITS.tsv');classes=read(BASE/'SIXTH_RECLASSIFIED_487_SURFACES.tsv');base_aut={r['unified_serial']:r['autonomy'] for r in read(BASE/'SIXTH_776_GROUP_AUTONOMY.tsv')}
surface_out=[]
for row in surfaces:
 out=dict(row);target=PARSE.get(row['visible_surface'])
 if target:
  atoms,value=target
  if row['visible_surface']=='os':
   out['common_atom_sequences']='PROSE:OS_WHOLE|ASTRO:OS';out['common_nucleus_de']='PROSE:MISCHGEFÄSS || ASTRO:FELD/RAHMEN';out['reading_rule_de']='register split: Prosa-Ganzkarte bewahren; Astro OS als Feld/Rahmen lesen'
  else:
   out['common_atom_sequences']=atoms;out['common_nucleus_de']=value;out['reading_rule_de']='lies lokalen Tabellenkörper und füge bekannte Quelle/Wert/Grad/Auswahl an'
  out['astro_short_values_de']=value
 surface_out.append(out)
write(HERE/'SEVENTH_487_SURFACE_DICTIONARY.tsv',list(surface_out[0]),surface_out)

group_target={r['opaque_local_id']:r for r in group_rows};ledger_out=[]
for row in ledger:
 out=dict(row);target=group_target.get(row['source_group_id'])
 if target:
  out['atom_sequence']=target['revised_atom_sequence'];out['short_value_de']=target['revised_short_reading_de'];out['lookup_mode']='ASTRO_LOCAL_AM_G_OS_ROOT'
 ledger_out.append(out)
by_unit=defaultdict(list)
for r in ledger_out:by_unit[(r['register'],r['page'],r['reading_unit_id'])].append(r)
unit_out=[];changed=0
for row in units:
 out=dict(row)
 if row['register']=='ASTRO':
  gs=by_unit[(row['register'],row['page'],row['unit_id'])]
  if any(g['lookup_mode']=='ASTRO_LOCAL_AM_G_OS_ROOT' for g in gs):
   out['speakable_reading_de']=row['speakable_reading_de'].split(':',1)[0]+': '+'; '.join(g['short_value_de'] for g in gs);changed+=1
 unit_out.append(out)
lu={(r['register'],r['page'],r['unit_id']):r['speakable_reading_de'] for r in unit_out}
for r in ledger_out:r['unit_reading_de']=lu[(r['register'],r['page'],r['reading_unit_id'])]
write(HERE/'SEVENTH_776_SPEAKABLE_LEDGER.tsv',list(ledger_out[0]),ledger_out);write(HERE/'SEVENTH_258_READING_UNITS.tsv',list(unit_out[0]),unit_out)

class_out=[]
for row in classes:
 out=dict(row);target=PARSE.get(row['visible_surface'])
 if target:
  atoms,value=target
  if row['visible_surface']=='os':
   out['classification']='REGISTER_SPLIT_ASTRO_OS_FIELD_PROSE_VESSEL';out['historical_layer']='ASTRO_TABLE_ROOT_VS_PROSE_NOMENCLATOR';out['composition_autonomy']='REGISTER_SPLIT';out['apprentice_action_de']='Astro OS=Feld lesen; Prosa-Ganzkarte Mischgefäß bewahren';out['memorized_body_or_residue']='PROSE:OS_WHOLE'
  else:
   out['classification']='ASTRO_LOCAL_PRODUCTIVE_CONTENT_ROOT';out['historical_layer']='LOCAL_TABLE_ROOT_PLUS_BREVIGRAPH';out['composition_autonomy']='FULL_WITH_OWNER';out['apprentice_action_de']='lokalen AM/G/OS-Körper lesen und bekannte Kerne anfügen';out['memorized_body_or_residue']='NONE'
  out['common_atom_sequences']=atoms;out['classification_evidence']='ASTRO_LOCAL:AM_G_OS';out['short_spoken_value_de']=value
 class_out.append(out)
write(HERE/'SEVENTH_RECLASSIFIED_487_SURFACES.tsv',list(class_out[0]),class_out)

aut=[]
for row in ledger_out:
 if row['lookup_mode']=='ASTRO_LOCAL_AM_G_OS_ROOT':a='FULL'
 else:a=base_aut[row['unified_serial']]
 aut.append({'unified_serial':row['unified_serial'],'register':row['register'],'page':row['page'],'source_group_id':row['source_group_id'],'visible_surface':row['visible_surface'],'autonomy':a})
write(HERE/'SEVENTH_776_GROUP_AUTONOMY.tsv',list(aut[0]),aut);ac=Counter(r['autonomy'] for r in aut);write(HERE/'SEVENTH_AUTONOMY_SUMMARY.tsv',['autonomy','visible_groups'],[{'autonomy':k,'visible_groups':ac[k]} for k in ('FULL','PARTIAL','NONE')])

base_text=(BASE/'COMPLETE_TEN_PAGE_WORKSHOP_SIXTH_EDITION.md').read_text(encoding='utf-8');prose=base_text.split('## Teil II',1)[0].rstrip();edition=prose+'\n\n---\n\n## Teil II — Drei Himmelsseiten, siebte Lesung\n\n'
for page in ('f67r2','f68r1','f69v'):
 edition+=f'### {page}\n\n'
 for r in unit_out:
  if r['register']=='ASTRO' and r['page']==page:edition+=f"- `{r['unit_id']}` — {r['speakable_reading_de']}\n"
 edition+='\n'
(HERE/'COMPLETE_TEN_PAGE_WORKSHOP_SEVENTH_EDITION.md').write_text(edition,encoding='utf-8')
pocket=(BASE/'SIXTH_POCKET_CODEBOOK.md').read_text(encoding='utf-8')+"\n## Drei lokale Tafelwörter\n\n- `AM` — **ASPEKT**; mit Y aktuell, mit AR Quellaspekt.\n- `G` — **GRAD**; mit IIN Gradstufe.\n- `OS` — **FELD/RAHMEN**; mit AR Feldquelle, AIIN Feldwert, HO Feldeingang, YK Klassenfeld.\n"
(HERE/'SEVENTH_POCKET_CODEBOOK.md').write_text(pocket,encoding='utf-8')

tc=Counter(r['composition_autonomy'] for r in class_out);result={'status':'PASS','counts':{'local_roots':3,'root_surface_types':len(type_rows),'root_groups':len(group_rows),'surfaces':len(surface_out),'groups':len(ledger_out),'units':len(unit_out),'changed_units':changed,'full_groups':ac['FULL'],'partial_groups':ac['PARTIAL'],'whole_groups':ac['NONE'],'full_types':sum(v for k,v in tc.items() if k.startswith('FULL')),'partial_types':tc['PARTIAL'],'whole_types':tc['NONE'],'split_types':tc['REGISTER_SPLIT']}}
(HERE/'BUILD_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
