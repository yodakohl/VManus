#!/usr/bin/env python3
"""Build R2's creative thermal/temporal process edition.

Inputs are restricted to the selected medium/substance prose edition.  The
builder reads no manuscript image, no sibling candidate and no sealed page.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_medium_substance_completion"

DICT_IN = SOURCE / "SELECTED_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"

DICT_OUT = HERE / "R2_173_DICTIONARY.tsv"
EVENT_OUT = HERE / "R2_381_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "R2_116_SENTENCES.tsv"
RECORD_OUT = HERE / "R2_11_RECORDS.md"
PARADIGM_OUT = HERE / "R2_PARADIGM.tsv"
SUMMARY_OUT = HERE / "R2_BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sentence_case(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def ov(parse: str, nucleus: str, gloss: str, family: str, note: str) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "R2_THERMAL_TEMPORAL__" + family,
        "family": family,
        "strength": "R2_CREATIVE_WORKING_VALUE",
        "note": note,
    }


# Three independent clocks are kept apart:
#   E/EE/EEE = local working grade; IIN = target grade;
#   OT = following step; OL = continuation from prior material.
# Learned thermal and endpoint cards remain whole cards.
OVERRIDES = {
    # E / EE / EEE: a portable grade contrast whose operation is supplied by
    # the exact host.  E is not always literal clock time.
    "08bd5ca0c2ad137a056d": ov("OK+E_SHORT_GRADE+Y_CURRENT", "OK=ansetzen; E=Kurzgrad; Y=Posten", "kurz anlegen", "E_GRADE", "Contact host supplies laying-on; E supplies only the short/mild grade."),
    "0275fbf14e07935b0a45": ov("OK+EE_HOLD_GRADE+Y_CURRENT", "OK=ansetzen; EE=Haltegrad; Y=Posten", "länger halten", "E_GRADE", "EE supplies sustained grade, not a universal number of hours."),
    "7db18b2f0fb7ed0fcfd3": ov("OK+E_SHORT_GRADE+DY_CLOSE", "OK=einsetzen; E=Kurzgrad; DY=Schluss", "kurz benetzen; Schluss", "E_GRADE", "Wet-contact host supplies benetzen; E remains Kurzgrad."),
    "7d25241b0e56c836372a": ov("OK+EE_HOLD_GRADE+DY_CLOSE", "OK=ansetzen; EE=Haltegrad; DY=Schluss", "länger einwirken; Schluss", "E_GRADE", "EE is the sustained grade across ten liquid, cloth and site cells."),
    "d25110e0d8488927278f": ov("OK+EEE_FULL_GRADE+DY_CLOSE", "OK=einsetzen; EEE=Vollgrad; DY=Schluss", "voll durchtränken; Schluss", "E_GRADE", "EEE supplies completion/fullness inside this saturation host."),
    "c45ebac60774620561e2": ov("OT_FOLLOW+E_SHORT_GRADE+DY_CLOSE", "OT=Folge; E=Kurzgrad; DY=Schluss", "danach kurz einwirken; Schluss", "E_GRADE", "OT orders the step and E supplies its short grade."),
    "5d5e0b288cf36864ed9d": ov("OT_FOLLOW+EE_HOLD_GRADE+Y_CURRENT", "OT=Folge; EE=Haltegrad; Y=Posten", "Folgeposten länger einwirken", "E_GRADE", "The same EE grade applies to the following item."),
    "ff178343c18e287ce3b7": ov("OT_FOLLOW+EE_HOLD_GRADE+DY_CLOSE", "OT=Folge; EE=Haltegrad; DY=Schluss", "danach länger einwirken; Schluss", "E_GRADE", "Following-step order and sustained grade remain separate."),
    "93f69c38fdedee1598e9": ov("OK+EE_HOLD_GRADE+AL_SITE", "OK=einsetzen; EE=Haltegrad; AL=Stelle", "länger an der Stelle halten", "E_GRADE", "The site host supplies location; EE supplies holding grade."),
    "42cdc187d5b9ffc60063": ov("SOLK_COLLECTION+E_SHORT_GRADE+Y_CURRENT", "SOLK=Auffangstelle; E=Kurzgrad; Y=Posten", "kurz auffangen", "E_GRADE", "Collection rather than contact realizes the short grade."),
    "1bfd786e6b8b63734a59": ov("SOLK_COLLECTION+EE_HOLD_GRADE+Y_CURRENT", "SOLK=Auffangstelle; EE=Haltegrad; Y=Posten", "länger auffangen", "E_GRADE", "Collection realizes the sustained grade."),
    "3b70942557b3a40e8030": ov("SOLK_COLLECTION+EE_HOLD_GRADE+DY_CLOSE", "SOLK=Auffangstelle; EE=Haltegrad; DY=Schluss", "länger auffangen; Schluss", "E_GRADE", "Terminal collection preserves the EE grade."),
    "03626ca94cb17800d767": ov("SHED_SETTLE+EE_HOLD_GRADE+DY_CLOSE", "SHED=absetzen; EE=Haltegrad; DY=Schluss", "länger absetzen lassen; Schluss", "SHED_SETTLING", "The liquid-process default is settling, with EE supplying duration grade."),
    "bc4f1f5c006c74a4d26d": ov("SHED_SETTLE+E_SHORT_GRADE+DY_CLOSE", "SHED=absetzen; E=Kurzgrad; DY=Schluss", "absetzen lassen; Schluss", "SHED_SETTLING", "Twelve terminal cells support a default settling step; E is default/short grade."),
    "a84fbe3ad380df345b97": ov("CHK_WARM+EE_HOLD_GRADE+DY_CLOSE", "CHK=wärmen; EE=Haltegrad; DY=Schluss", "warm halten; Schluss", "CHK_THERMAL", "CHK supplies warming and EE sustained heat."),
    "f0db6d30cd34f4cb2a4d": ov("CHK_WARM+EE_HOLD_GRADE+Y_CURRENT", "CHK=wärmen; EE=Haltegrad; Y=Posten", "Posten warm halten", "CHK_THERMAL", "The current item receives sustained warmth."),
    "d904bf7b044dd3922781": ov("CHK_WARM+E_SHORT_GRADE+Y_CONTINUE", "CHK=wärmen; E=Kurzgrad; Y=Posten", "mild wärmen", "CHK_THERMAL", "E realizes the mild/brief warming grade."),
    "2c1a5fd92b9e3c762242": ov("CHK_WARM+EE_HOLD_GRADE+Y_CONTINUE", "CHK=wärmen; EE=Haltegrad; Y=Posten", "warm halten", "CHK_THERMAL", "EE realizes sustained warmth."),
    "6b89d6dd70635bc60fe0": ov("CTH_READY+E_SHORT_GRADE+Y_CURRENT", "CTH=bereit; E=Kurzgrad; Y=Posten", "kurz bereithalten", "CTH_READY", "Readiness is a state; E gives the brief holding grade."),
    "daf32e6db9e04413ce7f": ov("OK+EE_HOLD_GRADE+OL_CONTINUATION", "OK=einsetzen; EE=Haltegrad; OL=Fortsetzung", "länger fortsetzen", "OL_CONTINUATION", "EE supplies sustained grade while OL links to prior work."),

    # IIN is a target grade.  AIIN remains the separate exact MEASURE card.
    "2c82523794dcb7d2b343": ov("IIN_TARGET_GRADE", "IIN=Grad", "Sollgrad", "IIN_GRADE", "The two base carriers name a target grade, not a duration."),
    "409de02322e7b2ca0c62": ov("K_SOFT+IIN_TARGET_GRADE", "K=weich; IIN=Grad", "Weichgrad", "IIN_GRADE", "K supplies softness and IIN the graded target."),
    "fcc1deda9e24ec268eb0": ov("DA_SECOND_OPENING+IIN_TARGET_GRADE", "DA=zweite Öffnung; IIN=Grad", "Öffnungsgrad II", "IIN_GRADE", "The opening hull supplies the station; IIN remains grade."),

    # One short settling root instead of the ambiguous 'rest or settle'.
    "abb23e5e6936b4147f76": ov("SHED_SETTLE+AL_SITE", "SHED=absetzen; AL=Stelle", "Absetzstelle", "SHED_SETTLING", "Two exact events retain the same settling station."),
    "daa1347f456415fe8737": ov("OL_CONTINUATION+SHED_SETTLE+DY_CLOSE", "OL=Fortsetzung; SHED=absetzen; DY=Schluss", "mit dem Vorigen absetzen; Schluss", "SHED_SETTLING", "OL links prior material; SHED supplies settling."),
    "db167f8e9b53eefb58f8": ov("OK_SET+SHED_SETTLE+DY_CLOSE", "OK=anstellen; SHED=absetzen; DY=Schluss", "zum Absetzen stellen; Schluss", "SHED_SETTLING", "OK initiates the settling step."),

    # CTH(Y) is the compact readiness card; SHECTHY remains an indivisible
    # TEMPERED whole card.
    "e0b630cb1b5df5e7105b": ov("CTH_READY+Y_CURRENT", "CTH=bereit; Y=Posten", "bereit", "CTH_READY", "Seven events support a short readiness state without naming its use."),

    # Learned thermal, time and endpoint nomenclator.  No internal stem is
    # exported from these singleton whole cards.
    "2e2027b1951d79911e24": ov("TCHODY_COOL_CLOSE_WHOLE_CARD", "TCHODY=Auskühlen; Schluss", "auskühlen; Schluss", "THERMAL_WHOLE_CARD", "Terminal cooling after the clear extract."),
    "0bdc8b6db811b4e67a63": ov("CHARY_COOL_WHOLE_CARD", "CHARY=Auskühlen", "auskühlen", "THERMAL_WHOLE_CARD", "One nonterminal cooling card; no CH/AR split."),
    "204b04837409088c48f9": ov("OLTCHY_WARM_WHOLE_CARD", "OLTCHY=Anwärmen", "anwärmen", "THERMAL_WHOLE_CARD", "Short learned warming action; it is not OL+TCHY."),
    "e8a6105b5c3a6220b440": ov("QOTCHOL_WARM_WHOLE_CARD", "QOTCHOL=Anwärmen", "anwärmen", "THERMAL_WHOLE_CARD", "Short learned warming action; it is not productive OT or OL."),
    "1496a731803a9f48d2e1": ov("ROL_WARM_STATE_WHOLE_CARD", "ROL=noch warm", "noch warm", "THERMAL_WHOLE_CARD", "A use-state before cooling, not an OL continuation compound."),
    "8c97dfde96fbc78e3355": ov("LOL_HANDWARM_ENDPOINT_WHOLE_CARD", "LOL=handwarm", "handwarm", "THERMAL_WHOLE_CARD", "A target warmth endpoint, not an OL continuation compound."),
    "97cc9ac109148723c472": ov("ODY_COOL_STORE_CLOSE_WHOLE_CARD", "ODY=Kühllager; Schluss", "Kühllager; Schluss", "THERMAL_WHOLE_CARD", "A memorized cool-storage close; no free O=cool claim."),
    "43eb9aa12959b4d5cdc9": ov("QEKEY_RAW_WHOLE_CARD", "QEKEY=roh", "roh", "THERMAL_WHOLE_CARD", "The B6 state is uncooked/raw; visible E is not split as grade."),
    "a8af08e69edab8e54f15": ov("SHFYDAIIN_STANDING_TIME_WHOLE_CARD", "SHFYDAIIN=Standzeit", "Standzeit", "TIME_WHOLE_CARD", "One compact process noun replaces the sentence-sized standing instruction."),
    "d72f71baff01cd0a0406": ov("CHLDAIIN_SETTLING_ENDPOINT_WHOLE_CARD", "CHLDAIIN=Absetzstand", "Absetzstand", "TIME_WHOLE_CARD", "The local endpoint combines settling with a prescribed stand; AIIN is not globally time."),
    "d788d8d72d41b25a3c71": ov("CHEALROR_CLEAR_ENDPOINT_WHOLE_CARD", "CHEALROR=Klarpunkt", "Klarpunkt", "ENDPOINT_WHOLE_CARD", "The card names the observable clear endpoint rather than the sentence 'until clear'."),

    # OT = FOLGE.  Next-item and after-event readings are local realizations of
    # one ordered successor relation.
    "10488b911aae52b3b334": ov("OT_FOLLOW+OR_BATCH", "OT=Folge; OR=Ansatz", "Folgeansatz", "OT_FOLLOW", "OT orders the next batch; OR supplies batch."),
    "497cbd9c7401810ff56b": ov("OT_FOLLOW+OL_CONTINUATION", "OT=Folge; OL=Fortsetzung", "danach fortsetzen", "OT_FOLLOW", "Successor order followed by continuation."),
    "4de12cf322dfb76ded1e": ov("OT_FOLLOW+CHED_TRANSFER+DY_CLOSE", "OT=Folge; CHED=umsetzen; DY=Schluss", "Folgeumsetzung; Schluss", "OT_FOLLOW", "OT supplies ordered succession, CHED the transfer."),
    "54d0e228ca346110af05": ov("OT_FOLLOW+AIIN_MEASURE", "OT=Folge; AIIN=Maß", "Folgemaß", "OT_FOLLOW", "AIIN remains measure; OT makes it the following measure."),
    "601b77449028deed39de": ov("OT_FOLLOW+CHD_TRANSFER+DY_CLOSE", "OT=Folge; CHD=umsetzen; DY=Schluss", "Folgeumsetzung; Schluss", "OT_FOLLOW", "Second exact successor-transfer card."),
    "90bcf0a9ec0ef56399e6": ov("OT_FOLLOW+AL_SITE", "OT=Folge; AL=Stelle", "Folgestelle", "OT_FOLLOW", "The ordered next station."),
    "b6b654722e55729cc947": ov("OT_FOLLOW+AR_SOURCE", "OT=Folge; AR=aus", "Folgeauslass", "OT_FOLLOW", "Ordered outlet step; not a new source substance."),
    "faf321940aed922846a9": ov("OT_FOLLOW+CHEY_CURRENT", "OT=Folge; Y=Posten", "Folgeposten", "OT_FOLLOW", "The following current item."),

    # OL = FORTSETZUNG: reuse/continuation from prior material.
    "1b1ffdd869fb1429ad03": ov("OL_CONTINUATION+DY_CLOSE", "OL=Fortsetzung; DY=Schluss", "fortsetzen; Schluss", "OL_CONTINUATION", "OL carries continuation and DY closes it."),
    "232195d6ff2f326322f7": ov("OK_SET+OL_CONTINUATION", "OK=einsetzen; OL=Fortsetzung", "Fortsetzung einsetzen", "OL_CONTINUATION", "Continuation of the preceding work."),
    "28ffbc88b97772a75f1e": ov("OL_CONTINUATION+CHED_TRANSFER+DY_CLOSE", "OL=Fortsetzung; CHED=führen; DY=Schluss", "fortsetzen; Schluss", "OL_CONTINUATION", "Transfer host realizes the continuation."),
    "322281bd391aa621f568": ov("OK_SET+CH_HULL+OL_CONTINUATION", "OK=in Arbeit setzen; OL=Fortsetzung", "Fortsetzungsstoff", "OL_CONTINUATION", "A short object-name for material retained into the next operation."),
    "94df4847b7b16c98394a": ov("OL_CONTINUATION+AIN_PORTION", "OL=Fortsetzung; AIN=Portion", "Fortsetzungsportion", "OL_CONTINUATION", "An additional portion continuing the same process."),
    "dcda95c81a5460feb191": ov("OL_CONTINUATION", "OL=Fortsetzung", "fortsetzen", "OL_CONTINUATION", "Nineteen events supply the recurrent continuation relation."),
    "d665560c8ff80799a82c": ov("CH_RENDERER+OL_CONTINUATION", "OL=Fortsetzung", "Fortsetzungsposten", "OL_CONTINUATION", "The preceding item retained for continuation."),
    "dec401773c1f0347793d": ov("OL_CONTINUATION+OR_BATCH", "OL=Fortsetzung; OR=Ansatz", "Fortsetzungsansatz", "OL_CONTINUATION", "The prior batch as the batch being continued."),

    # Two learned repetition cards.  Similar first/second-opening cards are
    # already short and are inventoried without alteration.
    "1322bc176443fc2a8a86": ov("OK+OK_REPEAT+CHY_CURRENT", "OK+OK=Wiederansatz; Y=Posten", "Wiederansatz", "REPETITION_WHOLE_CARD", "The doubled work call is shortened to a learned repetition noun."),
    "b958a512ca6a3559e86e": ov("LKEDY_DOUBLE_WASH_CLOSE_WHOLE_CARD", "LKEDY=Doppelwaschung; Schluss", "Doppelwaschung; Schluss", "REPETITION_WHOLE_CARD", "The exact card names repeated washing and closure; no free LKE rule."),
}


CONTEXT_BY_CARD = {
    "1b1ffdd869fb1429ad03": "Fortsetzen; Schluss",
    "03626ca94cb17800d767": "Länger absetzen lassen; Schluss",
    "bc4f1f5c006c74a4d26d": "Absetzen lassen; Schluss",
    "abb23e5e6936b4147f76": "Absetzstelle",
    "daa1347f456415fe8737": "Mit dem Vorigen absetzen lassen; Schluss",
    "db167f8e9b53eefb58f8": "Zum Absetzen stellen; Schluss",
    "6b89d6dd70635bc60fe0": "Den laufenden Posten kurz bereithalten",
    "e0b630cb1b5df5e7105b": "Bereit",
    "2c82523794dcb7d2b343": "Sollgrad",
    "409de02322e7b2ca0c62": "Weichgrad",
    "fcc1deda9e24ec268eb0": "Öffnungsgrad II",
    "2e2027b1951d79911e24": "Auskühlen; Schluss",
    "0bdc8b6db811b4e67a63": "Auskühlen",
    "204b04837409088c48f9": "Anwärmen",
    "e8a6105b5c3a6220b440": "Anwärmen",
    "1496a731803a9f48d2e1": "Noch warm verarbeiten",
    "8c97dfde96fbc78e3355": "Bis handwarm",
    "97cc9ac109148723c472": "Kühl lagern; Schluss",
    "43eb9aa12959b4d5cdc9": "Roh",
    "a8af08e69edab8e54f15": "Standzeit einhalten",
    "d72f71baff01cd0a0406": "Bis zum Absetzstand",
    "d788d8d72d41b25a3c71": "Bis zum Klarpunkt",
    "1322bc176443fc2a8a86": "Den Posten wieder ansetzen",
    "b958a512ca6a3559e86e": "Doppelwaschung; Schluss",
}


# Every active card that carries heat/cooling, grade, readiness, settling,
# explicit duration/endpoint, ordered succession or repetition is inventoried.
# Exact-lookalike controls are included at the end.
INVENTORY_GROUPS = [
    ("01_CONTACT_GRADE", ["08bd5ca0c2ad137a056d", "0275fbf14e07935b0a45", "7db18b2f0fb7ed0fcfd3", "7d25241b0e56c836372a", "d25110e0d8488927278f", "93f69c38fdedee1598e9"]),
    ("02_THERMAL_GRADE", ["d904bf7b044dd3922781", "2c1a5fd92b9e3c762242", "f0db6d30cd34f4cb2a4d", "a84fbe3ad380df345b97"]),
    ("03_COLLECTION_GRADE", ["42cdc187d5b9ffc60063", "1bfd786e6b8b63734a59", "3b70942557b3a40e8030"]),
    ("04_SETTLING_GRADE", ["bc4f1f5c006c74a4d26d", "03626ca94cb17800d767"]),
    ("05_FOLLOW_GRADE", ["c45ebac60774620561e2", "5d5e0b288cf36864ed9d", "ff178343c18e287ce3b7"]),
    ("06_READY_CONTINUE_GRADE", ["6b89d6dd70635bc60fe0", "daf32e6db9e04413ce7f"]),
    ("07_IIN_TARGET_GRADE", ["2c82523794dcb7d2b343", "409de02322e7b2ca0c62", "fcc1deda9e24ec268eb0"]),
    ("08_EXPLICIT_TIME_ENDPOINT", ["a8af08e69edab8e54f15", "21ed2873b71e57269c08", "d72f71baff01cd0a0406", "d788d8d72d41b25a3c71"]),
    ("09_READINESS_STATE", ["e0b630cb1b5df5e7105b", "cb57b696b815fdef9cb7", "43eb9aa12959b4d5cdc9"]),
    ("10_HEAT_COOL_WHOLE_CARD", ["204b04837409088c48f9", "e8a6105b5c3a6220b440", "428a5e3662aa57b4b256", "2e2027b1951d79911e24", "0bdc8b6db811b4e67a63", "4da0f0f7b5fc7ac20067", "1496a731803a9f48d2e1", "8c97dfde96fbc78e3355", "97cc9ac109148723c472", "98bdc4244c84cbef3321", "883a6708116c342cb10b"]),
    ("11_SHED_SETTLING", ["abb23e5e6936b4147f76", "daa1347f456415fe8737", "db167f8e9b53eefb58f8"]),
    ("12_OT_FOLLOW", ["10488b911aae52b3b334", "497cbd9c7401810ff56b", "4de12cf322dfb76ded1e", "54d0e228ca346110af05", "601b77449028deed39de", "90bcf0a9ec0ef56399e6", "b6b654722e55729cc947", "faf321940aed922846a9"]),
    ("13_OL_CONTINUATION", ["1b1ffdd869fb1429ad03", "232195d6ff2f326322f7", "28ffbc88b97772a75f1e", "322281bd391aa621f568", "94df4847b7b16c98394a", "dcda95c81a5460feb191", "d665560c8ff80799a82c", "dec401773c1f0347793d"]),
    ("14_REPETITION", ["1322bc176443fc2a8a86", "b958a512ca6a3559e86e", "9247e38d29c79a0d2fa5"]),
    ("15_OPENING_STAGE", ["3e9c7f217843b588489d", "5eff216ba51fbfb21f22", "92e43836d82f98bf02d3", "a06244ef1f2b37ca44c1", "78b3b3140714da19090d", "f329f2051370174e9a38"]),
    ("16_HERBAL_TIME", ["0ec6a45e2950e8e7061d", "9bb7122b386ebbc6138f"]),
    ("17_EXACT_IDENTITY_CONTROL", ["2f1c5e56e8f0ff459065", "4eab1841ed655c20a348", "62ff059766b21c7de083", "b5df9126607030b95175", "5fca8fc3dee57e1d8c1f", "cbb42a4fe68068325d6b"]),
]


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    if len(dictionary) != 173 or len(events) != 381:
        raise AssertionError("unexpected selected medium/substance dimensions")
    if {row["page"] for row in events} - ALLOWED_PAGES:
        raise AssertionError("input contains a page outside the fixed prose allow-list")
    source_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    inventory_ids = [ident for _, ids in INVENTORY_GROUPS for ident in ids]
    if len(inventory_ids) != len(set(inventory_ids)):
        raise AssertionError("duplicate target in R2 inventory")
    missing = sorted((set(OVERRIDES) | set(inventory_ids)) - set(source_by_id))
    if missing:
        raise AssertionError(f"missing target IDs: {missing}")

    dict_fields = list(dictionary[0]) + [
        "r2_thermal_previous_segmentation",
        "r2_thermal_previous_nucleus_de",
        "r2_thermal_previous_gloss_de",
        "r2_thermal_family",
        "r2_thermal_strength",
        "r2_thermal_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source in dictionary:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["r2_thermal_previous_segmentation"] = row["semantic_segmentation"]
            row["r2_thermal_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["r2_thermal_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Wärme-/Zeitfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] = row.get("variation_note", "") + "; R2 thermal/temporal: " + selected["note"]
            row["r2_thermal_family"] = selected["family"]
            row["r2_thermal_strength"] = selected["strength"]
            row["r2_thermal_note"] = selected["note"]
        else:
            row.update(
                r2_thermal_previous_segmentation="",
                r2_thermal_previous_nucleus_de="",
                r2_thermal_previous_gloss_de="",
                r2_thermal_family="UNCHANGED",
                r2_thermal_strength="UNCHANGED",
                r2_thermal_note="NOT_APPLICABLE",
            )
        revised_dictionary.append(row)
    by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}

    event_fields = list(events[0]) + [
        "r2_thermal_previous_segmentation",
        "r2_thermal_previous_nucleus_de",
        "r2_thermal_previous_gloss_de",
        "r2_thermal_previous_context_de",
        "r2_thermal_family",
        "r2_thermal_strength",
        "r2_thermal_note",
    ]
    revised_events: list[dict[str, str]] = []
    for source in events:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["r2_thermal_previous_segmentation"] = row["semantic_segmentation"]
            row["r2_thermal_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["r2_thermal_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["r2_thermal_previous_context_de"] = row["contextual_event_reading_de"]
            card = by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = CONTEXT_BY_CARD.get(row["joint_tuple_id"], row["contextual_event_reading_de"])
            row["r2_thermal_family"] = selected["family"]
            row["r2_thermal_strength"] = selected["strength"]
            row["r2_thermal_note"] = selected["note"]
        else:
            row.update(
                r2_thermal_previous_segmentation="",
                r2_thermal_previous_nucleus_de="",
                r2_thermal_previous_gloss_de="",
                r2_thermal_previous_context_de="",
                r2_thermal_family="UNCHANGED",
                r2_thermal_strength="UNCHANGED",
                r2_thermal_note="NOT_APPLICABLE",
            )
        revised_events.append(row)

    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    sentence_fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids", "event_ids", "event_count",
        "r2_thermal_revised_event_count", "r2_thermal_families", "surface_sequence", "card_sequence_de",
        "event_slot_trace", "canonical_slots_present", "workshop_sentence_de", "physical_line_note",
    ]
    slot_order = ["OWNER_ITEM", "SOURCE", "QUANTITY", "MEDIUM", "PREPARATION", "TARGET", "OPERATION", "FLOW_TRANSFER", "STATE_GRADE", "CLOSE"]
    sentences: list[dict[str, str]] = []
    for statement_id, rows in grouped.items():
        present = uniq(slot for row in rows for slot in row["workshop_slots"].split("+"))
        sentences.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(uniq([row["field_id"] for row in rows])),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "r2_thermal_revised_event_count": str(sum(row["r2_thermal_family"] != "UNCHANGED" for row in rows)),
                "r2_thermal_families": "|".join(uniq([row["r2_thermal_family"] for row in rows if row["r2_thermal_family"] != "UNCHANGED"])),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "card_sequence_de": " · ".join(row["concrete_word_reading_de"] for row in rows),
                "event_slot_trace": " | ".join(f"{row['event_id']}[{row['workshop_slots']}]" for row in rows),
                "canonical_slots_present": ">".join(slot for slot in slot_order if slot in present),
                "workshop_sentence_de": sentence_case("; ".join(row["contextual_event_reading_de"] for row in rows)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in sentences:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# R2 — elf vollständige Records nach der Wärme-/Zeitrunde",
        "",
        "Kreative Arzt-/Herbal-Werkstattlesung um 1420. E/EE/EEE, IIN, OT und OL bleiben getrennte Prozessachsen.",
        "Gelernte Wärme- und Endpunktkarten werden nicht nach bloßer Zeichenähnlichkeit zerlegt; die Zeile ist kein Satzschluss.",
        "",
    ]
    for record_id, rows in records.items():
        markdown.extend([f"## {record_id} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            markdown.append(f"{index}. **{row['statement_id']}** — {row['workshop_sentence_de']}.")
        markdown.append("")
    RECORD_OUT.write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    event_counts = {ident: 0 for ident in by_id}
    event_ids: dict[str, list[str]] = {ident: [] for ident in by_id}
    statement_ids: dict[str, list[str]] = {ident: [] for ident in by_id}
    pages: dict[str, list[str]] = {ident: [] for ident in by_id}
    for row in revised_events:
        ident = row["joint_tuple_id"]
        event_counts[ident] += 1
        event_ids[ident].append(row["event_id"])
        statement_ids[ident].append(row["statement_id"])
        pages[ident].append(row["page"])

    paradigm_rows: list[dict[str, str]] = []
    source_before = {row["joint_tuple_id"]: row for row in dictionary}
    for group, ids in INVENTORY_GROUPS:
        for ident in ids:
            selected = OVERRIDES.get(ident)
            paradigm_rows.append(
                {
                    "inventory_group": group,
                    "joint_tuple_id": ident,
                    "surface_family": by_id[ident]["surface_family"],
                    "active_before_de": source_before[ident]["concrete_word_reading_de"],
                    "r2_default_de": by_id[ident]["concrete_word_reading_de"],
                    "r2_nucleus_de": by_id[ident]["stable_concrete_nucleus_de"],
                    "occurrences": str(event_counts[ident]),
                    "event_ids": "|".join(event_ids[ident]),
                    "statement_ids": "|".join(uniq(statement_ids[ident])),
                    "pages": "|".join(uniq(pages[ident])),
                    "status": selected["family"] if selected else "INHERITED_OR_EXACT_IDENTITY_CONTROL",
                    "important_limit": selected["note"] if selected else "Retained unchanged; exact identity blocks decomposition by visible resemblance alone.",
                }
            )

    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(SENTENCE_OUT, sentences, sentence_fields)
    write_tsv(PARADIGM_OUT, paradigm_rows, list(paradigm_rows[0]))

    outputs = (DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT)
    changed_cards = [row for row in revised_dictionary if row["r2_thermal_family"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["r2_thermal_family"] != "UNCHANGED"]
    changed_sentences = [row for row in sentences if int(row["r2_thermal_revised_event_count"]) > 0]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_R2_THERMAL_TEMPORAL_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(sentences),
        "records": len(records),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": len(changed_sentences),
        "inventory_rows": len(paradigm_rows),
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
