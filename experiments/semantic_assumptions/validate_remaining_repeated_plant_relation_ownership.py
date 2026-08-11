#!/usr/bin/env python3
"""Independent source reconstruction of the remaining-relation ownership stop."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "REMAINING_REPEATED_PLANT_RELATION_OWNERSHIP_METHOD.md"
PRODUCER = BASE / "audit_remaining_repeated_plant_relation_ownership.py"
PAIRS = BASE / "cache" / "existing_human_annotations" / "stolfi_2025_internal_plant_pairs.tsv"
PAGES = RESULTS / "existing_human_page_annotations.tsv"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
LINES = ROOT / "transcription" / "voynich_stolfi25e1_lines.tsv"
FIVE = RESULTS / "five_pair_ordered_multiroot_capacity.json"
RESULT = RESULTS / "remaining_repeated_plant_relation_ownership.json"
REPORT = RESULTS / "remaining_repeated_plant_relation_ownership_report.md"
OUT = RESULTS / "remaining_repeated_plant_relation_ownership_validation.json"
OUT_MD = RESULTS / "remaining_repeated_plant_relation_ownership_validation_report.md"
IMAGE_URL = "https://collections.library.yale.edu/iiif/2/1006234/full/full/0/default.jpg"
HASHES = {
    PAIRS: "53248c1ab2a50ec43a56ecee0bb22478a890a00f38671c75882620d8c5d28230",
    PAGES: "b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa",
    EXACT: "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    LINES: "b4c83c18f8f814e547ab4a849dab8cf24188680fc512d9497885bdaa0d944988",
    FIVE: "9a2ae3bc0da47d8779066b30ffa098dd7ddea2f479caffb97d6dd2fe3d684415",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-native-visual-validator/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def expected_report(status: str) -> str:
    return (
        "# Remaining repeated-plant relation ownership\n\n"
        f"Status: **{status}**.\n\n"
        "All four unused good Herbal↔pharmaceutical relations fail singular label ownership. "
        "f102r1 row 3/item 2 has no second plant label; f102r2 row 1/items 1 and 2 are followed "
        "by paragraph text rather than individual plant labels; and the only plausible f89v2 "
        "row 3/item 4 inscription is explicitly between items 3 and 4. Direct inspection of the "
        "exact official image confirms open-whitespace proximity, not writing inside item 4.\n\n"
        "The recovered 2025 table therefore supplies no sixth singularly owned relation. Do not "
        "reopen the five-pair exact-root test from these candidates. No plant name, word, sound, "
        "language, cipher, plaintext, meaning, or translation follows.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise RuntimeError("refusing to overwrite remaining-relation validation")
    checks: list[str] = []
    for path, digest in HASHES.items():
        if sha(path.read_bytes()) != digest:
            raise RuntimeError(("input hash", path))
    checks.append("frozen_local_sources")

    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    if any(
        isinstance(node, ast.ImportFrom) and node.module and "validate_remaining" in node.module
        for node in ast.walk(tree)
    ):
        raise RuntimeError("producer imports validator")
    checks.append("nonimporting_independence")

    pair_rows = {row["relation_id"]: row for row in table(PAIRS)}
    ids = ("JSP2025_01", "JSP2025_06", "JSP2025_07", "JSP2025_08")
    if any(pair_rows[key]["match_kind"] != "GOOD_HERBAL_PHARMA" for key in ids):
        raise RuntimeError("relation type")
    checks.append("remaining_human_relations")

    pages = {row["page"]: row for row in table(PAGES)}
    if "1 label of a plant fragment" not in pages["f102r1"]["text_description"]:
        raise RuntimeError("f102r1 description")
    if "2 labels of plant fragments" not in pages["f102r2"]["text_description"]:
        raise RuntimeError("f102r2 description")
    checks.append("page_label_counts")

    lines = table(LINES)
    f102r1 = [row for row in lines if row["page"] == "f102r1" and row["code"] == "@Lf"]
    f102r2 = [row for row in lines if row["page"] == "f102r2" and row["code"] == "@Lf"]
    if len(f102r1) != 1 or {row["old_locus"] for row in f102r2} != {"f102r2.L3.1", "f102r2.L3.2"}:
        raise RuntimeError("line metadata")
    checks.append("current_label_inventory")

    exact = {row["locus"]: row for row in table(EXACT)}
    if "Between plants <f89v2>[3,3] and <f89v2>[3,4]" not in exact["f89v2.28"]["local_comment"]:
        raise RuntimeError("between-plant relation")
    checks.append("f89_between_plant_source")

    image = fetch(IMAGE_URL)
    image_hash = sha(image)
    if image_hash != "b6b0dd8ba7cd316f3b09a8b156d1eed0eb36ad8ec9086b975969f4f8f7dd5406":
        raise RuntimeError("image hash")
    checks.append("live_official_image")

    candidates = [
        {"relation_id": "JSP2025_01", "herbal_page": "f1v", "pharma_page": "f102r1", "row": 3, "item": 2, "status": "NO_INDIVIDUAL_LABEL", "basis": "The page has one plant-fragment label, already fixed to row 3/item 1."},
        {"relation_id": "JSP2025_06", "herbal_page": "f32v", "pharma_page": "f102r2", "row": 1, "item": 2, "status": "NO_INDIVIDUAL_LABEL", "basis": "The only two plant-fragment labels are f102r2 row 3/items 1 and 2."},
        {"relation_id": "JSP2025_07", "herbal_page": "f47v", "pharma_page": "f102r2", "row": 1, "item": 1, "status": "NO_INDIVIDUAL_LABEL", "basis": "The only two plant-fragment labels are f102r2 row 3/items 1 and 2."},
        {"relation_id": "JSP2025_08", "herbal_page": "f48r", "pharma_page": "f89v2", "row": 3, "item": 4, "status": "PROXIMITY_ONLY", "candidate_locus": "f89v2.28", "basis": "The source places the inscription between items 3 and 4; the official image shows it in open whitespace rather than inside item 4."},
    ]
    input_hashes = {str(METHOD.relative_to(ROOT)): sha(METHOD.read_bytes())}
    input_hashes.update({str(path.relative_to(ROOT)): digest for path, digest in HASHES.items()})
    claim = "The four unused good relations in the recovered 2025 table supply no sixth singularly owned pharmaceutical label. This closes only that acquisition route and supplies no plant name, word, sound, language, cipher, plaintext, meaning, or translation."
    expected = {
        "experiment": "REMAINING_REPEATED_PLANT_RELATION_OWNERSHIP",
        "status": "STOP_NO_SIXTH_SINGULARLY_OWNED_RELATION",
        "decision": "CLOSE_RECOVERED_2025_TABLE_ACQUISITION_ROUTE",
        "candidates": candidates,
        "official_image": {"canvas_id": "1006234", "image_url": IMAGE_URL, "sha256": image_hash, "width": 4204, "height": 3809, "review_region": "BOTTOM_PLANT_ROW"},
        "native_visual_observation": {
            "machine_authored_source_bound_observation": True,
            "f89v2_row3_item4_grade": "PROXIMITY_ONLY",
            "description": "The inscription nearest the far-right bottom-row fragment remains in open whitespace between the third and fourth fragments; it does not run inside or directly across the fourth fragment body.",
            "ocr_or_transcription_used": False,
            "automated_vision_embedding_or_similarity_used": False,
        },
        "gates": {
            "four_remaining_good_relations_exact": True,
            "f102r1_has_candidate_item2_label": False,
            "f102r2_row1_has_individual_labels": False,
            "f89v2_item4_has_singular_direct_ownership": False,
            "any_sixth_relation_admitted": False,
            "label_surfaces_accessed": False,
            "ocr_or_automated_vision_used": False,
        },
        "inputs": input_hashes,
        "claim_ceiling": claim,
    }
    result_bytes = RESULT.read_bytes()
    if result_bytes != canonical(expected):
        raise RuntimeError("canonical result mismatch")
    checks.append("canonical_result")
    if REPORT.read_text(encoding="utf-8") != expected_report(expected["status"]):
        raise RuntimeError("report mismatch")
    checks.append("exact_report")

    validation = {
        "experiment": "REMAINING_REPEATED_PLANT_RELATION_OWNERSHIP_VALIDATION",
        "status": "PASS_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "validated_result_sha256": sha(result_bytes),
        "producer_sha256": sha(PRODUCER.read_bytes()),
        "reconstructed": {"remaining_candidates": 4, "admitted_relations": 0, "image_sha256": image_hash},
        "visual_judgment_reclassified_by_validator": False,
        "claim_ceiling": claim,
    }
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(
        "# Remaining repeated-plant relation ownership validation\n\n"
        "Status: **PASS_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION**.\n\n"
        f"All {len(checks)} checks pass. Independent code reconstructs the four unused good "
        "relations, the f102r1/f102r2 plant-label inventories, the f89v2 between-plant source "
        "comment, the official image hash, and the canonical stop result. The validator binds "
        "but does not reclassify the machine-authored visual judgment.\n\n"
        "No plant name, word, sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
