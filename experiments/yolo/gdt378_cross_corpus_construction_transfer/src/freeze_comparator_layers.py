#!/usr/bin/env python3
"""Build form-blind GDT378 observations and hidden labels before scoring."""
from __future__ import annotations
import csv, gzip, hashlib, html, io, json, os, re, unicodedata
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "experiments/yolo/gdt378_cross_corpus_construction_transfer"
ART = BASE / "artifacts"
SOURCE_FREEZE = ART / "gdt378_source_freeze.json"
CONTRACT = ART / "gdt378_oracle_contract.json"
ENDPOINTS = ["HEAD_WITH_DEPENDENTS","HIGH_VALENCY_HEAD","REF_ANAPHORA","CORRELATIVE_MEMBER",
             "NEXT_RESUME","UNTIL_STATE_GATE","COORDINATOR","ALTERNATIVE_OR","POLARITY_EXCLUSION",
             "COMPARISON","FUNCTION_WORD","STATE_TRANSITION","CLOSER"]

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def opaque(domain: str, value: str) -> str:
    return hashlib.sha256(("GDT378_OPAQUE_ID_V1\0"+domain+"\0"+value).encode()).hexdigest()[:24]
def read_tsv(path: Path) -> list[dict[str,str]]:
    opener=gzip.open if path.suffix==".gz" else open
    with opener(path,"rt",encoding="utf-8",newline="") as handle: return list(csv.DictReader(handle,delimiter="\t"))
def write_tsv(path: Path, rows: list[dict[str,object]]) -> None:
    if path.suffix==".gz":
        raw=path.open("wb"); gz=gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0); handle=io.TextIOWrapper(gz,encoding="utf-8",newline="")
    else: handle=path.open("w",encoding="utf-8",newline="")
    with handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");writer.writeheader();writer.writerows(rows)
def content_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def canon(token: str) -> str:
    token=html.unescape(token).lower().replace("[th]","þ").replace("[gh]","ȝ")
    token=token.replace("þ","th").replace("ð","th").replace("ȝ","y")
    token=unicodedata.normalize("NFKD",token)
    return "".join(ch for ch in token if ch.isalpha())

def tokenize(text: str) -> list[str]:
    text=text.replace("[th]","þ").replace("[gh]","ȝ")
    return re.findall(r"[^\W\d_]+(?:-[^\W\d_]+)*|&",html.unescape(text),flags=re.UNICODE)

class ParagraphParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__();self.in_p=False;self.depth=0;self.cur=[];self.paragraphs=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="p" and "paragraph" in attrs.get("class","").split(): self.in_p=True;self.depth=1;self.cur=[]
        elif self.in_p:
            if tag=="br": self.cur.append("\n")
            else: self.depth+=1
    def handle_startendtag(self,tag,attrs):
        if self.in_p and tag=="br": self.cur.append("\n")
    def handle_endtag(self,tag):
        if self.in_p:
            self.depth-=1
            if tag=="p" and self.depth==0:
                self.paragraphs.append("".join(self.cur));self.in_p=False
    def handle_data(self,data):
        if self.in_p:self.cur.append(data)

def sexprs(text: str):
    stack=[]
    for match in re.finditer(r"\(|\)|[^\s()]+",text):
        tok=match.group()
        if tok=="(": stack.append([])
        elif tok==")":
            if not stack: continue
            node=stack.pop()
            if stack: stack[-1].append(node)
            else: yield node
        elif stack: stack[-1].append(tok)

def label(node) -> str:
    return node[0] if isinstance(node,list) and node and isinstance(node[0],str) else ""

def terminal_rows(node, ancestors=(), out=None):
    if out is None: out=[]
    if not isinstance(node,list) or not node:return out
    tag=label(node)
    if len(node)==2 and isinstance(node[1],str):
        out.append({"pos":tag,"token":node[1],"ancestors":ancestors,"node":node})
    else:
        for child in node[1:] if tag else node:
            if isinstance(child,list):terminal_rows(child,ancestors+(tag,),out)
    return out

LEXICAL_VERB=("VB","VAN","VAG","VBN","VBI")
AUXILIARY=("MD","BE","BEP","BED","BEN","BAG","HV","HVP","HVD","HVN","DO","DOP","DOD")
DEPENDENT=("NP","PP","ADJP","ADVP","CP","RP")

def pceec_heads(node, terminals, head=set(), high=set()):
    if not isinstance(node,list) or not node:return head,high
    tag=label(node)
    if tag.startswith("IP"):
        candidates=[];aux=[];deps=0
        for child in node[1:]:
            if not isinstance(child,list):continue
            ct=label(child)
            if ct.startswith("IP"):continue
            if ct.startswith(DEPENDENT):deps+=1
            leaves=terminal_rows(child)
            candidates.extend(x for x in leaves if x["pos"].startswith(LEXICAL_VERB))
            aux.extend(x for x in leaves if x["pos"].startswith(AUXILIARY))
        selected=candidates if candidates else aux[-1:]
        if deps:
            ids={id(x["node"]) for x in selected};head.update(ids)
            if deps>=2:high.update(ids)
    for child in node[1:] if tag else node:
        if isinstance(child,list):pceec_heads(child,terminals,head,high)
    return head,high

def emit_record(obs,oracle,domain,collection,record_id,record_ordinal,tokens,labels,quality,page="",line_count=0):
    if len(tokens)<3:return
    if len(tokens)>180:
        for chunk,start in enumerate(range(0,len(tokens),180),1):
            part=tokens[start:start+180];partlabels={k:set(i-start for i in v if start<=i<start+180) for k,v in labels.items()}
            emit_record(obs,oracle,domain,collection,f"{record_id}:C{chunk}",record_ordinal*100+chunk,part,partlabels,quality,page,line_count)
        return
    n=len(tokens);counts=Counter(canon(x) for x in tokens)
    for j,tok in enumerate(tokens):
        c=canon(tok)
        if not c:continue
        key=f"{domain}:{collection}:{record_id}:{j+1}"
        obs.append({"element_key":key,"domain":domain,"collection_id":collection,"record_id":record_id,
                    "record_ordinal":record_ordinal,"element_ordinal":j+1,"opaque_form_id":opaque(domain,c),
                    "surface_length":len(c),"direct_token_count":1,"record_element_count":n,
                    "relative_position":f"{(j+1)/n:.9f}","physical_page":page,"physical_line_count":line_count,
                    "boundary_before":int(j==0),"boundary_after":int(j==n-1),"within_record_frequency":counts[c],
                    "source_quality":quality})
        row={"element_key":key,"domain":domain,"collection_id":collection,"record_id":record_id}
        for endpoint in ENDPOINTS:row[endpoint]=int(j in labels.get(endpoint,set()))
        oracle.append(row)

def procedural_labels(tokens,contract):
    norm=[canon(x) for x in tokens];lab={k:set() for k in ENDPOINTS};sets=contract["lexical_sets"]
    for i,w in enumerate(norm):
        if any(w.startswith(stem) for stem in contract["head_stems"]):lab["HEAD_WITH_DEPENDENTS"].add(i)
        for ep,values in sets.items():
            if w in values:lab[ep].add(i)
        if w in {"and"}:lab["FUNCTION_WORD"].add(i)
        if w in {"or","if","yif","then","thanne","until","til","till","tyl","not","nought","no","ne","without","withoute","except","thereof","therof","aforeseid","aforeseyd","foresaid","same"}:lab["FUNCTION_WORD"].add(i)
    if any(w in {"if","yif"} for w in norm) and any(w in {"then","thanne"} for w in norm):
        lab["CORRELATIVE_MEMBER"].update(i for i,w in enumerate(norm) if w in {"if","yif","then","thanne"})
    if sum(1 for w in norm if w in {"like","lyke","as","same"})>=2:
        lab["COMPARISON"].update(i for i,w in enumerate(norm) if w in {"like","lyke","as","same"})
    return lab

def add_corema(obs,oracle):
    source=read_tsv(ROOT/"experiments/yolo/gdt376_corema_hidden_function_oracle/artifacts/gdt376_observation_layer.tsv")
    gold=read_tsv(ROOT/"gdt176_corema_role_oracle.tsv");assert len(source)==len(gold)
    byrec=defaultdict(list)
    for i,r in enumerate(gold):byrec[(r["collection_id"],r["recipe_id"])].append((i,r))
    labels={i:{k:0 for k in ENDPOINTS} for i in range(len(gold))}
    for values in byrec.values():
        values.sort(key=lambda z:int(z[1]["element_ordinal"]));children=Counter(int(r["parent_instruction_ordinal"]) for _,r in values if int(r["parent_instruction_ordinal"])>0);instruction=0
        for i,r in values:
            role=r["role"];flag=r["annotation_flags"]
            if role=="INSTRUCTION":
                instruction+=1;labels[i]["HEAD_WITH_DEPENDENTS"]=int(children[instruction]>0);labels[i]["HIGH_VALENCY_HEAD"]=int(children[instruction]>=2)
            labels[i]["REF_ANAPHORA"]=int(role=="REF");labels[i]["ALTERNATIVE_OR"]=int(role=="ALTERNATIVE")
            labels[i]["UNTIL_STATE_GATE"]=int(role=="TIME");labels[i]["CLOSER"]=int(role=="CLOSER")
            labels[i]["POLARITY_EXCLUSION"]=int(flag=="exclusion");labels[i]["COMPARISON"]=int(flag in {"analogy","comparison"})
    for i,(r,g) in enumerate(zip(source,gold)):
        if r["observable_surface"]!="1":continue
        key=f'COREMA:{r["collection_id"]}:{r["recipe_id"]}:{r["element_ordinal"]}'
        obs.append({"element_key":key,"domain":"COREMA","collection_id":r["collection_id"],"record_id":r["recipe_id"],
                    "record_ordinal":r["recipe_ordinal"],"element_ordinal":r["element_ordinal"],
                    "opaque_form_id":opaque("COREMA",r["opaque_form_id"]),"surface_length":0,
                    "direct_token_count":r["direct_token_count"],"record_element_count":r["record_element_count"],
                    "relative_position":r["relative_position"],"physical_page":"","physical_line_count":0,
                    "boundary_before":int(r["element_ordinal"]=="1"),"boundary_after":int(r["element_ordinal"]==r["record_element_count"]),
                    "within_record_frequency":0,"source_quality":"EDITOR_GOLD"})
        row={"element_key":key,"domain":"COREMA","collection_id":r["collection_id"],"record_id":r["recipe_id"]}
        row.update(labels[i]);oracle.append(row)

def add_pceec(obs,oracle,cache,contract):
    for path in sorted((cache/"pceec2/data/parsed").glob("*.psd")):
        kept=0;ordinal=0
        for form in sexprs(path.read_text(encoding="utf-8",errors="replace")):
            roots=[x for x in form if isinstance(x,list) and label(x) not in {"CODE","METADATA","ID"}]
            if not roots:continue
            terminals=[]
            for root in roots:terminal_rows(root,(),terminals)
            visible=[x for x in terminals if x["pos"] not in {"PUNC","CODE","ID"} and canon(x["token"]) and not x["token"].startswith("*") and x["token"]!="0"]
            if len(visible)<3:continue
            node_to_index={id(x["node"]):j for j,x in enumerate(visible)};heads=set();high=set()
            for root in roots:pceec_heads(root,visible,heads,high)
            lab={k:set() for k in ENDPOINTS};lab["HEAD_WITH_DEPENDENTS"]={node_to_index[x] for x in heads if x in node_to_index};lab["HIGH_VALENCY_HEAD"]={node_to_index[x] for x in high if x in node_to_index}
            norm=[canon(x["token"]) for x in visible]
            for j,x in enumerate(visible):
                pos=x["pos"];w=norm[j];anc=x["ancestors"]
                if pos.startswith(("PRO","WPRO")):lab["REF_ANAPHORA"].add(j)
                if pos=="CONJ":lab["COORDINATOR"].add(j)
                if pos=="NEG":lab["POLARITY_EXCLUSION"].add(j)
                if "CP-CMP" in anc:lab["COMPARISON"].add(j)
                if pos.startswith(("D","P","C","CONJ","PRO","WPRO","NEG","MD","TO")):lab["FUNCTION_WORD"].add(j)
                for ep,values in contract["lexical_sets"].items():
                    if w in values:lab[ep].add(j)
            if any(w in {"if","yif"} for w in norm) and any(w in {"then","thanne"} for w in norm):lab["CORRELATIVE_MEMBER"].update(j for j,w in enumerate(norm) if w in {"if","yif","then","thanne"})
            ordinal+=1;kept+=1
            emit_record(obs,oracle,"PCEEC2",path.stem,f"{path.stem}:{ordinal}",ordinal,[x["token"] for x in visible],lab,"PARSE_GOLD")
            if kept>=int(contract["pceec_records_per_file"]):break

def add_curious(obs,oracle,cache,contract):
    page_meta={int(r["sequence"]):r for r in read_tsv(ART/"gdt378_curious_cures_page_manifest.tsv")}
    ordinal=0
    for path in sorted((cache/"curious_add9308").glob("*.html")):
        parser=ParagraphParser();parser.feed(path.read_text(encoding="utf-8"));seq=int(path.stem)
        for pidx,text in enumerate(parser.paragraphs,1):
            tokens=tokenize(text);lines=max(1,text.count("\n")+1)
            if len(tokens)<3:continue
            ordinal+=1;emit_record(obs,oracle,"CURIOUS_CURES","MS-ADD-09308",f"ADD9308:{seq}:{pidx}",ordinal,tokens,procedural_labels(tokens,contract),"DIPLOMATIC_HTR_ASSISTED",page_meta[seq]["folio_label"],lines)

def add_harleian(obs,oracle,cache,contract):
    text=(cache/"harleian_ia_ocr.txt").read_text(encoding="utf-8",errors="replace")
    paras=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n\s*\n",text)]
    b1=next(i for i,p in enumerate(paras) if "Lange Wortys de chare" in p and re.search(r"\bTake\b",p))
    split=next(i for i,p in enumerate(paras[b1+1:],b1+1) if "HAELEIAN MS. 4016" in p)
    b2=next(i for i,p in enumerate(paras[split+1:],split+1) if p.startswith("Cabochis") and re.search(r"\bTake\b",p))
    end=next(i for i,p in enumerate(paras[b2+1:],b2+1) if "ASHMOLE MS. 1439" in p)
    for collection,lo,hi in [("HARL279",b1,split),("HARL4016",b2,end)]:
        ordinal=0
        for p in paras[lo:hi]:
            if not re.search(r"\b[Tt]ake\b",p):continue
            tokens=tokenize(p)
            if len(tokens)<3:continue
            ordinal+=1;emit_record(obs,oracle,"HARLEIAN_COOKERY",collection,f"{collection}:{ordinal}",ordinal,tokens,procedural_labels(tokens,contract),"PUBLIC_DOMAIN_EDITION_OCR")

def add_quinte(obs,oracle,cache,contract):
    text=(cache/"quinte_17179.txt").read_text(encoding="utf-8",errors="replace")
    positions=[m.start() for m in re.finditer(r"(?m)^BOOK I\.?$",text)]
    start=positions[-1];end=text.find("*** END OF THE PROJECT GUTENBERG EBOOK",start);body=text[start:end]
    kept=[];skip=False
    for line in body.splitlines():
        if re.match(r"^\s*\[(?:Footnote|Page|\[\*)",line):skip=True
        if skip:
            if not line.strip():skip=False
            continue
        if re.match(r"^\s*\[",line):continue
        if re.match(r"^\s*\d+\s*$",line):continue
        kept.append(line)
    paras=[re.sub(r"\s+"," ",p).strip() for p in re.split(r"\n\s*\n","\n".join(kept))]
    ordinal=0;collection="BOOK1"
    for p in paras:
        tokens=tokenize(p)
        if len(tokens)<3:continue
        if re.search(r"\bBOOK II\b",p): collection="BOOK2"
        ordinal+=1
        emit_record(obs,oracle,"QUINTE_ESSENCE",collection,f"QUINTE:{ordinal}",ordinal,tokens,procedural_labels(tokens,contract),"PUBLIC_DOMAIN_EDITED_TRANSCRIPTION")

def main():
    cache_name=os.environ.get("GDT378_SOURCE_CACHE")
    if not cache_name:raise SystemExit("set GDT378_SOURCE_CACHE")
    cache=Path(cache_name);freeze=json.loads(SOURCE_FREEZE.read_text());contract=json.loads(CONTRACT.read_text())
    assert freeze["status"]=="COMPARATOR_SOURCES_FROZEN_BEFORE_SCORING" and not freeze["voynich_scored"]
    obs=[];oracle=[]
    add_corema(obs,oracle);add_pceec(obs,oracle,cache,contract);add_curious(obs,oracle,cache,contract);add_harleian(obs,oracle,cache,contract);add_quinte(obs,oracle,cache,contract)
    assert len(obs)==len(oracle) and len({r["element_key"] for r in obs})==len(obs)
    assert [r["element_key"] for r in obs]==[r["element_key"] for r in oracle]
    assert set(r["domain"] for r in obs)==set(freeze["included_domains"])
    obs_path=ART/"gdt378_comparator_observation_layer.tsv.gz";oracle_path=ART/"gdt378_hidden_oracle.tsv.gz"
    write_tsv(obs_path,obs);write_tsv(oracle_path,oracle)
    counts=[]
    availability=contract["availability"]
    for domain in freeze["included_domains"]:
        ids=[i for i,r in enumerate(oracle) if r["domain"]==domain]
        for endpoint in ENDPOINTS:
            counts.append({"domain":domain,"endpoint":endpoint,"oracle_available":int(domain in availability.get(endpoint,[])),
                           "rows":len(ids),"positives":sum(int(oracle[i][endpoint]) for i in ids) if domain in availability.get(endpoint,[]) else "",
                           "oracle_strength":"GOLD" if domain in {"COREMA","PCEEC2"} else "HIGH_PRECISION_LEXICAL"})
    coverage=ART/"gdt378_endpoint_coverage.tsv";write_tsv(coverage,counts)
    design={"schema":"GDT378_COMPARATOR_LAYER_FREEZE_V1","status":"FORM_BLIND_LAYERS_FROZEN_BEFORE_SCORING",
            "domains":freeze["included_domains"],"rows":len(obs),"records":len({(r["domain"],r["collection_id"],r["record_id"]) for r in obs}),
            "representations":["ABSOLUTE_PROBABILITY","WITHIN_RECORD_RANK","STRUCTURE_MINUS_NUISANCE_DELTA","DOMAIN_STANDARDIZED","SCOPE_HORIZON","NEIGHBOR_RECURRENCE","FIXED_RANK_COMBINATION"],
            "head_gate":{"required_domains":["COREMA","PCEEC2"],"minimum_other_medical_or_procedural_domains":1,"minimum_domain_auc":0.65,"positive_structure_gain":True,"max_family_p_max":0.05},
            "forbidden_observation_fields":["surface","word","translation","pos","parse","role","concept_id","function_label","parent_link"],
            "inputs":{"source_freeze":sha(SOURCE_FREEZE),"oracle_contract":sha(CONTRACT),"gdt376_observation":sha(ROOT/"experiments/yolo/gdt376_corema_hidden_function_oracle/artifacts/gdt376_observation_layer.tsv"),"corema_oracle":sha(ROOT/"gdt176_corema_role_oracle.tsv")},
            "outputs":{str(p.relative_to(ROOT)):sha(p) for p in [obs_path,oracle_path,coverage]},"voynich_scored":False,"voynich_rows_read":0,
            "f84":{"opened":False,"parsed":False,"retained":False,"scored":False},"implementation":{str((BASE/"src/freeze_comparator_layers.py").relative_to(ROOT)):sha(BASE/"src/freeze_comparator_layers.py")},
            "claim_ceiling":"FORM_BLIND_COMPARATOR_OBSERVATION_AND_HIDDEN_ORACLE_FREEZE_ONLY"}
    design["content_hash"]=content_hash(design);(ART/"gdt378_comparator_design_freeze.json").write_text(json.dumps(design,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"rows":len(obs),"records":design["records"],"domains":Counter(r["domain"] for r in obs)},default=dict))

if __name__=="__main__":main()
