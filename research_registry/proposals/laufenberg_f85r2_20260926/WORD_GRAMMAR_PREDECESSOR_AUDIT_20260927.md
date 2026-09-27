# Existing word grammar: bounded primary audit

2026-09-27. Exploratory reuse audit for the f68r2 rings and complete f89v1.13–20
paragraph. No decoder, model fitting, new image, reserve opening, or semantic
assignment. The current route and composition/variants topics were read first;
the experiment reports below, rather than imported status labels, determine
the limits. This audit is distinct from the root agent's full packet application.

## What can already be used

| Primary result | Positive knowledge to retain | Constraint on the present reading |
|---|---|---|
| [GDT282](../../../GDT282_OUTER_WRAPPER_CLASS_TRANSFER_REPORT.md) | Full opaque wrapper identity adds information beyond presence across held folios, sections and hands; positive in 5/6 sections and 3/4 powered hands. | Keep wrapper identity. `q_flag` is exactly `wrapper=q`, not an independent second feature. Individual `ch` one-versus-rest gains are negative in all four reported regimes, so the full-class result cannot be advertised as a separate demonstrated `ch` function. |
| [GDT286](../../../GDT286_HOST_TO_WRAPPER_TRANSFER_REPORT.md) | Wrapper choice depends on exact host and position. Voynich host gain is +0.1298 bits/event and host×position adds +0.0320. | A surface family is not a license to delete q/ch without retaining host and position. The null is low mobility (411/8448 changed IDs in world 0), a stated limit. |
| [GDT318](../../../GDT318_GLOBAL_WRAPPER_ENTRY_STATE_REPORT.md) | For 126 sufficiently supported exact cells, line start and preceding-DY jointly improve wrapper prediction by +0.034597 bits/event. Shared s×line-start and q×preceding-DY coefficients are positive in all 91 folds. | Retain physical position and preceding state. These are tendencies conditional on known cells, not mandatory grammar, meanings, or an explanation of every q. |
| [GDT326](../../../GDT326_HOST_COORDINATE_COMPOSITION_REPORT.md) | The fixed independent coordinate-factorization models fail on 315 new host×coordinate combinations across 76 held folios. | Retain exact joint compatibility; do not generate unseen combinations merely because all pieces exist separately. This is a failure of the fixed models, not a proof that all composition is absent. |
| [GDT915](../../../experiments/yolo/gdt915_terminal_lr_phrase_transfer/REPORT.md) | Same-terminal r/l co-variation transfers for selected known two-group phrase families. | `okar ar` / `okal al` and `okar otar` / `okal otal` are among nominated families, but mixed endings remain. No universal agreement, case, number, or meaning follows. |
| [GDT916](../../../experiments/yolo/gdt916_unseen_lr_stem_pair_transfer/REPORT.md) | The known-phrase result survives as such. | Generalization to unseen ordered stem pairs was not established in the adequately powered primary category: 468 occurrences/411 pairs/45 leaves; conditional tail rank 450/1025. Do not transfer the GDT915 finding to a new ring phrase by analogy. |

The inherited statistical comparisons above are reported within their original
contracts. They are not new significance tests or project-wide probabilities.
All transcriptions remain alternate readings of one manuscript.

## Actual frozen decomposition is available, with explicit parser scope

The unchanged read-free function
[`run_gdt012_core_semantic_atlas.py::strip_layers`](../../../run_gdt012_core_semantic_atlas.py)
uses the fixed ordered inventory `che, ch, sh, t, s, d, q`, removes at most one
initial member when a nonempty remainder exists, and then removes terminal
`dy` only when the remainder has more than two characters.

The unchanged read-free function
[`run_gdt062_right_family_register_renderer.py::preparse`](../../../run_gdt062_right_family_register_renderer.py)
then removes final `m` if a nonempty host remains, uses the ordered right
inventory `aiin, air, ain, ar, al`, and tests inner `d` after `ch/che/sh`.
The separate `parser(source)` function learns O/OT licensing from its input.
Calling that learner on the current paragraph would be a new fit; it is not
needed to reuse `strip_layers` or `preparse` and was not done here.

Direct execution of the two unchanged functions gives:

| Exact form | Wrapper | Host before O/OT-frame stage | Right family | DY/B3/inner-D |
|---|---|---|---|---|
| `okoaiin` | NONE | `oko` | `aiin` | 0/0/0 |
| `okaiin` | NONE | `ok` | `aiin` | 0/0/0 |
| `qokaiin` | `q` | `ok` | `aiin` | 0/0/0 |
| `chokaiin` | `ch` | `ok` | `aiin` | 0/0/0 |
| `okar` | NONE | `ok` | `ar` | 0/0/0 |
| `okor` | NONE | `okor` | NONE | 0/0/0 |
| `okol` | NONE | `okol` | NONE | 0/0/0 |
| `okeo` | NONE | `okeo` | NONE | 0/0/0 |
| `okey` | NONE | `okey` | NONE | 0/0/0 |

These are outputs of one historical operational parser, not identified
morphemes. The `okar` versus `okor/okol` asymmetry follows from its fixed right
inventory. GDT915 separately drops final r/l for its own test; the two
segmentations must not be conflated into one proven grammar.

Selector-first queries of the existing GDT062 inventory also recover already
frozen, full-parser analyses at the actual f89v1 locations:

| Locus/group | Token | Wrapper | Local frame | PAGE_HOST | Right |
|---|---|---|---|---|---|
| f89v1.14 G7 | `okoaiin` | NONE | NONE | `oko` | `aiin` |
| f89v1.16 G1 | `qokaiin` | q | NONE | `ok` | `aiin` |
| f89v1.16 G8 | `okaiin` | NONE | NONE | `ok` | `aiin` |
| f89v1.14 G5 | `okol` | NONE | NONE | `okol` | NONE |

Reproduce the guarded lookup with:

```sh
./vmanus-exp query-tsv gdt062_right_family_inventory.tsv --selector page --allow f89v1 --columns locus,group_index,token,wrapper,inner_d,local_frame,page_host,right_family,dy_closure,b3
```

The query selects 56 legacy rows; it is not the complete current paragraph.
The GDT062 inventory has no f89v1.18 row, so it does not itself provide an
already-stored `chokaiin` analysis at the present location. Its read-free
preparse still supplies the formal result above. A narrower GDT276 census
contains only 22 f89v1 groups, illustrating why old event inventories must not
stand in for the complete source packet. A first incorrectly comma-joined
multi-value selector returned zero rows; that was a query-format error, not
absence of evidence. `--allow` is repeatable.

The stored GDT327 operational grammar further has an explicit
`UNLICENSED_OR_UNKNOWN_NO_COORDINATE_OR_HOST_FACTORIAL_BACKOFF` policy and
126 executable cells covering 5607/8448 historical events. It is a joint-tuple
renderer, not a universal word parser. No GDT327 source inventory was opened
for this audit.

## Meaning constraints already learned about okaiin

[GDT815](../../../experiments/yolo/gdt815_referent_property_discrimination/REPORT.md)
keeps `okaiin` property, thermal polarity, taste, possession, powder and copula
accounts distinct and unconfirmed. Exact `okol` and `otedy` label/prose chains
provide written candidates for antecedents; they do not prove reference,
picture ownership or part-whole relations. `ychey`, `qokain` and `solkeey`
remain unidentified. Another compatible property slot or warm/cold/bitter
substitution is explicitly insufficient to reopen meaning identification.

This existing result does not assign any of those meanings to `okoaiin`.
The frozen parser actually preserves a different host, `oko`, from the `ok`
host in the other three focal forms. No deletion of the extra o, shared
gloss, solar case form or solar derivation is justified by this audit.

## Consequence for the current work

Reuse the fixed representations on the complete already-open source packets,
retain whole raw forms and parser disagreements, and expose any missing
coverage rather than silently smoothing it. This turns the old grammar into
an explicit constraint on current hypotheses. It does not itself choose a
historical reading. The exact function application is independent of any
chosen SUN gloss, but not an independent test of SUN meaning.

No new RAW idea was added: the bounded audit supports the already authorized
application, not a genuinely distinct new meaning-bearing experiment. Existing
GDT815 stops and GDT916 limits remain unchanged. Confirmed words: zero.
