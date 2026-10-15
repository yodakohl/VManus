#!/usr/bin/env python3
"""Author ten fixed CountSpec assertions; do not invent native memberships/counts."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'vmanus-work').is_file())


def count_spec(members, belongs_to_kind, c):
    """Evaluate supplied finite sets, never manufacture members to match c."""
    if not isinstance(members, frozenset) or not callable(belongs_to_kind):
        raise TypeError('Supply a fixed finite group and a fixed member-kind predicate')
    if isinstance(c, bool) or not isinstance(c, int) or c < 1:
        raise ValueError('c must be a positive integer')
    return bool(members) and all(belongs_to_kind(x) for x in members) and len(members) == c


def main():
    pp = HERE/'CARDINAL157_PLAN_20261015.json'
    plan = json.loads(pp.read_text())
    source_path = ROOT/plan['source']
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == plan['source_sha256']
    base = json.loads(source_path.read_text())
    assertions, groups, other_relations = [], {}, []

    def group(name, descriptor, source_ids):
        g = groups.setdefault(name, dict(variable=name, member_kind_constraints=[],
            evidence=[], members=None, cardinality=None,
            membership_status='UNBOUND_NOT_CONSTRUCTED_FROM_WORDS_OR_c'))
        if descriptor not in g['member_kind_constraints']:
            g['member_kind_constraints'].append(descriptor)
        g['evidence'].append(source_ids)
        return g

    for document in base['documents']:
        for record in document['records']:
            for entry in record['ordered_entries']:
                group(entry['referent'], entry['descriptor'], [entry['source_id']])
            for construction in record['constructions']:
                group(construction['argument'], construction['descriptor'], construction['source_ids'])
                for relation in construction['relations']:
                    if relation['relation'] != 'daiin':
                        other_relations.append(dict(construction=construction['id'], **relation))
                        continue
                    assertions.append(dict(id=construction['id'], page=document['page'],
                        paragraph=record['context'], source_ids=construction['source_ids'],
                        raw=construction['raw'], kind=construction['descriptor'],
                        group=construction['argument'], anchor_source_id=construction['anchor_source_id'],
                        required_count='c', condition='finite_nonempty(G) and all(Kind_X(g) for g in G) and len(G)==c',
                        native_evaluation='UNBOUND_GROUP_MEMBERSHIP_AND_c'))
    assert len(assertions) == 10
    assert sum(len(a['source_ids']) for a in assertions) == 17
    assert len({t['id'] for d in base['documents'] for t in d['trace']}) == 132
    assert len({a['group'] for a in assertions}) == 10  # names, not unequal world groups

    # Three small formal examples, not manuscript observations or number estimates.
    left = frozenset({'a', 'b'}); right = frozenset({'u', 'v'}); larger = right | {'w'}
    equal = count_spec(left, lambda x:x in left, 2) and count_spec(right, lambda x:x in right, 2)
    unequal_has_common_c = len(left) == len(larger) and len(left) > 0
    reused = [left] * 5
    union_size = len(frozenset().union(*reused))
    assert equal and not unequal_has_common_c and union_size == 2
    assert not count_spec(left, lambda x:x == 'a', 2)
    examples = dict(status='FORMAL_OPERATOR_EXAMPLES_NOT_NATIVE_EVIDENCE',
        equal_count_distinct_members=dict(sizes=[2,2], chosen_example_c=2, satisfied=equal),
        unequal_fixed_groups=dict(sizes=[2,3], any_common_positive_c=unequal_has_common_c),
        identical_group_repeated_five_times=dict(each_size=2, union_size=union_size,
                                                sum_of_five_written_counts=10,
                                                union_equals_sum=False),
        wrong_member_kind=dict(group_size=2, chosen_example_c=2,
                               satisfied=count_spec(left, lambda x:x == 'a', 2)),
        number_limit='2and3 are arbitrary illustration sizes, not proposed native numeral values.')
    report = dict(status='TEN_CONDITIONAL_CARDINALITY_ASSERTIONS_NO_NATIVE_VALUE_SELECTED',
        plan_sha256=hashlib.sha256(pp.read_bytes()).hexdigest(),
        source_sha256=plan['source_sha256'],
        word_review='CARDINAL157_WORD_REVIEW_20261015.json',
        summary=dict(raw_groups=132, count_constructions=10, contributing_raw_groups=17,
                     other_structurally_preserved_raw_groups=115,
                     count_group_variable_names=10, known_group_memberships=0,
                     known_native_cardinalities=0, shared_count_parameters=1,
                     selected_c=None, other_unknown_relation_occurrences=len(other_relations),
                     confirmed_translated_words=0),
        assertions=assertions, groups=list(groups.values()), other_relations=other_relations,
        preserved_explicit_anchor_sites=base['explicit_anchor_sites'],
        preserved_documents=base['documents'], formal_examples=examples,
        all_positive_c_possible=dict(status='UNDER_UNBOUND_MEMBERSHIP_NO_c_IDENTIFICATION',
            reason='For any positive integer c, assign every group variable the same c-element set and let every unknown kind contain those members. Open identities permit this. Other relations remain free. This proves only that the current unbound draft selects no c; it is not a supplied interpretation of native groups.'),
        scope_limits=['Uniform finite-group/member-kind lift is a new semantic type assumption.',
                      'Members and their individuation must be bound before evaluating CountSpec; no per-head units or repairs.',
                      'Equal cardinality neither identifies groups nor makes their memberships disjoint.',
                      'The original P14/W94/W95/W96 decisions and local grammatical counterexamples remain.',
                      'DAIIN is proposed as quantitative here, but the existing word review gives no meaning preference.'])
    (HERE/'CARDINAL157_READING_20261015.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['summary'],indent=2))


if __name__ == '__main__':
    main()
