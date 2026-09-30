"""Reproduce external source capture bytes; never validates native readings."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent
RECEIPTS = BASE.parent / "external_cache" / "DB_UU_IMAGE_RECEIPTS.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Download the three recorded public source originals")
    args = parser.parse_args()
    rows = json.loads(RECEIPTS.read_text())
    assert [r["canvas_ordinal"] for r in rows] == [212, 225, 252]
    results = []
    for row in rows:
        path = RECEIPTS.parent / ("DB_UU_CANVAS_%s.jpg" % row["canvas_ordinal"])
        assert row["url"].startswith("https://objects.library.uu.nl/")
        if args.fetch:
            with urlopen(row["url"], timeout=35) as response:
                data = response.read()
            assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
            path.write_bytes(data)
        data = path.read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"]
        results.append({"canvas_ordinal": row["canvas_ordinal"], "bytes_and_sha256_match": True})
    print(json.dumps({"status": "CAPTURE_ACCOUNTING_PASS", "checks": results,
                      "not_checked": ["native transcription", "code granularity", "Voynich meaning"]}, indent=2))


if __name__ == "__main__":
    main()
