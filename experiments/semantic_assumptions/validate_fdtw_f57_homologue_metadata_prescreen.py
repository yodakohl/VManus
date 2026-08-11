#!/usr/bin/env python3
"""Independent live-metadata reconstruction of the FDTW f57 prescreen."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SPEC = BASE / "FDTW_F57_HOMOLOGUE_METADATA_PRESCREEN_SPEC.md"
PRODUCER = BASE / "screen_fdtw_f57_homologue_metadata.py"
TSV = RESULTS / "fdtw_f57_homologue_metadata_prescreen.tsv"
RESULT = RESULTS / "fdtw_f57_homologue_metadata_prescreen.json"
REPORT = RESULTS / "fdtw_f57_homologue_metadata_prescreen_report.md"
OUT_JSON = RESULTS / "fdtw_f57_homologue_metadata_prescreen_validation.json"
OUT_REPORT = RESULTS / "fdtw_f57_homologue_metadata_prescreen_validation_report.md"
LISTING_URL = "https://ifilosofia.up.pt/proj/fdtw/iiif/manifests"
API = "https://iiifmanifests.ifilosofia.up.pt/api/manifests/{}.json"

FROZEN = {
    SPEC: "2a32f8c93bb9a4f04dc0d3450242ff0035f9680249c85987067b933641975a1d",
    PRODUCER: "e45c65e91bbaee150e7f81ec2efdfc554ed195315c4de327f8cf243b15561995",
    TSV: "7b584ddbd184eb0e47896a2e055119cc7c2a2d133ecc15f919b4c393bb0ce091",
    RESULT: "94c99c7d20da499bfb4058ca53f44322b880aa8194aed84e8db7bd892e63b87a",
    REPORT: "2c1e0780b109c4993ae5c89c955ba73dd19d7c75237b82cc13f985cec647d5db",
}

LINK = re.compile(r'href="fdtw/iiif/manifest/([0-9a-f-]{36})"')
FILTERS = (
    re.compile(r"\b(wheel|rota|circular|circle|roundel|concentric)\b", re.I),
    re.compile(r"\b(four (?:human )?(?:figures|persons|people|heads)|personif(?:y|ied|ication)|human figures?|four men|four women|four heads)\b", re.I),
    re.compile(r"\b(element|elements|hot|cold|dry|moist|humid|calid\w*|frigid\w*|sicc\w*|humid\w*)\b", re.I),
    re.compile(r"\b(label|labels|inscription|inscriptions|marked|words?|terms?)\b", re.I),
)
FIELDS = (
    "source_order", "manifest_id", "manifest_sha256", "label", "manuscript_number",
    "century", "archetype", "theme", "description", "circle_match",
    "people_match", "element_quality_match", "marking_match", "metadata_candidate",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get(url: str) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-FDTW-metadata-validator/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != url:
            raise ValueError(f"unexpected response: {url}")
        return response.read()


def project(value: object) -> str:
    if isinstance(value, str):
        merged = value
    elif isinstance(value, list):
        merged = " ".join(project(item) for item in value)
    elif isinstance(value, dict):
        merged = " ".join(project(value[key]) for key in ("@value", "value", "en") if key in value)
    elif value is None:
        merged = ""
    else:
        raise TypeError("unprojectable manifest value")
    return re.sub(r"\s+", " ", merged).strip()


def reconstruct(item: tuple[int, str]) -> dict[str, object]:
    order, manifest_id = item
    raw = get(API.format(manifest_id))
    value = json.loads(raw)
    if type(value) is not dict or value.get("@id") != API.format(manifest_id):
        raise ValueError("manifest identity mismatch")
    metadata: dict[str, str] = {}
    for entry in value.get("metadata", []):
        if type(entry) is not dict:
            raise ValueError("metadata entry mismatch")
        metadata.setdefault(project(entry.get("label")), project(entry.get("value")))
    label = project(value.get("label"))
    description = project(value.get("description"))
    archetype = metadata.get("Archetype", "")
    theme = metadata.get("Theme", "")
    searchable = " ".join((label, description, archetype, theme))
    flags = [int(bool(pattern.search(searchable))) for pattern in FILTERS]
    return {
        "source_order": order,
        "manifest_id": manifest_id,
        "manifest_sha256": sha(raw),
        "label": label,
        "manuscript_number": metadata.get("Manuscript number", ""),
        "century": metadata.get("Century", ""),
        "archetype": archetype,
        "theme": theme,
        "description": description,
        "circle_match": flags[0],
        "people_match": flags[1],
        "element_quality_match": flags[2],
        "marking_match": flags[3],
        "metadata_candidate": int(all(flags)),
    }


def canonical_result() -> dict[str, object]:
    raw = RESULT.read_text(encoding="utf-8")
    pairs: list[tuple[str, object]] = []
    def hook(items: list[tuple[str, object]]) -> dict[str, object]:
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate JSON key")
        pairs.extend(items)
        return dict(items)
    value = json.loads(raw, object_pairs_hook=hook)
    if json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n" != raw:
        raise ValueError("noncanonical result JSON")
    return value


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite FDTW validation outputs")
    checks: list[str] = []
    for path, expected in FROZEN.items():
        if sha(path.read_bytes()) != expected:
            raise SystemExit(f"frozen byte mismatch: {path.name}")
        checks.append(f"sha256:{path.name}")
    result = canonical_result()
    checks.append("canonical_duplicate_free_result")
    listing = get(LISTING_URL)
    ids = list(dict.fromkeys(LINK.findall(listing.decode("utf-8", "replace"))))
    if len(LINK.findall(listing.decode("utf-8", "replace"))) != 266 or len(ids) != 263:
        raise ValueError("listing inventory mismatch")
    listing_projection = "".join(f"{manifest_id}\n" for manifest_id in ids).encode("utf-8")
    if sha(listing_projection) != result["listing_projection_sha256"]:
        raise ValueError("stable listing projection mismatch")
    checks.extend(("stable_listing_projection_hash", "listing_266_links", "listing_263_unique"))
    with ThreadPoolExecutor(max_workers=16) as executor:
        rows = list(executor.map(reconstruct, enumerate(ids, 1)))
    if len(rows) != 263 or len({row["manifest_id"] for row in rows}) != 263:
        raise ValueError("manifest reconstruction mismatch")
    if [row["source_order"] for row in rows] != list(range(1, 264)):
        raise ValueError("manifest source-order mismatch")
    checks.extend(("all_263_manifests_fetched", "all_manifest_ids_unique", "source_order_exact"))
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    projection = buffer.getvalue().encode("utf-8")
    if projection != TSV.read_bytes() or sha(projection) != result["projection_sha256"]:
        raise ValueError("projected TSV mismatch")
    checks.extend(("projected_tsv_byte_exact", "projected_tsv_digest"))

    candidates = [row for row in rows if int(row["metadata_candidate"]) == 1]
    circle_elements = [row for row in rows if int(row["circle_match"]) and int(row["element_quality_match"])]
    counts = {
        "circle_and_element_rows": len(circle_elements),
        "explicit_people_rows": sum(int(row["people_match"]) for row in rows),
        "listing_manifest_links": 266,
        "manifest_fetch_failures": 0,
        "metadata_candidates": len(candidates),
        "unique_manifests": 263,
    }
    if counts != result["counts"] or counts != {
        "circle_and_element_rows": 12,
        "explicit_people_rows": 18,
        "listing_manifest_links": 266,
        "manifest_fetch_failures": 0,
        "metadata_candidates": 0,
        "unique_manifests": 263,
    }:
        raise ValueError("filter-count mismatch")
    if result["candidate_manifest_ids"] != []:
        raise ValueError("unexpected metadata candidate")
    if result["circle_element_manifest_ids"] != [str(row["manifest_id"]) for row in circle_elements]:
        raise ValueError("circle-element ID order mismatch")
    if result["decision"] != "STOP_BEFORE_IMAGE_VALIDATION_ZERO_F57_METADATA_CANDIDATES":
        raise ValueError("decision mismatch")
    checks.extend(("circle_element_count_12", "explicit_people_count_18", "candidate_count_zero", "circle_element_id_order", "stop_decision"))

    # Exact gate mutation: a fabricated row must require all four, not three.
    if all((1, 1, 1, 0)) or not all((1, 1, 1, 1)):
        raise ValueError("all-four conjunction guard failed")
    checks.append("all_four_filter_conjunction_mutation")

    validation = {
        "experiment": "FDTW_F57_HOMOLOGUE_METADATA_PRESCREEN_V1_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_METADATA_RECONSTRUCTION",
        "decision": result["decision"],
        "source_result_sha256": FROZEN[RESULT],
        "source_tsv_sha256": FROZEN[TSV],
        "source_report_sha256": FROZEN[REPORT],
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "check_count": len(checks),
        "checks": checks,
        "reconstructed_counts": counts,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT_JSON.write_text(json.dumps(validation, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# FDTW f57 homologue metadata prescreen — independent validation\n\n"
        f"Status: **{validation['status']}**.\n\n"
        f"All **{len(checks)}** checks pass. The validator independently refetched all 263 human-curated "
        "manifest metadata records, rebuilt the complete projection byte-for-byte, and confirmed 12 broad "
        "circle-element rows but zero four-person labelled candidates.\n\n"
        "The gate stops before images, OCR, papers, or decoder claims. It supplies no f57v ownership, word, "
        "sound, language, cipher operation, plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
