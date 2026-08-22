#!/usr/bin/env python3
"""Build the creative state/endpoint completion over the fixed ten-page sidequest."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import OrderedDict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_quantity_preparation"

DICT_IN = SOURCE / "SELECTED_173_QUANTITY_PREPARATION_DICTIONARY.tsv"
EVENT_IN = SOURCE / "SELECTED_381_QUANTITY_PREPARATION_INTERLINEAR.tsv"
COMPONENT_IN = SOURCE / "SELECTED_QUANTITY_PREPARATION_COMPONENTS.tsv"
UNRESOLVED_IN = SOURCE / "REMAINING_UNRESOLVED_AFTER_QUANTITY.tsv"

DICT_OUT = HERE / "SELECTED_173_STATE_ENDPOINT_DICTIONARY.tsv"
EVENT_OUT = HERE / "SELECTED_381_STATE_ENDPOINT_INTERLINEAR.tsv"
STATEMENT_OUT = HERE / "SELECTED_116_STATE_ENDPOINT_SENTENCES.tsv"
RECORD_OUT = HERE / "SELECTED_11_STATE_ENDPOINT_RECORDS.md"
COMPONENT_OUT = HERE / "SELECTED_STATE_ENDPOINT_COMPONENTS.tsv"
LATTICE_OUT = HERE / "SELECTED_STATE_ENDPOINT_LATTICE.tsv"
COUNTER_OUT = HERE / "STATE_ENDPOINT_COUNTEREXAMPLES.tsv"
UNRESOLVED_OUT = HERE / "REMAINING_UNRESOLVED_AFTER_STATE_ENDPOINT.tsv"
SUMMARY_OUT = HERE / "SELECTED_BUILD_SUMMARY.json"


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


def ov(parse: str, nucleus: str, gloss: str, family: str, strength: str, note: str) -> dict[str, str]:
    return {
        "semantic_segmentation": parse,
        "stable_concrete_nucleus_de": nucleus,
        "concrete_word_reading_de": gloss,
        "reading_type": "SELECTED_STATE_ENDPOINT__" + family,
        "family": family,
        "strength": strength,
        "note": note,
    }


# Exact card identities only.  A visible final ``dy`` is not globally a close:
# the base Y card itself can be rendered ``dy``.  Terminal status is licensed by
# the exact card family and its stable field behaviour.
OVERRIDES = {
    # Named/required state.
    "2c82523794dcb7d2b343": ov("IIN_TARGET_GRADE", "IIN=Sollstufe", "Sollstufe", "IIN_GRADE", "SELECTED_RECURRENT", "The recurrent IIN card names the requested setting, not the amount used to reach it."),
    "409de02322e7b2ca0c62": ov("K_SOFT_HULL+IIN_TARGET_GRADE", "K=weich; IIN=Sollstufe", "weiche Sollstufe", "IIN_GRADE", "SELECTED_SINGLETON_EXTENSION", "The learned soft hull supplies the concrete dimension; IIN still supplies grade."),
    "fcc1deda9e24ec268eb0": ov("DA_OPENING_HULL+IIN_TARGET_GRADE", "DA=zweite Öffnung; IIN=Sollstufe", "zweite Öffnungsstufe", "IIN_GRADE", "SELECTED_SINGLETON_EXTENSION", "The local hull names the aperture while IIN retains the setting contribution."),

    # OK grid: unmarked, brief, sustained and complete exposure; Y continues,
    # while the exact DY cards close the work cell.
    "276a7c2d74d1143446f4": ov("OK+Y_CURRENT_ITEM", "OK=in Arbeit setzen; Y=aktueller Posten", "den laufenden Posten einsetzen", "OK_STATE_GRID", "SELECTED_STRONG", "Ungraded open base of the state grid."),
    "9ad66e67803a12e745de": ov("OK+CHY_WRAPPED_CURRENT_ITEM", "OK=in Arbeit setzen; CHY=umhüllter aktueller Posten", "den laufenden Posten einsetzen", "OK_STATE_GRID", "SELECTED_RECURRENT_WRAPPED_BASE", "The separate OKCHY exact card supplies the second learned surface template of the ungraded base."),
    "08bd5ca0c2ad137a056d": ov("OK+GRADE_1+Y_CURRENT_ITEM", "OK=einsetzen; E=kurz; Y=aktueller Posten", "den laufenden Posten kurz anlegen", "OK_STATE_GRID", "SELECTED_PRODUCTIVE", "Brief open member; water is a possible local medium, not the card meaning."),
    "0275fbf14e07935b0a45": ov("OK+GRADE_2+Y_CURRENT_ITEM", "OK=einsetzen; EE=anhaltend; Y=aktueller Posten", "den laufenden Posten länger einwirken lassen", "OK_STATE_GRID", "SELECTED_PRODUCTIVE", "Sustained open member across four Biological records."),
    "7db18b2f0fb7ed0fcfd3": ov("OK+GRADE_1+DY_CLOSE", "OK=einsetzen; E=kurz; Endkarte=Schluss", "kurz benetzen; Schluss", "OK_STATE_GRID", "SELECTED_PRODUCTIVE", "Brief closed member; all occurrences are complete cells."),
    "7d25241b0e56c836372a": ov("OK+GRADE_2+DY_CLOSE", "OK=einsetzen; EE=anhaltend; Endkarte=Schluss", "länger einweichen; Schluss", "OK_STATE_GRID", "SELECTED_PRODUCTIVE", "Sustained closed member; the owner supplies bath, basin or application."),
    "d25110e0d8488927278f": ov("OK+GRADE_3+DY_CLOSE", "OK=einsetzen; EEE=vollständig; Endkarte=Schluss", "vollständig durchtränken; Schluss", "OK_STATE_GRID", "SELECTED_THIN_TOP_GRADE", "The predicted complete grade has one occurrence."),
    "93f69c38fdedee1598e9": ov("OK+GRADE_2+AL_TARGET", "OK=einsetzen; EE=anhaltend; AL=Zielstelle", "an der Zielstelle länger einwirken lassen", "OK_STATE_EXTENSION", "SELECTED_SINGLETON_EXTENSION", "The target substitutes for Y/DY while the sustained grade remains."),
    "daf32e6db9e04413ce7f": ov("OK+GRADE_2+OL_CONTINUE", "OK=einsetzen; EE=anhaltend; OL=mit dem Vorigen", "länger mit dem Vorigen fortführen", "OK_STATE_EXTENSION", "SELECTED_SINGLETON_EXTENSION", "The continuation argument substitutes for Y/DY."),

    # The same grade operation after OT.
    "c45ebac60774620561e2": ov("OT_NEXT+GRADE_1+DY_CLOSE", "OT=danach; E=kurz; Endkarte=Schluss", "danach kurz einwirken lassen; Schluss", "OT_STATE_GRID", "SELECTED_RECURRENT", "Two short closed members on f83r."),
    "5d5e0b288cf36864ed9d": ov("OT_NEXT+GRADE_2+Y_CURRENT_ITEM", "OT=danach; EE=anhaltend; Y=aktueller Posten", "den nächsten Posten länger einwirken lassen", "OT_STATE_GRID", "SELECTED_RECURRENT", "Two sustained open members on f82r."),
    "ff178343c18e287ce3b7": ov("OT_NEXT+GRADE_2+DY_CLOSE", "OT=danach; EE=anhaltend; Endkarte=Schluss", "danach länger einwirken lassen; Schluss", "OT_STATE_GRID", "SELECTED_RECURRENT", "The sustained close transfers between f82r and f83r."),

    # Ready / fit for use.
    "e0b630cb1b5df5e7105b": ov("CTHY_READY_CARD", "CTHY=gebrauchsfertig", "gebrauchsfertig", "CTH_READY_GRID", "SELECTED_RECURRENT", "Seven uses cross Herbal and Biological records; this is the learned base state, not a forced CTH+Y cut."),
    "6b89d6dd70635bc60fe0": ov("CTH_READY+GRADE_1+Y_CURRENT_ITEM", "CTH=gebrauchsfertig; E=kurz halten; Y=aktueller Posten", "den laufenden Posten gebrauchsfertig halten", "CTH_READY_GRID", "SELECTED_RECURRENT", "A two-page ready-hold extension."),

    # Rest / settle family.
    "bc4f1f5c006c74a4d26d": ov("SHED_REST+GRADE_1+DY_CLOSE", "SHED=ruhen oder absetzen; E=kurz/default; Endkarte=Schluss", "ruhen oder absetzen; Schluss", "SHED_STATE_GRID", "SELECTED_STRONG_LEARNED_FAMILY", "Twelve field-final events share one rest close despite ch/sh/t surface variation."),
    "03626ca94cb17800d767": ov("SHED_REST+GRADE_2+DY_CLOSE", "SHED=ruhen oder absetzen; EE=länger; Endkarte=Schluss", "länger ruhen oder absetzen; Schluss", "SHED_STATE_GRID", "SELECTED_SINGLETON_GRADE", "The sole longer grade precedes an outward transfer."),
    "abb23e5e6936b4147f76": ov("SHED_REST+AL_TARGET", "SHED=ruhen oder absetzen; AL=Stelle", "Ruhe- oder Absetzstelle", "SHED_STATE_EXTENSION", "SELECTED_RECURRENT", "Two f83r records retain the station reading."),
    "db167f8e9b53eefb58f8": ov("OK+SHED_REST+DY_CLOSE", "OK=in Arbeit setzen; SHED=ruhen oder absetzen; Endkarte=Schluss", "zur Ruhe setzen; Schluss", "SHED_STATE_EXTENSION", "SELECTED_SINGLETON_EXTENSION", "The operation calls the learned rest close."),
    "daa1347f456415fe8737": ov("OL_CONTINUE+SHED_REST+DY_CLOSE", "OL=mit dem Vorigen; SHED=ruhen; Endkarte=Schluss", "mit dem Vorigen ruhen lassen; Schluss", "SHED_STATE_EXTENSION", "SELECTED_SINGLETON_COMPOSITION", "The old warmth gloss is replaced by the already selected OL continuation plus SHED rest close."),

    # Warmth family.  CHEKY/CHEEKY and CHKEEY/CHKEEDY are two learned
    # realization templates of one small codebook family, not a global letter
    # segmentation.
    "d904bf7b044dd3922781": ov("CHK_WARM+GRADE_1+Y_CONTINUE", "CHK=wärmen; E=kurz/mild; Weiterführung", "kurz oder mild erwärmen", "CHK_STATE_GRID", "SELECTED_RECURRENT", "Three open/internal occurrences support the mild grade."),
    "2c1a5fd92b9e3c762242": ov("CHK_WARM+GRADE_2+Y_CONTINUE", "CHK=wärmen; EE=länger; Weiterführung", "länger warm halten", "CHK_STATE_GRID", "SELECTED_RECURRENT", "Two pages support the sustained warmth grade."),
    "f0db6d30cd34f4cb2a4d": ov("CHK_WARM+GRADE_2+Y_CURRENT_ITEM", "CHK=wärmen; EE=länger; Y=aktueller Posten", "den laufenden Posten länger warm halten", "CHK_STATE_GRID", "SELECTED_SINGLETON_PREDICTION", "The former broad-vessel gloss is replaced by the predicted open CHK member."),
    "a84fbe3ad380df345b97": ov("CHK_WARM+GRADE_2+DY_CLOSE", "CHK=wärmen; EE=länger; Endkarte=Schluss", "länger warm halten; Schluss", "CHK_STATE_GRID", "SELECTED_SINGLETON_PREDICTION", "The former saturate gloss is replaced by the closed mate of CHKEEY."),

    # Local collection/holding station family.
    "42cdc187d5b9ffc60063": ov("SOLK_COLLECTION+GRADE_1+Y_CURRENT_ITEM", "SOLK=Auffangstelle; E=kurz; Y=aktueller Posten", "den Posten kurz an der Auffangstelle halten", "SOLK_STATE_GRID", "SELECTED_LOCAL_SINGLETON", "Y supplies the item, not openness; the cell merely lacks a close."),
    "1bfd786e6b8b63734a59": ov("SOLK_COLLECTION+GRADE_2+Y_CURRENT_ITEM", "SOLK=Auffangstelle; EE=länger; Y=aktueller Posten", "den Posten länger an der Auffangstelle halten", "SOLK_STATE_GRID", "SELECTED_LOCAL_SINGLETON", "Y supplies the item, not openness; the sustained cell begins B6."),
    "3b70942557b3a40e8030": ov("OLK_SOLK_COLLECTION+GRADE_2+DY_CLOSE", "OLK~SOLK=Auffangstelle; EE=länger; Endkarte=Schluss", "an der Auffangstelle länger halten; Schluss", "SOLK_STATE_GRID", "SELECTED_LOCAL_RECURRENT", "Three terminal events close the same owner-local station family."),

    # Base referent: the visible rendering ``dy`` here is explicitly not a
    # close.  This row prevents a global suffix rewrite.
    "b921a237be883a820352": ov("Y_CURRENT_ITEM_CARD", "Y=aktuell gemeinter Arbeitsposten; dies/es", "dieser Arbeitsposten", "Y_REFERENT", "SELECTED_STRONG", "One exact card has chey/chy/dy/shy/sy/y surfaces; owner context supplies the noun."),
}


LATTICE = [
    ("IIN", "IIN", "Sollstufe", "2c82523794dcb7d2b343", "NAMED_GRADE"),
    ("OK", "OK+Y", "laufenden Posten einsetzen", "276a7c2d74d1143446f4", "OPEN_UNGRADED"),
    ("OK", "OK+CHY", "laufenden Posten einsetzen", "9ad66e67803a12e745de", "OPEN_UNGRADED_WRAPPED"),
    ("OK", "OK+E+Y", "kurz anlegen", "08bd5ca0c2ad137a056d", "OPEN_GRADE_1"),
    ("OK", "OK+EE+Y", "länger einwirken lassen", "0275fbf14e07935b0a45", "OPEN_GRADE_2"),
    ("OK", "OK+E+DY", "kurz benetzen; Schluss", "7db18b2f0fb7ed0fcfd3", "CLOSED_GRADE_1"),
    ("OK", "OK+EE+DY", "länger einweichen; Schluss", "7d25241b0e56c836372a", "CLOSED_GRADE_2"),
    ("OK", "OK+EEE+DY", "vollständig durchtränken; Schluss", "d25110e0d8488927278f", "CLOSED_GRADE_3"),
    ("OT", "OT+E+DY", "danach kurz einwirken; Schluss", "c45ebac60774620561e2", "CLOSED_GRADE_1"),
    ("OT", "OT+EE+Y", "nächsten Posten länger einwirken lassen", "5d5e0b288cf36864ed9d", "OPEN_GRADE_2"),
    ("OT", "OT+EE+DY", "danach länger einwirken; Schluss", "ff178343c18e287ce3b7", "CLOSED_GRADE_2"),
    ("CTH", "CTHY", "gebrauchsfertig", "e0b630cb1b5df5e7105b", "READY_BASE"),
    ("CTH", "CTH+E+Y", "Posten gebrauchsfertig halten", "6b89d6dd70635bc60fe0", "READY_HOLD_OPEN"),
    ("SHED", "SHED+E+DY", "ruhen/absetzen; Schluss", "bc4f1f5c006c74a4d26d", "CLOSED_GRADE_1"),
    ("SHED", "SHED+EE+DY", "länger ruhen/absetzen; Schluss", "03626ca94cb17800d767", "CLOSED_GRADE_2"),
    ("CHK", "CHK+E+Y", "kurz/mild erwärmen", "d904bf7b044dd3922781", "OPEN_GRADE_1"),
    ("CHK", "CHK+EE+Y", "länger warm halten", "2c1a5fd92b9e3c762242", "OPEN_GRADE_2_TEMPLATE_A"),
    ("CHK", "CHK+EE+Y", "Posten länger warm halten", "f0db6d30cd34f4cb2a4d", "OPEN_GRADE_2_TEMPLATE_B"),
    ("CHK", "CHK+EE+DY", "länger warm halten; Schluss", "a84fbe3ad380df345b97", "CLOSED_GRADE_2"),
    ("SOLK", "SOLK+E+Y", "Posten kurz an Auffangstelle halten", "42cdc187d5b9ffc60063", "OPEN_GRADE_1"),
    ("SOLK", "SOLK+EE+Y", "Posten länger an Auffangstelle halten", "1bfd786e6b8b63734a59", "OPEN_GRADE_2"),
    ("SOLK", "SOLK+EE+DY", "an Auffangstelle länger halten; Schluss", "3b70942557b3a40e8030", "CLOSED_GRADE_2"),
    ("Y", "Y", "dieser Arbeitsposten", "b921a237be883a820352", "REFERENT_NOT_CLOSE"),
]


COUNTEREXAMPLES = [
    ("VISIBLE_DY_NOT_GLOBAL_CLOSE", "b921a237be883a820352", "chey|chy|dy|shy|sy|y", "derselbe exakte Y-Posten kann sichtbar dy heißen", "Exact-card identity, not visible dy, licenses closure."),
    ("CHED_NOT_E_GRADE", "6f7ff8287eddf4da9fdb", "chdy|chedy", "CHED ist ein Arbeitskern", "Do not count the e inside CHED as a free grade."),
    ("CHEEY_SHEY_WHOLE", "b5df9126607030b95175", "cheey|shey", "klare Flüssigkeit", "Separate exact card; not EE derived from Y."),
    ("SHEEY_WHOLE", "92e43836d82f98bf02d3", "sheey", "erste Öffnung", "Singleton whole card; no SH+EE+Y promotion."),
    ("CTHAIIN_WHOLE", "f3c23f42baf625639e1e", "cthaiin", "Kraut zerstoßen", "CTH and AIIN are not forced through this learned whole card."),
    ("SHECTHY_WHOLE", "cb57b696b815fdef9cb7", "shecthy", "warmes Wasser", "One occurrence does not license a SHE+CTH ready-fluid composition."),
    ("CHK_TWO_TEMPLATES", "2c1a5fd92b9e3c762242|f0db6d30cd34f4cb2a4d", "cheeky|chkeey", "zwei gelernte offene Warmhalteformen", "Semantic family is shared; visible segmentation is not asserted to be identical."),
    ("SOLK_OWNER_LOCAL", "42cdc187d5b9ffc60063|1bfd786e6b8b63734a59|3b70942557b3a40e8030", "solkey|solkeey|olkeedy|solkeedy", "lokale Auffangstelle", "Do not promote SOLK as a manuscript-wide word outside these exact cards."),
]


def slots_for(row: dict[str, str]) -> str:
    slots = row.get("workshop_slots", "").split("+") if row.get("workshop_slots") else []
    parse = row["semantic_segmentation"].upper()
    gloss = row["concrete_word_reading_de"].lower()
    if "Y_CURRENT_ITEM" in parse or "arbeitsposten" in gloss:
        slots.append("OWNER_ITEM")
    if any(token in parse for token in ("IIN_TARGET_GRADE", "GRADE_", "CTH_READY", "CTHY_READY", "SHED_REST", "CHK_WARM", "SOLK_COLLECTION")):
        slots.append("STATE_GRADE")
    if "AL_TARGET" in parse or "zielstelle" in gloss or "auffangstelle" in gloss:
        slots.append("TARGET")
    if "DY_CLOSE" in parse or "; schluss" in gloss:
        slots.append("CLOSE")
    return "+".join(uniq(slots)) or "OPERATION"


def build_components() -> list[dict[str, str]]:
    rows = read_tsv(COMPONENT_IN)
    changes = {
        "E_GRADE_1": ("e in licensed state frames", "kurze oder milde Einwirkung; erste Arbeitsstufe", "SELECTED_BOUNDED_STATE_GRADE", "OK/OT/SHED/CHK/SOLK exact-card rows", "brief open and closed members recur", "not every visible e"),
        "E_GRADE_2": ("ee in licensed state frames", "anhaltende oder längere Einwirkung; zweite Arbeitsstufe", "SELECTED_BOUNDED_STATE_GRADE", "OK/OT/SHED/CHK/SOLK exact-card rows", "open/closed pairs recur across records", "not an exact time or repetition count"),
        "E_GRADE_3": ("eee in licensed state frames", "vollständige oder durchgehende Einwirkung; dritte Arbeitsstufe", "SELECTED_BOUNDED_STATE_GRADE_THIN", "OK+EEE+DY", "one predicted top-grade member", "one occurrence only"),
        "Y_REFERENT": ("y; licensed chy wrappers", "aktuell gemeinter Arbeitsposten; dies oder es", "FIXED_CONTEXT_BOUND", "exact Y and licensed state grids", "base card plus open grid members", "Y is a referent, not the word open"),
        "DY_TERMINAL_CONSTRUCTION": ("dy only in licensed exact-card terminal frames", "lokalen Arbeitsschritt abschließen", "FIXED_CONTEXT_BOUND", "recognized terminal exact cards", "all selected close members are statement-final", "visible dy can also render the nonterminal base Y card"),
        "SHED_REST_FAMILY": ("cheedy|shedy|tedy; sheedy; shedal", "ruhen oder absetzen", "SELECTED_BOUNDED_STATE_FAMILY", "selected SHED exact cards only", "twelve default closes plus a long close and two stations", "not every visible sh"),
        "CHK_WARMTH_PAIR": ("cheky; cheeky; chkeey; chkeedy", "wärmen oder warm halten", "SELECTED_BOUNDED_STATE_FAMILY", "two learned realization templates", "brief/sustained open and sustained closed readings", "not a global CH or K meaning"),
        "OLK_SOLK_COLLECTION_STATION": ("solkey; solkeey; olkeedy|solkeedy", "lokale Auffang- oder Haltestelle", "SELECTED_LOCAL_STATE_FAMILY", "fixed Biological owners", "brief/sustained open and sustained closed station cards", "owner-local, not a portable universal word"),
        "IIN_GRADE": ("oiiin|soiiin and bounded IIN hulls", "Sollstufe; verlangte Arbeitseinstellung", "FIXED_CONTEXT_BOUND", "exact IIN and learned K/DA extensions", "two recurrent base events plus two extensions", "does not specify whether the dimension is softness, aperture or another setting"),
        "CTH_READY": ("cthy exact family; qcthey|shcthey", "gebrauchsfertig oder bereit", "SELECTED_RECURRENT_STATE_FAMILY", "CTH+Y and CTH+E+Y exact cards", "seven base and two held-ready events", "cthaiin remains a learned whole card"),
    }
    found = set()
    for row in rows:
        if row["component_id"] in changes:
            visible, meaning, status, environment, evidence, limit = changes[row["component_id"]]
            row.update(visible_realizations=visible, working_meaning_de=meaning, status=status, licensed_environment=environment, evidence_summary=evidence, important_limit=limit)
            found.add(row["component_id"])
    missing = set(changes) - found
    if missing:
        raise AssertionError(f"Missing component rows: {sorted(missing)}")
    return rows


def build_unresolved() -> list[dict[str, str]]:
    rows = read_tsv(UNRESOLVED_IN)
    result: list[dict[str, str]] = []
    for row in rows:
        key = row["candidate_component"]
        if key == "OR_INTERNAL_STRINGS":
            row.update(
                current_best_constraint="OR composes in OR OLOR OTCHOR CHOCHOR and ORAIN",
                why_not_closed="YCHE and OYK hulls may merely contain the same surface letters",
                working_default_until_better_model="split selected CHOCHOR, but keep YCHEOR and OYKCHOR whole",
                prediction_that_could_improve_it="another CHO+OR card should retain plant-preparation value",
            )
        elif key == "GLOBAL_E":
            row.update(
                current_best_constraint="bounded state grade in exact OK OT SHED CHK and SOLK families",
                why_not_closed="allography and lexical CHED/CKHE still block a global letter rule",
                working_default_until_better_model="use E/EE/EEE only in the selected lattice",
                prediction_that_could_improve_it="another core should independently fill both Y and terminal cells",
            )
        elif key == "GLOBAL_SH":
            row.update(
                current_best_constraint="bounded SHED rest/settle family",
                why_not_closed="ch/sh/t vary inside one exact card",
                working_default_until_better_model="rest/settle only in selected SHED exact cards",
                prediction_that_could_improve_it="an independent SH base should retain rest value",
            )
        elif key == "GLOBAL_CHK":
            row.update(
                current_best_constraint="bounded CHK warmth family with two learned templates",
                why_not_closed="CHEKY/CHEEKY and CHKEEY/CHKEEDY do not share a literal segmentation",
                working_default_until_better_model="warmth only in four selected CHK cards",
                prediction_that_could_improve_it="a new CHK argument should preserve warmth",
            )
        elif key == "GLOBAL_SOLK":
            row.update(
                current_best_constraint="owner-local graded collection/holding station family",
                why_not_closed="all three exact cards are tied to Biological station owners",
                working_default_until_better_model="Auffangstelle only in selected SOLK/OLK cards",
                prediction_that_could_improve_it="reuse at a second independent owner",
            )
        result.append(row)
    result.extend(
        [
            {"candidate_component": "CTHAIIN_WHOLE_CARD", "current_best_constraint": "CTH is ready and AIIN is measure elsewhere", "why_not_closed": "the lone exact CTHAIIN card has no parallel and the old action reading remains usable", "working_default_until_better_model": "Kraut zerstoßen", "prediction_that_could_improve_it": "a second CTH+measure card should mark a readiness threshold"},
            {"candidate_component": "VISIBLE_DY_GLOBALITY", "current_best_constraint": "closure belongs to licensed exact-card frames", "why_not_closed": "the nonterminal Y card itself can be visibly rendered dy", "working_default_until_better_model": "never close from visible spelling alone", "prediction_that_could_improve_it": "none; exact-card identity remains mandatory"},
            {"candidate_component": "SHECTHY_FLUID_HULL", "current_best_constraint": "a CTH contribution is possible inside a learned fluid card", "why_not_closed": "one event does not identify water oil wine decoction or a ready-state contribution", "working_default_until_better_model": "retain the learned whole card warmes Wasser", "prediction_that_could_improve_it": "another SHE+CTH card should retain a ready-fluid value"},
        ]
    )
    return result


def build() -> dict[str, object]:
    dictionary = read_tsv(DICT_IN)
    events = read_tsv(EVENT_IN)
    source_by_id = {row["joint_tuple_id"]: row for row in dictionary}
    missing = sorted(set(OVERRIDES) - set(source_by_id))
    if missing:
        raise AssertionError(f"Missing override IDs: {missing}")

    dict_fields = list(dictionary[0]) + [
        "state_endpoint_previous_segmentation", "state_endpoint_previous_nucleus_de",
        "state_endpoint_previous_gloss_de", "state_endpoint_revision_family",
        "state_endpoint_revision_strength", "state_endpoint_revision_note",
    ]
    revised_dictionary: list[dict[str, str]] = []
    for source in dictionary:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["state_endpoint_previous_segmentation"] = row["semantic_segmentation"]
            row["state_endpoint_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["state_endpoint_previous_gloss_de"] = row["concrete_word_reading_de"]
            for key in ("semantic_segmentation", "stable_concrete_nucleus_de", "concrete_word_reading_de", "reading_type"):
                row[key] = selected[key]
            row["local_expansion_examples_de"] = "Zustandsfassung: " + selected["concrete_word_reading_de"]
            row["variation_note"] += "; state/endpoint: " + selected["note"]
            row["state_endpoint_revision_family"] = selected["family"]
            row["state_endpoint_revision_strength"] = selected["strength"]
            row["state_endpoint_revision_note"] = selected["note"]
        else:
            row.update(
                state_endpoint_previous_segmentation="", state_endpoint_previous_nucleus_de="",
                state_endpoint_previous_gloss_de="", state_endpoint_revision_family="UNCHANGED",
                state_endpoint_revision_strength="UNCHANGED", state_endpoint_revision_note="NOT_APPLICABLE",
            )
        revised_dictionary.append(row)
    by_id = {row["joint_tuple_id"]: row for row in revised_dictionary}

    event_fields = list(events[0]) + [
        "state_endpoint_previous_segmentation", "state_endpoint_previous_nucleus_de",
        "state_endpoint_previous_gloss_de", "state_endpoint_previous_context_de",
        "state_endpoint_revision_family", "state_endpoint_revision_strength",
    ]
    revised_events: list[dict[str, str]] = []
    for source in events:
        row = dict(source)
        selected = OVERRIDES.get(row["joint_tuple_id"])
        if selected:
            row["state_endpoint_previous_segmentation"] = row["semantic_segmentation"]
            row["state_endpoint_previous_nucleus_de"] = row["stable_concrete_nucleus_de"]
            row["state_endpoint_previous_gloss_de"] = row["concrete_word_reading_de"]
            row["state_endpoint_previous_context_de"] = row["contextual_event_reading_de"]
            card = by_id[row["joint_tuple_id"]]
            row["semantic_segmentation"] = card["semantic_segmentation"]
            row["stable_concrete_nucleus_de"] = card["stable_concrete_nucleus_de"]
            row["concrete_word_reading_de"] = card["concrete_word_reading_de"]
            row["contextual_event_reading_de"] = sentence_case(card["concrete_word_reading_de"])
            row["state_endpoint_revision_family"] = selected["family"]
            row["state_endpoint_revision_strength"] = selected["strength"]
        else:
            row.update(
                state_endpoint_previous_segmentation="", state_endpoint_previous_nucleus_de="",
                state_endpoint_previous_gloss_de="", state_endpoint_previous_context_de="",
                state_endpoint_revision_family="UNCHANGED", state_endpoint_revision_strength="UNCHANGED",
            )
        row["workshop_slots"] = slots_for(row)
        revised_events.append(row)

    grouped: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in revised_events:
        grouped.setdefault(row["statement_id"], []).append(row)
    statement_fields = [
        "statement_id", "record_unit_id", "page", "loci", "field_ids", "event_ids",
        "event_count", "state_revised_event_count", "surface_sequence", "card_sequence_de",
        "event_slot_trace", "canonical_slots_present", "workshop_sentence_de", "physical_line_note",
    ]
    statements: list[dict[str, str]] = []
    slot_order = ["OWNER_ITEM", "SOURCE", "QUANTITY", "PREPARATION", "OPERATION", "FLOW_TRANSFER", "TARGET", "STATE_GRADE", "CLOSE"]
    for statement_id, rows in grouped.items():
        present = uniq(slot for row in rows for slot in row["workshop_slots"].split("+"))
        statements.append(
            {
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "loci": "|".join(uniq([row["locus"] for row in rows])),
                "field_ids": "|".join(uniq([row["field_id"] for row in rows])),
                "event_ids": "|".join(row["event_id"] for row in rows),
                "event_count": str(len(rows)),
                "state_revised_event_count": str(sum(row["state_endpoint_revision_family"] != "UNCHANGED" for row in rows)),
                "surface_sequence": " · ".join(row["surface_display"] for row in rows),
                "card_sequence_de": " · ".join(row["concrete_word_reading_de"] for row in rows),
                "event_slot_trace": " | ".join(f"{row['event_id']}[{row['workshop_slots']}]" for row in rows),
                "canonical_slots_present": ">".join(slot for slot in slot_order if slot in present),
                "workshop_sentence_de": sentence_case("; ".join(row["concrete_word_reading_de"] for row in rows)),
                "physical_line_note": rows[-1]["statement_continuation"],
            }
        )

    records: dict[str, list[dict[str, str]]] = OrderedDict()
    for row in statements:
        records.setdefault(row["record_unit_id"], []).append(row)
    markdown = [
        "# Elf vollständige Records nach Zustands-/Endpunktabschluss",
        "",
        "Die sichtbare Reihenfolge bleibt vollständig erhalten. `Y` bezeichnet den",
        "laufenden Posten; nur eine lizenzierte Endkarte schließt. Zeilen sind kein",
        "Satzschluss.",
        "",
    ]
    for record_id, rows in records.items():
        markdown.extend([f"## {record_id} — {rows[0]['page']}", ""])
        for index, row in enumerate(rows, 1):
            markdown.append(f"{index}. **{row['statement_id']}** `{row['canonical_slots_present']}` — {row['workshop_sentence_de']}.")
        markdown.append("")
    RECORD_OUT.write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")

    components = build_components()
    unresolved = build_unresolved()
    event_counts = {ident: sum(row["joint_tuple_id"] == ident for row in revised_events) for ident in source_by_id}
    lattice_rows = [
        {
            "core_family": family,
            "formula": formula,
            "selected_reading_de": gloss,
            "joint_tuple_id": ident,
            "surface_family": by_id[ident]["surface_family"],
            "events": str(event_counts[ident]),
            "cell_role": role,
            "selection_strength": OVERRIDES[ident]["strength"],
        }
        for family, formula, gloss, ident, role in LATTICE
    ]
    counter_rows = [
        {"counterexample": kind, "joint_tuple_ids": ident, "surface_forms": surface, "retained_reading_de": gloss, "reason": reason}
        for kind, ident, surface, gloss, reason in COUNTEREXAMPLES
    ]

    write_tsv(DICT_OUT, revised_dictionary, dict_fields)
    write_tsv(EVENT_OUT, revised_events, event_fields)
    write_tsv(STATEMENT_OUT, statements, statement_fields)
    write_tsv(COMPONENT_OUT, components, list(components[0]))
    write_tsv(LATTICE_OUT, lattice_rows, list(lattice_rows[0]))
    write_tsv(COUNTER_OUT, counter_rows, list(counter_rows[0]))
    write_tsv(UNRESOLVED_OUT, unresolved, list(unresolved[0]))

    outputs = (DICT_OUT, EVENT_OUT, STATEMENT_OUT, RECORD_OUT, COMPONENT_OUT, LATTICE_OUT, COUNTER_OUT, UNRESOLVED_OUT)
    changed_cards = [row for row in revised_dictionary if row["state_endpoint_revision_family"] != "UNCHANGED"]
    changed_events = [row for row in revised_events if row["state_endpoint_revision_family"] != "UNCHANGED"]
    summary: dict[str, object] = {
        "schema": "SIDEQUEST_SELECTED_STATE_ENDPOINT_SUMMARY_V1",
        "status": "PASS",
        "cards": len(revised_dictionary),
        "events": len(revised_events),
        "statements": len(statements),
        "records": len(records),
        "changed_cards": len(changed_cards),
        "changed_events": len(changed_events),
        "changed_statements": sum(int(row["state_revised_event_count"]) > 0 for row in statements),
        "components": len(components),
        "lattice_rows": len(lattice_rows),
        "counterexamples": len(counter_rows),
        "remaining_unresolved_rows": len(unresolved),
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in (DICT_IN, EVENT_IN, COMPONENT_IN, UNRESOLVED_IN)},
        "outputs": {str(path.relative_to(ROOT)): sha256(path) for path in outputs},
    }
    SUMMARY_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True))
