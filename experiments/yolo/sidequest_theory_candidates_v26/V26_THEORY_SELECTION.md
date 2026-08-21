# V26 selection — fields are clauses; lines are layout

Date: 2026-08-22

Status: **complete speculative sentence/operation segmentation**.

## Result

The 381 prose events form:

- 135 grammar-derived fields;
- 11 complete records;
- 90 DY/B3-committed steps;
- 45 open continuations.

This produces a much clearer register contrast than physical lines:

| register | fields | committed | open |
|---|---:|---:|---:|
| four Herbal pages | 20 | 5 | 15 |
| three Biological pages | 115 | 85 | 30 |

Herbal is therefore continuous illustrated article prose fitted around a plant.
Biological is a committed application worksheet made of many short executable
steps. The two sections can share cards while compiling them into different
document grammars.

## Reading rule

```text
physical line end   no automatic sentence boundary
SPACE/JOIN field    local clause or operand package
DY close            commit one local operation
B3 close            commit a major step or record-sized unit
OPEN field          retain owner, batch and discourse state; continue
```

This explains why a Herbal instruction can begin on one line and finish several
lines later, while a Bio line can contain several separately closed operations.

## Concrete consequences

- f10r's first record contains two open fields forming one root preparation,
  not two sentences.
- f11r commits the first clarified-liquor step, then continues with crown,
  poultice and application fields.
- f55v contains three committed recipe steps inside one illustrated article.
- f56r is one seven-field dossier whose repeated NEXT-PART card introduces new
  plant organs without ending the article.
- f82r contains 26 fields, many one-card committed operations; the seven-cell
  stencil on f82r.27 is genuinely a sequence of closed substeps.
- f83r contains four records and 65 fields, explaining why it reads as a sheet
  of alternative application configurations rather than one long recipe.

## Edition

`V26_COMPLETE_135_FIELD_TRANSLATION.tsv` publishes every field with its visible
source, literal translation and closure reading. `V26_COMPLETE_11_RECORD_TRANSLATION.tsv`
reassembles those fields into eleven complete articles or worksheets.

The English content remains the forced working translation. The new result is
the clause hierarchy: line is layout, field is the local construction, closure
commits a step, and record holds the continuing owner/process state. This does
not establish ordinary sentence syntax, a specific language or plaintext. f84
and f84r remained sealed.
