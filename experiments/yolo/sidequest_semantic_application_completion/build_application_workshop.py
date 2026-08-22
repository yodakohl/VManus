#!/usr/bin/env python3
"""Build the bounded application workshop from the selected filtration edition."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_filtration_separation_completion"
DICTIONARY = SOURCE / "SELECTED_173_FILTRATION_DICTIONARY.tsv"
INTERLINEAR = SOURCE / "SELECTED_381_FILTRATION_INTERLINEAR.tsv"
SENTENCES = SOURCE / "SELECTED_116_FILTRATION_SENTENCES.tsv"
OUTPUT = Path(__file__).with_name("APPLICATION_WORKSHOP_PARADIGM.tsv")


TARGET_SURFACES = {
    "chor|or|shor|sor",
    "cholor|olor",
    "otchor|qotchor",
    "chochor",
    "orain",
    "chkain|kain",
    "aiin|chaiin|daiin|saiin|taiin",
    "okain|qokain",
    "okaiin|qokaiin",
    "otaiin|sotaiin",
    "ykain",
    "ykan",
    "ykaiin",
    "al|chal|cheal|dal|sal|tal",
    "okal|qokal",
    "qokaly",
    "otal|qotal",
    "qokeedal",
    "lcheey",
    "dsheol",
    "shecthedchy",
    "qolky",
    "kchol",
    "cheeckhody",
    "qokylddy",
    "choy",
    "rshedy",
    "okey|qokey",
    "okeey|qokeey",
    "qokedy",
    "qokeedy",
    "qokeeedy",
    "choky|oky|qoky",
    "chokchy|okchy|qokchy",
    "chey|chy|dy|shy|sy|y",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


# stage, status, decomposition, atom, default, group, substitution, prediction, limit
OVERRIDES: dict[str, tuple[str, str, str, str, str, str, str, str, str]] = {
    "7a4bb8136330ee4e6e56": (
        "01_PREPARATION",
        "COMPOSITIONAL_CORE",
        "OR_PREPARATION",
        "OR=ZUBEREITUNG",
        "Zubereitung",
        "PREPARATION_DECK",
        "Grundkarte; OL/OT/CHO und AIN wählen Relation, Material oder Portion.",
        "Vor einer Zielkarte liefert OR den anzuwendenden Ansatz.",
        "Nur die exakte OR-Familie, nicht jeder sichtbare or-Substring.",
    ),
    "dec401773c1f0347793d": (
        "01_PREPARATION",
        "COMPOSITIONAL_CARD",
        "OL_CONTINUE+OR_PREPARATION",
        "OL=VORIGE; OR=ZUBEREITUNG",
        "vorige Zubereitung",
        "PREPARATION_DECK",
        "Wählt den vorigen statt eines neuen Ansatzes.",
        "Vor AL/OKAL: vorige Zubereitung an der Stelle anwenden.",
        "OL bleibt Fortsetzung, nicht Öl.",
    ),
    "10488b911aae52b3b334": (
        "01_PREPARATION",
        "COMPOSITIONAL_CARD",
        "OT_NEXT+OR_PREPARATION",
        "OT=NÄCHSTE; OR=ZUBEREITUNG",
        "nächste Zubereitung",
        "PREPARATION_DECK",
        "Wählt den nächsten Ansatz.",
        "Vor AL/OKAL: nächste Zubereitung an die Zielstelle bringen.",
        "OT heißt danach/nächster, nicht automatisch wiederholen.",
    ),
    "b9d7b6d68209a9019e7a": (
        "01_PREPARATION",
        "COMPOSITIONAL_CARD",
        "CHO_PLANT+OR_PREPARATION",
        "CHO=PFLANZENSTOFF; OR=ZUBEREITUNG",
        "Pflanzenzubereitung",
        "PREPARATION_DECK",
        "Materialauswahl innerhalb des Zubereitungsslots.",
        "Mit AIN/AIIN und AL ergibt sich eine portionierte Pflanzenanwendung.",
        "Ein Ereignis; CHO ist nur in dieser Karte Pflanzenstoff.",
    ),
    "6afeb5c9ab9f6cbdea0d": (
        "01_PREPARATION",
        "COMPOSITIONAL_CARD",
        "OR_PREPARATION+AIN_PORTION",
        "OR=ZUBEREITUNG; AIN=PORTION",
        "Portion der Zubereitung",
        "PREPARATION_DECK",
        "Portioniert den Ansatz; bedeutet nicht warm auflegen.",
        "Vor OKAL: eine Portion der Zubereitung an der Stelle einsetzen.",
        "Ein Ereignis, aber beide Beiträge sind anderweitig wiederholt.",
    ),
    "9da1b6ac2c929daea697": (
        "02_QUANTITY",
        "COMPOSITIONAL_CORE",
        "AIN_PORTION",
        "AIN=PORTION",
        "eine Portion",
        "QUANTITY_DECK",
        "Nennt den abgeteilten Teil, nicht das Maßrezept.",
        "Kann zwischen OR und AL stehen: Portion des Ansatzes an die Stelle.",
        "KAIN ist hier lizenzierte Hülle; nicht jede K-Schreibung trägt AIN.",
    ),
    "2f1c5e56e8f0ff459065": (
        "02_QUANTITY",
        "COMPOSITIONAL_CORE",
        "AIIN_MEASURE",
        "AIIN=MASS",
        "vorgeschriebenes Maß",
        "QUANTITY_DECK",
        "Nennt die Vorschrift, nicht die körperliche Portion.",
        "Vor einer Gradanwendung legt AIIN die Einsatzmenge fest.",
        "DAIN=Tuch und IIN=Stufe bleiben exakte andere Karten.",
    ),
    "1645e612504fcef59ced": (
        "02_QUANTITY",
        "COMPOSITIONAL_CARD",
        "OK_APPLY+AIN_PORTION",
        "OK=EINSETZEN; AIN=PORTION",
        "eine Portion zugeben",
        "QUANTITY_DECK",
        "Ausgeführte Portion, kein bloßer Mengenname.",
        "Vor OKAL: Portion zugeben und an der Zielstelle einsetzen.",
        "Der Empfänger kommt aus AL oder dem lokalen Besitzer.",
    ),
    "b5fcea1eaed06b2f2291": (
        "02_QUANTITY",
        "COMPOSITIONAL_CARD",
        "OK_SET+AIIN_MEASURE",
        "OK=EINSTELLEN; AIIN=MASS",
        "auf Maß einstellen",
        "QUANTITY_DECK",
        "Maßeinstellung vor Handlung oder Ziel.",
        "Mit OKEEDAL: auf Maß einstellen und länger an der Stelle einwirken.",
        "Kein räumliches Hineingeben ohne eigene Zielkarte.",
    ),
    "54d0e228ca346110af05": (
        "02_QUANTITY",
        "COMPOSITIONAL_CARD",
        "OT_NEXT+AIIN_MEASURE",
        "OT=NÄCHSTE; AIIN=MASS",
        "nächstes Maß",
        "QUANTITY_DECK",
        "Wechselt die Maßvorgabe.",
        "Ein folgendes OTAL kann dazu die nächste Zielstelle wählen.",
        "Nicht voriges Maß wiederholen.",
    ),
    "403c1592f918c8f23b88": (
        "02_QUANTITY",
        "COMPOSITIONAL_CARD",
        "Y_CURRENT+K_HULL+AIN_PORTION",
        "Y=DIES; AIN=PORTION",
        "Portion dieses Postens",
        "QUANTITY_DECK",
        "Bindet die Portion an den laufenden Posten.",
        "Mit AL: diese Portion an die Stelle.",
        "Ein Ereignis; K bleibt eine gelernte Hülle.",
    ),
    "d929a14ec45749b2e805": (
        "02_QUANTITY",
        "COMPOSITIONAL_CARD",
        "Y_CURRENT+K_HULL+AIN_PORTION",
        "Y=DIES; AIN=PORTION",
        "diese Portion",
        "QUANTITY_DECK",
        "Kurze deiktische Portion.",
        "Mit OKAL: diese Portion an der Stelle einsetzen.",
        "Ein Ereignis; keine Weißweinbedeutung.",
    ),
    "f7dc90b2c31fd341f0a4": (
        "02_QUANTITY",
        "COMPOSITIONAL_CARD",
        "Y_CURRENT+K_HULL+AIIN_MEASURE",
        "Y=DIES; AIIN=MASS",
        "Maß dieses Postens",
        "QUANTITY_DECK",
        "Bindet das Maß an den laufenden Posten.",
        "Kann eine folgende Zielanwendung bemessen.",
        "Ein Ereignis; keine Waschhandlung.",
    ),
    "dd0ecaf5e27d81befffc": (
        "03_TARGET",
        "COMPOSITIONAL_CORE",
        "AL_TARGET",
        "AL=ZIEL-/ARBEITSSTELLE",
        "Zielstelle",
        "TARGET_DECK",
        "Nackte Adresse; Handlung kommt aus Nachbarkarte oder Besitzer.",
        "OR+AIN vor AL liest sich als Portion der Zubereitung für diese Stelle.",
        "AL benennt keine feste Haut-, Pflanzen- oder Ablaufstelle.",
    ),
    "308e8ea2d5d190c498e8": (
        "03_TARGET",
        "COMPOSITIONAL_CARD",
        "OK_APPLY+AL_TARGET",
        "OK=EINSETZEN; AL=STELLE",
        "an der Stelle einsetzen",
        "TARGET_DECK",
        "Ausgeführte Zielanwendung ohne ausdrückliches Y.",
        "Nach OR/AIN: den vorbereiteten Anteil an der Stelle einsetzen.",
        "Die genaue Stelle kommt aus Bildbesitzer oder lokaler Fachkarte.",
    ),
    "4a7a6326ac95a8809302": (
        "03_TARGET",
        "COMPOSITIONAL_CARD",
        "OK_APPLY+AL_TARGET+Y_CURRENT",
        "OK=EINSETZEN; AL=STELLE; Y=DIES",
        "diesen Posten an der Stelle einsetzen",
        "TARGET_DECK",
        "Explizite Dreierkarte für Handlung, Ziel und Referent.",
        "Sagt die Lesung von OKAL+laufendem Posten voraus.",
        "Ein Ereignis; die Argumentreihenfolge ist nur hier direkt geschrieben.",
    ),
    "90bcf0a9ec0ef56399e6": (
        "03_TARGET",
        "COMPOSITIONAL_CARD",
        "OT_NEXT+AL_TARGET",
        "OT=DANACH; AL=STELLE",
        "danach zur Stelle",
        "TARGET_DECK",
        "Wechselt zur folgenden Zielstelle.",
        "Kann vor einer neuen Kontaktkarte stehen.",
        "Kein festes Wort Ablaufstelle.",
    ),
    "93f69c38fdedee1598e9": (
        "03_TARGET",
        "COMPOSITIONAL_GRADE_CARD",
        "OK_APPLY+EE_SUSTAINED+AL_TARGET",
        "OK=ANSETZEN; EE=LÄNGER; AL=STELLE",
        "länger an der Stelle einwirken",
        "TARGET_GRADE_GRID",
        "AL ersetzt im Ausgangsslot Y oder DY; der Grad bleibt erhalten.",
        "Sagt kurze und vollständige Zielkontakte als mögliche Schablonenzellen voraus.",
        "Nur eine besetzte Zielgradzelle; E+AL und EEE+AL bleiben Vorhersagen.",
    ),
    "c205570c49d4d93c23d3": (
        "03_TARGET",
        "LEARNED_TARGET_CARD",
        "QOLKY_WHOLE",
        "QOLKY=BETROFFENE STELLE",
        "betroffene Stelle",
        "LOCAL_TARGET_CARDS",
        "Konkreter Körper-/Arbeitsort; kein allgemeines AL nötig.",
        "Kann denselben Zielslot wie AL füllen.",
        "Nicht OL=weiter plus KY=Wärme zerlegen.",
    ),
    "5fca8fc3dee57e1d8c1f": (
        "03_TARGET",
        "LEARNED_RESULT_CARD",
        "LCHEEY_WHOLE",
        "LCHEEY=BENETZTE STELLE",
        "benetzte Stelle",
        "LOCAL_TARGET_CARDS",
        "Ziel nach einer Kontaktbehandlung, nicht Handlung selbst.",
        "Nach OKEEY bestätigt sie eine länger benetzte Zielstelle.",
        "Nicht aus SHEY=Klarauszug oder EEY-Grad ableiten.",
    ),
    "b921a237be883a820352": (
        "04_CURRENT_ITEM",
        "COMPOSITIONAL_CORE",
        "Y_CURRENT_ITEM_CARD",
        "Y=DIES/LAUFENDER POSTEN",
        "dieser Posten",
        "CURRENT_ITEM_DECK",
        "Referenzkarte, keine Handlung und kein Schluss.",
        "Nach einer Zielkarte hält Y denselben Auftrag verfügbar.",
        "Die sichtbare Variante dy dieser Karte ist ausdrücklich nicht terminal.",
    ),
    "276a7c2d74d1143446f4": (
        "04_CURRENT_ITEM",
        "COMPOSITIONAL_CARD",
        "OK_APPLY+Y_CURRENT",
        "OK=EINSETZEN; Y=DIES",
        "diesen Posten einsetzen",
        "CURRENT_ITEM_DECK",
        "Ungradierte Grundanwendung.",
        "Basis für OKEY/OKEEY und qokaly.",
        "Einsetzen ist ein neutraler Werkstattwert, nicht zwingend medizinisch.",
    ),
    "9ad66e67803a12e745de": (
        "04_CURRENT_ITEM",
        "COMPOSITIONAL_CARD",
        "OK_APPLY+CHY_WRAPPED_CURRENT",
        "OK=EINSETZEN; CHY=DIES",
        "diesen Posten einsetzen",
        "CURRENT_ITEM_DECK",
        "Umhüllte Rendererform derselben Grundanwendung.",
        "Soll dieselbe Folgelesung wie OK+Y tragen.",
        "CHY ist nur in der lizenzierten Wrapperfamilie Y-gleich.",
    ),
    "74c76d589d44120f647b": (
        "05_SPECIALIST_ACTION",
        "LEARNED_OPERATOR",
        "DSHEOL_WHOLE",
        "DSHEOL=BESTREICHEN",
        "bestreichen",
        "SPREAD_ACTION_DECK",
        "Gleicher Anwendungsplatz wie SHECTHEDCHY, andere Fachkarte.",
        "Vor einer Grad-/Stationskarte: Stoff auf die Stelle streichen.",
        "Nicht DSHE=sauberes Wasser plus OL=weiter zerlegen.",
    ),
    "348e81ba084c5acdb32b": (
        "05_SPECIALIST_ACTION",
        "LEARNED_OPERATOR",
        "SHECTHEDCHY_WHOLE",
        "SHECTHEDCHY=AUFSTREICHEN",
        "aufstreichen",
        "SPREAD_ACTION_DECK",
        "Praktische Schwester von DSHEOL ohne behauptete gemeinsame Wurzel.",
        "Mit folgendem OKY: aufstreichen und den Posten weiter einsetzen.",
        "Nicht CTH=bereit oder CHY=Referent aus dem Inneren herauslösen.",
    ),
    "893c570f3fa3fce99711": (
        "05_SPECIALIST_ACTION",
        "LEARNED_OPERATOR",
        "KCHOL_WHOLE",
        "KCHOL=AUFLEGEN",
        "auflegen",
        "PLACEMENT_ACTION_DECK",
        "Offene Platzierung; Festmachen kommt erst aus LDDY.",
        "Sagt eine mögliche Folge Auflegen -> Festmachen voraus.",
        "Nicht K plus OL=weiter zerlegen.",
    ),
    "c10aec6d4dd877ec8bd8": (
        "05_SPECIALIST_ACTION",
        "LEARNED_OPERATOR",
        "CHOY_WHOLE",
        "CHOY=MIT WASSER WASCHEN",
        "mit Wasser waschen",
        "WASH_APPLICATION_DECK",
        "Offene Waschhandlung vor weiterer Anwendung.",
        "Kann durch RSHEDY geschlossen werden, ohne dass beide eine sichtbare Wurzel teilen.",
        "Nicht CHO=Pflanzenstoff plus Y zerlegen.",
    ),
    "08bd5ca0c2ad137a056d": (
        "06_CONTACT_GRADE",
        "COMPOSITIONAL_GRADE_CARD",
        "OK_APPLY+E_BRIEF+Y_CURRENT",
        "E=KURZ; Y=DIES",
        "kurz anlegen",
        "CONTACT_GRADE_GRID",
        "Kurzer offener Kontakt am laufenden Posten.",
        "Mit AL statt Y wäre kurze Einwirkung an der Stelle zu erwarten.",
        "Wasser oder Salbe kommt aus dem lokalen Ansatz, nicht aus E/Y.",
    ),
    "0275fbf14e07935b0a45": (
        "06_CONTACT_GRADE",
        "COMPOSITIONAL_GRADE_CARD",
        "OK_APPLY+EE_SUSTAINED+Y_CURRENT",
        "EE=LÄNGER; Y=DIES",
        "länger einwirken lassen",
        "CONTACT_GRADE_GRID",
        "Anhaltender offener Kontakt.",
        "Mit AL ist die besetzte Karte OKEEDAL; mit DY die Karte OKEEDY.",
        "Y bedeutet nicht offen; Offenheit entsteht nur durch fehlenden Schluss.",
    ),
    "7db18b2f0fb7ed0fcfd3": (
        "06_CONTACT_GRADE",
        "COMPOSITIONAL_GRADE_CARD",
        "OK_APPLY+E_BRIEF+DY_CLOSE",
        "E=KURZ; DY=SCHLUSS",
        "kurz benetzen; Schluss",
        "CONTACT_GRADE_GRID",
        "Kurzer terminaler Kontakt.",
        "Bildet mit OKEY den offenen/geschlossenen Kurzgrad.",
        "Nicht jedes sichtbare dy ist Schluss.",
    ),
    "7d25241b0e56c836372a": (
        "06_CONTACT_GRADE",
        "COMPOSITIONAL_GRADE_CARD",
        "OK_APPLY+EE_SUSTAINED+DY_CLOSE",
        "EE=LÄNGER; DY=SCHLUSS",
        "länger einweichen; Schluss",
        "CONTACT_GRADE_GRID",
        "Anhaltender terminaler Kontakt.",
        "Bildet mit OKEEY und OKEEDAL die Y/AL/DY-Ausgangsreihe.",
        "Einweichen ist die konkrete Lesung; invariant ist anhaltender Kontakt mit Schluss.",
    ),
    "d25110e0d8488927278f": (
        "06_CONTACT_GRADE",
        "COMPOSITIONAL_GRADE_CARD",
        "OK_APPLY+EEE_COMPLETE+DY_CLOSE",
        "EEE=VOLLSTÄNDIG; DY=SCHLUSS",
        "vollständig durchtränken; Schluss",
        "CONTACT_GRADE_GRID",
        "Vollständiger terminaler Kontakt.",
        "Sagt eine offene oder zielgebundene Vollstufe nur als künftige Schablonenzelle voraus.",
        "Ein Ereignis; keine unbelegte EEE+Y/AL-Karte erfinden.",
    ),
    "7f68f60279efe6b28cd7": (
        "07_APPLICATION_CLOSE",
        "LEARNED_TERMINAL_CARD",
        "RSHE_WASH_PART+DY_CLOSE",
        "RSHE=ALS WASCHUNG; DY=SCHLUSS",
        "als Waschung anwenden; Schluss",
        "WASH_APPLICATION_DECK",
        "Geschlossene Waschanwendung.",
        "Praktisches terminales Gegenstück zu CHOY, nicht formales Allomorph.",
        "Nicht zur SHED-Ruhefamilie ziehen.",
    ),
    "95987d6f198d6d247511": (
        "07_APPLICATION_CLOSE",
        "LEARNED_TERMINAL_CARD",
        "CHEECKHO_EXTERNAL_APPLICATION+DY_CLOSE",
        "CHEECKHO=ÄUSSERLICH ANWENDEN; DY=SCHLUSS",
        "äußerlich anwenden; Schluss",
        "APPLICATION_CLOSE_DECK",
        "Allgemeine äußere Anwendung mit Schluss.",
        "Bleibt von Festmachen und Waschen getrennt.",
        "Nicht als CKH-Durchlauf oder freies CHEE+CKHO zerlegen.",
    ),
    "eb2e4bc143f623ee03ac": (
        "07_APPLICATION_CLOSE",
        "SINGLE_CARD_TERMINAL_CORE",
        "OK_APPLY+Y_CURRENT+LDDY_FASTEN_CLOSE",
        "LDDY=FESTMACHEN; TERMINAL",
        "diesen Posten festmachen; Schluss",
        "PLACEMENT_ACTION_DECK",
        "Geschlossene Befestigung nach einer gedachten oder expliziten Auflage.",
        "KCHOL auflegen -> LDDY festmachen ist die einfachste vorhergesagte Zweistufenfolge.",
        "Nur eine exakte Karte; LDDY bleibt ein gelernter terminaler Kern.",
    ),
}


def main() -> None:
    dictionary = [
        row for row in read_tsv(DICTIONARY) if row["surface_family"] in TARGET_SURFACES
    ]
    events_by_card: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in read_tsv(INTERLINEAR):
        events_by_card[event["joint_tuple_id"]].append(event)
    sentence_rows = read_tsv(SENTENCES)
    sentences = {row["statement_id"]: row for row in sentence_rows}
    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentence_rows:
        records[row["record_unit_id"]].append(row)

    fields = [
        "row_kind",
        "application_stage",
        "card_status",
        "joint_tuple_id_or_record",
        "surface_family",
        "occurrences",
        "event_ids",
        "statement_ids",
        "record_ids",
        "pages",
        "selected_decomposition",
        "atomic_contribution_de",
        "concrete_default_de",
        "substitution_group",
        "substitution_rule_de",
        "event_contexts_de",
        "complete_statements_de",
        "complete_record_de",
        "workshop_prediction_de",
        "strongest_rival_de",
        "contradiction_or_limit_de",
    ]
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        prepared = []
        for row in dictionary:
            card = row["joint_tuple_id"]
            if card not in OVERRIDES:
                raise ValueError(f"Missing application decision for {card} {row['surface_family']}")
            prepared.append((OVERRIDES[card][0], row["surface_family"], row))
        for _, _, row in sorted(prepared):
            card = row["joint_tuple_id"]
            stage, status, decomposition, atom, default, group, rule, prediction, limit = OVERRIDES[card]
            events = events_by_card[card]
            statement_ids = list(dict.fromkeys(event["statement_id"] for event in events))
            record_ids = list(dict.fromkeys(event["record_unit_id"] for event in events))
            contexts: dict[str, list[str]] = defaultdict(list)
            for event in events:
                contexts[event["contextual_event_reading_de"]].append(event["event_id"])
            writer.writerow(
                {
                    "row_kind": "TYPE",
                    "application_stage": stage,
                    "card_status": status,
                    "joint_tuple_id_or_record": card,
                    "surface_family": row["surface_family"],
                    "occurrences": row["occurrences"],
                    "event_ids": "|".join(event["event_id"] for event in events),
                    "statement_ids": "|".join(statement_ids),
                    "record_ids": "|".join(record_ids),
                    "pages": "|".join(dict.fromkeys(event["page"] for event in events)),
                    "selected_decomposition": decomposition,
                    "atomic_contribution_de": atom,
                    "concrete_default_de": default,
                    "substitution_group": group,
                    "substitution_rule_de": rule,
                    "event_contexts_de": " | ".join(
                        f"{','.join(ids)}={context}" for context, ids in contexts.items()
                    ),
                    "complete_statements_de": " | ".join(
                        f"{sid}={sentences[sid]['surface_sequence']} :: {sentences[sid]['workshop_sentence_de']}"
                        for sid in statement_ids
                    ),
                    "complete_record_de": "",
                    "workshop_prediction_de": prediction,
                    "strongest_rival_de": "den vollständigen lokalen Satz als Wortwert speichern",
                    "contradiction_or_limit_de": limit,
                }
            )
        for record_id, rows in records.items():
            writer.writerow(
                {
                    "row_kind": "RECORD",
                    "application_stage": "FULL_RECORD_CONTEXT",
                    "card_status": "CONTEXT_ONLY",
                    "joint_tuple_id_or_record": record_id,
                    "surface_family": "",
                    "occurrences": sum(int(row["event_count"]) for row in rows),
                    "event_ids": "|".join(row["event_ids"] for row in rows),
                    "statement_ids": "|".join(row["statement_id"] for row in rows),
                    "record_ids": record_id,
                    "pages": "|".join(dict.fromkeys(row["page"] for row in rows)),
                    "selected_decomposition": "FULL_SELECTED_RECORD",
                    "atomic_contribution_de": "KONTEXT; KEIN WORTWERT",
                    "concrete_default_de": "vollständiger Recordkontext",
                    "substitution_group": "NONE_RECORD_CONTEXT",
                    "substitution_rule_de": "Nicht als Kartenbedeutung verwenden.",
                    "event_contexts_de": "",
                    "complete_statements_de": "",
                    "complete_record_de": " || ".join(
                        f"{row['statement_id']}={row['surface_sequence']} :: {row['workshop_sentence_de']}"
                        for row in rows
                    ),
                    "workshop_prediction_de": "Der Record bleibt vollständig; nur die Zielkarten erhalten neue Kurzwerte.",
                    "strongest_rival_de": "Recordkontext fälschlich in einzelne Wörter hineinlesen",
                    "contradiction_or_limit_de": "Kontextzeile, keine zusätzliche Lexembehauptung.",
                }
            )


if __name__ == "__main__":
    main()
