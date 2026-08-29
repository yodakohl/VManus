#!/usr/bin/env python3
"""Reproduce and cross-check the registered GDT615 Stage-0 result.

The runner has exactly three scientific inputs, all fixed below. The caller
can choose only a fresh output root and registered resource limits. Primary
and independent processes never receive one another's result paths.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


PRIMARY_SCHEMA = "gdt615-stage0-primary-result-v1"
INDEPENDENT_SCHEMA = "gdt615-stage0-independent-result-v1"
INTEGRATION_SCHEMA = "gdt615-stage0-integration-result-v1"
MAXIMUM_TIME_LIMIT_SECONDS = 14_400
MAXIMUM_WORKERS = 32


class IntegrationError(RuntimeError):
    """A reproducibility or cross-solver validation gate failed."""


class IntegrationMismatch(IntegrationError):
    """The two exact solvers returned different canonical results."""

    def __init__(self, fields: Sequence[str]):
        self.fields = tuple(fields)
        super().__init__("cross-solver mismatch: " + ", ".join(self.fields))


class StageFailure(IntegrationError):
    """A build, self-test, or solver process failed."""

    def __init__(self, stage: str, returncode: int):
        self.stage = stage
        self.returncode = returncode
        super().__init__(f"{stage} exited with status {returncode}")


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXPERIMENT = ROOT / "experiments/yolo/gdt615_joint_output_permutation_recovery"
REGISTERED_SEARCH = EXPERIMENT / "artifacts/REGISTERED_SEARCH.json"
REGISTERED_SUBSTRINGS = EXPERIMENT / "artifacts/REGISTERED_TRAIN_SUBSTRINGS.txt"
MERGE_TREE = (
    ROOT
    / "experiments/yolo/gdt608_compositional_stem_orientation/artifacts/merge_tree.tsv"
)
PRIMARY_SOURCE = EXPERIMENT / "src/primary/solve.py"
INDEPENDENT_SOURCE = EXPERIMENT / "src/independent/stage0_independent.cpp"

SCIENTIFIC_INPUTS: Mapping[str, Path] = {
    "REGISTERED_SEARCH.json": REGISTERED_SEARCH,
    "REGISTERED_TRAIN_SUBSTRINGS.txt": REGISTERED_SUBSTRINGS,
    "merge_tree.tsv": MERGE_TREE,
}


@dataclass(frozen=True)
class RegisteredContext:
    primitive_order: tuple[tuple[str, str], ...]
    cards: Mapping[str, Mapping[str, object]]
    merge_names: tuple[str, ...]
    input_hashes: Mapping[str, str]


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def exclusive_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def exclusive_write_json(path: Path, value: object) -> None:
    exclusive_write(path, canonical_json(value))


def load_json(path: Path, label: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise IntegrationError(f"cannot read valid {label} JSON") from exc
    if not isinstance(value, dict):
        raise IntegrationError(f"{label} must be a JSON object")
    return value


def require_dict(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise IntegrationError(f"{label} must be an object")
    return value


def require_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise IntegrationError(f"{label} must be an array")
    return value


def require_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise IntegrationError(f"{label} must be an integer")
    return value


def require_str(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise IntegrationError(f"{label} must be a string")
    return value


def snapshot_inputs() -> dict[str, str]:
    result: dict[str, str] = {}
    for label, path in SCIENTIFIC_INPUTS.items():
        if not path.is_file():
            raise IntegrationError(f"missing fixed Stage-0 input: {label}")
        result[label] = sha256_path(path)
    return result


def assert_inputs_unchanged(expected: Mapping[str, str], stage: str) -> None:
    if snapshot_inputs() != dict(expected):
        raise IntegrationError(f"registered Stage-0 input changed during {stage}")


def load_registered_context(input_hashes: Mapping[str, str]) -> RegisteredContext:
    registered = load_json(REGISTERED_SEARCH, "registered search")
    if registered.get("schema") != "gdt615-joint-output-binding-search-v1":
        raise IntegrationError("unexpected registered-search schema")

    primitive_rows = require_list(
        registered.get("primitive_role_assignment"),
        "registered primitive_role_assignment",
    )
    primitive_order: list[tuple[str, str]] = []
    seen_primitives: set[str] = set()
    for position, raw_row in enumerate(primitive_rows):
        row = require_dict(raw_row, f"registered primitive row {position}")
        primitive_id = require_str(row.get("primitive_id"), "registered primitive_id")
        role = require_str(row.get("role"), "registered primitive role")
        if primitive_id in seen_primitives:
            raise IntegrationError("duplicate registered primitive ID")
        seen_primitives.add(primitive_id)
        primitive_order.append((primitive_id, role))
    if len(primitive_order) != 34:
        raise IntegrationError("registered primitive count is not 34")

    raw_deck = require_dict(registered.get("primitive_output_deck"), "registered deck")
    cards: dict[str, Mapping[str, object]] = {}
    role_counts: dict[str, int] = {}
    for role, raw_cards in raw_deck.items():
        if not isinstance(role, str):
            raise IntegrationError("registered deck role must be a string")
        card_rows = require_list(raw_cards, f"registered deck role {role}")
        role_counts[role] = len(card_rows)
        for position, raw_card in enumerate(card_rows):
            card = dict(require_dict(raw_card, f"registered card {role}/{position}"))
            card_id = require_str(card.get("card_id"), "registered card_id")
            output = require_str(card.get("output"), "registered card output")
            if card_id in cards:
                raise IntegrationError("duplicate registered card ID")
            card["role"] = role
            card["length"] = len(output)
            cards[card_id] = card
    primitive_role_counts: dict[str, int] = {}
    for _, role in primitive_order:
        primitive_role_counts[role] = primitive_role_counts.get(role, 0) + 1
    if len(cards) != 34 or role_counts != primitive_role_counts:
        raise IntegrationError("registered role/card cardinality mismatch")

    merge_names: list[str] = []
    try:
        with MERGE_TREE.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise IntegrationError("cannot read the fixed merge tree") from exc
    for expected_rank, row in enumerate(rows, 1):
        try:
            rank = int(row["rank"])
            name = row["merged"]
        except (KeyError, TypeError, ValueError) as exc:
            raise IntegrationError("malformed fixed merge tree") from exc
        if rank != expected_rank or not name:
            raise IntegrationError("noncanonical fixed merge-tree order")
        merge_names.append(name)
    if len(merge_names) != 64 or len(set(merge_names)) != 64:
        raise IntegrationError("fixed merge tree must contain 64 unique nodes")

    return RegisteredContext(
        primitive_order=tuple(primitive_order),
        cards=cards,
        merge_names=tuple(merge_names),
        input_hashes=dict(input_hashes),
    )


def canonical_mapping(
    raw_mapping: object,
    context: RegisteredContext,
    label: str,
    *,
    require_full_metadata: bool,
) -> list[dict[str, object]]:
    rows = require_list(raw_mapping, f"{label} mapping")
    expected_ids = [primitive_id for primitive_id, _ in context.primitive_order]
    observed_ids: list[str] = []
    by_primitive: dict[str, Mapping[str, object]] = {}
    for position, raw_row in enumerate(rows):
        row = require_dict(raw_row, f"{label} mapping row {position}")
        primitive_id = require_str(row.get("primitive_id"), f"{label} primitive_id")
        if primitive_id in by_primitive:
            raise IntegrationError(f"{label} mapping has duplicate primitive ID")
        observed_ids.append(primitive_id)
        by_primitive[primitive_id] = row
    if observed_ids != expected_ids:
        raise IntegrationError(f"{label} mapping is not in registered primitive order")

    seen_cards: set[str] = set()
    canonical: list[dict[str, object]] = []
    for primitive_id, expected_role in context.primitive_order:
        row = by_primitive[primitive_id]
        role = require_str(row.get("role"), f"{label} mapping role")
        card_id = require_str(row.get("card_id"), f"{label} mapping card_id")
        output = require_str(row.get("output"), f"{label} mapping output")
        if role != expected_role:
            raise IntegrationError(f"{label} mapping role disagrees with registration")
        card = context.cards.get(card_id)
        if card is None or card.get("role") != role:
            raise IntegrationError(f"{label} mapping uses an unregistered role/card pair")
        if output != card.get("output"):
            raise IntegrationError(f"{label} mapping output disagrees with its card")
        if card_id in seen_cards:
            raise IntegrationError(f"{label} mapping is not a card bijection")
        seen_cards.add(card_id)
        if "length" in row:
            length = require_int(row["length"], f"{label} mapping length")
            if length != card["length"]:
                raise IntegrationError(f"{label} mapping length disagrees with its card")
        elif require_full_metadata:
            raise IntegrationError(f"{label} mapping omits derived length")
        for key, value in card.items():
            if key in {"card_id", "output", "role", "length"}:
                continue
            if require_full_metadata and row.get(key) != value:
                raise IntegrationError(f"{label} mapping omits registered card metadata")

        canonical_row: dict[str, object] = {
            "primitive_id": primitive_id,
            "role": role,
            "card_id": card_id,
            "output": output,
            "length": card["length"],
        }
        for key in sorted(card):
            if key not in {"card_id", "output", "role", "length"}:
                canonical_row[key] = card[key]
        canonical.append(canonical_row)
    if len(seen_cards) != len(context.cards):
        raise IntegrationError(f"{label} mapping is not a complete card bijection")
    return canonical


def canonical_rank_list(value: object, label: str, maximum: int) -> list[int]:
    raw = require_list(value, label)
    ranks = [require_int(rank, label) for rank in raw]
    if ranks != sorted(set(ranks)):
        raise IntegrationError(f"{label} must be strictly ascending and unique")
    if any(rank < 1 or rank > maximum for rank in ranks):
        raise IntegrationError(f"{label} contains an out-of-range rank")
    return ranks


def canonical_primary(
    result: Mapping[str, object], context: RegisteredContext
) -> dict[str, object]:
    if result.get("schema") != PRIMARY_SCHEMA:
        raise IntegrationError("unexpected primary result schema")
    if result.get("decision") != "STAGE0_MAPPING_BOUND_PASS":
        raise IntegrationError("primary did not produce a complete mapping-bound pass")
    if result.get("input_hashes") != dict(context.input_hashes):
        raise IntegrationError("primary result input hashes disagree with the runner")

    mapping = canonical_mapping(
        result.get("mapping"), context, "primary", require_full_metadata=True
    )
    objective = require_dict(result.get("objective"), "primary objective")
    support_count = require_int(
        objective.get("raw_train_supported_named_merges"), "primary support count"
    )
    cover_count = require_int(
        objective.get("exact_minimum_core_hit"), "primary cover count"
    )
    lexicographic_key = require_list(
        objective.get("lexicographic_card_id_sequence"), "primary lexicographic key"
    )
    mapping_key = [row["card_id"] for row in mapping]
    if lexicographic_key != mapping_key:
        raise IntegrationError("primary objective key disagrees with its mapping")

    raw_merges = require_list(result.get("raw_merges"), "primary raw merges")
    if len(raw_merges) != len(context.merge_names):
        raise IntegrationError("primary raw-merge count mismatch")
    supported_ranks: list[int] = []
    for expected_rank, (raw_row, expected_name) in enumerate(
        zip(raw_merges, context.merge_names), 1
    ):
        row = require_dict(raw_row, f"primary raw merge {expected_rank}")
        if row.get("rank") != expected_rank or row.get("merge") != expected_name:
            raise IntegrationError("primary raw merges disagree with merge-tree order")
        member = row.get("train_substring_member")
        if not isinstance(member, bool):
            raise IntegrationError("primary support membership must be Boolean")
        if member:
            supported_ranks.append(expected_rank)
    if len(supported_ranks) != support_count:
        raise IntegrationError("primary support count disagrees with support ranks")

    raw_cover = require_list(
        result.get("canonical_minimum_cover"), "primary canonical cover"
    )
    cover_ranks: list[int] = []
    for position, raw_row in enumerate(raw_cover):
        row = require_dict(raw_row, f"primary cover row {position}")
        rank = require_int(row.get("rank"), "primary cover rank")
        if not 1 <= rank <= len(context.merge_names):
            raise IntegrationError("primary cover rank is out of range")
        if row.get("merge") != context.merge_names[rank - 1]:
            raise IntegrationError("primary cover name disagrees with merge tree")
        cover_ranks.append(rank)
    if cover_ranks != sorted(set(cover_ranks)) or len(cover_ranks) != cover_count:
        raise IntegrationError("primary canonical cover is malformed")

    negative = require_dict(result.get("negative_control"), "primary negative control")
    negative_support = require_int(
        negative.get("replayed_raw_supported_merges"),
        "primary negative-control support",
    )
    negative_cover = require_int(
        negative.get("replayed_exact_minimum"), "primary negative-control cover"
    )
    if negative.get("expected_raw_supported_merges") != negative_support:
        raise IntegrationError("primary negative-control support replay failed")
    if negative.get("expected_exact_minimum") != negative_cover:
        raise IntegrationError("primary negative-control cover replay failed")
    negative_cover_ranks = canonical_rank_list(
        negative.get("canonical_cover_ranks"),
        "primary negative-control cover ranks",
        len(context.merge_names),
    )
    if len(negative_cover_ranks) != negative_cover:
        raise IntegrationError("primary negative-control witness size mismatch")

    return {
        "decision": "STAGE0_MAPPING_BOUND_PASS",
        "mapping": mapping,
        "lexicographic_card_id_sequence": mapping_key,
        "raw_supported_merge_count": support_count,
        "supported_merge_ranks": supported_ranks,
        "minimum_inclusive_dag_cover": cover_count,
        "minimum_cover_ranks": cover_ranks,
        "negative_control": {
            "raw_supported_merge_count": negative_support,
            "minimum_inclusive_dag_cover": negative_cover,
            "minimum_cover_ranks": negative_cover_ranks,
        },
    }


def canonical_independent(
    result: Mapping[str, object], context: RegisteredContext
) -> dict[str, object]:
    if result.get("schema") != INDEPENDENT_SCHEMA:
        raise IntegrationError("unexpected independent result schema")
    if (
        result.get("status") != "GLOBAL_OPTIMUM_COMPLETE"
        or result.get("complete") is not True
    ):
        raise IntegrationError("independent global-optimum proof is incomplete")
    if result.get("winner_direct_replay_matches") is not True:
        raise IntegrationError("independent winner replay failed")
    if result.get("input_sha256") != dict(context.input_hashes):
        raise IntegrationError("independent result input hashes disagree with the runner")

    mapping = canonical_mapping(
        result.get("mapping"), context, "independent", require_full_metadata=False
    )
    objective = require_dict(result.get("objective"), "independent objective")
    support_count = require_int(
        objective.get("raw_supported_merge_count"), "independent support count"
    )
    cover_count = require_int(
        objective.get("minimum_inclusive_dag_cover"), "independent cover count"
    )
    supported_ranks = canonical_rank_list(
        result.get("supported_merge_ranks"),
        "independent supported-merge ranks",
        len(context.merge_names),
    )
    cover_ranks = canonical_rank_list(
        result.get("minimum_cover_ranks"),
        "independent minimum-cover ranks",
        len(context.merge_names),
    )
    if len(supported_ranks) != support_count:
        raise IntegrationError("independent support count disagrees with support ranks")
    if len(cover_ranks) != cover_count:
        raise IntegrationError("independent cover count disagrees with witness size")

    negative = require_dict(
        result.get("negative_control"), "independent negative control"
    )
    if negative.get("matches_registered_expectation") is not True:
        raise IntegrationError("independent negative-control replay failed")
    negative_support = require_int(
        negative.get("raw_supported_merge_count"),
        "independent negative-control support",
    )
    negative_cover = require_int(
        negative.get("minimum_inclusive_dag_cover"),
        "independent negative-control cover",
    )
    negative_cover_ranks = canonical_rank_list(
        negative.get("minimum_cover_ranks"),
        "independent negative-control cover ranks",
        len(context.merge_names),
    )
    if len(negative_cover_ranks) != negative_cover:
        raise IntegrationError("independent negative-control witness size mismatch")

    return {
        "decision": "STAGE0_MAPPING_BOUND_PASS",
        "mapping": mapping,
        "lexicographic_card_id_sequence": [row["card_id"] for row in mapping],
        "raw_supported_merge_count": support_count,
        "supported_merge_ranks": supported_ranks,
        "minimum_inclusive_dag_cover": cover_count,
        "minimum_cover_ranks": cover_ranks,
        "negative_control": {
            "raw_supported_merge_count": negative_support,
            "minimum_inclusive_dag_cover": negative_cover,
            "minimum_cover_ranks": negative_cover_ranks,
        },
    }


def compare_canonical_results(
    primary: Mapping[str, object], independent: Mapping[str, object]
) -> None:
    fields = (
        "decision",
        "mapping",
        "lexicographic_card_id_sequence",
        "raw_supported_merge_count",
        "supported_merge_ranks",
        "minimum_inclusive_dag_cover",
        "minimum_cover_ranks",
        "negative_control",
    )
    mismatches = [field for field in fields if primary.get(field) != independent.get(field)]
    if mismatches:
        raise IntegrationMismatch(mismatches)


def reserve_output_root(raw_path: Path) -> Path:
    output_root = raw_path.expanduser().resolve()
    if any("f84" in component.casefold() for component in output_root.parts):
        raise IntegrationError("output root contains a forbidden sealed-data token")
    if os.path.lexists(output_root):
        raise IntegrationError("refusing to overwrite an existing output root")
    try:
        output_root.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        raise IntegrationError("cannot create the requested output root") from exc
    return output_root


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise IntegrationError("fixed solver/input path escaped the repository") from exc


def primary_command(
    output_root: Path, time_limit_seconds: int, workers: int
) -> list[str]:
    return [
        sys.executable,
        repo_relative(PRIMARY_SOURCE),
        "--registered-search",
        repo_relative(REGISTERED_SEARCH),
        "--train-substrings",
        repo_relative(REGISTERED_SUBSTRINGS),
        "--merge-tree",
        repo_relative(MERGE_TREE),
        "--work-dir",
        str(output_root / "primary"),
        "--time-limit-seconds",
        str(time_limit_seconds),
        "--workers",
        str(workers),
    ]


def independent_command(
    output_root: Path, time_limit_seconds: int, workers: int
) -> list[str]:
    return [
        str(output_root / "independent/bin/stage0_independent"),
        "--registered-search",
        repo_relative(REGISTERED_SEARCH),
        "--substrings",
        repo_relative(REGISTERED_SUBSTRINGS),
        "--merge-tree",
        repo_relative(MERGE_TREE),
        "--output",
        str(output_root / "independent/RESULT.json"),
        "--threads",
        str(workers),
        "--time-limit",
        str(time_limit_seconds),
    ]


def run_logged(stage: str, command: Sequence[str], output_root: Path) -> None:
    log_dir = output_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    print(f"{stage}: starting", flush=True)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with (log_dir / f"{stage}.stdout.txt").open("xb") as stdout_handle, (
        log_dir / f"{stage}.stderr.txt"
    ).open("xb") as stderr_handle:
        completed = subprocess.run(
            list(command),
            cwd=ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=False,
        )
    if completed.returncode != 0:
        raise StageFailure(stage, completed.returncode)
    print(f"{stage}: complete", flush=True)


def validate_primary_artifacts(
    primary_dir: Path,
    result: Mapping[str, object],
    expected_input_hashes: Mapping[str, str],
    primary_source_hash: str,
) -> None:
    result_path = primary_dir / "RESULT.json"
    result_hash = sha256_path(result_path)
    try:
        declared_hash = (primary_dir / "RESULT.sha256").read_text(
            encoding="ascii"
        ).strip()
    except (OSError, UnicodeError) as exc:
        raise IntegrationError("cannot read primary result hash") from exc
    if declared_hash != result_hash:
        raise IntegrationError("primary result hash replay failed")
    complete = load_json(primary_dir / "COMPLETE.json", "primary completion state")
    if (
        complete.get("status") != "COMPLETE"
        or complete.get("decision") != result.get("decision")
        or complete.get("result_sha256") != result_hash
    ):
        raise IntegrationError("primary completion state disagrees with its result")
    manifest = load_json(primary_dir / "INPUT_MANIFEST.json", "primary input manifest")
    for name, digest in expected_input_hashes.items():
        if manifest.get(name) != digest:
            raise IntegrationError("primary input manifest hash mismatch")
    if manifest.get("solver_source") != primary_source_hash:
        raise IntegrationError("primary solver source changed during execution")
    query_path = primary_dir / "QUERY_CERTIFICATES.jsonl"
    if not query_path.is_file() or query_path.stat().st_size == 0:
        raise IntegrationError("primary query certificates are missing")


def build_integration_result(
    canonical: Mapping[str, object],
    context: RegisteredContext,
    primary_source_hash: str,
    independent_source_hash: str,
) -> dict[str, object]:
    supported_ranks = require_list(
        canonical.get("supported_merge_ranks"), "canonical support ranks"
    )
    cover_ranks = require_list(
        canonical.get("minimum_cover_ranks"), "canonical cover ranks"
    )
    return {
        "schema": INTEGRATION_SCHEMA,
        "status": "PRIMARY_INDEPENDENT_AGREEMENT_PASS",
        "decision": canonical["decision"],
        "input_hashes": dict(context.input_hashes),
        "solver_source_hashes": {
            "primary/solve.py": primary_source_hash,
            "independent/stage0_independent.cpp": independent_source_hash,
        },
        "objective": {
            "raw_train_supported_named_merges": canonical[
                "raw_supported_merge_count"
            ],
            "exact_minimum_core_hit": canonical[
                "minimum_inclusive_dag_cover"
            ],
            "lexicographic_card_id_sequence": canonical[
                "lexicographic_card_id_sequence"
            ],
        },
        "mapping": canonical["mapping"],
        "raw_supported_merges": [
            {"rank": rank, "merge": context.merge_names[rank - 1]}
            for rank in supported_ranks
        ],
        "canonical_minimum_cover": [
            {"rank": rank, "merge": context.merge_names[rank - 1]}
            for rank in cover_ranks
        ],
        "negative_control": canonical["negative_control"],
        "agreement": {
            "mapping": True,
            "objective": True,
            "raw_supported_merge_set": True,
            "canonical_minimum_cover": True,
            "negative_control": True,
        },
    }


def reproduce(output_root: Path, time_limit_seconds: int, workers: int) -> Path:
    root = reserve_output_root(output_root)
    stage = "initialization"
    try:
        input_hashes = snapshot_inputs()
        context = load_registered_context(input_hashes)
        primary_source_hash = sha256_path(PRIMARY_SOURCE)
        independent_source_hash = sha256_path(INDEPENDENT_SOURCE)
        exclusive_write_json(
            root / "RUN_CONFIG.json",
            {
                "schema": "gdt615-stage0-integration-config-v1",
                "scientific_inputs": input_hashes,
                "primary_source_sha256": primary_source_hash,
                "independent_source_sha256": independent_source_hash,
                "time_limit_seconds_per_solver": time_limit_seconds,
                "workers_per_solver": workers,
            },
        )

        stage = "primary"
        run_logged(
            stage,
            primary_command(root, time_limit_seconds, workers),
            root,
        )
        assert_inputs_unchanged(input_hashes, stage)
        primary_result = load_json(root / "primary/RESULT.json", "primary result")
        validate_primary_artifacts(
            root / "primary",
            primary_result,
            input_hashes,
            primary_source_hash,
        )

        compiler = shutil.which("g++")
        if compiler is None:
            raise IntegrationError("g++ is required for the independent solver")
        independent_binary = root / "independent/bin/stage0_independent"
        independent_binary.parent.mkdir(parents=True, exist_ok=False)
        stage = "independent_build"
        run_logged(
            stage,
            [
                compiler,
                "-O3",
                "-std=c++20",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-pthread",
                repo_relative(INDEPENDENT_SOURCE),
                "-o",
                str(independent_binary),
            ],
            root,
        )
        stage = "independent_self_test"
        run_logged(stage, [str(independent_binary), "--self-test"], root)
        stage = "independent"
        run_logged(
            stage,
            independent_command(root, time_limit_seconds, workers),
            root,
        )
        assert_inputs_unchanged(input_hashes, stage)
        if sha256_path(PRIMARY_SOURCE) != primary_source_hash:
            raise IntegrationError("primary source changed during reproduction")
        if sha256_path(INDEPENDENT_SOURCE) != independent_source_hash:
            raise IntegrationError("independent source changed during reproduction")

        independent_result = load_json(
            root / "independent/RESULT.json", "independent result"
        )
        primary_canonical = canonical_primary(primary_result, context)
        independent_canonical = canonical_independent(independent_result, context)
        stage = "cross_solver_comparison"
        compare_canonical_results(primary_canonical, independent_canonical)

        result = build_integration_result(
            primary_canonical,
            context,
            primary_source_hash,
            independent_source_hash,
        )
        result_path = root / "RESULT.json"
        exclusive_write_json(result_path, result)
        result_hash = sha256_path(result_path)
        exclusive_write(root / "RESULT.sha256", (result_hash + "\n").encode("ascii"))
        exclusive_write_json(
            root / "RUN_STATE.json",
            {
                "schema": "gdt615-stage0-integration-run-state-v1",
                "status": "COMPLETE",
                "result_sha256": result_hash,
                "primary_result_sha256": sha256_path(root / "primary/RESULT.json"),
                "independent_result_sha256": sha256_path(
                    root / "independent/RESULT.json"
                ),
                "independent_binary_sha256": sha256_path(independent_binary),
            },
        )
        exclusive_write_json(
            root / "COMPLETE.json",
            {
                "schema": "gdt615-stage0-integration-completion-v1",
                "status": "COMPLETE",
                "decision": result["decision"],
                "result_sha256": result_hash,
            },
        )
        print(
            "cross_solver_comparison: complete "
            f"support={primary_canonical['raw_supported_merge_count']} "
            f"cover={primary_canonical['minimum_inclusive_dag_cover']}",
            flush=True,
        )
        return result_path
    except Exception as exc:
        failure_path = root / "FAILURE.json"
        if not failure_path.exists():
            failure: dict[str, object] = {
                "schema": "gdt615-stage0-integration-failure-v1",
                "status": "IMPLEMENTATION_OR_VALIDATION_FAILURE",
                "stage": stage,
                "exception_type": type(exc).__name__,
                "reason": str(exc),
            }
            if isinstance(exc, IntegrationMismatch):
                failure["mismatched_fields"] = list(exc.fields)
            exclusive_write_json(failure_path, failure)
        raise


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        required=True,
        type=Path,
        help="new, nonexistent directory that will contain both solver runs",
    )
    parser.add_argument(
        "--time-limit-seconds",
        type=int,
        default=MAXIMUM_TIME_LIMIT_SECONDS,
        help="per-solver limit (maximum: 14400)",
    )
    parser.add_argument("--workers", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(sys.argv[1:] if argv is None else argv)
    if not 1 <= args.time_limit_seconds <= MAXIMUM_TIME_LIMIT_SECONDS:
        raise SystemExit(
            f"--time-limit-seconds must be in 1..{MAXIMUM_TIME_LIMIT_SECONDS}"
        )
    if not 1 <= args.workers <= MAXIMUM_WORKERS:
        raise SystemExit(f"--workers must be in 1..{MAXIMUM_WORKERS}")
    try:
        result_path = reproduce(
            args.output_root,
            args.time_limit_seconds,
            args.workers,
        )
    except IntegrationError as exc:
        print(f"STAGE0_INTEGRATION_FAILURE: {exc}", file=sys.stderr, flush=True)
        return 1
    print(f"STAGE0_INTEGRATION_PASS result={result_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
