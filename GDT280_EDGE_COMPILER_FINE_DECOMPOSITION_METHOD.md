# GDT280 — fine decomposition of the frozen edge compiler

## Question

GDT279 found two separate facts.  Restoring native layout removes a negative
opportunity-by-edge mismatch in the positive Latin controls, but the native
compression saving itself is overwhelmingly carried by the already-frozen
`EDGE_COMPILER` block.  GDT280 asks which part of that edge block carries the
incremental saving, and whether Voynich has the same profile.

This method and `gdt280_design.json` are frozen before any GDT280 score is
computed.  GDT278 and GDT279 remain byte-frozen.  No corpus, endpoint, host
substring, glyph predicate, or semantic field is added.

## Frozen panel and views

Reuse all 38 GDT279 panels and exactly its three views:

- `LENGTH_MATCHED_OVERLAY`;
- `MATCHED_SAMPLE_NATIVE_LAYOUT`;
- `NATIVE_ORDER`.

The intermediate view retains the exact GDT278 matched occurrences, mapped
hosts and length distribution while restoring only source layout/order.

## Fixed base and four edge blocks

The base context is always present and contains the GDT279 opportunity plus
closure/boundary fields:

```text
register, record ordinal, field ordinal, within-field position,
DY, B3, physical-line close, paragraph close
```

The frozen `EDGE_COMPILER` block is split once into:

1. `OUTER_WRAPPER`: wrapper and q flag;
2. `LOCAL_FRAME`: O/OT frame and inner-D;
3. `RIGHT_FAMILY`: right-family class;
4. `DISPLAY_RENDERER`: known label/diplomatic display renderer.

All 16 subsets are scored.  `FULL_EDGE` plus the fixed base must reproduce the
GDT279/GDT278 full compiler bucket exactly.  `BASE_NO_EDGE` removes all four
edge blocks but retains every opportunity and closure field.  All models use
the inherited 256-bucket SHA-256 ceiling.

## Frozen score and null

For subset `S`, retain the exact magnitude functional

```text
T(S) = mean(64 inherited-style null held bits) - observed held bits
T_event(S) = T(S) / events.
```

The same GDT276 seed family and exact
`register × record_ordinal × within_field_position × host_length` strata are
used.  A single event permutation is shared across all 16 subsets in each
world.

Exact four-player Shapley values allocate only the incremental edge saving

```text
T_event(FULL_EDGE) - T_event(BASE_NO_EDGE)
```

to the four blocks.  Interactions are distributed by the Shapley rule and may
produce negative contributions.  This is a compression allocation, not an
assignment of grammatical or semantic function.

## Representation safety

The primary allocation uses the byte-frozen GDT279 published representation.
Mandatory sensitivity relearns the parser/operation inventory and the
20-symbol alphabet without each held scoring folio by the exact GDT278/GDT279
procedure.  It scores all 16 observed subset models.  Its full-model null score
is inherited only after exact result/hash checks against GDT279.  Safe Shapley
values allocate observed `BASE_NO_EDGE minus subset` improvement; they are a
leakage sensitivity, not a second null-adjusted endpoint.

## Fixed profile comparison and decision

The mechanistic comparison is restricted to:

- the three GDT278 native-positive Latin controls;
- Voynich native order;
- the two Latin panels with all three views for layout sensitivity.

Within a panel, the leading block is the largest signed Shapley contribution;
ties use the literal block order above.  The decision is mechanical:

- if all three Latin native panels share one positive leading block and
  Voynich has the same positive leader, report
  `VOYNICH_EDGE_PROFILE_SHARES_LATIN_<BLOCK>_LEAD`;
- if all Latin panels share one positive leader but Voynich has another,
  report `VOYNICH_EDGE_PROFILE_DIFFERS_FROM_LATIN_<BLOCK>_LEAD`;
- otherwise report `EDGE_COMPILER_FINE_MECHANISM_HETEROGENEOUS`.

No composite distance, tolerance band, or after-seeing threshold is allowed.
All block values, negative interactions, and safe sensitivities remain public.

## Claim ceiling and f84 seal

GDT280 can say only which visible/source-native edge representation carries an
exposed held-folio character-compression effect.  A display-renderer lead would
not establish abbreviation; a wrapper, frame, or right-family lead would not
establish morphology.  No sound, word, morpheme, language, code, notation,
meaning, plaintext, or translation follows.

No f84 source is an input.  Only the already-published f84-free Voynich event
inventory may be used.  No f84 row may be opened, parsed, retained, joined, or
scored.
