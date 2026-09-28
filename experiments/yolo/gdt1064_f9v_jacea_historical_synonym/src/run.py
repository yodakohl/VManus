#!/usr/bin/env python3
"""Emit the fixed, post-exposure historical-name adjudication packet."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def main() -> int:
    source = HERE / "src/YACEA_GART_1485.jpg"
    if not source.is_file():
        raise SystemExit("missing fixed historical facsimile")
    result = {
        "experiment_id": "GDT1064",
        "design": "post-exposure source-only correction; no prospective semantic score",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "historical_entry": {
            "work": "Gart der Gesundheit, Mainz 1485, chapter 432",
            "visible_labels": ["yacea", "freyschem krut"],
            "image_owner": "pansy-like five-petalled herb",
            "source_url": "https://commons.wikimedia.org/wiki/File:Yacea_Gart.jpg",
        },
        "external_decoder": {
            "f9v_first_group": "fochor",
            "published_form": "JACEA",
            "published_expansion": "knapweed",
            "published_visual_id": "Wild pansy",
        },
        "decision": "BARE_JACEA_HISTORICALLY_COMPATIBLE_WITH_PANSY__KNAPWEED_EXPANSION_STILL_CONFLICTS__NO_WORD_CONFIRMATION",
        "translated_words_confirmed": 0,
    }
    out = HERE / "artifacts/RESULT.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
