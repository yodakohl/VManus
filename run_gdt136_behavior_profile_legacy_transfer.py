#!/usr/bin/env python3
"""GDT136: frozen behavior-profile cross-panel transfer."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt062_right_family_inventory.tsv"
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
ANN = ROOT / "gdt012_annotated_core_inventory.tsv"
PARSED = ROOT / "gdt059_hpr2_external_inventory.tsv"
TARGETS = ROOT / "gdt109_target_inventory.tsv"
CAPACITY = ROOT / "gdt136_capacity.tsv"
MANIFEST = ROOT / "gdt095_descriptor_token_manifest.tsv"
PREDICTION = ROOT / "gdt136_prediction.json"
METHOD = ROOT / "GDT136_BEHAVIOR_PROFILE_LEGACY_TRANSFER_METHOD.md"
REPORT = ROOT / "GDT136_BEHAVIOR_PROFILE_LEGACY_TRANSFER_REPORT.md"
SCORES = ROOT / "gdt136_representation_scores.tsv"
TOKENS = ROOT / "gdt136_token_scores.tsv"
FOLDS = ROOT / "gdt136_folio_scores.tsv"
NULL = ROOT / "gdt136_null_results.tsv"
COUNTER = ROOT / "gdt136_counterexamples.tsv"
VARIANTS = ROOT / "gdt136_variant_log.tsv"
RESULT = ROOT / "gdt136_result.json"

PREFIXES = ("che", "ch", "sh", "t", "s", "d", "q")
RIGHT = ("aiin", "air", "ain", "ar", "al")
EDITIONS = (("ZL3b", "zl3b_forms"), ("IT2a", "it2a_forms"), ("RF1b", "rf1b_forms"))
REPS = ("BEHAVIOR_SELF_NEIGHBOR_NOPOS", "PAGE_HOST_CHAR3", "RAW_CHAR3")
SCOPES = (
    "AVERAGE_PROFILEABLE_GE1", "AVERAGE_PROFILEABLE_GE2", "AVERAGE_ALL3_GE1",
    "ZL3b_GE1", "IT2a_GE1", "RF1b_GE1",
)
K, SHRINK, WORLDS, SEED = 5, 4.0, 10000, 136001
STOP = set("a an and are as at be been being but by for from has have in into is it its label labels labeled near next no not of on or page panel plant plants row since that the their them there these they this to under used was we were with word words kluge kluges petersen petersens grove groves latham perhaps seems likely associated actually between east west north south left right above below top bottom middle mid height side first second third fourth fifth sixth one two three four five six seven eight nine ten".split())


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields=None):
    fields = fields or list(rows[0])
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def strip_layers(token):
    wrapper, host = "NONE", token
    for prefix in PREFIXES:
        if host.startswith(prefix) and len(host) > len(prefix): wrapper, host = prefix, host[len(prefix):]; break
    dy = int(host.endswith("dy") and len(host) > 2)
    if dy: host = host[:-2]
    return wrapper, host, dy


def preparse(wrapper, host):
    b3 = int(host.endswith("m") and len(host) > 1)
    if b3: host = host[:-1]
    right = "NONE"
    for suffix in RIGHT:
        if host.endswith(suffix) and len(host) > len(suffix): host, right = host[:-len(suffix)], suffix; break
    inner = int(wrapper in {"ch", "che", "sh"} and host.startswith("d") and len(host) > 1)
    if inner: host = host[1:]
    return host, b3, right, inner


def licensed_hosts(prose):
    counts = Counter()
    for row in prose:
        host, _, _, _ = preparse(row["stripped_prefix"], row["residual_host"]); counts[host] += 1
    return {host for host in counts if counts[host] and counts["o" + host] and counts["ot" + host]} | {"ar", "al", "ol"}


def parse_token(token, licensed):
    wrapper, residual, dy = strip_layers(token)
    host, b3, right, inner = preparse(wrapper, residual)
    frame = "NONE"
    if host.startswith("ot") and host[2:] in licensed: host, frame = host[2:], "OT"
    elif host.startswith("o") and host[1:] in licensed: host, frame = host[1:], "O"
    return {"token": token, "page_host": host or "EMPTY", "wrapper": wrapper, "inner": inner,
            "frame": frame, "right": right, "dy": dy, "b3": b3}


def add_char3(counter, value):
    padded = "^" + value + "$"
    for index in range(max(1, len(padded) - 2)): counter[padded[index:index + 3]] += 1.0


def average(counters):
    output = Counter()
    for counter in counters:
        for key, value in counter.items(): output[key] += value / len(counters)
    return output


def distance(left, right):
    keys = set(left) | set(right); denominator = sum(max(left[key], right[key]) for key in keys)
    return 1.0 - sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 1.0


def descriptor_tokens(text):
    text = text.split("||", 1)[-1].lower()
    text = re.sub(r"<[^>]*>|&[^;]*;|\bf\d+[rv]\w*\b", " ", text)
    output = []
    for word in re.findall(r"[a-z]+", text):
        if word in STOP or len(word) < 3: continue
        if word.endswith("ies") and len(word) > 4: word = word[:-3] + "y"
        elif word.endswith("ves") and len(word) > 4: word = word[:-3] + "f"
        elif word.endswith("s") and len(word) > 4: word = word[:-1]
        if word not in STOP: output.append(word)
    return set(output)


def losses(labels, probability):
    probability = np.clip(probability, 1e-12, 1 - 1e-12)
    return -np.log2(np.where(labels > 0, probability, 1 - probability))


def main():
    prediction = json.loads(PREDICTION.read_text())
    assert prediction["status"] == "FROZEN_POSTHOC_CROSS_PANEL_BEFORE_DESCRIPTOR_SCORING"
    prose = [row for row in read(PROSE) if not row["page"].startswith("f84")]
    source = [row for row in read(SOURCE) if not row["page"].startswith("f84")]
    assert len(source) == 15364 and not any(row["page"].startswith("f84") for row in source)
    licensed = licensed_hosts(prose)

    byline = defaultdict(list)
    host_folios = defaultdict(set)
    for row in source:
        byline[row["locus"]].append(row); host_folios[row["page_host"]].add(row["physical_folio"])
    events = []
    for locus, line in byline.items():
        line.sort(key=lambda row: int(row["group_index"]))
        for index, row in enumerate(line):
            previous = line[index - 1] if index else None
            following = line[index + 1] if index + 1 < len(line) else None
            own = ["W=" + row["wrapper"], "D=" + row["inner_d"], "F=" + row["local_frame"],
                   "R=" + row["right_family"], "DY=" + row["dy_closure"], "B3=" + row["b3"]]
            neighbor = ["PW=" + (previous["wrapper"] if previous else "BOS"),
                        "PF=" + (previous["local_frame"] if previous else "BOS"),
                        "PDY=" + (previous["dy_closure"] if previous else "BOS"),
                        "NW=" + (following["wrapper"] if following else "EOS"),
                        "NF=" + (following["local_frame"] if following else "EOS"),
                        "NDY=" + (following["dy_closure"] if following else "EOS")]
            events.append({"folio": row["physical_folio"], "host": row["page_host"], "tokens": own + neighbor})

    targets = read(TARGETS); capacity = {row["locus"]: row for row in read(CAPACITY)}
    assert len(targets) == len(capacity) == 44
    for row in targets: assert not row["page"].startswith("f84")
    vocab = [row["descriptor_token"] for row in read(MANIFEST)]; assert len(vocab) == 19
    y = np.array([[int(token in set(row["descriptor_tokens"].split(";"))) for token in vocab] for row in targets], dtype=float)
    token_counts = y.sum(axis=0).astype(int)
    endpoint_panels = {"ALL_19": list(range(19)), "TARGET_CAPACITY_GE3": [i for i, value in enumerate(token_counts) if 3 <= value <= len(targets) - 3]}
    assert len(endpoint_panels["TARGET_CAPACITY_GE3"]) == 8
    target_folios = sorted({row["physical_folio"] for row in targets})
    folio_indexes_all = {folio: np.array([i for i,row in enumerate(targets) if row["physical_folio"] == folio], dtype=int) for folio in target_folios}

    annotations = read(ANN); parsed = read(PARSED); assert len(annotations) == len(parsed) == 671
    grouped = defaultdict(list)
    for annotation, formal in zip(annotations, parsed):
        assert annotation["locus"] == formal["locus"] and annotation["group_index"] == formal["group_index"]
        if annotation["kind"] == "L" and annotation["annotation_certainty"] == "UNHEDGED" and annotation["section"] == "P" and "PLANT" in annotation["object_tags"].split(";"):
            grouped[annotation["locus"]].append((annotation, formal))
    assert len(grouped) == 83

    profile_cache = {}
    def profiles(folio):
        if folio not in profile_cache:
            counts = defaultdict(lambda: {"tokens": Counter(), "n": 0})
            for event in events:
                if event["folio"] == folio: continue
                counts[event["host"]]["tokens"].update(event["tokens"]); counts[event["host"]]["n"] += 1
            profile_cache[folio] = {host: Counter({key: value / item["n"] for key,value in item["tokens"].items()}) for host,item in counts.items()}
        return profile_cache[folio]

    training_by_fold = {}
    for folio in target_folios:
        fold_profiles = profiles(folio); training = []
        for locus, pairs in sorted(grouped.items()):
            pairs.sort(key=lambda pair: int(pair[0]["group_index"]))
            if not all(formal["page_host"] in fold_profiles and len(host_folios[formal["page_host"]] - {folio}) >= 1 for _,formal in pairs): continue
            features = {rep: Counter() for rep in REPS}
            for annotation, formal in pairs:
                features["BEHAVIOR_SELF_NEIGHBOR_NOPOS"].update(fold_profiles[formal["page_host"]])
                add_char3(features["PAGE_HOST_CHAR3"], formal["page_host"]); add_char3(features["RAW_CHAR3"], annotation["token"])
            training.append({"locus": locus, "folio": pairs[0][0]["physical_folio"], "tokens": descriptor_tokens(pairs[0][0]["raw_source_description"]), "features": features})
        assert len(training) >= 55
        training_by_fold[folio] = training

    target_editions = []
    for row in targets:
        fold_profiles = profiles(row["physical_folio"]); editions = {}
        for edition, column in EDITIONS:
            parsed_groups = [parse_token(token, licensed) for token in row[column].split("|")]
            features = {rep: Counter() for rep in REPS}
            for item in parsed_groups:
                add_char3(features["PAGE_HOST_CHAR3"], item["page_host"]); add_char3(features["RAW_CHAR3"], item["token"])
                if item["page_host"] in fold_profiles: features["BEHAVIOR_SELF_NEIGHBOR_NOPOS"].update(fold_profiles[item["page_host"]])
            complete1 = all(len(host_folios[item["page_host"]] - {row["physical_folio"]}) >= 1 for item in parsed_groups)
            complete2 = all(len(host_folios[item["page_host"]] - {row["physical_folio"]}) >= 2 for item in parsed_groups)
            editions[edition] = {"features": features, "complete1": complete1, "complete2": complete2}
        target_editions.append(editions)

    scope_features = {}; scope_indexes = {}
    for scope in SCOPES:
        features = {}; indexes = []
        for index, editions in enumerate(target_editions):
            if scope == "AVERAGE_PROFILEABLE_GE1": chosen=[item for item in editions.values() if item["complete1"]]
            elif scope == "AVERAGE_PROFILEABLE_GE2": chosen=[item for item in editions.values() if item["complete2"]]
            elif scope == "AVERAGE_ALL3_GE1": chosen=list(editions.values()) if all(item["complete1"] for item in editions.values()) else []
            else:
                edition=scope.split("_",1)[0]; chosen=[editions[edition]] if editions[edition]["complete1"] else []
            if chosen:
                indexes.append(index); features[index]={rep:average([item["features"][rep] for item in chosen]) for rep in REPS}
        scope_features[scope]=features; scope_indexes[scope]=np.array(indexes,dtype=int)
    assert [len(scope_indexes[x]) for x in SCOPES] == [31,27,15,23,22,26]

    baselines=np.zeros_like(y); probabilities={}
    for index,row in enumerate(targets):
        train=training_by_fold[row["physical_folio"]]
        for token_index,token in enumerate(vocab): baselines[index,token_index]=(sum(token in item["tokens"] for item in train)+.5)/(len(train)+1)
    neighbor_counts={}
    for scope in SCOPES:
        for rep in REPS:
            prediction_matrix=np.array(baselines,copy=True); counts=[]
            for index in scope_indexes[scope]:
                row=targets[index]; train=training_by_fold[row["physical_folio"]]
                candidates=[]
                for item in train:
                    d=distance(scope_features[scope][index][rep],item["features"][rep])
                    if d < 1-1e-12:candidates.append((d,item["locus"],item))
                candidates.sort(key=lambda item:(item[0],item[1])); nearest=candidates[:K]; counts.append(len(nearest))
                weights=np.array([1/(.1+item[0]) for item in nearest]); denominator=weights.sum()+SHRINK
                pred=SHRINK*baselines[index]/denominator
                for weight,(_,_,item) in zip(weights,nearest): pred += weight*np.array([int(token in item["tokens"]) for token in vocab])/denominator
                prediction_matrix[index]=pred
            probabilities[scope,rep]=prediction_matrix; neighbor_counts[scope,rep]=counts

    baseline_losses=losses(y,baselines); score_rows=[]; token_rows=[]; fold_rows=[]
    for scope in SCOPES:
        indexes=scope_indexes[scope]
        for panel,token_indexes in endpoint_panels.items():
            for rep in REPS:
                model_losses=losses(y,probabilities[scope,rep]); gain=float((baseline_losses[np.ix_(indexes,token_indexes)]-model_losses[np.ix_(indexes,token_indexes)]).sum())
                folio_gains=[]
                for folio in target_folios:
                    fi=np.intersect1d(indexes,folio_indexes_all[folio])
                    if not len(fi): continue
                    fg=float((baseline_losses[np.ix_(fi,token_indexes)]-model_losses[np.ix_(fi,token_indexes)]).sum());folio_gains.append((folio,len(fi),fg));fold_rows.append({"scope":scope,"endpoint_panel":panel,"representation":rep,"physical_folio":folio,"eligible_loci":len(fi),"gain_bits":fg})
                score_rows.append({"scope":scope,"endpoint_panel":panel,"representation":rep,"eligible_loci":len(indexes),"physical_folios":len(folio_gains),"descriptor_tokens":len(token_indexes),"positive_cells":int(y[np.ix_(indexes,token_indexes)].sum()),"baseline_bits":float(baseline_losses[np.ix_(indexes,token_indexes)].sum()),"held_bits":float(model_losses[np.ix_(indexes,token_indexes)].sum()),"gain_bits":gain,"selector_paid_gain_bits":gain-math.log2(3) if scope=="AVERAGE_PROFILEABLE_GE1" else "SENSITIVITY","positive_gain_folios":sum(value>0 for _,_,value in folio_gains),"min_folio_gain":min(value for _,_,value in folio_gains),"max_folio_gain":max(value for _,_,value in folio_gains),"mean_available_neighbors":float(np.mean(neighbor_counts[scope,rep])),"local_permutation_p":"PENDING","max_three_p":"PENDING"})
                for ti in token_indexes: token_rows.append({"scope":scope,"endpoint_panel":panel,"representation":rep,"descriptor_token":vocab[ti],"eligible_loci":len(indexes),"positive_loci":int(y[indexes,ti].sum()),"gain_bits":float((baseline_losses[indexes,ti]-model_losses[indexes,ti]).sum())})

    observed={(r["scope"],r["endpoint_panel"],r["representation"]):float(r["gain_bits"]) for r in score_rows}; local=Counter(); maxc=Counter();rng=np.random.default_rng(SEED)
    for _ in range(WORLDS):
        perm=y.copy()
        for fi in folio_indexes_all.values():perm[fi]=perm[rng.permutation(fi)]
        base=losses(perm,baselines)
        for scope in SCOPES:
            indexes=scope_indexes[scope]
            for panel,token_indexes in endpoint_panels.items():
                gains={}
                for rep in REPS:
                    model=losses(perm,probabilities[scope,rep]); value=float((base[np.ix_(indexes,token_indexes)]-model[np.ix_(indexes,token_indexes)]).sum());gains[rep]=value;local[scope,panel,rep]+=value>=observed[scope,panel,rep]-1e-12
                maxc[scope,panel]+=max(gains.values())>=max(observed[scope,panel,rep] for rep in REPS)-1e-12
    null_rows=[]
    for scope in SCOPES:
        for panel in endpoint_panels:
            for rep in REPS:
                p=(local[scope,panel,rep]+1)/(WORLDS+1);mp=(maxc[scope,panel]+1)/(WORLDS+1);null_rows.append({"scope":scope,"endpoint_panel":panel,"representation":rep,"worlds":WORLDS,"seed":SEED,"observed_gain_bits":observed[scope,panel,rep],"local_inclusive_p":p,"max_three_inclusive_p":mp,"preserves":"TARGET_PHYSICAL_FOLIO;COMPLETE_19_TOKEN_VECTOR;FORMAL_PREDICTIONS"})
    null_map={(r["scope"],r["endpoint_panel"],r["representation"]):r for r in null_rows}
    for row in score_rows:
        n=null_map[row["scope"],row["endpoint_panel"],row["representation"]];row["local_permutation_p"]=n["local_inclusive_p"];row["max_three_p"]=n["max_three_inclusive_p"]

    primary={r["representation"]:r for r in score_rows if r["scope"]=="AVERAGE_PROFILEABLE_GE1" and r["endpoint_panel"]=="ALL_19"}
    stronger=next(r for r in score_rows if r["scope"]=="AVERAGE_PROFILEABLE_GE2" and r["endpoint_panel"]=="ALL_19" and r["representation"]==REPS[0])
    all3_raw=next(r for r in score_rows if r["scope"]=="AVERAGE_ALL3_GE1" and r["endpoint_panel"]=="ALL_19" and r["representation"]=="RAW_CHAR3")
    behavior=primary[REPS[0]]; gates={
        "selector_paid_positive":float(behavior["selector_paid_gain_bits"])>0,
        "beats_page_host":float(behavior["gain_bits"])>float(primary["PAGE_HOST_CHAR3"]["gain_bits"]),
        "beats_raw":float(behavior["gain_bits"])>float(primary["RAW_CHAR3"]["gain_bits"]),
        "positive_at_least_4_of_6_folios":int(behavior["positive_gain_folios"])>=4,
        "two_outside_folio_sensitivity_positive":float(stronger["gain_bits"])>0,
        "max_three_p_le_005":float(behavior["max_three_p"])<=.05,
    }
    status="BEHAVIOR_PROFILE_LEGACY_TRANSFER_PROVISIONAL" if all(gates.values()) else "BEHAVIOR_PROFILE_LEGACY_TRANSFER_NOT_SUPPORTED"
    counter_rows=[]
    for row in sorted((x for x in fold_rows if x["scope"]=="AVERAGE_PROFILEABLE_GE1" and x["endpoint_panel"]=="ALL_19" and x["representation"]==REPS[0]),key=lambda x:float(x["gain_bits"])):
        counter_rows.append({"counterexample_type":"HELD_FOLIO_BEHAVIOR_GAIN","physical_folio":row["physical_folio"],"eligible_loci":row["eligible_loci"],"gain_bits":row["gain_bits"],"interpretation":"NEGATIVE_FOLIO" if float(row["gain_bits"])<=0 else "POSITIVE_FOLIO"})
    counter_rows += [
        {"counterexample_type":"ARCHIVE_POSTSELECTION","physical_folio":"ALL","eligible_loci":31,"gain_bits":"NA","interpretation":"GDT068 model and GDT109 target both previously exposed; no fresh confirmation."},
        {"counterexample_type":"FORMAL_COVERAGE","physical_folio":"ALL","eligible_loci":13,"gain_bits":"NA","interpretation":"13/44 target loci lack a completely behavior-profileable reading and are excluded by the frozen source-only rule."},
        {"counterexample_type":"READING_STABILITY","physical_folio":"ALL","eligible_loci":15,"gain_bits":"NA","interpretation":"Only 15/44 loci have all three alternate readings profileable."},
        {"counterexample_type":"RAW_READING_SENSITIVITY","physical_folio":"ALL","eligible_loci":15,"gain_bits":all3_raw["gain_bits"],"interpretation":"The small primary raw lead reverses on the all-three-readings-profileable sensitivity."},
    ]
    variants=[
        {"variant_id":"V00","status":"PRIMARY","description":"Average every fully profileable reading at >=1 outside physical folio; all 19 endpoints."},
        {"variant_id":"V01","status":"RUN_SENSITIVITY","description":"At least two outside physical folios per PAGE_HOST."},
        {"variant_id":"V02","status":"RUN_SENSITIVITY","description":"All three readings fully profileable."},
        {"variant_id":"V03","status":"RUN_SENSITIVITY","description":"ZL3b, IT2a, and RF1b profileable-reading panels separately."},
        {"variant_id":"V04","status":"RUN_BASELINES","description":"PAGE_HOST and raw char3 on identical behavior-eligible candidate pools."},
        {"variant_id":"V05","status":"NOT_RUN","description":"No descriptor selection, new parser, supervised cluster, image access, f84 access, gloss, or translation."},
    ]
    def clean(rows):return [{key:f"{value:.12g}" if isinstance(value,float) else value for key,value in row.items()} for row in rows]
    write(SCORES,clean(sorted(score_rows,key=lambda r:(r["scope"],r["endpoint_panel"],-float(r["gain_bits"]),r["representation"]))))
    write(TOKENS,clean(token_rows));write(FOLDS,clean(fold_rows));write(NULL,clean(null_rows));write(COUNTER,clean(counter_rows));write(VARIANTS,variants)
    REPORT.write_text(f"""# GDT136 — behavior-profile transfer to the legacy out-of-panel atlas

## Outcome

**{status}**

The frozen source-only capacity rule retains 31/44 legacy loci on all six
physical folios.  The stricter two-outside-folio sensitivity retains 27/44;
only 15/44 have all three alternate readings profileable.  The target archive
and GDT068 representation were already exposed, but the model/target crossing
was frozen before its descriptor predictions were computed.

On all 19 endpoints, `BEHAVIOR_SELF_NEIGHBOR_NOPOS` gains
{float(behavior['gain_bits']):+.3f} bits over folio-excluded prevalence,
{float(behavior['selector_paid_gain_bits']):+.3f} after the fixed three-model
selector, is positive on {behavior['positive_gain_folios']}/6 folios, and has
local p={float(behavior['local_permutation_p']):.4f}.  The shared family
max-three p={float(behavior['max_three_p']):.4f} is set by the better raw model,
not by the behavior profile.  PAGE_HOST char3 scores
{float(primary['PAGE_HOST_CHAR3']['gain_bits']):+.3f} bits and raw char3
{float(primary['RAW_CHAR3']['gain_bits']):+.3f}.  The two-outside-folio
behavior sensitivity is {float(stronger['gain_bits']):+.3f} bits.  Frozen
gates: {json.dumps(gates,sort_keys=True)}.

The nominal raw trace is positive on only
{primary['RAW_CHAR3']['positive_gain_folios']}/6 folios and reverses to
{float(all3_raw['gain_bits']):+.3f} bits on the 15-locus all-three-readings
panel.  It is therefore a sensitivity finding, not a replacement semantic
lead.

This {('does' if status.endswith('PROVISIONAL') else 'does not')} support
transfer of the archived GDT068 behavior-profile lead to the fixed GDT109
legacy stratum.  Folio, endpoint, reading, baseline, coverage, and null details
are exported without selecting an attractive descriptor away.

This is a post-hoc archive stress test.  It can at most identify a reusable
source-formal behavior class.  No descriptor is promoted to a gloss, and no
semantic class, role, word, morpheme, POS, sound, language, plaintext,
meaning, or translation is assigned.  Every f84 row was rejected before
formal retention; no new f84r access occurred.
""",encoding="utf-8")
    result={"schema":"GDT136_BEHAVIOR_PROFILE_LEGACY_TRANSFER_RESULT_V1","status":status,"target_loci_total":44,"primary_loci":31,"primary_folios":6,"two_outside_folio_loci":27,"all_readings_profileable_loci":15,"training_loci_by_target_fold":{folio:len(rows) for folio,rows in training_by_fold.items()},"descriptor_tokens":19,"target_capacity_tokens":8,"representations":list(REPS),"scopes":list(SCOPES),"primary":primary,"two_outside_folio_behavior":stronger,"all_readings_raw":all3_raw,"gates":gates,"interpretation":"Post-hoc cross-panel test of a frozen source-only PAGE_HOST behavior representation; no semantic assignment.","claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84":{"all_rows_rejected_before_retention":True,"new_f84r_access":False},"inputs":{path.name:sha(path) for path in (SOURCE,PROSE,ANN,PARSED,TARGETS,CAPACITY,MANIFEST,PREDICTION,ROOT/"gdt068_result.json",ROOT/"gdt109_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{path.name:sha(path) for path in (SCORES,TOKENS,FOLDS,NULL,COUNTER,VARIANTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
    result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"behavior_gain":behavior["gain_bits"],"host_gain":primary["PAGE_HOST_CHAR3"]["gain_bits"],"raw_gain":primary["RAW_CHAR3"]["gain_bits"],"gates":gates},sort_keys=True))


if __name__ == "__main__": main()
