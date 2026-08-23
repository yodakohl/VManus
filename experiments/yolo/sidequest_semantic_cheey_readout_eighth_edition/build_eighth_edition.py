#!/usr/bin/env python3
from pathlib import Path
import csv,json
from collections import defaultdict,Counter

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=ROOT/'experiments/yolo/sidequest_semantic_astro_local_content_seventh_edition'

def read(path):
 with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(path,fields,rows):
 with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

PARSE={
'cheey':('CHEEY','sichtbares Ergebnis / Ablesewert'),
'shey':('CHEEY','sichtbares Ergebnis / Ablesewert'),
'lcheey':('L+CHEEY','sichtbares Ergebnis abführen'),
'tshey':('CHEEY','sichtbares Ergebnis einsetzen'),
'qocheey':('CHEEY','Ablesewert'),
'sshey':('CHEEY','Ablesewert'),
'yshey':('Y+CHEEY','aktueller Ablesewert'),
'otshey':('OT+CHEEY','nächster Ablesewert'),
'ychey':('Y+CHEEY','aktueller Ablesewert'),
'cheyky':('CHEEY+YK','Ablesewert der Klasse/des Hauses'),
}

surfaces=read(BASE/'SEVENTH_487_SURFACE_DICTIONARY.tsv');ledger=read(BASE/'SEVENTH_776_SPEAKABLE_LEDGER.tsv');units=read(BASE/'SEVENTH_258_READING_UNITS.tsv');classes=read(BASE/'SEVENTH_RECLASSIFIED_487_SURFACES.tsv');base_aut={r['unified_serial']:r['autonomy'] for r in read(BASE/'SEVENTH_776_GROUP_AUTONOMY.tsv')}

paradigm=[]
for surface,(atoms,reading) in PARSE.items():
 row=next(r for r in surfaces if r['visible_surface']==surface)
 paradigm.append({'visible_surface':surface,'prose_occurrences':row['prose_occurrences'],'astro_occurrences':row['astro_occurrences'],'total_groups':int(row['prose_occurrences'])+int(row['astro_occurrences']),'revised_atom_sequence':atoms,'common_value_de':'SICHTBARES ERGEBNIS/ABLESEWERT','wet_expansion_de':'klarer Auszug oder sichtbarer Ablauf','celestial_expansion_de':reading,'decision':'PROMOTE_CROSS_REGISTER_ROOT'})
write(HERE/'CHEEY_10_SURFACE_PARADIGM.tsv',list(paradigm[0]),paradigm)

surface_out=[]
for row in surfaces:
 out=dict(row);target=PARSE.get(row['visible_surface'])
 if target:
  atoms,reading=target;out['common_atom_sequences']=atoms;out['common_nucleus_de']='SICHTBARES ERGEBNIS/ABLESEWERT';out['reading_rule_de']='lies CHEEY/SHEY als sichtbares Ergebnis; Besitzer erweitert zu Klarauszug oder Tafelablesung'
  if int(row['astro_occurrences']):out['astro_short_values_de']=reading
 surface_out.append(out)
write(HERE/'EIGHTH_487_SURFACE_DICTIONARY.tsv',list(surface_out[0]),surface_out)

ledger_out=[];changed_astro=0
for row in ledger:
 out=dict(row);target=PARSE.get(row['visible_surface'])
 if target:
  atoms,reading=target
  if row['register']=='ASTRO':out['atom_sequence']=atoms;out['short_value_de']=reading;out['lookup_mode']='CROSS_REGISTER_CHEEY_READOUT';changed_astro+=1
  elif row['register']=='PROSE':out['lookup_mode']='CROSS_REGISTER_CHEEY_WET_RESULT'
 ledger_out.append(out)
by_unit=defaultdict(list)
for r in ledger_out:by_unit[(r['register'],r['page'],r['reading_unit_id'])].append(r)
unit_out=[];changed_units=0
for row in units:
 out=dict(row)
 if row['register']=='ASTRO':
  gs=by_unit[(row['register'],row['page'],row['unit_id'])]
  if any(g['lookup_mode']=='CROSS_REGISTER_CHEEY_READOUT' for g in gs):out['speakable_reading_de']=row['speakable_reading_de'].split(':',1)[0]+': '+'; '.join(g['short_value_de'] for g in gs);changed_units+=1
 unit_out.append(out)
lu={(r['register'],r['page'],r['unit_id']):r['speakable_reading_de'] for r in unit_out}
for r in ledger_out:r['unit_reading_de']=lu[(r['register'],r['page'],r['reading_unit_id'])]
write(HERE/'EIGHTH_776_SPEAKABLE_LEDGER.tsv',list(ledger_out[0]),ledger_out);write(HERE/'EIGHTH_258_READING_UNITS.tsv',list(unit_out[0]),unit_out)

class_out=[]
for row in classes:
 out=dict(row);target=PARSE.get(row['visible_surface'])
 if target:
  atoms,_=target;out['common_atom_sequences']=atoms;out['classification']='CROSS_REGISTER_PRODUCTIVE_CHEEY_RESULT';out['historical_layer']='BREVIGRAPH_PLUS_OWNER';out['composition_autonomy']='FULL_WITH_OWNER';out['apprentice_action_de']='CHEEY/SHEY als sichtbares Ergebnis lesen; Besitzer ergänzt nass oder Tafel';out['memorized_body_or_residue']='NONE';out['classification_evidence']='CROSS_REGISTER:WET_RESULT_AND_TABLE_READOUT';out['short_spoken_value_de']='sichtbares Ergebnis / Ablesewert'
 class_out.append(out)
write(HERE/'EIGHTH_RECLASSIFIED_487_SURFACES.tsv',list(class_out[0]),class_out)
aut=[]
for row in ledger_out:
 a='FULL' if row['visible_surface'] in PARSE else base_aut[row['unified_serial']]
 aut.append({'unified_serial':row['unified_serial'],'register':row['register'],'page':row['page'],'source_group_id':row['source_group_id'],'visible_surface':row['visible_surface'],'autonomy':a})
write(HERE/'EIGHTH_776_GROUP_AUTONOMY.tsv',list(aut[0]),aut);ac=Counter(r['autonomy'] for r in aut);write(HERE/'EIGHTH_AUTONOMY_SUMMARY.tsv',['autonomy','visible_groups'],[{'autonomy':k,'visible_groups':ac[k]} for k in ('FULL','PARTIAL','NONE')])

base_text=(BASE/'COMPLETE_TEN_PAGE_WORKSHOP_SEVENTH_EDITION.md').read_text(encoding='utf-8');prose=base_text.split('## Teil II',1)[0].rstrip();edition=prose+'\n\n---\n\n## Teil II — Drei Himmelsseiten, achte Lesung\n\n'
for page in ('f67r2','f68r1','f69v'):
 edition+=f'### {page}\n\n'
 for r in unit_out:
  if r['register']=='ASTRO' and r['page']==page:edition+=f"- `{r['unit_id']}` — {r['speakable_reading_de']}\n"
 edition+='\n'
(HERE/'COMPLETE_TEN_PAGE_WORKSHOP_EIGHTH_EDITION.md').write_text(edition.rstrip()+'\n',encoding='utf-8')
pocket=(BASE/'SEVENTH_POCKET_CODEBOOK.md').read_text(encoding='utf-8')+"\n## Gemeinsames Ergebniszeichen\n\n- `CHEEY/SHEY` — **SICHTBARES ERGEBNIS / ABLESEWERT**.\n- Nasser Besitzer: klarer Auszug oder sichtbarer Ablauf.\n- Tafelbesitzer: abgelesener oder freigegebener Wert.\n"
(HERE/'EIGHTH_POCKET_CODEBOOK.md').write_text(pocket,encoding='utf-8')

tc=Counter(r['composition_autonomy'] for r in class_out);result={'status':'PASS','counts':{'root_surfaces':len(PARSE),'root_groups':sum(r['total_groups'] for r in paradigm),'changed_astro_groups':changed_astro,'changed_astro_units':changed_units,'surfaces':len(surface_out),'groups':len(ledger_out),'units':len(unit_out),'full_groups':ac['FULL'],'partial_groups':ac['PARTIAL'],'whole_groups':ac['NONE'],'full_types':sum(v for k,v in tc.items() if k.startswith('FULL')),'partial_types':tc['PARTIAL'],'whole_types':tc['NONE'],'split_types':tc['REGISTER_SPLIT']}}
(HERE/'BUILD_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
