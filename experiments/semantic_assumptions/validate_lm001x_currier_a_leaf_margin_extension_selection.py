#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANN = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"
ZL = ROOT / "transcription/voynich_zl3b_lines.tsv"
OLD = ROOT / "experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv"
PANEL = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.tsv"
RESULT = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection.json"
OUT = ROOT / "experiments/semantic_assumptions/results/lm001x_currier_a_leaf_margin_extension_selection_validation.json"
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
MANIFEST_SHA256 = "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def main() -> None:
    checks = []
    metadata = {}
    with ZL.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            metadata.setdefault(row["page"], row)
    with OLD.open(encoding="utf-8", newline="") as handle:
        excluded = {row["physical_folio"] for row in csv.DictReader(handle, delimiter="\t")}
    pages = []
    all_a = {}
    with ANN.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            page = row["page"]
            match = re.match(r"^f(\d+)", page.lower())
            if "SOURCE_HERBAL_PAGE" not in row["source_tags"] or page not in metadata or metadata[page]["language"] != "A" or not match:
                continue
            folio = f"f{match.group(1)}"
            candidate = (int(match.group(1)), page)
            if folio not in all_a or digest(f"LM001_PAGE|{page}") < digest(f"LM001_PAGE|{all_a[folio][1]}"):
                all_a[folio] = candidate
            if folio not in excluded:
                pages.append((page, folio, int(match.group(1)), row["quire"] or metadata[page]["quire"]))
    ranked = sorted(all_a.items(), key=lambda item: (item[1][0], item[1][1]))
    quartile = {folio: min(4, 4 * index // len(ranked) + 1) for index, (folio, _) in enumerate(ranked)}
    one = {}
    for page, folio, number, quire in pages:
        row = (page, folio, number, quire, digest(f"LM001X_PAGE|{page}"), digest(f"LM001X_SELECT|{page}"))
        if folio not in one or row[4] < one[folio][4]:
            one[folio] = row
    chosen = []
    for quire in sorted({row[3] for row in one.values() if row[3] != "q05"}):
        chosen.extend(sorted((row for row in one.values() if row[3] == quire), key=lambda row: row[5])[:3])
    expected = {
        "LX" + digest(f"LM001X_OPAQUE|{row[0]}")[:8].upper(): {
            "page": row[0], "physical_folio": row[1], "folio_number": str(row[2]),
            "quire": row[3], "folio_rank_quartile": str(quartile[row[1]]),
            "folio_page_sha256": row[4], "selection_sha256": row[5],
        }
        for row in chosen
    }
    stored = list(csv.DictReader(PANEL.open(encoding="utf-8"), delimiter="\t"))
    assert len(stored) == 19 and {row["opaque_id"] for row in stored} == set(expected)
    for row in stored:
        assert all(row[key] == value for key, value in expected[row["opaque_id"]].items())
    checks.append("independent_exact_19_page_selection")
    assert len({row["physical_folio"] for row in stored}) == 19 and all(row["currier"] == "A" for row in stored)
    checks.append("new_folio_and_currier_guards")
    quire_counts = Counter(row["quire"] for row in stored)
    assert "q05" not in quire_counts and max(quire_counts.values()) == 3 and len(quire_counts) == 8
    checks.append("quire_exclusion_cap_and_spread")
    request = urllib.request.Request(MANIFEST_URL, headers={"User-Agent": "VManus-LM001X-validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256
    manifest = json.loads(raw.decode("utf-8"))
    canvas_ids = {canvas["id"].rsplit("/", 1)[-1] for canvas in manifest["items"]}
    assert all(row["canvas_id"] in canvas_ids for row in stored)
    checks.append("official_manifest_and_canvas_bindings")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["status"] == "FROZEN_BEFORE_EXTENSION_IMAGE_INSPECTION"
    assert result["panel_sha256"] == hashlib.sha256(PANEL.read_bytes()).hexdigest()
    checks.append("canonical_selection_result")
    assert result["gates"]["selected_images_not_opened_by_builder"] is True and result["gates"]["no_voynich_text_features_accessed"] is True
    checks.append("access_seal")
    validation = {
        "experiment": "LM001X_CURRIER_A_LEAF_MARGIN_EXTENSION_SELECTION_VALIDATION",
        "status": "PASS_6_CHECK_INDEPENDENT_SELECTION_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": hashlib.sha256(RESULT.read_bytes()).hexdigest(),
        "selected_images_opened_by_validator": False,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
