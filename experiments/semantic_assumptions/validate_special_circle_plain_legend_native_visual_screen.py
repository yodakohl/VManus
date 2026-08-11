#!/usr/bin/env python3
"""Independent metadata reconstruction of the f67--f73 anchor screen."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue"
PAGES = BASE / "results/existing_human_page_annotations.tsv"
RESULT = BASE / "results/special_circle_plain_legend_native_visual_screen.json"
REPORT = BASE / "results/special_circle_plain_legend_native_visual_screen_report.md"
OUT = BASE / "results/special_circle_plain_legend_native_visual_screen_validation.json"
OUT_MD = BASE / "results/special_circle_plain_legend_native_visual_screen_validation.md"

EXPECTED_PANELS = {
    "1006194": ["f67r1", "f67r2"], "1006195": ["f67v2", "f67v1"],
    "1006196": ["f68r1", "f68r2", "f68r3"], "1006197": ["f68v3", "f68v2", "f68v1"],
    "1006198": ["f69r"], "1006199": ["f69v", "f70r1", "f70r2"],
    "1006200": ["f70v2"], "1006201": ["f70v1"], "1006202": ["f71r"],
    "1006203": ["f71v", "f72r1", "f72r2", "f72r3"],
    "1006204": ["f72v3", "f72v2"], "1006205": ["f72v1"],
    "1006206": ["f73r"], "1006207": ["f73v"],
}
EXPECTED_MONTHS = {
    "f70v2": "March", "f70v1": "April", "f71r": "April", "f71v": "May",
    "f72r1": "May", "f72r2": "June", "f72r3": "July", "f72v3": "August",
    "f72v2": "September", "f72v1": "October", "f73r": "November", "f73v": "December",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    checks: list[dict[str, object]] = []

    def check(name: str, value: bool) -> None:
        checks.append({"name": name, "pass": bool(value)})
        if not value:
            raise SystemExit(name)

    hashes = {
        "q09": "56b592284239fbd4d2ffabac2c534207c2e8a6da00ce4570d526544b9793f977",
        "q10": "2f15159cd9ea04213f2031fbbebe33e3b057795656e349bf765e4f0344ff2ec5",
        "q11": "5553f82d3c7d016c3a9f7853388e844764239f929cdd24f2870a1d56b172ad64",
        "q12": "3a9b4e587c9b9d0228bf87eea1b3a0e34f3fcfe4abafd71e712213e0af9132b6",
    }
    check("catalogue_hashes", all(sha(CATALOGUE / f"{q}.html") == value for q, value in hashes.items()))
    check("page_annotation_hash", sha(PAGES) == "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa")
    mapping: dict[str, list[str]] = {}
    for q in hashes:
        current = None
        for line in (CATALOGUE / f"{q}.html").read_text(encoding="utf-8", errors="replace").splitlines():
            match = re.search(r'<TH CLASS="Ph" ID="([^"]+)">', line, re.I)
            if match:
                current = match.group(1)
            match = re.search(r"child_oid=(1006\d+)", line)
            if match and current and match.group(1) in EXPECTED_PANELS:
                mapping.setdefault(match.group(1), []).append(current)
    check("exact_canvas_panel_mapping", mapping == EXPECTED_PANELS)
    check("fourteen_canvases_twenty_six_panels", len(mapping) == 14 and sum(map(len, mapping.values())) == 26)
    months: dict[str, str] = {}
    with PAGES.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["page"] in EXPECTED_MONTHS:
                match = re.search(
                    r"month name ([A-Z][A-Za-z]+) is written in the centre in a different hand",
                    " ".join(row.values()),
                )
                if match:
                    months[row["page"]] = match.group(1)
    check("twelve_different_hand_month_names", months == EXPECTED_MONTHS)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("stop_status", result["status"] == "STOP_NATIVE_VISUAL_NO_NEW_MAIN_HAND_READABLE_REGISTER")
    check("zero_new_anchor_and_equivalence", result["counts"]["new_main_hand_readable_multicharacter_legends"] == 0 and result["counts"]["author_visible_plain_voynich_equivalences"] == 0)
    check("f68_near_miss_preserved_unresolved", result["counts"]["unresolved_preexisting_main_diagram_near_misses"] == 1 and result["gates"]["preexisting_f68r2_unresolved_sequence_not_reclassified"] is True)
    check("zero_text_feature_score_access", result["counts"]["voynich_surfaces_transcribed_or_loaded"] == 0 and result["counts"]["formal_features_constructed"] == 0 and result["counts"]["associations_scored"] == 0)
    check("report_status", result["status"] in REPORT.read_text(encoding="utf-8"))
    output = {
        "experiment": "SPECIAL_CIRCLE_PLAIN_LEGEND_NATIVE_VISUAL_SCREEN_VALIDATION",
        "status": "PASS_INDEPENDENT_METADATA_RECONSTRUCTION",
        "validated_status": result["status"],
        "check_count": len(checks),
        "checks": checks,
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Special-circle plain-legend screen validation\n\n"
        "Status: **PASS_INDEPENDENT_METADATA_RECONSTRUCTION** (10 checks).\n\n"
        "The complete 14-canvas/26-panel source map, twelve different-hand month names, unresolved f68r2 "
        "near-miss status, and zero text/feature/score access reconstruct exactly. The negative visual judgment "
        "remains a source-bound machine-authored observation rather than a human paleographic opinion.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
