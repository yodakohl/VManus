# GDT796 method

## Question

Does the f71 outer-ten source-family texture require a mirrored copying order,
and can the smaller graphical layer selected by GDT795 be interpreted as a
visible figure status or as a historically attested facies/decan status rather
than another opaque label class?

## Fixed scope and inputs

The manuscript panel is the same 101 GDT795 Kluge-A loci. No new page, image or
transcription is opened. The canonical source-family, alternate member-code,
prefix and residual fields come from the validated GDT795 atlas.

Existing GDT360 annotations are reacquired only through `./vmanus-exp
query-tsv`: selector `locus`, the 101 exact allowed loci and the columns frozen
in `src/GUARDED_QUERY_SPECS.tsv`. The useful varying channels are
`ZODIAC_BARREL`, `ZODIAC_CLOTHING` and `ZODIAC_FACING`; broad object-context
duplicates remain in the acquired count but receive no score. Page/sign names
come from the five explicitly allowed rows of
`public_zodiac_nymph_overview.tsv` through a second guarded query.

The two 12-sign by three-facies ruler tables are fixed in
`src/HISTORICAL_FACIES_MATRICES.tsv`. Their sources and evidential roles are
recorded in `src/HISTORICAL_SOURCE_REGISTRY.tsv`. Historical tables supply
candidate classes, never a Voynich lexeme by themselves.

## A. Outer-ten mirror reproduction

Only outer members A06 through A15 of f70v1, f71v and f72r1 are used. The
closed 10-to-5 cross-band route remains closed: no inner-five member is paired,
interpolated or added to this score.

With local coordinate `c=A-6`, transforms are
`Rr(c)=(c+r) mod 10` and `Fr(c)=(-c+r) mod 10`. f70 is fixed to R0 and all
400 `(f71,f72)` pairs are scored. The primary score is the sum of the three
pairwise character-level normalized Levenshtein similarities, including group
boundaries. Views are ZL3b/IT2a/RF1b member sequences, boundary family, compact
family, prefix and residual. Exact member-sequence identity is counted
separately.

The original inclusive-missing null uses 4,096 within-diagram permutations
with seed 79510 and re-optimizes all 400 transforms. An adjudicating sensitivity
keeps the two missing A14 masks fixed, permutes only observed labels with seed
796013 and sums three pairwise mean similarities rather than raw sums. Both
odd/even split directions select on one half and rank the frozen transform on
the other half.

## B. Visible status test

For each varying visual channel, representations are tested separately:
complete boundary family, compact family, transferred prefix and residual.
The basic unit is one unique channel×locus state. Exact-key leave-one-physical-
folio-out prediction uses only keys seen on another physical folio. Ties split
credit. A state-only held-folio majority is the baseline.

Permutation controls shuffle states only among mobile loci inside their source
selector and array, preserving state totals, missingness and the GDT795 local
prefix blocks. Candidate cards list every recurrent complete family observed
in at least two physical folios with its full state census and counterexamples.
A concrete visual status may remain C0 only if it is cross-folio consistent and
beats the state-only baseline; it never exports family components.

## C. Historical facies/status test

Primary signs are Pisces (f70v2), Taurus (f71v plus f72r1) and Gemini (f72r2).
Unpaired Aries-dark f70v1 is sensitivity-only. Taurus phase H0 fixes f71v to
positions 1–15 and f72r1 to 16–30; H1 reverses those halves and cannot be
chosen from the result.

For every matrix, phase and one of sixty global transforms:

`g=1+((offset + direction*(base_position-1)) mod 30)`

The resulting decan is 1–10, 11–20 or 21–30. Planet rulers are also collapsed
to the explicit analytical status `BENEFIC` (Jupiter/Venus), `MALEFIC`
(Mars/Saturn), or `OTHER` (Sun/Moon/Mercury).

The score is family-balanced status purity over recurrent complete families
that cross signs. Leave-one-family-out selects direction and offset without the
held family; leave-one-sign-out is reported where capacity exists. A
block-preserving within-array permutation redoes the full 60-transform search.
`AQABAC` is never allowed to choose its own phase. Its concrete rivals are
fortunate/benefic facies, adverse facies, semantically open marked quality, and
opaque learned class.

## Decision rule and claim ceiling

The f71 mirror may survive as a copying-order C0 rival if F9/R0 remains best
under the fixed-mask normalized control. It becomes a reusable ordering key
only if both split directions rank it in the leading decile across several
representations.

A visual or historical status becomes a bounded C0 family card only with
cross-folio/sign consistency beyond the corresponding held baseline and null.
A facies architecture requires one global transform to support at least three
independent held families. Otherwise the primary GDT795 architecture remains
learned individual designations plus a semantically open local graphical field.

GDT796 may add or reject concrete status rivals. It cannot confirm a word,
morpheme, number, planet, facies, day, degree, substance, action, disease,
treatment, language, cipher or plaintext translation, and it cannot reopen the
10-to-5 ring pairing route.
