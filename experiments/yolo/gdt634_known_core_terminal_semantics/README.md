# GDT634 — konkrete Vollglossierung von acht Mikrozeilen

GDT634 übersetzt acht bereits freigegebene Zeilen vollständig auf
Arbeitsniveau. Es wird keine neue Seite und kein neues Bild geöffnet. Alle 69
Tokenpositionen und alle 58 Oberflächentypen erhalten eine konkrete
Stoff-, Teil-, Zustands-, Qualitäts- oder Mengenbedeutung; kein Platzhalter
wie „Arbeitsgut“, „Arbeitsschritt“ oder „weiterleiten“ bleibt übrig.

Der Versuch verbindet die bislang belastbarste produktive Grammatik mit vier
bewusst aggressiven pharmazeutischen Wortkopf-Hypothesen:

```text
p- initial pulvis    Pulver / pulverisierte Zubereitung
-p terminal          separate Pulverform-Hypothese
s- initial sal       Salz                       (Rivale: semen / Samen)
r- initial radix     Wurzelstoff                 (Rivale: Pflanzenteil)
l- initial liquor    Flüssigkeit / Flüssigpräparat

al / ol               Material- oder Substanzträger
ar / or               Teil-, Portions- oder Dosisträger
o in Komposition      Ansatz / Zubereitung
```

`a` und `o` vor `l/r` bleiben verschiedene sichtbare Träger; insbesondere
wird `qokal` als `qo+k+a+l` und nicht als erfundenes `qok+ol` zerlegt.
`o` ist nur in den dafür kartierten Konstruktionen „Ansatz/Zubereitung“ und
nicht pauschal Wasser, Wein oder Öl. Ein finales `m` bleibt als sichtbarer,
positionsgebundener Terminalmarker unbekannter Funktion erhalten.

Die acht vollständigen Arbeitslesungen stehen in
`artifacts/COMPLETE_MICROLINE_TRANSLATIONS.tsv`, die 69 tokenweisen Zerlegungen
in `artifacts/COMPLETE_TOKEN_WORKING_EDITION.tsv`. Die geschlossenste kurze
Zeile ist:

```text
f22v.15  sho cthy chocthy qokchy dory
         feuchter Ansatz | Blatt-/Krautgut | trockene
         Blatt-/Krautzubereitung | heiß-trocken | abgemessene Portion.
```

Die stärkste Leser-Korrektur liegt auf f85r1.21: ZL3b `daiir` wird dort durch
IT2a und RF1b als `daiin` gelesen und daher lokal als Maß III glossiert. Diese
Normalisierung gilt nicht für die übrigen 13 `daiir`-Vorkommen. Auf f29r
bleibt die echte `s/r`-Gabel sichtbar:

```text
ZL3b/RF1b posaiin  → Salzpulver-Zubereitung III
IT2a       poraiin → Pulverportion III
```

Die produktive Qualitätsfamilie umfasst im erlaubten 179-Seiten-Korpus 4.950
Token in 75 Typen auf 176 Seiten. Acht von zehn ausdrücklich geprüften
Formlisten enthalten mindestens zwei der vorab genannten Varianten; das ist
Attestation, noch kein semantischer Relationsbeweis. Die zwei Einzelbelege
`rcheald` und `lkealy` bleiben klar als schwach markiert.

Ausführung:

```bash
python3 experiments/yolo/gdt634_known_core_terminal_semantics/src/run.py
python3 experiments/yolo/gdt634_known_core_terminal_semantics/src/validate.py
```

Die Methode steht in `METHOD.md`, die vollständige Interpretation in
`REPORT.md`. Das Ergebnis ist eine vollständig ausgesprochene, ersetzbare
Arbeitstheorie für diese acht Zeilen — noch kein entzifferter Gesamttext.
