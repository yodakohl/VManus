#!/usr/bin/env python3
"""Receipt and complete-visible-line accounting; does not validate native meaning."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
r=json.loads((P/'BERLIN_MERCURY_PAGE_RECEIPTS.json').read_text())
assert hashlib.sha256((P/'BERLIN_MERCURY_PAGE_DECISION.md').read_bytes()).hexdigest()==r['decision_sha256']
assert hashlib.sha256((P/'BERLIN_MERCURY_PAGE_ROOT.md').read_bytes()).hexdigest()==r['root_report_sha256']
unit=(P/'BERLIN_MERCURY_PAGE_ROOT.md').read_text().split('~~~')[1]
a,b=unit.split('\nB\n')
assert [int(n) for n in re.findall(r'^(\d{2}) ',a,re.M)]==list(range(1,26))
assert [int(n) for n in re.findall(r'^(\d{2}) ',b,re.M)]==list(range(1,25))
assert r['visible_baselines']==49 and r['folio']=='22r' and r['canvas']==47
assert r['new_voynich_access'] is False and r['confirmed_words']==0
f=ROOT/r['path']
if f.exists():
 data=f.read_bytes();assert len(data)==r['bytes'];assert hashlib.sha256(data).hexdigest()==r['sha256']
print(json.dumps({'status':'PASS_RECEIPTS_AND_BASELINES_ONLY','visible_baselines':49,'image_cache_hash_checked':f.exists(),'scope':'No automatic validation of palaeography, object identification or manuscript meaning.'}))
