# GDT1346 — alternation maximization does not recover the fixed vowel-letter benchmark

**EXACT_ORTHOGRAPHIC_RECOVERY_COUNTEREXAMPLES_ALL_SOURCES.** In each of the four
existing source collections, both predefined AEIOU and AEIOUY partitions admit
strictly improving single-letter flips under the unchanged1264mathematical
objective. Adding c OR h to the reference vowel-letter set improves EVERYcase.
Thus neither reference partition can be a global maximum in these eight tests.
No full optimizer, new source text or native Voynich test was needed.

This is a CONTROL finding about exact spelling-class recovery. It is not proof
that the manuscript is nonphonetic, that native1264classes have no approximate
phonetic resemblance, or that any other phonetic classifier fails. The test
uses spelling labels, not independently annotated historical pronunciation.

|Collection|Original words|Nonletter/non-ASCII excluded|Too short|Eligible interiors|c occurrences|Exact score gain adding c, AEIOU / AEIOUY|
|---|---:|---:|---:|---:|---:|---:|
|b4|19315|495|11762|7058|2295|1230.194877 /1234.353608|
|w1|18141|45|11700|6396|2130|1054.250216 /1060.075613|
|bs1|21963|594|13408|7961|2536|1052.766162 /1058.287807|
|gr1|21512|658|13919|6935|2297|771.389322 /774.462482|

All1054previously retained recipes,80931original source tokens and28350eligible
interiors are accounted for;1792whole tokens fail the ASCII-letter filter and
50789are too short. No punctuation was stripped or source spelling repaired.
These are four known recipe collections, not independent language families or
untouched controls. They are reused from1177before its failed P4word grouping.
Source attribution: CoReMA, University of Graz, CC BY4.0; inherited source
projection and cache hashes are in experiment.json and REGISTRATION_LOCK.json.

## What was fixed and what the certificate proves

The1264objective sums observed cross-class adjacent transitions minus the expected
number for uniformly ordered letters with each interior's exact letter bag.
Equivalently, its signed pair weight is observed adjacency minus2count(a)count(b)/n,
aggregated over interiors. Each aggregate pair weight is rounded at10^-6 using
nearest/ties-to-even before summing a cut. Both exact rational and quantized
changes are retained. Every positive c/h witness is positive under both versions.
These score changes are counts of objective units, not accuracy or significance.

The two reference spelling conventions and all four books were fixed before
scoring. Every active letter was tried as a single membership flip. All192flips,
including decreases and tiny gains, are saved; no best-letter-only filter was
used. A single strict gain suffices to exclude the given partition as an optimum.
This does NOT identify the actual global optimum or prove which letters every
optimum would move. No failure rate for a phonetic detector is inferred.

The control alphabets have24/24/23/25active letters. We reuse the mathematical
objective, not the original22-vertex-limited optimization executable. The
one-flip proof has no need for that executable or an enlarged optimizer. Near
optimality, approximate vowel recovery and out-of-sample phonetic prediction
were not measured and are not declared failed.

## A hand-checkable illustration

The source word machen occurs34/27/97/178times in b4/w1/bs1/gr1. Trimming one
letter at each end gives ache. For the AEIOUreference its class pattern is1001:
2crossings minus expected2, giving0. Adding c gives1101: still2crossings, but the
bag expectation is now1.5, so the score is0.5. Adding h similarly gives1011and0.5.

The criterion can therefore improve even without adding an observed crossing,
because changing the classification changes its reference expectation. This
post-result example explains the arithmetic; it is not a new prediction, a
quantified cause of the entire aggregate gain or a proposed sound value for c/h.
Source/script and original meaning are known independently here, but historical
v/u,i/j,y usage and letter combinations still prevent treating our labels as
phoneme ground truth. No normalization was changed to remove inconvenient cases.

## Consequence for the proposed Voynich sound reading

The fixed1264partition is

    class0: a e l n o p y
    class1: cfh ch ckh cph cth d f i k q r s sh t

These remain statistical labels. Existing1227already records complete singleton
forms a,d,o,r,s,y in every reading. If class0 were ALLwritten vowels, the d/r/s
singletons lack a vowel; if class1 were ALLwritten vowels, a/o/y do. Thus a strict
fully vocalized, one-unit-one-segment, every-group-lexical-word interpretation
fails either orientation. This is a use of old evidence, not a new census or a
ban on syllabic signs, abbreviations, syllabic consonants or vowel omission.

1264/1265structural positives remain valid.1278's original predictive failure and
1279's additional exact-identity information remain unchanged. The present
control does not rescue/reject those estimators or refit native classes. There
is no supported step from extra binary alternation to naming the classes vowels
and consonants. A phonetic interpretation needs a separate, explicitly justified
unit and sound account; favorable sequence statistics alone cannot supply it.

An unrestricted whole-word lookup writer could reproduce identical strings and
thus identical statistics without computing sound classes. This is a logical
identifiability limit, not a claim that the scribe used such a writer or that
historical linguistic evidence could never distinguish the alternatives.

## Verification and closure

Protocol and both programs were hash-locked before source scoring. The separately
written checker reconstructs eligibility from complete original words, computes
per-word class-switch expectations directly, and checks all192exact/quantized
flip differences against the signed-cut implementation.25exhaustive small bag
fixtures and positive/negative rounding ties pass. PASS validates arithmetic and
source accounting, not historical phoneme annotations. The original sources
were already exposed; no independent holdout or blind phonetic recovery claimed.

No Voynich raw TSV, image, new native count, word meaning, f84/f84r/f116v/f1rbody
or reserve was accessed. No missing-input audit or larger control framework is
started. Stop using this objective alone as an exact vowel-letter detector for
these source projections. Do not automatically retune classes, regroup letters,
add new languages or fit a decoder after this outcome. No word is translated.

A separate agent reviewed formula correspondence, source selection, all reported
c/h witnesses and the claim ceiling without rerunning the experiment, finding
no material correction. Reproduction in the publication checkout gives identical
result, accounting, validation and example bytes.
