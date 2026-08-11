#!/usr/bin/env python3
"""Independent live-metadata validation of the FDTW f69 worth check."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "FDTW_F69_28_SECTION_METADATA_WORTH_CHECK_SPEC.md"
PRODUCER = BASE / "check_fdtw_f69_28_section_metadata_worth.py"
CAPACITY = RESULTS / "f69m001_capacity.md"
TARGET = RESULTS / "f69m001_target_validation.md"
REGISTRY = RESULTS / "translation_anchor_acquisition_registry_v1.tsv"
RESULT = RESULTS / "fdtw_f69_28_section_metadata_worth.json"
REPORT = RESULTS / "fdtw_f69_28_section_metadata_worth_report.md"
OUT_JSON = RESULTS / "fdtw_f69_28_section_metadata_worth_validation.json"
OUT_REPORT = RESULTS / "fdtw_f69_28_section_metadata_worth_validation_report.md"
MANIFEST_ID = "a9a0e134-9a21-47b7-818b-c7058cd6b425"
URL = f"https://iiifmanifests.ifilosofia.up.pt/api/manifests/{MANIFEST_ID}.json"

FROZEN = {
    SPEC: "991b620505bf00c7f146e755cbc1031e47bca0c724e1210fb516242756ebaed4",
    PRODUCER: "7ff5dd033c5afa7cfb711b1149dc47912936ba39c5d218ff62ef78beb9890669",
    CAPACITY: "d2d1a2ff37a7508bab5656c02df4d527d72000b3228b0e3c6ef94d7ec68bbbb7",
    TARGET: "1eea25baf92d33934c3737b305217e64fa1cf7430c06f062ec275bced2c6f8b1",
    REGISTRY: "0261d2e7856ddf26b18fe46915f66446734dcc687cc516dac4aa23c4704b7a1c",
    RESULT: "2d1700e2f318e80cf443ca149844fef7b21b258e62e260db5b11e50688d12775",
    REPORT: "a256e387ed8c3eff1ecfdf68717a69aeb4e71dabf4589cef9273bb2ecf15206a",
}
MANIFEST_SHA = "53eb8c83f00619c9c30460ab6322d61e2900407e5be335d2173b833255ae9424"
PHRASES = (
    "circular diagram with four layers", "seven climates",
    "twenty eight sections with visible stars and corresponding images",
    "36 constellations", "twelve sections of the zodiac", "marginal labels for east and west",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duplicate_free(pairs: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def strict_json(path: Path) -> object:
    raw = path.read_text(encoding="utf-8")
    value = json.loads(raw, object_pairs_hook=duplicate_free)
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError("noncanonical result JSON")
    return value


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
        raise TypeError(type(value).__name__)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise ValueError(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")

    request = urllib.request.Request(URL, method="GET", headers={"User-Agent": "VManus-FDTW-f69-worth-validation/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != URL or response.headers.get("Location"):
            raise ValueError("unexpected manifest response")
        raw = response.read()
    if hashlib.sha256(raw).hexdigest() != MANIFEST_SHA:
        raise ValueError("live manifest mismatch")
    manifest = json.loads(raw, object_pairs_hook=duplicate_free)
    if manifest.get("@id") != URL or flatten(manifest.get("label")) != "Earth and the Heavens":
        raise ValueError("manifest identity mismatch")
    checks.extend(("live_manifest_sha256", "manifest_identity"))

    metadata: dict[str, str] = {}
    for entry in manifest.get("metadata", []):
        key = flatten(entry.get("label"))
        if key not in metadata:
            metadata[key] = flatten(entry.get("value"))
    if {
        "Manuscript number": metadata.get("Manuscript number"),
        "Century": metadata.get("Century"), "Language": metadata.get("Language"), "Theme": metadata.get("Theme"),
    } != {
        "Manuscript number": "MS. Arab. c. 90, f. 2b-3a", "Century": "c. 1200 AD",
        "Language": "Arabic", "Theme": "Astronomy",
    }:
        raise ValueError("source metadata drift")
    description = flatten(manifest.get("description"))
    phrase_checks = {phrase: phrase.casefold() in description.casefold() for phrase in PHRASES}
    if not all(phrase_checks.values()):
        raise ValueError("description topology drift")
    checks.extend(("source_identity", "nested_7_28_36_12_description"))

    if not all(text in CAPACITY.read_text(encoding="utf-8") for text in (
        "28 alternating long/short radial objects", "one inward-reading label apiece", "`f69v.X1.1` through `.28`",
    )):
        raise ValueError("f69 capacity contract drift")
    if "NONCONFIRM_FIXED_LATIN_MANSION_PREFIX_TOPOLOGY" not in TARGET.read_text(encoding="utf-8"):
        raise ValueError("f69 target contract drift")
    if "without selecting a spelling roster post hoc" not in REGISTRY.read_text(encoding="utf-8"):
        raise ValueError("acquisition rule drift")
    checks.extend(("f69_capacity_state", "f69_nonconfirmation_state", "posthoc_roster_exclusion"))

    result = strict_json(RESULT)
    if not isinstance(result, dict):
        raise ValueError("result is not object")
    if result["experiment"] != "FDTW_F69_28_SECTION_METADATA_WORTH_CHECK":
        raise ValueError("experiment mismatch")
    if result["status"] != "PASS_ONE_NEW_28_SECTION_COMPARATOR_IDENTIFIED":
        raise ValueError("status mismatch")
    if result["decision"] != "STOP_BEFORE_IMAGE_PAPER_OR_ROSTER_VALIDATION_ROUTE_NOT_NOVEL":
        raise ValueError("decision mismatch")
    if result["manifest_sha256"] != MANIFEST_SHA or result["manifest_url"] != URL:
        raise ValueError("manifest binding mismatch")
    if result["description_topology"] != {"central_climates": 7, "constellations": 36, "star_image_sections": 28, "zodiac_sections": 12}:
        raise ValueError("topology mismatch")
    expected_gates = {
        "exact_28_count_match": True, "single_register_topology_match": False,
        "readable_28_values_exposed_in_metadata": False,
        "unique_cross_manuscript_start_direction_slot_mapping": False,
        "new_route_not_posthoc_roster_substitution": False,
    }
    if result["gates"] != expected_gates or result["phrase_checks"] != phrase_checks:
        raise ValueError("worth decision reconstruction mismatch")
    checks.extend(("canonical_result", "status_decision", "manifest_binding", "topology_counts", "worth_rule"))

    expected_report = (
        "# FDTW f69 28-section comparator worth check\n\n"
        "Decision: **STOP_BEFORE_IMAGE_PAPER_OR_ROSTER_VALIDATION_ROUTE_NOT_NOVEL**.\n\n"
        "The human-curated FDTW metadata identifies one genuine new 28-section astronomical comparandum: *Earth and the Heavens*, Bodleian MS. Arab. c. 90, fols. 2b–3a. Its description is not a simple f69-style legend. It is a nested 7/28/36/12 scheme: seven climates, 28 star/image sections, 36 constellations, and 12 zodiac sections with east/west labels.\n\n"
        "The shared count is worth recording, but it does not fix a cross-manuscript start, direction, or slot ownership. F69M001 already nonconfirmed one fixed lunar-mansion prefix topology; opening a second language/spelling roster now would be a post-target roster substitution, not a new falsifier. The metadata does not expose the 28 readable values.\n\n"
        "No image, thumbnail, canvas, paper, PDF, OCR output, decoder claim, or roster score entered this result. The source remains a broad comparandum only and supplies no mansion, word, sound, language, cipher, plaintext, meaning, or translation.\n"
    )
    if REPORT.read_text(encoding="utf-8") != expected_report:
        raise ValueError("report mismatch")
    checks.append("exact_report_bytes")

    validation = {
        "experiment": "FDTW_F69_28_SECTION_METADATA_WORTH_CHECK_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_METADATA_RECONSTRUCTION",
        "decision": "VALIDATED_STOP_BEFORE_DEEP_VALIDATION",
        "check_count": len(checks), "checks": checks,
        "validated_result_sha256": FROZEN[RESULT], "live_manifest_sha256": MANIFEST_SHA,
        "claim_ceiling": "Validation confirms only the one-source text metadata worth stop; no f69 slot, mansion, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# FDTW f69 28-section worth-check validation\n\n"
        f"PASS: **{len(checks)}** checks independently refetch and reconstruct the source identity, nested 7/28/36/12 metadata, f69 route state, worth decision, and exact report.\n\n"
        "This validates a stop before image, paper, or roster analysis. No f69 slot value or translation follows.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
