# Pass 798 — der Transferautomat der Werkstatt

Die sechs neuen Operationskarten wurden in vollständige Sätze eingesetzt. In allen sechs bleibt das übrige Kartenende und jeder andere Satzbaustein fest; nur die Sachhandlung wechselt zwischen ZUGEBEN, LEITEN und UMSETZEN.

Die 14 wirklich gestapelten Karten ergeben einen sehr kleinen Automaten mit acht verständlichen Zuständen. Jede beginnt beim aktiven Posten:

- K führt zu MATERIAL_ADDED;
- L führt zu PATH_ENGAGED;
- CHD führt zu ITEM_TRANSFERRED;
- DY schließt danach den Schritt, AL legt ihn am Ziel ab, AR bindet ihn an die Quelle, Y hält ihn aktiv.

Die 14 Karten erzeugen 42 Übergänge. Zwölfmal steht L vor CHD: erst durch den angegebenen Lauf führen, dann in Empfänger oder neuen Zustand umsetzen. Einmal steht K vor CHD, einmal L vor K. Das ist eine konkrete, einem Lehrling erklärbare Prozessordnung und keine bloße Buchstabenzerlegung.

Beispiel `lchedy`: `ACTIVE_ITEM --LEITEN--> PATH_ENGAGED --UMSETZEN--> ITEM_TRANSFERRED --CLOSE--> STEP_CLOSED`. `lchedal` endet stattdessen an der owner-lokalen Zielstelle; `lchedar` beginnt semantisch an der owner-lokalen Quelle.

Als nächstes erstellen wir eine konsolidierte zweite Werkstattgrammatik: produktive Kerne, zugelassene Slots, bekannte Ganzkarten und alle bisher erzeugten, aber nicht belegten Prognosen werden in einer einzigen kurzen Lehrtafel zusammengeführt. Danach prüfen wir die 381 Ereignisse erneut auf eindeutige Zerlegung.
