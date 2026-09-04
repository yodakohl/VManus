# GDT807 method

## Question

After all lines containing any target whole are removed, does the rest of a
strict complete paragraph retain enough nonlocal information to distinguish
fixed complete-whole pairs on unseen physical folios?

## Corpus and strict paragraph reconstruction

The 179-selector inherited allow-list is used without opening a new page.
`voynich_zl3b_lines.tsv`, `voynich_cross_transcription_lines.tsv`, and
`voynich_zl3b_tokens.tsv` are read only through guarded `vmanus-exp query-tsv`
calls with explicit selector allow-values and output columns.  `f84` and `f84r`
remain forbidden.

Lines are ordered by page and numeric line number.  A paragraph opens only on
`paragraph_start=1` and closes only on `paragraph_end=1`; lines outside such a
pair remain `OUTSIDE_PARAGRAPH`.  The expected source census is 665 complete
paragraphs, 3,807 included lines, 31,938 included tokens, and 330 outside lines
with 401 tokens.  A nearest-previous-paragraph fill is forbidden.

The primary memberships come from the discovery-subtracted GDT805 occurrence
atlas.  A paragraph contributes at most one observation per target surface,
regardless of target frequency.  Raw and GDT805 rank-stable memberships are
scored separately; the stricter unique-forced-LCS reconstruction is an audit,
not a replacement membership invented after seeing scores.

## Common mask and representations

For every paragraph, remove every complete physical line containing any of
the seven registered target surfaces: `cheol`, `otal`, `okal`, `ol`, `qokeol`,
`qokol`, or `qotal`.  This creates one identical remainder for every target
membership in a multi-target paragraph.  Then exclude from features all eleven
GDT805 target wholes and all exact GDT800 paired-terminal partner surfaces.
The primary feature vector is a bag of exact remaining whole surfaces.  It
contains no substring, edit-neighbour, renderer, role, German, illustration,
page identity, section, language, hand, or target-position feature.

Eligible remainders have at least twelve retained tokens and two nonempty
retained lines.  `RAW_PAIRED` and `STABLE_PAIRED` use the exact quarantine.
`RAW_ED1_SENSITIVITY` and `STABLE_ED1_SENSITIVITY` additionally remove every
surface at Levenshtein distance at most one from any registered target; these
are destructive sensitivities rather than promotion channels.

## Held-folio model

Each registered pair is scored as a balanced binary problem on exclusive
paragraph memberships; paragraphs containing both members are excluded.
Physical folio is normalized as `^(f\d+[rv])`, so all selectors from the same
folio remain in one fold.  In each leave-one-folio-out fold, the vocabulary is
rebuilt from training data and retains an exact surface only when it has at
least two training tokens in at least two training paragraphs.  A multinomial
naive-Bayes model uses additive alpha `1/2` and equal class priors.  The primary
decision value is the mean positive-minus-negative log likelihood over the
retained tokens.  AUC counts ties as one half; balanced accuracy thresholds the
decision at zero.  A paragraph, never an occurrence, is one vote.

## Exchange null and K24 pseudo-pairs

For each primary pair and view, whole target-membership sets are cyclically
rotated by offsets 1 through 12 inside deterministic
`section × language × hand × post-mask-length-bin` strata.  The length bin is
`floor(log2(retained_token_count))`.  Within a stratum of size `n`, offset `k`
means rotation by `k mod n`; singleton and divisor-aligned strata therefore
remain unchanged, no replacement permutation is invented, and tied nulls
count against the target.  The remainders do not move.  This preserves target
prevalence, multi-target correlation, register, and approximate length while
breaking the proposed target-to-remainder link wherever the stratum permits.

The full `PRIMARY_K12` lists in GDT804's
`GDT804_NEAREST_CONTROL_POOLS.tsv` supply 24 deterministic pseudo-pairs per
target pair.  (GDT806's exported subset lacks the required `qotal` list.)  For
direct pair `A/B`, the first twelve compare `A_r/B_r`; the next twelve compare
`A_r/B_(r+1 mod 12)`.  If the two selected control surfaces are identical, the
negative rank advances cyclically until the first distinct surface.  Every
pseudo-pair uses the same strict paragraph builder, model, and folio folds.
Its line mask is the common seven-target set plus both pseudo-pair control
surfaces; its feature quarantine likewise adds both control wholes.  Thus the
classifier cannot see the surfaces that define its pseudo-label.  Ties count
against the target when ranks are reported.

## Secondary overlays

The eleven exact GDT757 high-line-initial wholes and four low-purity controls
are counted only by complete surface and position.  Their historical or German
labels receive zero selection credit.  GDT764 fields, same-page controls,
illustration relations, geometry, and fixed concrete rival cards are display
overlays only.  No secondary overlay can change the primary result.

## Decision rule and claim ceiling

A pair is `ROBUST_NONLOCAL_PARAGRAPH_ECOLOGY_SPLIT` only when:

- each stable side has at least 24 eligible paragraphs and 16 folios;
- raw and stable paired AUC are at least 0.60;
- stable ED1 AUC and stable balanced accuracy are at least 0.60;
- stable AUC exceeds the median cyclic null by at least 0.03 and ranks no worse
  than 3 of 13, with ties against it;
- at least 18 of 24 K24 pseudo-pairs are scoreable and the target ranks no worse
  than 6, with ties against it; and
- AUC remains above 0.50 after removal of each single eligible folio in at
  least 80 percent of the reported removal diagnostics.

If raw/stable AUC and stable balanced accuracy pass but a robustness gate does
not, the pair is `PROVISIONAL_PARAGRAPH_ECOLOGY_SPLIT`.  Otherwise it is
`NO_PARAGRAPH_ECOLOGY_SPLIT`.

An exact whole may be named only as a `PARAGRAPH_ECOLOGY_LANDMARK` when it
occurs in at least five eligible paragraphs on four folios and its training
log-odds direction is unchanged in at least 80 percent of scoreable folds.
That label is structural.  GDT807 selects no meaning, lexeme, plaintext,
renderer patch, component, ingredient, process, quality, plant, disease,
patient, measure, or language.
