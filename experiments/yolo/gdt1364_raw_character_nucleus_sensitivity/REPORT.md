# GDT1364 — The recurrent nucleus bound changes from nine to eight

**RAW_CHARACTER_NUCLEUS_SENSITIVITY.** Splitting the exact same transcription
strings into individual raw characters lowers the minimum whole-word hitting
size. On every recurrent-form panel it is8, whereas the original22working-unit
analysis gives9. Thus the recurrent<=8carrier exclusion is not invariant under
this fixed refinement. This does not identify actual vowels, glyph boundaries,
phonemes or a consonantal script.

## Same words, two representations

Original units include ch,sh,ckh,cth,cph,cfh as individual tokens. RAW_CHARuses
their literal constituent characters without changing any word, occurrence,
space or reader. Each FULL raw alphabet has18characters:
a,c,d,e,f,h,i,k,l,m,n,o,p,q,r,s,t,y. This is a transcription convention, not a
new paleographic determination. We neither delete rare words nor call the
raw-character split the true alphabet.

| Reading / panel | Groups / types | Old22unit minimum | RAW_CHAR minimum |
|---|---:|---:|---:|
| IT2a FULL |22528 /4272|13|11|
| RF1b FULL |19321 /3818|14|13|
| ZL3b FULL |19332 /3773|11|10|
| IT2a GE2 |19687 /1466|9|8|
| RF1b GE2 |16786 /1315|9|8|
| ZL3b GE2 |16865 /1337|9|8|

GE2retains wholeforms on at least two physical leaves. Its lower bound does not
replace FULL, establish that rare forms are errors, or create a holdout. In
particular FULL still requires10–13representatives in this raw representation;
eight does NOTcover every retained FULL group.

The canonical minimum GE2hitting set is a,c,d,l,o,r,s,y for each reader. This is
only a mathematical witness of coverage, not an assignment of vowel values or
independent agreement on a historical alphabet. The readings describe one
manuscript. A set may hit a word at an ordinary consonant or at a transcription
component that is not an independently written code at all.

## Exception costs also depend on representation

Below are RAW_CHARminimum missed WHOLEGROUP occurrences; the paired type
objectives and complete canonical witness lists are retained in RESULT.

| Panel | K3 | K5 | K7 | K8 |
|---|---:|---:|---:|---:|
| IT2a FULL |633|156|20|5|
| RF1b FULL |687|169|25|13|
| ZL3b FULL |493|117|14|3|
| IT2a GE2 |501|124|9|0|
| RF1b GE2 |561|127|10|0|
| ZL3b GE2 |396|90|7|0|

ForK5the FULL lowerbounds are0.605–0.875%of occurrences, below the original
0.921–1.299%. These remain optimistic necessary lowerbounds, not actual vowel
omission or sufficient spelling repairs. Occurrence and type minima are
separate optimizations; the report does not combine their best witnesses.

ForK7onGE2the canonical occurrence witness misses exact d9times in IT and7times
in ZL; RFmisses d8times and deiin2times. This post-result illustration does not
assign abbreviations, consonants, errors or any meaning to those words. Their
complete locations and physical-leaf support remain in the result artifact.

## Why refinement can only relax the bound

For each selected old representative unit choose one character from its raw
spelling. A word containing the old unit necessarily contains that character.
Thus≤Knewrepresentatives preserve all oldhits, so both minimum hitting size and
minimum misses cannot increase. Different old units can share a character;
the source-free example with atomic bc andbd needs two representatives, while
character splitting lets b hit both. No linguistic inference enters this proof.

The1042carrier lemma remains valid if its carriers are now complete nonempty
RAW_CHARstrings aligned to these character boundaries. It still does not cover
codes beginning inside a character, fusion that changes the output string, or
arbitrary physical strokes. The test establishes sensitivity between TWOdefined
representations, not a minimum over all plausible script analyses.

## Research decision

Preserve1355,1363and1042with their original22unit assumptions. Do not state that
at least9written nucleus forms are required for recurrent words independently
of segmentation. Eight remains possible at the necessary raw-character coverage
level; this is not a successful eight-vowel writer or a reason to prefer a
language. Five/seven still fail zero-exception coverage in both representations,
but small necessary exception counts and unbound wholeword/nucleus assumptions
continue to prevent broad language exclusions.

The full-data≤8zero-exception obstruction survives these two representations,
with materially rare-sensitive bounds. Neither result distinguishes an abjad
from an alphabet. Fixed-source Hebrew and other older failures retain their
actual contracts. No new source fitting, vowel map or decoder is selected.

## Reproduction and validation

Protocol, both programs, independent proof review and inputs were locked at
03:07:02UTC on13October before native enumeration. Primary adapts1363's
subset-zeta engine to raw-character supports; the independent validator adapts
its own recursive bitset engine, without reading/importing the primary. Its381
weighted fixtures and four refinement controls passed before scoring.

Independent validation reproduces six exact hitting minima/canonical witnesses,
all48K/objective optima, crosscounts, full missed-form/frequency/first-ID/leaf
lists and monotonicity relative to1355/1363:PASS. It verifies source accounting
and combinatorics, not real phonology or physical glyph decomposition.

Only unchanged1233strict cached Pgroups and631allowlist are used. Same readers,
wholeforms and panel denominators; no rawTSV,newimage,sourcecorpus,websource,
f84/f84r/f116v/f1rbody,reserve or semantic relation score. Zero sound/word meanings.
