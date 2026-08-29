# GDT632 artifacts

## Quelle und Hauptpopulation

- `PAGE_ALLOWLIST.tsv`: 179 explizit erlaubte Seiten; f1r/f84/f84r fehlen.
- `INTERFIX_FAMILY_OCCURRENCES.tsv`: 255 fusionierte ZL3b-Vorkommen des exakten
  `ch/sh+(∅|e|o|eo)+cth+R`-Rasters.
- `INTERFIX_CELL_SUMMARY.tsv`: Token-, Typen-, Seiten- und Stabilitätszahlen der
  acht Zellen.
- `INTERFIX_REMAINDER_MATRIX.tsv`: vollständiges Rest×Qualität×Interfix-Raster
  einschließlich leerer Zellen.
- `SHARED_REMAINDER_PAIRS.tsv`: zwölf direkte `ch/sh`-Gegenpaare mit gleichem
  Zwischenfeld und Rest.
- `EXPRESSION_POPULATION_SUMMARY.tsv`: getrennte Zählstände 255/262/265/266,
  damit Wortgrenznormalisierung nie als fusionierte Grundbeobachtung erscheint.

## Leser- und Wortgrenzen

- `CROSS_READER_INTERFIX_REALIZATIONS.tsv`: Zielspanne in ZL3b/IT2a/RF1b als
  fusioniert, getrennt oder abweichend.
- `CROSS_READER_INTERFIX_BOUNDARY_BRIDGES.tsv`: neun konkrete Leserbrücken samt
  fünf direkten linken Shellgrenzen, einer direkten `sh|cth`-Grenze, einer
  überlappenden linken Grenze und zwei nichtdiagnostischen Warnungen.
- `ALL_READER_SEPARATED_SHELL_CTH_SPANS.tsv`: sieben in allen Lesungen getrennte
  Shell-CTH-Ausdrücke, darunter drei split-only-Kompositionsvorhersagen.
- `BOUNDARY_ORIENTATION_SUMMARY.tsv`: konservative und inklusive Orientierung
  der sichtbaren Grenze.
- `ALTERNATIVE_INTERNAL_BOUNDARY_NULL.tsv`: vollständige Nullsuche nach
  `ch/sh | e/o/eo+cthR` und `ch/sh | e/o/eo | cthR`.
- `OUTER_FAMILY_BOUNDARY_BRIDGES.tsv`: vier dreifach normalisierte und eine
  paarweise äußere Fusions-/Spaltgrenze.
- `LEFT_QUALITY_SHELLS.tsv`: die acht sichtbaren linken Blöcke
  `ch/che/cho/cheo` und `sh/she/sho/sheo`.

## Innere E/O-Hierarchie

- `INNER_CTH_HEAD_PREFIX_SUMMARY.tsv`: nackte `cth/ecth/octh/eocth`-Köpfe;
  408/0/32/0 Token.
- `INNER_CTH_HEAD_REMAINDER_MATRIX.tsv`: Restgitter der vier nackten Kopfreihen.
- `HIERARCHICAL_E_O_BASE_COVERAGE.tsv`: fusionierte und inklusive Abdeckung der
  vorhergesagten `cthR`- beziehungsweise `octhR`-Basis. Die inklusive
  O-/EO-Reihe erreicht 54/55 und nennt `octheey` als einzige Lücke.
- `E_O_ORDER_CONTROL.tsv`: zehn `ch/sh+eo+cth` gegen null
  `ch/sh+oe+cth` sowie die nackten Kopfkontrollen.
- `CROSS_READER_E_O_HEAD_CONTROL.tsv`: dieselben Kopf-, Split- und
  Reihenfolgenkontrollen getrennt nach den drei Lesungen.
- `OUT_OF_LATTICE_Q_CTH_FORMS.tsv`: die fünf Formen außerhalb des
  255/260-Zielrasters—zwei `ee`-Rivalen und drei äußere OL/CH-Komposita.

## Register und lokale Paradigmen

- `INTERFIX_SECTION_PROFILE.tsv`: acht Zellen nach Manuskriptsektion.
- `INTERFIX_REGISTER_PROFILE.tsv`: Profile nach Sektion, Currier-Sprache und
  Hand für alle vier Populationen mit 255/262/265/266 Vorkommen.
- `INTERFIX_PAGE_COEXISTENCE.tsv`: Seitenkoexistenz in denselben vier
  Populationen; Gegenprobe zu einem deterministischen Seiten-/Handersatz.
- `FIXED_CONTEXT_PARADIGMS.tsv`: gleiche linke und rechte Nachbarn bei
  wechselnder Zielzelle.
- `ONE_SIDED_CONTEXT_PARADIGMS.tsv`: wiederkehrende einseitige Kontexte.
- `SHARED_CATEGORY_SLOTS.tsv`: konkrete gemeinsame Slotframes der acht Zellen.

## Konkrete Bedeutungsarbeit

- `INTERFIX_QUALITY_DEGREE_CONTACTS.tsv`: 97 Gradkontakte bis Distanz drei mit
  Material- und Qualitätslesung.
- `INTERFIX_QUALITY_SUMMARY.tsv`: zellenweise unmittelbare, passende,
  gegensinnige und orthogonale Kontakte.
- `INTERFIX_LOCAL_QUALITY_NEIGHBORS.tsv`: direkte Qualitätsnachbarn einschließlich
  der Gegenbeispiele.
- `REPEATED_INTERFIX_CLAUSE_FRAMES.tsv`: neun wiederkehrende konkrete
  Material-/Gradklammern.
- `CONCRETE_CLAUSES_V4.tsv`: 49 lokale Arbeitsübersetzungen ohne Fülltext für
  ungelesene Nachbartoken.
- `INTERFIX_ROLE_RANKING.tsv`: geordnete Hierarchie, Oberflächengrenze,
  Registerklasse und verbleibende Bedeutungsrivalen.
- `WORKING_DICTIONARY_V9.tsv`: 47 geerbte plus zwanzig neue Kompositionskarten;
  `e/o` bleiben lexikalisch offen.

## Reichweite und Reproduktion

- `INHERITED_VISUAL_INTERFIX_SCOPE.tsv`: vier geerbte Bildurteile und die
  ausdrückliche Nullabdeckung der E/O/EO-Ziele; keine neue Bildseite.
- `HISTORICAL_HYBRID_COMPARATORS.tsv`: Pal.lat.1256 und Wellcome MS 542 als
  Architekturvergleiche, nicht als Zeichen- oder Bedeutungsschlüssel.
- `RESULT.json`: kompakte maschinenlesbare Ergebnisschicht mit Eingabe- und
  Ausgabehashes.
- `VALIDATION.json`: deterministischer Replay, Zählbindungen, Seitengrenzen und
  Privacy-Prüfungen.
