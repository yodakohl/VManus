#!/usr/bin/env python3
"""Independent live reconstruction of the OMCI special-circle prescreen."""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "OMCI_SPECIAL_CIRCLE_METADATA_PRESCREEN_SPEC.md"
PRODUCER = BASE / "check_omci_special_circle_metadata_prescreen.py"
RESULT = RESULTS / "omci_special_circle_metadata_prescreen.json"
REPORT = RESULTS / "omci_special_circle_metadata_prescreen_report.md"
OUT_JSON = RESULTS / "omci_special_circle_metadata_prescreen_validation.json"
OUT_REPORT = RESULTS / "omci_special_circle_metadata_prescreen_validation_report.md"
URL = "https://omci.inha.fr/api/items?per_page=1000&sort_by=id&sort_order=asc&page=1"
FROZEN = {
    SPEC: "e46474703ed0c225d93cebf8aa46bd012396b6e783da7a7b1ba769b3e2311ccc",
    PRODUCER: "c697735266aee89703cf881fdff31695cd9b5770f5450257da3c00a26d446a32",
    RESULT: "52bde0a99c9f8d4a1ae4d86ce199f69fee001b9b98408654762b750a992fe82c",
    REPORT: "aa53d1ee69f33cfad5f89a8ead9ab30b0988dbcffced82b41137f42e6b98cdc8",
}
FIELDS = ("dcterms:description", "dcterms:isPartOf", "dcterms:provenance", "bibo:locator", "bibo:number", "dcterms:date")
FILTERS = {
    "F57_FOURFOLD_CIRCLE": (r"quatre|four", r"élément|element|saison|season|humeur|humor|qualit|quality", r"cercle|circle|roue|wheel|rosace|diagram"),
    "F68_SUN_MOON_STAR_RING": (r"soleil|sun", r"lune|moon", r"étoil|star|astre", r"cercle|circle|anneau|ring|médaillon|medallion"),
    "F67_WIND_FACE_CIRCLE": (r"vent|wind", r"visage|face|tête|head|personn", r"cercle|circle|roue|wheel|rose|diagram"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def strict_json(path: Path) -> object:
    raw = path.read_bytes()
    def hook(items: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        return dict(items)
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=hook, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if canonical(value) != raw:
        raise ValueError("noncanonical JSON")
    return value


def fetch() -> list[dict[str, object]]:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-OMCI-metadata-prescreen-validator/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected OMCI response")
        value = json.loads(response.read().decode("utf-8"), parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError("unexpected API schema")
    return value


def literals(row: dict[str, object], field: str) -> list[str]:
    values = row.get(field, [])
    if not isinstance(values, list):
        raise ValueError("literal list drift")
    return [value["@value"] for value in values if isinstance(value, dict) and isinstance(value.get("@value"), str)]


def rebuild(items: list[dict[str, object]]) -> list[dict[str, object]]:
    ids = [row.get("o:id") for row in items]
    if len(items) != 917 or ids != sorted(ids) or len(ids) != len(set(ids)):
        raise ValueError("item orbit drift")
    rows = []
    for item in items:
        resource_class = item.get("o:resource_class")
        if not isinstance(resource_class, dict) or resource_class.get("o:id") != 365:
            continue
        item_id, title = item.get("o:id"), item.get("o:title")
        if type(item_id) is not int or not isinstance(title, str):
            raise ValueError("illustration schema drift")
        row = {"item_id": item_id, "title": title}
        for field in FIELDS:
            row[field] = literals(item, field)
        rows.append(row)
    if len(rows) != 243:
        raise ValueError("illustration count drift")
    return rows


def text(row: dict[str, object]) -> str:
    source = " ".join([str(row["title"]), *[str(value) for value in row["dcterms:description"]]])
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(source))).strip().lower()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite OMCI validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = strict_json(RESULT)
    if not isinstance(result, dict):
        raise ValueError("result type drift")
    checks.append("canonical_duplicate_free_result")
    rows = rebuild(fetch())
    checks.extend(("live_official_api", "917_unique_ordered_items", "243_illustration_rows", "literal_text_projection_only"))
    hits = {
        name: [{"item_id": row["item_id"], "title": row["title"], "public_item_url": f"https://omci.inha.fr/s/ocmi/item/{row['item_id']}"}
               for row in rows if all(re.search(pattern, text(row), re.IGNORECASE) for pattern in patterns)]
        for name, patterns in FILTERS.items()
    }
    if [row["item_id"] for row in hits["F57_FOURFOLD_CIRCLE"]] != [935] or hits["F68_SUN_MOON_STAR_RING"] or hits["F67_WIND_FACE_CIRCLE"]:
        raise ValueError("filter result drift")
    checks.extend(("f57_only_item_935", "f68_zero_hits", "f67_zero_hits"))
    altered = dict(FILTERS)
    altered["F57_FOURFOLD_CIRCLE"] = (*FILTERS["F57_FOURFOLD_CIRCLE"], r"four persons exact")
    altered_hits = [row for row in rows if all(re.search(pattern, text(row), re.IGNORECASE) for pattern in altered["F57_FOURFOLD_CIRCLE"])]
    if altered_hits:
        raise ValueError("filter conjunction mutation failed")
    checks.append("filter_conjunction_mutation")
    expected = {
        "experiment": "OMCI_SPECIAL_CIRCLE_METADATA_PRESCREEN",
        "status": "PASS_COMPLETE_243_ILLUSTRATION_TEXT_SCREEN",
        "decision": "STOP_BEFORE_MEDIA_OR_BIBLIOGRAPHY_REVIEW_ONLY_F57_HIT_IS_ALREADY_CONSUMED_HARLEY_3099",
        "source": {"url": URL, "publisher": "OMCI - INHA", "all_item_count": 917, "illustration_resource_class_id": 365, "illustration_count": 243, "canonical_text_projection_sha256": sha(canonical(rows))},
        "filters": {name: list(patterns) for name, patterns in FILTERS.items()},
        "hits": hits, "hit_counts": {name: len(value) for name, value in hits.items()},
        "gates": {"complete_public_item_page_loaded": True, "human_literal_text_projection_only": True, "new_f57_owned_homologue_found": False, "f68_sun_moon_star_ring_metadata_candidate_found": False, "f67_wind_face_circle_metadata_candidate_found": False, "escalate_to_media_or_bibliography": False},
        "source_access": {"metadata_api_opened": True, "media_thumbnail_canvas_or_image_opened": False, "manuscripts_papers_or_pdfs_opened": False, "ocr_or_automated_visual_output_used": False, "decoder_claims_opened": False},
        "inputs": {str(SPEC.relative_to(BASE)): FROZEN[SPEC]},
        "claim_ceiling": "At human catalogue-description resolution, OMCI adds no unused owned homologue for f57v, f68r2, or f67v2; the sole f57 filter hit is the already consumed Harley MS 3099 record, and no object, direction, season, humour, quality, element, wind, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    if result != expected:
        raise ValueError("result reconstruction mismatch")
    checks.extend(("projection_digest_exact", "result_object_exact", "gate_vector_exact"))
    report = (
        "# OMCI special-circle metadata prescreen\n\n"
        "Decision: **STOP_BEFORE_MEDIA_OR_BIBLIOGRAPHY_REVIEW_ONLY_F57_HIT_IS_ALREADY_CONSUMED_HARLEY_3099**.\n\n"
        "The complete public OMCI API returned 917 unique items, including 243 illustration records. A canonical "
        "projection retained only human-written title and literal catalogue fields; media, thumbnails, linked motif "
        "labels, and image URLs were excluded before screening.\n\n"
        "The broad f57 fourfold-circle filter returns one item: OMCI 935, the already consumed Harley MS 3099 f157 "
        "diagram of sublunary mutations. The f68 Sun–Moon–star-ring and f67 wind-face-circle filters return zero. These "
        "are catalogue-description results, not proof that no matching image exists. They do show that OMCI currently "
        "supplies no new metadata candidate worth media or bibliography review for the missing ownership relation.\n\n"
        "No media, thumbnail, canvas, image, manuscript, paper, PDF, OCR, automated visual output, or decoder claim "
        "entered the screen. It supplies no object, direction, season, humour, quality, element, wind, label, word, "
        "sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != report:
        raise ValueError("report reconstruction mismatch")
    checks.append("report_bytes_exact")
    validation = {
        "experiment": "OMCI_SPECIAL_CIRCLE_METADATA_PRESCREEN_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_COMPLETE_METADATA_RECONSTRUCTION",
        "decision": result["decision"], "source_result_sha256": FROZEN[RESULT], "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()), "check_count": len(checks), "checks": checks,
        "counts": {"all_items": 917, "illustrations": 243, "f57_hits": 1, "f68_hits": 0, "f67_hits": 0},
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_bytes(canonical(validation))
    OUT_REPORT.write_text(
        "# OMCI special-circle metadata prescreen — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator live-refetches all 917 public items, independently projects "
        "243 illustration records, reapplies the three frozen text filters, and reconstructs the result and report exactly.\n\n"
        "This closes only the current OMCI catalogue-description lead before media or bibliography review. It supplies no "
        "object, direction, season, humour, quality, element, wind, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
