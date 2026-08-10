#!/usr/bin/env python3
"""CCT002 scorer: CCT001 statistic with a marginal-preserving merger null."""
from __future__ import annotations
from collections import Counter,defaultdict
import cho_che_canonical_transfer_core as base

READINGS=base.READINGS;LEAVES=base.LEAVES

def validate_events(events):
 if not events or len({e["event_id"] for e in events})!=len(events):raise base.ContractError("duplicate/empty event IDs")
 required={"event_id","edition","leaf","side","state","scope","prefix","raw_type","canonical_type","realization","length","site_index"};meta={};groups=defaultdict(dict);counts=Counter()
 for e in events:
  if set(e)!=required:raise base.ContractError("event schema")
  if e["edition"] not in base.READINGS or e["leaf"] not in base.LEAVES or e["side"] not in {"r","v"} or e["state"] not in (0,1):raise base.ContractError("event geometry")
  if e["scope"] not in base.SCOPES or e["prefix"] not in base.PREFIXES or e["realization"] not in {"o","e"}:raise base.ContractError("event class")
  if not isinstance(e["length"],int) or not isinstance(e["site_index"],int) or not 0<=e["site_index"]<e["length"]:raise base.ContractError("event position")
  m=(e["canonical_type"],e["realization"],e["prefix"],e["length"],e["site_index"])
  if e["raw_type"] in meta and meta[e["raw_type"]]!=m:raise base.ContractError("inconsistent raw-type metadata")
  meta[e["raw_type"]]=m
  if e["realization"] in groups[e["canonical_type"]] and groups[e["canonical_type"]][e["realization"]]!=e["raw_type"]:raise base.ContractError("multiple raw types")
  groups[e["canonical_type"]][e["realization"]]=e["raw_type"];counts[e["raw_type"]]+=1
 if {e["edition"] for e in events}!=set(READINGS) or {e["leaf"] for e in events}!=set(LEAVES):raise base.ContractError("coverage")
 pairs=[]
 for c,m in groups.items():
  if set(m)=={"o","e"}:
   o,q=m["o"],m["e"]
   if meta[o][0]!=c or meta[q][0]!=c or meta[o][2:]!=meta[q][2:]:raise base.ContractError("broken pair")
   pairs.append({"canonical":c,"o":o,"e":q,"shell":(meta[o][3],meta[o][2],meta[o][4])})
 pairs.sort(key=lambda p:(p["shell"],p["o"],p["e"]));shells=defaultdict(list)
 for p in pairs:shells[p["shell"]].append(p)
 movable=sum(len(v) for v in shells.values() if len(v)>=2);types={p[k] for p in pairs for k in ("o","e")};pe=[e for e in events if e["raw_type"] in types];capacity={"collision_pairs":len(pairs),"movable_pairs":movable,"collision_events":len(pe),"collision_event_fraction":len(pe)/len(events),"pair_event_leaves":sorted({e["leaf"] for e in pe}),"pair_event_readings":sorted({e["edition"] for e in pe})};capacity["passes"]=len(pairs)>=24 and movable>=16 and set(capacity["pair_event_leaves"])==set(LEAVES) and set(capacity["pair_event_readings"])==set(READINGS)
 return {"pairs":pairs,"shells":dict(shells),"meta":meta,"counts":counts,"capacity":capacity}

def score_world(events,merge_draws=8192):
 old=base.validate_events;base.validate_events=validate_events
 try:return base.score_world(events,merge_draws=merge_draws)
 finally:base.validate_events=old

compact_score=base.compact_score
complement_states=base.complement_states
