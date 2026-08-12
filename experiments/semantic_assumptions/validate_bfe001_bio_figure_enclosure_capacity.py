#!/usr/bin/env python3
"""Independent compact reconstruction of BFE001 capacity."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
CROSSWALK = RESULTS / "existing_human_current_locus_crosswalk.tsv"
PRODUCER = HERE / "audit_bfe001_bio_figure_enclosure_capacity.py"
RESULT = RESULTS / "bfe001_bio_figure_enclosure_capacity.json"
REPORT = RESULTS / "bfe001_bio_figure_enclosure_capacity_report.md"
OUT_JSON = RESULTS / "bfe001_bio_figure_enclosure_capacity_validation.json"
OUT_REPORT = RESULTS / "bfe001_bio_figure_enclosure_capacity_validation_report.md"

PAGE_STATE = {"f77r": "I", "f77v": "I", "f80r": "O", "f82r": "O", "f83r": "I", "f83v": "I", "f84r": "O"}
F82_I = {"f82v.2", "f82v.39", "f82v.40"}
F82_O = {"f82v.41", "f82v.46"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite BFE001 validation outputs")
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    with CROSSWALK.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    by_physical = {}
    for row in rows:
        by_physical.setdefault(row["source_physical_location_id"], row)
    selected = sorted([
        row for row in by_physical.values()
        if row["primary_eligible"] == "1" and row["source_section"] == "bio"
        and row["source_object_guess"] == "nymph?" and row["source_page"] not in {"f75r", "f75v"}
    ], key=lambda row: row["source_record_id"])
    states = []
    for row in selected:
        if row["source_page"] == "f82v":
            states.append("I" if row["current_locus"] in F82_I else "O" if row["current_locus"] in F82_O else "ERROR")
        else:
            states.append(PAGE_STATE[row["source_page"]])
    assert "ERROR" not in states
    folios = [re.match(r"f\d+", row["source_page"]).group(0) for row in selected]
    state_folios = {s: {f for s2, f in zip(states, folios) if s2 == s} for s in {"I", "O"}}
    mixed_folios = {f for f in set(folios) if {s for s, f2 in zip(states, folios) if f2 == f} == {"I", "O"}}
    mixed_pages = {p for p in {r["source_page"] for r in selected} if {s for s, r in zip(states, selected) if r["source_page"] == p} == {"I", "O"}}
    counts, folio_counts = Counter(states), Counter(folios)
    checks = {
        "producer_and_result_files": PRODUCER.is_file() and REPORT.is_file(),
        "physical_candidate_selection": len(selected) == 40,
        "page_partition": Counter(r["source_page"] for r in selected) == Counter({"f84r": 10, "f82r": 7, "f80r": 5, "f82v": 5, "f77r": 4, "f83v": 4, "f77v": 3, "f83r": 2}),
        "state_partition": counts == Counter({"O": 24, "I": 16}),
        "state_folio_support": state_folios == {"I": {"f77", "f82", "f83"}, "O": {"f80", "f82", "f84"}},
        "mixed_support": mixed_folios == {"f82"} and mixed_pages == {"f82v"},
        "stored_stop_and_access_seal": stored["status"] == "STOP_ONE_MIXED_FOLIO_PAGE_ECOLOGY_CONFOUND" and not stored["access"]["voynich_label_strings_accessed"] and not stored["access"]["formal_features_accessed"],
        "counts_and_floor": stored["state_counts"] == {"INDIVIDUAL_BOUNDED": 16, "OPEN_OR_COMMUNAL": 24} and stored["paired_mixed_folio_one_sided_p_floor"] == .5 and max(folio_counts.values()) / 40 == .3,
    }
    if not all(checks.values()):
        raise AssertionError([k for k, v in checks.items() if not v])
    validation = {
        "experiment": "BFE001_BIO_FIGURE_ENCLOSURE_CAPACITY_VALIDATION",
        "status": "PASS_8_CHECK_COMPACT_RECONSTRUCTION", "check_count": len(checks), "checks": list(checks),
        "validated_result_sha256": sha(RESULT), "producer_sha256": sha(PRODUCER),
        "reconstructed": {"locations": 40, "individual_bounded": 16, "open_or_communal": 24,
                          "folios": 5, "mixed_folios": ["f82"], "mixed_pages": ["f82v"], "p_floor": .5},
        "visual_judgment_reclassified_by_validator": False,
        "claim_ceiling": "Validation confirms only the filler-blind capacity stop and supplies no figure owner, word, meaning, plaintext, or translation.",
    }
    OUT_JSON.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    OUT_REPORT.write_text(
        "# BFE001 independent capacity validation\n\nAll eight compact checks pass. The independent reconstruction recovers 40 candidates, the 16/24 state partition, three folios per state, only f82/f82v as mixed support, the .5 paired-folio floor, and the sealed stop. The validator does not reclassify the machine-authored visual judgments and supplies no translation.\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
