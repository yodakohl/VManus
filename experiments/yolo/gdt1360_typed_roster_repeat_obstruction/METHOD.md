# GDT1360 — Canonical rosters under a whole-word typed-record reader

## Decision before executable replay

Select IDEA001040, a newly explicit physical realization of1038, contrasted with
1039. Every typed logical group, including FRAME/SUBJECT/HEAD/MEMBER, emits exactly
one nonempty visible whole word. A word identifies one typed group globally,
without hidden context. Allow arbitrarily many spellings per group, provided the
spelling sets of different groups are disjoint. Thus the test is more generous
than one fixed injective codeword per group; it demands no particular alphabet,
width, field code or efficient human dictionary.

This condition was NOT supplied by RAW1038, which left its physical carrier open.
Rejecting the added realization does not reject all roster content or require
all meaningful writing to be globally unambiguous. Unknown carrier1038 remains
inconclusive. The fact being tested concerns content grouping, not another small
alteration to individual source-word spellings.

Unknown: can this broad but explicit whole-word realization encode the canonical
1038stream when the old confirmed-within-transcription doublet is retained? The
smallest adequate test is an all-input adjacency proof plus replay of the already
saved1274cases. A contradiction prevents building that roster decoder. A phase
repeat counterexample only shows that the same observation does not exclude1039;
it supplies no native temporal interpretation or selected future decoder.
Conservative allocated window14:15–15:05UTC12October2026 includes selection,
proof, implementation and publication. First explicit clock14:32:45; allocation
is not a measured start claim. No expansion beyond this proof and old packet.

## Universal roster property

The canonical1038writer has unique context IDs and one FRAME per context. SUBJECT
names occur once in the initial domain declaration of each frame. Each HEAD owns
a nonempty roster. MEMBER(subject,count) occurs once per subject under that HEAD;
count is positive. Switching heads or frames inserts the corresponding typed
group. Constructor tags are part of logical group identity.

Different tags cannot be equal. The possible equal-tag adjacency cases are:
- FRAME/FRAME: different context IDs, hence different groups;
- SUBJECT/SUBJECT: different subject names within one declaration;
- MEMBER/MEMBER: different subjects within one roster;
- HEAD/HEAD: impossible because the first roster is nonempty.
Across rosters/frames the intervening group changes the tag. Therefore no valid
canonical source stream contains adjacent identical typed groups. This remains
true for empty frames, empty-profile declared subjects, selflinks, literal external
targets, contradictory signed observations and multiplicity written in count fields.

If adjacent visible words were identical, their globally single-valued typed
readings would be identical, contradicting this property. Disjoint spelling sets
make arbitrary optional spelling variation irrelevant. This is independent of
paragraph-to-roster identity, but needs one further explicit premise: each
nominated within-line pair belongs to ONE canonical source document. No unmarked
document restart is allowed between its words. Definite spaces do NOT prove this
semantic scope. Concatenating independently compiled empty documents with the same
context ID could otherwise emit FRAME(C),FRAME(C); that escape is outside this
realization. All FRAMEgroups remain written. One paragraph need not be one roster.

## Frozen existing evidence and contrast

Use ONLY the three cases already in1274RESULT.json, cross-check its manifest hash
and631allowlist. They are the known qokeedy doublets: ZL f108r.48 groups10–11,
IT/RF f103r.37 groups5–6. Preserve complete line data and all three definite seams
across the four-group neighbor span. Reader agreement is not independence; there
are two physical loci. No new raw TSV, image, source corpus, native census, reserve,
f84/f84r/f116v/f1rbody. Exact source boundaries and transcriptions remain premises.
No wordmeaning, phoneme or source identity assigned to qokeedy.

The witness was known before this proposal; this is an EXPOSED DEDUCTION, not a
new discovery, blind prediction or significance test.1274's reference-cost result
remains separate. RelatedIP080single-tree paragraph exclusion is not reopened
with invisible forests.1210/1220content-frequency failures and1002/1003semantic
organizations retain their scopes. Bounded review is not exhaustive originality.

For1039 retain a source-only schedule with two PHASE(1,P)groups, where Pcontains
one positiveDRY observation. They produce intervals[0,1)and[1,2). The record
boundary at1is source content. Same typed groups may use the same codeword, so XX
is compatible even with a globally injective encoding. No codeword is equated to
qokeedy and no native duration, profile, unit or clock is inferred.

Also retain a small OUTSIDE-contract counterexample: in a restricted fixed
four-group FRAME/SUBJECT/HEAD/MEMBER grammar, let the positive HEAD and MEMBER
share one opaque word ID, with positional decoding. Opposite-polarity inputs
still differ at HEAD. This shows why global context-free word decoding matters;
it is not a complete alternative carrier for1038or a Voynich fit.

## Source-free controls and independent validation

Before native replay, enumerate small valid observation multisets with canonical
roster encoding/readback, including empty data, counts, opposite signs, zero mass,
self/external links and empty declared subjects. Check absence of equal neighbors
and finite examples of disjoint multi-spelling sets. These controls supplement
the universal tag/value proof, not statistical evidence or a power analysis.
Check repeated positive phase intervals and the contextual-homograph countercase
using opaque synthetic IDs only, never native-word values.

Freeze protocol, code, controls, proof review, proposals and old evidence before
executable replay. Validator imports no runner, independently locates/compares
whole-word rows and seams, verifies old output hashes and the declared contrasts.
PASS means source accounting and formal consistency; no independent palaeography
or native semantic confirmation. No later marker, homograph, multiword group or
zero-cost frame change repairs this fixed realization after failure.
