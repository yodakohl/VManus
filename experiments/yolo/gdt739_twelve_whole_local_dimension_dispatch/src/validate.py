#!/usr/bin/env python3
"""Independent geometry, dispatch, scope, and replay audit for GDT739."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch")
EXP = ROOT / BASE
DEFAULT_ART = EXP / "artifacts"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
RUN = EXP / "src/run.py"
PATCH = ROOT / "experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication/artifacts/OCCURRENCE_RENDERER_PATCH.tsv"
OCC = ROOT / "experiments/yolo/gdt737_held_body_record_role_transfer/artifacts/HELD_811_OCCURRENCE_CONTEXTS.tsv"
STATUS = (
    "PARTIAL__202_HOST_FIRST_OCCURRENCE_DISPATCHES__FORM_CLASS_AND_LEVEL_CORE__"
    "RADIUS_TWO_AXIS_OR_CARRIER_BINDING__RADIUS_THREE_TO_FIVE_DISCOVERY_ONLY__"
    "CHEEDY_SHEEDY_RESULT_DEFAULT_DOWNGRADED__EIGHT_LOCAL_RESULT_OVERRIDES__"
    "ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "WINDOW_202_TOKEN_AUDIT.tsv", "DIMENSION_202_DISPATCH.tsv", "FORM_12_DISPATCH_PROFILE.tsv",
    "REPRESENTATIVE_PASSAGES.tsv", "GDT739_LOCAL_DIMENSION_READER.md", "RESULT.json",
)
SCALAR_FORMS = {"lain", "lkaiin", "lkain", "lkar", "rain", "sain", "skaiin"}
STATE_FORMS = {"lcheedy", "lcheol", "lsheedy", "pcheol", "rsheedy"}
RETIRED = ("pulver", "samen", "saat", "wurzel", "holz")
CARRIER_AXES = ("PREPARATION", "MATERIAL", "PART")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def integer(row: dict[str, str], field: str) -> int:
    return int(row[field])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def require(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT739", "manifest experiment id")
    check(manifest["slug"] == "twelve_whole_local_dimension_dispatch", "manifest slug")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors forbidden")
    placeholder = (
        manifest["status"] == "REGISTERED_UNSCORED" and manifest["inputs"] == []
        and manifest["outputs"] == [] and manifest["validation"] == {"artifact": None, "status": "NOT_RUN"}
    )
    if placeholder:
        check(True, "manifest placeholder accepted before sealing")
    else:
        check(manifest["status"] == STATUS, "manifest status")
        check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "manifest validation contract")
        check(bool(manifest["inputs"]) and bool(manifest["outputs"]), "sealed manifest has bindings")
        for binding in manifest["inputs"]:
            path = ROOT / binding["path"]
            require(not Path(binding["path"]).is_absolute(), f"absolute input: {binding['path']}")
            require(path.is_file() and sha256(path) == binding["sha256"], f"input binding mismatch: {binding['path']}")
        check(True, "all manifest inputs exist and hash-match")
        expected_outputs = {str(BASE / "artifacts" / name) for name in GENERATED} | {str(VALIDATION_REL)}
        check(expected_outputs <= {binding["path"] for binding in manifest["outputs"]}, "manifest binds all generated outputs")
        for binding in manifest["outputs"]:
            if binding["path"] == str(VALIDATION_REL):
                continue
            path = ROOT / binding["path"]
            require(path.is_file() and sha256(path) == binding["sha256"], f"output binding mismatch: {binding['path']}")
        check(True, "all non-validation outputs hash-match")

    check(art.is_dir(), "artifact directory exists")
    check(all((art / name).is_file() for name in GENERATED), "all generated artifacts exist")
    patches = read_tsv(PATCH)
    occurrences = read_tsv(OCC)
    occ_map = {row["occurrence_id"]: row for row in occurrences}
    check(len(patches) == 202 and len({row["patch_id"] for row in patches}) == 202, "source has 202 unique patches")
    check(Counter(row["surface"] in SCALAR_FORMS for row in patches) == Counter({True: 172, False: 30}), "source partitions 172 scalar and 30 state")
    check(not any(row["page"].startswith("f84") for row in patches), "source excludes sealed pages")

    windows = read_tsv(art / "WINDOW_202_TOKEN_AUDIT.tsv")
    check(len(windows) == 1373 and len({row["window_id"] for row in windows}) == 1373, "1373 unique radius-five neighbor rows")
    check(set(row["patch_id"] for row in windows) == {row["patch_id"] for row in patches}, "all target patches have a window")
    window_by_patch: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in windows:
        window_by_patch[row["patch_id"]].append(row)
        require(1 <= integer(row, "distance") <= 5, f"window radius: {row['window_id']}")
        require(abs(integer(row, "signed_offset")) == integer(row, "distance"), f"signed distance: {row['window_id']}")
        require((row["side"] == "L") == (integer(row, "signed_offset") < 0), f"window side: {row['window_id']}")
        require(integer(row, "neighbor_ordinal") == integer(row, "target_ordinal") + integer(row, "signed_offset"), f"window ordinal: {row['window_id']}")
        if row["eligible_local_anchor"] == "1":
            require(row["neighbor_reader_exact"] == "1", f"eligible exact: {row['window_id']}")
            require(row["neighbor_unknown_v99r7"] == "0", f"eligible known: {row['window_id']}")
            require(row["neighbor_confidence_level"].startswith(("W2", "W3")), f"eligible W2/W3: {row['window_id']}")
            require(row["neighbor_composition_semantic_credit"] == "0", f"eligible zero composition: {row['window_id']}")
            require(row["strict_initial_head_neighbor"] == row["another_gdt738_target"] == "0", f"eligible non-head and non-target: {row['window_id']}")
            require(row["retired_patient_words"] == "NONE" and row["axis_tags"] != "NONE", f"eligible semantic filters: {row['window_id']}")
        require(row["head_or_body_lexeme_credit"] == row["component_export_credit"] == "0", f"window export zero: {row['window_id']}")
    check(True, "all window geometry and eligibility fields are coherent")
    check(sum(row["eligible_local_anchor"] == "1" for row in windows) == 230, "230 eligible radius-five contacts")
    radius_counts = {
        radius: sum(any(item["eligible_local_anchor"] == "1" and integer(item, "distance") <= radius for item in rows) for rows in window_by_patch.values())
        for radius in (1, 2, 3, 5)
    }
    check(radius_counts == {1: 62, 2: 98, 3: 121, 5: 146}, "anchor target footprints are 62/98/121/146")

    dispatches = read_tsv(art / "DIMENSION_202_DISPATCH.tsv")
    check(len(dispatches) == 202 and len({row["dispatch_id"] for row in dispatches}) == 202, "202 unique dispatch rows")
    check({row["patch_id"] for row in dispatches} == {row["patch_id"] for row in patches}, "one dispatch per source patch")
    patch_map = {row["patch_id"]: row for row in patches}
    for row in dispatches:
        source = patch_map[row["patch_id"]]
        occurrence = occ_map[row["occurrence_id"]]
        require(all(row[field] == source[field] for field in ("occurrence_id", "page", "locus", "token_index", "surface", "body", "opaque_head_id", "line_position")), f"dispatch provenance: {row['dispatch_id']}")
        require(row["token_ordinal"] == occurrence["token_ordinal"], f"dispatch ordinal: {row['dispatch_id']}")
        require(row["scope"] == "EXACT_COMPLETE_SURFACE_AT_THIS_ENUMERATED_OCCURRENCE", f"dispatch scope: {row['dispatch_id']}")
        require(all(row[field] == "0" for field in (
            "literal_patient_or_species_claimed", "literal_plaintext_claimed", "unconditional_global_export",
            "head_or_body_lexeme_credit", "component_export_credit", "unseen_form_export",
        )), f"dispatch export zero: {row['dispatch_id']}")
        require(not any(word in row["gdt739_working_render_de"].lower() for word in RETIRED), f"retired patient in render: {row['dispatch_id']}")
    check(True, "all dispatch rows preserve source, scope and zero exports")

    for row in dispatches:
        if row["surface"] not in SCALAR_FORMS:
            continue
        selected = None
        for distance in (1, 2):
            classes = sorted({
                value for item in window_by_patch[row["patch_id"]]
                if item["eligible_local_anchor"] == "1" and integer(item, "distance") == distance
                for value in item["scalar_host_types"].split("|") if value != "NONE"
            })
            if classes:
                selected = classes[0] if len(classes) == 1 else "OPEN_SCALAR_CONFLICT"
                break
        expected = selected or "OPEN_SCALAR"
        require(row["dimension_dispatch"] == expected, f"scalar nearest-unanimous-ring rule: {row['dispatch_id']}")
    check(True, "all 172 scalar rows independently follow the nearest unanimous ring")
    scalar_counts = Counter(row["dimension_dispatch"] for row in dispatches if row["surface"] in SCALAR_FORMS)
    check(scalar_counts == Counter({
        "OPEN_SCALAR": 106, "QUALITY_DEGREE": 43, "AMOUNT_DOSE": 15,
        "PROCESS_PASS": 5, "OPEN_SCALAR_CONFLICT": 3,
    }), "scalar dispatch is 43 quality, 15 amount, 5 passage, 109 open/conflict")

    state_rows = [row for row in dispatches if row["surface"] in STATE_FORMS]
    check(Counter(row["state_mode"] for row in state_rows) == Counter({"QUALITY_STATE": 22, "PROCESS_RESULT": 8}), "state mode is 22 descriptive and 8 result")
    check(sum(row["state_mode_evidence_tier"] == "STRONG_LOCAL_W23" for row in state_rows) == 2, "two strong local result overrides")
    check(sum(row["state_mode_evidence_tier"] == "ENDPOINT_BEST_FIT" for row in state_rows) == 6, "six endpoint best-fit result overrides")
    check(sum(row["favored_axis_locally_supported"] == "1" for row in state_rows) == 6, "six state occurrences have local favored-axis support")
    check(Counter((row["surface"], row["favored_axis_locally_supported"]) for row in state_rows) == Counter({
        ("pcheol", "0"): 8, ("pcheol", "1"): 2, ("lcheol", "0"): 5, ("lcheol", "1"): 3,
        ("lcheedy", "0"): 6, ("lsheedy", "0"): 4, ("rsheedy", "0"): 1, ("rsheedy", "1"): 1,
    }), "favored dry/moist support stays occurrence-local")

    carrier_counts = Counter(row["carrier_dispatch"] for row in dispatches)
    check(carrier_counts == Counter({
        "OPEN": 129, "PREPARATION": 29, "MATERIAL": 27, "PREPARATION_MATERIAL": 6,
        "MATERIAL_PART": 5, "PART": 2, "PREPARATION_PART": 2,
        "PREPARATION_MATERIAL_PART": 2,
    }), "carrier classes match nearest eligible broad hosts")
    for row in dispatches:
        distances: dict[str, int] = {}
        for axis in CARRIER_AXES:
            found = [
                integer(item, "distance") for item in window_by_patch[row["patch_id"]]
                if item["eligible_local_anchor"] == "1" and integer(item, "distance") <= 2
                and axis in item["axis_tags"].split("|")
            ]
            if found:
                distances[axis] = min(found)
        if not distances:
            expected = "OPEN"
        else:
            nearest = min(distances.values())
            expected = "_".join(axis for axis in CARRIER_AXES if distances.get(axis) == nearest)
        require(row["carrier_dispatch"] == expected, f"carrier nearest-ring rule: {row['dispatch_id']}")
    check(True, "all carrier dispatches independently follow the nearest ring")

    profiles = read_tsv(art / "FORM_12_DISPATCH_PROFILE.tsv")
    check(len(profiles) == len({row["surface"] for row in profiles}) == 12, "twelve unique form profiles")
    check(sum(integer(row, "patched_occurrences") for row in profiles) == 202, "profile occurrences sum to 202")
    check(sum(integer(row, "axis_specific_dispatches") for row in profiles) == 69, "profile axis-specific sum is 69")
    check(sum(integer(row, "carrier_bound_dispatches") for row in profiles) == 73, "profile carrier-bound sum is 73")
    check(sum(integer(row, "fully_open_dispatches") for row in profiles) == 107, "profile fully-open sum is 107")

    passages = read_tsv(art / "REPRESENTATIVE_PASSAGES.tsv")
    check(len(passages) == len({row["passage_id"] for row in passages}) == 20, "twenty unique representative passages")
    check(sum(len(row["focal_surfaces"].split("|")) for row in passages) == 23, "representative lines contain 23 focal patches")
    check(set(surface for row in passages for surface in row["focal_surfaces"].split("|")) == SCALAR_FORMS | STATE_FORMS, "representatives cover all twelve forms")
    check(all("Drogenholz" not in row["gdt739_safe_line_render_de"] and "Holzdroge" not in row["gdt739_safe_line_render_de"] for row in passages), "safe reader removes old literal wood patients")
    reader = (art / "GDT739_LOCAL_DIMENSION_READER.md").read_text(encoding="utf-8")
    check(all(row["passage_id"] in reader for row in passages), "markdown reader contains every representative passage")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT739_TWELVE_WHOLE_LOCAL_DIMENSION_DISPATCH_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["inherited_allowlist_pages"] == 179 and result["scope"]["new_pages_used"] == 0, "result preserves inherited scope and uses no new pages")
    check(result["scope"]["f84_used"] is False and result["scope"]["f84r_used"] is False, "result excludes sealed selectors")
    check(result["target"] == {"licensed_complete_forms": 12, "position_scoped_occurrences": 202, "scalar_occurrences": 172, "state_occurrences": 30}, "result target geometry")
    check(result["dispatch"]["scalar_classes"] == dict(sorted(scalar_counts.items())), "result scalar counts")
    check(result["dispatch"]["carrier_bound_occurrences"] == 73 and result["dispatch"]["fully_open_occurrences"] == 107, "result carrier and open counts")
    check(all(value == 0 for value in result["claims"].values()), "result claim ceiling remains zero")
    for name in GENERATED[:-1]:
        rel = str(BASE / "artifacts" / name)
        require(result["artifact_hashes"][rel] == sha256(art / name), f"result artifact hash: {name}")
    check(True, "result artifact hashes match")

    with tempfile.TemporaryDirectory(prefix="gdt739-replay-") as tmp:
        replay = Path(tmp)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)], cwd=ROOT,
            check=True, capture_output=True, text=True,
        )
        require(completed.returncode == 0, "builder replay command")
        for name in GENERATED:
            require((replay / name).is_file(), f"replay output missing: {name}")
            require(sha256(replay / name) == sha256(art / name), f"replay byte identity: {name}")
    check(True, "builder replay is byte-identical for all generated artifacts")

    payload = {
        "schema": "GDT739_VALIDATION_V1", "status": "PASS", "checks_passed": len(checks),
        "checks": checks, "source_hashes": {str(PATCH.relative_to(ROOT)): sha256(PATCH), str(OCC.relative_to(ROOT)): sha256(OCC)},
        "artifact_hashes": {name: sha256(art / name) for name in GENERATED},
        "builder_replay": "BYTE_IDENTICAL", "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps({"status": "PASS", "checks_passed": len(checks), "builder_replay": "BYTE_IDENTICAL"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
