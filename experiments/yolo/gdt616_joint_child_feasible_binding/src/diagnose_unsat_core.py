#!/usr/bin/env python3
"""Reproduce and localize the frozen GDT616 Stage-A contradiction.

The diagnostic does not inspect held, LM-confirm, target, f84, or f84r data.
It imports the public primary Stage-A encoder so the formula and registered
TRAIN-only input validation are byte-bound to the executed experiment.

The reported core is deliberately a *group-level subset-minimal core of a
relaxation*, not an assertion-level or minimum-cardinality UNSAT core.  The
relaxation replaces each registered paid-card ``exactly once`` constraint by
the logically weaker ``at most once`` constraint.  Every other registered
constraint is retained for the full-relaxation replay.  A smaller named set of
role and rank groups is then proved UNSAT, and deleting any one named group is
proved SAT.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Mapping, Sequence

import z3


SCHEMA = "gdt616-stage-a-unsat-core-diagnostic-v1"
EXPECTED_Z3_VERSION = "4.15.3"
EXPECTED_PRIMARY_SOURCE_SHA256 = (
    "f99785892749ddafc999b8bb2145ee67cdfe5b7c75635012c271ee140c3dc381"
)
EXPECTED_FROZEN_RESULTS: Mapping[str, str] = {
    "PRIMARY_RESULT.json": (
        "d87d925fff5c7e185a256dacf53619b72a8fe430e2db21ce6f6232f2e906faef"
    ),
    "INDEPENDENT_RESULT.json": (
        "38b7e7741850791731946d9bc963f3ad44d5147eb267e0387d6c57b71f601361"
    ),
    "COMPARISON.json": (
        "e098d63da66b49134e2277e5646639a20cc3b6a8c840b22394da284a1f14aa2c"
    ),
}
EXPECTED_FULL_ASSERTION_COUNT = 1_366
MAX_QUERY_MILLISECONDS = 43_200_000


class DiagnosticError(RuntimeError):
    """A frozen input, grouping invariant, or exact query failed."""


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise DiagnosticError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = ROOT / "experiments/yolo/gdt616_joint_child_feasible_binding"
PRIMARY_SOURCE = EXPERIMENT / "src/primary_bound.py"
STAGE_A = EXPERIMENT / "artifacts/stage_a"
OUTPUT = STAGE_A / "UNSAT_CORE_DIAGNOSTIC.json"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    ).encode("ascii")


def load_json(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DiagnosticError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise DiagnosticError(f"JSON root is not an object: {path}")
    return value


def load_primary_module():
    if sha256_path(PRIMARY_SOURCE) != EXPECTED_PRIMARY_SOURCE_SHA256:
        raise DiagnosticError("frozen primary_bound.py hash mismatch")
    spec = importlib.util.spec_from_file_location("gdt616_primary_bound", PRIMARY_SOURCE)
    if spec is None or spec.loader is None:
        raise DiagnosticError("cannot create primary_bound.py import specification")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def role_group(role: str) -> str:
    return f"PRIMITIVE_ROLE::{role}"


def rank_group(rank: int, merged: str) -> str:
    return f"RANK::{rank:02d}::{merged}"


def cap_group(card_id: str) -> str:
    return f"CARD_AT_MOST_ONCE::{card_id}"


CORE_GROUPS: tuple[str, ...] = (
    "PRIMITIVE_ROLE::literal_carrier",
    "RANK::02::ok",
    "RANK::03::ol",
    "RANK::04::aN",
    "RANK::06::ot",
    "RANK::09::al",
    "RANK::10::or",
    "RANK::11::Se",
    "RANK::14::Ey",
    "RANK::23::ai",
    "RANK::38::air",
    "RANK::43::So",
    "RANK::45::Sol",
    "RANK::51::eol",
    "RANK::52::Sy",
    "RANK::60::okaN",
    "RANK::61::okal",
    "RANK::62::otal",
    "RANK::63::oky",
    "RANK::64::oty",
    "CARD_AT_MOST_ONCE::short:1",
    "CARD_AT_MOST_ONCE::short:2",
    "CARD_AT_MOST_ONCE::short:3",
)


def group_registered_assertions(instance, compiled, encoding):
    """Partition the public encoder's assertions without changing a formula.

    This follows ``build_encoding``'s registered emission order and checks the
    complete cursor and group sizes.  The eight exact-use assertions are kept
    separately so that their weaker at-most replacements are explicit.
    """

    assertions = encoding.assertions
    if len(assertions) != EXPECTED_FULL_ASSERTION_COUNT:
        raise DiagnosticError(
            f"unexpected Stage-A assertion count: {len(assertions)}"
        )
    cursor = 0
    groups: OrderedDict[str, list[z3.BoolRef]] = OrderedDict()
    exact_use: OrderedDict[str, z3.BoolRef] = OrderedDict()

    def take(group: str, count: int = 1) -> None:
        nonlocal cursor
        end = cursor + count
        if end > len(assertions):
            raise DiagnosticError("assertion grouping overran Stage-A formula")
        groups.setdefault(group, []).extend(assertions[cursor:end])
        cursor = end

    # Two primitive assertions per primitive: card-index domain and exact
    # card-output link.  Multi-card roles add one bijection assertion.
    primitive_roles: OrderedDict[str, list[object]] = OrderedDict()
    for primitive in instance.primitives:
        primitive_roles.setdefault(primitive.role, []).append(primitive)
        take(role_group(primitive.role), 2)
    # ``build_encoding`` emits Distinct constraints in first-primitive role
    # order, not JSON deck-key order.  Preserve that exact order here.
    for role, primitives in primitive_roles.items():
        if len(primitives) > 1:
            take(role_group(role))

    # Static qok prohibitions (four) precede the rank's one-location cap; all
    # other ranks contribute only the one-location cap in this encoder block.
    for merge in instance.merges:
        group = rank_group(merge.rank, merge.merged)
        forbidden = sum(
            card.card_id not in compiled.permitted_paid_ids[merge.merged]
            for card in instance.paid_cards
        )
        take(group, forbidden + 1)

    # The next eight assertions are the registered per-card exactly-once PbEq.
    for card in instance.paid_cards:
        if cursor >= len(assertions):
            raise DiagnosticError("missing registered exact paid-use assertion")
        exact_use[card.card_id] = assertions[cursor]
        cursor += 1

    # Per rank: child relation, effective TRAIN gate, default-child implication,
    # then paid-effective and paid-differs-child for each of eight cards.
    per_rank_tail = 3 + 2 * len(instance.paid_cards)
    if per_rank_tail != 19:
        raise DiagnosticError("unexpected per-rank Stage-A tail size")
    for merge in instance.merges:
        take(rank_group(merge.rank, merge.merged), per_rank_tail)

    if cursor != len(assertions):
        raise DiagnosticError(
            f"assertion grouping stopped at {cursor}/{len(assertions)}"
        )
    if len(exact_use) != 8:
        raise DiagnosticError("unexpected exact paid-use group count")
    for merge in instance.merges:
        expected = 24 if merge.merged == "qok" else 20
        observed = len(groups[rank_group(merge.rank, merge.merged)])
        if observed != expected:
            raise DiagnosticError(
                f"rank {merge.rank} group size {observed}, expected {expected}"
            )

    caps: OrderedDict[str, z3.BoolRef] = OrderedDict()
    for card in instance.paid_cards:
        caps[card.card_id] = z3.PbLe(
            [
                (encoding.paid_assignment[(merge.rank, card.card_id)], 1)
                for merge in instance.merges
            ],
            1,
        )
        groups[cap_group(card.card_id)] = [caps[card.card_id]]
    return groups, exact_use, caps


def exact_status(assertions: Sequence[z3.BoolRef]) -> tuple[str, z3.ModelRef | None]:
    solver = z3.Solver()
    solver.set(timeout=MAX_QUERY_MILLISECONDS)
    solver.add(*assertions)
    status = solver.check()
    if status == z3.sat:
        return "sat", solver.model()
    if status == z3.unsat:
        return "unsat", None
    raise DiagnosticError(f"solver returned unknown: {solver.reason_unknown()}")


class GroupOracle:
    """Incremental exact group checker with inactive groups forced off."""

    def __init__(self, groups: Mapping[str, Sequence[z3.BoolRef]]):
        self.groups = groups
        self.names = tuple(groups)
        self.solver = z3.Solver()
        self.solver.set(timeout=MAX_QUERY_MILLISECONDS)
        self.guards: dict[str, z3.BoolRef] = {}
        for index, name in enumerate(self.names):
            guard = z3.Bool(f"diagnostic_group_{index:03d}")
            self.guards[name] = guard
            self.solver.add(z3.Implies(guard, z3.And(*groups[name])))
        self.query_count = 0

    def check(self, selected: Sequence[str]) -> tuple[str, z3.ModelRef | None]:
        selected_set = set(selected)
        unknown = selected_set.difference(self.groups)
        if unknown:
            raise DiagnosticError("unknown diagnostic groups: " + ", ".join(sorted(unknown)))
        # Negative assumptions matter for witness interpretation: no inactive
        # group is allowed to become true merely because the solver prefers it.
        assumptions = [
            self.guards[name] if name in selected_set else z3.Not(self.guards[name])
            for name in self.names
        ]
        self.query_count += 1
        status = self.solver.check(*assumptions)
        if status == z3.sat:
            return "sat", self.solver.model()
        if status == z3.unsat:
            return "unsat", None
        raise DiagnosticError(f"group query returned unknown: {self.solver.reason_unknown()}")


def verify_frozen_results() -> dict[str, object]:
    observed: dict[str, str] = {}
    for filename, expected in EXPECTED_FROZEN_RESULTS.items():
        path = STAGE_A / filename
        if not path.is_file():
            raise DiagnosticError(f"missing frozen Stage-A result: {filename}")
        digest = sha256_path(path)
        if digest != expected:
            raise DiagnosticError(f"frozen Stage-A result hash mismatch: {filename}")
        observed[filename] = digest

    primary = load_json(STAGE_A / "PRIMARY_RESULT.json")
    independent = load_json(STAGE_A / "INDEPENDENT_RESULT.json")
    comparison = load_json(STAGE_A / "COMPARISON.json")
    expected_decision = "NO_JOINT_CHILD_FEASIBLE_BINDING"
    if primary.get("decision") != expected_decision:
        raise DiagnosticError("primary frozen decision drift")
    if independent.get("decision") != expected_decision:
        raise DiagnosticError("independent frozen decision drift")
    if comparison.get("decision") != expected_decision or comparison.get("status") != "PASS":
        raise DiagnosticError("dual-solver comparison drift")
    return {
        "decision": expected_decision,
        "files_sha256": observed,
        "primary_schema": primary.get("schema"),
        "independent_schema": independent.get("schema"),
        "comparison_schema": comparison.get("schema"),
    }


def describe_group(name: str, instance, cards_by_id: Mapping[str, object]) -> dict[str, object]:
    if name.startswith("PRIMITIVE_ROLE::"):
        role = name.split("::", 1)[1]
        primitives = [
            row.primitive_id for row in instance.primitives if row.role == role
        ]
        return {
            "group": name,
            "kind": "primitive_role_binding",
            "role": role,
            "primitive_count": len(primitives),
            "primitives": primitives,
            "meaning": "card-index domains, exact card-output links, and the same-role bijection",
        }
    if name.startswith("RANK::"):
        _, raw_rank, merged = name.split("::")
        rank = int(raw_rank)
        merge = next(row for row in instance.merges if row.rank == rank)
        if merge.merged != merged:
            raise DiagnosticError(f"rank group name mismatch: {name}")
        return {
            "group": name,
            "kind": "merge_rank",
            "rank": rank,
            "merge": merged,
            "left": merge.left,
            "right": merge.right,
            "composition": f"{merge.left}+{merge.right}->{merged}",
            "meaning": (
                "one paid card at this rank at most; exact TRAIN child relation; "
                "effective TRAIN gate; default-child equality; all paid-output and "
                "paid-differs-child implications"
            ),
        }
    if name.startswith("CARD_AT_MOST_ONCE::"):
        card_id = name.split("::", 1)[1]
        card = cards_by_id[card_id]
        return {
            "group": name,
            "kind": "relaxed_paid_card_cap",
            "card_id": card_id,
            "output": card.output,
            "role": card.role,
            "meaning": "this paid card may occur at zero or one merge rank",
        }
    raise DiagnosticError(f"cannot describe group: {name}")


def build_artifact() -> dict[str, object]:
    if z3.get_version_string() != EXPECTED_Z3_VERSION:
        raise DiagnosticError(
            f"unexpected Z3 version {z3.get_version_string()}, expected {EXPECTED_Z3_VERSION}"
        )
    frozen = verify_frozen_results()
    primary = load_primary_module()
    instance, registered_hashes = primary.load_registered_instance()
    compiled = primary.compile_instance(instance)
    encoding = primary.build_encoding(compiled)
    groups, exact_use, caps = group_registered_assertions(instance, compiled, encoding)
    cards_by_id = {card.card_id: card for card in instance.paid_cards}

    query_count = 0

    # Recompute the exact frozen decision from the public encoder.
    strict_status, _ = exact_status(encoding.assertions)
    query_count += 1
    if strict_status != "unsat":
        raise DiagnosticError(f"strict Stage-A replay is {strict_status}, expected unsat")

    # Prove, rather than merely state, that each replacement is weaker than the
    # original registered constraint: exact-use AND NOT(at-most-use) is UNSAT.
    implication_checks: list[dict[str, object]] = []
    for card in instance.paid_cards:
        status, _ = exact_status([exact_use[card.card_id], z3.Not(caps[card.card_id])])
        query_count += 1
        if status != "unsat":
            raise DiagnosticError(f"exactly-once does not imply cap for {card.card_id}")
        implication_checks.append(
            {
                "card_id": card.card_id,
                "output": card.output,
                "query": "registered_exactly_once AND NOT(diagnostic_at_most_once)",
                "status": status,
            }
        )

    oracle = GroupOracle(groups)
    all_groups = tuple(groups)
    all_without_caps = tuple(
        name for name in all_groups if not name.startswith("CARD_AT_MOST_ONCE::")
    )
    full_relaxed_status, _ = oracle.check(all_groups)
    no_cap_status, _ = oracle.check(all_without_caps)
    if full_relaxed_status != "unsat":
        raise DiagnosticError("full at-most-once relaxation is not UNSAT")
    if no_cap_status != "sat":
        raise DiagnosticError(
            "model without exact-use constraints and without replacement caps is not SAT"
        )

    if len(CORE_GROUPS) != len(set(CORE_GROUPS)):
        raise DiagnosticError("duplicate group in declared core")
    core_status, _ = oracle.check(CORE_GROUPS)
    if core_status != "unsat":
        raise DiagnosticError("declared group core is not UNSAT")

    drop_one: list[dict[str, object]] = []
    for dropped in CORE_GROUPS:
        selected = tuple(name for name in CORE_GROUPS if name != dropped)
        status, model = oracle.check(selected)
        if status != "sat" or model is None:
            raise DiagnosticError(f"core is not subset-minimal at {dropped}: {status}")
        row: dict[str, object] = {"dropped_group": dropped, "status": status}
        if dropped.startswith("CARD_AT_MOST_ONCE::"):
            card_id = dropped.split("::", 1)[1]
            active_ranks = {
                int(name.split("::")[1])
                for name in selected
                if name.startswith("RANK::")
            }
            used = [
                {
                    "rank": merge.rank,
                    "merge": merge.merged,
                }
                for merge in instance.merges
                if merge.rank in active_ranks
                and z3.is_true(
                    model.eval(
                        encoding.paid_assignment[(merge.rank, card_id)],
                        model_completion=True,
                    )
                )
            ]
            if len(used) < 2:
                raise DiagnosticError(
                    f"dropping {dropped} did not produce the logically required repetition"
                )
            row.update(
                {
                    "dropped_card_id": card_id,
                    "dropped_card_output": cards_by_id[card_id].output,
                    "logical_consequence": (
                        "because restoring this cap makes the same groups UNSAT, "
                        "every satisfying drop-one model repeats this card"
                    ),
                    "example_active_core_rank_uses": used,
                }
            )
        drop_one.append(row)

    core_descriptions = [
        describe_group(name, instance, cards_by_id) for name in CORE_GROUPS
    ]
    core_rank_count = sum(row["kind"] == "merge_rank" for row in core_descriptions)
    core_role_count = sum(
        row["kind"] == "primitive_role_binding" for row in core_descriptions
    )
    core_cap_count = sum(
        row["kind"] == "relaxed_paid_card_cap" for row in core_descriptions
    )
    core_assertion_count = sum(len(groups[name]) for name in CORE_GROUPS)

    return {
        "schema": SCHEMA,
        "experiment_id": "GDT616",
        "decision": "NO_JOINT_CHILD_FEASIBLE_BINDING",
        "diagnostic_kind": "SUBSET_MINIMAL_GROUP_CORE_OF_EXACTLY_TO_AT_MOST_RELAXATION",
        "frozen_stage_a": frozen,
        "input_sha256": registered_hashes,
        "source_sha256": {
            "primary_bound.py": sha256_path(PRIMARY_SOURCE),
            "diagnose_unsat_core.py": sha256_path(Path(__file__).resolve()),
        },
        "solver": {
            "name": "Z3",
            "version": z3.get_version_string(),
            "query_count": query_count + oracle.query_count,
            "unknown_or_timeout_can_pass": False,
        },
        "model_counts": {
            "primitives": len(instance.primitives),
            "merges": len(instance.merges),
            "paid_cards": len(instance.paid_cards),
            "train_substrings": len(instance.train_substrings),
            "strict_assertions": len(encoding.assertions),
            "relaxed_groups": len(groups),
        },
        "replay": {
            "strict_registered_stage_a": {
                "status": strict_status,
                "formula": "all 1366 assertions emitted by frozen primary_bound.py",
            },
            "full_exactly_to_at_most_relaxation": {
                "status": full_relaxed_status,
                "retained": (
                    "all primitive-role and all rank constraints, including every "
                    "child/effective TRAIN gate and rank-local paid implication"
                ),
                "replaced": (
                    "each of eight paid-card PbEq(use,1) constraints by "
                    "PbLe(use,1); only the at-least-one part is removed"
                ),
                "logical_relation": (
                    "every registered Stage-A model would satisfy this relaxation"
                ),
            },
            "exactly_once_implies_at_most_once_checks": implication_checks,
            "exact_use_removed_without_replacement_caps": {
                "status": no_cap_status,
                "interpretation": (
                    "SAT: merely deleting exact-use is not itself a contradiction; "
                    "the diagnostic therefore retains the logically implied at-most cap"
                ),
            },
        },
        "core": {
            "status": core_status,
            "group_count": len(CORE_GROUPS),
            "group_assertion_count": core_assertion_count,
            "role_group_count": core_role_count,
            "rank_group_count": core_rank_count,
            "card_cap_group_count": core_cap_count,
            "groups": core_descriptions,
            "plain_language": (
                "With only the literal-carrier bijection, the listed 19 recursive "
                "TRAIN-constrained merge ranks, and unlimited "
                "reuse of every paid output except de/di/ent, no assignment can keep "
                "all three of de, di, and ent to at most one rank. At least one of "
                "those three outputs must repeat. The registered model instead uses "
                "each paid card exactly once, so it cannot satisfy this necessary core."
            ),
            "claim_ceiling": (
                "This diagnoses a synthetic TRAIN-only generator contradiction. It "
                "assigns no Voynich unit, sound, word, language, plaintext, object, "
                "operation, or meaning."
            ),
        },
        "minimality": {
            "kind": "subset-minimal over the 23 declared semantic groups",
            "not_claimed": [
                "minimum-cardinality group core",
                "assertion-level minimal core",
                "unique core",
            ],
            "proof": (
                "the complete declared core is UNSAT and every one-group deletion is SAT"
            ),
            "drop_one_checks": drop_one,
        },
        "access_boundary": {
            "registered_train_only": True,
            "held_opened": False,
            "lm_confirm_opened": False,
            "voynich_target_opened": False,
            "f84_opened": False,
            "f84r_opened": False,
        },
    }


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    if path.exists() or temporary.exists():
        raise DiagnosticError(f"refusing to overwrite {path}")
    with temporary.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="create the frozen diagnostic")
    mode.add_argument("--check", action="store_true", help="recompute and byte-check it")
    args = parser.parse_args(argv)

    artifact = build_artifact()
    payload = canonical_json(artifact)
    if args.write:
        atomic_write(OUTPUT, payload)
        print(f"GDT616_UNSAT_CORE_DIAGNOSTIC_WRITTEN {sha256_path(OUTPUT)}")
        return 0
    if not OUTPUT.is_file():
        raise DiagnosticError(f"missing diagnostic artifact: {OUTPUT}")
    observed = OUTPUT.read_bytes()
    if observed != payload:
        raise DiagnosticError("diagnostic artifact differs from exact replay")
    print(
        "GDT616_UNSAT_CORE_DIAGNOSTIC_PASS "
        f"groups={len(CORE_GROUPS)} drop_one={len(CORE_GROUPS)} sha256={sha256_path(OUTPUT)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DiagnosticError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
