"""Complete owned-text lexical account, not a decoder or semantic parser."""
import csv
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = next(p for p in BASE.parents if (p / 'vmanus-work').exists())
INPUTS = {
    'parent': 'experiments/yolo/gdt1023_amulet_complete_typed_assembly/src/SOURCE.json',
    'extension': 'research_registry/proposals/raw_f108r_amulet_frozen71_complete_commentary_20260921.json',
    'whole_units': 'experiments/yolo/gdt999_typed_pair_frame_transfer/artifacts/MATCHING_PARAGRAPHS.json',
    'packing': 'experiments/yolo/gdt1038_amulet_atomic_binary_packing/src/SPEC.json',
}


def read(path):
    return json.loads((ROOT / path).read_text())


def main():
    parent, extension = read(INPUTS['parent']), read(INPUTS['extension'])
    lexicon = dict(parent['lexicon'])
    assert not set(lexicon) & set(extension['new_17_lexical_entries'])
    lexicon.update(extension['new_17_lexical_entries'])
    assert len(lexicon) == 88
    units = read(INPUTS['whole_units'])
    assert [(u['edition'], u['paragraph']['groups']) for u in units] == [('ZL3b', 57), ('IT2a', 55)]
    assert all(u['paragraph']['page'] == 'f106r' for u in units)
    rows = []
    for u in units:
        for line in u['paragraph']['lines']:
            for n, (word, sid) in enumerate(zip(line['words'], line['source_ids'])):
                alternatives = [[word]] if word in lexicon else []
                alternatives += [[word[:i], word[i:]] for i in range(1, len(word))
                                 if word[:i] in lexicon and word[i:] in lexicon]
                rows.append({
                    'edition': u['edition'], 'locus': line['locus'],
                    'index': n + 1, 'source_id': sid, 'raw': word,
                    'anchor_eligible': line['anchor_eligible'],
                    'alternatives': alternatives,
                    'tags': [[lexicon[w]['tag'] for w in a] for a in alternatives],
                    'meanings': [[lexicon[w]['meaning'] for w in a] for a in alternatives],
                    'status': 'UNBOUND' if not alternatives else 'OLD_VALUES_ONLY',
                })
    out = {
        'kind': 'post_exposure_lexical_account_not_semantic_test',
        'complete_units': units, 'unchanged_88_entries': lexicon,
        'rows': rows,
        'counts': {ed: {
            'groups': sum(r['edition'] == ed for r in rows),
            'atomic_positions': sum(r['edition'] == ed and r['raw'] in lexicon for r in rows),
            'any_old_analysis_positions': sum(r['edition'] == ed and bool(r['alternatives']) for r in rows),
            'unbound_positions': sum(r['edition'] == ed and not r['alternatives'] for r in rows),
            'unbound_types': len({r['raw'] for r in rows if r['edition'] == ed and not r['alternatives']}),
        } for ed in ('ZL3b', 'IT2a')},
        'inspected_role_occurrences': [r for r in rows if r['raw'] in ('otedy', 'qokeedy', 'qokain', 'qokaiin')],
        'input_hashes': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                         for path in INPUTS.values()},
        'limits': 'All groups retained; detailed separator classes absent from inherited packet. Aggregate source flags preserved. No unknown has acquired a meaning, no clause grammar is inferred, no world is simulated.',
    }
    (BASE / 'F106_AMULET_ACCOUNT.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    with (BASE / 'F106_AMULET_ALL_POSITIONS.tsv').open('w', newline='') as f:
        fields = ['edition', 'locus', 'index', 'source_id', 'raw', 'anchor_eligible', 'status', 'alternatives', 'tags', 'meanings']
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for r in rows:
            writer.writerow({k: json.dumps(r[k], ensure_ascii=False) if k in ('alternatives', 'tags', 'meanings') else r[k] for k in fields})
    print(json.dumps(out['counts'], ensure_ascii=False))


if __name__ == '__main__':
    main()
