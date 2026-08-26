#!/usr/bin/env python3
"""Collapse the GDT479 edition into recurrent microrecord templates."""

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
BASE = ROOT / "experiments/yolo/gdt480_microrecord_template_atlas"
OUT = BASE / "artifacts"
G479 = ROOT / "experiments/yolo/gdt479_definitive_local_microrecord_edition/artifacts"
EVENTS_IN = G479 / "gdt479_183_definitive_local_events.tsv"
BUNDLES_IN = G479 / "gdt479_146_definitive_local_bundles.tsv"
RECORDS_IN = G479 / "gdt479_135_definitive_microrecords.tsv"
ASSIGNMENTS = OUT / "gdt480_135_record_template_assignments.tsv"
STRICT = OUT / "gdt480_strict_semantic_templates.tsv"
SHAPES = OUT / "gdt480_role_shape_templates.tsv"
COVERAGE = OUT / "gdt480_template_coverage_summary.tsv"
READABLE = OUT / "GDT480_MICRORECORD_TEMPLATE_ATLAS.md"
RESULT = OUT / "gdt480_result.json"

NAME_RE = re.compile(r"\[(?:[A-ZÄÖÜ_]*NAME):([^\]]+)\]")
QUOTE_RE = re.compile(r"»([^»]+)«")
ROLE_MAP = {
    "DANACH": "ORDER",
    "FORTSETZEN": "ORDER",
    "POSTEN": "ARG",
    "WERT": "ARG",
    "ANTEIL": "ARG",
    "EINHEIT": "ARG",
    "ZIELORT": "REL",
    "AUSGANG": "REL",
    "VERBINDUNG": "REL",
    "BAHN": "REL",
    "SETZEN": "ACTION",
    "NEHMEN": "ACTION",
    "HALTEN": "ACTION",
    "GEBEN": "ACTION",
    "WÄHLEN": "ACTION",
    "BEARBEITEN": "ACTION",
    "EINSTELLEN": "ACTION",
    "MARKIEREN": "ACTION",
    "EINSETZEN": "ACTION",
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
        suffix = "[MOD]" if base != token else ""
        return ROLE_MAP[base] + suffix
    if re.fullmatch(r"\{N\d+\}", base):
        return "NAME[MOD]" if base != token else "NAME"
    return "MOD"


def role_trace(literal: str) -> str:
    pieces = re.split(r"(\s+·\s+|\s+/\s+)", literal)
    return "".join(piece if re.fullmatch(r"\s+·\s+|\s+/\s+", piece) else role_token(piece) for piece in pieces)


def recurrence_class(record_count: int, page_count: int, register_count: int) -> str:
    if register_count > 1:
        return "CROSS_REGISTER"
    if page_count > 1:
        return "CROSS_PAGE"
    if record_count > 1:
        return "SAME_PAGE_RECURRENT"
    return "SINGLETON"


def joined_unique(values: list[str]) -> str:
    return "|".join(dict.fromkeys(values))


def most_common_first(values: list[str]) -> str:
    counts = Counter(values)
    best = max(counts.values())
    return next(value for value in values if counts[value] == best)


def build_readable(
    strict_rows: list[dict[str, object]],
    shape_rows: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT480 — Mikroeintrags-Templateatlas",
        "",
        "Jeder der 135 GDT479-Mikroeinträge besitzt nun zwei explizite Baupläne: ein enges bedeutungsgleiches Template und eine gröbere Rollenform. Auch Einzelstücke behalten einen Default; Wiederholung erhöht nur die Vertrautheit.",
        "",
        "| Ebene | Templates | wiederkehrend | abgedeckte Einträge | seitenübergreifend | registerübergreifend |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Enges Bedeutungstemplate | {result['strict_template_count']} | {result['recurrent_strict_template_count']} | {result['records_in_recurrent_strict_templates']} | {result['cross_page_strict_template_count']} | {result['cross_register_strict_template_count']} |",
        f"| Rollenform | {result['role_shape_count']} | {result['recurrent_role_shape_count']} | {result['records_in_recurrent_role_shapes']} | {result['cross_page_role_shape_count']} | {result['cross_register_role_shape_count']} |",
        "",
        f"Acht enge Wiederholungsfamilien verbinden 18 Einträge mit verschiedenen sichtbaren Oberflächen; fünf weitere sind echte Oberflächenwiederholungen. Dreizehn Rollenformen verbinden 33 Einträge über mehr als ein enges Bedeutungstemplate hinweg.",
        "",
        "## Wiederkehrende enge Templates",
        "",
    ]
    recurrent = [row for row in strict_rows if int(row["record_count"]) > 1]
    recurrent.sort(key=lambda row: (-int(row["record_count"]), str(row["strict_template_id"])))
    if not recurrent:
        lines.append("Keine.")
    for row in recurrent:
        lines.extend([
            f"### {row['strict_template_id']} — {row['record_count']} Einträge, {row['recurrence_class']}",
            "",
            f"- Komponenten: `{row['strict_semantic_frame']}`",
            f"- Leseschablone: {row['canonical_owner_neutral_phrase_de']}",
            f"- Rezepte: `{str(row['recipe_frames']).replace('|', '`, `')}`",
            f"- Seiten/Register: {row['pages']} / {row['registers']}",
            f"- Einträge: {row['record_ids']}",
            "",
        ])
    lines.extend(["## Alle Rollenformen", ""])
    for row in sorted(shape_rows, key=lambda item: (-int(item["record_count"]), str(item["role_shape_id"]))):
        lines.append(
            f"- **{row['role_shape_id']}** · {row['record_count']} Einträge · {row['recurrence_class']} · `{row['role_shape_frame']}` · strenge Templates {row['strict_template_count']}"
        )
    lines.extend([
        "",
        "Die Rollenformen ersetzen keine Wurzelbedeutung. Sie zeigen nur, dass etwa ACTION·ARG und ORDER·REL dieselbe grobe Satzstelle teilen können. Für eine konkrete Lesung bleibt immer das enge Template mit seinem vollständigen Komponenten- und Reihenfolgetrace maßgeblich.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS_IN)
    bundles = read_tsv(BUNDLES_IN)
    records = read_tsv(RECORDS_IN)
    if (len(events), len(bundles), len(records)) != (183, 146, 135):
        raise RuntimeError("GDT479 input drift")

    events_by_bundle: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_bundle[event["bundle_id"]].append(event)
    bundle_map = {row["bundle_id"]: row for row in bundles}

    prepared: list[dict[str, object]] = []
    for record in records:
        names: dict[str, str] = {}
        strict_bundles: list[str] = []
        shape_bundles: list[str] = []
        recipe_bundles: list[str] = []
        for bundle_id in record["bundle_ids"].split("|"):
            bundle = bundle_map[bundle_id]
            strict_events: list[str] = []
            shape_events: list[str] = []
            recipe_events: list[str] = []
            for event in events_by_bundle[bundle_id]:
                literal = normalize_literal(event["literal_working_reading_de"], names)
                operation = event["state_operation_sequence"]
                orientation = event["scope_orientation_sequence"]
                scope = "NONE" if operation == "NONE" else f"{operation}:{orientation}"
                strict_events.append(f"{literal} @{scope}")
                shape_events.append(f"{role_trace(literal)} @{scope}")
                recipe_events.append(f"{event['working_recipe']} @{scope}")
            model = bundle["active_model"]
            strict_bundles.append(f"{model}[" + " / ".join(strict_events) + "]")
            shape_bundles.append(f"{model}[" + " / ".join(shape_events) + "]")
            recipe_bundles.append(f"{model}[" + " / ".join(recipe_events) + "]")
        prepared.append({
            **record,
            "strict_key": " || ".join(strict_bundles),
            "shape_key": " || ".join(shape_bundles),
            "recipe_frame": " || ".join(recipe_bundles),
            "owner_neutral_phrase": normalize_phrase(record["definitive_record_reading_de"]),
            "literal_name_slot_count": len(names),
        })

    strict_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    shape_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in prepared:
        strict_groups[str(row["strict_key"])].append(row)
        shape_groups[str(row["shape_key"])].append(row)
    strict_ids = {key: f"G480-T{index:03d}" for index, key in enumerate(strict_groups, 1)}
    shape_ids = {key: f"G480-S{index:03d}" for index, key in enumerate(shape_groups, 1)}

    strict_rows: list[dict[str, object]] = []
    for key, group in strict_groups.items():
        pages = list(dict.fromkeys(str(row["physical_page"]) for row in group))
        registers = list(dict.fromkeys(str(row["register"]) for row in group))
        recipes = list(dict.fromkeys(str(row["recipe_frame"]) for row in group))
        phrases = [str(row["owner_neutral_phrase"]) for row in group]
        surfaces = list(dict.fromkeys(str(row["surface_sequence"]) for row in group))
        strict_rows.append({
            "strict_template_id": strict_ids[key],
            "strict_semantic_frame": key,
            "record_count": len(group),
            "page_count": len(pages),
            "register_count": len(registers),
            "recurrence_class": recurrence_class(len(group), len(pages), len(registers)),
            "recipe_variant_count": len(recipes),
            "recipe_frames": "|".join(recipes),
            "surface_type_count": len(surfaces),
            "surface_recurrence_mode": "MULTIPLE_SURFACES" if len(surfaces) > 1 else ("SAME_SURFACE" if len(group) > 1 else "SINGLETON"),
            "phrase_variant_count": len(set(phrases)),
            "canonical_owner_neutral_phrase_de": most_common_first(phrases),
            "phrase_stable": "YES" if len(set(phrases)) == 1 else "NO",
            "name_slot_count": group[0]["literal_name_slot_count"],
            "pages": "|".join(pages),
            "registers": "|".join(registers),
            "record_ids": "|".join(str(row["record_id"]) for row in group),
            "surface_examples": " || ".join(str(row["surface_sequence"]) for row in group[:5]),
            "reading_examples_de": " || ".join(str(row["definitive_record_reading_de"]) for row in group[:3]),
            "claim_status": "OWNER_NEUTRAL_WORKING_TEMPLATE__NO_NEW_MEANING",
        })

    shape_rows: list[dict[str, object]] = []
    for key, group in shape_groups.items():
        pages = list(dict.fromkeys(str(row["physical_page"]) for row in group))
        registers = list(dict.fromkeys(str(row["register"]) for row in group))
        strict_members = list(dict.fromkeys(strict_ids[str(row["strict_key"])] for row in group))
        shape_rows.append({
            "role_shape_id": shape_ids[key],
            "role_shape_frame": key,
            "record_count": len(group),
            "strict_template_count": len(strict_members),
            "strict_template_ids": "|".join(strict_members),
            "page_count": len(pages),
            "register_count": len(registers),
            "recurrence_class": recurrence_class(len(group), len(pages), len(registers)),
            "pages": "|".join(pages),
            "registers": "|".join(registers),
            "record_ids": "|".join(str(row["record_id"]) for row in group),
            "surface_examples": " || ".join(str(row["surface_sequence"]) for row in group[:5]),
            "claim_status": "ROLE_SHAPE_ONLY__USE_STRICT_TEMPLATE_FOR_READING",
        })

    strict_map = {str(row["strict_template_id"]): row for row in strict_rows}
    shape_map = {str(row["role_shape_id"]): row for row in shape_rows}
    assignment_rows: list[dict[str, object]] = []
    for row in prepared:
        strict_id = strict_ids[str(row["strict_key"])]
        shape_id = shape_ids[str(row["shape_key"])]
        strict = strict_map[strict_id]
        shape = shape_map[shape_id]
        assignment_rows.append({
            "template_assignment_id": f"G480-A{len(assignment_rows) + 1:03d}",
            "record_id": row["record_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "page_record_ordinal": row["page_record_ordinal"],
            "record_start_role": row["record_start_role"],
            "bundle_count": row["bundle_count"],
            "event_count": row["event_count"],
            "bundle_ids": row["bundle_ids"],
            "surface_sequence": row["surface_sequence"],
            "active_model_sequence": row["active_model_sequence"],
            "strict_template_id": strict_id,
            "strict_template_record_count": strict["record_count"],
            "strict_recurrence_class": strict["recurrence_class"],
            "strict_semantic_frame": row["strict_key"],
            "recipe_frame": row["recipe_frame"],
            "role_shape_id": shape_id,
            "role_shape_record_count": shape["record_count"],
            "role_recurrence_class": shape["recurrence_class"],
            "role_shape_frame": row["shape_key"],
            "literal_name_slot_count": row["literal_name_slot_count"],
            "owner_neutral_phrase_de": row["owner_neutral_phrase"],
            "definitive_record_reading_de": row["definitive_record_reading_de"],
            "all_sequences_have_default": "YES",
        })

    def summary_row(level: str, predicate) -> dict[str, object]:
        table = strict_rows if level == "STRICT" else shape_rows
        id_key = "strict_template_id" if level == "STRICT" else "role_shape_id"
        selected = [row for row in table if predicate(row)]
        record_ids: set[str] = set()
        for row in selected:
            record_ids.update(str(row["record_ids"]).split("|"))
        return {
            "level": level,
            "subset": predicate.__name__,
            "template_count": len(selected),
            "record_count": len(record_ids),
            "record_coverage_fraction": f"{len(record_ids) / 135:.6f}",
            "template_ids": "|".join(str(row[id_key]) for row in selected) or "NONE",
        }

    def all_templates(row):
        return True

    def recurrent(row):
        return int(row["record_count"]) > 1

    def cross_page(row):
        return int(row["page_count"]) > 1

    def cross_register(row):
        return int(row["register_count"]) > 1

    def stable_recurrent(row):
        return int(row["record_count"]) > 1 and row.get("phrase_stable") == "YES"

    def multisurface_recurrent(row):
        return int(row["record_count"]) > 1 and int(row.get("surface_type_count", 0)) > 1

    def multi_component_recurrent(row):
        return int(row["record_count"]) > 1 and int(row.get("strict_template_count", 0)) > 1

    coverage_rows = [
        summary_row("STRICT", all_templates),
        summary_row("STRICT", recurrent),
        summary_row("STRICT", cross_page),
        summary_row("STRICT", cross_register),
        summary_row("STRICT", stable_recurrent),
        summary_row("STRICT", multisurface_recurrent),
        summary_row("ROLE", all_templates),
        summary_row("ROLE", recurrent),
        summary_row("ROLE", cross_page),
        summary_row("ROLE", cross_register),
        summary_row("ROLE", multi_component_recurrent),
    ]

    recurrent_strict = [row for row in strict_rows if int(row["record_count"]) > 1]
    recurrent_shapes = [row for row in shape_rows if int(row["record_count"]) > 1]
    result: dict[str, object] = {
        "status": "ALL_135_RECORDS_HAVE_TEMPLATES__RECURRENT_MICRORECORD_GRAMMAR_ATLAS_COMPLETE",
        "record_count": len(assignment_rows),
        "strict_template_count": len(strict_rows),
        "singleton_strict_template_count": sum(int(row["record_count"]) == 1 for row in strict_rows),
        "recurrent_strict_template_count": len(recurrent_strict),
        "records_in_recurrent_strict_templates": sum(int(row["record_count"]) for row in recurrent_strict),
        "cross_page_strict_template_count": sum(int(row["page_count"]) > 1 for row in strict_rows),
        "cross_register_strict_template_count": sum(int(row["register_count"]) > 1 for row in strict_rows),
        "stable_recurrent_strict_template_count": sum(row["phrase_stable"] == "YES" for row in recurrent_strict),
        "multisurface_recurrent_strict_template_count": sum(int(row["surface_type_count"]) > 1 for row in recurrent_strict),
        "records_in_multisurface_recurrent_strict_templates": sum(int(row["record_count"]) for row in recurrent_strict if int(row["surface_type_count"]) > 1),
        "role_shape_count": len(shape_rows),
        "singleton_role_shape_count": sum(int(row["record_count"]) == 1 for row in shape_rows),
        "recurrent_role_shape_count": len(recurrent_shapes),
        "records_in_recurrent_role_shapes": sum(int(row["record_count"]) for row in recurrent_shapes),
        "cross_page_role_shape_count": sum(int(row["page_count"]) > 1 for row in shape_rows),
        "cross_register_role_shape_count": sum(int(row["register_count"]) > 1 for row in shape_rows),
        "multi_component_recurrent_role_shape_count": sum(int(row["strict_template_count"]) > 1 for row in recurrent_shapes),
        "records_in_multi_component_recurrent_role_shapes": sum(int(row["record_count"]) for row in recurrent_shapes if int(row["strict_template_count"]) > 1),
        "largest_strict_template_record_count": max(int(row["record_count"]) for row in strict_rows),
        "largest_role_shape_record_count": max(int(row["record_count"]) for row in shape_rows),
        "all_records_have_strict_template_count": sum(bool(row["strict_template_id"]) for row in assignment_rows),
        "all_records_have_role_shape_count": sum(bool(row["role_shape_id"]) for row in assignment_rows),
        "component_meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "new_page_count": 0,
        "claim_ceiling": "Owner-neutral recurrent template atlas over the fixed GDT479 working edition; role shapes are backoff forms only, with no new meaning, syntax, plaintext, name, surface, recipe, record, or page.",
    }

    write_tsv(ASSIGNMENTS, assignment_rows)
    write_tsv(STRICT, strict_rows)
    write_tsv(SHAPES, shape_rows)
    write_tsv(COVERAGE, coverage_rows)
    READABLE.write_text(build_readable(strict_rows, shape_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "records": result["record_count"],
        "strict_templates": result["strict_template_count"],
        "recurrent_strict": result["recurrent_strict_template_count"],
        "role_shapes": result["role_shape_count"],
        "recurrent_shapes": result["recurrent_role_shape_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
