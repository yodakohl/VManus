# GDT702 method

## Question

Does the complete immediate-right-context census of all eleven GDT701 target
actions, together with both `ykaiin` targets and both in-scope `olpchedy`
occurrences, support one occurrence-bound C012 link from `f105v.1#4` to the
written result-state label at `#5` without generalizing adjacency, action
surface or morphology?

## Fixed scope and inputs

The scope is exactly GDT701's 479 token positions, 51 lines, 36 already
admitted pages, 175 GDT695 clauses and three bound spans. No page,
transcription or image is added. `f84` and `f84r` remain forbidden.

The direct evidential chain is deliberately separated by function:

- GDT682 `FINAL_COMPLETED_LINE_V56.tsv` records the old practical sentence
  that already called `olpchedy#5` the result of heating. Its
  `TARGET_EXACT_OCCURRENCE_AUDIT.tsv` also supplies the old local heat-object
  reading for `olpcheey#3`. These rows establish provenance and duplication;
  they are not fresh support for C012.
- GDT687 `V60_95_POSITION_SCOPE_DISPATCH.tsv` types both current
  `olpchedy` occurrences as high-confidence
  `NOMINAL_FINISHED_RESULT_STATE`. This licenses a result-state candidate but
  identifies no producing action.
- GDT689's surface and position inventories classify `olpchedy` as
  `UNPAIRED_WHOLE_RETAINED` with a visible sister lacking an independent
  working card. The whole-token reading may be retained; no `olpche*`
  morphology may be exported.
- GDT695 `V68_175_CLAUSE_REALIZATIONS.tsv` fixes the complete action clauses
  and the following clause boundaries used by the census.
- GDT696 fixes C001, the written material-object edge from
  `f105v.1#3 olpcheey` to `#4 ykaiin`, and C006, the different measured-share
  input to the second `ykaiin` at `f86v6.25#5`. C001's license itself descends
  from GDT682 and therefore is current graph state, not independent semantic
  confirmation.
- GDT697 `V70_7_EXACT_MICRORECORDS.tsv` fixes M002 to ordinals `#3–#4`, names
  `#5 olpchedy` as its right neighbour, and explicitly says not to call it the
  result of heating without a separate edge.
- GDT698 fixes the two exact `ykaiin` occurrences and finds two admitted
  participant frames, two self-replays and zero cross-occurrence replay. The
  action surface does not determine a participant frame or output label.
- GDT701 supplies the immutable eleven-edge/nine-component atlas, its exact
  target ordinals and the byte-frozen token, line and span projections.
- `src/V75_11_TARGET_RIGHT_CONTEXT_SPECS.tsv` fixes all eleven expected
  outcomes, anti-skip positions, strongest exclusions and forbidden
  inferences before C012 is built.

GDT388 remains an invalid, non-score-ready acquisition protocol. It supplies
no grounding evidence for C012.

## Complete-action right-context census

The unit of inspection is not the next raw token. For every inherited edge
C001–C011:

1. locate its exact GDT701 target action;
2. reproduce the complete containing GDT695 `ACTION_CLAUSE`;
3. move to the immediately following clause only after that full action has
   ended;
4. select the first semantic token of that clause, or record `END_OF_LINE`;
5. forbid every later token listed by the specification's
   `anti_skip_ordinals` from replacing that first item.

This matters at C011. Free `dy#7` is structural closure inside the complete
`ytedy#6–dy#7` action clause. The first semantic item after that full clause is
therefore `checthedy#8`, which is another action; neither `dy#7` nor the later
`ls#9` can become a result label.

The exhaustive expected partition is:

| right-context class | count | members |
|---|---:|---|
| `NOMINAL_BLOCK` | 7 | C001, C003, C005, C006, C008, C009, C010 |
| `ACTION_CLAUSE` | 3 | C004, C007, C011 |
| `END_OF_LINE` | 1 | C002 |

The seven nominal cases remain distinct:

- C001: `olpchedy`, high finished-result state with a concordant written
  wood-powder patient — sole C012 candidate;
- C003 and C008: `kain`, working state-like but without a material head;
- C005: `ltaiin`, material-bearing but discordant wood after the bound
  Arzneikompositum;
- C006: `or`, materially compatible with a drug share but not independently
  typed as a finished result;
- C009: `otarar`, a cold-source lineage label rather than a finished heating
  output;
- C010: `okal`, a raw-material/preparation register without finished-result
  status. The later `kchody#5` may not be substituted for it.

Thus a nominal right context, material compatibility or finished-state wording
alone is insufficient.

## C012 admission gates

C012 can be admitted only if all of the following remain exact:

1. `f105v.1#4 ykaiin` is the complete target action and `#5 olpchedy` is the
   first semantic item after it, with zero intervening semantic items.
2. GDT687 independently retains `#5` as high-confidence
   `NOMINAL_FINISHED_RESULT_STATE`.
3. The already written C001 patient at `#3` is the local wood-powder material,
   and the inherited whole-token reading of `#5` retains a concordant
   wood-powder result head.
4. Both negative axes below reject a portable default.
5. GDT689 continues to forbid a productive sister or suffix rule.
6. The old GDT682 result prose is recorded as prior prose, not counted as new
   support.

If admitted, the exact edge is:

```text
edge_id         C012
component       M002
locus           f105v.1
source node     #4 ykaiin, inferred action output
target node     #5 olpchedy, written nominal result-state label
support tier    B_WORKING_LOCAL
relation class  ACTION_OUTPUT_TO_WRITTEN_RESULT_STATE
admission basis OCCURRENCE_BOUND_MATERIAL_CONCORDANCE_CONTRAST
portability     OCCURRENCE_BOUND_ONLY
```

The word *written* modifies the `olpchedy` position, not the action-to-result
relation. That relation remains inferred. C012 therefore cannot be promoted to
A-minus merely because its target token is physically present.

## Symmetric 2×2 negative contrast

### Same action surface, different right context

| case | admitted input | first semantic item right of full action | decision |
|---|---|---|---|
| `f105v.1#4 ykaiin` | C001: `#3 olpcheey`, dry bound wood powder | `#5 olpchedy`, high finished wood-powder result | C012 candidate |
| `f86v6.25#5 ykaiin` | C006: `#4 qodar`, measured drug share output | `#6 or`, drug portion without finished-result typing | hold |

This rejects `YKAIIN → OLPCHEDY`, `YKAIIN → finished result` and any fixed
right-output default.

### Same result surface, different left context

| case | immediately preceding action | material relation | decision |
|---|---|---|---|
| `f105v.1#5 olpchedy` | `#4 ykaiin`, heating the C001 wood powder | concordant | C012 candidate |
| `f105v.14#4 olpchedy` | `#3 qokaiir`, take hot drug share III | discordant with wood-extract powder | hold |

This rejects `ACTION → adjacent OLPCHEDY`, a portable OLPCHEDY output role and
an adjacency rule. The second occurrence is a genuine negative control, not a
second edge.

## Graph update and practical rendering

C012 adds only the nodes `f105v.1#4` and `#5`; `#4` is already an M002 node.
M002 becomes a bounded input–action–written-result chain:

```text
#3 olpcheey --C001--> #4 ykaiin --C012--> #5 olpchedy
```

The permitted practical reading may expose the relation editorially:

> Das trocken gebundene Holzpulver, Form II, auf Stufe III erhitzen;
> [geschriebener Resultatzustand:] fertiges Holzextraktpulver.

It may not add extraction as an operation, rename `opchedaiin#6` or
`dairody#7` as the same output, carry the material into `ypcheddy#8`, or call
the shared `olpche*` spelling a productive morpheme.

## Decision rule and validation invariants

Pass requires all of the following:

- exactly eleven target-action contexts, each consumed once;
- the exact `7 NOMINAL_BLOCK / 3 ACTION_CLAUSE / 1 END_OF_LINE` partition;
- exactly one complete gate match, C001 at `f105v.1#4 → #5`;
- both `ykaiin` cases and both `olpchedy` cases reproduced symmetrically;
- both portable defaults explicitly rejected;
- exactly one new edge, C012, with `B_WORKING_LOCAL` and occurrence-only
  portability;
- no skipped first semantic item, adjacency fallback or later-label
  substitution;
- all eleven inherited edges and nine components otherwise preserved;
- all 479 token glosses, 51 line translations and three bound spans
  byte-identical;
- zero new or changed word meanings, operations, pages or morphological rules;
- zero `f84` or `f84r` access; and
- GDT388 intake still invalid and not score-ready.

Fail or hold C012 if another context passes the same gate, if either negative
control must be bound, if material concordance depends on a newly invented
head, if GDT687's nominal type is treated as a producer link, or if the old
GDT682 prose is counted as an independent witness.

## Claim ceiling

V75 may add one B-tier, occurrence-bound editorial relation from the output of
`f105v.1#4 ykaiin` to the written nominal result-state label `#5 olpchedy`.
The old German meanings and old result sentence remain inherited working
semantics. The experiment does not establish a YKAIIN output rule, an
OLPCHEDY role, productive `olpche*` morphology, plaintext, language, historical
lexemes, a specific ingredient or a decipherment.
