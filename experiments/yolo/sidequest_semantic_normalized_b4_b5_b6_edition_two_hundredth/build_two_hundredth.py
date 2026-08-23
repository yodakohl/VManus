#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
EVENTS=ROOT/"experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv";MASTER=ROOT/"experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv";NORMALIZATION=ROOT/"experiments/yolo/sidequest_semantic_reader_normalization_hundred_ninety_sixth/HUNDRED_NINETY_SIXTH_230_SURFACE_NORMALIZATION.tsv";MODES=ROOT/"experiments/yolo/sidequest_semantic_field_frame_modes_hundred_ninety_third/HUNDRED_NINETY_THIRD_135_FIELD_FRAME_MODES.tsv"
T={
"B4-S001":"Am Hauptpaar länger einwirken lassen; Schluss.",
"B4-S002":"Den Weiterposten zuerst länger, dann kurz einwirken lassen; Schluss.",
"B4-S003":"Überführen, danach den nächsten Posten dorthin bringen, länger einwirken lassen, einsetzen, weiterführen und kurz absetzen lassen; Schluss.",
"B4-S004":"Den Posten festsetzen; Schluss.",
"B4-S005":"Die Einlage überführen und länger einwirken lassen; Schluss.",
"B4-S006":"Einmal durchlassen; Schluss.",
"B4-S007":"Ein zweites Mal durchlassen; Schluss.",
"B4-S008":"Auf Sollmaß bringen, länger bearbeiten, länger halten und kurz einwirken lassen; Schluss.",
"B4-S009":"Kurz absetzen lassen; Schluss.",
"B4-S010":"Fertigstellen; Schluss.",
"B4-S011":"An der linken Unterlaufstation das Sollmaß kurz wärmen, länger weiterführen, einen Anteil zugeben, überführen, fortsetzen und kurz abziehen; Schluss.",
"B4-S012":"Abführen; Schluss.",
"B4-S013":"Weiter einsetzen und kurz absetzen lassen; Schluss.",
"B4-S014":"Diesen Ansatz durch den kurzen Gang führen und den Lauf schließen.",
"B4-S015":"Einen Anteil zum klaren Auszug geben, den Anteil durch die Zielpassage führen, kurz auffangen und abführen; Schluss.",
"B4-S016":"Einen weiteren Anteil dorthin bringen, aus der Quelle ausgießen und kurz absetzen lassen; Schluss.",
"B5-S001":"Den Nachtransfer am linken Endposten ausführen; Schluss.",
"B5-S002":"In den linken Endposten einführen; Schluss.",
"B5-S003":"Am Ziel absetzen, dorthin bringen, weiterführen und weiter abziehen; den Zieltransfer auf Sollmaß bringen, bis zur Endstufe fortsetzen und überführen.",
"B6-S001":"Am rechten Endposten länger auffangen, kurz bearbeiten, zum Endposten weiterführen, auf Sollmaß bringen, die Einlage als aktuellen Posten zum Endziel führen.",
}
def read(p):
    with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,r):
    with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(r)
def order(s):r=s.split("-")[0];return {"B4":0,"B5":1,"B6":2}[r],int(s.split("S")[1])
def main():
    recs={"B4","B5","B6"};ev=[r for r in read(EVENTS) if r["record_unit_id"] in recs];ma=[r for r in read(MASTER) if r["record_unit_id"] in recs];mb={int(r["event_serial"]):r for r in ma};no={r["surface"]:r for r in read(NORMALIZATION)};mo={r["field_id"]:r for r in read(MODES)}
    er=[]
    for r in ev:
        n=no[r["surface"]];m=mb[int(r["event_id"][1:])];er.append({"event_id":r["event_id"],"statement_id":r["statement_id"],"record_unit_id":r["record_unit_id"],"page":r["page"],"field_id":r["field_id"],"field_position":r["field_position"],"visible_surface":r["surface"],"normalized_master_form":n["master_form"],"master_card_id":r["master_card_id"],"portable_value_de":n["portable_value_de"],"normalization_rule":n["normalization_rule"],"field_frame_mode":mo[r["field_id"]]["field_frame_mode"],"visible_owner":m["visible_owner"],"terminal_status":m["terminal_status"]})
    write(OUT/"TWO_HUNDREDTH_67_EVENT_NORMALIZED_INTERLINEAR.tsv",er);bf=defaultdict(list);bs=defaultdict(list)
    for r in er:bf[r["field_id"]].append(r);bs[r["statement_id"]].append(r)
    fr=[]
    for fid in sorted(bf,key=lambda x:int(x[1:])):
        x=bf[fid];fr.append({"field_id":fid,"statement_id":x[0]["statement_id"],"record_unit_id":x[0]["record_unit_id"],"visible_owner":x[0]["visible_owner"],"field_frame_mode":x[0]["field_frame_mode"],"visible_sequence":" ".join(r["visible_surface"] for r in x),"normalized_sequence":" ".join(r["normalized_master_form"] for r in x),"card_sequence":" ".join(r["master_card_id"] for r in x),"literal_values":" | ".join(r["portable_value_de"] for r in x),"terminal":"YES" if x[-1]["terminal_status"]=="CLOSE" else "NO"})
    write(OUT/"TWO_HUNDREDTH_27_FIELD_NORMALIZED_EDITION.tsv",fr);old={}
    for r in ma:old.setdefault(r["statement_id"],r["complete_workshop_expansion_de"])
    sr=[]
    for sid in sorted(bs,key=order):
        x=bs[sid];fids=list(dict.fromkeys(r["field_id"] for r in x));sr.append({"statement_id":sid,"record_unit_id":x[0]["record_unit_id"],"visible_owner":x[0]["visible_owner"],"field_ids":"|".join(fids),"frame_modes":"|".join(mo[f]["field_frame_mode"] for f in fids),"visible_sequence":" ".join(r["visible_surface"] for r in x),"normalized_sequence":" ".join(r["normalized_master_form"] for r in x),"literal_card_reading":" | ".join(r["portable_value_de"] for r in x),"previous_fluent_expansion":old[sid],"revised_fluent_translation_de":T[sid],"revision_reason":"MAIN_PAIR_AND_LEFT_UNDERFLOW" if sid.startswith("B4") else "LEFT_END_POST" if sid.startswith("B5") else "RIGHT_END_POST"})
    write(OUT/"TWO_HUNDREDTH_20_STATEMENT_REVISED_EDITION.tsv",sr)
    lines=["# Normalisierte fortlaufende Ausgabe B4, B5 und B6",""]
    for rec,title in (("B4","B4 — Hauptpaar und linker Unterlauf"),("B5","B5 — linker Endposten"),("B6","B6 — rechter Endposten")):
        lines.extend([f"## {title}",""])
        for r in [q for q in sr if q["record_unit_id"]==rec]:lines.extend([f"- **{r['statement_id']}** `{r['visible_sequence']}`",f"  - Normalisiert: `{r['normalized_sequence']}`",f"  - Lesung: {r['revised_fluent_translation_de']}"])
        lines.append("")
    lines.extend(["## Continuous reading","","B4 works the visible main pair and then the left underflow station: contact, insert, pass twice, hold, settle, draw off and divide into a target passage. B5 and B6 are separate end-post records, not continuations forced through an invisible global circuit.",""])
    (OUT/"TWO_HUNDREDTH_THREE_RECORD_CONTINUOUS_EDITION.md").write_text("\n".join(lines),encoding="utf-8")
    z={"event_source_sha256":hashlib.sha256(EVENTS.read_bytes()).hexdigest(),"master_source_sha256":hashlib.sha256(MASTER.read_bytes()).hexdigest(),"normalization_sha256":hashlib.sha256(NORMALIZATION.read_bytes()).hexdigest(),"mode_source_sha256":hashlib.sha256(MODES.read_bytes()).hexdigest(),"records":3,"events":len(er),"fields":len(fr),"statements":len(sr),"record_event_counts":{r:sum(x["record_unit_id"]==r for x in er) for r in sorted(recs)},"all_translations_present":all(x["revised_fluent_translation_de"] for x in sr),"all_surfaces_normalized":all(x["normalized_master_form"] for x in er),"sealed_pages_accessed":False};(OUT/"BUILD_SUMMARY.json").write_text(json.dumps(z,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
