"""Independent GDT1033 validator. Never reads/imports the primary runner.
Self-test accesses only contracts, parent lexicon and synthetic fixtures.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
READERS = ('ZL3b', 'IT2a', 'RF1b')
N = frozenset(('sshey', 'sol', 'oltydy', 'or'))
FOOD = frozenset(('shedy','qokain','okedy','char','cheey','qokopy','dal','aiin'))
S = 'lshedy'

class Invalid(Exception):
    pass

def need(ok, message):
    if not ok:
        raise Invalid(message)

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def contracts():
    spec = read(EXP/'src/SPEC.json')
    for key in ('proposal','lexicon'):
        need(sha(ROOT/spec[key]['path']) == spec[key]['sha256'], key+' hash')
    proposal = read(ROOT/spec['proposal']['path'])
    parent = read(ROOT/spec['lexicon']['path'])
    entries = parent['frozen_parent_lexicon'] + parent['new_lexicon']
    lex = {e['form']:e for e in entries}
    need(len(lex) == len(entries) == 59, 'exact59')
    need(tuple(spec['readers']) == READERS and set(spec['N']) == N and spec['S'] == S, 'fixed trigger/readers')
    need(set(spec['food_forms']) == FOOD and spec['open_forms'] == ['olor'], '8/1 fixed sets')
    conflicts = set(lex)-FOOD-{'olor'}
    need(len(conflicts) == 50 and conflicts == set(spec['conflict_forms']), '50 fixed conflicts')
    writer = proposal['finite_writer']
    need(set(writer['exact_fixed_incompatible_forms']) == conflicts and set(writer['food_compatible_forms']) == FOOD, 'proposal agreement')
    need(set(writer['N']) == N and writer['S'] == S, 'proposal trigger')
    need(all(lex[n]['value'] == 'NOT' and lex[n]['type'] == 'proposition → negation' for n in N), 'NOT identity')
    need(lex[S]['value'] == 'SOLID_FOOD' and lex[S]['type'] == 'food → kind predicate', 'S identity')
    need(spec['exclude_leaves'] == [76,80] and spec['forbidden_exact'] == ['f116v'], 'scope fixed')
    return spec, lex

def classify_x(x, lex):
    if x in FOOD:
        return 'FOOD_TYPE_POSSIBLE'
    if x == 'olor':
        return 'OPEN_TYPE'
    return 'FIXED_TYPE_CONFLICT' if x in lex else 'UNKNOWN_WORD'

def frame(words, j):
    need(words[j] == S, 'not anchor')
    if j >= 2 and words[j-2] in N:
        return 'LONG', words[j-1]
    if j >= 1 and words[j-1] in N:
        return 'SHORT', None
    return 'OUTSIDE_CONTRACT', None

def reconstruct(packet, lex):
    need(set(packet) == set(READERS), 'reader keys')
    scope, events = [], []
    for reader in READERS:
        need(isinstance(packet[reader],list), 'paragraph list')
        seen, source_seen = set(), set()
        for p in sorted(packet[reader], key=lambda p:p['id']):
            page = p['page']
            need(isinstance(page,str) and not page.startswith('f84') and page != 'f116v', 'forbidden selector')
            m = re.fullmatch(r'f([0-9]+)[rv][0-9]*',page)
            need(m is not None, 'selector grammar')
            leaf = int(m.group(1))
            need(type(p['leaf']) is int and p['leaf'] == leaf, 'leaf mismatch')
            pid, lines = p['id'], p['lines']
            need(pid not in seen and pid.startswith(page+'|') and bool(lines), 'paragraph identity')
            seen.add(pid)
            need(pid == page+'|'+lines[0]['locus']+'-'+lines[-1]['locus'], 'boundary ID')
            need(type(p['groups']) is int and p['groups'] > 0, 'groups metadata')
            need(all(l['locus'].startswith(page+'.') for l in lines), 'line selector mismatch')
            scope.append(dict(reader=reader,paragraph=pid,page=page,leaf=leaf,groups=p['groups'],
                              lines=[dict(locus=l['locus'],anchor_eligible=l.get('anchor_eligible')) for l in lines],
                              category='EXCLUDED_DEVELOPMENT' if leaf in (76,80) else 'IN_SCOPE'))
            if leaf in (76,80):
                continue
            offset = 0
            for line in lines:
                words, ids = line['words'], line['source_ids']
                need(isinstance(words,list) and all(isinstance(w,str) for w in words), 'word list')
                need(len(words) == len(ids) and line['offset'] == offset, 'line offsets/IDs')
                literal = line.get('anchor_eligible') is True
                if literal:
                    need(all(re.fullmatch('[a-z]+',w) for w in words), 'literal nonalphabetic word')
                for j,(word,sid) in enumerate(zip(words,ids)):
                    need(sid == f"{reader}|{line['locus']}|G{j+1:03d}" and sid not in source_seen, 'source ID integrity')
                    source_seen.add(sid)
                    if word != S:
                        continue
                    shape,x = frame(words,j)
                    outcome = ('SOURCE_UNCERTAIN' if not literal else
                               classify_x(x,lex) if shape == 'LONG' else
                               'SHORT_CONTEXT_REQUIRED' if shape == 'SHORT' else 'OUTSIDE_CONTRACT')
                    events.append(dict(reader=reader,paragraph=pid,page=page,leaf=leaf,locus=line['locus'],
                                       line_position=j+1,position=line['offset']+j+1,source_id=sid,
                                       window_source_ids=ids[max(0,j-2):j+1],window_words=words[max(0,j-2):j+1],
                                       anchor_eligible=line.get('anchor_eligible'),frame=shape,X=x,outcome=outcome,
                                       parent_entry=lex.get(x) if shape == 'LONG' else None))
                offset += len(words)
            need(offset == p['groups'], 'whole paragraph count')
    return scope,events

def result_for(scope,events):
    readers = {}
    for reader in READERS:
        rows = [s for s in scope if s['reader'] == reader]
        ee = [e for e in events if e['reader'] == reader]
        primary = [e for e in ee if e['outcome'] != 'SOURCE_UNCERTAIN']
        long = [e for e in primary if e['frame'] == 'LONG']
        counts = dict(Counter(e['outcome'] for e in ee))
        status = ('NO_OWNED_PARAGRAPH_DATA' if not rows else
                  'REFUTED_FIXED_LOCAL_WRITER' if counts.get('FIXED_TYPE_CONFLICT',0) else
                  'CONDITIONAL_COMPATIBILITY_ONLY' if counts.get('FOOD_TYPE_POSSIBLE',0) else
                  'NO_TYPED_DISCRIMINATION' if long else 'NO_CAPACITY')
        dev = sum(s['category'] == 'EXCLUDED_DEVELOPMENT' for s in rows)
        readers[reader] = dict(paragraphs=len(rows),development_paragraphs=dev,scope_paragraphs=len(rows)-dev,
                               events=len(ee),primary_events=len(primary),source_uncertain_events=len(ee)-len(primary),
                               primary_long=len(long),primary_short=sum(e['frame']=='SHORT' for e in primary),
                               primary_outside=sum(e['frame']=='OUTSIDE_CONTRACT' for e in primary),
                               counts=counts,long_leaves=sorted({e['leaf'] for e in long}),status=status)
    statuses = {r['status'] for r in readers.values()}
    status = ('READING_SPECIFIC_COUNTEREXAMPLE' if 'REFUTED_FIXED_LOCAL_WRITER' in statuses else
              'CONDITIONAL_COMPATIBILITY_ONLY' if 'CONDITIONAL_COMPATIBILITY_ONLY' in statuses else
              'NO_TYPED_DISCRIMINATION' if 'NO_TYPED_DISCRIMINATION' in statuses else 'NO_CAPACITY')
    return dict(experiment='GDT1033',status=status,readers=readers,confirmed_words=0,
                independent_meaning_confirmation=0,significance_claim=False)

def fixture(lines,flags=None,page='f1r'):
    flags = [True]*len(lines) if flags is None else flags
    ls,offset = [],0
    for i,words in enumerate(lines,1):
        locus=f'{page}.{i}'
        ls.append(dict(locus=locus,offset=offset,words=words,source_ids=[f'ZL3b|{locus}|G{j+1:03d}' for j in range(len(words))],anchor_eligible=flags[i-1]))
        offset+=len(words)
    p=dict(page=page,leaf=int(re.search(r'\d+',page).group()),id=page+'|'+ls[0]['locus']+'-'+ls[-1]['locus'],groups=offset,lines=ls)
    return {'ZL3b':[p],'IT2a':[],'RF1b':[]}

def self_test(lex):
    checked=0
    for x in sorted(lex):
        expected='FOOD_TYPE_POSSIBLE' if x in FOOD else 'OPEN_TYPE' if x=='olor' else 'FIXED_TYPE_CONFLICT'
        for n in sorted(N):
            need(frame([n,x,S],2)==('LONG',x) and classify_x(x,lex)==expected,'59x4 direct')
            literal=bool(re.fullmatch('[a-z]+',x))
            _,ev=reconstruct(fixture([[n,x,S]],[literal]),lex)
            need(ev[-1]['outcome']==(expected if literal else 'SOURCE_UNCERTAIN'),'59x4 integrated')
            need(ev[-1]['parent_entry']==lex[x],'full parent preservation')
            checked+=1
    for n in N:
        _,ev=reconstruct(fixture([[n,S]]),lex)
        need(ev[-1]['outcome']=='SHORT_CONTEXT_REQUIRED','short4')
    _,ev=reconstruct(fixture([['or','unknownfixture',S]]),lex)
    need(ev[-1]['outcome']=='UNKNOWN_WORD','unknown')
    for flag in (False,None,1,0,'true'):
        p=fixture([['or','qoky',S]],[flag])
        if flag is None: del p['ZL3b'][0]['lines'][0]['anchor_eligible']
        _,ev=reconstruct(p,lex)
        need(ev[-1]['outcome']=='SOURCE_UNCERTAIN','true identity')
    for lines in ([['or','qoky'],[S]],[['or'],['shedy',S]]):
        _,ev=reconstruct(fixture(lines),lex)
        need(ev[-1]['outcome']=='OUTSIDE_CONTRACT','line seam')
    _,ev=reconstruct(fixture([['or','qoky',S],['uncertain']],[True,False]),lex)
    need(ev[0]['outcome']=='FIXED_TYPE_CONFLICT','other uncertain line')
    class Poison(dict):
        def __getitem__(self,k):
            if k in ('words','source_ids'): raise AssertionError('payload opened before guard')
            return super().__getitem__(k)
    for page in ('f76r','f76v','f80r','f80v','f84r','f84v','f84r1','f116v'):
        p=fixture([['or','qoky',S]],page=page)
        p['ZL3b'][0]['lines']=[Poison(l) for l in p['ZL3b'][0]['lines']]
        if page.startswith('f84') or page=='f116v':
            try: reconstruct(p,lex)
            except Invalid: pass
            else: raise Invalid('sealed not rejected')
        else:
            scope,ev=reconstruct(p,lex)
            need(scope[0]['category']=='EXCLUDED_DEVELOPMENT' and not ev,'development')
    p=fixture([['or','qoky',S]])
    p['ZL3b'][0]['leaf']=2
    p['ZL3b'][0]['lines']=[Poison(l) for l in p['ZL3b'][0]['lines']]
    try: reconstruct(p,lex)
    except Invalid: pass
    else: raise Invalid('leaf mismatch')
    for lines,wanted in [([[S]],'NO_CAPACITY'),([['or','olor',S]],'NO_TYPED_DISCRIMINATION'),
                         ([['or','shedy',S]],'CONDITIONAL_COMPATIBILITY_ONLY'),
                         ([['or','shedy',S],['or','qoky',S]],'READING_SPECIFIC_COUNTEREXAMPLE')]:
        scope,ev=reconstruct(fixture(lines),lex)
        result=result_for(scope,ev)
        need(result['status']==wanted and result['readers']['RF1b']['status']=='NO_OWNED_PARAGRAPH_DATA','outcome hierarchy')
    return dict(status='PASS',exhaustive59x4=checked,short4=True,unknown=True,flags=True,seams=True,
                unrelated_uncertain_line=True,poison_guards=True,outcome_hierarchy=True)

def compare(actual,expected,path='root'):
    need(type(actual) is type(expected),path+': type differs')
    if isinstance(expected,dict):
        need(actual.keys()==expected.keys(),path+': keys differ')
        for k in expected: compare(actual[k],expected[k],path+'.'+str(k))
    elif isinstance(expected,list):
        need(len(actual)==len(expected),path+': length differs')
        for i,(a,e) in enumerate(zip(actual,expected)): compare(a,e,path+f'[{i}]')
    else: need(actual==expected,path+': value differs '+repr(actual)+' != '+repr(expected))

def execute(spec,lex):
    lock=read(EXP/'PREREG_LOCK.json')
    files=lock['files']
    need(isinstance(files,dict),'lock files map')
    required={str(EXP.relative_to(ROOT)/p) for p in ('PREREGISTRATION.md','src/SPEC.json','src/validate.py','src/run.py')}
    need(required<=set(files),'lock omits essential files')
    for path,expected in files.items(): need(sha(ROOT/path)==expected,'lock hash '+path)
    packet_path=ROOT/spec['packet']['path']
    need(sha(packet_path)==spec['packet']['sha256'],'packet hash')
    packet=read(packet_path)
    scope,events=reconstruct(packet,lex)
    need(len(scope)==1349,'complete owned metadata census !=1349')
    expected={'SCOPE.json':scope,'EVENTS.json':events,'RESULT.json':result_for(scope,events)}
    for name,value in expected.items(): compare(read(EXP/'artifacts'/name),value,name)
    return dict(experiment='GDT1033',status='PASS',independent_implementation=True,
                primary_code_read_or_imported=False,scope_paragraphs=len(scope),events=len(events),
                files_compared=list(expected),lock_files_verified=len(files),
                validator_sha256=sha(Path(__file__)),packet_sha256=sha(packet_path),
                reconstructed_result=expected['RESULT.json'],synthetic=self_test(lex),
                claim_limit='Formal local-frame/type validation; no confirmed meanings or independent manuscript witness.')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    spec,lex=contracts()
    if not args.execute:
        print(json.dumps(self_test(lex),indent=2)); return 0
    try:
        result=execute(spec,lex)
    except Exception as error:
        result=dict(experiment='GDT1033',status='FAIL',error_type=type(error).__name__,error=str(error),primary_code_read_or_imported=False)
        (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2)); return 1
    (EXP/'artifacts/VALIDATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0

if __name__=='__main__':
    raise SystemExit(main())
