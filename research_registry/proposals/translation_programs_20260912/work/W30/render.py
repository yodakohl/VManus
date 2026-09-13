import csv,json
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr):
 with (E/n).open('w') as f:
  out=csv.DictWriter(f,fieldnames=[k for k in rr[0] if k!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');out.writeheader();out.writerows(dict(r,row_status='recorded') for r in rr)
s=[r for r in rows(E/'SCOPES.tsv') if r['shol']=='A' and r['contract']=='TRANSFER'];cs=[r for r in rows(E/'CANDIDATES.tsv') if (r['shol'],r['grammar'],r['model'],r['timing'])==('A','J','H','I')];a=rows(B/'A_ALIGNMENT.tsv');byid={r['locus']+':'+r['index']:r for r in a};paras={r['paragraph'] for r in s};full=[]
for r in a:
 if r['paragraph'] not in paras:continue
 loc=r['locus']+':'+r['index'];scope=next((x for x in s if x['chey']==loc),None);target=next((x for x in s if x['target']==loc),None)
 full.append(dict(r,N_H='nicht [Bereich bis '+scope['target']+']' if scope else ('NICHT: '+r['H'] if target else r['H']),N_D='nicht [Bereich bis '+scope['target']+']' if scope else ('NICHT: '+r['D'] if target else r['D'])))
table('CONTEXT_ALIGNMENT.tsv',full)
text=['# W30: acht konkrete Prüfen-/Negationsalternativen','Vollständige betroffene Arbeitsabsätze, unveränderte W28-Gruppen. A/H dient der Anzeige; D steht im Alignment, Q und alle B/J/M/O/I im Kandidatenvergleich. Dies ist eine Bereichslesung, keine durchgerechnete negative Zustandsfolge.','## Alle acht Stellen','| chey | C: Prüfen | N: feste Gegenlesung | Offener Bereich |','|---|---|---|---|']
for r,t in zip(cs,s):
 assert r['chey']==t['chey'];p=r['C_patient'];text.append('| '+r['chey']+' | Prüfe '+(byid[p]['H']+' ['+p+']' if p else '[ungebunden]')+' | '+r['N_wording']+'; Objekt '+r['N_patient_gloss']+' ['+r['N_patient']+']; Ziel '+r['N_target']+' | '+(t['open_interval'] or 'kein offenes Zwischenwort')+' |')
text+=['','Auf f86v5 hängt die geerbte Objektbindung der Qualität oty selbst am bisherigen chey-Prüfereignis (ASSUMED_RESULT_OR_PROCESS_CONDITION:f86v5.19:3). Das Festhalten dieses Objekts isoliert die Polarität, rechtfertigt den Bezug unter entferntem Prüfbefehl aber nicht neu. Für eine vollständige negative Lesung bleiben daher sowohl dieser Bindungsvertrag als auch die Behandlung negativer Zustandsaussagen zu klären. „Nicht kühl“ wird nicht still zu „warm“ übersetzt.','Auf f93r negiert diese Regel qokor .12:1; ychos .10:1 liegt vor chey und bleibt positiv. Zehn Gruppen liegen zwischen Negation und Ziel, darunter drei ungelesene. Unter C würde die Flüssigkeit geprüft und sal erhitzt, unter N entfiele die Prüfung und das Erhitzen von sal wäre verboten. Eine beobachtete Entscheidung darüber liefert dieser Bereichstest nicht.','Auf f29v wird nur das erste chol .3:1 negiert. Das zweite chol .3:2 bleibt positiv. Daraus folgt ohne zusätzliche Bereichs- oder Zeitannahme weder automatisch ein Widerspruch noch eine verständliche praktische Absicht.','## Vollständige Kontextlesung']
for p in dict.fromkeys(r['paragraph'] for r in full):
 text+=['','### '+p]
 for loc in dict.fromkeys(r['locus'] for r in full if r['paragraph']==p):
  rr=[r for r in full if r['locus']==loc];text+=['',loc+' · `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['N_H'] for r in rr)]
(E/'READINGS.md').write_text('\n'.join(text)+'\n');print(json.dumps(dict(paragraphs=len(paras),groups=len(full),chey=len(s))))
