# GDT441 method

## Question

Kann der laufende Leser eine vorher nicht katalogisierte Karte aus bekannten
Kernen lesen, ohne dafür ein neues Ganzwort zu erfinden?

## Inputs

- GDT434: 1.563 exakte Rezepte;
- GDT404/GDT425: acht Scope-Selectoren, 103 portable und vier lokale
  Fokusanschlüsse, 31 portable und sechs lokale Handlungspaare sowie neun
  Schlussträger;
- GDT437/GDT440: geordnete Kernfolge und flüssige zustandsabhängige Lesung;
- GDT430: 861 seitenprivate Rezepte und 4.938 Ein-Kern-Kandidaten als Belastung.

## Method

Für jede sichtbar gelieferte Karte gilt diese Reihenfolge:

1. Exakter Rezeptschlüssel vorhanden: bekannte Karte lesen.
2. Unbekanntes Atom vorhanden: stoppen.
3. Jeden Fokus mit dem unveränderten Acht-Selector-Parser an Kopf oder Besitzer
   binden. `AL/AR`, `L/AIR`, `R`, geerbter Kopf und höchstens eine Karte
   Vorgriff behalten ihre alten Sonderregeln.
4. Jede Fokus–Kopf-Kante prüfen. Seitenübergreifend belegt ist grün; eine der
   vier alten lokalen Kanten ist gelb; eine neue Kante stoppt.
5. Nur unmittelbar benachbarte Handlungskerne bilden ein Paar. Ein altes
   seitenübergreifendes Paar ist grün, eines der sechs lokalen Paare gelb, ein
   neues Paar stoppt.
6. `DY` darf nur den letzten sichtbaren oder im Arbeitszustand geerbten der
   neun bekannten Handlungsköpfe schließen.
7. Bei Grün/Gelb: exakte geordnete Kernlesung aus dem 46-Zeichen-Blatt und
   flüssige Lesung aus dem Besitzerzustand ausgeben. Bei Stopp: Zustand nicht
   verändern.

Der Scope-Zustand beginnt je Aussage neu. Der semantische Arbeitszustand bleibt
wie in GDT438 nach Seite und Besitzer getrennt. Dadurch darf eine reine
Schlusskarte den geerbten Handlungskopf schließen, ohne den Scope-Parser zu
verfälschen.

## Decision rule and claim ceiling

Eine neue Kombination wird nur **nach ihrem sichtbaren Auftreten** gelesen.
Grün heißt: alle Verbindungen sind seitenübergreifend alt. Gelb heißt: nur eine
bereits bekannte lokale Ausnahme wird wiederverwendet. Rot heißt: keine Lesung,
kein Zustandswechsel.

Das Verfahren ist absichtlich kein Oberflächen- oder Vorkommensgenerator. Dass
es 4.303 der 4.566 derzeit fehlenden Ein-Kern-Kandidaten formal akzeptiert,
zeigt gerade, dass der Faktorraum zum Vorhersagen zu breit ist.
