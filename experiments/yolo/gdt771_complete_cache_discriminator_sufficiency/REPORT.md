# GDT771 — Der vorhandene Cache füllt den fehlenden `ol`-Zweig

## Ergebnis

Der bereits vorhandene Vollzeilen-Cache enthält genug unterschiedliche
Kontexte, um den in GDT770 völlig unbelegten linken `ol`-Zweig in der nächsten
Runde wirklich zu testen:

| Frage | Strenges Ergebnis | Folgerung |
|---|---:|---|
| Menge/Wert direkt links von `ol` | 14 Vorkommen, 12 Zeilen, 9 Seiten | der linke Zweig ist klar vorhanden |
| zusätzlich reader-exakte Zelle rechts | 11 Vorkommen, 7 Seiten | das Muster ist meist nicht bloß zeilenfinal |
| zusätzlich rechts eine von GDT770 erlaubte Rolle | 7 Vorkommen, 7 Zeilen, 6 Seiten | der ganze `von/aus`-Relatorzweig ist score-fähig |
| finales `ckhy` mit Patient links | 1 Vorkommen, 1 Seite | die zweite unabhängige Mischstelle fehlt |
| `ols` direkt vor Wert in vollständiger Zeile | 1 Vorkommen, 1 Seite | Produkt gegen Siebvorgang bleibt offen |
| allgemeine `otar`-Folge | 5 Vorkommen, 4 Seiten | brauchbarer Anzeigelead |
| nominales `otar`-Feld | 3 Vorkommen, 3 Seiten | bleibt ein echter Rivale |
| `otar` vor rechtem Endpunkt | 1 Vorkommen, 1 Seite | `bis` ist lokal möglich, aber nicht repliziert |

Das ist ein praktischer Fortschritt gegenüber GDT770: Dort scheiterte die
stärkste `ol`-Policy allein daran, dass ihr ausdrücklich vorgesehener linker
Zweig kein einziges Mal vorkam. Diese Kapazitätslücke ist nun geschlossen.
Die Runde behauptet noch nicht, dass `ol` tatsächlich *von* oder *aus*
bedeutet; sie liefert die Kohorte, in der dieser Kandidat erstmals fair gegen
`Ansatz/Basis` und `Produkt/Resultat` antreten kann.

## Die sieben vollständigen `ol`-Brücken

Die score-fähigen lokalen Geometrien sind:

1. `f112r.36`: `sain → ol → checkhy`, rechts `PREPARATION`;
2. `f30v.2`: `keor → ol → chy`, rechts `FIELD`;
3. `f75r.26@2`: `dain → ol → sheol`, rechts `PREPARATION`;
4. `f81r.15`: `sain → ol → cheedy`, rechts `PREPARATION`;
5. `f81r.22@8`: `chedar → ol → oly`, rechts `PROCESS|FIELD`;
6. `f82r.33`: `sain → ol → cheol`, rechts `PREPARATION`;
7. `f85r1.21`: `oraiin → ol → okaiin`, rechts `FIELD|PREPARATION`.

Die Pfeile zeigen Strukturkontakte, keine gelesenen Wörter. Getrennte
Mengenspans werden als eine linke Einheit behandelt; derselbe Fall wird nicht
noch einmal als nackter Wert gezählt. Vier rechte Rollenübernahmen stammen aus
schon verwendeten target-unabhängigen Ganzwortrollen, nicht aus der erhofften
`ol`-Lesung.

Der Audit hat zugleich eine frühere Zählfalle beseitigt:
`f81r.22@ol6` besitzt rechts `AMOUNT_VALUE|QUALITY_STAGE`, aber der linke
Mengen-Zweig von GDT770 verlangt rechts ein Stoff-, Quellen-, Patienten-,
Prozess-, Feld-, Resultat-, Endpunkt- oder Produktfeld. Dieser Fall zählt daher
nicht zu den sieben vollständigen Brücken.

Alle lokalen Funde und ihre getrennten Zulassungsstufen stehen in
[OL_LEFT_BRANCH_ATLAS.tsv](artifacts/OL_LEFT_BRANCH_ATLAS.tsv). Die acht
Schwellenentscheidungen stehen in
[DISCRIMINATOR_SUMMARY.tsv](artifacts/DISCRIMINATOR_SUMMARY.tsv).

## Was bei `ckhy` und `ols` fehlt

Im vollständigen exakten Bestand gibt es sechs finale `ckhy`-Positionen. Nur
`f17v.5` besitzt die gesuchte Patientenstütze; keine zweite Seite wiederholt
sie. Finalposition allein wird deshalb nicht als Beleg für *mischen* gezählt.

Bei `ols` existieren drei exakte rechte Wertkontakte:

- `f104v.19` ist vollständig und schon aus GDT770 bekannt;
- `f83r.10` besitzt drei offene Vollzeilenzellen;
- `f99v.21` ist der stärkste neue lokale Kontrast, weil links eine unabhängig
  markierte Zubereitung und rechts ein Wert steht, doch sechs andere Zellen der
  Zeile bleiben offen.

`f99v.21` macht eine Produkt-/Resultatlesung interessanter als einen reinen
Siebvorgang, darf aber seine sechs offenen Zellen nicht selbst schließen. Im
strengen Vollzeilenbestand bleibt es deshalb bei 1/1.

## `otar`: ein Lead, kein gelöstes Wort

Unter den geerbten GDT769-Prädikaten enthält die Folgenmenge alle drei
Nominalfälle und zwei zusätzliche Fälle. Das rechtfertigt `dann/weiter?` als
knappe Arbeitsanzeige. Es eliminiert die nominale Lesung
`Zwischenzubereitung` nicht, weil die Übermengenrelation von genau diesen
Prädikaten abhängt.

Außerdem war die frühere Nullangabe für den terminativen Kandidaten falsch:
`f75r.43@6` besitzt in GDT770 links ein Material-/Patientenfeld und rechts ein
`RESULT|ENDPOINT|CLOSE`-Feld. Das ist ein echter lokaler `bis`-kompatibler
Fall. Eine zweite physisch unabhängige Seite fehlt, während mehrere andere
`otar`-Stellen die umgekehrte Richtung oder einen Prozess rechts zeigen.
Darum bleibt `bis zum Endzustand` ein lokaler Rivale und keine portable
Standardbedeutung. Der Mengenvergleich ist in
[OTAR_IDENTITY_COVERAGE.tsv](artifacts/OTAR_IDENTITY_COVERAGE.tsv) vollständig
sichtbar.

## Cache- und Ausschlussbilanz

Die Guard-Abfrage materialisierte 461 der ausdrücklich erlaubten GDT734-Loci
und null `f84*`-Zeilen. Die zweite Guard-Abfrage materialisierte 46 passende
GDT760-Mengenzeilen und ebenfalls null verbotene Zeilen. Aus 176 zugelassenen
Loci mit 203 Zielvorkommen bleiben nach den zeilenweiten Ausschlüssen 195
strenge Zielvorkommen.

Fünf neu explizierte Ausschlüsse betreffen vollständige Zeilen, deren geerbter
Reader noch zurückgezogene Hauptwort- oder Quellkompositionsprosa enthält:
`f103v.40`, `f34r.14`, `f77v.23`, `f78v.12` und `f86v6.23`. Ihre lokalen
Kontakte bleiben im Atlas sichtbar; sie tragen nur nicht den End-to-End-Score.

GDT771 erzeugt keine neue Relationsevidenz. Es filtert und kombiniert bereits
geerbte Textnachbarschaften aus GDT769/GDT770; deshalb ist kein neuer
GDT388-Edge-Packet entstanden.

## Nächster Schritt

GDT772 sollte die sieben vollständigen `ol`-Brücken samt Richtungs- und
Finalkontrollen aktuell rendern, alle `ol/ckhy/ols/otar` derselben Zeile
gleichzeitig maskieren und das unveränderte GDT770-Kandidatendeck neu scoren.
Damit bekommen wir eine echte Antwort auf die nächste Frage: Erklärt ein
positionales `ol` als `von/aus`, `mit` oder `und` die Nachbarkanten sparsamer
als ein nominaler Ansatz oder ein messbares Produkt?

Die fehlende zweite `ckhy`-Patientenfinale und die fehlende zweite vollständige
`ols`-Wertzeile bleiben konkrete Suchaufträge für das nächste freigegebene
Vierseitenpaket. Sie werden nicht durch weitere gleichartige Cachezeilen
ersetzt.

## Behauptungsgrenze und Reproduktion

Der unabhängige Validator wiederholte beide Guard-Abfragen, berechnete die
drei `ol`-Mengen separat, bestätigte `f75r.43@6` als einzigen strengen
`otar`-Endpunkt und reproduzierte alle neun Runner-Ausgaben bytegenau.
[VALIDATION.json](artifacts/VALIDATION.json) meldet PASS.

GDT771 bestätigt null Lexeme, null Klartextklauseln und null
Komponentenwerte. Es öffnet keine neue Seite, kein Bild, keine OCR und keine
Transkription. Die konkreten deutschen Anzeigen bleiben ausdrücklich
ersetzbare Arbeitsdefaults.
