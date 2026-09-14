#!/usr/bin/env python3
"""Evaluate a frozen native-observer packet; does not infer visual truth."""
import csv
import hashlib
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]


def read(path):
    return json.loads(path.read_text())


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def check_locks():
    for name, base in [('PREREG_LOCK.json', ROOT), ('OBSERVATION_LOCK.json', EXP)]:
        for rel, expected in read(EXP / name)['files'].items():
            assert hashlib.sha256((base / rel).read_bytes()).hexdigest() == expected, rel


def main():
    check_locks()
    obs = read(EXP / 'artifacts/OBSERVATIONS.json')
    fields = {x['id']: x['status'] for x in obs['fields']}
    localized = fields['localization'] == 'PRESENT'
    bound = all(fields[x] == 'PRESENT' for x in ('member_delimitation', 'list_value_binding'))
    decision = ('VISUAL_LOCALIZATION_UNRESOLVED' if not localized else
                'VISUAL_BINDING_CANDIDATE' if bound else 'NO_VISUAL_LIST_TOTAL_BINDING')
    expected = read(EXP / 'src/EXPECTED.json')
    lines = ['# Complete fixed paragraph: existing readings, not a new transcription', '']
    flat = []
    for edition, groups in expected.items():
        lines += [f'## {edition}', '']
        for locus in dict.fromkeys(x['locus'] for x in groups):
            seq = [x for x in groups if x['locus'] == locus]
            lines += [f"{locus}: " + ' '.join(x['ivtff_group_raw'] for x in seq), '']
        flat.extend(groups)
    lines += ['Display spaces separate recorded groups; original separator flags are in EXPECTED.json and EXPECTED_GROUPS.tsv.', '']
    (EXP / 'artifacts/FULL_PARAGRAPH.md').write_text('\n'.join(lines))
    with (EXP / 'artifacts/EXPECTED_GROUPS.tsv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(flat[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(flat)
    cases = [
        dict(candidate='LIST_TOTAL', prediction='The registered visible-binding route requires list-specific member delimitation AND a separate list-to-value device.',
             observation=f"member_delimitation={fields['member_delimitation']};list_value_binding={fields['list_value_binding']}",
             consequence=decision,
             contradiction='Required visible evidence is absent in the observer record; this does not refute an implicit grammatical list.',
             remaining_ambiguity='aiiin as total versus dose versus grade or a single compound remains unresolved.'),
        dict(candidate='DOSE_PER_ITEM', prediction='No unique visible-layout prediction was preregistered for this semantic alternative.',
             observation='Same complete four-line packet and same physical gaps.', consequence='NOT_DISCRIMINATED',
             contradiction='No dose-specific semantic consequence was tested.',
             remaining_ambiguity='No item ownership, dose unit or reading established.'),
        dict(candidate='DEGREE_OR_SINGLE_COMPOUND', prediction='No unique visible-layout prediction was preregistered for this semantic alternative.',
             observation='Same complete four-line packet; IT olr and ZL/RF o l r retained.', consequence='NOT_DISCRIMINATED',
             contradiction='Ink gaps alone do not contradict a compound or grade expression.',
             remaining_ambiguity='No word boundary, grade scale or meaning established.')
    ]
    for c in cases:
        c['independent_confirmation_capacity_this_test'] = 0
        c['selected_meaning'] = False
    with (EXP / 'artifacts/CANDIDATE_DECISIONS.tsv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(cases[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(cases)
    write(EXP / 'artifacts/RESULT.json', dict(
        experiment='GDT942', decision=decision, fields=fields,
        coverage={k: len(v) for k, v in expected.items()}, total_recorded_groups=len(flat),
        all_four_lines_retained=True, candidates=cases, independence=obs['independence'],
        numeric_test_performed=False, significance_claim=False, confirmed_translated_words=0,
        scope='One exposed paragraph on one physical leaf; native observation is not independently replicated.',
        interpretation='Stop this local count-only proof route. No choice among implicit list, dose and grade/compound semantics.'
    ))
    print(decision)


if __name__ == '__main__':
    main()
