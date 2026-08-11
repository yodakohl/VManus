#!/usr/bin/env python3
"""Cheap text-only worth check for the FDTW 28-section f69 comparator."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "FDTW_F69_28_SECTION_METADATA_WORTH_CHECK_SPEC.md"
F69_CAPACITY = RESULTS / "f69m001_capacity.md"
F69_TARGET = RESULTS / "f69m001_target_validation.md"
ANCHOR_REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
MANIFEST_ID = "a9a0e134-9a21-47b7-818b-c7058cd6b425"
MANIFEST_URL = f"https://iiifmanifests.ifilosofia.up.pt/api/manifests/{MANIFEST_ID}.json"
MANIFEST_SHA256 = "53eb8c83f00619c9c30460ab6322d61e2900407e5be335d2173b833255ae9424"
OUT_JSON = RESULTS / "fdtw_f69_28_section_metadata_worth.json"
OUT_REPORT = RESULTS / "fdtw_f69_28_section_metadata_worth_report.md"

PHRASES = (
    "circular diagram with four layers",
    "seven climates",
    "twenty eight sections with visible stars and corresponding images",
    "36 constellations",
    "twelve sections of the zodiac",
    "marginal labels for east and west",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


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
        raise TypeError(f"unsupported metadata value: {type(value).__name__}")
    return re.sub(r"\s+", " ", text).strip()


def get_manifest() -> tuple[bytes, dict[str, object]]:
    request = urllib.request.Request(MANIFEST_URL, method="GET", headers={"User-Agent": "VManus-FDTW-f69-worth-check/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != MANIFEST_URL:
            raise ValueError("unexpected manifest response")
        if response.headers.get("Location"):
            raise ValueError("redirected manifest response")
        raw = response.read()
    if sha_bytes(raw) != MANIFEST_SHA256:
        raise ValueError("manifest byte drift")
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get("@id") != MANIFEST_URL:
        raise ValueError("manifest identity mismatch")
    return raw, value


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite worth-check outputs")
    _, manifest = get_manifest()
    metadata: dict[str, str] = {}
    for entry in manifest.get("metadata", []):
        if not isinstance(entry, dict):
            raise ValueError("bad metadata entry")
        metadata.setdefault(flatten(entry.get("label")), flatten(entry.get("value")))
    description = flatten(manifest.get("description"))
    if flatten(manifest.get("label")) != "Earth and the Heavens":
        raise ValueError("label drift")
    if metadata.get("Manuscript number") != "MS. Arab. c. 90, f. 2b-3a":
        raise ValueError("manuscript identity drift")
    phrase_checks = {phrase: phrase.casefold() in description.casefold() for phrase in PHRASES}
    if not all(phrase_checks.values()):
        raise ValueError("registered topology phrase missing")

    capacity = F69_CAPACITY.read_text(encoding="utf-8")
    for phrase in (
        "28 alternating long/short radial objects",
        "one inward-reading label apiece",
        "`f69v.X1.1` through `.28`",
    ):
        if phrase not in capacity:
            raise ValueError(f"f69 capacity drift: {phrase}")
    target = F69_TARGET.read_text(encoding="utf-8")
    if "NONCONFIRM_FIXED_LATIN_MANSION_PREFIX_TOPOLOGY" not in target:
        raise ValueError("f69 target decision drift")
    registry = ANCHOR_REGISTRY.read_text(encoding="utf-8")
    if "without selecting a spelling roster post hoc" not in registry:
        raise ValueError("anchor acquisition rule drift")

    gates = {
        "exact_28_count_match": True,
        "single_register_topology_match": False,
        "readable_28_values_exposed_in_metadata": False,
        "unique_cross_manuscript_start_direction_slot_mapping": False,
        "new_route_not_posthoc_roster_substitution": False,
    }
    result = {
        "experiment": "FDTW_F69_28_SECTION_METADATA_WORTH_CHECK",
        "status": "PASS_ONE_NEW_28_SECTION_COMPARATOR_IDENTIFIED",
        "decision": "STOP_BEFORE_IMAGE_PAPER_OR_ROSTER_VALIDATION_ROUTE_NOT_NOVEL",
        "manifest_id": MANIFEST_ID,
        "manifest_url": MANIFEST_URL,
        "manifest_sha256": MANIFEST_SHA256,
        "source_identity": {
            "label": "Earth and the Heavens",
            "manuscript_number": metadata["Manuscript number"],
            "century": metadata.get("Century", ""),
            "language": metadata.get("Language", ""),
            "theme": metadata.get("Theme", ""),
        },
        "description_topology": {"central_climates": 7, "star_image_sections": 28, "constellations": 36, "zodiac_sections": 12},
        "phrase_checks": phrase_checks,
        "gates": gates,
        "inputs": {
            str(SPEC.relative_to(BASE)): sha_file(SPEC),
            str(F69_CAPACITY.relative_to(BASE)): sha_file(F69_CAPACITY),
            str(F69_TARGET.relative_to(BASE)): sha_file(F69_TARGET),
            str(ANCHOR_REGISTRY.relative_to(BASE)): sha_file(ANCHOR_REGISTRY),
        },
        "claim_ceiling": "One broad historical 28-part astronomical comparandum is identified, but it does not supply a unique f69 slot relation or authorize another post-hoc roster test, word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# FDTW f69 28-section comparator worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_PAPER_OR_ROSTER_VALIDATION_ROUTE_NOT_NOVEL**.\n\n"
        "The human-curated FDTW metadata identifies one genuine new 28-section astronomical comparandum: "
        "*Earth and the Heavens*, Bodleian MS. Arab. c. 90, fols. 2b–3a. Its description is not a simple f69-style "
        "legend. It is a nested 7/28/36/12 scheme: seven climates, 28 star/image sections, 36 constellations, and "
        "12 zodiac sections with east/west labels.\n\n"
        "The shared count is worth recording, but it does not fix a cross-manuscript start, direction, or slot ownership. "
        "F69M001 already nonconfirmed one fixed lunar-mansion prefix topology; opening a second language/spelling roster now "
        "would be a post-target roster substitution, not a new falsifier. The metadata does not expose the 28 readable values.\n\n"
        "No image, thumbnail, canvas, paper, PDF, OCR output, decoder claim, or roster score entered this result. "
        "The source remains a broad comparandum only and supplies no mansion, word, sound, language, cipher, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
