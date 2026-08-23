#!/usr/bin/env python3
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R163 = ROOT / "experiments/yolo/sidequest_semantic_master_day_workflow_hundred_sixty_third"
R164 = ROOT / "experiments/yolo/sidequest_semantic_process_pressure_current_hundred_sixty_fourth"
R167 = ROOT / "experiments/yolo/sidequest_semantic_b4_charge_through_apparatus_hundred_sixty_seventh"


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
    events = read_tsv(R164 / "HUNDRED_SIXTY_FOURTH_381_ATOMIC_EVENTS.tsv")
    article_records = {
        "A_F10R_TWO_RECORD_ARTICLE": ["H1", "H2"],
        "B_F11R_CLEAR_EXTRACT_ARTICLE": ["H3"],
        "C_F55V_PORTIONED_PREPARATION_ARTICLE": ["H4"],
        "D_F56R_ADDITIVE_APPLICATION_ARTICLE": ["H5"],
    }
    b4_cards = {row["master_card_id"] for row in events if row["record_unit_id"] == "B4"}
    meaning = {row["master_card_id"]: row["card_value_de"] for row in events}
    candidate_notes = {
        "A_F10R_TWO_RECORD_ARTICLE": ("NO", "einsetzen, Sollmaß, Ansatz, dies, weiter", "kein exakter Klarauszug und keine vorbereitete Einlage", "8/16"),
        "B_F11R_CLEAR_EXTRACT_ARTICLE": ("SELECTED", "Sollmaß, Klarauszug, dies", "weniger allgemeine Operationskarten, aber exakte Produktkarte", "15/16"),
        "C_F55V_PORTIONED_PREPARATION_ARTICLE": ("STRONG_RIVAL", "fertig, länger bearbeiten, Sollmaß, überführen, Ansatz, dies", "Quellauszug statt exaktem Klarauszug", "12/16"),
        "D_F56R_ADDITIVE_APPLICATION_ARTICLE": ("NO", "einsetzen, Sollmaß, dorthin, das nächste", "starke Zielanwendung, aber schwache Produktklärung", "9/16"),
    }
    candidate_rows = []
    for article, records in article_records.items():
        article_events = [row for row in events if row["record_unit_id"] in records]
        article_cards = {row["master_card_id"] for row in article_events}
        shared = sorted(article_cards & b4_cards)
        selection, useful, weakness, score = candidate_notes[article]
        candidate_rows.append({
            "article_id": article, "records": "|".join(records),
            "pages": "|".join(dict.fromkeys(row["page"] for row in article_events)),
            "event_count": str(len(article_events)), "distinct_cards": str(len(article_cards)),
            "exact_B4_bridge_count": str(len(shared)),
            "exact_B4_bridge_cards": "|".join(f"{card}:{meaning[card]}" for card in shared),
            "process_strength_de": useful, "main_weakness_de": weakness,
            "workshop_score": score, "selection": selection,
        })
    write_tsv("HUNDRED_SIXTY_EIGHTH_4_HERBAL_SOURCE_CANDIDATES.tsv", candidate_rows)

    bridge_ids = ["MC039", "MC119", "MC123"]
    bridge_rows = []
    for card_id in bridge_ids:
        h3 = [row for row in events if row["record_unit_id"] == "H3" and row["master_card_id"] == card_id]
        b4 = [row for row in events if row["record_unit_id"] == "B4" and row["master_card_id"] == card_id]
        bridge_rows.append({
            "master_card_id": card_id, "atomic_value_de": meaning[card_id],
            "H3_event_serials": "|".join(row["event_serial"] for row in h3),
            "H3_surfaces": "|".join(row["visible_surface"] for row in h3),
            "B4_event_serials": "|".join(row["event_serial"] for row in b4),
            "B4_surfaces": "|".join(row["visible_surface"] for row in b4),
            "bridge_reading_de": {
                "MC039": "derselbe Sollmaß-Kanal trotz daiin/saiin-Handwechsel",
                "MC119": "exakt dieselbe sichtbare shey-Karte für Klarauszug",
                "MC123": "derselbe laufende Posten in verschiedenen Handformen",
            }[card_id],
        })
    write_tsv("HUNDRED_SIXTY_EIGHTH_3_EXACT_H3_B4_BRIDGES.tsv", bridge_rows)

    h3 = read_tsv(R163 / "HUNDRED_SIXTY_THIRD_79_EVENT_MASTER_DAY_INTERLINEAR.tsv")
    h3 = [row for row in h3 if row["record_unit_id"] == "H3"]
    b4 = read_tsv(R167 / "HUNDRED_SIXTY_SEVENTH_36_EVENT_B4_PROCEDURE.tsv")
    selected_rows = []
    for row in h3:
        selected_rows.append({
            "combined_order": str(len(selected_rows) + 1), "source_record": "H3", "page": row["page"],
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "atomic_value_de": row["atomic_card_value_de"], "combined_phase": "PREPARE_CLEAR_EXTRACT",
            "complete_clause_translation_de": row["complete_clause_translation_de"],
            "cross_page_status": "SOURCE_ARTICLE",
        })
    for row in b4:
        selected_rows.append({
            "combined_order": str(len(selected_rows) + 1), "source_record": "B4", "page": row["page"],
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "atomic_value_de": row["atomic_card_value_de"], "combined_phase": "PROCESS_AND_DELIVER_CHARGE",
            "complete_clause_translation_de": row["complete_clause_translation_de"],
            "cross_page_status": "WORKSHOP_SCENARIO_NOT_VISIBLE_POINTER",
        })
    write_tsv("HUNDRED_SIXTY_EIGHTH_53_EVENT_H3_TO_B4_SCENARIO.tsv", selected_rows)

    readable = [
        "# Ausgewählte Quellenkette: f11r/H3 liefert die B4-Charge", "",
        "## Quellenartikel f11r", "",
        "Bereite aus dem Kochgut der blau bekrönten Bildpflanze einen Sud. Wringe ihn aus, lasse ihn",
        "die vorgeschriebene Zeit stehen, seihe nach und behalte den klaren Auszug. Gib den Endzusatz",
        "bei, bereite den weiteren Anteil und bringe ihn auf Sollmaß.", "",
        "## Übergabe an f83r/B4", "",
        "Die exakte Karte `shey = Klarauszug` erscheint in beiden Records. Der Meister kann deshalb",
        "dieselbe gelernte Produktkarte vom Quellenartikel in die Stationsanweisung übernehmen. Der",
        "Übergang selbst bleibt im Bild/Text ungeschrieben.", "",
        "## Stationsverfahren", "",
        "Richte die Station ein, setze die Einlage ein und führe die Charge zweimal hindurch. Bemiss",
        "und vollende das Produkt, ziehe am linken Unterlauf eine Fraktion ab und führe den Rest weiter.",
        "Gib am rechten Lauf klaren Auszug hinzu und bringe die letzte Portion an ihre Zielstelle.", "",
        "## Starker Rivale", "",
        "f55v/H4 bleibt der stärkste Rivale: Es teilt sechs exakte B4-Karten und liefert bereits",
        "portionierte, überführte und fertige Zubereitung. Es besitzt aber nur `Quellauszug`, nicht die",
        "exakte gemeinsame `shey`-Produktkarte.",
    ]
    (OUT / "HUNDRED_SIXTY_EIGHTH_SELECTED_H3_TO_B4_READING.md").write_text("\n".join(readable) + "\n", encoding="utf-8")

    report = [
        "# Hundertachtundsechzigste Runde: f11r/H3 ist die beste Quellenpflanze für B4", "",
        "The four pictured Herbal articles were compared as source articles. f55v/H4 shares six exact B4 cards",
        "and is the strongest procedural rival. f11r/H3 shares only three, but one is decisive: the exact visible",
        "surface `shey` and master card MC119 mean `Klarauszug` in both H3 and B4. It also shares Sollmaß and current",
        "item, while its unique local chain explicitly prepares, presses, rests and re-filters the clear product.", "",
        "The selected creative handoff is therefore H3 clear extract into the B4 treatment-charge apparatus.",
        "The combined edition contains all 17 H3 events and all 36 B4 procedure events. The handoff remains a",
        "workshop scenario, not a claimed manuscript cross-reference.", "",
        "Next give the selected f11r plant a bounded concrete material identity class—such as aromatic flowering",
        "wash herb, mucilaginous soothing herb, or astringent clarifying herb—and see which class best explains",
        "pressing, standing, re-filtering and later target application.",
    ]
    (OUT / "HUNDRED_SIXTY_EIGHTH_HERBAL_SOURCE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "candidate_articles": len(candidate_rows), "selected_article": "B_F11R_CLEAR_EXTRACT_ARTICLE",
        "strong_rival": "C_F55V_PORTIONED_PREPARATION_ARTICLE", "exact_H3_B4_bridges": len(bridge_rows),
        "selected_scenario_events": len(selected_rows), "H3_events": len(h3), "B4_events": len(b4),
        "card_value_changes": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
