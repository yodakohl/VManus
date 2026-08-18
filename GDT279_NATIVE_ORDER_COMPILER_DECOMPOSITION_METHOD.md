# GDT279 — native-order compiler decomposition

## Question

GDT278 froze the compiler-conditioned character-form magnitude before adding
controls.  No admitted control reproduced the Voynich magnitude on the exact
4,476-event overlay, while three real Latin diplomatic panels exceeded the
native-order reference.  GDT279 does not add a corpus, change that endpoint,
or reinterpret it.  It asks which already-frozen part of the compiler context
creates the order-sensitive excess.

This method and `gdt279_design.json` are frozen before GDT279 scoring.

## Frozen source panel and views

All GDT278 bytes listed in `gdt279_gdt278_freeze_manifest.tsv` remain fixed.
Every admitted GDT278 panel is retained.  Three observation views are allowed:

1. `LENGTH_MATCHED_OVERLAY` is the published GDT278 4,476-event overlay.
2. `MATCHED_SAMPLE_NATIVE_LAYOUT` takes the **same source occurrences and the
   same 20-symbol map** used in view 1, restores their source folio, page, line,
   record and group order, and changes nothing else.  It is available only for
   panels that passed the GDT278 exact-length capacity check.
3. `NATIVE_ORDER` is the published GDT278 native sample (all eligible events or
   the fixed 8,448-event source-unit sample).

The intermediate view is the causal bridge.  For a control with all three
views, full-model saving differences are reported as

```text
LAYOUT_DELTA    = MATCHED_SAMPLE_NATIVE_LAYOUT - LENGTH_MATCHED_OVERLAY
SELECTION_DELTA = NATIVE_ORDER - MATCHED_SAMPLE_NATIVE_LAYOUT
```

in normalized saving bits/event.  The layout delta holds source-occurrence
selection, mapped host strings and length distribution exactly fixed.  The
selection delta changes the event sample and therefore remains descriptive.
Neither contrast is a randomized intervention on a historical manuscript.

## Frozen compiler blocks

The published 14-field GDT276/GDT278 compiler tuple is partitioned exactly once:

- `OPPORTUNITY`: register, record ordinal, field ordinal, within-field position;
- `EDGE_COMPILER`: wrapper, q flag, local O/OT frame, inner-D, right family,
  known label/display renderer;
- `CLOSURE_BOUNDARY`: DY, B3, physical-line close, paragraph close.

All eight subsets of those three blocks are scored with the inherited
256-bucket SHA-256 context map.  `FULL` is byte-for-field equivalent to the
published compiler tuple.  `EMPTY` has one context.  No glyph, host substring,
meaning, language, or oracle field is added.

For subset `S`, retain the GDT278 magnitude functional

```text
T(S) = mean(null held bits for S) - observed held bits for S
T_event(S) = T(S) / events.
```

The same 64 GDT276 permutations and the same exact strata
`register × record_ordinal × within_field_position × host_length` are used for
every subset.  One event permutation is shared by all subsets in a world.
Because register, record ordinal and within-field position are conditioned by
the null, a pure `OPPORTUNITY` effect is deliberately mostly inestimable; its
interactions with field ordinal, edges and closure remain measurable.

Exact three-player Shapley values of `T_event` allocate the full matched saving
to the three frozen blocks.  Values may be negative.  Shapley values are a
descriptive allocation of this fixed compression score, not semantic effects.

## Representation safety

The primary decomposition uses the frozen published GDT278 representation so
that every view can be compared byte-for-field.  A mandatory leakage
sensitivity relearns the parser/operation inventory and 20-symbol alphabet
without each held scoring folio, using the exact GDT278 procedure.  It scores
all eight observed subset models and the 64-world null for `FULL`; no held
folio contributes to its representation or training counts.  The safe
full-model magnitude must be reported beside the published value.  Safe block
attribution uses Shapley values of the observed `EMPTY minus subset` held-bit
improvement, because running 64 separate safe nulls for every subset would add
no new endpoint and would be a different search family.

## Fixed summaries and decision

Report every panel and view.  The mechanistic headline is restricted to the
three GDT278 native reproductions and, for layout contrasts, to the subset with
an eligible matched view.  The leading block is the largest signed Shapley
contribution to positive saving; ties use the literal order
`OPPORTUNITY`, `EDGE_COMPILER`, `CLOSURE_BOUNDARY`.

The result label is mechanical:

- `NATIVE_EXCESS_SHARED_EDGE_COMPILER_LEAD` if every eligible positive Latin
  panel has a positive layout delta led by `EDGE_COMPILER`;
- `NATIVE_EXCESS_SHARED_CLOSURE_BOUNDARY_LEAD` analogously;
- `NATIVE_EXCESS_SHARED_OPPORTUNITY_INTERACTION_LEAD` analogously;
- otherwise `NATIVE_EXCESS_MECHANISM_HETEROGENEOUS`.

The source-selection contribution, every counterexample, safe/published
difference, and absence of a matched view must remain visible.  No p-value is
created by choosing the largest Shapley component.

## Claim ceiling and seal

GDT279 may localize an exposed compression difference to document opportunity,
source-edge compiler fields, closure/boundary fields, or their interactions.
It cannot establish an abbreviation system, language, code, notation,
meaning, plaintext, or translation.

No f84 source is an input.  Only the already-published f84-free GDT276/GDT278
Voynich inventory is permitted.  No f84 row may be opened, parsed, retained,
joined, or scored.
