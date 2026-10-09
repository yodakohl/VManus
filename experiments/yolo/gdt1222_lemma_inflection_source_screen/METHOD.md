# Projection and invariance

A lexical atom is (W,lemma,UPOS,features,traditional mood,traditional tense,
unknown-form fallback). Features are key-sorted key/value pairs, with their
literal values unchanged; null denotes the source underscore, not a zero
feature. A punctuation atom is (P,exact FORM). Every group contains one
lexical atom and its attached punctuation, except all-punctuation sentences.

Decoding the abstract groups concatenates their atom lists. This exactly
recovers the selected analysis stream and its declared boundaries, not FORM,
XPOS, dependencies or discarded MISC. Feature bundles may distinguish source
homographs and merge orthographic variants; no bound of two aliases applies
without an additional proof. Under a common injective code on complete groups,
equality classes and their frequencies are invariant. Hence both frequency
conditions are necessary independently of the future22-sign carrier.

Runner uses streaming sentence parsing and accumulates groups while reading
atoms. Separate validator parses blank-delimited blocks and assigns punctuation
to the nearest preceding lexical position, or first following one if leading.
It reconstructs all source/sample hashes, inventories, manual contrasts,
roundtrips and comparisons. Both implementations have the same author; their
agreement tests source/software consistency, not historical interpretation.
