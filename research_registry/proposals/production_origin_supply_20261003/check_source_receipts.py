#!/usr/bin/env python3
"""Verify the published source receipts; does not assess manuscript meaning."""
import argparse
import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--fetch-missing", action="store_true")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    source = json.loads((here / "COREMA_NATIVE_ABBREVIATION_SUPPLY.json").read_text())
    image_source = json.loads((here / "EGERTON_FIRST_ENTRY_NATIVE_ROOT.json").read_text())
    checks = []

    def read_checked(path, url, expected_hash, expected_size=None):
        if not path.exists() and args.fetch_missing:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(urllib.request.urlopen(url, timeout=60).read())
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected_hash, path.name
        if expected_size is not None:
            assert len(data) == expected_size, path.name
        return data

    blobs = {}
    for receipt in source["receipts"]:
        blobs[receipt["object"]] = read_checked(
            args.cache_dir / receipt["local_cache_basename"], receipt["url"],
            receipt["sha256"], receipt["bytes"])
        checks.append(receipt["object"] + ": pinned bytes verified")
    raw = blobs["o:corema.b4"]
    root = ET.fromstring(raw)
    ns = {"t": "http://www.tei-c.org/ns/1.0"}
    assert len(root.findall("./t:text/t:body/t:ab/t:seg", ns)) == 269
    assert len(root.findall(".//t:abbr", ns)) == 1174
    checks.append("B4: independent segment/abbreviation counts verified")
    for example in source["complete_examples"]:
        fragment = raw[example["source_byte_start"]:example["source_byte_end_exclusive"]]
        assert hashlib.sha256(fragment).hexdigest() == example["fragment_sha256"]
        assert fragment.decode() == example["complete_original_xml_fragment"]
        checks.append("B4 entry " + str(example["entry_ordinal"]) + ": exact source slice verified")
    read_checked(args.images_dir / "manifest.json", image_source["manifest_url"],
                 image_source["manifest_sha256"])
    checks.append("Egerton747: manifest bytes verified")
    names = ("f125v_1800.jpg", "f126r_2400.jpg", "f126r_first_native.jpg")
    assert len(image_source["images"]) == len(names)
    for name, receipt in zip(names, image_source["images"]):
        read_checked(args.images_dir / name, receipt["url"], receipt["sha256"], receipt["bytes"])
        checks.append("Egerton747 " + name + ": image bytes verified")
    print(json.dumps({"status": "PASS", "checks": checks,
                      "ceiling": "Source byte provenance and two metadata counts only; no paleographic, lexical or Voynich validation."}, indent=2))


if __name__ == "__main__":
    main()
