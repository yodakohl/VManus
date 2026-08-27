# GDT513 method

## Question

Was sind die 510 lokalen Gruppen, die außerhalb der bereits abgeschlossenen
183-Ereignis-Adressausgabe liegen, und welche Erwartungen ergeben sich daraus
für vier weitere Seiten?

## Inputs

- GDT407: 693 lokale Gruppen sowie der vollständige Lauftextkatalog;
- GDT408: seitenweiser Oberflächen-/Rezepttransfer der 693 Lokalgruppen;
- GDT413: aktuelles Wörterbuch mit 19 portablen Arbeitskernen und 27 formalen
  oder lokalen Strukturwerten;
- GDT473: die bereits vollständig behandelten 183 Adressereignisse;
- GDT405: 426 gesperrte Oberflächenrezepte für den nächsten Vierseitenbatch.

Die 510 Zeilen sind die exakte Mengen-Differenz `GDT407 lokal minus GDT473`.
Sie stammen überwiegend aus der älteren P912/Pass-1009-Schicht. Ihre 501
Komponentenrezepte sind daher **geerbte Arbeitszerlegungen**, keine in GDT513
neu entdeckten unabhängigen Wortgrenzen. GDT513 prüft, wie weit diese
Zerlegungen mit dem heutigen Wörterbuch, Lauftextkatalog und GDT405-Lock
zusammenpassen.

## Complete default reading

Jedes Rezept wird atomweise durch GDT413 gelesen. Portable Arbeitskerne werden
als breite deutsche Defaults ausgegeben. Formalkontrollen und Lokalzeichen
bleiben sichtbar geklammert. Sechs bereits in GDT407 benannte lokale Makros
bleiben ebenfalls reine Struktur-Tags:

`CHEO=LOKALER EINTRAG`, `CTH=BEREITSCHAFTSKLASSE`,
`CHK=BEDINGUNGSKLASSE`, `CPH=GEGENPLATZ`,
`CKH=VERBINDUNGSWEG`, `CFH=TRENNKLASSE`.

Die Karten werden aus der sichtbaren Komponentenfolge in fünf Rollen gelegt:
Anweisung, Adresse/Fortsetzung, Koordinate/Katalog, lokale Kennung oder
Abschnittsmarke. Diese Rollen sind Default-Paraphrasen, keine bestätigte
Syntax.

## Five working hypotheses

1. produktive Formelschicht;
2. reines Nomenklator-/Namenbuch;
3. positionsgebundene Datensatz- oder Recordkarten;
4. besitzergebundener Renderer;
5. Mischmodell aus Formel, Record und gelerntem Inhalt.

Die Rangfolge ist eine explizite explorative Arbeitstheorie, kein statistischer
Score. Entscheidend sind vollständige Abdeckung, direkte Laufrezeptkontakte,
Seitenprivatheit, Rollenvielfalt und sichtbare Strukturkonflikte.

## Collision and future-page rule

Gleich geschriebene Lauf- und Lokalformen mit abweichender Zerlegung werden
nicht zu Polysemie erklärt. Jede Kollision wird auf lokale Makros,
Klassenzeichen oder eine lokale Scope-/Schlussgrenze geprüft. Berührt die
Oberfläche GDT405, gilt für den neuen Batch weiterhin bytegenau das dort
gesperrte Rezept. Eine alte lokale Lesart darf den Zukunftslock nicht ändern.

## Decision rule and claim ceiling

Kein Struktur-Tag wird zum Wort befördert. Kein portabler Wert, keine
Oberfläche und keine Seite wird durch GDT513 geändert oder erfunden.
