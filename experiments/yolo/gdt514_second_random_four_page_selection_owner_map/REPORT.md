# GDT514 — Der zweite Vierseitenbatch ist ausgewählt

## Ergebnis

`PASS_SELECTION_AND_OWNER_MAP_READY`.

Die geschützte Seitenspalte ergibt 224 erlaubte Quellselektoren und nach
Paneel-Normalisierung exakt 200 physische Seiten. Nach Abzug der 26 bereits
gelesenen Seiten bleiben 174 Kandidaten. Die einmalige Ziehung ergibt:

| Ziehung | Seite | sichtbarer Hauptbesitzer |
|---:|---|---|
| 1 | f31r | eine Ganzpflanze |
| 2 | f66r | getrennte Hauptprosablöcke ohne Gegenstandsbesitzer |
| 3 | f20v | eine Ganzpflanze |
| 4 | f4r | eine Ganzpflanze |

Kein Kandidat wurde ersetzt oder nachgezogen. Jede ausgewählte physische Seite
entspricht genau einem Quellselektor.

## Was die Bilder bereits sagen

Die drei Kräuterseiten verlangen keine neue Besitzerlogik. Ihre jeweils zwei
sichtbaren oberen Textbereiche können denselben Ganzpflanzenbesitzer erben;
Blüte, Blatt, Trieb und Wurzel werden nicht künstlich als getrennte
Datensätze behandelt.

f66r ist der nützliche Kontrastfall. Die Seite zeigt mehrere durch Leerraum
getrennte Hauptprosablöcke, kurze Randzeichen und einen klar separaten späten
Nachtrag mit kleiner Tierzeichnung am unteren Rand. Für die kommende Lesung
gelten deshalb Hauptblockgrenzen; Randmaterial und Nachtrag dürfen keine
laufende Aussage verlängern.

## Warum das ein guter nächster Batch ist

Der Batch kombiniert drei neue Herbal-Seiten aus unterschiedlichen
Hand-/Registerlagen mit einer textdominierten Seite. Damit kann das
GDT405/GDT513-Mischmodell sowohl unter einem stabilen sichtbaren
Ganzpflanzenbesitzer als auch ohne Gegenstandsbesitzer weiterlaufen. Zugleich
ist keine Sonderseite oder Paneelzusammenführung nötig.

## Nächster Schritt

Nun werden genau `f31r`, `f66r`, `f20v` und `f4r` mit
`./vmanus-exp query-tsv` geladen. Für jede Folge gilt zuerst der
GDT405-Oberflächenlock, danach sichtbare Zusammensetzung aus den vorhandenen
Zeichen und schließlich die fünf GDT513-Erwartungen. Erst dieses nächste
Experiment entscheidet, ob die vier Seiten in die laufende Ausgabe aufgenommen
werden können.

## Grenze

GDT514 ist Auswahl und Bildkarte, keine Übersetzung. Es identifiziert keine
Pflanze, öffnet keinen Voynich-Textinhalt der vier Seiten und ändert weder
Wortstamm noch Rezept noch Arbeitsbedeutung.
