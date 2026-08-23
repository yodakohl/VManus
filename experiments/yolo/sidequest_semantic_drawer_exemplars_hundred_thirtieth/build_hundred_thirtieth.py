#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R127 = ROOT / "experiments/yolo/sidequest_semantic_revised_continuous_prose_hundred_twenty_seventh"
R129 = ROOT / "experiments/yolo/sidequest_semantic_specialist_drawers_hundred_twenty_ninth"

SELECTION = {
    "D1_MATERIAL_PRODUCT_VESSEL": ("H3-S001", "Blüte und junges Blatt in den Arbeitsansatz geben, auswringen, bis zum Sollmaß stehen lassen, nachseihen, den Klarlauf nehmen und den Restschritt schließen."),
    "D2_FILTER_WASH_FLOW": ("B2-S004", "Den Posten dort einsetzen, durch den örtlichen Gang führen, abwärts übertragen, länger einwirken lassen, beim Abführen seihen und schließen."),
    "D3_HEAT_SETTLE_STATE": ("B2-S005", "Den Posten an der sichtbaren Stelle einsetzen, bis zum Sollmaß auffangen, durchführen, am Zeilenübergang einmal auf Sollmaß stellen, länger warm halten, abziehen und schließen."),
    "D4_TRANSFER_SOURCE_TARGET": ("B1-S014", "Diesen Posten übertragen, weiterführen, zur Zielstelle abführen und danach vom bezeichneten Ausgang weiternehmen."),
    "D5_QUANTITY_PART_STAGE": ("B3-S034", "Auf Arbeitsstufe bringen, den Posten bereitstellen, einen Teil abtrennen, das nächste Sollmaß setzen, zur Zielstelle führen, kurz absetzen und schließen."),
    "D6_ORDER_CONTINUATION": ("H2-S002", "Den nächsten Arbeitsansatz übernehmen, weiterführen, mit demselben Ansatz weiterarbeiten, das Sollmaß halten und davon nehmen."),
    "D7_APPLICATION_FASTEN_STORE": ("B4-S004", "Diesen Posten an der sichtbaren Anwendung einsetzen und festbinden."),
    "D8_LOCAL_OPERATION": ("H5-S003", "Den Rest zurückhalten, eine weitere Zutat nehmen, diesen Posten kurz bearbeiten und ihn als zweiten Arbeitsansatz einsetzen."),
}

FUNCTION = {
    "D1_MATERIAL_PRODUCT_VESSEL": ("material enters and a named product leaves", "ingredient|preparation|carrier|product"),
    "D2_FILTER_WASH_FLOW": ("a work item crosses a passage and is separated or washed", "entry|passage|separation|outflow"),
    "D3_HEAT_SETTLE_STATE": ("a work item reaches a held, warm, settled or collected state", "item|grade|state|release"),
    "D4_TRANSFER_SOURCE_TARGET": ("a work item moves from a source to a target", "source|transfer|target|continuation"),
    "D5_QUANTITY_PART_STAGE": ("a share or stage is selected before the next operation", "item|share|prescribed value|stage"),
    "D6_ORDER_CONTINUATION": ("the previous or next batch is carried through the sequence", "next|same batch|continue|source"),
    "D7_APPLICATION_FASTEN_STORE": ("a prepared item is fixed, applied or stored", "prepared item|site|fasten/store"),
    "D8_LOCAL_OPERATION": ("an exact rare operation is copied from the page exemplar", "local owner|memorized operation|result"),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(R129 / "HUNDRED_TWENTY_NINTH_COMPLETE_381_EVENT_DICTIONARY.tsv")
    statements = read_tsv(R127 / "HUNDRED_TWENTY_SEVENTH_116_REVISED_STATEMENTS.tsv")
    statement_by_id = {row["statement_id"]: row for row in statements}
    events_by_statement = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)

    exemplar_rows = []
    md = ["# Acht vollständige Fachanweisungen aus dem Meistercodebuch", ""]
    for drawer, (statement_id, reconstruction) in SELECTION.items():
        statement = statement_by_id[statement_id]
        members = events_by_statement[statement_id]
        matching = [row for row in members if row["drawer"] == drawer]
        exemplar_rows.append({
            "drawer": drawer,
            "statement_id": statement_id,
            "record_unit_id": statement["record_unit_id"],
            "page": statement["page"],
            "visible_surface_sequence": " ".join(row["visible_surface"] for row in members),
            "complete_card_chain_de": " | ".join(row["current_spoken_default_de"] for row in members),
            "drawer_card_count": str(len(matching)),
            "drawer_cards": " | ".join(f"{row['visible_surface']}={row['current_spoken_default_de']}" for row in matching),
            "previous_fluent_reading_de": statement["revised_continuous_reading_de"],
            "drawer_reconstructed_instruction_de": reconstruction,
        })
        md += [f"## {drawer} · {statement_id}", "", f"Sichtbar: `{exemplar_rows[-1]['visible_surface_sequence']}`", "",
               f"Karten: {exemplar_rows[-1]['complete_card_chain_de']}", "", reconstruction, ""]
    write_tsv("HUNDRED_THIRTIETH_EIGHT_DRAWER_EXEMPLARS.tsv", exemplar_rows)
    (OUT / "HUNDRED_THIRTIETH_EIGHT_COMPLETE_INSTRUCTIONS.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    function_rows = []
    for drawer, (purpose, slots) in FUNCTION.items():
        exemplar = next(row for row in exemplar_rows if row["drawer"] == drawer)
        function_rows.append({
            "drawer": drawer,
            "practical_function": purpose,
            "typical_source_slots": slots,
            "representative_statement": exemplar["statement_id"],
            "distinguishing_question": {
                "D1_MATERIAL_PRODUCT_VESSEL": "what substance, carrier or product is active?",
                "D2_FILTER_WASH_FLOW": "through which passage and with what separation?",
                "D3_HEAT_SETTLE_STATE": "to what held or settled condition?",
                "D4_TRANSFER_SOURCE_TARGET": "from where to where does the item move?",
                "D5_QUANTITY_PART_STAGE": "how much or at which stage?",
                "D6_ORDER_CONTINUATION": "which prior or following work item continues?",
                "D7_APPLICATION_FASTEN_STORE": "where is the preparation fixed or stored?",
                "D8_LOCAL_OPERATION": "which exact exemplar-only operation is required?",
            }[drawer],
        })
    write_tsv("HUNDRED_THIRTIETH_DRAWER_FUNCTION_COMPARISON.tsv", function_rows)

    report = [
        "# Hundertdreißigste Runde: die acht Schubladen tun verschiedene Arbeiten", "",
        "Je eine vollständige Aussage zeigt, dass die Schubladen nicht bloß statistische Haufen sind.",
        "Materialkarten bestimmen Stoff und Produkt; Filterkarten den Durchgang; Zustandskarten die erreichte",
        "Arbeitslage; Transferkarten Quelle und Ziel; Mengenkarten Anteil oder Stufe; Ordnungskarten den",
        "vorigen/nächsten Ansatz; Anwendungskarten Befestigung oder Lagerung; lokale Karten eine seltene",
        "exemplarabhängige Operation.", "",
        "Besonders gut lesbar sind H3-S001 als Auswring–Steh–Nachseih–Klarlauf-Kette, B3-S034 als",
        "Stufe–Teil–Folgemaß–Ziel–Absetz-Kette und B4-S004 als knappe Anweisung, einen Posten an der",
        "sichtbaren Anwendung einzusetzen und festzubinden.", "",
        "Die nächste Verbesserung betrifft die eigentliche Bucharchitektur: aus den acht Funktionen werden",
        "für alle elf Records kurze Arbeitsprofile gebaut. Dann lässt sich sehen, ob Herbal und Biological",
        "dieselben Schubladen in unterschiedlicher Reihenfolge benutzen oder wirklich getrennte Fachsysteme sind.",
    ]
    (OUT / "HUNDRED_THIRTIETH_DRAWER_EXEMPLAR_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {"status": "COMPLETE", "drawers": len(exemplar_rows), "exemplar_statements": len({row["statement_id"] for row in exemplar_rows}), "exemplar_events": sum(len(events_by_statement[row["statement_id"]]) for row in exemplar_rows)}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
