"""Check fixed-source fidelity, full coverage and local consequences independently."""
from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import json
import run

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
ART = EXP / 'artifacts'
lock = json.loads((EXP / 'PREREG_LOCK.json').read_text())
for name, digest in lock['files'].items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
m = json.loads((EXP / 'src/MODEL.json').read_text())
source = json.loads((ROOT / m['source']).read_text())['groups']
byid = {r['source_group_id']: r for r in source}
assert len(source) == len(byid) == 1408
lex = {k: dict(json.loads((ROOT / m['base_model']).read_text())['models']['M']['lexicon']) for k in ['R', 'T']}
for p in m['extensions']:
    ext = json.loads((ROOT / p).read_text())['models']
    for k in lex:
        lex[k].update(ext[k]['lexicon'])
assert [len(lex[k]) for k in ['R', 'T']] == [21, 21]
assert m['new_word_values'] == {}
prior = list(csv.DictReader((ROOT / m['prior_alignment']).open(), delimiter='\t'))
assert len(prior) == 2816
assert len({(r['model'], r['source_group_id']) for r in prior}) == 2816
for r in prior:
    src = byid[r['source_group_id']]
    assert all(r[k] == str(v) for k, v in src.items())
    raw = src['ivtff_group_raw']
    assert [r['gloss'], r['role']] == lex[r['model']].get(raw, ['⟦' + raw + '⟧', 'UNREAD'])
focus = {sid: r for sid, r in byid.items() if r['locus'] in ['f77r.18', 'f77r.19', 'f77r.20']}
assert len(focus) == 81
rows = list(csv.DictReader((ART / 'CANDIDATE_ROLES.tsv').open(), delimiter='\t'))
assert len(rows) == len({(r['candidate'], r['source_group_id']) for r in rows}) == 324
expected_scopes = {
    'F': {'PRE': 'OUTSIDE_THIS_CONDITION', 'K': 'OUTSIDE_THIS_CONDITION', 'M': 'CONDITION_MARKER', 'A': 'ANTECEDENT', 'B': 'CONSEQUENT'},
    'P': {'PRE': 'OUTSIDE_THIS_CONDITION', 'K': 'CONSEQUENT', 'M': 'CONDITION_MARKER', 'A': 'ANTECEDENT', 'B': 'OUTSIDE_THIS_CONDITION'}}
blocks = {}
for ed in ['ZL3b', 'IT2a', 'RF1b']:
    for loc in ['f77r.18', 'f77r.19', 'f77r.20']:
        rr = sorted([r for r in focus.values() if r['edition'] == ed and r['locus'] == loc], key=lambda r: int(r['source_group_index']))
        if loc.endswith('.18'):
            parts = ['PRE'] * len(rr)
        elif loc.endswith('.19'):
            assert ' '.join(r['ivtff_group_raw'] for r in rr) == 'qokeedy lchey lsheey qokeedy qokeedy qokar qokeey laiin chey'
            parts = ['K'] * 8 + ['M']
        else:
            assert ' '.join(r['ivtff_group_raw'] for r in rr) == 'qotain sheal qokeedy qoteey qokain sheey qotedy dalchedy'
            parts = ['A'] * 3 + ['B'] * 5
        blocks.update({r['source_group_id']: p for r, p in zip(rr, parts)})
for r in rows:
    src = focus[r['source_group_id']]
    assert all(r[k] == str(v) for k, v in src.items())
    mid, direction = r['candidate'].split('_')
    assert r['partition'] == blocks[r['source_group_id']]
    assert r['local_scope'] == expected_scopes[direction][r['partition']]
    raw = r['ivtff_group_raw']
    assert [r['gloss'], r['lexical_role']] == lex[mid].get(raw, ['⟦' + raw + '⟧', 'UNREAD'])
    assert r['participant_binding'] == 'UNRESOLVED' and r['factual_assertion'] == 'False'
summaries = list(csv.DictReader((ART / 'CANDIDATE_SUMMARY.tsv').open(), delimiter='\t'))
assert len(summaries) == 12
for cid in ['R_F', 'R_P', 'T_F', 'T_P']:
    assert {r['source_group_id'] for r in rows if r['candidate'] == cid} == set(focus)
    for ed, count in [('ZL3b', 28), ('IT2a', 27), ('RF1b', 26)]:
        rr = [r for r in rows if r['candidate'] == cid and r['edition'] == ed]
        assert len(rr) == count and sum(r['lexical_role'] != 'UNREAD' for r in rr) == 9
        def ids(scope, role=None):
            return '|'.join(r['source_group_id'] for r in rr if r['local_scope'] == scope and (role is None or r['lexical_role'] == role))
        sc = next(s for s in summaries if s['candidate'] == cid and s['edition'] == ed)
        for key, scope, role in [('antecedent_ids','ANTECEDENT',None), ('consequent_ids','CONSEQUENT',None), ('antecedent_flow_ids','ANTECEDENT','FLOW'), ('consequent_flow_ids','CONSEQUENT','FLOW'), ('consequent_copula_ids','CONSEQUENT','COPULA')]:
            assert sc[key] == ids(scope, role)
        assert int(sc['known_groups']) == 9 and int(sc['unknown_groups']) == count - 9
        assert sc['complete_content_reading'] == sc['selected'] == 'False'
        assert sc['independent_meaning_tests'] == '0'
        assert sum(r['local_scope'] == 'ANTECEDENT' and r['lexical_role'] == 'FLOW' for r in rr) == 1
        assert sum(r['local_scope'] == 'CONSEQUENT' and r['lexical_role'] == 'FLOW' for r in rr) == (3 if cid.endswith('_P') else 0)
        assert sum(r['local_scope'] == 'CONSEQUENT' and r['lexical_role'] == 'COPULA' for r in rr) == (1 if cid.endswith('_F') else 0)
        assert sum(r['partition'] == 'PRE' and r['lexical_role'] in ['MOTION', 'REST_STATE'] for r in rr) == 2
        assert not any(r['ivtff_group_raw'] in ['qoteedy', 'cheey', 'teeolain', 'lchedy'] for r in rr)
# Full P1 source reconstruction uses source separators, independently of renderer join().
frame = [r for r in source if r['page'] == 'f77r' and 9 <= int(r['locus'].split('.')[1]) <= 24]
assert len(frame) == 422
for ed in ['ZL3b', 'IT2a', 'RF1b']:
    doc = (ART / f'P1_{ed}.md').read_text()
    for n in range(9, 25):
        rr = sorted([r for r in frame if r['edition'] == ed and r['locus'] == f'f77r.{n}'], key=lambda r: int(r['source_group_index']))
        text = rr[0]['ivtff_group_raw']
        for r in rr[1:]:
            text += {'DEFINITE_SPACE': ' ', 'UNCERTAIN_SMALL_SPACE': ' / ', 'DRAWING_INTERRUPTION': ' // '}[r['left_separator']] + r['ivtff_group_raw']
        assert f'## f77r.{n}\n' in doc and '`' + text + '`' in doc
res = json.loads((ART / 'RESULT.json').read_text())
assert res['selected_candidate'] is None
assert res['complete_content_readings'] == res['confirmed_words'] == res['independent_meaning_tests'] == res['new_admissions'] == 0
assert not any(res[k] for k in ['significance_claimed', 'semantics_validated', 'factual_events_inferred', 'empirical_scope_discriminator'])
for name, text in run.build().items():
    assert (ART / name).read_text() == text, name
result = {'status': 'PASS', 'checks': ['locked inputs intact', 'all2816 old alignment rows equal unchanged21-word models', 'all324 focus candidate/source pairs exact', '12 summaries checked', 'three conditional FLOW positions versus one conditional COPULA', 'all422 P1 raw groups preserved', 'no factual or confirmed-meaning claims', 'deterministic replay'], 'semantics_validated': False}
(ART / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
