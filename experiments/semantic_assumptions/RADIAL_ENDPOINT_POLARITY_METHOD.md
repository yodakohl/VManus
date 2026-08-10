# RPE001 — radial physical-endpoint polarity

Status: **REGISTERED_UNSCORED**

## Question and novelty

The official IVTFF convention defines `Ri` as radial text running from outside
to inside and `Ro` as text running from inside to outside. Does one anonymous
STA family preferentially touch the **physical center** or **physical outer
edge** of radial text even when textual first/last order reverses?

This is not a word guess and not a repeat of the circle-marker, zodiac-cycle,
or cross-role tests. A family tied only to textual start or textual end must
have opposite physical effects in `Ri` and `Ro`; it therefore fails the
direction-coherence gate. The public convention is documented at
<https://www.voynich.nu/extra/sp_transcr.html>.

The method was frozen before endpoint family identities were aggregated. Raw
radial transcription examples had already been incidentally visible during
source diagnostics, so this is preregistered but not claimed to be examiner-
blind. No endpoint-frequency table or statistic was inspected before freeze.

## Frozen panel and inputs

Use the 60 loci in `results/radial_endpoint_polarity_capacity.json`. A locus is
eligible exactly when it is `Ri` or `Ro`, has at least two source groups, all
groups are present in consecutive order, and every group has
`strict_zero_alternative=1` in the independently validated all-reading STA
consensus scaffold.

For each eligible locus:

- `Ri`: physical center = last family of the last group; physical outer edge =
  first family of the first group.
- `Ro`: physical center = first family of the first group; physical outer edge =
  last family of the last group.

The global tested alphabet is the sorted set of STA families occurring in the
validated consensus corpus, determined without restricting to radial loci. It
must be exactly `ABCDEFGHJKLMNPQTUVWXZ` (21 families). ZL3b, IT2a, and RF1b are
alternate readings already collapsed only where their family sequence agrees;
they are not three samples.

## Frozen statistic and exact null

For family `F` and locus `l`, define

`x_l(F) = 1(center_l = F) - 1(outer_l = F)`.

Average loci within each physical folio, then average the five folio means.
Call this `E(F)`. Select one family by maximum `E(F)`, breaking exact ties by
alphabetic order. The primary statistic is `M = max_F E(F)`.

This is a center-enrichment statistic, not an arbitrarily one-sided lexical
hypothesis. Every locus contributes one `+1` center family and one `-1` outer
family, so the 21 effects sum to zero. Any difference between the center and
outer family distributions therefore creates at least one positive center
effect. A two-sided `max(abs(E))` was rejected during target-blind calibration:
with five folio signs its global complement forces a minimum p of 2/32=.0625,
making the registered .05 gate impossible.

The exact null contains all 32 synchronous physical-folio swaps. For each of
the five folios independently, either retain every center/outer assignment or
swap every assignment. This sign-flips that folio's complete 21-family effect
vector, preserves loci and directions, and prevents prolific folios from
becoming independent votes. The family-wise p-value is

`p = count(null M >= observed M - 1e-15) / 32`.

This is an exact randomization test only for exchangeability of physical
center and outer endpoints within folio under the registered null; it is not a
general language null.

## Frozen controls

Before target access, eight deterministic worlds each must:

- pass a feasible distributed physical-center plant;
- reject a feasible exact-null plant;
- reject a one-folio plant;
- reject a textual-start-only plant (opposite effects in `Ri` and `Ro`);
- reject a textual-end-only plant;
- reject a one-direction-only plant;
- preserve family relabeling and row-order serialization, and prove that a
  simultaneous center/outer complement negates every family and folio effect;
  and
- reject duplicate, missing, wrong-direction, wrong-folio, and unknown-family
  mutations.

The synthetic endpoint pairs must use only the 60 frozen loci and the 21-family
alphabet. No manuscript endpoint family may be read by the control runner.

## Frozen manuscript gates

The aggregate target confirms only if all conditions hold:

1. `M >= .10` and exact max-family p <= .05;
2. the selected center effect is strictly positive in both the `Ri` and `Ro`
   subsets;
3. the center effect is supported by at least 3 of 4 informative `Ri` folios and at
   least 3 of 4 informative `Ro` folios;
4. every leave-one-folio-out selected-family effect is at least `.05`;
5. no folio contributes more than `.50` of the total absolute selected-family
   folio effect;
6. all capacity, source, hash, control, finiteness, uniqueness, target-isolation,
   and independent-reconstruction gates pass.

No family, threshold, subset, page, folio, or representation may be
changed after endpoint families are opened. Complete per-family diagnostics
are retained for reconstruction, but only the registered maximum is
inferential; individual runners-up are not discoveries.

## Claim ceiling

On pass: one anonymous STA family preferentially touches the physical center or
outer endpoint of strict multi-group radial loci across both inward and
outward writing. That supports a physical endpoint construction and may guide
a separately preregistered structural follow-up.

On failure: this exact STA-family endpoint representation does not establish a
transferable physical endpoint construction.

Neither outcome identifies a word, direction term, center/edge meaning,
grammar role, sound, language, cipher, plaintext, or translation.
