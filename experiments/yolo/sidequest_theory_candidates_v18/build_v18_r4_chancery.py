#!/usr/bin/env python3
"""Build the independent V18 R4 chancery/copying reconstruction.

This is a deliberately concrete ten-page workshop reading, not deciphered
plaintext.  It reads only guarded f84-free GDT327 rows and frozen V17 products.
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
GDT327 = ROOT / "gdt327_joint_tuple_interlinear.tsv"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_native_structural_interlinear_v1.tsv"
V17_LEDGER = OUT.parent / "sidequest_theory_candidates_v17/V17_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"
PAGES = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r"}
AFFECTED_PAGES = ("f10r", "f56r", "f81v", "f82r", "f83r")


# All scores and repair inventories were fixed after reading the V17 contexts
# and before generation of the outputs.  Repairs count omitted referents even
# where picture/register ellipsis makes them cheap; ad_hoc counts true rescue
# clauses or card-specific sense changes.
CARDS = {
    "0275fbf14e07935b0a45": {
        "name": "OKEEY/QOKEEY", "events": 7,
        "incumbent": "keep it lukewarm",
        "selected": "top up the active bath with warmed water",
        "conditioned": "restore the working liquid with warmed water when no person is immersed",
        "confidence": ".58",
        "rivals": [
            ("keep the active preparation lukewarm", 81, "substance=7;vessel=0;body=0;comparison=0;antecedent=7;ad_hoc=2",
             "works generally, but duplicates an immediately preceding KEEP-WARM card once and adds no material before several strain/rinse chains"),
            ("mix the active preparation thoroughly", 66, "substance=7;vessel=0;body=0;comparison=0;antecedent=7;ad_hoc=7",
             "collapses into the already recurrent CHEDY stir-evenly card and leaves the warm-liquid ecology unexplained"),
            ("top up the active bath with warmed water", 92, "substance=7;vessel=5;body=0;comparison=0;antecedent=0;ad_hoc=0",
             "supplies the working liquid before straining, immersion, rinsing and application; it is replenishment, not the separate initial pour or heat command"),
        ],
        "before": "active bath or working liquid is mixed, cooled, marked or awaiting reuse",
        "after": "bath volume and warmth are restored for straining, immersion, rinsing or application",
        "scribal": "The sole unwrapped OKEEY and six q-renderings keep one action; q is not translated. No adjacent duplicate occurs.",
    },
    "de7321bface5628e35d6": {
        "name": "LCHEDY", "events": 8,
        "incumbent": "leave it standing in the lower vessel",
        "selected": "let the whole liquid drain into the lower receiving vessel; close this step",
        "conditioned": "pour it into the lower receiving vessel when no open outlet is active",
        "confidence": ".64",
        "rivals": [
            ("leave it standing in the lower vessel", 79, "substance=8;vessel=8;body=0;comparison=0;antecedent=0;ad_hoc=3",
             "fits the lower receiver but duplicates OLKEEDY settling and is awkward beside OPEN/CLOSE LOWER OUTLET and immediate refilling"),
            ("let the whole liquid drain into the lower receiving vessel", 94, "substance=8;vessel=7;body=0;comparison=0;antecedent=0;ad_hoc=0",
             "explains lower-outlet ownership, upper-channel opening, wash-then-empty and drain-then-refill sequences across all eight copies"),
            ("cool it to the ordinary base setting", 59, "substance=8;vessel=0;body=0;comparison=8;antecedent=8;ad_hoc=3",
             "needs an unattested comparison standard and duplicates explicit COOL and SETTLE cards"),
        ],
        "before": "an immersed, washed or mixed liquid occupies the working place or upper vessel",
        "after": "the working place is emptied and the lower receiver holds the whole run; the substep is committed",
        "scribal": "All eight copies carry DY closure, but only one is physical-line final. The stable action-plus-close card is not a line-ending flourish.",
    },
    "259b2b3b0bf859882e2c": {
        "name": "DCHEDY/SCHEDY/TCHEDY", "events": 4,
        "incumbent": "finish this treatment",
        "selected": "wash the active vessel or conduit through once; close this step",
        "conditioned": "wash the connected route through once after a conduit has just been named",
        "confidence": ".56",
        "rivals": [
            ("finish the current treatment", 78, "substance=0;vessel=0;body=0;comparison=0;antecedent=4;ad_hoc=3",
             "fits the one post-channel copy, but three line-entry copies would close an unstated action before immediately beginning another"),
            ("strain the liquid once", 69, "substance=4;vessel=4;body=0;comparison=0;antecedent=0;ad_hoc=4",
             "is possible after channels but duplicates the explicit SHCKHEDY through-cloth strain card"),
            ("wash the active vessel or conduit through once", 90, "substance=4;vessel=4;body=0;comparison=0;antecedent=0;ad_hoc=0",
             "works as a self-contained first field and as the action immediately following connected channels while remaining distinct from local rinsing"),
        ],
        "before": "a vessel/route is available, or a measured immersed portion has just passed through connected channels",
        "after": "the active vessel/route has been flushed once and is ready for the next liquid or heating cycle",
        "scribal": "d/s/t are line-entry/hand renderings of one exact card, not three meanings. Three initial copies are resumptive starts, not dittography.",
    },
    "28ffbc88b97772a75f1e": {
        "name": "OLCHEDY/QOLCHEDY", "events": 3,
        "incumbent": "reserve the mixed liquid",
        "selected": "set the prepared liquor aside in a receiving vessel; close this step",
        "conditioned": "retain the entire freshly mixed liquor when no settled upper layer has been established",
        "confidence": ".54",
        "rivals": [
            ("set the prepared liquor aside in a receiving vessel", 91, "substance=3;vessel=3;body=0;comparison=0;antecedent=0;ad_hoc=0",
             "works after standing or mixing and before a new measured addition without requiring a clear upper layer"),
            ("draw off the clear upper liquor into a receiver", 82, "substance=3;vessel=3;body=0;comparison=0;antecedent=0;ad_hoc=2",
             "excellent after the explicit stand on f81v, but two copies lack a preceding settling/clarity condition"),
            ("retain the entire mixture in the same vessel", 85, "substance=3;vessel=3;body=0;comparison=0;antecedent=0;ad_hoc=1",
             "preserves material but gives a weaker reason for the closed field followed by a new addition or new entry"),
        ],
        "before": "a warmed, stirred or freshly mixed working liquor has been completed",
        "after": "the prepared liquor is reserved in a receiver while the scribe advances to the next addition or conduit step",
        "scribal": "All three are singleton close-bearing fields. They are neither accidental repeats nor the cloth-strain card; the field boundary marks completion of reserving.",
    },
    "4d4559019a961b834aa1": {
        "name": "CHAR/DAR/SAR", "events": 5,
        "incumbent": "from the same batch",
        "selected": "take it from the same preparation or batch",
        "conditioned": "of the same pictured simple in Herbal description",
        "confidence": ".62",
        "rivals": [
            ("take it from the same preparation or batch", 93, "substance=0;vessel=0;body=0;comparison=5;antecedent=5;ad_hoc=0",
             "links two measured additions on f82r and preserves one same-source relation in both Herbal and bath registers"),
            ("continue with the next step", 76, "substance=0;vessel=0;body=0;comparison=0;antecedent=0;ad_hoc=2",
             "is fluent but does not explain the identical additions surrounding CHAR or the final same-source qualifications"),
            ("repeat the whole foregoing preparation", 83, "substance=0;vessel=0;body=0;comparison=0;antecedent=5;ad_hoc=3",
             "overstates the repetition in Herbal clauses and would duplicate the whole process rather than select its material"),
        ],
        "before": "a named simple, working batch, flow or measured addition is active",
        "after": "the next amount/action inherits that same material source rather than starting a fresh batch",
        "scribal": "ch/d/s surfaces are renderings of one exact cross-register reference card. No copy is adjacent to itself, so dittography does not explain recurrence.",
    },
    "2cc054357a929df85f64": {
        "name": "CHO/SHO on f56r", "events": 4,
        "incumbent": "thereafter take the following detail",
        "selected": "then take or use the following plant part or ingredient",
        "conditioned": "then take the following named plant part in the two medial copies",
        "confidence": ".71",
        "rivals": [
            ("then take or use the following plant part or ingredient", 96, "substance=0;vessel=0;body=0;comparison=0;antecedent=0;ad_hoc=0",
             "governs lower root, wine, dried leaf and fresh remedy/honey with one ordinary imperative continuation"),
            ("resume the pictured plant topic", 78, "substance=0;vessel=0;body=0;comparison=0;antecedent=4;ad_hoc=2",
             "can explain line-entry reuse but does not do enough work in the two medial constructions"),
            ("use the flowering tops", 38, "substance=4;vessel=0;body=0;comparison=0;antecedent=0;ad_hoc=3",
             "contradicted by the explicit working defaults lower root, wine, dried leaf and honey/fresh preparation"),
        ],
        "before": "the Herbal article has supplied a season, seed statement or previous remedy clause",
        "after": "the immediately following part/ingredient becomes the operand of TAKE/USE and the article continues",
        "scribal": "Medial CHO and line-entry SHO preserve one imperative. The s/ch alternation follows placement; it does not name four different plant parts.",
    },
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def repair_total(spec: str) -> int:
    return sum(int(part.split("=")[1]) for part in spec.split(";"))


def locus_number(locus: str) -> int:
    return int(locus.split(".")[1])


def main() -> None:
    ledger = [r for r in read_tsv(V17_LEDGER) if r["ledger_scope"] == "GDT327_PROSE"]
    formal = list(GuardedTSV(GDT327, selector_column="page", allowed_values=PAGES, forbidden_prefixes=("f84",)))
    source = list(GuardedTSV(SOURCE, selector_column="page", allowed_values=PAGES, forbidden_prefixes=("f84",)))
    # SOURCE retains alternate ZL3b/IT2a/RF1b readings; they are not independent
    # events.  The last keyed row is used only for its shared boundary profile.
    if len(ledger) != 381 or len(formal) != 381 or len(source) < 381:
        raise SystemExit(f"guarded census mismatch ledger={len(ledger)} formal={len(formal)} source={len(source)}")

    fidx = {(r["locus"], r["group_index"]): r for r in formal}
    sidx = {(r["locus"], r["group_index"]): r for r in source}
    byline: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ledger:
        byline[(row["page"], row["locus"])].append(row)
    for rows in byline.values():
        rows.sort(key=lambda r: int(r["event_index"]))
    page_lines: dict[str, list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
    for (page, locus), rows in byline.items():
        page_lines[page].append((locus, rows))
    for rows in page_lines.values():
        rows.sort(key=lambda pair: locus_number(pair[0]))

    target_ids = set(CARDS)
    counts = Counter(r["exact_tuple_id"] for r in ledger if r["exact_tuple_id"] in target_ids)
    if counts != Counter({tid: card["events"] for tid, card in CARDS.items()}):
        raise SystemExit(f"target census mismatch: {counts}")
    if sum(counts.values()) != 31:
        raise SystemExit("expected exactly 31 targets")

    decisions: list[dict[str, object]] = []
    for tid, card in CARDS.items():
        occ = [r for r in ledger if r["exact_tuple_id"] == tid]
        row: dict[str, object] = {
            "tuple_id": tid,
            "surfaces": "|".join(sorted({r["surface"] for r in occ})),
            "events": len(occ),
            "folios": "|".join(sorted({r["page"] for r in occ})),
            "v17_incumbent": card["incumbent"],
            "selected_default": card["selected"],
            "conditioned_sense": card["conditioned"],
            "confidence": card["confidence"],
        }
        for i, (meaning, score, repairs, reason) in enumerate(card["rivals"], 1):
            row[f"rival_{i}"] = meaning
            row[f"rival_{i}_score_100"] = score
            row[f"rival_{i}_repair_counts"] = repairs
            row[f"rival_{i}_repair_total"] = repair_total(repairs)
            row[f"rival_{i}_assessment"] = reason
        row["selected_rival"] = max(range(1, 4), key=lambda i: card["rivals"][i - 1][1])
        row["copying_segmentation_audit"] = card["scribal"]
        decisions.append(row)
    write_tsv(OUT / "V18_R4_SIX_CARD_DECISIONS.tsv", decisions, list(decisions[0]))

    selected_map = {tid: str(card["selected"]) for tid, card in CARDS.items()}
    occurrences: list[dict[str, object]] = []
    serial = 0
    for page in AFFECTED_PAGES:
        lines = page_lines[page]
        line_pos = {locus: i for i, (locus, _) in enumerate(lines)}
        for locus, line in lines:
            for ix, event in enumerate(line):
                tid = event["exact_tuple_id"]
                if tid not in CARDS:
                    continue
                serial += 1
                meta = fidx[(locus, event["event_index"])]
                src = sidx[(locus, event["event_index"])]
                field = [x for x in line if fidx[(locus, x["event_index"])]["field_ordinal"] == meta["field_ordinal"]]
                prev_line = lines[line_pos[locus] - 1][1] if line_pos[locus] else []
                next_line = lines[line_pos[locus] + 1][1] if line_pos[locus] + 1 < len(lines) else []
                prior = line[ix - 1]["default_English"] if ix else (prev_line[-1]["default_English"] if prev_line else "page/record opening")
                following = line[ix + 1]["default_English"] if ix + 1 < len(line) else (next_line[0]["default_English"] if next_line else "page/record completion")
                rivals = CARDS[tid]["rivals"]
                occurrences.append({
                    "occurrence": serial,
                    "tuple_id": tid,
                    "surface": event["surface"],
                    "page": page,
                    "locus": locus,
                    "record_ordinal": meta["record_ordinal"],
                    "field_ordinal": meta["field_ordinal"],
                    "within_field_position": meta["within_field_position"],
                    "line_first": meta["line_first"],
                    "dy_closure": meta["dy_closure"],
                    "b3": meta["b3"],
                    "boundary_before": src["left_boundary_profile"],
                    "boundary_after": src["right_boundary_profile"],
                    "complete_field_surface": " ".join(x["surface"] for x in field),
                    "complete_field_v17": "; ".join(x["default_English"] for x in field),
                    "preceding_physical_line": "; ".join(x["default_English"] for x in prev_line) or "PAGE_START",
                    "target_physical_line_v17": "; ".join(x["default_English"] for x in line),
                    "following_physical_line": "; ".join(x["default_English"] for x in next_line) or "PAGE_END",
                    "immediate_before_state": prior,
                    "selected_transition": CARDS[tid]["selected"],
                    "immediate_after_state": following,
                    "rival_1_inserted_sequence": f"{prior} -> [{rivals[0][0]}] -> {following}",
                    "rival_2_inserted_sequence": f"{prior} -> [{rivals[1][0]}] -> {following}",
                    "rival_3_inserted_sequence": f"{prior} -> [{rivals[2][0]}] -> {following}",
                    "rewritten_target_line": "; ".join(selected_map.get(x["exact_tuple_id"], x["default_English"]) for x in line),
                    "process_before_class": CARDS[tid]["before"],
                    "process_after_class": CARDS[tid]["after"],
                    "visible_owner": "surface sequence, field/line placement and page drawing",
                    "silent_owner": "liquid/vessel/body referent inherited from current register or pictured apparatus",
                    "fit": "CONCRETE_DEFAULT_FITS",
                })
    if len(occurrences) != 31:
        raise SystemExit(f"expected 31 occurrence reconstructions, got {len(occurrences)}")
    write_tsv(OUT / "V18_R4_31_OCCURRENCE_RECONSTRUCTIONS.tsv", occurrences, list(occurrences[0]))

    graph = ["# V18 R4 — six explicit process graphs", "",
             "Every arrow is a concrete workshop expansion. It is not a plaintext claim.", ""]
    for tid, card in CARDS.items():
        graph += [f"## {card['name']} — `{tid[:8]}…`", "", "```text",
                  f"BEFORE: {card['before']}", f"  -> CARD: {card['selected']}",
                  f"AFTER:  {card['after']}", "```", "", f"Copy/segmentation audit: {card['scribal']}", ""]
    (OUT / "V18_R4_PROCESS_GRAPHS.md").write_text("\n".join(graph) + "\n", encoding="utf-8")

    passage = ["# V18 R4 — complete affected articles and records", "",
               "All five affected pages are rewritten below. No target is left neutral or untranslated. Line ends are physical reflow unless a close card explicitly ends a substep.", ""]
    for page in AFFECTED_PAGES:
        passage += [f"## {page}", ""]
        records: dict[str, list[tuple[str, list[dict[str, str]]]]] = defaultdict(list)
        for locus, line in page_lines[page]:
            records[line[0]["record"]].append((locus, line))
        for record in sorted(records, key=int):
            passage += [f"### Record {record}", ""]
            for locus, line in records[record]:
                surface = " ".join(x["surface"] for x in line)
                gloss = "; ".join(selected_map.get(x["exact_tuple_id"], x["default_English"]) for x in line)
                passage += [f"- `{locus}` — `{surface}`", f"  - {gloss}", ""]
    (OUT / "V18_R4_COMPLETE_AFFECTED_PASSAGES.md").write_text("\n".join(passage) + "\n", encoding="utf-8")

    report = ["# Candidate V18 R4 — chancery corrector's six-card reconstruction", "",
              "Date: 2026-08-21", "",
              "Status: concrete ten-page workshop expansion; not deciphered plaintext.", "",
              "## Decision", "",
              "The strongest copying-room deck is:", ""]
    for card in CARDS.values():
        report.append(f"- **{card['name']}**: {card['selected']} (confidence {card['confidence']})")
    report += ["", "Together these six cards turn the disputed passages into a teachable wet-work sequence:", "", "```text",
               "top up with warmed water",
               "-> wash the vessel/route through once",
               "-> set the prepared liquor aside",
               "-> take the next amount from the same batch",
               "-> drain the whole run into the lower receiver",
               "-> in Herbal prose, then take/use the following named part or ingredient",
               "```", "", "## Why these choices beat the rivals", "",
               "- OKEEY is material replenishment, not another heat or stir command. Its placement after KEEP WARM and before strain/rinse/application is especially useful.",
               "- LCHEDY is whole-run drainage. OPEN UPPER CHANNEL, CLOSE LOWER OUTLET, LOWER BASIN and drain-then-refill contexts make a lower receiver operational rather than decorative.",
               "- DCHEDY is a one-pass vessel/route wash. This explains three line-entry singleton fields and the post-channel copy without duplicating the explicit cloth-straining card.",
               "- OLCHEDY reserves the prepared liquor. A narrower clear-upper-liquor reading is attractive once but requires unmarked settling in two of three copies.",
               "- CHAR preserves same-source identity. The `OKAIN CHAR OKAIN` sequence is naturally 'add one measure; from the same batch add one measure'.",
               "- CHO/SHO is an imperative continuation governing the following plant part or ingredient. 'Flowering tops' is incompatible with lower root, wine, dried leaf and honey contexts.",
               "", "## c. 1420 scribal plausibility", "",
               "The local CoReMA controls contain the same mundane process repertoire: take/put, mix, pour, let stand, press or strain away liquid, move material between vessels, and resume with 'then take'. One Latin recipe explicitly orders a herb to stand for a day, then presses off the vinegar; German recipes strain through cloth or sieve and pour the product onward. This supports the workflow vocabulary without mapping any Voynich spelling to a historical word.",
               "", "The deck is easy to teach as six whole exemplars. A learner copies a closed action card for WASH, RESERVE or DRAIN, an open relation card for SAME-BATCH, and a forward-taking card before the next Herbal operand. Wrapper variation is copied from line/register exemplars and does not change the source action.",
               "", "## Dittography, abbreviation and segmentation audit", ""]
    for card in CARDS.values():
        report.append(f"- **{card['name']}**: {card['scribal']}")
    report += ["", "No target is explained away as filler. There are no adjacent duplicate target cards. The closure-heavy cards occur at varying physical positions, so closure is part of the learned action card rather than evidence that the entire card means only END.",
               "", "## Independence disclosure", "",
               "A broad local comparator search made after the preliminary R4 choices accidentally printed a few snippets from a concurrently created V18 R3 builder. Those snippets were not used to change the R4 deck. Any later verbal agreement with R3 must nevertheless be treated as non-independent; the present report remains useful for its own full-context reconstructions and contrary OLCHEDY choice.",
               "", "## Artifacts", "",
               "- `V18_R4_SIX_CARD_DECISIONS.tsv` — all three frozen rivals, scores and silent-repair counts.",
               "- `V18_R4_31_OCCURRENCE_RECONSTRUCTIONS.tsv` — complete field, preceding/target/following line, three inserted rival paths and selected rewrite for all 31 events.",
               "- `V18_R4_PROCESS_GRAPHS.md` — explicit before/card/after graph for each target.",
               "- `V18_R4_COMPLETE_AFFECTED_PASSAGES.md` — complete affected articles/records on five pages.",
               "", "## Seal", "",
               "Only guarded f84-free GDT327/source rows and frozen V17 products were read. f84 and f84r remained sealed."]
    (OUT / "CANDIDATE_V18_R4_CHANCERY_CORRECTOR.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print("cards=6 occurrences=31 affected_pages=5 guarded_prose=381")
    print("f84_opened=false f84r_opened=false")


if __name__ == "__main__":
    main()
