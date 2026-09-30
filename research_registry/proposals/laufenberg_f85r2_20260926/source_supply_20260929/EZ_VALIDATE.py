#!/usr/bin/env python3
"""Replay literal conservation and two fixed diagnostics; no meaning validator."""
import csv
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent

def read_json(name):
    return json.loads((P / name).read_text())

def read_tsv(name):
    with (P / name).open(newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    author = read_json("EZ_AUTHOR.json")
    old = read_json("AS_AUTHOR.json")
    checks = []
    def check(name, condition):
        checks.append({"check": name, "passed": bool(condition)})
    check("frozen_author", sha(P / "EZ_AUTHOR.json") == "95921b51f7dbe289f5a3f676d9c21728c4072a75fb09032e61c6217e85210c83")
    check("old_AS_bytes", sha(P / "AS_AUTHOR.json") == author["old_AS_byte_sha256"])
    check("old21values", author["old_AS_lexicon"] == old["lexicon"])
    check("old9rules", author["old_AS_rules"] == old["rules"])
    for path, expected in author["input_hashes"].items():
        check("input:" + path, sha(Path(path)) == expected)
    dictionary = {x["form"]: x for x in author["old_AS_lexicon"] + author["new_lexicon"]}
    check("75new_values_no_overlap", len(author["new_lexicon"]) == 75 and len(dictionary) == 96)
    raw = read_tsv("EZ_F26V_WHOLE_RAW.tsv")
    source_fields = list(raw[0])
    zl = [x for x in raw if x["edition"] == "ZL3b"]
    alt = [x for x in raw if x["edition"] != "ZL3b"]
    check("all275raw_groups", len(raw) == 275 and len(zl) == 93 and len(alt) == 182)
    for x, y in zip(zl, author["position_table"]):
        check("native:" + x["source_group_id"], all(str(y[k]) == x[k] for k in source_fields))
        meaning = dictionary[x["ivtff_group_raw"]]
        check("value_type:" + x["source_group_id"], y["value"] == meaning["value"] and y["type"] == meaning["type"])
    check("all182alternate_positions", len(author["alternate_reader_groups"]) == 182)
    check("positions1to93", [x["paragraph_position"] for x in author["position_table"]] == list(range(1,94)))
    check("78wholes", len({x["ivtff_group_raw"] for x in zl}) == 78)
    unknown = {}
    for x, y in zip(alt, author["alternate_reader_groups"]):
        check("alternate_native:" + x["source_group_id"], all(str(y[k]) == x[k] for k in source_fields))
        meaning = dictionary.get(x["ivtff_group_raw"])
        if meaning is None:
            unknown[x["edition"]] = unknown.get(x["edition"], 0) + 1
            check("unknown_retained:" + x["source_group_id"], y["value"] is None)
        else:
            check("alternate_value:" + x["source_group_id"], y["value"] == meaning["value"] and y["type"] == meaning["type"])
    check("unknown10each", unknown == {"IT2a": 10, "RF1b": 10})
    line4 = [x for x in author["position_table"] if x["locus"] == "f26v.4"]
    triple = line4[1:4]
    check("observed_modifier_triple", [x["value"] for x in triple] == ["APPLICATION", "GENTLE", "PRESSURE"])
    e3 = author["new_rules"][2]
    english = author["line_readings_in_literal_order"][3]["reading"]
    mismatch = "postmodified nominal cells" in e3 and "gentle pressure" in english.lower()
    check("registered_rendering_mismatch_detected", mismatch)
    outside = read_tsv("EZ_F39V_OUTSIDE_RAW.tsv")
    check("outside_only_complete1to6", {x["locus"] for x in outside} == {"f39v." + str(i) for i in range(1,7)})
    overlay = []
    for x in outside:
        meaning = dictionary.get(x["ivtff_group_raw"])
        overlay.append(dict(x, value=meaning["value"] if meaning else "UNKNOWN", type=meaning["type"] if meaning else "UNKNOWN", argument_scope="EZ new rules scoped to f26v; no f39v graph asserted"))
    with (P / "EZ_F39V_FIXED_OVERLAY.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=source_fields + ["value","type","argument_scope"], delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(overlay)
    contexts = read_tsv("AS_PARAGRAPH.tsv") + raw + outside
    obligations = []
    for locus in ["f22r.4", "f26v.5", "f39v.1", "f39v.5"]:
        for edition in ["ZL3b","IT2a","RF1b"]:
            line = [x for x in contexts if x["edition"] == edition and x["locus"] == locus]
            matches = [x for x in line if x["ivtff_group_raw"] in {"ofchy","opchy"}]
            check("all4loci_reader:" + edition + locus, len(matches) == 1)
            x = matches[0]
            ix = line.index(x)
            obligations.append({"edition":edition,"locus":locus,"source_group_id":x["source_group_id"],"whole":x["ivtff_group_raw"],"previous":line[ix-1]["ivtff_group_raw"] if ix else "","next":line[ix+1]["ivtff_group_raw"] if ix+1 < len(line) else "LINE_END_NOT_SENTENCE_END","fixed_value":"WORMLIKE_CREATURES" if x["ivtff_group_raw"] == "ofchy" else "UNKNOWN_NO_ALIAS","role":"ASstudy_material_W1" if locus == "f22r.4" else ("EZaffected_W2_paid_E5" if edition == "ZL3b" else "POSSIBLE_affected_slot_juice_and_case_unbound" if edition == "IT2a" else "MATCHING_CORE_WORDS_graph_not_asserted") if locus == "f26v.5" else "UNBOUND","old_source_debt":"AS pouch-versus-creature suspension bridge unpaid" if locus == "f22r.4" else ""})
    with (P / "EZ_OCCURRENCE_CONSEQUENCES.tsv").open("w",newline="") as f:
        w = csv.DictWriter(f,fieldnames=list(obligations[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(obligations)
    failures = [x for x in checks if not x["passed"]]
    result = {"status":"CONSERVATION_PASS_WITH_EXPECTED_RENDERING_CONFLICT" if not failures else "CONSERVATION_FAIL", "checks":len(checks),"failures":failures,"modifier_diagnostic":{"literal_order":"APPLICATION GENTLE PRESSURE","rule":"E3postmodified nominal cells","derived_attachment":"GENTLE->APPLICATION","rendered_attachment":"GENTLE->PRESSURE","mismatch":mismatch,"no_repair":True},"counts":{"ZL":len(zl),"IT":sum(x["edition"]=="IT2a" for x in alt),"RF":sum(x["edition"]=="RF1b" for x in alt),"f39v_rows":len(outside),"all_occurrence_obligations":len(obligations),"alternate_unknowns":unknown},"meaning_validation":False,"confirmed_words":0,"independent_confirmation_leaves":0,"semantic_whole_account":"PARTIAL; no semantic PASS"}
    (P / "EZ_ACCOUNTING_VALIDATION.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
    if failures: raise SystemExit(1)

if __name__ == "__main__": main()
