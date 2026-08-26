# GDT455 — Methode

## Question

Bleiben Stopps, Besitzerbanken und anschließende echte Karten korrekt, wenn
nicht nur ein lokales Paar, sondern fast jede mehrgliedrige Aussage desselben
Stroms gleichzeitig eine Zwei-Karten-Störung trägt?

## Inputs

- GDT441: geordneter 4.576er Strom und wirkliche Zustände;
- GDT454: feste Ein-Schritt-Nachbarn;
- GDT451: endgültige Liveentscheidung.

## Method

`EMPTY_RECIPE` wird ausgeschlossen: eine vollständig gelöschte Einatomkarte ist
kein sinnvoller Stellvertreter für eine künftig sichtbare Karte. Für jedes
Quellrezept wird aus den übrigen GDT454-Nachbarn genau einer gewählt:

1. neutraler Stopp vor neutral lesbar;
2. Atomlöschung vor Nachbartausch vor Klassensubstitution;
3. danach Zielrezept und Nachbar-ID lexikographisch.

In jeder mehrgliedrigen Aussage wird das benachbarte Paar mit den meisten
neutralen Stoppkandidaten gewählt, bei Gleichstand das früheste. So erhalten
513/514 Aussagen einen Burst; nur `G404-S004` besitzt wegen der einatomigen
`OS`-Mittelkarte kein Paar aus zwei nichtleeren Nachbarn.

Der Treiber verwaltet getrennt Handlung und Argument je
`(physical_page, owner)`-Bank, den aktiven Handlungskopf je Aussage, genau eine
sichtbare nächste Karte innerhalb derselben Aussage und Bank sowie die
endgültige GDT451-Liveentscheidung. `READ` und `READ_AMBER` schreiben nur in die
aktive Bank. `STOP` bewahrt Bank und Satz-Scope unverändert.

Der unveränderte Strom muss zuerst alle 4.576 Entscheidungen und Zustände
reproduzieren. Danach wird der dichte Störplan global und jede der 57 Banken
isoliert gelesen. Für jeden Burst läuft die Prüfung bis zur Zustandsparität,
zum nächsten geplanten Fehler oder zum Ende seiner Bank.

## Decision rule and claim ceiling

Jeder Stopp muss Handlung, Argument und Scope bewahren; globale und isolierte
Bankläufe müssen Ereignis für Ereignis übereinstimmen. Der Test erzeugt keine
Voynich-Form, sagt kein Auftreten voraus und ändert keine Bedeutung.
