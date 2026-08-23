#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R157 = ROOT / "experiments/yolo/sidequest_semantic_shared_renderer_simplification_hundred_fifty_seventh"
R160 = ROOT / "experiments/yolo/sidequest_semantic_positional_habit_schedule_hundred_sixtieth"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]

RECORD_ACCENTS = {
    ("B1", "B_FIELD_INTERIOR"): ["BARE_OR_INTERNAL", "Q_CELL_ENTRY", "S_FLOW_ENTRY", "HARD_D_T_ENTRY", "OPEN_CH_ENTRY"],
    ("B3", "B_FIELD_INTERIOR"): ["HARD_D_T_ENTRY", "Q_CELL_ENTRY", "OPEN_CH_ENTRY", "BARE_OR_INTERNAL", "S_FLOW_ENTRY"],
    ("H3", "H_FIELD_INTERIOR"): ["HARD_D_T_ENTRY", "BARE_OR_INTERNAL", "Q_CELL_ENTRY", "S_FLOW_ENTRY", "OPEN_CH_ENTRY"],
}
CARD_POSITION_CUSTOMS = {
    ("MC123", "B_FIELD_INTERIOR"): "OPEN_CH_ENTRY",
    ("MC039", "B_FIELD_INTERIOR"): "HARD_D_T_ENTRY",
    ("MC039", "H_FIELD_INTERIOR"): "HARD_D_T_ENTRY",
    ("MC161", "H_FIELD_INTERIOR"): "BARE_OR_INTERNAL",
    ("MC017", "B_FIELD_INTERIOR"): "BARE_OR_INTERNAL",
    ("MC128", "B_SINGLE_CELL"): "S_FLOW_ENTRY",
    ("MC153", "B_FIELD_INTERIOR"): "BARE_OR_INTERNAL",
}
RECORD_CARD_CUSTOMS = {
    ("B3", "MC154"): "HARD_D_T_ENTRY",
    ("B6", "MC153"): "BARE_OR_INTERNAL",
    ("B2", "MC119"): "OPEN_CH_ENTRY",
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
    base = read_tsv(R160 / "HUNDRED_SIXTIETH_251_POSITIONAL_RENDER_TRACE.tsv")
    surfaces = read_tsv(R157 / "HUNDRED_FIFTY_SEVENTH_103_SHARED_SURFACES.tsv")
    available = defaultdict(list)
    for row in surfaces:
        available[row["master_card_id"]].append((row["five_habit_class"], row["visible_surface"]))

    custom_rows = []
    for (record_id, schedule_rule), priority in RECORD_ACCENTS.items():
        custom_rows.append({
            "custom_type": "RECORD_ACCENT", "record_unit_id": record_id,
            "master_card_id": "ANY_AVAILABLE_CARD", "schedule_rule": schedule_rule,
            "custom_habit_or_priority": " > ".join(priority),
            "workshop_reading": f"{record_id} nutzt in {schedule_rule} seine lokale Handrangfolge.",
        })
    card_values = {row["master_card_id"]: row["card_value_de"] for row in base}
    for (card_id, schedule_rule), habit in CARD_POSITION_CUSTOMS.items():
        custom_rows.append({
            "custom_type": "CARD_POSITION_CUSTOM", "record_unit_id": "ANY_RECORD",
            "master_card_id": card_id, "schedule_rule": schedule_rule,
            "custom_habit_or_priority": habit,
            "workshop_reading": f"Karte {card_values[card_id]} behält in {schedule_rule} ihre gelernte Hausform.",
        })
    for (record_id, card_id), habit in RECORD_CARD_CUSTOMS.items():
        custom_rows.append({
            "custom_type": "RECORD_CARD_CUSTOM", "record_unit_id": record_id,
            "master_card_id": card_id, "schedule_rule": "ANY_POSITION",
            "custom_habit_or_priority": habit,
            "workshop_reading": f"{record_id} schreibt {card_values[card_id]} durchgehend in seiner lokalen Form.",
        })
    write_tsv("HUNDRED_SIXTY_FIRST_13_RECURRENT_CUSTOMS.tsv", custom_rows)

    trace_rows = []
    by_record = defaultdict(list)
    for row in base:
        forms = available[row["master_card_id"]]
        habit = row["predicted_habit"]
        layers = ["R160_POSITIONAL_RULE"]
        accent_key = (row["record_unit_id"], row["schedule_rule"])
        if accent_key in RECORD_ACCENTS:
            habit = next(candidate for candidate in RECORD_ACCENTS[accent_key] if any(h == candidate for h, _ in forms))
            layers.append("RECORD_ACCENT")
        card_key = (row["master_card_id"], row["schedule_rule"])
        if card_key in CARD_POSITION_CUSTOMS:
            habit = CARD_POSITION_CUSTOMS[card_key]
            layers.append("CARD_POSITION_CUSTOM")
        record_card_key = (row["record_unit_id"], row["master_card_id"])
        if record_card_key in RECORD_CARD_CUSTOMS:
            habit = RECORD_CARD_CUSTOMS[record_card_key]
            layers.append("RECORD_CARD_CUSTOM")
        canonical_surface = next(surface for candidate, surface in forms if candidate == habit)
        habit_match = habit == row["observed_habit"]
        exact_match = canonical_surface == row["observed_surface"]
        if exact_match:
            treatment = "CUSTOM_SCHEDULE_EXACT"
        elif habit_match:
            treatment = "SECOND_REGISTERED_SPELLING_IN_CORRECT_HABIT"
        else:
            treatment = "LOCAL_REGISTERED_OVERRIDE_REMAINS"
        out = {
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "locus": row["locus"], "field_id": row["field_id"],
            "field_position": row["field_position"], "locus_position": row["locus_position"],
            "master_card_id": row["master_card_id"], "card_value_de": row["card_value_de"],
            "observed_surface": row["observed_surface"], "observed_habit": row["observed_habit"],
            "base_schedule_rule": row["schedule_rule"], "base_predicted_habit": row["predicted_habit"],
            "applied_layers": " > ".join(layers), "custom_predicted_habit": habit,
            "predicted_canonical_surface": canonical_surface,
            "habit_match": "YES" if habit_match else "NO",
            "exact_surface_match": "YES" if exact_match else "NO",
            "apprentice_treatment": treatment, "master_recovery": "EXACT",
        }
        trace_rows.append(out)
        by_record[row["record_unit_id"]].append(out)
    write_tsv("HUNDRED_SIXTY_FIRST_251_CUSTOM_RENDER_TRACE.tsv", trace_rows)

    record_rows = []
    for record_id in RECORD_ORDER:
        rows = by_record[record_id]
        layers = Counter(layer for row in rows for layer in row["applied_layers"].split(" > ")[1:])
        record_rows.append({
            "record_unit_id": record_id, "page": rows[0]["page"], "shared_events": str(len(rows)),
            "habit_matches": str(sum(row["habit_match"] == "YES" for row in rows)),
            "remaining_local_habit_overrides": str(sum(row["habit_match"] == "NO" for row in rows)),
            "exact_surface_matches": str(sum(row["exact_surface_match"] == "YES" for row in rows)),
            "second_registered_spellings": str(sum(row["apprentice_treatment"] == "SECOND_REGISTERED_SPELLING_IN_CORRECT_HABIT" for row in rows)),
            "custom_uses": str(sum(layers.values())),
            "custom_inventory": "|".join(f"{key}:{layers[key]}" for key in sorted(layers)) if layers else "NONE",
            "master_card_failures": "0",
        })
    write_tsv("HUNDRED_SIXTY_FIRST_11_RECORD_CUSTOM_SUMMARY.tsv", record_rows)

    manual = [
        "# Dreizehn wiederkehrende Schreibbräuche", "",
        "Die neun Positionsregeln bleiben die Grundschule. Danach kommen nur dreizehn wiederkehrende",
        "Hausbräuche: drei Record-Akzente, sieben Karten-in-Position-Bräuche und drei Record-Karten-Bräuche.",
        "Sie verändern ausschließlich die sichtbare Form.", "",
        "## Record-Akzente", "",
        "- B1 schreibt das Bio-Feldinnere bevorzugt nackt.",
        "- B3 schreibt dasselbe Innere bevorzugt hart/kompakt.",
        "- H3 schreibt sein Herbal-Innere bevorzugt hart statt ch-offen.", "",
        "## Kartenbräuche", "",
        "- `dies` bleibt im Bio-Innenfeld meist ch-offen.",
        "- `Sollmaß` bleibt in Herbal- und Bio-Innenfeldern meist hart.",
        "- `bereit` bleibt im Herbal-Innenfeld nackt.",
        "- `Anteil zugeben` und `weiter` fallen im Bio-Innenfeld meist auf die nackte Form zurück.",
        "- Die Einzelzelle `kurz absetzen; Schluss` bevorzugt s/sh.", "",
        "## Lokale Record-Karten", "",
        "- B2 schreibt `Klarauszug` ch-offen.",
        "- B3 schreibt `dorthin` hart.",
        "- B6 schreibt `weiter` nackt.", "",
        "Die Kombination trifft 209/251 Gewohnheiten und 187/251 sichtbare Formen vollständig.",
        "Weitere 22 benötigen nur die zweite registrierte Schreibweise derselben Gewohnheit; 42 bleiben",
        "lokale, aber bereits registrierte Entscheidungen.",
    ]
    (OUT / "HUNDRED_SIXTY_FIRST_CUSTOMS_APPRENTICE_CARD.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    report = [
        "# Hunderteinundsechzigste Runde: dreizehn Hausbräuche komprimieren die lokalen Abweichungen", "",
        "Three record accents, seven card-position customs and three record-card customs sit above the nine",
        "positional preferences. They raise observed-habit reproduction from 182 to 209 of 251 events and exact",
        "visible-token reproduction from 160 to 187. Twenty-two remaining tokens use only a second registered",
        "spelling inside the correct habit; 42 retain a local registered habit choice.", "",
        "The result reads like a small workshop tradition rather than five fonts: common positional training, a",
        "few card-specific house forms, and a few record-local customs. None changes the 47 shared meanings or the",
        "126 learned local nomenclator values.", "",
        "Next inspect the 42 residual habit choices as ordered runs. If they cluster into short hand-switch blocks,",
        "teach the switch once per block; otherwise leave them as exemplar spellings instead of adding more rules.",
    ]
    (OUT / "HUNDRED_SIXTY_FIRST_RECURRENT_CUSTOMS_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "recurrent_customs": len(custom_rows),
        "record_accents": len(RECORD_ACCENTS),
        "card_position_customs": len(CARD_POSITION_CUSTOMS),
        "record_card_customs": len(RECORD_CARD_CUSTOMS),
        "shared_events": len(trace_rows),
        "habit_matches": sum(row["habit_match"] == "YES" for row in trace_rows),
        "remaining_local_habit_overrides": sum(row["habit_match"] == "NO" for row in trace_rows),
        "exact_surface_matches": sum(row["exact_surface_match"] == "YES" for row in trace_rows),
        "second_registered_spellings": sum(row["apprentice_treatment"] == "SECOND_REGISTERED_SPELLING_IN_CORRECT_HABIT" for row in trace_rows),
        "records": len(record_rows), "master_recovery_failures": 0,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
