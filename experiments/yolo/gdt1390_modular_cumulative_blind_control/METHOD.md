# Method and scope

The [preregistration](PREREGISTRATION.md) fixes the scientific design. This
file explains the exact scoring identity and its limits; implementation
artifacts bind the numerical models and search before controls are generated.

For a complete packet sequence, let s_i be the sum of the fixed22unit weights
in packet i, reduced modulo27. The source character is s_i-s_(i-1)+b, with
s_0=0. Its likelihood is the whole-message source mixture multiplied by
P(w_i)/Z_K(s_i) at every packet. Source characters determine intermediate
states; spelling choices are conditionally independent given those states.
The normalizing masses concern states, not decoded characters.

Every allowed key has an invertible weight. Repeating that unit1..27times
covers all residues, so positive spelling probabilities imply positive state
masses. This proves coverage only; it neither supplies native weights nor
justifies any particular historical word-formation mechanism.

The forward residue calculation carries the preceding unit and cumulative
residue at each position. Summing the final unit yields each length's residue
distribution; mixing lengths gives Z. The independent calculation works
backward from the required final residue and is also suitable for exact
conditional sampling without rejection.

For every invertible a modulo27, Z_(aK)(a*r)=Z_K(r). Consequently the emission
factor for observed words is invariant under common invertible scaling of K.
Evaluating18scales and27offsets reuses one exact normalization, while the six
whole-message source likelihoods are recomputed. This is an exact economy,
not removal of the source prior or selection of a source language.

The completed spelling law is an explicit model assumption. GDT1308 fitted
only lengths at least4; new shorter tables and a length distribution are
required here. Its native adequacy is not established by GDT1389. This control
asks whether the specified recovery procedure works when the writer actually
uses that law. Cached historical source fragments need not be typical of the
trained order3 source model, so a wrong high-scoring recovery can reflect
source-model mismatch as well as short-message ambiguity.

Correct plaintext on one observation does not establish the whole numerical
key. Unused or dependent unit-count columns can leave parameters unidentified.
The experiment therefore separates complete-message recovery from key
equality and from the relative likelihood of the known true key. No target
packet, English gloss, phonetic assignment or reserve is tested here.
