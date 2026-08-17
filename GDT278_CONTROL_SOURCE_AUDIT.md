# GDT278 expanded-control source audit

This audit was frozen after the GDT278 magnitude endpoint and before any newly
admitted control was scored.  It admits visible surface corpora and
already-published synthetic observation layers; oracle/expanded material is
used only to establish a ground-truth architecture label.

## Admitted real text systems

- **Nuremberg council letterbooks (1408–1423):** paired expanded and
  diplomatic views from four held books.  These remain a paired causal
  contrast, not independent corpora.
- **Sterzing Ste1 recipes (ca. 1400–1425):** paired expanded and diplomatic
  views of two recipe segments.  With only 111 groups, both are explicitly
  low-capacity native-order sensitivities and cannot enter the 4,476-event
  matched panel.
- **Augsburg municipal accounts (1402–1424):** 22,071 editorial entries and
  281,557 whitespace groups in the frozen electronic edition.  The account
  entry is an editorial record boundary, not a claimed physical manuscript
  line.
- **Five frozen GDT159 graphematic corpora:** medieval Latin medical,
  fifteenth-century Latin mixed genre, medieval Latin scholastic, 1395–1411
  Latin/Portuguese charters, and a late-fifteenth-century Latin/German
  apothecary corpus.  Visible graphematic abbreviation signs are retained;
  lemmas, translations, phoneme mappings, and meanings are absent.

## Admitted generated and coded systems

- **GDT157 held-book abbreviation transducer:** MAP and SAMPLED diplomatic
  outputs generated from expanded Nuremberg text by a transducer learned
  without the held book.  These are historically learned synthetic channels,
  not independent documents.
- **GDT172 lexical System A:** an exactly reversible bounded frequent lexical
  ID codebook with literal escape.
- **GDT172 factorial System B:** an exactly reversible compositional technical
  notation control.
- **GDT173 B2:** an exactly reversible irregular, hand-authored distributed
  table with partial family reuse, optional fields, analogies, and exceptions.

A/B/B2 are frozen observation-layer controls and are not natural medieval
documents.  Their shared source schedule does not make them independent.
Together with the learned MAP/SAMPLED outputs, they are the pre-existing
synthetic matched-capacity variants; no new synthetic encoder is tuned to
Voynich or GDT278.

## Audited exclusions

- GDT156's imposed HPR2-like encoder is excluded because it deliberately uses
  Voynich-derived wrapper/right/closure rules.
- The Foxton/Fontana historical comparator is excluded from scoring because
  the repository contains a scholarly mechanism audit, not a complete
  machine-readable diplomatic surface corpus.
- CoReMA role exports do not retain source surfaces and therefore cannot be
  reconstructed as a surface corpus from the published observation files.
- No corpus is admitted from a modern summary, inferred meaning list, or
  transliteration selected because it resembles a Voynich result.

## Common observation policy

Every admitted visible form is normalized only by the already-frozen GDT277
Unicode/letter policy and passed through the same blind edge-operation parser
family.  Existing published GDT172/GDT173 surface parses are retained as
anchors.  Exact folds/source units are kept for native order; the matched view
uses the already-frozen GDT277 scaffold.  Architecture labels are fixed in
`gdt278_control_manifest.tsv` before scoring.

The audit contains no Voynich substring query and no HPR1 semantic field.  No
f84 source is an input or is accessed.
