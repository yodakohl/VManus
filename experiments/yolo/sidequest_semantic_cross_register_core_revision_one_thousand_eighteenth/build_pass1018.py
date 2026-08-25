#!/usr/bin/env python3
"""Build Pass 1018: reread every portable core across all four registers."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PASS1013 = ROOT / "experiments/yolo/sidequest_semantic_embedded_stem_resegmentation_one_thousand_thirteenth"
PASS1016 = ROOT / "experiments/yolo/sidequest_semantic_local_channel_compression_one_thousand_sixteenth"
PASS1017 = ROOT / "experiments/yolo/sidequest_semantic_forward_composition_compiler_one_thousand_seventeenth"
SOURCE_CONTRACT = PASS1013 / "PASS1013_46_SIGN_SEMANTIC_CONTRACT.tsv"
SOURCE_STATEMENTS = PASS1013 / "PASS1013_627_SEMANTIC_PRESSURE_MAP.tsv"
SOURCE_EDITION = PASS1016 / "PASS1016_627_LOCAL_CHANNEL_EDITION.tsv"
SOURCE_LOCAL_SIGNS = PASS1016 / "PASS1016_19_LOCAL_SIGN_CHANNELS.tsv"
SOURCE_VALENCY = PASS1017 / "PASS1017_19_CORE_VALENCY.tsv"
SOURCE_PREDICTIONS = PASS1017 / "PASS1017_FOUR_FRESH_COMPOSITION_PREDICTIONS.tsv"


REGISTERS = ["HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA"]
OVERRIDES = {"AIIN": "WERT", "AIN": "ANTEIL", "OR": "EINHEIT"}
RATIONALE = {
    "AIIN": "MASS ist in Pflanzen-/Pharmakontexten gut, aber in Himmels- und Stationsregistern zu stofflich; WERT deckt Dosis, Einstellung und Tabellenwert.",
    "AIN": "PORTION ist für Stoffe gut, aber für Ring- und Stationssegmente zu eng; ANTEIL bleibt konkret und registerübergreifend.",
    "OR": "ANSATZ erzwingt eine Zubereitung auch in Himmelsringen; EINHEIT deckt Ansatz, Stationsblock, Eintragsgruppe und Charge.",
}
LOCAL_EXPANSION = {
    "AIIN": {
        "HERBAL": "Maß- oder Dosiswert", "BIOLOGICAL": "Einstell- oder Arbeitswert",
        "CELESTIAL": "Tabellen- oder Positionswert", "PHARMA": "Mengen- oder Ansatzwert",
    },
    "AIN": {
        "HERBAL": "Pflanzen- oder Mengenanteil", "BIOLOGICAL": "Teilposten oder Füllanteil",
        "CELESTIAL": "Teilwert oder Sektoranteil", "PHARMA": "Zutatenanteil",
    },
    "OR": {
        "HERBAL": "Ansatz oder Artikelblock", "BIOLOGICAL": "Stations- oder Arbeitsblock",
        "CELESTIAL": "Eintragsgruppe", "PHARMA": "Ansatz oder Charge",
    },
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    _, contract = read_tsv(SOURCE_CONTRACT)
    _, statements = read_tsv(SOURCE_STATEMENTS)
    _, edition = read_tsv(SOURCE_EDITION)
    _, local_sign_rows = read_tsv(SOURCE_LOCAL_SIGNS)
    _, valency = read_tsv(SOURCE_VALENCY)
    _, old_predictions = read_tsv(SOURCE_PREDICTIONS)
    portable = [row for row in contract if row["pass1012_class"] == "PORTABLE_CORE_MEANING"]
    old_values = {row["sign"]: row["single_core_value_de"] for row in portable}
    new_values = {root: OVERRIDES.get(root, value) for root, value in old_values.items()}
    role_by_root = {row["root"]: row for row in valency}
    edition_by_id = {row["statement_id"]: row for row in edition}
    channel_by_sign = {row["sign"]: row["channel_value_de"] for row in local_sign_rows}
    all_values = {row["sign"]: row["single_core_value_de"] for row in contract}
    all_values.update(new_values)
    all_values.update(channel_by_sign)

    occurrence_index = []
    for statement in statements:
        for index, (surface, recipe) in enumerate(zip(statement["surface_sequence"].split(), statement["component_sequence"].split(" | ")), 1):
            occurrence_index.append(
                {
                    "statement_id": statement["statement_id"], "page": statement["physical_page"],
                    "register": statement["register"], "owner": statement["visible_owner_or_namespace_de"],
                    "event_index": index, "surface": surface, "recipe": recipe, "tokens": recipe.split("+"),
                }
            )

    context_rows = []
    for root in old_values:
        for register in REGISTERS:
            occurrences = [row for row in occurrence_index if row["register"] == register and root in row["tokens"]]
            if not occurrences:
                raise SystemExit(f"portable root {root} absent from register {register}")
            recipe_counts = Counter(row["recipe"] for row in occurrences)
            representative_recipe = recipe_counts.most_common(1)[0][0]
            representative = next(row for row in occurrences if row["recipe"] == representative_recipe)
            expansion = LOCAL_EXPANSION.get(root, {}).get(register, f"{new_values[root]} mit dem sichtbaren Besitzer")
            context_rows.append(
                {
                    "root": root,
                    "old_value_de": old_values[root],
                    "pass1018_value_de": new_values[root],
                    "register": register,
                    "occurrence_count": str(len(occurrences)),
                    "representative_page": representative["page"],
                    "representative_statement_id": representative["statement_id"],
                    "representative_surface": representative["surface"],
                    "representative_recipe": representative["recipe"],
                    "visible_owner_or_namespace_de": representative["owner"],
                    "pass1018_local_expansion_de": expansion,
                    "representative_statement_translation_de": edition_by_id[representative["statement_id"]]["pass1015_core_owner_translation_de"],
                    "decision": "REVISE_PORTABLE_CORE" if root in OVERRIDES else "KEEP_PORTABLE_CORE",
                }
            )
    context_path = HERE / "PASS1018_76_CROSS_REGISTER_CONTEXTS.tsv"
    write_tsv(context_path, list(context_rows[0]), context_rows)

    decision_rows = []
    for root in old_values:
        contexts = [row for row in context_rows if row["root"] == root]
        val = role_by_root[root]
        decision_rows.append(
            {
                "root": root,
                "old_value_de": old_values[root],
                "pass1018_value_de": new_values[root],
                "decision": "REVISE" if root in OVERRIDES else "KEEP",
                "composition_role": val["composition_role"],
                "running_mentions": val["running_mentions"],
                "register_count": str(len(contexts)),
                "register_occurrence_counts": "|".join(f"{row['register']}:{row['occurrence_count']}" for row in contexts),
                "cross_register_reading_de": " | ".join(f"{row['register']}={row['pass1018_local_expansion_de']}" for row in contexts),
                "reason_de": RATIONALE.get(root, "Der kurze Wert bleibt in allen vier Registern als dieselbe Kernhandlung oder Relation lesbar."),
                "forward_rule_de": val["forward_rule_de"].replace(old_values[root], new_values[root]),
            }
        )
    decision_path = HERE / "PASS1018_19_CORE_DICTIONARY.tsv"
    write_tsv(decision_path, list(decision_rows[0]), decision_rows)

    revised_rows = []
    for statement in statements:
        old = edition_by_id[statement["statement_id"]]
        literal_events = []
        portable_mentions = Counter()
        for recipe in statement["component_sequence"].split(" | "):
            tokens = recipe.split("+")
            literal_events.append(" + ".join(all_values[token] for token in tokens))
            portable_mentions.update(token for token in tokens if token in new_values)
        revised_rows.append(
            {
                **old,
                "pass1018_core_literal_de": " | ".join(literal_events),
                "pass1018_portable_value_sequence": "+".join(
                    new_values[token]
                    for recipe in statement["component_sequence"].split(" | ")
                    for token in recipe.split("+")
                    if token in new_values
                ) or "NONE",
                "pass1018_revised_core_mentions": str(sum(portable_mentions[root] for root in OVERRIDES)),
                "pass1018_result": "CROSS_REGISTER_CORE_REVISION_APPLIED",
            }
        )
    edition_path = HERE / "PASS1018_627_REVISED_CORE_EDITION.tsv"
    edition_fields = list(edition[0]) + ["pass1018_core_literal_de", "pass1018_portable_value_sequence", "pass1018_revised_core_mentions", "pass1018_result"]
    write_tsv(edition_path, edition_fields, revised_rows)

    prediction_rows = []
    for old in old_predictions:
        left, right = old["left_root"], old["right_root"]
        reading = {
            ("CH", "AIN"): "einen Anteil nehmen",
            ("P", "AIN"): "einen Anteil einsetzen",
            ("P", "AIIN"): "einen Wert einsetzen",
            ("L", "AIR"): "Verbindung im bezeichneten Lauf",
        }[(left, right)]
        prediction_rows.append(
            {
                **old,
                "predicted_reading_de": reading,
                "pass1018_literal_de": f"{new_values[left]} + {new_values[right]}",
                "prediction_status": "DIRECT_FORM_STILL_ABSENT_READING_FIXED",
            }
        )
    prediction_path = HERE / "PASS1018_FOUR_UPDATED_PREDICTIONS.tsv"
    prediction_fields = list(old_predictions[0]) + ["pass1018_literal_de", "prediction_status"]
    write_tsv(prediction_path, prediction_fields, prediction_rows)

    report = f"""# Pass 1018 — Kernwörter über alle vier Register

## Ergebnis

Jeder der 19 portablen Kerne kommt in **Herbal, Biological, Celestial und Pharma** vor. Sechzehn kurze Werte bleiben unverändert. Drei Wörter waren noch zu eng und werden korrigiert:

- `AIIN`: **MASS → WERT**;
- `AIN`: **PORTION → ANTEIL**;
- `OR`: **ANSATZ → EINHEIT**.

Das sind keine neuen Funktionen. Es sind kürzere gemeinsame Nenner für dieselben Karten.

## Warum genau diese drei

### AIIN = WERT

In Herbal und Pharma kann WERT als Maß oder Dosis erscheinen. In Biological ist es ein Einstell-/Arbeitswert; in Celestial ein Tabellen- oder Positionswert. Das alte MASS war nur eine lokale Stofflesung.

### AIN = ANTEIL

Ein Anteil kann Pflanzenmenge, Teilposten, Füllanteil, Sektoranteil oder Zutatenanteil sein. PORTION war für die Himmelsregister unnötig eng.

### OR = EINHEIT

Eine Einheit wird im Herbal-/Pharmaregister lokal zum Ansatz oder zur Charge, im Biological zum Stations-/Arbeitsblock und im Celestial zur Eintragsgruppe. Das alte ANSATZ zwang eine ungemalte Zubereitung in 30 Himmelsvorkommen.

## Was unverändert bleibt

`Y=DIES`, `OK=SETZEN`, `OL=FORTSETZEN`, `OT=DANACH`, `AL=ZIELORT`, `CH=NEHMEN`, `SH=HALTEN`, `AR=AUSGANG`, `K=GEBEN`, `S=WÄHLEN`, `CHD=UMSETZEN`, `L=VERBINDUNG`, `T=EINSTELLEN`, `R=MARKIEREN`, `P=EINSETZEN`, `AIR=LAUF`.

Diese sechzehn Werte sind in jedem Register dieselbe kleine Handlung, Relation oder Referenz. Der Besitzer liefert weiterhin, *was* genommen, gehalten, gesetzt, markiert oder verbunden wird.

## Wirkung auf die vollständige Ausgabe

Alle **627 Aussagen / 3.888 Ereignisse** behalten Oberfläche, Reihenfolge, Besitzer, Komponenten, lokale Kanäle, Grad und Ende. Nur die portable Literalzeile wird neu gebaut. Eine flüssige lokale Fassung darf weiterhin *nach Maß*, *eine Portion* oder *im Ansatz* sagen, wenn der Besitzer das trägt; das Wörterbuch selbst sagt nun WERT, ANTEIL und EINHEIT.

## Aktualisierte Zukunftsformen

- `chain = CH+AIN = einen Anteil nehmen`;
- `pain = P+AIN = einen Anteil einsetzen`;
- `paiin = P+AIIN = einen Wert einsetzen`;
- `lair = L+AIR = Verbindung im bezeichneten Lauf`.

Damit sind die portablen Wörter jetzt bewusst so kurz, dass sie auf Pflanzenbildern, Bad-/Stationsseiten, Himmelsringen und Gefäßgruppen dieselbe Bedeutung behalten können.
"""
    report_path = HERE / "PASS1018_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    summary = {
        "pass": 1018,
        "source_contract_sha256": sha256(SOURCE_CONTRACT),
        "source_statements_sha256": sha256(SOURCE_STATEMENTS),
        "source_edition_sha256": sha256(SOURCE_EDITION),
        "source_valency_sha256": sha256(SOURCE_VALENCY),
        "portable_root_count": len(old_values),
        "register_count": len(REGISTERS),
        "cross_register_context_count": len(context_rows),
        "kept_root_count": len(old_values) - len(OVERRIDES),
        "revised_root_count": len(OVERRIDES),
        "revisions": {root: {"old": old_values[root], "new": new_values[root]} for root in OVERRIDES},
        "statement_count": len(revised_rows),
        "event_count": sum(int(row["event_count"]) for row in revised_rows),
        "updated_prediction_count": len(prediction_rows),
        "new_root_count": 0,
        "result": "THREE_CROSS_REGISTER_CORE_GLOSSES_BROADENED",
        "outputs": {
            context_path.name: sha256(context_path),
            decision_path.name: sha256(decision_path),
            edition_path.name: sha256(edition_path),
            prediction_path.name: sha256(prediction_path),
            report_path.name: sha256(report_path),
        },
    }
    (HERE / "PASS1018_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
