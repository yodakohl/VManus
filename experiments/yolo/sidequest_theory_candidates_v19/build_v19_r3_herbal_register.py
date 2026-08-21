#!/usr/bin/env python3
"""Build the independent V19 R3 technical-register Herbal reconstruction."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "sidequest_theory_candidates_v18" / "V18_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = ("f10r", "f11r", "f55v", "f56r")

# Exact cards remain opaque.  These phrases are a concrete source-register
# expansion selected from whole-article context, never from spelling parts.
M = {
"65f320e75510b2f38182":("the pictured twin-tubered blue-flowered simple","ARTICLE_HEAD",.34,"picture+article opening"),
"dedc383b600397a301ee":("keep the cut root in a covered jar","PRESERVATION",.46,"whole f10r preparation"),
"4d4559019a961b834aa1":("from the same prepared batch","REFERENCE",.66,"V18 recurrent deck"),
"80ebbbbf238eee9f0aef":("pound and stir until evenly joined","PREPARATION",.43,"f10r operation chain"),
"df1098831679a8ad1b39":("reduce the dried root to powder","PREPARATION",.47,"f10r operation chain"),
"12efe866f335461823a6":("use the reddish swollen root","PLANT_PART",.49,"visible paired red swellings"),
"62ff059766b21c7de083":("drink it for pain of the stomach","INDICATION_APPLICATION",.41,"article syntax+V18"),
"276a7c2d74d1143446f4":("apply or use this portion","APPLICATION",.61,"V17/V18 recurrent deck"),
"2f1c5e56e8f0ff459065":("in the stated or usual measure","MEASURE_REFERENCE",.65,"V16-V18 recurrent deck"),
"a6939862e33ece5a0483":("retain the remainder of the root","PRESERVATION",.38,"f10r article closure"),
"9ad66e67803a12e745de":("use the freshly prepared remedy","APPLICATION",.59,"V17/V18 recurrent deck"),
"e8a6105b5c3a6220b440":("apply it while warm","APPLICATION_CONDITION",.51,"f10r short use clause"),
"dcda95c81a5460feb191":("with the foregoing preparation","REFERENCE_RELATION",.59,"V16-V18 recurrent deck"),
"e0b630cb1b5df5e7105b":("when the preparation is ready","READINESS_GATE",.60,"V16-V18 recurrent deck"),
"7249edc4df3419c26999":("it grows beside running water","HABITAT",.39,"f10r article transition; water allowed"),
"7a4bb8136330ee4e6e56":("the prepared decoction or working liquid","PREPARATION_ENTITY",.62,"V17/V18 recurrent deck"),
"f3c23f42baf625639e1e":("express the juice from the root","PREPARATION",.48,"f10r liquid chain"),
"af816c04e65874a0f2fa":("boil it gently","PREPARATION",.52,"f10r liquid chain"),
"b921a237be883a820352":("this present portion","PORTION_POINTER",.65,"V16-V18 recurrent deck"),
"10488b911aae52b3b334":("gather it before flowering","GATHERING_TIME",.58,"V17/V18 recurrent deck"),
"497cbd9c7401810ff56b":("one handful","MEASURE",.52,"f10r measured liquid recipe"),
"dec401773c1f0347793d":("drawn from the foregoing batch","REFERENCE",.46,"f10r same-batch chain"),
"27d97af8c96eb056c2e6":("when the blue flower first opens","GATHERING_TIME",.42,"visible flower+article clause"),
"409de02322e7b2ca0c62":("it has a bitter taste","QUALITY",.45,"f10r quality clause"),
"834825c61d048a6b5628":("preserve this portion in oil","PRESERVATION",.49,"f10r article closure"),
"953ad19b79517fc8a211":("gather the mat-forming simple in spring","GATHERING_TIME",.40,"visible f11r plant+opening"),
"428a5e3662aa57b4b256":("where it grows in shaded woodland","HABITAT",.42,"f11r compact mat habit"),
"bdad9f9ea8b80f141496":("cut it before the blue flowers open","GATHERING_TIME",.46,"f11r visible flowers"),
"a8af08e69edab8e54f15":("strain the infusion first through coarse cloth","PREPARATION",.43,"ordered double-straining chain"),
"deb377381ceaf55ea310":("strain it again through fine cloth","PREPARATION",.43,"ordered double-straining chain"),
"b5df9126607030b95175":("continue until the liquid runs clear","STATE_GATE",.50,"f11r ordered filtering chain"),
"2e2027b1951d79911e24":("draw the clear liquid into a clean jar; close","PRESERVATION_CLOSE",.45,"f11r filter-chain closure"),
"577c03a928d674d420d7":("the genuine plant bears small blue flowers","IDENTIFICATION_FEATURE",.37,"visible f11r flowers after closed recipe"),
"d665560c8ff80799a82c":("of the pictured simple itself","PICTURE_REFERENCE",.52,"same exact card on two different plant pages"),
"b2812c8283c3a62438bd":("use it against a swollen place","INDICATION_APPLICATION",.44,"f11r measured-use clause"),
"a48efd6c4491a046ba78":("take the fresh leafy part","PLANT_PART",.38,"f11r second short formula"),
"322281bd391aa621f568":("lay it on while warm","APPLICATION_CONDITION",.48,"f11r short formula"),
"b5fcea1eaed06b2f2291":("take up the next portion or instruction","RECORD_ENTRY",.63,"V16-V18 recurrent deck"),
"403c1592f918c8f23b88":("boil the cut leaf gently","PREPARATION",.49,"f55v preparation record"),
"d929a14ec45749b2e805":("in white wine","MEDIUM",.50,"f55v preparation record"),
"97cc9ac109148723c472":("steep until clear; close the first preparation","STATE_GATE_CLOSE",.48,"f55v first subrecord"),
"6f7ff8287eddf4da9fdb":("stir until evenly mixed","PREPARATION",.56,"V17/V18 recurrent deck"),
"e026af581c99322fbd46":("wash the broad leaf once; close","PREPARATION_CLOSE",.39,"f55v visible broad leaf+subrecord"),
"f7dc90b2c31fd341f0a4":("for its medicinal use","APPLICATION_ENTRY",.43,"f55v second record opening"),
"807591efc3d3f7ddbfab":("add white wine","MEDIUM",.49,"f55v second preparation"),
"2c1a5fd92b9e3c762242":("while the mixture is still warm","APPLICATION_CONDITION",.52,"f55v operation order"),
"1b1ffdd869fb1429ad03":("boil gently; close the heating step","PREPARATION_CLOSE",.50,"f55v operation order"),
"308e8ea2d5d190c498e8":("mix the two measured portions together","PREPARATION",.58,"V17/V18 recurrent deck"),
"204b04837409088c48f9":("keep it in a covered jar","PRESERVATION",.53,"f55v preparation closure"),
"6afeb5c9ab9f6cbdea0d":("use that portion while fresh","APPLICATION",.49,"f55v article closure"),
"b9d7b6d68209a9019e7a":("gather the thistle-like simple in spring","GATHERING_TIME",.42,"visible f56r+article opening"),
"2cc054357a929df85f64":("then take the following ingredient or plant part","SEQUENCE_HEAD",.66,"V18 recurrent deck"),
"0ec6a45e2950e8e7061d":("the lower root","PLANT_PART",.54,"visible f56r lower stem/root"),
"893c570f3fa3fce99711":("white wine","MEDIUM",.51,"f56r preparation clause"),
"dd0ecaf5e27d81befffc":("on the afflicted place","APPLICATION_TARGET",.44,"f56r application syntax"),
"c10aec6d4dd877ec8bd8":("growing on shaded stony ground","HABITAT",.37,"f56r plant article"),
"95987d6f198d6d247511":("bind it in place overnight; close","APPLICATION_CLOSE",.39,"Herbal-local correction of outlet gloss"),
"ad3581d3144f69a5912d":("for the seed preparation","PLANT_PART_ENTRY",.38,"f56r next-part construction"),
"b74e9e65637b7c8538dd":("the leaves after cutting","PLANT_PART",.38,"followed by drying"),
"1322bc176443fc2a8a86":("dry them in shade","PREPARATION",.48,"f56r preparation sequence"),
"087a47b5423438cd6b6a":("drink it for pain of the stomach","INDICATION_APPLICATION",.43,"f56r use formula"),
"75a523fcf039b006f97b":("keep the dried medicine in shade","PRESERVATION",.37,"f56r use/preparation continuation"),
"c71c72da4e09e0833392":("mix it with honey","MEDIUM_RELATION",.50,"f56r preparation clause"),
"61a075bc54793c1c781f":("use it immediately while fresh","APPLICATION_CONDITION",.48,"f56r preparation closure"),
"faf321940aed922846a9":("set apart the following equal share","MEASURE_ENTRY",.41,"f56r terminal measure clause"),
"9bb7122b386ebbc6138f":("of the pale flower heads","PLANT_PART",.40,"visible f56r flower heads"),
}

FREEZE = [
("f10r","one tall herb; opposite paired broad serrate leaves with alternating green/brown bands; one blue composite-like terminal head; horizontal tan root joining two red swollen ends","twin-tubered blue-flowered waterside simple","composite-flowered simple with paired storage roots","https://www.voynich.com/folios/color/010r.jpg"),
("f11r","dense rounded mat or crown; many overlapping scalloped leaves; scattered small blue flowers; three pale petioles; long branching saw-toothed roots","mat-forming violet-like woodland simple","low rosette herb with blue flowers and spreading roots","https://www.voynich.com/folios/color/011r.jpg"),
("f55v","one enormous clasping broad leaf or leaf-crown; tall central reddish stalk; reticulate blue-tipped head; branching creeping root with a rounded lateral swelling","broad-leaved water-edge simple with clustered head","large dock/plantain-like simple with creeping storage root","https://www.voynich.com/folios/color/055v.jpg"),
("f56r","tall pale stem; one spiral disk with dark radial rays; two dark lateral heads ringed by narrow green points; two additional dark-blue flowers; sparse scale leaves","thistle-like many-headed simple","spiny composite-like simple with spiral seed head","https://www.voynich.com/folios/color/056r.jpg"),
]

def generic_alts(gloss: str, cls: str) -> tuple[str,str]:
    table = {
      "ARTICLE_HEAD": ("the pictured simple under its local workshop name", "the pictured simple under a second inherited name"),
      "PLANT_PART": ("take the corresponding leaf or root part", "take the visibly matching flower or seed part"),
      "PLANT_PART_ENTRY": ("as for its seed", "then take the flowering head"),
      "HABITAT": ("it grows beside still water", "it grows in moist shaded earth"),
      "GATHERING_TIME": ("gather it at first flowering", "gather it after the dew has dried"),
      "PREPARATION": ("pound it and steep it in water", "boil it and strain it once"),
      "PREPARATION_CLOSE": ("wash the root once and put it aside", "rinse the vessel once and end the step"),
      "PRESERVATION": ("keep it dried in a covered vessel", "store it immersed in oil"),
      "PRESERVATION_CLOSE": ("decant it into a covered jar; end", "let it settle in a clean vessel; end"),
      "APPLICATION": ("drink the measured preparation", "lay the measured preparation on the place"),
      "APPLICATION_CLOSE": ("leave the binding until morning; end", "wash the place and remove the binding; end"),
      "APPLICATION_CONDITION": ("use it while still warm", "use it once after cooling"),
      "INDICATION_APPLICATION": ("drink it for griping of the belly", "apply it to a painful swelling"),
      "MEDIUM": ("with spring water", "with clear wine"),
      "MEDIUM_RELATION": ("mix it with oil", "mix it with vinegar"),
      "MEASURE": ("one spoonful", "one small handful"),
      "MEASURE_ENTRY": ("set apart one equal portion", "reserve one lesser portion"),
      "QUALITY": ("it is warm and dry in the first degree", "it is cold and moist in the first degree"),
      "REFERENCE": ("repeat it from the same batch", "continue with the preceding batch"),
      "REFERENCE_RELATION": ("together with the preceding ingredient", "in the same vessel as before"),
      "IDENTIFICATION_FEATURE": ("its leaves are round and scalloped", "its root spreads close to the ground"),
      "PICTURE_REFERENCE": ("take the plant shown above", "use the corresponding pictured part"),
      "STATE_GATE": ("until it becomes clear", "until half the liquid remains"),
      "STATE_GATE_CLOSE": ("steep until clear and put it aside", "boil to half and close the step"),
      "APPLICATION_ENTRY": ("for drinking as a medicine", "for an outward binding"),
    }
    return table.get(cls, ("continue with the next concrete preparation step", "repeat the preceding concrete step once"))

def write_tsv(path: Path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w=csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main():
    rows=[r for r in csv.DictReader(SOURCE.open(encoding="utf-8"), delimiter="\t") if r["page"] in PAGES]
    counts=Counter(r["exact_tuple_id"] for r in rows)
    assert len(rows)==100 and len(counts)==66 and sum(n==1 for n in counts.values())==55
    assert set(counts)==set(M), (set(counts)-set(M),set(M)-set(counts))

    # Freeze artifact is deliberately emitted before any lexical result.
    write_tsv(HERE/"V19_R3_VISIBLE_PLANT_FREEZE.tsv", [dict(page=p,visible_features=v,primary_visual_family=a,broad_fallback=b,image_source=u,assignment_order="1_VISUAL_FREEZE_BEFORE_TEXT") for p,v,a,b,u in FREEZE], ["page","visible_features","primary_visual_family","broad_fallback","image_source","assignment_order"])

    byid=defaultdict(list)
    for r in rows: byid[r["exact_tuple_id"]].append(r)
    dictionary=[]
    for tid in sorted(byid):
        gloss,cls,conf,evidence=M[tid]
        rr=byid[tid]
        dictionary.append(dict(exact_tuple_id=tid,surfaces="|".join(sorted({x['surface'] for x in rr})),events=len(rr),pages="|".join(sorted({x['page'] for x in rr})),selected_default_English=gloss,source_class=cls,confidence=f"{conf:.2f}",evidence=evidence,recurrent_or_singleton="SINGLETON" if len(rr)==1 else "RECURRENT",silent_arguments="pictured simple/active batch/body place only where stated by article context"))
    write_tsv(HERE/"V19_R3_HERBAL_CARD_DICTIONARY.tsv",dictionary,list(dictionary[0]))

    inter=[]
    locrows=defaultdict(list)
    for r in rows: locrows[r['locus']].append(r)
    for r in rows:
        gloss,cls,conf,evidence=M[r['exact_tuple_id']]
        local=" ; ".join(M[x['exact_tuple_id']][0] for x in locrows[r['locus']])
        inter.append(dict(page=r['page'],locus=r['locus'],record=r['record'],line=r['line'],event_index=r['event_index'],surface=r['surface'],exact_tuple_id=r['exact_tuple_id'],selected_default_English=gloss,source_class=cls,confidence=f"{conf:.2f}",complete_local_phrase=local,sentence_may_cross_line="YES",evidence=evidence))
    write_tsv(HERE/"V19_R3_100_EVENT_INTERLINEAR.tsv",inter,list(inter[0]))

    alternatives=[]
    for d in dictionary:
        if d['recurrent_or_singleton']!='SINGLETON': continue
        a,b=generic_alts(d['selected_default_English'],d['source_class'])
        alternatives.append(dict(exact_tuple_id=d['exact_tuple_id'],surface=d['surfaces'],page=d['pages'],selected=d['selected_default_English'],alternative_1=a,alternative_2=b,selection_reason=f"Selected reading completes the containing article with class {d['source_class']} and fewer new inherited arguments."))
    assert len(alternatives)==55
    write_tsv(HERE/"V19_R3_SINGLETON_ALTERNATIVES.tsv",alternatives,list(alternatives[0]))

    # Complete source-register readings: punctuation follows proposed source
    # clauses, not physical line ends.
    article = '''# V19 R3 complete Herbal articles\n\nThese are concrete workshop back-expansions, not deciphered plaintext. Brackets mark picture-owned or inherited arguments absent from the individual visible group.\n\n## f10r — twin-tubered blue-flowered waterside simple\n\n**Article reading.** The pictured twin-tubered blue-flowered simple: keep the cut root in a covered jar. From the same prepared batch, pound and stir until evenly joined and reduce the dried root to powder. Use the reddish swollen root; drink it for pain of the stomach, applying the stated portion in the usual measure, and retain the remainder of the root. Use the freshly prepared remedy with the foregoing preparation; apply it while warm when the preparation is ready. It grows beside running water. When the root is ready, make the working decoction, express the root juice and boil gently; take this portion, this portion in the stated measure, and the final present portion. Gather before flowering. To one handful of decoction add the foregoing preparation, drawn from the same batch, in the usual measure. When the blue flower first opens, combine the working liquid with the prepared decoction; the present portion has a bitter taste. Preserve that portion in oil.\n\n**Executable register.** OWNER=pictured simple; PART=reddish storage root; HABITAT=running-water edge; BATCH persists through CHAR/CHOLOR; AIIN invokes the article's usual measure; each Y card readdresses the active portion.\n\n## f11r — mat-forming violet-like woodland simple\n\n**Article reading.** Gather the mat-forming simple in spring where it grows in shaded woodland, cutting it before the blue flowers open. Strain its infusion first through coarse cloth and then through fine cloth, continuing until the liquid runs clear; draw the clear liquid into a clean jar and close that preparation. The genuine plant bears small blue flowers. Of the pictured simple itself, use this present portion against a swollen place, with this present portion in the stated measure. Take the fresh leafy part, lay it on while warm when prepared, and use this portion.\n\n**Executable register.** The first sentence is identification+harvest+filtering; the close does not end the whole article. The two following short bookings reuse OWNER but open distinct outward-use formulas.\n\n## f55v — broad-leaved water-edge simple\n\n**Article reading.** Take up the next portion in the stated measure. Boil the cut leaf gently in white wine; steep until clear and close the first preparation. In the stated measure, stir until evenly mixed; wash the broad leaf once and close. For its medicinal use add white wine while the mixture is still warm; boil gently and close the heating step. In the usual measure mix the two portions, keep them in a covered jar as the prepared decoction, and use the present portion while fresh.\n\n**Executable register.** This is the most formulary-like Herbal page: two compact preparation cells share the illustrated simple. DY-like closes end substeps, not necessarily sentences or the article.\n\n## f56r — thistle-like many-headed simple\n\n**Article reading.** Gather the thistle-like simple in spring; then take the lower root in the stated measure. Next take white wine: gather the plant before flowering, apply this portion on the afflicted place. Of the pictured simple itself, growing on shaded stony ground, apply this portion and bind it in place overnight; close. For the seed preparation, take the leaves after cutting and dry them in shade. Use the freshly prepared remedy; drink it for pain of the stomach, and keep the dried medicine in shade. Next take the fresh remedy, mix it with honey and use it immediately while fresh. Set apart an equal share of the pale flower heads in the stated measure.\n\n**Executable register.** CHO/SHO opens the next material booking but does not name the material. ROOT, WINE, CUT LEAVES, FRESH REMEDY and FLOWER HEADS successively fill that slot.\n\n## Source-register inventory\n\nThe 66 cards use 24 narrowly named source classes, but collapse operationally to eleven teachable drawers: ARTICLE/PICTURE OWNER, PART, HABITAT, GATHERING, QUALITY, PREPARATION, MEDIUM, MEASURE, APPLICATION/INDICATION, REFERENCE/POINTER, and GATE/CLOSE. No disease, ingredient or plant is silently introduced except the pictured owner, an already active batch, and the body-place explicitly required by an application phrase.\n'''
    (HERE/"V19_R3_COMPLETE_HERBAL_ARTICLES.md").write_text(article,encoding="utf-8")

    report='''# Candidate V19 R3 — technical source-register reconstruction\n\n## Result\n\nThe four Herbal pages can be read as a compact article register with one active pictured OWNER, an inherited preparation BATCH, a CURRENT PORTION and short material bookings. All 100 events and all 66 exact cards receive concrete defaults. The 55 singleton cards do not require 55 semantic inventions: they occupy eleven operational drawers.\n\nThe most important correction to V18 is exact card `d665560...`: it occurs on f11r and f56r beside visibly different plants, so `local-name-D6655` cannot be a literal plant name under the one-card/one-default rule. I select **of the pictured simple itself**, a page-bound OWNER pointer. This is a genuine contradiction-driven revision, not substring inference. A second Herbal-local correction changes f56r `cheeckhody` from a biological `outlet` reading to **bind it in place overnight; close**, because no apparatus or outlet is visible or required in the Herbal article.\n\n## Register model taught to a scribe\n\n1. The drawing silently establishes OWNER; the first booking may name or describe it.\n2. A material/part card loads PART; a medium card loads MEDIUM.\n3. A preparation card transforms OWNER/PART into BATCH.\n4. AIIN recalls the usual measure; Y points to the current portion.\n5. CHO/SHO advances to the next material booking; it does not itself identify root, wine or leaf.\n6. WITH/SAME-BATCH cards preserve BATCH across a new operation.\n7. A close commits only the current substep; a sentence and article may continue across physical lines.\n\nThis is learnable without modern database machinery: it is the ordinary memory discipline of a recipe/register clerk using repeated abbreviated whole formulas.\n\n## Visible freeze and historical family guesses\n\nThe four drawings were inspected and frozen before article assignment in `V19_R3_VISIBLE_PLANT_FREEZE.tsv`. Exact species identification is not required. The primary working families are twin-tubered blue composite (f10r), mat-forming violet-like simple (f11r), broad-leaved water-edge simple (f55v), and many-headed thistle-like simple (f56r). Their broader fallbacks are retained in the freeze.\n\nThis register is historically ordinary in shape even though none of its card meanings is established. The early-fifteenth-century illustrated Herbal [Codex Bellunensis](https://www.english.cam.ac.uk/research/plantlife/digitised-manuscripts/) and the c.1440 [Sloane 4016 *Tractatus de herbis*](https://wellcomecollection.org/works/mcfn4abu) show that illustrated simples books belong in the period. The related *Circa instans* tradition organizes entries around qualities, names/synonyms and medicinal action, while the Egerton 747 compilation even contains a substitution list for unavailable ingredients ([British Library catalogue](https://searcharchives.bl.uk/catalog/032-001983805)). Those comparisons license the compact article inventory; they do not identify any depicted species or Voynich card.\n\n## Economy\n\n- visible events: 100/100\n- exact Herbal card types: 66/66\n- recurrent types: 11/11 with one fixed default each\n- singleton comparisons: 55/55 with two concrete rivals each\n- operational drawers: 11\n- explicit contextual silent arguments: pictured OWNER; active BATCH; afflicted PLACE in outward applications\n- invented one-off diseases: 0\n- invented one-off exotic ingredients: 0\n\n## Failure conditions\n\nThis reconstruction weakens if another authorized page forces `d665560...` to be a stable named substance rather than a picture pointer, if CHO/SHO occurs where no following material booking exists, or if the f11r double-straining sequence proves to be purely descriptive. The defaults remain in force until a better complete article deck replaces them.\n\n## Files\n\n- `V19_R3_VISIBLE_PLANT_FREEZE.tsv`\n- `V19_R3_HERBAL_CARD_DICTIONARY.tsv`\n- `V19_R3_100_EVENT_INTERLINEAR.tsv`\n- `V19_R3_SINGLETON_ALTERNATIVES.tsv`\n- `V19_R3_COMPLETE_HERBAL_ARTICLES.md`\n- `build_v19_r3_herbal_register.py`\n\nf84 and f84r were not accessed.\n'''
    (HERE/"CANDIDATE_V19_R3_TECHNICAL_HERBAL_REGISTER.md").write_text(report,encoding="utf-8")
    print(f"events={len(rows)} types={len(counts)} singletons={len(alternatives)}")

if __name__ == "__main__": main()
