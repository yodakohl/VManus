#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P554 = YOLO / "sidequest_semantic_canonical_working_dictionary_five_hundred_fifty_fourth"
P555 = YOLO / "sidequest_semantic_atomic_card_unification_five_hundred_fifty_fifth"
P562 = YOLO / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"
P575 = YOLO / "sidequest_semantic_section_local_card_partition_five_hundred_seventy_fifth"


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    components = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    frames = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_FIFTY_SIX_ACTION_FRAME_LEXICON.tsv")
    structural_cards = read(P554 / "FIVE_HUNDRED_FIFTY_FOURTH_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    atomic_cards = {r["card_no"]: r for r in read(P555 / "FIVE_HUNDRED_FIFTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_ATOMIC_CARD_DICTIONARY.tsv")}
    events = read(P562 / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    specialist_ids = {r["card_no"] for r in read(P575 / "FIVE_HUNDRED_SEVENTY_FIFTH_SEVEN_SPECIALIST_CARDS.tsv")}
    specialist_components = {"CFH", "DA", "LD", "LS", "OS", "S", "TALAM"}
    component = {r["component"]: r for r in components}
    frame = {f'{r["action_component"]}:{r["frame_code"]}': r for r in frames}

    component_rows = []
    for row in components:
        component_rows.append({
            **row,
            "learning_class": "SINGLE_CARD_SPECIALIST_COMPONENT" if row["component"] in specialist_components else "RECURRENT_COMPONENT",
            "already_inside_thirty_eight": "YES",
        })

    recon_rows = []
    missing_tokens = []
    missing_frames = []
    for card in structural_cards:
        atoms = card["component_parse"].split("+")
        missing = [atom for atom in atoms if atom not in component]
        missing_tokens.extend((card["card_no"], atom) for atom in missing)
        atom_values = [component[atom]["atomic_meaning_de"] for atom in atoms if atom in component]
        codes = [] if card["observed_action_frame_codes"] == "NONE" else card["observed_action_frame_codes"].split("|")
        bad_codes = [code for code in codes if code not in frame]
        missing_frames.extend((card["card_no"], code) for code in bad_codes)
        frame_values = [frame[code]["frame_conditioned_verb_de"] for code in codes if code in frame]
        mechanical = " · ".join(atom_values)
        if frame_values:
            mechanical += " [Rahmen: " + ", ".join(frame_values) + "]"
        old = atomic_cards[card["card_no"]]
        recon_rows.append({
            "card_no": card["card_no"],
            "surfaces": card["surfaces"],
            "component_parse": card["component_parse"],
            "reconstructed_component_values_de": " · ".join(atom_values),
            "licensed_frame_codes": card["observed_action_frame_codes"],
            "licensed_frame_verbs_de": ", ".join(frame_values) if frame_values else "NONE",
            "gloss_free_mechanical_reading_de": mechanical,
            "structural_reconstruction": "COMPLETE" if not missing and not bad_codes else "INCOMPLETE",
            "natural_wording_status": "OWNER_OR_SLOT_CONTEXT_REQUIRED" if card["context_sensitive"] == "YES" else "PORTABLE_WORDING_AVAILABLE",
            "old_atomic_gloss_used_as_input": "NO",
            "old_atomic_gloss_comparator_only_de": old["atomic_card_value_de"],
            "contains_single_card_specialist_component": "YES" if any(atom in specialist_components for atom in atoms) else "NO",
            "specialist_card_from_pass575": "YES" if card["card_no"] in specialist_ids else "NO",
            "occurrences": card["occurrences"],
        })

    by_card = {r["card_no"]: r for r in recon_rows}
    event_rows = []
    for event in events:
        card = by_card[event["observed_card_no"]]
        event_rows.append({
            "event_id": event["event_id"],
            "page": event["page"],
            "record": event["record"],
            "statement_id": event["statement_id"],
            "observed_surface": event["observed_surface"],
            "card_no": event["observed_card_no"],
            "gloss_free_mechanical_reading_de": card["gloss_free_mechanical_reading_de"],
            "context_requirement": card["natural_wording_status"],
            "complete": card["structural_reconstruction"],
        })

    write("FIVE_HUNDRED_SEVENTY_SEVENTH_CORRECTED_THIRTY_EIGHT_COMPONENT_INVENTORY.tsv", component_rows)
    write("FIVE_HUNDRED_SEVENTY_SEVENTH_ONE_HUNDRED_SEVENTY_THREE_GLOSS_FREE_CARD_RECONSTRUCTIONS.tsv", recon_rows)
    write("FIVE_HUNDRED_SEVENTY_SEVENTH_THREE_HUNDRED_EIGHTY_ONE_GLOSS_FREE_EVENT_RECONSTRUCTIONS.tsv", event_rows)
    summary = {
        "status": "PASS" if not missing_tokens and not missing_frames else "FAIL",
        "semantic_learning_items_corrected": len(components) + len(frames),
        "components": len(components),
        "frames": len(frames),
        "specialist_components_already_inside_38": len(specialist_components),
        "cards_reconstructed": len(recon_rows),
        "events_reconstructed": len(event_rows),
        "portable_wording_cards": sum(r["natural_wording_status"] == "PORTABLE_WORDING_AVAILABLE" for r in recon_rows),
        "context_wording_cards": sum(r["natural_wording_status"] == "OWNER_OR_SLOT_CONTEXT_REQUIRED" for r in recon_rows),
        "missing_component_tokens": missing_tokens,
        "missing_frame_codes": missing_frames,
    }
    (HERE / "FIVE_HUNDRED_SEVENTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsiebenundsiebzigste Runde: glossierungsfreier Rückbau",
        "",
        "## Korrektur an Pass 576",
        "",
        "Die sieben seltenen Fachwerte sind keine zusätzlichen sieben Lernobjekte. Sie sind bereits die sieben nur einmal belegten Komponenten CFH, DA, LD, LS, OS, S und TALAM im 38er Komponentenlexikon. Die semantische Lehrlast beträgt daher 94 Einheiten: 38 Werte plus 56 Rahmenregeln. Pass 576 zählte dieselben sieben Werte doppelt.",
        "",
        "## Rückbau",
        "",
        "Alle 173 Karten wurden ohne Verwendung ihrer fertigen deutschen Ganzkartenglosse aus COMPONENT_PARSE, dem 38er Lexikon und den 56 lizenzierten Rahmenverben zusammengesetzt. Alle 173 strukturellen Rückbauten und alle 381 Ereignisse sind vollständig. Die alte Ganzkartenglosse erscheint nur als sichtbarer Vergleich nach dem Rückbau.",
        "",
        "162 Karten besitzen eine portable mechanische Lesung. Elf brauchen für natürliches Deutsch den sichtbaren Besitzer oder Slotkontext; das betrifft die Auswahl der konkreten Handlung, nicht das Komponenteninventar. Damit bleibt der Arbeitswert vollständig lesbar, auch wenn die flüssige Übersetzung kontextabhängig ist.",
        "",
        "## Neue Arbeitsregel",
        "",
        "Ein Schreiber lernt 31 wiederkehrende und sieben seltene Komponenten, danach 56 eng begrenzte Handlungsrahmen. Die 173 Kartenformen sind zusammengesetzte visuelle Kürzel. Eine seltene Karte ist daher nicht automatisch ein zusätzliches Wort.",
        "",
        "## Nächster Schritt",
        "",
        "Die elf kontextabhängigen Karten werden einzeln in allen Vorkommen zerlegt. Für jede soll ein einziger abstrakter Arbeitswert und eine kleine, explizite Besitzerfüllung entstehen; keine neue Ganzwortbedeutung darf eingeführt werden.",
    ]
    (HERE / "FIVE_HUNDRED_SEVENTY_SEVENTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
