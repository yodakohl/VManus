from pathlib import Path
import json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'ARTIFACT_HASHES.json').read_text()).items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads((D/'SOURCES.json').read_text())
old=json.loads(Path(s['prior_source']).read_text())['source_images']
assert s['images']==[r for r in old if set(r['admitted_page_keys']) & {'f81r','f82r'}]
assert s['sealed']==['f84','f84r'] and not s['new_admission']
out=dict(status='PASS',scope='artifact integrity and prior source metadata only',meaning_validated=False,visual_interpretation_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
