# IDEA418 V2 — explicit filter-and-receiver constructor (development only)

Status: `RAW_UNREVIEWED / V2_DEVELOPMENT / NOT_SELECTED`. The original raw
card and the three-hypothesis dossier are preserved. This file is a bounded
worked construction, not a translation claim and not an executed experiment.

## Exact owning text and scope

The complete report-owned ZL3b paragraph is the seven-line W56 excerpt
`f80v.7`–`f80v.13` in
`research_registry/proposals/translation_programs_20260912/work/W56/COMPLETE_PARAGRAPHS.md`.
The source file SHA256 at review was
`4c8a1c9ff04021c9f424a72ec9b673ff1666290d27ebf031af1fff6bf8cb5557`.
The exact ZL3b lines are:

```text
f80v.7  polshol tchey qokol shedy qotshey saly kchey stolpchy
f80v.8  olteedy qokaiin shedy qokain sheol qokchdy qokchdy qoty dy
f80v.9  tchdy qol tol tal taldain chckhy qokal dol checthy qokal ly
f80v.10 sol sheey qokaiin shcthy dolshedy qokal shecthy qotainol
f80v.11 tol sheedy qokar olky rorcheey sheckhy qotain chedy rol
f80v.12 ycheol kain shey qokain chedy qokol olkain sh{cthh}y l
f80v.13 lor ar ol olor chey koldy
```

IT2a is an alternate reading of this same manuscript paragraph, not a second
witness. Its relevant differences are `chcthy` for ZL `chckhy` in `.9`,
`qotain ol` for ZL `qotainol` in `.10`, and `shcthhy` for ZL `sh{cthh}y` in
`.12`. V2 owns the ZL spelling above and records those variants without
pooling them as independent evidence.

## One finite content hypothesis

This is a deliberately strong, source-independent working hypothesis so that
the constructor has content to predict. It is not observed in the manuscript:

* `qokaiin` introduces a material input `I`; a newly written input supersedes
  the active filtered state.
* `qokain` introduces the output of a same-line input when one exists. If no
  same-line input exists, it introduces a fresh output whose provenance is
  unbound in this paragraph. This keeps the `.12` occurrence explicit rather
  than silently making it the `.10` input.
* `qokchdy` is the physical operation `FILTER`: it applies the same filter or
  separation operation to the current material, and its result becomes the
  current material. Therefore consecutive occurrences form a chain.
* `qoty` is the explicit condition `CLEAR_ENOUGH`, attached to the most recent
  FILTER result. This names a condition; it does not claim that the text says
  a numerical threshold or a particular visual test.
* `qokal` introduces a `RECEIVER_VESSEL`. The first occurrence in a line
  creates a vessel binding for that line; another `qokal` in the same line
  reasserts the same vessel. A later line creates a new vessel. This is an
  explicit frame rule, not an inference that repeated spelling always names
  one physical object.
* All remaining groups remain unresolved observations. They are not silently
  made into path, check, closure, agent, or scope operators. In particular,
  `dy`, `ly`, and `l` are not treated as closes merely to consume them.

The filter, clear-enough condition, and vessel are guessed semantic values.
The only observed facts are the written forms, their order, repetition, the
complete paragraph boundary, and the two transcription variants above.
Material identity, vessel identity, agent, filter medium, and whether the
condition is reported or commanded remain unknown.

## Deterministic reduction rules

The executable reducer is
`research_registry/work_batches/ten_hours_20260915/IDEA418_V2_REPEATED_APPLICATION.py`.
It emits the trace in
`research_registry/work_batches/ten_hours_20260915/IDEA418_V2_TRACE_20260920.json`.
The rules are global and occurrence-independent:

1. A `qokaiin` allocates a typed input occurrence. A following same-line
   `qokain` allocates an output derived from that input. A `qokain` without a
   same-line input allocates a fresh output with explicit `UNBOUND_PRIOR`
   provenance.
2. `qokchdy` consumes `current_state` if one exists, otherwise the current
   material, and produces a new state with operator `FILTER`.
3. `qoty` attaches `CLEAR_ENOUGH` to the latest state and annotates the latest
   FILTER event with that condition.
4. The first `qokal` in a line allocates a fresh `RECEIVER_VESSEL`; later
   `qokal` groups in that same line refer to the line's vessel. A line boundary
   ends only this vessel frame. It does not reset the item, state, or operation
   trace. A new `qokaiin` explicitly replaces the active material state.
5. Every other group is emitted as `UNKNOWN_GROUP` with its locus and ordinal.

This makes the same spelling/referent assumption visible: only the declared
same-line vessel frame shares a target. Cross-line `qokal` occurrences do not
share a vessel merely because their spelling is identical.

## Worked states for the two proposed clauses

For `f80v.8`, the reducer gives the following complete semantic events while
retaining all nine written groups:

```text
qokaiin  -> INPUT I0
qokain  -> OUTPUT O1, from I0
qokchdy -> FILTER(O1) = S0
qokchdy -> FILTER(S0) = S1
qoty    -> condition CLEAR_ENOUGH(S1)
```

The other four groups on this line (`olteedy`, `shedy`, `sheol`, `dy`) remain
unknown. The content prediction is concrete: the second filter consumes the
first filter's result, rather than starting a fresh operation. The condition
belongs to `S1`, not to an invented prior noun.

For `f80v.9`, all eleven written groups are retained. The two occurrences of
`qokal` produce:

```text
qokal(group 7)  -> RECEIVER_VESSEL T0 receives/references S1
qokal(group 10) -> reasserts the same T0 for S1
```

The intervening `tchdy qol tol tal taldain chckhy dol checthy` and terminal
`ly` remain unresolved. The explicit consequence is a repeated reference to
one receiver in this clause, while the preceding line's filtered state is
carried into it. That is a hypothesis about content and reference, not a
claim that the target's physical vessel is independently visible.

Two further checks show how the rule behaves without extra local exceptions:

* In `.10`, `qokaiin` starts a new input `I2`, and its `qokal` creates a new
  vessel `T1`; it cannot inherit `T0` from `.9`.
* In `.12`, `qokain` has no same-line input, so it is `O3` with explicit
  `UNBOUND_PRIOR` provenance. The reducer does not silently make it the result
  of `.10`.

The trace contains 60 groups: 2 `qokaiin`, 2 `qokain`, 2 `qokchdy`, 1
`qoty`, and 3 `qokal` recognized by the constructor, plus 50 retained
unknown groups. Thus every occurrence of the proposed operation, condition,
input/output, and target is reduced, while no unresolved group is used as
semantic filler.

## Concrete rival and changed outcome

The fixed rival is an independent-entry model over the same written forms:
each `qokchdy` starts a fresh FILTER input and yields an unrelated result, and
each `qokal` allocates a fresh receiver, including the repeated `.9` token.
For the same two clauses it predicts two independent filter results and three
receivers (`T0`, `T1`, `T2`), whereas V2 predicts the chain
`O1 -> S0 -> S1` and two receivers (`T0` in `.9`, `T1` in `.10`). The existing
trace's `independent_entry_rival` records this changed outcome.

This is a prospective discriminator only. No admitted observation currently
identifies a filter, a clear-enough condition, a vessel, or a physical
participant. A future already-exposed complete clause could favor V2 only if
it independently writes a reusable result/target relation that the rival
cannot express under its fixed fresh-entry rule. The current paragraph itself
shows the structural trigger (a consecutive repeated `qokchdy` and a
same-line repeated `qokal`), but not its meaning.

## Counterexamples and limits

The strongest retained counterexample is IDEA382, the source-owned f82r P3
proposal in `research_registry/proposals/raw_f82r_salt_sponge_expectation.json`.
It also requires repeated action after a material change, but its proposed
content distinguishes dissolution from absorption and expected from actual
weight. That source system does not license FILTER or a receiver vessel in
f80v; importing its salt/sponge entities would be source conflation. It shows
why a repeated action alone cannot establish this V2's physical operation.

GDT412 (`experiments/yolo/gdt412_chd_process_core_completion/REPORT.md`)
keeps CHD at a provisional `BEARBEITEN` core and leaves concrete objects and
technique to local wrappers. GDT769
(`experiments/yolo/gdt769_liquid_process_role_identity_dispatch/REPORT.md`)
explicitly keeps lexical identities and substances open despite contextual
roles. GDT792 (`experiments/yolo/gdt792_target_masked_image_form_host_transfer/REPORT.md`)
shows that repeated `okal` form/host behavior does not establish participant
identity. These are counterevidence to treating the V2 content labels as
observed, not reasons to retrofit more opaque fields.

The exact unresolved debt is therefore 50 groups plus the physical identities
and agent of the 10 recognized semantic occurrences. The executable result is
a deterministic, content-bearing hypothesis with a rival outcome; it is not a
complete reading or a semantic validation. No new target data, images,
reserves, route, ledger, decoder, manifest, or publication was used.
