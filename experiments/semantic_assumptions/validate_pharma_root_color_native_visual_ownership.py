#!/usr/bin/env python3
"""Validate source/image bindings and arithmetic for the native-visual audit.

The manual native-visual grades are observations, not something this source
validator can infer.  This validator independently checks that every held row
is represented once, that no label string enters the artifact, that eligibility
and all gates follow exactly from the frozen grades, and that the official Yale
bytes match their registered hashes.
"""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "public_pharma_root_color_candidates.tsv"
SOURCE_RESULT = RESULTS / "public_pharma_root_color_capacity.json"
PRODUCTION_TSV = RESULTS / "pharma_root_color_native_visual_ownership.tsv"
PRODUCTION_JSON = RESULTS / "pharma_root_color_native_visual_ownership.json"
PRODUCTION_REPORT = RESULTS / "pharma_root_color_native_visual_ownership_report.md"
OUT_JSON = RESULTS / "pharma_root_color_native_visual_ownership_validation.json"
OUT_REPORT = RESULTS / "pharma_root_color_native_visual_ownership_validation.md"

EXPECTED = {
    SOURCE: "092bdfcbbf17c78da2ebd00576921a464f61cfd50bc08ee070da8def444860ec",
    SOURCE_RESULT: "0cc6bf6b675a45c86b841d971be65c4c348f1eb789bfcec61d59b52bbc3d9909",
    PRODUCTION_TSV: "eb1b5563fa0d775a662f27b566d9c1acd75eba59fdf690e3fc8ac9ab9e225a7b",
    PRODUCTION_JSON: "e1172bfa547ddd36b21cd411402cc7bd924d382cd9a4bd3db9e0e19def3908be",
}

MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"

EXPECTED_IMAGES = {
    "1006233": ("88v and 89r", 9078, 3777, "3b553c70d0c068cb39a276d391127165c5d9d868ec08e7f5eb2e73b32bb95d1e"),
    "1006234": ("89v (part)", 4204, 3809, "b6b0dd8ba7cd316f3b09a8b156d1eed0eb36ad8ec9086b975969f4f8f7dd5406"),
    "1006235": ("89v (part) and 90r", 7796, 3761, "6aaa777945f288a8ba206921709292eaaf4ea972f9a0bb59cdf3040aaed3e15a"),
    "1006246": ("99r", 2702, 3765, "f17eba5496a1b1d92f589c33ee9be256a379ec8d2bba3da1ebe2ff5a2e3e2901"),
    "1006247": ("99v", 2802, 3697, "111f6dfc34b8ecb9230cb5a0d144afef4cbd788048ddda2f440108941c91d5e5"),
    "1006248": ("100r", 2676, 3756, "6dcf72a0d7eac14da2232987c9cc1521e6d70c9f0f92d3eb39b55fc075520429"),
    "1006249": ("100v and 101r", 7486, 3715, "72637b9770f40f7a8ff6b96a551e64775e88994ae69bafec0b43d48974364c33"),
    "1006250": ("101v (part)", 2698, 3779, "1122f1b13afdf1509402334816f95e5e9baa2b6c94aa9e347b04aa2e4e54f36b"),
    "1006251": ("101v (part) and 102r", 8176, 3864, "30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94"),
    "1006252": ("102v (part)", 2981, 3795, "8cdb1030d805b968932146124915cb0d86f7abf853167ffec028b59599820fad"),
}

CLEAR = "CLEAR_ONE_FRAGMENT_ONE_LABEL_CELL"
AMBIGUOUS = "AMBIGUOUS_NEAREST_NEIGHBOUR"
UNRESOLVED = "SOURCE_LOCATION_UNRESOLVED"
ALLOWED_GRADES = {CLEAR, AMBIGUOUS, UNRESOLVED, "NO_VISIBLE_CURRENT_LABEL"}
OUTPUT_FIELDS = {
    "source_record_id", "source_page", "physical_folio", "source_location",
    "root_state", "mapped_locus", "canvas_id", "canvas_label", "image_sha256",
    "visual_grade", "visual_basis", "eligible", "exclusion_reason",
}


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-validator/1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        if response.status != 200 or response.geturl() != url:
            raise AssertionError((response.status, response.geturl(), url))
        return response.read()


def check(condition: bool, name: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing overwrite of validation outputs")
    checks: list[str] = []
    for path, expected in EXPECTED.items():
        check(sha(path) == expected, f"hash_{path.name}", checks)

    manifest_bytes = fetch(MANIFEST_URL)
    check(sha_bytes(manifest_bytes) == MANIFEST_SHA, "live_yale_manifest_hash", checks)
    manifest = json.loads(manifest_bytes)
    canvases = {}
    for canvas in manifest["items"]:
        canvas_id = canvas["id"].rsplit("/", 1)[-1]
        if canvas_id in EXPECTED_IMAGES:
            canvases[canvas_id] = canvas
    check(set(canvases) == set(EXPECTED_IMAGES), "manifest_canvas_inventory", checks)

    for canvas_id, (label, width, height, expected_sha) in EXPECTED_IMAGES.items():
        canvas = canvases[canvas_id]
        check(canvas["label"]["none"] == [label], f"manifest_label_{canvas_id}", checks)
        check((canvas["width"], canvas["height"]) == (width, height), f"manifest_dimensions_{canvas_id}", checks)
        url = f"https://collections.library.yale.edu/iiif/2/{canvas_id}/full/full/0/default.jpg"
        check(sha_bytes(fetch(url)) == expected_sha, f"live_image_hash_{canvas_id}", checks)

    source = read_tsv(SOURCE)
    source_by_id = {row["source_record_id"]: row for row in source}
    held = [
        row for row in source
        if row["primary_current_mapping"] == "1" and row["physical_folio"] != "f88"
    ]
    check(len(held) == 48, "held_source_count", checks)
    check(len(source_by_id) == len(source), "source_ids_unique", checks)

    rows = read_tsv(PRODUCTION_TSV)
    check(len(rows) == 48, "audit_row_count", checks)
    check(set(rows[0]) == OUTPUT_FIELDS, "audit_schema", checks)
    check(len({row["source_record_id"] for row in rows}) == 48, "audit_ids_unique", checks)
    check({row["source_record_id"] for row in rows} == {row["source_record_id"] for row in held}, "exact_held_id_set", checks)

    for row in rows:
        original = source_by_id[row["source_record_id"]]
        check(
            tuple(row[key] for key in ("source_page", "physical_folio", "source_location", "root_state", "mapped_locus"))
            == tuple(original[key] for key in ("source_page", "physical_folio", "source_location", "root_state", "mapped_locus")),
            f"source_projection_{row['source_record_id']}", checks,
        )
        check(row["visual_grade"] in ALLOWED_GRADES, f"grade_{row['source_record_id']}", checks)
        canvas = row["canvas_id"]
        check(canvas in EXPECTED_IMAGES, f"canvas_{row['source_record_id']}", checks)
        check(
            (row["canvas_label"], row["image_sha256"])
            == (EXPECTED_IMAGES[canvas][0], EXPECTED_IMAGES[canvas][3]),
            f"image_binding_{row['source_record_id']}", checks,
        )
        conflict = original["state_comparison"] == "CONFLICT"
        expected_eligible = row["visual_grade"] == CLEAR and not conflict
        check((row["eligible"] == "1") == expected_eligible, f"eligibility_{row['source_record_id']}", checks)
        expected_exclusion = "NONE" if expected_eligible else "CROSS_DESCRIPTION_ROOT_STATE_CONFLICT" if conflict else row["visual_grade"]
        check(row["exclusion_reason"] == expected_exclusion, f"exclusion_{row['source_record_id']}", checks)

    grades = Counter(row["visual_grade"] for row in rows)
    eligible = [row for row in rows if row["eligible"] == "1"]
    states = Counter(row["root_state"] for row in eligible)
    by_folio = Counter(row["physical_folio"] for row in eligible)
    folios_by_state = {
        state: sorted({row["physical_folio"] for row in eligible if row["root_state"] == state})
        for state in ("DARK", "LIGHT")
    }
    check(grades == {CLEAR: 22, UNRESOLVED: 25, AMBIGUOUS: 1}, "grade_counts", checks)
    check(states == {"LIGHT": 15, "DARK": 6}, "eligible_state_counts", checks)
    check(by_folio == {"f89": 11, "f100": 8, "f102": 2}, "eligible_folio_counts", checks)
    check(folios_by_state == {"DARK": ["f100", "f102", "f89"], "LIGHT": ["f100", "f89"]}, "state_folios", checks)
    max_share = max(by_folio.values()) / len(eligible)
    check(max_share == 11 / 21 and max_share <= 0.60, "maximum_folio_share", checks)

    production = json.loads(PRODUCTION_JSON.read_text(encoding="utf-8"))
    check(production["status"] == "PASS_NATIVE_VISUAL_OWNERSHIP_CAPACITY", "production_status", checks)
    check(production["decision"] == "AUTHORIZE_SEPARATE_TEXT_PREREGISTRATION_ONLY_KEEP_LABELS_SEALED", "production_decision", checks)
    check(production["held_panel"]["eligible_clear_rows"] == 21, "stored_eligible_count", checks)
    check(production["held_panel"]["eligible_states"] == {"DARK": 6, "LIGHT": 15}, "stored_states", checks)
    check(production["held_panel"]["maximum_single_folio_share"] == 11 / 21, "stored_share", checks)
    check(all(production["gates"].values()), "all_gates_pass", checks)
    check(production["method"]["target_labels_masked"], "labels_masked", checks)
    check(not production["method"]["automated_ocr_segmentation_clip_embedding_similarity_or_object_naming"], "forbidden_vision_absent", checks)
    check(set(production["inputs"]["yale_images"]) == set(EXPECTED_IMAGES), "stored_image_inventory", checks)

    forbidden_columns = {"surface", "token", "formal_root", "role", "eva", "meaning", "translation"}
    check(not forbidden_columns.intersection(rows[0]), "no_target_columns", checks)
    report = PRODUCTION_REPORT.read_text(encoding="utf-8")
    for phrase in ("**21** clear pairings", "**6 DARK**", "**15", "labels remained sealed", "AUTHORIZE_SEPARATE_TEXT_PREREGISTRATION_ONLY_KEEP_LABELS_SEALED"):
        check(phrase in report, f"report_phrase_{len(checks)}", checks)

    result = {
        "experiment": "PHARMA_ROOT_COLOR_NATIVE_VISUAL_OWNERSHIP_CAPACITY_VALIDATION",
        "status": "PASS_SOURCE_IMAGE_BINDINGS_AND_GATE_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "inputs": {
            "production_tsv_sha256": sha(PRODUCTION_TSV),
            "production_json_sha256": sha(PRODUCTION_JSON),
            "production_report_sha256": sha(PRODUCTION_REPORT),
            "yale_manifest_sha256": MANIFEST_SHA,
        },
        "reconstructed": {
            "held_rows": 48,
            "visually_clear": 22,
            "eligible_clear": 21,
            "eligible_states": {"DARK": 6, "LIGHT": 15},
            "eligible_rows_by_folio": {"f89": 11, "f100": 8, "f102": 2},
            "maximum_single_folio_share": 11 / 21,
        },
        "scope_note": (
            "This validator checks source/image provenance, target masking, row completeness, "
            "eligibility logic, and gate arithmetic. Native visual grades remain machine-authored "
            "observations and are not independently inferred by this program."
        ),
        "decision": production["decision"],
        "claim_ceiling": production["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# Native-visual ownership validation\n\n"
        f"Status: **{result['status']}**\n\n"
        f"{len(checks)} source, image, schema, masking, and arithmetic checks passed. "
        "All ten registered Yale canvases were fetched and hash-matched. The validator "
        "reconstructed 21 eligible clear rows (6 DARK, 15 LIGHT) and the 11/21 maximum "
        "folio share.\n\n"
        f"Scope: {result['scope_note']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
