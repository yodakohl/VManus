#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
POCKET = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition"
ECOLOGY = ROOT / "experiments/yolo/sidequest_semantic_component_ecology_hundred_fourth_edition/HUNDRED_FOURTH_44_COMPONENT_ECOLOGY.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_atomic_defaults_hundred_first_edition/HUNDRED_FIRST_381_EVENT_ATOMIC_INTERLINEAR.tsv"


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sections(records):
    values = records.split("|")
    herbal = any(x.startswith("H") for x in values)
    bio = any(x.startswith("B") for x in values)
    return herbal, bio


def main():
    cards = load(POCKET / "HUNDRED_TENTH_173_CARD_POCKET.tsv")
    bridge_cards = [r for r in cards if r["teaching_tier"] == "BRIDGE_CARD"]
    events = load(EVENTS)
    by_card = defaultdict(list)
    for row in events:
        by_card[row["master_card_id"]].append(row)

    bridge_rows = []
    for row in bridge_cards:
        herbal, bio = sections(row["records"])
        if herbal and bio:
            status = "PORTABLE_EXACT_BRIDGE_CARD"
        elif herbal:
            status = "HERBAL_CARD_WITH_SHARED_BRIDGE_ATOM"
        else:
            status = "BIO_CARD_WITH_SHARED_BRIDGE_ATOM"
        bridge_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "semantic_atoms": row["semantic_atoms"],
            "short_default_de": row["short_default_de"],
            "records": row["records"],
            "event_count": row["event_count"],
            "bridge_status": status,
            "event_serials": "|".join(x["event_serial"] for x in by_card[row["master_card_id"]]),
            "teaching_instruction": (
                "teach the exact card in both prose sections" if status == "PORTABLE_EXACT_BRIDGE_CARD"
                else "teach the shared atom once, but practice this exact card only on its attested section tablet"
            ),
        })
    write_tsv("HUNDRED_FIFTEENTH_57_BRIDGE_CARD_AUDIT.tsv", bridge_rows)

    ecology = [r for r in load(ECOLOGY) if r["ecology_status"] == "THIN_CROSS_SECTION_BRIDGE"]
    atom_rows = []
    for atom in ecology:
        exact = [r for r in bridge_rows if atom["atom"] in r["semantic_atoms"].split("+") and r["bridge_status"] == "PORTABLE_EXACT_BRIDGE_CARD"]
        atom_rows.append({
            "bridge_atom": atom["atom"],
            "short_value_de": atom["atomic_default_de"],
            "herbal_occurrences": atom["herbal_occurrences"],
            "biological_occurrences": atom["biological_occurrences"],
            "exact_cross_section_card_count": str(len(exact)),
            "exact_cross_section_cards": "|".join(r["master_form"] for r in exact) if exact else "NONE",
            "teaching_decision": "PORTABLE_ATOM__SECTIONAL_CARDS_BY_EXAMPLE",
        })
    write_tsv("HUNDRED_FIFTEENTH_NINE_BRIDGE_ATOMS.tsv", atom_rows)

    revised = []
    bridge_map = {r["master_card_id"]: r for r in bridge_rows}
    for row in cards:
        if row["teaching_tier"] == "CORE_CARD":
            tier = "PORTABLE_CORE_CARD"
        elif row["teaching_tier"] == "SPECIALIST_OR_LEARNED_CARD":
            tier = "SPECIALIST_TABLET_CARD"
        else:
            status = bridge_map[row["master_card_id"]]["bridge_status"]
            tier = "PORTABLE_EXACT_BRIDGE_CARD" if status == "PORTABLE_EXACT_BRIDGE_CARD" else "SECTIONAL_CARD_WITH_SHARED_BRIDGE_ATOM"
        revised.append({**row, "revised_teaching_tier": tier})
    write_tsv("HUNDRED_FIFTEENTH_173_REVISED_TEACHING_DICTIONARY.tsv", revised)

    portable = [r for r in bridge_rows if r["bridge_status"] == "PORTABLE_EXACT_BRIDGE_CARD"]
    report = [
        "# Hundertfünfzehnte Runde: Brückenatom ist nicht Brückenkarte", "",
        "Die bisherige Bezeichnung ›57 Brückenkarten‹ war zu großzügig. Nur vier exakte Karten kommen",
        "wirklich in Herbal und Biological vor: `cheeky`, `chdy`, `chety` und `cheey`. Die anderen",
        "53 Karten teilen zwar einen der neun Brückenatome, sind als Ganzkarten aber sektionsgebunden:",
        "48 nur Biological, fünf nur Herbal.", "",
        "Die neun kurzen Beiträge bleiben brauchbar: Anteil, Lauf, Umsetzen, Ergebnis, Wärmen, Durchlass,",
        "Stufe, Abführen und Teilen. Der Lehrling lernt sie einmal; ihre konkreten Ganzkarten übt er jedoch",
        "auf der jeweiligen Herbal- oder Bade/Service-Tafel. So wird aus formaler Ähnlichkeit keine falsche",
        "portable Wortgleichheit.", "",
        "Die revidierte Lehrzählung ist 70 portable Kernkarten, vier portable exakte Brückenkarten,",
        "53 sektionsgebundene Karten mit gemeinsamem Brückenatom und 46 Spezialtafelkarten.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_FIFTEENTH_BRIDGE_REVISION_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    counts = {tier: sum(r["revised_teaching_tier"] == tier for r in revised) for tier in sorted({r["revised_teaching_tier"] for r in revised})}
    summary = {"status": "COMPLETE", "bridge_atoms": len(atom_rows), "former_bridge_cards": len(bridge_rows), "portable_exact_bridge_cards": len(portable), "revised_tiers": counts}
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
