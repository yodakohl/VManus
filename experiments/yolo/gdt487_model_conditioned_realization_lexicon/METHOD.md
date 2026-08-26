# GDT487 — Methode

## Question

Welche deutschen Formen nehmen die dreizehn funktionalen Komponentenwerte in
den drei aktiven Modellen tatsächlich an, und lassen sich die sechzehn nur
einmal beobachteten GDT486-Kontrastregeln über andere Kontrastwege anbinden?

## Inputs

- GDT486: 48 gleiche-Register-Minimalpaare, 29 modellgebundene
  Kontrastregeln und 135 Satzrahmenzuweisungen;
- GDT428: sechs Aktionskontraste innerhalb derselben Strukturklasse;
- GDT429: dreizehn Nichtaktionskontraste innerhalb derselben Strukturklasse.

## Method

1. Aus beiden Seiten jedes GDT486-Paars wird der dort schon formulierte
   deutsche Ausdruck des wechselnden Komponentenwerts entnommen. Ein Ausdruck
   bleibt an Record, Seite, Register, Modell und Satzrahmen gebunden.
2. Gleiche Ausdrücke werden pro Wert und aktivem Modell konsolidiert. Für jeden
   der dreizehn Werte entstehen genau drei Modellzellen: `CATALOGUE`,
   `COORDINATE` und `INSTRUCTION`.
3. Eine Zelle ohne Zeugen wird `OPEN`. Sie erhält weder eine erschlossene noch
   eine analog gebildete deutsche Form.
4. Die zwölf exakt wiederkehrenden GDT486-Regeln und die eine kontextuell
   erklärte wiederkehrende Regel bilden ein ungerichtetes lokales Netz.
5. Für jede der sechzehn Einzelregeln wird die direkte Kante vorübergehend
   entfernt. Existiert danach ein Weg zwischen ihren Endpunkten, ist die Regel
   lokal zyklisch trianguliert.
6. Für einen noch isolierten Wert werden nur bereits vorhandene GDT428- oder
   GDT429-Kontrastanker zugelassen. Ein externer Anker kann einen vollständigen
   Weg in das lokale Netz schließen oder lediglich einen Endpunkt anbinden.
7. Die Seitentabelle berichtet ausschließlich vorhandene Kapazität; Seiten
   ohne isolierte Form werden nicht als Gegenbeleg gewertet.

## Decision rule and claim ceiling

Eine beobachtete Realisierungsform muss wörtlich in mindestens einer
GDT486-Lesung vorkommen. `OPEN` bedeutet nur fehlende Isolationskapazität. Eine
Einzelregel ist vollständig trianguliert, wenn ein zweiter Weg beide
Komponentenwerte verbindet; ein externer Endpunktanker wird gesondert und
nicht als geschlossener Zyklus ausgewiesen.

Das Ergebnis ist ein Redaktions- und Vorhersagelexikon innerhalb der festen
Arbeitstheorie. Es bestätigt die Bedeutungen nicht unabhängig und darf keine
Wurzel, Bedeutung, Modellfolge, Recordgrenze, Oberfläche, Rezeptfolge, Event-
oder Seitenzuordnung ändern.
