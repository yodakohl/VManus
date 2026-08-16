#!/usr/bin/env python3
"""Independent table/layout/reversibility validator for GDT173 B2."""
from __future__ import annotations
import ast, csv, gzip, hashlib, json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parent
PARENT_OBS = R / "gdt172_observation_corpus.json.gz"; PARENT_ORACLE = R / "gdt172_sealed_oracle.json.gz"
PARENT_LOOKUP = R / "gdt171_sealed_lexical_lookup.tsv"; LOOKUP = R / "gdt173_b2_lookup.tsv"
FAMILIES = R / "gdt173_b2_family_manifest.tsv"; OBS = R / "gdt173_b2_observation_corpus.json.gz"
ORACLE = R / "gdt173_b2_sealed_oracle.json.gz"; FREEZE = R / "gdt173_b2_source_freeze.json"
AUTHOR = R / "author_gdt173_b2_lookup.py"; BUILDER = R / "build_gdt173_b2_control.py"
OUT = R / "gdt173_b2_source_validation.json"

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def csha(x): return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def load(p):
    with gzip.open(p, "rt", encoding="utf8") as h: return json.load(h)
def read(p):
    with p.open(encoding="utf8", newline="") as h: return list(csv.DictReader(h, delimiter="\t"))
def check(v,label,checks):
    if not v: raise AssertionError(label)
    checks.append(label)
def val(x): return "" if x == "NONE" else x

def main():
    checks=[]; freeze=json.loads(FREEZE.read_text())
    parent_obs=[x for x in load(PARENT_OBS)["rows"] if x["world_view"]=="CONTROL_P"]
    parent_truth={x["observation_id"]:x for x in load(PARENT_ORACLE)["rows"]}
    obs_payload,oracle_payload=load(OBS),load(ORACLE);obs,oracle=obs_payload["rows"],oracle_payload["rows"]
    table,parent_lookup,families=read(LOOKUP),read(PARENT_LOOKUP),read(FAMILIES)
    check(freeze["status"]=="FROZEN_B2_TABLE_RENDERER_AND_LAYOUT_BEFORE_BLIND_SCORE","status",checks)
    check(obs_payload["schema"]=="GDT173_B2_STRICT_OBSERVATION_CORPUS_V1" and oracle_payload["schema"]=="GDT173_B2_SEALED_ORACLE_V1","schemas",checks)
    check(len(parent_obs)==len(obs)==len(oracle)==15214 and len(table)==len(parent_lookup)==384 and len(families)==32,"counts",checks)
    check([(x["lexical_id"],x["source_form"],x["source_frequency"]) for x in table]==[(x["lexical_id"],x["source_form"],x["source_frequency"]) for x in parent_lookup],"lexical_universe_exact",checks)
    check([int(x["lexical_ids"]) for x in families]==[len(x["variant_sequence"]) for x in families] and sum(int(x["lexical_ids"]) for x in families)==384,"family_sizes_exact",checks)
    check((min(int(x["lexical_ids"]) for x in families),max(int(x["lexical_ids"]) for x in families))==(7,18),"family_size_range",checks)
    check(len({x["family_id"] for x in table})==32 and len({x["variant_code"] for x in table})==24 and sum(x["exception_note"]!="NONE" for x in table)==11,"irregular_table_census",checks)
    check(sum(x["s2_rule"]!="{}" for x in families)==6 and len({x["b2_host"] for x in table})==54,"host_render_census",checks)
    def key(x,hand): return val(x["b2_left"]),x["b2_host"] if hand=="S1" else x["s2_host"],val(x["b2_right"]),val(x["b2_field"]),val(x["b2_lexical_closure"])
    check(len({key(x,"S1") for x in table})==len(table) and len({key(x,"S2") for x in table})==len(table),"handwise_lookup_reversible",checks)
    tree=ast.parse(AUTHOR.read_text()); forbidden_nodes=(ast.Mod,)
    check(not any(isinstance(n,forbidden_nodes) for n in ast.walk(tree)),"no_modulo_assignment",checks)
    imports={n.names[0].name for n in ast.walk(tree) if isinstance(n,ast.Import)}|{n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)}
    check(not {"random","hashlib","numpy","scipy"}.intersection(imports),"no_random_hash_optimizer_import",checks)
    check(not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in {"product","permutations","combinations"} for n in ast.walk(tree)),"no_cartesian_enumeration",checks)

    omap={x["observation_id"]:x for x in oracle};tmap={x["source_form"]:x for x in table}
    check(len(omap)==len(oracle) and set(omap)=={x["observation_id"] for x in obs},"join_keys",checks)
    frequent=literal=0
    for old,new in zip(parent_obs,obs):
        old_truth=parent_truth[old["observation_id"]];truth=omap[new["observation_id"]]
        expected_id="R"+old["observation_id"][1:]
        check(new["observation_id"]==expected_id and truth["observation_id"]==expected_id,"observation_id_derivation",checks)
        ignored={"observation_id","world_view","folio_id","physical_line_id","surface_group"}
        check({k:v for k,v in new.items() if k not in ignored}=={k:v for k,v in old.items() if k not in ignored},"layout_metadata_exact",checks)
        check(new["folio_id"]==old["folio_id"].replace("CONTROL_P:","CONTROL_R:",1) and new["physical_line_id"]==old["physical_line_id"].replace("CONTROL_P:","CONTROL_R:",1),"anonymous_world_locator_only",checks)
        check(truth["source_form"]==old_truth["source_form"] and truth["source_unit_full"]==old_truth["source_unit_full"] and truth["true_source_occurrence_index"]==old_truth["true_source_occurrence_index"],"source_identity_order_exact",checks)
        table_row=tmap.get(truth["source_form"])
        if truth["lexical_status"]=="FREQUENT_LEXICAL_ID":
            frequent+=1;check(table_row is not None and truth["lexical_id"]==table_row["lexical_id"],"frequent_table_join",checks)
            expected_host=table_row["b2_host"] if new["hand"]=="S1" else table_row["s2_host"]
            check(truth["rendered_host"]==expected_host and truth["canonical_host"]==table_row["b2_host"],"frequent_host_render",checks)
            check((truth["true_lexical_left"],truth["true_lexical_right"],truth["true_field_marker"],truth["true_b2_lexical_closure"])==(val(table_row["b2_left"]),val(table_row["b2_right"]),val(table_row["b2_field"]),val(table_row["b2_lexical_closure"])),"frequent_tuple_exact",checks)
        else:
            literal+=1;check(table_row is None and truth["true_literal_escape"]=="w" and truth["canonical_host"]==truth["rendered_host"]==truth["source_form"],"literal_unchanged_source_form",checks)
            check(not any((truth["true_lexical_left"],truth["true_lexical_right"],truth["true_field_marker"],truth["true_b2_lexical_closure"])),"literal_no_b2_fields",checks)
        expected=truth["true_record_operator"]+truth["true_line_frame"]+truth["true_literal_escape"]+truth["true_lexical_left"]+truth["rendered_host"]+truth["true_lexical_right"]+truth["true_field_marker"]+truth["true_b2_lexical_closure"]+truth["true_positional_right"]+truth["true_closure"]
        check(new["surface_group"]==expected,"surface_reconstruction",checks)
    checks=list(dict.fromkeys(checks));check((frequent,literal)==(5711,9503),"frequent_literal_counts",checks)
    check(len({x["physical_line_id"] for x in obs})==2409 and len({x["layout_folio_ordinal"] for x in obs})==176 and {x["register"] for x in obs}=={"R1","R2","R3","R4"} and {x["hand"] for x in obs}=={"S1","S2"},"layout_census",checks)
    check(csha(obs)==freeze["commitments"]["observation_content_sha256"] and csha(oracle)==freeze["commitments"]["oracle_content_sha256"] and csha(table)==freeze["commitments"]["lookup_content_sha256"] and csha(families)==freeze["commitments"]["family_content_sha256"],"content_hashes",checks)
    check(all(sha(R/k)==v for k,v in freeze["inputs"].items()) and all(sha(R/k)==v for k,v in freeze["outputs"].items()),"artifact_hashes",checks)
    check(sha(AUTHOR)==freeze["implementation"][AUTHOR.name] and sha(BUILDER)==freeze["implementation"][BUILDER.name],"implementation_hashes",checks)
    stored=freeze.pop("freeze_content_sha256");check(csha(freeze)==stored,"freeze_content_hash",checks)
    check(freeze["layout_invariants"]["system_a_regenerated_or_modified"] is False and freeze["layout_invariants"]["factorial_system_b_regenerated_or_modified"] is False,"parent_systems_unchanged",checks)
    check(freeze["voynich_inputs"]==0 and not freeze["f84_access"] and freeze["no_voynich_tuning"],"no_voynich_f84",checks)
    out={"schema":"GDT173_B2_SOURCE_VALIDATION_V1","status":"PASS_INDEPENDENT_B2_TABLE_LAYOUT_AND_REVERSIBILITY_RECONSTRUCTION","checks_passed":len(checks),"checks_failed":0,"checks":checks,"observation_rows":len(obs),"frequent_rows":frequent,"literal_rows":literal,"lookup_rows":len(table),"families":len(families),"result_sha256":sha(FREEZE),"validator_sha256":sha(Path(__file__)),"voynich_inputs":0,"f84_access":False}
    out["validation_content_sha256"]=csha(out);OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(f"PASS {len(checks)}/{len(checks)}")

if __name__=="__main__":main()
