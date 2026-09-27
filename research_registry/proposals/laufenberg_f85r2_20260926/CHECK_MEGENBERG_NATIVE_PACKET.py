#!/usr/bin/env python3
"""Check recorded Cgm38 source bytes and scope, not visual or semantic truth.

Use --fetch to restore only missing, explicitly recorded source derivatives.
No Voynich data, OCR or unrecorded manuscript face is accessed.
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
inventory = json.loads((base / "MEGENBERG_NATIVE_ACCESS_INVENTORY_ROOT.json").read_text())
register = [f"{n}{s}" for n in range(1, 5) for s in "rv"] + ["5r"]
body = ["43r", "43v", "44r", "44v"]
missing = []
for section, expected in (("register", register), ("body", body)):
    rows = inventory[section]
    assert [r["label"].split()[0] for r in rows] == expected
    for row, folio in zip(rows, expected):
        assert row["http_status"] == 200
        url = urllib.parse.urlparse(row["url"])
        assert url.scheme == "https" and url.hostname == "api.digitale-sammlungen.de"
        assert url.path.startswith("/iiif/image/v2/bsb00043227_")
        assert url.path.endswith("/full/3000,/0/default.jpg")
        path = base / "external_cache" / f"cgm38_{folio}_20260927.jpg"
        assert path.name == Path(row["cache"]).name
        if not path.exists() and args.fetch:
            with urllib.request.urlopen(row["url"], timeout=45) as response:
                data = response.read()
            assert len(data) == row["bytes"]
            assert hashlib.sha256(data).hexdigest() == row["sha256"]
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(data)
        if not path.exists():
            missing.append(folio)
            continue
        data = path.read_bytes()
        assert len(data) == row["bytes"]
        assert hashlib.sha256(data).hexdigest() == row["sha256"]

first = json.loads((base / "MEGENBERG_NATIVE_BODY_ROOT_FIRST_RECEIPT.json").read_text())
assert first["whole_body_faces"] == body
assert hashlib.sha256((base / Path(first["file"]).name).read_bytes()).hexdigest() == first["sha256"]
assert (base / "MEGENBERG_NATIVE_ROOT_CORRECTIONS.md").exists()
print(json.dumps({
    "status": "MISSING_SOURCE_CACHE" if missing else "RECORDED_BYTES_AND_FACE_SCOPE_PASS",
    "register_faces": len(register), "body_faces": len(body), "missing": missing,
    "first_notes_byte_preservation": True,
    "first_notes_have_explicit_corrections": True,
    "visual_or_textual_truth_validated": False,
    "voynich_meaning_validated": False,
}, indent=2))
raise SystemExit(bool(missing))
