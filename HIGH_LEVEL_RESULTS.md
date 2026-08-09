# Voynich investigation: high-level results

Updated: 2026-08-09

## Bottom line

The Voynich manuscript is **not translated**. We have no confirmed English
word, plaintext sentence, language identification, phonetic alphabet, cipher,
part-of-speech system, or subject/verb/object order.

What we do have is a substantially better structural description. The text is
not well modelled as random glyph strings or as a list of unrelated codewords.
It behaves like a compositional, page-conditioned, line-reset construction
system whose physical lines often act as record-like units.

## Strongest positive findings

1. **Spaces carry structure.** Some are mandatory inside exact constructions;
   others separate detachable completions. They are real hierarchical
   boundaries, although they need not be ordinary European word boundaries.
2. **Forms are compositional.** Reusable roots combine with recurrent bound,
   free, relational, and state-like operations. Structural tags describe these
   formal roles; they are not translations.
3. **Physical lines matter.** A content/order coordinate rises within a line
   and resets at the next line. Bare `t` is associated with editor-marked
   paragraph openings, while bare `d` and `s` favour marked continuations.
   These are formal entry states, not the words START or CONTINUE.
4. **Directional dependencies exist.** Several exact D-to-q and E-to-q
   constructions consistently run from a relatively context/function-like
   element toward a relatively identifier/value-like dependent. This does not
   establish verbs, nouns, or SVO order.
5. **Root choice is structured beyond page vocabulary.** Adjacent root
   identities remain non-exchangeable after fixing page inventory, form shell,
   position, entry state, and dependency locations. The aggregate relation
   transfers across Currier, section, and hand boundaries.
6. **A cross-Currier directional component is real.** Direction-specific
   partner information survives unordered-pair and root-side controls. A fixed
   Timm local self-citation generator failed to reproduce it. This rejects that
   one generator as sufficient; it does not prove ordinary language.
7. **Some diagram text is record-segmented.** In a frozen panel of repeated
   graphical arrays, between-slot transitions are much more line-boundary-like
   than matched internal spaces. This confirms aggregate slot records, not the
   meaning or ownership of individual labels.
8. **The analysis covers the manuscript.** The current structural artifact
   covers 38,988 manually transcribed tokens and 5,376 loci across the three
   alternate ZL3b, IT2a, and RF1b readings, while deliberately assigning zero
   English lexical glosses.

## Important negative findings

- Repeated words, stems, labels, plant relations, bathing imagery, zodiac
  mappings, proposed numbers, historical-herbal orders, and known-language
  comparisons have not yielded a transferable meaning.
- Exact repetition shows at most a weak preference for the same broad editorial
  text kind; it is not a stable object or lexical key.
- Neural image recognition and OCR are excluded from evidence because repeated
  controls showed them to be too brittle for this task. The active work uses
  manual transcriptions and provenance-traceable human descriptions only.
- A broad historical prior remains compatible with an astrological-medical
  compendium containing herbal, bathing, astronomical, pharmaceutical, and
  recipe-like modules. No particular source manuscript has been identified.
- A clean human-annotated Herbal contrast found no recurrent text pattern that
  reliably separates eight explicitly berry-bearing drawings from seven
  explicitly fruitless/flowerless drawings. The sole near-miss, root prefix
  `oii`, misses both frozen familywise gates and is not a berry or negation
  translation.

## Latest provisional cross-page lead

The six labels between successive openings of the f77r top tube reproduce the
previously fixed f57 two-bit page-role states as COLD, DRY, HOT, HOT, MOIST,
COLD in all three manual readings. Every boundary where the state changes is
drawn emitting material; the sole unchanged HOT-HOT boundary is the sole
non-emitter. The four changes are exactly the four classical primary-quality
pairs traditionally defining Earth, Fire, Air, and Water.

This is the strongest current semantic-structure lead because it predicts an
author-visible relation across pages. It remains post-hoc and is **not a word
translation**. A later human proposal for the visual puff identities disagrees
at all four positions, and a second independently annotated segmented system
must reproduce the rule before any quality, element, `ot`, or terminal-`y`
meaning can be claimed.

Removing the two features that created those states does **not** reveal a
four-item quality vocabulary. The expected same-state spelling assignment is
only fourth of 24 possibilities, and deleting the strongest single resemblance
drops it to eighteenth. The bridge is therefore structural, not a translated
HOT/MOIST/COLD/DRY lexicon.

An exhaustive source-only audit of the current human annotation layer found
eleven broad apparatus/water label units, but f77r is the only one with a label
between every successive boundary and a documented mix of active and inactive
openings. There is therefore no second local panel capable of confirming the
pattern without new independent human evidence.

## Latest source-calibration result

We tested whether a semantic similarity representation could recover the known
mapping between two complete human descriptions of the twelve astrological
houses before applying anything comparable to Voynich text.

The final method used exact rational preprocessing, complete `12!` assignment
enumeration, and all twelve true ring-rebuilt `11!` record-deletion tests. The
known full identity was not recoverable: **90,034,289 assignments scored higher
and 29 tied it**. Every deletion also failed; the closest still had 708,301
higher assignments and 216 ties. An independent implementation reconstructed
the result in 40 checks with zero discrepancies.

This is a valuable calibration failure: the representation cannot reliably
recover known house identities across those human sources, so applying it to
the Voynich manuscript would be unjustified. The Voynich target remained
unopened, and no negative conclusion about the manuscript's subject follows.

## Best current model

The most defensible description is a **hierarchical, record-oriented
construction grammar**. We increasingly understand the wiring—boundaries,
dependencies, formal state changes, relative ordering, and record templates—
but not the component names or message.

Any future translation claim must add genuinely independent authorial evidence
or a new invariant that can falsify competing meanings. A new model, visual
guess, spelling resemblance, threshold, or larger brute-force search is not by
itself new evidence.

## Reproducibility pointers

- Live claim registry: [`VOYNICH_ACTIVE_STATE.md`](VOYNICH_ACTIVE_STATE.md)
- Compact experiment ledger:
  [`ACTIVE_EXPERIMENT_LEDGER.tsv`](experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv)
- Confirmed structural grammar:
  [`CONFIRMED_GRAMMAR.md`](experiments/semantic_assumptions/grammar/CONFIRMED_GRAMMAR.md)
- Closed-route memory:
  [`CLOSED_ROUTE_FAMILIES.tsv`](experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv)
- Independent houses validation:
  [`f67r2_ga4_001_houses_invocation_independent_validation_report.md`](experiments/semantic_assumptions/results/f67r2_ga4_001_houses_invocation_independent_validation_report.md)
- Provisional f77r transition bridge:
  [`f77r_quality_transition_bridge_report.md`](experiments/semantic_assumptions/results/f77r_quality_transition_bridge_report.md)
- Residual lexical-identity nonconfirmation:
  [`f77r_residual_form_assignment_report.md`](experiments/semantic_assumptions/results/f77r_residual_form_assignment_report.md)
- Same-orientation source-capacity stop:
  [`f77r_same_orientation_capacity_report.md`](experiments/semantic_assumptions/results/f77r_same_orientation_capacity_report.md)
- Explicit berry/no-fruit nonconfirmation:
  [`berry_explicit_contrast_report.md`](experiments/semantic_assumptions/results/berry_explicit_contrast_report.md)
