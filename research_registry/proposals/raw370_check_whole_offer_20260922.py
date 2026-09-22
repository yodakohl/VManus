#!/usr/bin/env python3
"""Reproduce positional completeness only, not the semantic review."""
from pathlib import Path
from collections import Counter
import hashlib, json

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'research_registry/proposals'
offer_path = BASE / 'raw370_two_paragraph_powder_partition_offer_20260922.json'
assert hashlib.sha256(offer_path.read_bytes()).hexdigest() == '4654afe0414d85f431371c799df6189b73b2cd4ace6adfc7eae833a51bf837da'
offer = json.loads(offer_path.read_text())
source_path = ROOT / offer['source_packet']
assert hashlib.sha256(source_path.read_bytes()).hexdigest() == offer['source_packet_sha256']
source = json.loads(source_path.read_text())
raw = {}
for para in source['paragraph_readings']:
    assert para['page'] in ('f21r','f32v')
    for line in para['lines']:
        for group in line['groups']:
            sid = group['source_group_id']
            assert sid not in raw
            raw[sid] = group
seen = set(); counts = {}; entries = {**offer['lexicon'], **offer['alternative_reading_values']}
def value(word):
    entry = entries[word]
    if 'same_hypothesized_value_as' in entry:
        return value(entry['same_hypothesized_value_as'])
    return entry['value']
for para in offer['complete_positional_alignment']:
    counter = counts.setdefault(para['edition'], Counter())
    for line in para['lines']:
        for group in line['groups']:
            sid = group['source_group_id']; assert sid not in seen; seen.add(sid)
            assert all(group[key] == val for key,val in raw[sid].items())
            word = group['ivtff_group_raw']; counter[word] += 1
            assert group['hypothesized_value'] == value(word)
assert seen == set(raw)
out = {}
for reader,counter in counts.items():
    declared = offer['bounded_annotation_costs'][reader]
    assert dict(counter) == declared['counts']
    actual = [sum(counter.values()),len(counter),sum(n==1 for n in counter.values())]
    assert actual == [declared['raw_groups'],declared['distinct_raw_forms'],declared['single_occurrence_forms']]
    out[reader] = dict(zip(['groups','types','singletons'],actual))
assert set(counts['ZL3b']) == set(offer['lexicon'])
assert len(offer['schematic_productions']['rules']) == 18
print(json.dumps({'status':'PASS','aligned_positions':len(seen),'readers':out,
                  'semantic_validation':False,'confirmed_words':0},ensure_ascii=False))
