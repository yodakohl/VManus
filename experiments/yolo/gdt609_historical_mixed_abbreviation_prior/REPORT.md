# Historische Vergleichsschiene für einen 34-Basis-Kompositionsdecoder

Stand: 2026-08-28
Status: **`HISTORICAL_MIXED_ABBREVIATION_FST_34_V1_SELECTED`**; keine historische Identifikation und keine semantische Deutung.
Arbeitsgrenze: GDT607/GDT608-Formrollen plus veröffentlichte historische
Vergleichsquellen; keine neue Zieldecodierung und kein Zugriff auf f84/f84r.

## Ergebnis in einem Satz

Der belastbarste Decoderprior ist **kein flacher Nomenklator und kein
„alchemistisches Alphabet“**, sondern eine lateinisch-spätmittelalterliche
Abbreviaturgrammatik aus erhaltenen Trägerzeichen, gebundenen Präfix-/Suffix-
und Kontextzeichen sowie wenigen Fach-Ganzformen; für Rezepttexte kommt ein
kleiner, separat bepreister `Recipe`/`ana`/Maß-Makrolayer hinzu. Kurz:
allgemeine Abbreviatur-FST plus kleiner Rezept/Medizin-Layer. Das hier
vorgeschlagene 34-Slot-Profil ist eine nachvollziehbare technische
Regularisierung dieser Evidenz, nicht ein historisch belegtes 34-Zeichen-
Codebuch.

Die drei Einsatzstufen sind daher:

1. `CORE_GRAMMAR`: allgemeine spätmittelalterliche Abbreviatur-FST;
2. `DOMAIN_OVERLAY`: wenige medizinisch-rezeptarische Ganzformen und Maße;
3. `CAPACITY_AND_NULL_CALIBRATOR`: Tranchedini nur für Größenordnungen von
   Buchstaben-/Silben-/Wort-/Nullklassen, ausdrücklich nicht für die
   Kompositionsregel.

## Struktureller Prüfmaßstab

Die Vergleichskandidaten wurden nur gegen die bereits öffentlich fixierten
Formrollen bewertet, nicht gegen Zeichenähnlichkeit oder vermutete Bedeutung:

| Einheit | gehaltene Formbeobachtung | im Modell zu prüfende Rolle |
|---|---:|---|
| `C` | chunk-initial 0.6934; chunk-final 0.0056 | strikter lokaler Opener/Präfix |
| `d` | chunk-initial 0.4992; line-initial 0.1759 | Opener oder Kopfträger |
| `y` | chunk-final 0.6390; line-final 0.2347 | Suffix-/Schlussoperator |
| `o` | initial 0.3120; final 0.2989; middle 0.4154 | flexibler Connector, nicht nur intern |
| `ol` | chunk-final 0.5463; standalone 0.1433 | Connector+Suffix oder Boundary-Makro |

Die qok-Gegenklasse ist ein zwingender Schutz gegen eine falsche
Standalone-Heuristik: `qokaI`, `qokaN`, `qokEdy`, `qokedy`, `qokEy` haben im
Held-Split Standalone-Raten von 1.0000, 0.9444, 0.9714, 0.9839 und 0.9776,
aber jeweils 0/36 W-Zuweisungen. Hohe Standalone-Rate darf daher weder
„Ganzwort“ noch lange Ausgabe erzwingen.

Lokale Evidenzbasis:
`experiments/yolo/gdt607_boundary_word_disentanglement/artifacts/role_attack/REPORT.md`.
Die Kandidatenscores sind vergleichende, vorab definierte Ordinalwerte von
0 (keine Unterstützung) bis 3 (starke direkte Unterstützung), keine
Signifikanztests.

## Kandidatenraster

| Rang nach Formfit | Kandidat | Komposition / 34-Fit | C/d | y | o | ol | qok | Formfit /15 | Urteil |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Medizin/Rezept | 3 / 2 | 3 | 3 | 2 | 3 | 3 | 14 | `DOMAIN_OVERLAY` |
| 2 | allgemeine Abbreviatur | 3 / 2 | 2 | 3 | 2 | 2 | 3 | 12 | `CORE_GRAMMAR` |
| 2 | notae iuris/notariell | 3 / 2 | 2 | 3 | 2 | 2 | 3 | 12 | alternative Fachschicht |
| 4 | Handel/Rechnung | 1 / 1 | 1 | 1 | 1 | 2 | 2 | 7 | nur Einheiten-Layer |
| 5 | griechische Tachygraphie 1364 | 2 / 1 | 1 | 1 | 1 | 1 | 2 | 6 | Auditkandidat |
| 5 | Mensuralnotation | 3 / 1 | 2 | 0 | 1 | 1 | 2 | 6 | formaler FST-Vergleich |
| 7 | diplomatischer Nomenklator | 0 / 1 | 0 | 0 | 0 | 1 | 3 | 4 | nur Kapazitätskalibrierung |
| 8 | lateinisch-westliche Alchemiesymbole | 0 / 0 | 0 | 0 | 0 | 1 | 1 | 2 | als Decoderprior verwerfen |

Das vollständige, maschinenlesbare Raster steht in `candidate_grid.tsv`;
Quellen, Seitenstellen, Evidenzparaphrasen, kurze Belegfragmente und
Limitierungen stehen in `source_evidence.tsv`.

## Quellenbefund nach Systemfamilie

### 1. Allgemeine spätmittelalterliche Abbreviatur: stärkster Kern

Die Zürcher Paläographie-Einführung unterscheidet für Hoch- und
Spätmittelalter Silbenkürzung, Suspension, Kontraktion und Sonderzeichen.
Der Nasalstrich ergänzt typischerweise `m` oder `n`, ein r-Zeichen kann je
nach Kontext `re`, `ir`, `ri`, `r` oder `e` expandieren; häufige Zeichen
werden ausdrücklich für Präfixe und Suffixe benutzt. Zugleich war das System
regional und schreiberspezifisch, also kein einheitliches Codebuch
([Ad fontes, Abschnitte Methods/Forms](https://www.adfontes.uzh.ch/en/tutorium/schriften-lesen/abkuerzungen)).

Der besonders wertvolle datierte Fall ist Dresd.Od.83, ca. 1400. Vier
hochgestellte Buchstaben repräsentieren sieben Buchstabenfolgen; ein
hochgestelltes `t` steht kontextabhängig für `at`, `ut`, `ot` oder eine
weitere Folge und ist ausschließlich wortfinal. Die Studie trennt zudem
Ganzwortabbreviaturen ausdrücklich von Zeichen für Buchstabenfolgen
([Grzybowska 2018, DOI 10.31743/lingbaw.5665](https://doi.org/10.31743/lingbaw.5665),
S. 52-53 und 56-61).

Das ist fast genau die benötigte abstrakte Architektur: derselbe kleine
Zeichenvorrat hat Träger-, gebundene und kontextuelle Rollen; kurze
Expansionen und Ganzformen koexistieren. Nicht belegt sind dagegen exakt 34
Grundzeichen oder eine universelle Schlüsselbelegung.

### 2. Notae iuris/notarielle Fachschicht: Mechanismus plausibel, Kapazität offen

Die juristische Tradition kombiniert einfache und silbische Suspension,
Kontraktion, tironisch abgeleitete und konventionelle Zeichen. Die Beispiele
unterscheiden unter anderem `cum`, `post`, `beneficio`, `omnia`, `per` und
`pro` ([UBTERM, „notae iuris“](https://www.ub.edu/ubterm/terme/notae-iuris/)).
Das unterstützt produktive Präfix-/Formelrollen und wenige Fach-Ganzformen.
Es liefert aber kein lokales spätmittelalterliches 34-Zeichen-Inventar; der
notarielle Kandidat ist deshalb eine Domänenschicht über derselben
Abbreviaturgrammatik, kein unabhängiger Decoder.

### 3. Medizinische Rezepte: stärkste Fachschicht

Die Korpusstudie zu mittelalterlichen medizinischen Handschriften belegt
Kontraktionen, Nasal-/Endstriche und Brevigraphen für `per/par/pre/pro`,
r-Cluster sowie Endungen wie `-us`, `-ur` und `-is/-es`. Daneben gibt es
medizinische Ganzzeichen für `Recipe`, `ana`, Handvoll und mehrere Gewichts-
und Maßeinheiten
([De la Cruz-Cabanillas & Diego-Rodríguez 2019](https://reunido.uniovi.es/index.php/SELIM/article/view/13301),
S. 169-180).

Damit sind drei Ebenen direkt belegt:

- kurze gebundene Ausgaben von 1-3 Buchstaben;
- formale Rezeptslots wie Kopf/Connector/Einheit;
- wenige normalisierte Ganzformen von etwa 3-11 Buchstaben.

Die Evidenz ist stark, aber domänenspezifisch und überwiegend aus
fünfzehntem-Jahrhundert-Zeugen, von denen einige nach 1450 liegen. Sie darf
daher einen kleinen Overlay-Prior, nicht die Zielsemantik liefern.

### 4. Tachygraphie 1364: periodengenau, aber kein 34-Kapazitätsbeleg

Vatican Regina 181 wurde 1364 geschrieben und enthält medizinische Texte,
Passagen, in denen der Schreiber von Normalschrift in Tachygraphie wechselt,
zusammenhängende Kurzschrift und eine formale Tabelle von Zeichen und ihren
Lesungen. Genannte Lesungen umfassen Silben beziehungsweise kurze Wörter
([Allen, Journal of Hellenic Studies 11, DOI 10.2307/623435](https://doi.org/10.2307/623435)).
Das ist ein echter periodengleicher Mixed-Mode-Beleg. Die zugängliche
Evidenz quantifiziert aber weder einen kompakten Grundzeichenvorrat noch die
benötigte Präfix-Core-Suffix-Grammatik. Deshalb nur Auditkandidat.

### 5. Diplomatischer Nomenklator: exakter Klassenvergleich, falsche Architektur

Domnina rekonstruiert mit einem archivierten Teilklartext ein frühes
Tranchedini-System. Der Artikel nennt **81 Zeichen** und gliedert sie in 36
Buchstaben, 4 Doppelbuchstaben, 1 Null, 30 Silben und 11 Wörter
([Domnina 2018, S. 4-5](https://ep.liu.se/ecp/149/007/ecp18149007.pdf)).
Diese veröffentlichten Teilzahlen summieren sich allerdings zu **82**, nicht
81. Der Widerspruch ist im Modell nicht stillschweigend „repariert“; die
Zahlen werden nur als ungefähre Klassenkapazität verwendet. Zusätzlich stammt
der entschlüsselnde Parallelzeuge vom 11. März 1454, also knapp außerhalb des
strikten Fensters, während der untersuchte Brief in die 1440er datiert wird.

Ein späteres, vollständig summierendes Profil umfasst 253 Zeichen:
55 Buchstaben, 12 Doppel, 8 Nullen, 65 Silben und 113 Wörter. Beide Profile
stützen die Existenz gemischter Ausgabegrößen und sparsamer Nullen. Sie sind
aber flache Substitutionswörterbücher; Präfix, Suffix und Connector entstehen
nicht produktiv aus 34 Basen. Dies ist deshalb ein Kalibrator und ein harter
Negativtest für den Kompositionsdecoder.

### 6. Alchemie: historisch nah, positive 34-Zeichen-These widerlegt

Barbara Obrists Überblick stellt fest, dass symbolische Zeichen, anders als
in griechischer Alchemie, im lateinischen Westen vom 12. bis 15. Jahrhundert
sporadisch blieben. Frühe Beispiele umfassen einzelne Metall-/Planetzeichen,
Schwefel/Arsen, Punkte, Kreise, magisch ähnliche Formen und Buchstaben;
lokale Praxis und Vokabular variierten stark
([Obrist 2003, S. 134-136](https://hyle.org/journal/issues/9-2/obrist.pdf)).

Ein digitalisiertes norditalienisches Mischmanuskript, ca. 1450-1475,
bestätigt die reale Mischung aus lateinisch/italienischem Text, praktischen
Rezepten und Instrumentzeichnungen
([Science History Institute, MS 2](https://digital.sciencehistory.org/works/3arao9u)).
Es belegt aber gerade kein dichtes produktives Symbolalphabet. „Alchemie“ ist
daher eine mögliche Inhaltsdomäne, nicht die gesuchte Kompositionsarchitektur.

### 7. Mensuralnotation: nützlicher formaler Kontrollfall

Im frühen 14. Jahrhundert zeigten Stückanfangszeichen, wie fünf
Notendauern binär oder ternär zu zerlegen waren
([Busse Berger 1997](https://www.persee.fr/doc/medi_0751-2708_1997_num_16_32_1379)).
Bei Ligaturen wirken Zeichenform, Stammrichtung, relative Position und
Nachbarn gemeinsam auf die Rhythmusfolge
([Universität Basel, Ligatures](https://tales.nmc.unibas.ch/de/from-ink-to-sound-32/early-mensural-notation-190/ligatures-as-rhythmic-figures-the-pre-franconian-ligatures-969)).
Das beweist, dass ein mittelalterlicher, positionssensitiver
Feature-Kompositionsautomat historisch normal sein kann. Seine Ausgaben sind
aber Dauern, nicht Buchstaben/Silben/Wörter; er gehört nur in die
Software-Kalibration der FST, nicht in den Sprachprior.

### 8. Kaufmännische Kürzel: Maße ja, autonome Zeichensprache nein

Ad fontes nennt gerade Münzen, Maße und Gewichte als häufige Ganzkürzel in
Geschäftsschrift. Für die Datini/di-Berto-Rechnungsbücher von 1367-1373 zeigt
Arlinghaus jedoch, dass Posten in ganzen Sätzen und Konten als vollständige
Texte geschrieben wurden, obwohl tabellarische Formen bekannt waren
([Arlinghaus, Datini/di Berto](https://www.uni-muenster.de/Geschichte/MittelalterSchriftlichkeit/ProjektA/datini.htm),
Schlussabschnitt). Daraus folgt ein kleiner Einheiten-Layer, nicht eine dichte
34-Zeichen-Fachsprache.

## Konkretes 34-Basis-Modell

Das vollständige Modell ist in `model_v1.json` maschinenlesbar. Die
Kapazitätsaufteilung lautet:

| Rolle | Zahl | normale Ausgabe | harte Position |
|---|---:|---:|---|
| Literalträger | 18 | exakt 1 Zeichen | Core |
| Silbenträger | 4 | 1-3 Zeichen | Core |
| Präfixoperator | 3 | 1-3 Zeichen | vor erstem Core |
| Suffixoperator | 3 | 1-3 Zeichen | nach letztem Core |
| Connector | 2 | 1-3 Zeichen | intern; an Chunkkante mit Strafe |
| kontextuelles Kürzungszeichen | 2 | 1-3 Zeichen | direkt an Träger |
| Ganzform/Logogramm | 1 | 2-8 Zeichen | ganzer Chunk oder typisierter Rezeptslot |
| Null/Layout | 1 | 0 Zeichen | Rand/Layout; darf inaktiv sein |
| **Summe** | **34** |  |  |

Die Zählung ist ein Soft-Prior: Der Gesamtvorrat bleibt 34, benachbarte
Funktionsklassen dürfen gegen Komplexitätskosten höchstens um einen Slot
tauschen. Das verhindert, dass die historische Literatur eine Scheingenauigkeit
von exakt 18/4/3/... erhält.

Die primäre Chunkgrammatik ist:

```ebnf
CHUNK := NULL* (CONNECTOR? BODY CONNECTOR? | CONNECTOR | BOUNDARY_COMPOUND) NULL*
BODY  := WHOLE | PREFIX{0,2} CORE (CONNECTOR CORE){0,3} SUFFIX{0,2}
CORE  := LITERAL | SYLLABIC | CONTEXT_MARK LITERAL | LITERAL CONTEXT_MARK
BOUNDARY_COMPOUND := CONNECTOR SUFFIX
```

Wichtige Regularisierungen:

- Nur der eine Nullslot darf primär leer ausgeben; er darf ganz inaktiv sein
  und höchstens 3 % der Tokenmasse tragen.
- Die 64 häufigen Mergeknoten werden standardmäßig kompositionell gelesen.
  Höchstens acht dürfen nach MDL-Kosten einen lexikalisierten Override
  erhalten, höchstens vier davon eine Ganzform von 2-8 Zeichen.
- Ein Override muss nach Einfrieren auf gehaltenen Folios die
  Kompositionslesung schlagen. Standalone-Rate und Frequenzbucket zählen
  nicht als Ganzformbeweis.
- Verwandte qok-Singletons müssen einen Familienparameter teilen oder einzeln
  bezahlen; fünf kostenlose Wortmakros sind verboten.
- Pro Primitive sind höchstens drei kontextuelle Allomorphe zulässig.
- Kompositionelle Ausgaben sind auf 12 Zeichen begrenzt; längere lesbare
  Folgen müssen aus mehreren Chunks entstehen.

## Abbildung der fünf beobachteten Rollen

### `C` und `d`

Beide erhalten einen Prior auf Präfixoperator/Kopf-Silbenträger. Das ist durch
historische Präfixkürzungen und Formel-/Rezeptköpfe motiviert. Es ist **keine**
Behauptung, `C` bedeute `Recipe`, `con`, `per` oder ein anderes Wort.

### `y`

Dies ist der stärkste direkte Formfit: Suspension, hochgestellte Endzeichen,
Nasalzeichen und `-us/-ur/-is`-Brevigraphen sind historisch positionsgebundene
Schlussexpander. `y` erhält daher einen Suffix-/Kontextzeichenprior, aber keine
fest vorgegebene Buchstabenfolge.

### `o`

Historische `et`/`cum`/`ana`-ähnliche Formen motivieren eine Connectorrolle.
Weil `o` real fast ebenso oft initial und final wie medial ist, darf der FST
den Connector mit Strafe an beide Chunkkanten setzen und als seltenen
Einzelchunk zulassen. Ein nur wortmedialer Morphemprior wäre bereits gegen
die Beobachtung falsch.

### `ol`

Primär wird `ol` als Connector+Suffix am rechten Rand getestet. Seine
Standalone-Nutzung läuft über einen teureren `BOUNDARY_COMPOUND`-Zustand;
erst bei gehaltenem Zugewinn darf daraus ein lexikalisierter Boundary-Makro
werden. Standalone bedeutet weiterhin nicht „Wort“.

### qok-Singleton-Familie

Die Familie ist der zentrale Gegenfalsifikator. Ein historisches System kann
Ganzformen und Sequenzabbreviaturen nebeneinander besitzen, aber deren Klasse
ist aus der bloßen räumlichen Isolation nicht erkennbar. Der Decoder muss
deshalb zwischen geteilter kompositioneller Familie und einem einzigen
familiengeteilten Makro entscheiden; er darf die fünf Einheiten nicht
unabhängig memorieren.

## Klare Empfehlung für den nächsten Decoder

1. **Primärlauf:** exakt `HISTORICAL_MIXED_ABBREVIATION_FST_34_V1` aus
   `model_v1.json`; alle 64 Merges zunächst strikt kompositionell, ein
   optionaler Nullslot, keine Ziellexikon-Boni für Ganzformen.
2. **Ablation A:** Ganzform- und Nullslot entfernen. Wenn die Held-Leistung
   nicht sinkt, waren beide Kategorien Degenerationsventile.
3. **Ablation B:** Connector an Chunkkanten verbieten. Der reale `o`-Anker
   sollte diese Variante klar verschlechtern; andernfalls ist die Rolle nicht
   korrekt genutzt.
4. **Ablation C:** qok-Standalone-Raten permutieren oder aus dem Ganzformscore
   entfernen. Die Makroauswahl muss stabil bleiben; sonst lernt sie nur
   Isolation/Frequenz.
5. **Post-failure-Erweiterung, separat:** höchstens ein zusätzlicher
   Layout-Null-Merge und höchstens acht MDL-Makros. Nie rückwirkend als
   Primärerfolg berichten.
6. **Target-ready-Kriterium:** Rollen und Ausgaben müssen über Starts und
   Folio-Held stabil sein, über eine sprachintern reihenfolgezerstörte Null
   hinausgehen und konkrete längere Bedeutungssegmente ohne
   Lexikon-Längenbonus erzeugen. Historische Plausibilität allein reicht nicht.

## Was ausdrücklich nicht empfohlen wird

- kein flaches 81/82- oder 253-Einheiten-Nomenklatorwörterbuch als
  Kompositionsmodell;
- keine Annahme, alle Standalone-Einheiten seien Wörter;
- keine Alchemiesymbol-Legende als Schlüsselprior;
- keine vielen Nullzeichen im Primärmodell;
- keine visuelle Gleichsetzung von `C`, `d`, `y`, `o`, `l` mit historischen
  Glyphen;
- keine semantische Vorbelegung `Recipe`, `ana`, `et`, `cum`, Maße oder
  Stoffnamen.

## Reproduzierbare Artefakte

| Datei | Zweck |
|---|---|
| `REPORT.md` | Quellenkritik, Modell und Empfehlung |
| `candidate_grid.tsv` | vollständiges maschinenlesbares 8-Kandidaten-Raster |
| `source_evidence.tsv` | 11 Quellen mit Datierung, Locator, Evidenz und Limitierung |
| `model_v1.json` | exaktes 34-Slot-/FST-/Makro-/Nullmodell |
| `validate.py` | prüft Raster, Scores, Quellenauflösung und Kapazität |

Validierung:
`python3 experiments/yolo/gdt609_historical_mixed_abbreviation_prior/src/validate.py`
muss mit `PASS` enden.
