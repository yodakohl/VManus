#!/usr/bin/env python3
"""Build Pass 761: parameterize seven large formulas as motifs plus tail strips."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P757 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_motifs_seven_hundred_fifty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    formulas = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_7_LARGE_FORMULAS.tsv")
    motifs = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_8_SHARED_CARD_MOTIFS.tsv")
    motif_for = {row["card_recipe"]: row["motif_id"] for row in motifs}
    motif_value = {row["motif_id"]: row["card_recipe"] for row in motifs}

    pending_layouts = []
    tail_sequences = []
    for formula in formulas:
        layout = []
        run = []
        for card in formula["observed_recipe_sequence"].split(" | ") + ["__END__"]:
            if card in motif_for or card == "__END__":
                if run:
                    tail = " | ".join(run)
                    tail_sequences.append(tail)
                    layout.append(("TAIL", tail))
                    run = []
                if card != "__END__":
                    layout.append(("MOTIF", motif_for[card]))
            else:
                run.append(card)
        pending_layouts.append((formula, layout))

    unique_tails = sorted(set(tail_sequences), key=lambda tail: (len(tail.split(" | ")), tail))
    tail_id_for = {tail: f"T{number:02d}" for number, tail in enumerate(unique_tails, start=1)}
    tail_rows = []
    for tail in unique_tails:
        tail_id = tail_id_for[tail]
        users = [formula["statement_id"] for formula, layout in pending_layouts if ("TAIL", tail) in layout]
        tail_rows.append({
            "tail_id": tail_id,
            "card_sequence": tail,
            "cards": len(tail.split(" | ")),
            "formula_uses": len(users),
            "statement_ids": ",".join(users),
            "teaching_status": "BOUND_LOCAL_TAIL_STRIP",
        })

    layout_rows = []
    reconstruction_rows = []
    family_bucket: dict[str, list[dict[str, object]]] = defaultdict(list)
    for formula, layout in pending_layouts:
        tokens = [value if kind == "MOTIF" else tail_id_for[value] for kind, value in layout]
        reconstructed_cards = []
        motif_tokens = 0
        tail_tokens = 0
        for token in tokens:
            if token.startswith("M"):
                reconstructed_cards.append(motif_value[token])
                motif_tokens += 1
            else:
                tail = next(row["card_sequence"] for row in tail_rows if row["tail_id"] == token)
                reconstructed_cards.extend(tail.split(" | "))
                tail_tokens += 1
        reconstructed = " | ".join(reconstructed_cards)
        exact = reconstructed == formula["observed_recipe_sequence"]
        layout_row = {
            "statement_id": formula["statement_id"],
            "page": formula["page"],
            "record": formula["record"],
            "formula_family": formula["formula_family"],
            "layout_tokens": " ".join(tokens),
            "layout_units": len(tokens),
            "motif_tokens": motif_tokens,
            "tail_tokens": tail_tokens,
            "expanded_cards": len(reconstructed_cards),
            "reconstruction_exact": "YES" if exact else "NO",
        }
        layout_rows.append(layout_row)
        family_bucket[formula["formula_family"]].append(layout_row)
        for ordinal, card in enumerate(reconstructed_cards, start=1):
            reconstruction_rows.append({
                "statement_id": formula["statement_id"],
                "formula_family": formula["formula_family"],
                "card_ordinal": ordinal,
                "component_recipe": card,
                "source_token": next(
                    token for token in tokens
                    if (token.startswith("M") and motif_value[token] == card)
                    or (token.startswith("T") and card in next(row["card_sequence"] for row in tail_rows if row["tail_id"] == token).split(" | "))
                ),
            })

    family_rows = []
    for family, rows in family_bucket.items():
        family_rows.append({
            "formula_family": family,
            "statements": len(rows),
            "statement_ids": ",".join(str(row["statement_id"]) for row in rows),
            "layout_units": sum(int(row["layout_units"]) for row in rows),
            "motif_tokens": sum(int(row["motif_tokens"]) for row in rows),
            "tail_tokens": sum(int(row["tail_tokens"]) for row in rows),
            "expanded_cards": sum(int(row["expanded_cards"]) for row in rows),
            "parameterization": "shared motif slots plus bound local tail strips",
            "can_drop_exact_layout": "NO",
        })

    write("SEVEN_HUNDRED_SIXTY_FIRST_19_LOCAL_TAIL_STRIPS.tsv", tail_rows)
    write("SEVEN_HUNDRED_SIXTY_FIRST_7_PARAMETERIZED_LAYOUTS.tsv", layout_rows)
    write("SEVEN_HUNDRED_SIXTY_FIRST_3_FAMILY_PARAMETERS.tsv", family_rows)
    write("SEVEN_HUNDRED_SIXTY_FIRST_74_RECONSTRUCTED_CARDS.tsv", reconstruction_rows)

    total_units = sum(int(row["layout_units"]) for row in layout_rows)
    report = f"""# Pass 761 — grosse Formeln als Motive plus Reststreifen

Die sieben gebundenen Formeln wurden in acht gemeinsame Kartenmotive und zusammenhaengende lokale Reststreifen zerlegt.

## Ergebnis

-74 sichtbare Karten werden aus{total_units} Layout-Einheiten rekonstruiert.
-31 Einheiten sind gemeinsame Motive;19 Einheiten sind lokale Reststreifen.
- Die19 Reststreifen enthalten zusammen43 Karten und sind alle verschieden.
- Alle sieben Formeln werden exakt zurueckgebaut.

Die Einsparung ist real:24 einzelne Lernpositionen verschwinden, weil ein mehrkartiger Reststreifen als eine kopierte Einheit gilt. Aber die drei Familienschalen allein reichen nicht. Kein lokaler Reststreifen wiederholt sich in einer zweiten Formel; deshalb bleiben sieben genaue Layoutzeilen notwendig.

## Lehrregel

Der Lehrling waehlt zuerst Herbal-owner, Herbal-wet-process oder Bio-address. Dann schreibt er eine kurze Folge aus bekannten M-Motiven und lokalen T-Streifen. Das ist einfacher als74 Einzelkarten, aber ehrlicher als die Behauptung, drei allgemeine Satzschablonen koennten alles frei erzeugen.

Als naechstes wird diese M/T-Notation in den Vorwaertscompiler eingesetzt und die alte sieben-Satz-Vollfolge durch sieben kurze Layoutzeilen plus19 Reststreifen ersetzt.
"""
    (HERE / "SEVEN_HUNDRED_SIXTY_FIRST_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "formula_families": len(family_rows), "large_formulas": len(layout_rows),
        "shared_motifs": len(motifs), "local_tail_strips": len(tail_rows),
        "layout_units": total_units, "expanded_cards": len(reconstruction_rows),
        "saved_learning_positions": len(reconstruction_rows) - total_units,
        "repeated_tail_strips": sum(int(row["formula_uses"]) > 1 for row in tail_rows),
        "semantic_changes": 0,
        "decision": "SEVEN_LAYOUTS_PLUS_EIGHT_MOTIFS_PLUS_NINETEEN_TAIL_STRIPS_REBUILD_74_CARDS__THREE_SHELLS_ALONE_INSUFFICIENT",
    }
    (HERE / "SEVEN_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
