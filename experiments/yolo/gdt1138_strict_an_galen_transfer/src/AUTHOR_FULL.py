"""Application/report wrapper only: semantics remain in immutable AUTHOR_CORE."""
from pathlib import Path
import json
import AUTHOR_CORE as core

ROOT = Path(__file__).resolve().parent.parent


def raw_groups(record):
    out = []
    for line in record['lines']:
        for within_line, (form, source_id) in enumerate(zip(line['words'],line['source_ids'])):
            out.append({'form':form,'source_id':source_id,'locus':line['locus'],
                        'row':line['row'],'offset':line['offset'],
                        'within_line':within_line,'start':line['start'],'end':line['end'],
                        'anchor_eligible':line['anchor_eligible']})
    return out


def replay(interventions=None, reader='ZL3b'):
    source = json.loads((ROOT/'src/SOURCE.json').read_text())
    if reader=='ZL3b':
        raw = source['whole_record']
    elif reader=='IT2a':
        raw = source['alternative_reader_records']['IT2a']
    elif reader=='RF1b':
        return {'status':source['RF_status'],'raw_record':source['alternative_reader_records']['RF1b']}
    else:
        raise ValueError('Only owned ZL3b/IT2a/RF1b allowed')
    groups = raw_groups(raw)
    result = core.replay(groups, interventions)
    for row, group in zip(result['trace'], groups):
        row['raw_group'] = group
    result['reader'] = reader
    result['raw_record'] = raw
    return result


def account():
    source = json.loads((ROOT/'src/SOURCE.json').read_text())
    zl, it = replay(), replay(reader='IT2a')
    return {
        'schema':'gdt1138-author-account-v1','outcome':'PARTIAL_NO_CAPACITY',
        'exposure':{'direct_SOURCE_read_after_CORE_GO':True,'CORE_GO_receipt_utc':'2026-10-02T09:19:23.740563+00:00',
                    'informational_target_blinding':False,'independent_confirmation':0,'confirmed_words':0},
        'complete_selected_source':source['complete_selected_source'],
        'source_obligations_locked':source['source_obligations_locked'],
        'strongest_prior_countercases':source['strongest_prior_countercases'],
        'literal34':core.SPEC['literal_entries'],'operators':core.SPEC['fixed_operators'],
        'costs':core.SPEC['costs'],'assumptions':core.SPEC['assumptions'],
        'source_separators':source['separator_metadata'],
        'ZL3b':zl,'IT2a':it,'RF1b':replay(reader='RF1b'),
        'scope':'Source-side entireII44.2 is retained as external historical comparison. No connected target translation of it is claimed.',
        'exact_barrier':{
            'FIRST':'Requires ordered-water-context x WATER. Bare aiin9 retains written IMMEDIATE_TRANSFER8 description, not WATER. No prior explicit WATER field or ordered-water-context exists.',
            'OTHER':'Requires water-reference x WATER. Bare aiin12 retains written OTHER11 unsaturated description, not WATER. FIRST is already blocked; no prior W0 exists.',
            'daiin':'d+aN retains quoted FULLY_BOIL27 and complete lexical/norm closure. No frozen syntax uses that returned ref as later rationale/explanandum; no BECAUSE introduced.',
            'general':'Other known literals remain description contributions with unfilled predicate arguments. Neither lexical completeness nor49-row coverage is whole semantic completion.'},
        'manuscript_finding':'No new manuscript finding or meaning binding. This fixed candidate has an explicit construction-capacity barrier.',
        'control_finding':'Required water-role/content, food-vs-water and quoted-prohibition downstream sensitivity remain unestablished; do not score absent consumers as PASS.',
        'engineering_finding':'Pure replay exposes actual immutable payloads and projection barriers for independent inspection; outcome does not certify full C functional transfer.',
        'intervention_api':{'call':'AUTHOR_FULL.replay(interventions, reader)',
                            'keys':'1-based actual written positions at aN/d+aN sites, as int or string',
                            'supported':['delete_donor: true','replace_payload: actual alternative description dictionary'],
                            'semantics':'Core code and external source duties stay fixed. Donor deletion or field replacement can change projection/reference availability; no meaningful later predicate exists in this candidate.'},
        'not_claimed':['complete49meaningful connected contributions','water/food content-sensitive downstream predicate','quoted-prohibition content-sensitive later rationale','independent confirmation','English meaning selection'],
        'reopening_requirement':'A prospectively licensed prior written WATER producer/projection and noncircular contexts, plus independently specified retained-content consumers. This frozen candidate is not repaired.'
    }


if __name__ == '__main__':
    print(json.dumps(account(),ensure_ascii=False,indent=2))
