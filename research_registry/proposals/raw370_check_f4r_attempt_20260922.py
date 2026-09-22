#!/usr/bin/env python3
"""Exact source/inheritance check; does not validate proposed meaning."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'research_registry/proposals/raw370_f4r_complete_extension_attempt_20260922.json'
assert hashlib.sha256(path.read_bytes()).hexdigest() == '677776574fd892b7034d999f59e521054172eeef907f5020c1de704767cb0ba8'
x = json.loads(path.read_text())
for name, sha in [('parent_contract', 'parent_contract_sha256'), ('selected_source', 'selected_source_sha256'), ('human_report', 'human_report_sha256')]:
    assert hashlib.sha256((ROOT / x[name]).read_bytes()).hexdigest() == x[sha], name
v2 = json.loads((ROOT / x['parent_contract']).read_text())
old = v2['unchanged_inherited_blocks']
assert x['frozen_original_lexicon'] == old['lexicon']
assert x['frozen_reader_aliases'] == old['alternative_reading_values']
assert x['frozen_surface_productions'] == old['schematic_productions']
assert x['frozen_global_effects'] == v2['global_effects']
selected = json.loads((ROOT / x['selected_source']).read_text())
assert x['selected_paragraphs'] == selected['paragraphs']
lex = x['frozen_original_lexicon']
new = x['new_exact_form_values']
assert not (lex.keys() & new.keys())
counts = {}
for reader, paragraph in x['selected_paragraphs'].items():
    expected = [(sid, word) for line in paragraph['lines'] for sid, word in zip(line['source_ids'], line['words'], strict=True)]
    actual = x['complete_positional_alignment'][reader]
    assert [(row['source_id'], row['raw']) for row in actual] == expected
    for row in actual:
        w = row['raw']
        assert row['value'] == (lex[w] if w in lex else new[w])
        assert row['status'] == ('FROZEN_OLD_VALUE' if w in lex else 'NEW_UNCONFIRMED_PROPOSAL')
    counts[reader] = {'positions': len(actual), 'fixed_positions': sum(r['raw'] in lex for r in actual), 'new_types': len({r['raw'] for r in actual if r['raw'] not in lex})}
assert counts == {'ZL3b': {'positions': 31, 'fixed_positions': 17, 'new_types': 13}, 'IT2a': {'positions': 31, 'fixed_positions': 18, 'new_types': 12}}
assert len(new) == 13
assert len(x['rivals']) == len(x['preserved_unsuccessful_variants']) == 4
print(json.dumps({'status': 'PASS', 'readers': counts, 'frozen_values': len(lex), 'frozen_aliases': len(x['frozen_reader_aliases']), 'frozen_productions': len(x['frozen_surface_productions']['rules']), 'semantic_model_executed': False, 'meaning_validation': False}))
