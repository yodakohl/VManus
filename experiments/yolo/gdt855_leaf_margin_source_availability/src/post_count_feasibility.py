"""Post-count decision audit, added after metadata discovery; not preregistered."""
import hashlib,itertools,json,re
from fractions import Fraction
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
paths={
 'remainder':E/'artifacts/REMAINDER.json',
 'old_counts':ROOT/'experiments/semantic_assumptions/results/lm001y_final_residual_leaf_margin_census_result_report.md',
 'visual_contract':ROOT/'experiments/semantic_assumptions/LM001_HERBAL_LEAF_MARGIN_VISUAL_CAPACITY_METHOD.md',
 'formal_contract':ROOT/'experiments/semantic_assumptions/LM002_LEAF_MARGIN_CHO_CHE_REGIME_METHOD.md',
}
rows=json.loads(paths['remainder'].read_text());folios=sorted({r['physical_folio'] for r in rows})
assert folios==['f35','f36','f37'] and len(rows)==6
assert all(r['quire']=='q05' for r in rows)
old=paths['old_counts'].read_text()
assert re.search(r'29 smooth,\s*13 toothed,\s*and 2 uncertain',old)
assert 'q02, q05, and q06 at 3/13 each' in old
assert 'no single quire contributes more than 25%' in paths['visual_contract'].read_text().lower()
assert 'acquisition phase × Currier' in paths['formal_contract'].read_text()
cases=[]
for labels in itertools.product(['SMOOTH','TOOTHED','UNCERTAIN'],repeat=3):
 t=labels.count('TOOTHED');share=Fraction(3+t,13+t)
 cap=share<=Fraction(1,4)
 # Presence of TOOTHED is necessary, not sufficient, for new-phase mobility.
 necessary=t>0
 assert not (cap and necessary)
 cases.append(dict(labels=list(labels),new_toothed=t,q05_toothed_share=str(share),quire_cap_holds=cap,new_phase_toothed_present=necessary))
out=dict(status='NO_EXTENSION_CAN_PRESERVE_QUIRE_CAP_AND_ADD_PHASE_MOBILITY',
 analysis_timing='POST_COUNT_NOT_PREREGISTERED',physical_folios=folios,
 assumptions=['old panel retained','one selected page per new physical folio','new acquisition phase','original class-specific quire cap'],
 old_toothed=13,old_q05_toothed=3,cases=cases,
 inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()},
 images_accessed=False,formal_target_accessed=False,semantic_validation=False)
(E/'artifacts/POST_COUNT_FEASIBILITY.json').write_text(json.dumps(out,sort_keys=True,separators=(',',':'))+'\n')
print(out['status'],len(cases),'possible leaf-state assignments checked')
