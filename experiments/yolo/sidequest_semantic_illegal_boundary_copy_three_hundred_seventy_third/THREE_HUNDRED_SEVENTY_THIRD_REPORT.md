# Pass 373 — Randkopie gegen echten Reset

Eine reine Identitätsregel würde beide Doppelränder read-once nennen und damit
den zweiten Produktionsfehler unsichtbar machen. Die vollständige Werkstattregel
prüft die Vorgängerkarte: ein Slotabfall vor der Doppelkarte sperrt die
Antizipation. So wird eine legale Kopie entfernt, eine illegale gelöscht und als
Fehler markiert; acht Quellkarten bleiben exakt.

Als nächstes wird diese Fehlerregel auf alle 46 realen Zeilenübergänge der sieben
Prosaseiten zurückgespielt, diesmal mit expliziter Vorgängerprüfung.
