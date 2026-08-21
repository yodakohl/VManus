# V16 selection — complete default-meaning working translation

Date: 2026-08-21

Status: **selected maximally abductive sidequest basis**, not a decipherment
claim or canonical GDT result.

## Decision

V16 imposed a new hard rule: uncertainty may lower confidence, but it may no
longer replace meaning. Four independent historical scribal perspectives each
assigned a concrete default to every visible group on the ten fixed pages.

| candidate | coverage | score / 100 | disposition |
|---|---:|---:|---|
| R1 workshop master | 776/776 | 94 | supplies the teaching grammar and construction inventory |
| R2 medical/Herbal scribe | 776/776 | 93 | supplies the strongest medical and historical expansions |
| R3 technical-register writer | 776/776 | 95 | supplies the cleanest executable register and water/bath workflow |
| R4 chancery corrector | 776/776 | **97** | **selected complete default dictionary and event reading** |

R4 wins because it combines a normal historical source layer with the exact
card mechanism: strongly abbreviated iatromedical professional prose is
compressed into whole-card brevigraphs, picture-supplied arguments and local
rubrics. It handles carry, dittography, line reflow and local closure without
turning the whole page into a rigid modern table. R1's four-table apprentice
workflow and R3's explicit working-memory decoder are incorporated as the
preferred explanation of how a small workshop learned and reproduced it.

The selected machine-readable basis is therefore:

- `V16_R4_COMPLETE_DEFAULT_LEXICON.tsv` — canonical current default dictionary;
- `V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv` — canonical 776-group reading;
- `V16_R4_FLUENT_LINE_READINGS.tsv` — canonical 199-locus sequence reading;
- `V16_R1_COMPLETE_CONSTRUCTION_READINGS.tsv` — secondary field/record
  construction audit, retained where it agrees with the selected dictionary.

## Current concrete dictionary

| card or formula | selected default meaning | confidence |
|---|---|---:|
| `qokaiin` | **take up the next entry / portion** | .68 |
| `L/O` | **with it; likewise under the same rubric** | .59 |
| `AIIN` | **in the stated or usual measure** | .48 |
| `Y` | **this share / present portion** | .43 |
| `CTHY` | **when prepared and ready** | .38 |
| `Y–AIIN–Y` | **both portions by the same stated standard** | .44 |
| `VAL-S` | **set it ready and close the instruction** | .34 |
| `VAL-QE` | **use the tempered warm medium and close** | .31 |
| `VAL-Q` | **retain the ordinary base setting and close** | .30 |
| `VAL-L` | **pour or rinse at the local place and close** | .27 |
| recurrent `OKEEY/QOKEEY` card | **warm it gently** | .39 |
| recurrent `CKHY` card | **through the connected channels** | .26 |

`OKEEY/QOKEEY = warm gently` is preferred over R2's `mix thoroughly` because
R1 and R3 independently chose the heat reading and it yields the simpler
recurrent bath workflow. Both remain speculative; the rejected concrete rival
is recorded rather than replaced by an empty structural label.

## Complete page reading

The present ten-page book reads as:

```text
f10r/f11r/f55v/f56r:
  pictured medicinal simples; names, parts, habitat/quality, preparation,
  measure, storage and use in strongly abbreviated article prose.

f81v/f82r/f83r:
  pictured baths, conduits or body applications; water, warm medium, measured
  portions, immersion, pouring, rinsing, settling, outlets and local closure.

f67r2:
  seven rulers + twelve zodiac divisions + twelve house functions + a local
  election/application rule.

f68r1:
  Moon-owned spatial catalogue with one centre and 28 locally addressed lunar
  stations; no invented authorial cycle start.

f69v:
  28-position lunar-election lookup, provisionally alternating perform/avoid
  instructions and followed by a circular use rule.
```

Every rare card keeps the concrete phrase recorded in the selected lexicon.
A `CONTEXT_DEFAULT` label describes its evidential basis, not its meaning: the
English gloss itself is always nonempty and concrete. Future iterations may
replace a weak assignment only with a better concrete assignment that improves
all of its occurrences.

## What changed

Before V16 the theory could stop at `PAYLOAD`, `VALUE`, `STATE` or an anonymous
card. After V16 those are no longer admissible terminal readings. The working
theory now contains:

- 381/381 concrete prose-event meanings;
- 173/173 exact prose-card defaults;
- 395/395 concrete ZL3b Astro-group meanings;
- 776/776 total visible-group readings;
- no semantic blank or neutral fallback;
- a fluent sequence reading for every one of the 199 physical loci;
- a construction reading for 288 fields, records or diagram labels in R1's
  independent audit.

This completeness does not make all assignments equally credible. It makes
the theory useful: every future contradiction now has a specific word or
construction to repair.

## Seal

Only the ten authorized pages and page-guarded f84-free formal sources were
used. `f84` and `f84r` remained sealed.
