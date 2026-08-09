# Pre-grounding surface/formal coverage correction

Decision: **COMPLETE SURFACE, PARTIAL FORMAL PARSE**.

The frozen `pre_grounding_interlinear.tsv` contains every available
manual-transcription locus and preserves its complete literal `surface` field.
Its `root_sequence`, `role_sequence`, `formal_interlinear`, and `word_count`
fields do **not** cover every surface group. They cover only the groups retained
by the former formal parser.

This mismatch had already been noticed narrowly during CC002 as a warning not
to zip raw surface tokens to parsed roots. The package-level completeness claim
was not corrected then. This audit makes the limitation explicit and supplies
the missing literal residual layer.

## Exact coverage

Across all three alternate readings:

| measure | literal surface | formal layer | residual |
|---|---:|---:|---:|
| reading-specific rows | 15,960 | 15,960 | 2,833 affected |
| space-delimited groups / nodes | 118,011 | 114,173 | 3,838 |
| non-space characters | 573,309 | 568,072 | 5,237 |

The formal layer therefore retains 96.748% of surface groups and 99.087% of
non-space characters. The difference is not insertion or replacement: on every
one of the 15,960 rows there is exactly one order-preserving subset of complete
surface groups whose concatenation equals the stored formal-node stream, and
the selected groups equal the formal node surfaces one-for-one.

| reading | affected rows | omitted groups | omitted characters |
|---|---:|---:|---:|
| ZL3b | 678 | 817 | 1,308 |
| IT2a | 516 | 599 | 1,072 |
| RF1b | 1,639 | 2,422 | 2,857 |

The most frequent residual groups are `y` (2,463), `dy` (774), `sy` (114),
`ky` (83), and `yty` (73). These are transcription strings, not assigned roots,
words, suffixes, or meanings. The new residual atlas preserves each omitted
group and its one-based surface position under the structural tag
`UNPARSED_SURFACE`.

## Consequences

- The package remains complete as a locus and literal-surface atlas.
- Root, role, tuple, relation, and `word_count` statistics are exact only for
  the retained formal-node layer. They are not an exhaustive inventory of all
  transcribed groups.
- Existing formal results are not automatically false. A result that explicitly
  tested the frozen parsed-node representation still tested that representation.
  Claims of exhaustive surface coverage or absence must be qualified, and a
  route may be reopened only if the residual groups are relevant to its frozen
  target or falsifier.
- SME003 remains closed: it failed target-free synthetic calibration before any
  morphology row was opened. The correction cannot turn that failure into a
  morphology result.
- COL001's frozen formal-node counts are unchanged. `f2r.15` has no residual,
  and none of the 3,838 omitted groups contains literal `i` or `o`, so there is
  no literal `i`/`o`-bearing residual candidate. This does not predict what a
  future parser might assign to an unparsed group. The counts remain partial
  formal-layer statistics, not translations or exhaustive surface absences.

## Reproducibility limit

The original package builder imports `run_internal_utterance_grammar.py`, but
that source is absent from the current tree and reachable Git history. An older
archive manifest recorded only its former size (23,732 bytes) and SHA-256
`39f38b89bba9cb02aaa2b56f5d4236ae1d3f041c4624f3f3b4ddc3181a481f4c`.
The frozen package can therefore be byte-validated and its surface residuals
independently reconstructed, but the formal parse cannot currently be rebuilt
from source. Do not silently recreate the missing parser. Any replacement must
be a new, versioned parser with explicit all-surface coverage and held
equivalence checks on the retained nodes.

## Reproduction

- `audit_pre_grounding_surface_coverage.py` builds the exact residual atlas and
  compact audit JSON from the frozen interlinear.
- `validate_pre_grounding_surface_coverage.py` independently reconstructs all
  15,960 unique alignments, the 2,833-row atlas, edition/scope/kind totals,
  omitted-type counts, exact inputs, examples, and the claim boundary in 32
  checks.
- `pre_grounding_surface_residual_atlas.tsv` is the new literal residual layer.

No OCR, automated image recognition, English gloss, or morphology label was
used.
