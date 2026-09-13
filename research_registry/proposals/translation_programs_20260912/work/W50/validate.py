"""Source/artifact check only; cannot validate a person's visual interpretation."""
from pathlib import Path
import csv,hashlib,json
D=Path(__file__).parent
for p,h in json.loads((D/'ARTIFACT_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
old=list(csv.DictReader(Path('experiments/yolo/gdt812_additional_page_semantic_bridge/src/IMAGE_SOURCES.tsv').open(),delimiter='\t'))
s=json.loads((D/'SOURCES.json').read_text());assert len(s)==3
for r in s:assert any(x['image_url']==r['url'] and x['sha256']==r['sha256'] for x in old)
out=dict(status='PASS',source_images=3,scope='artifact hashes and parity with previously admitted image metadata only',visual_interpretation_validated=False,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
