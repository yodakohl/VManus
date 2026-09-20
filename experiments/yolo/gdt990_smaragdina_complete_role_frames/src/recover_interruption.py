#!/usr/bin/env python3
"""Recover deterministic necessary certificates only; never import/call a solver."""
import collections
import csv
import gzip
import hashlib
import json
from pathlib import Path
import model
import validate

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'


def write(name, value):
    data = (json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n').encode()
    (A / name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)


def main():
    for name, digest in json.loads((E / 'PREREG_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    source, streams = validate.source_check()
    panel = json.loads((ROOT / source['input_paragraphs']).read_text())
    cases = []
    eligible_paragraphs = collections.Counter()
    for edition, paragraphs in panel.items():
        for p in paragraphs:
            assert not p['page'].startswith('f84') and p['page'] != 'f116v'
            words = [w for line in p['lines'] for w in line['words']]
            assert len(words) == p['groups']
            eligible = all(line['anchor_eligible'] for line in p['lines'])
            eligible_paragraphs[edition] += eligible
            for variant, spec in source['variants'].items():
                if eligible:
                    pre = model.necessary(spec['streams'][source['writers'][0]], words)
                    independent_status, basic = validate.necessity(streams[(variant, source['writers'][0])], words)
                    assert pre['status'] == independent_status
                    assert all(pre[k] == v for k, v in basic.items())
                for writer in source['writers']:
                    row = dict(case=len(cases) + 1, edition=edition, paragraph=p['id'], page=p['page'],
                               leaf=p['leaf'], variant=variant, writer=writer, source_forms=spec['forms'],
                               source_root_types=spec['root_types'], target_groups=len(words),
                               independent_meaning_confirmation_capacity=0)
                    if not eligible:
                        row.update(status='UNKNOWN_SOURCE', ineligible_lines=[x['locus'] for x in p['lines'] if not x['anchor_eligible']])
                    elif pre['status'] == 'REQUIRES_FULL_EQUATION':
                        row.update(status='UNKNOWN_UNRETAINED_SOLVER_RESULT', necessary=dict(basic, status=pre['status']))
                    else:
                        assert pre == dict(basic, status=pre['status'])
                        row.update(status=pre['status'], necessary=pre)
                    cases.append(row)
    counts = dict(collections.Counter(c['status'] for c in cases))
    observed = dict(UNKNOWN_SOURCE=19080, CONTRADICTED_NONEMPTY_LENGTH=7524,
                    CONTRADICTED_INJECTIVE_LENGTH=3696, CONTRADICTED_WORD_BOUNDARIES=96,
                    UNKNOWN_UNRETAINED_SOLVER_RESULT=1980)
    assert counts == observed
    assert len(cases) == 32376
    assert len({(c['edition'], c['paragraph'], c['variant'], c['writer']) for c in cases}) == len(cases)
    result = dict(experiment='GDT990', decision='INTERRUPTED_FULL_EQUATION_RESULTS_UNRETAINED',
                  cases=len(cases), status_counts=counts,
                  paragraph_counts={e: len(ps) for e, ps in panel.items()},
                  eligible_paragraph_counts=dict(eligible_paragraphs),
                  necessary_contradiction_cases=sum(n for s, n in counts.items() if s.startswith('CONTRADICTED_')),
                  full_equation_cases_unresolved=1980,
                  original_console_last_reported_completions=96,
                  original_completed_case_identities_known=False,
                  original_total_completed_before_termination_known=False,
                  original_full_witness_count_known=False,
                  retained_full_witnesses=0, recovery_solver_calls=0,
                  independent_meaning_confirmation_capacity=0, confirmed_translated_words=0,
                  significance_claim=False, unique_inverse_decoding_claim=False,
                  termination_cause='UNKNOWN', exit_code=143)
    result['breakdown'] = {e: {v: {w: dict(collections.Counter(c['status'] for c in cases
                                if (c['edition'], c['variant'], c['writer']) == (e, v, w)))
                                for w in source['writers']} for v in source['variants']} for e in panel}
    write('INTERRUPTED_CASES.json.gz', cases)
    columns = ['case', 'edition', 'paragraph', 'leaf', 'variant', 'writer', 'source_forms',
               'source_root_types', 'target_groups', 'status', 'independent_meaning_confirmation_capacity']
    with (A / 'INTERRUPTED_CANDIDATES.tsv').open('w', newline='') as f:
        table = csv.DictWriter(f, columns, delimiter='\t', lineterminator='\n', extrasaction='ignore')
        table.writeheader()
        table.writerows(cases)
    saved = json.loads(gzip.decompress((A / 'INTERRUPTED_CASES.json.gz').read_bytes()))
    assert saved == cases
    with (A / 'INTERRUPTED_CANDIDATES.tsv').open() as f:
        tab = list(csv.DictReader(f, delimiter='\t'))
    assert len(tab) == len(cases)
    assert all(all(r[k] == str(c[k]) for k in r) for r, c in zip(tab, cases))
    write('INTERRUPTION_RESULT.json', result)
    write('INTERRUPTION_VALIDATION.json', dict(status='PASS', scope='deterministic reconstruction only',
          cases=len(cases), source_checks=len(validate.CHECKS), independent_necessary_implementations=2,
          unchanged_preregistration_hashes=True, complete_table_roundtrip=True,
          original_full_run_validated=False, recovery_solver_calls=0,
          validator_independence='Separate necessary-condition implementations; same root author.'))
    print(json.dumps({k: v for k, v in result.items() if k != 'breakdown'}, indent=2))


if __name__ == '__main__':
    main()
