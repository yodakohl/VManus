# GDT684 — V57 semantic debt priority reader

V57 remains formally complete at 479/479 positions. The strict repair queue contains 139/479 card positions; the broader information audit marks 335/479 positions as identity-, object-, axis-, register- or resolution-open.
An independent five-selector literal audit flags 172/479 positions. Across all three layers, 371/479 positions carry at least one debt signal and only 108/479 carry none.

## Disjoint position classes

- `A1_LICENSED_OPERATION`: 71 positions / 56 surfaces; route `NONE`.
- `A2_IDENTITY_BEARING_ENTITY`: 73 positions / 65 surfaces; route `NONE`.
- `B1_LICENSED_OPERATION_WITH_GENERIC_OBJECT`: 13 positions / 9 surfaces; route `OBJECT_IDENTITY_BINDING`.
- `B2_LICENSED_OPERATION_WITH_REGISTER_WRAPPER`: 2 positions / 2 surfaces; route `REGISTER_WRAPPER_DISPATCH`.
- `C1_FUNCTIONAL_MATERIAL_ROLE_ONLY`: 165 positions / 121 surfaces; route `INGREDIENT_IDENTITY_SEARCH`.
- `C2_STATE_WITHOUT_OBJECT`: 72 positions / 37 surfaces; route `STATE_HOST_BINDING`.
- `C3_VALUE_WITHOUT_AXIS_OR_OBJECT`: 22 positions / 8 surfaces; route `VALUE_AXIS_BINDING`.
- `D1_UNRESOLVED_COMPONENT`: 20 positions / 2 surfaces; route `BOUNDARY_OR_COMPONENT_RECONCILIATION`.
- `D2_STRUCTURAL_OR_REGISTER_META`: 21 positions / 9 surfaces; route `STRUCTURAL_TO_PRACTICAL_CARD`.
- `D3_GENERIC_CARRIER`: 19 positions / 13 surfaces; route `PRODUCTIVE_CARRIER_COMPOSITION`.
- `D4_UNLICENSED_LITERAL_ACTION`: 1 positions / 1 surfaces; route `ACTION_SCOPE_REVIEW`.

## Highest-priority debt cards

| rank | surface | positions | class | current gloss | route |
|---:|---|---:|---|---|---|
| 1 | `olkar` | 16 | D1_UNRESOLVED_COMPONENT:16 | erste erhitzte Drogenfraktion im Ansatz; Holzbindung offen | `BOUNDARY_OR_COMPONENT_RECONCILIATION` |
| 2 | `chol` | 6 | D3_GENERIC_CARRIER:6 | trocken; nominal trockenes Gut/Material | `PRODUCTIVE_CARRIER_COMPOSITION` |
| 3 | `olam` | 4 | D1_UNRESOLVED_COMPONENT:4 | ein Maß Ansatz-/Drogenmaterial; Holzbindung offen | `BOUNDARY_OR_COMPONENT_RECONCILIATION` |
| 4 | `aiin` | 7 | C3_VALUE_WITHOUT_AXIS_OR_OBJECT:7 | Menge III | `VALUE_AXIS_BINDING` |
| 5 | `dy` | 3 | D2_STRUCTURAL_OR_REGISTER_META:3 | Qualitäts-/Wertfeld geschlossen | `STRUCTURAL_TO_PRACTICAL_CARD` |
| 6 | `daiin` | 6 | C3_VALUE_WITHOUT_AXIS_OR_OBJECT:6 | Grad-/Maßwert III | `VALUE_AXIS_BINDING` |
| 7 | `or` | 5 | C1_FUNCTIONAL_MATERIAL_ROLE_ONLY:5 | Drogenportion | `INGREDIENT_IDENTITY_SEARCH` |
| 8 | `y` | 3 | D2_STRUCTURAL_OR_REGISTER_META:3 | hierzu: | `STRUCTURAL_TO_PRACTICAL_CARD` |
| 9 | `okal` | 4 | C1_FUNCTIONAL_MATERIAL_ROLE_ONLY:4 | Rohstoffklasse I im Ansatz, heiß am Gradanfang | `INGREDIENT_IDENTITY_SEARCH` |
| 10 | `qol` | 4 | B1_LICENSED_OPERATION_WITH_GENERIC_OBJECT:4 | Drogenstoff zugeben | `OBJECT_IDENTITY_BINDING` |
| 11 | `al` | 3 | C1_FUNCTIONAL_MATERIAL_ROLE_ONLY:3 | Rohstoffklasse I | `INGREDIENT_IDENTITY_SEARCH` |
| 12 | `dain` | 3 | C3_VALUE_WITHOUT_AXIS_OR_OBJECT:3 | Grad-/Maßwert II | `VALUE_AXIS_BINDING` |
| 13 | `oror` | 3 | C1_FUNCTIONAL_MATERIAL_ROLE_ONLY:3 | zwei Portionen | `INGREDIENT_IDENTITY_SEARCH` |
| 14 | `shor` | 3 | A2_IDENTITY_BEARING_ENTITY:3 | Blüten-/Fruchtstand; reproduktiver Teil | `NONE` |
| 15 | `qodaiin` | 1 | C3_VALUE_WITHOUT_AXIS_OR_OBJECT:1 | Qualitätsgrad III | `VALUE_AXIS_BINDING` |
| 16 | `dchey` | 0 | A1_LICENSED_OPERATION:9|D4_UNLICENSED_LITERAL_ACTION:1 | eine Dosis bis zur Mittelstufe trocknen und abschließen | `ACTION_SCOPE_REVIEW` |
| 17 | `chal` | 2 | C1_FUNCTIONAL_MATERIAL_ROLE_ONLY:2 | Rohstoffklasse I, trocken am Gradanfang | `INGREDIENT_IDENTITY_SEARCH` |
| 18 | `chepy` | 2 | A2_IDENTITY_BEARING_ENTITY:2 | Trockenpulver in Grundform | `NONE` |
| 19 | `chor` | 2 | A2_IDENTITY_BEARING_ENTITY:2 | Pflanzen-/Reproduktionsteil | `NONE` |
| 20 | `qoekol` | 2 | B1_LICENSED_OPERATION_WITH_GENERIC_OBJECT:2 | heißen Drogenstoff der Mittelstufe zugeben | `OBJECT_IDENTITY_BINDING` |

## Action-layer warning

The source ledger licenses 86 action positions. Practical prose adds 74 operation-label-by-line pairs on 29 lines that are absent from the licensed token-action glosses. These are audit targets, not automatically valid inferred syntax.

## Provisional learned-base warning

Five free V57 `ol` positions retain the GDT664 working card `Grundansatz`. GDT664 marks that learned whole-word card MEDIUM, not confirmed. All five already sit inside the broad specificity-open census and now appear in `V57_PROVISIONAL_SEMANTIC_CONFIDENCE_WATCH.tsv`; they do not enlarge the narrower 139-position renderer-repair queue.

## Low-confidence card provenance

Exact surface-plus-current-gloss joins recover 30 V57 positions / 28 cards whose published source is LOW or EXPLORATORY. Ten of these positions had no signal in the strict, broad or mechanical layers, so adding confidence provenance leaves only 98/479 positions without a current debt or low-confidence flag.

## Next repair family

The shortest productive repair is the state+OL carrier family: `chol` 6×, `shol` 1×, `tol` 1×. GDT683 supplies `ol = Grundansatz`; the next occurrence circuit must test whether CH/SH/T predict dry/wet/cold preparation cards at every admitted exact occurrence before rewriting V57.

The free `l` on f111v.18 is not counted in V57. It is retained in `OUTSIDE_V57_COMPANION_DEBTS.tsv` as a separate global route.
