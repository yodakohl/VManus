#!/usr/bin/env python3
"""Audit one existing CountSpec draft; no numeral search or corpus test."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'vmanus-work').is_file())


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pp = HERE / 'CARDINAL157_PLAN_20261015.json'
    rp = HERE / 'CARDINAL157_READING_20261015.json'
    wp = HERE / 'CARDINAL157_WORD_ACCOUNT_20261015.json'
    wrp = HERE / 'CARDINAL157_WORD_REVIEW_20261015.json'
    plan, actual, account, review = read(pp), read(rp), read(wp), read(wrp)
    source_path = ROOT / plan['source']
    source = read(source_path)
    assert sha(source_path) == plan['source_sha256'] == actual['source_sha256']
    assert sha(pp) == actual['plan_sha256'] == account['source_packet']['sha256']
    assert account['source_packet']['path'] == str(pp.relative_to(ROOT))
    assert sha(wp) == review['contract_sha256']
    assert review['selection_status'] == 'NOT_READY_FOR_PREFERENCE'
    assert review['surface_decision'] == 'NO_TESTABLE_PREDICTIONS'
    assert review['semantic_decision'] == 'NO_AUTOMATIC_MEANING_PREFERENCE'
    assert actual['preserved_documents'] == source['documents']
    assert actual['preserved_explicit_anchor_sites'] == source['explicit_anchor_sites']
    assert actual['word_review'] == wrp.name

    traces = [t for d in source['documents'] for t in d['trace']]
    by_id = {t['id']: t for t in traces}
    assert len(by_id) == len(traces)
    descriptions = defaultdict(list)
    expected_assertions, other_relations, constructions = [], [], []
    for document in source['documents']:
        for record in document['records']:
            for entry in record['ordered_entries']:
                descriptions[entry['referent']].append((entry['descriptor'], [entry['source_id']]))
            for c in record['constructions']:
                constructions.append(c)
                assert [by_id[s]['raw'] for s in c['source_ids']] == c['raw']
                descriptions[c['argument']].append((c['descriptor'], c['source_ids']))
                for relation in c['relations']:
                    if relation['relation'] == 'daiin':
                        expected_assertions.append(dict(
                            id=c['id'], page=document['page'], paragraph=record['context'],
                            source_ids=c['source_ids'], raw=c['raw'], kind=c['descriptor'],
                            group=c['argument'], anchor_source_id=c['anchor_source_id'], required_count='c',
                            condition='finite_nonempty(G) and all(Kind_X(g) for g in G) and len(G)==c',
                            native_evaluation='UNBOUND_GROUP_MEMBERSHIP_AND_c'))
                    else:
                        other_relations.append(dict(construction=c['id'], **relation))
    assert expected_assertions == actual['assertions']
    assert other_relations == actual['other_relations']
    actual_groups = {g['variable']: g for g in actual['groups']}
    assert len(actual_groups) == len(actual['groups']) and set(actual_groups) == set(descriptions)
    for name, contributions in descriptions.items():
        g = actual_groups[name]
        assert set(g) == {'variable', 'member_kind_constraints', 'evidence', 'members', 'cardinality', 'membership_status'}
        assert set(g['member_kind_constraints']) == {word for word, _ in contributions}
        assert len(g['member_kind_constraints']) == len(set(g['member_kind_constraints']))
        assert Counter(tuple(ids) for ids in g['evidence']) == Counter(tuple(ids) for _, ids in contributions)
        assert g['members'] is None and g['cardinality'] is None
        assert g['membership_status'] == 'UNBOUND_NOT_CONSTRUCTED_FROM_WORDS_OR_c'
    kinds = {word for contributions in descriptions.values() for word, _ in contributions}
    contributing = [sid for a in expected_assertions for sid in a['source_ids']]
    assert len(contributing) == len(set(contributing))
    summary = dict(raw_groups=len(traces), count_constructions=len(expected_assertions),
                   contributing_raw_groups=len(contributing), other_structurally_preserved_raw_groups=len(traces) - len(contributing),
                   count_group_variable_names=len({a['group'] for a in expected_assertions}),
                   known_group_memberships=sum(g['members'] is not None for g in actual_groups.values()),
                   known_native_cardinalities=sum(g['cardinality'] is not None for g in actual_groups.values()),
                   shared_count_parameters=len({a['required_count'] for a in expected_assertions}), selected_c=None,
                   other_unknown_relation_occurrences=len(other_relations), confirmed_translated_words=0)
    assert summary == actual['summary']
    anchored_counts = [a for a in expected_assertions if a['anchor_source_id'] is not None]
    assert [(a['raw'], a['kind'], a['anchor_source_id']) for a in anchored_counts] == [
        (['daldaiin'], 'dal', 'IT2a|f45r.10|G009'),
        (['daldaiin'], 'dal', 'IT2a|f89r1.7|G004')]
    assert len(source['explicit_anchor_sites']) == 5
    assert len(kinds) == 97

    # Reconstruct only the four illustration outcomes already in the draft.
    # These sets are synthetic examples, never instantiated manuscript groups.
    a, b, bigger = {'a', 'b'}, {'u', 'v'}, {'u', 'v', 'w'}
    examples = actual['formal_examples']
    assert examples['status'] == 'FORMAL_OPERATOR_EXAMPLES_NOT_NATIVE_EVIDENCE'
    assert examples['equal_count_distinct_members'] == dict(
        sizes=[len(a), len(b)], chosen_example_c=2, satisfied=(len(a) == len(b) == 2))
    assert examples['unequal_fixed_groups'] == dict(sizes=[len(a), len(bigger)],
                                                    any_common_positive_c=(len(a) == len(bigger) and bool(a)))
    union = set().union(a, a, a, a, a)
    assert examples['identical_group_repeated_five_times'] == dict(
        each_size=len(a), union_size=len(union), sum_of_five_written_counts=5 * len(a),
        union_equals_sum=(len(union) == 5 * len(a)))
    assert examples['wrong_member_kind'] == dict(group_size=len(a), chosen_example_c=2,
                                                satisfied=(bool(a) and a <= {'a'} and len(a) == 2))
    assert actual['all_positive_c_possible']['status'] == 'UNDER_UNBOUND_MEMBERSHIP_NO_c_IDENTIFICATION'
    paths = [pp, rp, wp, wrp, source_path, HERE / 'CARDINAL157_BUILD_20261015.py']
    report = dict(status='PASS_COUNTSPEC_ACCOUNTING_NO_NUMERAL_OR_MEANING_SELECTION',
                  method='Independent projection of the20existing relation constructions and allordinary anchors; uniform-lift and source-identity accounting; direct arithmetic of the four already supplied formal examples. No builder import/execution or new corpus.',
                  input_sha256={str(p.relative_to(ROOT)): sha(p) for p in paths}, validator_sha256=sha(Path(__file__)),
                  derived_summary=summary, uniformly_lifted_group_variables=len(actual_groups),
                  unassigned_member_kind_predicates=len(kinds), count_assertions=expected_assertions,
                  preserved_explicit_anchor_sites=source['explicit_anchor_sites'],
                  word_review_status=review['selection_status'],
                  logical_scope_review=[
                      'CountSpec is a concrete proposed DAIIN quantity meaning, not a preferred or confirmed meaning. Preserved documents retain input alignment/source trace; their former DAIIN relation is replaced by CountSpec. The other-relations list contains only the four other marker types.',
                      'Kind_X is evaluated on each member, not merely attached as a group-level label. The supplied constructor takes a fixed finite frozenset and a callable kind predicate; it does not require the full kind extension to be finite. No native truth evaluation has occurred.',
                      'All nominal variables, including ordinary anchors and nonquantity arguments, receive the same finite-group/member-kind lift. This is new semantics, not inherited proof of actual groups.',
                      'One c occurs in every quantity assertion. Ten different variable names impose no group inequality, overlap prohibition or count-unit change.',
                      'All132groups and five source-anchor choices are preserved. Ten CountSpec constructions use17groups;115othergroups remain structural/untranslated. Only two quantity sites have explicit DAL source anchors.',
                      'For any positive c, one may construct a possible model with a c-member domain, every group variable denoting that same set, all97unknown kinds containing those members and the other unknown relations satisfied. This preserves all explicit anchors and proves nonidentification, not a native interpretation.',
                      'That existential witness is not an operational instruction to invent members to match c. Actual CountSpec evaluation requires fixed independently individuated members first.',
                      'For the five f89r1groups no5cunion size follows without disjointness. The repeated-two-member example demonstrates overlap only;2and3 are not native numeral candidates.',
                      'The supplied constructor has concrete quantitative content, but group membership, kind meanings and c remain unbound. Allpositivecpossible is logical feasibility, not empirical support.',
                      'Stored word review stays NOT_READY_FOR_PREFERENCE. No universal postfix-host claim, new numeral series, object identity, confirmedword or statistical comparison is licensed.',
                  ], changes='Only this validator and its compact accounting JSON written. All inputs/builders/observations unchanged.')
    (HERE / 'CARDINAL157_ACCOUNTING_20261015.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'summary': summary, 'unknown_kinds': len(kinds)}, sort_keys=True))


if __name__ == '__main__':
    main()
