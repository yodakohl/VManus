"""Replay the selector-first source packet and exact existing statements.
Provenance/coverage validation only: no new decoder or occupancy simulation.
"""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'research_registry/proposals'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    receipt = json.loads((P / 'raw479_source_receipt_20260922.json').read_text())
    for path_key, hash_key in [('decision_path', 'decision_sha256'), ('raw_path', 'raw_sha256')]:
        assert sha(ROOT / receipt[path_key]) == receipt[hash_key]
    for binding in receipt['raw_source_bindings']:
        assert sha(ROOT / binding['path']) == binding['sha256']
    rows = []
    for packet in receipt['replays']:
        assert sha(ROOT / packet['source_path']) == packet['source_sha256']
        assert sha(ROOT / packet['output_path']) == packet['output_sha256']
        cmd = ['./vmanus-exp', 'query-tsv', packet['source_path'], '--selector', packet['selector']]
        for value in packet['allow']:
            cmd += ['--allow', value]
        cmd += ['--columns', ','.join(packet['columns'])]
        r = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
        assert r.stdout == (ROOT / packet['output_path']).read_text()
        stats = json.loads(r.stderr.split('GUARD_STATS ', 1)[1])
        assert stats == packet['guard_stats']
        selected = list(csv.DictReader(io.StringIO(r.stdout), delimiter='\t'))
        assert len(selected) == packet['guard_stats']['selected']
        assert {x['physical_page'] for x in selected} == {'f81r', 'f81v'}
        rows.append(selected)
    hosts, actions = rows
    assert len(hosts) == 14 and len(actions) == 10
    hbykey = {h['primary_governor_key']: h for h in hosts}
    assert set(hbykey) == {a['primary_governor_key'] for a in actions} | {h['primary_governor_key'] for h in hosts if h['action_root'] == 'CONTROL'}
    for a in actions:
        h = hbykey[a['primary_governor_key']]
        for field in a.keys() & h.keys():
            assert a[field] == h[field]
    raw = json.loads((ROOT / receipt['raw_path']).read_text())
    outcomes = []
    for stated in raw['complete_existing_statements']:
        hs = [h for h in hosts if h['statement_id'] == stated['id']]
        assert [int(h['host_ordinal_in_statement']) for h in hs] == list(range(1, len(hs)+1))
        text = '. '.join(h['gdt599_complete_clause_de'] for h in hs)+'.'
        assert text == stated['text']
        for b in stated['bindings']:
            h = hbykey[b['host']]
            for k in ('object_class', 'reference_mode', 'source_pointer'):
                assert h[k] == b[k]
        assert hs[-1]['paragraph_boundary'] == 'PARAGRAPH_AFTER'
        outcomes.append({'statement_id':stated['id'], 'page':hs[0]['physical_page'], 'hosts':len(hs), 'actions':sum(h['action_root']!='CONTROL' for h in hs), 'complete_existing_reader':text, 'reference_chains_match_raw':True})
    result = {'status':'PASS_GUARDED_PROVENANCE_COMPLETE_UNITS_AND_REFERENCES_ONLY','statements':outcomes,'all_10_original_bindings_match':True,'all_10_raw_source_hashes_match':True,'new_words':0,'limit':'No actual bath identity, chronology, occupancy, word meaning or full physical feasibility is validated. Conditional consequences are separately reviewed by hand.'}
    (P/'raw479_source_validation_20260922.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
    main()
