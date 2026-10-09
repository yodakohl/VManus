# GDT1312: a small binary whole-group code is possible only with a rare signal class

**CAPACITY_FEASIBLE.** Exhausting every nontrivial two-class assignment of the
22working units finds a minimum of22distinct complete bitwords in each reading.
A32-row codebook is therefore not excluded by this finite-panel test. However,
only6/5/3partitions meet the budget in ZL/IT/RF, and the smaller signal class is
rare even in the most balanced admissible assignment.

| Reading | Nontrivial partitions tested | Minimum rows | Partitions needing<=32rows | Most balanced feasible class1 | Its rows | Maximum smaller-class unit share |
|---|---:|---:|---:|---|---:|---:|
|ZL3b|2,097,151|22|6|n,m|30|3553/89732 =3.95957%|
|IT2a|2,097,151|22|5|n|31|3855/102247 =3.77028%|
|RF1b|2,097,151|22|3|m|22|176/86585 =0.20327%|

These are exact maxima over the entire feasible set, not a fitted5%threshold
or an omitted balanced solution. Singleton signal classes were allowed from the
start. None of these partitions is selected as the manuscript's key, and the
result is not a word translation or a full statistical writer.

## Human rule being tested

A fixed key assigns every visible working unit to signal0or1, and each of32
source characters to one distinct nonempty bitword. The source domain includes
26lowercase letters, SPACE, four punctuation marks and NEWLINE. To write one
source character, spell its bitword using any visible member of each indicated
class and put a group gap afterward. The reader classifies the group and looks
up the resulting complete bitword. Original source spaces/linebreaks have their
own rows; output gaps separate encoded characters. The finite message end is
supplied by the record/document boundary, not inferred from an invisible END.

This is a permissive homophonic channel: alternative glyph choices may be
deliberate and still recover the same source character. No random-glyph hypothesis
is imposed. Conversely, those choices do not yet explain native word frequencies,
word construction or local repetitions. A future complete choice rule is a real
obligation, not satisfied merely by coverage.

Word lengths may vary. Leading zeroes are preserved;0,00and01are different rows.
Prefix-free codes are unnecessary because the visible group boundaries supply
the codeword boundaries. Multiple complete bitwords for the same source character
would cost more entries and are not a free escape from the32-row budget.
No source-character values are assigned to native forms in this experiment.

## All feasible partitions

Complement symmetry fixes a in class0; the table gives class1, with ALLother
working units in class0. This is the entire<=32set, not selected illustrations.

| Class1 | ZL rows | IT rows | RF rows |
|---|---:|---:|---:|
|m|22|22|22|
|n|29|31|33, outside budget|
|n,m|30|34, outside budget|34, outside budget|
|cph|31|32|32|
|cfh|26|26|27|
|cph,cfh|31|32|33, outside budget|

Thus m, cph and cfh isolated individually are the only three partitions feasible
SEPARATELYin every reading. Their codebooks may differ; this is not a pooled
transcription or one common decoded plaintext. The partition with best worst-reader
activity isolates m. Its smaller-class shares are0.19948%,0.21908%,0.20327%in
ZL/IT/RF. The minimum-row witness also isolates m in each reading.

All admissible partitions make the vast majority of glyph occurrences signal0.
For a group containing none of the selected rare units, its complete bitword is
only a run of zeroes, so its length alone determines the proposed source character.
The detailed shapes then provide no additional payload distinction in this
specific channel. For example, under every common partition, standalone daldy
and daiin each project to00000in the working segmentation. This is a conditional
code equality, not a claim of equal natural-language meaning, a character value,
or pooling a standalone word with an embedded substring.

For the common m-partition the ZLfive-zero row gathers4484occurrences from897
whole types; the four-zero row gathers4438from601types. Those are projected
codeword frequencies, not native word counts or a translated alphabet. The
artifact includes all projected patterns and type/token counts for each selected
witness. The exact minimum22does not identify22source letters in the manuscript.

## Why this is an exhaustive result

For a partition b, let K(b)be the number of DISTINCTcomplete projected bitwords
among all retained groups. Every observed bitword needs one codebook row. K<=32
is necessary, and sufficient only for finite-panel codebook capacity: inject the
observed bitwords into abstract source symbols, then fill unused rows with other
unobserved nonempty bitwords. That construction need not yield meaningful text,
match unseen pages, or provide a reasonable native glyph-choice rule.

Fixing a=0removes the irrelevant global0/1swap. All2^21−1nonzero remaining masks
are enumerated; the all-zero reference is stored but excluded from every minimum,
feasibility count and balance choice. Reversing every word preserves pattern
cardinality, so a second reading-direction scan adds no capacity alternative.
The sentinel representation2^length+binary_value preserves lengths and leading0s.

The primary Gray traversal flips one unit class at a time and updates weighted
pattern frequencies. Its runtime bit order puts rare type incidences first and
has no effect on the exhaustive answer. The independently implemented recursive
traversal assigns classes in the reverse order, rolls back each change, and uses
TYPEcounts rather than occurrence weights. It verifies every stored K(mask),
including the zero reference:6,291,456reader/count entries. Every reported
balance and tie is checked by exact rational arithmetic, not floating-point ties.

Independent raw segmentation, source guards, panel frequencies and witness
projections are also reconstructed:61181groups and4875distinct raw forms.
Small alphabets2..6compare both implementations to direct Python set projection;
a separate toy code demonstrates unambiguous reading of prefix-containing bitwords
through supplied gaps. These checks concern computation and the contract, not
independent palaeography or native meanings.

## Scope, predecessors and decision

The input is the unchanged1233strict Pcache: definite outside gaps and unique22
working-unit parsing in the179admitted selectors, with readers kept separate.
No group was dropped because of its frequency or an inconvenient bit pattern.
No new raw transcription/image, f84/f84r/f116v/f1rbody, old327/336body or reserve.
Uncertain physical units and gaps, including1311's qualifications, remain actual
assumptions. The selected panel is already exposed; no held confirmation claimed.

1264's binary interior alternation,1300's continuous Huffman channel,192's source
expansion model and889's arbitrary edit-correction capacity are different tests.
Their successes and failures remain unchanged. The present source-character/group
contract also differs from1202's source-WORD/group frequency constraint.
These two signal classes are not1310source letters: a whole bitword carries
one source character here, and glyph choice is free rather than its deterministic
local allograph function.1310is not reopened or contradicted.

A post-result predecessor illustration from the already exhaustive arrays: the
frozen1264class split needs353/375/366complete bitwords if its previously
unclassified m is placed in class0, and354/375/368if m is placed in class1
(ZL/IT/RF). Both possible completions exceed32. This does not undo1264's
positive alternation statistic; it shows that that statistical split is not
this small whole-character code. No additional partition fit or gate was used.

Retain a narrow mathematical possibility, not a selected writer. A compact binary
code with two substantial signal groups cannot be inferred from these data: every
<=32solution has the bounded rare-class activity shown above. Nor does the result
rule out every larger codebook, different segmentation, mixed channel or language.
Do not add rows, merge codewords, choose a favorable reader, or fit a language key
automatically. Further progress requires a separately justified plaintext or
construction discriminator that confronts the near length-based payload and the
still unexplained graphical choices. No translated word was obtained.

Protocol and both implementations were hash-locked16:14:06UTCbefore enumeration.
The producer's proof review was source-free and before any result. Complete
per-mask arrays, guarded input panel, witnesses, source hashes and verification
are published for reproduction. The60minute inclusive budget ends16:57:55UTC.

A publication-stage engineering correction moved scratch files out of a GDT-named
cache directory that the index treated as misplaced experiment artifacts. The
registered scientific programs and lock remain byte-frozen; reproduce.py changes
only their runtime cache path. Both wrapper commands reproduce the same numerical
artifact hashes. CACHE_LAYOUT_NOTE.json discloses this post-result correction.
