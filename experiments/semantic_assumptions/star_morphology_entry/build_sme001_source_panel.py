#!/usr/bin/env python3
"""Build the text-blind SME001 star-morphology source panel."""

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
RESULT = HERE / "source_capacity.json"
REPORT = ROOT / "experiments/semantic_assumptions/results/sme001_star_morphology_source_capacity.md"

EXPECTED_SOURCE_ROWS = 323
EXPECTED_SOURCE_PAGES = 23
EXPECTED_MATCHED_PAGES = [
    "f104r", "f104v", "f105r", "f105v", "f106r", "f107v", "f112v",
    "f113r", "f113v", "f114r", "f114v", "f115r", "f115v",
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def tsv_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        yield from csv.DictReader(fh, delimiter="\t")


def fetch_source() -> tuple[dict[str, str], bytes]:
    rows = {row["source_id"]: row for row in tsv_rows(MANIFEST)}
    spec = rows["STOLFI_STAR_PROPS"]
    with urllib.request.urlopen(spec["url"], timeout=30) as response:
        data = response.read()
    assert sha_bytes(data) == spec["sha256"], "live human source hash drift"
    return spec, data


def parse_star_props(data: bytes) -> list[dict[str, object]]:
    text = data.decode("utf-8")
    out: list[dict[str, object]] = []
    last: dict[str, int] = {}
    for raw in text.splitlines():
        if not re.match(r"^f\d+[rv]\s*[|]", raw):
            continue
        cells = [cell.strip() for cell in raw.split("|")]
        assert len(cells) == 9, raw
        page, snn, vpos, core, paint, color, rays, tail, observation = cells
        assert re.fullmatch(r"S\d\d", snn)
        ordinal = int(snn[1:])
        assert ordinal == last.get(page, 0) + 1
        last[page] = ordinal
        assert core in {"--", "no", "dot", "ring", "??", "no?"}
        assert paint in {"no", "splot", "grub", "fill", "frub"}
        assert color in {"--", "yel", "RED", "WHT"}
        assert int(rays) in {6, 7, 8, 9}
        assert tail in {"-", "1", "2"}
        out.append({
            "page": page,
            "physical_folio": page[:-1],
            "star_ordinal": ordinal,
            "vpos": vpos,
            "core": core,
            "paint": paint,
            "color": color,
            "rays": int(rays),
            "tail": tail,
            "observation": observation,
        })
    return out


def parse_markers() -> dict[str, list[str]]:
    pattern = re.compile(r"^<(?P<locus>f\d+[rv]\.\d+),[^>]+>\s+<%>")
    out: dict[str, list[str]] = {}
    with ZL.open(encoding="latin-1") as fh:
        for line in fh:
            match = pattern.match(line)
            if match:
                locus = match.group("locus")
                out.setdefault(locus.split(".", 1)[0], []).append(locus)
    return out


def variation(rows: list[dict[str, object]], field: str, allowed: set[object]) -> dict[str, object]:
    eligible = [row for row in rows if row[field] in allowed]
    counts = Counter(row[field] for row in eligible)
    pages = sorted({str(row["page"]) for row in eligible})
    variable_pages = []
    for page in pages:
        values = [row[field] for row in eligible if row["page"] == page]
        if len(set(values)) >= 2:
            variable_pages.append(page)
    return {
        "rows": len(eligible),
        "counts": {str(key): value for key, value in sorted(counts.items(), key=lambda item: str(item[0]))},
        "pages": len(pages),
        "folios": len({page[:-1] for page in pages}),
        "variable_pages": variable_pages,
        "variable_page_count": len(variable_pages),
        "informative_folios": len({page[:-1] for page in variable_pages}),
    }


def main() -> None:
    source, raw = fetch_source()
    stars = parse_star_props(raw)
    assert len(stars) == EXPECTED_SOURCE_ROWS
    assert len({row["page"] for row in stars}) == EXPECTED_SOURCE_PAGES
    assert len({row["physical_folio"] for row in stars}) == 12

    markers = parse_markers()
    star_counts = Counter(str(row["page"]) for row in stars)
    matched_pages = sorted(page for page, count in star_counts.items() if count == len(markers.get(page, [])))
    assert matched_pages == EXPECTED_MATCHED_PAGES

    by_key = {(str(row["page"]), int(row["star_ordinal"])): row for row in stars}
    coverage = Counter()
    for row in tsv_rows(INTER):
        coverage[(row["locus"], row["edition"])] += 1

    panel: list[dict[str, object]] = []
    for page in matched_pages:
        for ordinal, locus in enumerate(markers[page], 1):
            star = by_key[(page, ordinal)]
            editions = [edition for edition in ("ZL3b", "IT2a", "RF1b") if coverage[(locus, edition)] == 1]
            assert editions == ["ZL3b", "IT2a", "RF1b"], (locus, editions)
            panel.append({
                **star,
                "locus": locus,
                "zl_marker": "<%>",
                "reading_coverage": "ZL3b|IT2a|RF1b",
            })

    assert len(panel) == 171
    assert len({row["page"] for row in panel}) == 13
    assert len({row["physical_folio"] for row in panel}) == 8

    fields = [
        "page", "physical_folio", "star_ordinal", "locus", "vpos", "core",
        "paint", "color", "rays", "tail", "observation", "zl_marker", "reading_coverage",
    ]
    with PANEL.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(panel)

    binding_fields = ("page", "physical_folio", "star_ordinal", "locus")
    with BINDING.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=binding_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row[key] for key in binding_fields} for row in panel)

    ray = variation(panel, "rays", {7, 8})
    tail = variation(panel, "tail", {"1", "2"})
    core = variation(panel, "core", {"no", "dot"})
    assert ray == {
        "rows": 164, "counts": {"7": 90, "8": 74}, "pages": 13, "folios": 8,
        "variable_pages": EXPECTED_MATCHED_PAGES, "variable_page_count": 13, "informative_folios": 8,
    }
    assert tail["rows"] == 170 and tail["counts"] == {"1": 147, "2": 23}
    assert tail["variable_page_count"] == 9 and tail["informative_folios"] == 7
    assert core["rows"] == 77 and core["counts"] == {"dot": 12, "no": 65}
    assert core["variable_page_count"] == 6 and core["informative_folios"] == 4

    mismatches = {
        page: {"human_stars": star_counts[page], "manual_markers": len(markers.get(page, []))}
        for page in sorted(star_counts) if page not in matched_pages
    }
    payload = {
        "experiment": "SME001",
        "status": "PASS_SOURCE_CAPACITY_RAY_AND_TAIL_ONLY_TARGET_UNOPENED",
        "source": {"url": source["url"], "sha256": source["sha256"], "rows": 323, "pages": 23, "folios": 12},
        "input_hashes": {
            str(ZL.relative_to(ROOT)): sha_path(ZL),
            str(INTER.relative_to(ROOT)): sha_path(INTER),
            str(MANIFEST.relative_to(ROOT)): sha_path(MANIFEST),
        },
        "strict_panel": {"rows": 171, "pages": 13, "folios": 8, "matched_pages": matched_pages, "mismatches": mismatches},
        "ray_7_vs_8": {**ray, "decision": "PASS_CAPACITY"},
        "tail_1_vs_2": {**tail, "decision": "PASS_CAPACITY"},
        "core_no_vs_dot": {**core, "decision": "STOP_ONLY_FOUR_INFORMATIVE_FOLIOS"},
        "panel_sha256": sha_path(PANEL),
        "source_unit_binding_sha256": sha_path(BINDING),
        "target_text_features_accessed": False,
        "target_result_absent": not (HERE / "TARGET_RESULT.json").exists(),
        "claim_ceiling": "human star-morphology coordinate and exact ordinal-to-marker source capacity only",
    }
    assert payload["target_result_absent"]
    RESULT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    REPORT.write_text("\n".join([
        "# SME001 star-morphology source capacity",
        "",
        "## Decision",
        "",
        "**PASS for 7-vs-8 rays and one-vs-two tails; STOP for visible core state. Voynich text features remain unopened.**",
        "",
        "Jorge Stolfi's [public, human-authored table](https://www.ic.unicamp.br/~stolfi/voynich/Notes/076/star-props.txt) contains 323 marginal stars on 23 pages / 12 physical folios. It records top-to-bottom star number, center/core state, paint, color, ray count, tail count, and observations; the [page-by-page methodology](https://www.ic.unicamp.br/~stolfi/voynich/Notes/076/report/sec-per-page/page.html) is published with it. Both exact source URLs and SHA-256 identities are frozen. No OCR or automated/neural image analysis was used.",
        "",
        "Only pages whose complete human star count equals the existing manual ZL `<%>` paragraph-marker count are admitted. Thirteen pages / eight physical folios match exactly, yielding 171 ordinal bindings. Every bound marker has exactly one ZL3b, IT2a, and RF1b row. Ten mismatched pages are excluded and no proximity, inferred nearest line, or Stolfi paragraph assignment is used.",
        "",
        "After excluding the rare 6- and 9-ray forms, 7-vs-8 rays retains 164 entries; all 13 pages and all eight folios vary internally (90 seven-ray, 74 eight-ray). One-vs-two tails retains 170 entries; nine pages on seven folios vary internally (147 one-tail, 23 two-tail). Visible no-core vs dot retains 77 entries but varies within pages on only four physical folios, so it fails capacity and must not be scored. Opaque red cores are unknown (`--`), never negative.",
        "",
        "The tail-absence classifier reported elsewhere is not reproduced: this strict panel contains only one tail-less entry, while the full source places most tail absence on a few pages/bifolios. The admissible tail contrast is one tail versus the separately drawn two-stroke/fat-tail state, with page-sequence structure preserved in any future null.",
        "",
        "This source pass supplies marker morphology, not marker meaning. It establishes no category name, recipe class, number, word, lexeme, plaintext, language, or translation.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "./vpy experiments/semantic_assumptions/star_morphology_entry/build_sme001_source_panel.py",
        "```",
    ]) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
