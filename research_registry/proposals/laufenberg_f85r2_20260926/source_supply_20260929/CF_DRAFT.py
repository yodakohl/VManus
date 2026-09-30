#!/usr/bin/env python3
"""Four explicit unconfirmed whole-form drafts; preserve every unknown group."""
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = json.loads((BASE / "CF_FULL_LEAVES.json").read_text())
ce = json.loads((BASE / "CE_RESULT.json").read_text())
inherited = dict(ce["whole_form_assumptions"])
models = []
for bearer, bearer_meaning in (("leaf", "Blattgut"), ("herb", "oberirdisches Krautgut")):
    for field, field_meaning in (("A_natural", "von Natur aus kühl; unbestimmte Eigenschaftsstufe Q"),
                                 ("B_amount", "unbestimmte Materialmenge Q")):
        model_id = f"{field}_{bearer}"
        meanings = {**inherited, "cthy": bearer_meaning, "otaiin": field_meaning}
        positions = [
            {"source_group_id": row["source_group_id"], "raw": row["ivtff_group_raw"],
             "hypothesis": meanings.get(row["ivtff_group_raw"])}
            for line in source["lines"] for row in line["groups"]
        ]
        models.append({"id": model_id, "whole_form_assumptions": meanings,
            "cthy_assumption": bearer_meaning, "otaiin_assumption": field_meaning,
            "inherited_from_CE": "Five M2 whole-form C0s, unchanged; M4 remains a separate unresolved rival",
            "positions": positions,
            "assumed_positions": sum(p["hypothesis"] is not None for p in positions),
            "unread_positions": sum(p["hypothesis"] is None for p in positions),
            "meaning_status": "UNCONFIRMED_EXPLORATORY_CONSTRUCTION"})
result = {"stage": "exploratory whole-leaf content authoring; not a semantic test PASS",
    "models": models, "total_raw_groups": len(source["rows"]),
    "physical_leaves": ["f9", "f50"], "independent_meaning_confirmation_leaves": 0,
    "confirmed_words": 0, "legacy_meanings_or_decisions_changed": False,
    "raw_pair_contacts": 10, "contact_physical_sites": ["f9r.3", "f9v.3", "f50v.9"],
    "exact_direct_cthy_oky_contacts": 0,
    "decision": "Leaf/herb and natural-property/amount remain tied; written cthy supplies only an assumed bearer at f9v3. No inferred owner for kaiin at f9v4 or f50 contexts.",
    "global_obligations": "941 exact cthy/otaiin/oky positions retained; only direct fixed-pair contexts and two whole exposed leaves authored, not all meanings verified"}
(BASE / "CF_RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
md = ["# CF — four complete sparse drafts of exposed leaves f9 and f50",
    "All seven whole values are C0 assumptions. Bracketed raw groups remain unread. Semicolons are presentation, not recovered punctuation. CE's five whole assumptions are copied verbatim, not independently validated. No new language, plant identity or word translation is confirmed."]
for model in models:
    md += ["", "## " + model["id"],
        f"cthy: {model['cthy_assumption']}; otaiin: {model['otaiin_assumption']}",
        f"Authored coverage only: {model['assumed_positions']} assumed, {model['unread_positions']} unread."]
    for line in source["lines"]:
        md += ["", f"### {line['edition']} {line['locus']}",
            "; ".join(model["whole_form_assumptions"].get(r["ivtff_group_raw"], "[" + r["ivtff_group_raw"] + "]") for r in line["groups"])]
(BASE / "CF_FULL_SPARSE_DRAFTS.md").write_text("\n".join(md) + "\n")
print(json.dumps({"models": [{"id": m["id"], "assumed": m["assumed_positions"], "unread": m["unread_positions"]} for m in models],
    "counts_by_form": dict(Counter(p["raw"] for p in models[0]["positions"] if p["hypothesis"] is not None))}, indent=2))
