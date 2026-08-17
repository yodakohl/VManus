# GDT244 — f80r paragraph-coordinate correction

## Result

**GDT229_F80R_RECORD_COORDINATE_INVALID_FIVE_PARAGRAPHS_COLLAPSED_TO_TWO**

The f82r failure recurs independently on f80r.  The human audit records 43
prose lines in five paragraphs.  At the first source group, at least two
readings mark paragraph starts at f80r.11, .28, .34, .40, and .47.  f80r.18
has a start flag in IT2a alone and is preserved as disagreement rather than
promoted.

GDT229 contains only two f80r record IDs:

| corrected paragraph | physical prose loci | old role-covered loci | historical record |
|---|---:|---:|---|
| P1 | 17 | 7 | R01 |
| P2 | 6 | 2 | R01 |
| P3 | 6 | 1 | R01 |
| P4 | 7 | 3 | R02 |
| P5 | 7 | 1 | R02 |

Thus R01 merges physical paragraphs P1–P3 and R02 merges P4–P5.  The old
record-relative field positions and role predictions are not valid f80r
paragraph coordinates.

## Scope of the correction

Both source-complete GDT002 discovery pages now fail the same audit:

- f80r: five physical paragraphs collapsed to two role records;
- f82r: three physical paragraphs collapsed to one role record.

That makes the issue architectural, not a one-page anomaly.  Until every q13
page receives a full-start audit, treat the q13 record-relative outputs of
GDT224 and their downstream use in GDT227–230 as **unaudited role analogies**.
In particular:

- withdraw f80r-specific GDT229 role sequences;
- do not use GDT227 exact-identity role purity as semantic placement evidence;
- suspend the GDT228 multi-region role-fraction lead;
- treat the GDT229 q13 semantic lattice as a historical hypothesis scaffold,
  not the active field interlinear;
- suspend GDT230 host-role placement rankings.

The following survive unchanged because they do not depend on the faulty
record-relative role coordinate:

- source families and alternate readings;
- HPR2 PAGE_HOST/compiler/DY formal parses;
- GDT231–238 label-prefix, residual, and relation-renderer results;
- GDT240–243 formal coverage and the f82r missingness-aware two-way extent
  result.

## Interpretation

The central generator—a page-conditioned record/compiler architecture—remains
supported formally.  What is lost is the claim that the current q13 field
atlas already places fields into stable recipe-like roles.  Corrected pagewise
paragraph coordinates must be rebuilt before semantic-role exploration resumes.

## Claim ceiling

This is a coordinate and inheritance correction.  It supplies no replacement
semantic role, field ownership, word, language, plaintext, or translation.  No
f84 input was read or retained and no f84 result was scored.
