# GDT637 method

## Frage

Tragen die in GDT636 sichtbaren Fortsetzungen `aiir`, `oiiin`, `aim` und
`aiim` dieselben Stoffköpfe und dieselbe Stufenlogik weiter, und welche bereits
geöffneten Zeilen werden mit dem daraus entstehenden V14-Wörterbuch vollständig
oder bis auf genau ein konkretes Token lesbar?

## Eingaben und Umfang

- unveränderte GDT636-Auswahl von 179 Seiten;
- GDT636-Wörterbuch V13 mit 251 Zeilen;
- GDT636-Restkörper-, Ergebnis- und Builder-Artefakte;
- ZL3b-Token und ZL3b/IT2a/RF1b-Zeilen ausschließlich über zwei geschützte,
  explizit seitenbegrenzte Projektionen.

`f1r` ist nicht in der Auswahl. `f84` und `f84r` bleiben verboten. Es wird
weder eine neue Seite noch ein Bild geöffnet.

## Vier Leiterkörper und sechzehn Kopfzellen

Für jeden Körper werden die vollständigen Oberflächen `p/s/r/l + Körper`
gezählt:

```text
aiir   a+ii+R   Teil-/Sortierklasse III
oiiin  o+iiin   Formklasse IV
aim    a+i+m    Mengenklasse II
aiim   a+ii+m   Mengenklasse III
```

Eine belegte Oberfläche erhält die mechanische Komposition aus Stoffkopf und
Stufe. Eine leere Zelle wird nur als Vorhersage ausgewiesen und nicht ins
Wörterbuch aufgenommen. Bei `aim/aiim` kommt „Eintrag abgeschlossen“ nur dann
hinzu, wenn das konkrete Token wirklich am Zeilenende steht.

Die drei Überschriften sind GDT637-Oberklassen, keine rückwirkende
Umbenennung des byte-fixierten V13-Präfixes. Dort bleiben `ar/air` wörtlich
`Fraktionsklasse I/II` und `am` wörtlich `Maß-/Einheitsform I`. In den
Kontrastzeilen stehen deshalb jeweils alter V13-Wert und neuer GDT637-Wert
nebeneinander; nur ihre relative Stellung in derselben sichtbaren Minimreihe
wird gemeinsam beschrieben.

Die Körperkoexistenzen werden nach Abziehen eines tatsächlich vorhandenen
initialen `p/s/r/l`-Kopfes gezählt. So können `sar` und nacktes `aiir` dieselbe
Körperkontrastzeile bilden, ohne die vollständigen Oberflächen gleichzusetzen.

## Scope-sensitiver Zeilenleser

V13 wird nicht als naive Zeichenkette benutzt. Der Leser übernimmt:

- vollständige GDT635/GDT636-Kopfformen;
- konkrete V13-Zieloberflächen;
- einzeln geschriebene, lizenzierte Qualitäts-, Wert-, CTH- und Trägerformen;
- die acht belegten GDT637-Leiterformen;
- den alten `daiir`-Wert ausschließlich an `f85r1.21`.

Die 19 GDT636-Restkörper werden niemals als nackte Wörter globalisiert.
Komponenten wie `a` oder `d` zählen nicht selbständig als konkrete Wörter.
Jedes gelesene Token trägt einen sichtbaren Zustand:

```text
KNOWN_EXACT_WHOLE
KNOWN_CONTEXT_LICENSED
AMBIGUOUS_ACTIVE_RIVAL
UNKNOWN_SURFACE
READER_BOUNDARY_UNSTABLE
```

Eine strenge Ein-Loch-Zeile hat genau ein unbekanntes Token, keinen aktiven
Trägerrivalen, keinen Leserbruch unter den bereits gelesenen Token und eine
vollständig identische ZL3b/IT2a/RF1b-Zeile. Die explorative Hauptliste behält
zusätzlich sinnvolle, aber leserinstabile Kandidaten sichtbar.

## Vorschläge für das einzelne Loch

Für jedes der 65 Löcher wird ein kurzer Vorschlag ausgegeben. Dreizehn besonders
transparente Formen wurden separat als sichtbare Komposition gelesen, darunter
`otchol`, `keechy`, `cthoiin`, `cthor`, `choiin`, `dol`, `doiin`, `oaiir` und
`kcho`. Der übrige automatische Vorschlag darf nur bereits sichtbare Stoff-,
Qualitäts-, Träger-, Form- oder Abschlussfelder zusammensetzen. Bei opakem Rest
steht ausdrücklich `ungeklärt`; generische Prozessprosa ist nicht erlaubt.

Keiner dieser Lochvorschläge wird in V14 übernommen. V14 besteht aus allen 251
V13-Zeilen als identischem Präfix plus genau den acht belegten Leiterformen.

## Abgrenzung zu GDT582

GDT582 füllte nach einer festen Struktursegmentierung 30 Seiten mit breiten
Registerdefaults und sagte keine neuen Rohoberflächen voraus. GDT637 arbeitet
auf 179 Seiten direkt an geschriebenen Token, erweitert vier sichtbare
Minimreihen und veröffentlicht konkrete neue Kompositionsvorschläge. Es ist
daher kein erneuter generischer Fülldurchgang.

## Aussagegrenze

Das Ergebnis ist eine ersetzbare Arbeitsübersetzung mit relativen Stufen und
konkreten Passagekandidaten. Es identifiziert keine Sprache, Lautwerte,
historischen Einheiten oder sicheren Klartext. „III“ bedeutet die dritte
sichtbare Stufe der jeweiligen Reihe, nicht automatisch drei Unzen oder eine
andere bestimmte Maßeinheit.
