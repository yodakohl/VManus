#!/usr/bin/env python3
"""Replay the preregistered Egerton source-owner rule from recorded observations."""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def read_tsv(name):
    with (BASE / 'src' / name).open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def result():
    deck = read_tsv('SOURCE_DECK.tsv')
    shortlist = read_tsv('NATIVE_SHORTLIST.tsv')
    if len(deck) != 309 or [int(row['index']) for row in deck] != list(range(309)):
        raise ValueError('official 309-canvas deck is incomplete or disordered')
    if len({row['canvas_id'] for row in deck}) != 309:
        raise ValueError('duplicate canvas')
    for row in deck:
        if not row['thumbnail_url'].startswith('https://bl.digirati.io/images/'):
            raise ValueError('unofficial thumbnail')
        if not row['native_url'].startswith('https://bl.digirati.io/images/'):
            raise ValueError('unofficial native image')
        if int(row['bytes']) < 1000 or len(row['sha256']) != 64:
            raise ValueError('missing source receipt')
    identifiers = [int(row['index']) for row in shortlist]
    if identifiers != [37, 52, 112, 128, 137, 175, 184, 193]:
        raise ValueError('shortlist differs from reported visual audit')
    yes = {'YES', 'NO', 'UNCLEAR'}
    matches = []
    for row in shortlist:
        if row['label'] != deck[int(row['index'])]['label']:
            raise ValueError('shortlist label mismatch')
        if any(row[column] not in yes for column in ('blade', 'orange_fan', 'creature', 'entry_ownership')):
            raise ValueError('invalid visual code')
        if all(row[column] == 'YES' for column in ('blade', 'orange_fan', 'creature', 'entry_ownership')):
            matches.append(int(row['index']))
    return {
        'experiment_id': 'GDT1093',
        'decision': 'STRICT_NAMED_SOURCE_OWNER' if matches else 'NO_THREE_PART_NAMED_SOURCE_OWNER',
        'deck_canvases': len(deck),
        'native_shortlist': len(shortlist),
        'strict_match_indices': matches,
        'feature_yes_counts_on_shortlist': {key: sum(row[key] == 'YES' for row in shortlist) for key in ('blade', 'orange_fan', 'creature')},
        'post_result_partial_resemblance': {'index': 175, 'label': 'f.84v', 'source_heading': 'Rabarbarum', 'status': 'C0_ONLY_NOT_FIXED_MATCH'},
        'claim_ceiling': 'exploratory source-owner capacity; no Voynich word, plant identity, direct-copy, or medical meaning'
    }


def main():
    output = result()
    target = BASE / 'artifacts' / 'RESULT.json'
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(output, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
