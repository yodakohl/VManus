#!/usr/bin/env python3
"""Validate source provenance for the manual f69r.49 reading QC.

This script checks files, metadata, dimensions, source readings, and the human
annotation. It does not and cannot validate the human visual judgment.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
ANNOTATIONS = (
    ROOT / "experiments" / "semantic_assumptions" / "results"
    / "existing_human_exact_locus_annotations.tsv"
)
SOURCES = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
IMAGES = {
    "2004": {
        "url": "https://www.voynich.com/folios/color/069r.jpg",
        "sha256": "093f4550a86050db1264870f9dd41e847f9b91d0b25141253ff845c1eab514ff",
        "size": (1152, 1536),
    },
    "2014": {
        "url": "https://archive.org/download/voynich/125.jpg",
        "sha256": "803e02a64a0f68a6fe38ec5b50c5167a47888ade4221b5088f637ce2b34f84a7",
        "size": (2793, 3763),
    },
}


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-QC/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> None:
    checks = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    catalogue = download("https://www.voynich.nu/q10/index.html").decode(
        "utf-8", errors="replace"
    )
    check("human catalogue identifies f69r", 'ID="f69r"' in catalogue)
    check("human catalogue maps Yale child 1006198", (
        "child_oid=1006198" in catalogue
    ))
    gallery = download("https://www.voynich.nu/gallery.html").decode(
        "utf-8", errors="replace"
    )
    check("gallery documents 2004 and 2014 digitizations", (
        "first time, in 2004" in gallery and "second time, in 2014" in gallery
    ))
    metadata = json.loads(download("https://archive.org/metadata/voynich"))
    description = metadata["metadata"]["description"]
    check("archive metadata identifies 2014 Yale JP2 origin", (
        "Original 2014 scan jp2 files downloaded from" in description
        and "brbl-dl.library.yale.edu" in description
    ))
    file_entry = next(row for row in metadata["files"] if row["name"] == "125.jpg")
    check("archive file identity and size", (
        file_entry["size"] == "9094436"
        and file_entry["sha1"] == "b77a906e03f4976659c240320ba23b30f8515df1"
    ))

    with tempfile.TemporaryDirectory(prefix="vmanus_f69_qc_") as directory:
        for label, specification in IMAGES.items():
            data = download(specification["url"])
            check(f"{label} image SHA-256", (
                hashlib.sha256(data).hexdigest() == specification["sha256"]
            ))
            path = Path(directory) / f"{label}.jpg"
            path.write_bytes(data)
            with Image.open(path) as image:
                check(f"{label} image dimensions", image.size == specification["size"])

    expected_lines = {
        "ZL3b": r"<f69r\.49,@L0>\s+<!6>e\[d:g\]",
        "IT2a": r"<f69r\.49,@L0>\s+em\s*$",
        "RF1b": r"<f69r\.49,@L0>\s+ed\s*$",
    }
    for reading, path in SOURCES.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        check(f"{reading} exact recorded alternate", (
            re.search(expected_lines[reading], text, re.M) is not None
        ))

    with ANNOTATIONS.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["locus"] == "f69r.49"]
    check("one exact human annotation", len(matches) == 1)
    check("annotation clock and original-MS confirmation", (
        matches[0]["local_comment"].startswith("At 07:30.")
        and "confirmed" in matches[0]["local_comment"]
        and "@'ed' against the original MS" in matches[0]["local_comment"]
    ))
    print(json.dumps({
        "status": "PASS",
        "checks": len(checks),
        "scope": "source provenance only; human visual judgment not automated",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
