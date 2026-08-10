#!/usr/bin/env python3
"""Clean-room validation of the zodiac cross-sign phase capacity stop."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
R = BASE / "results"
SRC = BASE / "cache/existing_human_annotations/labtit-best.idx"
PROD = R / "zodiac_crosssign_phase_capacity.json"
REPORT = R / "zodiac_crosssign_phase_capacity.md"
OUT = R / "zodiac_crosssign_phase_capacity_validation.json"
OUT_MD = R / "zodiac_crosssign_phase_capacity_validation.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, label: str, passed: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    passed.append(label)


def main() -> None:
    if OUT.exists() or OUT_MD.exists():
        raise SystemExit("refusing overwrite")
    passed: list[str] = []
    slots = []
    for line in SRC.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split("|")
        check(len(f) == 11, "source_row_has_11_fields", passed)
        if f[1] != "zodiac":
            continue
        prose = f[10].lower()
        raw_sign = prose.split(",", 1)[0].split()[0]
        sign = "SCORPIUS" if raw_sign == "scorpio" else raw_sign.upper()
        candidates = [
            name for name, token in (
                ("C", "central star"), ("I", "inner"), ("M", "middle"),
                ("O", "outer"), ("N", "not in circle"),
            ) if token in prose
        ]
        check(len(candidates) == 1, "unique_layer_per_slot", passed)
        slots.append((f[0], f[2], re.match(r"f\d+", f[2]).group(0), sign, candidates[0], f[6] != "-"))
    check(len(slots) == 300, "exact_300_slots", passed)
    check(len({row[0] for row in slots}) == 300, "unique_slot_ids", passed)
    check(sum(row[5] for row in slots) == 299, "exact_299_labels", passed)

    by_panel = defaultdict(Counter)
    folios = defaultdict(set)
    labels = Counter()
    for _, page, folio, sign, layer, present in slots:
        by_panel[(sign, page)][layer] += 1
        folios[sign].add(folio)
        labels[sign] += present
    sign_names = (
        "PISCES", "ARIES", "TAURUS", "GEMINI", "CANCER",
        "LEO", "VIRGO", "LIBRA", "SCORPIUS", "SAGITTARIUS",
    )
    check(set(folios) == set(sign_names), "exact_sign_set", passed)
    signatures = {}
    expected_sign_rows = []
    for sign in sign_names:
        panels = []
        for (s, page), counts in by_panel.items():
            if s != sign:
                continue
            sig = "+".join(f"{layer}{counts[layer]}" for layer in "CIMON" if counts[layer])
            panels.append({
                "page": page,
                "shape": sig,
                "counts": {
                    "CENTRAL": counts["C"], "INNER": counts["I"],
                    "MIDDLE": counts["M"], "OUTER": counts["O"],
                    "OFF_CIRCLE": counts["N"],
                },
            })
        panels.sort(key=lambda row: row["page"])
        topology = " / ".join(sorted(row["shape"] for row in panels))
        signatures[sign] = topology
        expected_sign_rows.append({
            "sign": sign,
            "slot_count": sum(sum(row["counts"].values()) for row in panels),
            "label_count": labels[sign],
            "physical_folios": sorted(folios[sign]),
            "panel_topology": panels,
            "topology_signature_ignoring_page_identity": topology,
        })
    expected_signatures = {
        "PISCES": "C1+I10+O19",
        "ARIES": "I5+O10 / I5+O10",
        "TAURUS": "I5+O10 / I5+O10",
        "GEMINI": "I9+O16+N5",
        "CANCER": "I7+M11+O12",
        "LEO": "I12+O18",
        "VIRGO": "I12+O18",
        "LIBRA": "I10+O20",
        "SCORPIUS": "I10+O16+N4",
        "SAGITTARIUS": "I10+O16+N4",
    }
    check(signatures == expected_signatures, "exact_seven_topology_assignment", passed)
    groups = defaultdict(list)
    for sign in sign_names:
        groups[signatures[sign]].append(sign)
    repeated = []
    for signature, signs in groups.items():
        if len(signs) < 2:
            continue
        for left, right in itertools.combinations(signs, 2):
            overlap = sorted(folios[left] & folios[right])
            repeated.append({
                "topology": signature,
                "left": left,
                "right": right,
                "shared_physical_folios": overlap,
                "disjoint_physical_folios": not overlap,
            })
    check(len(groups) == 7, "exact_7_topologies", passed)
    check(len(repeated) == 3, "exact_3_repeated_topology_pairs", passed)
    check(all(row["shared_physical_folios"] for row in repeated), "all_repeated_pairs_share_folio", passed)

    prod = json.loads(PROD.read_text(encoding="utf-8"))
    check(prod["status"] == "STOP_UNSCORED_NO_IDENTIFIABLE_SHARED_30_POSITION_COORDINATE", "status_exact", passed)
    check(prod["decision"] == "DO_NOT_FIT_CROSSSIGN_DEGREE_PHASE_WITHOUT_EXTERNAL_BAND_AND_START_KEY", "decision_exact", passed)
    check(prod["signs"] == expected_sign_rows, "all_sign_rows_exact", passed)
    check(prod["topology_groups"] == dict(sorted(groups.items())), "topology_groups_exact", passed)
    check(prod["repeated_topology_pairs"] == repeated, "repeated_pair_rows_exact", passed)
    check(prod["counts"] == {
        "expected_slots": 300, "present_labels": 299, "signs": 10,
        "physical_folios": 4, "distinct_panel_topologies": 7,
        "repeated_topology_pairs": 3, "disjoint_folio_repeated_topology_pairs": 0,
    }, "summary_counts_exact", passed)
    check(prod["input"]["cache/existing_human_annotations/labtit-best.idx"] == sha(SRC), "source_hash_bound", passed)
    check(all(prod["gates"].values()), "all_gates_true", passed)
    text = REPORT.read_text(encoding="utf-8")
    check(prod["decision"] in text, "report_decision_bound", passed)
    check("seven distinct topologies" in text, "report_topology_claim_bound", passed)

    result = {
        "experiment": "ZODIAC_CROSSSIGN_PHASE_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_300_SLOT_RECONSTRUCTION",
        "checks": len(passed),
        "failures": [],
        "reconstructed": prod["counts"],
        "bindings": {
            "source_sha256": sha(SRC),
            "producer_result_sha256": sha(PROD),
            "producer_report_sha256": sha(REPORT),
            "validator_sha256": sha(Path(__file__)),
        },
        "decision": "VALIDATED_UNSCORED_CAPACITY_STOP",
        "claim_ceiling": prod["claim_ceiling"],
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Zodiac cross-sign phase capacity validation\n\n"
        "Status: **PASS_INDEPENDENT_300_SLOT_RECONSTRUCTION**\n\n"
        f"A nonimporting validator passed {len(passed):,} checks and independently reconstructed all "
        "300 public slot rows, 299 labels, ten signs, seven panel topologies, three repeated-topology "
        "pairs, their physical-folio overlaps, hashes, gates, decision, and report claims. No Voynich "
        "string, phase, direction, or band continuation was scored.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "checks": len(passed)}, sort_keys=True))


if __name__ == "__main__":
    main()
