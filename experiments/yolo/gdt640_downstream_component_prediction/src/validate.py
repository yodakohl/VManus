#!/usr/bin/env python3
"""Independent release validator for GDT640."""
from __future__ import annotations

import csv, hashlib, importlib.util, json, re, sys, tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt640_downstream_component_prediction")
ART, RUN = ROOT / BASE / "artifacts", ROOT / BASE / "src/run.py"
VALIDATION = ART / "VALIDATION.json"
TARGETS = ("qotomody", "qotor", "okal", "chotcheol")
OCCURRENCES = {"qotomody": 1, "qotor": 26, "okal": 123, "chotcheol": 1}
ACCEPTED = ("qotor", "okal", "chotcheol")
OUTPUTS = (
    "PAGE_ALLOWLIST.tsv", "TARGET_PREDICTION_DECK.tsv", "FORM_FAMILY_ATLAS.tsv",
    "COMPONENT_BINDING_AUDIT.tsv", "ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv",
    "SEQUENTIAL_DECISION_LEDGER.tsv", "ROUND_COVERAGE_COUNTS.tsv",
    "ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv", "HELD_TARGET_DEFAULTS.tsv",
    "NEWLY_COMPLETED_LINES.tsv", "V17_EXACT_TOKEN_GLOSSARY.tsv",
    "ALL_LINE_CONCRETE_COVERAGE_V17.tsv", "COMPLETE_PASSAGES_V17.tsv",
    "ONE_UNKNOWN_PASSAGES_V17.tsv", "WORKING_DICTIONARY_V17.tsv", "RESULT.json",
)
GENERIC = re.compile(r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|werkzeug|produkt weiter|f.hre .* aus|leite .* weiter", re.I)


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("gdt640_builder_validation", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT640 builder")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def main() -> int:
    passed, issues = [], []
    def check(ok, name, detail=""):
        (passed if ok else issues).append(name if ok else f"{name}: {detail or 'condition failed'}")

    b = load_builder()
    with tempfile.TemporaryDirectory(prefix="gdt640_validate_") as tmp:
        replay = Path(tmp)
        try:
            replay_result = b.build(replay)
        except Exception as exc:
            replay_result = None; issues.append(f"builder replay: {type(exc).__name__}: {exc}")
        if replay_result is not None:
            for name in OUTPUTS:
                expected, actual = ART/name, replay/name
                check(expected.is_file() and actual.is_file(), f"output present:{name}")
                if expected.is_file() and actual.is_file():
                    check(expected.read_bytes() == actual.read_bytes(), f"byte replay:{name}", f"repo={sha(expected)} replay={sha(actual)}")
            check(replay_result == json.loads((ART/"RESULT.json").read_text()), "builder return equals RESULT")

    result = json.loads((ART/"RESULT.json").read_text())
    core = {k:v for k,v in result.items() if k != "content_sha256"}
    check(result.get("content_sha256") == canonical(core), "RESULT content hash")
    for rel,digest in result.get("inputs",{}).items():
        p=ROOT/rel; check(p.is_file() and sha(p)==digest, f"input hash:{rel}")
    for rel,digest in result.get("outputs",{}).items():
        p=ROOT/rel; check(p.is_file() and sha(p)==digest, f"output hash:{rel}")

    allow=rows(ART/"PAGE_ALLOWLIST.tsv"); pages={r["page"] for r in allow}
    check(len(allow)==len(pages)==179, "179 unique allowed pages")
    check("f1r" not in pages, "f1r excluded")
    check(not any(p.startswith("f84") for p in pages), "f84/f84r forbidden")
    guard=result.get("guard",{})
    check(guard.get("allowed_pages")==179 and guard.get("f1r")=="EXCLUDED" and guard.get("f84")=="FORBIDDEN" and guard.get("f84r")=="FORBIDDEN" and guard.get("new_pages")==0 and guard.get("new_images")==0, "RESULT guard")

    query=b.g637.g636.g635.g634.g633.g632.g631.guarded_query
    token_rows,token_stats=query(b.TOKENS_REL,pages,"page,locus,token_index,eva,section,language,hand")
    cross_rows,cross_stats=query(b.CROSS_REL,pages,"page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean")
    counts=Counter(r["eva"] for r in token_rows)
    check({s:counts[s] for s in TARGETS}==OCCURRENCES, "guarded target census", str({s:counts[s] for s in TARGETS}))
    check(sum(counts[s] for s in TARGETS)==151, "151 guarded target occurrences")
    check(token_stats==guard.get("token_query") and cross_stats==guard.get("cross_query"), "guarded query statistics")
    check(all(r["page"] in pages and r["page"]!="f1r" and not r["page"].startswith("f84") for r in token_rows+cross_rows), "materialized scope clean")

    deck=rows(ART/"TARGET_PREDICTION_DECK.tsv")
    check(tuple(r["surface"] for r in deck)==TARGETS, "exact target order")
    check([int(r["occurrences"]) for r in deck]==[1,26,123,1], "deck occurrences")
    check(tuple(r["surface"] for r in deck if r["decision"]=="ACCEPT")==ACCEPTED, "accepted set/order")
    check([r["surface"] for r in deck if r["decision"]=="HOLD"]==["qotomody"], "held set")
    check(len(rows(ART/"ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv"))==151, "151 audit rows")

    held=rows(ART/"HELD_TARGET_DEFAULTS.tsv")
    check(len(held)==1 and held[0]["surface"]=="qotomody" and held[0]["decision"]=="HOLD", "qotomody held")
    check(bool(held) and held[0]["default_meaning_de"]=="kaltes Ansatzmaß, fertig aufbereitete Grundform", "qotomody concrete default")
    check(bool(held) and held[0]["barrier"]=="INTERNAL_M_ROLE_UNBOUND" and held[0]["composition"]=="qot+o+m+ody", "qotomody internal-m barrier")
    accepted=rows(ART/"ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv")
    check(tuple(r["surface"] for r in accepted)==ACCEPTED, "three accepted rows")
    check([int(r["occurrences"]) for r in accepted]==[26,123,1], "accepted occurrence counts")
    accepted_by_surface={r["surface"]:r for r in accepted}
    check(accepted_by_surface.get("okal",{}).get("working_meaning_de")=="Ansatz aus heißem Rohstoff, Form I" and accepted_by_surface.get("okal",{}).get("composition")=="o+k+al", "okal exact meaning/composition")
    check(accepted_by_surface.get("chotcheol",{}).get("working_meaning_de")=="Trockenansatz aus kalt-trockenem Drogenstoff" and accepted_by_surface.get("chotcheol",{}).get("composition")=="cho+tch+e+ol", "chotcheol corrected meaning/composition")
    check(all("exact complete surface only" in r["context_rule"] and "no substring, naked-body, wrapper or absent-cell transfer" in r["context_rule"] for r in accepted), "exact-only scopes")

    v16=rows(ROOT/b.G639_DICT_REL); v17=rows(ART/"WORKING_DICTIONARY_V17.tsv")
    check(len(v16)==280 and len(v17)==283, "V16 280 plus three")
    check(v17[:280]==v16, "V16 row prefix preserved")
    check(tuple(r["entry"].split("@",1)[0] for r in v17[280:])==ACCEPTED, "V17 accepted tail")
    check(not any(r["entry"].split("@",1)[0].lower() in {"or","al","m","cheol"} for r in v17[280:]), "no new bare OR/AL/M/CHEOL dictionary rows")
    glossary=rows(ART/"V17_EXACT_TOKEN_GLOSSARY.tsv"); base_gloss=rows(ROOT/b.G639_GLOSSARY_REL)
    check(len(glossary)==236 and len(base_gloss)==233, "glossary 233 plus three")
    added={r["surface"] for r in glossary}-{r["surface"] for r in base_gloss}
    check(added==set(ACCEPTED), "no bare component glossary promotion", str(added))

    components=rows(ART/"COMPONENT_BINDING_AUDIT.tsv")
    check(len(components)==10, "ten component binding rows")
    tch=[r for r in components if r["surface"]=="chotcheol" and r["segment"]=="tch"]
    g625_rel="experiments/yolo/gdt625_ordered_quality_state_transitions/artifacts/TERMINAL_QUALITY_OCCURRENCES.tsv"
    check(len(tch)==1 and tch[0]["working_value_de"]=="kalt-trocken" and tch[0]["evidence_path"]==g625_rel and tch[0]["evidence_kind"]=="BOUND_TCH_QUALITY_BLOCK", "GDT625 TCH component binding")
    check(g625_rel in result.get("inputs",{}) and sha(ROOT/g625_rel)==result["inputs"].get(g625_rel), "GDT625 input bound and hashed")
    active_rows=(deck+accepted+glossary+v17+rows(ART/"FORM_FAMILY_ATLAS.tsv")+
                 rows(ART/"NEWLY_COMPLETED_LINES.tsv"))
    active_compositions=[r.get("composition","") for r in active_rows]
    active_meanings=[r.get(key,"") for r in active_rows for key in
                     ("working_meaning_de","working_reading_de","default_meaning_de",
                      "literal_after_de","smoothed_working_reading_de")]
    check("ch+o+t+ch+e+ol" not in active_compositions,
          "obsolete chotcheol split absent from active cards")
    check("kalter Trockenansatz aus Trockengut" not in active_meanings,
          "obsolete chotcheol gloss absent from active cards")

    coverage=rows(ART/"ALL_LINE_CONCRETE_COVERAGE_V17.tsv"); complete=rows(ART/"COMPLETE_PASSAGES_V17.tsv"); one=rows(ART/"ONE_UNKNOWN_PASSAGES_V17.tsv")
    check(len(coverage)==4128, "4128 coverage lines")
    check(sum(int(r["known_tokens"]) for r in coverage)==9741 and sum(int(r["unknown_tokens"]) for r in coverage)==22598, "coverage 9741/22598")
    check(len(complete)==42 and sum(int(r["strict_complete"]) for r in complete)==31, "complete 42/31")
    check(len(one)==62 and sum(int(r["strict_eligible"]) for r in one)==19, "one-hole 62/19")
    new=rows(ART/"NEWLY_COMPLETED_LINES.tsv")
    check(len(new)==3 and {r["locus"] for r in new}=={"f37v.16","f25r.6","f49r.11"}, "exactly three new loci")
    run,cov=result.get("target_run",{}),result.get("coverage",{})
    check((run.get("candidates"),run.get("accepted"),run.get("held"),run.get("audited_occurrences"))==(4,3,1,151), "RESULT target counts")
    expected={"physical_lines":4128,"known_token_positions":9741,"unknown_token_positions":22598,"complete_multi_token_lines":42,"strict_complete_lines":31,"one_unknown_lines":62,"strict_one_unknown_lines":19,"exact_glossary_surfaces":236,"newly_completed_lines":3}
    check(all(cov.get(k)==v for k,v in expected.items()), "RESULT coverage")
    for name in OUTPUTS:
        check(GENERIC.search((ART/name).read_text(encoding="utf-8")) is None, f"no generic filler:{name}")

    manifest=json.loads((ROOT/BASE/"experiment.json").read_text())
    for field in ("inputs","outputs"):
        for item in manifest.get(field,[]):
            if isinstance(item,dict) and item.get("path") and item.get("sha256"):
                p=ROOT/item["path"]; check(p.is_file() and sha(p)==item["sha256"], f"manifest {field} hash:{item['path']}")

    payload={"schema":"GDT640_INDEPENDENT_VALIDATION_V1","experiment_id":"GDT640","status":"PASS" if not issues else "FAIL","checks_passed":len(passed),"issues":issues,"validated_result_sha256":sha(ART/"RESULT.json"),"validator_sha256":sha(Path(__file__))}
    VALIDATION.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"GDT640 validation: {payload['status']} checks={len(passed)} issues={len(issues)}")
    for issue in issues: print("FAIL:",issue)
    return 0 if not issues else 1


if __name__ == '__main__':
    raise SystemExit(main())
