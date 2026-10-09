"""Post-result descriptive decomposition, no new selection or statistical test."""
import json,math
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 result=json.loads((B/'artifacts/RESULT.json').read_text());detail=json.loads((B/'artifacts/DETAILS.json').read_text())
 src=R/'experiments/yolo/gdt1260_lr_line_margin_capacity/artifacts'
 ts=json.loads((src/'TOKENS.json').read_text())['ZL3b'];pairs=json.loads((src/'PAIRS.json').read_text())['ZL3b']
 nom=set(map(tuple,json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/CANDIDATES.json').read_text())))
 owner={i:c for c in detail['ZL3b']['active_cycle_indices'] for i in detail['ZL3b']['cycles'][c]}
 rows=[]
 for pair in pairs:
  a,b=pair['a'],pair['b']
  if tuple(pair['stems']) not in nom or owner.get(a)==owner.get(b):continue
  rows.append({'source_ids':pair['source_ids'],'forms':[ts[a]['word'],ts[b]['word']],'leaf':pair['leaf'],'observed_product':1 if ts[a]['ending']==ts[b]['ending'] else -1,'exact_reference_product_mean':0})
 out={'scope':'Complete ZL nominated pairs with nonconstant individual product under fixed orbit; descriptive decomposition, no new test or meaning','pairs':rows}
 (B/'artifacts/VARIABLE_PAIR_EXAMPLES.json').write_text(json.dumps(out,indent=2)+'\n')
 scales={}
 for reader,r in result['readers'].items():
  sd=math.sqrt(Fraction(r['variance']));scales[reader]={'reference_standard_deviation':sd,'residual_divided_by_sd':float(Fraction(r['residual']))/sd,'warning':'Scale only. No normal approximation, p-value or retrospective criterion.'}
 (B/'artifacts/DESCRIPTIVE_SCALE.json').write_text(json.dumps(scales,indent=2)+'\n')
 print('variable_pairs',len(rows),'same',sum(x['observed_product']==1 for x in rows),'mixed',sum(x['observed_product']==-1 for x in rows))
if __name__=='__main__':main()
