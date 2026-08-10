#!/usr/bin/env python3
"""Nonimporting validator for F69F70C001."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
PROD = RESULTS / "f69r_f70r1_central_slot_component_audit.json"
PROD_MD = RESULTS / "f69r_f70r1_central_slot_component_audit.md"
OUT = RESULTS / "f69r_f70r1_central_slot_component_validation.json"
OUT_MD = RESULTS / "f69r_f70r1_central_slot_component_validation.md"
F69 = ["f69r.45", "f69r.46", "f69r.47", "f69r.48", "f69r.49", "f69r.44"]
F70 = ["f70r1.15", "f70r1.16", "f70r1.17", "f70r1.18", "f70r1.19", "f70r1.14"]
NATIVE = {
    "ZL3b": ROOT / "transcription" / "sources" / "ZL3b-n.txt",
    "IT2a": ROOT / "transcription" / "sources" / "IT2a-n.txt",
    "RF1b": ROOT / "transcription" / "sources" / "RF1b-e.txt",
}
STA = {key: ROOT / "transcription" / "sources" / "sta" / f"{key}.txt" for key in NATIVE}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def row(path: Path, key: str) -> str:
    found = re.findall(rf"^<{re.escape(key)},@(?:L0|Ri)>\s+(.*?)\s*$", path.read_text(), re.MULTILINE)
    if len(found) != 1:
        raise AssertionError((path, key, len(found)))
    return re.sub(r"^<![^>]+>", "", found[0])


def score(labels: tuple[str, ...], words: tuple[str, ...]) -> int:
    return sum(label in word for label, word in zip(labels, words))


def dmax(labels: tuple[str, ...], words: tuple[str, ...]) -> int:
    values = []
    for base in (labels, tuple(reversed(labels))):
        for shift in range(6):
            candidate = base[shift:] + base[:shift]
            values.append(score(candidate, words))
    return max(values)


def main() -> None:
    prod = json.loads(PROD.read_text())
    checks = 0

    def check(value: bool, label: str) -> None:
        nonlocal checks
        if not value:
            raise AssertionError(label)
        checks += 1

    check(prod["experiment"] == "F69F70C001_CENTRAL_SLOT_COMPONENT_AUDIT", "experiment")
    check(prod["status"] == "STOP_NO_FIXED_SLOT_COMPONENT_KEY", "status")
    check(prod["decision"] == prod["status"], "decision")
    check(prod["post_hoc_disclosure"] is True, "post hoc")

    for edition in NATIVE:
        check(prod["native_source_sha256"][edition] == sha(NATIVE[edition].read_bytes()), f"{edition} native hash")
        check(prod["sta_source_sha256"][edition] == sha(STA[edition].read_bytes()), f"{edition} STA hash")
        labels = tuple(row(NATIVE[edition], key) for key in F69)
        words = tuple(row(NATIVE[edition], key) for key in F70)
        check(prod["native_rows"][edition]["f69"] == list(labels), f"{edition} f69 rows")
        check(prod["native_rows"][edition]["f70"] == list(words), f"{edition} f70 rows")
        permutations = list(itertools.permutations(labels))
        physical = score(labels, words)
        maximum = dmax(labels, words)
        tail = sum(score(item, words) >= physical for item in permutations)
        max_tail = sum(dmax(item, words) >= maximum for item in permutations)
        stored = prod["complete_group_results"][edition]
        expected = (4, 5, 720, 118, 240) if edition == "RF1b" else (4, 5, 720, 200, 360)
        check((physical, maximum, len(permutations), tail, max_tail) == expected, f"{edition} counts")
        check(stored["physical_matches"] == physical, f"{edition} physical")
        check(stored["best_dihedral_matches"] == maximum, f"{edition} maximum")
        check(stored["physical_tail_count"] == tail, f"{edition} tail")
        check(stored["optimized_tail_count"] == max_tail, f"{edition} max tail")

    sta_labels = tuple(re.findall(r"[A-Z][0-9a-z]", row(STA["ZL3b"], key))[0][0] for key in F69)
    sta_words = tuple(
        {token[0] for token in re.findall(r"[A-Z][0-9a-z]", row(STA["ZL3b"], key))} for key in F70
    )
    unique = sorted(set(itertools.permutations(sta_labels)))

    def fscore(item: tuple[str, ...]) -> int:
        return sum(label in word for label, word in zip(item, sta_words))

    def fmax(item: tuple[str, ...]) -> int:
        values = []
        for base in (item, tuple(reversed(item))):
            for shift in range(6):
                candidate = base[shift:] + base[:shift]
                values.append(fscore(candidate))
        return max(values)

    physical = fscore(sta_labels)
    maximum = fmax(sta_labels)
    tail = sum(fscore(item) >= physical for item in unique)
    max_tail = sum(fmax(item) >= maximum for item in unique)
    check((physical, maximum, len(unique), tail, max_tail) == (4, 6, 180, 180, 144), "family orbit")
    stored = prod["leading_sta_family_result"]
    check(stored["physical_matches"] == 4, "family physical")
    check(stored["best_dihedral_matches"] == 6, "family maximum")
    check(stored["physical_tail_count"] == 180, "family tail")
    check(stored["optimized_tail_count"] == 144, "family max tail")

    pairing = prod["physical_pairing"]
    check([item["f69_locus"] for item in pairing] == F69, "f69 order")
    check([item["f70_locus"] for item in pairing] == F70, "f70 order")
    check(prod["gates"]["fixed_alignment_exceptional_all_readings"] is False, "fixed gate")
    check(prod["gates"]["optimized_alignment_exceptional"] is False, "optimized gate")
    check(prod["gates"]["ocr_or_automated_vision_used"] is False, "method exclusion")
    check("No shared key" in prod["claim_ceiling"], "ceiling")
    check("STOP_NO_FIXED_SLOT_COMPONENT_KEY" in PROD_MD.read_text(), "report decision")
    check("360/720" in PROD_MD.read_text(), "report ZL/IT orbit")
    check("240/720" in PROD_MD.read_text(), "report RF orbit")
    check("144/180" in PROD_MD.read_text(), "report family orbit")

    validation = {
        "status": "PASS_NONIMPORTING_EXACT_ASSIGNMENT_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "production_sha256": sha(PROD.read_bytes()),
        "production_report_sha256": sha(PROD_MD.read_bytes()),
        "decision": prod["decision"],
        "ocr_or_automated_vision_used": False,
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# F69F70C001 independent validation\n\n"
        f"PASS: **{checks}** checks independently reconstruct all three complete-group "
        "720-assignment orbits, the 180-assignment leading-family orbit, physical and "
        "optimized scores, gates, report claims, and final stop.\n\n"
        "This validates only the component-key nonconfirmation. It supplies no glyph "
        "sound, abbreviation, planet, direction, number, word, plaintext, or translation.\n"
    )


if __name__ == "__main__":
    main()
