#!/usr/bin/env python3
"""Independent retained-artifact validation for GDT196."""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def csha(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def main() -> None:
    result = json.loads((ROOT / "gdt196_result.json").read_text())
    checks: list[tuple[str, bool]] = []
    add = lambda name, value: checks.append((name, bool(value)))
    inter = read("gdt196_f77_structural_interlinear.tsv")
    echoes = read("gdt196_label_prose_echoes.tsv")
    counters = read("gdt196_counterexamples.tsv")

    add("status", result["status"] == "STRICT_STRUCTURAL_INTERLINEAR_PARTIAL_LABEL_KEY_NOT_BRIDGED")
    add("line_count", len(inter) == result["consensus_covered_lines"] == 31)
    add("group_count", sum(int(r["groups"]) for r in inter) == result["strict_groups"] == 193)
    add("unique_lines", len({r["locus"] for r in inter}) == 31)
    add("all_f77", all(r["locus"].startswith("f77r.") for r in inter))
    add("no_f84_output", not any(r["locus"].startswith("f84") for r in inter)
        and not any(r["label_locus"].startswith("f84") or "f84" in r["f77_exact_loci"] or "f84" in r["f77_host_loci"] for r in echoes))
    add("all_reading_basis", all(r["reading_basis"] == "STRICT_ZERO_ALTERNATIVE_ALL_THREE_READINGS" for r in inter))
    add("coverage_counts", sum(r["coverage"] == "COMPLETE" for r in inter) == result["complete_lines"] == 18 and sum(r["coverage"] != "COMPLETE" for r in inter) == result["partial_lines"] == 13)
    add("complete_group_counts", all((int(r["groups"]) == int(r["expected_groups"])) == (r["coverage"] == "COMPLETE") for r in inter))
    add("missing_counts", all(int(r["expected_groups"]) - int(r["groups"]) == int(r["missing_or_unstable_groups"]) for r in inter))
    add("field_count_matches", all(r["structural_translation"].count("FIELD[") == int(r["groups"]) for r in inter))
    add("surface_count_matches", all(len(r["surface_sequence"].split(" | ")) == int(r["groups"]) for r in inter))
    add("checkpoint_total", sum(int(r["dy_checkpoints"]) for r in inter) == result["dy_checkpoints"])
    add("closer_total", sum(int(r["b3_closers"]) for r in inter) == result["b3_closers"])
    add("six_labels", len(echoes) == result["diagram_labels"] == 6)
    add("label_order", [r["label_surface"] for r in echoes] == ["olkchs", "otedy", "otork", "otol", "dchdy", "soral"])
    add("state_order", [r["provisional_state"] for r in echoes] == ["COLD", "DRY", "HOT", "HOT", "MOIST", "COLD"])
    add("one_exact_label", sum(int(r["exact_surface_f77_prose"]) > 0 for r in echoes) == result["exact_labels_echoed_on_page"] == 1)
    add("one_exact_occurrence", sum(int(r["exact_surface_f77_prose"]) for r in echoes) == result["exact_label_group_occurrences_on_page"] == 1)
    add("echo_is_otedy", [r["label_surface"] for r in echoes if int(r["exact_surface_f77_prose"])] == ["otedy"])
    add("echo_locus", next(r for r in echoes if r["label_surface"] == "otedy")["f77_exact_loci"] == "f77r.25")
    add("counterexamples", len(counters) == 5)
    add("claim_ceiling", "no word" in result["claim_ceiling"].lower() and "confirmed translation" in result["claim_ceiling"].lower())
    add("f84_flags", all(v is False for v in result["f84r"].values()))
    for group in ("inputs", "implementation", "outputs", "documents"):
        for name, digest in result[group].items():
            add(f"hash:{group}:{name}", sha(name) == digest)
    raw = dict(result); digest = raw.pop("result_content_sha256")
    add("content_hash", csha(raw) == digest)

    validation = {
        "schema": "GDT196_VALIDATION_V1", "status": "PASS" if all(x[1] for x in checks) else "FAIL",
        "checks_passed": sum(x[1] for x in checks), "checks_total": len(checks),
        "failed": [name for name, ok in checks if not ok],
        "result_sha256": sha("gdt196_result.json"),
        "scope": "Independent retained-output, arithmetic, provenance, and hash validation; does not confirm the post-hoc f77 semantic scaffold.",
    }
    (ROOT / "gdt196_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps(validation, sort_keys=True))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
