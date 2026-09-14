# Luna pipeline pilot — 2026-09-14

The authorized producer/worker/critic pipeline has completed its first batch.
Three `gpt-5.6-luna` workers used high reasoning and fresh bounded context
(`fork_turns="none"`); root chose the scope, reviewed claims and published.
The reusable helper validates source bindings, emits task briefs and collects
result files. It does not select scientific winners. No new experiment or
translated word resulted from this pilot.

## Actual candidate review

The original three proposals are preserved, including their errors. The
[producer's follow-up audit](PRODUCER_AUDIT.json) records corrections separately.
The [critic](CRITIC_RESULT.json) initially examined the sources without producer
output. Root subsequently requested explicit corrections to two overclaims:
phrase recurrence does not select component meanings, and variable line position
does not refute a fixed grammatical role under flexible word order. This is
independent initial inspection, not independent meaning confirmation.

| Candidate | Proposed consequence | Observed source facts / review | Decision |
|---|---|---|---|
| IDEA000278: qoteedy/qokeedy state/process order | Repeated direction and successor behavior across paragraphs/pages | Exact qoteedy is confined to f77r in this packet. Same-line qoteedy/qokeedy occurs at f77r.11, .14 and .17. The f85r1 example substitutes other forms. The literal difference is t/k, not eedy/teedy. | Not selected. The advertised second-page evidence is absent; the semantic model was not tested. Whole-phrase/position-conditioned grammar remains a rival. |
| IDEA000279: ol shell preserves content kernels | Kernel reuse plus neighbor reuse on multiple pages | olshedy qokeedy really recurs at f77r.23 and f85r1.4 in ZL/IT. Productive formal morphology or stored phrases also allow that result. | Not selected. A change in the proposed content relation must predict an observable difference beyond spelling/collocation. |
| IDEA000280: common content spine across readers | Invariant ordered kernels despite different spacing/marks | GDT944 already documents the split/fused f80v.32 variants. The packet lacks ZL/IT separator flags; RF retains raw flags. All readers describe the same manuscript. | Not selected as a semantic experiment. Alignment can audit rendering but does not identify content. |

These are source and design reviews, not three failed decipherment experiments.
No global exclusion of these mechanisms follows. The first proposal has a
concrete factual defect; the other two lack the proposed semantic discrimination.
Original raw records remain available as IDEA000278–280 with append-only assessed
reviews. No gloss, prefix, source or existing decoder was changed.

Root checked primary GDT608, GDT763, GDT944, P21 and W16 reports as relevant to
the selection decision. GDT608 already retains formal composition **and** whole-form
residuals; repeating form reuse does not supply a new meaning bridge. P21 and W16
also show why a stipulated role or a coherent combined rendering alone is
insufficient. Historical GDT763 word values remain working assumptions.
This is bounded predecessor review, not an exhaustive novelty proof.

## Data and reproducibility

[PACKET.json](PACKET.json) was written before delegation and binds eight inputs
by SHA256. The manuscript input is three previously exposed physical leaves:
f77r.9–24, f80v.30–37 and f85r1.1–6, totaling 30 loci. Six complete ZL/IT paragraph
records are alternative transcriptions of three paragraph locations. RF is the
matching line union, not three new independent paragraphs. Prior project exposure
was explicit. No images, reserved leaves, f84/f84r or unadmitted f116v were opened;
nobody was contacted. Independent meaning-confirmation capacity in this pilot: 0.

The exact-form audit below checks the factual premise of P01 over **all six**
paragraph records. It reports source IDs, counts including zero and same-line
orders. It is a post-proposal factual audit; near-adjacency and a statistical
endpoint were never defined. It is not a registered order test, and no safe-space
or meaning inference is made from the simplified word arrays.

```sh
python3 tools/luna_batch.py validate research_registry/work_batches/luna_pilot_20260914/PACKET.json
python3 tools/luna_batch.py brief research_registry/work_batches/luna_pilot_20260914/PACKET.json produce
python3 tools/luna_batch.py collect research_registry/work_batches/luna_pilot_20260914/PACKET.json
python3 research_registry/work_batches/luna_pilot_20260914/audit_exact_forms.py
python3 -m unittest tests.test_luna_batch tests.test_workflow_docs tests.test_work_context tests.test_work_preflight tests.test_repository_infrastructure
```

[EXACT_FORM_AUDIT.json](EXACT_FORM_AUDIT.json) contains the literal source audit.
[COLLECTED_RESULTS.json](COLLECTED_RESULTS.json) stores the three primary task
returns; the producer audit and exact-form audit are separately recorded bounded
follow-ups. `DONE` means a valid handoff package, even when no hypothesis is selected.
[RECEIPT.json](RECEIPT.json) binds the final code, results and review inputs.

## Operating decision

Keep the small automation and Luna high division of work. Root must still inspect
the actual discriminator and a close rival: the first round exposed errors that
JSON validation cannot detect. Future producer briefs should require exact source
forms and a plausible grammar/phrase rival; semantics cannot win merely against
randomly unrelated words. Hypothetical content remains allowed without a confirmed
anchor. A new joint reading may predict raw form/ordering consequences under
explicit shared assumptions; do not demand a translated relation in advance.

There is no measured token-saving or research-throughput multiplier from this
single engineering-heavy pilot. The 30-minute budget includes setup, handoffs,
implementation, review, checks and publication; timing and actual checks are in
the receipt. The new helper has four focused tests; 58 existing workflow,
navigation, preflight and infrastructure tests also passed. The global checker's
seven pre-existing GDT600 binding failures remain unrelated and are not repaired
or presented as a global pass. Exact staged privacy and scope checks are required
before publication.

No new scientific experiment is selected. Next active research should use the
existing idea registry and require a concrete shared content/form contrast after
primary review; do not rerun these three sketches, expand a failed role contract,
or add more helper infrastructure by default. Workers finish when their assigned
batch finishes; no background research between turns has been started.
