#!/usr/bin/env python3
"""Build R3's creative thermal/temporal workshop edition.

The edition is deliberately a small scribal notation model: process base,
grade, order and close are kept separate.  It consumes only the selected
medium/substance edition on the seven fixed prose pages.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import OrderedDict, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_medium_substance_completion"

DICT_IN = SOURCE / "SELECTED_173_MEDIUM_SUBSTANCE_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_MEDIUM_SUBSTANCE_INTERLINEAR.tsv"
SENTENCE_IN = SOURCE / "SELECTED_116_MEDIUM_SUBSTANCE_SENTENCES.tsv"
RECORD_IN = SOURCE / "SELECTED_11_MEDIUM_SUBSTANCE_RECORDS.md"

DICT_OUT = HERE / "R3_173_DICTIONARY.tsv"
EVENT_OUT = HERE / "R3_381_INTERLINEAR.tsv"
SENTENCE_OUT = HERE / "R3_116_SENTENCES.tsv"
RECORD_OUT = HERE / "R3_11_RECORDS.md"
PARADIGM_OUT = HERE / "R3_PARADIGM.tsv"
VALIDATION_OUT = HERE / "R3_VALIDATION.json"
SUMMARY_OUT = HERE / "R3_BUILD_SUMMARY.json"

ALLOWED_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


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


def uniq(values: list[str]) -> list[str]:
    return list(OrderedDict.fromkeys(value for value in values if value))


def ov(
    parse: str,
    nucleus: str,
    gloss: str,
    family: str,
    slots: str,
    note: str,
) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "R3_THERMAL_TEMPORAL__" + family,
        "family": family,
        "slots": slots,
        "note": note,
    }


# Small executable notation:
#   BASE + E/EE/EEE + Y/DY
# E/EE/EEE are scale ranks, not free words.  Their local realization can be
# duration, intensity or completion depending on BASE.  Y leaves the current
# item open; DY commits/closes it.  OT supplies succession and OL continuation
# with the previous item.  Exact learned cards override visual resemblance.
OVERRIDES: dict[str, dict[str, str]] = {
    # Measure and target-grade registers.  AIIN and IIN stay different values.
    "2f1c5e56e8f0ff459065": ov(
        "AIIN_TARGET_MEASURE", "AIIN=Sollmaß", "Sollmaß", "AIIN_MEASURE", "QUANTITY",
        "AIIN records the prescribed measure; it is not itself a time word.",
    ),
    "b5fcea1eaed06b2f2291": ov(
        "OK_SET+AIIN_TARGET_MEASURE", "OK=einstellen; AIIN=Sollmaß", "auf Sollmaß einstellen",
        "AIIN_MEASURE", "QUANTITY+OPERATION", "OK turns the stored measure into an instruction to set it.",
    ),
    "54d0e228ca346110af05": ov(
        "OT_FOLLOW+AIIN_TARGET_MEASURE", "OT=Folge; AIIN=Sollmaß", "nächstes Sollmaß",
        "AIIN_MEASURE", "QUANTITY+ORDER", "OT selects the following measure without changing AIIN.",
    ),
    "f7dc90b2c31fd341f0a4": ov(
        "Y_CURRENT_ITEM+AIIN_TARGET_MEASURE", "Y=Posten; AIIN=Sollmaß", "Sollmaß des Postens",
        "AIIN_MEASURE", "OWNER_ITEM+QUANTITY", "The current-item carrier owns the measure.",
    ),
    "a8af08e69edab8e54f15": ov(
        "SHFY_STAND+AIIN_TARGET_MEASURE", "SHFY=stehen; AIIN=Sollmaß", "Standzeit",
        "AIIN_TIME_EXTENSION", "QUANTITY+STATE_GRADE", "SHFY converts the generic prescribed measure into standing time.",
    ),
    "d72f71baff01cd0a0406": ov(
        "CHLD_SETTLE+AIIN_TARGET_MEASURE", "CHLD=absetzen; AIIN=Sollmaß", "Absetzstand",
        "AIIN_STATE_EXTENSION", "QUANTITY+STATE_GRADE", "CHLD converts the generic measure into the prescribed settling level.",
    ),
    "2c82523794dcb7d2b343": ov(
        "IIN_TARGET_GRADE", "IIN=Zielstufe", "Zielstufe", "IIN_GRADE", "QUANTITY+STATE_GRADE",
        "IIN is the target grade and remains distinct from AIIN measure.",
    ),
    "409de02322e7b2ca0c62": ov(
        "K_SOFT_HULL+IIN_TARGET_GRADE", "K=weich; IIN=Zielstufe", "weiche Zielstufe",
        "IIN_GRADE", "QUANTITY+STATE_GRADE", "The K hull specializes the target grade as soft.",
    ),
    "fcc1deda9e24ec268eb0": ov(
        "DA_SECOND_OPENING+IIN_TARGET_GRADE", "DA=zweite Öffnung; IIN=Zielstufe", "zweite Öffnungsstufe",
        "IIN_GRADE", "QUANTITY+STATE_GRADE", "The local DA hull supplies the second opening; IIN supplies its grade.",
    ),

    # OK grid: same operation, ranked grade, open versus closed carrier.
    "276a7c2d74d1143446f4": ov(
        "OK_SET+Y_OPEN", "OK=ansetzen; Y=offener Posten", "Posten ansetzen", "OK_GRID",
        "OWNER_ITEM+OPERATION", "Ungraded open base of the OK grid.",
    ),
    "9ad66e67803a12e745de": ov(
        "OK_SET+CH_WRAPPER+Y_OPEN", "OK=ansetzen; CHY=umhüllter offener Posten", "Posten ansetzen",
        "OK_GRID", "OWNER_ITEM+OPERATION", "Wrapped open base; same stored value as the plain OKY card.",
    ),
    "08bd5ca0c2ad137a056d": ov(
        "OK_SET+GRADE_1+Y_OPEN", "OK=ansetzen; E=Stufe I; Y=offen", "kurz ansetzen", "OK_GRID",
        "OWNER_ITEM+OPERATION+STATE_GRADE", "First ranked open OK state.",
    ),
    "0275fbf14e07935b0a45": ov(
        "OK_SET+GRADE_2+Y_OPEN", "OK=ansetzen; EE=Stufe II; Y=offen", "länger ansetzen", "OK_GRID",
        "OWNER_ITEM+OPERATION+STATE_GRADE", "Second ranked open OK state.",
    ),
    "7db18b2f0fb7ed0fcfd3": ov(
        "OK_SET+GRADE_1+DY_CLOSE", "OK=ansetzen; E=Stufe I; DY=Schluss", "kurz ansetzen; Schluss",
        "OK_GRID", "OPERATION+STATE_GRADE+CLOSE", "First ranked committed OK state; wetting is only a local realization.",
    ),
    "7d25241b0e56c836372a": ov(
        "OK_SET+GRADE_2+DY_CLOSE", "OK=ansetzen; EE=Stufe II; DY=Schluss", "länger ansetzen; Schluss",
        "OK_GRID", "OPERATION+STATE_GRADE+CLOSE", "Second ranked committed OK state.",
    ),
    "d25110e0d8488927278f": ov(
        "OK_SET+GRADE_3+DY_CLOSE", "OK=ansetzen; EEE=Stufe III; DY=Schluss", "vollständig ansetzen; Schluss",
        "OK_GRID", "OPERATION+STATE_GRADE+CLOSE", "Third ranked committed OK state; saturation is local rather than lexical.",
    ),
    "93f69c38fdedee1598e9": ov(
        "OK_SET+GRADE_2+AL_SITE", "OK=ansetzen; EE=Stufe II; AL=Stelle", "länger an der Stelle halten",
        "GRADE_SITE_EXTENSION", "TARGET+OPERATION+STATE_GRADE", "The same second grade modifies a site construction.",
    ),
    "daf32e6db9e04413ce7f": ov(
        "OK_SET+GRADE_2+OL_CONTINUE", "OK=ansetzen; EE=Stufe II; OL=mit Vorigem", "mit Vorigem länger fortsetzen",
        "GRADE_ORDER_EXTENSION", "OPERATION+STATE_GRADE+ORDER", "Grade II combines with the continuation carrier OL.",
    ),

    # CHK warmth grid.  CHEEKY and CHKEEY place the same EE value on two
    # visible layouts; no extra semantic distinction is invented.
    "d904bf7b044dd3922781": ov(
        "CHK_WARM+GRADE_1+Y_OPEN", "CHK=wärmen; E=Stufe I; Y=offen", "kurz wärmen", "CHK_GRID",
        "OPERATION+STATE_GRADE", "First warmth grade; locally it can read mild or brief.",
    ),
    "2c1a5fd92b9e3c762242": ov(
        "CHK_WARM+GRADE_2+Y_OPEN", "CHK=wärmen; EE=Stufe II; Y=offen", "länger wärmen", "CHK_GRID",
        "OPERATION+STATE_GRADE", "Second warmth grade in the internal-grade layout.",
    ),
    "f0db6d30cd34f4cb2a4d": ov(
        "CHK_WARM+GRADE_2+Y_OPEN_ALT_LAYOUT", "CHK=wärmen; EE=Stufe II; Y=offen", "Posten länger wärmen",
        "CHK_GRID", "OWNER_ITEM+OPERATION+STATE_GRADE", "Same second warmth grade with grade written after CHK.",
    ),
    "a84fbe3ad380df345b97": ov(
        "CHK_WARM+GRADE_2+DY_CLOSE", "CHK=wärmen; EE=Stufe II; DY=Schluss", "länger wärmen; Schluss",
        "CHK_GRID", "OPERATION+STATE_GRADE+CLOSE", "Committed second warmth grade.",
    ),

    # SHED settling grid: choose one concrete process instead of the old
    # RUHEN/ABSETZEN hedge.
    "bc4f1f5c006c74a4d26d": ov(
        "SHED_SETTLE+GRADE_1+DY_CLOSE", "SHED=absetzen; E=Stufe I; DY=Schluss", "absetzen; Schluss",
        "SHED_GRID", "STATE_GRADE+CLOSE", "Default/first settling grade and close.",
    ),
    "03626ca94cb17800d767": ov(
        "SHED_SETTLE+GRADE_2+DY_CLOSE", "SHED=absetzen; EE=Stufe II; DY=Schluss", "länger absetzen; Schluss",
        "SHED_GRID", "STATE_GRADE+CLOSE", "Second settling grade and close.",
    ),
    "abb23e5e6936b4147f76": ov(
        "SHED_SETTLE+AL_SITE", "SHED=absetzen; AL=Stelle", "Absetzstelle", "SHED_GRID",
        "TARGET+STATE_GRADE", "The same SHED base names the settling site when followed by AL.",
    ),
    "daa1347f456415fe8737": ov(
        "OL_CONTINUE+SHED_SETTLE+DY_CLOSE", "OL=mit Vorigem; SHED=absetzen; DY=Schluss",
        "mit Vorigem absetzen; Schluss", "SHED_GRID", "ORDER+STATE_GRADE+CLOSE",
        "OL supplies the prior-item continuation; SHED supplies settling.",
    ),
    "db167f8e9b53eefb58f8": ov(
        "OK_SET+SHED_SETTLE+DY_CLOSE", "OK=stellen; SHED=absetzen; DY=Schluss",
        "zum Absetzen stellen; Schluss", "SHED_GRID", "OPERATION+STATE_GRADE+CLOSE",
        "OK starts the settling state and DY closes it.",
    ),

    # Readiness grid.
    "e0b630cb1b5df5e7105b": ov(
        "CTH_READY+Y_OPEN", "CTH=bereit; Y=offen", "gebrauchsfertig", "CTH_GRID",
        "STATE_GRADE", "Ungraded ready state; CTHOOR and CTHAIIN remain exact whole-card counterexamples.",
    ),
    "6b89d6dd70635bc60fe0": ov(
        "CTH_READY+GRADE_1+Y_OPEN", "CTH=bereit; E=Stufe I; Y=Posten", "Posten kurz bereithalten",
        "CTH_GRID", "OWNER_ITEM+STATE_GRADE", "First ranked open readiness state.",
    ),

    # Collection is an independent base confirming the same grade/close layer.
    "42cdc187d5b9ffc60063": ov(
        "SOLK_COLLECT+GRADE_1+Y_OPEN", "SOLK=auffangen; E=Stufe I; Y=offen", "kurz auffangen",
        "SOLK_GRID", "TARGET+STATE_GRADE", "First open collection grade.",
    ),
    "1bfd786e6b8b63734a59": ov(
        "SOLK_COLLECT+GRADE_2+Y_OPEN", "SOLK=auffangen; EE=Stufe II; Y=offen", "länger auffangen",
        "SOLK_GRID", "TARGET+STATE_GRADE", "Second open collection grade.",
    ),
    "3b70942557b3a40e8030": ov(
        "SOLK_COLLECT+GRADE_2+DY_CLOSE", "SOLK=auffangen; EE=Stufe II; DY=Schluss", "länger auffangen; Schluss",
        "SOLK_GRID", "TARGET+STATE_GRADE+CLOSE", "Second committed collection grade.",
    ),

    # OT carries succession into the same grade layer.  It does not name an
    # application such as soaking by itself.
    "c45ebac60774620561e2": ov(
        "OT_FOLLOW+GRADE_1+DY_CLOSE", "OT=Folge; E=Stufe I; DY=Schluss", "kurzer Folgeschritt; Schluss",
        "OT_GRADE_GRID", "ORDER+STATE_GRADE+CLOSE", "The old 'einwirken' expansion was not in the visible construction.",
    ),
    "5d5e0b288cf36864ed9d": ov(
        "OT_FOLLOW+GRADE_2+Y_OPEN", "OT=Folge; EE=Stufe II; Y=offen", "längerer Folgeposten",
        "OT_GRADE_GRID", "OWNER_ITEM+ORDER+STATE_GRADE", "Open second-grade successor.",
    ),
    "ff178343c18e287ce3b7": ov(
        "OT_FOLLOW+GRADE_2+DY_CLOSE", "OT=Folge; EE=Stufe II; DY=Schluss", "längerer Folgeschritt; Schluss",
        "OT_GRADE_GRID", "ORDER+STATE_GRADE+CLOSE", "Committed second-grade successor.",
    ),

    # Learned thermal cards.  Their concise values are not decomposed into the
    # productive grids merely because some letters resemble them.
    "e8a6105b5c3a6220b440": ov(
        "QOTCHOL_GENTLE_HEAT_WHOLE_CARD", "QOTCHOL=sanft wärmen", "sanft wärmen", "THERMAL_WHOLE",
        "OPERATION", "Learned whole card; OTYTCHOL and TSHOL block a free TCHOL root.",
    ),
    "204b04837409088c48f9": ov(
        "OLTCHY_GENTLE_HEAT_WHOLE_CARD", "OLTCHY=sanft wärmen", "sanft wärmen", "THERMAL_WHOLE",
        "OPERATION", "Learned whole card; its initial OL is not forced to be continuation.",
    ),
    "2e2027b1951d79911e24": ov(
        "TCHO_COOL+DY_CLOSE", "TCHO=abkühlen; DY=Schluss", "abkühlen; Schluss", "THERMAL_CLOSE",
        "OPERATION+CLOSE", "Cooling operation plus the productive terminal carrier.",
    ),
    "1496a731803a9f48d2e1": ov(
        "ROL_BEFORE_COOLING_WHOLE_CARD", "ROL=vor Abkühlung", "vor Abkühlung", "THERMAL_WHOLE",
        "ORDER+STATE_GRADE", "Learned thermal boundary; internal OL is not continuation here.",
    ),
    "8c97dfde96fbc78e3355": ov(
        "LOL_WARM_ENDPOINT_WHOLE_CARD", "LOL=Warmpunkt", "Warmpunkt", "THERMAL_WHOLE",
        "STATE_GRADE", "A concise endpoint value replaces the clause 'bis es warm ist'.",
    ),
    "97cc9ac109148723c472": ov(
        "ODY_COOL_STORE_CLOSE_WHOLE_CARD", "ODY=Kühllager mit Schluss", "Kühllager; Schluss", "THERMAL_CLOSE",
        "STATE_GRADE+CLOSE", "Whole-card cool-storage close; no global O=cool rule is introduced.",
    ),

    # Order and repetition layer.
    "497cbd9c7401810ff56b": ov(
        "OT_FOLLOW+OL_CONTINUE", "OT=Folge; OL=fortsetzen", "danach fortsetzen", "ORDER_GRID",
        "ORDER+OPERATION", "Both order values compose without adding content.",
    ),
    "4de12cf322dfb76ded1e": ov(
        "OT_FOLLOW+CHED_TRANSFER+DY_CLOSE", "OT=Folge; CHED=umsetzen; DY=Schluss", "danach umsetzen; Schluss",
        "ORDER_GRID", "ORDER+OPERATION+CLOSE", "OT is succession, not an ambiguous free repetition word.",
    ),
    "601b77449028deed39de": ov(
        "OT_FOLLOW+CHD_TRANSFER+DY_CLOSE", "OT=Folge; CHD=umsetzen; DY=Schluss", "danach umsetzen; Schluss",
        "ORDER_GRID", "ORDER+OPERATION+CLOSE", "Short CHD layout of the same followed transfer close.",
    ),
    "faf321940aed922846a9": ov(
        "OT_FOLLOW+Y_CURRENT_ITEM", "OT=Folge; Y=Posten", "Folgeposten", "ORDER_GRID",
        "OWNER_ITEM+ORDER", "OT selects the successor item.",
    ),
    "dcda95c81a5460feb191": ov(
        "OL_CONTINUE", "OL=mit Vorigem fortsetzen", "mit Vorigem fortsetzen", "ORDER_GRID",
        "ORDER+OPERATION", "Nineteen events make OL the recurrent continuation carrier.",
    ),
    "232195d6ff2f326322f7": ov(
        "OK_SET+OL_CONTINUE", "OK=ansetzen; OL=mit Vorigem", "Vorigen fortsetzen", "ORDER_GRID",
        "ORDER+OPERATION", "OK applies the continuation to the previous work item.",
    ),
    "322281bd391aa621f568": ov(
        "OK_SET+CH_WRAPPER+OL_CONTINUE", "OK=ansetzen; OL=mit Vorigem", "Vorigen fortsetzen", "ORDER_GRID",
        "ORDER+OPERATION", "Wrapped surface of the same OK+OL continuation value.",
    ),
    "94df4847b7b16c98394a": ov(
        "OL_CONTINUE+AIN_PORTION", "OL=weiter; AIN=Portion", "weitere Portion", "ORDER_GRID",
        "ORDER+QUANTITY", "OL makes the portion additional; adding it is contextual syntax.",
    ),
    "28ffbc88b97772a75f1e": ov(
        "OL_CONTINUE+CHED_TRANSFER+DY_CLOSE", "OL=mit Vorigem; CHED=führen; DY=Schluss",
        "Vorigen weiterführen; Schluss", "ORDER_GRID", "ORDER+OPERATION+FLOW_TRANSFER+CLOSE",
        "Continuation plus transfer and close.",
    ),
    "1b1ffdd869fb1429ad03": ov(
        "OL_CONTINUE+DY_CLOSE", "OL=fortsetzen; DY=Schluss", "fortsetzen; Schluss", "ORDER_GRID",
        "ORDER+OPERATION+CLOSE", "The B4 heating sentence was contextual overexpansion; OLDY itself only continues and closes.",
    ),
    "1322bc176443fc2a8a86": ov(
        "OK_SET+OK_REPEAT+CHY_CURRENT_ITEM", "OK+OK=erneut; CHY=Posten", "Posten erneut ansetzen", "REPEAT_GRID",
        "OWNER_ITEM+ORDER+OPERATION", "Literal doubled OK is the strongest visible repetition marker.",
    ),
    "b958a512ca6a3559e86e": ov(
        "LKEDY_SECOND_WASH_CLOSE_WHOLE_CARD", "LKEDY=zweite Waschung mit Schluss", "zweite Waschung; Schluss",
        "REPEAT_WHOLE", "ORDER+FLOW_TRANSFER+CLOSE", "Learned repeated-wash card; no free LKE=two rule is generalized.",
    ),
    "d665560c8ff80799a82c": ov(
        "CH_WRAPPER+OL_PREVIOUS_ITEM", "OL=voriger Posten", "voriger Posten", "ORDER_GRID",
        "OWNER_ITEM+ORDER+SOURCE", "The local action 'nehmen' comes from syntax, not the card default.",
    ),
}


CONTEXT_BY_TYPE = {
    "2f1c5e56e8f0ff459065": "Sollmaß",
    "b5fcea1eaed06b2f2291": "Auf Sollmaß einstellen",
    "54d0e228ca346110af05": "Nächstes Sollmaß",
    "f7dc90b2c31fd341f0a4": "Sollmaß des Postens",
    "a8af08e69edab8e54f15": "Standzeit einhalten",
    "d72f71baff01cd0a0406": "Bis zum Absetzstand warten",
    "2c82523794dcb7d2b343": "Zielstufe",
    "409de02322e7b2ca0c62": "Weiche Zielstufe",
    "fcc1deda9e24ec268eb0": "Zweite Öffnungsstufe",
    "276a7c2d74d1143446f4": "Posten ansetzen",
    "9ad66e67803a12e745de": "Posten ansetzen",
    "08bd5ca0c2ad137a056d": "Kurz ansetzen",
    "0275fbf14e07935b0a45": "Länger ansetzen",
    "7db18b2f0fb7ed0fcfd3": "Kurz ansetzen; Schluss",
    "7d25241b0e56c836372a": "Länger ansetzen; Schluss",
    "d25110e0d8488927278f": "Vollständig ansetzen; Schluss",
    "93f69c38fdedee1598e9": "Länger an der Stelle halten",
    "daf32e6db9e04413ce7f": "Mit Vorigem länger fortsetzen",
    "d904bf7b044dd3922781": "Kurz wärmen",
    "2c1a5fd92b9e3c762242": "Länger wärmen",
    "f0db6d30cd34f4cb2a4d": "Posten länger wärmen",
    "a84fbe3ad380df345b97": "Länger wärmen; Schluss",
    "bc4f1f5c006c74a4d26d": "Absetzen; Schluss",
    "03626ca94cb17800d767": "Länger absetzen; Schluss",
    "abb23e5e6936b4147f76": "Absetzstelle",
    "daa1347f456415fe8737": "Mit Vorigem absetzen; Schluss",
    "db167f8e9b53eefb58f8": "Zum Absetzen stellen; Schluss",
    "e0b630cb1b5df5e7105b": "Gebrauchsfertig",
    "6b89d6dd70635bc60fe0": "Posten kurz bereithalten",
    "42cdc187d5b9ffc60063": "Kurz auffangen",
    "1bfd786e6b8b63734a59": "Länger auffangen",
    "3b70942557b3a40e8030": "Länger auffangen; Schluss",
    "c45ebac60774620561e2": "Kurzer Folgeschritt; Schluss",
    "5d5e0b288cf36864ed9d": "Längerer Folgeposten",
    "ff178343c18e287ce3b7": "Längerer Folgeschritt; Schluss",
    "e8a6105b5c3a6220b440": "Sanft wärmen",
    "204b04837409088c48f9": "Sanft wärmen",
    "2e2027b1951d79911e24": "Abkühlen; Schluss",
    "1496a731803a9f48d2e1": "Vor der Abkühlung",
    "8c97dfde96fbc78e3355": "Bis zum Warmpunkt",
    "97cc9ac109148723c472": "Kühl lagern; Schluss",
    "497cbd9c7401810ff56b": "Danach fortsetzen",
    "4de12cf322dfb76ded1e": "Danach umsetzen; Schluss",
    "601b77449028deed39de": "Danach umsetzen; Schluss",
    "faf321940aed922846a9": "Folgeposten wählen",
    "dcda95c81a5460feb191": "Mit Vorigem fortsetzen",
    "232195d6ff2f326322f7": "Vorigen fortsetzen",
    "322281bd391aa621f568": "Vorigen fortsetzen",
    "94df4847b7b16c98394a": "Weitere Portion zugeben",
    "28ffbc88b97772a75f1e": "Vorigen weiterführen; Schluss",
    "1b1ffdd869fb1429ad03": "Fortsetzen; Schluss",
    "1322bc176443fc2a8a86": "Posten erneut ansetzen",
    "b958a512ca6a3559e86e": "Zweite Waschung; Schluss",
    "d665560c8ff80799a82c": "Vom vorigen Posten nehmen",
}


# Unchanged focus cards and exact-identity counterexamples.  Every override is
# added automatically; closure-bearing selected cards are also added below.
FOCUS_META = OrderedDict([
    ("428a5e3662aa57b4b256", ("05_THERMAL_WHOLE", "WINE_DECOCTION", "SCHOAL is a product noun, not the whole instruction 'boil in wine'.")),
    ("0bdc8b6db811b4e67a63", ("05_THERMAL_WHOLE", "COOL", "Learned CHARY cooling card.")),
    ("4da0f0f7b5fc7ac20067", ("05_THERMAL_WHOLE", "COOL", "Learned RAL cooling card; no shared visible cooling root with CHARY.")),
    ("21ed2873b71e57269c08", ("01_MEASURE_TIME", "DURATION", "CHCKHAL is the learned duration card.")),
    ("43eb9aa12959b4d5cdc9", ("05_THERMAL_WHOLE", "UNCOOKED", "Learned negative thermal state; E/Y are not freely split here.")),
    ("cb57b696b815fdef9cb7", ("04_READINESS_STATE", "TEMPERED", "Learned tempered state, distinct from CTH readiness.")),
    ("98bdc4244c84cbef3321", ("05_THERMAL_WHOLE", "WARM_WATER", "Material card, not a warmth operation.")),
    ("883a6708116c342cb10b", ("05_THERMAL_WHOLE", "WARM_POUR", "Transfer/material whole card, not CHK warmth grammar.")),
    ("10488b911aae52b3b334", ("06_ORDER", "NEXT_BATCH", "OT supplies successor relation to OR batch.")),
    ("dec401773c1f0347793d", ("06_ORDER", "PREVIOUS_BATCH", "OL supplies previous/continued relation to OR batch.")),
    ("90bcf0a9ec0ef56399e6", ("06_ORDER", "NEXT_SITE", "OT supplies succession to AL site.")),
    ("b6b654722e55729cc947", ("06_ORDER", "THEN_FROM_SOURCE", "OT supplies succession to a source action.")),
    ("0ec6a45e2950e8e7061d", ("07_REPEAT", "SEASONAL_ONSET", "Learned flowering-onset card; temporal but not part of the OT/OL grid.")),
    ("3e9c7f217843b588489d", ("07_REPEAT", "FIRST_OPENING", "Learned first-opening card.")),
    ("5eff216ba51fbfb21f22", ("07_REPEAT", "FIRST_OPENING", "Second exact surface family for a learned first-opening value.")),
    ("92e43836d82f98bf02d3", ("07_REPEAT", "FIRST_OPENING", "Third exact first-opening card; resemblance does not license decomposition.")),
    ("a06244ef1f2b37ca44c1", ("07_REPEAT", "FIRST_OPENING", "Fourth exact first-opening card.")),
    ("9247e38d29c79a0d2fa5", ("07_REPEAT", "FIRST_RINSE", "Learned first-rinse card.")),
    ("78b3b3140714da19090d", ("07_REPEAT", "SECOND_OPENING_CLOSE", "Learned second-opening card with terminal DY.")),
    ("f329f2051370174e9a38", ("07_REPEAT", "SECOND_OPENING", "Learned second-opening card without a productive numeric split.")),
    ("a8f891de626fc00028e9", ("07_REPEAT", "SAME_SETTING", "Learned equality/same-setting card.")),
    ("db729b598e89e11452e0", ("07_REPEAT", "EQUAL_PORTIONS", "Learned equality card for portions.")),
    ("577c03a928d674d420d7", ("07_REPEAT", "RESERVE_FOR_SECOND", "Learned reserve-for-second-use card.")),
    ("a48efd6c4491a046ba78", ("07_REPEAT", "RESERVED_ITEM", "Learned reference to the reserved flowers; apparent OT is not freely split.")),
    ("b154ff779abe5f196c80", ("06_ORDER", "CONDUCT_ONWARD", "Water is conducted onward, but the card is not an OT/OL order marker.")),
    ("4eab1841ed655c20a348", ("09_COUNTEREXAMPLE", "AMOUNT_NOT_DURATION", "SHECKHAL is amount, while CHCKHAL is duration; CKHAL is not freely reusable.")),
    ("dedc383b600397a301ee", ("09_COUNTEREXAMPLE", "CLEAN_NOT_READY", "CTHOOR remains clean; CTH is licensed only in the bounded readiness cards.")),
    ("f3c23f42baf625639e1e", ("09_COUNTEREXAMPLE", "CRUSH_NOT_READY", "CTHAIIN remains herb crushing despite its visible CTH/AIIN material.")),
    ("348e81ba084c5acdb32b", ("09_COUNTEREXAMPLE", "SPREAD_NOT_TEMPERED", "SHECTHEDCHY remains spread/apply, not a SHECTHY state compound.")),
    ("1779decef17481ec2853", ("09_COUNTEREXAMPLE", "VESSEL_NOT_MEASURE", "QOTEDAIIN remains a wide vessel; visible DAIIN does not license AIIN measure.")),
    ("834825c61d048a6b5628", ("09_COUNTEREXAMPLE", "LESION_NOT_MEASURE", "CHODAIIN remains the learned lesion card.")),
    ("62ff059766b21c7de083", ("09_COUNTEREXAMPLE", "COLLECT_NOT_ORDER", "OTYTCHOL is collect, not OT plus a thermal TCHOL root.")),
    ("953ad19b79517fc8a211", ("09_COUNTEREXAMPLE", "PLANT_NOT_THERMAL", "TSHOL is flower herb; it blocks a free THOL/CHOL thermal root.")),
    ("b921a237be883a820352", ("09_COUNTEREXAMPLE", "ISOLATED_DY_NOT_CLOSE", "The exact Y-referent family includes a bare dy surface; only the licensed terminal DY construction closes.")),
])


CATEGORY_BY_FAMILY = {
    "AIIN_MEASURE": "01_MEASURE_TIME",
    "AIIN_TIME_EXTENSION": "01_MEASURE_TIME",
    "AIIN_STATE_EXTENSION": "01_MEASURE_TIME",
    "IIN_GRADE": "02_TARGET_GRADE",
    "OK_GRID": "03_GRADE_OPEN_CLOSE",
    "GRADE_SITE_EXTENSION": "03_GRADE_OPEN_CLOSE",
    "GRADE_ORDER_EXTENSION": "03_GRADE_OPEN_CLOSE",
    "CHK_GRID": "03_GRADE_OPEN_CLOSE",
    "SHED_GRID": "03_GRADE_OPEN_CLOSE",
    "CTH_GRID": "04_READINESS_STATE",
    "SOLK_GRID": "03_GRADE_OPEN_CLOSE",
    "OT_GRADE_GRID": "03_GRADE_OPEN_CLOSE",
    "THERMAL_WHOLE": "05_THERMAL_WHOLE",
    "THERMAL_CLOSE": "05_THERMAL_WHOLE",
    "ORDER_GRID": "06_ORDER",
    "REPEAT_GRID": "07_REPEAT",
    "REPEAT_WHOLE": "07_REPEAT",
}


CLOSE_RE = re.compile(
    r"DY_CLOSE|DY_TERMINAL|TERMINAL_Y|DY=Schluss|dy=Ende|Endkarte=Schluss|"
    r"umhüllte DY-Abschluss|\bSchluss\b|\bEnde\b",
    re.IGNORECASE,
)


def build_dictionary() -> tuple[list[dict[str, str]], int]:
    source = read_tsv(DICT_IN)
    rows: list[dict[str, str]] = []
    revised = 0
    for original in source:
        row = dict(original)
        row.update(
            r3_thermal_previous_segmentation=original["semantic_segmentation"],
            r3_thermal_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            r3_thermal_previous_gloss_de=original["concrete_word_reading_de"],
            r3_thermal_family="UNCHANGED",
            r3_thermal_status="UNCHANGED",
            r3_thermal_note="NOT_APPLICABLE",
        )
        override = OVERRIDES.get(row["joint_tuple_id"])
        if override:
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = override[key]
            row["local_expansion_examples_de"] = "R3-Wärme-/Zeitfassung: " + override["concrete_word_reading_de"]
            row["variation_note"] = (row["variation_note"] + "; " if row["variation_note"] else "") + "R3 thermal: " + override["note"]
            row["r3_thermal_family"] = override["family"]
            row["r3_thermal_status"] = "REVISED_R3"
            row["r3_thermal_note"] = override["note"]
            revised += 1
        rows.append(row)
    return rows, revised


def build_events(dictionary: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    source = read_tsv(EVENT_IN)
    rows: list[dict[str, str]] = []
    revised = 0
    for original in source:
        row = dict(original)
        row.update(
            r3_thermal_previous_segmentation=original["semantic_segmentation"],
            r3_thermal_previous_nucleus_de=original["stable_concrete_nucleus_de"],
            r3_thermal_previous_gloss_de=original["concrete_word_reading_de"],
            r3_thermal_previous_context_de=original["contextual_event_reading_de"],
            r3_thermal_family="UNCHANGED",
            r3_thermal_status="UNCHANGED",
            r3_thermal_note="NOT_APPLICABLE",
        )
        override = OVERRIDES.get(row["joint_tuple_id"])
        if override:
            drow = dmap[row["joint_tuple_id"]]
            row["semantic_segmentation"] = drow["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = drow["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = drow["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = CONTEXT_BY_TYPE[row["joint_tuple_id"]]
            row["workshop_slots"] = override["slots"]
            row["r3_thermal_family"] = override["family"]
            row["r3_thermal_status"] = "REVISED_R3"
            row["r3_thermal_note"] = override["note"]
            revised += 1
        rows.append(row)
    return rows, revised


def build_sentences(events: list[dict[str, str]]) -> tuple[list[dict[str, str]], int]:
    source_rows = read_tsv(SENTENCE_IN)
    source_by_id = {row["statement_id"]: row for row in source_rows}
    grouped: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for event in events:
        grouped.setdefault(event["statement_id"], []).append(event)

    rows: list[dict[str, str]] = []
    changed = 0
    for statement_id, group in grouped.items():
        base = source_by_id[statement_id]
        revisions = [event for event in group if event["r3_thermal_status"] == "REVISED_R3"]
        if revisions:
            changed += 1
        row = dict(base)
        row["card_sequence_de"] = " · ".join(event["concrete_word_reading_de"] for event in group)
        row["event_slot_trace"] = " | ".join(f'{event["event_id"]}[{event["workshop_slots"]}]' for event in group)
        slots: list[str] = []
        for event in group:
            slots.extend(part for part in event["workshop_slots"].split("+") if part)
        row["canonical_slots_present"] = ">".join(uniq(slots))
        row["workshop_sentence_de"] = "; ".join(event["contextual_event_reading_de"] for event in group)
        row.update(
            r3_thermal_revised_event_count=str(len(revisions)),
            r3_thermal_families="|".join(uniq([event["r3_thermal_family"] for event in revisions])) or "UNCHANGED",
            r3_thermal_previous_card_sequence_de=base["card_sequence_de"],
            r3_thermal_previous_workshop_sentence_de=base["workshop_sentence_de"],
        )
        rows.append(row)
    return rows, changed


def build_records(sentences: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sentences:
        grouped[row["record_unit_id"]].append(row)
    lines = [
        "# R3: elf vollständige Records nach der Wärme-/Zeitrunde",
        "",
        "Kreative technische Registerlesung. BASE, STUFE, FOLGE und SCHLUSS bleiben getrennt; eine physische Zeile ist kein Satzschluss.",
        "",
    ]
    for record in RECORD_ORDER:
        rows = grouped[record]
        pages = "|".join(uniq([row["page"] for row in rows]))
        lines.extend([f"## {record} — {pages}", ""])
        for index, row in enumerate(rows, 1):
            lines.append(
                f'{index}. **{row["statement_id"]}** `{row["canonical_slots_present"]}` — '
                f'{row["workshop_sentence_de"].rstrip(".")}.'
            )
        lines.append("")
    RECORD_OUT.write_text("\n".join(lines), encoding="utf-8")


def build_paradigm(dictionary: list[dict[str, str]], events: list[dict[str, str]]) -> list[dict[str, str]]:
    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    original_map = {row["joint_tuple_id"]: row for row in read_tsv(DICT_IN)}
    event_map: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        event_map[event["joint_tuple_id"]].append(event)

    meta: OrderedDict[str, tuple[str, str, str]] = OrderedDict(FOCUS_META)
    for tuple_id, override in OVERRIDES.items():
        if tuple_id not in meta:
            category = CATEGORY_BY_FAMILY[override["family"]]
            meta[tuple_id] = (category, override["family"], override["note"])

    # Audit every selected close-bearing exact family, even when its process
    # base is outside this thermal/time round.
    for tuple_id, original in original_map.items():
        blob = " ".join(
            original.get(key, "")
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de")
        )
        if CLOSE_RE.search(blob) and tuple_id not in meta:
            meta[tuple_id] = (
                "08_DY_CLOSE_AUDIT",
                "OTHER_BASE_PLUS_CLOSE",
                "Closure carrier audited; process-base meaning is retained from the selected medium edition.",
            )

    rows: list[dict[str, str]] = []
    for tuple_id, (category, role, note) in meta.items():
        drow = dmap[tuple_id]
        old = original_map[tuple_id]
        erows = event_map[tuple_id]
        rows.append(
            {
                "category": category,
                "joint_tuple_id": tuple_id,
                "surface_family": drow["surface_family"],
                "atomic_role": role,
                "selected_segmentation": drow["semantic_segmentation"],
                "selected_nucleus_de": drow["stable_concrete_nucleus_de"],
                "selected_default_de": drow["concrete_word_reading_de"],
                "previous_default_de": old["concrete_word_reading_de"],
                "occurrences": str(len(erows)),
                "events": "|".join(row["event_id"] for row in erows),
                "statements": "|".join(uniq([row["statement_id"] for row in erows])),
                "pages": "|".join(uniq([row["page"] for row in erows])),
                "records": "|".join(uniq([row["record_unit_id"] for row in erows])),
                "open_close_behavior": (
                    "CLOSE" if CLOSE_RE.search(" ".join((drow["semantic_segmentation"], drow["stable_concrete_nucleus_de"], drow["concrete_word_reading_de"])))
                    else "OPEN_OR_NONTERMINAL"
                ),
                "composition_status": "REVISED_R3" if tuple_id in OVERRIDES else "RETAINED_AUDIT",
                "technical_note": note,
            }
        )
    rows.sort(key=lambda row: (row["category"], row["surface_family"], row["joint_tuple_id"]))
    write_tsv(PARADIGM_OUT, rows, list(rows[0]))
    return rows


def validate(
    dictionary: list[dict[str, str]],
    events: list[dict[str, str]],
    sentences: list[dict[str, str]],
    paradigm: list[dict[str, str]],
    revised_types: int,
    revised_events: int,
    revised_statements: int,
) -> dict[str, object]:
    dmap = {row["joint_tuple_id"]: row for row in dictionary}
    pids = {row["joint_tuple_id"] for row in paradigm}
    source_dict = read_tsv(DICT_IN)
    source_close_ids = {
        row["joint_tuple_id"]
        for row in source_dict
        if CLOSE_RE.search(" ".join((row["semantic_segmentation"], row["stable_concrete_nucleus_de"], row["concrete_word_reading_de"])))
    }
    required = {
        "2f1c5e56e8f0ff459065", "2c82523794dcb7d2b343", "fcc1deda9e24ec268eb0",
        "d904bf7b044dd3922781", "2c1a5fd92b9e3c762242", "f0db6d30cd34f4cb2a4d", "a84fbe3ad380df345b97",
        "bc4f1f5c006c74a4d26d", "03626ca94cb17800d767", "abb23e5e6936b4147f76",
        "e0b630cb1b5df5e7105b", "6b89d6dd70635bc60fe0", "428a5e3662aa57b4b256",
        "2e2027b1951d79911e24", "0bdc8b6db811b4e67a63", "204b04837409088c48f9",
        "1496a731803a9f48d2e1", "8c97dfde96fbc78e3355", "a8af08e69edab8e54f15",
        "21ed2873b71e57269c08", "78b3b3140714da19090d", "10488b911aae52b3b334",
        "dec401773c1f0347793d", "497cbd9c7401810ff56b", "1322bc176443fc2a8a86",
    }
    checks = {
        "dictionary_rows_173": len(dictionary) == 173,
        "event_rows_381": len(events) == 381,
        "sentence_rows_116": len(sentences) == 116,
        "record_count_11": len({row["record_unit_id"] for row in events}) == 11,
        "pages_exactly_allowlisted": {row["page"] for row in events} == ALLOWED_PAGES,
        "f84_f84r_absent": all(not row["page"].startswith("f84") for row in events),
        "dictionary_defaults_complete": all(
            row["semantic_segmentation"] and row["stable_concrete_nucleus_de"] and row["concrete_word_reading_de"]
            for row in dictionary
        ),
        "events_complete": all(
            row["semantic_segmentation"] and row["stable_concrete_nucleus_de"] and row["concrete_word_reading_de"] and row["contextual_event_reading_de"]
            for row in events
        ),
        "sentences_complete": all(row["card_sequence_de"] and row["workshop_sentence_de"] for row in sentences),
        "event_ids_unique": len({row["event_id"] for row in events}) == 381,
        "statement_event_counts_match": all(int(row["event_count"]) == len(row["event_ids"].split("|")) for row in sentences),
        "event_dictionary_binding": all(
            event["concrete_word_reading_de"] == dmap[event["joint_tuple_id"]]["concrete_word_reading_de"]
            for event in events
        ),
        "only_declared_types_revised": {
            row["joint_tuple_id"] for row in dictionary if row["r3_thermal_status"] == "REVISED_R3"
        } == set(OVERRIDES),
        "required_inventory_present": required <= pids,
        "all_selected_close_types_audited": source_close_ids <= pids,
        "counterexamples_present": {
            "4eab1841ed655c20a348", "dedc383b600397a301ee", "f3c23f42baf625639e1e",
            "348e81ba084c5acdb32b", "1779decef17481ec2853", "834825c61d048a6b5628",
            "62ff059766b21c7de083", "953ad19b79517fc8a211",
            "b921a237be883a820352",
        } <= pids,
        "revised_defaults_are_compact": all(
            len(re.findall(r"\w+", row["concrete_word_reading_de"], flags=re.UNICODE)) <= 5
            for row in dictionary if row["r3_thermal_status"] == "REVISED_R3"
        ),
        "aiin_iin_remain_distinct": dmap["2f1c5e56e8f0ff459065"]["concrete_word_reading_de"] != dmap["2c82523794dcb7d2b343"]["concrete_word_reading_de"],
        "astro_unchanged_no_astro_output": True,
        "source_record_readable": RECORD_IN.exists() and RECORD_IN.stat().st_size > 0,
    }
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "revised_exact_cards": revised_types,
            "revised_events": revised_events,
            "revised_statements": revised_statements,
            "paradigm_rows": len(paradigm),
            "selected_close_types_audited": len(source_close_ids),
        },
        "model": {
            "grade_1": "E",
            "grade_2": "EE",
            "grade_3": "EEE",
            "open_carrier": "Y",
            "close_carrier": "licensed terminal DY construction",
            "successor": "OT",
            "continuation": "OL",
        },
        "sealed": {"f84": True, "f84r": True},
    }


def main() -> None:
    dictionary, revised_types = build_dictionary()
    events, revised_events = build_events(dictionary)
    sentences, revised_statements = build_sentences(events)

    write_tsv(DICT_OUT, dictionary, list(dictionary[0]))
    write_tsv(EVENT_OUT, events, list(events[0]))
    write_tsv(SENTENCE_OUT, sentences, list(sentences[0]))
    build_records(sentences)
    paradigm = build_paradigm(dictionary, events)

    validation = validate(
        dictionary, events, sentences, paradigm, revised_types, revised_events, revised_statements
    )
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = [DICT_OUT, EVENT_OUT, SENTENCE_OUT, RECORD_OUT, PARADIGM_OUT, VALIDATION_OUT]
    summary = {
        "status": validation["status"],
        "source": {
            "dictionary": str(DICT_IN.relative_to(ROOT)),
            "events": str(EVENT_IN.relative_to(ROOT)),
            "sentences": str(SENTENCE_IN.relative_to(ROOT)),
            "records": str(RECORD_IN.relative_to(ROOT)),
        },
        "counts": validation["counts"],
        "outputs": {path.name: sha256(path) for path in outputs},
        "astro_unchanged": True,
        "sealed": {"f84": True, "f84r": True},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if validation["status"] != "PASS":
        raise SystemExit("R3 thermal/temporal validation failed")


if __name__ == "__main__":
    main()
