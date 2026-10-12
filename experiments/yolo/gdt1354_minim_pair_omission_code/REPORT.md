# GDT1354 — Explicit suffix codes show that singleton i is not forced

**ALL_FIXED_I_OMISSION_CODES_COVER.** Three small, fixed countercodes cover all
61,181retained whole-group occurrences with exactly one parse per word, without
any singleton i entry. The previously unresolved FULL i question is therefore
settled in each alternative transcription. Together with GDT1353's mandatory
entries and its other omission witnesses, the FULL forced-singleton intersections
are now exact:17IT2a,18RF1b,16ZL3b. No new forced singleton is added.

This is a constructive existence result under the fixed freelyUD whole-word
contract. It is not a decoded language, phoneme inventory, predictive frequency
fit or evidence that the historical scribe chose this code. The proposal was
selected from already inspected endpoint witnesses; no blind selection claimed.

## One simple rule, three fixed instantiations

Choose a set H of signs that may end a two-unit code. Every sign outsideH is
also a singleton code. Every pair ending inH is an offered two-unit code:

    C_H = (Sigma outside H) UNION (Sigma followed by H).

Use H={i,n}forIT2a andH={i}forRF1b/ZL3b, as frozen before full coverage checking.
The names i,n are working transcription units, not sounds, numbers or newly
identified physical strokes. This is not a shared decoding table for all three
readings. They are alternate transcriptions of one manuscript.

Reading from the right, a last sign outsideH is one code; a last sign inH takes
its predecessor with it. All code entries are nonempty. A singleton ends outside
H, while each pair ends insideH; different pairs have equal length. Thus no
entry is a suffix of another. The table is freely uniquely decodable for all
finite sequences of its entries, not merely these observed words.

Coverage is equivalent to even length of the initial H-run. A later odd H-run
can absorb its preceding outside sign; its remaining signs pair internally.
ForIT, initial in and iiin have length2and4underH={i,n}; plainH={i}would fail them.
The RF/ZL chosen initial i-runs are even. This was the source-informed motivation,
not a rule selected after the coverage result. No exception or repair was added.

## Complete result

| Reader | Whole groups / types | Offered entries | Used entries | Used singles / pairs | Groups using a pair | Failures |
|---|---:|---:|---:|---:|---:|---:|
| IT2a |22528 /4272|64|31|20 /11|4359 (19.35%)|0|
| RF1b |19321 /3818|43|29|21 /8|3897 (20.17%)|0|
| ZL3b |19332 /3773|43|27|21 /6|3716 (19.22%)|0|

All unused offered entries were removed and every word checked again with the
reduced table. Removing entries preserves suffix freedom; observed coverage
and unique re-encoding are explicitly verified. Used-entry counts are witness
sizes, not minima and not a recovered source alphabet. Compound activity is
substantial within this narrow formal sense; it is not phonetic plausibility.

InitialH-run histograms (length:groupcount):
- IT2a:0:22522,2:4,4:2.
- RF1b:0:19317,2:3,4:1.
- ZL3b:0:19330,2:2.

The rare endpoint forms remain included. No recurrent-only filter or supposed
transcription correction was used to obtain coverage. No GE2experiment was
rerun; GDT1353already established i as not forced on those sensitivity panels.

## Concrete structural examples

These fixed illustration forms were nominated before the coverage run. Counts
refer only to the unchanged strict internal P-group panel, not manuscript-wide
word profiles. No meaning or sound is assigned to a complete word or a block.

| Whole form | IT2a parse | RF1b/ZL3b parse |
|---|---|---|
| daldy |d \| a \| l \| d \| y|d \| a \| l \| d \| y|
| daiin |d \| ai \| in|d \| a \| ii \| n|
| aiin |ai \| in|a \| ii \| n|
| iir |ii \| r|ii \| r|
| qokaiii |q \| o \| k \| ai \| ii|q \| o \| k \| ai \| ii|

Standalone in and iiin are attested only in the IT2a strict panel here; they
parse as in and ii|in there. They are explicitly marked absent for RF/ZL, not
invented as witnesses. All example counts and first source IDs are in RESULT.
Bars mark the candidate code boundaries, not observed ink gaps or established
linguistic divisions. In particular daldy's repeated d remains unchanged; this
code supplies no interpretation of that repetition.

For ZL3b, the entire used table is especially compact to state: all21non-i
singletons plus the six pairs ai,ii,ki,oi,ri,si. The actual source values of all
27entries remain unassigned. Within this candidate table the sequence of code entries is recoverable
exactly, while its interpretation remains unknown.

## What is now exact, and what is not

GDT1353proved forced sets and supplied separate countercodes for every remaining
sign excepti. The present code supplies precisely the missing counterexample.
The exact FULL singleton membership intersections are:

- IT2a forced: a,ch,ckh,cth,d,e,f,k,l,m,o,p,r,s,sh,t,y;
  not forced: cfh,cph,i,n,q.
- RF1b forced: a,ch,ckh,cth,d,e,f,k,l,m,n,o,p,r,s,sh,t,y;
  not forced: cfh,cph,i,q.
- ZL3b forced: a,ch,ckh,cth,d,e,f,k,l,o,p,r,s,sh,t,y;
  not forced: cfh,cph,i,m,n,q.

The ITcountercode really omits i ANDn jointly. That one positive joint example
is explicitly checked. It does not establish a single table omitting every
nonforced sign. Other optional signs keep their different GDT1353countercodes.
RF/ZLtables here include n. No cross-reader vote or pooled source was used.

Exactness concerns which singleton entries every admissible code must contain.
It is not a complete list of admissible whole codebooks or their possible
segmentations. A forced singleton may still occur inside another code together
with unforced units. No source letters, phonemes, syllables, words or meanings
are selected. An actual statistical/historical writer would still need to
explain source values, grammar, distribution and context.

## Prior decisions and research consequence

The old GDT1353registered outcome remains PARTIAL on FULL under its original
quotient/edge-absence procedure. This is a distinct residue/pair construction,
not another iteration or retroactive pass of that procedure. The existing
mandatory singleton proofs and their rare-form qualifications stay unchanged.
The old<=22entry exclusion is not challenged by these27–31entry examples.
No minimum-size claim follows from the ZLtable matching an unrelated27prefix
bound. Different code classes have different minima.

This constructive boundary result does not rescue the old fixed-language/source
failures. In particular k,e,s remain singleton codes, so the old keeees repeated-
entry obstruction remains. GDT1351's representation issue and1352's unresolved
physical alphabet are also unchanged. Formal alternative segmentation cannot
by itself distinguish phonetic from nonphonetic content.

The concrete unresolved-singleton question is closed; repeating that census or
trying larger moduli is unnecessary. Future phonetic work can retain these
explicit segmentations as hypotheses, but must test a distinct source/writing
consequence and preserve the existing exclusions. No decoder/key search or
historical source preference is selected automatically here.

## Validation and reproduction

Source is unchanged GDT1233 GROUPS.json.gz with definite outer spaces, pure
working-unit strings and P prose. No new image, raw TSV, f84/f84r, f116v/f1rbody,
reserve, external corpus or lexical assignment. Protocol, source and scripts
were hash-locked before full coverage. Source-free controls and prospective
peer review preceded the outcome.

The independent validator imports no runner. It uses forward dynamic programming
rather than the backward parser, checks offered and reduced suffix-free tables,
Sardinas-Patterson uniqueness, all61,181source rows and23,726whole-type parse
checks, re-encoding, uses/activity, fixed examples and prior-forced inclusion.
It also checks19,680source-free words of lengths1..8, including failed odd-start
cases. Computational validation does not establish palaeography or sound values.
