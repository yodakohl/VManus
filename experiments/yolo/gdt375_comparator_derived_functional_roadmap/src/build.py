#!/usr/bin/env python3
"""Register the comparator-derived functional-operator roadmap."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt375_comparator_derived_functional_roadmap"
ART = BASE / "artifacts"
OLD = ROOT / "experiments/yolo/gdt373_functional_operator_roadmap/artifacts/gdt373_hypothesis_registry.tsv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def new_rows() -> list[dict[str, object]]:
    raw = [
        (1,"STATE_TRANSITION_FINGERPRINTS","NEW_COMPARATOR_FIRST_PRIMARY","operator identity is the opaque before-to-after grammatical-state distribution it induces","held-collection state-delta classification; then held-folio Voynich signature transfer","all surface-pattern and next-state routes","surface identity is never a detector feature; require cross-collection transition-vector transfer","fails if position, frequency, or exact identity explains the state delta"),
        (2,"LOCAL_VALENCY_PREDICATE_HEAD","NEW_COMPARATOR_FIRST_PRIMARY","candidate head predicts number and arrangement of locally attached dependents","CoReMA parent_instruction_ordinal head/dependent/arity recovery on held collections","GDT373 VALENCY_RELATION_MARKERS; GDT345","parent links are oracle-only and hidden from all detector inputs","fails if held parent/arity recovery does not beat position and opaque-identity baselines"),
        (3,"REF_ANAPHORA_ELLIPSIS_RECOVERY","NEW_COMPARATOR_FIRST_PRIMARY","current step is structurally incomplete but recoverable from prior-record identity/state","held REF and omitted-information recovery","GDT373 ANAPHORA_ELLIPSIS_REPEAT; GDT343","requires missing-information recovery, not mere token recurrence","fails if previous-record length/frequency or exact cache suffices"),
        (4,"LONG_DISTANCE_CORRELATIVE_PAIRS","NEW_COMPARATOR_FIRST_PRIMARY","separated A...B candidates jointly delimit a scope and predict its terminal state","held paired-end completion and ALTERNATIVE-sensitive branch span","GDT373 PAIRED_CORRELATIVE_OPERATORS; GDT346","long-distance scope pair rather than same-field coordinate coupling","fails if pair co-occurrence follows independent marginals or record length"),
        (5,"NEXT_RESUME_LOCAL_RESET","NEW_COMPARATOR_FIRST_PRIMARY","record/step initializer resumes a prior state or establishes a local reset","held REF/CLOSER-sensitive reset and downstream-state prediction","GDT373 RECORD_DISCOURSE_OPERATORS; GDT126","darnach is calibration analogy only; no lexical matching","fails if record ordinal and generic opener/closer position explain it"),
        (6,"UNTIL_STATE_GATING","NEW_COMPARATOR_FIRST_PRIMARY","operator opens a bounded horizon ending at an intermediate-state transition","held TIME-sensitive gate endpoint and scope length","GDT373 TEMPORAL_PROCESS_OPERATORS","bis is calibration analogy only; requires state gate, not adjacency","fails if duration/position or record length explains the horizon"),
        (7,"AND_VARIABLE_ARITY_CHAINS","NEW_COMPARATOR_FIRST_SECONDARY","same candidate repeats between homogeneous opaque units in X C Y C Z chains","held chain extension and arity","GDT373 COORDINATION_LIST_STRUCTURE","variable-arity homogeneous chain is distinct from one XY-to-XCY insertion","fails if repeated punctuation/field separators explain the chain"),
        (8,"OR_BRANCH_RECONVERGENCE","NEW_COMPARATOR_FIRST_SECONDARY","two alternatives diverge from a shared state and reconverge to a shared downstream state","held ALTERNATIVE branch and reconvergence","GDT373 OR_LIKE_MUTUAL_EXCLUSION; GDT311","requires branch-and-reconverge, not simple X C Y or mutual exclusion alone","fails if alternatives are register variants or lack reconvergence"),
        (9,"POLARITY_NEGATION_INVERSE_TRANSITION","NEW_COMPARATOR_FIRST_SECONDARY","marked transition approximates the inverse of an unmarked state-change vector","held inverse-vector direction and exclusion sensitivity","GDT373 MARKEDNESS_NEGATION_EXCLUSION","not N+X and no negation gloss until comparator transfer","fails if rarity or host licensing explains the inverse-like vector"),
        (10,"COMPOSITIONAL_POINTER_RELATION_PARADIGMS","NEW_COMPARATOR_FIRST_SECONDARY","pointer-like and relation-like anonymous operators combine productively across referents","held unseen pointer-by-relation combination and REF/parent sensitivity","GDT373 DEIXIS_REFERENCE; ASSIGNMENT_EQUATION_POSSESSION","dar- is analogy only; glyph identities forbidden","fails without unseen-base factorial transfer"),
        (11,"EXCLUDE_WITHOUT","NEW_COMPARATOR_FIRST_SECONDARY","candidate removes or blocks an otherwise expected entity/state within a bounded scope","held CoReMA exclusion annotation recovery","GDT373 MARKEDNESS_NEGATION_EXCLUSION","directly calibrated on exclusion oracle, distinct from polarity inverse","fails if excluded entity identity or local content frequency explains it"),
        (12,"LIKE_AS_SAME_COMPARISON","NEW_COMPARATOR_FIRST_SECONDARY","candidate establishes symmetric analogy/comparison relation between opaque entities/states","held analogy and comparison annotation recovery","GDT373 COMPARISON_EQUALITY_RANGE; ANALOGY_PARADIGM_RELATIONS","direct comparator oracle; no equality or lexical gloss","fails if repeated entity identity or fixed record position explains it"),
        (13,"FUNCTION_WORD_INFORMATION_BOTTLENECK","NEW_COMPARATOR_FIRST_DIAGNOSTIC","candidate has high information about structural state but low information about local opaque content identity","held structural-information minus content-information contrast","GDT373 OPEN_CLOSED_CLASS_DIAGNOSTICS","information bottleneck is a detector family, not a POS claim","fails if exact identity or global frequency carries the apparent signal"),
        (14,"SCOPE_LENGTH_HORIZON","NEW_COMPARATOR_FIRST_DIAGNOSTIC","candidate predicts the distance and closure class of its affected downstream span","held horizon length/closure prediction","GDT373 HIERARCHICAL_SPACE_ATTACHMENT_SCOPE","scope length is the fingerprint; surface and semantic labels are hidden","fails if source record length and position suffice"),
        (15,"LATENT_PROCEDURAL_AUTOMATON","NEW_COMPARATOR_FIRST_PRIMARY","low-state ordered automaton START-ACTION-ARGUMENT*-CONDITION/STATE/NEXT-CLOSE inferred without role labels","held-collection latent-state path and hidden-role recovery","GDT340-GDT344; GDT373 TEMPORAL_PROCESS_OPERATORS","states are anonymous until oracle evaluation and remain anonymous on Voynich","fails if order-only nuisance matches the state path"),
    ]
    keys=("priority","hypothesis_family","route_status","formal_signature","held_endpoint","nearest_prior","distinctive_constraint","registered_failure")
    return [dict(zip(keys, row)) for row in raw]


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    new = new_rows()
    with OLD.open(encoding="utf-8", newline="") as handle:
        legacy = list(csv.DictReader(handle, delimiter="\t"))
    registry = list(new)
    for index, row in enumerate(legacy, 16):
        registry.append({
            "priority": index,
            "hypothesis_family": row["hypothesis_family"],
            "route_status": "LEGACY_BROAD_CONSTRAINED" if row["route_status"] != "AUXILIARY_DIAGNOSTIC" else "LEGACY_AUXILIARY",
            "formal_signature": row["formal_signature"],
            "held_endpoint": row["held_endpoint"],
            "nearest_prior": row["nearest_prior"],
            "distinctive_constraint": "Retained as a separate broad GDT373 family; the new comparator-derived families above are not subnotes. " + row["distinctive_constraint"],
            "registered_failure": row["registered_failure"],
        })
    crosswalk = []
    refinements = {
        "STATE_TRANSITION_FINGERPRINTS":"VARIABLE_RECORD_REWRITES;TEMPORAL_PROCESS_OPERATORS",
        "LOCAL_VALENCY_PREDICATE_HEAD":"VALENCY_RELATION_MARKERS;ACTION_IMPERATIVE_HEADS",
        "REF_ANAPHORA_ELLIPSIS_RECOVERY":"ANAPHORA_ELLIPSIS_REPEAT;DEIXIS_REFERENCE",
        "LONG_DISTANCE_CORRELATIVE_PAIRS":"PAIRED_CORRELATIVE_OPERATORS;CONDITIONAL_BRANCHING",
        "NEXT_RESUME_LOCAL_RESET":"RECORD_DISCOURSE_OPERATORS;DEIXIS_REFERENCE",
        "UNTIL_STATE_GATING":"TEMPORAL_PROCESS_OPERATORS;HIERARCHICAL_SPACE_ATTACHMENT_SCOPE",
        "AND_VARIABLE_ARITY_CHAINS":"COORDINATION_LIST_STRUCTURE",
        "OR_BRANCH_RECONVERGENCE":"OR_LIKE_MUTUAL_EXCLUSION;CONDITIONAL_BRANCHING",
        "POLARITY_NEGATION_INVERSE_TRANSITION":"MARKEDNESS_NEGATION_EXCLUSION",
        "COMPOSITIONAL_POINTER_RELATION_PARADIGMS":"DEIXIS_REFERENCE;ASSIGNMENT_EQUATION_POSSESSION",
        "EXCLUDE_WITHOUT":"MARKEDNESS_NEGATION_EXCLUSION",
        "LIKE_AS_SAME_COMPARISON":"COMPARISON_EQUALITY_RANGE;ANALOGY_PARADIGM_RELATIONS",
        "FUNCTION_WORD_INFORMATION_BOTTLENECK":"OPEN_CLOSED_CLASS_DIAGNOSTICS",
        "SCOPE_LENGTH_HORIZON":"HIERARCHICAL_SPACE_ATTACHMENT_SCOPE;EMBEDDING_COMPLEMENTIZERS",
        "LATENT_PROCEDURAL_AUTOMATON":"TEMPORAL_PROCESS_OPERATORS;RECORD_DISCOURSE_OPERATORS",
    }
    for row in new:
        crosswalk.append({
            "new_family": row["hypothesis_family"],
            "related_gdt373_families": refinements[row["hypothesis_family"]],
            "distinct_family": "YES",
            "why_not_a_subnote": row["distinctive_constraint"],
            "comparator_oracle_endpoint": row["held_endpoint"],
        })
    detector = [
        ("STATE_TRANSITION_FINGERPRINTS","ALL_HIDDEN_CLASSES","before/after recurrence-state delta; downstream novelty/return/closure horizon"),
        ("LOCAL_VALENCY_PREDICATE_HEAD","PREDICATE_HEAD_WITH_DEPENDENTS;PARENTED_DEPENDENT;HIGH_VALENCY_HEAD","local dependent density and repeated-entity attachment; parent links hidden"),
        ("REF_ANAPHORA_ELLIPSIS_RECOVERY","REF","previous-record overlap, omitted/recovered identities, recurrence horizon"),
        ("LONG_DISTANCE_CORRELATIVE_PAIRS","ALTERNATIVE","separated recurrent endpoint pair, scope length, paired completion"),
        ("NEXT_RESUME_LOCAL_RESET","REF;CLOSER","record-boundary reset/resumption and following-state delta"),
        ("UNTIL_STATE_GATING","TIME","bounded horizon and intermediate-state closure"),
        ("AND_VARIABLE_ARITY_CHAINS","PARENTED_DEPENDENT","homogeneous repeated chain and variable arity"),
        ("OR_BRANCH_RECONVERGENCE","ALTERNATIVE","shared predecessor, alternative paths, shared downstream reconvergence"),
        ("POLARITY_NEGATION_INVERSE_TRANSITION","EXCLUSION","inverse transition-vector similarity"),
        ("COMPOSITIONAL_POINTER_RELATION_PARADIGMS","REF;PARENTED_DEPENDENT","cross-identity pointer/relation combination"),
        ("EXCLUDE_WITHOUT","EXCLUSION","expected-identity deficit inside bounded scope"),
        ("LIKE_AS_SAME_COMPARISON","ANALOGY;COMPARISON","symmetric repeated-entity relation and shared-state path"),
        ("FUNCTION_WORD_INFORMATION_BOTTLENECK","ANY_FUNCTIONAL_CLASS","structural-state information minus local opaque-identity information"),
        ("SCOPE_LENGTH_HORIZON","ALTERNATIVE;TIME;REF","downstream affected-span length and closure"),
        ("LATENT_PROCEDURAL_AUTOMATON","ANY_FUNCTIONAL_CLASS","anonymous ordered state path; oracle names hidden until evaluation"),
    ]
    dkeys=("hypothesis_family","hidden_oracle_endpoints","form_blind_signature","development_protocol","transfer_rule")
    detector_rows=[dict(zip(dkeys, (*r,"leave-one-CoReMA-collection-out; train on five only","transfer only if structure beats nuisance and opaque-identity baselines in >=4 held collections"))) for r in detector]

    paths = [
        ART / "gdt375_ranked_hypothesis_registry.tsv",
        ART / "gdt375_gdt373_crosswalk.tsv",
        ART / "gdt375_detector_contract.tsv",
    ]
    write_tsv(paths[0], registry)
    write_tsv(paths[1], crosswalk)
    write_tsv(paths[2], detector_rows)
    result = {
        "schema":"GDT375_RESULT_V1",
        "status":"COMPARATOR_DERIVED_FUNCTIONAL_FAMILIES_REGISTERED_BEFORE_ORACLE_EVALUATION",
        "new_distinct_families":len(new),
        "legacy_distinct_families":len(legacy),
        "total_ranked_families":len(registry),
        "oracle_values_evaluated":False,
        "voynich_scored":False,
        "f84_accessed":False,
        "inputs":{str(OLD.relative_to(ROOT)):sha(OLD)},
        "outputs":{str(p.relative_to(ROOT)):sha(p) for p in paths},
        "implementation":{str((BASE/'src/build.py').relative_to(ROOT)):sha(BASE/'src/build.py')},
        "claim_ceiling":"RANKED_COMPARATOR_FIRST_HYPOTHESIS_REGISTRY_ONLY",
    }
    result["content_hash"] = hashlib.sha256(json.dumps(result,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    (ART / "gdt375_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
