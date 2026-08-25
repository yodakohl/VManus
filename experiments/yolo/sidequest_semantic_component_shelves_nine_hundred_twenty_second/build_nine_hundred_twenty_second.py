#!/usr/bin/env python3
"""Build Pass 922: separate productive cores, learned roots, and local signs."""

import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P912=ROOT/'experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth'
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

PRODUCTIVE={
 'Y':('DIESER POSTEN','DY','Endpunkt'), 'OK':('ANSETZEN','SH,CHK','Handlung'),
 'E':('KURZ','EE,EEE','Grad'), 'DY':('SCHLUSS','Y','Endpunkt'),
 'O':('AUSFUEHREN','T','Arbeitsgang'), 'OL':('FORTSETZEN','OT,OS','Reihenfolge'),
 'EE':('LAENGER','E,EEE','Grad'), 'OT':('DANACH/NAECHSTER','OL,OS','Reihenfolge'),
 'AL':('ZIELSTELLE','AR,AIR','Richtung'), 'CH':('ENTNEHMEN','K,P','Transferhandlung'),
 'SH':('HALTEN','OK,CHK','Handlung'), 'AR':('ENTNAHMESTELLE','AL,AIR','Richtung'),
 'K':('ZUGEBEN','CH,P','Transferhandlung'), 'AIIN':('SOLLMASS','AIN,IIN','Menge/Index'),
 'S':('WAEHLEN','CTH,R','Zustandsentscheidung'), 'CHD':('UMSETZEN','CH,K','Transferhandlung'),
 'OR':('ANSATZ','CHEO,HO','Inhalt'), 'L':('LEITEN','CKH,AIR','Weg'),
 'T':('EINSTELLEN','O','Arbeitsgang'), 'AIN':('PORTION','AIIN,IIN','Menge/Index'),
 'R':('KENNZEICHNEN','S,CTH','Zustandsentscheidung'), 'P':('EINSETZEN','CH,K','Transferhandlung'),
 'CTH':('BEREITSTELLEN','S,R','Zustandsentscheidung'), 'CKH':('DURCHLASS','L,AIR','Weg'),
 'CHEO':('AUSZUG/EINTRAG','OR,HO','Inhalt'), 'DA':('ZWEITE STUFE','IIN','Menge/Index'),
 'AIR':('LAUF','AL,AR,L','Richtung/Weg'), 'CHK':('BEHANDELN','OK,SH','Handlung'),
 'IIN':('STUFE','AIN,AIIN,DA','Menge/Index'), 'EEE':('VOLLSTAENDIG','E,EE','Grad'),
}
LEARNED={
 'SHED':('ABSETZEN','häufige Bio-Fachkarte; kein vollständiges Austauschparadigma'),
 'SOLK':('AUFFANGEN','lokale Sammel-/Haltekartenfamilie'),
 'LSH':('SPUELEN','Bio-/Pharma-Durchgangskarte'),
 'CPH':('RUECKFUEHREN','registerübergreifender Gegen-/Empfangsgang'),
 'HO':('STOFFTEIL','gelernter Inhaltsklassifikator'),
 'AN':('ZUSATZ','gelernter Nachgabe-Klassifikator'),
 'CFH':('PRESSEN','seltene Trennoperation'),
 'OS':('DAZU','gelernter additiver Aufruf'),
 'LD':('BEFESTIGEN','einmalige gebundene Fachoperation'),
 'RESUME_CARD':('WIEDERAUFNEHMEN','einmalige Wiederaufnahmekarte'),
}
ADDRESS={
 'D_ADDR':('TEILSTELLE','produktiver Unterplatz ohne Sachwort'),
 'A_ADDR':('LOKALE ADRESSE','allgemeine lokale Stelle'),
 'AM_ADDR':('INNENSTELLE','lokale Gegen-/Innenadresse'),
 'S_ADDR':('STERN-/S-STELLE','registergebundene Adresse'),
 'Z_ADDR':('Z-STELLE','lokale z-spezifische Adresse'),
}
LOCAL={
 'CARRIER_Q':('Q-EINTRITTSTRAEGER','Positionsallograph'), 'D_LABEL':('D-ZEICHEN','lokales Kennzeichen'),
 'G_LABEL':('G-ZEICHEN','lokales Kennzeichen'), 'S_LABEL':('S-ZEICHEN','lokales Kennzeichen'),
 'M_LOCAL':('M-ZEICHEN','lokales Kennzeichen'), 'LOCAL_CHAR_F':('F-ZEICHEN','lokales Kennzeichen'),
 'LOCAL_CHAR_G':('G-LOKALZEICHEN','lokales Kennzeichen'), 'LOCAL_CHAR_I':('I-ZEICHEN','lokales Kennzeichen'),
 'LOCAL_CHAR_B':('B-ZEICHEN','lokales Kennzeichen'), 'LOCAL_CHAR_J':('J-ZEICHEN','lokales Kennzeichen'),
 'LOCAL_CHAR_Z':('Z-LOKALZEICHEN','lokales Kennzeichen'),
}

def main():
 ev=read(P912/'PASS912_2511_EVENT_INTERLINEAR.tsv');stats=defaultdict(lambda:{'events':0,'recipes':set(),'surfaces':set(),'pages':set(),'regs':set(),'pos':Counter()})
 for r in ev:
  atoms=r['component_recipe'].split('+')
  for i,a in enumerate(atoms):
   d=stats[a];d['events']+=1;d['recipes'].add(r['component_recipe']);d['surfaces'].add(r['surface']);d['pages'].add(r['physical_page']);d['regs'].add(r['register']);d['pos']['ONLY' if len(atoms)==1 else 'FIRST' if i==0 else 'LAST' if i==len(atoms)-1 else 'MIDDLE']+=1
 rows=[]
 for a,d in sorted(stats.items(),key=lambda x:(-x[1]['events'],x[0])):
  if a in PRODUCTIVE:meaning,partner,axis=PRODUCTIVE[a];shelf='PRODUCTIVE_CONTRAST_CORE';note='Bedeutung durch Austauschpartner begrenzt'
  elif a in LEARNED:meaning,note=LEARNED[a];partner='NONE';axis='LEARNED_FUNCTION';shelf='LEARNED_WORKSHOP_ROOT'
  elif a in ADDRESS:meaning,note=ADDRESS[a];partner='A_ADDR,AM_ADDR,D_ADDR,S_ADDR,Z_ADDR';axis='ADDRESS';shelf='FORMAL_ADDRESS_SIGN'
  else:meaning,note=LOCAL[a];partner='NONE';axis='RENDERER_OR_LOCAL_MARK';shelf='LOCAL_WRITING_SIGN'
  rows.append({'component':a,'shelf':shelf,'fixed_default_de':meaning,'contrast_axis':axis,'contrast_partners':partner,
               'component_events':str(d['events']),'distinct_recipes':str(len(d['recipes'])),'distinct_surfaces':str(len(d['surfaces'])),
               'physical_pages':str(len(d['pages'])),'registers':str(len(d['regs'])),'positions':','.join(f'{k}:{v}' for k,v in d['pos'].items()),'teaching_note_de':note})
 write('PASS922_56_COMPONENT_SHELVES.tsv',rows,list(rows[0]))
 learned=[r for r in rows if r['shelf']=='LEARNED_WORKSHOP_ROOT'];write('PASS922_10_LEARNED_ROOTS.tsv',learned,list(learned[0]))
 productive=[r for r in rows if r['shelf']=='PRODUCTIVE_CONTRAST_CORE'];write('PASS922_30_PRODUCTIVE_CORES.tsv',productive,list(productive[0]))
 signs=[r for r in rows if r['shelf'] in {'FORMAL_ADDRESS_SIGN','LOCAL_WRITING_SIGN'}];write('PASS922_16_ADDRESS_AND_LOCAL_SIGNS.tsv',signs,list(signs[0]))
 report='''# Pass 922 — drei Schubladen statt eines falschen Wörterbuchs

## Inventar

Die vollständige 14-Seiten-Schrift braucht 56 analysierte Kerne:

- **30 produktive Bedeutungskerne** mit einem sichtbaren Austauschpartner;
- **10 gelernte Werkstattwurzeln** mit kurzer konkreter Defaultbedeutung;
- **5 formale Adresszeichen**;
- **11 lokale Schreib-/Rendererzeichen**.

Die produktiven Kerne sind keine 30 frei memorierten Wörter. Ihre Bedeutung wird
durch Würfel und Paarreihen eingeschränkt: E/EE/EEE, AIN/AIIN/IIN, AL/AR/AIR,
OK/SH/CHK, Y/DY, OL/OT/OS und so weiter.

## Was wirklich gelernt werden muss

Nur zehn inhaltliche Wurzeln bleiben vorerst ohne vollständiges Paradigma:

`SHED absetzen`, `SOLK auffangen`, `LSH spülen`, `CPH rückführen`, `HO Stoffteil`,
`AN Zusatz`, `CFH pressen`, `OS dazu`, `LD befestigen`, `RESUME_CARD wiederaufnehmen`.

Das ist ein plausibler Lehrumfang: zehn Fachwurzeln plus produktive Achsen. Die
Adress- und Lokalzeichen sind keine Wörter und werden beim Kopieren durch Position,
Bild oder Exemplar gewählt.

## Wo Bedeutung noch weich ist

Am weichsten bleiben `HO`, `AN`, `OS`, `LD` und `RESUME_CARD`, weil sie wenige
Ereignisse oder nur einen klaren Kontext besitzen. Die stärkeren gelernten Wurzeln
`SHED`, `SOLK`, `LSH`, `CPH` und `CFH` haben wiederholte Arbeitsabläufe und können
schon als kurze Werkstattverben gelehrt werden.

## Nächster Schritt

Die zehn gelernten Wurzeln werden nun nacheinander in vollständigen Passagen
gelesen. Ziel ist nicht, sie zwanghaft zu zerlegen, sondern ihre kürzeste feste
Bedeutung zu finden und überladene Glossierung zu entfernen.
'''
 (OUT/'PASS922_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS922_56_COMPONENT_SHELVES.tsv','PASS922_10_LEARNED_ROOTS.tsv','PASS922_30_PRODUCTIVE_CORES.tsv','PASS922_16_ADDRESS_AND_LOCAL_SIGNS.tsv','PASS922_REPORT.md']
 counts=Counter(r['shelf'] for r in rows);s={'status':'BUILT','components':len(rows),'shelves':dict(counts),'component_occurrences':sum(int(r['component_events']) for r in rows),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS922_BUILD_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
