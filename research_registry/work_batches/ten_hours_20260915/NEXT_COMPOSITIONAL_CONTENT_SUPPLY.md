# Next compositional content supply

This bounded source-only note proposes one new whole-reading architecture from
the established GDT605/607/608 formal results. It does not inspect Voynich
text or images, access reserves, alter GDT966, or assign any BPE unit a letter
or confirmed English meaning.

## Primary evidence

* [GDT607 report](../../../experiments/yolo/gdt607_boundary_word_disentanglement/REPORT.md), SHA-256 `f0246c846ed975340e8c148357754f5f2e7e0b4d22cdd8f1ba99f5434d85abe0`:
  `W` is mainly a frequency/mobility-weighted output-capacity bucket rather
  than an observed whole-word class. Five recurring units retain distinct
  formal carrier roles; their stable information is orientation and scope, not
  plaintext.
* [GDT608 report](../../../experiments/yolo/gdt608_compositional_stem_orientation/REPORT.md), SHA-256 `7c59478cdd9e9a7d4c4a3bda6c369892411f7830aefc49b3dce9a041d4e8c501`:
  64 frozen BPE merges carry directed exterior-role information on 23 held
  folios, while atomic merge identity remains better overall and supplies a
  pair-specific residual role. The result is formal composition, not
  morphology or meaning.

The bounded duplicate screen used `ideas search`, `ideas duplicates`, and
`route-check` for directed composition, W-bucket roles, residual pivots, and
content frames. GDT608, GDT611, GDT393, GDT805, IDEA000024, and related
history were the closest candidates. The new design differs by requiring a
single three-position **joint chain**—left directed carrier, exact whole
residual, right directed carrier—before any occurrence-scoped content role is
even considered. It was added as
[IDEA000341](../../proposals/directed_carrier_chain_content_pivot_20260915.json).

## Proposed architecture: directed carrier chain with a whole pivot

The possible reading is a complete local field of the form:

`[left opener/entry carrier] → [whole-form residual pivot] → [right closer/result carrier]`

This is a content relation, not a character translation. A conservative
structural rendering would be “begin the field; record the item carried by the
whole form; close or complete the field.” The words *begin*, *item*, and
*close* are role labels for a hypothetical sentence and are not claimed
lexemes.

The chain uses three established facts jointly:

1. GDT607's formal defaults distinguish opener-like `C`/`d`, flexible
   connector-like `o`, closure-like `y`/`dy`, and boundary/standalone-like
   `ol`; these labels describe measured edges only.
2. GDT608 preserves the direction of a merge (`L+R=M`) and shows that the
   atomic whole `M` still carries residual information. Concrete pairs include
   `ol=o+l`, `or=o+r`, `ok=o+k`, `ot=o+t`, `dy=d+y`, and `aN=a+N`.
3. The corrected `W` result prevents treating capacity membership as a
   semantic word class. A whole pivot therefore has to retain its exact
   identity and entry context; its components cannot be exported as words.

For a future source-first check, a complete field must satisfy all of these
conditions: exact hard-chunk/line boundary; an observed left edge role; an
exact whole residual; an observed right edge role; and an entry context held
out from the role labels. A field with only one exterior edge, only a W
membership, or only a repeated whole is not a content-chain instance.

## Concrete cases and predictions

The candidate cases are formal merge families already named in GDT607/608,
not newly selected targets:

| Case | Joint reading if licensed | Required relation |
|---|---|---|
| `d+y=dy` | a line/chunk entry carrier followed by a whole pivot and a closure-bearing right edge | left head profile and right closure profile both survive, while `dy` retains an atomic residual |
| `o+l=ol` | a flexible connector enters a bounded field whose whole pivot reaches a boundary/standalone edge | the observed paired boundary profile must add to, rather than replace, the component profiles |
| `o+k=ok` or `o+t=ot` | a connector enters a field whose pivot is followed by a non-final or result-side carrier | the pair-specific entry profile must be present with the right-side non-finality control |
| `qok+X` deep merges | a rare whole pivot inside a strongly entering `q` family | the deep merge's atomic residual must beat a component-only explanation on held complete fields |
| `a+N=aN` | a two-sided composed pivot with both exterior roles available | both left and right backoff relations must hold; one-sided transfer is a failure |

The architecture predicts a joint held-field margin for the complete-chain
model against four controls: component-only edge roles, atomic-only whole
identity, within-family residual permutation, and W-capacity matching. The
test must stratify by section, hand, Currier, line position, and entry context,
and preserve physical folio holdouts. It must count a chain once at its exact
field locus; repeated boundaries or alternate renderers do not create new
semantic evidence.

If the chain passes, a later content reading is allowed only as an
occurrence-scoped field relation: opener → whole item/pivot → closure/result.
This yields a complete structural sentence such as “the entry begins, records
the carried item, and closes,” while leaving the item name unresolved. It also
blocks component-by-component translation and global W-to-word assignments.
If it fails, GDT607/608 retain their formal composition findings, but the
whole pivot is removed as a content architecture.

## Why it may fail

The measured edge roles may be positional only; `ol`, `or`, `ok`, and `ot`
already show pair-specific behavior that can defeat a shared chain. Atomic
identity may reflect frequency or mobility, and the W bucket's capacity bias
can create apparent output-bearing pivots. A complete field may be a title,
amount, or diagram label rather than content. Entry boundaries can be
ambiguous, and inherited renderer categories cannot serve as independent
semantic endpoints. GDT608's atomic advantage on all held folios is a direct
warning against assuming that component backoff is a complete code.

## Relation to existing proposals

GDT608 tests directed exterior backoff and pair-specific residuals. GDT611
tests whether formal carriers identify recipe/medical lexical slots against
within-family meaning permutations. IDEA000024 asks whether one whole changes
role by argument position. This proposal has a different minimum unit and
decision: a **joint three-position chain** must survive held field controls
before any content role is entertained. The duplicate screen found no exact
declared-design match, but these neighboring results remain explicit rivals.

No additional cards were added: the single distinct proposal is IDEA000341;
the rest of the bounded alternatives remain in the existing registry. No
global route, active state, ledger, experiment index, or title/mark decision
was changed.

## Smallest adequate follow-up

Use only already cached guarded artifacts. Freeze exact BPE merge boundaries,
complete field boundaries, the left/right formal role labels, whole residual
identity, entry context, and the four rival models before scoring. Apply
physical folio holdouts and matched W/frequency/mobility controls. Stop if an
endpoint or content label depends on inherited German rendering, or if the
three-position relation does not separate from the controls. This is a
bounded source/model review, not a decoder repair or reserve experiment.
