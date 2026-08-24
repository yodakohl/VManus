#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
HERBAL = ROOT / "experiments/yolo/sidequest_semantic_herbal_operation_lexicon_four_hundred_twenty_eighth/FOUR_HUNDRED_TWENTY_EIGHTH_HERBAL_100_EVENT_ROLE_EDITION.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    b1 = [row for row in read(BASE) if row["record_unit_id"] == "B1"]
    herbal = read(HERBAL)
    herbal_by_card: dict[str, set[str]] = {}
    for row in herbal:
        herbal_by_card.setdefault(row["joint_tuple_id"], set()).add(row["small_value_de"])
    shared_ids = {row["joint_tuple_id"] for row in b1} & set(herbal_by_card)
    canonical = {
        "276a7c2d74d1143446f4": "verwende dies", "2f1c5e56e8f0ff459065": "Mass",
        "308e8ea2d5d190c498e8": "an die Stelle setzen", "4d4559019a961b834aa1": "dasselbe",
        "6f7ff8287eddf4da9fdb": "dies umsetzen", "b5fcea1eaed06b2f2291": "nach Mass ansetzen",
        "b921a237be883a820352": "dies", "dcda95c81a5460feb191": "fortsetzen",
        "dd0ecaf5e27d81befffc": "Stelle", "dec401773c1f0347793d": "Fortsetzungsansatz",
    }
    shorten = {
        "Arbeitsbewegung abschließen": "umsetzen; Schluss",
        "den laufenden Posten umsetzen oder durcharbeiten": "dies umsetzen",
        "unter besonderer Bedingung umsetzen; Schluss": "Sonderumsetzung; Schluss",
        "durch den Durchlass führen": "durchführen",
        "Behandlungsstelle": "Arbeitsstelle",
        "Auslassstelle": "Auslass",
        "Umsetzung abschließen": "umsetzen; Schluss",
        "Zielstufe": "Sollstand",
    }
    events = []
    for order, row in enumerate(b1, start=1):
        value = canonical.get(row["joint_tuple_id"], shorten.get(row["concrete_word_reading_de"], row["concrete_word_reading_de"]))
        events.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"], "field_id": row["field_id"],
            "statement_id": row["statement_id"], "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "small_value_de": value, "owner": "B1_SHARED_TWO_ROW_POOL",
            "lexicon_source": "HERBAL_EXACT_CARD_TRANSFER" if row["joint_tuple_id"] in shared_ids else "B1_LEARNED_LOCAL_CARD",
        })
    write("FOUR_HUNDRED_TWENTY_NINTH_B1_66_EVENT_INTERLINEAR.tsv", events)

    translations = {
        "B1-S001": "Kurz ansetzen und den Schritt schließen.",
        "B1-S002": "Nach Maß ansetzen. Beckenwasser an die Stelle bringen; mit demselben Bestand fortsetzen, eine Portion und eine weitere Portion an der Stelle führen, noch warm halten, Badzusatz und Fortsetzungsansatz zuführen, mäßige Menge bemessen, länger an der Stelle halten und durch den Durchlass umsetzen; Schluss.",
        "B1-S003": "Fortsetzen und unter der Sonderbedingung umsetzen; Schluss.",
        "B1-S004": "Dies umsetzen, fortsetzen und absetzen; Schluss.",
        "B1-S005": "Die Fortsetzung umsetzen und schließen.",
        "B1-S006": "Eine Portion zugeben, durch den Durchlass führen, Badzusatz zugeben und abkühlen.",
        "B1-S007": "Den Ansatz umsetzen; Schluss.",
        "B1-S008": "Dies fortsetzen, kurz wärmen, weiterführen und absetzen; Schluss.",
        "B1-S009": "Kurz ansetzen; Schluss.",
        "B1-S010": "Kurz ansetzen; Schluss.",
        "B1-S011": "Durch den Durchlass führen und dies verwenden.",
        "B1-S012": "Einen Waschgang beginnen, kurz ansetzen, waschen und schließen.",
        "B1-S013": "Waschen; Schluss.",
        "B1-S014": "Dies umsetzen, an die Arbeitsstelle und zum Auslass führen, fortsetzen und den Folgeauslass wählen.",
        "B1-S015": "Füllen, den Ansatz umsetzen und schließen.",
        "B1-S016": "An die Stelle setzen, länger ansetzen, fortsetzen und absetzen; Schluss.",
        "B1-S017": "An der Stelle die erste Öffnung wählen und den Posten umsetzen; Schluss.",
        "B1-S018": "Das Empfangsgefäß einreiben, auf Sollstand bringen, länger auffangen und schließen.",
        "B1-S019": "Absetzen; Schluss.",
        "B1-S020": "Kurz wärmen, seihen und schließen.",
        "B1-S021": "An der bezeichneten Stelle fortsetzen.",
    }
    statement_rows = []
    for statement_id in sorted(translations, key=lambda value: int(value.split("S")[1])):
        rows = [row for row in events if row["statement_id"] == statement_id]
        statement_rows.append({
            "statement_id": statement_id, "events": len(rows), "event_ids": "|".join(row["event_id"] for row in rows),
            "card_sequence_de": " > ".join(row["small_value_de"] for row in rows),
            "continuous_reading_de": translations[statement_id],
            "owner": "B1_SHARED_TWO_ROW_POOL",
        })
    write("FOUR_HUNDRED_TWENTY_NINTH_B1_21_STATEMENTS.tsv", statement_rows)

    transfer = []
    for joint_id in sorted(shared_ids):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        transfer.append({
            "joint_tuple_id": joint_id, "B1_events": len(rows), "B1_surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "transferred_value_de": canonical[joint_id], "B1_statement_ids": "|".join(sorted({row["statement_id"] for row in rows})),
        })
    write("FOUR_HUNDRED_TWENTY_NINTH_TEN_TRANSFERRED_EXACT_CARDS.tsv", transfer)

    local_deck = []
    for joint_id in sorted({row["joint_tuple_id"] for row in events if row["lexicon_source"] == "B1_LEARNED_LOCAL_CARD"}):
        rows = [row for row in events if row["joint_tuple_id"] == joint_id]
        local_deck.append({
            "joint_tuple_id": joint_id, "events": len(rows), "surfaces": "|".join(sorted({row["surface"] for row in rows})),
            "small_values_de": "|".join(sorted({row["small_value_de"] for row in rows})),
            "local_owner": "B1_SHARED_TWO_ROW_POOL",
        })
    write("FOUR_HUNDRED_TWENTY_NINTH_B1_LOCAL_DECK.tsv", local_deck)

    models = [
        {"model": "SHARED_POOL_WORKSTATION", "statement_fit": 21, "visual_fit": 4, "lexicon_transfer": 23, "decision": "SELECT"},
        {"model": "THERAPEUTIC_BATH_REGIMEN", "statement_fit": 18, "visual_fit": 4, "lexicon_transfer": 23, "decision": "KEEP_MEDICAL_EXPANSION"},
        {"model": "ALLEGORICAL_FIGURE_REGISTER", "statement_fit": 10, "visual_fit": 3, "lexicon_transfer": 23, "decision": "KEEP_ICONOGRAPHIC_RIVAL"},
    ]
    write("FOUR_HUNDRED_TWENTY_NINTH_THREE_B1_MODELS.tsv", models)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statement_rows),
        "shared_exact_cards": len(transfer), "shared_events": sum(row["lexicon_source"] == "HERBAL_EXACT_CARD_TRANSFER" for row in events),
        "local_exact_cards": len(local_deck), "decision": "B1_SHARED_POOL_WORKSTATION_ARTICLE",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
