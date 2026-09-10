# GDT901 — complete solmization register excluded under the fixed model

All ten preregistered grammatical-role partitions are impossible on the 259
admitted IT2a whole paragraphs. The other readings contain only 1, 11 and 14
paragraphs, below the 22 mandatory source records. No complete lexicon was found.

Two independently implemented solvers agree. The primary model includes exact
counts, headings, distinct word values and paragraph assignments, and every
possible shared nonempty-root/prefix/suffix factorization. All ten cases return
UNSAT before any order cut, in 1.57–5.08 seconds including construction. The
independent model omits both morphology and word order and still returns UNSAT
in all ten cases, in 20.03–101.98 seconds. Thus these extra constraints are not
needed for the exclusion. Neither engine reached its time limit.

The source is the complete operational projection of Hieronymus of Moravia's
chapter12: 22 pitches, 42 memberships, 52 directed mutations and eight zero
records, totaling 416 positions. Two independent readings and independent role
compilations agree. The ten partitions, including the original merged-word case,
were frozen before any target-domain result. All ten necessary individual word
domains survived; impossibility arises only when the assignments are required
to agree jointly across records.

This excludes the conjunction of this complete source, its fixed operational
projection, one word per realized form, paragraph-first headings, global
background and the admitted target scope. It does not exclude music generally,
shared morphological roots generally, or another independently motivated
representation. Source graph rigidity did not imply a manuscript embedding.
There are zero confirmed meanings and no held-data evaluation. No automatic
source, heading, alias, segmentation or solver repair follows.

The full solver was published in commit7303db94 before its first actual run.
Source and model seals remain unchanged. Synthetic exhaustive checks and an
independent code audit support the encoding; result bindings and all case
receipts replay. These are two independent solver conclusions, not an exported
formal UNSAT certificate. See `artifacts/FULL_RESULT.json` and the reproducible
commands in `README.md`.
