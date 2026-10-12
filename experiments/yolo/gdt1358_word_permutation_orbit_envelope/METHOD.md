# GDT1358 — Orbit-frequency envelopes for within-word reordering

## Decision before counting

IDEA001034 cyclically cuts a word using the previous word's length.1256already
excludes its unchanged Deot/one-letter case; do not rerun that old source. A
broader new necessary consequence addresses the actual observed spelling
variants rather than an assumed maximum of two aliases per source word.
Select IDEA001036: any exact source word has one fixed nonempty base spelling,
then each occurrence may freely rotate it, or more generously permute its units.
No cost, human algorithm or invertibility requirement restricts these choices.
Multiple source identities may share an orbit. Test their frequency consequence
before fitting any alphabet or a specific cyclic-cut decoder.

Unknown: how much native word diversity/concentration remains after quotienting
out ALL permitted ordering variants, and whether the four existing8000-token
source profiles satisfy the resulting necessary coarsening inequalities. A
violation stops fitting this much broader source/base-spelling/reordering family
on those exact profiles. A pass retains necessary capacity only, not a writer.
The source-independent native bounds remain useful without selecting a language.
No new corpus or cutoff is chosen for success. Smallest adequate test: exact
orbit tables, cumulative frequency inequalities and a conservative whole-group
replacement lower bound; no optimizer, language scorer, source decoder or image.
Conservative allocated work window13:00–13:45UTC12October2026 includes selection,
implementation, proof, validation and publication. First explicit clock reading
13:14:33;13:00is an allocation, not a claimed measured start. Stop expansion at45.

## Inputs and scope

Use unchanged1233strict INTERNAL Pgroups,631allowlist, and1177SOURCE_TEXTS.json.
For each IT2a/RF1b/ZL3b separately: native FULL and first8000cache rows in their
stored order. FIRST8000is a prospectively fixed exposed prefix, NOT1174's target
sample. No inherited1174/1202+/-400tolerance or statistical decision threshold is
transferred to this new quotient. Native FULL supplies descriptive native-only
bounds; source comparisons use FIRST8000only.

Sources: b4,w1,bs1,gr1 each first8000stored words, recipe and word order unchanged,
including punctuation/case and all editorial projection choices. They are fixed
comparison profiles, not identified Voynich originals or universal surrogates
for medieval languages. No paragraph, passage or source subset search. The source
alphabet need not have22letters: each whole source word may receive an arbitrary
fixed base codeword over the22working output units. This enlarges1034's exact
letter-bijection writer and avoids hiding an alphabet-size assumption.

All raw group strings are independently reparsed with the inherited22working
units; source IDs, Pkind, definite external spaces, allowlist and exclusions
retained. Alternate readers are not independent samples. No new raw TSV, image,
f84/f84r/f116v/f1rbody or reserve. Working units and complete-group/source-token
correspondence remain assumptions. No native word or sign meaning assigned.

## Orbits and exact necessary bounds

CYCLIC: canonical signature is the lexicographically least whole cyclic rotation.
BAG: signature is the sorted complete unit multiset, including multiplicity.
A fixed bijection of symbols may change a canonical representative, but cannot
change orbit membership or its frequency profile. BAG is a generous enlargement
of CYCLIC. Do not call members of either observed orbit actual synonyms.

Let S be the sorted frequencies of distinct exact source words and B the sorted
frequencies of native orbits, both totaling N=8000. A fixed source word always
maps to one orbit; different source words may merge into it. Hence B is a
coarsening of S. Necessarily:
- number of native orbits <= number of source word types;
- sum of largest k B counts >= sum of largest k S counts, for EVERY k.
Pad shorter vectors with zeros and include k=0. The k most frequent sourcewords
flow to at most k outputorbits; those orbits contain at least their total mass.
These inequalities are necessary, not a complete integer partition test.

A replacement changes one entire target group into an arbitrary other group,
keeping N fixed. It can change the number of active orbit classes by at most1,
and can change each largest-k frequency sum by at most1. Therefore
D=max(0, |B|-|S|, max_k(sumTopK(S)-sumTopK(B)))
is a LOWER bound on target group replacements needed before any output of this
fixed-source family could be obtained. Take the maximum, NOT the sum. Preserve
all comparisons, with smallest k witnessing the largest nonnegative prefix gap.
D=0means not excluded by these bounds, not a realized mapping. D/N is a
conditional replacement burden, not an observed transcription error rate,
optimal repair, distance between languages or p-value. No repair will be made.

For native FULL/FIRST8000 retain raw type count, orbit count, sorted orbit-count
vector, maximum and Top10orbitmass, plus every orbit/member/source-ID table.
They imply a minimum source vocabulary size and maximum possible mass of its
k most frequent words under the stated family, not a recovered vocabulary.
For each source retain exact first8000frequency table and ordered-prefix digest.
For all24reader/family/book comparisons retain types/prefix lower bounds,
max-gap witness, D and [D,8000]. All source profiles and readers stay separate.

## Novelty, validation and stop

Reviewed1034,1256primary/followups,1202primary/followups,1323primary andIP036.
1256uses one rare native multiplicity signature and a fixed literal source
alphabet.1202allows at mosttwoaliases.1323's neighbor-echo conditional permutation
stopped for insufficient capacity; it remains stopped. None supplies these new
global orbit coarsening counts. No synonym, prior statistical failure rescue or
unreviewed history conclusion is imported. Bounded search is not exhaustive
novelty proof.

Before native counting: exhaustive small source frequency assignments and
coarsenings verify inequalities; one-group replacement controls verify D<=1;
short-string rotation/bag controls verify canonicalization. Freeze protocols,
programs, controls, proposal, proof review and all inputs before first result.
An independent validator must import no runner, reconstruct sources and native
panels, independently group orbits and replay all bounds/support/digests. PASS
validates arithmetic and provenance, not source identity or linguistic use.
No additional metric, source, threshold, error budget, decoder or tighter
optimization is selected after outcomes.1034without a source is not globally
refuted by a comparison-profile failure; earlier exact source failures stand.
