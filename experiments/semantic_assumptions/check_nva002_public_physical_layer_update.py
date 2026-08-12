#!/usr/bin/env python3
"""Metadata-only live prescreen for new public Voynich physical-layer data."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
METHOD = BASE / "NVA002_PUBLIC_PHYSICAL_LAYER_UPDATE_PRESCREEN_METHOD.md"
LEDGER = BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv"
OUT = RES / "nva002_public_physical_layer_update_prescreen.json"
REPORT = RES / "nva002_public_physical_layer_update_prescreen_report.md"
YALE = "https://collections.library.yale.edu/manifests/2002046"
DRIVE_ROOT = "1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig"
DRIVE_URL = "https://drive.google.com/drive/mobile/folders/{folder}?usp=sharing"
KNOWN_FOLIOS = ("001r", "008r", "017r", "026r", "047r", "070v1", "071r", "093r", "102v1", "116v")
EXPECTED_TOP = {
    "1r0FWOBJfKEeKVdJdhubprsHzC7Wv3yQb": "Lab_true_color_TIFF Shared folder",
    "1BFwNZTgLqvgnIU8rmXQCdW6kIuC4baS7": "Processed_Images Shared folder",
    "1cG27kgxCsxyU4DkCKo7eLRa1Pq8XM79N": "Raw TIFFs (not readable by most image viewers) Shared folder",
    "1to9QOXNrSfIUITnogjkZSTy8zN553OGi": "RGB_true_color_JPEG Shared folder",
    "1nzKNlV2BqCEz3VvheAFZ_4IULFwLExng": "READ ME.pdf PDF",
}


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 NVA002-metadata-only"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError((url, response.status))
        return response.read()


def drive_items(folder: str) -> dict[str, str]:
    text = fetch(DRIVE_URL.format(folder=folder)).decode("utf-8", "strict")
    pairs = re.findall(r'data-id="([^"]+)"[^>]*data-tooltip="([^"]+)"', text)
    result: dict[str, str] = {}
    for item_id, name in pairs:
        name = html.unescape(name)
        if item_id in result and result[item_id] != name:
            raise ValueError("Drive item-name conflict")
        result[item_id] = name
    return result


def folio_inventory(items: dict[str, str]) -> list[dict[str, str]]:
    output = []
    for item_id, name in items.items():
        match = re.fullmatch(r"Voynich_(\d+(?:v\d+|r\d+|[rv])) Shared folder", name)
        if match:
            output.append({"folio": match.group(1), "folder_id": item_id})
    return sorted(output, key=lambda item: KNOWN_FOLIOS.index(item["folio"]) if item["folio"] in KNOWN_FOLIOS else 999)


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")

    manifest_raw = fetch(YALE)
    manifest = json.loads(manifest_raw)
    body_counts: Counter[int] = Counter()
    body_formats: Counter[str] = Counter()
    for canvas in manifest["items"]:
        bodies = [annotation["body"] for page in canvas.get("items", []) for annotation in page.get("items", [])]
        body_counts[len(bodies)] += 1
        for body in bodies:
            if isinstance(body, list):
                raise ValueError("multiple body list")
            body_formats[body.get("format", "MISSING")] += 1

    top = drive_items(DRIVE_ROOT)
    if top != EXPECTED_TOP:
        raise SystemExit("Drive top-level inventory changed")
    processed = folio_inventory(drive_items("1BFwNZTgLqvgnIU8rmXQCdW6kIuC4baS7"))
    raw = folio_inventory(drive_items("1cG27kgxCsxyU4DkCKo7eLRa1Pq8XM79N"))
    processed_folios = [item["folio"] for item in processed]
    raw_folios = [item["folio"] for item in raw]

    with LEDGER.open(encoding="utf-8", newline="") as handle:
        ledger = {row["experiment"]: row["status"] for row in csv.DictReader(handle, delimiter="\t")}
    prerequisite = {
        "public_msi_translation_anchor_worth_screen": "STOP_NO_NEW_TRANSLATION_ANCHOR_IN_PUBLIC_MSI_SUBSET",
        "remaining_public_msi_plant_folios_worth_screen": "STOP_NO_ANCHOR_IN_REMAINING_PUBLIC_MSI_PLANT_FOLIOS",
        "f57v_namenmantik_f1r_17_slot_claim_audit": "STOP_FALSE_INTERPOLATED_SEVENTEEN_SLOT_BRIDGE",
    }
    if {key: ledger[key] for key in prerequisite} != prerequisite:
        raise SystemExit("prerequisite route drift")

    yale_projection = {
        "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "canvases": len(manifest["items"]),
        "body_count_distribution": {str(key): value for key, value in sorted(body_counts.items())},
        "body_formats": dict(sorted(body_formats.items())),
        "top_level_annotations": len(manifest.get("annotations", [])),
    }
    gates = {
        "yale_manifest_remains_known_213_single_jpeg_canvases": yale_projection == {
            "manifest_sha256": "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309",
            "canvases": 213,
            "body_count_distribution": {"1": 213},
            "body_formats": {"image/jpeg": 213},
            "top_level_annotations": 0,
        },
        "processed_inventory_is_known_ten_folios": processed_folios == list(KNOWN_FOLIOS),
        "raw_inventory_is_known_ten_folios": raw_folios == list(KNOWN_FOLIOS),
        "all_ten_folios_previously_routed": True,
        "zero_image_bodies_opened": True,
    }
    if not all(gates.values()):
        raise SystemExit(gates)

    payload = {
        "experiment": "NVA002_PUBLIC_PHYSICAL_LAYER_UPDATE_PRESCREEN",
        "schema": "NVA002_RESULT_V1",
        "status": "STOP_NO_NEW_PUBLIC_IMAGE_LAYER_OR_UNCOVERED_MSI_FOLIO",
        "decision": "WAIT_FOR_GENUINELY_NEW_PUBLIC_OR_PROVENANCE_CLEAN_PHYSICAL_EVIDENCE",
        "sources": {
            "yale_manifest": YALE,
            "drive_root": DRIVE_URL.format(folder=DRIVE_ROOT),
            "processed_folder": DRIVE_URL.format(folder="1BFwNZTgLqvgnIU8rmXQCdW6kIuC4baS7"),
            "raw_tiff_folder": DRIVE_URL.format(folder="1cG27kgxCsxyU4DkCKo7eLRa1Pq8XM79N"),
        },
        "yale": yale_projection,
        "drive": {"top_level_items": top, "processed_folios": processed, "raw_folios": raw},
        "prerequisite_route_statuses": prerequisite,
        "gates": gates,
        "inputs": {str(METHOD.relative_to(ROOT)): sha(METHOD)},
        "access": {
            "manifest_and_folder_listing_metadata_opened": True,
            "manuscript_image_thumbnail_tiff_or_jpeg_body_opened": False,
            "transcription_or_formal_feature_opened": False,
            "ocr_clip_embedding_or_automated_vision_used": False,
        },
        "claim_ceiling": (
            "The live official Yale manifest exposes the same single-JPEG canvas class and the public 2014 MSI Drive "
            "exposes only the same ten already routed folios. This does not address unpublished or future imaging and "
            "establishes no glyph, word, sound, language, cipher, plaintext, meaning, or translation."
        ),
    }
    OUT.write_bytes(canonical(payload))
    REPORT.write_text(
        "# NVA002 public physical-layer update prescreen\n\n"
        "Status: **STOP_NO_NEW_PUBLIC_IMAGE_LAYER_OR_UNCOVERED_MSI_FOLIO**.\n\n"
        "The live official Yale IIIF manifest remains the previously bound 213-canvas object: every canvas has exactly "
        "one JPEG body and the manifest has no top-level image-annotation layer. The public 2014 Lazarus Project Drive "
        "still exposes the same ten folio folders in both `Processed_Images` and `Raw TIFFs`: f1r, f8r, f17r, f26r, "
        "f47r, f70v1, f71r, f93r, f102v1, and f116v. All ten are already covered by the two public-MSI screens or the "
        "separate later-alphabet-table audit for f1r.\n\n"
        "No manuscript image body, thumbnail, TIFF, JPEG, transcription filler, or formal feature was opened. The stop "
        "does not generalize to unpublished or future imaging and supplies no glyph, word, sound, language, cipher, "
        "plaintext, meaning, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "folios": len(processed_folios)}, sort_keys=True))


if __name__ == "__main__":
    main()
