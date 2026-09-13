"""Complete paragraph edition; no new lexical values or inferred missing words."""
import csv,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent;B=E.parent/'W28'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def table(n,rr):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=[k for k in rr[0] if k!='row_status']+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
p='f93r|f93r.1-f93r.32';a=[r for r in rows(B/'A_ALIGNMENT.tsv') if r['paragraph']==p];table('F93R_ALIGNMENT.tsv',a)
args=[r for r in rows(B/'A_ARGUMENTS.tsv') if r['paragraph']==p];table('F93R_ARGUMENTS.tsv',args)
takes=[r for r in rows(B/'A_TAKE_ARGUMENTS.tsv') if r['paragraph']==p];table('F93R_TAKE.tsv',takes)
byid={r['locus']+':'+r['index']:r for r in a}
chain=[]
for r in args:
 if r['grammar']!='J':continue
 chain.append(dict(location=r['operation'],form=r['form'],instruction=r['meaning'],patient=r['patient'],patient_gloss=byid[r['patient']]['H'] if r['patient'] else '[ungebunden]',second=r['coingredient'],second_gloss=byid[r['coingredient']]['H'] if r['coingredient'] else '',rule=r['rule'],debts=r['debts']))
for r in takes:
 if r['grammar']=='J':chain.append(dict(location=r['target'],form='ychor',instruction='nimm',patient=r['patient'],patient_gloss=byid[r['patient']]['H'] if r['patient'] else '[ungebunden]',second='',second_gloss='',rule=r['rule'],debts=r['debts']))
chain.sort(key=lambda r:(int(r['location'].split('.')[1].split(':')[0]),int(r['location'].split(':')[1])));table('F93R_ACTION_CHAIN.tsv',chain)
lines=list(dict.fromkeys(r['locus'] for r in a));reader=['# f93r.1–32: vollständige Arbeitslesung mit zwei Stoffbezügen',
'Alle Wortwerte sind Hypothesen aus W28. A/H ist die angezeigte Fassung: shol≈befeuchte; chol≈erhitze (D≈trockne bleibt offen). Die 32 Transkriptionszeilen bilden den schon gewählten Arbeitsabsatz; Zeilengrenzen beweisen keine Satzgrenzen. Unbekannte Gruppen sind ausdrücklich erhalten. Keine nahezu vollständige Übersetzung.',
'## Zusammenhängender Handlungsentwurf',
'**Zeilen 1–5:** Ein überwiegend ungelesener Einstieg führt Mengen- und Stoffausdrücke ein. In Zeile 2: „Erhitze [unter D: trockne] die feuchte Zubereitung“, mit zwei ungelesenen Gruppen zwischen Befehl und Material. Danach werden getrocknetes und benetztes Material sowie ein erwärmter Grundansatz genannt. Ihre Herkunft aus dem ersten Arbeitsgang ist nicht festgelegt; der frühere W09-chody-Alias wird hier nicht zusätzlich eingesetzt.',
'**Zeilen 6–10:** „Erhitze [D: trockne] den kühlen Anteil. Befeuchte die Samen.“ Danach Pulver und eine Dosis Trockenmaterial. „Zerkleinere [diese Dosis]“, aber nur mit dem angenommenen Rückbezug über vier ungelesene Gruppen. Der folgende Prüfbefehl bezieht sich auf die flüssige Zubereitung, nicht automatisch auf das zerkleinerte Material. Der Name „Endprodukt“ in Zeile 7 allein verbindet keine dieser Portionen.',
'**Zeilen 11–12, Fassung E:** Warme Flüssigkeit, kühle Flüssigkeit und die erneut genannte feuchte Zubereitung stehen neben „davon“ und Arzneimaterial. „Erhitze [das Arzneimaterial]“. sal führt hier einen eigenen Bestand ein. Weder Zusammenmischen der Flüssigkeiten noch der Bezug von „davon“ wird ergänzt.',
'**Zeilen 11–12, Fassung R:** sal bezeichnet hypothetisch denselben Bestand wie sheo in Zeile 11 und 2. Unter H: „Die schon erhitzte Zubereitung [als Arzneimaterial bezeichnet] erhitzen.“ Unter D: „Die zuvor getrocknete Zubereitung [als Arzneimaterial bezeichnet] erhitzen.“ Das zweite Erhitzen ist ein weiterer geschriebener Befehl; ein Wortwert „erneut“ wird nicht erfunden. Es gibt keine gelesene Umbenennungsmarkierung.',
'**Zeilen 13–18:** „Trenne die Dosis feuchten Materials vom Trockenmaterial“; „verbinde … mit …“ bleibt der geerbte lexikalische Rivale. Später „erhitze [den Blütenrest]“, mit einem Rückbezug über vier offene Gruppen. Erneut erscheinen die feuchte Dosis und benetztes Material. Eine Herkunft aus sal wird nicht angesetzt.',
'**Zeilen 19–25:** „Befeuchte das verarbeitete Blütenmaterial.“ Krautpulver wird genannt; dann „befeuchte [das Krautpulver]“ über eine offene Gruppe. Weitere Dosis-, Kraut- und benetzte Materialnennungen bleiben mit ihren offenen Nachbarn stehen. Sie ergeben noch keine gelesene Mischung oder fertige Rezeptur.',
'**Zeilen 26–32:** Ein weiterer Bestandteil; „erhitze die Zubereitung“. Dann „nimm [die abgemessene Zubereitung]“ (festes take-Modell); weitere Dosis- und Krautmehlangaben. „Verarbeite die feuchte Dosis warm“ und „erhitze [D: trockne] das Krautpulver“. Der Schluss nennt eine Portion und zwei ungelesene Wörter. Die warm bearbeitete Dosis und das Krautpulver bleiben getrennte Objekte.',
'## Jeder angesetzte Befehl und sein Objekt',
'Die Tabelle zeigt J; B/J/M binden in diesem Absatz dieselben Patienten. Q ersetzt die drei shol-Befehle durch Qualitätsannahmen. Numerische Dosiswerte sind nicht identifiziert. Unvollständigkeit wird nicht allein durch den technischen Status ARGUMENT_INCOMPLETE erfasst: die aufgeführten offenen Zwischenwörter und impliziten Fortsetzungen bleiben Schulden.',
'| Stelle | Hypothetische Anweisung | Gebundenes Material | Regel / offene Bindung |','|---|---|---|---|']
for r in chain:
 reader.append('| '+r['location']+' | '+r['instruction']+' | '+r['patient']+' '+r['patient_gloss']+(' / '+r['second']+' '+r['second_gloss'] if r['second'] else '')+' | '+r['rule']+('; '+r['debts'] if r['debts'] else '')+' |')
reader+=['## Vollständige Wortfolge',f'{len(a)} Gruppen, davon {sum(r["status"]=="ASSUMED" for r in a)} hypothetisch zugeordnet und {sum(r["status"]=="UNREAD" for r in a)} ungelesen. Jede Gruppe steht einmal im folgenden Alignment. Die Prosa oben ersetzt dieses Alignment nicht.']
for loc in lines:
 rr=[r for r in a if r['locus']==loc];reader+=['','### '+loc,'','`'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['H'] for r in rr)]
reader+=['','## Prüfentscheidung','E und R bleiben offen. Auf f93r folgt auf sal nur der gebundene Erhitzungsbefehl; danach keine weitere Anforderung an sal/sheo. Auf f102v2 übernimmt R den vorherigen cheor-Bestand ohne angesetzte physische Vorgeschichte; „warm“ ist in E und R eine erste Zustandsangabe. Bei der späteren cheor-Nennung f102v2.39:2 führt R daher Wärme mit, E nicht; dort steht aber keine neue Temperaturanforderung. Die unterschiedlichen mitgeführten Zustände entscheiden die Stoffidentität nicht. Details und sämtliche Rivalen: REPORT.md, TARGETS.tsv, ALL_LATER_REQUIREMENTS.tsv.']
(E/'F93R_READING.md').write_text('\n'.join(reader)+'\n')
print(json.dumps(dict(groups=len(a),assumed=sum(r['status']=='ASSUMED' for r in a),unread=sum(r['status']=='UNREAD' for r in a),lines=len(lines),actions=len(chain))))
