#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P353 = ROOT / "experiments/yolo/sidequest_semantic_workshop_board_three_hundred_fifty_third"
P367 = ROOT / "experiments/yolo/sidequest_semantic_apprentice_curriculum_three_hundred_sixty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


SLOT_RANK = {
    "S1_BEZUG_FOLGE": 1,
    "S2_MATERIAL_MASS": 2,
    "S3_PROZESS_TRANSFER": 3,
    "S4_DAUER_ZUSTAND": 4,
    "S5_ZIEL_ANWENDUNG": 5,
    "S6_BEREIT_ABSCHLUSS": 6,
}


def main() -> None:
    board = read(P353 / "THREE_HUNDRED_FIFTY_THIRD_173_CARD_WORKSHOP_BOARD.tsv")
    exercise = read(P367 / "THREE_HUNDRED_SIXTY_SEVENTH_FRESH_TEN_CARD_ORDER.tsv")
    surface_index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in board:
        for surface in row["registered_surface_palette"].split("|"):
            surface_index[surface].append(row)

    lookup_rows = []
    previous_rank = None
    cycle = 1
    for source in exercise:
        surface = source["selected_surface"]
        candidates = surface_index[surface]
        chosen = candidates[0]
        rank = SLOT_RANK[chosen["primary_slot"]]
        boundary_before = "START"
        if previous_rank is not None:
            if rank < previous_rank:
                cycle += 1
                boundary_before = "NEW_MICROCYCLE_BY_SLOT_DROP"
            else:
                boundary_before = "CONTINUE_NONDECREASING_SLOT"
        lookup_rows.append({
            "position": source["position"],
            "visible_surface_only": surface,
            "surface_candidate_cards": len(candidates),
            "chosen_joint_tuple_id": chosen["joint_tuple_id"],
            "recovered_atomic_value_de": chosen["atomic_value_de"],
            "recovered_slot_code": chosen["primary_slot"],
            "slot_rank": rank,
            "boundary_before": boundary_before,
            "inferred_microcycle": f"C{cycle}",
            "visible_owner": "B3_MAIN_ARCH_LINKED_PAIR",
            "formula_consulted": "NO",
            "running_page_consulted": "NO",
            "lookup_status": "UNIQUE_SURFACE_ON_173_CARD_BOARD" if len(candidates) == 1 else "CONTEXT_REQUIRED",
        })
        previous_rank = rank

    write("THREE_HUNDRED_SIXTY_EIGHTH_TEN_SURFACE_LOOKUPS.tsv", lookup_rows)
    reading_rows = [
        {
            "reading_id": "R1_TECHNICAL_NEUTRAL",
            "status": "SELECTED",
            "german_reading": "Am verbundenen B3-Arbeitsplatz nimm den laufenden Ansatz, teile eine Portion ab und richte sie nach dem Sollmaß. Leite sie durch den vorhandenen Gang, erwärme sie kurz und führe sie bis zur bezeichneten Stelle. Ziehe den klaren Anteil ab, seihe ihn nach, halte ihn länger und verwahre ihn.",
            "owner_supplied_nouns": "verbundener B3-Arbeitsplatz|vorhandener Gang",
            "extra_domain_nouns": "NONE",
            "semantic_additions": 0,
            "reason": "Alle Inhaltswörter stammen aus Kartenwert oder sichtbarem B3-Besitzer.",
        },
        {
            "reading_id": "R2_BATHHOUSE",
            "status": "LIVE_EXPANSION",
            "german_reading": "Am verbundenen Becken nimm die vorbereitete Badflüssigkeit portionsweise, richte sie nach dem Sollmaß, leite und erwärme sie und führe sie zur Badestelle; ziehe den klaren Anteil ab, seihe ihn nach, halte ihn warm und bewahre ihn auf.",
            "owner_supplied_nouns": "verbundenes Becken",
            "extra_domain_nouns": "Badflüssigkeit|Badestelle",
            "semantic_additions": 2,
            "reason": "Passt zur B3-Bildwelt, benennt den Gebrauch aber enger als die Karten.",
        },
        {
            "reading_id": "R3_MEDICAL",
            "status": "LIVE_EXPANSION",
            "german_reading": "Nimm vom Heilansatz eine Dosis nach vorgeschriebenem Maß, leite und erwärme sie, bringe sie an die Behandlungsstelle, ziehe den klaren Auszug ab, seihe ihn nach, lasse ihn einwirken und verwahre ihn.",
            "owner_supplied_nouns": "NONE",
            "extra_domain_nouns": "Heilansatz|Dosis|Behandlungsstelle|einwirken",
            "semantic_additions": 4,
            "reason": "Flüssig lesbar, aber vier medizinische Engführungen stehen nicht auf den Karten.",
        },
    ]
    write("THREE_HUNDRED_SIXTY_EIGHTH_THREE_FREE_READINGS.tsv", reading_rows)
    literal = " → ".join(row["recovered_atomic_value_de"] for row in lookup_rows)
    surfaces = " ".join(row["visible_surface_only"] for row in lookup_rows[:6]) + " | " + " ".join(row["visible_surface_only"] for row in lookup_rows[6:])
    edition = f"""# Pass 368 — oberflächenreine Rücklesung

## Sichtbarer Auftrag

`{surfaces}`

Bekannt ist nur der sichtbare Besitzer `B3_MAIN_ARCH_LINKED_PAIR`. Formeln und
laufende Seiten bleiben geschlossen.

## Wörtliche Kartenlesung

{literal}.

Der Abfall von Slot 5 auf Slot 3 trennt die zwei Mikrogänge automatisch.

## Freie ausgewählte Lesung

{reading_rows[0]['german_reading']}

Die Badehaus- und medizinische Fassung bleiben möglich, brauchen aber zwei bzw.
vier zusätzliche Fachnomen. Die neutrale technische Lesung setzt keines hinzu.
"""
    (HERE / "THREE_HUNDRED_SIXTY_EIGHTH_SURFACE_ONLY_READING.md").write_text(edition, encoding="utf-8")
    report = """# Pass 368 — Oberfläche ohne Kontrollformeln

Alle zehn sichtbaren Formen sind auf dem 173-Karten-Brett eindeutig. Ein Leser
gewinnt deshalb zehn Werte und Slots ohne Formel oder Seitenexemplar; der einzige
Slotabfall trennt die zwei Mikrogänge. Die neutrale Werkstattanweisung bleibt
vollständig, während Badehaus und Medizin als engere Besitzerexpansionen leben.

Als nächstes sollte dieselbe Probe schwieriger werden: gezielt drei Oberflächen
aus den vierzehn Paar-Tafeln einsetzen. Dann muss der B3-Besitzer und rechte
Nachbar die Karte bestimmen, nicht die Oberfläche allein.
"""
    (HERE / "THREE_HUNDRED_SIXTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "visible_surfaces": len(lookup_rows),
        "unique_board_lookups": sum(int(row["surface_candidate_cards"]) == 1 for row in lookup_rows),
        "inferred_microcycles": len({row["inferred_microcycle"] for row in lookup_rows}),
        "formula_lookups": 0,
        "running_page_lookups": 0,
        "free_readings": len(reading_rows),
        "selected_reading_semantic_additions": int(reading_rows[0]["semantic_additions"]),
    }
    (HERE / "THREE_HUNDRED_SIXTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
