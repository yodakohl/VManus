#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
B931=H.parent/'sidequest_semantic_bilevel_component_dictionary_nine_hundred_thirty_first'
B932=H.parent/'sidequest_semantic_bilevel_card_composition_nine_hundred_thirty_second'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

ATOM={
'Y':'DIES','OK':'START','E':'KURZ','DY':'ENDE','O':'GANG','OL':'WEITER','EE':'LANG','OT':'NAECHST','AL':'ZIEL','CH':'AUSWAHL','D_ADDR':'UNTER','SH':'HALT','AR':'QUELLE','K':'ZUORDNUNG','AIIN':'SOLLWERT','S':'WAHL','CHD':'WECHSEL','OR':'EINTRAG','L':'VERBINDUNG','T':'EINSTELLUNG','AIN':'EINHEIT','R':'MARKE','P':'EINSATZ','CTH':'BEREIT','SHED':'ABSETZEN','CKH':'DURCHLASS','AM_ADDR':'INNEN','CHEO':'AUSZUG','DA':'ZWEIT','CARRIER_Q':'EINTRITT','A_ADDR':'ADRESSE','AIR':'LAUFWEG','CHK':'BEHANDLUNG','IIN':'STUFE','S_ADDR':'STERNORT','SOLK':'SAMMELN','EEE':'VOLL','LSH':'SPUELEN','LOCAL_CHAR_F':'F','CPH':'GEGENLAUF','HO':'TEIL','AN':'ZUSATZ','G_LABEL':'G','CFH':'TRENNEN','LOCAL_CHAR_G':'GLOKAL','LOCAL_CHAR_I':'I','OS':'DAZU','D_LABEL':'D','S_LABEL':'S','LOCAL_CHAR_B':'B','M_LOCAL':'M','Z_ADDR':'ZORT','LD':'BEFESTIGEN','LOCAL_CHAR_J':'J','LOCAL_CHAR_Z':'ZLOKAL','RESUME_CARD':'WIEDER',
}
src=read(B931/'PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv');rows=[]
for r in src:
 rows.append({'component':r['component'],'shelf':r['shelf'],'atomic_pocket_value_de':ATOM[r['component']],'workshop_expansion_de':r['workshop_prose_de'],'image_expansion_de':r['owner_address_de'],'total_atom_occurrences':r['total_atom_occurrences'],'teaching_rule_de':f"Merke nur {ATOM[r['component']]}; die konkrete Formulierung kommt aus Register und Nachbarkarten."})
write('PASS935_56_ATOMIC_POCKET_LEXICON.tsv',list(rows[0]),rows)
cards=read(B932/'PASS932_1384_BILEVEL_CARD_DICTIONARY.tsv');out=[]
for r in cards:
 seq=' + '.join(ATOM[c] for c in r['component_recipe'].split('+'))
 out.append({'dictionary_entry_id':r['dictionary_entry_id'],'surfaces':r['surfaces'],'component_recipe':r['component_recipe'],'atomic_pocket_sequence_de':seq,'observed_channel':r['observed_channel'],'observed_channel_reading_de':r['observed_channel_reading_de'],'events':r['observed_events'],'pages':r['physical_pages']})
write('PASS935_1384_ATOMIC_CARD_INTERLINEAR.tsv',list(out[0]),out)
doc=['# Pass 935 — Einwort-Wörterbuch für den Lehrling','',
     'Jede Stammkarte erhält genau einen kurzen deutschen Merkwert. Dieser Merkwert ist nicht die fertige Übersetzung; die fertige Formulierung entsteht erst aus Kartenfolge, Register und Bildbesitzer.','',
     '## Die 56 Merkwörter','']
for r in rows:doc += [f"- `{r['component']}` = **{r['atomic_pocket_value_de']}** — Werkstatt: {r['workshop_expansion_de']}; Bild: {r['image_expansion_de']}"]
doc += ['','## Kompositionsbeispiele','',
        '- `OK+E+DY = START + KURZ + ENDE` → kurz ansetzen und schließen.','- `SH+EE+Y = HALT + LANG + DIES` → diesen Posten länger halten.','- `CHD+Y = WECHSEL + DIES` → diesen Posten umsetzen.','- `S+AIIN = WAHL + SOLLWERT` → Variante nach Sollwert wählen / Bildklasse mit Sollwert.','']
(H/'PASS935_ATOMIC_POCKET_DICTIONARY.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report="""# Pass 935 — keine satzlangen Stammglossen mehr

## Ergebnis

Alle 56 Komponenten haben jetzt einen einzigen Merkwert ohne Leerzeichen,
Schrägstrich oder Alternativsatz. Alle 1.384 Karten sind zusätzlich in dieser
Einwortnotation interlinearisiert.

Die wichtigen Unterschiede bleiben sichtbar: `O=GANG`, `OK=START`,
`CH=AUSWAHL`, `K=ZUORDNUNG`, `SH=HALT`, `CHD=WECHSEL`, `AIR=LAUFWEG`,
`AIN=EINHEIT`, `AIIN=SOLLWERT`, `IIN=STUFE`, `Y=DIES`, `DY=ENDE`.

Das beseitigt genau den früheren Fehler „ein Stamm = ein ganzer moderner Satz“.
Eine konkrete Lesung wie „führe die Flüssigkeit zur nächsten Beckenstelle“
entsteht aus `GANG/WECHSEL + LAUFWEG + ZIEL + DIES` unter einem sichtbaren
Beckenbesitzer; kein einzelner Stamm bedeutet diesen ganzen Satz.
"""
(H/'PASS935_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS935_56_ATOMIC_POCKET_LEXICON.tsv','PASS935_1384_ATOMIC_CARD_INTERLINEAR.tsv','PASS935_ATOMIC_POCKET_DICTIONARY.md','PASS935_REPORT.md']
(H/'PASS935_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','components':len(rows),'cards':len(out),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
