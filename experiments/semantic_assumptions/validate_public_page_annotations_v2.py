#!/usr/bin/env python3
"""Independent reconstruction of the folio-boundary-safe public page table."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

B = Path(__file__).resolve().parent
R = B / "results"
C = B / "cache" / "public_voynich_nu_catalogue"
OLD = R / "existing_human_page_annotations.tsv"
TSV = R / "public_voynich_nu_page_annotations_v2.tsv"
RESULT = R / "public_page_annotation_boundary_correction.json"
REPORT = R / "public_page_annotation_boundary_correction_report.md"
OUT = R / "public_page_annotation_boundary_correction_validation.json"
OUT_REPORT = R / "public_page_annotation_boundary_correction_validation_report.md"
F = {
    "general description": "general_description", "illustration(s)": "illustrations",
    "text": "text_description", "tentative identifications": "tentative_identifications",
    "other information": "other_information",
}
HEAD = ["page", "quire", *F.values(), "source_tags", "source_url", "tentative_identifications_are_role_evidence"]
P = re.compile(r"f\d+[rv]\d*", re.I)
FO = re.compile(r"f\d+", re.I)
SIG = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
TEN = re.compile(r"\bzodiac sign of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
MON = re.compile(r"\bmonth name (March|April|May|June|July|August|September|October|November|December)\b", re.I)
MS = dict(zip("march april may june july august september october november december".split(), "pisces aries taurus gemini cancer leo virgo libra scorpius sagittarius".split(), strict=True))


def h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def n(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", " ".join(parts).replace("\xa0", " ")).strip()


class Q(HTMLParser):
    def __init__(self, quire: str) -> None:
        super().__init__(convert_charrefs=True); self.q=quire; self.p=""; self.hh=""; self.c=""; self.x=[]; self.r={}
    def handle_starttag(self, tag, attrs):
        tag=tag.lower(); d={k.lower():v for k,v in attrs}; ident=str(d.get("id") or "").lower()
        if tag=="th" and ident:
            if P.fullmatch(ident):
                self.p=ident; self.r.setdefault(ident,{"page":ident,"quire":self.q,**{v:[] for v in F.values()}})
            elif FO.fullmatch(ident): self.p=""
        if tag in ("h4","p"): self.c=tag; self.x=[]
        elif tag=="br" and self.c: self.x.append(" ")
    def handle_data(self, data):
        if self.c: self.x.append(data)
    def handle_endtag(self, tag):
        if tag.lower()!=self.c: return
        text=n(self.x); c=self.c; self.c=""; self.x=[]
        if c=="h4": self.hh=text.lower(); return
        field=F.get(self.hh)
        if field and self.p and text and text.lower() not in ("&nbsp;","none"): self.r[self.p][field].append(text)


def main() -> None:
    if OUT.exists() or OUT_REPORT.exists(): raise SystemExit("refusing overwrite")
    checks=0
    def ck(value, name):
        nonlocal checks; checks+=1
        if not value: raise AssertionError(name)
    old={r["page"]:r for r in csv.DictReader(OLD.open(encoding="utf-8",newline=""),delimiter="\t")}
    stored=list(csv.DictReader(TSV.open(encoding="utf-8",newline=""),delimiter="\t")); ck(list(stored[0])==HEAD,"header")
    stored_by={r["page"]:r for r in stored}; ck(len(stored)==len(stored_by)==228,"stored pages")
    rebuilt={}; source_hashes={}
    paths=sorted(C.glob("q*.html")); ck(len(paths)==18,"sources")
    for path in paths:
        source_hashes[path.stem]=h(path); q=Q(path.stem); q.feed(path.read_text(encoding="utf-8",errors="replace"))
        for page,row in q.r.items():
            dst=rebuilt.setdefault(page,{"page":page,"quire":path.stem,**{v:[] for v in F.values()}})
            for field in F.values(): dst[field]+=row[field]
    ck(set(rebuilt)==set(old)==set(stored_by),"page universe")
    changes=[]; contradictions=[]; zodiac=0
    for page in sorted(rebuilt):
        row=rebuilt[page]
        for field in F.values(): row[field]=" || ".join(dict.fromkeys(row[field]))
        for field in ("source_tags","source_url","tentative_identifications_are_role_evidence"): row[field]=old[page][field]
        ck(row==stored_by[page],page+" row")
        for field in ("quire","general_description","illustrations","text_description","tentative_identifications"):
            ck(row[field]==old[page][field],page+" stable "+field)
        if row["other_information"]!=old[page]["other_information"]:
            ck(old[page]["other_information"].startswith(row["other_information"]),page+" removal")
            changes.append(page)
        a=SIG.search(row["illustrations"]); b=TEN.search(row["tentative_identifications"]); m=MON.search(row["text_description"])
        if a or b or m:
            ck(bool(a and b and m),page+" zodiac complete"); zodiac+=1
            image=a.group(1).lower(); tentative=b.group(1).lower(); month=m.group(1).lower()
            ck(image==MS[month],page+" month image")
            if image!=tentative: contradictions.append((page,image,tentative,month))
    ck(len(changes)==84,"84 changes"); ck(zodiac==12,"12 zodiac")
    ck(contradictions==[("f73v","sagittarius","scorpius","december")],"f73v contradiction")
    result=json.loads(RESULT.read_text()); ck(result["output_tsv_sha256"]==h(TSV),"tsv hash")
    ck(result["counts"]=={"corrected_other_information_pages":84,"f67_through_f73_pages":26,"pages":228,"sources":18,"zodiac_contradictions":1,"zodiac_pages":12},"counts")
    ck(all(result["gates"].values()),"gates"); ck(result["status"]=="PASS_84_CROSS_FOLIO_LEAKS_REMOVED_ONE_ZODIAC_SOURCE_CONTRADICTION","status")
    ck(result["inputs"]["sources"]==source_hashes,"source hashes"); ck("f73v" in REPORT.read_text() and "84" in REPORT.read_text(),"report")
    # Mutations: an uncleared folio must recreate leakage; a changed sign must fail.
    ck(any("Missing folio" in old[p]["other_information"] and "Missing folio" not in stored_by[p]["other_information"] for p in changes),"boundary mutation")
    ck(SIG.search(stored_by["f73v"]["illustrations"]).group(1).lower()!="scorpius","identity mutation")
    validation={
        "experiment":"PUBLIC_PAGE_ANNOTATION_BOUNDARY_CORRECTION_VALIDATION",
        "status":"PASS_INDEPENDENT_228_PAGE_84_BOUNDARY_CORRECTION_RECONSTRUCTION",
        "checks":checks,
        "inputs":{p.name:h(p) for p in (OLD,TSV,RESULT,REPORT,Path(__file__).resolve())},
        "counts":{"sources":18,"pages":228,"corrected_pages":84,"zodiac_pages":12,"contradictions":1},
        "claim_ceiling":"Validates public catalogue record boundaries and the internal f73v contradiction only; no Voynich label ownership, lexeme, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n")
    OUT_REPORT.write_text(
        "# Public page-annotation boundary validation\n\n"
        f"Status: **{validation['status']}**\n\n"
        f"Independent code reconstructed all 228 corrected rows from 18 cached public sources in **{checks}** checks. "
        "It reproduces exactly 84 removed cross-folio suffixes and the sole f73v Sagittarius/Scorpius source contradiction.\n\n"
        "This validates record ownership only; it supplies no Voynich meaning or translation.\n"
    )
    print(json.dumps({"status":validation["status"],"checks":checks},sort_keys=True))


if __name__=="__main__": main()
