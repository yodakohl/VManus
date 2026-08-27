# GDT514 — Methode

## Frage

Welche vier bislang unbenutzten Seiten bilden den zweiten Zufallsbatch, und
welche sichtbaren Besitzer- und Blockgrenzen müssen vor jeder Textlesung
gelten?

## Seitengrundmenge

Der Builder erzeugt alle syntaktisch möglichen ZL3b-Seitenselektoren von
`f1r` bis `f116v6`, lässt den gesamten Folio-84-Präfix aus und reicht diese
Werte als explizite Allow-Liste an `./vmanus-exp query-tsv`. Materialisiert
wird ausschließlich die Spalte `page`.

Die 224 tatsächlich vorhandenen erlaubten Selektoren werden durch Entfernen
eines abschließenden Paneelzählers zu 200 physischen Seiten zusammengeführt.
Dasselbe geschieht mit den 26 Seiten der GDT407-Ausgabe. Es verbleiben exakt
174 Kandidaten.

## Einmalige Ziehung

Der Seed ist die erste 128-Bit-Hälfte von
`SHA256("GDT514|158184d6|second-random-four-page-batch")`:
`b8cf14cd694c9a44f2b321a4e0a8af1c`.

`random.Random(int(seed, 16)).sample(sorted(candidates), 4)` liefert in
Ziehungsreihenfolge:

`f31r | f66r | f20v | f4r`

Es gibt kein Nachziehen. Alle vier Seiten besitzen genau einen
ZL3b-Quellselektor.

## Bild zuerst

Erst nach der Ziehung wurden die vier offiziellen Yale-IIIF-Bilder in
Originalauflösung betrachtet. Festgehalten werden nur neutrale
Layoutbeobachtungen und Verbindungsgrenzen:

- f31r, f20v und f4r besitzen jeweils eine sichtbare Ganzpflanze;
- f66r ist textdominiert und besitzt mehrere räumlich getrennte Hauptblöcke;
- Randzeichen und der späte untere Nachtrag auf f66r werden nicht mit der
  laufenden Hauptprosa verschmolzen;
- Pflanzenbestandteile werden nicht ohne sichtbare Zuweisung zu eigenen
  Textbesitzern gemacht.

## Grenze und nächster Schritt

GDT514 öffnet keine Voynich-Textspalte der vier Seiten. Es ändert kein Rezept,
keinen Stamm und keine Bedeutung. Der nächste Schritt darf ausschließlich die
vier Selektoren über die geschützte Abfrage laden und muss die hier
veröffentlichten Besitzergrenzen beibehalten.
