#!/usr/bin/env python3
"""Build the compact state/grade teaching inventory from the selected ten-page edition."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_quantity_preparation"
DICTIONARY = SOURCE / "SELECTED_173_QUANTITY_PREPARATION_DICTIONARY.tsv"
INTERLINEAR = SOURCE / "SELECTED_381_QUANTITY_PREPARATION_INTERLINEAR.tsv"
OUTPUT = Path(__file__).with_name("STATE_GRADE_PARADIGM.tsv")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def selected(row: dict[str, str]) -> bool:
    seg = row["semantic_segmentation"]
    surf = row["surface_family"]
    named = (
        "IIN_GRADE",
        "E_GRADE_1",
        "E_GRADE_2",
        "E_GRADE_3",
        "CTH_READY",
        "SHED_REST",
        "SH_REST",
        "CHK_WARMTH",
        "SOLK_COLLECTION",
        "OLK~SOLK",
        "Y_REFERENT",
        "DY_TERMINAL",
        "TERMINAL_Y",
    )
    surface_neighbors = (
        "cth",
        "shed",
        "sheed",
        "tedy",
        "chek",
        "cheek",
        "chck",
        "chk",
        "solk",
        "olk",
    )
    explicit_grade = any(f"+{g}+" in f"+{seg}+" for g in ("E", "EE", "EEE"))
    return any(token in seg for token in named) or explicit_grade or any(
        token in surf for token in surface_neighbors
    )


OVERRIDES: dict[str, tuple[str, str, str, str, str, str, str]] = {
    # status, decomposition, core, grade, endpoint, default, limit
    "2c82523794dcb7d2b343": (
        "GRADE_NAMER",
        "IIN_GRADE",
        "IIN=STUFE/GRAD",
        "NAMED",
        "—",
        "vorgeschriebene Stufe",
        "Nennt eine Einstellung, aber keine Zahl und keine Zeiteinheit.",
    ),
    "fcc1deda9e24ec268eb0": (
        "GRADE_NAMER",
        "DA_OPENING+IIN_GRADE",
        "DA=ÖFFNUNG; IIN=STUFE",
        "NAMED",
        "—",
        "zweite Öffnungsstufe",
        "Ein Einzelbeleg; die Ordnungszahl bleibt als gelernter DA-Rahmen lokal.",
    ),
    "409de02322e7b2ca0c62": (
        "GRADE_NAMER",
        "K_SOFT+IIN_GRADE",
        "K=WEICH; IIN=STUFE",
        "NAMED",
        "—",
        "Weichstufe",
        "Ein Einzelbeleg; weich ist hier eine Zustandsstufe, keine allgemeine K-Bedeutung.",
    ),
    "e0b630cb1b5df5e7105b": (
        "CORE_BASE",
        "CTH_READY+Y_REFERENT (gelernte Rendererfamilie)",
        "CTH=BEREIT",
        "0",
        "Y=dies",
        "bereit; diesen Posten als bereit behandeln",
        "CTH ist nur in dieser exakten Familie bereit; cthoor und cthaiin bleiben eigene Karten.",
    ),
    "6b89d6dd70635bc60fe0": (
        "MATRIX_CELL",
        "CTH_READY+E_GRADE_1+Y_REFERENT",
        "CTH=BEREIT",
        "E=kurz/direkt halten",
        "Y=dies",
        "diesen Posten bereit halten",
        "Nur zwei Ereignisse und kein CTH+DY-Gegenstück.",
    ),
    "d904bf7b044dd3922781": (
        "MATRIX_CELL_WITH_LOCAL_ENDING",
        "CHK_WARMTH+E_GRADE_1+KY_HEAT_ENDING",
        "CHK=ERWÄRMEN",
        "E=kurz/mild",
        "KY=gelernte Wärmeform",
        "kurz oder mild erwärmen",
        "KY ist ausdrücklich nicht das freie Y-Referenzzeichen.",
    ),
    "2c1a5fd92b9e3c762242": (
        "MATRIX_CELL_WITH_LOCAL_ENDING",
        "CHK_WARMTH+E_GRADE_2+KY_HEAT_ENDING",
        "CHK=ERWÄRMEN",
        "EE=anhaltend",
        "KY=gelernte Wärmeform",
        "länger warm halten",
        "KY ist ausdrücklich nicht das freie Y-Referenzzeichen.",
    ),
    "42cdc187d5b9ffc60063": (
        "MATRIX_CELL",
        "SOLK_COLLECTION_STATION+E_GRADE_1+Y_REFERENT",
        "SOLK=SAMMELSTELLE",
        "E=kurz",
        "Y=diese",
        "diese Sammelstelle kurz offen halten",
        "Ein Ereignis; offen ist die konkrete Stationshandlung, nicht die globale Bedeutung von Y.",
    ),
    "1bfd786e6b8b63734a59": (
        "MATRIX_CELL",
        "SOLK_COLLECTION_STATION+E_GRADE_2+Y_REFERENT",
        "SOLK=SAMMELSTELLE",
        "EE=anhaltend",
        "Y=diese",
        "diese Sammelstelle länger offen halten",
        "Ein Ereignis; die SOLK-Bedeutung ist lokal, nicht aus jeder olk-Schreibung ableitbar.",
    ),
    "3b70942557b3a40e8030": (
        "MATRIX_CELL",
        "SOLK_COLLECTION_STATION+E_GRADE_2+DY_TERMINAL",
        "SOLK=SAMMELSTELLE",
        "EE=anhaltend",
        "DY=Schritt schließen",
        "an der Sammelstelle stehen oder absetzen lassen; Schritt schließen",
        "Die drei Ereignisse stützen die Endform, aber nicht eine allgemeine SOLK-Wortwurzel außerhalb dieser Familie.",
    ),
    "bc4f1f5c006c74a4d26d": (
        "MATRIX_CELL",
        "SH_REST+E_GRADE_1+DY_TERMINAL",
        "SH=RUHEN/ABSETZEN",
        "E=kurz/gewöhnlich",
        "DY=Schritt schließen",
        "kurz oder gewöhnlich ruhen lassen; Schritt schließen",
        "Rendererformen cheedy/shedy/tedy teilen hier eine Karte; nicht jedes sichtbare shed gehört dazu.",
    ),
    "03626ca94cb17800d767": (
        "MATRIX_CELL",
        "SH_REST+E_GRADE_2+DY_TERMINAL",
        "SH=RUHEN/ABSETZEN",
        "EE=anhaltend",
        "DY=Schritt schließen",
        "länger ruhen oder nachwirken lassen; Schritt schließen",
        "Nur ein Ereignis, aber als längere Schwester der zwölf E-DY-Ereignisse lehrbar.",
    ),
    "abb23e5e6936b4147f76": (
        "CORE_DESTINATION",
        "SHED_REST+AL_TARGET",
        "SHED=RUHE/ABSETZEN",
        "0",
        "AL=Zielstelle",
        "Ruhe- oder Absetzstelle",
        "Nomenhafte Zielkarte, kein Zeitgrad und kein Abschluss.",
    ),
    "db167f8e9b53eefb58f8": (
        "PRODUCTIVE_ENDPOINT",
        "OK+SHED_REST+DY_TERMINAL",
        "SHED=RUHEN/ABSETZEN",
        "0",
        "DY=Schritt schließen",
        "Ansatz zur Ruhe bringen oder absetzen lassen; Schritt schließen",
        "Ein Ereignis; OK setzt den Ansatz in die gelernte Ruhehandlung.",
    ),
    "b921a237be883a820352": (
        "Y_REFERENCE",
        "Y_REFERENT_CARD (Rendererfamilie)",
        "—",
        "—",
        "Y=dies/es",
        "der laufende Posten; dies oder es",
        "Die sichtbare Form dy kann hier reine Y-Karte sein; Oberfläche allein entscheidet nie über Abschluss.",
    ),
    "7db18b2f0fb7ed0fcfd3": (
        "MATRIX_CELL",
        "OK+E_GRADE_1+DY_TERMINAL",
        "OK=IN ARBEIT SETZEN",
        "E=kurz/direkt",
        "DY=Schritt schließen",
        "kurz benetzen oder spülen; Schritt schließen",
        "E bezeichnet einen geordneten Kontaktgrad, keine feste Minutenangabe.",
    ),
    "7d25241b0e56c836372a": (
        "MATRIX_CELL",
        "OK+E_GRADE_2+DY_TERMINAL",
        "OK=IN ARBEIT SETZEN",
        "EE=anhaltend",
        "DY=Schritt schließen",
        "eintauchen oder einweichen; Schritt schließen",
        "Die konkrete deutsche Handlung ist kontextuell; invariant ist der anhaltende Kontakt mit Abschluss.",
    ),
    "d25110e0d8488927278f": (
        "MATRIX_CELL",
        "OK+E_GRADE_3+DY_TERMINAL",
        "OK=IN ARBEIT SETZEN",
        "EEE=vollständig/durchgehend",
        "DY=Schritt schließen",
        "vollständig durchtränken; Schritt schließen",
        "Nur ein EEE-Ereignis; es stützt die Ordnung, nicht die Häufigkeit des Grades.",
    ),
    "08bd5ca0c2ad137a056d": (
        "MATRIX_CELL",
        "OK+E_GRADE_1+Y_REFERENT",
        "OK=IN ARBEIT SETZEN",
        "E=kurz/direkt",
        "Y=dies",
        "diesen Posten kurz anlegen oder benetzen",
        "Y hält den Referenten fest; es bedeutet nicht selbst offen.",
    ),
    "0275fbf14e07935b0a45": (
        "MATRIX_CELL",
        "OK+E_GRADE_2+Y_REFERENT",
        "OK=IN ARBEIT SETZEN",
        "EE=anhaltend",
        "Y=dies",
        "diesen Posten anhaltend in Kontakt halten",
        "Kein EEE+Y-Beleg; die Matrix darf diese Zelle nicht erfinden.",
    ),
    "c45ebac60774620561e2": (
        "MATRIX_CELL",
        "OT_THEN+E_GRADE_1+DY_TERMINAL",
        "OT=DANACH",
        "E=kurz/gewöhnlich",
        "DY=Schritt schließen",
        "danach kurz einwirken lassen; Schritt schließen",
        "OT ist ein Reihenfolgenrahmen; die konkrete Einwirkung kommt aus der Konstruktion.",
    ),
    "5d5e0b288cf36864ed9d": (
        "MATRIX_CELL",
        "OT_THEN+E_GRADE_2+Y_REFERENT",
        "OT=DANACH",
        "EE=anhaltend",
        "Y=dies",
        "diesen Posten danach anhaltend einwirken lassen",
        "Zwei Ereignisse, kein eigenes Abschlusszeichen.",
    ),
    "ff178343c18e287ce3b7": (
        "MATRIX_CELL",
        "OT_THEN+E_GRADE_2+DY_TERMINAL",
        "OT=DANACH",
        "EE=anhaltend",
        "DY=Schritt schließen",
        "danach anhaltend einwirken lassen; Schritt schließen",
        "Zwei Ereignisse; die Paarung mit OT+EE+Y stützt die Endpunktdifferenz.",
    ),
    "daf32e6db9e04413ce7f": (
        "GRADE_WITH_OTHER_ENDPOINT",
        "OK+E_GRADE_2+OL_CONTINUATION",
        "OK=IN ARBEIT SETZEN",
        "EE=anhaltend",
        "OL=mit Vorigem weiter",
        "mit dem Vorigen anhaltend in Kontakt weiterführen",
        "Ein Ereignis; zeigt, dass nach dem Grad auch OL statt Y/DY stehen kann.",
    ),
    "93f69c38fdedee1598e9": (
        "GRADE_WITH_OTHER_ENDPOINT",
        "OK+E_GRADE_2+AL_TARGET",
        "OK=IN ARBEIT SETZEN",
        "EE=anhaltend",
        "AL=Zielstelle",
        "an der Zielstelle anhaltend in Kontakt halten",
        "Ein Ereignis; zeigt eine Zielstelle statt Referenz oder Abschluss.",
    ),
    "eb2e4bc143f623ee03ac": (
        "PRODUCTIVE_ENDPOINT",
        "OK+Y_REFERENT+LDDY_APPLICATION_CLOSE",
        "OK=IN ARBEIT SETZEN; LDDY=AUFLAGE BEFESTIGEN",
        "0",
        "LDDY=Auflagenschritt schließen",
        "diesen Posten als Auflage befestigen; Schritt schließen",
        "Ein Ereignis; dies ist eine gelernte Auflagen-Endform und keine freie Zerlegung jedes doppelten d/y.",
    ),
}


def infer_core(seg: str) -> str:
    for token, value in (
        ("AIR_FLOW", "AIR=FLÜSSIGKEITSLAUF"),
        ("DSHE_CLEAN_WATER", "DSHE=SAUBERES WASSER ZUGEBEN"),
        ("RSHE_WASH_PART", "RSHE=TEIL ALS WASCHUNG"),
        ("LCH", "LCH=FLÜSSIGEN ANTEIL ABZIEHEN"),
        ("LO_LEARNED+CHED", "LO+CHED=REST HINAUSFÜHREN"),
        ("DAL+CHD", "DAL+CHD=LOKAL UMSETZEN"),
        ("OT+CHD", "OT+CHD=DANACH UMSETZEN"),
        ("OL+CHED", "OL+CHED=WEITERFÜHREN"),
        ("L+CHED", "L+CHED=HINAUSFÜHREN"),
        ("P+CHED", "P+CHED=HINEINFÜHREN"),
        ("OT+CHED", "OT+CHED=DANACH UMSETZEN"),
        ("OK+CHED", "OK+CHED=ANSATZ UMSETZEN"),
        ("OK+CHD", "OK+CHD=ANSATZ UMSETZEN"),
        ("CHD", "CHD~CHED=UMSETZEN"),
        ("CHED", "CHED=UMSETZEN"),
        ("OK+SHED", "OK+SHED=ANSATZ ZUR RUHE BRINGEN"),
        ("SHED_REST", "SHED=RUHEN/ABSETZEN"),
        ("SH_REST", "SH=RUHEN/ABSETZEN"),
        ("OK", "OK=IN ARBEIT SETZEN"),
        ("OT", "OT=DANACH"),
        ("AIN_PORTION", "AIN=PORTION"),
        ("AIIN_MEASURE", "AIIN=MASS"),
        ("Y_REFERENT", "Y=LAUFENDER POSTEN"),
    ):
        if token in seg:
            return value
    return "GELERNTER KERN DER EXAKTEN KARTE"


def infer_grade(seg: str) -> str:
    padded = f"+{seg}+"
    if "E_GRADE_3" in seg or "+EEE+" in padded:
        return "EEE=vollständig/durchgehend"
    if "E_GRADE_2" in seg or "+EE+" in padded:
        return "EE=anhaltend"
    if "E_GRADE_1" in seg or "+E+" in padded:
        return "E=kurz/direkt"
    return "0"


def generic(row: dict[str, str]) -> tuple[str, str, str, str, str, str, str]:
    seg = row["semantic_segmentation"]
    surf = row["surface_family"]
    default = row["concrete_word_reading_de"]
    named_in_seg = any(
        token in seg
        for token in (
            "IIN_GRADE",
            "E_GRADE_",
            "CTH_READY",
            "SHED_REST",
            "SH_REST",
            "CHK_WARMTH",
            "SOLK_COLLECTION",
            "OLK~SOLK",
            "Y_REFERENT",
            "DY_TERMINAL",
            "TERMINAL_Y",
        )
    ) or any(f"+{g}+" in f"+{seg}+" for g in ("E", "EE", "EEE"))
    if not named_in_seg:
        return (
            "SURFACE_NEIGHBOR_ONLY",
            seg,
            "GELERNTE GANZKARTE",
            "—",
            "—",
            default,
            "Ähnliche Buchstaben reichen nicht zur Zerlegung; exakte Karte und lokaler Satz behalten Vorrang.",
        )
    if "DY_TERMINAL" in seg or "TERMINAL_Y" in seg:
        status = "PRODUCTIVE_ENDPOINT"
        endpoint = "DY=Schritt schließen"
        limit = "Abschluss gilt nur in dieser lizenzierten exakten Karte, nicht für jedes sichtbare -dy."
    elif "Y_REFERENT" in seg:
        status = "Y_REFERENCE"
        endpoint = "Y=dies/es"
        limit = "Referenz gilt nur in dieser lizenzierten exakten Karte; Y bedeutet nicht selbst offen."
    else:
        status = "NAMED_FAMILY"
        endpoint = "lokal gelernt"
        limit = "Die Karte bleibt ein gelernter Werkstattwert außerhalb der produktiven Matrix."
    return (status, seg, infer_core(seg), infer_grade(seg), endpoint, default, limit)


def rival_for(status: str, row: dict[str, str]) -> str:
    seg = row["semantic_segmentation"]
    if status == "SURFACE_NEIGHBOR_ONLY":
        return "bloße Substring-Zerlegung nach ähnlich aussehender Nachbarkarte"
    if "IIN" in seg:
        return "IIN als Zahl, Maß oder Zeitwert statt als benannter Grad"
    if "CTH" in seg or "cth" in row["surface_family"]:
        return "CTH überall als säubern, warm oder bereit lesen"
    if "SH" in seg or "shed" in row["surface_family"] or "tedy" in row["surface_family"]:
        return "SHED allgemein als waschen oder Wärme lesen"
    if "CHK" in seg or "chk" in row["surface_family"] or "chek" in row["surface_family"]:
        return "CHK allgemein als Gefäß, Lauf oder Dauer lesen"
    if "SOLK" in seg or "solk" in row["surface_family"] or "olk" in row["surface_family"]:
        return "jede SOLK/OLK-Schreibung als Sammelstelle oder Tuch lesen"
    if "DY" in seg or "Y" in seg:
        return "jedes sichtbare y/dy mechanisch als Referenz beziehungsweise Abschluss lesen"
    return "unzerlegte Ganzkarte ohne gemeinsame Lehrregel"


def consequence(status: str, grade: str, endpoint: str) -> str:
    if status == "MATRIX_CELL":
        return f"Kern wählen; {grade}; dann {endpoint}."
    if status == "MATRIX_CELL_WITH_LOCAL_ENDING":
        return f"Gradregel nutzen, aber {endpoint} als lokale Wärmeendung lernen."
    if status == "GRADE_NAMER":
        return "IIN benennt die verlangte Stufe; es führt keinen Schritt aus."
    if status == "SURFACE_NEIGHBOR_ONLY":
        return "Als eigene Karte auswendig lernen; nicht durch Schriftähnlichkeit ableiten."
    if status == "Y_REFERENCE":
        return "Den laufenden Posten wieder aufnehmen; keinen Abschluss hinzufügen."
    if status == "PRODUCTIVE_ENDPOINT":
        return "Die Kernhandlung ausführen und den lokalen Schritt schließen."
    if status == "CORE_BASE":
        return "Den Grundzustand ohne zusätzlichen Grad lesen."
    return "Als lokale Erweiterung der Kernkarte lehren."


def main() -> None:
    dictionary = [row for row in read_tsv(DICTIONARY) if selected(row)]
    events_by_type: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in read_tsv(INTERLINEAR):
        events_by_type[event["joint_tuple_id"]].append(event)

    fields = [
        "inventory_status",
        "joint_tuple_id",
        "surface_family",
        "occurrences",
        "event_ids",
        "statement_ids",
        "pages",
        "selected_decomposition",
        "core_value_de",
        "grade_value_de",
        "endpoint_value_de",
        "default_reading_de",
        "event_contexts_de",
        "strongest_rival_de",
        "contradiction_or_limit_de",
        "teaching_consequence_de",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in sorted(dictionary, key=lambda item: (item["surface_family"], item["joint_tuple_id"])):
            card = row["joint_tuple_id"]
            status, decomposition, core, grade, endpoint, default, limit = OVERRIDES.get(
                card, generic(row)
            )
            events = events_by_type[card]
            grouped_contexts: dict[str, list[str]] = defaultdict(list)
            for event in events:
                grouped_contexts[event["contextual_event_reading_de"]].append(event["event_id"])
            contexts = " | ".join(
                f"{','.join(ids)}={reading}" for reading, ids in grouped_contexts.items()
            )
            writer.writerow(
                {
                    "inventory_status": status,
                    "joint_tuple_id": card,
                    "surface_family": row["surface_family"],
                    "occurrences": row["occurrences"],
                    "event_ids": "|".join(event["event_id"] for event in events),
                    "statement_ids": "|".join(dict.fromkeys(event["statement_id"] for event in events)),
                    "pages": "|".join(dict.fromkeys(event["page"] for event in events)),
                    "selected_decomposition": decomposition,
                    "core_value_de": core,
                    "grade_value_de": grade,
                    "endpoint_value_de": endpoint,
                    "default_reading_de": default,
                    "event_contexts_de": contexts,
                    "strongest_rival_de": rival_for(status, row),
                    "contradiction_or_limit_de": limit,
                    "teaching_consequence_de": consequence(status, grade, endpoint),
                }
            )


if __name__ == "__main__":
    main()
