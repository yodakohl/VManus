# GDT702 — V75 exact written-result contrast

Status: `PASS_V75_11_TARGET_RIGHT_CONTEXTS__7_NOMINAL_3_ACTION_1_EOS__1_EXACT_WRITTEN_RESULT__2X2_DEFAULTS_REJECTED__C012_OCCURRENCE_BOUND__ZERO_WORD_DELTA`

GDT702 prüft die erste semantische Position rechts von jeder der elf
Zielaktionen C001–C011 aus dem vollständigen GDT701-Atlas. Der vollständige
Zensus ist vorab auf sieben nominale Rechtskontexte, drei weitere Aktionen und
ein Zeilenende festgelegt. Kein späteres, besser passendes Wort darf an der
ersten Position vorbeigewählt werden.

Die einzige nominierte Arbeitshypothese ist C012:

```text
f105v.1#3 olpcheey  --C001-->  #4 ykaiin  --C012-->  #5 olpchedy
trocken gebundenes              erhitzen              fertiges
Holzpulver, Form II                                   Holzextraktpulver
```

C012 ist höchstens `B_WORKING_LOCAL` und ausschließlich an dieses Vorkommen
gebunden. Das rechte Token ist geschrieben und bereits als nominaler
Fertigresultatzustand typisiert; die Beziehung zwischen der Heizaktion und
diesem Zustand bleibt eine explorative Arbeitsbindung.

## Warum dies kein Rechtsnachbar-Default ist

Der Test enthält einen symmetrischen 2×2-Negativkontrast:

| Vergleich | Kandidatenstelle | Kontrollstelle | verworfener Default |
|---|---|---|---|
| beide `ykaiin`-Ziele | `f105v.1#4 → #5 olpchedy` | `f86v6.25#5 → #6 or` | `YKAIIN` erzeugt kein festes rechtes Ergebniswort |
| beide `olpchedy`-Stellen | `f105v.1#4 ykaiin → #5` | `f105v.14#3 qokaiir → #4` | Ein rechts stehendes `OLPCHEDY` ist nicht automatisch Ausgang der linken Aktion |

Bei `f105v.14` lautet die linke Aktion „nimm den heißen Drogenanteil III“;
das folgende Holzextraktpulver ist materiell unvereinbar und bleibt
ungebunden. GDT689 führt `olpchedy` außerdem als
`UNPAIRED_WHOLE_RETAINED`: Aus dem sichtbaren Rahmen `olpche*` entsteht keine
produktive Wortbildungsregel.

## Provenienzgrenze

GDT682 druckte für `f105v.1` bereits die Prosa „Ergebnis ist fertiges
Trockenpulver aus Holzdrogenansatz“. Diese alte Lesung ist ausdrücklich keine
neue Evidenz. GDT687 typisierte `olpchedy` unabhängig nur als nominalen
Fertigresultatzustand, ohne es an die vorherige Aktion zu binden. GDT697 schnitt
das bisherige Mikrofenster nach `ykaiin#4` ab und verbot eine Ergebnislesung
von `#5` ohne eigene Kante. Neu geprüft wird daher nur, ob der vollständige
aktuelle Kontrast eine lokale C012-Kante rechtfertigt.

GDT702 fügt keine Wortbedeutung, Operation, Zutat, Seite oder Morphologie
hinzu. Die 479 Token-Glossen, 51 Zeilenlesungen und drei gebundenen Spannen
bleiben unverändert; `f84` und `f84r` bleiben verboten.

## Dateien und Ausführung

- `METHOD.md` beschreibt Zensus, Gates, Negativkontrollen und
  Entscheidungsregel.
- `src/V75_11_TARGET_RIGHT_CONTEXT_SPECS.tsv` enthält alle elf vorab
  festgelegten Rechtskontexte einschließlich Anti-Skip-Grenzen.
- `experiment.json` bindet die reproduzierbaren Eingaben und Ausgaben.

Reproduktion:

```bash
./vmanus-exp run experiments/yolo/gdt702_v75_exact_written_result_contrast
./vmanus-exp validate experiments/yolo/gdt702_v75_exact_written_result_contrast
```
