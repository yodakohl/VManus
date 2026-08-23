#!/usr/bin/env python3
from pathlib import Path
import csv, json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TYPES=ROOT/'experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_301_TYPE_PARSE.tsv'
GROUPS=ROOT/'experiments/yolo/sidequest_semantic_astro_surface_transfer/ASTRO_395_SURFACE_PARSE.tsv'

def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

SEGMENTS={
'chekody':('CHK+OD+Y','erwärmten/gehaltenen Posten markieren'),
'eykeody':('E+YK+E+OD+Y','Klassenposten in kurzer Stufe markieren'),
'odaeiin':('OD+IIN','Arbeits- oder Bedingungsstufe markieren'),
'odaiiin':('OD+IIN','Stufe markieren'),
'odain':('OD+AIN','Portion markieren'),
'odair':('OD+AIR','Lauf oder Bahn markieren'),
'odal':('OD+AL','Ziel markieren'),
'odas':('OD','Nebenwert markieren'),
'odchecthy':('OD+CTH','Bereitbedingung markieren'),
'ody':('OD+Y','diesen Posten eintragen'),
'oeeody':('EE+OD+Y','diesen Posten in langer Stufe eintragen'),
'okeeodal':('OK+EE+OD+AL','markiertes Ziel länger aktivieren'),
'okeeody':('OK+EE+OD+Y','diesen Posten länger aktivieren und eintragen'),
'okeod':('OK+E+OD','kurz aktivieren und markieren'),
'okeodal':('OK+E+OD+AL','markiertes Ziel kurz aktivieren'),
'okeody':('OK+E+OD+Y','diesen Posten kurz aktivieren und eintragen'),
'okodaly':('OK+OD+AL+Y','dieses markierte Ziel aktivieren'),
'okodar':('OK+OD+AR','markierte Quelle aktivieren'),
'okodchy':('OK+OD+Y','diesen markierten Posten aktivieren'),
'okody':('OK+OD+Y','diesen markierten Posten aktivieren'),
'oteody':('OT+E+OD+Y','den nächsten Posten kurz markieren'),
'otody':('OT+OD+Y','den nächsten Posten markieren'),
'qokeeody':('OK+EE+OD+Y','diesen Posten länger aktivieren und eintragen'),
'sheody':('E+OD+Y','diesen gehaltenen Posten kurz markieren'),
'ykeeody':('YK+EE+OD+Y','diesen Klassenposten länger markieren'),
'ykeody':('YK+E+OD+Y','diesen Klassenposten kurz markieren'),
'yteody':('YT+E+OD+Y','diesen Platz kurz markieren'),
'ytody':('YT+OD+Y','diesen Platz eintragen'),
}
types={r['visible_surface']:r for r in read(TYPES)}
rows=[]
for surface,(atoms,reading) in SEGMENTS.items():
    src=types[surface]
    rows.append({'visible_surface':surface,'occurrences':src['occurrences'],'pages':src['pages'],'owners':src['owners'],'revised_atom_sequence':atoms,'od_contribution_de':'MARKIERT/EINGETRAGEN','revised_short_reading_de':reading,'previous_reading_de':src['representative_astro_reading_de'],'decision':'PROMOTE_OD_BOUND_TABLE_MODIFIER'})
write(HERE/'OD_28_TYPE_PARADIGM.tsv',list(rows[0]),rows)

groups=[]
for src in read(GROUPS):
    if src['visible_surface'] not in SEGMENTS:continue
    atoms,reading=SEGMENTS[src['visible_surface']]
    groups.append({'group_serial':src['group_serial'],'opaque_local_id':src['opaque_local_id'],'page':src['page'],'locus':src['locus'],'visible_owner':src['visible_owner'],'visible_surface':src['visible_surface'],'revised_atom_sequence':atoms,'revised_short_reading_de':reading})
write(HERE/'OD_36_GROUP_READINGS.tsv',list(groups[0]),groups)

contrasts=[
('C01','ain','odain','PORTION','MARKIERTE PORTION'),('C02','air','odair','LAUF/BAHN','MARKIERTER LAUF'),('C03','al','odal','ZIEL','MARKIERTES ZIEL'),('C04','iiin','odaiiin','STUFE','MARKIERTE STUFE'),('C05','cthy','odchecthy','BEREIT','MARKIERT BEREIT'),('C06','okar','okodar','QUELLE AKTIVIEREN','MARKIERTE QUELLE AKTIVIEREN'),('C07','okeal','okeodal','ZIEL KURZ AKTIVIEREN','MARKIERTES ZIEL KURZ AKTIVIEREN'),('C08','okeeal','okeeodal','ZIEL LÄNGER AKTIVIEREN','MARKIERTES ZIEL LÄNGER AKTIVIEREN'),('C09','oty','otody','NÄCHSTER POSTEN','NÄCHSTEN POSTEN MARKIEREN'),('C10','ykey','ykeody','KLASSENPOSTEN','KLASSENPOSTEN KURZ MARKIEREN'),('C11','yto','ytody','PLATZ','PLATZ EINTRAGEN')]
contrast_rows=[{'contrast_id':i,'base_surface':b,'od_surface':o,'base_reading_de':br,'od_reading_de':orr,'constant_od_effect_de':'markiert/eingetragen'} for i,b,o,br,orr in contrasts]
write(HERE/'OD_CONTRASTS.tsv',list(contrast_rows[0]),contrast_rows)

pred=[
('P01','OD+AIIN','markierter Sollwert','odaiin or renderer allograph'),('P02','OL+OD+Y','Fortsetzung markieren','olody or renderer allograph'),('P03','YK+OD+AR','markierte Klassenquelle','ykodar or renderer allograph'),('P04','YT+OD+AIIN','markierter Platzwert','ytodaiin or renderer allograph'),('P05','CHD+OD+AL','markiertes Ziel umsetzen','chedodal or renderer allograph'),('P06','OD+OR','markierter Satz/Ansatz','odor or renderer allograph')]
pred_rows=[{'prediction_id':i,'atom_sequence':a,'predicted_short_reading_de':v,'surface_skeleton':s,'status':'EMPTY_CELL'} for i,a,v,s in pred]
write(HERE/'OD_FORWARD_CELLS.tsv',list(pred_rows[0]),pred_rows)

result={'status':'PASS','counts':{'types':len(rows),'groups':len(groups),'owners':len({g['visible_owner'] for g in groups}),'contrasts':len(contrast_rows),'forward_cells':len(pred_rows)}}
(HERE/'BUILD_SUMMARY.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False,indent=2))
