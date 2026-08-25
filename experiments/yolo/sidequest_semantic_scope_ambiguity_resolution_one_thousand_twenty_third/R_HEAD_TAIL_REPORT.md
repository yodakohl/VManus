# Pass 1023 — R als Kopf, Schwanz oder innerer Kopf

## Ergebnis

Alle 63 offenen `R_HEAD_OR_TAIL`-Anschlüsse aus Pass 1022 sind entschieden.
Sie stammen von 42 verschiedenen R-Karten in 35 Aussagen.

| Entscheidung | R-Karten | Alternativzeilen | Lesung von `R=MARKIEREN` |
|---|---:|---:|---|
| `HEAD` | 32 | 46 | eröffnet einen eigenen Kopf |
| `TAIL` | 9 | 16 | markiert den bereits offenen äußeren Kopf |
| `NESTED` | 1 | 1 | eröffnet einen inneren Kopf im äußeren Kartenpaket |
| `UNRESOLVED` | 0 | 0 | — |

Sechzehn Pass-1022-Anschlüsse wechseln dadurch vom vorläufigen R-Kopf zurück
zum äußeren Kopf. Der Wurzelwert ändert sich nirgends: Auch als Schwanz heißt
`R` weiterhin **MARKIEREN**; es wird weder gelöscht noch zu einem neuen Wort.

## Die Lehrregel

Der Lehrling braucht vier Griffe:

1. **Links schon eine Handlung, rechts kein eigenes R-Glied:** `TAIL`.
   Kartenfinales `R` markiert den Handlungskopf links. Nachfolgende Karten
   bleiben bei diesem äußeren Kopf.
2. **Links schon eine Handlung, rechts vor jeder neuen Handlung ein eigenes
   Glied:** `NESTED`. Der linke Kopf bleibt außen, `R=MARKIEREN` regiert nur
   sein örtliches rechtes Glied.
3. **Links in der Karte noch keine Handlung:** `HEAD`, sobald rechts ein Glied
   folgt. Das Glied darf in derselben Karte stehen oder nach einer alleinigen
   R-Karte unmittelbar in der nächsten beginnen. `L+R` setzt R als ersten
   Kopf in den nach rechts geöffneten Verbindungsrahmen.
4. **Sonderform `R+OL` ohne eigenes Glied:** `TAIL`. `OL` führt ausdrücklich
   den vorher offenen Kopf fort und gibt R deshalb keinen neuen Gang.

Eine neue Handlung oder ein lizenziertes `DY` beendet die Reichweite. Die
Regel fragt nur nach Stellung, Paketgrenze und direkter Nachbarschaft.

## Was die harten Formen jetzt tun

- `DA+R+Y` und `R+AIIN/AIN/OR/AL/Y` sind `HEAD`: Das rechte Glied gehört zu
  MARKIEREN.
- `R | AIIN/AIN/OR/Y` ist ebenfalls `HEAD`: Die alleinige R-Karte eröffnet
  sichtbar den folgenden kurzen Argumentblock.
- `CH+E+O+R | AIIN/Y/L` ist `TAIL`: NEHMEN bleibt offen; R markiert diese
  Ausführung, und die nächste Karte hängt weiter an NEHMEN.
- `S+OR+AIIN+R | Y` und `S+O+DA+R | AR ...` sind `TAIL`: WÄHLEN bleibt der
  äußere Kopf.
- `P+D_ADDR+R+AIR+DY` ist der einzige `NESTED`-Fall:
  `EINSETZEN[MARKIEREN[LAUF]]`, danach schließt `DY`.
- `R+OL | L` ist `TAIL`: VERBINDUNG bleibt am fortgesetzten GEBEN-Gang.
- `R+AL+CH+E+Y` ist ein R-Kopf mit einem inneren CH-Paket. `AL` bindet an R,
  `Y` an CH; beide Köpfe behalten ihren vorhandenen Wert.

## Warum das einem Schreiber um 1420 vertraut wäre

Die Analogie ist die Stellung von Kürzeln, nicht eine Gleichsetzung des
Voynich-R mit einem lateinischen Zeichen.

- In medizinischen Rezepten steht das kurze `℞/R` für *Recipe* am
  **Eintragskopf** und trägt den Auftrag nach rechts über die Zutaten. Maßsigla
  und `ana` hängen dagegen an einer schon eröffneten Zutatenreihe. Diese
  beständige Arbeitsteilung der Rezeptkürzel ist für mehrere mittelalterliche
  Schreiber belegt ([Digital Scholarship in the Humanities](https://academic.oup.com/dsh/article/37/3/765/6401180)).
- Das nordostitalienische [Wellcome MS.683](https://wellcomecollection.org/works/w6ne7k4t)
  zeigt genau die räumliche Werkstattökonomie: Überschrift, einmaliges
  *Recipe*, Zutaten und Maßangabe stehen in verschiedenen Positionen; ein
  abschließendes *fiat* fasst die Reihe rückwärts zusammen. Dasselbe Manuskript
  besitzt auch Randnotizen und `nota`-Zeichen, die eine vorhandene Stelle
  markieren, ohne selbst einen neuen Rezeptkopf zu eröffnen.
- In zeitnahen Rechnungsrollen führen kurze Rückgriffe wie *idem*, *eodem* und
  *ut supra* einen offenen Eintrag weiter, statt ihn neu zu beginnen, etwa in
  den [Durhamer Rechnungsrollen](https://quod.lib.umich.edu/c/cme/CME00048/1%3A2?rgn=div1&view=fulltext).

Damit ist die Doppelverwendung lehrbar: **vorn mit rechtem Glied eröffnet das
Zeichen; hinten ohne eigenes Glied markiert es; zwischen äußerem Kopf und
rechtem Glied arbeitet es innen.**

## Dateien

- `R_HEAD_TAIL_63_ADJUDICATION.tsv` — alle 63 Entscheidungen mit R-Karte,
  Nachbarschaft, Paketform, Fokus und gewähltem Anschluss
- `R_HEAD_TAIL_COUNTS.json` — Karten- und Zeilenzahlen sowie Quellhashes
- `R_HEAD_TAIL_BUILD.py` — der kleine vollständige Neubau aus den drei
  Pass-1022-Primärtabellen
