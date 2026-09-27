"""Reproduce the bounded IIIF resolution finding; no image or target access.

Default: validate frozen metadata, predecessor receipt and registration hashes.
--fetch: acquire only the two declared metadata responses into external_cache.
Fetching does not update the frozen result or its published metadata snapshots.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent
CANVASES = {"91v": "5967406", "92r": "5967407"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        cache = BASE / "external_cache"
        cache.mkdir(exist_ok=True)
        for label, canvas in CANVASES.items():
            url = f"https://digital.blb-karlsruhe.de/i3f/v20/{canvas}/info.json"
            with urlopen(url, timeout=20) as response:
                raw = response.read()
            info = json.loads(raw)
            path = cache / f"karlsruhe_{label}_resolution_info.json"
            path.write_bytes(raw)
            print(json.dumps({"label": label, "url": url, "sha256": sha(path),
                              "width": info["width"], "height": info["height"]}))
        return

    result = json.loads((BASE / "KARLSRUHE_RELATION_ACQUISITION_RESULT.json").read_text())
    for item in result["frozen_inputs"]:
        assert sha(BASE / item["file"]) == item["sha256"], item["file"]
    old = json.loads((BASE / "SOURCE_ELEMENT_PASSAGE_RECEIPTS.json").read_text())
    assert {r["platform_label"] for r in result["resolution"]} == set(CANVASES)
    for row in result["resolution"]:
        label = row["platform_label"]
        info_path = BASE / row["metadata_file"]
        assert sha(info_path) == row["metadata_sha256"]
        info = json.loads(info_path.read_text())
        service = f"https://digital.blb-karlsruhe.de/i3f/v20/{CANVASES[label]}"
        assert info["@id"] == service
        assert row["metadata_url"] == service + "/info.json"
        native = [info["width"], info["height"]]
        prior = old["sources"][f"karlsruhe_platform_{label}"]["dimensions_px"]
        assert row["service_full_dimensions_px"] == native
        assert row["previously_inspected_dimensions_px"] == prior
        assert prior[0] >= native[0] and prior[1] >= native[1]
        assert all(s["width"] <= native[0] and s["height"] <= native[1]
                   for s in info["sizes"])
        assert any(isinstance(p, dict) and "sizeAboveFull" in p.get("supports", [])
                   for p in info["profile"])
        assert row["larger_size_request_adds_source_resolution"] is False
    assert result["decision"] == "NO_CHANGED_SOURCE_TEXT_ACQUIRED"
    assert result["new_native_images"] == result["new_target_accesses"] == 0
    assert result["new_transcribed_baselines"] == result["confirmed_words_added"] == 0
    print("PASS: both service dimensions and previous exposure verified; "
          "artifact consistency only, no semantic or visual validation")


if __name__ == "__main__":
    main()
