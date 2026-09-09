"""Validate source provenance and receipt consistency, not visual truth."""
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]
def read(n): return json.loads((p/'artifacts'/n).read_text())
s,b,r=read('SOURCE.json'),read('OBSERVER_B.json'),read('RESULT.json')
assert s['label']==b['source_label']=='38r'
assert s['canvas']==b['canvas'] and s['image_sha256']==b['image_sha256']
assert s['canvas'].endswith('/MSS_Vat.lat.3468.pt.1/canvas/p0089')
assert s['image_url'].startswith('https://digi.vatlib.it/iiifimage/MSS_Vat.lat.3468.pt.1/')
assert [x['left_to_right'] for x in b['figures']]==[1,2,3,4]
assert [x['red_label_literal'].lower().replace('ua','va') for x in b['figures']]==[x.lower() for x in r['left_to_right_normalized']]
assert len(read('OBSERVER_ROOT.json')['figures'])==4
assert r['complete_required_conjunction'] is False and len(r['unconfirmed_functions'])==2
assert r['voynich_targets_selected']==r['voynich_pages_opened']==r['meanings_confirmed']==0
v={'status':'PASS','scope':'Source/receipt consistency only; no independent visual truth or semantic validation.'}
(p/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v))
