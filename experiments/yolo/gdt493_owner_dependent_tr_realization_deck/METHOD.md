# GDT493 — Methode

## Question

Welche konkrete owner-abhängige Arbeitslesung ergibt sich für jeden der elf
T/R-Rahmen, beide Aktionen und alle fünf Register? Welche Zellen sind bereits
als ganze Klausel beobachtet und welche nur aus alten Slots zusammengesetzt?

## Inputs

- GDT413: 46 Komponentenwerte, insbesondere `E=GRAD I`;
- GDT415: 95 beobachtete Kernwurzel×Register-Realisierungen;
- GDT416: 4.576 alte Imperativklauseln und der unveränderte Klauselrenderer;
- GDT428: elf exakte T/R-Ersatzrahmen;
- GDT492: abgeschlossene Owner-Slot-Route ohne undefinierte Werte.

## Method

1. Die elf Rahmen werden mit T und R instanziiert und in jedes der fünf
   Register projiziert: 11×2×5 = 110 Zellen.
2. Alle elf benötigten Werte T, R, AIIN, AIN, AL, Y, CH, E, CHD, OL und OR
   erhalten ihre alte Registerrealisierung aus GDT415 beziehungsweise GDT413.
   Jede Zelle behält die portable und owner-lokale Komponentenspur.
3. Existiert das exakte Rezept im Register in GDT416, heißt die Zelle
   `OBSERVED_CLAUSE`. Angezeigt wird die häufigste beobachtete Klausel; bei
   Gleichstand die kürzere, dann alphabetisch erste. Alle Varianten und
   Eventträger bleiben im Datensatz.
4. Fehlt das exakte Rezept×Register, heißt die Zelle `COMPOSED_WORKING`. Ihre
   Phrase erzeugt unverändert der alte GDT416-Renderer aus den alten
   Registerwerten. Die Karte bleibt sichtbar als Komposition markiert.
5. Vier Rahmen enthalten kein sichtbares Argument: `@ACTION`, `@ACTION+AL`,
   `@ACTION+OL`, `CH+@ACTION`. Nur für ihre zusammengesetzte Arbeitsausgabe
   dient `Y=POSTEN [wie zuvor]` als Default des aktiven Zustands. Beobachtete
   Klauseln überschreiben ihn stets mit ihrem tatsächlichen geerbten Argument.
6. Für jedes Rahmen×Register werden T und R direkt verglichen. Der formale Rest
   muss gleich und die ausgegebenen Phrasen müssen verschieden bleiben.

## Decision rule and claim ceiling

Eine Phrase darf nur `OBSERVED_CLAUSE` heißen, wenn mindestens ein exakter
GDT416-Eventträger im selben Rezept und Register existiert. Jede andere Ausgabe
trägt `COMPOSED_WORKING`; kein fehlender Slotwert darf erfunden werden.

Das Ergebnis ist ein vollständiges Arbeitslesungsdeck, keine bestätigte
Übersetzung. Es ändert keine alte Formulierung, Bedeutung, Modellfolge, Grenze,
Oberfläche, Rezeptfolge, Event- oder Seitenzuordnung.
