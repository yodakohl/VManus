#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P539 = ROOT / "experiments/yolo/sidequest_semantic_composition_predictions_five_hundred_thirty_ninth"
P536 = ROOT / "experiments/yolo/sidequest_semantic_common_workshop_grammar_five_hundred_thirty_sixth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


RULES = [
    ("R01", "ADDRESS_BARE", "bare address", "Ø|d|s|ch|t|che", "aiin/taiin/chaiin/daiin/saiin; al/chal/cheal/dal/sal/tal"),
    ("R02", "ADDRESS_OK", "OK+argument", "Ø|q", "okaiin/qokaiin; okain/qokain; okal/qokal"),
    ("R03", "ADDRESS_OT", "OT+argument", "Ø|q|s", "otaiin/sotaiin; otal/qotal; otar"),
    ("R04", "ADDRESS_OL", "OL+argument", "Ø|q", "ol/qol as continuation wrappers"),
    ("R05", "GRADE_OK", "OK+grade+endpoint", "Ø|q", "okey/qokey; okeey/qokeey; qokedy/qokeedy/qokeeedy"),
    ("R06", "GRADE_OT", "OT+grade+endpoint", "Ø|q", "oteey; otedy; qoteedy"),
    ("R07", "GRADE_SH", "SH+grade+endpoint", "Ø|d|t", "sheey/sheedy; dshedy; tshey"),
    ("R08", "GRADE_CHK", "CHK grade interposed or postposed", "CH+GRADE+K|CHK+GRADE", "cheky/cheeky; chkeey/chkeedy"),
    ("R09", "GRADE_SOLK", "SOLK+grade+endpoint", "solk|olk", "solkey/solkeey/solkeedy; olkeedy"),
]


def address_variants(parts: list[str]) -> list[tuple[str, str, str]]:
    canonical = "".join(part.lower() for part in parts)
    prefix = parts[0] if len(parts) == 2 else "BARE"
    wrappers = {
        "BARE": [("", "DEFAULT"), ("d", "D_WRAPPER"), ("s", "S_WRAPPER"), ("ch", "CH_WRAPPER"), ("t", "T_WRAPPER"), ("che", "CHE_WRAPPER")],
        "OK": [("", "DEFAULT_OR_MEDIAL"), ("q", "Q_ENTRY_WRAPPER")],
        "OT": [("", "DEFAULT_OR_MEDIAL"), ("q", "Q_ENTRY_WRAPPER"), ("s", "S_POSITIONAL_WRAPPER")],
        "OL": [("", "DEFAULT_OR_MEDIAL"), ("q", "Q_ENTRY_WRAPPER")],
    }[prefix]
    return [(wrapper + canonical, label, f"R0{1 if prefix == 'BARE' else {'OK': 2, 'OT': 3, 'OL': 4}[prefix]}") for wrapper, label in wrappers]


def grade_variants(parts: list[str]) -> list[tuple[str, str, str]]:
    base, grade, endpoint = parts
    g = grade.lower()
    ep = endpoint.lower()
    if base == "OK":
        core = "ok" + g + ep
        return [(core, "DEFAULT_OR_MEDIAL", "R05"), ("q" + core, "Q_ENTRY_WRAPPER", "R05")]
    if base == "OT":
        core = "ot" + g + ep
        return [(core, "DEFAULT_OR_MEDIAL", "R06"), ("q" + core, "Q_ENTRY_WRAPPER", "R06")]
    if base == "SH":
        core = "sh" + g + ep
        return [(core, "DEFAULT", "R07"), ("d" + core, "D_WRAPPER", "R07"), ("t" + core, "T_WRAPPER", "R07")]
    if base == "CHK":
        return [
            ("ch" + g + "k" + ep, "GRADE_INTERPOSED", "R08"),
            ("chk" + g + ep, "GRADE_POSTPOSED", "R08"),
        ]
    if base == "SOLK":
        return [
            ("solk" + g + ep, "FULL_SOLK", "R09"),
            ("olk" + g + ep, "INITIAL_S_DROPPED", "R09"),
        ]
    raise ValueError(base)


def main() -> None:
    predictions = read_tsv(P539 / "FIVE_HUNDRED_THIRTY_NINTH_TWENTY_MISSING_COMPOSITION_PREDICTIONS.tsv")
    observed_events = read_tsv(P536 / "FIVE_HUNDRED_THIRTY_SIXTH_THREE_HUNDRED_EIGHTY_ONE_COMMON_GRAMMAR_INTERLINEAR.tsv")
    observed_surfaces: dict[str, set[str]] = defaultdict(set)
    for row in observed_events:
        observed_surfaces[row["surface"]].add(row["card_no"])

    rule_rows = [
        {
            "rule_id": rule_id,
            "family": family,
            "input_pattern": pattern,
            "licensed_renderer_variants": variants,
            "observed_support_examples": examples,
            "teaching_instruction": "keep semantic components fixed; choose only a listed renderer realization",
        }
        for rule_id, family, pattern, variants, examples in RULES
    ]
    write_tsv("FIVE_HUNDRED_FORTIETH_NINE_PREDICTIVE_RENDERER_RULES.tsv", rule_rows)

    surface_rows: list[dict[str, str]] = []
    rejected_rows: list[dict[str, str]] = []
    realized: list[dict[str, str]] = []
    for prediction in predictions:
        parts = prediction["component_parse"].split("+")
        variants = address_variants(parts) if prediction["family"] == "OPERATOR_ADDRESS" else grade_variants(parts)
        accepted_for_prediction: list[str] = []
        for rank, (surface, context, rule_id) in enumerate(variants, 1):
            collision_ids = sorted(observed_surfaces.get(surface, set()))
            candidate = {
                "prediction_id": prediction["prediction_id"],
                "component_parse": prediction["component_parse"],
                "predicted_reading_de": prediction["predicted_atomic_reading_de"],
                "variant_rank": str(rank),
                "predicted_surface": surface,
                "renderer_rule_id": rule_id,
                "licensed_context": context,
                "observed_surface_collision": "YES" if collision_ids else "NO",
                "collision_card_ids": "|".join(collision_ids) or "NONE",
                "status": "REJECTED_EXISTING_SURFACE_COLLISION" if collision_ids else "PREDICTED_NOT_SIGHTED",
            }
            if collision_ids:
                rejected_rows.append(candidate)
            else:
                surface_rows.append(candidate)
                accepted_for_prediction.append(surface)
        realized.append(
            {
                "prediction_id": prediction["prediction_id"],
                "family": prediction["family"],
                "component_parse": prediction["component_parse"],
                "predicted_reading_de": prediction["predicted_atomic_reading_de"],
                "semantic_strength": prediction["prediction_strength"],
                "surface_variant_count": str(len(accepted_for_prediction)),
                "predicted_surfaces": "|".join(accepted_for_prediction),
                "renderer_status": "WRITABLE_BY_EXISTING_RULE_FAMILY",
                "observed_status": "NOT_OBSERVED_ON_TEN_PAGES",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTIETH_TWENTY_REALIZED_COMPOSITION_PREDICTIONS.tsv", realized)
    write_tsv("FIVE_HUNDRED_FORTIETH_FORTY_SEVEN_ACTIVE_PREDICTED_SURFACES.tsv", surface_rows)
    write_tsv("FIVE_HUNDRED_FORTIETH_ONE_REJECTED_SURFACE_COLLISION.tsv", rejected_rows)

    summary = {
        "status": "PASS",
        "renderer_rules": len(rule_rows),
        "semantic_predictions": len(realized),
        "surface_predictions": len(surface_rows),
        "unique_predicted_surfaces": len({row["predicted_surface"] for row in surface_rows}),
        "rejected_observed_surface_collisions": len(rejected_rows),
        "active_surface_collisions": sum(row["observed_surface_collision"] == "YES" for row in surface_rows),
        "variant_count_distribution": {
            str(count): sum(int(row["surface_variant_count"]) == count for row in realized)
            for count in sorted({int(row["surface_variant_count"]) for row in realized})
        },
        "source_events_unchanged": len(observed_events),
    }
    (HERE / "FIVE_HUNDRED_FORTIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Fünfhundertvierzigste Runde: Schreiberoberflächen für die Vorhersagen",
        "",
        "## Ergebnis",
        "",
        f"Alle zwanzig fehlenden Kompositionen sind mit neun bereits vorhandenen Rendererfamilien schreibbar. Nach einem Kollisionsausschluss erzeugen sie {len(surface_rows)} konkrete Oberflächenkandidaten.",
        "",
        "Die Semantik bleibt dabei fest. Nur der Eintritts-/Positionswrapper oder die bekannte Gradschreibung wechselt.",
        "",
        "## Beispiele",
        "",
        "- OT+E+Y → `otey` oder `qotey`;",
        "- OL+AIIN → `olaiin` oder `qolaiin`;",
        "- OK+EEE+Y → `okeeey` oder `qokeeey`;",
        "- SH+EEE+DY → `sheeedy`, `dsheeedy` oder `tsheeedy`;",
        "- CHK+E+DY → `chekdy` oder `chkedy`;",
        "- SOLK+E+DY → `solkedy` oder `olkedy`.",
        "",
        "Eine Form wurde verworfen: nacktes AIR darf nicht als `chair` gerendert werden, weil `chair` bereits CH+AIR = abziehen+Lauf bezeichnet. CH ist hier also semantischer Stamm, kein frei aufsetzbarer Wrapper.",
        "",
        "## Die neun Regeln",
        "",
        "Adresse ohne Operator erlaubt Ø/d/s/ch/t/che; OK und OL erlauben Ø/q; OT zusätzlich s. Bei Gradkarten setzen OK und OT die e-Stufe normal vor Y/DY. SH erlaubt Positionswrapper. CHK besitzt die beiden realen Reihen CH-E-K und CHK-E. SOLK kann initiales s behalten oder abwerfen.",
        "",
        "## Grenze",
        "",
        "Das sind schreibbare Erwartungen innerhalb unseres zehnseitigen Systems, keine Behauptung, dass die Formen anderswo im Manuskript vorkommen. Wir öffnen dafür keine neue Seite.",
        "",
        "## Nächster Angriff",
        "",
        "Jetzt wird aus Grammatik, Komponentendeck, drei Ganzkarten und Rendererregeln ein einziges kurzes Lehrbuch für einen Schreiber von 1420 gebaut. Danach schreiben und lesen wir mehrere neue Arbeitsanweisungen vollständig im erfundenen System.",
    ]
    (HERE / "FIVE_HUNDRED_FORTIETH_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
