# Source-preserving STA alignment

## Purpose

Replace the lossy legacy ASCII character layer with the official common STA1
representation while retaining the source transcribers' separator topology.
This is a transcription repair and normalization pass, not a decipherment
experiment.

## Frozen inputs

Native IVTFF sources:

- `transcription/sources/IT2a-n.txt`
- `transcription/sources/ZL3b-n.txt`
- `transcription/sources/RF1b-e.txt`

Official STA1 level-0 conversions downloaded from René Zandbergen's
transliteration site:

- `transcription/sources/sta/IT2a.txt`
- `transcription/sources/sta/ZL3b.txt`
- `transcription/sources/sta/RF1b.txt`

Official bidirectional conversion rules:

- `transcription/sources/sta/STA-EvaT_def.bit` for IT2a;
- `transcription/sources/sta/STA-Eva_def.bit` for ZL3b and RF1b;
- `transcription/sources/sta/STA-Eva_Bint.bit` only for the explicitly lossy
  nearest-basic-EVA convenience projection.

The already validated source-separator atlas is used only as a frozen
crosswalk:

- `experiments/semantic_assumptions/results/source_separator_transcription.tsv`

The three readings describe one manuscript and are never independent samples.

## Exact alignment contract

For each edition:

1. Native and STA files must have the same unique locus keys and locus codes.
2. Split each locus only at `.`, `,`, `<->`, or `<~>` outside annotations.
3. The native and STA rows must have the same ordered separator sequence and
   therefore the same number of source groups.
4. Each STA character is exactly one two-byte code matching
   `[A-Z][0-9a-z]`. Square brackets retain all supplied alternatives; the
   first alternative is stored separately only as a deterministic analysis
   path.
5. Applying the official edition-appropriate bidirectional rules to the STA
   row must reconstruct the native row exactly after removal of native inline
   comments, which the official STA release deliberately omits.
6. Every observed STA code must exist in both the exact reverse rule and the
   nearest-basic-EVA rule. The latter projection is marked lossy and may never
   replace the retained raw STA form.
7. Every aligned group must match exactly one frozen source-group ID and its
   separator metadata.

No network access is permitted during a build or validation. Cached official
files are hash-bound inputs.

## Output

One TSV row per source group stores the source-group ID, STA markup, the
deterministic first-alternative STA code sequence, its family sequence, and a
nearest-basic-EVA convenience projection. The raw STA markup remains the
authoritative normalized surface.

## Hard gates

- exact hashes for every frozen source, rule, specification, and crosswalk;
- exact native/STA locus-key and locus-code equality;
- exact group and separator topology in every row;
- exact reverse reconstruction of every native row and group;
- fixed-width and rule-coverage validation of every STA code and alternative;
- exact one-row-per-source-group crosswalk coverage;
- independent nonimporting reconstruction of the complete TSV, JSON, and
  report;
- zero formal roles, roots, English glosses, or semantic labels.

## Claim ceiling

This pass may establish a lossless, common, source-separator-preserving
character representation and an explicitly lossy basic-EVA convenience view.
STA families and members are transcription codes, not proven physical letters,
sounds, morphemes, words, or meanings. The pass cannot establish authorial word
boundaries, language, cipher, lexemes, plaintext, or translation.
