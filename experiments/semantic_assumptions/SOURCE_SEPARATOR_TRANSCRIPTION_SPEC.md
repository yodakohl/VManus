# Source-separator transcription correction

## Purpose

Build a loss-accounted transcription layer directly from the three frozen
human IVTFF sources.  The layer must preserve the transcribers' separator
states before any grammar, morphology, or semantic experiment is attempted.
It corrects representation coverage; it is not a decipherment experiment.

## Frozen inputs

- `transcription/sources/ZL3b-n.txt`
- `transcription/sources/IT2a-n.txt`
- `transcription/sources/RF1b-e.txt`
- `experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv`

The three editions are alternate readings of one manuscript, never independent
replications.

## Source grouping

Within each IVTFF locus body, scan left to right and split only at the four
source separator markers outside square, brace, and angle annotations:

- `.` = confident apparent space;
- `,` = uncertain small apparent space;
- `<->` = drawing interruption;
- `<~>` = unaligned drawing interruption.

The first two definitions and the two drawing-break forms follow IVTFF format
section 6.7.  `<%>` and `<$>` are stored as row-opening/closing flags, not as
group content.  Other angle annotations remain inside the source group so that
the original cleaner mapping is reproducible.  Square alternatives, brace
forms, question marks, apostrophes, and `@number;` extended entities remain
verbatim inside the source group.  No extended entity is guessed or expanded.

Every nonempty source group receives exactly one row in the output atlas.  Its
left and right separator states are stored explicitly.  Empty spans and
compound separator sequences are forbidden on the frozen sources.

## Legacy mapping

For audit only, independently reproduce the legacy ASCII cleaner:

1. select the first field of a square alternative;
2. remove brace content;
3. replace angle annotations with spaces;
4. remove `?`, `!`, `*`, and apostrophes;
5. split at whitespace or `. , ; : = / \\ | + -`;
6. retain lower-case ASCII letters only.

Map its emitted ASCII fragments back to the containing source group and to the
existing pre-grounding `surface` positions.  A zero-fragment source group is a
source omission in the legacy layer.  A source group producing two or more
fragments contains one or more cleaner-created boundaries; these must be
labelled nonmanual and may not be treated as human word boundaries.

## Hard gates

- exact frozen input hashes;
- unique `(edition,locus)` source and interlinear keys;
- exact source/interlinear row coverage accounting;
- exact legacy surface-token equality for every retained row;
- every zero-token source row absent from the legacy interlinear and every
  nonzero source row present;
- exactly one atlas row per source group with contiguous group indices;
- exact four-state separator vocabulary and source-level adjacency;
- no inferred extended-glyph expansion, formal role, root, English gloss, or
  semantic label.

## Claim ceiling

The artifact may establish source-row, source-group, separator, and
legacy-cleaner loss/split provenance.  It cannot establish authorial word
boundaries, pronunciation, a language, a cipher, grammatical roles, lexemes,
plaintext, or translation.
