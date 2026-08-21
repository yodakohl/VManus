#!/usr/bin/env python3
"""Build the bounded V21 three-page consultation and propagate 12 body areas."""

from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
V20 = HERE.parent / "sidequest_theory_candidates_v20"

SIGNS = [
    ("Aries", "head and face"), ("Taurus", "neck and throat"),
    ("Gemini", "shoulders, arms and hands"), ("Cancer", "chest and breast"),
    ("Leo", "heart and upper back"), ("Virgo", "belly and intestines"),
    ("Libra", "lower back and kidneys"), ("Scorpio", "genitals and bladder"),
    ("Sagittarius", "hips and thighs"), ("Capricorn", "knees"),
    ("Aquarius", "shins and ankles"), ("Pisces", "feet"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    lexicon = read(V20 / "V20_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(V20 / "V20_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    astro = [row for row in ledger if row["page"] in {"f67r2", "f68r1", "f69v"}]
    assert len(astro) == 395

    revised: dict[str, tuple[str, str]] = {}
    sign_rows = []
    for number, (sign, body) in enumerate(SIGNS, 1):
        locus = f"f67r2.{number}"
        candidates = [row for row in astro if row["locus"] == locus and
                      row["default_English"].startswith("zodiac division")]
        assert len(candidates) == 1
        row = candidates[0]
        meaning = f"{sign}: protect the {body}; avoid invasive treatment there"
        revised[row["exact_tuple_id"]] = (meaning, ".36")
        sign_rows.append({
            "page": "f67r2", "local_index": str(number), "locus": locus,
            "surface": row["surface"], "working_owner": sign,
            "working_medical_role": body,
            "complete_instruction": meaning,
            "alignment_status": "LOCAL_TWELVEFOLD_ORDER_ONLY",
        })
    write(HERE / "V21_ZODIAC_BODY_SELECTOR.tsv", list(sign_rows[0]), sign_rows)

    station_rows = []
    for index in range(1, 29):
        spatial_locus = f"f68r1.{index + 8}"
        schedule_locus = f"f69v.{index + 3}"
        spatial = [row for row in astro if row["locus"] == spatial_locus]
        schedule = [row for row in astro if row["locus"] == schedule_locus]
        assert len(spatial) == 1
        assert schedule
        station_rows.append({
            "working_index": str(index),
            "f68_spatial_locus": spatial_locus,
            "f68_surface": spatial[0]["surface"],
            "f68_role": "identify the drawn lunar station by its spatial pattern",
            "f69_schedule_locus": schedule_locus,
            "f69_surface": " ".join(row["surface"] for row in schedule),
            "f69_working_rule": schedule[0]["default_English"],
            "cross_page_alignment": "NOT_VISIBLE_CONVENTIONAL_INDEX_REQUIRED",
        })
    write(HERE / "V21_28_STATION_CONSULTATION.tsv", list(station_rows[0]),
          station_rows)

    changed_lexicon = 0
    for row in lexicon:
        if row["lexicon_id"] in revised:
            row["default_English"], row["confidence"] = revised[row["lexicon_id"]]
            row["source_class"] = "ZODIAC_BODY_SAFETY_SELECTOR"
            row["inheritance_context_rule"] = (
                "V21 local twelvefold melothesia expansion; sign assignment remains speculative."
            )
            changed_lexicon += 1
    assert changed_lexicon == 12
    write(HERE / "V21_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", list(lexicon[0]), lexicon)

    changed_events = 0
    for row in ledger:
        if row["exact_tuple_id"] in revised:
            row["default_English"], row["confidence"] = revised[row["exact_tuple_id"]]
            row["source_class"] = "ZODIAC_BODY_SAFETY_SELECTOR"
            row["inheritance_context_rule"] = (
                "V21 local twelvefold melothesia expansion; no phonetic label claim."
            )
            changed_events += 1
    assert changed_events == 12
    assert len(ledger) == 776
    write(HERE / "V21_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", list(ledger[0]), ledger)
    print("PASS astro_events=395 zodiac_body_rows=12 station_rows=28 changed=12 total=776")


if __name__ == "__main__":
    main()
