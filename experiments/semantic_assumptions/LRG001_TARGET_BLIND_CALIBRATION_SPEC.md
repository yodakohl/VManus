# LRG001 target-blind calibration specification

Status: `REGISTERED_TARGET_BLIND_SYNTHETIC_ONLY`

The real STA-family surfaces remain forbidden in this pass.  Calibration uses
only the published 109-cell capacity geometry and synthetic 24-family
sequences.

## Primary target geometry

The primary is restricted to the two independently multi-folio sections `B`
and `P`: 288 label rows and 2,479 prose rows on 13 physical folios.  `H` and
`T` are future diagnostic sensitivities and cannot make a target pass.

Odd-numbered physical folios train a fixed profile which is scored on even
folios; even folios then train the same profile and are scored on odd folios.
Every held comparison remains inside exact `(page, symbol_count)` cells.

## Fixed feature map and profile

For each synthetic or future manuscript family sequence over the fixed 24
families `A`--`X`, create:

- 24 normalized family counts;
- 24 one-hot first-family indicators;
- 24 one-hot last-family indicators; and
- 576 normalized directed adjacent-family counts.

This is a 648-column representation.  For each training cell, subtract the
mean prose vector from the mean label vector.  Average cells equally within
each physical folio and folios equally, then L2-normalize the resulting
profile.  No feature selection, exact-form feature, EVA spelling, member code,
or hyperparameter search is permitted.

Held row scores are dot products with the opposite-parity profile.  A held
cell effect is mean label score minus mean prose score; cells are averaged
equally within folio and folios equally.  Fixed-count Monte Carlo assignments
shuffle labels only inside held exact page-by-length cells.  There are 8,192
assignments per direction, generated from the frozen seed and reused for every
world and the future target.

## Target decision gates

Both parity directions must independently satisfy:

- plus-one upper-tail `p <= .01`;
- equal-folio effect `>= .05`;
- at least 5/7 positive even-held folios or 4/6 positive odd-held folios;
- held effects of at least `.05` in both `B` and `P`;
- every one-held-folio deletion remains positive; and
- maximum absolute folio contribution fraction `<= .35`.

The cosine between the two independently learned profiles must be at least
`.10`.  All numbers, assignments, finite checks, counts, and decisions must be
reconstructed independently before a manuscript target can be frozen.

## Synthetic worlds

Run 64 null worlds and eight worlds in each named family:

- `DISTRIBUTED_FULL`: shared start, end, and internal transition profile;
- `DISTRIBUTED_HALF`: the same profile at half row penetration;
- `DISTRIBUTED_START_ONLY`: a genuine shared initial-only profile;
- `ONE_FOLIO`: signal confined to one physical folio;
- `ONE_SECTION`: signal confined to section B;
- `PAGE_ONLY`: state-independent page signatures;
- `FOLIO_RANDOM`: a different label signature on every folio;
- `PARITY_MISMATCH`: nonmatching odd/even label profiles; and
- `EXACT_IDENTITY_ONLY`: nontransferable row-specific label sequences.

Acceptance requires zero null passes, 8/8 `DISTRIBUTED_FULL`, at least 6/8
`DISTRIBUTED_HALF`, 8/8 `DISTRIBUTED_START_ONLY`, and zero passes in every
adversarial family.

### v2 correction before target access

The first synthetic run was correctly stopped. `EXACT_IDENTITY_ONLY` drew
label rows uniformly while ordinary rows used the frozen decreasing family
distribution, accidentally planting a shared frequency signal; v2 draws its
row-specific sequences from that same base distribution. The sign-only
section guard also accepted 2/8 `ONE_SECTION` worlds on random positive P
effects; v2 applies the already declared `.05` material scale separately to
both sections. All other features, statistics, worlds, thresholds, seeds, and
acceptance counts are unchanged. The v1 artifacts remain preserved.

## Claim ceiling

Calibration can authorize one separately hash-frozen target only.  It supplies
no manuscript label profile, identifier, name, noun, object ownership, part of
speech, language, meaning, plaintext, or translation.
