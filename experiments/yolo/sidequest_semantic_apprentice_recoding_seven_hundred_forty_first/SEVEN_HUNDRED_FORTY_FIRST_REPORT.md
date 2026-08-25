# Pass 741 — der Lehrling schreibt zurueck

Der Lehrling erhielt nur Bildbesitzer, die bereinigte deutsche Werkstattanweisung und 39 kurze Bedeutungsstichwoerter. Die Voynich-Oberflaeche, Karten-ID und beobachtete Komponentenfolge gingen nicht in die Rekodierung ein.

## Was schon funktioniert

- In 93/116 Aussagen wird die **gesamte Komponentenmenge** exakt wiedergefunden.
- Mittlere Komponenten-Recall: 0.994; mittlere Precision: 0.977.
- Alle Aussagen erreichen mindestens 0.70 Recall.
- Das grobe Satzmuster wird in 89/116 Aussagen wiedergefunden.

Damit ist unser 39-Eintraege-System nicht bloss rueckwaerts lesbar: Aus einer normalen Werkstattanweisung bekommt ein Schreiber fast immer die richtigen Bedeutungsfamilien zurueck.

## Wo die echte Codebuchschicht sitzt

27 Satzmuster weichen ab. Davon sind 25 besonders aufschlussreich: Im Deutschen steht die Adresse oft vorn (`nach Sollmass ansetzen`, `an der Zielstelle ansetzen`), die Voynich-Karte packt aber den **Handlungskopf zuerst** (`OK+AIIN`, `OK+AL`). Weitere zwei Aussagen sprechen im Deutschen ein `halten` aus, obwohl die Karte diese Handlung elliptisch vom laufenden Kontext erbt.

Die verbleibende Huerde ist daher nicht mehr die Bedeutung der 39 Familien, sondern **Kartenpackung**:

1. Wann wird Handlung+Adresse zu einer einzigen handlungskopfigen Karte?
2. Wann bleibt die Adresse als eigene Kopfkarte davor stehen?
3. Wann darf ein Hilfsverb in der fluessigen Lesung erscheinen, ohne eine eigene Karte zu erhalten?

## Konkrete Fehler

Nur sechs beobachtete Komponenten werden ueber alle 116 Aussagen hinweg verschwiegen: O zweimal sowie OS,Y,T,AIN und OT je einmal. Dagegen entstehen 21 zusaetzliche Lesetreffer, vor allem elfmal SH, weil deutsche Wendungen wie `bereitet halten` oder `an der Sammelstelle halten` grammatisch `halten` brauchen, ohne immer eine eigene SH-Karte zu besitzen.

## Nächster Hebel

Baue nun einen kleinen **Kartenpacker**: Er nimmt die rekodierten Bedeutungsfamilien, bevorzugt attestierte Mehrkomponenten-Karten aus dem 173er Deck und entscheidet zwischen Handlungskopf und separatem Adresskopf. Keine neue Bedeutung wird eingefuehrt; gesucht wird nur die historische Mischung aus produktiver Kurzkomposition und gelernter Ganzkarte.
