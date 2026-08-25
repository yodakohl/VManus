#!/usr/bin/env python3
"""Build Pass 1005: reconcile allographs, open tails, and fluent statements."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P1004 = ROOT / "experiments/yolo/sidequest_semantic_fresh_page_continuous_edition_one_thousand_fourth"
SOURCE_EVENTS = P1004 / "PASS1004_657_REVISED_EVENT_INTERLINEAR.tsv"
SOURCE_COMBINED = P1004 / "PASS1004_3168_COMBINED_EVENT_INTERLINEAR.tsv"
ROOT_SOURCE = (
    ROOT
    / "experiments/yolo/sidequest_semantic_canonical_scribe_workshop_sixth_edition_nine_hundred_ninety_sixth"
    / "PASS996_53_PORTABLE_ROOTS.tsv"
)

PAGE_ORDER = {"f17r": 0, "f77r": 1, "f88v": 2, "f71v": 3}
PAGE_TITLES = {
    "f17r": "Pflanzenartikel",
    "f77r": "Becken- und Stationsartikel",
    "f88v": "Gefäss- und Zutatenartikel",
    "f71v": "Ring- und Himmelsregister",
}
CONTEXT_FIELD = {
    "MATERIAL": "material_workshop_expansion_de",
    "STATION": "station_workshop_expansion_de",
    "CELESTIAL": "celestial_relational_expansion_de",
}

# Twenty-nine old nearest-neighbour readings are replaced by visible root
# compositions. Five genuinely useful scribe/allograph conventions remain.
DIRECT_RECIPES = {
    "P1003-E0004": "HO+LOCAL_CHAR_G",
    "P1003-E0009": "D_ADDR+O+DY",
    "P1003-E0019": "O+D_ADDR+S",
    "P1003-E0033": "S+O+M_LOCAL",
    "P1003-E0045": "T+SH+O",
    "P1003-E0050": "K+SH+E+O",
    "P1003-E0058": "S+AR",
    "P1003-E0060": "S+O+Y",
    "P1003-E0061": "CKH+O",
    "P1003-E0063": "DA+S",
    "P1003-E0070": "M_LOCAL+OL",
    "P1003-E0072": "CTH+AR",
    "P1003-E0076": "Y+CH+O+D_ADDR",
    "P1003-E0078": "CH+OT+O+M_LOCAL",
    "P1003-E0227": "CPH+E+Y",
    "P1003-E0235": "SH+E+D_ADDR+AR",
    "P1003-E0238": "D_ADDR+AR+OR",
    "P1003-E0254": "OL+CH+EE+DY",
    "P1003-E0256": "L+O+M_LOCAL",
    "P1003-E0279": "AL+OR",
    "P1003-E0307": "AL+Y",
    "P1003-E0354": "CH+L",
    "P1003-E0374": "CARRIER_Q+E+P+CHD+Y",
    "P1003-E0467": "Y+LOCAL_CHAR_F+OL+AIIN",
    "P1003-E0469": "Y+SH+E+O+D_ADDR",
    "P1003-E0492": "S+OT+E+OL",
    "P1003-E0515": "K+OR+AIN",
    "P1003-E0533": "DA+IIN+M_LOCAL+D_ADDR",
    "P1003-E0620": "OT+O",
}

LICENSED_ALLOGRAPHS = {
    "P1003-E0013": ("OK+Y", "SHAPED_Y_WRAPPER", "shy is the learned wrapped form of the current-item card"),
    "P1003-E0035": ("Y+P+AIR", "LINE_FINAL_M_FOR_R", "line-final m carries the registered AIR-tail used by ypair"),
    "P1003-E0197": ("AL+CHD+DY", "CHD_CHED_EXPANSION", "chd and ched are the learned short and expanded shapes of CHD"),
    "P1003-E0210": ("O+IIN", "SHORT_IIN_GRADE", "the grade stroke count contracts locally without changing IIN"),
    "P1003-E0289": ("O+IIN", "LONG_IIN_GRADE", "the grade stroke count expands locally without changing IIN"),
}

TAIL_MODES = {
    ("P1003-E0056", "P1003-E0078"): (
        "TRUE_OPEN_ARTICLE_END",
        "Der Pflanzenartikel endet nach einer Fortsetzungsform ohne Schlusskarte; kein Folgesatz wird erfunden.",
    ),
    ("P1003-E0372", "P1003-E0409"): (
        "OWNER_RESET_TO_LOWER_STATION_LABELS",
        "Der lange Prosalauf endet vor dem unteren Beschriftungsfeld; der sichtbare Besitzerwechsel setzt den Text zurück.",
    ),
    ("P1003-E0439", "P1003-E0457"): (
        "OWNER_RESET_TO_BATCH_B",
        "Die erste Gefässpartie endet vor den Kennungen der zweiten Partie; der Chargenwechsel setzt den Text zurück.",
    ),
    ("P1003-E0550", "P1003-E0553"): (
        "OWNER_RESET_TO_LABEL_ONLY_BATCH_C",
        "Die zweite Gefässpartie endet vor der nur beschrifteten dritten Partie; der Besitzerwechsel ersetzt eine Schlusskarte.",
    ),
    ("P1003-E0577", "P1003-E0594"): (
        "RING_NAMESPACE_RESET_A_TO_B",
        "Der erste Ringlauf endet an seiner Bildgrenze; der zweite Ring beginnt einen eigenen Namensraum.",
    ),
    ("P1003-E0638", "P1003-E0640"): (
        "RING_NAMESPACE_RESET_B_TO_C",
        "Der zweite Ringlauf endet an seiner Bildgrenze; der dritte Ring beginnt einen eigenen Namensraum.",
    ),
    ("P1003-E0647", "P1003-E0657"): (
        "TRUE_OPEN_FINAL_RING",
        "Der letzte Ringlauf endet offen am Seitenrand; eine unsichtbare Schlusskarte wird nicht ergänzt.",
    ),
}

ROOT_PHRASES = {
    "Y": "diesen Posten",
    "OK": "ansetzen",
    "E": "kurz",
    "DY": "den Teilgang schließen",
    "O": "ausführen",
    "OL": "damit fortfahren",
    "EE": "länger",
    "OT": "danach",
    "AL": "zur Zielstelle",
    "CH": "entnehmen",
    "D_ADDR": "vom bezeichneten Teil",
    "SH": "halten",
    "AR": "aus der Quelle",
    "K": "zugeben",
    "AIIN": "nach Maß",
    "S": "auswählen",
    "CHD": "umsetzen",
    "OR": "den Ansatz",
    "L": "weiterleiten",
    "T": "einstellen",
    "AIN": "eine Portion",
    "R": "merken",
    "P": "einsetzen",
    "CTH": "bis bereit",
    "SHED": "absetzen lassen",
    "CKH": "durch den Durchlass",
    "AM_ADDR": "im Inneren",
    "CHEO": "den Auszug",
    "DA": "als zweiten Gang",
    "CARRIER_Q": "einen neuen Gang beginnen",
    "A_ADDR": "am bezeichneten Ort",
    "AIR": "durch den Lauf",
    "CHK": "behandeln",
    "IIN": "auf die Stufe",
    "S_ADDR": "am Sonderort",
    "SOLK": "auffangen",
    "EEE": "vollständig",
    "LSH": "spülen",
    "LOCAL_CHAR_F": "über den Nebenweg",
    "CPH": "umleiten",
    "HO": "einen Teilstoff",
    "AN": "einen Zusatz",
    "G_LABEL": "prüfen",
    "CFH": "trennen",
    "LOCAL_CHAR_G": "einmal",
    "LOCAL_CHAR_I": "auf die Unterstufe",
    "OS": "dazugeben",
    "D_LABEL": "am Rand",
    "LOCAL_CHAR_B": "paarweise",
    "M_LOCAL": "in der Mitte",
    "LD": "befestigen",
    "LOCAL_CHAR_J": "verbinden",
    "RESUME_CARD": "wiederholen",
}

SPECIAL_CARDS = {
    "Y": "diesen Posten weiterführen",
    "OL": "mit demselben Ansatz fortfahren",
    "AIIN": "nach dem vorgeschriebenen Maß arbeiten",
    "AIN": "eine Portion nehmen",
    "AL": "an die bezeichnete Zielstelle gehen",
    "AR": "aus der bezeichneten Quelle nehmen",
    "OK+AIIN": "den Posten nach Maß ansetzen",
    "OK+AIN": "eine Portion ansetzen",
    "CHD+Y": "diesen Posten umsetzen",
    "SHED+DY": "absetzen lassen",
    "OK+E+DY": "kurz ansetzen",
    "OK+EE+DY": "länger ansetzen",
    "OT+E+DY": "danach kurz halten",
    "OT+EE+DY": "danach länger halten",
    "L+CHD+DY": "weiter umsetzen",
    "O+DY": "ausführen",
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


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def card_phrase(recipe: str) -> str:
    if recipe in SPECIAL_CARDS:
        return SPECIAL_CARDS[recipe]
    parts = recipe.split("+")
    words = [ROOT_PHRASES[part] for part in parts]
    if parts[-1] == "DY":
        body = " ".join(words[:-1]).strip()
        return body if body else "den laufenden Gang"
    return " ".join(words)


def main() -> int:
    roots = read_tsv(ROOT_SOURCE)
    root_by_component = {row["recognition_form"]: row for row in roots}
    atomic = {key: row["atomic_meaning_de"] for key, row in root_by_component.items()}

    def root_default(recipe: str) -> str:
        return " · ".join(atomic[part] for part in recipe.split("+"))

    def local_expansion(row: dict[str, str]) -> str:
        values = [
            root_by_component[part][CONTEXT_FIELD[row["register"]]]
            for part in row["component_recipe"].split("+")
        ]
        prefix = {"MATERIAL": "am Stoffbild", "STATION": "an der Station", "CELESTIAL": "im Ring"}[
            row["register"]
        ]
        return f"{prefix} {row['visible_owner_de']}: " + " · ".join(values)

    source = read_tsv(SOURCE_EVENTS)
    revised: list[dict[str, str]] = []
    decisions: list[dict[str, object]] = []
    for original in source:
        row = dict(original)
        event_id = row["fresh_event_id"]
        if event_id in DIRECT_RECIPES:
            old_recipe = row["component_recipe"]
            row["component_recipe"] = DIRECT_RECIPES[event_id]
            row["portable_default_de"] = root_default(row["component_recipe"])
            row["local_contextual_expansion_de"] = local_expansion(row)
            row["transfer_class"] = "VISIBLE_ROOT_COMPOSITION_RECONCILED"
            row["source_surface"] = row["surface"]
            row["edit_distance"] = "0"
            row["confidence"] = "MEDIUM_HIGH"
            row["note"] = "Vollständig sichtbare Komposition; die frühere nächste Form wird nicht mehr gebraucht."
            decisions.append(
                {
                    "event_id": event_id,
                    "page": row["physical_page"],
                    "locus": row["locus"],
                    "surface": row["surface"],
                    "old_source_surface": original["source_surface"],
                    "old_recipe": old_recipe,
                    "new_recipe": row["component_recipe"],
                    "portable_default_de": row["portable_default_de"],
                    "decision_class": "VISIBLE_COMPOSITION",
                    "scribe_rule": "NONE_NEEDED",
                }
            )
        elif event_id in LICENSED_ALLOGRAPHS:
            old_recipe = row["component_recipe"]
            recipe, rule, explanation = LICENSED_ALLOGRAPHS[event_id]
            row["component_recipe"] = recipe
            row["portable_default_de"] = root_default(recipe)
            row["local_contextual_expansion_de"] = local_expansion(row)
            row["transfer_class"] = "LICENSED_SCRIBAL_ALLOGRAPH"
            row["confidence"] = "MEDIUM_HIGH"
            row["note"] = explanation
            decisions.append(
                {
                    "event_id": event_id,
                    "page": row["physical_page"],
                    "locus": row["locus"],
                    "surface": row["surface"],
                    "old_source_surface": original["source_surface"],
                    "old_recipe": old_recipe,
                    "new_recipe": recipe,
                    "portable_default_de": row["portable_default_de"],
                    "decision_class": "LICENSED_ALLOGRAPH",
                    "scribe_rule": rule,
                }
            )
        revised.append(row)

    if len(decisions) != 34:
        raise ValueError(f"expected 34 decisions, got {len(decisions)}")
    if any(row["transfer_class"] == "NEAR_REGISTERED_ALLOGRAPH" for row in revised):
        raise ValueError("unreconciled nearest allograph remains")
    write_tsv(HERE / "PASS1005_34_ALLOGRAPH_DECISIONS.tsv", decisions)
    write_tsv(HERE / "PASS1005_657_CONSOLIDATED_EVENT_INTERLINEAR.tsv", revised, list(source[0]))

    by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in revised:
        by_surface[row["surface"]].append(row)
    surface_rows: list[dict[str, object]] = []
    for surface in sorted(by_surface):
        rows = by_surface[surface]
        content = [row for row in rows if row["component_recipe"] != "LOCAL_ADDRESS"]
        representative = content[0] if content else rows[0]
        if content and len({row["component_recipe"] for row in content}) != 1:
            raise ValueError(f"surface collision remains for {surface}")
        surface_rows.append(
            {
                "surface": surface,
                "events": len(rows),
                "pages": "|".join(sorted({row["physical_page"] for row in rows}, key=PAGE_ORDER.get)),
                "kinds": "|".join(sorted({row["kind"] for row in rows})),
                "component_recipe": representative["component_recipe"],
                "portable_default_de": representative["portable_default_de"],
                "reading_class": representative["transfer_class"],
                "source_surface": representative["source_surface"],
                "owner_bound_label_use": "YES" if any(row["kind"] == "L" for row in rows) else "NO",
                "confidence": representative["confidence"],
            }
        )
    write_tsv(HERE / "PASS1005_393_CONSOLIDATED_SURFACE_DICTIONARY.tsv", surface_rows)

    running = [row for row in revised if row["kind"] != "L"]
    raw_statements: list[list[dict[str, str]]] = []
    current: list[dict[str, str]] = []
    for row in running:
        if current and (row["physical_page"], row["owner_id"]) != (
            current[-1]["physical_page"],
            current[-1]["owner_id"],
        ):
            raw_statements.append(current)
            current = []
        current.append(row)
        if row["component_recipe"].split("+")[-1] == "DY":
            raw_statements.append(current)
            current = []
    if current:
        raw_statements.append(current)

    statements: list[dict[str, object]] = []
    tails: list[dict[str, object]] = []
    serial: Counter[str] = Counter()
    for rows in raw_statements:
        page = rows[0]["physical_page"]
        serial[page] += 1
        loci: list[str] = []
        for row in rows:
            if not loci or loci[-1] != row["locus"]:
                loci.append(row["locus"])
        range_key = (rows[0]["fresh_event_id"], rows[-1]["fresh_event_id"])
        if rows[-1]["component_recipe"].split("+")[-1] == "DY":
            end_mode = "LICENSED_DY_CLOSE"
            boundary = "Dann den Teilgang schließen."
        else:
            if range_key not in TAIL_MODES:
                raise ValueError(f"unclassified open range {range_key}")
            end_mode, boundary = TAIL_MODES[range_key]
        intro = {
            ("f17r", "MATERIAL"): "Bei der abgebildeten Pflanze",
            ("f77r", "STATION"): "An der bezeichneten Körper-/Beckenstation",
            ("f88v", "MATERIAL"): "In dieser Gefäss- und Zutatenpartie",
            ("f71v", "CELESTIAL"): "In diesem Ringabschnitt",
        }[(page, rows[0]["register"])]
        fluent = intro + ": " + "; ".join(card_phrase(row["component_recipe"]) for row in rows) + ". " + boundary
        statement_id = f"P1005-{page.upper()}-S{serial[page]:03d}"
        statements.append(
            {
                "statement_id": statement_id,
                "physical_page": page,
                "register": rows[0]["register"],
                "owner_id": rows[0]["owner_id"],
                "visible_owner_de": rows[0]["visible_owner_de"],
                "first_locus": loci[0],
                "last_locus": loci[-1],
                "locus_count": len(loci),
                "crosses_physical_line": "YES" if len(loci) > 1 else "NO",
                "groups": len(rows),
                "first_event_id": rows[0]["fresh_event_id"],
                "last_event_id": rows[-1]["fresh_event_id"],
                "end_mode": end_mode,
                "boundary_reading_de": boundary,
                "surface_sequence": " ".join(row["surface"] for row in rows),
                "component_sequence": " | ".join(row["component_recipe"] for row in rows),
                "literal_workshop_de": " ; ".join(row["portable_default_de"] for row in rows),
                "fluent_workshop_de": fluent,
            }
        )
        if end_mode != "LICENSED_DY_CLOSE":
            tails.append(
                {
                    "statement_id": statement_id,
                    "physical_page": page,
                    "owner_id": rows[0]["owner_id"],
                    "first_locus": loci[0],
                    "last_locus": loci[-1],
                    "first_event_id": rows[0]["fresh_event_id"],
                    "last_event_id": rows[-1]["fresh_event_id"],
                    "surface_tail": " ".join(row["surface"] for row in rows[-6:]),
                    "tail_mode": end_mode,
                    "reading_de": boundary,
                    "invented_close": "NO",
                }
            )
    write_tsv(HERE / "PASS1005_108_CONSOLIDATED_STATEMENTS.tsv", statements)
    write_tsv(HERE / "PASS1005_7_OPEN_TAIL_DECISIONS.tsv", tails)

    by_locus: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in revised:
        by_locus[(row["physical_page"], row["locus"])].append(row)
    locus_rows: list[dict[str, object]] = []
    for (page, locus), rows in sorted(
        by_locus.items(), key=lambda item: (PAGE_ORDER[item[0][0]], locus_number(item[0][1]))
    ):
        rows.sort(key=lambda row: int(row["group_index"]))
        locus_rows.append(
            {
                "physical_page": page,
                "locus": locus,
                "kind": rows[0]["kind"],
                "owner_id": rows[0]["owner_id"],
                "visible_owner_de": rows[0]["visible_owner_de"],
                "surface_sequence": " ".join(row["surface"] for row in rows),
                "component_sequence": " | ".join(row["component_recipe"] for row in rows),
                "portable_reading_de": " ; ".join(row["portable_default_de"] for row in rows),
                "groups": len(rows),
            }
        )
    write_tsv(HERE / "PASS1005_111_CONSOLIDATED_LOCUS_READINGS.tsv", locus_rows)

    combined_source = read_tsv(SOURCE_COMBINED)
    combined = [row for row in combined_source if row["edition_source"] != "PASS1004_FRESH_CONTINUOUS"]
    for row in revised:
        combined.append(
            {
                "event_id": row["fresh_event_id"],
                "physical_page": row["physical_page"],
                "locus": row["locus"],
                "kind": row["kind"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "portable_default_de": row["portable_default_de"],
                "local_contextual_expansion_de": row["local_contextual_expansion_de"],
                "edition_source": "PASS1005_ALLOGRAPH_TAIL_CONSOLIDATION",
            }
        )
    write_tsv(HERE / "PASS1005_3168_COMBINED_EVENT_INTERLINEAR.tsv", combined, list(combined_source[0]))

    page_intro = {
        "f17r": "Die Pflanze bleibt der stille Gegenstand. Der Text wechselt zwischen Teil, Quelle, Ansatz, Lauf, Maß und Behandlung; sein letzter Gang bleibt sichtbar offen.",
        "f77r": "Die Seite besteht aus vielen kurzen Stationszellen und einem langen Schlusslauf. Die untere Beschriftungsgruppe setzt diesen Schlusslauf zurück.",
        "f88v": "Die Seite hat getrennte Gefäss-/Zutatenpartien. Ihre Besitzerwechsel beenden zwei Läufe auch ohne Schlusskarte.",
        "f71v": "Jeder Ring ist ein eigener Namensraum. Ringgrenzen, nicht erfundene Satzzeichen, beenden die Eintragsläufe.",
    }
    lines = [
        "# Pass 1005 — konsolidierte Vierseiten-Ausgabe",
        "",
        "Alle 34 früheren Nahformen sind entschieden: 29 sind sichtbare Kompositionen, fünf bleiben gelernte Schreiberformen. Zwei vermeintliche Schlusskarten lösen sich als offene Y- bzw. S-Karten auf; deshalb entstehen 108 statt 110 Aussagen.",
        "",
    ]
    for page in PAGE_ORDER:
        lines.extend([f"## {page} — {PAGE_TITLES[page]}", "", page_intro[page], ""])
        for row in (item for item in statements if item["physical_page"] == page):
            group_word = "Gruppe" if int(row["groups"]) == 1 else "Gruppen"
            lines.append(
                f"- **{row['statement_id']}** ({row['first_locus']}→{row['last_locus']}, "
                f"{row['groups']} {group_word}): {row['surface_sequence']} — {row['fluent_workshop_de']}"
            )
        lines.append("")
    (HERE / "PASS1005_FOUR_PAGE_FLUENT_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    class_counts = Counter(row["decision_class"] for row in decisions)
    page_counts = Counter(row["physical_page"] for row in statements)
    close_count = sum(row["end_mode"] == "LICENSED_DY_CLOSE" for row in statements)
    cross_count = sum(row["crosses_physical_line"] == "YES" for row in statements)
    report = (
        "# Pass 1005 — Nahformen und offene Enden konsolidiert\n\n"
        "Die 34 bisherigen Ein-Zeichen-Nahformen sind jetzt entschieden. "
        f"{class_counts['VISIBLE_COMPOSITION']} lesen sich direkt als längere Kombinationen "
        "bereits bekannter Wurzeln. Fünf bleiben einfache Werkstattschreibungen: "
        "die umhüllte Y-Form, line-finales m für einen r-Ausgang, die kurze/lange "
        "IIN-Stufe und die CHD/CHED-Erweiterung. Keine Nahform bleibt unentschieden.\n\n"
        "Zwei wichtige alte Schlüsse fallen weg: ods enthält sichtbar O+D+S statt O+DY, "
        "und cphey enthält CPH+E+Y statt CPH+E+DY. Dadurch verbinden sich je zwei "
        "alte Abschnitte. Die 608 laufenden Gruppen ergeben nun "
        f"{len(statements)} Aussagen: {close_count} mit Schlusskarte und sieben mit "
        f"explizitem Bild-/Besitzerende; {cross_count} Aussagen überschreiten Zeilen.\n\n"
        "Die sieben offenen Enden sind nicht mehr pauschal offen: fünf enden an "
        "sichtbaren Besitzer- oder Ringwechseln und zwei bleiben echte Seitenenden. "
        "Nirgends wird eine unsichtbare "
        "Schlusskarte ergänzt.\n\n"
        f"Seitenbilanz: f17r {page_counts['f17r']}, f77r {page_counts['f77r']}, "
        f"f88v {page_counts['f88v']}, f71v {page_counts['f71v']} Aussagen. "
        "Die vollständige flüssige Ausgabe hält denselben Stammwert überall fest; "
        "Bildbesitzer liefern weiterhin nur den lokalen Gegenstand.\n"
    )
    (HERE / "PASS1005_REPORT.md").write_text(report, encoding="utf-8")

    outputs = [
        "PASS1005_34_ALLOGRAPH_DECISIONS.tsv",
        "PASS1005_657_CONSOLIDATED_EVENT_INTERLINEAR.tsv",
        "PASS1005_393_CONSOLIDATED_SURFACE_DICTIONARY.tsv",
        "PASS1005_108_CONSOLIDATED_STATEMENTS.tsv",
        "PASS1005_7_OPEN_TAIL_DECISIONS.tsv",
        "PASS1005_111_CONSOLIDATED_LOCUS_READINGS.tsv",
        "PASS1005_3168_COMBINED_EVENT_INTERLINEAR.tsv",
        "PASS1005_FOUR_PAGE_FLUENT_EDITION.md",
        "PASS1005_REPORT.md",
    ]
    summary = {
        "status": "PASS",
        "decision": "ALL_NEAR_FORMS_AND_OPEN_TAILS_CONSOLIDATED",
        "fresh_pages": 4,
        "fresh_groups": len(revised),
        "running_groups": len(running),
        "labels": len(revised) - len(running),
        "unique_surfaces": len(surface_rows),
        "allograph_decisions": len(decisions),
        "visible_compositions": class_counts["VISIBLE_COMPOSITION"],
        "licensed_scribal_allographs": class_counts["LICENSED_ALLOGRAPH"],
        "nearest_allographs_remaining": 0,
        "statements": len(statements),
        "licensed_closes": close_count,
        "explicit_open_or_owner_ends": len(tails),
        "cross_line_statements": cross_count,
        "page_statement_counts": dict(page_counts),
        "combined_groups": len(combined),
        "combined_pages": len({row["physical_page"] for row in combined}),
        "new_portable_roots": 0,
        "source_hashes": {
            "pass1004_events": sha(SOURCE_EVENTS),
            "pass1004_combined": sha(SOURCE_COMBINED),
            "pass996_roots": sha(ROOT_SOURCE),
        },
        "output_hashes": {name: sha(HERE / name) for name in outputs},
    }
    (HERE / "PASS1005_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
