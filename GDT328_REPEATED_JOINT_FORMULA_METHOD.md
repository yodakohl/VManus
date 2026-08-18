# GDT328 — repeated joint-formula atlas

## Question

Does the f84-free GDT327 interlinear contain exact multi-group field formulas
that recur on different physical folios, and do any of them preserve a stable
record position across registers?

This is an exploratory, post-hoc atlas.  It does not test meanings and it does
not turn a recurrent source string into a word, phrase, or translation.

## Frozen input and units

The sole scientific source is `gdt327_joint_tuple_interlinear.tsv`.  Its 8,448
rows are grouped by `(page, locus, field_ordinal)` and ordered by physical
`group_index`.  Only complete fields of at least two source groups are
eligible.  No f84 row is present in the input.

Two formula resolutions are inventoried separately:

1. `EXACT_JOINT_SEQUENCE`: the ordered sequence of opaque GDT327 joint-tuple
   IDs, including PAGE_HOST and all compiler coordinates;
2. `PAGE_HOST_SEQUENCE`: the ordered sequence of opaque PAGE_HOST IDs,
   ignoring renderer differences while retaining the field boundary.

A formula enters the atlas only when it occurs on at least two physical
folios.  ZL3b/IT2a/RF1b are not counted as replications; GDT327 supplies one
source-native event stream.

## Ranking and positional diagnostic

Formulas are ranked without a fitted score: longer sequence, more physical
folios, more occurrences, then higher modal-field purity.  For each formula we
report its modal field ordinal and the fraction of occurrences at that
ordinal.

For the unique recurrent three-group PAGE_HOST formula, a predeclared
descriptive positional diagnostic conditions on each occurrence's register
and on field length three.  It reports the product of the empirical
same-register probabilities of landing at the observed field ordinal, plus
the probability that all occurrences land at *any* common ordinal.  These are
post-hoc empirical diagnostics, not confirmation p-values: the formula was
noticed before this method was written and the corpus itself supplied the
candidate.

## Display reconstruction

Display strings are reconstructed solely from the already frozen GDT278
components carried by GDT327's source lineage:

`WRAPPER + INNER_D + O/OT_FRAME + PAGE_HOST + RIGHT_FAMILY + B3(m) + DY`.

The reconstruction is accepted only if its SHA-256 equals the frozen source
surface hash for every event.  Display strings are audit aids; opaque tuple
IDs remain the analytical objects.

## Claim ceiling

GDT328 can identify a reusable structural field formula and a stable record
position.  It cannot assign a word boundary, linguistic phrase, semantic
role, object, meaning, language, plaintext, or translation.  f84 is not
opened, parsed, retained, joined, or scored.
