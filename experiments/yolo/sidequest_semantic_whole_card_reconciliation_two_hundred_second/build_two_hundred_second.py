#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;BASE=ROOT/"experiments/yolo/sidequest_semantic_unified_prose_edition_two_hundred_first"
DICT=BASE/"TWO_HUNDRED_FIRST_173_CARD_CURRENT_DICTIONARY.tsv";EVENTS=BASE/"TWO_HUNDRED_FIRST_381_EVENT_CURRENT_EDITION.tsv";STATEMENTS=BASE/"TWO_HUNDRED_FIRST_116_STATEMENT_CURRENT_EDITION.tsv"
DECISIONS={
"MC012":("Zusatz","KEEP_CURRENT","Two basin contexts both take an added item."),
"MC027":("Zubereitungsgefäß","RESTORE_LEGACY","A vessel before Ansatz avoids three consecutive preparation synonyms."),
"MC037":("kalt stellen; Schluss","RESTORE_LEGACY","It follows clear extract after pressing and restraining and terminates the chain."),
"MC052":("kurz bearbeiten","KEEP_CURRENT","In B6 it is an operation between collecting and target transfer; RAW is inert here."),
"MC059":("Einlage","KEEP_CURRENT","Both B4 and B6 place a transferable insert; cloth remains a possible local material."),
"MC061":("Haltetransfer; Schluss","KEEP_CURRENT","It closes after continuation; generic swinging is less readable."),
"MC071":("Wurzel","RESTORE_LEGACY","Initial pictured-plant source part gives the most concrete Herbal reading."),
"MC084":("Waschgang; Schluss","REFINE","The singleton is an entire closed wash cell."),
"MC099":("auftragen; Schluss","RESTORE_LEGACY","It follows taking and setting an application item at the target."),
"MC100":("abkühlen; Schluss","REFINE","Cooling is shared by both readings and the exact card is terminal."),
"MC109":("Kurzteil","KEEP_CURRENT","It is the item introduced from the just-set source."),
"MC114":("Stängel","RESTORE_LEGACY","A pictured-plant part plus another ingredient is more concrete than a free HOLD command."),
"MC118":("Auffanggefäß","REFINE","The following hold, stage and long collection actions require a receiver."),
"MC119":("Klarlauf","RESTORE_LEGACY","This spans strained product and apparatus outlet better than only extract."),
"MC124":("Kurzabzug; Schluss","KEEP_CURRENT","It terminates an underflow transfer chain; rewash is not required."),
"MC129":("auswringen","KEEP_CURRENT","It sits before standing and restraining in H3."),
"MC138":("Frischwasser zugeben; Schluss","RESTORE_LEGACY","A standalone new station cell is better as a fresh charge than an unlicensed duplicate settle."),
"MC142":("vom vorigen","KEEP_CURRENT","Both Herbal occurrences introduce an anaphoric prior batch."),
"MC152":("teilen","KEEP_CURRENT","It is embedded between source draw and measured follow-on feed."),
"MC156":("nachseihen","KEEP_CURRENT","It follows pressing and standing and precedes clear flow."),
"MC159":("Aufnahmegefäß","KEEP_CURRENT","H1 explicitly prepares and pours into a receiver."),
"MC164":("befestigen; Schluss","REFINE","The isolated B4 cell follows insertion and licenses a fastening close."),
}
OVERRIDES={
"H1-S001":"Die Wurzel der Bildpflanze nehmen, einen Anteil im Aufnahmegefäß vorbereiten, Flüssigkeit zugießen, den Folgeteil einsetzen und auf Sollmaß bringen.",
"H2-S003":"Im Zubereitungsgefäß den Ansatz in der nächsten Stufe bearbeiten und die vorgeschriebene Zugabemenge einsetzen.",
"H3-S001":"Das Kochgut in einem Sud ansetzen, auswringen, eine Stehzeit abwarten, nachseihen, den Klarlauf abnehmen und kalt stellen; Schluss.",
"H4-S001":"Den Ansatz bemessen, auf Sollmaß in eine erste und zweite Portion teilen und abkühlen lassen; Schluss.",
"H5-S002":"Vom vorigen Ansatz den Zugabeposten nehmen, einsetzen und an der Zielstelle auftragen; Schluss.",
"H5-S003":"Den Stängel und eine weitere Zutat kurz bearbeiten und erneut einsetzen.",
"B1-S018":"Im Auffanggefäß kurz halten, die Arbeitsstufe setzen und länger auffangen; Schluss.",
"B2-S007":"An der mittleren linken Knotenstation Frischwasser zugeben; Schluss.",
"B4-S004":"Den Posten befestigen; Schluss.",
}
def read(p):
    with p.open(encoding="utf-8",newline="") as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,r):
    with p.open("w",encoding="utf-8",newline="") as h:w=csv.DictWriter(h,fieldnames=list(r[0]),delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(r)
def main():
    d=read(DICT);e=read(EVENTS);s=read(STATEMENTS);whole={r["master_card_id"]:r for r in d if r["component_class"]=="MEMORIZED_WHOLE_CARD"}
    rows=[]
    for cid in sorted(whole,key=lambda x:int(x[2:])):
        value,status,reason=DECISIONS[cid];x=whole[cid];occ=[r for r in e if r["master_card_id"]==cid]
        rows.append({"master_card_id":cid,"registered_surfaces":x["registered_surfaces"],"occurrences":len(occ),"event_ids":"|".join(r["event_id"] for r in occ),"statements":"|".join(dict.fromkeys(r["statement_id"] for r in occ)),"owners":"|".join(dict.fromkeys(r["visible_owner"] for r in occ)),"previous_current_value_de":x["current_value_de"],"legacy_snapshot_de":x["component_reading_snapshot_de"],"decision":status,"selected_value_de":value,"decision_reason":reason})
    write(OUT/"TWO_HUNDRED_SECOND_22_WHOLE_CARD_DECISIONS.tsv",rows)
    selected={r["master_card_id"]:r["selected_value_de"] for r in rows}
    for r in d:
        if r["master_card_id"] in selected:r["current_value_de"]=selected[r["master_card_id"]]
    write(OUT/"TWO_HUNDRED_SECOND_173_CARD_RECONCILED_DICTIONARY.tsv",d)
    for r in e:
        if r["master_card_id"] in selected:r["portable_value_de"]=selected[r["master_card_id"]]
    write(OUT/"TWO_HUNDRED_SECOND_381_EVENT_RECONCILED_EDITION.tsv",e)
    byst=defaultdict(list)
    for r in e:byst[r["statement_id"]].append(r)
    revisions=[]
    for r in s:
        old_literal=r["literal_card_reading"];r["literal_card_reading"]=" | ".join(x["portable_value_de"] for x in byst[r["statement_id"]]);old_fluent=r["revised_fluent_translation_de"]
        if r["statement_id"] in OVERRIDES:r["revised_fluent_translation_de"]=OVERRIDES[r["statement_id"]]
        if old_literal!=r["literal_card_reading"] or old_fluent!=r["revised_fluent_translation_de"]:
            revisions.append({"statement_id":r["statement_id"],"old_literal":old_literal,"new_literal":r["literal_card_reading"],"old_fluent":old_fluent,"new_fluent":r["revised_fluent_translation_de"],"fluent_changed":"YES" if old_fluent!=r["revised_fluent_translation_de"] else "NO"})
    write(OUT/"TWO_HUNDRED_SECOND_116_STATEMENT_RECONCILED_EDITION.tsv",s);write(OUT/"TWO_HUNDRED_SECOND_AFFECTED_STATEMENTS.tsv",revisions)
    summary={"dictionary_source_sha256":hashlib.sha256(DICT.read_bytes()).hexdigest(),"event_source_sha256":hashlib.sha256(EVENTS.read_bytes()).hexdigest(),"statement_source_sha256":hashlib.sha256(STATEMENTS.read_bytes()).hexdigest(),"decisions":len(rows),"occurrences":sum(int(r["occurrences"]) for r in rows),"decision_distribution":dict(Counter(r["decision"] for r in rows)),"cards":len(d),"events":len(e),"statements":len(s),"affected_statements":len(revisions),"fluent_revisions":sum(r["fluent_changed"]=="YES" for r in revisions),"sealed_pages_accessed":False};(OUT/"BUILD_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
