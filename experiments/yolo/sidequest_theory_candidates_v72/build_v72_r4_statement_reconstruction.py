#!/usr/bin/env python3
"""Build R4's complete V72 statement reconstruction."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
V69 = REPO / "experiments/yolo/sidequest_theory_candidates_v69"
V71 = REPO / "experiments/yolo/sidequest_theory_candidates_v71"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def clean_source(text: str) -> str:
    text = re.sub(r"\[EXEMPLAR:[^:]+:", "", text)
    text = text.replace("]", "")
    replacements = {
        "Teufelsabbisses": "abgebildeten unbekannten Pflanze",
        "Drüsiges Feuchtlandmaterial": "Material der abgebildeten unbekannten Pflanze",
        "Magenschmerz": "der im Exemplar bezeichneten Beschwerde",
        "wunde Stelle": "bezeichnete äußere Stelle",
        "geschwollene Stelle": "bezeichnete äußere Stelle",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def main() -> None:
    statements = read(V69 / "V69_R4_FINAL_116_STATEMENT_EDITION.tsv")
    fields = {r["field_id"]: r for r in read(V69 / "V69_R4_FINAL_135_FIELD_EDITION.tsv")}
    owners = {r["unit_id"]: r for r in read(V71 / "V71_SELECTED_OWNER_LEDGER.tsv") if r["unit_kind"] == "PROSE_FIELD"}
    out = []
    for row in statements:
        fids = row["constituent_fields"].split("|")
        o = [owners[f] for f in fids]
        owner_ids = []
        for item in o:
            if item["selected_visible_owner"] not in owner_ids:
                owner_ids.append(item["selected_visible_owner"])
        statuses = [item["owner_status"] for item in o]
        loci = list(dict.fromkeys(fields[f]["locus"] for f in fids))
        source = clean_source(row["iatromedical_statement_text"])
        if row["record_unit_id"].startswith("B"):
            source = "Nur an der lokalen Bildstation: " + source
        else:
            source = "Von der abgebildeten unbekannten Pflanze: " + source
        repair = 1
        reasons = []
        if "UNRESOLVED" in statuses:
            repair = 4
            reasons.append("owner unresolved and source action must come from exemplar")
        elif "PAGE_OWNER_ONLY" in statuses:
            repair = max(repair, 2)
            reasons.append("only page/article owner visible")
        elif "INHERITED_VISIBLE" in statuses:
            reasons.append("owner inherited within record or station")
        if any(word in source.lower() for word in ["wasser", "warm", "flüss", "wein", "beschwerde", "stelle"]):
            repair = max(repair, 3)
            reasons.append("substance, condition, or use is unpictured exemplar content")
        if len(owner_ids) > 1:
            repair = max(repair, 2)
            reasons.append("statement crosses an owner transition")
        literal = (
            f"OWNER={' + '.join(owner_ids)} ; TEMPLATE={row['primary_template']} ; "
            f"LICENSED={row['licensed_primitive_sequence'] or 'NONE'} ; "
            "all remaining nouns/actions are exact exemplar content"
        )
        out.append({
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "constituent_fields": row["constituent_fields"],
            "event_count": row["event_count"],
            "event_serials": row["event_serials"],
            "owner_ids": "|".join(owner_ids),
            "owner_statuses": "|".join(statuses),
            "owner_transition": "SINGLE_OWNER" if len(owner_ids) == 1 else "LOCAL_OWNER_CHANGE",
            "literal_owner_card_exemplar_layer": literal,
            "concrete_source_class_paraphrase": source,
            "strongest_concrete_rival": clean_source(row["practical_statement_text"]),
            "repair_cost_0_4": str(repair),
            "repair_reason": "; ".join(reasons) or "direct local owner and no extra repair",
            "physical_locus_status": "CROSSES_PHYSICAL_LOCI" if len(loci) > 1 else "WITHIN_ONE_PHYSICAL_LOCUS",
            "loci": "|".join(loci),
            "chief_contradiction": row["strongest_practical_contradiction"],
            "semantic_ceiling": "CONCRETE_CREATIVE_SOURCE_PARAPHRASE_NOT_PLAINTEXT",
        })

    cols = list(out[0])
    with (HERE / "V72_R4_116_STATEMENTS.tsv").open("w", encoding="utf-8", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(out)

    by_record = defaultdict(list)
    for row in out: by_record[row["record_unit_id"]].append(row)
    summary = []
    for record, rs in by_record.items():
        summary.append({
            "record": record,
            "page": rs[0]["page"],
            "statements": str(len(rs)),
            "events": str(sum(int(r["event_count"]) for r in rs)),
            "owner_ids": str(len(set(x for r in rs for x in r["owner_ids"].split("|")))),
            "max_repair_cost": str(max(int(r["repair_cost_0_4"]) for r in rs)),
            "record_reading": " ".join(r["concrete_source_class_paraphrase"] for r in rs),
        })
    with (HERE / "V72_R4_ELEVEN_RECORD_WALKTHROUGH.tsv").open("w", encoding="utf-8", newline="") as handle:
        w=csv.DictWriter(handle,fieldnames=list(summary[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(summary)
    result = {
        "schema": "V72_R4_STATEMENT_VALIDATION_V1",
        "status": "PASS" if len(out) == 116 and sum(int(r["event_count"]) for r in out) == 381 and len(summary) == 11 else "FAIL",
        "counts": {"statements": len(out), "events": sum(int(r["event_count"]) for r in out), "records": len(summary), "repair_costs": dict(Counter(r["repair_cost_0_4"] for r in out))},
        "sealed_pages_opened": [],
    }
    (HERE / "V72_R4_VALIDATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if result["status"] != "PASS": raise SystemExit(1)


if __name__ == "__main__": main()
