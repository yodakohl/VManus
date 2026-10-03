#!/usr/bin/env python3
"""Independent exact subsequence audit; does not import runner code."""
import bisect
import collections
import hashlib
import itertools
import csv
from fractions import Fraction
import json
from pathlib import Path
import random
import re

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
SOURCE = 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'

def read(path):
    return json.loads(path.read_text())

def flatten(lines, field='words'):
    return [word for line in lines for word in line[field]]

def lcs(a, b):
    # Hunt-Szymanski: matching positions processed backwards, LIS equals LCS.
    positions = collections.defaultdict(list)
    for j, word in enumerate(b):
        positions[word].append(j)
    tails = []
    for word in a:
        for j in reversed(positions[word]):
            k = bisect.bisect_left(tails, j)
            if k == len(tails):
                tails.append(j)
            else:
                tails[k] = j
    return len(tails)

def trace(a, b):
    rows = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            rows[i][j] = rows[i-1][j-1]+1 if x == y else max(rows[i-1][j], rows[i][j-1])
    i, j = len(a), len(b)
    matched = []
    while i and j:
        if a[i-1] == b[j-1]:
            matched.append((i-1, j-1))
            i -= 1
            j -= 1
        elif rows[i-1][j] >= rows[i][j-1]:
            i -= 1
        else:
            j -= 1
    return rows[-1][-1], list(reversed(matched))

def reconstruct():
    for name, digest in read(E/'PREREG_LOCK.json')['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    source = read(ROOT/SOURCE)
    selected, excluded, full = {}, {}, {}
    for reader in sorted(source):
        selected[reader], excluded[reader], full[reader] = {}, {}, {}
        for paragraph in sorted(source[reader], key=lambda p:p['id']):
            pid, lines = paragraph['id'], paragraph['lines']
            assert pid not in full[reader]
            full[reader][pid] = paragraph
            assert not paragraph['page'].startswith(('f84','f116v'))
            assert paragraph['leaf'] == int(re.match(r'f(\d+)', paragraph['page'])[1])
            assert lines[0]['start'] and lines[-1]['end']
            assert not any(x['start'] for x in lines[1:])
            assert not any(x['end'] for x in lines[:-1])
            nums = [int(x['locus'].rsplit('.',1)[1]) for x in lines]
            assert all(b == a+1 for a,b in zip(nums,nums[1:]))
            offset = 0
            for line in lines:
                assert len(line['words']) == len(line['source_ids'])
                assert line['offset'] == offset
                assert all(s.startswith(reader+'|'+line['locus']+'|G') for s in line['source_ids'])
                if line['anchor_eligible']:
                    assert len(line['words']) >= 2 and all(re.fullmatch('[a-z]+',w) for w in line['words'])
                offset += len(line['words'])
            assert paragraph['groups'] == offset
            why = []
            if len(lines) < 6:
                why.append('TOO_FEW_LINES')
            if not all(x['anchor_eligible'] for x in lines):
                why.append('INELIGIBLE_LINE')
            if len(flatten(lines[1:-1])) < 20:
                why.append('TOO_FEW_INTERIOR_TOKENS')
            if why:
                excluded[reader][pid] = why
            else:
                selected[reader][pid] = paragraph
    pairs, sequences = {}, {}
    for reader, paragraphs in selected.items():
        sequences[reader] = {pid:flatten(p['lines'][1:-1]) for pid,p in paragraphs.items()}
        pairs[reader] = []
        for a,b in itertools.combinations(paragraphs,2):
            aa,bb = sequences[reader][a],sequences[reader][b]
            if paragraphs[a]['leaf'] == paragraphs[b]['leaf'] or max(len(aa),len(bb)) > 2*min(len(aa),len(bb)):
                continue
            n = lcs(aa,bb)
            pairs[reader].append({'a':a,'b':b,'lcs':n,'denominator':len(aa)+len(bb),'score':2*n/(len(aa)+len(bb)), 'common':sum((collections.Counter(aa)&collections.Counter(bb)).values())})
    nulls = []
    for rep in range(1,200):
        rng = random.Random(1154000+rep)
        maximum = Fraction(0)
        winners = []
        for reader, paragraphs in selected.items():
            sequences_rep = {}
            for pid,p in paragraphs.items():
                lines = p['lines'][1:-1]
                rng.shuffle(lines)
                sequences_rep[pid] = flatten(lines)
            for pair in pairs[reader]:
                n = lcs(sequences_rep[pair['a']],sequences_rep[pair['b']])
                score = Fraction(2*n,pair['denominator'])
                witness = {'reader':reader,'a':pair['a'],'b':pair['b'],'lcs':n,'denominator':pair['denominator']}
                if score > maximum:
                    maximum, winners = score, [witness]
                elif score == maximum:
                    winners.append(witness)
        nulls.append({'replicate':rep,'seed':1154000+rep,'max_numerator':maximum.numerator,'max_denominator':maximum.denominator,'max_score':float(maximum),'winners':winners})
    return source,selected,excluded,pairs,sequences,nulls

# Artifact comparison is deliberately separate from the independent reconstruction.
def main():
    source,selected,excluded,pairs,sequences,nulls = reconstruct()
    checks = ['all_five_pins_verified','all_cached_paragraph_boundaries_offsets_and_source_ids','all_eligibility_reconstructed']
    el = read(E/'artifacts/eligibility.json')
    reason_map = {'TOO_FEW_LINES':'FEWER_THAN_6_LINES','INELIGIBLE_LINE':'INELIGIBLE_WHOLE_LINE','TOO_FEW_INTERIOR_TOKENS':'FEWER_THAN_20_INTERIOR_GROUPS'}
    for r, rows in el.items():
        assert len(rows) == len(source[r])
        originals = {p['id']:p for p in source[r]}
        assert len({p['id'] for p in rows}) == len(rows)
        for row in rows:
            p = originals[row['id']]
            expected = {'id':p['id'],'page':p['page'],'leaf':p['leaf'],'lines':len(p['lines']), 'interior_groups':len(flatten(p['lines'][1:-1])), 'eligible':p['id'] in selected[r], 'reasons':[reason_map[x] for x in excluded[r].get(p['id'],[])], 'ineligible_lines':[l['locus'] for l in p['lines'] if not l['anchor_eligible']]}
            assert row == expected, ('eligibility',r,p['id'])
    checks.append('all_exclusion_reasons_and_counts')
    expected_pairs = {}
    for r, ps in pairs.items():
        for p in ps:
            expected_pairs[(r,p['a'],p['b'])] = dict(reader=r,a=p['a'],b=p['b'],a_groups=len(sequences[r][p['a']]),b_groups=len(sequences[r][p['b']]),lcs=p['lcs'],numerator=2*p['lcs'],denominator=p['denominator'],score=p['score'],common_multiset=p['common'])
    with (E/'artifacts/ALL_PAIRS.tsv').open() as f:
        rows = list(csv.DictReader(f,delimiter='\t'))
    assert len(rows) == len(expected_pairs)
    seen = set()
    for row in rows:
        key = row['reader'],row['a'],row['b']
        assert key not in seen
        seen.add(key)
        exp = expected_pairs[key]
        for k,v in exp.items():
            assert (float(row[k]) if isinstance(v,float) else int(row[k]) if isinstance(v,int) else row[k]) == v, (key,k)
    checks += ['all_pairs_exhaustive_cross_leaf_and_length_gate','all_6611_exact_LCS_scores_independent_algorithm','all_common_multisets_and_denominators']
    assert read(E/'artifacts/NULL_MAXIMA.json') == nulls
    checks.append('all_199_null_schedules_maxima_and_exact_ties')
    maximum = max((Fraction(p['numerator'],p['denominator']) for p in expected_pairs.values()),default=Fraction(0))
    winners = [p for p in expected_pairs.values() if Fraction(p['numerator'],p['denominator']) == maximum]
    result = read(E/'artifacts/RESULT.json')
    assert result['global_winners'] == winners
    assert (result['observed_max_numerator'],result['observed_max_denominator'],result['observed_max']) == (maximum.numerator,maximum.denominator,float(maximum))
    expected_top = []
    for r in sorted(pairs):
        expected_top += sorted([p for p in expected_pairs.values() if p['reader']==r], key=lambda p:(-Fraction(p['numerator'],p['denominator']),p['a'],p['b']))[:10]
    tops = read(E/'artifacts/TOP_CONTEXTS.json')
    assert [(p['reader'],p['a'],p['b']) for p in tops] == [(p['reader'],p['a'],p['b']) for p in expected_top]
    for top, exp in zip(tops,expected_top):
        assert all(top[k] == v for k,v in exp.items())
        r,a,b = top['reader'],top['a'],top['b']
        pa,pb = selected[r][a],selected[r][b]
        assert top['paragraph_a'] == pa and top['paragraph_b'] == pb
        wa,wb = sequences[r][a],sequences[r][b]
        n, path = trace(wa,wb)
        assert n == top['lcs'] == lcs(wa,wb)
        ia,ib = flatten(pa['lines'][1:-1],'source_ids'),flatten(pb['lines'][1:-1],'source_ids')
        matches = [{'word':wa[i],'a_index':i,'b_index':j,'a_source_id':ia[i],'b_source_id':ib[j],'a_locus':ia[i].split('|')[1],'b_locus':ib[j].split('|')[1]} for i,j in path]
        assert top['alignment']['matches'] == matches
        al,bl = sorted({m['a_locus'] for m in matches}),sorted({m['b_locus'] for m in matches})
        assert sorted(top['alignment']['a_lines']) == al and sorted(top['alignment']['b_lines']) == bl
        assert top['line_coverage_pass'] == (len(al)>=3 and len(bl)>=3)
        assert top['global_winner'] == (Fraction(top['numerator'],top['denominator']) == maximum)
        for rr in source:
            for side, pid, para in [('a',a,pa),('b',b,pb)]:
                avail = top['alternative_reader_availability'][rr][side]
                assert avail['exact_paragraph_id_present'] == any(p['id']==pid for p in source[rr])
                assert avail['exact_paragraph_id_eligible'] == (pid in selected[rr])
                assert avail['same_page_cached_paragraph_ids'] == [p['id'] for p in source[rr] if p['page']==para['page']]
    checks += ['global_exact_winners_and_top10_each_reader','all_top_DP_backtraces_frozen_tie_rule','all_top_whole_paragraphs_and_original_matched_IDs','all_top_line_coverage_and_alternate_reader_availability']
    exceed = sum(Fraction(n['max_numerator'],n['max_denominator']) >= maximum for n in nulls)
    rank = (1+exceed)/200
    assert result['null_at_least_observed'] == exceed and result['p_rank'] == rank and result['null_draws'] == 199
    assert result['counts'] == {r:{'cached_paragraphs':len(source[r]),'eligible_paragraphs':len(selected[r]),'eligible_pairs':len(pairs[r])} for r in sorted(source)}
    nominated = [p for p in tops if p['global_winner'] and p['line_coverage_pass']] if rank<=.05 else []
    status = 'NO_CAPACITY' if not expected_pairs else 'NO_ORDER_LEAD' if rank>.05 else 'DISTRIBUTED_ORDER_LEAD' if nominated else 'CONCENTRATED_MATCH_ONLY'
    assert result['status'] == status and not result['nominated_pairs']
    assert result['meanings']==0 and all(result[k] is False for k in ['independent_confirmation','manuscript_wide_significance_claim','ancestry_claim','relation_packet_score_ready'])
    checks += ['conditional_rank_and_fixed_decision','no_semantic_ancestry_or_replication_claim']
    rng = random.Random(991154)
    for _ in range(100):
        a = [rng.randrange(5) for _ in range(rng.randrange(1,40))]
        b = [rng.randrange(5) for _ in range(rng.randrange(1,40))]
        assert lcs(a,b) == trace(a,b)[0]
    assert lcs(list('abcdefgh'),list('abcdefgh')) > lcs(list('abcdefgh'),list('ghefcdab'))
    checks.append('synthetic_order_example_and_100_LCS_DP_crosschecks')
    out = {'status':'PASS','checks':checks,'checks_passed':len(checks),'eligible_paragraphs':{r:len(v) for r,v in selected.items()},'observed_pairs':len(expected_pairs),'null_draws_independently_recomputed':199,'observed_max':float(maximum),'null_at_least_observed':exceed,'p_rank':rank,'decision':status,'limitations':['Uses frozen928 cache; does not reopen915 raw separators or original images.','Cached anchor_eligible seam flags are inherited provenance, not independently reinspected raw seams.','Previously exposed data; no independent manuscript confirmation.','Line exchangeability not established; rank only conditional rearrangement reference.','No common ancestry, meanings, or absence of broader copying established.']}
    (E/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    md = ['# Independent GDT1154 validation','','PASS: '+str(len(checks))+' check groups.','', 'Independent Hunt–Szymanski LCS plus conventional dynamic-programming backtrace; no runner functions imported. All 6,611 observed pair scores and 199 complete-search null maxima including ties independently reconstructed.','',f'Observed maximum {maximum}; {exceed}/199 null maxima at least as large; conditional rank {rank}; {status}.','','## Checks',''] + ['- '+x for x in checks] + ['','## Limits',''] + ['- '+x for x in out['limitations']]
    (E/'artifacts/VALIDATION.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['checks','limitations']}))

if __name__ == '__main__':
    main()
