#!/usr/bin/env python3
"""Independent live/source reconstruction of the FDTW f68r2 worth check."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "FDTW_F68R2_SUN_MOON_RING_METADATA_WORTH_CHECK_SPEC.md"
PRODUCER = BASE / "check_fdtw_f68r2_sun_moon_ring_metadata_worth.py"
FDTW = RESULTS / "fdtw_f57_homologue_metadata_prescreen.tsv"
FDTW_VALIDATION = RESULTS / "fdtw_f57_homologue_metadata_prescreen_validation.json"
CATALOGUE = BASE / "cache/public_voynich_nu_catalogue/q09.html"
F68_VALIDATION = RESULTS / "f68r2_sun_ring_cleartext_validation.md"
ANCHOR_REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
RESULT = RESULTS / "fdtw_f68r2_sun_moon_ring_metadata_worth.json"
REPORT = RESULTS / "fdtw_f68r2_sun_moon_ring_metadata_worth_report.md"
OUT_JSON = RESULTS / "fdtw_f68r2_sun_moon_ring_metadata_worth_validation.json"
OUT_REPORT = RESULTS / "fdtw_f68r2_sun_moon_ring_metadata_worth_validation_report.md"
API = "https://iiifmanifests.ifilosofia.up.pt/api/manifests/{}.json"

FROZEN = {
    SPEC: "0b46d01f0f7e0ff1f281b6fb270f8d8610dcafaeed0b0f91d5b1901b0961749b",
    PRODUCER: "fb77c87774d9516a33d8f18847bd47d620e5c3e892ce190bb344d8dddc630706",
    FDTW: "7b584ddbd184eb0e47896a2e055119cc7c2a2d133ecc15f919b4c393bb0ce091",
    FDTW_VALIDATION: "0e59feee08693c9dbcdcfbae863248740a1deeb1d463682f6f3fa22c73d9961e",
    CATALOGUE: "56b592284239fbd4d2ffabac2c534207c2e8a6da00ce4570d526544b9793f977",
    F68_VALIDATION: "6107dcab8894e42f712bc6f8c671e7b277e5a5e26afeb865c575809e8ab1fd3f",
    ANCHOR_REGISTRY: "0261d2e7856ddf26b18fe46915f66446734dcc687cc516dac4aa23c4704b7a1c",
    RESULT: "b62d73f93446b0d120b2214f3b90c412d377fc92047aa488527a59588bcc58fb",
    REPORT: "97046f9bf2cfc11b3e5197c2f446d6e066082ad2607877c391333d193542e86c",
}

BROAD = (
    ("circle", re.compile(r"\b(?:wheel|rota|circular|circle|circles|roundel|concentric)\b", re.I)),
    ("sun", re.compile(r"\b(?:sun|sunlight)\b", re.I)),
    ("moon", re.compile(r"\b(?:moon|moonlight)\b", re.I)),
    ("star", re.compile(r"\b(?:star|stars|constellation|constellations)\b", re.I)),
)
TOPOLOGY = (
    ("separate_top_moon_and_bottom_sun_medallions", re.compile(
        r"\b(?:top|upper|above)\b[^.]{0,180}\bmoon\b[^.]{0,180}\b(?:bottom|lower|below)\b[^.]{0,180}\bsun\b", re.I)),
    ("star_circle_connects_medallions", re.compile(
        r"\b(?:circle|ring)\b[^.]{0,180}\bstars?\b[^.]{0,180}\b(?:connects?|connecting|joins?|joining)\b"
        r"[^.]{0,180}\bsun\b[^.]{0,180}\bmoon\b", re.I)),
    ("interior_stars_are_labelled", re.compile(
        r"\b(?:inside|interior)\b[^.]{0,180}\bstars?\b[^.]{0,180}\b(?:labels?|labelled|labeled)\b", re.I)),
    ("separate_owned_circular_text_at_both_medallions", re.compile(
        r"\bcircular (?:text|writing|inscription)\b[^.]{0,180}\bmoon\b[^.]{0,180}\bsun\b", re.I)),
    ("readable_one_to_one_label_relation", re.compile(
        r"\b(?:readable|transcribed|identified|named)\b[^.]{0,180}\b(?:labels?|inscriptions?|text)\b", re.I)),
)
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


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def flatten(value: object) -> str:
    if isinstance(value, str):
        text = value
    elif isinstance(value, list):
        text = " ".join(flatten(item) for item in value)
    elif isinstance(value, dict):
        text = " ".join(flatten(value[key]) for key in ("@value", "value", "en") if key in value)
    elif value is None:
        text = ""
    else:
        raise TypeError("unsupported manifest value")
    return re.sub(r"\s+", " ", text).strip()


def fetch(manifest_id: str) -> dict[str, object]:
    url = API.format(manifest_id)
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-FDTW-f68-worth-validator/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != url or response.headers.get("Location"):
            raise ValueError("unexpected live manifest response")
        raw = response.read()
    value = json.loads(raw)
    if type(value) is not dict or value.get("@id") != url:
        raise ValueError("live manifest identity mismatch")
    metadata: dict[str, str] = {}
    for item in value.get("metadata", []):
        if type(item) is not dict:
            raise ValueError("bad live metadata entry")
        metadata.setdefault(flatten(item.get("label")), flatten(item.get("value")))
    return {
        "manifest_id": manifest_id,
        "manifest_sha256": digest(raw),
        "label": flatten(value.get("label")),
        "manuscript_number": metadata.get("Manuscript number", ""),
        "century": metadata.get("Century", ""),
        "theme": metadata.get("Theme", ""),
        "description": flatten(value.get("description")),
    }


def strict_result() -> dict[str, object]:
    raw = RESULT.read_text(encoding="utf-8")
    def hook(items: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate result key")
        return dict(items)
    value = json.loads(raw, object_pairs_hook=hook, parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError("noncanonical result")
    return value


def broad_flags(row: dict[str, str]) -> dict[str, bool]:
    text = " ".join(row[key] for key in ("label", "description", "archetype", "theme"))
    return {name: bool(pattern.search(text)) for name, pattern in BROAD}


def relation_flags(description: str) -> dict[str, bool]:
    text = re.sub(r"\s+", " ", description)
    return {name: bool(pattern.search(text)) for name, pattern in TOPOLOGY}


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite f68r2 validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if digest(path.read_bytes()) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = strict_result()
    checks.append("canonical_duplicate_free_result")

    with FDTW.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 263 or len({row["manifest_id"] for row in rows}) != 263:
        raise ValueError("source projection inventory mismatch")
    checks.extend(("source_projection_263_rows", "source_projection_unique_ids"))
    broad_rows = [row for row in rows if all(broad_flags(row).values())]
    if tuple(row["manifest_id"] for row in broad_rows) != EXPECTED_IDS:
        raise ValueError("broad selection mismatch")
    checks.extend(("four_term_conjunction", "five_broad_rows", "broad_source_order"))

    with ThreadPoolExecutor(max_workers=5) as executor:
        live_rows = list(executor.map(fetch, EXPECTED_IDS))
    by_id = {row["manifest_id"]: row for row in rows}
    for live in live_rows:
        stored = by_id[str(live["manifest_id"])]
        for key in ("manifest_sha256", "label", "manuscript_number", "century", "theme", "description"):
            if str(live[key]) != stored[key]:
                raise ValueError(f"live projection mismatch: {live['manifest_id']}:{key}")
    checks.extend(("five_live_manifests_fetched", "five_live_hashes", "five_live_metadata_projections"))

    candidates: list[dict[str, object]] = []
    for row in broad_rows:
        topology = relation_flags(row["description"])
        candidates.append({
            "source_order": int(row["source_order"]),
            "manifest_id": row["manifest_id"],
            "manifest_sha256": row["manifest_sha256"],
            "label": row["label"],
            "manuscript_number": row["manuscript_number"],
            "century": row["century"],
            "theme": row["theme"],
            "term_flags": broad_flags(row),
            "topology_flags": topology,
            "exact_topology_metadata_candidate": all(topology.values()),
        })
    if any(row["exact_topology_metadata_candidate"] for row in candidates):
        raise ValueError("unexpected exact metadata candidate")
    checks.extend(("five_topology_vectors", "zero_exact_topology_candidates"))

    fabricated = (
        "At the top is a Moon face and at the bottom is a Sun face. A circle of stars connecting Sun and Moon. "
        "Inside are stars labelled in order. Circular text around the Moon and Sun. Named labels are transcribed."
    )
    if not all(relation_flags(fabricated).values()):
        raise ValueError("positive topology mutation failed")
    if all(relation_flags("A circle shows the Sun, Moon, and stars.").values()):
        raise ValueError("broad-only topology mutation failed")
    checks.extend(("positive_topology_fixture", "broad_only_fixture_rejected"))

    catalogue_text = re.sub(r"\s+", " ", CATALOGUE.read_text(encoding="utf-8")).casefold()
    phrase_checks = {phrase: phrase in catalogue_text for phrase in F68_PHRASES}
    if not all(phrase_checks.values()):
        raise ValueError("f68 human-source phrase mismatch")
    if "not a readable plaintext anchor" not in F68_VALIDATION.read_text(encoding="utf-8"):
        raise ValueError("cleartext route mismatch")
    if "f67r_f68r_historical_homologue_search\tSTOP_NO_EXACT_LABELLED_SLOT_HOMOLOGUE_FOUND" not in ANCHOR_REGISTRY.read_text(encoding="utf-8"):
        raise ValueError("historical route mismatch")
    checks.extend(("five_f68_human_topology_phrases", "cleartext_route_stop", "historical_homologue_route_stop"))

    expected_result = {
        "experiment": "FDTW_F68R2_SUN_MOON_RING_METADATA_WORTH_CHECK",
        "status": "PASS_COMPLETE_TEXT_ONLY_METADATA_WORTH_CHECK",
        "decision": "STOP_BEFORE_IMAGE_OR_PAPER_REVIEW_ZERO_EXACT_TOPOLOGY_METADATA_CANDIDATES",
        "counts": {"fdtw_rows": 263, "broad_sun_moon_circle_star_rows": 5, "exact_topology_metadata_candidates": 0},
        "broad_candidates": candidates,
        "f68r2_human_topology_phrase_checks": phrase_checks,
        "escalation_requirements": [name for name, _ in TOPOLOGY],
        "source_access": {
            "manuscript_images_opened": False,
            "thumbnails_or_canvases_opened": False,
            "papers_or_pdfs_opened": False,
            "ocr_or_automated_visual_output_used": False,
            "decoder_claims_or_historical_word_lists_opened": False,
        },
        "inputs": {
            str(SPEC.relative_to(BASE)): FROZEN[SPEC],
            str(FDTW.relative_to(BASE)): FROZEN[FDTW],
            str(FDTW_VALIDATION.relative_to(BASE)): FROZEN[FDTW_VALIDATION],
            str(CATALOGUE.relative_to(BASE)): FROZEN[CATALOGUE],
            str(F68_VALIDATION.relative_to(BASE)): FROZEN[F68_VALIDATION],
            str(ANCHOR_REGISTRY.relative_to(BASE)): FROZEN[ANCHOR_REGISTRY],
        },
        "claim_ceiling": "Five broad human-metadata comparanda are retained, but zero metadata row describes the complete f68r2 paired-medallion, connecting-star-ring, internally labelled-star, owned-circular-text topology; no object, label, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    if result != expected_result:
        raise ValueError("result reconstruction mismatch")
    checks.append("result_object_exact")
    expected_report = (
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
        "sound, language, cipher, plaintext, meaning, or translation follows.\n"
    )
    if REPORT.read_text(encoding="utf-8") != expected_report:
        raise ValueError("report reconstruction mismatch")
    checks.append("report_bytes_exact")

    validation = {
        "experiment": "FDTW_F68R2_SUN_MOON_RING_METADATA_WORTH_CHECK_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_AND_SOURCE_METADATA_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": digest(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": expected_result["counts"],
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# FDTW f68r2 Sun--Moon ring metadata worth check — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator independently reapplies the four-term filter to all 263 "
        "cached human-metadata records, live-refetches the five retained manifests, and reconstructs the five broad "
        "comparanda, zero exact-topology candidates, decision, result, and report.\n\n"
        "The stop is metadata-only and precedes image or paper review. It supplies no object, label, word, sound, "
        "language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
