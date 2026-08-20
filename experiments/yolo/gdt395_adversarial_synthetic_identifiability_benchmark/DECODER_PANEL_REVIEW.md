# GDT395 decoder panel static adversarial re-review

## Decision: GO

All five current decoder sources and the current freeze, validation, and blind
runner sources pass this pre-execution static review. The former D03--D05
blockers are repaired. The latest runner closes the previously identified
freeze-binding, manifest/path, blind-input-hash, and row-split gaps.

This was a source-only review. No decoder or panel program was imported or
executed. No observation/held packet, world or generator/design source,
method file, work product, oracle, codebook, genealogy, Voynich/f84 material,
or git history was inspected. Only the decoder contract/API, `decoder_api.py`,
D01--D05 source and attestations, `freeze_decoder_panel.py`,
`validate_decoder_panel.py`, and `run_blind_decoders.py` were read. Only this
review file was edited.

## Gate summary

| Gate | Result | Finding |
|---|---|---|
| Exact decoder API and schemas | GO | D01--D05 export literal `DECODER_META`, `decode(train_rows, held_rows, representation)`, and `classify_world(train_rows)`. Their event and world rows use the exact declared fields. The runner applies `validate_claims()` to every event batch and exact-field/provenance/confidence checks to world claims. |
| Literal metadata | GO | Every `DECODER_META` is an `ast.literal_eval`-compatible dictionary and literally lists all six representations. |
| 2 Sol + 3 Luna | GO | D01 declares `gpt-5.6-sol`; D02 declares `OpenAI Codex (Sol)`; D03--D05 each declare `gpt-5.6-luna`. The repaired Luna attestations agree. These are source/attestation provenance declarations; static review cannot independently identify an authoring model. |
| Standard-library-only/local imports | GO | Algorithmic imports are standard-library-only. D03/D04 use the permitted benchmark-local `src.decoder_api`; the runner puts the experiment root on `sys.path`. D05's relative local import has an exact-schema fallback. |
| Train-only fitting | GO | Learned vocabularies, thresholds, components, contexts, and schemas are fitted from `train_rows`. Held use is direct model application plus permitted equality/structural ordering. |
| Empty fallbacks | GO | D03--D05 now preserve `UNRESOLVED` when licensed surface/record evidence is absent. D04's RECORD_TOPOLOGY branch is gated on nonempty observed tokens. |
| Prohibited-key boundary | GO, with D02 advisory | D01/D03/D04/D05 have explicit forbidden-key defenses or strict allowlists. D04 schema keys are now restricted to `_STRUCTURAL_KEYS`. D02 excludes major answer-bearing hints but not a bare `label`; the declared sanitized blind-packet guarantee makes this defense-in-depth rather than an execution blocker. |
| Anonymous/no-meaning output | GO | Claims are opaque hashes, anonymous structural classes, or `UNRESOLVED`; no readable translations or actual world-family names are emitted. |
| Determinism | GO | Stable hashes, sorted/canonicalized structures, fixed graph iterations, deterministic gzip metadata, exact output validation, and final manifest sorting make values/files deterministic for fixed TSV-like inputs and row order. |
| Cross-decoder independence/diversity | GO on source evidence | No obvious algorithm copying is present. The five families are materially distinct: multiview graph, MDL components/topology, frequency-position baseline, surface components, and context/topology graph. |
| Plausible ~126k train / 8.4k held scale | GO with performance advisory | D03/D05 are linear or near-linear; D01/D02 have higher constants; D04 held component lookup is now bounded by token length. The runner loads training rows once per decoder/world job and caps concurrency at four. The frozen API still causes 30 fits per decoder/world (six representations × five held seeds), so runtime should be monitored, but memory growth is bounded and there is no remaining Cartesian held-inventory scan. |
| Obvious crash on declared fields | GO | No decoder has an obvious crash on the mandatory identity fields and packet-style values. D04 world classification now uses numeric `token_counts`, fixing the former set/int failure. This is a static finding, not a data-run result. |

## Decoder dispositions

### D01_MULTIVIEW_GRAPH — GO

Unchanged and conforming. It blocks answer-bearing key names, fits all learned
structures on train rows, uses only visible held equality/topology, and emits
anonymous hashes. Memory is linear with a high constant because field-value
lists, an unused `row_sequences` list, surface tuples, and context counters
coexist.

### D02_MDL_COMPONENTS — GO with advisories

Unchanged and conforming. It has train-only MDL/component/schema fitting,
anonymous output, conservative held topology, exact schemas, and no external
dependency. Internal residual-host sets plus repeated scans of up to 160
component candidates may be expensive on high-cardinality or long-token
vocabularies. Add bare `label` to `_FORBIDDEN_HINTS` for defense in depth.

### D03_frequency_position — GO

Every former blocker is repaired: Luna provenance is literal; representations
are validated; exact field allowlists plus a broad prohibited-key guard replace
the arbitrary-row fingerprint; absent surface/record evidence remains
unresolved; containers and finite scalars are deterministically canonicalized;
and runtime/memory are linear.

Minor advisory: a string such as `"nan"` becomes non-finite only after
`_position()` converts it. Reject non-finite converted positions before using
them in a structural hash.

### D04_surface_components — GO with memory advisory

Every former blocker is repaired:

- Luna provenance and supported representations are literal.
- held component generation enumerates only bounded token-edge and length
  2/3/4 substring candidates, using learned-set membership rather than a scan
  of every learned component.
- support is measured across distinct complete token forms, and productive
  and fossil sets are disjoint.
- `classify_world()` uses numeric `token_counts`, fixing the former `TypeError`.
- empty RECORD_TOPOLOGY claims remain unresolved.
- surface values are allowlisted/guarded and schema keys are limited to the
  explicit structural allowlist.

Training retains complete-token sets for each learned prefix, suffix, and
short substring. This may be memory-heavy for an unusually high-cardinality
vocabulary but is bounded by training token material and no longer multiplies
against all held tokens.

### D05 — GO

Every former blocker is repaired: Luna provenance is literal; `label` is no
longer a licensed surface field; blocked keys and container values are
rejected; missing surface/record evidence stays unresolved; implicit records
are gone; and empty training evidence yields an unresolved zero-confidence
world claim. Its structures are linear or near-linear in rows, vocabulary, and
observed adjacency edges.

Advisory: a novel held token gets `ctx = UNRESOLVED`, after which its entity
claim hashes that sentinel. Hashing the directly observable token or leaving
the entity unresolved would avoid collapsing all unseen surfaces together.

## Panel-program review

### `freeze_decoder_panel.py` — GO for pre-execution freezing

The freezer:

- refuses to overwrite an existing freeze;
- refuses to freeze after any file exists under `.work/claims`;
- records the observed zero claim-file count and active one-shot guards as
  `pre_execution_evidence`;
- requires exactly five complete decoder directories;
- extracts literal metadata without importing decoder modules;
- hashes each source and attestation;
- binds the contract, implementation API, claim API, interface/audit protocol
  files, both observation manifests, and all three panel programs; and
- seals the complete JSON body with `content_sha256`.

The historical fields stating that designers saw no observations/oracles and
that no prior execution/Voynich/f84 access occurred are necessarily
attestations, not facts a local source freezer can independently discover. The
one-shot and empty-claims checks honestly enforce the local state they can
observe; downstream prose should continue to call the remaining fields
attested declarations rather than measured proof.

### `validate_decoder_panel.py` — GO for its static/hash scope

The validator checks current bindings and decoder/attestation hashes, the
freeze content hash, literal metadata equality, exact top-level function
arguments, representation support, unique IDs, the exact approved model-name
mix (one `gpt-5.6-sol`, one `OpenAI Codex (Sol)`, three `gpt-5.6-luna`),
standard-library/permitted-local imports, absence of several direct
file/dynamic-call forms, attestation predicates, and frozen pre-execution/seal
declarations.

Its scope is correctly non-executing, so it cannot establish output behavior,
runtime, train/held dataflow, author identity, or the historical truth of an
attestation. In particular, `api_exact`, `no_file_or_dynamic_io`, and
`attestations` are syntactic checks rather than proofs. This manual source
review covers the current decoder logic, and the blind runner provides the
dynamic exact-output validation when execution is later authorized.

### `run_blind_decoders.py` — GO with performance/atomicity advisories

Blindness and freeze enforcement are now adequate from current source:

- there is no oracle path, oracle option, scorer, or oracle loader;
- the runner verifies freeze status, embedded content hash, every binding,
  each decoder source hash, and exact frozen metadata before use;
- both observation manifests are bound by the freeze;
- `SAFE_ID` rejects path separators/traversal in pair/world IDs;
- each manifest observation path must equal the constructed blind relative
  path and each blind observation file must match its manifest SHA-256;
- every loaded row must match the requested `world_id` and numeric
  `corpus_seed`;
- train seeds are exactly 0--14 and held seeds exactly 15--19;
- one decoder/world job loads training rows once and processes all five held
  seeds; world classification runs once per authentic training set;
- event and world output schemas/provenance/confidence are validated; and
- gzip bytes and the final claim manifest order are deterministic.

The frozen API requires a fresh internal fit on each `decode()` call, leaving
30 fits per decoder/world. With at most four workers and training rows loaded
once per job this is plausible as an offline run, but it is the main runtime
risk. Writes are direct rather than staged/atomic, so a late failure can leave
partial claim files without a completed manifest; clean the partial run or use
an atomic staging directory before retrying.

If pair identity is a declared observation field, add a row-level pair-ID
check. If event IDs are required to be globally disjoint across seeds, assert
train/held disjointness; neither invariant is stated in the reviewed decoder
API.

## Current reviewed hashes

These SHA-256 values were computed by byte-reading only; no Python source was
imported or executed.

| File | SHA-256 |
|---|---|
| `decoders/d01_multiview_graph/decoder.py` | `c458b7d1a3b994e198d4a11c97096b9fee21804233918c8dc962487596c5d9e1` |
| `decoders/d02_mdl_components/decoder.py` | `bbeacc0a828e7f57c0814e7daa8af3279ff6e4a68d63944454b7b0cd90c62fa5` |
| `decoders/d03_frequency_position/decoder.py` | `5bee36320e6a18c3a80a21ee2be144567b9dc0dfe0418b6c6c58ea6a33931419` |
| `decoders/d04_surface_components/decoder.py` | `605d344d7c49205f11fb73cef050921b3e3b2e53913fc8633172947053d00802` |
| `decoders/d05_context_topology/decoder.py` | `451f5bd0293db511af0ba2a00b12c76541945819eb4387860e15e0e97586a5fd` |
| `src/freeze_decoder_panel.py` | `be3ba42f5609389026b259300f59bea85f63a7130eb6bc10b80c9102a3fd7f61` |
| `src/validate_decoder_panel.py` | `846591f954cee882d00710feef9d81ec63b40aa20d8250534ddd48c66771c17f` |
| `src/run_blind_decoders.py` | `d19d32c5f20da41bcabeb8f9b0f0bc2361d6097cd5fbb5b0d3a0ccfb4578de89` |
| `DECODER_CONTRACT.md` | `285f7256756975a2296949246284eaeee94da29a0632b73d3b6025aa600f918e` |
| `DECODER_IMPLEMENTATION_API.md` | `be7816b017e59b2aa60afb1ef5a252a27ccd7bb2ee14fa7ee72604dd20749a19` |
| `src/decoder_api.py` | `6ec981248cde228280485c681a00c69bcc80931ed707465aad2971265926a247` |

Attestation hashes:

| Decoder | SHA-256 |
|---|---|
| D01 | `0d41f13a5100fc8fd26649489d6e0ce45a856a7b786d70736cdbf72a800e8b17` |
| D02 | `2787f5f866a2ea9733e1569d6e1d644bf50a424cfc021d3dde96a52b17fc2c77` |
| D03 | `7055c0a828b33d4e558e76462d652f5a56fb4b9e75bda3ee345cd36bbe50a146` |
| D04 | `19bee42e1b818b5bf0f0415638330fe7177f6e511264cdea27eebea7273d1522` |
| D05 | `7b5057795b18c9fba78406fc61b370b892b499a40bc5f04a39cc4f4f38a9941c` |

## GO conditions and cautions

This GO is authorization only from the static panel perspective. Before any
decoder import, create the one-shot freeze from the reviewed bytes, run the
static validator, and require its PASS. Do not modify a bound source, manifest,
or protocol artifact afterward. No source reviewed here authorizes oracle or
Voynich/f84 access.

Monitor wall time and memory during the blind run because the frozen API
repeats fitting. Treat a partial-output failure as an incomplete run, not a
score-ready result, and preserve the frozen inputs/hashes during recovery.
