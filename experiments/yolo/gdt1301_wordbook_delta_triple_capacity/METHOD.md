# GDT1301 preregistration: whole-word rank displacement

Frozen before counting source progressions on 2026-10-09.

## Decision and budget
The specific unknown is whether a fixed alphabetical whole-word displacement
writer has enough distinct repeatable codes for the four common exact AAA forms
already retained by GDT857. This differs from GDT1268's letter-coordinate
subtraction and GDT1217's previous-letter ring. Ring arithmetic itself is old
(IDEA237); static ordinals (IDEA960) and trie child ranks (GDT1229) are also prior
work. Their failures remain unchanged. Bounded route/registry searches and the
relevant primary followups were inspected before selection; no exhaustive
novelty claim is made.
Smallest test: count exact source arithmetic progressions, without fitting any
Voynich glyph table. Inclusive budget: 10:38:08–11:23:08 UTC (45 minutes),
including prior review, implementation, independent validation and publication.
If capacity is below four, exclude this fixed source/order model regardless of
its injective codeword table. If at least four, retain only NOT_EXCLUDED and do
not assert statistical fit or adopt a decoder. No automatic new source,
reordering, reset, alias, threshold or table enlargement follows either result.

## Writer and inverse
For each of the four unchanged GDT1177 books, W is its distinct exact stored
whole-token strings sorted by Unicode lexicographic order, without normalization.
V=len(W); rank is zero based. Choose one fixed paragraph-start anchor a in
0..V-1. Each source recipe starts at a; line wrapping does not reset state.
For source word w emit C[(rank(w)-state) mod V], then state=rank(w).
C is any fixed injective map from residues to distinct nonempty whole codewords
over the 22 working units. Reader inverts C, adds the residue modulo V, and
returns W[state]. The fixed dictionary, C, V, and visible recipe boundaries are
paid key information. This is closed-vocabulary; OOV insertion is unsupported.
No native word meaning is assigned, no historical attestation is asserted, and
no physical glyph codebook is fitted in this necessary-capacity test.

## Necessary capacity
An interior triple of identical outputs requires FOUR consecutive source ranks
r,r+d,r+2d,r+3d modulo V. Include d=0, order-2 and order-3 cycles; ranks need not
be distinct. Let I be all residues with such an interior witness in any recipe.
For the first THREE ranks r0,r1,r2, if their successive differences both equal d,
an initial triple occurs only at anchor a=(r0-d) mod V. Put d into P[a].
For a shared anchor, triple-capable residue set is I union P[a]. Primary capacity
is Kmax=max_a |I union P[a]| over ALL shared anchors, not a fitted convenient
reference anchor. Also report anchor-zero capacity and maximizing anchors.
Distinct repeated codeword types require distinct residues because C is fixed
and injective. Different source words may legitimately share an output code
in different states. Many witnesses for one d still give only one code type.

## Native evidence and decision
Reuse GDT857 HITS only, preserving editions. Primary required capacity is FOUR:
sheol, okaiin, chol, ytaiin at its four common exact coordinates. Reader-specific
sensitivity targets are six ZL3b, seven IT2a, five RF1b distinct forms. Readers
are alternative readings of one manuscript, not independent replications.
The old transcription premise is not new image confirmation. All common hits
are interior in their retained lines; no new raw TSV or pixels are admitted.
Kmax<4 => PRIMARY_CAPACITY_EXCLUDED for that source book. Otherwise NOT_EXCLUDED.
Reader-specific inequalities are diagnostics, not a changed primary target.
The source books are comparison texts, not claimed original plaintext. Changing
word order, vocabulary/collation, paragraph boundary convention, code aliases or
source content lies outside the exclusion. Rotations and reflection of the same
rank circle preserve maximum capacity over anchors.

## Validation
Independent implementation must reconstruct ranks and test modular second
differences rather than reuse the runner's delta-window predicate. Check every
maximizer, reference capacity and witness. Recover every stored source token
using the numerical channel. Toy cases cover zero steps, order2, order3,
ordinary progression, initial triple exception and paragraph resets. Exhaustive
small-rank fixtures compare the closed-form capacity with direct encoding for
all anchors. All input hashes and this preregistration are locked before count.
f84/f84r forbidden; no reserves or new image grants.
