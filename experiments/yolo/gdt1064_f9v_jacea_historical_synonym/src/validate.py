#!/usr/bin/env python3
"""Check packet identity and declared limits, not historical reading truth."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def main() -> int:
    obj = json.loads((HERE / "artifacts/RESULT.json").read_text(encoding="utf-8"))
    source = HERE / "src/YACEA_GART_1485.jpg"
    checks = {
        "source_byte_identity": source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == obj["source_sha256"],
        "historical_name_pair_retained": obj["historical_entry"]["visible_labels"] == ["yacea", "freyschem krut"],
        "published_ambiguity_retained": obj["external_decoder"]["published_form"] == "JACEA" and obj["external_decoder"]["published_expansion"] == "knapweed",
        "no_semantic_promotion": obj["translated_words_confirmed"] == 0,
        "post_exposure_marked": obj["design"].startswith("post-exposure"),
    }
    out = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
           "limit": "Mechanical validation does not establish historical transcription or Voynich meaning."}
    (HERE / "artifacts/VALIDATION.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
