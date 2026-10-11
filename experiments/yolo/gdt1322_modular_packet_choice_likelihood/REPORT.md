# GDT1322 — complete modular packet channel, source-free check

Decision: NORMALIZED_CHANNEL_AND_RANKING_COUNTEREXAMPLE. The invented writer has an exact inverse on its declared lowercase-and-space source domain. It is not a fitted Voynich system or a recovered key.

## Construction and result

Give each of 22 abstract drawings a fixed value modulo 27. A whole group decodes to the sum of its drawing values modulo 27: zero is a source space, 1–26 are letters. Choose the spelling from a fixed finite bank, with replacement, using declared positive weights. Physical spaces separate packets; source spaces have their own packets. The bank must cover every residue. Word order and shapes are paid bank apparatus, not explained by addition.

The teaching bank contains the 22 singleton drawings and all 484 ordered pairs, with drawing values 0–21. All 506 alternatives decode correctly and all 27 classes are covered. Packets (1), (6,21), (5,21) restore `a z`. Both (13,15) and (15,13) encode `a`: their ordinary sum is 28. This deliberately short bank is not a proposed native repertoire.

For fixed bank weights q and an independently fixed normalized source prior at a specified source length, the correct likelihood is

`P_K(w_1,...,w_n) = P_source(D_K(w_1),...,D_K(w_n)) * product_i q(w_i)/Z_K(D_K(w_i))`.

Here Z is the total bank weight of the decoded class. Bank and weights must be fixed before key comparison. A source-only language score omits a key-dependent factor.

The modulus-3 teaching example fixes bank b, bb, bbb, a, aa, uniform bank weights and source initial probabilities (0.6, 0.3, 0.1). Under K1 (a=1,b=0), observed b has source-only score 0.6 but actual probability 0.2; under K2 (a=0,b=1), the corresponding numbers are 0.3 and 0.3. The two rankings reverse. Neither key is designated true: this is not a recovery success. With the fixed transition matrix in FIXTURE.json, exact enumeration of all output strings of lengths 1–3 sums to one separately under each key.

If an IID source prior is instead fitted to each key's own class masses, the bank distribution is recovered unchanged: the old empirical pooling identity remains in force. Fifty two-packet cases verify that special identity. Equal single-character marginals alone do not erase non-IID sequence dependence. Keys giving the same decoder partition on the bank are indistinguishable.

## Validation and scope

An independent validator uses iterative modular folds and recursive enumeration rather than the runner's direct sums and Cartesian products. Exact rational checks cover 506 inverse alternatives, 310 toy sequence probabilities and 50 pooling pairs. Validation PASS. The runner additionally rejects missing residue coverage despite gcd one, an out-of-alphabet drawing, an unlisted packet and uppercase source input; these four exception branches are not independently retested by the validator.

No manuscript text, image, source-language corpus or fitted native key was used. No word meaning was assigned. This checks the abstract decoder and probability model, not a historically used writing practice or Voynich statistics. The fixed contract includes physical wrapping and finite-message framing; no general punctuation or uppercase preservation is claimed.

## Prior evidence and next decision

GDT1231/1232 and GDT1258 concern positive ordinary sums; GDT1232 explicitly excludes modulo, and the value-one singleton argument in GDT1258 does not transfer to modular sums. GDT1286 concerns a common paragraph total, not variable per-group characters. GDT1272 and its GDT978 predecessor use an order-sensitive checksum of an omitted source suffix with a wordbook. Their failures remain unchanged. Bounded primary review found no exact executed predecessor; this is not an exhaustive novelty claim.

Before any native key search, specify the bank and its estimation scope, spelling-choice law, independent source prior and key-search contract. Then require a small known-key recovery control with rival keys. If the decoder cannot recover a known source under its own stated assumptions, do not attack native text. The present result does not authorize an automatic search, new corpus or repair sequence. Unexplained native directed word construction remains a substantive cost of the bank.

The preregistration, raw contract, fixture and both programs were hash-locked before execution. Reproduce with the manifest run and validate commands. This is a completed source-free prototype within the fixed preparation-to-publication budget, not decipherment progress.
