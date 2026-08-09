#!/usr/bin/env python3
"""Restore and exact-check the public voynich.nu quire catalogue snapshot."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
CACHE = BASE / "cache" / "public_voynich_nu_catalogue"
OLD = BASE / "results" / "existing_human_page_annotations.tsv"
METHOD = BASE / "PUBLIC_VOYNICH_NU_CATALOGUE_REFRESH_METHOD.md"
OUT = BASE / "results" / "public_voynich_nu_catalogue_refresh.json"
REPORT = BASE / "results" / "public_voynich_nu_catalogue_refresh_report.md"
EXPECTED = {
    "q01":"6c82ec816e5b4b320d87551af34eaec768531e32bde00afc4415652f5ddc10a4",
    "q02":"62dacc593854f9de724820c427ee5285492084b08839684fe59143ff2e95c89a",
    "q03":"c43ff6e75e0d6db22a6c7e887101f3d1045f8a72878717e733c10ec93ce65ab3",
    "q04":"c4e5921c0f6d312f8b73ec9a4a3e09cee0089ff7d53c1f279a24066a8c830dbd",
    "q05":"48d3ee83bde2ffffa8a95770f5ca54ae996f340d81080e4024f9f94581d7f3ed",
    "q06":"bd377ccecf0c472e4b7965f9885b130943be6c98097b33fa5486c592cf133beb",
    "q07":"69af3fe68a574e4ac12e1af5eddf46c642d0ffa52b36b0fa577d3676294c2b1f",
    "q08":"ce3df63cb48cf440faa2d637b382b7665b992a55709b5a721fdce078e21e42d7",
    "q09":"56b592284239fbd4d2ffabac2c534207c2e8a6da00ce4570d526544b9793f977",
    "q10":"2f15159cd9ea04213f2031fbbebe33e3b057795656e349bf765e4f0344ff2ec5",
    "q11":"5553f82d3c7d016c3a9f7853388e844764239f929cdd24f2870a1d56b172ad64",
    "q12":"3a9b4e587c9b9d0228bf87eea1b3a0e34f3fcfe4abafd71e712213e0af9132b6",
    "q13":"424956a525b3bc0cf63aee266e8fd92c3c8c98c3f6d36427eeb3f62085ad6437",
    "q14":"a7f48085a58fec9d2e842665f74424a42a9a0524f8c9e7589616c15b2a667a4f",
    "q15":"25a8bb0083a2c6c09913910c52d03a699091c100294f8fe3c604e3846253f3a7",
    "q17":"5b5f1743df54e5e0b5f3e1e60e994870b237a3722122b8c6ce7be9121d6a24dd",
    "q19":"119fe32a005723833ec07a313fd87e1cd044a1f685ddd4fdd199e573c1dff1fb",
    "q20":"322002b8c8da66a5f1d2d4c05ab4e4bfca8233bb05751fbac5a7be88cea33201",
}
FIELDS = {
    "general description":"general_description", "illustration(s)":"illustrations",
    "text":"text_description", "tentative identifications":"tentative_identifications",
    "other information":"other_information",
}
PAGE_RE = re.compile(r"f\d+[rv]\d*", re.I)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def norm(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(parts).replace("\xa0", " ")).strip()


class Parser(HTMLParser):
    def __init__(self, quire: str) -> None:
        super().__init__(convert_charrefs=True); self.quire=quire; self.page=""; self.heading=""; self.capture=""; self.parts=[]; self.records={}
    def handle_starttag(self, tag, attrs):
        a={k.lower():v for k,v in attrs}; tag=tag.lower()
        if tag=="th" and a.get("id") and PAGE_RE.fullmatch(str(a["id"]).lower()):
            self.page=str(a["id"]).lower(); self.records.setdefault(self.page,{"page":self.page,"quire":self.quire,**{f:[] for f in FIELDS.values()}})
        if tag in {"h4","p"}: self.capture=tag; self.parts=[]
        elif tag=="br" and self.capture:self.parts.append(" ")
    def handle_data(self,data):
        if self.capture:self.parts.append(data)
    def handle_endtag(self,tag):
        tag=tag.lower()
        if tag!=self.capture:return
        text=norm(self.parts); self.capture=""; self.parts=[]
        if tag=="h4":self.heading=text.lower(); return
        field=FIELDS.get(self.heading)
        if field and self.page and text and text.lower() not in {"&nbsp;","none"}:self.records[self.page][field].append(text)


def fetch(source_id: str) -> tuple[str, bytes]:
    url=f"https://www.voynich.nu/{source_id}/index.html"
    request=urllib.request.Request(url,headers={"User-Agent":"VManus public-catalogue provenance refresh"})
    with urllib.request.urlopen(request,timeout=45) as response:return source_id,response.read()


def main() -> None:
    if OUT.exists() or REPORT.exists():raise SystemExit("refusing overwrite")
    if sha(OLD)!="b358f244cbe853448dd5c32dbc04004cb8ce63d9a8c5ed5afe2a679a115d87fa":raise SystemExit("stored page atlas drift")
    with ThreadPoolExecutor(max_workers=18) as pool:
        downloaded=dict(pool.map(fetch,EXPECTED))
    for source_id,data in downloaded.items():
        if sha_bytes(data)!=EXPECTED[source_id]:raise SystemExit(f"upstream drift: {source_id}")
    CACHE.mkdir(parents=True,exist_ok=True)
    for source_id,data in downloaded.items():
        path=CACHE/f"{source_id}.html"
        if path.exists():
            if path.read_bytes()!=data:raise SystemExit(f"cache collision: {source_id}")
        else:
            with path.open("xb") as handle:handle.write(data)
    records={}; sources=[]
    for source_id in EXPECTED:
        data=downloaded[source_id]; parser=Parser(source_id); parser.feed(data.decode("utf-8",errors="replace"))
        sources.append({"source_id":source_id,"url":f"https://www.voynich.nu/{source_id}/index.html","bytes":len(data),"sha256":sha_bytes(data),"pages":len(parser.records)})
        for page,row in parser.records.items():
            target=records.setdefault(page,{"page":page,"quire":source_id,**{f:[] for f in FIELDS.values()}})
            for field in FIELDS.values():target[field].extend(row[field])
    for row in records.values():
        for field in FIELDS.values():row[field]=" || ".join(dict.fromkeys(row[field]))
    with OLD.open(encoding="utf-8",newline="") as handle:old={row["page"]:row for row in csv.DictReader(handle,delimiter="\t")}
    diffs=[]
    for page in sorted(set(records)&set(old)):
        for field in ("quire",*FIELDS.values()):
            if records[page][field]!=old[page][field]:diffs.append({"page":page,"field":field,"old":old[page][field],"live":records[page][field]})
    gates={
        "exact_18_public_source_hashes":len(sources)==18 and all(item["sha256"]==EXPECTED[item["source_id"]] for item in sources),
        "exact_228_page_records":len(records)==len(old)==228,
        "no_added_or_missing_page_ids":set(records)==set(old),
        "zero_exact_description_field_differences":not diffs,
        "image_ocr_or_vision_used":False,
        "semantic_or_grammar_score_computed":False,
    }
    if not all(v for k,v in gates.items() if k not in {"image_ocr_or_vision_used","semantic_or_grammar_score_computed"}) or gates["image_ocr_or_vision_used"] or gates["semantic_or_grammar_score_computed"]:raise SystemExit("refresh gate failure")
    result={
        "experiment":"PUBLIC_VOYNICH_NU_CATALOGUE_REFRESH",
        "status":"PASS_18_PUBLIC_SOURCES_228_PAGES_ZERO_DESCRIPTION_DRIFT",
        "decision":"RESTORE_PUBLIC_PROVENANCE_NO_NEW_SEMANTIC_ANCHOR",
        "inputs":{OLD.name:sha(OLD),METHOD.name:sha(METHOD),Path(__file__).name:sha(Path(__file__).resolve())},
        "sources":sources,"page_records":len(records),"compared_fields":["quire",*FIELDS.values()],"differences":diffs,"gates":gates,
        "claim_ceiling":"The restored public sources exactly reproduce the retained page-description atlas. No new relation, ownership, lexical key, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    REPORT.write_text("""# Public voynich.nu catalogue refresh

Status: **PASS_18_PUBLIC_SOURCES_228_PAGES_ZERO_DESCRIPTION_DRIFT**

All 18 live public quire pages match their previously registered SHA-256
values. Independent parsing reconstructs the same 228 page IDs and every
stored general-description, illustration, text, tentative-identification, and
other-information field with **zero differences**.

Decision: **RESTORE_PUBLIC_PROVENANCE_NO_NEW_SEMANTIC_ANCHOR**. The missing
public HTML snapshot is restored and the atlas builder now points to it. The
live catalogue supplies no new description or one-to-one lexical key. No OCR,
automated vision, manuscript string, grammar score, meaning, plaintext, or
translation is involved.
""",encoding="utf-8")
    print(json.dumps({"status":result["status"],"sources":18,"pages":228,"differences":0},sort_keys=True))


if __name__=="__main__":main()
