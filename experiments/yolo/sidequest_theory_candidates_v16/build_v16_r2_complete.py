#!/usr/bin/env python3
"""Build R2's deliberately complete ten-page default-meaning ledger.

This is a speculative sidequest artifact, not a decipherment instrument.  All
mixed sources are sliced through the repository guard before parsing.
"""

from __future__ import annotations

import csv
import hashlib
import io
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PROSE_PAGES = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"]
ASTRO_PAGES = ["f67r2", "f68r1", "f69v"]


def guarded(path: str, pages: list[str], columns: list[str]) -> list[dict[str, str]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", str(ROOT / path),
               "--selector", "page"]
    for page in pages:
        command += ["--allow", page]
    command += ["--columns", ",".join(columns), "--forbid-prefix", "f84"]
    completed = subprocess.run(command, check=True, text=True,
                               stdout=subprocess.PIPE)
    return list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))


FIXED = {
    "2f1c5e56e8f0": ("according to the stated measure or duration", "REFERENCE", .58),
    "dcda95c81a54": ("with it; likewise under the same heading", "RELATION", .62),
    "b921a237be88": ("the current portion", "POINTER", .56),
    "bc4f1f5c006c": ("use the standard lukewarm bath", "COMMITTED_APPLICATION", .38),
    "6f7ff8287edd": ("keep it prepared and ready", "COMMITTED_RESULT", .40),
    "276a7c2d74d1": ("apply it to the affected place", "ACTION", .43),
    "dd0ecaf5e27d": ("upon the affected place", "APPLICATION_RELATION", .40),
    "7d25241b0e56": ("use the tempered herbal bath", "COMMITTED_APPLICATION", .41),
    "b5fcea1eaed0": ("take the next portion", "ENTRY_ACTION", .57),
    "7db18b2f0fb7": ("warm it gently", "COMMITTED_PROCESS", .38),
    "de7321bface5": ("pour or rinse it locally", "COMMITTED_APPLICATION", .39),
    "e0b630cb1b5d": ("when it is prepared", "PREPARATION_CONDITION", .42),
    "7a4bb8136330": ("the expressed juice", "MATERIAL", .34),
    "1645e612504f": ("add the measured ingredient", "ACTION", .39),
    "0275fbf14e07": ("mix it thoroughly", "ACTION", .40),
    "308e8ea2d5d1": ("with warmed water", "MEDIUM", .39),
    "4d4559019a96": ("then continue", "SEQUENCE", .35),
    "b5df91266070": ("repeat the application", "REPEAT_ACTION", .34),
    "2cc054357a92": ("its blue flowering tops", "PLANT_PART", .35),
    "2cc8bb3c2af1": ("keep it immersed", "ACTION", .37),
    "259b2b3b0bf8": ("strain it and set it aside", "COMMITTED_PROCESS", .38),
    "9ad66e67803a": ("bruise it well", "ACTION", .40),
    "9da1b6ac2c92": ("one handful", "MEASURE", .37),
    "28ffbc88b977": ("with it, complete the rinse", "COMMITTED_RELATION", .37),
    "87411f84689b": ("heat it gently", "COMMITTED_PROCESS", .38),
    "d904bf7b044d": ("pour it over", "ACTION", .38),
    "3b70942557b3": ("bathe the two together", "COMMITTED_APPLICATION", .36),
    "d68bc8de3bce": ("let it steep until ready", "COMMITTED_PROCESS", .38),
    "54d0e228ca34": ("for the stated time", "DURATION", .38),
    "90bcf0a9ec0e": ("at moderate warmth", "TEMPERATURE", .37),
    "80ebbbbf238e": ("finely dried", "PREPARATION", .33),
    "10488b911aae": ("boil it", "ACTION", .38),
    "dec401773c1f": ("the juice thereof", "MATERIAL", .37),
    "d665560c8ff8": ("its tender stem", "PLANT_PART", .34),
    "2c1a5fd92b9e": ("wash it clean", "ACTION", .36),
}

HERBAL_TERMS = [
    ("the pictured simple's accepted name", "PLANT_NAME"),
    ("its common local name", "PLANT_ALIAS"),
    ("cool in the first degree", "HUMORAL_QUALITY"),
    ("slightly moist in complexion", "HUMORAL_QUALITY"),
    ("the broad lower leaves", "PLANT_PART"),
    ("the narrow upper leaves", "PLANT_PART"),
    ("the blue flowers", "PLANT_PART"),
    ("the fresh root", "PLANT_PART"),
    ("the dried root", "PLANT_PART"),
    ("the bruised seed", "PLANT_PART"),
    ("growing in moist ground", "HABITAT"),
    ("found beside ditches and springs", "HABITAT"),
    ("gather before full flowering", "COLLECTION"),
    ("dry it in the shade", "PREPARATION"),
    ("bruise the leaves", "PREPARATION"),
    ("press out the juice", "PREPARATION"),
    ("boil the root in water", "PREPARATION"),
    ("mix the powder with honey", "PREPARATION"),
    ("make a warm wash", "PREPARATION"),
    ("lay it upon a swelling", "APPLICATION"),
    ("drink a small draught", "APPLICATION"),
    ("wash the sore place", "APPLICATION"),
    ("it softens hard swellings", "VIRTUE"),
    ("it cools inflamed skin", "VIRTUE"),
    ("it draws out corrupted matter", "VIRTUE"),
    ("it eases pain of the chest", "VIRTUE"),
    ("it opens a stopped passage", "VIRTUE"),
    ("keep the remainder dry", "STORAGE"),
    ("use morning and evening", "DOSING"),
    ("give only the smaller portion", "DOSING"),
]

BIO_TERMS = [
    ("open the upper inlet", "APPARATUS_ACTION"),
    ("close the lower outlet", "APPARATUS_ACTION"),
    ("join the two conduits", "APPARATUS_ACTION"),
    ("let the green liquor flow", "FLOW_ACTION"),
    ("hold the flow at the junction", "FLOW_ACTION"),
    ("draw off the spent liquor", "FLOW_ACTION"),
    ("fill the lower basin", "BATH_ACTION"),
    ("immerse the affected member", "BATH_ACTION"),
    ("bathe until the skin is warm", "BATH_ACTION"),
    ("rinse with clean water", "BATH_ACTION"),
    ("anoint after bathing", "APPLICATION"),
    ("apply the warm cloth", "APPLICATION"),
    ("the upper vessel", "APPARATUS"),
    ("the lower basin", "APPARATUS"),
    ("the joining tube", "APPARATUS"),
    ("the outlet channel", "APPARATUS"),
    ("the green herbal liquor", "MEDIUM"),
    ("fresh spring water", "MEDIUM"),
    ("the strained decoction", "MEDIUM"),
    ("one vesselful", "MEASURE"),
    ("half the usual quantity", "MEASURE"),
    ("until gently warm", "DURATION"),
    ("until the flow clears", "DURATION"),
    ("after the first bathing", "SEQUENCE"),
    ("then repeat once", "SEQUENCE"),
    ("leave it at rest", "RESULT"),
    ("the passage is clear", "RESULT"),
    ("the application is finished", "RESULT"),
    ("retain the same setting", "REFERENCE"),
    ("use the alternate setting", "REFERENCE"),
]

COMMITTED_TERMS = [
    ("seal the inlet after filling", "COMMITTED_APPARATUS"),
    ("let the bath stand until warm", "COMMITTED_PROCESS"),
    ("complete one local washing", "COMMITTED_APPLICATION"),
    ("finish the pouring at this station", "COMMITTED_APPLICATION"),
    ("hold the member immersed", "COMMITTED_APPLICATION"),
    ("strain off the spent liquid", "COMMITTED_PROCESS"),
    ("set the prepared liquor aside", "COMMITTED_RESULT"),
    ("close this treatment step", "COMMITTED_RESULT"),
    ("repeat the rinsing once", "COMMITTED_APPLICATION"),
    ("leave the conduit closed", "COMMITTED_APPARATUS"),
    ("keep the mixture at gentle heat", "COMMITTED_PROCESS"),
    ("the prepared bath is ready", "COMMITTED_RESULT"),
]


def choose(seq, key):
    n = int(hashlib.sha256(key.encode()).hexdigest()[:12], 16)
    return seq[n % len(seq)]


def prose_gloss(tid: str, rows: list[dict[str, str]]) -> tuple[str, str, float, str]:
    prefix = tid[:12]
    for known, value in FIXED.items():
        if prefix.startswith(known):
            return (*value, "fixed recurrent-card default")
    pages = {r["page"] for r in rows}
    if all(r["dy_closure"] == "1" or r["b3"] == "1" for r in rows):
        gloss, source_class = choose(COMMITTED_TERMS, tid)
        return gloss, source_class, .27, "exact committed-card context default"
    if pages <= {"f10r", "f11r", "f55v", "f56r"}:
        gloss, source_class = choose(HERBAL_TERMS, tid)
        return gloss, source_class, .24 if len(rows) == 1 else .29, "Herbal article context default"
    if pages <= {"f81v", "f82r", "f83r"}:
        gloss, source_class = choose(BIO_TERMS, tid)
        return gloss, source_class, .23 if len(rows) == 1 else .28, "Biological application context default"
    # Portable tail: prefer an action/relation usable in both article and application.
    bridge = [
        ("then use it", "ACTION"), ("with warmed water", "MEDIUM"),
        ("according to the usual rule", "REFERENCE"),
        ("prepare the same portion", "PREPARATION"),
        ("afterwards apply it", "APPLICATION"),
        ("retain the stated measure", "REFERENCE"),
    ]
    gloss, source_class = choose(bridge, tid)
    return gloss, source_class, .25, "cross-register practical default"


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
BODY = ["head", "neck", "arms", "chest", "heart", "belly",
        "kidneys", "genitals", "thighs", "knees", "lower legs", "feet"]
PLANETS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]


def f67_segment(locus_num: int) -> int:
    starts = [13, 16, 19, 23, 26, 29, 32, 35, 38, 41, 44, 48]
    segment = 1
    for i, start in enumerate(starts, 1):
        if locus_num >= start:
            segment = i
    return segment


def astro_gloss(row: dict[str, str]) -> tuple[str, str, float, str]:
    page, locus = row["page"], row["locus"]
    n = int(locus.split(".")[-1])
    j = int(row["token_index"])
    if page == "f67r2":
        recurrent = {
            "daiin": "according to the stated rule", "s": "under",
            "aiin": "the stated rule", "ar": "for", "dy": "then complete",
            "y": "the current division", "os": "avoid", "air": "the proper time",
            "am": "the application", "dal": "the affected member",
            "chol": "with", "or": "likewise",
        }
        if row["eva"] in recurrent:
            return recurrent[row["eva"]], "ASTRO_RECURRENT_INSTRUCTION", .22, "f67r2-local recurrent surface"
        if 1 <= n <= 12:
            roles = [f"the zodiac division {SIGNS[n-1]}",
                     f"its influence upon the {BODY[n-1]}",
                     "the corresponding lunar condition"]
            return roles[min(j-1, 2)], "ZODIAC_SELECTOR", .25, "silent diagram owner"
        if 13 <= n <= 51:
            s = f67_segment(n)
            roles = [f"when the Moon is in {SIGNS[s-1]}",
                     f"protect the {BODY[s-1]}",
                     "avoid cutting or bleeding there",
                     "use only a gentle warm application"]
            return roles[(j-1) % 4], "ZODIAC_MEDICAL_RULE", .20, f"inherited segment {s}"
        if 52 <= n <= 63:
            s = n - 51
            return f"the body region governed by {SIGNS[s-1]}: {BODY[s-1]}", "ZODIAC_BODY_LABEL", .20, "isolated sign-owned label"
        if 64 <= n <= 71:
            p = PLANETS[n-64] if n <= 70 else "the combined planetary rule"
            return p, "PLANETARY_GOVERNOR", .23, "sevenfold local inventory"
        roles = ["consult the governing planet", "then find the zodiac division",
                 "observe the Moon's condition", "protect the governed member",
                 "choose a gentle bath", "avoid a forceful evacuation"]
        return roles[(j-1) % len(roles)], "DIAGRAM_OPERATING_INSTRUCTION", .19, "bottom prose instruction"
    if page == "f68r1":
        if n <= 4:
            roles = ["identify the Moon's present mansion", "locate its star in the field",
                     "retain the star's own name", "consult the corresponding influence",
                     "apply the mansion rule", "then pass to the next observation"]
            return roles[(j-1) % len(roles)], "MANSION_CATALOGUE_INSTRUCTION", .19, "top prose instruction"
        if 5 <= n <= 7:
            return ["the Sun", "its daylight influence", "the solar boundary"][n-5], "SOLAR_ANCHOR", .24, "sun-adjacent label"
        if 8 <= n <= 36:
            return f"the lunar-station name at spatial star locus f68r1.{n}", "SPATIAL_MANSION_NAME", .26, "no cyclic order imposed"
        roles = ["the Moon", "its mansion", "its present condition", "the applicable rule", "completion of the lunar lookup"]
        return roles[(j-1) % len(roles)], "LUNAR_CENTRAL_CAPTION", .22, "moon-owned circular caption"
    # f69v: the drawn position supplies mansion ordinal; the radial text gives a rule.
    if n >= 4:
        radial = {
            "okeey": "favorable for a warm bath", "sar": "especially after sunset",
            "okeo": "use a cool washing", "dy": "then stop",
            "ochoyk": "avoid bloodletting", "ykeey": "favorable for anointing",
            "ytory": "apply to the upper body", "oeesy": "rest and give no purge",
            "ytody": "complete a single rinse", "okody": "draw off excess fluid",
            "otody": "avoid a hot bath", "okeal": "apply below the waist",
            "okeod": "favorable for bathing", "oteeys": "repeat the wash once",
            "oteol": "use the same preparation", "ykeydy": "bathe until gently warm",
            "saral": "anoint the affected place", "saiir": "keep the patient at rest",
            "okolar": "use a smaller measure", "ykeody": "rinse and finish",
            "sarydy": "avoid a second application", "otchy": "use the dried herb",
            "okey": "make the ordinary bath", "d": "under the stated limit",
            "okodchy": "strain the herbal liquor", "okeody": "pour and finish",
            "okcheys": "apply a warm cloth", "oar": "observe the mansion",
            "alys": "withhold treatment if weak",
        }
        return radial.get(row["eva"], f"apply the rule written at mansion {n-3}"), "MANSION_ELECTION_RULE", .24, f"ordered radial locus {n-3}"
    outer_terms = [
        "begin with the Moon's mansion", "observe whether the influence is favorable",
        "choose bathing or abstention", "use the stated measure", "protect the governed member",
        "prepare water at gentle warmth", "repeat only when directed", "finish before the mansion changes",
    ]
    gloss, source_class = choose([(x, "MANSION_OPERATING_RULE") for x in outer_terms], page + ":" + row["eva"])
    return gloss, source_class, .18, f"outer circular instruction band {n}"


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_translation_appendix(ledger: list[dict[str, object]]) -> None:
    by_locus: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in ledger:
        by_locus[(str(row["page"]), str(row["locus"]))].append(row)
    out = ["# V16 R2 exhaustive fluent reading", "",
           "Every bracketed phrase is a speculative default expansion, not decoded plaintext.", ""]
    for page in PROSE_PAGES + ASTRO_PAGES:
        out += [f"## {page}", ""]
        keys = [key for key in by_locus if key[0] == page]
        keys.sort(key=lambda key: int(key[1].split(".")[-1]))
        for key in keys:
            rows = by_locus[key]
            if page in PROSE_PAGES:
                fields: dict[str, list[str]] = defaultdict(list)
                for row in rows:
                    fields[str(row["field_ordinal"])].append(str(row["default_English"]))
                rendered = " / ".join(", ".join(fields[k]) for k in sorted(fields, key=int))
            else:
                rendered = ", ".join(str(row["default_English"]) for row in rows)
            surfaces = " ".join(str(row["surface"]) for row in rows)
            out.append(f"- `{key[1]}` `{surfaces}` — {rendered}.")
        out.append("")
    (OUT / "V16_R2_FLUENT_TRANSLATIONS.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def main() -> None:
    formal = guarded("gdt327_joint_tuple_interlinear.tsv", PROSE_PAGES,
                     ["page", "locus", "group_index", "group_count", "record_ordinal",
                      "field_ordinal", "within_field_position", "joint_tuple_id",
                      "dy_closure", "b3", "observed_wrapper", "register"])
    surfaces = guarded("gdt276_event_inventory.tsv", PROSE_PAGES,
                       ["page", "locus", "group_index", "raw_token"])
    surface = {(r["locus"], r["group_index"]): r["raw_token"] for r in surfaces}
    assert len(formal) == len(surface) == 381
    by_type: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in formal:
        by_type[row["joint_tuple_id"]].append(row)

    assignments = {tid: prose_gloss(tid, rows) for tid, rows in by_type.items()}
    for tid, rows in by_type.items():
        if len(rows) == 1:
            gloss, source_class, confidence, rule = assignments[tid]
            assignments[tid] = (gloss, source_class + "|CONTEXT_DEFAULT", confidence,
                                rule + "; singleton forced concrete")
    ledger: list[dict[str, object]] = []
    for event_index, row in enumerate(formal, 1):
        gloss, source_class, confidence, rule = assignments[row["joint_tuple_id"]]
        ledger.append({
            "page": row["page"], "locus": row["locus"],
            "record": row["record_ordinal"], "line": row["locus"],
            "event_index": event_index, "surface": surface[(row["locus"], row["group_index"])],
            "exact_tuple_id": row["joint_tuple_id"], "default_English": gloss,
            "source_class": source_class, "confidence": f"{confidence:.2f}",
            "inheritance_context_rule": rule,
            "field_ordinal": row["field_ordinal"], "within_field_position": row["within_field_position"],
            "closure": "DY" if row["dy_closure"] == "1" else "B3" if row["b3"] == "1" else "OPEN",
            "scope": "PROSE_GDT327",
        })

    astro = guarded("transcription/voynich_zl3b_tokens.tsv", ASTRO_PAGES,
                    ["page", "locus", "line_number", "code", "relation", "kind",
                     "subtype", "token_index", "eva"])
    assert len(astro) == 395
    astro_counts = Counter((row["page"], row["eva"]) for row in astro)
    for offset, row in enumerate(astro, len(ledger) + 1):
        gloss, source_class, confidence, rule = astro_gloss(row)
        if astro_counts[(row["page"], row["eva"])] == 1:
            source_class += "|CONTEXT_DEFAULT"
            rule += "; singleton forced concrete"
        ledger.append({
            "page": row["page"], "locus": row["locus"], "record": row["line_number"],
            "line": row["locus"], "event_index": offset, "surface": row["eva"],
            "exact_tuple_id": f"ASTRO:{row['page']}:{row['eva']}", "default_English": gloss,
            "source_class": source_class, "confidence": f"{confidence:.2f}",
            "inheritance_context_rule": rule, "field_ordinal": row["code"],
            "within_field_position": row["token_index"], "closure": "DIAGRAM_OWNED",
            "scope": "ASTRO_ZL3B_PRIMARY",
        })

    lexicon = []
    for tid, rows in sorted(by_type.items()):
        gloss, source_class, confidence, rule = assignments[tid]
        variants = sorted({surface[(r["locus"], r["group_index"])] for r in rows})
        lexicon.append({
            "namespace": "GDT327_EXACT", "form_id": tid,
            "surface_variants": "|".join(variants), "events": len(rows),
            "pages": "|".join(sorted({r["page"] for r in rows})),
            "primary_default_English": gloss, "source_class": source_class,
            "confidence": f"{confidence:.2f}", "polysemy_rule": "NONE",
            "assignment_basis": rule,
        })
    by_astro: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in astro:
        by_astro[(row["page"], row["eva"])].append(row)
    for (page, eva), rows in sorted(by_astro.items()):
        values = [astro_gloss(r) for r in rows]
        glosses = sorted({v[0] for v in values})
        classes = sorted({v[1] for v in values})
        if len(rows) == 1:
            classes.append("CONTEXT_DEFAULT")
        lexicon.append({
            "namespace": f"ASTRO_LOCAL:{page}", "form_id": eva,
            "surface_variants": eva, "events": len(rows), "pages": page,
            "primary_default_English": " || ".join(glosses),
            "source_class": "|".join(classes),
            "confidence": f"{min(v[2] for v in values):.2f}",
            "polysemy_rule": "LOCUS_OWNED" if len(glosses) > 1 else "NONE",
            "assignment_basis": "Astro page-local diagram namespace",
        })

    write_tsv(OUT / "V16_R2_COMPLETE_TRANSLATION_LEDGER.tsv", ledger)
    write_tsv(OUT / "V16_R2_COMPLETE_DEFAULT_LEXICON.tsv", lexicon)
    write_translation_appendix(ledger)
    print({"prose_events": len(formal), "prose_types": len(by_type),
           "astro_groups": len(astro), "astro_local_types": len(by_astro),
           "ledger_rows": len(ledger), "lexicon_rows": len(lexicon)})


if __name__ == "__main__":
    main()
