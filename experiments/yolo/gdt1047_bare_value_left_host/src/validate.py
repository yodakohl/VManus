#!/usr/bin/env python3
"""Independent source reconstruction for GDT1047; never imports its runner."""
from __future__ import annotations

import argparse
import collections
import copy
import csv
import hashlib
import json
import subprocess
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
COLS = ["source_group_id", "edition", "page", "locus", "source_row_index",
        "source_group_index", "source_group_count", "kind", "paragraph_start",
        "paragraph_end", "left_separator", "right_separator", "ivtff_group_raw"]
INVENTORIES = {"FAMILY": {"dan", "dain", "daiin", "daiiin"},
               "DAIIN": {"daiin"}, "AIIN": {"aiin"}}
EDITIONS = {"ZL3b", "IT2a", "RF1b"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def flag(value: str) -> bool:
    if value not in {"0", "1"}:
        raise ValueError(f"Unexpected boundary flag {value!r}")
    return value == "1"


def reconstruct(rows: list[dict[str, str]]) -> list[dict]:
    """Group source loci before scanning independently ordered streams."""
    ids = [r["source_group_id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate source group ID"
    loci: dict[tuple, list[dict]] = collections.defaultdict(list)
    for row in rows:
        loci[(row["edition"], row["page"], int(row["source_row_index"]))].append(row)
    streams: dict[tuple, list[list[dict]]] = collections.defaultdict(list)
    consistent = ["edition", "page", "locus", "source_row_index",
                  "source_group_count", "kind", "paragraph_start", "paragraph_end"]
    for (edition, page, _), groups in loci.items():
        for column in consistent:
            assert len({r[column] for r in groups}) == 1, ("inconsistent locus", column)
        groups.sort(key=lambda r: int(r["source_group_index"]))
        count = int(groups[0]["source_group_count"])
        assert len(groups) == count, "incomplete locus group count"
        assert [int(r["source_group_index"]) for r in groups] == list(range(1, count + 1)), "group ordering"
        streams[(edition, page)].append(groups)
    blocks = []
    for (edition, page), source_loci in sorted(streams.items()):
        source_loci.sort(key=lambda groups: int(groups[0]["source_row_index"]))
        pending: list[dict] = []
        starts = False
        for groups in source_loci:
            first = groups[0]
            pstart, pend = flag(first["paragraph_start"]), flag(first["paragraph_end"])
            if first["kind"] != "P" or pstart:
                if pending:
                    blocks.append({"edition": edition, "page": page, "groups": pending,
                                   "explicit_start": starts, "explicit_end": False})
                    pending = []
            if first["kind"] != "P":
                continue
            if not pending:
                starts = pstart
            pending.extend(groups)
            if pend:
                blocks.append({"edition": edition, "page": page, "groups": pending,
                               "explicit_start": starts, "explicit_end": True})
                pending = []
        if pending:
            blocks.append({"edition": edition, "page": page, "groups": pending,
                           "explicit_start": starts, "explicit_end": False})
    assert sum(len(b["groups"]) for b in blocks) == sum(r["kind"] == "P" for r in rows)
    return blocks


def inventory_runs(block: dict, name: str) -> list[dict]:
    groups = block["groups"]
    members = INVENTORIES[name]
    runs = []
    index = 0
    while index < len(groups):
        if groups[index]["ivtff_group_raw"] not in members:
            index += 1
            continue
        first = index
        while index < len(groups) and groups[index]["ivtff_group_raw"] in members:
            index += 1
        left = "CAPACITY" if first else "CONTRADICTION" if block["explicit_start"] else "UNKNOWN"
        right = "CAPACITY" if index < len(groups) else "CONTRADICTION" if block["explicit_end"] else "UNKNOWN"
        runs.append({"inventory": name, "groups": groups[first:index], "start": first,
                     "end": index, "left": left, "right": right})
    return runs


def synthetic_checks() -> list[str]:
    """Boundary capacity checks include known failure modes, not word meanings."""
    def row(number: int, form: str, start: str = "0", end: str = "0", kind: str = "P") -> dict:
        return dict(zip(COLS, [f"test-{number}", "ZL3b", "f1r", str(number),
                    str(number), "1", "1", kind, start, end, "", "", form]))

    closed = reconstruct([row(1, "daiin", "1"), row(2, "daiiin"),
                          row(3, "unknown", end="1")])
    run = inventory_runs(closed[0], "FAMILY")[0]
    assert (run["left"], run["right"], len(run["groups"])) == ("CONTRADICTION", "CAPACITY", 2)
    single = inventory_runs(reconstruct([row(1, "daiin", "1", "1")])[0], "DAIIN")[0]
    assert single["left"] == single["right"] == "CONTRADICTION"
    fragment = inventory_runs(reconstruct([row(1, "daiin")])[0], "DAIIN")[0]
    assert fragment["left"] == fragment["right"] == "UNKNOWN"
    split = reconstruct([row(1, "unknown", "1"), row(2, "daiin", "1", "1")])
    assert len(split) == 2 and split[0]["explicit_end"] is False
    non_p = reconstruct([row(1, "unknown", "1"), row(2, "label", kind="L"),
                         row(3, "daiin", end="1")])
    assert len(non_p) == 2 and inventory_runs(non_p[1], "DAIIN")[0]["left"] == "UNKNOWN"
    assert inventory_runs(closed[0], "DAIIN")[0]["right"] == "CAPACITY"
    for broken in ([row(1, "daiin"), row(1, "daiin")],
                   [dict(row(1, "daiin"), source_group_count="2")]):
        try:
            reconstruct(broken)
        except AssertionError:
            pass
        else:
            raise AssertionError("Malformed source mutation was accepted")
    return ["maximal_family_run_cannot_host_itself", "marked_singleton_both_directions",
            "unmarked_fragment_is_unknown", "new_start_does_not_invent_previous_end",
            "non_P_breaks_scope", "inventories_remain_separate",
            "duplicate_source_id_rejected", "incomplete_locus_rejected"]


def replay_projection(allow: set[str], path: Path) -> dict:
    """Compare exact bytes with a separately invoked selector-first guard."""
    command = [str(ROOT / "vmanus-exp"), "query-tsv",
               "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
               "--selector", "page"]
    for selector in sorted(allow):
        command.extend(["--allow", selector])
    command.extend(["--columns", ",".join(COLS), "--forbid-prefix", "f84",
                    "--forbid-prefix", "f84r"])
    replay = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    assert replay.stdout == path.read_bytes(), "fresh guarded projection differs"
    diagnostic = replay.stderr.decode("utf-8").strip()
    assert diagnostic.startswith("GUARD_STATS "), "guard receipt missing"
    return {"sha256": hashlib.sha256(replay.stdout).hexdigest(),
            "bytes": len(replay.stdout), "guard_stats": json.loads(diagnostic[len("GUARD_STATS "):])}


def derive(rows: list[dict[str, str]], old: set[str]) -> tuple[list[dict], dict, dict]:
    blocks = reconstruct(rows)
    runs = {}
    summary = {}
    for inventory in INVENTORIES:
        for edition in sorted(EDITIONS):
            for stratum in ("old_overlap27", "additional152", "all179"):
                summary[(inventory, edition, stratum)] = collections.Counter()
    for number, block in enumerate(blocks):
        block["independent_id"] = number
        block["stratum"] = "old_overlap27" if block["page"] in old else "additional152"
        block["has_contradiction"] = False
        for inventory in INVENTORIES:
            for run in inventory_runs(block, inventory):
                key = (inventory, block["edition"], block["page"],
                       run["groups"][0]["source_group_id"], run["groups"][-1]["source_group_id"])
                assert key not in runs
                run.update({"block": block, "key": key})
                runs[key] = run
                block["has_contradiction"] |= "CONTRADICTION" in {run["left"], run["right"]}
                for stratum in (block["stratum"], "all179"):
                    counter = summary[(inventory, block["edition"], stratum)]
                    counter["runs"] += 1
                    counter["tokens"] += len(run["groups"])
                    for side in ("left", "right"):
                        counter[f"{side}_{run[side]}"] += 1
    for inventory, members in INVENTORIES.items():
        for edition in EDITIONS:
            source_count = sum(r["edition"] == edition and r["kind"] == "P" and
                               r["ivtff_group_raw"] in members for r in rows)
            assert source_count == summary[(inventory, edition, "all179")]["tokens"]
    return blocks, runs, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without rewriting VALIDATION.json")
    args = parser.parse_args()
    try:
        result = validate()
    except (AssertionError, ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        result = {"experiment_id": "GDT1047", "status": "FAIL",
                  "error": f"{type(error).__name__}: {error}", "semantic_confirmation": False}
    if not args.check:
        (HERE / "artifacts/VALIDATION.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


def expected_block_id(block: dict) -> str:
    return ":".join([block["edition"], block["page"], block["groups"][0]["locus"]])


def compare_outputs(rows: list[dict], published_runs: list[dict], published_blocks: list[dict],
                    result: dict, blocks: list[dict], runs: dict, summary: dict) -> None:
    assert len(published_runs) == len(runs), "run coverage"
    seen = set()
    for observed in published_runs:
        key = tuple(observed[k] for k in ("inventory", "edition", "page", "start_group_id", "end_group_id"))
        assert key not in seen, "duplicate published run"
        seen.add(key)
        expected = runs[key]
        assert observed["stratum"] == expected["block"]["stratum"], "run stratum"
        assert observed["block_id"] == expected_block_id(expected["block"]), "run block binding"
        assert observed["forms"] == [r["ivtff_group_raw"] for r in expected["groups"]], "run raw groups"
        assert observed["start_index_0based"] == expected["start"], "run start position"
        assert observed["end_index_0based"] == expected["end"] - 1, "run end position"
        for side in ("left", "right"):
            assert observed[f"{side}_status"] == expected[side], ("run directional status", key, side)
    assert seen == set(runs), "missing run identity"

    contradictory = {expected_block_id(b): b for b in blocks if b["has_contradiction"]}
    assert len(published_blocks) == len(contradictory), "contradiction block coverage"
    seen_blocks = set()
    for observed in published_blocks:
        bid = observed["block_id"]
        assert bid not in seen_blocks, "duplicate contradiction block"
        seen_blocks.add(bid)
        expected = contradictory[bid]
        assert observed["edition"] == expected["edition"] and observed["page"] == expected["page"]
        assert observed["left_marked"] is expected["explicit_start"], "block left marker"
        assert observed["right_marked"] is expected["explicit_end"], "block right marker"
        grouped: dict[int, list[dict]] = collections.defaultdict(list)
        for row in expected["groups"]:
            grouped[int(row["source_row_index"])].append(row)
        assert len(observed["lines"]) == len(grouped), "complete block locus coverage"
        for line, (row_number, source_groups) in zip(observed["lines"], grouped.items()):
            assert line["source_row_index"] == row_number, "block locus order"
            for column in ("locus", "kind", "paragraph_start", "paragraph_end"):
                assert line[column] == source_groups[0][column], ("block locus metadata", column)
            assert len(line["groups"]) == len(source_groups), "complete block group coverage"
            for group, source in zip(line["groups"], source_groups):
                assert group["source_group_index"] == int(source["source_group_index"])
                for column in ("source_group_id", "left_separator", "right_separator", "ivtff_group_raw"):
                    assert group[column] == source[column], ("block source identity", column)
    assert seen_blocks == set(contradictory), "missing contradiction block"

    assert result["total_runs"] == len(runs)
    assert result["contradiction_blocks"] == len(contradictory)
    row_counts = {edition: dict(collections.Counter(r["kind"] for r in rows if r["edition"] == edition))
                  for edition in EDITIONS}
    assert result["row_counts"] == row_counts, "all kinds and editions accounted"
    boundary_counts = {edition: {"blocks": sum(b["edition"] == edition for b in blocks),
                                "left_marked": sum(b["edition"] == edition and b["explicit_start"] for b in blocks),
                                "right_marked": sum(b["edition"] == edition and b["explicit_end"] for b in blocks)}
                       for edition in EDITIONS}
    assert result["paragraph_boundary_counts"] == boundary_counts, "boundary totals"
    expected_keys = {key for key in summary if key[-1] != "all179"}
    seen_summary = set()
    for observed in result["summary"]:
        key = tuple(observed[k] for k in ("inventory", "edition", "stratum"))
        assert key not in seen_summary
        seen_summary.add(key)
        expected = summary[key]
        assert observed["occurrences"] == expected["tokens"] and observed["runs"] == expected["runs"]
        for side in ("left", "right"):
            assert observed[side] == {state: expected[f"{side}_{state}"] for state in ("CAPACITY", "CONTRADICTION", "UNKNOWN")}
    assert seen_summary == expected_keys, "all inventory/edition/stratum cells"
    decision_keys = {(inventory, edition, direction) for inventory in INVENTORIES
                     for edition in EDITIONS for direction in ("left", "right")}
    seen_decisions = set()
    for observed in result["decisions"]:
        inventory, edition, side = (observed[k] for k in ("inventory", "edition", "direction"))
        key = inventory, edition, side
        assert key not in seen_decisions
        seen_decisions.add(key)
        expected = summary[(inventory, edition, "all179")]
        counts = {state: expected[f"{side}_{state}"] for state in ("CAPACITY", "CONTRADICTION", "UNKNOWN")}
        assert observed["counts"] == counts, "full directional counts"
        if not (boundary_counts[edition]["left_marked"] or boundary_counts[edition]["right_marked"]):
            verdict = "NO_SOURCE_MARKED_PARAGRAPH_CAPACITY"
        elif counts["CONTRADICTION"]:
            verdict = "CONTRADICTED_FIXED_HOST_CONDITION"
        elif counts["UNKNOWN"]:
            verdict = "COMPATIBLE_NECESSARY_CONDITION_WITH_UNKNOWNS"
        else:
            verdict = "COMPATIBLE_NECESSARY_CONDITION_ONLY"
        assert observed["verdict"] == verdict, ("decision ceiling", key, verdict)
    assert seen_decisions == decision_keys, "all candidate decisions"
    for key, value in {"confirmed_words": 0, "new_access": 0,
                       "statistical_significance_claimed": False, "independent_confirmation": False}.items():
        assert result[key] == value, ("claim ceiling", key)


def validate() -> dict:
    tests = synthetic_checks()
    lock_path = HERE / "src/PREREG_LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    for record in lock["fixed_files"] + lock["inputs"]:
        assert digest(ROOT / record["path"]) == record["sha256"], ("prereg hash", record["path"])
    scope_lock_path = HERE / "src/SCOPE_ADDENDUM_LOCK.json"
    scope_lock = json.loads(scope_lock_path.read_text(encoding="utf-8"))
    assert digest(ROOT / scope_lock["path"]) == scope_lock["sha256"], "scope amendment hash"
    assert lock["registered_utc"] < scope_lock["registered_utc"], "registration order"
    allow_path = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
    allow_rows = tsv(allow_path)
    allow = {r["page"] for r in allow_rows}
    assert len(allow) == len(allow_rows) == 179
    assert all(not p.startswith("f84") and p != "f116v" for p in allow)
    old = {r["source_selector"] for r in tsv(ROOT / "experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv")}
    old |= {r["source_selector"] for r in tsv(ROOT / "experiments/yolo/gdt812_additional_page_semantic_bridge/src/PAGE_ADMISSIONS.tsv")}
    assert (len(old), len(old & allow), len(old - allow), len(allow - old)) == (39, 27, 12, 152)
    projection = HERE / "runtime/PROJECTION.tsv"
    replay = replay_projection(allow, projection)
    rows = tsv(projection)
    assert set(rows[0]) == set(COLS), "exact registered projection columns"
    assert {r["page"] for r in rows} == allow, "projection selector coverage"
    assert {r["edition"] for r in rows} == EDITIONS
    blocks, runs, summary = derive(rows, old)
    artifact_names = ("RUNS.json", "BLOCKS.json", "RESULT.json")
    emitted = [json.loads((HERE / "artifacts" / name).read_text(encoding="utf-8")) for name in artifact_names]
    published_runs, published_blocks, result = emitted
    assert result["registered_utc"] == lock["registered_utc"]
    assert result["selectors"] == len(allow)
    assert result["old_selectors"] == sorted(old & allow)
    assert result["extra_selector_count"] == len(allow - old)
    assert result["old_outside_current_selectors"] == sorted(old - allow)
    assert result["allowlist_sha256"] == digest(allow_path)
    assert result["prereg_lock_sha256"] == digest(lock_path)
    assert result["scope_addendum_lock_sha256"] == digest(scope_lock_path)
    assert result["source_sha256"] == digest(ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv")
    assert result["guarded_query"]["projection_sha256"] == replay["sha256"]
    assert result["guarded_query"]["stats"] == replay["guard_stats"]
    command = result["guarded_query"]["command"]
    assert {command[i + 1] for i, value in enumerate(command) if value == "--allow"} == allow
    assert command[command.index("--selector") + 1] == "page"
    assert command[command.index("--columns") + 1].split(",") == COLS
    assert "f84" in {command[i + 1] for i, value in enumerate(command) if value == "--forbid-prefix"}
    compare_outputs(rows, *emitted, blocks, runs, summary)
    for name in ("changed_run_status", "missing_contradiction_block", "changed_paragraph_flag", "changed_summary_count"):
        changed = copy.deepcopy(emitted)
        if name == "changed_run_status":
            changed[0][0]["left_status"] = "MUTATED"
        elif name == "missing_contradiction_block":
            changed[1].pop()
        elif name == "changed_paragraph_flag":
            changed[1][0]["lines"][0]["paragraph_start"] = "MUTATED"
        else:
            changed[2]["summary"][0]["occurrences"] += 1
        try:
            compare_outputs(rows, *changed, blocks, runs, summary)
        except AssertionError:
            tests.append(name + "_rejected")
        else:
            raise AssertionError("Artifact mutation accepted: " + name)
    return {"experiment_id": "GDT1047", "status": "PASS",
            "implementation_independence": "Separate validator author; runner source neither read nor imported.",
            "semantic_confirmation": False, "source_guard_replay": replay,
            "coverage": {"projection_groups": len(rows), "reconstructed_P_blocks": len(blocks),
                         "runs": len(runs), "contradiction_blocks": len(published_blocks),
                         "summary_cells": len(result["summary"]), "directional_decisions": len(result["decisions"])},
            "scope": {"current": len(allow), "old_overlap": len(old & allow),
                      "additional": len(allow - old), "old_not_admitted": sorted(old - allow)},
            "synthetic_and_mutation_checks": tests,
            "artifact_sha256": {name: digest(HERE / "artifacts" / name) for name in artifact_names},
            "prereg_lock_sha256": digest(lock_path), "scope_addendum_lock_sha256": digest(scope_lock_path),
            "validator_sha256": digest(Path(__file__)),
            "limitation": "Verifies guarded source bookkeeping and fixed host-condition consequences; no native boundary authentication or meaning confirmation."}


if __name__ == "__main__":
    raise SystemExit(main())
