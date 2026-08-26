# GDT481 method

## Question

Do recurrent one-event or adjacent-event fragments explain the diversity of
GDT480's 107 singleton whole-record templates, and which fragments recur across
pages, registers, or different surfaces?

## Inputs

The experiment reads only GDT479's complete event, bundle, and record tables
plus GDT480's 135 record-template assignments. No source transcription or new
page is opened.

## Fragment construction

Each record is linearized through its fixed bundle order. This yields 183
one-event fragments and exactly 48 adjacent pairs (`183 - 135`). Eleven pairs
cross a GDT475 bundle boundary; their `EXPLICIT_CONTINUATION_OL` boundary is
kept in the pair key. The other 37 are inside one bundle.

Names become ordered `{N1}`, `{N2}`, ... slots separately inside each fragment,
with equality preserved. A strict key retains active grammatical model,
complete ordered component meanings, OT/OL state and direction, and—on
pairs—the bundle boundary. A role key replaces exact components with ACTION,
ARG, REL, ORDER, NAME, or MOD. It is backoff only.

Templates report occurrence, record, page, register, surface, recipe, and
phrase variation. The 135-record coverage table counts strict and role
recurrence for every event and pair, with a separate view of the 107 GDT480
whole-record singletons.

## Integrity

The validator rebuilds all ten generated artifacts byte-for-byte, checks every
source event and all 48 true adjacencies, verifies the eleven cross-bundle
pairs, recomputes every template family and coverage class, checks the exact
cross-register event deck and sole repeated strict pair, and confirms zero
meaning, model, boundary, surface, recipe, or page change. It passes 118/118
checks.
