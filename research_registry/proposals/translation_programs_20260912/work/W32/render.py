import csv
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
a=rows(B/'A_ALIGNMENT.tsv');byid={r['locus']+':'+r['index']:r for r in a};rr=[r for r in rows(E/'CANDIDATES.tsv') if (r['shol'],r['grammar'],r['model'],r['timing'])==('A','J','H','I')]
def word(loc):return (byid[loc]['H']+' ['+loc+']') if loc else '[fehlt]'
def wording(r):
 return (word(r['governor'])+'; Patient '+word(r['patient'])+'; mit '+word(r['companion'])+'; '+(r['attachment_issues'] or 'zwei verschiedene gebundene Objekte'))
text=['# W32: mit-Material und vorheriger/folgender Arbeitsgang','Alle Werte hypothetisch aus W28. P/F ergänzen nur einen angenommenen Begleitbezug; weder Mischung noch Behandlung der Begleitung, neue Portion, Dosierung oder Zustandswirkung wird daraus automatisch abgeleitet. Die ursprünglichen Ereignisse bleiben unverändert.','## Konkreter Ausbau auf f93r','F: „Zerkleinere die Dosis Q des Trockenmaterials mit Pulver.“ Das Pulver sheeody .8:2 begleitet hypothetisch ychos .10:1; dessen Patient bleibt chodaiin .8:3. Das ist eine vorangestellte mit-Phrase über offene Wörter hinweg. Die Dosis gehört weiterhin zum Trockenmaterial, nicht automatisch zum Pulver.','P unter A: „Befeuchte die Samen mit Pulver.“ Hier begleitet sheeody das vorherige shol .7:2 an shor .7:1. Unter Q ist shol keine Aktion und P greift auf das frühere chol .6:6 am kühlen Anteil zurück. Keine dieser Fassungen ist ausgewählt.','Die spätere chodaiin-Nennung .28:3 wiederholt die angesetzte Stoffkonstitution des Trockenmaterials. Das prüft keine Wirkung des Pulvers und bestätigt den Begleitbezug nicht. Eine spätere direkte Verarbeitungs-/Qualitätsanforderung an sheeody fehlt.','## Alle 17 Marker, Anzeige A/H/J/I','| Marker | P: vorheriger Arbeitsgang | F: folgender Arbeitsgang |','|---|---|---|']
for loc in dict.fromkeys(r['marker'] for r in rr):
 p=next(r for r in rr if r['marker']==loc and r['direction']=='P');f=next(r for r in rr if r['marker']==loc and r['direction']=='F');text.append('| '+loc+' | '+wording(p)+' | '+wording(f)+' |')
text+=['','B/M,Q,D,O sind vollständig in CANDIDATES.tsv erhalten. Ein diagnostisch genannter Arbeitsgang bei fehlendem Material macht den Bezug nicht vollständig. SAME_OBJECT_ACCOMPANIMENT bezeichnet einen Bezug auf denselben bestehenden Bestand, keine neu entdeckte Portion.','## Ganze ursprüngliche Wortfolge mit Markerhinweisen','1045 Gruppen in 17 Absätzen. Die P/F-Tabelle ergänzt die folgenden unveränderten Wortannahmen; sie repariert keine offenen Wörter.']
marks={r['marker'] for r in rr}
for p in dict.fromkeys(r['paragraph'] for r in a):
 text+=['','### '+p]
 for loc in dict.fromkeys(r['locus'] for r in a if r['paragraph']==p):
  line=[r for r in a if r['locus']==loc];text+=['',loc+' · `'+' '.join(r['raw'] for r in line)+'`','',' · '.join(r['H']+(' [P/F-Bezug oben offen verglichen]' if r['locus']+':'+r['index'] in marks else '') for r in line)]
(E/'READINGS.md').write_text('\n'.join(text)+'\n')
