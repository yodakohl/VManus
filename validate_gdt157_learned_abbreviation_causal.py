#!/usr/bin/env python3
"""Independent integrity/arithmetic validator for GDT157."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "gdt157_result.json"
OUT = ROOT / "gdt157_validation.json"
BOOKS = ("Band2", "Band3", "Band4", "Band5")
VIEWS = ("EXPANDED_PLAINTEXT", "GENERATED_DIPLOMATIC_MAP", "GENERATED_DIPLOMATIC_SAMPLED", "REAL_DIPLOMATIC")
FOLD_MAP = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s"})


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def norm(value: str, marker: bool = False) -> str:
    value = unicodedata.normalize("NFC", value).translate(FOLD_MAP).lower()
    return "".join(ch for ch in value if ch.isalnum() or (marker and ch == "¤"))


def groups(value: str, marker: bool = False) -> list[str]:
    return [token for part in value.split() if (token := norm(part, marker))]


def entropy(counter: Counter[str]) -> float:
    total = sum(counter.values())
    return -sum((n / total) * math.log2(n / total) for n in counter.values() if n)


def edit(left: str, right: str) -> int:
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        nxt = [i]
        for j, b in enumerate(right, 1): nxt.append(min(nxt[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = nxt
    return row[-1]


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8")); checks = []
    def check(name: str, state: bool) -> None: checks.append({"check": name, "pass": bool(state)})
    check("schema", result["schema"] == "GDT157_LEARNED_ABBREVIATION_CAUSAL_RESULT_V1")
    check("status", result["status"] == "LEARNED_ABBREVIATION_GENERATES_PARTIAL_ARCHITECTURE")
    stored = result.pop("result_content_sha256"); check("result_content_sha", csha(result) == stored); result["result_content_sha256"] = stored
    for name, digest in result["inputs"].items(): check("input_hash:" + name, sha(ROOT / name) == digest)
    for name, digest in result["outputs"].items(): check("output_hash:" + name, sha(ROOT / name) == digest)
    for name, digest in result["documents"].items(): check("document_hash:" + name, sha(ROOT / name) == digest)
    for name, digest in result["implementation"].items(): check("implementation_hash:" + name, sha(ROOT / name) == digest)

    blind = [row for row in read(ROOT / "gdt155_blinded_diplomatic.tsv") if row["corpus"] == "NUREMBERG"]
    expanded = {row["line_id"]: row for row in read(ROOT / "gdt155_unblinded_lines.tsv") if row["corpus"] == "NUREMBERG"}
    pairs = []; excluded = 0; empty_aligned = 0
    for row in blind:
        source = groups(expanded[row["line_id"]]["expanded_diplomatic"])
        target = [token.replace("¤", "") or "¤" for token in groups(row["diplomatic_marked"], True)]
        if len(source) != len(target): excluded += 1; continue
        if not source: empty_aligned += 1; continue
        for index, (left, right) in enumerate(zip(source, target), 1):
            pairs.append({"group_id": f"{row['line_id']}|G{index:03d}", "line_id": row["line_id"], "book": row["book_or_ms"], "expanded": left, "real": right})
    check("excluded_lines_45", excluded == 45)
    check("empty_aligned_lines_3", empty_aligned == result["counts"]["empty_aligned_nuremberg_lines"] == 3)
    check("aligned_groups_436572", len(pairs) == result["counts"]["aligned_groups"] == 436572)
    check("records_3176", result["counts"]["records"] == 3176)
    check("no_f84_external", not any("f84" in value.lower() for row in blind for value in row.values()))

    generated = {row["line_id"]: row for row in read(ROOT / "gdt157_generated_diplomatic.tsv")}
    check("generated_lines", len(generated) == len(blind) - excluded - empty_aligned)
    map_by_group = {}; sampled_by_group = {}
    for line_id, row in generated.items():
        left = row["generated_map"].split(); right = row["generated_sampled"].split()
        check("line_group_count:" + line_id, len(left) == len(right) == int(row["group_count"]))
        for index, value in enumerate(left, 1): map_by_group[f"{line_id}|G{index:03d}"] = value
        for index, value in enumerate(right, 1): sampled_by_group[f"{line_id}|G{index:03d}"] = value
    check("generated_map_group_keys", set(map_by_group) == {row["group_id"] for row in pairs})
    check("generated_sample_group_keys", set(sampled_by_group) == set(map_by_group))

    folds = {row["held_book"]: row for row in read(ROOT / "gdt157_channel_folds.tsv")}
    check("four_channel_folds", set(folds) == set(BOOKS))
    total_map_hits = total_groups = total_identity = 0
    for held in BOOKS:
        lex: dict[str, Counter[str]] = defaultdict(Counter)
        for row in pairs:
            if row["book"] != held: lex[row["expanded"]][row["real"]] += 1
        held_rows = [row for row in pairs if row["book"] == held]
        exact = 0; map_hits = 0; actual_abbr = 0; errors = real_chars = 0
        for row in held_rows:
            prediction = map_by_group[row["group_id"]]
            map_hits += prediction == row["real"]; actual_abbr += row["expanded"] != row["real"]
            errors += edit(prediction, row["real"]); real_chars += len(row["real"])
            if row["expanded"] in lex:
                exact += 1; modal = min(lex[row["expanded"]], key=lambda value: (-lex[row["expanded"]][value], value))
                check("exact_lexicon_modal:" + row["group_id"], prediction == modal)
        fold = folds[held]
        check("fold_groups:" + held, len(held_rows) == int(fold["held_groups"]))
        check("fold_exact_lex_count:" + held, exact == int(fold["exact_lexicon_groups"]))
        check("fold_map_hits:" + held, map_hits == int(fold["map_exact_groups"]))
        check("fold_actual_abbr:" + held, actual_abbr == int(fold["actual_abbreviated_groups"]))
        check("fold_cer:" + held, abs(errors / real_chars - float(fold["map_character_error_rate"])) < 1e-12)
        total_map_hits += map_hits; total_groups += len(held_rows); total_identity += len(held_rows) - actual_abbr
    check("map_accuracy", abs(total_map_hits / total_groups - result["channel"]["map_group_accuracy"]) < 1e-15)
    check("identity_accuracy", abs(total_identity / total_groups - result["channel"]["identity_baseline_accuracy"]) < 1e-15)
    check("channel_beats_identity", total_map_hits > total_identity)

    fps = read(ROOT / "gdt157_structural_fingerprints.tsv")
    check("four_fingerprints", {row["corpus_id"] for row in fps} == set(VIEWS))
    check("each_fingerprint_12k", all(int(row["tokens"]) == 12000 and int(row["folds"]) == 12 for row in fps))
    architecture = read(ROOT / "gdt157_architecture.tsv"); check("four_architecture_views", {row["view"] for row in architecture} == set(VIEWS))
    pair_by_line = defaultdict(list)
    for row in pairs: pair_by_line[row["line_id"]].append(row)
    for row in architecture:
        view = row["view"]; values = []
        for item in pairs:
            if view == "EXPANDED_PLAINTEXT": values.append(item["expanded"])
            elif view == "REAL_DIPLOMATIC": values.append(item["real"])
            elif view == "GENERATED_DIPLOMATIC_MAP": values.append(map_by_group[item["group_id"]])
            else: values.append(sampled_by_group[item["group_id"]])
        check("arch_groups:" + view, int(row["groups"]) == len(values))
        check("arch_types:" + view, int(row["types"]) == len(set(values)))
        check("arch_mean_length:" + view, abs(float(row["mean_group_length"]) - sum(map(len, values)) / len(values)) < 1e-12)
        check("arch_group_entropy:" + view, abs(float(row["group_entropy"]) - entropy(Counter(values))) < 1e-12)

    retrieval = read(ROOT / "gdt157_content_retrieval.tsv")
    check("retrieval_rows_60", len(retrieval) == 60)
    check("retrieval_all_queries", all(int(row["queries"]) == 3172 for row in retrieval if row["book"] == "ALL"))
    attr = read(ROOT / "gdt157_causal_attribution.tsv"); check("attribution_25", len(attr) == 25)
    counts = Counter()
    for row in attr:
        exp, real, gm, gs = map(float, (row["expanded"], row["real_diplomatic"], row["generated_map"], row["generated_sampled"]))
        gap = real - exp; rm = (gm - exp) / gap if abs(gap) > 1e-12 else 0; rs = (gs - exp) / gap if abs(gap) > 1e-12 else 0
        label = "ABBREVIATION_SUFFICIENT" if rm >= .5 and rs >= .5 else "PARTIAL_ABBREVIATION_EFFECT" if rm > 0 and rs > 0 else "NOT_GENERATED_BY_ABBREVIATION"
        check("attr_formula:" + row["feature"], abs(rm - float(row["map_gap_fraction_closed"])) < 1e-12 and abs(rs - float(row["sampled_gap_fraction_closed"])) < 1e-12 and label == row["attribution"])
        counts[label] += 1
    check("attribution_counts", counts["ABBREVIATION_SUFFICIENT"] == 7 and counts["PARTIAL_ABBREVIATION_EFFECT"] == 5 and counts["NOT_GENERATED_BY_ABBREVIATION"] == 13)
    check("f84_flags", result["f84r"]["voynich_source_inputs"] == 0 and all(result["f84r"][key] is False for key in ("opened", "queried", "retained", "joined", "scored")))

    validation = {"schema": "GDT157_LEARNED_ABBREVIATION_CAUSAL_VALIDATION_V1", "status": "PASS" if all(row["pass"] for row in checks) else "FAIL", "checks_passed": sum(row["pass"] for row in checks), "checks_total": len(checks), "result_sha256": sha(RESULT), "validator_sha256": sha(Path(__file__)), "validation_scope": "Independent source alignment, exact-lexicon MAP reconstruction, held-fold arithmetic, generated-stream joins, entropy/counts, attribution, hashes and seal; productive character-backoff emissions and full retrieval ranks are retained-output integrity rather than independently refit."}
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if validation["status"] != "PASS": raise SystemExit(json.dumps([row for row in checks if not row["pass"]][:20], indent=2))
    print(f"PASS {validation['checks_passed']}/{validation['checks_total']}")


if __name__ == "__main__": main()
