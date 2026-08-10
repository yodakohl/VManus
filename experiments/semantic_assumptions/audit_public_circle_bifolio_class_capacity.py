#!/usr/bin/env python3
"""Public-source bifolio-level capacity audit for the f67--f73 circle block."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
ATLAS = RESULTS / "public_circle_block_role_atlas.tsv"
OUT = RESULTS / "public_circle_bifolio_class_capacity.json"
OUT_MD = RESULTS / "public_circle_bifolio_class_capacity.md"
URLS = {
    "Q09": "https://www.voynich.nu/q09/index.html",
    "Q10": "https://www.voynich.nu/q10/index.html",
    "Q11": "https://www.voynich.nu/q11/index.html",
    "Q12": "https://www.voynich.nu/q12/index.html",
}
BIFOLIO_BY_FOLIO = {
    "f67": "Q09_f67_f68",
    "f68": "Q09_f67_f68",
    "f69": "Q10_f69_f70",
    "f70": "Q10_f69_f70",
    "f71": "Q11_f71_f72",
    "f72": "Q11_f71_f72",
    "f73": "Q12_f73_f74_missing",
}
PUBLIC_PHRASES = {
    "Q09": "one bifolio composing folios 67 and 68",
    "Q10": "one bifolio composing folios 69 and 70",
    "Q11": "one bifolio composing folios 71 and 72",
    "Q12": "contains the remains of one bifolio, which is folio 73",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "VManus-public-bifolio-audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def visible(data: bytes) -> str:
    value = data.decode("utf-8", "replace")
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def report(result: dict) -> str:
    return (
        "# Public circle-block bifolio class capacity\n\n"
        "Decision: **STOP_UNSCORED_INSUFFICIENT_INDEPENDENT_BIFOLIO_CLASS_SUPPORT**.\n\n"
        "The 26 public f67--f73 panels occupy seven extant folios but only four "
        "bifolio production units: f67+f68, f69+f70, f71+f72, and f73 plus the "
        "missing f74. The page-class counts by bifolio are:\n\n"
        "- Q9: 7 astronomical, 3 cosmological;\n"
        "- Q10: 4 cosmological, 2 zodiac;\n"
        "- Q11: 8 zodiac;\n"
        "- Q12: 2 zodiac on the surviving f73 portion.\n\n"
        "Astronomical material occurs on only Q9, so a bifolio-held classifier "
        "cannot train that class outside its target sheet. Q10 is the only held "
        "sheet where both remaining classes can be trained elsewhere and compared "
        "within one sheet. Its four-versus-two count-preserving orbit has only "
        "15 assignments, so the smallest attainable one-sided p-value is 1/15 "
        "= 0.066667.\n\n"
        "Therefore no Voynich text features were opened and no class score was "
        "computed. Seven physical folios must not be advertised as seven "
        "independent class replications. This supplies no class-specific group, "
        "word, meaning, plaintext, or translation.\n"
    )


def main() -> None:
    live = {name: fetch(url) for name, url in URLS.items()}
    for name, phrase in PUBLIC_PHRASES.items():
        if phrase not in visible(live[name]):
            raise RuntimeError((name, phrase))

    atlas_data = ATLAS.read_bytes()
    unique_pages = {}
    with ATLAS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = row["page"]
            identity = (row["physical_folio"], row["public_page_class"])
            previous = unique_pages.setdefault(key, identity)
            if previous != identity:
                raise RuntimeError((key, previous, identity))

    if len(unique_pages) != 26:
        raise RuntimeError(len(unique_pages))
    by_bifolio = defaultdict(Counter)
    pages_by_bifolio = defaultdict(list)
    for page, (folio, public_class) in sorted(unique_pages.items()):
        bifolio = BIFOLIO_BY_FOLIO[folio]
        by_bifolio[bifolio][public_class] += 1
        pages_by_bifolio[bifolio].append(page)

    expected = {
        "Q09_f67_f68": {"ASTRONOMICAL": 7, "COSMOLOGICAL": 3},
        "Q10_f69_f70": {"COSMOLOGICAL": 4, "ZODIAC": 2},
        "Q11_f71_f72": {"ZODIAC": 8},
        "Q12_f73_f74_missing": {"ZODIAC": 2},
    }
    observed = {key: dict(value) for key, value in by_bifolio.items()}
    if observed != expected:
        raise RuntimeError((observed, expected))

    class_support = defaultdict(list)
    for bifolio, counts in expected.items():
        for public_class in counts:
            class_support[public_class].append(bifolio)
    class_support = {key: sorted(value) for key, value in class_support.items()}

    q10_orbit = math.comb(6, 2)
    result = {
        "experiment": "CBD001_PUBLIC_CIRCLE_BIFOLIO_CLASS_CAPACITY",
        "status": "STOP_UNSCORED_INSUFFICIENT_INDEPENDENT_BIFOLIO_CLASS_SUPPORT",
        "public_sources": {
            name: {"url": URLS[name], "sha256": sha(data), "required_bifolio_phrase_found": True}
            for name, data in live.items()
        },
        "atlas_input": {"path": "experiments/semantic_assumptions/results/public_circle_block_role_atlas.tsv", "sha256": sha(atlas_data)},
        "scope": {"panels": 26, "extant_folios": 7, "bifolio_units": 4},
        "bifolio_class_counts": expected,
        "pages_by_bifolio": {key: value for key, value in sorted(pages_by_bifolio.items())},
        "class_bifolio_support": class_support,
        "held_sheet_capacity": {
            "astronomical_trainable_outside_Q09": False,
            "only_trainable_mixed_held_sheet": "Q10_f69_f70",
            "Q10_count_preserving_assignments": q10_orbit,
            "Q10_minimum_attainable_one_sided_p": 1 / q10_orbit,
            "p_at_most_0_05_attainable": False,
        },
        "gates": {
            "all_26_public_panels_accounted_for": True,
            "all_four_bifolio_sources_publicly_bound": True,
            "every_class_has_two_bifolio_support": False,
            "held_mixed_sheet_can_attain_p_at_most_0_05": False,
            "voynich_text_features_accessed": False,
            "class_score_computed": False,
            "ocr_or_automated_vision_used": False,
        },
        "decision": "STOP_UNSCORED_INSUFFICIENT_INDEPENDENT_BIFOLIO_CLASS_SUPPORT",
        "claim_ceiling": (
            "The 26 public f67--f73 panels provide four bifolio production units, not seven "
            "independent class replications. Astronomical occurs on one bifolio and the sole "
            "trainable mixed cosmological-versus-zodiac sheet has a 15-assignment orbit with "
            "minimum p 1/15. No Voynich feature, class-specific group, word, meaning, plaintext, "
            "or translation follows."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(report(result))


if __name__ == "__main__":
    main()
