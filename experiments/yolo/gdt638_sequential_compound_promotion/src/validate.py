#!/usr/bin/env python3
"""Independently validate and byte-replay GDT638."""
from __future__ import annotations
import csv, hashlib, io, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.dont_write_bytecode = True

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists(): return candidate
    raise RuntimeError("VManus repository root not found")

ROOT=find_repo_root(Path(__file__).resolve()); BASE_REL=Path("experiments/yolo/gdt638_sequential_compound_promotion")
BASE=ROOT/BASE_REL; ART=BASE/"artifacts"; RUN=BASE/"src/run.py"; MANIFEST=BASE/"experiment.json"
RESULT=ART/"RESULT.json"; VALIDATION=ART/"VALIDATION.json"
G637=ROOT/"experiments/yolo/gdt637_ladder_completion_one_unknown_passages/artifacts"
V14=G637/"WORKING_DICTIONARY_V14.tsv"; G637_GLOSSARY=G637/"V14_EXACT_TOKEN_GLOSSARY.tsv"
G637_COVERAGE=G637/"ALL_LINE_CONCRETE_COVERAGE.tsv"; G637_COMPLETE=G637/"COMPLETE_PASSAGE_CANDIDATES.tsv"; G637_ALLOW=G637/"PAGE_ALLOWLIST.tsv"
TOKENS_REL=Path("transcription/voynich_zl3b_tokens.tsv")
TSV_NAMES=("PAGE_ALLOWLIST.tsv","PROMOTION_CANDIDATE_DECK.tsv","ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv","SEQUENTIAL_PROMOTION_LEDGER.tsv","ROUND_COVERAGE_COUNTS.tsv","ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv","HELD_REJECTED_CANDIDATES.tsv","NEWLY_COMPLETED_LINES.tsv","V15_EXACT_TOKEN_GLOSSARY.tsv","ALL_LINE_CONCRETE_COVERAGE_V15.tsv","COMPLETE_PASSAGES_V15.tsv","ONE_UNKNOWN_PASSAGES_V15.tsv","WORKING_DICTIONARY_V15.tsv")
GENERATED=tuple(ART/n for n in TSV_NAMES)+(RESULT,)
ORDER=("cthoiin","choiin","cthey","cthor","qotchol","otchol","kcho","chkaiin","chtain","doiin","dol","oaiir","qoky","keechy","chokshy")
OCC=(2,13,38,43,13,27,7,16,4,11,76,4,138,3,1); ACCEPTED=ORDER[:13]; HELD=ORDER[13:]
PREDICTED={"laiir","poiiin","paim","raim","laim","paiim","raiim","laiim"}
BARE={"ar","chey","al","y","air","chdy","oiin","shey","am","cheey","chy","olchedy","chol","odaiin","oraiin","ody","cheo","oaiin","oral","aiir","oiiin","aim","aiim"}
STATES={"KNOWN_EXACT_WHOLE","KNOWN_CONTEXT_LICENSED","AMBIGUOUS_ACTIVE_RIVAL","UNKNOWN_SURFACE","READER_BOUNDARY_UNSTABLE"}
VERDICTS={"CONSISTENT_CONCRETE","OPAQUE_CONTEXT","READER_BOUNDARY_WARNING","HARD_CONTRADICTION","NONSENSE"}
FILLER=re.compile(r"arbeitsgut|arbeitschritt|arbeitsschritt|arbeitsmittel|arbeitsstoff|arbeitsobjekt|werkzeug|produkt weiter|f(?:ü|ue)hre .* aus|leite .* weiter|\b(?:arbeite|prozessiere|verarbeite)\b|nimm\s+werkzeug|bring\s+das\s+produkt",re.I)

def read_tsv(path):
    with Path(path).open(encoding="utf-8",newline="") as h: return list(csv.DictReader(h,delimiter="\t"))
def sha256(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value): return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def dhash(rows): return canonical(rows)
def pipes(value): return value.split(" | ") if value else []
def guarded_tokens(pages):
    cmd=[str(ROOT/"vmanus-exp"),"query-tsv",str(TOKENS_REL),"--selector","page"]
    for page in pages: cmd.extend(("--allow",page))
    cmd.extend(("--columns","page,locus,token_index,eva,section,language,hand","--forbid-prefix","f84","--forbid-prefix","f84r"))
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=False)
    if p.returncode: raise RuntimeError(p.stderr or "guarded token query failed")
    stats=[x for x in p.stderr.splitlines() if x.startswith("GUARD_STATS ")]
    if len(stats)!=1: raise RuntimeError("guard statistics missing")
    rows=list(csv.DictReader(io.StringIO(p.stdout),delimiter="\t"))
    if any(x["page"]=="f1r" or x["page"].startswith("f84") for x in rows): raise RuntimeError("protected page materialized")
    return rows,{k:int(v) for k,v in json.loads(stats[0][12:]).items()}

def main():
    checks=[]
    def check(ok,label):
        if not ok: raise AssertionError(label)
        checks.append(label)

    check(VALIDATION not in GENERATED,"validation excluded from replay"); check(len(GENERATED)==14 and len(set(GENERATED))==14,"fourteen unique builder outputs"); check(all(p.is_file() for p in GENERATED),"all builder outputs exist")
    before={p:p.read_bytes() for p in GENERATED}; replay=subprocess.run([sys.executable,str(RUN)],cwd=ROOT,text=True,capture_output=True,check=False)
    check(replay.returncode==0,"builder exits zero"); check(replay.stdout.strip()=="GDT638 built: candidates=15 accepted=13 held=2 audits=396 complete=30 strict=20 one_unknown=62","builder summary exact")
    for p in GENERATED: check(p.read_bytes()==before[p],f"byte replay {p.name}")

    result=json.loads(RESULT.read_text()); check(result["schema"]=="GDT638_SEQUENTIAL_COMPOUND_PROMOTION_RESULT_V1","result schema"); check(result["experiment_id"]=="GDT638","experiment id"); check(result["status"]=="PASS_13_EXACT_COMPOUNDS_PROMOTED__14_NEW_COMPLETE_LINES__2_HELD","result status")
    core={k:v for k,v in result.items() if k!="content_sha256"}; check(result["content_sha256"]==canonical(core),"canonical result hash")
    guard=result["guard"]; check(guard["allowed_pages"]==179 and guard["new_pages"]==guard["new_images"]==0,"unchanged 179-page scope"); check(guard["f1r"]=="EXCLUDED","f1r excluded"); check(guard["f84"]==guard["f84r"]=="FORBIDDEN","f84 family forbidden")
    source=RUN.read_text(); check(source.count("guarded_query(")==2,"two guarded source projections"); check("read_tsv(ROOT / TOKENS_REL)" not in source and "read_tsv(ROOT / CROSS_REL)" not in source,"mixed transcription not parsed directly")
    for path,digest in sorted(result["inputs"].items()): check((ROOT/path).is_file(),f"input exists {path}"); check(sha256(ROOT/path)==digest,f"input hash {path}")
    expected={str(BASE_REL/"artifacts"/n) for n in TSV_NAMES}; check(set(result["outputs"])==expected,"result binds every evidence TSV")
    for path,digest in sorted(result["outputs"].items()): check((ROOT/path).is_file(),f"output exists {path}"); check(sha256(ROOT/path)==digest,f"output hash {path}")
    manifest=json.loads(MANIFEST.read_text()); check(manifest["experiment_id"]=="GDT638","manifest experiment id"); check(manifest["sealed_data"]["f84"]==manifest["sealed_data"]["f84r"]=="FORBIDDEN","manifest seals f84 family")
    for group in ("inputs","outputs"):
        for item in manifest.get(group,[]): p=ROOT/item["path"]; check(p.is_file(),f"manifest {group} exists {item['path']}"); check(sha256(p)==item["sha256"],f"manifest {group} hash {item['path']}")

    allow=read_tsv(ART/"PAGE_ALLOWLIST.tsv"); pages=[r["page"] for r in allow]; check(len(pages)==len(set(pages))==179 and pages==sorted(pages),"179 sorted unique pages"); check((ART/"PAGE_ALLOWLIST.tsv").read_bytes()==G637_ALLOW.read_bytes(),"allowlist inherited byte-identically"); check("f1r" not in pages and all(not p.startswith("f84") for p in pages),"protected pages absent")
    deck=read_tsv(ART/"PROMOTION_CANDIDATE_DECK.tsv"); check(len(deck)==15,"fifteen candidates"); check(tuple(r["surface"] for r in deck)==ORDER,"candidate order exact"); check([int(r["candidate_order"]) for r in deck]==list(range(1,16)),"candidate ordinals consecutive"); check(tuple(int(r["occurrences"]) for r in deck)==OCC,"candidate occurrence counts exact"); check(tuple(r["decision"] for r in deck)==("ACCEPT",)*13+("HOLD",)*2,"accepted and held sets exact"); check(all(r["admission_barrier"]=="NONE" for r in deck[:13]),"accepted barriers absent"); check(tuple(r["admission_barrier"] for r in deck[13:])==("FIELD_ORDER_AMBIGUITY","INTERNAL_DRY_MOIST_SCOPE_COLLISION"),"held barriers exact"); check(not ({r["surface"] for r in deck}&(BARE|PREDICTED|{"kyty"})),"no bare predicted or kyty candidate")
    for r in deck: check(bool(r["working_meaning_de"].strip()) and not FILLER.search(r["working_meaning_de"]),f"candidate concrete {r['surface']}")

    token_rows,stats=guarded_tokens(pages); check(stats==guard["token_query"],"guard token stats replay"); check(len(token_rows)==32339,"32339 guarded tokens")
    lines=defaultdict(list)
    for r in token_rows: lines[r["locus"]].append(r)
    source_occ=Counter()
    for locus,members in lines.items():
        members.sort(key=lambda r:int(r["token_index"]))
        for ordinal,r in enumerate(members,1):
            if r["eva"] in ORDER: source_occ[(r["eva"],r["page"],locus,ordinal)]+=1
    check(sum(source_occ.values())==396,"396 guarded occurrences"); check(tuple(sum(n for k,n in source_occ.items() if k[0]==s) for s in ORDER)==OCC,"guarded surface census")
    audits=read_tsv(ART/"ALL_OCCURRENCE_SEMANTIC_AUDIT.tsv"); check(len(audits)==len({r["audit_id"] for r in audits})==396,"396 unique audits"); audit_occ=Counter((r["surface"],r["page"],r["locus"],int(r["token_ordinal"])) for r in audits); check(audit_occ==source_occ,"audit multiset equals guarded source")
    round_of={r["surface"]:int(r["candidate_order"]) for r in deck}
    for r in audits:
        surface,locus,ordinal=r["surface"],r["locus"],int(r["token_ordinal"]); members=lines[locus]
        check(int(r["round"])==round_of[surface],f"audit round {r['audit_id']}"); check(members[ordinal-1]["eva"]==surface,f"audit alignment {r['audit_id']}")
        pos="FIRST" if ordinal==1 else "LAST" if ordinal==len(members) else "MIDDLE"; check(r["line_position"]==pos,f"audit position {r['audit_id']}")
        prev="<BOS>" if ordinal==1 else members[ordinal-2]["eva"]; foll="<EOS>" if ordinal==len(members) else members[ordinal]["eva"]; check(r["previous"]==prev and r["following"]==foll,f"audit neighbours {r['audit_id']}")
        check(r["verdict"] in VERDICTS and bool(r["review_reason"].strip()),f"audit verdict {r['audit_id']}"); check(r["before_state"]=="UNKNOWN_SURFACE" and r["before_gloss"]==f"[{surface}:?]",f"audit starts unknown {r['audit_id']}"); check(r["after_gloss"]==deck[int(r["round"])-1]["working_meaning_de"],f"audit trial meaning {r['audit_id']}"); check(not FILLER.search(r["local_after_de"]),f"audit concrete {r['audit_id']}")
    verdicts=Counter(r["verdict"] for r in audits); check(verdicts==Counter({"CONSISTENT_CONCRETE":85,"OPAQUE_CONTEXT":260,"READER_BOUNDARY_WARNING":50,"HARD_CONTRADICTION":1}),"verdict census exact")

    ledger=read_tsv(ART/"SEQUENTIAL_PROMOTION_LEDGER.tsv"); rounds=read_tsv(ART/"ROUND_COVERAGE_COUNTS.tsv"); check(len(ledger)==15 and len(rounds)==16,"ledger and coverage rounds"); check([int(r["round"]) for r in ledger]==list(range(1,16)),"ledger rounds consecutive"); check([int(r["round"]) for r in rounds]==list(range(16)) and rounds[0]["surface"]=="BASE_V14","coverage rounds consecutive")
    v14=read_tsv(V14); check(len(v14)==259,"V14 259 rows"); check(rounds[0]["dictionary_sha256"]==dhash(v14),"base dictionary hash independent")
    defaults=read_tsv(ART/"ACCEPTED_WHOLE_SURFACE_DEFAULTS.tsv"); check(tuple(r["surface"] for r in defaults)==ACCEPTED,"accepted defaults exact"); by_default={r["surface"]:r for r in defaults}
    prior_hash=rounds[0]["dictionary_sha256"]; prior_entries=259; pk=int(rounds[0]["known_token_positions"]); pu=int(rounds[0]["unknown_token_positions"]); pc=int(rounds[0]["complete_multi_token_lines"]); tail=[]
    for i,r in enumerate(ledger,1):
        surface,decision=r["surface"],r["decision"]; rr=rounds[i]; check(surface==ORDER[i-1]==rr["surface"],f"round surface {i}"); check(r["pre_dictionary_sha256"]==prior_hash and int(r["pre_dictionary_entries"])==prior_entries,f"pre hash chain {i}"); check(int(r["occurrences"])==int(r["audited_occurrences"])==OCC[i-1],f"all audited {i}")
        vc=Counter(x["verdict"] for x in audits if int(x["round"])==i)
        for field,key in (("consistent_concrete","CONSISTENT_CONCRETE"),("opaque_context","OPAQUE_CONTEXT"),("reader_boundary_warning","READER_BOUNDARY_WARNING"),("hard_contradiction","HARD_CONTRADICTION"),("nonsense","NONSENSE")): check(int(r[field])==vc[key],f"{field} round {i}")
        if decision=="ACCEPT":
            check(surface in ACCEPTED and int(r["hard_contradiction"])==int(r["nonsense"])==0,f"accepted no veto {i}"); check(int(r["reader_exact_occurrences"])>0 and int(r["marginal_complete"])>=1,f"accepted anchor and gain {i}")
            tail.append({k:by_default[surface][k] for k in ("entry","kind","working_meaning_de","composition","context_rule","status")}); prior_entries+=1; expected=dhash([*v14,*tail])
        else:
            check(surface in HELD and decision=="HOLD",f"held set {i}"); check(int(r["marginal_complete"])==int(r["marginal_strict_complete"])==0,f"held unapplied {i}"); expected=prior_hash
        check(int(r["post_dictionary_entries"])==prior_entries and r["post_dictionary_sha256"]==expected==rr["dictionary_sha256"],f"post hash chain {i}"); check(int(rr["dictionary_entries"])==prior_entries,f"round entries {i}")
        nk,nu,nc=int(rr["known_token_positions"]),int(rr["unknown_token_positions"]),int(rr["complete_multi_token_lines"]); check(nk>=pk and nu<=pu and nc>=pc and nk+nu==32339,f"monotone round {i}"); prior_hash,pk,pu,pc=expected,nk,nu,nc
    held=read_tsv(ART/"HELD_REJECTED_CANDIDATES.tsv"); check(tuple(r["surface"] for r in held)==HELD and all(r["decision"]=="HOLD" and r["veto_codes"]!="NONE" for r in held),"held artifact exact")

    dictionary=read_tsv(ART/"WORKING_DICTIONARY_V15.tsv"); check(len(dictionary)==272 and dictionary[:259]==v14,"V14 exact prefix"); check(dictionary[259:]==tail,"V15 sequential tail"); check(dhash(dictionary)==prior_hash,"final dictionary hash"); surfaces={r["entry"].split("@",1)[0] for r in dictionary[259:]}; check(surfaces==set(ACCEPTED) and not(surfaces&(BARE|PREDICTED|{"kyty"})),"tail surfaces exact and safe")
    for r in dictionary[259:]: check(r["kind"]=="EXACT_WHOLE_SURFACE_PROMOTION" and "exact complete surface only" in r["context_rule"] and "no substring, bare-body or absent-cell transfer" in r["context_rule"],f"whole scope {r['entry']}"); check(not FILLER.search(r["working_meaning_de"]),f"dictionary concrete {r['entry']}")
    bg={r["surface"]:r for r in read_tsv(G637_GLOSSARY)}; grows=read_tsv(ART/"V15_EXACT_TOKEN_GLOSSARY.tsv"); glossary={r["surface"]:r for r in grows}; check(len(bg)==212 and len(glossary)==225,"212 to 225 glossary"); check(all(glossary[s]==r for s,r in bg.items()),"V14 glossary preserved"); check(set(glossary)-set(bg)==set(ACCEPTED),"glossary additions exact")
    for s in ACCEPTED: check(glossary[s]["working_meaning_de"]==by_default[s]["working_meaning_de"] and glossary[s]["scope_state"]=="KNOWN_EXACT_WHOLE",f"glossary row {s}")

    base_rows=read_tsv(G637_COVERAGE); coverage=read_tsv(ART/"ALL_LINE_CONCRETE_COVERAGE_V15.tsv"); check(len(coverage)==len({r["locus"] for r in coverage})==4128,"4128 final lines"); base={r["locus"]:r for r in base_rows}; final={r["locus"]:r for r in coverage}; check(set(base)==set(final),"coverage loci unchanged"); changed=0
    for r in coverage:
        locus=r["locus"]; b=base[locus]; count=int(r["token_count"]); known,unknown=int(r["known_tokens"]),int(r["unknown_tokens"]); check(r["page"] in pages and known+unknown==count,f"coverage partition {locus}")
        tokens=r["zl3b_line"].split(); gl,st,so=pipes(r["token_glosses_de"]),pipes(r["scope_states"]),pipes(r["gloss_sources"]); bgl,bst,bso=pipes(b["token_glosses_de"]),pipes(b["scope_states"]),pipes(b["gloss_sources"]); check(len(tokens)==len(gl)==len(st)==len(so)==count,f"coverage vectors {locus}"); check(set(st)<=STATES and st.count("UNKNOWN_SURFACE")==unknown,f"coverage states {locus}"); check(not FILLER.search(r["token_glosses_de"]),f"coverage concrete {locus}")
        for j,s in enumerate(tokens):
            if s in ACCEPTED: check(bst[j]=="UNKNOWN_SURFACE" and st[j] in {"KNOWN_EXACT_WHOLE","READER_BOUNDARY_UNSTABLE"} and so[j].startswith("GDT638:ROUND_"),f"accepted change {locus}:{j+1}"); changed+=1
            else: check((gl[j],st[j],so[j])==(bgl[j],bst[j],bso[j]),f"preserved position {locus}:{j+1}")
    check(changed==sum(OCC[:13])==392,"392 exact changed positions")
    complete=read_tsv(ART/"COMPLETE_PASSAGES_V15.tsv"); one=read_tsv(ART/"ONE_UNKNOWN_PASSAGES_V15.tsv"); check(len(complete)==30 and sum(int(r["strict_complete"]) for r in complete)==20,"30 complete 20 strict"); check(len(one)==62 and sum(int(r["strict_eligible"]) for r in one)==24,"62 one-hole 24 strict"); check([int(r["rank"]) for r in complete]==list(range(1,31)) and [int(r["rank"]) for r in one]==list(range(1,63)),"final ranks consecutive")
    for r in complete: check(int(r["unknown_tokens"])==0 and int(r["known_tokens"])==int(r["token_count"]) and not re.search(r"\[[a-z]+:\?\]",r["working_translation_de"]) and not FILLER.search(r["working_translation_de"]),f"complete concrete {r['locus']}")
    for r in one: check(int(r["unknown_tokens"])==1,f"one-hole exact {r['locus']}")
    old_complete={r["locus"] for r in read_tsv(G637_COMPLETE)}; newset={r["locus"] for r in complete}-old_complete; newly=read_tsv(ART/"NEWLY_COMPLETED_LINES.tsv"); check(len(newset)==len(newly)==14 and {r["locus"] for r in newly}==newset,"14 exact new loci"); check(len({r["locus"] for r in newly})==14,"new loci unique")
    for r in newly: check(r["surface"] in ACCEPTED and not FILLER.search(r["literal_after_de"]) and not FILLER.search(r["smoothed_working_reading_de"]),f"new line concrete {r['locus']}")

    run=result["candidate_run"]; check((run["candidates"],run["accepted"],run["held"],run["audited_occurrences"])==(15,13,2,396),"result candidate census"); check(tuple(run["accepted_surfaces"])==ACCEPTED and tuple(run["held_surfaces"])==HELD,"result decisions"); check(Counter(run["verdicts"])==verdicts,"result verdict census")
    m=result["coverage"]; check((m["physical_lines"],m["complete_multi_token_lines"],m["strict_complete_lines"],m["one_unknown_lines"],m["newly_completed_lines"],m["exact_glossary_surfaces"])==(4128,30,20,62,14,225),"result coverage census"); check((m["known_token_positions"],m["unknown_token_positions"])==(9259,23080),"result token census")
    w=result["working_dictionary"]; check((w["v14_entries"],w["v15_entries"],w["accepted_tail_entries"])==(259,272,13),"result dictionary census"); check(w["v14_prefix_sha256"]==dhash(v14) and w["v15_sha256"]==dhash(dictionary),"result dictionary hashes")

    vcore={"schema":"GDT638_VALIDATION_V1","experiment_id":"GDT638","status":"PASS","checks":len(checks),"builder_outputs_replayed":len(GENERATED),"candidates":15,"accepted":13,"held":2,"audited_occurrences":396,"physical_lines":4128,"complete_multi_token_lines":30,"strict_complete_lines":20,"one_unknown_lines":62,"newly_completed_lines":14,"dictionary_entries":272,"validated_claim":"Fifteen exact whole-surface candidates were processed sequentially over every guarded occurrence. Thirteen accepted cards preserve V14 as an exact prefix and add fourteen complete lines; two held cards change neither the hash chain nor the final reader."}
    validation={**vcore,"content_sha256":canonical(vcore)}; VALIDATION.write_text(json.dumps(validation,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"GDT638 validation PASS: {len(checks)} checks, {len(GENERATED)} outputs replayed"); return 0

if __name__=="__main__": raise SystemExit(main())
