#!/usr/bin/env python3
"""Build R4's complete, explicitly speculative ten-page default reading.

This sidequest deliberately assigns a concrete default to every selected
surface event.  It is a workshop interpretation, not a decipherment result.
Mixed transcription inputs are filtered by the raw page selector before rows
are materialized; f84/f84r are never selected.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.vmanus_experiment import GuardedTSV


OUT = Path(__file__).resolve().parent
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
ASTRO = {"f67r2", "f68r1", "f69v"}

GDT327 = ROOT / "gdt327_joint_tuple_interlinear.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_native_structural_interlinear_v1.tsv"
ASTRO_SOURCE = ROOT / "transcription/voynich_zl3b_tokens.tsv"

LEXICON = OUT / "V16_R4_COMPLETE_DEFAULT_LEXICON.tsv"
LEDGER = OUT / "V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv"
LINES = OUT / "V16_R4_FLUENT_LINE_READINGS.tsv"
SUMMARY = OUT / "V16_R4_BUILD_SUMMARY.txt"


KNOWN = {
    "b5fcea1eaed06b2f2291": ("take up the next entry", "ENTRY_HEAD", ".68", "One entry/catchword sense across all occurrences."),
    "dcda95c81a5460feb191": ("with it; likewise under the same heading", "CONTINUING_RELATION", ".59", "Missing left argument is inherited at field entry; line-final use carries the relation onward."),
    "2f1c5e56e8f0ff459065": ("in the stated or usual measure", "REFERENCE_STANDARD", ".48", "The active measure may be inherited; no numeral is supplied."),
    "b921a237be883a820352": ("this portion", "CURRENT_PORTION", ".43", "Refers to the locally active portion, preparation, or rubric entry."),
    "e0b630cb1b5df5e7105b": ("when prepared and ready", "READINESS_CONDITION", ".38", "Same readiness phrase in Herbal and application registers."),
    "bc4f1f5c006c74a4d26d": ("set ready in the usual manner; close the rubric", "READY_RESULT_CLOSE", ".34", "VAL-S; the final clause includes the attached local close."),
    "7d25241b0e56c836372a": ("use the tempered warm medium; close the rubric", "WARM_MEDIUM_CLOSE", ".31", "VAL-QE; one concrete default for all ten occurrences."),
    "de7321bface5628e35d6": ("leave at the ordinary base setting; close the rubric", "BASE_SETTING_CLOSE", ".30", "VAL-Q; base configuration, not a numeral."),
    "7db18b2f0fb7ed0fcfd3": ("rinse or pour over the local place; close the rubric", "LOCAL_RINSE_CLOSE", ".27", "VAL-L; local carried application."),
    "2cc054357a929df85f64": ("thereafter", "PROSE_CONTINUATION", ".30", "f56r early-line recurrence; ordinary resumptive adverb, not a page title."),
    "4d4559019a961b834aa1": ("of the same", "PROSE_REFERENCE", ".29", "Ordinary resumptive phrase; no privileged topic ownership."),
    "6f7ff8287eddf4da9fdb": ("mix until even", "MIXING_ACTION", ".31", "Recurrent open Biological action; f55v use is the same preparation instruction."),
    "276a7c2d74d1143446f4": ("use the lesser portion", "QUANTITY_INSTRUCTION", ".29", "Portable open card; lesser is a relative, not numeric, measure."),
    "dd0ecaf5e27d81befffc": ("at the indicated place", "LOCAL_REFERENCE", ".29", "Mobile locative reference shared across applications and one Herbal clause."),
    "0275fbf14e07935b0a45": ("keep gently warmed", "PROCESS_CONDITION", ".29", "Recurrent Biological process instruction."),
    "1645e612504fcef59ced": ("then put it in", "TRANSFER_ACTION", ".31", "Field-entry-biased but permits interior continuation."),
    "7a4bb8136330ee4e6e56": ("the prepared liquid", "WORKING_LIQUID", ".28", "Portable Herbal/Biological material phrase."),
    "308e8ea2d5d190c498e8": ("combine the two portions", "COMBINATION_ACTION", ".29", "Recurrent cross-page application instruction."),
    "259b2b3b0bf859882e2c": ("finish this application; close the rubric", "APPLICATION_CLOSE", ".28", "Recurrent short committed cell."),
    "2cc8bb3c2af19607888f": ("through the joined channels", "CHANNEL_CONFIGURATION", ".26", "CKHY-family concrete default; not the rejected leaf gloss."),
    "b5df9126607030b95175": ("until it becomes clear", "CLARITY_CONDITION", ".25", "Open condition shared across records."),
    "28ffbc88b97772a75f1e": ("retain the combined mixture; close the rubric", "MIXTURE_CLOSE", ".27", "Three-page recurrent committed answer."),
    "3b70942557b3a40e8030": ("let it settle; close the rubric", "SETTLING_CLOSE", ".27", "Recurrent committed result."),
    "54d0e228ca346110af05": ("for the same duration", "DURATION_REFERENCE", ".25", "Three Biological occurrences."),
    "87411f84689b4f93a303": ("heat once; close the rubric", "HEATING_CLOSE", ".26", "Recurrent committed operation."),
    "90bcf0a9ec0ef56399e6": ("toward the lower outlet", "DIRECTION_REFERENCE", ".24", "f83r local routing phrase."),
    "9ad66e67803a12e745de": ("use the fresh preparation", "FRESH_PREPARATION", ".26", "Herbal-open instruction crossing two dossiers."),
    "9da1b6ac2c929daea697": ("one measured share", "MEASURED_SHARE", ".25", "Mobile count/portion phrase."),
    "d68bc8de3bcee09db23c": ("strain completely; close the rubric", "STRAINING_CLOSE", ".26", "Repeated committed action."),
    "d904bf7b044dd3922781": ("at gentle heat", "HEAT_QUALIFIER", ".25", "Recurrent Biological qualifier."),
}


COMMON_FIRST = [
    "then take", "next add", "put this with", "continue with", "use again",
    "prepare also", "for the next part", "afterward pour", "begin this remedy",
    "mark the following share", "take from the foregoing", "set beside it",
]
COMMON_MIDDLE = [
    "and mix", "with clean water", "in the vessel", "for the affected place",
    "for one measured interval", "from the foregoing batch", "until evenly joined",
    "as written above", "the second portion", "the first portion", "with warmed oil",
    "with wine", "with the expressed juice", "through the opening", "over a gentle fire",
    "after it has settled", "while still warm", "twice in succession",
]
COMMON_LAST = [
    "and retain it", "until the next use", "for the stated time", "then let it rest",
    "and keep it covered", "for use at the place", "as above", "then proceed onward",
]

HERBAL_FIRST = [
    "the pictured simple is called local-name-A", "the pictured simple is called local-name-B",
    "its root is", "its leaves are", "it is found in", "gather it in spring",
    "for preparation take", "for its medicinal use", "dry the pictured plant",
    "pound the pictured plant", "its flower appears", "its seed is",
]
HERBAL_MIDDLE = [
    "a branching root", "broad leaves", "narrow leaves", "a reddish stem",
    "a pale flower", "dark seed", "moist ground", "beside running water",
    "shaded woodland", "stony soil", "the fresh root", "the dried leaf",
    "the expressed juice", "a handful", "clean water", "white wine",
    "olive oil", "honey", "vinegar", "pounded to powder", "boiled gently",
    "steeped overnight", "strained through cloth", "laid upon a wound",
    "drunk for stomach pain", "used against swelling", "applied while warm",
    "kept in a covered jar", "gathered before flowering", "the upper shoots",
    "the lower root", "a bitter taste", "a cooling quality", "a drying quality",
]
HERBAL_LAST = [
    "and it grows by water", "and dry it in shade", "and keep the root",
    "and strain the decoction", "and drink it morning and evening",
    "and bind it upon the swelling", "and preserve it in oil", "and use it fresh",
    "and this completes the plant note", "and repeat the dose twice",
]

BIO_FIRST = [
    "take the prepared bath", "next open the upper channel", "then fill the vessel",
    "place the person at the basin", "pour in the warmed water", "begin the rinsing",
    "close the lower outlet", "let the mixture enter", "apply at the marked place",
    "continue at the second conduit", "draw off the clear liquid", "repeat the washing",
]
BIO_MIDDLE = [
    "the upper basin", "the lower basin", "the joined conduit", "the narrow outlet",
    "the broad vessel", "warm water", "cool water", "the prepared oil",
    "the affected place", "the immersed part", "the returning flow", "the first opening",
    "the second opening", "a moderate quantity", "for one interval", "until warm",
    "until clear", "after settling", "with the foregoing mixture", "under the same setting",
    "gently", "in equal portions", "through a cloth", "toward the lower vessel",
    "over the local place", "without boiling", "before it cools", "after the first rinse",
]
BIO_LAST = [
    "then hold it there", "until the flow clears", "and let it cool",
    "then use the lower outlet", "and repeat once", "for the stated duration",
    "then cover the vessel", "and proceed to the next basin", "at the indicated place",
]

COMMITTED = [
    "immerse fully; close the rubric", "wash once; close the rubric",
    "wash twice; close the rubric", "let it cool; close the rubric",
    "keep it warm; close the rubric", "strain it clear; close the rubric",
    "set aside overnight; close the rubric", "apply locally; close the rubric",
    "draw it off; close the rubric", "cover the vessel; close the rubric",
    "use immediately; close the rubric", "retain the residue; close the rubric",
    "repeat at the second opening; close the rubric", "leave the outlet open; close the rubric",
    "stop the flow; close the rubric", "mix in equal shares; close the rubric",
    "add clean water; close the rubric", "add warmed oil; close the rubric",
    "pound finely; close the rubric", "boil gently; close the rubric",
    "steep until clear; close the rubric", "dry in shade; close the rubric",
    "bind upon the place; close the rubric", "drink the stated portion; close the rubric",
]


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, data: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(data)


def choose(pool: list[str], key: str, offset: int = 0) -> str:
    return pool[(int(key[:12], 16) + offset) % len(pool)]


def derive_card_gloss(tid: str, occ: list[dict]) -> tuple[str, str, str, str]:
    if tid in KNOWN:
        return KNOWN[tid]
    pages = {x["page"] for x in occ}
    herbal = all(x in {"f10r", "f11r", "f55v", "f56r"} for x in pages)
    bio = all(x in {"f81v", "f82r", "f83r"} for x in pages)
    close = sum(x["dy_closure"] == "1" or x["b3"] == "1" for x in occ) / len(occ)
    positions = Counter(x["within_field_position"] for x in occ)
    recurrent = len(occ) > 1
    if close >= .5:
        gloss = choose(COMMITTED, tid)
        cls = "COMMITTED_TECHNICAL_INSTRUCTION"
    elif positions["FIRST"] + positions["ONLY"] > len(occ) / 2:
        pool = HERBAL_FIRST if herbal else BIO_FIRST if bio else COMMON_FIRST
        gloss = choose(pool, tid)
        cls = "HERBAL_CLAUSE_HEAD" if herbal else "APPLICATION_CLAUSE_HEAD" if bio else "PORTABLE_CLAUSE_HEAD"
    elif positions["LAST"] > len(occ) / 2:
        pool = HERBAL_LAST if herbal else BIO_LAST if bio else COMMON_LAST
        gloss = choose(pool, tid)
        cls = "HERBAL_CLAUSE_END" if herbal else "APPLICATION_CLAUSE_END" if bio else "PORTABLE_CLAUSE_END"
    else:
        pool = HERBAL_MIDDLE if herbal else BIO_MIDDLE if bio else COMMON_MIDDLE
        gloss = choose(pool, tid)
        cls = "HERBAL_PHRASE" if herbal else "APPLICATION_PHRASE" if bio else "PORTABLE_TECHNICAL_PHRASE"
    if "local-name-" in gloss:
        gloss = gloss.rsplit("local-name-", 1)[0] + "local-name-" + tid[:5].upper()
    confidence = ".24" if recurrent else ".16"
    rule = "Fixed exact-card default across all selected occurrences."
    if not recurrent:
        rule = "CONTEXT_DEFAULT: page/register and field ecology select this low-confidence expansion."
    return gloss, cls, confidence, rule


def astro_locus_role(page: str, locus_no: int, kind: str) -> tuple[str, int]:
    if page == "f67r2":
        if 1 <= locus_no <= 12:
            return "ZODIAC_DIVISION", locus_no
        seven = [15, 22, 28, 31, 34, 37, 47]
        if locus_no in seven:
            return "SEVENFOLD_GOVERNOR", seven.index(locus_no) + 1
        if 52 <= locus_no <= 63:
            return "ASTROLOGICAL_HOUSE", locus_no - 51
        if 64 <= locus_no <= 71:
            return "CENTRAL_CONDITION_SECTOR", locus_no - 63
        return "SELECTOR_RULE_PROSE", locus_no
    if page == "f68r1":
        if locus_no == 8:
            return "CENTRAL_LUNAR_OWNER", 0
        if 9 <= locus_no <= 36:
            return "SPATIAL_LUNAR_STATION", locus_no - 8
        if locus_no == 37:
            return "CENTRAL_CATALOGUE_LEGEND", 0
        return "CATALOGUE_INSTRUCTION", locus_no
    if 4 <= locus_no <= 31:
        return "ORDERED_LUNAR_SCHEDULE_LOCUS", locus_no - 3
    return "SCHEDULE_RULE_PROSE", locus_no


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PLANETS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
HOUSES = ["life and body", "goods and wealth", "siblings and messages", "home and land", "children and pleasure", "illness and service", "marriage and partners", "death and inheritance", "journeys and learning", "office and dignity", "friends and aid", "confinement and hidden enemies"]
SECTORS = ["hot and dry", "warm and dry", "warm and moist", "hot and moist", "cold and moist", "cool and moist", "cool and dry", "cold and dry"]

RULE_WORDS = [
    "choose", "the governing influence", "for this division", "when the Moon enters",
    "use the indicated remedy", "avoid bleeding", "favour washing", "favour purging",
    "apply while warm", "wait until the next station", "with the usual measure",
    "under the same governor", "at night", "in the morning", "for the sick person",
    "at the affected place", "repeat once", "do not overheat", "let it settle",
    "then proceed", "the favourable condition", "the adverse condition", "as written above",
]


def astro_gloss(page: str, locus_no: int, kind: str, token_index: int) -> tuple[str, str, str, str]:
    role, n = astro_locus_role(page, locus_no, kind)
    if role == "ZODIAC_DIVISION":
        vals = [f"zodiac division {n}: {SIGNS[n-1]}", "its ruling quality", "its application rule"]
        return vals[min(token_index - 1, 2)], role, ".30", "Label role is inherited from the drawn twelvefold selector locus."
    if role == "SEVENFOLD_GOVERNOR":
        return f"sevenfold governor {n}: {PLANETS[n-1]}", role, ".29", "Sevenfold label; conventional planet order is the R4 default wager."
    if role == "ASTROLOGICAL_HOUSE":
        vals = [f"house {n}: {HOUSES[n-1]}", "its permitted application", "its warning"]
        return vals[min(token_index - 1, 2)], role, ".25", "Twelvefold secondary label expanded as an astrological house locus."
    if role == "CENTRAL_CONDITION_SECTOR":
        return f"central condition sector {n}: {SECTORS[n-1]}", role, ".22", "Spatially owned eightfold central condition; no phonetic reading."
    if role == "SELECTOR_RULE_PROSE":
        return RULE_WORDS[(locus_no + token_index - 2) % len(RULE_WORDS)], role, ".18", "CONTEXT_DEFAULT: running selector instruction, source order retained."
    if role == "CENTRAL_LUNAR_OWNER":
        return "the Moon governing the twenty-eight stations", role, ".32", "Central owner, not the start of the surrounding catalogue."
    if role == "SPATIAL_LUNAR_STATION":
        return f"noncentral lunar station at source locus {page}.{locus_no}", role, ".30", "Spatial catalogue identity only; explicitly no authorial cyclic start."
    if role == "CENTRAL_CATALOGUE_LEGEND":
        vals = ["the Moon", "governs", "the whole circuit", "of twenty-eight", "lunar stations"]
        return vals[min(token_index - 1, 4)], role, ".25", "Five-part centre legend default."
    if role == "CATALOGUE_INSTRUCTION":
        pool = ["identify", "the lunar station", "by its drawn place", "and consult its rule", "without changing the catalogue order"]
        return pool[(locus_no + token_index - 2) % len(pool)], role, ".18", "CONTEXT_DEFAULT: catalogue instruction prose."
    if role == "ORDERED_LUNAR_SCHEDULE_LOCUS":
        polarity = "favour the named application" if n % 2 else "withhold the named application"
        vals = [f"schedule station {n}: {polarity}", "repeat the station rule"]
        return vals[min(token_index - 1, 1)], role, ".27", "Source locus order retained; alternation rendered as perform/withhold advice."
    pool = ["when the Moon reaches the station", "inspect the pictured schedule", "if the condition is favourable", "apply the remedy", "if adverse, withhold it", "keep the usual measure", "continue to the next station", "repeat only once", "close the consultation"]
    return pool[(locus_no * 3 + token_index - 1) % len(pool)], role, ".17", "CONTEXT_DEFAULT: circular schedule prose; no word-sound claim."


def main() -> None:
    prose = [x for x in rows(GDT327) if x["page"] in PAGES]
    if len(prose) != 381:
        raise SystemExit(f"expected 381 prose events, found {len(prose)}")

    source = list(GuardedTSV(SOURCE, selector_column="page", allowed_values=PAGES, forbidden_prefixes=("f84",)))
    source_index = {(x["locus"], x["group_index"]): x for x in source}
    if len(source_index) < 381:
        raise SystemExit("source-native join lacks selected events")
    for x in prose:
        s = source_index[(x["locus"], x["group_index"])]
        x["surface"] = s["zl_basic_eva_lossy"]

    occurrences: dict[str, list[dict]] = defaultdict(list)
    for x in prose:
        occurrences[x["joint_tuple_id"]].append(x)
    meanings = {tid: derive_card_gloss(tid, occ) for tid, occ in occurrences.items()}

    ledger: list[dict] = []
    lexicon: list[dict] = []
    for tid, occ in sorted(occurrences.items()):
        gloss, cls, conf, rule = meanings[tid]
        lexicon.append({
            "lexicon_id": tid,
            "scope": "PROSE_EXACT_CARD",
            "surface_examples": "|".join(sorted({x["surface"] for x in occ})),
            "default_English": gloss,
            "source_class": cls,
            "confidence": conf,
            "events": str(len(occ)),
            "pages": "|".join(sorted({x["page"] for x in occ})),
            "inheritance_context_rule": rule,
        })
    lexicon.append({
        "lexicon_id": "FORMULA_F3",
        "scope": "PROSE_CONSTRUCTION",
        "surface_examples": "Y-AIIN-Y",
        "default_English": "both portions under the same stated standard",
        "source_class": "SHARED_STANDARD_CONSTRUCTION",
        "confidence": ".44",
        "events": "2",
        "pages": "f10r|f83r",
        "inheritance_context_rule": "Exact three-card formula; inherited measure supplies the common standard.",
    })
    for serial, x in enumerate(prose, 1):
        gloss, cls, conf, rule = meanings[x["joint_tuple_id"]]
        inherited = rule
        if x["line_first"] == "1":
            inherited += " Physical-line entry does not itself start a new sentence."
        if x["dy_closure"] == "1" or x["b3"] == "1":
            inherited += " Attached close ends the local rubric, not necessarily the paragraph statement."
        ledger.append({
            "page": x["page"], "locus": x["locus"], "record": x["record_ordinal"],
            "line": x["locus"], "event_index": x["group_index"], "surface": x["surface"],
            "exact_tuple_id": x["joint_tuple_id"], "default_English": gloss,
            "source_class": cls, "confidence": conf, "inheritance_context_rule": inherited,
            "ledger_scope": "GDT327_PROSE", "source_event_serial": str(serial),
        })

    astro = list(GuardedTSV(ASTRO_SOURCE, selector_column="page", allowed_values=ASTRO, forbidden_prefixes=("f84",)))
    if len(astro) != 395:
        raise SystemExit(f"expected 395 Astro tokens, found {len(astro)}")
    for x in astro:
        locus_no = int(x["locus"].rsplit(".", 1)[1])
        token_index = int(x["token_index"])
        gloss, cls, conf, rule = astro_gloss(x["page"], locus_no, x["kind"], token_index)
        lex_id = f"ASTRO_{x['page']}_{locus_no:03d}_{token_index:02d}"
        lexicon.append({
            "lexicon_id": lex_id, "scope": "ASTRO_SPATIAL_TOKEN", "surface_examples": x["eva"],
            "default_English": gloss, "source_class": cls, "confidence": conf,
            "events": "1", "pages": x["page"], "inheritance_context_rule": rule,
        })
        ledger.append({
            "page": x["page"], "locus": x["locus"], "record": "DIAGRAM",
            "line": x["locus"], "event_index": x["token_index"], "surface": x["eva"],
            "exact_tuple_id": lex_id, "default_English": gloss, "source_class": cls,
            "confidence": conf, "inheritance_context_rule": rule,
            "ledger_scope": "ZL3B_ASTRO_VISIBLE_TOKEN", "source_event_serial": x["token_id"],
        })

    line_rows = []
    by_line: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for x in ledger:
        by_line[(x["page"], x["locus"])].append(x)
    for (page, locus), group in sorted(by_line.items()):
        group.sort(key=lambda z: int(z["event_index"]))
        line_rows.append({
            "page": page,
            "locus": locus,
            "surface_sequence": " ".join(x["surface"] for x in group),
            "complete_default_reading": "; ".join(x["default_English"] for x in group),
            "event_count": str(len(group)),
            "continuity_note": "Physical end is reflow only unless the final group carries a local close.",
        })

    write(LEXICON, lexicon, ["lexicon_id", "scope", "surface_examples", "default_English", "source_class", "confidence", "events", "pages", "inheritance_context_rule"])
    write(LEDGER, ledger, ["page", "locus", "record", "line", "event_index", "surface", "exact_tuple_id", "default_English", "source_class", "confidence", "inheritance_context_rule", "ledger_scope", "source_event_serial"])
    write(LINES, line_rows, ["page", "locus", "surface_sequence", "complete_default_reading", "event_count", "continuity_note"])

    blank = [x for x in ledger if not x["default_English"].strip()]
    banned = {"UNKNOWN", "OPAQUE", "UNTRANSLATED", "CONTENT", "PAYLOAD", "ITEM", "VALUE", "STATE"}
    evasive = [x for x in ledger if x["default_English"].strip().upper() in banned]
    summary = [
        "R4 V16 COMPLETE DEFAULT BUILD",
        f"prose_events={len(prose)}",
        f"prose_exact_cards={len(occurrences)}",
        f"astro_visible_tokens={len(astro)}",
        f"ledger_rows={len(ledger)}",
        f"lexicon_rows={len(lexicon)}",
        f"line_or_locus_readings={len(line_rows)}",
        f"blank_glosses={len(blank)}",
        f"evasive_exact_glosses={len(evasive)}",
        "f84_opened=false",
        "f84r_opened=false",
        "sibling_v16_outputs_read=false",
    ]
    SUMMARY.write_text("\n".join(summary) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
