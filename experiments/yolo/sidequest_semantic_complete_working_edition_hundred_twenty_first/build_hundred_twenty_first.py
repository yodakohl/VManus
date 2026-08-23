#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
Y = ROOT / "experiments/yolo"


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    atoms = load(Y / "sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_44_ATOM_POCKET.tsv")
    dictionary = load(Y / "sidequest_semantic_exact_portable_deck_hundred_sixteenth_edition/HUNDRED_SIXTEENTH_173_FINAL_TEACHING_DICTIONARY.tsv")
    surfaces = load(Y / "sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_230_SURFACE_INDEX.tsv")
    base_events = load(Y / "sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv")
    clauses = load(Y / "sidequest_semantic_creative_owner_resolution_hundred_seventh_edition/HUNDRED_SEVENTH_254_REVISED_OWNER_BINDING.tsv")
    statements = load(Y / "sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_116_CURRENT_STATEMENTS.tsv")
    formula_statements = {r["statement_id"]: r for r in load(Y / "sidequest_semantic_recurrent_formulae_hundred_eleventh_edition/HUNDRED_ELEVENTH_116_FORMULA_ANNOTATED_STATEMENTS.tsv")}
    order_statements = {r["statement_id"]: r for r in load(Y / "sidequest_semantic_formula_order_hundred_twelfth_edition/HUNDRED_TWELFTH_116_ORDER_ANNOTATED_STATEMENTS.tsv")}
    renderer = {r["event_serial"]: r for r in load(Y / "sidequest_semantic_secondary_renderer_hundred_twentieth_edition/HUNDRED_TWENTIETH_381_REVISED_RENDERER_TRACE.tsv")}
    membership = {r["master_card_id"]: r for r in load(Y / "sidequest_semantic_section_extension_decks_hundred_eighteenth_edition/HUNDRED_EIGHTEENTH_173_SECTION_MEMBERSHIP.tsv")}
    astro = load(Y / "sidequest_semantic_centennial_working_edition/HUNDREDTH_395_ASTRO_GROUPS.tsv")
    shared = load(Y / "sidequest_semantic_exact_portable_deck_hundred_sixteenth_edition/HUNDRED_SIXTEENTH_SEVENTEEN_EXACT_PORTABLE_CARDS.tsv")
    workloads = load(Y / "sidequest_semantic_four_scribe_schedule_hundred_nineteenth_edition/HUNDRED_NINETEENTH_FOUR_SCRIBE_WORKLOADS.tsv")
    habits = {r["renderer_id"]: r for r in load(Y / "sidequest_semantic_secondary_renderer_hundred_twentieth_edition/HUNDRED_TWENTIETH_FOUR_SECONDARY_HAND_HABITS.tsv")}

    write_tsv("HUNDRED_TWENTY_FIRST_44_ATOM_LEXICON.tsv", atoms)
    write_tsv("HUNDRED_TWENTY_FIRST_173_TEACHING_DICTIONARY.tsv", dictionary)
    write_tsv("HUNDRED_TWENTY_FIRST_230_SURFACE_INDEX.tsv", surfaces)
    write_tsv("HUNDRED_TWENTY_FIRST_254_OWNER_CLAUSES.tsv", clauses)
    write_tsv("HUNDRED_TWENTY_FIRST_395_ASTRO_GROUPS.tsv", astro)
    write_tsv("HUNDRED_TWENTY_FIRST_17_SHARED_CARDS.tsv", shared)

    card_map = {r["master_card_id"]: r for r in dictionary}
    statement_map = {r["statement_id"]: r for r in statements}
    event_rows = []
    for row in base_events:
        card = card_map[row["master_card_id"]]
        rr = renderer[row["event_serial"]]
        statement = statement_map[row["statement_id"]]
        event_rows.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["atomic_default_de"],
            "final_teaching_tier": card["final_teaching_tier"],
            "section_deck_status": membership[row["master_card_id"]]["section_deck_status"],
            "assigned_renderer": rr["assigned_renderer"],
            "revised_renderer_status": rr["revised_renderer_status"],
            "formula_tags_for_statement": formula_statements[row["statement_id"]]["formula_tags"],
            "order_tags_for_statement": order_statements[row["statement_id"]]["order_tags"],
            "selected_content_layer": statement["selected_content_layer"],
            "current_statement_reading_de": statement["current_reading_de"],
        })
    write_tsv("HUNDRED_TWENTY_FIRST_381_EVENT_INTERLINEAR.tsv", event_rows)

    statement_rows = []
    for row in statements:
        statement_rows.append({
            **row,
            "formula_tags": formula_statements[row["statement_id"]]["formula_tags"],
            "formula_card_spans": formula_statements[row["statement_id"]]["formula_card_spans"],
            "formula_expansions_de": formula_statements[row["statement_id"]]["formula_expansions_de"],
            "order_tags": order_statements[row["statement_id"]]["order_tags"],
        })
    write_tsv("HUNDRED_TWENTY_FIRST_116_CURRENT_STATEMENTS.tsv", statement_rows)

    hand_rows = []
    for row in workloads:
        secondary = habits[row["renderer_id"]]
        hand_rows.append({
            "renderer_id": row["renderer_id"],
            "workshop_hand": row["workshop_hand"],
            "primary_habit": row["habit"],
            "secondary_gesture": secondary["secondary_gesture"],
            "assigned_records": row["assigned_records"],
            "assigned_events": row["assigned_events"],
            "shared_cards_memorized": row["shared_cards_memorized"],
            "additional_recurrent_cards_memorized": row["additional_recurrent_cards_memorized"],
            "singleton_cards_copied_from_master": row["singleton_cards_copied_from_master"],
            "primary_plus_secondary_events": str(int(row["actual_surface_matches"]) + int(secondary["absorbed_by_secondary"])),
            "remaining_exemplar_overrides": secondary["remaining_master_overrides"],
            "supervision_duty": row["supervision_duty"],
        })
    write_tsv("HUNDRED_TWENTY_FIRST_FOUR_HAND_MANUAL.tsv", hand_rows)

    unified = []
    for row in event_rows:
        unified.append({
            "unified_serial": str(len(unified) + 1),
            "compiler_mode": "COMBINATORIAL_PROSE",
            "page": row["page"],
            "unit_id": row["record_unit_id"],
            "local_address": row["statement_id"] + ":E" + row["event_serial"],
            "visible_identity": row["visible_surface"],
            "registered_identity": row["master_card_id"],
            "short_default_de": row["short_default_de"],
            "continuous_reading_de": row["current_statement_reading_de"],
            "owner_or_namespace": row["selected_content_layer"],
        })
    for row in astro:
        unified.append({
            "unified_serial": str(len(unified) + 1),
            "compiler_mode": "LOCAL_ASTRO_NOMENCLATOR",
            "page": row["page"],
            "unit_id": row["unit_id"],
            "local_address": row["locus"] + ":G" + row["group_serial"],
            "visible_identity": row["opaque_local_id"],
            "registered_identity": row["local_namespace"],
            "short_default_de": row["default_local_meaning_de"],
            "continuous_reading_de": row["instrument_reading_de"],
            "owner_or_namespace": row["local_owner"],
        })
    write_tsv("HUNDRED_TWENTY_FIRST_776_UNIFIED_LEDGER.tsv", unified)

    readable = ["# Vollständige aktuelle Zehnseiten-Lesung", ""]
    by_record = defaultdict(list)
    for row in statement_rows:
        by_record[row["record_unit_id"]].append(row)
    for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]:
        members = by_record[record]
        readable += [f"## {record} — {members[0]['page']}", ""]
        for row in members:
            readable.append(f"- {row['statement_id']}: {row['current_reading_de']}")
        readable.append("")
    for unit in ["A1", "A2", "A3"]:
        members = [r for r in astro if r["unit_id"] == unit]
        readable += [f"## {unit} — {members[0]['page']}", "", members[0]["instrument_reading_de"], "", f"{len(members)} sichtbare Gruppen; jede bleibt im lokalen Namensraum.", ""]
    (OUT / "HUNDRED_TWENTY_FIRST_COMPLETE_TEN_PAGE_READING.md").write_text("\n".join(readable), encoding="utf-8")

    tiers = Counter(r["final_teaching_tier"] for r in dictionary)
    theory = [
        "# Hundertundeinundzwanzigste beste Arbeitstheorie", "",
        "## Kurzfassung", "",
        "Das feste Zehnseiten-System ist ein bildadressiertes Werkstattregister aus einem kleinen",
        "gemeinsamen Ganzkartendeck, portablen Bedeutungsatomen, sektionsgebundenen Karten, fünf",
        "Spezialtafeln und einem getrennten Astro-Nomenklator. Bilder nennen den Gegenstand; Karten",
        "nennen kurze Arbeitswerte; Stellung bindet sie; seltene Werte kommen aus dem Masterexemplar.", "",
        "## Gemeinsames Deck", "",
        "Siebzehn exakte Karten sind zwischen Herbal und Biological portabel. Nur aiin erscheint in",
        "allen elf Prosa-Records. Das Deck schreibt 136/381 Ereignisse und drei vollständige vorhandene",
        "Aussagen; es ist Steuergerüst, nicht Gesamtlexikon.", "",
        "## Fachdecks", "",
        "Herbal: 17 gemeinsame + 49 exklusive = 66 Karten für 100 Ereignisse. Biological: 17 + 107",
        "= 124 Karten für 281 Ereignisse. Herbal kopiert exemplarreiche Bildartikel; Biological nutzt",
        "ein stärker wiederkehrendes Zubereitungs-, Bade- und Serviceprozessdeck.", "",
        "## Inhalt", "",
        "Der konkrete Lead ist ein illustriertes Pflanzen- und therapeutisches Badewerk mit eigener",
        "Zubereitung/Wartung sowie drei unabhängigen lokalen Himmelsinstrumenten. Das ist eine vollständige",
        "Arbeitsübersetzung, keine behauptete Entzifferung.", "",
        "## Vier Hände", "",
        "Vier Hände mit je zwei Vorlieben erklären 306/381 Oberflächen direkt; 75 seltene Varianten werden",
        "aus der Seitenvorlage kopiert. Alle lernen das 17-Karten-Deck, aber niemand muss alle 173 Karten",
        "frei memorieren.", "",
        "f84 und f84r bleiben versiegelt.",
    ]
    (OUT / "HUNDRED_TWENTY_FIRST_BEST_WORKING_THEORY.md").write_text("\n".join(theory) + "\n", encoding="utf-8")
    report = [
        "# Hundertundeinundzwanzigste vollständige Arbeitsausgabe", "",
        "Die R110–R120-Korrekturen stehen jetzt in einer einzigen reproduzierbaren Ausgabe.",
        "Sie enthält 44 Atome, 173 Karten, 230 Oberflächen, 254 Besitzerklauseln, 381 Prosaereignisse,",
        "116 Aussagen, 395 Astrogruppen, 776 Gesamtgruppen, siebzehn gemeinsame Karten und vier Hände.", "",
        "Die wichtigsten neuen Bindungen sind die zehn Mehrkartenformeln, die geordnete Y–AIIN–Y-",
        "Gleichmaßform, der 17/49/107-Decksplit, fünf Spezialtafeln, die lokale Bio-Bad/Service-Lesung",
        "und das Zwei-Gewohnheiten-plus-Exemplar-Modell der Schreiber.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_TWENTY_FIRST_COMPLETE_EDITION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "atoms": len(atoms), "cards": len(dictionary), "surfaces": len(surfaces),
        "clauses": len(clauses), "events": len(event_rows), "statements": len(statement_rows),
        "astro_groups": len(astro), "unified": len(unified), "shared_cards": len(shared), "hands": len(hand_rows),
        "teaching_tiers": dict(tiers),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
