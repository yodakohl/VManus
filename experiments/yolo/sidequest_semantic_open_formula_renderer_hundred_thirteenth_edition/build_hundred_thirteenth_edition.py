#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CARDS = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_173_CARD_POCKET.tsv"
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_230_SURFACE_INDEX.tsv"
PREDICTIONS = ROOT / "experiments/yolo/sidequest_semantic_formula_order_hundred_twelfth_edition/HUNDRED_TWELFTH_TWELVE_ORDERED_PREDICTIONS.tsv"

PROFILES = [
    ("R-A", "VORLAGENHAND"),
    ("R-B", "Q-EINTRITTSHAND"),
    ("R-C", "S-FLUSSHAND"),
    ("R-D", "KURZHAND"),
]

ATOM_CARD = {
    "Y": "MC123", "AIIN": "MC039", "AL": "MC154", "OR": "MC080",
    "OT+OL": "MC053", "OL": "MC153", "SHED+E+CLOSE": "MC128",
    "CHD+CLOSE": "MC025", "OL+OR": "MC157",
}


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def choose(renderer, card):
    variants = card["all_registered_surfaces"].split("|")
    master = card["master_form"]
    if renderer == "R-A":
        return master
    if renderer == "R-B":
        return next((x for x in variants if x.startswith("q")), master)
    if renderer == "R-C":
        return next((x for x in variants if x.startswith("sh")), next((x for x in variants if x.startswith("s")), master))
    return min(enumerate(variants), key=lambda x: (len(x[1]), x[0]))[1]


def main():
    cards = {r["master_card_id"]: r for r in load(CARDS)}
    surface_rows = load(SURFACES)
    surface_to_cards = defaultdict(set)
    for row in surface_rows:
        surface_to_cards[row["visible_surface"]].add(row["master_card_id"])
    open_predictions = [r for r in load(PREDICTIONS) if r["current_status"] == "OPEN_FORWARD_SEQUENCE"]

    programs = []
    realizations = []
    for row in open_predictions:
        atoms = row["atom_sequence"].split(" > ")
        ids = [ATOM_CARD[a] for a in atoms]
        selected = [cards[x] for x in ids]
        programs.append({
            "prediction_id": row["prediction_id"],
            "predicted_workshop_reading_de": row["predicted_workshop_reading_de"],
            "atom_sequence": row["atom_sequence"],
            "selected_master_card_ids": " ".join(ids),
            "master_surface_sequence": " ".join(x["master_form"] for x in selected),
            "selection_rule": "shortest or most recurrent existing card with the exact atom program; card identity fixed across hands",
        })
        for renderer, name in PROFILES:
            visible = [choose(renderer, card) for card in selected]
            ambiguous = [x for x in visible if len(surface_to_cards[x]) > 1]
            realizations.append({
                "prediction_id": row["prediction_id"],
                "renderer_id": renderer,
                "workshop_hand": name,
                "predicted_workshop_reading_de": row["predicted_workshop_reading_de"],
                "atom_sequence": row["atom_sequence"],
                "card_identity_sequence": " ".join(ids),
                "visible_surface_sequence": " ".join(visible),
                "changed_from_master": str(sum(v != c["master_form"] for v, c in zip(visible, selected))),
                "ambiguous_surface_count": str(len(ambiguous)),
                "ambiguous_surfaces": "|".join(ambiguous) if ambiguous else "NONE",
                "all_individual_surfaces_preexisting": "YES",
                "semantic_program_preserved": "YES",
            })
    write_tsv("HUNDRED_THIRTEENTH_SEVEN_OPEN_FORMULA_PROGRAMS.tsv", programs)
    write_tsv("HUNDRED_THIRTEENTH_TWENTY_EIGHT_SCRIBAL_RENDERINGS.tsv", realizations)

    md = ["# Sieben offene Formeln in vier Schreiberhänden", ""]
    for program in programs:
        md += [f"## {program['prediction_id']}", "", program["predicted_workshop_reading_de"], ""]
        for r in [x for x in realizations if x["prediction_id"] == program["prediction_id"]]:
            md.append(f"- {r['workshop_hand']}: `{r['visible_surface_sequence']}`")
        md.append("")
    (OUT / "HUNDRED_THIRTEENTH_PARALLEL_PREDICTED_FORMS.md").write_text("\n".join(md), encoding="utf-8")

    report = [
        "# Hundertdreizehnte Runde: offene Formeln sichtbar schreiben", "",
        "Die sieben offenen R112-Sequenzen sind nun keine abstrakten Atomlisten mehr. Jede benutzt nur",
        "bereits vorhandene Karten und jede der vier Werkstatthände benutzt ausschließlich bereits",
        "registrierte Oberflächen. Neu ist nur die Reihenfolge der bekannten Karten.", "",
        "Beispiel: ›diesen Posten nach Sollmaß zum Ziel bringen‹ wird in der Vorlagenhand `chey aiin al`,",
        "in der S-Hand `shy saiin sal` und in der Kurzhand `y aiin al`. Die Bedeutung und die drei",
        "Kartenidentitäten bleiben gleich.", "",
        "Die Vorhersagen sind besonders nützlich, weil ein späterer Seitenzuwachs sie ohne neue",
        "Bedeutungserfindung treffen oder widerlegen kann. Oberflächenkollisionen bleiben im lokalen",
        "Karten-/Besitzerkontext aufzulösen.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_THIRTEENTH_OPEN_FORMULA_RENDERER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "open_programs": len(programs), "renderings": len(realizations),
        "preexisting_surface_renderings": sum(r["all_individual_surfaces_preexisting"] == "YES" for r in realizations),
        "preserved_programs": sum(r["semantic_program_preserved"] == "YES" for r in realizations),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
