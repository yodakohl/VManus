# GDT635 — vier pharmazeutische Wortköpfe auf identischem Rest

GDT635 prüft die vier initialen Zeichen `p/s/r/l` ausschließlich dort, wo
nach Entfernung des ersten Zeichens **derselbe vollständige Rest** bleibt.
`sh...`, Einzeichenformen sowie innere und terminale Zeichen sind ausdrücklich
nicht Teil dieser Regel.

Das Ergebnis ist die bisher geschlossenste konkrete Wortkopf-Arbeitstheorie:

```text
p = pulvis  → Pulver/Pulverform
s = semen   → Samen/Saatgut
r = radix   → Wurzel/Wurzeldroge
l = lignum  → Drogenholz/holziger Pflanzenteil
```

Auf 179 bereits erlaubten Seiten entstehen 760 Restkörper. 144 tragen
mindestens zwei Köpfe, 24 alle vier. Fünf vollständige Viererraster erhalten
konkrete Bedeutungen: Typ/Charge III, getrocknet, eingeweicht, Stoff und
Portion. Alle 20 Zellen sind belegt; zusammen umfassen sie 639 Token.

Zehn echte Passagen werden vollständig tokenweise ausgesprochen, etwa:

```text
f77r.38  pol shedy       Pulverstoff, angefeuchtet zu Paste oder Brei
f76v.40  sol shedy       Saatgut, eingeweicht
f106v.8  cheo rol aiin   Trockenansatz aus Wurzelstoff, Menge III
f111v.10 cheo lol aiin   Trockenansatz aus Holzstoff, Menge III
```

Die Ausgabe korrigiert zwei Fehler der vorigen Fassung: `l` ist nicht länger
standardmäßig Flüssigkeit, und `s` nicht länger standardmäßig Salz. Außerdem
werden `Kopf+aIII = Typ/Charge III` und `d+aIII = Dosis/Maß III` getrennt,
damit `paiin/saiin + daiin` keine sinnlose Doppelmenge ergibt.

Ausführung:

```bash
python3 experiments/yolo/gdt635_initial_head_same_remainder_swaps/src/run.py
python3 experiments/yolo/gdt635_initial_head_same_remainder_swaps/src/validate.py
```

Die vollständige Interpretation steht in `REPORT.md`, die genaue Konstruktion
in `METHOD.md` und alle Tabellen unter `artifacts/`.
