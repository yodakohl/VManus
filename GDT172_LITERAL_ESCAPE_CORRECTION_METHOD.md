# GDT172 — unchanged-graphematic literal escape sensitivity

Status at registration: **FROZEN_LITERAL_ONLY_CORRECTION_BEFORE_BLIND_RERUN**.

## Question

GDT171 encoded every source type outside its frozen 384-entry frequent
lexical-ID table as `w` followed by a reversible base-19 encoding of the UTF-8
bytes.  That channel was mechanically clean but historically artificial and
made most rare source forms much longer.  GDT172 asks whether the GDT171
instrument findings survive when the literal channel is instead:

```text
escape marker `w` + unchanged source graphematic form
```

This is a sensitivity correction, not a new encoder search.  No parameter is
selected from Voynich statistics or from GDT172 outcomes.

## Frozen invariants

GDT172 is derived row-for-row from the published GDT171 observation and oracle
layers.  It must preserve exactly:

- all 384 frequent lexical-ID assignments and lookup rows;
- the System-A and System-B frequent-row fields;
- source order, register allocation, partial register overlap, hand allocation,
  folio, record, physical-line, separator and layout fields;
- observation identifiers and anonymous world labels;
- the small deterministic S2 frequent-ID spelling variants; and
- every frequent-row visible surface string.

Only rows already marked `LITERAL_ESCAPE` may change.  On those rows the
canonical and rendered host become the unchanged `source_form`; the existing
escape marker remains `w`; all outer record/layout fields remain frozen.

System B is explicitly an **factorial distributed control**, not a
historical-naturalistic encoding.  Its published 384-row Cartesian allocation
is retained because this run isolates the literal channel.  A possible B2 with
a separately frozen hand-authored/non-Cartesian table is deferred and is not
part of GDT172.

## Blind instrument

The GDT170/GDT171 blind parser, operation discovery thresholds, operation
limits, layout-assisted ranking, diagnostics, smoothing and null sizes are
inherited unchanged.  The oracle and frequent lookup remain forbidden until
the blind parse and diagnostics are frozen.

Before execution, descriptive material-change rules are frozen:

- a recovery rate or information-fraction shift is material at absolute
  change at least 0.05;
- a signed diagnostic gain changes materially if its sign changes or its
  absolute change is at least 10% of the absolute GDT171 value (with zero
  anchors reported descriptively);
- the selected operation library changes materially if side-aware Jaccard is
  below 0.80; and
- any change from zero to nonzero, or conversely, in a discrete exact-hit
  count is reported explicitly whether or not a rate threshold is crossed.

Frequent-ID recovery and global all-row diagnostics are evaluated separately.
Because frequent visible rows are byte-identical, any frequent-ID change can
only arise indirectly through corpus-wide operation discovery.

## Claim ceiling

GDT172 can establish only whether the GDT171 synthetic instrument calibration
is sensitive to its artificial literal representation.  It cannot establish a
Voynich lexical unit, code value, compiler, language, meaning, plaintext or
translation.  No Voynich source, image or f84 material is an input.
