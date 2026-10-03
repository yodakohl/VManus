#!/usr/bin/env python3
"""Render the complete fixed result; no annotation, adjudication or selection."""
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
CATS = ['WATER', 'AIR', 'BASIN_ART', 'PIPE_ART', 'BASIN_NAT', 'PIPE_NAT']


def main():
    result = json.loads((EXP / 'artifacts/RESULT.json').read_text())
    validation = json.loads((EXP / 'artifacts/VALIDATION.json').read_text())
    assert validation['status'] == 'PASS'
    assert result['coverage'] == {'A': 579, 'B': 579}
    lines = [
        '# GDT1162: complete nominal-candidate and source-prediction table',
        '',
        'These are newly global-obligatory hypothetical extensions, not established',
        'meanings. Source-window counts are not Voynich frequency ceilings or',
        'translation likelihoods. The original local GDT827 accounts stay unchanged.',
        '',
        '|Candidate|qokain commitment|qokaiin commitment|Priority requirement|',
        '|---|---|---|---|',
        '|T|Ordinary WATER|Physical AIR|Robustly dominate both F alternatives under METHOD|',
        '|F_ART|Manufactured BASIN/open receiving pool|Manufactured PIPE/conduit|Both F alternatives must robustly dominate T|',
        '|F_BROAD|Manufactured basin or natural reservoir/chamber|Manufactured or natural conduit|Same F requirement; broader functional meanings are explicit additional assumptions|',
        '',
        'Every original occurrence would have to carry its assigned concept if the',
        'global extension were adopted. This source-only comparison tests none of',
        'those manuscript occurrences and supplies no independent meaning check.',
        '',
        'Each cell is lower–upper presence over all fixed windows. Joint means',
        'same-window proximity, not participation in the same event. Larger scales',
        'are recomputed within each observer before comparison.',
        '',
        '|Work|Words/window|Windows|T: water; air; joint|F_ART: basin; pipe; joint|F_BROAD: reservoir; conduit; joint|',
        '|---|---:|---:|---|---|---|',
    ]
    for cell in result['cells']:
        values = []
        for pair in ['T', 'F_ART', 'F_BROAD']:
            values.append('; '.join(f"{a}–{b}" for a, b in zip(cell[pair]['lower'], cell[pair]['upper'])))
        lines.append(f"|{cell['work']}|{cell['scale']}|{cell['windows']}|" + '|'.join(values) + '|')
    lines += ['', '## All dominance conditions', '',
              '|Comparison|All non-strict inequalities|Strict first/second marginal|Positive-joint works at100/200/400|Decision|',
              '|---|---|---|---|---|']
    for name, d in validation['dominance_details'].items():
        lines.append(f"|{name}|{d['all_cells']}|{d['strict_marginals']}|{list(d['positive_joint_works'].values())}|{d['passes']}|")
    lines += ['', '## Every failed inequality', '',
              'A failure here defeats this particular source-priority condition; it',
              'does not contradict a manuscript occurrence or refute a local noun.',
              '', '|Comparison|Work|Scale|Failed aligned dimensions|', '|---|---|---:|---|']
    for name, d in validation['dominance_details'].items():
        for cell in d['cells']:
            failed = [key for key, passed in cell['passes'].items() if not passed]
            if failed:
                lines.append(f"|{name}|{cell['work']}|{cell['scale']}|{', '.join(failed)}|")
    lines += ['', f"Registered decision: **{result['status']}**.", '',
              'Remaining ambiguity: observer uncertainty, source-domain selection,',
              'genre mediation, the paid natural-object extension, and all original',
              'eight-group syntax/repetition/ownership debts. Independent manuscript',
              'confirmation capacity added by this experiment: **zero**.', '']
    (EXP / 'CANDIDATE_TABLE.md').write_text('\n'.join(lines))

    observers = {'A': {}, 'B': {}}
    for file in sorted((EXP / 'artifacts').glob('ANNOTATIONS_*.json')):
        packet = json.loads(file.read_text())
        for row in packet['rows']:
            assert row['id'] not in observers[packet['observer']]
            observers[packet['observer']][row['id']] = row['values']
    lines = ['# Complete base-window observer comparison', '',
             'E=expressed; U=uncertain; N=not expressed after reading. Each cell is',
             'A/B. Original short quotations, reasons and antecedents remain in the',
             'six frozen annotation packets; no disagreements are adjudicated here.', '',
             '|Window|' + '|'.join(CATS) + '|', '|---|' + '|'.join(['---'] * 6) + '|']
    windows = json.loads((EXP / 'artifacts/WINDOWS.json').read_text())['windows']
    for window in windows:
        key = window['id']
        lines.append('|' + key + '|' + '|'.join(observers['A'][key][c] + '/' + observers['B'][key][c] for c in CATS) + '|')
    (EXP / 'OBSERVER_TABLE.md').write_text('\n'.join(lines) + '\n')
    print('Rendered all12cells, all failed inequalities and all579 observer rows.')


if __name__ == '__main__':
    main()
