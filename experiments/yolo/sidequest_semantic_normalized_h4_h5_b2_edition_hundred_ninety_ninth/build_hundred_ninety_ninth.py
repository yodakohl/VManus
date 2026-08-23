#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
EVENTS=ROOT/"experiments/yolo/sidequest_semantic_six_slot_pressure_test_hundred_eighty_first/HUNDRED_EIGHTY_FIRST_381_EVENT_SIX_SLOT_PARSE.tsv"
MASTER=ROOT/"experiments/yolo/sidequest_semantic_ten_page_master_edition_hundred_seventy_fifth/HUNDRED_SEVENTY_FIFTH_381_PROSE_MASTER_EDITION.tsv"
NORMALIZATION=ROOT/"experiments/yolo/sidequest_semantic_reader_normalization_hundred_ninety_sixth/HUNDRED_NINETY_SIXTH_230_SURFACE_NORMALIZATION.tsv"
MODES=ROOT/"experiments/yolo/sidequest_semantic_field_frame_modes_hundred_ninety_third/HUNDRED_NINETY_THIRD_135_FIELD_FRAME_MODES.tsv"

TRANSLATIONS={
"H4-S001":"Den Ansatz bemessen, auf Sollmaß in eine erste und zweite Portion teilen und abkühlen lassen.",
"H4-S002":"Die Sollmenge überführen und am Verwahrort ablegen.",
"H4-S003":"Eine Sollportion aus dem Quellauszug nehmen, länger bearbeiten und fertigstellen.",
"H4-S004":"Das Sollmaß am Ziel einsetzen und aus diesem Ansatz mit dem Bereitungsanteil die Folgezubereitung bilden.",
"H5-S001":"Einen Zugabeansatz herstellen, die weitere Zutat als Zielzugabe auf Sollmaß bringen, den Folgeansatz einsetzen und dorthin führen.",
"H5-S002":"Vom vorigen Ansatz den Zugabeposten nehmen, einsetzen und länger an der Zielstelle führen; Schluss.",
"H5-S003":"Den Posten halten, eine weitere Zutat zugeben, kurz bearbeiten und erneut einsetzen.",
"H5-S004":"Weiterbearbeiten, den Auszug einsetzen und an der Zielstelle verteilen.",
"H5-S005":"Eine weitere Zutat mit dem Quellauszug bearbeiten und die Folgeanwendung ausführen.",
"H5-S006":"Zum nächsten Posten wechseln, kurz fortfahren und auf Sollmaß bringen.",
"B2-S001":"In die obere Paarbeckenstation überführen; Schluss.",
"B2-S002":"Durch die obere Station weiterführen; Schluss.",
"B2-S003":"Einen Anteil zugeben, diesen Posten länger einwirken lassen; Schluss.",
"B2-S004":"Am Ziel einsetzen, durch die Abführpassage führen, abführen, länger einwirken lassen und getrennt abziehen; Schluss.",
"B2-S005":"Am Ziel einsetzen, bis zum Soll sammeln, durchleiten, am Zeilenübergang einmal bemessen, die Fortsetzung vorbereiten, länger wärmen und abziehen; Schluss.",
"B2-S006":"Die lange Folge ausführen, dorthin einsetzen, durch die kurze Passage führen und einsetzen.",
"B2-S007":"An der mittleren linken Knotenstation kurz absetzen lassen; Schluss.",
"B2-S008":"Das Folgemaß aus der Quelle einsetzen und kurz absetzen lassen; Schluss.",
"B2-S009":"Den Folgeposten absetzen lassen; Schluss.",
"B2-S010":"Länger einwirken lassen, einsetzen und den klaren Auszug zum Auslass führen.",
"B2-S011":"An der mittleren rechten Station einen Anteil zugeben, davon einen weiteren Anteil nehmen und länger einwirken lassen; Schluss.",
"B2-S012":"Das Abführgut als klaren Auszug kurz vorbereiten, länger einwirken lassen, klar abziehen, auf Sollmaß bringen und den aktuellen Posten vollständig einsetzen; Schluss.",
"B2-S013":"In das untere grüne Mehrfigurenfeld abführen; Schluss.",
"B2-S014":"Aus der Quelle abziehen.",
"B2-S015":"An der lokalen Randstation den klaren Lauf länger einwirken lassen; Schluss.",
"B2-S016":"Dorthin führen, aus der Quelle abführen, teilen, auf Sollmaß bringen, die lange Folge bemessen, kurz einwirken lassen und zuführen; Schluss.",
"B2-S017":"Am Ziel kurz halten und den Zielschritt schließen.",
"B2-S018":"Länger einwirken lassen; Schluss.",
"B2-S019":"Den Waschgang schließen.",
"B2-S020":"Die folgende Stufe länger halten; Schluss.",
"B2-S021":"Länger einwirken lassen; Schluss.",
"B2-S022":"Abführen; Schluss.",
}

def read(path):
    with path.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(path,rows):
    with path.open("w",encoding="utf-8",newline="") as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def order(s):
    r=s.split("-")[0];return {"H4":0,"H5":1,"B2":2}[r],int(s.split("S")[1])
def main():
    records={"H4","H5","B2"}; events=[r for r in read(EVENTS) if r["record_unit_id"] in records]; masters=[r for r in read(MASTER) if r["record_unit_id"] in records]
    mb={int(r["event_serial"]):r for r in masters}; norm={r["surface"]:r for r in read(NORMALIZATION)}; modes={r["field_id"]:r for r in read(MODES)}
    er=[]
    for r in events:
        n=norm[r["surface"]];m=mb[int(r["event_id"][1:])]
        er.append({"event_id":r["event_id"],"statement_id":r["statement_id"],"record_unit_id":r["record_unit_id"],"page":r["page"],"field_id":r["field_id"],"field_position":r["field_position"],"visible_surface":r["surface"],"normalized_master_form":n["master_form"],"master_card_id":r["master_card_id"],"portable_value_de":n["portable_value_de"],"normalization_rule":n["normalization_rule"],"field_frame_mode":modes[r["field_id"]]["field_frame_mode"],"visible_owner":m["visible_owner"],"terminal_status":m["terminal_status"]})
    write(OUT/"HUNDRED_NINETY_NINTH_107_EVENT_NORMALIZED_INTERLINEAR.tsv",er)
    bf=defaultdict(list);bs=defaultdict(list)
    for r in er:bf[r["field_id"]].append(r);bs[r["statement_id"]].append(r)
    fr=[]
    for fid in sorted(bf,key=lambda x:int(x[1:])):
        x=bf[fid];fr.append({"field_id":fid,"statement_id":x[0]["statement_id"],"record_unit_id":x[0]["record_unit_id"],"visible_owner":x[0]["visible_owner"],"field_frame_mode":x[0]["field_frame_mode"],"visible_sequence":" ".join(r["visible_surface"] for r in x),"normalized_sequence":" ".join(r["normalized_master_form"] for r in x),"card_sequence":" ".join(r["master_card_id"] for r in x),"literal_values":" | ".join(r["portable_value_de"] for r in x),"terminal":"YES" if x[-1]["terminal_status"]=="CLOSE" else "NO"})
    write(OUT/"HUNDRED_NINETY_NINTH_37_FIELD_NORMALIZED_EDITION.tsv",fr)
    old={}
    for r in masters:old.setdefault(r["statement_id"],r["complete_workshop_expansion_de"])
    sr=[]
    for sid in sorted(bs,key=order):
        x=bs[sid];fids=list(dict.fromkeys(r["field_id"] for r in x));sr.append({"statement_id":sid,"record_unit_id":x[0]["record_unit_id"],"visible_owner":x[0]["visible_owner"],"field_ids":"|".join(fids),"frame_modes":"|".join(modes[f]["field_frame_mode"] for f in fids),"visible_sequence":" ".join(r["visible_surface"] for r in x),"normalized_sequence":" ".join(r["normalized_master_form"] for r in x),"literal_card_reading":" | ".join(r["portable_value_de"] for r in x),"source_token_correction":"E180_E181_TWO_VISIBLE_ONE_LOGICAL_MEASURE" if sid=="B2-S005" else "NONE","previous_fluent_expansion":old[sid],"revised_fluent_translation_de":TRANSLATIONS[sid],"revision_reason":"PORTION_AND_STORAGE" if sid.startswith("H4") else "ADDITIVE_TARGET_APPLICATION" if sid.startswith("H5") else "VISIBLE_STATION_CELL_NORMALIZED"})
    write(OUT/"HUNDRED_NINETY_NINTH_32_STATEMENT_REVISED_EDITION.tsv",sr)
    lines=["# Normalisierte fortlaufende Ausgabe H4, H5 und B2",""]
    for rec,title in (("H4","H4 / f55v — Portionieren und verwahren"),("H5","H5 / f56r — Zusatz und Zielanwendung"),("B2","B2 / f82r — sichtbarer Stationslauf")):
        lines.extend([f"## {title}",""])
        for r in [q for q in sr if q["record_unit_id"]==rec]:lines.extend([f"- **{r['statement_id']}** `{r['visible_sequence']}`",f"  - Normalisiert: `{r['normalized_sequence']}`",f"  - Lesung: {r['revised_fluent_translation_de']}"])
        lines.append("")
    lines.extend(["## Continuous reading","","H4 measures, divides, cools and stores a preparation. H5 turns a measured addition or extract into repeated target applications. B2 moves those working portions through several visibly distinct upper, middle, lower and rim stations; each owner reset starts a new local cell rather than implying one global pipe direction.",""])
    (OUT/"HUNDRED_NINETY_NINTH_THREE_RECORD_CONTINUOUS_EDITION.md").write_text("\n".join(lines),encoding="utf-8")
    summary={"event_source_sha256":hashlib.sha256(EVENTS.read_bytes()).hexdigest(),"master_source_sha256":hashlib.sha256(MASTER.read_bytes()).hexdigest(),"normalization_sha256":hashlib.sha256(NORMALIZATION.read_bytes()).hexdigest(),"mode_source_sha256":hashlib.sha256(MODES.read_bytes()).hexdigest(),"records":3,"visible_events":len(er),"logical_source_tokens":len(er)-1,"fields":len(fr),"statements":len(sr),"record_event_counts":{r:sum(x["record_unit_id"]==r for x in er) for r in sorted(records)},"all_translations_present":all(x["revised_fluent_translation_de"] for x in sr),"all_surfaces_normalized":all(x["normalized_master_form"] for x in er),"sealed_pages_accessed":False}
    (OUT/"BUILD_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
