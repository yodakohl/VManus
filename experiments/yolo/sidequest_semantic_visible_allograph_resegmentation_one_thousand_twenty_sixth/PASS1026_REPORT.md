# Pass 1026 — Die alten Ein-Zeichen-„Allographe“ zerlegt

## Der Fehler war größer als die zwei Wörter aus Pass 1025

Pass 1008 hatte für eine neue Oberfläche im Abstand eins das komplette Rezept
des ähnlichsten bekannten Wortes übernommen. Das war schnell, aber als
Kompositionsregel falsch: **ein Zeichen Unterschied wurde automatisch zu null
Bedeutungsunterschied erklärt.**

Der vollständige Rückgang über alle damaligen Fälle ergibt:

| Entscheidung | Ereignisse | verschiedene Oberflächen |
|---|---:|---:|
| sichtbare Änderung verlangt ein neues Komponentenrezept | 239 | 203 |
| eng lizenzierte Schreib-/Paketform behält das Rezept | 23 | 21 |
| schon in Pass 1025 repariert (`cheo`, `okeor`) | 9 | 2 |
| **gesamt** | **271** | **226** |

Damit waren nicht 271 echte Allographe gefunden worden. Es waren überwiegend
neue sichtbare Kompositionen, die durch die damalige Nachbarsuche flachgedrückt
wurden.

## Was jetzt als echte Schreibform übrigbleibt

Ein Rezept darf unverändert bleiben, wenn die Form in eine bereits gelehrte
Verpackung fällt:

- `q` vor einer vollständigen OK-/OT-/OL-/OR-Karte ist ein Schreiberrahmen;
- `chd` und `ched` sind die kurze und ausgezogene CHD-Schreibung;
- `chk` und `chek` können denselben linearen CH+K-Kopf schreiben;
- `os/oes` bleibt dieselbe lokale VORBEZUG-Karte;
- initiales `d` kann AL/OL/AIN/AIIN umhüllen;
- sichtbares `dy` bleibt bei ausdrücklich offenen Karten eine Y-Verpackung;
  nur die lizenzierte Endkarte ist SCHLUSS.

Alles andere wird wieder sichtbar gelesen. Ein zusätzliches `y`, `l`, `o`,
`s`, `p`, `t`, `k` oder ein zusätzlicher Grad darf nicht mehr verschwinden,
nur weil ein Nachbarwort ähnlich aussieht.

## Konkrete Reparaturen

| Oberfläche | alte Übernahme | neue sichtbare Lesung |
|---|---|---|
| `aiiny` | `AIIN` | `AIIN+Y` — WERT + AKTIVER POSTEN |
| `olain` | `OL+AIIN` | `OL+AIN` — FORTSETZEN + ANTEIL |
| `otees` | `OT+EE+Y` | `OT+EE+S` — DANACH + GRAD II + WÄHLEN |
| `chokaiin` | `SH+OK+AIIN` | `OK+AIIN` — SETZEN + WERT |
| `chekaiin` | `CH+K+EE+K+AIIN` | `CH+K+AIIN` — NEHMEN + GEBEN + WERT |
| `qokas` | `OK+AL` | `OK+A_ADDR+S` — SETZEN + HIER + WÄHLEN |
| `teo` | `E+OL` | `T+E+O` — EINSTELLEN + GRAD I + AUSFÜHRUNG |
| `cheo` | zwei geliehene Schwänze | `CH+E+O` |
| `okeor` | kein Grad oder Grad II | `OK+E+OR` |

Die Korrektur ändert 239 der 3.888 laufenden Ereignisse und 96 der 627
Aussagen. Sie liegt vollständig auf den vier Seiten, auf denen Pass 1008 den
Ein-Edit-Abkürzungsweg benutzt hatte: f18r 21, f72r 77, f76r 74 und f89r 67
Ereignisse.

## Was sich im kleinen Blatt verschiebt

Kein deutscher Kernwert wird umbenannt. Die sichtbaren Karten enthalten aber
mehr von den bereits vorhandenen Atomen:

- `E` +35, `O` +25, `S` +15, `L` +14;
- `Y` +6, `SH` +7, `P` +5, `D_ADDR` +4;
- die fälschlich mitkopierten `EE` sinken um 18 und `DY` um 8;
- `AIIN` sinkt um 7, weil einige Formen sichtbar zu AIN/IIN oder lokalen
  Varianten wechseln.

Das ist genau die gewünschte Art von Fortschritt: nicht neue Wörter erfinden,
sondern die schon behauptete Komposition endlich an der sichtbaren Form
festmachen.

## Neue harte Werkstattregel

> **Ein Edit ist kein Allograph.** Erst eine benannte Verpackungsregel darf
> eine Zeichenänderung semantisch neutral machen. Ohne solche Regel wird die
> Oberfläche neu zerlegt; das Rezept des Nachbarwortes darf nicht kopiert
> werden.

Diese Regel ist für kommende Seiten viel nützlicher als Levenshtein-Nähe. Sie
sagt vorher, wann `e/ee/eee`, `ain/aiin`, `y/s/o`, `l/r` oder ein zusätzlicher
Handlungskopf wirklich eine andere Karte bilden.

## Grenze und nächster Schritt

Die neuen Rezepte sind die kreative Arbeitsfassung des 19+8+4-Blatts, keine
entzifferten Wörter. Lokale Zeichen bleiben HIER, VARIANTE, KLASSE oder
VORBEZUG. Einige seltene Pakete sind weiterhin Werkstattentscheidungen und
keine sprachhistorisch bestätigten Morpheme.

Pass 1025 darf nach dieser Reparatur nicht einfach als letzte Zahlenbasis
weiterlaufen: 239 Ereignisse und damit ihre Scope-Anschlüsse haben sich
geändert. Der nächste sinnvolle Durchgang ist deshalb ein vollständiger neuer
627-Aussagen-/Scope-Replay auf dieser korrigierten Kartenfolge. Erst danach ist
das Blatt wieder bereit für vier wirklich neue Seiten.

## Dateien

- `PASS1026_271_ONE_EDIT_EVENT_AUDIT.tsv` — jeder alte Ein-Edit-Fall;
- `PASS1026_226_SURFACE_RESEGMENTATION.tsv` — eine Entscheidung je Oberfläche;
- `PASS1026_EDIT_RULE_COUNTS.tsv` — Verpackungs- und Änderungsregeln;
- `PASS1026_3888_CORRECTED_EVENT_LEDGER.tsv` — vollständige neue Lauftextbasis;
- `PASS1026_AFFECTED_STATEMENTS.tsv` — alle 96 betroffenen Aussagen;
- `build_pass1026.py`, `validate_pass1026.py`, Summary und Validation.
