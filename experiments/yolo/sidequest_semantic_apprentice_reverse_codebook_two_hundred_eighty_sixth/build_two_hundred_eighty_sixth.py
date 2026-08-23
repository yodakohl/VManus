#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R278 = ROOT / "experiments/yolo/sidequest_semantic_thirty_six_stem_families_two_hundred_seventy_eighth"
R279 = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth"
FAMILIES = R278 / "TWO_HUNDRED_SEVENTY_EIGHTH_36_STEM_FAMILIES.tsv"
CARDS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"

FORECASTS = [
    ("Sollmaß einsetzen und festsetzen", "OK+AIIN+DY", "qok-aiin-dy", "OK before quantity; licensed terminal DY after payload", "NEW_COMBINATION"),
    ("eine Portion einsetzen und festsetzen", "OK+AIN+DY", "qok-ain-dy", "OK before portion; terminal DY", "NEW_COMBINATION"),
    ("zum nächsten Portionsposten wechseln", "OT+AIN", "ot-ain", "OT before following payload", "NEW_COMBINATION"),
    ("mit dem vorgeschriebenen Maß weiter", "OL+AIIN", "ol-aiin", "OL before continued value", "NEW_COMBINATION"),
    ("das Sollmaß aus der Quelle nehmen", "AR+AIIN", "ar-aiin", "source address plus prescribed value", "NEW_COMBINATION"),
    ("das Sollmaß aus der Quelle überführen", "AR+AIIN+CHED_TRANSFER", "ar-aiin-ched", "source and value before transfer", "NEW_COMBINATION"),
    ("eine Portion in den Empfänger überführen", "P+AIN+CHED_TRANSFER", "p-ain-ched", "receiver feed plus portion plus transfer", "NEW_COMBINATION"),
    ("Sollmenge sammeln und festsetzen", "AIIN+SOLK+DY", "solk-aiin-dy", "collection carrier plus prescribed value and terminal", "NEW_COMBINATION"),
    ("einen Waschgang länger halten und schließen", "LSH+E_GRADE+DY", "lsh-ee-dy", "wash base plus long grade plus terminal", "NEW_COMBINATION"),
    ("vollständig absetzen und schließen", "E_GRADE+DY+SHED", "shed-eee-dy", "extend attested short/long settle family to full grade", "NEW_GRADE_MEMBER"),
    ("lange zur Zielpassage führen", "AL+E_GRADE+CKH", "al-ee-ckh", "extend attested short target-passage to long grade", "NEW_GRADE_MEMBER"),
    ("den Folgeposten aus der Quelle überführen und schließen", "OT+AR+DY+CHED_TRANSFER", "ot-ar-ched-dy", "following selector plus source plus terminal transfer", "NEW_COMBINATION"),
]


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


def enriched_recipe(row: dict[str, str]) -> tuple[str, str]:
    old = row["old_component_parse"]
    modifiers: list[str] = []
    if "GRADE_1" in old or "E_SHORT" in old:
        modifiers.append("GRADE=E_SHORT")
    if "GRADE_2" in old:
        modifiers.append("GRADE=EE_LONG")
    if "GRADE_3" in old:
        modifiers.append("GRADE=EEE_FULL")
    if "OK + OK" in old:
        modifiers.append("REPEAT=YES")
    if "DY" not in row["family_parse"] and ("CLOSE" in old or "TERMINAL" in old or "Schluss" in row["local_prose_default_de"]):
        modifiers.append("LICENSED_CLOSE=YES")
    modifier = ",".join(modifiers) if modifiers else "NONE"
    recipe = row["family_parse"] if not modifiers else f"{row['family_parse']}[{modifier}]"
    return recipe, modifier


def main() -> None:
    roots = read_tsv(FAMILIES)
    cards = read_tsv(CARDS)
    composed = [r for r in cards if r["card_class_279"] == "COMPOSED_FROM_36_FAMILIES"]
    whole = [r for r in cards if r["card_class_279"] == "MEMORIZED_WHOLE_SIGN"]
    framed_whole = [r for r in cards if r["card_class_279"] == "FRAME_PLUS_LEARNED_WHOLE"]
    by_parse: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in composed:
        recipe, _ = enriched_recipe(row)
        by_parse[recipe].append(row)

    root_rows: list[dict[str, object]] = []
    for row in roots:
        root_rows.append({
            "family_order": row["family_order"],
            "family_id": row["family_id"],
            "visible_core_or_variants": row["member_component_ids"],
            "short_value_de": row["short_value_de"],
            "writing_rule_de": row["variant_rule"],
            "register_reach": row["reach_class"],
            "observed_support": int(row["herbal_events"]) + int(row["bio_events"]) + int(row["astro_groups"]),
            "apprentice_action": "learn as productive stem family",
        })

    template_rows: list[dict[str, object]] = []
    for recipe, members in by_parse.items():
        ranked = sorted(members, key=lambda r: (-int(r["prose_event_count"]), r["master_card_id"]))
        canonical = ranked[0]
        support = sum(int(r["prose_event_count"]) for r in members)
        _, modifiers = enriched_recipe(canonical)
        template_rows.append({
            "enriched_recipe": recipe,
            "base_family_parse": canonical["family_parse"],
            "recipe_modifiers": modifiers,
            "family_count": len(canonical["family_parse"].split("+")),
            "canonical_master_card_id": canonical["master_card_id"],
            "canonical_form": canonical["master_form"],
            "canonical_registered_surfaces": canonical["registered_surfaces"],
            "canonical_workshop_value_de": canonical["local_prose_default_de"],
            "alternate_master_forms": "|".join(r["master_form"] for r in ranked[1:]) or "NONE",
            "all_workshop_values_de": " | ".join(dict.fromkeys(r["local_prose_default_de"] for r in ranked)),
            "card_type_count": len(members),
            "event_support": support,
            "canonical_event_hits": int(canonical["prose_event_count"]),
            "writer_rule": "WRITE_CANONICAL" if len(members) == 1 else "WRITE_CANONICAL_UNLESS_LOCAL_ALLOGRAPH_IS_MEMORIZED",
        })
    template_rows.sort(key=lambda r: (-int(r["event_support"]), str(r["enriched_recipe"])))

    whole_rows: list[dict[str, object]] = []
    for row in sorted(whole, key=lambda r: (-int(r["prose_event_count"]), r["master_card_id"])):
        whole_rows.append({
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "learned_value_de": row["local_prose_default_de"],
            "event_support": row["prose_event_count"],
            "apprentice_action": "memorize as one nomenclator sign; do not split",
        })

    framed_rows = [
        {
            "master_card_id": row["master_card_id"],
            "master_form": row["master_form"],
            "registered_surfaces": row["registered_surfaces"],
            "frame_plus_whole_parse": row["family_parse"],
            "learned_value_de": row["local_prose_default_de"],
            "event_support": row["prose_event_count"],
            "apprentice_action": "memorize the inner whole sign and its licensed outer frame together",
        }
        for row in framed_whole
    ]

    exercises: list[dict[str, object]] = []
    for i, row in enumerate(template_rows[:40], 1):
        exercises.append({
            "exercise": i,
            "source_instruction_de": row["canonical_workshop_value_de"],
            "choose_family_recipe": row["enriched_recipe"],
            "write_default_card": row["canonical_form"],
            "accepted_surface_spellings": row["canonical_registered_surfaces"],
            "local_allograph_alternatives": row["alternate_master_forms"],
            "observed_event_support": row["event_support"],
            "default_writer_hits": row["canonical_event_hits"],
            "teaching_answer_de": f"Wähle {row['enriched_recipe']}; schreibe normalerweise {row['canonical_form']}.",
        })

    forecast_rows = [
        {
            "forecast": i,
            "new_instruction_de": prompt,
            "predicted_family_recipe": parse,
            "predicted_surface_skeleton": surface,
            "formation_rule": rule,
            "forecast_kind": kind,
            "use_policy": "prediction for later permitted pages; not inserted into the current translation",
        }
        for i, (prompt, parse, surface, rule, kind) in enumerate(FORECASTS, 1)
    ]

    root_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_36_PRODUCTIVE_ROOTS.tsv"
    template_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_124_COMPOSITION_TEMPLATES.tsv"
    whole_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_23_WHOLE_SIGNS.tsv"
    framed_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_ONE_FRAMED_WHOLE_EXCEPTION.tsv"
    exercise_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_40_REVERSE_ENCODINGS.tsv"
    forecast_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_12_NEW_COMPOSITION_FORECASTS.tsv"
    manual_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_APPRENTICE_CODEBOOK.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_SIXTH_REPORT.md"
    write_tsv(root_path, root_rows, list(root_rows[0]))
    write_tsv(template_path, template_rows, list(template_rows[0]))
    write_tsv(whole_path, whole_rows, list(whole_rows[0]))
    write_tsv(framed_path, framed_rows, list(framed_rows[0]))
    write_tsv(exercise_path, exercises, list(exercises[0]))
    write_tsv(forecast_path, forecast_rows, list(forecast_rows[0]))

    manual = [
        "# Lehrlings-Codebuch für die zehn Seiten",
        "",
        "## So schreibt man eine neue Zelle",
        "",
        "1. Nimm Besitzer und örtlichen Sachinhalt aus Bild, Diagramm oder Masterexemplar.",
        "2. Wähle in dieser Reihenfolge nur die benötigten Rollen: Folge/Weiterführung, Quelle oder Posten, Portion oder Grad, Handlung oder Bahn, Ziel, Festsetzung.",
        "3. Setze gegebenenfalls den Modifier E=kurz, EE=lang, EEE=voll, Wiederholung oder lizenzierten Schluss. Suche dann das Ergebnis in den 124 Kompositionsrezepten und schreibe die Standardkarte.",
        "4. Hat das Rezept mehrere Kartenformen, benutze die gelernte lokale Allographie; erfinde keine neue Bedeutung.",
        "5. Steht der Inhalt unter den 23 Ganzzeichen oder der einen gerahmten Ganzzeichen-Ausnahme, kopiere die ganze registrierte Form und zerlege sie nicht.",
        "6. Diagrammnamen und andere örtliche Schlüssel werden direkt aus dem Exemplar kopiert.",
        "",
        "## Praktisches Ergebnis",
        "",
        "Die 149 zusammengesetzten Prosakarten verwenden nach Abtrennung der kurzen, langen, vollen, wiederholten und geschlossenen Varianten 124 Bedeutungsrezepte. 104 Rezepte haben genau eine Kartenform. 20 Rezepte haben mehrere Werkstattallographen. Nimmt der Lehrling jeweils die häufigste Standardkarte, schreibt er 324 von 352 zusammengesetzten Vorkommen direkt richtig; die restlichen 28 lernt er als kleine Allographenliste. Die 23 Ganzzeichen decken weitere 28 Vorkommen, eine gerahmte Ganzzeichen-Ausnahme ein weiteres.",
        "",
        "## Vierzig häufige Rückwärtsübungen",
        "",
    ]
    for row in exercises:
        manual.append(f"- **{row['exercise']} — {row['source_instruction_de']}**: {row['teaching_answer_de']} Allographen: {row['local_allograph_alternatives']}.")
    manual.extend(["", "## Zwölf echte Vorhersagen", ""])
    for row in forecast_rows:
        manual.append(f"- **{row['new_instruction_de']}** → `{row['predicted_family_recipe']}` → erwartetes Gerüst `{row['predicted_surface_skeleton']}`.")
    manual_path.write_text("\n".join(manual) + "\n", encoding="utf-8")

    ambiguous = [r for r in template_rows if int(r["card_type_count"]) > 1]
    canonical_hits = sum(int(r["canonical_event_hits"]) for r in template_rows)
    report_path.write_text(
        "# Sidequest-Pass 286: das rückwärts benutzbare Lehrlings-Codebuch\n\n"
        "## Ergebnis\n\n"
        "Die aktuelle Wortstammtheorie ist erstmals produktiv statt nur lesend. Aus einer deutschen Werkstattanweisung wird zunächst eine der 124 Rollen- und Modifierfolgen und daraus eine Standardkarte gewählt. "
        "104 Folgen sind eindeutig; 20 besitzen gelernte lokale Allographen. Die Standardwahl deckt 324/352 zusammengesetzte Ereignisse, die Allographenliste den Rest. 23 unteilbare Ganzzeichen plus eine gerahmte Ganzzeichen-Ausnahme bleiben ein echter Nomenklator.\n\n"
        "Zwölf noch nicht benutzte oder noch nicht voll ausgebaute Kompositionen sind als Vorhersagen festgehalten. Sie werden nicht rückwirkend in die zehn Seiten geschrieben. "
        "Der stärkste praktische Mechanismus ist damit: produktive Fachkürzel + kleine Allographentafel + gelernte Ganzzeichen + exemplarabhängige lokale Namen.\n\n"
        f"Mehrdeutige Rezepte {len(ambiguous)}; kanonische Treffer {canonical_hits}. Inputs `{sha(FAMILIES)}` und `{sha(CARDS)}`.\n",
        encoding="utf-8",
    )

    outputs = (root_path, template_path, whole_path, framed_path, exercise_path, forecast_path, manual_path, report_path)
    summary = {
        "status": "PASS",
        "productive_roots": len(root_rows),
        "composed_cards": len(composed),
        "composition_templates": len(template_rows),
        "unique_surface_templates": sum(int(r["card_type_count"]) == 1 for r in template_rows),
        "ambiguous_allograph_templates": len(ambiguous),
        "whole_signs": len(whole_rows),
        "framed_whole_exceptions": len(framed_rows),
        "composed_events": sum(int(r["prose_event_count"]) for r in composed),
        "canonical_event_hits": canonical_hits,
        "reverse_exercises": len(exercises),
        "new_forecasts": len(forecast_rows),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
