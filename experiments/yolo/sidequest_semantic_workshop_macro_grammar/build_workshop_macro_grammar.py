#!/usr/bin/env python3
"""Build a creative cross-dossier macro grammar and four master source texts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
CASEBOOK = ROOT / "experiments/yolo/sidequest_semantic_integrated_workshop_casebook"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: str(row.get(key, "")) for key in fields})


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


MACROS = [
    ("M00", "BEDINGUNG_NACHSCHLAGEN", "Unter welcher sichtbaren Bedingung wird gearbeitet?", "Astro-Modul wählen; keine Kreisrichtung erfinden", "WHEN"),
    ("M01", "MATERIAL_WAEHLEN", "Welcher Stoff oder Teil ist gemeint?", "Bildbesitzer, Zutat, Wurzel, Stängel oder Teilposten aktivieren", "WHAT"),
    ("M02", "POSTEN_FORTFUEHREN", "Welcher laufende, vorige oder nächste Posten gilt?", "Y/OL/OT und gelernte Bezugskarten führen den aktiven Posten", "WHAT_OR_HOW"),
    ("M03", "ANSATZ_PRODUKT", "Welcher Ansatz, Auszug oder Lauf wird bearbeitet?", "OR/CHEO/AIR und gelernte Produktkarten setzen den Arbeitsbestand", "WHAT"),
    ("M04", "MENGE_STUFE", "Wie viel und bis zu welcher Stufe?", "AIN=Portion, AIIN=Sollmaß, IIN=Sollstufe, TY=Teil", "WHAT_OR_HOW"),
    ("M05", "QUELLE_ZIEL_WERKZEUG", "Woher, wohin und in oder durch welches Werkzeug?", "AR=aus/von, AL=an/zu; Gefäß und Tuch können Ganzkarten sein", "HOW"),
    ("M06", "FUEHREN_UEBERTRAGEN", "Wie bewegt sich der Posten?", "CHED umsetzen, L-CHED abführen, P-CHED einführen, CKH durchleiten", "HOW"),
    ("M07", "ARBEITSGANG_AUSFUEHREN", "Was wird mit dem Posten getan?", "ansetzen, waschen, wärmen, seihen, absetzen, kühlen, teilen oder befestigen", "HOW"),
    ("M08", "ZUSTAND_PRUEFEN", "Welcher sicht- oder fühlbare Zustand gilt?", "bereit, roh, klar, warm, kurz/länger/vollständig", "HOW"),
    ("M09", "SCHRITT_SCHLIESSEN_ODER_UEBERGEBEN", "Ist die lokale Zelle fertig oder trägt sie etwas weiter?", "gelernte Endkarte schließt; sonst Material oder Gerätezustand weitergeben", "HOW"),
]

MACRO_INFO = {row[0]: row for row in MACROS}


MASTER_PARAGRAPHS = {
    "D1_ROOT_BATH_RIGHT_WHEEL": (
        "Wähle am rechten Doppelrad den sichtbaren Sektor, lies die Ringregel und setze die passende Phase. "
        "Nimm dann die Wurzel, bereite daraus den Ansatz, trenne den benötigten Teil ab und stelle Auszug und Pflanzencharge auf Sollmaß und Weichstufe. "
        "Fülle das gemeinsame Becken, gib Portion und Zusatz zu, führe den Posten durch die bezeichnete Stelle, wasche, lasse absetzen, wärme kurz und seihe. "
        "Bewahre den geklärten Bad- oder Waschansatz unter der gewählten Bedingung bereit."
    ),
    "D2_CLEAR_EXTRACT_STAR_ATLAS": (
        "Wähle am Sternatlas zuerst den Paneelmodus, dann die sichtbare Sternstation und lies Zentrum oder Legende als Grundwert. "
        "Nimm den Kräuter- oder Blütenansatz, wringe ihn aus, lasse ihn bis zum Standmaß stehen, seihe erneut, ziehe den Klarauszug ab und kühle ihn. "
        "Führe die Flüssigkeit durch die örtlichen Stationen, sammle sie, wärme sie nach Bedarf, teile sie und bringe die vorgeschriebene Portion an den Zielposten. "
        "Der fertige Klarauszug bleibt mit seiner Sternklasse und Stationsadresse eingetragen."
    ),
    "D3_STORED_APPLICATION_THREE_WHEELS": (
        "Schlage am linken Rad den Platz, am mittleren Rad die Qualität und am rechten Rad den Lichtzustand getrennt nach. "
        "Nimm vom gelagerten Ansatz die vorgeschriebene Portion, halte oder wärme sie länger und führe sie zur bezeichneten Stelle. "
        "Lege oder setze den Posten mit dem Tuch an, befestige ihn, lasse ihn einwirken, wasche danach und führe den Rest ab. "
        "Trage Anwendung, Zielstelle und die drei gewählten Bedingungen als abgeschlossenen Arbeitsfall ein."
    ),
    "D4_FRESH_PLANT_LEFT_WHEEL": (
        "Wähle am linken Doppelrad Sternfeld, äußere Station und Ringregel; vergleiche Platz, Aspekt, Ausgang, Ziel und Sollwert. "
        "Nimm die frische Zutat und den bezeichneten Stängel, bereite den Folgeansatz, gewinne den Auszug und stelle die Portion ein. "
        "Führe die Charge durch Zulauf, Becken, Sammelstelle und die wiederholten Übertragungen des langen Arbeitswegs; gib weitere Portionen zu und bringe den Posten schließlich ans Ziel. "
        "Halte den fertigen Pflanzenansatz unter dem gewählten Vergleichswert bereit."
    ),
}


def card_macros(parse: str, reading: str) -> tuple[str, list[str], bool]:
    """Return primary macro, all applicable macros, and commit flag."""
    p = parse.upper()
    r = reading.lower()
    tags: list[str] = []

    def add(mid: str, condition: bool) -> None:
        if condition and mid not in tags:
            tags.append(mid)

    add("M01", any(x in p for x in ("HO_INGREDIENT", "TY_PART")) or any(x in r for x in ("wurzel", "zutat", "stängel", "blüten", "kraut", "teilposten")))
    add("M02", any(x in p for x in ("Y_CURRENT", "Y_ITEM", "OT_", "OL_CONTINUE", "PREVIOUS_ITEM")) or any(x in r for x in ("dieser posten", "folgeposten", "fortsetzen", "weiterf", "voriges", "danach")))
    add("M03", any(x in p for x in ("OR_BATCH", "CHEO_EXTRACT", "AIR_WATER", "CLEAR_LIQUID", "CLEAR_FLOW")) or any(x in r for x in ("ansatz", "auszug", "klarlauf", "wasser", "zusatz")))
    add("M04", any(x in p for x in ("AIIN", "AIN_PORTION", "IIN_", "TY_PART", "EEE_FULL")) or any(x in r for x in ("sollmaß", "fertigmaß", "standmaß", "absetzmaß", "portion", "stufe", "ganzen teil", "anteil")))
    add("M05", any(x in p for x in ("AL_TO", "AR_FROM", "VESSEL", "CLOTH", "T_STORE", "S_PORT")) or any(x in r for x in ("dorthin", "daraus", "von dort", "zielstelle", "gefäß", "tuch", "einlass", "auslass", "verwahren", "öffnung")))
    add("M06", any(x in p for x in ("CHED_TRANSFER", "CHD_TRANSFER", "CKH_THROUGH", "L_OUT", "P_IN", "AIR_WATER", "SK_POUR", "WITHDRAW")) or any(x in r for x in ("umsetzen", "durchleiten", "abführen", "einführen", "abziehen", "weiterleiten", "ausgiessen", "einlassen")))
    add("M07", any(x in p for x in ("OK_SET", "OK+", "SHED_SETTLE", "CHK_WARM", "CKHE_STRAIN", "KCH_PROCESS", "LSH_WASH", "SOLK_COLLECT", "COOL", "APPLY", "SWIVEL", "FASTEN")) or any(x in r for x in ("ansetzen", "wärmen", "seihen", "wasch", "absetzen", "kühlen", "bearbeiten", "auswringen", "nachseihen", "teilen", "befestigen", "füllen", "anwenden", "auftragen", "schwenken", "sammeln")))
    add("M08", any(x in p for x in ("CTH_READY", "SHEY_CLEAR", "RAW", "REST")) or any(x in r for x in ("bereit", "roh", "klar", "ruhen")))
    commit = any(x in p for x in ("CLOSE", "TERMINAL")) or "schluss" in r or r.endswith("ende")
    add("M09", commit)

    if not tags:
        # A learned exact card still occupies a concrete workshop slot.
        tags.append("M07")

    # Select the semantic head, not merely the last formal ending.
    priority = ["M04", "M06", "M07", "M08", "M03", "M01", "M05", "M02", "M09"]
    primary = next(mid for mid in priority if mid in tags)
    return primary, tags, commit


def compact(sequence: list[str]) -> list[str]:
    result: list[str] = []
    for item in sequence:
        if not result or result[-1] != item:
            result.append(item)
    return result


def main() -> None:
    dictionary = read_tsv(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    events = read_tsv(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    phrases = read_tsv(PROSE / "CLOSED_116_PHRASES.tsv")
    dossiers = read_tsv(CASEBOOK / "FOUR_WORKSHOP_DOSSIERS.tsv")
    case_context = read_tsv(CASEBOOK / "TEN_PAGE_776_CASE_CONTEXT.tsv")
    workflow_steps = read_tsv(CASEBOOK / "WORKFLOW_STEPS.tsv")

    context_by_event = {row["local_unit_id"]: row for row in case_context if row["register"] == "PROSE_WORKSHOP"}
    card_by_tuple = {row["joint_tuple_id"]: row for row in dictionary}
    phrase_by_id = {row["statement_id"]: row for row in phrases}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    events_by_tuple: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_statement[event["statement_id"]].append(event)
        events_by_tuple[event["joint_tuple_id"]].append(event)

    macro_rows = [
        {"macro_id": mid, "macro_name_de": name, "apprentice_question_de": question,
         "composition_rule_de": rule, "book_layer": layer}
        for mid, name, question, rule, layer in MACROS
    ]
    write_tsv(OUT / "TEN_WORKSHOP_MACROS.tsv", macro_rows,
              ["macro_id", "macro_name_de", "apprentice_question_de", "composition_rule_de", "book_layer"])

    card_rows: list[dict[str, object]] = []
    tuple_macro: dict[str, tuple[str, list[str], bool]] = {}
    for card in dictionary:
        primary, tags, closes = card_macros(card["closed_parse"], card["closed_reading_de"])
        tuple_macro[card["joint_tuple_id"]] = (primary, tags, closes)
        occurrences = events_by_tuple[card["joint_tuple_id"]]
        dossier_ids = sorted({context_by_event[e["event_id"]]["dossier_id"] for e in occurrences})
        phases = sorted({context_by_event[e["event_id"]]["case_phase"] for e in occurrences})
        card_rows.append({
            "joint_tuple_id": card["joint_tuple_id"], "surface_family": card["surface_family"],
            "occurrences": card["occurrences"], "closed_parse": card["closed_parse"],
            "atomic_default_de": card["closed_reading_de"], "primary_macro": primary,
            "primary_macro_name_de": MACRO_INFO[primary][1], "all_macros": ";".join(tags),
            "closes_local_step": "YES" if closes else "NO", "dossier_count": len(dossier_ids),
            "dossiers": ";".join(dossier_ids), "case_phases": ";".join(phases),
            "portable_status": "PORTABLE_CORE" if len(dossier_ids) >= 3 else ("CROSS_DOSSIER" if len(dossier_ids) == 2 else "LOCAL_OR_SINGLE_DOSSIER"),
        })
    card_fields = ["joint_tuple_id", "surface_family", "occurrences", "closed_parse", "atomic_default_de",
                   "primary_macro", "primary_macro_name_de", "all_macros", "closes_local_step", "dossier_count",
                   "dossiers", "case_phases", "portable_status"]
    write_tsv(OUT / "CARD_MACRO_LEXICON.tsv", card_rows, card_fields)
    portable = [row for row in card_rows if row["portable_status"] != "LOCAL_OR_SINGLE_DOSSIER"]
    portable.sort(key=lambda r: (-int(r["dossier_count"]), -int(r["occurrences"]), str(r["surface_family"])))
    write_tsv(OUT / "CROSS_DOSSIER_PORTABLE_CORE.tsv", portable, card_fields)

    statement_rows: list[dict[str, object]] = []
    transition_counts: Counter[tuple[str, str]] = Counter()
    macro_statement_counts: Counter[str] = Counter()
    dossier_statement_counts: Counter[str] = Counter()
    for phrase in phrases:
        statement_id = phrase["statement_id"]
        statement_events = events_by_statement[statement_id]
        event_macros: list[str] = []
        event_macro_trace: list[str] = []
        for event in statement_events:
            primary, tags, closes = tuple_macro[event["joint_tuple_id"]]
            event_macros.append(primary)
            event_macro_trace.append(f"{event['event_id']}:{primary}{'+M09' if closes and primary != 'M09' else ''}")
            if closes and primary != "M09":
                event_macros.append("M09")
        macro_sequence = compact(event_macros)
        for macro in set(macro_sequence):
            macro_statement_counts[macro] += 1
        for a, b in zip(macro_sequence, macro_sequence[1:]):
            transition_counts[(a, b)] += 1
        dossier_id = context_by_event[statement_events[0]["event_id"]]["dossier_id"]
        dossier_statement_counts[dossier_id] += 1
        statement_rows.append({
            "statement_id": statement_id, "dossier_id": dossier_id, "record_unit_id": phrase["record_unit_id"],
            "page": phrase["page"], "loci": phrase["loci"], "event_count": phrase["event_count"],
            "surface_sequence": phrase["surface_sequence"], "card_reading_sequence_de": phrase["card_reading_sequence_de"],
            "event_macro_trace": " | ".join(event_macro_trace), "macro_sequence": ">".join(macro_sequence),
            "macro_names_de": " > ".join(MACRO_INFO[mid][1] for mid in macro_sequence),
            "normalized_master_clause_de": phrase["fluent_workshop_sentence_de"],
            "ends_with_commit": "YES" if macro_sequence and macro_sequence[-1] == "M09" else "NO",
        })
    statement_fields = ["statement_id", "dossier_id", "record_unit_id", "page", "loci", "event_count",
                        "surface_sequence", "card_reading_sequence_de", "event_macro_trace", "macro_sequence",
                        "macro_names_de", "normalized_master_clause_de", "ends_with_commit"]
    write_tsv(OUT / "STATEMENT_MACRO_PARSES.tsv", statement_rows, statement_fields)

    transition_rows = [
        {"from_macro": a, "from_name_de": MACRO_INFO[a][1], "to_macro": b, "to_name_de": MACRO_INFO[b][1], "statement_internal_count": count}
        for (a, b), count in sorted(transition_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    write_tsv(OUT / "MACRO_TRANSITIONS.tsv", transition_rows,
              ["from_macro", "from_name_de", "to_macro", "to_name_de", "statement_internal_count"])

    usage_rows = []
    for mid, name, question, rule, layer in MACROS:
        card_count = sum(row["primary_macro"] == mid for row in card_rows)
        event_count = sum(int(row["occurrences"]) for row in card_rows if row["primary_macro"] == mid)
        usage_rows.append({"macro_id": mid, "macro_name_de": name, "card_type_count": card_count,
                           "prose_event_count": event_count, "statement_count": macro_statement_counts[mid],
                           "apprentice_question_de": question, "book_layer": layer})
    # M00 is the 395-group condition layer rather than a prose card macro.
    usage_rows[0]["card_type_count"] = 0
    usage_rows[0]["prose_event_count"] = 0
    usage_rows[0]["statement_count"] = 0
    write_tsv(OUT / "MACRO_USAGE_SUMMARY.tsv", usage_rows,
              ["macro_id", "macro_name_de", "card_type_count", "prose_event_count", "statement_count", "apprentice_question_de", "book_layer"])

    dossier_by_id = {row["dossier_id"]: row for row in dossiers}
    master_lines = ["# Vier Meistertexte in tatsächlicher Arbeitsordnung", "",
                    "Die Buchordnung ist `WAS -> WIE -> WANN`. Die tatsächliche Benutzung ist meist `WANN -> WAS -> WIE`: erst Bedingung nachschlagen, dann Material bereiten, dann den örtlichen Arbeitsweg ausführen. Die folgenden Texte sind unsere flüssigste Werkstattrekonstruktion; sie behaupten keine ausgeschriebenen Querverweise im Manuskript.", ""]
    for dossier in dossiers:
        did = dossier["dossier_id"]
        master_lines += [f"## {dossier['title_de']}", "", "### Meisterfassung", "", MASTER_PARAGRAPHS[did], "",
                         "### Buchordnung und vollständige Klauseln", ""]
        dossier_steps = [row for row in workflow_steps if row["dossier_id"] == did]
        for phase in ("WHAT", "HOW", "WHEN"):
            master_lines.append(f"#### {phase}")
            master_lines.append("")
            for step in dossier_steps:
                if step["phase"] != phase:
                    continue
                master_lines.append(f"- **{step['source_unit']} / {step['page']}** — {step['short_action_de']}.")
            master_lines.append("")
        master_lines += ["### Exakte Prosa-Klauseln mit Makrospur", ""]
        for row in statement_rows:
            if row["dossier_id"] == did:
                master_lines.append(f"- **{row['statement_id']}** `{row['macro_sequence']}` — {row['normalized_master_clause_de']}")
        master_lines.append("")
    (OUT / "FOUR_MASTER_SOURCE_TEXTS.md").write_text("\n".join(master_lines).rstrip() + "\n", encoding="utf-8")

    most_common_transitions = transition_rows[:8]
    transition_phrase = ", ".join(f"{r['from_name_de']}→{r['to_name_de']} ({r['statement_internal_count']})" for r in most_common_transitions)
    portable_count = len(portable)
    report = f"""# Gemeinsame Werkstatt-Makrogrammatik

## Neue Arbeitstheorie

Die vier Dossiers teilen nicht bloß Einzelwörter, sondern eine kleine Satzmaschine. Zehn Meisterfragen reichen aus: Bedingung, Material, laufender Posten, Ansatz/Produkt, Menge/Stufe, Quelle/Ziel/Werkzeug, Transfer, Arbeitsgang, Zustand und Abschluss/Übergabe.

Die wichtigste Korrektur ist die Trennung zweier Ordnungen:

- **Buchordnung:** WAS (Herbal) -> WIE (Biological) -> WANN (Astro).
- **Arbeitsordnung:** WANN nachschlagen -> WAS bereiten -> WIE ausführen.

Das macht die räumlich getrennten Seiten praktisch benutzbar, ohne einen geschriebenen Seitenschlüssel zu erfinden.

## Gemeinsamer Kern

Von 173 exakten Prosakarten sind {portable_count} in mindestens zwei der vier Dossiers zu Hause. Die häufigsten tragenden Werte bleiben kurz: `AIIN=Sollmaß`, `Y=dieser Posten`, `OL=fortsetzen`, `OT=Folge`, `AR=daraus`, `AL=dorthin`, `OR=Ansatz`, `CHED=umsetzen`, `OK=ansetzen`, `SHED=absetzen`, `CHK=wärmen`, `CKHE=seihen` und die gelernte ganze Endkarte als Schrittabschluss.

Die häufigsten aussageninternen Übergänge sind: {transition_phrase}.

## Vier flüssige Meisterfälle

1. **Wurzelbad:** rechte Radbedingung wählen; Wurzel und Auszug messen; das gemeinsame Becken füllen, waschen, absetzen, wärmen und seihen.
2. **Klarauszug:** Sternatlas-Modus wählen; Kräuteransatz auswringen, stehen lassen und nachseihen; den Klarauszug durch örtliche Stationen führen.
3. **Tuchanwendung:** Platz, Qualität und Licht getrennt wählen; gelagerten Ansatz portionieren; mit Tuch anlegen, befestigen, nachwaschen und abführen.
4. **Frische Pflanzenfolge:** linkes Sternfeld und Ziel vergleichen; frische Zutat und Stängel bereiten; die Charge durch den langen Becken- und Übertragungsweg führen.

## Schreibregel für mehrere Hände

Der Meister nennt zunächst Besitzer, Arbeitsfall und sichtbare Bedingung. Der Schreiber setzt dann nur die benötigten Makros: Material/Bezug, Ansatz, Maß, Quelle/Ziel, Operation, Zustand und gegebenenfalls die gelernte Endkarte. Lokale Spezialkarten werden als Ganzzeichen kopiert. Eine physische Zeile beendet den Auftrag nicht automatisch.

`CARD_MACRO_LEXICON.tsv` ordnet alle 173 Karten ein; `STATEMENT_MACRO_PARSES.tsv` gibt allen 116 Aussagen eine Makrospur; `FOUR_MASTER_SOURCE_TEXTS.md` enthält die vier flüssigen Meisterfassungen und jede einzelne Klausel.

Die Dossierpaarungen bleiben eine konkrete Werkstatt-Arbeitstheorie und keine behaupteten expliziten Manuskriptverweise.
"""
    (OUT / "WORKSHOP_MACRO_GRAMMAR_REPORT.md").write_text(report, encoding="utf-8")

    outputs = ["TEN_WORKSHOP_MACROS.tsv", "CARD_MACRO_LEXICON.tsv", "CROSS_DOSSIER_PORTABLE_CORE.tsv",
               "STATEMENT_MACRO_PARSES.tsv", "MACRO_TRANSITIONS.tsv", "MACRO_USAGE_SUMMARY.tsv",
               "FOUR_MASTER_SOURCE_TEXTS.md", "WORKSHOP_MACRO_GRAMMAR_REPORT.md"]
    summary = {
        "status": "PASS", "macros": 10, "card_types": len(dictionary), "prose_events": len(events),
        "statements": len(phrases), "dossiers": len(dossiers), "portable_card_types": portable_count,
        "unified_case_groups_inherited": len(case_context),
        "book_order": ["WHAT", "HOW", "WHEN"], "execution_order": ["WHEN", "WHAT", "HOW"],
        "output_sha256": {name: sha(OUT / name) for name in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
