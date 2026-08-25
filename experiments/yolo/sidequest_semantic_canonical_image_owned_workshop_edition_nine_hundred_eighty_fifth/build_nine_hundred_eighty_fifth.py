#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P977 = ROOT / "experiments/yolo/sidequest_semantic_complete_hybrid_clause_edition_nine_hundred_seventy_seventh"
P979 = ROOT / "experiments/yolo/sidequest_semantic_f13r_root_crown_article_nine_hundred_seventy_ninth"
P981 = ROOT / "experiments/yolo/sidequest_semantic_fourteen_page_readable_fourth_edition_nine_hundred_eighty_first"
P983 = ROOT / "experiments/yolo/sidequest_semantic_159_unit_address_aware_codebook_nine_hundred_eighty_third"
P984 = ROOT / "experiments/yolo/sidequest_semantic_53_root_plain_dictionary_nine_hundred_eighty_fourth"


F88_CLAUSES = {
    "P915-C350": (
        "Die sechs oberen Drogenposten auswählen, vom bezeichneten Vorrat die Sollmengen nehmen, in das obere Gefäß geben, "
        "kurz vorbereiten und den entstehenden Auszug zur nächsten Aufnahme leiten."
    ),
    "P915-C351": (
        "Mit dem mittleren Drogenfach einen zweiten Ansatz beginnen, einen Anteil überführen und den kurzen Auftakt schließen."
    ),
    "P915-C352": (
        "Die übrigen mittleren Drogenposten nach Sollmaß zugeben, den Ansatz mehrfach fortführen, den Auszug leiten, länger "
        "halten und den Teilgang schließen."
    ),
    "P915-C353": (
        "Von den vier unteren Drogenposten den ersten Vorrat nehmen, kurz ansetzen, länger auffangen und den Vorbereitungsgang schließen."
    ),
    "P915-C354": (
        "Die letzte Gefäßcharge fortsetzen, weitere Anteile nach Sollmaß zugeben, den Auszug leiten, einen Folgeteil nehmen und "
        "den unteren Ansatz schließen."
    ),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    codebook = read(P983 / "PASS983_159_TEACHING_UNIT_CODEBOOK.tsv")
    events = read(P983 / "PASS983_2511_EVENT_ADDRESS_AWARE_BINDING.tsv")
    roots = read(P984 / "PASS984_53_PORTABLE_ROOT_DICTIONARY.tsv")
    pages = read(P981 / "PASS981_FOURTEEN_PAGE_READABLE_EDITION.tsv")
    address = read(P977 / "PASS977_501_LOCAL_ADDRESS_HYBRID.tsv")
    clauses = read(P977 / "PASS977_354_COMPLETE_HYBRID_CLAUSES.tsv")
    f13 = {r["clause_id"]: r["complete_working_translation_de"] for r in read(P979 / "PASS979_FIVE_STAGE_ROOT_CROWN_ARTICLE.tsv")}
    event_by_id = {r["event_id"]: r for r in events}

    write(HERE / "PASS985_159_CODEBOOK.tsv", codebook, list(codebook[0]))
    write(HERE / "PASS985_2511_EVENT_INTERLINEAR.tsv", events, list(events[0]))
    write(HERE / "PASS985_53_ROOT_DICTIONARY.tsv", roots, list(roots[0]))
    write(HERE / "PASS985_14_PAGE_READABLE_EDITION.tsv", pages, list(pages[0]))
    write(HERE / "PASS985_501_LOCAL_ADDRESS_LEDGER.tsv", address, list(address[0]))

    clause_rows = []
    for clause in clauses:
        clause_events = [event_by_id[event_id] for event_id in clause["event_ids"].split("|")]
        if clause["clause_id"] in f13:
            reading = f13[clause["clause_id"]]
            reading_source = "F13_IMAGE_PART_ARTICLE"
        elif clause["clause_id"] in F88_CLAUSES:
            reading = F88_CLAUSES[clause["clause_id"]]
            reading_source = "F88_THREE_BATCH_PHARMACY"
        elif clause["clause_id"] == "P915-C003":
            reading = clause["continuous_working_translation_de"]
            reading_source = "F11_COMPLETE_FILTRATION_RECIPE"
        else:
            reading = (
                f"Bei {clause['visible_owner_or_namespace_de']}: "
                + "; ".join(event["complete_working_reading_de"] for event in clause_events)
                + ("; Teilgang schließen." if clause["end_reason"] == "LICENSED_DY_CLOSE" else "; Fortsetzung offen.")
            )
            reading_source = "CARD_BY_CARD_IMAGE_OWNER_EXPANSION"
        clause_rows.append({
            "clause_id": clause["clause_id"],
            "physical_page": clause["physical_page"],
            "locus_span": clause["locus_span"],
            "visible_owner_or_namespace_de": clause["visible_owner_or_namespace_de"],
            "event_count": clause["event_count"],
            "surface_sequence": clause["surface_sequence"],
            "complete_working_translation_de": reading,
            "reading_source": reading_source,
            "end_reason": clause["end_reason"],
            "event_ids": clause["event_ids"],
        })
    write(HERE / "PASS985_354_COMPLETE_CLAUSE_EDITION.tsv", clause_rows, list(clause_rows[0]))

    lines = [
        "# Pass 985 — aktuelle kanonische Sidequest-Arbeitsausgabe",
        "",
        "## Kurzfassung",
        "",
        "Das Manuskriptstück wird als bildadressiertes Werkstattbuch gelesen:",
        "",
        "> Pflanzenstoff wählen → im Gefäß zubereiten → in Bad, Auflage oder",
        "> Station anwenden → Himmelsplatz oder Arbeitsklasse nachschlagen.",
        "",
        "## Schreibsystem",
        "",
        "Ein Lehrling lernt 159 Einheiten:",
        "",
        "- 53 portable Bedeutungswurzeln und 3 lokale Diagrammzeichen;",
        "- 30 häufige Formelkarten;",
        "- 51 ältere Fachwort-Einheiten;",
        "- 5 Bildteilkarten auf f13r;",
        "- 16 Drogenetiketten auf f88r;",
        "- 1 Regel zum Kopieren lokaler Bild- und Ringadressen.",
        "",
        "Die längste gelernte Karte gewinnt. Sonst werden Wurzeln von links nach",
        "rechts komponiert. `E/EE/EEE` geben kurz/länger/vollständig an; `Y` hält",
        "den aktuellen POSTEN; nur gelernte `DY`-Karten schließen. Ein Labelort",
        "kopiert die ganze Bildadresse und zwingt ähnlich aussehende Teile nicht in",
        "eine falsche Werkstattbedeutung.",
        "",
        "## Vollständigkeit",
        "",
        "- 2.511 sichtbare Gruppen auf 14 physischen Seiten;",
        "- 2.010 laufende Textgruppen in 354 Aussagen;",
        "- 501 Bildetiketten, Ring- und Stationsadressen;",
        "- 53 kurze Stammwerte;",
        "- jede Gruppe, Aussage und Seite mit einer konkreten Arbeitslesung.",
        "",
        "## Stärkster fortlaufender Auszug",
        "",
        "`tshol schoal cfhy shfydaiin cphy shey tchody`",
        "",
        "> Vom Blütenkraut einen Sudansatz bilden, auswringen, die vorgeschriebene",
        "> Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; Schluss.",
        "",
        "`shey` bedeutet hier nur KLARLAUF. Die Handlung steckt in den sechs",
        "anderen Karten; kein Wort trägt einen ganzen Satz.",
        "",
        "## Bildrevisionen, die bleiben",
        "",
        "- f55v: große Doldenpflanze, keine bevorzugte Wasserpflanze;",
        "- f56r: mehrere Reifestufen eines stachelköpfigen Krauts;",
        "- f13r: Wurzelkrone, kleine Rundkörper, Blatt- und Blütenanteil;",
        "- f88r: drei Gefäßchargen mit sechs, sechs und vier Drogenposten;",
        "- f70v: Widder- und Fischring als Adressregister;",
        "- f75r: stark repetitives Stationsformular ohne neues Fachwortinventar.",
        "",
        "## Historischer Mechanismus",
        "",
        "Die nächste reale Analogie ist kein einzelnes Geheimlexikon, sondern die",
        "Mischung aus Nomenklatorvorrang, produktiven Kürzeln und stabilen",
        "Notationsmodifikatoren. Ein bebildertes Herbal/Antidotarium mit Bad- und",
        "Kalenderteilen liefert den plausibelsten Buchtyp; f88r zeigt den Übergang",
        "zwischen lokalem Drogennamen und produktiver Rezeptprosa direkt.",
        "",
        "## Arbeitsstatus",
        "",
        "Dies ist die beste kreative Werkstatttheorie der vierzehn freigegebenen",
        "Seiten. Sie ist eine konkrete Übersetzungsbasis, keine behauptete",
        "historische Entzifferung. Neue Seiten sind für den nächsten echten",
        "Reality-Check noch nicht nötig; der größte verbleibende Gewinn liegt in",
        "natürlicheren Lesungen der langen Stationsaussagen und in vorsichtigen",
        "botanischen Namen für die sechzehn f88r-Drogenposten.",
        "",
    ]
    (HERE / "PASS985_CURRENT_WORKING_THEORY.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "codebook_units": len(codebook),
        "roots": len(roots),
        "events": len(events),
        "clauses": len(clause_rows),
        "addresses": len(address),
        "pages": len(pages),
    }
    (HERE / "PASS985_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
