#!/usr/bin/env python3
"""Independent exact-source/inventory audit. No semantic or material execution."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 'research_registry/proposals/'
TARGET = 'f37v|f37v.8-f37v.13'
READERS = ('ZL3b', 'IT2a')
AUTHOR_HASHES = {
    'CONTENT_STOP.md': 'ce201bc23c93761933e185c55af71cc078b66596da33a28b2fac1e4dcaab642b',
    'DECISION.md': '8c002361c2781d0796fce2e777f88994f8ad28527300b6693570b7e3f720e499',
    'GROUPS.json': 'e770ef4d05ae966f3d48b1ba2e2140f17cedd4891ba8abaacb19ef36a3ecd25b',
    'INHERITED_FREEZE.json': '5ada239c1c32319fea951f8014d5c790ca22c3446678364c650a381f43809265',
    'LEXICAL_INVENTORY.json': '70f14b7bba3091181a4a969fe40016627f0fde066d5c9a3db625fe0a67096476',
    'SOURCE.json': 'c957a6a6a77c79e45fc59f0991bd92d0f192b03e35840c7d980c38a4ba536385',
    'SOURCE_RECEIPT.json': 'fd92907bf917fdbb11a55736658cb21ca1b04fc553f8a2eb8235f0070de608d0',
    'STATE_LEDGER.json': '828d7873fe328199edd77be8f8d111aa2f9a84961a98616c1897a1ac3ce5f5d3',
}
PRIMARY_HASHES = {
    BASE+'raw_f37v_p2_stored_material_continuation_20260922.json': '8d2c5b79600e8b21c26bc122a5fd5519eb0525a9cfe321ba65948c616c50a164',
    BASE+'raw370_two_paragraph_powder_partition_offer_20260922.json': '4654afe0414d85f431371c799df6189b73b2cd4ace6adfc7eae833a51bf837da',
    BASE+'raw370_powder_partition_v2_material_contract_20260922.json': '7676250faf7adabc2fd240635a520852c65c2d7a2f8070fb82717351a8ab6d78',
    BASE+'raw370_f4r_complete_extension_attempt_20260922.json': '677776574fd892b7034d999f59e521054172eeef907f5020c1de704767cb0ba8',
    BASE+'raw512_f37v_powder_whole_working_offer_20260922.json': '1fb4ceeccf6f5fe85ee455760ba5e365e1f6627f00031e8c0efebbaf88ad5a3a',
    'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json': '667ca3ae0705a6bb3ccfcd09ea7ee04e28747e58d810e8fa9379f28c0f4fc89b',
    'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv': 'f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def require(test, message):
    if not test:
        raise ValueError(message)


def audit():
    for name, expected in AUTHOR_HASHES.items():
        require(digest((HERE/name).read_bytes()) == expected, 'Author bytes changed: '+name)
    for path, expected in PRIMARY_HASHES.items():
        require(digest((ROOT/path).read_bytes()) == expected, 'Primary bytes changed: '+path)
    original = load(ROOT/BASE/'raw370_two_paragraph_powder_partition_offer_20260922.json')
    v2 = load(ROOT/BASE/'raw370_powder_partition_v2_material_contract_20260922.json')
    p512 = load(ROOT/BASE/'raw512_f37v_powder_whole_working_offer_20260922.json')
    f4 = load(ROOT/BASE/'raw370_f4r_complete_extension_attempt_20260922.json')
    freeze = load(HERE/'INHERITED_FREEZE.json')
    source = load(HERE/'SOURCE.json')
    receipt = load(HERE/'SOURCE_RECEIPT.json')
    groups = load(HERE/'GROUPS.json')
    authored = load(HERE/'LEXICAL_INVENTORY.json')

    blocks = {
        'original_65': original['lexicon'],
        'alternate_15': original['alternative_reading_values'],
        'raw512_20': p512['new_exact_form_entries'],
        'f4r_13_including_dchor': f4['new_exact_form_values'],
    }
    require([len(x) for x in blocks.values()] == [65, 15, 20, 13], 'Primary inventory sizes')
    require(freeze['inherited_old_values'] == blocks['original_65'] == p512['frozen_parent']['all_65_lexical_entries'], '65 entries not exact')
    require(freeze['inherited_alternate_values'] == blocks['alternate_15'] == p512['frozen_parent']['all_15_alternate_entries'], '15 alternatives not exact')
    require(freeze['raw512_new_exact_form_entries'] == blocks['raw512_20'], '20 RAW512 entries not exact')
    require(freeze['retained_dchor'] == blocks['f4r_13_including_dchor']['dchor'] == p512['additional_known_family_constraint']['dchor'], 'dchor changed')
    require(freeze['inherited_effects'] == v2['global_effects'] == p512['frozen_parent']['global_effects'], 'V2 effects changed')
    dictionary = {}
    provenance = {}
    for block, entries in blocks.items():
        for word, entry in entries.items():
            require(word not in dictionary or dictionary[word] == entry, 'Conflicting retained entry: '+word)
            dictionary[word] = entry
            provenance.setdefault(word, []).append(block)
    require(len(dictionary) == 113, 'Unexpected inherited dictionary union')

    require(source['selection_id'] == receipt['selection_id'] == groups['selection_id'] == TARGET, 'Target selector changed')
    require(set(source['readers']) == set(READERS), 'Unexpected source reader')
    # Owned f84-free cache: only compare the already selected exact records.
    # No other paragraph's words, frequencies or eligibility are evaluated.
    packet = load(ROOT/source['source_path'])
    expected_groups = []
    result_readers = {}
    union_unknown = set()
    for reader in READERS:
        candidates = [x for x in packet[reader] if x['id'] == TARGET]
        require(len(candidates) == 1, 'Counterpart absent/duplicate: '+reader)
        record = source['readers'][reader]
        require(record == candidates[0], 'Whole cached record changed: '+reader)
        require(record['page'] == 'f37v' and record['leaf'] == 37, 'Page/leaf changed')
        require([x['locus'] for x in record['lines']] == ['f37v.'+str(i) for i in range(8, 14)], 'Whole locus order')
        require(record['lines'][0]['start'] and record['lines'][-1]['end'], 'Incomplete paragraph')
        canonical = json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
        require(digest(canonical) == receipt['reader_records'][reader]['record_sha256'], 'Receipt record hash')
        words = []
        metadata_lines = []
        for line in record['lines']:
            require(line['offset'] == len(words), 'Wrong offset')
            require(len(line['words']) == len(line['source_ids']), 'Word/ID length')
            metadata_lines.append({k: line[k] for k in ['locus', 'row', 'start', 'end', 'anchor_eligible', 'offset']} | {'group_count': len(line['words'])})
            for ordinal, (word, sid) in enumerate(zip(line['words'], line['source_ids']), 1):
                require(sid == f"{reader}|{line['locus']}|G{ordinal:03d}", 'Source-ID mismatch')
                expected_groups.append(dict(reader=reader, locus=line['locus'], row=line['row'], line_start=line['start'], line_end=line['end'], anchor_eligible=line['anchor_eligible'], line_offset=line['offset'], group_ordinal=line['offset']+ordinal, source_id=sid, word=word))
                words.append(word)
        require(len(words) == record['groups'] == {'ZL3b': 25, 'IT2a': 23}[reader], 'Group count mismatch')
        require(metadata_lines == freeze['source_metadata'][reader]['lines'], 'Metadata freeze mismatch')
        types = set(words)
        known, unknown = types & dictionary.keys(), types - dictionary.keys()
        categories = {name: sorted(types & entries.keys()) for name, entries in blocks.items()}
        require(sorted(known) == authored['known_inherited_or_retained'][reader], 'Authored known set mismatch')
        require(sorted(unknown) == authored['unassigned_exact_forms'][reader], 'Authored unknown set mismatch')
        require(len(unknown) == authored['unassigned_counts'][reader], 'Authored unknown count mismatch')
        require(len(types) == authored['reader_type_counts'][reader], 'Authored type count mismatch')
        union_unknown.update(unknown)
        result_readers[reader] = dict(groups=len(words), types=len(types), known_types=sorted(known), known_positions=sum(w in dictionary for w in words), unknown_types=sorted(unknown), unknown_count=len(unknown), unknown_positions=sum(w not in dictionary for w in words), inherited_hits=categories, anchor_eligible_lines=sum(x['anchor_eligible'] for x in record['lines']), cap_exceeded=len(unknown)>12)
    require(expected_groups == groups['groups'], 'Full GROUPS fields/order differ from source')
    require(groups['groups_total'] == len(expected_groups) == 48, 'Total group count')
    require(groups['by_reader'] == {r: result_readers[r]['groups'] for r in READERS}, 'GROUPS reader counts')
    require(sorted(union_unknown) == authored['union_unassigned_exact_forms'], 'Union unknown set mismatch')
    require(len(union_unknown) == authored['union_unassigned_count'] == 19, 'Union unknown count mismatch')
    for word, entry in authored['known_value_records']['old'].items():
        require(entry == blocks['original_65'][word], 'Authored old hit changed: '+word)
    for word, entry in authored['known_value_records']['retained_RAW512_new'].items():
        require(entry == blocks['raw512_20'][word], 'Authored RAW512 hit changed: '+word)
    require(freeze['caps']['new_exact_whole_values_max'] == authored['cap']['max_new_exact_whole_values'] == 12, 'Cap changed')
    require(freeze['caps']['new_reusable_productions_max'] == 3 and freeze['caps']['additional_nondefault_material_or_scope_bindings_max'] == 4, 'Other caps changed')
    return {
        'status': 'CAPACITY_STOP_COUNTS_VALIDATED_WITH_DOCUMENTATION_ERRORS',
        'validation_scope': 'Exact inventory/source audit, not a semantic replay or a pre-exposure certification.',
        'author_hashes': AUTHOR_HASHES, 'primary_hashes': PRIMARY_HASHES,
        'dictionary_sizes': {k: len(v) for k, v in blocks.items()},
        'dictionary_union': len(dictionary), 'readers': result_readers,
        'union_unknown_forms': sorted(union_unknown), 'union_unknown_count': len(union_unknown),
        'cap': 12, 'both_readers_exceed_cap': all(x['cap_exceeded'] for x in result_readers.values()),
        'source_groups_exact': 48,
        'f4r_extra_exact_target_overlaps': sorted({word for row in result_readers.values() for word in row['inherited_hits']['f4r_13_including_dchor']}),
        'documentation_errors': [
            'CONTENT_STOP says six old ZL plus dor; actual ZL is five base entries plus dor = six retained types.',
            'INHERITED_FREEZE.created_utc 17:20:00 is not independently established; see observed local file chronology in ROOT_REVIEW.',
            'DECISION calls the allowlist-file digest a page hash; it is the SHA256 of PAGE_ALLOWLIST.tsv.'
        ],
        'execution_limits': ['No new values', 'No semantic or numeric execution', 'No countermodel selected', 'No public preregistration timing certified'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Write deterministic inventory validation only')
    args = parser.parse_args()
    if not args.execute:
        parser.error('--execute is required for this nonsemantic inventory audit')
    result = audit()
    (HERE/'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['status', 'dictionary_union', 'source_groups_exact', 'union_unknown_count', 'both_readers_exceed_cap']}, sort_keys=True))


if __name__ == '__main__':
    main()
