import csv,json
from pathlib import Path
E=Path(__file__).resolve().parent
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
a=rows(E/'A_ALIGNMENT.tsv');scopes=[r for r in rows(E.parent/'W30/SCOPES.tsv') if r['shol']=='A' and r['contract']=='TRANSFER'];cs=[r for r in rows(E/'CANDIDATES.tsv') if (r['shol'],r['grammar'],r['model'],r['timing'])==('A','J','H','I')];byid={r['locus']+':'+r['index']:r for r in a};targets={r['target']:r for r in cs}
text=['# W31: vollständige Negationsalternative mit neu angewandten Objektregeln','Alle1045Gruppen/17Absätze erhalten; W28-Wortannahmen mit chey≈nicht. Keine ausgewählte Übersetzung. A/H/J/I dient der Anzeige; Q,D,B/M,O bleiben in allen Tabellen enthalten. Die Wortfolge enthält die Negation an chey; NEG-Markierungen am Ziel zeigen deren Bereich, keine zweite Negation.','## Ergebnis der Objektprüfung','Auf f86v5.19 ergibt die Regel nicht-kühl, dann kühl. Beide Qualitätsangaben sind nach Entfernung des Prüfvorgangs ungebunden. Hier steht deshalb ausdrücklich [Objekt offen]; Endprodukt wird nicht still übernommen. Unter einem hypothetischen gemeinsamen Objekt und ohne Zustandswechsel wären die Aussagen widersprüchlich. Dieser zusätzliche Bezug wird nicht als gelesene Tatsache eingesetzt.','Auf f93r.10 bindet das weiter positive ychos≈zerkleinere nun cheol≈flüssige Zubereitung .10:4 statt der Trockenmaterialdosis .8:3, weil chey keine Aktionsgrenze mehr bildet. Eine ungelesene Gruppe keol bleibt in der neuen Patientenbindung. Das spätere qokor .12:1 wird verboten; sein Objekt bleibt sal .11:7.','## Alle acht negierten Ziele','| chey → Ziel | Wortannahme | N-Objekt | Tatsächlicher Modellstatus |','|---|---|---|---|']
for r in cs:text.append('| '+r['chey']+' → '+r['target']+' | nicht: '+byid[r['target']]['H']+' | '+(r['N_patient']+' '+byid[r['N_patient']]['H'] if r['N_patient'] else '[Objekt offen]')+' | '+r['N_status']+' |')
text+=['','## Ganze Wortfolge']
for p in dict.fromkeys(r['paragraph'] for r in a):
 text+=['','### '+p]
 for loc in dict.fromkeys(r['locus'] for r in a if r['paragraph']==p):
  rr=[r for r in a if r['locus']==loc];gl=[]
  for r in rr:
   rid=r['locus']+':'+r['index'];v=r['H']
   if rid in targets:v+=' [NEG durch chey; '+('Objekt '+targets[rid]['N_patient'] if targets[rid]['N_patient'] else 'Objekt offen')+']'
   if rid=='f86v5.19:7':v+=' [positiv; Objekt offen]'
   if rid=='f93r.10:1':v+=' [N-Patient cheol f93r.10:4; keol dazwischen offen]'
   gl.append(v)
  text+=['',loc+' · `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(gl)]
(E/'READING.md').write_text('\n'.join(text)+'\n')
