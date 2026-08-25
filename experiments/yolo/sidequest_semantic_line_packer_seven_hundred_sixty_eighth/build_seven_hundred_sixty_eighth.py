#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
V78 = ROOT / "experiments/yolo/sidequest_theory_candidates_v78/V78_SELECTED_381_EVENT_INTERLINEAR.tsv"
V79 = ROOT / "experiments/yolo/sidequest_theory_candidates_v79/V79_SELECTED_19_LINE_TRANSITION_AUDIT.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    clean = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    continuity = read(V78)
    transitions = read(V79)
    clean_by_event = {row["event_id"]: row for row in clean}
    locus_surfaces: dict[str, list[str]] = defaultdict(list)
    locus_page: dict[str, str] = {}
    for row in continuity:
        locus_surfaces[row["locus"]].append(clean_by_event[row["event_id"]]["surface"])
        locus_page[row["locus"]] = row["page"]
    locus_width = {locus: sum(len(surface) for surface in surfaces) + max(0, len(surfaces) - 1) for locus, surfaces in locus_surfaces.items()}
    page_capacity: dict[str, int] = defaultdict(int)
    for locus, width in locus_width.items():
        page_capacity[locus_page[locus]] = max(page_capacity[locus_page[locus]], width)

    audit = []
    for row in transitions:
        left_surface = clean_by_event[row["line_final_event"]]["surface"]
        right_surface = clean_by_event[row["line_initial_event"]]["surface"]
        current_width = locus_width[row["from_locus"]]
        projected = current_width + 1 + len(right_surface)
        capacity = page_capacity[row["page"]]
        space_fits = projected <= capacity
        observed_copy = row["frozen_v78_gold"] == "ANTICIPATORY_MARGIN_COPY"
        audit.append({
            "transition_id": row["transition_id"],
            "page": row["page"],
            "statement_id": row["statement_id"],
            "from_locus": row["from_locus"],
            "to_locus": row["to_locus"],
            "left_event": row["line_final_event"],
            "right_event": row["line_initial_event"],
            "left_surface": left_surface,
            "right_surface": right_surface,
            "left_line_char_width": current_width,
            "page_observed_max_char_width": capacity,
            "right_card_char_width": len(right_surface),
            "projected_if_anticipated": projected,
            "space_proxy_fits": "YES" if space_fits else "NO",
            "same_exact_card": row["same_exact_card"],
            "same_visible_owner": row["same_visible_owner"],
            "no_close_between": row["no_close_between"],
            "observed_edge_copy": "YES" if observed_copy else "NO",
            "generic_space_rule": "COPY" if space_fits else "NO_COPY",
            "full_identity_guard": "COPY" if space_fits and row["same_exact_card"] == "YES" and row["same_visible_owner"] == "YES" and row["no_close_between"] == "YES" else "NO_COPY",
        })
    write(
        "SEVEN_HUNDRED_SIXTY_EIGHTH_19_LINE_PACKER_AUDIT.tsv",
        audit,
        ["transition_id", "page", "statement_id", "from_locus", "to_locus", "left_event", "right_event", "left_surface", "right_surface", "left_line_char_width", "page_observed_max_char_width", "right_card_char_width", "projected_if_anticipated", "space_proxy_fits", "same_exact_card", "same_visible_owner", "no_close_between", "observed_edge_copy", "generic_space_rule", "full_identity_guard"],
    )

    line_rows = []
    used_loci = {row["from_locus"] for row in transitions} | {row["to_locus"] for row in transitions}
    for locus in sorted(used_loci):
        line_rows.append({
            "page": locus_page[locus],
            "locus": locus,
            "cards": len(locus_surfaces[locus]),
            "surface_sequence": " ".join(locus_surfaces[locus]),
            "char_width_proxy": locus_width[locus],
            "page_observed_max_char_width": page_capacity[locus_page[locus]],
        })
    write(
        "SEVEN_HUNDRED_SIXTY_EIGHTH_TRANSITION_LINE_WIDTHS.tsv",
        line_rows,
        ["page", "locus", "cards", "surface_sequence", "char_width_proxy", "page_observed_max_char_width"],
    )

    def score(rule_id: str, predicate) -> dict[str, object]:
        predicted = [row for row in audit if predicate(row)]
        tp = sum(row["observed_edge_copy"] == "YES" for row in predicted)
        fp = len(predicted) - tp
        fn = sum(row["observed_edge_copy"] == "YES" and row not in predicted for row in audit)
        return {"rule_id": rule_id, "predicted_copies": len(predicted), "tp": tp, "fp": fp, "fn": fn}

    models = [
        score("R1_SPACE_PROXY_ONLY", lambda r: r["space_proxy_fits"] == "YES"),
        score("R2_SPACE_OWNER_NO_CLOSE", lambda r: r["space_proxy_fits"] == "YES" and r["same_visible_owner"] == "YES" and r["no_close_between"] == "YES"),
        score("R3_SAME_EXACT_CARD_ONLY", lambda r: r["same_exact_card"] == "YES"),
        score("R4_SPACE_PLUS_FULL_IDENTITY_GUARD", lambda r: r["full_identity_guard"] == "COPY"),
        score("R5_LOCAL_MASTER_LICENSE", lambda r: r["transition_id"] == "LT06"),
    ]
    interpretations = {
        "R1_SPACE_PROXY_ONLY": "Platz reicht an neun Grenzen; acht falsche Randkopien.",
        "R2_SPACE_OWNER_NO_CLOSE": "Besitzer und offener Satz reduzieren, lassen aber sechs falsche Kopien.",
        "R3_SAME_EXACT_CARD_ONLY": "Beschreibt die sichtbare Doppelung, kann sie aber aus einer einzelnen Quellkarte nicht vorhersagen.",
        "R4_SPACE_PLUS_FULL_IDENTITY_GUARD": "Liest die fertige Seite korrekt, ist als Vorwaertsregel zirkulaer.",
        "R5_LOCAL_MASTER_LICENSE": "Kleine nichtallgemeine Layoutanweisung; beste ehrliche Vorwaertsregel.",
    }
    for row in models:
        row["interpretation"] = interpretations[str(row["rule_id"])]
    write("SEVEN_HUNDRED_SIXTY_EIGHTH_5_PACKER_RULES.tsv", models, ["rule_id", "predicted_copies", "tp", "fp", "fn", "interpretation"])

    license_rows = [{
        "license_id": "L_EDGE_01",
        "role": "BIO_STATION_SCRIBE",
        "page": "f82r",
        "from_locus": "f82r.3",
        "to_locus": "f82r.4",
        "source_event": "E181",
        "rendered_edge_copy": "E180",
        "instruction_de": "Wenn du am Ende von f82r.3 den fuer f82r.4 bestimmten qokaiin-Posten erreichst, setze ihn einmal an den Rand und am Anfang der Folgezeile nochmals; lies ihn nur einmal.",
        "generalize": "NO",
    }]
    write(
        "SEVEN_HUNDRED_SIXTY_EIGHTH_LOCAL_LAYOUT_LICENSE.tsv",
        license_rows,
        ["license_id", "role", "page", "from_locus", "to_locus", "source_event", "rendered_edge_copy", "instruction_de", "generalize"],
    )

    report = """# Pass 768 — Der Zeilenpacker

Wir haben fuer alle19 aussageninternen physischen Zeilenwechsel eine grobe Schreibbreite aus sichtbaren Oberflaechen und Leerraeumen berechnet. Das ist kein Pixelmass, aber genug fuer die Werkstattfrage: Haette die erste Karte der naechsten Zeile noch auf die vorige gepasst?

Bei neun der19 Grenzen lautet die Antwort ja. Platz allein wuerde also neben `E180/E181` acht falsche Randkopien erzeugen. Mit gleichem Besitzer und fehlendem Schluss bleiben immer noch sieben Kandidaten. Erst die bereits sichtbare identische Karte isoliert den echten Fall—doch das ist fuer einen Vorwaertsschreiber zirkulaer, weil er die zweite Kopie erst erzeugen soll.

Die ehrliche Schreibregel bleibt deshalb lokal: Der Bio-Schreiber lernt genau einen Modellblatt-Hinweis fuer f82r.3→f82r.4. Er setzt die fuer die Folgezeile bestimmte Karte vorweg an den Rand und liest beide Formen als einen Posten. Daraus wird keine allgemeine Kustoden- oder Catchwordregel gemacht.

Als naechstes kommt dieser eine Bio-Sondergriff als eigene kurze Lektion in den Lehrplan. Danach pruefen wir die Rollenbelastung erneut und versuchen, andere lokale Ausnahmen durch Seitenspezialisierung statt durch immer mehr allgemeine Regeln zu tragen.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "line_transitions": len(audit),
        "space_proxy_candidates": sum(row["space_proxy_fits"] == "YES" for row in audit),
        "space_owner_no_close_candidates": sum(row["space_proxy_fits"] == "YES" and row["same_visible_owner"] == "YES" and row["no_close_between"] == "YES" for row in audit),
        "observed_edge_copies": sum(row["observed_edge_copy"] == "YES" for row in audit),
        "local_layout_licenses": len(license_rows),
        "decision": "SPACE_INSUFFICIENT_TO_SELECT_EDGE_COPY__KEEP_ONE_LOCAL_MASTER_LAYOUT_LICENSE",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
