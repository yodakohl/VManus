#!/usr/bin/env python3
"""Build the R1 Astro second edition from the frozen V22/V55 Astro ledgers."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, OrderedDict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
P22 = ROOT / "experiments/yolo/sidequest_theory_candidates_v22"
P55 = ROOT / "experiments/yolo/sidequest_theory_candidates_v55"
PAGES = ("f67r2", "f68r1", "f69v")
NAMESPACE = {"f67r2": "A67", "f68r1": "A68", "f69v": "A69"}
DIAGRAM = {"f67r2": "A1", "f68r1": "A2", "f69v": "A3"}


PLANETS = [
    (1, "Saturn", "kalt und trocken", "starke Eingriffe verschieben und nur mäßig behandeln", "Samstag"),
    (2, "Jupiter", "warm und feucht", "eine sanfte stärkende Anwendung begünstigen", "Donnerstag"),
    (3, "Mars", "heiß und trocken", "Schneiden und Aderlass am betroffenen Sektor meiden", "Dienstag"),
    (4, "Sonne", "warm und trocken", "mäßig erwärmen und Überhitzung meiden", "Sonntag"),
    (5, "Venus", "kühl und feucht", "Baden und Salben begünstigen", "Freitag"),
    (6, "Merkur", "wechselnd", "nach der eingestellten Bedingung dosieren", "Mittwoch"),
    (7, "Mond", "kühl und feucht", "Waschen und Ruhe bevorzugen", "Montag"),
]

ZODIAC = [
    (1, "Widder", "Kopf und Gesicht", "Januar"),
    (2, "Stier", "Hals und Kehle", "Februar"),
    (3, "Zwillinge", "Schultern, Arme und Hände", "März"),
    (4, "Krebs", "Brustkorb und Brust", "April"),
    (5, "Löwe", "Herz und oberen Rücken", "Mai"),
    (6, "Jungfrau", "Bauch und Eingeweide", "Juni"),
    (7, "Waage", "unteren Rücken und Nieren", "Juli"),
    (8, "Skorpion", "Geschlechtsteile und Blase", "August"),
    (9, "Schütze", "Hüften und Oberschenkel", "September"),
    (10, "Steinbock", "Knie", "Oktober"),
    (11, "Wassermann", "Schienbeine und Knöchel", "November"),
    (12, "Fische", "Füße", "Dezember"),
]

MANSIONS = [
    (1, "al-Sharatan", "die zwei Hörner"),
    (2, "al-Butayn", "der kleine Bauch"),
    (3, "al-Thurayya", "die Plejaden"),
    (4, "al-Dabaran", "der Nachfolger/Aldebaran"),
    (5, "al-Haqa", "das weiße Zeichen am Kopf"),
    (6, "al-Hana", "das Brandzeichen"),
    (7, "al-Dhira", "der Unterarm"),
    (8, "al-Nathra", "die Krippe"),
    (9, "al-Tarf", "das Auge"),
    (10, "al-Jabha", "die Stirn"),
    (11, "al-Zubra", "die Mähne"),
    (12, "al-Sarfa", "die Wende"),
    (13, "al-Awwa", "die Bellenden"),
    (14, "al-Simak", "die Hohe/Spica"),
    (15, "al-Ghafr", "die Bedeckung"),
    (16, "al-Zubana", "die Scheren"),
    (17, "al-Iklil", "die Krone"),
    (18, "al-Qalb", "das Herz/Antares"),
    (19, "al-Shawla", "der Stachel"),
    (20, "al-Naam", "die Strauße"),
    (21, "al-Balda", "der leere Ort"),
    (22, "Sad al-Dhabih", "das Glück des Schlachtenden"),
    (23, "Sad Bula", "das Glück des Verschlingenden"),
    (24, "Sad al-Suud", "das glücklichste Glück"),
    (25, "Sad al-Akhbiya", "das Glück der Zelte"),
    (26, "al-Fargh al-Muqaddam", "der vordere Ausguss"),
    (27, "al-Fargh al-Muakhkhar", "der hintere Ausguss"),
    (28, "Batn al-Hut", "der Bauch des Fisches"),
]

F69_TECH_RIVALS = [
    "den Warmgang nach Sonnenuntergang freigeben",
    "kühl spülen und dann stoppen",
    "Schneidarbeit aussetzen",
    "den Schmiergang freigeben",
    "am oberen Anschluss arbeiten",
    "die Charge ruhen lassen und nicht entleeren",
    "genau einen Spülgang abschließen",
    "überschüssige Flüssigkeit abziehen",
    "den Heißgang vermeiden",
    "am unteren Anschluss arbeiten",
    "den Beckengang freigeben",
    "den Spülgang einmal wiederholen",
    "dieselbe Charge verwenden",
    "den Beckengang bis lauwarm fahren",
    "den Beckengang freigeben",
    "den markierten Anschluss schmieren",
    "die Anlage in Ruhe halten",
    "ein kleineres Maß einstellen",
    "spülen und abschließen",
    "keinen zweiten Durchgang ausführen",
    "getrocknetes Arbeitsmaterial verwenden",
    "den Warmgang freigeben und dann stoppen",
    "den Standard-Beckengang unter dem Grenzwert fahren",
    "den Beckengang freigeben",
    "die Arbeitsflüssigkeit filtern",
    "gießen und abschließen",
    "ein warmes Filtertuch anbringen",
    "die Station prüfen und bei schwachem Lauf stoppen",
]


GERMAN = {
    "Aries: protect the head and face; avoid invasive treatment there": "Widder: Kopf und Gesicht schonen; dort keinen invasiven Eingriff vornehmen",
    "Taurus: protect the neck and throat; avoid invasive treatment there": "Stier: Hals und Kehle schonen; dort keinen invasiven Eingriff vornehmen",
    "Gemini: protect the shoulders, arms and hands; avoid invasive treatment there": "Zwillinge: Schultern, Arme und Hände schonen; dort keinen invasiven Eingriff vornehmen",
    "Cancer: protect the chest and breast; avoid invasive treatment there": "Krebs: Brustkorb und Brust schonen; dort keinen invasiven Eingriff vornehmen",
    "Leo: protect the heart and upper back; avoid invasive treatment there": "Löwe: Herz und oberen Rücken schonen; dort keinen invasiven Eingriff vornehmen",
    "Virgo: protect the belly and intestines; avoid invasive treatment there": "Jungfrau: Bauch und Eingeweide schonen; dort keinen invasiven Eingriff vornehmen",
    "Libra: protect the lower back and kidneys; avoid invasive treatment there": "Waage: unteren Rücken und Nieren schonen; dort keinen invasiven Eingriff vornehmen",
    "Scorpio: protect the genitals and bladder; avoid invasive treatment there": "Skorpion: Geschlechtsteile und Blase schonen; dort keinen invasiven Eingriff vornehmen",
    "Sagittarius: protect the hips and thighs; avoid invasive treatment there": "Schütze: Hüften und Oberschenkel schonen; dort keinen invasiven Eingriff vornehmen",
    "Capricorn: protect the knees; avoid invasive treatment there": "Steinbock: Knie schonen; dort keinen invasiven Eingriff vornehmen",
    "Aquarius: protect the shins and ankles; avoid invasive treatment there": "Wassermann: Schienbeine und Knöchel schonen; dort keinen invasiven Eingriff vornehmen",
    "Pisces: protect the feet; avoid invasive treatment there": "Fische: Füße schonen; dort keinen invasiven Eingriff vornehmen",
    "its ruling quality": "seine herrschende Qualität",
    "its application rule": "seine Anwendungsregel",
    "at night": "bei Nacht",
    "in the morning": "am Morgen",
    "for the sick person": "für die kranke Person",
    "at the affected place": "an der betroffenen Stelle",
    "repeat once": "einmal wiederholen",
    "do not overheat": "nicht überhitzen",
    "let it settle": "absetzen lassen",
    "then proceed": "danach fortfahren",
    "the favourable condition": "die günstige Bedingung",
    "the adverse condition": "die ungünstige Bedingung",
    "as written above": "wie oben geschrieben",
    "choose": "auswählen",
    "the governing influence": "den herrschenden Einfluss",
    "for this division": "für diesen Sektor",
    "when the Moon enters": "wenn der Mond eintritt",
    "use the indicated remedy": "das angezeigte Heilmittel verwenden",
    "avoid bleeding": "Aderlass meiden",
    "favour washing": "Waschen begünstigen",
    "favour purging": "Purgieren begünstigen",
    "apply while warm": "noch warm anwenden",
    "wait until the next station": "bis zur nächsten Station warten",
    "with the usual measure": "im üblichen Maß",
    "under the same governor": "unter demselben Regenten",
    "sevenfold governor 1: Saturn": "Siebenerregent 1: Saturn",
    "sevenfold governor 2: Jupiter": "Siebenerregent 2: Jupiter",
    "sevenfold governor 3: Mars": "Siebenerregent 3: Mars",
    "sevenfold governor 4: Sun": "Siebenerregent 4: Sonne",
    "sevenfold governor 5: Venus": "Siebenerregent 5: Venus",
    "sevenfold governor 6: Mercury": "Siebenerregent 6: Merkur",
    "sevenfold governor 7: Moon": "Siebenerregent 7: Mond",
    "house 1: life and body": "Haus 1: Leben und Leib",
    "house 2: goods and wealth": "Haus 2: Gut und Vermögen",
    "house 3: siblings and messages": "Haus 3: Geschwister und Botschaften",
    "house 4: home and land": "Haus 4: Heim und Land",
    "house 5: children and pleasure": "Haus 5: Kinder und Vergnügen",
    "house 6: illness and service": "Haus 6: Krankheit und Dienst",
    "house 7: marriage and partners": "Haus 7: Ehe und Partner",
    "house 8: death and inheritance": "Haus 8: Tod und Erbschaft",
    "house 9: journeys and learning": "Haus 9: Reisen und Lernen",
    "house 10: office and dignity": "Haus 10: Amt und Würde",
    "house 11: friends and aid": "Haus 11: Freunde und Hilfe",
    "house 12: confinement and hidden enemies": "Haus 12: Einschließung und verborgene Feinde",
    "its permitted application": "seine erlaubte Anwendung",
    "its warning": "seine Warnung",
    "central condition sector 1: hot and dry": "Zentralbedingung 1: heiß und trocken",
    "central condition sector 2: warm and dry": "Zentralbedingung 2: warm und trocken",
    "central condition sector 3: warm and moist": "Zentralbedingung 3: warm und feucht",
    "central condition sector 4: hot and moist": "Zentralbedingung 4: heiß und feucht",
    "central condition sector 5: cold and moist": "Zentralbedingung 5: kalt und feucht",
    "central condition sector 6: cool and moist": "Zentralbedingung 6: kühl und feucht",
    "central condition sector 7: cool and dry": "Zentralbedingung 7: kühl und trocken",
    "central condition sector 8: cold and dry": "Zentralbedingung 8: kalt und trocken",
    "identify": "bestimmen",
    "the lunar station": "die Mondstation",
    "by its drawn place": "nach ihrer gezeichneten Lage",
    "and consult its rule": "und ihre lokale Regel nachschlagen",
    "without changing the catalogue order": "ohne die Kataloglage zu verändern",
    "the Moon governing the twenty-eight stations": "der Mond als Besitzer der achtundzwanzig Stationen",
    "the Moon": "der Mond",
    "governs": "beherrscht",
    "the whole circuit": "den ganzen Kreis",
    "of twenty-eight": "von achtundzwanzig",
    "lunar stations": "Mondstationen",
    "apply the remedy": "das Heilmittel anwenden",
    "if adverse, withhold it": "bei ungünstiger Bedingung zurückhalten",
    "keep the usual measure": "das übliche Maß einhalten",
    "continue to the next station": "zur nächsten Station fortfahren",
    "repeat only once": "nur einmal wiederholen",
    "close the consultation": "die Konsultation schließen",
    "when the Moon reaches the station": "wenn der Mond die Station erreicht",
    "inspect the pictured schedule": "die gezeichnete Tafel prüfen",
    "if the condition is favourable": "wenn die Bedingung günstig ist",
    "favorable for a warm bath": "für ein Warmbad günstig",
    "especially after sunset": "besonders nach Sonnenuntergang",
    "use a cool washing": "eine kühle Waschung verwenden",
    "then stop": "danach aufhören",
    "avoid bloodletting": "Aderlass meiden",
    "favorable for anointing": "für eine Salbung günstig",
    "apply to the upper body": "am Oberkörper anwenden",
    "rest and give no purge": "ruhen lassen und nicht purgieren",
    "complete a single rinse": "genau eine Spülung abschließen",
    "draw off excess fluid": "überschüssige Flüssigkeit abziehen",
    "avoid a hot bath": "ein heißes Bad meiden",
    "apply below the waist": "unterhalb der Taille anwenden",
    "favorable for bathing": "für Baden günstig",
    "repeat the wash once": "die Waschung einmal wiederholen",
    "use the same preparation": "denselben Ansatz verwenden",
    "bathe until gently warm": "baden, bis es gelind warm ist",
    "anoint the affected place": "die betroffene Stelle salben",
    "keep the patient at rest": "die kranke Person ruhen lassen",
    "use a smaller measure": "ein kleineres Maß verwenden",
    "rinse and finish": "spülen und abschließen",
    "avoid a second application": "eine zweite Anwendung meiden",
    "use the dried herb": "das getrocknete Kraut verwenden",
    "make the ordinary bath": "das gewöhnliche Bad bereiten",
    "under the stated limit": "unter der angegebenen Grenze",
    "strain the herbal liquor": "den Kräuterauszug seihen",
    "pour and finish": "gießen und abschließen",
    "apply a warm cloth": "ein warmes Tuch auflegen",
    "observe the mansion": "das Mondhaus beobachten",
    "withhold treatment if weak": "bei Schwäche die Behandlung zurückhalten",
}


def header(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return next(csv.reader(handle, delimiter="\t"))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def guarded_astro(path: Path) -> list[dict[str, str]]:
    columns = header(path)
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in PAGES:
        cmd.extend(("--allow", page))
    cmd.extend(("--columns", ",".join(columns), "--forbid-prefix", "f84"))
    result = subprocess.run(cmd, cwd=ROOT, check=True, text=True, capture_output=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in columns})


def locus_number(locus: str) -> int:
    return int(locus.rsplit(".", 1)[1])


def station_number(page: str, locus: str) -> int | None:
    number = locus_number(locus)
    if page == "f68r1" and 9 <= number <= 36:
        return number - 8
    if page == "f69v" and 4 <= number <= 31:
        return number - 3
    return None


def german_default(row: dict[str, str]) -> str:
    if row["source_class"] == "SPATIAL_LUNAR_STATION":
        index = station_number(row["page"], row["locus"])
        assert index is not None
        _, name, mnemonic = MANSIONS[index - 1]
        return f"Bildadresse S{index:02d}: Lehrrotation R0 setzt hier Mondhaus M{index:02d} {name} ({mnemonic})"
    value = GERMAN.get(row["default_English"])
    if value is None:
        raise KeyError(f"missing German default: {row['default_English']!r}")
    return value


def locus_role(page: str, locus: str) -> str:
    number = locus_number(locus)
    if page == "f67r2":
        if 1 <= number <= 12:
            return "TWELVE_ZODIAC_BODY_SECTOR"
        if number in {15, 22, 28, 31, 34, 37, 47}:
            return "SEVEN_PLANET_GOVERNOR"
        if 52 <= number <= 63:
            return "TWELVE_HOUSE_CONTROL_INVENTORY"
        if 64 <= number <= 71:
            return "EIGHT_CONDITION_CONTROL_INVENTORY"
        return "SELECTOR_RUBRIC_OR_INSTRUCTION"
    if page == "f68r1":
        if number == 8:
            return "CENTRAL_OWNER"
        if 9 <= number <= 36:
            return "SPATIAL_STATION"
        if number == 37:
            return "CENTRAL_LEGEND"
        return "CATALOGUE_RUBRIC_OR_ANCHOR"
    if number <= 3:
        return "CIRCULAR_RUBRIC_BAND"
    return "ORDERED_RULE_ENTRY"


def address(page: str, locus: str, role: str) -> str:
    number = locus_number(locus)
    if page == "f67r2" and role == "TWELVE_ZODIAC_BODY_SECTOR":
        return f"A67:Z{number:02d}"
    if page == "f67r2" and role == "SEVEN_PLANET_GOVERNOR":
        planet_loci = [15, 22, 28, 31, 34, 37, 47]
        return f"A67:P{planet_loci.index(number)+1:02d}"
    if page == "f67r2" and role == "TWELVE_HOUSE_CONTROL_INVENTORY":
        return f"A67:H{number-51:02d}"
    if page == "f67r2" and role == "EIGHT_CONDITION_CONTROL_INVENTORY":
        return f"A67:C{number-63:02d}"
    if page == "f68r1" and role == "SPATIAL_STATION":
        return f"A68:S{number-8:02d}"
    if page == "f68r1" and role in {"CENTRAL_OWNER", "CENTRAL_LEGEND"}:
        return "A68:CENTER"
    if page == "f69v" and role == "ORDERED_RULE_ENTRY":
        return f"A69:R{number-3:02d}"
    return f"{NAMESPACE[page]}:RUBRIC:L{number:02d}"


def rival_for(page: str, locus: str, role: str, german: str) -> str:
    number = locus_number(locus)
    if page == "f67r2" and role == "TWELVE_ZODIAC_BODY_SECTOR":
        return f"[RIVALE_KALENDER] Monatsabschnitt {ZODIAC[number-1][3]} statt Tierkreis-/Körpersektor"
    if page == "f67r2" and role == "SEVEN_PLANET_GOVERNOR":
        planet_loci = [15, 22, 28, 31, 34, 37, 47]
        p = PLANETS[planet_loci.index(number)]
        return f"[RIVALE_KALENDER] Wochentag {p[4]} statt Planetenregent {p[1]}"
    if page == "f67r2":
        return "[RIVALE_LEHRTAFEL] denselben lokalen Rubrikplatz als kopiertes Astronomiebeispiel lesen"
    if page == "f68r1" and role == "SPATIAL_STATION":
        return f"[RIVALE_STERNKATALOG] Merklocus S{number-8:02d} ohne Mondhausname oder Kalenderlauf"
    if page == "f68r1":
        return "[RIVALE_STERNKATALOG] Anleitung eines räumlichen Sternnamenspeichers"
    if role == "ORDERED_RULE_ENTRY":
        return f"[RIVALE_ARBEITSKALENDER] {F69_TECH_RIVALS[number-4]}"
    transformed = german.replace("Heilmittel", "Arbeitsmittel").replace("Konsultation", "Buchung").replace("Mond", "Zeiger")
    return f"[RIVALE_ARBEITSKALENDER] {transformed}"


def main() -> None:
    source = guarded_astro(P22 / "V22_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv")
    source.sort(key=lambda r: (PAGES.index(r["page"]), locus_number(r["locus"]), int(r["event_index"])))
    f69_source_rules = read_tsv(P22 / "V22_F69_28_RULES.tsv")
    v55_diagrams = {row["folio"]: row for row in read_tsv(P55 / "V55_SELECTED_THREE_DIAGRAMS.tsv")}
    assert len(source) == 395

    grouped: OrderedDict[tuple[str, str], list[dict[str, str]]] = OrderedDict()
    for row in source:
        grouped.setdefault((row["page"], row["locus"]), []).append(row)
    assert len(grouped) == 142

    group_rows: list[dict[str, object]] = []
    for row in source:
        role = locus_role(row["page"], row["locus"])
        local_address = address(row["page"], row["locus"], role)
        german = german_default(row)
        group_rows.append(
            {
                "page": row["page"],
                "diagram_id": DIAGRAM[row["page"]],
                "page_namespace": NAMESPACE[row["page"]],
                "locus": row["locus"],
                "locus_role": role,
                "inventory_address": local_address,
                "group_index_in_locus": row["event_index"],
                "surface_display_only": row["surface"],
                "astro_local_group_id": row["exact_tuple_id"],
                "source_event_serial": row["source_event_serial"],
                "v22_local_default_English": row["default_English"],
                "german_group_default": f"[ASTRO_LOKAL_EXEMPLAR; KEINE_PROSAKARTE] {german}",
                "competing_value_system": rival_for(row["page"], row["locus"], role, german),
                "source_class": row["source_class"],
                "confidence": row["confidence"],
                "binding_status": "PAGE_LOCAL_EXEMPLAR;SURFACE_HAS_NO_IMPORTED_MEANING",
                "cross_page_join": "NONE",
                "source_lineage": "V22_SELECTED_ASTRO_LEDGER+V55_SELECTED_ARCHITECTURE+V66_R1",
            }
        )
    write_tsv(OUT / "V66_R1_395_GROUP_INTERLINEAR.tsv", group_rows, list(group_rows[0]))

    f69_rule_by_locus = {row["locus"]: row for row in f69_source_rules}
    locus_rows: list[dict[str, object]] = []
    for (page, locus), rows in grouped.items():
        role = locus_role(page, locus)
        local_address = address(page, locus, role)
        parts = [german_default(row) for row in rows]
        number = locus_number(locus)
        primary = " ; ".join(parts)
        layout = "N/A"
        orientation = "NOT_CYCLIC"
        if page == "f68r1" and role == "SPATIAL_STATION":
            idx = number - 8
            _, name, mnemonic = MANSIONS[idx - 1]
            primary = f"Bildadresse S{idx:02d} aufsuchen; in Lehrrotation R0 als M{idx:02d} {name} ({mnemonic}) memorieren"
            orientation = "R0_IS_EDITORIAL_ONLY;55_OTHER_ROTATION_DIRECTION_ALTERNATIVES_LIVE"
        if page == "f69v" and role == "ORDERED_RULE_ENTRY":
            rule = f69_rule_by_locus[locus]
            primary = GERMAN[rule["selected_concrete_rule"].split("; ")[0]]
            if "; " in rule["selected_concrete_rule"]:
                primary = " ; ".join(GERMAN[part] for part in rule["selected_concrete_rule"].split("; "))
            layout = rule["layout_parity"]
            orientation = "SOURCE_RULE_ORDER_FIXED;CYCLIC_START_DIRECTION_UNPROVEN;LONG_SHORT_NO_POLARITY"
        locus_rows.append(
            {
                "page": page,
                "diagram_id": DIAGRAM[page],
                "page_namespace": NAMESPACE[page],
                "locus": locus,
                "locus_ordinal_on_page": number,
                "locus_role": role,
                "inventory_address": local_address,
                "group_count": len(rows),
                "astro_local_group_ids": "|".join(row["exact_tuple_id"] for row in rows),
                "surface_sequence_display_only": " ".join(row["surface"] for row in rows),
                "german_group_parts": " | ".join(parts),
                "complete_german_locus_default": f"[ASTRO_LOKAL_EXEMPLAR; KEINE_PROSAKARTE] {primary}",
                "competing_locus_value": rival_for(page, locus, role, primary),
                "layout_class": layout,
                "orientation_status": orientation,
                "cross_page_join": "NONE",
                "teaching_action": "Bildadresse zeigen; sichtbare Gruppenfolge kopieren; nur im Seitennamensraum den Exemplarwert aufsagen; Rücklesung an derselben Adresse prüfen",
            }
        )
    write_tsv(OUT / "V66_R1_142_LOCUS_EDITION.tsv", locus_rows, list(locus_rows[0]))

    grid_rows: list[dict[str, object]] = []
    for p_idx, p_name, quality, p_rule, weekday in PLANETS:
        for z_idx, sign, body, month in ZODIAC:
            grid_rows.append(
                {
                    "configuration_id": f"A67:P{p_idx:02d}xZ{z_idx:02d}",
                    "planet_axis_index": p_idx,
                    "planet_default": p_name,
                    "planet_quality_exemplar": quality,
                    "zodiac_axis_index": z_idx,
                    "zodiac_default": sign,
                    "body_sector_exemplar": body,
                    "medical_configuration_default": f"[IATROMED_EXEMPLAR] Unter {p_name} im {sign}: {body} schonen; {p_rule}.",
                    "calendar_rival_default": f"[KALENDER_RIVALE] {weekday} im Monatsabschnitt {month}: den lokalen Werkstattposten nach Wochen- und Monatsrubrik auswählen.",
                    "visible_matrix_cell": "NO_DERIVED_FROM_TWO_VISIBLE_INVENTORIES",
                    "composition_rule": "CHOOSE_ONE_A67_PLANET+CHOOSE_ONE_A67_ZODIAC;DO_NOT_READ_AS_GROUP_TEXT",
                }
            )
    write_tsv(OUT / "V66_R1_F67_84_CONFIGURATION_TABLE.tsv", grid_rows, list(grid_rows[0]))

    source_group_by_locus = {locus: rows[0] for (page, locus), rows in grouped.items() if page == "f68r1" and 9 <= locus_number(locus) <= 36}
    station_rows: list[dict[str, object]] = []
    for idx, name, mnemonic in MANSIONS:
        locus = f"f68r1.{idx+8}"
        row = source_group_by_locus[locus]
        station_rows.append(
            {
                "station_address": f"A68:S{idx:02d}",
                "source_locus": locus,
                "surface_display_only": row["surface"],
                "astro_local_group_id": row["exact_tuple_id"],
                "editorial_mansion_id_R0": f"M{idx:02d}",
                "conventional_name_exemplar": name,
                "german_memory_image": mnemonic,
                "complete_default": f"[ASTRO_LOKAL_EXEMPLAR] S{idx:02d}: {name}, {mnemonic}; nur in Lehrrotation R0",
                "strongest_rival": f"[STERNKATALOG_RIVALE] individueller Merklocus S{idx:02d} ohne Mondhaus- oder Zeitwert",
                "orientation_status": "NO_AUTHORIAL_START_OR_DIRECTION;R0_EDITORIAL;55_ALTERNATIVES_LIVE",
                "cross_page_join": "NONE",
            }
        )
    write_tsv(OUT / "V66_R1_F68_28_STATIONS.tsv", station_rows, list(station_rows[0]))

    rule_rows: list[dict[str, object]] = []
    for row in f69_source_rules:
        idx = int(row["station_index"])
        parts = row["selected_concrete_rule"].split("; ")
        medical = " ; ".join(GERMAN[part] for part in parts)
        rule_rows.append(
            {
                "rule_address": f"A69:R{idx:02d}",
                "source_locus": row["locus"],
                "surface_entry_display_only": row["surface_entry"],
                "medical_regimen_default": f"[ASTRO_LOKAL_EXEMPLAR] {medical}",
                "technical_calendar_rival": f"[ARBEITSKALENDER_RIVALE] {F69_TECH_RIVALS[idx-1]}",
                "layout_class": row["layout_parity"],
                "layout_polarity": "NONE",
                "ordered_rule_index": idx,
                "cyclic_orientation_status": "SOURCE_ORDER_FIXED;START_AND_DIRECTION_NOT_PROMOTED_TO_F68_MAPPING",
                "cross_page_join": "NONE",
            }
        )
    write_tsv(OUT / "V66_R1_F69_28_RULES.tsv", rule_rows, list(rule_rows[0]))

    orientation_rows: list[dict[str, object]] = []
    for system in ("A68_SPATIAL", "A69_RULE_TRAVERSAL"):
        prefix = "S" if system.startswith("A68") else "R"
        for direction, step in (("ASC", 1), ("DESC", -1)):
            for offset in range(28):
                sequence = [((offset + step * i) % 28) + 1 for i in range(28)]
                if system.startswith("A68"):
                    mapping = "|".join(f"S{i+1:02d}=M{sequence[i]:02d}" for i in range(28))
                    status = "ALL_56_ASSIGNMENTS_STRUCTURALLY_LIVE;R0_ASC_ONLY_EDITORIAL_TEACHING_DEFAULT"
                else:
                    mapping = "|".join(f"STEP{i+1:02d}=R{sequence[i]:02d}" for i in range(28))
                    status = "RULES_STAY_AT_SOURCE_LOCI;56_TRAVERSALS_PUBLISHED;NO_F68_BINDING"
                orientation_rows.append(
                    {
                        "system": system,
                        "orientation_id": f"{system}_{direction}_R{offset:02d}",
                        "direction": direction,
                        "rotation_offset": offset,
                        "full_mapping_or_traversal": mapping,
                        "evidence_preference": "NONE",
                        "teaching_default": "YES_EDITORIAL_ONLY" if direction == "ASC" and offset == 0 else "NO",
                        "status": status,
                        "cross_page_join": "NONE",
                    }
                )
    write_tsv(OUT / "V66_R1_ORIENTATION_ALTERNATIVES.tsv", orientation_rows, list(orientation_rows[0]))

    contract_rows = [
        {
            "page": "f67r2",
            "namespace": "A67",
            "visible_inventory": "7 Regenten + 12 Tierkreis-/Körpersektoren + 12 Häuser + 8 Bedingungen + Rubriken",
            "productive_rule": "7×12-Auswahl wird als abgeleitete Konsultation komponiert; keine 84 sichtbaren Zellen behaupten",
            "allowed_external_exemplar": "Planeten, Tierkreis/Melothesie, Häuser, Qualitäten",
            "forbidden_transfer": "keine Prosa-Karte; kein A68/A69-Wert",
            "cross_page_join": "NONE",
        },
        {
            "page": "f68r1",
            "namespace": "A68",
            "visible_inventory": "Zentrum + 28 räumliche Stationen",
            "productive_rule": "Station ausschließlich an Bildadresse S01–S28 finden; Namen nur unter markierter Lehrrotation",
            "allowed_external_exemplar": "28 arabisch abgeleitete Mondhausnamen als rotierbares Merkinventar",
            "forbidden_transfer": "kein f69-Regelindex; keine Prosa-Karte",
            "cross_page_join": "NONE",
        },
        {
            "page": "f69v",
            "namespace": "A69",
            "visible_inventory": "3 Kreisrubriken + 28 geordnete lokale Regeln",
            "productive_rule": "Regeln an R01–R28 ausführen; LONG/SHORT nur als Schreitraum behandeln",
            "allowed_external_exemplar": "Regimen-/Wahlregeln oder technischer Arbeitskalender",
            "forbidden_transfer": "kein f68-Stationsindex; keine Prosa-Karte",
            "cross_page_join": "NONE",
        },
    ]
    write_tsv(OUT / "V66_R1_NAMESPACE_CONTRACT.tsv", contract_rows, list(contract_rows[0]))

    loci_by_page = {page: [row for row in locus_rows if row["page"] == page] for page in PAGES}
    diagram_meta = {
        "f67r2": {
            "title": "Siebenerregent × Zwölfer-Körpersektor",
            "workflow": "A67-Deck wählen; einen Planetenregenten und einen Tierkreis-/Körpersektor nehmen; 7×12-Regel komponieren; Haus- und Bedingungsinventar nur als Zusatzkontrolle lesen; Ergebnis rückwärts auf beide Karten zeigen.",
            "rival": "Sieben Wochentage × zwölf Monatsabschnitte als allgemeine Arbeitstafel",
            "contradiction": "Die Seite zeigt keine vollständige 84-Zellen-Matrix und kein Label ist als Planet, Zeichen oder Körperteil identifiziert.",
            "orientation": "keine Kreisrotation nötig; konventionelle Achsenordnung ist Exemplar, nicht sichtbarer Start",
            "purpose": "WHEN/BEDINGUNG für V64/V65 nur auf Gattungsebene; keine Recordadresse",
        },
        "f68r1": {
            "title": "Zentrum plus 28 räumliche Mondhaus-Merkstationen",
            "workflow": "A68-Zentrum setzen; Station an ihrer gezeichneten Lage S01–S28 zeigen; sichtbares Label kopieren; unter der ausdrücklich gewählten Lehrrotation den Mondhausnamen aufsagen; niemals eine Nummer nach A69 tragen.",
            "rival": "räumlicher Sternnamens- oder Merkkatalog ohne Kalenderlauf",
            "contradiction": "28 passt zu Mondhäusern, doch Start, Richtung und historische Namen fehlen vollständig.",
            "orientation": "56 Rotations-/Richtungsalternativen gleichrangig publiziert; R0_ASC nur Lehrdefault",
            "purpose": "selbständiger räumlicher WHEN-Merkkatalog; kein Schlüssel zu V64/V65 oder f69",
        },
        "f69v": {
            "title": "Geordnete 28 Regimen-/Wahlregeln",
            "workflow": "A69-Kreisrubriken lesen; R01–R28 in lokaler Quellordnung buchen; jede Regel vollständig ausführen; identisches okeod an R11/R15/R24 gleich lesen; LONG/SHORT nicht als günstig/ungünstig deuten.",
            "rival": "unabhängiger 28er Arbeits-, Wartungs- und Loskalender",
            "contradiction": "Keine Regelbedeutung ist extern verankert; Start/Richtung erzeugen keinen sichtbaren Anschluss an f68.",
            "orientation": "sichtbare Regelorte bleiben fest; 56 mögliche zyklische Traversalen publiziert, ohne f68-Abbildung",
            "purpose": "lokaler WHEN-/REGIMEN-Anhang zu V64/V65 nur als Zweckrahmen, ohne Eintragsjoin",
        },
    }
    diagram_rows: list[dict[str, object]] = []
    for page in PAGES:
        meta = diagram_meta[page]
        baseline = v55_diagrams[page]
        full_text = " ".join(f"[{row['locus']}] {row['complete_german_locus_default']}" for row in loci_by_page[page])
        diagram_rows.append(
            {
                "diagram_id": DIAGRAM[page],
                "page": page,
                "title": meta["title"],
                "locus_count": len(loci_by_page[page]),
                "group_count": sum(int(row["group_count"]) for row in loci_by_page[page]),
                "selected_formal_role": baseline["selected_formal_role"],
                "complete_german_diagram_reading": full_text,
                "apprentice_workflow": meta["workflow"],
                "rotation_direction_policy": meta["orientation"],
                "strongest_competing_value_system": meta["rival"],
                "strongest_contradiction": meta["contradiction"],
                "v64_v65_purpose_frame": meta["purpose"],
                "direct_crosspage_mapping": "NONE",
                "prose_card_import": "NONE",
                "edition_status": "COMPLETE_CREATIVE_ASTRO_SECOND_EDITION;NOT_DECRYPTION",
            }
        )
    write_tsv(OUT / "V66_R1_THREE_DIAGRAMS.tsv", diagram_rows, list(diagram_rows[0]))

    digest = hashlib.sha256("\n".join(row["astro_local_group_id"] for row in group_rows).encode()).hexdigest()
    summary = {
        "status": "BUILT",
        "pages": list(PAGES),
        "groups": len(group_rows),
        "loci": len(locus_rows),
        "diagrams": len(diagram_rows),
        "page_group_counts": dict(Counter(row["page"] for row in group_rows)),
        "page_locus_counts": dict(Counter(row["page"] for row in locus_rows)),
        "f67_derived_configurations": len(grid_rows),
        "f68_station_rows": len(station_rows),
        "f69_rule_rows": len(rule_rows),
        "orientation_alternatives": len(orientation_rows),
        "cross_page_join_rows": 0,
        "prose_card_import_rows": 0,
        "astro_local_identity_sha256": digest,
    }
    (OUT / "V66_R1_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
