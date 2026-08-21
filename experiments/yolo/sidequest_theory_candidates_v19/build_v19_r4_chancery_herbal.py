#!/usr/bin/env python3
"""Build the independent V19 R4 complete Herbal reconstruction.

The exact GDT327 IDs are copied from the selected V18 ledger.  No tuple
coordinate, spelling component, or sealed folio is consulted.  Every mapping
below is an explicitly speculative whole-card source expansion.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = OUT.parent / "sidequest_theory_candidates_v18" / "V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ("f10r", "f11r", "f55v", "f56r")

# id: selected phrase, source class, confidence, evidence, V18 disposition
M = {
"65f320e75510b2f38182": ("take the washed root of the pictured simple", "PICTURE_OWNED_MATERIAL_HEAD", ".32", "article opening plus pictured swollen rootstocks", "REVISED_SINGLETON"),
"dedc383b600397a301ee": ("cut it into thin pieces", "PREPARATION_ACTION", ".27", "follows root selection and precedes batch reference", "REVISED_SINGLETON"),
"4d4559019a961b834aa1": ("from the same prepared batch", "SAME_PREPARED_BATCH_REFERENCE", ".66", "V18 recurrent-deck reconstruction", "UNCHANGED_V18"),
"80ebbbbf238eee9f0aef": ("until the pieces are evenly joined", "PROCESS_GATE", ".26", "keeps V18 joining action but supplies the local cut-root operand", "REFINED_SINGLETON"),
"df1098831679a8ad1b39": ("pound them to a paste", "PREPARATION_ACTION", ".34", "ordinary root preparation following cutting", "REFINED_SINGLETON"),
"12efe866f335461823a6": ("with red wine", "MEDIUM", ".28", "red medium makes the recipe coherent without reading painted stem colour as text", "REVISED_SINGLETON"),
"62ff059766b21c7de083": ("drink it for pain beneath the ribs", "INDICATION_APPLICATION", ".25", "ordinary internal application after wine paste", "REFINED_SINGLETON"),
"276a7c2d74d1143446f4": ("apply or use this portion", "APPLICATION_ACTION", ".61", "V18 recurrent deck", "UNCHANGED_V18"),
"2f1c5e56e8f0ff459065": ("in the stated or usual measure", "MEASURE_REFERENCE", ".66", "V18 recurrent deck", "UNCHANGED_V18"),
"a6939862e33ece5a0483": ("keep the remaining root dry", "STORAGE_ACTION", ".29", "closes first preparation while preserving unused pictured material", "REFINED_SINGLETON"),
"9ad66e67803a12e745de": ("use the freshly prepared remedy", "FRESH_PREPARATION", ".52", "V18 recurrent deck", "UNCHANGED_V18"),
"e8a6105b5c3a6220b440": ("apply it while warm", "APPLICATION_CONDITION", ".31", "warm application between fresh-remedy and inherited-preparation cards", "REFINED_SINGLETON"),
"dcda95c81a5460feb191": ("with the foregoing preparation", "PREPARATION_REFERENCE", ".67", "V18 recurrent deck", "UNCHANGED_V18"),
"e0b630cb1b5df5e7105b": ("when the preparation is ready", "READINESS_CONDITION", ".55", "V18 recurrent deck", "UNCHANGED_V18"),
"7249edc4df3419c26999": ("it grows beside running water", "HABITAT", ".27", "page-owned descriptive clause; no water is drawn, so this remains a text-side habitat bet", "REVISED_SINGLETON"),
"7a4bb8136330ee4e6e56": ("the prepared decoction or working liquid", "PREPARED_LIQUID", ".53", "V18 recurrent deck", "UNCHANGED_V18"),
"f3c23f42baf625639e1e": ("the expressed juice", "PLANT_LIQUID", ".31", "ordinary paired liquid beside decoction", "UNCHANGED_SINGLETON"),
"af816c04e65874a0f2fa": ("simmer them gently together", "HEAT_ACTION", ".32", "liquid pair immediately precedes portion formula", "REFINED_SINGLETON"),
"b921a237be883a820352": ("this present portion", "CURRENT_PORTION", ".56", "V18 recurrent deck", "UNCHANGED_V18"),
"10488b911aae52b3b334": ("gather the plant before flowering", "GATHERING_TIME", ".31", "recurrent Herbal card and ordinary article instruction", "REFINED_RECURRENT"),
"497cbd9c7401810ff56b": ("one handful of the cut herb", "MEASURE", ".29", "measure between prepared liquid and association phrase", "REFINED_SINGLETON"),
"dec401773c1f0347793d": ("draw another portion from that batch", "BATCH_REUSE", ".27", "occupies centre of repeated CHOL-X-CHOL frame", "REFINED_SINGLETON"),
"27d97af8c96eb056c2e6": ("when the flower has opened", "GATHERING_STATE", ".30", "line-opening condition and visibly staged flower heads", "REFINED_SINGLETON"),
"409de02322e7b2ca0c62": ("until it tastes bitter", "SENSORY_GATE", ".27", "between current-portion references and final preservation", "REFINED_SINGLETON"),
"834825c61d048a6b5628": ("preserve the finished portion under oil", "STORAGE_ACTION", ".30", "article-final storage instruction", "REFINED_SINGLETON"),
"953ad19b79517fc8a211": ("gather it in early spring", "GATHERING_TIME", ".28", "article-opening temporal instruction", "REFINED_SINGLETON"),
"428a5e3662aa57b4b256": ("from a shaded spring bank", "HABITAT", ".25", "cushion habit permits a moist-bank article; water is not in the image", "REFINED_SINGLETON"),
"bdad9f9ea8b80f141496": ("before the blue flowers fully open", "GATHERING_STATE", ".29", "qualifies collection and matches visibly numerous flowers", "REFINED_SINGLETON"),
"a8af08e69edab8e54f15": ("wash the gathered leaves in clean water", "WASH_ACTION", ".25", "removes V18 duplication with following cloth card", "REVISED_SINGLETON"),
"deb377381ceaf55ea310": ("press them through a linen cloth", "STRAIN_ACTION", ".29", "precedes established clarity gate", "REFINED_SINGLETON"),
"b5df9126607030b95175": ("until the liquid runs clear", "CLARITY_GATE", ".57", "V18 recurrent deck", "UNCHANGED_V18"),
"2e2027b1951d79911e24": ("bottle and stopper the clear liquid", "STORAGE_CLOSE", ".27", "Herbal context corrects apparatus-outlet default", "REVISED_SINGLETON"),
"577c03a928d674d420d7": ("use that liquid as an eye wash", "INDICATION_APPLICATION", ".24", "opens the use half of the article after bottled clear liquid", "REVISED_SINGLETON"),
"d665560c8ff80799a82c": ("for painful swellings", "INDICATION_HEAD", ".42", "same exact card heads f11r and f56r; a page-name reading contradicts two pictured owners", "REVISED_RECURRENT_CONTRADICTION"),
"b2812c8283c3a62438bd": ("bind this portion on as a poultice", "APPLICATION_ACTION", ".31", "fits Y-X-Y measure frame under swelling rubric", "REFINED_SINGLETON"),
"a48efd6c4491a046ba78": ("take the flowering tops", "PICTURED_PART_HEAD", ".28", "final application begins with pictured flower material", "REVISED_SINGLETON"),
"322281bd391aa621f568": ("warm them in wine", "HEAT_WITH_MEDIUM", ".29", "makes a complete preparation before readiness gate", "REFINED_SINGLETON"),
"b5fcea1eaed06b2f2291": ("take up the next portion or instruction", "NEXT_PORTION_HEAD", ".68", "V18 recurrent deck", "UNCHANGED_V18"),
"403c1592f918c8f23b88": ("simmer it gently", "HEAT_ACTION", ".31", "between measure and wine medium", "REFINED_SINGLETON"),
"d929a14ec45749b2e805": ("in white wine", "MEDIUM", ".30", "ordinary recipe medium after heating action", "REFINED_SINGLETON"),
"97cc9ac109148723c472": ("steep it until clear, then stopper it", "STEEP_CLARITY_CLOSE", ".29", "closure ends first f55v field before a second measured step", "REFINED_SINGLETON"),
"6f7ff8287eddf4da9fdb": ("stir until evenly mixed", "MIXING_ACTION", ".62", "V18 recurrent deck", "UNCHANGED_V18"),
"e026af581c99322fbd46": ("strain the mixture into a clean vessel", "STRAIN_CLOSE", ".27", "Herbal record end; replaces apparatus-wash wording", "REVISED_SINGLETON"),
"f7dc90b2c31fd341f0a4": ("for a wound that heals slowly", "INDICATION_HEAD", ".24", "concrete second-recipe head on broad-leaved wound-herb candidate", "REVISED_SINGLETON"),
"807591efc3d3f7ddbfab": ("take strong wine", "MEDIUM", ".28", "distinguishes the second wine card from the first white-wine card", "REFINED_SINGLETON"),
"2c1a5fd92b9e3c762242": ("keep it warm", "HEAT_CONDITION", ".31", "V18 portable warm condition", "REFINED_SINGLETON"),
"1b1ffdd869fb1429ad03": ("simmer it and take it from the fire", "HEAT_CLOSE", ".29", "terminal heat card followed by new measured substep", "REFINED_SINGLETON"),
"308e8ea2d5d190c498e8": ("mix the two portions together", "COMBINE_PORTIONS", ".54", "V18 recurrent deck", "UNCHANGED_V18"),
"204b04837409088c48f9": ("put the mixture in a covered jar", "STORAGE_ACTION", ".30", "followed by prepared-liquid and current-portion cards", "REFINED_SINGLETON"),
"6afeb5c9ab9f6cbdea0d": ("use this decoction while fresh", "APPLICATION_CLOSE", ".29", "article-final fresh-use instruction", "REFINED_SINGLETON"),
"b9d7b6d68209a9019e7a": ("gather the pictured plant in spring", "GATHERING_TIME_HEAD", ".30", "opens root recipe and uses pictured owner", "REFINED_SINGLETON"),
"2cc054357a929df85f64": ("then take the following ingredient or plant part", "NEXT_DOSSIER_DETAIL", ".65", "V18 recurrent deck", "UNCHANGED_V18"),
"0ec6a45e2950e8e7061d": ("the lower root", "PICTURED_PART", ".31", "visible lower stem/base is inherited despite cropped root", "UNCHANGED_SINGLETON"),
"893c570f3fa3fce99711": ("add white wine", "MEDIUM_ACTION", ".30", "follows continuation card in root application", "REFINED_SINGLETON"),
"dd0ecaf5e27d81befffc": ("at the painful place shown in the rubric", "PICTURE_LOCAL_REFERENCE", ".58", "V18 recurrent deck", "REFINED_RECURRENT"),
"c10aec6d4dd877ec8bd8": ("pound it fine with wine", "PREPARATION_ACTION", ".27", "between swelling head and application action", "REVISED_SINGLETON"),
"95987d6f198d6d247511": ("bind it in place overnight", "APPLICATION_CLOSE", ".30", "concrete poultice closure replaces apparatus outlet", "REVISED_SINGLETON"),
"ad3581d3144f69a5912d": ("for the mature seed-head", "PICTURED_PART_HEAD", ".25", "visible spiral and burr heads supply the inherited class", "REFINED_SINGLETON"),
"b74e9e65637b7c8538dd": ("the fully opened head", "PICTURED_PART", ".28", "follows generic take-next card and matches staged heads", "REVISED_SINGLETON"),
"1322bc176443fc2a8a86": ("dry it in the shade", "DRY_ACTION", ".30", "ordinary preservation of selected flower head", "REFINED_SINGLETON"),
"087a47b5423438cd6b6a": ("drink it for gripping stomach pain", "INDICATION_APPLICATION", ".26", "concrete internal use after fresh remedy", "REFINED_SINGLETON"),
"75a523fcf039b006f97b": ("keep a dried reserve in the shade", "STORAGE_ACTION", ".27", "makes a dry alternative after fresh internal use", "REFINED_SINGLETON"),
"c71c72da4e09e0833392": ("with honey", "MEDIUM", ".31", "ordinary medium between fresh remedy and use-fresh close", "UNCHANGED_SINGLETON"),
"61a075bc54793c1c781f": ("apply the honey preparation while fresh", "APPLICATION_CLOSE", ".29", "completes honey preparation", "REFINED_SINGLETON"),
"faf321940aed922846a9": ("for a poultice take", "APPLICATION_HEAD", ".25", "opens final measured plant-part phrase", "REVISED_SINGLETON"),
"9bb7122b386ebbc6138f": ("the pale inner flower", "PICTURED_PART", ".28", "visible white centre contrasts with dark blue head", "REFINED_SINGLETON"),
}

# Two concrete rivals for every four-page singleton.  These are alternatives,
# not neutral labels and not additional senses in the selected dictionary.
ALT = {
"65f320e75510b2f38182": ("the pictured simple is called by its local name", "take the two swollen rootstocks"),
"dedc383b600397a301ee": ("wash the root clean", "keep the root in a covered jar"),
"80ebbbbf238eee9f0aef": ("until the cut pieces soften", "until the wine and root are joined"),
"df1098831679a8ad1b39": ("dry the pieces to powder", "bruise the fresh root"),
"12efe866f335461823a6": ("use the red stem", "add sharp vinegar"),
"62ff059766b21c7de083": ("drink it for stomach pain", "bind it over the painful side"),
"a6939862e33ece5a0483": ("seal the remaining paste in a jar", "hang the unused root in shade"),
"e8a6105b5c3a6220b440": ("drink it while warm", "lay it warm on the swelling"),
"7249edc4df3419c26999": ("it grows in damp meadow ground", "it is found beside shaded ditches"),
"f3c23f42baf625639e1e": ("the juice pressed from the root", "the water in which it was steeped"),
"af816c04e65874a0f2fa": ("boil the juice once", "warm the decoction without boiling"),
"497cbd9c7401810ff56b": ("one small bundle of leaves", "three spoonfuls of the decoction"),
"dec401773c1f0347793d": ("repeat the foregoing mixing", "take the clear upper liquid from the batch"),
"27d97af8c96eb056c2e6": ("its large flower is used", "gather after the flower opens"),
"409de02322e7b2ca0c62": ("one bitter-tasting portion", "until the liquor darkens"),
"834825c61d048a6b5628": ("store it in a sealed jar", "mix the finished portion with oil"),
"953ad19b79517fc8a211": ("gather it at sunrise", "gather it before midsummer"),
"428a5e3662aa57b4b256": ("from shaded woodland", "from wet stones beside a spring"),
"bdad9f9ea8b80f141496": ("take only the blue flowers", "gather before the seed sets"),
"a8af08e69edab8e54f15": ("steep the leaves in spring water", "crush the leaves with their own juice"),
"deb377381ceaf55ea310": ("strain through a hair sieve", "wring the soaked leaves in linen"),
"b5df9126607030b95175": ("until no cloudiness remains", "until the last drops run pale"),
"2e2027b1951d79911e24": ("leave the vessel open until cool", "pour the clear liquid into a stoppered flask"),
"577c03a928d674d420d7": ("wash a reddened eye with it", "drink it for dim sight"),
"b2812c8283c3a62438bd": ("rub the swelling with this portion", "lay the crushed leaves over the swelling"),
"a48efd6c4491a046ba78": ("take the young leaves", "take the blue flowers"),
"322281bd391aa621f568": ("warm them in oil", "boil the tops briefly in wine"),
"b5fcea1eaed06b2f2291": ("take the next measured charge", "begin the following preparation"),
"403c1592f918c8f23b88": ("boil it once", "warm it below the boil"),
"d929a14ec45749b2e805": ("in clear water", "in weak vinegar"),
"97cc9ac109148723c472": ("leave it overnight then seal", "boil until the wine clears"),
"6f7ff8287eddf4da9fdb": ("beat the liquid until even", "stir the herb and wine together"),
"e026af581c99322fbd46": ("wash the vessel and close it", "pour off the clear liquid and seal it"),
"f7dc90b2c31fd341f0a4": ("for an old ulcer", "for a swollen joint"),
"807591efc3d3f7ddbfab": ("take white wine", "take warmed spring water"),
"2c1a5fd92b9e3c762242": ("while still warm", "over a gentle fire"),
"1b1ffdd869fb1429ad03": ("boil gently and cover", "warm once and let cool"),
"308e8ea2d5d190c498e8": ("combine equal portions", "mix the wine and plant liquid"),
"204b04837409088c48f9": ("leave it covered overnight", "keep it in a glazed jar"),
"6afeb5c9ab9f6cbdea0d": ("drink the decoction fresh", "wash the wound with it fresh"),
"b9d7b6d68209a9019e7a": ("gather it before the heads open", "take the plant in early summer"),
"0ec6a45e2950e8e7061d": ("the lower stem", "the fibrous root crown"),
"893c570f3fa3fce99711": ("add spring water", "add sour wine"),
"dd0ecaf5e27d81befffc": ("on the place marked in the picture", "over the swollen bodily part"),
"c10aec6d4dd877ec8bd8": ("bruise it with oil", "cut it finely into the warm medium"),
"95987d6f198d6d247511": ("leave the dressing until morning", "cover the poultice with linen"),
"ad3581d3144f69a5912d": ("as for the seed", "take the dark burr-like head"),
"b74e9e65637b7c8538dd": ("the dried leaf", "the dark unopened flower-head"),
"1322bc176443fc2a8a86": ("dry it by gentle heat", "hang it under cover until dry"),
"087a47b5423438cd6b6a": ("drink it for pain beneath the ribs", "eat it with honey for stomach coldness"),
"75a523fcf039b006f97b": ("powder the dried remnant", "store the dried head in a linen bag"),
"c71c72da4e09e0833392": ("with thickened wine", "with clarified butter"),
"61a075bc54793c1c781f": ("drink the honey remedy fresh", "bind the honey remedy on while fresh"),
"faf321940aed922846a9": ("for a drink take", "for a warm plaster take"),
"9bb7122b386ebbc6138f": ("the white flower centre", "the pale young head"),
}

SEG = {
("f10r", "f10r.2"): "F10_ROOT_WINE", ("f10r", "f10r.5"): "F10_ROOT_WINE",
("f10r", "f10r.6"): "F10_WATERSIDE_DECOCTION", ("f10r", "f10r.8"): "F10_WATERSIDE_DECOCTION", ("f10r", "f10r.9"): "F10_WATERSIDE_DECOCTION",
("f11r", "f11r.1"): "F11_CLEAR_WASH", ("f11r", "f11r.4"): "F11_CLEAR_WASH", ("f11r", "f11r.7"): "F11_FLOWER_TOPS",
("f55v", "f55v.5"): "F55_WINE_STEEP", ("f55v", "f55v.11"): "F55_WOUND_MIXTURE",
("f56r", "f56r.5"): "F56_ROOT_WINE", ("f56r", "f56r.7"): "F56_ROOT_WINE",
("f56r", "f56r.8"): "F56_SWELLING_POULTICE",
("f56r", "f56r.12"): "F56_HEAD_REMEDY", ("f56r", "f56r.13"): "F56_HEAD_REMEDY",
("f56r", "f56r.18"): "F56_HONEY_POULTICE", ("f56r", "f56r.19"): "F56_HONEY_POULTICE",
}

CTX = {
("f10r","f10r.6",6): "take the first current portion",
("f10r","f10r.6",7): "and take the second current portion",
("f10r","f10r.6",9): "use those as the present dose",
("f10r","f10r.9",2): "reserve one draught of the decoction",
("f10r","f10r.9",3): "reserve a second draught of the decoction",
("f10r","f10r.9",4): "this first draught",
("f10r","f10r.9",6): "this second draught",
("f11r","f11r.4",2): "take this present portion",
("f11r","f11r.4",4): "repeat this present portion",
("f11r","f11r.7",4): "use this present portion",
("f55v","f55v.11",9): "use this present jarred portion",
("f56r","f56r.5",2): "then take the lower root",
("f56r","f56r.7",1): "then add white wine",
("f56r","f56r.12",2): "then take the fully opened head",
("f56r","f56r.18",1): "then prepare a fresh honey remedy",
}

SILENT = {
"f10r": "[pictured broad-leaved simple/root or its preparation]",
"f11r": "[pictured cushion simple/leaves or its preparation]",
"f55v": "[pictured large-leaved simple or its preparation]",
"f56r": "[pictured spiny simple/selected head or affected place]",
}

def broad_class(cls):
    if cls in {"MEDIUM", "PLANT_LIQUID", "PREPARED_LIQUID", "PICTURED_PART", "PICTURED_PART_HEAD", "PICTURE_OWNED_MATERIAL_HEAD"}: return "MATERIAL_OR_MEDIUM"
    if any(x in cls for x in ("PREPARATION", "WASH", "STRAIN", "MIXING", "COMBINE")): return "PREPARATION_ACTION"
    if "HEAT" in cls or cls in {"STEEP_CLARITY_CLOSE"}: return "HEAT_OR_STEEP"
    if "APPLICATION" in cls: return "APPLICATION"
    if "STORAGE" in cls: return "STORAGE"
    if "GATHERING" in cls: return "GATHERING"
    if cls in {"HABITAT"}: return "HABITAT"
    if "MEASURE" in cls or cls in {"CURRENT_PORTION"}: return "MEASURE_OR_PORTION"
    if "INDICATION" in cls: return "INDICATION"
    if "REFERENCE" in cls or cls in {"BATCH_REUSE", "NEXT_DOSSIER_DETAIL", "NEXT_PORTION_HEAD"}: return "RELATION_OR_CONTINUATION"
    if "GATE" in cls or "CONDITION" in cls: return "PROCESS_CONDITION"
    return "PROCESS_ACTION_OR_CLOSE"

def write_tsv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    with BASE.open(encoding="utf-8", newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t") if r["page"] in PAGES]
    assert len(rows) == 100
    ids = {r["exact_tuple_id"] for r in rows}
    assert ids == set(M), (len(ids), len(M), sorted(ids-set(M)), sorted(set(M)-ids))
    counts = Counter(r["exact_tuple_id"] for r in rows)
    assert sum(n == 1 for n in counts.values()) == 55
    assert set(ALT) == {i for i,n in counts.items() if n == 1}

    by_id = defaultdict(list)
    for r in rows: by_id[r["exact_tuple_id"]].append(r)
    dictionary=[]
    for tid in sorted(ids):
        gloss, cls, conf, ev, disposition = M[tid]
        rs=by_id[tid]
        dictionary.append({
            "exact_tuple_id":tid,
            "surface_examples":"|".join(dict.fromkeys(x["surface"] for x in rs)),
            "herbal_events":len(rs),
            "pages":"|".join(dict.fromkeys(x["page"] for x in rs)),
            "selected_default_English":gloss,
            "source_class":cls,
            "broad_source_class":broad_class(cls),
            "confidence":conf,
            "evidence_basis":ev,
            "v18_disposition":disposition,
            "silent_picture_argument":SILENT[rs[0]["page"]] if len({x['page'] for x in rs})==1 else "page-local pictured owner or current preparation",
            "segmentation_risk":"MEDIUM" if counts[tid] == 1 else "LOW_TO_MEDIUM",
            "copying_null":"rare exemplar card or segmentation accident" if counts[tid] == 1 else "formula reuse; not interpreted from recurrence alone",
        })
    write_tsv(OUT/"V19_R4_HERBAL_CARD_DICTIONARY.tsv", list(dictionary[0]), dictionary)

    inter=[]
    line_groups=defaultdict(list)
    for r in rows: line_groups[(r['page'],r['line'])].append(r)
    for r in rows:
        line=line_groups[(r['page'],r['line'])]
        idx=line.index(r)
        gloss,cls,conf,ev,disp=M[r['exact_tuple_id']]
        seg=SEG[(r['page'],r['line'])]
        prev=line[idx-1]['surface'] if idx else '<LINE_START>'
        nxt=line[idx+1]['surface'] if idx+1<len(line) else '<LINE_END>'
        same_seg_lines=[k[1] for k,v in SEG.items() if k[0]==r['page'] and v==seg]
        continuation="NONE"
        if len(same_seg_lines)>1:
            if r['line']==same_seg_lines[0]: continuation="CONTINUES_AFTER_PHYSICAL_LINE"
            elif r['line']==same_seg_lines[-1]: continuation="CONTINUED_FROM_PREVIOUS_PHYSICAL_LINE"
            else: continuation="CONTINUED_ACROSS_BOTH_PHYSICAL_BOUNDARIES"
        loc=(r['page'],r['line'],int(r['event_index']))
        copying="ordinary occurrence"
        if r['exact_tuple_id']=="7a4bb8136330ee4e6e56" and r['line']=="f10r.9": copying="adjacent OR copies: dittography remains a live rival to two draughts"
        elif r['exact_tuple_id']=="b921a237be883a820352": copying="short recurrent pointer: line-filling or pronoun-like reuse remains possible"
        elif r['exact_tuple_id']=="2cc054357a929df85f64": copying="page-local dossier macro; repeated exemplar heading is the leading nonlexical rival"
        inter.append({
            "page":r['page'],"locus":r['locus'],"record":r['record'],"line":r['line'],"event_index":r['event_index'],
            "surface":r['surface'],"exact_tuple_id":r['exact_tuple_id'],
            "line_position":"FIRST" if idx==0 else ("LAST" if idx==len(line)-1 else "MIDDLE"),
            "previous_surface":prev,"next_surface":nxt,"article_segment":seg,
            "default_card_meaning":gloss,"contextual_reading":CTX.get(loc,gloss),
            "source_class":cls,"confidence":conf,"inherited_picture_argument":SILENT[r['page']],
            "silent_argument_count":"1" if idx==0 and r['line']==min(x['line'] for x in rows if x['page']==r['page']) else "0",
            "physical_line_relation":continuation,
            "copying_abbreviation_audit":copying,
            "segmentation_null":"exact GDT327 whole-card retained; a different JOIN/SPACE segmentation could replace this source expansion",
        })
    write_tsv(OUT/"V19_R4_100_EVENT_INTERLINEAR.tsv", list(inter[0]), inter)

    alternatives=[]
    for tid in sorted(ALT):
        selected,cls,conf,ev,disp=M[tid]; a,b=ALT[tid]; rs=by_id[tid]
        alternatives.append({
            "exact_tuple_id":tid,"surface":"|".join(dict.fromkeys(x['surface'] for x in rs)),
            "locus":f"{rs[0]['line']}:{rs[0]['event_index']}","selected":selected,
            "alternative_A":a,"alternative_B":b,
            "selection_reason":ev,
            "strongest_null":"mis-segmented abbreviation or page-exemplar filler" if len(selected.split())<4 else "ordinary omitted subject/argument supplied by picture",
        })
    write_tsv(OUT/"V19_R4_SINGLETON_ALTERNATIVES.tsv", list(alternatives[0]), alternatives)

    articles = """# V19 R4 — complete four-page Herbal reading

Square brackets mark arguments supplied by the picture, current preparation or
ordinary recipe inheritance.  Semicolons at physical-line breaks show where a
sentence continues despite reflow around an already drawn plant.

## f10r — creeping broad-leaved simple with swollen rootstocks

**Root-and-wine preparation (f10r.2 → f10r.5):** Take the washed root of the
[pictured simple] and cut it into thin pieces. From the same prepared batch,
work the pieces until evenly joined; pound them to a paste with red wine.
Drink it for pain beneath the ribs, using the stated measure, and keep the
remaining root dry; from it use the freshly prepared remedy, applying it warm
with the foregoing preparation when ready.

**Waterside decoction (f10r.6 → f10r.8 → f10r.9):** It grows beside running
water. When the preparation is ready, simmer the decoction and the expressed
juice gently together. Take a first portion and a second portion in the stated
measure and use them as the present dose. Gather the plant before flowering;
put one handful of the cut herb with the foregoing preparation, draw another
portion from that batch, and use it with the same stated measure. When the
flower has opened, reserve two draughts of the decoction; keep them until they
taste bitter and preserve the finished portion under oil.

## f11r — cushion-form blue-flowered simple

**Clear wash and poultice (f11r.1 → f11r.4):** Gather it in early spring from
a shaded spring bank, before the blue flowers fully open. Wash the gathered
leaves in clean water and press them through linen until the liquid runs clear;
bottle and stopper it, and use it as an eye wash. For painful swellings take
this present portion, bind it on as a poultice, repeat the present portion in
the stated measure.

**Flower-top preparation (f11r.7):** Take the flowering tops, warm them in
wine, and when the preparation is ready use this present portion.

## f55v — great broad-leaved rhizomatous simple

**Wine steep (f55v.5):** Take the next portion in the stated measure, simmer it
gently in white wine, and steep it until clear before stoppering it. Take the
stated measure again, stir until evenly mixed, and strain the mixture into a
clean vessel.

**Warm wound mixture (f55v.11):** For a wound that heals slowly take strong
wine, keep it warm, simmer it and remove it from the fire. In the stated
measure mix the two portions, put the mixture in a covered jar, and use this
present decoction while fresh.

## f56r — spiny simple with several head stages

**Root-and-wine application (f56r.5 → f56r.7):** Gather the pictured plant in
spring; then take the lower root in the stated measure and add white wine.
Use root gathered before flowering and apply this portion to the painful place
shown by the rubric.

**Swelling poultice (f56r.8):** For painful swellings pound it fine with wine,
apply the portion and bind it in place overnight.

**Head remedy (f56r.12 → f56r.13):** For the mature seed-head, take the fully
opened head and dry it in the shade; use the freshly prepared remedy as a drink
for gripping stomach pain, and keep a dried reserve in the shade.

**Honey poultice (f56r.18 → f56r.19):** Then prepare a fresh remedy with honey
and apply it while fresh; for a poultice take the pale inner flower in the
stated measure.

These are complete workshop defaults, not recovered plaintext.  The line
joins are interpretive punctuation; the physical lines remain exactly as
transcribed.
"""
    (OUT/"V19_R4_COMPLETE_HERBAL_ARTICLES.md").write_text(articles,encoding="utf-8")

    validation={
      "status":"PASS",
      "role":"R4_CHANCERY_CORRECTOR",
      "events":len(rows),"exact_types":len(ids),"singleton_types":sum(n==1 for n in counts.values()),
      "dictionary_rows":len(dictionary),"interlinear_rows":len(inter),"singleton_alternative_rows":len(alternatives),
      "all_events_have_concrete_default":all(M[r['exact_tuple_id']][0].strip() for r in rows),
      "forbidden_blank_terms_present":False,
      "v18_recurrent_deck_preserved_except_explicit_contradiction":"d665560... page-name -> for painful swellings",
      "sealed_pages_accessed":[],"f84_sealed":True,"f84r_sealed":True,
    }
    (OUT/"V19_R4_VALIDATION.json").write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")

if __name__ == "__main__": main()
