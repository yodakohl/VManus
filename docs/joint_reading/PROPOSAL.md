# Wortfamilien und Absatzkontext unter einem gemeinsamen Leseschlüssel

Umsetzung nach Nutzerauftrag: [GDT832](../../experiments/yolo/gdt832_joint_family_context_control/REPORT.md)
beginnt mit einem begrenzten unabhängigen Kontrollmodell. Der ursprüngliche
Vorschlag unten bleibt als Entwurf erhalten; Status und Ergebnisse stehen im
verlinkten Bericht. Die erste Umsetzung nutzt belegte Co-Lemma-Beziehungen,
noch keinen vollständigen historischen Paradigmengenerator.

5. September 2026. **PROPOSED_CONTROL_ONLY_UNEXECUTED**. Methodenvorschlag und
statische Quellenprüfung; kein neuer GDT, kein Fit, keine Lesung und keine
numerische Preregistrierung. Empfohlener nächster Methodenkandidat. Die frühere
[Parallelpassagensuche](../internal_parallel_passages/PROPOSAL.md) bleibt
ungetestet und wird durch diese Prioritätsänderung nicht widerlegt.

## Idee und erwarteter Nutzen

Eine vorgeschlagene Lesung soll gleichzeitig den vollständigen geschriebenen
Wortformen, ihren wiederkehrenden Formbeziehungen und dem fortlaufenden
Klartextzusammenhang genügen. Ein begrenztes gemeinsames Schreibmodell verbindet
beides. Änderungen an einer Zuordnung wirken dadurch auf sämtliche betroffenen
Wortfamilien und Textstellen. Ziel sind überprüfbare konkrete Lesungen mit einem
übertragbaren Schlüssel. Der Ansatz setzt keine intern doppelt überlieferte
Passage voraus; ob er bessere Erfolgsaussichten hat, ist noch unbekannt.

Als **zu prüfende Modellklasse** dürfen ausgeschriebene Teile, regelhafte
Abkürzungen und eine begrenzte Zahl gespeicherter Ganzformen zusammenwirken.
Das ist keine Feststellung über die tatsächliche Voynichschrift. Frühere
98-Einheiten-Zerlegungen, 34-Rollen-Zahlen und angenommene deutsche Wortwerte
werden nicht zu Beobachtungstatsachen erklärt. Eine konkrete, kapazitätsbegrenzte
Kodierungsklasse muss vor einer Durchführung erst festgelegt werden.

Die [bestätigte formale Struktur](../STRUCTURAL_KNOWLEDGE.md) bleibt erhalten.
Ähnliche Schriftformen werden jedoch nicht automatisch als Flexion derselben
Wurzel behandelt. Der Decoder müsste eine solche Analyse unter einem gemeinsamen
Schreibmodell begründen. Historische Wortfamilien wären externe Beschränkungen
ganzer Formensätze, einschließlich Stammwechseln und mehrdeutigen Formen;
ihre Paradigmenplätze dürfen nicht nachträglich passend umbenannt werden.
Ererbte Parsergrenzen und Wortarten sind keine unabhängige historische Wahrheit.

## Konkreter Anlass aus dem alten Code

Die Prüfung ist begrenzt auf die genannten Quellen. Die dortigen Ergebnisse
wurden nicht neu berechnet:

| Quelle | Nachprüfbare Eigenschaft | Grenze der Schlussfolgerung |
|---|---|---|
| [GDT610-Bericht](../../experiments/yolo/gdt610_consensus_carrier_control_audit/REPORT.md), [Decoder](../../experiments/yolo/gdt610_consensus_carrier_control_audit/src/consensus_carrier_decoder.py), `NgramModel.log_score_word`, `chunk_score` | Im bekannten Kontrollcode sind alle elf Ganzwortträger stabil falsch. Der lokale Score summiert kontextlos einzeln bewertete Wörter sowie Längen-/Anzahlterme. | Das beweist weder die Ursache des gesamten Kontrollfehlers noch einen Nutzen der vorgeschlagenen Reparatur. |
| [GDT612-Decoder](../../experiments/yolo/gdt612_historical_fst34_target_attack/src/full/decoder.cpp), `CharModel::score`, `score_chunk` | Zeichenkontext läuft innerhalb des übergebenen Wortvektors über Wortgrenzen, beginnt aber bei jedem getrennt bewerteten Chunk neu. | GDT612 ignoriert nicht jede Wortfolge. Der spätere Held-Evaluator ist nicht mit dem Trainingsziel gleichzusetzen. |
| [GDT612-Kontrollgenerator](../../experiments/yolo/gdt612_historical_fst34_target_attack/src/full/make_synthetic.py), Schleife über `words` und `Counter(encoded)` | Nicht kodierbare Wörter werden ausgelassen; Kontextbeispiele werden zusätzlich angehängt. Der Fitter erhält frequenzsortierte Chunktypen. | Dies ist kein unverändert verschlüsselter fortlaufender historischer Absatz. Der alte [Autopsiebericht](../../experiments/yolo/gdt612_historical_fst34_target_attack/REPORT.md) nennt weitere Fehler; Kontext allein behebt diese nicht. |
| [GDT001-Ganzwortmodell](../../run_gdt001_word_nomenclator.py), `split` | Es benutzt Wortbigrams, beendet einen Lauf jedoch bei einer Gruppe außerhalb des ausgewählten Ganzwortinventars; der Rest bleibt anonym. | Die Aussage „Wortkontext wurde noch nie benutzt“ wäre falsch. |
| [GDT001-Komponentenmodell](../../run_gdt001_nomenclator.py), `split` | Der alphabetische Sprachlauf endet beim opaken Ganzworteintrag. | Die beiden geprüften Teilmodelle identifizieren nicht gemeinsam einen durchgehenden gemischten Klartext. |
| [GDT001-Morphologiemodell](../../run_gdt001_morphology_grammar.py) | Häufige Präfixe/Suffixe und anonyme Kerne werden ausgewählt und modelliert. | Das ist noch kein Decoder mit historischen Lemma-/Paradigmenzuordnungen unter einem gemeinsamen Schreibschlüssel. |

Root hat diese Codepfade und die GDT610/GDT612-Berichte selbst gelesen;
Subagenten halfen bei unabhängiger Methoden- und Vorgängerprüfung. Die
Quellenprüfung erzeugt keine neue Manuskriptevidenz.

## Was sich gegenüber Vorläufern tatsächlich ändern müsste

[GDT603](../../experiments/yolo/gdt603_naibbe_end_to_end_control/REPORT.md)
benutzt bereits fortlaufenden alphabetischen Kontext und löst seinen
Naibbe-Kontrollfall. Der anschließende
[GDT604](../../experiments/yolo/gdt604_naibbe_frozen_target_attack/REPORT.md)
liefert keine Voynichlesung. Durchgehender Kontext allein wäre deshalb keine
neue Route. [GDT747](../../experiments/yolo/gdt747_supported_whole_passage_application/REPORT.md)
und [GDT748](../../experiments/yolo/gdt748_complete_whole_serial_paradigm_census/REPORT.md)
kombinieren bereits lokale Reihen und Ganzformähnlichkeit; ihre Arbeitsrollen
sind keine unabhängigen historischen Flexionsparadigmen oder Klartextanker.

Der hier vorgeschlagene Unterschied ist eine **gemeinsame Identifikation über
Ganzform-/Komponentenübergänge**, beschränkt durch historische ganze
Formfamilien. Derselbe ausgegebene Klartext muss denselben Sprachscore erhalten,
gleichgültig, an welchen Eingabegrenzen er zusammengesetzt wurde. Kosten für
Schlüssel, Segmentierung und Beobachtung bleiben davon getrennt. Ein kurzer,
für alle Vorkommen gültiger Regelsatz ersetzt keine nachträglich beliebig
änderbare Einzelstellenübersetzung.

Die geschlossene [GDT616-Konfiguration](../../experiments/yolo/gdt616_joint_child_feasible_binding/REPORT.md)
wird nicht repariert oder wiederholt. Ihr erzwungenes Einheiteninventar und
ihre synthetischen Kind-/Override-Bedingungen werden nicht übernommen.

## Erste Entscheidung durch einen unabhängigen Kontrollfall

Vor einem Manuskriptfit muss ein getrennt gebauter Generator unveränderte
historische Absätze unter einer vorab begrenzten Mischkodierung verschlüsseln.
Er darf Wörter nicht auslassen oder umsortieren, um eine erwünschte
Voynich-Chunkverteilung zu erzeugen. Schlüssel und Bestätigungstexte bleiben
dem Decoder verborgen; Referenztraining enthält diese Absätze und ihre
Dublettenkopien nicht.

Der neue Falsifikator ist die korrekte Wiedergewinnung des Klartexts auf ganzen
ausgeschlossenen Absätzen **und** von zuvor ausgeschlossenen Wortformen und
Lemmas unter demselben Schlüssel. Eine Kontrollanalyse muss die Identifizierbarkeit
des Schlüssels prüfen; bei äquivalenten Kodierungen zählt die offen ausgewiesene
Äquivalenzklasse, nicht ein künstlich unmöglicher exakter Parametervergleich.
Für die Prüfungen sind getrennte, ausreichend belegte Partitionen nötig.
Alle informationshaltigen Schlüsselregeln müssen im Discovery-Material
ausreichend vorkommen. Gehaltene neue Formen müssen aus bereits belegten Regeln
rekonstruierbar sein; ein erstmals auftauchender opaker Ganzwortträger erhält
keinen zuvor unbekannten Wortwert. Damit wird GDT612s fehlende Schlüsseldeckung
nicht als vermeintlich strenger Holdout wiederholt.

Verglichen werden das vollständige Modell und ansonsten identische Varianten,
die entweder den Kontext an Mischübergängen abschneiden oder die externen
Lemma-/Paradigmenbeziehungen zerstören. Zusätzlich braucht es Pseudotexte mit
vergleichbarer Häufigkeit, Wortform- und Familienstruktur. Sprachflüssigkeit,
hoher Referenzscore, Restart-Einigkeit und Rückkodierbarkeit allein bestehen
diese Prüfung nicht. Aufwand, Schwellen, Kodierungsklasse und Nullkonstruktionen
müssen vor Ergebnissen numerisch festgeschrieben werden. Diese Seite ersetzt
eine solche Preregistrierung nicht.
Der behauptete gemeinsame Informationsgewinn ist nur unterstützt, wenn die
exakte gehaltene Rekonstruktion beide vorab festgelegten Ablationen materiell
übertrifft. Gleich gute Wiedergewinnung durch alle Varianten zeigt nur die
allgemeine Lösbarkeit dieses Kontrollfalls; auch die Verbesserungsschwelle
gehört in die spätere Preregistrierung.

Historische Sprachkorpora sind im Projekt vorhanden. Eine geeignete geprüfte
historische Lemma-/Paradigmenressource ist für diesen Vorschlag **noch nicht
nachgewiesen**. Ihre Verfügbarkeit und der Informationsgewinn der gemeinsamen
Beschränkungen sind die ersten Machbarkeitsfragen, keine erledigten Arbeitspakete.

## Manuskript- und Evidenzgrenzen

Ein gelöster Kontrollfall prüft das Werkzeug und seine begrenzte Kodierungsklasse.
Er etabliert weder diese Klasse für Voynich noch eine Übersetzung. Der geschlossene
Eintrag `CACHED_DATA_TRANSLATION_SUCCESSOR` und sein
[CDA001-Bericht](../../experiments/semantic_assumptions/results/cda001_cached_data_route_exhaustion.json)
bleiben bestehen: Ein stärkerer Decoder ersetzt die fehlende unabhängige
Text-/Wertverbindung nicht. Ein späterer Zielversuch braucht eine eigene
begründete Evidenzroute und Preregistrierung; dieser Vorschlag öffnet ihn nicht.

Keine neuen Manuskriptbilder oder gemischten Transkriptionszeilen wurden für
diese Prüfung geöffnet. Rohgruppen, unsichere Abstände und alternative Lesungen
bleiben sichtbar; letztere sind keine unabhängigen Manuskripte. Keine neue
Seitenaufnahme; f84 und f84r bleiben versiegelt. Neue Relationsevidenz müsste
weiterhin sämtliche GDT388-Einlassprüfungen bestehen.

## Nutzerauftrag 9. September: Gesamtarchitektur 5 + 3

Aktiver Beginn 18:34:04 UTC; mindestens zehn Stunden angefordert, ohne inaktive
Lücken. Die bestehende Langlaufsteuerung meldet usageLimited; daraus entsteht
keine behauptete Arbeitszeit. Schwerpunkt: unbekannte Schriftbausteine, volle
Flexionsparadigmen und Satzbeziehungen unter einem globalen Leseschlüssel.
832–837 nutzten nur Co-Lemma-Mitgliedschaft, vorgegebene Atome/Grenzen und wenige
Suffixkarten; ihre Fehler und 616 bleiben bestehen. Neu verfügbar ist die
Primärressource LatInfLexi mit expliziten Paradigmenzellen und phonologischen
Formen; sie schließt mittelalterlichen Wortschatz ausdrücklich aus. Sie wird
nicht als belegte Voynichsprache behandelt.

Erster Entscheidungspunkt nach höchstens 30 Minuten einschließlich Quellenzugriff,
Architektur, unabhängiger Kritik und kompakter Veröffentlichung: Gibt es einen
endlichen globalen Schriftkanal, in dem diese zusätzlichen Beschränkungen die
Wort-/Merkmalszuordnungen tatsächlich identifizierbar machen können? Bei einem
konkreten tragfähigen Modell folgt eine gemeinsame Rekonstruktion vollständiger
Texte; ungelöste freie Bedeutungsumbenennung oder fehlende Kanaldefinition führen
zur Modellrevision auf Papier, nicht zu einem größeren LM-/Kontrolllauf. Der
Unterschied muss über den bekannten Co-Lemma-Bonus hinausgehen. Nr.48 bleibt
die unabhängige Quellenalternative. Keine neuen Voynichseiten oder versiegelten
Daten; Quellenregister und Sprachannahmen bleiben getrennt.

Checkpoint nach etwa30Minuten: GDT892 definiert einen endlichen gemeinsamen
orthographischen CV-Kanal ohne freie Wurzelcodes. Präfixfreiheit bei1/2-Zeichen-
Codes reduziert die latenten Zerlegungen auf globale Zeichenmasken; vollständige
Codebuchergänzbarkeit bleibt zusätzlich verpflichtend.425561 feste Quellformen
und eine Grammatik aus13586 projektiven Referenzbäumen liegen vor. Das genügt
für die begrenzte Implementierung/Identifikationsprüfung, nicht für eine
Manuskriptlesung. Nächstes Budget90Minuten ab19:04UTC einschließlich Ergebnis-
prüfung und Veröffentlichung; kein automatischer Reparaturlauf bei Scheitern.

GDT892 stopped before key/cipher generation: the unchanged source supplies12D+9H,
below the fixed12+12 requirement. No decoder fit or threshold/corpus repair.
The architecture remains untested; move to the independently prioritized source
montage model, conditional on complete source runs and an identifiable shared
writing map. No old control failure is reopened.

Source montage decision, 2026-09-09 19:30UTC: GDT378/211 tested anonymous
roles,838 internal windows,884 one fixed expanded passage,887 one fixed medical
compiler. The unknown is whether complete source runs from a frozen14-witness
pool jointly identify whole manuscript paragraphs under ONE injective word code.
Pool: all8 current ALIM Medicina works/versions plus6 cached COREMA recipe XMLs;
related witnesses remain dependent. Maximize written word positions covered by
whole eligible discovery paragraphs, retain every optimal plaintext projection,
and leave residual text untranslated. No fragment-length or match-count threshold.
A forced complete passage supports a corpus-relative candidate for independent
continuation validation; no compatible passage or only ambiguous optima parks
this exact-copy model on this pool. No enlarged corpus or relaxed code follows.
Use existing887 paragraph cache, odd physical leaves only; historical exposure
is disclosed, even leaves unused by this fit. First complete enumeration/optimizer
budget90min through21:00UTC, including source preparation, independent validation
and publication. No scored null/meaning before separate388 packet and held gates.

GDT894 decision,20:21UTC: GDT893 RF has one independently reproduced forced
28-group projection,26 written values and one source provenance. GDT884 tested
a different fixed expanded passage;893 permits source changes at paragraph
boundaries and entails no continuation. The genuinely unknown additional law
is continuous exact copying on both sides of this particular source window.
Freeze the adjacent128 source positions per direction, clipped only by the
already frozen gap-bounded unit (128 preceding,39 following). The same26-value
key predicts known-code equality and forbids those codes for unknown source
words; no new values or source offsets are selected. Compare only literal RF
groups on f103v, anchored by all28 original group IDs; stop positional evidence
at an uncertain raw group, separator, missing line or folio edge. STA parse
ineligibility alone is irrelevant to this explicitly literal-word model.
One secure contradiction refutes the continuous-copy law for that direction;
both directions are assessed, all provenance retained. No contradiction is
only necessary-condition compatibility, never full decoding or independent
held confirmation. Historical exposure remains explicit. Rejection parks this
continuation rather than repairing keys, shifting windows or enlarging sources.
Budget35min20:21–20:56UTC including preregistration, two implementations, guarded
intake, validation and publication. No visual admission or f84/f84r access.

Simon dictionary decision, 2026-09-09 21:04UTC:893/894 are closed; their source
pool and word key will not be repaired. The distinct #13/#44 hypothesis is a
collection of complete dictionary entries under one compositional writing code.
888 leaves18 opaque name assignments;884 is a single fixed passage equation;
893 permits arbitrary word values and uncovered paragraphs. The unknown is
whether Simon's complete edited entries provide enough actual bounded text to
constrain both whole-entry identity and a shared script, without arbitrary word
values. Two archived examples (Nefros, Kit) do not establish a usable corpus.
First recover the23 source index sections and a deterministic varied entry
sample, assess the edition's word/uncertainty boundaries, and specify a finite
global code with explicit invertibility limits. A complete reproducible source
inventory and defensible contract permit preregistering the joint entry model;
missing source coverage or unconstrained word loss parks this source/model before
decoder work. No source substitutions, target-selected entry omissions, or
editorial commentary used as medieval text. Budget45min21:04–21:49UTC, including
source intake, independent architecture review and compact publication. No new
Voynich data are needed for this preparation. Further work requires a concrete
decision at that checkpoint, not an automatic corpus/decoder expansion.

Early source checkpoint21:16UTC:21/23 archived letter indices expose5803 entry
links; eight varied complete bodies are verified, eight failed requests retained.
The edition is eclectic and expanded, with witness-dependent entry boundaries.
Full-book coverage is not established. Select an explicitly PARTIAL AVAILABLE
EDITION inventory, not a claim about every Simon entry or any individual witness.
Acquire metadata for all5803 already indexed titles and each available body's
capture nearest the fixed20220812000000 anchor; no title/content selection by
Voynich fit, no new archive/source after results. Raw modern edition stays local.
Before target access, freeze all successfully acquired complete unambiguous main
entries and every exclusion with source reason. This is a conditional complete-
target reconstruction from that partial pool; an exclusion cannot reject missing
Simon entries or the broader dictionary hypothesis.

Select the exact lossless892 CV channel as a new source-equation hypothesis:
all eligible odd887 paragraphs must match different complete source entries under
one27-component prefix-free1/2-character key, with all six inherent vowels kept.
It can contract inherent CVs and reconstructs every letter; it supplies no free
root/word values. This is not a rerun or repair of892's failed source eligibility
control: attested complete entries replace its lexicon/grammar task, with exact
compatibility and all-solution identification as the falsifier. 892's control
never passed and no grammar-decoder claim is imported. The broader block-expansion
alternative is not selected and will not be an automatic fallback.

Next budget90min21:16–22:46UTC including archive intake, parser/source validation,
formal specification and publication. Source-only work until the exact finite
inventory and its alphabet contract pass independent review. If the available
inventory cannot support a reproducible complete-entry equation, stop this source
without further archive chasing. If it can, set the smallest adequate exact-search
budget in its preregistration. A forced portable key opens a separately fixed held
reading; only ambiguous keys or exact rejection parks this pool/channel. No target
omissions, changed source spellings, threshold relaxation or fitted source variants.

GDT895 preparation checkpoint,22:27UTC: complete-entry word partitions may leave
an individual panel unresolved; they do not themselves test the CV channel.
Within the existing22:46 preparation end, allow at most15minutes for two small
independent exact word-equation kernels on invented data only: direct codeword
DFS and binary component-length equations. A verified empty domain closes a
panel; otherwise these kernels can decide the already registered channel rather
than reporting preliminary compatibility as a fit. No broader decoder, alternate
source or target processing is selected. Actual target-search duration and
frozen inputs remain to be published after source closure.

GDT896 decision,22:58UTC:895 is closed. Alberti's source-attested decoded-control
ring is a different complete channel: previous signs change later letter values,
controls emit no letter, and written word boundaries impose no plaintext boundary.
604's fixed U/P/S failure and895's word-equality contradictions do not decide it.
Test one explicit conjunction: every inherited odd paragraph is one initialized
message encoding a distinct complete entry from the unchanged895 available pool.
Only j->i and v->u are projected; any remaining out-of-alphabet letter excludes
the entire source entry. This copy/message contract is hypothetical, not historical
evidence linking Simon, Alberti and Voynich. Allow the mechanical superset with
consecutive/trailing controls, all20 index letters and every injective24-position
ring. Exact failure closes this conjunction; complete solutions permit examining
whether the shared key/plaintexts are forced; timeout parks it without repair.
First derive complete-source run domains, then solve shared ring/entry constraints
only if needed. Independent recursion/constraint validation must check the result.
Budget60min through23:58UTC including preparation, validation and publication;
checkpoint23:18 before target access, latest target start23:38, at most300seconds
per panel per independent implementation. No new pages, source, LM or coverage
relaxation; full contract in896/METHOD.md. This is a conditional source-equation
test, not an inference that the manuscript uses the later Alberti cipher.


GDT905 decision, 2026-09-10 05:50 UTC, new explicit user construction task:
Select a bounded exploratory manuscript construction under the UNCHANGED892
CV channel,425561-word reference and frozen feature grammar.892 never ran a
cipher fit; its12+9 capacity stop remains, with no threshold/source repair or
claim of a passing control.832/837 wrong high-score keys motivate exact
constraint satisfaction with all surviving readings retained, no fluency winner.
Unlike895, no complete source entry is assumed; the unknown plaintext is generated
from the fixed word/grammar constraints. This is explicit hypothesis generation,
not a semantic validation successor or permission to evaluate held folios.
Use the already published904 odd-leaf paragraph intake. Select whole paragraphs
with12..24 raw groups, every selected reading preserved separately. Enumerate
all global1/2-codeword segmentations per complete paragraph, then exact shared
component keys and full grammar acceptance. No source word deletion, target
window, private word code or later character/grammar repair. Compatible keys
provide concrete whole-passage candidates; ambiguity/timeout stays explicit.
A candidate changes the next decision only by supplying a fully stated key whose
additional consequences can subsequently be assessed. Empty domains stop this
fixed construction scope; timeout stops optimization. No translated-meaning
claim without separately justified independent evidence and applicable gates.
Budget40min through06:30UTC including implementation, independent validation and
publication. First target scan by06:02; stop all search06:17. No new images,
even-leaf bodies, f84/f84r or control truth. Protocol905/METHOD.md fixes details.
