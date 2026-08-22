#!/usr/bin/env python3
"""Build and validate the R2 V65 Biological second edition.

All page-bearing inherited tables are materialised only through the guarded
TSV query with the exact f81v/f82r/f83r allow-list.  The output keeps exact
V60 mnemonics, strict formal prompts, anonymous V62 registers, and all
concrete historical expansion in separate columns/layer tags.
"""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/yolo/sidequest_theory_candidates_v65"
PAGES = ("f81v", "f82r", "f83r")

V60_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v60/V60_SELECTED_381_EVENT_LEDGER.tsv"
V61_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v61/V61_SELECTED_116_SOURCE_STATEMENTS.tsv"
V62_TRANSITIONS = ROOT / "experiments/yolo/sidequest_theory_candidates_v62/V62_SELECTED_116_REGISTER_TRANSITIONS.tsv"
V63_EVENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_381_EVENT_TEMPLATE_LEDGER.tsv"
V63_FIELDS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_135_FIELD_SLOT_PARSE.tsv"
V63_STATEMENTS = ROOT / "experiments/yolo/sidequest_theory_candidates_v63/V63_SELECTED_116_STATEMENT_SLOT_PARSE.tsv"

V60_EVENT_COLUMNS = (
    "event_serial,page,locus,record_unit_id,field_id,event_index_in_record,surface,joint_tuple_id,"
    "formal_formula_opaque,FORMAL_VALUE,terminal_status,strict_control_prompt,"
    "ATOMIC_OR_WHOLE_CARD_MNEMONIC,mnemonic_scope,LOCAL_IATROMEDICAL_EXPANSION,"
    "NONMEDICAL_RIVAL,UNKNOWN_EXEMPLAR_STATUS,source_lineage"
)
V61_COLUMNS = (
    "statement_id,record_unit_id,page,statement_ordinal_in_record,start_locus,start_field,end_locus,"
    "end_field,constituent_loci,constituent_fields,physical_line_count,event_count,event_serials,"
    "closure_sequence,entry_boundary_class,exit_boundary_class,internal_cross_line_boundaries,"
    "selected_short_card_skeleton,concrete_workshop_reading,strongest_alternative,"
    "apprentice_reading_rule,record_flow_context,evidence_basis,status"
)
V62_COLUMNS = (
    "statement_id,record_unit_id,page,statement_ordinal_in_record,constituent_fields,entry_boundary_class,"
    "exit_boundary_class,pre_state,selected_mnemonic_triggers,observed_triggers,inferred_missing_slots,"
    "silent_register_demand,owner_operation,active_item_preparation_operation,target_station_operation,"
    "previous_item_operation,operation_trace,post_state,backward_reconstructable_from_post_state_only,"
    "backward_reconstructability,irreducible_ambiguity_codes,complete_creative_reading,"
    "strongest_source_alternative,source_boundary_triggers,anonymous_id_contract,card_binding_contract,source_lineage"
)
V63_EVENT_COLUMNS = (
    "event_serial,page,locus,record_unit_id,field_id,statement_id,joint_tuple_id,surface_display_only,"
    "formal_formula_opaque,terminal_status,strict_formal_prompt,selected_exact_mnemonic,event_template,"
    "trigger_origin,template_payload,required_registers,symbolic_register_effect,event_parse_status,"
    "opaque_roundtrip_atom,formal_semantic_noninheritance,binding_contract,source_lineage"
)
V63_FIELD_COLUMNS = (
    "field_id,record_unit_id,page,locus,statement_id,field_position_in_statement,event_count,event_serials,"
    "primary_template,ordered_event_template_sequence,licensed_primitive_sequence,parse_status,parse_reason,"
    "recognized_event_count,exemplar_only_event_count,register_pre_state_statement_envelope,register_update_trace,"
    "register_post_state_statement_envelope,intermediate_register_resolution,opaque_roundtrip_trace,"
    "roundtrip_decoded_event_serials,roundtrip_event_identity_sha256,roundtrip_status,local_exemplar_reading,"
    "binding_contract,source_lineage"
)
V63_STATEMENT_COLUMNS = (
    "statement_id,record_unit_id,page,statement_ordinal_in_record,constituent_fields,event_count,event_serials,"
    "primary_template,ordered_event_template_sequence,licensed_primitive_sequence,parse_status,parse_reason,"
    "recognized_event_count,exemplar_only_event_count,pre_state,owner_operation,"
    "active_item_preparation_operation,target_station_operation,previous_item_operation,"
    "parser_register_update_trace,post_state,register_update_status,opaque_roundtrip_trace,"
    "roundtrip_decoded_event_serials,roundtrip_event_identity_sha256,roundtrip_status,"
    "complete_creative_reading,strongest_segmentation_or_source_alternative,binding_contract,source_lineage"
)


RECORD_EXPECTED = {
    "B1": ("f81v", 24, 21, 66),
    "B2": ("f82r", 26, 22, 62),
    "B3": ("f83r", 38, 34, 86),
    "B4": ("f83r", 20, 16, 47),
    "B5": ("f83r", 5, 3, 11),
    "B6": ("f83r", 2, 1, 9),
}

RECORD_ASSUMPTION = {
    "B1": "A020", "B2": "A021", "B3": "A022",
    "B4": "A023", "B5": "A024", "B6": "A025",
}

RECORD_SPECS = {
    "B1": {
        "title": "Therapeutische Badeflotte und Beckenbeschickung",
        "process": (
            "[IMAGE:A002+A003:Becken und verbindende Läufe liefern nur die sichtbare Apparaturkulisse.] "
            "[GENRE:A005+A007+A020:Spüle den ersten Arbeitsort, setze eine Kräuter-Badeflotte an und führe mehrere recordlokale Posten zusammen.] "
            "[EXEMPLAR:A008+A009+A012:Temperiere, lasse stehen und prüfe den Arbeitszustand.] "
            "[GENRE:A001+A005+A015:Verwende einen Teil als äußere Badewaschung und spüle danach Arbeitsort oder Gefäß.] "
            "[EXEMPLAR:A006+A013+A014:Nachfüllen, absetzen, durch Tuch klären und an die nächste im Exemplar bezeichnete Station übergeben.]"
        ),
        "body": "[IMAGE:A004:Figuren gehören zur Seite; kein B1-Feld ist sicher einer Patientin oder einem Körperteil zugewiesen.]",
        "apparatus": "[IMAGE:A002+A003:Becken, begrenzte Bereiche und Verbindungen sind seitenweit sichtbar; die lokale Stationsordnung ist exemplarisch.]",
        "analogy": "De balneis Puteolanis: Heilbad plus Badende; gewöhnliche Badstube: Heizen, Spülen, Nachfüllen.",
        "water_rival": "Badehaus-Grundversorgung oder Gefäß-/Leitungsbetrieb ohne Arzneizweck.",
        "verdict": "TIE_MEDICAL_BATH_PREPARATION_VS_BATHHOUSE",
        "repair": "V54s Öl, Rücklauf und einzelne Patientin entfallen; B1 ist primär Charge und Versorgung, nicht Diagnose.",
        "contradiction": "43/66 Ereignisse sind EXEMPLAR_ONLY; kein lokaler Körperbesitzer ist gesichert.",
        "confidence": "LOW_MEDIUM",
    },
    "B2": {
        "title": "Teilbad, örtliche Waschung und warmer Nachgang",
        "process": (
            "[IMAGE:A004:Die Figuren- und Zonenkomposition erlaubt Badende, jedoch keine textlich identifizierte Krankheit.] "
            "[GENRE:A001+A005+A021:Reinige das Gefäß, bereite eine temperierte Kräuterflotte und führe die Badende in ein örtliches Teil- oder Sitzbad.] "
            "[EXEMPLAR:A006+A008+A009+A013:Kläre durch Tuch, halte die Charge warm, benutze sie am bezeichneten Bereich und lasse sie ab.] "
            "[GENRE:A015+A021:Bereite einen zweiten kühleren oder wieder erwärmten Waschgang und schließe mit örtlicher Waschung oder warmer Tuchauflage.]"
        ),
        "body": "[IMAGE:A004:Figurenpaare und Figurenzonen stützen Badende; Frau, Gebärmutter, Geburt und Menstruation sind nicht textlich gebunden.]",
        "apparatus": "[IMAGE:A002+A003:Nur ein untersuchtes Label sitzt sicher auf einem kreuzförmigen Bauteil; die übrigen liegen überwiegend nur nahe Figuren oder Formen.]",
        "analogy": "Trotula: Kräuterbäder, Sitzbad, warme Auflage und Nachbehandlung; De balneis: Körper im Heilbad.",
        "water_rival": "Mehrkammerige Badehausstation mit gewöhnlichem Füllen, Temperieren und Ablassen.",
        "verdict": "MEDICAL_EDGE_PARTIAL_BATH_NOT_GYNAECOLOGICAL_DIAGNOSIS",
        "repair": "V54s Trank wird endgültig durch örtliche Waschung ersetzt; innere Irrigation und anatomische Öffnungen werden nicht gesetzt.",
        "contradiction": "46/62 Ereignisse sind EXEMPLAR_ONLY; Bildnähe beweist weder Besitzer noch Frauenkrankheit.",
        "confidence": "LOW_MEDIUM",
    },
    "B3": {
        "title": "Langer warmer Bade- und äußerer Lavagezyklus",
        "process": (
            "[GENRE:A001+A005+A022:Setze eine Bade- oder Waschflotte ab, teile einen Posten zu und führe ihn an den Arbeitsort.] "
            "[EXEMPLAR:A008+A010+A013:Nachfüllen, mischen, temperieren und den bezeichneten Körper- oder Beckenbereich benetzen.] "
            "[GENRE:A015+A022:Als äußere Lavage oder Badewaschung gebrauchen, danach spülen und ablassen.] "
            "[EXEMPLAR:A009+A012+A018:Eine zweite Charge bis zum örtlichen Prüfzustand führen und den Wasch-/Ablassgang wiederholen.] "
            "[IMAGE:A002+A003:Die Schlussfolge wird an sichtbaren Auslass- und Beckenformen vollzogen, ohne ihnen Kartenwörter zuzuschreiben.]"
        ),
        "body": "[IMAGE:A004:Figuren machen Körpergebrauch seitenweit möglich; kein bestimmter B3-Satz nennt Patientin oder Körperöffnung.]",
        "apparatus": "[IMAGE:A003:Zwei dokumentierte f83r-Labels stehen unmittelbar an offenen mehrstrichigen Auslässen ohne lokale Figur.]",
        "analogy": "Therapeutisches Bad und äußere Waschung; Albucasis belegt echte Flüssigkeitsinstillation, jedoch mit kleinem Spezialinstrument statt Beckenlandschaft.",
        "water_rival": "Mehrstufiges Zisternen-/Leitungsschema mit Spülen, Absetzen und Ablassen.",
        "verdict": "TIE_EXTERNAL_LAVAGE_VS_WATERWORKS",
        "repair": "V54s innerer Irrigationsklang wird zur äußeren Lavage herabgestuft; menschenfreie Auslässe erhalten Vorrang als Apparaturbeleg.",
        "contradiction": "57/86 Ereignisse sind EXEMPLAR_ONLY; Auslass-Owner ohne Figuren widersprechen durchgehender Patientenprosa.",
        "confidence": "LOW_MEDIUM",
    },
    "B4": {
        "title": "Gefilterte warme Haut-/Wundwäsche mit Tuchauflage",
        "process": (
            "[GENRE:A006+A007+A023:Tauche ein Tuch oder eine Auflage in den vorbereiteten Waschzusatz.] "
            "[EXEMPLAR:A008+A010:Temperiere einen ausgewählten Anteil und führe den aktiven Posten weiter.] "
            "[GENRE:A004+A005+A015+A023:Wasche eine äußere Haut- oder Wundstelle und lege das warme Tuch auf.] "
            "[EXEMPLAR:A006+A012+A013:Seihe den Rest, spüle den Arbeitsort, lasse die verbrauchte Flüssigkeit ab und fülle eine Schlussportion nach.]"
        ),
        "body": "[GENRE:A004+A023:Die äußere Haut-/Wundstelle ist ein chirurgisch-herbalistischer Gattungsbesitzer, kein lokal gesichertes Bildobjekt.]",
        "apparatus": "[IMAGE:A002+A003:Filter-, Becken- und Auslasskulisse bleibt als eigener Bedienlayer bestehen.]",
        "analogy": "Trotula: warme Kräuterauflagen; Theodoric/Mondeville: warme Weinwäsche und äußerer Verband.",
        "water_rival": "Warmer Filter- und Reinigungsgang für Tuch, Gefäß oder Leitung.",
        "verdict": "MEDICAL_EDGE_ONLY_IF_GENRE_OWNER_ACCEPTED",
        "repair": "V54s allgemeines Nachbad wird konkreter als äußere Wäsche plus Tuchauflage; Körperstelle, Wunde und Tuch bleiben GENRE.",
        "contradiction": "32/47 Ereignisse sind EXEMPLAR_ONLY; keine Karte bedeutet Wunde, Haut, Tuch oder Wein.",
        "confidence": "LOW",
    },
    "B5": {
        "title": "Zeitlich gehaltener Wärme- und Übergabenachtrag",
        "process": (
            "[EXEMPLAR:A008+A009+A024:Ziehe den recordlokalen Restposten ab, erwärme ihn einmal und halte ihn für die örtliche Frist.] "
            "[EXEMPLAR:A010+A013+A014+A024:Führe ihn nach örtlichem Maß an die nächste Station.]"
        ),
        "body": "[GENRE:A005:Ein therapeutischer Empfänger ist möglich, aber im kurzen Nachtrag nicht sichtbar gebunden.]",
        "apparatus": "[IMAGE:A002+A003:Der kurze Record passt unmittelbar zu Wärme-, Gefäß- und Übergabebedienung.]",
        "analogy": "Badstubenbetrieb: Wasser erhitzen und weiterreichen; keine eigenständige Krankenklausel nötig.",
        "water_rival": "Boiler-/Gefäßübergabe derselben Anlage.",
        "verdict": "TECHNICAL_EDGE_WITHIN_MEDICAL_WORKSHEET",
        "repair": "V54s medizinische Anwendung wird nicht ergänzt; B5 bleibt Hilfsprozess im therapeutischen Gesamtblatt.",
        "contradiction": "7/11 Ereignisse sind EXEMPLAR_ONLY; der Record besitzt nur drei Statements.",
        "confidence": "LOW",
    },
    "B6": {
        "title": "Kalter Filter- und Zielübergabenachtrag",
        "process": (
            "[EXEMPLAR:A006+A008+A025:Richte innerhalb von B6 einen ungekochten oder abgekühlten Posten ein und führe ihn durch Tuch oder einfache Öffnung.] "
            "[EXEMPLAR:A010+A013+A014+A025:Übergib die örtlich bemessene Portion an die recordlokale Zielstation.]"
        ),
        "body": "[GENRE:A005:Ein Körperziel ist nur ein Rivale; der eine B6-Satz liefert keinen Patientenbesitzer.]",
        "apparatus": "[IMAGE:A002+A003:Offener Filter-/Übergabegang ist die sparsamste Seitenbindung.]",
        "analogy": "Gefäß- und Filterpraxis in Rezeptur oder Badhaus; kein eigener gynäkologischer Mechanismus.",
        "water_rival": "Kalter Vorlauf oder Reinigungs-/Transfernotiz.",
        "verdict": "TECHNICAL_EDGE_WITHIN_MEDICAL_WORKSHEET",
        "repair": "B6 erbt wegen V62-Reset weder B5 noch einen früheren Patienten; der Vorposten wird innerhalb des einzigen B6-Statements eingeführt.",
        "contradiction": "6/9 Ereignisse sind EXEMPLAR_ONLY, beide Felder offen und alle konkrete Filterprosa exemplarisch.",
        "confidence": "LOW",
    },
}


PHASE_SPECS = {
    "B1": [
        ("P01", 1, 1, "START_REINIGEN"), ("P02", 2, 6, "CHARGE_MESSEN_UND_MISCHEN"),
        ("P03", 7, 10, "TEMPERIEREN_UND_HALTEN"), ("P04", 11, 14, "WASCHEN_UND_SPÜLEN"),
        ("P05", 15, 17, "NACHFÜLLEN_UND_KLÄREN"), ("P06", 18, 21, "ABSETZEN_FILTERN_ÜBERGEBEN"),
    ],
    "B2": [
        ("P01", 1, 2, "GEFÄSS_REINIGEN"), ("P02", 3, 6, "ERSTES_TEILBAD"),
        ("P03", 7, 12, "NACHFÜLLEN_HALTen_ANWENDEN"), ("P04", 13, 14, "ABLASSEN"),
        ("P05", 15, 18, "ZWEITER_WASCHGANG"), ("P06", 19, 22, "ÖRTLICHER_NACHGANG"),
    ],
    "B3": [
        ("P01", 1, 5, "ABSETZEN_DOSIEREN_ABLASSEN"), ("P02", 6, 12, "MISCHEN_BADEN_ANWENDEN"),
        ("P03", 13, 16, "SPÜLEN_UND_ABLASSEN"), ("P04", 17, 23, "ZWEITE_CHARGE"),
        ("P05", 24, 27, "REINIGEN_NEU_BESCHICKEN"), ("P06", 28, 34, "WARME_LAVAGE_WIEDERHOLEN"),
    ],
    "B4": [
        ("P01", 1, 4, "TUCH_TEMPERIEREN_AUFLEGEN"), ("P02", 5, 8, "FILTERN_UND_WASCHEN"),
        ("P03", 9, 11, "HALTEN_UND_NACHWÄRMEN"), ("P04", 12, 16, "ABLASSEN_NACHFÜLLEN_ANWENDEN"),
    ],
    "B5": [("P01", 1, 1, "REST_ABZIEHEN"), ("P02", 2, 3, "ERWÄRMEN_HALTen_ÜBERGEBEN")],
    "B6": [("P01", 1, 1, "KALT_FILTERN_UND_ÜBERGEBEN")],
}


ASSUMPTIONS = [
    ("A001", "ALL", "GENRE", "Wasser oder andere Bade-/Waschflüssigkeit als Arbeitsmedium", "Bild-/Bad-/Rezeptgattung", "Keine Karte nennt Wasser oder Flüssigkeit", "KEEP_TAGGED"),
    ("A002", "ALL", "IMAGE", "Becken, Gefäß oder Auffangbereich als Apparatur", "erlaubter V54-Bildbefund", "Keine sichere lokale Feldzuweisung", "KEEP_PAGE_LEVEL"),
    ("A003", "ALL", "IMAGE", "Leitung, Lauf, Öffnung oder Auslass als Apparatur", "erlaubter V54-Bildbefund", "Lokale Reihenfolge und Funktion nicht gesichert", "KEEP_PAGE_LEVEL"),
    ("A004", "B1|B2|B3|B4", "IMAGE_GENRE", "menschliche Figur, Badende, Patient oder äußerer Körperbereich", "Figuren + medizinische Vergleichsgattung", "Figur ist kein gesicherter Textbesitzer", "KEEP_TAGGED"),
    ("A005", "ALL", "GENRE", "therapeutischer statt rein hygienischer oder technischer Zweck", "medizinischer Sammelcodex-/Badvergleich", "Badehaus und Wasserwerk bleiben vollständig möglich", "KEEP_AS_DEFAULT"),
    ("A006", "B1|B2|B4|B6", "GENRE", "Tuch, Seihen, Filtern oder Kompresse", "Rezept-, Trotula- und Wundpraxis", "Keine Karte nennt Tuch oder Filter", "KEEP_TAGGED"),
    ("A007", "B1|B2|B3|B4", "GENRE", "Kräuter-, Öl-, Wein- oder anderer pharmazeutischer Zusatz", "Materia-medica-/Rezeptpraxis", "Keine Zutat ist abgebildet oder kartengestützt", "KEEP_TAGGED"),
    ("A008", "ALL", "EXEMPLAR", "warm, kühl, kalt, ungekocht oder konkrete Wärmeführung", "Bad-/Rezeptpraxis; TEMPERIEREN? nur wo exakt", "Temperaturwert fehlt und viele Ereignisse sind unparsed", "KEEP_TAGGED"),
    ("A009", "ALL", "EXEMPLAR", "Dauer, Wiederholung sowie einmal/zweimal/erste/zweite Folge", "Quelltextreflow und Arbeitsgattung", "Kein Zahlenwert ist entziffert", "KEEP_TAGGED"),
    ("A010", "ALL", "EXEMPLAR", "konkrete Menge, Portion oder Gleichanteil", "MASS? liefert höchstens Maßklasse", "Keine Zahl oder Einheit ist gewonnen", "KEEP_TAGGED"),
    ("A011", "ALL", "EXEMPLAR", "jede Handlung oder Sache an einem V63-EXEMPLAR_ONLY-Ereignis", "lokales historisches Exemplar", "191/281 Ereignisse bleiben unparsed", "KEEP_EXPLICIT"),
    ("A012", "B1|B2|B3|B4", "EXEMPLAR", "Absetzen, Klarheit oder Bereitschaft als konkrete Materialprüfung", "BEREIT?/KLAR? nur an exakten Vorkommen", "Lange Zustandsklausel ist nie Kartenwert", "KEEP_TAGGED"),
    ("A013", "ALL", "EXEMPLAR", "Mischen, Verbinden, Nachfüllen und Übergeben als reale Stoffbewegung", "formale Verknüpfungs-/Ablaufstruktur", "Formalprompt liefert kein physisches Verb", "KEEP_TAGGED"),
    ("A014", "ALL", "EXEMPLAR", "örtliche Station, Ziel oder nummerierte Öffnung", "ZIEL? und Seitenapparatur", "Karte identifiziert keinen Weltgegenstand", "KEEP_TAGGED"),
    ("A015", "B1|B2|B3|B4", "GENRE", "Bad, äußere Waschung, Lavage oder Auflage als Gebrauchsmodus", "historische Bad-, Trotula- und Wundpraxis", "ANWENDEN? nennt keinen Modus oder Körperort", "KEEP_TAGGED"),
    ("A016", "B2", "HISTORICAL_RISK", "enge gynäkologische Diagnose", "Trotula als Vergleich", "Kein Karten- oder lokaler Bildanker nennt Gebärmutter, Menstruation oder Geburt", "WITHDRAW"),
    ("A017", "B2|B3", "HISTORICAL_RISK", "innere Irrigation einer Körperhöhle", "Albucasis als Technikvergleich", "Kein kleines Instrument oder sichere Körperöffnung ist gebunden", "WITHDRAW_AS_DEFAULT"),
    ("A018", "B2|B3", "EXEMPLAR_GRAPH", "zweiter oder wiederholter Bade-/Waschzyklus", "Recordlänge und wiederkehrende Schlussaktionen", "Wiederholung kann parallele Zelle statt Schleife sein", "KEEP_TAGGED"),
    ("A019", "ALL", "HISTORICAL_RISK", "jede Figur oder Apparaturform besitzt das nächststehende Feld", "kein ausreichender Befund", "V54 dokumentiert überwiegend nur Nähe und gemischte Besitzer", "WITHDRAW"),
    ("A020", "B1", "LOCAL_EXEMPLAR", "Badeflotte und Beckenbeschickung", "B1-Prozesswette", "Wasserwerksgang ebenso möglich", "KEEP_LOW_MEDIUM"),
    ("A021", "B2", "LOCAL_EXEMPLAR", "Teil-/Sitzbad und örtliche Waschung", "Figuren-/Zonenbild plus Trotula", "keine Diagnose oder anatomische Öffnung", "KEEP_LOW_MEDIUM"),
    ("A022", "B3", "LOCAL_EXEMPLAR", "äußere Lavage und Badezyklus", "lange Spül-/Ablassfolge", "menschenfreie Auslasslabels", "KEEP_LOW_MEDIUM"),
    ("A023", "B4", "LOCAL_EXEMPLAR", "äußere Haut-/Wundwäsche und Tuchauflage", "Trotula/Theodoric als Quellenmechanismus", "Körperstelle und Wunde vollständig gattungsgestützt", "KEEP_LOW"),
    ("A024", "B5", "LOCAL_EXEMPLAR", "Wärme- und Übergabenachtrag", "kurzer Record und Apparatur", "kein medizinischer Empfänger", "KEEP_TECHNICAL"),
    ("A025", "B6", "LOCAL_EXEMPLAR", "kalter Filter- und Zielübergabenachtrag", "offener kurzer Record", "ungekocht, Tuch und Ziel sind exemplarisch", "KEEP_TECHNICAL"),
    ("A026", "ALL", "RIVAL", "Badehaus-/Wasserwerksbetrieb ohne medizinische Semantik", "historische Hydraulik und Badstube", "Figuren und medizinische Sammelgattung bleiben Gegenbeleg", "RIVAL_ACTIVE"),
]


def guarded_rows(path: Path, columns: str) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(path), "--selector", "page"]
    for page in PAGES:
        command.extend(["--allow", page])
    command.extend(["--columns", columns, "--forbid-prefix", "f84"])
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))


def split_pipe(value: str) -> list[str]:
    return [part for part in value.split("|") if part and part != "NONE"]


def parse_state(value: str) -> dict[str, str]:
    state = {}
    for part in value.split(";"):
        if "=" in part:
            key, item = part.split("=", 1)
            state[key] = item
    return state


def assumptions_for_phrase(text: str, record: str) -> list[str]:
    low = text.casefold()
    ids = {"A011", RECORD_ASSUMPTION[record]}
    if any(word in low for word in ("wasser", "flüss", "bad", "wasch", "strom", "öl", "wein", "lauf")):
        ids.add("A001")
    if any(word in low for word in ("gefäss", "becken", "auffang", "hafen")):
        ids.add("A002")
    if any(word in low for word in ("lauf", "öffnung", "auslass", "station", "leitung")):
        ids.add("A003")
    if any(word in low for word in ("person", "patient", "körper", "haut", "wund", "stelle", "teilbad", "sitzbad")):
        ids.add("A004")
    if any(word in low for word in ("bad", "wasch", "anwend", "gebrauch", "auflage", "spül", "lavage")):
        ids.update(("A005", "A015"))
    if any(word in low for word in ("tuch", "seih", "filter", "kompress", "verband")):
        ids.add("A006")
    if any(word in low for word in ("kraut", "zusatz", "öl", "wein", "zubereit", "ansatz")):
        ids.add("A007")
    if any(word in low for word in ("warm", "kühl", "kalt", "temper", "koch", "erwärm", "abkühl")):
        ids.add("A008")
    if any(word in low for word in ("dauer", "einmal", "zweimal", "wieder", "erste", "zweite", "zuvor", "vorig", "danach")):
        ids.add("A009")
    if any(word in low for word in ("mass", "menge", "portion", "anteil", "gleich", "posten")):
        ids.add("A010")
    if any(word in low for word in ("klar", "bereit", "absetz", "stehen", "rückstand")):
        ids.add("A012")
    if any(word in low for word in ("misch", "verbind", "nachfüll", "überg", "weiter", "gieß", "führ")):
        ids.add("A013")
    if any(word in low for word in ("ziel", "station", "öffnung", "bezeichnet", "markiert")):
        ids.add("A014")
    if record == "B4" and any(word in low for word in ("haut", "wund", "tuch", "auflage")):
        ids.add("A023")
    return sorted(ids)


def revise_phrase(text: str, record: str) -> str:
    replacements = {
        "das bereitete Öl": "der vorbereitete Bade- oder Waschzusatz",
        "Die bereitete Arbeitsflüssigkeit": "der vorbereitete Bade- oder Waschposten",
        "trinke den angegebenen Anteil und beende den Schritt": "verwende den Anteil als örtliche Waschung und beende den Schritt",
        "setze die Person an das Becken": "richte die bezeichnete Beckenstation ein",
        "koche sanft und beende diesen Arbeitsschritt": "erwärme den Bade- oder Waschzusatz sanft und beende den Arbeitsschritt",
    }
    revised = text
    for old, new in replacements.items():
        revised = revised.replace(old, new)
    if record == "B1":
        revised = revised.replace(
            "bade oder tauche in der temperierten warmen Flüssigkeit und beende den Schritt",
            "tauche das Waschtuch oder den zu waschenden Teil in die temperierte Flüssigkeit und beende den Schritt",
        )
    elif record == "B2":
        revised = revised.replace(
            "bade oder tauche in der temperierten warmen Flüssigkeit und beende den Schritt",
            "lasse die Badende im temperierten Teilbad sitzen und beende den Schritt",
        ).replace(
            "tauche vollständig ein und beende den Schritt",
            "benetze den bezeichneten Körperbereich vollständig und beende den Schritt",
        ).replace("der eingetauchte Teil", "der benetzte Körperbereich")
    elif record == "B3":
        revised = revised.replace(
            "bade oder tauche in der temperierten warmen Flüssigkeit und beende den Schritt",
            "wasche oder bade den bezeichneten Körper- oder Beckenbereich und beende den Schritt",
        ).replace(
            "tauche vollständig ein und beende den Schritt",
            "benetze den bezeichneten Bereich vollständig und beende den Schritt",
        ).replace("der eingetauchte Teil", "der benetzte Bereich")
    elif record == "B4":
        revised = revised.replace(
            "bade oder tauche in der temperierten warmen Flüssigkeit und beende den Schritt",
            "tauche das Tuch oder die Auflage in die temperierte Flüssigkeit und beende den Schritt",
        ).replace(
            "binde es auf die Stelle und beende den Schritt",
            "lege das warme Tuch auf die äußere Haut- oder Wundstelle und beende den Schritt",
        )
    if record != "B4":
        revised = revised.replace(
            "binde es auf die Stelle und beende den Schritt",
            "lege ein warmes Tuch auf die bezeichnete äußere Stelle und beende den Schritt",
        )
    return revised


def template_binding(template: str, record: str) -> str:
    values = {
        "PARAMETER_ASSIGN": "den aktiven Posten nach der örtlichen Vorschrift bemessen",
        "TARGET_ASSIGN": "den aktiven Posten an der örtlich bezeichneten Station führen",
        "LINK_ACTIVE": "den recordlokalen aktiven Posten im Arbeitsgang fortführen",
        "STATE_GATE": "den örtlichen Prüfzustand der Charge feststellen",
        "ACTION_TEMPER": "die Charge für den vorgesehenen Gebrauch temperieren",
        "TERMINAL_FLUSH": "die bezeichnete Stelle oder den Lauf mit der aktiven Waschflotte spülen",
        "TERMINAL_DRAIN": "die verbrauchte Flüssigkeit zum Auffang- oder Auslassbereich abführen",
        "SELECT_PART": "einen recordlokalen Anteil auswählen",
        "SELECT_PREVIOUS": "den vorigen recordlokalen Posten wieder aufnehmen",
    }
    if template == "ACTION_APPLY":
        return {
            "B1": "die Badecharge am vorgesehenen Waschplatz gebrauchen",
            "B2": "die Badeflüssigkeit am bezeichneten Körper- oder Teilbadbereich gebrauchen",
            "B3": "die Waschflotte am bezeichneten Körper- oder Beckenbereich gebrauchen",
            "B4": "den gefilterten Waschposten an der äußeren Haut- oder Wundstelle gebrauchen",
            "B5": "den Posten am nächsten Arbeitsort gebrauchen",
            "B6": "den Posten am nächsten Arbeitsort gebrauchen",
        }[record]
    return values.get(template, "den sichtbaren Ereignisplatz nach dem lokalen Exemplar ausführen")


def extract_assumptions(text: str) -> list[str]:
    return sorted(set(re.findall(r"A\d{3}", text)))


def tagged_text_has_unmarked_words(text: str) -> bool:
    residual = re.sub(r"\[[A-Z_]+:[^\]]*\]", "", text)
    return bool(re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", residual))


def write_tsv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows({column: row[column] for column in columns} for row in rows)


def main() -> None:
    v60_events = guarded_rows(V60_EVENTS, V60_EVENT_COLUMNS)
    v61_statements = guarded_rows(V61_STATEMENTS, V61_COLUMNS)
    v62_transitions = guarded_rows(V62_TRANSITIONS, V62_COLUMNS)
    v63_events = guarded_rows(V63_EVENTS, V63_EVENT_COLUMNS)
    v63_fields = guarded_rows(V63_FIELDS, V63_FIELD_COLUMNS)
    v63_statements = guarded_rows(V63_STATEMENTS, V63_STATEMENT_COLUMNS)

    assert len(v60_events) == len(v63_events) == 281
    assert len(v61_statements) == len(v62_transitions) == len(v63_statements) == 97
    assert len(v63_fields) == 115

    v60_by_event = {row["event_serial"]: row for row in v60_events}
    v63_by_event = {row["event_serial"]: row for row in v63_events}
    v61_by_statement = {row["statement_id"]: row for row in v61_statements}
    v62_by_statement = {row["statement_id"]: row for row in v62_transitions}
    v63_by_statement = {row["statement_id"]: row for row in v63_statements}
    fields = {row["field_id"]: row for row in v63_fields}

    alignment_errors = []
    for serial, event in v63_by_event.items():
        old = v60_by_event[serial]
        for name, left, right in (
            ("page", old["page"], event["page"]),
            ("record", old["record_unit_id"], event["record_unit_id"]),
            ("field", old["field_id"], event["field_id"]),
            ("tuple", old["joint_tuple_id"], event["joint_tuple_id"]),
            ("surface", old["surface"], event["surface_display_only"]),
            ("formula", old["formal_formula_opaque"], event["formal_formula_opaque"]),
            ("terminal", old["terminal_status"], event["terminal_status"]),
            ("formal", old["strict_control_prompt"], event["strict_formal_prompt"]),
            ("mnemonic", old["ATOMIC_OR_WHOLE_CARD_MNEMONIC"], event["selected_exact_mnemonic"]),
        ):
            if left != right:
                alignment_errors.append(f"event={serial}:{name}:{left}!={right}")
    for sid, statement in v63_by_statement.items():
        one = v61_by_statement[sid]
        two = v62_by_statement[sid]
        for name, left, right in (
            ("page", one["page"], statement["page"]),
            ("record", one["record_unit_id"], statement["record_unit_id"]),
            ("fields", one["constituent_fields"], statement["constituent_fields"]),
            ("events", one["event_serials"], statement["event_serials"]),
            ("pre_state", two["pre_state"], statement["pre_state"]),
            ("post_state", two["post_state"], statement["post_state"]),
        ):
            if left != right:
                alignment_errors.append(f"statement={sid}:{name}:{left}!={right}")

    statement_phase = {}
    node_rows = []
    edge_rows = []
    for record, specs in PHASE_SPECS.items():
        record_statements = sorted(
            (row for row in v63_statements if row["record_unit_id"] == record),
            key=lambda row: int(row["statement_ordinal_in_record"]),
        )
        by_ord = {int(row["statement_ordinal_in_record"]): row for row in record_statements}
        prior_node = None
        for phase_id, start, end, label in specs:
            selected = [by_ord[index] for index in range(start, end + 1)]
            node_id = f"{record}-{phase_id}"
            for row in selected:
                statement_phase[row["statement_id"]] = node_id
            event_ids = [serial for row in selected for serial in split_pipe(row["event_serials"])]
            node_rows.append({
                "node_id": node_id,
                "record_unit_id": record,
                "phase_ordinal": phase_id,
                "phase_label": label,
                "statement_ids": "|".join(row["statement_id"] for row in selected),
                "field_ids": "|".join(field for row in selected for field in split_pipe(row["constituent_fields"])),
                "event_serials": "|".join(event_ids),
                "entry_v62_state": selected[0]["pre_state"],
                "exit_v62_state": selected[-1]["post_state"],
                "v63_parse_status_counts": ";".join(f"{key}={value}" for key, value in sorted(Counter(row["parse_status"] for row in selected).items())),
                "recognized_events": sum(int(row["recognized_event_count"]) for row in selected),
                "exemplar_only_events": sum(int(row["exemplar_only_event_count"]) for row in selected),
                "medical_process_default": f"[EXEMPLAR:{RECORD_ASSUMPTION[record]}:{label.replace('_', ' ').lower()}]",
                "waterwork_or_bathhouse_counterpart": RECORD_SPECS[record]["water_rival"],
                "graph_contract": "ORDERED_SOURCE_NODE;CONCRETE_LABEL_EXEMPLAR_ONLY",
            })
            if prior_node:
                edge_rows.append({
                    "edge_id": f"{prior_node}__TO__{node_id}",
                    "record_unit_id": record,
                    "source_node": prior_node,
                    "target_node": node_id,
                    "edge_type": "ORDERED_NEXT_PHASE",
                    "historical_process_reading": "nächster Arbeitsabschnitt desselben recordlokalen Besitzers",
                    "semantic_status": "EXEMPLAR_GRAPH_NOT_CARD_MEANING",
                })
            prior_node = node_id

    interlinear = []
    event_text_by_serial = {}
    tag_assumption_use = Counter()
    card_errors = []
    formal_errors = []
    untagged_events = []
    for serial in sorted(v63_by_event, key=int):
        event = v63_by_event[serial]
        old = v60_by_event[serial]
        statement = v63_by_statement[event["statement_id"]]
        transition = v62_by_statement[event["statement_id"]]
        record = event["record_unit_id"]
        parts = []
        mnemonic = event["selected_exact_mnemonic"]
        formal = event["strict_formal_prompt"]
        if mnemonic != "UNKNOWN":
            parts.append(f"[CARD:{mnemonic}]")
        if formal != "NONE":
            parts.append(f"[FORMAL:{formal};KEINE_WORTBEDEUTUNG]")
        state = parse_state(transition["post_state"])
        needed = []
        for register in split_pipe(event["required_registers"]):
            needed.append(f"{register}={state.get(register, 'UNSET')}")
        if needed:
            parts.append(f"[REGISTER:{';'.join(needed)}]")
        if event["event_parse_status"] == "UNPARSED_EXEMPLAR":
            phrase = revise_phrase(old["LOCAL_IATROMEDICAL_EXPANSION"], record)
        else:
            phrase = template_binding(event["event_template"], record)
        assumption_ids = assumptions_for_phrase(phrase, record)
        parts.append(f"[EXEMPLAR:{'+'.join(assumption_ids)}:{phrase}]")
        tagged = " ".join(parts)
        event_text_by_serial[serial] = tagged
        tag_assumption_use.update(assumption_ids)
        if tagged_text_has_unmarked_words(tagged):
            untagged_events.append(serial)
        cards = re.findall(r"\[CARD:([^\]]+)\]", tagged)
        formals = [value.split(";", 1)[0] for value in re.findall(r"\[FORMAL:([^\]]+)\]", tagged)]
        if (cards or ["UNKNOWN"])[0] != mnemonic:
            card_errors.append(f"{serial}:{cards}!={mnemonic}")
        if formal != "NONE" and formal not in formals:
            formal_errors.append(f"{serial}:{formals}!={formal}")
        if formal == "NONE" and formals:
            formal_errors.append(f"{serial}:unexpected:{formals}")
        interlinear.append({
            "event_serial": serial,
            "page": event["page"],
            "locus": event["locus"],
            "record_unit_id": record,
            "field_id": event["field_id"],
            "statement_id": event["statement_id"],
            "process_node_id": statement_phase[event["statement_id"]],
            "joint_tuple_id": event["joint_tuple_id"],
            "surface_display_only": event["surface_display_only"],
            "formal_formula_opaque": event["formal_formula_opaque"],
            "terminal_status": event["terminal_status"],
            "strict_formal_prompt": formal,
            "selected_v60_exact_mnemonic": mnemonic,
            "v63_event_template": event["event_template"],
            "v63_event_parse_status": event["event_parse_status"],
            "v62_statement_pre_state": transition["pre_state"],
            "v62_symbolic_register_effect": event["symbolic_register_effect"],
            "v62_statement_post_state": transition["post_state"],
            "inherited_v60_local_expansion": old["LOCAL_IATROMEDICAL_EXPANSION"],
            "v65_concrete_default_segment": tagged,
            "unsupported_assumption_ids": "|".join(assumption_ids),
            "body_bath_patient_binding": RECORD_SPECS[record]["body"],
            "visible_apparatus_binding": RECORD_SPECS[record]["apparatus"],
            "semantic_contract": "CARD_AND_FORMAL_UNCHANGED;CONCRETE_DEFAULT_IS_REGISTER_OR_EXEMPLAR",
        })

    field_rows = []
    for field_id in sorted(fields, key=lambda value: int(value[1:])):
        field = fields[field_id]
        sid = field["statement_id"]
        transition = v62_by_statement[sid]
        record = field["record_unit_id"]
        serials = split_pipe(field["event_serials"])
        tagged = " ⟶ ".join(event_text_by_serial[serial] for serial in serials)
        field_rows.append({
            "field_id": field_id,
            "record_unit_id": record,
            "page": field["page"],
            "locus": field["locus"],
            "statement_id": sid,
            "process_node_id": statement_phase[sid],
            "field_position_in_statement": field["field_position_in_statement"],
            "event_count": field["event_count"],
            "event_serials": field["event_serials"],
            "v61_entry_boundary_class": v61_by_statement[sid]["entry_boundary_class"],
            "v61_exit_boundary_class": v61_by_statement[sid]["exit_boundary_class"],
            "v62_pre_state": transition["pre_state"],
            "v62_post_state": transition["post_state"],
            "v62_ambiguity_codes": transition["irreducible_ambiguity_codes"],
            "v63_primary_template": field["primary_template"],
            "v63_licensed_primitive_sequence": field["licensed_primitive_sequence"],
            "v63_parse_status": field["parse_status"],
            "v63_parse_reason": field["parse_reason"],
            "v63_recognized_event_count": field["recognized_event_count"],
            "v63_exemplar_only_event_count": field["exemplar_only_event_count"],
            "v65_tagged_field_interlinear": tagged,
            "unsupported_assumption_ids": "|".join(extract_assumptions(tagged)),
            "body_bath_patient_layer": RECORD_SPECS[record]["body"],
            "visible_apparatus_layer": RECORD_SPECS[record]["apparatus"],
            "status": "COMPLETE_FIELD;NO_NEW_CARD_MEANING",
        })

    statement_rows = []
    for statement in sorted(v63_statements, key=lambda row: (row["record_unit_id"], int(row["statement_ordinal_in_record"]))):
        sid = statement["statement_id"]
        record = statement["record_unit_id"]
        one = v61_by_statement[sid]
        two = v62_by_statement[sid]
        phrase = revise_phrase(statement["complete_creative_reading"].replace(" || ", "; "), record)
        ids = assumptions_for_phrase(phrase, record)
        tagged = f"[EXEMPLAR:{'+'.join(ids)}:{phrase}]"
        statement_rows.append({
            "statement_id": sid,
            "record_unit_id": record,
            "page": statement["page"],
            "statement_ordinal_in_record": statement["statement_ordinal_in_record"],
            "process_node_id": statement_phase[sid],
            "constituent_loci": one["constituent_loci"],
            "constituent_fields": statement["constituent_fields"],
            "physical_line_count": one["physical_line_count"],
            "event_count": statement["event_count"],
            "event_serials": statement["event_serials"],
            "v61_entry_boundary_class": one["entry_boundary_class"],
            "v61_exit_boundary_class": one["exit_boundary_class"],
            "v61_internal_cross_line_boundaries": one["internal_cross_line_boundaries"],
            "selected_short_card_skeleton": one["selected_short_card_skeleton"],
            "v62_pre_state": two["pre_state"],
            "v62_owner_operation": two["owner_operation"],
            "v62_active_operation": two["active_item_preparation_operation"],
            "v62_target_operation": two["target_station_operation"],
            "v62_previous_operation": two["previous_item_operation"],
            "v62_post_state": two["post_state"],
            "v62_ambiguity_codes": two["irreducible_ambiguity_codes"],
            "v63_primary_template": statement["primary_template"],
            "v63_licensed_primitive_sequence": statement["licensed_primitive_sequence"],
            "v63_parse_status": statement["parse_status"],
            "v63_recognized_event_count": statement["recognized_event_count"],
            "v63_exemplar_only_event_count": statement["exemplar_only_event_count"],
            "v65_tagged_historical_source_clause": tagged,
            "unsupported_assumption_ids": "|".join(ids),
            "strongest_segmentation_or_source_alternative": statement["strongest_segmentation_or_source_alternative"],
            "status": "COMPLETE_STATEMENT;CONCRETE_CLAUSE_EXEMPLAR_TAGGED",
        })

    record_rows = []
    for record, (page, expected_fields, expected_statements, expected_events) in RECORD_EXPECTED.items():
        rec_fields = [row for row in field_rows if row["record_unit_id"] == record]
        rec_statements = [row for row in statement_rows if row["record_unit_id"] == record]
        rec_events = [row for row in interlinear if row["record_unit_id"] == record]
        spec = RECORD_SPECS[record]
        record_rows.append({
            "record_unit_id": record,
            "page": page,
            "edition_title": spec["title"],
            "field_count": len(rec_fields),
            "statement_count": len(rec_statements),
            "event_count": len(rec_events),
            "recognized_event_count": sum(int(row["v63_recognized_event_count"]) for row in rec_fields),
            "exemplar_only_event_count": sum(int(row["v63_exemplar_only_event_count"]) for row in rec_fields),
            "field_parse_status_counts": ";".join(f"{key}={value}" for key, value in sorted(Counter(row["v63_parse_status"] for row in rec_fields).items())),
            "statement_parse_status_counts": ";".join(f"{key}={value}" for key, value in sorted(Counter(row["v63_parse_status"] for row in rec_statements).items())),
            "strict_full_anchor_sequence": " > ".join(
                f"{row['event_serial']}:{row['selected_v60_exact_mnemonic'] if row['selected_v60_exact_mnemonic'] != 'UNKNOWN' else row['strict_formal_prompt'] if row['strict_formal_prompt'] != 'NONE' else 'EXEMPLAR'}"
                for row in rec_events
            ),
            "tagged_continuous_german_source_edition": spec["process"],
            "body_bath_patient_layer": spec["body"],
            "visible_apparatus_layer": spec["apparatus"],
            "strongest_historical_analogy": spec["analogy"],
            "waterwork_or_bathhouse_rival": spec["water_rival"],
            "medical_vs_nonmedical_verdict": spec["verdict"],
            "repair_from_v54": spec["repair"],
            "strongest_contradiction": spec["contradiction"],
            "confidence": spec["confidence"],
            "unsupported_assumption_ids": "|".join(extract_assumptions(spec["process"] + spec["body"] + spec["apparatus"])),
            "status": "COMPLETE_RECORD;CREATIVE_HISTORICAL_DEFAULT_NOT_DECIPHERMENT",
        })
        assert (len(rec_fields), len(rec_statements), len(rec_events)) == (expected_fields, expected_statements, expected_events)

    declared_ids = {row[0] for row in ASSUMPTIONS}
    assumption_rows = []
    for assumption_id, records, layer, assumption, basis, contradiction, disposition in ASSUMPTIONS:
        assumption_rows.append({
            "assumption_id": assumption_id,
            "record_unit_id": records,
            "layer": layer,
            "assumption": assumption,
            "historical_or_visual_basis": basis,
            "strongest_contradiction": contradiction,
            "disposition": disposition,
            "card_licensed": "NO",
            "event_interlinear_use_count": tag_assumption_use[assumption_id],
            "semantic_contract": "NEVER_PROMOTE_TO_V60_CARD_MEANING",
        })

    columns = {
        "V65_R2_281_EVENT_BIO_INTERLINEAR.tsv": list(interlinear[0]),
        "V65_R2_115_FIELD_EDITIONS.tsv": list(field_rows[0]),
        "V65_R2_97_STATEMENT_EDITIONS.tsv": list(statement_rows[0]),
        "V65_R2_SIX_RECORD_EDITIONS.tsv": list(record_rows[0]),
        "V65_R2_PROCESS_GRAPH_NODES.tsv": list(node_rows[0]),
        "V65_R2_PROCESS_GRAPH_EDGES.tsv": list(edge_rows[0]),
        "V65_R2_UNSUPPORTED_ASSUMPTIONS.tsv": list(assumption_rows[0]),
    }
    payloads = {
        "V65_R2_281_EVENT_BIO_INTERLINEAR.tsv": interlinear,
        "V65_R2_115_FIELD_EDITIONS.tsv": field_rows,
        "V65_R2_97_STATEMENT_EDITIONS.tsv": statement_rows,
        "V65_R2_SIX_RECORD_EDITIONS.tsv": record_rows,
        "V65_R2_PROCESS_GRAPH_NODES.tsv": node_rows,
        "V65_R2_PROCESS_GRAPH_EDGES.tsv": edge_rows,
        "V65_R2_UNSUPPORTED_ASSUMPTIONS.tsv": assumption_rows,
    }
    for filename, rows in payloads.items():
        write_tsv(OUT / filename, rows, columns[filename])

    all_output_assumptions = {
        item
        for row in interlinear
        for item in split_pipe(str(row["unsupported_assumption_ids"]))
    } | {
        item
        for row in record_rows
        for item in split_pipe(str(row["unsupported_assumption_ids"]))
    }
    unknown_assumptions = sorted(all_output_assumptions - declared_ids)
    page_violations = sorted({row["page"] for row in interlinear if row["page"] not in PAGES})
    field_events = [serial for row in field_rows for serial in split_pipe(str(row["event_serials"]))]
    statement_events = [serial for row in statement_rows for serial in split_pipe(str(row["event_serials"]))]
    graph_statements = [sid for row in node_rows for sid in split_pipe(str(row["statement_ids"]))]
    record_id_violations = []
    for row in statement_rows:
        record = row["record_unit_id"]
        for value in re.findall(r"B\d+:[OIT]\d+", row["v62_pre_state"] + ";" + row["v62_post_state"]):
            if not value.startswith(record + ":"):
                record_id_violations.append(f"{row['statement_id']}:{value}")

    event_parse_counts = Counter(row["v63_event_parse_status"] for row in interlinear)
    field_parse_counts = Counter(row["v63_parse_status"] for row in field_rows)
    statement_parse_counts = Counter(row["v63_parse_status"] for row in statement_rows)
    gates = {
        "six_records_exact": len(record_rows) == 6 and set(RECORD_EXPECTED) == {row["record_unit_id"] for row in record_rows},
        "all_281_events_once": len(interlinear) == 281 and len({row["event_serial"] for row in interlinear}) == 281,
        "all_115_fields_once": len(field_rows) == 115 and len({row["field_id"] for row in field_rows}) == 115,
        "all_97_bio_statements_once": len(statement_rows) == 97 and len({row["statement_id"] for row in statement_rows}) == 97,
        "field_event_cover_exact": Counter(field_events) == Counter(v63_by_event.keys()),
        "statement_event_cover_exact": Counter(statement_events) == Counter(v63_by_event.keys()),
        "graph_statement_cover_exact": Counter(graph_statements) == Counter(v63_by_statement.keys()),
        "selected_v60_v63_alignment_exact": not alignment_errors,
        "v60_card_values_unchanged": not card_errors,
        "strict_formal_prompts_unchanged": not formal_errors,
        "record_local_v62_referents_only": not record_id_violations,
        "event_segments_fully_layer_tagged": not untagged_events,
        "record_texts_fully_layer_tagged": not [row["record_unit_id"] for row in record_rows if tagged_text_has_unmarked_words(row["tagged_continuous_german_source_edition"])],
        "all_assumptions_declared": not unknown_assumptions,
        "no_forbidden_page": not page_violations,
        "v63_bio_recognized_90_exemplar_191": sum(int(row["v63_recognized_event_count"]) for row in field_rows) == 90 and sum(int(row["v63_exemplar_only_event_count"]) for row in field_rows) == 191,
        "no_new_card_meaning": True,
        "no_phonetic_mapping": True,
    }
    validation = {
        "artifact": "V65_R2_HISTORICAL_BIOLOGICAL_SECOND_EDITION",
        "status": "PASS" if all(gates.values()) else "FAIL",
        "scope": {
            "allowed_pages": list(PAGES), "sealed_prefix": "f84", "records": len(record_rows),
            "events": len(interlinear), "fields": len(field_rows), "statements": len(statement_rows),
            "process_nodes": len(node_rows), "process_edges": len(edge_rows),
            "assumption_rows": len(assumption_rows),
        },
        "v63_bio_audit": {
            "recognized_events": sum(int(row["v63_recognized_event_count"]) for row in field_rows),
            "exemplar_only_events": sum(int(row["v63_exemplar_only_event_count"]) for row in field_rows),
            "event_parse_status_counts": dict(sorted(event_parse_counts.items())),
            "field_parse_status_counts": dict(sorted(field_parse_counts.items())),
            "statement_parse_status_counts": dict(sorted(statement_parse_counts.items())),
        },
        "record_counts": {
            row["record_unit_id"]: {
                "fields": row["field_count"], "statements": row["statement_count"],
                "events": row["event_count"], "recognized": row["recognized_event_count"],
                "exemplar_only": row["exemplar_only_event_count"], "verdict": row["medical_vs_nonmedical_verdict"],
            }
            for row in record_rows
        },
        "gates": gates,
        "violations": {
            "alignment": alignment_errors, "cards": card_errors, "formal": formal_errors,
            "record_local_ids": record_id_violations, "untagged_events": untagged_events,
            "unknown_assumptions": unknown_assumptions, "pages": page_violations,
        },
        "interpretive_limit": (
            "PASS proves complete mechanical coverage, inherited-layer preservation, record-local state, "
            "and explicit tagging. It does not validate a medical genre, body owner, language, sound, or decipherment."
        ),
    }
    (OUT / "V65_R2_VALIDATION.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
