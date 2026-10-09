# GDT1253 — 23 Einträge genügen mit einer festgelegten Quellgrammatik

**UNIVERSAL_GRAMMAR_RESTRICTED_COVER_CONSTRUCTED.** Für ein Alphabet aus22
sichtbaren Arbeitseinheiten lässt sich mit23Codeeinträgen und einer einzigen
verbotenen Quellzeichen-Nachbarschaft jede nichtleere sichtbare Zeichenfolge
eindeutig zurücklesen. Das ist eine formale Konstruktion, keine identifizierte
Voynich-Grammatik und keine statistisch passende historische Textquelle.

Zusammen mit der bereits vorhandenen <=22-Formabdeckungsgrenze erreicht dies
bedingt das Minimum23 für eine nichttriviale feste, grammatikbeschränkt lesbare
Konkatenationstabelle. Die alten Einheiten-/Ganzgruppen-/Exaktheitsannahmen bleiben
Voraussetzungen. Die Einschränkung zählt CODEEINTRÄGE, nicht sichtbare Zeichen.

## Kleine vollständige Schreib- und Leseregel

Das Lehrbeispiel benutzt abstrakte Binärzeichen, keine Voynichwerte:

| Quellsymbol | Schreibung |
|---|---|
| A |0|
| B |01|
| C |1|

Erlaubt sind alle nichtleeren Quellwörter über A/B/C, außer solchen mit der
unmittelbaren Folge AC. Diese Einschränkung wird vor dem Schreiben festgelegt.
Der Schreiber ersetzt jedes erlaubte Quellsymbol durch seinen Tabelleneintrag.
Der Leser nimmt jedes01alsB, sonst0alsA und1alsC. Sichtbare Wortgrenzen bleiben.

Beispiel: ABCC wird00111 und wieder eindeutigABCC. Ohne die Grammatik würden
B undAC beide01ergeben; AC ist hier ausdrücklich keine erlaubte Nachricht.
Die Konstruktion liest also nicht nachträglich die gewünschte Alternative aus.
Sie ist vollständig für ihre deklarierte künstliche Quellsprache, nicht für
beliebige natürliche Wörter. Quellsymbole besitzen hier keine Übersetzungswerte.

## Warum das für beliebige Länge funktioniert

Verallgemeinerung: Für jeden sichtbaren Buchstaben s gibt es X_s→s. Für zwei
verschiedene sichtbare Zeichen x,y kommt B→xy hinzu. Verboten ist ausschließlich
das benachbarte Quellpaar X_x X_y.

Vorkommen vonxykönnen nicht überlappen, weilxundyunterschiedlich sind. In der
Expansion einer erlaubten Quelle kannxyentweder innerhalb vonBstehen oder an
der Grenze X_x X_y. Letzteres ist verboten; andere Codegrenzen könnenxy nicht
neu erzeugen. Deshalb erkennt der Leser genau dieB-Einträge, nicht versehentlich
zwei andere Quellsymbole. Umgekehrt ergibt das Zusammenfassen jedesxyin einem
beliebigen Ausgabewort immer eine erlaubte Quellfolge. Expansion und Lesung sind
auf dieser Quellsprache gegenseitige Inversen. Benötigt werdenn+1Einträge bei
nsichtbaren Zeichen; keine zusätzliche sichtbare Marke, Tabelle pro Wort oder
unsichtbare Auswahlentscheidung während des Lesens.

Die freie Tabelle bleibt mehrdeutig. Das Beispiel unterscheidet sich von1201:
dort dürfen mehrere Zerlegungen dieselbe primitive Nachricht expandieren; hier
sindB undX_x X_yverschiedene primitive Folgen, von denen die Grammatik nur eine
zulässt. GDT856 hatte bereits vor der Verwechslung von freier Mehrdeutigkeit
und kanonischer BPE-Lesbarkeit gewarnt. Dieser Grundsatz ist keine neue Entdeckung.

## Exakte Reichweite des23er-Ergebnisses

Die vorhandene NON_UD22_DEFECT_CONSEQUENCE_20261006 schließt unter ihren
Voraussetzungen jede nichttriviale feste Tabelle mit höchstens22Einträgen aus,
auch wenn eine Grammatik die erlaubten Codefolgen begrenzt. Die22Einzelzeichen
selbst bleiben möglich. Diese ursprüngliche Folge wird NICHT neu berechnet.

Die neue Konstruktion ist eine passende obere Grenze. Für tatsächliche Nutzung
des Zusatzcodes wähle ein verschiedenes Zeichenpaar, das inWvorkommt. Bereits
1235s alte Zweizeichen-Typzahlen63/75/67übersteigen jeweils die höchstens22
möglichen gleichen Doppelzeichen. Damit existiert ein solches Paar unter dem
alten Datenvertrag. Hier wird kein bestimmtes natives Paar als richtige
Spracheinheit gewählt und kein Manuskriptstring neu abgefragt oder ausgewertet.

## Was die Konstruktion nicht erklärt

Sie deckt JEDES mögliche Ausgabewort ab. Daher kann reine Formabdeckung diese
Klasse nicht anhand des Manuskripts auswählen: Sie würde ebenso gut beliebige
andere Texte oder bedeutungslose Zeichenfolgen zulassen. Es wurde keine
unabhängig festgelegte natürliche Quellsprache erzeugt, kein Wort übersetzt und
keine Häufigkeitsverteilung vorhergesagt. Ein deterministischer Wort-zu-Wort-
Bijektionsschreiber erhält weiterhin die Quellworthäufigkeiten;1202s feste
Quellfehlschläge werden dadurch nicht repariert.

Ein weiterer Codebuch-Solver für bloße23er-Abdeckung ist daher nicht sinnvoll.
Eine historische Lesung bräuchte eine unabhängig begründete Quellgrammatik und
gemeinsame Zeichenwerte mit prüfbaren Folgen. Diese fehlen weiterhin. Weder
Prefixfreiheit noch die freieUD-Annahme werden heimlich wieder eingeführt;
auch werden alte Prüfungen nicht nachträglich umgewertet.

## Prüfung

Registrierung und Code-Lock liegen vor dem kleinen Softwarelauf. Alle510
nichtleeren binären Ausgaben bis Länge8besitzen genau eine legale Quelllesung.
Alle608legalen Quellfolgen bis Länge6werden exakt zurückgewonnen;484illegale
Folgen werden abgewiesen. Ein separater dynamischer Parser zählt alle möglichen
Zerlegungen unter der Grammatik, statt den greedy Decoder zu importieren.
PASS betrifft diesen endlichen Softwarevergleich. Der obige allgemeine Beweis
trägt die Aussage beliebiger Länge; die Zahlen sind kein Manuskriptfortschritt.
Gleicher Autor, keine unabhängige natursprachliche Bestätigung.

```
python experiments/yolo/gdt1253_grammar_restricted_code_attainment/src/run.py
python experiments/yolo/gdt1253_grammar_restricted_code_attainment/src/validate.py
```

Keine native Rohdaten-, Bild-, Quellenkorpus- oder Reservenöffnung. f84/f84r
bleiben geschlossen. Source-free construction; lokaler Checkpoint, kein Push.
