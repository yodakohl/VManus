#!/usr/bin/env python3
"""Independent GDT905 channel, pattern-mask and candidate validator.
No import from the GDT905 search or GDT892 channel/grammar implementation.
"""
import argparse
import collections
import csv
import gzip
import io
import hashlib
import itertools
import json
from pathlib import Path
import pickle
import re
import time
import numpy as np

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
OLD = ROOT/'experiments/yolo/gdt892_joint_abugida_paradigm_reconstruction'
CACHE = None
VOWELS = 'aeiouy'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signature(sequence):
    # Pairwise first-index representation is independent from insertion IDs.
    sequence = list(sequence)
    first = [sequence.index(x) for x in sequence]
    indices = {p:i for i,p in enumerate(sorted(set(first)))}
    return tuple(indices[p] for p in first)


def components(word, inherent):
    assert inherent in VOWELS and re.fullmatch('[a-z]+',word)
    units = re.findall(r'[^aeiouy][aeiouy]?|[aeiouy]',word)
    assert ''.join(units) == word
    out = []
    for unit in units:
        if unit[0] in VOWELS:
            out.append('CARRIER')
            vowel = unit[0]
        else:
            out.append('C:'+unit[0])
            if len(unit)==1:
                out.append('VIRAMA')
                continue
            vowel = unit[1]
        if vowel != inherent:
            out.append('V:'+vowel)
    return tuple(out)


def split_word(word, singletons):
    pieces = []
    cursor = 0
    while cursor < len(word):
        stop = cursor + (1 if word[cursor] in singletons else 2)
        if stop > len(word):
            return None
        pieces.append(word[cursor:stop])
        cursor = stop
    return tuple(pieces)


def code_capacity(singletons, alphabet, used):
    singles, used = set(singletons), set(used)
    if not singles <= set(alphabet):
        return False
    possible = len(singles) + (len(alphabet)-len(singles))*len(alphabet)
    mandatory = len(singles) + len({x for x in used if len(x)==2})
    return possible >= 27 and mandatory <= 27 and len(used) <= 27


def pattern_masks(words, alphabet, allowed_patterns):
    """Intersect local truth tables lifted to every global singleton mask.
    This enumerates every mask, not a sample or only reported survivors.
    Capacity completion is checked separately on each survivor.
    """
    assert len(set(alphabet)) == len(alphabet)
    full = np.arange(1 << len(alphabet),dtype=np.uint32)
    admitted = np.ones(len(full),dtype=bool)
    lookup_cache = {}
    for word in dict.fromkeys(words):
        letters = sorted(set(word))
        assert set(letters) <= set(alphabet)
        local = np.zeros(1 << len(letters),dtype=bool)
        for mask in range(len(local)):
            pieces = split_word(word,{c for j,c in enumerate(letters) if mask & (1 << j)})
            if pieces is not None and signature(pieces) in allowed_patterns:
                local[mask] = True
        compact = np.zeros(len(full),dtype=np.uint32)
        for j,c in enumerate(letters):
            compact |= ((full >> alphabet.index(c)) & 1) << j
        admitted &= local[compact]
        if not admitted.any():
            break
    survivors = []
    for mask in full[admitted].tolist():
        singles = {c for j,c in enumerate(alphabet) if mask & (1 << j)}
        units = [split_word(word,singles) for word in words]
        assert all(x is not None for x in units)
        if code_capacity(singles,alphabet,itertools.chain.from_iterable(units)):
            survivors.append(mask)
    return survivors


def exhaustive_mask_bits(words, alphabet, signature_bits):
    if any(c not in alphabet for w in words for c in w):
        return {}
    doubles = sorted({w[j:j+2] for w in words for j in range(len(w)-1)})
    pair_index = {p:i for i,p in enumerate(doubles)}
    blocks = max(1,(len(doubles)+63)//64)
    prepared = []
    for word in dict.fromkeys(words):
        letters = sorted(set(word))
        bits = np.zeros(1 << len(letters),dtype=np.uint8)
        used = np.zeros((blocks,len(bits)),dtype=np.uint64)
        for m in range(len(bits)):
            parts = split_word(word,{c for j,c in enumerate(letters) if m & (1 << j)})
            if parts is None:
                continue
            bits[m] = signature_bits.get(signature(parts),0)
            if not bits[m]:
                continue
            for pair in {x for x in parts if len(x)==2}:
                k = pair_index[pair]
                used[k//64,m] |= np.uint64(1) << np.uint64(k%64)
        prepared.append((np.count_nonzero(bits)/len(bits),word,letters,bits,used))
    full = np.arange(1 << len(alphabet),dtype=np.uint32)
    admitted = np.full(len(full),63,dtype=np.uint8)
    union = np.zeros((blocks,len(full)),dtype=np.uint64)
    for _,word,letters,bits,used in sorted(prepared,key=lambda x:(x[0],x[1])):
        compact = np.zeros(len(full),dtype=np.uint32)
        for j,c in enumerate(letters):
            compact |= ((full >> alphabet.index(c)) & 1) << j
        admitted &= bits[compact]
        union |= used[:,compact]
        keep = admitted != 0
        full, admitted, union = full[keep], admitted[keep], union[:,keep]
        if not len(full):
            return {}
    pop = np.array([i.bit_count() for i in range(256)],dtype=np.uint8)
    singles = pop[full.view(np.uint8).reshape(len(full),4)].sum(axis=1)
    counts = pop[np.ascontiguousarray(union).view(np.uint8).reshape(blocks,len(full),8)].sum(axis=(0,2))
    capacity = (singles+len(alphabet)*(len(alphabet)-singles)>=27) & (singles+counts<=27)
    return dict(zip(full[capacity].tolist(),admitted[capacity].tolist()))


def grammar_accepts(grammar, analyses):
    """Independent bottom-up CFG span closure, with no Earley chart imports.
    Rules are epsilon-free and every dependency production contains a terminal.
    Unary nonterminal closure is handled to a fixed point at each span length.
    """
    tag_ids = {tuple(tag):i for i,tag in enumerate(grammar['tags'])}
    terminals = [{tag_ids[tuple(t)] for t in aa if tuple(t) in tag_ids} for aa in analyses]
    n = len(terminals)
    if not n or any(not x for x in terminals):
        return False
    chart = collections.defaultdict(set)
    rules = grammar['productions']
    for width in range(1,n+1):
        for begin in range(n-width+1):
            end = begin+width
            changed = True
            while changed:
                changed = False
                for rule in rules:
                    lhs = rule['lhs']
                    if lhs in chart[begin,end]:
                        continue
                    positions = {begin}
                    for kind, symbol in rule['rhs']:
                        nxt = set()
                        if kind == 'T':
                            nxt = {p+1 for p in positions if p < end and symbol in terminals[p]}
                        else:
                            for p in positions:
                                nxt.update(q for q in range(p+1,end+1) if symbol in chart[p,q])
                        positions = nxt
                        if not positions:
                            break
                    if end in positions:
                        chart[begin,end].add(lhs)
                        changed = True
    return grammar['start'] in chart[0,n]


def check_candidate(words, plaintext, unit_to_component, singletons, inherent, alphabet, reference, expected_grammar=True):
    assert len(words) == len(plaintext) and inherent in VOWELS
    codes = set(unit_to_component)
    assert len(set(unit_to_component.values())) == len(codes)
    inventory = {'C:'+c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in VOWELS}
    inventory |= {'V:'+v for v in VOWELS if v != inherent} | {'CARRIER','VIRAMA'}
    assert set(unit_to_component.values()) <= inventory
    for code in codes:
        assert len(code) in (1,2) and set(code) <= set(alphabet)
        assert (len(code)==1) == (code[0] in set(singletons))
    used = set()
    for ciphertext, plain in zip(words,plaintext):
        pieces = split_word(ciphertext,set(singletons))
        assert pieces is not None and set(pieces) <= codes
        used.update(pieces)
        assert tuple(unit_to_component[x] for x in pieces) == components(plain,inherent)
        assert plain in reference['analyses']
    assert code_capacity(singletons,alphabet,used)
    accepted = grammar_accepts(reference['grammar'],[reference['analyses'][p] for p in plaintext])
    assert accepted == expected_grammar
    return {'words':len(words),'used_component_codes':len(used),'exact_reencoding':True,'dictionary':True,'independent_CFG_accepted':accepted}


def load_reference():
    meta = json.loads((OLD/'artifacts/REFERENCE.json').read_text())
    path = CACHE/'reference.pkl'
    assert sha(path) == meta['cache_files']['reference.pkl']['sha256']
    with path.open('rb') as stream:
        reference = pickle.load(stream)
    assert len(reference['forms']) == 425561
    return reference, meta


def validate_pattern_index(reference, meta, vowel):
    path = CACHE/('patterns_'+vowel+'.pkl')
    assert sha(path) == meta['cache_files'][path.name]['sha256']
    with path.open('rb') as stream:
        index = pickle.load(stream)
    seen = set()
    for pat, rows in index.items():
        for form_id, values in rows:
            assert form_id not in seen
            seen.add(form_id)
            expected = components(reference['forms'][form_id],vowel)
            assert tuple(values) == expected and tuple(pat) == signature(expected)
    assert seen == set(range(len(reference['forms'])))
    return index


def invented_checks():
    assert components('rosa','a') == ('C:r','V:o','C:s')
    assert components('est','a') == ('CARRIER','V:e','C:s','VIRAMA','C:t','VIRAMA')
    assert components('a','a') == ('CARRIER',)
    assert split_word('abc',{'a'}) == ('a','bc')
    assert split_word('abc',{'b'}) is None
    assert signature(['x','y','x']) == (0,1,0)
    assert not code_capacity({'a','b'},'ab',('a','b'))
    # Independent complete-code enumeration on a tiny alphabet checks the
    # parameterized arithmetic behind the27component completion condition.
    for width in range(1,4):
        alphabet = 'abc'[:width]
        for singlemask in range(1 << width):
            singles = {c for i,c in enumerate(alphabet) if singlemask & (1 << i)}
            available = singles | {a+b for a in alphabet if a not in singles for b in alphabet}
            assert len(available) == len(singles)+width*(width-len(singles))
    alphabet = 'abcdef'
    allowed = {(0,), (0,1), (0,1,0), (0,1,2), (0,1,2,1)}
    cases = [('ab',),('aba','bcb'),('abcabc','abcdef'),('f','ab','cd'),('abcdefabcdef',)]
    for words in cases:
        expected = []
        for mask in range(64):
            singles = {c for i,c in enumerate(alphabet) if mask & (1 << i)}
            parts = [split_word(w,singles) for w in words]
            if any(p is None or signature(p) not in allowed for p in parts):
                continue
            if code_capacity(singles,alphabet,itertools.chain.from_iterable(parts)):
                expected.append(mask)
        assert pattern_masks(words,alphabet,allowed) == expected
        combined = exhaustive_mask_bits(words,alphabet,{p:1 for p in allowed})
        assert combined == {m:1 for m in expected}
    noun = ('NOUN','Nom','Sing','_','_','_')
    verb = ('VERB','_','Sing','3','Fin','Ind')
    grammar = {'tags':[noun,verb], 'start':2, 'productions':[
        {'lhs':0,'rhs':[['T',0]]},
        {'lhs':1,'rhs':[['T',1]]},
        {'lhs':2,'rhs':[['N',0],['N',1]]},
        {'lhs':2,'rhs':[['N',0],['N',1],['N',2]]}]}
    assert grammar_accepts(grammar,[[noun],[verb]])
    assert grammar_accepts(grammar,[[noun],[verb],[noun],[verb]])
    assert grammar_accepts(grammar,[[noun,verb],[verb]])
    assert not grammar_accepts(grammar,[[verb],[noun]])
    assert not grammar_accepts(grammar,[[noun]])
    assert not grammar_accepts(grammar,[])
    return {'channel_fixed_examples':6,'capacity_alphabets':3,'mask_lifting_toys':5,'CFG_examples':6}



def rejected_explanation_checks(reference, selected, output):
    path = EXP/'artifacts/LEXICAL_KEY_EXPLANATION.json'
    if not path.exists():
        return
    if output.get('lexical_key_explanation_sha256') == sha(path):
        return
    explanation = json.loads(path.read_text())
    checks = []
    alphabet = 'acdefghiklmnopqrstxy'
    for record in explanation['records']:
        row = selected[record['edition'],record['paragraph_id']]
        assert row['words'] == record['written_groups'] and row['loci'] == record['loci']
        for key in record['keys']:
            assert key['grammar_accepted'] is False
            singles = {c for j,c in enumerate(alphabet) if key['mask'] & (1 << j)}
            detail = check_candidate(row['words'],key['plaintext'],key['observed_key'],singles,key['inherent'],alphabet,reference,expected_grammar=False)
            inventory = {'C:'+c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in VOWELS} | {'V:'+v for v in VOWELS if v!=key['inherent']} | {'CARRIER','VIRAMA'}
            complete = key['complete_key']
            assert set(complete) == inventory and len(set(complete.values())) == 27
            for component,code in complete.items():
                assert len(code) in (1,2) and set(code) <= set(alphabet)
                assert (len(code)==1) == (code[0] in singles)
            assert {code:component for component,code in complete.items() if code in key['observed_key']} == key['observed_key']
            assert key['analyses'] == [[list(tag) for tag in reference['analyses'][word]] for word in key['plaintext']]
            checks.append(dict(edition=record['edition'],paragraph_id=record['paragraph_id'],inherent=key['inherent'],mask=key['mask'],complete_codebook=True,all_analyses_exact=True,**detail))
    assert len(checks) == explanation['keys']
    output['lexical_key_explanation_sha256'] = sha(path)
    output['rejected_lexical_key_checks'] = checks
    output['rejected_key_scope'] = 'Independent code/dictionary/fullCFG check of explanatory keys only; primary deterministic search-count replay not independently reproduced here. These grammar-rejected keys are not accepted readings.'


def main():
    global CACHE
    parser = argparse.ArgumentParser()
    parser.add_argument('--cache-dir',type=Path,required=True)
    parser.add_argument('--candidates-only',action='store_true')
    args = parser.parse_args()
    CACHE = args.cache_dir
    tests = invented_checks()
    reference,meta = load_reference()
    target_path = EXP/'artifacts/TARGET.json'
    scans_path = EXP/'artifacts/SCANS.json'
    target = json.loads(target_path.read_text())
    scans = json.loads(scans_path.read_text())
    selected = {(edition,r['paragraph_id']):r for edition,rows in target['panels'].items() for r in rows if 12<=len(r['words'])<=24}
    assert len(scans) == len(selected) == 49
    assert {(r['edition'],r['paragraph_id']) for r in scans} == set(selected)
    alphabet = 'acdefghiklmnopqrstxy'
    report_path = EXP/'artifacts/INDEPENDENT_VALIDATION.json'
    if args.candidates_only:
        output = json.loads(report_path.read_text())
        assert output['target_sha256'] == sha(target_path) and output['scans_sha256'] == sha(scans_path)
    else:
        began = time.monotonic()
        pattern_bits = {}
        source_checks = []
        for bit,v in enumerate(VOWELS):
            index = validate_pattern_index(reference,meta,v)
            for pattern in index:
                pattern_bits[tuple(pattern)] = pattern_bits.get(tuple(pattern),0) | (1 << bit)
            source_checks.append({'inherent':v,'forms':len(reference['forms']),'patterns':len(index),'index_sha256':meta['cache_files']['patterns_'+v+'.pkl']['sha256']})
            print(json.dumps({'reference_inherent':v,'status':'PASS'}),flush=True)
        mask_checks = []
        for scan in scans:
            key = (scan['edition'],scan['paragraph_id'])
            row = selected[key]
            assert int(row['physical_folio'][1:]) % 2 == 1 and not row['page'].startswith('f84')
            assert len(row['words']) == len(row['loci']) == len(row['source_group_ids'])
            assert scan['status'] == 'COMPLETE' and scan['masks_examined'] == (1 << 20)
            expected = exhaustive_mask_bits(row['words'],alphabet,pattern_bits)
            path = EXP/scan['masks_path']
            assert sha(path) == scan['masks_sha256']
            raw = gzip.decompress(path.read_bytes())
            assert hashlib.sha256(raw).hexdigest() == scan['uncompressed_sha256']
            parsed = list(csv.DictReader(io.StringIO(raw.decode())))
            observed = {int(r['mask']):int(r['inherent_bits']) for r in parsed}
            assert len(observed) == len(parsed) == scan['surviving_masks']
            assert expected == observed, (key,len(expected),len(observed),list(set(expected)^set(observed))[:3])
            mask_checks.append({'edition':key[0],'paragraph_id':key[1],'all_masks':1 << 20,'surviving_masks':len(expected),'exact_vowel_bitsets_equal':True,'uncompressed_sha256':scan['uncompressed_sha256']})
            print(json.dumps({'mask_panel':key[0],'paragraph':key[1],'survivors':len(expected),'status':'PASS'}),flush=True)
        output = {'schema':'GDT905_INDEPENDENT_VALIDATION_V1','status':'MASK_VALIDATION_PASS_CANDIDATE_RESULTS_PENDING','target_sha256':sha(target_path),'scans_sha256':sha(scans_path),'reference_sha256':meta['cache_files']['reference.pkl']['sha256'],'source_checks':source_checks,'invented_checks':tests,'mask_checks':mask_checks,'mask_seconds':time.monotonic()-began,'mask_algorithm':'Independent per-word local truth tables lifted over all2^20 masks; six-vowel bit intersections; exact used-digram union and27component completion including unused singletons.'}
        report_path.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    candidates_path = EXP/'artifacts/CANDIDATES.json'
    final_result = EXP/'artifacts/RESULT.json'
    packed_candidates = candidates_path.with_suffix('.json.gz')
    if (not candidates_path.exists() and not packed_candidates.exists()) or not final_result.exists():
        print(json.dumps({'status':output['status'],'candidates_pending':True}))
        return
    candidate_bytes = candidates_path.read_bytes() if candidates_path.exists() else gzip.decompress(packed_candidates.read_bytes())
    candidates = json.loads(candidate_bytes)
    candidate_checks = []
    for record in candidates:
        key = (record['edition'],record['paragraph_id'])
        assert key in selected
        row = selected[key]
        for witness in record['witnesses']:
            mask = witness['mask']
            singles = {c for j,c in enumerate(alphabet) if mask & (1 << j)}
            result = check_candidate(row['words'],witness['plaintext'],witness['observed_key'],singles,witness['inherent'],alphabet,reference)
            complete = witness['complete_key']
            inventory = {'C:'+c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in VOWELS} | {'V:'+v for v in VOWELS if v!=witness['inherent']} | {'CARRIER','VIRAMA'}
            assert set(complete) == inventory and len(set(complete.values())) == 27
            for component,code in complete.items():
                assert len(code) in (1,2) and set(code) <= set(alphabet)
                assert (len(code)==1) == (code[0] in singles)
            assert {code:component for component,code in complete.items() if code in witness['observed_key']} == witness['observed_key']
            assert witness['analyses'] == [[list(tag) for tag in reference['analyses'][word]] for word in witness['plaintext']]
            candidate_checks.append(dict(edition=key[0],paragraph_id=key[1],inherent=witness['inherent'],mask=mask,**result))
    rejected_explanation_checks(reference,selected,output)
    output.update(status='PASS',validator_sha256=sha(Path(__file__)),candidates_sha256=hashlib.sha256(candidate_bytes).hexdigest(),result_sha256=sha(final_result),candidate_checks=candidate_checks,candidate_count=len(candidate_checks),claim_ceiling='All complete mask lists independently verified, and all reported candidate witnesses independently reencoded and grammar checked. Nonzero local masks do not establish a shared key. Unfinished searches remain unknown. No semantics or uniqueness certified.')
    report_path.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'PASS','candidate_witnesses':len(candidate_checks)}))


if __name__ == '__main__':
    main()
