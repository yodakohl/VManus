# GDT1324 — exact finite modular-key recovery, source-free

Decision note11October2026 before enumeration. Inclusive budget02:18–02:40UTC
covers predecessor review, specification, two small implementations, exact checks
and publication. No native attack, language corpus, optimization machinery or
post-result longer-message/control expansion. This is a bounded finite calculation.

Unknown: does the already-fixed GDT1322 toy channel retain key information when
its source law is independently fixed, and how much exact finite-message recovery
is possible?1322verified inverse/normalization and a two-key ranking reversal,
not recovery.1323stopped its native necessary test for capacity; it stays closed.
The empirical pooling identity already proves a freely cofit IID prior cannot
identify a key. Here bank/q and each source law are fixed for ALL candidate keys.
GDT602's oracle segmentation recovery and604's failed native Naibbe attack warn
that source-control success does not transfer to a target. No such transfer here.

Use only1322's existing modulus3 fixture: drawings a,b, bank in fixed order
[b,bb,bbb,a,aa], all q=1. Exhaust a,b in{0,1,2}, excluding precisely keys whose
bank misses any source residue. Expected valid set is the eight nonzero pairs;
check rather than assume it. At each source character draw a bank word independently
with replacement, uniformly within its decoded residue class. Complete ciphertext
packets and their boundaries are supplied, as is the bank and exact source law.
This is an oracle specification, but no unknown plaintext or key is supplied to
the scorer. All8possible true keys receive equal prior weight, not a selected key.

Case FIXED_MARKOV uses unchanged1322pi=(.6,.3,.1) and transition rows
(.1,.8,.1),(.3,.1,.6),(.6,.3,.1). Case UNIFORM_IID has each source residue1/3
independently, unchanged across all keys. These cases change both initial and
transition laws; differences cannot be attributed solely to memory. No actual
language or meaning is associated with residues0,1,2.

Enumerate EVERY ciphertext of lengths1,2,3,4,5,6 over the five-entry bank. For each
key use the correct normalized1322channel likelihood, not source score alone.
At a ciphertext choose all maximum-likelihood keys and split ties uniformly.
Record the exact conditional8x8confusion matrix, macro exact-key accuracy and macro
exact-WHOLE-source-sequence accuracy under the uniform true-key prior. Source
sequence accuracy checks the decoded residue tuple, not character-wise fraction.
Also record equivalence classes of keys with identical full output distributions
at EACH length. Distinguish distribution identifiability from finite-sample exact
recovery, and key recovery from plaintext recovery. No pvalues or success cutoff.

Primary uses an integer likelihood lattice denominator180per step (all initial,
transition and spelling probabilities in both cases have denominators dividing180),
Cartesian output enumeration and integer tie-accounting scale840. Validator uses
recursive enumeration, direct Fraction source probabilities and independent class
lookup. Check all distributions sum1, all confusion rows sum1, probability-table
hashes, exact metrics and exact law-equivalence classes. Preserve compact result,
per-length confusion matrices and per-key table digests; full tables are exactly
reconstructible from programs and fixture. Check arithmetic scale before use.

Analytic checks, known before enumeration: for invertible u modulo m, scaling every
key value by u relabels source residues. If the fixed source law is invariant under
that relabeling, all output probabilities are unchanged. If the source law is free
to be relabeled jointly, equality also holds for arbitrary non-IID laws. Thus fixing
an asymmetric independent prior is substantive, not a free inference result.
For this UNIFORM_IID bank the nonzero a,b keys have classes of sizes1,2,2and all
four share exactly the same output probabilities; the other four form two pairs.
Expect three distribution classes (sizes4,2,2), so exact-key Bayes accuracy is at
most3/8for ANY message length, not merely the1/2scaling-pair bound. This is a bank-
specific extra collision, not a universal modular-cipher ceiling. The asymmetric
fixed pi already distinguishes the eight single-packet distributions; do not
attribute all identifiability to Markov transitions. Verify both facts exactly.

Decision consequences: identical distributions are intrinsically indistinguishable
under this contract and must not be called a failed optimizer. Distinct distributions
retain only toy statistical distinguishability; exact finite-message error is paid.
Neither outcome opens native bank fitting or the27^22key search. The full22drawing,
27residue recovery problem, source-law mismatch, unknown bank, segmentation and
historical plausibility remain untested. No arbitrary Voynich meanings, no corpus,
no sealed/reserved data, no semantic relation packet. Stop after this finite result.
