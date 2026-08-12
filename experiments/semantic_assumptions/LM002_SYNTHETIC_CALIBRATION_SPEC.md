# LM002 target-free synthetic calibration specification

Status: **FROZEN BEFORE SYNTHETIC EXECUTION; FORMAL TARGET SEALED**.

This calibration implements the already published LM002 method on
`lm002_leaf_margin_cho_che_capacity_panel.tsv`. It may read the visual labels
and nuisance geometry in that target-blind panel. It must not open, parse, or
hash anew `parisel_cho_che_folio_states.tsv`; its already published whole-file
hash is only an inert binding inherited from the capacity result.

## Exact suite

World order is: 64 `NULL`, 8 `DISTRIBUTED_FULL`, 8 `DISTRIBUTED_REDUCED`, then
8 worlds each for `ONE_CELL`, `ONE_CURRIER`, `ONE_PHASE`, `PAGE_SIDE_ONLY`,
`QUIRE_ONLY`, `TEXT_VOLUME_ONLY`, `READING_DISAGREEMENT`, and
`ONE_PHASE_REVERSED`: 144 worlds total. World IDs are
`<FAMILY>_<zero-based-index-padded-to-three-digits>`.

Every world supplies three binary EM outcome vectors, three binary literal-
threshold robustness vectors, and one nonnegative integer text-volume vector.
Threshold equals EM in every non-null world. Null bits are the low bit of the
first eight bytes of SHA-256
`LM002|<world-id>|<channel>|<reading>|<opaque-id>`, interpreted big-endian.
Null EM and threshold channels use distinct keys. Unless a family definition
says otherwise, volume is identically zero.

`DISTRIBUTED_FULL` sets every reading and both state channels to the visual
`TOOTHED=1`, `SMOOTH=0` vector. The eight worlds differ only by ID.

For `DISTRIBUTED_REDUCED`, form all 15 pairs of one of the five toothed rows in
a mobile `PHASE_QUARTILE_SIDE` cell and one reading in `ZL3b,IT2a,RF1b` order.
Order pairs by SHA-256 of `LM002_REDUCED|<opaque-id>|<reading>` and select the
first eight. Begin from the full plant and flip exactly that row in exactly
that reading for both EM and threshold. This is a one-error, one-reading
reduced distributed signal; errors on fixed/noninferential rows are forbidden.

Adversaries are deterministic:

- `ONE_CELL`: use the visual vector only inside mobile primary cell `i mod 5`
  in sorted cell order, and zero elsewhere.
- `ONE_CURRIER`: use the visual vector in Currier `A` for even `i`, `B` for odd
  `i`, and its complement in the other Currier.
- `ONE_PHASE`: use the visual vector only in acquisition phase `i mod 3` in
  sorted `LM001X,LM001Y,LM001_HELD` order, and zero elsewhere.
- `PAGE_SIDE_ONLY`: output one on recto and zero on verso.
- `QUIRE_ONLY`: output the SHA low bit keyed by
  `LM002_QUIRE|<world-id>|<quire>`.
- `TEXT_VOLUME_ONLY`: state channels equal the full plant and volume equals
  the visual vector, forcing the registered volume-confound stop.
- `READING_DISAGREEMENT`: reading `i mod 3` uses the visual vector, the next
  reading its complement, and the third the visual vector.
- `ONE_PHASE_REVERSED`: begin from the full plant and complement every row in
  acquisition phase `i mod 3`.

## Exact scorer and gates

Enumerate every assignment in both frozen conditional orbits. Cell ordering is
UTF-8 lexical; within-cell row ordering is opaque-ID lexical; combinations are
lexicographic in those row indices; the Cartesian product has the first cell
vary slowest. Binary outcomes and integer volume use the identical scorer.

For one channel, compute the method's equal-cell reading effects, symmetric
common-direction statistic, inclusive tail, per-reading aligned cell-sign
counts, and per-reading maximum absolute cell-contribution ratios. Direction
is `+1` only when every reading effect is positive, `-1` only when every effect
is negative, otherwise zero. Currier contrasts use all mobile rows in the
primary view, pooled within Currier. Acquisition-phase × Currier contrasts use
all 42 admitted rows. Both are ordinary within-block toothed-minus-smooth
means, oriented by the common direction.

A world full-passes exactly when the nine target gates in the LM002 method all
pass, applied to synthetic EM, threshold, and volume. Numeric comparisons are
literal binary64 comparisons with no tolerance except inclusive-tail equality,
which compares exact rational integer numerators after multiplying every cell
mean by the least common denominator of its two state counts. The implementation
may use `fractions.Fraction`; stored decimal effects are diagnostics only.

Calibration passes only with 0/64 null full passes, 8/8 full plants, 8/8
reduced plants, and 0/8 full passes in each adversary family. It must also show
row-order and reading-order equality, global state-complement equality,
complete orbit cardinalities 108/324 with the observed assignment present
once, and equality to a separately written scalar reconstruction.

Any failed calibration gate yields `STOP_SYNTHETIC_INSTRUMENT_FAILED` and
forbids formal-target access. No plant strength, tail, effect, nuisance view,
or adversary may be changed after seeing calibration.

## Output and ceiling

The public result stores only family pass counts, per-world gate booleans and
aggregate rational/decimal diagnostics. It stores no favorable page, cell, or
synthetic vector. No formal target row or outcome may enter any output.

Calibration can authorize at most one separately frozen target join. It cannot
establish an association, leaf word, plant identity, sound, language, cipher,
plaintext, meaning, or translation.
