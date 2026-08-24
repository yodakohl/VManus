#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    with (HERE / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    prose = read("FIVE_HUNDRED_FORTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_PRACTICAL_PROSE_INTERLINEAR.tsv")
    statements = read("FIVE_HUNDRED_FORTY_FOURTH_ONE_HUNDRED_SIXTEEN_COMPLETE_PROSE_STATEMENTS.tsv")
    astro = read("FIVE_HUNDRED_FORTY_FOURTH_THREE_HUNDRED_NINETY_FIVE_PRACTICAL_ASTRO_INTERLINEAR.tsv")
    unified = read("FIVE_HUNDRED_FORTY_FOURTH_SEVEN_HUNDRED_SEVENTY_SIX_UNIFIED_PRACTICAL_LEDGER.tsv")
    by_card = defaultdict(set)
    for row in prose:
        by_card[row["card_no"]].add(row["literal_card_reading_de"])
    checks = {
        "prose381": len(prose) == 381 and [row["event_id"] for row in prose] == [f"E{i:03d}" for i in range(1, 382)],
        "prose_source380": len({row["source_position_id"] for row in prose}) == 380 and prose[179]["source_position_id"] == prose[180]["source_position_id"] == "SRC_E180_E181",
        "statements116": len(statements) == 116 and sum(len(row["event_ids"].split("|")) for row in statements) == 381,
        "closed89_open27": Counter(row["terminal"] for row in statements) == Counter({"YES": 89, "NO": 27}),
        "astro395": len(astro) == 395 and Counter(row["page"] for row in astro) == Counter({"f67r2": 190, "f68r1": 65, "f69v": 140}),
        "astro_loci142": len({(row["page"], row["locus"]) for row in astro}) == 142,
        "unified776": len(unified) == 776 and [row["unified_index"] for row in unified] == [f"U{i:03d}" for i in range(1, 777)],
        "unified_sources775": len({row["source_position_id"] for row in unified}) == 775,
        "kind_counts381_395": Counter(row["kind"] for row in unified) == Counter({"PROSE_CARD": 381, "ASTRO_GROUP": 395}),
        "card_values_invariant": all(len(values) == 1 for values in by_card.values()) and len(by_card) == 173,
        "composition374_4_3": Counter(row["composition_status"] for row in prose) == Counter({"COMPOSITIONAL": 374, "PARTIAL_WITH_LEARNED_ATOM": 4, "LEARNED_WHOLE_CARD": 3}),
        "no_blanks": all(row["blank"] == "NO" and row["literal_value_de"] and row["practical_expansion_de"] for row in unified),
        "no_astro_join": all(row["crosspage_join"] == "NONE" and row["prose_card_import"] == "NONE" for row in astro),
        "fixed_pages10": {row["page"] for row in unified} == {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"},
        "seal_absent": all(not row["page"].lower().startswith("f84") for row in unified),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (HERE / "FIVE_HUNDRED_FORTY_FOURTH_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for key, value in checks.items():
        print(f"{key}\t{'PASS' if value else 'FAIL'}")
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
