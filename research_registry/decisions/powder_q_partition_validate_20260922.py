"""Check frozen offer coverage; this does not validate its meanings."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'research_registry/proposals'
offer_path = BASE / 'raw370_q_partition_composition_offer_20260922.json'
offer = json.loads(offer_path.read_text())
assert hashlib.sha256(offer_path.read_bytes()).hexdigest() == '57808d1291a9b47839e047112ea5395e76a647f7c22986f62b6807d9818845c1'
parents = {}
for item in offer['parents']:
    path = ROOT / item['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
    parents[path.name] = json.loads(path.read_text())
v1 = parents['raw370_two_paragraph_powder_partition_offer_20260922.json']
v2 = parents['raw370_powder_partition_v2_material_contract_20260922.json']
f4 = parents['raw370_f4r_complete_extension_attempt_20260922.json']
for key, value in offer['frozen_inherited_blocks'].items():
    assert value == v1[key], key
assert offer['frozen_global_effects'] == v2['global_effects']
assert offer['frozen_nominal_compatibility'] == v2['nominal_compatibility']
lex = v1['lexicon']
alts = v1['alternative_reading_values']
qkeys = sorted(k for k in lex.keys() | alts.keys() if k.startswith('q'))
assert qkeys == sorted(x['form'] for x in offer['all_fixed_q_forms'])
for item in offer['all_fixed_q_forms']:
    assert item['unchanged_entry'] == lex[item['form']]
    assert item['raw_remainder'] == item['form'][1:]
    assert item['unchanged_base_entry'] == lex[item['raw_remainder']]
groups = [g for p in v1['complete_positional_alignment'] for line in p['lines'] for g in line['groups']]
assert [g for g in groups if g['ivtff_group_raw'].startswith('q')] == offer['all_fixed_q_positions']
assert len(groups) == 238 and len(lex) == 65 and len(alts) == 15
assert offer['known_f4r_unpaired_q_entry'] == f4['new_exact_form_values']['qotey']
assert [g for rows in f4['complete_positional_alignment'].values() for g in rows
        if g['raw'].startswith('q')] == offer['known_f4r_q_positions']
assert 'otey' not in lex.keys() | alts.keys() | f4['new_exact_form_values'].keys()
assert hashlib.sha256((ROOT / offer['human_report']).read_bytes()).hexdigest() == offer['human_report_sha256']
print(json.dumps({'status': 'PASS_COVERAGE_AND_FROZEN_BYTES_ONLY', 'parents': 4,
    'unchanged_blocks': len(offer['frozen_inherited_blocks']), 'primary_forms': len(lex),
    'alternate_forms': len(alts), 'reader_positions': len(groups),
    'paired_q_forms': len(qkeys), 'q_positions': len(offer['all_fixed_q_positions']),
    'independent_meaning_confirmation': 0}, indent=2))
