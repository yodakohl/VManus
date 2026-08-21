#!/usr/bin/env python3
"""Replace position polarity with the existing identity-consistent f69 rules."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
V16 = HERE.parent / "sidequest_theory_candidates_v16"
V21 = HERE.parent / "sidequest_theory_candidates_v21"


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
    source = read(V16 / "V16_R2_COMPLETE_TRANSLATION_LEDGER.tsv")
    lexicon = read(V21 / "V21_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv")
    ledger = read(V21 / "V21_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    loci = {f"f69v.{number}" for number in range(4, 32)}
    source_rows = [row for row in source if row["locus"] in loci]
    assert len(source_rows) == 33
    target_rows = [row for row in ledger if row["locus"] in loci]
    assert len(target_rows) == 33
    source_by_target_id = {}
    for number in range(4, 32):
        locus = f"f69v.{number}"
        source_at_locus = [row for row in source_rows if row["locus"] == locus]
        target_at_locus = [row for row in target_rows if row["locus"] == locus]
        assert [row["surface"] for row in source_at_locus] == [
            row["surface"] for row in target_at_locus
        ]
        for target, source_row in zip(target_at_locus, source_at_locus):
            source_by_target_id[target["exact_tuple_id"]] = source_row
    assert len(source_by_target_id) == 33

    entries = []
    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for number in range(4, 32):
        locus = f"f69v.{number}"
        rows = [row for row in source_rows if row["locus"] == locus]
        surface = " ".join(row["surface"] for row in rows)
        reading = "; ".join(row["default_English"] for row in rows)
        entry = {
            "station_index": str(number - 3),
            "locus": locus,
            "surface_entry": surface,
            "selected_concrete_rule": reading,
            "layout_parity": "LONG" if (number - 3) % 2 else "SHORT",
            "polarity_from_layout": "NO",
            "cross_page_alignment": "NONE",
        }
        entries.append(entry)
        by_surface[surface].append(entry)

    repeated = []
    for surface, rows in sorted(by_surface.items()):
        if len(rows) < 2:
            continue
        meanings = {row["selected_concrete_rule"] for row in rows}
        assert len(meanings) == 1
        repeated.append({
            "surface_entry": surface,
            "station_indices": "|".join(row["station_index"] for row in rows),
            "layout_parities": "|".join(row["layout_parity"] for row in rows),
            "shared_concrete_rule": next(iter(meanings)),
            "contradicts_odd_even_polarity": (
                "YES" if len({row["layout_parity"] for row in rows}) > 1 else "NO"
            ),
        })
    assert any(row["surface_entry"] == "okeod" and
               row["contradicts_odd_even_polarity"] == "YES" for row in repeated)
    write(HERE / "V22_F69_28_RULES.tsv", list(entries[0]), entries)
    write(HERE / "V22_REPEATED_RULE_AUDIT.tsv", list(repeated[0]), repeated)

    replacements = {
        target_id: (row["default_English"], row["confidence"], row["source_class"])
        for target_id, row in source_by_target_id.items()
    }
    changed_lexicon = 0
    for row in lexicon:
        if row["lexicon_id"] in replacements:
            meaning, confidence, source_class = replacements[row["lexicon_id"]]
            row["default_English"] = meaning
            row["confidence"] = confidence
            row["source_class"] = source_class
            row["inheritance_context_rule"] = (
                "V22 identity-consistent f69 radial rule; LONG/SHORT is not polarity."
            )
            changed_lexicon += 1
    assert changed_lexicon == 33
    write(HERE / "V22_SELECTED_COMPLETE_DEFAULT_LEXICON.tsv", list(lexicon[0]), lexicon)

    changed_events = 0
    for row in ledger:
        source_row = source_by_target_id.get(row["exact_tuple_id"])
        if source_row is not None:
            row["default_English"] = source_row["default_English"]
            row["confidence"] = source_row["confidence"]
            row["source_class"] = source_row["source_class"]
            row["inheritance_context_rule"] = (
                "V22 repeated-entry consistency; radial slot supplies station, text supplies rule."
            )
            changed_events += 1
    assert changed_events == 33
    assert len(ledger) == 776
    write(HERE / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv", list(ledger[0]), ledger)
    print("PASS f69_entries=28 radial_events=33 repeated_entries=%d changed=33 total=776" % len(repeated))


if __name__ == "__main__":
    main()
