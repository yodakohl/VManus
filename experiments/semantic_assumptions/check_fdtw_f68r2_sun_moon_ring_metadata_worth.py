#!/usr/bin/env python3
"""Cheap text-only worth check for FDTW f68r2 Sun--Moon ring comparanda."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "FDTW_F68R2_SUN_MOON_RING_METADATA_WORTH_CHECK_SPEC.md"
FDTW = RESULTS / "fdtw_f57_homologue_metadata_prescreen.tsv"
FDTW_VALIDATION = RESULTS / "fdtw_f57_homologue_metadata_prescreen_validation.json"
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q09.html"
F68_VALIDATION = RESULTS / "f68r2_sun_ring_cleartext_validation.md"
ANCHOR_REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
OUT_JSON = RESULTS / "fdtw_f68r2_sun_moon_ring_metadata_worth.json"
OUT_REPORT = RESULTS / "fdtw_f68r2_sun_moon_ring_metadata_worth_report.md"

TERM_PATTERNS = {
    "circle": re.compile(r"\b(wheel|rota|circular|circle|circles|roundel|concentric)\b", re.I),
    "sun": re.compile(r"\b(sun|sunlight)\b", re.I),
    "moon": re.compile(r"\b(moon|moonlight)\b", re.I),
    "star": re.compile(r"\b(star|stars|constellation|constellations)\b", re.I),
}
TOPOLOGY_PATTERNS = {
    "separate_top_moon_and_bottom_sun_medallions": re.compile(
        r"\b(top|upper|above)\b[^.]{0,180}\bmoon\b[^.]{0,180}\b(bottom|lower|below)\b[^.]{0,180}\bsun\b", re.I
    ),
    "star_circle_connects_medallions": re.compile(
        r"\b(circle|ring)\b[^.]{0,180}\bstars?\b[^.]{0,180}\b(connects?|connecting|joins?|joining)\b"
        r"[^.]{0,180}\bsun\b[^.]{0,180}\bmoon\b", re.I
    ),
    "interior_stars_are_labelled": re.compile(
        r"\b(inside|interior)\b[^.]{0,180}\bstars?\b[^.]{0,180}\b(labels?|labelled|labeled)\b", re.I
    ),
    "separate_owned_circular_text_at_both_medallions": re.compile(
        r"\bcircular (text|writing|inscription)\b[^.]{0,180}\bmoon\b[^.]{0,180}\bsun\b", re.I
    ),
    "readable_one_to_one_label_relation": re.compile(
        r"\b(readable|transcribed|identified|named)\b[^.]{0,180}\b(labels?|inscriptions?|text)\b", re.I
    ),
}
EXPECTED_IDS = (
    "5bd37226-d246-4e4a-a3cf-f56bb165afda",
    "73e8cb2e-74d6-4c31-94b0-d585718e2953",
    "20c9ff3b-8d5d-48a6-84f7-70891f1ed906",
    "65009837-8ae0-4c22-a992-e7d5c61e004d",
    "221915f0-dc11-4095-afde-4c5f37915634",
)
F68_PHRASES = (
    "near the top is a moon face and near the bottom a sun face",
    "large circle of unlabeled stars connecting sun and moon",
    "area inside this is also filled up with stars",
    "most (but not all) have a label",
    "two pieces of circular text, one around the moon and one around the sun",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def flags(row: dict[str, str]) -> dict[str, bool]:
    searchable = " ".join(row[key] for key in ("label", "description", "archetype", "theme"))
    return {name: bool(pattern.search(searchable)) for name, pattern in TERM_PATTERNS.items()}


def topology_flags(row: dict[str, str]) -> dict[str, bool]:
    description = re.sub(r"\s+", " ", row["description"])
    return {name: bool(pattern.search(description)) for name, pattern in TOPOLOGY_PATTERNS.items()}


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite f68r2 worth-check outputs")
    with FDTW.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 263 or len({row["manifest_id"] for row in rows}) != 263:
        raise ValueError("FDTW projection inventory drift")
    validation = json.loads(FDTW_VALIDATION.read_text(encoding="utf-8"))
    if validation.get("status") != "PASS_INDEPENDENT_LIVE_METADATA_RECONSTRUCTION":
        raise ValueError("FDTW source validation drift")
    selected: list[dict[str, object]] = []
    for row in rows:
        row_flags = flags(row)
        if all(row_flags.values()):
            relation_flags = topology_flags(row)
            selected.append({
                "source_order": int(row["source_order"]),
                "manifest_id": row["manifest_id"],
                "manifest_sha256": row["manifest_sha256"],
                "label": row["label"],
                "manuscript_number": row["manuscript_number"],
                "century": row["century"],
                "theme": row["theme"],
                "term_flags": row_flags,
                "topology_flags": relation_flags,
                "exact_topology_metadata_candidate": all(relation_flags.values()),
            })
    if tuple(str(row["manifest_id"]) for row in selected) != EXPECTED_IDS:
        raise ValueError("broad candidate identity drift")
    exact_candidates = [row for row in selected if row["exact_topology_metadata_candidate"]]
    if exact_candidates:
        raise ValueError("exact topology metadata candidate requires separate escalation")

    catalogue = CATALOGUE.read_text(encoding="utf-8")
    catalogue_text = re.sub(r"\s+", " ", catalogue).casefold()
    f68_phrase_checks = {phrase: phrase in catalogue_text for phrase in F68_PHRASES}
    if not all(f68_phrase_checks.values()):
        raise ValueError("f68r2 human topology description drift")
    if "not a readable plaintext anchor" not in F68_VALIDATION.read_text(encoding="utf-8"):
        raise ValueError("F68CL001 state drift")
    registry = ANCHOR_REGISTRY.read_text(encoding="utf-8")
    if "f67r_f68r_historical_homologue_search\tSTOP_NO_EXACT_LABELLED_SLOT_HOMOLOGUE_FOUND" not in registry:
        raise ValueError("historical route state drift")

    result = {
        "experiment": "FDTW_F68R2_SUN_MOON_RING_METADATA_WORTH_CHECK",
        "status": "PASS_COMPLETE_TEXT_ONLY_METADATA_WORTH_CHECK",
        "decision": "STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_ZERO_EXACT_TOPOLOGY_METADATA_CANDIDATES",
        "counts": {
            "fdtw_rows": len(rows),
            "broad_sun_moon_circle_star_rows": len(selected),
            "exact_topology_metadata_candidates": len(exact_candidates),
        },
        "broad_candidates": selected,
        "f68r2_human_topology_phrase_checks": f68_phrase_checks,
        "escalation_requirements": list(TOPOLOGY_PATTERNS),
        "source_access": {
            "manuscript_images_opened": False,
            "thumbnails_or_canvases_opened": False,
            "papers_or_pdfs_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_or_historical_word_lists_opened": False,
        },
        "inputs": {
            str(SPEC.relative_to(BASE)): sha_file(SPEC),
            str(FDTW.relative_to(BASE)): sha_file(FDTW),
            str(FDTW_VALIDATION.relative_to(BASE)): sha_file(FDTW_VALIDATION),
            str(CATALOGUE.relative_to(BASE)): sha_file(CATALOGUE),
            str(F68_VALIDATION.relative_to(BASE)): sha_file(F68_VALIDATION),
            str(ANCHOR_REGISTRY.relative_to(BASE)): sha_file(ANCHOR_REGISTRY),
        },
        "claim_ceiling": "Five broad human-metadata comparanda are retained, but zero metadata row describes the complete f68r2 paired-medallion, connecting-star-ring, internally labelled-star, owned-circular-text topology; no object, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# FDTW f68r2 Sun--Moon ring metadata worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_ZERO_EXACT_TOPOLOGY_METADATA_CANDIDATES**.\n\n"
        "The complete validated 263-row FDTW metadata projection contains five broad descriptions that mention "
        "a circle or concentric scheme together with the Sun, Moon, and stars or constellations. They are a "
        "computus *Horologium*, a geocentric-spheres diagram, two element/celestial schemes, and a creation miniature.\n\n"
        "None of the five human-authored descriptions states the complete f68r2 relation: separate upper Moon and lower Sun "
        "medallions, a star circle connecting them, labelled stars inside it, and separately owned circular text around both "
        "medallions. They therefore remain broad comparanda and do not justify image or paper review as translation anchors.\n\n"
        "This is a catalogue-metadata no-find, not proof that no matching manuscript exists. No image, thumbnail, canvas, paper, "
        "PDF, OCR, automated visual output, decoder claim, or historical word list entered the result. No object, label, word, "
        "sound, language, cipher, plaintext, meaning, or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
