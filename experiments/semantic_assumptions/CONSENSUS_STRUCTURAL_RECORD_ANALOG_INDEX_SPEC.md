# Consensus structural record analogue index v1

## Purpose

Build a transparent cross-folio inspection index for the 26 records in the
validated consensus structural packet.  The index does not search for a
translation and does not call nearest records parallel passages.  It exposes
the closest already published formal records so a human reader can compare
recurring constructional shapes without silently selecting examples.

## Frozen source

The only scientific table is
`results/consensus_structural_record_interlinear_v1.tsv` at SHA-256
`7c375a9336588096e657917548eb3f2038828d9d6d42b75da2d24b57ccd3f387`.
Its independent validation JSON is required at SHA-256
`368d1be6a70c403f77abb5f87e3c0635bea1cf084c6b7408530cbf857c2e1533`
with status `PASS_INDEPENDENT_RECORD_LEVEL_CONSENSUS_RECONSTRUCTION`.

No manuscript image, OCR, automated vision, legacy parser root or role,
external decoder, historical-language guess, or English gloss may enter.

## Targets and candidates

The targets are exactly the 26 rows having `packet_selected=1` in source
`record_order`.  A candidate must:

1. have `grammar_scope=CONFIRMED_PROSE`;
2. have `transcription_consensus_status=ALL_MEMBER_AND_BOUNDARY_STABLE`;
3. have the same `currier` and exact `group_count` as the target; and
4. lie on a different physical folio.

The physical folio is the leading decimal integer after `f` in `page`; recto,
verso, foldout panel, and locus suffixes on that integer remain one folio.
Every eligible candidate is emitted.  This is a descriptive candidate pool,
not a matched statistical sample.

## Exact expression parser

Each group in `formal_expression` must parse as

`POSITION:SURFACE{adj=ADJ;fl=FL;ec=EC;o=O;c=C;p=PATH}`

with groups separated by the literal string ` | `.  Candidate and target group
ordinals are aligned because `group_count` is exact.  STA member expressions
are split first on ` | ` and then on ASCII spaces.

## Distances

Use unit-cost Levenshtein distance with insertions, deletions, and
substitutions each costing one.  For aligned group ordinal `j`, compute:

- adjacency distance: Levenshtein distance between the `adj` strings;
- first/last mismatch: one iff `fl` differs;
- edge/core mismatch: one iff `ec` differs;
- opening-count distance: `abs(O_target - O_candidate)`;
- closing-count distance: `abs(C_target - C_candidate)`;
- favored-path distance: Levenshtein distance between `p` strings after
  replacing `-` by the empty string;
- family distance: Levenshtein distance between the family surfaces; and
- STA-member distance: token-level Levenshtein distance between the ZL STA
  code sequences.  ZL is a display choice only: all eligible rows are
  all-reading member-stable.

Sum every component over aligned group ordinals.  Define

`structure_distance = adjacency_distance + first_last_mismatches +
edge_core_mismatches + opening_count_distance + closing_count_distance`.

The favored path, family surface, and exact STA member distances remain
separate so the index never hides surface identity inside the formal score.

## Ranking and outputs

Within each target rank every candidate by the exact tuple:

1. ascending `structure_distance`;
2. ascending `family_distance`;
3. ascending `sta_member_distance`;
4. ascending `favored_path_distance`;
5. same section before different section;
6. ascending UTF-8 bytes of `candidate_segment_id`.

Emit the full candidate index and a compact packet containing ranks 1--3 for
each target.  Include all distance components and both source expressions.
The report must state candidate capacity and whether an exact surface-blind
formal match exists; absence of such a match is a capacity description, not a
negative semantic result.

## Claim ceiling

The result is a deterministic inspection concordance over already validated
formal tags.  A close neighbor may be called a formal analogue only.  It is not
evidence of a repeated sentence, parallel passage, shared referent, word,
part of speech, morphology, sound, language, cipher operation, plaintext,
meaning, or translation.  Basic EVA is an explicitly lossy display field.
