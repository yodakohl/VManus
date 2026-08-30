#!/usr/bin/env python3
"""Independent source-first validator for GDT675."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan"
ART = EXP / "artifacts"
CARDS_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/src/F81R_TRANSFER_CARDS.tsv"
TRACES_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/artifacts/F81R_COMPONENT_TRACES.tsv"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
ALLOWLIST_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/PAGE_ALLOWLIST.tsv"
OLD_OCC_PATH = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/artifacts/TRANSFERABLE_EXACT_OCCURRENCES.tsv"
DECISIONS_PATH = EXP / "src/CARD_TRANSFER_DECISIONS.tsv"
RUN_PATH = EXP / "src/run.py"
VALIDATION_PATH = ART / "VALIDATION.json"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unknowns(row: dict[str, str]) -> set[int]:
    return {int(value) for value in row["unknown_ordinals"].split("|") if value and value != "NONE"}


def align(source: list[str], alternate: list[str]) -> dict[int, tuple[str, str]]:
    n, m = len(source), len(alternate)
    grid: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    grid[0][0] = (0, 0, [])

    def place(i: int, j: int, candidate: tuple[int, int, list[tuple[str, tuple[int, ...], str]]]) -> None:
        if grid[i][j] is None or candidate[:2] < grid[i][j][:2]:
            grid[i][j] = candidate

    for i in range(n + 1):
        for j in range(m + 1):
            cell = grid[i][j]
            if cell is None:
                continue
            cost, steps, path = cell
            if i < n and j < m:
                place(i + 1, j + 1, (cost + (0 if source[i] == alternate[j] else 10), steps + 1,
                                      [*path, ("ONE", (i,), alternate[j])]))
            if i + 1 < n and j < m and source[i] + source[i + 1] == alternate[j]:
                place(i + 2, j + 1, (cost + 1, steps + 1, [*path, ("MERGE_2", (i, i + 1), alternate[j])]))
            if i + 2 < n and j < m and source[i] + source[i + 1] + source[i + 2] == alternate[j]:
                place(i + 3, j + 1, (cost + 1, steps + 1, [*path, ("MERGE_3", (i, i + 1, i + 2), alternate[j])]))
            if i < n and j + 1 < m and source[i] == alternate[j] + alternate[j + 1]:
                place(i + 1, j + 2, (cost + 1, steps + 1, [*path, ("SPLIT_2", (i,), source[i])]))
            if i < n:
                place(i + 1, j, (cost + 10, steps + 1, [*path, ("DELETE", (i,), "")]))
            if j < m:
                place(i, j + 1, (cost + 10, steps + 1, [*path, ("INSERT", (), alternate[j])]))
    final = grid[n][m]
    if final is None:
        raise RuntimeError("no reader alignment")
    result: dict[int, tuple[str, str]] = {}
    for operation, indices, rendered in final[2]:
        for index in indices:
            result[index] = (
                "EXACT" if operation == "ONE" and rendered == source[index] else operation,
                rendered or "EMPTY",
            )
    if set(result) != set(range(n)):
        raise RuntimeError("reader alignment is incomplete")
    return result


def guarded_query(allowlist: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", "transcription/voynich_cross_transcription_lines.tsv",
        "--selector", "page",
    ]
    for page in allowlist:
        command.extend(("--allow", page))
    command.extend((
        "--columns", "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
        "--forbid-prefix", "f84",
    ))
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("missing guard statistics")
    return (
        list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")),
        {str(key): int(value) for key, value in json.loads(match.group(1)).items()},
    )


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(condition: bool, name: str, detail: object = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    cards = read_tsv(CARDS_PATH)
    card_by_surface = {row["surface"]: row for row in cards}
    decisions = {row["surface"]: row for row in read_tsv(DECISIONS_PATH)}
    panel = read_tsv(PANEL_PATH)
    allowlist = [row["page"] for row in read_tsv(ALLOWLIST_PATH)]
    old_overlay = {
        (row["locus"], int(row["ordinal"])): row
        for row in read_tsv(OLD_OCC_PATH)
        if row["promotable"] == "1" and row["was_v48_unknown"] == "1"
    }
    occurrences = read_tsv(ART / "EXACT_OCCURRENCE_CONTEXTS.tsv")
    external = read_tsv(ART / "EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv")
    source_rows = read_tsv(ART / "SOURCE_PAGE_CARD_OCCURRENCES.tsv")
    profiles = read_tsv(ART / "CARD_PANEL_TRANSFER_PROFILE.tsv")
    compositions = read_tsv(ART / "COMPOSITION_BYTE_AUDIT.tsv")
    touched = read_tsv(ART / "TOUCHED_LINE_OVERLAY.tsv")
    closed = read_tsv(ART / "NEWLY_CLOSED_LINES.tsv")
    rivals = read_tsv(ART / "READER_RIVAL_OCCURRENCES.tsv")
    promoted = read_tsv(ART / "V50_PANEL_TRANSFER_OVERLAY.tsv")
    source_only = read_tsv(ART / "SOURCE_ONLY_CARDS.tsv")
    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))

    check(len(cards) == 23, "card_count", len(cards))
    check(Counter(row["class"] for row in cards) == {"P": 20, "W": 3}, "card_classes")
    check(set(decisions) == set(card_by_surface), "decision_surface_identity")
    check(len(panel) == 4128, "panel_line_count", len(panel))
    check(len(allowlist) == len(set(allowlist)) == 179, "allowlist_count", len(allowlist))
    check("f81r" in allowlist, "source_page_admitted")
    check(all(not page.lower().startswith("f84") for page in allowlist), "allowlist_excludes_f84")
    check(len(old_overlay) == 162, "gdt673_overlay_count", len(old_overlay))

    cross_rows, guard = guarded_query(allowlist)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    check(guard.get("selected") == len(cross_rows) == 4137, "guard_selected", guard)
    check(guard.get("skipped_forbidden", 0) > 0, "guard_forbidden_gate", guard)
    check(all(not row["page"].lower().startswith("f84") for row in cross_rows), "guard_output_excludes_f84")

    artifact_by_key = {(row["locus"], int(row["ordinal"])): row for row in occurrences}
    expected_keys: set[tuple[str, int]] = set()
    expected_external: set[tuple[str, int]] = set()
    reader_counts = Counter()
    external_reader_counts = Counter()
    metrics = {name: Counter() for name in ("GDT673", "GDT674", "GDT675")}
    promoted_surfaces = {row["surface"] for row in promoted}
    for line in panel:
        tokens = line["zl3b_line"].split()
        v48_unknown = unknowns(line)
        v49_unknown = {index for index in v48_unknown if (line["locus"], index) not in old_overlay}
        gdt674_unknown = {
            index for index in v49_unknown
            if not (line["page"] == "f81r" and tokens[index - 1] in card_by_surface)
        }
        gdt675_unknown = {
            index for index in gdt674_unknown
            if not (line["page"] != "f81r" and tokens[index - 1] in promoted_surfaces)
        }
        for name, values in (("GDT673", v49_unknown), ("GDT674", gdt674_unknown), ("GDT675", gdt675_unknown)):
            metrics[name]["unknown"] += len(values)
            metrics[name]["complete"] += not values
            if len(tokens) > 1:
                metrics[name]["multi_complete"] += not values
                metrics[name]["multi_one"] += len(values) == 1
        hit_indices = [i for i, token in enumerate(tokens, start=1) if token in card_by_surface]
        if not hit_indices:
            continue
        cross = cross_by_locus.get(line["locus"])
        check(cross is not None, f"cross_locus:{line['locus']}")
        if cross is None:
            continue
        check(cross["zl3b_clean"].split() == tokens, f"cross_zl3b:{line['locus']}")
        it2a = align(tokens, cross["it2a_clean"].split())
        rf1b = align(tokens, cross["rf1b_clean"].split())
        for index in hit_indices:
            key = (line["locus"], index)
            expected_keys.add(key)
            if line["page"] != "f81r":
                expected_external.add(key)
            row = artifact_by_key.get(key)
            check(row is not None, f"occurrence_present:{line['locus']}:{index}")
            if row is None:
                continue
            check(row["surface"] == tokens[index - 1], f"surface:{line['locus']}:{index}")
            check(row["was_v49_unknown"] == ("1" if index in v49_unknown else "0"), f"v49_state:{line['locus']}:{index}")
            check(row["source_f81r"] == ("1" if line["page"] == "f81r" else "0"), f"source_flag:{line['locus']}:{index}")
            a, b = it2a[index - 1][0], rf1b[index - 1][0]
            support = "BOTH_EXACT" if a == b == "EXACT" else "ONE_EXACT" if "EXACT" in {a, b} else "NEITHER_EXACT"
            check(row["reader_support"] == support, f"reader_support:{line['locus']}:{index}")
            check(row["it2a_operation"] == a and row["rf1b_operation"] == b, f"reader_ops:{line['locus']}:{index}")
            reader_counts[support] += 1
            if line["page"] != "f81r":
                external_reader_counts[support] += 1

    check(set(artifact_by_key) == expected_keys, "exact_occurrence_keyset")
    check(len(expected_keys) == 75, "all_occurrence_count", len(expected_keys))
    check(len(expected_external) == 51, "external_occurrence_count", len(expected_external))
    check({(row["locus"], int(row["ordinal"])) for row in external} == expected_external, "external_keyset")
    check(len(source_rows) == 24, "source_occurrence_count", len(source_rows))
    check(reader_counts == {"BOTH_EXACT": 52, "ONE_EXACT": 18, "NEITHER_EXACT": 5}, "all_reader_profile", reader_counts)
    check(external_reader_counts == {"BOTH_EXACT": 42, "ONE_EXACT": 7, "NEITHER_EXACT": 2}, "external_reader_profile", external_reader_counts)
    check(len({row["surface"] for row in external}) == 12, "external_surface_count")
    check(len({row["page"] for row in external}) == 36, "external_page_count")
    check(len({row["locus"] for row in external}) == 51, "external_line_count")
    check(all(row["was_gdt674_unknown"] == "1" for row in external), "all_external_were_open")

    check(len(profiles) == 23, "profile_count")
    profile_by_surface = {row["surface"]: row for row in profiles}
    for surface, card in card_by_surface.items():
        hits = [row for row in occurrences if row["surface"] == surface]
        outside = [row for row in hits if row["source_f81r"] == "0"]
        profile = profile_by_surface[surface]
        check(int(profile["external_positions"]) == len(outside), f"profile_external:{surface}")
        check(profile["composition"] == card["composition"], f"profile_composition:{surface}")
        check(profile["decision"] == decisions[surface]["decision"], f"profile_decision:{surface}")
        check(profile["render_mode"] == decisions[surface]["render_mode"], f"profile_render:{surface}")
    check(Counter(row["decision"] for row in profiles) == {
        "HOLD_SAME_CARD": 2, "HOLD_WITH_ACTION_RESULT_SPLIT": 4,
        "HOLD_WITH_SCOPE_SPLIT": 5, "HOLD_LEARNED_WHOLE": 1,
        "SOURCE_PAGE_ONLY_UNTESTED": 11,
    }, "decision_profile")
    check(len(promoted) == 12, "promoted_surface_count")
    check(len(source_only) == 11, "source_only_count")

    traces = read_tsv(TRACES_PATH)
    check(len(compositions) == 20, "composition_audit_count")
    for row in compositions:
        surface = row["surface"]
        check(row["byte_complete"] == "1", f"byte_complete:{surface}")
        check(row["segment_trace"].replace("+", "") == surface, f"segment_join:{surface}")
        check(row["role_trace"] == card_by_surface[surface]["composition"], f"role_join:{surface}")
        source_ordinal = int(row["source_global_ordinal"])
        trace = [item for item in traces if item["eva"] == surface and int(item["global_ordinal"]) == source_ordinal]
        check("".join(item["surface_segment"] for item in sorted(trace, key=lambda item: int(item["component_ordinal"]))) == surface,
              f"source_trace:{surface}")

    check(len(touched) == 51, "touched_line_count")
    check(len(closed) == 2, "newly_closed_count")
    check({row["locus"] for row in closed} == {"f102v2.3", "f112v.10"}, "closed_loci")
    check(len(rivals) == 5, "reader_rival_count")
    check(sum(row["source_f81r"] == "0" for row in rivals) == 2, "external_reader_rivals")
    check({row["surface"] for row in rivals if row["source_f81r"] == "0"} == {"olkar"}, "external_reader_rival_surface")
    check(metrics["GDT673"]["unknown"] == 8018, "gdt673_unknown")
    check(metrics["GDT674"]["unknown"] == 7994, "gdt674_unknown")
    check(metrics["GDT675"]["unknown"] == 7943, "gdt675_unknown")
    check(metrics["GDT674"]["complete"] == 1380 and metrics["GDT675"]["complete"] == 1382, "complete_lines")
    check(metrics["GDT674"]["multi_complete"] == 1258 and metrics["GDT675"]["multi_complete"] == 1259,
          "multi_complete_lines")
    check(metrics["GDT674"]["multi_one"] == 172 and metrics["GDT675"]["multi_one"] == 180,
          "multi_one_unknown")

    check(result["status"] == "PASS_51_EXTERNAL_POSITIONS__12_CARDS_HOLD__9_RENDER_SPLITS__11_SOURCE_ONLY",
          "result_status", result["status"])
    check(result["cards"]["action_result_split_surfaces"] == 4, "result_action_result_splits")
    check(result["cards"]["scope_or_boundary_split_surfaces"] == 5, "result_scope_splits")
    check(result["coverage_overlay"]["unknown_positions_after"] == 7943, "result_unknown_after")
    for filename, expected_hash in result["files"].items():
        path = ART / filename
        check(path.is_file(), f"result_file:{filename}")
        if path.is_file():
            check(digest(path) == expected_hash, f"result_hash:{filename}")

    replay_paths = sorted(path for path in ART.glob("*") if path.is_file() and path.name != "VALIDATION.json")
    before = {path.name: digest(path) for path in replay_paths}
    completed = subprocess.run(["python3", str(RUN_PATH)], cwd=ROOT, text=True, capture_output=True)
    check(completed.returncode == 0, "builder_replay_exit", completed.stderr[-1000:])
    after = {path.name: digest(path) for path in replay_paths}
    check(before == after, "builder_byte_identical_replay")

    failed = sum(not row["pass"] for row in checks)
    validation = {
        "status": "PASS" if failed == 0 else "FAIL",
        "checks_passed": len(checks) - failed,
        "checks_failed": failed,
        "checks": checks,
    }
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("status", "checks_passed", "checks_failed")}, sort_keys=True))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
