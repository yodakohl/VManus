"""Exposed consequence collection; no semantic scorer or decoder.
Run from repository root. Reader lines are alternatives, not independent tests.
"""
import csv
import hashlib
import json
from pathlib import Path
from tools import word_profiles

D = Path(__file__).resolve().parent
AUTHOR = D / 'EP_CONTINUATION_AUTHOR.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    author = json.loads(AUTHOR.read_text())
    conn = word_profiles.ensure_cache()
    cases = []
    for form in ('qolkain', 'lom'):
        for target in word_profiles.occurrences(conn, form):
            line = [dict(r) for r in conn.execute(
                'SELECT * FROM groups WHERE edition=? AND page=? AND locus=? ORDER BY source_group_index',
                (target['edition'], target['page'], target['locus']))]
            assert not target['page'].startswith('f84')
            assert len(line) == line[0]['source_group_count']
            applications = []
            for account in author['accounts']:
                annotations = []
                for row in line:
                    raw = row['ivtff_group_raw']
                    new = account['new_exact_whole_values'].get(raw)
                    annotations.append({'source_id': row['source_group_id'], 'raw': raw,
                        'G': account['parent_G'].get(raw, new),
                        'I': account['parent_I'].get(raw, new)})
                applications.append({'candidate': account['id'], 'annotations': annotations,
                    'assessment': 'MANUAL_REVIEW_REQUIRED_NOT_SEMANTIC_PASS'})
            cases.append({'form': form, 'target': target, 'whole_line': line, 'applications': applications})
    result = {'phase': 'EXPOSED_EXPLORATORY_CONSEQUENCE_COLLECTION',
        'author_sha256': sha(AUTHOR), 'code_sha256': sha(Path(__file__)),
        'source_receipt': word_profiles.receipt(conn), 'cases': cases,
        'counts': {form: {edition: sum(c['form'] == form and c['target']['edition'] == edition for c in cases)
            for edition in word_profiles.EDITIONS} for form in ('qolkain', 'lom')},
        'semantic_validation': False, 'independent_confirmation': False,
        'confirmed_words': 0, 'known_before_collection': 'All QOLKAIN lines and several LOM contexts already exposed; no blind preregistration.'}
    (D / 'EP_CONTEXT_CASES.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    with (D / 'EP_CONTEXT_CASES.tsv').open('w', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(['form','edition','locus','target_source_id','whole_raw_line','separation_fixed_values','mixing_fixed_values'])
        for c in cases:
            a = [' | '.join(z['G'] or 'UNREAD:'+z['raw'] for z in app['annotations']) for app in c['applications']]
            t = c['target'];w.writerow([c['form'],t['edition'],t['locus'],t['source_group_id'],' '.join(r['ivtff_group_raw'] for r in c['whole_line']),*a])
    print(json.dumps({'counts':result['counts'], 'cases':len(cases), 'semantic_validation':False}))

if __name__ == '__main__':
    run()
