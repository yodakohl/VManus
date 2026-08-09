# Source-native STA member-code agreement atlas

## Purpose

Characterize fine STA member-code stability across ZL3b, IT2a, and RF1b on the
strict exact-family scaffold before any further grammar model chooses a symbol
resolution. This is a descriptive transcription-policy audit, not a vote for
the physically correct glyph and not a grammar or semantic score.

## Frozen inputs

- `results/source_sta_family_consensus_groups.tsv`, SHA-256
  `a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225`
- `results/source_sta_family_consensus_validation.json`, SHA-256
  `fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76`
- this specification and builder.

## Unit and classifications

Use every aligned symbol position in every strict zero-alternative locus. The
three member codes must have the same already-confirmed STA family at each
position. Classify the reading triplet exactly as:

- `ALL3`: ZL = IT = RF;
- `ZL_IT`: ZL = IT != RF;
- `ZL_RF`: ZL = RF != IT;
- `IT_RF`: IT = RF != ZL;
- `ALL_DIFF`: all three codes differ.

Record exact counts by family, Currier, group position, reading pair, and
ordered `(ZL,IT,RF)` disagreement triplet. Recto/verso and panels share the
same physical-folio prefix, but no inferential test treats positions or
readings as independent samples.

## Hard gates

- exact reconstruction of 95,451 strict positions;
- exact same-family membership for every code triplet;
- every position assigned to exactly one of the five patterns;
- pairwise agreement counts reconstructed directly, not inferred from a
  preferred reading;
- all disagreement-triplet, family, Currier, and position counts sum back to
  the position universe;
- independent nonimporting reconstruction of the TSVs, JSON, and report;
- no member-code collapsing, corrected transcription, physical-glyph choice,
  grammar score, legacy root/role, or English gloss.

## Claim ceiling

The atlas may identify stable fine-code agreement and systematic differences
between manual transcription policies. It cannot establish which reading is
physically correct, that two codes are allographs or equivalent, a sound,
alphabet, cipher alphabet, word, meaning, plaintext, language, or translation.
