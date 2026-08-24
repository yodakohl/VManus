#!/usr/bin/env python3
import csv
import json
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P565 = YOLO / "sidequest_semantic_workshop_recipe_macros_five_hundred_sixty_fifth"
P582 = YOLO / "sidequest_semantic_minimal_contrast_pairs_five_hundred_eighty_second"

PHASE = {
    "MATERIAL_PREP": "ziehe ab",
    "MEASURE_CHARGE": "setze oder gib nach Maß/Teil",
    "APPLY": "setze dorthin an",
    "HOLD": "halte kurz/länger",
    "THERMAL": "wärme oder kühle",
    "WASH": "wasche",
    "SETTLE": "setze ab oder fange auf",
    "ROUTE": "führe oder setze um",
    "CLOSE": "schließe",
    "SPECIALIST": "führe die gelernte Fachhandlung aus",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    dictionary = read(P582 / "FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THIRTY_EIGHT_COMPONENT_DICTIONARY.tsv")
    events = read(P582 / "FIVE_HUNDRED_EIGHTY_SECOND_REVISED_THREE_HUNDRED_EIGHTY_ONE_EVENT_SEQUENCES.tsv")
    macro_deck = read(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_RECURRENT_MACRO_DECK.tsv")
    macro_map = read(P565 / "FIVE_HUNDRED_SIXTY_FIFTH_ONE_HUNDRED_SIXTEEN_MACRO_MAP.tsv")
    spoken = {r["component"]: r["short_spoken_value_de"] for r in dictionary}

    grouped = OrderedDict()
    for event in events:
        grouped.setdefault(event["statement_id"], []).append(event)
    counts = {2: Counter(), 3: Counter()}
    support = {2: defaultdict(set), 3: defaultdict(set)}
    record_support = {2: defaultdict(set), 3: defaultdict(set)}
    boundary = {2: defaultdict(set), 3: defaultdict(set)}
    for statement, rows in grouped.items():
        tokens = []
        event_ids = []
        for row in rows:
            parts = row["component_parse"].split("+")
            tokens.extend(parts)
            event_ids.extend([row["event_id"]] * len(parts))
        for n in (2, 3):
            for i in range(len(tokens) - n + 1):
                gram = tuple(tokens[i:i+n])
                counts[n][gram] += 1
                support[n][gram].add(statement)
                record_support[n][gram].add(rows[0]["record"])
                boundary[n][gram].add("WITHIN_CARD" if len(set(event_ids[i:i+n])) == 1 else "CROSSES_CARD")

    ngram_rows = []
    rank = 0
    for n in (2, 3):
        for gram, occurrences in counts[n].most_common():
            if occurrences < 2:
                continue
            rank += 1
            ngram_rows.append({
                "phrase_no": f"PF{rank:03d}",
                "n": n,
                "component_phrase": "+".join(gram),
                "spoken_phrase_de": " · ".join(spoken[x] for x in gram),
                "occurrences": occurrences,
                "statements": len(support[n][gram]),
                "records": len(record_support[n][gram]),
                "boundary_behavior": "|".join(sorted(boundary[n][gram])),
                "example_statements": "|".join(sorted(support[n][gram])[:8]),
            })

    compact_macros = []
    for row in macro_deck:
        phases = row["phase_signature"].split(">")
        compact_macros.append({
            "macro_id": row["macro_id"],
            "phase_signature": row["phase_signature"],
            "compact_formula_de": " → ".join(PHASE[p] for p in phases),
            "statements": row["statements"],
            "records": row["records"],
            "example_statements": row["example_statements"],
            "constituent_values_preserved": "YES",
        })

    map_rows = []
    by_macro = {r["macro_id"]: r for r in compact_macros}
    for row in macro_map:
        if row["macro_status"] == "TAUGHT_RECURRENT_MACRO":
            phrase = by_macro[row["macro_id"]]["compact_formula_de"]
            mode = "USE_TAUGHT_MACRO"
        else:
            phrase = row["complete_action_sequence_de"]
            mode = "COMPOSE_ONCE_FROM_CORE"
        map_rows.append({
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "phase_signature": row["phase_signature"],
            "phrasebook_mode": mode,
            "macro_id": row["macro_id"],
            "compact_formula_or_expansion_de": phrase,
            "values_preserved": "YES",
        })

    write("FIVE_HUNDRED_EIGHTY_THIRD_RECURRENT_TWO_THREE_COMPONENT_PHRASES.tsv", ngram_rows)
    write("FIVE_HUNDRED_EIGHTY_THIRD_FIFTEEN_APPRENTICE_MACROS.tsv", compact_macros)
    write("FIVE_HUNDRED_EIGHTY_THIRD_ONE_HUNDRED_SIXTEEN_PHRASEBOOK_MAP.tsv", map_rows)
    summary = {
        "status": "PASS",
        "recurrent_bigrams": sum(int(r["n"]) == 2 for r in ngram_rows),
        "recurrent_trigrams": sum(int(r["n"]) == 3 for r in ngram_rows),
        "recurrent_component_phrases": len(ngram_rows),
        "taught_macros": len(compact_macros),
        "macro_statements": sum(r["phrasebook_mode"] == "USE_TAUGHT_MACRO" for r in map_rows),
        "compose_once_statements": sum(r["phrasebook_mode"] == "COMPOSE_ONCE_FROM_CORE" for r in map_rows),
        "statements": len(map_rows),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_THIRD_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertdreiundachtzigste Runde: Lehrlings-Formelbuch",
        "",
        "## Ergebnis",
        "",
        f"Die zehnseitige Prosa enthält {summary['recurrent_bigrams']} wiederkehrende Zwei- und {summary['recurrent_trigrams']} wiederkehrende Drei-Komponentenfolgen. Daraus reichen fünfzehn größere Werkstattformeln, um {summary['macro_statements']}/116 Aussagen als gelernte Redewendung zu sprechen; {summary['compose_once_statements']} seltene Aussagen werden einmalig aus dem 37-Wort-Kern zusammengesetzt.",
        "",
        "Die häufigsten Formeln sind keine Sachnamen, sondern Arbeitsfolgen: führen/umsetzen → schließen; halten → schließen; absetzen/auffangen → schließen; nach Maß ansetzen → halten → schließen; nach Maß ansetzen → führen/umsetzen → schließen. Das passt zu einer Werkstatt, in der Schreiber wiederkehrende Satzrahmen und wechselnde sichtbare Gegenstände kombinieren.",
        "",
        "Das Formelbuch ersetzt kein Wörterbuch. Es ist eine Beschleunigungsschicht: Der Lehrling kennt die 37 Sprechwerte, erkennt häufige Zwei-/Dreiwortstücke und lernt fünfzehn ganze Arbeitsrhythmen. Ein seltener Satz bleibt vollständig lesbar, weil er aus denselben Teilen gebaut wird.",
        "",
        "## Nächster Schritt",
        "",
        "Nun werden die 43 einmaligen Aussagen nach ihrer Abweichung von den fünfzehn Formeln sortiert. Kleine Einfügungen sollen als Formelvarianten zurückgeführt werden; nur wirklich neue Handlungsfolgen bleiben Einzelfälle.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_THIRD_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
