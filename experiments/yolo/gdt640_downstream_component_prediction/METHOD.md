# GDT640 method

## Question

Halten die vier durch GDT639 neu freigelegten strikten Ein-Loch-Bedeutungen,
wenn ihre Formfamilien zuerst vollständig ausgegeben und anschließend alle
Vorkommen der exakten Oberflächen gerendert werden?

## Inputs

- das bytegebundene V16-Wörterbuch mit 280 Zeilen und 233 ausführbaren
  Oberflächen;
- GDT639s vollständige 4.128-Zeilen-Abdeckung, 39 vollständige Zeilen und 62
  Ein-Loch-Zeilen;
- die vor dem GDT640-Umlauf in GDT639 benannten vier Zieloberflächen
  `qotomody`, `qotor`, `okal`, `chotcheol`;
- GDT625s gebundenen vollständigen `tch=kalt-trocken`-Block sowie die
  Kälte-/Hitze-, Zubereitungs-, OL/OR-, AL/AR- und ODY-Rollen aus
  GDT627/GDT628/GDT633/GDT634/GDT636;
- dieselbe 179-Seiten-Auswahl wie GDT639.

ZL3b/IT2a/RF1b sind alternative Lesungen einer Handschrift. `f1r` ist
ausgeschlossen, `f84` und `f84r` sind verboten. Keine Seite und kein Bild wird
neu geöffnet.

## Method

Zuerst wird für jede Zieloberfläche eine kleine beobachtete Formfamilie
ausgegeben. Die vier Arbeitswerte werden dann unverändert nacheinander als
exakte Ganzoberflächen in den V16-Leser eingesetzt. Nach jeder Karte werden
alle 4.128 Zeilen neu berechnet und sämtliche Vorkommen der Zieloberfläche mit
Nachbarn, drei Lesungen, vorheriger und versuchsweiser Bedeutung ausgegeben.

```text
qotomody   qot+o+m+ody      kaltes Ansatzmaß, fertig aufbereitete Grundform
qotor      qo+t+or          kalte Drogenportion
okal       o+k+al           Ansatz aus heißem Rohstoff, Form I
chotcheol  cho+tch+e+ol     Trockenansatz aus kalt-trockenem Drogenstoff
```

`qotomody` ist bewusst keine leere Zelle. Seine Gesamtlesung wird auf der
Quellzeile ausprobiert und vollständig veröffentlicht. Nur die Aufnahme ins
ausführbare Wörterbuch unterbleibt, weil `m` einmal terminal in `qotom` und
einmal intern in `qotomody` steht, ohne eine unabhängige nichtterminale
Bedeutung zu besitzen.

Die drei anderen Karten gelten ausschließlich für die vollständige
Oberfläche. `qotor` globalisiert kein nacktes `or`; `okal` kein nacktes `al`;
`chotcheol` weder `cheol` noch einen anderen Substring.

## Decision rule and claim ceiling

Eine Karte kommt in V17, wenn sie ihre vorab benannte strikte Quellzeile
schließt, mindestens einen reader-exakten Anker besitzt, an allen Vorkommen
gerendert wurde und keine sichtbare Komponente löscht oder eine harte
Bedeutungskollision erzeugt. Ein konkret lesbarer Kandidat mit einem noch
ungebundenen inneren Feld bleibt als Default außerhalb des Lesers erhalten.

Die Werte sind konkrete, ersetzbare Arbeitseinträge eines technischen
Codebuchmodells. Sie sind keine behaupteten Lautwerte, historischen Wörter,
Klartexte oder Sprachidentifikation.
