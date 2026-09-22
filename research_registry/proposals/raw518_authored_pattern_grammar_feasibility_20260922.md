# IDEA518: ausführbare feste Muster, keine allgemeine Grammatik

2026-09-22. **Formale Vorprüfung ohne Zerlegungszensus oder Lesergebnis.**
IDEA518 kann prinzipiell die Verträglichkeit vollständiger vorgegebener
Terminalfolgen mit einer neuen Wortpackung prüfen. Die geerbten 9+4 Konstruktionen
sind jedoch **verfasste Positionsmuster**. Nur die neun Originalmuster besitzen
hier bereits eine ausführbare Prüfung samt fest angeschlossenem Inhaltsplan.
Die vier Erweiterungsmuster liegen als vollständige JSON-Spezifikation vor;
RAW492 wurde ausdrücklich nicht zur Ausführung ausgewählt.

## Was die Primärfelder und der Code tatsächlich tun

- [Original SOURCE.json](../../experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json#L1064):
  `complete_clauses` enthält C01–C09 mit jeweils `locus`, `raw`, `production`,
  `terminal_tags` und einer verfassten `reduction`. Die neun Terminalzahlen sind
  9/13/10/9/10/10/9/8/6. Das sind Spezifikationsgrößen, keine neue Leserzählung.
- `grammar_contract.productions`, Zeile1251, bindet genau diese neun Muster
  an die neun geerbten Zeilenpositionen und bezeichnet sie ausdrücklich als
  frei angepasste Schemata. `goal_scope`/`choice_scope`, Zeilen1253–1254,
  ordnen GOAL genau C01 und die Alternative genau C06/C07 zu.
- [model.py](../../experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/model.py#L3),
  `compile_program`: Es müssen neun Zeilen und neun Klauseln vorliegen.
  `zip(lines,clauses)` paart sie positionsweise. Jede Zeile wird an ihren
  vorhandenen Leerstellen zerlegt; die lexikalischen Tags müssen exakt
  `c['terminal_tags']` gleichen. Anschließend werden Plan, Teilnehmer S/G/P/I/A/W,
  Bild-/Materialrollen und die beiden WITH-Bindungen direkt im Code aufgebaut.
  Die Prosareduktionen werden nicht von einem allgemeinen Typ- oder
  Funktionsanwendungsparser interpretiert.
- [independent.py](../../experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/independent.py#L5),
  `compile_reverse`, prüft dieselben Zeilenmuster rückwärts und baut denselben
  festgelegten Plan getrennt auf. Das ist eine unabhängige Implementierung
  dieser Spezifikation, kein zweiter unabhängig erschlossener Syntaxbefund.
- [Erweiterungs-JSON](raw_f108r_amulet_frozen71_complete_commentary_20260921.json#L1692):
  `complete_new_block_clauses` enthält C10–C13 mit den expliziten ursprünglichen
  Positionsspannen1–6/7–18/19–24/25–33 und Terminalzahlen6/12/6/9.
  `exact_new_grammar`, Zeilen1812–1816, verlangt deren feste Folge und nur die
  bereits bezeichneten Zeilenüberschreitungen; `not_general_grammar` nennt sie
  ausdrücklich vier weitere frei verfasste Produktionen.
  `new_binding_assumptions` ab1819 ergänzt die festen Gegenstands-, Zeit- und
  Behauptungsbezüge. Diese entstehen nicht erst aus der neuen Wortzerlegung.

Eine endliche Sprache aus festen Mustern ist formal implementierbar. Ihr
vollständiges Erkennen ist aber schwächer als das Erkennen beliebiger neuer
Aussagen durch eine wiederverwendbare Grammatik. Die alte Ausführung von1023
ist dadurch nicht ungültig: Sie prüfte ausdrücklich einen verfassten ganzen
Inhaltsplan unter gesetzten Bedeutungen.

## Was vor einer späteren IDEA518-Auswahl ausdrücklich festzulegen ist

Die neue Packungsregel erzeugt **lexikalische Terminals innerhalb unveränderter
Rohgruppen**. Die alten Matcher arbeiten dagegen direkt auf Rohgruppen. Ein
neuer Matcher wäre daher nötig; der vorhandene Code kann nicht unverändert
als bereits fertiger Parser ausgegeben werden.

Die kleinste klar begrenzte Auslegung wäre:

1. Beim Original bleiben die neun physischen Zeilen und ihre zugehörigen Muster
   fest. Keine Umverteilung von Terminals auf andere Zeilen oder Klauseln.
2. Bei der Erweiterung werden die vier verfassten Muster vollständig in der
   alten Reihenfolge verlangt. Es muss **vor jeder Zerlegungsrechnung** entschieden
   werden, ob die alten Positionsspannen Rohgruppen oder expandierte lexikalische
   Terminals bezeichnen und wie ihre vorhandenen physischen Zeilenbezüge erhalten
   bleiben. Für ein Packungsmodell wäre die Terminal-Auslegung nachvollziehbar,
   ist aber eine explizite neue Koordinatenregel, kein automatisch unveränderter
   Altvertrag. Auch eine mögliche Klauselgrenze innerhalb einer gepackten Gruppe
   darf nicht erst nach einem günstigen Fall zugelassen werden.
3. Jede erzeugte Terminalposition behält den Verweis auf ihre Rohgruppe und
   Zeichenposition. Alle atomaren und zulässigen binären Analysen bleiben erhalten;
   keine Auswahl durch den gewünschten Sinn oder nur die bekannten Kollisionen.

Diese Punkte sind **eine angebotene Auswahlpräzisierung, hier nicht ausgewählt
oder implementiert**. IDEA518 bleibt bytefest. Eine andere allgemeine Grammatik,
freie Klauselanordnung oder neu erfundene Typinferenz wäre eine zusätzliche
Entwicklung und darf nicht unter dem Namen der unveränderten13 Schemata laufen.

## Entscheidungswert und Grenze

Ein vollständiger Erfolg könnte zeigen: Derselbe neue Packungsvertrag lässt
eine ganze alternative Rohlesung genau den zuvor verfassten Inhalts-Terminalstrom
darstellen. Das wäre eine begrenzte neue Repräsentationsverträglichkeit, nicht
eine unabhängige Auswahl der Amulettbedeutungen. Ein Scheitern beträfe diese
Kombination aus Packung und festen Mustern.

Da die erfolgreichen Terminalfolgen selbst festgelegt sind, bedeuten mehrere
lexikalische Zerlegungen zunächst **Zerlegungsmehrdeutigkeit**. Unterschiedliche
vollständige Bedeutungen folgen nur, soweit bereits verschiedene erhaltene
Reduktionen/Bindungsrivalen vorhanden sind. Insbesondere wählt der Matcher nicht
selbstständig zwischen Stein und Zusammenstellung als Behauptungsträger. Eine
Übereinstimmung mit einer vorgeschriebenen Tagfolge darf nicht als unabhängig
gewonnene semantische Eindeutigkeit berichtet werden.

Keine Aussage darüber, welche zusätzlichen Splits vorkommen, welcher Leser
vollständig passt oder wie viele Kandidaten überleben: Nichts davon wurde
berechnet. Kein Parser, Lexikonwechsel, Zielzugriff, neuer RAW-Vorschlag oder
Registry-Eintrag in diesem Pass.

## Hashbelege

- IDEA518 JSON: `bde784cf499b993ac66e7b1468c6db26c1783e188d590bcb189e622e96883805`.
- Original SOURCE.json: `a4afec1925b5561215124df1206d02c152786154756bb80c9a6a38c7470ab155`.
- Erweiterungs-JSON: `3c55e256c1d389068660a003eea068ad7f8d1690466f1289e7a4e67cc41227c9`.
- `model.py`: `18fe78e28178fa2bb7b11f6290e499f4c2426002b1b276be2bdeeae464a49d88`.
- `independent.py`: `8f358e59e94aed6e9cba64a5663399c309e1db846c846ffe916e23d0b9a7aa5e`.
- `run.py`: `d89815e5873bc810f68c2c801973ab31160cf67c3ed9d7c11d2bcdf8cd2af491`.
