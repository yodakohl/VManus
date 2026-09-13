from pathlib import Path
import json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'ARTIFACT_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads((D/'SOURCES.json').read_text());old=json.loads(Path('docs/visual_overview/FIGURE_ORIENTATION_2026-09-06_SOURCES.json').read_text())['source_images'];assert s==[x for x in old if x['admitted_key']=='f83r']
out=dict(status='PASS',scope='artifact integrity and admitted source metadata only',visual_interpretation_validated=False,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
