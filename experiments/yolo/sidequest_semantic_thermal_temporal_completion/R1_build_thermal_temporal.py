#!/usr/bin/env python3
"""Build the independent R1 thermal/temporal workshop edition."""

from __future__ import annotations

import csv
import json
from collections import OrderedDict, Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "experiments/yolo/sidequest_semantic_medium_substance_completion"
OUT = Path(__file__).resolve().parent

DICT_IN = SRC / "SELECTED_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_IN = SRC / "SELECTED_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
SENT_IN = SRC / "SELECTED_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# Revision tuple:
# segmentation, nucleus, short default, family, strength, apprentice rule, note
R = {
    # IIN: one target stage, never a free reading of every visible iin string.
    "2c82523794dcb7d2b343": (
        "IIN_TARGET_STAGE", "IIN=Stufe", "Stufe", "IIN_STAGE",
        "SELECTED_RECURRENT_CORE", "IIN nennt die einzustellende Stufe.",
        "Soll- is supplied by the instruction slot; the card itself is shortened to STUFE.",
    ),
    "409de02322e7b2ca0c62": (
        "K_SOFT_HULL+IIN_TARGET_STAGE", "K=weich; IIN=Stufe", "weiche Stufe", "IIN_STAGE",
        "SELECTED_SINGLETON_COMPOSITION", "K macht die Stufe weich.",
        "The whole remains compositionally transparent inside the licensed IIN family.",
    ),
    "fcc1deda9e24ec268eb0": (
        "DA_OPENING_HULL+IIN_TARGET_STAGE", "DA=zweite Öffnung; IIN=Stufe", "zweite Öffnungsstufe", "IIN_STAGE",
        "SELECTED_SINGLETON_COMPOSITION", "DA wählt die zweite Öffnung, IIN ihre Stufe.",
        "Exact DAI IIN identity is required; DAIIN measure cards are different tuple identities.",
    ),
    # CHK warmth grid.
    "d904bf7b044dd3922781": (
        "CHK_WARM+GRADE_1+Y_CONTINUE", "CHK=wärmen; E=kurz oder mild", "anwärmen", "CHK_WARMTH",
        "SELECTED_RECURRENT_GRADE", "CHK+E heißt ANWÄRMEN.",
        "Three events support the brief/mild warmth member.",
    ),
    "2c1a5fd92b9e3c762242": (
        "CHK_WARM+GRADE_2+Y_CONTINUE", "CHK=wärmen; EE=länger", "warmhalten", "CHK_WARMTH",
        "SELECTED_RECURRENT_GRADE", "CHK+EE heißt WARMHALTEN.",
        "Two records support the sustained warmth member.",
    ),
    "f0db6d30cd34f4cb2a4d": (
        "CHK_WARM+GRADE_2+Y_CURRENT_ITEM", "CHK=wärmen; EE=länger; Y=laufender Posten", "Posten warmhalten", "CHK_WARMTH",
        "SELECTED_SINGLETON_PREDICTION", "Y hält den laufenden Posten als Gegenstand verfügbar.",
        "The B2 tool/measure chain supplies the current-item version.",
    ),
    "a84fbe3ad380df345b97": (
        "CHK_WARM+GRADE_2+DY_CLOSE", "CHK=wärmen; EE=länger; Endkarte=Schluss", "warmhalten; Schluss", "CHK_WARMTH",
        "SELECTED_SINGLETON_PREDICTION", "Die lizenzierte Endkarte schließt das Warmhalten.",
        "The close is exact-card licensed, not inferred from visible dy alone.",
    ),
    # CTH readiness grid.
    "e0b630cb1b5df5e7105b": (
        "CTHY_READY_CARD", "CTHY=bereit", "bereit", "CTH_READINESS",
        "SELECTED_RECURRENT_CORE", "CTHY heißt BEREIT.",
        "Seven events make this the recurrent readiness card.",
    ),
    "6b89d6dd70635bc60fe0": (
        "CTH_READY+GRADE_1+Y_CURRENT_ITEM", "CTH=bereit; E=kurz; Y=laufender Posten", "kurz bereithalten", "CTH_READINESS",
        "SELECTED_RECURRENT_EXTENSION", "CTH+E+Y hält den Posten kurz bereit.",
        "Two events retain a brief ready hold without turning all CTH substrings into readiness.",
    ),
    # SHED rest/settling grid: one apprentice word, settling is the wet-work expansion.
    "bc4f1f5c006c74a4d26d": (
        "SHED_REST+GRADE_1+DY_CLOSE", "SHED=ruhen lassen; E=kurz oder normal; Endkarte=Schluss", "ruhen lassen; Schluss", "SHED_REST",
        "SELECTED_RECURRENT_CORE", "SHED lässt den Posten ruhen; die Endkarte schließt.",
        "Twelve events support the ordinary rest close; settling is a local liquid consequence.",
    ),
    "03626ca94cb17800d767": (
        "SHED_REST+GRADE_2+DY_CLOSE", "SHED=ruhen lassen; EE=länger; Endkarte=Schluss", "länger ruhen lassen; Schluss", "SHED_REST",
        "SELECTED_SINGLETON_GRADE", "EE verlängert den Ruhegang.",
        "The one long rest immediately follows AIR activation.",
    ),
    "abb23e5e6936b4147f76": (
        "SHED_REST+AL_SITE", "SHED=ruhen lassen; AL=Stelle", "Ruhestelle", "SHED_REST",
        "SELECTED_RECURRENT_SITE", "AL macht aus SHED eine Ruhestelle.",
        "Two events support the site extension.",
    ),
    "daa1347f456415fe8737": (
        "OL_CONTINUE+SHED_REST+DY_CLOSE", "OL=mit Vorigem; SHED=ruhen lassen; Endkarte=Schluss", "mit Vorigem ruhen; Schluss", "SHED_REST",
        "SELECTED_SINGLETON_COMPOSITION", "OL nimmt den vorigen Posten in den Ruhegang mit.",
        "The exact card composes continuation with the selected rest close.",
    ),
    "db167f8e9b53eefb58f8": (
        "OK+SHED_REST+DY_CLOSE", "OK=in Arbeit setzen; SHED=ruhen lassen; Endkarte=Schluss", "zur Ruhe setzen; Schluss", "SHED_REST",
        "SELECTED_SINGLETON_COMPOSITION", "OK ruft den Ruhegang auf.",
        "No separate bath or warmth meaning is needed.",
    ),
    # Bounded whole-card fire/cool/time deck.
    "204b04837409088c48f9": (
        "OLTCHY_WARM_WHOLE_CARD", "OLTCHY=anwärmen", "anwärmen", "THERMAL_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "OLTCHY wird als ganze Karte ANWÄRMEN gelernt.",
        "Do not split visible OL here; its exact identity is a specialist heat card.",
    ),
    "e8a6105b5c3a6220b440": (
        "QOTCHOL_WARM_WHOLE_CARD", "QOTCHOL=anwärmen", "anwärmen", "THERMAL_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "QOTCHOL ist die zweite gelernte ANWÄRMEN-Karte.",
        "It is not parsed as OT+OL despite its surface resemblance.",
    ),
    "2e2027b1951d79911e24": (
        "TCHO_COOL+DY_CLOSE", "TCHO=abkühlen; Endkarte=Schluss", "abkühlen; Schluss", "THERMAL_WHOLE_CARD",
        "SELECTED_SINGLETON_CLOSE", "TCHO kühlt ab; die Endkarte schließt.",
        "The terminal Herbal member remains separate from CHARY and RAL.",
    ),
    "1496a731803a9f48d2e1": (
        "ROL_WARM_WINDOW_WHOLE_CARD", "ROL=noch warm", "noch warm", "THERMAL_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "ROL markiert das Arbeitsfenster NOCH WARM.",
        "This short state replaces the sentence-sized BEFORE COOLING gloss.",
    ),
    "8c97dfde96fbc78e3355": (
        "LOL_WARM_ENDPOINT_WHOLE_CARD", "LOL=warm genug", "warm genug", "THERMAL_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "LOL markiert WARM GENUG.",
        "This is an endpoint card, not a productive visible L/O/L analysis.",
    ),
    "a8af08e69edab8e54f15": (
        "SHFY_STANDING_TIME_WHOLE_CARD", "SHFYDAIIN=Stehzeit", "Stehzeit", "TIME_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "SHFYDAIIN ist die gelernte STEHZEIT-Karte.",
        "The sentence-sized former gloss is removed; AIIN is not globally redefined as time.",
    ),
    "21ed2873b71e57269c08": (
        "CHCKHAL_DURATION_WHOLE_CARD", "CHCKHAL=Dauer", "Dauer", "TIME_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "CHCKHAL nennt die DAUER.",
        "No value or unit is inferred.",
    ),
    "d72f71baff01cd0a0406": (
        "CHLD_SETTLING_SETPOINT_WHOLE_CARD", "CHLDAIIN=Absetzstand", "Absetzstand", "ENDPOINT_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "CHLDAIIN nennt den ABSETZSTAND.",
        "The sentence-sized UNTIL PRESCRIBED LEVEL gloss is reduced to a learned endpoint noun.",
    ),
    "d788d8d72d41b25a3c71": (
        "CHEALROR_CLEAR_ENDPOINT_WHOLE_CARD", "CHEALROR=Klarpunkt", "Klarpunkt", "ENDPOINT_WHOLE_CARD",
        "SELECTED_SINGLETON_WHOLE_CARD", "CHEALROR nennt den KLARPUNKT.",
        "Clear-flow expansion belongs to the statement, not the card.",
    ),
    # OL: carry the previous work forward. OT: advance one step.
    "dcda95c81a5460feb191": (
        "OL_CONTINUE_PREVIOUS", "OL=mit Vorigem fortsetzen", "fortsetzen", "OL_CONTINUATION",
        "SELECTED_RECURRENT_CORE", "OL führt den vorigen Arbeitsposten weiter.",
        "Nineteen events make this the strongest continuation card.",
    ),
    "497cbd9c7401810ff56b": (
        "OT_FOLLOW+OL_CONTINUE", "OT=danach; OL=fortsetzen", "danach fortsetzen", "OT_OL_ORDER",
        "SELECTED_SINGLETON_COMPOSITION", "OT springt vor, OL setzt fort.",
        "The two order contributions remain distinct.",
    ),
    "28ffbc88b97772a75f1e": (
        "OL_CONTINUE+CHED+DY_CLOSE", "OL=fortsetzen; CHED=führen; Endkarte=Schluss", "fortsetzen; Schluss", "OL_CONTINUATION",
        "SELECTED_RECURRENT_COMPOSITION", "OL führt den vorigen Gang bis zum Schluss weiter.",
        "Three records support the closed continuation.",
    ),
    "1b1ffdd869fb1429ad03": (
        "OL_CONTINUE+DY_CLOSE", "OL=fortsetzen; Endkarte=Schluss", "fortsetzen; Schluss", "OL_CONTINUATION",
        "SELECTED_RECURRENT_CLOSE", "OLDY setzt fort und schließt.",
        "The B4 sentence is repaired: this exact card does not itself heat a bath additive.",
    ),
    "232195d6ff2f326322f7": (
        "OK+OL_CONTINUE_PREVIOUS", "OK=in Gang setzen; OL=vorigen Gang fortsetzen", "vorigen Gang fortsetzen", "OL_CONTINUATION",
        "SELECTED_SINGLETON_COMPOSITION", "OK ruft den vorigen Gang erneut auf; OL liefert die Fortsetzung.",
        "This is continuation, not a liquid-flow noun.",
    ),
    "322281bd391aa621f568": (
        "OK+CHOL[OL_CONTINUE_PREVIOUS]", "OK=in Gang setzen; OL=voriges Arbeitsgut fortsetzen", "voriges Arbeitsgut fortsetzen", "OL_CONTINUATION",
        "SELECTED_SINGLETON_COMPOSITION", "Die CHOL-Hülle ruft dieselbe OL-Fortsetzung auf.",
        "No oil meaning is admitted.",
    ),
    "94df4847b7b16c98394a": (
        "OL_CONTINUE+AIN_PORTION", "OL=weitere; AIN=Portion", "weitere Portion", "OL_CONTINUATION",
        "SELECTED_RECURRENT_COMPOSITION", "OL übernimmt die vorige Reihe; AIN nennt die weitere Portion.",
        "The statement may supply ADD, but the card default remains a bounded amount.",
    ),
    "daf32e6db9e04413ce7f": (
        "OK+GRADE_2+OL_CONTINUE", "OK=ansetzen; EE=länger; OL=mit Vorigem fortsetzen", "länger fortsetzen", "OL_CONTINUATION",
        "SELECTED_SINGLETON_COMPOSITION", "EE verlängert, OL führt mit dem Vorigen fort.",
        "The compact default removes the whole surrounding clause.",
    ),
    "10488b911aae52b3b334": (
        "OT_FOLLOW+OR_BATCH", "OT=Folge; OR=Ansatz", "Folgeansatz", "OT_OL_ORDER",
        "SELECTED_RECURRENT_COMPOSITION", "OT vor einem Gegenstand heißt FOLGE-.",
        "Two Herbal occurrences support the next-batch reading.",
    ),
    "54d0e228ca346110af05": (
        "OT_FOLLOW+AIIN_MEASURE", "OT=Folge; AIIN=Maß", "Folgemaß", "OT_OL_ORDER",
        "SELECTED_RECURRENT_COMPOSITION", "OT macht aus AIIN das Folgemaß.",
        "Three events support the next-measure cell.",
    ),
    "90bcf0a9ec0ef56399e6": (
        "OT_FOLLOW+AL_SITE", "OT=Folge; AL=Stelle", "Folgestelle", "OT_OL_ORDER",
        "SELECTED_RECURRENT_COMPOSITION", "OT macht aus AL die Folgestelle.",
        "Three B3/B4 events support the station succession.",
    ),
    "faf321940aed922846a9": (
        "OT_FOLLOW+CHEY_CURRENT_ITEM", "OT=Folge; CHEY=Postenverweis", "Folgeposten wählen", "OT_OL_ORDER",
        "SELECTED_RECURRENT_COMPOSITION", "OT wählt den Folgeposten.",
        "Two records support the next-item call.",
    ),
    "5d5e0b288cf36864ed9d": (
        "OT_FOLLOW+GRADE_2+Y_CURRENT_ITEM", "OT=Folge; EE=länger; Y=Posten", "Folgeposten länger halten", "OT_OL_ORDER",
        "SELECTED_RECURRENT_COMPOSITION", "OT wählt den Folgeposten, EE verlängert seinen Halt.",
        "Two B2 events support the open sustained member.",
    ),
    "4de12cf322dfb76ded1e": (
        "OT_AFTER+CHED+DY_CLOSE", "OT=danach; CHED=umsetzen; Endkarte=Schluss", "danach umsetzen; Schluss", "OT_OL_ORDER",
        "SELECTED_RECURRENT_COMPOSITION", "OT heißt hier DANACH, nicht ERNEUT.",
        "Repetition has separate exact cards; the ambiguous again gloss is removed.",
    ),
    "1322bc176443fc2a8a86": (
        "OK+OK+CHY_CURRENT_ITEM", "OK+OK=erneut; CHY=laufender Posten", "erneut einsetzen", "REPETITION_WHOLE_OR_COMPOSITION",
        "SELECTED_SINGLETON_COMPOSITION", "Doppel-OK ruft denselben Posten ERNEUT auf.",
        "This one card licenses recurrence; it does not make every doubled glyph repetitive.",
    ),
}


# Context readback for revised exact identities.
CONTEXT = {ident: values[2].capitalize() for ident, values in R.items()}
CONTEXT.update(
    {
        "dcda95c81a5460feb191": "Mit dem Vorigen fortsetzen",
        "94df4847b7c8538dd": "Weitere Portion",
        "10488b911aae52b3b334": "Folgeansatz",
        "54d0e228ca346110af05": "Folgemaß",
        "90bcf0a9ec0ef56399e6": "Folgestelle",
        "faf321940aed922846a9": "Folgeposten wählen",
        "5d5e0b288cf36864ed9d": "Folgeposten länger halten",
        "6b89d6dd70635bc60fe0": "Den laufenden Posten kurz bereithalten",
        "f0db6d30cd34f4cb2a4d": "Den laufenden Posten warmhalten",
        "daa1347f456415fe8737": "Mit dem Vorigen ruhen; Schluss",
    }
)


# Full inventory. Types in R are revised; the rest are retained and explicitly audited.
AUDIT = {
    # Core grade/contact grid.
    "08bd5ca0c2ad137a056d": ("E_GRADE", "PRODUCTIVE_GRADE", "E=kurz; Y keeps the current item open"),
    "0275fbf14e07935b0a45": ("E_GRADE", "PRODUCTIVE_GRADE", "EE=länger; Y keeps the current item open"),
    "7db18b2f0fb7ed0fcfd3": ("E_GRADE", "PRODUCTIVE_GRADE", "E=kurz; licensed terminal card closes"),
    "7d25241b0e56c836372a": ("E_GRADE", "PRODUCTIVE_GRADE", "EE=länger; licensed terminal card closes"),
    "d25110e0d8488927278f": ("E_GRADE", "PRODUCTIVE_GRADE", "EEE=vollständig; licensed terminal card closes"),
    "93f69c38fdedee1598e9": ("E_GRADE", "PRODUCTIVE_GRADE", "EE=länger before AL site"),
    "42cdc187d5b9ffc60063": ("E_GRADE", "PRODUCTIVE_GRADE", "E=kurz at collection station"),
    "1bfd786e6b8b63734a59": ("E_GRADE", "PRODUCTIVE_GRADE", "EE=länger at collection station"),
    "3b70942557b3a40e8030": ("E_GRADE", "PRODUCTIVE_GRADE", "EE=länger and terminal collection"),
    "c45ebac60774620561e2": ("OT_OL_ORDER", "PRODUCTIVE_ORDER_GRADE", "OT=danach; E=kurz; terminal"),
    "ff178343c18e287ce3b7": ("OT_OL_ORDER", "PRODUCTIVE_ORDER_GRADE", "OT=danach; EE=länger; terminal"),
    "601b77449028deed39de": ("OT_OL_ORDER", "PRODUCTIVE_ORDER", "OT=danach; CHD operation; terminal"),
    "b6b654722e55729cc947": ("OT_OL_ORDER", "PRODUCTIVE_ORDER", "OT=danach; AR=source/out"),
    "dec401773c1f0347793d": ("OL_CONTINUATION", "PRODUCTIVE_ORDER", "OL=previous; OR=batch"),
    "d665560c8ff80799a82c": ("OL_CONTINUATION", "PRODUCTIVE_ORDER", "CH renderer plus OL previous-item call"),
    # Productive and learned cores revised in R.
    **{ident: (values[3], "REVISED_SELECTED_CARD", values[5]) for ident, values in R.items()},
    # Whole cards retained but essential to the inventory.
    "428a5e3662aa57b4b256": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "SCHOAL=Weinsud; heat operation comes from statement position"),
    "0bdc8b6db811b4e67a63": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "CHARY=abkühlen"),
    "4da0f0f7b5fc7ac20067": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "RAL=abkühlen"),
    "43eb9aa12959b4d5cdc9": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "QEKY=ungekocht"),
    "97cc9ac109148723c472": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "ODY=kühl lagern; terminal"),
    "883a6708116c342cb10b": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "SKAR=Warmausguss"),
    "98bdc4244c84cbef3321": ("THERMAL_WHOLE_CARD", "LEARNED_WHOLE_CARD", "RSHEAL=Warmwasser"),
    "cb57b696b815fdef9cb7": ("CTH_READINESS", "LEARNED_WHOLE_CARD", "SHECTHY=temperiert; do not split as CTH grid"),
    "9247e38d29c79a0d2fa5": ("REPETITION", "LEARNED_WHOLE_CARD", "CHEEETY=erste Spülung"),
    "b958a512ca6a3559e86e": ("REPETITION", "LEARNED_WHOLE_CARD", "LKEDY=zweimal waschen; terminal"),
    # Exact-identity traps a real apprentice is likely to over-segment.
    "1779decef17481ec2853": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "QOTEDAIIN=breites Gefäß, not OT+E+DAIIIN"),
    "f3c23f42baf625639e1e": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "CTHAIIN=Kraut zerstoßen, not CTH+AIIN"),
    "2d2e37ccb2dacc53ee5a": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "SOLKAIIN=Seihtuch, not SOLK+AIIN"),
    "834825c61d048a6b5628": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "CHODAIIN=Geschwür, not a stage"),
    "a48efd6c4491a046ba78": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "QOTCHY=zurückbehaltene Blüten, not OT+current item"),
    "62ff059766b21c7de083": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "OTYTCHOL=auffangen, not OT+OL"),
    "3e9c7f217843b588489d": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "RALY=erste Öffnung, not RAL cooling"),
    "4eab1841ed655c20a348": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "SHECKHAL=mäßige Menge, not CHCKHAL duration"),
    "2cc8bb3c2af19607888f": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "CHCKHY=Durchlass, not CHK warmth"),
    "348e81ba084c5acdb32b": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "SHECTHEDCHY=aufstreichen, not SHECTHY tempered"),
    "92e43836d82f98bf02d3": ("EXACT_IDENTITY_TRAP", "COUNTEREXAMPLE", "SHEEY=erste Öffnung, not E/EE grade"),
}


ERROR_BY_KIND = {
    "PRODUCTIVE_GRADE": "E und EE vertauschen oder Y fälschlich als Schluss lesen",
    "PRODUCTIVE_ORDER_GRADE": "OT als Wiederholung statt als Folgeschritt lesen",
    "PRODUCTIVE_ORDER": "OL und OT vertauschen: fortsetzen versus vorrücken",
    "REVISED_SELECTED_CARD": "eine gelernte Hülle produktiv auf nur ähnlich aussehende Karten übertragen",
    "LEARNED_WHOLE_CARD": "die Ganzkarte in erfundene Teilstämme zerlegen",
    "COUNTEREXAMPLE": "nach Oberfläche statt nach exakter Kartenidentität lesen",
}


RIVAL_BY_FAMILY = {
    "IIN_STAGE": "IIN could be an abstract setting rather than a process stage.",
    "CHK_WARMTH": "The four exact cards could be learned states with no productive CHK core.",
    "CTH_READINESS": "CTH may mark release/availability rather than semantic readiness.",
    "SHED_REST": "Formal closure/hold rather than physical resting or settling.",
    "THERMAL_WHOLE_CARD": "A memorized operation whose temperature is supplied by the exemplar.",
    "TIME_WHOLE_CARD": "Quantity or station parameter rather than literal elapsed time.",
    "ENDPOINT_WHOLE_CARD": "Formal setpoint with no physical clarity/settling content.",
    "OL_CONTINUATION": "Formal recurrence link rather than temporal continuation.",
    "OT_OL_ORDER": "Record-order selector rather than chronological succession.",
    "REPETITION_WHOLE_OR_COMPOSITION": "Dittography or emphatic call rather than repeat instruction.",
    "E_GRADE": "Construction-strength grade rather than time/duration.",
    "REPETITION": "Ordinal or variant label rather than repeated performance.",
    "EXACT_IDENTITY_TRAP": "Retained current whole-card value.",
}


def revise_dictionary() -> list[dict[str, str]]:
    fields, rows = read_tsv(DICT_IN)
    extra = [
        "r1_previous_segmentation", "r1_previous_nucleus_de", "r1_previous_gloss_de",
        "r1_thermal_family", "r1_revision_strength", "r1_apprentice_rule", "r1_revision_note",
    ]
    for row in rows:
        ident = row["joint_tuple_id"]
        for key in extra:
            row[key] = "NOT_APPLICABLE"
        if ident in R:
            old = (row["semantic_segmentation"], row["stable_concrete_nucleus_de"], row["concrete_word_reading_de"])
            seg, nucleus, gloss, family, strength, rule, note = R[ident]
            row.update(
                semantic_segmentation=seg,
                stable_concrete_nucleus_de=nucleus,
                concrete_word_reading_de=gloss,
                reading_type="R1_THERMAL_TEMPORAL__" + family,
                local_expansion_examples_de="R1-Lehrmeister: " + CONTEXT[ident],
                variation_note=(row["variation_note"] + "; R1 thermal/temporal: " + note).strip("; "),
                r1_previous_segmentation=old[0],
                r1_previous_nucleus_de=old[1],
                r1_previous_gloss_de=old[2],
                r1_thermal_family=family,
                r1_revision_strength=strength,
                r1_apprentice_rule=rule,
                r1_revision_note=note,
            )
        elif ident in AUDIT:
            family, kind, rule = AUDIT[ident]
            row.update(
                r1_thermal_family=family,
                r1_revision_strength="RETAINED_" + kind,
                r1_apprentice_rule=rule,
                r1_revision_note="Audited without changing the selected medium/substance default.",
            )
        else:
            row.update(r1_thermal_family="OUTSIDE_R1_TARGET", r1_revision_strength="UNCHANGED")
    write_tsv(OUT / "R1_173_DICTIONARY.tsv", fields + extra, rows)
    return rows


def revise_events() -> list[dict[str, str]]:
    fields, rows = read_tsv(EVENT_IN)
    extra = [
        "r1_previous_segmentation", "r1_previous_nucleus_de", "r1_previous_gloss_de", "r1_previous_context_de",
        "r1_thermal_family", "r1_revision_strength", "r1_apprentice_rule", "r1_revision_note",
    ]
    for row in rows:
        ident = row["joint_tuple_id"]
        for key in extra:
            row[key] = "NOT_APPLICABLE"
        if ident in R:
            old = (
                row["semantic_segmentation"], row["stable_concrete_nucleus_de"],
                row["concrete_word_reading_de"], row["contextual_event_reading_de"],
            )
            seg, nucleus, gloss, family, strength, rule, note = R[ident]
            row.update(
                semantic_segmentation=seg,
                stable_concrete_nucleus_de=nucleus,
                concrete_word_reading_de=gloss,
                contextual_event_reading_de=CONTEXT[ident],
                r1_previous_segmentation=old[0],
                r1_previous_nucleus_de=old[1],
                r1_previous_gloss_de=old[2],
                r1_previous_context_de=old[3],
                r1_thermal_family=family,
                r1_revision_strength=strength,
                r1_apprentice_rule=rule,
                r1_revision_note=note,
            )
        elif ident in AUDIT:
            family, kind, rule = AUDIT[ident]
            row.update(
                r1_thermal_family=family,
                r1_revision_strength="RETAINED_" + kind,
                r1_apprentice_rule=rule,
                r1_revision_note="Audited without changing the selected medium/substance reading.",
            )
        else:
            row.update(r1_thermal_family="OUTSIDE_R1_TARGET", r1_revision_strength="UNCHANGED")
    write_tsv(OUT / "R1_381_INTERLINEAR.tsv", fields + extra, rows)
    return rows


def revise_sentences(events: list[dict[str, str]]) -> list[dict[str, str]]:
    fields, rows = read_tsv(SENT_IN)
    by_statement: dict[str, list[dict[str, str]]] = OrderedDict()
    for event in events:
        by_statement.setdefault(event["statement_id"], []).append(event)

    replacements = [
        ("Weiche Sollstufe", "Weiche Stufe"),
        ("Sollstufe", "Stufe"),
        ("Erwärme ihn gelinde", "Wärme ihn an"),
        ("Erwärme sie gelinde", "Wärme sie an"),
        ("Kurz oder mild erwärmen", "Anwärmen"),
        ("Den laufenden Posten länger warm halten", "Den laufenden Posten warmhalten"),
        ("Länger warm halten", "Warmhalten"),
        ("Den laufenden Posten gebrauchsfertig halten", "Den laufenden Posten kurz bereithalten"),
        ("Den laufenden Posten bereit halten", "Den laufenden Posten kurz bereithalten"),
        ("Länger ruhen oder absetzen", "Länger ruhen lassen"),
        ("Ruhen oder absetzen", "Ruhen lassen"),
        ("Ruhe-/Absetzstelle", "Ruhestelle"),
        ("Bevor es abkühlt", "Noch warm"),
        ("vor dem Abkühlen", "noch warm"),
        ("Bis es warm ist", "Bis warm genug"),
        ("Für die vorgeschriebene Zeit stehen lassen", "Stehzeit einhalten"),
        ("bis zum vorgeschriebenen Stand absetzen lassen", "bis zum Absetzstand ruhen lassen"),
        ("Bis zum vorgeschriebenen Stand absetzen lassen", "Bis zum Absetzstand ruhen lassen"),
        ("Bis der Strom klar wird", "Bis zum Klarpunkt führen"),
        ("Danach oder erneut umsetzen", "Danach umsetzen"),
        ("danach oder erneut umsetzen", "danach umsetzen"),
        ("Danach weiter", "Danach fortsetzen"),
        ("mit Vorigem weiter", "mit Vorigem fortsetzen"),
        ("und mit dem vorigen Ansatz weiter", "mit dem vorigen Ansatz fortsetzen"),
        ("Mit dem vorigen Arbeitsgut weiterarbeiten", "Voriges Arbeitsgut fortsetzen"),
        ("Weiterführen; Schluss", "Fortsetzen; Schluss"),
        ("Vorigen Arbeitsgang weiterführen", "Vorigen Arbeitsgang fortsetzen"),
        ("Nächster Ansatz", "Folgeansatz"),
        ("Das nächste Maß", "Folgemaß"),
        ("das nächste Maß", "Folgemaß"),
        ("Danach zur Stelle", "Zur Folgestelle"),
        ("danach zur Stelle", "zur Folgestelle"),
        ("Den nächsten Posten länger einwirken lassen", "Den Folgeposten länger halten"),
        ("Den nächsten Posten wählen", "Den Folgeposten wählen"),
        ("Den laufenden Posten erneut in Arbeit nehmen", "Den laufenden Posten erneut einsetzen"),
        ("Länger mit dem Vorigen fortführen", "Länger fortsetzen"),
        ("Beende diesen Gebrauch", "Fortsetzen; Schluss"),
        ("Gebrauchsfertig", "Bereit"),
        ("gebrauchsfertig", "bereit"),
    ]

    for row in rows:
        statement_events = by_statement[row["statement_id"]]
        old_cards = row["card_sequence_de"]
        old_reading = row["workshop_sentence_de"]
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in statement_events)
        reading = old_reading
        for old, new in replacements:
            reading = reading.replace(old, new)
        if row["statement_id"] == "B4-S010":
            reading = "Fortsetzen; Schluss"
        row["workshop_sentence_de"] = reading
        revised = [event for event in statement_events if event["joint_tuple_id"] in R]
        audited = [event for event in statement_events if event["joint_tuple_id"] in AUDIT]
        row["r1_thermal_revised_event_count"] = str(len(revised))
        row["r1_thermal_audited_event_count"] = str(len(audited))
        row["r1_thermal_families"] = "|".join(sorted({event["r1_thermal_family"] for event in audited})) or "OUTSIDE_R1_TARGET"
        row["r1_previous_card_sequence_de"] = old_cards if revised else "NOT_APPLICABLE"
        row["r1_previous_workshop_sentence_de"] = old_reading if revised else "NOT_APPLICABLE"
    out_fields = fields + [
        "r1_thermal_revised_event_count", "r1_thermal_audited_event_count", "r1_thermal_families",
        "r1_previous_card_sequence_de", "r1_previous_workshop_sentence_de",
    ]
    write_tsv(OUT / "R1_116_SENTENCES.tsv", out_fields, rows)
    return rows


def write_records(sentences: list[dict[str, str]]) -> None:
    groups: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for row in sentences:
        groups.setdefault(row["record_unit_id"], []).append(row)
    lines = [
        "# Elf vollständige Records nach der R1-Wärme-/Zeitrunde",
        "",
        "Lehrmeisterlesung: STUFE, KURZ–LÄNGER–VOLL, WÄRME, BEREIT, RUHE,",
        "FOLGE und FORTSETZUNG sind das kleine Regelwerk; seltene Feuer- und",
        "Zeitwerte bleiben gelernte Ganzkarten. Zeilen sind kein Satzschluss.",
        "",
    ]
    for record, rows in groups.items():
        lines.extend([f"## {record} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            sentence = row["workshop_sentence_de"].rstrip(".") + "."
            lines.append(f"{index}. **{row['statement_id']}** — {sentence}")
        lines.append("")
    (OUT / "R1_11_RECORDS.md").write_text("\n".join(lines), encoding="utf-8")


def write_paradigm(events: list[dict[str, str]], sentences: list[dict[str, str]]) -> int:
    statement_text = {row["statement_id"]: row["workshop_sentence_de"] for row in sentences}
    fields = [
        "family", "inventory_kind", "event_id", "statement_id", "record", "page", "locus",
        "joint_tuple_id", "surface", "selected_segmentation", "short_default_de",
        "contextual_readback_de", "complete_statement_de", "apprentice_copy_rule",
        "likely_apprentice_error", "strongest_rival_or_limit",
    ]
    rows: list[dict[str, str]] = []
    for event in events:
        ident = event["joint_tuple_id"]
        if ident not in AUDIT:
            continue
        family, kind, rule = AUDIT[ident]
        rows.append(
            {
                "family": family,
                "inventory_kind": kind,
                "event_id": event["event_id"],
                "statement_id": event["statement_id"],
                "record": event["record_unit_id"],
                "page": event["page"],
                "locus": event["locus"],
                "joint_tuple_id": ident,
                "surface": event["surface_display"],
                "selected_segmentation": event["semantic_segmentation"],
                "short_default_de": event["concrete_word_reading_de"],
                "contextual_readback_de": event["contextual_event_reading_de"],
                "complete_statement_de": statement_text[event["statement_id"]],
                "apprentice_copy_rule": rule,
                "likely_apprentice_error": ERROR_BY_KIND[kind],
                "strongest_rival_or_limit": RIVAL_BY_FAMILY.get(family, RIVAL_BY_FAMILY.get("EXACT_IDENTITY_TRAP", "Exact-card scope only.")),
            }
        )
    write_tsv(OUT / "R1_PARADIGM.tsv", fields, rows)
    return len(rows)


def validate(dictionary: list[dict[str, str]], events: list[dict[str, str]], sentences: list[dict[str, str]], paradigm_n: int) -> None:
    allowed_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
    required_surfaces = {
        "oiiin|soiiin", "okeey|qokeey", "qokeeedy", "cheky", "cheeky", "chkeey", "chkeedy",
        "checthy|cthy|shcthy", "qcthey|shcthey", "cheedy|shedy|tedy", "sheedy", "schoal",
        "tchody", "chary", "oltchy", "rol", "lol", "shfydaiin", "chckhal", "daiiin",
    }
    dictionary_by_surface = {row["surface_family"]: row for row in dictionary}
    event_by_id = {row["event_id"]: row for row in events}
    ordered_event_ids = [row["event_id"] for row in events]
    statement_event_ids = [event_id for row in sentences for event_id in row["event_ids"].split("|")]
    forbidden_phrases = {
        "vor dem Abkühlen", "bis warm", "für die vorgeschriebene Zeit stehen lassen",
        "bis zum vorgeschriebenen Stand absetzen lassen", "danach oder erneut umsetzen",
    }
    validation = {
        "dictionary_rows": len(dictionary),
        "event_rows": len(events),
        "sentence_rows": len(sentences),
        "record_count": len({row["record_unit_id"] for row in sentences}),
        "revised_types": len(R),
        "revised_events": sum(row["joint_tuple_id"] in R for row in events),
        "audited_types": len(AUDIT),
        "audited_events": paradigm_n,
        "audit_family_event_counts": dict(sorted(Counter(row["r1_thermal_family"] for row in events if row["joint_tuple_id"] in AUDIT).items())),
        "dictionary_empty_defaults": sum(not row["concrete_word_reading_de"].strip() for row in dictionary),
        "event_empty_defaults": sum(not row["contextual_event_reading_de"].strip() for row in events),
        "sentence_empty_defaults": sum(not row["workshop_sentence_de"].strip() for row in sentences),
        "required_surfaces_missing": sorted(required_surfaces - dictionary_by_surface.keys()),
        "pages_outside_scope": sorted({row["page"] for row in events} - allowed_pages),
        "event_binding_exact": ordered_event_ids == statement_event_ids,
        "event_ids_unique": len(event_by_id) == len(events),
        "forbidden_long_target_glosses_remaining": sorted(
            phrase for phrase in forbidden_phrases
            if any(phrase.lower() in row["concrete_word_reading_de"].lower() for row in dictionary if row["joint_tuple_id"] in AUDIT)
        ),
        "sealed_page_mentions_in_data": sum(row["page"] in {"f84", "f84r"} for row in events),
    }
    validation["ok"] = (
        validation["dictionary_rows"] == 173
        and validation["event_rows"] == 381
        and validation["sentence_rows"] == 116
        and validation["record_count"] == 11
        and validation["dictionary_empty_defaults"] == 0
        and validation["event_empty_defaults"] == 0
        and validation["sentence_empty_defaults"] == 0
        and not validation["required_surfaces_missing"]
        and not validation["pages_outside_scope"]
        and validation["event_binding_exact"]
        and validation["event_ids_unique"]
        and not validation["forbidden_long_target_glosses_remaining"]
        and validation["sealed_page_mentions_in_data"] == 0
    )
    (OUT / "R1_VALIDATION.json").write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not validation["ok"]:
        raise SystemExit(json.dumps(validation, ensure_ascii=False))


def main() -> None:
    dictionary = revise_dictionary()
    events = revise_events()
    sentences = revise_sentences(events)
    write_records(sentences)
    paradigm_n = write_paradigm(events, sentences)
    validate(dictionary, events, sentences, paradigm_n)


if __name__ == "__main__":
    main()
