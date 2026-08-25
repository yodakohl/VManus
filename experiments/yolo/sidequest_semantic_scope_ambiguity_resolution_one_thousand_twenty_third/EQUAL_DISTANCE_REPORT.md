# Pass 1023 — Gleichabstand ohne Rätselwort

## Ergebnis

Alle 120 Gleichabstandsstellen sind mit einer einzigen kleinen Paketregel
entscheidbar:

```text
1. Eine Pass-1021-Doppelung zuerst als Paket oder freies Paar öffnen.
2. Innerhalb des geöffneten Pakets von links nach rechts lesen.
3. Ein Zusatz nach einem offenen Handlungskopf schließt an diesen linken Kopf,
   bevor ein späteres Handlungssymbol seinen neuen Innenrahmen eröffnet.
4. Nur L/AIR sind Vorwärtsrahmen und greifen auf den rechten Kopf.
```

Die geometrische Gleichnähe muss also nicht durch eine neue Bedeutung
aufgelöst werden. Entscheidend ist, ob der Kern den offenen Kopf schließt oder
selbst einen vorwärts gerichteten Rahmen eröffnet.

| Entscheidung | Stellen |
|---|---:|
| `LEFT` | 119 |
| `RIGHT` | 1 |
| `NESTED` | 0 |
| `UNRESOLVED` | 0 |
| **gesamt** | **120** |

`NESTED=0` heißt nicht, dass die Mehrkopfkarten flach wären. Die Karte bleibt
verschachtelt; lediglich der strittige Fokus selbst bildet in diesen 120
Stellen keine eigene äußere/innere Doppelstufe.

## Die Klammerformen

Gewöhnlicher Schluss nach links:

```text
A + X + B + ...  →  A[X; B[...]]
```

Vorwärtsrahmen:

```text
A + L/AIR + B + ...  →  A[(L/AIR → B)[...]]
```

Pass-1021-Paket, das stets vorher geöffnet würde:

```text
A + X + X + Z  →  A[X_außen[X_innen[Z]]]
```

Der dritte Fall erhält die Entscheidung `NESTED`. Unter den 120
Gleichabstandszeilen kommt er jedoch nicht vor.

## Grad — 89-mal `LEFT`

`E` erscheint 67-mal, `EE` 22-mal. Der Grad gehört zur bereits geöffneten
Handlung links; der rechte Kopf beginnt erst danach seine innere Handlung.

```text
CH + E + T + E + Y
→ CH[GRAD I; T[GRAD I; Y]]
```

Das bleibt auch in den zwei längeren Gleichständen so. In
`Y+T+O+E+O+P+CH+E+Y` stehen Ausführungszeichen zwischen `T`, dem ersten `E`
und `P`; sie eröffnen keinen Handlungskopf. Daher schließt dieses `E` weiterhin
an `T` an. Rohe Atomnähe allein wäre hier die falsche Lehrregel.

## Argument — 18-mal `LEFT`

Die elf `Y`- und sieben `OR`-Stellen vervollständigen den links offenen Kopf.
Der rechte Kopf bildet anschließend die innere Folgehandlung:

```text
T + OR + SH + OR
→ T[EINHEIT; SH[EINHEIT]]

Y + K + Y + CH + Y
→ Y; K[POSTEN; CH[POSTEN]]
```

Auch `CH+OR+CH+Y` bleibt eindeutig, obwohl beide Köpfe denselben Wert NEHMEN
tragen: Atom 1 erhält die EINHEIT; Atom 3 eröffnet danach den inneren
NEHMEN-POSTEN. Insgesamt stehen bei 20 der 120 Fälle links und rechts Köpfe
mit demselben Kern. Die Atomposition, nicht der ausgeschriebene deutsche Wert,
unterscheidet sie.

## Beziehung — zwölfmal `LEFT`, einmal `RIGHT`

`AL=ZIELORT` und `AR=AUSGANG` schließen gemäß ihrer festen Seite links an.
Das gilt sogar für den weitesten Gleichstand:

```text
P + OL + D_ADDR + AR + A_ADDR + IIN + S
→ P[FORTSETZEN; HIER; AUSGANG; HIER; STUFE; S[...]]
```

Hier liegt `AR` drei Atome von beiden Köpfen entfernt. `OL`, die örtlichen
Zeichen und `IIN` öffnen dazwischen keinen neuen Handlungskopf.

Der einzige Rechtsfall ist:

```text
f77r · P1003-E0393
CH + L + CH + P + SH + EE + Y
→ CH[(VERBINDUNG → CH)[P[SH[GRAD II; POSTEN]]]]
```

`L=VERBINDUNG` eröffnet den folgenden `CH`-Rahmen. `AIR=LAUF` hätte dieselbe
Richtung, erscheint aber in keiner der 120 Gleichabstandsstellen.

## Mehrkopfkarte und Doppelregel

Alle Stellen liegen definitionsgemäß zwischen zwei Handlungsköpfen. Der
direkte Anschluss des Fokus und die Klammerung der ganzen Karte sind zwei
verschiedene Fragen:

- `LEFT` bedeutet: Fokus direkt am linken Kopf; der rechte Kopf bleibt darin
  als folgende innere Handlung verschachtelt.
- `RIGHT` bedeutet: Fokus rahmt direkt den rechten inneren Kopf.
- `NESTED` wäre nötig, wenn der Fokus selbst eine äußere/innere Doppelstufe
  bildet.

Keine der 120 Ereigniskarten überschneidet sich mit den 40 in Pass 1021
entschiedenen Doppelereignissen. Die Doppelregel wird deshalb weder geändert
noch erneut ausgelegt. Ihr Vorrang bleibt trotzdem der erste Handgriff: erst
Paket öffnen, danach Seite binden.

## Entfernung und Vollständigkeit

- 118 Foki stehen genau ein Atom von beiden Köpfen entfernt.
- Ein Grad steht je zwei Atome entfernt.
- Ein `AR` steht je drei Atome entfernt.
- 120 verschiedene Ereigniskarten liefern genau 120 Entscheidungen.
- Kein Wurzelwert wurde verändert und keine Stelle bleibt offen.

Die vollständige Zeile-für-Zeile-Liste nennt beide Kopfatome, Zwischenzeichen,
direkten Regenten, Paketklammer und die vorhandene Pass-1022-Bindungsspur.

## Dateien

- `EQUAL_DISTANCE_RESOLUTIONS.tsv` — alle 120 Entscheidungen
- `EQUAL_DISTANCE_COUNTS.tsv` — Entscheidungen nach Familie, Kern und Abstand
- `EQUAL_DISTANCE_SUMMARY.json` — kompakte Summen und Anschlussprüfungen
- `EQUAL_DISTANCE_BUILD.py` — vollständiger Neubau aus Pass 1021/1022
