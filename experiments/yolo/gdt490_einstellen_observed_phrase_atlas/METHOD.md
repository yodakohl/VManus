# GDT490 — Methode

## Question

Welche bereits vorhandenen deutschen GDT416-Klauseln realisieren die elf
T-seitigen GDT428-Rahmen, und lässt sich für jeden Rahmen ein beobachteter
Default auswählen, ohne einen Satz zu erfinden?

## Inputs

- GDT416: 4.576 owner-lokale Imperativklauseln mit exakter Rückprojektion;
- GDT428: 104 Aktionsersatzrahmen, davon elf T/R-Rahmen;
- GDT489: lokaler Kontext- und T-Kontaktstatus derselben elf Rahmen.

## Method

1. In jedem T/R-Rahmen wird `@ACTION` durch `T` ersetzt. Das resultierende
   Rezept wird exakt gegen die 4.576 GDT416-Klauseln gehalten.
2. Jeder Treffer behält Event, Aussage, Seite, Register, Besitzerklasse,
   Oberfläche, Schablone, Imperativklausel, owner-lokale Lesung, portable
   Rückprojektion und Roundtrip-Status.
3. Identische deutsche Klauseln werden nur innerhalb desselben Rahmens
   zusammengefasst. Besitzer- und Registervarianten bleiben getrennt
   nachvollziehbar.
4. Der Default pro Rahmen ist die beobachtete Klausel mit den meisten Trägern.
   Bei Gleichstand gewinnt die kürzere Klausel, dann die alphabetisch erste.
   Alle Alternativen bleiben neben dem Default erhalten.
5. Der GDT489-Status wird angefügt. Ein lokal fehlender Kontext darf durch
   bereits zugelassene T-Träger sprachlich ausgefüllt werden, bleibt aber als
   lokale Abwesenheit markiert.
6. Die fünf priorisierten Nachbarn WERT, ANTEIL, ZIELORT, FORTSETZEN und POSTEN
   müssen jeweils mindestens eine beobachtete T-Klausel besitzen.

## Decision rule and claim ceiling

Eine Satzform ist nur zulässig, wenn sie als vollständige
`imperative_clause_de` in GDT416 steht und `roundtrip_exact=YES` trägt. Der
Default darf keine Normalisierung oder Analogiebildung enthalten.

Das Ergebnis bleibt ein beobachtetes Satzlexikon der bestehenden
Werkstattparaphrase. Es bestätigt keine Sprache oder Lexeme und ändert keine
Bedeutung, Formulierung, Modellfolge, Grenze, Oberfläche, Rezeptfolge, Event-
oder Seitenzuordnung.
