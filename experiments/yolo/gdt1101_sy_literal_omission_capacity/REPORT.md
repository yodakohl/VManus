# GDT1101 — kein wörtliches Vergleichspaar mit und ohne sy

**Entscheidung: NO_LITERAL_SY_PRESENCE_ABSENCE_COMPARISON.** Die registrierte
Vierwortsuche findet keine wiederkehrende Folge, die einmal mit und einmal ohne
`sy` geschrieben ist. Daher gibt es hier keinen Umbruchvergleich und keine
Auswahl zwischen Inhaltswort, grammatischem Anschluss und Schreibfunktion.
`sy` wird nicht gestrichen oder als `von/des` bestätigt.

| Lesung | Alle exakten sy | Prüfbare sy-Rahmen | Vierwortfenster ohne sy | Kontrastpaare | Andere Blätter + gleicher bekannter Schreiber + geänderter Umbruch |
|---|---:|---:|---:|---:|---:|
| ZL3b | 27 | 15 | 20.729 | 0 | 0 |
| IT2a | 30 | 29 | 28.415 | 0 | 0 |
| RF1b | 31 | 0 | 0 | 0 | 0 |

Die 44 prüfbaren Rahmen sind 15/29 verschiedene Formenfolgen, kein gemeinsamer
Stichprobenumfang über unabhängige Texte. Jede Lesung wurde separat verglichen.
In ZL werden neun sy-Stellen wegen unsicherer intervenierender Leerstellen und
drei wegen nichtliteral lesbarer Flanken zurückgehalten; sie sind keine
Gegenbeweise. In IT fehlt für f76r.26 ein vollständiger nativer Absatz. RF hat
keine entsprechenden Absatzflags: alle 31 Fälle bleiben nicht prüfbar, ohne
ZL-Grenzen nachträglich als RF-Befund einzusetzen.

[SY_INVENTORY.tsv](artifacts/SY_INVENTORY.tsv) bewahrt alle 88 Zeilen mit Grund,
auch die unsicheren. [PRESENT_FRAMES.tsv](artifacts/PRESENT_FRAMES.tsv) enthält
alle 44 zugelassenen Vierwortkontexte, IDs und sämtliche physischen Grenzen.
`sy` steht in der Mitte ihrer fünf erhaltenen Quellgruppen; die Vierwortform
ist ausdrücklich eine Suchsignatur, kein korrigierter Manuskripttext. Beispiele:

| Fall | Geprüfter Rahmen (sy-Stelle durch senkrechten Strich) | Resultat |
|---|---|---|
| f22r.4, ZL und IT | doroiin ypchol \| schor daiin | kein zweiter identischer Rahmen ohne sy |
| f29v.3–4, ZL und IT | she otey \| ysho otshy | kein zweiter identischer Rahmen ohne sy |
| f83r.14–15, ZL und IT | shcthy dal \| saiin shedal | kein zweiter identischer Rahmen ohne sy |
| f5v.1–2, nur IT | daiin dchol \| chol otaiin | kein zweiter identischer Rahmen ohne sy |

Auch alle anderen Rahmen wurden durchsucht und oben mitgezählt. Es wurde
kein passendes Einzelbeispiel ausgesucht. Die einzigen wiederholten Rahmen im
zulässigen **Ohne-sy-Bestand**: null in ZL, einer in IT. Keine sy-Signatur ist
wiederholt. Diese Beschreibung betrifft ausschließlich die wörtlichen
Viererfolgen und sicheren Binnenabstände dieses vollständigen Absatzbestands;
sie ist keine Aussage, dass Voynich generell keine Wiederholungen besitzt.

## Was der Durchgang entscheidet

| Kandidat oder Frage | Tatsächlich prüfbare Konsequenz | Entscheidung |
|---|---|---|
| sy ist bei geänderten Zeilenumbrüchen einfügbar/entbehrlich | gleiche vier ganze Nachbarformen, mit/ohne sy, andere Umbruchlage | kein Paar; Mechanismus ungetestet |
| sy trägt eine feste sprachliche Beziehung | dieselbe Gegenüberstellung könnte weitere vollständige Kontextunterschiede verlangen | kein Paar; weder ausgewählt noch widerlegt |
| A/B/C-Aritymodelle aus GDT1100 | diese Prüfung fügt ihnen keinen bedeutungsgebundenen Operand hinzu | ursprüngliche Dreiermehrdeutigkeit bleibt |

Es gibt **0 geeignete unabhängige Bestätigungsblätter**. Bereits exponierte
Blätter wären auch bei einem Fund keine neue blinde Bedeutungsprüfung. Ein
identischer kurzer Rahmen würde zudem nicht beweisen, dass beide vollständigen
Sätze dieselbe Sache sagen; deshalb ist sogar ein denkbarer Fund allein kein
Lexikonnachweis. Keine Signifikanzbehauptung, keine neue scorefähige Relation,
keine Bedeutungsbestätigung, keine neuen Datenfreigaben oder Bilder.

GDT829s Nullbefund zur terminalen l/m-Variation bleibt unverändert. Hier wurde
mit eigener, vorab eingefrorener Frage die Einfügung einer **ganzen sy-Gruppe**
geprüft. Die Nullzahl wird nicht durch kürzere Flanken, ähnliche Schreibungen,
geschätzte Morpheme, eine andere Endung oder weitere Seiten repariert. Eine
weitere Suche müsste eine andere inhaltlich begründete Konsequenz besitzen.
Die Randvorliebe aus GDT1100 bleibt eine Beobachtung, keine Leseregel.
AS, GDT1090 und die unbestätigte schor-Spur werden nicht umgeschrieben.

## Reproduktion und Buchhaltung

[METHOD.md](METHOD.md) wurde mit Runner, Validator und den festen Vorgängern
am **2026-09-29 20:15:38.490325 UTC** gehasht; Vorbereitung begann20:04:34UTC.
Alle Quellen sind die sechs bereits geschützten GDT915-Projektionen mit179
freigegebenen Selektoren. Der Selektor wird vor dem Gruppeninhalt geprüft.
f84/f84r bleiben versiegelt, f116v ausgeschlossen. ZL/IT/RF sind alternative
Transkriptionen desselben Manuskripts; die Untersuchung war nicht blind.

Der Runner nutzt GDT1100s eingefrorene Absatzrekonstruktion. Der Validator
rekonstruiert Absätze und Literalrahmen separat aus den Quellprojektionen:
659ZL- und690IT-Absätze, sämtliche88sy-Gruppen, alle44Prüfrahmen und alle49.144
Ohne-sy-Fenster stimmen überein. Anschließend besteht ein bytegenauer Replay.
Der PASS bezeichnet ausschließlich Literalprüfung und Reproduzierbarkeit.

```
python experiments/yolo/gdt1101_sy_literal_omission_capacity/src/run.py
python experiments/yolo/gdt1101_sy_literal_omission_capacity/src/validate.py
```

Die kompletten Ohne-sy-Fenster werden aus den gehashten Quellen rekonstruiert;
ein geordneter Digest ist in RESULT.json gespeichert. MATCHING_ABSENT_FRAMES.tsv
und PAIRS.tsv sind gültige Tabellen mit Kopfzeile ohne Datenzeilen. Es gibt
entsprechend keine gepaarten Vollabsätze, deren Inhalt als neue Aussage gelesen
werden könnte. Keine alten Quelldateien oder Decodereinstellungen wurden verändert.

Die parallel begrenzte Quellensichtung AV lieferte0neue Ideen: bestehende
Quellenfolgen sind bereits im Ideenbestand. Sie ist keine unabhängige
Bedeutungsprüfung. Abschlusszeit und Veröffentlichungszustand in CLOSURE.json.
