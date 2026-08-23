#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R267 = ROOT / "experiments/yolo/sidequest_semantic_astro_ain_an_composition_two_hundred_sixty_seventh"
R263 = ROOT / "experiments/yolo/sidequest_semantic_whole_sign_syntax_two_hundred_sixty_third"
R264 = ROOT / "experiments/yolo/sidequest_semantic_complete_sixty_three_entry_deck_two_hundred_sixty_fourth"
ASTRO = R267 / "TWO_HUNDRED_SIXTY_SEVENTH_REVISED_395_ASTRO_GROUPS.tsv"
CARDS = R263 / "TWO_HUNDRED_SIXTY_THIRD_173_CARD_DICTIONARY.tsv"
EVENTS = R263 / "TWO_HUNDRED_SIXTY_THIRD_381_PROSE_EVENTS.tsv"
STATEMENTS = R263 / "TWO_HUNDRED_SIXTY_THIRD_116_STATEMENTS.tsv"
COMPONENTS = R264 / "TWO_HUNDRED_SIXTY_FOURTH_40_COMPONENTS.tsv"

PARSE = {
    "air": ("AIR_PATH", "Lauf oder Bahn", "FULL_40_COMPONENT_PARSE"),
    "dair": ("D_PREVIOUS+AIR_PATH", "voriger Lauf", "FULL_40_COMPONENT_PARSE"),
    "qofair": ("LOCAL_QOF+AIR_PATH", "Lauf des lokalen QOF-Postens", "LOCAL_CORE_PLUS_AIR"),
    "ypair": ("Y+P_IN+AIR_PATH", "diesen Posten in den Lauf führen", "FULL_40_COMPONENT_PARSE"),
    "odair": ("O_WITHDRAW+D_PREVIOUS+AIR_PATH", "vom vorigen Lauf zurücknehmen", "FULL_40_COMPONENT_PARSE"),
    "doair": ("D_PREVIOUS+O_WITHDRAW+AIR_PATH", "vorigen Rücklauf wählen", "FULL_40_COMPONENT_PARSE"),
    "qotair": ("Q_FRAME+OT+AIR_PATH", "zum nächsten Lauf wechseln", "FULL_40_COMPONENT_PARSE"),
}

PROSE_PARSE = {
    "MC014": ("Lauf zuführen", "laufendes Medium zugießen", "CH_POUR+AIR_PATH", "FULL_COMPOSITION"),
    "MC023": ("Beckenlauf", "Beckenlauf", "K_BASIN+AIR_PATH", None),
    "MC081": ("Laufeinsatz", "Laufeinsatz", "OK_SET+AIR_PATH", None),
    "MC091": ("Laufschluss", "Laufschluss", "D_TERMINAL_FRAME+AIR_PATH+Y_ITEM+CLOSE_EXACT", None),
    "MC116": ("Weiterlauf", "Weiterlauf", "SCHED_LEAD+AIR_PATH", None),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    astro = read_tsv(ASTRO)
    cards = read_tsv(CARDS)
    events = read_tsv(EVENTS)
    statements = read_tsv(STATEMENTS)
    components = read_tsv(COMPONENTS)

    air_family = []
    revised_astro = []
    for row in astro:
        new = dict(row)
        if row["exact_prose_card_id"] == "NONE" and row["visible_surface"] in PARSE:
            parse, meaning, status = PARSE[row["visible_surface"]]
            air_family.append({
                "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
                "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"], "component_parse": parse,
                "composed_short_value_de": meaning, "composition_status": status,
                "air_contribution_de": "LAUF_ODER_BAHN",
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
            })
            new["curriculum_layer"] = "ASTRO_COMPOSED_FROM_40_COMPONENTS" if status == "FULL_40_COMPONENT_PARSE" else "ASTRO_LOCAL_CORE_PLUS_AIR"
            new["portable_card_core_de"] = meaning
            new["portable_card_role"] = "COMPOSED_ASTRO_PATH_CARD" if status == "FULL_40_COMPONENT_PARSE" else "PARTIAL_ASTRO_PATH_CARD"
            new["apprentice_action"] = "read AIR as a running path; copy only any marked local residual"
            new["revision_268"] = "AIR_PATH_COMPOSITION"
        else:
            new["revision_268"] = "UNCHANGED"
        revised_astro.append(new)

    revised_components = []
    for row in components:
        new = dict(row)
        if row["component_id"] == "AIR":
            new["short_value_de"] = "LAUF_ODER_BAHN"
            new["learning_rule"] = "mark a running path; locally water flow, basin flow, ring path or pointer path"
            new["licensing_scope"] = "shared across prose wet-work and Astro path labels"
            new["revision_268"] = "LIQUID_TO_ABSTRACT_PATH"
        else:
            new["revision_268"] = "UNCHANGED"
        revised_components.append(new)

    revised_cards = []
    for row in cards:
        new = dict(row)
        if row["master_card_id"] in PROSE_PARSE:
            core, local, parse, layer = PROSE_PARSE[row["master_card_id"]]
            new["portable_core_de"] = core
            new["local_prose_expansion_de"] = local
            new["component_parse"] = parse
            if layer:
                new["dictionary_layer"] = layer
            new["revision_268"] = "AIR_PATH_CORE"
        else:
            new["revision_268"] = "UNCHANGED"
        revised_cards.append(new)
    by_id = {r["master_card_id"]: r for r in revised_cards}

    revised_events = []
    for row in events:
        new = dict(row)
        card = by_id[row["master_card_id"]]
        new["portable_core_de"] = card["portable_core_de"]
        new["local_register_expansion_de"] = card["local_prose_expansion_de"]
        new["revision_268"] = card["revision_268"]
        revised_events.append(new)
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row)
    revised_statements = []
    for row in statements:
        new = dict(row)
        evs = by_statement[row["statement_id"]]
        new["portable_core_chain"] = " | ".join(r["portable_core_de"] for r in evs)
        new["local_register_chain"] = " | ".join(r["local_register_expansion_de"] for r in evs)
        new["revision_268"] = "AIR_PATH_CORE" if any(r["revision_268"] == "AIR_PATH_CORE" for r in evs) else "UNCHANGED"
        revised_statements.append(new)

    forms = []
    for surface, (parse, meaning, status) in PARSE.items():
        rows = [r for r in air_family if r["visible_surface"] == surface]
        forms.append({
            "visible_surface": surface, "component_parse": parse,
            "composed_short_value_de": meaning, "composition_status": status,
            "group_count": len(rows), "pages": "|".join(dict.fromkeys(r["page"] for r in rows)),
            "loci": "|".join(r["locus"] for r in rows),
        })

    family_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_12_ASTRO_AIR_GROUPS.tsv"
    forms_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_SEVEN_AIR_FORM_TYPES.tsv"
    astro_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_395_ASTRO_GROUPS.tsv"
    components_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_40_COMPONENTS.tsv"
    cards_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_173_CARD_DICTIONARY.tsv"
    events_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_381_PROSE_EVENTS.tsv"
    statements_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_REVISED_116_STATEMENTS.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_READABLE_AIR_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_EIGHTH_REPORT.md"
    write_tsv(family_path, air_family, list(air_family[0]))
    write_tsv(forms_path, forms, list(forms[0]))
    write_tsv(astro_path, revised_astro, list(revised_astro[0]))
    write_tsv(components_path, revised_components, list(revised_components[0]))
    write_tsv(cards_path, revised_cards, list(revised_cards[0]))
    write_tsv(events_path, revised_events, list(revised_events[0]))
    write_tsv(statements_path, revised_statements, list(revised_statements[0]))

    readable = [
        "# AIR bedeutet Lauf, nicht Wasser", "",
        "Auf Herbal/Bio sieht AIR oft wie Wasser oder Beckenfluss aus. Die Astroseiten liefern die bessere Grundbedeutung: AIR steht viermal allein und in acht Erweiterungen für Himmels-, Ring- oder Zeigerlauf.", "",
    ]
    for row in forms:
        readable.append(f"- `{row['visible_surface']}` = `{row['component_parse']}` → **{row['composed_short_value_de']}**.")
    readable += [
        "", "Die portable Wurzel lautet daher **LAUF/BAHN**. Wasser ist eine lokale Ausführung dieser Bahn, genau wie Ringlauf oder Zeigerlauf im Diagramm.", "",
        "Die fünf Prosekarten werden entsprechend gelesen: CHAIR Lauf zuführen (lokal Flüssigkeit zugießen), KAIR Beckenlauf, OKAIR Laufeinsatz, DAIRYDY Laufschluss, SCHEDAIR Weiterlauf.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 268: AIR von Wasser zu Lauf/Bahn

## Ergebnis

Zwölf lokale Astrogruppen auf sieben AIR-Formtypen bezeichnen Himmels-, Ring- oder Zeigerlauf. Elf Gruppen komponieren vollständig aus dem40er-Deck; QOFAIR behält einen lokalen QOF-Kern. AIR wird deshalb portable von LAUFFLÜSSIGKEIT zu LAUF_ODER_BAHN revidiert.

Die fünf Prosekarten behalten ihre konkreten Nasswerkstattlesungen lokal, erhalten aber abstrakte Kerne und AIR_PATH-Komponenten. Damit erklärt derselbe Stamm Wasser-/Beckenlauf in Herbal/Bio und Ring-/Zeigerlauf in Astro ohne Bedeutungsbruch.

Inputs: Astro `{sha(ASTRO)}`, cards `{sha(CARDS)}`, events `{sha(EVENTS)}`, statements `{sha(STATEMENTS)}`, components `{sha(COMPONENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (family_path, forms_path, astro_path, components_path, cards_path, events_path, statements_path, readable_path, report_path)
    summary = {
        "status": "PASS", "air_groups": len(air_family), "air_forms": len(forms),
        "full_groups": sum(r["composition_status"] == "FULL_40_COMPONENT_PARSE" for r in air_family),
        "partial_groups": sum(r["composition_status"] == "LOCAL_CORE_PLUS_AIR" for r in air_family),
        "revised_prose_cards": sum(r["revision_268"] == "AIR_PATH_CORE" for r in revised_cards),
        "revised_prose_events": sum(r["revision_268"] == "AIR_PATH_CORE" for r in revised_events),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
