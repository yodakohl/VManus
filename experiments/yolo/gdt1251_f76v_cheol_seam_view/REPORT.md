# GDT1251 — Abstand cheol/chey nicht entschieden

**UNRESOLVED_REGION_MISLOCALIZED.** Der einzige Detailausschnitt liegt zu hoch
und schneidet die ausgewählte Zielzeile f76v.28 am unteren Rand an. Damit ist
kein zuverlässiger Vergleich der strittigen Innenlücke mit beiden äußeren
Abständen möglich. Dies ist ein Lokalisierungsfehler, kein negativer Befund
über Wortzusammensetzung oder eine Wahl zwischen den Transkriptionen.

## Feste Frage und Quelle

Vor Bildzugriff wurde ausschließlich f76v.28 ausgewählt. IT2a schreibt dort
`cheol chey` mit DEFINITE_SPACE; ZL3b/RF1b schreiben `cheolchey`. Der feste
Vergleich sollte SPACE_LIKE, INTERNAL_LIKE oder UNRESOLVED ergeben. Gleiche
Bedeutung getrennter und verbundener Formen war nicht Teil des Tests.

Eine neue begrenzte Bildzulassung wurde vor Zugriff dokumentiert in
`docs/VOYNICH_DATA_SCOPE_20261007_F76V_SEAM.md`; die alte179-Textzulassung war
keine Bildfreigabe. Das aktuelle offizielle Yale-IIIF-v3-Manifest bezeichnet
Canvas1006211 als76v. Der erste Metadatenleser erwartete noch v2 und stoppte
ohne Treffer; die v3-Auswertung korrigierte die Navigation vor Bildzugriff.

Die vollständige Original-JPEG-Aufnahme misst2823×3712Pixel, SHA256
`affdb2ff70e84ae277d3d30d18b3a468bd4eded393f70514978ad8b0c48df49e`.
Quellenvertrag, Scope und Fetcher waren vor Abruf lokal gebunden. Empfang,
Dimensionen und Hash wurden vor der ersten Ansicht gespeichert.

## Tatsächlicher Bilddurchgang und Abweichung

Root betrachtete die vollständige Aufnahme zur Lokalisation und anschließend
einen originalen IIIF-Ausschnitt bei x760,y2070,Breite1910,Höhe160. Die
vorläufige Zuordnung zur vierten Zeile des vierten Hauptblocks war in der
Wahl der vertikalen Ausschnittlage unzureichend umgesetzt: Der Ausschnitt zeigt
die dshol/qokaiin- und die daiin/shckhey-Zeile; die eigentliche saiin/sheckhy-
Zielzeile wird angeschnitten. Die strittige Innenstelle wurde nicht beurteilt.

Der Ausschnitt erfasst dabei auch Bildinhalt von .26 außerhalb des vorgesehenen
Nachbarbands .27–29. Diese Abweichung bleibt ausdrücklich als Exposition
vermerkt, nicht als zusätzliche Freigabe oder Beleg. Kein zweiter Ausschnitt,
anderes Ziel, OCR, Bildverbesserung oder nachträglich passender Messwert.

Alle93Rohgruppen der vorher festgelegten .27–29 aus den drei Lesungen bleiben
in SOURCE_LINES.tsv erhalten. Die drei Lesungen betreffen dieselbe Handschrift.
Eine informierte KI-Betrachtung ist keine unabhängige Paläographie.

## Entscheidung

Alle drei Abstandsbeurteilungen bleiben UNRESOLVED. Die Zusammenschreibungen
an anderen Stellen und die formalen cheol-Kandidaten bleiben unverändert.
Für f76v.28 gibt es durch diesen Versuch KEINEN neuen Beleg für absichtliche
Zusammen-/Getrenntschreibung oder für deren Bedeutung. GDT910s fehlende
wiederkehrende Ersetzungsregel wird nicht durch die Bildarbeit aufgehoben.

Die Quellen-/Chronologieprüfung besteht; sie bestätigt auch, dass die
ungeklärte Entscheidung samt Abweichung korrekt gespeichert ist. Ihr PASS
bestätigt weder die Lokalisation noch den Abstand noch die Einhaltung des
beabsichtigten Detailbands. Ergebnisreduktion und Validator wurden nach der
Beobachtung geschrieben; sie erzeugen keine unabhängige Bildbeurteilung.

## Reproduktion

```
python experiments/yolo/gdt1251_f76v_cheol_seam_view/src/fetch_source.py
python experiments/yolo/gdt1251_f76v_cheol_seam_view/src/run.py
python experiments/yolo/gdt1251_f76v_cheol_seam_view/src/validate.py
```

IMAGE_RECEIPT und REGION_RECEIPT bewahren beide exakten Quell-URLs und Hashes;
REGION_SELECTION bewahrt die Auswahl vor der Detailansicht. Ein erneuter
Reducer-Lauf reproduziert die gespeicherte Entscheidung, nicht eine neue
Bildprüfung. Kein Wort übersetzt, kein semantisches Relationsergebnis.
Lokaler Checkpoint unter der bestehenden Nutzerausnahme, kein Push.
