# GDT715 — V88 axis/action core–context repair

Status: `PASS_V88_7_AXIS_ACTION_READINGS_REVISED__2_VALUE_CORES_5_ACTION_CORES__7_TARGET_POSITIONS_7_PAGES__84_WEAK_READINGS_REMAIN__F7R2_RERENDERED__ALL_H0_NONE`

## Ergebnis

Die letzten sieben V87-Holds dieser Klasse haben jetzt einen engen
Woerterbuchkern und eine getrennte konkrete Fundstellenlesung:

| Form | Woerterbuchkern | konkrete Stelle | Confidence |
|---|---|---|---|
| `aiiin` | Wert IV | Menge IV | 36→39 (W1_WEAK_WORKING) |
| `ydaiin` | Bezugswert III | davon: Wert III | 28→31 (W1_WEAK_WORKING) |
| `dold` | abmessen und abschließen | diese Blüte abmessen und abschließen | 39→39 (W1_WEAK_WORKING) |
| `qckhedy` | bis zur Mittelstufe fertig aufbereiten | den vorstehenden Trockenposten bis zur Mittelstufe fertig aufbereiten | 36→36 (W1_WEAK_WORKING) |
| `qey` | anschließend nehmen | die vorstehende trockene Mittelstufenportion anschließend nehmen | 39→39 (W1_WEAK_WORKING) |
| `qochedain` | Trockenwert II auf Mittelstufe abmessen | hiervon die Trockenmenge II auf Mittelstufe abmessen | 39→39 (W1_WEAK_WORKING) |
| `yky` | leicht erhitzen | die heiße Portion auf Stufe III leicht nachwärmen | 35→35 (W1_WEAK_WORKING) |

Der entscheidende Gewinn ist nicht mehr Prosa, sondern Vorhersagbarkeit der
Komposition. `aiiin` liefert nur **Wert IV**; erst P052 waehlt **Menge IV**.
`ydaiin` liefert **Bezugswert III**; weder "drei" noch "Maße" bleiben im Kern.
Bei den fuenf Aktionen sitzt der Vorgang im Wort, waehrend der Patient aus der
explizit benannten linken Stelle kommt. So kann derselbe Aktionskern spaeter an
einem anderen Patienten getestet werden.

## f7r.2 wirklich neu gerendert

Der geerbte Einmal-Span bleibt aktiv:

```text
P288 keo + P289 r  ->  heiße Portion
```

P289 wird konsumiert und nicht separat ausgegeben. P291 verwendet nun den
reparierten DOLD-Kontext. Die acht tatsaechlichen Ausgabeeinheiten sind:

```text
eine Dosis vollständig trocknen und abschließen · heiße Portion · Blüte · diese Blüte abmessen und abschließen · fertige abgemessene Mittelstufen-Trockenportion · heiß-trocken, Mittelstufe · kalt-trockene Zubereitung am Anfang des Grades · getrocknete Masse
```

## Bestand

- 7 revidierte Lesungen an 7 Positionen auf 7 Seiten
- 2 Wertkerne, 5 Aktionskerne
- 19 exakt aufgeloeste Primaerevidenzbindungen
- Confidence-Aenderung nur bei `aiiin` und `ydaiin`, jeweils `F_N +3`
- aktive Stufen: `{"W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 7, "W1_WEAK_WORKING": 135, "W2_PROVISIONAL_WORKING": 163, "W3_SOLID_WORKING_THEORY": 19}`
- vollstaendiges Woerterbuch: 1586 Lesungen mit Score,
  Level, positiver Evidenz und Gegenbeleg in jeder Zeile
- verbleibende einzeln unbearbeitete schwache Lesungen: 84

## Grenze

Die konkreten Patienten sind bewusst als Fundstellenhypothesen markiert. Sie
werden nicht in den portablen Wortkern und nicht in freie Komponenten
exportiert. Das ist die beste aktuelle Arbeitsuebersetzung, keine bestaetigte
Klartextlesung; historische Bestaetigung bleibt `H0_NONE`.
