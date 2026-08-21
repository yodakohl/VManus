#!/usr/bin/env python3
"""Build R1's deliberately speculative complete-default reading for ten pages.

This is a sidequest artifact, not a decipherment or canonical GDT result.  It
uses only page-guarded f84-free observations and assigns a concrete revisable
English default to every selected visible group.
"""
from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV  # noqa: E402

OUT = Path(__file__).resolve().parent
PROSE_PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
HERBAL = {"f10r", "f11r", "f55v", "f56r"}
BIO = {"f81v", "f82r", "f83r"}
ASTRO = {"f67r2", "f68r1", "f69v"}


def guarded(path: Path, pages: set[str]) -> list[dict[str, str]]:
    reader = GuardedTSV(
        path,
        selector_column="page",
        allowed_values=pages,
        forbidden_prefixes=("f84",),
        forbidden_action="skip",
    )
    rows = list(reader)
    assert not any(r["page"].startswith("f84") for r in rows)
    return rows


def write(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def choose(key: str, values: list[tuple[str, str]]) -> tuple[str, str]:
    n = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)
    return values[n % len(values)]


COMMON = [
    ("continue the same prescription", "CONTINUATION"),
    ("take the next prescribed portion", "ENTRY_ACTION"),
    ("likewise with the preparation above", "INHERITED_RELATION"),
    ("use the usual prescribed measure", "MEASURE_REFERENCE"),
    ("bind this addition to the current preparation", "RELATION"),
    ("repeat the preceding direction", "REPETITION"),
    ("retain the same degree of strength", "DEGREE_REFERENCE"),
    ("then proceed to the following direction", "SEQUENCE"),
]

HERBAL_OPEN = [
    ("the pictured medicinal simple", "PLANT_NAME"),
    ("belongs to the marsh-growing kind", "PLANT_CLASS"),
    ("has a narrow divided leaf", "LEAF_DESCRIPTION"),
    ("has a broad soft leaf", "LEAF_DESCRIPTION"),
    ("has a pale hollow stalk", "STALK_DESCRIPTION"),
    ("bears a small clustered flower", "FLOWER_DESCRIPTION"),
    ("has a fibrous bitter root", "ROOT_DESCRIPTION"),
    ("grows beside running water", "WATER_HABITAT"),
    ("thrives in damp shaded ground", "MOIST_HABITAT"),
    ("is cooling in the second degree", "QUALITY_DEGREE"),
    ("is moist in the first degree", "QUALITY_DEGREE"),
    ("gather it before flowering", "COLLECTION_TIME"),
    ("take the fresh leaves", "PLANT_PART"),
    ("take the scraped root", "PLANT_PART"),
    ("bruise it well in a mortar", "PREPARATION_ACTION"),
    ("boil it in spring water", "WATER_PREPARATION"),
    ("steep it overnight", "PREPARATION_DURATION"),
    ("strain the resulting liquor", "PREPARATION_ACTION"),
    ("mix it with wine", "MIXING_MEDIUM"),
    ("mix it with honey", "MIXING_MEDIUM"),
    ("apply it while warm", "APPLICATION"),
    ("wash the afflicted place", "APPLICATION"),
    ("drink one small cup", "DOSE"),
    ("it eases swelling", "INDICATION"),
    ("it cools a fever", "INDICATION"),
    ("it opens an obstruction", "INDICATION"),
    ("repeat for three days", "DURATION"),
    ("keep the herb after drying", "STORAGE"),
    ("the seed is less strong", "PART_COMPARISON"),
    ("use only the inner bark", "PLANT_PART"),
    ("avoid an excessive dose", "CAUTION"),
]

HERBAL_B = [
    ("take the pictured herb", "PLANT_ENTRY"),
    ("cut the fresh stalks", "PREPARATION_ACTION"),
    ("pound the leaves finely", "PREPARATION_ACTION"),
    ("add clean well-water", "WATER_MEDIUM"),
    ("boil to one half", "REDUCTION"),
    ("strain through linen", "PREPARATION_ACTION"),
    ("add a spoon of honey", "ADDITION"),
    ("apply the warm liquor", "APPLICATION"),
    ("wash the sore place", "APPLICATION"),
    ("keep the remainder covered", "STORAGE"),
    ("give the usual small measure", "DOSE"),
    ("the remedy is ready", "RESULT"),
]

BIO_OPEN = [
    ("take the prepared bath", "APPLICATION_ENTRY"),
    ("admit warm water through the upper channel", "FLOW_ACTION"),
    ("seat the patient in the lower basin", "PATIENT_PLACEMENT"),
    ("keep the body below the marked level", "LEVEL_CONDITION"),
    ("pour the herbal liquor over the affected part", "APPLICATION"),
    ("let the liquor return through the side conduit", "FLOW_ACTION"),
    ("close the lower outlet", "APPARATUS_ACTION"),
    ("open the upper outlet", "APPARATUS_ACTION"),
    ("add the strained herbal liquor", "ADDITION"),
    ("mix with clean spring water", "WATER_MEDIUM"),
    ("warm it gently", "HEATING_ACTION"),
    ("allow it to cool", "COOLING_ACTION"),
    ("hold until the skin is warmed", "DURATION_GATE"),
    ("rinse the local part", "APPLICATION"),
    ("immerse the limbs", "APPLICATION"),
    ("repeat the washing", "REPETITION"),
    ("transfer to the next basin", "TRANSFER"),
    ("retain the same proportion", "PROPORTION_REFERENCE"),
    ("use the usual measure", "MEASURE_REFERENCE"),
    ("apply before sleep", "APPLICATION_TIME"),
    ("continue on the following day", "SEQUENCE"),
    ("the preparation is ready", "RESULT"),
    ("the course is complete", "CLOSURE"),
    ("do not let the liquor boil", "CAUTION"),
    ("use for the person shown", "PICTURE_OWNED_APPLICATION"),
]

BIO_CLOSE = [
    ("finish with the ordinary warm bath", "COMMITTED_APPLICATION"),
    ("leave the mixture to settle", "COMMITTED_RESULT"),
    ("complete the local rinsing", "COMMITTED_APPLICATION"),
    ("hold the usual measure until ready", "COMMITTED_DURATION"),
    ("seal the vessel after straining", "COMMITTED_APPARATUS_ACTION"),
    ("end this course after one immersion", "COMMITTED_DURATION"),
    ("retain the prepared liquor for the next washing", "COMMITTED_STORAGE"),
    ("close the outlet when the basin is full", "COMMITTED_APPARATUS_ACTION"),
]

KNOWN_PREFIX = {
    "2f1c5e56": ("in the stated or usual measure", "ACTIVE_STANDARD_REFERENCE", "0.61"),
    "b921a237": ("the current prescribed portion", "CURRENT_PORTION", "0.52"),
    "dcda95c8": ("with it; likewise under the same heading", "ACTIVE_RELATION", "0.59"),
    "e0b630cb": ("prepared and ready for use", "PREPARED_CONDITION", "0.44"),
    "b5fcea1e": ("take the next entry", "ENTRY_OR_RESUMPTION", "0.57"),
}


def identify_value_aliases(events: list[dict[str, str]]) -> dict[str, tuple[str, str, str]]:
    aliases = {
        "qokedy": ("use the standard bath configuration", "VAL_Q_STANDARD", "0.50"),
        "qokeedy": ("use the tempered circulating liquor", "VAL_QE_TEMPERED", "0.48"),
        "shedy": ("let the preparation settle until ready", "VAL_S_READY", "0.45"),
        "cheedy": ("let the preparation settle until ready", "VAL_S_READY", "0.45"),
        "tedy": ("let the preparation settle until ready", "VAL_S_READY", "0.45"),
        "lchedy": ("pour the liquor over the local part", "VAL_L_LOCAL_POUR", "0.43"),
    }
    out: dict[str, tuple[str, str, str]] = {}
    for event in events:
        if event["raw_token"] in aliases:
            out[event["joint_tuple_id"]] = aliases[event["raw_token"]]
    return out


def build_prose() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, list[str]]]:
    # GDT278 deliberately hashes its source surface; the aligned GDT276 layer
    # retains the same f84-free observation IDs with the visible source group.
    native = guarded(ROOT / "gdt276_event_inventory.tsv", PROSE_PAGES)
    inter = guarded(ROOT / "gdt327_joint_tuple_interlinear.tsv", PROSE_PAGES)
    assert len(native) == len(inter) == 381
    native_by = {(r["locus"], r["group_index"]): r for r in native}
    events: list[dict[str, str]] = []
    for row in inter:
        source = native_by[(row["locus"], row["group_index"])]
        merged = dict(row)
        merged["raw_token"] = source["raw_token"]
        events.append(merged)
    events.sort(key=lambda r: (r["page"], int(r["record_ordinal"]), int(r["locus"].split(".")[1]), int(r["group_index"])))

    by_tuple: dict[str, list[dict[str, str]]] = defaultdict(list)
    for event in events:
        by_tuple[event["joint_tuple_id"]].append(event)
    value_aliases = identify_value_aliases(events)
    meanings: dict[str, tuple[str, str, str, str]] = {}
    for tuple_id, occurrences in sorted(by_tuple.items()):
        known = next((v for prefix, v in KNOWN_PREFIX.items() if tuple_id.startswith(prefix)), None)
        if known:
            gloss, source_class, confidence = known
            meanings[tuple_id] = (gloss, source_class, confidence, "GLOBAL_CORE_DEFAULT")
            continue
        if tuple_id in value_aliases:
            gloss, source_class, confidence = value_aliases[tuple_id]
            meanings[tuple_id] = (gloss, source_class, confidence, "BIO_VALUE_DECK_DEFAULT")
            continue
        pages = {r["page"] for r in occurrences}
        if pages & HERBAL and pages & BIO:
            gloss, source_class = choose(tuple_id, COMMON)
            meanings[tuple_id] = (gloss, source_class, "0.30", "CROSS_REGISTER_DEFAULT")
        elif pages <= HERBAL:
            pool = HERBAL_B if pages == {"f55v"} else HERBAL_OPEN
            gloss, source_class = choose(tuple_id, pool)
            meanings[tuple_id] = (gloss, source_class, "0.18", "PICTURED_SIMPLE_CONTEXT_DEFAULT")
        else:
            close_rate = sum(int(r["dy_closure"]) or int(r["b3"]) for r in occurrences) / len(occurrences)
            pool = BIO_CLOSE if close_rate >= 0.5 else BIO_OPEN
            gloss, source_class = choose(tuple_id, pool)
            meanings[tuple_id] = (gloss, source_class, "0.20", "BIO_STENCIL_CONTEXT_DEFAULT")

    ledger: list[dict[str, object]] = []
    page_event = Counter()
    for event in events:
        page_event[event["page"]] += 1
        gloss, source_class, confidence, rule = meanings[event["joint_tuple_id"]]
        inherited = rule
        if event["page"] in HERBAL:
            inherited += "; subject=[PICTURED SIMPLE] when omitted"
        else:
            inherited += "; apparatus/patient=[PICTURED CONFIGURATION] when omitted"
        if event["dy_closure"] == "1" or event["b3"] == "1":
            inherited += "; local cell committed after this card"
        ledger.append({
            "page": event["page"],
            "locus": event["locus"],
            "record": event["record_ordinal"],
            "field_ordinal": event["field_ordinal"],
            "line": event["locus"],
            "event_index": page_event[event["page"]],
            "group_index": event["group_index"],
            "surface": event["raw_token"],
            "exact_tuple_id": event["joint_tuple_id"],
            "default_English": gloss,
            "source_class": source_class,
            "confidence": confidence,
            "inheritance_context_rule": inherited,
        })

    lexicon: list[dict[str, object]] = []
    for tuple_id, occurrences in sorted(by_tuple.items()):
        gloss, source_class, confidence, rule = meanings[tuple_id]
        lexicon.append({
            "lexicon_key": f"PROSE:{tuple_id}",
            "domain": "HERBAL_AND_BIO" if {r["page"] for r in occurrences} & HERBAL and {r["page"] for r in occurrences} & BIO else ("HERBAL" if occurrences[0]["page"] in HERBAL else "BIOLOGICAL"),
            "exact_tuple_or_surface_id": tuple_id,
            "surface_realizations": "|".join(sorted({r["raw_token"] for r in occurrences})),
            "occurrences": len(occurrences),
            "pages": "|".join(sorted({r["page"] for r in occurrences})),
            "default_English": gloss,
            "source_class": source_class,
            "confidence": confidence,
            "sense_rule": rule,
        })
    lines: dict[str, list[str]] = defaultdict(list)
    for row in ledger:
        lines[str(row["locus"])].append(str(row["default_English"]))
    return ledger, lexicon, lines


def comment_location(comment: str) -> str:
    text = comment.split(". ")[0].strip().rstrip(".")
    if text.startswith("Label on star at "):
        return text[len("Label on star at "):]
    if text.startswith("Log at "):
        return text[len("Log at "):]
    if text.startswith("At "):
        return text[len("At "):]
    return text[:90]


F67_TEXT = {
    72: ["for", "the", "current", "zodiacal division", "select", "its", "planetary governor", "then", "read", "the corresponding", "inner", "condition"],
    73: ["if", "the", "marked", "hour", "falls", "under", "the same", "governor", "carry", "the rule", "forward"],
    74: ["for", "bathing", "or", "applying", "the remedy", "choose", "a favorable", "condition", "and", "avoid", "the contrary", "hour", "thereafter"],
}
F68_TEXT = {
    1: ["this", "star map", "sets forth", "the named", "celestial stations", "around", "the central", "light", "for consultation"],
    2: ["choose", "the station", "nearest", "the required", "celestial light", "and", "carry", "its rule", "to the case"],
    3: ["stars of", "the inner", "and outer", "courses", "share", "one", "appointed", "reckoning"],
    37: ["use", "the central star", "as", "the local", "reference"],
}
F69_PROSE = [
    "for", "the lunar course", "reckon", "the mansion", "shown", "on the long spoke", "then", "the answering mansion", "on the short spoke", "observe", "the favorable hour", "for bathing", "the unfavorable hour", "for bleeding", "carry", "the count", "forward", "one place", "each day", "when the moon", "enters", "the next mansion", "use", "the corresponding rule", "for the patient", "shown in the register", "and", "repeat", "after the cycle", "is complete", "the long member", "governs", "the first interval", "the short member", "governs", "the second interval", "do not reverse", "the paired order", "without a fresh observation", "thereafter",
]


def astro_gloss(row: dict[str, str], array: dict[str, str] | None) -> tuple[str, str, str, str]:
    page, locus = row["page"], row["locus"]
    token_index = int(row["token_index"])
    line_no = int(locus.split(".")[1])
    if array:
        unit = array["unit"]
        slot = int(array["slot_index"])
        location = comment_location(array["local_comment"])
        if unit == "M1":
            head = f"planetary governor {slot} at {location}"
            kind = "PLANETARY_GOVERNOR_LABEL"
        elif unit == "M2":
            head = f"zodiacal division {slot} at {location}"
            kind = "ZODIAC_DIVISION_LABEL"
        elif unit == "M3":
            head = f"inner celestial condition {slot} at {location}"
            kind = "INNER_CONDITION_LABEL"
        elif unit == "S1":
            head = f"named star at {location}"
            kind = "SPATIALLY_OWNED_STAR_LABEL"
        else:
            length = "long" if "long" in array["local_comment"].lower() else "short"
            head = f"lunar mansion on the {length} spoke at {location}"
            kind = "LUNAR_MANSION_LABEL"
        if token_index == 1:
            return head, kind, "0.31", "SPATIAL_OWNER_DEFAULT; no phonetic reading"
        tails = [
            ("under its appointed ruler", "RULER_QUALIFIER"),
            ("for the favorable interval", "INTERVAL_QUALIFIER"),
            ("with the corresponding medical election", "ELECTION_QUALIFIER"),
            ("as entered in the local table", "TABLE_QUALIFIER"),
        ]
        gloss, source_class = tails[(token_index - 2) % len(tails)]
        return gloss, source_class, "0.16", "QUALIFIER_OF_PRECEDING_SPATIALLY_OWNED_LABEL"
    if page == "f67r2" and line_no in F67_TEXT:
        words = F67_TEXT[line_no]
        return words[token_index - 1], "CELESTIAL_LOOKUP_INSTRUCTION", "0.17", "CONTINUOUS_DIAGRAM_INSTRUCTION_DEFAULT"
    if page == "f68r1" and line_no in F68_TEXT:
        words = F68_TEXT[line_no]
        return words[token_index - 1], "STAR_MAP_INSTRUCTION", "0.17", "CONTINUOUS_STAR_MAP_TEXT_DEFAULT"
    if page == "f69v" and line_no <= 3:
        return F69_PROSE[(sum([40, 38, 29][: line_no - 1]) + token_index - 1) % len(F69_PROSE)], "LUNAR_SCHEDULE_INSTRUCTION", "0.15", "CONTINUOUS_LUNAR_SCHEDULE_TEXT_DEFAULT"
    # Uncatalogued f67 groups are still given concrete local diagram ownership.
    local_roles = [
        "names the celestial influence at this drawn locus",
        "marks that influence as favorable for washing",
        "assigns the current zodiacal division",
        "refers it to the ruling planet",
    ]
    return local_roles[(token_index - 1) % len(local_roles)], "LOCAL_CELESTIAL_RULE", "0.12", "UNCATALOGUED_DRAWN_LOCUS_CONTEXT_DEFAULT"


def build_astro() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, list[str]]]:
    tokens = guarded(ROOT / "transcription/voynich_zl3b_tokens.tsv", ASTRO)
    arrays = guarded(ROOT / "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv", ASTRO)
    assert len(tokens) == 395
    by_locus = {r["locus"]: r for r in arrays}
    tokens.sort(key=lambda r: (r["page"], int(r["locus"].split(".")[1]), int(r["token_index"])))
    ledger: list[dict[str, object]] = []
    lexicon: list[dict[str, object]] = []
    lines: dict[str, list[str]] = defaultdict(list)
    page_event = Counter()
    for row in tokens:
        page_event[row["page"]] += 1
        gloss, source_class, confidence, rule = astro_gloss(row, by_locus.get(row["locus"]))
        surface_id = "ASTRO-" + hashlib.sha256(f'{row["page"]}|{row["locus"]}|{row["token_index"]}|{row["eva"]}'.encode()).hexdigest()[:16]
        owner = by_locus.get(row["locus"], {})
        record = owner.get("array_id", f'{row["page"]}:TEXT_OR_LOCAL_LABEL')
        ledger.append({
            "page": row["page"],
            "locus": row["locus"],
            "record": record,
            "field_ordinal": owner.get("unit", "LOCAL_TEXT"),
            "line": row["locus"],
            "event_index": page_event[row["page"]],
            "group_index": row["token_index"],
            "surface": row["eva"],
            "exact_tuple_id": "ASTRO_NO_GDT327:" + surface_id,
            "default_English": gloss,
            "source_class": source_class,
            "confidence": confidence,
            "inheritance_context_rule": rule,
        })
        lexicon.append({
            "lexicon_key": f'{row["page"]}:{row["locus"]}:{row["token_index"]}',
            "domain": "ASTRO_LOCAL_NAMESPACE",
            "exact_tuple_or_surface_id": surface_id,
            "surface_realizations": row["eva"],
            "occurrences": 1,
            "pages": row["page"],
            "default_English": gloss,
            "source_class": source_class,
            "confidence": confidence,
            "sense_rule": rule,
        })
        lines[row["locus"]].append(gloss)
    return ledger, lexicon, lines


def add_constructions(lexicon: list[dict[str, object]]) -> None:
    constructions = [
        ("CONSTRUCTION:qokaiin", "take the next entry", "ENTRY_OR_RESUMPTION", "0.57", "same exact card at all occurrences"),
        ("CONSTRUCTION:L_O", "with it; likewise under the same heading", "ACTIVE_RELATION", "0.59", "inherits missing left anchor at field entry"),
        ("CONSTRUCTION:AIIN", "in the stated or usual measure", "ACTIVE_STANDARD_REFERENCE", "0.61", "measure may be inherited from current prescription"),
        ("CONSTRUCTION:Y", "the current prescribed portion", "CURRENT_PORTION", "0.52", "points to the locally active portion"),
        ("CONSTRUCTION:CTHY", "prepared and ready for use", "PREPARED_CONDITION", "0.44", "applies to current plant preparation or bath"),
        ("CONSTRUCTION:FORMULA_F3", "both portions under the same stated measure", "SHARED_STANDARD_FORMULA", "0.44", "Y-AIIN-Y copied as a complete formula"),
        ("CONSTRUCTION:VAL_Q", "use the standard bath configuration", "VAL_Q_STANDARD", "0.50", "exact categorical answer followed by local commitment"),
        ("CONSTRUCTION:VAL_QE", "use the tempered circulating liquor", "VAL_QE_TEMPERED", "0.48", "exact categorical answer followed by local commitment"),
        ("CONSTRUCTION:VAL_S", "let the preparation settle until ready", "VAL_S_READY", "0.45", "exact categorical answer followed by local commitment"),
        ("CONSTRUCTION:VAL_L", "pour the liquor over the local part", "VAL_L_LOCAL_POUR", "0.43", "exact categorical answer followed by local commitment"),
    ]
    for key, gloss, source_class, confidence, rule in constructions:
        lexicon.append({
            "lexicon_key": key,
            "domain": "CROSS_PAGE_CONSTRUCTION",
            "exact_tuple_or_surface_id": key.split(":", 1)[1],
            "surface_realizations": "construction",
            "occurrences": "see event ledger",
            "pages": "fixed ten-page scope",
            "default_English": gloss,
            "source_class": source_class,
            "confidence": confidence,
            "sense_rule": rule,
        })


def main() -> None:
    prose_ledger, prose_lexicon, prose_lines = build_prose()
    astro_ledger, astro_lexicon, astro_lines = build_astro()
    ledger = prose_ledger + astro_ledger
    lexicon = prose_lexicon + astro_lexicon
    add_constructions(lexicon)
    banned = {"unknown", "opaque", "untranslated", "content", "payload", "item", "value", "state"}
    for row in ledger:
        words = {w.strip(".,;:()[]").lower() for w in str(row["default_English"]).split()}
        assert row["default_English"] and not words & banned, (row, words & banned)
    assert len(prose_ledger) == 381
    assert len(astro_ledger) == 395
    assert len(ledger) == 776
    assert {r["page"] for r in ledger} == PROSE_PAGES | ASTRO
    write(OUT / "V16_R1_COMPLETE_TRANSLATION_LEDGER.tsv", ledger)
    write(OUT / "V16_R1_COMPLETE_DEFAULT_LEXICON.tsv", lexicon)

    # Explicitly cover multi-group fields, whole records (which may cross a
    # physical line), and Astro labels/lines.  This prevents a word-complete
    # ledger from silently leaving its sequences uninterpreted.
    constructions: list[dict[str, object]] = []
    prose_fields: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    prose_records: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    astro_loci: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in ledger:
        if row["page"] in PROSE_PAGES:
            prose_fields[(str(row["page"]), str(row["record"]), str(row["locus"]), str(row["field_ordinal"]))].append(row)
            prose_records[(str(row["page"]), str(row["record"]))].append(row)
        else:
            astro_loci[(str(row["page"]), str(row["locus"]))].append(row)
    for (page, record, locus, field), rows in sorted(prose_fields.items()):
        constructions.append({
            "construction_id": f"{page}:{record}:{locus}:F{field}",
            "page": page,
            "construction_level": "PROSE_FIELD",
            "visible_sequence": " ".join(str(r["surface"]) for r in rows),
            "default_reading": "; ".join(str(r["default_English"]) for r in rows) + ".",
            "confidence": min(str(r["confidence"]) for r in rows),
            "composition_rule": "ordered exact-card meanings; omitted subject supplied by picture/current prescription",
        })
    for (page, record), rows in sorted(prose_records.items()):
        constructions.append({
            "construction_id": f"{page}:RECORD:{record}",
            "page": page,
            "construction_level": "PROSE_RECORD_ACROSS_PHYSICAL_LINES",
            "visible_sequence": " ".join(str(r["surface"]) for r in rows),
            "default_reading": "; ".join(str(r["default_English"]) for r in rows) + ".",
            "confidence": min(str(r["confidence"]) for r in rows),
            "composition_rule": "record continuity outranks physical line endings",
        })
    for (page, locus), rows in sorted(astro_loci.items(), key=lambda kv: (kv[0][0], int(kv[0][1].split(".")[1]))):
        constructions.append({
            "construction_id": f"{page}:{locus}:LABEL_OR_LINE",
            "page": page,
            "construction_level": "ASTRO_LABEL_OR_INSTRUCTION_LINE",
            "visible_sequence": " ".join(str(r["surface"]) for r in rows),
            "default_reading": " ".join(str(r["default_English"]) for r in rows) + ".",
            "confidence": min(str(r["confidence"]) for r in rows),
            "composition_rule": "spatial owner fixes the local label; no universal surface dictionary or f68 cycle start",
        })
    write(OUT / "V16_R1_COMPLETE_CONSTRUCTION_READINGS.tsv", constructions)

    # Compact line-level renderings used by the candidate report.
    rendered: list[dict[str, object]] = []
    for locus, phrases in sorted({**prose_lines, **astro_lines}.items(), key=lambda kv: (kv[0].split(".")[0], int(kv[0].split(".")[1]))):
        rendered.append({"locus": locus, "default_reading": "; ".join(phrases) + "."})
    write(OUT / "V16_R1_LINE_READINGS.tsv", rendered)

    print({
        "prose_events": len(prose_ledger),
        "astro_groups": len(astro_ledger),
        "total": len(ledger),
        "prose_tuple_defaults": len(prose_lexicon),
        "astro_spatial_defaults": len(astro_lexicon),
        "lexicon_rows_with_constructions": len(lexicon),
        "multi_group_and_record_constructions": len(constructions),
    })


if __name__ == "__main__":
    main()
