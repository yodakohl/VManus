#!/usr/bin/env python3
"""Check fixed IDEA588 bytes and literal accounting, never meaning validity."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read_tsv(p):
    with p.open(newline='') as f:
        r = csv.DictReader(f, delimiter='\t')
        return list(r), r.fieldnames

def main():
    receipt = json.loads((BASE/'PERCEPTION_WHOLE_AUTHOR_FREEZE_RECEIPT.json').read_text())
    for name, spec in receipt['files'].items():
        p = BASE/name
        assert digest(p) == spec['sha256'], name
        assert len(p.read_bytes()) == spec['bytes'], name
    inp = receipt['input_hashes']
    safe = ROOT/inp['safe_projection']
    assert digest(safe) == inp['safe_projection_sha256']
    for name, sha in inp['source_inputs'].items():
        p = BASE/name
        if not name.startswith('external_cache/'):
            assert digest(p) == sha, name
    rows, fields = read_tsv(safe)
    out, out_fields = read_tsv(BASE/'PERCEPTION_WHOLE_AUTHOR_473_CONSEQUENCES.tsv')
    x = json.loads((BASE/'PERCEPTION_WHOLE_AUTHOR_DRAFT.json').read_text())
    assert len(rows) == len(out) == 473 and len(fields) == 12
    assert out_fields[:12] == fields
    assert [{k:r[k] for k in fields} for r in out] == rows
    assert x['all473_consequences'] == out
    assert len({r['source_group_id'] for r in out}) == 473
    lex = x['lexicon']
    assert len(lex) == 115 and len(x['grammar']) == 38
    for form, entry in lex.items():
        owned = [r for r in out if r['ivtff_group_raw'] == form]
        assert [r['source_group_id'] for r in owned] == entry['all_occurrences'], form
        for r in owned:
            assert r['assigned_value'] == entry['value'], r['source_group_id']
            assert r['assigned_type'] == entry['type'], r['source_group_id']
            assert r['argument_requirements'] == entry['argument_requirements']
            assert r['binding_effects'] == entry['binding_effects']
    zl = [r for r in rows if r['edition'] == 'ZL3b']
    clauses = x['manual_clauses']
    assert len(clauses) == 9
    assert [i for c in clauses for i in c['source_ids']] == [r['source_group_id'] for r in zl]
    assert [w for c in clauses for w in c['literal_words']] == [r['ivtff_group_raw'] for r in zl]
    counts = {}
    for edition in ['ZL3b','IT2a','RF1b']:
        rr = [r for r in out if r['edition'] == edition]
        assigned = sum(r['ivtff_group_raw'] in lex for r in rr)
        counts[edition] = {'rows':len(rr),'assigned':assigned,'unknown':len(rr)-assigned}
    assert counts == {'ZL3b':{'rows':156,'assigned':156,'unknown':0}, 'IT2a':{'rows':157,'assigned':136,'unknown':21}, 'RF1b':{'rows':160,'assigned':128,'unknown':32}}
    assert sum(e['payload_lower_bound'] for e in lex.values()) == 158
    print(json.dumps({'status':'FIXED_BYTES_AND_LITERAL_ACCOUNTING_PASS','counts':counts,'whole_manual_content_rows':156,'typed_completion_validated':False,'meaning_validated':False,'known_formal_interface_gaps':2},indent=2))

if __name__ == '__main__':
    main()
