"""Replay a hand readback and a small already-exposed necessary counterproof.

No native query, key search, parameter fitting or new corpus measurement.
This is a post-design evidence-binding check, not blinded confirmation.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

P = Path('research_registry/proposals/production_origin_supply_20261003')
FILES = {
    'rules': P / 'HUMAN_SHARED_JUNCTION_READER_RULES_20261006.json',
    'challenge': P / 'HUMAN_SHARED_JUNCTION_MANUAL_CHALLENGE_20261006.json',
    'expected': P / 'HUMAN_SHARED_JUNCTION_MANUAL_EXPECTED_20261006.json',
    'readback': P / 'HUMAN_SHARED_JUNCTION_ROOT_READBACK_20261006.json',
    'singletons': Path('experiments/yolo/gdt1227_relation_path_one_sign_capacity/artifacts/RESULT.json'),
    'examples': Path('experiments/yolo/gdt1234_prefix_quotient_code_capacity/artifacts/PROOF_EXAMPLES.json'),
    'q_example': Path('experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/FORCING_EXAMPLES.json'),
}
FIXED_HASHES = {
    'rules': '004333678565ea9ec70a66340a20dfd9854741e879943347cd1a3620a0632ed0',
    'challenge': '4305414a9700eebbbf224e34a04af6a617365a46ace8eef98dbf425afe81cb29',
    'expected': '4866efd165ccaa071f6398eae0a97332004bb89e4e28fdbc1f9ad6808da23099',
    'readback': 'dcf754bb70244eda936464e2fa6c7ab24b36b25657e7f9fe806a45e5047806d1',
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load(k):
    if k in FIXED_HASHES:
        assert sha(FILES[k]) == FIXED_HASHES[k], k
    return json.loads(FILES[k].read_text())

rules, challenge, expected, readback = (load(k) for k in ['rules','challenge','expected','readback'])
assert readback['source_readback'] == expected['source']
assert expected['continued_word']['word'] == 'bartholomew'
assert readback['manual_trace'][0]['readback_fragment'] == expected['continued_word']['first_row_decodes']
assert readback['manual_trace'][1]['readback'].split()[0] == expected['continued_word']['second_row_first_group_decodes']

# Independently interpret the reader's saved block trace. This is not a decoder
# which supplied the original manual answer; the answer was frozen first.
inverse = {tuple(v): k for k,v in rules['complete_source_letter_table'].items()}
assert len(inverse) == 26
roles = rules['physical_inventory']
S,H,M,T = (set(roles[k]) for k in ['simple_S','heads_H','middles_M','tails_T'])
assert [len(s) for s in [S,H,M,T]] == [14,2,2,4]
assert len(S|H|M|T) == 22

def read_block(block):
    b = tuple(block)
    if len(b) == 3:
        assert b[0] in H and b[1] in M and b[2] in T
        return inverse[b[:2]] + inverse[b[1:]]
    return inverse[b]

row_texts = []
row_cells = []
for row, trace in zip(challenge['rows'], readback['manual_trace']):
    if row is None:
        assert trace['readback'] == '.'
        row_texts.append('.')
        row_cells.append(0)
        continue
    blocks = trace.get('word_blocks', [trace.get('glyph_blocks')])
    assert blocks and blocks[0]
    visible = ' '.join(''.join(''.join(b) for b in word) for word in blocks)
    assert visible == row['body']
    decoded = ' '.join(''.join(read_block(b) for b in word) for word in blocks)
    assert decoded == trace.get('readback', trace.get('readback_fragment'))
    cells = sum(len(b) for word in blocks for b in word) + len(blocks)-1
    assert cells <= 12
    row_texts.append(decoded)
    row_cells.append(cells)
assert row_cells == expected['row_body_cells_including_written_word_gaps']
assert challenge['rows'][0]['gutter'] == 'a'
assert all(row['gutter'] == '' for row in challenge['rows'][1:] if row)

# A non-S component always belongs to an HM, MT or HMT block. Hence a lone
# non-S symbol delimited on each side by S or a group end is impossible.
# The following witnesses were already printed/exposed in earlier artifacts.
old = load('singletons')['readings']
examples = load('examples')['readers']
q_examples = load('q_example')['readings']
targets = {
    'IT2a': [('p','op'),('ckh','chckh'),('f','chtchyf')],
    'ZL3b': [('p','op'),('ckh','chckh'),('f','chof'),('t','lt'),('e','che')],
}
results = {}
for reader in ['IT2a','RF1b','ZL3b']:
    forced = set(old[reader]['counts'])
    initial = sorted(forced)
    steps = []
    planned = []
    if reader == 'RF1b':
        q_step = next(x for x in q_examples[reader] if x['head'] == 'q')
        witness = next(x for x in q_step['witnesses'] if x['word'] == 'qokain')
        assert witness['offset'] == 0
        planned.append(('q', {'units':witness['units'], 'display':witness['word'],
            'panel_count':witness['eligible_form_count'], 'pages':witness['eligible_form_pages'],
            'first_occurrence':{'id':witness['id']}}))
    else:
        for target, form in targets[reader]:
            proof = examples[reader]['forced_singletons'][target]
            seed = next(x for x in proof['steps'] if x['parents'] is None and x['display'] == form)
            assert seed['first_occurrence']['left_separator'] == 'DEFINITE_SPACE'
            assert seed['first_occurrence']['right_separator'] == 'DEFINITE_SPACE'
            planned.append((target,seed))
    for target, witness in planned:
        assert target not in forced
        units = witness['units']
        positions = [i for i,g in enumerate(units) if g == target
            and (i == 0 or units[i-1] in forced)
            and (i == len(units)-1 or units[i+1] in forced)]
        assert positions, (reader,target,units)
        steps.append({'new_forced_simple_sign':target,'known_simple_before':sorted(forced),
            'isolated_position':positions[0], 'witness':witness})
        forced.add(target)
    assert len(forced) == 15
    results[reader] = {'initial_simple_signs':initial,
        'initial_counts':old[reader]['counts'],
        'initial_first_witnesses':old[reader]['witnesses'],
        'steps':steps,'forced_simple_signs':sorted(forced),'bound':len(forced),
        'candidate_capacity':14,'decision':'EXCLUDED_UNDER_EVERY_GLOBAL_BIJECTION'}

result = {
    'status':'HAND_READBACK_PASS_AND_14_SIMPLE_SIGN_KERNEL_EXCLUDED_ALL_READINGS',
    'checked_utc':datetime.now(timezone.utc).isoformat(),
    'source_bindings':{k:{'path':str(p),'sha256':sha(p)} for k,p in FILES.items()},
    'checker':{'path':str(Path(__file__)) if not Path(__file__).is_absolute() else str(P/Path(__file__).name),
               'sha256':sha(Path(__file__))},
    'manual_lesson':{'frozen_answer_matches':True,'source':expected['source'],
        'row_body_cells':row_cells,'total_body_glyphs':55,'gutter_glyphs':1,
        'shared_source_pairs':['ou','ot'],
        'scope':'One source-held synthetic exercise; independent reader access, not independent human or native confirmation. The computer replay only checks the earlier manually written answer and trace.'},
    'necessary_proof':[
        'Each non-S source-letter code is HM or MT; permitted sharing makes HMT. Each resulting non-S block has at least two signs, and none contains an S sign.',
        'An S sign therefore cuts every non-S run. A whole singleton must be S. A single sign between S signs or group boundaries must also be S.',
        'The exact retained old witnesses force15 distinct S signs separately in each reading. The candidate provides14. A global bijection preserves these cardinalities.',
        'No old prefix-code quotient inference is transferred: only the original whole-form seeds and singleton witnesses are reused.'
    ],
    'results':results,
    'limits':[
        'The14-S,H2,M2,T4 partition and whole-group/22-working-unit conventions are assumed. This is not a proof of true atomic native signs.',
        'The witness set is selected from known exposed examples after considering the candidate, not a prospective random or blind native sample.',
        'Several initial singletons and short witnesses occur once. Exact transcription/segmentation error would affect this conditional proof; no image checking or error correction is claimed.',
        'All witnesses are ordinary complete interior prose groups; line-fragment/gutter rules cannot exempt them. Alternate readings are not independent manuscripts.',
        'No full native enumeration, source corpus encoding, statistical fit, table enlargement or word meaning was attempted.'
    ],
    'decision':'Preserve readable teaching contract; stop this14-S native reconstruction before an encoder or role-key search. No automatic new role partition.'
}
out = P/'SHARED_JUNCTION_HAND_VALIDATION_20261006.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'bounds':{r:z['bound'] for r,z in results.items()},'output':str(out)}))
