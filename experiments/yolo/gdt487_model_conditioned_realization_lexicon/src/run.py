#!/usr/bin/env python3
"""Invert GDT486 contrasts into a model-conditioned German realization lexicon."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt487_model_conditioned_realization_lexicon"
OUT = BASE / "artifacts"
G486 = ROOT / "experiments/yolo/gdt486_fluent_frame_component_contrast_deck/artifacts"
G428 = ROOT / "experiments/yolo/gdt428_within_class_action_semantic_contrasts/artifacts"
G429 = ROOT / "experiments/yolo/gdt429_nonaction_core_semantic_contrasts/artifacts"
PAIRS_IN = G486 / "gdt486_48_register_minimal_pairs.tsv"
RULES_IN = G486 / "gdt486_29_model_conditioned_contrast_rules.tsv"
ASSIGNMENTS_IN = G486 / "gdt486_135_fluent_frame_assignments.tsv"
ACTION_CONTRASTS_IN = G428 / "gdt428_6_within_class_contrasts.tsv"
NONACTION_CONTRASTS_IN = G429 / "gdt429_13_nonaction_core_contrasts.tsv"
LEXICON = OUT / "gdt487_13_component_realization_lexicon.tsv"
MODEL_CELLS = OUT / "gdt487_39_component_model_cells.tsv"
REALIZATION_FORMS = OUT / "gdt487_29_observed_realization_forms.tsv"
SINGLETON_TRIANGULATION = OUT / "gdt487_16_singleton_triangulations.tsv"
EXTERNAL_ANCHORS = OUT / "gdt487_3_external_contrast_anchors.tsv"
LOCAL_EDGES = OUT / "gdt487_13_local_recurrent_edges.tsv"
PAGE_SUPPORT = OUT / "gdt487_6_page_realization_support.tsv"
READABLE = OUT / "GDT487_MODEL_CONDITIONED_REALIZATION_LEXICON.md"
RESULT = OUT / "gdt487_result.json"
STATUS = "THIRTEEN_VALUE_REALIZATION_LEXICON__FOURTEEN_SINGLETON_CYCLES__TWO_ENDPOINT_ANCHORS"

MODELS = ("CATALOGUE", "COORDINATE", "INSTRUCTION")

COMPONENT_META = {
    "ANTEIL": ("AIN", "ARGUMENT"),
    "AUSGANG": ("AR", "RELATION"),
    "BAHN": ("AIR", "RELATION"),
    "DANACH": ("OT", "ORDER_CONTROL"),
    "EINHEIT": ("OR", "ARGUMENT"),
    "EINSTELLEN": ("T", "ACTION"),
    "FORTSETZEN": ("OL", "ORDER_CONTROL"),
    "HALTEN": ("SH", "ACTION"),
    "HIER": ("LOCAL_HIER", "LOCAL_SCOPE"),
    "POSTEN": ("Y", "ARGUMENT"),
    "SCHLUSS": ("LICENSED_CLOSE_HULL", "LOCAL_SCOPE"),
    "WERT": ("AIIN", "ARGUMENT"),
    "ZIELORT": ("AL", "RELATION"),
}

# Each contrast-side witness must match exactly one form for its component/model.
FORM_PATTERNS = [
    ("ANTEIL", "CATALOGUE", "Anteilsangabe", r"Anteilsangabe"),
    ("ANTEIL", "CATALOGUE", "Anteils- (Koordination)", r"Anteils-(?=\s+und)"),
    ("ANTEIL", "COORDINATE", "Sektoranteil", r"Sektoranteil"),
    ("ANTEIL", "INSTRUCTION", "Drogenanteil", r"Drogenanteil"),
    ("AUSGANG", "CATALOGUE", "Ausgangszuordnung", r"Ausgangszuordnung"),
    ("AUSGANG", "COORDINATE", "Ausgangsposition", r"Ausgangsposition"),
    ("AUSGANG", "INSTRUCTION", "ausgehend von der Ausgangsposition", r"ausgehend von der Ausgangsposition"),
    ("AUSGANG", "INSTRUCTION", "von der Ausgangsposition aus", r"von der Ausgangsposition aus"),
    ("BAHN", "CATALOGUE", "Bahnvermerk", r"Bahnvermerk"),
    ("DANACH", "CATALOGUE", "Folgevermerk", r"Folgevermerk"),
    ("EINHEIT", "CATALOGUE", "Einheitsangabe", r"Einheitsangabe"),
    ("EINSTELLEN", "INSTRUCTION", "stelle … ein", r"stelle beide ein"),
    ("FORTSETZEN", "INSTRUCTION", "Führe das Setzen … fort", r"Führe das Setzen"),
    ("HALTEN", "INSTRUCTION", "halte ihn", r"halte ihn"),
    ("HIER", "CATALOGUE", "Hier-Vermerk", r"Hier-Vermerk"),
    ("HIER", "COORDINATE", "bezeichnete Stelle", r"bezeichneten Stelle"),
    ("HIER", "INSTRUCTION", "an der bezeichneten Stelle", r"an der bezeichneten Stelle"),
    ("POSTEN", "CATALOGUE", "Postenangabe", r"Postenangabe"),
    ("POSTEN", "COORDINATE", "Positionsposten", r"Positionsposten"),
    ("POSTEN", "INSTRUCTION", "Positionsposten", r"Positionsposten"),
    ("SCHLUSS", "INSTRUCTION", "schließe den Schritt", r"schließe den Schritt"),
    ("WERT", "CATALOGUE", "Wertangabe", r"Wertangabe"),
    ("WERT", "COORDINATE", "Positionswert", r"Positionswert"),
    ("WERT", "INSTRUCTION", "Mengenwert", r"Mengenwert"),
    ("WERT", "INSTRUCTION", "Positionswert", r"Positionswert"),
    ("ZIELORT", "CATALOGUE", "Zielzuordnung", r"Zielzuordnung"),
    ("ZIELORT", "COORDINATE", "Zielposition", r"Zielposition"),
    ("ZIELORT", "INSTRUCTION", "am Zielgefäß", r"am Zielgefäß"),
    ("ZIELORT", "INSTRUCTION", "zur Zielposition", r"zur Zielposition"),
]

ANCHOR_SPECS = {
    "DANACH": {
        "source_experiment": "GDT429",
        "source_pair": "OL~OT",
        "anchor_value": "FORTSETZEN",
        "anchor_root": "OL",
        "expected_frames": 14,
        "bridge_class": "DIRECT_TO_LOCAL_RECURRENT_GRAPH",
    },
    "EINSTELLEN": {
        "source_experiment": "GDT428",
        "source_pair": "T~R",
        "anchor_value": "MARKIEREN",
        "anchor_root": "R",
        "expected_frames": 11,
        "bridge_class": "EXTERNAL_ACTION_ENDPOINT_ANCHOR",
    },
    "HALTEN": {
        "source_experiment": "GDT428",
        "source_pair": "SH~CHD",
        "anchor_value": "BEARBEITEN",
        "anchor_root": "CHD",
        "expected_frames": 14,
        "bridge_class": "EXTERNAL_ACTION_ENDPOINT_ANCHOR",
    },
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


def shortest_path(graph: dict[str, set[str]], start: str, target: str) -> list[str] | None:
    queue: deque[list[str]] = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == target:
            return path
        for neighbour in sorted(graph.get(node, set()) - seen):
            seen.add(neighbour)
            queue.append([*path, neighbour])
    return None


def form_sort_key(form: str) -> tuple[int, str]:
    return (len(form), form)


def build_readable(
    lexicon: list[dict[str, object]],
    cells: list[dict[str, object]],
    triangulations: list[dict[str, object]],
    anchors: list[dict[str, object]],
    result: dict[str, object],
) -> str:
    lines = [
        "# GDT487 — modellgebundenes deutsches Realisierungslexikon",
        "",
        "GDT487 dreht die 48 GDT486-Paare um: Nicht mehr die Kante, sondern jeder einzelne Bedeutungswert ist der Einstieg. Jede beobachtete deutsche Form ist an konkrete Kontrastrecords gebunden; unbelegte Modellzellen bleiben `OPEN`.",
        "",
        f"- Bedeutungswerte: **{result['component_value_count']}**.",
        f"- Komponenten×Modell-Zellen: **{result['observed_model_cell_count']} beobachtet / {result['open_model_cell_count']} offen**.",
        f"- Unterschiedliche beobachtete Realisierungsformen: **{result['realization_form_count']}** aus **{result['realization_witness_count']}** Record×Wert-Zeugen.",
        f"- Einzelregeln: **{result['singleton_rule_count']}** = {result['local_cycle_triangulated_count']} lokale Zyklen + {result['external_cycle_triangulated_count']} externer Brückenzyklus + {result['endpoint_anchored_only_count']} nur am Endpunkt verankerte Regeln; völlig unverankert: **{result['unanchored_singleton_count']}**.",
        "",
        "## Lexikon der dreizehn Werte",
        "",
        "| Wert | Wurzel/Schicht | Klasse | Katalog | Koordinate | Anweisung | lokale Wiederholkanten | Anker |",
        "|---|---|---|---|---|---|---:|---|",
    ]
    for row in lexicon:
        catalogue = str(row["catalogue_forms_de"]).replace("|", "<br>")
        coordinate = str(row["coordinate_forms_de"]).replace("|", "<br>")
        instruction = str(row["instruction_forms_de"]).replace("|", "<br>")
        lines.append(
            f"| `{row['component_value']}` | `{row['portable_root_or_layer']}` | {row['component_class']} | {catalogue} | {coordinate} | {instruction} | {row['local_recurrent_degree']} | {row['anchor_class']} |"
        )
    lines.extend([
        "",
        "`OPEN` heißt nur, dass der enge GDT486-Kontraststapel in diesem Modell keine Form isoliert. Es ist keine Erlaubnis, eine Form zu erfinden und kein Gegenbeispiel gegen den Wert.",
        "",
        "## Die sechzehn Einzelregeln",
        "",
        "| Regel | Wechsel | Rahmen | Triangulation | Pfad/Anker |",
        "|---|---|---|---|---|",
    ])
    for row in triangulations:
        lines.append(
            f"| `{row['rule_id']}` | `{row['component_a']} ↔ {row['component_b']}` | `{row['fluent_frame_class']}` | `{row['triangulation_class']}` | {row['triangulation_path_de']} |"
        )
    lines.extend([
        "",
        "Dreizehn Einzelkanten besitzen bereits einen alternativen Weg ausschließlich durch die dreizehn wiederkehrenden GDT486-Regeln. `DANACH ↔ EINHEIT` erhält einen vollständigen Zyklus über GDT429s vierzehn exakte `DANACH ↔ FORTSETZEN`-Rahmen und den lokalen Weg von FORTSETZEN zu EINHEIT.",
        "",
        "`EINSTELLEN ↔ HIER` und `HALTEN ↔ ZIELORT` haben noch keinen zweiten lokalen Weg. Ihre Aktionsenden hängen aber nicht frei: GDT428 trägt EINSTELLEN über elf exakte T/R-Rahmen gegen MARKIEREN und HALTEN über vierzehn SH/CHD-Rahmen gegen BEARBEITEN. Diese beiden Regeln bleiben deshalb **endpoint-anchored**, nicht zyklisch geschlossen.",
        "",
        "## Drei geerbte Kontrastanker",
        "",
        "| Wert | alter Kontrast | exakte Rahmen | Partner | Rolle im Netz |",
        "|---|---|---:|---|---|",
    ])
    for row in anchors:
        lines.append(
            f"| `{row['component_value']}` | `{row['source_experiment']} {row['source_contrast_pair']}` | {row['shared_exact_substitution_frame_count']} | `{row['anchor_value']}` | `{row['bridge_class']}` |"
        )
    lines.extend([
        "",
        "## Konsequenz",
        "",
        "Das Realisierungslexikon sagt jetzt nicht mehr nur `ZIELORT`, sondern wo der Wert tatsächlich wie gesprochen wird: im Katalog als „Zielzuordnung“, in Koordinaten als „Zielposition“ und in Anweisungen als „zur Zielposition“ oder pharmazeutisch „am Zielgefäß“. Entsprechend trennt es `WERT` in Wertangabe, Positionswert und Mengenwert, ohne daraus drei Wörterbuchbedeutungen zu machen.",
        "",
        "Der nächste engste Schritt ist klar: Suche innerhalb der vorhandenen 135 Records nach je einem zweiten, nur leicht gelockerten Satzrahmen für EINSTELLEN und HALTEN. Die übrigen vierzehn Einzelregeln besitzen bereits einen alternativen Kontrastweg; globale Umdeutung wäre derzeit kontraproduktiv.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = read_tsv(PAIRS_IN)
    rules = read_tsv(RULES_IN)
    assignments = read_tsv(ASSIGNMENTS_IN)
    action_contrasts = read_tsv(ACTION_CONTRASTS_IN)
    nonaction_contrasts = read_tsv(NONACTION_CONTRASTS_IN)
    if (len(pairs), len(rules), len(assignments)) != (48, 29, 135):
        raise RuntimeError("GDT486 input count drift")

    assignment_map = {row["record_id"]: row for row in assignments}
    witnesses: dict[tuple[str, str], dict[str, str]] = {}
    for pair in pairs:
        witnesses[(pair["source_record_id"], pair["component_a"])] = {
            "record_id": pair["source_record_id"],
            "component_value": pair["component_a"],
            "physical_page": pair["source_physical_page"],
            "register": pair["register"],
            "active_model": pair["active_model_sequence"],
            "fluent_frame_class": pair["fluent_frame_class"],
            "fluent_reading_de": pair["source_fluent_reading_de"],
        }
        witnesses[(pair["target_record_id"], pair["component_b"])] = {
            "record_id": pair["target_record_id"],
            "component_value": pair["component_b"],
            "physical_page": pair["target_physical_page"],
            "register": pair["register"],
            "active_model": pair["active_model_sequence"],
            "fluent_frame_class": pair["fluent_frame_class"],
            "fluent_reading_de": pair["target_fluent_reading_de"],
        }
    if len(witnesses) != 56:
        raise RuntimeError(f"Expected 56 record×component witnesses, got {len(witnesses)}")

    pattern_rows = [
        {"component_value": component, "active_model": model, "canonical_realization_de": form, "pattern": pattern}
        for component, model, form, pattern in FORM_PATTERNS
    ]
    form_witnesses: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for witness in witnesses.values():
        candidates = [
            row for row in pattern_rows
            if row["component_value"] == witness["component_value"]
            and row["active_model"] == witness["active_model"]
            and re.search(row["pattern"], witness["fluent_reading_de"], flags=re.IGNORECASE)
        ]
        if len(candidates) != 1:
            raise RuntimeError(f"Realization match count {len(candidates)} for {witness}")
        pattern = candidates[0]
        matches = re.findall(pattern["pattern"], witness["fluent_reading_de"], flags=re.IGNORECASE)
        enriched = dict(witness)
        enriched["matched_surface_forms_de"] = "|".join(dict.fromkeys(matches))
        form_witnesses[(witness["component_value"], witness["active_model"], pattern["canonical_realization_de"])].append(enriched)

    form_rows: list[dict[str, object]] = []
    for number, key in enumerate(sorted(form_witnesses), 1):
        local = form_witnesses[key]
        form_rows.append({
            "form_id": f"G487-F{number:02d}",
            "component_value": key[0],
            "active_model": key[1],
            "canonical_realization_de": key[2],
            "witness_record_count": len(local),
            "witness_records": "|".join(sorted(row["record_id"] for row in local)),
            "page_count": len({row["physical_page"] for row in local}),
            "pages": "|".join(sorted({row["physical_page"] for row in local})),
            "register_count": len({row["register"] for row in local}),
            "registers": "|".join(sorted({row["register"] for row in local})),
            "fluent_frame_class_count": len({row["fluent_frame_class"] for row in local}),
            "fluent_frame_classes": "|".join(sorted({row["fluent_frame_class"] for row in local})),
            "matched_surface_forms_de": "|".join(sorted({form for row in local for form in row["matched_surface_forms_de"].split("|")})),
            "example_reading_de": sorted(row["fluent_reading_de"] for row in local)[0],
            "all_forms_observed_not_invented": "YES",
        })
    if len(form_rows) != 29:
        raise RuntimeError(f"Expected 29 realization forms, got {len(form_rows)}")
    write_tsv(REALIZATION_FORMS, form_rows)

    cell_rows: list[dict[str, object]] = []
    for component in sorted(COMPONENT_META):
        for model in MODELS:
            local_forms = [row for row in form_rows if row["component_value"] == component and row["active_model"] == model]
            local_witnesses = [row for row in witnesses.values() if row["component_value"] == component and row["active_model"] == model]
            cell_rows.append({
                "cell_id": f"G487-MC{len(cell_rows) + 1:02d}",
                "component_value": component,
                "portable_root_or_layer": COMPONENT_META[component][0],
                "component_class": COMPONENT_META[component][1],
                "active_model": model,
                "cell_status": "OBSERVED" if local_forms else "OPEN",
                "realization_form_count": len(local_forms),
                "realization_forms_de": "|".join(row["canonical_realization_de"] for row in local_forms) or "OPEN",
                "witness_record_count": len(local_witnesses),
                "witness_records": "|".join(sorted(row["record_id"] for row in local_witnesses)) or "NONE",
                "page_count": len({row["physical_page"] for row in local_witnesses}),
                "pages": "|".join(sorted({row["physical_page"] for row in local_witnesses})) or "NONE",
                "frame_class_count": len({row["fluent_frame_class"] for row in local_witnesses}),
                "frame_classes": "|".join(sorted({row["fluent_frame_class"] for row in local_witnesses})) or "NONE",
                "invented_form_count": 0,
            })
    write_tsv(MODEL_CELLS, cell_rows)

    recurrent_rules = [row for row in rules if int(row["pair_count"]) > 1]
    local_edge_rows: list[dict[str, object]] = []
    graph: dict[str, set[str]] = defaultdict(set)
    for number, rule in enumerate(recurrent_rules, 1):
        graph[rule["component_a"]].add(rule["component_b"])
        graph[rule["component_b"]].add(rule["component_a"])
        local_edge_rows.append({
            "edge_id": f"G487-LE{number:02d}",
            "source_rule_id": rule["rule_id"],
            "active_model_sequence": rule["active_model_sequence"],
            "fluent_frame_class": rule["fluent_frame_class"],
            "component_a": rule["component_a"],
            "component_b": rule["component_b"],
            "pair_count": rule["pair_count"],
            "same_page_pair_count": rule["same_page_pair_count"],
            "rule_status": rule["rule_status"],
            "phrase_signature_count": rule["phrase_signature_count"],
            "recurrent_local_edge": "YES",
        })
    write_tsv(LOCAL_EDGES, local_edge_rows)

    external_rows: list[dict[str, object]] = []
    contrast_sources = {"GDT428": action_contrasts, "GDT429": nonaction_contrasts}
    for component in ("DANACH", "EINSTELLEN", "HALTEN"):
        spec = ANCHOR_SPECS[component]
        matches = [row for row in contrast_sources[spec["source_experiment"]] if row["contrast_pair"] == spec["source_pair"]]
        if len(matches) != 1:
            raise RuntimeError(f"External anchor lookup drift for {component}")
        source = matches[0]
        meanings = {source["left_meaning_de"], source["right_meaning_de"]}
        if {component, spec["anchor_value"]} != meanings or int(source["shared_exact_substitution_frame_count"]) != spec["expected_frames"]:
            raise RuntimeError(f"External anchor value drift for {component}")
        external_rows.append({
            "anchor_id": f"G487-EA{len(external_rows) + 1:02d}",
            "component_value": component,
            "portable_root_or_layer": COMPONENT_META[component][0],
            "source_experiment": spec["source_experiment"],
            "source_contrast_pair": spec["source_pair"],
            "shared_exact_substitution_frame_count": source["shared_exact_substitution_frame_count"],
            "shared_frame_event_count": source["shared_frame_event_count"],
            "anchor_value": spec["anchor_value"],
            "anchor_root": spec["anchor_root"],
            "bridge_class": spec["bridge_class"],
            "workshop_interpretation_de": source["workshop_interpretation_de"],
            "decision": source["decision"],
            "meaning_change": "NO",
        })
    write_tsv(EXTERNAL_ANCHORS, external_rows)
    external_map = {row["component_value"]: row for row in external_rows}

    singleton_rules = [row for row in rules if int(row["pair_count"]) == 1]
    triangulation_rows: list[dict[str, object]] = []
    for number, rule in enumerate(singleton_rules, 1):
        component_a = rule["component_a"]
        component_b = rule["component_b"]
        local_path = shortest_path(graph, component_a, component_b)
        if local_path:
            tri_class = "LOCAL_RECURRENT_CYCLE"
            path_text = " → ".join(local_path)
            anchor_experiment = "GDT486"
            alternate_path_complete = "YES"
        else:
            external_component = next((component for component in (component_a, component_b) if component in external_map), None)
            if external_component is None:
                tri_class = "UNANCHORED"
                path_text = "NONE"
                anchor_experiment = "NONE"
                alternate_path_complete = "NO"
            else:
                anchor = external_map[external_component]
                other = component_b if external_component == component_a else component_a
                bridge_path = shortest_path(graph, anchor["anchor_value"], other)
                if bridge_path:
                    tri_class = "EXTERNAL_TO_LOCAL_CYCLE"
                    path_text = f"{external_component} —{anchor['source_experiment']}→ " + " → ".join(bridge_path)
                    alternate_path_complete = "YES"
                else:
                    tri_class = "EXTERNAL_ENDPOINT_ANCHOR_ONLY"
                    path_text = f"{external_component} —{anchor['source_experiment']}→ {anchor['anchor_value']}; anderer Endpunkt {other} liegt lokal"
                    alternate_path_complete = "NO"
                anchor_experiment = anchor["source_experiment"]
        triangulation_rows.append({
            "triangulation_id": f"G487-T{number:02d}",
            "rule_id": rule["rule_id"],
            "active_model_sequence": rule["active_model_sequence"],
            "fluent_frame_class": rule["fluent_frame_class"],
            "component_a": component_a,
            "component_b": component_b,
            "pair_id": rule["pair_ids"],
            "triangulation_class": tri_class,
            "triangulation_path_de": path_text,
            "path_edge_count": path_text.count("→"),
            "external_anchor_experiment": anchor_experiment,
            "alternate_path_complete": alternate_path_complete,
            "both_endpoints_anchored": "NO" if tri_class == "UNANCHORED" else "YES",
            "dictionary_remap_required": "NO",
        })
    write_tsv(SINGLETON_TRIANGULATION, triangulation_rows)

    lexicon_rows: list[dict[str, object]] = []
    for number, component in enumerate(sorted(COMPONENT_META), 1):
        local_witnesses = [row for row in witnesses.values() if row["component_value"] == component]
        local_forms = [row for row in form_rows if row["component_value"] == component]
        model_forms = {
            model: [row["canonical_realization_de"] for row in local_forms if row["active_model"] == model]
            for model in MODELS
        }
        if component in graph:
            anchor_class = "LOCAL_RECURRENT_GRAPH"
            anchor_detail = f"{len(graph[component])} wiederkehrende GDT486-Nachbarn"
        elif component in external_map:
            anchor_class = external_map[component]["bridge_class"]
            anchor_detail = f"{external_map[component]['source_experiment']} {external_map[component]['source_contrast_pair']} ×{external_map[component]['shared_exact_substitution_frame_count']}"
        else:
            anchor_class = "UNANCHORED"
            anchor_detail = "NONE"
        lexicon_rows.append({
            "lexicon_id": f"G487-L{number:02d}",
            "component_value": component,
            "portable_root_or_layer": COMPONENT_META[component][0],
            "component_class": COMPONENT_META[component][1],
            "witness_record_count": len(local_witnesses),
            "witness_records": "|".join(sorted(row["record_id"] for row in local_witnesses)),
            "page_count": len({row["physical_page"] for row in local_witnesses}),
            "pages": "|".join(sorted({row["physical_page"] for row in local_witnesses})),
            "register_count": len({row["register"] for row in local_witnesses}),
            "registers": "|".join(sorted({row["register"] for row in local_witnesses})),
            "observed_model_count": sum(bool(model_forms[model]) for model in MODELS),
            "observed_models": "|".join(model for model in MODELS if model_forms[model]),
            "open_models": "|".join(model for model in MODELS if not model_forms[model]) or "NONE",
            "realization_form_count": len(local_forms),
            "catalogue_forms_de": "|".join(model_forms["CATALOGUE"]) or "OPEN",
            "coordinate_forms_de": "|".join(model_forms["COORDINATE"]) or "OPEN",
            "instruction_forms_de": "|".join(model_forms["INSTRUCTION"]) or "OPEN",
            "local_recurrent_degree": len(graph.get(component, set())),
            "local_recurrent_neighbours": "|".join(sorted(graph.get(component, set()))) or "NONE",
            "anchor_class": anchor_class,
            "anchor_detail": anchor_detail,
            "all_forms_observed_not_invented": "YES",
        })
    write_tsv(LEXICON, lexicon_rows)

    page_rows: list[dict[str, object]] = []
    for page in dict.fromkeys(row["physical_page"] for row in assignments):
        page_assignments = [row for row in assignments if row["physical_page"] == page]
        page_witnesses = [row for row in witnesses.values() if row["physical_page"] == page]
        page_forms = [row for row in form_rows if page in row["pages"].split("|")]
        page_rows.append({
            "physical_page": page,
            "register": page_assignments[0]["register"],
            "record_count": len(page_assignments),
            "realization_witness_count": len(page_witnesses),
            "witness_record_count": len({row["record_id"] for row in page_witnesses}),
            "component_value_count": len({row["component_value"] for row in page_witnesses}),
            "component_values": "|".join(sorted({row["component_value"] for row in page_witnesses})) or "NONE",
            "realization_form_count": len(page_forms),
            "has_realization_support": "YES" if page_witnesses else "NO",
        })
    write_tsv(PAGE_SUPPORT, page_rows)

    tri_counts = Counter(row["triangulation_class"] for row in triangulation_rows)
    result = {
        "status": STATUS,
        "component_value_count": len(lexicon_rows),
        "component_model_cell_count": len(cell_rows),
        "observed_model_cell_count": sum(row["cell_status"] == "OBSERVED" for row in cell_rows),
        "open_model_cell_count": sum(row["cell_status"] == "OPEN" for row in cell_rows),
        "realization_form_count": len(form_rows),
        "realization_witness_count": len(witnesses),
        "witness_record_count": len({row["record_id"] for row in witnesses.values()}),
        "local_recurrent_edge_count": len(local_edge_rows),
        "local_recurrent_node_count": len(graph),
        "external_anchor_count": len(external_rows),
        "singleton_rule_count": len(triangulation_rows),
        "local_cycle_triangulated_count": tri_counts["LOCAL_RECURRENT_CYCLE"],
        "external_cycle_triangulated_count": tri_counts["EXTERNAL_TO_LOCAL_CYCLE"],
        "full_cycle_triangulated_count": tri_counts["LOCAL_RECURRENT_CYCLE"] + tri_counts["EXTERNAL_TO_LOCAL_CYCLE"],
        "endpoint_anchored_only_count": tri_counts["EXTERNAL_ENDPOINT_ANCHOR_ONLY"],
        "unanchored_singleton_count": tri_counts["UNANCHORED"],
        "all_component_values_anchored": all(row["anchor_class"] != "UNANCHORED" for row in lexicon_rows),
        "all_realization_forms_observed": all(row["all_forms_observed_not_invented"] == "YES" for row in form_rows),
        "page_count": len(page_rows),
        "support_page_count": sum(row["has_realization_support"] == "YES" for row in page_rows),
        "zero_support_pages": [row["physical_page"] for row in page_rows if row["has_realization_support"] == "NO"],
        "meaning_change_count": 0,
        "active_model_change_count": 0,
        "record_boundary_change_count": 0,
        "surface_change_count": 0,
        "recipe_change_count": 0,
        "page_change_count": 0,
        "claim_ceiling": "Model-conditioned German realization lexicon and contrast-network routing over fixed GDT486/GDT428/GDT429 working meanings; no independent semantic confirmation, invented form, new meaning, model, boundary, surface, recipe, event, or page.",
    }
    READABLE.write_text(build_readable(lexicon_rows, cell_rows, triangulation_rows, external_rows, result), encoding="utf-8")
    RESULT.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
