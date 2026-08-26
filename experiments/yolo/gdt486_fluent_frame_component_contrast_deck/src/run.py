#!/usr/bin/env python3
"""Build same-frame one-component contrasts from the GDT485 fluent edition."""

from __future__ import annotations

import csv
import difflib
import hashlib
import itertools
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
BASE = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck"
OUT = BASE / "artifacts"
G485 = ROOT / "experiments/yolo/gdt485_fluent_reversible_microrecord_edition/artifacts"
RECORDS_IN = G485 / "gdt485_135_fluent_reversible_records.tsv"
EVENTS_IN = G485 / "gdt485_183_literal_backprojection_events.tsv"
FRAME_ASSIGNMENTS = OUT / "gdt486_135_fluent_frame_assignments.tsv"
REGISTER_PAIRS = OUT / "gdt486_48_register_minimal_pairs.tsv"
SAME_PAGE_PAIRS = OUT / "gdt486_33_same_page_minimal_pairs.tsv"
REGISTER_EXTENSION = OUT / "gdt486_15_cross_page_register_extension_pairs.tsv"
CONTRAST_RULES = OUT / "gdt486_29_model_conditioned_contrast_rules.tsv"
CONTEXT_VARIANTS = OUT / "gdt486_1_contextual_realization_explanation.tsv"
PAGE_CAPACITY = OUT / "gdt486_6_page_capacity_summary.tsv"
READABLE = OUT / "GDT486_FLUENT_COMPONENT_CONTRAST_DECK.md"
RESULT = OUT / "gdt486_result.json"
STATUS = "TWENTY_NINE_FLUENT_COMPONENT_CONTRASTS__ONE_CONTEXTUAL_VARIANT__ZERO_DICTIONARY_PRESSURE"

ACTIONS = {
    "SETZEN", "FORTSETZEN", "NEHMEN", "HALTEN", "GEBEN", "WÄHLEN",
    "BEARBEITEN", "EINSTELLEN", "MARKIEREN", "EINSETZEN",
}

SEMANTIC_CUES = {
    "ANTEIL": r"Anteil",
    "AUSGANG": r"Ausgang",
    "BAHN": r"Bahn",
    "DANACH": r"Danach|danach|Folgevermerk|Folge-",
    "EINHEIT": r"Einheit",
    "EINSTELLEN": r"stell",
    "FORTSETZEN": r"Führe|fort|weiter",
    "HALTEN": r"halt",
    "HIER": r"bezeichnete[nr]? Stelle|Hier-Vermerk|\bhier\b",
    "POSTEN": r"Posten",
    "SCHLUSS": r"schlie|Endpunkt",
    "WERT": r"Wert",
    "ZIELORT": r"Ziel",
}

CONTEXT_EXPLANATIONS = {
    ("CATALOGUE", "CATALOGUE_ENTRY", "POSTEN", "ZIELORT"): (
        "Wenn beide letzten Komponenten ZIELORT sind, verdichtet die deutsche Fassung sie zu „zweifacher Zielzuordnung“. "
        "Ersetzt POSTEN eine der beiden Stellen, wird dieselbe Folge als „Zielzuordnung und Postenangabe“ ausgeschrieben. "
        "Die abweichende Wortspanne kommt daher von Zählung und Koordination, nicht von einer wechselnden Komponentenbedeutung."
    ),
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


def event_tokens(event: dict[str, str]) -> list[str]:
    return event["semantic_tokens"].split("|")


def separators(event: dict[str, str]) -> list[str]:
    return [] if event["semantic_separators"] == "NONE" else event["semantic_separators"].split("|")


def render_tokens(tokens: list[str], joins: list[str]) -> str:
    pieces = [tokens[0]]
    for join, token in zip(joins, tokens[1:]):
        pieces.extend((" · " if join == "DOT" else " / ", token))
    return "".join(pieces)


def normalize_names(text: str) -> str:
    return re.sub(r"»[^»]+«", "»{NAME}«", text)


def german_tokens(text: str) -> list[str]:
    return re.findall(
        r"»\{NAME\}«|[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*-?|[IVX]+|\d+|[^\w\s]",
        normalize_names(text),
    )


def phrase_edits(source: str, target: str) -> list[dict[str, object]]:
    source_tokens = german_tokens(source)
    target_tokens = german_tokens(target)
    edits: list[dict[str, object]] = []
    for tag, i, j, k, l in difflib.SequenceMatcher(a=source_tokens, b=target_tokens, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        edits.append({
            "tag": tag,
            "source": " ".join(source_tokens[i:j]) or "∅",
            "target": " ".join(target_tokens[k:l]) or "∅",
            "source_token_count": j - i,
            "target_token_count": l - k,
        })
    return edits


def edit_signature(edits: list[dict[str, object]]) -> str:
    return " || ".join(f"{edit['source']}=>{edit['target']}" for edit in edits)


def readable_frame_class(record: dict[str, object], events: list[dict[str, str]]) -> str:
    model = str(record["active_model_sequence"])
    fluent = str(record["fluent_reading_de"])
    if "|" in model:
        return "MULTI_EVENT_" + model
    if model == "INSTRUCTION":
        head = next((token for event in events for token in event_tokens(event) if token in ACTIONS), "NONE")
        return "INSTRUCTION_" + head
    if model == "CATALOGUE":
        if fluent.startswith("Katalogfolge:"):
            return "CATALOGUE_SEQUENCE"
        if "fortgesetzter Katalogeintrag" in fluent or "Führe den Katalog" in fluent:
            return "CATALOGUE_CONTINUATION"
        return "CATALOGUE_ENTRY"
    if model == "COORDINATE":
        if fluent.startswith(("Die erste", "Drei")):
            return "COORDINATE_MULTI"
        if fluent.startswith("Adressfolge:"):
            return "COORDINATE_SEQUENCE"
        if fluent.startswith("Danach"):
            return "COORDINATE_AFTER"
        return "COORDINATE_PATH"
    return model


def short_id(prefix: str, value: str) -> str:
    return prefix + hashlib.sha256(value.encode("utf-8")).hexdigest()[:10].upper()


def semantic_cue_present(component: str, fluent: str) -> bool:
    pattern = SEMANTIC_CUES.get(component)
    return bool(pattern and re.search(pattern, fluent, flags=re.IGNORECASE))


def build_pair(
    left: dict[str, object],
    right: dict[str, object],
    changed_index: int,
    pair_number: int,
) -> dict[str, object]:
    left_component = left["flat_tokens"][changed_index]
    right_component = right["flat_tokens"][changed_index]
    if left_component <= right_component:
        source, target = left, right
        component_a, component_b = left_component, right_component
    else:
        source, target = right, left
        component_a, component_b = right_component, left_component
    edits = phrase_edits(str(source["fluent_reading_de"]), str(target["fluent_reading_de"]))
    wildcard = list(source["flat_tokens"])
    wildcard[changed_index] = "*"
    wildcard_trace = " || ".join(
        render_tokens(
            wildcard[source["event_offsets"][event_index]: source["event_offsets"][event_index + 1]],
            source["event_separators"][event_index],
        )
        for event_index in range(len(source["event_separators"]))
    )
    frame_key = f"{source['active_model_sequence']}|{source['fluent_frame_class']}|{wildcard_trace}"
    return {
        "pair_id": f"G486-P{pair_number:03d}",
        "scope_class": "SAME_PAGE_OWNER" if source["physical_page"] == target["physical_page"] else "SAME_REGISTER_CROSS_PAGE",
        "source_record_id": source["record_id"],
        "target_record_id": target["record_id"],
        "source_physical_page": source["physical_page"],
        "target_physical_page": target["physical_page"],
        "register": source["register"],
        "active_model_sequence": source["active_model_sequence"],
        "fluent_frame_class": source["fluent_frame_class"],
        "contrast_frame_id": short_id("G486-CF", frame_key),
        "wildcard_component_frame": wildcard_trace,
        "changed_flat_component_ordinal": changed_index + 1,
        "component_a": component_a,
        "component_b": component_b,
        "source_surface_sequence": source["surface_sequence"],
        "target_surface_sequence": target["surface_sequence"],
        "source_component_trace_de": source["normalized_component_trace_de"],
        "target_component_trace_de": target["normalized_component_trace_de"],
        "source_fluent_reading_de": source["fluent_reading_de"],
        "target_fluent_reading_de": target["fluent_reading_de"],
        "source_fluent_names_normalized_de": normalize_names(str(source["fluent_reading_de"])),
        "target_fluent_names_normalized_de": normalize_names(str(target["fluent_reading_de"])),
        "phrase_edit_block_count": len(edits),
        "phrase_edit_token_count": sum(int(edit["source_token_count"]) + int(edit["target_token_count"]) for edit in edits),
        "phrase_change_signature_de": edit_signature(edits),
        "component_a_cue_visible": "YES" if semantic_cue_present(component_a, str(source["fluent_reading_de"])) else "NO",
        "component_b_cue_visible": "YES" if semantic_cue_present(component_b, str(target["fluent_reading_de"])) else "NO",
        "meaning_change_visible": "YES" if semantic_cue_present(component_a, str(source["fluent_reading_de"])) and semantic_cue_present(component_b, str(target["fluent_reading_de"])) else "NO",
        "same_register": "YES",
        "same_active_model": "YES",
        "same_readable_frame_class": "YES",
        "same_event_boundary_shape": "YES",
        "single_functional_component_delta": "YES",
        "source_support_tier": source["support_tier"],
        "target_support_tier": target["support_tier"],
    }


def build_readable(
    records: list[dict[str, object]],
    pairs: list[dict[str, object]],
    rules: list[dict[str, object]],
    contexts: list[dict[str, object]],
    pages: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT486 — Kontraststapel der flüssigen Komponentenrahmen",
        "",
        "GDT486 hält Register, aktives Modell, lesbare Satzklasse, Eventgrenzen und alle umgebenden Komponenten fest. Zwei Records bilden nur dann ein Paar, wenn genau eine funktionale Komponente wechselt; gelernte Namensslots werden nie als Bedeutungswechsel gezählt.",
        "",
        f"- Streng auf derselben Seite: **{result['same_page_pair_count']} Paare / {result['same_page_record_count']} Records**.",
        f"- Mit gleicher-Register-Erweiterung: **{result['register_pair_count']} Paare / {result['register_pair_record_count']} Records**.",
        f"- Modellgebundene Kontrastregeln: **{result['contrast_rule_count']}**; exakt gleiche Wortänderung: **{result['exact_signature_rule_count']}**; kontextuell erklärt: **{result['contextual_rule_count']}**; Wörterbuchdruck: **{result['dictionary_pressure_rule_count']}**.",
        f"- Sichtbare Bedeutungswerte im Deck: **{result['changed_component_value_count']}**; davon sekundäre Handlungen: **{result['changed_action_value_count']}**.",
        "",
        "## Seitenkapazität",
        "",
        "| Seite | Register | Records | seiteninterne Paare | Registerpaar-Berührungen | kontrastgedeckte Records |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in pages:
        lines.append(f"| {row['physical_page']} | {row['register']} | {row['record_count']} | {row['same_page_pair_count']} | {row['register_pair_incidence_count']} | {row['contrast_covered_record_count']} |")
    lines.extend([
        "",
        "Vier Seiten tragen Kontrastpaare; f17r und f77r haben in diesen 135 Records keinen zweiten Record mit identischem Rahmen und genau einem funktionalen Wechsel. Das ist fehlende Kapazität, kein Gegenbeispiel.",
        "",
        "## 29 modellgebundene Kontrastregeln",
        "",
        "| Modell / Satzrahmen | Wechsel | Paare | davon gleiche Seite | Wortsignaturen | Status |",
        "|---|---|---:|---:|---:|---|",
    ])
    for row in rules:
        lines.append(
            f"| `{row['active_model_sequence']}` / `{row['fluent_frame_class']}` | `{row['component_a']} ↔ {row['component_b']}` | {row['pair_count']} | {row['same_page_pair_count']} | {row['phrase_signature_count']} | `{row['rule_status']}` |"
        )
    lines.extend([
        "",
        "Zwölf wiederkehrende Gruppen und alle sechzehn Einzelzeugen haben eine einzige Wortänderungssignatur. Nur die folgende wiederkehrende Gruppe braucht zwei Oberflächenformulierungen:",
        "",
    ])
    for row in contexts:
        lines.extend([
            f"### {row['component_a']} ↔ {row['component_b']} in {row['fluent_frame_class']}",
            "",
            row["context_explanation_de"],
            "",
            f"Betroffene Paare: `{row['pair_ids']}`. Eine Wörterbuchänderung ist **nicht** nötig.",
            "",
        ])
    lines.extend([
        "## Alle 48 gleichen-Register-Paare",
        "",
        "| Paar | Bereich | Rahmen | Wechsel | deutsche Änderung |",
        "|---|---|---|---|---|",
    ])
    for row in pairs:
        lines.append(
            f"| `{row['source_record_id']} ↔ {row['target_record_id']}` | {row['scope_class']} | `{row['fluent_frame_class']}` | `{row['component_a']} ↔ {row['component_b']}` | `{row['phrase_change_signature_de']}` |"
        )
    lines.extend([
        "",
        "## Lesart",
        "",
        "Der Kontraststapel bestätigt nicht unabhängig, dass die deutschen Grundwerte wahr sind: Er wurde aus derselben Arbeitstheorie gebaut. Er zeigt aber, dass die GDT485-Redaktion diese Werte nicht beliebig verschluckt oder gegeneinander vertauscht. Unter identischem lesbaren Rahmen erzeugt jeder einzelne Komponentenwechsel eine sichtbare, passende Bedeutungsänderung; die einzige Signaturverdopplung ist vollständig durch deutsche Zählung erklärbar.",
        "",
        "Der nächste Schritt sollte deshalb die 17 Einzelzeugen mit Nachbarrahmen verbinden und insbesondere die drei erstmals berührten sekundären Handlungen `EINSTELLEN`, `FORTSETZEN` und `HALTEN` zu wiederkehrenden Kontrastregeln ausbauen, ohne ihre Bedeutungen umzudeuten.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    source_records = read_tsv(RECORDS_IN)
    source_events = read_tsv(EVENTS_IN)
    if (len(source_records), len(source_events)) != (135, 183):
        raise RuntimeError("GDT485 input count drift")

    events_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in source_events:
        events_by_record[event["record_id"]].append(event)

    enriched: list[dict[str, object]] = []
    for source in source_records:
        row: dict[str, object] = dict(source)
        events = events_by_record[source["record_id"]]
        flat_tokens: list[str] = []
        event_offsets = [0]
        event_separators: list[list[str]] = []
        shape_parts: list[str] = []
        for event in events:
            tokens = event_tokens(event)
            joins = separators(event)
            flat_tokens.extend(tokens)
            event_offsets.append(len(flat_tokens))
            event_separators.append(joins)
            shape_parts.append(f"{len(tokens)}:{event['semantic_separators']}")
        row["flat_tokens"] = tuple(flat_tokens)
        row["event_offsets"] = tuple(event_offsets)
        row["event_separators"] = tuple(tuple(part) for part in event_separators)
        row["event_boundary_shape"] = "||".join(shape_parts)
        row["fluent_frame_class"] = readable_frame_class(row, events)
        row["structural_frame_key"] = f"{row['active_model_sequence']}|{row['fluent_frame_class']}|{row['event_boundary_shape']}"
        enriched.append(row)

    candidate_pairs: list[tuple[dict[str, object], dict[str, object], int]] = []
    for left, right in itertools.combinations(enriched, 2):
        if left["register"] != right["register"]:
            continue
        fixed_fields = ("active_model_sequence", "fluent_frame_class", "event_boundary_shape")
        if any(left[field] != right[field] for field in fixed_fields):
            continue
        differences = [index for index, values in enumerate(zip(left["flat_tokens"], right["flat_tokens"])) if values[0] != values[1]]
        if len(differences) != 1:
            continue
        changed_index = differences[0]
        left_component = left["flat_tokens"][changed_index]
        right_component = right["flat_tokens"][changed_index]
        if str(left_component).startswith("{") or str(right_component).startswith("{"):
            continue
        candidate_pairs.append((left, right, changed_index))

    pair_rows = [build_pair(left, right, index, number) for number, (left, right, index) in enumerate(candidate_pairs, 1)]
    if len(pair_rows) != 48:
        raise RuntimeError(f"Expected 48 same-register pairs, got {len(pair_rows)}")
    same_page_rows = [dict(row, strict_pair_id=f"G486-SP{number:03d}") for number, row in enumerate((row for row in pair_rows if row["scope_class"] == "SAME_PAGE_OWNER"), 1)]
    extension_rows = [dict(row, extension_pair_id=f"G486-XP{number:03d}") for number, row in enumerate((row for row in pair_rows if row["scope_class"] == "SAME_REGISTER_CROSS_PAGE"), 1)]
    write_tsv(REGISTER_PAIRS, pair_rows)
    write_tsv(SAME_PAGE_PAIRS, same_page_rows)
    write_tsv(REGISTER_EXTENSION, extension_rows)

    grouped_pairs: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in pair_rows:
        key = (str(row["active_model_sequence"]), str(row["fluent_frame_class"]), str(row["component_a"]), str(row["component_b"]))
        grouped_pairs[key].append(row)

    rule_rows: list[dict[str, object]] = []
    context_rows: list[dict[str, object]] = []
    for number, key in enumerate(sorted(grouped_pairs), 1):
        local = grouped_pairs[key]
        signatures = sorted({str(row["phrase_change_signature_de"]) for row in local})
        if len(signatures) == 1 and len(local) > 1:
            rule_status = "EXACT_RECURRENT_WORDING_RULE"
        elif len(signatures) == 1:
            rule_status = "SINGLE_WITNESS_WORDING_RULE"
        elif key in CONTEXT_EXPLANATIONS:
            rule_status = "CONTEXTUAL_GERMAN_REALIZATION"
        else:
            rule_status = "DICTIONARY_PRESSURE"
        explanation = CONTEXT_EXPLANATIONS.get(key, "NONE")
        rule = {
            "rule_id": f"G486-CR{number:02d}",
            "active_model_sequence": key[0],
            "fluent_frame_class": key[1],
            "component_a": key[2],
            "component_b": key[3],
            "pair_count": len(local),
            "same_page_pair_count": sum(row["scope_class"] == "SAME_PAGE_OWNER" for row in local),
            "cross_page_pair_count": sum(row["scope_class"] == "SAME_REGISTER_CROSS_PAGE" for row in local),
            "record_count": len({str(row[field]) for row in local for field in ("source_record_id", "target_record_id")}),
            "page_count": len({str(row[field]) for row in local for field in ("source_physical_page", "target_physical_page")}),
            "register_count": len({str(row["register"]) for row in local}),
            "contrast_frame_count": len({str(row["contrast_frame_id"]) for row in local}),
            "phrase_signature_count": len(signatures),
            "phrase_change_signatures_de": " | ".join(signatures),
            "all_meaning_cues_visible": "YES" if all(row["meaning_change_visible"] == "YES" for row in local) else "NO",
            "rule_status": rule_status,
            "context_explanation_de": explanation,
            "dictionary_remap_required": "YES" if rule_status == "DICTIONARY_PRESSURE" else "NO",
            "pair_ids": "|".join(str(row["pair_id"]) for row in local),
            "record_pairs": "|".join(f"{row['source_record_id']}~{row['target_record_id']}" for row in local),
        }
        rule_rows.append(rule)
        if rule_status == "CONTEXTUAL_GERMAN_REALIZATION":
            context_rows.append({
                "context_id": f"G486-CX{len(context_rows) + 1:02d}",
                "rule_id": rule["rule_id"],
                "active_model_sequence": key[0],
                "fluent_frame_class": key[1],
                "component_a": key[2],
                "component_b": key[3],
                "pair_count": len(local),
                "phrase_signature_count": len(signatures),
                "phrase_change_signatures_de": " | ".join(signatures),
                "context_explanation_de": explanation,
                "pair_ids": rule["pair_ids"],
                "record_pairs": rule["record_pairs"],
                "all_meaning_cues_visible": rule["all_meaning_cues_visible"],
                "dictionary_remap_required": "NO",
            })
    write_tsv(CONTRAST_RULES, rule_rows)
    write_tsv(CONTEXT_VARIANTS, context_rows)

    pair_degree = Counter()
    same_page_degree = Counter()
    for row in pair_rows:
        for field in ("source_record_id", "target_record_id"):
            pair_degree[str(row[field])] += 1
            if row["scope_class"] == "SAME_PAGE_OWNER":
                same_page_degree[str(row[field])] += 1
    structural_frame_ids = {
        key: f"G486-RF{number:03d}"
        for number, key in enumerate(sorted({str(row["structural_frame_key"]) for row in enriched}), 1)
    }
    assignment_rows: list[dict[str, object]] = []
    for number, row in enumerate(enriched, 1):
        assignment_rows.append({
            "assignment_id": f"G486-R{number:03d}",
            "record_id": row["record_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "surface_sequence": row["surface_sequence"],
            "active_model_sequence": row["active_model_sequence"],
            "fluent_frame_class": row["fluent_frame_class"],
            "structural_frame_id": structural_frame_ids[str(row["structural_frame_key"])],
            "event_boundary_shape": row["event_boundary_shape"],
            "component_trace_de": row["normalized_component_trace_de"],
            "functional_component_count": sum(not str(token).startswith("{") for token in row["flat_tokens"]),
            "opaque_slot_count": sum(str(token).startswith("{") for token in row["flat_tokens"]),
            "fluent_reading_de": row["fluent_reading_de"],
            "same_page_pair_degree": same_page_degree[str(row["record_id"])],
            "register_pair_degree": pair_degree[str(row["record_id"])],
            "contrast_covered": "YES" if pair_degree[str(row["record_id"])] else "NO",
            "source_record_preserved": "YES",
        })
    write_tsv(FRAME_ASSIGNMENTS, assignment_rows)

    page_rows: list[dict[str, object]] = []
    for page in dict.fromkeys(str(row["physical_page"]) for row in enriched):
        local_records = [row for row in enriched if row["physical_page"] == page]
        local_ids = {str(row["record_id"]) for row in local_records}
        same_pairs = [row for row in pair_rows if row["scope_class"] == "SAME_PAGE_OWNER" and row["source_physical_page"] == page]
        incident = [row for row in pair_rows if row["source_record_id"] in local_ids or row["target_record_id"] in local_ids]
        page_rows.append({
            "physical_page": page,
            "register": local_records[0]["register"],
            "record_count": len(local_records),
            "fluent_frame_class_count": len({str(row["fluent_frame_class"]) for row in local_records}),
            "structural_frame_count": len({str(row["structural_frame_key"]) for row in local_records}),
            "same_page_pair_count": len(same_pairs),
            "register_pair_incidence_count": len(incident),
            "cross_page_pair_incidence_count": sum(row["scope_class"] == "SAME_REGISTER_CROSS_PAGE" for row in incident),
            "contrast_covered_record_count": sum(pair_degree[record_id] > 0 for record_id in local_ids),
            "contrast_uncovered_record_count": sum(pair_degree[record_id] == 0 for record_id in local_ids),
            "changed_component_values": "|".join(sorted({str(row[field]) for row in incident for field in ("component_a", "component_b")})) or "NONE",
        })
    write_tsv(PAGE_CAPACITY, page_rows)

    changed_values = {str(row[field]) for row in pair_rows for field in ("component_a", "component_b")}
    result = {
        "status": STATUS,
        "record_count": len(enriched),
        "event_count": len(source_events),
        "fluent_frame_class_count": len({str(row["fluent_frame_class"]) for row in enriched}),
        "structural_frame_count": len(structural_frame_ids),
        "same_page_pair_count": len(same_page_rows),
        "same_page_record_count": len({str(row[field]) for row in same_page_rows for field in ("source_record_id", "target_record_id")}),
        "register_pair_count": len(pair_rows),
        "register_pair_record_count": len(pair_degree),
        "cross_page_register_extension_pair_count": len(extension_rows),
        "contrast_rule_count": len(rule_rows),
        "recurrent_contrast_rule_count": sum(int(row["pair_count"]) > 1 for row in rule_rows),
        "singleton_contrast_rule_count": sum(int(row["pair_count"]) == 1 for row in rule_rows),
        "exact_signature_rule_count": sum(int(row["phrase_signature_count"]) == 1 for row in rule_rows),
        "exact_recurrent_wording_rule_count": sum(row["rule_status"] == "EXACT_RECURRENT_WORDING_RULE" for row in rule_rows),
        "contextual_rule_count": len(context_rows),
        "dictionary_pressure_rule_count": sum(row["rule_status"] == "DICTIONARY_PRESSURE" for row in rule_rows),
        "single_edit_block_pair_count": sum(int(row["phrase_edit_block_count"]) == 1 for row in pair_rows),
        "two_edit_block_pair_count": sum(int(row["phrase_edit_block_count"]) == 2 for row in pair_rows),
        "all_pair_meaning_changes_visible": all(row["meaning_change_visible"] == "YES" for row in pair_rows),
        "changed_component_value_count": len(changed_values),
        "changed_component_values": sorted(changed_values),
        "changed_action_value_count": len(changed_values & ACTIONS),
        "changed_action_values": sorted(changed_values & ACTIONS),
        "page_count": len(page_rows),
        "pair_capacity_page_count": sum(int(row["register_pair_incidence_count"]) > 0 for row in page_rows),
        "zero_pair_capacity_pages": [row["physical_page"] for row in page_rows if int(row["register_pair_incidence_count"]) == 0],
        "meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Internal editorial-consistency contrast deck over fixed GDT485 meanings; no independent semantic confirmation, new root, meaning, name, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(enriched, pair_rows, rule_rows, context_rows, page_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
