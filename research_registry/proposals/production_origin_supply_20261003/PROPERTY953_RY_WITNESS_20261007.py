"""Replay one exposed literal-carrier check; no native semantic assignment."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

BASE = Path('research_registry/proposals/production_origin_supply_20261003')
CONTRACT = BASE / 'HUMAN_PROPERTY953_PHYSICAL_CONTRACT_20261006.json'
SOURCE = Path('experiments/semantic_assumptions/results/source_separator_transcription.tsv')
COLUMNS = 'edition,locus,source_group_id,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator'
cmd = ['./vmanus-exp', 'query-tsv', str(SOURCE), '--selector', 'locus', '--allow', 'f66r.57', '--columns', COLUMNS]
proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
rows = list(csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'))
contract = json.loads(CONTRACT.read_text())
tails = {tuple(t) for t in contract['word_grammar']['complete_suffix_tails']}
units = contract['physical_alphabet']['units']

def tokenize(s):
    answer = []
    while s:
        hits = [u for u in units if s.startswith(u)]
        if not hits:
            return None
        u = max(hits, key=len)
        answer.append(u)
        s = s[len(u):]
    return answer

def marker_positions(u):
    return [i for i in range(len(u)-1) if u[i:i+2] == ['r','y']]

def root_ok(u):
    return bool(u) and not marker_positions(u)

def predicate_ok(u):
    if u[:3] == ['r','y','p']:
        u = u[3:]
    pos = marker_positions(u)
    if not pos:
        return root_ok(u)
    return len(pos) == 1 and root_ok(u[:pos[0]]) and tuple(u[pos[0]+2:]) in tails

zl = [r for r in rows if r['edition'] == 'ZL3b']
target = next(r for r in zl if r['source_group_id'] == 'ZL3b|f66r.57|G007')
i = zl.index(target)
u = tokenize(target['ivtff_group_raw'])
assert u == list('dairykodas')
prev, nxt = zl[i-1]['ivtff_group_raw'], zl[i+1]['ivtff_group_raw']
checks = {
    'ordinary_root_legal': root_ok(u),
    'predicate_shape_legal': predicate_ok(u),
    'is_name_control': u in [['r','y','r'], ['r','y','l']],
    'has_required_name_payload_flanks': prev == 'ryr' and nxt == 'ryl',
    'is_physical_edge_group': int(target['source_group_index']) in [1,int(target['source_group_count'])],
}
assert not any(checks.values())
assert target['left_separator'] == target['right_separator'] == 'DEFINITE_SPACE'
# Independent finite membership construction from the contract for this target:
# Enumerate every possible nonempty root slice after optional past prefix and
# compare complete strings to roots + each complete suffix. No learned lexicon
# restriction is imposed: this is deliberately an overgenerous shape check.
whole = target['ivtff_group_raw']
possible = []
for prefix in ['', 'ryp']:
    for a in range(len(whole)):
        for b in range(a+1,len(whole)+1):
            root = whole[a:b]
            if 'ry' in root:
                continue
            for tail in ['', *['ry'+''.join(t) for t in tails]]:
                if prefix+root+tail == whole:
                    possible.append([prefix,root,tail])
assert not possible
# Positive nearby forms show why the split reading is not the same witness.
assert root_ok(tokenize('dair')) and root_ok(tokenize('ykodas'))
assert predicate_ok(tokenize('fktrye')) and predicate_ok(tokenize('rypfktryaon'))
assert not predicate_ok(tokenize('fktrya'))
result = {
 'status':'LITERAL_953_CARRIER_CONTRADICTION_CONDITIONAL_ON_ZL_WHOLE_GROUP',
 'selection':'Exposed exploratory witness selected after word-profile inspection; no independence or preregistered-discovery claim.',
 'contract':str(CONTRACT), 'contract_sha256':hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
 'source':str(SOURCE), 'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'guard_command':cmd, 'guard_stats':proc.stderr.strip(), 'selected_rows':len(rows),
 'witness_rows':rows, 'target_working_units':u, 'literal_checks':checks,
 'independent_shape_enumeration':possible,
 'manual_reason':'The ry at positions4-5 requires the complete suffix kodas, which is not one of the nine legal tails. The root cannot contain ry. Neither quote control matches; the required immediate opener/closer are absent. The interior group cannot be a margin continuation fragment. Sentence-gap placement cannot change these lexical facts.',
 'reader_limits':{'ZL3b':'One exact whole occurrence, internal with definite flanking spaces.','IT2a':'dair | ykodas; each independently satisfies the open root-shape condition, not a whole-line semantic success.','RF1b':'@152;air ~ ykodar; entity and uncertain separator preserved, not normalized or pooled.'},
 'scope':['Only the unchanged literal953marker realization with these transcription units and boundaries.','No global renaming, general property-language or semantic morphology exclusion.','No image adjudication or measured gap geometry; the disputed inner boundary remains unresolved.','Legal root shapes do not supply learned meanings, grammatical roles or a full reading.','Earlier953teaching readback and triple seam obligation remain unchanged.','No new meanings, source corpus, scored relation packet, reserve or sealed data.'],
 'decision':'Do not apply the unchanged literal953carrier as an exact whole-group reading of this ZLwitness. Retain IT/RF uncertainty and semantic lesson; no marker repair or image expansion selected.',
 'validation':'Same-author finite lexical enumeration agrees with direct parser and manual branch accounting; checks establish implementation consistency only.'
}
out=BASE/'PROPERTY953_RY_WITNESS_RESULT_20261007.json'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'selected_rows':len(rows),'checks':checks,'output':str(out)}))
