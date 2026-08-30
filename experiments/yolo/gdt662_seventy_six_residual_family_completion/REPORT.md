# GDT662 — aus 76 Restformen wird ein gemischtes Rezeptregister

Status: `PASS_861_TARGET_POSITIONS__V39_MIXED_RECIPE_REGISTER`

## Ergebnis

Alle 76 durch GDT661 neu sichtbaren Restformen erhalten eine konkrete
Arbeitskarte. Damit werden 861 vorher offene Positionen in 776 Zeilen auf 160
Seiten geschlossen. Die 78 Ausgangszeilen sind sämtlich vollständig; global
entstehen 98 zusätzliche vollständige Mehrwortzeilen.

Der wichtige Fortschritt ist nicht bloß ein größeres Stoffverzeichnis. V39
liest einige sehr häufige kurze Formen erstmals als praktische Mikrohandlungen:

| Form | Vorkommen | V39-Default / praktischer Renderer | stärkster Rivale |
|---|---:|---|---|
| `qo` | 50 | `nimm Folgendes:`; zweimal zeilenfinal `nimm Vorstehendes` | Rezept-/Qualitätsrahmen |
| `qol` | 132 | `gib Folgendes hinzu:`; vor neuer Handlung `gib Vorstehendes hinzu` | Rezeptgrundlage/Trägerdroge |
| `qokol` | 88 | `erhitze Folgendes:`; vor Grad II–IV `erhitze bis Grad …` | heißes Drogenmaterial |
| `oly` | 53 | `seihe Vorstehendes ab` | Drogenmaterial in Grundform |
| `chl` | 28 | `trockne Folgendes:`; in zwei Rückbezügen `trockne die vorstehende …` | Trockengut oder verkürztes `chol` |
| `ey` | 14 | `anschließend:`; am Rand oder zwischen Trockenstoffen `mische …` | Mittelstufe |
| `a` | 9 | `je, zu gleichen Teilen` | davon/mit als Wertanschluss |
| `qodaiin` | 41 | Qualitätsgrad III | Ansatzdosis III |

`qodaiin` bleibt bewusst ein Wertwort: die sichtbare Reihe `qodain` (II),
`qodaiin` (III), `qodaiiin` (IV) ist stärker als ein zusätzlicher Imperativ.
Ebenso wird freies `qo` exakt gelernt; sein Verbwert wird nicht in gebundene
`qo-`-Formen exportiert.

## Architektur

| Kartentyp | Formen | Positionen | Anteil |
|---|---:|---:|---:|
| produktive Komposita | 61 | 741 | 86,1 % |
| gelernte Funktionswörter (`qo`, `a`, `ey`) | 3 | 73 | 8,5 % |
| gelernte Ganzwörter (`chl`, `far`, `los`, `cheyet`) | 4 | 36 | 4,2 % |
| exakte Hybrid-/Ausnahmekarten | 8 | 11 | 1,3 % |

Das kompositionelle Werkstattschema lautet:

`[Rahmen] + [Stoffkopf/gelernter Name] + [Behandlung] + [Stufe/Form] + [Menge] + [Abschluss]`

Die Stoffköpfe bleiben `p` Pulver, `s` Saat, `r` Wurzel, `l` Holz und `cth`
Blatt-/Krautdroge. `k/t` tragen heiß/kalt, `ch/sh` trocken/feucht, `o` eine
Zubereitungsfunktion; `ol/or/ar/al` tragen Stoff-, Portions- und
Rohstofffelder; `y/ey/eey` und die abgeschlossenen `d`-Gegenreihen liefern
Form-/Stufenunterschiede; `an/ain/aiin/aiiin` bilden Werte. Diese Zerlegung
erklärt und prognostiziert Familien, übersetzt aber niemals automatisch ein
Substring.

## Die dichte Front

Die 33 Formen mit mindestens fünf Vorkommen decken 792/861 Positionen:

| Form | n | konkrete V39-Arbeitslesung |
|---|---:|---|
| `qol` | 132 | Drogenstoff zugeben |
| `qokol` | 88 | erhitzen |
| `oly` | 53 | abseihen |
| `qo` | 50 | nehmen |
| `qodaiin` | 41 | Qualitätsgrad III |
| `choty` | 34 | kalter Trockenansatz |
| `shar` | 29 | angefeuchtete Drogenfraktion I |
| `chl` | 28 | trocknen |
| `qokeeey` | 27 | stark erhitzt, Endstufe III |
| `dchedy` | 26 | abgemessene Trockendroge, fertig |
| `oldy` | 25 | fertiger, abgeseihter Auszug |
| `dchy` | 22 | Dosis Trockendroge, Grundform |
| `olkedy` | 22 | erhitzte Drogenbasis, fertig |
| `tchor` | 21 | kalt-trockene Drogenportion |
| `ctho` | 18 | Krautansatz |
| `opchdy` | 18 | fertiges Trockenpulverpräparat |
| `tchol` | 16 | kalt-trockenes Drogenmaterial |
| `aral` | 15 | Rohdrogenfraktion I |
| `ey` | 14 | anschließend |
| `ydaiin` | 14 | davon drei Maße |
| `kair` | 11 | heiße Drogenfraktion II |
| `keeol` | 10 | stark erhitzter Drogenstoff |
| `pcheol` | 10 | getrockneter Pulverstoff |
| `a` | 9 | je, zu gleichen Teilen |
| `otoldy` | 9 | fertiger Kaltansatz |
| `choldy` | 8 | fertig getrocknete Droge |
| `dsheey` | 7 | abgemessene, vollständig angefeuchtete Droge |
| `shety` | 7 | feucht-kalt ansetzen |
| `oteeo` | 6 | zweiter Kaltansatz |
| `sham` | 6 | ein Maß Flüssigkeit |
| `ycheeo` | 6 | Eintrag: zweiter Trockenansatz |
| `lain` | 5 | Drogenholz, Charge II |
| `los` | 5 | Drogenholzposten |

Die restlichen 43 exakten Karten stehen vollständig in
`artifacts/TARGET_DECISION_DECK.tsv`. Besonders `far` und `cheyet` bleiben
gelernte Namensslots: `far` steht zweimal vor Menge III, `cheyet` nur im
Wurzel-Label `r cheyet`. Es wird keine Pflanzenart erfunden.

## Praktische Beispielzeilen

`f32r.8 — qo ar daiin dam`

> Nimm Folgendes: Drogenfraktion I; Grad-/Maßwert III; Dosis I.

`f22v.8 — qotchy cthy qokol daiin dam`

> Kalt und trocken am Gradanfang; Blatt-/Krautdroge; erhitze bis Grad III; Dosis I.

`f76v.41 — sol shey chedy qokedy chedy qol r aiin shedy`

> Samenmaterial; feucht bis zur Mittelstufe; trocken abgeschlossen; heiß
> abgeschlossen; nochmals trocken abgeschlossen; gib Folgendes hinzu: Wurzel, Menge III;
> feucht abgeschlossen.

`f78v.16 — lshey r shedy d qokedy okey lchedy qokdy daiin oly`

> Eingeweichtes Drogenholz, Form I; Wurzel; feucht abgeschlossen; Dosis; heiß
> abgeschlossen; heißer Mittelansatz; getrocknetes Drogenholz; heiß am
> Gradanfang abgeschlossen; Grad III; seihe Vorstehendes ab.

`f82r.33 — sain ol cheol ey cheor chey`

> Saatgut, Charge II; Drogenbasis; trockener Drogenstoff; mische Vorstehendes
> mit Folgendem: trockener Drogenteil; trocken bis zur Mittelstufe.

`f78r.19 — y ches aiin okeedy qokain chl`

> Eintrag: trockenes Drogenmaterial, Mittelstufe, Menge III; heißen Ansatz bis
> zur Endstufe abschließen; auf Grad II erhitzen; trockne.

Diese Fassungen bleiben knapp und teilweise listenartig, enthalten aber echte
praktische Information. Sie fallen nicht auf „Arbeitsgut nehmen, Arbeitsschritt
ausführen“ zurück.

## Warum die Handlungskarten derzeit führen

- `qokol` steht 10-mal am Zeilenanfang, 78-mal medial und nie am Zeilenende.
  Acht direkte Gradkontakte ergeben einmal Grad II, sechsmal Grad III und
  einmal Grad IV; zwei echte Doppelungen werden als „erhitze zweimal“ bewahrt.
- `oly` endet 36/53-mal eine Zeile, während freies `ol` nur 42/463-mal am Ende
  steht. Nur ein sichtbares `ol | y` existiert. Das macht das gelernte
  „seihe ab“ derzeit informativer als eine bloße Grundform.
- `chl` steht 27/28-mal medial; rechts folgen unter anderem fünfmal `l`,
  dreimal `s` und zweimal `ol`, plausible Objekte von „trockne“.
- `qol` ist stark registergebunden (130/132 Sprache B). Sein praktischer
  Ganzwortrenderer wird deshalb ausdrücklich nicht als universelle Bedeutung
  von `q`, `o` oder `l` behandelt. Die vier sichtbaren Folgen `qol qol`
  klammern je einen linken und einen rechten Stoff: „gib Vorstehendes hinzu;
  gib Folgendes hinzu“.
- `ey` ist 12/14-mal medial. V39 wählt dort den robusten Sequenzwert
  „anschließend“. Der einmalige Anfang, das einmalige Ende und der eine
  Trockenstoff–`ey`–Trockenstoff-Kontext erhalten den praktisch stärkeren
  Renderer „mische …“.

## Abdeckung

| Größe | V38 | V39 | Änderung |
|---|---:|---:|---:|
| bekannte Tokenpositionen | 18.451 | 19.312 | +861 |
| unbekannte Tokenpositionen | 13.888 | 13.027 | −861 |
| vollständige Mehrwortzeilen | 233 | 331 | +98 |
| davon dreileser-streng | 99 | 125 | +26 |
| Ein-Loch-Zeilen | 290 | 302 | +12 netto |
| davon dreileser-streng | 73 | 67 | −6 netto |
| Glossaroberflächen | 556 | 632 | +76 |
| Wörterbucheinträge | 678 | 785 | +107 |

667/861 Zielpositionen sind in allen vorhandenen Leserfassungen exakt dasselbe
Token; die konservative Split-Normalisierung erreicht 682. Alle 31.478
Nichtzielpositionen bleiben in Glosse, Quelle und Scope unverändert. Zwei
manuelle Re-Audits geben nach den Anschlusskorrekturen GO; der unabhängige
source-first Validator besteht 125 Prüfungen samt bytegleichem 19-Dateien-
Tempdir-Replay. Die konkreten Korrekturen stehen in
`MANUAL_PASSAGE_AUDIT.md`.

## Nächste Front

V39 exponiert 105 neue Ein-Loch-Zeilen mit 102 verschiedenen Restformen und
zusammen 1.105 geerbten Vorkommen. Die dichte Spitze lautet `l` 163, `chody`
78, `char` 75, `shody` 46, `olaiin` und `ytaiin` je 39, `lkain` 33,
`chedaiin` 32, `chedar` 31 und `olkaiin` 28. GDT663 kann diese Front mit dem
jetzt sichtbaren Aktions-/Stoffkontrast schließen, ohne eine neue Seite zu
öffnen.

## Historische Ähnlichkeit, nicht Identifikation

Spätmittelalterliche Rezeptbücher verbinden Rezeptzeichen und Maßkürzel mit
gelernten Pflanzen-/Drogennamen und ausgeschriebenen Herstellungsangaben. Als
zeitnahe Vergleichspunkte dienen etwa [Wellcome MS 5262](https://wellcomecollection.org/works/hkxxeu85),
[Wellcome MS 683](https://wellcomecollection.org/works/w6ne7k4t) und
[Wellcome MS 418](https://wellcomecollection.org/works/f6nzyzh4). Eine
[Untersuchung spätmittelalterlicher medizinischer Kürzel](https://reunido.uniovi.es/index.php/SELIM/article/download/13301/12036/28090)
dokumentiert getrennte Kürzeltypen unter anderem für Rezeptbeginn, *ana* und
Maße. Das macht ein Mischregister historisch plausibel; es beweist ausdrücklich
nicht, dass Voynich-`qo`, `a` oder `ey` diese lateinischen Zeichen darstellen.

## Aussagegrenze

V39 ist eine aggressive, ersetzbare Arbeitsübersetzung. Sie bestätigt weder
eine Sprache noch eine historische Klartextzeile. Die Handlungen „nehmen“,
„zugeben“, „erhitzen“, „trocknen“ und „abseihen“ sind die derzeit praktisch
besten Ganzwortlesungen, keine entzifferten Lexeme. Die Karte darf stehen
bleiben, bis eine bessere Lesung mehr Schwesterformen und Passagen zugleich
erklärt oder ein klarer Konflikt sie unmöglich macht.
