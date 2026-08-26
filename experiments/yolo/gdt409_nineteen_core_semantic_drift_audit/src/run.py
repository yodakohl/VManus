#!/usr/bin/env python3
"""Audit the nineteen portable working meanings across the admitted pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "artifacts"
BASE = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
EVENTS = BASE / "gdt407_4576_running_event_edition.tsv"
STATEMENTS = BASE / "gdt407_715_statement_edition.tsv"
ATTACHMENTS = BASE / "gdt407_5051_attachment_edition.tsv"
ATOM_DICT = ROOT / "experiments/yolo/gdt405_second_random_batch_recipe_lock/artifacts/gdt405_46_locked_atom_dictionary.tsv"

ROOT_META = {
    "Y": ("ARGUMENT", "POSTEN", "DIES", "GEGENSTAND"),
    "OK": ("HANDLUNG", "SETZEN", "ANSETZEN", "AKTIVIEREN"),
    "OL": ("REIHENFOLGE", "FORTSETZEN", "WEITER", "GLEICHER GANG"),
    "OT": ("REIHENFOLGE", "DANACH", "NÄCHSTER", "WECHSEL"),
    "AL": ("BEZIEHUNG", "ZIELORT", "ZU", "ANSCHLUSS"),
    "CH": ("HANDLUNG", "NEHMEN", "BEARBEITEN", "GREIFEN"),
    "SH": ("HANDLUNG", "HALTEN", "RUHEN LASSEN", "BEWAHREN"),
    "AR": ("BEZIEHUNG", "AUSGANG", "VON", "QUELLE"),
    "K": ("HANDLUNG", "GEBEN", "ZUFÜHREN", "ZUORDNEN"),
    "AIIN": ("ARGUMENT", "WERT", "MASS", "VORGABE"),
    "S": ("HANDLUNG", "WÄHLEN", "TRENNEN", "PRÜFEN"),
    "CHD": ("HANDLUNG", "UMSETZEN", "ÜBERFÜHREN", "WECHSELN"),
    "OR": ("ARGUMENT", "EINHEIT", "ANSATZ", "BESTAND"),
    "L": ("BEZIEHUNG", "VERBINDUNG", "MIT", "ANSCHLUSS"),
    "T": ("HANDLUNG", "EINSTELLEN", "ORDNEN", "BESTIMMEN"),
    "AIN": ("ARGUMENT", "ANTEIL", "PORTION", "TEIL"),
    "R": ("HANDLUNG", "MARKIEREN", "VERWEISEN", "KENNZEICHNEN"),
    "P": ("HANDLUNG", "EINSETZEN", "BEGINNEN", "EINBRINGEN"),
    "AIR": ("BEZIEHUNG", "LAUF", "WEG", "FLUSS"),
}

# These are deliberately minimal working decisions, not translations.  The
# status expresses how much of the *role* is stable, not how certain the German
# lexeme is.
DECISION = {
    "Y": ("KEEP", "POSTEN", "Referentrolle breit und registerübergreifend"),
    "OK": ("KEEP", "SETZEN", "produktiver Handlungskopf; genauer Verbton offen"),
    "OL": ("KEEP", "FORTSETZEN", "wiederkehrende Fortsetzungs-/Weiterführungslage"),
    "OT": ("KEEP", "DANACH", "Geschwister-/Folgewechsel statt Stoffwort"),
    "AL": ("KEEP", "ZIELORT", "komplementäre Zieladresse zu AR"),
    "CH": ("KEEP_PROVISIONAL", "NEHMEN", "Handlungskopf stabil; NEHMEN bleibt breit"),
    "SH": ("KEEP_PROVISIONAL", "HALTEN", "Handlungskopf stabil; Halten/Ruhen lokal offen"),
    "AR": ("KEEP", "AUSGANG", "komplementäre Quelladresse zu AL"),
    "K": ("KEEP_PROVISIONAL", "GEBEN", "Handlungskopf stabil; Zuführen/Zuordnen lokal offen"),
    "AIIN": ("KEEP", "WERT", "MASS wäre auf Himmelsseiten zu eng"),
    "S": ("KEEP_PROVISIONAL", "WÄHLEN", "Auswahlkopf stabil; Prüfen/Trennen lokale Rivalen"),
    "CHD": ("KEEP_PROVISIONAL", "UMSETZEN", "Transfer-/Zustandswechselkern, genauer Vorgang offen"),
    "OR": ("KEEP", "EINHEIT", "ANSATZ wäre in Bio/Himmel zu eng"),
    "L": ("KEEP_PROVISIONAL", "VERBINDUNG", "relationale Brücke stabil, MIT bleibt Rivale"),
    "T": ("KEEP_PROVISIONAL", "EINSTELLEN", "Setz-/Bestimmungskopf stabil"),
    "AIN": ("KEEP", "ANTEIL", "PORTION wäre in Himmels-/Adresskontexten zu stofflich"),
    "R": ("KEEP_PROVISIONAL", "MARKIEREN", "R-Kopf/Schwanz stabil, genauer Verweisakt offen"),
    "P": ("KEEP_PROVISIONAL", "EINSETZEN", "Eingangs-/Einbringungskopf stabil"),
    "AIR": ("KEEP_PROVISIONAL", "LAUF", "WASSER klar verworfen; Weg/Fluss lokale Expansion"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_recipe(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    attachments = read_tsv(ATTACHMENTS)
    atoms = read_tsv(ATOM_DICT)
    atom_values = {row["atom"]: row["locked_working_value_de"] for row in atoms}
    roots = set(ROOT_META)
    assert (len(events), len(statements), len(attachments), len(roots)) == (4576, 715, 5051, 19)
    assert all(atom_values[root] for root in roots)
    statement_by_id = {row["source_statement_id"]: row for row in statements}

    mention_rows: list[dict[str, object]] = []
    frame_counter: dict[str, Counter[str]] = {root: Counter() for root in roots}
    frame_pages: dict[tuple[str, str], set[str]] = defaultdict(set)
    for event in events:
        parts = split_recipe(event["component_recipe"])
        for ordinal, atom in enumerate(parts, start=1):
            if atom not in roots:
                continue
            frame = list(parts)
            frame[ordinal-1] = "{SLOT}"
            frame_text = "+".join(frame)
            frame_counter[atom][frame_text] += 1
            frame_pages[(atom, frame_text)].add(event["physical_page"])
            mention_rows.append({
                "root": atom, "working_value_de": DECISION[atom][1],
                "global_running_event_id": event["global_running_event_id"],
                "physical_page": event["physical_page"], "register": event["register"],
                "source_statement_id": event["source_statement_id"], "surface": event["surface"],
                "component_recipe": event["component_recipe"], "atom_ordinal": ordinal,
                "atom_position": "FIRST" if ordinal == 1 else "LAST" if ordinal == len(parts) else "MIDDLE",
                "substitution_frame": frame_text,
            })

    focus_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    governed_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in attachments:
        if row["focus_core"] in roots:
            focus_by_root[row["focus_core"]].append(row)
        if row["action_core"] in roots:
            governed_by_root[row["action_core"]].append(row)

    summary_rows: list[dict[str, object]] = []
    register_rows: list[dict[str, object]] = []
    examples: list[dict[str, object]] = []
    for root in ROOT_META:
        category, current, rival_a, rival_b = ROOT_META[root]
        mentions = [row for row in mention_rows if row["root"] == root]
        event_ids = {row["global_running_event_id"] for row in mentions}
        root_events = [row for row in events if row["global_running_event_id"] in event_ids]
        pages = sorted({row["physical_page"] for row in mentions})
        registers = sorted({row["register"] for row in mentions})
        positions = Counter(row["atom_position"] for row in mentions)
        focus = focus_by_root[root]
        governed = governed_by_root[root]
        decision, selected, reason = DECISION[root]
        summary_rows.append({
            "root": root, "structural_category": category, "selected_minimal_value_de": selected,
            "decision": decision, "rival_a_de": rival_a, "rival_b_de": rival_b,
            "atom_mention_count": len(mentions), "event_count": len(root_events),
            "distinct_surface_count": len({row["surface"] for row in root_events}),
            "page_count": len(pages), "pages": "|".join(pages),
            "register_count": len(registers), "registers": "|".join(registers),
            "first_count": positions["FIRST"], "middle_count": positions["MIDDLE"], "last_count": positions["LAST"],
            "standalone_event_count": sum(row["component_recipe"] == root for row in root_events),
            "focus_attachment_count": len(focus),
            "focus_family_counts": "|".join(f"{k}:{v}" for k, v in sorted(Counter(row["focus_family"] for row in focus).items())) or "NONE",
            "governed_focus_count": len(governed),
            "governed_focus_family_counts": "|".join(f"{k}:{v}" for k, v in sorted(Counter(row["focus_family"] for row in governed).items())) or "NONE",
            "distinct_substitution_frame_count": len(frame_counter[root]),
            "decision_reason_de": reason,
        })
        for register in sorted({row["register"] for row in events}):
            reg_mentions = [row for row in mentions if row["register"] == register]
            register_rows.append({
                "root": root, "selected_minimal_value_de": selected, "register": register,
                "atom_mention_count": len(reg_mentions),
                "event_count": len({row["global_running_event_id"] for row in reg_mentions}),
                "page_count": len({row["physical_page"] for row in reg_mentions}),
                "surface_count": len({row["surface"] for row in reg_mentions}),
                "register_reading_guardrail_de": (
                    "Himmelswert bleibt abstrakt; kein Stoff-/Wasserwort"
                    if register == "CELESTIAL" else
                    "sichtbarer Besitzer liefert den lokalen Gegenstand"
                    if register in {"HERBAL", "BIOLOGICAL", "PHARMA"} else
                    "Textblock ist Besitzer; kein Objekt ergänzen"
                ),
            })
            if reg_mentions:
                chosen = min(reg_mentions, key=lambda row: int(str(row["global_running_event_id"]).split("E")[-1]))
                statement = statement_by_id[chosen["source_statement_id"]]
                examples.append({
                    "root": root, "selected_minimal_value_de": selected, "register": register,
                    "physical_page": chosen["physical_page"], "source_statement_id": chosen["source_statement_id"],
                    "surface": chosen["surface"], "component_recipe": chosen["component_recipe"],
                    "owner_de": statement["owner_de"], "statement_surface_sequence": statement["surface_sequence"],
                    "statement_literal_core_sequence_de": statement["literal_core_sequence_de"],
                    "semantic_caution_de": reason,
                })

    pair_rows: list[dict[str, object]] = []
    ordered_roots = list(ROOT_META)
    for index, left in enumerate(ordered_roots):
        for right in ordered_roots[index+1:]:
            shared = set(frame_counter[left]) & set(frame_counter[right])
            overlap_events = sum(min(frame_counter[left][frame], frame_counter[right][frame]) for frame in shared)
            left_total = sum(frame_counter[left].values())
            right_total = sum(frame_counter[right].values())
            union_weight = left_total + right_total - overlap_events
            pair_rows.append({
                "root_a": left, "value_a_de": DECISION[left][1], "root_b": right, "value_b_de": DECISION[right][1],
                "same_structural_category": "YES" if ROOT_META[left][0] == ROOT_META[right][0] else "NO",
                "shared_exact_substitution_frame_count": len(shared),
                "weighted_frame_overlap_event_count": overlap_events,
                "weighted_frame_jaccard": f"{(overlap_events / union_weight if union_weight else 0):.6f}",
                "shared_frame_examples": " | ".join(sorted(shared)[:8]) or "NONE",
                "shared_frame_page_union": "|".join(sorted(set().union(*(
                    frame_pages[(left, frame)] | frame_pages[(right, frame)] for frame in shared
                )))) if shared else "NONE",
            })
    pair_rows.sort(key=lambda row: (-int(row["weighted_frame_overlap_event_count"]), row["root_a"], row["root_b"]))

    dictionary_rows = []
    for row in summary_rows:
        dictionary_rows.append({
            "root": row["root"], "structural_category": row["structural_category"],
            "selected_minimal_value_de": row["selected_minimal_value_de"], "decision": row["decision"],
            "rival_a_de": row["rival_a_de"], "rival_b_de": row["rival_b_de"],
            "portable_use_rule_de": {
                "ARGUMENT": "als kurzen Posten-/Wertslot lesen; konkretes Nomen kommt vom Besitzer",
                "HANDLUNG": "als kurze Werkstatthandlung lesen; konkrete Technik bleibt lokal",
                "BEZIEHUNG": "als Quell-, Ziel- oder Wegrelation lesen; keine Flussrichtung erfinden",
                "REIHENFOLGE": "als Fortsetzung oder nächsten Geschwistergang lesen",
            }[str(row["structural_category"])],
            "atom_mention_count": row["atom_mention_count"], "page_count": row["page_count"],
            "register_count": row["register_count"], "decision_reason_de": row["decision_reason_de"],
        })

    summary_path = OUT / "gdt409_19_core_semantic_audit.tsv"
    register_path = OUT / "gdt409_19_by_register.tsv"
    pair_path = OUT / "gdt409_substitution_frame_pairs.tsv"
    example_path = OUT / "gdt409_cross_register_examples.tsv"
    dictionary_path = OUT / "gdt409_selected_minimal_dictionary.tsv"
    write_tsv(summary_path, summary_rows, list(summary_rows[0]))
    write_tsv(register_path, register_rows, list(register_rows[0]))
    write_tsv(pair_path, pair_rows, list(pair_rows[0]))
    write_tsv(example_path, examples, list(examples[0]))
    write_tsv(dictionary_path, dictionary_rows, list(dictionary_rows[0]))

    result = {
        "status": "NINETEEN_MINIMAL_VALUES_RETAINED__TEN_PROVISIONAL_VERBS_OR_RELATIONS",
        "portable_roots": 19, "root_mentions": len(mention_rows),
        "root_events": len({row["global_running_event_id"] for row in mention_rows}),
        "decision_counts": dict(sorted(Counter(row["decision"] for row in dictionary_rows).items())),
        "substitution_pair_count": len(pair_rows), "cross_register_examples": len(examples),
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in (EVENTS, STATEMENTS, ATTACHMENTS, ATOM_DICT)},
        "output_sha256": {str(path.relative_to(HERE)): sha256(path) for path in (summary_path, register_path, pair_path, example_path, dictionary_path)},
    }
    (OUT / "gdt409_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
