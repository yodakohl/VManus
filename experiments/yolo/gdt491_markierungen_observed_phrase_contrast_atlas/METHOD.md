# GDT491 — Methode

## Question

Welche bereits vorhandenen deutschen GDT416-Klauseln realisieren die elf
R-seitigen GDT428-Rahmen? Für wie viele Rahmen kann außerdem ein beobachtetes
T/R-Satzpaar gewählt werden, bei dem außer der Aktionsform der gesamte deutsche
Wortlaut gleich bleibt?

## Inputs

- GDT416: 4.576 owner-lokale Imperativklauseln mit exakter Rückprojektion;
- GDT428: 104 Aktionsersatzrahmen, davon elf T/R-Rahmen;
- GDT490: 22 beobachtete T-Satzformen und elf beobachtete T-Defaults.

## Method

1. In jedem T/R-Rahmen wird `@ACTION` durch `R` ersetzt und das Rezept exakt
   gegen GDT416 gehalten. Alle Treffer behalten Event, Seite, Register,
   Besitzerklasse, Oberfläche, Schablone, Klausel und Rückprojektion.
2. Identische deutsche Klauseln werden nur innerhalb desselben Rahmens
   zusammengefasst. Der R-Default ist die häufigste beobachtete Klausel; bei
   Gleichstand gewinnt die kürzere, dann die alphabetisch erste.
3. Für den direkten Kontrast werden die 22 alten T-Formen mit den 22 R-Formen
   desselben Rahmens gekreuzt. Nur die bekannten Aktionsrealisierungen
   `stelle … ein`, `lege … fest`, `markiere` und `kennzeichne` werden durch
   `@ACTION` ersetzt. Alle Argumente, Relationen, Grade, Folgehandlungen,
   Besitzerwörter und Satzzeichen bleiben stehen.
4. Gibt es einen identischen neutralisierten Satzrest, gewinnt das Paar mit
   dem größten Produkt seiner T- und R-Trägerzahlen, dann der größten Summe,
   dann der kürzesten Gesamtlänge. Gibt es keinen, stehen die beiden
   beobachteten Einzelddefaults unverändert nebeneinander.
5. Die ersten Karten heißen `RESTGLEICH`; die übrigen `OWNER-VARIANTE`. Eine
   Owner-Variante darf nicht in einen neuen künstlichen Einheitssatz
   normalisiert werden.

## Decision rule and claim ceiling

Jede R-Phrase und beide Seiten jeder Kontrastkarte müssen wortwörtlich in den
alten GDT416/GDT490-Artefakten vorkommen. `RESTGLEICH` gilt nur bei exakt
identischem Aktions-neutralem deutschen Satz. Der formale Komponentenrest ist
in allen elf GDT428-Rahmen unverändert.

Das Ergebnis ist ein konkretes Arbeitsübersetzungs-Lexikon der bestehenden
Werkstattparaphrasen. Es bestätigt keine historische Sprache oder Lexeme und
ändert keine Bedeutung, Formulierung, Modellfolge, Grenze, Oberfläche,
Rezeptfolge, Event- oder Seitenzuordnung.
