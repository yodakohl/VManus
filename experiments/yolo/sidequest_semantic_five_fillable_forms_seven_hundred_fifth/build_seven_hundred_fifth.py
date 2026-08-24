#!/usr/bin/env python3
"""Build Pass 705: five fillable forms and fifteen fresh practice statements."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P700 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_manual_seven_hundredth"
P704 = ROOT / "experiments/yolo/sidequest_semantic_statement_phrasebook_seven_hundred_fourth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


FORMS = [
    ("F01", "QUANTITY_STAGE>CURRENT_ITEM", "Menge/Stufe vor aktuellem Arbeitsposten", "[MENGE/STUFE]; [HANDLUNG AM AKTUELLEN POSTEN]"),
    ("F02", "CURRENT_ITEM>CURRENT_ITEM", "zwei Handlungen am selben fortgefuehrten Posten", "[ERSTE HANDLUNG DIES]; [ZWEITE HANDLUNG DIES]"),
    ("F03", "CURRENT_ITEM>CLOSE_STEP", "Handlung am Posten gefolgt von Abschluss", "[HANDLUNG DIES]; [ABSCHLUSSHANDLUNG]"),
    ("F04", "CURRENT_ITEM>QUANTITY_STAGE", "Posten oder Handlung gefolgt von Parameter", "[HANDLUNG DIES]; [MENGE/STUFE]"),
    ("F05", "CURRENT_ITEM>CONTINUE", "Posten gefolgt von Fortsetzung", "[HANDLUNG DIES]; [FORTSETZEN]"),
]


PRACTICE = [
    ("N01", "HERBAL", "F01", "PROC009|PROC008", "Vorgeschriebenes Mass; diesen Pflanzenteil ansetzen."),
    ("N02", "BIOLOGICAL", "F01", "PROC009|PROC031", "Vorgeschriebenes Mass; diesen Badeposten laenger halten."),
    ("N03", "APPARATUS", "F01", "PROC156|PROC095", "Eine Portion; diese durch die Anlage weiterleiten."),
    ("N04", "HERBAL", "F02", "PROC008|PROC001", "Diesen Pflanzenteil ansetzen; ihn kurz abnehmen."),
    ("N05", "BIOLOGICAL", "F02", "PROC031|PROC075", "Diesen Badeposten laenger halten; ihn durch den Durchlass fuehren."),
    ("N06", "APPARATUS", "F02", "PROC095|PROC075", "Diesen Posten weiterleiten; ihn durch den Durchlass fuehren."),
    ("N07", "HERBAL", "F03", "PROC028|PROC078", "Diesen Pflanzenteil auswringen; absetzen und den Schritt schliessen."),
    ("N08", "BIOLOGICAL", "F03", "PROC083|PROC041", "Diesen Badeposten kurz waermen; den Arbeitsgang schliessen."),
    ("N09", "APPARATUS", "F03", "PROC075|PROC108", "Diesen Posten durch den Durchlass fuehren; weiterleiten und schliessen."),
    ("N10", "HERBAL", "F04", "PROC008|PROC009", "Diesen Pflanzenteil ansetzen; das vorgeschriebene Mass notieren."),
    ("N11", "BIOLOGICAL", "F04", "PROC031|PROC009", "Diesen Badeposten laenger halten; das vorgeschriebene Mass notieren."),
    ("N12", "APPARATUS", "F04", "PROC095|PROC156", "Diesen Posten weiterleiten; eine Portion notieren."),
    ("N13", "HERBAL", "F05", "PROC056|PROC013", "Diese Pflanzenzutat nehmen; mit dem vorigen Arbeitsschritt fortfahren."),
    ("N14", "BIOLOGICAL", "F05", "PROC008|PROC013", "Diesen Badeposten ansetzen; fortfahren."),
    ("N15", "APPARATUS", "F05", "PROC075|PROC167", "Diesen Posten durch den Durchlass fuehren; weiterleiten und fortfahren."),
]


def role(card: dict[str, str]) -> str:
    if card["card_class"] == "MEMORIZED_WHOLE_COMMAND":
        return "WHOLE_COMMAND"
    final = card["component_recipe"].split("+")[-1]
    return {
        "DY": "CLOSE_STEP", "Y": "CURRENT_ITEM", "AIN": "QUANTITY_STAGE",
        "AIIN": "QUANTITY_STAGE", "IIN": "QUANTITY_STAGE", "AN": "QUANTITY_STAGE",
        "DA": "QUANTITY_STAGE", "AL": "TARGET", "AR": "SOURCE", "AIR": "FLOW",
        "OR": "PREPARATION", "OL": "CONTINUE", "S": "BOUND_RESULT",
    }.get(final, "OPEN_ACTION")


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    cards = read(P700 / "SEVEN_HUNDREDTH_173_CARD_MANUAL.tsv")
    events = read(P700 / "SEVEN_HUNDREDTH_381_FORWARD_TRACE.tsv")
    role_pairs = read(P704 / "SEVEN_HUNDRED_FOURTH_55_ROLE_BIGRAMS.tsv")
    card_by_no = {row["card_no"]: row for row in cards}
    role_support = {(row["left_role"], row["right_role"]): int(row["token_count"]) for row in role_pairs}

    surface_counts: dict[str, Counter[str]] = defaultdict(Counter)
    exact_pair_counts: Counter[tuple[str, str]] = Counter()
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        surface_counts[event["card_no"]][event["observed_surface"]] += 1
        by_statement[event["statement_id"]].append(event)
    for rows in by_statement.values():
        for left, right in zip(rows, rows[1:]):
            exact_pair_counts[(left["card_no"], right["card_no"])] += 1

    cards_by_role: dict[str, set[str]] = defaultdict(set)
    for card in cards:
        cards_by_role[role(card)].add(card["card_no"])
    form_rows = []
    for form_id, template, purpose, frame in FORMS:
        left, right = template.split(">")
        form_rows.append({
            "form_id": form_id, "role_template": template,
            "observed_template_tokens": role_support[(left, right)],
            "left_slot_card_families": len(cards_by_role[left]),
            "right_slot_card_families": len(cards_by_role[right]),
            "purpose_de": purpose, "dictation_frame_de": frame,
            "apprentice_rule_de": "Besitzer nennen; je Slot eine vorhandene Kartenfamilie waehlen; lokale Oberflaeche kopieren.",
        })

    practice_rows = []
    for item_id, domain, form_id, sequence, prompt in PRACTICE:
        selected = [card_by_no[number] for number in sequence.split("|")]
        roles = [role(card) for card in selected]
        template = ">".join(roles)
        surfaces = []
        for card in selected:
            most_common = surface_counts[card["card_no"]].most_common()
            surfaces.append(most_common[0][0] if most_common else card["surfaces"].split("|")[0])
        practice_rows.append({
            "practice_id": item_id, "domain": domain, "form_id": form_id,
            "fresh_prompt_de": prompt, "role_template": template,
            "role_template_support": role_support[(roles[0], roles[1])],
            "selected_card_sequence": sequence,
            "component_sequence": " | ".join(card["component_recipe"] for card in selected),
            "practice_surface_sequence": " ".join(surfaces),
            "all_allowed_surface_families": " || ".join(card["surfaces"] for card in selected),
            "exact_card_pair_seen_in_fixed_pages": exact_pair_counts[(selected[0]["card_no"], selected[1]["card_no"])],
            "literal_backreading_de": " ; ".join(card["compact_atomic_reading_de"] for card in selected),
            "owner_insertion_de": {"HERBAL": "abgebildete Pflanze/Pflanzenteil", "BIOLOGICAL": "lokale Badestation/Koerperposten", "APPARATUS": "lokale Leitung/Beckenstation"}[domain],
            "new_card": "NO", "new_surface": "NO",
        })

    write("SEVEN_HUNDRED_FIFTH_5_FILLABLE_FORMS.tsv", form_rows)
    write("SEVEN_HUNDRED_FIFTH_15_FRESH_PRACTICE_STATEMENTS.tsv", practice_rows)

    readable = ["# Fuenf Formulare, fuenfzehn neue Uebungssaetze", "", "Alle Oberflaechen stammen aus den festen zehn Seiten; der Satzinhalt ist kreative Werkstattpraxis.", ""]
    for row in practice_rows:
        readable.extend([
            f"## {row['practice_id']} — {row['domain']} / {row['form_id']}", "",
            row["fresh_prompt_de"], "",
            f"Praxisoberflaeche: `{row['practice_surface_sequence']}`", "",
            f"Ruecklesung: {row['literal_backreading_de']}", "",
        ])
    (HERE / "SEVEN_HUNDRED_FIFTH_15_READABLE_PRACTICE_STATEMENTS.md").write_text("\n".join(readable), encoding="utf-8")

    summary = {
        "status": "PASS", "forms": len(form_rows), "fresh_practice_statements": len(practice_rows),
        "domains": dict(Counter(row["domain"] for row in practice_rows)),
        "role_templates": len({row["role_template"] for row in practice_rows}),
        "all_role_templates_attested": all(int(row["role_template_support"]) >= 1 for row in practice_rows),
        "exact_pair_reuses": sum(int(row["exact_card_pair_seen_in_fixed_pages"]) > 0 for row in practice_rows),
        "new_exact_pair_fillings": sum(int(row["exact_card_pair_seen_in_fixed_pages"]) == 0 for row in practice_rows),
        "new_cards": 0, "new_surfaces": 0,
        "decision": "FIVE_ATTESTED_ROLE_FORMS_GENERATE_FIFTEEN_READABLE_PRACTICE_STATEMENTS_FROM_EXISTING_CARDS",
    }
    (HERE / "SEVEN_HUNDRED_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
