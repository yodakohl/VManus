# Pass 1023 — 328 offene Klammern werden zu sechs Werkstattgriffen

## Was jetzt besser ist

Pass 1022 konnte jede Karte zerlegen, ließ aber bei 328 Fokusstellen zwei
mögliche Handlungsköpfe stehen. Diese Restfrage ist jetzt für die laufende
Werkstattfassung vollständig entschieden:

| Baustelle | Stellen | Auswahl |
|---|---:|---|
| gleicher Abstand zwischen zwei Köpfen | 120 | 119 links, 1 rechts (`L`) |
| Bildbesitzer oder Kopf der nächsten Karte | 146 | 127 kurz voraus, 19 Besitzer |
| `R` als Kopf oder Schwanz | 63 | 46 Kopf, 16 Schwanz, 1 innerer Kopf |

Eine Stelle gehört zugleich zur ersten und dritten Gruppe. Deshalb sind es
329 Entscheidungszeilen, aber **328 verschiedene Anschlüsse**. Alle haben nun
eine ausführbare Arbeitslesung. 143 Anschlüsse ändern sich gegenüber dem
vorläufigen Pass-1022-Default; die übrigen 185 erhalten nur eine jetzt
begründete eindeutige Klammer.

Kein Kernwert wurde verändert und keine neue Seite wurde dafür gebraucht.

## Die wichtigste Selbstkorrektur

Die erste verführerische Kurzregel lautete: „Alles außer `L/AIR` hängt links.“
Das wäre zu grob und scheitert im Vollinventar viermal klar:

- `SH+O+Y+T+Y`: das mittlere `Y` gehört zum näheren `T`, nicht zum `SH`;
- `OK+O+E+S`: `E` gehört zum näheren `S`, nicht zum `OK`;
- `S+OR+AIIN+R`: `AIIN` gehört zum näheren `R`, nicht zum `S`;
- `CH+O+E+R`: `E` gehört zum näheren `R`, nicht zum `CH`.

Die haltbare Regel ist kleiner:

> Argument und Grad nehmen den nächsten Kopf; nur bei Gleichstand gewinnt
> links. `AL/AR` bevorzugen links beziehungsweise den offenen Besitzer.
> `L/AIR` bevorzugen rechts und fallen nur ohne rechten Kopf zurück.

Auf allen 4.345 Fokusanschlüssen stimmt diese örtliche Regel in 3.100/3.100
direkt prüfbaren Fällen. 1.245 kopflose Fälle sind keine Gegenbeispiele,
sondern brauchen den Besitzer-/Paketstapel.

Das ist genau die Art von Reparatur, die wir für spätere Seiten brauchen: nicht
eine neue Bedeutung erfinden, sondern eine zu breite Schreibregel rechtzeitig
enger machen.

## Griff 1 — Gleichstand schließt links

Bei `A + X + B` gehört `X` zum bereits geöffneten linken Kopf, wenn beide
Köpfe gleich weit entfernt sind. Der rechte Kopf beginnt danach sein inneres
Paket:

```text
CH + E + T + E + Y
→ CH[GRAD I; T[GRAD I; AKTIVER POSTEN]]

T + OR + SH + OR
→ T[EINHEIT; SH[EINHEIT]]
```

Der einzige Rechtsfall ist `CH+L+CH+P+SH+EE+Y`, weil `L=VERBINDUNG` absichtlich
den folgenden Kopf rahmt. `AIR=LAUF` verhält sich ebenso, kommt aber unter den
120 Gleichständen nicht vor.

## Griff 2 — höchstens eine Karte voraus

Beginnt ein Paket mit Posten, Wert, Anteil, Einheit oder Grad und besitzt noch
keinen Handlungskopf, darf der Lehrling genau bis zum ersten Kopf der
unmittelbar nächsten Karte vorausgreifen. Das funktioniert 127-mal.

Alle 127 Ziele liegen eine Karte entfernt. Kein Fall überschreitet einen
Besitzer- oder Proseblockwechsel; 22 überschreiten nur einen physischen
Locus-/Zeilenknick. Ein solcher Knick schließt also weiterhin nichts.

`Q`, `OT`, `L` und `AIR` lizenzieren den Rechtsgriff ausdrücklich. Ein `DY`
auf der Zielkarte schließt erst, nachdem deren Kopf die vorausgehenden Zusätze
aufgenommen hat.

## Griff 3 — `AR/AL` können am Bildbesitzer hängen

Die 19 Gegenfälle sind genau nackte `AR/AL`-Adressen ohne linken oder
geerbten Kopf und ohne `Q/OT/L/AIR` als Rechtsrahmen. Sie bleiben beim
sichtbaren Besitzer.

Das lässt sich sogar innerhalb einer Karte sehen:

```text
D_ADDR + AR + OR  |  Y + K + AR
```

Hier bleibt `AR=AUSGANG` am Bildbesitzer, während `OR=EINHEIT` zum folgenden
`K=GEBEN` greift. Man darf also nie die ganze Karte pauschal nach rechts
ziehen; ihre Bestandteile bilden ein Paket.

## Griff 4 — `R` bleibt MARKIEREN, ändert aber seine Stellung

`R` braucht keinen zweiten Sinn. Seine Paketposition genügt:

- erster Kopf mit rechtem Glied: `R` eröffnet `MARKIEREN[...]`;
- alleinige `R`-Karte vor einem kurzen Glied: ebenfalls Kopf;
- nach einer äußeren Handlung und ohne eigenes rechtes Glied: Schwanz, der
  den äußeren Gang markiert;
- zwischen äußerem Kopf und eigenem Rechtsglied: innerer Kopf.

Beispiele:

```text
R + AIIN        → MARKIEREN[WERT]
CH + O + E + R  |  AIIN
                → NEHMEN[AUSFÜHRUNG; GRAD I; MARKIEREN]; WERT bleibt bei NEHMEN
P + HIER + R + AIR + DY
                → EINSETZEN[MARKIEREN[LAUF]]; SCHLUSS
```

Damit wechseln 16 zuvor an `R` gehängte Zusätze zurück zum äußeren Kopf. Das
ist eine Scope-Korrektur, keine Umdeutung von `R`.

## Die sechs Griffe auf einer späteren Seite

1. Längstes Kartenpaket und Pass-1021-Doppelung zuerst öffnen.
2. Argument/Grad an den nächsten Kopf; bei Gleichstand links.
3. `AL/AR` links oder beim Besitzer; `L/AIR` rechts, sonst Rückfall.
4. Kopflose Pakete höchstens eine Karte im selben Besitzersegment vorauslesen.
5. `Q` pusht, `OT` wechselt Geschwister, `OL` führt fort,
   `VORBEZUG` restauriert und lizenziertes `DY` schließt.
6. `R` nach seiner Kopf-/Schwanzposition behandeln.

Diese Fassung macht eine klare Vorhersage für die nächste freigegebene Seite:
Sie darf neue lokale Bildnamen und neue gelernte Ganzkarten besitzen, aber sie
darf für bekannte Kerne weder einen zweiten Wortsinn noch einen Vorgriff über
mehrere Karten oder über eine echte Besitzergrenze verlangen.

## Woran die Fassung auf einer neuen Seite scheitern würde

- bekannte Argumente brauchen regelmäßig mehr als eine Karte Vorgriff;
- `AR/AL` müssen ohne Rahmen systematisch an einen rechten Kopf statt an den
  Besitzer;
- `L/AIR` müssen trotz vorhandenem rechten Kopf systematisch links hängen;
- `R` verlangt eine vierte, nicht positionsabhängige Funktion;
- eine echte Bild-/Proseblockgrenze wird von der Klammerung überlaufen;
- ein bekannter Kern braucht für eine lesbare Passage eine neue Bedeutung.

Dann wird nicht die Seite passend gemacht; dann ist die betreffende
Werkstattregel falsch.

## Dateien

- `PASS1023_CURRENT_SCOPE_SHEET.md` — kompakte selbständige Lehrlingsfassung
- `PASS1023_SIX_SCOPE_RULES.tsv` — die sechs Griffe
- `PASS1023_328_RESOLVED_ATTACHMENTS.tsv` — jede ehemalige Alternative
- `PASS1023_4345_SCOPE_ATTACHMENTS.tsv` — das vollständige Anschlussinventar
- `PASS1023_627_STATEMENT_SCOPE_EDITION.tsv` — alle Aussagen mit Auswahlspur
- `EQUAL_DISTANCE_GENERALIZATION_AUDIT.tsv` — Vollcheck der engen Regel
- `EQUAL_DISTANCE_*`, `OWNER_NEXT_*`, `R_HEAD_TAIL_*` — drei Einzelarbeiten
- `build_pass1023.py`, `validate_pass1023.py` — Neubau und Konsistenzprüfung
