#!/usr/bin/env python3
"""Independent, source-only SCP001 panel reconstruction."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BIND = HERE / "source_phase_binding.tsv"
PANEL = HERE / "source_panel.tsv"
CAP = HERE / "source_capacity.json"
ANNOT = ROOT / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
ZL = ROOT / "transcription/sources/ZL3b-n.txt"
INTER = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
OUT = HERE / "source_validation.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/star_color_source_capacity_validation.md"

EXPECTED = {
    "f104v": (13, "RED"), "f105v": (10, "RED"),
    "f107v": (15, "RED"), "f112v": (13, "RED"),
    "f113r": (16, "YELLOW"), "f113v": (15, "RED"),
    "f114r": (13, "RED"), "f114v": (12, "YELLOW"),
    "f115r": (13, "RED"),
}


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: dict[str, bool] = {}
    cap = json.loads(CAP.read_text(encoding="utf-8"))
    binding = read_rows(BIND)
    panel = read_rows(PANEL)
    annotations = {r["page"]: r for r in read_rows(ANNOT)}

    checks["bound_input_hashes"] = cap["inputs"] == {
        str(p.relative_to(ROOT)): digest(p) for p in (ANNOT, ZL, INTER, BIND)
    }
    checks["exact_binding"] = {
        r["page"]: (int(r["star_count"]), r["first_color"]) for r in binding
    } == EXPECTED
    checks["two_distinct_scan_families"] = all(
        r["scan_2004_url"].startswith("https://www.voynich.com/folios/color/")
        and r["scan_2014_url"].startswith("https://archive.org/download/voynich/")
        and re.fullmatch(r"[0-9a-f]{64}", r["scan_2004_sha256"])
        and re.fullmatch(r"[0-9a-f]{64}", r["scan_2014_sha256"])
        and r["scan_2004_sha256"] != r["scan_2014_sha256"]
        for r in binding
    )
    checks["annotation_alternation"] = all(
        "alternat" in annotations[p]["illustrations"].lower() for p in EXPECTED
    )
    checks["explicit_reverse_descriptions"] = all(
        "unusually starting with faded yellow" in annotations[p]["illustrations"].lower()
        for p in ("f113r", "f114v")
    )

    marker_re = re.compile(r"^<(?P<locus>f\d+[rv]\.\d+),[^>]+>\s+<%>")
    markers: dict[str, list[str]] = {}
    with ZL.open(encoding="latin-1") as fh:
        for line in fh:
            m = marker_re.match(line)
            if m:
                locus = m.group("locus")
                markers.setdefault(locus.split(".", 1)[0], []).append(locus)
    checks["marker_counts_equal_visible_counts"] = all(
        len(markers.get(p, [])) == n for p, (n, _) in EXPECTED.items()
    )

    coverage = Counter()
    with INTER.open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            coverage[(r["locus"], r["edition"])] += 1

    rebuilt = []
    for page, (count, first) in EXPECTED.items():
        for i, locus in enumerate(markers[page], 1):
            color = first if i % 2 else ("YELLOW" if first == "RED" else "RED")
            rebuilt.append({
                "page": page,
                "physical_folio": page[:-1],
                "star_ordinal": str(i),
                "ordinal_parity": "ODD" if i % 2 else "EVEN",
                "color": color,
                "first_color": first,
                "locus": locus,
                "zl_marker": "<%>",
                "reading_coverage": "ZL3b|IT2a|RF1b",
            })
    checks["exact_panel_reconstruction"] = rebuilt == panel
    checks["exact_three_reading_cardinality"] = all(
        coverage[(r["locus"], edition)] == 1
        for r in rebuilt for edition in ("ZL3b", "IT2a", "RF1b")
    )
    checks["capacity_counts"] = (
        len(panel) == 120
        and len({r["page"] for r in panel}) == 9
        and len({r["physical_folio"] for r in panel}) == 7
        and Counter(r["color"] for r in panel) == Counter({"RED": 63, "YELLOW": 57})
    )
    checks["phase_not_parity_identity"] = (
        sum(r["first_color"] == "YELLOW" for r in panel) == 28
        and {r["page"] for r in panel if r["first_color"] == "YELLOW"} == {"f113r", "f114v"}
    )
    checks["panel_hash"] = digest(PANEL) == cap["panel_sha256"]
    checks["target_unopened"] = (
        cap["target_text_feature_accessed"] is False
        and not (HERE / "TARGET_RESULT.json").exists()
        and not (HERE / "target_features.tsv").exists()
    )
    checks["claim_ceiling"] = cap["claim_ceiling"] == "author-visible alternating marker-color coordinate only"

    assert all(checks.values()), {k: v for k, v in checks.items() if not v}
    payload = {
        "experiment": "SCP001",
        "status": "PASS_INDEPENDENT_SOURCE_VALIDATION_TARGET_UNOPENED",
        "checks": checks,
        "passed": sum(checks.values()),
        "total": len(checks),
        "panel_sha256": digest(PANEL),
        "target_text_feature_accessed": False,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# SCP001 independent source validation\n\n"
        f"**PASS — {sum(checks.values())}/{len(checks)} source-only checks; target unopened.**\n\n"
        "A nonimporting reconstruction verifies the bound input hashes, exact nine-page "
        "phase table, two distinct scan families, human alternation descriptions, two "
        "explicit reversed phases, equality of visible-star and manual-marker counts, "
        "all 120 marker-to-line rows, exact three-reading cardinality, seven-folio "
        "capacity, color counts, panel hash, absent target artifacts, and claim ceiling.\n\n"
        "The code validates provenance and row construction; the color judgment itself "
        "was made by direct human inspection, never OCR or automated vision. No text "
        "feature, color function, lexeme, plaintext, language, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
