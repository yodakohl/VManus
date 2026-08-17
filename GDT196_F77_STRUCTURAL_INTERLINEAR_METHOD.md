# GDT196 — f77 structural interlinear and label-to-prose bridge

## Purpose

Produce the first exhaustive structural reading of every all-reading-stable
confirmed-prose group on `f77r`, then test the necessary bridge from the six
exposed diagram-state labels to that prose.  This is a continuation of the
GDT181 hybrid technical-compiler theory, not a new language or cipher search.

The key question is deliberately simple: if the six labels are a usable local
key, do their exact visible forms or their frozen HPR2 tuples recur in the
associated prose more than ordinary same-register exposure predicts?

## Frozen inputs and scope

- `gdt062_right_family_inventory.tsv` supplies the already frozen HPR2 parse
  of strict, exact-all-reading prose.  Every `f84*` row is rejected before
  retention; only `f77r` rows enter the interlinear.
- `gdt180_f77_process_steps.tsv` supplies the six exposed diagram labels and
  the post-hoc state scaffold.  It is not regenerated or strengthened.
- `gdt180_result.json`, `gdt182_result.json`, and `gdt195_result.json` preserve
  the state-decoder multiplicity and readable-homolog counterevidence.

The interlinear covers the 31 `f77r` lines and 193 groups that survive the
strict three-reading consensus pipeline.  Eighteen lines are complete (130
groups); thirteen retain only 63 stable groups and are marked partial.  Omitted
ambiguous/non-consensus groups are reported as outside this exact view, not
silently reconstructed.

## Structural translation

Each group is rendered as:

```text
WRAPPER? + INNER_D? + O/OT_FRAME? + PAGE_HOST + RIGHT_FAMILY? + DY? + B3?
```

Each physical line is serialized as a sequence of anonymous `FIELD[...]`
records; `DY` is displayed as an internal checkpoint and `B3` as a
probabilistic close.  This is a formal translation skeleton.  No English
lexical value is inserted into an unresolved `PAGE_HOST`.

## Label bridge endpoints

For each of the six GDT180 labels, count in strict non-`f84*` prose:

1. exact whole surface;
2. exact complete HPR2 tuple;
3. exact stripped `PAGE_HOST`;
4. the same three counts on `f77r` alone;
5. physical-folio support and example loci.

The one predeclared page-level diagnostic compares the count of any of the
six exact label surfaces in the 193 `f77r` prose groups against a
hypergeometric draw of 193 groups from the same Section B / Currier B / hand 2
stratum.  This is a descriptive exchangeability diagnostic: groups within a
page are dependent and the six labels are already exposed.

## Outcomes

- `LABEL_KEY_BRIDGES_F77_PROSE`: at least three of six label surfaces recur on
  the page, the page rate is enriched at one-sided p <= .05, and at least two
  recurrences preserve distinct non-generic HPR2 tuples.
- `STRICT_STRUCTURAL_INTERLINEAR_PARTIAL_LABEL_KEY_NOT_BRIDGED`: otherwise,
  including the present case where the exact view does not cover every group
  on the page.

The second outcome does not reject the structural compiler or the possibility
that the labels are local codes.  It says they do not currently provide a
dictionary for the prose.

## Claim ceiling

At most this experiment supplies a complete anonymous structural skeleton of
the strict `f77r` prose and a measured diagram-label/prose bridge.  The GDT180
state words remain post-hoc display labels.  No source group, PAGE_HOST,
wrapper, right family, checkpoint, or closer receives a word meaning, sound,
language, plaintext value, or confirmed translation.  `f84r` is not opened,
retained, queried, joined, or scored.
