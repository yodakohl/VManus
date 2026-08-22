#!/usr/bin/env python3
"""Build the filtration/separation workshop inventory from the selected state edition."""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_state_endpoint_completion"
DICTIONARY = SOURCE / "SELECTED_173_STATE_ENDPOINT_DICTIONARY.tsv"
INTERLINEAR = SOURCE / "SELECTED_381_STATE_ENDPOINT_INTERLINEAR.tsv"
SENTENCES = SOURCE / "SELECTED_116_STATE_ENDPOINT_SENTENCES.tsv"
OUTPUT = Path(__file__).with_name("WORKSHOP_FILTRATION_PARADIGM.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def selected(row: dict[str, str]) -> bool:
    surface = row["surface_family"]
    reading = row["concrete_word_reading_de"].lower()
    segmentation = row["semantic_segmentation"]
    explicit_neighbor = surface in {"sheey", "cheky", "cheeky", "chkeey", "chkeedy"}
    named_surface = re.search(
        r"ckh|lsh|tsh|dain|kchal|qoctholy|solkaiin|cheey|shey|cfhy|cphy", surface
    )
    filtration_reading = re.search(
        r"säubern|spül|wasch|wasser zugeben|benetz|anlegen|einwirk|einweich|"
        r"durchtränk|ruh|absetz|stehen lassen|seih|tuch|wring|klare flüss|"
        r"bis klar|auffang|verwahr|gefäß|beckenstation|auszug|flüssigkeitslauf|"
        r"flüssigkeitszulauf|beckenflüssigkeit|flüssigen anteil|zurückbehalt|"
        r"zurückhalt|hinausführ|hineinführ|einfüllstelle|auslassstelle|durchlauf|"
        r"abziehen|kühl lagern|abkühl|ablauf",
        reading,
    )
    named_component = re.search(r"CHEO_EXTRACT|AIR_FLOW|SOLK_COLLECTION", segmentation)
    return bool(explicit_neighbor or named_surface or filtration_reading or named_component)


# status, stage, decomposition, atom, default, group, substitution rule, limit
OVERRIDES: dict[str, tuple[str, str, str, str, str, str, str, str]] = {
    "2cc8bb3c2af19607888f": (
        "COMPOSITIONAL_CORE",
        "SEIHEN_AUSWRINGEN",
        "CH/SH_RENDERER+CKH_PASSAGE+Y_CURRENT",
        "CKH=DURCHLASS/SEIHWEG",
        "durch den verbundenen Seihweg",
        "CKH_PASSAGE_GRID",
        "Offene Wegkarte; noch kein Seihschluss.",
        "Nur diese exakte Rendererfamilie trägt den verbundenen Durchlauf.",
    ),
    "d68bc8de3bcee09db23c": (
        "COMPOSITIONAL_CORE",
        "SEIHEN_AUSWRINGEN",
        "SH_CLOTH_HULL+CKH_PASSAGE+E_DIRECT+DY_CLOSE",
        "CKH=DURCHLASS; E=EINMAL; DY=SCHLUSS",
        "einmal durch Tuch seihen; Schluss",
        "CKH_PASSAGE_GRID",
        "Direkter Tuchpass mit Abschluss.",
        "SH ist hier eine gelernte Tuchhülle, nicht die allgemeine SHED-Ruhekarte.",
    ),
    "c1db6b0a28d5cbb5d3d2": (
        "COMPOSITIONAL_CORE",
        "SEIHEN_AUSWRINGEN",
        "LCHE_CLEAR_OUTLET_HULL+CKH_PASSAGE+E_DIRECT+DY_CLOSE",
        "CKH=DURCHLASS; E=EINMAL; DY=SCHLUSS",
        "zum Klarlauf seihen; Schluss",
        "CKH_PASSAGE_GRID",
        "Klarlauf-Ausgang statt gewöhnlichem Tuchpass.",
        "Die LCHE-Hülle ist nur durch dieses Paar mit lcheckhy gestützt.",
    ),
    "f329f2051370174e9a38": (
        "LEARNED_HULL",
        "SEIHEN_AUSWRINGEN",
        "LCHE_CLEAR_OUTLET_HULL+CKH_PASSAGE+Y_CURRENT",
        "LCHE+CKH=ZWEITER SIEBAUSLASS",
        "zweiter Siebauslass",
        "CKH_PASSAGE_GRID",
        "Offene Schwester des terminalen Klarseihens.",
        "Ein Ereignis; zweite Öffnung bleibt die stärkste neutrale Gegenlesung.",
    ),
    "21ed2873b71e57269c08": (
        "LEARNED_HULL",
        "SEIHEN_AUSWRINGEN",
        "CKHAL_FLOW_SETTING",
        "CKHAL=DURCHLAUFVORGABE",
        "Durchlaufzeit",
        "CKH_FLOW_SETTING",
        "Zeitvorgabe für den Seih- oder Sammellauf.",
        "Ein Ereignis; der alte Ganzwortwert Dauer bleibt als Rivale vollständig möglich.",
    ),
    "4eab1841ed655c20a348": (
        "LEARNED_HULL",
        "SEIHEN_AUSWRINGEN",
        "SHE_CKHAL_FLOW_SETTING",
        "CKHAL=DURCHLAUFVORGABE",
        "mäßiger Durchsatz",
        "CKH_FLOW_SETTING",
        "Mengen- oder Durchsatzeinstellung, kein Seihschluss.",
        "Ein Ereignis; mäßige Menge bleibt die stärkste Gegenlesung.",
    ),
    "ecce30bc8dcc400bf2c8": (
        "LOOKALIKE_WHOLE_CARD",
        "POSITIONIERUNG",
        "QOCKHEY_WHOLE",
        "GELERNTE STELLENKARTE",
        "über der Stelle",
        "CKH_BOUNDARIES",
        "Nicht gegen eine Seihkarte austauschbar.",
        "Die O-Hülle sperrt die freie CKH-Zerlegung.",
    ),
    "c1913ec4ff84148da6d3": (
        "LOOKALIKE_WHOLE_CARD",
        "POSITIONIERUNG",
        "SHECKHY_WHOLE",
        "GELERNTE STELLENKARTE",
        "über der Stelle",
        "CKH_BOUNDARIES",
        "Nicht gegen eine Seihkarte austauschbar.",
        "Exakte Kartenidentität schlägt die CKH-Substringähnlichkeit.",
    ),
    "95987d6f198d6d247511": (
        "LOOKALIKE_WHOLE_CARD",
        "ANWENDUNG",
        "CHEECKHO_APPLICATION+DY_CLOSE",
        "CHEECKHO=ÄUSSERLICH ANWENDEN",
        "äußerlich anwenden; Schluss",
        "CKH_BOUNDARIES",
        "Kein Filtrationsschritt.",
        "Der Innenstring ähnelt CKH, die exakte Karte gehört aber zur äußeren Anwendung.",
    ),
    "bdad9f9ea8b80f141496": (
        "LEARNED_OPERATOR",
        "SEIHEN_AUSWRINGEN",
        "CFHY_WHOLE",
        "CFHY=AUSWRINGEN",
        "durch Tuch auswringen",
        "HERBAL_DOUBLE_SEPARATION",
        "Erster mechanischer Trennschritt vor der Stehzeit.",
        "Ein Ereignis; nicht als produktives F- oder HY-Morphem behandeln.",
    ),
    "deb377381ceaf55ea310": (
        "LEARNED_OPERATOR",
        "SEIHEN_AUSWRINGEN",
        "CPHY_WHOLE",
        "CPHY=NACHSEIHEN",
        "nochmals seihen",
        "HERBAL_DOUBLE_SEPARATION",
        "Zweiter Trennschritt nach der Stehzeit; kein Synonym von CFHY.",
        "Ein Ereignis; die Reihenfolge CFHY vor CPHY ist Teil der gelernten Passage.",
    ),
    "be0974b366c981dc1eef": (
        "COMPOSITIONAL_CORE",
        "WASCHEN_BENETZEN",
        "LSH_WASH+O_START",
        "LSH=WASCHEN/SPÜLEN",
        "Spülgang beginnen",
        "WASH_START",
        "Kann im Startslot durch TSHEY vertreten werden; O ist nur hier Startform.",
        "O bedeutet nicht global beginnen.",
    ),
    "2e7e89e0bd12b999c280": (
        "COMPOSITIONAL_CORE",
        "WASCHEN_BENETZEN",
        "LSH_WASH+E_DIRECT+DY_CLOSE",
        "LSH=WASCHEN; E=EINMAL; DY=SCHLUSS",
        "einmal waschen; Schluss",
        "WASH_CLOSE",
        "Geschlossene Waschkarte nach LSHO oder einer lokalen Vorbereitung.",
        "Zwei Ereignisse; nicht mit der SHED-Ruhefamilie zusammenziehen.",
    ),
    "d4a31dbcf1ed6d9e5aa9": (
        "LEARNED_OPERATOR",
        "WASCHEN_BENETZEN",
        "TSHEY_WHOLE",
        "TSHEY=SPÜLGANG BEGINNEN",
        "Spülgang beginnen",
        "WASH_START",
        "Gleicher praktischer Slot wie LSHO, aber keine gemeinsame sichtbare Wurzel.",
        "Ein Ereignis; TSHOL ist ausdrücklich keine Spülkarte.",
    ),
    "953ad19b79517fc8a211": (
        "LOOKALIKE_WHOLE_CARD",
        "PFLANZENMATERIAL",
        "TSHOL_WHOLE",
        "GELERNTES PFLANZENWORT",
        "Blütenkraut",
        "LSH_TSH_BOUNDARIES",
        "Nicht gegen LSHO oder TSHEY austauschbar.",
        "Die TSH-Schreibung allein trägt keine Waschbedeutung.",
    ),
    "b5df9126607030b95175": (
        "LEARNED_STATE_CARD",
        "KLARE_FLUESSIGKEIT",
        "CHEEY_SHEY_CLEAR_RUN_CARD",
        "CHEEY/SHEY=KLARLAUF",
        "Klarlauf; klare Flüssigkeit",
        "CLEAR_RUN",
        "Rendererformen derselben exakten Karte; Ergebnis-/Prüfslot nach Trennung.",
        "Nennt den klaren Flüssigkeitsposten, nicht die ganze Anweisung warten bis klar.",
    ),
    "92e43836d82f98bf02d3": (
        "LOOKALIKE_WHOLE_CARD",
        "OEFFNUNG",
        "SHEEY_WHOLE",
        "GELERNTE ÖFFNUNGSKARTE",
        "erste Öffnung",
        "CHEEY_BOUNDARIES",
        "Nicht gegen CHEEY/SHEY = Klarlauf austauschbar.",
        "Das zusätzliche e ändert die exakte Karte.",
    ),
    "5fca8fc3dee57e1d8c1f": (
        "LEARNED_RESULT_CARD",
        "WASCHEN_BENETZEN",
        "LCHEEY_WHOLE",
        "LCHEEY=BENETZTE STELLE",
        "benetzte Stelle",
        "WET_RESULT",
        "Ergebnis-/Zielkarte, keine klare Flüssigkeit.",
        "Der längere Anlaut sperrt die CHEEY-Klarlauflesung.",
    ),
    "d72f71baff01cd0a0406": (
        "COMPOSITIONAL_LEARNED_CORE",
        "RUHEN_ABSETZEN",
        "CHLD_SETTLING_LEVEL+AIIN_MEASURE",
        "CHLD=ABSETZSTAND; AIIN=MASS",
        "auf Sollstand absetzen",
        "SETTLING_CONTROL",
        "Standvorgabe, nicht Tuch- oder DAIN-Karte.",
        "Ein Ereignis; CHLD bleibt ein gelernter Kern.",
    ),
    "a8af08e69edab8e54f15": (
        "COMPOSITIONAL_LEARNED_CORE",
        "RUHEN_ABSETZEN",
        "SHFY_STAND_TIME+AIIN_MEASURE",
        "SHFY=STEHZEIT; AIIN=MASS",
        "vorgeschriebene Stehzeit",
        "SETTLING_CONTROL",
        "Zeitvorgabe zwischen Auswringen und Nachseihen.",
        "Ein Ereignis; weder PHY noch DAIN wird daraus frei abgeleitet.",
    ),
    "d788d8d72d41b25a3c71": (
        "LEARNED_STATE_CARD",
        "KLARE_FLUESSIGKEIT",
        "CHEALROR_CLEAR_LIMIT",
        "CHEALROR=KLARGRENZE",
        "bis klar",
        "CLEAR_RUN",
        "Endpunktbedingung vor der Auffangstation.",
        "Ein Ereignis; kein allgemeines ROR-Komponent wird gesetzt.",
    ),
    "342c3f0777337648f4b3": (
        "LEARNED_STATION_CARD",
        "AUFFANGEN_AUFBEWAHREN",
        "CHEEDAR_BASIN_STATION",
        "CHEEDAR=BECKENSTATION",
        "Beckenstation",
        "COLLECTION_STATION",
        "Richtet den lokalen Sammelplatz ein.",
        "Ein Ereignis; nicht aus AR=Quelle komponieren.",
    ),
    "62ff059766b21c7de083": (
        "LEARNED_OPERATOR",
        "AUFFANGEN_AUFBEWAHREN",
        "OTYTCHOL_FIRST_EXTRACT_CATCH",
        "OTYTCHOL=ERSTAUSZUG AUFFANGEN",
        "Erstauszug auffangen",
        "CATCH_STORE_OPERATORS",
        "Auffanghandlung, nicht bloß Gefäßname.",
        "Ein Ereignis; die innere OL-Ähnlichkeit wird nicht semantisiert.",
    ),
    "e026af581c99322fbd46": (
        "LEARNED_OPERATOR",
        "AUFFANGEN_AUFBEWAHREN",
        "TALAM_EXTRACT_STORE",
        "TALAM=AUSZUG VERWAHREN",
        "Auszug verwahren",
        "CATCH_STORE_OPERATORS",
        "Aufbewahrung nach der Bearbeitung; kein Synonym von auffangen.",
        "Ein Ereignis; gelernte Ganzkarte.",
    ),
}


CLOTH_ROUTE_IDS = {
    "53cd0637c6820ba5e91f",
    "75a523fcf039b006f97b",
    "af816c04e65874a0f2fa",
    "2d2e37ccb2dacc53ee5a",
}
VESSEL_FILL_IDS = {
    "b38d70daefd663d74625",
    "e2eb77ca9d9e1a8ba29a",
    "a7af89ab31ce5e247395",
}
CHK_IDS = {
    "d904bf7b044dd3922781",
    "2c1a5fd92b9e3c762242",
    "f0db6d30cd34f4cb2a4d",
    "a84fbe3ad380df345b97",
}


def generic(row: dict[str, str]) -> tuple[str, str, str, str, str, str, str, str]:
    card = row["joint_tuple_id"]
    seg = row["semantic_segmentation"]
    reading = row["concrete_word_reading_de"]
    low = reading.lower()
    if card in CLOTH_ROUTE_IDS:
        return (
            "LEARNED_EQUIVALENT_CARD",
            "SEIHEN_AUSWRINGEN",
            "OPAQUE_CLOTH_ROUTE_CARD",
            "GANZKARTE=DURCH TUCH",
            "durch Tuch",
            "CLOTH_ROUTE_EQUIVALENTS",
            "Gleicher Instrument-/Wegslot; die vier Karten haben keine gemeinsame sichtbare Wurzel.",
            "DAIN bleibt insbesondere von AIIN=Maß getrennt.",
        )
    if card in VESSEL_FILL_IDS:
        return (
            "LEARNED_EQUIVALENT_CARD",
            "AUFFANGEN_AUFBEWAHREN",
            seg,
            "GANZKARTE=GEFÄSS FÜLLEN",
            "Gefäß füllen",
            "VESSEL_FILL_EQUIVALENTS",
            "Gleicher Füllslot; Oberfläche bleibt registerlokal gelernt.",
            "Keine gemeinsame sichtbare Füllwurzel wird erfunden.",
        )
    if card in CHK_IDS:
        grade = "E=kurz" if "GRADE_1" in seg else "EE=anhaltend"
        close = "DY=Schluss" if "DY_CLOSE" in seg else "Y=dies/offen"
        return (
            "LETTER_ORDER_CONTROL",
            "VORWAERMEN",
            seg,
            f"CHK=WÄRMEN; {grade}; {close}",
            reading,
            "CHK_WARM_GRID",
            "Kann vor dem Seihen stehen, ist aber keine CKH-Durchlasskarte.",
            "Buchstabenfolge CHK und CKH nicht vertauschen.",
        )

    if re.search(r"qokedy|qokeedy|qokeeedy|okey|okeey", row["surface_family"]) or (
        "GRADE_" in seg and ("OK" in seg or "OT" in seg)
    ):
        return (
            "GRADED_COMPONENT_CARD",
            "WASCHEN_BENETZEN",
            seg,
            "OK=ANSETZEN; E/EE/EEE=KURZ/LÄNGER/GANZ; Y/DY=REFERENZ/SCHLUSS",
            reading,
            "OK_CONTACT_GRID",
            "Gradvarianten, keine freien Synonyme.",
            "Die konkrete Handlung reicht von Anlegen bis Einweichen; der Grad bleibt invariant.",
        )
    if "SHED_REST" in seg or "ruhen" in low or "absetzen" in low:
        return (
            "GRADED_COMPONENT_CARD" if "SHED_REST" in seg else "LEARNED_OPERATOR",
            "RUHEN_ABSETZEN",
            seg,
            "SHED=RUHEN/ABSETZEN",
            reading,
            "REST_SETTLE_GRID",
            "Kurze/lange/örtliche Varianten derselben Ruhephase, soweit die exakte Karte lizenziert.",
            "Nicht jedes sichtbare shed gehört zur Ruhefamilie.",
        )
    if "SOLK_COLLECTION" in seg or "OLK_SOLK_COLLECTION" in seg:
        return (
            "GRADED_COMPONENT_CARD",
            "AUFFANGEN_AUFBEWAHREN",
            seg,
            "SOLK=AUFFANGSTELLE; E/EE=KURZ/LÄNGER; Y/DY=REFERENZ/SCHLUSS",
            reading,
            "SOLK_COLLECTION_GRID",
            "Dauer- und Schlussvarianten am Auffangplatz.",
            "SOLK ist nur in dieser lokalen exakten Familie Auffangstelle.",
        )
    if "AIR_FLOW" in seg:
        return (
            "COMPOSITIONAL_CORE",
            "KLARE_FLUESSIGKEIT",
            seg,
            "AIR=FLÜSSIGKEIT IM LAUF",
            reading,
            "LIQUID_FLOW_GRID",
            "Zulauf, Beckenlauf, Aktivierung, Durchführung oder Schluss desselben Flusskerns.",
            "AIR behauptet weder reines Wasser noch einen bloßen gezeichneten Pfeil.",
        )
    if "CHEO_EXTRACT" in seg:
        return (
            "COMPOSITIONAL_LEARNED_CORE",
            "KLARE_FLUESSIGKEIT",
            seg,
            "CHEO=AUSZUGSFLÜSSIGKEIT",
            reading,
            "EXTRACT_LIQUID_GRID",
            "Quelle oder Zugabe derselben Auszugsflüssigkeit.",
            "Die Flüssigkeitsart bleibt offen; kein Wasser-, Öl- oder Weinzwang.",
        )
    if "hinaus" in low or "auslass" in low or "ablauf" in low or "abziehen" in low:
        return (
            "TRANSFER_SUPPORT_CARD",
            "SEIHEN_AUSWRINGEN",
            seg,
            "L/AB=FLÜSSIGEN POSTEN HINAUSFÜHREN",
            reading,
            "OUTFLOW_TRANSFER",
            "Abzug/Auslass nach Trennung; nicht selbst der Seihvorgang.",
            "Lokale Ganzkarten und die lizenzierte L+CHED-Familie bleiben getrennt.",
        )
    if "hinein" in low or "einfüll" in low:
        return (
            "TRANSFER_SUPPORT_CARD",
            "AUFFANGEN_AUFBEWAHREN",
            seg,
            "P+CHED=HINEINFÜHREN",
            reading,
            "INFLOW_TRANSFER",
            "Einfüllweg; Gegenstück zum Auslass.",
            "Nur in der exakten P+CHED-Familie produktiv.",
        )
    if "gefäß" in low:
        return (
            "LEARNED_VESSEL_CARD",
            "AUFFANGEN_AUFBEWAHREN",
            seg,
            "GELERNTER GEFÄSSWERT",
            reading,
            "VESSEL_TYPES",
            "Empfängerwahl oder Füllhandlung, keine Seihoperation.",
            "Breit, glasiert und neutral bleiben verschiedene Ganzkarten.",
        )
    if (
        "wasch" in low
        or "spül" in low
        or "benetz" in low
        or "einweich" in low
        or "durchtränk" in low
        or "säubern" in low
        or "wasser zugeben" in low
    ):
        return (
            "LEARNED_WASH_CARD",
            "WASCHEN_BENETZEN",
            seg,
            "GELERNTE WASCH-/BENETZKARTE",
            reading,
            "WASH_CLOSE",
            "Konkrete Waschstufe; nur bei ausgewiesenem DY terminal.",
            "Ähnliche SHED-Schreibung kann Ruhe statt Waschen tragen.",
        )
    if "zurückbehalt" in low or "zurückhalt" in low:
        return (
            "LEARNED_RESIDUE_CARD",
            "SEIHEN_AUSWRINGEN",
            seg,
            "GELERNTER RÜCKSTANDSWERT",
            reading,
            "SEPARATION_RESIDUE",
            "Bezeichnet den zurückbleibenden Feststoff, nicht den Klarlauf.",
            "Die konkrete Pflanzenteilart bleibt in der Ganzkarte.",
        )
    if "klar" in low:
        return (
            "LEARNED_STATE_CARD",
            "KLARE_FLUESSIGKEIT",
            seg,
            "GELERNTER KLARLAUFWERT",
            reading,
            "CLEAR_RUN",
            "Klarzustand oder Klarlauf, keine mechanische Trennhandlung.",
            "Der lokale Satz liefert warten, prüfen oder erreichen; die Karte selbst bleibt kurz.",
        )
    if "seih" in low or "tuch" in low or "wring" in low or "durchlauf" in low:
        return (
            "LEARNED_SEPARATION_CARD",
            "SEIHEN_AUSWRINGEN",
            seg,
            "GELERNTE TRENNKARTE",
            reading,
            "SEPARATION_MISC",
            "Lokale Trennhandlung oder Wegkarte.",
            "Keine zusätzliche sichtbare Wurzel wird ohne Paarbeleg gesetzt.",
        )
    if "auffang" in low or "verwahr" in low or "beckenstation" in low or "kühl lagern" in low:
        return (
            "LEARNED_COLLECTION_CARD",
            "AUFFANGEN_AUFBEWAHREN",
            seg,
            "GELERNTER AUFFANG-/LAGERWERT",
            reading,
            "CATCH_STORE_OPERATORS",
            "Empfangen, halten oder lagern sind aufeinanderfolgende, nicht synonyme Rollen.",
            "Die exakte Karte bestimmt die konkrete Rolle.",
        )
    if "abkühl" in low:
        return (
            "LEARNED_COOLING_CARD",
            "AUFFANGEN_AUFBEWAHREN",
            seg,
            "GELERNTER KÜHLWERT",
            reading,
            "COOL_STORE",
            "Kühlen vor oder nach Lagerung; nur DY-Karten schließen.",
            "Kein allgemeines Temperaturmorphem wird aus der Oberfläche gezogen.",
        )
    return (
        "SUPPORTING_WHOLE_CARD",
        "TRENNKETTE_NEBENKARTE",
        seg,
        "GELERNTER KONKRETER GANZKARTENWERT",
        reading,
        "BOUNDARY_CONTROLS",
        "Nicht frei substituierbar.",
        "Diese Karte bleibt konkret, verhindert aber eine zu breite Substringregel.",
    )


def rival(row: dict[str, str], status: str) -> str:
    surface = row["surface_family"]
    if "CKH" in row["semantic_segmentation"] or "ckh" in surface:
        return "jede CKH-Schreibung als dasselbe Seihwort lesen"
    if "SHED" in row["semantic_segmentation"] or "shed" in surface:
        return "Waschen, Ruhen und sauberes Wasser wegen sichtbarem SHED zusammenziehen"
    if "dain" in surface or "daiin" in surface:
        return "DAIN, AIIN und IIN nach bloßer Endschrift gleichsetzen"
    if status == "LEARNED_EQUIVALENT_CARD":
        return "eine gemeinsame sichtbare Wurzel für funktional gleiche Ganzkarten erfinden"
    return "den gesamten lokalen Satz als angebliche Wortbedeutung speichern"


def consequence(stage: str, default: str) -> str:
    return {
        "WASCHEN_BENETZEN": f"Reinigungsphase: {default}.",
        "RUHEN_ABSETZEN": f"Ruhephase: {default}.",
        "SEIHEN_AUSWRINGEN": f"Trennphase: {default}.",
        "KLARE_FLUESSIGKEIT": f"Flüssigkeits-/Klarlaufphase: {default}.",
        "AUFFANGEN_AUFBEWAHREN": f"Empfangs-/Lagerphase: {default}.",
    }.get(stage, f"Nebenkarte unverändert konkret lesen: {default}.")


def main() -> None:
    dictionary = [row for row in read_tsv(DICTIONARY) if selected(row)]
    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in read_tsv(INTERLINEAR):
        events_by_card[event["joint_tuple_id"]].append(event)
    sentences = {row["statement_id"]: row for row in read_tsv(SENTENCES)}

    fields = [
        "stage",
        "card_status",
        "joint_tuple_id",
        "surface_family",
        "occurrences",
        "event_ids",
        "statement_ids",
        "pages",
        "selected_decomposition",
        "atomic_contribution_de",
        "concrete_default_de",
        "substitution_group",
        "substitution_rule_de",
        "event_contexts_de",
        "complete_passages_de",
        "strongest_rival_de",
        "contradiction_or_limit_de",
        "passage_consequence_de",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        order = {
            "WASCHEN_BENETZEN": 1,
            "RUHEN_ABSETZEN": 2,
            "SEIHEN_AUSWRINGEN": 3,
            "KLARE_FLUESSIGKEIT": 4,
            "AUFFANGEN_AUFBEWAHREN": 5,
        }
        prepared = []
        for row in dictionary:
            card = row["joint_tuple_id"]
            data = OVERRIDES.get(card, generic(row))
            prepared.append((order.get(data[1], 9), row["surface_family"], row, data))
        for _, _, row, data in sorted(prepared):
            status, stage, decomposition, atom, default, group, rule, limit = data
            events = events_by_card[row["joint_tuple_id"]]
            contexts: dict[str, list[str]] = defaultdict(list)
            for event in events:
                contexts[event["contextual_event_reading_de"]].append(event["event_id"])
            context_text = " | ".join(
                f"{','.join(ids)}={context}" for context, ids in contexts.items()
            )
            statement_ids = list(dict.fromkeys(event["statement_id"] for event in events))
            passages = " | ".join(
                f"{statement_id}={sentences[statement_id]['surface_sequence']} :: "
                f"{sentences[statement_id]['workshop_sentence_de']}"
                for statement_id in statement_ids
            )
            writer.writerow(
                {
                    "stage": stage,
                    "card_status": status,
                    "joint_tuple_id": row["joint_tuple_id"],
                    "surface_family": row["surface_family"],
                    "occurrences": row["occurrences"],
                    "event_ids": "|".join(event["event_id"] for event in events),
                    "statement_ids": "|".join(statement_ids),
                    "pages": "|".join(dict.fromkeys(event["page"] for event in events)),
                    "selected_decomposition": decomposition,
                    "atomic_contribution_de": atom,
                    "concrete_default_de": default,
                    "substitution_group": group,
                    "substitution_rule_de": rule,
                    "event_contexts_de": context_text,
                    "complete_passages_de": passages,
                    "strongest_rival_de": rival(row, status),
                    "contradiction_or_limit_de": limit,
                    "passage_consequence_de": consequence(stage, default),
                }
            )


if __name__ == "__main__":
    main()
