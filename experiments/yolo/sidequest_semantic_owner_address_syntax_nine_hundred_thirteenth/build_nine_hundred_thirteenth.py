#!/usr/bin/env python3
"""Derive a concrete owner/address syntax for the 198 Pass-912 labels."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
P912 = ROOT / "experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth"
P909 = ROOT / "experiments/yolo/sidequest_semantic_four_page_reality_check_nine_hundred_ninth"
V75 = ROOT / "experiments/yolo/sidequest_theory_candidates_v75"

EVENTS = P912 / "PASS912_2511_EVENT_INTERLINEAR.tsv"
F70 = P909 / "F70V_TRANSFER.tsv"
F75 = P909 / "F75R_TRANSFER.tsv"
F88 = P909 / "F88R_TRANSFER.tsv"
ASTRO = V75 / "V75_SELECTED_142_LOCUS_CELESTIAL_EDITION.tsv"

EVENT_OUT = BASE / "PASS913_198_OWNER_LABEL_EVENTS.tsv"
LOCUS_OUT = BASE / "PASS913_153_OWNER_LABEL_LOCI.tsv"
CENSUS_OUT = BASE / "PASS913_COMPONENT_ROLE_CENSUS.tsv"
GRAMMAR_OUT = BASE / "PASS913_ADDRESS_GRAMMAR.tsv"
BRIDGE_OUT = BASE / "PASS913_CROSS_REGISTER_BRIDGES.tsv"
REPORT_OUT = BASE / "PASS913_REPORT.md"
SUMMARY_OUT = BASE / "PASS913_BUILD_SUMMARY.json"


LABEL_FUNCTION = {
    "OT": "NÄCHSTER PLATZ / NÄCHSTER LISTENEINTRAG",
    "OL": "GLEICHE REIHE FORTSETZEN",
    "DA": "ZWEITER ODER MARKIERTER UNTERPLATZ",
    "AL": "ZIEL- ODER ZUGEWIESENER PLATZ",
    "AR": "QUELL- ODER BEZUGSPLATZ",
    "AM_ADDR": "GEGEN- ODER INNENFELD",
    "A_ADDR": "LOKALE ADRESSE",
    "D_ADDR": "UNTER- ODER TEILADRESSE",
    "S_ADDR": "S-ADRESSE / STERNBEZUG",
    "AIIN": "SOLLZAHL ODER MASSINDEX",
    "AIN": "EINHEIT ODER EINZELPLATZ",
    "IIN": "STUFE ODER INDEX",
    "E": "KURZER / ERSTER GRAD",
    "EE": "LÄNGERER / ZWEITER GRAD",
    "EEE": "VOLLER / HÖCHSTER GRAD",
    "Y": "AKTUELL GEMEINTER BESITZER",
    "DY": "GEBUNDENER ODER ABGESCHLOSSENER EINTRAG",
    "CPH": "GEGEN- ODER EMPFANGSPLATZ",
    "K": "WERT ZUORDNEN",
    "T": "PLATZ MARKIEREN",
    "CH": "KENNUNG ABLESEN",
    "O": "LOKALEN GANG / KREISLESUNG AUFRUFEN",
    "OK": "PLATZ AKTIVIEREN",
    "S": "KLASSEN- ODER KONTEXTMARKER",
    "R": "MARKIERTER ZUSTAND",
    "OR": "LOKALER EINTRAG ODER ANSATZKLASSE",
    "G_LABEL": "LOKALES G-KLASSENZEICHEN",
    "M_LOCAL": "LOKALES M-KLASSENZEICHEN",
    "Z_ADDR": "LOKALER Z-BEZUG",
}


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


def parts(recipe: str) -> list[str]:
    return [part for part in recipe.split("+") if part and part != "CARRIER_Q"]


def astro_role(content_class: str) -> str:
    if "SECTOR" in content_class:
        return "CELESTIAL_SECTOR"
    if "OUTER_STAR" in content_class:
        return "OUTER_STAR_POSITION"
    if "STAR_RAY" in content_class or "ASTERISM" in content_class or "LOCAL_STAR" in content_class:
        return "STAR_OR_RAY_STATION"
    if "PHASE" in content_class:
        return "PHASE_OR_CONDITION_SLOT"
    if "CENTRE" in content_class or "CENTER" in content_class or "FACE_CENTRE" in content_class:
        return "CENTRE_OR_FACE_SLOT"
    if "RUBRIC" in content_class:
        return "RING_OR_PANEL_RUBRIC"
    if "HEADER" in content_class or "LEGEND" in content_class:
        return "DIAGRAM_HEADER_OR_LEGEND"
    return "CELESTIAL_LOCAL_SLOT"


def f70_role(owner: str) -> str:
    if "OUTER_FIGURE" in owner:
        return "ZODIAC_OUTER_FIGURE"
    if "INNER_FIGURE" in owner:
        return "ZODIAC_INNER_FIGURE"
    if "CENTRAL" in owner or "CENTRE" in owner:
        return "ZODIAC_CENTRE"
    return "ZODIAC_LOCAL_FIGURE_OR_BAND"


def f88_role(visible_owner: str) -> str:
    if visible_owner.startswith("oberes Zutatenfeld"):
        return "UPPER_INGREDIENT_SLOT"
    if visible_owner.startswith("mittleres Zutatenfeld"):
        return "MIDDLE_INGREDIENT_SLOT"
    if visible_owner.startswith("unteres Zutatenfeld"):
        return "LOWER_INGREDIENT_SLOT"
    return "INGREDIENT_SLOT"


def main() -> None:
    events = [row for row in read_tsv(EVENTS) if row["owner_binding_required"] == "YES"]
    if len(events) != 198:
        raise RuntimeError("expected 198 owner-bound label events")

    astro = {row["locus"]: row for row in read_tsv(ASTRO)}
    f70 = {(row["page"], row["locus"], int(row["group_index"])): row for row in read_tsv(F70) if row["locus_code"] in {"@Lz", "&Lz"}}
    f75 = {(row["locus"], int(row["token_index"])): row for row in read_tsv(F75) if row["paragraph_or_label_block"] == "LABEL"}
    f88 = {row["locus"]: row for row in read_tsv(F88) if row["kind"] == "LABEL"}

    output = []
    join_counts = Counter()
    for event in events:
        page = event["physical_page"]
        source_page = event["source_page"]
        locus = event["locus"]
        token_index = int(event["token_index"])
        namespace = ""
        role_family = ""
        role_detail = ""
        concrete_owner = event["owner_description_de"]
        owner_source = ""
        source_class = ""

        if source_page in {"f67r2", "f68r1"}:
            row = astro[locus]
            namespace = row["local_namespace"]
            role_detail = row["local_content_class"]
            role_family = astro_role(role_detail)
            concrete_owner = row["silent_argument_default"]
            owner_source = "V75_SELECTED_CELESTIAL_OWNER"
            source_class = row["source_status"]
            join_counts["ASTRO_V75"] += 1
        elif source_page in {"f70v1", "f70v2"}:
            row = f70[(source_page, locus, token_index)]
            namespace = row["owner_namespace"]
            role_detail = row["concrete_owner"]
            role_family = f70_role(role_detail)
            concrete_owner = role_detail.replace("_", " ").lower()
            owner_source = "PASS909_F70_VISIBLE_OWNER"
            source_class = row["locus_code"]
            join_counts["F70"] += 1
        elif source_page == "f75r":
            row = f75[(locus, token_index)]
            namespace = row["owner_station_id"]
            role_detail = row["visible_owner_de"]
            role_family = "LOWER_POOL_STATION_LABEL"
            concrete_owner = f"Kennung von {row['owner_station_id'].replace('_', ' ').lower()}"
            owner_source = "PASS909_F75_VISIBLE_STATION"
            source_class = row["card_pattern"]
            join_counts["F75"] += 1
        elif source_page == "f88r":
            row = f88[locus]
            namespace = row["visible_owner"].split(";")[0]
            role_detail = row["visible_owner"]
            role_family = f88_role(row["visible_owner"])
            if locus == "f88r.24":
                concrete_owner = "Kleinteil N" if token_index == 1 else "Kleinteil O"
            else:
                concrete_owner = row["creative_default_de"].replace("_", " ").title()
            owner_source = "PASS909_F88_VISIBLE_INGREDIENT"
            source_class = row["transfer_status"]
            join_counts["F88"] += 1
        elif source_page == "f81v":
            namespace = "F81_SHARED_POOL_LABEL_BLOCK"
            role_family = "SHARED_POOL_LABEL"
            role_detail = "Beschriftung am gemeinsamen Bad-/Beckenfeld"
            concrete_owner = "lokaler Wert am gemeinsamen Becken"
            owner_source = "PASS910_IMAGE_OWNER"
            source_class = "BIO_LABEL"
            join_counts["BIO_MANUAL"] += 1
        elif source_page == "f82r":
            namespace = "F82_LOCAL_STATION_LABELS"
            role_family = "BATH_OR_APPARATUS_STATION_LABEL"
            role_detail = "lokale Becken-, Gefäß- oder Leitungsstation; Richtung nicht im Bild festgelegt"
            concrete_owner = f"lokaler Stationswert {locus}"
            owner_source = "PASS910_IMAGE_OWNER"
            source_class = "BIO_LABEL"
            join_counts["BIO_MANUAL"] += 1
        elif source_page == "f83r":
            namespace = "F83_LOCAL_ASSEMBLY_LABELS"
            role_family = "CHANNEL_OR_FIGURE_ASSEMBLY_LABEL"
            role_detail = "lokale Figuren-, Becken- oder Kanalbaugruppe; keine seitenweite Verbindung"
            concrete_owner = f"lokaler Baugruppenwert {locus}"
            owner_source = "PASS910_IMAGE_OWNER"
            source_class = "BIO_LABEL"
            join_counts["BIO_MANUAL"] += 1
        else:
            raise RuntimeError(f"unhandled owner page {source_page}")

        recipe = event["component_recipe"]
        functions = [LABEL_FUNCTION.get(part, part) for part in parts(recipe)]
        output.append({
            "event_id": event["event_id"],
            "prior_local_code": event["prior_local_code"],
            "surface": event["surface"],
            "register": event["register"],
            "physical_page": page,
            "source_page": source_page,
            "locus": locus,
            "token_index": token_index,
            "namespace": namespace,
            "role_family": role_family,
            "role_detail": role_detail,
            "concrete_owner_or_name_de": concrete_owner,
            "component_recipe": recipe,
            "component_label_functions_de": " · ".join(functions),
            "combined_creative_reading_de": f"{concrete_owner}: " + "; ".join(functions),
            "owner_source": owner_source,
            "source_class": source_class,
            "interpretation_rule": "OWNER_NAME_FIRST__COMPONENTS_AS_ADDRESS_OR_CLASSIFIER",
        })

    output.sort(key=lambda row: int(str(row["event_id"]).removeprefix("P912-E")))
    fields = [
        "event_id", "prior_local_code", "surface", "register", "physical_page", "source_page", "locus",
        "token_index", "namespace", "role_family", "role_detail", "concrete_owner_or_name_de",
        "component_recipe", "component_label_functions_de", "combined_creative_reading_de",
        "owner_source", "source_class", "interpretation_rule",
    ]
    write_tsv(EVENT_OUT, output, fields)

    locus_groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in output:
        locus_groups[(str(row["source_page"]), str(row["locus"]))].append(row)
    locus_rows = []
    for number, ((source_page, locus), members) in enumerate(locus_groups.items(), start=1):
        locus_rows.append({
            "label_locus_order": number,
            "physical_page": members[0]["physical_page"],
            "source_page": source_page,
            "locus": locus,
            "register": members[0]["register"],
            "namespace": members[0]["namespace"],
            "role_family": members[0]["role_family"],
            "role_detail": members[0]["role_detail"],
            "concrete_owner_or_name_de": " | ".join(dict.fromkeys(str(row["concrete_owner_or_name_de"]) for row in members)),
            "groups": len(members),
            "surfaces": " · ".join(str(row["surface"]) for row in members),
            "recipes": " | ".join(str(row["component_recipe"]) for row in members),
            "creative_label_reading_de": " / ".join(str(row["combined_creative_reading_de"]) for row in members),
        })
    write_tsv(LOCUS_OUT, locus_rows, [
        "label_locus_order", "physical_page", "source_page", "locus", "register", "namespace", "role_family",
        "role_detail", "concrete_owner_or_name_de", "groups", "surfaces", "recipes", "creative_label_reading_de",
    ])

    component_occurrences = Counter()
    component_events: dict[str, set[str]] = defaultdict(set)
    component_roles: dict[str, Counter[str]] = defaultdict(Counter)
    component_pages: dict[str, set[str]] = defaultdict(set)
    component_registers: dict[str, set[str]] = defaultdict(set)
    for row in output:
        for component in parts(str(row["component_recipe"])):
            component_occurrences[component] += 1
            component_events[component].add(str(row["event_id"]))
            component_roles[component][str(row["role_family"])] += 1
            component_pages[component].add(str(row["physical_page"]))
            component_registers[component].add(str(row["register"]))
    census = []
    for component in sorted(component_occurrences, key=lambda item: (-len(component_events[item]), item)):
        roles = component_roles[component]
        top_role, top_count = roles.most_common(1)[0]
        total = sum(roles.values())
        entropy = -sum((count / total) * math.log2(count / total) for count in roles.values()) if total else 0.0
        census.append({
            "component": component,
            "label_function_de": LABEL_FUNCTION.get(component, "REGISTERLOKALER KLASSIFIKATOR"),
            "events": len(component_events[component]),
            "component_occurrences": component_occurrences[component],
            "registers": "|".join(sorted(component_registers[component])),
            "physical_pages": "|".join(sorted(component_pages[component])),
            "role_families": "|".join(f"{role}:{count}" for role, count in roles.most_common()),
            "largest_role_family": top_role,
            "largest_role_share": f"{top_count / total:.3f}",
            "role_entropy_bits": f"{entropy:.3f}",
            "creative_decision": "KEEP_LABEL_CLASSIFIER" if component in LABEL_FUNCTION else "KEEP_REGISTER_LOCAL",
        })
    write_tsv(CENSUS_OUT, census, [
        "component", "label_function_de", "events", "component_occurrences", "registers", "physical_pages",
        "role_families", "largest_role_family", "largest_role_share", "role_entropy_bits", "creative_decision",
    ])

    grammar = [
        {"slot_order": 1, "slot": "OWNER", "components": "VISIBLE_IMAGE_OR_LOCAL_NAMESPACE", "value_de": "konkreter Gegenstand, Figur, Sektor oder Station", "rule_de": "Immer zuerst aus Bild und Lage einsetzen; nicht aus Buchstaben erfinden."},
        {"slot_order": 2, "slot": "ORDER", "components": "OT|OL|DA", "value_de": "nächster Platz | gleiche Reihe | markierter Unterplatz", "rule_de": "Ordnet einen Listeneintrag relativ zum vorigen."},
        {"slot_order": 3, "slot": "CLASS_OR_ACTION", "components": "O|OK|CH|K|T|S|OR", "value_de": "Gang/Klasse aufrufen | aktivieren | ablesen | zuordnen | markieren | Klasse | lokaler Eintrag", "rule_de": "Im Etikett bevorzugt Klassifikator; in Prosa bevorzugt Handlung."},
        {"slot_order": 4, "slot": "ADDRESS", "components": "AL|AR|AM_ADDR|A_ADDR|D_ADDR|S_ADDR", "value_de": "Ziel | Bezug/Quelle | Innen/Gegen | lokale | Teil | S-Adresse", "rule_de": "Bestimmt die räumliche oder tabellarische Stelle."},
        {"slot_order": 5, "slot": "INDEX_OR_AMOUNT", "components": "AIIN|AIN|IIN", "value_de": "Sollzahl/Maß | Einheit | Stufe/Index", "rule_de": "Im Diagramm Zahl-/Indexwert; im Zutatenfeld Menge oder Einheit."},
        {"slot_order": 6, "slot": "GRADE", "components": "E|EE|EEE", "value_de": "kurz/erste | länger/zweite | voll/höchste Stufe", "rule_de": "Staffelt den Eintrag, ohne selbst den Gegenstand zu benennen."},
        {"slot_order": 7, "slot": "TOPOLOGY", "components": "L|CKH|AIR|CPH", "value_de": "Verbindung | Durchlass | Lauf | Gegen-/Empfangsplatz", "rule_de": "Beschreibt Lagebeziehung oder Bahn, nicht automatisch Wasser."},
        {"slot_order": 8, "slot": "REFERENT_OR_BOUNDARY", "components": "Y|DY", "value_de": "aktueller Besitzer | gebundener/abgeschlossener Eintrag", "rule_de": "Y hält den Bildbesitzer aktuell; DY bindet nur in lizenzierter Form."},
    ]
    write_tsv(GRAMMAR_OUT, grammar, ["slot_order", "slot", "components", "value_de", "rule_de"])

    bridges = [
        ("OT_AL", lambda p: "OT" in p and "AL" in p, "NÄCHSTER ZIEL-/LISTENPLATZ", "verbindet Sternfiguren und Zutatenplätze"),
        ("OT_AR", lambda p: "OT" in p and "AR" in p, "NÄCHSTER BEZUGSPLATZ", "verbindet Ring- und Figurenadressen"),
        ("AM", lambda p: "AM_ADDR" in p, "GEGEN-/INNENFELD", "tritt in Himmels- und Zutatenfeldern auf"),
        ("AL_Y", lambda p: "AL" in p and "Y" in p, "ZIELPLATZ DES AKTUELLEN BESITZERS", "bindet Figur, Station oder Zutat an einen Platz"),
        ("S_AL", lambda p: "S" in p and "AL" in p, "KLASSENMARKIERTER ZIELPLATZ", "f75-Beckenlabel und f70-Figurenlabel teilen das Muster"),
        ("OK_AL", lambda p: "OK" in p and "AL" in p, "AKTIVIERTER/ZUGEWIESENER PLATZ", "Beckenstation und Himmelsfeld teilen die Adressform"),
        ("Y_K", lambda p: "Y" in p and "K" in p, "AKTUELLEN BESITZER ZUORDNEN", "häufige sektor- und figurenbezogene Zuordnungsform"),
        ("CPH", lambda p: "CPH" in p, "GEGEN-/EMPFANGSPLATZ", "Himmelslabel und Arbeitskarten teilen dieselbe Topologie"),
    ]
    bridge_rows = []
    for name, predicate, value, explanation in bridges:
        members = [row for row in output if predicate(parts(str(row["component_recipe"])))]
        bridge_rows.append({
            "bridge": name,
            "creative_value_de": value,
            "events": len(members),
            "registers": "|".join(sorted({str(row["register"]) for row in members})),
            "physical_pages": "|".join(sorted({str(row["physical_page"]) for row in members})),
            "role_families": "|".join(f"{role}:{count}" for role, count in Counter(str(row["role_family"]) for row in members).most_common()),
            "surfaces": "|".join(sorted({str(row["surface"]) for row in members})),
            "why_useful_de": explanation,
        })
    write_tsv(BRIDGE_OUT, bridge_rows, [
        "bridge", "creative_value_de", "events", "registers", "physical_pages", "role_families", "surfaces", "why_useful_de",
    ])

    role_counts = Counter(str(row["role_family"]) for row in output)
    report = [
        "# Pass 913 — Besitzer- und Adresssyntax der Bildetiketten", "",
        "## Ergebnis", "",
        "Die 198 Etikettengruppen in 153 Bildloci sind jetzt an konkrete räumliche Rollen",
        "gebunden: Himmelssektor, Sternstation, Außen-/Innenfigur, Beckenstation, Baugruppe",
        "oder Zutatenplatz. Der sichtbare Name/Klassenwert bleibt zuerst; die wiederkehrenden",
        "Teile bilden darüber eine kleine Adresssyntax.", "",
        "Der wichtigste Fortschritt ist die Doppelverwendung von `OT–AL`: Auf f70 adressiert",
        "sie nacheinander Sternfiguren, auf f88 Zutatenplätze. Das passt besser zu „nächster",
        "zugewiesener Platz“ als zu einem Pflanzenteil oder einem Badeverb. Ebenso werden",
        "`AR`, `AM`, `Y` und `DY` als Bezug, Innenfeld, aktueller Besitzer und gebundener Eintrag",
        "konkreter, ohne die Bildnamen zu erfinden.", "",
        "## Acht lesbare Slots", "",
    ]
    for row in grammar:
        report.append(f"{row['slot_order']}. **{row['slot']}** — `{row['components']}`: {row['value_de']}.")
    report += ["", "## Rollenbilanz", ""]
    for role, count in role_counts.most_common():
        report.append(f"- `{role}`: {count} Gruppen")
    report += [
        "", "## Konkrete Lesebeispiele", "",
        "- f70 `OT–AL–Y`: nächster Zielplatz der aktuell bezeichneten Sternfigur.",
        "- f88 `OT–AL–DY`: nächster gebundener Zutatenplatz; sichtbarer Wert Wurzelbündel G.",
        "- f75 `S–AL`: klassenmarkierte Zielstelle am unteren Beckenlabel.",
        "- f67 `OK–AR`: den bezeichneten Bezugsplatz im Rad aktivieren.",
        "- f68 `CPH–O–CTH–Y`: Gegenstelle des lokalen Ringgangs, mit Status des aktuellen Sternplatzes.",
        "", "## Was bewusst lokal bleibt", "",
        "Die Etiketten nennen weiterhin keine identifizierte Pflanze, Zutat, Sternfigur oder",
        "historische Himmelsstation. Pass 913 liefert eine brauchbare Klassen-/Adresslesung",
        "über dem sichtbaren Besitzer; der eigentliche Eigenname bleibt Werkstattwissen.", "",
        "## Nächster Hebel", "",
        "Pass 914 soll diese acht Slots in das vollständige Handbuch zurückschreiben und die",
        "f70-/f88-Etiketten als fortlaufende Listen lesen. Danach wird geprüft, welche der",
        "vier Registeroperationen O/OK/CH/K im Namensregister wirklich Klassifikatoren sind.",
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "pass": 913,
        "decision": "OWNER_FIRST_LABELS_WITH_EIGHT_SLOT_ADDRESS_SYNTAX",
        "label_events": len(output),
        "label_loci": len(locus_rows),
        "role_families": dict(sorted(role_counts.items())),
        "join_counts": dict(sorted(join_counts.items())),
        "components_in_labels": len(census),
        "address_slots": len(grammar),
        "cross_register_bridges": len(bridge_rows),
        "source_hashes": {path.name: sha(path) for path in (EVENTS, F70, F75, F88, ASTRO)},
        "output_hashes": {path.name: sha(path) for path in (EVENT_OUT, LOCUS_OUT, CENSUS_OUT, GRAMMAR_OUT, BRIDGE_OUT, REPORT_OUT)},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
