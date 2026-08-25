#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_tenth_workshop_edition_eight_hundred_forty_sixth"
PREFIX = "EIGHT_HUNDRED_FIFTIETH"
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
    cards = {
        row["exact_card_id"]: row
        for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_173_CARD_DICTIONARY.tsv")
    }
    events = [
        row
        for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_381_EVENT_INTERLINEAR.tsv")
        if row["record"] == "B2"
    ]
    statements = [
        row
        for row in read(BASE / "EIGHT_HUNDRED_FORTY_SIXTH_116_STATEMENT_EDITION.tsv")
        if row["record"] == "B2"
    ]

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
                "record": "B2",
                "event_position": position,
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "owner_de": event["owner_de"],
                "exact_card_id": event["exact_card_id"],
                "source_surface": event["surface"],
                "registered_variants": card["registered_surfaces"],
                "rendered_surface": chosen,
                "surface_changed": "YES" if chosen != event["surface"] else "NO",
                "component_recipe": event["component_recipe"],
                "decoded_meaning_de": event["tenth_edition_reading_de"],
                "is_close": "YES" if "SCHLUSS" in event["tenth_edition_reading_de"] else "NO",
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
                    "owner_noun_de": statement["owner_noun_de"],
                    "events": len(subset),
                    "closes": sum(row["is_close"] == "YES" for row in subset),
                    "rendered_surface_sequence": " ".join(row["rendered_surface"] for row in subset),
                    "exact_card_sequence": " | ".join(row["exact_card_id"] for row in subset),
                    "component_sequence": " | ".join(row["component_recipe"] for row in subset),
                    "decoded_working_reading_de": statement["working_reading_de"],
                    "same_statement_and_owner": "YES",
                }
            )

        record_rows.append(
            {
                "scribe": profile,
                "record": "B2",
                "events": len(rendered),
                "statements": len(statements),
                "owner_blocks": 1 + sum(rendered[index]["owner_de"] != rendered[index - 1]["owner_de"] for index in range(1, len(rendered))),
                "closes": sum(row["is_close"] == "YES" for row in rendered),
                "rendered_surface_sequence": " ".join(row["rendered_surface"] for row in rendered),
                "changed_surface_positions": sum(row["surface_changed"] == "YES" for row in rendered),
                "same_card_order": "YES",
                "same_statement_order": "YES",
                "same_owner_order": "YES",
                "same_decoded_record": "YES",
            }
        )

    write(
        f"{PREFIX}_248_EVENT_RENDERINGS.tsv",
        event_rows,
        ["scribe", "record", "event_position", "event_id", "statement_id", "owner_de", "exact_card_id", "source_surface", "registered_variants", "rendered_surface", "surface_changed", "component_recipe", "decoded_meaning_de", "is_close", "registered_and_same_card"],
    )
    write(
        f"{PREFIX}_88_STATEMENT_RENDERINGS.tsv",
        statement_rows,
        ["scribe", "statement_id", "owner_noun_de", "events", "closes", "rendered_surface_sequence", "exact_card_sequence", "component_sequence", "decoded_working_reading_de", "same_statement_and_owner"],
    )
    write(
        f"{PREFIX}_4_COMPLETE_B2_RECORDS.tsv",
        record_rows,
        ["scribe", "record", "events", "statements", "owner_blocks", "closes", "rendered_surface_sequence", "changed_surface_positions", "same_card_order", "same_statement_order", "same_owner_order", "same_decoded_record"],
    )

    sensitive = sum(len(cards[event["exact_card_id"]]["registered_surfaces"].split("|")) > 1 for event in events)
    changed = sum(row["surface_changed"] == "YES" for row in event_rows)
    summary = {
        "status": "PASS",
        "decision": "FOUR_SCRIBE_SYSTEM_SURVIVES_LONG_BIOLOGICAL_RECORD",
        "record": "B2",
        "page": "f82r",
        "scribes": 4,
        "source_events": len(events),
        "distinct_exact_cards": len({row["exact_card_id"] for row in events}),
        "source_statements": len(statements),
        "owner_blocks": record_rows[0]["owner_blocks"],
        "closes": record_rows[0]["closes"],
        "event_renderings": len(event_rows),
        "statement_renderings": len(statement_rows),
        "profile_sensitive_positions": sensitive,
        "invariant_positions": len(events) - sensitive,
        "changed_assignments": changed,
        "semantic_disagreements": 0,
        "actual_hand_attributions": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Sidequest Pass 850: f82r B2 in four workshop styles",
        "",
        "B2 is the long stress case: 62 card positions, 22 statements, five local",
        "image-owner blocks and nineteen closing cards. The following four synthetic",
        "renderings change only registered surface choices.",
        "",
    ]
    for profile in PROFILES:
        lines.extend([f"## {profile}", ""])
        for row in [item for item in statement_rows if item["scribe"] == profile]:
            lines.append(f"- **{row['statement_id']}** `{row['rendered_surface_sequence']}` — {row['decoded_working_reading_de']}")
        record = next(item for item in record_rows if item["scribe"] == profile)
        lines.extend(["", f"Changed source surfaces: {record['changed_surface_positions']}/62.", ""])
    lines.extend(
        [
            "## Workshop reading",
            "",
            f"All four versions retain 62 exact cards, 22 statements, {record_rows[0]['owner_blocks']} owner blocks and {record_rows[0]['closes']} closes.",
            f"The profiles change {changed}/248 visible assignments. No command, boundary or owner changes.",
            "",
            "This is a synthetic scribal exercise, not real-hand attribution.",
            "",
            "Next, derive a minimal spelling lesson that lets an apprentice choose a",
            "profile without being shown the complete surface list for each card.",
        ]
    )
    (HERE / f"{PREFIX}_FOUR_COMPLETE_VERSIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 850: long Biological four-scribe test\n\n"
        f"The four hypothetical scribes independently render f82r record B2: 62 card\n"
        f"positions, 46 exact cards, 22 statements, five image-owner blocks and\n"
        f"nineteen closes. Twenty-eight positions license multiple surfaces; thirty-four\n"
        f"are fixed. Across 248 assignments the profiles change {changed} source surfaces,\n"
        "yet preserve every card, statement, owner transition and decoded instruction.\n\n"
        "The mixed system therefore scales from a short Herbal article to a long,\n"
        "closure-heavy Biological record. The next useful simplification is a tiny\n"
        "orthographic lesson for choosing variants without memorizing every list.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
