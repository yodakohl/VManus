"""Check frozen whole-offer provenance and coverage, not meaning or physics.
Run from repository root with Python 3; only owned, already guarded rows are read.
"""
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'research_registry/proposals'

def read(name):
    return json.loads((P / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    offer_path = P / 'raw512_f37v_powder_whole_working_offer_20260922.json'
    assert sha(offer_path) == '1fb4ceeccf6f5fe85ee455760ba5e365e1f6627f00031e8c0efebbaf88ad5a3a'
    x = json.loads(offer_path.read_text())
    v1 = read('raw370_two_paragraph_powder_partition_offer_20260922.json')
    v2 = read('raw370_powder_partition_v2_material_contract_20260922.json')
    f4 = read('raw370_f4r_complete_extension_attempt_20260922.json')
    assert sha(ROOT / x['frozen_parent']['path']) == x['frozen_parent']['sha256']
    assert sha(ROOT / x['additional_known_family_constraint']['path']) == x['additional_known_family_constraint']['sha256']
    assert sha(ROOT / x['human_report']) == x['human_report_sha256']
    parent = x['frozen_parent']
    assert parent['all_65_lexical_entries'] == v1['lexicon']
    assert parent['all_15_alternate_entries'] == v1['alternative_reading_values']
    assert parent['global_effects'] == v2['global_effects']
    assert parent['nominal_compatibility'] == v2['nominal_compatibility']
    assert x['additional_known_family_constraint']['dchor'] == f4['new_exact_form_values']['dchor']
    src = ROOT / x['source_packet']
    assert sha(src) == x['source_packet_sha256']
    # This packet contains only the 88 preselected f37v groups; no mixed source read.
    with src.open() as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
    aligned = x['complete_88_group_alignment']
    assert len(rows) == len(aligned) == 88
    keys = rows[0].keys()
    assert rows == [{k: a[k] for k in keys} for a in aligned]
    assert {r['page'] for r in rows} == {'f37v'}
    lex = dict(v1['lexicon'])
    assert not (set(lex) & set(x['new_exact_form_entries']))
    lex.update(v1['alternative_reading_values'])
    lex['dchor'] = f4['new_exact_form_values']['dchor']
    lex.update(x['new_exact_form_entries'])
    unknown = {ed: [] for ed in ['ZL3b', 'IT2a', 'RF1b']}
    for row in aligned:
        raw = row['ivtff_group_raw']
        assert row['lexical_entry'] == lex.get(raw)
        if raw not in lex:
            unknown[row['edition']].append(raw)
    assert unknown == {'ZL3b': [], 'IT2a': ['kshody', 'oscho'], 'RF1b': ['kshody', 'chop@152;ain', 'qotchon', '@152;aiin']}
    zl = [r for r in rows if r['edition'] == 'ZL3b']
    ordered = [r['source_group_id'].split('|', 1)[1].replace('|', '/') for r in zl]
    assert [p for c in x['whole_zl_clause_partition'] for p in c['positions']] == ordered
    productions = {p['id']: p for p in x['actually_used_productions']}
    old = {p['id']: p for p in v1['schematic_productions']['rules']}
    assert set(productions) == {'I1', 'N1', 'N2', 'A1', 'G2', 'Q1'}
    for pid in set(productions) - {'Q1'}:
        assert productions[pid] == old[pid]
    used = {p for c in x['whole_zl_clause_partition'] for p in re.findall(r'\b([A-Z][0-9]+)\(', c['production_tree'])}
    assert used == set(productions)
    assert len(x['new_exact_form_entries']) == 20
    assert len(x['explicit_bindings']) == 8
    assert len({r['ivtff_group_raw'] for r in zl}) == 25
    result = {
        'status': 'PASS_PROVENANCE_COVERAGE_AND_LITERAL_INHERITANCE_ONLY',
        'offer_sha256': sha(offer_path), 'source_sha256': sha(src),
        'groups_by_edition': dict(Counter(r['edition'] for r in rows)),
        'primary_groups_once_in_written_order': len(ordered),
        'primary_types': 25, 'new_primary_exact_form_guesses': 20,
        'old_lexical_entries_unchanged': 65, 'old_alternate_entries_unchanged': 15,
        'additional_dchor_unchanged': True,
        'used_productions': sorted(used), 'listed_bindings': 8,
        'unassigned_forms': unknown,
        'limits': 'No semantic, physical, grammar-uniqueness, or independent image confirmation is certified; binding adequacy is reviewed manually.'
    }
    out = P / 'raw512_coverage_validation_20260922.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()
