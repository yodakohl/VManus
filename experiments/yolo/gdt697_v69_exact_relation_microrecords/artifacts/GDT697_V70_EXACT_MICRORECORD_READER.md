# GDT697 / V70 — sieben exakte Relations-Mikrorecords

Status: `PASS_V70_7_EXACT_MICRORECORDS__9_EDGE_COVERAGE__1_SERIAL_CHAIN_1_SHARED_DESTINATION_REPEAT_5_SINGLE__ZERO_WORD_MEANING_DELTA`

V70 setzt die neun bereits in V69 zugelassenen lokalen Kanten zu sieben eng begrenzten Arbeitsanweisungen zusammen. Die bisherigen 479 Glossen und 51 Zeilen bleiben unverändert; der praktische Text steht in einer getrennten Spalte.

## Die sieben konkreten Fenster

| ID | Stelle | Formen | Stütze | konkrete Mikroanweisung |
|---|---|---|---|---|
| M001 | `f104v.2 #4–6` | `otaiin<br>ydaiin<br>qokamdy` | `B_ONLY` | Kalter Ansatz, Grad III: davon drei Maße. Eines der drei Maße nehmen und erhitzen. |
| M002 | `f105v.1 #3–4` | `olpcheey<br>ykaiin` | `A_ONLY` | Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. |
| M003 | `f113v.17 #6–7` | `cthororaiin<br>yteeeor` | `A_ONLY` | Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen. |
| M004 | `f75r.3 #3–4` | `orchey<br>qey` | `A_ONLY` | Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen. |
| M005 | `f77r.38 #5–6` | `chcphey<br>qol` | `A_ONLY` | Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben. |
| M006 | `f80v.35 #3–6` | `olkar<br>y<br>qol<br>qol` | `A_PLUS_B` | Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben. |
| M007 | `f86v6.25 #2–5` | `qokar<br>olkar<br>qodar<br>ykaiin` | `A_MINUS_PLUS_B` | Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen. |

Nur M007 ist eine wirkliche Zweischrittkette mit benanntem Zwischenprodukt. M006 sind zwei getrennte Zugaben an dasselbe Ziel; die erste Zugabe erzeugt keinen geschriebenen Ausgang für die zweite. In keinem Fenster ist ein Endprodukt nach der letzten Handlung benannt.

## Token- und Grenzapparat

### M001 — `f104v.2 #4–6`

**Lesetext:** Kalter Ansatz, Grad III: davon drei Maße. Eines der drei Maße nehmen und erhitzen.

- `#4 otaiin` — kalter Ansatz, Grad III [`PREPARATION_HEAD:C009`]
- `#5 ydaiin` — davon drei Maße [`DONOR_MEASURE_POOL:C009|REFERENCE:C009`]
- `#6 qokamdy` — ein Maß nehmen und erhitzen [`TARGET_ACTION:C009`]

Grenze: `CUT_AFTER_UNLINKED_3` / `CUT_BEFORE_UNLINKED_7`. Die zeileninitiale Referenz bei #1 bleibt offen; #3 und #7 werden nicht eingezogen.

Nicht einziehen: Do not infer that an earlier action produced the cold preparation or the three measures.

### M002 — `f105v.1 #3–4`

**Lesetext:** Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen.

- `#3 olpcheey` — trocken gebundenes Holzpulver, Form II [`DONOR_MATERIAL:C001`]
- `#4 ykaiin` — erhitze hiervon auf Stufe III [`REFERENCE:C001|TARGET_ACTION:C001`]

Grenze: `CUT_AFTER_UNLINKED_2` / `CUT_BEFORE_UNLINKED_5`. Die spätere Richtungsrivalität bei #7–#9 bleibt außerhalb des Fensters.

Nicht einziehen: Do not call #5 the result of heating without a separate edge.

### M003 — `f113v.17 #6–7`

**Lesetext:** Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen.

- `#6 cthororaiin` — drei Portionen Krautdroge [`DONOR_PORTION_POOL:C002`]
- `#7 yteeeor` — hiervon eine Portion bis zur letzten Stufe abkühlen [`REFERENCE:C002|TARGET_ACTION:C002`]

Grenze: `CUT_AFTER_UNLINKED_5` / `END_OF_LINE`. Das vorangehende Mengen- und Zustandsregister bleibt außerhalb; rechts endet die Zeile.

Nicht einziehen: Do not cool all three portions or attach the earlier hot preparation.

### M004 — `f75r.3 #3–4`

**Lesetext:** Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen.

- `#3 orchey` — eine Portion bis zur Mittelstufe getrocknete Droge [`DONOR_PRECEDING_PORTION:C003`]
- `#4 qey` — die vorstehende Mittelstufenportion anschließend nehmen [`REFERENCE:C003|TARGET_ACTION:C003`]

Grenze: `CUT_AFTER_UNLINKED_2` / `CUT_BEFORE_UNLINKED_5`. Die spätere Aktion #6 erhält weder #3 noch #4 als Objekt.

Nicht einziehen: Do not carry the taken portion into sheeky at #6.

### M005 — `f77r.38 #5–6`

**Lesetext:** Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben.

- `#5 chcphey` — bis zur Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum [`ADDED_OBJECT:C005`]
- `#6 qol` — Drogenstoff zugeben [`TARGET_ACTION:C005`]

Grenze: `CUT_AFTER_UNLINKED_4` / `CUT_BEFORE_UNLINKED_7`. Das gleich geschriebene qol bei #9 hat keine C005-Lizenz und bleibt ungebunden.

Nicht einziehen: Do not extend the object to qol at #9 or equate Arzneikompositum universally with Drogenstoff.

### M006 — `f80v.35 #3–6`

**Lesetext:** Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben.

- `#3 olkar` — Anteil I des heißen Holzansatzes [`DESTINATION:C004|DESTINATION:C008`]
- `#4 y` — Hierzu: [`REFERENCE:C004`]
- `#5 qol` — Drogenstoff zugeben [`TARGET_ACTION:C004`]
- `#6 qol` — Drogenstoff zugeben [`TARGET_ACTION:C008`]

Grenze: `CUT_AFTER_UNLINKED_2` / `CUT_BEFORE_UNLINKED_7`. Nur die erste Zugabe besitzt das geschriebene Hierzu; die zweite Zielwiederholung bleibt B-tier.

Nicht einziehen: Do not invent a second reference token, a different ingredient, or an output between the additions.

### M007 — `f86v6.25 #2–5`

**Lesetext:** Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen.

- `#2 qokar` — heißer Drogenanteil I [`OUTPUT_LABEL:C007`]
- `#3 olkar` — Anteil I des heißen Holzansatzes [`DONOR_SOURCE_SHARE:C007`]
- `#4 qodar` — Drogenanteil I abmessen [`DONOR_ACTION_OUTPUT:C006|TARGET_ACTION:C007`]
- `#5 ykaiin` — erhitze hiervon auf Stufe III [`REFERENCE:C006|TARGET_ACTION:C006`]

Grenze: `CUT_AFTER_UNRESOLVED_1` / `CUT_BEFORE_UNLINKED_6`. Die zeileninitiale Kühlreferenz #1 und die intratoken Maßreferenz #10 bleiben außerhalb.

Nicht einziehen: Do not call the heated material a final named product or connect the unresolved cooling action.

## Vollständige 51-Zeilen-Projektion

Die mittlere Spalte ist der byte-identische V69-Reader. Die rechte Spalte enthält nur an sieben Stellen eine zusätzliche V70-Mikroanweisung.

| Stelle | unveränderte V69-Zeile | zusätzliche V70-Mikroanweisung |
|---|---|---|
| `f102v2.3` | Zwei Portionen. | — |
| `f104v.2` | Hiervon drei Dosen bis zur Mittelstufe getrocknete Droge abmessen. Auszug vollständig abkühlen und abziehen. Trockene Arzneizubereitung, Gradanfang; kalter Ansatz, Grad III; davon drei Maße. Ein Maß nehmen und erhitzen. Unteranteil I des Anteils I des kalten Ansatzes; Rohdroge I, bis zur Mittelstufe getrocknet und abgeschlossen; Anteil II des kalten Ansatzes; eine Maßportion Ansatz. | Kalter Ansatz, Grad III: davon drei Maße. Eines der drei Maße nehmen und erhitzen. |
| `f105r.2` | Eine Dosis vollständig eingeweichte Arzneimischung; hieran anschließend: trocken am Ende des Grades; Wurzel, Charge III; kalt-trockene Zubereitung, Anfangsstufe erreicht. Eine Portion des Ansatzes abmessen. Trockenes Drogenmaterial, Mittelstufe; Drogenportion; trocken am Ende des Grades; Charge vollständig erhitzten Ansatzes. Anteil I des Ansatzes abmessen. Getrocknete Masse; fertige Zubereitung. | — |
| `f105r.31` | Vollständig erhitzte und abgeschlossene Zubereitungsdosis; getrocknetes Holz; eingeweichtes Gummi; Drogenanteil I. In drei Bündel abfüllen und schließen. Vollständig bereitetes und abgeschlossenes Arzneikompositum; Rohstoffklasse I im heißen Ansatz, Gradanfang; bis zur mittleren Heizstufe erhitztes Holz; Anteil I der erhitzten Holzdroge; mittlere Trockenstufe erreicht; heiß, Grad III; Drogenportion; heiß-trockene Blütenzubereitung in Grundform. | — |
| `f105v.1` | Pulveranteil II, abgeschlossen; Anteil II des Ansatzes; trocken gebundenes Holzpulver, Form II. Erhitze hiervon auf Stufe III. Fertiges Holzextraktpulver; drei Dosen bis zur Mittelstufe getrockneten Pulvers; abgemessener Ansatzanteil II, fertiggestellt. Hieraus Pulver bis zur Mittelstufe trocknen. Samenanteil II, abgeschlossen. | Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen. |
| `f105v.14` | Drei Dosen bis Mittelstufe getrocknetes Pulver; trockenes Arzneikompositum, Anfangsstufe erreicht. Nimm den heißen Drogenanteil III. Fertiges Holzextraktpulver; abgezogene Portion Holzauszug; Menge IV; kaltgestellte Rohdroge II. Anteil I des Ansatzes abmessen. Erhitzter Drogenanteil I, abgezogen. Droge kalt trocknen und leicht nachtrocknen. | — |
| `f106r.23` | Bis zur Mittelstufe getrocknet und abgeschlossen. Das Arzneikompositum bis zur Mittelstufe aufbereiten. Abgemessener Anteil II; Rohstoffklasse I; heiße Mittelstufe erreicht; bis zur Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum; heiß und trocken am Anfang des Grades; kalter Ansatz, Mittelstufe erreicht; abgemessener Anteil I; eine Portion des Drogenanteils I. | — |
| `f107r.2` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Eine bis zur Mittelstufe gekühlte Ansatzcharge nehmen. Menge III; mittlere Feuchtstufe erreicht; vollständig abgekühlter und abgezogener Auszug. Nimm eine Drogenportion. Menge III; trocken angesetztes Arzneikompositum am Gradanfang; Holzansatz vollständig erhitzt; kalter Ansatz, Grad II; trocken in der Mitte des Grades. Die vorstehende Behandlung bis zur letzten Stufe führen und abschließen. Holzportion. | — |
| `f107r.40` | Holzstoff, heiß auf Stufe III; trocken in der Mitte des Grades; heiß, Grad III; Rohstoffklasse I, trocken am Gradanfang; Menge III; heißer Ansatz, Grad III; Anteil I des heißen Holzansatzes; Anteil II des kalten Ansatzes; Rohstoffklasse I im heißen Ansatz, Gradanfang; Rohstoffklasse I im heißen Ansatz, Gradanfang. | — |
| `f10r.2` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Eine Portion Krautansatz; trockener Drogenanteil I; trocken-kalt am Gradanfang; Ansatzcharge; trockener Drogenanteil II; nachgekühlter Trockenstoff im Ansatz; heißer Ansatz am Anfang des Grades; Qualitätsgrad III des erhitzten Ansatzes; bis Mittelstufe gekühlte Zubereitung, abgeschlossen. | — |
| `f112r.36` | Samen, Charge II; Grundansatz; trockenes Arzneikompositum am Gradanfang; Holzansatz, trocken auf Stufe II; heißer Ansatz am Ende des Grades: ein Maß Holz. | — |
| `f112v.10` | Feuchtgrad II; feucht am Ende des Grades; heiß-trockene Zubereitung, Mittelstufe erreicht: zwei Portionen. | — |
| `f113v.12` | Bis zur Mittelstufe getrocknete Samenmasse; fertiges kalt angefeuchtetes Mazerat; Anteil I der Holzdroge; Holzansatz, bis Mittelstufe getrocknet; zwei Portionen. | — |
| `f113v.17` | Drei Teile des Samenanteils I; mittlere Feuchtstufe erreicht; trocken gebundenes Holz, Form II; Anteil I des heißen Holzansatzes: heißer Ansatz, Grad III; drei Portionen Krautdroge. Hiervon eine Portion bis zur letzten Stufe abkühlen. | Von den drei Portionen Krautdroge eine Portion bis zur letzten Stufe abkühlen. |
| `f113v.3` | Samenanteil I; Menge III; Anteil I des abgekühlten Trockenansatzes; Anteil I des vollständig erhitzten Auszugs; heiß, Grad II; Holz-Grundansatz: ein Maß Holz. | — |
| `f114r.24` | Drei Dosen bis zur Mittelstufe kalt-getrocknete Droge; abgemessener Drogenrohstoff I; Pflanzenteil; nachgetrocknetes Pulver, Form II; bis zur Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum; leicht angetrocknetes Arzneikompositum im Ansatz; eine Charge Trockenansatz; Drogenanteil III; trocken-kalt am Gradanfang; Pulverzubereitung aus Trockengut; Samenanteil II; Arzneikompositum in Grundform; abgemessener Anteil II. | — |
| `f114r.26` | Hiervon drei Dosen des zweiten Trockenansatzes abmessen. Anteil III des heißen Holzansatzes; heiß, Grad III; Trockenansatz, Dosis III; Anteil I des heißen Ansatzes; heiße Drogenbasis, Stufe III; heißer Ansatz, Grad III; getrocknete Masse; Grundansatz aus Drogenanteil II; ein Maß Holz. | — |
| `f114v.36` | Kalt und feucht in der Mitte des Grades; abgemessene Rohstoffmenge I im Grundansatz; Pulverzubereitung; erhitztes Mazerat; kalt-trockene Zubereitung in der Mitte des Grades. Nimm getrockneten Pulverstoff. Drei Teile Pulverzubereitung nehmen. Kalter Drogenanteil I; Rohstoffklasse I; Rohstoffklasse I, heiß am Gradanfang; ein Maß Wurzel. | — |
| `f115r.1` | Blütenanteil I abmessen. Nimm getrockneten Pulverstoff. Zwei Dosen bis zur Mittelstufe getrocknetes Gut abmessen. Kalter Ansatz, Mittelstufe erreicht; bis zur Mittelstufe getrocknet; Pulverstoff; vollständig abgekühlte Zubereitung, fertig; eine Portion des Ansatzanteils III; fertige, bis zur Mittelstufe getrocknete Masse; kalter Ansatz am Ende des Grades; kalt-trockene Mittelstufe erreicht. | — |
| `f115r.23` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Heiß am Ende des Grades. Heißen Auszug bereiten und abschließen. Leicht getrocknete Zubereitung, abgeschlossen. Erhitze, trockne und setze an. Samenposten; trockenes Kraut; stark erhitzt, Endstufe III; stark erhitzt, Endstufe III; Holzstoff; mittlere Trockenstufe erreicht; heiß-trockene Mittelstufe erreicht; fertig aufbereitetes Holz. | — |
| `f116r.12` | Zweiten Ansatz nehmen. Drogenanteil I; nachgetrocknetes Drogenmaterial, Mittelstufe; heißer Ansatz, Grad II; zwei Portionen des erhitzten nachgetrockneten Drogenmaterials; trocken am Ende des Grades; heißer Ansatz am Ende des Grades; kalter Ansatz, Grad II; Holz im Ansatz fertig getrocknet; Rohstoffklasse I im kalten Ansatz, Gradanfang; zwei Portionen der Rohdroge I im kalten Anfangsansatz; ein Maß Holz. | — |
| `f23r.6` | Kalt eingeweichter Drogenstoff; hierzu: heiße Drogenportion; heiß, Grad III. Hierzu leicht erhitzen. Abgemessener Anteil I; heißer Ansatzstoff; fertige abgemessene Mittelstufen-Trockenportion; drei abgemessene Mengen Rohdroge I; Dosis I. Hieraus eine kalte Trockenmischung herstellen. Eine Charge Holzrohstoff I abmessen. | — |
| `f24v.15` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Heißer Auszug aus Trockengut, abgezogen und abgeschlossen; eine Dosis angetrocknete Rohdroge I; fertige Trockenmasse. | — |
| `f26r.2` | Fertige abgemessene Mittelstufen-Trockenportion: Menge III; gleicher abgemessener Teil der fertigen Zubereitung. Hiervon Krautdroge bis zur Mittelstufe erhitzen und abschließen. Mittlere Trockenstufe erreicht. Hiervon bis zur Mittelstufe abkühlen und abschließen. Krautdroge mäßig trocknen, nochmals mäßig trocknen und abschließen. Eine Charge Holz. | — |
| `f27r.9` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Vollständig erhitzter und abgezogener Auszug; Mazerat aus kalt bis Mittelstufe getrockneter Droge; trocken; kalter Ansatz am Anfang des Grades; trocken am Anfang des Grades; ein Gran kalten Drogenmaterials. | — |
| `f30r.9` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Trockenen Drogenanteil I nehmen. Trocken; vollständig erhitzt, Stufe III. Krautdroge bis zur mittleren Stufe trocknen. Pflanzenteil. Bis zur mittleren Trockenstufe, dann leicht erhitzen. | — |
| `f49r.16` | Getrocknete Droge nehmen. Trocken am Ende des Grades; fertige abgemessene Mittelstufen-Trockenportion. Abkühlen, bis zur Mittelstufe trocknen und neu ansetzen. | — |
| `f56r.6` | Hieraus eine warme Trockenmischung bereiten. Fertige abgemessene Mittelstufen-Trockenportion; heiß am Ende des Grades; Qualitätsgrad III des heißen Endzustands. | — |
| `f75r.3` | Heiß, Grad II; Rohstoffklasse I, trocken am Gradanfang; eine Portion bis zur Mittelstufe getrocknete Droge. Die vorstehende Mittelstufenportion anschließend nehmen. Heiß, Grad II. Vollständig einweichen, erhitzen und abschließen. Holz, kalt auf Stufe II; Anteil I des heißen Holzansatzes: Drogenportion. | Die vorstehende, bis zur Mittelstufe getrocknete Drogenportion anschließend nehmen. |
| `f76v.10` | Eine Portion Arzneikompositum abmessen. Feuchte abgemessene Rohstoffmenge I in der Gradmitte. Fertig getrocknetes Pulver nehmen. Bis zur Mittelstufe angefeuchtete Drogenportion; mittlere Feuchtstufe erreicht; kalt-trockene Mittelstufe erreicht; Rohholz I, vollständig eingeweicht und kaltgestellt; bis zur Mittelstufe eingeweichtes und abgeschlossenes Arzneikompositum: drei Portionen des eingeweichten Arzneikompositums. | — |
| `f77r.38` | Pulverstoff; mittlere Feuchtstufe erreicht. Nimm die Endportion hinzu. Heiß, Grad III; bis zur Mittelstufe getrocknetes und abgeschlossenes Arzneikompositum. Drogenstoff zugeben. Holz, kalt auf Stufe III; mittlere Feuchtstufe erreicht. Drogenstoff zugeben. | Das bis zur Mittelstufe getrocknete und abgeschlossene Arzneikompositum zugeben. |
| `f77v.7` | Bis zur Mittelstufe eingeweichte Drogenbasis, abgeschlossen. Vollständig eingeweichten Drogenstoff zugeben und abschließen. Hiervon nehmen. Getrocknete Wurzel. Hiervon bis zur Endstufe trocknen. Heißer Ansatz, Mittelstufe erreicht; vollständig eingeweichtes Holz, Form I; Trockengut, Grundform; feuchte abgemessene Rohstoffmenge I am Gradanfang; mittlere Trockenstufe erreicht. Leicht erhitzten Drogenstoff hinzugeben. | — |
| `f7r.2` | Eine Dosis vollständig trocknen und abschließen. Ansatz auf mittlerer Heizstufe; Wurzel; Blüte. Drogenstoff abmessen und abschließen. Fertige abgemessene Mittelstufen-Trockenportion; heiß und trocken in der Mitte des Grades; kalt-trockene Zubereitung am Anfang des Grades; getrocknete Masse. | — |
| `f80r.17` | Samenansatz, leicht erhitzt; feuchtes Arzneikompositum am Gradanfang. Bis zur Mittelstufe einweichen, erhitzen und abschließen. Eingeweichter Drogenstoff, bis Mittelstufe erhitzt; heißer Drogenanteil I. Bis zur Mittelstufe einweichen, erhitzen und abschließen. Bis Mittelstufe trocknen, dann auf Kühlstufe II bringen. Grundansatz; Anteil I des heißen Holzansatzes: heißer Ansatz, Grad II. Bis zur Mittelstufe einweichen, erhitzen und abschließen. Rohstoffklasse I, heiß am Gradanfang. Eine Teilmenge abmessen. | — |
| `f80v.27` | Eingeweichtes Pulver; heiß, Grad II; Anteil I des heißen Holzansatzes; feucht in der Mitte des Grades; heiß, Grad II; abgemessene Rohstoffmenge I; Holzansatz, kalt auf Stufe III; heißer Ansatz, Grad II; Rohstoffklasse I, feucht am Gradanfang; kalt am Anfang des Grades. | — |
| `f80v.35` | Kalt; Holzansatz, kalt auf Stufe II; Anteil I des heißen Holzansatzes. Hierzu: Drogenstoff zugeben. Drogenstoff zugeben. Heiß, Grad II; erhitzte Zubereitung, Form III; Grundansatz; heiß, Grad II; feucht in der Mitte des Grades; fertig aufbereitetes Holz. | Dem Anteil I des heißen Holzansatzes Drogenstoff zugeben. Dem Anteil I des heißen Holzansatzes nochmals Drogenstoff zugeben. |
| `f83v.12` | Drei Portionen feuchten Arzneikompositums; Arzneikompositum: feucht, Gradanfang; zweites Mazerat. Anteil I der Holzdroge abmessen. Trocken am Ende des Grades; Rohstoffklasse I; heiß am Ende des Grades; Anteil I des heißen Holzansatzes; feucht am Ende des Grades; heiß, Grad II; Ansatz aus Holzrohstoff, Form I. | — |
| `f85r2.5` | Abgemessener Anteil I der Arzneizubereitung; Anteil I des heißen Holzansatzes; Blütenrohdroge I. | — |
| `f86v3.13` | Vollständig eingeweichtes Mazerat; eine Portion vollständig eingeweichte Droge. Abkühlen, bis zur Mittelstufe trocknen und ansetzen. Heiß, Grad II; drei Portionen des Anteils I des heißen Holzansatzes; abgemessene Trockendroge, Dosis III; hierzu: mittlere Trockenstufe erreicht. Einen gleichen Teil erhitzen. Trockengut, heiß auf Stufe II. | — |
| `f86v3.18` | Drei Dosen bis Mittelstufe getrocknetes Pulver; fertige abgemessene Trockenportion; heiß-trockene Anfangsstufe erreicht. Nimm getrockneten Pulverstoff. Feucht; feucht angesetztes Mazerat auf Anfangsstufe, abgeschlossen; ein Maß erhitzter Samenzubereitung. | — |
| `f86v3.19` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Kalter Ansatz, Grad II. Holzansatz mäßig erhitzen, trocknen und abschließen. Nimm ein Maß und erhitze es. Trocken; heiß-trockene Anfangsstufe erreicht; trocken; kalt-trockene Anfangsstufe erreicht; abgemessener Anteil I; drei fertig abgeteilte Teile. | — |
| `f86v5.2` | Anteil II des Holzpostens; fertige kalte Zubereitung; heißer Drogenanteil I; feucht am Anfang des Grades; heißer Drogenanteil I; Blüte. Nimm getrockneten Pulverstoff. Rohstoffklasse I, kalt am Gradanfang; Grundansatz. Kühle hiervon den Drogenstoff ab. Ein Maß kalten Ansatzes; ein Maß kalten Ansatzes. | — |
| `f86v5.24` | Anteil I des Ansatzes; Menge III. Erhitze hiervon auf Stufe II. Rohstoffklasse I im heißen Ansatz, Gradanfang; fertige heiß-trockene Zubereitung; Arzneikompositum: trocken, Gradanfang; kalter Ansatz, Grad III; Anteil I des heißen Holzansatzes; kalter Ansatz, Grad III. | — |
| `f86v5.4` | Hiervon Samenpulver bis zur Mittelstufe trocknen. Heißer Ansatz am Anfang des Grades; vollständig eingeweichtes Gut der Schlussstufe; kalt am Anfang des Grades; kalt, Grad III; Samen, Charge II; Trockenpulver in Grundform; fertig abgekühltes Holz, Mittelstufe; abgemessener Anteil I; Anteil I des heißen Holzansatzes: Maßeinheit I. | — |
| `f86v6.25` | Hiervon bis zur Endstufe abkühlen. Heißer Drogenanteil I; Anteil I des heißen Holzansatzes. Drogenanteil I abmessen. Erhitze hiervon auf Stufe III. Drogenportion; Zubereitung vollständig bis zur letzten Heizstufe geführt; fertig getrocknete Blütenmasse; heiß, Grad III; Drogenanteil I; davon ein Maß. | Aus dem Anteil I des heißen Holzansatzes einen heißen Drogenanteil I abmessen. Den so abgemessenen Drogenanteil I auf Stufe III erhitzen. |
| `f86v6.31` | Abgemessener Anteil II; Trockenpulver in Grundform; heiß, Grad III; Anteil I des heißen Holzansatzes; fertige heiß-trockene Drogenportion; Anteil I des heißen Ansatzes; Rohstoffklasse I; abgemessener Anteil I; erhitzter Holzansatz, bis Mittelstufe getrocknet. Aus dem Kaltansatz ein Maß nehmen und erneut kühlen. Eine Handvoll Drogenmaterial als Portion. | — |
| `f86v6.4` | Abgemessene Blütendroge; feuchte Anfangsstufe erreicht; Blüte; Grundansatz; Menge III; Holzansatz vollständig erhitzt; feuchte abgemessene Rohstoffmenge I am Gradanfang; eine Portion kalten Ansatzes, Mittelstufe; abgemessener trockener Drogenanteil I; vollständig getrocknete Charge aus Anteil I der erhitzten Holzdroge; Anteil I des heißen Holzansatzes; ein Maß Rohdroge I. | — |
| `f86v6.5` | Kalter Drogenanteil I; Holzstoff; trocken; Anteil I des heißen Holzansatzes; drei Portionen davon; trockener Drogenanteil I; Drogenportion; kaltes Mazerat in der Mitte des Grades; heißer Drogenanteil I; Trockenpulver, Form I; kalt angesetzte Charge, leicht angewärmt; kalter Drogenanteil I. | — |
| `f88r.19` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Heißer Absud aus Trockengut; Qualitätsgrad III dieses heißen Absuds. Heißen Drogenstoff der Mittelstufe zugeben. Heißen Drogenstoff der Mittelstufe zugeben. Drogenstoff aus Arzneikompositum zugeben. Heißer Ansatzstoff; trockener Drogenstoff. | — |
| `f8r.15` | Eine abgemessene Portion bis zur Mittelstufe trocknen. Drogenstoff aus Arzneikompositum; trocken; trocken in der Mitte des Grades; Charge unter Wärme getrockneter Droge; trocken am Anfang des Grades; drei Materialmaße; Materialmaß; abgemessener Drogenanteil IV, leicht getrocknet; Arzneikompositum am Gradanfang. | — |
| `f95v1.7` | Eine Dosis bis zur Mittelstufe angefeuchtete Droge; heiß, Grad II; heißer Drogenanteil I; Anteil I des heißen Holzansatzes; trocken am Anfang des Grades; kalter Drogenanteil I; Anteil I des kalten Ansatzes; trockene Anfangsstufe erreicht; heiß-trockene Anfangsstufe erreicht; abgemessenes heißes Drogenmaterial, Stufe II; fertiger Anteil I des kalten Ansatzes. | — |

## Harte Reichweite

- 9/9 V69-Kanten genau einmal; keine aus bloßer Nachbarschaft erzeugte Kante.
- 7 disjunkte Minimalfenster mit 19 Tokenpositionen und 16 berührten V68-Klauseln.
- 5 Einzelhandlungen, 1 geordnete Zielwiederholung, 1 serielle Ausgangskette.
- 1 benanntes Zwischenprodukt, 0 benannte Endprodukte.
- 479 Token, 51 Zeilen und 3 gebundene Spannen unverändert; 0 neue Wortbedeutungen.

Diese Mikrorecords sagen lokal mehr als der alte Semikolon-Reader, ohne die offenen Anschlüsse vor oder nach dem Fenster zu erfinden.
