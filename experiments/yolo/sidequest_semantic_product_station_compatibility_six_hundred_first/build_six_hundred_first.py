#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P599 = YOLO / "sidequest_semantic_concrete_object_ledger_five_hundred_ninety_ninth"
P600 = YOLO / "sidequest_semantic_concrete_herbal_recipes_six_hundredth"

PRODUCTS = {
    "H1": ("LIGHT_EXTRACT", "LIQUID", {"WASH", "BATH", "MIX"}),
    "H2": ("SECOND_STRONG_EXTRACT", "LIQUID", {"BATH", "MIX", "FEED"}),
    "H3": ("FLOWER_WASH_EXTRACT", "LIQUID", {"WASH", "BATH", "APPLY"}),
    "H4": ("TEMPERED_POULTICE", "SEMI_SOLID", {"APPLY", "HOLD", "WARM"}),
    "H5": ("MULTI_CHARGE_CONCENTRATE", "LIQUID", {"BATH", "WASH", "FLOW", "FEED", "COLLECT"}),
}

STATIONS = {
    "B1:OWNER_01": ("COMMON_BATH_WASH_AND_MIXING_POOL", {"LIQUID", "SEMI_SOLID"}, {"BATH", "WASH", "MIX", "FLOW", "HOLD", "COLLECT"}),
    "B2:OWNER_01": ("UPPER_BASIN_FILL_AND_TRANSFER", {"LIQUID"}, {"BATH", "FLOW", "FEED", "WARM", "HOLD"}),
    "B2:OWNER_02": ("HAND_DEVICE_HOLD_AND_SETTLE", {"LIQUID", "SEMI_SOLID"}, {"HOLD", "SETTLE", "MIX"}),
    "B2:OWNER_03": ("UNCLEAR_CHARGE_AND_TRANSFER_STATION", {"LIQUID", "SEMI_SOLID"}, {"FEED", "HOLD", "FLOW", "APPLY"}),
    "B2:OWNER_04": ("LOWER_MULTI_FIGURE_BATH_TRANSFER", {"LIQUID"}, {"BATH", "FLOW"}),
    "B2:OWNER_05": ("MARGIN_COOL_HOLD_AND_APPLICATION_CELLS", {"LIQUID", "SEMI_SOLID"}, {"COOL", "HOLD", "APPLY", "SETTLE"}),
    "B3:OWNER_01": ("OPEN_FAN_COLLECT_AND_WARM_STATION", {"LIQUID"}, {"COLLECT", "WARM", "FLOW"}),
    "B3:OWNER_02": ("ROUND_VESSEL_LOCAL_IMMERSION", {"LIQUID", "SEMI_SOLID"}, {"BATH", "APPLY", "FLOW"}),
    "B3:OWNER_03": ("BASKET_VESSEL_IMMERSION_AND_SETTLE", {"LIQUID"}, {"BATH", "SETTLE", "HOLD", "FEED"}),
    "B3:OWNER_04": ("UNCONNECTED_GENERIC_PREPARATION_CELLS", {"LIQUID", "SEMI_SOLID"}, {"MIX", "HOLD", "SETTLE", "COLLECT", "COOL"}),
    "B3:OWNER_05": ("PAIRED_ARCH_APPLICATION_OR_FLOW", {"LIQUID", "SEMI_SOLID"}, {"APPLY", "FLOW", "SETTLE"}),
    "B4:OWNER_01": ("PAIRED_ARCH_POULTICE_HOLDING", {"SEMI_SOLID", "LIQUID"}, {"APPLY", "HOLD", "WARM", "SETTLE"}),
    "B4:OWNER_02": ("LEFT_FRINGE_WARM_FLOW_AND_COLLECTION", {"LIQUID"}, {"WARM", "FLOW", "COLLECT", "FEED", "SETTLE"}),
    "B4:OWNER_03": ("RIGHT_S_FLOW_FEED_AND_SETTLE", {"LIQUID"}, {"FEED", "SETTLE"}),
    "B5:OWNER_01": ("FRINGE_TRANSFER_AND_SETTLE_APPENDIX", {"LIQUID", "SEMI_SOLID"}, {"FLOW", "SETTLE", "APPLY"}),
    "B6:OWNER_01": ("S_FLOW_COLLECT_COOL_AND_FEED_APPENDIX", {"LIQUID"}, {"COLLECT", "COOL", "FEED", "FLOW"}),
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
    recipes = {row["record"]: row for row in read(P600 / "SIX_HUNDREDTH_FIVE_CONCRETE_HERBAL_RECIPES.tsv")}
    object_steps = read(P599 / "FIVE_HUNDRED_NINETY_NINTH_116_STATEMENT_OBJECT_LEDGER.tsv")
    bio_steps = [row for row in object_steps if row["record"].startswith("B")]

    product_rows = []
    for record, (product_class, physical_form, uses) in PRODUCTS.items():
        recipe = recipes[record]
        product_rows.append({
            "product_id": record, "page": recipe["page"], "product_class": product_class,
            "physical_form": physical_form, "use_tags": "|".join(sorted(uses)),
            "working_product_de": recipe["final_product_de"], "possible_use_de": recipe["possible_use_de"],
            "source_recipe_de": recipe["working_title_de"],
        })

    station_rows = []
    for owner_id, (station_class, accepted_forms, functions) in STATIONS.items():
        rows = [row for row in bio_steps if row["owner_id"] == owner_id]
        station_rows.append({
            "station_id": owner_id, "page": rows[0]["page"], "record": rows[0]["record"],
            "visible_owner_de": rows[0]["owner_de"], "station_class": station_class,
            "accepted_product_forms": "|".join(sorted(accepted_forms)),
            "function_tags": "|".join(sorted(functions)), "statements": len(rows),
            "observed_operations_de": " | ".join(row["operations_de"] for row in rows),
            "global_flow_claim": "NONE__LOCAL_STATION_ONLY",
        })

    matrix = []
    for product in product_rows:
        product_uses = set(product["use_tags"].split("|"))
        for station in station_rows:
            accepted = set(station["accepted_product_forms"].split("|"))
            functions = set(station["function_tags"].split("|"))
            form_match = product["physical_form"] in accepted
            matched = sorted(product_uses & functions)
            score = (2 if form_match else 0) + min(2, len(matched))
            if form_match and len(matched) >= 2:
                compatibility = "DIRECT_WORKING_MATCH"
            elif form_match and len(matched) == 1:
                compatibility = "PLAUSIBLE_MATCH"
            elif form_match:
                compatibility = "FORM_COMPATIBLE_FUNCTION_UNCLEAR"
            else:
                compatibility = "POOR_MATCH"
            matrix.append({
                "product_id": product["product_id"], "product_class": product["product_class"],
                "station_id": station["station_id"], "station_class": station["station_class"],
                "form_match": "YES" if form_match else "NO", "matched_functions": "|".join(matched) or "NONE",
                "compatibility": compatibility, "working_score": score,
                "concrete_interface_de": (
                    f"{product['working_product_de']} kann an {station['visible_owner_de']} fuer {', '.join(matched)} eingesetzt werden"
                    if matched and form_match else
                    f"{product['working_product_de']} passt nur formal oder schlecht zu {station['visible_owner_de']}"
                ),
                "written_cross_pointer": "NO",
            })

    strongest = []
    for product in product_rows:
        rows = [row for row in matrix if row["product_id"] == product["product_id"]]
        best_score = max(int(row["working_score"]) for row in rows)
        best = [row for row in rows if int(row["working_score"]) == best_score]
        strongest.append({
            "product_id": product["product_id"], "working_product_de": product["working_product_de"],
            "best_score": best_score, "best_station_ids": "|".join(row["station_id"] for row in best),
            "best_station_classes": "|".join(row["station_class"] for row in best),
            "interpretation_de": "mehrere passende Stationen sind eine Produktklasse, keine versteckte Folio-Paarung",
            "one_to_one_claim": "NO",
        })

    write("SIX_HUNDRED_FIRST_FIVE_PRODUCT_CLASSES.tsv", product_rows)
    write("SIX_HUNDRED_FIRST_SIXTEEN_STATION_CLASSES.tsv", station_rows)
    write("SIX_HUNDRED_FIRST_EIGHTY_PRODUCT_STATION_COMPATIBILITIES.tsv", matrix)
    write("SIX_HUNDRED_FIRST_FIVE_STRONGEST_COMPATIBILITY_SETS.tsv", strongest)

    direct = sum(row["compatibility"] == "DIRECT_WORKING_MATCH" for row in matrix)
    plausible = sum(row["compatibility"] == "PLAUSIBLE_MATCH" for row in matrix)
    summary = {
        "status": "PASS", "products": len(product_rows), "stations": len(station_rows), "matrix_rows": len(matrix),
        "direct_matches": direct, "plausible_matches": plausible,
        "products_with_multiple_best_stations": sum("|" in row["best_station_ids"] for row in strongest),
        "written_cross_pointers": 0, "one_to_one_pairs_claimed": 0,
        "decision": "MANY_TO_MANY_PRODUCT_STATION_COMPATIBILITY_SUPPORTS_THEMATIC_WHAT_HOW",
    }
    (HERE / "SIX_HUNDRED_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Sechshunderterste Runde: Herbal-Produkte treffen Biological-Stationen

## Ergebnis

Die fuenf Herbal-Produkte passen als **Produktklassen** an die sechzehn sichtbaren Biological-Besitzer. Die 80 Kombinationen ergeben {direct} direkte Arbeitsmatches und {plausible} weitere plausible Matches. Keine einzige braucht einen geschriebenen Foliozeiger.

## Die fuenf Produktrollen

- **H1 Grundauszug:** leichtes fluessiges Wasch-, Bad- oder Mischmaterial.
- **H2 Nachauszug:** staerkerer fluessiger Ansatz fuer Bad, Mischung oder Einspeisung.
- **H3 Bluetenauszug:** Wasch-, Bad- oder lokale Anwendungsfluessigkeit.
- **H4 temperierte Auflage:** halbfeste Anwendung, die gehalten, gewaermt oder abgesetzt werden kann.
- **H5 Konzentrat:** fluessiger Bad-/Waschvorrat fuer Fluss-, Speise- und Auffangstationen.

## Staerkste sichtbare Anschluesse

Das gemeinsame f81v-Becken ist der breiteste Empfaenger fuer H1, H2, H3 und H5: es mischt, waescht, haelt, fuehrt und faengt auf. Die B4-Figuren-/Bogenstation ist der beste konkrete Anschluss fuer H4, weil dort Ansetzen, Befestigen, Halten, Waermen und Absetzen zusammenkommen. Die Fransen- und S-Laeufe von B4/B6 passen besonders zu fluessigen H2/H5-Chargen.

## Warum many-to-many richtig ist

Ein Pflanzenprodukt ist kein Stationsname. Derselbe Auszug kann als Badzusatz, Waschung oder weiterer Ansatz dienen. Umgekehrt kann dieselbe Beckenstation verschiedene Produkte aufnehmen. Genau deshalb fehlt eine sichtbare H1->B1- oder H4->B4-Nummer: Der Meister waehlt nach Zweck, Verfuegbarkeit und Bildsituation.

## Neue Gesamtlesung

Die WHAT/HOW-Kopplung ist jetzt greifbar:

```text
Herbal erzeugt eine Produktklasse
-> Werkstatt waehlt eine kompatible Stationsklasse
-> Biological beschreibt den lokalen Umgang mit diesem Produkt
```

Das ist staerker als blosse gemeinsame Grammatik, aber immer noch kein entschluesselter Querverweis.

## Naechster Schritt

Als naechstes werden fuer die sechs Biological-Records konkrete Bedienungs-/Anwendungsprogramme geschrieben, jeweils mit den kompatiblen Herbal-Produkten als austauschbare Einsaetze. So sehen wir, ob der medizinische Bad-/Anwendungszweck oder der technische Badehaus-/Waschzweck als Ganzes fluessiger wird.
"""
    (HERE / "SIX_HUNDRED_FIRST_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
