# GDT685 — V58 state-cell patch reader

The tested universal nouns `Trockenansatz / Feuchtansatz / Kaltansatz` do not survive the full occurrence circuit.
The portable defaults are `chol = trocken`, `shol = feucht`, and `tol = kalt`; a visible or inherited outer head supplies the material.

## Revised V57 lines

### f27r.9

Eine Dosis bis zur Mittelstufe trocknen und abschließen. Den vollständig erhitzten Ansatz abziehen und damit einen Feuchtansatz aus kalt bis zur Mittelstufe nachgetrockneter Droge ansetzen. Danach: trocken; kalter Anfangsansatz, leicht getrocknet; ein Gran kalten Drogenmaterials.

Dispatch: chol#4=trocken; Kopf zwischen vorherigem Feuchtansatz und folgender Kaltansatzzelle offen

### f30r.9

Eine Dosis bis zur Mittelstufe trocknen und abschließen. Die erste Trockenfraktion nehmen: trocken; vollständig auf Stufe III erhitzen. Die Krautdroge bis zur Mittelstufe trocknen, den Pflanzen- oder Blütenteil dazugeben und bis zur mittleren Trockenstufe bringen, dann leicht anwärmen.

Dispatch: chol#3=erste Trockenfraktion: trocken

### f80v.35

Kalt. Holzdrogenansatz auf Kühlstufe II; erste erhitzte Drogenfraktion im Ansatz. Hierzu zweimal Drogenstoff zugeben. Danach: Heizgrad II; erhitzter Ansatz in Form III; Grundansatz; Heizgrad II; mittlere Feuchtstufe; fertig aufbereitete Holzdroge.

Dispatch: tol#1=kalt; Rubrik- oder Stoffkopf offen

### f86v3.18

Drei Dosen bis zur Mittelstufe getrocknetes Pulver; abgemessene Trockendroge, fertig. Heiß-trocken auf Anfangsstufe abschließen. Fertig getrockneten Pulverstoff nehmen: feucht; den angefeuchteten Ansatz fertigstellen. Zum Schluss ein Maß erhitzter Saatgutzubereitung.

Dispatch: shol#5=vorheriger Pulverstoff: feucht

### f86v3.19

Eine Dosis bis zur Mittelstufe trocknen und abschließen; kalter Ansatz auf Grad II. Den Holzdrogenansatz mäßig erhitzen, trocknen und abschließen. Ein Maß nehmen und erhitzen: trocken; heiß-trocken auf Anfangsstufe abgeschlossen. Danach erneut trocken; kalt-trocken auf Anfangsstufe abgeschlossen. Die erste abgemessene Fraktion in drei Teile fertig abteilen.

Dispatch: chol#5=erhitztes Maß: trocken | chol#7=zweite Zustandszelle: trocken

### f86v6.5

Kalte Drogenfraktion I · Holzstoff: trocken · erste erhitzte Drogenfraktion im Ansatz · Grad/Maß III · trockene Fraktion I · Drogenportion · kalt-feuchter Ansatz, Mittelstufe · heiße Drogenfraktion I · Trockenpulver-Ansatz, Form I · kalt angesetzte Charge, leicht angewärmt · kalte Drogenfraktion I.

Dispatch: chol#3=unmittelbar linker Holzstoff: trocken

### f8r.15

Eine Dosis Arzneikompositum bis zur Mittelstufe trocknen und abschließen. Arzneikompositumstoff: trocken, bis zur Mittelstufe; eine Charge unter Wärme getrockneter Droge leicht nachtrocknen. Drei Teile als Materialmaß abnehmen und die vierte abgemessene, leicht getrocknete Fraktion mit Arzneikompositum auf Anfangsstufe ansetzen.

Dispatch: chol#3=unmittelbar linker Arzneikompositumstoff: trocken

## Working limit

These are concrete state cards, not ingredient identities. A nominal `-gut/-stoff` fallback is no longer printed by default; where no head is visible, the state remains explicit and the head remains open.
