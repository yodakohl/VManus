#!/usr/bin/env python3
"""Audit OT direction and compile the complete paired OT/OL order grammar."""

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
BASE = ROOT / "experiments/yolo/gdt478_paired_ot_ol_order_grammar"
OUT = BASE / "artifacts"
G460 = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts"
G461 = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts"
G474 = ROOT / "experiments/yolo/gdt474_locus_bundle_meaning_triptych/artifacts"
G475 = ROOT / "experiments/yolo/gdt475_ot_ol_page_microrecord_itineraries/artifacts"
G476 = ROOT / "experiments/yolo/gdt476_boundary_context_tie_resolution/artifacts"
G477 = ROOT / "experiments/yolo/gdt477_ol_directional_scope_phrasebook/artifacts"
EDGES = G460 / "gdt460_27_calibrated_edge_stems.tsv"
INTERNALS = G461 / "gdt461_9_calibrated_internal_stems.tsv"
EVENTS = G474 / "gdt474_183_event_meaning_triptych.tsv"
ORDER = G475 / "gdt475_69_order_occurrence_positions.tsv"
BOUNDARIES = G475 / "gdt475_146_bundle_boundary_roles.tsv"
DECISIONS = G476 / "gdt476_64_tie_context_decisions.tsv"
OL_SCOPE = G477 / "gdt477_28_ol_directional_scope_occurrences.tsv"
OL_RULES = G477 / "gdt477_3_directional_scope_rules.tsv"

PAIRED_OUT = OUT / "gdt478_69_paired_order_scope_occurrences.tsv"
EVENT_OUT = OUT / "gdt478_60_paired_order_event_editions.tsv"
RULE_OUT = OUT / "gdt478_5_paired_order_scope_rules.tsv"
JOINT_OUT = OUT / "gdt478_7_ot_ol_joint_events.tsv"
PAGE_OUT = OUT / "gdt478_6_page_order_summary.tsv"
READABLE_OUT = OUT / "GDT478_PAIRED_OT_OL_ORDER_GRAMMAR.md"
RESULT_OUT = OUT / "gdt478_result.json"

NAME_RE = re.compile(r"^\[([A-ZÄÖÜ_]+NAME):(.+)\]$")
NAME_LABELS = {
    "PFLANZENNAME": "Pflanze",
    "STERNSTELLENNAME": "Sternstelle",
    "BADSTATIONSNAME": "Badstation",
    "DROGENNAME": "Droge",
}
TOKEN_LABELS = {
    "AUSFÜHRUNG": "Ausführung",
    "HIER": "bezeichnete Stelle",
    "AUSGANG": "Ausgang",
    "ZIELORT": "Zielort",
    "WERT": "Wert",
    "ANTEIL": "Anteil",
    "BAHN": "Bahn",
    "POSTEN": "Posten",
    "GRAD I": "Grad I",
    "GRAD II": "Grad II",
    "SCHLUSS": "Schluss",
    "FORTSETZEN": "Fortsetzung",
    "SETZEN": "Setzen",
    "BEARBEITEN": "Bearbeiten",
}


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
        return f"{NAME_LABELS.get(name_class, 'Name')} »{surface}«"
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


def marked_literal(tokens: list[str], index: int, token: str) -> str:
    return " · ".join(f"⟦{token}⟧" if offset == index else value for offset, value in enumerate(tokens))


def ot_formula(scope: str) -> str:
    if scope == "FORWARD_OPEN":
        return "OT · X = nächster Träger: X"
    if scope == "BRIDGE_LEFT_TO_RIGHT":
        return "X · OT · Y = nach X folgt Y"
    return "X · OT = UNBELEGT"


def ot_phrase(scope: str, left: str, right: str) -> str:
    if scope == "FORWARD_OPEN":
        return f"danach {token_label(right)}"
    if scope == "BRIDGE_LEFT_TO_RIGHT":
        return f"nach {token_label(left)} folgt {token_label(right)}"
    return f"nach {token_label(left)}"


def markdown_escape(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_readable(
    paired: list[dict[str, object]],
    rules: list[dict[str, object]],
    joint: list[dict[str, object]],
    pages: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    ot_rows = [row for row in paired if row["root"] == "OT"]
    ot_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in ot_rows:
        ot_by_page[str(row["physical_page"])].append(row)
    page_map = {str(row["physical_page"]): row for row in pages}
    lines = [
        "# GDT478 — gepaarte OT/OL-Reihenfolgegrammatik",
        "",
        "Die beiden Reihenfolgestämme sind jetzt als unterschiedliche Zustandsoperationen lesbar: `OT=DANACH` eröffnet den nächsten Träger; `OL=FORTSETZEN` hält den aktuellen Träger aktiv und führt ihn je nach Stellung weiter.",
        "",
        "| Stamm | Kernoperation | Richtungsformen | Slots |",
        "|---|---|---|---:|",
        f"| OT / DANACH | neuen Geschwisterträger beginnen | 40 vorwärts + 1 Namensbrücke + 0 rückwärts | {result['ot_occurrence_count']} |",
        f"| OL / FORTSETZEN | aktiven Träger beibehalten | 9 vorwärts + 10 Brücken + 9 rückwärts | {result['ol_occurrence_count']} |",
        "",
        "## Die fünf ausführbaren Stellungsregeln",
        "",
        "| Stamm | Stellung | Formel | Operation | Vorkommen |",
        "|---|---|---|---|---:|",
    ]
    for row in rules:
        lines.append(
            f"| {row['root']} | {row['scope_orientation']} | `{markdown_escape(row['scope_formula_de'])}` | {row['state_operation']} | {row['occurrence_count']} |"
        )
    lines.extend([
        "",
        "## Die sieben gemeinsamen OT+OL-Ereignisse",
        "",
        "In allen sieben steht OT vor OL: zuerst wird der neue Träger eröffnet, danach wird genau dieser Träger weitergeführt. Damit liest sich `otol` nicht als kompliziertes Ganzwort, sondern als zwei aufeinanderfolgende Steuerkarten.",
        "",
        "| Seite · Locus | Form | Wurzelfolge | Zustandsfolge | konkrete Reihenfolgelesung |",
        "|---|---|---|---|---|",
    ])
    for row in joint:
        lines.append(
            f"| {row['physical_page']} · {row['locus']} | `{row['surface']}` | {markdown_escape(row['order_root_sequence'])} | {markdown_escape(row['state_operation_sequence'])} | {markdown_escape(row['paired_scope_reading_de'])} |"
        )
    lines.extend(["", "## Alle 41 OT-Stellen", ""])
    for page, rows in ot_by_page.items():
        summary = page_map[page]
        lines.extend([
            f"### {page}",
            "",
            f"{summary['ot_occurrence_count']} OT-Stellen; {summary['ot_forward_count']} vorwärts und {summary['ot_bridge_count']} als Brücke.",
            "",
            "| Form · Locus | markierte Literalfolge | Nameposition | OT-Scope | aktive Ereignislesung |",
            "|---|---|---|---|---|",
        ])
        for row in rows:
            lines.append(
                f"| `{row['surface']}` · {row['locus']} | {markdown_escape(row['marked_literal_working_reading_de'])} | {row['name_relative_position']} | {markdown_escape(row['directional_scope_phrase_de'])} | {markdown_escape(row['context_selected_event_reading_de'])} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    edges = read_tsv(EDGES)
    internals = read_tsv(INTERNALS)
    events = read_tsv(EVENTS)
    order = read_tsv(ORDER)
    boundaries = read_tsv(BOUNDARIES)
    decisions = read_tsv(DECISIONS)
    ol_scope = read_tsv(OL_SCOPE)
    ol_rules = read_tsv(OL_RULES)
    if (len(edges), len(internals), len(events), len(order), len(boundaries), len(decisions), len(ol_scope), len(ol_rules)) != (27, 9, 183, 69, 146, 64, 28, 3):
        raise RuntimeError("GDT460/GDT461/GDT474-GDT477 input drift")

    event_map = {row["source_event_id"]: row for row in events}
    boundary_map = {row["bundle_id"]: row for row in boundaries}
    decision_map = {row["bundle_id"]: row for row in decisions}
    ol_map = {row["order_occurrence_id"]: row for row in ol_scope}
    root_seen: Counter[tuple[str, str]] = Counter()
    paired: list[dict[str, object]] = []

    for ordinal, source in enumerate(order, start=1):
        event = event_map[source["source_event_id"]]
        decision = decision_map.get(source["bundle_id"])
        model = decision["context_selected_model"] if decision else event["bundle_selected_model"]
        model_source = "GDT476_CONTEXT" if decision and decision["context_decided"] == "YES" else "GDT474_SELECTED_DEFAULT"
        if source["root"] == "OT":
            root_seen[(source["source_event_id"], "OT")] += 1
            root_ordinal = root_seen[(source["source_event_id"], "OT")]
            tokens = event["literal_working_reading_de"].split(" · ")
            indices = [index for index, token in enumerate(tokens) if token == "DANACH"]
            if len(indices) != sum(atom == "OT" for atom in event["working_recipe"].split("+")):
                raise RuntimeError(f"Literal/recipe OT count drift in {source['source_event_id']}")
            index = indices[root_ordinal - 1]
            left = tokens[index - 1] if index else "NONE"
            right = tokens[index + 1] if index + 1 < len(tokens) else "NONE"
            scope = orientation(tokens, index)
            row = {
                "paired_scope_id": f"G478-O{ordinal:03d}",
                "order_occurrence_id": source["order_occurrence_id"],
                "root": "OT",
                "working_meaning_de": "DANACH",
                "source_event_id": source["source_event_id"],
                "bundle_id": source["bundle_id"],
                "record_id": source["record_id"],
                "physical_page": source["physical_page"],
                "register": event["register"],
                "locus": source["locus"],
                "surface": source["surface"],
                "working_recipe": source["working_recipe"],
                "literal_working_reading_de": event["literal_working_reading_de"],
                "marked_literal_working_reading_de": marked_literal(tokens, index, "DANACH"),
                "root_ordinal_in_event": root_ordinal,
                "literal_token_ordinal": index + 1,
                "literal_token_count": len(tokens),
                "left_token": left,
                "left_token_type": token_type(left),
                "right_token": right,
                "right_token_type": token_type(right),
                "name_relative_position": name_position(tokens, index),
                "scope_orientation": scope,
                "scope_formula_de": ot_formula(scope),
                "directional_scope_phrase_de": ot_phrase(scope, left, right),
                "state_operation": "START_FRESH_SIBLING",
                "gdt475_position_role": source["position_role"],
                "gdt475_stream_interpretation": source["stream_interpretation"],
                "boundary_role": boundary_map[source["bundle_id"]]["boundary_role"],
                "context_selected_model": model,
                "model_source": model_source,
                "context_selected_event_reading_de": event[f"{model.lower()}_event_reading_de"],
                "root_meaning_change": "NO",
                "learned_name_change": "NO",
                "claim_status": "PAIRED_ORDER_SCOPE_DEFAULT__ROOT_MEANINGS_UNCHANGED",
            }
        else:
            old = ol_map[source["order_occurrence_id"]]
            row = {
                "paired_scope_id": f"G478-O{ordinal:03d}",
                "order_occurrence_id": source["order_occurrence_id"],
                "root": "OL",
                "working_meaning_de": "FORTSETZEN",
                "source_event_id": source["source_event_id"],
                "bundle_id": source["bundle_id"],
                "record_id": source["record_id"],
                "physical_page": source["physical_page"],
                "register": old["register"],
                "locus": source["locus"],
                "surface": source["surface"],
                "working_recipe": source["working_recipe"],
                "literal_working_reading_de": old["literal_working_reading_de"],
                "marked_literal_working_reading_de": old["marked_literal_working_reading_de"],
                "root_ordinal_in_event": old["ol_ordinal_in_event"],
                "literal_token_ordinal": old["ol_literal_token_ordinal"],
                "literal_token_count": old["literal_token_count"],
                "left_token": old["left_token"],
                "left_token_type": old["left_token_type"],
                "right_token": old["right_token"],
                "right_token_type": old["right_token_type"],
                "name_relative_position": old["name_relative_position"],
                "scope_orientation": old["scope_orientation"],
                "scope_formula_de": old["scope_formula_de"],
                "directional_scope_phrase_de": old["directional_scope_phrase_de"],
                "state_operation": "KEEP_ACTIVE_UNIT",
                "gdt475_position_role": source["position_role"],
                "gdt475_stream_interpretation": source["stream_interpretation"],
                "boundary_role": old["boundary_role"],
                "context_selected_model": old["context_selected_model"],
                "model_source": old["model_source"],
                "context_selected_event_reading_de": old["context_selected_event_reading_de"],
                "root_meaning_change": "NO",
                "learned_name_change": "NO",
                "claim_status": "PAIRED_ORDER_SCOPE_DEFAULT__ROOT_MEANINGS_UNCHANGED",
            }
        paired.append(row)

    by_event: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in paired:
        by_event[str(row["source_event_id"])].append(row)
    event_rows: list[dict[str, object]] = []
    joint_rows: list[dict[str, object]] = []
    for event in events:
        rows = by_event.get(event["source_event_id"])
        if not rows:
            continue
        root_sequence = "|".join(str(row["root"]) for row in rows)
        operation_sequence = "|".join(str(row["state_operation"]) for row in rows)
        scope_reading = "; ".join(f"{row['root']}: {row['directional_scope_phrase_de']}" for row in rows)
        event_rows.append({
            "paired_event_id": f"G478-E{len(event_rows) + 1:03d}",
            "source_event_id": event["source_event_id"],
            "bundle_id": event["bundle_id"],
            "physical_page": event["physical_page"],
            "register": event["register"],
            "locus": event["locus"],
            "surface": event["surface"],
            "working_recipe": event["working_recipe"],
            "literal_working_reading_de": event["literal_working_reading_de"],
            "order_occurrence_count": len(rows),
            "order_root_sequence": root_sequence,
            "scope_orientation_sequence": "|".join(str(row["scope_orientation"]) for row in rows),
            "state_operation_sequence": operation_sequence,
            "paired_scope_reading_de": scope_reading,
            "context_selected_model": rows[0]["context_selected_model"],
            "context_selected_event_reading_de": rows[0]["context_selected_event_reading_de"],
            "paired_order_event_reading_de": f"{rows[0]['context_selected_event_reading_de']} Reihenfolge: {scope_reading}.",
            "root_meaning_change": "NO",
            "learned_name_change": "NO",
        })
        if {str(row["root"]) for row in rows} == {"OT", "OL"}:
            joint_rows.append({
                "joint_event_id": f"G478-J{len(joint_rows) + 1:02d}",
                "source_event_id": event["source_event_id"],
                "bundle_id": event["bundle_id"],
                "physical_page": event["physical_page"],
                "register": event["register"],
                "locus": event["locus"],
                "surface": event["surface"],
                "working_recipe": event["working_recipe"],
                "literal_working_reading_de": event["literal_working_reading_de"],
                "order_occurrence_count": len(rows),
                "order_root_sequence": root_sequence,
                "scope_orientation_sequence": "|".join(str(row["scope_orientation"]) for row in rows),
                "state_operation_sequence": operation_sequence,
                "ot_precedes_every_ol": "YES" if [row["root"] for row in rows][0] == "OT" and all(row["root"] == "OL" for row in rows[1:]) else "NO",
                "paired_scope_reading_de": scope_reading,
                "context_selected_model": rows[0]["context_selected_model"],
                "context_selected_event_reading_de": rows[0]["context_selected_event_reading_de"],
                "claim_status": "NEXT_UNIT_THEN_KEEP_ACTIVE__NO_COMPOUND_LEXEME_CLAIM",
            })

    edge_map = {(row["edge"], row["surface_stem"]): row for row in edges}
    internal_map = {row["surface_stem"]: row for row in internals}
    ot_prefix = edge_map[("PREFIX", "ot")]
    ot_internal = internal_map["ot"]
    rules: list[dict[str, object]] = []
    rule_specs = [
        ("OT", "FORWARD_OPEN", "START_FRESH_SIBLING", "OT · X = nächster Träger: X", "danach X", "PREFIX_ot"),
        ("OT", "BRIDGE_LEFT_TO_RIGHT", "START_FRESH_SIBLING", "X · OT · Y = nach X folgt Y", "nach X folgt Y", "INTERNAL_ot"),
        ("OL", "FORWARD_OPEN", "KEEP_ACTIVE_UNIT", "OL · X = weiter mit X", "weiter mit X", "PREFIX_ol"),
        ("OL", "BRIDGE_LEFT_TO_RIGHT", "KEEP_ACTIVE_UNIT", "X · OL · Y = X in Y weiterführen", "X in Y weiterführen", "PREFIX_SUFFIX_ol"),
        ("OL", "BACKWARD_HOLD", "KEEP_ACTIVE_UNIT", "X · OL = X weiterführen", "X weiterführen", "SUFFIX_ol"),
    ]
    for root, scope, operation, formula, phrase, evidence in rule_specs:
        rows = [row for row in paired if row["root"] == root and row["scope_orientation"] == scope]
        rules.append({
            "paired_rule_id": f"G478-R{len(rules) + 1}",
            "root": root,
            "working_meaning_de": "DANACH" if root == "OT" else "FORTSETZEN",
            "scope_orientation": scope,
            "scope_formula_de": formula,
            "default_scope_reading_de": phrase,
            "state_operation": operation,
            "occurrence_count": len(rows),
            "event_count": len({row["source_event_id"] for row in rows}),
            "name_position_counts": "|".join(f"{key}:{value}" for key, value in sorted(Counter(str(row["name_relative_position"]) for row in rows).items())),
            "position_role_counts": "|".join(f"{key}:{value}" for key, value in sorted(Counter(str(row["gdt475_position_role"]) for row in rows).items())),
            "right_successor_present_count": sum(row["right_token"] != "NONE" for row in rows),
            "running_channel_evidence": evidence,
            "new_root_meaning": "NO",
        })

    rows_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in paired:
        rows_by_page[str(row["physical_page"])].append(row)
    pages: list[dict[str, object]] = []
    for page, rows in rows_by_page.items():
        ot_rows = [row for row in rows if row["root"] == "OT"]
        ol_rows = [row for row in rows if row["root"] == "OL"]
        pages.append({
            "physical_page": page,
            "register": rows[0]["register"],
            "order_occurrence_count": len(rows),
            "order_event_count": len({row["source_event_id"] for row in rows}),
            "ot_occurrence_count": len(ot_rows),
            "ol_occurrence_count": len(ol_rows),
            "ot_forward_count": sum(row["scope_orientation"] == "FORWARD_OPEN" for row in ot_rows),
            "ot_bridge_count": sum(row["scope_orientation"] == "BRIDGE_LEFT_TO_RIGHT" for row in ot_rows),
            "ol_forward_count": sum(row["scope_orientation"] == "FORWARD_OPEN" for row in ol_rows),
            "ol_bridge_count": sum(row["scope_orientation"] == "BRIDGE_LEFT_TO_RIGHT" for row in ol_rows),
            "ol_backward_count": sum(row["scope_orientation"] == "BACKWARD_HOLD" for row in ol_rows),
            "joint_ot_ol_event_count": sum(row["physical_page"] == page for row in joint_rows),
            "all_order_slots_have_default": "YES",
        })

    ot_rows = [row for row in paired if row["root"] == "OT"]
    ol_rows = [row for row in paired if row["root"] == "OL"]
    result: dict[str, object] = {
        "status": "OT_STARTS_NEXT_UNIT__OL_KEEPS_CURRENT_UNIT__PAIRED_ORDER_GRAMMAR_COMPLETE",
        "order_occurrence_count": len(paired),
        "order_event_count": len(event_rows),
        "ot_occurrence_count": len(ot_rows),
        "ol_occurrence_count": len(ol_rows),
        "ot_scope_counts": dict(Counter(str(row["scope_orientation"]) for row in ot_rows)),
        "ol_scope_counts": dict(Counter(str(row["scope_orientation"]) for row in ol_rows)),
        "ot_name_position_counts": dict(Counter(str(row["name_relative_position"]) for row in ot_rows)),
        "ot_right_successor_count": sum(row["right_token"] != "NONE" for row in ot_rows),
        "ot_backward_hold_count": sum(row["scope_orientation"] == "BACKWARD_HOLD" for row in ot_rows),
        "state_operation_counts": dict(Counter(str(row["state_operation"]) for row in paired)),
        "joint_ot_ol_event_count": len(joint_rows),
        "joint_ot_precedes_ol_count": sum(row["ot_precedes_every_ol"] == "YES" for row in joint_rows),
        "joint_root_sequence_counts": dict(Counter(str(row["order_root_sequence"]) for row in joint_rows)),
        "running_ot_support": {
            "PREFIX_OT": {
                "extension_types": int(ot_prefix["running_extension_type_count"]),
                "matching_types": int(ot_prefix["running_matching_type_count"]),
                "precision": float(ot_prefix["running_type_precision"]),
                "events": int(ot_prefix["running_matching_event_count"]),
                "pages": len(ot_prefix["running_matching_pages"].split("|")),
            },
            "INTERNAL_OT": {
                "extension_types": int(ot_internal["running_internal_extension_type_count"]),
                "matching_types": int(ot_internal["running_matching_type_count"]),
                "precision": float(ot_internal["running_type_precision"]),
                "events": int(ot_internal["running_matching_event_count"]),
                "pages": len(ot_internal["running_matching_pages"].split("|")),
            },
        },
        "paired_rule_count": len(rules),
        "page_count": len(pages),
        "all_order_slots_have_default_count": len(paired),
        "component_meaning_change_count": 0,
        "learned_name_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "selected_model_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Paired directional working renderer for the unchanged OT=DANACH and OL=FORTSETZEN roots over 69 admitted local occurrences; no plaintext, confirmed syntax, lexeme, object identity, new component meaning, name, surface, recipe, model, event, or page.",
    }

    write_tsv(PAIRED_OUT, paired)
    write_tsv(EVENT_OUT, event_rows)
    write_tsv(RULE_OUT, rules)
    write_tsv(JOINT_OUT, joint_rows)
    write_tsv(PAGE_OUT, pages)
    READABLE_OUT.write_text(build_readable(paired, rules, joint_rows, pages, result), encoding="utf-8")
    RESULT_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "occurrences": len(paired), "events": len(event_rows), "joint": len(joint_rows), "ot_scopes": result["ot_scope_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
