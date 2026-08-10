# `cho/che` canonical-transfer synthetic preflight

## Question and isolation

This target-blind preflight asks whether a held-physical-leaf scorer can
distinguish a useful latent-form collapse from the automatic vocabulary
compression caused by merging types.  It may read only the frozen 2,223-row
realization/template-masked capacity panel and its capacity artifacts.  It
must not read source surfaces, the `o/e` realization, a raw type, a canonical
template, or a manuscript score.

ZL3b, IT2a, and RF1b are alternate readings.  They are scored separately and
the weakest reading is primary.  The physical folio is the held unit.  The
eight registered leaves are `f39,f55,f68,f73,f87,f89,f90,f96`; each supplies
two opposite-state page sides.  All 256 within-leaf side/state assignments are
the exact state orbit.

## Future target representation

A target event is a clean one-fragment group with exactly one ASCII
`(ch|sh)(o|e)` site.  `raw_type` is the complete cleaned source group.
`canonical_type` is obtained by replacing only the `o/e` character at that
site by `X`.  A collision pair exists only when both the `o` and `e` raw types
for the same canonical type occur in the frozen target universe.  Singleton
canonical types cannot create transfer gain and remain identity-mapped.

Each raw type must have one consistent length, site prefix, site index,
realization, and canonical type.  Each canonical collision must contain
exactly one `o` and one `e` type.  Any violation stops before scoring.

## Held-leaf transfer gain

For an evaluation event on held folio `f`, use only other physical folios in
the same reading.  A training event is eligible only when its assigned state
is opposite to the evaluation event's assigned state.  For a requested scope
or prefix block, both evaluation and training events must be in that block.

For event raw type `t` with proposed mate `m`, the added-transfer indicator is
one exactly when `t` is absent from the eligible training types and `m` is
present; otherwise it is zero.  Average indicators within each nonempty
reading/held-folio context, then average contexts equally.  The resulting
gain is therefore the fraction of held cases newly supported across the state
boundary by the proposed merge; ordinary raw matches receive no credit.

The candidate score pairs the actual `o/e` counterparts.  The primary raw
score is the arithmetic mean of the three equal-folio reading gains.  The registered
material effect is **state excess**: the observed raw score minus its mean over
all 256 within-leaf state assignments.  Reading, folio, scope, prefix, and
deletion robustness effects are centered by their corresponding complete
state-orbit means in the same way.  The exact state p value is the inclusive
upper-tail rank of the observed primary raw score in that orbit.  Because the
global complement is identical, its attainable minimum is
`2/256 = .0078125`.

## Complexity-matched merger null

Candidate collision pairs are partitioned by exact ASCII length, `ch/sh`
prefix, exact site index, and the base-2 log-frequency bin of each member.
Within each shell, `o` members stay fixed and `e` members are deterministically
reranked by SHA-256 under domain
`CCT001|MERGE|<draw>|<shell>|<e-type>`.  This preserves the member set, pair
count, length, prefix, site position, and both member-frequency bins while
destroying surrounding-string correspondence.  Shells of size one are fixed.

Exactly 8,192 deterministic Monte Carlo draws are scored under the observed
state assignment.  Duplicates are retained.  The merger p value is
`(1 + count(null >= candidate)) / 8193`.  This is a frozen deterministic
Monte Carlo rank, not an exact permutation p value.  Candidate advantage is
candidate primary gain minus the null mean.  The real target must have at
least 24 collision pairs, at least 16 pairs in shells of size at least two,
and collision-pair events on all eight leaves and all three readings; otherwise
it stops unscored.

## Registered gates

The general latent-collapse claim requires all of the following:

1. candidate primary state excess at least `.05`;
2. candidate-minus-null-mean advantage at least `.03`;
3. state-orbit p at most `.01`;
4. merger-null p at most `.01`;
5. every reading state excess at least `.02`, at least six positive aggregate
   leaf-state excesses, and at least four positive leaf-state excesses in every
   reading;
6. every leave-one-folio-out primary state excess at least `.03` and no folio supplies
   more than `.30` of the summed positive folio gain;
7. confirmed-prose aggregate-reading state excess at least `.03`, positive in
   every reading, and at least five of its six available physical folios
   positive after aggregating the alternate readings;
8. diagnostic-nonprose aggregate-reading state excess at least `.03`, positive
   in every reading, and at least two of its three available physical folios
   positive after aggregating the alternate readings;
9. both `ch` and `sh` prefix-block aggregate-reading state excesses at least
   `.02` and positive in every reading;
10. all access, schema, orbit, complement-invariance, and malformed-input
    controls pass.

The scope and prefix gates deliberately prevent a one-domain or one-prefix
improvement from being called a manuscript-wide collapse.  Such a target may
be reported only as a frozen domain-limited nonconfirmation of this general
claim; it does not authorize post-hoc retuning.

## Synthetic calibration

Use the exact masked 2,223-event geometry.  Generate raw/canonical identities
without opening manuscript types.  Run 64 null worlds and eight worlds each
for: distributed state-aligned collapse, side-only, one-folio, one-reading,
prose-only, diagnostic-only, one-prefix, one-side, generic state-independent
collapse, and unique-surrounding no-collision controls.  Also run distributed
partial-alignment strengths `.25,.50,.75,1.00` in eight worlds each.

Acceptance requires:

- no more than 1 of 64 null worlds passes;
- all 8 full distributed worlds pass;
- at least 6 of 8 worlds pass at the weakest registered partial strength whose
  realized primary state excess is at least `.05`;
- zero of 8 worlds passes for every named negative control;
- state complement leaves the complete score/gates unchanged;
- malformed duplicate IDs, inconsistent type metadata, broken canonical
  pairs, missing readings/leaves/sides, and target-valued columns in the
  masked panel all stop;
- an independent implementation reconstructs every world and decision.

Thresholds and controls may be corrected only while target types remain
unopened.  Every failed calibration attempt is preserved and logged.

## Claim ceiling

A calibrated target pass can show only that replacing the defining `o/e`
site supplies transferable, distributed, complexity-matched formal support
across the registered page-side state, making this particular canonical form
useful for later structural modeling.  It does not prove authorial word
boundaries, pronunciation, phonology, language, cipher, plaintext, lexical
meaning, or translation.
