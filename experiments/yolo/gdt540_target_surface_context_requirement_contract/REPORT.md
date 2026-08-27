# GDT540 — der Satzkontext ist jetzt eine konkrete Leserregel

Status: `PASS_149_OCCURRENCES_CLASSIFIED__145_SURFACE_CONTRACTS__ONE_CONTEXT_SWITCH`

## Ergebnis

Alle 149 neuen Prosavorkommen besitzen jetzt eine konkrete
Kontextanforderung:

- 92 sind im bekannten Satz selbständig;
- fünf holen nur die laufende Handlung;
- 41 holen nur das laufende Argument;
- elf holen Handlung und Argument.

Auf die 145 Oberflächen zusammengezogen ergeben sich 88 nur selbständig
beobachtete, fünf handlungsabhängige, 40 argumentabhängige und elf doppelt
abhängige Formen. Eine Oberfläche besitzt zwei Modi.

## Der wichtige Umschalter

Nur drei Oberflächen wiederholen sich. `keody` erscheint dreimal und `shain`
zweimal, jeweils mit demselben selbständigen Modus. `qokees` erscheint zweimal
mit exakt `OK+EE+S`: am Satzanfang wird „ansetzen und wählen; Grad II“
objektlos gelesen, nach einem sichtbaren `Y` übernimmt dieselbe Form den
laufenden Eintrag.

Das macht aus einer früher stillschweigenden Ergänzung eine einfache
Vorhersageregel:

- sichtbare Handlung vorhanden: sie lesen;
- keine sichtbare Handlung: die letzte Handlung desselben Satzes einsetzen,
  sonst nur ein nichtverbales Fragment ausgeben;
- sichtbares Argument vorhanden: es lesen;
- kein sichtbares Argument: das laufende Satzargument übernehmen, falls eines
  existiert, sonst objektlos bleiben.

Damit ist `qokees` kein widersprüchliches Ganzwort. Es ist eine sichtbare
Handlungskombination mit freier Objektstelle, die der Satzkontext füllen kann.

## Wie viel Gedächtnis nötig ist

Die sechzehn übernommenen Handlungen liegen achtmal eine, sechsmal zwei und
zweimal drei Karten zurück. Die 52 übernommenen Argumente liegen 39-mal eine,
neunmal zwei und viermal drei Karten zurück. Alle Quellen stehen links im
selben Satz. Der Leser braucht weiterhin nur zwei gespeicherte Werte — letzte
sichtbare Handlung und letztes sichtbares Argument — nicht 145 individuelle
Sonderregeln.

Die beobachtete Dreikartenreichweite ist keine künstliche Zukunftsgrenze. Die
Satzgrenze bleibt die eigentliche Grenze.

## Praktischer Gewinn

`src/context_surface.py` nimmt eine der 145 Oberflächen und optional einen
aktiven Handlungs- und Argumentsstamm. Es zeigt, ob eine kontextuelle
Werkstattlesung sofort möglich ist, ob ein Argument übernommen wird oder ob
wegen fehlender Handlung nur eine Fragmentlesung zulässig ist.

Alle 50 Prüfungen bestehen. Kein Rezept, Stammwert oder Seitenbestand wurde
verändert.

## Nächster sinnvoller Schritt

Jetzt sollten die 49 betroffenen Aussagen nicht weiter Wort für Wort geglättet
werden. Sinnvoller ist ein Zustandslauf, der die 145 Oberflächen aus leerem
Satzanfang erneut einliest und für jede Aussage den genauen Ein- und
Ausgangszustand zeigt. Danach kann derselbe kleine Leser auf bereits
zugelassenen, aber bisher nicht als Vier-Seiten-Test verwendeten Material
angewandt werden, bevor weitere Seiten geöffnet werden.
