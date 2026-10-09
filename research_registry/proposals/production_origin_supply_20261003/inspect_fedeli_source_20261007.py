"""Inspect the deposited edition without rendering XSL or normalizing readings.

Usage: python inspect_fedeli_source_20261007.py EXTERNAL_CACHE_DIRECTORY
Downloads only six fixed files of the selected edition; prints a JSON receipt.
Raw source files must remain outside the repository. No Voynich data are read.
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://epapers.bham.ac.uk/id/eprint/1964/1/"
FILES = ("start.xml", "NTstart.xsl", "Arabic1.xsl", "Q18_Birm1572a.xml",
         "Q19_Birm1572a.xml", "Q20_Birm1572a.xml")
NS = {"t": "http://www.tei-c.org/ns/1.0"}
cache = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[3]
if cache == repo or repo in cache.parents:
    raise SystemExit("Use an external cache directory; do not add source bytes to the repository.")
cache.mkdir(parents=True, exist_ok=True)
receipts = []
for name in FILES:
    target = cache / name
    if not target.exists():
        with urllib.request.urlopen(BASE + name, timeout=30) as response:
            target.write_bytes(response.read())
    raw = target.read_bytes()
    root = ET.fromstring(raw)
    item = {"name": name, "url": BASE + name, "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}
    if name.startswith("Q"):
        item["elements"] = dict(collections.Counter(
            e.tag.rsplit("}", 1)[-1] for e in root.iter()))
        item["supplied_attributes"] = [e.attrib for e in root.findall(".//t:supplied", NS)]
        labels = [e.get("n") for e in root.findall(".//t:ab", NS)]
        item["duplicate_verse_labels"] = [k for k, v in collections.Counter(labels).items() if v > 1]
        item["encoding_description_nonempty"] = any(
            "".join(e.itertext()).strip() for e in root.findall(".//t:encodingDesc", NS))
    receipts.append(item)
print(json.dumps({"inspected_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "files": receipts}, indent=2, ensure_ascii=False))
