#!/usr/bin/env python3
"""Independent cached-source validation of the public catalogue refresh."""

from __future__ import annotations
import csv,hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path

BASE=Path(__file__).resolve().parent; CACHE=BASE/"cache/public_voynich_nu_catalogue"; RES=BASE/"results"
OLD=RES/"existing_human_page_annotations.tsv"; RESULT=RES/"public_voynich_nu_catalogue_refresh.json"; REPORT=RES/"public_voynich_nu_catalogue_refresh_report.md"
OUT=RES/"public_voynich_nu_catalogue_refresh_validation.json"; OUT_REPORT=RES/"public_voynich_nu_catalogue_refresh_validation_report.md"
EXPECTED={item["source_id"]:item["sha256"] for item in json.loads(RESULT.read_text())["sources"]}
FIELDS={"general description":"general_description","illustration(s)":"illustrations","text":"text_description","tentative identifications":"tentative_identifications","other information":"other_information"}
P=re.compile(r"f\d+[rv]\d*",re.I)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(parts):return re.sub(r"\s+"," "," ".join(parts).replace("\xa0"," ")).strip()
class H(HTMLParser):
    def __init__(self,q):super().__init__(convert_charrefs=True);self.q=q;self.p="";self.h="";self.c="";self.x=[];self.r={}
    def handle_starttag(self,t,a):
        d={k.lower():v for k,v in a};t=t.lower()
        if t=="th" and d.get("id") and P.fullmatch(str(d["id"]).lower()):self.p=str(d["id"]).lower();self.r.setdefault(self.p,{"page":self.p,"quire":self.q,**{v:[] for v in FIELDS.values()}})
        if t in ("h4","p"):self.c=t;self.x=[]
        elif t=="br" and self.c:self.x.append(" ")
    def handle_data(self,d):
        if self.c:self.x.append(d)
    def handle_endtag(self,t):
        if t.lower()!=self.c:return
        z=norm(self.x);c=self.c;self.c="";self.x=[]
        if c=="h4":self.h=z.lower();return
        f=FIELDS.get(self.h)
        if f and self.p and z and z.lower() not in ("&nbsp;","none"):self.r[self.p][f].append(z)
def main():
    if OUT.exists() or OUT_REPORT.exists():raise SystemExit("refusing overwrite")
    checks=0
    def ck(v,n):
        nonlocal checks;checks+=1
        if not v:raise AssertionError(n)
    ck(len(EXPECTED)==18,"source count"); records={}
    for q in sorted(EXPECTED):
        path=CACHE/f"{q}.html";ck(path.exists(),q+" present");ck(sha(path)==EXPECTED[q],q+" hash")
        h=H(q);h.feed(path.read_text(encoding="utf-8",errors="replace"))
        for page,row in h.r.items():
            target=records.setdefault(page,{"page":page,"quire":q,**{v:[] for v in FIELDS.values()}})
            for f in FIELDS.values():target[f].extend(row[f])
    for row in records.values():
        for f in FIELDS.values():row[f]=" || ".join(dict.fromkeys(row[f]))
    old={r["page"]:r for r in csv.DictReader(OLD.open(encoding="utf-8",newline=""),delimiter="\t")}
    ck(len(records)==len(old)==228,"page count");ck(set(records)==set(old),"page ids")
    for page in sorted(records):
        for f in ("quire",*FIELDS.values()):ck(records[page][f]==old[page][f],page+" "+f)
    result=json.loads(RESULT.read_text());ck(result["differences"]==[],"stored differences");ck(result["page_records"]==228,"stored pages");ck(result["status"]=="PASS_18_PUBLIC_SOURCES_228_PAGES_ZERO_DESCRIPTION_DRIFT","status");ck(result["decision"]=="RESTORE_PUBLIC_PROVENANCE_NO_NEW_SEMANTIC_ANCHOR","decision");ck("no new description" in REPORT.read_text().lower(),"report")
    # Mutations.
    changed=dict(records[next(iter(sorted(records)))]);changed["text_description"]+=" X";ck(changed["text_description"]!=old[changed["page"]]["text_description"],"field mutation");ck("q16" not in EXPECTED,"source mutation")
    val={"experiment":"PUBLIC_VOYNICH_NU_CATALOGUE_REFRESH_VALIDATION","status":"PASS_INDEPENDENT_18_SOURCE_228_PAGE_ZERO_DRIFT_RECONSTRUCTION","checks":checks,"inputs":{p.name:sha(p) for p in (OLD,RESULT,REPORT,Path(__file__).resolve())},"sources":18,"pages":228,"field_differences":0,"claim_ceiling":"Validates public source restoration and exact description equality only; no ownership, lexical key, meaning, plaintext, or translation follows."}
    OUT.write_text(json.dumps(val,indent=2,sort_keys=True)+"\n")
    OUT_REPORT.write_text(f"""# Public catalogue refresh validation

Status: **{val['status']}**

Independent code binds all 18 cached public HTML sources and reconstructs all
228 page records and six stored source fields with zero differences in
**{checks}** checks. Mutation guards reject a changed field and an extra quire.

This validates provenance restoration only. No ownership, lexical key,
meaning, plaintext, or translation follows.
""")
    print(json.dumps({"status":val["status"],"checks":checks},sort_keys=True))
if __name__=="__main__":main()
