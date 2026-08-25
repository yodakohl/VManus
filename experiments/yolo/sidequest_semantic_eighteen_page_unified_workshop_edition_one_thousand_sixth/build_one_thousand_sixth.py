#!/usr/bin/env python3
"""Build the unified eighteen-page creative workshop edition (Pass 1006)."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P1002 = ROOT / "experiments/yolo/sidequest_semantic_dual_layer_release_one_thousand_second"
P1005 = ROOT / "experiments/yolo/sidequest_semantic_allograph_and_open_tail_consolidation_one_thousand_fifth"
OLD_EVENTS_PATH = P1002 / "PASS1002_2511_DUAL_EVENT_INTERLINEAR.tsv"
OLD_CLAUSES_PATH = P1002 / "PASS1002_354_DUAL_CLAUSE_EDITION.tsv"
CODEBOOK_PATH = P1002 / "PASS1002_175_CURRENT_CODEBOOK.tsv"
NEW_EVENTS_PATH = P1005 / "PASS1005_657_CONSOLIDATED_EVENT_INTERLINEAR.tsv"
NEW_STATEMENTS_PATH = P1005 / "PASS1005_108_CONSOLIDATED_STATEMENTS.tsv"
NEW_COMBINED_PATH = P1005 / "PASS1005_3168_COMBINED_EVENT_INTERLINEAR.tsv"
ALLOGRAPH_PATH = P1005 / "PASS1005_34_ALLOGRAPH_DECISIONS.tsv"
ROOT_SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)

PAGE_ORDER = [
    "f10r", "f11r", "f13r", "f17r", "f55v", "f56r",
    "f67r2", "f68r1", "f69v", "f70v", "f71v",
    "f75r", "f77r", "f81v", "f82r", "f83r", "f88r", "f88v",
]
PAGE_INDEX = {page: number for number, page in enumerate(PAGE_ORDER)}
REGISTER = {
    **{page: "HERBAL" for page in ("f10r", "f11r", "f13r", "f17r", "f55v", "f56r")},
    **{page: "CELESTIAL" for page in ("f67r2", "f68r1", "f69v", "f70v", "f71v")},
    **{page: "BIOLOGICAL" for page in ("f75r", "f77r", "f81v", "f82r", "f83r")},
    **{page: "PHARMA" for page in ("f88r", "f88v")},
}
PAGE_DESCRIPTION = {
    "f10r": "Pflanzenartikel mit zwei langen Zubereitungsgängen",
    "f11r": "Pflanzenartikel mit Trennen, Stehenlassen und Nachseihen",
    "f13r": "Pflanzenartikel mit offenem Prozesslauf",
    "f17r": "Pflanzenartikel der grossen Blütenpflanze",
    "f55v": "Pflanzen-/Anwendungsartikel mit fünf Teilgängen",
    "f56r": "Pflanzenartikel mit wiederaufgenommenem Bildbesitzer",
    "f67r2": "mehrteiliges Himmels- und Wahlregister",
    "f68r1": "Sternstations- und Ringregister",
    "f69v": "drei lokale Himmelsräder als reines Adressregister",
    "f70v": "Widder- und Fischring als reines Adressregister",
    "f71v": "drei weitere Ringnamensräume",
    "f75r": "Becken-, Figuren- und Stationsartikel",
    "f77r": "langer Körper-/Beckenstationsartikel",
    "f81v": "gemeinschaftliche Becken- und Anwendungseinträge",
    "f82r": "mehrere lokale Figuren-/Beckenstationen",
    "f83r": "lokale Becken-, Bogen- und Verbindungsszenen",
    "f88r": "Gefäss-/Drogenregister mit sechzehn lokalen Etiketten",
    "f88v": "drei Gefäss- und Zutatenpartien",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"cannot infer fields for {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def natural_boundary(end_mode: str) -> str:
    if end_mode == "LICENSED_DY_CLOSE":
        return "Die gelernte Schlusskarte beendet den Teilgang."
    if end_mode == "PAGE_END_OPEN":
        return "Der Seitenlauf bleibt ohne ergänzte Schlusskarte offen."
    if end_mode == "NONPROSE_OWNER_OR_DIAGRAM_BOUNDARY":
        return "Der sichtbare Bild- oder Diagrammbesitzer beendet diesen Eintrag."
    return end_mode.replace("_", " ").capitalize() + "."


def main() -> int:
    old_events = read_tsv(OLD_EVENTS_PATH)
    old_clauses = read_tsv(OLD_CLAUSES_PATH)
    new_events = read_tsv(NEW_EVENTS_PATH)
    new_statements = read_tsv(NEW_STATEMENTS_PATH)
    combined_source = read_tsv(NEW_COMBINED_PATH)
    allograph_decisions = read_tsv(ALLOGRAPH_PATH)
    roots = read_tsv(ROOT_SOURCE)
    root_names = {row["recognition_form"] for row in roots}

    old_by_id = {row["event_id"]: row for row in old_events}
    new_by_id = {row["fresh_event_id"]: row for row in new_events}
    old_event_position = {row["event_id"]: number for number, row in enumerate(old_events)}
    new_running_order = [row["fresh_event_id"] for row in new_events if row["kind"] != "L"]
    new_event_position = {event_id: number for number, event_id in enumerate(new_running_order)}

    pending: list[dict[str, object]] = []
    for row in old_clauses:
        event_ids = row["event_ids"].split("|")
        locus_list = row["locus_span"].split("|")
        pending.append(
            {
                "_sort": (PAGE_INDEX[row["physical_page"]], old_event_position[event_ids[0]]),
                "legacy_statement_id": row["clause_id"],
                "physical_page": row["physical_page"],
                "register": REGISTER[row["physical_page"]],
                "visible_owner_or_namespace_de": row["visible_owner_or_namespace_de"],
                "locus_span": row["locus_span"],
                "locus_count": len(locus_list),
                "crosses_physical_line": "YES" if len(locus_list) > 1 else "NO",
                "event_count": len(event_ids),
                "surface_sequence": row["surface_sequence"],
                "component_sequence": " | ".join(old_by_id[event_id]["component_recipe"] for event_id in event_ids),
                "portable_literal_de": row["portable_root_sequence_de"],
                "fluent_workshop_de": row["local_fluent_expansion_de"],
                "end_mode": row["end_reason"],
                "boundary_reading_de": natural_boundary(row["end_reason"]),
                "reading_source": row["reading_source"],
                "source_release": "PASS1002",
                "event_ids": "|".join(event_ids),
            }
        )

    for row in new_statements:
        start = new_event_position[row["first_event_id"]]
        end = new_event_position[row["last_event_id"]]
        event_ids = new_running_order[start : end + 1]
        loci: list[str] = []
        for event_id in event_ids:
            locus = new_by_id[event_id]["locus"]
            if not loci or loci[-1] != locus:
                loci.append(locus)
        pending.append(
            {
                "_sort": (PAGE_INDEX[row["physical_page"]], 100000 + start),
                "legacy_statement_id": row["statement_id"],
                "physical_page": row["physical_page"],
                "register": REGISTER[row["physical_page"]],
                "visible_owner_or_namespace_de": row["visible_owner_de"],
                "locus_span": "|".join(loci),
                "locus_count": len(loci),
                "crosses_physical_line": row["crosses_physical_line"],
                "event_count": len(event_ids),
                "surface_sequence": row["surface_sequence"],
                "component_sequence": row["component_sequence"],
                "portable_literal_de": row["literal_workshop_de"],
                "fluent_workshop_de": row["fluent_workshop_de"],
                "end_mode": row["end_mode"],
                "boundary_reading_de": row["boundary_reading_de"],
                "reading_source": "PASS1005_FLUENT_WORKSHOP",
                "source_release": "PASS1005",
                "event_ids": "|".join(event_ids),
            }
        )

    pending.sort(key=lambda row: row["_sort"])
    statements: list[dict[str, object]] = []
    statement_by_event: dict[str, str] = {}
    for number, row in enumerate(pending, 1):
        clean = {key: value for key, value in row.items() if key != "_sort"}
        clean = {"statement_id": f"P1006-S{number:03d}", **clean}
        statements.append(clean)
        for event_id in str(clean["event_ids"]).split("|"):
            if event_id in statement_by_event:
                raise ValueError(f"event assigned twice: {event_id}")
            statement_by_event[event_id] = str(clean["statement_id"])
    write_tsv(HERE / "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv", statements)

    combined_by_id = {row["event_id"]: row for row in combined_source}
    if len(combined_by_id) != len(combined_source):
        raise ValueError("duplicate combined event IDs")
    event_rows: list[dict[str, object]] = []
    address_rows: list[dict[str, object]] = []
    for sequence, source_row in enumerate(combined_source, 1):
        event_id = source_row["event_id"]
        statement_id = statement_by_event.get(event_id, "")
        event_role = "RUNNING_STATEMENT" if statement_id else "LOCAL_ADDRESS_OR_LABEL"
        row = {
            "book_event_ordinal": sequence,
            "event_id": event_id,
            "physical_page": source_row["physical_page"],
            "register": REGISTER[source_row["physical_page"]],
            "locus": source_row["locus"],
            "kind": source_row["kind"],
            "surface": source_row["surface"],
            "component_recipe": source_row["component_recipe"],
            "portable_default_de": source_row["portable_default_de"],
            "local_contextual_expansion_de": source_row["local_contextual_expansion_de"],
            "event_role": event_role,
            "statement_id": statement_id,
            "source_release": source_row["edition_source"],
        }
        event_rows.append(row)
        if event_role == "LOCAL_ADDRESS_OR_LABEL":
            address_rows.append(row)
    write_tsv(HERE / "PASS1006_3168_UNIFIED_EVENT_LEDGER.tsv", event_rows)
    write_tsv(HERE / "PASS1006_550_LOCAL_ADDRESS_LEDGER.tsv", address_rows)

    # Keep the established 175 teaching lines byte-for-byte.
    shutil.copyfile(CODEBOOK_PATH, HERE / "PASS1006_175_APPRENTICE_CODEBOOK.tsv")

    allograph_rules: list[dict[str, object]] = []
    for number, row in enumerate(
        [item for item in allograph_decisions if item["decision_class"] == "LICENSED_ALLOGRAPH"], 1
    ):
        allograph_rules.append(
            {
                "rule_id": f"A{number:02d}",
                "surface": row["surface"],
                "registered_neighbour": row["old_source_surface"],
                "component_recipe": row["new_recipe"],
                "portable_default_de": row["portable_default_de"],
                "scribe_rule": row["scribe_rule"],
                "example_page": row["page"],
                "example_locus": row["locus"],
                "teaching_instruction_de": {
                    "SHAPED_Y_WRAPPER": "Die umhüllte shy-Form als dieselbe POSTEN-Karte lesen.",
                    "LINE_FINAL_M_FOR_R": "Am Zeilenende den m-Ausgang dieser gelernten Karte wie den registrierten r-Ausgang lesen.",
                    "CHD_CHED_EXPANSION": "chd und ched als kurze und ausgezogene Form derselben UMSETZEN-Karte lesen.",
                    "SHORT_IIN_GRADE": "Eine verkürzte i-Folge verändert die gelernte STUFE-Karte nicht.",
                    "LONG_IIN_GRADE": "Eine verlängerte i-Folge verändert die gelernte STUFE-Karte nicht.",
                }[row["scribe_rule"]],
            }
        )
    write_tsv(HERE / "PASS1006_5_SCRIBE_ALLOGRAPH_RULES.tsv", allograph_rules)

    statement_for_event = statement_by_event
    new_compositions: list[dict[str, object]] = []
    for number, row in enumerate(
        [item for item in allograph_decisions if item["decision_class"] == "VISIBLE_COMPOSITION"], 1
    ):
        parts = row["new_recipe"].split("+")
        unknown = [part for part in parts if part not in root_names]
        if unknown:
            raise ValueError(f"new root in composition {row['surface']}: {unknown}")
        new_compositions.append(
            {
                "composition_id": f"N{number:02d}",
                "surface": row["surface"],
                "component_recipe": row["new_recipe"],
                "portable_default_de": row["portable_default_de"],
                "parts": len(parts),
                "example_page": row["page"],
                "example_locus": row["locus"],
                "statement_id": statement_for_event[row["event_id"]],
                "teaching_status": "ROOT_SUM_NOT_NEW_WORD",
            }
        )
    write_tsv(HERE / "PASS1006_29_NEW_COMPOSITION_APPENDIX.tsv", new_compositions)

    page_summaries: list[dict[str, object]] = []
    for page in PAGE_ORDER:
        page_events = [row for row in event_rows if row["physical_page"] == page]
        page_statements = [row for row in statements if row["physical_page"] == page]
        running_count = sum(row["event_role"] == "RUNNING_STATEMENT" for row in page_events)
        address_count = len(page_events) - running_count
        page_summaries.append(
            {
                "page_order": PAGE_INDEX[page] + 1,
                "physical_page": page,
                "register": REGISTER[page],
                "page_description_de": PAGE_DESCRIPTION[page],
                "total_groups": len(page_events),
                "running_groups": running_count,
                "address_or_label_groups": address_count,
                "statements": len(page_statements),
                "licensed_closes": sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in page_statements),
                "visible_boundary_or_open_ends": sum(
                    row["end_mode"] != "LICENSED_DY_CLOSE" for row in page_statements
                ),
                "cross_line_statements": sum(row["crosses_physical_line"] == "YES" for row in page_statements),
            }
        )
    write_tsv(HERE / "PASS1006_18_PAGE_SUMMARY.tsv", page_summaries)

    manual = """# Lehrlingshandbuch für die achtzehn Seiten

1. Zuerst den sichtbaren Besitzer merken: Pflanze, Gefässpartie, Beckenstation oder Ring.
2. Bildnahe Kennungen als lokale Namen kopieren; sie sind keine automatisch lesbaren Werkstattwörter.
3. Die längste bekannte Karte erkennen und danach ihre Wurzeln von links nach rechts sprechen.
4. Die 53 Wurzeln behalten überall denselben kurzen Kernwert; das Bild liefert erst die konkrete Sache.
5. Die 30 häufigen Ligaturen und 72 längeren Kompositionen sind Schreibkarten, aber keine zusätzlichen Bedeutungswörter.
6. Die 29 neuen Formen aus Pass 1005 ebenso als Wurzelsummen lesen; keine davon auswendig als neues Wort lernen.
7. Fünf Schreibervarianten lernen: umhülltes Y, line-finaler m/r-Ausgang, CHD/CHED und kurze/lange IIN-Stufe.
8. Nicht nach dem ähnlichsten Wort raten: Jeder sichtbare Teil muss Wurzel, lokale Kennung oder eine dieser fünf Varianten sein.
9. E, EE und EEE bleiben kurz, länger und voll; IIN bleibt eine Stufe und AIIN ein Maß.
10. Y trägt den aktuellen Posten. Es beendet keinen Satz.
11. Nur eine lizenzierte DY-Karte schließt einen Teilgang.
12. Eine physische Zeile ist Schreibraum, keine Satzgrenze.
13. Ein klarer Bild-, Gefäss-, Stations- oder Ringwechsel darf einen offenen Eintrag zurücksetzen.
14. Beim Vorlesen zuerst die Wurzelsumme, dann die lokale Bildfüllung nennen.

Die achtzehn Seiten besitzen 462 Lauftextaussagen. f69v und f70v sind reine lokale Himmelsregister und werden nicht zu künstlicher Prosa umgeschrieben.
"""
    (HERE / "PASS1006_APPRENTICE_MANUAL.md").write_text(manual, encoding="utf-8")

    addresses_by_locus: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in address_rows:
        addresses_by_locus[(str(row["physical_page"]), str(row["locus"]))].append(row)
    statement_by_page: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in statements:
        statement_by_page[str(row["physical_page"])].append(row)

    lines = [
        "# Achtzehn-Seiten-Werkstattausgabe",
        "",
        "Diese Ausgabe bindet 3.168 sichtbare Gruppen: 2.618 in 462 laufenden Aussagen und 550 als lokale Bild-, Gefäss-, Stations- oder Ringadressen.",
        "",
    ]
    summary_by_page = {row["physical_page"]: row for row in page_summaries}
    for page in PAGE_ORDER:
        summary = summary_by_page[page]
        lines.extend(
            [
                f"## {page} — {PAGE_DESCRIPTION[page]}",
                "",
                f"{summary['total_groups']} Gruppen: {summary['running_groups']} laufend, "
                f"{summary['address_or_label_groups']} lokal; {summary['statements']} Aussagen.",
                "",
            ]
        )
        for row in statement_by_page[page]:
            group_word = "Gruppe" if int(row["event_count"]) == 1 else "Gruppen"
            lines.append(
                f"- **{row['statement_id']}** ({row['locus_span']}; {row['event_count']} {group_word}): "
                f"{row['surface_sequence']} — {row['fluent_workshop_de']}"
            )
        page_address_loci = sorted(
            [key for key in addresses_by_locus if key[0] == page],
            key=lambda key: int(key[1].rsplit(".", 1)[1]),
        )
        if page_address_loci:
            lines.extend(["", "### Lokale Adressen und Etiketten", ""])
            for key in page_address_loci:
                rows = addresses_by_locus[key]
                surfaces = " ".join(str(row["surface"]) for row in rows)
                local_values = " ; ".join(dict.fromkeys(str(row["local_contextual_expansion_de"]) for row in rows))
                lines.append(f"- **{key[1]}**: {surfaces} — {local_values}")
        lines.append("")
    (HERE / "PASS1006_18_PAGE_READABLE_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    closed = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements)
    cross = sum(row["crosses_physical_line"] == "YES" for row in statements)
    report = (
        "# Pass 1006 — einheitliche Achtzehn-Seiten-Ausgabe\n\n"
        "Die bisher getrennten Textkörper sind jetzt ein Buch: 354 ältere Klauseln "
        "plus 108 Pass-1005-Aussagen ergeben 462 Aussagen über 2.618 laufende Gruppen. "
        "Weitere 550 Gruppen bleiben lokale Adressen oder Etiketten. Zusammen sind "
        "alle 3.168 Gruppen genau einmal gebunden.\n\n"
        f"{closed} Aussagen enden an einer lizenzierten Schlusskarte; "
        f"{len(statements) - closed} enden an einem sichtbaren Besitzer-/Diagrammrand "
        f"oder bleiben am Seitenende offen. {cross} Aussagen überschreiten mindestens "
        "eine physische Zeile. f69v und f70v bleiben reine Himmelsregister ohne "
        "erfundene Prosasätze.\n\n"
        "Das 175-zeilige Codebuch bleibt bytegleich. Die fünf tatsächlich benötigten "
        "Schreiberregeln stehen in einem eigenen Anhang. Die 29 neuen Formen sind "
        "ausdrücklich Wurzelsummen und keine neuen Wörter. Damit besitzt der Lehrling "
        "nun einen einzigen Arbeitsgang für alle achtzehn Seiten.\n\n"
        "Inhaltlich bleibt die beste kreative Lesung ein bebildertes Werkstattbuch: "
        "Pflanzen und Gefässe liefern Stoffbesitzer, die Biological-Seiten lokale "
        "Anwendungs-/Beckenstationen und die Himmelsseiten getrennte Auswahlregister.\n"
    )
    (HERE / "PASS1006_REPORT.md").write_text(report, encoding="utf-8")

    outputs = [
        "PASS1006_462_UNIFIED_STATEMENT_EDITION.tsv",
        "PASS1006_3168_UNIFIED_EVENT_LEDGER.tsv",
        "PASS1006_550_LOCAL_ADDRESS_LEDGER.tsv",
        "PASS1006_175_APPRENTICE_CODEBOOK.tsv",
        "PASS1006_5_SCRIBE_ALLOGRAPH_RULES.tsv",
        "PASS1006_29_NEW_COMPOSITION_APPENDIX.tsv",
        "PASS1006_18_PAGE_SUMMARY.tsv",
        "PASS1006_APPRENTICE_MANUAL.md",
        "PASS1006_18_PAGE_READABLE_EDITION.md",
        "PASS1006_REPORT.md",
    ]
    summary = {
        "status": "PASS",
        "decision": "EIGHTEEN_PAGE_UNIFIED_WORKSHOP_EDITION_COMPLETE",
        "pages": len(PAGE_ORDER),
        "groups": len(event_rows),
        "running_groups": len(statement_by_event),
        "local_address_or_label_groups": len(address_rows),
        "statements": len(statements),
        "old_statements": len(old_clauses),
        "new_statements": len(new_statements),
        "licensed_closes": closed,
        "visible_boundary_or_open_ends": len(statements) - closed,
        "cross_line_statements": cross,
        "codebook_lines": len(read_tsv(CODEBOOK_PATH)),
        "scribe_allograph_rules": len(allograph_rules),
        "new_root_sum_compositions": len(new_compositions),
        "new_portable_roots": 0,
        "source_hashes": {
            "pass1002_events": sha(OLD_EVENTS_PATH),
            "pass1002_clauses": sha(OLD_CLAUSES_PATH),
            "pass1002_codebook": sha(CODEBOOK_PATH),
            "pass1005_events": sha(NEW_EVENTS_PATH),
            "pass1005_statements": sha(NEW_STATEMENTS_PATH),
            "pass1005_combined": sha(NEW_COMBINED_PATH),
            "pass1005_allographs": sha(ALLOGRAPH_PATH),
            "pass996_roots": sha(ROOT_SOURCE),
        },
        "output_hashes": {name: sha(HERE / name) for name in outputs},
    }
    (HERE / "PASS1006_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
