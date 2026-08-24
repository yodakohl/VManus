#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    rows = read("FIVE_HUNDRED_EIGHTIETH_ONE_HUNDRED_SIXTEEN_COMPACT_INSTRUCTIONS.tsv")
    repl = read("FIVE_HUNDRED_EIGHTIETH_IDIOM_REPLACEMENTS.tsv")
    summary = json.loads((HERE / "FIVE_HUNDRED_EIGHTIETH_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    checks = {
        "statements116": len(rows) == 116 and len({r["statement_id"] for r in rows}) == 116,
        "records11": len({r["record"] for r in rows}) == 11,
        "replacements16": len(repl) == 16,
        "shorter": summary["compact_words"] < summary["source_words"] and summary["words_saved"] > 0,
        "no_modern_meta": all(r["modern_meta_phrases_remaining"] == "NO" for r in rows),
        "slots_preserved": all(r["semantic_slots_preserved"] == "YES" for r in rows),
        "nonempty": all(r["compact_workshop_instruction_de"].strip() for r in rows),
        "fixed_pages": {r["page"] for r in rows} <= {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"},
        "seal_absent": all(not r["page"].lower().startswith("f84") for r in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_EIGHTIETH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
