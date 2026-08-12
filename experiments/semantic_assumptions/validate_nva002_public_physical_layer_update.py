#!/usr/bin/env python3
"""Independent live reconstruction of the NVA002 metadata-only stop."""
from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
RES = BASE / "results"
RESULT = RES / "nva002_public_physical_layer_update_prescreen.json"
REPORT = RES / "nva002_public_physical_layer_update_prescreen_report.md"
OUT = RES / "nva002_public_physical_layer_update_prescreen_validation.json"
YALE = "https://collections.library.yale.edu/manifests/2002046"
DRIVE = "https://drive.google.com/drive/mobile/folders/{folder}?usp=sharing"


class ItemParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: dict[str, str] = {}

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        item_id, name = values.get("data-id"), values.get("data-tooltip")
        if item_id and name:
            if item_id in self.items and self.items[item_id] != name:
                raise ValueError("conflicting item")
            self.items[item_id] = name


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 NVA002-independent-validator"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(response.status)
        return response.read()


def items(folder: str) -> dict[str, str]:
    parser = ItemParser()
    parser.feed(fetch(DRIVE.format(folder=folder)).decode("utf-8", "strict"))
    return parser.items


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    checks: dict[str, bool] = {}
    checks["canonical_result"] = RESULT.read_bytes() == canonical(result)
    checks["source_hashes"] = result["inputs"] == {key: sha(ROOT / key) for key in result["inputs"]}
    checks["source_endpoints"] = result["sources"] == {
        "yale_manifest": YALE,
        "drive_root": DRIVE.format(folder="1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig"),
        "processed_folder": DRIVE.format(folder="1BFwNZTgLqvgnIU8rmXQCdW6kIuC4baS7"),
        "raw_tiff_folder": DRIVE.format(folder="1cG27kgxCsxyU4DkCKo7eLRa1Pq8XM79N"),
    }

    raw = fetch(YALE)
    manifest = json.loads(raw)
    body_counts: Counter[int] = Counter()
    formats: Counter[str] = Counter()
    for canvas in manifest["items"]:
        bodies = [annotation["body"] for page in canvas.get("items", []) for annotation in page.get("items", [])]
        body_counts[len(bodies)] += 1
        for body in bodies:
            formats[body.get("format", "MISSING")] += 1
    checks["yale_manifest_hash"] = hashlib.sha256(raw).hexdigest() == result["yale"]["manifest_sha256"] == "317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309"
    checks["yale_213_canvases"] = len(manifest["items"]) == result["yale"]["canvases"] == 213
    checks["yale_one_body_each"] = body_counts == Counter({1: 213}) and result["yale"]["body_count_distribution"] == {"1": 213}
    checks["yale_jpeg_only"] = formats == Counter({"image/jpeg": 213}) and result["yale"]["body_formats"] == {"image/jpeg": 213}
    checks["yale_no_top_annotations"] = not manifest.get("annotations", []) and result["yale"]["top_level_annotations"] == 0

    top = items("1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig")
    checks["drive_top_inventory"] = top == result["drive"]["top_level_items"] and len(top) == 5
    processed = items("1BFwNZTgLqvgnIU8rmXQCdW6kIuC4baS7")
    raw_items = items("1cG27kgxCsxyU4DkCKo7eLRa1Pq8XM79N")
    expected_names = {f"Voynich_{folio} Shared folder" for folio in ("001r", "008r", "017r", "026r", "047r", "070v1", "071r", "093r", "102v1", "116v")}
    checks["processed_ten_folios"] = set(processed.values()) == expected_names and len(processed) == 10
    checks["raw_ten_folios"] = set(raw_items.values()) == expected_names and len(raw_items) == 10
    checks["recorded_drive_ids"] = (
        {(row["folder_id"], f"Voynich_{row['folio']} Shared folder") for row in result["drive"]["processed_folios"]} == set(processed.items())
        and {(row["folder_id"], f"Voynich_{row['folio']} Shared folder") for row in result["drive"]["raw_folios"]} == set(raw_items.items())
    )
    checks["no_image_or_text_access"] = result["access"] == {
        "manifest_and_folder_listing_metadata_opened": True,
        "manuscript_image_thumbnail_tiff_or_jpeg_body_opened": False,
        "transcription_or_formal_feature_opened": False,
        "ocr_clip_embedding_or_automated_vision_used": False,
    }
    checks["decision_and_ceiling"] = (
        result["status"] == "STOP_NO_NEW_PUBLIC_IMAGE_LAYER_OR_UNCOVERED_MSI_FOLIO"
        and "unpublished or future" in result["claim_ceiling"]
        and "translation" in result["claim_ceiling"]
    )
    with (BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv").open(encoding="utf-8", newline="") as handle:
        ledger = {row["experiment"]: row["status"] for row in csv.DictReader(handle, delimiter="\t")}
    checks["prerequisite_routes_live"] = (
        result["prerequisite_route_statuses"]
        == {key: ledger[key] for key in result["prerequisite_route_statuses"]}
    )
    if not all(checks.values()):
        raise SystemExit({key: value for key, value in checks.items() if not value})
    payload = {
        "experiment": "NVA002_PUBLIC_PHYSICAL_LAYER_UPDATE_PRESCREEN_VALIDATION",
        "status": "PASS_15_CHECK_INDEPENDENT_LIVE_METADATA_RECONSTRUCTION",
        "check_count": len(checks),
        "checks": checks,
        "source_result_sha256": sha(RESULT),
        "source_report_sha256": sha(REPORT),
        "claim_ceiling": "Validation confirms only the live public-inventory stop and supplies no manuscript reading or translation.",
    }
    OUT.write_bytes(canonical(payload))
    print(json.dumps({"status": payload["status"], "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
