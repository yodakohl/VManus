# GDT868 fixed CORE13 raw-group source fidelity

This is a retrospective deterministic audit of the unchanged1777GDT808 events
used by GDT865, not a new significance test, learned decoder or model refit.
GDT808's unique-forced LCS and rank stability operate on clean token vectors.
The atlas maps raw groups to an older interlinear vector, so its positions
cannot be assumed identical to the current clean vectors without full-line
parity. GDT819 performed that comparison for a different small local panel;
no checked primary report has performed it for this entire fixed event set.

## Frozen inputs and exposure

SPEC fixes the179-selector allowlist, three exact guarded TSV projections and
the published865event metadata. Only headers and implementation code were
inspected for this design; one illustrative865EVENT_METADATA row (G808-E0001,
f2r.5, clean chol) was printed during navigation. Prior808/865predictions and
other public raw texts are known. No target-to-raw-group mapping or count was
computed before registration. Publication of this contract and all source
code precedes target projection. No new images/pages, f84/f84r remain sealed.

## Gates before classification

1. Require exactly1777unique event IDs and unchanged carrier/axis/surface/page/
   locus/token_index against865. Read the three position fields from808,
   preserving the recorded IT/RF1-based unique-LCS ordinals.
2. For every focal(page,locus) and all three readings, reconstruct the complete
   ordered source-group row. Require indices1..n, consistent declared group
   counts, fragment counts and ZERO/ONE/MULTI_ASCII_FRAGMENT statuses,
   consecutive comma-separated legacy token positions, and adjacent separator
   agreement. Do not confuse group indices with legacy token positions.
3. Require the concatenated whitespace-split fragments to equal the full
   corresponding current cross-reader clean vector, not just the target word.
   Any mismatch stops the entire mapping audit; no manual offset repair,
   salvage subset, alignment relaxation or replacement event.
4. Only after all full lines pass, each stored event position must resolve
   uniquely and its fragment must exactly equal the fixed event surface.
   Missing, ambiguous or mismatching source contracts stop without classification.

## Descriptive categories

- EXACT_RAW_WHOLE: one fragment and literal raw group equals event surface.
- NORMALIZED_WHOLE: one fragment but literal raw group differs. This includes
  editorial annotations/alternatives removed by cleaning; no glyph identity
  is inferred.
- CLEANER_FRAGMENT: multiple fragments from one raw group; the event is one
  fragment, even if it agrees with the other cleaned readings.

Retain raw form, separators and source-group ID for every event/reading. Count
by edition and by edition/axis; also report all-three-exact, all-three-single-
group, any-fragment event counts and target incidences touching uncertain
small spaces or drawing interruptions. These boundary flags are separate
from raw-string exactness. Alternate readings remain one manuscript.

No AUC, model, null, feature vocabulary, neighbor classifier or event exclusion
is recomputed. Target fidelity does not establish the fidelity of every model
feature or its full training corpus, authorial wordhood, a phonetic glyph,
morpheme, syntax, relation or meaning. No threshold converts this census into
independent semantic evidence. A later correction would need its own contract.

## Reproduction and scope

Runner performs selector-first guard queries; caches complete projections only
in ignored runtime and records exact hashes/stats. Compact artifacts preserve
all complete source groups on focal lines plus all event mappings. Validator
is independently authored, re-queries each projection and reconstructs source
parity, classification and all counts without importing the runner. Its PASS
validates source arithmetic, not the manuscript reading. No raw mixed TSV is
opened directly or whole-file hashed.

Budget: start10:14:01UTC, intended final publication by10:35UTC. Failure stops
the route rather than adding a model. The ten-hour overall goal stays active.
