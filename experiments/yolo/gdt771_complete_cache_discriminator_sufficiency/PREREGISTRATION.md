# GDT771 — Festgelegte Suche nach den vier fehlenden Kontrasten

Datum: 2026-09-03

## Ziel

GDT771 prüft ausschließlich im bereits vorhandenen Cache, ob die nach GDT770
fehlenden Kontexte für `ol`, `ckhy`, `ols` und `otar` vorhanden sind. Es werden
keine neuen Seiten, Bilder, OCR-Zeilen oder Transkriptionen geöffnet. `f84` und
`f84r` bleiben gesperrt.

## Quellen und Zulassung

- Die Zieloberflächen und target-unabhängigen Frames stammen aus GDT769.
- Die gemischte GDT734-Zeilentabelle wird nur durch `vmanus-exp query-tsv`
  gelesen. Ihre explizite Allow-Liste sind die 461 bereits bekannten
  `ol/ckhy/ols/otar`-Loci des GDT769-Atlas.
- GDT760s Mengenatlas wird mit derselben Allow-Liste und nur vierzehn
  angeforderten Spalten gelesen. Ein Mengenspan zählt links von `ol` nur, wenn
  sein besessener Span genau bei `ol-1` endet und das rechte `ol` reader-exakt
  ist.
- Als vollständige Zeile gilt eine GDT734-Zeile mit
  `complete_line_v99r7=1` und null unbekannten Zellen oder eine der fünfzehn
  später in GDT770 zugelassenen Zeilen.
- GDT770s Ausschlussregister bleibt bindend. Fünf zusätzliche vollständige,
  aber noch mit zurückgezogener Hauptwort- oder Quellkompositionsprosa
  belastete Zeilen stehen ausdrücklich in
  `src/ADDITIONAL_EXCLUSION_SPECS.tsv`; ihre lokalen Kontakte bleiben als
  Sensitivität sichtbar, tragen aber keine strenge Entscheidung.

Die nackten Wertformen, zwei ausdrücklich geprüften linken Rollenübernahmen,
vier rechten Rollenübernahmen und der konservative Crosswalk stehen als
eigene TSV-Quellen unter `src/`. Diese Tabellen übertragen Strukturrollen,
keine deutschen Wörter, Lexeme oder EVA-Buchstabenwerte.

## Acht Kontraste

`src/DISCRIMINATOR_SPECS.tsv` enthält acht feste Zeilen:

1. lizenzierte Menge oder Wert unmittelbar links von `ol`;
2. derselbe Zweig mit physisch vorhandenem reader-exaktem Rechtsnachbarn;
3. der vollständige GDT770-Zweig mit einer rechts erlaubten
   Stoff-, Prozess-, Feld-, Quellen-, Patienten-, Resultat-, Endpunkt- oder
   Produktrolle;
4. finales `ckhy` mit dem GDT769-Patientenframe;
5. `ols` unmittelbar vor einem eigenen Wertfeld;
6. allgemeine `otar`-Folgebrücke;
7. nominale `otar`-Brücke;
8. `otar` zwischen linkem Prozess/Feld und rechtem Endpunkt.

Ein rechter Mengen-/Wertkontakt erfüllt beim dritten Kontrast nicht
automatisch die rechte Pflichtkante. `QUALITY_STAGE`, `CLOSE` und
`KNOWN_OTHER` werden ebenfalls nicht still zu `FIELD` oder `ENDPOINT`
umbenannt.

## Entscheidung und Behauptungsgrenze

Ein Kontrast ist verfügbar, wenn seine Mindestzahl an Vorkommen und Seiten
erreicht wird und nach Entfernung der stärksten Seite noch die festgelegte
Seitenzahl bleibt. Ein PASS bedeutet nur, dass der Kontext für die nächste
Score-Runde vorhanden ist.

GDT771 vergibt keine Lexeme, keinen Klartext und keinen Komponentenexport.
`von/aus`, `mischen`, `fertige Zubereitung`, `dann/weiter`,
`Zwischenzubereitung` und `bis zum Endzustand` sind austauschbare Anzeigen der
jeweiligen Kandidaten, keine Übersetzungsbestätigungen.
