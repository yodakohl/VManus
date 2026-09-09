# GDT884 — fixed Laufenberg introduction excluded under the declared code

**UNSAT_ANALYTIC for all 24 fixed equations.** No fixed string image for each
exact STA symbol, even allowing empty images and homophony, turns the complete
five-line North block into any of the eight frozen introduction strings while
keeping each recorded source group nonempty. This excludes this specific text
and encoding contract. It does not identify a language or reject the broader
historical image-program comparison. Confirmed meanings: zero.

Each of the three primary readings contains 19 groups, 72 STA units and 20
types, with no marked STA alternatives. They are alternate readings of one
manuscript. Raw separator uncertainty remains in INPUT.json. The historical
strings contain 313–315 normalized letters. The Winter continuation was not
queried; no new Voynich image or sealed data was accessed.

The preregistered decoder hit 1,000,000 nodes with no solution in every case:
its original RESULT.json remains **UNKNOWN_BUDGET**, not an exhaustive search.
VALIDATION.json independently reconstructed the admitted input. Frozen solver,
source variants and method bytes remain unchanged. The following proof was
developed **after that search**, on precisely the same equations, without a
budget increase, new plaintext variant or decoder repair.

## Short proof

Groups 2 and 3 are both `or`, exactly STA `[A1,C1]`. Write their nonempty image
as W=h(A1)h(C1). The plaintext must contain WW after a nonempty first group,
with room for the remaining 16 nonempty groups. Enumerating every such square
and every split of W, including empty symbol images, gives 408 cases across
the 24 equations.

Every subsequent occurrence of A1 or C1 must emit its same assigned substring
disjointly in the remaining plaintext. Exact maximum disjoint-occurrence counts
exclude 368 cases. The remaining 40 assign h(A1)=empty and h(C1)=`n`, or, for
some IT2a/RF1b cases, `t`. These are necessary trial assignments, not translations.

Every target contains exactly one `x`, followed by exactly `ion`. That `x` must
come from a source code occurring only once: a repeated code would repeat its
entire image, including `x`. Each reading has nine such source positions. After
every possible position at least two C1 occurrences remain, or four for ZL3b.
They must emit their images wholly after the unique `x`. But `ion` contains
only one `n` and no `t`. All 360 possible singleton allocations therefore fail.
There is no remaining assignment.

The producer computes disjoint counts by earliest-finish greedy matching.
The independent checker uses interval dynamic programming, reconstructs all
square/split cases and singleton allocations, and checks every rejection witness.
ANALYTIC_VALIDATION.json records PASS and exact input/certificate hashes.

## Sources and reproduction

Historical passage: [HAB scan 00161](https://diglib.hab.de/inkunabeln/167-9-poet/00161.jpg),
14 introductory verses after the chapter-IV heading; photographic hash,
transcription variants and selection precede the Voynich query in SOURCE_INTRO.json.
[KdiH Karlsruhe](https://kdih.badw.de/datenbank/handschrift/87/3/4) records rhyme
pairs as long physical lines; this corrects the sufficiency of an inherited
odd-line objection, but establishes no Voynich verse segmentation or copied text.

Run `python3 experiments/yolo/gdt884_laufenberg_fixed_passage_equation/src/analytic_certificate.py`
then `python3 experiments/yolo/gdt884_laufenberg_fixed_passage_equation/src/validate_analytic.py`.
The original source reader/search and independent reconstruction remain in
`src/run.py` and `src/validate.py`. No expanded search or Winter comparison follows.
