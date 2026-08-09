#!/usr/bin/env python3
"""Build SCP001 without reading any Voynich word or grammar feature."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ANNOT = ROOT / "experiments/semantic_assumptions/results/existing_human_page_annotations.tsv"
ZL = ROOT / "transcription/sources/ZL3b-n.txt"
INTER = ROOT / "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv"
BIND = HERE / "source_phase_binding.tsv"
OUT = HERE / "source_panel.tsv"
REPORT = ROOT / "experiments/semantic_assumptions/results/star_color_source_capacity_report.md"
JSON_OUT = HERE / "source_capacity.json"

EXPECTED_EXCLUSIONS = {
    "f103v": "VISIBLE_STAR_COUNT_14_BUT_ONLY_13_MANUAL_ZL_MARKERS",
    "f103r": "THREE_COLOR_OR_UNPAINTED",
    "f104r": "NONBINARY_RED_FORMS",
    "f105r": "MOSTLY_NOT_EXACTLY_ALTERNATING",
    "f106v": "VISIBLE_STAR_COUNT_14_BUT_15_MANUAL_ZL_MARKERS",
    "f107r": "VISIBLE_STAR_COUNT_15_BUT_ONLY_14_MANUAL_ZL_MARKERS",
    "f108r": "THREE_COLOR_OR_UNPAINTED",
    "f108v": "MIDPAGE_PHASE_RESTART",
    "f111r": "VISIBLE_STAR_COUNT_17_BUT_ONLY_6_MANUAL_ZL_MARKERS",
    "f111v": "VISIBLE_STAR_COUNT_19_BUT_ONLY_8_MANUAL_ZL_MARKERS",
    "f112r": "VISIBLE_STAR_COUNT_12_BUT_ONLY_11_MANUAL_ZL_MARKERS",
    "f115v": "RED_VERSUS_UNPAINTED_NOT_RED_VERSUS_YELLOW",
    "f116r": "RED_VERSUS_UNPAINTED_AND_PHASE_UNSTATED",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="\t")


def parse_zl_markers() -> dict[str, list[str]]:
    marker = re.compile(r"^<(?P<locus>f\d+[rv]\.\d+),[^>]+>\s+<%>")
    out: dict[str, list[str]] = {}
    with ZL.open(encoding="latin-1") as fh:
        for line in fh:
            m = marker.match(line)
            if m:
                locus = m.group("locus")
                page = locus.split(".", 1)[0]
                out.setdefault(page, []).append(locus)
    return out


def main() -> None:
    binding = list(rows(BIND))
    assert len(binding) == 9
    assert len({r["page"] for r in binding}) == len(binding)
    assert {r["first_color"] for r in binding} == {"RED", "YELLOW"}
    assert [r["page"] for r in binding if r["first_color"] == "YELLOW"] == ["f113r", "f114v"]
    for b in binding:
        assert b["scan_2004_url"].startswith("https://www.voynich.com/folios/color/")
        assert b["scan_2014_url"].startswith("https://archive.org/download/voynich/")
        assert re.fullmatch(r"[0-9a-f]{64}", b["scan_2004_sha256"])
        assert re.fullmatch(r"[0-9a-f]{64}", b["scan_2014_sha256"])
        assert b["scan_2004_sha256"] != b["scan_2014_sha256"]

    annotations = {r["page"]: r for r in rows(ANNOT)}
    markers = parse_zl_markers()
    covered = Counter()
    for r in rows(INTER):
        # Deliberately inspect identifiers only, never surface/root/role fields.
        covered[(r["locus"], r["edition"])] += 1

    panel = []
    for b in binding:
        page = b["page"]
        expected = int(b["star_count"])
        desc = annotations[page]["illustrations"]
        assert "alternat" in desc.lower() or "unusually starting" in desc.lower()
        if page == "f113r":
            assert "unusually starting with faded yellow" in desc.lower()
        if page == "f114v":
            assert "unusually starting with faded yellow" in desc.lower()
        loci = markers.get(page, [])
        assert len(loci) == expected, (page, expected, len(loci))
        for ordinal, locus in enumerate(loci, 1):
            first = b["first_color"]
            color = first if ordinal % 2 else ("YELLOW" if first == "RED" else "RED")
            editions = [e for e in ("ZL3b", "IT2a", "RF1b") if covered[(locus, e)] == 1]
            assert editions == ["ZL3b", "IT2a", "RF1b"], (locus, editions)
            panel.append({
                "page": page,
                "physical_folio": page[:-1],
                "star_ordinal": ordinal,
                "ordinal_parity": "ODD" if ordinal % 2 else "EVEN",
                "color": color,
                "first_color": first,
                "locus": locus,
                "zl_marker": "<%>",
                "reading_coverage": "ZL3b|IT2a|RF1b",
            })

    assert len(panel) == 120
    assert len({r["page"] for r in panel}) == 9
    assert len({r["physical_folio"] for r in panel}) == 7
    assert Counter(r["color"] for r in panel) == Counter({"RED": 63, "YELLOW": 57})
    assert sum(r["first_color"] == "YELLOW" for r in panel) == 28

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(panel[0]), delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(panel)

    payload = {
        "experiment": "SCP001",
        "status": "PASS_SOURCE_CAPACITY_TEXT_FEATURES_UNOPENED",
        "inputs": {str(p.relative_to(ROOT)): sha(p) for p in (ANNOT, ZL, INTER, BIND)},
        "pages": 9,
        "physical_folios": 7,
        "markers": 120,
        "colors": dict(sorted(Counter(r["color"] for r in panel).items())),
        "first_color_pages": dict(sorted(Counter(r["first_color"] for r in binding).items())),
        "reversed_phase_markers": 28,
        "two_scan_manual_phase_qc_pages": 9,
        "excluded_pages": EXPECTED_EXCLUSIONS,
        "target_text_feature_accessed": False,
        "claim_ceiling": "author-visible alternating marker-color coordinate only",
        "panel_sha256": sha(OUT),
    }
    JSON_OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# SCP001 star-color source capacity",
        "",
        "## Decision",
        "",
        "**PASS — source panel frozen; Voynich text features remain unopened.**",
        "",
        "Human page descriptions and manual scan QC identify 120 marginal stars on",
        "9 pages / 7 physical folios whose centers alternate exactly between red",
        "and faded yellow. The manually transcribed ZL `<%>` marker count equals the",
        "described star count on every page, giving a direct marker-to-line binding.",
        "Every bound physical locus has exactly one ZL3b, IT2a, and RF1b row. Six",
        "otherwise clean-color pages were rejected because the visible star count did",
        "not equal the retained manual ZL marker count; no proximity repair was used.",
        "",
        "Seven pages start RED; f113r and f114v start YELLOW. The two reversed",
        "pages contribute 28 markers, so color is not identical to odd/even ordinal",
        "position. The final panel has 63 RED and 57 YELLOW markers.",
        "Manual inspection of both the 2004 and independently digitized 2014 scan",
        "families agrees on the first-color phase for all nine retained pages; both",
        "public URLs and exact SHA-256 identities are frozen in the binding table.",
        "",
        "Excluded before text scoring: f103r/f108r (white/three-state), f104r",
        "(nonbinary red forms), f105r (only mostly alternating), f108v (mid-page",
        "restart), f115v/f116r (red versus unpainted), plus f103v, f106v, f107r,",
        "f111r, f111v, and f112r because visible-star and manual-marker counts differ.",
        "",
        "The intended falsifier is page-phase exchange: preserve every line, ordinal,",
        "alternation, page, and folio, but flip RED/YELLOW phase at whole-page level.",
        "This tests a color-conditioned construction after controlling the otherwise",
        "perfect local odd/even alternation.",
        "",
        "No Voynich surface, root, role, English meaning, lexeme, plaintext, language,",
        "or translation has been tested or inferred.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "./vpy experiments/semantic_assumptions/star_color_phase/build_star_color_source_panel.py",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
