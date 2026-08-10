#!/usr/bin/env python3
"""Clean-room live-source validation of F70C001."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parent.parent
RESULTS = BASE / "results"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
PRODUCTION_TSV = RESULTS / "public_central_star_register_rows.tsv"
PRODUCTION_JSON = RESULTS / "public_central_star_register.json"
PRODUCTION_REPORT = RESULTS / "public_central_star_register_report.md"
OUT = RESULTS / "public_central_star_register_validation.json"
REPORT = RESULTS / "public_central_star_register_validation.md"

URLS = {
    "q10": ("https://www.voynich.nu/q10/index.html", "2f15159cd9ea04213f2031fbbebe33e3b057795656e349bf765e4f0344ff2ec5"),
    "q08": ("https://www.voynich.nu/q08/index.html", "ce3df63cb48cf440faa2d637b382b7665b992a55709b5a721fdce078e21e42d7"),
}
MANUALS = {
    "ZL3b": (REPO / "transcription/sources/ZL3b-n.txt", "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc"),
    "IT2a": (REPO / "transcription/sources/IT2a-n.txt", "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5"),
    "RF1b": (REPO / "transcription/sources/RF1b-e.txt", "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782"),
}
EXACT_SHA = "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61"

ARRAYS = {
    "F69R_INNER_STAR": ["f69r.45", "f69r.46", "f69r.47", "f69r.48", "f69r.49", "f69r.44"],
    "F69R_OUTER_RADIAL": [f"f69r.{i}" for i in range(21, 43)],
    "F70R1_INNER_STAR": ["f70r1.15", "f70r1.16", "f70r1.17", "f70r1.18", "f70r1.19", "f70r1.14"],
    "F70R1_OUTER_RADIAL": ["f70r1.6", "f70r1.7", "f70r1.8", "f70r1.9", "f70r1.10", "f70r1.11", "f70r1.12", "f70r1.4", "f70r1.5"],
    "F70V2_INNER_LABEL_BAND": [f"f70v2.{i}" for i in range(23, 32)] + ["f70v2.22"],
    "F70V2_OUTER_LABEL_BAND": [f"f70v2.{i}" for i in range(5, 21)] + ["f70v2.2", "f70v2.3", "f70v2.4"],
}
UNIT_KEYS = {
    "F69R_INNER_STAR": ("f69r", "K1"),
    "F69R_OUTER_RADIAL": ("f69r", "E1"),
    "F70R1_INNER_STAR": ("f70r1", "X1"),
    "F70R1_OUTER_RADIAL": ("f70r1", "Y1"),
    "F70V2_INNER_LABEL_BAND": ("f70v2", "S1"),
    "F70V2_OUTER_LABEL_BAND": ("f70v2", "S2"),
}
ROW_RE = re.compile(r"^<([^,>]+),[^>]+>\s+(.*)$")
SEP_RE = re.compile(r"(?:<->|[.,])")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def check(value: bool, name: str, checks: list[str]) -> None:
    if not value:
        raise AssertionError(name)
    checks.append(name)


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus F70C001 validator"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def manual_rows(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        locus, surface = match.groups()
        if locus in result:
            raise AssertionError(f"duplicate:{locus}")
        surface = re.sub(r"^(?:<![^>]*>)+", "", surface.strip())
        surface = re.sub(r"(?:<\$>|<\|>)+$", "", surface)
        result[locus] = surface
    return result


def count_groups(surface: str) -> int:
    return len([part for part in SEP_RE.split(surface) if part.strip()])


def main() -> None:
    for path in (OUT, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")
    checks: list[str] = []

    live = {name: get(url) for name, (url, _) in URLS.items()}
    for name, (_url, expected) in URLS.items():
        check(sha_bytes(live[name]) == expected, f"live_{name}_hash", checks)
    live_text = {
        name: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", data.decode("utf-8"))).strip()
        for name, data in live.items()
    }
    for phrase in (
        "In the six areas between the arms of the star are individual letters",
        "nine short lines of radial text just inside the outer circles and six words of radial text inside the inner circle",
        "The central star is similar to that on f69r",
    ):
        check(phrase in live_text["q10"], f"q10_phrase_{len(checks)}", checks)
    check("There are four short texts radiating from the centre and four labels near the persons" in live_text["q08"], "q08_comparator_phrase", checks)

    check(sha(EXACT) == EXACT_SHA, "exact_annotation_hash", checks)
    with EXACT.open(encoding="utf-8", newline="") as handle:
        annotations = list(csv.DictReader(handle, delimiter="\t"))
    for name, (page, unit) in UNIT_KEYS.items():
        loci = {row["locus"] for row in annotations if row["page"] == page and row["unit"] == unit}
        check(loci == set(ARRAYS[name]), f"unit_mapping_{name}", checks)

    sources = {}
    for edition, (path, expected) in MANUALS.items():
        check(sha(path) == expected, f"manual_hash_{edition}", checks)
        sources[edition] = manual_rows(path)

    rebuilt = []
    summaries = {}
    for array, loci in ARRAYS.items():
        summaries[array] = {}
        for edition in ("ZL3b", "IT2a", "RF1b"):
            values = []
            for locus in loci:
                surface = sources[edition][locus]
                count = count_groups(surface)
                check(count > 0, f"nonempty_{array}_{edition}_{locus}", checks)
                values.append(count)
                rebuilt.append({
                    "array": array, "edition": edition, "locus": locus,
                    "source_group_count": str(count), "surface": surface,
                })
            summaries[array][edition] = {
                "loci": len(values), "minimum": min(values), "maximum": max(values),
                "mean": sum(values) / len(values),
                "distribution": {str(key): value for key, value in sorted(Counter(values).items())},
            }

    with PRODUCTION_TSV.open(encoding="utf-8", newline="") as handle:
        stored_rows = list(csv.DictReader(handle, delimiter="\t"))
    check(stored_rows == rebuilt, "exact_row_inventory", checks)
    check(len(rebuilt) == 216, "row_count_216", checks)
    check(count_groups("cho@152;al") == 1, "entity_is_not_separator", checks)
    check(count_groups("cho.al") == 2, "dot_is_separator", checks)
    check(count_groups("cho,al") == 2, "comma_is_separator", checks)
    check(count_groups("cho<->al") == 2, "drawing_break_is_separator", checks)

    for edition in ("ZL3b", "IT2a", "RF1b"):
        check(summaries["F69R_INNER_STAR"][edition]["distribution"] == {"1": 6}, f"f69_inner_{edition}", checks)
        check(summaries["F70R1_INNER_STAR"][edition]["distribution"] == {"1": 6}, f"f70_inner_{edition}", checks)
        check(summaries["F69R_OUTER_RADIAL"][edition]["mean"] > 1, f"f69_outer_{edition}", checks)
        check(summaries["F70R1_OUTER_RADIAL"][edition]["mean"] > 1, f"f70_outer_{edition}", checks)

    directions = {}
    for edition in ("ZL3b", "IT2a", "RF1b"):
        inner = summaries["F70V2_INNER_LABEL_BAND"][edition]["mean"]
        outer = summaries["F70V2_OUTER_LABEL_BAND"][edition]["mean"]
        direction = "INNER_SHORTER" if inner < outer else "INNER_LONGER" if inner > outer else "TIE"
        directions[edition] = {"inner_mean": inner, "outer_mean": outer, "direction": direction}
    check({item["direction"] for item in directions.values()} == {"INNER_SHORTER", "INNER_LONGER"}, "comparator_direction_disagreement", checks)

    production = json.loads(PRODUCTION_JSON.read_text(encoding="utf-8"))
    check(production["status"] == "LOCAL_CENTRAL_STAR_COMPACT_REGISTER_GENERALIZATION_STOPPED", "status", checks)
    check(production["decision"] == "RETAIN_LOCAL_ROLE_CONTRAST_ONLY", "decision", checks)
    check(production["arrays"] == summaries, "all_summaries", checks)
    check(production["f70v2_universal_rule_comparator"] == directions, "comparator", checks)
    check(not production["gates"]["universal_inner_shorter_rule_supported_by_f70v2"], "universal_gate_false", checks)
    for key in (
        "zero_retained_parser_root_or_grammar_field_used",
        "zero_ocr_or_automated_vision",
        "zero_english_lexical_gloss",
    ):
        check(production["gates"][key], key, checks)
    check("No planet, apsis, sphere, wind, number" in production["claim_ceiling"], "claim_ceiling", checks)

    report = PRODUCTION_REPORT.read_text(encoding="utf-8")
    for phrase in (
        "The grouping was not accepted from a prompt",
        "3.000/3.091/2.955",
        "2.111/2.222/1.778",
        "not a universal centre-to-edge grammar",
        "No PLANET, APSIS, SPHERE, WIND, NUMBER",
    ):
        check(phrase in report, f"report_{len(checks)}", checks)

    validation = {
        "experiment": "F70C001_PUBLIC_CENTRAL_STAR_REGISTER_VALIDATION",
        "status": "PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION",
        "checks": len(checks),
        "failures": [],
        "production_hashes": {
            "rows": sha(PRODUCTION_TSV), "json": sha(PRODUCTION_JSON), "report": sha(PRODUCTION_REPORT),
        },
        "reconstructed_rows": len(rebuilt),
        "decision": production["decision"],
        "target_strings_scored_for_meaning": False,
        "ocr_or_automated_vision_used": False,
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# F70C001 validation\n\n"
        f"Status: `PASS_INDEPENDENT_LIVE_SOURCE_RECONSTRUCTION` ({len(checks)} checks).\n\n"
        "Clean-room code downloaded both public catalogue pages, reparsed all three manual transcriptions, reconstructed all 216 array-reading rows and source-group summaries, and reproduced the local-only decision. It also verifies that an IVTFF glyph entity is not mistaken for a separator. No retained parser, OCR, automated vision, semantic score, or English gloss was used.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
