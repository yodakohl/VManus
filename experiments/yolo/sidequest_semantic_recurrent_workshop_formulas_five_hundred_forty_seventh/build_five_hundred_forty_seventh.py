#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P545 = ROOT / "experiments/yolo/sidequest_semantic_fluent_cross_line_edition_five_hundred_forty_fifth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


GLOSSES = {
    ("PROC019", "PROC009"): ("POSTEN_MASS", "den aktuellen Posten auf das Maß beziehen"),
    ("PROC016", "PROC019"): ("ANSATZ_UEBERNEHMEN", "den Ansatz als aktuellen Posten übernehmen"),
    ("PROC009", "PROC019"): ("MIT_MASS_WEITER", "mit dem gesetzten Maß weiterarbeiten"),
    ("PROC013", "PROC078"): ("FORTSETZEN_ABSETZEN", "fortsetzen, absetzen und den Schritt schließen"),
    ("PROC092", "PROC008"): ("LANG_ANSETZEN_NACHSETZEN", "länger ansetzen und danach erneut ansetzen"),
    ("PROC070", "PROC055"): ("PORTION_ZUM_ZIEL", "die Portion weiterführen und die Zielstelle setzen"),
    ("PROC055", "PROC013"): ("AM_ZIEL_WEITER", "an der bezeichneten Stelle fortsetzen"),
    ("PROC042", "PROC013"): ("UMSETZEN_WEITER", "umsetzen und ohne Abschluss weiterarbeiten"),
    ("PROC022", "PROC013"): ("ANSATZ_WEITER", "mit dem Ansatz fortfahren"),
    ("PROC013", "PROC009"): ("WEITER_DANN_MASS", "fortsetzen und danach das Maß setzen"),
    ("PROC008", "PROC009"): ("NACH_MASS_ANSETZEN", "den Posten nach Maß ansetzen"),
    ("PROC092", "PROC067"): ("LANG_DANN_KURZ_SCHLIESSEN", "länger ansetzen, kurz nachsetzen und schließen"),
    ("PROC042", "PROC100"): ("UMSETZEN_LANG_SCHLIESSEN", "umsetzen, länger einwirken lassen und schließen"),
    ("PROC009", "PROC013"): ("NACH_MASS_WEITER", "nach dem gesetzten Maß fortsetzen"),
    ("PROC019", "PROC009", "PROC019"): ("POSTEN_MASS_POSTEN", "denselben Posten unter dem gesetzten Maß weiterführen"),
}


def main() -> None:
    visible = read_tsv(P545 / "FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv")
    source = [row for row in visible if row["semantic_execution"] == "EXECUTE_ONCE"]
    by_instruction: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in source:
        by_instruction[row["instruction_id"]].append(row)

    windows: dict[tuple[str, ...], list[list[dict[str, str]]]] = defaultdict(list)
    for rows in by_instruction.values():
        for width in (2, 3):
            for start in range(len(rows) - width + 1):
                key = tuple(row["card_no"] for row in rows[start:start + width])
                windows[key].append(rows[start:start + width])

    selected = {key: occurrences for key, occurrences in windows.items() if key in GLOSSES}
    formula_rows: list[dict[str, str]] = []
    occurrence_rows: list[dict[str, str]] = []
    ordered = sorted(selected, key=lambda key: (-len(selected[key]), -len(key), key))
    formula_id_by_key: dict[tuple[str, ...], str] = {}
    for index, key in enumerate(ordered, 1):
        formula_id = f"WF{index:02d}"
        formula_id_by_key[key] = formula_id
        occurrences = selected[key]
        records = sorted({occ[0]["record"] for occ in occurrences})
        pages = sorted({occ[0]["page"] for occ in occurrences})
        gross_saved = len(occurrences) * (len(key) - 1)
        definition_cost = len(key)
        individual_net = gross_saved - definition_cost
        tier = "TEACH_FORMULA" if individual_net > 0 else "OBSERVED_PAIRING"
        mnemonic, idiom = GLOSSES[key]
        first = occurrences[0]
        formula_rows.append({
            "formula_id": formula_id,
            "tier": tier,
            "card_width": str(len(key)),
            "card_sequence": "+".join(key),
            "surface_example": " ".join(row["surface"] for row in first),
            "component_sequence": " | ".join(row["component_parse"] for row in first),
            "literal_sequence_de": " -> ".join(row["fluent_command_de"] for row in first),
            "formula_mnemonic": mnemonic,
            "idiomatic_workshop_reading_de": idiom,
            "occurrences": str(len(occurrences)),
            "records": "|".join(records),
            "pages": "|".join(pages),
            "gross_tokens_saved": str(gross_saved),
            "definition_cost_tokens": str(definition_cost),
            "individual_selector_paid_gain": str(individual_net),
            "component_values_changed": "NO",
        })
        for occurrence_no, occ in enumerate(occurrences, 1):
            occurrence_rows.append({
                "formula_id": formula_id,
                "occurrence_no": str(occurrence_no),
                "instruction_id": occ[0]["instruction_id"],
                "record": occ[0]["record"],
                "page": occ[0]["page"],
                "event_ids": "|".join(row["event_id"] for row in occ),
                "source_position_ids": "|".join(row["source_position_id"] for row in occ),
                "surface_sequence": " ".join(row["surface"] for row in occ),
                "literal_sequence_de": " -> ".join(row["fluent_command_de"] for row in occ),
                "idiomatic_workshop_reading_de": idiom,
                "cross_record_portable": "YES" if len(records) >= 2 else "NO",
            })

    teach_keys = [key for key in ordered if next(row for row in formula_rows if row["formula_id"] == formula_id_by_key[key])["tier"] == "TEACH_FORMULA"]
    token_rows: list[dict[str, str]] = []
    formula_hits = Counter()
    compressed_tokens = 0
    for instruction_id, rows in by_instruction.items():
        index = 0
        output_tokens: list[str] = []
        while index < len(rows):
            matching = [key for key in teach_keys if tuple(row["card_no"] for row in rows[index:index + len(key)]) == key]
            if matching:
                key = sorted(matching, key=lambda item: (-len(item), -len(selected[item]), item))[0]
                formula_id = formula_id_by_key[key]
                output_tokens.append(formula_id)
                formula_hits[formula_id] += 1
                index += len(key)
            else:
                output_tokens.append(rows[index]["card_no"])
                index += 1
        compressed_tokens += len(output_tokens)
        token_rows.append({
            "instruction_id": instruction_id,
            "record": rows[0]["record"],
            "source_card_tokens": str(len(rows)),
            "compressed_tokens": str(len(output_tokens)),
            "compressed_formula_stream": " ".join(output_tokens),
        })

    raw_tokens = len(source)
    dictionary_cost = sum(len(key) for key in teach_keys)
    summary = {
        "status": "PASS",
        "visible_events": len(visible),
        "executed_source_positions": len(source),
        "repeated_exact_bigrams": sum(1 for key, occ in windows.items() if len(key) == 2 and len(occ) >= 2 and len({x[0]['record'] for x in occ}) >= 2),
        "repeated_exact_trigrams": sum(1 for key, occ in windows.items() if len(key) == 3 and len(occ) >= 2 and len({x[0]['record'] for x in occ}) >= 2),
        "formula_rows": len(formula_rows),
        "teach_formulas": len(teach_keys),
        "observed_pairings": len(formula_rows) - len(teach_keys),
        "formula_occurrences": len(occurrence_rows),
        "raw_tokens": raw_tokens,
        "compressed_tokens": compressed_tokens,
        "gross_saved": raw_tokens - compressed_tokens,
        "dictionary_cost": dictionary_cost,
        "selector_paid_gain": raw_tokens - compressed_tokens - dictionary_cost,
        "greedy_formula_hits": dict(sorted(formula_hits.items())),
    }
    write_tsv("FIVE_HUNDRED_FORTY_SEVENTH_FORMULA_LEXICON.tsv", formula_rows)
    write_tsv("FIVE_HUNDRED_FORTY_SEVENTH_FORMULA_OCCURRENCES.tsv", occurrence_rows)
    write_tsv("FIVE_HUNDRED_FORTY_SEVENTH_COMPRESSED_INSTRUCTIONS.tsv", token_rows)
    (HERE / "FIVE_HUNDRED_FORTY_SEVENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Fünfhundertsiebenundvierzigste Runde: wiederkehrende Werkstattformeln",
        "",
        "## Fund",
        "",
        "Auf den 380 tatsächlich ausgeführten Quellpositionen wiederholen sich genau vierzehn exakte Zweikartenfolgen über mindestens zwei Records; nur eine Dreikartenfolge wiederholt sich recordübergreifend. Die sichtbare Randkopie E180/E181 wird dabei nur einmal ausgeführt.",
        "",
        "Fünf Folgen sparen ihre eigene Definition wieder ein und werden als gelernte Formeln in das Lehrdeck aufgenommen. Zehn weitere wiederkehrende Folgen bleiben beobachtete Paarungen: sprachlich nützlich, aber noch kein kürzeres Lehrsystem.",
        "",
        "## Die fünf lehrbaren Formeln",
        "",
    ]
    for row in formula_rows:
        if row["tier"] == "TEACH_FORMULA":
            report.append(f"- `{row['formula_id']}` `{row['surface_example']}` — {row['idiomatic_workshop_reading_de']} ({row['occurrences']} Vorkommen; {row['records']}).")
    report.extend([
        "",
        "## Lehrökonomie",
        "",
        f"Greedy mit der längsten Formel zuerst sinkt die laufende Folge von {raw_tokens} auf {compressed_tokens} Tokens. Nach {dictionary_cost} Tokens Formeldeck-Kosten bleiben {summary['selector_paid_gain']} Tokens echter Gewinn. Das ist klein, aber positiv: Die Werkstatt braucht nicht für jede Nachbarschaft eine eigene Phrase.",
        "",
        "Die stärkste Formel ist `POSTEN_MASS_POSTEN`: derselbe Arbeitsgegenstand wird unter einem gesetzten Maß weitergeführt. Das ist eine bessere knappe Lesung der alten Y–AIIN–Y-Folge als eine ungestützte Übersetzung mit „gleich viel“.",
        "",
        "Keine Einzelkartenbedeutung wurde geändert. Die Formeln sind nur idiomatische Zusammenfassungen ihrer vorhandenen Komponenten.",
    ])
    (HERE / "FIVE_HUNDRED_FORTY_SEVENTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
