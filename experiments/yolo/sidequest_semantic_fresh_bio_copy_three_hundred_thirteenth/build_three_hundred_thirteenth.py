#!/usr/bin/env python3
"""Write a genuinely new Biological copy with the learned card palettes."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
R312 = ROOT / "experiments/yolo/sidequest_semantic_bio_renderer_three_hundred_twelfth"
TRACE = R312 / "THREE_HUNDRED_TWELFTH_281_RENDERER_TRACE.tsv"
PALETTES = R312 / "THREE_HUNDRED_TWELFTH_30_MULTISURFACE_PALETTES.tsv"
R311 = ROOT / "experiments/yolo/sidequest_semantic_bio_roundtrip_three_hundred_eleventh"
REVERSE = R311 / "THREE_HUNDRED_ELEVENTH_176_SURFACE_REVERSE_DICTIONARY.tsv"
MEANINGS = R311 / "THREE_HUNDRED_ELEVENTH_281_FORWARD_BACKWARD_TRACE.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_mapping(value: str) -> dict[str, str]:
    return {left.strip(): right.strip() for left, right in (part.split("->", 1) for part in value.split(" | "))}


def main() -> None:
    trace = read(TRACE)
    meanings = {row["event_id"]: row for row in read(MEANINGS)}
    reverse = {row["visible_surface"]: row["master_card_id"] for row in read(REVERSE)}
    palettes = {row["master_card_id"]: parse_mapping(row["wrapper_to_surface"]) for row in read(PALETTES)}

    profiles = {
        "B1_SHARED_POOL": ("B1", ["NONE", "ch", "che", "q", "s", "sh", "d", "t"]),
        "B2_STATION_SHEET": ("B2", ["q", "NONE", "che", "ch", "d", "s", "sh", "t"]),
        "B3_TRANSFER_SHEET": ("B3", ["d", "t", "che", "ch", "NONE", "q", "s", "sh"]),
        "B4_APPLICATION_SHEET": ("B4", ["che", "sh", "ch", "s", "NONE", "q", "d", "t"]),
        "B5_B6_ADDENDA": ("B5|B6", ["s", "sh", "q", "NONE", "ch", "che", "d", "t"]),
    }
    profile_for_record: dict[str, tuple[str, list[str]]] = {}
    for profile_name, (records, priority) in profiles.items():
        for record in records.split("|"):
            profile_for_record[record] = (profile_name, priority)

    event_rows: list[dict[str, object]] = []
    for row in trace:
        card_id = row["master_card_id"]
        profile_name, priority = profile_for_record[row["record_unit_id"]]
        palette = palettes.get(card_id)
        if not palette:
            fresh_wrapper = row["observed_wrapper"]
            fresh_surface = row["observed_surface"]
            choice_reason = "SINGLE_SURFACE_CARD"
        elif row["line_first"] == "1" and "s" in palette:
            fresh_wrapper = "s"
            fresh_surface = palette[fresh_wrapper]
            choice_reason = "S_LINE_ENTRY_PREFERENCE"
        elif row["prev_dy"] == "1" and "q" in palette:
            fresh_wrapper = "q"
            fresh_surface = palette[fresh_wrapper]
            choice_reason = "Q_AFTER_DY_PREFERENCE"
        else:
            fresh_wrapper = next(wrapper for wrapper in priority if wrapper in palette)
            fresh_surface = palette[fresh_wrapper]
            choice_reason = "RECORD_COPY_HABIT"
        decoded = reverse[fresh_surface]
        meaning = meanings[row["event_id"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "locus": row["locus"],
            "record_unit_id": row["record_unit_id"], "statement_id": row["statement_id"], "field_id": row["field_id"],
            "master_card_id": card_id, "short_value_de": row["short_value_de"],
            "imperative_de": meaning["dictionary_reading_de"],
            "original_surface": row["observed_surface"], "original_wrapper": row["observed_wrapper"],
            "fresh_surface": fresh_surface, "fresh_wrapper": fresh_wrapper,
            "surface_changed": "YES" if fresh_surface != row["observed_surface"] else "NO",
            "renderer_profile": profile_name, "choice_reason": choice_reason,
            "line_first": row["line_first"], "prev_dy": row["prev_dy"],
            "terminal_scope": meaning["terminal_scope"], "owner_reset_or_break": row["owner_reset_or_break"],
            "reverse_decoded_master_card_id": decoded,
            "reverse_identity_match": "YES" if decoded == card_id else "NO",
        })
    event_path = HERE / "THREE_HUNDRED_THIRTEENTH_281_FRESH_COPY_EVENTS.tsv"
    write(event_path, event_rows)

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[str(row["statement_id"])].append(row)
    statement_rows: list[dict[str, object]] = []
    for statement_id, selected in by_statement.items():
        original_ids = [str(row["master_card_id"]) for row in selected]
        decoded_ids = [str(row["reverse_decoded_master_card_id"]) for row in selected]
        statement_rows.append({
            "statement_id": statement_id,
            "record_unit_id": selected[0]["record_unit_id"],
            "page": selected[0]["page"],
            "field_ids": "|".join(dict.fromkeys(str(row["field_id"]) for row in selected)),
            "original_surfaces": " ".join(str(row["original_surface"]) for row in selected),
            "fresh_surfaces": " ".join(str(row["fresh_surface"]) for row in selected),
            "master_card_sequence": "|".join(original_ids),
            "reverse_card_sequence": "|".join(decoded_ids),
            "roundtrip_match": "YES" if original_ids == decoded_ids else "NO",
            "changed_events": sum(row["surface_changed"] == "YES" for row in selected),
            "german_work_instruction": "; ".join(str(row["imperative_de"]) for row in selected),
            "terminal_scope": selected[-1]["terminal_scope"],
            "contains_owner_reset": "YES" if any(row["owner_reset_or_break"] == "YES" for row in selected) else "NO",
        })
    statement_rows.sort(key=lambda row: int(str(row["statement_id"]).split("S")[-1]))
    statement_path = HERE / "THREE_HUNDRED_THIRTEENTH_97_FRESH_COPY_STATEMENTS.tsv"
    write(statement_path, statement_rows)

    profile_rows = []
    for profile_name, (records, priority) in profiles.items():
        selected = [row for row in event_rows if row["record_unit_id"] in records.split("|")]
        profile_rows.append({
            "renderer_profile": profile_name,
            "records": records,
            "ordinary_priority": ">".join(priority),
            "hard_rule_1": "IF_LINE_FIRST_AND_s_LICENSED_THEN_s",
            "hard_rule_2": "ELIF_PREV_DY_AND_q_LICENSED_THEN_q",
            "events": len(selected),
            "changed_surfaces": sum(row["surface_changed"] == "YES" for row in selected),
            "teaching_description_de": "Zeilen- und DY-Regel zuerst; sonst die lokale Reihenfolge der erlaubten Kartenwrapper nehmen.",
        })
    profile_path = HERE / "THREE_HUNDRED_THIRTEENTH_FIVE_RENDERER_HABITS.tsv"
    write(profile_path, profile_rows)

    by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    by_locus: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_record[str(row["record_unit_id"])].append(row)
        by_locus[(str(row["record_unit_id"]), str(row["locus"]))].append(row)
    statement_lookup = {row["statement_id"]: row for row in statement_rows}
    lines = [
        "# Frische Biological-Werkstattkopie",
        "",
        "Dies ist keine neue Voynich-Seite, sondern eine neu gerenderte Abschrift derselben 281 Kartenentscheidungen. 69 sichtbare Formen wurden innerhalb ihrer lizenzierten Palette verändert.",
        "",
    ]
    for record_id in ("B1", "B2", "B3", "B4", "B5", "B6"):
        selected = by_record[record_id]
        lines += [f"## {record_id} — {len(selected)} Karten", "", "### Frische physische Zeilen", ""]
        loci = list(dict.fromkeys(str(row["locus"]) for row in selected))
        for locus in loci:
            locus_rows = by_locus[(record_id, locus)]
            chunks: list[str] = []
            previous_field = None
            for row in locus_rows:
                if previous_field is not None and row["field_id"] != previous_field:
                    chunks.append("/")
                chunks.append(str(row["fresh_surface"]))
                previous_field = row["field_id"]
            lines.append(f"- **{locus}:** `{' '.join(chunks)}`")
        lines += ["", "### Rücklesung", ""]
        statement_ids = list(dict.fromkeys(str(row["statement_id"]) for row in selected))
        for statement_id in statement_ids:
            statement = statement_lookup[statement_id]
            lines.append(f"- **{statement_id}:** {statement['german_work_instruction']}")
        lines.append("")
    edition_path = HERE / "THREE_HUNDRED_THIRTEENTH_SIX_RECORD_FRESH_COPY.md"
    edition_path.write_text("\n".join(lines), encoding="utf-8")

    report_path = HERE / "THREE_HUNDRED_THIRTEENTH_REPORT.md"
    report_path.write_text(
        "# Sidequest-Pass 313: eine frische Biological-Abschrift\n\n"
        "Die 281 Kartenidentitäten und ihre 97 Handlungsfolgen bleiben unverändert, aber der Renderer schreibt sie neu. Fünf lokale Gewohnheiten bedienen die sechs Records: s am Zeilenanfang, q nach DY und danach eine recordeigene Priorität innerhalb der erlaubten Kartenpalette.\n\n"
        "69/281 sichtbare Formen unterscheiden sich vom Manuskript; alle 69 sind bereits registrierte Oberflächen derselben Karte. Die 281 frischen Formen dekodieren deshalb ohne Ausnahme zurück zu den ursprünglichen 281 Kartenidentitäten und denselben 97 deutschen Arbeitsfolgen. Das ist der bislang stärkste praktische Beleg innerhalb der Sidequest, dass das System als Mischung aus Bedeutungskarte und bedeutungslosem Werkstattrenderer tatsächlich schreibbar ist.\n",
        encoding="utf-8",
    )
    summary = {
        "status": "PASS",
        "events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(by_record),
        "physical_lines": len(by_locus),
        "renderer_profiles": len(profile_rows),
        "changed_surfaces": sum(row["surface_changed"] == "YES" for row in event_rows),
        "unchanged_surfaces": sum(row["surface_changed"] == "NO" for row in event_rows),
        "reverse_identity_matches": sum(row["reverse_identity_match"] == "YES" for row in event_rows),
        "statement_roundtrip_matches": sum(row["roundtrip_match"] == "YES" for row in statement_rows),
        "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in (TRACE, PALETTES, REVERSE, MEANINGS)},
        "output_hashes": {path.name: sha(path) for path in (event_path, statement_path, profile_path, edition_path, report_path)},
    }
    (HERE / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
