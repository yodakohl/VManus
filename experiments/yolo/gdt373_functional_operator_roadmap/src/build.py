#!/usr/bin/env python3
"""Build the static, pre-search GDT373 functional-operator registry."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt373_functional_operator_roadmap"
ART = BASE / "artifacts"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def hypotheses() -> list[dict[str, object]]:
    raw = [
        (1,"VARIABLE_RECORD_REWRITES","NEW_PRIMARY","X<->NX; X<->XN; XY<->XCY; AXB<->APXQB over atomic tuple records","held exact/near-exact record counterpart after training-only rewrite discovery","GDT003;GDT345","differs by record and boundary conditioning; no character edits or target-state features","fails if gain is explained by tuple frequency, placement, or exact predecessor"),
        (2,"HIERARCHICAL_SPACE_ATTACHMENT_SCOPE","CONSTRAINED_NEW_ENDPOINT","same tuple rewrite at source-native separator and reset scopes","held scope choice and affected-span prediction","GDT126;GDT273;CHE_JOIN_SPACE_ARCHIVE","new only for transferable rewrite span; marginal space association is duplicate","fails without cross-scope transfer or if source length explains span"),
        (3,"RECORD_DISCOURSE_OPERATORS","NEW_PRIMARY","prior-record-conditioned continuation, resumption, restart, or shortening","held next-record length/boundary/rewrite class","GDT120;GDT125;GDT126","distinct from weak OPEN profile selection by exact variable rewrite endpoint","fails if record ordinal and page profile suffice"),
        (4,"VALENCY_RELATION_MARKERS","CONSTRAINED_NEW_ENDPOINT","operator changes count or arrangement of opaque dependent fields","held arity delta conditional on source record and layout","GDT143-GDT148;GDT345","no visual relation or PAGE_HOST content; source-side structural arity only","fails if operator has no reusable arity signature"),
        (5,"COORDINATION_LIST_STRUCTURE","NEW_PRIMARY","symmetric tuple/field insertion, parallel repeat, or list extension","held parallel-branch or repeat completion","GDT273;GDT341-GDT343","record rewrite not semantic event flow or first-order field chain","fails if apparent symmetry is length/position recurrence"),
        (6,"ANAPHORA_ELLIPSIS_REPEAT","NEW_PRIMARY","short record predictable from immediately prior complete record by deletion/repeat pointer","held omitted-span or resume-class prediction","GDT165;GDT341-GDT343","uses cross-record structural reuse, not next-host identity or semantic concepts","fails if exact record cache/frequency matches or wins"),
        (7,"PAIRED_CORRELATIVE_OPERATORS","NEW_PRIMARY","two separated rewrite sites co-occur beyond marginals","held paired-site completion from source-side context","GDT346;GDT347","record-level paired rewrite; not target-coordinate compatibility graph","fails if coupling null preserving marginal rewrite rates explains it"),
        (8,"MARKEDNESS_NEGATION_EXCLUSION","EXPLORATORY_ANONYMOUS_ONLY","rare optional operator mutually excludes a common construction","held exclusion and downstream-state signature","GDT087;GDT311","anonymous EXCLUSION_LIKE only; no negation gloss","fails if rarity/host licensing explains exclusion"),
        (9,"AGREEMENT","NEW_SECONDARY","separated fields covary in rewrite class conditional on record/layout","held distant partner class","GDT077;GDT346","not same-group wrapper-right coupling; requires separated scope","fails if exact tuple identity or shared position explains covariation"),
        (10,"ASSIGNMENT_EQUATION_POSSESSION","LOW_CAPACITY_ANONYMOUS","reversible or directional two-field relation template","held relation orientation/partner arity","GDT143-GDT148;GDT339-GDT343","no referent, possession, or equality gloss; formal RELATION_LIKE only","fails without recurrent cross-host two-place template"),
        (11,"QUANTIFICATION_PLURALITY","EXPLORATORY_ANONYMOUS_ONLY","operator predicts multiplicity, repeat count, or record-size delta","held count distribution conditional on layout/source","NUMBER_CALENDAR_CLOSED;GDT121","no number value or plurality gloss","fails if length/opportunity baseline explains counts"),
        (12,"TEMPORAL_PROCESS_OPERATORS","LOW_CAPACITY_ANONYMOUS","ordered continuation/state-change rewrite over records","held direction and downstream transition","GDT340-GDT344","source-only SEQUENCE_LIKE behavior; comparator event semantics remain uncalibrated","fails if order-only or exact identity baseline wins"),
        (13,"OR_LIKE_MUTUAL_EXCLUSION","NEW_SECONDARY","two alternative rewrite classes occupy the same licensed source context but do not co-occur","held alternative choice and exclusion","GDT311;GDT346","distinct from rare markedness by symmetric alternatives","fails if alternatives are register allomorphs or host-disjoint"),
        (14,"COMPARISON_EQUALITY_RANGE","LOW_CAPACITY_ANONYMOUS","paired/repeated fields with symmetry or bounded interval structure","held pair/range completion","GDT273;NUMBER_CALENDAR_CLOSED","formal symmetry only; no quantity/equality meaning","fails without multiple independent base records"),
        (15,"CONDITIONAL_BRANCHING","NEW_SECONDARY","one source state predicts two structured continuation branches","held branch existence and branch-type distribution","GDT120;GDT125","record branching, not latent class naming","fails if page-local template mixture explains branches"),
        (16,"ACTION_IMPERATIVE_HEADS","LOW_CAPACITY_ANONYMOUS","record-initial optional operator changes continuation architecture","held downstream record signature","GDT334-GDT336;GDT311","anonymous entry-controller only, not action/POS","fails if known line-entry renderer and position suffice"),
        (17,"EMBEDDING_COMPLEMENTIZERS","LOW_CAPACITY_ANONYMOUS","operator introduces nested field span and predictable closure","held nested boundary/closure completion","GDT273;GDT345","hierarchical rewrite endpoint rather than guessed complementizer","fails if ordinary field length and DY/B3 explain nesting"),
        (18,"ARGUMENT_ALTERNATIONS","NEW_SECONDARY","same opaque base record alternates dependent-field count/order with stable rewrite","held alternate construction for unseen base","GDT127;GDT345","whole-record alternation, not one-slot substitution","fails without unseen-base transfer"),
        (19,"DEIXIS_REFERENCE","LOW_CAPACITY_ANONYMOUS","record-position-sensitive operator resumes or points to a prior structural object","held antecedent distance/class","GDT165;GDT166","no demonstrative gloss; exact prior-record structural reference only","fails if recency/frequency/page position baseline wins"),
        (20,"REGISTER_SPECIFIC_ALLOMORPHY","CONSTRAINED_EXTENSION","same record rewrite realized by different atomic operators across registers","held cross-register rewrite equivalence","GDT017;GDT025;GDT077;GDT087;GDT091","q/DY/EO and wrapper facts are priors, not rediscoveries","fails if equivalence needs tuple merging or substring identity"),
        (21,"ANALOGY_PARADIGM_RELATIONS","DUPLICATE_UNLESS_RECORD_LEVEL","paradigm relation only when induced from whole-record rewrite behavior","held unseen-base record variant","GDT003;GDT078;MINIMAL_PAIRS_CLOSED","character rectangles and isolated minimal pairs are forbidden duplicates","do not run if reducible to surface/string edit"),
        (22,"OPEN_CLOSED_CLASS_DIAGNOSTICS","AUXILIARY_DIAGNOSTIC","operator-context diversity versus opaque tuple inventory concentration","held type recurrence/diversity and operator productivity","GDT162-GDT167;GDT327","diagnostic for candidate interpretation only; not an operator or lexical claim","fails as evidence if exact identity/frequency entirely determines class"),
    ]
    keys=("priority","hypothesis_family","route_status","formal_signature","held_endpoint","nearest_prior","distinctive_constraint","registered_failure")
    return [dict(zip(keys,row)) for row in raw]


def crosswalk() -> list[dict[str, object]]:
    raw = [
        ("STRING_PARADIGM","GDT003;GDT078;GDT094","CLOSED_AS_PRIMARY","character/subword transformations and rectangle completion","use only atomic-tuple record rewrites with no glyph similarity"),
        ("SYNONYM_MINIMAL_PAIR","MINIMAL_PAIRS_ALLOGRAPHY_AND_SYNONYMS;GDT127","CLOSED","isolated substitution/equivalence and one-slot exemplars","require recurrent variable rewrite over unrelated base records and held folios"),
        ("MARGINAL_SCOPE_ORDER","GDT126;GDT273;archived hierarchical-space work","CONSTRAINED","boundary texture and coarse field-order effects","predict rewrite span/attachment or record shortening beyond length/position"),
        ("NEXT_STATE_OPERATOR","GDT311;GDT345;GDT346;GDT347","CLOSED_AS_PRIMARY","licensed pair choice and source-state to target-coordinate smoothing","predict occurrence of a whole record variant; target state never a feature"),
        ("PAGE_HOST_SUBSTRING_CONTEXT","GDT094;GDT162-GDT167","CLOSED","substring classes, substitutions, host-neighbor/context geometry","keep GDT327 tuple atomic and forbid PAGE_HOST/glyph features"),
        ("EXTERNAL_RELATION_GROUNDING","GDT143-GDT148;GDT367-GDT369","CLOSED_FOR_THIS_ROUTE","visual/referent correlations and posthoc PAGE_HOST retrieval","source-internal operator behavior only"),
        ("COMPARATOR_EVENT_SEMANTICS","GDT339-GDT344","NOT_CALIBRATED","anonymous event/flow graphs did not add beyond identity","comparators may calibrate machinery but cannot name Voynich functions"),
        ("REGISTER_RENDERER","GDT017;GDT025;GDT077;GDT087;GDT091;GDT314-GDT323","ESTABLISHED_FORMAL_PRIOR","register-conditioned q/s/wrapper/right/DY placement","treat as nuisance/prior; test only whole-record allomorphic rewrite transfer"),
    ]
    keys=("prior_family","experiments","status","what_is_closed_or_known","new_route_boundary")
    return [dict(zip(keys,row)) for row in raw]


def signature_schema() -> list[dict[str, object]]:
    raw = [
        ("candidate_id","IDENTITY","stable hash of family plus rewrite signature","REQUIRED"),
        ("hypothesis_family","IDENTITY","one GDT373 registered family","REQUIRED"),
        ("rewrite_type","FORM","PREFIX_INSERT|SUFFIX_INSERT|INTERNAL_INSERT|DELETE|REPLACE|PAIRED|BOUNDARY_SPLIT_JOIN|DUPLICATE|SHORTEN_RESUME","REQUIRED"),
        ("operator_tuple_ids","FORM","opaque atomic GDT327 tuple IDs only","REQUIRED"),
        ("scope_level","SCOPE","FIELD|PHYSICAL_LINE|DRAWING_RESET|RECORD_PAIR","REQUIRED"),
        ("symmetry","BEHAVIOR","forward/reverse support and directionality","REQUIRED"),
        ("valency_delta","BEHAVIOR","change in dependent field or branch count","REQUIRED"),
        ("host_diversity","CAPACITY","distinct opaque base records after exact deduplication","REQUIRED"),
        ("optionality","BEHAVIOR","operator present/absent in matched licensed contexts","REQUIRED"),
        ("mutual_exclusion","BEHAVIOR","co-occurrence deficit against matched marginals","REQUIRED"),
        ("downstream_state_change","BEHAVIOR","change after rewritten span, never used as discovery feature","REQUIRED"),
        ("record_length_effect","NUISANCE","record/field/group length delta","REQUIRED"),
        ("physical_folios","TRANSFER","distinct physical folios; editions not multiplied","REQUIRED"),
        ("registers","TRANSFER","distinct registers and register-specific flag","REQUIRED"),
        ("held_gain_bits","SCORE","held-folio gain over strongest matched baseline","REQUIRED"),
        ("positive_held_folios","SCORE","folio-balanced sign count","REQUIRED"),
        ("local_p","CONTROL","candidate-local matched null tail","REQUIRED"),
        ("max_search_p","CONTROL","full-library max-search tail","REQUIRED"),
        ("selector_cost_bits","MDL","log2 full enumerated candidate library plus operator form cost","REQUIRED"),
        ("reading_stability","ROBUSTNESS","agreement and alternate-reading sensitivity","REQUIRED"),
        ("anonymous_behavior_label","INTERPRETATION","optional *_LIKE label; semantic state remains UNASSIGNED","OPTIONAL"),
        ("confounds","AUDIT","page/register/layout/position/frequency/opportunity caveats","REQUIRED"),
    ]
    keys=("field","category","definition","requirement")
    return [dict(zip(keys,row)) for row in raw]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    hp = ART / "gdt373_hypothesis_registry.tsv"
    cp = ART / "gdt373_prior_route_crosswalk.tsv"
    sp = ART / "gdt373_candidate_signature_schema.tsv"
    write_tsv(hp, hypotheses())
    write_tsv(cp, crosswalk())
    write_tsv(sp, signature_schema())
    inputs = [
        ROOT / "VOYNICH_ACTIVE_STATE.md",
        ROOT / "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv",
        ROOT / "experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv",
        ROOT / "gdt327_result.json",
    ]
    outputs = [hp, cp, sp]
    implementation = [BASE / "src/build.py"]
    result = {
        "schema": "GDT373_RESULT_V1",
        "status": "FUNCTIONAL_OPERATOR_HYPOTHESES_REGISTERED_BEFORE_SEARCH",
        "hypothesis_families": len(hypotheses()),
        "new_primary": sum(x["route_status"] == "NEW_PRIMARY" for x in hypotheses()),
        "constrained_or_secondary": sum(x["route_status"] not in {"NEW_PRIMARY", "DUPLICATE_UNLESS_RECORD_LEVEL", "AUXILIARY_DIAGNOSTIC"} for x in hypotheses()),
        "candidate_forms_scored": 0,
        "semantic_roles_assigned": 0,
        "next_experiment": "GDT374_COMMON_FUNCTIONAL_OPERATOR_DISCOVERY",
        "f84_accessed": False,
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        "outputs": {str(p.relative_to(ROOT)): sha(p) for p in outputs},
        "implementation": {str(p.relative_to(ROOT)): sha(p) for p in implementation},
        "claim_ceiling": "RANKED_DEDUPLICATED_ROUTE_REGISTRY_ONLY",
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (ART / "gdt373_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
