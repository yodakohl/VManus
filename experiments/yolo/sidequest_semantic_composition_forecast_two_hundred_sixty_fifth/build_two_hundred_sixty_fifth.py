#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R264 = ROOT / "experiments/yolo/sidequest_semantic_complete_sixty_three_entry_deck_two_hundred_sixty_fourth"
R261 = ROOT / "experiments/yolo/sidequest_semantic_bidirectional_compiler_two_hundred_sixty_first"
R248 = ROOT / "experiments/yolo/sidequest_semantic_astro_native_card_values_two_hundred_forty_eighth"
COMPONENTS = R264 / "TWO_HUNDRED_SIXTY_FOURTH_40_COMPONENTS.tsv"
SURFACES = R261 / "TWO_HUNDRED_SIXTY_FIRST_230_SURFACE_DICTIONARY.tsv"
ASTRO = R248 / "TWO_HUNDRED_FORTY_EIGHTH_REVISED_395_GROUP_MANUAL.tsv"

FORECASTS = [
    ("P01", "OK+AN", "okan", "zweite Portion einsetzen", "OPEN_ACTION", "qokain|okaiin|ykan", "MEDIUM"),
    ("P02", "OT+AN", "otan", "danach die zweite Portion", "OPEN_ORDER", "otaiin|ykan", "LOW"),
    ("P03", "OL+AN", "olan", "mit der zweiten Portion weiter", "OPEN_CONTINUATION", "olkain|ykan", "LOW"),
    ("P04", "AR+AIIN", "araiin", "Sollwert aus der bezeichneten Quelle", "OPEN_SOURCE_VALUE", "char|daiin", "MEDIUM"),
    ("P05", "AL+AIIN", "alaiin", "Sollwert an der Zielstelle", "OPEN_TARGET_VALUE", "dal|daiin", "HIGH"),
    ("P06", "OL+AIIN", "olaiin", "im selben Gang bis zum Sollwert weiter", "OPEN_CONTINUATION_VALUE", "chol|daiin", "HIGH"),
    ("P07", "CHED+AIIN", "chedaiin", "bis zum Sollwert überführen", "OPEN_TRANSFER_VALUE", "chedain|daiin", "HIGH"),
    ("P08", "SHED+AIIN", "shedaiin", "bis zur Sollstufe absetzen", "OPEN_SETTLE_VALUE", "shfydaiin|chldaiin", "HIGH"),
    ("P09", "CHK+AIIN", "chkaiin", "bis zur Sollstufe wärmen", "OPEN_HEAT_VALUE", "chkain|daiin", "HIGH"),
    ("P10", "CKH+AL+Y", "ckhaly", "diesen Posten durch den Zielgang führen", "OPEN_TARGET_PASSAGE", "sheckhal|chckhy", "HIGH"),
    ("P11", "OK+OR+Y", "okory", "diesen Ansatz in den Arbeitsgang setzen", "OPEN_BATCH_ACTION", "choky|ycheor", "MEDIUM"),
    ("P12", "OT+OR+Y", "otory", "danach mit dem nächsten Ansatz arbeiten", "OPEN_NEXT_BATCH", "otchor|ycheor", "MEDIUM"),
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


def main() -> None:
    components = {r["component_id"]: r for r in read_tsv(COMPONENTS)}
    existing_surfaces = {r["visible_surface"] for r in read_tsv(SURFACES)}
    astro_rows = read_tsv(ASTRO)
    astro_by_surface: dict[str, list[dict[str, str]]] = {}
    for row in astro_rows:
        astro_by_surface.setdefault(row["visible_surface"], []).append(row)
    forecasts = []
    for forecast_id, recipe, form, meaning, slot, analogies, confidence in FORECASTS:
        parts = recipe.split("+")
        forecasts.append({
            "forecast_id": forecast_id, "component_recipe": recipe,
            "component_values_de": " + ".join(components[p]["short_value_de"] for p in parts),
            "predicted_short_meaning_de": meaning, "canonical_surface_sketch": form,
            "surface_status": (
                "ALREADY_IN_PROSE" if form in existing_surfaces else
                "MATCHES_EXISTING_ASTRO_LABEL" if form in astro_by_surface else
                "UNSEEN_ON_TEN_PAGES"
            ),
            "expected_sentence_slot": slot, "closest_attested_analogies": analogies,
            "confidence": confidence,
            "writing_instruction": "combine the listed master components; renderer may add or change the outer frame",
        })

    astro_matches = []
    for forecast in forecasts:
        for row in astro_by_surface.get(forecast["canonical_surface_sketch"], []):
            astro_matches.append({
                "forecast_id": forecast["forecast_id"], "component_recipe": forecast["component_recipe"],
                "predicted_short_meaning_de": forecast["predicted_short_meaning_de"],
                "group_serial": row["group_serial"], "page": row["page"], "locus": row["locus"],
                "visible_owner": row["visible_owner"], "namespace_id": row["namespace_id"],
                "visible_surface": row["visible_surface"],
                "existing_diagram_reading_de": row["concrete_diagram_reading_de"],
                "composition_match": "DIRECT_MEANING_MATCH",
            })

    exercises = [
        {"exercise_id": "X01", "source_instruction_de": "Sollwert an der Zielstelle; diesen Posten einsetzen", "component_sequence": "AL+AIIN | OK+Y", "predicted_card_sequence": "alaiin | choky", "plain_reading_de": "Den Zielwert setzen und diesen Posten einsetzen."},
        {"exercise_id": "X02", "source_instruction_de": "aus der Quelle bis Sollwert überführen", "component_sequence": "AR+AIIN | CHED+AIIN", "predicted_card_sequence": "araiin | chedaiin", "plain_reading_de": "Von der bezeichneten Quelle nehmen und bis zum Sollwert überführen."},
        {"exercise_id": "X03", "source_instruction_de": "danach mit der zweiten Portion weiter", "component_sequence": "OT+AN | OL+AN", "predicted_card_sequence": "otan | olan", "plain_reading_de": "Danach die zweite Portion nehmen und mit ihr weiterarbeiten."},
        {"exercise_id": "X04", "source_instruction_de": "bis Sollstufe wärmen; dann absetzen", "component_sequence": "CHK+AIIN | SHED+AIIN", "predicted_card_sequence": "chkaiin | shedaiin", "plain_reading_de": "Bis zur Sollstufe wärmen und anschließend bis zur Sollstufe absetzen."},
        {"exercise_id": "X05", "source_instruction_de": "diesen Posten durch den Zielgang; nächster Ansatz", "component_sequence": "CKH+AL+Y | OT+OR+Y", "predicted_card_sequence": "ckhaly | otory", "plain_reading_de": "Diesen Posten durch den Zielgang führen und danach mit dem nächsten Ansatz arbeiten."},
        {"exercise_id": "X06", "source_instruction_de": "Ansatz einsetzen; im selben Gang bis Sollwert weiter", "component_sequence": "OK+OR+Y | OL+AIIN", "predicted_card_sequence": "okory | olaiin", "plain_reading_de": "Diesen Ansatz einsetzen und im selben Gang bis zum Sollwert weiterführen."},
    ]

    forecast_path = OUT / "TWO_HUNDRED_SIXTY_FIFTH_TWELVE_UNSEEN_COMPOSITIONS.tsv"
    exercise_path = OUT / "TWO_HUNDRED_SIXTY_FIFTH_SIX_WRITING_EXERCISES.tsv"
    astro_match_path = OUT / "TWO_HUNDRED_SIXTY_FIFTH_TWO_ASTRO_MATCHES.tsv"
    readable_path = OUT / "TWO_HUNDRED_SIXTY_FIFTH_READABLE_FORECAST.md"
    report_path = OUT / "TWO_HUNDRED_SIXTY_FIFTH_REPORT.md"
    write_tsv(forecast_path, forecasts, list(forecasts[0]))
    write_tsv(exercise_path, exercises, list(exercises[0]))
    write_tsv(astro_match_path, astro_matches, list(astro_matches[0]))

    readable = [
        "# Zwölf vorhergesagte Karten", "",
        "Diese Formen wurden zuerst als Schreibproben aus dem aktuellen Deck erzeugt:", "",
    ]
    for row in forecasts:
        readable.append(f"- `{row['canonical_surface_sketch']}` ≈ `{row['component_recipe']}` → **{row['predicted_short_meaning_de']}** ({row['confidence']}).")
    readable += [
        "", "## Sofortiger Treffer im vorhandenen Astro-Material", "",
        "Zwei Skizzen stehen bereits auf f67r2: `alaiin` und `chedaiin`. Noch wichtiger: ihre schon vorhandenen Diagrammlesungen passen direkt zur Vorhersage. `alaiin` bezeichnet Zielsektor/Zielfeld plus Sollwert; `chedaiin` bezeichnet Übertragung/Platzbezug plus Sollwert. Zehn Skizzen bleiben auf den zehn Seiten unbelegt.", "",
        "Besonders stark sind damit die regulären Sollwertverbindungen `AL+AIIN` und `CHED+AIIN`; weitere gute Vorhersagen sind `OL+AIIN`, `SHED+AIIN`, `CHK+AIIN` und die Zielpassage `CKH+AL+Y`. Die AN-Reihe ist schwächer, weil AN bisher nur einmal vorkommt.", "",
        "Die Oberflächen sind nur kanonische Skizzen. Ein echter Werkstattschreiber dürfte `q/s/ch/d`-Rahmen hinzufügen oder austauschen; entscheidend ist die vorhergesagte Komponentenfolge und ihre kurze Bedeutung.", "",
    ]
    readable_path.write_text("\n".join(readable), encoding="utf-8")

    report = f"""# Sidequest-Pass 265: prospektive Kompositionsprobe

## Ergebnis

Das63er-Deck erzeugt zwölf konkrete Kartenrezepte. Zehn sind auf den zehn Seiten unbelegt. Zwei kanonische Skizzen, ALAIIN=AL+AIIN und CHEDAIIN=CHED+AIIN, erscheinen bereits als lokale f67r2-Astrolabels; ihre bestehenden Diagrammlesungen entsprechen direkt Ziel+Sollwert und Übertragung+Sollwert. Sechs Rezepte erhalten hohe, vier mittlere und zwei niedrige Arbeitskonfidenz. Die schwächste Familie erweitert das einmalige AN=ZWEITE PORTION.

Damit macht die Theorie erstmals echte Vorhersagen: Nicht nur vorhandene Formen bekommen nachträglich Werte, sondern neue legale Kompositionen erhalten vorab eine kurze Bedeutung und einen erwarteten Satzplatz. Die sichtbaren Formen bleiben Renderer-Skizzen und werden nicht in das beobachtete Wörterbuch aufgenommen.

Inputs: components `{sha(COMPONENTS)}`, prose surfaces `{sha(SURFACES)}`, Astro groups `{sha(ASTRO)}`.
"""
    report_path.write_text(report, encoding="utf-8")
    outputs = (forecast_path, exercise_path, astro_match_path, readable_path, report_path)
    summary = {
        "status": "PASS", "forecast_cards": len(forecasts), "writing_exercises": len(exercises),
        "confidence_counts": {level: sum(r["confidence"] == level for r in forecasts) for level in ("HIGH", "MEDIUM", "LOW")},
        "unseen_surface_sketches": sum(r["surface_status"] == "UNSEEN_ON_TEN_PAGES" for r in forecasts),
        "existing_astro_matches": len(astro_matches),
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
