#!/usr/bin/env python3
"""Run the unchanged GDT170/172 blind instrument on anonymous B2."""
from __future__ import annotations
import csv,gzip,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from run_gdt170_blind_instrument import annotation_scores,compatibility,discover,greedy_alignment,held_gain,host_signature,parse_token,record_metrics,short_and_substitution

R=Path(__file__).resolve().parent
SOURCE=R/"gdt173_b2_observation_corpus.json.gz";FREEZE=R/"gdt173_b2_source_freeze.json";DESIGN=R/"gdt173_blind_design.json"
METHOD=R/"GDT173_HUMAN_GROWN_DISTRIBUTED_CONTROL_METHOD.md";CORE=R/"run_gdt170_blind_instrument.py"
PARSES=R/"gdt173_blind_parses.json.gz";OPS=R/"gdt173_blind_operations.tsv";DIAG=R/"gdt173_blind_diagnostics.tsv";RESULT=R/"gdt173_blind_result.json"
MODES=("SURFACE_ONLY","VMANUS_ANNOTATION_ASSISTED")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def write(path,rows):
    fields=[]
    for row in rows:
        for f in row:
            if f not in fields:fields.append(f)
    with path.open("w",encoding="utf8",newline="") as h:
        w=csv.DictWriter(h,fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows([{f:r.get(f,"NA") for f in fields} for r in rows])
def write_gzip(path,payload):
    raw=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
    with path.open("wb") as target:
        with gzip.GzipFile(fileobj=target,mode="wb",mtime=0) as h:h.write(raw)

def main():
    design=json.loads(DESIGN.read_text());freeze=json.loads(FREEZE.read_text())
    assert design["status"]=="FROZEN_UNCHANGED_GDT172_INSTRUMENT_BEFORE_B2_BLIND_PARSE" and design["core_runner_sha256"]==sha(CORE)
    with gzip.open(SOURCE,"rt",encoding="utf8") as h:payload=json.load(h)
    assert payload["schema"]=="GDT173_B2_STRICT_OBSERVATION_CORPUS_V1";rows=payload["rows"]
    assert len(rows)==15214 and {x["world_view"] for x in rows}=={"CONTROL_R"}
    left,right,stats,envelope,counts=discover(rows);ann=annotation_scores(rows,left,right)
    selected={("LEFT",x) for x in left}|{("RIGHT",x) for x in right};operation_rows=[]
    for item in stats:
        if (item["side"],item["operation"]) not in selected:continue
        operation_rows.append({"world_view":"CONTROL_R","scope":"ALL_PARTITIONED_REGISTERS","side":item["side"],"operation":item["operation"],"selected_rank":(left.index(item["operation"])+1) if item["side"]=="LEFT" else (right.index(item["operation"])+1),"distinct_hosts":item["distinct_hosts"],"exact_pair_types":item["exact_pair_types"],"synthetic_folios":item["synthetic_folios"],"transformed_occurrences":item["transformed_occurrences"],"annotation_rank_adjustment":ann.get((item["side"],item["operation"]),0.)})
    parse_rows=[];diagnostics=[];parsed_by={}
    for mode in MODES:
        cache={token:parse_token(token,counts,left,right,envelope,mode,ann) for token in counts};parsed=[]
        for row in rows:
            item={"observation_id":row["observation_id"],"world_view":"CONTROL_R","witness_renderer":row["witness_renderer"],"register":row["register"],"hand":row["hand"],"folio_id":row["folio_id"],"layout_folio_ordinal":row["layout_folio_ordinal"],"physical_line_id":row["physical_line_id"],"line_ordinal_on_folio":row["line_ordinal_on_folio"],"group_index":row["group_index"],"group_count":row["group_count"],"paragraph_start":row["paragraph_start"],"paragraph_end":row["paragraph_end"],"right_separator":row["right_separator"],"surface_group":row["surface_group"],"parser_level":mode,**cache[row["surface_group"]]}
            parsed.append(item);parse_rows.append(item)
        parsed_by[mode]=parsed;rec=record_metrics(parsed);comp=compatibility(set(counts),left,right,"CONTROL_R"+mode);short,same,external=short_and_substitution(parsed);base={"world_view":"CONTROL_R","scope":"ALL_PARTITIONED_REGISTERS","parser_level":mode}
        diagnostics += [{**base,"diagnostic":"RECORD_ARCHITECTURE",**rec},{**base,"diagnostic":"OPERATION_COMPATIBILITY",**comp},{**base,"diagnostic":"SHORT_HOST_STRUCTURE",**short},{**base,"diagnostic":"SAME_GROUP_SUBSTITUTION",**same},{**base,"diagnostic":"EXTERNAL_CONTEXT_SUBSTITUTION",**external},{**base,"diagnostic":"HELD_CONTEXT",**held_gain(parsed,"NEXT_HOST")},{**base,"diagnostic":"HELD_CONTEXT",**held_gain(parsed,"WHOLE_LINE")}]
    for mode in MODES:
        values=parsed_by[mode];byreg=defaultdict(list)
        for row in values:byreg[row["register"]].append(row)
        regs=sorted(byreg)
        for i,leftreg in enumerate(regs):
            for rightreg in regs[i+1:]:
                ar,br=byreg[leftreg],byreg[rightreg];ap=[x for x,_ in Counter(x["inferred_host"] for x in ar).most_common(100)];bp=[x for x,_ in Counter(x["inferred_host"] for x in br).most_common(100)]
                diagnostics.append({"world_view":"CONTROL_R","scope":"REGISTER_PAIR","parser_level":mode,"diagnostic":"REGISTER_GEOMETRY_ALIGNMENT","left_register":leftreg,"right_register":rightreg,"panel_hosts":min(len(ap),len(bp)),"greedy_matched_mean_cosine":greedy_alignment(host_signature(ar,ap),host_signature(br,bp))})
    parse_rows.sort(key=lambda x:(x["parser_level"],int(x["layout_folio_ordinal"]),int(x["line_ordinal_on_folio"]),int(x["group_index"])))
    write_gzip(PARSES,{"schema":"GDT173_BLIND_PARSES_V1","rows":parse_rows});write(OPS,operation_rows);write(DIAG,diagnostics)
    summary={}
    for mode,values in parsed_by.items():summary[mode]={"inferred_host_types":len({x["inferred_host"] for x in values}),"mean_operation_count":sum(int(x["operation_count"]) for x in values)/len(values),"surface_exact_host_rate":sum(x["inferred_host"]==x["surface_group"] for x in values)/len(values)}
    result={"schema":"GDT173_BLIND_INSTRUMENT_RESULT_V1","status":"GDT173_B2_BLIND_OUTPUTS_FROZEN_BEFORE_ORACLE_EVALUATION","counts":{"observation_rows":len(rows),"parse_rows":len(parse_rows),"operation_rows":len(operation_rows),"diagnostic_rows":len(diagnostics),"anonymous_worlds":1,"content_folios":freeze["counts"]["content_folios"]},"summary":summary,
            "inputs":{p.name:sha(p) for p in (SOURCE,FREEZE,DESIGN,CORE)},"outputs":{PARSES.name:sha(PARSES),OPS.name:sha(OPS),DIAG.name:sha(DIAG)},"commitments":{"parse_content_sha256":csha(parse_rows),"diagnostic_content_sha256":csha(diagnostics)},"implementation":{Path(__file__).name:sha(Path(__file__))},"documents":{METHOD.name:sha(METHOD)},
            "blind_firewall":{"read_files":[SOURCE.name,FREEZE.name,DESIGN.name,CORE.name,METHOD.name],"forbidden_inputs_opened":False,"oracle_fields_used":False,"voynich_inputs":0,"f84_access":False},"claim_ceiling":"Blind synthetic B2 outputs only; no Voynich architecture word code value language meaning plaintext or translation."}
    result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":result["status"],**result["counts"]},sort_keys=True))
if __name__=="__main__":main()
