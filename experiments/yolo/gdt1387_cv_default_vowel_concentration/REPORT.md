# GDT1387 — every surviving CV key forces a majority vowel

**Every key in the unchanged IDEA1053/GDT1383 family assigns more than half
of the decoded vowels to one anonymous vowel V0.** The exact minimum share
ranges from52.13% to59.32% across the six separate reader/head cases. This is
a new numerical obligation of the existing writer, not a language exclusion,
a sound identification or a statistical fit to a source language.

## Six complete bounds

| Reading | Prefix H | Original groups | Decoded vowels | Exact lower bound, rounded | Exact upper bound, rounded | Lower / upper isolated-V0 witness |
|---|---|---:|---:|---:|---:|---|
| IT2a | `cfh` | 22,528 | 102,169 | 53.53% | 60.40% | `cph` / `i` |
| IT2a | `cph` | 22,528 | 101,981 | 58.91% | 62.89% | `cfh` / `q` |
| RF1b | `cfh` | 19,321 | 86,511 | 52.13% | 58.82% | `cph` / `ch` |
| RF1b | `cph` | 19,321 | 86,329 | 57.49% | 61.59% | `cfh` / `q` |
| ZL3b | `cfh` | 19,332 | 89,660 | 53.65% | 60.30% | `cph` / `ch` |
| ZL3b | `cph` | 19,332 | 89,482 | 59.32% | 63.57% | `cfh` / `q` |

Both endpoints are attained by compatible role assignments. Exact fractions,
integer counts, every extremal isolated sign and an attaining vowel triple are
in [RESULT.json](artifacts/RESULT.json). These are bounds over possible keys,
not confidence intervals. Readers are alternate readings of one manuscript,
not independent replications; no pooled average or majority vote is used.

The letters in the witness column name **transcription units**, not actual
vowels. V0 is the unnamed vowel shared by the model's six Ca-style selector
signs. It need not be pronounced /a/. The claim concerns a fraction of all
**vowels**, not a fraction of all phonemes or of written characters.

## Why the entire key space is covered

The fixed writer has18 CV signs,3 isolated-vowel signs and one prefix H.
A pair HF writes a bare consonant. The six F selectors each write a different
consonant followed by the same V0 when used alone. The other12 CV signs never
write V0. This is the old writer, not a newly assumed phonotactic process.

Let N be the weighted number of working units and m the actual number of HF
code occurrences. Every HF consumes two written units and contributes zero
vowels; every singleton contributes exactly one. Therefore:

```text
all decoded vowels V = N - 2m = sum of singleton-code usages
fixed V0 contribution D = sum of the six F singleton-code usages
V0 contribution for isolated sign s = D + singleton_usage(s)
```

GDT1383 permits every three-element subset of its eligible pool. Each eligible
sign can therefore serve as the isolated V0 sign, with two other eligible signs
serving as the other isolated vowels. The smallest and largest such counts
produce exact endpoints. Changing the six consonant names or permuting the
other12 CV entries cannot change V0 or the total vowel count. No enumeration
of trillions of detailed sound tables is required, and no particular table wins.

The identity N-2m was already known. The added result is the optimized V0
concentration interval over the complete surviving role classes. Code usage
counts are inherited, not newly discovered manuscript observations. Prefix
occurrences must not generally be replaced by prefix-containing word counts.

## Scope of the source obligation

The data are the complete occurrence-weighted **GDT1233** eligible population
already counted by GDT1248. GDT1233 is an experiment identifier, not a claim that
only1,233 words were used. Selection keeps P groups internal to physical lines,
with definite spaces on both sides, literal lowercase representations and a
unique parse into the22 working units. All retained rare forms and occurrences
remain. This selection is systematic; representativeness is not assumed.

Consequently a proposed matching source population must have a most frequent
vowel at least as frequent as the applicable lower bound. Because every lower
bound exceeds one half, V0 is its unique most frequent vowel in this model.
This does not say that an entire historical language has the same distribution.
Comparing an unmatched whole-language corpus average would not test this result.
No comparison corpus, transcription, image, new folio or reserved material was
opened. No rhyme, stress, word-final distribution or native pronunciation was
inferred from aggregate counts.

Other obligations remain jointly binding: exactly six source consonants and
three vowels in this writer; very sparse bare consonants in the inherited
panel; the already known internal fourfold identical CV sequence forced by
`keeees`; and preserved source-word identity frequencies. A feature pre-code,
extra phonemes, different word grouping or discarded rare forms would define
a different source/writer contract. None is silently introduced here.

## Decision and reproduction

Retain **EXACT_DEFAULT_VOWEL_BOUNDS**, with forced strict majority in all six
cases. The canonical writer remains structurally possible. Neither a natural
source language nor a constructed language is chosen or rejected by this
calculation. A candidate source contract must address this concentration and
the older obligations together before a sound-table search becomes meaningful.
Do not automatically start a decoder or a source-corpus scan.

Unlike the earlier contemplated6x3 Markov fit, this calculation adds **no
first-order source assumption**. That larger fit was not selected: failure of
an arbitrary added source model would not reject the CV writer itself.

The [method](METHOD.md), [specification](src/SPEC.json) and programs were locked
locally at23:40:48UTC on15October2026 before the first derived concentration
run. The underlying aggregate counts and model were already public/exposed;
no blind registration is claimed. [INPUT_COUNTS.json](artifacts/INPUT_COUNTS.json)
projects only the six relevant old aggregate cases, with original input hashes.

The independent [validator](src/validate.py) imports no primary code. It decodes
all aggregate code occurrences under every retained vowel triple and all six
isolated-vowel label assignments, then checks the extrema and witnesses.
Its4,350 finite assignments verify the arithmetic and source projection; they
are not4,350 independent manuscript observations or sound confirmations.
[Validation PASS](artifacts/VALIDATION.json). The remaining12! freedom is
covered by the fact that those entries never emit V0. No old source was changed.

Reproduce using the two manifest commands. The new source obligation and its
limits are the scientific result; successful accounting is not decipherment.
Confirmed translated words remain0. The user's ten-hour research run continues
beyond this bounded checkpoint; its minimum horizon is08:58:57UTC16October.
