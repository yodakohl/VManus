# IL011 — Timm control for the cross-Currier directional relation

Status before validation: **REGISTERED_UNSCORED**.

## Question

Does IL010's confirmed Currier-excluded, orientation-specific D/C root relation
exceed what the fixed Timm local self-citation process produces when generated
manuscripts are poured into the identical ZL3b prose geometry?

This is a mechanism and system-class control, not a word-meaning experiment.
The archive compared Timm texts with broad context, sequence-typology, and
joint-profile statistics, but did not apply IL010's oriented-minus-unordered,
target-Currier-excluded invariant under the exact IL006 conditional null.

## Inputs and provenance

- Primary manuscript reading: manual ZL3b only.
- Fixed structural parser, D/C root maps, metadata, page split, smoothing, and
  source-exclusion logic inherited without retuning from IL006/IL009/IL010.
- Generated controls:
  `archive_pre_reset_2026-08-06/semantic_assumptions/cache/timm_generated_controls/`.
- Development controls: seeds `19, 23, 41, 73, 97`.
- Sealed final controls: all 64 seeds `101` through `164`, with no selection by
  result.
- No OCR, images, visual labels, recognition model, embedding, dictionary,
  gloss, or known-language alignment is used.

The final control files may be hashed and counted for provenance before final
scoring, but no directional score from seeds 101--164 may be computed before
all validation gates pass.

## Fixed relayout and representation

Each generated token stream is poured into the raw ZL3b prose word slots in
physical order. Page, line, paragraph, section, Currier, and hand fields remain
the ZL3b template values. Generated strings are then parsed by the same frozen
parser as ZL3b; they are not treated as already parsed roots.

For each corpus separately:

1. only SHA256 training pages are sources and only SHA256 bucket-0 pages are
   scored;
2. the source model for Currier A excludes every source page marked A, and the
   source model for Currier B excludes every source page marked B;
3. the oriented D/C table and the same table pooled over physical DC/CD
   orientation are fitted exactly as in IL010;
4. their edge-score difference is the directional increment;
5. page vocabulary, exact form shell, five-bin horizontal position, paragraph
   opening state, stratum, D/C side, and every physical D/C edge location remain
   fixed by the IL006 within-page null.

## Exact conditional-null expectation

IL006 estimated each page's null mean by random within-cell permutations.
IL011 computes that same expectation exactly. For each fixed physical D/C edge,
the oriented-minus-unordered score is averaged over the empirical D-root and
C-root frequencies in the two corresponding permutation cells. Linearity then
gives the exact expected page mean without Monte Carlo error.

An exhaustive two-D/two-C enumeration must equal the analytic expectation to
`1e-12`. On real ZL3b the exact-null score must retain the same 36 eligible
pages as IL010 and differ from IL010's published 2,048-permutation residual by
no more than `0.001` bit/edge.

## Training-only disclosure

Before registration, the exact method gave ZL3b `+0.0169191` bit/edge on 36/44
pages with 80.56% positive pages. This is `-0.0003275` from IL010's published
Monte Carlo value. Development Timm residuals for seeds 19/23/41/73/97 were
`-0.007493, -0.001747, +0.006541, +0.004047, +0.001643`; they used 24--30
eligible pages. These values calibrate feasibility only and do not set a
control quantile or permit a final conclusion.

The development coverage showed that generated corpora have fewer mobile D/C
pages than ZL3b. An eligible control is therefore frozen as at least 20 scored
pages and at least 50% of pages with ten or more D/C edges passing IL006's
unchanged six-movable-D and six-movable-C gate. This threshold was fixed from
development coverage, not from held control scores.

## Validation gates

All must pass before seeds 101--164 are scored:

1. exhaustive exact-null self-test passes;
2. repeated development and real runs are byte-for-byte deterministic;
3. real integrity and target-Currier exclusion pass;
4. real exact-null/published-IL010 parity passes the `0.001` tolerance with the
   same eligible page count;
5. all five development controls have at least 20 scored pages, at least 50%
   coverage, intact margins, and target-Currier exclusion;
6. exactly 64 held seed files, 101--164, are present and hash-bound;
7. the runner, preregistration, dependencies, metadata, ZL3b source, IL010
   result, and complete 69-control manifest are hash-bound.

Validation failure stops the experiment without any held-control score.

## Final eligibility and decision

All 64 held controls are run once. Controls failing the frozen 20-page/50%
coverage/integrity/source-exclusion rule are excluded without reference to
their score; at least 60 controls must remain or the experiment stops without a
system-class conclusion.

Let `R` be ZL3b's frozen exact mean directional residual and `P` its positive-
page fraction. A held control is a conservative exceedance if its residual is
at least `R` **or** its positive-page fraction is at least `P`. With `N`
eligible controls,

`p = (1 + number of conservative exceedances) / (N + 1)`.

- If `p <= 0.05`, report
  `IL010_EXCEEDS_TIMM_DIRECTION_CONTROL`.
- Otherwise report
  `IL010_COMPATIBLE_WITH_TIMM_DIRECTION_CONTROL`.

Residual-only and positive-page-only tails are descriptive; the union tail is
the sole decision statistic. No alternative seed subset, axis, root subset,
threshold, parser, relayout, or score may replace it.

## Licensed interpretation

An excess rejects this fixed Timm local self-citation process as sufficient for
the IL010 relation. Compatibility means IL010 alone cannot distinguish that
process. Neither outcome proves or disproves ordinary language, meaningful
notation, mnemonics, synthetic generation generally, authorship, spoken
reading direction, POS, sound, root meaning, or plaintext.
