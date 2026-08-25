# Pass 970 — der ausführbare Werkstattcompiler

Das System kann nun in beide Richtungen benutzt werden:

1. **Lesen:** Jede der 1.078 beobachteten Oberflächen führt eindeutig zu einer
   Komponentenfolge und einer portablen Kernbedeutung.
2. **Schreiben:** Jede der 948 beobachteten Komponentenfolgen besitzt eine
   häufigste Defaultoberfläche und eine Liste erlaubter Allographen.
3. **Rücklesen:** Defaultoberfläche und jede gelistete Variante führen wieder
   exakt zur ursprünglichen Komponentenfolge.

Beispiele:

- `Diesen Posten setzen` → `OK+Y` → `qoky` → `SETZEN · DIES`.
- `Eine Einheit setzen` → `OK+AIN` → `qokain` → `SETZEN · EINHEIT`.
- `kurz setzen; schließen` → `OK+E+DY` → `qokedy`.
- `länger setzen; schließen` → `OK+EE+DY` → `qokeedy`.
- `Posten umsetzen` → `CHD+Y` → `chedy`.
- `Ziel auswählen` → `S+AL` → `sal`.

Der Compiler erfindet keine unbekannte Oberfläche. Wenn eine gewünschte
Stammfolge unter den 948 beobachteten Rezepten fehlt, meldet er `UNSEEN_RECIPE`
und verlangt die Form aus dem Meisterexemplar. Das hält die kreative Theorie
schreibbar, ohne beliebige Voynich-ähnliche Wörter zu produzieren.
