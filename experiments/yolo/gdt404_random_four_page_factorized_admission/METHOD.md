# Methode

## Frage

Halten die feste 46-Zeichen-Tafel und der faktorzerlegte Scope-Parser auf vier
wirklich zufällig gezogenen, zuvor nicht in der 22-Seiten-Ausgabe enthaltenen
Seiten, ohne einen Kernwert umzudeuten oder eine neue Scope-Regel zu erfinden?

## 1. Einmalige Zufallsauswahl

Aus 178 erlaubten physischen Seiten außerhalb der bisherigen 22 Seiten wurde
mit Seed `2c3b94fccfaa6aa88e557bbd03730d9a` genau einmal gezogen:

`f1r | f24v | f81r | f95v`

Es gab kein Nachziehen. `f95v` wird in ZL3b als `f95v1` und `f95v2` geführt;
beide Paneele gehören zur gezogenen physischen Seite.

## 2. Guarded Quelle

Die Zeilen wurden ausschließlich mit `./vmanus-exp query-tsv` und den fünf
expliziten Allow-Werten `f1r`, `f24v`, `f81r`, `f95v1`, `f95v2` geladen. Der
gesperrte Präfix wurde vor der Materialisierung verworfen. Ergebnis: 95
Quellzeilen und 688 Kartenereignisse.

## 3. Bild zuerst

Vor der Textdeutung wurden vier Originalbilder einzeln betrachtet und Besitzer
eingefroren:

- f1r: vier rubrizierte Textblöcke, kein sicherer Gegenstandsbesitzer;
- f24v: eine Ganzpflanze für zwei Prosaabschnitte;
- f81r: getrenntes oberes und unteres Figurenbecken; keine erfundene Richtung;
- f95v: eine Ganzpflanze für beide Textpaneele.

## 4. Oberflächenvertrag

Eine bereits in Pass 1026 vorkommende Oberfläche behält bytegleich ihr altes
Rezept. Eine neue Oberfläche darf nur aus den 46 vorhandenen Zeichen bestehen.
Ein Ein-Edit-Nachbar ist nur Vergleich, nie automatische Lizenz.

Die 211 neuen Oberflächen wurden vollständig explizit zerlegt. 162 haben eine
klare sichtbare Zusammensetzung; 49 besitzen mehr als eine plausible innere
Grenze und bleiben Amber. Keine bekommt einen neuen Bedeutungsstamm.

## 5. Aussagen

Ein lizenziertes terminales `DY` schließt die laufende Aussage. Sonst bleibt sie
über physische Zeilen offen und endet erst am realen Prosa-/Besitzerblock. Das
ergibt 88 Aussagen: 78 geschlossen, 10 blockfinal offen; 37 laufen über
mindestens eine physische Zeile.

## 6. Faktorzerlegter Scope

Jedes Vorkommen von `AIIN, AIN, OR, Y, E, EE, EEE, AL, AR, L, AIR` wird mit
dem unveränderten GDT399/GDT402-Mechanismus gebunden. Zulässig sind nur:

- 8 Scope-Selectoren;
- 6 sichtbare Geometrien;
- 10 Zielköpfe einschließlich Besitzer;
- 4 R-Lagen;
- 3 Doppelungsmodi;
- höchstens eine Karte Vorgriff;
- niemals eine Besitzer- oder Aussagegrenze.

## 7. Ehrlicher Grenz-Stresstest

Zwei Amber-Formen enden im Arbeitsrezept auf `DY`. Deshalb wird der gesamte Lauf
zweimal gebaut: einmal mit diesen Schlüssen und einmal, als ob beide nicht
schließen. Der zweite Lauf darf weniger Aussagen haben, aber keine neue Achse
oder Grenze benötigen.

## 8. Reproduzierbarkeit

Der Validator baut alle Artefakte zweimal bytegleich neu und prüft Quelle,
Reihenfolge, Rezepte, Aussagen, Bindungen, Bilder, Achsen, Grenzen, Rekurrenz,
gesperrte Daten und private Pfade.
