#!/usr/bin/env python3
"""Independent reconstruction of the apparatus-caption worth stop."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
METHOD = BASE / "APPARATUS_COMPONENT_CAPTION_CAPACITY_METHOD.md"
PRODUCER = BASE / "audit_apparatus_component_caption_capacity.py"
ANNOTATIONS = RESULTS / "existing_human_exact_locus_annotations.tsv"
RESULT = RESULTS / "apparatus_component_caption_capacity.json"
REPORT = RESULTS / "apparatus_component_caption_capacity_report.md"
OUT = RESULTS / "apparatus_component_caption_capacity_validation.json"
OUT_MD = RESULTS / "apparatus_component_caption_capacity_validation_report.md"
ANNOTATION_SHA = "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61"
IMAGES = {
    "f77v": ("1006213", "e2e2f629753bfe6a9c111d8157ac63cfc4524966cbf367ddaaffece07cffdab2", 2861, 3697),
    "f78r": ("1006214", "0054f691ac8fddcac324fba6b385f8ad578cd0f2f9879d5498a325bab0310893", 2793, 3761),
    "f80r": ("1006218", "81223a0b0aa0a24fe821cf62a9bdf4ac504f222ab3cfcb89fcedd7946bceada0", 2793, 3733),
    "f81v": ("1006221", "bb1a2316e7fc2966f5761f591d79339c75dcfbc6c2c9ab2b88a37e800266d4bf", 2835, 3705),
    "f82r": ("1006222", "269cb42307824ab82764f80009429e58d98c649371d8efe10d2a1f54132a21ef", 2753, 3745),
    "f82v": ("1006223", "4c86853e2d6e62690ec0106dcc3812c95f009022b06e7edfd347386728003142", 2821, 3709),
    "f85v2": ("1006231", "4b08afeee514691b0a511099ca299aed544d6fd1782b7dee8df163dfc06354ed", 7925, 7268),
}
FAMILIES = {"TUBE_PIPE_CHANNEL": r"\btube|\bpipe|\bchannel", "TUB_CONTAINER": r"\btub\b|\bbarrel\b|\bcontainer", "POOL_POND": r"\bpool\b|\bpond\b", "STREAM_OUTFLOW": r"\bstream\b|\boutflow|\binflow|\bwaterfall"}
SINGULAR = {"f77v.45": ("TUB_CONTAINER", "ONE_TUB_LOCAL"), "f78r.45": ("TUBE_PIPE_CHANNEL", "ONE_PIPE_SEGMENT_LOCAL"), "f82r.10": ("TUBE_PIPE_CHANNEL", "ONE_CROSS_SHAPED_TUBE_LOCAL"), "f82v.3": ("POOL_POND", "ONE_POOL_LOCAL")}


def sha(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def canonical(value: object) -> bytes: return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def fetch(canvas: str) -> bytes:
    req = urllib.request.Request(f"https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg", headers={"User-Agent": "VManus-native-visual-validator/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response: return response.read()


def main() -> None:
    if OUT.exists() or OUT_MD.exists(): raise RuntimeError("refusing to overwrite validation")
    checks = []
    if sha(ANNOTATIONS.read_bytes()) != ANNOTATION_SHA: raise RuntimeError("annotation hash")
    checks.append("human_annotation_source_hash")
    if any(isinstance(n, ast.ImportFrom) and n.module and "validate_apparatus" in n.module for n in ast.walk(ast.parse(PRODUCER.read_text()))): raise RuntimeError("producer imports validator")
    checks.append("nonimporting_independence")
    with ANNOTATIONS.open(newline="", encoding="utf-8") as handle: rows = list(csv.DictReader(handle, delimiter="\t"))
    eligible = [r for r in rows if "WATER_OR_APPARATUS" in r["object_tags"] and "LABEL" in r["object_tags"] and r["certainty"] == "UNHEDGED" and "REL_EXPLICIT_ATTACHMENT" in (r["local_relation_tags"] + ";" + r["unit_relation_tags"])]
    if (len(eligible), len({r["page"] for r in eligible})) != (14, 7): raise RuntimeError("eligible counts")
    checks.append("eligible_panel_14_rows_7_pages")
    family_rows = {name: [] for name in FAMILIES}
    for row in eligible:
        text = (row["unit_description"] + " " + row["local_comment"]).lower()
        for name, pattern in FAMILIES.items():
            if re.search(pattern, text): family_rows[name].append(row["locus"])
    counts = {k: len(v) for k, v in family_rows.items()}
    if counts != {"TUBE_PIPE_CHANNEL": 5, "TUB_CONTAINER": 3, "POOL_POND": 3, "STREAM_OUTFLOW": 4}: raise RuntimeError("family counts")
    checks.append("fixed_keyword_family_counts")
    images = {}
    for page, (canvas, digest, width, height) in IMAGES.items():
        if sha(fetch(canvas)) != digest: raise RuntimeError(("image", page))
        images[page] = {"canvas_id": canvas, "sha256": digest, "width": width, "height": height, "image_url": f"https://collections.library.yale.edu/iiif/2/{canvas}/full/full/0/default.jpg"}
    checks.append("seven_official_image_hashes")
    observations = [{"locus": locus, "family": family, "grade": grade, "singular": True} for locus, (family, grade) in SINGULAR.items()]
    folios = {name: len({next(r["page"] for r in eligible if r["locus"] == locus) for locus, (family, _) in SINGULAR.items() if family == name}) for name in FAMILIES}
    if folios != {"TUBE_PIPE_CHANNEL": 2, "TUB_CONTAINER": 1, "POOL_POND": 1, "STREAM_OUTFLOW": 0}: raise RuntimeError("singular folios")
    checks.append("maximum_two_singular_folios")
    claim = "No repeated apparatus-component class has three physical folios with singular ownership, so no component-caption text test is warranted. No component name, word, sound, language, cipher, plaintext, meaning, or translation follows."
    expected = {"experiment": "APPARATUS_COMPONENT_CAPTION_CAPACITY", "status": "STOP_NO_THREE_FOLIO_SINGULAR_COMPONENT_CLASS", "decision": "DO_NOT_OPEN_APPARATUS_TEXT_FEATURE_ASSOCIATION", "eligible_rows": 14, "eligible_pages": 7, "keyword_family_row_counts": counts, "generous_singular_observations": observations, "singular_physical_folios_by_family": folios, "maximum_singular_physical_folios": 2, "worth_gate": {"required_physical_folios": 3, "passed": False}, "official_images": images, "inputs": {str(ANNOTATIONS.relative_to(ROOT)): ANNOTATION_SHA, str(METHOD.relative_to(ROOT)): sha(METHOD.read_bytes())}, "access": {"voynich_label_strings_accessed": False, "formal_features_accessed": False, "ocr_or_automated_vision_used": False, "machine_authored_native_visual_inspection": True}, "claim_ceiling": claim}
    result_bytes = RESULT.read_bytes()
    if result_bytes != canonical(expected): raise RuntimeError("canonical result")
    checks.append("canonical_result")
    expected_report = "# Apparatus-component caption capacity\n\nStatus: **STOP_NO_THREE_FOLIO_SINGULAR_COMPONENT_CLASS**.\n\nThe human layer supplies 14 unhedged apparatus-label rows on seven pages, but most repeated component descriptions are between/near multiple objects or mix component kinds. Under a deliberately generous source-bound singular grade, the largest repeated component class reaches only two physical folios.\n\nThis is below the frozen three-folio worth gate, so no Voynich string or formal feature association was opened. No component name, word, sound, language, cipher, plaintext, meaning, or translation follows.\n"
    if REPORT.read_text() != expected_report: raise RuntimeError("report")
    checks.append("exact_report")
    validation = {"experiment": "APPARATUS_COMPONENT_CAPTION_CAPACITY_VALIDATION", "status": "PASS_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION", "check_count": len(checks), "checks": checks, "validated_result_sha256": sha(result_bytes), "producer_sha256": sha(PRODUCER.read_bytes()), "reconstructed": {"eligible_rows": 14, "eligible_pages": 7, "maximum_singular_physical_folios": 2, "target_features_opened": 0}, "visual_judgment_reclassified_by_validator": False, "claim_ceiling": claim}
    OUT.write_bytes(canonical(validation))
    OUT_MD.write_text(f"# Apparatus-component caption capacity validation\n\nStatus: **PASS_INDEPENDENT_SOURCE_AND_IMAGE_RECONSTRUCTION**.\n\nAll {len(checks)} checks pass. Independent code reconstructs the human-tagged capacity panel, fixed keyword families, seven exact official image bindings, canonical stop, and report. It binds but does not reclassify the machine visual judgments.\n\nNo component name, word, sound, language, cipher, plaintext, meaning, or translation follows.\n")


if __name__ == "__main__": main()
