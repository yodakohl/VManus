#!/usr/bin/env python3
"""GDT040: exact AIIN / D+AIIN / carrier+AIIN / carrier+D+AIIN test."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gdt016_group_state_inventory.tsv"
METHOD = ROOT / "GDT040_AIIN_NESTED_WRAPPER_METHOD.md"
REPORT = ROOT / "GDT040_AIIN_NESTED_WRAPPER_REPORT.md"
OCC = ROOT / "gdt040_aiin_occurrences.tsv"
TABLES = ROOT / "gdt040_register_tables.tsv"
TESTS = ROOT / "gdt040_folio_compatibility_tests.tsv"
PREDICTIONS = ROOT / "gdt040_cross_register_predictions.tsv"
RESULT = ROOT / "gdt040_result.json"
REGISTERS = ("HB", "SB", "HA", "OB")


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csha(value): return hashlib.sha256(json.dumps(value, sort_keys=True,
    ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))
def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)


def register(row):
    if row["section"] == "H" and row["currier"] == "B": return "HB"
    if row["section"] == "S" and row["currier"] == "B": return "SB"
    if row["section"] == "H" and row["currier"] == "A": return "HA"
    return "OB"


def inventory(rows):
    lines=defaultdict(list)
    for row in rows:
        assert not row["locus"].startswith("f84r")
        lines[row["locus"]].append(row)
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
            if row["residual_host"] not in {"aiin","daiin"}:continue
            carrier=row["stripped_prefix"] in {"ch","che","sh"}
            inner=(row["residual_host"]=="daiin"or(not carrier and row["stripped_prefix"]=="d"))
            fi,j=address[index];field,closed=fields[fi];size=len(field)
            if size==1:position="SINGLE"
            elif j==0:position="FIELD_START"
            elif j==size-1:position="FIELD_CLOSE"if closed else"OPEN_FIELD_END"
            elif closed and j==size-2:position="PRECLOSE"
            else:position="FIELD_INTERNAL"
            previous="BOS"if index==0 else line[index-1]["record_state"]
            following="EOS"if index+1==len(line)else line[index+1]["record_state"]
            output.append({"locus":locus,"page":row["page"],"physical_folio":row["physical_folio"],
                "register":register(row),"section":row["section"],"currier":row["currier"],
                "hand":row["hand"],"group_index":row["group_index"],"group_count":row["group_count"],
                "token":row["token"],"frozen_wrapper":row["stripped_prefix"],
                "frozen_residual_host":row["residual_host"],"base_host":"aiin",
                "outer_carrier":str(int(carrier)),"inner_d":str(int(inner)),
                "cell":f'C{int(carrier)}D{int(inner)}',"record_state":row["record_state"],
                "retained_line_complete":str(int(complete)),"field_position":position,
                "previous_state":previous,"following_state":following})
    output.sort(key=lambda row:(REGISTERS.index(row["register"]),row["physical_folio"],
                                row["locus"],int(row["group_index"])))
    return output


def hypergeom(n,successes,draws):
    denominator=math.comb(n,draws);lo=max(0,draws-(n-successes));hi=min(successes,draws)
    return {x:math.comb(successes,x)*math.comb(n-successes,draws-x)/denominator
            for x in range(lo,hi+1)}
def convolve(left,right):
    out=defaultdict(float)
    for a,p in left.items():
        for b,q in right.items():out[a+b]+=p*q
    return dict(out)


def folio_test(rows,registers):
    selected=[row for row in rows if row["register"]in registers]
    by=defaultdict(list)
    for row in selected:by[row["physical_folio"]].append(row)
    pmf={0:1.};observed=0;expected=0.;positive=0
    for folio,items in sorted(by.items()):
        n=len(items);carriers=sum(row["outer_carrier"]=="1"for row in items)
        inner=sum(row["inner_d"]=="1"for row in items)
        both=sum(row["cell"]=="C1D1"for row in items);observed+=both;expected+=carriers*inner/n
        positive+=both>carriers*inner/n
        pmf=convolve(pmf,hypergeom(n,carriers,inner))
    return {"registers":"+".join(registers),"occurrences":len(selected),"folios":len(by),
        "double_observed":observed,"double_expected":expected,"excess":observed-expected,
        "one_sided_enrichment_p":sum(p for x,p in pmf.items()if x>=observed),
        "one_sided_depletion_p":sum(p for x,p in pmf.items()if x<=observed),
        "positive_folios":positive,"null_min":min(pmf),"null_max":max(pmf)}


def predictive(train,test,train_name,test_name):
    def counts(data,key=None):
        z=data if key is None else[row for row in data if row["outer_carrier"]==key]
        return sum(row["inner_d"]=="1"for row in z),len(z)
    successes,total=counts(train);global_p=(successes+.5)/(total+1)
    probs={key:(counts(train,key)[0]+.5)/(counts(train,key)[1]+1)for key in("0","1")}
    global_bits=conditional_bits=0.
    for row in test:
        y=row["inner_d"]=="1";p=global_p;q=probs[row["outer_carrier"]]
        global_bits-=math.log2(p if y else 1-p);conditional_bits-=math.log2(q if y else 1-q)
    raw=global_bits-conditional_bits;penalty=.5*math.log2(len(train))
    return {"train_register":train_name,"test_register":test_name,"train_events":len(train),
        "test_events":len(test),"global_test_bits":global_bits,"conditional_test_bits":conditional_bits,
        "raw_gain_bits":raw,"additional_parameter_bic_bits":penalty,"paid_gain_bits":raw-penalty,
        "train_global_inner_d_probability":global_p,"train_no_carrier_inner_d_probability":probs["0"],
        "train_carrier_inner_d_probability":probs["1"]}


def weighted_jaccard(a,b):
    na=sum(a.values());nb=sum(b.values());shared=sum(min(a[k]/na,b[k]/nb)for k in set(a)|set(b))
    return shared/(2-shared)if shared<2 else 1.


def main():
    rows=inventory(read(SOURCE));assert len(rows)==774 and not any(r["locus"].startswith("f84r")for r in rows)
    write(OCC,rows,list(rows[0]))
    tables=[]
    for reg in REGISTERS:
        rr=[row for row in rows if row["register"]==reg];counts=Counter(row["cell"]for row in rr)
        for cell in("C0D0","C0D1","C1D0","C1D1"):
            cellrows=[row for row in rr if row["cell"]==cell]
            tables.append({"register":reg,"cell":cell,"occurrences":counts[cell],
                "physical_folios":len({row["physical_folio"]for row in cellrows}),
                "complete_line_occurrences":sum(row["retained_line_complete"]=="1"for row in cellrows),
                "field_positions_complete":";".join(f'{k}:{v}'for k,v in sorted(Counter(
                    row["field_position"]for row in cellrows if row["retained_line_complete"]=="1").items()))or"NONE"})
    write(TABLES,tables,list(tables[0]))
    tests=[folio_test(rows,(reg,))for reg in REGISTERS]+[folio_test(rows,("HB","SB"))]
    tfields=list(tests[0]);write(TESTS,[{k:(f'{r[k]:.12g}'if isinstance(r[k],float)else r[k])for k in tfields}for r in tests],tfields)
    hb=[row for row in rows if row["register"]=="HB"];sb=[row for row in rows if row["register"]=="SB"]
    predictions=[predictive(hb,sb,"HB","SB"),predictive(sb,hb,"SB","HB")]
    pfields=list(predictions[0]);write(PREDICTIONS,[{k:(f'{r[k]:.12g}'if isinstance(r[k],float)else r[k])for k in pfields}for r in predictions],pfields)
    position={}
    for cell in("C0D0","C0D1","C1D0","C1D1"):
        a=Counter(row["field_position"]for row in hb if row["cell"]==cell and row["retained_line_complete"]=="1")
        b=Counter(row["field_position"]for row in sb if row["cell"]==cell and row["retained_line_complete"]=="1")
        position[cell]={"hb_n":sum(a.values()),"sb_n":sum(b.values()),
                        "weighted_jaccard":weighted_jaccard(a,b)if a and b else None}
    byreg={row["registers"]:row for row in tests};forward=predictions[0];decision="DAIIN_DECOMPOSES_AS_CURRIER_B_CARRIER_D_AIIN_STACK"
    assert byreg["HB+SB"]["excess"]>0 and byreg["HB+SB"]["one_sided_enrichment_p"]<.01
    assert forward["paid_gain_bits"]>0 and byreg["HA"]["double_observed"]==0
    report=f"""# GDT040 — AIIN nested-wrapper construction

## Outcome

**{decision}**

DAIIN is better represented as a stacked surface construction than as an
indivisible content core. All four AIIN cells occur in Currier B:

| Register | no carrier/no D | no carrier + D | carrier/no D | carrier + D |
|---|---:|---:|---:|---:|
| Herbal B | 29 | 31 | 2 | 6 |
| Stars/Recipe B | 136 | 59 | 11 | 17 |
| Herbal A | 39 | 235 | 29 | 0 |
| Other | 84 | 91 | 1 | 4 |

The double cell recurs on four Herbal-B and five S/B physical folios. With
carrier and inner-D margins fixed separately on every physical folio, HB+S/B
contains {byreg['HB+SB']['double_observed']} double forms versus
{byreg['HB+SB']['double_expected']:.3f} expected (excess
{byreg['HB+SB']['excess']:+.3f}; exact p={byreg['HB+SB']['one_sided_enrichment_p']:.4g}).
S/B alone is positive (p={byreg['SB']['one_sided_enrichment_p']:.4g}); Herbal B
has the same sign but lower capacity (p={byreg['HB']['one_sided_enrichment_p']:.3g}).

Learning only on Herbal B, carrier-conditioned inner-D probabilities save
{forward['raw_gain_bits']:.3f} held S/B bits over a global inner-D rate and
{forward['paid_gain_bits']:.3f} bits after the declared additional-parameter
penalty. The reverse S/B→HB direction saves {predictions[1]['raw_gain_bits']:.3f}
raw bits but {predictions[1]['paid_gain_bits']:.3f} paid bits, so transfer is
directionally asymmetric rather than a perfect invariant.

Herbal A is the decisive contrast: carrier+AIIN occurs 29 times and D+AIIN 235
times on 45 folios, yet carrier+D+AIIN occurs zero times. Its folio-stratified
depletion p is {byreg['HA']['one_sided_depletion_p']:.3g}. The nesting rule is
therefore Currier-B/register-specific, not a manuscript-universal free
concatenation.

The complete-line field-position overlap of the double cell across HB/S is
{position['C1D1']['weighted_jaccard']:.3f} ({position['C1D1']['hb_n']}/
{position['C1D1']['sb_n']} occurrences). That is moderate, not a stable named
role. The construction is reusable and ordered, while its detailed placement
remains register-conditioned.

This supports `[carrier]+[d]+AIIN` as a formal Currier-B stack. It does not
make D, AIIN, or the carrier a morpheme, word, POS, sound, language, plaintext,
meaning, or translation. f84r was not opened, retained, queried, joined, or
scored.
""";REPORT.write_text(report,encoding="utf-8")
    result={"schema":"GDT040_AIIN_NESTED_WRAPPER_RESULT_V1","status":decision,
        "occurrences":len(rows),"register_tables":{reg:{cell:next(x["occurrences"]for x in tables if x["register"]==reg and x["cell"]==cell)for cell in("C0D0","C0D1","C1D0","C1D1")}for reg in REGISTERS},
        "folio_tests":{row["registers"]:row for row in tests},"cross_register_predictions":predictions,
        "complete_line_field_position_overlap":position,
        "claim_ceiling":"Ordered reusable formal wrapper stack only; no morpheme, word, POS, sound, language, plaintext, meaning, or translation.",
        "f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},
        "inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt037_result.json":sha(ROOT/"gdt037_result.json"),"gdt038_result.json":sha(ROOT/"gdt038_result.json")},
        "implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{OCC.name:sha(OCC),TABLES.name:sha(TABLES),TESTS.name:sha(TESTS),PREDICTIONS.name:sha(PREDICTIONS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}}
    result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":decision,"occurrences":len(rows),"combined_p":byreg["HB+SB"]["one_sided_enrichment_p"],"hb_to_sb_paid_bits":forward["paid_gain_bits"],"ha_double":byreg["HA"]["double_observed"]},sort_keys=True))


if __name__=="__main__":main()
