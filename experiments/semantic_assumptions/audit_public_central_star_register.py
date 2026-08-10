#!/usr/bin/env python3
"""Audit the public f69r/f70r1 central-star text register.

This consumes only public human catalogue prose and public manual
transcriptions.  It deliberately bypasses the incomplete retained parser.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parent.parent
RESULTS = BASE / "results"
Q10 = BASE / "cache/public_voynich_nu_catalogue/q10.html"
Q08 = BASE / "cache/public_voynich_nu_catalogue/q08.html"
EXACT = RESULTS / "existing_human_exact_locus_annotations.tsv"
SOURCES = {
    "ZL3b": REPO / "transcription/sources/ZL3b-n.txt",
    "IT2a": REPO / "transcription/sources/IT2a-n.txt",
    "RF1b": REPO / "transcription/sources/RF1b-e.txt",
}
OUT_TSV = RESULTS / "public_central_star_register_rows.tsv"
OUT_JSON = RESULTS / "public_central_star_register.json"
REPORT = RESULTS / "public_central_star_register_report.md"

EXPECTED_HASHES = {
    "experiments/semantic_assumptions/cache/public_voynich_nu_catalogue/q10.html":
        "2f15159cd9ea04213f2031fbbebe33e3b057795656e349bf765e4f0344ff2ec5",
    "experiments/semantic_assumptions/cache/public_voynich_nu_catalogue/q08.html":
        "ce3df63cb48cf440faa2d637b382b7665b992a55709b5a721fdce078e21e42d7",
    "experiments/semantic_assumptions/results/existing_human_exact_locus_annotations.tsv":
        "79c7f06e91f90054aff4cdf27f098a5977d820acdf91f239a14c6ddf553a7f61",
    "transcription/sources/ZL3b-n.txt":
        "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "transcription/sources/IT2a-n.txt":
        "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5",
    "transcription/sources/RF1b-e.txt":
        "e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782",
}

PUBLIC_URLS = {
    "q10": "https://www.voynich.nu/q10/index.html",
    "q08": "https://www.voynich.nu/q08/index.html",
    "f69r_detail": "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f69r.htm",
    "f70r1_detail": "https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f70r1.htm",
}

ARRAYS = {
    "F69R_INNER_STAR": ["f69r.45", "f69r.46", "f69r.47", "f69r.48", "f69r.49", "f69r.44"],
    "F69R_OUTER_RADIAL": [f"f69r.{number}" for number in range(21, 43)],
    "F70R1_INNER_STAR": ["f70r1.15", "f70r1.16", "f70r1.17", "f70r1.18", "f70r1.19", "f70r1.14"],
    "F70R1_OUTER_RADIAL": ["f70r1.6", "f70r1.7", "f70r1.8", "f70r1.9", "f70r1.10", "f70r1.11", "f70r1.12", "f70r1.4", "f70r1.5"],
    "F70V2_INNER_LABEL_BAND": [f"f70v2.{number}" for number in range(23, 32)] + ["f70v2.22"],
    "F70V2_OUTER_LABEL_BAND": [f"f70v2.{number}" for number in range(5, 21)] + ["f70v2.2", "f70v2.3", "f70v2.4"],
}

EXPECTED_UNITS = {
    "F69R_INNER_STAR": ("f69r", "K1", 6),
    "F69R_OUTER_RADIAL": ("f69r", "E1", 22),
    "F70R1_INNER_STAR": ("f70r1", "X1", 6),
    "F70R1_OUTER_RADIAL": ("f70r1", "Y1", 9),
    "F70V2_INNER_LABEL_BAND": ("f70v2", "S1", 10),
    "F70V2_OUTER_LABEL_BAND": ("f70v2", "S2", 19),
}

ROW_RE = re.compile(r"^<([^,>]+),([^>]+)>\s+(.*)$")
LEADING_NOTE_RE = re.compile(r"^(?:<![^>]*>)+")
TRAILING_NOTE_RE = re.compile(r"(?:<\$>|<\|>)+$")
SEPARATOR_RE = re.compile(r"(?:<->|[.,])")
FIELDS = ("array", "edition", "locus", "source_group_count", "surface")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_write(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_manual(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        locus, _code, body = match.groups()
        if locus in rows:
            raise AssertionError(f"duplicate locus {locus} in {path}")
        body = LEADING_NOTE_RE.sub("", body.strip())
        body = TRAILING_NOTE_RE.sub("", body)
        rows[locus] = body
    return rows


def source_groups(surface: str) -> list[str]:
    groups = [part.strip() for part in SEPARATOR_RE.split(surface) if part.strip()]
    if not groups:
        raise AssertionError(f"empty surface after source split: {surface!r}")
    return groups


def html_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="strict")
    raw = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def summary(rows: list[dict[str, object]], array: str, edition: str) -> dict[str, object]:
    values = [int(row["source_group_count"]) for row in rows if row["array"] == array and row["edition"] == edition]
    assert len(values) == len(ARRAYS[array])
    return {
        "loci": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "mean": sum(values) / len(values),
        "distribution": {str(key): value for key, value in sorted(Counter(values).items())},
    }


def main() -> None:
    for path in (OUT_TSV, OUT_JSON, REPORT):
        if path.exists():
            raise SystemExit(f"refusing overwrite: {path}")

    paths = [Q10, Q08, EXACT, *SOURCES.values()]
    actual_hashes = {str(path.relative_to(REPO)): digest(path) for path in paths}
    assert actual_hashes == EXPECTED_HASHES

    q10 = html_text(Q10)
    q08 = html_text(Q08)
    required_q10 = (
        "In the six areas between the arms of the star are individual letters",
        "nine short lines of radial text just inside the outer circles and six words of radial text inside the inner circle",
        "The central star is similar to that on f69r",
    )
    required_q08 = (
        "4 items of writing along radii",
        "There are four short texts radiating from the centre and four labels near the persons",
    )
    assert all(phrase in q10 for phrase in required_q10)
    assert all(phrase in q08 for phrase in required_q08)

    exact = read_tsv(EXACT)
    for name, (page, unit, count) in EXPECTED_UNITS.items():
        loci = [row["locus"] for row in exact if row["page"] == page and row["unit"] == unit]
        assert len(loci) == count
        assert set(loci) == set(ARRAYS[name])

    manuals = {edition: parse_manual(path) for edition, path in SOURCES.items()}
    rows: list[dict[str, object]] = []
    for array, loci in ARRAYS.items():
        for edition in ("ZL3b", "IT2a", "RF1b"):
            manual = manuals[edition]
            for locus in loci:
                assert locus in manual
                surface = manual[locus]
                rows.append({
                    "array": array,
                    "edition": edition,
                    "locus": locus,
                    "source_group_count": len(source_groups(surface)),
                    "surface": surface,
                })

    summaries = {
        array: {edition: summary(rows, array, edition) for edition in ("ZL3b", "IT2a", "RF1b")}
        for array in ARRAYS
    }
    for edition in ("ZL3b", "IT2a", "RF1b"):
        assert summaries["F69R_INNER_STAR"][edition]["minimum"] == 1
        assert summaries["F69R_INNER_STAR"][edition]["maximum"] == 1
        assert summaries["F70R1_INNER_STAR"][edition]["minimum"] == 1
        assert summaries["F70R1_INNER_STAR"][edition]["maximum"] == 1
        assert summaries["F69R_OUTER_RADIAL"][edition]["mean"] > 1
        assert summaries["F70R1_OUTER_RADIAL"][edition]["mean"] > 1

    comparator_directions = {}
    universal_inner_shorter = True
    for edition in ("ZL3b", "IT2a", "RF1b"):
        inner = summaries["F70V2_INNER_LABEL_BAND"][edition]["mean"]
        outer = summaries["F70V2_OUTER_LABEL_BAND"][edition]["mean"]
        direction = "INNER_SHORTER" if inner < outer else "INNER_LONGER" if inner > outer else "TIE"
        comparator_directions[edition] = {"inner_mean": inner, "outer_mean": outer, "direction": direction}
        universal_inner_shorter &= inner < outer
    assert not universal_inner_shorter

    gates = {
        "public_catalogue_hashes_bound": True,
        "manual_source_hashes_bound": True,
        "public_prose_confirms_both_six_slot_star_arrays": True,
        "all_central_star_items_one_source_group_all_readings": True,
        "both_surrounding_radial_arrays_longer_mean_all_readings": True,
        "universal_inner_shorter_rule_supported_by_f70v2": universal_inner_shorter,
        "zero_retained_parser_root_or_grammar_field_used": True,
        "zero_ocr_or_automated_vision": True,
        "zero_english_lexical_gloss": True,
    }
    result = {
        "experiment": "F70C001_PUBLIC_CENTRAL_STAR_REGISTER",
        "status": "LOCAL_CENTRAL_STAR_COMPACT_REGISTER_GENERALIZATION_STOPPED",
        "decision": "RETAIN_LOCAL_ROLE_CONTRAST_ONLY",
        "inputs": actual_hashes,
        "public_urls": PUBLIC_URLS,
        "arrays": summaries,
        "f70v2_universal_rule_comparator": comparator_directions,
        "gates": gates,
        "claim_ceiling": (
            "On f69r and f70r1 only, the six text items between the arms of a central six-pointed star form a more compact source-group register than the surrounding radial arrays. The public sources classify the f69r items as individual letter labels and the f70r1 items as word labels, so the shared layout does not establish one shared textual scale or semantic field. The f70v2 comparison blocks a universal inner-versus-outer compactness rule. No planet, apsis, sphere, wind, number, abbreviation, word meaning, plaintext, or translation follows."
        ),
    }

    tsv = ["\t".join(FIELDS)]
    for row in rows:
        tsv.append("\t".join(str(row[field]).replace("\t", " ").replace("\n", " ") for field in FIELDS))
    canonical_write(OUT_TSV, "\n".join(tsv) + "\n")
    canonical_write(OUT_JSON, json.dumps(result, indent=2, sort_keys=True) + "\n")

    lines = [
        "# F70C001 public central-star register audit",
        "",
        "Decision: `RETAIN_LOCAL_ROLE_CONTRAST_ONLY`.",
        "",
        "The grouping was not accepted from a prompt. Public human catalogues independently describe both f69r and f70r1 as six-pointed central-star diagrams with six text items between the arms. The same sources call the f69r items individual letter labels, but the f70r1 items word labels; f70r1 also has nine surrounding radial phrases.",
        "",
        "The three public manual readings agree on the robust source-group result. All 12 central-star loci are one source group in every reading. The f69r 22-item outer array averages "
        + "/".join(f"{summaries['F69R_OUTER_RADIAL'][ed]['mean']:.3f}" for ed in ("ZL3b", "IT2a", "RF1b"))
        + " groups, and the f70r1 nine-item outer array averages "
        + "/".join(f"{summaries['F70R1_OUTER_RADIAL'][ed]['mean']:.3f}" for ed in ("ZL3b", "IT2a", "RF1b"))
        + ".",
        "",
        "This is local, not a universal centre-to-edge grammar. The public f70v2 inner and outer zodiac-label bands do not give the same direction in every reading: "
        + ", ".join(f"{ed} {data['direction']}" for ed, data in comparator_directions.items())
        + ".",
        "",
        "The repeated visual slot is therefore informative about document role: on these two adjacent diagrams it hosts a compact label register. It is not a semantic key. The differing f69r glyph-level versus f70r1 word-level realization specifically blocks treating the two sixes as a one-to-one vocabulary without new evidence.",
        "",
        "Historical six-planet/apogee and nine-sphere counts remain only generic comparisons. The published apsides tradition requires six eccentric planetary circles and six zodiacal signs, a topology not stated in the public f70r1 description. No PLANET, APSIS, SPHERE, WIND, NUMBER, abbreviation, word meaning, plaintext, or translation is assigned.",
        "",
        "Public sources: [Voynich Quire 10](https://www.voynich.nu/q10/index.html), [Stolfi f69r](https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f69r.htm), [Stolfi f70r1](https://www.ic.unicamp.br/en/~stolfi/EXPORT/voynich/00-06-07-word-grammar/Notes/040/html/f70r1.htm), and [Eastwood on medieval planetary diagrams](https://api.pageplace.de/preview/DT0400.9781351744195_A31718041/preview-9781351744195_A31718041.pdf).",
    ]
    canonical_write(REPORT, "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
