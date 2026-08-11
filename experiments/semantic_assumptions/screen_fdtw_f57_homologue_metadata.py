#!/usr/bin/env python3
"""Text-only FDTW catalogue prescreen for an exact f57-style homologue."""

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
SPEC = BASE / "FDTW_F57_HOMOLOGUE_METADATA_PRESCREEN_SPEC.md"
LISTING_URL = "https://ifilosofia.up.pt/proj/fdtw/iiif/manifests"
API = "https://iiifmanifests.ifilosofia.up.pt/api/manifests/{}.json"
OUT_TSV = RESULTS / "fdtw_f57_homologue_metadata_prescreen.tsv"
OUT_JSON = RESULTS / "fdtw_f57_homologue_metadata_prescreen.json"
OUT_REPORT = RESULTS / "fdtw_f57_homologue_metadata_prescreen_report.md"

LINK = re.compile(r'href="fdtw/iiif/manifest/([0-9a-f-]{36})"')
CIRCLE = re.compile(r"\b(wheel|rota|circular|circle|roundel|concentric)\b", re.I)
PEOPLE = re.compile(r"\b(four (?:human )?(?:figures|persons|people|heads)|personif(?:y|ied|ication)|human figures?|four men|four women|four heads)\b", re.I)
ELEMENT = re.compile(r"\b(element|elements|hot|cold|dry|moist|humid|calid\w*|frigid\w*|sicc\w*|humid\w*)\b", re.I)
MARKING = re.compile(r"\b(label|labels|inscription|inscriptions|marked|words?|terms?)\b", re.I)
FIELDS = (
    "source_order", "manifest_id", "manifest_sha256", "label", "manuscript_number",
    "century", "archetype", "theme", "description", "circle_match",
    "people_match", "element_quality_match", "marking_match", "metadata_candidate",
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def get(url: str) -> bytes:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "VManus-FDTW-metadata-prescreen/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.geturl() != url:
            raise ValueError(f"unexpected response for {url}")
        return response.read()


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
        raise TypeError(f"unsupported projected value: {type(value).__name__}")
    return re.sub(r"\s+", " ", text).strip()


def fetch_manifest(item: tuple[int, str]) -> dict[str, object]:
    order, manifest_id = item
    raw = get(API.format(manifest_id))
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("@id") != API.format(manifest_id):
        raise ValueError(f"manifest identity mismatch: {manifest_id}")
    metadata: dict[str, str] = {}
    for entry in data.get("metadata", []):
        if not isinstance(entry, dict):
            raise ValueError("bad metadata entry")
        key = flatten(entry.get("label"))
        if key not in metadata:
            metadata[key] = flatten(entry.get("value"))
    label = flatten(data.get("label"))
    description = flatten(data.get("description"))
    archetype = metadata.get("Archetype", "")
    theme = metadata.get("Theme", "")
    search = " ".join((label, description, archetype, theme))
    matches = tuple(int(bool(pattern.search(search))) for pattern in (CIRCLE, PEOPLE, ELEMENT, MARKING))
    return {
        "source_order": order,
        "manifest_id": manifest_id,
        "manifest_sha256": sha_bytes(raw),
        "label": label,
        "manuscript_number": metadata.get("Manuscript number", ""),
        "century": metadata.get("Century", ""),
        "archetype": archetype,
        "theme": theme,
        "description": description,
        "circle_match": matches[0],
        "people_match": matches[1],
        "element_quality_match": matches[2],
        "marking_match": matches[3],
        "metadata_candidate": int(all(matches)),
    }


def make_report(result: dict[str, object]) -> str:
    counts = result["counts"]
    return f"""# FDTW f57 homologue metadata prescreen v1

Decision: **{result['decision']}**.

The 2026 human-curated FDTW listing contains **{counts['unique_manifests']}**
unique manifests.  All were fetched as JSON metadata with zero failures.  The
exact text filter retains **{counts['circle_and_element_rows']}** broad
circle-plus-element records but **{counts['metadata_candidates']}** records
that also describe four human figures/personifications and readable markings.

The catalogue therefore does not justify image-level or full scholarly-source
validation as an f57v homologue route.  Harley 3099 and other known elemental
schemes remain useful source-family comparanda, but the metadata does not
describe the missing four-person, explicitly labelled, two-register topology.
This is a metadata no-find, not proof that no such image or manuscript exists.

No manuscript image, thumbnail, canvas, OCR, pixel, PDF, linked paper, or
external decoder claim was opened.  The result supplies no f57v ownership,
word, sound, language, cipher operation, plaintext, meaning, or translation.
"""


def main() -> None:
    outputs = (OUT_TSV, OUT_JSON, OUT_REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite FDTW prescreen outputs")
    listing = get(LISTING_URL)
    text = listing.decode("utf-8", "replace")
    ids = list(dict.fromkeys(LINK.findall(text)))
    if len(ids) < 200:
        raise ValueError("implausibly small FDTW manifest inventory")
    with ThreadPoolExecutor(max_workers=16) as executor:
        rows = list(executor.map(fetch_manifest, enumerate(ids, 1)))
    if [row["source_order"] for row in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("source-order drift")
    if len({row["manifest_id"] for row in rows}) != len(rows):
        raise ValueError("duplicate manifest projection")
    candidates = [row for row in rows if row["metadata_candidate"] == 1]
    circle_elements = [row for row in rows if row["circle_match"] == 1 and row["element_quality_match"] == 1]
    decision = (
        "STOP_BEFORE_IMAGE_VALIDATION_ZERO_F57_METADATA_CANDIDATES"
        if not candidates else "CANDIDATE_METADATA_REQUIRES_SEPARATE_HUMAN_SOURCE_AUDIT"
    )
    counts = {
        "listing_manifest_links": len(LINK.findall(text)),
        "unique_manifests": len(rows),
        "manifest_fetch_failures": 0,
        "circle_and_element_rows": len(circle_elements),
        "explicit_people_rows": sum(int(row["people_match"]) for row in rows),
        "metadata_candidates": len(candidates),
    }
    result = {
        "experiment": "FDTW_F57_HOMOLOGUE_METADATA_PRESCREEN_V1",
        "status": "PASS_COMPLETE_TEXT_ONLY_METADATA_PRESCREEN",
        "decision": decision,
        "listing_url": LISTING_URL,
        "listing_projection_sha256": sha_bytes("".join(f"{manifest_id}\n" for manifest_id in ids).encode("utf-8")),
        "spec_sha256": sha_file(SPEC),
        "producer_sha256": sha_file(Path(__file__)),
        "counts": counts,
        "candidate_manifest_ids": [str(row["manifest_id"]) for row in candidates],
        "circle_element_manifest_ids": [str(row["manifest_id"]) for row in circle_elements],
        "projection_sha256": "PENDING",
        "claim_ceiling": "Metadata acquisition stop only; no f57v ownership, word, sound, language, cipher, plaintext, meaning, or translation.",
    }
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result["projection_sha256"] = sha_file(OUT_TSV)
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(make_report(result), encoding="utf-8")


if __name__ == "__main__":
    main()
