# GDT453 — Methode

## Question

Synchronisiert der Leser nach allen 765 aussageterminalen Stopps an der ersten
wirklich folgenden Karte, ohne den gestoppten Zustand in einen anderen Besitzer
oder auf eine andere Seite zu verschleppen?

## Inputs

- GDT452-Vorkommenstabelle;
- geordneter 4.576-Ereignis-Strom aus GDT441;
- integrierter GDT451-Aufnahmebefehl.

## Method

Jeder terminale Zielstopp wird erneut ausgeführt. Danach wird das unmittelbar
nächste globale Stromereignis klassifiziert:

- gleicher Besitzer, nächste Aussage: erhaltenen Stopzustand verwenden;
- neuer Besitzer auf derselben Seite: dessen eigene Bank verwenden;
- neue Seite: deren eigene Besitzerbank verwenden;
- Stromende: keine Recovery-Karte vorhanden.

Der Aussage-Scope wird an jeder Grenze auf `NONE` gesetzt. Für die Grenzkarte
wird wieder der wirkliche Ein-Karten-Ausblick benutzt. Ein fremder
Besitzerzustand darf nie aus dem Stopp übernommen werden.

## Decision rule and claim ceiling

Alle vorhandenen Grenzkarten müssen lesbar sein; jeder Besitzer-/Seitenwechsel
muss aus seiner unabhängigen Bank starten. Stromende ist kein Fehler.

Der Test prüft nur Recovery und Zustandsisolation. Er ändert keine Bedeutung,
Oberfläche oder Auftretensbehauptung.
