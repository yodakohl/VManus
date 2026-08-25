#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_speakable_condition_lexicon_eight_hundred_ninety_seventh"
PREFIX = "EIGHT_HUNDRED_NINETY_EIGHTH"

VOCAB_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_231_COMPLETE_WORKSHOP_VOCABULARY.tsv"
MARK_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_437_ALL_SPEAKABLE_MARK_DECK.tsv"
UNIT_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_118_ALL_EXECUTABLE_UNITS.tsv"
CARD_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_6_COMPLETE_JOB_CARDS.tsv"
CONDITION_SOURCE = SOURCE / "EIGHT_HUNDRED_NINETY_SEVENTH_73_SPEAKABLE_CONDITION_LEXICON.tsv"

SHARED_SURFACES = {
    "cheey": "LANG HALTEN",
    "chey": "POSTEN",
    "cho": "TEIL",
    "dal": "ZIELSTELLE",
    "ody": "ARBEITSGANG SCHLIESSEN",
    "ol": "FORTSETZEN",
    "oteey": "DANACH LANG HALTEN",
    "sheey": "LANG HALTEN",
}

SHARED_COMPONENTS = {
    "AIIN": "MASS",
    "AIR": "LAUF",
    "AL": "ZIELSTELLE",
    "AR": "QUELLE",
    "CH": "ENTNEHMEN",
    "CHD": "UMSETZEN",
    "CKH": "DURCHLASS",
    "CTH": "BEREIT",
    "DY": "SCHLIESSEN",
    "E": "KURZ",
    "EE": "LANG",
    "HO": "TEIL",
    "K": "ZUGEBEN",
    "O": "ARBEITSGANG",
    "OK": "ANSETZEN",
    "OL": "FORTSETZEN",
    "OR": "ANSATZ",
    "OT": "DANACH",
    "R": "BEZUG",
    "SH": "HALTEN",
    "T": "BEARBEITEN",
    "Y": "POSTEN",
}

LOCAL_COMPONENTS = {
    "A_ADDR": "STELLE",
    "AM_ADDR": "GEGENFELD",
    "D_ADDR": "TEILSTELLE",
    "D_LABEL": "PHASE",
    "S_ADDR": "STERNBEZUG",
    "S_LABEL": "PHASENZEICHEN",
    "CHEO": "AUSZUG",
    "WHOLE[cheey|shey]": "LANG HALTEN",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(recipe: str) -> list[str]:
    if recipe in {"NONE", "WHOLE[cheey|shey]"}:
        return [recipe]
    return recipe.split("+")


def main() -> None:
    vocabulary = read(VOCAB_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)
    conditions = read(CONDITION_SOURCE)

    surface_rows = []
    for surface, root in SHARED_SURFACES.items():
        local = [row for row in marks if row["surface"] == surface]
        prose = [row for row in local if row["master_section"] != "WHEN"]
        when = [row for row in local if row["master_section"] == "WHEN"]
        surface_rows.append({
            "surface": surface,
            "portable_root_de": root,
            "prose_marks": len(prose),
            "condition_marks": len(when),
            "total_marks": len(local),
            "old_prose_values_de": " | ".join(sorted({row["concrete_default_de"] for row in prose})),
            "old_condition_values_de": " | ".join(sorted({row["concrete_default_de"] for row in when})),
            "new_value_de": root,
            "workshop_rule": "GLEICHE SICHTBARE FORM TRAEGT DENSELBEN KURZEN KERN",
        })

    section_counts: dict[tuple[str, str], int] = Counter()
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in marks:
        section = "CONDITION" if row["master_section"] == "WHEN" else "PROSE"
        for token in tokens(row["component_recipe"]):
            if token in SHARED_COMPONENTS:
                section_counts[(token, section)] += 1
                if len(examples[(token, section)]) < 4:
                    examples[(token, section)].append(f"{row['surface']}={row['concrete_default_de']}")
    component_rows = []
    for component, root in SHARED_COMPONENTS.items():
        component_rows.append({
            "component": component,
            "portable_root_de": root,
            "prose_marks": section_counts[(component, "PROSE")],
            "condition_marks": section_counts[(component, "CONDITION")],
            "prose_examples": " | ".join(examples[(component, "PROSE")]),
            "condition_examples": " | ".join(examples[(component, "CONDITION")]),
            "composition_rule": f"{component}(X) TRAEGT {root}; BILD UND REGISTER LIEFERN DEN SACHBEREICH",
        })

    condition_by_id = {row["opaque_local_id"]: row for row in conditions}
    portable_conditions = []
    portable_by_id: dict[str, str] = {}
    for row in conditions:
        if row["surface"] in SHARED_SURFACES:
            portable = SHARED_SURFACES[row["surface"]]
            source = "EXACT_SURFACE_BRIDGE"
        elif row["component_parse"] == "NONE":
            portable = row["speakable_condition_word_de"]
            source = "LOCAL_WHOLE_WORD"
        else:
            parts = []
            for token in tokens(row["component_parse"]):
                if token in SHARED_COMPONENTS:
                    parts.append(SHARED_COMPONENTS[token])
                elif token in LOCAL_COMPONENTS:
                    parts.append(LOCAL_COMPONENTS[token])
                else:
                    raise AssertionError(f"unmapped condition component: {token}")
            portable = " · ".join(parts)
            source = "PORTABLE_COMPONENT_COMPOSITION"
        portable_by_id[row["opaque_local_id"]] = portable
        portable_conditions.append({
            **row,
            "portable_workshop_reading_de": portable,
            "reading_source": source,
            "local_expansion_de": row["speakable_condition_word_de"],
        })

    revised_marks = []
    for row in marks:
        if row["source_id"] in portable_by_id:
            value = portable_by_id[row["source_id"]]
            lesson = "CONDITION_COMPONENT_COMPOSITION"
        elif row["surface"] in SHARED_SURFACES:
            value = SHARED_SURFACES[row["surface"]]
            lesson = "EXACT_SURFACE_BRIDGE"
        else:
            value = row["concrete_default_de"]
            lesson = "NO_CHANGE"
        revised_marks.append({
            **row,
            "concrete_default_de": value,
            "ninth_lesson": lesson,
            "portable_surface_root_de": SHARED_SURFACES.get(row["surface"], "NONE"),
        })

    identities_to_values: dict[str, set[str]] = defaultdict(set)
    identities_to_lessons: dict[str, set[str]] = defaultdict(set)
    for row in revised_marks:
        identities_to_values[row["identity"]].add(row["concrete_default_de"])
        identities_to_lessons[row["identity"]].add(row["ninth_lesson"])
    assert all(len(values) == 1 for values in identities_to_values.values())
    revised_vocab = []
    for row in vocabulary:
        revised_vocab.append({
            **row,
            "short_value_de": next(iter(identities_to_values[row["identity"]])),
            "ninth_lesson": "|".join(sorted(identities_to_lessons[row["identity"]])),
            "portable_surface_root_de": SHARED_SURFACES.get(row["house_surface"], "NONE"),
        })

    source_unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = source_unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)

    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        literal = "; ".join(str(row["concrete_default_de"]) for row in local)
        revised_units.append({
            **unit,
            "literal_sequence_de": literal,
            "speakable_condition_sequence_de": " -> ".join(str(row["concrete_default_de"]) for row in local) if unit["section"] == "WHEN" else "NONE",
            "cross_register_stems_applied": sum(row["ninth_lesson"] != "NO_CHANGE" for row in local),
        })

    revised_cards = []
    for card in cards:
        local = [row for row in revised_units if row["order_id"] == card["order_id"]]
        revised_cards.append({
            **card,
            "cross_register_surface_bridges": sum(int(row["cross_register_stems_applied"]) for row in local),
            "portable_grammar_complete": "YES",
        })

    write(f"{PREFIX}_8_EXACT_SURFACE_BRIDGES.tsv", surface_rows, list(surface_rows[0]))
    write(f"{PREFIX}_22_SHARED_COMPONENT_ROOTS.tsv", component_rows, list(component_rows[0]))
    write(f"{PREFIX}_73_PORTABLE_CONDITION_READINGS.tsv", portable_conditions, list(portable_conditions[0]))
    write(f"{PREFIX}_231_UNIFIED_WORKSHOP_VOCABULARY.tsv", revised_vocab, list(vocabulary[0]) + ["ninth_lesson", "portable_surface_root_de"])
    write(f"{PREFIX}_437_UNIFIED_MARK_DECK.tsv", revised_marks, list(marks[0]) + ["ninth_lesson", "portable_surface_root_de"])
    write(f"{PREFIX}_118_UNIFIED_UNIT_EDITION.tsv", revised_units, list(units[0]) + ["cross_register_stems_applied"])
    write(f"{PREFIX}_6_UNIFIED_JOB_CARDS.tsv", revised_cards, list(revised_cards[0]))

    lines = [
        "# Gemeinsame Prosa-/Bedingungsgrammatik",
        "",
        "Die Diagramme benutzen jetzt dieselben kleinen Werkstattkerne wie die Prosa.",
        "WASSERLAUF und LICHTLAUF teilen den Kern LAUF; der Besitzer macht daraus Wasser oder Licht.",
        "PFLANZENZUTAT und KOERPERTEIL teilen TEIL; Ziel-, Quellen-, Maß-, Folge- und Haltekerne bleiben ebenfalls gleich.",
        "",
        "## Acht wortgleiche Brücken",
        "",
    ]
    for row in surface_rows:
        lines.append(f"- `{row['surface']}` = **{row['portable_root_de']}** ({row['prose_marks']} Prosa, {row['condition_marks']} Bedingung)")
    lines.extend(["", "## 22 gemeinsame Komponenten", ""])
    for row in component_rows:
        lines.append(f"- `{row['component']}` = **{row['portable_root_de']}**")
    lines.extend(["", "## Die sechs Bedingungsfolgen", ""])
    for unit in revised_units:
        if unit["section"] == "WHEN":
            lines.extend([
                f"### {unit['order_id']} / {unit['stage']}",
                "",
                f"`{unit['back_copy_sequence']}`",
                "",
                unit["speakable_condition_sequence_de"] + ".",
                "",
            ])
    (HERE / f"{PREFIX}_PORTABLE_GRAMMAR_BOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    lesson_counts = Counter(row["ninth_lesson"] for row in revised_marks)
    source_counts = Counter(row["reading_source"] for row in portable_conditions)
    summary = {
        "status": "PASS",
        "decision": "EIGHT_SHARED_SURFACES_AND_TWENTY_TWO_COMPONENT_ROOTS_UNIFY_PROSE_AND_CONDITION_CHANNELS",
        "shared_surfaces": len(surface_rows),
        "shared_surface_marks": sum(int(row["total_marks"]) for row in surface_rows),
        "shared_components": len(component_rows),
        "portable_condition_readings": len(portable_conditions),
        "condition_reading_sources": dict(source_counts),
        "mark_revisions": dict(lesson_counts),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "vocabulary_identities": len(revised_vocab),
        "model_copy_actions": sum(row["apprentice_action"] == "COPY_LOCAL_MODEL" for row in revised_marks),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 898: gemeinsame Prosa-/Bedingungsstämme\n\n"
        "Acht wortgleiche Formen und 22 sichtbare Komponenten erhalten kurze registerübergreifende Kerne. "
        "Der entscheidende Gewinn ist die Trennung von Kern und Bildbesitzer: AIR bedeutet LAUF, während Wasser oder Licht aus der Seite kommt; "
        "AL bedeutet ZIELSTELLE, AIIN MASS, OL FORTSETZEN, Y POSTEN. "
        "So werden die 73 Bedingungszeichen kompositionell lesbar, ohne ein zweites Sonderwörterbuch zu erfinden.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
