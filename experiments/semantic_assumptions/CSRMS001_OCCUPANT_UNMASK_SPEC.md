# CSRMS001 frozen-slot occupant unmask

Status before execution: **REGISTERED_TEN_OCCUPANTS_UNOPENED**

## Bound selection

This one-time descriptive reveal is authorized by the independently validated
CSRMS001 masked selection. Bind:

- `csrms001_masked_recurrent_slot_selection.json`, SHA-256
  `e5c02c3ae7aa4376075e1e7310dad457e06bffc8384aa9deb611ff3299f3f270`;
- `csrms001_masked_recurrent_slot_selection.tsv`, SHA-256
  `75077c41057f1dc0169add9f9f10356e5c8a676d1c6c8222301cff8dc47e4c86`;
- its validation JSON, SHA-256
  `bc268a3006eff3a5cfaf3a62240c5e46d28605f3fabfe05137bfdd72769835c9`;
- the consensus interlinear, SHA-256
  `7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387`.

The frozen context is Currier A, five-group record, ordinal 3, with left
neighbour shell `C/I/U` and right neighbour shell `C/I/I`. It has exactly ten
rows on nine physical folios across sections H and P. No row or context may be
added, removed, reranked, or substituted.

## Reveal

For each frozen row, reveal only the ordinal-3 occupant's:

- consensus family surface;
- exact ZL/IT/RF STA member group, requiring all three to agree;
- separate ZL, IT, and RF lossy-EVA displays;
- its already registered current formal expression.

Do not reveal neighbouring surfaces in the unmask table and do not search any
other context. Treat the three readings as alternate descriptions, not three
observations.

## Descriptive recurrence flags

Compute exact counts and physical-folio support for family, exact member, and
current formal shell. Set these flags without changing their thresholds:

- `FAMILY_RECURRENCE`: one family has at least 5/10 occurrences on at least 5
  physical folios;
- `MEMBER_RECURRENCE`: one exact member group has at least 4/10 occurrences on
  at least 4 physical folios;
- `CURRENT_SHELL_RECURRENCE`: one current formal shell, after removing family
  surface and favored path, has at least 7/10 occurrences on at least 6
  physical folios.

These are transparent description thresholds, not p-values. No background
comparison, enrichment score, model, permutation, alternative-context search,
or English gloss is permitted.

## Decision and ceiling

- If no flag passes: `STOP_DIVERSE_OCCUPANTS_NO_RECURRENT_FILLER_CLASS`.
- If a flag passes: `PASS_DESCRIPTIVE_RECURRENT_FILLER_CLASS` and retain only
  the named anonymous formal recurrence for a separately designed test.

Even a pass does not establish a lexical slot, synonymy, POS, morpheme, word,
sound, language, cipher operation, plaintext, meaning, or translation.
