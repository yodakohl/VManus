#!/usr/bin/env python3
"""Export the committed GDT155 expansion/regularized truth after blind freeze."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "gdt155_source_freeze.json"
BLIND = ROOT / "gdt155_blind_result.json"
PAGE_NS = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
TEI_NS = "http://www.tei-c.org/ns/1.0"
STE_SHA = "3db06c80345e584e5b6af7e062af839964312b92bcf1edb8b88aa05110024df6"
NB_SHA = "59e5264acb4546477567e78c8b3d444c472f1a0a5256ee0ee7d0407a70904652"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def local(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def render(element: ET.Element, *, expanded: bool, linebreaks: bool = False) -> str:
    out: list[str] = []
    def walk(node: ET.Element) -> None:
        tag = local(node)
        if tag == "ex" and not expanded:
            return
        if tag == "am":
            return
        if tag == "lb" and linebreaks:
            out.append("\n")
        if node.text: out.append(node.text)
        for child in node:
            walk(child)
            if child.tail: out.append(child.tail)
    walk(element)
    return unicodedata.normalize("NFC", "".join(out))


def clean(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())


def site_id(corpus: str, record: str, ordinal: int) -> str:
    return "AS" + hashlib.sha256(f"{corpus}|{record}|{ordinal}".encode()).hexdigest()[:14].upper()


def omitted(node: ET.Element) -> str:
    return clean("".join("".join(ex.itertext()) for ex in node.iter() if local(ex) == "ex"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def nuremberg(path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[tuple], list[tuple]]:
    line_rows = []; site_rows = []; section_rows = []; truth = []; regularized_truth = []
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist() if name.startswith("nuremberg_letterbooks/diplomatic-regularised/Band") and name.endswith(".xml")]
        members.sort(key=lambda name: (int(name.split("/")[-2][4:]), int(Path(name).stem)))
        for member in members:
            book = member.split("/")[-2]; numeric = int(Path(member).stem)
            record = f"NB_B{book[4:]}_R{numeric:06d}"
            root = ET.fromstring(archive.read(member)); line_index = 0; site_index = 0
            expanded_record_lines = []
            for page in root.findall(f".//{{{PAGE_NS}}}Page"):
                for text_line in page.findall(f".//{{{PAGE_NS}}}TextLine"):
                    unicode = text_line.find(f"{{{PAGE_NS}}}TextEquiv/{{{PAGE_NS}}}Unicode")
                    if unicode is None: continue
                    line_index += 1; line_id = f"{record}_L{line_index:04d}"
                    expanded = clean(render(unicode, expanded=True)); expanded_record_lines.append(expanded)
                    line_rows.append({"corpus":"NUREMBERG","book_or_ms":book,"record_id":record,"line_id":line_id,"expanded_diplomatic":expanded or "EMPTY"})
                    truth.append(("LINE", line_id, expanded))
                    for node in unicode.iter():
                        if local(node) != "expan": continue
                        site_index += 1; sid = site_id("NUREMBERG", record, site_index)
                        surface = clean(render(node, expanded=False)); expanded_span = clean(render(node, expanded=True))
                        site_rows.append({"site_id":sid,"corpus":"NUREMBERG","book_or_ms":book,"record_id":record,"line_id":line_id,"site_index_in_record":site_index,"surface_span_bare":surface,"expanded_span":expanded_span,"editorially_inserted":omitted(node) or "NONE"})
                        truth.append(("SITE", sid, expanded_span))
            sections = defaultdict(list)
            for div in root.iter():
                if local(div) != "div" or div.attrib.get("type") == "regularised": continue
                typ = div.attrib.get("type", "UNKNOWN"); text = clean(render(div, expanded=True, linebreaks=True))
                sections[typ].append(text); regularized_truth.append((record, typ, text))
            section_rows.append({
                "corpus":"NUREMBERG","book_or_ms":book,"record_id":record,
                "expanded_diplomatic_record":" ".join(expanded_record_lines),
                "regularized_addressee":" || ".join(sections.get("addressee", [])),
                "regularized_content":" || ".join(sections.get("content", [])),
                "regularized_other_sections":" || ".join(f"{typ}={' || '.join(values)}" for typ, values in sorted(sections.items()) if typ not in {"addressee","content"}) or "NONE",
            })
    return line_rows, site_rows, section_rows, truth, regularized_truth


def ste1(path: Path) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[tuple], list[tuple]]:
    root = ET.parse(path).getroot(); line_rows=[]; site_rows=[]; record_rows=[]; truth=[]; regularized_truth=[]
    for seg_index, seg in enumerate(root.findall(f".//{{{TEI_NS}}}text//{{{TEI_NS}}}seg"), 1):
        record=f"STE1_SEG{seg_index:02d}"
        expanded_parts=[clean(x) for x in render(seg,expanded=True,linebreaks=True).split("\n")]
        expanded_parts=[x for x in expanded_parts if x]
        nodes=[node for node in seg.iter() if local(node)=="abbr"]
        marked_parts=[]
        # Rebuild line assignment from anonymous markers only; no content decision is made.
        def marked_render(element: ET.Element) -> str:
            out=[]
            def walk(node:ET.Element):
                tag=local(node)
                if tag=="ex" or tag=="am": return
                if tag=="lb": out.append("\n")
                if node.text: out.append(node.text)
                for child in node:
                    walk(child)
                    if child.tail: out.append(child.tail)
                if tag=="abbr": out.append("¤")
            walk(element);return unicodedata.normalize("NFC","".join(out))
        marked_parts=[clean(x) for x in marked_render(seg).split("\n")]
        marked_parts=[x for x in marked_parts if x]
        cursor=0
        for line_index,(expanded,marked) in enumerate(zip(expanded_parts,marked_parts),1):
            line_id=f"{record}_L{line_index:04d}";line_rows.append({"corpus":"STE1","book_or_ms":"Ste1","record_id":record,"line_id":line_id,"expanded_diplomatic":expanded or "EMPTY"});truth.append(("LINE",line_id,expanded))
            for _ in range(marked.count("¤")):
                node=nodes[cursor];cursor+=1;sid=site_id("STE1",record,cursor);surface=clean(render(node,expanded=False));expanded_span=clean(render(node,expanded=True))
                site_rows.append({"site_id":sid,"corpus":"STE1","book_or_ms":"Ste1","record_id":record,"line_id":line_id,"site_index_in_record":cursor,"surface_span_bare":surface,"expanded_span":expanded_span,"editorially_inserted":omitted(node) or "NONE"});truth.append(("SITE",sid,expanded_span))
        assert cursor==len(nodes)
        expanded_record=" ".join(expanded_parts);record_rows.append({"corpus":"STE1","book_or_ms":"Ste1","record_id":record,"expanded_diplomatic_record":expanded_record,"regularized_addressee":"","regularized_content":expanded_record,"regularized_other_sections":"technical_recipe_record"})
        regularized_truth.append((record,"technical_recipe_record",expanded_record))
    return line_rows,site_rows,record_rows,truth,regularized_truth


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument("--ste1",type=Path,required=True);parser.add_argument("--nuremberg",type=Path,required=True);parser.add_argument("--output-dir",type=Path,default=ROOT);args=parser.parse_args()
    assert sha(args.ste1)==STE_SHA and sha(args.nuremberg)==NB_SHA
    freeze=json.loads(FREEZE.read_text(encoding="utf-8"));blind=json.loads(BLIND.read_text(encoding="utf-8"))
    assert freeze["truth_exported"] is False and blind["truth_exported_or_used"] is False
    nl,ns,nr,nt,nrt=nuremberg(args.nuremberg);sl,ss,sr,st,srt=ste1(args.ste1)
    truth_material={"expanded_line_and_site_truth":sorted(nt+st),"regularized_or_record_truth":sorted(nrt+srt)}
    commitment=csha(truth_material);assert commitment==freeze["truth_content_sha256"],(commitment,freeze["truth_content_sha256"])
    args.output_dir.mkdir(parents=True,exist_ok=True)
    line_path=args.output_dir/"gdt155_unblinded_lines.tsv";site_path=args.output_dir/"gdt155_unblinded_abbreviation_sites.tsv";record_path=args.output_dir/"gdt155_unblinded_record_truth.tsv"
    write(line_path,sl+nl);write(site_path,ss+ns);write(record_path,sr+nr)
    result={"schema":"GDT155_UNBLIND_EXPORT_V1","status":"COMMITTED_EXPANSION_TRUTH_EXPORTED_AFTER_BLIND_FREEZE","truth_content_sha256":commitment,"truth_commitment_match":True,"counts":{"lines":len(sl)+len(nl),"sites":len(ss)+len(ns),"records":len(sr)+len(nr)},"chronology":{"source_freeze_commit":"d62de97","blind_analysis_commit":"99bab66","unblind_after_both":True},"inputs":{"gdt155_source_freeze.json":sha(FREEZE),"gdt155_blind_result.json":sha(BLIND),"ste1_sha256":STE_SHA,"nuremberg_sha256":NB_SHA},"implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{p.name:sha(p) for p in (line_path,site_path,record_path)},"f84":{"voynich_inputs":0,"accessed":False}}
    result["result_content_sha256"]=csha(result);(args.output_dir/"gdt155_unblind_export.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8");print(json.dumps(result["counts"],sort_keys=True))


if __name__=="__main__":main()
