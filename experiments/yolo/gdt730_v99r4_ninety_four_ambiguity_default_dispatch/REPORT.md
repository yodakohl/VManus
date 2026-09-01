# GDT730 report — V99R4 single-default consolidation

Status: `PASS_V99R4_94_AMBIGUOUS_GLOBAL_WHOLES__1039_OCCURRENCES__TECHNICAL_SELECTOR_95_ROWS_1050_OCCURRENCES__CPHOL_LEXICAL_FALSE_POSITIVE__MAIN_AND_CONTEXT_DEFAULTS_AMBIGUITY_FREE__GDT730_PROVENANCE_APPENDED__SCORE_CONFIDENCE_EVIDENCE_SCOPE_EXPORT_SPAN_STRUCTURE_ACTION_UNCHANGED__ZERO_COMPONENT_CREDIT`

## Result

The broad selector found 95 global rows with 1,050 occurrences. One was not a
semantic ambiguity: `cphol = zusammengesetzter Drogenstoff` matched only
because `menge` occurs inside `zusammengesetzter`. GDT730 therefore changes
exactly 94 rows with 1,039 occurrences and keeps `cphol` byte-identical.

Every target now has one default in both semantic-rendering fields. The rival
reading remains attached to the audit; it no longer leaks into the spoken
default through a slash, `oder`, or unresolved `Menge` label.

| Family | Rows | Occurrences | Working policy |
|---|---:|---:|---|
| learned technical wholes | 12 | 148 | one form, state, entry or measured-input reading |
| open value wholes | 3 | 116 | indexed value or field boundary without a fabricated unit |
| plant wholes | 25 | 341 | global Pflanzendroge/material; Blattgut stays a local rival |
| powder wholes | 8 | 38 | Pulver, Pulveranteil, Pulverpaste and preparations |
| quantity wholes | 8 | 90 | cardinal amount or measured DAL input, kept distinct |
| root wholes | 12 | 30 | Wurzeldroge, preparation, share and processing state |
| seed wholes | 20 | 233 | Samen, preparation, quantity class and processing state |
| wood wholes | 6 | 43 | Holzdroge, measure and preparation states |

Representative practical defaults include:

- `chcthy` → `trockenes Pflanzenmaterial`
- `shcthy` → `feuchtes Pflanzenmaterial`
- `dail` → `abgewogener Rohstoffposten II`
- `cthar` → `Pflanzenanteil I`
- `paiir` → `Pulveranteil III`
- `pshedy` → `Pulverpaste`
- `sshedy` → `eingeweichte Samen`
- `ydy` → `Wertfeldgrenze`

The complete old/new table is
`artifacts/V99R4_94_AMBIGUITY_DEFAULT_AUDIT.tsv`.

## Confidence and evidence

No confidence was upgraded merely because a default was selected. The 94
targets retain 20 W3, 48 W2, 20 W1 and six W0 readings. Every row still carries
its inherited positive evidence and counterevidence; the separate evidence
table binds those fields by hash. Component and historical-relation credit are
zero throughout.

Three inherited comparator decks show that learned drug names, plant-part and
quality slots, compact form systems, dosage rubrics and relative parts all
occur in late-medieval technical manuscripts. They constrain the style of the
working codebook but do not identify a Voynich sign or word.

## Controls and limits

All 324 active V99 readings, 1,168 non-target global rows, fourteen GDT729
targets and five active reader artifacts are unchanged. Only the target
semantic, provenance and audit fields move; scores, confidence, evidence,
scope, spans, source-reading identities, export permissions and action or
structural flags do not.

V99R4 is still a working dictionary, not verified plaintext. The immediate
next useful pass is to test how much concrete prose these defaults actually
produce in fixed already-admitted passages and to inventory the remaining
abstract `Wertstufe`, form, charge and entry labels that still block a practical
reading. No new page is needed for that test.
