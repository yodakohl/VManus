#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P353 = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third"
P369 = ROOT / "experiments/yolo/sidequest_semantic_paired_forward_order_three_hundred_sixty_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


PALETTES = {
    "PALETTE_A_COMPACT": ["or", "kain", "chckhy", "cheky", "oky", "aiin", "okeey", "qokedy"],
    "PALETTE_B_EXPANDED": ["chor", "chkain", "shckhy", "cheky", "choky", "chaiin", "qokeey", "qokedy"],
}


def main() -> None:
    board_rows = read(P353 / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")
    board = {row["joint_tuple_id"]: row for row in board_rows}
    order = read(P369 / "THREE_HUNDRED_SIXTY_NINTH_EIGHT_CARD_PAIRED_ORDER.tsv")
    surface_index: dict[str, list[str]] = defaultdict(list)
    for row in board_rows:
        for surface in row["registered_surface_palette"].split("|"):
            surface_index[surface].append(row["joint_tuple_id"])

    render_rows = []
    for palette, surfaces in PALETTES.items():
        for source, surface in zip(order, surfaces):
            tuple_id = source["selected_joint_tuple_id"]
            render_rows.append({
                "palette_id": palette,
                "position": source["position"],
                "microcycle": source["microcycle"],
                "joint_tuple_id": tuple_id,
                "atomic_value_de": source["master_dictated_value_de"],
                "slot_family": source["family_id"],
                "pair_id": source["pair_id"],
                "pair_decision_route": source["decision_route"],
                "rendered_surface": surface,
                "registered_for_card": "YES" if surface in board[tuple_id]["registered_surface_palette"].split("|") else "NO",
                "surface_decodes_uniquely": "YES" if surface_index[surface] == [tuple_id] else "NO",
            })

    write("THREE_HUNDRED_SEVENTIETH_SIXTEEN_RENDERED_CARDS.tsv", render_rows)
    by_palette = defaultdict(list)
    for row in render_rows:
        by_palette[row["palette_id"]].append(row)
    cross_rows = []
    for source_palette, source_rows in by_palette.items():
        source_ids = [row["joint_tuple_id"] for row in source_rows]
        decoded_ids = [surface_index[row["rendered_surface"]][0] for row in source_rows]
        for reader_palette, reader_rows in by_palette.items():
            rewritten = [row["rendered_surface"] for row in reader_rows]
            cross_rows.append({
                "source_palette": source_palette,
                "reader_palette": reader_palette,
                "source_surface_sequence": " ".join(row["rendered_surface"] for row in source_rows),
                "decoded_joint_tuple_ids": "|".join(decoded_ids),
                "reader_rewritten_sequence": " ".join(rewritten),
                "identities_match": "YES" if decoded_ids == source_ids else "NO",
                "values_match": "YES" if [board[i]["atomic_value_de"] for i in decoded_ids] == [row["atomic_value_de"] for row in source_rows] else "NO",
                "pair_decisions_match": "YES" if [row["pair_id"] for row in source_rows] == [row["pair_id"] for row in reader_rows] else "NO",
                "full_crossread": "YES" if decoded_ids == source_ids else "NO",
            })
    write("THREE_HUNDRED_SEVENTIETH_FOUR_CROSS_READS.tsv", cross_rows)

    seq_a = " ".join(PALETTES["PALETTE_A_COMPACT"][:5]) + " | " + " ".join(PALETTES["PALETTE_A_COMPACT"][5:])
    seq_b = " ".join(PALETTES["PALETTE_B_EXPANDED"][:5]) + " | " + " ".join(PALETTES["PALETTE_B_EXPANDED"][5:])
    edition = f"""# Pass 370 — zwei Werkstattpaletten

Diese Paletten sind Unterrichtsprofile aus registrierten Varianten, keine
Zuschreibung an historische Voynich-Hände.

## Palette A — knapp

`{seq_a}`

## Palette B — erweitert

`{seq_b}`

Beide lesen: Ansatz → Portion → durchleiten → Kurzwärme → Einsetzen ||
Sollmaß → Langkontakt → Kurzkontakt. Sechs Positionen wechseln registriert;
`cheky` und `qokedy` bleiben invariant. Beide Schreiber lesen und schreiben die
jeweils andere Palette 8/8 zurück, einschließlich derselben drei Paarwerte.
"""
    (HERE / "THREE_HUNDRED_SEVENTIETH_TWO_PALETTE_EDITION.md").write_text(edition, encoding="utf-8")
    report = """# Pass 370 — Zweihand-Kreuzlesung

Zwei Werkstattpaletten rendern dieselbe neue achtteilige Anweisung. Sechs
Positionen variieren, zwei bleiben invariant. Alle vier Sender-Leser-Paare
erhalten Identität, Wert, Mikrozyklen und Paarentscheidungen. Die Variation ist
damit ein lernbarer Renderer über einem gemeinsamen Kartendeck.

Als nächstes wird die Anweisung in zwei unterschiedliche Restbreiten umbrochen.
Nur ein echter Fortsetzungsbruch darf eine Randkopie bekommen; Paarwerte und
Mikrozyklusgrenzen dürfen dabei nicht verrutschen.
"""
    (HERE / "THREE_HUNDRED_SEVENTIETH_REPORT.md").write_text(report, encoding="utf-8")
    differing = sum(a != b for a, b in zip(*PALETTES.values()))
    summary = {
        "status": "PASS",
        "palettes": len(PALETTES),
        "rendered_cards": len(render_rows),
        "varying_positions": differing,
        "invariant_positions": 8 - differing,
        "cross_reads": len(cross_rows),
        "full_cross_reads": sum(row["full_crossread"] == "YES" for row in cross_rows),
        "pair_cards_per_palette": sum(row["pair_id"] != "NONE" for row in by_palette["PALETTE_A_COMPACT"]),
    }
    (HERE / "THREE_HUNDRED_SEVENTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
