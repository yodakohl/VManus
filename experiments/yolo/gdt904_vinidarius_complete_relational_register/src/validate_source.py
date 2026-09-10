#!/usr/bin/env python3
"""Independent frozen A/M source projection and interval-stack validator.
Does not import the compiler or access target material.
"""
import collections
import hashlib
import html
import json
import re
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
MEM = ROOT / 'research_registry/proposals/vinidarius_source_checkpoint'
WORD = re.compile(r'[A-Za-z]+|[0-9]+')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_word_coordinates(raw, start):
    # Independently align raw words after masking the two punctuation entities.
    # No decoded-character coordinate-map algorithm from the compiler is used.
    def mask(match):
        assert not WORD.search(html.unescape(match.group()))
        return ' ' * len(match.group())
    masked = re.sub(r'&[^;]+;', mask, raw)
    decoded = html.unescape(raw)
    left, right = list(WORD.finditer(masked)), list(WORD.finditer(decoded))
    assert [x.group() for x in left] == [x.group() for x in right]
    return {y.span(): (start+x.start(), start+x.end()) for x, y in zip(left, right)}


def main():
    a = json.loads((MEM/'SOURCE_TYPED_A.json').read_text())
    m = json.loads((MEM/'SOURCE_TYPED_M.json').read_text())
    actual = json.loads((EXP/'artifacts/SOURCE.json').read_text())
    assert digest(MEM/'SOURCE_TYPED_A.json') == '24677f284bfdb6bdc91cf1d9d126f760a2b7cb215645c5ba534ddc892c7e7d86'
    assert digest(MEM/'SOURCE_TYPED_M.json') == 'dafab28e525b812ecc61b94a7f265f6289ca2eb994fe270b9b55f58b28d18016'
    for path, sha in actual['source_bindings'].items():
        assert digest(ROOT/path) == sha
    amap = {}
    for r in a['records'] + [{'source':'pantry','segments':[a['common_pantry_closing']]}]:
        for seg in r['segments']:
            assert html.unescape(seg['raw']) == seg['text']
            coords = raw_word_coordinates(seg['raw'], seg['html_span'][0])
            for token in seg['mentions'] + seg['omitted_tokens']:
                span = tuple(token['span'])
                assert seg['text'][span[0]:span[1]] == token['surface']
                key = (r['source'], *coords[span])
                assert key not in amap
                amap[key] = token
    expected_records = m['records'] + [m['pantry_postlude']]
    assert len(expected_records) == len(actual['records']) == 38
    assert [r['id'] for r in actual['records']] == [r['id'] for r in expected_records]
    origin_counts = collections.Counter()
    additions = collections.Counter()
    omitted = collections.Counter()
    atoms = set()
    seen_a = set()
    intervals_count = total_tokens = emitted_count = 0
    audits = collections.defaultdict(list)
    for src, got in zip(expected_records, actual['records']):
        assert got['text'] == src['text']
        assert got['id'] == src['id']
        source_tokens = {}
        for origin in ('mentions', 'unresolved_tokens', 'omitted_tokens'):
            for token in src[origin]:
                key = tuple(token['span'])
                assert key not in source_tokens
                source_tokens[key] = (origin, token)
        assert sorted(source_tokens) == [x.span() for x in WORD.finditer(src['text'])]
        assert sorted(source_tokens) == [tuple(t['span']) for t in got['tokens']]
        coord_map = {}
        for seg in src['source_segments']:
            offset = seg['record_text_span'][0]
            assert html.unescape(seg['source_html']) == seg['text']
            assert src['text'][slice(*seg['record_text_span'])] == seg['text']
            for span, rawspan in raw_word_coordinates(seg['source_html'], seg['html_character_span'][0]).items():
                coord_map[(span[0]+offset, span[1]+offset)] = (seg['document'], *rawspan)
        lexical = []
        for out in got['tokens']:
            span = tuple(out['span'])
            origin, token = source_tokens[span]
            coord = coord_map[span]
            at = amap[coord]
            seen_a.add(coord)
            assert token['surface'] == out['surface'] == at['surface'] == src['text'][slice(*span)]
            assert list(coord) == out['source_coordinate']
            assert out['m_origin'] == origin and out['m_category'] == token['category']
            assert out['a_category'] == at.get('category')
            assert out['role_alternatives'] == token.get('possible_categories',token.get('category_alternatives',[]))
            origin_counts[origin] += 1
            total_tokens += 1
            active = origin != 'omitted_tokens'
            if origin == 'omitted_tokens':
                active = at.get('category','OMITTED') not in {'OMITTED','SOURCE_ORDINAL_NOT_SEMANTIC','TOOL_OR_MEDIUM_OUTSIDE_DECLARED_CATEGORIES','EXPLICIT_CONDITION_MARKER'}
            lower = token['surface'].lower()
            if src['id'] == 'R01' and lower in ('2','una'):
                active = False
            assert out['emitted'] == active
            if not active:
                assert out['atom'] is None
                omitted[at.get('category','OMITTED')] += 1
                continue
            basis = at if origin == 'omitted_tokens' else token
            lemma = basis.get('lemma')
            if origin == 'unresolved_tokens':
                lemma = {'spica':'spica','tritura':'tritura','conditum':'conditus','friges':'frigo','frigantur':'frigo'}.get(lower)
            if lower in ('friges','frigantur','frigis'):
                lemma = 'frigo'
            if lower == 'fiat':
                lemma = 'fio'
            if lower == 'supersit':
                lemma = 'supersum'
            identity = 'LEX:'+lemma if lemma else 'LITERAL:'+lower
            if basis['category'] == 'NUMERAL':
                cardinal_families = {'1':{'Roman_I','I','unus'},'2':{'duo'},'3':{'Roman_III','III'},'10':{'decem'},'50':{'Roman_L','L'}}
                for number, aliases in cardinal_families.items():
                    if lemma in aliases:
                        identity = 'NUMBER:'+number
            assert out['atom'] == identity, (src['id'], lower, out['atom'], identity)
            lexical.append(identity)
            atoms.add(identity)
            emitted_count += 1
            if origin == 'omitted_tokens':
                additions[at['category']] += 1
            if lower in {'amulo','amulabis','addes','addis','adices','adicies','fiat','aspargis','adspargis','folium','folia','spica','tritura','supersit','sit','friges','frigantur','frigis','quantum','cochleare','una'}:
                audits[lower].append({'record':src['id'],'span':list(span),'atom':identity})
        assert lexical == got['lexical']
        assert [x for x in got['trace'] if not x.startswith(('OPEN:','CLOSE:'))] == lexical
        expected_intervals = {(tuple(s['span']),s['kind']):s for s in src['explicit_spans']}
        assert len(expected_intervals) == len(src['explicit_spans']) == len(got['intervals'])
        for span in got['intervals']:
            key = (tuple(span['span']),span['kind'])
            assert key in expected_intervals
            assert span['surface'] == expected_intervals[key]['surface'] == src['text'][slice(*span['span'])]
            assert span['token_members'] == [i for i,t in enumerate(got['tokens']) if span['span'][0] <= t['span'][0] and t['span'][1] <= span['span'][1]]
        # Independent coordinate sweep with explicit stack. OPEN equal ties are
        # alphabetic, CLOSEs pop the stack; no compiler rank/event sorting used.
        stack, trace, recovered = [], [], []
        by_start = collections.defaultdict(list)
        for (bounds, kind) in expected_intervals:
            by_start[bounds[0]].append((bounds[1],kind,bounds[0]))
        lexical_at = {t['span'][0]:t['atom'] for t in got['tokens'] if t['emitted']}
        positions = sorted(set(lexical_at) | {x for bounds,kind in expected_intervals for x in bounds})
        for pos in positions:
            while stack and stack[-1][0] == pos:
                end,kind,start = stack.pop()
                trace.append('CLOSE:'+kind)
                recovered.append(((start,end),kind))
            assert not stack or stack[-1][0] > pos
            for entry in sorted(by_start[pos],key=lambda x:(-x[0],x[1])):
                if stack:
                    assert entry[0] <= stack[-1][0]
                stack.append(entry)
                trace.append('OPEN:'+entry[1])
            if pos in lexical_at:
                trace.append(lexical_at[pos])
        assert not stack
        assert sorted(recovered) == sorted(expected_intervals)
        assert trace == got['trace']
        intervals_count += len(recovered)
    unused_a = [v for k,v in amap.items() if k not in seen_a]
    assert len(unused_a) == 31 and all(x['category']=='SOURCE_ORDINAL_NOT_SEMANTIC' for x in unused_a)
    assert total_tokens == 1217 and intervals_count == 175
    assert dict(origin_counts) == actual['totals'] == {'mentions':862,'unresolved_tokens':15,'omitted_tokens':340}
    assert len(atoms) == actual['lexical_atoms']
    result = {
        'schema':'GDT904_INDEPENDENT_SOURCE_VALIDATION_V1','status':'PASS','source_only':True,'target_access':False,
        'source_artifact_sha256':digest(EXP/'artifacts/SOURCE.json'),
        'validator_sha256':digest(Path(__file__)),
        'checks':{'records':38,'tokens':total_tokens,'M_origins':dict(origin_counts),'A_outside_tokens_all_h4_ordinals':31,'intervals_recovered_by_stack':intervals_count,'emitted':emitted_count,'omitted':total_tokens-emitted_count,'distinct_lexical_atoms':len(atoms),'substantive_A_additions':dict(additions),'omissions_by_A_category':dict(omitted),'all_emitted_identity_policy_checks':True,'all_raw_source_coordinates_independent_word_alignment':True},
        'reconciliation_decisions':{
            'F01':'amulum noun and amulo verb retained distinctly','F02':'addo/adicio distinct','F03':'fiat=fio','F04':'aspargo/adspargo distinct','F05':'folium lemma shared; occurrence role separate','F06':'all unresolved mentions retained; only M written nominal membership, no deeper attachment claim','F07':'31h4 ordinals outside; internal2 and comitativeuna omitted; explicit cardinals normalized','F08':'A substantive lexical predicates added; A condition-class cum omitted, M clause boundaries retained','F09':'A written unbound references added without antecedent substitution','F10':'175span stack exact; cochleare retained; quantities not executed','F11':'unresolved titles retained; equipment headings omitted by projection; postlude once','F12':'37electronic records plus postlude; malformedI.2 all tokens accounted'},
        'selected_identity_audits':dict(audits),
        'claim_ceiling':'Complete declared literal projection; no full dependency parsing, executed recipe, target compatibility, or meaning certified. Scope markers may be deleted only for a necessary-condition relaxation: a relaxed fit cannot certify a full trace fit.'
    }
    (EXP/'artifacts/SOURCE_VALIDATION.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'PASS','tokens':total_tokens,'intervals':intervals_count,'emitted':emitted_count,'atoms':len(atoms)}))


if __name__ == '__main__':
    main()
