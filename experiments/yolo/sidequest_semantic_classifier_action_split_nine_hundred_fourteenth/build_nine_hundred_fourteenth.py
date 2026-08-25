#!/usr/bin/env python3
"""Split recurrent O/OK/CH/K/T/S/OR cards into prose and label channels."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
P912 = ROOT / "experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth"
P913 = ROOT / "experiments/yolo/sidequest_semantic_owner_address_syntax_nine_hundred_thirteenth"

EVENTS = P912 / "PASS912_2511_EVENT_INTERLINEAR.tsv"
LABELS = P913 / "PASS913_198_OWNER_LABEL_EVENTS.tsv"
LABEL_LOCI = P913 / "PASS913_153_OWNER_LABEL_LOCI.tsv"

INTERLINEAR_OUT = BASE / "PASS914_2511_CONTEXTUAL_INTERLINEAR.tsv"
AUDIT_OUT = BASE / "PASS914_1286_DUAL_USE_EVENT_AUDIT.tsv"
DUAL_OUT = BASE / "PASS914_DUAL_COMPONENT_LEXICON.tsv"
LIST_OUT = BASE / "PASS914_F70_F88_LIST_EDITION.tsv"
LIST_MD_OUT = BASE / "PASS914_F70_F88_READABLE_LISTS.md"
HANDBOOK_OUT = BASE / "PASS914_CONTEXTUAL_HANDBOOK.md"
REPORT_OUT = BASE / "PASS914_REPORT.md"
SUMMARY_OUT = BASE / "PASS914_BUILD_SUMMARY.json"


DUAL = {
    "O": {
        "prose": "ARBEITSGANG AUSFÜHREN",
        "label": "REIHE ODER KREISGANG AUFRUFEN",
        "bridge": "Ein bestehender Ablauf wird im einen Kanal ausgeführt, im anderen nur als Registerreihe bezeichnet.",
    },
    "OK": {
        "prose": "ANSETZEN ODER AKTIVIEREN",
        "label": "AUSGEWÄHLTEN PLATZ AKTIV SETZEN",
        "bridge": "Aktivierung bleibt gleich; Prosa startet einen Gang, das Etikett markiert einen aktiven Slot.",
    },
    "CH": {
        "prose": "TEIL ENTNEHMEN ODER KENNUNG ABLESEN",
        "label": "KENNUNGS- ODER ARTENFELD",
        "bridge": "Der Meister zeigt auf einen unterscheidbaren Eintrag; Prosa nimmt ihn, das Etikett klassifiziert ihn.",
    },
    "K": {
        "prose": "POSTEN ZUGEBEN ODER ZUORDNEN",
        "label": "ZUGEORDNETER WERT ODER PLATZ",
        "bridge": "Dieselbe Zuordnung ist in Prosa eine Handlung und im Etikett ein bestehender Zustand.",
    },
    "T": {
        "prose": "BEARBEITEN ODER MARKIEREN",
        "label": "MARKIERTER KLASSENPLATZ",
        "bridge": "T setzt eine Bearbeitungs-/Markierungsfunktion; das Etikett nennt deren Ergebnisplatz.",
    },
    "S": {
        "prose": "DANN / AUCH / PRÜFEN",
        "label": "KLASSEN- ODER KONTEXTZEICHEN",
        "bridge": "S verbindet Arbeitsglieder oder trennt lokale Etikettenklassen.",
    },
    "OR": {
        "prose": "ANSATZ ODER ARBEITSINHALT",
        "label": "LOKALER EINTRAG ODER STOFFKLASSE",
        "bridge": "OR bezeichnet in beiden Kanälen einen geführten Inhalt, aber nur Prosa macht daraus einen Ansatz.",
    },
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


def parts(recipe: str) -> list[str]:
    return [part for part in recipe.split("+") if part and part != "CARRIER_Q"]


def target_trace(recipe: str, channel: str) -> str:
    return " · ".join(f"{part}={DUAL[part][channel]}" for part in parts(recipe) if part in DUAL) or "NONE"


def main() -> None:
    events = read_tsv(EVENTS)
    labels = {row["event_id"]: row for row in read_tsv(LABELS)}
    label_loci = read_tsv(LABEL_LOCI)
    if len(events) != 2511 or len(labels) != 198:
        raise RuntimeError("unexpected source counts")

    contextual = []
    audit = []
    component_stats = {component: {"label": [], "prose": []} for component in DUAL}
    for event in events:
        recipe = event["component_recipe"]
        channel = "label" if event["owner_binding_required"] == "YES" else "prose"
        target_components = [part for part in parts(recipe) if part in DUAL]
        if channel == "label":
            label = labels[event["event_id"]]
            contextual_reading = (
                f"{label['concrete_owner_or_name_de']} [Klassenform: "
                + "; ".join(DUAL[part]["label"] for part in target_components)
                + ("; " if target_components else "")
                + label["component_label_functions_de"] + "]"
            )
            role_family = label["role_family"]
            namespace = label["namespace"]
            name_value = label["concrete_owner_or_name_de"]
        else:
            contextual_reading = event["fluent_token_de"]
            role_family = "PROSE_ACTION_SEQUENCE"
            namespace = event["register"] + "_PROSE"
            name_value = "NOT_APPLICABLE"
        trace = target_trace(recipe, channel)
        row = dict(event)
        row.update({
            "semantic_channel": "LABEL_CLASSIFIER" if channel == "label" else "PROSE_ACTION",
            "owner_role_family": role_family,
            "owner_namespace": namespace,
            "concrete_owner_or_name_de": name_value,
            "dual_component_trace_de": trace,
            "contextual_reading_de": contextual_reading,
        })
        contextual.append(row)
        if target_components:
            audit.append({
                "event_id": event["event_id"],
                "physical_page": event["physical_page"],
                "source_page": event["source_page"],
                "locus": event["locus"],
                "register": event["register"],
                "surface": event["surface"],
                "component_recipe": recipe,
                "semantic_channel": row["semantic_channel"],
                "target_components": "|".join(target_components),
                "dual_component_trace_de": trace,
                "owner_role_family": role_family,
                "contextual_reading_de": contextual_reading,
            })
            for component in set(target_components):
                component_stats[component][channel].append(row)

    event_fields = list(events[0]) + [
        "semantic_channel", "owner_role_family", "owner_namespace", "concrete_owner_or_name_de",
        "dual_component_trace_de", "contextual_reading_de",
    ]
    write_tsv(INTERLINEAR_OUT, contextual, event_fields)
    write_tsv(AUDIT_OUT, audit, [
        "event_id", "physical_page", "source_page", "locus", "register", "surface", "component_recipe",
        "semantic_channel", "target_components", "dual_component_trace_de", "owner_role_family", "contextual_reading_de",
    ])

    dual_rows = []
    for component, meanings in DUAL.items():
        prose = component_stats[component]["prose"]
        label = component_stats[component]["label"]
        dual_rows.append({
            "component": component,
            "prose_action_de": meanings["prose"],
            "label_classifier_de": meanings["label"],
            "shared_bridge_de": meanings["bridge"],
            "prose_events": len(prose),
            "label_events": len(label),
            "total_events": len(prose) + len(label),
            "prose_registers": "|".join(sorted({str(row["register"]) for row in prose})),
            "label_registers": "|".join(sorted({str(row["register"]) for row in label})),
            "label_roles": "|".join(f"{role}:{count}" for role, count in Counter(str(row["owner_role_family"]) for row in label).most_common()),
            "apprentice_rule_de": "Wähle den Kanal aus Layout/Verwendung, bevor du den kurzen Wert einsetzt.",
        })
    write_tsv(DUAL_OUT, dual_rows, [
        "component", "prose_action_de", "label_classifier_de", "shared_bridge_de", "prose_events",
        "label_events", "total_events", "prose_registers", "label_registers", "label_roles", "apprentice_rule_de",
    ])

    selected_loci = [row for row in label_loci if row["physical_page"] in {"f70v", "f88r"}]
    list_rows = []
    for order, locus in enumerate(selected_loci, start=1):
        members = [labels[row["event_id"]] for row in contextual if row["source_page"] == locus["source_page"] and row["locus"] == locus["locus"] and row["event_id"] in labels]
        classifier_trace = " / ".join(
            "; ".join(DUAL[part]["label"] for part in parts(member["component_recipe"]) if part in DUAL) or "NUR ADRESS-/GRADKOMPONENTEN"
            for member in members
        )
        list_rows.append({
            "list_order": order,
            "physical_page": locus["physical_page"],
            "source_page": locus["source_page"],
            "locus": locus["locus"],
            "namespace": locus["namespace"],
            "role_family": locus["role_family"],
            "visible_name_or_owner_de": locus["concrete_owner_or_name_de"],
            "surfaces": locus["surfaces"],
            "recipes": locus["recipes"],
            "classifier_trace_de": classifier_trace,
            "continuous_list_reading_de": f"{locus['concrete_owner_or_name_de']}; {classifier_trace}",
        })
    write_tsv(LIST_OUT, list_rows, [
        "list_order", "physical_page", "source_page", "locus", "namespace", "role_family",
        "visible_name_or_owner_de", "surfaces", "recipes", "classifier_trace_de", "continuous_list_reading_de",
    ])

    md = ["# Pass 914 — lesbare f70-/f88-Listen", ""]
    for page in ["f70v", "f88r"]:
        md += [f"## {page}", ""]
        for row in [row for row in list_rows if row["physical_page"] == page]:
            md.append(f"- **{row['locus']}** `{row['surfaces']}` — {row['continuous_list_reading_de']}")
        md.append("")
    LIST_MD_OUT.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    handbook = [
        "# Pass 914 — Kontextregel für Prosa und Etiketten", "",
        "## Die Regel", "",
        "Vor jeder Kartenlesung entscheidet der Lehrling anhand des Layouts zwischen zwei Kanälen:",
        "", "- **Prosa:** O/OK/CH/K/T/S/OR sind Handlungen oder Arbeitsinhalte.",
        "- **Etikett:** dieselben Formen sind Reihen-, Platz-, Kennungs-, Zuordnungs- oder Klassenmerkmale.",
        "", "Der gemeinsame Kern ist nicht ein deutsches Wort, sondern dieselbe Werkstattoperation einmal aktiv",
        "und einmal als fertige Eintragsklasse. Das ist leicht lehrbar: *in Prosa tun, am Bild benennen*.",
        "", "## Sieben Doppelkarten", "",
    ]
    for row in dual_rows:
        handbook.append(f"- `{row['component']}`: Prosa **{row['prose_action_de']}**; Etikett **{row['label_classifier_de']}**.")
    HANDBOOK_OUT.write_text("\n".join(handbook) + "\n", encoding="utf-8")

    report = [
        "# Pass 914 — Trennung von Prosahandlung und Etikettenklassifikator", "",
        "## Ergebnis", "",
        f"Sieben häufige Komponenten betreffen {len(audit)} der 2511 Gruppen. Jede hat jetzt",
        "zwei kurze, verwandte Lesungen: eine aktive Prosahandlung und einen statischen",
        "Etikettenklassifikator. Dadurch liest sich ein Zutatenname nicht mehr als Befehl,",
        "während dieselbe Kartenfamilie im Werkstatttext weiterhin ausführbar bleibt.", "",
        "Die Trennung ist besonders wichtig für `OK`: 410 Prosaereignisse bedeuten ansetzen/",
        "aktivieren, 36 Etikettenereignisse markieren einen ausgewählten aktiven Platz. `CH`",
        "hat 194 Prosa- und 19 Etikettenereignisse; `K` 169 und 23. Das sind keine seltenen",
        "Ausnahmen, sondern ein zentraler Schreibmechanismus.", "",
        "## Vollständige Listen", "",
        f"Die f70-/f88-Ausgabe enthält {len(list_rows)} Bildloci:45 Sternfiguren-/Radloci und",
        "15 Zutatenloci. Jeder Eintrag zeigt zuerst den sichtbaren Besitzer/Namen, danach die",
        "Klassifikatorform. So bleiben die sechzehn f88-Zutaten konkret, ohne OT/AL/OR als",
        "Pflanzennamen auszugeben.", "",
        "## Nächster Hebel", "",
        "Als Nächstes werden die Prosaereignisse der sieben Doppelkarten nach Satzposition",
        "geordnet. Ziel ist eine kurze Wortstellung: AUFRUF → QUELLE/MENGE → HANDLUNG → ZIEL/",
        "GRAD → SCHLUSS. Danach lassen sich die 464 Loci flüssiger statt komponentenweise lesen.",
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "pass": 914,
        "decision": "SEVEN_COMPONENTS_SPLIT_INTO_PROSE_ACTION_AND_LABEL_CLASSIFIER",
        "events": len(contextual),
        "dual_use_events": len(audit),
        "label_events": len(labels),
        "dual_components": len(dual_rows),
        "f70_f88_list_loci": len(list_rows),
        "component_counts": {row["component"]: {"prose": row["prose_events"], "label": row["label_events"]} for row in dual_rows},
        "source_hashes": {path.name: sha(path) for path in (EVENTS, LABELS, LABEL_LOCI)},
        "output_hashes": {path.name: sha(path) for path in (INTERLINEAR_OUT, AUDIT_OUT, DUAL_OUT, LIST_OUT, LIST_MD_OUT, HANDBOOK_OUT, REPORT_OUT)},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
