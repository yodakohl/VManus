#!/usr/bin/env python3
"""Mechanical completeness and no-overclaim checks, not semantic validation."""
import csv,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
e=json.loads((P/'src/EVIDENCE.json').read_text());r=json.loads((P/'artifacts/RESULT.json').read_text())
rows=list(csv.DictReader((P/'artifacts/CANDIDATE_TABLE.tsv').open(),delimiter='\t'))
checks={
 'complete_registered_candidates':[x['id'] for x in rows]==['A','B','C','D'],
 'manual_records_reproduced':all(all(row[k]==str(c[k]) for k in row) for row,c in zip(rows,e['candidates'])),
 'no_selected_translation':not r['selected_candidates'] and r['confirmed_voynich_words']==0,
 'no_new_folio_or_independent_confirmation':r['new_physical_folios']==r['independent_meaning_confirmation_capacity']==0,
 'old_equivalence_stop_retained':not e['native_result']['visible_equivalence_device'],
 'no_significance_claim':not r['significance_claim'],
 'sealed_selectors':['f84','f84r']==e['sealed_selectors'] and e['unadmitted_selectors']==['f116v'],
 'source_receipts_complete':len(e['sources'])==6 and all(s['url'].startswith('https://') and s['locator'] and s['limit'] for s in e['sources']),
 'judgment_limits_explicit':all(c['contradictions_or_costs'] and c['remaining_ambiguity'] for c in e['candidates'])}
v={'status':'PASS' if all(checks.values()) else 'FAIL','scope':'mechanical table completeness and claim limits; does not validate graphemes, historical semantics, chronology or pictorial identity','checks':checks}
(P/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v));raise SystemExit(not all(checks.values()))
