#!/usr/bin/env python3
"""Check the fixed 18-face source packet; --fetch restores only recorded images.

Byte and coverage checks do not reproduce native visual or semantic judgments.
"""
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

base = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--fetch", action="store_true")
args = parser.parse_args()
receipt = json.loads((base / "ROYAL_PROGRAM_NATIVE_SOURCE_RECEIPT.json").read_text())
expected = [f"{n}{side}" for n in range(50, 59) for side in "rv"]
assert [r["folio"] for r in receipt["images"]] == expected
for key in ("decision", "root_first"):
    p = base / Path(receipt[f"{key}_path"]).name
    assert hashlib.sha256(p.read_bytes()).hexdigest() == receipt[f"{key}_sha256"]
missing = []
for row in receipt["images"]:
    url = urllib.parse.urlparse(row["url"])
    assert url.scheme == "https" and url.hostname == "bl.digirati.io"
    assert url.path.startswith("/images/ark:/81055/")
    assert url.path.endswith("/full/2200,/0/default.jpg")
    name = f"royal19ci_{row['folio']}_20260927.jpg"
    assert Path(row["path"]).name == name
    path = base / "external_cache" / name
    if not path.exists() and args.fetch:
        with urllib.request.urlopen(row["url"], timeout=45) as response:
            data = response.read()
        assert len(data) == row["bytes"]
        assert hashlib.sha256(data).hexdigest() == row["sha256"]
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
    if not path.exists():
        missing.append(row["folio"])
        continue
    data = path.read_bytes()
    assert len(data) == row["bytes"]
    assert hashlib.sha256(data).hexdigest() == row["sha256"]
notes = (base / "ROYAL_PROGRAM_NATIVE_ROOT_FIRST.md").read_text()
assert all(f"|{folio}|" in notes for folio in expected)
print(json.dumps({
    "status": "MISSING_SOURCE_CACHE" if missing else "FIXED_PACKET_BYTES_AND_COVERAGE_PASS",
    "selected_faces": 18, "missing": missing,
    "native_visual_truth_validated": False,
    "full_text_transcription_validated": False,
    "voynich_meaning_validated": False,
}, indent=2))
raise SystemExit(bool(missing))
