#!/usr/bin/env python3
"""Validate the published source-deck identity; visual judgments remain human."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MANIFEST = ROOT / "experiments/yolo/gdt617_triple_herbal_plaintext_transducer/artifacts/source_freeze/sloane4016_manifest.json"
DECK = HERE / "IDEA739_SLOANE_SOURCE_DECK.tsv"
RESULT = HERE / "IDEA739_SLOANE_RESULT.json"
VALIDATION = HERE / "IDEA739_SLOANE_VALIDATION.json"


def main():
    manifest = json.loads(MANIFEST.read_text())
    with DECK.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    result = json.loads(RESULT.read_text())
    assert len(manifest["items"]) == len(rows) == result["total_canvases"] == 235
    assert result["thumbnails_retrieved"] == 235 and result["thumbnail_errors"] == 0
    assert result["native_review_indices"] == [125, 147, 218, 220]
    for i, (canvas, row) in enumerate(zip(manifest["items"], rows)):
        assert int(row["index"]) == i
        label = ";".join(canvas.get("label", {}).get("en", [])) or str(i)
        body = canvas["items"][0]["items"][0]["body"]["id"]
        url = body.split("/full/")[0] + "/full/320,/0/default.jpg"
        assert (row["source_folio"], row["official_iiif_thumbnail"]) == (label, url)
        assert int(row["bytes"]) > 0 and len(bytes.fromhex(row["sha256"])) == 32
    for value in result["native_review_full_sha256"].values():
        assert len(bytes.fromhex(value)) == 32
    validation = {
        "status": "PASS",
        "canvas_rows": 235,
        "deck_sha256": hashlib.sha256(DECK.read_bytes()).hexdigest(),
        "checked": "source manifest identity, every index/label/IIIF thumbnail URL, hash shapes and result roster",
        "not_checked": "pixel bytes or human visual judgments; live re-download needed to verify recorded image hashes",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
