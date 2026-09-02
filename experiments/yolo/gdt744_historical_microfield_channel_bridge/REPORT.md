# GDT744 — historical microfield channel bridge

## Outcome

GDT744 turns part of the inherited generic renderer into explicit historical
record fields without pretending to know the missing substance names.

Across all 202 cached targets, 140 microfields are fully bounded inside radius
five and 62 are censored on at least one side. Sixteen exact-target/channel
templates recur on at least two fully bounded pages with different anchors.
They cover 80 target occurrences: 47 fully bounded F3 cases and 33 censored F2
applications. Combining these field readings with GDT743's 59 target-specific
readings yields 95 context-specific occurrences, 36 more than before.

This is not a translation. Confirmed lexemes and plaintext clauses remain zero.

## What the renderer can now say

The 80 template-backed fields divide into:

| field channel | occurrences |
|---|---:|
| descriptive materia | 40 |
| descriptive quality | 17 |
| prescriptive recipe/process field | 11 |
| prescriptive process field | 3 |
| quantity or part field | 9 |

Examples now distinguish materially different structures:

- `lkaiin` at `f105v.37` is a processing/recipe field for a moist preparation,
  with the ingredient still open and target passage level III retained.
- `sain` at `f113r.49` is a hot/dry preparation-description entry at level II,
  with the visible content surface left as an unidentified lemma candidate.
- `sain` at `f106v.19` is a quantity/material field at level II, with the
  referenced substance still open.

Seven licensed occurrences contain hot/cold or dry/moist competition. The
renderer states that collision instead of merging it into one quality.

## The target wholes are probably fields, not drug names

Four exact targets recur in several fully demonstrated channel templates:

- `lkaiin`: descriptive materia, descriptive quality and prescriptive
  recipe/process;
- `lkain`: descriptive materia, prescriptive recipe, prescriptive process and
  quantity/part;
- `lkar`: descriptive materia, descriptive quality and quantity/part;
- `sain`: descriptive materia, descriptive quality and quantity/part.

The best current working interpretation is therefore that these wholes supply
reusable level/state or entry fields whose dimension comes from the surrounding
record. Treating them as single substance names would have to explain the same
surface moving through several coherent record channels. This is an
architecture inference, not a recovered lexeme.

## Manual passage result

The 20-example reader contains all sixteen complete templates, one censored
template application, two window-only countercases and one open countercase.
The manual audit marks 17 as practically informative at field level. The three
remaining cases intentionally receive no licence: two are window-only and one
is open. The audit also exposed and repaired the initial omission of `PASS`
from the process channel.

The new cards avoid the retired universal prose pattern “take work item, carry
out work step, continue cycle.” They say which kind of record field is present,
which qualities/carriers are actually anchored, what level the target supplies,
and exactly which content role is still unknown.

## Where concrete words must now live

Within the 80 template-backed fields, 42 exact-reader unknown cells are
plausible unresolved content slots. They represent 41 distinct surfaces in 28
fields. None repeats across two pages inside this restricted 202-window deck;
therefore none can yet be called water, wine, salt, root, leaf, a plant name or
an ingredient.

That result localizes the problem rather than hiding it. The level/state target
is usually not where the concrete noun should be sought. The concrete noun
should be sought among these learned whole/name or ingredient candidates.

## Sensitivities

- W3-only anchors retain a template-backed reading at 69/80 occurrences and
  retain the same channel at 67/80.
- Restricting evidence to radius two preserves the raw channel at 172/202.
- Removing field boundaries preserves it at only 152/202, showing why a naked
  ±5 window over-imports neighboring records.
- Two inherited W3 wholes lacked GDT739 axis tags. The explicit whole-role
  supplement changes one in-bound occurrence (`olor`) to an ambiguous
  material/ingredient field. `qoly` remains beyond a close boundary and has no
  effect.

## Relation readiness

The GDT388-compatible packet is deliberately ineligible. The executable
checker reports `INVALID_PACKET`: formal content was accessed, and capacity,
held-folio and mobile-null gates are all closed. No score-ready visual relation
claim is made.

## Next route

Use the 41 unresolved exact content surfaces as a candidate deck and locate all
of their already cached exact occurrences outside the 202 windows. For each
whole, compare descriptive, prescriptive, quantity and open contexts using the
GDT744 templates. Cross-page role persistence can then distinguish learned
lemma/name candidates from ingredient or process complements. Preserve whole
identity; do not infer meanings from EVA substrings.

This is the shortest current path from field grammar to concrete candidates:

`recurrent field channel → exact open content slot → cached cross-page contexts
→ historical learned-name/ingredient comparison`.

## Reproduction

```bash
python3 experiments/yolo/gdt744_historical_microfield_channel_bridge/src/run.py
python3 experiments/yolo/gdt744_historical_microfield_channel_bridge/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt744_historical_microfield_channel_bridge/artifacts/GDT744_GDT388_MICROFIELD_EDGE_PACKET.tsv
```

The independent validator passes 2,919 checks and a byte-identical builder
replay.
