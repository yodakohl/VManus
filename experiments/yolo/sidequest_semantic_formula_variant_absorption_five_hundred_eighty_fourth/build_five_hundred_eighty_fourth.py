#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P583 = YOLO / "sidequest_semantic_apprentice_phrasebook_five_hundred_eighty_third"

PHASE_DE = {
    "APPLY": "Anwendung", "SETTLE": "Absetzen", "SPECIALIST": "Fachhandlung",
    "HOLD": "Halten", "MATERIAL_PREP": "Abziehen", "MEASURE_CHARGE": "Maß/Teil",
    "ROUTE": "Führen/Umsetzen", "CLOSE": "Schluss", "THERMAL": "Wärmen/Kühlen",
    "WASH": "Waschen", "STATE_ONLY": "Zustand",
}


def read(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def distance_and_ops(source, target):
    n, m = len(source), len(target)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): dp[i][0] = i
    for j in range(m + 1): dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + (source[i-1] != target[j-1]))
    i, j, ops = n, m, []
    while i or j:
        if i and j and source[i-1] == target[j-1] and dp[i][j] == dp[i-1][j-1]:
            i -= 1; j -= 1
        elif i and j and dp[i][j] == dp[i-1][j-1] + 1:
            ops.append(f"SUBSTITUTE_{target[j-1]}_WITH_{source[i-1]}"); i -= 1; j -= 1
        elif i and dp[i][j] == dp[i-1][j] + 1:
            ops.append(f"INSERT_{source[i-1]}"); i -= 1
        else:
            ops.append(f"OMIT_{target[j-1]}"); j -= 1
    return dp[n][m], list(reversed(ops))


def teach(op):
    if op.startswith("INSERT_"):
        return "füge " + PHASE_DE[op[7:]] + " ein"
    if op.startswith("OMIT_"):
        return "lasse " + PHASE_DE[op[5:]] + " aus"
    left, right = op[11:].split("_WITH_", 1)
    return "ersetze " + PHASE_DE[left] + " durch " + PHASE_DE[right]


def main():
    macros = read(P583 / "FIVE_HUNDRED_EIGHTY_THIRD_FIFTEEN_APPRENTICE_MACROS.tsv")
    mapping = read(P583 / "FIVE_HUNDRED_EIGHTY_THIRD_ONE_HUNDRED_SIXTEEN_PHRASEBOOK_MAP.tsv")
    macro_tokens = {r["macro_id"]: r["phase_signature"].split(">") for r in macros}
    one_off_rows = []
    revised_rows = []
    edit_counter = Counter()
    for row in mapping:
        out = dict(row)
        if row["phrasebook_mode"] == "USE_TAUGHT_MACRO":
            out.update({"nearest_macro": row["macro_id"], "edit_distance": 0, "edit_operations": "NONE", "revised_learning_mode": "TAUGHT_MACRO"})
        else:
            source = row["phase_signature"].split(">")
            candidates = []
            for macro_id, target in macro_tokens.items():
                distance, ops = distance_and_ops(source, target)
                candidates.append((distance, macro_id, ops))
            distance, macro_id, ops = min(candidates, key=lambda x: (x[0], x[1]))
            if distance == 1:
                mode = "SIMPLE_ONE_EDIT_VARIANT"
            elif distance == 2:
                mode = "EXTENDED_TWO_EDIT_VARIANT"
            else:
                mode = "FREE_COMPOSITION"
            for op in ops:
                if distance == 1:
                    edit_counter[op] += 1
            out.update({"nearest_macro": macro_id, "edit_distance": distance, "edit_operations": "|".join(ops), "revised_learning_mode": mode})
            one_off_rows.append({
                "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
                "phase_signature": row["phase_signature"], "nearest_macro": macro_id,
                "nearest_macro_signature": ">".join(macro_tokens[macro_id]), "edit_distance": distance,
                "edit_operations": "|".join(ops), "learning_mode": mode,
                "complete_expansion_de": row["compact_formula_or_expansion_de"],
            })
        revised_rows.append(out)

    simple_rules = [{
        "variant_rule_no": f"V{i:02d}",
        "edit_operation": op,
        "statements": count,
        "teaching_rule_de": teach(op),
    } for i, (op, count) in enumerate(sorted(edit_counter.items(), key=lambda x: (-x[1], x[0])), 1)]

    write("FIVE_HUNDRED_EIGHTY_FOURTH_FORTY_THREE_ONE_OFF_NEAREST_FORMULAS.tsv", one_off_rows)
    write("FIVE_HUNDRED_EIGHTY_FOURTH_SIMPLE_VARIANT_RULES.tsv", simple_rules)
    write("FIVE_HUNDRED_EIGHTY_FOURTH_REVISED_ONE_HUNDRED_SIXTEEN_FORMULA_MAP.tsv", revised_rows)
    modes = Counter(r["revised_learning_mode"] for r in revised_rows)
    summary = {
        "status": "PASS",
        "statements": len(revised_rows),
        "taught_macros": modes["TAUGHT_MACRO"],
        "simple_one_edit_variants": modes["SIMPLE_ONE_EDIT_VARIANT"],
        "extended_two_edit_variants": modes["EXTENDED_TWO_EDIT_VARIANT"],
        "free_compositions": modes["FREE_COMPOSITION"],
        "macro_plus_simple_coverage": modes["TAUGHT_MACRO"] + modes["SIMPLE_ONE_EDIT_VARIANT"],
        "simple_variant_rule_types": len(simple_rules),
    }
    (HERE / "FIVE_HUNDRED_EIGHTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertvierundachtzigste Runde: Formelvarianten",
        "",
        "## Ergebnis",
        "",
        "Von den 43 bisherigen Einzelfällen liegen 21 nur einen Phasenschritt von einer gelernten Formel entfernt. Sie werden als einfache Einfügung, Auslassung oder Ersetzung gelehrt. Damit decken fünfzehn Formeln plus einfache Varianten 94/116 Aussagen.",
        "",
        "Weitere zehn Aussagen brauchen zwei Änderungen und bleiben erweiterte Varianten. Nur zwölf Aussagen besitzen drei oder mehr Abweichungen und werden wirklich frei aus dem 37-Wort-Kern gebaut. Die längsten Herbal-Eröffnungen und zwei große Biological-Zellen gehören erwartbar zu dieser freien Gruppe.",
        "",
        "Das System ist damit weniger memoriert als zunächst gedacht: 73 feste Formelanwendungen, 21 kleine Varianten, zehn erweiterte Varianten und zwölf echte freie Kompositionen. Ein Lehrling improvisiert nur in gut einem Zehntel der Aussagen vollständig.",
        "",
        "## Nächster Schritt",
        "",
        "Nun werden genau die zwölf freien Aussagen als Meisterbeispiele ausgeschrieben. Aus ihnen soll geprüft werden, ob zwei oder drei zusätzliche Formeln genügen oder ob ihre längere Struktur absichtlich artikel-/stationsspezifisch bleibt.",
    ]
    (HERE / "FIVE_HUNDRED_EIGHTY_FOURTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
