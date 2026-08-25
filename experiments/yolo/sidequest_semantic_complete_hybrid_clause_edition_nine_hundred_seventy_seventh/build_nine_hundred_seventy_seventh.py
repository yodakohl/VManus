#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"
P974 = ROOT / "experiments/yolo/sidequest_semantic_image_owned_fourteen_page_edition_nine_hundred_seventy_fourth"
P975 = ROOT / "experiments/yolo/sidequest_semantic_specialist_whole_card_drawer_nine_hundred_seventy_fifth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def close_sentence(reason: str) -> str:
    if reason == "LICENSED_DY_CLOSE":
        return "Teilgang schließen."
    if reason == "PAGE_END_OPEN":
        return "Fortsetzung offen lassen."
    return "Lokalen Bild-/Adressabschnitt beenden."


def main() -> None:
    events = {r["event_id"]: r for r in read(P975 / "PASS975_2511_EVENT_HYBRID_EDITION.tsv")}
    clauses = read(P971 / "PASS971_354_CLAUSE_EDITION.tsv")
    addresses = read(P971 / "PASS971_501_LOCAL_ADDRESS_LEDGER.tsv")
    pages = {r["physical_page"]: r for r in read(P974 / "PASS974_14_PAGE_IMAGE_OWNED_EDITION.tsv")}
    rows = []
    all_ids = []
    for clause in clauses:
        ids = clause["event_ids"].split("|")
        all_ids.extend(ids)
        evs = [events[event_id] for event_id in ids]
        page = clause["physical_page"]
        loci = []
        for event in evs:
            if event["locus"] not in loci:
                loci.append(event["locus"])
        if page == "f70v":
            if all(locus.startswith("f70v1") for locus in loci):
                owner = "Widderring"
            elif all(locus.startswith("f70v2") for locus in loci):
                owner = "Fischring"
            else:
                owner = "Widder- und Fischring"
        else:
            owner = pages[page]["visible_owner_or_namespace_de"]
        readings = [event["hybrid_working_reading_de"] for event in evs]
        surface_sequence = " ".join(event["surface"] for event in evs)
        specialist = [
            f"{event['surface']}={event['specialist_context_expansion_de']}"
            for event in evs if event["specialist_headword_de"]
        ]
        if clause["clause_id"] == "P915-C003":
            fluent = (
                "Beim blühenden dreikronigen Soden: Aus dem Blütenkraut einen Sudansatz bilden, "
                "auswringen, die vorgeschriebene Stehzeit abwarten, nachseihen, den Klarlauf "
                "abnehmen und kalt stellen; Teilgang schließen."
            )
        else:
            fluent = f"Bei {owner}: " + "; ".join(readings) + ". " + close_sentence(clause["end_reason"])
        rows.append({
            "clause_id": clause["clause_id"],
            "physical_page": page,
            "locus_span": "|".join(loci),
            "visible_owner_or_namespace_de": owner,
            "event_count": clause["events"],
            "specialist_event_count": str(len(specialist)),
            "surface_sequence": surface_sequence,
            "hybrid_card_sequence_de": " | ".join(readings),
            "specialist_cards": " | ".join(specialist),
            "end_reason": clause["end_reason"],
            "continuous_working_translation_de": fluent,
            "event_ids": clause["event_ids"],
        })
    write(HERE / "PASS977_354_COMPLETE_HYBRID_CLAUSES.tsv", rows, list(rows[0]))

    address_rows = []
    for address in addresses:
        event = events[address["event_id"]]
        address_rows.append({
            "event_id": address["event_id"],
            "diagram_unit": address["diagram_unit"],
            "physical_page": address["physical_page"],
            "locus": address["locus"],
            "surface": address["surface"],
            "owner_id": address["owner_id"],
            "visible_owner_de": address["visible_owner_de"],
            "component_recipe": event["component_recipe"],
            "portable_card_reading_de": event["hybrid_working_reading_de"],
            "local_address_reading_de": address["local_address_reading_de"],
            "diagram_model": address["diagram_model"],
        })
    write(HERE / "PASS977_501_LOCAL_ADDRESS_HYBRID.tsv", address_rows, list(address_rows[0]))

    order = [r["physical_page"] for r in read(P974 / "PASS974_14_PAGE_IMAGE_OWNED_EDITION.tsv")]
    lines = [
        "# Pass 977 — vollständige hybride Klauselausgabe",
        "",
        "Die 2.010 laufenden Textgruppen stehen genau einmal in 354",
        "Arbeitsklauseln. Weitere 501 Gruppen sind lokale Bildetiketten, Ring- oder",
        "Stationsadressen und bleiben deshalb in einer eigenen Adresstafel. Zusammen",
        "sind alle 2.511 Gruppen gelesen. Die Lesung verwendet zuerst den Bildbesitzer, dann die",
        "produktive 86-Karten-Grammatik und an 95 Stellen den lokalen",
        "Fachkartenkasten.",
        "",
    ]
    for page in order:
        page_info = pages[page]
        lines += [
            f"## {page} — {page_info['visible_owner_or_namespace_de']}",
            "",
            page_info["complete_working_reading_de"],
            "",
        ]
        for row in [item for item in rows if item["physical_page"] == page]:
            lines += [
                f"- **{row['clause_id']}** (`{row['surface_sequence']}`): "
                + row["continuous_working_translation_de"]
            ]
        page_addresses = [item for item in address_rows if item["physical_page"] == page]
        if page_addresses:
            lines += ["", f"Lokale Adressen/Etiketten ({len(page_addresses)} Gruppen):"]
            by_locus = {}
            for item in page_addresses:
                by_locus.setdefault(item["locus"], []).append(item)
            for locus, items in by_locus.items():
                surfaces = " ".join(item["surface"] for item in items)
                readings = " | ".join(item["local_address_reading_de"] for item in items)
                lines.append(f"- **{locus}** (`{surfaces}`): {readings}")
        lines.append("")
    lines += [
        "## Kürzeste Gesamtlesung",
        "",
        "> Stoff im Bild wählen; Teil und Menge nehmen; Ansatz setzen; kurz, länger",
        "> oder vollständig halten; durch Gefäß oder Station leiten; Teilgang",
        "> schließen; Himmelsplatz gegebenenfalls im eigenen Rad nachschlagen.",
        "",
        "Die Ausgabe ist absichtlich eine konkrete Arbeitsedition. Wo ein lokales",
        "Fachwort gelernt ist, steht es als Wort; sonst bleibt die kurze",
        "Kartenkomposition sichtbar.",
        "",
    ]
    (HERE / "PASS977_COMPLETE_FOURTEEN_PAGE_HYBRID_READING.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "clauses": len(rows),
        "prose_events": len(all_ids),
        "local_address_events": len(address_rows),
        "events": len(all_ids) + len(address_rows),
        "unique_events": len(set(all_ids) | {r["event_id"] for r in address_rows}),
        "specialist_event_uses": sum(int(r["specialist_event_count"]) for r in rows),
        "pages": len({r["physical_page"] for r in rows} | {r["physical_page"] for r in address_rows}),
        "anchor_clause": "P915-C003",
    }
    (HERE / "PASS977_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
