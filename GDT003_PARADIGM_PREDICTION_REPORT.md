# GDT003 paradigm prediction report

Status: **NOT DISTINGUISHABLE FROM STRING STATISTICS**.

GDT003 asks only whether recurrent formal transformations combine strongly
enough to predict an unseen fourth cell. It assigns no morpheme, operator
meaning, part of speech, semantic role, language, plaintext, or translation.
The nearest-basic-EVA forms below are lossy displays of manual source groups.
ZL3b, IT2a, and RF1b are alternate readings, not replications.

## Corpus and learned transformations

The primary analysis retains 18,760 physical groups and 4,394 form types for
which all three readings agree on surface and source-group topology. It
excludes 20,704 union keys with a missing, alternative, or topology-disagreeing
reading. The f84r formal holdout is filtered before retention.

Every predeclared GDT002 operation has at least five exact type pairs:

| Transformation | Exact stable pairs | Empirically recovered attachment |
|---|---:|---|
| prepend `q` | 290 | LEFT_EDGE |
| initial `d→s` | 72 | LEFT_EDGE |
| initial `o→ot` | 39 | EDGE_MIXED/local |
| append `dy` | 197 | RIGHT_EDGE |
| append `dal` | 36 | RIGHT_EDGE |
| append `dar` | 33 | RIGHT_EDGE |
| final `dal→dar` | 34 | RIGHT_EDGE |
| final `dal→dy` | 61 | RIGHT_EDGE |
| final `dar→dy` | 76 | RIGHT_EDGE |

Thus positional classes emerge from the observed edit locations: two left-edge
operations, six right-edge operations, and one local/mixed operation. This is
a formal distributional result, not a linguistic morphology analysis.

## Rectangle inventory

Across all operation pairs and stable hosts, the scan finds:

| Structure | Count |
|---|---:|
| Complete 2×2 rectangles | 44 |
| Three of four cells | 232 |
| Two of four cells | 2,673 |

Five operation pairs with at least three complete rectangles exceed 256
length- and edge-count-matched randomized transformation graphs. The clearest
pair is prepend-`q` plus append-`dy`: 17 complete rectangles and 20 three-cell
structures. Initial `d→s` plus append-`dy` has three complete and eight
three-cell structures.

These two signals do not depend on admitting ambiguous groups. In the separate
edition surfaces, `q`+`dy` has 26/24/23 complete rectangles in ZL3b/IT2a/RF1b
versus 17 in the strict all-reading intersection; `d→s`+`dy` has 7/6/8 versus
three strict rectangles. The editions remain sensitivity views of one object,
not three confirmations.

After also checking whether applying one operation changes the other's edge
rate, only these two pairs are classified `INDEPENDENT`. Eight are
`CONDITIONALLY_COMPATIBLE`, fifteen are `ORDER_DEPENDENT`, and eleven have
`INSUFFICIENT_DATA`. In particular, two operations competing for the same
right edge usually do not commute.

## Hidden fourth-cell prediction

The highest-value test excludes an entire physical folio, learns operation and
baseline statistics from the rest, generates exact fourth cells absent from
training, and only then checks the held folio.

| Evaluation | Predictions | Exact correct | Precision (95% CI) | Recall/coverage | Top-1 / top-5 correct |
|---|---:|---:|---:|---:|---:|
| Host-cell target removed globally | 72 | 37 | 51.39% (40.07–62.57%) | 30 unique forms / 4,394 = 0.683% | 31 / 37 |
| Whole-folio held | 3,527 | 9 | 0.255% (0.134–0.484%) | 9 / 2,945 novel held types = 0.306% | 1 / 2 |
| Whole-section held | 240 | 8 | 3.33% (1.70–6.44%) | 8 / 3,217 novel held section-types = 0.249% | 1 / 1 |

Nine specific folio-held forms were absent from their training corpora and
then found exactly in the named held folio:

| Held folio | Three model-visible cells | Predicted fourth | Operation pair | Held locus |
|---|---|---|---|---|
| f114 | `oeeo`, `qoeeo`, `oeeody` | `qoeeody` | `q` + append `dy` | f114r.18 |
| f34 | `ol`, `qol`, `oldar` | `qoldar` | `q` + append `dar` | f34v.4 |
| f37 | `otol`, `qotol`, `otoldy` | `qotoldy` | `q` + append `dy` | f37v.1 |
| f43 | `oty`, `qoty`, `otydy` | `qotydy` | `q` + append `dy` | f43r.3 |
| f58 | `dy`, `sy`, `dydy` | `sydy` | `d→s` + append `dy` | f58v.38 |
| f81 | `oldar`, `qoldar`, `oldy` | `qoldy` | `q` + final `dar→dy` | f81v.20 |
| f82 | `okol`, `qokol`, `okoldy` | `qokoldy` | `q` + append `dy` | f82v.13 |
| f83 | `otal`, `qotal`, `otaldy` | `qotaldy` | `q` + append `dy` | f83v.3 |
| f93 | `okcho`, `qokcho`, `okchody` | `qokchody` | `q` + append `dy` | f93v.4 |

These are genuine *model-hidden* fourth cells: the target type was absent from
the fold's training corpus. They are not newly acquired manuscript evidence;
the readings were public before computational masking.

## Strong baselines

The exact successes do not provide a comparative win:

| Evaluation | Paradigm average precision | Character KT | Visible whole-group frequency | Nearest edit |
|---|---:|---:|---:|---:|
| Host-cell | 0.7273 | **0.7780** | 0.6896 | 0.5808 |
| Folio-held | 0.1138 | 0.1148 | **0.1191** | 0.0035 |
| Section-held | **0.1650** | 0.0364 | 0.1151 | 0.0737 |

On the decisive folio split, paradigm ranking is 0.0010 AP below the character
model and 0.0053 below the strongest string baseline. Visible whole-group
frequency also has much higher folio AUC (0.753 versus 0.544). Section-held
average precision favors the paradigm score, but only eight positives exist;
whole-group frequency still has higher AUC and four rather than one top-five
hits. The section result is therefore insufficient to reverse the folio test.

The GDT001 context mixer is not assigned a fabricated isolated-form score: its
reversible decoder requires the complete canonical-locus serialization and
context. It remains the stronger whole-source benchmark, but has no comparable
missing-group API.

## Split/join and counterexamples

Only append `dy/dal/dar` receive manual split/join support in this fixed
operation set. Their host-cell tasks complete 22/55 times (40.0%), while
substring-only operation pairs complete 15/17 times (88.2%). Split/join
evidence therefore does not increase out-of-sample productivity here. This
does not negate the physical boundary evidence; it prevents using it as proof
of a predictive linguistic slot.

The principal falsifiers are:

- most apparent grids are two-cell local-similarity structures rather than
  complete rectangles;
- fifteen operation pairs are order-dependent;
- exact novel folio predictions cover only 0.306% of novel held types;
- paradigm ranking loses to strong string statistics on both the host-cell and
  folio tests;
- ambiguous readings were excluded, so the negative comparison is not caused
  by forcing uncertain surfaces;
- the transformation set was discovered before this cross-validation, so the
  results are conditional on a postselected family even though each target was
  hidden from the model.

## Conclusion

The manuscript contains real local grids and a small number of computationally
unseen exact completions. In particular, prepend-`q` and append-`dy` behave as
compatible formal edge operations more often than a randomized edge graph.
But their fourth-cell predictions do not outrank ordinary Voynich character
and whole-group statistics on the decisive folio split. The evidence therefore
does not establish an independently predictive slot algebra beyond the
manuscript's general local string regularity.

NOT DISTINGUISHABLE FROM STRING STATISTICS
