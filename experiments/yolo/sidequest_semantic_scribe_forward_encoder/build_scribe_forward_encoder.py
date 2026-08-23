#!/usr/bin/env python3
"""Build a creative source-command -> card -> surface encoder for ten pages."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE = ROOT / "experiments/yolo/sidequest_semantic_bound_carrier_closure"
MACRO = ROOT / "experiments/yolo/sidequest_semantic_workshop_macro_grammar"
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


# These are deliberately narrow observed paradigms.  They generate an exact
# already learned card; they do not invent an unobserved surface spelling.
RULES = [
    ("P01", "laufenden Posten nennen", "Y", "chey|chy|dy|shy|sy|y", "y", "OPEN", "choose registered local allograph"),
    ("P02", "denselben Arbeitsgang fortsetzen", "OL", "cheol|chol|ol|qol|sol|tol", "ol", "OPEN", "choose registered local allograph"),
    ("P03", "Sollmaß nennen", "AIIN", "aiin|chaiin|daiin|saiin|taiin", "daiin", "OPEN", "choose registered local allograph"),
    ("P04", "eine Portion nennen", "AIN", "chkain|kain", "kain", "OPEN", "choose registered local allograph"),
    ("P05", "Sollstufe nennen", "IIN", "oiiin|soiiin", "oiiin", "OPEN", "choose registered local allograph"),
    ("P06", "Zieladresse nennen", "AL", "al|chal|cheal|dal|sal|tal", "dal", "OPEN", "choose registered local allograph"),
    ("P07", "Quelladresse nennen", "AR", "char|dar|sar", "char", "OPEN", "choose registered local allograph"),
    ("P08", "Ansatz nennen", "OR", "chor|or|shor|sor", "chor", "OPEN", "choose registered local allograph"),
    ("P09", "Zutat nennen", "HO", "cho|sho", "cho", "OPEN", "choose registered local allograph"),
    ("P10", "laufenden Posten ansetzen", "OK+Y", "choky|oky|qoky", "qoky", "OPEN", "q only after a committed cell; otherwise registered bare form"),
    ("P11", "auf Sollmaß einstellen", "OK+AIIN", "okaiin|qokaiin", "qokaiin", "OPEN", "q only after a committed cell"),
    ("P12", "eine Portion zugeben", "OK+AIN", "okain|qokain", "qokain", "OPEN", "q only after a committed cell"),
    ("P13", "am Ziel ansetzen", "OK+AL", "okal|qokal", "qokal", "OPEN", "q only after a committed cell"),
    ("P14", "kurz ansetzen und offen lassen", "OK+E+Y", "okey|qokey", "okey", "OPEN", "choose registered local allograph"),
    ("P15", "länger ansetzen und offen lassen", "OK+EE+Y", "okeey|qokeey", "qokeey", "OPEN", "choose registered local allograph"),
    ("P16", "kurz ansetzen und schließen", "OK+E+DY", "qokedy", "qokedy", "CLOSE", "fixed learned close card"),
    ("P17", "länger ansetzen und schließen", "OK+EE+DY", "qokeedy", "qokeedy", "CLOSE", "fixed learned close card"),
    ("P18", "vollständig ansetzen und schließen", "OK+EEE+DY", "qokeeedy", "qokeeedy", "CLOSE", "fixed learned close card"),
    ("P19", "laufenden Posten umsetzen", "CHED+Y", "chdy|chedy", "chedy", "OPEN", "choose registered local allograph"),
    ("P20", "umsetzen und schließen", "CHED+DY", "dchedy|schedy|tchedy", "dchedy", "CLOSE", "choose registered local allograph"),
    ("P21", "abführen und schließen", "L+CHED+DY", "lchedy", "lchedy", "CLOSE", "fixed learned close card"),
    ("P22", "einführen und schließen", "P+CHED+DY", "pchedy", "pchedy", "CLOSE", "fixed learned close card"),
    ("P23", "fortsetzend umsetzen und schließen", "OL+CHED+DY", "olchedy|qolchedy", "olchedy", "CLOSE", "choose registered local allograph"),
    ("P24", "als Folgeschritt umsetzen und schließen", "OT+CHED+DY", "otchedy|qotchedy", "otchedy", "CLOSE", "choose registered local allograph"),
    ("P25", "kurz absetzen und schließen", "SHED+E+DY", "cheedy|shedy|tedy", "shedy", "CLOSE", "choose registered local allograph"),
    ("P26", "länger absetzen und schließen", "SHED+EE+DY", "sheedy", "sheedy", "CLOSE", "fixed learned close card"),
    ("P27", "kurz wärmen und offen lassen", "CHK+E+Y", "cheky", "cheky", "OPEN", "fixed learned card"),
    ("P28", "länger wärmen und offen lassen", "CHK+EE+Y", "cheeky", "cheeky", "OPEN", "fixed learned card"),
    ("P29", "länger wärmen und schließen", "CHK+EE+DY", "chkeedy", "chkeedy", "CLOSE", "fixed learned close card"),
    ("P30", "durchleiten und offen lassen", "CKH+Y", "chckhy|shckhy", "chckhy", "OPEN", "choose registered local allograph"),
    ("P31", "seihen und schließen", "CKHE+DY", "shckhedy", "shckhedy", "CLOSE", "fixed learned close card"),
    ("P32", "waschen und schließen", "LSH+DY", "lshedy", "lshedy", "CLOSE", "fixed learned close card"),
    ("P33", "kurz sammeln und offen lassen", "SOLK+E+Y", "solkey", "solkey", "OPEN", "fixed learned card"),
    ("P34", "länger sammeln und offen lassen", "SOLK+EE+Y", "solkeey", "solkeey", "OPEN", "fixed learned card"),
    ("P35", "länger sammeln und schließen", "SOLK+EE+DY", "olkeedy|solkeedy", "olkeedy", "CLOSE", "choose registered local allograph"),
    ("P36", "bereit halten", "CTH+Y", "checthy|cthy|shcthy", "cthy", "OPEN", "choose registered local allograph"),
    ("P37", "Klarlauf nennen", "SHEY", "cheey|shey", "cheey", "OPEN", "choose registered local allograph"),
]


EXERCISES = [
    ("X01", "D1_ROOT_BATH_RIGHT_WHEEL", "Wurzelansatz bereitstellen und auf Sollmaß einstellen", "dchey cthoor qokaiin"),
    ("X02", "D1_ROOT_BATH_RIGHT_WHEEL", "Aus demselben Ansatz weiterarbeiten", "char chor chol"),
    ("X03", "D1_ROOT_BATH_RIGHT_WHEEL", "Eine Portion zugeben und kurz geschlossen ansetzen", "qokain qokedy"),
    ("X04", "D1_ROOT_BATH_RIGHT_WHEEL", "Beckenwasser durchleiten und abführen", "kair chckhy lchedy"),
    ("X05", "D2_CLEAR_EXTRACT_STAR_ATLAS", "Auswringen, bis zum Standmaß stehen lassen, nachseihen und Klarlauf kühlen", "cfhy shfydaiin cphy cheey ody"),
    ("X06", "D2_CLEAR_EXTRACT_STAR_ATLAS", "Klarlauf durch die Stelle führen und schließen", "cheey chckhal dchedy"),
    ("X07", "D2_CLEAR_EXTRACT_STAR_ATLAS", "Vom Auszugsansatz eine Portion entnehmen und länger ansetzen", "ycheor cheoar qokain qokeedy"),
    ("X08", "D2_CLEAR_EXTRACT_STAR_ATLAS", "Bereiten Posten fortsetzen und auf Sollmaß bringen", "cthy ol qokaiin"),
    ("X09", "D3_STORED_APPLICATION_THREE_WHEELS", "Tuch an die Zielstelle bringen, länger halten und befestigen", "dain dal qokeey qokylddy"),
    ("X10", "D3_STORED_APPLICATION_THREE_WHEELS", "Klarlauf abführen und danach nachwaschen", "cheey lchedy lkedy"),
    ("X11", "D3_STORED_APPLICATION_THREE_WHEELS", "Vom vorigen Ansatz dort länger arbeiten", "dchol char qokal qokeedy"),
    ("X12", "D3_STORED_APPLICATION_THREE_WHEELS", "Ansatz am Ziel verwahren und den Folgeposten messen", "chor talam otchey qokaiin"),
    ("X13", "D4_FRESH_PLANT_LEFT_WHEEL", "Zutat zum Ziel bringen, Portion zugeben und umsetzen", "cho chodaly qokain qokchdy"),
    ("X14", "D4_FRESH_PLANT_LEFT_WHEEL", "Posten ansetzen, länger offen halten und kurz geschlossen beenden", "qoky qokeey qokedy"),
    ("X15", "D4_FRESH_PLANT_LEFT_WHEEL", "Kurz sammeln, dann länger sammeln und schließen", "solkey olkeedy"),
    ("X16", "D4_FRESH_PLANT_LEFT_WHEEL", "Danach den fertigen Posten anwenden", "cthy sotodan"),
]


def main() -> None:
    dictionary = read_tsv(PROSE / "CLOSED_173_CARD_DICTIONARY.tsv")
    events = read_tsv(PROSE / "CLOSED_381_EVENT_INTERLINEAR.tsv")
    phrases = read_tsv(PROSE / "CLOSED_116_PHRASES.tsv")
    macro_cards = read_tsv(MACRO / "CARD_MACRO_LEXICON.tsv")
    statement_macros = read_tsv(MACRO / "STATEMENT_MACRO_PARSES.tsv")
    case_context = read_tsv(CASEBOOK / "TEN_PAGE_776_CASE_CONTEXT.tsv")
    dossiers = read_tsv(CASEBOOK / "FOUR_WORKSHOP_DOSSIERS.tsv")

    card_by_family = {row["surface_family"]: row for row in dictionary}
    card_by_tuple = {row["joint_tuple_id"]: row for row in dictionary}
    macro_by_tuple = {row["joint_tuple_id"]: row for row in macro_cards}
    event_by_id = {row["event_id"]: row for row in events}
    statement_macro_by_id = {row["statement_id"]: row for row in statement_macros}
    context_by_event = {row["local_unit_id"]: row for row in case_context if row["register"] == "PROSE_WORKSHOP"}

    rule_rows: list[dict[str, object]] = []
    tuple_to_rule: dict[str, str] = {}
    for rid, prompt, formula, family, canonical, closure, selection in RULES:
        card = card_by_family.get(family)
        if not card:
            raise ValueError(f"missing exact family for {rid}: {family}")
        if card["joint_tuple_id"] in tuple_to_rule:
            raise ValueError(f"card assigned to two rules: {family}")
        tuple_to_rule[card["joint_tuple_id"]] = rid
        rule_rows.append({
            "rule_id": rid, "semantic_prompt_de": prompt, "component_formula": formula,
            "exact_surface_family": family, "canonical_copy_form": canonical, "closure": closure,
            "observed_card_occurrences": card["occurrences"], "exact_tuple_id": card["joint_tuple_id"],
            "surface_selection_rule": selection, "status": "OBSERVED_PARADIGM__GENERATE_ONLY_REGISTERED_CARD",
        })
    rule_fields = ["rule_id", "semantic_prompt_de", "component_formula", "exact_surface_family", "canonical_copy_form",
                   "closure", "observed_card_occurrences", "exact_tuple_id", "surface_selection_rule", "status"]
    write_tsv(OUT / "FORWARD_ENCODER_RULES.tsv", rule_rows, rule_fields)

    card_rows: list[dict[str, object]] = []
    for card in dictionary:
        rule_id = tuple_to_rule.get(card["joint_tuple_id"], "")
        if rule_id:
            mode = "PARADIGM_RULE"
        elif card["closed_architecture"] == "PRODUCTIVE_COMPOSITION":
            mode = "COMPOSE_FROM_COMPONENTS"
        else:
            mode = "COPY_WHOLE_CARD"
        macro = macro_by_tuple[card["joint_tuple_id"]]
        card_rows.append({
            "joint_tuple_id": card["joint_tuple_id"], "surface_family": card["surface_family"],
            "semantic_input_de": card["closed_reading_de"], "component_formula": card["closed_parse"],
            "primary_macro": macro["primary_macro"], "encoder_mode": mode,
            "paradigm_rule_id": rule_id or "NONE", "canonical_copy_form": card["surface_family"].split("|")[0],
            "surface_choice_de": "Position/Hand wählt nur eine bereits registrierte Familienform" if "|" in card["surface_family"] else "feste registrierte Form",
            "occurrences": card["occurrences"], "dossiers": macro["dossiers"],
        })
    card_fields = ["joint_tuple_id", "surface_family", "semantic_input_de", "component_formula", "primary_macro",
                   "encoder_mode", "paradigm_rule_id", "canonical_copy_form", "surface_choice_de", "occurrences", "dossiers"]
    write_tsv(OUT / "ENCODER_173_CARD_TABLE.tsv", card_rows, card_fields)

    first_in_locus: set[str] = set()
    seen_loci: set[tuple[str, str]] = set()
    previous_by_record: dict[str, dict[str, str]] = {}
    renderer_by_event: dict[str, str] = {}
    for event in events:
        key = (event["record_unit_id"], event["locus"])
        if key not in seen_loci:
            first_in_locus.add(event["event_id"]); seen_loci.add(key)
        surface = event["surface_display"]
        previous = previous_by_record.get(event["record_unit_id"])
        if surface.startswith("s") and event["event_id"] in first_in_locus:
            renderer = "LINE_ENTRY_S_ALLOGRAPH"
        elif surface.startswith("q") and previous and previous["step_closure_role"] == "COMMIT_CELL":
            renderer = "POST_COMMIT_Q_ALLOGRAPH"
        elif "|" in card_by_tuple[event["joint_tuple_id"]]["surface_family"]:
            renderer = "REGISTERED_LOCAL_ALLOGRAPH"
        else:
            renderer = "FIXED_SURFACE"
        renderer_by_event[event["event_id"]] = renderer
        previous_by_record[event["record_unit_id"]] = event

    event_rows: list[dict[str, object]] = []
    for event in events:
        card = card_by_tuple[event["joint_tuple_id"]]
        macro = macro_by_tuple[event["joint_tuple_id"]]
        rule_id = tuple_to_rule.get(event["joint_tuple_id"], "")
        if rule_id:
            mode = "PARADIGM_RULE"
        elif card["closed_architecture"] == "PRODUCTIVE_COMPOSITION":
            mode = "COMPOSE_FROM_COMPONENTS"
        else:
            mode = "COPY_WHOLE_CARD"
        context = context_by_event[event["event_id"]]
        event_rows.append({
            "event_id": event["event_id"], "dossier_id": context["dossier_id"], "record_unit_id": event["record_unit_id"],
            "statement_id": event["statement_id"], "page": event["page"], "locus": event["locus"],
            "semantic_input_de": event["contextual_event_reading_de"], "primary_macro": macro["primary_macro"],
            "component_formula": card["closed_parse"], "encoder_mode": mode, "paradigm_rule_id": rule_id or "NONE",
            "selected_exact_tuple_id": event["joint_tuple_id"], "selected_surface": event["surface_display"],
            "renderer_choice": renderer_by_event[event["event_id"]], "local_close": event["step_closure_role"],
        })
    event_fields = ["event_id", "dossier_id", "record_unit_id", "statement_id", "page", "locus", "semantic_input_de",
                    "primary_macro", "component_formula", "encoder_mode", "paradigm_rule_id", "selected_exact_tuple_id",
                    "selected_surface", "renderer_choice", "local_close"]
    write_tsv(OUT / "ENCODER_381_EVENT_TRACE.tsv", event_rows, event_fields)

    phrase_surface_set = {row["surface_sequence"] for row in phrases}
    observed_surfaces = {row["surface_display"] for row in events}
    exercise_rows: list[dict[str, object]] = []
    for ex_id, dossier_id, prompt, sequence in EXERCISES:
        tokens = sequence.split()
        missing = [token for token in tokens if token not in observed_surfaces]
        if missing:
            raise ValueError(f"exercise {ex_id} uses unseen surface(s): {missing}")
        semantic_trace = []
        formula_trace = []
        mode_trace = []
        for token in tokens:
            candidates = [event for event in events if event["surface_display"] == token]
            chosen = candidates[0]
            card = card_by_tuple[chosen["joint_tuple_id"]]
            semantic_trace.append(card["closed_reading_de"])
            formula_trace.append(card["closed_parse"])
            mode_trace.append(tuple_to_rule.get(chosen["joint_tuple_id"], "COMPOSE_OR_COPY"))
        exercise_rows.append({
            "exercise_id": ex_id, "dossier_id": dossier_id, "master_dictation_de": prompt,
            "semantic_card_trace_de": " -> ".join(semantic_trace), "component_formula_trace": " | ".join(formula_trace),
            "encoder_rule_trace": " | ".join(mode_trace), "generated_surface_sequence": sequence,
            "sequence_status": "REPRODUCES_EXISTING_STATEMENT" if sequence in phrase_surface_set else "NEW_SEQUENCE_FROM_OBSERVED_CARDS",
            "use_status": "APPRENTICE_EXERCISE__NOT_MANUSCRIPT_TEXT",
        })
    exercise_fields = ["exercise_id", "dossier_id", "master_dictation_de", "semantic_card_trace_de",
                       "component_formula_trace", "encoder_rule_trace", "generated_surface_sequence", "sequence_status", "use_status"]
    write_tsv(OUT / "GENERATED_DICTATION_EXERCISES.tsv", exercise_rows, exercise_fields)

    event_trace_by_id = {row["event_id"]: row for row in event_rows}
    unified_rows: list[dict[str, object]] = []
    for row in case_context:
        if row["register"] == "PROSE_WORKSHOP":
            event = event_trace_by_id[row["local_unit_id"]]
            mode = event["encoder_mode"]
            rule_id = event["paradigm_rule_id"]
            formula = event["component_formula"]
            source_input = event["semantic_input_de"]
            selected_surface = event["selected_surface"]
            renderer = event["renderer_choice"]
        else:
            mode = "ASTRO_SHARED_COMPOSITION" if row["mechanism"] == "COMMON_BRIDGE_RETAINED" else "ASTRO_LOCAL_NOMENCLATOR_COPY"
            rule_id = "A02_SHARED_COMPONENTS" if mode == "ASTRO_SHARED_COMPOSITION" else "A03_LOCAL_VALUE"
            formula = row["nomenclator_layer"]
            source_input = row["operational_reading_de"]
            selected_surface = row["surface_display"]
            renderer = "COPY_AT_VISIBLE_OWNER_ADDRESS"
        unified_rows.append({
            "unified_serial": row["unified_serial"], "dossier_id": row["dossier_id"], "case_phase": row["case_phase"],
            "register": row["register"], "page": row["page"], "locus": row["locus"],
            "semantic_or_operational_input_de": source_input, "encoder_mode": mode, "encoder_rule_id": rule_id,
            "component_or_nomenclator_formula": formula, "selected_surface": selected_surface,
            "renderer_or_address_choice": renderer, "source_status": "OBSERVED_GROUP_REENCODING",
        })
    unified_fields = ["unified_serial", "dossier_id", "case_phase", "register", "page", "locus",
                      "semantic_or_operational_input_de", "encoder_mode", "encoder_rule_id",
                      "component_or_nomenclator_formula", "selected_surface", "renderer_or_address_choice", "source_status"]
    write_tsv(OUT / "TEN_PAGE_776_ENCODER_TRACE.tsv", unified_rows, unified_fields)

    statements_by_dossier: dict[str, list[dict[str, str]]] = defaultdict(list)
    for phrase in phrases:
        events_here = [row for row in events if row["statement_id"] == phrase["statement_id"]]
        dossier_id = context_by_event[events_here[0]["event_id"]]["dossier_id"]
        statements_by_dossier[dossier_id].append(phrase)
    dossier_by_id = {row["dossier_id"]: row for row in dossiers}
    edition_lines = ["# Vier rückwärts codierte Werkstatt-Dossiers", "",
                     "Links steht der Meisterbefehl, rechts die tatsächlich beobachtete Kartenfolge. Das ist die Rückrichtung unserer Arbeitstheorie: Bedeutung/Makro -> exakte Karte -> lokale Oberflächenform. Die zusätzlichen Übungen am Ende sind ausdrücklich neu zusammengesetzte Werkstattübungen und kein Manuskripttext.", ""]
    for dossier_id, dossier in dossier_by_id.items():
        edition_lines += [f"## {dossier['title_de']}", ""]
        for phrase in statements_by_dossier[dossier_id]:
            macro = statement_macro_by_id[phrase["statement_id"]]
            event_modes = [event_trace_by_id[e["event_id"]]["encoder_mode"] for e in events if e["statement_id"] == phrase["statement_id"]]
            edition_lines += [f"### {phrase['statement_id']} / {phrase['page']} {phrase['loci']}", "",
                              f"- Meisterbefehl: {phrase['fluent_workshop_sentence_de']}",
                              f"- Makros: `{macro['macro_sequence']}`",
                              f"- Kartensinne: {phrase['card_reading_sequence_de']}",
                              f"- Auswahlarten: {' -> '.join(event_modes)}",
                              f"- Geschriebene Folge: `{phrase['surface_sequence']}`", ""]
    edition_lines += ["## Neue Diktierübungen", ""]
    for row in exercise_rows:
        edition_lines += [f"- **{row['exercise_id']}** {row['master_dictation_de']} -> `{row['generated_surface_sequence']}` ({row['sequence_status']})."]
    (OUT / "FOUR_REENCODED_DOSSIERS.md").write_text("\n".join(edition_lines).rstrip() + "\n", encoding="utf-8")

    manual = """# Lehrlingsblatt: vom Meisterbefehl zur Kartenfolge

1. Wähle zuerst Dossier und sichtbaren Bildbesitzer.
2. Schlage die Astro-Bedingung am sichtbaren Modul nach; kopiere keine erfundene Kreisordnung.
3. Zerlege den Meisterbefehl in Material, Posten, Ansatz, Maß/Stufe, Quelle/Ziel, Transfer, Handlung, Zustand und Abschluss.
4. Nimm für die häufigen Kombinationen eine der 37 beobachteten Paradigmenkarten.
5. Gibt es keine enge Paradigmenkarte, setze die bereits gelernte Komponentenform aus dem 173-Karten-Lexikon.
6. Ist die Karte eine der 22 Ganzkarten, kopiere sie vollständig aus dem Exemplar.
7. `Y` hält den aktuellen Posten, `OL` denselben Arbeitsgang und `OT` den Folgeschritt.
8. `AIN` wählt die Portion, `AIIN` das Sollmaß und `IIN` die Sollstufe.
9. `AR` wählt die Quelle, `AL` das Ziel, `CHED` den Transfer, `L-CHED` den Ausgang und `P-CHED` den Eingang.
10. `OK` setzt den Arbeitsgang an; `E/EE/EEE` unterscheiden kurz/länger/vollständig nur in gelernten Reihen.
11. Wähle `q`, `s` oder eine bare Form nur innerhalb der registrierten Oberflächenfamilie und nach lokaler Position.
12. Eine gelernte ganze Endkarte schließt die Zelle; sichtbares `dy` allein tut es nicht.
13. Eine offene Zelle übergibt ihren Material- oder Gerätezustand an die nächste Klausel, auch über eine Zeile.
14. Auf den Astro-Seiten komponiere die gemeinsamen Kürzel und kopiere den lokalen Nomenklatorrest an genau seiner sichtbaren Adresse.
15. Erfinde bei der Diktierübung neue Folgen nur aus bereits beobachteten Karten; nenne sie niemals Manuskripttext.
"""
    (OUT / "SCRIBE_ENCODER_MANUAL.md").write_text(manual, encoding="utf-8")

    card_mode_counts = Counter(row["encoder_mode"] for row in card_rows)
    event_mode_counts = Counter(row["encoder_mode"] for row in event_rows)
    astro_mode_counts = Counter(row["encoder_mode"] for row in unified_rows if row["register"] == "ASTRO_DIAGRAM")
    new_exercises = sum(row["sequence_status"] == "NEW_SEQUENCE_FROM_OBSERVED_CARDS" for row in exercise_rows)
    report = f"""# Vorwärtsencoder der Zehnseiten-Werkstatt

## Ergebnis

Die kreative Theorie ist jetzt in beide Richtungen benutzbar. Der Meister kann eine kurze Arbeitsanweisung diktieren; der Schreiber zerlegt sie in Makros, wählt eine Komponentenkarte oder Ganzkarte und setzt anschließend nur eine bereits registrierte Oberflächenform.

Auf Typebene ergeben sich {card_mode_counts['PARADIGM_RULE']} Karten in 37 engen Paradigmenregeln, {card_mode_counts['COMPOSE_FROM_COMPONENTS']} weitere zusammengesetzte Karten und {card_mode_counts['COPY_WHOLE_CARD']} außerhalb der Regeln zu kopierende Ganzkarten. Die zweiundzwanzigste Ganzkartenfamilie `CHEEY/SHEY` besitzt mit P37 bereits eine enge Auswahlregel. Auf Ereignisebene werden {event_mode_counts['PARADIGM_RULE']} der 381 Prosakarten durch die engen Regeln gewählt, {event_mode_counts['COMPOSE_FROM_COMPONENTS']} aus dem weiteren Komponentenlexikon gebaut und {event_mode_counts['COPY_WHOLE_CARD']} vollständig kopiert.

Die Astro-Seiten benutzen dieselbe Werkstattarchitektur anders: {astro_mode_counts['ASTRO_SHARED_COMPOSITION']} Gruppen werden aus gemeinsamen Registerkomponenten gelesen, {astro_mode_counts['ASTRO_LOCAL_NOMENCLATOR_COPY']} lokale Werte werden am sichtbaren Ort kopiert. Zusammen besitzt `TEN_PAGE_776_ENCODER_TRACE.tsv` wieder alle 776 Gruppen.

## Stärkste Vorhersagereihen

- `OK+Y / OK+E+Y / OK+EE+Y` = Posten ansetzen / kurz / länger offen bearbeiten.
- `OK+E+DY / OK+EE+DY / OK+EEE+DY` = kurzer / längerer / vollständiger geschlossener Arbeitsgang.
- `CHED+Y / CHED+DY / L+CHED+DY / P+CHED+DY` = offen umsetzen / geschlossen umsetzen / abführen / einführen.
- `SHED+E+DY / SHED+EE+DY` = kurz oder länger absetzen und schließen.
- `CHK+E+Y / CHK+EE+Y / CHK+EE+DY` = kurz oder länger wärmen, offen oder geschlossen.
- `SOLK+E+Y / SOLK+EE+Y / SOLK+EE+DY` = kurz oder länger sammeln, offen oder geschlossen.

## Lehrlingsproben

Sechzehn Diktierübungen verwenden ausschließlich bereits sichtbare Karten. {new_exercises} ihrer ganzen Folgen kommen nicht als bestehende Aussage vor und sind daher echte Vorhersagen unserer Werkstattgrammatik, aber ausdrücklich kein neu entdeckter Manuskripttext. Beispiele sind `dain dal qokeey qokylddy` für „Tuch an die Zielstelle bringen, länger halten und befestigen“ und `cho chodaly qokain qokchdy` für „Zutat zum Ziel bringen, Portion zugeben und umsetzen“.

## Mehrschreiber-Modell

Alle Schreiber teilen Bedeutungsbundle und exakte Kartenfamilie. Die lokale Hand entscheidet erst danach über eine registrierte `q`-, `s`- oder bare Oberfläche. Damit muss ein Lehrling nicht 173 unabhängige Wörter erfinden: Er lernt 37 häufige Paradigmen, das weitere Komponentenblatt und 22 Ganzkarten.

Die neuen Übungsfolgen sind eine kreative Belastungsprobe der Theorie. Sie werden nicht als Voynich-Text ausgegeben und begründen keine Sprache oder Lautung.
"""
    (OUT / "SCRIBE_FORWARD_ENCODER_REPORT.md").write_text(report, encoding="utf-8")

    outputs = ["FORWARD_ENCODER_RULES.tsv", "ENCODER_173_CARD_TABLE.tsv", "ENCODER_381_EVENT_TRACE.tsv",
               "GENERATED_DICTATION_EXERCISES.tsv", "TEN_PAGE_776_ENCODER_TRACE.tsv", "FOUR_REENCODED_DOSSIERS.md",
               "SCRIBE_ENCODER_MANUAL.md", "SCRIBE_FORWARD_ENCODER_REPORT.md"]
    summary = {
        "status": "PASS", "paradigm_rules": len(RULES), "card_types": len(dictionary),
        "card_mode_counts": dict(card_mode_counts), "prose_events": len(events), "event_mode_counts": dict(event_mode_counts),
        "statements": len(phrases), "dictation_exercises": len(exercise_rows), "new_exercise_sequences": new_exercises,
        "unified_groups": len(unified_rows), "astro_mode_counts": dict(astro_mode_counts),
        "output_sha256": {name: sha(OUT / name) for name in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
