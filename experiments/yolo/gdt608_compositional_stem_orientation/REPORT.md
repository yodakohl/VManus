# GDT608: kompositionelle Stamm-/Rollenanalyse

## Entscheidung

**`PARTIAL_COMPOSITIONAL_BACKOFF__ATOMIC_MERGE_IDENTITY_RETAINS_RESIDUAL_ROLE`**

Die 64 registrierten BPE-Zusammensetzungen besitzen eine echte, gerichtete
Außenkanten-Komposition.  Aus dem Trainingsprofil von `L` und `R` lässt sich
für ein gehaltenes `L+R=M` ein Teil der linken/rechten Nachbarschaft sowie der
Chunk-, Zeilen- und Absatzkanten vorhersagen.  Das unveränderte Modell schlägt
GLOBAL und die Richtungsumkehr auf allen 23 held Folios und schlägt das nach
Trainingsfrequenz/Folio-Mobilität gematchte Komponentenpaar-Nullmodell deutlich
(`1.0592` statt `1.7061` primäre Bits/Merkmal/Ereignis,
`p=0.000999`).

Es ist aber kein vollständiger kompositioneller Code.  Die atomische
Merge-Identität bleibt wesentlich besser (`0.8659` Bits) und gewinnt auf allen
23 held Folios sowie bei 51/64 Merge-Typen.  Ein train-only, leave-one-merge-out
Ridge-Modell verbessert die direkte Komponentenregel für die sechs
Kantenindikatoren von `0.3291` auf `0.3159` Bits, bleibt aber hinter ATOMIC
`0.2553`.  Der korrekte Befund lautet daher: **gerichtete formale
Kompositions-Backoffstruktur plus paarspezifische Residualrolle**.  Er ist keine
linguistische Morphologie und liefert keine Bedeutung.

Die wichtigsten konkreten Resultate sind:

- Rechte Komponenten `y`, `dy` und `aN` tragen robuste
  Near-closure-Profile in ihre direkten Kinder: gewichtete held
  Chunk-final-Raten `0.952`, `0.972` und `0.989`.
- Rechte Komponente `k` trägt das Gegenprofil: vier Kinder sind nahezu nie
  Chunk-final (`0.006`).
- Linke Komponente `q` trägt einen fast obligatorischen Chunk-Eintritt in vier
  Kinder (`0.984`).
- `o` ist **kein** stabiler linker Stamm: nur 5/8 Kinder bevorzugen die echte
  Richtung gegenüber der Umkehr, das Familiennull erreicht `p=0.0859`, und die
  held Chunk-initial-Rate reicht von `0.149` (`od`) bis `0.945` (`op`).
- Von den sechs nominierten Paaren ist `a+N=aN` der sauberste zweiseitige
  Backoff. `d+y=dy` übernimmt die rechte Closure-Tendenz, aber nicht das linke
  Head-Profil. `ol` und `or` sind paarspezifische Gegenbeispiele; `ok` und `ot`
  erhalten starke paarspezifische Entry-Profile.

Alle Rollennamen in diesem Bericht beschreiben ausschließlich messbare
Außenkanten.  `Stamm` bedeutet hier nur ein wiederverwendetes Element des
eingefrorenen BPE-Baums.

## Umfang und wissenschaftliche Begrenzung

Verwendet wurden nur die bereits guarded, f84/f84r-freien Artefakte von GDT605
und GDT606.  Es wurde keine Transkription neu abgefragt, keine Seite oder
Abbildung geöffnet und kein Workshop-Wert benutzt.  Die 68/23-Aufteilung nach
physischen Folios bleibt unverändert.

Der vorgeschaltete Route-Check lautete:

```text
./vmanus-exp route-check 'GDT605 GDT606 collapsed 98 unit BPE merge composition
stem role profile compound atom compositional versus atomic train held frequency
control destroyed mobile o l ol o r or o k ok o t ot d y dy a N aN'
```

Er verwies primär auf GDT605/GDT606 und zusätzlich auf nichtkanonische
Workshop-Kompositionsrouten wie GDT557.  Deren Bedeutungen, Karten und
Übersetzungen wurden nicht gelesen oder übernommen.  Diese Analyse fragt nur,
ob der kanonische kollabierte GDT605-Strom seine formalen Rollen entlang der
eingefrorenen Merge-Kanten transportiert.

Die Analyse ist explorativ, nicht blind: Ein vorheriger unabhängiger
GDT606-Rollenlauf hatte bereits held-Zusammenfassungen für `o`, `ol`, `or`,
`ot` und einige Kontrollen offengelegt.  Deshalb wurden Endpunkte und Nulls in
`PREREGISTRATION.md` vor der vollständigen 64-Merge-Auswertung festgeschrieben,
aber hier nicht als vorab verblindet dargestellt.

## Eingaben und Bindung

| Artefakt | SHA-256 |
|---|---|
| `gdt605_bpe_merges.tsv` | `4625c9389ead390907e4ac74e65bc158236f02b439c69cf3b09157f0cd6ca539` |
| `gdt605_unit_inventory.tsv` | `ade74733200e941ddc66285988eb1498ac98e87ad374cad11ac412ce42893e82` |
| `gdt605_unit_result.json` | `c2d293c121f1ee01fe0ddcbe4647c77f5f94796b4ecc4b1adc554cc2f740c3d9` |
| `guarded_rows.tsv` | `d6674f3d54edc49590c884b5d703cb032b966c1abd4da6338093795ce1f31ef9` |
| `unit_sequences.json` | `3ee0841e211314b72719acbbf79ed3a6dc7bfc3c157734f54dbdac92ac458fdf` |
| `complete_mappings.tsv` | `005ddec8e5b67763c9ccfd1d3244e44c1e68d8c0c6c46a2c7d7edcc36fa4aabe` |
| Latin-Kategorietabelle | `2a43d309b78392781ab9111c00dcead82424d648ad820fd02f1479dbb33e7997` |
| Altitalienisch-Kategorietabelle | `069023255a729b0918f7298ca5482f9bfa6fa1815541098f801db7ddc4704169` |
| MHG-Kategorietabelle | `998a6f093584f26321bc4e4ef2f88171ff245383eecb786adde7fe98733e81b5` |

Der Datenumfang ist:

| Größe | Wert |
|---|---:|
| Guarded-Zeilen | 4,165 |
| finale Unit-Typen | 98 train; 97 held; keine held-only Unit |
| Unit-Ereignisse | 43,335 train; 21,679 held |
| direkte BPE-Regeln | 64 |
| Ereignisse der 64 Merge-Ausgaben | 28,756 train; 14,390 held |
| wiederholte linke/rechte Stammfamilien mit mindestens drei Kindern | 18 |

Die neun vor-BPE Kollapszeichen (`C`, `S`, `N` usw.) bleiben formale
kollabierte Graphemzustände.  Großbuchstaben sind weder Laute noch Klartext.

## Beobachtung und Modelle

Nachbarn überschreiten nie eine sichere Hard-Chunk-Grenze.  Zeilenkanten
stammen aus der Reihenfolge aller Chunks am gleichen Locus.  Absatzkanten werden
nur aus den bereits vorhandenen IVTFF-Markern `<%>` und `<$>` abgeleitet.
`standalone` bedeutet exakt “ein finaler 98-Unit-Chunk der Länge eins”, nicht
“Manuskriptwort”.

Für jede Unit werden train und held diese Profile bestimmt:

- standalone, Chunk-initial/final, Zeilen-initial/final und
  Absatz-initial/final;
- äußerer linker und rechter Unit-Nachbar;
- Section, Hand, Currier-Code und physisches Folio.

Alle Wahrscheinlichkeiten verwenden `alpha=0.5`.

| Modell | held-Vorhersage |
|---|---|
| GLOBAL | gesamter Trainingsstrom ohne Unit-Identität |
| ATOMIC | eigenes Trainingsprofil der Merge-Ausgabe `M` |
| DIRECT | linker Außenkontext und initiale Kanten aus `L`; rechter Außenkontext und finale Kanten aus `R` |
| SWAPPED | identische Regel nach Vertauschung von `L` und `R` |
| LOMO-RIDGE | für jedes Kantenmerkmal train-only Regression aus den anderen 63 Merges; die Ziel-Merge-Antwort bleibt ausgeschlossen |

Für Section, Hand und Currier verwendet DIRECT das normalisierte geometrische
Mittel der beiden Komponentenprofile.  Der primäre Score mittelt gleichgewichtet
linken/rechten Nachbarn und sechs Initial-/Finalindikatoren.  Standalone bleibt
ein separat ausgewiesener sekundärer Falsifikator.

Das mobile Nullmodell ersetzt für 1,000 feste Replikate jedes echte Paar durch
ein Paar aus den acht nächstliegenden anderen Merges.  Distanzmerkmale sind nur
train log-Frequenz und train effektiver Folioanteil.  Die held-Ziele bleiben
unverändert.  Damit wird echte Paaridentität gegen gleich häufige und ähnlich
mobile Komponentenpaare geprüft.

## Aggregierte train→held-Ergebnisse

### Primäre Außenkanten

| Modell | primäre Bits/Merkmal/Ereignis | Abstand zu DIRECT |
|---|---:|---:|
| ATOMIC | **0.865886** | DIRECT ist 0.193340 schlechter |
| DIRECT | **1.059225** | — |
| GLOBAL | 1.237040 | DIRECT gewinnt 0.177814 |
| SWAPPED | 2.019941 | DIRECT gewinnt 0.960715 |
| mobile Paar-Null, Mittel | 1.706100 ± 0.084247 | DIRECT gewinnt 0.646875 |

Die mobile Nullspanne ist 1.4359--1.9808; ihr 1%-Quantil ist 1.5216.  Keine der
1,000 Nullreplikate erreicht DIRECT (`p=(0+1)/(1000+1)=0.000999`).

DIRECT schlägt GLOBAL bei 58/64 Merge-Typen, SWAPPED bei 63/64 und den lokalen
Mittelwert seiner acht gematchten Donorpaare bei 64/64.  Gegen ATOMIC gewinnt
DIRECT nur 13/64.  Der einzige Merge mit negativem Richtungsgewinn ist `o+d=od`.

### Einzelmerkmale

| Merkmal | ATOMIC | DIRECT | GLOBAL | SWAPPED |
|---|---:|---:|---:|---:|
| linker Nachbar | 3.0462 | 3.6415 | 3.8439 | 5.3655 |
| rechter Nachbar | 2.3489 | 2.8577 | 3.3470 | 5.8051 |
| Chunk-initial | 0.6141 | 0.8171 | 0.9963 | 1.3321 |
| Chunk-final | 0.3679 | 0.5238 | 1.0189 | 2.8140 |
| Zeilen-initial | 0.1804 | 0.2064 | 0.2280 | 0.2880 |
| Zeilen-final | 0.2497 | 0.3035 | 0.3240 | 0.3821 |
| Absatz-initial | 0.0226 | 0.0238 | 0.0311 | 0.0423 |
| Absatz-final | 0.0974 | 0.1000 | 0.1071 | 0.1305 |

DIRECT verbessert gegenüber GLOBAL jedes primäre Merkmal, nicht nur einen
dominierenden Kanal.  Die Richtung ist besonders klar an äußerem Kontext und
Chunk-Enden.

### Folio-Stabilität

DIRECT schlägt GLOBAL auf 23/23 held Folios; der Gewinn liegt zwischen 0.0570
und 0.2541 Bits.  DIRECT schlägt SWAPPED ebenfalls auf 23/23.  Umgekehrt schlägt
ATOMIC DIRECT auf 23/23 Folios.  Der partielle Befund hängt somit weder an
einem großen Folio noch an einem Registerwechsel.

## Gelernte Seitenrichtung

Das leave-one-merge-out Ridge-Modell lernt aus 63 Train-Merges und sagt die
64. held voraus.  Seine standardisierten Profilkoeffizienten zeigen die
erwartete Orientierung, ohne sie im Fit festzuschreiben:

| Zielrate | Koeffizient linkes Komponentenprofil | rechtes Komponentenprofil |
|---|---:|---:|
| Chunk-initial | **2.386** | 0.411 |
| Chunk-final | -0.039 | **3.155** |
| Zeilen-initial | **1.212** | -0.093 |
| Zeilen-final | 0.260 | **1.553** |
| Absatz-initial | 0.337 | 0.359 |
| Absatz-final | 0.112 | **1.116** |

Absatz-initial ist extrem selten und liefert keine klare Seitenrichtung.  Über
die sechs Kantenraten verbessert LOMO DIRECT von 0.3291 auf 0.3159 Bits, bleibt
aber hinter ATOMIC 0.2553.  Über alle sieben Raten sind die mittleren absoluten
Fehler ATOMIC 0.02235, LOMO 0.07672 und DIRECT 0.10101.

## Baumtiefe: Backoff wird bei tiefen Einheiten nützlicher

Dies ist eine nach dem Freeze ausgewiesene deskriptive Schichtung; sie ändert
den Entscheidungsgate nicht.

| direkte Baumtiefe | Merge-Typen | held Ereignisse | DIRECT-Gewinn vs GLOBAL | ATOMIC-Gewinn vs DIRECT | DIRECT schlägt ATOMIC |
|---:|---:|---:|---:|---:|---:|
| 1 | 30 | 8,837 | 0.1323 | 0.2439 | 1/30 |
| 2 | 28 | 5,065 | 0.2300 | 0.1280 | 6/28 |
| 3 | 6 | 488 | 0.4596 | **-0.0440** | 6/6 |

Alle sechs tiefsten Einheiten sind `qok+X`-Merges.  Bei ihnen kann
Komponenten-Backoff die kleine atomische Stichprobe tatsächlich übertreffen.
Das ist eine praktische Seltenheits-Backoffeigenschaft.  Es beweist keine
Autorenmorphologie; insbesondere scheitert die separate Standalone-Komposition
weiterhin.

## Nominierte Paare

| Merge | held n | DIRECT vs GLOBAL | Richtung vs SWAPPED | ATOMIC-Vorsprung | präziser Befund |
|---|---:|---:|---:|---:|---|
| `o+l=ol` | 712 | **-0.1361** | +0.2275 | +0.2069 | final held .546 vs Komponentenprognose .161; paarspezifisches Boundary-Profil |
| `o+r=or` | 535 | **-0.0315** | +0.3588 | +0.1525 | final .650 vs .380; paarspezifisches Finalprofil |
| `o+k=ok` | 625 | +0.1477 | +0.1262 | +0.3220 | `k` sagt Nonfinalität voraus (.010 vs .015), aber Entry entsteht paarspezifisch (.821 vs .336) |
| `o+t=ot` | 689 | +0.0923 | +0.0773 | +0.3854 | Nonfinalität überträgt, Entry entsteht paarspezifisch (.920 vs .336) |
| `d+y=dy` | 204 | +0.0578 | +0.4924 | +0.3755 | rechte Closure überträgt (.936 vs .711), linkes Head-Profil bricht (.181 vs .635) |
| `a+N=aN` | 556 | +0.2131 | +1.1551 | +0.1584 | sauberster zweiseitiger Backoff: initial .187 vs .134; final .977 vs .962 |

Positive Zahlen in “DIRECT vs GLOBAL” und “Richtung vs SWAPPED” begünstigen
Komposition; “ATOMIC-Vorsprung” begünstigt die eigene Merge-Identität.

### Warum `o` kein Stammrollen-Schlüssel ist

`o` hat acht direkte Kinder: `ok`, `ol`, `ot`, `or`, `ody`, `od`, `op`, `os`.
Die linke Familienregel erreicht nur 5/8 positive Richtungsvergleiche und
verfehlt das mobile Familiennull (`p=0.0859`).  Besonders deutlich:

- `ok` und `ot` sind held zu 0.821 und 0.920 Chunk-initial;
- `ol` und `or` sind nur 0.404 und 0.250 initial, aber 0.546 und 0.650 final;
- `od` ist 0.149 initial und der einzige Merge, bei dem SWAPPED besser als
  DIRECT ist;
- `op` ist 0.945 initial.

Das gemeinsame sichtbare `o` reicht daher nicht aus, um die zusammengesetzte
Rolle zu bestimmen.  `ol`, `or`, `ok`, `ot` dürfen nicht auf einen einzigen
`o`-Wert oder eine einzige `o`-Rolle reduziert werden.

## Stabile direkte Stammseiten

Der Gate verlangt mindestens drei Kinder, mindestens 75% positive
Richtungsvergleiche und `p<=0.05` gegen die mobile Familiennull.  Vierzehn von
18 Familien bestehen.

| Seite | Stamm | Kinder | held Kantenanker | Richtungsgewinn | Gewinn vs mobile Null | p | formale Rolle |
|---|---:|---:|---:|---:|---:|---:|---|
| links | `q` | 4 | Chunk-initial .984 | .169 | .637 | .0010 | nahezu obligatorischer Chunk-Eintritt |
| links | `S` | 4 | Chunk-initial .670 | .943 | .451 | .0010 | entry-bias |
| links | `C` | 8 | Chunk-initial .507 | .768 | .234 | .0050 | moderater lokaler Entry-Träger |
| links | `d` | 5 | Chunk-initial .425; Zeilen-initial .083 | .375 | .344 | .0010 | gemischter lokaler Head-Träger |
| links | `a` | 6 | Chunk-initial .177 | .660 | .474 | .0010 | non-entry linker Außenkontext |
| links | `e` | 3 | Chunk-initial .009 | 1.289 | 1.075 | .0010 | innerer linker Außenkontext |
| rechts | `y` | 12 | Chunk-final .952 | 2.543 | .862 | .0020 | nahezu obligatorischer Chunk-Abschluss |
| rechts | `dy` | 6 | Chunk-final .972 | 2.743 | .722 | .0010 | nahezu obligatorischer Chunk-Abschluss |
| rechts | `aN` | 3 | Chunk-final .989 | 1.852 | 1.400 | .0010 | nahezu obligatorischer Chunk-Abschluss |
| rechts | `k` | 4 | Chunk-final .006 | .918 | 1.298 | .0010 | internes/nonterminales rechtes Profil |
| rechts | `r` | 3 | Chunk-final .706 | .685 | 1.015 | .0010 | chunk-final bias |
| rechts | `al` | 4 | Chunk-final .667 | 1.316 | .464 | .0010 | chunk-final bias |

Die vollständige Tabelle enthält zusätzlich die bestehenden linken Familien
`Ce` und `ok`.  Die vier strikten Nichtbesteher sind links `o`, links `qok`
(`p=.05095` trotz 6/6 Richtungszeichen), rechts `o` und rechts `ol`
(`p=.05894`).  Nahe Schwellenwerte werden nicht aufgerundet.

Diese Familienrollen sind richtungsgebundene Außenkontext-Träger.  Sie sind
keine Präfixe, Suffixe oder Wörter im linguistischen Sinn.

## Klare Gegenbeispiele und Grenzen

### Standalone ist nicht aus Komponenten-Standalone ableitbar

Die preregistrierte Standalone-Komposition verwendet das geometrische Mittel
der beiden Komponenten-Standalone-Raten.  Sie scheitert deutlich:

| Modell | held Standalone-Logloss | mittlerer Ratenfehler |
|---|---:|---:|
| ATOMIC | **0.4078** | **0.0366** |
| GLOBAL | 0.6523 | — |
| LOMO | 0.6911 | 0.2020 |
| DIRECT | **0.9846** | **0.2586** |

Damit reicht getrennte Seiteninformation nicht für die gemeinsame Aussage
“beide Enden zugleich”.  Gerade tiefe `qok+X`-Merges sind fast immer
Standalone, obwohl `qok` selbst es kaum ist.  Diese Joint-Abhängigkeit sitzt in
der Paaridentität.

### Merge-Profile driften stärker als gleich häufige Nichtausgaben

Jede Merge-Ausgabe wurde mit Ersetzung an die nächsthäufige Unit gematcht, die
keine Ausgabe einer der 64 Regeln ist.  Der train→held Fehler der sieben
Kantenraten beträgt bei Merges 0.02174, bei Kontrollen 0.01581
(`sign-flip p=.0080`).  Merge-Identitäten sind also nicht deshalb stabil, weil
sie bloß häufiger wären.  Die Nachbar-JS-Divergenz ist bei Merges 0.05845 und
Kontrollen 0.06538; dieser kleine Vorteil bleibt grenzwertig (`p=.0563`).

### BPE-Komposition ist formal erwartbar, aber nicht tautologisch

Ein registriertes `L+R` ist definitionsgemäß eine geordnete Konkatenation; eine
gerichtete Außenkante ist deshalb ein natürlicher formaler Mechanismus.  Die
verwendeten `L`- und `R`-Profile stammen jedoch aus ihren **anderen**, im finalen
98-Unit-Strom verbliebenen Vorkommen, nicht aus denjenigen Paarvorkommen, die
bereits zu `M` verschmolzen wurden.  Der held-Transfer und das mobile Donorpaar-
Nullmodell zeigen daher echte Wiederverwendung des Außenkontexts.  Gleichwohl
kann dieselbe Erscheinung vollständig durch wiederkehrende Graphemumgebungen
und den trainierten BPE-Algorithmus entstehen.  Sie identifiziert keine
sprachliche Morphologie.

## Bezug zur GDT606-W-Kategorie und deren destroyed Null

Für alle 64 Merge-Ausgaben wurden nur die Kategoriehäufigkeiten aus den 36
realen und 12 order-destroyed GDT606-Schlüsseln übernommen; kein generierter
Output wurde angesehen oder übertragen.

| Zusammenhang | Wert |
|---|---:|
| Kompositionsgewinn vs reale W-Fraktion, Spearman | 0.0778 |
| Kompositionsgewinn vs destroyed W-Fraktion, Spearman | 0.2305 |
| Train-Frequenz vs reale W-Fraktion, Spearman | **0.6523** |
| Kompositionsgewinn vs reale W-Fraktion nach linearer Frequenzkontrolle | -0.2387 |
| Kompositionsgewinn vs destroyed W-Fraktion nach Frequenzkontrolle | -0.1120 |

W markiert somit nicht die am stärksten kompositionellen Merge-Einheiten.  Die
bereits bekannte Frequenz-/Kapazitätsarchitektur bleibt die bessere Erklärung.
W darf weder als “Ganzwort” noch als Stammrollenklasse semantisiert werden.

## Endinterpretation

Die 98-Unit-Schicht hat eine hierarchische, gerichtete Backoffstruktur:

```text
linke Komponente  -> linker Außenkontext + Initialtendenz
rechte Komponente -> rechter Außenkontext + Finaltendenz
exakte Merge-ID   -> Joint-/Standalone- und paarspezifische Residualrolle
```

Diese Architektur ist praktisch verwertbar: Für seltene tiefe Einheiten kann
die Komposition einen besseren formalen Backoff liefern als deren kleine eigene
Train-Stichprobe.  Sie rechtfertigt aber keine Stammübersetzung.  Besonders die
`o`-Familie verhindert einen einheitlichen Schlüssel: gleiche linke Komponente,
mehrere deutlich verschiedene held Rollen.  Der nächste Decoder darf
Komponentenprofile als geglätteten Prior verwenden, muss aber die exakte
Merge-Identität und Joint-Grenzabhängigkeiten erhalten.

## Reproduzierbare Artefakte

- `PREREGISTRATION.md`: eingefrorene Modelle, Nulls und Gates.
- `src/analyze.py`: End-to-End-Auswertung.
- `merge_tree.tsv`: alle 64 registrierten direkten Zerlegungen und Blätter.
- `unit_profiles.tsv`: train/held Profile aller 98 Units.
- `merge_composition_scores.tsv`: alle vier Modelle für alle Merges.
- `model_feature_scores.tsv`: Scores pro Merkmal und Modell.
- `nominated_pairs.tsv`, `nominated_pair_verdicts.tsv`: die sechs Pflichtpaare.
- `stem_family_roles.tsv`, `stable_stem_role_summary.tsv`,
  `stem_family_children.tsv`: Familiengates und Kinder.
- `lomo_predictions.tsv`, `lomo_coefficients.tsv`: train-only Backoffregression.
- `matched_frequency_controls.tsv`, `mobile_null_scores.tsv`,
  `held_folio_model_scores.tsv`: Null- und Stabilitätsresultate.
- `w_composition_diagnostic.tsv`: reale/destroyed W-Diagnose ohne Outputwerte.
- `compositional_counterexamples.tsv`, `tree_depth_summary.tsv`: Grenzen.
- `RESULT.json`, `ARTIFACT_MANIFEST.json`: kompakte Resultate und Hashbindung.
- `src/validate.py`, `VALIDATION.json`: unabhängige Rekonstruktion und Prüfung.
