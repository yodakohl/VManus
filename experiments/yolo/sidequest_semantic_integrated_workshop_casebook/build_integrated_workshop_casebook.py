#!/usr/bin/env python3
"""Build the creative ten-page WHAT/HOW/WHEN workshop casebook.

This is deliberately a sidequest edition.  It combines already selected prose
readings and diagram-instrument readings into four usable workshop scenarios;
it does not assert that the manuscript contains explicit cross-page pointers.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
ASTRO = ROOT / "experiments/yolo/sidequest_semantic_astro_instrument_readings"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: str(row.get(key, "")) for key in fields})


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


RECORD_SUMMARIES = {
    "H1": "Wurzelansatz ansetzen, einen Teil abtrennen, Wasserlauf und Sollmaß einstellen",
    "H2": "Auszugsansatz fertigstellen, Pflanzencharge weiterführen und weich einstellen",
    "H3": "Kräuteransatz auswringen, stehen lassen, nachseihen, klar abziehen und kühlen",
    "H4": "Ansatz portionieren, lagern, wieder entnehmen und länger einwirken lassen",
    "H5": "frische Zutat und Stängel weiterverarbeiten, Auszug gewinnen und anwenden",
    "B1": "Bad- oder Waschbecken füllen, dosieren, waschen, ruhen, wärmen und seihen",
    "B2": "Flüssigkeit durch lokale Stationen führen, sammeln, wärmen, klären und verteilen",
    "B3": "lange Beckenfolge mit Zuläufen, Portionen, Übertragungen und Zielstellen bedienen",
    "B4": "Tuch-, Auflage- oder Einsatzfolge anlegen, festmachen, nachwaschen und abführen",
    "B5": "kurze Fortsetzungs- und Übergaberoutine ausführen",
    "B6": "Rohposten sammeln, zum Ziel bringen, abmessen, durch Tuch führen und abschließen",
}


DOSSIERS = [
    {
        "dossier_id": "D1_ROOT_BATH_RIGHT_WHEEL",
        "title_de": "Wurzelbad unter rechter Radbedingung",
        "records": ["H1", "H2", "B1"],
        "modules": ["M67_RIGHT_SECTORS", "M67_RIGHT_RING_RULES", "M67_RIGHT_PHASES", "M67_SHARED_LEGEND"],
        "input_de": "Wurzel, Auszugsansatz, Pflanzencharge und vorgeschriebenes Maß",
        "process_de": "im gemeinsamen Bad-/Waschbecken dosieren, führen, waschen, ruhen, wärmen und seihen",
        "condition_de": "rechten Sektor, Ringregel und sichtbaren Phasenplatz am Doppelrad wählen",
        "output_de": "abgemessene, geklärte Bade- oder Waschzubereitung unter gewählter Bedingung",
        "use_de": "Werkstattfall für eine Wurzelzubereitung, die in einem gemeinsamen Becken gebraucht wird",
    },
    {
        "dossier_id": "D2_CLEAR_EXTRACT_STAR_ATLAS",
        "title_de": "Klarauszug durch Stationen mit Sternatlas-Ablesung",
        "records": ["H3", "B2"],
        "modules": ["M68_PANEL_HEADERS", "M68_STAR_STATIONS", "M68_CENTER_KEY"],
        "input_de": "Kräuter- oder Blütenansatz, Tuchweg und Standmaß",
        "process_de": "auswringen, stehen lassen, nachseihen und den Klarauszug durch lokale Stationen führen",
        "condition_de": "Paneelmodus wählen, sichtbare Sternstation adressieren und Zentrum oder Legende ablesen",
        "output_de": "gekühlter Klarauszug in einer gewählten Stations- und Himmelsklasse",
        "use_de": "Werkstattfall für eine fein geklärte Flüssigkeit mit eigener Stationsfolge",
    },
    {
        "dossier_id": "D3_STORED_APPLICATION_THREE_WHEELS",
        "title_de": "Gelagerter Ansatz, Tuchanwendung und Dreirad-Bedingung",
        "records": ["H4", "B4", "B5", "B6"],
        "modules": ["M69_LEFT_RUBRIC", "M69_LEFT_28_SLOTS", "M69_MIDDLE_QUALITY", "M69_RIGHT_LIGHT"],
        "input_de": "gelagerter Ansatz, entnommene Portion, Tuch und Zielstelle",
        "process_de": "Portion entnehmen, länger halten, auflegen oder einsetzen, festmachen, nachwaschen und abführen",
        "condition_de": "linken Platz, mittlere Qualität und rechten Lichtzustand als drei getrennte Abfragen lesen",
        "output_de": "an der Zielstelle ausgeführte Tuch- oder Flüssigkeitsanwendung unter drei gewählten Bedingungen",
        "use_de": "Werkstattfall für eine gespeicherte Zubereitung, die örtlich angewendet und anschließend gereinigt wird",
    },
    {
        "dossier_id": "D4_FRESH_PLANT_LEFT_WHEEL",
        "title_de": "Frische Pflanzenfolge im langen Beckenweg mit linker Radablesung",
        "records": ["H5", "B3"],
        "modules": ["M67_LEFT_ASPECT_FIELDS", "M67_LEFT_OUTER_STATIONS", "M67_LEFT_RING_RULE"],
        "input_de": "frische Zutat, Stängel, Folgeposten, Auszug und mehrere Zielstellen",
        "process_de": "die frische Pflanzenfolge durch den langen Becken-, Zulauf- und Übertragungsweg führen",
        "condition_de": "linkes Sternfeld, äußere Station und Ringregel für Platz, Aspekt, Ausgang und Ziel vergleichen",
        "output_de": "weitergeführter Pflanzenansatz am gewählten Ziel mit eingestelltem Vergleichswert",
        "use_de": "Werkstattfall für eine mehrstufige frische Pflanzencharge mit wiederholten Übergaben",
    },
]


MANUAL_RULES = [
    ("R01", "BILD", "Bestimme zuerst den gezeichneten Besitzer: Pflanze, Becken/Station oder Rad/Panelfläche."),
    ("R02", "DOSSIER", "Wähle genau einen Arbeitsfall; die vier Fälle sind Lehrordnungen, keine behaupteten Seitenverweise."),
    ("R03", "WHAT", "Beginne mit dem Herbal-Record: Er nennt oder übernimmt Material, Teil, Ansatz, Auszug und Maß."),
    ("R04", "OWNER", "Der Pflanzenbesitzer bleibt aktiv, bis der Record ausdrücklich einen anderen Posten einführt."),
    ("R05", "HOW", "Wechsle danach zum zugeordneten Biological-Record und lies jede Zelle als lokale Arbeitsanweisung."),
    ("R06", "STATION", "Ein gezeichneter Besitzerwechsel eröffnet eine neue Station; er beweist keinen unsichtbaren Rohrweg."),
    ("R07", "FLOW", "AR gibt die Quelle, AL das Ziel und AIR den laufenden Arbeits- oder Wasserweg an."),
    ("R08", "QUANTITY", "AIN ist eine Portion, AIIN ein Sollmaß und IIN eine einzustellende Stufe."),
    ("R09", "ACTION", "OK setzt einen Arbeitsgang an; CHED setzt oder überträgt; L-CHED führt ab; P-CHED führt ein."),
    ("R10", "GRADE", "E, EE und EEE unterscheiden kurz, länger und vollständig nur in den gelernten Reihen."),
    ("R11", "STATE", "CTH heißt bereit, SHED absetzen, CHK wärmen, CKHE seihen und SOLK sammeln."),
    ("R12", "CLOSE", "Nur die gelernte ganze Endkarte schließt eine Zelle; sichtbares dy allein genügt nicht."),
    ("R13", "HANDOFF", "Eine offene Zelle trägt Material oder Gerätezustand in die nächste Anweisung, auch über eine Zeile."),
    ("R14", "WHEN", "Zum Schluss wähle am Astro-Instrument nur den sichtbaren Sektor, Sternplatz oder Radialplatz."),
    ("R15", "NO_CYCLE", "Erfinde keinen Kreisstart, keine Drehrichtung und keine Nummerierung aus der Schriftfolge."),
    ("R16", "NO_KEY", "f67, f68 und f69 sind getrennte Werkzeuge; kein f68-f69-Schlüssel wird benötigt."),
    ("R17", "READBACK", "Lies rückwärts: Bedingung -> ausgeführter Arbeitsweg -> verwendetes Material und Sollmaß."),
    ("R18", "COPY", "Kann ein Kartenrest nicht komponiert werden, kopiere die gelernte Ganzkarte aus dem lokalen Exemplar."),
]


def main() -> None:
    phrases = read_tsv(PROSE / "CLOSED_116_PHRASES.tsv")
    events = read_tsv(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    loci = read_tsv(ASTRO / "ASTRO_142_OPERATIONAL_LOCI.tsv")
    modules = read_tsv(ASTRO / "FOURTEEN_INSTRUMENT_MODULES.tsv")
    unified = read_tsv(ASTRO / "TEN_PAGE_776_INSTRUMENT_CONTEXT.tsv")

    phrase_by_record: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in phrases:
        phrase_by_record[row["record_unit_id"]].append(row)
    event_by_id = {row["event_id"]: row for row in events}
    module_by_id = {row["module_id"]: row for row in modules}
    loci_by_module: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in loci:
        loci_by_module[row["module_id"]].append(row)

    record_to_dossier: dict[str, str] = {}
    module_to_dossier: dict[str, str] = {}
    dossier_by_id = {row["dossier_id"]: row for row in DOSSIERS}
    for dossier in DOSSIERS:
        for record in dossier["records"]:
            if record in record_to_dossier:
                raise ValueError(f"record assigned twice: {record}")
            record_to_dossier[record] = dossier["dossier_id"]
        for module in dossier["modules"]:
            if module in module_to_dossier:
                raise ValueError(f"module assigned twice: {module}")
            module_to_dossier[module] = dossier["dossier_id"]

    if set(record_to_dossier) != set(phrase_by_record):
        raise ValueError("record partition is not exhaustive")
    if set(module_to_dossier) != set(module_by_id):
        raise ValueError("module partition is not exhaustive")

    event_counts = Counter(row["record_unit_id"] for row in events)
    statement_counts = Counter(row["record_unit_id"] for row in phrases)
    dossier_rows: list[dict[str, object]] = []
    for dossier in DOSSIERS:
        records = dossier["records"]
        module_ids = dossier["modules"]
        record_pages = sorted({phrase_by_record[r][0]["page"] for r in records})
        herbal_pages = sorted({phrase_by_record[r][0]["page"] for r in records if r.startswith("H")})
        bio_pages = sorted({phrase_by_record[r][0]["page"] for r in records if r.startswith("B")})
        astro_pages = sorted({module_by_id[m]["page"] for m in module_ids})
        row = {
            **{k: v for k, v in dossier.items() if k not in {"records", "modules"}},
            "what_pages": ";".join(herbal_pages),
            "how_pages": ";".join(bio_pages),
            "when_pages": ";".join(astro_pages),
            "record_units": ";".join(records),
            "astro_modules": ";".join(module_ids),
            "prose_statement_count": sum(statement_counts[r] for r in records),
            "prose_event_count": sum(event_counts[r] for r in records),
            "astro_locus_count": sum(int(module_by_id[m]["locus_count"]) for m in module_ids),
            "astro_group_count": sum(int(module_by_id[m]["group_count"]) for m in module_ids),
            "total_group_count": sum(event_counts[r] for r in records) + sum(int(module_by_id[m]["group_count"]) for m in module_ids),
            "pairing_status": "CREATIVE_WORKSHOP_SCENARIO__NO_MANUSCRIPT_CROSS_REFERENCE_CLAIM",
        }
        dossier_rows.append(row)

    dossier_fields = [
        "dossier_id", "title_de", "what_pages", "how_pages", "when_pages", "record_units", "astro_modules",
        "prose_statement_count", "prose_event_count", "astro_locus_count", "astro_group_count", "total_group_count",
        "input_de", "process_de", "condition_de", "output_de", "use_de", "pairing_status",
    ]
    write_tsv(OUT / "FOUR_WORKSHOP_DOSSIERS.tsv", dossier_rows, dossier_fields)

    step_rows: list[dict[str, object]] = []
    for dossier in DOSSIERS:
        step_no = 0
        for phase, units in (("WHAT", [r for r in dossier["records"] if r.startswith("H")]),
                             ("HOW", [r for r in dossier["records"] if r.startswith("B")])):
            for record in units:
                step_no += 1
                full = " ".join(row["fluent_workshop_sentence_de"] for row in phrase_by_record[record])
                step_rows.append({
                    "dossier_id": dossier["dossier_id"], "step_no": step_no, "phase": phase,
                    "source_unit": record, "page": phrase_by_record[record][0]["page"],
                    "short_action_de": RECORD_SUMMARIES[record], "full_reading_de": full,
                    "statement_or_locus_count": len(phrase_by_record[record]),
                    "visible_group_count": event_counts[record],
                    "handoff_de": "Material und Arbeitsposten an die nächste Dossierphase übergeben",
                })
        for module in dossier["modules"]:
            step_no += 1
            info = module_by_id[module]
            step_rows.append({
                "dossier_id": dossier["dossier_id"], "step_no": step_no, "phase": "WHEN",
                "source_unit": module, "page": info["page"], "short_action_de": info["apprentice_instruction_de"],
                "full_reading_de": info["module_role_de"], "statement_or_locus_count": info["locus_count"],
                "visible_group_count": info["group_count"],
                "handoff_de": "Gewählten lokalen Bedingungswert zum fertigen Arbeitsfall notieren",
            })
    step_fields = ["dossier_id", "step_no", "phase", "source_unit", "page", "short_action_de", "full_reading_de",
                   "statement_or_locus_count", "visible_group_count", "handoff_de"]
    write_tsv(OUT / "WORKFLOW_STEPS.tsv", step_rows, step_fields)

    page_rows = []
    all_pages = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]
    for page in all_pages:
        dossier_ids = []
        units = []
        phase = ""
        role = ""
        for dossier in DOSSIERS:
            for record in dossier["records"]:
                if phrase_by_record[record][0]["page"] == page:
                    dossier_ids.append(dossier["dossier_id"]); units.append(record)
                    phase = "WHAT" if record.startswith("H") else "HOW"
            for module in dossier["modules"]:
                if module_by_id[module]["page"] == page:
                    dossier_ids.append(dossier["dossier_id"]); units.append(module); phase = "WHEN"
        if phase == "WHAT":
            role = "Bildbesitzer und Stoff-/Zubereitungseintrag"
        elif phase == "HOW":
            role = "lokale Becken-, Stations-, Tuch- oder Anwendungsschritte"
        else:
            role = "sichtbar adressierte Bedingungs- und Ablesemodule"
        page_rows.append({"page": page, "phase": phase, "dossiers": ";".join(dict.fromkeys(dossier_ids)),
                          "source_units": ";".join(units), "workshop_role_de": role,
                          "usage_status": "USED_IN_COMPLETE_CASEBOOK"})
    write_tsv(OUT / "TEN_PAGE_USAGE_MAP.tsv", page_rows,
              ["page", "phase", "dossiers", "source_units", "workshop_role_de", "usage_status"])

    contextual_rows: list[dict[str, object]] = []
    for row in unified:
        if row["register"] == "PROSE_WORKSHOP":
            record = row["namespace_or_record"]
            dossier_id = record_to_dossier[record]
            event = event_by_id[row["local_unit_id"]]
            phase = "WHAT" if record.startswith("H") else "HOW"
            source_unit = record
            local_statement = event["statement_id"]
            case_context = RECORD_SUMMARIES[record]
        else:
            module = row["module_id"]
            dossier_id = module_to_dossier[module]
            phase = "WHEN"
            source_unit = module
            local_statement = row["locus"]
            case_context = module_by_id[module]["module_role_de"]
        contextual_rows.append({
            **row,
            "dossier_id": dossier_id,
            "case_phase": phase,
            "case_source_unit": source_unit,
            "case_statement_or_locus": local_statement,
            "case_context_de": case_context,
            "dossier_title_de": dossier_by_id[dossier_id]["title_de"],
            "crosspage_link_status": "THEMATIC_WORKSHOP_PAIRING__NOT_AN_EXPLICIT_MANUSCRIPT_POINTER",
        })
    context_fields = list(unified[0]) + ["dossier_id", "case_phase", "case_source_unit", "case_statement_or_locus",
                                              "case_context_de", "dossier_title_de", "crosspage_link_status"]
    write_tsv(OUT / "TEN_PAGE_776_CASE_CONTEXT.tsv", contextual_rows, context_fields)

    manual_lines = ["# Meisterblatt: vier WAS–WIE–WANN-Arbeitsfälle", "",
                    "Diese Ausgabe behandelt die zehn Seiten so, als hätte eine kleine Werkstatt damit vier wiederkehrende Fälle gelehrt. Die Zusammenstellungen sind unsere konkrete Arbeitstheorie; sie behaupten keine geschriebenen Querverweise zwischen den Seiten.", ""]
    for rule_id, layer, text in MANUAL_RULES:
        manual_lines.append(f"{rule_id}. **{layer}:** {text}")
    manual_lines += ["", "## Die vier Fälle", ""]
    for d in dossier_rows:
        manual_lines += [f"### {d['dossier_id']} — {d['title_de']}", "",
                         f"- WAS: {d['input_de']}", f"- WIE: {d['process_de']}",
                         f"- WANN: {d['condition_de']}", f"- ERGEBNIS: {d['output_de']}", ""]
    (OUT / "MASTER_WORKSHOP_MANUAL.md").write_text("\n".join(manual_lines).rstrip() + "\n", encoding="utf-8")

    case_lines = ["# Vier vollständige Werkstatt-Dossiers", "",
                  "Die folgenden Lesungen sind absichtlich konkret. Jede Prosa-Aussage und jeder Astro-Ort erscheint genau einmal. Die Dossiers sind eine rekonstruierte Benutzungsordnung, keine Behauptung, dass die Seiten im Manuskript ausdrücklich aufeinander verweisen.", ""]
    for dossier in DOSSIERS:
        did = dossier["dossier_id"]
        case_lines += [f"## {did}: {dossier['title_de']}", "", f"**Ausgang:** {dossier['input_de']}.",
                       f"**Arbeitsweg:** {dossier['process_de']}.", f"**Bedingung:** {dossier['condition_de']}.",
                       f"**Fertiger Fall:** {dossier['output_de']}.", "", "### WAS und WIE — vollständige Recordlesung", ""]
        for record in dossier["records"]:
            phase = "WAS" if record.startswith("H") else "WIE"
            page = phrase_by_record[record][0]["page"]
            case_lines += [f"#### {phase}: {record} / {page} — {RECORD_SUMMARIES[record]}", ""]
            for phrase in phrase_by_record[record]:
                case_lines.append(f"- **{phrase['statement_id']}** `{phrase['surface_sequence']}` — {phrase['fluent_workshop_sentence_de']}")
            case_lines.append("")
        case_lines += ["### WANN — vollständige Instrumentablesung", ""]
        for module in dossier["modules"]:
            info = module_by_id[module]
            case_lines += [f"#### {module} / {info['page']} — {info['module_title_de']}", "",
                           f"Lehrbefehl: {info['apprentice_instruction_de']}.", ""]
            for locus in loci_by_module[module]:
                case_lines.append(f"- **{locus['locus']}** `{locus['surface_sequence']}` — {locus['imperative_reading_de']}")
            case_lines.append("")
        case_lines += ["### Rücklesung des ganzen Falls", "",
                       f"Unter der gewählten Bedingung ({dossier['condition_de']}) wird {dossier['input_de']} so verarbeitet: {dossier['process_de']}. Das Werkstattergebnis ist {dossier['output_de']}.", ""]
    (OUT / "FOUR_COMPLETE_WORKSHOP_CASES.md").write_text("\n".join(case_lines).rstrip() + "\n", encoding="utf-8")

    report = f"""# Integriertes Zehnseiten-Werkstattfallbuch

## Ergebnis

Die zehn festen Seiten ergeben in der aktuellen kreativen Lesung vier vollständige Arbeitsdossiers. Das Herbal-Bild und sein Record liefern **WAS** verwendet wird; die Biological-Seite liefert **WIE** der Posten durch Becken, Station, Tuch oder Zielstelle geführt wird; ein sichtbares Astro-Modul liefert **WANN bzw. unter welcher Bedingung** der Fall eingetragen wird.

Die Aufteilung ist vollständig und ohne Rest: 11 Prosa-Records, 116 Anweisungen, 381 Prosaereignisse, 14 Astro-Module, 142 Loci und 395 Diagrammgruppen. Zusammen sind es 776 sichtbare Gruppen. Jede erscheint genau einmal in einem Dossier.

## Die vier rekonstruierten Fälle

1. **Wurzelbad unter rechter Radbedingung:** f10r H1/H2 liefert Wurzel und Auszugsansatz; f81v B1 die gemeinsame Bade-/Waschfolge; die rechte Hälfte von f67r2 Sektor, Ringregel und Phase.
2. **Klarauszug mit Sternatlas:** f11r H3 liefert Auswringen, Standzeit, Nachseihen und Klarauszug; f82r B2 die lokale Stationsfolge; f68r1 Paneelmodus und Sternklasse.
3. **Gelagerte Tuchanwendung:** f55v H4 liefert gelagerten und wieder entnommenen Ansatz; f83r B4–B6 die Tuch-, Befestigungs-, Nachwasch- und Abschlussarbeit; f69v Platz, Qualität und Lichtzustand.
4. **Frische Pflanzenfolge:** f56r H5 liefert frische Zutat, Stängel und Folgeauszug; f83r B3 den langen Beckenweg; die linke Hälfte von f67r2 Platz–Aspekt–Ausgang–Ziel-Vergleich.

## Warum das als Werkstattbuch funktioniert

Mehrere Schreiber müssen nur drei Register lernen: erst Bildbesitzer und Material, dann lokales Arbeitsprogramm, dann sichtbare Bedingungsadresse. Die häufigen Komponenten werden komponiert; die kleinen Ganzkarten werden aus dem Exemplar kopiert. Ein Record kann über Zeilen laufen, eine geschlossene Zelle beendet nur den lokalen Schritt, und das Bild stellt ausgelassene Gegenstände bereit.

Die gleiche Apparatur kann für verschiedene Pflanzenfälle wiederverwendet werden, und dasselbe Rad kann verschiedene Arbeitsfälle konditionieren. Deshalb muss nicht jede Herbal-Seite eine eigene Biological- oder Astro-Seite physisch nennen.

## Bewusste kreative Setzung

Die vier Paarungen sind keine entdeckten Manuskriptlinks. Sie sind der bislang kohärenteste ausführbare Benutzungsentwurf für unsere zehn Seiten. Auch die Astro-Werte bleiben lokal sichtbar ausgewählte Klassen und Bedingungen; es wird kein Kreisstart, keine Drehrichtung und kein Schlüssel zwischen f68r1 und f69v erfunden.

## Zählung

- Dossiers: {len(DOSSIERS)}
- Prosa-Records: {len(record_to_dossier)}
- Prosa-Aussagen: {len(phrases)}
- Prosaereignisse: {len(events)}
- Astro-Module: {len(module_to_dossier)}
- Astro-Loci: {len(loci)}
- Astro-Gruppen: {sum(int(row['group_count']) for row in loci)}
- Einheitliche sichtbare Gruppen: {len(unified)}

Die Volltexte stehen in `FOUR_COMPLETE_WORKSHOP_CASES.md`, die Lehrregeln in `MASTER_WORKSHOP_MANUAL.md`, und `TEN_PAGE_776_CASE_CONTEXT.tsv` bindet jede sichtbare Gruppe an genau einen Fall.
"""
    (OUT / "INTEGRATED_WORKSHOP_CASEBOOK_REPORT.md").write_text(report, encoding="utf-8")

    rule_rows = [{"rule_id": rid, "layer": layer, "instruction_de": text} for rid, layer, text in MANUAL_RULES]
    write_tsv(OUT / "WORKSHOP_RULES.tsv", rule_rows, ["rule_id", "layer", "instruction_de"])

    outputs = [
        "FOUR_WORKSHOP_DOSSIERS.tsv", "WORKFLOW_STEPS.tsv", "TEN_PAGE_USAGE_MAP.tsv",
        "TEN_PAGE_776_CASE_CONTEXT.tsv", "MASTER_WORKSHOP_MANUAL.md", "FOUR_COMPLETE_WORKSHOP_CASES.md",
        "INTEGRATED_WORKSHOP_CASEBOOK_REPORT.md", "WORKSHOP_RULES.tsv",
    ]
    summary = {
        "status": "PASS",
        "dossiers": len(DOSSIERS), "records": len(record_to_dossier), "prose_statements": len(phrases),
        "prose_events": len(events), "astro_modules": len(module_to_dossier), "astro_loci": len(loci),
        "astro_groups": sum(int(row["group_count"]) for row in loci), "unified_groups": len(unified),
        "pages": sorted({row["page"] for row in unified}),
        "output_sha256": {name: sha256(OUT / name) for name in outputs},
        "interpretation_status": "CREATIVE_WORKSHOP_SCENARIO__NO_EXPLICIT_CROSSPAGE_LINK_CLAIM",
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
