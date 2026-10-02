#!/usr/bin/env python3
"""Replay a frozen manual lexical account; this is not a decoder or parser."""
from pathlib import Path
import collections
import csv
import hashlib
import json

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source = json.loads((HERE / 'src/SOURCE.json').read_text())
    for item in source['inputs']:
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    receipt = json.loads((HERE / 'artifacts/AUTHOR_RECEIPT.json').read_text())
    for path, digest in receipt['files'].items():
        assert sha(HERE / path) == digest, path
    core = json.loads((HERE / 'CORE.json').read_text())
    account = json.loads((HERE / 'artifacts/AUTHOR_ACCOUNT.json').read_text())
    target_path = ROOT / 'experiments/yolo/gdt1094_f25v_source_package_whole_reading/src/TARGET_RAW.tsv'
    with target_path.open() as stream:
        source_rows = list(csv.DictReader(stream, delimiter='\t'))
    expected = [(r['edition'], r['locus'], int(r['source_group_index']), r['ivtff_group_raw'], r['left_separator'], r['right_separator']) for r in source_rows]
    rows = account['rows']
    actual = [(r['edition'], r['locus'], r['index'], r['raw'], r['left_separator'], r['right_separator']) for r in rows]
    assert actual == expected, 'Exact native occurrence sequence mismatch'
    assert len(set(actual)) == len(actual), 'Duplicate occurrence identity'
    assert not set(core['lexicon']).intersection(account['extension_values'])
    for row in rows:
        if row['status'] == 'CORE_C0':
            assert row['value'] == core['lexicon'][row['raw']]['value']
        elif row['status'] == 'EXTENSION_C0':
            assert row['value'] == account['extension_values'][row['raw']]['value']
        else:
            assert row['status'] == 'UNKNOWN_OR_UNSEGMENTED' and row['value'] is None
    per_reader = {}
    for reader in ['IT2a', 'ZL3b', 'RF1b']:
        selected = [r for r in rows if r['edition'] == reader]
        counts = collections.Counter(r['status'] for r in selected)
        per_reader[reader] = {'groups': len(selected), 'core_C0': counts['CORE_C0'], 'extension_C0': counts['EXTENSION_C0'], 'unknown': counts['UNKNOWN_OR_UNSEGMENTED'], 'daiin': sum(r['raw'] == 'daiin' for r in selected)}
    result = {
        'status': 'PARTIAL_LEXICAL_ACCOUNT_NO_COMPLETE_READING',
        'basis': 'Frozen author explicitly reports underived patient, reference and naming-reason bindings; replay checks lexical accounting only.',
        'native_groups': len(rows), 'per_reader': per_reader,
        'lexicon': {'core_whole_guesses': len(core['lexicon']), 'extension_whole_guesses': len(account['extension_values'])},
        'provisionally_glossed_occurrences': sum(r['value'] is not None for r in rows),
        'unknown_occurrences': sum(r['value'] is None for r in rows),
        'executable_sentence_derivation': False,
        'unresolved_obligations': ['eye/hair recipient and ownership', 'growth locative attachment', 'hare-condition and plant-benefit argument linkage', 'actual naming-reason consumption', 'final leaf/plant phrase'],
        'protocol_scope_ambiguity': 'See unchanged METHOD and subsequent PROTOCOL_NOTE.md; hypothetical names do not identify pictured species.',
        'confirmed_words': 0, 'independent_meaning_confirmation_capacity': 0,
        'no_new_target_access': True,
        'claim_ceiling': 'Stored C0 glosses and their consistency, not translation or compositional derivation.'
    }
    (HERE / 'artifacts/RESULT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[(row['edition'], row['locus'])].append(row)
    with (HERE / 'artifacts/LITERAL_GLOSS_LINES.tsv').open('w') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['edition', 'locus', 'raw_groups', 'literal_C0_values_not_translation', 'unknown_groups'])
        for (edition, locus), group in grouped.items():
            writer.writerow([edition, locus, ' '.join(r['raw'] for r in group), ' | '.join(r['value'] if r['value'] is not None else 'UNKNOWN[' + r['raw'] + ']' for r in group), sum(r['value'] is None for r in group)])
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
