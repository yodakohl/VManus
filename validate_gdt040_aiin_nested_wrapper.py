#!/usr/bin/env python3
"""Independent reconstruction for the GDT040 AIIN wrapper-stack result."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"gdt016_group_state_inventory.tsv";OCC=ROOT/"gdt040_aiin_occurrences.tsv"
TABLES=ROOT/"gdt040_register_tables.tsv";TESTS=ROOT/"gdt040_folio_compatibility_tests.tsv"
PRED=ROOT/"gdt040_cross_register_predictions.tsv";RESULT=ROOT/"gdt040_result.json"
LEDGER=ROOT/"GDT002_YOLO_LEDGER.tsv";VALIDATION=ROOT/"gdt040_validation.json"
REGISTERS=("HB","SB","HA","OB")

def read(path):
 with path.open(encoding="utf-8",newline="")as handle:return list(csv.DictReader(handle,delimiter="\t"))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def csha(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def reg(row):
 if row["section"]=="H"and row["currier"]=="B":return"HB"
 if row["section"]=="S"and row["currier"]=="B":return"SB"
 if row["section"]=="H"and row["currier"]=="A":return"HA"
 return"OB"

def reconstruct(rows):
 lines=defaultdict(list)
 for row in rows:
  assert not row["locus"].startswith("f84r");lines[row["locus"]].append(row)
 output=[]
 for locus,line in lines.items():
  line.sort(key=lambda row:int(row["group_index"]));count=int(line[0]["group_count"])
  complete=len(line)==count and {int(row["group_index"])for row in line}==set(range(1,count+1))
  fields=[];current=[]
  for index,row in enumerate(line):
   current.append((index,row))
   if row["record_state"]=="DY_RESOLUTION":fields.append((current,True));current=[]
  if current:fields.append((current,False))
  address={index:(fi,j)for fi,(field,_)in enumerate(fields)for j,(index,_)in enumerate(field)}
  for index,row in enumerate(line):
   if row["residual_host"]not in{"aiin","daiin"}:continue
   carrier=row["stripped_prefix"]in{"ch","che","sh"}
   inner=row["residual_host"]=="daiin"or(not carrier and row["stripped_prefix"]=="d")
   fi,j=address[index];field,closed=fields[fi];size=len(field)
   position=("SINGLE"if size==1 else"FIELD_START"if j==0 else
             "FIELD_CLOSE"if j==size-1 and closed else"OPEN_FIELD_END"if j==size-1 else
             "PRECLOSE"if closed and j==size-2 else"FIELD_INTERNAL")
   output.append({"locus":locus,"page":row["page"],"physical_folio":row["physical_folio"],
    "register":reg(row),"section":row["section"],"currier":row["currier"],"hand":row["hand"],
    "group_index":row["group_index"],"group_count":row["group_count"],"token":row["token"],
    "frozen_wrapper":row["stripped_prefix"],"frozen_residual_host":row["residual_host"],
    "base_host":"aiin","outer_carrier":str(int(carrier)),"inner_d":str(int(inner)),
    "cell":f'C{int(carrier)}D{int(inner)}',"record_state":row["record_state"],
    "retained_line_complete":str(int(complete)),"field_position":position,
    "previous_state":"BOS"if index==0 else line[index-1]["record_state"],
    "following_state":"EOS"if index+1==len(line)else line[index+1]["record_state"]})
 output.sort(key=lambda row:(REGISTERS.index(row["register"]),row["physical_folio"],row["locus"],int(row["group_index"])))
 return output

def hypergeom(n,K,k):
 den=math.comb(n,k);return{x:math.comb(K,x)*math.comb(n-K,k-x)/den for x in range(max(0,k-(n-K)),min(K,k)+1)}
def conv(a,b):
 out=defaultdict(float)
 for i,p in a.items():
  for j,q in b.items():out[i+j]+=p*q
 return dict(out)
def exact(rows,registers):
 chosen=[row for row in rows if row["register"]in registers];by=defaultdict(list)
 for row in chosen:by[row["physical_folio"]].append(row)
 pmf={0:1.};observed=0;expected=0.;positive=0
 for items in by.values():
  n=len(items);C=sum(row["outer_carrier"]=="1"for row in items);D=sum(row["inner_d"]=="1"for row in items);both=sum(row["cell"]=="C1D1"for row in items)
  observed+=both;expected+=C*D/n;positive+=both>C*D/n;pmf=conv(pmf,hypergeom(n,C,D))
 return{"registers":"+".join(registers),"occurrences":len(chosen),"folios":len(by),"double_observed":observed,
        "double_expected":expected,"excess":observed-expected,"one_sided_enrichment_p":sum(p for x,p in pmf.items()if x>=observed),
        "one_sided_depletion_p":sum(p for x,p in pmf.items()if x<=observed),"positive_folios":positive,"null_min":min(pmf),"null_max":max(pmf)}
def prediction(train,test,tn,vn):
 def count(data,key=None):
  z=data if key is None else[row for row in data if row["outer_carrier"]==key]
  return sum(row["inner_d"]=="1"for row in z),len(z)
 s,n=count(train);globalp=(s+.5)/(n+1);probs={k:(count(train,k)[0]+.5)/(count(train,k)[1]+1)for k in("0","1")}
 gb=cb=0.
 for row in test:
  y=row["inner_d"]=="1";p=globalp;q=probs[row["outer_carrier"]];gb-=math.log2(p if y else 1-p);cb-=math.log2(q if y else 1-q)
 raw=gb-cb;pen=.5*math.log2(len(train))
 return{"train_register":tn,"test_register":vn,"train_events":len(train),"test_events":len(test),"global_test_bits":gb,
        "conditional_test_bits":cb,"raw_gain_bits":raw,"additional_parameter_bic_bits":pen,"paid_gain_bits":raw-pen,
        "train_global_inner_d_probability":globalp,"train_no_carrier_inner_d_probability":probs["0"],"train_carrier_inner_d_probability":probs["1"]}
def close(a,b,tol=5e-9):return abs(float(a)-float(b))<=tol

def main():
 checks={};rows=reconstruct(read(SOURCE));actual=read(OCC)
 checks["occurrence_inventory_exact"]=actual==rows and len(rows)==774 and not any(row["locus"].startswith("f84r")for row in rows)
 expected_tables=[]
 for register in REGISTERS:
  rr=[row for row in rows if row["register"]==register];counts=Counter(row["cell"]for row in rr)
  for cell in("C0D0","C0D1","C1D0","C1D1"):
   zz=[row for row in rr if row["cell"]==cell];expected_tables.append({"register":register,"cell":cell,"occurrences":str(counts[cell]),
    "physical_folios":str(len({row["physical_folio"]for row in zz})),"complete_line_occurrences":str(sum(row["retained_line_complete"]=="1"for row in zz)),
    "field_positions_complete":";".join(f'{k}:{v}'for k,v in sorted(Counter(row["field_position"]for row in zz if row["retained_line_complete"]=="1").items()))or"NONE"})
 checks["register_tables_exact"]=read(TABLES)==expected_tables
 expected_tests=[exact(rows,(register,))for register in REGISTERS]+[exact(rows,("HB","SB"))];actual_tests=read(TESTS);test_ok=len(actual_tests)==len(expected_tests)
 for stored,expected in zip(actual_tests,expected_tests):
  for key in("registers","occurrences","folios","double_observed","positive_folios","null_min","null_max"):test_ok&=str(expected[key])==stored[key]
  for key in("double_expected","excess","one_sided_enrichment_p","one_sided_depletion_p"):test_ok&=close(stored[key],expected[key])
 checks["folio_exact_tests_reconstructed"]=test_ok
 hb=[row for row in rows if row["register"]=="HB"];sb=[row for row in rows if row["register"]=="SB"]
 expected_predictions=[prediction(hb,sb,"HB","SB"),prediction(sb,hb,"SB","HB")];actual_predictions=read(PRED);pred_ok=len(actual_predictions)==2
 for stored,expected in zip(actual_predictions,expected_predictions):
  for key in("train_register","test_register","train_events","test_events"):pred_ok&=str(expected[key])==stored[key]
  for key in("global_test_bits","conditional_test_bits","raw_gain_bits","additional_parameter_bic_bits","paid_gain_bits","train_global_inner_d_probability","train_no_carrier_inner_d_probability","train_carrier_inner_d_probability"):pred_ok&=close(stored[key],expected[key])
 checks["cross_register_predictions_exact"]=pred_ok
 table={(row["register"],row["cell"]):int(row["occurrences"])for row in actual_tests[:0] for _ in()} # intentionally empty; counts below use inventory
 counts=Counter((row["register"],row["cell"])for row in rows)
 byreg={row["registers"]:row for row in expected_tests}
 checks["headline_counts_and_decision"]=(counts["HB","C1D1"]==6 and counts["SB","C1D1"]==17 and counts["HA","C1D1"]==0 and
  byreg["HB+SB"]["one_sided_enrichment_p"]<.01 and expected_predictions[0]["paid_gain_bits"]>0 and expected_predictions[1]["paid_gain_bits"]<0)
 result=json.loads(RESULT.read_text());body=dict(result);claimed=body.pop("result_content_sha256")
 checks["result_content_hash"]=csha(body)==claimed
 checks["result_status"]=result["status"]=="DAIIN_DECOMPOSES_AS_CURRIER_B_CARRIER_D_AIIN_STACK"
 checks["all_bound_hashes"]=all(sha(ROOT/name)==digest for family in("inputs","outputs","documents")for name,digest in result[family].items())and all(sha(ROOT/name)==digest for name,digest in result["implementation"].items())
 checks["f84_sealed"]=not any(result["f84r"].values())
 report=(ROOT/"GDT040_AIIN_NESTED_WRAPPER_REPORT.md").read_text();checks["claim_ceiling"]=all(text in report for text in("formal Currier-B stack","does not","f84r was not opened"))
 ledger=[row for row in read(LEDGER)if row["checkpoint_id"]=="GDT040_CKPT001"];checks["ledger_exact"]=len(ledger)==1 and ledger[0]["status"]==result["status"]and ledger[0]["result_artifact"]==RESULT.name
 passed=all(checks.values());validation={"schema":"GDT040_AIIN_NESTED_WRAPPER_VALIDATION_V1","status":"PASS_INDEPENDENT_EXACT_RECONSTRUCTION"if passed else"FAIL","checks":checks,"checks_passed":sum(checks.values()),"checks_total":len(checks),"result_sha256":sha(RESULT),"validator_sha256":sha(Path(__file__)),"scope":"Independent inventory, four cells, physical-folio exact tests, cross-register prediction, hashes, claims, and ledger."}
 VALIDATION.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":validation["status"],"checks":f'{validation["checks_passed"]}/{validation["checks_total"]}'},sort_keys=True))
 if not passed:raise SystemExit(1)
if __name__=="__main__":main()
