#!/usr/bin/env python3
"""Independent reconstruction validator for KART001 retained artifacts."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
R = ROOT / "experiments/semantic_assumptions/results"
RESULT = ROOT / "kart001_result.json"
VALIDATION = ROOT / "kart001_validation.json"
ARRAYS = R / "special_circle_text_blind_array_inventory.tsv"
ANNOTATIONS = R / "existing_human_exact_locus_annotations.tsv"
SURFACE = R / "source_separator_transcription.tsv"
ALIGNMENT = R / "source_sta_group_alignment.tsv"
STA = R / "source_sta_family_consensus_loci.tsv"
INVENTORY = ROOT / "kart001_voynich_structural_inventory.tsv"
TESTS = ROOT / "kart001_tests.tsv"
NULLS = ROOT / "kart001_null_results.tsv"
COUNTERS = ROOT / "kart001_counterexamples.tsv"
REPORT = ROOT / "KART001_A65_SYSTEM_COMPARATOR_REPORT.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
UNIVERSE = (3, 4, 7, 8, 10, 12, 16, 19, 27, 28, 29, 30, 36)
A65 = (7, 12, 28, 30)
WORLDS = 8192
SEED = 65001


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_selected_tsv(path: Path, key: str, allowed: set[str]) -> list[dict[str, str]]:
    rows = []
    with path.open(encoding="utf-8", newline="") as handle:
        fields = handle.readline().rstrip("\r\n").split("\t")
        key_index = fields.index(key)
        for raw in handle:
            values = raw.rstrip("\r\n").split("\t")
            if values[key_index] not in allowed:
                continue
            rows.append(dict(zip(fields, values, strict=True)))
    return rows


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def grams(value: str, width: int) -> set[str]:
    return {value[i : i + width] for i in range(max(0, len(value) - width + 1))}


def similarity(a: str, b: str, mode: str) -> float:
    if mode == "SURFACE_EXACT":
        return float(a == b)
    if mode == "SURFACE_BIGRAM_JACCARD":
        aa, bb = grams(a, 2), grams(b, 2)
    elif mode == "SURFACE_TRIGRAM_JACCARD":
        aa, bb = grams(a, 3), grams(b, 3)
    elif mode == "STA_FAMILY_JACCARD":
        aa, bb = set(a), set(b)
    else:
        raise ValueError(mode)
    return len(aa & bb) / len(aa | bb) if aa | bb else 1.0


def score(sequence: list[str], lag: int, mode: str) -> float:
    return sum(similarity(sequence[i], sequence[(i + lag) % 28], mode) for i in range(28)) / 28


def panel_data() -> tuple[list[dict[str, object]], dict[str, list[str]], list[str]]:
    panel = []
    for row in read_selected_tsv(ANNOTATIONS, "page", {"f69v"}):
        if row["unit"] == "X1":
            number = re.fullmatch(r"f69v\.X1\.(\d+)", row["old_locus"])
            state = re.search(r"\b(long|short)\b", row["local_comment"].lower())
            if not number or not state:
                raise AssertionError("bad panel source")
            panel.append({"ordinal": int(number.group(1)), "locus": row["locus"], "state": state.group(1).upper()})
    panel.sort(key=lambda row: int(row["ordinal"]))
    loci = [str(row["locus"]) for row in panel]
    locus_set = set(loci)
    selected: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_selected_tsv(SURFACE, "locus", locus_set):
        if row["edition"] in EDITIONS:
            selected[(row["locus"], row["edition"])].append(row)
    ids = {row["source_group_id"] for values in selected.values() for row in values}
    align = {
        row["source_group_id"]: row["nearest_basic_eva_primary"]
        for row in read_selected_tsv(ALIGNMENT, "locus", locus_set)
        if row["source_group_id"] in ids
    }
    editions: dict[str, list[str]] = {}
    for edition in EDITIONS:
        editions[edition] = [
            "".join(align[row["source_group_id"]] for row in sorted(selected[(locus, edition)], key=lambda x: int(x["source_group_index"])))
            for locus in loci
        ]
    sta = {row["locus"]: row["family_sequence"] for row in read_selected_tsv(STA, "locus", locus_set)}
    return panel, editions, [sta[locus] for locus in loci]


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "pass": bool(condition), "detail": detail})
        if not condition:
            raise AssertionError(f"{name}: {detail}")

    result = json.loads(RESULT.read_text(encoding="utf-8"))
    check("schema", result["schema"] == "KART001_A65_SYSTEM_COMPARATOR_RESULT_V1")
    check("source_freeze_commit", result["source_freeze_commit"] == "73989f1da45a1a1f544057e971b93e5e23b1f3f0")
    check("primary_decision", result["primary_decision"] == "A65_SYSTEM_MATCH_NOT_ABOVE_GENERIC_MEDIEVAL")
    check("direct_transfer_falsified", "A65_DIRECT_TABLE_TRANSFER_FALSIFIED" in result["decisions"])
    check("cultural_specificity_low", result["cultural_specificity"] == "LOW")
    check(
        "f84_sealed",
        result["sealed_holdout"] == {
            "folio": "f84r",
            "formal_payload_retained_joined_or_scored": False,
            "guarded_stream_skipped_before_formal_field_retention": True,
        },
    )

    content = dict(result)
    claimed_content_hash = content.pop("result_content_sha256")
    raw = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    check("result_content_hash", hashlib.sha256(raw).hexdigest() == claimed_content_hash)
    check("all_input_hashes", all(sha256(ROOT / name) == digest for name, digest in result["inputs"].items()))
    check("all_output_hashes", all(sha256(ROOT / name) == digest for name, digest in result["outputs"].items()))
    check("producer_hash", result["implementation"] == {"run_kart001_a65_system_comparator.py": sha256(ROOT / "run_kart001_a65_system_comparator.py")})

    manifest = {row["feature_id"]: row for row in read_tsv(ROOT / "kart001_a65_comparator_manifest.tsv")}
    check("a65_feature_ids", set(manifest) == {f"A65_F{i:02d}" for i in range(1, 11)})
    check("a65_f01_f06_supported", all(manifest[f"A65_F{i:02d}"]["support_status"] == "SUPPORTED" for i in range(1, 7)))
    check("a65_f07_restricted", manifest["A65_F07"]["support_status"] == "SUPPORTED_WITH_DECLARED_GAPS")
    check("a65_f08_profile_only", manifest["A65_F08"]["support_status"] == "SUPPORTED_PROFILE_ONLY")
    check("a65_f09_f10_unsupported", all(manifest[key]["support_status"] == "UNSUPPORTED" for key in ("A65_F09", "A65_F10")))
    check("a65_red_black_specificity_unknown", manifest["A65_F06"]["generic_prevalence"] == "UNKNOWN")

    arrays = read_tsv(ARRAYS)
    array_map = {row["array_id"]: int(row["slot_count"]) for row in arrays}
    check("special_inventory_counts", len(arrays) == 504 and len(array_map) == 45)
    check("no_f84_array_input", not any(row["page"] == "f84r" for row in arrays))
    freq = Counter(array_map.values())
    observed = (len(set(A65) & set(freq)), sum(freq[x] for x in A65))
    all_scores = []
    for values in itertools.combinations(UNIVERSE, 4):
        all_scores.append((len(set(values) & set(freq)), sum(freq[x] for x in values)))
    tail = sum(value >= observed for value in all_scores)
    check("t1_observed", observed == (3, 10), repr(observed))
    check("t1_exact_null", len(all_scores) == 715 and tail == 302)
    check("t1_local_p", abs(result["t1"]["local_p"] - 302 / 715) < 1e-15)
    check("t1_adjusted_p", abs(result["t1"]["search_adjusted_p"] - 604 / 715) < 1e-15)

    panel, editions, sta_sequence = panel_data()
    check("f69_panel_ordinals", [row["ordinal"] for row in panel] == list(range(1, 29)))
    check("f69_exact_alternation", [row["state"] for row in panel] == ["LONG" if i % 2 else "SHORT" for i in range(1, 29)])
    retained = {(row["edition"], row["representation"]): row for row in result["t3"]["representations"]}
    series = [(edition, mode, editions[edition]) for edition in EDITIONS for mode in (
        "SURFACE_EXACT", "SURFACE_BIGRAM_JACCARD", "SURFACE_TRIGRAM_JACCARD"
    )] + [("CONSENSUS", "STA_FAMILY_JACCARD", sta_sequence)]
    minimum_p = 1.0
    for edition, mode, sequence in series:
        values = [score(sequence, lag, mode) for lag in range(1, 15)]
        row = retained[(edition, mode)]
        check(f"t3_score_{edition}_{mode}", abs(row["lag14_score"] - values[13]) < 1e-14)
        check(f"t3_rank_{edition}_{mode}", row["lag14_rank_of_14_descending"] == 1 + sum(v > values[13] + 1e-15 for v in values))
        rng = random.Random(f"{SEED}|{edition}|{mode}")
        exceed = 0
        for _ in range(WORLDS):
            shuffled = sequence.copy()
            rng.shuffle(shuffled)
            exceed += int(score(shuffled, 14, mode) >= values[13] - 1e-15)
        p = (exceed + 1) / (WORLDS + 1)
        minimum_p = min(minimum_p, p)
        check(f"t3_permutation_{edition}_{mode}", exceed == row["permutation_exceedances"] and abs(p - row["permutation_p"]) < 1e-15)
    check("t3_minimum_p", abs(minimum_p - result["t3"]["minimum_local_permutation_p"]) < 1e-15)
    check("t3_adjusted_p", result["t3"]["search_adjusted_p"] == 1.0)

    inventory = read_tsv(INVENTORY)
    tests = read_tsv(TESTS)
    nulls = read_tsv(NULLS)
    counters = read_tsv(COUNTERS)
    check("inventory_rows", len(inventory) == 52)
    check("structured_f84_exclusion", not any(row["page_or_scope"].startswith("f84") for row in inventory))
    check("seven_tests", len(tests) == 7 and {row["test_id"] for row in tests} == {f"KART001-T{i}" for i in range(1, 8)})
    statuses = {row["test_id"]: row["status"] for row in tests}
    check("t4_unscored", statuses["KART001-T4"] == "UNSCORED_NO_IDENTIFIABLE_30_POSITION_PHASE")
    check("t5_unscored", statuses["KART001-T5"] == "UNSCORED_NO_COMPLETE_ELIGIBLE_VISUAL_STATE")
    check("t7_unscored", statuses["KART001-T7"] == "UNSCORED_NO_SPECIFIC_A65_FOURFOLD_PREDICTION")
    check("null_row_count", len(nulls) == 865)
    check("counterexample_count", len(counters) == 14)
    check("required_counterexamples", {"F69V_LAG14", "GENERIC_COMPUTUS", "NINETEEN_TIMES_TWENTYEIGHT"} <= {row["target_claim"] for row in counters})
    ledger_rows = read_tsv(ROOT / "GDT002_YOLO_LEDGER.tsv")
    kart_rows = [row for row in ledger_rows if row["checkpoint_id"] == "KART001_CKPT002"]
    check(
        "branch_ledger_registration",
        len(kart_rows) == 1
        and kart_rows[0]["status"] == "A65_SYSTEM_MATCH_NOT_ABOVE_GENERIC_MEDIEVAL;A65_DIRECT_TABLE_TRANSFER_FALSIFIED"
        and kart_rows[0]["holdout_page"] == "f84r",
    )

    seven = defaultdict(list)
    for row in arrays:
        if int(row["slot_count"]) == 7:
            seven[row["array_id"]].append(row)
    check("three_nominal_seven_arrays", len(seven) == 3)
    check("seven_source_inconsistency_disclosed", any("8 labels" in rows[0]["unit_description"] for rows in seven.values()))
    check("t6_inconsistency_flag", any(not row["description_count_consistent"] for row in result["t6"]["arrays"]))
    check("report_terminal_decision", REPORT.read_text(encoding="utf-8").rstrip().endswith("**A65_SYSTEM_MATCH_NOT_ABOVE_GENERIC_MEDIEVAL**"))
    check("claim_ceiling", all(term in result["claim_ceiling"] for term in ("No Georgian", "plaintext", "translation")))

    validation = {
        "schema": "KART001_A65_SYSTEM_COMPARATOR_VALIDATION_V1",
        "experiment": "KART001_A65_SYSTEM_COMPARATOR",
        "status": "PASS_INDEPENDENT_RECONSTRUCTION",
        "checks_passed": len(checks),
        "checks_failed": 0,
        "checks": checks,
        "result_sha256": sha256(RESULT),
        "validator_sha256": sha256(Path(__file__)),
        "scope": "Independent source-table reconstruction of retained cardinality, f69v lag, permutation, hash, holdout, capacity-stop, and claim-ceiling facts; no translation.",
    }
    VALIDATION.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
