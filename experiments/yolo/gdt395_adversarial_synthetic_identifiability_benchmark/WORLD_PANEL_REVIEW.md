# GDT395 independent adversarial world-panel review

## Decision

**HOLD BEFORE BLIND DECODING.**

The panel has good conceptual diversity, the ten generators are deterministic,
all ten satisfy the shared field-set validator, eight worlds contain genuine
multi-stage organic histories, no meaningful world reduces to a plain
character substitution, and W10 preserves the intended semantic-null boundary.
Those positives do not cure several pre-decoding design defects. In particular,
the two declared matched-carrier comparisons are not currently matched, some
observation packets have internally contradictory physical boundaries or
hierarchies, two sealed oracles contain demonstrably wrong truth, and the
binary morphology truth is not encoded consistently enough for a common
scorer.

This is a design review, not a benchmark-result review. No decoder, corpus
result, Voynich source, or other experiment was inspected. Corrections below
are based only on the frozen method/contract and generator behavior and should
be made before any decoder is allowed to see a packet.

## Materials and smoke protocol

Reviewed only:

- `METHOD.md`
- `WORLD_DESIGN_CONTRACT.md`
- `artifacts/gdt395_interface_freeze.json`
- `src/world_api.py`
- all ten `worlds/*/DESIGN.md` and `worlds/*/generator.py` files

For each generator I produced a complete-record-bounded corpus with
`seed=17, target_events=512`, ran `src.world_api.validate_rows`, generated the
same seed twice and a different seed once, and audited identifiers, declared
alphabet, adjacent separators, hierarchy nesting, relation targets, scope
endpoints, and semantic-null fields. I additionally compared both adversarial
pairs over all twenty frozen seeds at 512 target events per seed. This audit
created no corpus artifact.

All ten generators passed `validate_rows`; all ten were byte-deterministic for
the repeated seed; and all ten changed at seed 18. Thus the HOLD is not a basic
execution or determinism failure. The shared validator is simply too weak to
catch the blockers below.

## Exact blockers

### B1. Neither declared adversarial pair satisfies the matched-carrier contract

The contract requires matched page/record/line length, alphabet, token length,
recurrence, and separator distributions. Alphabet cardinality matches within
each pair (14 for W02/W03 and 12 for W09/W10), but the empirical envelopes do
not.

Across the twenty 512-event smoke corpora:

| Pair | Token-length TV | Separator TV | Record-length TV | Line-length TV | Ambiguous rate | Mean type/token | Mean top-type rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| W02 organic / W03 engineered | 0.453 | 0.295 | 0.591 | 0.224 | 15.6% / 50.2% | 0.235 / 0.383 | 11.4% / 7.0% |
| W09 meaningful / W10 semantics-light | 0.175 | 0.220 | 0.201 | 0.166 | 11.0% / 10.8% | 0.355 / 0.450 | 6.3% / 5.1% |

Page and paragraph density are also different. W02/W03 average 12.21/7.59
records per page and 4.46/1.98 per paragraph; W09/W10 average 9.44/11.99 per
page and 2.92/4.28 per paragraph. W02/W03 are especially far apart: W02's
512-event token lengths range 2--7 while almost every W03 token has length 5,
and W03 exposes roughly three times as many `JOIN` boundaries.

These contrasts would let a decoder distinguish paired worlds from carrier
shape before addressing the hidden organic/engineered or meaningful/null
contrast. The pair labels alone do not constitute matching.

**Required correction:** freeze one truth-independent carrier schedule per
pair and seed, then make both members consume it. The schedule should fix page
and paragraph breaks, record and line profiles, register/hand draws, token
lengths, separator types, ambiguous flags, and recurrence-rank draws while
allowing world-local glyph labels and nonidentical strings. Add a pre-decoding
pair validator that rejects divergence in every contract-named carrier
dimension. Do not tune the schedule against decoder behavior.

### B2. The common binary truth schema is not common or binary

`productive_morphology` is emitted as lowercase `yes/no` (W01), uppercase
`YES/NO` (W02, W09), `TRUE/FALSE` strings (W03), `YES/NO/NONE` (W04),
`YES/NO/LIMITED` (W05), lowercase `true/false` strings (W06), Python booleans
(W07), component labels such as `PM_ITER`, `PM_ACTION_CUE`, and
`PM_S2_DETERMINATIVE` (W08), and `NONE` (W10). `ambiguous_boundary`,
`corpus_seed`, and index fields also mix booleans, integers, and differently
cased strings. The frozen method calls the productive/fossilized scoring task
binary. W08 in particular places the identity of a productive component in a
binary truth field.

**Required correction:** freeze canonical scalar encodings before corpus
generation: `YES`, `NO`, or `NONE` for eligible binary truth; integer
`corpus_seed`, `event_index`, and `group_index`; and one canonical representation
for `ambiguous_boundary`. Put productive component identities only in
`current_morpheme_ids`; map W05 `LIMITED` to a binary current-status value and
retain the limitation in genealogy/rules. Enforce types and enums in the shared
validator.

### B3. Index semantics differ across worlds, and W10's event index is invalid

W10 sets `event_index=offset_in_record`, yielding 498 duplicate event indices
and 41 non-increasing transitions in its 514-event smoke corpus. Every other
world uses a corpus-global event index. `group_index` is also split across the
panel: W01/W02/W08/W09 use record-local order, whereas
W03/W04/W05/W06/W07/W10 reset it at each physical line. The paired worlds use
opposite conventions in both declared pairs, so this itself is a carrier cue.

**Required correction:** define `event_index` as unique corpus-global order and
choose one meaning for `group_index` (record-local order is the least
ambiguous given the current schema). Apply it to every world and validate
monotonicity and reset points.

### B4. Four worlds describe one physical boundary two different ways

At seed 17/512, adjacent rows disagreed on
`left.separator_after == right.separator_before` 11 times in W01, 96 in W02,
86 in W06, and 182 in W08. W01 mainly hard-codes a record-final `RECORD` even
when the next onset is `PAGE` or `PARAGRAPH`. W02, W06, and W08 additionally
sample the two sides of a boundary independently. This corrupts separator
features and invalidates carrier comparisons.

**Required correction:** construct one boundary vector per corpus and derive
both adjacent fields from that single vector. Add equality validation for all
adjacent events, including hierarchical transitions and the terminal event.

### B5. W09's hierarchy is not nested

W09 computes pages every ten records but paragraphs every three records using
independent global counters. Three paragraph IDs span two page IDs in the
seed-17 smoke corpus. A paragraph cannot be a child of two pages under the
declared hierarchy.

**Required correction:** close/reset a paragraph at every page boundary and
validate `paragraph_id -> exactly one page_id`, `record_id -> exactly one
paragraph_id`, and `line_id -> exactly one record_id`.

### B6. W03 corrupts cross-reference truth

After a `CROSSREF` record, W03 assigns the target product's
`last_product_event` to the source product's item event when no previous target
exists (`generator.py`, current lines 484--486). Later product references can
therefore target an event whose oracle entity is a different product. The
seed-0/512 audit found 5 wrong-entity targets among 44 eligible
`DECLARES_ITEM`/`REFERS_BACK` references; seed 17 found 1 among 29.

**Required correction:** preserve the previous target-product mention or point
to the actual composite event that contains the target product. Add a semantic
referent validator: product-reference targets must contain the referenced
product entity.

### B7. W01 contains wrong state truth and labels fossils as current semantics

In inspection records W01 chooses either a bad or good visible state but always
stores the sampled bad state in `state_after` (current lines 272--273). This
produced 10 contradictions at seed 0/512 and 9 at seed 17/512. W01 also appends
`fossil:*` values to `current_component_semantics` for every fossilized
component (36 events at seed 17), despite the design saying those components
have lost productive/current meaning.

**Required correction:** bind the selected finding once and use it for both
lexical truth and state truth. Keep old component identity only in
`fossilized_component_ids` and genealogy; do not represent it as current
component semantics.

### B8. W04 violates its declared alphabet and mixes old fossil meanings into current semantics

`MAT_CLAY` contains Latin `m`, which is absent from `WORLD_META["alphabet"]`.
Four seed-17 smoke events therefore contain an undeclared visible character.
W04 also places `FOSSIL_LOCATIVE`, `FOSSIL_BODY_PART`,
`FOSSIL_IMPERATIVE`, and `BLEACHED_DEICTIC` in
`current_component_semantics` while simultaneously marking those components
as fossilized. This makes the live-versus-fossil truth internally ambiguous.

**Required correction:** either declare `m` or map it into the frozen invented
inventory, then enforce alphabet membership. Remove old meanings from
`current_component_semantics`; retain current scope/reference/instrument
meaning there and old-source identity only in fossil/genealogy fields.

### B9. Two observation packets use descriptive rather than opaque layout labels

W04 exposes `HEADER`, `BODY`, and `FOOTER`; W09 exposes `BODY` and
`RECORD_ONSET`. These are avoidable English role disclosures, unlike the
opaque `LR*`/`L*` labels used elsewhere. Even where physical position makes a
role inferable, the observation contract prohibits hidden names and the
benchmark should not reward reading an English label.

**Required correction:** remap them bijectively to opaque role IDs before
freezing corpora. Preserve equality and physical layout, not descriptive
glosses.

## Per-world review

Counts below are from the seed-17/512 smoke corpus. `R` is the number of events
with non-`NONE` relation truth; `S` is the number carrying a complete scope
interval. References may be local or cross-record as noted.

| World | System / evolutionary audit | Functional, relation, scope, reference audit | Local status |
|---|---|---|---|
| W01 | Strong organic shorthand: shortening, merger/split, fossils, suppletion, incorporation, register/hand effects; clearly more than substitution. | R=364, S=18; local anaphora and recurrence present. State/fossil truth and separators fail B4/B7. | HOLD |
| W02 | Convincing organic whole-codebook ecology with mergers, frame split, bleaching, fossilized recipes, analogy, exceptions, and attachment. | R=482, S=273; real previous-mention targets. Boundary contradiction and severe W02/W03 carrier mismatch. | HOLD |
| W03 | Valid clean engineered contrast in concept; checksum composition and register transforms make it more than atomic substitution. | R=467, S=519; state and cross-record machinery present, but 46 first-mention edges are target-ineligible and the maintained target index is corrupted by B6. | HOLD |
| W04 | Eight-stage procedural system with nonconcatenative construction mutation, merger/split, analogy, fossils, suppletion, and four schools. | R=27, S=11; local repeat/back-reference exists but relation/scope positives are much sparser than other meaningful worlds. Alphabet and fossil-current truth fail B8; layout labels fail B9. | HOLD |
| W05 | Strong mnemonic rather than word-for-word carrier; merger/split, bleaching, fossils, suppletion, register and hand divergence are implemented. | R=501, S=353; explicit alternatives, recurrence, true cross-record reference, and executable state are present. | Conditional GO after B2/B3 panel normalization |
| W06 | Organic catalogue is nontrivial and auditable: recurrent frames, split/polyfunctional relation forms, fossils, merger, suppletion, and register divergence. | R=119, S=125; cross-record index targets and local scope are present. Independently sampled boundary sides fail B4. | HOLD |
| W07 | Strongest hybrid contrast: words, opaque lot codes, productive base-six quantities, fossils, mergers, polyfunctionality, state and cross-record references coexist. | R=448, S=513; 21 first-occurrence code references are legitimately target-ineligible. | Conditional GO after B2/B3 panel normalization |
| W08 | Genuine multi-school divergence with distinct innovations, mergers, split, fossil compounds, productive cues, suppletion, and allography. | R=447, S=67; rich functional graph and local anaphora, but no true cross-record reference. Boundary sides fail B4 and productive component IDs occupy the binary field under B2. | HOLD |
| W09 | Strong meaningful member of the semantic pair: real route/resource entities, directed relations, persistent states, cross-record amendment/receipt references, organic opacity. | R=193, S=14; semantic contrast is sound, but hierarchy, opaque-label, index-convention, and carrier-match failures remain. | HOLD |
| W10 | Semantics-light purity passes: every semantic oracle field is `NONE`; only production state, form lineage, formal construction/scope, schema, register, and inert fossils remain. This is a useful false-positive control and not a substitution shuffle. | R=0 by design, S=514 structural; no semantic reference. Event index and carrier matching fail B1/B3. | HOLD |

## Panel-level positives

### Independence and diversity

Within the permitted evidence, the sources look independently designed: they
use materially different inventories, event planners, realization mechanisms,
genealogies, state models, and exception structures. The interface freeze
records ten isolated design assignments. Actual session isolation cannot be
proven from the permitted files alone, but there is no source-level sign that
one world is a relabeling of another.

The family panel is broad enough. It includes prose-like technical shorthand,
an organic professional codebook, a clean engineered catalogue, stateful
recipe notation, conservative mnemonic ritual cues, an organic index, a
word/code/quantity hybrid, four diverged schools, a meaningful relation graph,
and a semantics-light formal process. Eight worlds (W01, W02, and W04--W09)
claim and implement organic history, exceeding the six-world requirement.

### More than substitution

No meaningful generator is merely one hidden token mapped to one visible
token. The mechanisms include phrase/clitic fusion, patient incorporation,
checksummed composites, nonconcatenative mutation, whole-cue replacement,
polyfunctional operators, productive numeral structure, school-specific
innovations, contextual mergers, and position/hand effects. W10 is also a
stateful lineage generator rather than a shuffled control.

### Coverage and requested adversarial contrasts

Taken collectively, the panel covers lexical identity, historical ancestry,
live and fossil morphology, function/operator classes, coordinator or
alternative structure, local and cross-record reference, state change, scope,
record schema, and register-local variation. W04 is the only meaningful world
with notably thin explicit relation/scope truth in the smoke corpus; it still
has hundreds of expected positives at full size, so this is a caution rather
than a standalone blocker.

The hidden contrast inside each pair is appropriate. W02 versus W03 isolates
organic history versus explicit engineering; W09 versus W10 isolates real
entity/relation/state semantics versus inert production structure. Once B1 is
fixed, these can support the requested contrasts. In their present carriers,
they cannot.

## Non-outcome-driven repair and re-review gate

Repairs should be limited to the contract-derived defects above. Do not change
semantic prevalence or rendering rules in response to decoder success or
failure. Before issuing GO:

1. Freeze the canonical scalar/index conventions and the two pair carrier
   schedules.
2. Correct B4--B9 in source and regenerate all affected corpora from the same
   frozen seed list.
3. Extend the pre-decoding validator to enforce alphabet membership, scalar
   enums/types, global event-index uniqueness, chosen group-index semantics,
   adjacent-boundary equality, hierarchy nesting, target existence plus the
   W03 product-referent invariant, semantic-null purity, and pair-carrier
   equality/tolerances.
4. Re-run deterministic 512-event audits for all ten worlds and the twenty-seed
   pair audit. Require zero truth/topology violations.
5. Freeze new generator and corpus hashes, then obtain an independent GO
   review before exposing any packet to a decoder.

Until those gates pass, decoding would confound world family with correctable
carrier and truth-schema artifacts and must not begin.

# Final re-review after B1--B9 repairs and pair-protocol correction

## Final decision: GO within the frozen amended scope

This section supersedes the initial HOLD above. The corrected authentic world
panel is suitable for blind decoder exposure, and the two adversarial pairs are
suitable for the **record/line-local comparison defined by
`PAIR_PROTOCOL_AMENDMENT.md` only**. There are no remaining pre-decoding world-
panel blockers in that scope.

This is not a GO for the original full-envelope pair claim. Page, paragraph,
register, hand, layout, glyph-component, morpheme, productive/fossil
morphology, and genealogy outcomes must not enter an adversarial-pair verdict.
They remain valid targets on the authentic full-world corpora. Any later use of
the pair view for an excluded channel would fall outside this review and return
that comparison to HOLD.

The review remained outcome-independent. I inspected no decoder, decoder
output, corpus result/oracle artifact, Voynich row, or other experiment. The
correction was driven by observation-only carrier and truth-integrity audits
before decoding.

## What changed and why it is admissible

The first attempted shared carrier adapter was rejected during re-review. It
repartitioned authentic events into synthetic records and assigned
register/hand labels that were not causal inputs to the renderer. That would
have severed record-schema, scope, and register truth. The adapter and its old
audit were removed; the authentic observations and sealed truth are no longer
rewritten.

The final correction is narrower and truth-safe:

* the main ten corpora remain authentic;
* each pair view selects exactly ten complete authentic records per world and
  seed using observations only;
* paired records match exactly on record length, ordered line profile,
  ambiguity count, and within-record separator histogram;
* page, paragraph, register, hand, layout, and glyph-internal channels are
  explicitly masked and excluded;
* a direct salted hash maps each raw visible type injectively to a common
  fixed-width opaque alphabet, preserving the visible equality and recurrence
  partition without using frequencies or held-seed outcomes; and
* the oracle is not read or rewritten. Event identity, within-record order,
  line membership, internal separators, ambiguity, and scope/reference keys
  remain intact.

The amended method records the original frozen METHOD hash and states the lost
claim scope explicitly. This is a legitimate pre-decoder protocol correction,
not a post-outcome relaxation.

## Final disposition of the original blockers

| Blocker | Final observation-layer result | Disposition |
|---|---|---|
| B1: adversarial carriers unmatched | The original full-page carrier claim was narrowed rather than cosmetically forced. Across 40 seed-pair audits, 400 matched record pairs have exact record/line/separator/ambiguity structure. Final pair views gate TTR, top-type rate, and hapax-fraction differences at `<= 0.10`; excluded higher-level channels are masked. | RESOLVED under the frozen amendment |
| B2: inconsistent truth scalar/type conventions | `productive_morphology` is canonical `TRUE`/`FALSE`/`NONE`; ambiguity is binary; indices are integers; W08 component IDs are in the component field rather than the binary field. | PASS |
| B3: noncanonical event/group indices | All ten normalized 512-event audits have globally monotone event indices and record-local group indices. | PASS |
| B4: contradictory separator sides | Every adjacent authentic observation boundary agrees after canonical duplication. Pair views also preserve internal boundaries and consistently normalize record edges. | PASS |
| B5: W09 paragraphs spanning pages | Authentic hierarchy is nested for paragraph-to-page, record-to-paragraph, and line-to-record in all ten worlds. Pair views mask the excluded page/paragraph channel. | PASS |
| B6: W03 target-product referent corruption | Every eligible sampled `REFERS_BACK` edge targets an event carrying the same product entity; zero wrong-product referents were found. | PASS |
| B7: W01 state/fossil truth | `state_after` is the event's actual resulting state, and obsolete determinative meanings occur only in fossil truth, not current semantics. | PASS |
| B8: W04 alphabet/fossil truth | The clay form uses declared `beta`, every visible character is in the frozen alphabet, and fossil meanings are absent from current component semantics. | PASS |
| B9: descriptive layout labels | Final authentic layout roles are opaque `L<number>` values. Layout is masked entirely in the pair view. | PASS |

## Independent final smoke audit

I regenerated seeds 17 and 18 at a 512-event target for every world and
regenerated seed 17 twice. All ten worlds were deterministic for a fixed seed,
different across seeds, valid against the shared schema, and valid after
canonical normalization. Across the ten seed-17 bundles there were zero:

* observation/oracle event-key mismatches or duplicate event IDs;
* event-index, group-index, separator, or hierarchy violations;
* alphabet, register metadata, hand metadata, or opaque-layout violations;
* missing relation targets or malformed/reversed scope intervals;
* physical records containing multiple `record_schema_id` values;
* overlaps between fossil component IDs and current component semantics;
* W03 wrong-product back-references; or
* W10 non-`NONE` values in the semantic-null fields.

| World | Events | Records | Relation targets | Scope rows | Final assessment |
|---|---:|---:|---:|---:|---|
| W01 | 524 | 46 | 364 | 18 | GO -- organic technical shorthand; state and fossil semantics corrected |
| W02 | 515 | 50 | 471 | 254 | GO -- organic codebook member; authentic carrier retained |
| W03 | 519 | 52 | 422 | 519 | GO -- engineered contrast; referents and scope truth coherent |
| W04 | 521 | 23 | 27 | 11 | GO -- procedural system; sparse relation/scope positives remain a declared coverage caution, not a truth defect |
| W05 | 528 | 27 | 501 | 353 | GO -- mnemonic legacy system with rich relation/scope coverage |
| W06 | 520 | 57 | 119 | 125 | GO -- organic catalogue/index; boundary topology corrected |
| W07 | 513 | 65 | 427 | 513 | GO -- hybrid word/code/quantity system with broad truth coverage |
| W08 | 527 | 33 | 454 | 63 | GO -- multi-school divergence; productive truth and boundaries canonical |
| W09 | 517 | 41 | 193 | 14 | GO -- meaningful semantic-pair member; hierarchy and labels corrected |
| W10 | 514 | 42 | 0 | 514 | GO -- semantics-light purity retained; scopes are formal production structure |

The panel therefore retains the diversity, organic-evolution coverage,
non-substitution mechanisms, and functional/relation/scope/reference coverage
described in the initial review. W10 remains a genuinely semantics-light
false-positive control: its semantic fields are null while its permitted
formal state, lineage, construction, scope, and fossil structure remain
nontrivial.

## Independent pair-view audit

I reproduced the selector on all 40 pair/seed combinations from the frozen
generators. All 40 selections exactly matched the 400-row selection artifact,
including search attempt and recurrence deltas.

I then checked all 80 final observation-only views against independently
regenerated authentic observations (8,686 selected events total):

* zero selected-event identity or ordering differences;
* zero incomplete/duplicate record selections;
* zero record-key, line-profile, separator-histogram, ambiguity-count, or
  record-edge differences;
* zero equality-partition changes or type-code collisions;
* zero deviations from the direct SHA-derived 16-character code assignment;
* zero mask, fixed-width, local-index, or adjacency violations; and
* zero scope intervals with an endpoint outside the selected complete record.

The maximum recurrence differences were:

| Pair | TTR | Top-type rate | Hapax fraction | Exact local carrier channels |
|---|---:|---:|---:|---|
| W02/W03 (`PAIR_CODEBOOK`) | 0.100000 | 0.100000 | 0.097264 | all zero-distance |
| W09/W10 (`PAIR_SEMANTIC`) | 0.096491 | 0.052174 | 0.097222 | all zero-distance |

Some selected W03 and W09 relation targets intentionally point outside the
ten-record view. The amendment permits only **within-view** endpoint scoring,
so these rows are ineligible for the pair endpoint and must not be treated as
wrong references. All authentic full-corpus targets remain available for the
main-world evaluation.

## Freeze and validation integrity

All 41 permitted declared source, design, document, provenance, interface,
pair-artifact, amendment, content, and validation bindings matched their
current bytes. No forbidden sealed data were opened to perform this check.

Key final bindings are:

* world-panel freeze SHA-256:
  `a6902f982eff9058b24748e38535f53c857d9e76928ebafff938b0de988b5b98`;
* world-panel content SHA-256:
  `f9d5745fa639eb28dded20b69d25a71d71813e5a088b9e1ca0e99dc879158320`;
* world-panel validation SHA-256:
  `8fd2c6f94e5691465943251dcf62437f886e4c48b634f7fd1f26dd2c3df6814d`,
  `PASS 26/26`;
* pair-protocol amendment SHA-256:
  `883f4b461ae5b1dc9a10f95ca76ab91e35396be9d6b2d020a8848e14afba0cd9`;
* amendment validation SHA-256:
  `910112e151cf95dc984894553075ee601d239390ecf01a82cc8f813f7d9de3f4`,
  `PASS 9/9`; and
* independent 80-view preflight manifest SHA-256:
  `751239ecc77622e5ce01735576e76c450541393c07ff9e066058d2ca6c843524`,
  with observation-only validation SHA-256
  `ab50f424785a25f9cbe987d6f2c91268f014dfb55076f7e52713c7fc3338f1a5`,
  `PASS 9/9`.

The final gate is therefore **GO for blind decoding**, provided the decoder and
scorer enforce the amended pair exclusions exactly. No further generator or
carrier correction is required before corpus exposure.
