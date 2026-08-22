#!/usr/bin/env python3
"""Build the complete R4 Herbal third edition."""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


REPO=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
V69=REPO/"experiments/yolo/sidequest_theory_candidates_v69"
V71=REPO/"experiments/yolo/sidequest_theory_candidates_v71"
V72=REPO/"experiments/yolo/sidequest_theory_candidates_v72"


def read(p):
    with Path(p).open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))


def clean(s:str)->str:
    s=s.replace("Teufelsabbisses","abgebildeten unbekannten Pflanze")
    s=s.replace("Veilchen","abgebildeten unbekannten Pflanze")
    s=s.replace("Sonnentau","abgebildeten unbekannten Pflanze")
    s=re.sub(r"\[(?:IMAGE|GENRE|REGISTER|EXEMPLAR|CARD|FORMAL|LOCAL):([^\]]+)\]",lambda m:m.group(1).split(":")[-1],s)
    s=s.strip(" .;")
    return " ".join(s.split()) or "kopiere den konkreten Vorgang für diesen Pflanzenartikel aus dem Masterexemplar"


def write(name,rows):
    with (HERE/name).open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)


def main():
    events=[r for r in read(V69/"V69_R4_FINAL_381_PROSE_EVENT_INTERLINEAR.tsv") if r["record_unit_id"].startswith("H")]
    fields=[r for r in read(V69/"V69_R4_FINAL_135_FIELD_EDITION.tsv") if r["record_unit_id"].startswith("H")]
    owners={r["unit_id"]:r for r in read(V71/"V71_SELECTED_OWNER_LEDGER.tsv") if r["unit_kind"]=="PROSE_FIELD"}
    statements=[r for r in read(V72/"V72_SELECTED_116_STATEMENTS.tsv") if r["record_unit_id"].startswith("H")]
    out=[]
    for r in events:
        owner=owners[r["field_id"]]
        known=[]
        if r["selected_exact_mnemonic"]!="UNKNOWN":known.append("CARD:"+r["selected_exact_mnemonic"])
        if r["strict_formal_prompt"]!="NONE":known.append("FORMAL:"+r["strict_formal_prompt"])
        layer="KNOWN_CARD_OR_FORMAL_PLUS_CONTEXT" if known else "TYPED_MASTER_EXEMPLAR_CONTENT"
        default=clean(r["iatromedical_source_segment"])
        if default.startswith("unterer Wurzelstock") or default.startswith("von diesem"):
            default=default.replace("unterer Wurzelstock der abgebildeten unbekannten Pflanze","bezeichneter Anteil der abgebildeten unbekannten Pflanze")
        out.append({
            "event_serial":r["event_serial"],"page":r["page"],"locus":r["locus"],"record_unit_id":r["record_unit_id"],"field_id":r["field_id"],"statement_id":r["statement_id"],
            "joint_tuple_id":r["joint_tuple_id"],"surface_display_only":r["surface_display_only"],"visible_owner":owner["selected_visible_owner"],"owner_status":owner["owner_status"],
            "literal_exact_layer":"|".join(known) or "EXACT_CARD:EXEMPLAR_VALUE_UNKNOWN","source_layer":layer,"concrete_german_default":default,
            "confidence":"MEDIUM" if known else "LOW","strongest_alternative":clean(r["practical_source_segment"]),
            "contradiction":"plant species, selected part, medium, operation and use are not fixed by the image or exact card",
            "semantic_ceiling":"CREATIVE_CONTEXT_DEFAULT_NOT_WORD_OR_PLAINTEXT",
        })
    write("V73_R4_100_EVENT_INTERLINEAR.tsv",out)
    evby=defaultdict(list)
    for r in out:evby[r["field_id"]].append(r)
    fs=[]
    for f in fields:
        es=evby[f["field_id"]]
        fs.append({"field_id":f["field_id"],"record_unit_id":f["record_unit_id"],"page":f["page"],"locus":f["locus"],"statement_id":f["statement_id"],"event_count":str(len(es)),"visible_owner":owners[f["field_id"]]["selected_visible_owner"],"complete_field_reading":"; ".join(e["concrete_german_default"] for e in es),"strongest_rival":"; ".join(e["strongest_alternative"] for e in es),"status":"COMPLETE_CREATIVE"})
    write("V73_R4_20_FIELD_EDITION.tsv",fs)
    byrec=defaultdict(list)
    for s in statements:byrec[s["record_unit_id"]].append(s)
    lines=["# V73 R4 — fünf vollständige Herbal-Artikel","","> Jede Lesung ist konkrete Exemplarfüllung, keine Entzifferung.",""]
    for rec,rs in byrec.items():
        lines += [f"## {rec} / {rs[0]['page']}","", " ".join(r["selected_concrete_paraphrase"] for r in rs),"", "**Stärkster Rivale:** "+" ".join(r["strongest_rival"] for r in rs),""]
    (HERE/"V73_R4_FIVE_RECORD_ARTICLES.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    result={"schema":"V73_R4_HERBAL_VALIDATION_V1","status":"PASS" if len(out)==100 and len(fs)==20 and len(statements)==19 and len(byrec)==5 else "FAIL","counts":{"events":len(out),"fields":len(fs),"statements":len(statements),"records":len(byrec),"source_layers":dict(Counter(r["source_layer"] for r in out))},"sealed_pages_opened":[]}
    (HERE/"V73_R4_VALIDATION.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if result["status"]!="PASS":raise SystemExit(1)


if __name__=="__main__":main()
