#!/usr/bin/env python3
"""Build V18 R2's six-card medical reconstruction from the frozen V17 ledger."""

from __future__ import annotations

import csv
from collections import Counter, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = ROOT / "experiments/yolo/sidequest_theory_candidates_v17/V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"

# Rival meanings are exactly the V18 frozen alternatives, rendered concretely.
# Repair tuples count: silent substance, vessel, body part, comparison,
# antecedent, ad-hoc sense/contradiction.
CARDS = {
    "0275fbf14e07935b0a45": {
        "surfaces": "okeey|qokeey", "selected": "temper the working liquid and keep it lukewarm",
        "confidence": .68, "source_class": "LUKEWARM_WORKING_CONDITION",
        "rivals": [
            ("temper the working liquid and keep it lukewarm", (7,0,0,0,7,1), 26),
            ("mix the preparation thoroughly", (7,0,0,0,7,6), 16),
            ("add warmed water to the preparation", (7,0,0,0,0,5), 19),
        ],
        "conditioned": "after an immersion card: keep the bath lukewarm",
        "before": "mixed, filled, immersed, bound, or settled working liquid",
        "after": "lukewarm liquid ready for straining, rinsing, immersion, or application",
    },
    "de7321bface5628e35d6": {
        "surfaces": "lchedy", "selected": "let the spent liquid drain into the lower vessel; end this instruction",
        "confidence": .64, "source_class": "LOWER_VESSEL_DRAIN_CLOSE",
        "rivals": [
            ("leave it standing in the lower vessel; end this instruction", (8,8,0,0,8,3), 19),
            ("let the spent liquid drain into the lower vessel; end this instruction", (8,8,0,0,8,0), 25),
            ("let it cool to the ordinary base setting; end this instruction", (8,0,0,8,8,6), 10),
        ],
        "conditioned": "after full immersion: let the bath drain down into the lower vessel",
        "before": "immersed, washed, boiled, or mixed liquid remains in the active basin/channel",
        "after": "spent liquid is collected below and the local liquid-handling step is closed",
    },
    "259b2b3b0bf859882e2c": {
        "surfaces": "dchedy|schedy|tchedy", "selected": "wash the used basin or channel through once; end this instruction",
        "confidence": .56, "source_class": "APPARATUS_FLUSH_CLOSE",
        "rivals": [
            ("finish this treatment; end this instruction", (0,0,0,0,4,3), 17),
            ("strain the application and set it aside", (0,4,0,0,4,5), 13),
            ("wash the used basin or channel through once; end this instruction", (4,4,0,0,4,0), 23),
        ],
        "conditioned": "after connected channels: wash the channels through once",
        "before": "the preceding bath, channel passage, or treatment has spent its liquid",
        "after": "the apparatus is rinsed and ready for a retained or newly warmed charge",
    },
    "28ffbc88b97772a75f1e": {
        "surfaces": "olchedy|qolchedy", "selected": "set the mixed liquid aside in a covered vessel; end this instruction",
        "confidence": .60, "source_class": "COVERED_RESERVE_CLOSE",
        "rivals": [
            ("set the mixed liquid aside in a covered vessel; end this instruction", (3,3,0,0,3,0), 25),
            ("draw off the clear liquor; end this instruction", (3,3,0,0,3,4), 17),
            ("retain the mixture in the present vessel; end this instruction", (3,3,0,0,3,2), 21),
        ],
        "conditioned": "none",
        "before": "a warm, stirred, or flushed mixture has just been prepared",
        "after": "a protected reserve is available while a new measured portion is prepared",
    },
    "4d4559019a961b834aa1": {
        "surfaces": "char|dar|sar", "selected": "from the same prepared batch",
        "confidence": .66, "source_class": "SAME_BATCH_SOURCE_REFERENCE",
        "rivals": [
            ("from the same prepared batch", (0,0,0,0,5,1), 26),
            ("then continue with the next step", (0,0,0,0,0,3), 20),
            ("repeat the foregoing preparation", (0,0,0,0,5,4), 17),
        ],
        "conditioned": "after a measure/addition: take the next charge from that same batch",
        "before": "a named preparation, measured addition, or returning liquid is active",
        "after": "the active material source remains identical across the next operation",
    },
    "2cc054357a929df85f64": {
        "surfaces": "cho|sho", "selected": "then take the following ingredient or plant part",
        "confidence": .76, "source_class": "NEXT_INGREDIENT_IMPERATIVE",
        "rivals": [
            ("then take the following ingredient or plant part", (0,0,0,0,4,0), 28),
            ("resume the description of the pictured plant", (0,0,0,0,4,3), 18),
            ("take the flowering tops", (0,0,4,0,0,7), 11),
        ],
        "conditioned": "at physical-line entry: for the next preparation, take the following ingredient",
        "before": "a harvest clause, seed clause, or preceding preparation is complete",
        "after": "the immediately following root, wine, dried leaf, or fresh remedy becomes the active material",
    },
}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path: Path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def line_text(seq, override_tid=None, override=None):
    out=[]
    used=False
    for r in seq:
        meaning=r["default_English"]
        if override_tid and r["exact_tuple_id"] == override_tid and not used:
            meaning=override; used=True
        out.append(f'{r["surface"]} = {meaning}')
    return " ; ".join(out)


def main():
    rows=[r for r in read_tsv(LEDGER) if r["ledger_scope"]=="GDT327_PROSE"]
    targets=[r for r in rows if r["exact_tuple_id"] in CARDS]
    assert len(targets)==31, len(targets)
    assert Counter(r["exact_tuple_id"] for r in targets)==Counter({
        "0275fbf14e07935b0a45":7,"de7321bface5628e35d6":8,
        "259b2b3b0bf859882e2c":4,"28ffbc88b97772a75f1e":3,
        "4d4559019a961b834aa1":5,"2cc054357a929df85f64":4})

    byline=OrderedDict()
    for r in rows: byline.setdefault((r["page"],r["locus"]),[]).append(r)
    linekeys=list(byline)
    decision=[]
    for tid,c in CARDS.items():
        rr=[r for r in targets if r["exact_tuple_id"]==tid]
        out={"exact_tuple_id":tid,"surfaces":c["surfaces"],"occurrences":len(rr),
             "pages":"|".join(sorted({r['page'] for r in rr})),
             "v17_incumbent":rr[0]["default_English"]}
        for i,(meaning,rep,score) in enumerate(c["rivals"],1):
            out[f"rival_{i}"]=meaning
            for n,v in zip(("silent_substances","silent_vessels","silent_bodyparts","silent_comparisons","inherited_antecedents","adhoc_or_contradictions"),rep): out[f"rival_{i}_{n}"]=v
            out[f"rival_{i}_whole_context_score_0_30"]=score
        out.update(selected_meaning=c["selected"],conditioned_sense=c["conditioned"],confidence=f'{c["confidence"]:.2f}',source_class=c["source_class"],medical_process_before=c["before"],medical_process_after=c["after"])
        decision.append(out)
    write_tsv(HERE/"V18_R2_SIX_CARD_DECISIONS.tsv",decision)

    occ=[]
    serial=0
    for r in targets:
        serial+=1; tid=r["exact_tuple_id"]; c=CARDS[tid]; k=(r["page"],r["locus"]); i=linekeys.index(k)
        prev=byline[linekeys[i-1]] if i and linekeys[i-1][0]==r["page"] else []
        nxt=byline[linekeys[i+1]] if i+1<len(linekeys) and linekeys[i+1][0]==r["page"] else []
        cur=byline[k]
        rivals=c["rivals"]
        occ.append({
            "occurrence":serial,"page":r["page"],"locus":r["locus"],"record":r["record"],"event_index":r["event_index"],
            "surface":r["surface"],"exact_tuple_id":tid,"previous_complete_line":line_text(prev) if prev else "PAGE_OR_SCOPE_START",
            "complete_target_line_v17":line_text(cur),"following_complete_line":line_text(nxt) if nxt else "PAGE_OR_SCOPE_END",
            "rival_1_complete_target_line":line_text(cur,tid,rivals[0][0]),
            "rival_2_complete_target_line":line_text(cur,tid,rivals[1][0]),
            "rival_3_complete_target_line":line_text(cur,tid,rivals[2][0]),
            "selected_complete_target_line":line_text(cur,tid,c["selected"]),
            "process_graph":f'{c["before"]} -> [{r["surface"]}: {c["selected"]}] -> {c["after"]}',
            "silent_repairs_selected":"active preparation/person/vessel inherited from the current record; no new unpictured entity",
            "medical_comment":"selected against all three frozen rivals in the full line and adjacent-line process",
        })
    write_tsv(HERE/"V18_R2_31_OCCURRENCE_RECONSTRUCTIONS.tsv",occ)

    pages=sorted({r["page"] for r in targets})
    md=["# V18 R2 — complete affected passages", "",
        "Every target is expanded with the R2 selected concrete medical meaning. Physical lines are retained; they are not assumed to be sentence boundaries.",""]
    for p in pages:
        md += [f"## {p}",""]
        for k,seq in byline.items():
            if k[0]!=p: continue
            text=[]
            for x in seq:
                m=CARDS[x["exact_tuple_id"]]["selected"] if x["exact_tuple_id"] in CARDS else x["default_English"]
                text.append(m)
            md.append(f'- `{k[1]}`: '+"; ".join(text)+".")
        md.append("")
    (HERE/"V18_R2_COMPLETE_AFFECTED_PASSAGES.md").write_text("\n".join(md),encoding="utf-8")


if __name__=="__main__": main()
