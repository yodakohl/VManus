#!/usr/bin/env python3
"""Re-fetch the fixed external institutional assets; no Voynich sources."""
import hashlib
import json
from pathlib import Path
import urllib.request


def main():
    base = Path(__file__).resolve().parent
    receipt = json.loads((base / "EXTERNAL_RECEIPTS.json").read_text())
    for entry in receipt["assets"]:
        destination = base / "external_cache" / entry["filename"]
        destination.parent.mkdir(exist_ok=True)
        if destination.exists():
            data = destination.read_bytes()
        else:
            request = urllib.request.Request(entry["url"], headers={"User-Agent": "manuscript-source-check/1.0"})
            with urllib.request.urlopen(request, timeout=60) as response:
                data = response.read()
            destination.write_bytes(data)
        actual = hashlib.sha256(data).hexdigest()
        if actual != entry["sha256"]:
            raise ValueError(f"Changed bytes: {entry['filename']}: {actual}")
        print(f"OK {entry['filename']} {actual}")


if __name__ == "__main__":
    main()
