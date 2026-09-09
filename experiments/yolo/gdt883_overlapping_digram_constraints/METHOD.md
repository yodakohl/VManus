# GDT883 — exact overlapping-pair constraint

Registered before pair extraction or scoring, 2026-09-09.

Decision: test whether adjacent written symbols can be overlapping pairs of an
unknown underlying alphabet: a fixed symbol g has pair (L_g,R_g), and every
within-group adjacency gh requires R_g=L_h. Unknown values and alphabet size
are unrestricted. An injective pair alphabet additionally requires different
written symbols to have different pairs. A homophonic version allows equal pairs.
This is a precise candidate mechanism, not an observed property or historical
attribution. The strong positional structure motivates testing overlapping units;
it does not establish that the mechanism was used.

Primary predecessor review: GDT188 excludes fixed one-to-one renaming for its
specific Latin controls; the older typology-neutral audit establishes productive
structure without excluding all ciphers. GDT605 tests a learned unit alphabet
against ordinary letter readings. None of these is this pair-overlap equality
system. GDT882 concerns a different whole-line additive invariant. No language
model, comparator corpus, guessed meanings, or cipher-key search is used here.

Smallest test: reuse only the 413 admitted odd-leaf loci in GDT882's frozen
SELECTED_LINES. Require exact agreement of all three complete raw-group arrays.
Retain groups whose two external boundaries are definite spaces or line ends in
all readings. Panel L uses literal EVA characters. Panel S uses exact official
STA member codes in those same groups, obtained by selector-first query of the
cached source alignment on precisely these loci, with f84/f84r forbidden. S also
requires zero marked alternatives, exact member-sequence agreement among all
three readings, matching source indices/counts and separators. Panels are fixed
before either is scored; no family merging or learned segmentation. These remain
transcription units, not proven linguistic units. No cross-group adjacency.

For each panel form an undirected equality graph on every L_g and R_g; every
observed gh contributes edge R_g--L_h. Connected components are the most general
solution, up to merging components. Publish a spanning forest with source witnesses,
component pairs for every symbol, and forced collisions. If distinct symbols
have identical component pairs, the injective model is impossible. If all used
components collapse, only group length distinguishes underlying sequences under
the homophonic model. Otherwise retain the precise unresolved freedoms. A surviving
model is compatibility only; before any later decoder it would need a separately
justified discriminating prediction. A failure closes this exact class at that
fixed unit scale; no adaptive atomization, exception allowance or longer code block.

Prospective corollary: the same forced collision excludes an injective fixed
block code of EVERY length k>=2, when successive blocks advance by one underlying
symbol and overlap by k-1. For each adjacent coordinate pair j,j+1, the block
coordinates satisfy the same endpoint graph; equality of both endpoints for g,h
therefore forces all k coordinates to agree. This entails no additional data
selection or fit. Variable lengths, other strides and error exceptions are outside
this contract.

Implementation and an independent graph-closure validator must reconstruct the
source groups and verify every forest witness. Two/three readings are alternative
readings of one manuscript, not independent replicates. This is an exact necessary
condition, with no p-value, semantic score, relation packet or held-leaf claim.

Total budget: 20 minutes including the preceding bounded review, implementation,
verification and publication; checkpoint before extending source scope. All data
needed are already admitted. On input/validation failure stop and repair only a
bounded implementation error; do not change the model to secure a finding. The
fixed exact-member panel addresses EVA's composite-unit limitation prospectively.
