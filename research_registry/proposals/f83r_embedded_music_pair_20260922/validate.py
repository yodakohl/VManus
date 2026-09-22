#!/usr/bin/env python3
"""Independent coverage/count check of the fixed proposal projection."""
import csv
import hashlib
import json
from pathlib import Path

p = Path(__file__).resolve().parent
root = p.parents[2]
receipt = json.loads((p / 'EXTRACTION_RECEIPT.json').read_text())
source = json.loads((p / 'SOURCE.json').read_text())
capacity = json.loads((p / 'CAPACITY.json').read_text())
old = json.loads((root / 'experiments/yolo/gdt1026_rota_crossleaf_frozen_meanings/src/SOURCE.json').read_text())
lex = dict(old['frozen_family']['all71_entries_unchanged'])
lex.update(old['new20_lexicon'])
assert lex == json.loads((p / 'FROZEN_LEXICON.json').read_text()) and len(lex) == 91
for name, digest in receipt['source_bindings'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name
rows = []
for reader, lines in source.items():
    assert [line['metadata']['locus'] for line in lines] == receipt['selected_loci']
    assert len(lines) == 7
    words = []
    ids = []
    for line in lines:
        locus = line['metadata']['locus']
        assert line['metadata']['page'] == 'f83r'
        assert len(line['groups']) == int(line['metadata']['source_group_count'])
        for group in line['groups']:
            word = group['ivtff_group_raw']
            words.append(word)
            ids.append(group['source_group_id'])
            rows.append([reader, locus, group['source_group_id'], group['source_group_index'], word,
                         lex[word]['tag'] if word in lex else 'UNKNOWN',
                         lex[word]['meaning'] if word in lex else 'UNASSIGNED'])
    assert len(set(ids)) == len(ids)
    unknown = sorted(set(words) - lex.keys())
    c = capacity[reader]
    assert c['groups'] == len(words) == (28 if reader == 'RF1b' else 27)
    assert c['types'] == len(set(words))
    assert c['known_positions'] == sum(word in lex for word in words) == 14
    assert c['known_types'] == len(set(words) & lex.keys())
    assert c['unknown_occurrences'] == {word: words.count(word) for word in unknown}
    assert c['new_whole_types_required'] == len(unknown) == (14 if reader == 'RF1b' else 13)
    assert c['fits_eight_new_values'] is False
    # Compare selected rows to the bound original, not just to our projection.
    originals = {}
    for path in receipt['source_bindings']:
        if not path.endswith('_' + reader + '.json'):
            continue
        data = json.loads((root / path).read_text())
        for line in data['lines']:
            meta = line['metadata']
            if meta['page'] == 'f83r' and meta['locus'] in receipt['selected_loci']:
                originals[meta['locus']] = {'metadata': meta, 'groups': [dict(zip(data['group_columns'], g)) for g in line['groups']]}
    assert lines == [originals[locus] for locus in receipt['selected_loci']]
with (p / 'COMPLETE_GROUP_VALUES.tsv').open('w', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
    writer.writerow(['reader', 'locus', 'source_group_id', 'index', 'raw', 'fixed_tag', 'fixed_meaning'])
    writer.writerows(rows)
result = {'status': 'PASS', 'checked_groups': len(rows), 'independent_algorithm': True,
          'independent_reviewer': False, 'semantic_execution': False,
          'decision': 'CLOSED_CAPACITY_LIMIT_OF_FIXED_OFFER', 'confirmed_words': 0}
(p / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
