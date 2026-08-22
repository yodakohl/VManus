#!/usr/bin/env python3
"""Validate V68 R2's bound 776-group adversarial edition."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
QUERY = ROOT / "vmanus-exp"
UNITS = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6", "A1", "A2", "A3"]
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise AssertionError(f"malformed TSV: {path.name}")
    return rows


def guarded(path: Path, allows: list[str], columns: list[str]) -> list[dict[str, str]]:
    cmd = [str(QUERY), "query-tsv", str(path), "--selector", "page"]
    for value in allows:
        cmd.extend(["--allow", value])
    cmd.extend(["--columns", ",".join(columns), "--forbid-prefix", "f84"])
    result = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    text = "\n".join(line for line in result.stdout.splitlines() if not line.startswith("GUARD_STATS "))
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def need(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)


def main() -> int:
    edition = tsv(HERE / "V68_R2_FOURTEEN_UNIT_RIVAL_EDITION.tsv")
    binding = tsv(HERE / "V68_R2_776_COVERAGE_BINDING.tsv")
    scores = tsv(HERE / "V68_R2_SYMMETRIC_SCORECARD.tsv")
    costs = tsv(HERE / "V68_R2_ASSUMPTION_COSTS.tsv")
    contradictions = tsv(HERE / "V68_R2_CONTRADICTION_LEDGER.tsv")
    sources = tsv(HERE / "V68_R2_HISTORICAL_SOURCES.tsv")
    report = (HERE / "V68_R2_HISTORICAL_ADVERSARIAL_REPORT.md").read_text(encoding="utf-8")

    for name, rows in (("edition", edition), ("binding", binding), ("scorecard", scores)):
        need([row["unit_id"] for row in rows] == UNITS, f"{name} must contain the ordered 14 units")
    need({row["page"] for row in edition} == PAGES, "edition page set mismatch")
    need(all("NO_PHONETIC_MAPPING" in row["semantic_contract"] for row in edition), "phonetic gate missing")
    need(all("NO_NEW_CARD_MEANING" in row["semantic_contract"] for row in binding), "binding semantic gate missing")

    expected = {
        "H1": (1, 14, 14), "H2": (15, 38, 24), "H3": (39, 55, 17), "H4": (56, 73, 18), "H5": (74, 100, 27),
        "B1": (101, 166, 66), "B2": (167, 228, 62), "B3": (229, 314, 86), "B4": (315, 361, 47), "B5": (362, 372, 11), "B6": (373, 381, 9),
        "A1": (1, 190, 190), "A2": (191, 255, 65), "A3": (256, 395, 140),
    }
    for row in binding:
        start, end, count = expected[row["unit_id"]]
        need((int(row["serial_start"]), int(row["serial_end"]), int(row["visible_group_count"])) == (start, end, count), f"binding mismatch {row['unit_id']}")
        need(end - start + 1 == count, f"non-contiguous interval {row['unit_id']}")
    need(sum(int(row["visible_group_count"]) for row in binding) == 776, "bound coverage must total 776")
    need(sum(int(row["visible_group_count"]) for row in binding if row["register"] != "ASTRO") == 381, "prose binding must total 381")
    need(sum(int(row["visible_group_count"]) for row in binding if row["register"] == "ASTRO") == 395, "Astro binding must total 395")

    herbal = guarded(ROOT / "experiments/yolo/sidequest_theory_candidates_v64/V64_R2_100_EVENT_HERBAL_INTERLINEAR.tsv", ["f10r", "f11r", "f55v", "f56r"], ["page", "record_unit_id", "event_serial"])
    bio = guarded(ROOT / "experiments/yolo/sidequest_theory_candidates_v65/V65_R2_281_EVENT_BIO_INTERLINEAR.tsv", ["f81v", "f82r", "f83r"], ["page", "record_unit_id", "event_serial"])
    astro = guarded(ROOT / "experiments/yolo/sidequest_theory_candidates_v66/V66_R2_395_GROUP_ASTRO_INTERLINEAR.tsv", ["f67r2", "f68r1", "f69v"], ["page", "group_serial", "locus"])
    need((len(herbal), len(bio), len(astro)) == (100, 281, 395), "canonical ledger totals mismatch")
    observed: dict[str, tuple[int, int, int]] = {}
    for unit in UNITS[:11]:
        rows = [row for row in herbal + bio if row["record_unit_id"] == unit]
        serials = [int(row["event_serial"]) for row in rows]
        observed[unit] = (min(serials), max(serials), len(serials))
    for unit, page in (("A1", "f67r2"), ("A2", "f68r1"), ("A3", "f69v")):
        rows = [row for row in astro if row["page"] == page]
        serials = [int(row["group_serial"]) for row in rows]
        observed[unit] = (min(serials), max(serials), len(serials))
    need(observed == expected, "bound intervals do not match guarded canonical ledgers")
    need(len({(row["page"], row["locus"]) for row in astro}) == 142, "Astro loci must total 142")

    criteria = ["visible_fit", "sequence_fit", "historical_fit", "layer_discipline", "book_coherence"]
    medical_total = rival_total = 0
    for row in scores:
        medical = sum(int(row[f"medical_{item}"]) for item in criteria)
        rival = sum(int(row[f"rival_{item}"]) for item in criteria)
        need(medical == int(row["medical_total"]) and rival == int(row["rival_total"]), f"score arithmetic {row['unit_id']}")
        need(all(0 <= int(row[f"{side}_{item}"]) <= 4 for side in ("medical", "rival") for item in criteria), f"score range {row['unit_id']}")
        expected_winner = "MEDICAL" if medical > rival else "RIVAL" if rival > medical else "TIE"
        need(row["winner"] == expected_winner, f"winner mismatch {row['unit_id']}")
        medical_total += medical
        rival_total += rival
    need((medical_total, rival_total) == (236, 249), "aggregate score mismatch")
    need(Counter(row["winner"] for row in scores) == Counter({"MEDICAL": 5, "RIVAL": 5, "TIE": 4}), "winner profile mismatch")

    total_cost = next(row for row in costs if row["register"] == "TOTAL_HEURISTIC")
    need((int(total_cost["medical_cost"]), int(total_cost["rival_cost"]), int(total_cost["rival_minus_medical"])) == (831, 760, -71), "cost total mismatch")
    need({row["unit_id"] for row in contradictions} >= set(UNITS), "every unit needs a published contradiction")
    need(len(contradictions) >= 18, "contradiction ledger too small")
    need(len(sources) >= 10 and all(row["reference_url"].startswith("https://") for row in sources), "historical source gate failed")
    normalized = " ".join(report.split())
    need("249 zu 236" in normalized and "776/776" in normalized, "report decision or coverage missing")
    lower_report = normalized.lower()
    need("keine entzifferung" in lower_report and "kein f68r1↔f69v-schlüssel" in lower_report, "report semantic disclaimer missing")

    result = {
        "status": "PASS",
        "decision": "PRACTICAL_RIVAL_BEATS_IATROMEDICAL_DEFAULT_NARROWLY",
        "units": len(edition),
        "coverage": {"Herbal_events": len(herbal), "Bio_events": len(bio), "Prose_events": len(herbal) + len(bio), "Astro_groups": len(astro), "Astro_loci": len({(row['page'], row['locus']) for row in astro}), "total_visible_groups": len(herbal) + len(bio) + len(astro)},
        "symmetric_score": {"medical": medical_total, "practical_rival": rival_total, "delta_rival": rival_total - medical_total, "unit_winners": dict(Counter(row["winner"] for row in scores))},
        "assumption_cost_sensitivity": {"medical": 831, "practical_rival": 760, "delta_rival": -71},
        "contradictions": len(contradictions),
        "historical_sources": len(sources),
        "semantic_gates": {"new_card_meanings": False, "phonetic_mapping": False, "prose_cards_imported_to_Astro": False, "f68_f69_mapping": False, "sealed_f84_used": False},
    }
    (HERE / "V68_R2_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
