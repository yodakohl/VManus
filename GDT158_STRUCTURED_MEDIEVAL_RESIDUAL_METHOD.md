# GDT158 — structured medieval document residual control

Status: **SOURCE PANEL FROZEN BEFORE RESIDUAL SCORING**.

Date: 2026-08-15

Branch: `yolo/gdt002-visual-grammar-constraints`

## Question

Can authentic early-fifteenth-century document structure, acting on genuinely
abbreviated historical text, generate the residual architecture left open by
GDT157: operation scale, compatible-operation density, left-dominant edge
support, a stable line/record reset, opening/closing classes, and a B3-like
closing class?

This is a document-architecture control, not a language, decipherment,
plaintext, or translation test. GDT157 already calibrated abbreviation. GDT158
does not tune, refit, or add a Nuremberg abbreviation rule, and it introduces no
Voynich wrapper or literal.

## Frozen source panel

The panel is selected solely by date, genre, public scholarly provenance, and
boundary capacity:

1. `AUGSBURG_ACCOUNTS_1402_1424`: all nonempty `Originaltext` entries whose
   source year is 1402–1425 in Dieter Voigt's research-data workbook of the
   Augsburg *Baumeisterbücher*. The resulting 22,071 entries span 18 available
   years and 1,817 year+folio units. A spreadsheet row is an **edited account
   entry boundary**, not claimed to be a physical manuscript line.
2. `NUREMBERG_LETTERBOOKS_1408_1423`: all 48,337 frozen diplomatic PAGE-XML
   lines in 3,176 outgoing-letter/register records from GDT155. TextLine and
   document-division boundaries are retained.
3. `STE1_TECHNICAL_RECIPES_1400_1425`: both frozen Ste1 technical recipe
   segments (10 TEI line rows total) from GDT155. This is a relevance control,
   not a powered operation-algebra sample.

The source inventory, dates, roles, counts, public URLs and exact hashes are in
`gdt158_structured_source_manifest.tsv` and `gdt158_source_freeze.json`.
Corpus choice was frozen before calculating any residual score.

## Views and causal separation

No new abbreviation transducer is trained.

- Nuremberg supplies paired `EXPANDED` and real `DIPLOMATIC` views already
  frozen by GDT155/GDT157.
- Ste1 supplies the same editorial expanded/diplomatic pair at low capacity.
- Augsburg supplies the edition's `Originaltext` account-entry surface. It is
  not represented as a parallel expansion corpus and is never used to retune
  the Nuremberg channel.

For every real structured surface, a topology-preserving boundary null keeps
the complete ordered token stream and the exact multiset of line/entry lengths
inside its parent record/page, but cyclically rotates the length sequence by a
nonzero deterministic offset. Thus vocabulary, abbreviation, token order,
record/page membership, and length opportunities are identical; only the
placement of openings and closings changes. One-sided or single-line parent
units remain observations but do not contribute permutation mobility.

## Frozen endpoints

### Surface algebra

On a deterministic matched 12,000-group sample for each powered corpus/view,
reuse the exact GDT003 nested held-fold diagnostic:

- mean discovered edge operations;
- compatible-operation-pair density;
- left/right edge support, reported as `log2((right+1)/(left+1))` so negative
  values mean left-dominant support;
- complete rectangles and held-fourth-cell performance against the original
  KT/frequency/edit baselines.

The already-published, explicitly f84r-free `VOYNICH_MATCHED` row is the fixed
reference. Ste1 is reported as low-capacity descriptive only.

### Boundary architecture

For each corpus/view calculate:

- exact-token and learned edge-class opening/interior and closing/interior
  Jensen–Shannon distances;
- within-line versus across-line character-trigram similarity reset;
- within-record line-boundary versus cross-record boundary reset where the
  source has multi-line records;
- cross-space edge dependence;
- held-source B3-like closure lift.

The B3-like endpoint is language agnostic. In each outer source fold, training
data enumerate complete-token, one-to-three-character suffix, and learned
right-edge-operation predicates with at least eight hosts and five parent
units. The single training-best terminal-vs-interior predicate is frozen and
evaluated on the held fold. Literal `dy`, `m`, `q`, or any other Voynich value
is unavailable. The null repeats the complete train/select/held evaluation
after boundary rotation; selection is therefore inside every null world.

## Controls and decision

- Boundary tests use 4,096 deterministic, parent-unit-preserving rotations.
- Surface-algebra comparisons include all exercised corpus/views in the
  descriptive family; no local corpus resemblance is called confirmation.
- Nuremberg diplomatic-minus-expanded is an integrity anchor for calibrated
  abbreviation, not a newly fitted causal result.
- Augsburg is the powered genuinely structured accounting transfer.
- Ste1's two recipes cannot establish a generic recipe effect.

Final status vocabulary:

- `DOCUMENT_STRUCTURE_GENERATES_MOST_RESIDUAL_ARCHITECTURE`
- `DOCUMENT_STRUCTURE_GENERATES_PARTIAL_RESIDUAL_ARCHITECTURE`
- `DOCUMENT_STRUCTURE_DOES_NOT_GENERATE_RESIDUAL_ARCHITECTURE`
- `INSUFFICIENT_STRUCTURED_CONTROL_CAPACITY`

## Seal and claim ceiling

No Voynich source row, image, parser, or transcription is read. The only
Voynich numerical target is the published f84r-free GDT003 aggregate and
context-only published reset/B3 summaries. f84r is not opened, queried,
retained, joined, or scored.

At most GDT158 can show that authentic medieval document boundaries plus
historical abbreviated surface do or do not generate specified formal
statistics. It cannot identify a Voynich language, word, morpheme, sound,
plaintext, semantic role, meaning, origin, scribal tradition, or translation.
