# GDT1196 — six cheap vowel-boundary rules fail necessary frequency bounds

Scientific decision: **ALL_SIX_CHEAP_GROUPING_RULES_EXCLUDED**. Independent validation: **PASS**. These are different conclusions: the counting and bounds validate a negative construction result. No glyph writer or native reading was produced.

## Question and fixed contract

Can a source writer avoid GDT1193's 2,130-entry fragment dictionary by cutting ordinary words at vowel runs and remembering only the previous fragment's final character class? The registered test examines necessary capacity before choosing or fitting any Voynich working signs. See [preregistration](PREREGISTRATION.md) and [bound proof](METHOD.md).

Two source segmentations are fixed: AFTER cuts after each maximal `aeiou` run except the last; BEFORE cuts before each run except the first. Only lowercase a–z words are split. Other words, and words with at most one vowel run, stay whole. These are orthographic chunks, not a claim about syllables. For example, `schreiben` becomes `schrei|ben` or `schreib|en`. Every group explicitly carries source-word-end E or continuation C.

Each arm has three entry-state rules: NONE; VC, previous fragment ends in a vowel or other character; V6, previous fragment ends in a/e/i/o/u or other character. Recipe start is other. State is constant within a printed group and updates after every decoded fragment; word spaces do not update it. No counter, learned fragment dictionary, or other writing state is allowed. A complete group is a deterministic function of its literal source fragment, E/C flag and declared entry state.

The four previously exposed CoReMA source projections and cached GDT1174 target summaries are unchanged. Each book contributes its first 8,000 source fragments. All 1,054 recipes and 80,931 source words are processed for reconstruction. No new native transcription, image, source acquisition, reserve or word assignment was used. f84/f84r remain sealed and f116v remains unadmitted. The three target readings are alternate readings of one manuscript.

## Why the test can exclude an alphabet before constructing it

One complete source label always has one spelling under this contract. Several labels may share a spelling; allowing that is an optimistic relaxation. Such merging can only reduce distinct forms and increase or preserve the share occupied by the ten most frequent forms. Thus label counts give an upper bound on output diversity and a lower bound on top-ten concentration, regardless of glyph choices.

The inherited all-reader necessary limits are at least **2,130 distinct forms per 8,000 groups**, and a top-ten share of at most **17.6%**. Both are the original tolerance limits, not exact target values or newly tightened criteria. Too many label types or too little concentration are deliberately not grounds for rejection: collisions could change those in the required direction. Passing these relaxed bounds would only mean not excluded.

## Exact outcome

Each table cell is **maximum distinct forms / minimum top-ten percentage**. Every cell fails both necessary directions.

| Split and state | b4 | w1 | bs1 | gr1 |
|---|---:|---:|---:|---:|
| AFTER / NONE | 941 / 25.3250% | 1,033 / 23.9250% | 899 / 23.6250% | 1,037 / 26.5375% |
| AFTER / VC | 1,112 / 23.0250% | 1,251 / 21.8000% | 1,091 / 21.6750% | 1,191 / 25.4250% |
| AFTER / V6 | 1,276 / 23.0250% | 1,447 / 21.8000% | 1,270 / 21.6750% | 1,320 / 25.3375% |
| BEFORE / NONE | 977 / 32.3500% | 1,093 / 30.3625% | 916 / 31.5250% | 1,071 / 33.4250% |
| BEFORE / VC | 1,140 / 30.8625% | 1,291 / 29.1875% | 1,103 / 29.9625% | 1,197 / 32.6125% |
| BEFORE / V6 | 1,194 / 30.8625% | 1,354 / 29.1875% | 1,168 / 29.9625% | 1,219 / 32.6125% |

The maximum diversity across these cases is 1,447, still below 2,130; the lowest concentration is 21.675%, still above 17.6%. No deterministic glyph table with exactly these source/group/state contracts can repair this. This is a necessary obstruction, not an unsuccessful alphabet search. No alphabet optimization ran.

## Alias relaxation: a bound, not a new writer

The preregistered auxiliary calculation allows each base `(fragment,E/C)` up to A hypothetical spellings, for A=1 through 16. A base occurring n times can provide at most min(n,A) types. Its most even integer split minimizes every pooled top-k sum; cross-base collisions cannot improve either necessary bound. This assumes freedom that a public writing rule might not implement.

Both segmentations first clear the two relaxed directions jointly at **A=5**. At A=4 the limiting bs1 type counts are 2,109 (AFTER) and 2,094 (BEFORE), below 2,130. At A=5 all four type upper bounds and concentration lower bounds clear the necessary directions. This does not show a five-state writer exists, that every fragment needs five forms, or that full type/concentration ranges and other statistics can jointly pass. It supplies no encoding, decoding, state-selection or glyph rule.

The actual V6 rules fail despite having six nominal states. A count of available states alone is insufficient: source occurrences do not distribute freely among them. Do not turn the A=5 relaxation into an automatic counter or another fitted table.

## Validation and correction

The independent validator does not import the runner. It identifies vowel runs with character transitions instead of regex, independently reconstructs source words and checks all 24 rule/book counts and their exact frequency digests. It checks 128 alias/book counts using occurrence-by-occurrence round-robin allocation instead of the quotient formula. A separate exhaustive set of 2,679 small pooled-partition fixtures verifies the top-k bound. The two segmentations reconstruct each complete source recipe, giving 2,108 grouping reconstructions. These are not glyph inverses or native-language tests.

The initial invocation stopped before producing any census because the start-state guard tested membership of None too early. [CORRECTION.md](CORRECTION.md), the original runner and the original lock preserve that engineering correction. No rule, data, criterion or result selection changed. The corrected source and dependencies were locked before the successful run. [RESULT.json](artifacts/RESULT.json) and [VALIDATION.json](artifacts/VALIDATION.json) contain the machine-readable results.

Reproduce from the repository root:

```sh
python3 experiments/yolo/gdt1196_vowel_boundary_capacity/src/run.py
python3 experiments/yolo/gdt1196_vowel_boundary_capacity/src/validate.py
```

## Dependencies, limits and decision

The raw IDEA000937 supplied AFTER segmentation; its illustrative carrier is not adopted. That carrier lacks final y and does not implement the near-obligatory qo behavior already known from the target summaries. GDT1180 used contextual source alphabets with updates within whole printed source words; its failure remains separate. GDT892's capacity stop, GDT906's fixed Latin/CV failure, and GDT907/910's lack of generic continuation support remain unchanged. These predecessors do not license native syllable identities or hidden hyphenation. No old report's example meanings are reused.

GDT1193 remains a working artificial basic-screen control with an expensive dictionary and known q/y/entropy mismatches. GDT1194/1195 remain failed stronger constructions. This result closes the six exact cheap grouping/state families on the four exposed source controls; it does not exclude all vowel-based writing, medieval systems, other source languages, or meaningful Voynich text. No translated native words have been added.

Do not fit a carrier or rerun these unchanged six rules. A subsequent candidate must specify a genuinely different, human-executable rule for distributing information among visible groups, with explicit learning/state costs and the known native word-form constraints. Review primary predecessors before selection. Mere extra states, favorable theoretical alias capacity, or another random fit are insufficient. No next candidate is selected here. Total registered work block 09:37–10:00 UTC includes local closure; no automatic extension. Local construction checkpoint under the current-route exception; no commit or push.
