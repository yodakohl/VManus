#!/usr/bin/env python3
"""Order the Pass-910 local drawer and replace avoidable whole-card readings.

This remains a creative workshop-sidequest artifact.  It does not claim a
decipherment.  It asks a practical question: which entries really need to be
copied whole, and which can a 1420s apprentice generate from the current small
card grammar?
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
P910 = ROOT / "experiments/yolo/sidequest_semantic_three_layer_master_handbook_nine_hundred_tenth"

NOMENCLATOR = P910 / "PASS910_LOCAL_NOMENCLATOR.tsv"
EVENTS = P910 / "PASS910_2511_EVENT_INTERLINEAR.tsv"
DICTIONARY = P910 / "PASS910_CARD_DICTIONARY.tsv"

ORDERED_OUT = BASE / "PASS911_ORDERED_LOCAL_DRAWER.tsv"
WORKSHOP_OUT = BASE / "PASS911_REVISED_WORKSHOP_CARDS.tsv"
FAMILY_OUT = BASE / "PASS911_RECURRENT_FAMILIES.tsv"
CPH_OUT = BASE / "PASS911_CPH_FAMILY.tsv"
REPORT_OUT = BASE / "PASS911_REPORT.md"
SUMMARY_OUT = BASE / "PASS911_BUILD_SUMMARY.json"


# Every Pass-910 copied workshop card is reconsidered explicitly.  The mapping
# uses only already active components plus one new register root, CPH.
WORKSHOP_RECIPES = {
    "B-W001": "CH+E+CPH+E+DY",
    "B-W002": "CPH+AL",
    "B-W003": "CPH+E+DY",
    "B-W004": "DA+IIN+DY",
    "B-W005": "D_ADDR+E+DY",
    "B-W006": "K+AM_ADDR",
    "B-W007": "K+E+DY",
    "B-W008": "K+E+S_ADDR+D_ADDR",
    "B-W009": "L+CH+CPH+E+DY",
    "B-W010": "L+K+E+D_ADDR+E+Y",
    "B-W011": "L+K+Y",
    "B-W012": "O+P+E+DY",
    "B-W013": "CARRIER_Q+E+DY",
    "B-W014": "CARRIER_Q+O+DY",
    "B-W015": "CARRIER_Q+O+E+S+E+DY",
    "B-W016": "CARRIER_Q+O+P",
    "B-W017": "CARRIER_Q+O+P+Y",
    "B-W018": "R+A_ADDR+G_LABEL",
    "B-W019": "R+A_ADDR+S+Y",
    "B-W020": "S+AIIN",
    "B-W021": "S+AM_ADDR",
    "B-W022": "SH+O+CPH+E+DY",
    "B-W023": "Y+DY",
    "B-W024": "Y+K+E+DY",
    "B-W025": "Y+T+E+DY",
    "H-W001": "D_ADDR+K+Y",
    "H-W002": "D_ADDR+O+D_ADDR",
    "H-W003": "D_ADDR+O+DY+D_LABEL",
    "H-W004": "D_ADDR+O+IIN+R",
    "H-W005": "E+S+E+DY",
    "H-W006": "K+O+M_LOCAL",
    "H-W007": "O+D_ADDR+L",
    "H-W008": "Y+CH+O+CPH+Y",
    "H-W009": "Y+K+A_ADDR+K+Y",
    "H-W010": "Y+T+Y",
    "P-W001": "CPH+OL",
    "P-W002": "K+O+A_ADDR+Y",
    "P-W003": "S+AM_ADDR",
    "Z-W001": "S+AIIN+R",
    "Z-W002": "Y+K+E+Y+DY",
    "Z-W003": "Y+T+O+DY",
    "Z-W004": "AM_ADDR+Y",
    "Z-W005": "CPH+OL",
    "Z-W006": "O+LOCAL_CHAR_F+Y+DY",
    "Z-W007": "O+G_LABEL",
    "Z-W008": "CARRIER_Q+K+O+Y",
    "Z-W009": "CARRIER_Q+S+G_LABEL",
    "Z-W010": "S+OR+AIIN+R",
    "Z-W011": "Y+K+Y",
    "Z-W012": "Y+T+E+O+DY",
    "Z-W013": "Y+T+O",
    "Z-W014": "Y+T+O+DY",
    "Z-W015": "D_ADDR+O+IIN+R",
    "Z-W016": "E+Y+K+E+O+DY",
    "Z-W017": "O+Y+G_LABEL+Y",
    "Z-W018": "T+E+Y",
    "Z-W019": "Y+T+O",
}


LABEL_REPAIRS = {
    "Z-L017": "CPH+EE+Y",
    "Z-L018": "CPH+O+CTH+Y",
    "Z-L029": "G_LABEL",
    "Z-L035": "O+CPH+Y",
    "Z-L116": "S+Y+K+O+S_ADDR",
}


SHORT = {
    "AIIN": "SOLL-MASS",
    "AIN": "PORTION",
    "AIR": "LAUF",
    "AL": "ZIELSTELLE",
    "AR": "QUELLSTELLE",
    "CKH": "DURCHLASS",
    "CPH": "GEGEN-/EMPFANGSGANG",
    "DY": "SCHLUSS",
    "E": "KURZ",
    "EE": "LANG",
    "EEE": "VOLL",
    "IIN": "STUFE",
    "L": "LEITEN",
    "OL": "FORTSETZEN",
    "OT": "DANACH",
    "Y": "DIESER POSTEN",
    "O": "GANG",
    "OK": "ANSETZEN",
    "CH": "ENTNEHMEN/ABLESEN",
    "CHD": "UMSETZEN",
    "CHK": "ZUSTAND BEHANDELN",
    "CTH": "STATUS",
    "K": "ZUORDNEN/ZUGEBEN",
    "P": "BEGINNEN/EINSETZEN",
    "R": "MARKIERTER ZUSTAND",
    "S": "KONTEXT/PROBE",
    "SH": "HALTEN",
    "SHED": "RUHESTUFE",
    "T": "BEARBEITEN/MARKIEREN",
    "OR": "ANSATZ/EINTRAG",
    "DA": "ZWEITE STUFE",
    "A_ADDR": "LOKALE ADRESSE",
    "AM_ADDR": "GEGEN-/INNENFELD",
    "D_ADDR": "TEILADRESSE",
    "S_ADDR": "S-ADRESSE",
    "D_LABEL": "D-KENNZEICHEN",
    "G_LABEL": "G-KENNZEICHEN",
    "M_LOCAL": "M-KENNZEICHEN",
    "Z_ADDR": "Z-BEZUG",
    "CARRIER_Q": "Q-TRAEGER",
    "AN": "ZUSATZ",
    "OS": "AUCH",
    "RESUME_CARD": "WIEDERAUFNAHME",
    "CFH": "TRENNEN/PRESSEN",
    "CHEO": "REGISTER-EINTRAG",
    "HO": "OBJEKTTEIL",
    "LD": "BEFESTIGEN",
    "LSH": "WASCHEN/SPUELEN",
    "SOLK": "SAMMELSTELLE",
    "S_LABEL": "S-KENNZEICHEN",
}


CPH_REGISTER = {
    "HERBAL": "NACHLAUF ODER ZWEITER DURCHGANG",
    "BIOLOGICAL": "RUECKLAUF ZUR EMPFANGSSTATION",
    "ZODIAC": "GEGEN- ODER RUECKSTELLE IM RAD",
    "PHARMA": "AUSZUG AUFFANGEN ODER NACHFUEHREN",
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
    return [part for part in recipe.split("+") if part]


def atomic_reading(recipe: str) -> str:
    values = []
    for component in parts(recipe):
        if component == "CARRIER_Q":
            continue
        if component.startswith("LOCAL_CHAR_"):
            values.append(component.removeprefix("LOCAL_CHAR_") + "-KENNZEICHEN")
        else:
            values.append(SHORT.get(component, component))
    return " · ".join(values)


def context_for(event: dict[str, str], locus_events: dict[str, list[dict[str, str]]]) -> str:
    sequence = locus_events[event["locus"]]
    index = sequence.index(event)
    left = sequence[index - 1]["surface"] if index else "<START>"
    right = sequence[index + 1]["surface"] if index + 1 < len(sequence) else "<END>"
    return f"{left} > [{event['surface']}] > {right}"


def family_rows(all_events: list[dict[str, str]], revised_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_code = {str(row["local_code"]): row for row in revised_rows}
    definitions = [
        ("CPH", "CPH", "GEGEN-/EMPFANGSGANG", "new_root", "Empfang oder Gegenlauf bleibt erkennbar, der Sachwert wechselt mit dem Register."),
        ("E_DY", "+E+DY", "KURZER GRAD + SCHLUSS", "existing_components", "Keine eigene KEDY- oder EDY-Wurzel; K, T, O, CPH usw. besetzen denselben Rahmen."),
        ("Y_K_T", "Y+K|Y+T", "AKTUELLER POSTEN + ZUORDNEN/MARKIEREN", "existing_components", "Y rahmt einen laufenden Posten; K oder T liefert die Operation."),
        ("AM", "AM_ADDR", "GEGEN-/INNENFELD", "existing_address", "SAM, KAM und AMY sind Adresskompositionen, keine drei Ganzwörter."),
        ("AIIR", "IIN+R|AIIN+R", "MARKIERTE STUFE/MASSZAHL", "scribal_contraction", "Vor R kann das Schluss-n ausfallen; kein neues Sachwort wird benötigt."),
        ("G", "G_LABEL", "LOKALES G-KENNZEICHEN", "local_sign", "G trägt lokale Identität, aber keinen portablen Gegenstandswert."),
        ("D_ECHO", "D_ADDR|D_LABEL", "TEILADRESSE ODER KOPIERECHO", "existing_address", "DOD und DODYD bleiben aus Gang plus Teiladresse/Kennzeichen lesbar."),
    ]
    result = []
    for family, needle, value, kind, rule in definitions:
        members = []
        if family == "CPH":
            matched_events = [row for row in all_events if "cph" in row["surface"]]
            member_codes = sorted({row["local_code"] for row in matched_events if row["local_code"]})
        else:
            member_codes = []
            for code, row in by_code.items():
                recipe = str(row["revised_recipe"])
                match = any(item in recipe for item in needle.split("|"))
                if match:
                    member_codes.append(code)
            matched_events = [row for row in all_events if row["local_code"] in member_codes]
        members = sorted({row["surface"] for row in matched_events})
        result.append({
            "family": family,
            "mechanism": kind,
            "short_value_de": value,
            "surfaces": "|".join(members),
            "local_codes": "|".join(member_codes),
            "events": len(matched_events),
            "registers": "|".join(sorted({row["register"] for row in matched_events})),
            "physical_pages": "|".join(sorted({row["physical_page"] for row in matched_events})),
            "apprentice_rule_de": rule,
        })
    return result


def main() -> None:
    nomenclator = read_tsv(NOMENCLATOR)
    events = read_tsv(EVENTS)
    dictionary = read_tsv(DICTIONARY)
    if len(nomenclator) != 240 or sum(int(row["events"]) for row in nomenclator) != 261:
        raise RuntimeError("unexpected Pass-910 drawer inventory")

    workshop_codes = {row["local_code"] for row in nomenclator if row["drawer"] == "COPIED_WORKSHOP_CARD"}
    if workshop_codes != set(WORKSHOP_RECIPES):
        raise RuntimeError(f"workshop mapping mismatch: {workshop_codes ^ set(WORKSHOP_RECIPES)}")

    events_by_code: dict[str, list[dict[str, str]]] = defaultdict(list)
    locus_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        locus_events[event["locus"]].append(event)
        if event["local_code"]:
            events_by_code[event["local_code"]].append(event)

    same_surface_codes: dict[str, set[str]] = defaultdict(set)
    for row in nomenclator:
        same_surface_codes[row["surface"]].add(row["local_code"])

    ordered = []
    workshop = []
    for row in nomenclator:
        code = row["local_code"]
        event_rows = events_by_code[code]
        if len(event_rows) != int(row["events"]):
            raise RuntimeError(f"event mismatch for {code}")
        if row["drawer"] == "COPIED_WORKSHOP_CARD":
            recipe = WORKSHOP_RECIPES[code]
            if "CPH" in parts(recipe):
                order_class = "1_CPH_REUSABLE_FAMILY"
                mechanism = "NEW_REGISTER_ROOT_CPH"
            elif int(row["events"]) > 1:
                order_class = "2_RECURRENT_COMPOSED_WORKSHOP_CARD"
                mechanism = "EXISTING_COMPONENT_RECIPE"
            else:
                order_class = "3_REPAIRED_COMPOSED_WORKSHOP_CARD"
                mechanism = "EXISTING_COMPONENT_RECIPE"
            decision = "REMOVE_FROM_WHOLE_CARD_DRAWER"
        else:
            recipe = LABEL_REPAIRS.get(code, row["form_recipe_if_any"])
            if recipe.startswith("WHOLE["):
                raise RuntimeError(f"unrepaired whole label {code}")
            has_local_sign = any(
                component.startswith("LOCAL_CHAR_") or component in {"G_LABEL", "M_LOCAL", "Z_ADDR"}
                for component in parts(recipe)
            )
            if int(row["events"]) > 1:
                order_class = "4_RECURRENT_OWNER_BOUND_LABEL"
            elif has_local_sign:
                order_class = "5_COMPOSED_LABEL_WITH_LOCAL_SIGN"
            else:
                order_class = "6_COMPOSED_OWNER_BOUND_LABEL"
            mechanism = "OWNER_BOUND_COMPOUND_LABEL__CLASSIFIER_HYPOTHESIS"
            decision = "KEEP_OWNER_BOUND_NOMENCLATOR__FORM_SEGMENTED_ONLY"

        atomic = atomic_reading(recipe)
        if "CPH" in parts(recipe):
            register_value = CPH_REGISTER[row["register"]]
        elif row["drawer"] == "PICTURED_NAME_OR_CLASS":
            register_value = row["visible_owner_or_default_de"]
        else:
            register_value = atomic
        contexts = " || ".join(context_for(event, locus_events) for event in event_rows)
        surface_codes = sorted(same_surface_codes[row["surface"]] - {code})
        output = {
            "rank_class": order_class,
            "local_code": code,
            "surface": row["surface"],
            "register": row["register"],
            "old_drawer": row["drawer"],
            "events": row["events"],
            "loci": row["loci"],
            "physical_pages": "|".join(sorted({event["physical_page"] for event in event_rows})),
            "visible_owner_or_default_de": row["visible_owner_or_default_de"],
            "old_recipe": row["form_recipe_if_any"],
            "revised_recipe": recipe,
            "atomic_reading_de": atomic,
            "register_short_reading_de": register_value,
            "mechanism": mechanism,
            "decision": decision,
            "same_surface_other_codes": "|".join(surface_codes) or "NONE",
            "local_contexts": contexts,
            "apprentice_rule_de": (
                "Lies zuerst den sichtbaren Besitzer; behandle die Komponenten nur als mögliche Klassen-/Adressform, nicht als übersetzten Namen."
                if row["drawer"] == "PICTURED_NAME_OR_CLASS"
                else "Baue die Karte aus dem kurzen Werkstattrezept; kopiere sie nicht mehr als Ganzwort."
            ),
        }
        ordered.append(output)
        if row["drawer"] == "COPIED_WORKSHOP_CARD":
            workshop.append(output)

    ordered.sort(key=lambda row: (str(row["rank_class"]), -int(row["events"]), str(row["register"]), str(row["surface"]), str(row["local_code"])))
    workshop.sort(key=lambda row: (str(row["rank_class"]), -int(row["events"]), str(row["register"]), str(row["surface"])))
    fields = [
        "rank_class", "local_code", "surface", "register", "old_drawer", "events", "loci",
        "physical_pages", "visible_owner_or_default_de", "old_recipe", "revised_recipe",
        "atomic_reading_de", "register_short_reading_de", "mechanism", "decision",
        "same_surface_other_codes", "local_contexts", "apprentice_rule_de",
    ]
    write_tsv(ORDERED_OUT, ordered, fields)
    write_tsv(WORKSHOP_OUT, workshop, fields)

    families = family_rows(events, ordered)
    write_tsv(FAMILY_OUT, families, [
        "family", "mechanism", "short_value_de", "surfaces", "local_codes", "events",
        "registers", "physical_pages", "apprentice_rule_de",
    ])

    cph_events = [row for row in events if "cph" in row["surface"]]
    cph_rows = []
    for event in cph_events:
        cph_rows.append({
            "event_id": event["event_id"],
            "surface": event["surface"],
            "register": event["register"],
            "physical_page": event["physical_page"],
            "locus": event["locus"],
            "usage_class": event["usage_class"],
            "visible_owner_de": event["visible_owner_de"],
            "old_recipe": event["component_recipe"],
            "old_mode": event["meaning_mode"],
            "cph_value_de": CPH_REGISTER[event["register"]],
            "local_context": context_for(event, locus_events),
        })
    write_tsv(CPH_OUT, cph_rows, [
        "event_id", "surface", "register", "physical_page", "locus", "usage_class",
        "visible_owner_de", "old_recipe", "old_mode", "cph_value_de", "local_context",
    ])

    rank_counts = Counter(str(row["rank_class"]) for row in ordered)
    report = [
        "# Pass 911 — Ordnung des lokalen Kartenfachs",
        "",
        "## Ergebnis",
        "",
        "Die 240 Pass-910-Schubladeneinträge sind jetzt nach Funktion statt nach bloßer",
        "Unbekanntheit geordnet. Die 57 kopierten Arbeitskarten lassen sich vollständig",
        "als kurze Kompositionen lesen. 49 brauchen nur bereits vorhandene Komponenten;",
        "acht weitere Karten gehören zu derselben wiederkehrenden Familie und erhalten",
        "gemeinsam den neuen Fachkern `CPH`.",
        "",
        "Die 183 Bildetiketten bleiben Besitzer-gebundene Namen oder Klassen. Ihre sichtbare",
        "Form lässt sich zwar in Adress-, Grad- und Bezugsteile zerlegen; das übersetzt den",
        "konkreten Namen aber nicht. Besonders bei den f88r-Zutaten gilt: Bildreferent zuerst,",
        "Komponenten nur als mögliche Klassifikatoren. Nur auf der Formebene bleibt keine",
        "unsegmentierte Ganzkarte übrig.",
        "",
        "## Der neue kurze Kern",
        "",
        "`CPH = GEGEN-/EMPFANGSGANG`. Seine zwölf sichtbaren Verwendungen verteilen sich",
        "über alle vier Register. Im Pflanzen-/Zutatenregister ergibt er Nachlauf oder",
        "zweiten Durchgang, im Beckenregister Rücklauf zur Empfangsstation und im Himmelsrad",
        "eine Gegen- oder Rückstelle. Das gemeinsame Minimum ist topologisch, nicht stofflich.",
        "",
        "## Was keine neue Wurzel ist",
        "",
        "- `KEDY`, `TEDY`, `OPEDY` und verwandte Formen sind Kern + `E` + `DY`.",
        "- `YKY`, `YTEDY`, `YTO(DY)` sind laufender Bezug + Operation + optionaler Schluss.",
        "- `SAM`, `KAM`, `AMY` verwenden das bestehende Gegen-/Innenfeld `AM`.",
        "- `DOIIR`, `SAIIR`, `SORAIIR` verwenden `IIN/AIIN + R` mit Ausfall des Schluss-n.",
        "- `G` bleibt ein lokales Kennzeichen und wird nicht zu einem Sachwort gemacht.",
        "",
        "## Geordnete Klassen",
        "",
    ]
    for key in sorted(rank_counts):
        report.append(f"- `{key}`: {rank_counts[key]} Einträge")
    report += [
        "",
        "## Konkrete neue Lesungen",
        "",
        "- `cphedy`: Empfangs-/Rückgang kurz ausführen; schließen.",
        "- `cphal`: an die Empfangsstelle führen.",
        "- `ychocphy`: den laufenden Pflanzenposten in den Nachlauf geben.",
        "- `cphol`: den Empfangs-/Gegengang fortsetzen.",
        "- `ytedy`: diesen Posten kurz bearbeiten/markieren; schließen.",
        "- `qoesedy`: den Gang kurz prüfen, nochmals kurz halten; schließen.",
        "- `soraiir`: den lokalen Eintrag auf der markierten Maß-/Indexstufe lesen.",
        "",
        "## Nächste Runde",
        "",
        "Pass 912 setzt diese Ordnung in das vollständige 2511-Ereignis-Wörterbuch ein.",
        "Dabei werden `cphy` und alle übrigen `CPH`-Formen gemeinsam korrigiert, die 57",
        "Ganzkarten aus dem Nomenklator entfernt und die Besitzeretiketten als komponierte",
        "Adress-/Wertformeln ausgegeben.",
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    summary = {
        "pass": 911,
        "decision": "LOCAL_DRAWER_ORDERED__CPH_PROMOTED__NO_OPAQUE_WORKSHOP_CARD",
        "source_drawer_entries": len(nomenclator),
        "source_drawer_events": sum(int(row["events"]) for row in nomenclator),
        "source_workshop_cards": len(workshop),
        "source_owner_labels": len(nomenclator) - len(workshop),
        "revised_whole_cards": sum(1 for row in ordered if str(row["revised_recipe"]).startswith("WHOLE[")),
        "new_register_roots": ["CPH"],
        "cph_events": len(cph_events),
        "cph_surfaces": len({row["surface"] for row in cph_events}),
        "rank_counts": dict(sorted(rank_counts.items())),
        "source_hashes": {path.name: sha(path) for path in (NOMENCLATOR, EVENTS, DICTIONARY)},
        "output_hashes": {path.name: sha(path) for path in (ORDERED_OUT, WORKSHOP_OUT, FAMILY_OUT, CPH_OUT, REPORT_OUT)},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
