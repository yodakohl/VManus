# GDT242 — f82r paragraph-coordinate correction

## Result

**GDT229_F82R_RECORD_COORDINATE_INVALID_THREE_PARAGRAPHS_COLLAPSED**

The f82r abstract role projection used the wrong record coordinate.  The human
catalogue states that f82r contains three prose paragraphs, and the source line
codes mark starts at f82r.1 (`@P0`), f82r.11 (`@P0`), and f82r.20 (`*P0`).
None of those three start loci occurs in the complete-line frame used by
GDT224/GDT229.  Consequently all eight covered role-scaffold loci were assigned
to one historical key, `Q13|f82r|R01`.

| corrected paragraph | physical prose loci | HPR2-covered loci | formal fields on covered loci | old role-covered loci |
|---|---:|---:|---:|---:|
| P1, f82r.1–.9 | 9 | 6 | 17 | 4 |
| P2, f82r.11–.19 | 9 | 5 | 17 | 1 |
| P3, f82r.20–.33 | 14 | 6 | 17 | 3 |

The equal count of 17 formal fields in each **covered subset** is descriptive
only.  Each paragraph has missing lines, so it is not an authorial 17-field
cardinality.

## Correction

Withdraw the f82r-specific GDT229/GDT239 record-relative role counts: the
reported 16 short-argument-like and 10 instruction-clause-like fields depended
on positions within a merged three-paragraph record.  They cannot support the
f82r page interpretation.

Retain the underlying source and formal layers:

- all human visual annotations and ownership grades;
- all consensus family expressions;
- all 51 GDT241 formal fields, PAGE_HOSTs, compiler cells, and DY/line ends;
- the transferred label/relation renderer;
- the broad q13 document prior as an abductive hypothesis.

The correction is local to f82r.  It does not by itself invalidate GDT229 rows
on other pages, but it establishes that any page whose paragraph-start line is
missing from the complete-line frame needs the same audit before its
record-relative roles are used.

## Translation consequence

The f82r page dossier is now structurally richer but semantically thinner:

```text
three physical paragraph records
  each containing a partially observed chain of HPR2 fields
  plus separately placed graphical labels
```

The therapeutic/hydraulic, case/indication, apparatus-key, and nonsemantic
worlds remain candidates, but the old short-versus-long role balance no longer
ranks them on f82r.  Replacement roles require an uncertainty-aware paragraph
coordinate and a fresh application of the external instrument.

## Claim ceiling

This is a coordinate correction.  It supplies no replacement role, field
ownership, object, action, material, word, language, plaintext, or translation.
No f84 input was read or retained and no f84 result was scored.
