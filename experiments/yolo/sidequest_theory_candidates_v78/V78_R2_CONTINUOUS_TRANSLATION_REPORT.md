# V78 R2 — historische kontinuierliche Prosaausgabe

## Ergebnis

Die unabhängige R2-Ausgabe deckt **381/381 Ereignisse genau einmal**, alle
**116 Aussagen** und alle **11 Prosarecords H1–H5/B1–B6** ab. Die physische
Zeile ist nirgends Satzgrenze: 18 Aussagen mit 129 Ereignissen laufen über
mindestens eine Zeile weiter. Zehn sichtbare Stationswechsel in B2–B4 setzen
hingegen Besitzer, Stoff, Ziel und Richtung ausdrücklich zurück.

Die Ausgabe besitzt zwei streng getrennte Schichten:

1. die Literal-Schicht mit anonymer Karten-ID und ausschließlich dem
   V77-Status `ET?`, `PER?`, `[FORMAL:…; KEIN WORT]` oder
   `[EXEMPLARWERT UNBEKANNT]`;
2. eine flüssige deutsche Quellenausweitung, deren **gesamter Inhalt** in
   `[EXEMPLAR:…]` steht.

Damit ist der lesbare Text eine historisch plausible Arbeitsedition, keine
Entzifferung und kein Wörterbuch. Pflanzenart, Wasser/Wein, Dosis, Indikation,
Badende, Beckenfunktion, Richtung und Handlung bleiben source-lokale
Exemplarinhalte. Die elf vollständigen Lesungen stehen in
`V78_R2_11_CONTINUOUS_RECORDS.tsv`; die vollständig eventgebundene
Literal-plus-Quellenfassung steht dort in einer eigenen Spalte.

## Wörterbuchdisziplin

| Karte | V78-Ausgabe | Vorkommen | Ergebnis der Syntaxprobe |
|---|---:|---:|---|
| `dcda95c81a5460feb191` | `ET? (UND/AUCH?)` | 19/19 | 9 mediale Verknüpfungen, 8 Glieder in wiederholten Ketten, 2 additive Aussageanfänge; kein harter Syntaxbruch |
| `b5fcea1eaed06b2f2291` | `PER? (DURCH/GEMÄSS?)` | 9/9 | 7 nur mit unmittelbar folgender Ergänzung möglich; E180/E181 bilden einen harten `PER? PER?`-Bruch vor nur einer Ergänzung |
| `2f1c5e56e8f0ff459065` | `[FORMAL:VORGABEPARAMETER?; KEIN WORT]` | 20/20 | nur formaler Kanal |
| `308e8ea2d5d190c498e8` | `[FORMAL:LOKALEN_RELATIONSSLOT_SETZEN; KEIN WORT]` | 6/6 | nur formaler Kanal |
| alle übrigen Karten | `[EXEMPLARWERT UNBEKANNT]` | 327/327 | kein portabler Wortwert |

Keiner der zurückgezogenen V69/V73/V74-Werte MASS, ANWENDEN, BEREIT,
ANSATZ, ZIEL, KLAR, VORIGES, ANTEIL, TEMPERIEREN, SPÜLEN oder ABLASSEN
erscheint wieder als Kartenwert. Solche Handlungen dürfen nur innerhalb einer
eckig geklammerten Quellenausweitung vorkommen.

## Historische Formularsyntax

Die Quellen wurden nur zur **Gattungs- und Syntaxkontrolle** herangezogen. Sie
attestieren keine Voynich-Karte.

- Das nordostitalienische [Wellcome MS.683](https://wellcomecollection.org/works/w6ne7k4t)
  ist ein von mehreren Händen geschriebenes Receptarium der Mitte des
  15. Jahrhunderts; es enthält `Recipe … et …`-Folgen und vor 1445 datierte
  Antidotarium-Auszüge. Das stützt lange rezeptartige Quellenglieder und
  Kompilation, nicht unsere konkreten Stoffe.
- Das [Rheinfränkische Kochbuch um 1445](https://www.uni-giessen.de/de/fbz/fb05/germanistik/absprache/sprachverwendung/gloning/tx/rfk.htm)
  und die institutionelle [CoReMA-Edition B2](https://gams.uni-graz.at/o%3Acorema.b2.recipes)
  zeigen, dass ein spätmittelalterlicher Rezeptgang viele imperative Glieder
  durch wiederholtes `vnd` verbinden kann; physische oder moderne
  Satzsegmentierung ist dafür kein notwendiger Abschluss.
- Die mittelalterliche Antidotarium-Formel `colentur per pannum` in der
  [Edition des Antidotarium Nicolai](https://www.dbnl.org/tekst/_ant004wsva01_01/_ant004wsva01_01.pdf)
  zeigt den entscheidenden Prüfmechanismus für `PER?`: `per` regiert eine
  Ergänzung. Es ist kein freier allgemeiner „Arbeitsgang“-Marker.
- Die c.1414-Codebook-Belege `et` und `per` bleiben ausschließlich die in V77
  gefrorenen Fi1-Kategorien (Aloys Meister, *Die Anfänge der modernen
  diplomatischen Geheimschrift*, 1902, S. 49–50; Archivio di Stato di Firenze,
  *Chiavi delle cifre* II, Pars 3, Nr. 1). Keine Rezeptquelle wird als zweite
  Attestation einer Voynich-Lesung gezählt.

### `ET?`

`ET?` benötigt keinen eigenen Inhaltswert. In H2 bildet E027/E029 tatsächlich
die lesbare Struktur

> `[EXEMPLAR:eine Handvoll] ET? [EXEMPLAR:den vorherigen Posten] ET? [EXEMPLAR:von beiden das gleiche örtliche Maß]`

Die vergleichbaren Doppelketten in B1, B5 und B6 sind als additive
Quellenglieder formulierbar. E121 und E295 stehen am Anfang einer formalen
Aussage, setzen jedoch ohne Bildbesitzerbruch den unmittelbar vorigen
Arbeitsgang fort; sie sind deshalb schwächer, aber nicht syntaxwidrig. Das
Ergebnis hält `ET?` **syntaktisch möglich**, bestätigt aber weder Sprache noch
Bedeutung.

### `PER?`

R2 gibt `PER?` nirgends die alte Bedeutung „Standardslot setzen“. Jedes
Vorkommen bleibt dieselbe fragliche Präposition und muss das folgende
Quellenglied regieren. So sind beispielsweise nur bedingt lesbar:

- E056 `PER? [EXEMPLAR:das örtlich vorgeschriebene Maß]`;
- E102 `PER? [EXEMPLAR:den zurücklaufenden Strom]`;
- E219 `PER? [EXEMPLAR:warmes Wasser]`;
- E243 `PER? [EXEMPLAR:Rühren bis zur Gleichmäßigkeit]`.

E180/E181 ergeben dagegen:

> `… [EXEMPLAR:durch die verbundenen Läufe] PER? PER? [EXEMPLAR:dieselbe örtliche Einstellung] …`

Für zwei Präpositionen steht nur eine Ergänzung zur Verfügung. Eine
Sonderbedeutung, Polysemie oder unsichtbare zweite Ergänzung würde die Probe
retten, ist aber nicht erlaubt. Beide Ereignisse sind deshalb als
`HARD_SYNTAX_BREAK__CONSECUTIVE_PER_PER_SINGLE_COMPLEMENT` ausgewiesen. Unter
einem strengen „ein portables Wort muss überall dieselbe Formularfunktion
haben“-Kriterium steht `PER?` damit unter **Rückzugsdruck**; es darf aus dieser
Runde nicht befördert werden.

## Quellenausgabe und Widersprüche

- H1–H5 folgen als kreative Standardausweitung dem Artikel-/Receptariumgang
  Bildpflanze → Teil/Charge → Bereitung → Gebrauch/Aufbewahrung. Jede konkrete
  Auswahl bleibt geklammert; keine Pflanze wird benannt.
- B1–B6 folgen lokalen Stationsartikeln. Nur ein wirklich sichtbarer
  Stationswechsel setzt den Quellenbesitzer zurück. Nacktheit allein bedeutet
  weder Patientin noch Therapie; eine Rinne beweist weder Richtung noch
  Kreislauf.
- Die 116-zeilige Datei `V78_R2_SOURCE_ORDER_CONTRADICTIONS.tsv` nennt für jede
  Aussage Quellenklasse, Eigentümerfolge, Linienübergang, ET/PER-Syntax,
  stärksten Rivalen, Reparaturkosten und härtesten Bildwiderspruch.
- Eine kontinuierliche Lesung darf über Zeilen laufen, aber nie über einen
  unverbundenen Bildbesitzerbruch hinweg Stoff oder Richtung erben.

## Artefakte und Prüfung

- `V78_R2_381_EVENT_INTERLINEAR.tsv`
- `V78_R2_11_CONTINUOUS_RECORDS.tsv`
- `V78_R2_SOURCE_ORDER_CONTRADICTIONS.tsv`
- `V78_R2_RESULT.json`
- `build_v78_r2_continuous_translation.py`
- `validate_v78_r2_continuous_translation.py`
- `V78_R2_VALIDATION.json`

Der Validator meldet `PASS`: 381 eindeutige Ereignisse, 116 Aussagen, elf
Records, 19 feste `ET?`- und neun feste `PER?`-Vorkommen, genau zwei gefrorene
PER-Syntaxbrüche, nur zwei portable Wörter, beide Formalprompts überall als
Nichtwörter und alle Inhalts-/Besitzerausweitungen geklammert. `f84` und `f84r`
blieben vollständig versiegelt.

## Interpretationsgrenze

Dies ist eine absichtlich kreative, historisch kalibrierte Werkstattausgabe.
Sie etabliert weder Karten-, Stamm-, Laut- noch Sprachwerte und weder Medizin,
Balneologie noch Übersetzung. Der stärkste neue Befund ist rein intern:
`ET?` übersteht die Formularsyntaxprobe; `PER?` tut dies wegen E180/E181 nicht
bruchfrei.
