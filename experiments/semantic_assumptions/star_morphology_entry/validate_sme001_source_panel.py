#!/usr/bin/env python3
"""Independent, nonimporting reconstruction of the SME001 source pass."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ZL = ROOT / "transcription/sources/ZL3b-n.txt"
INTER = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
MANIFEST = HERE / "SOURCE_MANIFEST.tsv"
PANEL = HERE / "source_panel.tsv"
BINDING = HERE / "source_unit_binding.tsv"
CAPACITY = HERE / "source_capacity.json"
OUT = HERE / "source_validation.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_source_validation.md"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    checks: list[str] = []
    manifest = {row["source_id"]: row for row in read_tsv(MANIFEST)}
    spec = manifest["STOLFI_STAR_PROPS"]
    with urllib.request.urlopen(spec["url"], timeout=30) as response:
        raw = response.read()
    assert sha(raw) == spec["sha256"]
    checks.append("live_source_hash")
    report_spec = manifest["STOLFI_PAGE_REPORT"]
    with urllib.request.urlopen(report_spec["url"], timeout=30) as response:
        report_raw = response.read()
    assert sha(report_raw) == report_spec["sha256"]
    checks.append("live_method_report_hash")

    stars: dict[tuple[str, int], dict[str, str]] = {}
    page_counts: Counter[str] = Counter()
    last: dict[str, int] = {}
    for line in raw.decode("utf-8").splitlines():
        if not re.match(r"^f\d+[rv]\s*[|]", line):
            continue
        cells = [cell.strip() for cell in line.split("|")]
        assert len(cells) == 9
        page, snn, vpos, core, paint, color, rays, tail, observation = cells
        ordinal = int(snn[1:])
        assert ordinal == last.get(page, 0) + 1
        last[page] = ordinal
        stars[(page, ordinal)] = {
            "page": page, "physical_folio": page[:-1], "star_ordinal": str(ordinal),
            "vpos": vpos, "core": core, "paint": paint, "color": color,
            "rays": rays, "tail": tail, "observation": observation,
        }
        page_counts[page] += 1
    assert len(stars) == 323 and len(page_counts) == 23 and len({page[:-1] for page in page_counts}) == 12
    checks.append("source_inventory")

    marker_pattern = re.compile(r"^<(?P<locus>f\d+[rv]\.\d+),[^>]+>\s+<%>")
    markers: dict[str, list[str]] = {}
    with ZL.open(encoding="latin-1") as fh:
        for line in fh:
            match = marker_pattern.match(line)
            if match:
                locus = match.group("locus")
                markers.setdefault(locus.split(".", 1)[0], []).append(locus)
    matched = sorted(page for page in page_counts if page_counts[page] == len(markers.get(page, [])))
    assert matched == ["f104r", "f104v", "f105r", "f105v", "f106r", "f107v", "f112v", "f113r", "f113v", "f114r", "f114v", "f115r", "f115v"]
    checks.append("exact_count_page_gate")

    coverage = Counter((row["locus"], row["edition"]) for row in read_tsv(INTER))
    rebuilt: list[dict[str, str]] = []
    for page in matched:
        for ordinal, locus in enumerate(markers[page], 1):
            assert all(coverage[(locus, edition)] == 1 for edition in ("ZL3b", "IT2a", "RF1b"))
            rebuilt.append({
                **stars[(page, ordinal)], "locus": locus, "zl_marker": "<%>",
                "reading_coverage": "ZL3b|IT2a|RF1b",
            })
    assert len(rebuilt) == 171 and len({row["physical_folio"] for row in rebuilt}) == 8
    checks.extend(["strict_panel_cardinality", "three_reading_coverage"])

    stored = read_tsv(PANEL)
    assert stored == rebuilt
    checks.append("panel_exact_rows")
    assert len({(row["page"], row["star_ordinal"]) for row in stored}) == len(stored)
    assert len({row["locus"] for row in stored}) == len(stored)
    binding = read_tsv(BINDING)
    assert binding == [{key: row[key] for key in ("page", "physical_folio", "star_ordinal", "locus")} for row in rebuilt]
    assert not ({"vpos", "core", "paint", "color", "rays", "tail", "observation"} & set(binding[0]))
    checks.append("one_to_one_bindings")

    ray = [row for row in stored if row["rays"] in {"7", "8"}]
    assert len(ray) == 164 and Counter(row["rays"] for row in ray) == Counter({"7": 90, "8": 74})
    assert all(len({row["rays"] for row in ray if row["page"] == page}) == 2 for page in matched)
    checks.append("ray_capacity")

    tail = [row for row in stored if row["tail"] in {"1", "2"}]
    tail_pages = [page for page in matched if len({row["tail"] for row in tail if row["page"] == page}) == 2]
    assert len(tail) == 170 and Counter(row["tail"] for row in tail) == Counter({"1": 147, "2": 23})
    assert len(tail_pages) == 9 and len({page[:-1] for page in tail_pages}) == 7
    checks.append("tail_capacity")

    core = [row for row in stored if row["core"] in {"no", "dot"}]
    core_pages = [page for page in matched if len({row["core"] for row in core if row["page"] == page}) == 2]
    assert len(core) == 77 and Counter(row["core"] for row in core) == Counter({"no": 65, "dot": 12})
    assert len(core_pages) == 6 and len({page[:-1] for page in core_pages}) == 4
    assert all(row["core"] == "--" for row in stored if row["color"] == "RED")
    checks.append("core_stop_and_missingness")

    capacity = json.loads(CAPACITY.read_text(encoding="utf-8"))
    assert capacity["panel_sha256"] == sha(PANEL.read_bytes())
    assert capacity["source_unit_binding_sha256"] == sha(BINDING.read_bytes())
    assert capacity["ray_7_vs_8"]["decision"] == "PASS_CAPACITY"
    assert capacity["tail_1_vs_2"]["decision"] == "PASS_CAPACITY"
    assert capacity["core_no_vs_dot"]["decision"] == "STOP_ONLY_FOUR_INFORMATIVE_FOLIOS"
    checks.append("capacity_artifact")
    assert capacity["target_text_features_accessed"] is False
    assert capacity["target_result_absent"] is True and not (HERE / "TARGET_RESULT.json").exists()
    checks.append("target_absence")
    assert capacity["claim_ceiling"] == "human star-morphology coordinate and exact ordinal-to-marker source capacity only"
    checks.append("claim_ceiling")

    payload = {"experiment": "SME001", "status": "PASS_INDEPENDENT_SOURCE_RECONSTRUCTION", "checks": checks, "check_count": len(checks), "panel_sha256": sha(PANEL.read_bytes()), "target_absent": True}
    assert len(checks) == 14
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# SME001 independent source validation", "", "**PASS — 14/14 independent checks.**", "",
        "A nonimporting implementation refetched and hash-checked the human source, reconstructed all 323 source stars, the exact-count page gate, all 171 ordinal-to-marker rows, all-reading coverage, uniqueness, morphology capacities, the visible-core stop, artifact hash, target absence, and claim ceiling.", "",
        "No Voynich text feature, marker meaning, lexeme, plaintext, language, or translation was opened.",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
