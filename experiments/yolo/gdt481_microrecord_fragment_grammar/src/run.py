#!/usr/bin/env python3
"""Mine recurrent one-event and adjacent-event fragments inside GDT479 records."""

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
BASE = ROOT / "experiments/yolo/gdt481_microrecord_fragment_grammar"
OUT = BASE / "artifacts"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
G480 = ROOT / "experiments/yolo/gdt480_microrecord_template_atlas/artifacts"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
BUNDLES_IN = G479 / "gdt479_146_definitive_local_bundles.tsv"
RECORDS_IN = G479 / "gdt479_135_definitive_microrecords.tsv"
G480_ASSIGNMENTS = G480 / "gdt480_135_record_template_assignments.tsv"
EVENT_ASSIGNMENTS = OUT / "gdt481_183_event_fragment_assignments.tsv"
EVENT_STRICT = OUT / "gdt481_event_strict_templates.tsv"
EVENT_ROLES = OUT / "gdt481_event_role_shapes.tsv"
PAIR_ASSIGNMENTS = OUT / "gdt481_48_adjacent_pair_assignments.tsv"
PAIR_STRICT = OUT / "gdt481_pair_strict_templates.tsv"
PAIR_ROLES = OUT / "gdt481_pair_role_shapes.tsv"
RECORD_COVERAGE = OUT / "gdt481_135_record_fragment_coverage.tsv"
SUMMARY = OUT / "gdt481_fragment_coverage_summary.tsv"
READABLE = OUT / "GDT481_MICRORECORD_FRAGMENT_GRAMMAR.md"
RESULT = OUT / "gdt481_result.json"

NAME_RE = re.compile(r"\[(?:[A-ZÄÖÜ_]*NAME):([^\]]+)\]")
QUOTE_RE = re.compile(r"»([^»]+)«")
ROLE_MAP = {
    "DANACH": "ORDER", "FORTSETZEN": "ORDER",
    "POSTEN": "ARG", "WERT": "ARG", "ANTEIL": "ARG", "EINHEIT": "ARG",
    "ZIELORT": "REL", "AUSGANG": "REL", "VERBINDUNG": "REL", "BAHN": "REL",
    "SETZEN": "ACTION", "NEHMEN": "ACTION", "HALTEN": "ACTION",
    "GEBEN": "ACTION", "WÄHLEN": "ACTION", "BEARBEITEN": "ACTION",
    "EINSTELLEN": "ACTION", "MARKIEREN": "ACTION", "EINSETZEN": "ACTION",
}
OWNER_PHRASE_REPLACEMENTS = [
    (r"\b(?:von der Ausgangsposition|vom Ausgangsgefäß)\b", "vom Ausgang"),
    (r"\b(?:zur Zielposition|zum Zielgefäß)\b", "zum Zielort"),
    (r"\b(?:von der Zielposition|vom Zielgefäß)\b", "vom Zielort"),
    (r"\b(?:zur Ausgangsposition|zum Ausgangsgefäß)\b", "zum Ausgang"),
    (r"\b(?:entlang der Ringbahn|entlang der Stationsbahn|entlang der Verarbeitungsbahn|entlang der Transferbahn|entlang der Lesebahn)\b", "entlang der Bahn"),
    (r"\b(?:Positionswert|Stationswert|Mengenwert)\b", "Wert"),
    (r"\b(?:Positionsposten|Stationsposten|Drogenposten)\b", "Posten"),
    (r"\b(?:Zielposition|Zielgefäß)\b", "Zielort"),
    (r"\b(?:Ausgangsposition|Ausgangsgefäß)\b", "Ausgang"),
    (r"\b(?:Ringbahn|Stationsbahn|Verarbeitungsbahn|Transferbahn|Lesebahn)\b", "Bahn"),
    (r"\b(?:Sektoranteil|Drogenanteil)\b", "Anteil"),
    (r"\b(?:Positionseinheit|Stationseinheit|Ansatzeinheit)\b", "Einheit"),
    (r"\bDrogenfamilie\b", "Namensfamilie"),
    (r"\b(?:Pflanzeneintrag|Pflanzenname|Pflanze)\b", "Namenseintrag"),
    (r"\b(?:Sternstelleneintrag|Sternstelle)\b", "Namenseintrag"),
    (r"\b(?:Drogeneintrag|Droge)\b", "Namenseintrag"),
    (r"\b(?:Badstationseintrag|Badstation)\b", "Namenseintrag"),
]


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


def normalize_literal(text: str, names: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        core = match.group(1)
        names.setdefault(core, f"N{len(names) + 1}")
        return "{" + names[core] + "}"

    value = NAME_RE.sub(replace, text)
    return re.sub(r"\b[^ ·/]+:DROGENFAMILIE\b", "{F1}:NAMENSFAMILIE", value)


def normalize_phrase(text: str) -> str:
    names: dict[str, str] = {}

    def replace_quote(match: re.Match[str]) -> str:
        core = match.group(1)
        names.setdefault(core, f"N{len(names) + 1}")
        return "»{" + names[core] + "}«"

    value = QUOTE_RE.sub(replace_quote, text)
    for pattern, replacement in OWNER_PHRASE_REPLACEMENTS:
        value = re.sub(pattern, replacement, value)
    return value


def role_token(token: str) -> str:
    token = token.strip()
    if re.fullmatch(r"\{N\d+\}", token):
        return "NAME"
    base = re.sub(r"\s*\[[^\]]+\]\s*$", "", token)
    if base in ROLE_MAP:
        return ROLE_MAP[base] + ("[MOD]" if base != token else "")
    if re.fullmatch(r"\{N\d+\}", base):
        return "NAME[MOD]" if base != token else "NAME"
    return "MOD"


def role_trace(literal: str) -> str:
    pieces = re.split(r"(\s+·\s+|\s+/\s+)", literal)
    return "".join(piece if re.fullmatch(r"\s+·\s+|\s+/\s+", piece) else role_token(piece) for piece in pieces)


def event_scope(event: dict[str, str]) -> str:
    operation = event["state_operation_sequence"]
    if operation == "NONE":
        return "NONE"
    return f"{operation}:{event['scope_orientation_sequence']}"


def recurrence_class(count: int, pages: int, registers: int) -> str:
    if registers > 1:
        return "CROSS_REGISTER"
    if pages > 1:
        return "CROSS_PAGE"
    if count > 1:
        return "SAME_PAGE_RECURRENT"
    return "SINGLETON"


def most_common_first(values: list[str]) -> str:
    counts = Counter(values)
    best = max(counts.values())
    return next(value for value in values if counts[value] == best)


def compile_templates(
    items: list[dict[str, object]], key_field: str, id_prefix: str, frame_field: str,
    strict_member_field: str | None = None,
) -> tuple[list[dict[str, object]], dict[str, str]]:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        groups[str(item[key_field])].append(item)
    ids = {key: f"{id_prefix}{index:03d}" for index, key in enumerate(groups, 1)}
    rows: list[dict[str, object]] = []
    for key, group in groups.items():
        pages = list(dict.fromkeys(str(row["physical_page"]) for row in group))
        registers = list(dict.fromkeys(str(row["register"]) for row in group))
        records = list(dict.fromkeys(str(row["record_id"]) for row in group))
        surfaces = list(dict.fromkeys(str(row["surface_fragment"]) for row in group))
        recipes = list(dict.fromkeys(str(row["recipe_frame"]) for row in group))
        phrases = [str(row["owner_neutral_phrase_de"]) for row in group]
        row: dict[str, object] = {
            "template_id": ids[key],
            frame_field: key,
            "occurrence_count": len(group),
            "record_count": len(records),
            "page_count": len(pages),
            "register_count": len(registers),
            "recurrence_class": recurrence_class(len(group), len(pages), len(registers)),
            "surface_type_count": len(surfaces),
            "surface_recurrence_mode": "MULTIPLE_SURFACES" if len(surfaces) > 1 else ("SAME_SURFACE" if len(group) > 1 else "SINGLETON"),
            "recipe_variant_count": len(recipes),
            "recipe_frames": "|".join(recipes),
            "phrase_variant_count": len(set(phrases)),
            "canonical_owner_neutral_phrase_de": most_common_first(phrases),
            "phrase_stable": "YES" if len(set(phrases)) == 1 else "NO",
            "pages": "|".join(pages),
            "registers": "|".join(registers),
            "record_ids": "|".join(records),
            "source_fragment_ids": "|".join(str(row["fragment_id"]) for row in group),
            "surface_examples": " || ".join(surfaces[:8]),
        }
        if strict_member_field:
            members = list(dict.fromkeys(str(item[strict_member_field]) for item in group))
            row["strict_template_count"] = len(members)
            row["strict_template_ids"] = "|".join(members)
            row["claim_status"] = "ROLE_FRAGMENT_BACKOFF__STRICT_TEMPLATE_CONTROLS_READING"
        else:
            row["claim_status"] = "STRICT_OWNER_NEUTRAL_FRAGMENT__NO_NEW_MEANING"
        rows.append(row)
    return rows, ids


def build_readable(
    event_strict: list[dict[str, object]], pair_strict: list[dict[str, object]], result: dict[str, object]
) -> str:
    lines = [
        "# GDT481 — Mikroeintrags-Fragmentgrammatik",
        "",
        "Die 135 vollständigen Records zerfallen in 183 Einzelevents und 48 echte Nachbarpaare. Jedes Fragment behält ein enges Bedeutungstemplate und eine Rollenform; Wiederholung ist Vertrautheit, kein Zwang zur Umdeutung.",
        "",
        "| Fragment | eng/gesamt | eng wiederkehrend (Vorkommen) | Rollenformen/gesamt | Rollen wiederkehrend (Vorkommen) |",
        "|---|---:|---:|---:|---:|",
        f"| Einzelevent | {result['event_strict_template_count']}/183 | {result['recurrent_event_strict_template_count']} ({result['events_in_recurrent_strict_templates']}) | {result['event_role_shape_count']}/183 | {result['recurrent_event_role_shape_count']} ({result['events_in_recurrent_role_shapes']}) |",
        f"| Nachbarpaar | {result['pair_strict_template_count']}/48 | {result['recurrent_pair_strict_template_count']} ({result['pairs_in_recurrent_strict_templates']}) | {result['pair_role_shape_count']}/48 | {result['recurrent_pair_role_shape_count']} ({result['pairs_in_recurrent_role_shapes']}) |",
        "",
        f"Von 107 einzigartigen Ganzrecords enthalten {result['singleton_records_with_any_recurrent_strict_event']} wenigstens ein wiederkehrendes enges Event; {result['singleton_records_with_all_events_recurrent_strict']} sind vollständig aus solchen Events gebaut. {result['singleton_records_with_any_recurrent_strict_pair']} enthalten ein wiederkehrendes enges Nachbarpaar.",
        f"Mit Rollen-Backoff werden {result['singleton_records_with_any_recurrent_role_event']} der 107 Einzelrecords erreicht; {result['singleton_records_with_no_recurrent_fragment']} behalten einen vollständig einzigartigen Fragmenttail. Alle elf Querbündelpaare bleiben eng einzigartig.",
        f"Von diesen 48 Resttails sind {result['no_recurrent_fragment_single_event_record_count']} bereits Einzelevent-Records; die nächste Zerlegung muss daher innerhalb des Events ansetzen, nicht an einer Satzgrenze.",
        "",
        "## Wiederkehrende enge Einzelevents",
        "",
    ]
    event_rows = [row for row in event_strict if int(row["occurrence_count"]) > 1]
    event_rows.sort(key=lambda row: (-int(row["occurrence_count"]), str(row["template_id"])))
    for row in event_rows:
        lines.extend([
            f"- **{row['template_id']}** · {row['occurrence_count']} Vorkommen · {row['recurrence_class']} · `{row['strict_frame']}` · {row['canonical_owner_neutral_phrase_de']} · Oberflächen {row['surface_examples']}",
        ])
    lines.extend(["", "## Wiederkehrende enge Nachbarpaare", ""])
    pair_rows = [row for row in pair_strict if int(row["occurrence_count"]) > 1]
    pair_rows.sort(key=lambda row: (-int(row["occurrence_count"]), str(row["template_id"])))
    if not pair_rows:
        lines.append("Keine engen Nachbarpaare wiederholen sich.")
    for row in pair_rows:
        lines.append(
            f"- **{row['template_id']}** · {row['occurrence_count']} Vorkommen · {row['recurrence_class']} · `{row['strict_frame']}` · Oberflächen {row['surface_examples']}"
        )
    lines.extend([
        "",
        "Die Rollenformen stehen in den Maschinentabellen. Sie dürfen ein seltenes Fragment typisieren, ersetzen aber nie dessen enges Komponenten-Template. Record-Grenzen und die elf OL-gebundenen Querbündelpaare bleiben explizit.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS_IN)
    bundles = read_tsv(BUNDLES_IN)
    records = read_tsv(RECORDS_IN)
    g480 = read_tsv(G480_ASSIGNMENTS)
    if (len(events), len(bundles), len(records), len(g480)) != (183, 146, 135, 135):
        raise RuntimeError("GDT479/GDT480 input drift")

    events_by_bundle: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_bundle[event["bundle_id"]].append(event)
    bundle_map = {row["bundle_id"]: row for row in bundles}
    record_map = {row["record_id"]: row for row in records}
    g480_map = {row["record_id"]: row for row in g480}

    sequences: dict[str, list[tuple[dict[str, str], dict[str, str], int, int]]] = {}
    event_items: list[dict[str, object]] = []
    for record in records:
        sequence: list[tuple[dict[str, str], dict[str, str], int, int]] = []
        for bundle_index, bundle_id in enumerate(record["bundle_ids"].split("|"), 1):
            bundle = bundle_map[bundle_id]
            for event_index, event in enumerate(events_by_bundle[bundle_id], 1):
                sequence.append((event, bundle, bundle_index, event_index))
        sequences[record["record_id"]] = sequence
        for record_event_index, (event, bundle, bundle_index, event_index) in enumerate(sequence, 1):
            names: dict[str, str] = {}
            literal = normalize_literal(event["literal_working_reading_de"], names)
            scope = event_scope(event)
            model = bundle["active_model"]
            if event_index > 1:
                boundary_context = "WITHIN_BUNDLE"
            elif bundle_index > 1:
                boundary_context = f"CROSS_BUNDLE:{bundle['boundary_role']}"
            else:
                boundary_context = f"RECORD_START:{record['record_start_role']}"
            event_items.append({
                "fragment_id": f"G481-E{len(event_items) + 1:03d}",
                "source_event_id": event["source_event_id"],
                "record_id": record["record_id"],
                "bundle_id": bundle["bundle_id"],
                "physical_page": record["physical_page"],
                "register": record["register"],
                "record_event_ordinal": record_event_index,
                "bundle_event_ordinal": event_index,
                "boundary_context": boundary_context,
                "active_model": model,
                "surface_fragment": event["surface"],
                "strict_key": f"{model}[{literal} @{scope}]",
                "role_key": f"{model}[{role_trace(literal)} @{scope}]",
                "recipe_frame": f"{model}[{event['working_recipe']} @{scope}]",
                "owner_neutral_phrase_de": normalize_phrase(event["definitive_event_reading_de"]),
                "definitive_fragment_reading_de": event["definitive_event_reading_de"],
                "literal_name_slot_count": len(names),
            })

    event_strict_rows, event_strict_ids = compile_templates(event_items, "strict_key", "G481-ET", "strict_frame")
    for item in event_items:
        item["strict_template_id"] = event_strict_ids[str(item["strict_key"])]
    event_role_rows, event_role_ids = compile_templates(event_items, "role_key", "G481-ES", "role_frame", "strict_template_id")
    for item in event_items:
        item["role_shape_id"] = event_role_ids[str(item["role_key"])]
    event_strict_map = {str(row["template_id"]): row for row in event_strict_rows}
    event_role_map = {str(row["template_id"]): row for row in event_role_rows}

    event_assignment_rows: list[dict[str, object]] = []
    event_by_source: dict[str, dict[str, object]] = {}
    for item in event_items:
        strict = event_strict_map[str(item["strict_template_id"])]
        role = event_role_map[str(item["role_shape_id"])]
        row = {
            "event_fragment_id": item["fragment_id"],
            "source_event_id": item["source_event_id"],
            "record_id": item["record_id"],
            "bundle_id": item["bundle_id"],
            "physical_page": item["physical_page"],
            "register": item["register"],
            "record_event_ordinal": item["record_event_ordinal"],
            "bundle_event_ordinal": item["bundle_event_ordinal"],
            "boundary_context": item["boundary_context"],
            "active_model": item["active_model"],
            "surface": item["surface_fragment"],
            "strict_template_id": item["strict_template_id"],
            "strict_occurrence_count": strict["occurrence_count"],
            "strict_recurrence_class": strict["recurrence_class"],
            "strict_frame": item["strict_key"],
            "recipe_frame": item["recipe_frame"],
            "role_shape_id": item["role_shape_id"],
            "role_occurrence_count": role["occurrence_count"],
            "role_recurrence_class": role["recurrence_class"],
            "role_frame": item["role_key"],
            "owner_neutral_phrase_de": item["owner_neutral_phrase_de"],
            "definitive_fragment_reading_de": item["definitive_fragment_reading_de"],
            "all_fragments_have_default": "YES",
        }
        event_assignment_rows.append(row)
        event_by_source[str(item["source_event_id"])] = row

    pair_items: list[dict[str, object]] = []
    for record in records:
        sequence = sequences[record["record_id"]]
        for pair_index in range(len(sequence) - 1):
            left_event, left_bundle, _, _ = sequence[pair_index]
            right_event, right_bundle, _, _ = sequence[pair_index + 1]
            names: dict[str, str] = {}
            left_literal = normalize_literal(left_event["literal_working_reading_de"], names)
            right_literal = normalize_literal(right_event["literal_working_reading_de"], names)
            left_scope = event_scope(left_event)
            right_scope = event_scope(right_event)
            same_bundle = left_bundle["bundle_id"] == right_bundle["bundle_id"]
            boundary = "SAME_BUNDLE" if same_bundle else f"CROSS_BUNDLE:{right_bundle['boundary_role']}"
            left_model = left_bundle["active_model"]
            right_model = right_bundle["active_model"]
            pair_items.append({
                "fragment_id": f"G481-P{len(pair_items) + 1:03d}",
                "record_id": record["record_id"],
                "physical_page": record["physical_page"],
                "register": record["register"],
                "pair_ordinal_in_record": pair_index + 1,
                "left_source_event_id": left_event["source_event_id"],
                "right_source_event_id": right_event["source_event_id"],
                "left_bundle_id": left_bundle["bundle_id"],
                "right_bundle_id": right_bundle["bundle_id"],
                "pair_boundary": boundary,
                "surface_fragment": f"{left_event['surface']}|{right_event['surface']}",
                "strict_key": f"{left_model}[{left_literal} @{left_scope}] <{boundary}> {right_model}[{right_literal} @{right_scope}]",
                "role_key": f"{left_model}[{role_trace(left_literal)} @{left_scope}] <{boundary}> {right_model}[{role_trace(right_literal)} @{right_scope}]",
                "recipe_frame": f"{left_model}[{left_event['working_recipe']} @{left_scope}] <{boundary}> {right_model}[{right_event['working_recipe']} @{right_scope}]",
                "owner_neutral_phrase_de": normalize_phrase(left_event["definitive_event_reading_de"] + " Dann: " + right_event["definitive_event_reading_de"]),
                "definitive_fragment_reading_de": left_event["definitive_event_reading_de"] + " Dann: " + right_event["definitive_event_reading_de"],
                "literal_name_slot_count": len(names),
            })

    pair_strict_rows, pair_strict_ids = compile_templates(pair_items, "strict_key", "G481-PT", "strict_frame")
    for item in pair_items:
        item["strict_template_id"] = pair_strict_ids[str(item["strict_key"])]
    pair_role_rows, pair_role_ids = compile_templates(pair_items, "role_key", "G481-PS", "role_frame", "strict_template_id")
    for item in pair_items:
        item["role_shape_id"] = pair_role_ids[str(item["role_key"])]
    pair_strict_map = {str(row["template_id"]): row for row in pair_strict_rows}
    pair_role_map = {str(row["template_id"]): row for row in pair_role_rows}

    pair_assignment_rows: list[dict[str, object]] = []
    pairs_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in pair_items:
        strict = pair_strict_map[str(item["strict_template_id"])]
        role = pair_role_map[str(item["role_shape_id"])]
        row = {
            "pair_fragment_id": item["fragment_id"],
            "record_id": item["record_id"],
            "physical_page": item["physical_page"],
            "register": item["register"],
            "pair_ordinal_in_record": item["pair_ordinal_in_record"],
            "left_source_event_id": item["left_source_event_id"],
            "right_source_event_id": item["right_source_event_id"],
            "left_bundle_id": item["left_bundle_id"],
            "right_bundle_id": item["right_bundle_id"],
            "pair_boundary": item["pair_boundary"],
            "surface_pair": item["surface_fragment"],
            "strict_template_id": item["strict_template_id"],
            "strict_occurrence_count": strict["occurrence_count"],
            "strict_recurrence_class": strict["recurrence_class"],
            "strict_frame": item["strict_key"],
            "recipe_frame": item["recipe_frame"],
            "role_shape_id": item["role_shape_id"],
            "role_occurrence_count": role["occurrence_count"],
            "role_recurrence_class": role["recurrence_class"],
            "role_frame": item["role_key"],
            "owner_neutral_phrase_de": item["owner_neutral_phrase_de"],
            "definitive_fragment_reading_de": item["definitive_fragment_reading_de"],
            "all_fragments_have_default": "YES",
        }
        pair_assignment_rows.append(row)
        pairs_by_record[str(item["record_id"])].append(row)

    events_by_record: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_assignment_rows:
        events_by_record[str(row["record_id"])].append(row)
    coverage_rows: list[dict[str, object]] = []
    for record in records:
        record_events = events_by_record[record["record_id"]]
        record_pairs = pairs_by_record[record["record_id"]]
        strict_event_recurrent = sum(int(row["strict_occurrence_count"]) > 1 for row in record_events)
        role_event_recurrent = sum(int(row["role_occurrence_count"]) > 1 for row in record_events)
        strict_pair_recurrent = sum(int(row["strict_occurrence_count"]) > 1 for row in record_pairs)
        role_pair_recurrent = sum(int(row["role_occurrence_count"]) > 1 for row in record_pairs)
        singleton = g480_map[record["record_id"]]["strict_recurrence_class"] == "SINGLETON"
        if strict_event_recurrent == len(record_events):
            decomposition = "FULL_STRICT_EVENT_COVERAGE"
        elif strict_pair_recurrent:
            decomposition = "HAS_RECURRENT_STRICT_PAIR"
        elif strict_event_recurrent:
            decomposition = "PARTIAL_STRICT_EVENT_COVERAGE"
        elif role_event_recurrent == len(record_events):
            decomposition = "FULL_ROLE_EVENT_COVERAGE"
        elif role_event_recurrent or role_pair_recurrent:
            decomposition = "PARTIAL_ROLE_FRAGMENT_COVERAGE"
        else:
            decomposition = "SINGLETON_FRAGMENT_TAIL"
        coverage_rows.append({
            "record_id": record["record_id"],
            "physical_page": record["physical_page"],
            "register": record["register"],
            "gdt480_strict_template_id": g480_map[record["record_id"]]["strict_template_id"],
            "gdt480_strict_recurrence_class": g480_map[record["record_id"]]["strict_recurrence_class"],
            "gdt480_whole_record_singleton": "YES" if singleton else "NO",
            "event_count": len(record_events),
            "recurrent_strict_event_count": strict_event_recurrent,
            "all_events_strict_recurrent": "YES" if strict_event_recurrent == len(record_events) else "NO",
            "recurrent_role_event_count": role_event_recurrent,
            "all_events_role_recurrent": "YES" if role_event_recurrent == len(record_events) else "NO",
            "pair_count": len(record_pairs),
            "recurrent_strict_pair_count": strict_pair_recurrent,
            "any_strict_pair_recurrent": "YES" if strict_pair_recurrent else "NO",
            "recurrent_role_pair_count": role_pair_recurrent,
            "any_role_pair_recurrent": "YES" if role_pair_recurrent else "NO",
            "decomposition_class": decomposition,
            "surface_sequence": record["surface_sequence"],
            "definitive_record_reading_de": record["definitive_record_reading_de"],
        })

    def metric_row(scope: str, label: str, predicate) -> dict[str, object]:
        rows = coverage_rows if scope == "ALL_RECORDS" else [row for row in coverage_rows if row["gdt480_whole_record_singleton"] == "YES"]
        selected = [row for row in rows if predicate(row)]
        return {
            "scope": scope,
            "metric": label,
            "record_count": len(selected),
            "denominator": len(rows),
            "fraction": f"{len(selected) / len(rows):.6f}",
            "record_ids": "|".join(str(row["record_id"]) for row in selected) or "NONE",
        }

    metrics = [
        ("ANY_RECURRENT_STRICT_EVENT", lambda row: int(row["recurrent_strict_event_count"]) > 0),
        ("ALL_EVENTS_RECURRENT_STRICT", lambda row: row["all_events_strict_recurrent"] == "YES"),
        ("ANY_RECURRENT_STRICT_PAIR", lambda row: row["any_strict_pair_recurrent"] == "YES"),
        ("ANY_RECURRENT_ROLE_EVENT", lambda row: int(row["recurrent_role_event_count"]) > 0),
        ("ALL_EVENTS_RECURRENT_ROLE", lambda row: row["all_events_role_recurrent"] == "YES"),
        ("ANY_RECURRENT_ROLE_PAIR", lambda row: row["any_role_pair_recurrent"] == "YES"),
        ("NO_RECURRENT_FRAGMENT", lambda row: row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL"),
    ]
    summary_rows = [metric_row(scope, label, predicate) for scope in ("ALL_RECORDS", "GDT480_SINGLETON_RECORDS") for label, predicate in metrics]

    recurrent_event_strict = [row for row in event_strict_rows if int(row["occurrence_count"]) > 1]
    recurrent_event_roles = [row for row in event_role_rows if int(row["occurrence_count"]) > 1]
    recurrent_pair_strict = [row for row in pair_strict_rows if int(row["occurrence_count"]) > 1]
    recurrent_pair_roles = [row for row in pair_role_rows if int(row["occurrence_count"]) > 1]
    singleton_coverage = [row for row in coverage_rows if row["gdt480_whole_record_singleton"] == "YES"]
    no_fragment_coverage = [row for row in singleton_coverage if row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL"]
    result: dict[str, object] = {
        "status": "EVENT_FRAGMENTS_REACH_59_OF_107_SINGLETON_RECORDS__ADJACENT_PAIRS_REMAIN_SPARSE",
        "event_count": len(event_assignment_rows),
        "adjacent_pair_count": len(pair_assignment_rows),
        "cross_bundle_pair_count": sum(row["pair_boundary"].startswith("CROSS_BUNDLE") for row in pair_assignment_rows),
        "event_strict_template_count": len(event_strict_rows),
        "recurrent_event_strict_template_count": len(recurrent_event_strict),
        "events_in_recurrent_strict_templates": sum(int(row["occurrence_count"]) for row in recurrent_event_strict),
        "cross_page_event_strict_template_count": sum(int(row["page_count"]) > 1 for row in event_strict_rows),
        "cross_register_event_strict_template_count": sum(int(row["register_count"]) > 1 for row in event_strict_rows),
        "events_in_cross_register_strict_templates": sum(int(row["occurrence_count"]) for row in event_strict_rows if int(row["register_count"]) > 1),
        "multisurface_recurrent_event_strict_template_count": sum(int(row["surface_type_count"]) > 1 for row in recurrent_event_strict),
        "events_in_multisurface_recurrent_strict_templates": sum(int(row["occurrence_count"]) for row in recurrent_event_strict if int(row["surface_type_count"]) > 1),
        "event_role_shape_count": len(event_role_rows),
        "recurrent_event_role_shape_count": len(recurrent_event_roles),
        "events_in_recurrent_role_shapes": sum(int(row["occurrence_count"]) for row in recurrent_event_roles),
        "cross_register_event_role_shape_count": sum(int(row["register_count"]) > 1 for row in event_role_rows),
        "pair_strict_template_count": len(pair_strict_rows),
        "recurrent_pair_strict_template_count": len(recurrent_pair_strict),
        "pairs_in_recurrent_strict_templates": sum(int(row["occurrence_count"]) for row in recurrent_pair_strict),
        "cross_page_pair_strict_template_count": sum(int(row["page_count"]) > 1 for row in pair_strict_rows),
        "cross_register_pair_strict_template_count": sum(int(row["register_count"]) > 1 for row in pair_strict_rows),
        "multisurface_recurrent_pair_strict_template_count": sum(int(row["surface_type_count"]) > 1 for row in recurrent_pair_strict),
        "recurrent_cross_bundle_pair_occurrence_count": sum(int(row["strict_occurrence_count"]) > 1 and str(row["pair_boundary"]).startswith("CROSS_BUNDLE") for row in pair_assignment_rows),
        "pair_role_shape_count": len(pair_role_rows),
        "recurrent_pair_role_shape_count": len(recurrent_pair_roles),
        "pairs_in_recurrent_role_shapes": sum(int(row["occurrence_count"]) for row in recurrent_pair_roles),
        "cross_register_pair_role_shape_count": sum(int(row["register_count"]) > 1 for row in pair_role_rows),
        "gdt480_singleton_record_count": len(singleton_coverage),
        "singleton_records_with_any_recurrent_strict_event": sum(int(row["recurrent_strict_event_count"]) > 0 for row in singleton_coverage),
        "singleton_records_with_all_events_recurrent_strict": sum(row["all_events_strict_recurrent"] == "YES" for row in singleton_coverage),
        "singleton_records_with_any_recurrent_strict_pair": sum(row["any_strict_pair_recurrent"] == "YES" for row in singleton_coverage),
        "singleton_records_with_any_recurrent_role_event": sum(int(row["recurrent_role_event_count"]) > 0 for row in singleton_coverage),
        "singleton_records_with_all_events_recurrent_role": sum(row["all_events_role_recurrent"] == "YES" for row in singleton_coverage),
        "singleton_records_with_any_recurrent_role_pair": sum(row["any_role_pair_recurrent"] == "YES" for row in singleton_coverage),
        "singleton_records_with_no_recurrent_fragment": sum(row["decomposition_class"] == "SINGLETON_FRAGMENT_TAIL" for row in singleton_coverage),
        "no_recurrent_fragment_single_event_record_count": sum(int(row["event_count"]) == 1 for row in no_fragment_coverage),
        "no_recurrent_fragment_event_count_profile": dict(Counter(str(row["event_count"]) for row in no_fragment_coverage)),
        "no_recurrent_fragment_page_counts": dict(Counter(str(row["physical_page"]) for row in no_fragment_coverage)),
        "all_events_have_default_count": sum(row["all_fragments_have_default"] == "YES" for row in event_assignment_rows),
        "all_pairs_have_default_count": sum(row["all_fragments_have_default"] == "YES" for row in pair_assignment_rows),
        "component_meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Recurrent event and adjacent-event fragment grammar over fixed GDT479/GDT480 readings; no new meaning, syntax, plaintext, name, surface, recipe, boundary, record, or page.",
    }

    write_tsv(EVENT_ASSIGNMENTS, event_assignment_rows)
    write_tsv(EVENT_STRICT, event_strict_rows)
    write_tsv(EVENT_ROLES, event_role_rows)
    write_tsv(PAIR_ASSIGNMENTS, pair_assignment_rows)
    write_tsv(PAIR_STRICT, pair_strict_rows)
    write_tsv(PAIR_ROLES, pair_role_rows)
    write_tsv(RECORD_COVERAGE, coverage_rows)
    write_tsv(SUMMARY, summary_rows)
    READABLE.write_text(build_readable(event_strict_rows, pair_strict_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "event_templates": result["event_strict_template_count"],
        "recurrent_events": result["events_in_recurrent_strict_templates"],
        "pair_templates": result["pair_strict_template_count"],
        "recurrent_pairs": result["pairs_in_recurrent_strict_templates"],
        "singleton_any_event": result["singleton_records_with_any_recurrent_strict_event"],
        "singleton_all_events": result["singleton_records_with_all_events_recurrent_strict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
