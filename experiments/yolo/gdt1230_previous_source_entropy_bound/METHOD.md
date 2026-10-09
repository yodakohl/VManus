# Empirical proof and exact scope

Choose an index uniformly from all actual within-word adjacent output pairs of this fixed source. At that index Xis the current source letter, Pthe preceding one, Qthe one beforeP(or the public reset sentinel). The preceding output Z=f_Q(P)is deterministic from(P,Q). The current output Y=f_P(X)is bijective inXat each fixedP. Thus

`H(Y|Z) >= H(Y|Z,P,Q) = H(Y|P,Q) = H(X|P,Q)`.

This uses only finite counts and conditional-entropy monotonicity. It assumes no language stationarity, no independent characters, and no correct guess of the22!sign names. Neither source letter probabilities nor output rows are fitted. Arbitrary fixed previous-letter row permutations are covered, including the simpler circular-distance subset.

Qat a word's first pair is critical: with word reset it is RESET; with paragraph reset it is the preceding word's final letter unless this is the first word of the paragraph. A preceding one-letter word contributes no pair of its own but still suppliesQ. The source orientation is applied before this stream bookkeeping. Reversing already encoded words is a different operation and is not automatically covered.

Additional position counters, preceding-output memory, line resets, long-prefix/whole-word state, character expansions, noninjective channels or changed word groups are outside this family. All source words are checked to fit the24cell row convention without splitting. No such alternative is thereby preferred or selected.

Reusing1228nativeH2means no new raw query and no rescore of an old writer. Compare to all scoreable cells, not a preferred genre/hand/reader. A low bound is simply inconclusive; satisfying a necessary lower-bound condition does not construct an output that attains it.
