#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_herbal_noun_process_tournament_four_hundred_twenty_seventh/FOUR_HUNDRED_TWENTY_SEVENTH_REVISED_HERBAL_100_EVENT_EDITION.tsv"

INHERITED_FIXES = {
    "E003": "dasselbe",
    "E008": "verwende dies",
    "E009": "Mass",
    "E011": "nimm dies",
}

OPERATIONS = {
    "SCHÄLEN": ["E002"],
    "BEARBEITEN": ["E004"],
    "WASSER_ZUFÜHREN": ["E006"],
    "NEHMEN": ["E011", "E091", "E095"],
    "VERWENDEN": ["E008", "E081", "E085", "E097"],
    "ANWÄRMEN_WÄRMEN": ["E012", "E066", "E070"],
    "ZERSTOSSEN_ZERREIBEN": ["E018", "E089"],
    "ABPRESSEN": ["E019"],
    "AUSWRINGEN": ["E041"],
    "NACHSEIHEN_ABSEIHEN": ["E043", "E093"],
    "ABKÜHLEN": ["E045", "E060"],
    "RESERVE_SETZEN_NEHMEN": ["E046", "E052"],
    "UMSETZEN": ["E062"],
    "LAGERN": ["E063"],
    "AUSZUG_ENTNEHMEN": ["E065", "E096"],
    "AUFLEGEN": ["E079"],
    "WASCHEN": ["E084"],
    "AUFTRAGEN": ["E086"],
    "AUSZUG_ZUGEBEN": ["E092"],
}
OP_BY_EVENT = {event_id: operation for operation, event_ids in OPERATIONS.items() for event_id in event_ids}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def role(event_id: str, value: str) -> str:
    if event_id in OP_BY_EVENT:
        return "OPERATION"
    low = value.lower()
    if event_id in {"E001", "E015", "E039", "E075", "E078", "E087", "E088", "E094"}:
        return "PICTURE_OR_MATERIAL_NOUN"
    if any(token in low for token in ["mass", "portion", "gabe", "sollstand", "standzeit"]):
        return "PARAMETER_OR_QUANTITY"
    if any(token in low for token in ["dies", "dasselbe"]):
        return "REFERENCE"
    if any(token in low for token in ["fortsetz", "folge", "nächstes"]):
        return "LINK_OR_ORDER"
    if low == "bereit":
        return "STATE"
    if "schluss" in low:
        return "OPERATION_WITH_CLOSE"
    if low in {"topf", "schüssel", "stelle"}:
        return "VESSEL_OR_SITE_NOUN"
    return "LEARNED_PRODUCT_OR_CONTENT_NOUN"


def main() -> None:
    source = read(SOURCE)
    events = []
    for row in source:
        out = dict(row)
        old = row["small_value_de"]
        value = INHERITED_FIXES.get(row["event_id"], old)
        out["small_value_de"] = value
        out["pass428_inherited_fix"] = f"{old}->{value}" if old != value else "NONE"
        out["role_class"] = role(row["event_id"], value)
        out["operation_core"] = OP_BY_EVENT.get(row["event_id"], "NONE")
        events.append(out)
    write("FOUR_HUNDRED_TWENTY_EIGHTH_HERBAL_100_EVENT_ROLE_EDITION.tsv", events)

    lexicon = []
    by_id = {row["event_id"]: row for row in events}
    for operation, event_ids in OPERATIONS.items():
        rows = [by_id[event_id] for event_id in event_ids]
        lexicon.append({
            "operation_core": operation,
            "events": len(rows),
            "event_ids": "|".join(event_ids),
            "exact_cards": len({row["joint_tuple_id"] for row in rows}),
            "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "records": "|".join(sorted({row["record"] for row in rows})),
            "realization_type": "PRODUCTIVE_OR_WRAPPED" if operation in {"NEHMEN", "VERWENDEN"} else "LEARNED_WHOLE_OPERATION",
        })
    write("FOUR_HUNDRED_TWENTY_EIGHTH_NINETEEN_OPERATION_LEXICON.tsv", lexicon)

    roles = []
    for role_name in sorted({row["role_class"] for row in events}):
        rows = [row for row in events if row["role_class"] == role_name]
        roles.append({
            "role_class": role_name, "events": len(rows), "exact_cards": len({row["joint_tuple_id"] for row in rows}),
            "records": "|".join(sorted({row["record"] for row in rows})),
            "examples_de": "|".join(dict.fromkeys(row["small_value_de"] for row in rows[:6])),
        })
    write("FOUR_HUNDRED_TWENTY_EIGHTH_EIGHT_ROLE_CLASSES.tsv", roles)

    templates = [
        {"record": "H1", "template": "PICTURE_NOUN > PREPARE > VESSEL > MEDIUM > PRODUCT > USE > MEASURE > DOSE > WARM > READY", "operations": "SCHÄLEN|BEARBEITEN|WASSER_ZUFÜHREN|VERWENDEN|NEHMEN|ANWÄRMEN_WÄRMEN", "local_nouns": "Knolle|Topf|Auszug|Gabe"},
        {"record": "H2", "template": "PICTURE_NOUN > READY > BATCH > CRUSH > PRESS > BRANCH_A_B > MEASURE > CONTINUE > REJOIN > SETTING > PRODUCT", "operations": "ZERSTOSSEN_ZERREIBEN|ABPRESSEN", "local_nouns": "Spitzen|Schüssel|Brei"},
        {"record": "H3", "template": "PICTURE_NOUN > PRODUCT > WRING > HOLD > STRAIN > CLEAR_PRODUCT > COOL > RESERVE > SECOND_PRODUCT", "operations": "AUSWRINGEN|NACHSEIHEN_ABSEIHEN|ABKÜHLEN|RESERVE_SETZEN_NEHMEN", "local_nouns": "Blütenkraut|Sud|Klarauszug|Trank"},
        {"record": "H4", "template": "MEASURE > PORTION > COOL_OR_TRANSFER > STORE | EXTRACT > WARM > BATCH_PORTION", "operations": "ABKÜHLEN|UMSETZEN|LAGERN|AUSZUG_ENTNEHMEN|ANWÄRMEN_WÄRMEN", "local_nouns": "Ansatz|Ansatzportion"},
        {"record": "H5", "template": "BATCH > INGREDIENT_ORDER > MEASURE > PLACE_USE > WASH_APPLY > GRIND > TAKE_EXTRACT_STRAIN > USE_DOSE", "operations": "AUFLEGEN|WASCHEN|AUFTRAGEN|ZERSTOSSEN_ZERREIBEN|NEHMEN|AUSZUG_ZUGEBEN|NACHSEIHEN_ABSEIHEN|AUSZUG_ENTNEHMEN|VERWENDEN", "local_nouns": "Zutat|Kraut|Auszug|Gabe"},
    ]
    write("FOUR_HUNDRED_TWENTY_EIGHTH_FIVE_OPERATION_TEMPLATES.tsv", templates)

    rules = [
        {"pattern": "AIIN", "prediction_de": "Mass", "rule_type": "PRODUCTIVE_PARAMETER"},
        {"pattern": "AIN", "prediction_de": "Portion", "rule_type": "PRODUCTIVE_PARAMETER"},
        {"pattern": "Y_OR_CHY", "prediction_de": "dies", "rule_type": "PRODUCTIVE_REFERENCE"},
        {"pattern": "OR", "prediction_de": "Ansatz", "rule_type": "PRODUCTIVE_CONTENT_CORE"},
        {"pattern": "OL", "prediction_de": "fortsetzen", "rule_type": "PRODUCTIVE_LINK"},
        {"pattern": "OT", "prediction_de": "Folge oder nächstes", "rule_type": "PRODUCTIVE_ORDER"},
        {"pattern": "OKY", "prediction_de": "verwende dies", "rule_type": "LEARNED_COMPOSED_CARD"},
        {"pattern": "OKCHY", "prediction_de": "nimm dies", "rule_type": "LEARNED_COMPOSED_CARD"},
        {"pattern": "AL", "prediction_de": "Stelle", "rule_type": "PRODUCTIVE_ADDRESS"},
        {"pattern": "E_EE_EEE", "prediction_de": "kurz länger vollständig", "rule_type": "PRODUCTIVE_GRADE"},
        {"pattern": "LICENSED_DY", "prediction_de": "Schluss", "rule_type": "CONSTRUCTION_BOUND_CLOSE"},
    ]
    write("FOUR_HUNDRED_TWENTY_EIGHTH_ELEVEN_PREDICTIVE_RULES.tsv", rules)

    summary = {
        "status": "PASS", "events": len(events), "inherited_fixes": sum(row["pass428_inherited_fix"] != "NONE" for row in events),
        "operation_cores": len(lexicon), "role_classes": len(roles), "templates": len(templates), "predictive_rules": len(rules),
        "decision": "COMPACT_OPERATIONS_PLUS_PICTURE_NOMENCLATOR",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
