# KART001 A-65 system comparator method

Status: `STAGE_A_EXTERNAL_COMPARATOR_FROZEN`

Branch: `yolo/gdt002-visual-grammar-constraints`

Date frozen: 2026-08-14

## Question and ceiling

KART001 asks whether the already inventoried Voynich astronomical/circle
structures are unusually compatible with the architecture attested by Tbilisi,
Korneli Kekelidze Georgian National Centre of Manuscripts, MS A-65 and the Old
Georgian tract *Eṭlta da šwdta mnatobtatws*, relative to ordinary medieval
astronomical and computistical systems.

This is a system comparison, not a Georgian, Kartvelian, Mingrelian, phonetic,
lexical, numerical, or translation hypothesis. No Voynich string may receive a
sound, letter, word, morpheme, part of speech, zodiac name, number, or meaning.

## Two-stage firewall

Stage A freezes the external A-65 claims, generic comparators, eligible feature
parameters, source URLs, and prevalence judgements before any KART001 Voynich
score is computed. `kart001_a65_comparator_manifest.tsv`,
`kart001_generic_medieval_comparators.tsv`, and
`kart001_source_provenance.json` are the source freeze.

Stage B may then reconstruct only existing source-native or human-inventoried
Voynich structures. It must not open or use f84r. ZL3b, IT2a, and RF1b remain
alternate observations of one manuscript.

## Frozen A-65 feature treatment

- A65_F01--F06 and A65_F08 are supported as stated in the manifest.
- A65_F07 is supported only for the ten unambiguous sign-specific degree sets
  frozen in the manifest. Cancer is excluded because the electronic edition
  preserves an ambiguous abbreviated numeral sequence; Capricorn is excluded
  because no fortunate-degree list is stated there.
- A65_F09 and A65_F10 are unsupported and excluded.
- A65_F06 is a manuscript-presentation fact from the edition note: odd-numbered
  lunar-night text is red and even-numbered text is black. It is not assumed to
  encode the same binary property as any Voynich visual alternation.

## Generic-medieval control universe

The cardinality null is not sampled from arbitrary integers. Before target
scoring, KART001 freezes the distinct cardinalities

`{3,4,7,8,10,12,16,19,27,28,29,30,36}`

attested by the comparator sources and the existing computus audit. KART001-T1
compares the fixed A-65 set `{7,12,28,30}` with every equally sized
four-cardinality subset of that 13-value universe. Its local tail is the
inclusive fraction of the 715 sets whose target-inventory score equals or
exceeds A-65. The reported search-adjusted value additionally pays for the
number of KART001 test families that actually return a numerical p-value.

The generic table classifies each A-65 feature as `COMMON_MEDIEVAL`,
`REGIONALLY_ENRICHED`, `POSSIBLY_A65_SPECIFIC`, or `UNKNOWN`. Absence from this
small source audit is never treated as evidence of rarity.

## Predeclared Stage-B tests

### KART001-T1: cardinality profile

Use the complete 45-array/504-slot text-blind special-circle inventory. Score a
four-cardinality set by (1) distinct external cardinalities present among the
array sizes and (2) the number of arrays hit, reporting both. The primary tail
uses distinct-cardinality coverage, with array-hit count as a tie-break. Report
raw, inclusive-null, and family-adjusted values.

### KART001-T2: ordered 28 plus binary alternation

Compare only the structural tuple `ordered 28-cycle + exact two-state
alternation`. Do not identify LONG/SHORT with odd/even or red/black. Quantify
compatibility, but report cultural specificity as `UNKNOWN` unless the frozen
generic sources provide an adequate prevalence denominator.

### KART001-T3: externally predicted f69v lag 14

Because the A-65 odd/even presentation gives nights `n` and `n+14` the same
state, compare opposite f69v positions without selecting a representation.
Use all three alternate readings separately for exact surface, character
2/3-gram Jaccard, source-native STA-family sequence, and any already validated
root representation with complete coverage. Rank lag 14 among all circular
lags 1--14 and use a ring-order permutation or exact all-lag tail as applicable.
A weak or bottom-ranked lag 14 counts against direct table transfer.

### KART001-T4: 30-position zodiac organization

Only rotation/reflection-invariant tests are eligible. Seven incompatible panel
topologies and the absence of an authorial common phase force
`UNSCORED_NO_IDENTIFIABLE_30_POSITION_PHASE` unless an existing frozen
inventory already contains a topology-independent 3-by-10 state.

### KART001-T5: sign-specific fortunate degrees

Only the ten source-clear A-65 sets may be used. Convert each to a cyclic gap
signature. Compare only with pre-existing, independently frozen Voynich visual
binary/subset states assigned to the corresponding human-catalogued sign.
Search over rotation and reflection and pay a manuscript-wide maxT correction
over signs and all eligible visual-state families. A failed-capacity state is
ineligible for ownership but may be used as a visual subset only when its
frozen inventory is complete. No new visual feature may be selected for fit.

### KART001-T6: seven-member architecture

Inventory seven-member arrays, but do not score `7 == 7` alone. Test for a
shared internal formal architecture using source-native structures. Preserve
the existing negative Mingrelian weekday observation and assign no weekday or
planet meaning.

### KART001-T7: fourfold architecture

Run only if the external freeze supplies a specific A-65 fourfold opposition
that predicts one of the three possible f67v2 pairings. Generic sign elements
or directions alone are insufficient. Otherwise return
`UNSCORED_NO_SPECIFIC_A65_FOURFOLD_PREDICTION`.

## Scoring and multiplicity

Every scored positive reports `LOCAL_P` and `SEARCH_ADJUSTED_P`. The adjusted
search includes all exercised array, feature, sign, rotation, reflection,
visual-family, and representation choices. Exact permutations or exhaustive
finite orbits are preferred. A numerical familywise adjustment also covers all
KART001 tests that yield a numerical local p-value.

The summary has two separate axes:

1. `SYSTEM_COMPATIBILITY`: how much of the frozen A-65 profile is structurally
   compatible with eligible Voynich observations.
2. `CULTURAL_SPECIFICITY`: whether the same package is better explained by
   A-65 than by generic Latin, Byzantine, Arabic, Persian, or broader medieval
   astronomical practice.

Compatibility without specificity cannot support a Georgian origin or source.

## Required falsifiers

The report must retain: no Georgian or Mingrelian language identification; no
phonetic, number-word, `q`, or `dy` interpretation; the negative weekday and
direction-morphology observations; rejection of the modern Mingrelian
`-tuta` month-name analogy; F69LS001's nonconfirming text result; a poor lag-14
result if observed; and the confounded `19 x 28` Chronikon speculation because
f70v2's 19 band belongs to a 30-position layout.
