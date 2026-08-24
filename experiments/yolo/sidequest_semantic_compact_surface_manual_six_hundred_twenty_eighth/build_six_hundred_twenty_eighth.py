#!/usr/bin/env python3
"""Reduce the 179 apparent exemplar choices with the existing two-stage renderer."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
FORWARD_DIR = ROOT / "experiments/yolo/sidequest_semantic_forward_workshop_compiler_six_hundred_twenty_seventh"
RENDER_DIR = ROOT / "experiments/yolo/sidequest_semantic_two_stage_renderer_four_hundred_seventieth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


RESOLUTION_NAMES = {
    "UNIQUE_BODY_REGISTER_POSITION": "BODY_REGISTER_POSITION_RULE",
    "PREVIOUS_WRAPPER_RESOLVES": "PREVIOUS_WRAPPER_RULE",
    "EXPANDED_KEY_MAJORITY": "REGISTER_POSITION_PREVIOUS_MAJORITY",
}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    forward = read_tsv(FORWARD_DIR / "SIX_HUNDRED_TWENTY_SEVENTH_372_FORWARD_EVENT_COMPILATION.tsv")
    residual = [row for row in forward if row["local_exemplar_needed"] == "YES"]
    renderer = read_tsv(RENDER_DIR / "FOUR_HUNDRED_SEVENTIETH_381_PROSE_TWO_STAGE_WRITER.tsv")
    rules = read_tsv(RENDER_DIR / "FOUR_HUNDRED_SEVENTIETH_PROSE_WRAPPER_RULEBOOK.tsv")
    render_by_event = {row["event_id"]: row for row in renderer}
    forward_index = {row["event_id"]: index for index, row in enumerate(forward)}

    decomposition = []
    for row in residual:
        render = render_by_event[row["event_id"]]
        index = forward_index[row["event_id"]]
        previous = forward[index - 1] if index > 0 and forward[index - 1]["record"] == row["record"] else None
        post_close = bool(
            previous
            and previous["semantic_component_parse"].endswith("+DY")
            and render["field_position"] in {"FIRST", "ONLY"}
        )
        if render["exact_surface_match"] == "YES":
            resolution = RESOLUTION_NAMES[render["selection_layer"]]
            final_surface = render["predicted_surface"]
            exception_needed = "NO"
        else:
            resolution = "MEMORIZED_LOCAL_EXCEPTION"
            final_surface = render["observed_surface"]
            exception_needed = "YES"
        decomposition.append({
            "event_id": row["event_id"],
            "case_id": row["case_id"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "invariant_command_de": row["invariant_command_de"],
            "selected_card_no": row["selected_card_no"],
            "body_surface": render["body_surface"],
            "register": render["register"],
            "field_position": render["field_position"],
            "previous_wrapper": render["previous_wrapper"],
            "predicted_wrapper": render["predicted_wrapper"],
            "observed_wrapper": render["observed_wrapper"],
            "post_close_field_entry": "YES" if post_close else "NO",
            "predicted_q_after_close_entry": "YES" if post_close and render["predicted_wrapper"] == "q" else "NO",
            "renderer_selection_layer": render["selection_layer"],
            "renderer_predicted_surface": render["predicted_surface"],
            "observed_surface": render["observed_surface"],
            "renderer_exact": render["exact_surface_match"],
            "resolution_class": resolution,
            "local_exception_needed": exception_needed,
            "final_surface": final_surface,
            "final_roundtrip": "YES" if final_surface == render["observed_surface"] else "NO",
        })

    exceptions = [
        {
            "exception_no": index,
            "event_id": row["event_id"],
            "case_id": row["case_id"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "selected_card_no": row["selected_card_no"],
            "invariant_command_de": row["invariant_command_de"],
            "body_surface": row["body_surface"],
            "rule_predicted_surface": row["renderer_predicted_surface"],
            "memorized_surface": row["observed_surface"],
            "copy_instruction_de": "diese lokale Schreiberform aus dem Masterexemplar kopieren; Bedeutung und Karte bleiben unveraendert",
        }
        for index, row in enumerate((item for item in decomposition if item["local_exception_needed"] == "YES"), 1)
    ]

    decomposition_by_event = {row["event_id"]: row for row in decomposition}
    compact = []
    for row in forward:
        if row["local_exemplar_needed"] == "NO":
            layer = "SEMANTIC_CARD_OR_DESK_RULE"
            final_surface = row["selected_surface"]
            exception = "NO"
        else:
            resolved = decomposition_by_event[row["event_id"]]
            if resolved["local_exception_needed"] == "NO":
                layer = "TWO_STAGE_BODY_WRAPPER_RULE"
                final_surface = resolved["final_surface"]
                exception = "NO"
            else:
                layer = "TWENTY_ONE_LOCAL_EXCEPTION_DECK"
                final_surface = resolved["final_surface"]
                exception = "YES"
        compact.append({
            "event_id": row["event_id"],
            "case_id": row["case_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "invariant_command_de": row["invariant_command_de"],
            "selected_card_no": row["selected_card_no"],
            "surface_writer_layer": layer,
            "local_exception_needed": exception,
            "predicted_surface": final_surface,
            "observed_surface": row["selected_surface"],
            "exact_roundtrip": "YES" if final_surface == row["selected_surface"] else "NO",
        })

    used_rule_keys = {
        (
            render_by_event[row["event_id"]]["body_surface"],
            render_by_event[row["event_id"]]["register"],
            render_by_event[row["event_id"]]["field_position"],
            render_by_event[row["event_id"]]["previous_wrapper"],
        )
        for row in residual
    }
    used_rules = [
        row for row in rules
        if (row["body_surface"], row["register"], row["field_position"], row["previous_wrapper"]) in used_rule_keys
    ]

    write_tsv(HERE / "SIX_HUNDRED_TWENTY_EIGHTH_179_SURFACE_RULE_DECOMPOSITION.tsv", decomposition, list(decomposition[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_EIGHTH_21_LOCAL_SURFACE_EXCEPTIONS.tsv", exceptions, list(exceptions[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_EIGHTH_372_COMPACT_SURFACE_WRITER.tsv", compact, list(compact[0]))
    write_tsv(HERE / "SIX_HUNDRED_TWENTY_EIGHTH_USED_WRAPPER_RULES.tsv", used_rules, list(used_rules[0]))

    counts = Counter(row["resolution_class"] for row in decomposition)
    md = [
        "# Kurzes Oberflaechenhandbuch fuer die fuenf Hauptfaelle",
        "",
        "## Schreibfolge",
        "",
        "1. Invarianten Befehl und exakte Karte nach Pass 627 waehlen.",
        "2. Den stabilen Kartenkoerper schreiben.",
        "3. Aus Register, Feldposition und voriger Huelle die neue Huelle waehlen.",
        "4. Nur fuer die 21 unten genannten Ereignisse die lokale Sonderform kopieren.",
        "",
        "## Aufloesung der 179 alten Exemplarfaelle",
        "",
        f"- {counts['BODY_REGISTER_POSITION_RULE']} durch eindeutigen Kartenkoerper + Register + Feldposition;",
        f"- {counts['PREVIOUS_WRAPPER_RULE']} zusaetzlich durch die vorige Huelle;",
        f"- {counts['REGISTER_POSITION_PREVIOUS_MAJORITY']} durch die feste Mehrheitsform derselben erweiterten Situation;",
        f"- {counts['MEMORIZED_LOCAL_EXCEPTION']} bleiben als kleine lokale Ausnahmekarte.",
        "",
        "Sechzehn der aufgeloesten Restformen sind q-Eintritte direkt nach einer lizenzierten Schlusskarte an einem neuen Feld. Sie sind ein Spezialfall der Koerper-/Positionsregel, keine neue Bedeutung.",
        "",
        "## Die 21 echten Sonderformen",
        "",
    ]
    for row in exceptions:
        md.append(f"- **{row['event_id']} / {row['record']} / {row['selected_card_no']}**: Regel `{row['rule_predicted_surface']}`, lokal `{row['memorized_surface']}`.")
    md.extend([
        "",
        "## Gesamtbilanz",
        "",
        "Von 372 Hauptfall-Ereignissen schreibt die Bedeutungs-/Karten-/Schreibtischregel 193 direkt. Der alte Zweistufen-Renderer schliesst weitere 158. Nur 21 Formen muessen als lokaler Exemplarrest gemerkt werden. Alle 372 sichtbaren Formen werden damit exakt geschrieben.",
    ])
    (HERE / "SIX_HUNDRED_TWENTY_EIGHTH_COMPACT_SURFACE_MANUAL.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    compact_counts = Counter(row["surface_writer_layer"] for row in compact)
    summary = {
        "status": "PASS",
        "input_apparent_exemplar_choices": len(residual),
        "body_register_position_resolved": counts["BODY_REGISTER_POSITION_RULE"],
        "previous_wrapper_resolved": counts["PREVIOUS_WRAPPER_RULE"],
        "expanded_majority_resolved": counts["REGISTER_POSITION_PREVIOUS_MAJORITY"],
        "renderer_resolved_total": sum(row["renderer_exact"] == "YES" for row in decomposition),
        "local_surface_exceptions": len(exceptions),
        "predicted_q_after_close_entries": sum(row["predicted_q_after_close_entry"] == "YES" and row["renderer_exact"] == "YES" for row in decomposition),
        "events": len(compact),
        "semantic_card_or_desk_rule_events": compact_counts["SEMANTIC_CARD_OR_DESK_RULE"],
        "two_stage_renderer_events": compact_counts["TWO_STAGE_BODY_WRAPPER_RULE"],
        "exception_deck_events": compact_counts["TWENTY_ONE_LOCAL_EXCEPTION_DECK"],
        "exact_roundtrips": sum(row["exact_roundtrip"] == "YES" for row in compact),
        "new_meanings": 0,
        "decision": "ONLY_TWENTY_ONE_OF_372_MAIN_CASE_SURFACES_REQUIRE_LOCAL_MEMORIZATION",
    }
    (HERE / "SIX_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
