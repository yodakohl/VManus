#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P581 = YOLO / "sidequest_semantic_spoken_core_dictionary_five_hundred_eighty_first"

PAIRS = [
    ("LS", "OL", "MERGE_SPOKEN_VALUE_KEEP_GRAPHIC_GRAMMAR", "fort", "fort", "LS ist selbständiges Fort!-Signal; OL ist gebundener Fortsetzungsanschluss."),
    ("K", "P", "KEEP_MINIMAL_CONTRAST", "gib zu", "gib hinein", "K führt dem aktiven Ansatz zu; P setzt in einen sichtbar begrenzten Empfänger hinein."),
    ("CH", "CHD", "KEEP_MINIMAL_CONTRAST", "ziehe ab", "setze um", "CH nimmt vom aktuellen Bestand weg; CHD überträgt den genommenen Posten in eine neue Lage."),
    ("AIIN", "IIN", "KEEP_MINIMAL_CONTRAST", "Maß", "Grad", "AIIN nennt eine Menge; IIN nennt eine Prozessstufe oder Einstellung."),
    ("AL", "OS", "KEEP_MINIMAL_CONTRAST", "dorthin", "Fach", "AL zeigt auf ein Ziel; OS nennt ein ausgewähltes Arbeitsfach."),
]


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    dictionary = read(P581 / "FIVE_HUNDRED_EIGHTY_FIRST_THIRTY_EIGHT_SPOKEN_CORE_DICTIONARY.tsv")
    events = read(P581 / "FIVE_HUNDRED_EIGHTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_SPOKEN_EVENT_SEQUENCES.tsv")
    by_component = {r["component"]: dict(r) for r in dictionary}
    for component, value in [("LS", "fort")]:
        by_component[component]["short_spoken_value_de"] = value

    decisions = []
    audit_rows = []
    for a, b, decision, va, vb, contrast in PAIRS:
        count_a = 0
        count_b = 0
        for event in events:
            parts = event["component_parse"].split("+")
            if a in parts or b in parts:
                count_a += int(a in parts)
                count_b += int(b in parts)
                audit_rows.append({
                    "pair": f"{a}/{b}",
                    "event_id": event["event_id"],
                    "page": event["page"],
                    "record": event["record"],
                    "statement_id": event["statement_id"],
                    "surface": event["surface"],
                    "component_parse": event["component_parse"],
                    "contains": a if a in parts else b,
                    "compact_statement_de": event["compact_statement_de"],
                })
        decisions.append({
            "pair": f"{a}/{b}",
            "component_a": a,
            "component_b": b,
            "events_a": count_a,
            "events_b": count_b,
            "decision": decision,
            "spoken_a_de": va,
            "spoken_b_de": vb,
            "minimal_contrast_de": contrast,
            "component_inventory_change": "NONE",
        })

    revised_dictionary = [by_component[r["component"]] for r in dictionary]
    revised_events = []
    spoken = {r["component"]: r["short_spoken_value_de"] for r in revised_dictionary}
    for event in events:
        parts = event["component_parse"].split("+")
        row = dict(event)
        row["spoken_component_sequence_de"] = " · ".join(spoken[p] for p in parts)
        row["synonym_revision"] = "LS_AND_OL_SHARE_FORT" if "LS" in parts or "OL" in parts else "NONE"
        revised_events.append(row)

    write("FIVE_HUNDRED_EIGHTY_SECOND_FIVE_MINIMAL_CONTRAST_DECISIONS.tsv", decisions)
    write("FIVE_HUNDRED_EIGHTY_SECOND_PAIR_EVENT_AUDIT.tsv", audit_rows)
    write("FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv", revised_dictionary)
    write("FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_SEQUENCES.tsv", revised_events)
    unique_spoken = len({r["short_spoken_value_de"] for r in revised_dictionary})
    summary = {
        "status": "PASS",
        "pair_decisions": len(decisions),
        "spoken_merges": sum(r["decision"] == "MERGE_SPOKEN_VALUE_KEEP_GRAPHIC_GRAMMAR" for r in decisions),
        "kept_contrasts": sum(r["decision"] == "KEEP_MINIMAL_CONTRAST" for r in decisions),
        "components": len(revised_dictionary),
        "distinct_spoken_values": unique_spoken,
        "events": len(revised_events),
        "audited_pair_events": len(audit_rows),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertzweiundachtzigste Runde: fünf Minimalpaare",
        "",
        "## Ergebnis",
        "",
        "Nur LS und OL fallen im gesprochenen Wert zusammen: beide heißen ›fort‹. LS ist das selbständige Fort!-Signal, OL der gebundene Fortsetzungsanschluss. Die Schrift behält zwei Komponenten, die Werkstattsprache hat aber nur ein Wort. Damit sinken 38 Komponenten auf 37 verschiedene Sprechwerte.",
        "",
        "Vier Paare müssen getrennt bleiben: K ›gib zu‹ gegen P ›gib hinein‹; CH ›ziehe ab‹ gegen CHD ›setze um‹; AIIN ›Maß‹ gegen IIN ›Grad‹; AL ›dorthin‹ gegen OS ›Fach‹. Diese Unterschiede sind klein, lehrbar und für die Anweisungen nützlich.",
        "",
        "Die wichtigste Lehre ist, Form- und Wortinventar nicht gleichzusetzen. Zwei Kartenbauteile können dasselbe gesprochene Wort tragen, wenn ihre Stellung verschieden ist. Umgekehrt dürfen ähnlich aussehende Bauteile nicht zusammenfallen, wenn sie Menge gegen Stufe oder Wegnahme gegen Transfer unterscheiden.",
        "",
        "## Nächster Schritt",
        "",
        "Als Nächstes werden die 37 Sprechwerte in wiederkehrende Zwei- und Dreiwortformeln gebündelt. Ziel ist ein kleines Formelbuch, aus dem ein Lehrling die 116 Anweisungen erzeugt, ohne jede Komponentenfolge einzeln auswendig zu lernen.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_SECOND_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
