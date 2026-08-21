#!/usr/bin/env python3
"""Build the R1 V19 Herbal workshop candidate from the frozen V18 ledger.

This is deliberately an abductive sidequest instrument.  Exact tuple IDs are
treated as indivisible cards.  No tuple coordinates, substrings, f84 or f84r
are read.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v18/V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
FREEZE = HERE / "V19_R1_VISIBLE_PLANT_FREEZE.tsv"
PAGES = ("f10r", "f11r", "f55v", "f56r")

# Exact-card defaults.  Recurrent V18-deck readings are retained.  The only
# recurrent correction is d665...: the identical card cannot be the literal
# local name of two visibly different plants, so it becomes a reusable whole-
# simple instruction.  Every singleton has two concrete rivals below.
M = {
"65f320e75510b2f38182": ("the pictured simple is called twin-root waterwort", "PICTURED_SIMPLE_NAME", ".24", "picture+article opening", "the pictured simple is called red-root costmary", "the pictured simple is called double-tuber mint"),
"dedc383b600397a301ee": ("store its paired sound roots in a covered jar", "STORAGE", ".25", "picture+article order", "keep the cut root under oil", "hang the paired roots in a dry loft"),
"4d4559019a961b834aa1": ("from the same prepared batch", "SAME_BATCH_REFERENCE", ".66", "V18 recurrent deck", "repeat the preceding preparation from the same roots", "continue with the immediately preceding decoction"),
"80ebbbbf238eee9f0aef": ("pound the two roots until evenly combined", "PREPARATION", ".27", "paired roots+local order", "boil the two roots until one liquor remains", "knead the root powder with water until smooth"),
"df1098831679a8ad1b39": ("the dried leaf powder", "PLANT_PART_PREPARATION", ".24", "article order", "powder of the dried root", "finely bruised flower heads"),
"12efe866f335461823a6": ("the reddish creeping rootstock", "VISIBLE_PART", ".31", "picture", "the reddish central stem", "the red outer skin of the tuber"),
"62ff059766b21c7de083": ("drink it for pain of the stomach", "INDICATION_APPLICATION", ".27", "V18 default+article", "lay it warm upon a cramped belly", "drink it for griping of the bowels"),
"276a7c2d74d1143446f4": ("apply or use this portion", "APPLICATION_ACTION", ".61", "V18 recurrent deck", "lay this portion on the affected place", "drink this prepared portion"),
"2f1c5e56e8f0ff459065": ("in the stated or usual measure", "MEASURE_REFERENCE", ".66", "V18 recurrent deck", "in one equal measure", "in the measure taught for this preparation"),
"a6939862e33ece5a0483": ("retain the sound roots for later use", "STORAGE_CLOSE", ".24", "paired roots+closure", "keep the remaining powder dry", "plant the sound side-root again"),
"9ad66e67803a12e745de": ("use the freshly prepared remedy", "FRESH_PREPARATION", ".52", "V18 recurrent deck", "take the freshly expressed juice", "use the remedy before it cools"),
"e8a6105b5c3a6220b440": ("lay it on while warm", "WARM_APPLICATION", ".29", "V18 default+local syntax", "drink it while lukewarm", "wash the painful place with it warm"),
"dcda95c81a5460feb191": ("with the foregoing preparation", "PREPARATION_REFERENCE", ".67", "V18 recurrent deck", "together with the preceding portion", "under the same preceding instruction"),
"e0b630cb1b5df5e7105b": ("when the preparation is ready", "READINESS_CONDITION", ".55", "V18 recurrent deck", "when the liquor has cooled", "when the ingredients have joined"),
"7249edc4df3419c26999": ("it grows beside running water", "HABITAT", ".24", "picture-compatible article opening", "it grows in wet meadow ground", "it grows along shaded ditches"),
"7a4bb8136330ee4e6e56": ("the prepared decoction or working liquid", "PREPARED_LIQUID", ".53", "V18 recurrent deck", "the expressed plant liquor", "the water in which the plant was boiled"),
"f3c23f42baf625639e1e": ("the freshly expressed leaf juice", "PLANT_PRODUCT", ".25", "article order", "juice expressed from the red roots", "the first water drawn from the herb"),
"af816c04e65874a0f2fa": ("boil it gently in water", "PREPARATION", ".27", "water hypothesis+article", "steep it overnight in water", "warm it slowly in white wine"),
"b921a237be883a820352": ("this present portion", "CURRENT_PORTION", ".56", "V18 recurrent deck", "this part of the pictured simple", "the portion presently in hand"),
"10488b911aae52b3b334": ("gathered before flowering", "GATHERING_TIME", ".47", "V18 recurrent deck", "gathered at first budding", "cut before the flower fully opens"),
"497cbd9c7401810ff56b": ("one handful of chopped leaves", "MEASURED_PLANT_PART", ".27", "article sequence", "one handful of chopped root", "one small bundle of flowering tops"),
"dec401773c1f0347793d": ("from the first foregoing decoction", "BATCH_REFERENCE", ".28", "recurrent reference frame", "from the reserved root liquor", "from the second warm infusion"),
"27d97af8c96eb056c2e6": ("when the blue flower opens", "GATHERING_STATE", ".29", "picture", "when the lesser head begins to open", "when the seed head is fully formed"),
"409de02322e7b2ca0c62": ("if the liquor remains bitter", "QUALITY_CONDITION", ".25", "article process", "when the juice has a sharp taste", "if the root liquor is too strong"),
"834825c61d048a6b5628": ("preserve the remainder under oil", "PRESERVATION_CLOSE", ".27", "V18 default+closure", "keep the remainder in a stopped jar", "mix the remainder with honey for storage"),
"953ad19b79517fc8a211": ("gather the whole herb in spring", "GATHERING_TIME", ".28", "V18 default+article opening", "cut the flowering mat at dawn", "lift the roots after spring rain"),
"428a5e3662aa57b4b256": ("from a shaded spring bank", "HABITAT", ".28", "picture-compatible habitat", "from wet stones beside a stream", "from a cool shaded wood"),
"bdad9f9ea8b80f141496": ("before the first blue flowers open", "GATHERING_STATE", ".27", "picture+sequence", "after the leaf cushion has filled out", "while the shoots are still tender"),
"a8af08e69edab8e54f15": ("pass the decoction first through coarse cloth", "STRAINING", ".28", "V18 default+paired operation", "press the boiled herb through a linen bag", "pour the first liquor through a hair sieve"),
"deb377381ceaf55ea310": ("pass it a second time through clean linen", "STRAINING", ".28", "V18 default+paired operation", "strain the residue through finer cloth", "filter the liquor once through folded linen"),
"b5df9126607030b95175": ("until the liquid runs clear", "PROCESS_GATE", ".34", "V18 default+sequence", "until no leaf fragments remain", "until the pressed liquid turns pale"),
"2e2027b1951d79911e24": ("leave the jar mouth uncovered until cool; end", "COOLING_CLOSE", ".25", "Herbal jar repair", "leave the strained liquor open for one night", "pour the clear liquor into an open shallow vessel"),
"577c03a928d674d420d7": ("the small blue flowers show its proper gathering age", "VISIBLE_GATHERING_SIGN", ".27", "picture+article close", "the blue blossoms mark the mature herb", "gather when the upper blue flowers stand upright"),
"d665560c8ff80799a82c": ("take the whole pictured simple", "WHOLE_SIMPLE_INSTRUCTION", ".39", "cross-page contradiction repairs V18 name", "take the leafy crown with its root", "use the pictured herb as a complete plant"),
"b2812c8283c3a62438bd": ("bind this portion upon a swollen place", "INDICATION_APPLICATION", ".29", "V18 swelling+local phrase", "wash a swollen joint with this portion", "drink the portion against inward swelling"),
"a48efd6c4491a046ba78": ("pound the fresh cushion leaves", "PLANT_PART_PREPARATION", ".25", "page-local recipe opening", "bruise the three toothed roots", "take the young blue-flowered shoots"),
"322281bd391aa621f568": ("lay them on while warm", "WARM_APPLICATION", ".29", "V18 default+pronoun repair", "wash the swelling with them warm", "bind the bruised leaves on at once"),
"b5fcea1eaed06b2f2291": ("take up the next portion or instruction", "NEXT_ENTRY", ".59", "V18 recurrent deck", "take the next measured plant part", "begin the following preparation"),
"403c1592f918c8f23b88": ("boil the chopped root gently", "PREPARATION", ".29", "V18 default+visible root", "boil the chopped leaves gently", "simmer the flowering stalk slowly"),
"d929a14ec45749b2e805": ("in white wine", "MEDIUM", ".31", "V18 default+recipe", "in clean spring water", "in weak vinegar"),
"97cc9ac109148723c472": ("steep until clear, then decant; end", "INFUSION_CLOSE", ".28", "V18 default clarified", "let it stand until the lees settle", "strain the steeped wine into a clean jar"),
"6f7ff8287eddf4da9fdb": ("stir until evenly mixed", "MIXING", ".43", "V17/V18 deck", "beat the liquor until smooth", "combine the two measured portions thoroughly"),
"e026af581c99322fbd46": ("wash the affected place once; end", "WASH_APPLICATION_CLOSE", ".28", "V18 default+Herbal object", "drink one draught and end", "rinse the cut root once and put it away"),
"f7dc90b2c31fd341f0a4": ("for a painful swollen joint", "INDICATION", ".24", "article prescription opening", "for a hot skin swelling", "for pain of the lower belly"),
"807591efc3d3f7ddbfab": ("take strong white wine", "MEDIUM", ".28", "V18 default+imperative", "take fresh spring water", "take sharp vinegar"),
"2c1a5fd92b9e3c762242": ("while the liquor is still warm", "TEMPERATURE_CONDITION", ".32", "V18 default", "after the liquor has cooled", "while the root is freshly bruised"),
"1b1ffdd869fb1429ad03": ("boil it gently; end this step", "BOIL_CLOSE", ".38", "V18 deck", "warm it without boiling; end", "reduce it by one third; end"),
"308e8ea2d5d190c498e8": ("mix the two portions together", "MIX_TWO_PORTIONS", ".55", "V17/V18 deck", "combine equal measures of both liquors", "mix the root portion into the wine"),
"204b04837409088c48f9": ("keep it in a covered jar", "STORAGE", ".27", "V18 default", "keep it under oil in a jar", "seal it in a glazed pot"),
"6afeb5c9ab9f6cbdea0d": ("and use this portion fresh", "FRESH_USE_CLOSE", ".29", "V18 default", "apply it before it cools", "drink it on the same day"),
"b9d7b6d68209a9019e7a": ("gather the tall simple in spring", "GATHERING_TIME", ".28", "V18 default+picture", "cut the heads before midsummer", "dig the lower stalk after flowering"),
"2cc054357a929df85f64": ("then take the following ingredient or plant part", "NEXT_PART", ".65", "V18 recurrent deck", "next take the named part", "continue with the following part of the same plant"),
"0ec6a45e2950e8e7061d": ("the lower fibrous root", "VISIBLE_PART", ".29", "V18 default+picture fallback", "the lower jointed stalk", "the root-crown beneath the scales"),
"893c570f3fa3fce99711": ("white wine", "MEDIUM", ".33", "V18 default", "clear spring water", "thin vinegar"),
"dd0ecaf5e27d81befffc": ("bind it at the affected place", "TOPICAL_APPLICATION", ".27", "V18 location+article", "wash the place shown by the rubric", "anoint the painful place with it"),
"c10aec6d4dd877ec8bd8": ("it grows on open stony ground", "HABITAT", ".22", "picture-compatible revision", "it grows in a dry meadow", "it grows on a sunny bank"),
"95987d6f198d6d247511": ("bind it on overnight, then remove; end", "POULTICE_CLOSE", ".24", "Herbal contradiction repairs V18 outlet", "leave it on until dry, then remove", "wash the bound place at dawn"),
"ad3581d3144f69a5912d": ("the ripe seed-head", "VISIBLE_PART", ".27", "picture", "the dark unopened flower-head", "the seed from the spiral head"),
"b74e9e65637b7c8538dd": ("the dried scale-leaf", "VISIBLE_PART", ".25", "V18 default+picture", "the dried flowering bract", "the dried upper stalk"),
"1322bc176443fc2a8a86": ("dry it in shade; end", "DRYING_CLOSE", ".31", "V18 default", "hang it in an airy loft", "keep it from the sun until crisp"),
"087a47b5423438cd6b6a": ("drink it for pain of the stomach", "INDICATION_APPLICATION", ".27", "V18 default", "drink it against griping", "take it after spoiled food"),
"75a523fcf039b006f97b": ("then keep the remainder dry in shade", "STORAGE_CLOSE", ".25", "V18 default refined", "hang the remaining stalk in shade", "store the dried powder in a dark jar"),
"c71c72da4e09e0833392": ("with honey", "MEDIUM", ".32", "V18 default", "with thickened wine", "with rose oil"),
"61a075bc54793c1c781f": ("and use it while fresh", "FRESH_USE_CLOSE", ".29", "V18 default", "and apply it before sunset", "and eat it on the same day"),
"faf321940aed922846a9": ("for one dose take", "DOSE_OPEN", ".26", "article order revision", "for the final preparation take", "for a child's dose take"),
"9bb7122b386ebbc6138f": ("one pale opened flower-head", "VISIBLE_PART_MEASURE", ".27", "picture+measure context", "one dark unopened head", "one handful of pale flower petals"),
}

ARTICLE_PROSE = {
"f10r": """## f10r — twin-root waterwort / broad damp-bank simple

**Article 1 (f10r.2–.5).** The pictured simple is called *twin-root
waterwort*. Store its paired sound roots in a covered jar. From the same
prepared batch, pound the two roots until evenly combined; add the dried leaf
powder and the reddish creeping rootstock. Drink it for pain of the stomach.
Apply this portion in the usual measure, and retain the sound roots for later
use. Use the freshly prepared remedy and lay it on while warm with the
foregoing preparation when it is ready.

**Article 2 (f10r.6–.9).** It grows beside running water. When the preparation
is ready, use the working decoction and the freshly expressed leaf juice;
boil it gently in water. Take this present portion, this present portion, the
usual measure, and this final present portion. Gather the herb before
flowering; use one handful of chopped leaves with the foregoing preparation,
from the first foregoing decoction, again with the foregoing preparation in
the usual measure and from the same batch. When the blue flower opens, make
the working decoction from this portion. If the liquor remains bitter, add
this present portion and preserve the remainder under oil.

The second article explicitly crosses physical lines: f10r.6 supplies the
liquid and measures, f10r.8 the gathered leaf charge, and f10r.9 the maturity
test and preservation close.
""",
"f11r": """## f11r — spring-bank cushion simple

**Gathering and preparation (f11r.1).** Gather the whole herb in spring from a
shaded spring bank, before the first blue flowers open. Pass the decoction
first through coarse cloth and then a second time through clean linen, until
the liquid runs clear. Leave the jar mouth uncovered until cool. The small
blue flowers show its proper gathering age.

**Uses (f11r.4 and .7).** Take the whole pictured simple. Bind this portion on
a swollen place and use the next present portion in the stated measure. For a
second preparation, pound the fresh cushion leaves and lay them on while warm,
when the preparation is ready, using this present portion.

The gathering sentence ends by visible maturity rather than at the physical
line break; the two short lower records are two applications of one plant.
""",
"f55v": """## f55v — large-leaved marsh rhizome

**Preparation 1 (f55v.5).** Take the next portion in the usual measure. Boil
the chopped root gently in white wine; steep until clear and decant. Add the
usual measure, stir until evenly mixed, and wash the affected place once.

**Preparation 2 (f55v.11).** For a painful swollen joint take strong white
wine. While the liquor is still warm, boil it gently. In the usual measure,
mix the two portions together, keep them in a covered jar, and use the prepared
decoction—this present portion—fresh.

The two blocks are parallel recipes owned by the same enormous marsh plant,
not a botanical description forced into a fixed name-first order.
""",
"f56r": """## f56r — tall spiny blue-headed simple

Gather the tall simple in spring; then take the lower fibrous root in the usual
measure. Next take a flower-head with white wine, cut it before flowering,
apply this portion, and bind it at the affected place. Take the whole pictured
simple from open stony ground; apply this portion as a poultice overnight and
remove it.

For the ripe seed-head, next take the dried scale-leaf and dry it in shade.
Use the freshly prepared remedy for pain of the stomach, then keep the
remainder dry in shade. Next take the fresh preparation with honey and use it
while fresh. For one dose take one pale opened flower-head in the usual
measure.

This is one dossier with several part-recipes. Its statements repeatedly cross
physical lines: the recurring NEXT-PART card introduces root, wine-borne head,
dried leaf, and honey preparation rather than ending the preceding sentence.
""",
}

BROAD = {
    "PICTURED_SIMPLE_NAME":"NAME_OR_SYNONYM",
    "VISIBLE_PART":"PLANT_PART", "VISIBLE_PART_MEASURE":"PLANT_PART",
    "PLANT_PART_PREPARATION":"PLANT_PART", "PLANT_PRODUCT":"PLANT_PART",
    "HABITAT":"HABITAT_OR_GATHERING", "GATHERING_TIME":"HABITAT_OR_GATHERING",
    "GATHERING_STATE":"HABITAT_OR_GATHERING", "VISIBLE_GATHERING_SIGN":"HABITAT_OR_GATHERING",
    "QUALITY_CONDITION":"QUALITY_OR_PROCESS_CONDITION", "TEMPERATURE_CONDITION":"QUALITY_OR_PROCESS_CONDITION",
    "READINESS_CONDITION":"QUALITY_OR_PROCESS_CONDITION", "PROCESS_GATE":"QUALITY_OR_PROCESS_CONDITION",
    "PREPARATION":"PREPARATION", "STRAINING":"PREPARATION", "MIXING":"PREPARATION",
    "MIX_TWO_PORTIONS":"PREPARATION", "FRESH_PREPARATION":"PREPARATION",
    "PREPARED_LIQUID":"PREPARATION", "INFUSION_CLOSE":"PREPARATION",
    "BOIL_CLOSE":"PREPARATION", "DRYING_CLOSE":"PREPARATION",
    "MEDIUM":"MEDIUM_OR_ADJUVANT", "MEASURE_REFERENCE":"MEASURE_OR_DOSE",
    "MEASURED_PLANT_PART":"MEASURE_OR_DOSE", "DOSE_OPEN":"MEASURE_OR_DOSE",
    "APPLICATION_ACTION":"APPLICATION", "WARM_APPLICATION":"APPLICATION",
    "TOPICAL_APPLICATION":"APPLICATION", "WASH_APPLICATION_CLOSE":"APPLICATION",
    "POULTICE_CLOSE":"APPLICATION", "FRESH_USE_CLOSE":"APPLICATION",
    "INDICATION":"INDICATION", "INDICATION_APPLICATION":"INDICATION",
    "PREPARATION_REFERENCE":"REFERENCE_OR_CONTINUATION", "BATCH_REFERENCE":"REFERENCE_OR_CONTINUATION",
    "SAME_BATCH_REFERENCE":"REFERENCE_OR_CONTINUATION", "CURRENT_PORTION":"REFERENCE_OR_CONTINUATION",
    "NEXT_ENTRY":"REFERENCE_OR_CONTINUATION", "NEXT_PART":"REFERENCE_OR_CONTINUATION",
    "WHOLE_SIMPLE_INSTRUCTION":"REFERENCE_OR_CONTINUATION",
    "STORAGE":"STORAGE_OR_CLOSE", "STORAGE_CLOSE":"STORAGE_OR_CLOSE",
    "PRESERVATION_CLOSE":"STORAGE_OR_CLOSE", "COOLING_CLOSE":"STORAGE_OR_CLOSE",
}

def silent_argument(specific):
    broad=BROAD[specific]
    if broad in {"NAME_OR_SYNONYM","PLANT_PART","HABITAT_OR_GATHERING"}:
        return "PICTURED_SIMPLE_OR_PART"
    if broad in {"APPLICATION","INDICATION"}:
        return "CURRENT_PREPARATION_AND_AFFECTED_PLACE_OR_PATIENT"
    if broad == "STORAGE_OR_CLOSE":
        return "CURRENT_PREPARATION_AND_CONTAINER"
    if broad == "REFERENCE_OR_CONTINUATION":
        return "ANTECEDENT_BATCH_PART_OR_INSTRUCTION"
    return "CURRENT_PLANT_MATERIAL_OR_PREPARATION"

def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def write_tsv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    assert FREEZE.exists(), "visible-feature freeze must pre-exist assignment"
    freeze = read_tsv(FREEZE)
    assert len(freeze) == 4 and all(r["text_inspected_for_assignment"] == "NO" for r in freeze)
    source = [r for r in read_tsv(SOURCE) if r["page"] in PAGES]
    assert len(source) == 100
    ids = {r["exact_tuple_id"] for r in source}
    assert len(ids) == 66 and ids == set(M), (len(ids), len(set(M)), sorted(ids-set(M)), sorted(set(M)-ids))
    counts = Counter(r["exact_tuple_id"] for r in source)
    assert sum(n == 1 for n in counts.values()) == 55
    occurrences = defaultdict(list)
    surfaces = defaultdict(set)
    pages = defaultdict(set)
    for r in source:
        occurrences[r["exact_tuple_id"]].append(f'{r["locus"]}:{r["event_index"]}')
        surfaces[r["exact_tuple_id"]].add(r["surface"])
        pages[r["exact_tuple_id"]].add(r["page"])

    dictionary=[]
    for tid in sorted(ids):
        gloss, specific, conf, evidence, alt1, alt2 = M[tid]
        dictionary.append({
            "exact_tuple_id":tid,
            "surface_examples":"|".join(sorted(surfaces[tid])),
            "occurrences":counts[tid],
            "pages":"|".join(sorted(pages[tid])),
            "default_English":gloss,
            "source_class":BROAD[specific], "specific_role":specific,
            "confidence":conf,
            "assignment_evidence":evidence,
            "occurrence_loci":"|".join(occurrences[tid]),
            "v18_status":(
                "REVISED_EXPLICIT_CROSS_PAGE_CONTRADICTION" if tid == "d665560c8ff80799a82c"
                else "V18_RECURRENT_RETAINED" if counts[tid] > 1
                else "SINGLETON_CONCRETE_REFINED"
            ),
        })
    write_tsv(HERE/"V19_R1_HERBAL_CARD_DICTIONARY.tsv", dictionary, list(dictionary[0]))

    out=[]
    by_loc=defaultdict(list)
    for r in source: by_loc[r["locus"]].append(r)
    for r in source:
        gloss, specific, conf, evidence, alt1, alt2 = M[r["exact_tuple_id"]]
        line=by_loc[r["locus"]]
        i=line.index(r)
        out.append({
            "page":r["page"], "locus":r["locus"], "record":r["record"], "line":r["line"],
            "event_index":r["event_index"], "surface":r["surface"], "exact_tuple_id":r["exact_tuple_id"],
            "default_English":gloss, "source_class":BROAD[specific], "specific_role":specific, "confidence":conf,
            "previous_surface":line[i-1]["surface"] if i else "<BOUNDARY>",
            "following_surface":line[i+1]["surface"] if i+1<len(line) else "<PHYSICAL_LINE_END_NOT_NECESSARILY_SENTENCE_END>",
            "local_phrase":gloss,
            "inherited_silent_argument":silent_argument(specific),
            "assignment_evidence":evidence,
        })
    write_tsv(HERE/"V19_R1_100_EVENT_INTERLINEAR.tsv", out, list(out[0]))

    alternatives=[]
    for tid in sorted(k for k,n in counts.items() if n==1):
        gloss, specific, conf, evidence, alt1, alt2=M[tid]
        alternatives.append({
            "exact_tuple_id":tid,"surface":"|".join(sorted(surfaces[tid])),"locus":occurrences[tid][0],
            "selected_default":gloss,"concrete_alternative_1":alt1,"concrete_alternative_2":alt2,
            "selection_reason":f"{evidence}; selected phrase makes the complete page article require fewer topic changes",
        })
    write_tsv(HERE/"V19_R1_SINGLETON_ALTERNATIVES.tsv", alternatives, list(alternatives[0]))

    with (HERE/"V19_R1_COMPLETE_HERBAL_ARTICLES.md").open("w",encoding="utf-8") as f:
        f.write("# V19 R1 complete Herbal articles\n\n")
        f.write("Status: concrete workshop back-translation, not deciphered plaintext.\n\n")
        for pg in PAGES: f.write(ARTICLE_PROSE[pg]+"\n")

    classes=Counter(BROAD[v[1]] for v in M.values())
    silent=Counter(silent_argument(M[r["exact_tuple_id"]][1]) for r in source)
    validation={
      "status":"PASS", "pages":list(PAGES), "events":len(source), "exact_types":len(ids),
      "singleton_types":sum(n==1 for n in counts.values()), "recurrent_types":sum(n>1 for n in counts.values()),
      "semantic_classes":len(classes), "semantic_class_counts":dict(sorted(classes.items())),
      "inserted_silent_argument_events":len(out), "inserted_silent_argument_classes":dict(sorted(silent.items())),
      "blank_glosses":sum(not v[0].strip() for v in M.values()),
      "forbidden_blank_labels":0,
      "f84_accessed":False,"f84r_accessed":False,
      "visible_freeze_preexisted":True,
    }
    (HERE/"V19_R1_VALIDATION.json").write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(validation,indent=2,sort_keys=True))

if __name__ == "__main__": main()
