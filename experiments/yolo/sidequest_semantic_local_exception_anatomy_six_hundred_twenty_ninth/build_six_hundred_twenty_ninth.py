#!/usr/bin/env python3
"""Explain or compress the remaining 21 local surface exceptions."""

from __future__ import annotations

import csv
import io
import json
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXCEPTION_DIR = ROOT / "experiments/yolo/sidequest_semantic_compact_surface_manual_six_hundred_twenty_eighth"
FORWARD_DIR = ROOT / "experiments/yolo/sidequest_semantic_forward_workshop_compiler_six_hundred_twenty_seventh"
LAYER_DIR = ROOT / "experiments/yolo/sidequest_semantic_layered_readable_six_hundred_eighteenth"
PAGES = ("f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


CAUSES = {
    "E011": ("FIELD_ENTRY_LOCAL_COPY", "KEEP_LOCAL", "neuer H1-Untergang beginnt mit q; nur einmal in dieser Kartenidentitaet"),
    "E022": ("Y_AIIN_Y_DESK_CENTER", "RESOLVED_COMPACT_RULE", "P-Schreibtisch schreibt die Mittelkarte der Y-AIIN-Y-Formel mit t"),
    "E033": ("REPEATED_OR_CONTRAST", "KEEP_LOCAL", "shor steht zwischen gleichwertigen OR-Nachbarn; Kontrast ist plausibel, aber nur einmal"),
    "E061": ("POST_CLOSE_D_ENTRY", "KEEP_LOCAL", "neuer H4-Feldposten nach Schluss beginnt mit d; nicht die allgemeine q-Regel"),
    "E081": ("H5_LOCAL_CHAIN", "KEEP_LOCAL", "choky ist die lokale Mittelkarte zwischen otchor und dal"),
    "E083": ("RESUME_S_ENTRY", "KEEP_LOCAL", "WIEDERAUFNEHMEN beginnt den neuen H5-Faden mit s; semantisch passend, aber einmalig"),
    "E105": ("B1_SOURCE_LINK_CHAIN", "KEEP_LOCAL", "sar steht lokal zwischen Ziel-Ansetzen und Fortsetzen"),
    "E148": ("B1_CONTINUE_NEAR_LINE_END", "KEEP_LOCAL", "qol steht als Fortsetzung nahe dem physischen Zeilenende"),
    "E153": ("B1_THREE_CARD_CADENCE", "GROUPED_PHRASE", "erster Teil der memorierten Folge okeey-qol-cheedy"),
    "E154": ("B1_THREE_CARD_CADENCE", "GROUPED_PHRASE", "zweiter Teil der memorierten Folge okeey-qol-cheedy"),
    "E155": ("B1_THREE_CARD_CADENCE", "GROUPED_PHRASE", "dritter und schliessender Teil der memorierten Folge okeey-qol-cheedy"),
    "E186": ("B2_TARGET_HOLD_CHAIN", "KEEP_LOCAL", "qokal steht zwischen Danach-Lang und Halten am Durchlass"),
    "E233": ("Y_AIIN_Y_DESK_CENTER", "RESOLVED_COMPACT_RULE", "S-Schreibtisch schreibt die Mittelkarte der Y-AIIN-Y-Formel mit d"),
    "E239": ("B3_SINGLE_CELL_S_CLOSE", "KEEP_LOCAL", "einzelne Umsetzen-Schlusskarte wird lokal als schedy kopiert"),
    "E254": ("B3_S_FIELD_ENTRY", "KEEP_LOCAL", "neuer B3-Feldposten beginnt den Ansatz mit s"),
    "E268": ("B3_POST_CLOSE_D_TARGET", "KEEP_LOCAL", "Zielstelle beginnt nach Schluss lokal mit d"),
    "E271": ("B3_READY_GATE_S_FORM", "KEEP_LOCAL", "Bereit-Posten verwendet innerhalb der B3-Kette die sh-Form"),
    "E283": ("B3_POST_CLOSE_T_SINGLE_CELL", "KEEP_LOCAL", "einzelne Umsetzen-Schlusskarte nach Schluss wird lokal mit t kontrastiert"),
    "E291": ("B3_S_SINGLE_CELL_COLLECT", "KEEP_LOCAL", "einzelne Auffangen-Lang-Schlusskarte traegt die lokale s-Form"),
    "E352": ("Q_POST_CLOSE_ENTRY", "RESOLVED_COMPACT_RULE", "q markiert den neuen Portionseintrag direkt nach einer Schlusskarte"),
    "E366": ("B5_LINK_CHAIN", "KEEP_LOCAL", "cheol steht zwischen Zielstelle und Weiterleiten-Fortsetzen"),
}


def guarded_formal_rows() -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", "gdt327_joint_tuple_interlinear.tsv", "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend([
        "--columns",
        "page,locus,group_index,group_count,register,hand,within_field_position,joint_tuple_id,observed_wrapper",
        "--forbid-prefix", "f84",
    ])
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    stats_line = next(line for line in result.stderr.splitlines() if line.startswith("GUARD_STATS "))
    return rows, json.loads(stats_line.removeprefix("GUARD_STATS "))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    exceptions = read_tsv(EXCEPTION_DIR / "SIX_HUNDRED_TWENTY_EIGHTH_21_LOCAL_SURFACE_EXCEPTIONS.tsv")
    compact = read_tsv(EXCEPTION_DIR / "SIX_HUNDRED_TWENTY_EIGHTH_372_COMPACT_SURFACE_WRITER.tsv")
    forward = read_tsv(FORWARD_DIR / "SIX_HUNDRED_TWENTY_SEVENTH_372_FORWARD_EVENT_COMPILATION.tsv")
    all_events = read_tsv(LAYER_DIR / "SIX_HUNDRED_EIGHTEENTH_381_LAYERED_EVENTS.tsv")
    formal, guard_stats = guarded_formal_rows()
    if len(formal) != len(all_events) or len(exceptions) != 21:
        raise ValueError((len(formal), len(all_events), len(exceptions)))
    all_index = {row["event_id"]: index for index, row in enumerate(all_events)}
    formal_by_event = {event["event_id"]: source for event, source in zip(all_events, formal)}
    forward_by_event = {row["event_id"]: row for row in forward}

    cause_rows = []
    for row in exceptions:
        event_id = row["event_id"]
        event = forward_by_event[event_id]
        source = formal_by_event[event_id]
        index = all_index[event_id]
        previous = all_events[index - 1] if index > 0 and all_events[index - 1]["record"] == event["record"] else None
        following = all_events[index + 1] if index + 1 < len(all_events) and all_events[index + 1]["record"] == event["record"] else None
        post_close = bool(previous and previous["semantic_component_parse"].endswith("+DY") and source["within_field_position"] in {"FIRST", "ONLY"})
        cause, status, explanation = CAUSES[event_id]
        if status == "RESOLVED_COMPACT_RULE":
            deck_entry = "NONE"
        elif cause == "B1_THREE_CARD_CADENCE":
            deck_entry = "X01_B1_KEEY_OL_SHED_CADENCE"
        else:
            deck_entry = f"X_{event_id}"
        cause_rows.append({
            "event_id": event_id,
            "case_id": row["case_id"],
            "page": source["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "locus": source["locus"],
            "physical_group_position": f"{source['group_index']}/{source['group_count']}",
            "field_position": source["within_field_position"],
            "register": source["register"],
            "hand": source["hand"],
            "previous_event_surface_parse": f"{previous['event_id']}:{previous['surface']}:{previous['semantic_component_parse']}" if previous else "NONE",
            "current_surface_parse": f"{event_id}:{row['memorized_surface']}:{event['semantic_component_parse']}",
            "next_event_surface_parse": f"{following['event_id']}:{following['surface']}:{following['semantic_component_parse']}" if following else "NONE",
            "post_close_field_entry": "YES" if post_close else "NO",
            "cause_class": cause,
            "resolution_status": status,
            "working_explanation_de": explanation,
            "compact_exception_entry": deck_entry,
        })

    deck_groups: dict[str, list[dict[str, str]]] = {}
    for row in cause_rows:
        entry = row["compact_exception_entry"]
        if entry == "NONE":
            continue
        deck_groups.setdefault(entry, []).append(row)
    deck_rows = []
    for entry, rows in deck_groups.items():
        deck_rows.append({
            "exception_entry": entry,
            "cause_class": rows[0]["cause_class"],
            "event_count": len(rows),
            "event_ids": "|".join(row["event_id"] for row in rows),
            "record": rows[0]["record"],
            "visible_surface_or_phrase": " ".join(row["current_surface_parse"].split(":", 2)[1] for row in rows),
            "copy_rule_de": (
                "die ganze Dreikartenfolge okeey qol cheedy als eine lokale B1-Kadenz kopieren"
                if entry == "X01_B1_KEEY_OL_SHED_CADENCE"
                else rows[0]["working_explanation_de"] + "; lokale Form kopieren"
            ),
        })

    revised = []
    cause_by_event = {row["event_id"]: row for row in cause_rows}
    for row in compact:
        cause = cause_by_event.get(row["event_id"])
        if cause and cause["resolution_status"] == "RESOLVED_COMPACT_RULE":
            layer = "ADDITIONAL_COMPACT_RULE"
            exception_entry = "NONE"
        elif cause:
            layer = "SIXTEEN_ENTRY_LOCAL_EXCEPTION_DECK"
            exception_entry = cause["compact_exception_entry"]
        else:
            layer = row["surface_writer_layer"]
            exception_entry = "NONE"
        revised.append({
            **row,
            "revised_surface_writer_layer": layer,
            "compact_exception_entry": exception_entry,
            "revised_exact_roundtrip": row["exact_roundtrip"],
        })

    resolved_rows = [row for row in cause_rows if row["resolution_status"] == "RESOLVED_COMPACT_RULE"]
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_NINTH_21_EXCEPTION_CAUSES.tsv", cause_rows, list(cause_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_NINTH_16_MEMORIZED_SURFACE_ENTRIES.tsv", deck_rows, list(deck_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_NINTH_3_ADDITIONAL_RULE_RESOLUTIONS.tsv", resolved_rows, list(resolved_rows[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_NINTH_372_REVISED_SURFACE_WRITER.tsv", revised, list(revised[0]))

    md = [
        "# Restdeck der lokalen Schreiberformen",
        "",
        "## Drei zusaetzlich geschlossene Stellen",
        "",
        "- E022 und E233 sind die beiden vollstaendigen Y-AIIN-Y-Formeln. Der P-Tisch schreibt die Mittelkarte taiin, der S-Tisch daiin.",
        "- E352 ist ein q-Eintritt nach der unmittelbar vorhergehenden Schlusskarte.",
        "",
        "## Eine komprimierte Dreikartenformel",
        "",
        "B1-S016 schreibt lokal `okeey qol cheedy`. Das wird als eine einzige gelernte Kadenz statt als drei unabhaengige Sonderformen gelehrt.",
        "",
        "## Sechzehn zu merkende Eintraege",
        "",
    ]
    for row in deck_rows:
        md.append(f"- **{row['exception_entry']}** ({row['event_ids']}): `{row['visible_surface_or_phrase']}` — {row['copy_rule_de']}.")
    md.extend([
        "",
        "Handwechsel erklaert keine der 21 Ausgangsstellen: die Ausnahmen liegen innerhalb ihrer normalen Seitenhand. Neun stehen am Feldanfang oder als Einzelfeld; diese Position hilft bei der Beschreibung, bestimmt aber ausser E352 die konkrete Huelle nicht eindeutig.",
    ])
    (HERE / "SIX_HUNDRED_TWENTY_NINTH_LOCAL_EXCEPTION_CARD.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    statuses = Counter(row["resolution_status"] for row in cause_rows)
    revised_layers = Counter(row["revised_surface_writer_layer"] for row in revised)
    summary = {
        "status": "PASS",
        "guard_stats": guard_stats,
        "input_exceptions": len(cause_rows),
        "additional_rule_resolutions": statuses["RESOLVED_COMPACT_RULE"],
        "grouped_phrase_events": statuses["GROUPED_PHRASE"],
        "keep_local_events": statuses["KEEP_LOCAL"],
        "memorized_entries": len(deck_rows),
        "memorized_events": sum(int(row["event_count"]) for row in deck_rows),
        "field_entry_or_only_events": sum(row["field_position"] in {"FIRST", "ONLY"} for row in cause_rows),
        "post_close_field_entries": sum(row["post_close_field_entry"] == "YES" for row in cause_rows),
        "hand_change_explanations": 0,
        "revised_writer_layers": revised_layers,
        "exact_roundtrips": sum(row["revised_exact_roundtrip"] == "YES" for row in revised),
        "decision": "THREE_MORE_EVENTS_RULE_RESOLVED__EIGHTEEN_EVENTS_COMPRESSED_TO_SIXTEEN_LOCAL_ENTRIES",
    }
    (HERE / "SIX_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
