#!/usr/bin/env python3
"""Root executes the frozen author; separate validator reimplements predictions."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
SELECTED = 'IT2a|f83r.25|G004'
OTHER = 'IT2a|f83r.28|G004'
NAMES = ('baseline', 'delete_selected_edge', 'change_relation_root', 'swap_endpoints',
         'toggle_origin_role', 'change_origin_root', 'forge_producer_id', 'substitute_other_written_producer')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    lock_path = BASE/'artifacts/AUTHOR_LOCK.json'
    lock = json.loads(lock_path.read_text())
    assert sha(lock_path) == '993147a54c2cde15d8c8c2ea05ff1103abe4e2d872c1c944f56b2ea6d2333208'
    for rel, digest in lock['files'].items():
        assert sha(ROOT/rel) == digest, rel
    spec = importlib.util.spec_from_file_location('frozen_author', BASE/'src/author.py')
    author = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(author)
    account = json.loads((BASE/'artifacts/AUTHOR_ACCOUNT.json').read_text())
    frozen = {x['policy']:x for x in account['policy_executions']}
    results = []
    for policy in author.POLICIES:
        for name in NAMES:
            def transform(edge):
                if edge['producer'] != SELECTED or name == 'baseline':
                    return edge
                if name == 'delete_selected_edge':
                    return None
                if name == 'change_relation_root':
                    edge['root'] = 'LOVE'
                elif name == 'swap_endpoints':
                    edge['origin'], edge['destination'] = edge['destination'], edge['origin']
                elif name == 'toggle_origin_role':
                    edge['origin']['role'] = 'RECEPTIVE' if edge['origin']['role'] == 'ACTIVE' else 'ACTIVE'
                elif name == 'change_origin_root':
                    edge['origin']['root'] = 'LOVE'
                elif name == 'forge_producer_id':
                    edge['producer'] = 'INTERVENTION_ONLY_NO_WRITTEN_PRODUCER'
                elif name == 'substitute_other_written_producer':
                    edge['producer'] = OTHER
                return edge
            result = author.execute(policy, None if name == 'baseline' else transform)
            if name == 'baseline':
                assert result == frozen[policy]
            results.append({'policy':policy, 'intervention':name, 'result':result})
    artifact = {
        'status':'EXECUTED_ROOT_PROBES_NOT_INDEPENDENT_IMPLEMENTATION',
        'author_lock_sha256':sha(lock_path), 'probe_code_sha256':sha(Path(__file__)),
        'scope':'Actual frozen author dependency interventions; no dictionary, source or author-byte changes.',
        'interpretation':'Mutations are computational causal probes, not observed manuscript variants or additional semantic evidence.',
        'selected_producer':SELECTED, 'rows':results,
        'baseline_exact_replay':True, 'independent_validation':'Separate src/validate.py reimplements outcomes without importing author or runner.'}
    (BASE/'artifacts/ROOT_PROBES.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k!='result'}|{'outcome':r['result']['status']} for r in results],indent=2))
if __name__ == '__main__':
    main()
