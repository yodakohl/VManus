#!/usr/bin/env python3
"""Complete text-only OMCI metadata prescreen for three special-circle routes."""

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
URL = "https://omci.inha.fr/api/items?per_page=1000&sort_by=id&sort_order=asc&page=1"
OUT_JSON = RESULTS / "omci_special_circle_metadata_prescreen.json"
OUT_REPORT = RESULTS / "omci_special_circle_metadata_prescreen_report.md"
LITERAL_FIELDS = (
    "dcterms:description", "dcterms:isPartOf", "dcterms:provenance",
    "bibo:locator", "bibo:number", "dcterms:date",
)
FILTERS = {
    "F57_FOURFOLD_CIRCLE": (
        r"quatre|four", r"élément|element|saison|season|humeur|humor|qualit|quality",
        r"cercle|circle|roue|wheel|rosace|diagram",
    ),
    "F68_SUN_MOON_STAR_RING": (
        r"soleil|sun", r"lune|moon", r"étoil|star|astre",
        r"cercle|circle|anneau|ring|médaillon|medallion",
    ),
    "F67_WIND_FACE_CIRCLE": (
        r"vent|wind", r"visage|face|tête|head|personn",
        r"cercle|circle|roue|wheel|rose|diagram",
    ),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def fetch() -> list[dict[str, object]]:
    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-OMCI-metadata-prescreen/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected OMCI response")
        raw = response.read()
    value = json.loads(raw.decode("utf-8"), parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError("unexpected OMCI schema")
    return value


def literal_values(row: dict[str, object], field: str) -> list[str]:
    values = row.get(field, [])
    if not isinstance(values, list):
        raise ValueError(f"non-list literal field: {field}")
    answer: list[str] = []
    for value in values:
        if not isinstance(value, dict):
            raise ValueError(f"non-object literal value: {field}")
        literal = value.get("@value")
        if isinstance(literal, str):
            answer.append(literal)
    return answer


def projection(items: list[dict[str, object]]) -> list[dict[str, object]]:
    ids = [row.get("o:id") for row in items]
    if len(items) != 917 or len(ids) != len(set(ids)) or ids != sorted(ids):
        raise ValueError("OMCI full-item guard failed")
    rows: list[dict[str, object]] = []
    for item in items:
        resource_class = item.get("o:resource_class")
        if not isinstance(resource_class, dict) or resource_class.get("o:id") != 365:
            continue
        item_id = item.get("o:id")
        title = item.get("o:title")
        if type(item_id) is not int or not isinstance(title, str):
            raise ValueError("illustration identity schema drift")
        row = {"item_id": item_id, "title": title}
        for field in LITERAL_FIELDS:
            row[field] = literal_values(item, field)
        rows.append(row)
    if len(rows) != 243:
        raise ValueError("OMCI illustration count drift")
    return rows


def screen_text(row: dict[str, object]) -> str:
    descriptions = row["dcterms:description"]
    if not isinstance(descriptions, list):
        raise ValueError("description projection drift")
    text = " ".join([str(row["title"]), *[str(value) for value in descriptions]])
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(text))).strip().lower()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite OMCI prescreen outputs")
    rows = projection(fetch())
    hits = {
        name: [
            {"item_id": row["item_id"], "title": row["title"], "public_item_url": f"https://omci.inha.fr/s/ocmi/item/{row['item_id']}"}
            for row in rows if all(re.search(pattern, screen_text(row), re.IGNORECASE) for pattern in patterns)
        ]
        for name, patterns in FILTERS.items()
    }
    if [row["item_id"] for row in hits["F57_FOURFOLD_CIRCLE"]] != [935]:
        raise ValueError("f57 screen drift")
    if hits["F68_SUN_MOON_STAR_RING"] or hits["F67_WIND_FACE_CIRCLE"]:
        raise ValueError("special-circle screen drift")
    projection_bytes = canonical(rows)
    result = {
        "experiment": "OMCI_SPECIAL_CIRCLE_METADATA_PRESCREEN",
        "status": "PASS_COMPLETE_243_ILLUSTRATION_TEXT_SCREEN",
        "decision": "STOP_BEFORE_MEDIA_OR_BIBLIOGRAPHY_REVIEW_ONLY_F57_HIT_IS_ALREADY_CONSUMED_HARLEY_3099",
        "source": {
            "url": URL,
            "publisher": "OMCI - INHA",
            "all_item_count": 917,
            "illustration_resource_class_id": 365,
            "illustration_count": 243,
            "canonical_text_projection_sha256": sha(projection_bytes),
        },
        "filters": {name: list(patterns) for name, patterns in FILTERS.items()},
        "hits": hits,
        "hit_counts": {name: len(value) for name, value in hits.items()},
        "gates": {
            "complete_public_item_page_loaded": True,
            "human_literal_text_projection_only": True,
            "new_f57_owned_homologue_found": False,
            "f68_sun_moon_star_ring_metadata_candidate_found": False,
            "f67_wind_face_circle_metadata_candidate_found": False,
            "escalate_to_media_or_bibliography": False,
        },
        "source_access": {
            "metadata_api_opened": True,
            "media_thumbnail_canvas_or_image_opened": False,
            "manuscripts_papers_or_pdfs_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_opened": False,
        },
        "inputs": {str(SPEC.relative_to(BASE)): sha(SPEC.read_bytes())},
        "claim_ceiling": "At human catalogue-description resolution, OMCI adds no unused owned homologue for f57v, f68r2, or f67v2; the sole f57 filter hit is the already consumed Harley MS 3099 record, and no object, direction, season, humour, quality, element, wind, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_bytes(canonical(result))
    OUT_REPORT.write_text(
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
        "sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
