# GDT1324 — exact toy recovery depends on a genuinely fixed source law

**TOY_DISTINGUISHABILITY_WITH_PRIOR_DEPENDENT_RECOVERY_LIMITS.** In the unchanged GDT1322 modulus-3 teaching bank, all eight keys have different output distributions under its fixed asymmetric source law. At six ciphertext groups, exact maximum-likelihood key accuracy averages72.718734% over all equally likely true keys and all possible outputs. This is an oracle-channel toy result, not a native recovery control at Voynich scale.

With a different, fixed uniform IID source law, the same eight keys generate only three distinguishable output distributions. Exact-key accuracy can never exceed37.5%, however much text is supplied. This bank-specific information limit is not an optimizer failure or a universal modular-cipher bound.

| Output groups | Fixed1322source: exact key | Fixed1322source: exact whole source tuple | Uniform IID: exact key | Uniform IID: exact whole source tuple |
|---|---:|---:|---:|---:|
|1|22.5000%|70.0000%|20.8333%|55.5556%|
|2|41.5000%|73.0833%|21.7593%|41.3580%|
|3|50.3333%|72.1986%|24.5370%|36.7970%|
|4|60.3621%|74.0741%|25.2572%|32.8151%|
|5|66.5395%|75.9620%|27.1205%|32.1618%|
|6|72.7187%|78.5999%|27.8572%|31.0540%|

These are exact expectation values, not success proportions from sampled trials. Whole-source recovery means the entire decoded residue tuple is correct, not character accuracy. A wrong key can decode a short observed tuple correctly; conversely, exact whole-message accuracy need not grow with message length. The two source laws change both initial and transition probabilities. Already the asymmetric initial distribution distinguishes the eight one-packet laws; the difference cannot be credited solely to Markov memory.

## What was fixed and exhaustively checked

The bank remains b, bb, bbb, a, aa with equal spelling weights. A key is(a,b)modulo3. Exactly eight of the nine possible keys cover all three source residues; only(0,0)is invalid. Bank, boundaries and the exact source law are supplied to the scorer. No true key or true plaintext is supplied. All eight true keys have equal prior weight, and every one of the5^noutput strings is enumerated for each n=1..6. There is no chosen favorable message, fitted prior, stochastic search or pruning.

The scorer uses the normalized GDT1322 likelihood including within-class spelling probability. All maximum-likelihood ties receive equal probability. For the uniform true-key prior the expected exact-key accuracy is exactly(1/8)times the sum, over possible output strings, of their largest key likelihood. The full conditional confusion matrices and rational metrics are retained. At finite lengths every output has positive probability under every key, so no universal error-free key decision is possible.

## The intrinsic ambiguity

Under uniform IID source characters, keys(1,1),(1,2),(2,1),(2,2)all produce the bank probabilities(1/6,1/6,1/3,1/6,1/6), in the stated bank order. The other keys form two further equal-law pairs: (1,0)/(2,0)and(0,1)/(0,2). These are three distinct IID output laws, so equality persists at every length. Within a class of indistinguishable keys, no ciphertext-based procedure can favor the true key on average under the uniform key prior. Summing over the three classes bounds exact recovery by3/8.

Scaling all drawing weights by an invertible residue multiplier relabels the decoded residues. An invariant source law preserves the output law; allowing the source law to be relabeled jointly also preserves it, including non-IID laws. The four-key class above is an additional collision beyond the two-key scaling symmetry. Unequal source laws may break these symmetries; that independent restriction must be paid.

This is distinct from the old empirical pooling identity. A fixed uniform source prior still leaves class-size information here. Fitting a separate source prior pi_K(c)=Z_K(c)/5to each key would instead give exactly the same uniform bank output for all eight keys, retaining only1/8exact-key accuracy; that is an old result, not newly measured here.

**Clarification of GDT1322 wording:** its phrase 'same decoder partition' must mean the same labeled decoder, or a class relabeling under which the fixed source law is invariant. The same unlabeled partition alone does not imply equal likelihood under an asymmetric fixed source prior. GDT1322's formulas and numerical results remain unchanged; this qualification prevents an overbroad reading of its prose.

## Validation and decision

The primary uses integer probabilities on a denominator180-per-step lattice and Cartesian output enumeration. A separate validator uses recursive enumeration with exact rational source and emission probabilities. It verifies312,480key/output likelihoods through full-table digests, all12confusion matrices, normalization, both accuracy definitions and law-equivalence classes. Hand checks give9/40and5/24key accuracy for one group. Validation PASS. A bounded source-free reviewer independently derived the class-size collision and tie-risk formula before numerical results.

No Voynich text, image, language corpus or new word meaning was used. This does not establish efficient search over27^22keys, a suitable native bank, native segmentation, a historical writing rule, robustness to source-law mismatch or a realistic recovery rate. GDT1323's native capacity stop remains unchanged. Earlier GDT602/604already show why a controlled recovery result must not be promoted to a target reading.

Retain the narrow positive: the modular channel is not inherently informationless when its bank and asymmetric source law are fixed. Retain the negative: even known spelling rules can leave genuine key ambiguity under an insufficiently distinguishing source law. No native attack or automatic larger control follows. A native proposal still needs independently justified bank/choice policy and source-law constraints; this tiny exact enumeration does not satisfy the full-scale recovery gate.
