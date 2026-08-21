#!/usr/bin/env python3
"""Build the R2 V19 complete Herbal reconstruction from the frozen V18 ledger."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v18/V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ("f10r", "f11r", "f55v", "f56r")


# Exact cards remain atomic.  None of the assignments below uses spelling,
# substrings or an internal GDT327 coordinate.
M = {
"65f320e75510b2f38182": ("take the fibrous lower root", "PLANT_PART_TAKE", ".35", "wash the broad leaves", "cut the red basal swellings"),
"dedc383b600397a301ee": ("wash it in running water", "WATER_WASH", ".34", "steep it in spring water", "clean it with cold water"),
"4d4559019a961b834aa1": ("from the same prepared batch", "SAME_BATCH_REFERENCE", ".66", "from the same harvested plant", "from the preceding decoction"),
"80ebbbbf238eee9f0aef": ("pound until the mass is even", "POUNDING_GATE", ".38", "mix until evenly joined", "knead until no coarse piece remains"),
"df1098831679a8ad1b39": ("reduce it to a coarse powder", "POUNDING_RESULT", ".38", "bruise it to release the juice", "grind it to a fine powder"),
"12efe866f335461823a6": ("add red wine", "MEDIUM_WINE", ".32", "use the reddish stem", "add red vinegar"),
"62ff059766b21c7de083": ("drink it for pain of the stomach", "INDICATION_INTERNAL", ".38", "drink it against griping", "take it for a cold stomach"),
"276a7c2d74d1143446f4": ("apply or use this portion", "APPLICATION_ACTION", ".61", "administer this portion", "lay this portion on the affected place"),
"2f1c5e56e8f0ff459065": ("in the stated or usual measure", "MEASURE_REFERENCE", ".66", "in equal measure", "in the customary dose"),
"a6939862e33ece5a0483": ("keep the remaining root dry", "STORAGE_ROOT", ".34", "keep the remaining powder dry", "hang the root in shade"),
"9ad66e67803a12e745de": ("use the freshly prepared remedy", "FRESH_PREPARATION", ".52", "take the freshly expressed juice", "apply the preparation before it cools"),
"e8a6105b5c3a6220b440": ("apply it while warm", "WARM_APPLICATION", ".35", "drink it while warm", "bind it on while warm"),
"dcda95c81a5460feb191": ("with the foregoing preparation", "PREPARATION_REFERENCE", ".67", "together with the preceding portion", "using the same liquid"),
"e0b630cb1b5df5e7105b": ("when the preparation is ready", "READINESS_CONDITION", ".55", "when it has settled", "when it is sufficiently warm"),
"7249edc4df3419c26999": ("it grows in damp meadow ground", "HABITAT_MOIST", ".31", "it grows beside running water", "it is found in low shaded ground"),
"7a4bb8136330ee4e6e56": ("the prepared decoction or working liquid", "PREPARED_LIQUID", ".53", "the expressed plant liquor", "the strained infusion"),
"f3c23f42baf625639e1e": ("add the expressed juice", "PLANT_JUICE", ".36", "add clear spring water", "add the juice of the root"),
"af816c04e65874a0f2fa": ("boil it gently", "GENTLE_BOIL", ".36", "steep it without hard boiling", "warm it over a small fire"),
"b921a237be883a820352": ("this present portion", "CURRENT_PORTION", ".56", "the portion just named", "the present plant part"),
"10488b911aae52b3b334": ("gathered before flowering", "GATHERING_TIME", ".45", "cut before the flower opens", "take while the leaves are young"),
"497cbd9c7401810ff56b": ("one handful", "HANDFUL_MEASURE", ".42", "one small bundle", "as much as the hand holds"),
"dec401773c1f0347793d": ("from the foregoing batch", "BATCH_REFERENCE", ".38", "from the same decoction", "from the preceding measure"),
"27d97af8c96eb056c2e6": ("when its flower has opened", "FLOWERING_GATE", ".35", "when the flower first appears", "after the head has formed"),
"409de02322e7b2ca0c62": ("until a bitter taste remains", "TASTE_GATE", ".37", "until its sharp taste is evident", "until the liquor is strongly bitter"),
"834825c61d048a6b5628": ("preserve that portion under oil", "OIL_STORAGE", ".39", "mix that portion with oil", "keep it in an oiled vessel"),
"953ad19b79517fc8a211": ("gather the root in spring", "GATHERING_TIME", ".36", "gather the young leaves in spring", "dig it before midsummer"),
"428a5e3662aa57b4b256": ("from shaded woodland", "HABITAT_SHADE", ".34", "from a damp woodland edge", "from shaded garden ground"),
"bdad9f9ea8b80f141496": ("before the flowering crown opens", "GATHERING_TIME", ".33", "while the basal leaves are tender", "before the stem hardens"),
"a8af08e69edab8e54f15": ("press the bruised root through cloth", "CLOTH_PRESS", ".37", "strain the root decoction through linen", "wrap the bruised root in cloth"),
"deb377381ceaf55ea310": ("strain the liquor a second time", "SECOND_STRAIN", ".35", "press the cloth once more", "filter it through a finer linen"),
"b5df9126607030b95175": ("until the liquid runs clear", "CLARITY_GATE", ".57", "until no sediment passes", "until the liquor is bright"),
"2e2027b1951d79911e24": ("leave the strained liquor uncovered to cool", "COOLING_CLOSURE", ".33", "leave the mouth of the vessel open", "set the clear liquor aside to cool"),
"577c03a928d674d420d7": ("reserve the flowering crown", "FLOWERING_PART", ".31", "keep the young flower heads", "separate the upper flowering stems"),
"d665560c8ff80799a82c": ("of this pictured simple", "PICTURED_OWNER_REFERENCE", ".42", "from the same plant", "as for the herb shown here"),
"b2812c8283c3a62438bd": ("bind it upon a swollen place", "INDICATION_EXTERNAL", ".38", "apply it to a hard swelling", "wash an inflamed place with it"),
"a48efd6c4491a046ba78": ("make a warm poultice from its leaves", "POULTICE_PREPARATION", ".34", "make a warm wash from its root", "bruise the fresh leaves for a plaster"),
"322281bd391aa621f568": ("lay it on while warm", "WARM_APPLICATION", ".35", "wash the place while the liquor is warm", "bind on the warm bruised leaves"),
"b5fcea1eaed06b2f2291": ("take the next measured portion", "NEXT_PORTION_HEAD", ".68", "take another portion", "enter the following preparation"),
"403c1592f918c8f23b88": ("boil the broad leaf gently", "GENTLE_BOIL", ".34", "bruise the fresh leaf", "simmer the root gently"),
"d929a14ec45749b2e805": ("in white wine", "MEDIUM_WINE", ".38", "in spring water", "in thin vinegar"),
"97cc9ac109148723c472": ("steep it until the liquor is clear", "STEEP_CLOSURE", ".36", "let it settle until clear", "macerate it overnight"),
"6f7ff8287eddf4da9fdb": ("stir until evenly mixed", "MIXING_ACTION", ".62", "mix until the leaf liquor is uniform", "stir the two measures together"),
"e026af581c99322fbd46": ("wash the sore place once", "WASH_APPLICATION", ".35", "rinse the mouth once", "wash the wound with one portion"),
"f7dc90b2c31fd341f0a4": ("for its second medicinal use", "USE_CLAUSE_HEAD", ".32", "for an inward remedy", "for a fresh external remedy"),
"807591efc3d3f7ddbfab": ("add white wine", "MEDIUM_WINE", ".37", "add clear water", "add mild vinegar"),
"2c1a5fd92b9e3c762242": ("while the liquor remains warm", "WARM_STATE", ".39", "before the liquor cools", "while the leaf is still warm"),
"1b1ffdd869fb1429ad03": ("boil gently and remove from the fire", "BOIL_CLOSURE", ".39", "warm without boiling over", "simmer until reduced"),
"308e8ea2d5d190c498e8": ("mix the two portions together", "COMBINE_PORTIONS", ".54", "combine equal portions", "mix the wine and plant liquor"),
"204b04837409088c48f9": ("keep it in a covered jar", "COVERED_STORAGE", ".38", "set it aside in a stoppered vessel", "store it away from the sun"),
"6afeb5c9ab9f6cbdea0d": ("use the finished liquor fresh", "FRESH_USE_CLOSURE", ".36", "drink the dose the same day", "wash with it before it spoils"),
"b9d7b6d68209a9019e7a": ("gather the plant in spring", "GATHERING_TIME", ".35", "gather it in damp weather", "cut it before midsummer"),
"2cc054357a929df85f64": ("then take the following ingredient or plant part", "NEXT_DOSSIER_DETAIL", ".65", "next use the named organ", "thereafter add the following material"),
"0ec6a45e2950e8e7061d": ("the thin lower root", "PLANT_PART_ROOT", ".35", "the lower rosette", "the root fibres"),
"893c570f3fa3fce99711": ("steep it in white wine", "MEDIUM_WINE", ".36", "wash it in spring water", "macerate it in vinegar"),
"dd0ecaf5e27d81befffc": ("upon the afflicted place", "BODY_SITE_REFERENCE", ".38", "upon the swollen place", "upon the painful joint"),
"c10aec6d4dd877ec8bd8": ("which grows on damp shaded heath", "HABITAT_MOIST", ".36", "which grows beside running water", "which grows in shaded marsh ground"),
"95987d6f198d6d247511": ("leave the plaster uncovered until dry", "PLASTER_CLOSURE", ".35", "leave the dressing open to the air", "remove it after the place dries"),
"ad3581d3144f69a5912d": ("its small seed or bud-head", "PLANT_PART_SEED", ".32", "its upper flower head", "its dark seed head"),
"b74e9e65637b7c8538dd": ("the dried narrow leaf", "PLANT_PART_LEAF", ".35", "the dried flowering head", "the dried stem tip"),
"1322bc176443fc2a8a86": ("dry it in shade", "SHADE_DRYING", ".39", "hang it where no sun reaches", "dry it slowly in moving air"),
"087a47b5423438cd6b6a": ("drink it for pain of the stomach", "INDICATION_INTERNAL", ".36", "drink it against griping", "take it for a cold stomach"),
"75a523fcf039b006f97b": ("keep the remainder dry in shade", "DRY_STORAGE", ".35", "powder the dry remainder", "hang the remaining herb in shade"),
"c71c72da4e09e0833392": ("mix it with honey", "MEDIUM_HONEY", ".38", "mix it with thick syrup", "mix it with clarified butter"),
"61a075bc54793c1c781f": ("use it while freshly mixed", "FRESH_USE_CLOSURE", ".37", "lick it before it dries", "apply the honeyed paste fresh"),
"faf321940aed922846a9": ("for the final preparation take", "FINAL_USE_HEAD", ".32", "for the following dose use", "for a mild preparation take"),
"9bb7122b386ebbc6138f": ("the pale opened flower", "PLANT_PART_FLOWER", ".34", "the pale seed head", "the light-coloured root tip"),
}


VISIBLE = [
    ("f10r", "one tall branching simple; paired broad serrated or banded leaves; two unlike flower-head forms; horizontal basal structure ending in two red swollen bodies", "[pictured broad-leaved meadow simple]; [root]; [leaf]; [flower]", "scabious/knapweed article tradition", "broad serrate meadow or waterside simple with paired swollen basal organs"),
    ("f11r", "dense rounded flowering crown on several stems; divided or jagged basal leaves; broad flattened root-like base", "[pictured umbellifer-like simple]; [root]; [flowering crown]", "wild-carrot or related umbellifer article tradition", "dense-crowned divided-leaf simple of shaded ground"),
    ("f55v", "one huge upward broad leaf; terminal dotted flower or fruit cluster; branched composite root; prose split around the already drawn plant", "[pictured broad leaf]; [root]; [flower/fruit head]", "greater-plantain/broad-leaf wound-herb tradition", "large broad-leaved roadside medicinal simple"),
    ("f56r", "tall highly stylized plant; narrow or prickly organs; two dark heads; one very large radial spiral-centred head", "[pictured spiny wet-ground simple]; [lower root]; [narrow leaf]; [head]", "ros-solis/sundew article tradition, with thistle/teasel contamination possible", "spiny or glandular heath/wet-ground simple with conspicuous radial heads"),
]


ARTICLE = {
"f10r": """# f10r — broad meadow simple / scabious-knapweed family\n\n**Working identification.** A scabious or knapweed article tradition; fallback: a broad serrate meadow or waterside simple with paired swollen basal organs.\n\n> Take the fibrous lower root and wash it in running water. From the same prepared batch, pound it until the mass is even and reduce it to coarse powder. Add red wine and drink it for pain of the stomach, applying the usual measure; keep the remaining root dry. Use the freshly prepared remedy while warm, with the foregoing preparation, when it is ready.\n>\n> The plant grows in damp meadow ground. When the preparation is ready, take the prepared decoction, add the expressed juice and boil gently. Use this portion and the next in the stated measure. The plant is gathered before flowering: take one handful for the decoction, with the foregoing preparation and from the foregoing batch, again in the usual measure and from the same prepared batch. When its flower has opened, combine one portion of decoction with another; continue until a bitter taste remains, then preserve that portion under oil.\n\nThe first statement continues across `.2` to `.5`; the second continues across `.6`, `.8`, and `.9`.""",
"f11r": """# f11r — wild-carrot/umbellifer-like simple\n\n**Working identification.** Wild carrot or a related umbellifer article tradition; fallback: a dense-crowned, divided-leaf simple of shaded ground.\n\n> Gather the root in spring from shaded woodland, before the flowering crown opens. Press the bruised root through cloth, strain the liquor a second time, and continue until it runs clear; leave the strained liquor uncovered to cool, reserving the flowering crown. Of this pictured simple, bind the present portion upon a swollen place and use the usual measure. Make a warm poultice from its leaves; lay it on while warm when the preparation is ready, using the present portion.\n\nAll three physical lines are one compact article. The two cloth cards are read as first pressing and finer second filtration, not accidental synonyms.""",
"f55v": """# f55v — broad-leaf wound herb / greater-plantain family\n\n**Working identification.** Greater plantain or a cognate broad-leaf wound-herb article; fallback: a large broad-leaved roadside medicinal simple.\n\n> Take the next measured portion of the broad leaf in the usual measure. Boil it gently in white wine and steep it until the liquor is clear. Add another usual measure, stir until evenly mixed, and wash the sore place once. For its second medicinal use, add white wine; while the liquor remains warm, boil gently and remove it from the fire. In the usual measure mix the two portions together, keep them in a covered jar, and use the prepared decoction—this present portion—fresh.\n\nThe illustration interrupts the writing surface, but not the two preparation clauses. The page's Currier-B texture suits its unusually explicit recipe sequence.""",
"f56r": """# f56r — ros-solis/sundew or spiny wet-heath simple\n\n**Working identification.** A *ros solis* / sundew article tradition, perhaps contaminated by thistle or teasel imagery; fallback: a spiny or glandular heath/wet-ground simple with conspicuous radial heads.\n\n> Gather the plant in spring; then take the thin lower root in the stated measure. Next steep the following part in white wine, gathered before flowering, and apply this portion upon the afflicted place. Of this pictured simple, which grows on damp shaded heath, apply the portion and leave the plaster uncovered until dry. Its small seed or bud-head is the next part: take the dried narrow leaf and dry it in shade. Use the freshly prepared remedy for pain of the stomach and keep the remainder dry in shade. Next use the freshly prepared part mixed with honey, while freshly mixed. For the final preparation take the pale opened flower in the stated measure.\n\nThe seven physical lines form one dossier with repeated `CHO/SHO` continuations. They do not become seven sentences merely because the pre-drawn plant forced short lines.""",
}


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def broad_class(role: str) -> str:
    """Collapse detailed roles to the deliberately small Herbal source deck."""
    if role.startswith("PLANT_PART") or role == "FLOWERING_PART": return "PLANT_PART"
    if "HABITAT" in role: return "HABITAT"
    if "GATHERING" in role: return "GATHERING_TIME"
    if role.startswith("MEDIUM_"): return "MEDIUM"
    if "MEASURE" in role: return "MEASURE"
    if "INDICATION" in role: return "INDICATION"
    if "APPLICATION" in role or role in {"POULTICE_PREPARATION", "PLASTER_CLOSURE", "BODY_SITE_REFERENCE"}: return "APPLICATION"
    if "STORAGE" in role: return "STORAGE"
    if "REFERENCE" in role or role in {"CURRENT_PORTION", "PREPARED_LIQUID", "PICTURED_OWNER_REFERENCE"}: return "REFERENCE"
    if "GATE" in role or "STATE" in role or "CONDITION" in role: return "PROCESS_CONDITION"
    if "HEAD" in role: return "CLAUSE_HEAD"
    if "CLOSURE" in role: return "CLAUSE_CLOSURE"
    return "PREPARATION_ACTION"


def main() -> None:
    with SOURCE.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["page"] in PAGES]
    assert len(rows) == 100
    counts = Counter(r["exact_tuple_id"] for r in rows)
    assert len(counts) == 66 and sum(n == 1 for n in counts.values()) == 55
    assert set(counts) == set(M), (set(counts) - set(M), set(M) - set(counts))

    # The image freeze is serialized independently of textual assignments.
    vf = []
    for page, desc, silent, family, fallback in VISIBLE:
        vf.append({"page": page, "frozen_visible_features": desc,
                   "permitted_silent_arguments": silent,
                   "specific_source_family_guess": family,
                   "broad_fallback": fallback,
                   "freeze_order": "BEFORE_TEXT_ASSIGNMENT"})
    write_tsv(HERE / "V19_R2_VISIBLE_PLANT_FREEZE.tsv", list(vf[0]), vf)

    pages = defaultdict(set)
    surfaces = defaultdict(set)
    for r in rows:
        pages[r["exact_tuple_id"]].add(r["page"]); surfaces[r["exact_tuple_id"]].add(r["surface"])

    dr = []
    for tid in sorted(counts):
        gloss, cls, conf, a1, a2 = M[tid]
        dr.append({"exact_tuple_id": tid, "surface_realizations": "|".join(sorted(surfaces[tid])),
                   "occurrences": str(counts[tid]), "folios": "|".join(sorted(pages[tid])),
                   "concrete_default_phrase": gloss, "source_class": broad_class(cls), "detailed_role": cls, "confidence": conf,
                   "assignment_basis": "cross-page exact-card consistency + V18 deck + complete-article order" if counts[tid] > 1 else "complete-article order + visible owner + medieval materia-medica inventory",
                   "recurrent_or_singleton": "RECURRENT" if counts[tid] > 1 else "SINGLETON"})
    write_tsv(HERE / "V19_R2_HERBAL_CARD_DICTIONARY.tsv", list(dr[0]), dr)

    ir = []
    by_locus = defaultdict(list)
    for r in rows:
        by_locus[r["locus"]].append(M[r["exact_tuple_id"]][0])
    action_words = ("take", "wash", "pound", "reduce", "add", "drink", "apply", "keep", "use", "boil", "gather", "press", "strain", "leave", "reserve", "bind", "lay", "steep", "stir", "mix", "dry")
    for r in rows:
        gloss, cls, conf, _, _ = M[r["exact_tuple_id"]]
        rr = dict(r)
        rr["default_English"] = gloss; rr["source_class"] = broad_class(cls); rr["detailed_role"] = cls; rr["confidence"] = conf
        rr["inheritance_context_rule"] = "R2 V19 exact-card default; no spelling decomposition."
        rr["inserted_silent_argument"] = "[pictured simple / currently named part]" if gloss.startswith(action_words) else ""
        rr["complete_local_phrase"] = "; ".join(by_locus[r["locus"]])
        ir.append(rr)
    fields = list(rows[0]); fields.insert(fields.index("confidence"), "detailed_role"); fields += ["inserted_silent_argument", "complete_local_phrase"]
    write_tsv(HERE / "V19_R2_100_EVENT_INTERLINEAR.tsv", fields, ir)

    ar = []
    for tid in sorted(k for k, n in counts.items() if n == 1):
        gloss, cls, conf, a1, a2 = M[tid]
        r = next(x for x in rows if x["exact_tuple_id"] == tid)
        ar.append({"exact_tuple_id": tid, "surface": r["surface"], "page": r["page"], "locus": r["locus"],
                   "selected_default": gloss, "concrete_rival_1": a1, "concrete_rival_2": a2,
                   "selection_reason": "selected phrase yields the least-repaired complete article while remaining an ordinary 1420 materia-medica slot",
                   "confidence": conf})
    write_tsv(HERE / "V19_R2_SINGLETON_ALTERNATIVES.tsv", list(ar[0]), ar)

    (HERE / "V19_R2_COMPLETE_HERBAL_ARTICLES.md").write_text(
        "# V19 R2 complete Herbal articles\n\n" + "\n\n".join(ARTICLE[p] for p in PAGES) +
        "\n\n## Reading convention\n\nInserted subjects and objects are supplied by the pictured page owner or the last explicitly named part. Every visible event nevertheless has its own concrete default in the interlinear. Physical-line ends do not force sentence ends.\n",
        encoding="utf-8")

    semantic_classes = len({broad_class(v[1]) for v in M.values()})
    inserted = sum(bool(r["inserted_silent_argument"]) for r in ir)
    banned = ("unknown", "opaque", "payload", "untranslated", "local-name-")
    bad = [g for g, *_ in M.values() if any(x in g.lower() for x in banned)]
    assert not bad
    validation = {
        "status": "PASS_COMPLETE_R2_HERBAL_RECONSTRUCTION",
        "events": len(rows), "exact_card_types": len(counts),
        "singleton_types": sum(n == 1 for n in counts.values()),
        "recurrent_types": sum(n > 1 for n in counts.values()),
        "broad_source_classes": semantic_classes,
        "events_with_marked_silent_argument": inserted,
        "pages": list(PAGES), "complete_article_count": len(ARTICLE),
        "singleton_rival_rows": len(ar), "neutral_placeholder_count": len(bad),
        "sealed": ["f84", "f84r"],
    }
    (HERE / "V19_R2_VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(f"PASS events=100 types=66 singletons=55 classes={semantic_classes} inserted_silent={inserted}")


if __name__ == "__main__":
    main()
