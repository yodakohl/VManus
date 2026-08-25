#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_mixed_root_codebook_eight_hundred_ninety_ninth"
PREFIX = "NINE_HUNDREDTH"

ROOT_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_36_MIXED_ROOT_CODEBOOK.tsv"
VOCAB_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_231_MIXED_CODEBOOK_VOCABULARY.tsv"
MARK_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_437_MIXED_CODEBOOK_MARK_DECK.tsv"
UNIT_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_118_MIXED_CODEBOOK_UNITS.tsv"
CARD_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_NINTH_6_MIXED_CODEBOOK_JOB_CARDS.tsv"

UTILITY = {
    "A_ADDR": ("STELLE", "ADDRESS", "LOCAL_ADDRESS_SIGN"),
    "AM_ADDR": ("GEGENFELD", "ADDRESS", "LOCAL_ADDRESS_SIGN"),
    "D_ADDR": ("TEILSTELLE", "ADDRESS", "LOCAL_ADDRESS_SIGN"),
    "D_LABEL": ("PHASE", "LABEL", "LOCAL_LABEL_SIGN"),
    "S_ADDR": ("STERNBEZUG", "ADDRESS", "LOCAL_ADDRESS_SIGN"),
    "S_LABEL": ("PHASENZEICHEN", "LABEL", "LOCAL_LABEL_SIGN"),
    "CHEO": ("AUSZUG", "MATERIAL", "LOCAL_MATERIAL_SIGN"),
    "WHOLE[cheey|shey]": ("LANG HALTEN", "WHOLE", "FUSED_WHOLE_SIGN"),
    "NONE": ("LOKALES GANZWORT", "WHOLE", "LOCAL_WHOLE_SIGN"),
    "CFH": ("AUSPRESSEN", "OPERATION", "WORKSHOP_UTILITY_ROOT"),
    "OS": ("DAZU", "ORDER", "WORKSHOP_UTILITY_ROOT"),
    "RESUME_CARD": ("DAVON", "REFERENT", "WORKSHOP_UTILITY_ROOT"),
}

PATTERNS = [
    ("WHOLE_LEXICON", "Eine verschmolzene oder lokale Ganzkarte direkt aus dem Werkstattdeck lesen."),
    ("CLOSING_INSTRUCTION", "Beliebige Nutzlast plus DY; den lokalen Schritt nach Ausführung schließen."),
    ("ORDERED_INSTRUCTION", "OT/OL/OS zuerst; danach die folgende Nutzlast als Folge oder Fortsetzung lesen."),
    ("OPERATION_INSTRUCTION", "Mindestens ein Handlungskern; übrige Kerne geben Stoff, Ort, Grad oder Posten an."),
    ("TRANSFER_OR_PATH", "L/AIR/CKH führt einen Posten von Quelle, durch Lauf oder Durchlass, zur Zielstelle."),
    ("STATE_OR_GRADE", "Zustand oder Grad ohne eigene Handlung; am aktiven Posten halten oder prüfen."),
    ("ARGUMENT_OR_ADDRESS", "Menge, Stoff, Quelle oder Zielstelle für die benachbarte Handlung bereitstellen."),
    ("REFERENT_OR_LABEL", "Den aktiven Posten oder eine lokale Diagrammadresse benennen."),
]

ROUNDTRIP_RECIPES = [
    ("Y+K+AIIN", "Den Posten nach Maß zugeben"),
    ("OK+EE+AL", "Lange an der Zielstelle ansetzen"),
    ("OT+CHD+DY", "Danach umsetzen und schließen"),
    ("R+SHED+DY", "Kühl ruhen lassen und schließen"),
    ("HO+CH+OR", "Einen Teil für den Ansatz entnehmen"),
    ("L+CKH+E+DY", "Kurz durch den Durchlass leiten und schließen"),
    ("SOLK+EE+Y", "Den Posten lange sammeln"),
    ("AIR+Y+DY", "Den Laufposten schließen"),
    ("OT+EE+Y", "Danach den Posten lange halten"),
    ("TALAM", "Beiseitestellen"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(recipe: str) -> list[str]:
    if recipe in {"NONE", "WHOLE[cheey|shey]", "RESUME_CARD"}:
        return [recipe]
    return recipe.split("+")


def primary_pattern(recipe: str, roles: list[str], action: str) -> str:
    parts = tokens(recipe)
    if action in {"READ_FUSED_WHOLE_WORD", "READ_LEARNED_WHOLE_ROOT"} or recipe in {"NONE", "WHOLE[cheey|shey]"}:
        return "WHOLE_LEXICON"
    if parts[-1] == "DY":
        return "CLOSING_INSTRUCTION"
    if roles[0] == "ORDER":
        return "ORDERED_INSTRUCTION"
    if "OPERATION" in roles:
        return "OPERATION_INSTRUCTION"
    if "PATH" in roles:
        return "TRANSFER_OR_PATH"
    if "STATE" in roles or "GRADE" in roles:
        return "STATE_OR_GRADE"
    if any(role in {"ARGUMENT", "MATERIAL", "ADDRESS"} for role in roles):
        return "ARGUMENT_OR_ADDRESS"
    return "REFERENT_OR_LABEL"


def main() -> None:
    roots = read(ROOT_SOURCE)
    vocabulary = read(VOCAB_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)

    symbols: dict[str, tuple[str, str, str]] = {
        row["root"]: (row["atomic_value_de"], row["role"], row["root_class"])
        for row in roots
    }
    symbols.update(UTILITY)
    symbol_rows = []
    use_counts: Counter[str] = Counter()
    for row in vocabulary:
        for token in tokens(row["component_recipe"]):
            use_counts[token] += int(row["marks"])
    for symbol, (value, role, symbol_class) in symbols.items():
        symbol_rows.append({
            "symbol": symbol,
            "atomic_value_de": value,
            "slot_role": role,
            "symbol_class": symbol_class,
            "marks": use_counts[symbol],
            "scribe_rule": f"SETZE {symbol} IN DEN SLOT {role}; LIES {value}",
        })
    assert set(use_counts) == set(symbols)

    parses = []
    parse_by_identity: dict[str, dict[str, object]] = {}
    for row in vocabulary:
        parts = tokens(row["component_recipe"])
        roles = [symbols[token][1] for token in parts]
        values = [symbols[token][0] for token in parts]
        pattern = primary_pattern(row["component_recipe"], roles, row["apprentice_action"])
        parsed = {
            "identity": row["identity"],
            "surface": row["house_surface"],
            "component_recipe": row["component_recipe"],
            "slot_signature": ">".join(roles),
            "root_reading_de": " · ".join(values),
            "dictionary_value_de": row["short_value_de"],
            "local_fluent_expansions_de": row["local_fluent_expansions_de"],
            "primary_pattern": pattern,
            "marks": row["marks"],
            "orders": row["orders"],
            "renderer_rule": "LEARN EXACT SURFACE ALLOGRAPH AFTER ROOT RECIPE",
        }
        parses.append(parsed)
        parse_by_identity[row["identity"]] = parsed

    pattern_counts: Counter[str] = Counter()
    pattern_mark_counts: Counter[str] = Counter()
    for row in parses:
        pattern_counts[str(row["primary_pattern"])] += 1
        pattern_mark_counts[str(row["primary_pattern"])] += int(row["marks"])
    pattern_rows = []
    for rank, (pattern, rule) in enumerate(PATTERNS, start=1):
        pattern_rows.append({
            "precedence": rank,
            "pattern": pattern,
            "identity_count": pattern_counts[pattern],
            "mark_count": pattern_mark_counts[pattern],
            "teaching_rule_de": rule,
        })

    revised_marks = []
    for row in marks:
        parsed = parse_by_identity[row["identity"]]
        revised_marks.append({
            **row,
            "slot_signature": parsed["slot_signature"],
            "primary_card_pattern": parsed["primary_pattern"],
            "root_reading_de": parsed["root_reading_de"],
            "eleventh_lesson": "SCRIBE_SLOT_GRAMMAR",
        })

    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        revised_units.append({
            **unit,
            "card_pattern_sequence": " -> ".join(str(row["primary_card_pattern"]) for row in local),
            "slot_signature_sequence": " || ".join(str(row["slot_signature"]) for row in local),
            "root_reading_sequence_de": " ; ".join(str(row["root_reading_de"]) for row in local),
            "slot_grammar_complete": "YES",
        })

    revised_cards = []
    for card in cards:
        local_marks = [row for row in revised_marks if row["order_id"] == card["order_id"]]
        counts = Counter(str(row["primary_card_pattern"]) for row in local_marks)
        revised_cards.append({
            **card,
            "pattern_counts": " | ".join(f"{key}:{counts[key]}" for key, _ in PATTERNS if counts[key]),
            "slot_parsed_marks": len(local_marks),
            "slot_grammar_complete": "YES",
        })

    vocab_by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in vocabulary:
        vocab_by_recipe[row["component_recipe"]].append(row)
    roundtrips = []
    for number, (recipe, intended) in enumerate(ROUNDTRIP_RECIPES, start=1):
        candidates = vocab_by_recipe[recipe]
        assert candidates
        row = candidates[0]
        parsed = parse_by_identity[row["identity"]]
        roundtrips.append({
            "example": number,
            "intended_instruction_de": intended,
            "root_recipe": recipe,
            "slot_signature": parsed["slot_signature"],
            "attested_surface": row["house_surface"],
            "backward_root_reading_de": parsed["root_reading_de"],
            "local_fluent_reading_de": row["local_fluent_expansions_de"],
            "roundtrip_rule": "INTENTION -> ROOT SLOTS -> LEARNED SURFACE; SURFACE -> ROOT SLOTS -> WORKSHOP READING",
        })

    write(f"{PREFIX}_48_GRAMMAR_SYMBOLS.tsv", symbol_rows, list(symbol_rows[0]))
    write(f"{PREFIX}_8_CARD_PATTERNS.tsv", pattern_rows, list(pattern_rows[0]))
    write(f"{PREFIX}_231_IDENTITY_SLOT_PARSES.tsv", parses, list(parses[0]))
    write(f"{PREFIX}_437_MARK_SLOT_PARSES.tsv", revised_marks, list(marks[0]) + ["slot_signature", "primary_card_pattern", "root_reading_de", "eleventh_lesson"])
    write(f"{PREFIX}_118_UNIT_SLOT_GRAMMAR.tsv", revised_units, list(units[0]) + ["card_pattern_sequence", "slot_signature_sequence", "root_reading_sequence_de", "slot_grammar_complete"])
    write(f"{PREFIX}_6_JOB_CARD_SLOT_SUMMARY.tsv", revised_cards, list(revised_cards[0]))
    write(f"{PREFIX}_10_WORKED_ROUNDTRIPS.tsv", roundtrips, list(roundtrips[0]))

    lines = [
        "# Einfache Slotgrammatik des Schreibers",
        "",
        "Der Schreiber denkt nicht in langen Wörtern, sondern legt kleine Kartenkerne in Rollen ab.",
        "Die sichtbare Reihenfolge bleibt erhalten; die genaue Oberflächenform wird als Werkstattallograph zum Wurzelrezept gelernt.",
        "",
        "## Acht Kartenmuster",
        "",
    ]
    for row in pattern_rows:
        lines.append(f"{row['precedence']}. **{row['pattern']}** — {row['teaching_rule_de']} ({row['identity_count']} Identitäten / {row['mark_count']} Marken)")
    lines.extend(["", "## Zehn Vorwärts-/Rückwärtsbeispiele", ""])
    for row in roundtrips:
        lines.extend([
            f"### {row['example']}. {row['intended_instruction_de']}",
            "",
            f"Wurzeln: `{row['root_recipe']}` → Oberfläche: `{row['attested_surface']}`.",
            f"Rücklesung: {row['backward_root_reading_de']} → {row['local_fluent_reading_de']}.",
            "",
        ])
    (HERE / f"{PREFIX}_SCRIBE_SLOT_GRAMMAR.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "FORTY_EIGHT_SYMBOLS_AND_EIGHT_CARD_PATTERNS_PARSE_ALL_TWO_HUNDRED_THIRTY_ONE_IDENTITIES_AND_FOUR_HUNDRED_THIRTY_SEVEN_MARKS",
        "semantic_roots": len(roots),
        "utility_and_local_symbols": len(UTILITY),
        "grammar_symbols": len(symbol_rows),
        "patterns": len(pattern_rows),
        "pattern_identity_counts": dict(pattern_counts),
        "pattern_mark_counts": dict(pattern_mark_counts),
        "identities": len(parses),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "job_cards": len(revised_cards),
        "roundtrips": len(roundtrips),
        "unparsed_identities": 0,
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 900: Slotgrammatik des Schreibers\n\n"
        "Die 36 Bedeutungswurzeln werden um zwölf lokale oder technische Hilfszeichen ergänzt. "
        "Acht Kartenmuster parsen alle 231 Identitäten, 437 Marken und 118 Einheiten. "
        "Zehn Vorwärts-/Rückwärtsbeispiele zeigen, wie aus einer Werkstattanweisung erst ein Rollenrezept und dann eine gelernte Oberflächenkarte wird.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
