#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent
B924=H.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'
B931=H.parent/'sidequest_semantic_bilevel_component_dictionary_nine_hundred_thirty_first'
B935=H.parent/'sidequest_semantic_atomic_pocket_lexicon_nine_hundred_thirty_fifth'

def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,fields,rows):
 with (H/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

SIGNS={
'LOCAL_CHAR_F':('NEBENPFAD','über einen Nebenpfad','Nebenreihe oder Seitenzweig','O+F+AR/AL and Y+F+AIN place F between active item/run and source, target or unit'),
'G_LABEL':('PRUEFMARKE','Prüfmarke setzen','Prüfmarke am Eintrag','standalone or final g marks a checked entry'),
'LOCAL_CHAR_G':('EINMAL','einmal ausführen','Einzelmarke','final g follows an operation; initial g precedes one stage'),
'LOCAL_CHAR_I':('UNTERINDEX','auf der Unterstufe','Unterindex','i repeatedly sits immediately before IIN or a marked substate'),
'D_LABEL':('RAND','am Rand abschließen','Randmarke','terminal d follows a close or target place'),
'S_LABEL':('RAHMEN','im markierten Rahmen','Rahmengrenze','s brackets the f70v2 AL-OL address'),
'LOCAL_CHAR_B':('PAAR','paarweise entnehmen','Paarmarke','same CH+EE+B card recurs in Biological and Pharma'),
'M_LOCAL':('MITTE','im Mittelgang ausführen','Mittelplatz','m follows a work run once and an indexed second stage once'),
'Z_ADDR':('AUSSEN','am Außenplatz','Außenplatz','z is a dedicated Aries address before source or added unit'),
'LOCAL_CHAR_J':('VERBUND','im verbundenen Gang','Verbundstelle','single f88 form joins local and inner address around an extract'),
'LOCAL_CHAR_Z':('ZWISCHEN','zwischen zwei Stellen','Zwischenadresse','z occurs exactly between two local addresses'),
}
base=read(B935/'PASS935_56_ATOMIC_POCKET_LEXICON.tsv');revised=[]
for r in base:
 q=dict(r)
 if r['component'] in SIGNS:
  atomic,prose,image,_=SIGNS[r['component']];q['atomic_pocket_value_de']=atomic;q['workshop_expansion_de']=prose;q['image_expansion_de']=image;q['teaching_rule_de']=f'Merke {atomic}; der Ort erweitert zu „{prose}“ oder „{image}“.'
 revised.append(q)
write('PASS938_56_REVISED_ATOMIC_LEXICON.tsv',list(revised[0]),revised)

signrows=[]
for c,(a,p,i,reason) in SIGNS.items():
 signrows.append({'component':c,'atomic_value_de':a,'workshop_value_de':p,'image_value_de':i,'creative_context_reason':reason})
write('PASS938_11_LOCAL_SIGN_VALUES.tsv',list(signrows[0]),signrows)

bi={r['component']:r for r in read(B931/'PASS931_56_BILEVEL_COMPONENT_DICTIONARY.tsv')}
for c,(a,p,i,_) in SIGNS.items():bi[c]['abstract_core_de']=a;bi[c]['workshop_prose_de']=p;bi[c]['owner_address_de']=i
events=read(B924/'PASS924_2511_CURRENT_EVENT_LEDGER.tsv');eventrows=[];atomrows=[];atom_id=0
for e in events:
 cs=e['component_recipe'].split('+');used=[c for c in cs if c in SIGNS]
 if not used:continue
 channel=e['current_channel'];reading='; '.join((bi[c]['workshop_prose_de'] if channel=='WORKSHOP_PROSE' else bi[c]['owner_address_de']) for c in cs)
 eventrows.append({'event_id':e['event_id'],'physical_page':e['physical_page'],'locus':e['locus'],'register':e['register'],'channel':channel,'surface':e['surface'],'component_recipe':e['component_recipe'],'revised_signs':'|'.join(used),'visible_owner_de':e['visible_owner_de'],'revised_compositional_reading_de':reading})
 for pos,c in enumerate(cs,1):
  if c not in SIGNS:continue
  atom_id+=1;atomic,prose,image,_=SIGNS[c]
  atomrows.append({'sign_atom_id':f'P938-A{atom_id:02d}','event_id':e['event_id'],'physical_page':e['physical_page'],'locus':e['locus'],'surface':e['surface'],'component_position':pos,'component':c,'atomic_value_de':atomic,'register_value_de':prose if channel=='WORKSHOP_PROSE' else image})
write('PASS938_43_SIGN_EVENT_READINGS.tsv',list(eventrows[0]),eventrows)
write('PASS938_44_SIGN_ATOM_READINGS.tsv',list(atomrows[0]),atomrows)

doc=['# Pass 938 — Bedeutungen der letzten lokalen Zeichen','',
     'Die Werte sind kurze kreative Werkstattmerker. Sie ersetzen bloße Buchstabennamen; sie machen aus den Zeichen keine Lautbuchstaben.','']
for r in signrows:doc += [f"## {r['component']} = {r['atomic_value_de']}",'',f"Werkstatt: **{r['workshop_value_de']}**. Bild: **{r['image_value_de']}**. Grund: {r['creative_context_reason']}.",'']
(H/'PASS938_LOCAL_SIGN_DICTIONARY.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')
report="""# Pass 938 — keine bloßen F/G/I-Zeichen mehr

## Ergebnis

Elf bisher nur benannte lokale Zeichen erhalten kurze Arbeitswerte in 44
Atomen innerhalb von 43 Kartenereignissen: F=NEBENPFAD,
G-Prüfzeichen=PRUEFMARKE, lokales g=EINMAL,
i=UNTERINDEX, d=RAND, s=RAHMEN, b=PAAR, m=MITTE, Z-Adresse=AUSSEN,
j=VERBUND und lokales z=ZWISCHEN.

Diese Werte sind bewusst klein. `ofal` wird nicht zu einem Satzwort, sondern
zu `GANG + NEBENPFAD + ZIEL`: einen Arbeitsgang über den Nebenpfad zum Ziel
führen. `otaza` wird `NAECHST + ADRESSE + ZWISCHEN + ADRESSE`: nächster Platz
zwischen zwei lokalen Adressen.

## Kreative Wirkung

Das 56-Wert-Lexikon enthält jetzt auch für die seltensten Zeichen eine
sprechbare Werkstattfunktion. Nur Besitzer- und Sachnomen bleiben bildlokal;
keine sichtbare Kartenfolge muss mit „F-Zeichen“ oder „unbekannt“ enden.
"""
(H/'PASS938_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS938_56_REVISED_ATOMIC_LEXICON.tsv','PASS938_11_LOCAL_SIGN_VALUES.tsv','PASS938_43_SIGN_EVENT_READINGS.tsv','PASS938_44_SIGN_ATOM_READINGS.tsv','PASS938_LOCAL_SIGN_DICTIONARY.md','PASS938_REPORT.md']
(H/'PASS938_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','signs':len(signrows),'events':len(eventrows),'sign_atoms':len(atomrows),'outputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
