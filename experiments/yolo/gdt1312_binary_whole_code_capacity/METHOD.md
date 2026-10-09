# GDT1312: binary whole-group codebook capacity

Exploratory exact capacity test, not a language decoder. Inclusive60minute budget
15:57:55–16:57:55UTC9October covers selection, proof, implementation, independent
verification and publication. No bigger alphabet/codebook, marker or grouping repair
after the outcome. Stop computation at the budget rather than expand this test.

## Complete conditional hand channel
A fixed key partitions all22working units into TWO nonempty signal classes. It
also assigns each of32source characters one distinct nonempty binary word. The
source alphabet is a..z, SPACE, comma, period, colon, semicolon and NEWLINE:32inall.
Unsupported source characters stop explicitly. For each source character the
writer looks up its bitword, writes one member of the appropriate signal class
for each bit, then a visible group gap. A finite message ends at its supplied
record/document boundary; source NEWLINE and SPACE have explicit codewords and
are not borrowed from output layout. Empty input has zero groups.

Within-class graphical choices are freely allowed and may be deliberate, not
assumed random or learned from a source language here. Every such legal choice
decodes to the SAME source character. A reader classifies the complete visible
group, looks up the resulting binary word, and concatenates the recovered source
characters. Thus this is an unambiguous reader for a permissive homophonic writer
family, once a key is supplied. There is no claim that free choices explain the
native word distribution or constitute a recovered economical choice rule.

Visible gaps delimit source CHARACTERS, not source words. Arbitrary positive
bitword lengths are allowed; leading zeroes are significant. Prefix freedom is
unnecessary. The32-entry budget includes all32source characters, even if some
are absent from a sample. Several distinct bitwords for one source character
would consume additional entries and are outside this budget. No glyph or native
word receives a source-character or semantic assignment during this test.

## Unknown, decision and predecessors
For any proposed signal partition b, every distinct projected whole bitword b(w)
requires a codebook row. K(b)<=32is necessary. It is also sufficient for this
finite panel's codebook CAPACITY: assign the observed bitwords to distinct abstract
source symbols and fill unused rows with other unobserved bitwords. This does not
make the decoded sequence meaningful or select the partition/source key.

If all nontrivial partitions need>32rows, stop this entire fixed family. Otherwise
retain only capacity feasibility with the exact cost/activity profile; do not
promote a viable manuscript writer, decode by language-model guessing, or add a
new source fit automatically. Computing the exact feasible set's maximum smaller-
class occurrence share will show whether capacity requires an almost unused
second signal class, without imposing a post-result balance threshold.

1264optimizes interior alternation, not full bitword count;1300uses continuous
source bits and contextual Huffman/pair tables, not a global22→2projection;
192marks variable source expansions;889guarantees arbitrary one-edit correction.
Their different decisions remain unchanged.1202whole-SOURCE-WORDfrequency limits
do not directly apply because the present visible groups carry source characters.
Source-free producer proof, composition topic, bounded duplicate/route searches
and these claim-bearing primaries were inspected. Empty searches are not proof
of novelty. No old failed writer is rescored or repaired.

## Fixed input and exhaustive calculation
Use unchanged1233strict interior Pgroups with definite outside gaps and unique
22-unit parsing, current179selector allowlist, each reader separately. All groups
and types are included, without frequency filtering. No rawTSV,image,reserve,
f84/f84r/f116v/f1rbody or327/336body. Source and boundaries are assumptions;
all material is exposed. Readers are not independent replications.

Unit order: a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh.
Complement symmetry fixes a=0. Enumerate every nonzero assignment to the other
21units:2,097,151partitions per reader. A global0/1swap and common word reversal
preserve K, so do not rerun orientation variants. Do not trim first/last units.

Represent a projected length-n bitword by integer(2^n + binary_value), so length
and leading zeroes cannot collide. Stop before optimization if any source word
exceeds20units; this is a declared array/memory bound, not permission to truncate.
No source grouping or cap adjustment follows such a stop.

Primary outputs for EACH reader: exact minimum K and smallest-numeric original-
unit-mask witness, number of K<=32partitions, and among those the largest smaller-
signal-class share of all retained unit OCCURRENCES (ties smallest mask). Report
both class inventories, actual projected bitwords with type/token counts, and
source units/types contributing to each selected witness. No source letters or
meanings assigned to these codewords. The existence of one feasible partition
is not a native alphabet inference. Singleton signal classes are allowed.

Secondary: number of masks with K<=32SEPARATELYinallthree readings, and the mask
maximizing the worst of their smaller-class shares, ties smallest mask. Readers
are not pooled; the codebooks may differ. This is not one joint decoder fitting
all transcriptions. No minimum activity threshold or best-language score.

Retain every K(mask) in deterministic little-endian uint16arrays indexed by the
original-unit mask>>1, including index0as an explicitly inadmissible all-zero
integrity reference. Bounds fit within observed type count; verify<=65535.
Compressed arrays and exact input panel preserve exhaustive-check reproducibility.

## Implementation and validation
Primary Gray traversal updates each affected word's bit projection when one
unit changes class; pattern frequency uses occurrence WEIGHTS. Bit order is fixed
by increasing total distinct-type incidence across the three readers (lexical
label tie), affecting runtime only, never the exhaustive answer.
Independent traversal assigns bits recursively in reverse order and rolls back;
it uses TYPEmultiplicity per projected pattern rather than token mass and checks
every saved K(mask). It rebuilds the input from the guarded source separately,
including raw parsing, and recomputes witnesses directly from words. Neither
validator imports primary optimizer code. No stochastic algorithm or optimization
restart. Source-free small alphabets compare exhaustive direct-set enumeration,
preserve leading-zero/length distinctions and demonstrate prefix-containing
bitword tables with unique reading via supplied group gaps.

This tests a key-independent necessary codebook budget. It does not recover
plain text, certify a medieval origin, explain whole-form selection, establish
word/letter boundaries, or treat a small bit-pattern count as a translation.
