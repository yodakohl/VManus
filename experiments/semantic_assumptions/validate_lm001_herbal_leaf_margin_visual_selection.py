#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANN = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"
ZL = ROOT / "transcription/voynich_zl3b_lines.tsv"
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
RESULT = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.json"
MANIFEST_SHA = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def h(tag: str, page: str) -> str:
    return hashlib.sha256(f"{tag}|{page}".encode("ascii")).hexdigest()


def main() -> None:
    checks: list[str] = []
    with ZL.open(encoding="utf-8", newline="") as f:
        meta = {}
        for row in csv.DictReader(f, delimiter="\t"):
            meta.setdefault(row["page"], row)
    pool = []
    with ANN.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            page = row["page"]
            m = re.match(r"^f(\d+)", page.lower())
            if "SOURCE_HERBAL_PAGE" in row["source_tags"] and page in meta and m:
                pool.append((page, f"f{m.group(1)}", int(m.group(1)), meta[page]["language"]))
    one = {}
    for page, folio, num, currier in pool:
        item = (h("LM001_PAGE", page), page, folio, num, currier)
        if folio not in one or item < one[folio]:
            one[folio] = item
    expected = []
    for currier in ("A", "B"):
        cp = sorted((x for x in one.values() if x[4] == currier), key=lambda x: (x[3], x[1]))
        tagged = [(x, min(4, 4 * i // len(cp) + 1)) for i, x in enumerate(cp)]
        for q in range(1, 5):
            selected = sorted((x for x, qq in tagged if qq == q), key=lambda x: x[0])[:4]
            phase = sorted(selected, key=lambda x: h("LM001_PHASE", x[1]))
            for i, x in enumerate(phase):
                expected.append(("LM" + h("LM001_OPAQUE", x[1])[:8].upper(), "CALIBRATION" if i < 2 else "HELD", currier, str(q), x[1], x[2], str(x[3]), x[0]))
    with PANEL.open(encoding="utf-8", newline="") as f:
        actual = list(csv.DictReader(f, delimiter="\t"))
    projection = [(r["opaque_id"], r["phase"], r["currier"], r["folio_rank_quartile"], r["page"], r["physical_folio"], r["folio_number"], r["page_selection_sha256"]) for r in actual]
    assert sorted(expected) == sorted(projection)
    checks.append("independent_selection_reconstruction")
    assert len(actual) == len({r["page"] for r in actual}) == len({r["physical_folio"] for r in actual}) == 32
    checks.append("page_and_folio_uniqueness")
    c = Counter((r["currier"], r["folio_rank_quartile"], r["phase"]) for r in actual)
    assert all(c[(cur, str(q), phase)] == 2 for cur in ("A", "B") for q in range(1, 5) for phase in ("CALIBRATION", "HELD"))
    checks.append("cell_balance")
    assert len({r["canvas_id"] for r in actual}) == 32 and all(r["review_image_url"].endswith("/full/1600,/0/default.jpg") for r in actual)
    checks.append("official_canvas_bindings")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["status"] == "FROZEN_BEFORE_SELECTED_IMAGE_INSPECTION"
    assert stored["inputs"]["yale_manifest_2002046_sha256"] == MANIFEST_SHA
    assert stored["panel_sha256"] == hashlib.sha256(PANEL.read_bytes()).hexdigest()
    assert all(stored["gates"].values())
    checks.append("canonical_result_bindings_and_gates")
    out = {
        "experiment": "LM001_HERBAL_LEAF_MARGIN_VISUAL_SELECTION_VALIDATION",
        "status": "PASS_INDEPENDENT_METADATA_ONLY_SELECTION_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "claim_ceiling": stored["claim_ceiling"],
    }
    path = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection_validation.json"
    path.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
