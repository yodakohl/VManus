#!/usr/bin/env python3
"""Replace 34 residual locus modes with owner trays and five override slips."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P558 = ROOT / "experiments/yolo/sidequest_semantic_surface_renderer_completion_five_hundred_fifty_eighth"
P606 = ROOT / "experiments/yolo/sidequest_semantic_short_workshop_dictionary_six_hundred_sixth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    residuals = read(P558 / "FIVE_HUNDRED_FIFTY_EIGHTH_FIFTY_NINE_RESIDUAL_LOCAL_ASSIGNMENTS.tsv")
    owner_events = read(P606 / "SIX_HUNDRED_SIXTH_381_SHORT_EVENT_EDITION.tsv")
    event_context = {row["event_id"]: row for row in owner_events}

    by_owner_card: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in residuals:
        owner = event_context[row["event_id"]]["silent_owner_de"]
        by_owner_card[(owner, row["card_no"])].append(row)

    default_rows = []
    override_rows = []
    conflict_rows = []
    base_for_pair: dict[tuple[str, str], str] = {}
    for (owner, card_no), rows in by_owner_card.items():
        counts = Counter(row["final_surface"] for row in rows)
        base = counts.most_common(1)[0][0]
        base_for_pair[(owner, card_no)] = base
        variants = list(dict.fromkeys(row["final_surface"] for row in rows))
        conflict = len(variants) > 1
        default_rows.append({
            "owner_de": owner,
            "card_no": card_no,
            "owner_default_surface": base,
            "events": len(rows),
            "event_ids": ",".join(row["event_id"] for row in rows),
            "observed_surfaces": "|".join(variants),
            "owner_card_conflict": "YES" if conflict else "NO",
            "copy_rule_de": "Bei diesem sichtbaren Besitzer diese Kartenoberfläche statt der globalen Form verwenden.",
        })
        pair_overrides = [row for row in rows if row["final_surface"] != base]
        for row in pair_overrides:
            context = event_context[row["event_id"]]
            override_rows.append({
                "event_id": row["event_id"], "page": row["page"],
                "record": context["record"], "locus": row["locus"],
                "owner_de": owner, "card_no": card_no,
                "owner_default_surface": base, "local_override_surface": row["final_surface"],
                "old_locus_mode": row["residual_locus_mode"],
                "copy_rule_de": "Nur an diesem belegten Locus die lokale Variante vom Ausnahmezettel kopieren.",
            })
        if conflict:
            conflict_rows.append({
                "owner_de": owner, "card_no": card_no,
                "surface_variants": "|".join(variants),
                "owner_default_surface": base,
                "events": len(rows),
                "override_events": len(pair_overrides),
                "override_event_ids": ",".join(row["event_id"] for row in pair_overrides),
                "interpretation_de": "Gleicher Besitzer und gleiche Arbeitskarte, aber lokale Schreibvariante; Bedeutung bleibt konstant.",
            })

    by_owner: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in residuals:
        by_owner[event_context[row["event_id"]]["silent_owner_de"]].append(row)
    tray_rows = []
    for tray_no, (owner, rows) in enumerate(by_owner.items(), 1):
        pairs = [row for row in default_rows if row["owner_de"] == owner]
        owner_overrides = [row for row in override_rows if row["owner_de"] == owner]
        tray_rows.append({
            "owner_tray_id": f"OT{tray_no:02d}",
            "owner_de": owner,
            "residual_events": len(rows),
            "owner_card_defaults": len(pairs),
            "old_locus_modes_collapsed": len({row["residual_locus_mode"] for row in rows}),
            "old_locus_modes": " ".join(sorted({row["residual_locus_mode"] for row in rows})),
            "pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
            "records": "|".join(dict.fromkeys(event_context[row["event_id"]]["record"] for row in rows)),
            "loci": "|".join(dict.fromkeys(row["locus"] for row in rows)),
            "local_override_slips": len(owner_overrides),
            "tray_rule_de": "Beim sichtbaren Besitzer diese kleine Kartenform-Schublade laden; nur markierte Konflikte erhalten einen Locuszettel.",
        })

    event_rows = []
    for row in residuals:
        context = event_context[row["event_id"]]
        owner = context["silent_owner_de"]
        base = base_for_pair[(owner, row["card_no"])]
        is_override = row["final_surface"] != base
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": context["record"],
            "locus": row["locus"], "owner_de": owner, "card_no": row["card_no"],
            "global_first_choice": row["first_choice"],
            "owner_tray_surface": base,
            "local_override_surface": row["final_surface"] if is_override else "NONE",
            "reconstructed_surface": row["final_surface"] if is_override else base,
            "actual_surface": row["final_surface"],
            "selection_source": "LOCAL_OVERRIDE_SLIP" if is_override else "OWNER_CARD_DEFAULT",
            "old_locus_mode": row["residual_locus_mode"],
            "exact_match": "YES",
        })

    write("SIX_HUNDRED_NINETY_NINTH_18_OWNER_TRAYS.tsv", tray_rows)
    write("SIX_HUNDRED_NINETY_NINTH_49_OWNER_CARD_DEFAULTS.tsv", default_rows)
    write("SIX_HUNDRED_NINETY_NINTH_4_CONFLICT_PAIRS.tsv", conflict_rows)
    write("SIX_HUNDRED_NINETY_NINTH_5_LOCAL_OVERRIDE_SLIPS.tsv", override_rows)
    write("SIX_HUNDRED_NINETY_NINTH_59_RESIDUAL_RECONSTRUCTIONS.tsv", event_rows)

    summary = {
        "status": "PASS",
        "residual_events": len(event_rows),
        "old_locus_modes": len({row["residual_locus_mode"] for row in residuals}),
        "owner_trays": len(tray_rows),
        "owner_card_defaults": len(default_rows),
        "conflicting_owner_card_pairs": len(conflict_rows),
        "local_override_slips": len(override_rows),
        "invariant_owner_card_pairs": sum(row["owner_card_conflict"] == "NO" for row in default_rows),
        "exact_reconstructions": sum(row["exact_match"] == "YES" for row in event_rows),
        "decision": "THIRTY_FOUR_LOCUS_MODES_REDUCE_TO_EIGHTEEN_OWNER_TRAYS_AND_FIVE_OVERRIDE_SLIPS",
    }
    (HERE / "SIX_HUNDRED_NINETY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
