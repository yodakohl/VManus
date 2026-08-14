# GDT002 visual-grammar constraints method

Status: **EXPLORATORY HYPOTHESIS GENERATION ACTIVE; NO VALIDATION HYPOTHESIS FROZEN**.

## Question and claim ceiling

Can already-confirmed source-native Voynich grammar and independently described
visible page geometry jointly constrain a small anonymous semantic-role
vocabulary? The first checkpoint builds the evidence layers and exposes their
limits. It assigns no role and opens no holdout text.

The allowed future role vocabulary is:

`OBJECT_ENTITY`, `PROCESS_OPERATION`, `PROCESS_STAGE`, `STATE_PROPERTY`,
`RELATION`, `SOURCE_DESTINATION`, `POSITION`, `QUANTITY_DEGREE`,
`CASE_INDICATION`, `MATERIAL_SUBSTANCE`, `DISCOURSE_RECORD_STATE`, `UNKNOWN`.

These are latent hypotheses, not translations. Historical terms such as
“nymph”, “pool”, “tube”, and “waterfall” remain quoted source descriptions;
analysis uses neutral figure, bounded-region, linear-component, position, and
connection fields.

## Evidence order

1. Read the cached human catalogue and exact-locus annotations without text
   strings or formal features.
2. Normalize only explicitly described geometry and uncertainty into
   `gdt002_visual_inventory.tsv`.
3. Carry prior AI visual judgments in `prior_ai_visual_state`; never relabel
   them human evidence.
4. Project the frozen source-native grammar only after the visual inventory is
   fixed.
5. Join f80r/f82r for a descriptive discovery atlas.
6. Generate f84r mechanically but publish only its row counts and SHA-256
   commitments. Do not inspect or use its exact projection payload.

No image, OCR, CLIP, embedding, object detection, segmentation, captioning, or
automatic visual classification is used in this checkpoint. There are zero
`AI_DIRECT_VISUAL_OBSERVATION` rows.

## Visual evidence and ownership

The inventory distinguishes `DIRECT_LEADER`, `SAME_ENCLOSURE`,
`CONNECTED_COMPONENT`, `PROXIMITY_ONLY`, and `UNKNOWN`. Only f82r.10 reaches
`CONNECTED_COMPONENT` from a human statement that the label is on the
cross-shaped component. “Above”, “near”, “between”, “below”, and array/group
relations remain `PROXIMITY_ONLY`; prior RRA001 judgments remain separate.

Page-level catalogue clauses and exact-locus comments are overlapping views,
not independent witnesses. The derived annotation TSV, Stolfi source comments,
crosswalk, and VIB heritage are likewise not counted as replication.

## Frozen formal projection

`gdt002_grammar_projection.tsv` is the full discovery-page alternate-reading
layer. It joins `source_sta_group_alignment.tsv` and
`source_separator_transcription.tsv` by `source_group_id`, retaining exact raw
source groups, separators, STA codes/families, and alternatives for ZL3b,
IT2a, and RF1b. The editions are alternate readings of one manuscript.

`gdt002_grammar_consensus_projection.tsv` is a high-confidence source-native
view. It uses `source_native_structural_interlinear_v1.tsv` and explicitly
marks every locus as `STRICT_EXACT_FAMILY`,
`EXACT_FAMILY_WITH_ALTERNATIVE`, or `NO_EXACT_FAMILY_CONSENSUS`.

The projection excludes cached full-corpus fitted tags (`exact_first_last`,
edge-core tendencies, opening/closing features, transition labels, and favored
paths) from predictive use. They would be transductive for this holdout.
Legacy `pre_grounding_interlinear.tsv` roots, roles, carriers, and parser
semantics are not used. Page, section, Currier, hand, code, kind, scope, and
paragraph start/end flags are audit metadata and may not be predictors of
visual roles.

Physical-folio isolation applies jointly to all readings. Any later training
rule must purge every f80*, f82*, and f84* locus when those physical folios are
held.

## Holdout contract

f80r and f82r are discovery pages. f84r visual descriptions are visible, but
its exact GDT002 formal payload is analysis-sealed in
`gdt002_f84r_holdout_projection_commitment.json`. It may be opened only after
all of the following are frozen:

- visual feature schema;
- role vocabulary;
- primitive grammar features;
- complexity and exception penalties;
- control permutations;
- the retained discovery-world beam and deterministic tie-break.

The future `gdt002_frozen_holdout_prediction.json` must be written before the
committed f84r payload is exported, inspected, joined, or scored. The builder
mechanically materialized the rows in isolated memory solely to compute the
published commitments. This checkpoint deliberately does not create that
prediction because no solver has yet been specified or run.

This is not a pristine observer-blind holdout: f84r strings and prior formal
work have appeared elsewhere in the repository and in earlier audits. That
exposure is disclosed. The valid safeguard is procedural and mechanical: the
GDT002 solver must be frozen from f80r/f82r, then scored deterministically
against the committed f84r projection without manual repair or tuning.

## Joint solver design, currently capacity-blocked

The present panel does not identify this solver. Its 18 strict text-linked
discovery records are isolated one-group labels with a common line-start/line-
end boundary pattern. Mapping the two repeated exact family expressions
directly to roles would merely rename the closed exact-label route. Therefore
no joint world is scored, no beam is selected, and no f84r prediction is
frozen. The following remains a prospective design only after acquisition of
a new repeated author-visible relation with contrasting formal states and held
support.

A world assigns selected family/construction/position predicates to at most a
small number of roles. It scores the joint correspondence of:

- repeated visual group and ordinal structure;
- conservative ownership class;
- containment and drawn connection topology;
- source-native family sequence and boundary profiles;
- factual position within a line/label record;
- reading uncertainty.

The beam will retain 50–200 worlds. The objective is a two-part MDL/posterior
score: mapping-library cost + role assignments + residual visual/formal
misfit + explicit page exceptions. No role gets a page-specific synonym for
free. Hard ownership contradictions cannot be averaged away.

Matched controls preserve exactly the information available to the role
world: within-page visual-unit permutations, ownership-compatible label
permutations, repetition-group permutations, frequency-preserving family
permutations, page-conditioned root/family permutations, and
geometry-preserving assignments. GDT001 source codes are adversarial baselines,
not discovery engines.

## Success and failure

Success would require a frozen discovery world to improve held f84r role
prediction without changing the dictionary. f75v and f67r2 cannot be treated
as fresh confirmation for their already-consumed label/edge mechanisms; they
could be used later only if a genuinely new observable relation, not scored by
RTA001 or prior transfer screens, is preregistered.

This checkpoint can establish only a provenance-bound atlas and risky joint
constraints. It establishes no object name, process, material, word, POS,
sound, language, cipher, plaintext, meaning, or translation.

## Exploratory discovery supersession

The capacity-blocked language above records the first validation-first
checkpoint. It remains historical, but it no longer governs YOLO discovery.
The current exploratory stage uses every acquired CONTACT, CLEAR_GAP, and
UNCERTAIN observation, including one-sided arrays. The old f89, f88/f102, and
complete-array gate outcomes stay recorded as failures of their preregistered
procedures; they are not retroactively called successful.

Discovery canonicalizes inherited observations by physical locus, retains
UNCERTAIN as missing plus both deterministic sensitivity assignments, and
joins only source-native family, component, group, boundary, and primary
member-code fields. It may search primitive predicates and compact depth-two
AND/OR combinations. It reports conditional mutual information, two-part code
improvement, exact within-array permutations, cyclic rotations,
length/group-count sensitivity, leave-one-array/folio behavior, and separate
ZL3b/IT2a/RF1b masks. These are ranking diagnostics, not confirmation gates.

Folio, page, array, ordinal, reviewer provenance, section, Currier, hand,
layout code, kind, and grammar scope are audit/confound fields, never candidate
meanings. CONTACT/GAP, existing human layout, and BFE enclosure observations
are analyzed as separate channels because pooling them would manufacture
section/Currier/hand effects. Exact ordered surfaces, legacy parser roles,
historical-language models, and lexical glosses remain outside GDT002.

The formal f84r payload remains sealed. A candidate may be frozen for f84r
validation only in a later checkpoint with its feature, direction, penalty,
uncertainty rule, and score fixed in advance. Until then every ranked candidate
is postselected exploratory evidence and may be dirty, unstable, sparse, or
page-confounded.

## CKPT010 targeted exposed-data transfer

CKPT010 performs no new feature search. It takes exactly the two page-local
CKPT009 predicates `FAMILY_PREFIX_3:AQA` and `FAMILY_3GRAM:ACA`, preserving
their direction and source-native definition. Existing human annotations
define all visual states before the selected records are joined to formal
data. f75v/f67r2 test the row/register predicate; the complete non-f84r set of
unhedged, exclusive apparatus-versus-figure annotations with consensus
`kind=L` records tests the apparatus predicate. One-sided pages remain
descriptive observations; exact permutations use only pages containing both
states.

These pages are explicitly exposed discovery data. f75v/f67r2 cannot confirm
their prior consumed layout mechanisms, and f77/f82 also have extensive prior
route exposure. A same-direction result may rank a candidate but cannot turn
this checkpoint into validation. The sealed f84r formal projection remains
unread, unjoined, and unscored.

## CKPT011 source-only replication-capacity audit

After CKPT010, the current exact human annotation layer is exhaustively
screened for a genuinely independent apparatus/figure page without consulting
Voynich forms. Every non-f84r label-layout row is classified from its existing
human tags as apparatus-exclusive, figure-exclusive, mixed, or outside scope;
hedged and unhedged counts remain separate. A clean page requires at least two
unhedged exclusive observations of each state on a physical folio other than
f77 and f82. This rule diagnoses the capacity of the cached annotation layer;
failure does not close permissive exploration or reassign mixed observations.
The f84r formal payload remains excluded before row classification.

## CKPT012 f83r post-exposure direct visual reinspection

The source-only CKPT011 fallback fixes f83r.45/.46/.50/.51 before native image
review. Direct observations use the exact official canvas and fixed IIIF crops,
are labeled `AI_DIRECT_VISUAL_OBSERVATION`, and remain separate from inherited
human tags. Visible local geometry may correct a tag's scope, but proximity
does not become ownership. Formal values are explicitly already exposed, so
the ensuing fixed four-row comparison is post-exposure exploration, not
validation. f84r remains excluded.

## CKPT013 falsification-first morphology

The fixed candidates are `AR`, `OL`, `DAL`, `DAR`, `SY`, `TE`, `TEE`, `DY`,
and the left contrasts `d-/s-/q-/o-/ot-`. Occurrences are scanned only within
manual source groups. The nearest-basic-EVA column is a lossy display of the
source-native STA alignment; cleaner-created fragment boundaries are never
used as spaces. ZL3b, IT2a, and RF1b are alternate readings and are consolidated
as one physical inventory with explicit disagreement states.

Falsifiers are free/bound support, position concentration, unique host types,
exact insertion/replacement partners, manual split/join analogues, label/prose
density per source symbol, and page-conditioned contrasts among explicit human
visual descriptions. Unmentioned description terms are UNKNOWN, not negative.
Ranks describe formal reusability only. A semantic operator or slot requires a
stable independently annotated role and is not inferred from productivity.
The f84r formal payload is skipped before formal fields are retained or scored.
