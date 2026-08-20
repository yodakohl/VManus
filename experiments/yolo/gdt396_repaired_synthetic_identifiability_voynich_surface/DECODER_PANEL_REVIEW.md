# GDT396 independent decoder-panel pre-qualification review

Date: 2026-08-20

Decision: **HOLD**. Do not generate or decode qualification data, open a
qualification oracle, freeze this decoder panel, or generate confirmation data
from the audited snapshot. Continued blind development-only engineering is
permitted.

This was a static/read-only audit except for this report. I inspected the public
GDT396 protocol documents, GDT396 source, the four decoder sources and
attestations, public freeze/validation artifacts, and blind legacy/development
observations through `observation_api`. I did not inspect any sealed oracle,
qualification or confirmation observation, GDT395 world design/generator/oracle
or scorer, sibling history, Voynich corpus/data, `f84`, or `f84r`. No subagent
participated.

## GO findings

- The existing protocol freeze still matches every file it claims to bind. Its
  public validator reports 15/15 checks passing, and the public development
  corpus validator reports 18/18 checks passing. Those artifacts do not cover
  the later execution/scoring/decoder layer discussed below.
- No qualification or confirmation observation/claim artifact was present under
  the experiment directory. The only matching filename was the public
  `DECODER_QUALIFICATION_SPEC.md`.
- Static import/I/O review found no prohibited input path, generator/scorer
  import, network access, subprocess, or top-level file read in any decoder's
  fit/decode implementation. D396S01's only file-loading code is its explicit
  development-only `--self-test` path. The four attestations state the required
  historical blindness.
- The sources represent four materially distinguishable implementations:
  multiview record graph (D396S01), MDL component/context (D396S02),
  relation/scope topology (D396S03), and register-contrastive latent roles
  (D396S04). Method-family labels alone are not treated as proof of independence.
- All four sources genuinely accepted a two-seed training list. A blind smoke
  used W01 legacy seeds 0 and 1 (16,909 training events), five complete records
  from development seed 3960000 (58 held events), and each surface separately.
  Each decoder passed the current in-memory shape/locality checks and left the
  directly supplied model byte-identical:

  | decoder | FREE | VOYNICH | tested representation |
  |---|---:|---:|---|
  | D396S01 | PASS | PASS | `FULL_GROUP` |
  | D396S02 | PASS | PASS | `FULL_GROUP` |
  | D396S03 | PASS | PASS | `COMPOSITE_STATE` |
  | D396S04 | PASS | PASS | `FULL_GROUP` |

  Across the two blind training seeds, event IDs were unique. Record IDs did
  repeat across seeds; D396S01/D396S02 explicitly namespace them, and
  D396S03/D396S04 use `(seed, record_id)` keys. Thus the audited multi-seed paths
  do not merge same-named records across seeds.
- Held seeds are selected from the phase manifest, training blocks are fixed by
  phase, models are fitted separately by world and surface, and each held seed is
  loaded independently. These are sound foundations once the mechanical gaps
  below are repaired.

## HOLD blockers

### H1 — Boolean serialization makes binary and scope scoring wrong

All four decoders emit Python `bool` values for `predicted_bool` and
`scope_present`. `csv.DictWriter` serializes those as `True`/`False`, while
`score_decoder_phase.py` tests exact uppercase strings (`== "TRUE"`). The result
is that every serialized binary prediction is interpreted as false and every
positive scope is omitted from scoring. `run_blind_decoders.validate_claims`
also checks positive scopes only when the in-memory value equals the string
`"TRUE"`, so a Python `True` bypasses endpoint validation. `decoder_api_v2`
does not enforce Boolean spelling or type.

This is outcome-determinative. Canonicalize booleans at the API boundary (or
require exact `TRUE`/`FALSE` strings), validate them before writing and after
reading, and add a round-trip test that scores one known true and one known false
fixture. Development outputs produced by the current writer cannot qualify a
decoder.

### H2 — The advertised experiment entry points are nonfunctional

`experiment.json` advertises `src/run.py` and `src/validate.py`; both raise
`NotImplementedError`. There is therefore no executable end-to-end chronology
or independent validator behind the manifest commands. Implement the phase
orchestrator and validator before qualification.

### H3 — The executable qualification decision is not the registered decision

`qualify_decoders.py` applies generic partition/binary/ranked/scope gates but
does not implement the full frozen qualification suite:

- morphology boundary F1, productive/fossil macro-F1 and AP, no-current-
  morphology false discovery, recurring-component, disjoint-status, and
  proper-substring requirements are absent;
- the three-relation-type requirement, the decoder-wide easy-equality/simple-
  relation/schema-validity/deterministic-rerun suite, and a W10 semantic false-
  positive veto are absent;
- architecture rows are excluded from route qualification and retained only as
  ungated diagnostics; no leave-family-out BA/MCC, W10 false-positive rate,
  paired interval, or multi-constraint lead is enforced;
- a route qualifies after two non-W10 worlds pass, regardless of what it emits
  on W10; and
- `DECODER_QUALIFICATION_SPEC.md` says two independent qualified decoders are
  sufficient for a confirmation statement, while `SCORING_DESIGN.md` requires
  three. The authoritative gate must be made singular and executable.

No qualification oracle should be opened against this implementation.

### H4 — Decoder/API/execution/scoring hashes are not frozen together

The current protocol freeze binds the early interface and surface protocol but
not `DECODER_EXECUTION_SPEC.md`, `ORACLE_TRUTH_SPEC.md`,
`TRACE_DIGEST_CORRECTION.md`, `RUNNER_INTEGRATION_CORRECTION.md`,
`observation_api.py`, `run_blind_decoders.py`, `metrics.py`,
`score_decoder_phase.py`, `qualify_decoders.py`, any decoder or attestation, or
a decoder-panel/qualification validator. There is no later panel freeze
artifact.

The newly added `freeze_decoder_panel.py` does not clear this blocker. It only
checks that `DECODER_PANEL_REVIEW.md` exists, not that the review decision is
GO; it would therefore freeze this explicitly HOLD panel. It also omits itself,
`generate_paired_corpora.py`, `surface_channel.py`, the manifest entry points,
and an independent panel-freeze validator from its bindings. Its imposed
three-Sol/four-method-family composition quota also conflicts with the written
rule that model brand is not a vote quota. `freeze_claims.py` checks union-level
world/surface/seed coverage but not the complete per-decoder/table/
representation Cartesian product, actual row counts, model hashes/training
blocks, or confirmation prerequisites.

The corpus generator will generate qualification with no prerequisite artifact
check. Confirmation is protected only by a manually supplied
`--allow-confirmation` flag, not by verified decoder, route, scorer, threshold,
null, or validator freezes. The decoder runner also overwrites phase outputs and
manifests without a one-shot/frozen-state guard.

Create and independently validate one pre-qualification binding that includes
the repaired API, runner, qualification scorer/aggregator, decoder sources and
attestations, exact development selections, and absence of qualification and
confirmation blocks. Make qualification/confirmation generation and execution
refuse to run unless their prerequisite binding passes.

### H5 — The promised process and prohibited-path boundary is not mechanical

The protocol says each surface is supplied in a fresh process. The runner
instead imports a decoder once and iterates both surfaces in the same Python
process. It provides no filesystem/import/network sandbox or file-access audit.
Its path check proves only that `decoder.py` is located under the panel root; it
does not prevent that module from reading sibling decoders, GDT395 material,
sealed oracle paths, or Voynich data.

In addition, `observation_api.block_manifest()` returns full internal manifest
rows, including `oracle_relpath`, `oracle_sha256`, hidden-trace digests, and the
mapping commitment. The audited decoders do not consume those values in
fit/decode, but the blind API unnecessarily exposes them.

Run every `(decoder, world, surface)` fit/decode in a fresh restricted process,
project blind manifests to an explicit observation-only allow-list, and enforce
or attest file access mechanically. Static cleanliness of the present sources
is a GO finding, not a substitute for this runtime gate.

### H6 — Runner/schema validation is substantially weaker than specified

The runner passes `deepcopy(model)` to `decode` but hashes the untouched
original afterward. It therefore does not establish the claimed fact that the
model object supplied to decode was immutable. It also does not rerun decodes
for deterministic byte equality.

The validator does not enforce `supported_claim_kinds`, registered rank caps,
Boolean spelling, unit-type enums, anonymous/safe IDs, query-key uniqueness,
one query per attempted source/property, predicted-target count equality,
unique ranked targets, status-dependent empty fields, morphology rank
contiguity, or complete table/cartesian coverage. D396S04's
`classify_world(model)` returns private descriptor dictionaries rather than
normalized API claim rows; this is masked only because its `decode` currently
emits architecture rows.

Repair these checks and add adversarial fixture tests that must fail for each
invalid form.

### H7 — The claim/scoring path is not feasible or provenance-safe

The bounded smoke emitted 2,084–2,832 rows for only 58 events in one
representation. Projecting those first-representation densities across the
four declared representation counts gives roughly 733 million qualification
claim rows (about 18,000 gzip tables) before D396S04's extra representation-
specific rows. `score_decoder_phase.py` eagerly reads every table into a global
`groups` dictionary before scoring, so the registered panel is not operationally
scoreable at the target scale.

The scorer also trusts claim-manifest paths and metadata without checking file
hashes, row counts, decoder/model hashes, training blocks, phase bindings, or
duplicate table entries; repeated entries silently overwrite one another in a
dictionary. `merge_claim_manifests.py` and `freeze_claims.py` join a manifest
`relpath` without proving the resolved path remains inside the claims root, so
`..` path escape is accepted. Stream one context at a time, reduce redundant
per-representation emission, and validate the exact manifest and source
bindings before any oracle join.

### H8 — The registered multi-constraint comparison is not executable as stated

All event-level function/operator claims use only `PRIMARY`; no corresponding
`MULTI_CONSTRAINT` and `SCALAR_BOTTLENECK` claims share the same event endpoint,
candidates, abstention rule, and budget. Current variant rows are only
world-architecture flags.

The decoder variants are also not uniformly matched: D396S01 duplicates primary
flags as multi-constraint flags; D396S02 changes only part of the flag set;
D396S03 emits multi/scalar predictions only for `SEMANTICS_LIGHT_LIKE`; and
D396S04's nominal scalar flag function still consults equality, relation,
morphology, and schema signals for several flags. Freeze one exact endpoint and
ensure the scalar path can access only its selected scalar.

### H9 — Truth/scoring specifications disagree and final inference is absent

`ORACLE_TRUTH_SPEC.md` and the implemented partition scorer treat pipe-valued
IDs as sorted exact composite signatures. `SCORING_DESIGN.md` instead says they
are exploded into repeated rows. Resolve this before qualification so truth
units cannot change after claims are frozen.

The available scorer produces seed-level metrics only. The registered
hierarchical intervals, seed/decoder/world gates, locality randomizations, Holm
correction, W10 false-claim bounds, adversarial contrasts, paired-surface
decisions, leave-one-decoder-out analysis, and final property classifications
are not implemented, and the independent validator is still a placeholder.
These may be staged after qualification, but their code and exact bindings must
be frozen before confirmation generation as registered.

### H10 — Repository/release metadata is incomplete

GDT396 has no row in `experiments/EXPERIMENT_INDEX.tsv`; the whole experiment is
currently untracked. `experiment.json` leaves `question`, `claim_ceiling`,
`inputs`, and `outputs` empty and records validation as `NOT_RUN`. This is not a
publishable or reproducible pre-qualification freeze.

## Decoder-specific disposition

| decoder | static disposition | reason beyond shared blockers |
|---|---|---|
| D396S01 | HOLD | Multi-seed fit/locality pass; clean source. Architecture `PRIMARY` and `MULTI_CONSTRAINT` flags are identical, and structural clusters emit semantic-category/entity/current-meaning claims whose W10 veto is not enforced. |
| D396S02 | HOLD | Multi-seed fit/locality pass; clean source. `classify_world` is normalized, but broad structural semantic claims and all-resolved binary fallbacks depend on the missing false-positive/morphology qualification suite. |
| D396S03 | HOLD | Multi-seed fit/locality pass; clean and conservative on several semantic endpoints. Architecture comparison is incomplete and only `MULTI_RESOLUTION` receives injected architecture rows. |
| D396S04 | HOLD | Multi-seed fit/locality pass; clean source and the fixed-width two-atom analysis uses only the public channel contract. `classify_world` violates the normalized API, and its scalar architecture flags are not scalar-only. |

## Required re-audit gate

GO requires all H1–H8 blockers to be repaired and frozen before qualification
data are generated or decoded. H9's exact truth normalization must be resolved
before qualification scoring; its final-inference implementation and the full
independent validator must be frozen before confirmation. H10 must be resolved
before publication. Re-audit should use new hashes and development-only
fixtures; it must not reuse a qualification seed after any qualification oracle
has been opened.

## Audited snapshot hashes (SHA-256)

### Protocol and design documents

```text
2dc2f9afdd70a5707fb25a8265495b69f790442fd38974356b089bc94d8863ef  README.md
a846e026aba2ed1fc717458c9e4573aac9abe418154da0a13e567b8694708c7b  METHOD.md
a37213e12142c9596ab1f0e72315f4458f18d1097b2613fecf4109c7dd70b8a9  CLAIM_INTERFACE.md
9d7a48d79cc6b3c0ba6ce17b65b9bec4835435879f2512a89a8f01ddcf3aa6d9  DECODER_EXECUTION_SPEC.md
2ec5700c0dd8bddea0955cee40442f244fdde340b0ee26fc1fe0d6b0ff50f345  DECODER_QUALIFICATION_SPEC.md
2b16c2be1f48bdcfb0374a12b4c7fc665abf4d284cf9089574d3ba845f58b3fb  ORACLE_TRUTH_SPEC.md
9581c3775320ccdd5ccd0a1a48e55b8240d04aa882935df65c933878fe62acb2  SCORING_DESIGN.md
07ad9070b1e2523311277288b796dcd095447ee93d80ad34dd1137531b18e1a3  VALIDATION_DESIGN.md
bb61b72507b02c4953ddab5a20038ecdabceeb982205bb2121c46b42f3e9e9dd  TRACE_DIGEST_CORRECTION.md
2208c73215897ab09f7b2bc9583f7b06805427d913f2ee0c19ce052fe23714ff  RUNNER_INTEGRATION_CORRECTION.md
ba11fedfabc793b52a48407042a79e6539f6cbe035fce4cf7bd0c411cac5c64c  experiment.json
```

### Execution/scoring source

```text
276451822e1e356dd4fe1f252007299e18f4e6ca089386226847fc0d1b1d5261  src/decoder_api_v2.py
5d7190bdd0d4ddc166f802e37b38e5520a63415d65941f3f5090612c325036d4  src/observation_api.py
6523e40163baf5949ecdc95c1fbb29ccd13b4e1631dcb92c562fa3c85b30352e  src/run_blind_decoders.py
7c25c85f9ea48a24b065a7932fe1491927a58e5ab909020e8ec50fbb2d9723f5  src/freeze_claims.py
da10e29b7a074b3cb5f100e87b14ea66d590bff490db916dadb6a07af9f61c2e  src/freeze_decoder_panel.py
0e6c84d566c7dbebb2064bc8d1006b933e17e0cf37756cb970a91b1a663466dc  src/merge_claim_manifests.py
87029f7f403f1226625e68a702860808f78ca84b10bd2e10830ac343962c6be7  src/score_decoder_phase.py
27151abe11af914541e9dd6a5aa70f8e79ada733dae94df6a052f5ee1c69c102  src/qualify_decoders.py
78b436bf16dcf3faf963eb20b03d0b134e9c5889bb1f90737b05d373efbf0d0a  src/metrics.py
82819fe5a84a0829820ca95f647e4af71c932f5e7bbce9662cd7b8c4d43f15aa  src/run.py
82819fe5a84a0829820ca95f647e4af71c932f5e7bbce9662cd7b8c4d43f15aa  src/validate.py
0e66b9e0da6242237be644769ced7175475da62a6104fb45a4ef71b69b81e42c  src/freeze_protocol.py
91b374ac6ebda5eab785d5b4284650ae13c8fb195a66df9d56db32945070b93f  src/validate_protocol.py
be7d0481d58b70df8541aec159111d82548e73bebb8284d4c92ecff75feb2da7  src/generate_paired_corpora.py
62e512d4f426f607b170789efcfbd52ed1c14ddde795099b20d3763aa3c88a90  src/repair_trace_manifests.py
9cce0c2928f6fcd555b6bb4bc7dfefda3520a5be1c63d1d0229b9c1e32dfc4f3  src/validate_paired_corpora.py
c25b12138f30d15e6083d6a642a1fc21ee9b48e6b0f924dac4843a9324646aca  src/surface_channel.py
```

### Decoder sources and attestations

```text
fc052400cd2b0e017a02fdaadf4a3eaad7f1157218a3eb332629735af5b838ce  decoders/d396s01_multiview_graph/decoder.py
7dd38e1ee3384b3b4e84fe33fb7c21713bd447c1a436dde364792f516c3eec0d  decoders/d396s01_multiview_graph/ATTESTATION.md
1996f4b6e003d19bcc63c09c038aeabeee9443df54375235bc1a55cb6ead385c  decoders/d396s02_mdl_components/decoder.py
c590256435721625256174403f4e8ec8752b418908e720b5fc97bd8d5410b4d8  decoders/d396s02_mdl_components/ATTESTATION.md
623ebb020e93d9100580cb6d9379a7e437f330eee91d60bc9fed007f9ea44b98  decoders/d396s03_relation_topology/decoder.py
daa1fe534ef1afc8c6e6679d4159b9f35749ecbaf05d4909bddc2123a8e27434  decoders/d396s03_relation_topology/ATTESTATION.md
a0afbb6bedf1a951fd864bb6bacd29c302cc02ed26bccec6ed80c41313d9fe08  decoders/d396s04_contrastive_roles/decoder.py
9bd6f2db58ac2a287cb6d8bc665d3e8775447019e00ef2c128209884245254c9  decoders/d396s04_contrastive_roles/ATTESTATION.md
```

### Public artifacts and blind manifest bindings

```text
1289584fd7b632dd5feaa8ac82af5b7b41d94ef52405d9adc3ca878cd656487b  artifacts/gdt396_protocol_freeze.json
7bb59aaf530d1bc508b7272595c88aefd893c78522374172348cbc2380e9b101  artifacts/gdt396_protocol_validation.json
2e953be50bd5fd441f907c6e9de9ec72574c91993f98b7cfa003eb27ca65a9f6  artifacts/gdt396_development_corpus_validation.json
e6bd87a38d280fbb1500bb35e0d14e8f6cfca7f6543d9d306a40880861387896  .work/corpora/gdt396_legacy_paired_manifest.tsv
2646d2a7fd94a61e79bd6adfd889fa02d7d8288328cb2112ef6668e0f8bb285c  .work/corpora/gdt396_legacy_paired_manifest_v2.tsv
20fa26d0b2c204ce592c769e561d758c4251ea4c83cf036632fc668cd87c0363  .work/corpora/gdt396_development_paired_manifest.tsv
fe65ff08064db4e027a72d8bd0b0cc89631ac498b4ab6e258f05f7a6a01876e6  .work/corpora/gdt396_development_paired_manifest_v2.tsv
```

---

## Fresh development-only re-audit of the settled prequalification sources

Date: 2026-08-20  
Scope: static/read-only prequalification audit plus blind development-only
contract and runner tests. The historical HOLD above is retained verbatim.
This section evaluates H1--H10 against the new bytes supplied as the settled
snapshot. No qualification or confirmation observation exists. This audit did
not inspect an oracle, a hidden world/generator/source, GDT395 internals,
Voynich data, `f84`, or `f84r`.

### Outcome first

The five current decoders are source-clean and operational on the real pooled-
seed runner. The Boolean contract, fixed retention plan, fresh-process runner,
candidate locality, executable multi/scalar function comparison, correction
chronology sources, and public run/validation entry points are material
repairs. Four framework/repository blocker families nevertheless remain:

1. conflicting logical claim keys and several status/cap invariants are still
   accepted by the runner;
2. scoring does not mechanically bind itself to the frozen claim packet, and
   phase entry points trust a possibly stale stored PASS;
3. the W10 implementation does not compute the registered false-claim rate on
   oracle-absent events when the same endpoint has any scoreable truth; and
4. the experiment manifest and index do not describe the current correction
   state exactly.

### H1--H10 re-disposition

| historical blocker | current disposition | evidence |
|---|---|---|
| H1 Boolean serialization | CLOSED | `validate_shape` requires exact Python `bool`; the runner writes uppercase `TRUE`/`FALSE`; the scorer compares exact stored literals. `test_instrument_contract.py` passed the positive round trip and rejected a string Boolean. |
| H2 placeholder entry points | CLOSED | `run.py` exposes the registered phase stages and `validate.py` dispatches the available pre-panel/panel/phase validators. Both CLI help smokes passed. |
| H3 qualification gates | HOLD | Most registered anti-degeneracy, five-seed, two-world, both-surface, three-decoder/two-family, representation-selection, decoder-wide equality/relation, architecture, and function-variant calculations now exist. The W10 veto is incomplete: scorer rows expose `resolved_without_truth_rate`/`positive_prediction_rate` only in `NO_CAPACITY` cases, while `qualify_decoders.py` defaults a missing rate to zero. It therefore does not implement the correction's rate over oracle-absent events for a partially populated W10 truth endpoint. |
| H4 binding and chronology | HOLD | The versioned correction freezer/validator correctly limit disclosed early-protocol drift to `decoder_api_v2.py` and `generate_paired_corpora.py`, require narrow historical failures, bind the two blind manifests, and gate the panel freezer. However, decoder/generation authority checks read only a stored validation `status`; they do not revalidate its bindings at the action boundary. More seriously, `score_decoder_phase.py` does not require the phase claim-freeze artifact or compare its frozen manifest/file bindings before opening the phase oracle. |
| H5 process/prohibited paths | CLOSED for the audited sources | The runner requires one decoder/world/surface per process, projects the blind manifest to an observation-only allow-list, materializes rows before installing its audit hook, and then denies out-of-decoder repository reads plus process/network events. Static scans of all five sources found only standard-library imports and no oracle, GDT395, Voynich, `f84`, sibling-decoder, or external-data path. |
| H6 schema/determinism | HOLD | Supplied-model immutability, deterministic rerun, target candidate locality, query/rank agreement, target caps, Boolean types, scope locality, retained event coverage, and morphology rank contiguity are now checked. But duplicate detection uses every serialized field, not each table's logical key. A conflicting duplicate with the same partition context/property/unit but a changed confidence passed the current validator (`LOGICAL_DUPLICATE_ACCEPTED`). Equivalent logical-key gaps affect binary, scope, record, and architecture rows; unresolved status-dependent payload rules are incomplete; and morphology's declared rank cap is not enforced. Scorer dictionary comprehensions can consequently select one conflicting row by input order. |
| H7 feasibility/provenance | HOLD on provenance; feasibility CLOSED | Exclusive retention reduced the exact one-world/one-surface/one-held-seed smoke to 36--63 gzip tables and 113,552--417,235 retained rows per decoder. Each scorer context is loaded only when scored; path containment, table hashes, row counts, decoder hashes, training blocks, duplicate table cells, and model stability are checked. The unresolved claim-freeze-to-scorer binding permits a changed manifest/claim packet to be scored after a stale freeze, so oracle chronology is not mechanically sealed. |
| H8 multi-constraint comparison | CLOSED | D396S05 emits matched, complete `MULTI_CONSTRAINT` and `SCALAR_BOTTLENECK` `FUNCTION_OPERATOR_CLASS` rows only at `MULTI_RESOLUTION`, with the same eight-cluster budget. The scorer computes matched pair-F1 and the qualifier records the `>=.10`, four-of-five, at-least-two-world gate. Architecture variants are separately aggregated against direct metadata. |
| H9 truth/final inference | CLOSED for prequalification, staged for confirmation | `PREQUALIFICATION_INSTRUMENT_CORRECTION.md` authoritatively resolves pipe-valued identity fields as exact sorted composite signatures and relation targets alone as sets. Morphology offsets are diagnostic rather than fabricated truth. Confirmation generation is barred pending a later confirmation-instrument validation; final intervals/nulls/Holm/paired-surface inference may therefore remain staged, but must be implemented, independently validated, and frozen before confirmation generation. |
| H10 release metadata | HOLD | GDT396 now has an index row and populated question, ceiling, inputs, outputs, and explicit `f84`/`f84r` seals. But `experiment.json` says validation `PASS` while pointing to `gdt396_protocol_validation.json`, whose current status is `FAIL`; it does not yet point to a PASS correction validation. The index lists D396S05's decoder but omits its attestation and omits the correction freezer/validator and contract fixture from the registered source/validator inventory. |

### Exact remaining fixes

1. Define and reject duplicate logical primary keys for all nine tables,
   including method variant where applicable. Enforce all status-dependent
   empty/nonempty fields and the declared morphology rank cap. Extend the
   adversarial contract fixture so each invalid form must fail.
2. Make scoring require the matching `FROZEN_BEFORE_ORACLE_SCORING` claim
   freeze and verify at least the frozen manifest hash, panel-freeze hash, and
   claim bindings before any oracle is loaded. Revalidate current panel or
   confirmation-instrument bindings at every non-development generation,
   decode, freeze, and score action rather than trusting a stored status alone.
3. Emit a W10 false-claim numerator and denominator over oracle-absent events
   for every semantic partition, binary, and ranked-target row, including
   otherwise `SCORED` rows. Make the qualifier fail closed when that metric or
   the complete five-seed W10 panel is absent.
4. After producing and validating the versioned correction artifacts, update
   `experiment.json` to bind the current PASS validation truthfully. Update the
   GDT396 index row to include D396S05's attestation and all correction/contract
   sources in their proper document/source/validator columns.

### Decoder source audit and exact runner feasibility

All five `fit` implementations accept multiple training seeds for exactly one
world and surface. Seed-local physical containers are namespaced in D396S01,
D396S02, D396S03, D396S04, and D396S05 wherever pooled record statistics are
formed. Each source emits JSON-safe model state, uses only visible held-seed
context for transductive candidates, and passed the real runner's model-
immutability and byte-identical rerun gates.

The independent runner test used only W01 blind legacy observations for pooled
training and blind development seed 3960000 as held data, on `FREE_SURFACE`,
through every representation declared by the decoder. Outputs went to a
temporary directory outside the repository.

| decoder | result | declared representations | wall time | peak RSS | retained rows | gzip tables |
|---|---:|---:|---:|---:|---:|---:|
| D396S01 | PASS | 4 | 145.86 s | 1,559,260 KiB | 331,745 | 36 |
| D396S02 | PASS | 5 | 108.97 s | 1,389,612 KiB | 113,552 | 45 |
| D396S03 | PASS | 4 | 128.28 s | 1,349,260 KiB | 330,585 | 36 |
| d396s04_contrastive_roles | PASS | 7 | 52.06 s | 1,137,756 KiB | 417,235 | 63 |
| d396s05_multiconstraint_function | PASS | 7 | 119.34 s | 1,446,276 KiB | 410,151 | 63 |

The default eight-worker phase run can approach roughly 12 GiB during several
simultaneous heavy fits; this is an operator sizing concern, not a correctness
blocker, because `--workers` is bounded and configurable from 1 to 32.

The development-only contract fixture reported `PASS 6/6`. The additional
logical-duplicate adversarial probe copied one completed `FULL_GROUP`
partition row, changed only its confidence, and was accepted, establishing H6
without consulting outcomes.

### Current audited snapshot hashes (SHA-256)

#### Protocol, correction, and metadata

```text
2dc2f9afdd70a5707fb25a8265495b69f790442fd38974356b089bc94d8863ef  README.md
a846e026aba2ed1fc717458c9e4573aac9abe418154da0a13e567b8694708c7b  METHOD.md
a37213e12142c9596ab1f0e72315f4458f18d1097b2613fecf4109c7dd70b8a9  CLAIM_INTERFACE.md
9f93cc0bd3676478b9972720f1f0002606b3279757ca8377829fe70d55d92780  CLAIM_RETENTION_PLAN.md
9d7a48d79cc6b3c0ba6ce17b65b9bec4835435879f2512a89a8f01ddcf3aa6d9  DECODER_EXECUTION_SPEC.md
2ec5700c0dd8bddea0955cee40442f244fdde340b0ee26fc1fe0d6b0ff50f345  DECODER_QUALIFICATION_SPEC.md
2b16c2be1f48bdcfb0374a12b4c7fc665abf4d284cf9089574d3ba845f58b3fb  ORACLE_TRUTH_SPEC.md
9581c3775320ccdd5ccd0a1a48e55b8240d04aa882935df65c933878fe62acb2  SCORING_DESIGN.md
07ad9070b1e2523311277288b796dcd095447ee93d80ad34dd1137531b18e1a3  VALIDATION_DESIGN.md
bb61b72507b02c4953ddab5a20038ecdabceeb982205bb2121c46b42f3e9e9dd  TRACE_DIGEST_CORRECTION.md
483959d623f5636554dd22517f58d713298190a9018542c6cbdd9aa5a63151d7  RUNNER_INTEGRATION_CORRECTION.md
783e14c8377db20c4591820bb53a1bbdaa043e3422356f719e535598ed64c23b  PREQUALIFICATION_INSTRUMENT_CORRECTION.md
cf1a85ceb2c288f885a5667594b4545f3ea60dff5ef7bd7c20911cfcce0b0a57  experiment.json
e2bb26294cc82b5586e7cc4f50f4a2f114cba2645a359b38f815fd04bd21f6b1  experiments/EXPERIMENT_INDEX.tsv
```

#### Runner, scorer, freezer, and validators

```text
446046f78748e2cddaf65c535ba5f17aac93ae83b3aa7fd3ef8e1ccf997fd960  src/decoder_api_v2.py
5f4ac356118415c7b8c66cc1377f6de8da78ef3a6eac6602762d891705193476  src/observation_api.py
dcec667bd0fc8ba2160d0a8ec8d5bf2f125da4293a9277b132197b7ffb47480f  src/run_blind_decoders.py
7ea0f587afa1031bbf7979e54eecbf074afbc611da8241522be0a68e306a71a9  src/score_decoder_phase.py
5218c09600b331bf3c5dbefcd6900aa9f6f5d4e60f23915679067f3be5038004  src/qualify_decoders.py
5488c62bf783559865b9555e3ee6608db8228f449b04524110229d410f192083  src/run.py
6ddcbb1c1b370c88efc00066725e9af9203b3e6464371da07bd3d724b816ae85  src/validate.py
482e4d8afc26405b3f17bca8f68e5ddd52a6dfd2a4133a7b496deb3b182823a9  src/freeze_claims.py
6f6185ad454cc7cc3a2cfe4d21a09788b6bfdccbb4e2595eb27146c30ddef32d  src/freeze_decoder_panel.py
9159e54aa27f7711dfa0b750eb829000e0e3e820616aa4ca090118fc5ffa174e  src/freeze_prequalification_correction.py
4b4d1fa05f48f984b5d856aa1c654e77a1c5ab11194b00a73c3c2dbe95241794  src/validate_prequalification_correction.py
753eab7f9be16878787181da21086ad2279feea734f7756941ff1d369ebeeb17  src/validate_decoder_panel.py
72a9bde42ef226e8a7161931a3b3bbd43618b1a0803330f34e8aae48dddd2e92  src/test_instrument_contract.py
f3bfeb4a7628e9a00b4b3789016768b606069f2b65fe9a0b45f71a0853307a89  src/generate_paired_corpora.py
38846b41c6c7a0d5641bac42575950a9f4f5d87601352cda752dd26a401054de  src/merge_claim_manifests.py
78b436bf16dcf3faf963eb20b03d0b134e9c5889bb1f90737b05d373efbf0d0a  src/metrics.py
62e512d4f426f607b170789efcfbd52ed1c14ddde795099b20d3763aa3c88a90  src/repair_trace_manifests.py
2cd3e9a1b30435ddfb434b9d9c5d6254dc19c16513efae958a05e01d89c50e1c  src/validate_phase_corpora.py
0e66b9e0da6242237be644769ced7175475da62a6104fb45a4ef71b69b81e42c  src/freeze_protocol.py
91b374ac6ebda5eab785d5b4284650ae13c8fb195a66df9d56db32945070b93f  src/validate_protocol.py
9cce0c2928f6fcd555b6bb4bc7dfefda3520a5be1c63d1d0229b9c1e32dfc4f3  src/validate_paired_corpora.py
c25b12138f30d15e6083d6a642a1fc21ee9b48e6b0f924dac4843a9324646aca  src/surface_channel.py
```

#### Decoder sources and attestations

```text
8c52c318402a85874b5cb2ae1561fd9c1a954b31d7ef23edcbc02e66219235f4  decoders/d396s01_multiview_graph/decoder.py
7dd38e1ee3384b3b4e84fe33fb7c21713bd447c1a436dde364792f516c3eec0d  decoders/d396s01_multiview_graph/ATTESTATION.md
c633fcb9a8ba501db7e9bce4eda023146d1f87f3bf2d5e6c3d9bddedd932d2d0  decoders/d396s02_mdl_components/decoder.py
c590256435721625256174403f4e8ec8752b418908e720b5fc97bd8d5410b4d8  decoders/d396s02_mdl_components/ATTESTATION.md
623ebb020e93d9100580cb6d9379a7e437f330eee91d60bc9fed007f9ea44b98  decoders/d396s03_relation_topology/decoder.py
daa1fe534ef1afc8c6e6679d4159b9f35749ecbaf05d4909bddc2123a8e27434  decoders/d396s03_relation_topology/ATTESTATION.md
b61fb3bd4b545c9ec8d30f3a360a9cdb055db5e71bc36306b29b51211fcb8ba7  decoders/d396s04_contrastive_roles/decoder.py
9bd6f2db58ac2a287cb6d8bc665d3e8775447019e00ef2c128209884245254c9  decoders/d396s04_contrastive_roles/ATTESTATION.md
12f14d4b2150382055e9fc91a8734420b68013ab9798d4e3b9926e37926efe6d  decoders/d396s05_multiconstraint_function/decoder.py
b48df3c58caeca02207048e6c504d1ccb37e3d21c1dc0d1979c7cd9c5264d434  decoders/d396s05_multiconstraint_function/ATTESTATION.md
```

#### Current public freeze/validation and blind-manifest bindings

```text
1289584fd7b632dd5feaa8ac82af5b7b41d94ef52405d9adc3ca878cd656487b  artifacts/gdt396_protocol_freeze.json
d82d175aa773c7b4b59bfbf732cba95fd0479a61aeff1d3fbd119881235d7e37  artifacts/gdt396_protocol_validation.json
d936d8c003bc7e3a0674298912bf0c4f19d5de3ad1a1dba976357e5ca453b2d9  artifacts/gdt396_development_corpus_validation.json
2646d2a7fd94a61e79bd6adfd889fa02d7d8288328cb2112ef6668e0f8bb285c  .work/corpora/gdt396_legacy_paired_manifest_v2.tsv
fe65ff08064db4e027a72d8bd0b0cc89631ac498b4ab6e258f05f7a6a01876e6  .work/corpora/gdt396_development_paired_manifest_v2.tsv
```

### Final prequalification decision on this snapshot

Final decision: **HOLD**

Qualification/confirmation generation and oracle scoring must remain barred
until the four exact fixes above are implemented, the correction/index/
manifest state is truthful and complete, and a fresh development-only audit of
the resulting hashes closes H3, H4, H6, H7, and H10.

---

## Final development-only re-audit after correction V3

Date: 2026-08-20  
Scope: the settled public prequalification bytes only. The historical HOLD and
its evidence above are retained as an append-only audit record. This pass did
not inspect any hidden generator/world source or oracle/world truth, GDT395
internals, qualification or confirmation observations, Voynich data, `f84`, or
`f84r`. No qualification/confirmation observation or paired-manifest file was
present.

### Final H1--H10 disposition

| blocker | final disposition | current evidence |
|---|---|---|
| H1 Boolean serialization | CLOSED | Exact Python `bool` input and uppercase TSV serialization remain enforced. The adversarial/round-trip fixture passes. |
| H2 real entry points | CLOSED | The public run and validation dispatchers select the current V3 prequalification validation, real panel freezer/validator, phase runners, phase validation, and claim freezer. |
| H3 qualification gates | CLOSED | Route, suite, representation, panel-diversity, architecture-binary, and matched function-variant gates remain executable. For every semantic route, `semantic_w10_false_rates()` now requires exactly five rows from five distinct W10 corpus seeds, requires an explicit event-level `resolved_without_truth_rate` or `positive_prediction_rate` on every row, and applies the registered `<= 0.10` veto. Missing, duplicate-seed, and missing-rate panels fail closed. |
| H4 binding and chronology | CLOSED | Every non-development action calls the current-binding authority. Stored PASS alone is insufficient: freeze bytes, validation-to-freeze hash, every registered binding, decoder source, and attestation are rehashed at action time. The scorer authenticates the phase claim freeze before loading an oracle. Correction V3 binds V2 and records only the six authorized V2-to-V3 changes. |
| H5 process/prohibited paths | CLOSED | Each invocation remains exactly one decoder/world/surface in a fresh process. Observation projection, post-load read/process/network denial, repository path containment, source scans, and attestations exclude oracle, sibling, external-data, Voynich, `f84`, and `f84r` access. |
| H6 schema/determinism | CLOSED | All nine tables now use explicit logical keys, reject conflicting duplicates, enforce status-dependent payload rules, normalize inactive identifiers, enforce candidate/scope locality, require retained-event coverage, enforce target uniqueness/rank/caps, and enforce declared morphology rank caps and contiguity. The 9-case contract fixture exercises the repaired negative cases and passes. Model immutability and byte-identical rerun gates remain in the real runner. |
| H7 feasibility/provenance | CLOSED | The five exact decoder sources previously passed pooled multi-seed development runner smokes, with bounded retained tables and configurable worker count. Current scoring requires the authenticated claim freeze, exact phase manifest and panel hashes, every frozen claim path/hash, decoder/training/model bindings, and refuses output overwrite. |
| H8 architecture/function variants | CLOSED | Matched `MULTI_CONSTRAINT` versus `SCALAR_BOTTLENECK` function rows remain executable and aggregated. `architecture_partition_claims` is intentionally an anonymous diagnostic and is not aggregated: the registered independently scoreable architecture endpoints are the direct Boolean metadata claims. Scoring the anonymous partition against a visible opaque world identifier would add no legitimate confirmatory test. Retaining it under schema/locality enforcement is therefore acceptable and not a blocker. |
| H9 truth/final inference | CLOSED for prequalification | The public instrument correction still fixes composite identity, set-valued targets, and morphology semantics. Confirmation-only inference remains correctly staged behind later confirmation-instrument validation and cannot be exercised by this GO. |
| H10 release metadata | CLOSED | `experiment.json` is `REGISTERED_PREQUALIFICATION`, points to V3 PASS, inventories the five decoder/attestation pairs and V1/V2/V3 sources and artifacts, and seals `f84` and `f84r`. The GDT396 index row describes the current prequalification state. `./vmanus-exp check` returned `REPOSITORY_PREFLIGHT_PASS` on these source/manifest/index bytes before this review append. |

### Correction V3 lineage and action bindings

The V3 freeze has schema
`GDT396_PREQUALIFICATION_CORRECTION_FREEZE_V3`, status
`FROZEN_BEFORE_QUALIFICATION_GENERATION`, binds V2 freeze SHA-256
`e41e9e052dbba9d89a58f7d4941c699bc262173ea354013bffd72c33eef47660`,
and has content SHA-256
`0d660be1423d00ea956f288d1e9b5133f9133da108c45ba53b99d57228f4b49f`.
Its recorded V2 drift is exactly:

```text
src/freeze_decoder_panel.py
src/qualify_decoders.py
src/run.py
src/test_instrument_contract.py
src/validate.py
src/validate_decoder_panel.py
```

For each entry the artifact contains both the V2-bound hash and current V3
hash. `validate_prequalification_correction_v3.py` recomputes the actual drift,
requires equality with that exact set, checks both sides of every recorded
change, rehashes every V3 binding, and verifies that qualification and
confirmation observations remain absent. Its fresh result was PASS 8/8.

`phase_authority.require_instrument()` is called by non-development corpus
generation, decoder execution, claim freezing, phase validation, and scoring.
It rejects a stale PASS after any bound byte changes. Before any oracle open,
`score_decoder_phase.py` additionally authenticates the phase claim-freeze
schema/status/content hash, current manifest hash, panel-freeze hash, and every
frozen claim binding. The earlier chronology and claim-authentication blockers
are therefore mechanically closed.

### Final blind checks

```text
PASS 9/9                                      src/test_instrument_contract.py
PASS 8/8                                      src/validate_prequalification_correction_v3.py
REPOSITORY_PREFLIGHT_PASS                     ./vmanus-exp check
absent semantic W10 panel                     REJECT
five W10 rows with a duplicate corpus seed    REJECT
five W10 rows with one missing false rate     REJECT
five distinct W10 seeds with all rates        ACCEPT
qualification/confirmation observations       ABSENT
qualification/confirmation paired manifests   ABSENT
```

The W10 probes called the exact current helper with synthetic public-shaped
rows for `FUNCTION_OPERATOR_CLASS/MULTI_RESOLUTION`; they did not access an
observation or outcome. The earlier exact-source development runner smokes and
their resource measurements remain valid because V3 changed none of the five
decoder sources or the blind runner.

### Final audited snapshot hashes (SHA-256)

#### Corrections, authority, runner, scorer, and release state

```text
783e14c8377db20c4591820bb53a1bbdaa043e3422356f719e535598ed64c23b  PREQUALIFICATION_INSTRUMENT_CORRECTION.md
d6c9ea0e1d854516ecb8bed0d4682c196c83d8c6e5c6002ed8c918414f296a37  PREQUALIFICATION_REAUDIT_CORRECTION.md
800cb326af4ec69bdbbf55100989512150a87fe37e52c7cee5a52e307b18e393  PREQUALIFICATION_W10_CORRECTION.md
0b7ed8f5bcc2a42ccb9dfd2799e82afd260418cc41fa935907a8924128289432  src/phase_authority.py
578c810dca299ac2e5a8af7515b3cf90b1e5a201f054ef433898b7fdafe4056b  src/generate_paired_corpora.py
cfa577483c08d54dc38fb099b36f3088de8db0198cddb52f79a0ad94187cd43c  src/run_blind_decoders.py
ab3f29c501eb82777e881cd8fe547c2d61ab27b6dbaaf99a99040236a893d35f  src/score_decoder_phase.py
da5f645e7212f4ea2851034c5ffdb69a226bc55cd18f4e4df9df2ff81869d3fe  src/qualify_decoders.py
6487fa2c4a740d1075653f0c8d78fc50cdd7ccbf708c047da0c70934e002f9fd  src/freeze_claims.py
bde5c39fa9259cc3a5d9985790a246c353b47405292360c87a7ebdda353d1117  src/validate_phase_corpora.py
38a9b2d169318e72c1fb058480de4012986a25811a4da988721bc841dccf97b1  src/freeze_decoder_panel.py
304e89a4244d1db5bfaa0a44987505ceeff6247e9ac85b2ad5627e518b619169  src/validate_decoder_panel.py
3abfc893a686cd14edca8ddb16500dfa462da3b64406ff8009b4302913d5c95b  src/test_instrument_contract.py
0968b9c6d63e88a36c1e43a6605c99cd8656aa57dbdd56a72acec8ae54e091e7  src/run.py
83b10e9946ad472c7f466c45ef551ab3453e2f8069a0c916ba3f0148b35614f7  src/validate.py
933c5359e64a30e3e6d7a162fe6e858f36e4e90d7b0da3b95271ee70f541f573  experiment.json
f86bc5d6fda49e9b3b133d9b761d38439fb42e0f8869bbcab60747fbcca6dde0  experiments/EXPERIMENT_INDEX.tsv
```

#### Versioned correction sources and artifacts

```text
9159e54aa27f7711dfa0b750eb829000e0e3e820616aa4ca090118fc5ffa174e  src/freeze_prequalification_correction.py
4b4d1fa05f48f984b5d856aa1c654e77a1c5ab11194b00a73c3c2dbe95241794  src/validate_prequalification_correction.py
40bd142487d7b72ab24aab342114f15f8d1e17d975e3a88d7ebbdb59e0cb8b7c  src/freeze_prequalification_correction_v2.py
f7264919eb7cf9946dff9bee62dbecd9209685cf5e08b630d10453289f942fa0  src/validate_prequalification_correction_v2.py
231f5d496f6dffed3332440d38b190b5b2f8da32683b87c10da901dcfdbafa06  src/freeze_prequalification_correction_v3.py
ade156f257bf9b83f4e8e546da4d4eb585e58163f3c059602ae8107e928c7d9c  src/validate_prequalification_correction_v3.py
1eb18881324d25b5da9f918e2dce7d59953fdd2e701182ccf829aca13471f8da  artifacts/gdt396_prequalification_correction_freeze.json
83bfac9b6bc6204056c0ababa978958ee3ba262e316413a6b1b69b357362f762  artifacts/gdt396_prequalification_correction_validation.json
e41e9e052dbba9d89a58f7d4941c699bc262173ea354013bffd72c33eef47660  artifacts/gdt396_prequalification_correction_freeze_v2.json
6d6c626275680111042f26965918ac472adb1a932762951b2a68e4b7749c4be0  artifacts/gdt396_prequalification_correction_validation_v2.json
fc587ec03b1f02be3acb50a180ef12b7974ad09429bfade0d57545403b32f636  artifacts/gdt396_prequalification_correction_freeze_v3.json
e44f400aa459cf9d7c6459353d130e880c2c15abb7e7e579204be7f41936a4af  artifacts/gdt396_prequalification_correction_validation_v3.json
```

#### Decoder sources and attestations

```text
8c52c318402a85874b5cb2ae1561fd9c1a954b31d7ef23edcbc02e66219235f4  decoders/d396s01_multiview_graph/decoder.py
7dd38e1ee3384b3b4e84fe33fb7c21713bd447c1a436dde364792f516c3eec0d  decoders/d396s01_multiview_graph/ATTESTATION.md
c633fcb9a8ba501db7e9bce4eda023146d1f87f3bf2d5e6c3d9bddedd932d2d0  decoders/d396s02_mdl_components/decoder.py
c590256435721625256174403f4e8ec8752b418908e720b5fc97bd8d5410b4d8  decoders/d396s02_mdl_components/ATTESTATION.md
623ebb020e93d9100580cb6d9379a7e437f330eee91d60bc9fed007f9ea44b98  decoders/d396s03_relation_topology/decoder.py
daa1fe534ef1afc8c6e6679d4159b9f35749ecbaf05d4909bddc2123a8e27434  decoders/d396s03_relation_topology/ATTESTATION.md
b61fb3bd4b545c9ec8d30f3a360a9cdb055db5e71bc36306b29b51211fcb8ba7  decoders/d396s04_contrastive_roles/decoder.py
9bd6f2db58ac2a287cb6d8bc665d3e8775447019e00ef2c128209884245254c9  decoders/d396s04_contrastive_roles/ATTESTATION.md
e3f2c2148b4dd8a8ab423ab894565a2b8a6baee4bc36ba83756d591f27baa08a  decoders/d396s05_multiconstraint_function/decoder.py
b48df3c58caeca02207048e6c504d1ccb37e3d21c1dc0d1979c7cd9c5264d434  decoders/d396s05_multiconstraint_function/ATTESTATION.md
```

Updating this independent review necessarily changes its own hash after the
successful preflight snapshot. The panel freezer is designed to bind the GO
review bytes directly; the manifest/index review-output hash must be refreshed
as the ordinary post-review publication step before the next repository
preflight. This bookkeeping consequence is not a scientific or instrument
blocker and does not authorize qualification until the panel freeze validates.

### Final prequalification decision on the V3 snapshot

Final decision: **GO**
