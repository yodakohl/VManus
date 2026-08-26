# GDT488 — HALTEN geschlossen, EINSTELLEN kapazitätsbegrenzt

Status: `HALTEN_CYCLE_CLOSED__EINSTELLEN_REMAINS_CAPACITY_LIMITED`

## Ergebnis

Die Register-only-Suche findet genau ein neues Endpunktpaar:

`G475-R035 ↔ G475-R129` hält Modell, Satzklasse, Eventform und die komplette
Wildcardfolge `SETZEN · * · {N1}` fest. Nur Register/Besitzerart und die
funktionale Komponente wechseln: `BAHN ↔ HALTEN`.

Da `BAHN ↔ ZIELORT` in GDT486 bereits zweimal wiederkehrt, ist der bisherige
Singleton `HALTEN ↔ ZIELORT` jetzt über einen zweiten Weg geschlossen:

`HALTEN → BAHN → ZIELORT`.

Die Eventprojektion liefert fünf exakte Endpunkt-Minimalpaare. Zwei sind die
bekannten GDT486-Paare; drei sind neu und liegen sämtlich innerhalb einer
Seite:

- `DANACH ↔ HALTEN` vor demselben `AUSGANG`;
- `HALTEN ↔ SETZEN` vor `AUSGANG · HIER`;
- `HALTEN ↔ SETZEN` vor `FORTSETZEN`.

Damit hat `HALTEN` neben dem alten `ZIELORT` drei zusätzliche konkrete
Kontrastnachbarn: `BAHN`, `DANACH` und `SETZEN`.

## EINSTELLEN

`EINSTELLEN` kommt lokal zweimal vor, auf f72r als `CH+T` und auf f88v als
`CH+T+Y`. Beide Lesungen zeigen ausdrücklich „einstellen“. Der kürzere Träger
passt exakt in GDT428s `CH+@ACTION`-Rahmen, in dem T und R je einen Träger
besitzen; der längere liefert die bekannte GDT486-Kante `EINSTELLEN ↔ HIER`.

Keine der beiden einmaligen Lockerungen erzeugt einen zweiten lokalen
EINSTELLEN-Kontrast. Der Wert bleibt deshalb als kapazitätsbegrenzter Endpunkt
stehen. Das ist keine Umdeutung: zwei lokale Träger und elf exakte externe
T/R-Rahmen bleiben erhalten.

Der deterministische Validator besteht 93 von 93 Prüfungen. Keine Bedeutung,
Modellfolge, Grenze, Oberfläche, Rezeptfolge, Event- oder Seitenzuordnung
ändert sich.

## Nächster sinnvoller Schritt

`HALTEN` braucht keine weitere Lockerung. Für `EINSTELLEN` sollte nun das
Kompositionsumfeld statt des Ersatzgraphen genutzt werden: die elf GDT428-T/R-
Rahmen nach stabilen Nachbarn wie `WERT`, `ANTEIL`, `ZIELORT`, `FORTSETZEN` und
`POSTEN` ordnen und ihre Teilrahmen in den festen 183 Events suchen.
