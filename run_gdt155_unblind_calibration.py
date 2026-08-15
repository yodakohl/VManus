#!/usr/bin/env python3
"""Evaluate the frozen GDT155 blind objects against committed readable truth."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BLINES = ROOT / "gdt155_blinded_diplomatic.tsv"
BSITES = ROOT / "gdt155_blinded_abbreviation_sites.tsv"
ULINES = ROOT / "gdt155_unblinded_lines.tsv"
USITES = ROOT / "gdt155_unblinded_abbreviation_sites.tsv"
TRUTH = ROOT / "gdt155_unblinded_record_truth.tsv"
PARSES = ROOT / "gdt155_blind_group_parses.tsv"
TRANS = ROOT / "gdt155_blind_transformations.tsv"
BLIND_RESULT = ROOT / "gdt155_blind_result.json"
UNBLIND_RESULT = ROOT / "gdt155_unblind_export.json"
METHOD = ROOT / "GDT155_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_METHOD.md"

SITE_SUMMARY = ROOT / "gdt155_abbreviation_recovery.tsv"
SITE_ERRORS = ROOT / "gdt155_abbreviation_counterexamples.tsv"
OP_CORR = ROOT / "gdt155_operation_correspondence.tsv"
RETRIEVAL = ROOT / "gdt155_unblind_retrieval.tsv"
RETRIEVAL_SUMMARY = ROOT / "gdt155_unblind_retrieval_summary.tsv"
EFFECTS = ROOT / "gdt155_semantic_effect_sizes.tsv"
REPORT = ROOT / "GDT155_MEDIEVAL_ABBREVIATION_UNBLIND_REPORT.md"
RESULT = ROOT / "gdt155_unblind_calibration_result.json"

BOOKS = ("Band2", "Band3", "Band4", "Band5")
SITE_REPS = (
    "GLOBAL_EXPANSION_FREQUENCY", "RAW_SITE_IDENTITY", "RAW_GROUP_IDENTITY",
    "RAW_CHAR3_BACKOFF", "PAGE_HOST_IDENTITY", "COMPILER_SIGNATURE",
    "HOST_PLUS_COMPILER", "MARKER_AND_POSITION",
)
RECORD_REPS = (
    "RAW_GROUP_IDENTITY", "RAW_CHAR3", "PAGE_HOST_IDENTITY",
    "PAGE_HOST_CHAR3", "COMPILER_SIGNATURE", "MARKER_AND_POSITION",
    "HOST_PLUS_COMPILER",
)
FOLD_MAP = str.maketrans({"ſ": "s", "ı": "i", "ȷ": "j", "ẜ": "s"})


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def norm(value: str, marker: bool = True) -> str:
    value = unicodedata.normalize("NFC", value).translate(FOLD_MAP).lower()
    keep = [ch for ch in value if ch.isalnum() or (marker and ch == "¤")]
    return "".join(keep)


def phrase(value: str) -> str:
    return "_".join(filter(None, (norm(part, False) for part in value.split()))) or "EMPTY"


def groups(value: str) -> list[str]:
    return [token for part in value.split() if (token := norm(part))]


def char3(value: str) -> set[str]:
    value = "^" + value + "$"
    return {value[i:i + 3] for i in range(max(1, len(value) - 2))}


def words(value: str) -> set[str]:
    return {token for part in value.split() if (token := norm(part, False))}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a or b else 0.0


def wilson(success: int, total: int) -> tuple[float, float]:
    if not total: return 0.0, 0.0
    z = 1.959963984540054; p = success / total; den = 1 + z*z/total
    mid = (p + z*z/(2*total))/den
    half = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/den
    return max(0.0, mid-half), min(1.0, mid+half)


def compiler(row: dict[str, str]) -> str:
    return "|".join(row[field] for field in ("outer_left", "local_left", "right_inner", "right_outer", "abbreviation_marker"))


blines = read(BLINES); bsites = read(BSITES); ulines = read(ULINES); usites = read(USITES)
truth_rows = read(TRUTH); parse_rows = read(PARSES); trans_rows = read(TRANS)
assert len(blines) == len(ulines) == 48347 and len(bsites) == len(usites) == 119064
assert all(not any(value.lower().startswith("f84") for value in row.values()) for table in (blines, bsites, ulines, usites, truth_rows) for row in table)

blind_line = {row["line_id"]: row for row in blines}
unblind_line = {row["line_id"]: row for row in ulines}
site_truth = {row["site_id"]: row for row in usites}
sites_by_line: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in bsites: sites_by_line[row["line_id"]].append(row)
for values in sites_by_line.values(): values.sort(key=lambda row: int(row["site_index_in_record"]))
parse_map = {(row["fold"].replace("STE1_TRANSFER", "Ste1"), row["surface_group"]): row for row in parse_rows}

# Bind every editorial site to its containing frozen surface group without using expansion letters.
site_context: dict[str, dict[str, object]] = {}
aligned_group_expansions: dict[str, dict[str, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
aligned_lines = 0; unaligned_lines = 0
for line_id, brow in blind_line.items():
    marked = groups(brow["diplomatic_marked"]); expanded = groups(unblind_line[line_id]["expanded_diplomatic"])
    assignments = []
    for ordinal, token in enumerate(marked, 1): assignments.extend([(token, ordinal, len(marked))] * token.count("¤"))
    listed = sites_by_line.get(line_id, [])
    assert len(assignments) == len(listed), (line_id, len(assignments), len(listed))
    fold = brow["book_or_ms"]
    for srow, (token, ordinal, total) in zip(listed, assignments):
        parsed = parse_map[(fold, token)]
        site_context[srow["site_id"]] = {
            "book": fold, "record": brow["record_id"], "line": line_id,
            "raw_site": norm(srow["surface_span_bare"], False) or "EMPTY",
            "raw_group": token.replace("¤", "") or "EMPTY",
            "page_host": parsed["page_host"], "compiler": compiler(parsed),
            "host_compiler": parsed["page_host"] + "@" + compiler(parsed),
            "marker_position": f"RQ={brow['record_position_quartile']}|GQ={min(3,4*(ordinal-1)//max(1,total))}",
        }
    if len(marked) == len(expanded):
        aligned_lines += 1
        for surface, target in zip(marked, expanded):
            aligned_group_expansions[fold][surface.replace("¤", "")][target] += 1
    else:
        unaligned_lines += 1
assert len(site_context) == len(bsites)


def site_key(ctx: dict[str, object], rep: str) -> str:
    return {
        "RAW_SITE_IDENTITY": str(ctx["raw_site"]), "RAW_GROUP_IDENTITY": str(ctx["raw_group"]),
        "PAGE_HOST_IDENTITY": str(ctx["page_host"]), "COMPILER_SIGNATURE": str(ctx["compiler"]),
        "HOST_PLUS_COMPILER": str(ctx["host_compiler"]), "MARKER_AND_POSITION": str(ctx["marker_position"]),
    }[rep]


site_summary = []; site_errors = []
predicted_by_fold_rep: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {}
for held in BOOKS + ("Ste1",):
    train_books = BOOKS if held == "Ste1" else tuple(book for book in BOOKS if book != held)
    train = [row for row in usites if row["corpus"] == "NUREMBERG" and row["book_or_ms"] in train_books]
    test = [row for row in usites if row["book_or_ms"] == held]
    target_frequency = Counter(phrase(row["expanded_span"]) for row in train)
    raw_keys = defaultdict(Counter)
    for row in train: raw_keys[norm(row["surface_span_bare"], False) or "EMPTY"][phrase(row["expanded_span"])] += 1
    raw_vocab = sorted(raw_keys)
    nearest_cache: dict[str, str] = {}
    for rep in SITE_REPS:
        tables: dict[str, Counter[str]] = defaultdict(Counter)
        if rep not in {"GLOBAL_EXPANSION_FREQUENCY", "RAW_CHAR3_BACKOFF"}:
            for row in train:
                tables[site_key(site_context[row["site_id"]], rep)][phrase(row["expanded_span"])] += 1
        correct = top3 = covered = 0; class_score = defaultdict(lambda: [0, 0]); predictions = {}; rank_cache = {}
        for row in test:
            sid = row["site_id"]; ctx = site_context[sid]; target = phrase(row["expanded_span"])
            counter: Counter[str]
            if rep == "GLOBAL_EXPANSION_FREQUENCY": counter = target_frequency; cache_key = "GLOBAL"
            elif rep == "RAW_CHAR3_BACKOFF":
                raw = str(ctx["raw_site"])
                if raw in raw_keys: counter = raw_keys[raw]; cache_key = "RAW=" + raw
                else:
                    if raw not in nearest_cache:
                        candidates = [x for x in raw_vocab if x[:1] == raw[:1] and abs(len(x)-len(raw)) <= 2]
                        if not candidates: candidates = [x for x in raw_vocab if abs(len(x)-len(raw)) <= 2]
                        if not candidates: candidates = raw_vocab
                        nearest_cache[raw] = min(candidates, key=lambda x: (-jaccard(char3(raw), char3(x)), abs(len(x)-len(raw)), x))
                    nearest = nearest_cache[raw]; counter = raw_keys[nearest]; cache_key = "NEAR=" + nearest
            else:
                key = site_key(ctx, rep); counter = tables.get(key, Counter()); cache_key = "KEY=" + key
            if cache_key not in rank_cache:
                rank_cache[cache_key] = tuple(value for value, _ in sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:3])
            ranked = rank_cache[cache_key]
            predictions[sid] = ranked
            if ranked:
                covered += 1; hit = int(ranked[0] == target); correct += hit; top3 += int(target in ranked)
                class_score[target][0] += hit; class_score[target][1] += 1
        predicted_by_fold_rep[(held, rep)] = predictions
        lo, hi = wilson(correct, covered)
        macro = statistics.mean(a/b for a,b in class_score.values()) if class_score else 0.0
        site_summary.append({
            "held_book_or_ms":held, "training_books":";".join(train_books), "representation":rep,
            "test_sites":len(test), "predictions_made":covered, "coverage":f"{covered/max(1,len(test)):.12g}",
            "top1_correct":correct, "top1_accuracy":f"{correct/max(1,covered):.12g}",
            "top1_wilson_low":f"{lo:.12g}", "top1_wilson_high":f"{hi:.12g}",
            "top3_correct":top3, "top3_accuracy":f"{top3/max(1,covered):.12g}",
            "macro_target_accuracy":f"{macro:.12g}", "distinct_test_targets":len(class_score),
        })

for row in usites:
    held = row["book_or_ms"]
    if held not in BOOKS: continue
    target = phrase(row["expanded_span"]); raw = predicted_by_fold_rep[(held,"RAW_SITE_IDENTITY")][row["site_id"]]
    host = predicted_by_fold_rep[(held,"PAGE_HOST_IDENTITY")][row["site_id"]]
    comp = predicted_by_fold_rep[(held,"COMPILER_SIGNATURE")][row["site_id"]]
    if raw and ((raw[0] == target) != (bool(host) and host[0] == target)):
        ctx = site_context[row["site_id"]]
        site_errors.append({
            "site_id":row["site_id"], "book":held, "record_id":row["record_id"],
            "surface_bare":row["surface_span_bare"] or "EMPTY", "expanded_truth":row["expanded_span"],
            "page_host":ctx["page_host"], "compiler_signature":ctx["compiler"],
            "raw_prediction":raw[0], "page_host_prediction":host[0] if host else "NO_PREDICTION",
            "compiler_prediction":comp[0] if comp else "NO_PREDICTION",
            "contrast":"RAW_CORRECT_HOST_WRONG" if raw[0] == target else "HOST_CORRECT_RAW_WRONG",
        })
site_errors.sort(key=lambda row: (row["contrast"], row["book"], row["record_id"], row["site_id"]))
site_errors = site_errors[:250]

# Interpret the already-frozen blind operations through expansion-preserving group alignments.
op_rows = []
for trow in trans_rows:
    fold = trow["fold"]
    train_books = BOOKS if fold == "ALL_NUREMBERG" else tuple(book for book in BOOKS if book != fold)
    expansion: dict[str, Counter[str]] = defaultdict(Counter)
    for book in train_books:
        for surface, counts in aligned_group_expansions[book].items(): expansion[surface].update(counts)
    vocab = {value for value in expansion if value}; op = trow["operation"]; side = trow["side"]
    preserved = same = other = 0; examples = []
    for base in sorted(vocab):
        transformed = op + base if side == "LEFT" else base + op
        if transformed not in vocab: continue
        bexp = min(expansion[base], key=lambda x: (-expansion[base][x], x))
        texp = min(expansion[transformed], key=lambda x: (-expansion[transformed][x], x))
        expected = op + bexp if side == "LEFT" else bexp + op
        if texp == expected: preserved += 1; label = "EDGE_OPERATION_PRESERVED"
        elif texp == bexp: same += 1; label = "SAME_EXPANDED_FORM"
        else: other += 1; label = "OTHER_LEXICAL_OR_ORTHOGRAPHIC_CONTRAST"
        if len(examples) < 4: examples.append(f"{base}>{transformed}:{bexp}>{texp}:{label}")
    total = preserved + same + other
    op_rows.append({
        "fold":fold, "side":side, "operation":op, "exact_aligned_pairs":total,
        "edge_operation_preserved":preserved, "same_expanded_form":same,
        "other_lexical_or_orthographic":other,
        "preserved_fraction":f"{preserved/max(1,total):.12g}",
        "same_expansion_fraction":f"{same/max(1,total):.12g}",
        "examples":" || ".join(examples) or "NONE",
    })

# Reconstruct frozen record representations, then rank known content/addressee neighbors.
by_record_lines: dict[str, list[dict[str,str]]] = defaultdict(list)
for row in blines: by_record_lines[row["record_id"]].append(row)
for values in by_record_lines.values(): values.sort(key=lambda row:int(row["line_index"]))
profiles: dict[str, dict[str,set[str]]] = {}
pages = {}; record_book = {}
for record, lines in by_record_lines.items():
    book = lines[0]["book_or_ms"]; record_book[record]=book; pages[record]={row["page_id"] for row in lines}
    feats={rep:set() for rep in RECORD_REPS}; seq=[]
    for row in lines:
        seq.extend((token,row) for token in groups(row["diplomatic_marked"]))
    total=len(seq)
    for ordinal,(token,row) in enumerate(seq,1):
        parsed=parse_map[(book,token)]; host=parsed["page_host"]; sig=compiler(parsed)
        lq=min(3,4*(int(row["line_index"])-1)//max(1,int(row["record_line_count"])))
        tq=min(3,4*(ordinal-1)//max(1,total))
        feats["RAW_GROUP_IDENTITY"].add("W="+token); feats["RAW_CHAR3"].update("C="+x for x in char3(token))
        feats["PAGE_HOST_IDENTITY"].add("H="+host); feats["PAGE_HOST_CHAR3"].update("HC="+x for x in char3(host))
        feats["COMPILER_SIGNATURE"].add("S="+sig)
        feats["MARKER_AND_POSITION"].add(f"M={parsed['abbreviation_marker']}|LQ={lq}|TQ={tq}")
        feats["HOST_PLUS_COMPILER"].add("J="+host+"@"+sig)
    profiles[record]=feats

truth_by_record={row["record_id"]:row for row in truth_rows if row["corpus"]=="NUREMBERG"}
truth_sets={record:{"CONTENT":words(row["regularized_content"]),"ADDRESSEE":words(row["regularized_addressee"])} for record,row in truth_by_record.items()}
retrieval_rows=[]; aggregate=defaultdict(lambda:{"n":0,"rr":0.0,"top1":0,"top10":0,"topdec":0,"nr":[]})
for book in BOOKS:
    records=sorted(record for record in truth_by_record if record_book[record]==book)
    for query in records:
        candidates=[candidate for candidate in records if candidate!=query and not(pages[query]&pages[candidate])]
        model_ranks={}
        for rep in RECORD_REPS:
            ranked=sorted(candidates,key=lambda c:(-jaccard(profiles[query][rep],profiles[c][rep]),c))
            model_ranks[rep]={candidate:rank for rank,candidate in enumerate(ranked,1)}
        for dimension in ("CONTENT","ADDRESSEE"):
            qtruth=truth_sets[query][dimension]
            if not qtruth: continue
            truth_scores=[(jaccard(qtruth,truth_sets[candidate][dimension]),candidate) for candidate in candidates if truth_sets[candidate][dimension]]
            if not truth_scores: continue
            best_similarity,target=max(truth_scores,key=lambda item:(item[0],-int(item[1].split("R")[-1])))
            if best_similarity<=0: continue
            for rep in RECORD_REPS:
                rank=model_ranks[rep][target]; pool=len(candidates); decile=max(1,math.ceil(pool/10))
                similarity=jaccard(profiles[query][rep],profiles[target][rep])
                retrieval_rows.append({
                    "book":book,"query_record":query,"truth_dimension":dimension,"truth_target_record":target,
                    "truth_set_jaccard":f"{best_similarity:.12g}","representation":rep,
                    "candidate_pool":pool,"model_rank":rank,"reciprocal_rank":f"{1/rank:.12g}",
                    "top1":int(rank==1),"top10":int(rank<=10),"top_decile":int(rank<=decile),
                    "normalized_rank":f"{rank/pool:.12g}","model_set_jaccard":f"{similarity:.12g}",
                })
                for key in ((book,dimension,rep),("ALL",dimension,rep)):
                    acc=aggregate[key];acc["n"]+=1;acc["rr"]+=1/rank;acc["top1"]+=int(rank==1);acc["top10"]+=int(rank<=10);acc["topdec"]+=int(rank<=decile);acc["nr"].append(rank/pool)
retrieval_summary=[]
for (book,dimension,rep),acc in sorted(aggregate.items()):
    n=acc["n"]
    retrieval_summary.append({
        "book":book,"truth_dimension":dimension,"representation":rep,"queries_with_nonzero_truth_neighbor":n,
        "mean_reciprocal_rank":f"{acc['rr']/n:.12g}","top1":acc["top1"],"top1_rate":f"{acc['top1']/n:.12g}",
        "top10":acc["top10"],"top10_rate":f"{acc['top10']/n:.12g}",
        "top_decile":acc["topdec"],"top_decile_rate":f"{acc['topdec']/n:.12g}",
        "median_normalized_rank":f"{statistics.median(acc['nr']):.12g}",
    })

write(SITE_SUMMARY,site_summary);write(SITE_ERRORS,site_errors);write(OP_CORR,op_rows)
write(RETRIEVAL,retrieval_rows);write(RETRIEVAL_SUMMARY,retrieval_summary)

def srow(rep:str, held:str="ALL") -> dict[str,str]:
    rows=[row for row in site_summary if row["representation"]==rep and (held=="ALL" or row["held_book_or_ms"]==held) and row["held_book_or_ms"] in BOOKS]
    n=sum(int(row["predictions_made"]) for row in rows); correct=sum(int(row["top1_correct"]) for row in rows)
    return {"n":str(n),"correct":str(correct),"accuracy":f"{correct/max(1,n):.12g}"}

def rrow(rep:str,dim:str="CONTENT") -> dict[str,str]:
    return next(row for row in retrieval_summary if row["book"]=="ALL" and row["truth_dimension"]==dim and row["representation"]==rep)

raw=srow("RAW_SITE_IDENTITY");host=srow("PAGE_HOST_IDENTITY");comp=srow("COMPILER_SIGNATURE");back=srow("RAW_CHAR3_BACKOFF")
rawret=rrow("RAW_CHAR3");hostret=rrow("PAGE_HOST_CHAR3");compret=rrow("COMPILER_SIGNATURE")
add_raw=rrow("RAW_CHAR3","ADDRESSEE");add_host=rrow("PAGE_HOST_CHAR3","ADDRESSEE");add_comp=rrow("COMPILER_SIGNATURE","ADDRESSEE")
effect_rows=[
    {"endpoint":"EXPANDED_SITE_TOP1_CONDITIONAL_ON_COVERAGE","contrast":"RAW_SITE_IDENTITY_MINUS_PAGE_HOST","left_value":raw["accuracy"],"right_value":host["accuracy"],"difference":f"{float(raw['accuracy'])-float(host['accuracy']):.12g}","n_left":raw["n"],"n_right":host["n"],"interpretation":"RAW_SURFACE_RETAINS_MORE_EXPANSION_IDENTITY"},
    {"endpoint":"EXPANDED_SITE_TOP1_CONDITIONAL_ON_COVERAGE","contrast":"PAGE_HOST_MINUS_COMPILER","left_value":host["accuracy"],"right_value":comp["accuracy"],"difference":f"{float(host['accuracy'])-float(comp['accuracy']):.12g}","n_left":host["n"],"n_right":comp["n"],"interpretation":"HOST_RETAINS_LEXICAL_INFORMATION_BEYOND_COMPILER"},
    {"endpoint":"CONTENT_RETRIEVAL_MRR","contrast":"RAW_CHAR3_MINUS_PAGE_HOST_CHAR3","left_value":rawret["mean_reciprocal_rank"],"right_value":hostret["mean_reciprocal_rank"],"difference":f"{float(rawret['mean_reciprocal_rank'])-float(hostret['mean_reciprocal_rank']):.12g}","n_left":rawret["queries_with_nonzero_truth_neighbor"],"n_right":hostret["queries_with_nonzero_truth_neighbor"],"interpretation":"HOST_PRESERVES_MOST_BUT_NOT_ALL_RAW_CONTENT_SIGNAL"},
    {"endpoint":"CONTENT_RETRIEVAL_MRR","contrast":"PAGE_HOST_CHAR3_MINUS_COMPILER","left_value":hostret["mean_reciprocal_rank"],"right_value":compret["mean_reciprocal_rank"],"difference":f"{float(hostret['mean_reciprocal_rank'])-float(compret['mean_reciprocal_rank']):.12g}","n_left":hostret["queries_with_nonzero_truth_neighbor"],"n_right":compret["queries_with_nonzero_truth_neighbor"],"interpretation":"HOST_CARRIES_CONTENT_SIGNAL_BEYOND_DOCUMENT_FORMULA"},
    {"endpoint":"ADDRESSEE_RETRIEVAL_MRR","contrast":"RAW_CHAR3_MINUS_PAGE_HOST_CHAR3","left_value":add_raw["mean_reciprocal_rank"],"right_value":add_host["mean_reciprocal_rank"],"difference":f"{float(add_raw['mean_reciprocal_rank'])-float(add_host['mean_reciprocal_rank']):.12g}","n_left":add_raw["queries_with_nonzero_truth_neighbor"],"n_right":add_host["queries_with_nonzero_truth_neighbor"],"interpretation":"HOST_AND_RAW_ADDRESS_SIGNAL_NEAR_EQUAL"},
    {"endpoint":"ADDRESSEE_RETRIEVAL_MRR","contrast":"PAGE_HOST_CHAR3_MINUS_COMPILER","left_value":add_host["mean_reciprocal_rank"],"right_value":add_comp["mean_reciprocal_rank"],"difference":f"{float(add_host['mean_reciprocal_rank'])-float(add_comp['mean_reciprocal_rank']):.12g}","n_left":add_host["queries_with_nonzero_truth_neighbor"],"n_right":add_comp["queries_with_nonzero_truth_neighbor"],"interpretation":"COMPILER_FORMULA_HAS_WEAK_ADDRESS_SIGNAL"},
]
write(EFFECTS,effect_rows)
result={
    "schema":"GDT155_UNBLIND_CALIBRATION_RESULT_V1","status":"REAL_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_CALIBRATED",
    "chronology":{"source_freeze_commit":"d62de97","blind_analysis_commit":"99bab66","truth_export_commit":"3374596","unblind_scoring_after_all":True},
    "counts":{"lines":len(blines),"sites":len(usites),"records":len(truth_rows),"aligned_group_lines":aligned_lines,"unaligned_group_lines":unaligned_lines,"retrieval_rows":len(retrieval_rows)},
    "site_expansion_recovery":{"raw_identity":raw,"raw_char3_backoff":back,"page_host":host,"compiler":comp},
    "content_retrieval":{"raw_char3":rawret,"page_host_char3":hostret,"compiler":compret},
    "calibration_findings":[
        "Form-only rectangles and productive edge operations are abundant in genuine abbreviated medieval German.",
        "Expanded-word identity is principally retained by diplomatic surface identity; PAGE_HOST stripping and compiler-only features are lower-information controls.",
        "Record-level PAGE_HOST similarity can be evaluated against known content and addressee structure, but any gain shared with raw character features is not Voynich-specific.",
    ],
    "claim_ceiling":"Positive-control calibration only; no Voynich word, morpheme, sound, part of speech, language, plaintext, meaning, or translation.",
    "f84":{"voynich_inputs":0,"accessed":False},
    "inputs":{path.name:sha(path) for path in (BLINES,BSITES,ULINES,USITES,TRUTH,PARSES,TRANS,BLIND_RESULT,UNBLIND_RESULT)},
    "implementation":{Path(__file__).name:sha(Path(__file__))},
    "documents":{METHOD.name:sha(METHOD)},
    "outputs":{path.name:sha(path) for path in (SITE_SUMMARY,SITE_ERRORS,OP_CORR,RETRIEVAL,RETRIEVAL_SUMMARY,EFFECTS)},
}
result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")

ste=next(row for row in site_summary if row["held_book_or_ms"]=="Ste1" and row["representation"]=="RAW_SITE_IDENTITY")
REPORT.write_text(f"""# GDT155 — unblinded medieval abbreviation calibration

## Outcome

**REAL_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_CALIBRATED**

The frozen form-only analysis was unblinded only after its public source and
analysis checkpoints.  Across the four held Nuremberg books, raw diplomatic
site identity recovers {raw['correct']}/{raw['n']} expanded spans
({float(raw['accuracy']):.1%}); training-only raw-character backoff recovers
{back['correct']}/{back['n']} ({float(back['accuracy']):.1%}).  The HPR2-like
`PAGE_HOST` representation recovers {host['correct']}/{host['n']}
({float(host['accuracy']):.1%}), while compiler signature alone recovers
{comp['correct']}/{comp['n']} ({float(comp['accuracy']):.1%}).  The two Ste1
technical records are a strict Nuremberg-trained descriptive transfer:
{ste['top1_correct']}/{ste['predictions_made']} sites are recovered by exact
raw-site identity; their small size does not make them a separate statistical
replication.

The blind transformation inventory contained thousands of complete formal
rectangles before meanings were visible.  Unblinding shows which selected
edge contrasts survive literally in expanded spelling and which collapse to
the same expansion or become ordinary lexical/orthographic contrasts.  This
is the central positive-control warning: rectangles and reusable edge
operations are expected in real abbreviated natural language, but do not by
themselves localize semantics or establish a linguistic analysis.

For GDT148-style document retrieval, the target for every query is selected
mechanically as the non-co-page, same-book record with greatest regularized
content (or addressee) token-set overlap.  Raw character retrieval has content
MRR {float(rawret['mean_reciprocal_rank']):.4f}, PAGE_HOST character retrieval
MRR {float(hostret['mean_reciprocal_rank']):.4f}, and compiler-only retrieval
MRR {float(compret['mean_reciprocal_rank']):.4f}.  Raw therefore exceeds the
stripped host by {float(rawret['mean_reciprocal_rank'])-float(hostret['mean_reciprocal_rank']):.4f}
MRR, whereas the host exceeds compiler-only retrieval by
{float(hostret['mean_reciprocal_rank'])-float(compret['mean_reciprocal_rank']):.4f}.
These are effect-size calibrations, not evidence that the blind host is a stem
or semantic unit.

### Interpretation

Real medieval abbreviated language produces strong local string families,
left/right asymmetry, complete transformation rectangles, record-position
effects, and recurrent stripped hosts.  The known expansion truth nevertheless
shows that raw visible spelling usually retains more exact lexical information
than aggressive PAGE_HOST stripping.  Compiler features can encode document
formula and position, but are not an independent content vocabulary.

No Voynich source, image, or f84 material was accessed.  The next checkpoint
applies the already frozen `VMS_HPR2_ABBR_V1` encoder to this readable control
and labels every resulting property as imposed or emergent.
""",encoding="utf-8")
print(json.dumps({"status":result["status"],"raw_site_accuracy":raw["accuracy"],"host_site_accuracy":host["accuracy"],"content_raw_mrr":rawret["mean_reciprocal_rank"],"content_host_mrr":hostret["mean_reciprocal_rank"]},sort_keys=True))
