from pathlib import Path
import json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'ARTIFACT_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads((D/'SOURCES.json').read_text());old=json.loads(Path('experiments/yolo/gdt844_ychor_visual_subentry/artifacts/SOURCES.json').read_text())['images'];assert s==old
r=json.loads((D/'RESULT.json').read_text());assert r['pages']==['f6v','f9v'] and r['new_admissions']==0 and not r['f99r_access']
out=dict(status='PASS',scope='artifact integrity and original source metadata only; manual observations are not machine validated',source_images=2,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
