#!/usr/bin/env python3
"""Restore the two exact public source folios and replay the viewing crops.

This validates source identity and coverage, not paleography or translation.
No Voynich source is read or fetched.
"""
import datetime
import hashlib
import json
from pathlib import Path
import urllib.request

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def data(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def restore(relative, url, sha):
    path = ROOT / relative
    if not path.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "VManus-source-replay"})
        with urllib.request.urlopen(request, timeout=45) as response:
            blob = response.read()
        assert digest(blob) == sha, "Changed public source bytes"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    assert digest(path.read_bytes()) == sha, relative
    return path


def main():
    first = next(x for x in data("ALCHEMICAL_COMPOSITE_RECEIPTS.json")["images"]
                 if x["label"] == "1r-3")
    second = data("AURORA_LEIDEN_F38R_RECEIPT.json")
    sources = [restore(first["path"], first["url"], first["sha256"]),
               restore(second["file"], second["url"], second["sha256"])]
    n = 0
    for receipt, source in zip(
        ["AURORA_TEXT_CROP_RECEIPTS.json", "AURORA_LEIDEN_CROP_RECEIPTS.json"], sources):
        record = data(receipt)
        assert digest(source.read_bytes()) == record["source_sha256"]
        with Image.open(source) as original:
            for row in record["regions"]:
                crop = original.crop(row["box"])
                angle = row.get("rotation_counterclockwise_degrees", 0)
                if angle:
                    crop = crop.transpose({90: Image.Transpose.ROTATE_90,
                                           270: Image.Transpose.ROTATE_270}[angle])
                assert list(crop.size) == row["dimensions"]
                path = ROOT / row["file"]
                if not path.exists():
                    crop.save(path)
                with Image.open(path) as saved:
                    assert saved.size == crop.size and saved.tobytes() == crop.tobytes()
                n += 1
    reading = data("AURORA_TEXT_READING.json")
    assert {x["zone"] for x in reading["rows"]} == {
        "top_intro", "top_list", "right", "bottom", "left"}
    assert len(reading["rows"][1]["published_latin"]) == 3
    assert reading["complete_unambiguous_argument_translation"] is False
    assert reading["full_diplomatic_collation"] is False
    assert reading["new_target_access"] is False
    result = {
        "status": "PASS",
        "full_public_source_folios_hash_checked": len(sources),
        "lossless_crop_pixels_replayed": n,
        "all_four_original_margins_accounted": True,
        "native_paleography_automatically_verified": False,
        "manuscript_meaning_verified": False,
        "new_target_access": False,
        "checked_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    (HERE / "AURORA_TEXT_VALIDATION.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
