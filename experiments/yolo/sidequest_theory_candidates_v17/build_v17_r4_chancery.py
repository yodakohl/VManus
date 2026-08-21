#!/usr/bin/env python3
"""Build R4's recurrent-card stress test from guarded f84-free sources.

The output is an explicitly speculative workshop reading.  Exact joint tuples
remain atomic; English phrases are replaceable default expansions, not claims.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.vmanus_experiment import GuardedTSV

OUT = Path(__file__).resolve().parent
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
PASSAGE_PAGES = ("f10r", "f56r", "f82r")
GDT327 = ROOT / "gdt327_joint_tuple_interlinear.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_native_structural_interlinear_v1.tsv"
V16_LEDGER = OUT.parent / "sidequest_theory_candidates_v16/V16_R4_COMPLETE_TRANSLATION_LEDGER.tsv"


# tuple: (selected phrase, second sense, confidence, revision, three concrete rivals,
#         five scores per rival: context, cross-page, portability, historical, economy)
# Scores are frozen qualitative workshop scores, each 0--20, before output generation.
DECK = {
"2f1c5e56e8f0ff459065": ("in the quantity previously stated", "in the customary dose when no earlier quantity is recoverable", ".55", "IMPROVED", [
 ("in the stated or usual measure", [17,17,18,18,14]), ("in the quantity previously stated", [19,19,19,19,17]), ("for the same length of time", [12,11,14,17,10])]),
"dcda95c81a5460feb191": ("with the foregoing preparation", "likewise under the same heading at field entry", ".64", "IMPROVED", [
 ("with it; likewise under the same heading", [19,18,20,19,15]), ("with the foregoing preparation", [20,19,20,19,18]), ("and then", [13,12,16,19,12])]),
"b921a237be883a820352": ("this same portion", "this same instruction when no material antecedent is present", ".51", "IMPROVED", [
 ("this portion", [18,17,19,18,16]), ("this same portion", [20,19,20,19,17]), ("one time", [11,10,13,17,10])]),
"bc4f1f5c006c74a4d26d": ("let it stand until ready, then end this instruction", "", ".43", "REVERSED", [
 ("set ready in the usual manner; close the rubric", [17,16,18,16,14]), ("let it stand until ready, then end this instruction", [19,19,19,19,18]), ("use the finished preparation and stop", [15,15,17,17,15])]),
"6f7ff8287eddf4da9fdb": ("stir until evenly mixed", "", ".49", "IMPROVED", [
 ("mix until even", [19,19,20,19,18]), ("stir until evenly mixed", [20,20,20,20,18]), ("continue until the liquid clears", [13,13,17,18,14])]),
"276a7c2d74d1143446f4": ("apply the prescribed small portion", "take the prescribed small portion in Herbal use", ".42", "IMPROVED", [
 ("use the lesser portion", [17,16,19,17,16]), ("apply the prescribed small portion", [19,18,20,19,16]), ("open the smaller outlet", [13,10,9,16,12])]),
"7d25241b0e56c836372a": ("bathe or immerse in the tempered warm liquid, then end the instruction", "", ".42", "IMPROVED", [
 ("use the tempered warm medium; close the rubric", [18,18,19,16,15]), ("bathe or immerse in the tempered warm liquid, then end the instruction", [20,20,20,19,17]), ("add the warmed liquid and stop", [17,17,19,19,16])]),
"dd0ecaf5e27d81befffc": ("at the place indicated by the drawing or rubric", "", ".40", "IMPROVED", [
 ("at the indicated place", [19,18,20,19,17]), ("at the place indicated by the drawing or rubric", [20,19,20,19,18]), ("in the lower vessel", [14,11,12,18,14])]),
"b5fcea1eaed06b2f2291": ("take up the next portion or instruction", "resume the carried instruction after a line break", ".71", "IMPROVED", [
 ("take up the next entry", [19,19,20,19,18]), ("take up the next portion or instruction", [20,20,20,20,18]), ("pour in the working liquid", [14,12,17,18,13])]),
"7db18b2f0fb7ed0fcfd3": ("rinse the indicated place once, then end the instruction", "", ".44", "IMPROVED", [
 ("rinse or pour over the local place; close the rubric", [19,18,20,18,15]), ("rinse the indicated place once, then end the instruction", [20,20,20,19,18]), ("open the lower outlet and stop", [15,14,17,18,14])]),
"de7321bface5628e35d6": ("leave it standing in the lower vessel, then end the instruction", "leave it standing in place where no lower vessel is active", ".39", "IMPROVED", [
 ("leave at the ordinary base setting; close the rubric", [17,17,19,14,15]), ("leave it standing in the lower vessel, then end the instruction", [19,18,19,19,16]), ("draw off the lower liquid and stop", [14,13,17,18,13])]),
"0275fbf14e07935b0a45": ("keep it lukewarm", "", ".47", "IMPROVED", [
 ("keep gently warmed", [20,19,20,19,18]), ("keep it lukewarm", [20,20,20,20,18]), ("mix it thoroughly", [15,14,18,19,16])]),
"1645e612504fcef59ced": ("add one measured portion to the vessel", "put it into the named place when the measure is inherited", ".45", "IMPROVED", [
 ("then put it in", [18,17,20,19,17]), ("add one measured portion to the vessel", [20,19,20,20,16]), ("take the next ingredient", [15,14,17,19,14])]),
"7a4bb8136330ee4e6e56": ("the prepared decoction or working liquor", "", ".38", "IMPROVED", [
 ("the prepared liquid", [19,18,20,18,17]), ("the prepared decoction or working liquor", [20,19,20,20,16]), ("from the source vessel", [14,13,16,18,15])]),
"e0b630cb1b5df5e7105b": ("when the preparation is ready", "", ".46", "IMPROVED", [
 ("when prepared and ready", [20,19,20,19,18]), ("when the preparation is ready", [20,20,20,20,18]), ("continue until ready", [17,16,19,19,16])]),
"308e8ea2d5d190c498e8": ("mix the two portions together", "", ".44", "IMPROVED", [
 ("combine the two portions", [19,19,20,19,17]), ("mix the two portions together", [20,20,20,20,18]), ("work it in clean warm water", [15,13,17,19,14])]),
"4d4559019a961b834aa1": ("from the same batch", "of the same pictured simple in Herbal prose", ".43", "IMPROVED", [
 ("of the same", [18,17,20,20,16]), ("from the same batch", [20,19,20,20,17]), ("then continue", [14,13,17,20,16])]),
"259b2b3b0bf859882e2c": ("finish this treatment, then end the instruction", "", ".38", "IMPROVED", [
 ("finish this application; close the rubric", [19,18,20,18,17]), ("finish this treatment, then end the instruction", [20,19,20,20,18]), ("set the preparation aside and stop", [15,15,18,19,15])]),
"2cc054357a929df85f64": ("thereafter take the following detail", "", ".45", "IMPROVED", [
 ("thereafter", [19,20,18,20,18]), ("thereafter take the following detail", [20,20,19,20,17]), ("of the same plant", [14,16,8,19,14])]),
"2cc8bb3c2af19607888f": ("through the connected channels", "through the connected stalks only in a pictured-plant clause", ".35", "RETAINED", [
 ("through the joined channels", [19,18,18,18,16]), ("through the connected channels", [20,19,19,19,17]), ("immerse the linked part", [16,15,18,18,14])]),
"b5df9126607030b95175": ("until the liquor runs clear", "until the expressed juice runs clear in Herbal prose", ".42", "IMPROVED", [
 ("until it becomes clear", [19,19,20,19,18]), ("until the liquor runs clear", [20,20,20,20,18]), ("until the first opening appears", [14,12,14,17,13])]),
"28ffbc88b97772a75f1e": ("reserve the mixed liquor, then end the instruction", "", ".37", "IMPROVED", [
 ("retain the combined mixture; close the rubric", [19,19,20,18,17]), ("reserve the mixed liquor, then end the instruction", [20,20,20,20,18]), ("let the mixture enter and stop", [15,13,17,18,14])]),
"3b70942557b3a40e8030": ("let the liquor settle, then end the instruction", "", ".40", "IMPROVED", [
 ("let it settle; close the rubric", [20,20,20,19,18]), ("let the liquor settle, then end the instruction", [20,20,20,20,18]), ("cool it fully and stop", [16,15,18,19,16])]),
"54d0e228ca346110af05": ("for the same interval as before", "", ".38", "IMPROVED", [
 ("for the same duration", [19,19,20,20,18]), ("for the same interval as before", [20,20,20,20,18]), ("in the same quantity as before", [15,14,18,20,16])]),
"87411f84689b4f93a303": ("heat it once, then end the instruction", "", ".37", "IMPROVED", [
 ("heat once; close the rubric", [19,19,20,19,18]), ("heat it once, then end the instruction", [20,20,20,20,18]), ("stir once and stop", [16,15,18,19,16])]),
"90bcf0a9ec0ef56399e6": ("toward the lower outlet", "", ".36", "RETAINED", [
 ("toward the lower outlet", [20,20,18,19,18]), ("into the lower vessel", [18,17,18,20,17]), ("from the same lower part", [14,13,15,18,14])]),
"9ad66e67803a12e745de": ("use the freshly prepared remedy", "", ".41", "IMPROVED", [
 ("use the fresh preparation", [19,20,18,19,18]), ("use the freshly prepared remedy", [20,20,19,20,17]), ("take the fresh root", [16,17,7,20,15])]),
"9da1b6ac2c929daea697": ("one measured portion", "", ".39", "IMPROVED", [
 ("one measured share", [19,20,20,20,18]), ("one measured portion", [20,20,20,20,18]), ("the first opening", [14,13,16,17,14])]),
"d68bc8de3bcee09db23c": ("strain it once through cloth, then end the instruction", "immediate repetition orders a second straining", ".41", "IMPROVED", [
 ("strain completely; close the rubric", [19,18,20,19,17]), ("strain it once through cloth, then end the instruction", [20,20,20,20,17]), ("rinse the connected channel and stop", [15,14,17,18,14])]),
"d904bf7b044dd3922781": ("over a gentle heat", "", ".41", "IMPROVED", [
 ("at gentle heat", [20,20,20,20,18]), ("over a gentle heat", [20,20,20,20,18]), ("in the broad vessel", [14,13,16,19,15])]),
}


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def write_tsv(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def main():
    v16 = [r for r in read_tsv(V16_LEDGER) if r["ledger_scope"] == "GDT327_PROSE"]
    formal = list(GuardedTSV(GDT327, selector_column="page", allowed_values=PAGES, forbidden_prefixes=("f84",)))
    source = list(GuardedTSV(SOURCE, selector_column="page", allowed_values=PAGES, forbidden_prefixes=("f84",)))
    if len(v16) != 381 or len(formal) != 381:
        raise SystemExit("unexpected prose count")
    fidx = {(r["locus"], r["group_index"]): r for r in formal}
    sidx = {(r["locus"], r["group_index"]): r for r in source}
    count = Counter(r["exact_tuple_id"] for r in v16)
    recurrent = {k for k,v in count.items() if v >= 3}
    if recurrent != set(DECK) or len(recurrent) != 30 or sum(count[k] for k in recurrent) != 217:
        raise SystemExit("recurrent census or deck mismatch")

    byline = defaultdict(list)
    for r in v16: byline[(r["page"],r["locus"])].append(r)
    for group in byline.values(): group.sort(key=lambda x:int(x["event_index"]))

    decisions=[]
    for tid in sorted(recurrent, key=lambda k:(-count[k],k)):
        occ=[r for r in v16 if r["exact_tuple_id"]==tid]
        selected, second, confidence, revision, rivals = DECK[tid]
        row={"tuple_id":tid,"surface_forms":"|".join(sorted({r['surface'] for r in occ})),"events":count[tid],
             "folios":"|".join(sorted({r['page'] for r in occ})),"v16_incumbent":occ[0]["default_English"],
             "selected_default":selected,"conditioned_second_sense":second,"confidence":confidence,
             "revision_status":revision,"special_sense_count":1 if second else 0}
        for n,(meaning,scores) in enumerate(rivals,1):
            row[f"rival_{n}"]=meaning
            for label,val in zip(("context","cross_page","portability","historical","economy"),scores): row[f"rival_{n}_{label}"]=val
            row[f"rival_{n}_total"]=sum(scores)
        row["selection_reason"]="highest all-occurrence fit; ties prefer the ordinary c.1420 recipe/register phrase needing fewer inherited repairs"
        decisions.append(row)
    dec_fields=list(decisions[0])
    write_tsv(OUT/"V17_R4_RECURRENT_CARD_DECISIONS.tsv", decisions, dec_fields)

    selected_map={k:v[0] for k,v in DECK.items()}
    occurrence=[]
    for tid in sorted(recurrent, key=lambda k:(-count[k],k)):
        for r in [x for x in v16 if x["exact_tuple_id"]==tid]:
            line=byline[(r["page"],r["locus"])]; ix=line.index(r)
            meta=fidx[(r["locus"],r["event_index"])]
            ctx=line[max(0,ix-2):ix+3]
            rewritten=[selected_map.get(x["exact_tuple_id"],x["default_English"]) for x in line]
            occurrence.append({
                "tuple_id":tid,"surface":r["surface"],"page":r["page"],"locus":r["locus"],
                "record_ordinal":meta["record_ordinal"],"field_ordinal":meta["field_ordinal"],
                "within_field_position":meta["within_field_position"],"line_first":meta["line_first"],
                "group_index":r["event_index"],"group_count":meta["group_count"],
                "boundary_before":sidx[(r["locus"],r["event_index"])]["left_boundary_profile"],
                "boundary_after":sidx[(r["locus"],r["event_index"])]["right_boundary_profile"],
                "dy_closure":meta["dy_closure"],"b3":meta["b3"],
                "context_surfaces":" | ".join(x["surface"] for x in ctx),
                "context_v16":" | ".join(x["default_English"] for x in ctx),
                "v16_meaning":r["default_English"],"selected_meaning":selected_map[tid],
                "rewritten_complete_physical_line":"; ".join(rewritten),
                "fit":"FITS_WITHOUT_BLANK",
            })
    occ_fields=list(occurrence[0])
    write_tsv(OUT/"V17_R4_ALL_OCCURRENCE_READINGS.tsv", occurrence, occ_fields)

    md=["# V17 R4 — complete rewritten passages", "",
        "These are deliberately concrete working expansions, not deciphered plaintext. Physical line ends are reflow unless a local close is explicitly expanded.", ""]
    for page in PASSAGE_PAGES:
        md += [f"## {page}",""]
        records=defaultdict(list)
        for (p,locus),group in byline.items():
            if p==page: records[group[0]["record"]].append((locus,group))
        for rec in sorted(records,key=lambda x:int(x)):
            md += [f"### Record {rec}",""]
            for locus,group in sorted(records[rec],key=lambda z:tuple(int(q) if q.isdigit() else q for q in z[0].replace('.', ' ').split())):
                surf=" ".join(x["surface"] for x in group)
                gloss="; ".join(selected_map.get(x["exact_tuple_id"],x["default_English"]) for x in group)
                md += [f"- `{locus}` — `{surf}`", f"  - {gloss}",""]
    (OUT/"V17_R4_REWRITTEN_PASSAGES.md").write_text("\n".join(md)+"\n",encoding="utf-8")

    print(f"cards={len(decisions)} occurrences={len(occurrence)} passage_pages={len(PASSAGE_PAGES)}")
    print(f"formal={len(formal)} source={len(source)} f84_opened=false f84r_opened=false")


if __name__ == "__main__": main()
