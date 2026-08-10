# Source-native structural query tool

Status: **DESCRIPTIVE_INFRASTRUCTURE_ONLY**.

This tool searches the validated source-native structural interlinear without
OCR, image recognition, the unavailable legacy parser, or English glosses.  It
is intended to make manual hypothesis formation fast while preserving the
distinction between:

- complete source-separated construction groups;
- internal STA-family substrings;
- exact sequences of complete groups;
- edition-specific STA member codes and explicitly lossy basic-EVA lookup;
- factual locus position, validated structural tags, and manual separator
  profiles.

All supplied filters are conjunctive.  Regular expressions use Python syntax.
`--surface-regex` searches one complete family surface, `--contains` searches
an internal family substring, and `--locus-sequence-regex` searches the
space-separated sequence of complete family surfaces in one locus.  These are
deliberately separate so a whole group, a group-internal fragment, and a
cross-group pattern cannot be silently conflated.

The default text output prints the complete matching locus and marks matching
groups with `*`.  JSON output is deterministic and suitable for scripts.
Queries never alter the source or create a semantic score.

Claim ceiling: a query result is a concordance hit in a fixed manual-
transcription-derived structural representation.  It is not a word, stem,
morpheme, sound, part of speech, plaintext, language, cipher, or translation.
