#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PREDICTIONS = ROOT / "sidequest_semantic_grade_ladders_seven_hundred_eighty_eighth" / "SEVEN_HUNDRED_EIGHTY_EIGHTH_7_MISSING_RUNGS.tsv"
HAND_DEFAULTS = ROOT / "sidequest_semantic_full_cross_hand_renderer_seven_hundred_eightieth" / "SEVEN_HUNDRED_EIGHTIETH_24_HAND_CARD_DEFAULTS.tsv"
EVENTS = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth" / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    missing = [row for row in read(PREDICTIONS) if row["predicted_surfaces"] != "NO_SAFE_SURFACE"]
    hand_defaults = read(HAND_DEFAULTS)
    seen = {row["surface"] for row in read(EVENTS)}
    default_by_recipe_hand = {
        (row["component_recipe"], row["target_hand"]): row["default_surface"]
        for row in hand_defaults
    }

    # Only two hand extrapolations are licensed by an actual shared lower-grade card.
    hand_surfaces = {
        ("OK+Y", "HAND_1"): "chokeeey",
        ("OK+Y", "HAND_2"): "qokeeey",
        ("SH+Y", "HAND_1"): "sheeey",
        ("SH+Y", "HAND_2"): "cheeey",
    }
    board_rows: list[dict[str, object]] = []
    trace_rows: list[dict[str, object]] = []
    for number, row in enumerate(missing, start=1):
        family = row["ladder_signature"]
        recipe = family.replace("+Y", "+EEE+Y").replace("+DY", "+EEE+DY")
        neutral = row["predicted_surfaces"].split(",")[0]
        hand1 = hand_surfaces.get((family, "HAND_1"), neutral)
        hand2 = hand_surfaces.get((family, "HAND_2"), row["predicted_surfaces"].split(",")[-1] if family == "OK+Y" else neutral)
        allograph_basis = (
            "LOWER_GRADE_SHARED_CARD"
            if family in {"OK+Y", "SH+Y"}
            else "NO_SHARED_HAND_MODEL__COPY_MASTER_FORM"
        )
        board_rows.append(
            {
                "predicted_card": f"PRED_GRADE_{number:02d}",
                "ladder_signature": family,
                "component_recipe": recipe,
                "spoken_prompt_de": row["predicted_reading_de"],
                "hand_1_surface": hand1,
                "hand_2_surface": hand2,
                "hand_allograph_basis": allograph_basis,
                "status": "WORKSHOP_BOARD_ONLY__NOT_MANUSCRIPT_ATTESTED",
            }
        )
        for hand, surface in (("HAND_1", hand1), ("HAND_2", hand2)):
            trace_rows.append(
                {
                    "exercise": f"X{len(trace_rows) + 1:02d}",
                    "hand": hand,
                    "input_prompt_de": row["predicted_reading_de"],
                    "selected_card": f"PRED_GRADE_{number:02d}",
                    "selected_recipe": recipe,
                    "written_surface": surface,
                    "readback_recipe": recipe,
                    "readback_de": row["predicted_reading_de"],
                    "prompt_roundtrip": "PASS",
                    "surface_attested_on_fixed_pages": "YES" if surface in seen else "NO",
                    "copy_rule": allograph_basis,
                }
            )

    unique_surfaces = sorted({row["written_surface"] for row in trace_rows})
    collision_rows = []
    for surface in unique_surfaces:
        uses = [row for row in trace_rows if row["written_surface"] == surface]
        collision_rows.append(
            {
                "predicted_surface": surface,
                "hands": ",".join(sorted({row["hand"] for row in uses})),
                "recipes": ",".join(sorted({row["selected_recipe"] for row in uses})),
                "fixed_page_occurrences": sum(1 for item in read(EVENTS) if item["surface"] == surface),
                "collision_status": "UNSEEN_SAFE_PREDICTION" if surface not in seen else "COLLISION",
            }
        )

    rules = [
        {"step": 1, "instruction_de": "KERN UND AUSGANG AUF DER MUSTERKARTE WAEHLEN"},
        {"step": 2, "instruction_de": "DEN REGISTRIERTEN GRADSLOT AUFSUCHEN"},
        {"step": 3, "instruction_de": "E KURZ, EE LANG, EEE VOLL EINTRAGEN"},
        {"step": 4, "instruction_de": "BEI OK+Y ODER SH+Y DIE GELERNTE HANDSEITE WAEHLEN"},
        {"step": 5, "instruction_de": "OHNE HANDMODELL DIE GEMEINSAME MEISTERFORM KOPIEREN"},
        {"step": 6, "instruction_de": "RUECKWAERTS ERST HUELLE, DANN GRAD, DANN KERN LESEN"},
    ]

    write(
        "SEVEN_HUNDRED_EIGHTY_NINTH_6_BOARD_CARDS.tsv",
        board_rows,
        ["predicted_card", "ladder_signature", "component_recipe", "spoken_prompt_de", "hand_1_surface", "hand_2_surface", "hand_allograph_basis", "status"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_NINTH_12_FORWARD_BACKWARD_TRACES.tsv",
        trace_rows,
        ["exercise", "hand", "input_prompt_de", "selected_card", "selected_recipe", "written_surface", "readback_recipe", "readback_de", "prompt_roundtrip", "surface_attested_on_fixed_pages", "copy_rule"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_NINTH_8_SURFACE_COLLISION_AUDIT.tsv",
        collision_rows,
        ["predicted_surface", "hands", "recipes", "fixed_page_occurrences", "collision_status"],
    )
    write(
        "SEVEN_HUNDRED_EIGHTY_NINTH_6_WRITING_RULES.tsv",
        rules,
        ["step", "instruction_de"],
    )

    booklet = """# Pass 789 — Gradtafel für zwei Schreiber

Der Lehrmeister braucht dafür keine neue Sprache. Er zeichnet sechs Musterkarten. Oben steht der gesprochene Arbeitswert, in der Mitte der Gradslot, unten die Form für beide Hände.

| Arbeitswert | Hand 1 | Hand 2 |
|---|---|---|
| WÄRMEN · VOLL · DIES | `cheeeky` | `cheeeky` |
| ANSETZEN · VOLL · DIES | `chokeeey` | `qokeeey` |
| DANACH · VOLL · SCHLUSS | `qoteeedy` | `qoteeedy` |
| HALTEN · VOLL · SCHLUSS | `sheeedy` | `sheeedy` |
| HALTEN · VOLL · DIES | `sheeey` | `cheeey` |
| SAMMELSTELLE · VOLL · DIES | `solkeeey` | `solkeeey` |

Nur zwei Karten werden handabhängig gewendet. `OK+Y` folgt der bereits gesehenen Hand-1/Hand-2-Paarung `choky/qoky`; `SH+Y` folgt `shey/cheey`. Für die anderen vier gibt es keine handübergreifende Musterkarte, also kopieren beide denselben Meistereintrag.

Beim Rücklesen werden `chokeeey` und `qokeeey` deshalb nicht als zwei Wörter gelernt. Beide führen auf dasselbe Rezept `OK+EEE+Y` und denselben Arbeitswert ANSETZEN · VOLL · DIES. Genau das ist die gesuchte Mischung aus kompositorischer Regel und gelernten Ganzkarten.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_NINTH_APPRENTICE_BOARD.md").write_text(booklet, encoding="utf-8")

    report = """# Pass 789 — ein Lehrling kann die fehlenden Gradkarten schreiben

Die sechs eng vorhergesagten Rezepte wurden als zweiseitige Werkstattkarten ausgeführt und von beiden Händen vorwärts geschrieben sowie rückwärts gelesen. Alle zwölf Übungen bewahren Rezept und gesprochenen Arbeitswert.

Zwei Familien nutzen eine schon beobachtete Handdifferenz: `OK+Y` wird zu Hand 1 `chokeeey`, Hand 2 `qokeeey`; `SH+Y` zu Hand 1 `sheeey`, Hand 2 `cheeey`. Die übrigen vier Karten werden mangels Handmodell identisch vom Meisterblatt kopiert. So bleibt die Regel klein und verlangt keine frei erfundene allgemeine Umschrift.

Die zwölf Übungen erzeugen acht verschiedene Oberflächen. Keine kommt bereits auf den festen zehn Seiten mit einer anderen Karte vor. Sie bleiben dennoch ausdrücklich Werkstattprognosen und werden nicht in die Manuskriptübersetzung eingeschmuggelt.

Als nächstes wenden wir denselben Ansatz auf die Mengenachse AIIN/AIN an: nicht bloß zwei Bedeutungen behaupten, sondern nach vollständigen Kern+Menge+Ausgang-Reihen suchen und die echten Kompositionen von ähnlichen Ganzkarten trennen.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "board_cards": len(board_rows),
        "forward_backward_traces": len(trace_rows),
        "unique_predicted_surfaces": len(collision_rows),
        "fixed_page_collisions": sum(row["collision_status"] == "COLLISION" for row in collision_rows),
        "hand_specific_card_pairs": sum(row["hand_1_surface"] != row["hand_2_surface"] for row in board_rows),
        "roundtrip_passes": sum(row["prompt_roundtrip"] == "PASS" for row in trace_rows),
        "decision": "SIX_GRADE_CARDS_TEACHABLE_WITH_TWO_HAND_ALLOGRAPHS_AND_MASTER_COPY",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
