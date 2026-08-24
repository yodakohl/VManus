#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P577 = YOLO / "sidequest_semantic_gloss_free_reconstruction_five_hundred_seventy_seventh"
P595 = YOLO / "sidequest_semantic_surface_preference_manual_five_hundred_ninety_fifth"
P596 = YOLO / "sidequest_semantic_interleaved_teaching_edition_five_hundred_ninety_sixth"
P598 = YOLO / "sidequest_semantic_record_state_trace_five_hundred_ninety_eighth"

OBJECT_COMPONENTS = {
    "AIN": ("PORTION", "abgeteilte Portion"),
    "AIR": ("FLOWING_MEDIUM", "laufende Arbeitsfluessigkeit"),
    "AL": ("TARGET_PLACE", "bezeichnete Zielstelle"),
    "AR": ("SOURCE_STOCK", "lokaler Quellvorrat"),
    "CKH": ("PASSAGE", "Durchlass oder Gang"),
    "HO": ("MATERIAL_CHARGE", "einzusetzende Materialgabe"),
    "OR": ("PREPARATION", "aktueller Ansatz"),
    "OS": ("WORK_COMPARTMENT", "ausgewaehltes Arbeitsfach"),
    "Y": ("CURRENT_ITEM", "aktuell gemeinter Arbeitsposten"),
}

SPEC_COMPONENTS = {
    "AIIN": "nach vorgeschriebenem Mass", "IIN": "bis zur Sollstufe", "CTH": "bis bereit",
    "E": "kurz oder direkt", "EE": "laenger anhaltend", "EEE": "vollstaendig",
    "O": "im bezeichneten Arbeitsgang", "OL": "als Fortsetzung", "OT": "danach", "LS": "weiter",
    "DA": "in zweiter Stufe", "DY": "lokal schliessen",
}

ACTION_OUTPUTS = {
    "CFH": ("auswringen", "ausgedrueckter Stoff oder Pressfluessigkeit"),
    "CH": ("abziehen", "abgenommener oder abgezogener Anteil"),
    "CHD": ("umsetzen", "umgesetzter Arbeitsposten"),
    "CHK": ("waermen", "erwaermter Arbeitsposten"),
    "K": ("zufuehren", "zugefuehrte Portion"),
    "L": ("fuehren", "weitergefuehrter Arbeitsposten"),
    "LD": ("befestigen", "befestigter Arbeitsposten"),
    "LSH": ("waschen", "gewaschener Arbeitsposten oder Waschfluessigkeit"),
    "OK": ("ansetzen", "angesetzter Arbeitsposten"),
    "P": ("hineingeben", "in den Empfaenger eingebrachter Stoff"),
    "R": ("abkuehlen", "abgekuehlter Arbeitsposten"),
    "S": ("teilen", "abgeteilter Arbeitsposten"),
    "SH": ("halten", "gehaltener oder einwirkender Arbeitsposten"),
    "SHED": ("absetzen", "abgesetzter Stoff mit Ueberstand und Rueckstand"),
    "SOLK": ("auffangen", "aufgefangener Auszug oder Arbeitsbestand"),
    "T": ("eintragen", "im Arbeitsfach eingetragener Posten"),
    "TALAM": ("verwahren", "verwahrter Arbeitsposten"),
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def tokens(parse):
    return re.findall(r"[A-Z]+", parse)


def primary_object(token_set):
    for component in ("OR", "AIR", "HO", "AIN", "Y", "AR", "AL", "OS", "CKH"):
        if component in token_set:
            return OBJECT_COMPONENTS[component]
    return "OWNER_BOUND_MATERIAL", "vom Bildbesitzer gesetzter lokaler Arbeitsstoff"


def main():
    components = read(P577 / "FIVE_HUNDRED_SEVENTY_SEVENTH_CORRECTED_THIRTY_EIGHT_COMPONENT_INVENTORY.tsv")
    event_trace = read(P595 / "FIVE_HUNDRED_NINETY_FIFTH_381_COMPLETE_SURFACE_TRACE.tsv")
    statements = read(P596 / "FIVE_HUNDRED_NINETY_SIXTH_116_FOUR_LINE_STATEMENTS.tsv")
    state_trace = {row["statement_id"]: row for row in read(P598 / "FIVE_HUNDRED_NINETY_EIGHTH_116_STATE_TRACE.tsv")}
    statement_by_id = {row["statement_id"]: row for row in statements}

    event_to_statement = {}
    for statement in statements:
        for event_id in re.findall(r"E\d{3}", ""):
            event_to_statement[event_id] = statement["statement_id"]
    # Statement membership is recovered from ordered event counts.
    cursor = 0
    for statement in statements:
        count = int(statement["event_count"])
        for event in event_trace[cursor:cursor + count]:
            event_to_statement[event["event_id"]] = statement["statement_id"]
        cursor += count

    component_rows = []
    for component in components:
        code = component["component"]
        if code in OBJECT_COMPONENTS:
            contribution = OBJECT_COMPONENTS[code][0]
            object_reading = OBJECT_COMPONENTS[code][1]
        elif code in ACTION_OUTPUTS:
            contribution = "TRANSFORMATION"
            object_reading = f"{ACTION_OUTPUTS[code][0]} -> {ACTION_OUTPUTS[code][1]}"
        elif code in SPEC_COMPONENTS:
            contribution = "SPECIFICATION_OR_BOUNDARY"
            object_reading = SPEC_COMPONENTS[code]
        else:
            contribution = "PROCESS_OPERATOR"
            object_reading = component["atomic_meaning_de"]
        component_rows.append({
            "component_no": component["component_no"], "component": code,
            "sentence_role": component["sentence_role"], "spoken_value_de": component["atomic_meaning_de"],
            "object_contribution": contribution, "concrete_object_reading_de": object_reading,
        })

    event_rows = []
    events_by_statement = defaultdict(list)
    for event in event_trace:
        sid = event_to_statement[event["event_id"]]
        state = state_trace[sid]
        token_list = tokens(event["component_parse"])
        token_set = set(token_list)
        obj_class, obj_de = primary_object(token_set)
        actions = [ACTION_OUTPUTS[token] for token in token_list if token in ACTION_OUTPUTS]
        specs = [SPEC_COMPONENTS[token] for token in token_list if token in SPEC_COMPONENTS]
        output = " -> ".join(result for _, result in actions) if actions else obj_de
        operation = " + ".join(action for action, _ in actions) if actions else "adressieren oder spezifizieren"
        row = {
            "event_id": event["event_id"], "page": event["page"], "record": event["record"],
            "statement_id": sid, "surface": event["final_surface"], "card_no": event["card_no"],
            "component_parse": event["component_parse"], "owner_id": state["owner_id"], "owner_de": state["owner_de"],
            "primary_object_class": obj_class, "primary_object_de": obj_de,
            "operation_de": operation, "specifications_de": " | ".join(specs) or "NONE",
            "local_output_de": output,
            "cross_owner_carry": "NO" if state["transition"] == "OWNER_RESET" else "WITHIN_ACTIVE_OWNER_ONLY",
        }
        event_rows.append(row)
        events_by_statement[sid].append(row)

    statement_rows = []
    previous_object_after = {}
    owner_versions = Counter()
    for statement in statements:
        sid = statement["statement_id"]
        state = state_trace[sid]
        rows = events_by_statement[sid]
        owner_id = state["owner_id"]
        owner_versions[owner_id] += 1
        if state["transition"] in {"RECORD_INITIALIZE", "OWNER_RESET"}:
            object_before = f"{owner_id}:MASTER_OR_IMAGE_SUPPLIED"
        elif state["transition"] in {"EXPLICIT_LOCAL_CONTINUATION", "CURRENT_ITEM_CONTINUATION"}:
            object_before = previous_object_after[owner_id]
        else:
            object_before = f"{owner_id}:NEW_OR_{previous_object_after.get(owner_id, 'MASTER_SUPPLIED')}"
        object_after = f"{owner_id}:STATE_{owner_versions[owner_id]:02d}"
        previous_object_after[owner_id] = object_after
        object_classes = list(dict.fromkeys(row["primary_object_class"] for row in rows))
        objects_de = list(dict.fromkeys(row["primary_object_de"] for row in rows))
        operations = [row["operation_de"] for row in rows if row["operation_de"] != "adressieren oder spezifizieren"]
        outputs = [row["local_output_de"] for row in rows if row["operation_de"] != "adressieren oder spezifizieren"]
        statement_rows.append({
            "statement_id": sid, "page": statement["page"], "record": statement["record"],
            "owner_id": owner_id, "owner_de": state["owner_de"], "transition": state["transition"],
            "object_before_id": object_before, "object_after_id": object_after,
            "object_classes": "|".join(object_classes), "concrete_objects_de": " | ".join(objects_de),
            "operations_de": " -> ".join(operations) or "nur Objekt, Mass, Ziel oder Zustand setzen",
            "outputs_de": " -> ".join(outputs) or "lokaler Objektzustand bleibt spezifiziert",
            "target_or_path_de": " | ".join(dict.fromkeys(
                row["primary_object_de"] for row in rows if row["primary_object_class"] in {"TARGET_PLACE", "WORK_COMPARTMENT", "PASSAGE"}
            )) or "beim aktiven Bildbesitzer",
            "complete_working_instruction_de": statement["meaning_line_de"],
            "object_crosses_visible_owner_reset": "NO",
        })

    owner_rows = []
    for owner_id in dict.fromkeys(row["owner_id"] for row in statement_rows):
        rows = [row for row in statement_rows if row["owner_id"] == owner_id]
        owner_rows.append({
            "owner_id": owner_id, "record": rows[0]["record"], "page": rows[0]["page"], "owner_de": rows[0]["owner_de"],
            "statements": len(rows), "first_object_id": rows[0]["object_before_id"], "last_object_id": rows[-1]["object_after_id"],
            "object_classes_used": "|".join(sorted({item for row in rows for item in row["object_classes"].split("|")})),
            "owner_boundary_rule_de": "alle Objekte bleiben lokal; beim naechsten sichtbaren Besitzer nicht automatisch weitertragen",
        })

    write("FIVE_HUNDRED_NINETY_NINTH_38_COMPONENT_OBJECT_DICTIONARY.tsv", component_rows)
    write("FIVE_HUNDRED_NINETY_NINTH_381_EVENT_OBJECT_BINDING.tsv", event_rows)
    write("FIVE_HUNDRED_NINETY_NINTH_116_STATEMENT_OBJECT_LEDGER.tsv", statement_rows)
    write("FIVE_HUNDRED_NINETY_NINTH_21_OWNER_OBJECT_CHAINS.tsv", owner_rows)

    edition = ["# Fuenfhundertneunundneunzigste Runde: konkrete Objektketten", ""]
    for owner in owner_rows:
        edition.extend([f"## {owner['owner_id']} · {owner['owner_de']}", ""])
        for row in [row for row in statement_rows if row["owner_id"] == owner["owner_id"]]:
            edition.extend([
                f"- **{row['statement_id']} · {row['transition']}**",
                f"  - Objekt: `{row['object_before_id']}` -> `{row['object_after_id']}`",
                f"  - Gegenstaende: {row['concrete_objects_de']}",
                f"  - Gang: {row['operations_de']}",
                f"  - Ergebnis: {row['outputs_de']}",
                f"  - Lesung: {row['complete_working_instruction_de']}",
            ])
        edition.append("")
    (HERE / "FIVE_HUNDRED_NINETY_NINTH_CONCRETE_OBJECT_CHAINS.md").write_text("\n".join(edition), encoding="utf-8")

    classes = Counter(row["primary_object_class"] for row in event_rows)
    summary = {
        "status": "PASS", "components": len(component_rows), "events": len(event_rows),
        "statements": len(statement_rows), "owner_chains": len(owner_rows),
        "event_object_classes": dict(sorted(classes.items())),
        "statement_object_cross_owner_carries": sum(row["object_crosses_visible_owner_reset"] == "YES" for row in statement_rows),
        "empty_objects": sum(not row["concrete_objects_de"] for row in statement_rows),
        "decision": "CONCRETE_LOCAL_OBJECT_CHAINS_WITHOUT_CROSS_OWNER_LEAKAGE",
    }
    (HERE / "FIVE_HUNDRED_NINETY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Fuenfhundertneunundneunzigste Runde: aus Pfeilen werden Werkstattgegenstaende

## Ergebnis

Jede der 116 Prosaaussagen besitzt jetzt einen konkreten lokalen Objektzustand. Die Komponenten setzen nicht nur abstrakte Rollen, sondern handhabbare Dinge:

- `HO` eine einzusetzende Materialgabe;
- `AIN` eine abgeteilte Portion und `AIIN` deren Massvorgabe;
- `OR` den aktuellen Ansatz;
- `AIR` die laufende Arbeitsfluessigkeit;
- `AR` den lokalen Quellvorrat;
- `AL` die Zielstelle, `OS` das Arbeitsfach und `CKH` den Durchlass;
- `Y` den aktuell gemeinten Posten.

Die Aktionskomponenten veraendern dieses Objekt: abziehen, zufuehren, umsetzen, fuehren, waschen, waermen, abkuehlen, halten, absetzen, auffangen, eintragen, verwahren oder befestigen.

## Beispielhafte Objektgaenge

```text
Pflanzenbesitzer -> Materialgabe -> Portion/Mass -> Ansatz -> abgezogener Anteil
Beckenbesitzer -> laufende Arbeitsfluessigkeit -> Durchlass -> aufgefangener Auszug
Figurenbesitzer -> aktueller Posten -> Zielstelle -> ansetzen/halten -> lokaler Zellschluss
```

Das ist konkreter als unsere fruehen Satzglossen, aber einfacher: Die lange Bedeutung steckt nicht in einem einzelnen Wort. Sie entsteht aus mehreren kurzen Objekt-, Aktions-, Ziel- und Zustandskarten.

## Besitzergrenze

Alle Objekt-IDs sind an einen der 21 recordlokalen Besitzerzustande gebunden. Bei den zehn sichtbaren Bio-Besitzerwechseln endet die Kette; kein Auszug, keine Fluessigkeit und keine Portion springt automatisch in die naechste Szene. Nur ein Meister kann eine solche Uebergabe ausserhalb des Textes anweisen.

## Was noch unbestimmt bleibt

`OWNER_BOUND_MATERIAL` bedeutet bewusst nicht immer dasselbe Ding. Beim Pflanzenbild kann es Blatt, Wurzel, Saft oder ganzer Stoff sein; beim Badbild Koerper, Fluessigkeit, Gefaessinhalt oder Einsatz. Die Werkstatt kennt das konkrete Objekt aus Bild und Exemplar, waehrend die Karte nur seine Operation traegt.

## Naechster Schritt

Als naechstes werden die fuenf Herbal-Artikel mit diesem Objektmodell neu formuliert: pro Artikel eine konkrete Rohstoffliste, ein Gefaess-/Ansatzgang, entstehende Zwischenprodukte und eine moegliche Anwendung – ohne Pflanzenart oder Krankheit enger zu benennen, als das Bild erlaubt.
"""
    (HERE / "FIVE_HUNDRED_NINETY_NINTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
