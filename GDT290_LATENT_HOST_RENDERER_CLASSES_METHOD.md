# GDT290 — latent opaque host renderer classes

## Question

GDT289 rejected a single cross-host position-transition table: it lost in all
eight Voynich host buckets and all four positions.  The remaining compact
alternative is a small number of opaque host classes, each with its own
position-conditioned wrapper ecology.  GDT290 asks whether four such classes
predict a forbidden host-position cell on unseen folios.

This is not substring clustering.  Exact `PAGE_HOST` values are opaque IDs;
their glyph identities, similarities, meanings, sounds, and proposed
morphology never enter the class representation.

## Frozen panels and exclusions

Use the same eight f84-free 8,448-event panels as GDT289 and the same immutable
eight host buckets.  Hold out one physical folio.  For a target host at target
position `T`:

- forbid every training occurrence of that host at `T`;
- describe it only by normalized wrapper distributions at other positions on
  other folios;
- learn clusters and their target-position wrapper distributions only from
  hosts outside the target host bucket and outside the held folio.

Rows without a cross-folio other-position profile are unscored.

## Frozen class learner

For each target position and target host bucket, encode every eligible training
host as the concatenation of its normalized wrapper distributions at the other
three positions plus one missing-position flag per position.  Fit Euclidean
K-means with `K=4`, deterministic SHA-minimum first center, farthest-first
remaining centers, lexicographic tie breaks, and at most 30 Lloyd iterations.
Require at least `3K` eligible training hosts; otherwise that fold-position is
capacity-unscored.

A capacity-only first invocation stopped before any result because the Latin
scholastic panel has zero K=4 scoreable rows under this rule.  It is retained
as `UNSCORED_NO_LATENT_CLASS_CAPACITY`; the other seven panels keep the frozen
model.  This mechanical exclusion was fixed after exposing only scoreable-row
counts and before any effect or decision was published.

The wrapper distribution for a cluster is the host-equal average of its
members' normalized target-position profiles with Dirichlet-1/2 smoothing.
Assign the target host by nearest center.  Give the class forecast the same
effective count as the target host's other-position evidence and shrink it by
the same fixed 11-event `POSITION_CONTEXT` prior as GDT289.

Compare against GDT289's `OTHER_POSITION_HOST_BAG`, which knows the same target
host evidence but ignores which other positions supplied it.  The primary
effect is bag bits minus class-model bits.  Report all buckets, positions,
folios, and held-section/held-hand sensitivities.  Repeat `K=2` and `K=8` on
Voynich only as declared capacity/scale sensitivities; they cannot replace the
K=4 primary.

## Null and calibration

After training-only probability vectors are fixed, permute held wrapper
outcomes within exact `physical folio × section × Currier × hand × register ×
target position × host length × first host character × last host character`
strata for 64 shared worlds.  Seed family:
`GDT290_HELD_WRAPPER_ALIGNMENT|panel|K|world|stratum`.

Report local p-values and standardized max-family p-values across the seven
K=4-capable panels whose null variance is positive.  A panel with exact zero null
variance remains descriptively scored but receives
`NA_ZERO_NULL_VARIANCE` and is excluded mechanically from maxT.

## Frozen decision

Call `COMPACT_LATENT_HOST_RENDERER_CLASSES_SUPPORTED` only if the Voynich K=4
model has:

- at least 1,000 scoreable events;
- positive gain over the other-position host bag;
- positive gain in at least six of eight host buckets and three of four target
  positions;
- variable-family maxT `p <= .05`; and
- positive held-section and held-hand gains.

Otherwise call `HOST_POSITION_RENDERING_REMAINS_LEXICALIZED_OR_HIGH_CAPACITY`.
If fewer than 1,000 rows are scoreable, call
`INSUFFICIENT_LATENT_HOST_CLASS_CAPACITY`.

## Claim ceiling and seal

At most this identifies compact opaque renderer classes.  It cannot establish
lexical classes, morphology, grammar functions, abbreviation, sound, language,
meaning, plaintext, or translation.  Only the published f84-free native event
inventory is read.  No f84 row may be opened, parsed, retained, joined, or
scored.
