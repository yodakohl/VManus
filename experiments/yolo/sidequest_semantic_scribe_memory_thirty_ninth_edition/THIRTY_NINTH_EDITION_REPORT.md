# Neununddreißigste Ausgabe: das Arbeitsgedächtnis des Schreibers

Diese Runde macht die Ellipse praktisch ausführbar. Der Schreiber führt vier
kleine recordlokale Werte: sichtbarer Besitzer, aktiver Arbeitsposten,
gegenwärtige Zielstelle und unmittelbar voriger Posten. Er muss nicht die
gesamte ausgeschriebene Lesung memorieren.

Die 116-Aussagen-Tabelle verbindet den heutigen Bildbesitzer, die aktuelle
Atomlesung und das Prozessmakro mit dem jeweiligen Zustand vor und nach jeder
Aussage. Die 26-Schritt-Tabelle führt dasselbe Gedächtnis durch den vollständig
ausgearbeiteten D2-Auftrag.

Die entscheidende Werkstattregel lautet: Ein Zeilenende setzt nichts zurück,
und ein Zellschluss löscht die Merktafel nicht automatisch. Ein sichtbarer
Stationswechsel ersetzt den Besitzer und zwingt den Schreiber, die Zielstelle
neu zu prüfen. Erst ein echter neuer Posten verschiebt ACTIVE nach PREVIOUS.

Dadurch werden lange Ergänzungen wie „daraus“, „dorthin“, „denselben Posten“
oder „mit dem Vorigen“ nicht mehr als überladene Wortbedeutungen behandelt.
Sie entstehen aus einer kurzen Karte plus dem gerade geführten Registerwert.

Artefakte:

- `THIRTY_NINTH_FOUR_MEMORY_SLOTS.tsv`;
- `THIRTY_NINTH_116_MEMORY_TRANSITIONS.tsv`;
- `THIRTY_NINTH_26_WORKED_JOB_MEMORY_TRACE.tsv`;
- `THIRTY_NINTH_SCRIBE_MEMORY_MANUAL.md`;
- Builder, Build-Summary und Konsistenzprüfung.
