#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    events = read("FIVE_HUNDRED_NINETY_SEVENTH_381_PROSE_EVENT_BACKREAD.tsv")
    statements = read("FIVE_HUNDRED_NINETY_SEVENTH_116_PROSE_STATEMENT_BACKREAD.tsv")
    fragments = read("FIVE_HUNDRED_NINETY_SEVENTH_395_ASTRO_FRAGMENT_BACKREAD.tsv")
    loci = read("FIVE_HUNDRED_NINETY_SEVENTH_142_ASTRO_LOCUS_BACKREAD.tsv")
    manual = read("FIVE_HUNDRED_NINETY_SEVENTH_TWELVE_STEP_CORRECTOR_MANUAL.tsv")
    prose = Counter(row["resolution_class"] for row in statements)
    astro = Counter(row["resolution_class"] for row in loci)
    checks = {
        "events381": len(events) == 381 and len({row["event_id"] for row in events}) == 381,
        "cards_exact381": sum(row["card_recovery"] == "EXACT" for row in events) == 381,
        "values_exact381": sum(row["value_recovery"] == "EXACT" for row in events) == 381,
        "statements116": len(statements) == 116,
        "prose_resolution92_17_7": prose == Counter({"SURFACE_SEQUENCE_UNIQUE": 92, "IMAGE_OWNER_RESOLVES_OCCURRENCE": 17, "REPEATED_SAME_OWNER_AND_INSTRUCTION": 7}),
        "no_functional_ambiguity": all(row["functional_instruction_ambiguity_after_owner"] == "NO" for row in statements),
        "fragments395": len(fragments) == 395 and len({row["opaque_local_id"] for row in fragments}) == 395,
        "ambiguous_fragments140": sum(row["fragment_self_identifying"] == "NO" for row in fragments) == 140,
        "loci142": len(loci) == 142 and len({row["locus"] for row in loci}) == 142,
        "astro_resolution137_2_3": astro == Counter({"FULL_LOCUS_SURFACE_UNIQUE": 137, "NAMESPACE_RESOLVES": 2, "IMAGE_OWNER_RESOLVES": 3}),
        "owner_unique142": all(row["owner_plus_surface_occurrences"] == "1" for row in loci),
        "external_values_not_invented": all(row["external_master_value_recovered_from_surface"] == "NO" for row in loci),
        "manual12": len(manual) == 12 and [int(row["step"]) for row in manual] == list(range(1, 13)),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_NINETY_SEVENTH_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
