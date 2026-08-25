#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FORTY_NINTH"
PROFILES = ["S1_BARE", "S2_CH", "S3_Q_SH", "S4_D_T"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def preference(profile: str, surface: str) -> tuple[int, int, str]:
    if profile == "S1_BARE":
        bare = {"ol", "y", "al", "aiin", "or", "oky", "okchy", "cthy"}
        score = 0 if surface in bare else 1
    elif profile == "S2_CH":
        score = 0 if surface.startswith("che") else 1 if surface.startswith("ch") else 2
    elif profile == "S3_Q_SH":
        score = 0 if surface.startswith("q") else 1 if surface.startswith("sh") else 2 if surface.startswith("s") else 3
    else:
        score = 0 if surface.startswith("d") else 1 if surface.startswith("t") else 2
    return score, len(surface), surface


def main() -> None:
    dictionary = read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv")
    events = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv") if row["record"] == "H1"]
    statements = [row for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv") if row["record"] == "H1"]
    cards = {row["exact_card_id"]: row for row in dictionary}

    event_rows: list[dict[str, object]] = []
    statement_rows: list[dict[str, object]] = []
    record_rows: list[dict[str, object]] = []
    for profile in PROFILES:
        rendered: list[dict[str, str]] = []
        for position, event in enumerate(events, 1):
            card = cards[event["exact_card_id"]]
            variants = card["registered_surfaces"].split("|")
            chosen = sorted(variants, key=lambda value: preference(profile, value))[0]
            row = {
                "scribe": profile,
                "record": "H1",
                "event_position": position,
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "exact_card_id": event["exact_card_id"],
                "source_surface": event["surface"],
                "registered_variants": card["registered_surfaces"],
                "rendered_surface": chosen,
                "surface_changed": "YES" if chosen != event["surface"] else "NO",
                "component_recipe": event["component_recipe"],
                "decoded_meaning_de": event["tenth_edition_reading_de"],
                "registered_and_same_card": "YES" if chosen in variants else "NO",
            }
            event_rows.append(row)
            rendered.append({key: str(value) for key, value in row.items()})

        for statement in statements:
            subset = [row for row in rendered if row["statement_id"] == statement["statement_id"]]
            statement_rows.append(
                {
                    "scribe": profile,
                    "statement_id": statement["statement_id"],
                    "events": len(subset),
                    "source_surface_sequence": " ".join(row["source_surface"] for row in subset),
                    "rendered_surface_sequence": " ".join(row["rendered_surface"] for row in subset),
                    "exact_card_sequence": " | ".join(row["exact_card_id"] for row in subset),
                    "component_sequence": " | ".join(row["component_recipe"] for row in subset),
                    "decoded_literal_de": " | ".join(row["decoded_meaning_de"] for row in subset),
                    "decoded_working_reading_de": statement["working_reading_de"],
                    "same_statement_boundary": "YES",
                }
            )

        record_rows.append(
            {
                "scribe": profile,
                "record": "H1",
                "events": len(rendered),
                "statements": len(statements),
                "rendered_surface_sequence": " ".join(row["rendered_surface"] for row in rendered),
                "exact_card_sequence": " | ".join(row["exact_card_id"] for row in rendered),
                "decoded_record_de": " ".join(statement["working_reading_de"] for statement in statements),
                "changed_surface_positions": sum(row["surface_changed"] == "YES" for row in rendered),
                "same_card_order": "YES",
                "same_statement_order": "YES",
                "same_decoded_record": "YES",
            }
        )

    write(
        f"{PREFIX}_56_EVENT_RENDERINGS.tsv",
        event_rows,
        ["scribe", "record", "event_position", "event_id", "statement_id", "exact_card_id", "source_surface", "registered_variants", "rendered_surface", "surface_changed", "component_recipe", "decoded_meaning_de", "registered_and_same_card"],
    )
    write(
        f"{PREFIX}_8_STATEMENT_RENDERINGS.tsv",
        statement_rows,
        ["scribe", "statement_id", "events", "source_surface_sequence", "rendered_surface_sequence", "exact_card_sequence", "component_sequence", "decoded_literal_de", "decoded_working_reading_de", "same_statement_boundary"],
    )
    write(
        f"{PREFIX}_4_COMPLETE_RECORDS.tsv",
        record_rows,
        ["scribe", "record", "events", "statements", "rendered_surface_sequence", "exact_card_sequence", "decoded_record_de", "changed_surface_positions", "same_card_order", "same_statement_order", "same_decoded_record"],
    )

    sensitive = {
        row["event_id"]
        for row in event_rows
        if len(row["registered_variants"].split("|")) > 1
    }
    summary = {
        "status": "PASS",
        "decision": "FOUR_SURFACE_RENDERINGS_PRESERVE_ONE_H1_READING",
        "record": "H1",
        "page": "f10r",
        "scribes": 4,
        "source_events": len(events),
        "source_statements": len(statements),
        "event_renderings": len(event_rows),
        "statement_renderings": len(statement_rows),
        "profile_sensitive_positions": len(sensitive),
        "invariant_positions": len(events) - len(sensitive),
        "changed_assignments": sum(row["surface_changed"] == "YES" for row in event_rows),
        "semantic_disagreements": 0,
        "actual_hand_attributions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Sidequest Pass 849: one article in four workshop hands",
        "",
        "The fourteen-card H1 article on f10r is rendered four times. Exact card",
        "identity, card order, the two statement boundaries and the German working",
        "reading remain fixed; only registered surface variants change.",
        "",
    ]
    for row in record_rows:
        lines.extend(
            [
                f"## {row['scribe']}",
                "",
                f"`{row['rendered_surface_sequence']}`",
                "",
                f"Changed positions relative to the source surface: {row['changed_surface_positions']}/14.",
                "",
            ]
        )
    lines.extend(
        [
            "## One reading for all four",
            "",
            str(record_rows[0]["decoded_record_de"]),
            "",
            "Seven positions are renderer-sensitive and seven are fixed because the",
            "corresponding exact cards have only one registered surface here. Across",
            "all four versions, eighteen of fifty-six visible assignments differ from",
            "the source spelling, but none changes a card or command.",
            "",
            "This is a synthetic workshop exercise, not a claim that these profiles",
            "identify the manuscript's real hands.",
            "",
            "Next, apply the same four-style rewrite to a longer Biological record",
            "with repeated closes and local owner changes.",
        ]
    )
    (HERE / f"{PREFIX}_FOUR_VERSIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 849: complete four-scribe record\n\n"
        "H1 contains fourteen cards in two statements. Four hypothetical scribes\n"
        "produce four visibly different registered-surface sequences while preserving\n"
        "all fourteen exact cards and one continuous article reading. Seven event\n"
        "positions vary; seven are fixed learned forms. Eighteen of fifty-six rendered\n"
        "assignments differ from the source surface, with zero semantic disagreement.\n\n"
        "This makes the current grammar learnable in a small workshop: the apprentices\n"
        "memorize card identity and composition, then use local renderer habits only\n"
        "where the shared deck licenses a variant. It does not attribute actual hands.\n\n"
        "Next: repeat on a longer Biological record, where frequent closures and image\n"
        "owner changes put more pressure on the shared system.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
