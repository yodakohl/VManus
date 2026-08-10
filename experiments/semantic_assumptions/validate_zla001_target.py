#!/usr/bin/env python3
"""Production-free target reconstruction for ZLA001."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import validate_zla001_controls as clean


BASE = Path(__file__).resolve().parent
ROOT = BASE.parent.parent
R = BASE / "results"
FREEZE = ROOT / "ZLA001_TARGET_FREEZE.json"
R1_FREEZE = ROOT / "ZLA001_TARGET_VALIDATOR_R1_FREEZE.json"
AMENDMENT = ROOT / "ZLA001_TARGET_VALIDATOR_AMENDMENT.md"
PANEL = R / "zodiac_label_cycle_capacity.tsv"
STA = R / "source_sta_group_alignment.tsv"
TARGET = R / "zla001_target.json"
TARGET_REPORT = R / "zla001_target.md"
OUT = R / "zla001_target_validation.json"
OUT_MD = R / "zla001_target_validation.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sequences(rings: list[dict[str, object]]) -> tuple[dict, dict[str, object]]:
    loci = {locus for ring in rings for locus in ring["loci"]}
    grouped = {}
    with STA.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["edition"] in clean.READINGS and row["locus"] in loci:
                grouped.setdefault((row["edition"], row["locus"]), []).append(row)
    if len(grouped) != 705:
        raise AssertionError("join coverage")
    sequences = {reading: {view: [] for view in clean.VIEWS} for reading in clean.READINGS}
    payload = bytearray(); groups_total = 0
    for reading in clean.READINGS:
        for ring in rings:
            family_ring = []; boundary_ring = []
            for locus in ring["loci"]:
                rows = sorted(grouped[(reading, locus)], key=lambda row: int(row["source_group_index"]))
                count = int(rows[0]["source_group_count"])
                if len(rows) != count or [int(row["source_group_index"]) for row in rows] != list(range(1, count + 1)):
                    raise AssertionError("group order")
                pieces = [tuple(row["primary_sta_families"]) for row in rows]
                if any(not piece for piece in pieces):
                    raise AssertionError("empty family piece")
                family = tuple(token for piece in pieces for token in piece)
                boundary = tuple(token for index, piece in enumerate(pieces) for token in (("|",) if index else tuple()) + piece)
                family_ring.append(family); boundary_ring.append(boundary); groups_total += count
                payload.extend(f"{reading}\t{ring['id']}\t{locus}\t{''.join(family)}\t{''.join(boundary)}\n".encode())
            sequences[reading]["FAMILY_ONLY"].append(family_ring)
            sequences[reading]["BOUNDARY_AWARE"].append(boundary_ring)
    return sequences, {"reading_slots": 705, "physical_slots": 235, "source_groups": groups_total, "sequence_payload_sha256": hashlib.sha256(payload).hexdigest()}


def rotate(sequences: dict, rings: list[dict[str, object]]) -> dict:
    output = {reading: {view: [] for view in clean.VIEWS} for reading in clean.READINGS}
    for reading in clean.READINGS:
        for view in clean.VIEWS:
            for ring, values in zip(rings, sequences[reading][view]):
                shift = int.from_bytes(hashlib.sha256(f"ZLA001|TARGET_ROTATE|{ring['id']}".encode()).digest()[:2], "big") % len(values)
                output[reading][view].append(values[-shift:] + values[:-shift] if shift else list(values))
    return output


def reflect(sequences: dict) -> dict:
    return {reading: {view: [list(reversed(values)) for values in sequences[reading][view]] for view in clean.VIEWS} for reading in clean.READINGS}


def numeric(value: object, prefix: str = "") -> dict[str, float]:
    result = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if "sha256" in str(key): continue
            result.update(numeric(item, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, (int, float)) and not isinstance(value, bool): result[prefix] = float(value)
    return result


def invariant(left: dict, right: dict) -> dict[str, object]:
    a=numeric(left); b=numeric(right)
    if set(a)!=set(b): return {"pass":False,"max_abs":None,"same_logic":False}
    maximum=max(abs(a[k]-b[k]) for k in a) if a else 0.0
    logic=left["gates"]==right["gates"] and left["confirmed"]==right["confirmed"]
    return {"pass":maximum<=clean.TOL and logic,"max_abs":maximum,"same_logic":logic}


def report_text(result: dict) -> str:
    evaluation=result["evaluation"]; primary=evaluation["primary"]; noexact=evaluation["noexact"]; components=evaluation["components"]
    positive_folio_counts = {reading: evaluation["positive_folio_counts"][reading] for reading in clean.READINGS}
    return (
        "# ZLA001 zodiac label cyclic adjacency target\n\n"
        f"Status: **{result['status']}**. Decision: **{result['decision']}**.\n\n"
        f"The fixed weakest-reading composite effect is `{primary['minimum_effect']:.6f}` with joint `p={primary['p_plus_one']:.6f}`. "
        f"Component minimum effects are `FAMILY_ONLY={components['FAMILY_ONLY']['minimum_effect']:.6f}` and "
        f"`BOUNDARY_AWARE={components['BOUNDARY_AWARE']['minimum_effect']:.6f}`. After removing exact complete-record pairs, "
        f"the minimum effect is `{noexact['minimum_effect']:.6f}` with `p={noexact['p_plus_one']:.6f}`.\n\n"
        f"Positive-folio counts by alternate reading are `{positive_folio_counts}`. All 21 rings, all 235 physical slots, "
        "and the complete frozen 65,536-world distance orbit were scored once. No individual label sequence, family identity, favorable "
        "ring, object assignment, or English gloss is emitted.\n\n"
        "A confirmation would establish only a local length-adjusted construction signal among adjacent public zodiac labels. A "
        "nonconfirmation closes only this representation. Neither outcome can establish ownership, a serial code, number, degree, "
        "sign name, word, meaning, plaintext, or translation.\n"
    )


def main() -> None:
    if OUT.exists() or OUT_MD.exists(): raise SystemExit("refusing overwrite")
    frozen=json.loads(FREEZE.read_text()); replacement=json.loads(R1_FREEZE.read_text()); stored=json.loads(TARGET.read_text()); checks=0
    if replacement.get("status") != "FROZEN_REPORT_ORDER_VALIDATOR_REPLACEMENT": raise AssertionError("replacement freeze")
    if replacement.get("original_freeze_sha256") != sha(FREEZE): raise AssertionError("original freeze binding")
    if replacement.get("amendment_sha256") != sha(AMENDMENT): raise AssertionError("amendment binding")
    if replacement.get("replacement_validator_sha256") != sha(Path(__file__)): raise AssertionError("replacement validator binding")
    if replacement.get("immutable_target_sha256") != sha(TARGET) or replacement.get("immutable_report_sha256") != sha(TARGET_REPORT): raise AssertionError("immutable target binding")
    checks += 5
    if frozen["status"]!="FROZEN_TARGET_AND_VALIDATION_ABSENT": raise AssertionError("freeze")
    for relative,digest in frozen["files"].items():
        if relative == "experiments/semantic_assumptions/validate_zla001_target.py":
            if replacement.get("original_validator_sha256") != digest: raise AssertionError("original validator hash")
        elif sha(ROOT/relative)!=digest: raise AssertionError(f"hash {relative}")
        checks+=1
    rings,pages,folios=clean.geometry(); assignments,orbit=clean.orbit(rings)
    if orbit!=frozen["orbit"] or orbit!=stored["orbit"]: raise AssertionError("orbit")
    checks+=2
    sequences,source_join=load_sequences(rings)
    if source_join!=stored["source_join"]: raise AssertionError("source join")
    checks+=1
    evaluation=clean.evaluate(rings,pages,folios,assignments,sequences)
    checks+=clean.compare(evaluation,stored["evaluation"],"evaluation")
    invariances={"rotation":invariant(evaluation,clean.evaluate(rings,pages,folios,assignments,rotate(sequences,rings))),
                 "reflection":invariant(evaluation,clean.evaluate(rings,pages,folios,assignments,reflect(sequences)))}
    if invariances!=stored["invariances"]: raise AssertionError("invariances")
    checks+=2
    confirmed=all(evaluation["gates"].values()) and all(item["pass"] for item in invariances.values())
    expected_status="CONFIRMED_LOCAL_ZODIAC_LABEL_ADJACENCY_CONSTRUCTION" if confirmed else "FINAL_NONCONFIRMATION_ZODIAC_LABEL_ADJACENCY"
    expected_decision="RETAIN_LOCAL_ORDERED_LABEL_REGISTER" if confirmed else "CLOSE_FIXED_ZLA001_REPRESENTATION"
    if stored["status"]!=expected_status or stored["decision"]!=expected_decision: raise AssertionError("decision")
    checks+=2
    if not all(stored["execution_gates"].values()) == confirmed: raise AssertionError("execution gates")
    if stored["target_access"]!={"manual_STA_rows_accessed":True,"parser_roots_accessed":False,"object_attributes_accessed":False,"images_OCR_or_neural_vision_accessed":False,"English_glosses_emitted":0}: raise AssertionError("access flags")
    checks+=2
    if TARGET_REPORT.read_text()!=report_text(stored): raise AssertionError("report")
    checks+=1
    result={"experiment":"ZLA001_TARGET_VALIDATION","status":"PASS","checks":checks,"inputs":{p.name:sha(p) for p in (FREEZE,PANEL,STA,TARGET,TARGET_REPORT,Path(__file__),Path(clean.__file__))},
            "reconstructed":{"rings":21,"slots":235,"reading_slots":705,"source_groups":source_join["source_groups"],"orbit_sha256":orbit["sha256"],
                             "primary_minimum_effect":evaluation["primary"]["minimum_effect"],"primary_p":evaluation["primary"]["p_plus_one"],"decision":expected_decision},
            "target_access":{"parser_roots":False,"object_attributes":False,"images_OCR_neural_vision":False,"English_glosses":0},
            "claim_ceiling":"Validation of the fixed aggregate target only; no ownership, serial code, number, degree, sign name, word, meaning, plaintext, or translation."}
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    OUT_MD.write_text(f"# ZLA001 target validation\n\nStatus: **PASS** ({checks} checks). A production-free clean-room implementation rejoined all 705 reading-slot records, rebuilt the complete 65,536-world orbit, every aggregate score, exact-record sensitivity, folio support/deletion/concentration value, dihedral invariance, decision, and report. No parser roots, object attributes, images, OCR, neural vision, or English glosses were accessed.\n")
    print(json.dumps({"status":"PASS","checks":checks,"decision":expected_decision,"primary_minimum_effect":evaluation["primary"]["minimum_effect"],"primary_p":evaluation["primary"]["p_plus_one"]},sort_keys=True))


if __name__=="__main__": main()
