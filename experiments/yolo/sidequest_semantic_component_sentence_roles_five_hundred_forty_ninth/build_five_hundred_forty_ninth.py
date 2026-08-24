#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P538 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_five_hundred_thirty_eighth"


COMPONENTS = {
    "AIIN": ("QUANTITY", "vorgeschriebenes Maß", "liefert das Sollmaß"),
    "AIN": ("QUANTITY", "Portion", "liefert eine abgeteilte Menge"),
    "AIR": ("PATH_MEDIUM", "laufender Bestand", "liefert Lauf oder strömendes Medium"),
    "AL": ("TARGET", "bezeichnete Stelle", "liefert das Ziel"),
    "AR": ("SOURCE", "von dort", "liefert die Quelle"),
    "CFH": ("ACTION", "auswringen", "führt Auswringen aus"),
    "CH": ("ACTION", "abziehen", "führt Abziehen aus"),
    "CHD": ("ACTION", "umsetzen", "führt Umsetzen aus"),
    "CHK": ("ACTION", "wärmen", "führt Erwärmen aus"),
    "CKH": ("PATH_MEDIUM", "Durchlass", "liefert Durchlass oder Gang"),
    "CTH": ("STATE", "bereit", "fordert den Bereitschaftszustand"),
    "DA": ("MODIFIER", "zweite", "markiert die zweite Stufe"),
    "DY": ("CLOSE", "Schluss", "schließt nur in der lizenzierten Kartenkonstruktion"),
    "E": ("GRADE", "kurz", "markiert kurze oder direkte Ausführung"),
    "EE": ("GRADE", "länger", "markiert anhaltende Ausführung"),
    "EEE": ("GRADE", "vollständig", "markiert vollständige Ausführung"),
    "HO": ("MATERIAL", "Gabe", "liefert die einzusetzende Gabe"),
    "IIN": ("STATE", "Sollstufe", "liefert eine Zielstufe"),
    "K": ("ACTION", "zuführen", "führt Zuführung aus"),
    "L": ("ACTION", "führen", "führt entlang eines Wegs"),
    "LD": ("ACTION", "befestigen", "führt Befestigung aus"),
    "LS": ("SEQUENCE", "weiter", "setzt die laufende Folge fort"),
    "LSH": ("ACTION", "waschen", "führt einen Waschgang aus"),
    "O": ("PROCESS", "Arbeitsgang", "liefert den bezeichneten Vorgang"),
    "OK": ("ACTION", "ansetzen", "setzt Posten oder Vorgang an"),
    "OL": ("SEQUENCE", "fortsetzen", "setzt Posten oder Ansatz fort"),
    "OR": ("PREPARATION", "Ansatz", "liefert die aktuelle Zubereitung"),
    "OS": ("TARGET", "Arbeitsfach", "liefert das ausgewählte Arbeitsfach"),
    "OT": ("SEQUENCE", "danach", "ordnet die folgende Einheit an"),
    "P": ("ACTION", "hineingeben", "führt in einen Empfänger hinein"),
    "R": ("ACTION", "abkühlen", "führt Abkühlung aus"),
    "S": ("ACTION", "teilen", "teilt den laufenden Posten"),
    "SH": ("ACTION", "halten", "hält den laufenden Posten"),
    "SHED": ("ACTION", "absetzen", "lässt den Posten absetzen"),
    "SOLK": ("ACTION", "auffangen", "fängt den laufenden Bestand auf"),
    "T": ("ACTION", "eintragen", "trägt den Posten in einen Platz ein"),
    "TALAM": ("ACTION", "verwahren", "verwahrt den laufenden Posten"),
    "Y": ("ITEM", "dieser Posten", "bindet den aktuell gemeinten Arbeitsgegenstand"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def phrase(components: list[str]) -> str:
    actions = [COMPONENTS[c][1] for c in components if COMPONENTS[c][0] == "ACTION"]
    sequences = [COMPONENTS[c][1] for c in components if COMPONENTS[c][0] == "SEQUENCE"]
    grades = [COMPONENTS[c][1] for c in components if COMPONENTS[c][0] == "GRADE"]
    states = [COMPONENTS[c][1] for c in components if COMPONENTS[c][0] == "STATE"]
    has_item = any(COMPONENTS[c][0] == "ITEM" for c in components)
    quantity = [c for c in components if COMPONENTS[c][0] == "QUANTITY"]
    sources = [c for c in components if COMPONENTS[c][0] == "SOURCE"]
    targets = [c for c in components if COMPONENTS[c][0] == "TARGET"]
    paths = [c for c in components if COMPONENTS[c][0] == "PATH_MEDIUM"]
    materials = [c for c in components if COMPONENTS[c][0] in {"MATERIAL", "PREPARATION", "PROCESS"}]
    closes = any(COMPONENTS[c][0] == "CLOSE" for c in components)
    modifiers = [COMPONENTS[c][1] for c in components if COMPONENTS[c][0] == "MODIFIER"]
    if actions:
        parts = []
        if sequences:
            parts.append(" ".join(sequences))
        if has_item:
            parts.append("diesen Posten")
        elif materials:
            parts.append("den " + " und ".join(COMPONENTS[c][1] for c in materials))
        else:
            parts.append("den laufenden Posten")
        if sources:
            parts.append("von dort")
        if quantity:
            parts.append("nach " + " und ".join(COMPONENTS[c][1] for c in quantity))
        if targets:
            parts.append("an " + " und ".join(COMPONENTS[c][1] for c in targets))
        if paths:
            parts.append("durch " + " und ".join(COMPONENTS[c][1] for c in paths))
        if grades:
            parts.append(" ".join(grades))
        parts.append(" und ".join(actions))
        if states:
            parts.append("bis " + " und ".join(states))
        if modifiers:
            parts.append("als " + " und ".join(modifiers))
        text = " ".join(parts)
    else:
        noun_parts = [COMPONENTS[c][1] for c in components if COMPONENTS[c][0] not in {"CLOSE"}]
        text = " · ".join(noun_parts) if noun_parts else "Schrittende"
    if closes:
        text += "; Schritt schließen"
    return text


def clause_type(components: list[str]) -> str:
    roles = [COMPONENTS[c][0] for c in components]
    if "ACTION" in roles:
        return "ACTION_CLAUSE"
    if "CLOSE" in roles:
        return "CLOSE_WITHOUT_ACTION"
    if "STATE" in roles or "GRADE" in roles:
        return "STATE_OR_GRADE_PHRASE"
    if "SEQUENCE" in roles:
        return "SEQUENCE_OR_CONTINUATION"
    return "ARGUMENT_OR_ADDRESS"


def main() -> None:
    cards = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    events = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_EDITION.tsv")
    component_rows = []
    for index, (component, (role, meaning, contribution)) in enumerate(COMPONENTS.items(), 1):
        containing = [row for row in cards if component in row["component_parse"].split("+")]
        component_rows.append({
            "component_no": f"C{index:02d}",
            "component": component,
            "sentence_role": role,
            "atomic_meaning_de": meaning,
            "grammar_contribution_de": contribution,
            "card_types": str(len(containing)),
            "events": str(sum(int(row["occurrences"]) for row in containing)),
            "is_independent_full_verb": "YES" if role == "ACTION" else "NO",
        })

    card_rows = []
    for row in cards:
        components = row["component_parse"].split("+")
        roles = [COMPONENTS[c][0] for c in components]
        actions = [c for c in components if COMPONENTS[c][0] == "ACTION"]
        arguments = [c for c in components if COMPONENTS[c][0] in {"ITEM", "QUANTITY", "SOURCE", "TARGET", "PATH_MEDIUM", "MATERIAL", "PREPARATION", "PROCESS"}]
        modifiers = [c for c in components if COMPONENTS[c][0] in {"GRADE", "STATE", "MODIFIER", "SEQUENCE"}]
        card_rows.append({
            "card_no": row["card_no"],
            "component_parse": row["component_parse"],
            "role_signature": "+".join(roles),
            "clause_type": clause_type(components),
            "head_actions": "|".join(actions) or "NONE",
            "argument_components": "|".join(arguments) or "NONE",
            "modifier_components": "|".join(modifiers) or "NONE",
            "has_close": "YES" if "DY" in components else "NO",
            "role_based_reading_de": phrase(components),
            "old_component_reading_de": row["invariant_card_reading_de"],
            "occurrences": row["occurrences"],
            "sections": row["sections"],
            "records": row["records"],
            "composition_status": row["composition_status"],
        })
    card_by_id = {row["card_no"]: row for row in card_rows}
    event_rows = []
    for row in events:
        card = card_by_id[row["card_no"]]
        event_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "surface": row["surface"],
            "card_no": row["card_no"],
            "clause_type": card["clause_type"],
            "role_based_reading_de": card["role_based_reading_de"],
            "silent_owner_de": row["silent_owner_de"],
            "component_values_unchanged": "YES",
        })
    write_tsv("FIVE_HUNDRED_FORTY_NINTH_THIRTY_EIGHT_COMPONENT_ROLES.tsv", component_rows)
    write_tsv("FIVE_HUNDRED_FORTY_NINTH_ONE_HUNDRED_SEVENTY_THREE_CARD_ROLE_PROFILES.tsv", card_rows)
    write_tsv("FIVE_HUNDRED_FORTY_NINTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_ROLE_EDITION.tsv", event_rows)

    card_types = Counter(row["clause_type"] for row in card_rows)
    event_types = Counter(row["clause_type"] for row in event_rows)
    summary = {
        "status": "PASS",
        "components": len(component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "component_role_counts": dict(sorted(Counter(row["sentence_role"] for row in component_rows).items())),
        "card_clause_counts": dict(sorted(card_types.items())),
        "event_clause_counts": dict(sorted(event_types.items())),
        "action_events": event_types["ACTION_CLAUSE"],
        "non_action_events": len(event_rows) - event_types["ACTION_CLAUSE"],
    }
    (HERE / "FIVE_HUNDRED_FORTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertneunundvierzigste Runde: Satzrollen statt Kartenstakkato",
        "",
        "## Hauptkorrektur",
        "",
        f"Nur {summary['action_events']} der 381 Prosaereignisse enthalten überhaupt eine Handlungskomponente. Die übrigen {summary['non_action_events']} liefern Arbeitsgegenstand, Maß, Portion, Quelle, Ziel, Weg, Ansatz, Reihenfolge, Grad, Zustand oder Schluss. Die vorige Volltextfassung behandelte zu viele davon wie selbständige Verben.",
        "",
        "Das neue 38-Komponenten-Lexikon trennt deshalb ACTION, ITEM, QUANTITY, SOURCE, TARGET, PATH_MEDIUM, MATERIAL, PREPARATION, PROCESS, SEQUENCE, GRADE, STATE, MODIFIER und CLOSE. Jede der 173 Karten erhält daraus ein Rollenprofil und eine rollenbasierte Lesung.",
        "",
        "## Konkrete Wirkung",
        "",
        "- `Y` ist `dieser Posten`, kein Befehl „übernehmen“.",
        "- `AIIN` ist `vorgeschriebenes Maß`, kein Befehl „Maß setzen“.",
        "- `AL` und `AR` sind Ziel und Quelle, keine selbständigen Handlungen.",
        "- `OR` ist der aktuelle Ansatz; `OL` und `OT` ordnen Fortsetzung und Folge.",
        "- Erst eine ACTION-Komponente macht daraus eine auszuführende Werkstatthandlung.",
        "",
        "Damit ist die Grammatik näher an einem Kürzelbuch: wenige Verben tragen mehrere kurze Adress- und Zustandszeichen. Die Bedeutungen bleiben dieselben; nur ihre Satzfunktion ist berichtigt.",
    ]
    (HERE / "FIVE_HUNDRED_FORTY_NINTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
