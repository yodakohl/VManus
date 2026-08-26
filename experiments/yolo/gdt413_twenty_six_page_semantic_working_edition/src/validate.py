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
HERE = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition"
OUT = HERE / "artifacts"
RUN = HERE / "src/run.py"


def read_tsv(name):
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def hashes():
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("gdt413_*")) if path.name != "gdt413_validation.json"}


def main():
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    first = hashes()
    subprocess.run(["python3", str(RUN)], cwd=ROOT, check=True)
    second = hashes()
    dictionary = read_tsv("gdt413_46_component_working_dictionary.tsv")
    groups = read_tsv("gdt413_5269_group_semantic_edition.tsv")
    events = read_tsv("gdt413_4576_event_semantic_edition.tsv")
    statements = read_tsv("gdt413_715_statement_semantic_edition.tsv")
    pages = read_tsv("gdt413_26_page_semantic_summary.tsv")
    result = json.loads((OUT / "gdt413_result.json").read_text(encoding="utf-8"))
    checks = {
        "dictionary_46_unique": len(dictionary) == 46 and len({row["atom"] for row in dictionary}) == 46,
        "portable_19": sum(row["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE" for row in dictionary) == 19,
        "all_portable_keep": all(row["decision"] == "KEEP" for row in dictionary if row["semantic_layer"] == "PORTABLE_BROAD_WORKING_CORE"),
        "groups_5269": len(groups) == 5269 and [int(row["global_group_ordinal"]) for row in groups] == list(range(1, 5270)),
        "group_kind_4576_693": Counter(row["group_kind"] for row in groups) == {"RUNNING_EVENT": 4576, "LOCAL_ADDRESS_OR_LABEL": 693},
        "events_4576": len(events) == 4576 and [int(row["global_running_ordinal"]) for row in events] == list(range(1, 4577)),
        "statements_715": len(statements) == 715 and [int(row["global_statement_ordinal"]) for row in statements] == list(range(1, 716)),
        "pages_26": len(pages) == 26,
        "all_running_readings": all(row["working_core_reading_de"] for row in events),
        "all_statement_readings": all(row["working_core_reading_de"] and row["owner_bound_workshop_paraphrase_de"] for row in statements),
        "local_copy_not_word": all(row["working_reading_de"] == "LOKALE ADRESSE ODER KENNUNG KOPIEREN" for row in groups if row["group_kind"] != "RUNNING_EVENT"),
        "chd_bearbeiten_301": result["chd_mention_count"] == 301 and sum("BEARBEITEN" in row["working_core_reading_de"].split(" · ") for row in events) >= 301,
        "air_bahn_43": result["air_mention_count"] == 43 and sum("BAHN" in row["working_core_reading_de"] for row in events) >= 43,
        "no_old_chd_air_defaults": not any(row["atom"] == "CHD" and row["working_value_de"] != "BEARBEITEN" or row["atom"] == "AIR" and row["working_value_de"] != "BAHN" for row in dictionary),
        "source_bounds_preserved": all(int(row["first_global_group_ordinal"]) <= int(row["last_global_group_ordinal"]) for row in statements),
        "no_forbidden_page": not any("f84" in "\t".join(row.values()).lower() for table in (dictionary, groups, events, statements, pages) for row in table),
        "readable_exists": (OUT / "TWENTY_SIX_PAGE_WORKING_READING.md").is_file(),
        "status_exact": result["status"] == "COMPLETE_TWENTY_SIX_PAGE_SEMANTIC_WORKING_EDITION",
        "deterministic_rebuild": first == second,
    }
    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "check_count": len(checks), "failure_count": sum(not value for value in checks.values()), "checks": checks}
    (OUT / "gdt413_validation.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(checks.values()):
        raise SystemExit(json.dumps(validation, indent=2))
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
