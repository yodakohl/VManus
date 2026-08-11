#!/usr/bin/env python3
"""Validate provenance and metadata for the f102r1 fifth-pair visual observation."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
PAIR_SOURCE = BASE / "cache/existing_human_annotations/stolfi_2025_internal_plant_pairs.tsv"
PAGES = BASE / "results/existing_human_page_annotations.tsv"
Q19 = BASE / "cache/public_voynich_nu_catalogue/q19.html"
LINES = ROOT / "transcription/voynich_stolfi25e1_lines.tsv"
PRIOR = BASE / "results/public_repeated_plant_source_native_capacity.json"
METHOD = BASE / "F102R1_FIFTH_REPEATED_PLANT_LABEL_NATIVE_VISUAL_OWNERSHIP_METHOD.md"
PRODUCER = BASE / "audit_f102r1_fifth_repeated_plant_label_native_visual_ownership.py"
RESULT = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership.json"
REPORT = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership_report.md"
OUT = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership_validation.json"
OUT_REPORT = BASE / "results/f102r1_fifth_repeated_plant_label_native_visual_ownership_validation_report.md"
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006251/full/full/0/default.jpg"
IMAGE_SHA = "30fd529fc6bf8999d5be48024ee6a1676af55e8d66dc0a4f77993fe2565e9d94"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False) + "\n").encode()


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    if data[:2] != b"\xff\xd8":
        raise ValueError("not JPEG")
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
           0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            continue
        length = int.from_bytes(data[offset:offset + 2], "big")
        if marker in sof:
            height = int.from_bytes(data[offset + 3:offset + 5], "big")
            width = int.from_bytes(data[offset + 5:offset + 7], "big")
            return width, height
        offset += length
    raise ValueError("JPEG SOF not found")


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite f102r1 ownership validation")
    checks = []
    expected = {
        PAIR_SOURCE: "53248c1ab2a50ec43a56ecee0bb22478a890a00f38671c75882620d8c5d28230",
        PAGES: "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
        Q19: "119fe32a005723833ec07a313fd87e1cd044a1f685ddd4fdd199e573c1dff1fb",
        LINES: "b4c83c18f8f814e547ab4a849dab8cf24188680fc512d9497885bdaa0d944988",
        PRIOR: "a16700eafc88653c3b95f8fcd840a4c86a185ca240a0e19123e880a46373cb2e",
    }
    for path, value in expected.items():
        assert sha(path) == value
    checks.append("frozen_local_sources")

    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    keys = {node.slice.value for node in ast.walk(tree)
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)}
    assert not keys.intersection({"clean_text", "raw_text", "word_count", "family_surface",
                                  "zl_sta_expression", "it_sta_expression", "rf_sta_expression"})
    checks.append("producer_label_identity_static_seal")

    with PAIR_SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 12
    relation = next(row for row in rows if row["relation_id"] == "JSP2025_05")
    assert (relation["first_page"], relation["second_page_current"],
            relation["second_row"], relation["second_item"], relation["match_kind"],
            relation["root_copied"], relation["leaves_copied"], relation["flower_copied"]) == (
                "f37v", "f102r1", "3", "1", "GOOD_HERBAL_PHARMA", "1", "1", "0")
    checks.append("human_relation_exact")

    with PAGES.open(encoding="utf-8", newline="") as handle:
        page = next(row for row in csv.DictReader(handle, delimiter="\t")
                    if row["page"] == "f102r1")
    assert "1 label of a plant fragment" in page["text_description"]
    assert "There are 4 labels in total" in page["text_description"]
    checks.append("human_page_label_counts")

    found = []
    current = None
    for line in Q19.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.search(r'<TH CLASS="Ph" ID="([^"]+)">', line, re.I)
        if match:
            current = match.group(1)
        match = re.search(r"child_oid=([0-9]+)", line)
        if current == "f102r1" and match:
            found.append(match.group(1))
    assert found == ["1006251"]
    checks.append("official_canvas_mapping")

    with LINES.open(encoding="utf-8", newline="") as handle:
        label_metadata = [(row["locus"], row["old_locus"], row["code"])
                          for row in csv.DictReader(handle, delimiter="\t")
                          if row["page"] == "f102r1" and row["code"] == "@Lf"]
    assert label_metadata == [("f102r1.2", "f102r1.L1.1", "@Lf")]
    checks.append("unique_current_plant_label_metadata")

    request = urllib.request.Request(IMAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        assert response.status == 200
        assert response.geturl() == IMAGE_URL
        image = response.read()
    assert hashlib.sha256(image).hexdigest() == IMAGE_SHA
    assert jpeg_dimensions(image) == (8176, 3864)
    checks.append("live_official_image_hash_and_dimensions")

    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    assert prior["capacity"]["relations"] == 4
    checks.append("prior_four_pair_panel")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert RESULT.read_bytes() == canonical(result)
    assert result["status"] == "PASS_PROVISIONAL_NATIVE_VISUAL_SINGULAR_DIRECT_INTERIOR_OWNERSHIP"
    assert result["decision"] == "REOPEN_FIVE_PAIR_SCORE_BLIND_CAPACITY_AND_DESIGN_ONLY"
    assert result["label_binding"]["current_locus"] == "f102r1.2"
    assert result["label_binding"]["label_surface_accessed"] is False
    assert result["official_image"]["sha256"] == IMAGE_SHA
    assert result["capacity_change"] == {"previous_strongly_owned_relations": 4,
                                         "new_relations_added": 1,
                                         "current_strongly_owned_relations": 5}
    assert result["native_visual_observation"]["machine_authored_source_bound_observation"] is True
    checks.append("canonical_result_and_claim_scope")

    report = REPORT.read_text(encoding="utf-8")
    assert "characters remain sealed" in report
    assert "score-blind capacity/design audit" in report
    checks.append("report_ceiling")

    validation = {
        "experiment": "F102R1_FIFTH_REPEATED_PLANT_LABEL_NATIVE_VISUAL_OWNERSHIP_VALIDATION",
        "status": "PASS_INDEPENDENT_SOURCE_AND_IMAGE_PROVENANCE_RECONSTRUCTION",
        "validated_result_sha256": sha(RESULT), "check_count": len(checks),
        "checks": checks,
        "reconstructed": {"relation_id": "JSP2025_05", "canvas_id": "1006251",
                            "image_sha256": IMAGE_SHA, "image_width": 8176,
                            "image_height": 3864, "plant_label_locus": "f102r1.2",
                            "previous_relations": 4, "current_relations": 5},
        "visual_judgment_reclassified_by_validator": False,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_bytes(canonical(validation))
    OUT_REPORT.write_text(
        "# f102r1 fifth repeated-plant ownership validation\n\n"
        "Status: **PASS_INDEPENDENT_SOURCE_AND_IMAGE_PROVENANCE_RECONSTRUCTION**\n\n"
        f"All **{len(checks)}** checks pass. Independent code reconstructs the exact human "
        "f37v↔f102r1 row-3/item-1 relation, the one-plant-label page description, the unique "
        "current `@Lf` locus `f102r1.2`, the prior four-pair count, and the live official "
        "8176×3864 JPEG byte hash. Static inspection confirms that the producer never reads "
        "the label surface.\n\n"
        "The validator binds the image and metadata; it does not convert the machine-authored "
        "visual ownership judgment into human annotation. The result authorizes only a new "
        "score-blind five-pair capacity/design audit and supplies no plant name, word, sound, "
        "language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
