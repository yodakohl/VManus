# GDT903 — unrestricted reversible line actions remain compatible

The registered class is **compatible, without an identified writing rule**.
Two independent constructions give the same ordinary difference subgroup core:
10,451 vertices, 10,862 positive edges, rank 412, infinite index in the free
group on the 20 literal characters. Thus the subgroup is proper. A published
completion supplies 20 explicit permutations on 10,451 reachable states; every
one of the 413 complete source lines sends state 0 to the same state 453.
This is an existence witness, not a minimum-size machine or a decoding key.

The question concerns all finite and infinite fixed reversible character
actions at once. For left-to-right word actions the ordinary subgroup is
H = <w_i w_ref^-1>, with reference f19r.8. Equality H = F would force the start
to have a trivial orbit. It does not hold. Normal closure or requiring the
endpoint to equal the start would answer different questions. The mathematical
method is standard graph folding, as specified and referenced in METHOD.md.

The primary construction starts with 13,538 vertices and 13,949 positive edges;
3,087 forced unions produce the final graph. No core pruning is needed. It
finishes in 0.118 seconds. The independent reduced-difference bouquet uses
412 nonempty generators and a separate full-edge-pass folding algorithm,
finishing in 1.205 seconds. Its canonical rooted inverse-labeled core agrees
exactly. Both computations stayed below their preregistered 600-second limits.

A separately implemented certificate validator reconstructs every original
line path, verifies every forced union, preserves all original edges, checks
the final core and all 20 bijections, and replays all 413 endpoints and state
reachability. The source is the unchanged GDT882 packet: 413 concordant literal
lines, 80 page/panel selectors, 43 odd physical leaves. No held body or new image
was accessed. The first certificate call stopped before reading the result
because its metadata check confused selectors with physical leaves. The sole
correction counts these separately; VALIDATOR_CORRECTION.json preserves the
original code hash, failure and unchanged proof checks. The subsequent proof
replay and complete aggregate validation pass.

Preregistration and executable methods were published in commit 1871cc11 before
either actual fold. FOLD_LOG.json.gz contains the local proof;
FOLD_RESULT.json includes the complete finite witness; INDEPENDENT_SUBGROUP.json
contains the second core. Reproduction commands are in README.md.

Decision: close this unrestricted compatibility question. Its surviving class
does not identify historical atomic signs, a writing rule, a language or any
meaning. No minimum-state search, overgroup search, alternative completion or
held-word query follows automatically. A historical decoding model would need
independently motivated additional constraints.
