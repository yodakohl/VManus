#!/usr/bin/env python3
"""Derive compact sequence rules for the 17 shared Herbal/Bio cards."""

from __future__ import annotations

import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
LEXICON = ROOT / "experiments/yolo/sidequest_semantic_handoff_lexicon_three_hundred_twentieth/THREE_HUNDRED_TWENTIETH_17_SHARED_HANDOFF_WORDS.tsv"

SLOTS = {
    "Sollstellung": "ENTRY_CONTROL",
    "Zieleinsatz": "ENTRY_CONTROL",
    "Ansatz": "ENTRY_ITEM",
    "Folgeposten": "ENTRY_ITEM",
    "Diesposten": "ARGUMENT_ITEM",
    "Stelle": "ARGUMENT_TARGET",
    "Gleichvorrat": "ARGUMENT_SOURCE",
    "Sollmaß": "ARGUMENT_MEASURE",
    "Klarauszug": "ARGUMENT_PRODUCT",
    "Zerkleinern": "ACTION",
    "Umsetzen": "ACTION",
    "Einsetzen": "ACTION",
    "Langwärme": "ACTION_STATE",
    "Fortsetzung": "CONTINUATION",
    "Fortsetzungsansatz": "CONTINUATION_ITEM",
    "Bereit": "STATE",
    "Fortschluss": "CLOSE",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def band(value: float) -> str:
    if value <= 0.25:
        return "START"
    if value >= 0.75:
        return "END"
    return "MIDDLE"


def main() -> None:
    ledger = read(LEDGER)
    atom = {x["joint_tuple_id"]: x["handoff_atomic_value_de"] for x in read(LEXICON)}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        by_statement[row["statement_id"]].append(row)

    direct2: Counter[tuple[str, str]] = Counter()
    direct3: Counter[tuple[str, str, str]] = Counter()
    skeleton2: Counter[tuple[str, str]] = Counter()
    skeleton3: Counter[tuple[str, str, str]] = Counter()
    positions: dict[str, list[float]] = defaultdict(list)
    sections: dict[str, Counter[str]] = defaultdict(Counter)
    for statement in by_statement.values():
        visible = [atom.get(x["joint_tuple_id"]) for x in statement]
        skeleton = [x for x in visible if x]
        for i, value in enumerate(visible):
            if value:
                pos = i / (len(visible) - 1) if len(visible) > 1 else 0.5
                positions[value].append(pos)
                sections[value]["HERBAL" if statement[0]["record_unit_id"].startswith("H") else "BIO"] += 1
        for a, b in zip(visible, visible[1:]):
            if a and b:
                direct2[(a, b)] += 1
        for a, b, c in zip(visible, visible[1:], visible[2:]):
            if a and b and c:
                direct3[(a, b, c)] += 1
        for a, b in zip(skeleton, skeleton[1:]):
            skeleton2[(a, b)] += 1
        for a, b, c in zip(skeleton, skeleton[1:], skeleton[2:]):
            skeleton3[(a, b, c)] += 1

    ngrams = []
    for mode, counter in [
        ("DIRECT_BIGRAM", direct2),
        ("DIRECT_TRIGRAM", direct3),
        ("SHARED_SKELETON_BIGRAM", skeleton2),
        ("SHARED_SKELETON_TRIGRAM", skeleton3),
    ]:
        for values, count in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
            ngrams.append(
                {
                    "mode": mode,
                    "sequence": " → ".join(values),
                    "slot_sequence": " → ".join(SLOTS[x] for x in values),
                    "count": str(count),
                    "recurrent": "YES" if count >= 2 else "NO",
                }
            )

    profiles = []
    for value in sorted(positions, key=lambda x: (statistics.median(positions[x]), x)):
        vals = positions[value]
        bands = Counter(band(x) for x in vals)
        profiles.append(
            {
                "atomic_value_de": value,
                "teaching_slot": SLOTS[value],
                "events": str(len(vals)),
                "herbal_events": str(sections[value]["HERBAL"]),
                "bio_events": str(sections[value]["BIO"]),
                "median_statement_position": f"{statistics.median(vals):.3f}",
                "start_events": str(bands["START"]),
                "middle_events": str(bands["MIDDLE"]),
                "end_events": str(bands["END"]),
                "apprentice_rule": {
                    "ENTRY_CONTROL": "Setze zuerst Arbeitsstufe oder Zieleinsatz.",
                    "ENTRY_ITEM": "Eröffne einen Ansatz oder Folgeposten.",
                    "ARGUMENT_ITEM": "Halte den aktuellen Posten aktiv.",
                    "ARGUMENT_TARGET": "Nenne die adressierte Stelle.",
                    "ARGUMENT_SOURCE": "Binde den vorigen oder gleichen Vorrat.",
                    "ARGUMENT_MEASURE": "Setze oder prüfe das Sollmaß.",
                    "ARGUMENT_PRODUCT": "Binde den klaren Auszug als Arbeitsgut.",
                    "ACTION": "Führe die sichtbare Arbeit aus.",
                    "ACTION_STATE": "Halte den Posten länger warm.",
                    "CONTINUATION": "Führe den laufenden Gang weiter.",
                    "CONTINUATION_ITEM": "Behalte den fortgesetzten Ansatz.",
                    "STATE": "Markiere den Posten als bereit.",
                    "CLOSE": "Setze Fortsetzung und Abschluss gemeinsam.",
                }[SLOTS[value]],
            }
        )

    rules = [
        {"rule_id": "R1", "rule": "ENTRY_OR_ITEM_FIRST", "expansion": "[Sollstellung|Zieleinsatz|Ansatz|Folgeposten] eröffnet einen neuen lokalen Arbeitsbogen."},
        {"rule_id": "R2", "rule": "ARGUMENTS_CLUSTER_FLEXIBLY", "expansion": "Diesposten, Stelle, Gleichvorrat, Sollmaß und Klarauszug können vor oder nach einer Handlung stehen."},
        {"rule_id": "R3", "rule": "ACTION_THEN_CONTINUE", "expansion": "Umsetzen oder Einsetzen wird häufig von Fortsetzung gefolgt."},
        {"rule_id": "R4", "rule": "ITEM_MEASURE_ITEM_FRAME", "expansion": "Diesposten → Sollmaß → Diesposten bedeutet: diesen Posten messen und als denselben aktiven Posten behalten."},
        {"rule_id": "R5", "rule": "CONTINUATION_BRACKETS_BATCH", "expansion": "Fortsetzung → Fortsetzungsansatz → Fortsetzung rahmt einen weiterlaufenden Ansatz."},
        {"rule_id": "R6", "rule": "STATE_OR_CLOSE_LAST_WHEN_PRESENT", "expansion": "Bereit kann den Bogen offen übergeben; Fortschluss beendet ihn."},
        {"rule_id": "R7", "rule": "PARATAXIS_AND_LOOPING_ALLOWED", "expansion": "Nach Fortsetzung darf ein neues Argument oder eine neue Handlung folgen; die Ordnung ist keine starre Satzschablone."},
    ]

    write("THREE_HUNDRED_TWENTY_THIRD_ALL_SHARED_NGRAMS.tsv", ngrams)
    write("THREE_HUNDRED_TWENTY_THIRD_17_POSITION_PROFILES.tsv", profiles)
    write("THREE_HUNDRED_TWENTY_THIRD_SEVEN_WRITING_RULES.tsv", rules)
    names = [
        "THREE_HUNDRED_TWENTY_THIRD_ALL_SHARED_NGRAMS.tsv",
        "THREE_HUNDRED_TWENTY_THIRD_17_POSITION_PROFILES.tsv",
        "THREE_HUNDRED_TWENTY_THIRD_SEVEN_WRITING_RULES.tsv",
    ]
    summary = {
        "status": "PASS",
        "shared_events": sum(len(x) for x in positions.values()),
        "direct_bigrams": sum(direct2.values()),
        "direct_trigrams": sum(direct3.values()),
        "skeleton_bigrams": sum(skeleton2.values()),
        "skeleton_trigrams": sum(skeleton3.values()),
        "recurrent_direct_bigrams": sum(v >= 2 for v in direct2.values()),
        "recurrent_direct_trigrams": sum(v >= 2 for v in direct3.values()),
        "hashes": {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names},
    }
    (HERE / "THREE_HUNDRED_TWENTY_THIRD_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
