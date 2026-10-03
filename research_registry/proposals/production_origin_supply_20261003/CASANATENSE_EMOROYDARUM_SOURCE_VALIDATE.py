#!/usr/bin/env python3
"""Check acquisition integrity only; this does not validate Latin readings."""
import argparse
import hashlib
import json
from pathlib import Path
import re

PREFIX = "CASANATENSE_EMOROYDARUM_SOURCE_"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, help="Optional directory containing original/crop bytes")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    receipt_bytes = (folder / (PREFIX + "RECEIPT.json")).read_bytes()
    receipt = json.loads(receipt_bytes)
    frozen = receipt["transcription_freeze"]
    text_bytes = (folder / frozen["file"]).read_bytes()
    checks = {
        "frozen_transcription_sha256": digest(text_bytes) == frozen["sha256"],
        "frozen_transcription_bytes": len(text_bytes) == frozen["bytes"],
        "physical_line_numbers": re.findall(r"^(\d{2}) ", text_bytes.decode(), re.M) == [f"{n:02d}" for n in range(1, 16)],
        "unique_locator_record": receipt["identity_query"]["result"]["pager"]["total"] == 1,
        "institutional_locator": receipt["item_metadata"]["fields"]["identi"] == "MS0459C0019V",
        "complete_extent_without_continuation": receipt["entry_extent"]["continuation_acquired"] is False,
        "uncertainty_retained": frozen["letters_secure"] is False and "[...unread...]" in text_bytes.decode(),
    }
    images = []
    if args.cache:
        records = [receipt["primary_image"], receipt["earlier_lower_resolution_image"]] + receipt["native_views"]["crops"]
        for record in records:
            data = (args.cache / record["file"]).read_bytes()
            good = digest(data) == record["sha256"] and len(data) == record["bytes"]
            images.append({"file": record["file"], "sha256_and_bytes_match": good})
    result = {
        "kind": "source-acquisition-integrity-only",
        "receipt_sha256": digest(receipt_bytes),
        "checks": checks,
        "cached_images": images,
        "integrity_pass": all(checks.values()) and all(x["sha256_and_bytes_match"] for x in images),
        "manual_reading_status": "Complete entry extent inspected; unresolved letters, abbreviations, conditional hinge and application forms retained. Latin correctness is not an executable check.",
        "scope": "One public historical source folio; no target inference or experiment selection.",
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    raise SystemExit(0 if result["integrity_pass"] else 1)


if __name__ == "__main__":
    main()
