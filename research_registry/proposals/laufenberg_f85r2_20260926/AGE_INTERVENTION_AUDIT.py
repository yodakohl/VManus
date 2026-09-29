#!/usr/bin/env python3
"""Replay an exposed-data authorship sheet; no semantic score or new experiment."""
import collections
import csv
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
src = ROOT / 'experiments/yolo/gdt1042_f85r2_source_program_surface_census/artifacts/native_groups.tsv'
receipt = json.loads((D / 'AGE_INTERVENTION_CONTEXTS.json').read_text())
assert hashlib.sha256(src.read_bytes()).hexdigest() == receipt['source_sha256']
context = D / 'AGE_INTERVENTION_CONTEXTS.tsv'
assert hashlib.sha256(context.read_bytes()).hexdigest() == receipt['projection_sha256']
rows = list(csv.DictReader(context.open(), delimiter='\t'))
assert len(rows) == 473 and all(r['locus'] in receipt['allow'] for r in rows)
draft = D / 'AGE_INTERVENTION_AUTHORED_CORE.json'
roles = json.loads(draft.read_text())['hypothetical_whole_values']
blocks = collections.defaultdict(list)
for row in rows:
    blocks[(row['edition'], row['block'])].append(row)
events = []
annotated = []
for (edition, block), group in blocks.items():
    left = 0
    for pos, row in enumerate(group):
        role = roles.get(row['ivtff_group_raw'])
        annotated.append(dict(row, block_position=pos+1,
                              hypothetical_role=role or 'UNRESOLVED', complete_group_interpreted=False))
        if role != 'PROHIBITION_CLOSER':
            continue
        prefix = group[left:pos]
        found = {roles[x['ivtff_group_raw']] for x in prefix if x['ivtff_group_raw'] in roles}
        interventions = sorted(found & {'BLOODLETTING', 'PURGING'})
        events.append(dict(edition=edition, block=block, closer_id=row['source_group_id'],
                           closer_position=pos+1, prefix_groups=len(prefix), interventions=interventions,
                           great_need_in_prefix='GREAT_NEED' in found,
                           intervention_ids=[x['source_group_id'] for x in prefix
                                             if roles.get(x['ivtff_group_raw']) in interventions],
                           guard_ids=[x['source_group_id'] for x in prefix
                                      if roles.get(x['ivtff_group_raw']) == 'GREAT_NEED']))
        left = pos+1
output = dict(status='EXPLORATORY_CORE_PROJECTION_ONLY', events=events,
              all473positions_preserved=len(annotated) == 473,
              source_sha256=hashlib.sha256(context.read_bytes()).hexdigest(),
              draft_sha256=hashlib.sha256(draft.read_bytes()).hexdigest(), rows=annotated)
saved = json.loads((D / 'AGE_INTERVENTION_CORE_PROJECTION.json').read_text())
assert output == saved, 'Presentation differs from exact declared core projection'
# Check the displayed positional consequences directly from source IDs, without
# deriving meanings or repairing alternate reader forms.
expected = {('ZL3b','S'):['BLOODLETTING','PURGING'], ('ZL3b','W'):['BLOODLETTING'],
            ('IT2a','S'):['BLOODLETTING','PURGING'], ('IT2a','W'):['BLOODLETTING'],
            ('RF1b','S'):['BLOODLETTING'], ('RF1b','W'):['BLOODLETTING']}
assert {(x['edition'],x['block']):x['interventions'] for x in events} == expected
assert all(x['great_need_in_prefix'] for x in events)
validation = dict(status='PASS_INVENTORY_AND_DRAFT_REPLAY_ONLY', rows=len(rows),
                  exact_closer_contexts=len(events), confirmed_words=0,
                  semantic_validation=False, independent_confirmation=False,
                  source_choice_and_draft_post_exposure=True)
(D / 'AGE_INTERVENTION_VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n')
print(json.dumps(validation))
