#!/usr/bin/env python3
import csv
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = ROOT / "experiments/yolo/gdt414_next_page_semantic_failure_deck"
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"


def read_tsv(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob("gdt414_*")) if p.name != "gdt414_validation.json"}


def main():
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    first = hashes()
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    second = hashes()
    deck = read_tsv("gdt414_19_core_semantic_failure_deck.tsv")
    mentions = read_tsv("gdt414_8505_root_mention_pressure_ledger.tsv")
    matrix = read_tsv("gdt414_95_root_register_guardrails.tsv")
    weakest = read_tsv("gdt414_19_weakest_existing_contexts.tsv")
    decisions = read_tsv("gdt414_eight_next_page_decisions.tsv")
    result = json.loads((OUT / "gdt414_result.json").read_text(encoding="utf-8"))
    checks = {
        "deck_19_unique": len(deck) == 19 and len({row["root"] for row in deck}) == 19,
        "mentions_8505": len(mentions) == 8505,
        "matrix_95": len(matrix) == 95 and Counter(row["root"] for row in matrix) == {row["root"]: 5 for row in deck},
        "weakest_19_unique": len(weakest) == 19 and len({row["root"] for row in weakest}) == 19,
        "decisions_8": len(decisions) == 8 and len({row["code"] for row in decisions}) == 8,
        "all_roots_all_registers": result["all_roots_all_registers"] is True,
        "mention_counts_match_deck": all(sum(row["root"] == root["root"] for row in mentions) == int(root["mention_count"]) for root in deck),
        "event_ids_known": all(row["global_running_event_id"].startswith("G407-E") for row in mentions),
        "support_classes_known": {row["leave_one_page_support_class"] for row in mentions} <= {"EXACT_SURFACE_FROM_OTHER_PAGE", "EXACT_RECIPE_FROM_OTHER_PAGE", "ALL_ADJACENT_PACKAGES_FROM_OTHER_PAGES", "KNOWN_ATOMS_NEW_PACKAGE_COMPOSITION", "KNOWN_ATOM_NO_INTERNAL_PAIR", "KNOWN_CORE_PLUS_PAGE_PRIVATE_LOCAL_SIGN"},
        "no_empty_policy": all(row["allowed_owner_local_expansions_de"] and row["green_next_page_condition_de"] and row["amber_next_page_condition_de"] and row["red_next_page_condition_de"] for row in deck),
        "all_defaults_keep": all(row["working_value_de"] for row in deck),
        "handbook_exists": (OUT / "NEXT_FOUR_PAGE_SEMANTIC_ERROR_DECK.md").is_file(),
        "status_exact": result["status"] == "NEXT_PAGE_SEMANTIC_FAILURE_DECK_READY",
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (deck, mentions, matrix, weakest, decisions) for row in table),
        "deterministic_rebuild": first == second,
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not value for value in checks.values()), "checks": checks}
    (OUT / "gdt414_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
