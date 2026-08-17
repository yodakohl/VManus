# GDT274 — executable q13 formal grammar checkpoint

## Purpose

Turn the corrected q13 scaffold into one explicit, machine-readable formal
grammar.  This is a synthesis and coverage audit, not a semantic model search.
It records exactly what can currently be parsed and exactly where the content
interpretation remains unknown.

The sole row-level source is the f84-free GDT227 abstract interlinear.  GDT264,
GDT270, GDT271, GDT272, and GDT273 results supply evidence labels only.  No
sealed folio is queried.

## Frozen hierarchy

```text
Q13_PAGE   -> RECORD+
RECORD     -> PHYSICAL_LINE+
PHYSICAL_LINE -> FIELD+
FIELD      -> GROUP{1..}
GROUP      -> COMPILER_CELL(PAGE_HOST)
COMPILER_CELL -> WRAPPER × O_OT_FRAME × INNER_D × RIGHT_FAMILY × DY × B3
```

`PAGE_HOST` and all compiler coordinates are opaque formal values.  A physical
source group is not asserted to be a linguistic word; a field is not asserted
to be a clause or argument.  The GDT227 role-like labels remain archived but
are excluded from the grammar schema because GDT255 showed they are a field-
size relabeling.

The parser serializes all 33 mechanical records, 240 physical lines, 701
fields, and 1,896 source groups.  For every line it also emits four templates:

- exact raw group sequence;
- exact PAGE_HOST sequence;
- exact compiler-cell sequence;
- coarse field sequence, with field size `S12` or `L3P` plus DY/line endpoint.

Cross-folio support is descriptive: it asks whether the identical line
template occurs on another physical folio.  No row shuffling, significance
claim, or semantic inference is attached to this checkpoint.

## Evidence classes

- `CONFIRMED_FORMAL`: reproducible source/boundary or frozen parser structure.
- `EXPLORATORY_REGISTER_LOCAL`: repeatable association limited to q13.
- `WEAK_NONCONFIRMING_TRANSFER`: same-direction external echo that failed its
  frozen gate.
- `NOT_SUPPORTED`: a tested generalization that failed.
- `UNASSIGNED`: content, linguistic function, and meaning.

## Claim ceiling

This checkpoint may state a hierarchical formal generator and distinguish
reusable coarse templates from unique rendered lines.  It may not call a
group a word, a field a clause, assign a semantic role, identify a language,
or produce plaintext or translation.
