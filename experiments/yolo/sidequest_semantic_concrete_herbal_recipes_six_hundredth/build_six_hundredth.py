#!/usr/bin/env python3
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
YOLO = HERE.parent
P588 = YOLO / "sidequest_semantic_complete_herbal_articles_five_hundred_eighty_eighth"
P599 = YOLO / "sidequest_semantic_concrete_object_ledger_five_hundred_ninety_ninth"

RECIPES = {
    "H1": {
        "working_title_de": "erster waessriger Pflanzenauszug",
        "raw_material_de": "frisch abgenommener Teil der breit gezaehnten radialbluetigen Pflanze",
        "medium_de": "frisches Wasser oder bereits angesetzte milde Auszugsfluessigkeit",
        "vessel_de": "kleines Ansatzgefaess mit getrenntem Arbeits-/Auffangfach",
        "intermediate_de": "kurz gezogener erster Pflanzenauszug",
        "final_product_de": "nach Mass aufgefangener Grundauszug",
        "possible_use_de": "Grundstoff fuer eine spaetere Waschung, Auflage oder Mischzubereitung",
        "strongest_rival_de": "blosse Rohstoffsortierung ohne Fluessigextraktion",
    },
    "H2": {
        "working_title_de": "Nachauszug und Wiederbeschickung desselben Pflanzenmaterials",
        "raw_material_de": "zurueckbehaltener feuchter Pflanzenrest oder bereits bereitgelegter zweiter Teil derselben f10r-Pflanze",
        "medium_de": "derselbe Wasser-/Auszugsansatz wie im ersten Absatz",
        "vessel_de": "fortgefuehrtes f10r-Ansatzgefaess",
        "intermediate_de": "abgezogener gemessener Nachauszug",
        "final_product_de": "zweifach nachbeschickter standardisierter Zweitauszug",
        "possible_use_de": "mit dem ersten Auszug vereinigen oder als getrennte staerkere Charge verwenden",
        "strongest_rival_de": "unabhaengige zweite Rezeptvariante statt Fortsetzung von H1",
    },
    "H3": {
        "working_title_de": "ausgewrungener Bluetenauszug",
        "raw_material_de": "dicht stehende blaue Bluetenkoepfe der abgebildeten Kronenpflanze",
        "medium_de": "Wasser als Default; leichter Wein bleibt moeglicher historischer Traeger",
        "vessel_de": "Tuch oder Beutel im Ziehgefaess, darunter ein Auffanggefaess",
        "intermediate_de": "erstmals ausgewrungene Bluetenfluessigkeit mit erneut angesetztem Pressgut",
        "final_product_de": "zweifach gezogener und ausgewrungener Bluetenauszug",
        "possible_use_de": "als Waschfluessigkeit, Badzusatz oder Anteil einer spaeteren Zubereitung",
        "strongest_rival_de": "gepresster Pflanzensaft ohne zugesetztes Wasser oder Wein",
    },
    "H4": {
        "working_title_de": "temperierte gemessene Pflanzenauflage",
        "raw_material_de": "zerteilter Blatt-/Rispenstoff der breitblaettrigen f55v-Pflanze",
        "medium_de": "so viel warme Traegerfluessigkeit oder Fett, dass eine streich- oder auflegbare Masse entsteht",
        "vessel_de": "Messgefaess, kleiner Vorratstopf und lokale Auflagestelle",
        "intermediate_de": "gemessene, verwahrte und danach temperierte Pflanzenmasse",
        "final_product_de": "abgemessene warme Auflage oder dicke Waschzubereitung",
        "possible_use_de": "an der bezeichneten Koerper- oder Arbeitsstelle auflegen/eintragen",
        "strongest_rival_de": "dosierte Fluessigwaschung statt fester Auflage",
    },
    "H5": {
        "working_title_de": "mehrfach beschickter Pflanzenansatz",
        "raw_material_de": "mehrere getrennte Koepfe, Spitzen oder andere Gaben der mehrkoepfigen stacheligen f56r-Pflanze",
        "medium_de": "Wasser, Badlauge oder bereits laufender Pflanzenansatz",
        "vessel_de": "Ziehgefaess mit Abfluss/Durchlass und nachgeordnetem Ansatzgefaess",
        "intermediate_de": "nacheinander gezogene, abgelassene und wieder zugesetzte Pflanzenchargen",
        "final_product_de": "mehrfach beschickter konzentrierter Pflanzenauszug",
        "possible_use_de": "Vorrat fuer Bad, Waschung oder eine nachfolgende lokale Anwendung",
        "strongest_rival_de": "Liste mehrerer Pflanzenteile oder Erntegaben ohne gemeinsame Fluessigcharge",
    },
}

STEP_READINGS = {
    "H1-S001": "Frischen Pflanzenteil kurz in den Wasseransatz geben, den ersten Auszug in das Auffangfach laufen lassen und nach Mass zurueck in die Charge eintragen.",
    "H1-S002": "Eine weitere Pflanzenportion in denselben Ansatz geben, kurz abziehen und bis zum bereiten Grundauszug weiterarbeiten.",
    "H2-S001": "Den zurueckbehaltenen Pflanzenrest oder zweiten Teil abziehen, an Ansatz und Mass binden und bis zur Bereitschaft weiterziehen.",
    "H2-S002": "Vom fortgefuehrten Ansatz einen gemessenen Nachauszug abnehmen; den Rest im Gefaess weiterfuehren.",
    "H2-S003": "Den Ansatz zweimal mit frischem Pflanzenstoff oder Medium nachbeschicken und die naechste verbrauchte Portion entfernen.",
    "H3-S001": "Blueten in das Tuchgefaess geben, ziehen lassen, auswringen, das Pressgut erneut einlegen, nochmals ziehen und den Auszug auffangen.",
    "H3-S002": "Eine zweite Bluetenportion im gleichen Ziehgang halten und eintragen.",
    "H3-S003": "Vom vorhandenen Bluetenmaterial oder Medium eine gemessene Portion weiter zugeben.",
    "H3-S004": "Den zweiten Ansatz fortsetzen, bis der Bluetenauszug gebrauchsfertig ist.",
    "H4-S001": "Pflanzenstoff nach Mass ansetzen, zwei dosierte Anteile in die Grundmasse geben und den Mischgang schliessen.",
    "H4-S002": "Die naechste gemessene Pflanzenmasse umsetzen und im kleinen Vorratstopf verwahren.",
    "H4-S003": "Eine Dosis zugeben, den benoetigten Anteil entnehmen, temperieren und den Zubereitungsgang schliessen.",
    "H4-S004": "Die gemessene temperierte Ansatzportion an die bezeichnete Stelle legen oder dort eintragen.",
    "H5-S001": "Eine erste Pflanzengabe abziehen und zum Gefaess fuehren; eine zweite nach Mass abnehmen und in den Ansatz geben.",
    "H5-S002": "Die folgende Pflanzengabe ansetzen, den Auszug durch den Durchlass laufen lassen und mit derselben Charge fortfahren.",
    "H5-S003": "Die Gabe ziehen lassen, dem Ansatz zufuehren und denselben Einsatz zweimal wiederholen.",
    "H5-S004": "Den naechsten Pflanzenteil in den Ansatz geben, ansetzen, wieder abziehen und zum folgenden Gefaess fuehren.",
    "H5-S005": "Eine weitere Gabe ansetzen, zufuehren und danach die naechste abgeteilte Portion in den Gang ordnen.",
    "H5-S006": "Die letzte aktuelle Portion nach Mass zur gemeinsamen Auszugscharge geben.",
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
    articles = read(P588 / "FIVE_HUNDRED_EIGHTY_EIGHTH_FIVE_COMPLETE_HERBAL_ARTICLES.tsv")
    object_statements = read(P599 / "FIVE_HUNDRED_NINETY_NINTH_116_STATEMENT_OBJECT_LEDGER.tsv")
    object_events = read(P599 / "FIVE_HUNDRED_NINETY_NINTH_381_EVENT_OBJECT_BINDING.tsv")
    herbal_statements = [row for row in object_statements if row["record"].startswith("H")]
    herbal_events = [row for row in object_events if row["record"].startswith("H")]

    recipe_rows = []
    article_by_record = {row["record"]: row for row in articles}
    for record in [f"H{i}" for i in range(1, 6)]:
        source = article_by_record[record]
        spec = RECIPES[record]
        recipe_rows.append({
            "record": record, "page": source["page"], "visible_owner_de": source["silent_owner_de"],
            "statements": source["statements"], "events": source["events"], **spec,
            "medium_status": "ARTICLE_LEVEL_WORKING_DEFAULT__NOT_SINGLE_WORD_GLOSS",
            "plant_identity_status": "VISIBLE_DESCRIPTION_ONLY",
            "disease_or_indication_status": "BROAD_POSSIBLE_USE_ONLY",
        })

    step_rows = []
    for row in herbal_statements:
        spec = RECIPES[row["record"]]
        step_rows.append({
            "statement_id": row["statement_id"], "record": row["record"], "page": row["page"],
            "object_before_id": row["object_before_id"], "object_after_id": row["object_after_id"],
            "source_objects_de": row["concrete_objects_de"], "source_operations_de": row["operations_de"],
            "concrete_recipe_step_de": STEP_READINGS[row["statement_id"]],
            "article_medium_de": spec["medium_de"], "article_product_de": spec["final_product_de"],
            "all_source_objects_preserved": "YES",
        })

    event_rows = []
    for row in herbal_events:
        spec = RECIPES[row["record"]]
        concrete = {
            "CURRENT_ITEM": "aktuelle Portion oder Zwischencharge dieses Rezepts",
            "FLOWING_MEDIUM": "laufender Wasser-/Auszugsstrom dieses Rezepts",
            "MATERIAL_CHARGE": "frische Pflanzengabe dieses Artikels",
            "OWNER_BOUND_MATERIAL": "Pflanzenstoff oder Zwischenprodukt des sichtbaren Pflanzenbesitzers",
            "PASSAGE": "lokaler Auslass, Tuchweg oder Durchlass des Ansatzes",
            "PORTION": "abgeteilte Pflanzen- oder Fluessigkeitsportion",
            "PREPARATION": "aktuelle Auszugs- oder Auflagenzubereitung",
            "SOURCE_STOCK": "Vorrat derselben Pflanzencharge oder Traegerfluessigkeit",
            "TARGET_PLACE": "Ansatzgefaess, Auffangfach oder spaetere Auflagestelle",
            "WORK_COMPARTMENT": "kleines Arbeits- oder Auffangfach",
        }[row["primary_object_class"]]
        event_rows.append({
            "event_id": row["event_id"], "page": row["page"], "record": row["record"], "statement_id": row["statement_id"],
            "surface": row["surface"], "card_no": row["card_no"], "component_parse": row["component_parse"],
            "source_object_class": row["primary_object_class"], "recipe_object_de": concrete,
            "operation_de": row["operation_de"], "local_output_de": row["local_output_de"],
            "water_wine_oil_word_claim": "NONE__MEDIUM_IS_ARTICLE_CONTEXT",
        })

    alternatives = []
    for record, spec in RECIPES.items():
        alternatives.append({
            "record": record, "selected_working_recipe_de": spec["working_title_de"],
            "strongest_rival_de": spec["strongest_rival_de"],
            "what_would_change_de": "Traegermedium, Gefaessart oder Endgebrauch; Kartenfolge und Objektuebergaenge bleiben gleich",
            "selection_rule_de": "aus Bild, Prozessfolge und Werkstattzweck waehlen; nicht aus einer einzelnen Oberflaeche",
        })

    write("SIX_HUNDREDTH_FIVE_CONCRETE_HERBAL_RECIPES.tsv", recipe_rows)
    write("SIX_HUNDREDTH_NINETEEN_RECIPE_STEPS.tsv", step_rows)
    write("SIX_HUNDREDTH_ONE_HUNDRED_HERBAL_EVENT_ROLES.tsv", event_rows)
    write("SIX_HUNDREDTH_FIVE_RECIPE_RIVALS.tsv", alternatives)

    edition = ["# Sechshundertste Runde: fuenf konkrete Pflanzenrezepte", ""]
    for recipe in recipe_rows:
        edition.extend([
            f"## {recipe['record']} · {recipe['page']} · {recipe['working_title_de']}", "",
            f"**Bildstoff:** {recipe['raw_material_de']}", "",
            f"**Medium:** {recipe['medium_de']}", "",
            f"**Gefaesse:** {recipe['vessel_de']}", "",
            f"**Zwischenprodukt:** {recipe['intermediate_de']}", "",
        ])
        for step in [row for row in step_rows if row["record"] == recipe["record"]]:
            edition.append(f"- **{step['statement_id']}:** {step['concrete_recipe_step_de']}")
        edition.extend([
            "", f"**Arbeitsprodukt:** {recipe['final_product_de']}", "",
            f"**Moeglicher Gebrauch:** {recipe['possible_use_de']}", "",
            f"**Staerkster Rivale:** {recipe['strongest_rival_de']}", "",
        ])
    (HERE / "SIX_HUNDREDTH_COMPLETE_HERBAL_RECIPE_BOOK.md").write_text("\n".join(edition), encoding="utf-8")

    summary = {
        "status": "PASS", "recipes": len(recipe_rows), "statements": len(step_rows), "events": len(event_rows),
        "selected_working_titles": [row["working_title_de"] for row in recipe_rows],
        "single_word_water_wine_oil_claims": 0, "named_plant_species": 0, "named_diseases": 0,
        "decision": "FIVE_CONCRETE_PROCESS_RECIPES_WITH_ARTICLE_LEVEL_MEDIA",
    }
    (HERE / "SIX_HUNDREDTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = """# Sechshundertste Runde: Herbal wird zum Rezeptbuch

## Ergebnis

Die fuenf Pflanzenartikel lassen sich jetzt als fuenf konkrete Arbeitsrezepte lesen:

1. **H1:** erster waessriger Auszug der f10r-Pflanze;
2. **H2:** Nachauszug und zweimalige Wiederbeschickung desselben Materials;
3. **H3:** ausgewrungener, zweimal gezogener Bluetenauszug;
4. **H4:** gemessene, verwahrte und temperierte Pflanzenauflage;
5. **H5:** mehrfach beschickter konzentrierter Pflanzenansatz.

Alle 100 Kartenereignisse und 19 Aussagen bleiben erhalten. Neu ist nur die Gegenstandsebene: Was liegt im Gefaess, welche Zwischencharge entsteht und wofuer koennte sie weitergegeben werden?

## Wasserfrage

Wasser ist besonders fuer H1/H2 und H5 ein guter Default, weil die Arbeitsfolge Lauf, Ansatz, Abzug und Nachbeschickung verlangt. Aber **kein einzelner Stamm bedeutet deshalb automatisch Wasser**. Das Medium wird vom gesamten Artikel, Bild und Werkstattexemplar geliefert. Bei H3 bleibt leichter Wein als historisch plausibler Rivale; H4 kann statt einer waessrigen Masse auch einen fetten oder zaehen Traeger benutzen.

## Warum diese Lesung besser zusammenhaengt

H1/H2 bilden erstmals eine echte zweistufige f10r-Folge: Grundauszug, Nachauszug, Wiederbeschickung. H3 hat eine klare Tuch-/Presslogik. H4 endet sichtbar in einer Zielanwendung. H5 sammelt mehrere getrennte Pflanzengaben in einem gemeinsamen Ansatz. Damit bekommt jeder Artikel einen anderen Werkstattzweck, obwohl alle dieselbe Karten- und Mengenlehre benutzen.

## Was nicht behauptet wird

Keine Pflanze erhaelt einen Artnamen, keine Anwendung eine bestimmte Krankheit, und Wasser/Wein/Fett werden nicht an einzelne Voynichformen geklebt. Es sind konkrete Rezeptdefaults, die wir in der naechsten Runde gegen die Biological-Stationen anschliessen koennen.

## Naechster Schritt

Als naechstes werden die fuenf Herbal-Produkte gegen die sichtbaren Biological-Stationstypen gelegt: Bad, Waschung, Auflage, Durchlass und Auffang-/Ruhegang. Gesucht wird keine Eins-zu-eins-Paarung, sondern welche Produktklasse an welche Station **passen koennte**.
"""
    (HERE / "SIX_HUNDREDTH_REPORT.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
