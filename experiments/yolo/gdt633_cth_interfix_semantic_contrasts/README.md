# GDT633 — konkrete E-/O-Lesung im CTH-Raster

GDT633 setzt auf GDT632 auf, ohne eine neue Seite oder ein neues Bild zu
öffnen. Das bisher stumme Zwischenraster erhält folgende Arbeitslesung:

```text
[ch/sh + e-Bindung?] + [o-Zubereitung? + cth-Material + Restform]
```

Die primären deutschen Defaults sind:

- `chcthy` → **Blatt-/Krautgut: trocken**;
- `checthy` → **trockenes Blatt-/Krautgut**;
- `shcthy` → **Blatt-/Krautgut: feucht**;
- `shecthy` → **feuchtes Blatt-/Krautgut**;
- `octhy` → **CTH-Zubereitung / CTH-Ansatz**, im Herbal
  **Blatt-/Krautansatz**;
- `chocthy` → **trockene CTH-Zubereitung**;
- `cheocthy` → **attributiv trockene CTH-Zubereitung**.

Das äußere `e` wird in der flüssigen Übersetzung nicht als eigenes Wort
gesprochen. Es wandelt `Blattgut: trocken` in `trockenes Blattgut` um. Die zwei
stabilen `ee`-Formen erhalten eine erweiterte oder zweite Bindungsstufe. Das
ist strikt vom inneren Rest zu trennen: `cthey` ist CTH-Form I, `ctheey`
CTH-Form II. Folglich enthält `sheecthey` äußeres `ee` und inneres `ey`, nicht
inneres `eey`.

Das fusionierte GDT632-Raster umfasst 255 Token und 48 Typen. Darin tragen 65
Token äußeres `e`, 46 inneres `o`; zwei zusätzliche stabile `ee`-Rivalen
erweitern den lesbaren Familienrand auf 257/50. Mit elf sichtbaren
Grenzrealisierungen liest die Ausgabe 268 Ausdrücke in 55 normalisierten
Typen. Die nackten Köpfe `cth+R` und `octh+R`
sind 408/69 beziehungsweise 32/16 Token/Typen stark. `octheey` bleibt die
konkrete fehlende O-Kopfform: **CTH-Zubereitung, Form II**. Sie ist eine
Vorhersage, kein bereits beobachtetes Wort.

`e=erhitzt/gekocht` bleibt nur als schwacher Sachrival offen. Nach
Vorkommensnormalisierung sind E-Formen nicht heißer als NONE-Formen; sichtbar
ist lediglich ein Mangel an kalten E-Kontakten. Eine Gradlesung bleibt wegen
der literalen `e/ee`-Leitern ebenfalls offen. `o` bedeutet weder automatisch
Wasser noch Wein noch Öl; dafür fehlt ein Mediumanker.

Ausführung:

```bash
python3 experiments/yolo/gdt633_cth_interfix_semantic_contrasts/src/run.py
python3 experiments/yolo/gdt633_cth_interfix_semantic_contrasts/src/validate.py
```

Die Methode steht in `METHOD.md`, die vollständige deutsche Auswertung in
`REPORT.md`.
