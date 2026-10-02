#!/usr/bin/env python3
"""Independent read-only source validation; author review added after freezes."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_source():
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    baseline = json.loads((BASE / 'src/BASELINE34.json').read_text())
    core = json.loads((BASE / 'src/C_FIXED_OPERATORS.json').read_text())
    pp = ROOT / source['parent_path']
    assert sha(pp) == source['parent_sha256'] == baseline['parent_sha256']
    parent = json.loads(pp.read_text())
    assert source['whole_record'] == parent['target_choice']['whole_record']
    assert source['alternative_reader_records'] == parent['target_choice']['alternative_reader_records']
    assert source['complete_selected_source'] == parent['complete_selected_source']
    expected = [x for x in parent['lexicon'] if x['form'] not in {'aiin', 'daiin'}]
    assert baseline['entries'] == expected and len(expected) == 34
    cp = ROOT / core['parent_path']
    assert sha(cp) == core['parent_sha256']
    original = json.loads(cp.read_text())
    assert core['families'] == [x for x in original['families'] if x['id'] in {'aN', 'd'}]
    assert core['initial_exact_entries'] == {k: original['initial_exact_entries'][k] for k in ['aiin', 'daiin']}
    assert sha(ROOT / core['implementation_receipt']['path']) == core['implementation_receipt']['sha256']
    counts = {}
    for edition, packet in [('ZL3b', source['whole_record']), ('IT2a', source['alternative_reader_records']['IT2a'])]:
        counts[edition] = sum(len(x['words']) for x in packet['lines'])
        for line in packet['lines']:
            assert len(line['words']) == len(line['source_ids'])
            assert line['locus'] in {'f107v.' + str(i) for i in range(45, 50)}
            assert all(s.startswith(edition + '|' + line['locus'] + '|') for s in line['source_ids'])
    assert counts == {'ZL3b': 49, 'IT2a': 51}
    assert 'NOT_PRESENT' in source['separator_metadata']
    assert 'No matching complete' in source['RF_status']
    return {'status': 'SOURCE_MECHANICAL_PASS_AUTHOR_NOT_EVALUATED', 'groups': counts,
            'baseline_types': 34, 'confirmed_words': 0, 'independent_confirmation_capacity': 0}


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True))


def validate_author():
    import copy
    import datetime
    import sys
    sys.path.insert(0, str(BASE / 'src'))
    import AUTHOR_FULL as author
    core = author.core
    receipt = json.loads((BASE / 'artifacts/AUTHOR_FINAL_FREEZE.json').read_text())
    for p, expected in receipt['files'].items():
        assert sha(BASE / p) == expected, p
    pins_before = {p: sha(BASE / p) for p in receipt['files']}
    source = json.loads((BASE / 'src/SOURCE.json').read_text())
    artifact = json.loads((BASE / 'artifacts/AUTHOR_ACCOUNT.json').read_text())
    baseline = json.loads((BASE / 'src/BASELINE34.json').read_text())
    assert canonical(author.account()) == artifact
    assert artifact['literal34'] == core.SPEC['literal_entries'] == baseline['entries']
    assert artifact['operators'] == json.loads((BASE / 'src/C_FIXED_OPERATORS.json').read_text())
    assert artifact['complete_selected_source'] == source['complete_selected_source']
    assert artifact['source_obligations_locked'] == source['source_obligations_locked']
    assert artifact['source_separators'] == source['separator_metadata']
    unknown = {}
    for reader, raw in [('ZL3b', source['whole_record']), ('IT2a', source['alternative_reader_records']['IT2a'])]:
        replay = author.replay(reader=reader)
        assert replay['raw_record'] == raw
        assert [x['raw_group'] for x in replay['trace']] == author.raw_groups(raw)
        assert len(replay['trace']) == (49 if reader == 'ZL3b' else 51)
        unknown[reader] = [{'position':x['position'], 'form':x['form']} for x in replay['trace'] if x['status'] == 'UNKNOWN_WHOLE_RESIDUAL']
        for row in replay['trace']:
            if row['form'] in core.LEXICON:
                assert row['literal_entry'] == core.LEXICON[row['form']]
    assert artifact['RF1b'] == author.replay(reader='RF1b')
    primary = author.replay()
    refs = [x for x in primary['trace'] if x['form'] in {'aiin','daiin'}]
    assert [x['position'] for x in refs] == [9, 12, 28]
    contents = [json.loads(x['actual_return']['record']['content_json']) for x in refs]
    assert contents[0]['value'] == 'IMMEDIATE_TRANSFER'
    assert contents[1]['value'] == 'OTHER'
    assert all('WATER' not in x for x in contents)
    closure = contents[2]['dependency_closure']
    assert {x['id'] for x in closure} == {'written:23','written:24','written:25','written:26','written:27','construct:25','construct:27'}
    assert contents[2]['contribution']['kind'] == 'quoted-reprise'
    assert contents[2]['contribution']['norm_content']['mode'] == 'prohibited'
    # Exact retained return is immutable and detached from dictionaries exposed to a consumer.
    r = core.record('review-actual-copy', contents[2])
    b = []
    ref = core.aN(r, b)
    assert ref.record is r and b[-1] is ref
    exposed = ref.record.content
    exposed['contribution']['mode'] = 'changed-outside-record'
    assert ref.record.content == contents[2]
    immutable = False
    try:
        ref.record.content_json = '{}'
    except AttributeError:
        immutable = True
    assert immutable

    def semantic_summary(run):
        return {'water_predicates':[x['later_predicate'] for x in run['water_applications']],
                'quoted_consumer':run['quoted_reference_consumer'],
                'complete_connected_reading':run['complete_connected_reading']}

    def altered_return(ordinal, kind):
        original = core.aN
        calls = 0
        observation = {}
        def intercept(current, buffer):
            nonlocal calls
            calls += 1
            returned = original(current, buffer)
            if calls != ordinal:
                return returned
            before = returned.record.content
            observation['original_payload_sha256'] = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
            if kind == 'delete_actual_return':
                assert buffer.pop() is returned
                observation['replacement'] = 'No returned/published retained reference'
                raise ValueError('Independent deletion of actual aN return')
            changed = copy.deepcopy(before)
            deps = returned.record.dependencies
            if kind == 'remove_quote_prohibition_dependency':
                changed['contribution'].pop('norm_content', None)
                changed['dependency_closure'] = [x for x in changed['dependency_closure'] if x['content'].get('kind') != 'prohibition']
                for item in changed['dependency_closure']:
                    item['content'].pop('norm_content', None)
                deps = tuple(x for x in deps if x != 'construct:25')
            elif kind == 'change_retained_quote_mode':
                changed['contribution']['mode'] = 'executed'
                for item in changed['dependency_closure']:
                    if item['content'].get('kind') == 'quoted-reprise':
                        item['content']['mode'] = 'executed'
            else:
                raise ValueError(kind)
            replacement = core.BoundDescriptionRef(returned.id, core.record(returned.record.id, changed, deps))
            buffer[-1] = replacement
            observation['replacement_payload_sha256'] = hashlib.sha256(json.dumps(changed, sort_keys=True).encode()).hexdigest()
            assert observation['replacement_payload_sha256'] != observation['original_payload_sha256']
            return replacement
        core.aN = intercept
        try:
            result = author.replay()
        finally:
            core.aN = original
        position = [9,12,28][ordinal-1]
        observation.update({'case':kind,'actual_return_position':position,
                            'reference_status':result['trace'][position-1]['status'],
                            'water_projection_statuses':[x['projection']['status'] for x in result['water_applications']],
                            'semantic_summary':semantic_summary(result),
                            'meaningful_later_change':semantic_summary(result) != semantic_summary(primary)})
        assert result['raw_record'] == primary['raw_record']
        return observation

    interventions = [altered_return(i, 'delete_actual_return') for i in (1,2,3)]
    interventions += [altered_return(3, 'remove_quote_prohibition_dependency'), altered_return(3, 'change_retained_quote_mode')]
    assert all(not x['meaningful_later_change'] for x in interventions)
    assert all(sha(BASE / p) == h for p,h in pins_before.items())
    return {'schema':'gdt1138-independent-validation-v1','validated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_mechanical':check_source(), 'author_replay':'PASS_EXACT_FROZEN_ACCOUNT',
            'author_pins':pins_before,'outcome':'PARTIAL_NO_CAPACITY',
            'literal34':'Full entries exact; copying a lexical denotation does not apply its typed predicate',
            'trace_counts':{'ZL3b':49,'IT2a':51},'unknown_whole_residuals':unknown,
            'operators':'Actual aN exact immutable returns and d seven-record closure verified; required meaningful later consumer absent',
            'reference_producers':[{'position':x['position'],'record_id':x['actual_return']['record']['id'],'payload_kind':c.get('kind', 'collated-description'),'payload_value':c.get('value'),'WATER_field_present':'WATER' in c} for x,c in zip(refs,contents)],
            'd_closure_ids':[x['id'] for x in closure],
            'baseline_water_applications':[{'position':x['position'],'operator':x['operator'],'status':x['status'],'projection_status':x['projection']['status'],'required_noun_type':x['required_noun_type'],'required_context_type':x['required_context_type'],'context_supplied':x['context_supplied'],'later_predicate':x['later_predicate']} for x in primary['water_applications']],
            'interventions':interventions,
            'required_water_role_swap':'NOT_APPLICABLE_NO_RETAINED_W0_OR_W1_FIELDS_OR_LICENSED_TYPED_CONTEXT',
            'required_food_water_swap':'NOT_APPLICABLE_NO_BOUND_FOOD_OR_WATER_IDENTITIES_IN_RETAINED_PAYLOADS',
            'required_quoted_prohibition_sensitivity':'FAIL_TO_ESTABLISH: actual returned content/dependency changed, no later meaningful consumer',
            'construction_limit':'This frozen core has no WATER producer/projection or noncircular ordered-water context. This is not a proof that every permitted prospective productive grammar is impossible.',
            'implementation_limits':['R5 stated intervening IMMEDIATE_TRANSFER entry condition is implemented only by relative distance2; actual primary satisfies it. No off-target test/new corpus performed.', 'consume_water never constructs a water-reference even if externally supplied a WATER field and typed context; reports UNLICENSED_CONTEXT_VALUE. No such licensed actual input exists.', 'R1 gives lexical-description records, so most literal predicates remain unsaturated, not49meaningful connected contributions.'],
            'engineering_limits':['Frozen reading Markdown embeds unescaped pipes in source IDs, breaking table column rendering; JSON trace is canonical and exact. No author-file repair.'],
            'exposure':'Stage1 primary order reconstructible from46 baseline positions and3 named sites; only direct SOURCE access staged. Previously exposed manuscript, no informational target blinding.',
            'independent_confirmation':0,'confirmed_English_words':0,'root_semantic_review':'PENDING_SEPARATE_REVIEW'}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--author', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    result = validate_author() if args.author else check_source()
    if args.output:
        destination = Path(args.output).resolve()
        if BASE.resolve() not in destination.parents:
            raise ValueError('Output must stay in owned experiment')
        destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
