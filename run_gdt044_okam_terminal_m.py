#!/usr/bin/env python3
"""GDT044: nest exact OKAM placement inside the terminal-M system."""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import run_gdt039_terminal_m_positional_control as exact
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT/"gdt016_group_state_inventory.tsv";METHOD=ROOT/"GDT044_OKAM_TERMINAL_M_METHOD.md";REPORT=ROOT/"GDT044_OKAM_TERMINAL_M_REPORT.md";OCC=ROOT/"gdt044_okam_complete_occurrences.tsv";TESTS=ROOT/"gdt044_okam_tests.tsv";RESULT=ROOT/"gdt044_result.json"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def read(p):
 with Path(p).open(encoding="utf-8",newline="")as h:return list(csv.DictReader(h,delimiter="\t"))
def write(p,rows,fields):
 with Path(p).open("w",encoding="utf-8",newline="")as h:w=csv.DictWriter(h,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader();w.writerows(rows)
def lines(rows):
 by=defaultdict(list)
 for r in rows:
  assert not r["locus"].startswith("f84r")
  if exact.section(r)in{"HB","SB"}:by[r["locus"]].append(r)
 out=[]
 for locus,line in by.items():
  line.sort(key=lambda r:int(r["group_index"]));n=int(line[0]["group_count"])
  if len(line)!=n or{int(r["group_index"])for r in line}!=set(range(1,n+1)):continue
  last=max([-1]+[i for i,r in enumerate(line)if r["record_state"]=="DY_RESOLUTION"])
  out.append([{**r,"target_section":exact.section(r),"physical_line_end":int(i==n-1),"final_open_field":int(i>last)}for i,r in enumerate(line)])
 return sorted(out,key=lambda z:z[0]["locus"])
def main():
 ls=lines(read(SOURCE));allrows=[r for line in ls for r in line];pred=lambda r:r["residual_host"]=="okam"
 bases={"ALL_GROUPS":lambda r:True,"WITHIN_TERMINAL_M":lambda r:r["residual_host"].endswith("m"),"WITHIN_TERMINAL_AM":lambda r:r["residual_host"].endswith("am"),"WITHIN_TERMINAL_OKM":lambda r:r["residual_host"].startswith("ok")and r["residual_host"].endswith("m")}
 tests=[]
 for name,base in bases.items():
  for outcome in("physical_line_end","final_open_field"):
   z=exact.exact_test(ls,pred,outcome,base);tests.append({"contrast":name,"outcome":outcome,**z})
 for z in tests:z["bonferroni_8_p"]=min(1,z["local_p"]*8)
 fields=list(tests[0]);numeric={"observed_rate","null_expected_hits","null_expected_rate","rate_effect","local_p","lofo_min_rate","lofo_min_effect","bonferroni_8_p"};write(TESTS,[{k:f"{v:.12g}"if k in numeric else v for k,v in z.items()}for z in tests],fields)
 occ=[]
 for r in allrows:
  if pred(r):occ.append({k:str(r[k])for k in("locus","page","physical_folio","target_section","hand","group_index","group_count","token","stripped_prefix","residual_host","record_state","physical_line_end","final_open_field")})
 occ.sort(key=lambda r:(r["physical_folio"],r["locus"],int(r["group_index"])));write(OCC,occ,list(occ[0]))
 q={(r["contrast"],r["outcome"]):r for r in tests};raw=q["ALL_GROUPS","physical_line_end"];nested=q["WITHIN_TERMINAL_M","physical_line_end"];field=q["WITHIN_TERMINAL_M","final_open_field"]
 decision="OKAM_PLACEMENT_ATTRIBUTED_TO_TERMINAL_M_SYSTEM";assert raw["rate_effect"]>.5 and nested["local_p"]>=.5 and field["rate_effect"]==0
 report=f"""# GDT044 — OKAM terminal-M attribution

## Outcome

**{decision}**

Six of the sixteen GDT038 `OKAM` occurrences lie on completely retained HB/S
physical lines. Five of those six are line-final. Against all groups this is a
large apparent effect: {raw['observed']}/{raw['family_n']} observed versus
{raw['null_expected_hits']:.3f} expected, effect {raw['rate_effect']:+.3f},
local p={raw['local_p']:.3g}.

The effect does not survive the correct parent control. Within terminal-M
forms, the same 5/6 compares with {nested['null_expected_hits']:.3f} expected
(effect {nested['rate_effect']:+.3f}, p={nested['local_p']:.3g}, minimum
leave-folio effect {nested['lofo_min_effect']:+.3f}). For final-open-field
membership, exact OKAM is 5/6 observed and 5.000 expected within terminal M:
effect {field['rate_effect']:+.3f}, p={field['local_p']:.3g}. Terminal-AM and
terminal-OK...M controls are equally non-specific.

OKAM's late placement is therefore inherited from the terminal-M system. Its
section-dependent wrapper mixture remains real, but neither exact OKAM nor an
OKAM meaning is identified. This completes formal attribution of all four
GDT038 hosts: DAIIN to carrier+D, DAM and OKAM to terminal M, and ODAIN to the
OD+AIN/AIIN short/long system.

No function, word, morpheme, POS, sound, language, plaintext, meaning, or
translation is assigned. f84r was not opened, retained, queried, joined, or
scored.
""";REPORT.write_text(report,encoding="utf-8")
 result={"schema":"GDT044_OKAM_TERMINAL_M_RESULT_V1","status":decision,"complete_hb_sb_lines":len(ls),"complete_hb_sb_groups":len(allrows),"complete_okam_occurrences":len(occ),"raw_physical_line_end":raw,"within_terminal_m_physical_line_end":nested,"within_terminal_m_final_open_field":field,"claim_ceiling":"Exact OKAM placement attributed to terminal-M positional system only; no function, word, morpheme, POS, sound, language, plaintext, meaning, or translation.","f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False},"inputs":{"gdt016_group_state_inventory.tsv":sha(SOURCE),"gdt016_result.json":sha(ROOT/"gdt016_result.json"),"gdt038_result.json":sha(ROOT/"gdt038_result.json"),"gdt039_result.json":sha(ROOT/"gdt039_result.json")},"implementation":{Path(__file__).name:sha(Path(__file__)),"run_gdt039_terminal_m_positional_control.py":sha(ROOT/"run_gdt039_terminal_m_positional_control.py")},"outputs":{OCC.name:sha(OCC),TESTS.name:sha(TESTS)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)}};result["result_content_sha256"]=csha(result);RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":decision,"complete":len(occ),"raw_p":raw["local_p"],"nested_p":nested["local_p"],"nested_effect":nested["rate_effect"]},sort_keys=True))
if __name__=="__main__":main()
