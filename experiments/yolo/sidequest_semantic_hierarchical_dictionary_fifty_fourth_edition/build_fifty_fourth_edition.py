#!/usr/bin/env python3
"""Consolidate every current teaching layer without confusing it with word meaning."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_owner_atlas_forty_sixth_edition/FORTY_SIXTH_28_ROOT_TRANSFER_VERDICTS.tsv"
OWNERS = ROOT / "experiments/yolo/sidequest_semantic_owner_atlas_forty_sixth_edition/FORTY_SIXTH_140_OWNER_EXPANSIONS.tsv"
NOMENCLATOR = ROOT / "experiments/yolo/sidequest_semantic_nomenclator_forty_third_edition/FORTY_THIRD_15_NOMENCLATOR_LESSONS.tsv"
MEMORY = ROOT / "experiments/yolo/sidequest_semantic_scribe_memory_thirty_ninth_edition/THIRTY_NINTH_FOUR_MEMORY_SLOTS.tsv"
MACROS = ROOT / "experiments/yolo/sidequest_semantic_process_macros_thirty_eighth_edition/THIRTY_EIGHTH_20_PROCESS_MACROS.tsv"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_speakable_astro_thirty_sixth_edition/THIRTY_SIXTH_13_INSTRUMENT_MODULES.tsv"
MASTER = ROOT / "experiments/yolo/sidequest_semantic_simulated_master_exemplar_fifty_third_edition/FIFTY_THIRD_4_MASTER_CATALOG_CARDS.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def human(value: str) -> str:
    compact = {
        "LAUF_BAHN": "Lauf/Bahn",
        "ANSATZ_SATZ": "Ansatz",
        "DIESER_POSTEN": "dieser Posten",
        "AUSGABE_AUSZUG": "Auszug",
        "SICHTBARES_ERGEBNIS": "sichtbares Ergebnis",
        "FESTMACHEN_UND_SCHLIESSEN": "festmachen und schließen",
        "PROSA_TUCH__ASTRO_PORTION": "Prosa: Tuch / Astro: Portion",
        "PROSA_KUEHLEN__ASTRO_MARKIEREN": "Prosa: kühlen / Astro: markieren",
        "PROSA_GEFAESS__ASTRO_FELD": "Prosa: Gefäß / Astro: Feld",
    }
    return compact.get(value, value.replace("__", " / ").replace("_", " ").lower())


def entry(level: str, entry_id: str, kind: str, sign: str, value: str, written: str,
          scope: str, composition: str, supplied: str, boundary: str, source: Path) -> dict[str, str]:
    return {
        "hierarchy_level": level,
        "entry_id": entry_id,
        "entry_kind": kind,
        "surface_symbol_or_pattern": sign,
        "short_value_de": value,
        "written_as_manuscript_card": written,
        "scope": scope,
        "composition_license": composition,
        "what_supplies_concrete_content": supplied,
        "must_not_be_read_as": boundary,
        "source_path": str(source.relative_to(ROOT)),
    }


def main() -> None:
    entries: list[dict[str, str]] = []
    root_rows = read_tsv(ROOTS)
    for row in root_rows:
        entries.append(entry(
            "L1_ATOMIC_ROOT", f"ROOT_{row['root']}", "PRODUCTIVE_CARD_COMPONENT",
            row["root"], human(row["atomic_value_de"]), "YES_INSIDE_REGISTERED_CARDS",
            row["register_evidence"], "May combine only in registered or lattice-licensed base/ending slots",
            "OWNER supplies the concrete noun or address", "a full sentence, object name, or historical plaintext word", ROOTS,
        ))

    nomenclator_rows = read_tsv(NOMENCLATOR)
    for row in nomenclator_rows:
        entries.append(entry(
            "L2_LEARNED_NOMENCLATOR", row["lesson_id"], row["lesson_kind"],
            row["registered_surfaces"], human(row["learned_value_de"]), "YES_AS_LEARNED_REGISTERED_FORM",
            row["pages"], row["composition_rule"], "learned workshop convention and local owner",
            "a productive letter-by-letter decomposition unless its named rule licenses one", NOMENCLATOR,
        ))

    master_rows = read_tsv(MASTER)
    for row in master_rows:
        entries.append(entry(
            "L2B_SIMULATED_MASTER_SUPPLEMENT", row["catalog_id"], "HYPOTHETICAL_TEACHING_CATEGORY",
            f"[{row['catalog_id']}]", human(row["short_value_de"]), "NO_NEUTRAL_CATALOG_LABEL_ONLY",
            "SIMULATED_WORKSHOP", "May fill its named bare slot in the four-card training compiler",
            "the spoken master lesson", "a Voynich surface or an observed manuscript word", MASTER,
        ))

    memory_rows = read_tsv(MEMORY)
    for row in memory_rows:
        entries.append(entry(
            "L3_SILENT_MEMORY_REGISTER", f"MEM_{row['slot']}", "SCRIBE_STATE_NOT_CARD",
            f"<{row['slot']}>", row["what_the_scribe_remembers"], "NO",
            "ONE_RECORD", f"set: {row['set_rule']}; carry: {row['carry_rule']}; clear: {row['clear_rule']}",
            row["physical_aid"], "a word, glyph, stem, or silent noun encoded by one card", MEMORY,
        ))

    macro_rows = read_tsv(MACROS)
    for row in macro_rows:
        entries.append(entry(
            "L4_PROCESS_MACRO", f"MAC_{row['macro_id']}", "MULTI_CLAUSE_TEACHING_MOVE",
            row["clause_family_pattern"], row["spoken_workshop_phrase_de"], "NO_PATTERN_OVER_SEVERAL_CARDS",
            row["raw_records"], f"exactly {row['clause_length']} clauses in the listed order",
            "the sequence of independently read cards and memory state", "the meaning of any one surface or card", MACROS,
        ))

    owner_rows = read_tsv(OWNERS)
    owners = {}
    for row in owner_rows:
        owners.setdefault(row["owner_class"], row)
    for owner_class, row in sorted(owners.items()):
        entries.append(entry(
            "L5_VISIBLE_OWNER", f"OWNER_{owner_class}", "PICTURE_OR_LOCAL_STATION",
            owner_class, row["owner_item"], "NO",
            owner_class, f"supplies target={row['owner_target']}; source={row['owner_source']}; run={row['owner_run']}",
            "the visible plant, basin, cloth, diagram, or current workpiece", "a hidden word silently contained in every card", OWNERS,
        ))

    astro_rows = read_tsv(ASTRO)
    for row in astro_rows:
        entries.append(entry(
            "L6_ASTRO_LOCAL_MODULE", row["namespace_id"], "DIAGRAM_NAMESPACE_NOT_WORD",
            row["visible_kind"], row["output_de"], "NO_NAMESPACE_OVER_VISIBLE_GROUPS",
            row["page"], row["local_rule_de"], "the drawn panel, wheel, star locus, or local master key",
            row["do_not_assume_de"], ASTRO,
        ))

    for order, row in enumerate(entries, 1):
        row["global_teaching_order"] = order
    fields = ["global_teaching_order"] + [key for key in entries[0] if key != "global_teaching_order"]
    entries = [{key: row[key] for key in fields} for row in entries]
    write_tsv(OUT / "FIFTY_FOURTH_89_HIERARCHICAL_ENTRIES.tsv", entries)

    layer_specs = [
        ("L1_ATOMIC_ROOT", "28", "short reusable card value", "read first inside a registered composition"),
        ("L2_LEARNED_NOMENCLATOR", "15", "memorized technical body, whole card, or register split", "longest learned form outranks shorter visible resemblance"),
        ("L2B_SIMULATED_MASTER_SUPPLEMENT", "4", "neutral missing-card category", "training placeholder only; never a manuscript surface"),
        ("L3_SILENT_MEMORY_REGISTER", "4", "record-local referent carried by the scribe", "expands ellipsis but is never a word gloss"),
        ("L4_PROCESS_MACRO", "20", "recurring two- or three-clause move", "helps execute a dossier but never defines one card"),
        ("L5_VISIBLE_OWNER", "5", "picture or station supplies concrete nouns and addresses", "owner content may not leak into the root"),
        ("L6_ASTRO_LOCAL_MODULE", "13", "local diagram namespace and lookup instruction", "never exported across wheels, panels, pages, or into prose"),
    ]
    layer_rows = [
        {"layer": layer, "entry_count": count, "job_de": job, "precedence_or_boundary_de": rule}
        for layer, count, job, rule in layer_specs
    ]
    write_tsv(OUT / "FIFTY_FOURTH_7_LAYER_RULES.tsv", layer_rows)

    examples = [
        ("ROOT_ONLY", "OK+AIN", "ansetzen an einer Portion", "OK and AIN contribute; owner supplies what the portion is"),
        ("ROOT_PLUS_OWNER", "AIR under BASIN_STATION", "Lauf der Beckenflüssigkeit", "AIR remains Lauf/Bahn; basin supplies liquid"),
        ("ROOT_PLUS_OWNER", "AIR under CELESTIAL_TABLE", "sichtbare Himmelsbahn", "same AIR value; celestial table supplies sky object"),
        ("NOMENCLATOR", "CFH+Y", "auswringen am aktuellen Posten", "CFH is learned before Y is added"),
        ("NOMENCLATOR", "OK+Y+LDDY", "den aktuellen Posten ansetzen, festmachen und schließen", "LDDY remains a learned body"),
        ("MEMORY", "Y + <ACTIVE>", "dieser zuvor gesetzte Arbeitsposten", "the noun comes from ACTIVE, not from Y"),
        ("MEMORY", "OL + <PREVIOUS>", "mit dem unmittelbar vorigen Posten fortfahren", "PREVIOUS is a carried slot, not a hidden OL gloss"),
        ("MACRO", "SET>CONTINUE>SETTLE", "ansetzen, fortführen, absetzen", "three clauses; never one word"),
        ("OWNER", "AL under CLOTH_FILTER", "am Empfangsgefäß des Tuchs", "AL says target; owner supplies the receiving vessel"),
        ("ASTRO", "F69_LEFT_WHEEL_NS", "einen lokalen linken Radplatz ablesen", "no direction or link to f68"),
        ("MASTER", "CKHE | AIN", "trennen an einer Portion", "M02 can stand for CKHE only inside the simulation"),
        ("PARAPHRASE", "OK+E+CLOSE for OK+CLOSE", "kurz ansetzen und schließen", "extra brief grade remains spoken"),
    ]
    example_rows = [
        {"example_no": index, "layer_mix": mix, "input_or_pattern": pattern, "spoken_de": spoken, "why_not_one_word_de": why}
        for index, (mix, pattern, spoken, why) in enumerate(examples, 1)
    ]
    write_tsv(OUT / "FIFTY_FOURTH_12_BOUNDARY_EXAMPLES.tsv", example_rows)

    by_layer = Counter(row["hierarchy_level"] for row in entries)
    doc = [
        "# Gesamtes Wörterbuch als Hierarchie",
        "",
        "Die Werkstatt besitzt nicht ein flaches Wörterbuch, sondern sieben sauber",
        "getrennte Ebenen. Nur Ebene 1 und die beobachteten Teile von Ebene 2 sind",
        "Kartenbedeutungen. Alles darüber erklärt, wie Karten verwendet, ergänzt oder",
        "aus Bildern und Registern konkretisiert werden.",
        "",
    ]
    for layer, _, job, rule in layer_specs:
        doc.extend([f"## {layer} ({by_layer[layer]})", "", f"{job}. {rule}.", ""])
        for row in entries:
            if row["hierarchy_level"] == layer:
                doc.append(f"- `{row['surface_symbol_or_pattern']}` — **{row['short_value_de']}**")
        doc.append("")
    (OUT / "FIFTY_FOURTH_COMPLETE_HIERARCHICAL_DICTIONARY.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {"hierarchical_entries": len(entries), "layers": len(layer_rows), "boundary_examples": len(example_rows), **dict(by_layer)},
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (ROOTS, OWNERS, NOMENCLATOR, MEMORY, MACROS, ASTRO, MASTER)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
