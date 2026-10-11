from pathlib import Path
from fractions import Fraction
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def main():
 correction=read(B/'artifacts/REPORT_CORRECTION_20261011.json')
 for p,h in correction['source_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 tables=read(B/'artifacts/ALL_HEAD_COUNTS.json');result=read(B/'artifacts/RESULT.json')
 for ed,rows in tables.items():
  facts=correction['facts'][ed];ratio=lambda row:Fraction(*row['bound_among_parsable']);g=facts['global'];a=facts['budget_minimum'];assert g in rows and a in rows;assert g['heads']==['a','o','y'] and a['heads']==['a','e','o'];assert ratio(g)==min(map(ratio,rows));assert facts['ten_percent_budget']==result['readers'][ed]['groups']//10;assert ratio(a)==min(ratio(r) for r in rows if r['unparsed']<=facts['ten_percent_budget']);assert facts['global_percent']==100*float(ratio(g));assert facts['budget_minimum_percent']==100*float(ratio(a));assert ratio(g)<ratio(a)
  frontier=result['readers'][ed]['frontier'];assert Fraction(*frontier[-1]['lower_bound'])==ratio(g) and frontier[-1]['unparsed']==g['unparsed']
 report=(B/'REPORT.md').read_text();assert 'Even the minimum over ALL relaxed heads remains a7–8%' not in report;assert 'Correction11October2026' in report
 print(json.dumps({'status':'PASS','readers':3,'head_rows':sum(map(len,tables.values())),'original_data_and_outputs_unchanged':True,'scope':'Exact rational global and bounded optimum qualification; not new native evidence.'}))
if __name__=='__main__':main()
