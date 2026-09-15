#!/usr/bin/env python3
"""Reproduce the recorded manual candidate comparison; no image recognition."""
import csv, json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
e=json.loads((P/'src/EVIDENCE.json').read_text())
fields=['id','prediction','observed','contradictions_or_costs','remaining_ambiguity','status','selected_translation']
with (P/'artifacts/CANDIDATE_TABLE.tsv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(e['candidates'])
r={k:e[k] for k in ['experiment_id','mode','decision','confirmed_voynich_words','independent_meaning_confirmation_capacity','significance_claim']}
r.update(status='CONTEXTUAL_HYPOTHESES_RETAINED_NO_COMPLETE_READING',candidate_count=len(e['candidates']),selected_candidates=[c['id'] for c in e['candidates'] if c['selected_translation']],new_physical_folios=e['image']['new_physical_folios'],figure_caption_correction=True)
(P/'artifacts/RESULT.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r,ensure_ascii=False))
