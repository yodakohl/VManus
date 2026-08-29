#!/usr/bin/env python3
"""Hash-bound, contract-only Stage-1 necessary-bound audit for GDT615.

This program is deliberately not a Stage-1 world solver.  It reads only the
two public preregistrations, the immutable Stage-0 mapping commit, the frozen
train-substring table, and the directed merge tree.  It neither selects paid
locations nor opens any held, LM-confirm, target, f84, or f84r input.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


SCHEMA = "gdt615-stage1-contract-necessary-bound-audit-v1"
DECISION_INFEASIBLE = "CONTRACT_NECESSARY_BOUND_PROVES_W0_INFEASIBLE"
DECISION_NOT_DECISIVE = "CONTRACT_NECESSARY_BOUND_NOT_DECISIVE"

INPUT_SPECS: Mapping[str, tuple[str, str]] = {
    "GDT614_PREREGISTRATION.md": (
        "experiments/yolo/gdt614_core_run_macro_recovery/PREREGISTRATION.md",
        "552b3ee1cda663157c793ab30434aa67aef3ab534a94117bdb62e8d33b9600d1",
    ),
    "GDT615_PREREGISTRATION.md": (
        "experiments/yolo/gdt615_joint_output_permutation_recovery/PREREGISTRATION.md",
        "283b3d0199064eaeb7f1197ca1fde743bb64e7236fa43e6083ccbdb5261c5485",
    ),
    "STAGE0_MAPPING_COMMIT.json": (
        "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/"
        "stage0/STAGE0_MAPPING_COMMIT.json",
        "edb909f41ced2c17e5b8cbe55189adb5736dc03b3893bfc6e6582c46b443a262",
    ),
    "REGISTERED_TRAIN_SUBSTRINGS.txt": (
        "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/"
        "REGISTERED_TRAIN_SUBSTRINGS.txt",
        "5b6859d8656f63cf8e8cf89221ae8ff1dea345e135a6cd012248b9b4c4ff14a9",
    ),
    "merge_tree.tsv": (
        "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/"
        "merge_tree.tsv",
        "2098c71be9da13b483cf2561e06412276d8c60aa32e72520e8877f8f5d53090a",
    ),
}

REQUIRED_CLAUSES: tuple[dict[str, str], ...] = (
    {
        "clause_id": "DIRECT_UNIT_CONTIGUOUS_INTERVAL",
        "input_id": "GDT615_PREREGISTRATION.md",
        "text": "direct source unit must occupy a contiguous plaintext interval",
        "anchor": "direct source unit must occupy a contiguous plaintext interval",
    },
    {
        "clause_id": "PRIMITIVE_LEAVES_NOT_PAID",
        "input_id": "GDT615_PREREGISTRATION.md",
        "text": "Primitive leaves are not selectable hit nodes.",
        "anchor": "Primitive leaves are not selectable hit nodes.",
    },
    {
        "clause_id": "STAGE0_IGNORES_CHILD_COUNTERPARTS",
        "input_id": "GDT615_PREREGISTRATION.md",
        "text": (
            "This remains a relaxation: it ignores grammar, transition placement, "
            "paid types/outputs, child counterparts, ambiguity, and exact unit tiling."
        ),
        "anchor": "This remains a relaxation:",
    },
    {
        "clause_id": "STAGE1_ALL_DEFAULTS_COUNTERPARTS_AND_MERGES",
        "input_id": "GDT615_PREREGISTRATION.md",
        "text": (
            "It must cover all 34 primitive cards, eight paid cards, 56 defaults, "
            "eight paid-child counterparts, all 64 named merges in train"
        ),
        "anchor": "primitive cards, eight paid cards, 56 defaults, eight paid-child counterparts,",
    },
    {
        "clause_id": "DEFAULT_EFFECTIVE_CHILD_CONCATENATION",
        "input_id": "GDT615_PREREGISTRATION.md",
        "text": (
            "leave every default as the exact left-to-right effective-child "
            "concatenation."
        ),
        "anchor": "default as the exact left-to-right effective-child concatenation.",
    },
    {
        "clause_id": "DEFAULT_EXACT_CHILD_SPAN",
        "input_id": "GDT614_PREREGISTRATION.md",
        "text": (
            "Labelling a default merge span counts only when its two registered "
            "children occupy that exact span"
        ),
        "anchor": "default merge span counts only when its two registered children occupy that",
    },
    {
        "clause_id": "PAID_CHILD_UNOVERRIDDEN_PARSE",
        "input_id": "GDT614_PREREGISTRATION.md",
        "text": (
            "Paid-child exposure must use the unoverridden child parse, not the paid atom."
        ),
        "anchor": "Paid-child exposure must use the unoverridden child parse, not the paid atom.",
    },
    {
        "clause_id": "PAID_CHILD_COMPOSITION_PRESENT",
        "input_id": "GDT614_PREREGISTRATION.md",
        "text": (
            "every paid card's unoverridden child composition present in both partitions;"
        ),
        "anchor": "every paid card's unoverridden child composition present in both partitions;",
    },
    {
        "clause_id": "DEFAULT_MERGES_DIRECTLY_LABELLED",
        "input_id": "GDT614_PREREGISTRATION.md",
        "text": "all 56 default merge nodes directly labelled in both partitions;",
        "anchor": "all 56 default merge nodes directly labelled in both partitions;",
    },
    {
        "clause_id": "EVERY_NAMED_MERGE_IN_TRAIN",
        "input_id": "GDT614_PREREGISTRATION.md",
        "text": "every named merge node in at least one train type and one held event;",
        "anchor": "every named merge node in at least one train type and one held event;",
    },
)


class AuditError(RuntimeError):
    """A frozen input or a contract invariant failed validation."""


@dataclass(frozen=True)
class MergeAudit:
    rank: int
    left: str
    right: str
    merged: str
    raw_render: str
    inclusive_subtree_ranks: tuple[int, ...]
    proper_descendant_ranks: tuple[int, ...]


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_whitespace(value: str) -> str:
    return " ".join(value.split())


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists() and (
            candidate / "experiments/yolo/gdt615_joint_output_permutation_recovery"
        ).is_dir():
            return candidate
    raise AuditError("VManus repository root not found")


def read_hash_bound_inputs(root: Path) -> tuple[dict[str, bytes], list[dict[str, object]]]:
    payloads: dict[str, bytes] = {}
    records: list[dict[str, object]] = []
    for input_id, (relative, expected_hash) in INPUT_SPECS.items():
        path = root / relative
        if not path.is_file():
            raise AuditError(f"missing frozen input: {relative}")
        payload = path.read_bytes()
        actual_hash = sha256_bytes(payload)
        if actual_hash != expected_hash:
            raise AuditError(
                f"hash drift for {input_id}: {actual_hash} != {expected_hash}"
            )
        payloads[input_id] = payload
        records.append(
            {
                "input_id": input_id,
                "path": relative,
                "bytes": len(payload),
                "expected_sha256": expected_hash,
                "actual_sha256": actual_hash,
                "hash_match": True,
            }
        )
    return payloads, records


def clause_evidence(payloads: Mapping[str, bytes]) -> list[dict[str, object]]:
    decoded = {
        input_id: payload.decode("utf-8") for input_id, payload in payloads.items()
        if input_id.endswith("PREREGISTRATION.md")
    }
    evidence: list[dict[str, object]] = []
    for clause in REQUIRED_CLAUSES:
        input_id = clause["input_id"]
        text = decoded[input_id]
        normalized_text = normalized_whitespace(text)
        expected = normalized_whitespace(clause["text"])
        if expected not in normalized_text:
            raise AuditError(f"required clause drift: {clause['clause_id']}")
        line_number = next(
            (
                index
                for index, line in enumerate(text.splitlines(), start=1)
                if clause["anchor"] in normalized_whitespace(line)
            ),
            None,
        )
        if line_number is None:
            # Wrapped clauses may place the identifying words on the following line.
            anchor_words = normalized_whitespace(clause["anchor"]).split()
            short_anchor = " ".join(anchor_words[: min(6, len(anchor_words))])
            line_number = next(
                (
                    index
                    for index, line in enumerate(text.splitlines(), start=1)
                    if short_anchor in normalized_whitespace(line)
                ),
                None,
            )
        evidence.append(
            {
                "clause_id": clause["clause_id"],
                "input_id": input_id,
                "line": line_number,
                "normalized_text": expected,
                "present": True,
            }
        )
    return evidence


def validate_mapping_commit(payload: bytes) -> tuple[dict[str, object], dict[str, str]]:
    try:
        commit = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise AuditError(f"invalid Stage-0 mapping commit: {exc}") from exc
    if commit.get("schema") != "gdt615-stage0-mapping-commit-v1":
        raise AuditError("Stage-0 mapping-commit schema drift")
    if commit.get("status") != "STAGE0_MAPPING_CERTIFICATE_PASS__STAGE1_NOT_RUN":
        raise AuditError("Stage-0 mapping status does not open contract audit")
    if commit.get("stage1_status") != "NOT_RUN":
        raise AuditError("Stage-1 was already marked as run")
    if commit.get("stage0_cover_is_actual_paid_location_selection") is not False:
        raise AuditError("Stage-0 relaxed cover mislabelled as actual paid selection")

    mapping_rows = commit.get("mapping")
    if not isinstance(mapping_rows, list) or len(mapping_rows) != 34:
        raise AuditError("Stage-0 mapping must contain exactly 34 primitive rows")
    primitive_output: dict[str, str] = {}
    card_ids: set[str] = set()
    for row in mapping_rows:
        primitive_id = str(row["primitive_id"])
        card_id = str(row["card_id"])
        output = str(row["output"])
        if primitive_id in primitive_output:
            raise AuditError(f"duplicate primitive in mapping: {primitive_id}")
        if card_id in card_ids:
            raise AuditError(f"duplicate output card in mapping: {card_id}")
        if int(row["length"]) != len(output):
            raise AuditError(f"derived length drift for primitive {primitive_id}")
        primitive_output[primitive_id] = output
        card_ids.add(card_id)
    if sum(not output for output in primitive_output.values()) != 1:
        raise AuditError("mapping must contain exactly one empty primitive output")
    return commit, primitive_output


def validate_substrings(payload: bytes) -> tuple[str, ...]:
    try:
        values = tuple(payload.decode("ascii").splitlines())
    except UnicodeDecodeError as exc:
        raise AuditError("train substring table is not ASCII") from exc
    if len(values) != 28_101 or len(set(values)) != len(values):
        raise AuditError("train substring count or uniqueness drift")
    if any(
        not value
        or not value.isascii()
        or not value.isalpha()
        or not value.islower()
        or not 1 <= len(value) <= 12
        for value in values
    ):
        raise AuditError("malformed train substring")
    if values != tuple(sorted(values, key=lambda value: (len(value), value))):
        raise AuditError("train substring ordering drift")
    return values


def derive_merges(payload: bytes, primitive_output: Mapping[str, str]) -> list[MergeAudit]:
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise AuditError("merge tree is not ASCII") from exc
    rows = list(csv.DictReader(io.StringIO(text), delimiter="\t"))
    if len(rows) != 64:
        raise AuditError("merge tree must contain exactly 64 rows")

    render = dict(primitive_output)
    descendant_ranks: dict[str, set[int]] = {
        primitive_id: set() for primitive_id in primitive_output
    }
    known_names = set(primitive_output)
    merges: list[MergeAudit] = []
    for expected_rank, row in enumerate(rows, start=1):
        rank = int(row["rank"])
        left = row["left"]
        right = row["right"]
        merged = row["merged"]
        if rank != expected_rank:
            raise AuditError("merge ranks are not contiguous and ordered")
        if left not in known_names or right not in known_names or merged in known_names:
            raise AuditError(f"non-topological or duplicate merge {merged}")
        raw_render = render[left] + render[right]
        if not raw_render:
            raise AuditError(f"empty raw merge render at rank {rank}")
        inclusive = {rank} | descendant_ranks[left] | descendant_ranks[right]
        merges.append(
            MergeAudit(
                rank=rank,
                left=left,
                right=right,
                merged=merged,
                raw_render=raw_render,
                inclusive_subtree_ranks=tuple(sorted(inclusive)),
                proper_descendant_ranks=tuple(sorted(inclusive - {rank})),
            )
        )
        render[merged] = raw_render
        descendant_ranks[merged] = inclusive
        known_names.add(merged)
    return merges


def validate_stage0_replay(
    commit: Mapping[str, object], merges: Sequence[MergeAudit], substrings: set[str]
) -> tuple[list[MergeAudit], list[int]]:
    unsupported = [merge for merge in merges if merge.raw_render not in substrings]
    supported_ranks = [merge.rank for merge in merges if merge.raw_render in substrings]
    published_unsupported = [
        (int(row["rank"]), str(row["merge"]), str(row["raw_render"]))
        for row in commit.get("raw_unsupported_merges", [])
    ]
    replayed_unsupported = [
        (merge.rank, merge.merged, merge.raw_render) for merge in unsupported
    ]
    if replayed_unsupported != published_unsupported:
        raise AuditError("recomputed raw-unsupported merge table disagrees with commit")
    if supported_ranks != [int(rank) for rank in commit.get("raw_supported_merge_ranks", [])]:
        raise AuditError("recomputed raw-supported ranks disagree with commit")
    objective = commit.get("objective", {})
    if int(objective.get("raw_train_supported_named_merges", -1)) != len(supported_ranks):
        raise AuditError("Stage-0 raw-support objective disagrees with replay")
    return unsupported, supported_ranks


def audit_unsupported_merge(merge: MergeAudit) -> dict[str, object]:
    descendant_override_available = bool(merge.proper_descendant_ranks)
    reading_invariant_impossibility = not descendant_override_available
    return {
        "rank": merge.rank,
        "merge": merge.merged,
        "left_child": merge.left,
        "right_child": merge.right,
        "raw_unoverridden_child_composition": merge.raw_render,
        "raw_composition_in_train_substrings": False,
        "inclusive_recursive_merge_subtree_ranks": list(
            merge.inclusive_subtree_ranks
        ),
        "proper_merge_descendant_ranks": list(merge.proper_descendant_ranks),
        "primitive_leaves_are_selectable_paid_nodes": False,
        "default_case": {
            "case_assumption": f"merge rank {merge.rank} is not paid",
            "registered_requirement": (
                "default label uses the two registered children on the exact direct span; "
                "the default output is their left-to-right effective concatenation"
            ),
            "raw_span_absent": True,
            "proper_paid_descendant_could_change_effective_child_render": (
                descendant_override_available
            ),
            "result_from_raw_absence_alone": (
                "IMPOSSIBLE"
                if reading_invariant_impossibility
                else "NOT_DECISIVE_WITHOUT_ENUMERATING_DESCENDANT_PAID_OVERRIDES"
            ),
        },
        "paid_case": {
            "case_assumption": f"merge rank {merge.rank} is paid",
            "registered_requirement": (
                "the paid atom does not count as its child exposure; an unoverridden "
                "child parse/composition is mandatory"
            ),
            "strict_fully_raw_counterpart_span_absent": True,
            "proper_paid_descendant_could_change_effective_child_render_under_a_weaker_reading": (
                descendant_override_available
            ),
            "result_invariant_across_raw_and_effective_descendant_readings": (
                "IMPOSSIBLE"
                if reading_invariant_impossibility
                else "NOT_DECISIVE_WITHOUT_FIXING_DESCENDANT_COUNTERPART_SEMANTICS"
            ),
        },
        "paid_or_default_case_partition_is_complete": True,
        "two_case_contradiction_invariant_to_descendant_counterpart_reading": (
            reading_invariant_impossibility
        ),
    }


def alternative_readings() -> list[dict[str, object]]:
    return [
        {
            "reading_id": "EFFECTIVE_DESCENDANT_OVERRIDES_REMAIN_IN_COUNTERPART",
            "description": (
                "Removing a paid override at the audited node may retain paid overrides "
                "strictly below it."
            ),
            "changes_a_registered_gate": False,
            "removes_the_singleton_Ey_contradiction": False,
            "reason": "Ey has no proper merge descendant, so both readings render ho+i=hoi.",
        },
        {
            "reading_id": "CHILDREN_MAY_APPEAR_SEPARATELY_ANYWHERE",
            "description": (
                "Count the left and right children separately instead of requiring their "
                "joint ordered exact span."
            ),
            "changes_a_registered_gate": True,
            "changed_contract_clauses": [
                "DEFAULT_EXACT_CHILD_SPAN",
                "PAID_CHILD_UNOVERRIDDEN_PARSE",
                "PAID_CHILD_COMPOSITION_PRESENT",
            ],
            "removes_the_singleton_Ey_contradiction": True,
            "does_not_by_itself_prove_world_feasibility": True,
        },
        {
            "reading_id": "PAID_NODE_EXEMPT_FROM_CHILD_COUNTERPART",
            "description": "A paid atom alone may satisfy exposure for its overridden node.",
            "changes_a_registered_gate": True,
            "changed_contract_clauses": [
                "STAGE1_ALL_DEFAULTS_COUNTERPARTS_AND_MERGES",
                "PAID_CHILD_UNOVERRIDDEN_PARSE",
                "PAID_CHILD_COMPOSITION_PRESENT",
            ],
            "removes_the_singleton_Ey_contradiction": True,
            "does_not_by_itself_prove_world_feasibility": True,
        },
        {
            "reading_id": "ANCESTOR_OR_EQUAL_RENDER_MAY_CREDIT_NODE_ID",
            "description": (
                "Credit Ey through a paid ancestor or another node/string without an exact "
                "Ey child-labelled span."
            ),
            "changes_a_registered_gate": True,
            "changed_contract_clauses": [
                "DIRECT_UNIT_CONTIGUOUS_INTERVAL",
                "DEFAULT_EXACT_CHILD_SPAN",
                "EVERY_NAMED_MERGE_IN_TRAIN",
            ],
            "removes_the_singleton_Ey_contradiction": True,
            "does_not_by_itself_prove_world_feasibility": True,
        },
        {
            "reading_id": "NONCONTIGUOUS_OR_CROSS_WORD_CHILD_SPAN",
            "description": (
                "Allow the two child outputs to be separated or cross a plaintext-word boundary."
            ),
            "changes_a_registered_gate": True,
            "changed_contract_clauses": [
                "DIRECT_UNIT_CONTIGUOUS_INTERVAL",
                "DEFAULT_EXACT_CHILD_SPAN",
            ],
            "removes_the_singleton_Ey_contradiction": True,
            "does_not_by_itself_prove_world_feasibility": True,
        },
    ]


def audit(root: Path, source_path: Path | None = None) -> dict[str, object]:
    payloads, input_records = read_hash_bound_inputs(root)
    clauses = clause_evidence(payloads)
    commit, primitive_output = validate_mapping_commit(
        payloads["STAGE0_MAPPING_COMMIT.json"]
    )
    substring_values = validate_substrings(
        payloads["REGISTERED_TRAIN_SUBSTRINGS.txt"]
    )
    substring_set = set(substring_values)
    merges = derive_merges(payloads["merge_tree.tsv"], primitive_output)
    unsupported, supported_ranks = validate_stage0_replay(
        commit, merges, substring_set
    )
    per_merge = [audit_unsupported_merge(merge) for merge in unsupported]
    decisive = [
        row
        for row in per_merge
        if row["two_case_contradiction_invariant_to_descendant_counterpart_reading"]
    ]
    minimum_subtree_size = min(
        (len(row["inclusive_recursive_merge_subtree_ranks"]) for row in decisive),
        default=None,
    )
    minimal_witnesses = [
        row
        for row in decisive
        if len(row["inclusive_recursive_merge_subtree_ranks"])
        == minimum_subtree_size
    ]

    source = source_path or Path(__file__).resolve()
    source_relative = source.resolve().relative_to(root.resolve()).as_posix()
    decision = DECISION_INFEASIBLE if decisive else DECISION_NOT_DECISIVE
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS",
        "decision": decision,
        "claim_ceiling": (
            "Hash-bound contract interpretation and train-only necessary bound. "
            "This is not a Stage-1 parser, paid-location search, truth-world result, "
            "held result, oracle result, recovery result, or Voynich claim."
        ),
        "registered_outcome_implication_if_contract_is_applied_literally": (
            "MAPPING_BOUND_PASS__FULL_WORLD_INFEASIBLE" if decisive else None
        ),
        "stage1_search_performed": False,
        "paid_locations_selected": False,
        "worlds_constructed": 0,
        "input_access": {
            "allowlist": [record["path"] for record in input_records],
            "held_opened": False,
            "lm_confirm_opened": False,
            "voynich_target_opened": False,
            "f84_opened": False,
            "f84r_opened": False,
        },
        "input_hashes": input_records,
        "contract_clause_evidence": clauses,
        "stage0_replay": {
            "mapping_rows": len(primitive_output),
            "merge_rows": len(merges),
            "train_substrings": len(substring_values),
            "raw_supported_count": len(supported_ranks),
            "raw_supported_ranks": supported_ranks,
            "raw_unsupported_count": len(unsupported),
            "raw_unsupported_ranks": [merge.rank for merge in unsupported],
            "matches_mapping_commit": True,
        },
        "two_case_audit": per_merge,
        "decisive_two_case_witness_count": len(decisive),
        "minimal_witness_order": "inclusive subtree cardinality, then merge rank",
        "minimal_witnesses": minimal_witnesses,
        "proof_summary": {
            "case_partition": "each actual merge location is either paid or default",
            "default_branch": (
                "a default merge is credited only by its registered children on the exact "
                "direct span"
            ),
            "paid_branch": (
                "a paid atom cannot replace the mandatory unoverridden child "
                "parse/composition counterpart"
            ),
            "singleton_subtree_consequence": (
                "when both children are primitive leaves, no proper paid descendant can "
                "alter either branch's required child render"
            ),
            "train_substring_absence_consequence": (
                "absence of that render from the complete length-1..12 train table rules "
                "out a contiguous train span"
            ),
        },
        "alternative_readings": alternative_readings(),
        "generated_by": {
            "path": source_relative,
            "sha256": sha256_path(source),
        },
    }
    return result


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_result(path: Path, result: Mapping[str, object]) -> str:
    payload = canonical_json(result)
    if path.exists():
        current = path.read_bytes()
        if current != payload:
            raise AuditError(f"refusing to overwrite differing result: {path}")
        return sha256_bytes(current)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        raise AuditError(f"refusing existing temporary result: {temporary}")
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return sha256_bytes(payload)


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    root = (
        args.repo_root.resolve()
        if args.repo_root is not None
        else find_repo_root(Path(__file__).resolve())
    )
    result = audit(root)
    output = args.output or (
        root
        / "experiments/yolo/gdt615_joint_output_permutation_recovery/artifacts/"
        "stage1_work/contract/RESULT.json"
    )
    result_hash = None if args.check_only else write_result(output, result)
    print(
        json.dumps(
            {
                "decision": result["decision"],
                "minimal_witness_ranks": [
                    row["rank"] for row in result["minimal_witnesses"]
                ],
                "raw_unsupported_count": result["stage0_replay"][
                    "raw_unsupported_count"
                ],
                "result_sha256": result_hash,
                "status": result["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
