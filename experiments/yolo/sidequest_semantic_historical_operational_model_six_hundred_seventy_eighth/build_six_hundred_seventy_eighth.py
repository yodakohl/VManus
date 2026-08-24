#!/usr/bin/env python3
"""Build the creative historical operational-model comparison for pass 678."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def write_tsv(name: str, rows: list[dict[str, object]]) -> None:
    path = HERE / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            delimiter="\t",
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


PROPERTIES = [
    ("P01", "SHORT_REUSABLE_SIGNS", "39 kurze wiederverwendbare Bedeutungs-/Kontrolleintraege"),
    ("P02", "LEARNED_WHOLE_ENTRIES", "exakte Ganzkarten und drei unteilbare Befehle"),
    ("P03", "EXACT_MASTER_LOOKUP", "Bedeutungsrezept wird erst ueber eine Mustertafel schreibbar"),
    ("P04", "SEMANTIC_COMPOSITION", "Bausteine bilden neue lesbare Arbeitsrezepte"),
    ("P05", "BOUND_GRADE", "E/EE/EEE modifiziert kurz/lang/voll"),
    ("P06", "POSITIONAL_ALLOGRAPH", "q/s und lokale Formen werden positionsabhaengig kopiert"),
    ("P07", "SILENT_VISUAL_OWNER", "Bild oder Diagramm liefert den unausgeschriebenen Besitzer"),
    ("P08", "MEASURE_AND_STAGE_SIGNS", "Portion Sollmass und Arbeitsstufe sind eigene Kurzwerte"),
    ("P09", "LINEAR_WORK_TEXT", "Karten laufen als fortgesetzte Arbeitsfolge ueber Zeilen"),
    ("P10", "MULTI_REGISTER_USE", "Herbal Bio und Himmeltafeln benutzen verwandte Schreibtechnik"),
]

MODELS = [
    (
        "M1_MIXED_ITALIAN_NOMENCLATOR",
        "italienische Kanzleichiffre 1379-1440",
        [2, 3, 3, 0, 0, 3, 0, 1, 3, 3],
        "beste Oberflaechenarchitektur: produktive Zeichen plus Ganzwerte Nulls und Varianten",
    ),
    (
        "M2_MEDICAL_BREVIGRAPH_APOTHECARY",
        "medizinische Brevigrafie und Apothekerzeichen ca.1450",
        [3, 2, 2, 1, 1, 3, 2, 3, 3, 3],
        "beste Schreibpraxis-Analogie fuer Kuerzel Masszeichen und gelernte Ganzformen im selben Band",
    ),
    (
        "M3_BDHD_ALCHEMICAL_CODE_ALPHABET",
        "Buch der heiligen Dreifaltigkeit ca.1416-1430",
        [2, 3, 3, 3, 1, 2, 3, 2, 2, 3],
        "bester einzelner Gesamtvergleich: kleines Fachalphabet Kombinationen Decknamen und Embleme",
    ),
    (
        "M4_PSEUDO_LULLIAN_COMBINATION",
        "lullische und pseudo-lullische Kombinatorik",
        [3, 1, 2, 3, 2, 1, 2, 2, 1, 3],
        "beste Analogie fuer semantische Kombination von Stoff Operation und Prozessstufe",
    ),
    (
        "M5_BLACK_MENSURAL_NOTATION",
        "schwarze Mensuralnotation spaetes14-fruehes15 Jahrhundert",
        [3, 1, 1, 1, 3, 3, 0, 2, 3, 1],
        "beste Analogie fuer gebundene Grade und positionsabhaengige Formwerte",
    ),
    (
        "M6_ALFONSINE_TABLE_LOOKUP",
        "Alfonsinische Tafeln 1401-1407",
        [2, 2, 3, 2, 2, 2, 3, 3, 1, 2],
        "beste Analogie fuer lokale Ring- oder Tabellenadresse plus kurzen eingetragenen Wert",
    ),
    (
        "M7_PICTURED_TECHNICAL_MODELBOOK",
        "illustriertes Werkstatt- und Ingenieurexemplar ca.1430",
        [1, 2, 2, 0, 1, 2, 3, 2, 3, 3],
        "beste Analogie fuer Bild-zuerst Produktion und stillen Gegenstand aber ohne Codegrammatik",
    ),
]


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)

    matrix_rows: list[dict[str, object]] = []
    ranking_rows: list[dict[str, object]] = []
    for model_id, label, scores, verdict in MODELS:
        total = sum(scores)
        ranking_rows.append(
            {
                "model_id": model_id,
                "historical_model": label,
                "creative_fit_total_of_30": total,
                "best_use": verdict,
            }
        )
        for (property_id, property_name, observed_system), score in zip(PROPERTIES, scores, strict=True):
            matrix_rows.append(
                {
                    "model_id": model_id,
                    "historical_model": label,
                    "property_id": property_id,
                    "property": property_name,
                    "our_working_system": observed_system,
                    "creative_fit_0_to_3": score,
                }
            )
    ranking_rows.sort(key=lambda row: (-int(row["creative_fit_total_of_30"]), str(row["model_id"])))
    for rank, row in enumerate(ranking_rows, start=1):
        row["rank"] = rank

    layer_rows = [
        {
            "layer_order": 1,
            "selected_layer": "PICTURE_OR_TABLE_OWNER",
            "historical_donor": "illustriertes Werkstattexemplar plus Alfonsinische Tafeln",
            "workshop_rule": "Bild Ring Feld oder Station waehlt zuerst den stillen Gegenstand und lokalen Namensraum.",
            "voynich_working_material": "Pflanze Becken Station Sternring Tabellenfeld",
        },
        {
            "layer_order": 2,
            "selected_layer": "SEMANTIC_RECIPE",
            "historical_donor": "Buch der heiligen Dreifaltigkeit plus pseudo-lullische Fachkombination",
            "workshop_rule": "Kurze Fachwerte fuer Handlung Stoff Menge Richtung Grad und Zustand zu einem Rezept ordnen.",
            "voynich_working_material": "39 Eintraege und 108 belegte Komponentenrezepte",
        },
        {
            "layer_order": 3,
            "selected_layer": "EXACT_CARD_NOMENCLATOR",
            "historical_donor": "gemischte italienische Kanzleichiffre plus medizinische Brevigrafie",
            "workshop_rule": "Laengster gelernter Eintrag hat Vorrang; das Rezept bestimmt die Bedeutung, die Tafel die exakte Ganzkarte.",
            "voynich_working_material": "173 exakte Karten davon drei unteilbare Befehle",
        },
        {
            "layer_order": 4,
            "selected_layer": "GRADE_AND_RENDERER",
            "historical_donor": "schwarze Mensuralnotation plus scribal abbreviation practice",
            "workshop_rule": "Gebundene Grade und Eintrittsallographen werden nur in lizenzierten Reihen angewandt und aus dem Exemplar kopiert.",
            "voynich_working_material": "E EE EEE; Y gegen lizenzierte DY-Endkarte; q/s Eintrittsformen",
        },
        {
            "layer_order": 5,
            "selected_layer": "READBACK",
            "historical_donor": "Werkstattlehre mit Musterbuch",
            "workshop_rule": "Karte atomar ruecklesen und erst mit Besitzer und aktivem Posten als Arbeitsanweisung aussprechen.",
            "voynich_working_material": "116 Aussagen und 11 fortlaufende Records",
        },
    ]

    crosswalk_rows = [
        {
            "working_feature": "OK_CHD_SH_ACTION_CORES",
            "selected_historical_mechanism": "alchemistisch-lullische Operationszeichen",
            "operational_reading": "gelernter stabiler Handlungswert in einem kurzen Fachrezept",
            "what_not_to_copy": "keine lateinische Lautung und keine konkrete historische Operation",
        },
        {
            "working_feature": "AIN_AIIN_IIN",
            "selected_historical_mechanism": "Apotheker- und Rechenzeichen fuer Menge Wert und Stufe",
            "operational_reading": "drei getrennte Parameterkarten statt Vokallaengen eines Wortes",
            "what_not_to_copy": "keine moderne Zahl und keine Unze ohne eigenen Anker",
        },
        {
            "working_feature": "E_EE_EEE",
            "selected_historical_mechanism": "mensuraler gebundener Grad",
            "operational_reading": "kurz laenger voll nur innerhalb lizenzierter Kartenreihen",
            "what_not_to_copy": "kein universelles E-Morphem in jeder sichtbaren Zeichenfolge",
        },
        {
            "working_feature": "Y_LICENSED_DY",
            "selected_historical_mechanism": "Grundwert gegen markierte Endform einer Notationsfamilie",
            "operational_reading": "laufender Posten bleibt aktiv; nur die gelernte Endkarte schliesst",
            "what_not_to_copy": "sichtbares dy ist nicht automatisch Satzende",
        },
        {
            "working_feature": "AR_AL_L_OL_OT",
            "selected_historical_mechanism": "tabellarische Adresse plus kurze Kanzleioperatoren",
            "operational_reading": "Quelle Ziel Weiterleitung Fortsetzung und Folge bleiben knappe Relationen",
            "what_not_to_copy": "keine erfundene Rohrgeometrie oder moderne Praepositionssyntax",
        },
        {
            "working_feature": "Q_S_ENTRY_FORMS",
            "selected_historical_mechanism": "diplomatische Varianten und positionsabhaengige Ligaturform",
            "operational_reading": "lokale Schreibform aus der Tafel kopieren nachdem die Karte gewaehlt ist",
            "what_not_to_copy": "q und s erhalten keine eigene Stoff- oder Aktionsbedeutung",
        },
        {
            "working_feature": "THREE_WHOLE_COMMANDS",
            "selected_historical_mechanism": "Nomenklatorwert oder gelernte Brevigrafe",
            "operational_reading": "laengster Ganzkarteneintrag blockiert kuenstliche Teilung",
            "what_not_to_copy": "innere Buchstabenfolgen werden nicht automatisch zu Wurzeln",
        },
        {
            "working_feature": "ABSENT_READABLE_RECIPES",
            "selected_historical_mechanism": "semantische Kombinatorik ohne freie Oberflaechenschrift",
            "operational_reading": "Bedeutung kann zusammensetzbar sein obwohl eine neue Karte erst der Meister eintragen muss",
            "what_not_to_copy": "keine neue Voynich-Oberflaeche aus Komponenten erfinden",
        },
        {
            "working_feature": "PICTURE_OWNER",
            "selected_historical_mechanism": "illustriertes Fach- oder Musterbuch",
            "operational_reading": "Bild liefert den Gegenstand; Text kodiert vor allem Aenderung Menge Richtung und Zustand",
            "what_not_to_copy": "kein exakt benannter Pflanzen- oder Koerperreferent ohne Bildanker",
        },
        {
            "working_feature": "ASTRO_LOCAL_NAMESPACE",
            "selected_historical_mechanism": "Alfonsinische Tabellen und lokale Diagrammadressen",
            "operational_reading": "Ring Feld und Position tragen einen Teil des Werts ausserhalb der Karte",
            "what_not_to_copy": "kein f68-f69 Schluessel und keine lineare Radleserichtung",
        },
    ]

    source_rows = [
        {"source_id": "S01", "system": "MIXED_ITALIAN_NOMENCLATOR", "date": "1379-1440", "witness": "Parma Venice Urbino cipher tables", "contribution": "alphabet syllables nulls variants and whole-word nomenclator", "url": "https://www.nsa.gov/portals/75/documents/about/cryptologic-heritage/historical-figures-publications/publications/misc/voynich_manuscript.pdf"},
        {"source_id": "S02", "system": "MEDICAL_BREVIGRAPH", "date": "ca.1450", "witness": "TCC O.1.77 Collectanea medica", "contribution": "productive abbreviation whole signs numerals and apothecary measures together", "url": "https://varieng.helsinki.fi/series/volumes/14/honkapohja/"},
        {"source_id": "S03", "system": "BDHD_ALCHEMICAL_CODE", "date": "1416-1430", "witness": "Buch der heiligen Dreifaltigkeit Wellcome MS.164 and GNM Hs.80061", "contribution": "small letter inventory three-letter metal identifiers operation letters and whole emblems", "url": "https://wellcomecollection.org/works/d3vapay8"},
        {"source_id": "S04", "system": "BDHD_ALCHEMICAL_CODE", "date": "ca.1420", "witness": "GNM Hs.80061 discussed by Obrist", "contribution": "letters for metals and alchemical operations", "url": "https://hyle.org/journal/issues/9-2/obrist.pdf"},
        {"source_id": "S05", "system": "LULLIAN_COMBINATION", "date": "1432 witness", "witness": "Ars brevis and Logica nova manuscript", "contribution": "memorized alphabet combined through pairs triples figures and tables", "url": "https://bvpb.mcu.es/es/consulta/registro.do?id=397905"},
        {"source_id": "S06", "system": "LULLIAN_COMBINATION", "date": "15th century", "witness": "Edinburgh MS 117 ff.1r-10v", "contribution": "alphabet and figures used to form propositions and questions", "url": "https://archives.collections.ed.ac.uk/repositories/2/archival_objects/169401"},
        {"source_id": "S07", "system": "MENSURAL_NOTATION", "date": "late14-early15", "witness": "Vat. Reg. lat.1146", "contribution": "base note values modified by shape position ligature and mensuration", "url": "https://digi.vatlib.it/mss/edition/MSS_Reg.lat.1146"},
        {"source_id": "S08", "system": "MENSURAL_NOTATION", "date": "1412", "witness": "Prosdocimus mensural treatise", "contribution": "in-window teachable rule culture for graded notation", "url": "https://www.corpusmusicae.com/msd/msd-samples/54-029-000spgs.pdf"},
        {"source_id": "S09", "system": "ALFONSINE_TABLES", "date": "1401-1404", "witness": "UPenn LJS 174", "contribution": "celestial labels combined with table position and numeric coordinate", "url": "https://openn.library.upenn.edu/Data/0001/html/ljs174.html"},
        {"source_id": "S10", "system": "PICTURED_TECHNICAL_MODELBOOK", "date": "ca.1431-1433", "witness": "Taccola De ingeneis III-IV Palatino 766", "contribution": "picture-first technical workshop material with measurements and hydraulics", "url": "https://brunelleschi.imss.fi.it/genscheda.asp?appl=LIR&chiave=100556&lingua=ENG&xsl=manoscritto"},
        {"source_id": "S11", "system": "MEDICAL_FORMULARY", "date": "14th century", "witness": "UAB Tractatus fol.20v", "contribution": "material measure operation duration endpoint and closure in a real recipe sequence", "url": "https://library.uab.edu/locations/reynolds/collections/medieval-renaissance-manuscripts/tractatus/folio-20v"},
        {"source_id": "S12", "system": "MERCHANT_MEASURE_NOTATION", "date": "1409", "witness": "Datini bill of exchange", "contribution": "productive number times memorized currency and measure units", "url": "https://www.paperinmotion.org/paper/bill-of-exchange-with-endorsement-on-security-from-antonio-di-neve-in-montpellier-to-francesco-di-marco-datini-and-his-partners-in-barcelona/"},
    ]

    write_tsv("SIX_HUNDRED_SEVENTY_EIGHTH_7_MODEL_RANKING.tsv", ranking_rows)
    write_tsv("SIX_HUNDRED_SEVENTY_EIGHTH_70_PROPERTY_MATRIX.tsv", matrix_rows)
    write_tsv("SIX_HUNDRED_SEVENTY_EIGHTH_5_LAYER_HYBRID.tsv", layer_rows)
    write_tsv("SIX_HUNDRED_SEVENTY_EIGHTH_10_RULE_CROSSWALK.tsv", crosswalk_rows)
    write_tsv("SIX_HUNDRED_SEVENTY_EIGHTH_12_HISTORICAL_SOURCES.tsv", source_rows)

    summary = {
        "status": "PASS",
        "models_compared": len(MODELS),
        "properties_per_model": len(PROPERTIES),
        "property_rows": len(matrix_rows),
        "highest_single_model": ranking_rows[0]["model_id"],
        "highest_single_model_score_of_30": ranking_rows[0]["creative_fit_total_of_30"],
        "selected_hybrid_layers": len(layer_rows),
        "rule_crosswalk_rows": len(crosswalk_rows),
        "historical_sources": len(source_rows),
        "selected_operational_model": "PICTURE_ADDRESSED_SEMANTIC_NOMENCLATOR_WITH_BOUND_GRADES_AND_EXACT_CARD_LOOKUP",
    }
    (HERE / "SIX_HUNDRED_SEVENTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
