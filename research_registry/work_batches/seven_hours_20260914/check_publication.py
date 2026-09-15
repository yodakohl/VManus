#!/usr/bin/env python3
"""Read-only replay of the session's direct experiment binding check.

Run from the repository root. Does not rerun experiments, inspect private caches,
certify meanings or replace the separately recorded global worktree audit.
"""
from pathlib import Path
import hashlib,json
for number in range(950,962):
    manifests=list(Path('experiments/yolo').glob(f'gdt{number}_*/experiment.json'))
    assert len(manifests)==1,number
    manifest=json.loads(manifests[0].read_text())
    for record in manifest['inputs']+manifest['outputs']:
        source=Path(record['path'])
        assert source.is_file(),str(source)
        assert hashlib.sha256(source.read_bytes()).hexdigest()==record['sha256'],str(source)
    validation=json.loads(Path(manifest['validation']['artifact']).read_text())
    recorded_status=validation.get('status',validation.get('overall',{}).get('validator_status'))
    assert recorded_status=='PASS',number
    print(f'GDT{number}: direct bound bytes match; recorded validator PASS; no semantic certification')
