#!/usr/bin/env python3
"""Build the Pass-1010 OT-grade and concept-review artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P1009 = ROOT / "experiments/yolo/sidequest_semantic_twenty_two_page_statement_consolidation_one_thousand_ninth"
P1002 = ROOT / "experiments/yolo/sidequest_semantic_dual_layer_release_one_thousand_second"

STATEMENTS = P1009 / "PASS1009_627_STATEMENT_EDITION.tsv"
EVENTS = P1009 / "PASS1009_4581_EVENT_LEDGER.tsv"
ELLIPSES = P1009 / "PASS1009_27_ELLIPSIS_RESOLUTIONS.tsv"
CODEBOOK = P1002 / "PASS1002_175_CURRENT_CODEBOOK.tsv"

GRADE_FROM_OLD = {"KURZ": "E", "LÄNGER": "EE", "VOLLSTÄNDIG": "EEE"}
GRADE_RANK = {"E": 1, "EE": 2, "EEE": 3}
GRADE_ATOMIC = {"E": "GRAD I", "EE": "GRAD II", "EEE": "GRAD III"}
GRADE_LOCAL = {
    "E": "kurz, leicht oder einmal",
    "EE": "länger, stärker oder als weiterer Durchgang",
    "EEE": "vollständig oder bis zum Abschluss",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", lineterminator="\n", fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def grade_tokens(component_sequence: str) -> list[str]:
    answer: list[str] = []
    for component in component_sequence.split(" | "):
        answer.extend(token for token in component.split("+") if token in GRADE_RANK)
    return answer


def replace_grade_words(text: str) -> str:
    replacements = {"KURZ": "GRAD I", "LÄNGER": "GRAD II", "VOLL": "GRAD III"}
    for old, new in replacements.items():
        text = re.sub(rf"(?<![A-ZÄÖÜ]){old}(?![A-ZÄÖÜ])", new, text)
    return text


def transition(source: str, target: str) -> str:
    if source == "NONE":
        return "FIRST_ASSIGNED"
    if source == target:
        return "SAME"
    if GRADE_RANK[target] > GRADE_RANK[source]:
        return "RAISED"
    return "LOWERED"


statements = read_tsv(STATEMENTS)
events = read_tsv(EVENTS)
ellipses = read_tsv(ELLIPSES)
codebook = read_tsv(CODEBOOK)
statement_by_id = {row["statement_id"]: row for row in statements}

action_rows = [row for row in ellipses if row["resolution_kind"] == "ANAPHORIC_ACTION_INHERITANCE"]
assert len(action_rows) == 24

chain_rows: list[dict[str, object]] = []
transition_counts: Counter[str] = Counter()
operation_grade: dict[str, Counter[str]] = defaultdict(Counter)
operation_pages: dict[str, set[str]] = defaultdict(set)
operation_owners: dict[str, set[str]] = defaultdict(set)

for row in action_rows:
    source = statement_by_id[row["inheritance_source_statement_id"]]
    source_grades = grade_tokens(source["component_sequence"])
    source_grade = source_grades[-1] if source_grades else "NONE"
    target_grade = GRADE_FROM_OLD[row["grade_de"]]
    grade_transition = transition(source_grade, target_grade)
    transition_counts[grade_transition] += 1
    operation = row["inherited_operation_de"]
    operation_grade[operation][target_grade] += 1
    operation_pages[operation].add(row["physical_page"])
    operation_owners[operation].add(row["owner_id"])
    atomic = f"DANACH · {operation} · {GRADE_ATOMIC[target_grade]} · SCHLUSS"
    fluent_grade = GRADE_ATOMIC[target_grade].replace("GRAD", "Grad")
    fluent = (
        f"{row['physical_page']} / {row['owner_id']}: danach im {fluent_grade} "
        f"{operation.lower()}; den Teilgang schließen."
    )
    chain_rows.append(
        {
            "statement_id": row["statement_id"],
            "physical_page": row["physical_page"],
            "owner_id": row["owner_id"],
            "locus_span": row["locus_span"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "inherited_operation_de": operation,
            "source_statement_id": row["inheritance_source_statement_id"],
            "source_surface": source["surface_sequence"],
            "source_rightmost_grade": source_grade,
            "target_grade": target_grade,
            "grade_transition": grade_transition,
            "atomic_workshop_reading_de": atomic,
            "local_grade_range_de": GRADE_LOCAL[target_grade],
            "grade_neutral_fluent_de": fluent,
        }
    )

chain_fields = list(chain_rows[0])
write_tsv(OUT / "PASS1010_24_OT_GRADE_CHAINS.tsv", chain_rows, chain_fields)

matrix_rows: list[dict[str, object]] = []
for operation in sorted(operation_grade):
    counts = operation_grade[operation]
    used = [grade for grade in ("E", "EE", "EEE") if counts[grade]]
    matrix_rows.append(
        {
            "inherited_operation_de": operation,
            "grade_E_count": counts["E"],
            "grade_EE_count": counts["EE"],
            "grade_EEE_count": counts["EEE"],
            "total": sum(counts.values()),
            "physical_pages": "|".join(sorted(operation_pages[operation])),
            "owner_count": len(operation_owners[operation]),
            "grade_contrast": "MULTIPLE_GRADES" if len(used) > 1 else "ONE_GRADE_OBSERVED",
            "working_reading_de": " / ".join(GRADE_ATOMIC[grade] for grade in used),
        }
    )
write_tsv(OUT / "PASS1010_OPERATION_GRADE_MATRIX.tsv", matrix_rows, list(matrix_rows[0]))

grid_recipes = [
    ("E", "Y", "OT+E+Y"),
    ("E", "DY", "OT+E+DY"),
    ("EE", "Y", "OT+EE+Y"),
    ("EE", "DY", "OT+EE+DY"),
    ("EEE", "Y", "OT+EEE+Y"),
    ("EEE", "DY", "OT+EEE+DY"),
]
grid_rows: list[dict[str, object]] = []
for grade, endpoint, recipe in grid_recipes:
    matched = [row for row in events if row["component_recipe"] == recipe]
    running = [row for row in matched if row["event_role"] == "RUNNING_STATEMENT"]
    local = [row for row in matched if row["event_role"] == "LOCAL_ADDRESS_OR_LABEL"]
    grid_rows.append(
        {
            "grade_token": grade,
            "grade_value_de": GRADE_ATOMIC[grade],
            "endpoint_token": endpoint,
            "endpoint_value_de": "POSTEN BLEIBT AKTIV" if endpoint == "Y" else "TEILGANG SCHLIESST",
            "component_recipe": recipe,
            "running_events": len(running),
            "local_address_events": len(local),
            "total_events": len(matched),
            "physical_pages": "|".join(sorted({row["physical_page"] for row in matched})) or "NONE",
            "interpretation_de": (
                f"DANACH · {GRADE_ATOMIC[grade]} · "
                f"{'POSTEN' if endpoint == 'Y' else 'SCHLUSS'}"
            ),
        }
    )
write_tsv(OUT / "PASS1010_GRADE_ENDPOINT_GRID.tsv", grid_rows, list(grid_rows[0]))

revised_codebook: list[dict[str, object]] = []
for original in codebook:
    row: dict[str, object] = dict(original)
    recognition = original["recognition_forms"]
    row["spoken_value_de"] = replace_grade_words(original["spoken_value_de"])
    if recognition in GRADE_ATOMIC:
        row["spoken_value_de"] = GRADE_ATOMIC[recognition]
        row["concrete_context_values_de"] = GRADE_LOCAL[recognition]
        row["teaching_rule_de"] = (
            "Grundtafel: als allgemeinen Arbeitsgrad zusammensetzen; "
            "die lokale Handlung liefert Zeit-, Stärke- oder Umfangslesung."
        )
    revised_codebook.append(row)
write_tsv(OUT / "PASS1010_175_GRADE_REVISED_CODEBOOK.tsv", revised_codebook, list(codebook[0]))

action_ids = {row["statement_id"] for row in action_rows}
chain_by_id = {row["statement_id"]: row for row in chain_rows}
revised_statements: list[dict[str, object]] = []
for original in statements:
    row: dict[str, object] = dict(original)
    row["portable_literal_de"] = replace_grade_words(original["portable_literal_de"])
    if original["statement_id"] in action_ids:
        chain = chain_by_id[original["statement_id"]]
        row["grade_policy"] = "INHERITED_OPERATION_PLUS_EXPLICIT_GRADE"
        row["grade_neutral_workshop_de"] = chain["grade_neutral_fluent_de"]
    else:
        row["grade_policy"] = "NO_PASS1010_ACTION_ELLIPSIS_REVISION"
        row["grade_neutral_workshop_de"] = original["resolved_workshop_de"]
    revised_statements.append(row)
statement_fields = list(statements[0]) + ["grade_policy", "grade_neutral_workshop_de"]
write_tsv(OUT / "PASS1010_627_GRADE_AWARE_STATEMENTS.tsv", revised_statements, statement_fields)

report = f"""# Pass 1010 — OT übernimmt die Handlung, E/EE/EEE setzt den Grad

Die 24 echten Folgeketten bestätigen eine einfache Werkstattregel. `OT` trägt
nicht selbst das ausgelassene Verb: Es ruft die letzte aktive Handlung desselben
Bildbesitzers wieder auf. `E`, `EE` oder `EEE` setzt anschließend unabhängig den
Arbeitsgrad. Alle 24 Ketten behalten so eine konkrete Handlung; keine neue
Wurzel ist nötig.

## Was sich tatsächlich ändert

Die Grade werden nicht bloß mitkopiert. Von 24 Ketten behalten
**{transition_counts['SAME']}** den Grad, **{transition_counts['LOWERED']}** gehen
von Grad II auf Grad I zurück, **{transition_counts['RAISED']}** erhöhen ihn und
**{transition_counts['FIRST_ASSIGNED']}** weisen einer zuvor ungraduierten
Handlung erstmals einen Grad zu. Handlung und Grad sind damit zwei getrennte
Speicherplätze.

`SETZEN` erscheint innerhalb der Folgeketten {operation_grade['SETZEN']['E']}×
im Grad I und {operation_grade['SETZEN']['EE']}× im Grad II. Auf f75r, f77r und
f83r stehen beide Grade sogar im selben Besitzerblock. `GEBEN` kommt einmal im
Grad I und einmal im Vollgrad vor. Die übrigen Handlungen zeigen bislang nur
einen der drei Grade.

## Wörterbuchkorrektur

Die bisherigen atomaren Werte `KURZ / LÄNGER / VOLL` waren zu zeitlich. Das
gleiche Zeichen graduiert auch **auswählen, geben, nehmen, stellen, leiten** und
**umsetzen**. Die kürzere und überall brauchbare Grundtafel lautet deshalb:

- `E = GRAD I` — lokal kurz, leicht oder einmal;
- `EE = GRAD II` — lokal länger, stärker oder als weiterer Durchgang;
- `EEE = GRAD III` — lokal vollständig oder bis zum Abschluss.

Die alte flüssige Zeitlesung bleibt eine erlaubte lokale Expansion, aber nicht
mehr die Wörterbuchbedeutung.

## Die vollständige kleine Formel

`OT + GRAD + Y/DY` wird gelesen als:

> DANACH · [AKTIVE HANDLUNG] · [GRAD] · [POSTEN BLEIBT AKTIV / TEILGANG SCHLIESST]

Das sichtbare Raster stützt die Trennung: Im Lauftext gibt es 12× `OT+E+Y`,
29× `OT+E+DY`, 23× `OT+EE+Y`, 26× `OT+EE+DY` und einmal
`OT+EEE+DY`. Damit sind Grad und Schluss keine gemeinsame Bedeutung. Grad III
bleibt wegen seines Einzelbelegs die schwächste, aber weiterhin nützliche Stufe.

## Kreatives Ergebnis

Das Schreibsystem braucht hier kein ausgelassenes Geheimwort. Der Schreiber
merkt sich pro Bildbesitzer nur **aktuelle Handlung** und **aktuellen Posten**.
Eine OT-Karte startet den Folgegang, setzt einen neuen Grad und entscheidet mit
Y/DY, ob der Posten offen bleibt oder der Teilgang endet. Das ist kurz genug,
dass mehrere Schreiber es aus einem gemeinsamen Lehrdeck lernen konnten.
"""
(OUT / "PASS1010_OT_GRADE_REPORT.md").write_text(report, encoding="utf-8")

summary = {
    "status": "PASS",
    "decision": "OT_INHERITS_OPERATION_WHILE_E_EE_EEE_SET_AN_INDEPENDENT_WORK_GRADE",
    "action_inheritance_chains": len(chain_rows),
    "transition_counts": dict(sorted(transition_counts.items())),
    "operation_grade_counts": {
        operation: {grade: operation_grade[operation][grade] for grade in ("E", "EE", "EEE")}
        for operation in sorted(operation_grade)
    },
    "grade_endpoint_running_counts": {
        row["component_recipe"]: row["running_events"] for row in grid_rows
    },
    "codebook_rows": len(revised_codebook),
    "statement_rows": len(revised_statements),
    "portable_roots": 53,
    "new_portable_roots": 0,
    "source_hashes": {path.name: sha256(path) for path in (STATEMENTS, EVENTS, ELLIPSES, CODEBOOK)},
}
(OUT / "PASS1010_BUILD_SUMMARY.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

generated = [
    OUT / "PASS1010_24_OT_GRADE_CHAINS.tsv",
    OUT / "PASS1010_OPERATION_GRADE_MATRIX.tsv",
    OUT / "PASS1010_GRADE_ENDPOINT_GRID.tsv",
    OUT / "PASS1010_175_GRADE_REVISED_CODEBOOK.tsv",
    OUT / "PASS1010_627_GRADE_AWARE_STATEMENTS.tsv",
    OUT / "PASS1010_OT_GRADE_REPORT.md",
]
summary["output_hashes"] = {path.name: sha256(path) for path in generated}
(OUT / "PASS1010_BUILD_SUMMARY.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

print(json.dumps({key: value for key, value in summary.items() if key != "output_hashes"}, ensure_ascii=False))
