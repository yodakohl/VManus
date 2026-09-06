# GDT858 — held-face versus held-leaf metadata audit

Static GDT808 physical_folio() matches f[digits][rv], retaining recto/verso;
leaf_folio() separately removes it. Its primary model trains on source-axis
events with carrier!=held_carrier AND event.folio!=held face. Test events
match target axis, held carrier and held face. The exclusion flag verifies
that same face-valued field. GDT809 retains the same face normalizer, but its
actual folds are not reconstructed here. Old code remains byte-frozen.

Only two fixed GDT808 primary models: M01_L_TO_L and M02_DY_TO_DY,
population CORE13. First project source metadata through query-tsv with the
exact selectors, allow-values and columns in SPEC. Event page allowance is
current179; fold allowance is its unique faces after removing panel digits.
f84/f84r are forbidden before payload materialization. Projected event fields
are event_id/carrier/axis/page/physical_folio; fold fields are model/population,
source/target axes, held carrier/face, train/test counts and exclusion flags.
No outcomes, predictions, scores, text or images. Only after projection filter
to the two models and CORE13. Hashing source files for provenance before GO
is allowed; no TSV body interpretation before public registration.

Normalize a face as fN followed by r/v, and a physical leaf as fN. Reconstruct
each projected primary fold using the exact registered source predicates.
Crosscheck train/test counts and both exclusion flags against published
metadata. For each fold count retained training events whose leaf equals
held leaf but whose face differs, after source-axis AND carrier exclusion.
Save all such event IDs and one deterministic lexicographically smallest
retained-train / held-test event-ID pair for every affected fold. Save every
primary fold's counts, including zeros, and unique event selectors/faces/
leaves plus leaves represented on both faces. Never call the entire4538fold
collection audited; state the actual two-model coverage. Compare that coverage
with the 569/394 primary-fold counts declared in GDT808 src/run.py:66
(EXPECTED_MODEL_FOLDS, enforced by preflight_relation_folds at lines658–659),
flag incompleteness. Source: experiments/yolo/gdt808_exact_relation_slot_residual_bridge/src/run.py.

Any count/flag/coverage mismatch gives SOURCE_RECONSTRUCTION_MISMATCH, with
all diagnostics and no unqualified reconstruction claim. When metadata match
and a counterexample exists, the audited split holds out faces, not whole
physical leaves. This does not quantify a performance penalty or imply bad
predictions. Zero counterexamples clears neither GDT809 nor all models.
No refit, repair, score access, other model or scope expansion.

Controls before data: f104r and f104v share a leaf but differ in face;
f86v3→f86v→f86; f84 variants stay forbidden. Other-face/different-carrier
source-axis events survive the old rule, same carrier does not, wrong axis
does not, and a same-face panel does not. A proper whole-leaf rule excludes
the surviving opposite-face example. Independent validator uses separate
set reconstruction and reissues both exact guarded metadata queries after
GO to verify byte-projection hashes, rather than trusting runner outputs.

Budget15min total07:12:15–07:27:15UTC. Root reviews before bind-lock,
publicly registers, then sends GO before source interpretation. Root owns
registry and git; this experiment changes no legacy source or model.
