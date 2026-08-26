#!/usr/bin/env python3
"""Compile literal left/right scope readings for all 28 local OL occurrences."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt477_ol_directional_scope_phrasebook"
OUT = BASE / "artifacts"
G460 = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
EDGES = G460 / "gdt460_27_calibrated_edge_stems.tsv"
EVENTS = G474 / "gdt474_183_event_meaning_triptych.tsv"
OCCURRENCES = G475 / "gdt475_69_order_occurrence_positions.tsv"
BOUNDARIES = G475 / "gdt475_146_bundle_boundary_roles.tsv"
DECISIONS = G476 / "gdt476_64_tie_context_decisions.tsv"

SCOPE_OUT = OUT / "gdt477_28_ol_directional_scope_occurrences.tsv"
EVENT_OUT = OUT / "gdt477_26_ol_event_scope_editions.tsv"
RULE_OUT = OUT / "gdt477_3_directional_scope_rules.tsv"
PAGE_OUT = OUT / "gdt477_5_page_scope_summary.tsv"
READABLE_OUT = OUT / "GDT477_OL_DIRECTIONAL_SCOPE_PHRASEBOOK.md"
RESULT_OUT = OUT / "gdt477_result.json"

NAME_RE = re.compile(r"^\[([A-ZÄÖÜ_]+NAME):(.+)\]$")
TOKEN_LABELS = {
    "AUSFÜHRUNG": "Ausführung",
    "HIER": "bezeichnete Stelle",
    "SETZEN": "Setzen",
    "AUSGANG": "Ausgang",
    "HALTEN": "Halten",
    "DANACH": "Folgeschritt",
    "ZIELORT": "Zielort",
    "WERT": "Wert",
    "BAHN": "Bahn",
    "POSTEN": "Posten",
}
NAME_CLASS_LABELS = {
    "STERNSTELLENNAME": "Sternstelle",
    "DROGENNAME": "Droge",
    "BADSTATIONSNAME": "Badstation",
    "PFLANZENNAME": "Pflanze",
}
ORIENTATION_ORDER = ("FORWARD_OPEN", "BRIDGE_LEFT_TO_RIGHT", "BACKWARD_HOLD")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def token_type(token: str) -> str:
    if token == "NONE":
        return "BOUNDARY"
    if NAME_RE.match(token):
        return "LEARNED_NAME"
    if token in {"NEHMEN", "HALTEN", "GEBEN", "WÄHLEN", "BEARBEITEN", "EINSTELLEN", "MARKIEREN", "SETZEN", "EINSETZEN"}:
        return "ACTION"
    return "FUNCTION"


def token_label(token: str) -> str:
    match = NAME_RE.match(token)
    if match:
        name_class, surface = match.groups()
        return f"{NAME_CLASS_LABELS.get(name_class, 'Name')} »{surface}«"
    return TOKEN_LABELS.get(token, token.lower())


def orientation(tokens: list[str], index: int) -> str:
    if index == 0:
        return "FORWARD_OPEN"
    if index == len(tokens) - 1:
        return "BACKWARD_HOLD"
    return "BRIDGE_LEFT_TO_RIGHT"


def name_position(tokens: list[str], index: int) -> str:
    names = [offset for offset, token in enumerate(tokens) if NAME_RE.match(token)]
    if not names:
        return "NAME_FREE"
    if index < min(names):
        return "PRE_NAME"
    if index > max(names):
        return "POST_NAME"
    return "BETWEEN_NAMES"


def scope_formula(scope: str) -> str:
    return {
        "FORWARD_OPEN": "OL · X = weiter mit X",
        "BRIDGE_LEFT_TO_RIGHT": "X · OL · Y = X in Y weiterführen",
        "BACKWARD_HOLD": "X · OL = X weiterführen",
    }[scope]


def scope_phrase(scope: str, left: str, right: str) -> str:
    if scope == "FORWARD_OPEN":
        return "im aktiven Eintrag weiter" if right == "NONE" else f"weiter mit {token_label(right)}"
    if scope == "BACKWARD_HOLD":
        return f"{token_label(left)} weiterführen"
    return f"{token_label(left)} in {token_label(right)} weiterführen"


def marked_literal(tokens: list[str], selected_index: int) -> str:
    return " · ".join("⟦FORTSETZEN⟧" if index == selected_index else token for index, token in enumerate(tokens))


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_readable(
    scope_rows: list[dict[str, object]],
    event_rows: list[dict[str, object]],
    rule_rows: list[dict[str, object]],
    page_rows: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in scope_rows:
        by_page[str(row["physical_page"])].append(row)
    page_map = {str(row["physical_page"]): row for row in page_rows}
    lines = [
        "# GDT477 — OL-Richtungssprachführer",
        "",
        "`OL=FORTSETZEN` braucht keine zweite Wortbedeutung. Seine Stellung in der vollständigen Funktion/Namens-Spur bestimmt, wohin die Fortsetzung greift: nach rechts, von links nach rechts oder zurück auf den linken Träger.",
        "",
        "| Stellung | Formel | Vorkommen | Ereignisse | konkrete Default-Lesung |",
        "|---|---|---:|---:|---|",
    ]
    for row in rule_rows:
        lines.append(
            f"| {row['scope_orientation']} | `{markdown_escape(row['scope_formula_de'])}` | {row['occurrence_count']} | {row['event_count']} | {row['default_scope_reading_de']} |"
        )
    lines.extend([
        "",
        "Die Teilung ist vollständig: alle neun vorangestellten OL eröffnen eine Funktionskette; alle sechzehn karteninternen OL sind entweder Brücke (8) oder Rückhalt (8). Die elf recordbindenden OL dürfen trotzdem alle drei Richtungen tragen: acht öffnen nach rechts, zwei stehen als Brücke und eines hält einen links stehenden Namen weiter aktiv.",
        "",
        f"Die ältere Kanalkalibrierung passt dazu: freies linkes `ol-` trifft {result['running_edge_support']['PREFIX_OL']['matching_types']}/{result['running_edge_support']['PREFIX_OL']['extension_types']} Erweiterungstypen auf {result['running_edge_support']['PREFIX_OL']['pages']} Seiten; rechtes `-ol` trifft {result['running_edge_support']['SUFFIX_OL']['matching_types']}/{result['running_edge_support']['SUFFIX_OL']['extension_types']} auf {result['running_edge_support']['SUFFIX_OL']['pages']} Seiten. Beide Richtungen sind alte Karten, keine Notkorrekturen.",
        "",
        "## Alle 28 OL-Stellen",
        "",
    ])
    for page, rows in by_page.items():
        summary = page_map[page]
        lines.extend([
            f"### {page}",
            "",
            f"{summary['occurrence_count']} OL-Stellen in {summary['event_count']} Ereignissen: {summary['forward_open_count']} öffnend, {summary['bridge_count']} Brücken, {summary['backward_hold_count']} rückhaltend.",
            "",
            "| Form · Locus | markierte Literalfolge | Stellung | OL-Scope | aktive Ereignislesung |",
            "|---|---|---|---|---|",
        ])
        for row in rows:
            lines.append(
                f"| `{row['surface']}` · {row['locus']} | {markdown_escape(row['marked_literal_working_reading_de'])} | {row['scope_orientation']} / {row['name_relative_position']} | {markdown_escape(row['directional_scope_phrase_de'])} | {markdown_escape(row['context_selected_event_reading_de'])} |"
            )
        lines.append("")
    lines.extend([
        "## Ereignisebene",
        "",
        f"Die 28 Stellen gehören zu {len(event_rows)} Ereignissen. Zwei Formen (`ykolairol`, `otolarol`) enthalten je zwei OL-Slots; ihre beiden Richtungslesungen bleiben getrennt und werden nicht zu einem angeblich komplexen Einzelwort zusammengeschoben.",
    ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS)
    occurrences = read_tsv(OCCURRENCES)
    boundaries = read_tsv(BOUNDARIES)
    decisions = read_tsv(DECISIONS)
    edges = read_tsv(EDGES)
    if len(events) != 183 or len(occurrences) != 69 or len(boundaries) != 146 or len(decisions) != 64 or len(edges) != 27:
        raise RuntimeError("GDT460/GDT474/GDT475/GDT476 input drift")

    event_map = {row["source_event_id"]: row for row in events}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    decision_map = {row["bundle_id"]: row for row in decisions}
    ol_source = [row for row in occurrences if row["root"] == "OL"]
    if len(ol_source) != 28:
        raise RuntimeError("OL occurrence count drift")

    occurrence_seen: Counter[str] = Counter()
    scope_rows: list[dict[str, object]] = []
    for ordinal, source in enumerate(ol_source, start=1):
        event = event_map[source["source_event_id"]]
        occurrence_seen[source["source_event_id"]] += 1
        ol_ordinal = occurrence_seen[source["source_event_id"]]
        tokens = event["literal_working_reading_de"].split(" · ")
        ol_indices = [index for index, token in enumerate(tokens) if token == "FORTSETZEN"]
        if len(ol_indices) != sum(atom == "OL" for atom in event["working_recipe"].split("+")):
            raise RuntimeError(f"Literal/recipe OL count drift in {source['source_event_id']}")
        index = ol_indices[ol_ordinal - 1]
        left = tokens[index - 1] if index else "NONE"
        right = tokens[index + 1] if index + 1 < len(tokens) else "NONE"
        scope = orientation(tokens, index)
        name_place = name_position(tokens, index)
        decision = decision_map.get(source["bundle_id"])
        model = decision["context_selected_model"] if decision else event["bundle_selected_model"]
        model_source = "GDT476_CONTEXT" if decision and decision["context_decided"] == "YES" else "GDT474_SELECTED_DEFAULT"
        boundary = boundary_map[source["bundle_id"]]
        scope_rows.append({
            "scope_id": f"G477-O{ordinal:03d}",
            "order_occurrence_id": source["order_occurrence_id"],
            "source_event_id": source["source_event_id"],
            "bundle_id": source["bundle_id"],
            "record_id": source["record_id"],
            "physical_page": source["physical_page"],
            "register": event["register"],
            "locus": source["locus"],
            "surface": source["surface"],
            "working_recipe": source["working_recipe"],
            "literal_working_reading_de": event["literal_working_reading_de"],
            "marked_literal_working_reading_de": marked_literal(tokens, index),
            "ol_ordinal_in_event": ol_ordinal,
            "ol_literal_token_ordinal": index + 1,
            "literal_token_count": len(tokens),
            "left_token": left,
            "left_token_type": token_type(left),
            "right_token": right,
            "right_token_type": token_type(right),
            "name_relative_position": name_place,
            "scope_orientation": scope,
            "scope_formula_de": scope_formula(scope),
            "directional_scope_phrase_de": scope_phrase(scope, left, right),
            "gdt475_position_role": source["position_role"],
            "gdt475_stream_interpretation": source["stream_interpretation"],
            "boundary_role": boundary["boundary_role"],
            "context_selected_model": model,
            "model_source": model_source,
            "context_selected_event_reading_de": event[f"{model.lower()}_event_reading_de"],
            "root_meaning_change": "NO",
            "learned_name_change": "NO",
            "claim_status": "POSITIONAL_SCOPE_RECAST__OL_MEANING_UNCHANGED",
        })

    events_by_id: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in scope_rows:
        events_by_id[str(row["source_event_id"])].append(row)
    event_rows: list[dict[str, object]] = []
    for event in events:
        rows = events_by_id.get(event["source_event_id"])
        if not rows:
            continue
        event_rows.append({
            "scope_event_id": f"G477-E{len(event_rows) + 1:03d}",
            "source_event_id": event["source_event_id"],
            "bundle_id": event["bundle_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "locus": event["locus"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "literal_working_reading_de": event["literal_working_reading_de"],
            "ol_occurrence_count": len(rows),
            "scope_orientation_sequence": "|".join(str(row["scope_orientation"]) for row in rows),
            "name_position_sequence": "|".join(str(row["name_relative_position"]) for row in rows),
            "directional_scope_phrase_sequence_de": " | ".join(str(row["directional_scope_phrase_de"]) for row in rows),
            "context_selected_model": rows[0]["context_selected_model"],
            "context_selected_event_reading_de": rows[0]["context_selected_event_reading_de"],
            "direction_refined_event_reading_de": f"{rows[0]['context_selected_event_reading_de']} OL-Scope: " + "; ".join(str(row["directional_scope_phrase_de"]) for row in rows) + ".",
            "root_meaning_change": "NO",
            "learned_name_change": "NO",
        })

    edge_map = {(row["edge"], row["surface_stem"]): row for row in edges}
    prefix = edge_map[("PREFIX", "ol")]
    suffix = edge_map[("SUFFIX", "ol")]
    rule_rows: list[dict[str, object]] = []
    for rule_id, scope in enumerate(ORIENTATION_ORDER, start=1):
        rows = [row for row in scope_rows if row["scope_orientation"] == scope]
        position_counts = Counter(str(row["gdt475_position_role"]) for row in rows)
        name_counts = Counter(str(row["name_relative_position"]) for row in rows)
        rule_rows.append({
            "scope_rule_id": f"G477-R{rule_id}",
            "scope_orientation": scope,
            "literal_shape": {"FORWARD_OPEN": "OL|X", "BRIDGE_LEFT_TO_RIGHT": "X|OL|Y", "BACKWARD_HOLD": "X|OL"}[scope],
            "scope_formula_de": scope_formula(scope),
            "default_scope_reading_de": {"FORWARD_OPEN": "weiter mit dem rechten Träger", "BRIDGE_LEFT_TO_RIGHT": "den linken Träger in den rechten weiterführen", "BACKWARD_HOLD": "den linken Träger weiterführen"}[scope],
            "occurrence_count": len(rows),
            "event_count": len({row["source_event_id"] for row in rows}),
            "gdt475_position_role_counts": "|".join(f"{key}:{position_counts[key]}" for key in sorted(position_counts)),
            "name_position_counts": "|".join(f"{key}:{name_counts[key]}" for key in sorted(name_counts)),
            "running_edge_evidence": (
                f"PREFIX_ol:{prefix['running_matching_type_count']}/{prefix['running_extension_type_count']}:{prefix['running_matching_event_count']}events:{len(prefix['running_matching_pages'].split('|'))}pages"
                if scope == "FORWARD_OPEN"
                else f"SUFFIX_ol:{suffix['running_matching_type_count']}/{suffix['running_extension_type_count']}:{suffix['running_matching_event_count']}events:{len(suffix['running_matching_pages'].split('|'))}pages"
                if scope == "BACKWARD_HOLD"
                else "PREFIX_AND_SUFFIX_OL_CHANNELS_COMPOSE"
            ),
            "working_root_meaning_de": "FORTSETZEN",
            "new_root_meaning": "NO",
        })

    page_rows: list[dict[str, object]] = []
    rows_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in scope_rows:
        rows_by_page[str(row["physical_page"])].append(row)
    for page, rows in rows_by_page.items():
        scopes = Counter(str(row["scope_orientation"]) for row in rows)
        page_rows.append({
            "physical_page": page,
            "register": rows[0]["register"],
            "occurrence_count": len(rows),
            "event_count": len({row["source_event_id"] for row in rows}),
            "forward_open_count": scopes["FORWARD_OPEN"],
            "bridge_count": scopes["BRIDGE_LEFT_TO_RIGHT"],
            "backward_hold_count": scopes["BACKWARD_HOLD"],
            "cross_locus_record_binding_count": sum(row["gdt475_position_role"] == "BUNDLE_LEADING" for row in rows),
            "event_internal_count": sum(row["gdt475_position_role"] == "EVENT_INTERNAL" for row in rows),
            "all_occurrences_have_directional_default": "YES",
        })

    scope_counts = Counter(str(row["scope_orientation"]) for row in scope_rows)
    name_counts = Counter(str(row["name_relative_position"]) for row in scope_rows)
    position_cross = Counter((str(row["scope_orientation"]), str(row["gdt475_position_role"])) for row in scope_rows)
    result: dict[str, object] = {
        "status": "OL_HAS_THREE_POSITIONAL_SCOPE_REALIZATIONS__ONE_ROOT_MEANING",
        "ol_occurrence_count": len(scope_rows),
        "ol_event_count": len(event_rows),
        "scope_orientation_counts": dict(scope_counts),
        "name_relative_position_counts": dict(name_counts),
        "forward_open_event_opening_count": sum(row["scope_orientation"] == "FORWARD_OPEN" and row["gdt475_position_role"] in {"BUNDLE_LEADING", "LATER_EVENT_LEADING"} for row in scope_rows),
        "forward_open_event_internal_count": position_cross[("FORWARD_OPEN", "EVENT_INTERNAL")],
        "event_internal_bridge_count": position_cross[("BRIDGE_LEFT_TO_RIGHT", "EVENT_INTERNAL")],
        "event_internal_backward_count": position_cross[("BACKWARD_HOLD", "EVENT_INTERNAL")],
        "cross_locus_orientation_counts": dict(Counter(str(row["scope_orientation"]) for row in scope_rows if row["gdt475_position_role"] == "BUNDLE_LEADING")),
        "running_edge_support": {
            "PREFIX_OL": {
                "extension_types": int(prefix["running_extension_type_count"]),
                "matching_types": int(prefix["running_matching_type_count"]),
                "precision": float(prefix["running_type_precision"]),
                "events": int(prefix["running_matching_event_count"]),
                "pages": len(prefix["running_matching_pages"].split("|")),
            },
            "SUFFIX_OL": {
                "extension_types": int(suffix["running_extension_type_count"]),
                "matching_types": int(suffix["running_matching_type_count"]),
                "precision": float(suffix["running_type_precision"]),
                "events": int(suffix["running_matching_event_count"]),
                "pages": len(suffix["running_matching_pages"].split("|")),
            },
        },
        "all_occurrences_have_directional_default_count": len(scope_rows),
        "page_count": len(page_rows),
        "component_meaning_change_count": 0,
        "learned_name_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "selected_model_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Directional German scope rendering of the unchanged OL=FORTSETZEN root in 28 admitted local occurrences; no plaintext, confirmed syntax, lexeme, object identity, new component meaning, name, surface, recipe, model, event, or page.",
    }

    write_tsv(SCOPE_OUT, scope_rows)
    write_tsv(EVENT_OUT, event_rows)
    write_tsv(RULE_OUT, rule_rows)
    write_tsv(PAGE_OUT, page_rows)
    READABLE_OUT.write_text(build_readable(scope_rows, event_rows, rule_rows, page_rows, result), encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "occurrences": len(scope_rows), "events": len(event_rows), "orientations": dict(scope_counts)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
