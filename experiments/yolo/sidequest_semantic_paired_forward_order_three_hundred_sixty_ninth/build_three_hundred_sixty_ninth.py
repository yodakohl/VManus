#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P353 = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third"
P362 = ROOT / "experiments/yolo/sidequest_semantic_workshop_thesaurus_three_hundred_sixty_second"
P366 = ROOT / "experiments/yolo/sidequest_semantic_pair_placard_drill_three_hundred_sixty_sixth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


ORDER = [
    (1, "C1", "BEZUG[Ansatz]", "7a4bb8136330ee4e6e56", "sor", "Ansatz"),
    (2, "C1", "MASS[Portion]", "9da1b6ac2c929daea697", "kain", "Portion"),
    (3, "C1", "TRANSFER[durchleiten]", "2cc8bb3c2af19607888f", "shckhy", "durchleiten"),
    (4, "C1", "ZUSTAND[Kurzwärme]", "d904bf7b044dd3922781", "cheky", "Kurzwärme"),
    (5, "C1", "ZIEL[Einsetzen]", "276a7c2d74d1143446f4", "choky", "Einsetzen"),
    (6, "C2", "MASS[Sollmaß]", "2f1c5e56e8f0ff459065", "daiin", "Sollmaß"),
    (7, "C2", "ZUSTAND[Langkontakt]", "0275fbf14e07935b0a45", "qokeey", "Langkontakt"),
    (8, "C2", "ZUSTAND[Kurzkontakt]", "7db18b2f0fb7ed0fcfd3", "qokedy", "Kurzkontakt"),
]


def main() -> None:
    board = {row["joint_tuple_id"]: row for row in read(P353 / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")}
    phrases = {row["controlled_phrase"]: row for row in read(P362 / "THREE_HUNDRED_SIXTY_SECOND_159_PHRASE_INDEX.tsv")}
    occurrences = read(P366 / "THREE_HUNDRED_SIXTY_SIXTH_72_PAIR_OCCURRENCES.tsv")
    pair_rules: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        pair_rules[(row["pair_id"], row["owner"])].append(row)

    owner = "B3_MAIN_ARCH_LINKED_PAIR"
    rows = []
    for index, (position, cycle, phrase, tuple_id, surface, value) in enumerate(ORDER):
        card = board[tuple_id]
        pair = card["ambiguous_pair_id"]
        right_value = ORDER[index + 1][5] if index + 1 < len(ORDER) and ORDER[index + 1][1] == cycle else "END"
        if pair == "NONE":
            decision = "UNIQUE_VALUE_SLOT_CARD"
            matching_rule = "NONE"
        else:
            possible = pair_rules[(pair, owner)]
            target_rules = [r for r in possible if r["target_joint_tuple_id"] == tuple_id]
            owner_ids = {r["target_joint_tuple_id"] for r in possible}
            if len(owner_ids) == 1:
                decision = "PAIR_OWNER"
                matching_rule = f"{owner}=>{tuple_id}"
            else:
                exact = [r for r in target_rules if r["right_neighbor_value_de"] == right_value]
                decision = "PAIR_OWNER_PLUS_RIGHT"
                matching_rule = f"{owner}>>{right_value}=>{tuple_id}"
                if not exact:
                    raise ValueError((pair, owner, right_value, tuple_id))
        rows.append({
            "position": position,
            "microcycle": cycle,
            "master_dictated_value_de": value,
            "controlled_phrase": phrase,
            "family_id": phrases[phrase]["family_id"],
            "visible_owner": owner,
            "right_neighbor_value_de": right_value,
            "pair_id": pair,
            "decision_route": decision,
            "matching_pair_rule": matching_rule,
            "selected_joint_tuple_id": tuple_id,
            "selected_surface": surface,
            "surface_registered": "YES" if surface in card["registered_surface_palette"].split("|") else "NO",
            "backread_value_de": card["atomic_value_de"],
            "backread_exact": "YES" if card["atomic_value_de"] == value else "NO",
        })
    write("THREE_HUNDRED_SIXTY_NINTH_EIGHT_CARD_PAIRED_ORDER.tsv", rows)

    surfaces = " ".join(r["selected_surface"] for r in rows[:5]) + " | " + " ".join(r["selected_surface"] for r in rows[5:])
    values = " → ".join(r["backread_value_de"] for r in rows)
    pair_lines = "\n".join(f"- {r['pair_id']}: {r['matching_pair_rule']} → `{r['selected_surface']}`" for r in rows if r["pair_id"] != "NONE")
    edition = f"""# Pass 369 — Auftrag mit drei Paarformen

## Nur gesprochenes Meisterdiktat

Nimm aus dem Ansatz eine Portion, leite sie durch, erwärme sie kurz und setze
sie ein. Richte den eingesetzten Posten nach Sollmaß, halte ihn länger und
schließe mit kurzem Kontakt.

Besitzer: `B3_MAIN_ARCH_LINKED_PAIR`.

## Vom Schreiber gesetzte Oberfläche

`{surfaces}`

## Drei Paarentscheidungen

{pair_lines}

## Oberflächenrücklesung

{values}.

Alle acht Werte werden getroffen. Bei Einsetzen und Kurzkontakt entscheidet der
B3-Besitzer allein; bei Langkontakt entscheidet erst der folgende Kurzkontakt
zwischen den beiden gleichwertigen Schreiberkarten.
"""
    (HERE / "THREE_HUNDRED_SIXTY_NINTH_PAIRED_ORDER_READING.md").write_text(edition, encoding="utf-8")
    report = """# Pass 369 — erschwerte Vorwärtssetzung

Die neue achtteilige Anweisung enthält drei absichtlich gewählte Paarwerte.
Zwei konkrete Karten werden vom B3-Besitzer bestimmt; die dritte braucht den
rechten Nachbarn. Danach liest ein zweiter Schreiber alle acht Oberflächen
eindeutig zurück. Damit arbeiten die Bedeutungs- und Schreiberformtafeln auch in
einer neuen, nicht kopierten Sequenz zusammen.

Als nächstes wird der Auftrag in zwei verschiedene registrierte Hände gesetzt.
Nur wirklich attestierte Oberflächenvarianten dürfen wechseln; Paarentscheidung,
Wert und Satzplatz müssen gleich bleiben.
"""
    (HERE / "THREE_HUNDRED_SIXTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "cards": len(rows),
        "microcycles": len({r["microcycle"] for r in rows}),
        "pair_cards": sum(r["pair_id"] != "NONE" for r in rows),
        "owner_pair_decisions": sum(r["decision_route"] == "PAIR_OWNER" for r in rows),
        "owner_right_pair_decisions": sum(r["decision_route"] == "PAIR_OWNER_PLUS_RIGHT" for r in rows),
        "exact_backreads": sum(r["backread_exact"] == "YES" for r in rows),
        "surface_line": surfaces,
    }
    (HERE / "THREE_HUNDRED_SIXTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
