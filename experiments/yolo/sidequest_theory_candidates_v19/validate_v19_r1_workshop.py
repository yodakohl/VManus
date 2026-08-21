#!/usr/bin/env python3
import csv, json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
def read(name):
    with (HERE/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f,delimiter="\t"))

events=read("V19_R1_100_EVENT_INTERLINEAR.tsv")
cards=read("V19_R1_HERBAL_CARD_DICTIONARY.tsv")
alts=read("V19_R1_SINGLETON_ALTERNATIVES.tsv")
freeze=read("V19_R1_VISIBLE_PLANT_FREEZE.tsv")
forbidden={"unknown","opaque","content","payload","item","value","state","plant detail","property","operation"}
problems=[]
if len(events)!=100: problems.append(f"event_count={len(events)}")
if len(cards)!=66: problems.append(f"card_count={len(cards)}")
if len(alts)!=55: problems.append(f"singleton_count={len(alts)}")
if len(freeze)!=4: problems.append(f"freeze_count={len(freeze)}")
if len({r['exact_tuple_id'] for r in events})!=66: problems.append("event_unique_type_count")
if any(not r['default_English'].strip() or r['default_English'].strip().lower() in forbidden for r in cards): problems.append("blank_card")
if any(not r['concrete_alternative_1'].strip() or not r['concrete_alternative_2'].strip() for r in alts): problems.append("blank_alternative")
if any(r['text_inspected_for_assignment']!='NO' for r in freeze): problems.append("freeze_not_pretext")
freq=Counter(r['exact_tuple_id'] for r in events)
if sum(v==1 for v in freq.values())!=55: problems.append("singleton_frequency")
result={"status":"PASS" if not problems else "FAIL","problems":problems,
        "events":len(events),"cards":len(cards),"singletons":len(alts),
        "pages":sorted({r['page'] for r in events}),"f84_accessed":False,"f84r_accessed":False}
print(json.dumps(result,indent=2,sort_keys=True))
raise SystemExit(bool(problems))
