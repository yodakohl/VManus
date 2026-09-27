#!/usr/bin/env python3
"""Independent GDT1048 capacity validator; no runner import or semantic scoring."""
from __future__ import annotations

import argparse
import collections
import copy
import csv
import hashlib
import io
import json
import subprocess
from datetime import datetime
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parents[1]
TARGET_ID = "f111r|f111r.48-f111r.50"
READERS = ("ZL3b", "IT2a")
COLS = ["source_group_id", "edition", "page", "locus", "source_group_index",
        "ivtff_group_raw", "paragraph_start", "paragraph_end", "left_separator", "right_separator"]
PARENT = "research_registry/proposals/raw_vitruvius_ix89_complete_continuation_20260921.json"
PROPOSAL = "research_registry/proposals/raw_f111r_preceding_clock_seasonal_setting_whole_20260922.json"
SOURCE = "research_registry/proposals/raw_vitruvius_ix88_frozen_extension_20260922.json"
CACHE = "experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(target: dict, positions: list[dict], lexicon: list[dict], source: dict,
            result: dict, expected_target: dict, parent: dict, expected_source: dict,
            raw: dict, cap: int) -> list[dict]:
    assert target == expected_target, "Complete cached targets, flags or uncertainty changed"
    assert lexicon == parent["lexicon"], "Frozen lexical object changed"
    assert len(lexicon) == 33 and len({x["form"] for x in lexicon}) == 33
    assert source == expected_source, "Complete source10 object changed"
    source_hash = hashlib.sha256(source["complete_text"].encode("utf-8")).hexdigest()
    assert source_hash == source["utf8_sha256"] == result["source10_sha256"]
    meanings = {x["form"]: x for x in parent["lexicon"]}
    expected_positions = []
    expected_summary = []
    for edition in READERS:
        record = expected_target[edition]
        assert record["id"] == TARGET_ID and record["page"] == "f111r" and record["leaf"] == 111
        assert record["lines"][0]["start"] is True and record["lines"][-1]["end"] is True
        assert [line["locus"] for line in record["lines"]] == ["f111r.48", "f111r.49", "f111r.50"]
        words = []
        for line in record["lines"]:
            assert line["offset"] == len(words)
            assert len(line["words"]) == len(line["source_ids"])
            for number, (word, gid) in enumerate(zip(line["words"], line["source_ids"]), 1):
                source_row = raw[gid]
                assert source_row["edition"] == edition and source_row["page"] == "f111r"
                assert source_row["locus"] == line["locus"]
                assert int(source_row["source_group_index"]) == number
                assert source_row["ivtff_group_raw"] == word, "Raw spelling or segmentation changed"
                assert source_row["paragraph_start"] == str(int(line["start"]))
                assert source_row["paragraph_end"] == str(int(line["end"]))
                words.append(word)
                entry = meanings.get(word)
                expected_positions.append({"edition": edition, "position": len(words),
                    "source_group_id": gid, "locus": line["locus"], "raw": word,
                    "paragraph_start": line["start"], "paragraph_end": line["end"],
                    "left_separator": source_row["left_separator"],
                    "right_separator": source_row["right_separator"],
                    "fixed_value": entry["value"] if entry else None,
                    "fixed_type": entry["type"] if entry else None,
                    "status": "FROZEN_OLD_VALUE_UNBOUND_IN_NEW_SOURCE" if entry else "UNASSIGNED_NEW_TYPE"})
        assert len(words) == record["groups"]
        old_types = set(words) & meanings.keys()
        new_types = set(words) - meanings.keys()
        old_positions = sum(word in meanings for word in words)
        assert len(new_types) > cap, "This validator's capacity-stop outcome no longer follows"
        expected_summary.append({"edition": edition, "groups": len(words), "types": len(set(words)),
            "old_types": sorted(old_types), "old_positions": old_positions,
            "new_types": sorted(new_types), "new_type_count": len(new_types),
            "new_positions": len(words) - old_positions, "new_value_cap": cap,
            "excess": len(new_types) - cap, "verdict": "FIXED_LEXICAL_CAPACITY_EXCEEDED"})
    assert positions == expected_positions, "Every exact source position must appear once and unchanged"
    assert len({x["source_group_id"] for x in positions}) == len(positions) == 63
    selected_raw_ids = {gid for gid, row in raw.items() if row["edition"] in READERS
                        and row["locus"] in {"f111r.48", "f111r.49", "f111r.50"}}
    assert selected_raw_ids == {x["source_group_id"] for x in positions}, "Whole guarded-unit coverage"
    assert result["summary"] == expected_summary, "All lexical counts and lists must be independently derived"
    assert result["status"] == "FIXED_LEXICAL_CAPACITY_EXCEEDED_BOTH_READERS"
    assert result["RF1b"] == "NO_MATCHING_SOURCE_MARKED_WHOLE_PARAGRAPH"
    assert result["target"] == TARGET_ID
    for key in ("new_values_authored", "new_productions", "new_bindings", "source_obligations_completed",
                "confirmed_words", "independent_confirmation_capacity"):
        assert result[key] == 0, ("capacity-only claim ceiling", key)
    assert result["semantic_execution"] is False and result["new_access"] is False
    assert result["prior_exposure"] is True
    return expected_summary


def verify_parent_profiles(parent: dict) -> dict:
    """Recount existing descriptive profiles, using only an admitted projection."""
    previous = ROOT / "experiments/yolo/gdt1047_bare_value_left_host"
    prior_result_path = previous / "artifacts/RESULT.json"
    prior_result = load(prior_result_path)
    projection = previous / "runtime/PROJECTION.tsv"
    assert sha(projection) == prior_result["guarded_query"]["projection_sha256"], "Prior guarded projection hash"
    profiles_path = HERE / "src/PARENT_PRIOR_PROFILES.json"
    profiles = load(profiles_path)["profiles"]
    meanings = {entry["form"]: entry for entry in parent["lexicon"]}
    assert len(profiles) == len(meanings) == 33
    assert {entry["form"] for entry in profiles} == set(meanings)
    by_reader = collections.defaultdict(list)
    with projection.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            assert not row["page"].startswith("f84") and row["page"] != "f116v"
            by_reader[row["edition"]].append(row)
    assert sum(map(len, by_reader.values())) == prior_result["guarded_query"]["stats"]["selected"] == 96184
    checked = 0
    for edition, rows in by_reader.items():
        frequency = collections.Counter(row["ivtff_group_raw"] for row in rows)
        kind_totals = collections.Counter(row["kind"] for row in rows)
        page_count = len({row["page"] for row in rows})
        assert page_count == 179
        for profile in profiles:
            form = profile["form"]
            assert profile["hypothesis_value"] == meanings[form]["value"]
            assert profile["hypothesis_type"] == meanings[form]["type"]
            observed = profile["readers"][edition]
            hits = [row for row in rows if row["ivtff_group_raw"] == form]
            count = len(hits)
            rank = 1 + sum(total > count for total in frequency.values()) if count else None
            assert observed["count"] == count, ("profile count", form, edition)
            assert observed["rank"] == rank, ("profile rank", form, edition)
            assert observed["pages_with_form"] == len({row["page"] for row in hits})
            assert observed["pages_total"] == page_count
            positions = dict.fromkeys(("start", "middle", "end", "single"), 0)
            lines = collections.defaultdict(list)
            kind_counts = collections.Counter()
            for row in hits:
                index, length = int(row["source_group_index"]), int(row["source_group_count"])
                position = "single" if length == 1 else "start" if index == 1 else "end" if index == length else "middle"
                positions[position] += 1
                lines[(row["page"], row["locus"])].append(index)
                kind_counts[row["kind"]] += 1
            assert observed["positions"] == positions, ("profile positions", form, edition)
            repetitions = {"lines_with_form": len(lines),
                          "repeated_lines": sum(len(indices) > 1 for indices in lines.values()),
                          "adjacent_pairs": sum(sum(b == a + 1 for a, b in zip(sorted(indices), sorted(indices)[1:])) for indices in lines.values()),
                          "max_per_line": max(map(len, lines.values()), default=0)}
            assert observed["repetition"] == repetitions, ("profile repetition", form, edition)
            expected_kind = [{"value": kind, "count": kind_counts[kind], "total_groups": kind_totals[kind]}
                             for kind in sorted(kind_totals)]
            assert observed["strata"]["kind"] == expected_kind, ("profile kind strata", form, edition)
            checked += 1
    assert checked == 99
    return {"profile_reader_cells": checked, "profiles": len(profiles),
            "verified_fields": ["count", "rank", "pages_with_form", "pages_total", "positions", "repetition", "strata.kind", "hypothesis_value", "hypothesis_type"],
            "not_reverified": ["strata.section", "strata.currier", "strata.hand"],
            "reason_for_limit": "Those metadata fields are absent from the existing GDT1047 projection; no broader source query was made.",
            "profiles_sha256": sha(profiles_path), "projection_sha256": sha(projection),
            "projection_receipt_sha256": sha(prior_result_path),
            "meaning": "Independent descriptive recount, not a likelihood or semantic prior calibration."}


def validate() -> dict:
    lock_path = HERE / "src/PREREG_LOCK.json"
    lock = load(lock_path)
    for item in lock["fixed_files"] + lock["inputs"]:
        assert sha(ROOT / item["path"]) == item["sha256"], ("Registered input changed", item["path"])
    assert (datetime.fromisoformat(lock["deadline_utc"]) - datetime.fromisoformat(lock["registered_utc"])).total_seconds() == 2700
    proposal = load(ROOT / PROPOSAL)
    assert proposal["design"]["target"]["id"] == TARGET_ID
    cap = proposal["design"]["costs"]["new_exact_whole_values_max"]
    assert cap == 18 and proposal["design"]["costs"]["aliases_or_packing"] == 0
    parent = load(ROOT / PARENT)
    expected_source = load(ROOT / SOURCE)["source_only_future_options"][0]
    assert expected_source["unit"] == "IX.8.10"
    assert expected_source["utf8_sha256"] == proposal["design"]["whole_owned_source"]["sha256_utf8"]
    cached = load(ROOT / CACHE)
    expected_target = {}
    for edition in READERS:
        matches = [r for r in cached[edition] if r["id"] == TARGET_ID]
        assert len(matches) == 1, "Exactly one complete cached unit per reader"
        expected_target[edition] = matches[0]
    assert not any(r["id"] == TARGET_ID for r in cached["RF1b"])
    allow_path = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
    with allow_path.open(encoding="utf-8", newline="") as f:
        allowed = {r["page"] for r in csv.DictReader(f, delimiter="\t")}
    assert "f111r" in allowed
    command = ["./vmanus-exp", "query-tsv",
        "experiments/semantic_assumptions/results/source_separator_transcription.tsv",
        "--selector", "page", "--allow", "f111r", "--columns", ",".join(COLS),
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    guarded = subprocess.run(command, cwd=ROOT, capture_output=True, check=True)
    raw_rows = list(csv.DictReader(io.StringIO(guarded.stdout.decode("utf-8")), delimiter="\t"))
    assert all(r["page"] == "f111r" for r in raw_rows)
    raw = {r["source_group_id"]: r for r in raw_rows}
    assert len(raw) == len(raw_rows), "Duplicate guarded source IDs"
    names = ["TARGET.json", "ALL_POSITIONS.json", "FROZEN_LEXICON.json", "SOURCE10.json", "RESULT.json"]
    emitted = [load(HERE / "artifacts" / name) for name in names]
    result = emitted[-1]
    assert result["registration"] == lock["registered_utc"] and result["deadline"] == lock["deadline_utc"]
    assert result["prereg_sha256"] == sha(lock_path)
    receipt = result["guard_replay"]
    assert receipt["command"] == command
    assert receipt["source_sha256"] == sha(ROOT / command[2])
    assert receipt["projection_sha256"] == hashlib.sha256(guarded.stdout).hexdigest()
    assert receipt["stats"] == guarded.stderr.decode("utf-8").strip()
    expected_summary = compare(*emitted, expected_target, parent, expected_source, raw, cap)
    prior_profile_validation = verify_parent_profiles(parent)
    mutations = []
    for name in ("missing_position", "collapsed_new_type", "changed_old_value", "normalized_uncertain_form"):
        damaged = copy.deepcopy(emitted)
        if name == "missing_position":
            damaged[1].pop()
        elif name == "collapsed_new_type":
            row = damaged[-1]["summary"][0]
            row["new_types"].pop()
            row["new_type_count"] -= 1
            row["excess"] -= 1
        elif name == "changed_old_value":
            damaged[2][0]["denotation"] = "MUTATED"
        else:
            damaged[0]["ZL3b"]["lines"][-1]["words"][7] = "keel"
        try:
            compare(*damaged, expected_target, parent, expected_source, raw, cap)
        except AssertionError:
            mutations.append(name + "_rejected")
        else:
            raise AssertionError("Mutation accepted: " + name)
    return {"experiment_id": "GDT1048", "status": "PASS", "semantic_confirmation": False,
        "independence": "Separate validator author; no runner source read or imported.",
        "coverage": {"complete_units": len(expected_target), "target_positions": 63,
                     "unchanged_lexical_objects": len(parent["lexicon"]), "guarded_f111r_rows": len(raw_rows)},
        "summary": expected_summary,
        "alternate_reading_limits": {"RF1b": "No matching whole cached unit",
            "ZL3b_uncertain_whole": "k[ee:ei]l preserved; not collapsed to IT2a keel",
            "segmentation": "ZL3b l + chedy remains distinct from IT2a lchedy",
            "anchor_eligibility": "All original per-line eligibility flags retained without promotion"},
        "mutation_checks": mutations,
        "parent_prior_profile_validation": prior_profile_validation,
        "source10_sha256": expected_source["utf8_sha256"],
        "guarded_projection_sha256": hashlib.sha256(guarded.stdout).hexdigest(),
        "registered_lock_sha256": sha(lock_path),
        "artifact_sha256": {name: sha(HERE / "artifacts" / name) for name in names},
        "validator_sha256": sha(Path(__file__)),
        "ceiling": "Verifies lexical development capacity only; no semantic execution, historical translation or global clock rejection."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Do not rewrite VALIDATION.json")
    args = parser.parse_args()
    try:
        result = validate()
    except (AssertionError, KeyError, ValueError, OSError, subprocess.CalledProcessError) as error:
        result = {"experiment_id": "GDT1048", "status": "FAIL",
                  "error": f"{type(error).__name__}: {error}", "semantic_confirmation": False}
    if not args.check:
        (HERE / "artifacts/VALIDATION.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
