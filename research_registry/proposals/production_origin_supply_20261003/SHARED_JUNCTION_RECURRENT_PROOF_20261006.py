"""Post-result recurrent support for the unchanged shared-junction failure.

Fixed eleven whole forms; no key enumeration or model repair.
"""
from pathlib import Path
from datetime import datetime, timezone
import gzip, hashlib, json, re

P = Path('research_registry/proposals/production_origin_supply_20261003')
source = Path('experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')
source_hash = 'ccbf478614fea62c992812c91cb2fd206c43384ea0062f80ec772566287222a4'
assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
groups = json.loads(gzip.decompress(source.read_bytes()))
forms = ['d','l','o','r','s','y','daiin','qokeedy','chor','shy','otchey']
seed_simple = {'d','l','o','r','s','y'}
steps = [
    ('repeated_sign','i','daiin',2),
    ('repeated_sign','e','qokeedy',3),
    ('isolated_sign','a','daiin',1),
    ('isolated_sign','n','daiin',4),
    ('isolated_sign','q','qokeedy',0),
    ('isolated_sign','k','qokeedy',2),
    ('isolated_sign','ch','chor',0),
    ('isolated_sign','sh','shy',0),
    ('isolated_sign','t','otchey',1),
]
results = {}
for reader, rows in sorted(groups.items()):
    selected = {form:[r for r in rows if r['ivtff_group_raw'] == form] for form in forms}
    inventories = {}
    for form, hits in selected.items():
        assert hits, (reader,form)
        units = hits[0]['units']
        witnesses = {}
        for row in hits:
            assert row['units'] == units
            assert ''.join(units) == form
            assert row['left_separator'] == row['right_separator'] == 'DEFINITE_SPACE'
            leaf = re.fullmatch(r'(f\d+)[rv]\d*', row['page']).group(1)
            witnesses.setdefault(leaf,row)
        inventories[form] = {'units':units,'tokens':len(hits),
            'selectors':sorted({r['page'] for r in hits}),
            'physical_leaves':sorted(witnesses),
            'witnesses_on_two_leaves':[witnesses[k] for k in sorted(witnesses)[:2]]}
    forced = set(seed_simple)
    for g in forced:
        assert inventories[g]['units'] == [g]
    certificate = []
    for rule, target, form, offset in steps:
        units = inventories[form]['units']
        assert target not in forced
        assert units[offset] == target
        if rule == 'repeated_sign':
            assert units[offset+1] == target
        else:
            assert offset == 0 or units[offset-1] in forced
            assert offset == len(units)-1 or units[offset+1] in forced
        certificate.append({'rule':rule,'target':target,'whole_form':form,
            'offset':offset,'known_simple_before':sorted(forced)})
        forced.add(target)
    assert forced == {'d','l','o','r','s','y','i','e','a','n','q','k','ch','sh','t'}
    min_tokens = min(z['tokens'] for z in inventories.values())
    min_leaves = min(len(z['physical_leaves']) for z in inventories.values())
    results[reader] = {'support':inventories,'initial_simple':sorted(seed_simple),
        'certificate':certificate,'forced_simple':sorted(forced),'bound':len(forced),
        'minimum_whole_form_tokens':min_tokens,'minimum_physical_leaves':min_leaves,
        'decision':'RECURRENT_15_SIMPLE_SIGN_CONTRADICTION' if min_leaves >= 2 else 'RECURRENT_SUPPORT_INSUFFICIENT'}

result = {
    'status':'RECURRENT_SHARED_JUNCTION_CONTRADICTION_ALL_READINGS' if all(r['decision']=='RECURRENT_15_SIMPLE_SIGN_CONTRADICTION' for r in results.values()) else 'RECURRENT_SUPPORT_NOT_COMPLETE_ALL_READINGS',
    'created_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'Post-result fixed eleven-form necessary consequence and support check. No new manuscript access, native key or full enumeration.',
    'source':{'path':str(source),'sha256':source_hash},
    'checker':{'path':str(P/Path(__file__).name),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
    'frozen_candidate':{'path':str(P/'HUMAN_SHARED_JUNCTION_READER_RULES_20261006.json'),'sha256':hashlib.sha256((P/'HUMAN_SHARED_JUNCTION_READER_RULES_20261006.json').read_bytes()).hexdigest()},
    'universal_repeat_lemma':[
        'H cannot end a non-simple block, so HH cannot occur. T cannot begin a block, so TT cannot occur.',
        'The only potential MM boundary is between an HM letter and an MT letter. If the M signs are equal, the frozen mandatory contraction writes one M. If different, they are not an equal adjacent pair.',
        'Within HM, MT and HMT every adjacent pair has different disjoint roles. S is disjoint from those roles.',
        'Consequently any immediately repeated identical working sign must be S in canonical output, including repeated i in daiin and repeated e in qokeedy.'
    ],
    'isolation_lemma':'Every non-S run is assembled from blocks of at least two signs. A single sign delimited by S signs or complete group boundaries must itself be S.',
    'results':results,
    'decision':'The unchanged14-S construction fails using recurring whole forms, provided the fixed whole-group and working-unit readings hold. This strengthens support for the existing failure; it does not alter the prior hand-readback positive or select an enlarged table.',
    'limits':[
        'Physical leaves are f-number stems; foldout panels and sides of one leaf are not counted as independent leaves.',
        'These are alternate readings of the same exposed manuscript, not independent confirmations.',
        'Support is for the fixed whole-form obligations. Repeated occurrence does not prove the working-unit segmentation, whole-word equivalence, exact historical rule, or meaning.',
        'The eleven forms were selected after existing outcomes for a specific proof. No p-value, general rarity threshold, key search or unseen prediction is claimed.',
        'okeeaiin is a raw hapax in every reading and is not included in the recurrent proof. Its earlier mention as a possible frequent witness was corrected after profiling.',
        'The earlier15-S proof with rare witnesses stays frozen; this is a separate support-strengthening consequence.'
    ]
}
out = P/'SHARED_JUNCTION_RECURRENT_PROOF_RESULT_20261006.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'readers':{r:{k:v[k] for k in ['bound','minimum_whole_form_tokens','minimum_physical_leaves']} for r,v in results.items()},'output':str(out)}))
