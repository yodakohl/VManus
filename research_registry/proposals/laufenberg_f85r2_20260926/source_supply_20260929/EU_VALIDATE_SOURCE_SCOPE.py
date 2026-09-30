"""Reproduce EU span, fixed-value and whole-context conservation; no meaning scorer."""
import json, hashlib
from pathlib import Path
P = Path('research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929')
load = lambda name: json.loads((P / name).read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()
source = load('EU_SOURCE_BEARERS.json')
review = load('EU_ACTUAL_CONTEXT_REVIEW.json')
et = load('ET_F111R_AUTHOR.json')
es = load('ES_JOINT_FAMILY_AUTHOR.json')
primary = load('H_DIOSCORIDES_II_164_COMPLETE.json')
for path, expected in source['source']['read_file_hashes'].items():
    assert sha(Path(path).read_bytes()) == expected, path
for path, expected in review['primary_sha256'].items():
    assert sha(Path(path).read_bytes()) == expected, path
sections = primary['main_text_paragraphs']
assert len(sections) == 4
assert [sha(s.encode()) for s in sections] == source['source']['section_sha256_utf8']
for clause in source['clause_bearers']:
    span = clause['span']
    text = sections[span['section'] - 1][span['unicode_start_inclusive']:span['unicode_end_exclusive']]
    assert sha(text.encode()) == span['utf8_sha256'], clause['id']
xml = (P / 'H_DIOSCORIDES_II_164_XML.txt').read_text()
assert '<ns0:del>' in xml and 'χυλὸς</ns0:del>' in xml and 'delevi' in xml
counts = {}
for row in review['whole_known_clauses']:
    unit, edition, model = row['unit'], row['edition'], row['model']
    if unit == 'ET':
        original = et['full_native_focus_G_I_renderings'][edition][model]
        parent = et['parent_values_unchanged']
        mapping = dict(parent['parent32'][model]['dictionary'])
        mapping.update(parent['EQ14']); mapping.update(parent['ES13'])
        mapping.update(et['new_whole_outputs'])
        expected_size = 61
    else:
        original = next(u for u in es['complete_native_G_I_renderings'][edition][model] if u['id'] == row['native_id'])
        mapping = dict(es['parent32_models_unchanged'][model]['dictionary'])
        mapping.update(es['prospective_EQ14_unchanged']); mapping.update(es['new_exact_whole_values'])
        expected_size = 59
    assert len(mapping) == expected_size
    canonical = json.dumps(mapping, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    assert sha(canonical) == review['fixed_whole_values'][model][f'{unit}{expected_size}_sha256_canonical_json']
    original_rows = [(line['locus'], [(g['source_id'], g['raw'], g['value']) for g in line['groups']]) for line in original['lines']]
    projected_rows = [(line['locus'], [(g['source_id'], g['raw'], g['frozen_value']) for g in line['groups']]) for line in row['whole_known_and_unknown_clauses']]
    assert projected_rows == original_rows
    groups = [g for line in row['whole_known_and_unknown_clauses'] for g in line['groups']]
    assert len(groups) == row['total_groups']
    assert sum(g['frozen_value'] is not None for g in groups) == row['known_groups']
    assert all(g['frozen_value'] == mapping.get(g['raw']) for g in groups)
    counts[f'{unit}/{edition}/{model}'] = len(groups)
assert len(counts) == 8
assert all(r['RETURN'] == 'UNBOUND' or 'UNBOUND' in r['RETURN'] for r in review['RETURN_vs_JUICE_CARRY_table'])
assert review['claim_ceiling']['confirmed_words'] == 0
print(json.dumps({'status': 'MECHANICAL_SOURCE_AND_SCOPE_PASS', 'source_clauses': len(source['clause_bearers']), 'source_sections': 4, 'whole_context_groups': counts, 'maps': '59ES/61ET G/I unchanged', 'semantic_validation': False}))
