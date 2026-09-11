#!/usr/bin/env python3
import json,hashlib
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parents[1];R=E.parents[2]
s=json.loads((E/'src/SOURCE.json').read_text());im=R/s['image_path'];assert hashlib.sha256(im.read_bytes()).hexdigest()==s['sha256'];assert Image.open(im).size==(2500,3254)
for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
expected={'ROOT_OBSERVATION.json':'c4d76cf3278a65044ed3ebc22c08157cae9fa3294ad330058cf4484ad9ac0bf0','OBSERVER_B.json':'28c18dbcf792ce4aca004dd27ddfedf90fba847d10de6a6a56428d118ab4e779'}
for n,h in expected.items():assert hashlib.sha256((E/'artifacts'/n).read_bytes()).hexdigest()==h
r=json.loads((E/'artifacts/RESULT.json').read_text());a=json.loads((E/'artifacts/ROOT_OBSERVATION.json').read_text());b=json.loads((E/'artifacts/OBSERVER_B.json').read_text());assert a['human_figure_count']==b['human_figures']['count']==4
assert r['four_figures_agree'] and r['two_offset_registers_agree'];assert a['gates']['explicit_cross_register_ownership'] is False and b['gates']['explicit_cross_register_ownership'] is False
assert r['complete_source_capacity'] is False and r['target_binding'] is False and r['confirmed_meanings']==0
assert json.loads((E/'artifacts/POSTFREEZE_AUDIT.json').read_text())['root_month_ring_claim']=='WITHDRAWN'
o={'status':'PASS','checks':['official image bytes/dimensions','preregistered source/protocol locks','both frozen observer bytes','both fourfigure/twooffsetregister reports','unresolved readings and falseownership preserved','root monthring correction explicit','zero targetbinding/meanings'],'coverage':'Receipt consistency and source bytes only; not independent visual truth or diplomatic reading','validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(E/'artifacts/VALIDATION.json').write_text(json.dumps(o,indent=2)+'\n');print(json.dumps(o,indent=2))
