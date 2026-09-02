# GDT741 report — ID-free boundary/relay grammar

## Outcome

The thirteen manual GDT740 exceptions can be replayed by one local feature
grammar instead of an occurrence lookup. The adjudicator receives a whitelisted
feature record with no dispatch ID, locus or GDT740 outcome field. Across the
complete inherited deck it reproduces:

- all 103 binding-contact axis/carrier flag pairs;
- all eight old state/result cases: one result retained, seven downgraded;
- all 95 target functions;
- all 202 renderer patches; and
- all twenty cached passage renders.

The inherited 104th ring row remains bookkeeping-only nonbinding conflict
evidence; GDT741 does not independently predict that label. The active renderer
itself does not change: 36 axis-specific, 43 carrier-bound and 56 specific
positions remain, while 146 positions remain fully open.

This moves the working theory from “thirteen places were manually corrected”
to “one explicit local feature system compresses all thirteen corrections and
surfaces its counterexamples.” It remains fitted in-sample: six role-bearing
rules are singletons in this fixed sample.

## What the grammar actually sees

The adjudicator does not receive occurrence identity, folio or line. It does
receive the target's current complete-whole feature class and local geometry:

- which axis or carrier the target is looking for;
- what the immediate and radius-two hosts currently carry;
- whether roles come from one flank or incompatible flanks;
- whether a single host covers a requested compound carrier;
- whether a middle cell is known, exact, its own unit, a strict head or a
  boundary; and
- whether quality or carrier content continues through that middle cell.

GDT740's 103-contact artifact alone lacked the opposite unselected R1 field and
the middle field's tags. GDT741 supplies those from the already cached GDT739
windows before identities and prior outcomes are stripped from the decision
records. No new transcription or page is read.

The two active relay middles and the opposite-axis veto field were not positive
GDT739 anchors. Their tags can act here only as relational continuity or a
negative conflict cue. Separate eligibility fields in the contact artifact
prevent this use from silently promoting them to standalone hosts.

## Ten ordered registry entries

| rule | effect | observed support | working confidence |
|---|---|---:|---|
| G00 inherited nonbinding conflict | audits the rival cue; no dispatch | 1 ring row | high internal |
| G01 reverse closure crossing | blocks the close host and the field behind it | 1 target | provisional singleton |
| G02 bilateral role split | prevents cross-flank axis/carrier fusion | 1 target | provisional singleton |
| G03 opposite axis rival | opens a disputed state axis; carrier may remain | 1 target | provisional singleton |
| G04 pure amount ownership | amount stays with its own field; carrier may bind | 1 target | provisional singleton |
| G05 single-host composite carrier | rejects carriers assembled from hosts | 2 targets | supported internal |
| G06A tight axis relay | continues one exact quality axis through the middle | 1 target | exploratory singleton |
| G06C tight carrier relay | continues the full requested carrier | 1 target | exploratory singleton |
| G07 direct process support | retains result only with an attached PROCESS host | 8 cases | supported internal |
| G08 zero export | blocks lexical/component/plaintext promotion | all outputs | hard guard |

The predicates live in `src/run.py`; the TSV is their ordered description and
confidence ledger. G00 is inherited bookkeeping and G08 is a hard output guard,
not a learned decision predicate.

G07 is the strongest discriminating block: one positive and seven negative
cases are separated by direct process support. G05 has two independent target
triggers. G01–G04 and both relay rules remain compact explanations of one local
case apiece and should not be mistaken for unseen-page confirmation.

## The two strict relays

Radius two remains silent by default. Only two contacts satisfy the strict
continuity grammar:

- `qokeey–okeey–lain` at `f116r.17`: host and middle carry the same single
  current hot-quality signature, so the AXIS role relays;
- `pcheol–sholoiin–cthor` at `f52v.7`: host and middle both cover the requested
  material carrier, so the CARRIER role relays.

Both require a reader-exact known middle cell that emits its own unit, is neither
a strict head nor another target, and has `middle_barrier=OPEN`; they also
require an attested exact full frame, a single selected role and matching formal
direction. Neither frame has a second occurrence. Their value is that the
feature conditions are now explicit and produce counterfactual candidates;
their weakness is that each still has one observed trigger.

The useful near-collision `qokeey–qokedy–lkaiin` has the same current HOT
signature in host and middle, but it fails three separate gates: the middle is
`CLOSE`, it is not reader-exact, and the exact full-frame count is zero. It is
therefore evidence that semantic continuity alone is too permissive, not an
isolated proof for any one boundary feature.

## Six open collisions instead of six silent choices

The relaxed continuity channel finds eight possible roles. Two are the active
strict relays. The other six occur on five currently open targets:

| target | relaxed role |
|---|---|
| `G739-D0040` | AXIS |
| `G739-D0075` | AXIS and CARRIER |
| `G739-D0184` | AXIS |
| `G739-D0143` | CARRIER |
| `G739-D0164` | CARRIER |

Activating all six roles would move specific positions 56→61 and open positions
146→141. GDT741 deliberately does not do that. They are the concrete next
questions: five cases where a broader continuity rule predicts more speech and
therefore risks five renderer false positives.

Their five unique geometries are sent through the GDT388 intake format. The
packet correctly returns `INVALID_PACKET`: zero eligible edges, no external
capacity, no held-folio split and no mobile-null evidence. The packet exposes
the candidates; it does not certify them.

## Renderer consequence

GDT741 changes the *reason* for the renderer but not its visible output. The
GDT740 rendering counts replay exactly:

| channel | positions |
|---|---:|
| axis-specific | 36 |
| broad carrier bound | 43 |
| any specific local dispatch | 56 |
| fully open | 146 |

This is still useful. The feature compression exposes counterfactual collisions
that an occurrence list leaves hidden. It also makes the remaining fragility inspectable: the five
open-collision targets and the six singleton role rules are now the places to
attack, not an undifferentiated 202-position patch.

The passage reader preserves surrounding cached German working defaults only as
a cellwise audit. It does not turn them into sentences, and GDT741 adds no
ingredient, plant, action, unit, disease or cure meaning.

## Best next move

Use the five open-collision targets and their closest held analogues as a
focused visual/local audit. The aim is to choose among a stricter formal-
direction grammar, a broader semantic-continuity grammar, or a third boundary
feature. A useful next rule must explain more than its seed occurrence and must
not manufacture a fluent phrase merely by joining neighboring tags.

No new page is required for that pass. If the five cases remain genuinely
ambiguous, they stay open; the current active renderer is already reproduced by
the executable grammar.

## Reproduction

```bash
python3 experiments/yolo/gdt741_local_attachment_boundary_relay_grammar/src/run.py
python3 experiments/yolo/gdt741_local_attachment_boundary_relay_grammar/src/validate.py
./vmanus-exp check-edge-packet experiments/yolo/gdt741_local_attachment_boundary_relay_grammar/artifacts/GDT741_GDT388_OPEN_COLLISION_EDGE_PACKET.tsv
```

The validator performs a byte-identical clean-directory rebuild. The final
relation command is expected to return `INVALID_PACKET`.
