# Pass 1025 — Vier ganze Register auf einmal

## Der Test stoppte zuerst an einem echten Fehler

Der geplante Register-Replay begann mit einer einfachen Forderung:

> Dieselbe sichtbare Lauftextoberfläche muss dieselbe sichtbare
> Komponentenfolge haben. Eine lokale Bild-/Ringadresse bleibt ihr eigener
> Namensraum.

Die bisherige Ausgabe verletzte das bei genau zwei Oberflächen:

```text
cheo   → CH+E+O+R  auf f72r
       → CH+E+O+L  auf f76r/f89r

okeor  → OK+OR     auf f18r
       → OK+EE+OR  auf f72r/f76r
```

Das war kein tiefer Manuskriptmechanismus, sondern ein alter Fehler unserer
Ein-Edit-Zuordnung. `cheo` war einmal an `cheor`, einmal an `cheol` angelehnt
worden; `okeor` einmal an `okor`, einmal an `okeeor`. Der ähnliche Nachbar
hatte dadurch unsichtbare Atome in die Übersetzung eingeschmuggelt.

Die Reparatur ist kleiner und besser vorhersagbar:

```text
cheo   = CH + E + O     NEHMEN · GRAD I · AUSFÜHRUNG
okeor  = OK + E + OR    SETZEN · GRAD I · EINHEIT
```

Damit besitzen alle 3.888 Laufereignisse wieder die Regel **eine sichtbare
Lauftextoberfläche → eine Komponentenfolge**. Neun Ereignisse in acht Aussagen ändern
sich. Vier unsichtbare L-Anschlüsse fallen weg, zwei EE werden zu E, ein
sichtbares E kommt hinzu und zwei nachfolgende Werte brauchen keinen
unsichtbaren R-Vermittler mehr. Das Fokusinventar sinkt dadurch von 4.345 auf
4.342 echte Anschlüsse.

Das ist die wichtigste Erkenntnis dieser Runde. Ein Allograph darf eine
Schreiberverwandtschaft anzeigen; er darf niemals ein auf der Karte fehlendes
semantisches Atom importieren.

## Danach: Ein ganzes Register als neue Welt

Nach der Korrektur wurde nacheinander das komplette Herbal-, Biological-,
Celestial- und Pharma-Register aus seiner eigenen Lehrbasis entfernt. Die
Frage war härter als in Pass 1024:

- Kommt jede auf dem ausgelassenen Register benutzte Kategorie auch außerhalb
  dieses Registers vor?
- Kommt jede dort benutzte grobe Scope-Regel außerhalb vor?
- Wie viele ganze Oberflächen und Komponentenfolgen kann ein Schreiber aus den
  anderen drei Registern bereits kennen?

## Ergebnis

**Alle vier Register behalten das feste Blatt und dieselben neun groben
Scope-Regeln.** Kein benutzter Kern, keine Steuerung und keine Regel ist nur im
jeweils ausgelassenen Register verfügbar.

| ausgelassenes Register | Ereignisse | exakte Fremdoberfläche | bekannte Fremdrezeptur | neue Rezeptur, alte Atome |
|---|---:|---:|---:|---:|
| Herbal | 601 | 332 | 101 | 168 |
| Biological | 2.161 | 1.241 | 292 | 628 |
| Celestial | 523 | 295 | 96 | 132 |
| Pharma | 603 | 393 | 105 | 105 |
| **gesamt** | **3.888** | **2.261** | **594** | **1.033** |

Damit kommen 58,2 % der Laufkarten als exakte Oberfläche in einem anderen
Register vor. Weitere 15,3 % benutzen dort bereits dieselbe Komponentenfolge.
Bei 26,6 % ist selbst die ganze Rezeptur registerprivat — aber jedes Atom ist
bekannt und behält seinen Wert.

Die starke Aussage ist daher nicht „alle Wörter wiederholen sich“. Sie lautet:

> Ein Viertel der Karten darf registerneue Kompositionen bilden, ohne das
> 19-Kern-Wörterbuch oder die Klammermaschine zu erweitern.

## Die 31 Kategorien

Dreißig der 31 Lehrkategorien erscheinen in allen vier Registern. Nur
`VORBEZUG` ist schmaler: sieben Vorkommen auf Herbal und Celestial. Es fällt
trotzdem bei keinem benutzten Register-Holdout aus, weil sich diese beiden
Register gegenseitig lehren.

Alle neunzehn Bedeutungsanker stehen somit weiterhin in Herbal, Biological,
Celestial und Pharma:

```text
AKTIVER POSTEN · SETZEN · FORTSETZEN · DANACH · ZIELORT
NEHMEN · HALTEN · AUSGANG · GEBEN · WERT · WÄHLEN
UMSETZEN · EINHEIT · VERBINDUNG · EINSTELLEN · ANTEIL
MARKIEREN · EINSETZEN · LAUF
```

Das bestätigt noch nicht, dass die deutschen Wörter historisch richtig sind.
Es zeigt aber, dass keiner von ihnen nur durch eine einzige Bildgattung am
Leben gehalten wird.

## Die neun Scope-Familien

Acht Regelfamilien erscheinen in allen vier Registern. `OWNER_CONTEXT` fehlt
nur in Herbal, wird dort aber auch nicht gebraucht; Biological, Celestial und
Pharma lehren es gegenseitig. Die kleinsten universellen Familien bleiben
`Q/OT`-Vorgriff und positionsabhängiges R. Beide kommen trotz geringer Zahl in
allen vier Registern vor.

Die vier schon aus Pass 1024 bekannten privaten Mikroformen bleiben lokal:

```text
f18r  R_NESTED
f77r  EQUAL_RIGHT
f77r  AL_AR_RIGHT_FALLBACK_NO_LEFT
f82r  EQUAL_LEFT+R_HEAD
```

Ihre Elternregeln sind jedoch registerübergreifend. Keine davon verlangt ein
Herbal-, Bad-, Stern- oder Pharma-Sonderwort.

## Die acht korrigierten Aussagen

- f18r S019: `okeor` erhält den sichtbaren Grad I;
- f72r S056 und f76r S254: `okeor` fällt von Grad II auf Grad I;
- f72r S057: `cheo` verliert das unsichtbare MARKIEREN;
- f72r S067: `cheo` verliert MARKIEREN, nachfolgendes L/WERT hängt direkt am
  offenen NEHMEN-Kopf;
- f76r S244 und f89r S617: `cheo` verliert die unsichtbare VERBINDUNG;
- f89r S627: beide `cheo` verlieren die unsichtbare VERBINDUNG.

Die vollständigen Kartenfolgen vor und nach der Reparatur stehen in
`PASS1025_EIGHT_CORRECTED_STATEMENTS.tsv`.

## Was wir daraus für die nächsten Seiten lernen

Die nächste Seite darf sehr viele neue ganze Kompositionen besitzen. Das ist
nach dem Register-Holdout kein Alarm. Alarm ist jetzt präziser:

- dieselbe sichtbare Oberfläche braucht zwei Komponentenfolgen;
- ein bekannter Kern muss umbenannt werden;
- ein fehlendes Atom wird aus einem ähnlichen Wort ergänzt;
- eine neue grobe Scope-Regel oder ein Besitzergrenzsprung wird benötigt.

Pass 1025 ist weiterhin keine Entzifferung und kein echter Zukunftstreffer.
Aber er hat einen realen Fehler gefunden, ihn ohne Bedeutungsverschiebung
entfernt und danach die gesamte Maschine auf vier weit auseinanderliegende
Register gestellt. Das ist deutlich mehr wert als eine weitere schöne
Einzelübersetzung.

## Dateien

- `PASS1025_3888_REGISTER_EVENT_REPLAY.tsv` — jede Karte gegen drei andere
  Register;
- `PASS1025_4342_CORRECTED_ATTACHMENTS.tsv` — korrigiertes Scope-Inventar;
- `PASS1025_SURFACE_DETERMINISM_CORRECTIONS.tsv` — alle 18 Reparaturschritte;
- `PASS1025_EIGHT_CORRECTED_STATEMENTS.tsv` — vollständige betroffene Folgen;
- `PASS1025_31_CATEGORY_REGISTER_SUPPORT.tsv` — Kern-/Steuerungsstütze;
- `PASS1025_9_RULE_REGISTER_SUPPORT.tsv` — Scope-Stütze;
- `PASS1025_MICROFORM_REGISTER_SUPPORT.tsv` — feine Formen;
- `PASS1025_FOUR_REGISTER_REPLAY.tsv` — vier Gesamtbilanzen;
- Builder, Summary und Validator im selben Verzeichnis.
