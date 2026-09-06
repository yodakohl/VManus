import json
from pathlib import Path

import pytest

from tools.semantic_source_review import lookup, main

REVIEW = 'research_registry/decisions/review.json'
SOURCE = 'experiments/yolo/example/REPORT.md'
HASH = 'a' * 64


def write_review(tmp_path, document):
    p = tmp_path / REVIEW
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(document))
    return [REVIEW]


def evidence(lo=1, hi=16):
    return {'path': SOURCE, 'line': lo, 'line_end': hi, 'sha256': HASH,
            'quote': 'No source file is created or opened.'}


def row(e=None, decision='scoped_proposition_candidates', source_id='PARENT'):
    return {'source_id': source_id, 'decision': decision,
            'full_block_read': True, 'evidence': evidence() if e is None else e,
            'reason': 'Whole ladder claim compared; no semantic confirmation.'}


def test_object_and_list_evidence_are_equivalent(tmp_path):
    reviews = write_review(tmp_path, {'reviewed_blocks': [row(evidence())]})
    first = lookup(tmp_path, review_paths=reviews, source_id='PARENT',
                   path=SOURCE, line=8, line_end=11, source_sha256=HASH)
    write_review(tmp_path, {'reviewed_blocks': [row([evidence()])]})
    second = lookup(tmp_path, review_paths=reviews, source_id='PARENT',
                    path=SOURCE, line=8, line_end=11, source_sha256=HASH)
    for result in [first, second]:
        assert result['results'][0]['relationships'] == ['exact_id', 'contains_span']
        assert result['results'][0]['source_binding'] == 'matches_supplied_hash'
        assert result['source_bytes_read'] is False
    assert first['results'][0]['evidence'] == second['results'][0]['evidence']


def test_both_real_open_statuses_remain_pending_after_full_read(tmp_path):
    reviews = write_review(tmp_path, {'reviewed_blocks': [
        row(decision='scope_open'), row(decision='scope_comparison_open'),
        row(decision='unrecognized_new_status')]})
    result = lookup(tmp_path, review_paths=reviews, source_id='PARENT')
    assert [r['review_state'] for r in result['results']] == ['pending', 'pending', 'unknown']
    assert all(r['full_read_recorded'] for r in result['results'])


def test_real_de_style_sibling_does_not_inherit_parent_identity(tmp_path):
    # DG: DE13, source fd1c... lines8–11 inside AL:b681... lines1–16.
    reviews = write_review(tmp_path, {'reviewed_blocks': [
        row(source_id='LEGACY_COMPONENT:b681ba4a4b1e05317ec4')]})
    result = lookup(tmp_path, review_paths=reviews,
                    source_id='LEGACY_COMPONENT:fd1c875769fb1f96fecc',
                    path=SOURCE, line=8, line_end=11, source_sha256=HASH)
    r = result['results'][0]
    assert r['relationships'] == ['contains_span']
    assert 'skip' not in r and 'covered' not in r
    assert 'no automatic skip' in result['meaning']


def test_partial_overlap_and_quotes_never_become_assessed_source_rows(tmp_path):
    reviews = write_review(tmp_path, {
        'reviewed_blocks': [row(evidence(8, 12))],
        'cards': [{'id': 'C', 'source_id': 'CHILD', 'evidence': evidence()}],
        'selection': [row()], 'excluded': [row()]})
    result = lookup(tmp_path, review_paths=reviews, source_id='CHILD',
                    path=SOURCE, line=10, line_end=16)
    assert result['matched'] == 1
    assert result['results'][0]['relationships'] == ['partial_overlap']
    assert lookup(tmp_path, review_paths=reviews, source_id='CHILD')['matched'] == 0


def test_stale_and_unknown_source_bindings_are_visible(tmp_path):
    incomplete = evidence()
    del incomplete['sha256']
    reviews = write_review(tmp_path, {'results': [row(), row(incomplete)]})
    results = lookup(tmp_path, review_paths=reviews, source_id='PARENT',
                     source_sha256='b' * 64)['results']
    assert [r['source_binding'] for r in results] == ['mismatch_or_conflict', 'unknown']
    assert len(results) == 2  # Staleness never silently hides work.


def test_paging_is_bounded_and_unknown_does_not_become_complete(tmp_path):
    reviews = write_review(tmp_path, {'source_reassessments': [
        row(decision='some_unrecognized_decision', source_id=f'ID{i:04}')
        for i in range(120)]})
    result = lookup(tmp_path, review_paths=reviews, path=SOURCE, line=2,
                    limit=8, offset=8)
    assert len(result['results']) == 8
    assert result['matched'] == 120 and result['next_offset'] == 16
    assert all(r['review_state'] == 'unknown' for r in result['results'])
    assert all(len(r['reason']) <= 500 for r in result['results'])


def test_reading_whole_report_does_not_cover_omitted_marker_claim(tmp_path):
    # DG Pass347: prior handoff card does not itself state the marker-reset rule.
    reviews = write_review(tmp_path, {'reviewed_blocks': [dict(
        row(), card_ids=['CLEAN_GAP_AL:h3_b2_extract_handoff'])]})
    result = lookup(tmp_path, review_paths=reviews, source_id='NEW_MARKER_CLAUSE',
                    path=SOURCE, line=3, line_end=6)
    assert result['results'][0]['relationships'] == ['contains_span']
    assert not any(k in result['results'][0] for k in ['coverage', 'equivalent', 'skip'])


def test_cli_and_input_boundaries(tmp_path, capsys):
    write_review(tmp_path, {'dispositions': [row()]})
    assert main(['--root', str(tmp_path), '--review', REVIEW,
                 '--source-id', 'PARENT', '--limit', '1']) == 0
    assert json.loads(capsys.readouterr().out)['matched'] == 1
    for bad in ['../private.json', str(Path('outside_review.json').absolute()), 'research_registry/runtime/private.json']:
        with pytest.raises(ValueError):
            lookup(tmp_path, review_paths=[bad], source_id='PARENT')
    with pytest.raises(ValueError):
        lookup(tmp_path, review_paths=[REVIEW], path=SOURCE, line=9, line_end=2)
    with pytest.raises(ValueError):
        lookup(tmp_path, review_paths=[REVIEW], source_id='PARENT', limit=21)


def test_current_open_correction_takes_precedence_over_original_decision(tmp_path):
    corrected = row(decision='scope_comparison_open')
    corrected['original_decision'] = 'existing_whole_reading'
    fallback = row()
    del fallback['decision']
    fallback['original_decision'] = 'scope_open'
    reviews = write_review(tmp_path, {'results': [corrected, fallback]})
    results = lookup(tmp_path, review_paths=reviews, source_id='PARENT')['results']
    assert results[0]['review_state'] == 'pending'
    assert results[0]['decision'] == 'scope_comparison_open'
    assert results[0]['original_decision'] == 'existing_whole_reading'
    assert results[1]['review_state'] == 'pending'
    assert results[1]['decision'] == 'scope_open'
