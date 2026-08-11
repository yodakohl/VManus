# CSRMS001 masked recurrent-slot selection

Status before execution: **REGISTERED_FILLER_MASKED_CAPACITY_ONLY**

## Question

Does the validated record-level consensus interlinear contain a recurrent
interior position that can be selected without using the identity of the group
occupying that position?

This is a deliberately narrower question than record prediction, centered
substitution, or whole-record analogue ranking.  It selects one position from
the already validated structural interlinear and does not fit a model or score
a target identity.

## Frozen input and scope

Use only
`results/consensus_structural_record_interlinear_v1.tsv`, SHA-256
`7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387`,
after checking its independent validation result, SHA-256
`368d1be6a70c403f77abb5f87e3c0635bea1cf084c6b7408530cbf857c2e1533`.

Retain records with:

- `grammar_scope == CONFIRMED_PROSE`;
- `transcription_consensus_status == ALL_MEMBER_AND_BOUNDARY_STABLE`;
- five through twelve groups inclusive.

Candidate positions are one-based ordinals 3 through `L-2`, so the occupant
has two groups on both sides.  Physical folios are the leading decimal number
in the page identifier.

## Filler masking

The selector must not access `family_expression`, any ZL/IT/RF STA expression,
any lossy EVA expression, or the current group's surface or favored path.
Within `formal_expression`, the surface and path are syntactically skipped.
Only the two immediate neighbours contribute a structural shell.

Every context also includes exact `currier`, record length, and one-based
occupant ordinal.  The current occupant contributes no family, member, surface,
path, adjacency, tendency, edge/core, opening, or closing value.

## Fixed coarsening ladder

Test these neighbouring-shell definitions in order and stop at the first level
with a passing context:

1. `FULL`: position, exact adjacency string, first/last tendency, edge/core
   state, opening count, closing count.
2. `COMPOSITION`: position, counts of F/D/U in adjacency, first/last tendency,
   edge/core state, binary nonzero opening and closing indicators.
3. `TENDENCY_COUNTS_BINARY`: position, first/last tendency, edge/core state,
   binary nonzero opening and closing indicators.
4. `TENDENCY_EDGE`: position, first/last tendency, edge/core state.
5. `EDGE_ONLY`: position and edge/core state.

A context passes only with at least 10 occurrences, 8 distinct physical
folios, and 2 distinct manuscript sections.  Among passing contexts at the
first passing level, rank by distinct folios, occurrences, sections, and hands,
all descending, then by compact UTF-8 JSON encoding of the context ascending.

The output contains the selected context and its occurrence metadata but no
occupant or neighbouring surface, family, member, path, EVA, or image-derived
identity.  The later unmask step, if authorized, must bind this result hash and
may reveal only the occupants of these already frozen rows.

## Decision and ceiling

- No passing level: `STOP_NO_RECURRENT_FILLER_BLIND_SLOT`.
- Passing level: `PASS_MASKED_RECURRENT_SLOT_SELECTED` and authorize one exact
  occupant unmask.

Neither outcome assigns a word, part of speech, morpheme, sound, language,
cipher operation, plaintext, meaning, or translation.
