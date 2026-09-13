import csv,json
from pathlib import Path
E=Path(__file__).resolve().parent
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
a=rows(E/'O_A_ALIGNMENT.tsv');byid={r['locus']+':'+r['index']:r for r in a}
text=['# W33: ol als Zubereitungsposten, lor bleibt mit — vollständiger Gegenentwurf O','Diese Fassung ist eine bedingte Gegenlesung zu W28, keine ausgewählte globale Übersetzung. Alle1045Gruppen bleiben erhalten; A/H ist die Anzeige, Q/D/B/J/M/O/I sind geprüft. Die anderen ganzen Lexika stehen in L_Q/A_READING.md und OL_Q/A_READING.md, C unverändert in W28.','## Konkreter Lesungsbaustein auf f106r','„[Zubereitungsposten] … vollständig kühlen, abkühlen … vollständig abgekühlt.“ Die drei Auslassungen ersetzen keine gelesenen Wörter; die vollständige Folge mit den offenen Gruppen steht unten. oteedy .8:6 und qotor .8:7 binden ol .8:3, qoteedy .8:9 wird am selben Objekt geprüft und passt zu dessen angesetztem Kältezustand. Zwei Kühlbefehle bleiben zwei; ihr unterschiedlicher Zweck ist ungeklärt.','Die folgende Zeile ist kein gelesener Kühl-Wärme-Zyklus dieses Ansatzes. Unter J/M nimmt ychor die erwärmte Dosis qokain .9:3 auf, die chol erhitzt (D: trocknet). Unter B nimmt ychor nun den vorherigen ol-Posten, während chol weiterhin qokain behandelt. qokar am Ende bleibt ein weiterer angesetzter Anteil. Keine ungeschriebene Abfüllung oder Identität wird ergänzt.','## Sämtliche geänderten direkten Verarbeitungsbezüge','| Stelle | Bisheriger Patient C | Neuer Patient O |','|---|---|---|']
for r in rows(E/'ALL_CHANGES.tsv'):
 if r['candidate']=='O' and r['shol']=='A' and r['table'] in ['ARGUMENTS','QUALITY']:
  c=json.loads(r['C']);n=json.loads(r['N'])
  if n['grammar']=='J':text.append('| '+n.get('operation',n.get('mention',''))+' | '+(c['patient']+' '+byid[c['patient']]['H'] if c['patient'] else '[fehlt]')+' | '+n['patient']+' '+byid[n['patient']]['H']+' |')
text+=['','Die Tabelle nennt J; B/M haben dieselben sechs veränderten Verarbeitungsstellen. Der zusätzliche Nimm-Bezug auf f106r tritt nur unter B auf. Alle Bindungsschulden, insbesondere offene Zwischenwörter, stehen unverändert in den Argument-/Qualitätstabellen.','## Alle Wörter in der O-Fassung']
for p in dict.fromkeys(r['paragraph'] for r in a):
 text+=['','### '+p]
 for loc in dict.fromkeys(r['locus'] for r in a if r['paragraph']==p):
  rr=[r for r in a if r['locus']==loc];text+=['',loc+' · `'+' '.join(r['raw'] for r in rr)+'`','',' · '.join(r['H'] for r in rr)]
(E/'READING.md').write_text('\n'.join(text)+'\n')
