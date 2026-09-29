#!/usr/bin/env python3
"""Restore only the eleven public F source files at their recorded hashes."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent
receipts = json.loads((BASE / "F_SOURCE_RECEIPTS.json").read_text())["source_receipts"]
assert len(receipts) == 11
fetched = 0
for receipt in receipts:
    name = Path(receipt["file"]).name
    assert name.startswith("F_") and name == receipt["file"].rsplit("/", 1)[-1]
    url = urlparse(receipt["url"])
    assert url.scheme == "https" and url.hostname in {"mateo.uni-mannheim.de", "ica.themorgan.org"}
    path = BASE / name
    if path.exists():
        data = path.read_bytes()
    else:
        with urlopen(Request(receipt["url"], headers={"User-Agent": "Mozilla/5.0"}), timeout=30) as response:
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == receipt["sha256"], name
        path.write_bytes(data)
        fetched += 1
    assert hashlib.sha256(data).hexdigest() == receipt["sha256"], name
    assert len(data) == receipt["bytes"], name
print(json.dumps({"source_files_verified": len(receipts), "newly_fetched": fetched,
                  "target_files_opened": 0, "meaning_verified": False}))
