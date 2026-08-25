#!/usr/bin/env python3
"""Compact validator for Pass 1019."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    contexts = read_tsv("PASS1019_12_VISUAL_CORE_CONTEXTS.tsv")
    pages = read_tsv("PASS1019_FOUR_IMAGE_CORE_TABLE.tsv")
    herbal_pharma = read_tsv("HERBAL_PHARMA_VISUAL_CORE_CONTEXTS.tsv")
    bio_astro = read_tsv("BIO_ASTRO_VISUAL_CORE_CONTEXTS.tsv")
    checks = {
        "twelve_contexts": len(contexts) == 12,
        "four_pages": len(pages) == 4,
        "three_contexts_per_page": Counter(r["page"] for r in contexts) == Counter({"f13r": 3, "f75r": 3, "f67r2": 3, "f88r": 3}),
        "four_registers": {r["register"] for r in contexts} == {"HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"},
        "unique_statements": len({r["statement_id"] for r in contexts}) == 12,
        "all_have_surfaces": all(r["surface_sequence"] for r in contexts),
        "all_have_components": all(r["component_sequence"] for r in contexts),
        "all_have_image_hash": all(len(r["image_sha256"]) == 64 for r in contexts),
        "all_keep_three_core_contract": all(r["decision"] == "KEEP_WERT_ANTEIL_EINHEIT_WITH_REGISTER_LOCAL_EXPANSION" for r in contexts),
        "no_image_contradiction": all(r["visual_fit"] in {"STARK", "PLAUSIBEL"} for r in contexts),
        "all_three_roots_seen": {root for r in contexts for root in r["portable_roots_present"].split("+")} == {"WERT", "ANTEIL", "EINHEIT"},
        "no_new_pages": {r["page"] for r in contexts} == {"f13r", "f75r", "f67r2", "f88r"},
        "no_sealed_pages": all(not r["page"].startswith("f84") for r in contexts),
        "no_empty_page_values": all(all(value for value in r.values()) for r in pages),
        "eight_herbal_pharma_counterreads": len(herbal_pharma) == 8,
        "eight_bio_astro_counterreads": len(bio_astro) == 8,
        "counterread_page_split": (
            {r["page"] for r in herbal_pharma} == {"f13r", "f88r"}
            and {r["page"] for r in bio_astro} == {"f75r", "f67r2"}
        ),
        "counterreads_have_no_rejection": all(
            "CONTRADICTION" not in (r.get("decision") or r.get("visual_verdict") or "")
            for r in herbal_pharma + bio_astro
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    result = {"status": "PASS" if not failures else "FAIL", "checks": checks, "failures": failures}
    (OUT / "PASS1019_VALIDATION.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
