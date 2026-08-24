# Pass 374 — reale Zeilenübergänge korrigieren die neue Regel

Die Vorgängerregel aus Pass 373 scheitert genau am einzigen realen
Read-once-Fall. Vor E180 steht E179 `chckhy` im Transferslot; E180/E181
`qokaiin` steht im niedrigeren Maßslot und eröffnet einen neuen Mikrogang. Die
Karte wird trotzdem am alten Rand antizipiert und am neuen Anfang ausgeführt.

Darum wird "Slotabfall sperrt Randkopie" vollständig zurückgezogen. Die 46
realen Entscheidungen bleiben 6 Fortsetzungen,
1 Read-once und
39 Resets. Der synthetische
`aiin | aiin`-Fall aus Pass 373 ist intern strukturgleich und darf nicht mehr als
erkennbarer Fehler bezeichnet werden.

Als nächstes braucht die Werkstatt eine positive sichtbare Konvention, wenn sie
Fehler von Antizipation unterscheiden will: etwa ein Randpunkt, kleinerer
Abstand oder eine feste marginale Stellung. Auf den realen sieben Seiten wird
nichts davon erfunden; die neue Markierung wird nur an der Übungszeile getestet.
