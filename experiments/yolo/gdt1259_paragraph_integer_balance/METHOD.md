# GDT1259: fixed integer paragraph balance

## Decision and predecessors
GDT882 excludes constant sums on physical lines over20 literal transcription
characters; it does not imply constant sums on whole paragraphs over22 working
units. The old single-tree paragraph obstruction assumes one wholeword arity.
The source-free proof review bound in SPEC supplies an explicit counterexample
to subsumption and preserves those earlier failures. The positive premise used
is the existence of source-marked paragraphs; their syntactic status is unknown.
Question: can globally fixed integer weights on active working units give one
common total C for every complete paragraph in the declared scope?
A full-rank result rejects that precise simple completion-counter class. A
rank-deficient result stops at necessary capacity; no parser follows. Either
outcome changes whether this necessary invariant is available to that class.
An arbitrary forced reset at the boundary is NOT a common naturally attained sum.

## Fixed population and representation
ZL3b primary, IT2a separate sensitivity; RF1b has no usable own flags (1073) and
is excluded before querying. Use the179 selectors from the unchanged1170spec,
selector-first guard, exact columns in SPEC. No sealed/reserved pages or images.
Source row indices enumerate parsed loci, not comments or physical file lines.
Group rows by reader/page/locus; require unique indices1..declaredcount and
consistent line metadata. Iterate by source_row_index within each page.
A candidate starts at a P line with paragraph_start=1 and ends at the first
paragraph_end=1. A new start, non-P line, nonconsecutive source-row index or page
end aborts the old incomplete candidate; a new marked start may start another.
No leading unmarked fragments are completed by assumption. A line with both
flags is a complete one-line paragraph. Markers are the atlas source annotations,
not newly observed authorial or independently image-validated boundaries.
For each complete candidate, retain ALL groups/lines or exclude the WHOLE paragraph.
Exclude if any raw group fails exact unique parsing in the fixed22 units, or any
separator is not LINE_START/LINE_END/DEFINITE_SPACE/UNCERTAIN_SMALL_SPACE.
Uncertain small spaces are allowed because total counts do not depend on word
seams. No entities, braces, case or unsupported glyphs are normalized. Zero-token
missing loci create an index gap and invalidate a spanning candidate. Report
all aborted/complete exclusions. The working alphabet is a model, not established
linguistic segmentation. Allactuallyobserved units form the active column set.

## Fixed exact test
For each reader separately, construct all rows[counts,-1] for retained paragraphs.
With m active units, rank m+1 over the rationals proves w=0,C=0 and excludes every
nontrivial integer assignment on observed units, including +/-1 bracket counters.
Global relabeling permutes columns and does not rescue rank. No modular/nonabelian
claim follows. Absent signs remain unconstrained. Empty population is unscorable;
nonfull rank is necessary capacity only, not valid prefix nesting or semantics.
Select independent original rows deterministically in page/source order by exact
rational elimination. Save the original count vectors and full raw witness lines.
A separate validator rebuilds census/eligibility with a different paragraph scan
and parser, checks the full matrix, and validates a nonzero exact determinant of
the selected square minor with integer Bareiss elimination. No numerical tolerance.
No alternative alphabet, new boundaries, prefix parser or context repair afterward.

## Budget and disclosure
Inclusive45minute interval14:32:32--15:17:32UTC on2026-10-07 includes preparation,
implementation, validation and local publication. Stop expansion at the endpoint.
Protocol and both programs are hash-locked before the first native query. Earlier
source/flag reviews are disclosed prior knowledge; no count matrix yet inspected.
Local checkpoint only per4October instruction. No word meaning or source-language
assignment is made. Alternate readers are not independent manuscripts.
