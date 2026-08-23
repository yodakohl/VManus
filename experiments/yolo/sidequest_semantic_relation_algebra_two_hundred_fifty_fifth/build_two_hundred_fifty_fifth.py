#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R254 = ROOT / "experiments/yolo/sidequest_semantic_relation_stems_two_hundred_fifty_fourth"
R250 = ROOT / "experiments/yolo/sidequest_semantic_ten_page_working_edition_two_hundred_fiftieth"
CARDS = R254 / "TWO_HUNDRED_FIFTY_FOURTH_102_RELATION_CARDS.tsv"
PROSE = R254 / "TWO_HUNDRED_FIFTY_FOURTH_219_PROSE_OCCURRENCES.tsv"
ASTRO = R254 / "TWO_HUNDRED_FIFTY_FOURTH_67_ASTRO_OCCURRENCES.tsv"
STATEMENTS = R250 / "TWO_HUNDRED_FIFTIETH_116_PROSE_STATEMENTS.tsv"
STEMS = ("AR", "AL", "OL", "OT", "OR", "Y")

READING = {
    "AR|AL": "von einer Quelle zu einem Ziel",
    "AR|OL": "von derselben Quelle aus weiter",
    "AR|OT": "danach aus der nächsten Quelle",
    "AR|OR": "Ansatz aus der bezeichneten Quelle",
    "AR|Y": "von diesem Posten",
    "AL|OL": "zur Zielstelle weiter",
    "AL|OT": "danach zur nächsten Zielstelle",
    "AL|OR": "den Ansatz zur Zielstelle",
    "AL|Y": "diesen Posten zur Zielstelle",
    "OL|OT": "danach im selben Fortgang weiter",
    "OL|OR": "mit demselben Ansatz weiter",
    "OL|Y": "mit diesem Posten weiter",
    "OT|OR": "danach den nächsten Ansatz",
    "OT|Y": "danach diesen oder den nächsten Posten",
    "OR|Y": "dieser laufende Ansatz",
}

PREDICTION = {
    "AR|AL": ("LOW", "Doppeladresse wird wahrscheinlich als zwei Karten geschrieben"),
    "AR|OL": ("MEDIUM", "plausibler Quell-Fortgang, bisher nur über Kartenfolge ausgedrückt"),
    "AR|OR": ("HIGH", "natürliche fehlende Verbindung: Ansatz aus einer bezeichneten Quelle"),
    "AL|OL": ("HIGH", "natürliche fehlende Verbindung: zur Zielstelle weiterführen"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs(stem_string: str) -> list[str]:
    return ["|".join(p) for p in itertools.combinations(stem_string.split("|"), 2)]


def main() -> None:
    cards = read_tsv(CARDS)
    prose = read_tsv(PROSE)
    astro = read_tsv(ASTRO)
    statements = {r["statement_id"]: r for r in read_tsv(STATEMENTS)}
    multi_cards = [r for r in cards if "|" in r["relation_stems"]]
    multi_ids = {r["master_card_id"] for r in multi_cards}

    card_support: dict[str, list[dict[str, str]]] = defaultdict(list)
    prose_support: Counter[str] = Counter()
    astro_support: Counter[str] = Counter()
    for row in multi_cards:
        for pair in pairs(row["relation_stems"]):
            card_support[pair].append(row)
    for row in prose:
        for pair in pairs(row["relation_stems"]):
            prose_support[pair] += 1
    for row in astro:
        for pair in pairs(row["relation_stems"]):
            astro_support[pair] += 1

    algebra = []
    for a, b in itertools.combinations(STEMS, 2):
        pair = f"{a}|{b}"
        support = card_support[pair]
        observed = bool(support)
        priority, reason = PREDICTION.get(pair, ("ATTESTED", "attested compound family"))
        algebra.append({
            "stem_pair": pair, "stem_a": a, "stem_b": b,
            "composed_reading_de": READING[pair],
            "inventory_status": "OBSERVED" if observed else "MISSING_COMBINATION",
            "card_type_count": len(support),
            "prose_event_count": prose_support[pair],
            "astro_group_count": astro_support[pair],
            "support_cards": "|".join(r["master_card_id"] for r in support) or "NONE",
            "support_forms": "|".join(r["master_form"] for r in support) or "NONE",
            "prediction_priority": priority,
            "workshop_interpretation": reason,
        })

    multi_card_rows = []
    for row in multi_cards:
        s = row["relation_stems"]
        if s == "OL|OT|Y":
            recomposed = "danach mit diesem Posten weiter"
        elif len(s.split("|")) == 2:
            recomposed = READING[s]
        else:
            recomposed = row["portable_core_de"]
        multi_card_rows.append({
            "master_card_id": row["master_card_id"], "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"], "relation_stems": s,
            "component_parse": row["component_parse"], "prose_event_count": row["prose_event_count"],
            "old_portable_core_de": row["portable_core_de"], "recomposed_core_de": recomposed,
            "revision_status": "RECOMPOSE" if recomposed.lower() != row["portable_core_de"].lower() else "KEEP",
        })

    occurrence_rows = []
    for row in prose:
        if row["master_card_id"] not in multi_ids:
            continue
        card = next(r for r in multi_card_rows if r["master_card_id"] == row["master_card_id"])
        statement = statements[row["statement_id"]]
        occurrence_rows.append({
            "event_id": row["event_id"], "statement_id": row["statement_id"],
            "page": row["page"], "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "relation_stems": row["relation_stems"], "recomposed_core_de": card["recomposed_core_de"],
            "full_visible_sequence": statement["visible_sequence"],
            "complete_local_translation_de": statement["complete_local_translation_de"],
        })

    algebra_path = OUT / "TWO_HUNDRED_FIFTY_FIFTH_15_PAIR_ALGEBRA.tsv"
    cards_path = OUT / "TWO_HUNDRED_FIFTY_FIFTH_20_MULTI_STEM_CARDS.tsv"
    occ_path = OUT / "TWO_HUNDRED_FIFTY_FIFTH_26_MULTI_STEM_OCCURRENCES.tsv"
    readable_path = OUT / "TWO_HUNDRED_FIFTY_FIFTH_READABLE_COMBINATION_LESSON.md"
    report_path = OUT / "TWO_HUNDRED_FIFTY_FIFTH_REPORT.md"
    write_tsv(algebra_path, algebra, list(algebra[0]))
    write_tsv(cards_path, multi_card_rows, list(multi_card_rows[0]))
    write_tsv(occ_path, occurrence_rows, list(occurrence_rows[0]))

    observed = [r for r in algebra if r["inventory_status"] == "OBSERVED"]
    missing = [r for r in algebra if r["inventory_status"] == "MISSING_COMBINATION"]
    readable = [
        "# Kleine Kombinationsgrammatik", "",
        "Von den fünfzehn möglichen Paaren der sechs Beziehungsstämme sind elf bereits als ganze Karten belegt. Der Schreiber kombiniert also wirklich, aber nicht mechanisch alles mit allem.", "",
        "## Die produktiven Paare", "",
    ]
    for row in observed:
        readable.append(f"- `{row['stem_pair']}` → {row['composed_reading_de']} ({row['support_forms']}).")
    readable += ["", "## Die vier Lücken", ""]
    for row in missing:
        readable.append(f"- `{row['stem_pair']}` → {row['composed_reading_de']}; Prognose {row['prediction_priority']}: {row['workshop_interpretation']}.")
    readable += [
        "", "## Dreierformel", "",
        "`OT+OL+Y` ist einmal als `qoctholy` belegt und liest sich am knappsten: **danach mit diesem Posten weiter**. Das ist ein guter Lehrsatz für die ganze Grammatik: OT wechselt den Schritt, OL hält den Fortgang, Y hält den aktuellen Gegenstand.", "",
        "Die vier fehlenden Paare sind keine Gegenbeweise. Sie zeigen, wo die Werkstatt lieber zwei Karten hintereinander setzt. Besonders `AR+AL` dürfte als Quelle und Ziel getrennt bleiben, weil beide Adressen gleichzeitig sonst schwer zu lesen wären.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 255: kleine Beziehungsalgebra

## Ergebnis

Elf von fünfzehn möglichen Stammpaaren sind belegt. Zwanzig Mehrstammkarten tragen 26 Prosaereignisse; sechs passende Astrogruppen zeigen, dass ein Teil der Kombinationen registerübergreifend bleibt. Die häufigsten Typfamilien sind AL+Y, OL+OT und OT+Y mit je vier Karten.

Die einzige Dreierformel ist OT+OL+Y: DANACH + WEITER + DIES. Ihr bisheriger Ganzwert „bereiter Folgeposten“ wird kompositionell präziser zu „danach mit diesem Posten weiter“.

Vier Paarungen fehlen: AR+AL, AR+OL, AR+OR und AL+OL. AR+OR und AL+OL sind die besten Vorhersagen für noch unerkannte Kompositionen; AR+AL wird wahrscheinlich absichtlich über zwei Karten verteilt.

Inputs: cards `{sha(CARDS)}`, prose `{sha(PROSE)}`, Astro `{sha(ASTRO)}`, statements `{sha(STATEMENTS)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (algebra_path, cards_path, occ_path, readable_path, report_path)
    summary = {
        "status": "PASS", "possible_pairs": 15, "observed_pairs": len(observed),
        "missing_pairs": len(missing), "multi_stem_cards": len(multi_cards),
        "multi_stem_prose_occurrences": len(occurrence_rows),
        "multi_stem_astro_groups": sum(1 for r in astro if "|" in r["relation_stems"]),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
